from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import httpx
import os
import logging
import secrets
import urllib.parse
from datetime import datetime, timedelta
import json
from motor.motor_asyncio import AsyncIOMotorClient
import uuid

from auth import get_current_active_user, User

# Initialize router
social_router = APIRouter(prefix="/social", tags=["social-media"])

# MongoDB connection (reuse from main app)
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Facebook App credentials from environment
FACEBOOK_CLIENT_ID = os.environ.get('FACEBOOK_APP_ID', '')
FACEBOOK_CLIENT_SECRET = os.environ.get('FACEBOOK_APP_SECRET', '')
FACEBOOK_REDIRECT_URI = os.environ.get('FACEBOOK_REDIRECT_URI', 'http://localhost:3000/auth/facebook/callback')

# Base URLs
FACEBOOK_AUTH_URL = "https://www.facebook.com/v19.0/dialog/oauth"
FACEBOOK_TOKEN_URL = "https://graph.facebook.com/v19.0/oauth/access_token"
FACEBOOK_API_BASE = "https://graph.facebook.com/v19.0"

# Pydantic Models
class FacebookAuthRequest(BaseModel):
    business_id: str
    scopes: Optional[List[str]] = ["pages_manage_posts", "pages_read_engagement", "instagram_basic", "instagram_content_publish"]

class SocialMediaPost(BaseModel):
    platform: str  # facebook, instagram
    content: str
    image_url: Optional[str] = None
    page_id: Optional[str] = None  # For Facebook pages
    instagram_user_id: Optional[str] = None  # For Instagram
    scheduled_time: Optional[datetime] = None

class FacebookPageInfo(BaseModel):
    id: str
    name: str
    access_token: str
    category: str
    instagram_business_account: Optional[Dict[str, Any]] = None

class InstagramAccountInfo(BaseModel):
    id: str
    username: str
    account_type: str

# OAuth State Management
oauth_states = {}  # In production, use Redis or database

class FacebookOAuthManager:
    """Manages Facebook OAuth flow"""
    
    def __init__(self):
        self.client_id = FACEBOOK_CLIENT_ID
        self.client_secret = FACEBOOK_CLIENT_SECRET
        self.redirect_uri = FACEBOOK_REDIRECT_URI
    
    def generate_auth_url(self, user_id: str, business_id: str, scopes: List[str]) -> Dict[str, str]:
        """Generate Facebook authorization URL"""
        state = secrets.token_urlsafe(32)
        
        # Store state with user context
        oauth_states[state] = {
            "user_id": user_id,
            "business_id": business_id,
            "timestamp": datetime.utcnow().timestamp()
        }
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": ",".join(scopes),
            "response_type": "code",
            "state": state
        }
        
        auth_url = f"{FACEBOOK_AUTH_URL}?{urllib.parse.urlencode(params)}"
        
        return {
            "authorization_url": auth_url,
            "state": state
        }
    
    async def exchange_code_for_token(self, code: str, state: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        # Validate state
        if state not in oauth_states:
            raise HTTPException(status_code=400, detail="Invalid state parameter")
        
        state_data = oauth_states[state]
        
        # Check state expiration (10 minutes)
        if datetime.utcnow().timestamp() - state_data["timestamp"] > 600:
            del oauth_states[state]
            raise HTTPException(status_code=400, detail="State expired")
        
        # Exchange code for token
        token_params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": code
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(FACEBOOK_TOKEN_URL, params=token_params)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Token exchange failed: {response.text}"
                )
            
            token_data = response.json()
            
            # Get long-lived token
            long_lived_token = await self.get_long_lived_token(token_data["access_token"])
            
            # Clean up state
            user_id = state_data["user_id"]
            business_id = state_data["business_id"]
            del oauth_states[state]
            
            return {
                "access_token": long_lived_token["access_token"],
                "expires_in": long_lived_token.get("expires_in", 5184000),  # 60 days default
                "user_id": user_id,
                "business_id": business_id
            }
    
    async def get_long_lived_token(self, short_token: str) -> Dict[str, Any]:
        """Convert short-lived token to long-lived token"""
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "fb_exchange_token": short_token
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(FACEBOOK_TOKEN_URL, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                # If long-lived token fails, return short token
                return {"access_token": short_token, "expires_in": 3600}

class FacebookAPIClient:
    """Handles Facebook API interactions"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = FACEBOOK_API_BASE
    
    async def get_user_info(self) -> Dict[str, Any]:
        """Get user profile information"""
        url = f"{self.base_url}/me"
        params = {
            "fields": "id,name,email",
            "access_token": self.access_token
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to get user info: {response.text}"
                )
    
    async def get_user_pages(self) -> List[FacebookPageInfo]:
        """Get user's Facebook pages"""
        url = f"{self.base_url}/me/accounts"
        params = {
            "fields": "id,name,access_token,category,instagram_business_account",
            "access_token": self.access_token
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                pages = []
                
                for page_data in data.get("data", []):
                    page_info = FacebookPageInfo(
                        id=page_data["id"],
                        name=page_data["name"],
                        access_token=page_data["access_token"],
                        category=page_data.get("category", ""),
                        instagram_business_account=page_data.get("instagram_business_account")
                    )
                    pages.append(page_info)
                
                return pages
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to get pages: {response.text}"
                )
    
    async def post_to_page(self, page_id: str, page_token: str, content: str, image_url: Optional[str] = None) -> Dict[str, Any]:
        """Post content to a Facebook page"""
        url = f"{self.base_url}/{page_id}/feed"
        
        post_data = {
            "message": content,
            "access_token": page_token
        }
        
        if image_url:
            post_data["link"] = image_url
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=post_data)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to post to Facebook: {response.text}"
                )

class InstagramAPIClient:
    """Handles Instagram Business API interactions"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = FACEBOOK_API_BASE
    
    async def get_instagram_account_info(self, instagram_user_id: str) -> InstagramAccountInfo:
        """Get Instagram account information"""
        url = f"{self.base_url}/{instagram_user_id}"
        params = {
            "fields": "id,username,account_type",
            "access_token": self.access_token
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return InstagramAccountInfo(
                    id=data["id"],
                    username=data["username"],
                    account_type=data.get("account_type", "BUSINESS")
                )
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to get Instagram info: {response.text}"
                )
    
    async def create_media_container(self, instagram_user_id: str, image_url: str, caption: str) -> str:
        """Create Instagram media container"""
        url = f"{self.base_url}/{instagram_user_id}/media"
        
        data = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.access_token
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)
            
            if response.status_code == 200:
                result = response.json()
                return result["id"]
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to create Instagram media container: {response.text}"
                )
    
    async def publish_media(self, instagram_user_id: str, creation_id: str) -> Dict[str, Any]:
        """Publish Instagram media"""
        url = f"{self.base_url}/{instagram_user_id}/media_publish"
        
        data = {
            "creation_id": creation_id,
            "access_token": self.access_token
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to publish Instagram media: {response.text}"
                )
    
    async def post_to_instagram(self, instagram_user_id: str, image_url: str, caption: str) -> Dict[str, Any]:
        """Complete Instagram posting workflow"""
        # Step 1: Create media container
        container_id = await self.create_media_container(instagram_user_id, image_url, caption)
        
        # Step 2: Publish media
        result = await self.publish_media(instagram_user_id, container_id)
        
        return {
            "container_id": container_id,
            "media_id": result["id"],
            "success": True
        }

# Initialize OAuth manager
oauth_manager = FacebookOAuthManager()

# API Routes

@social_router.get("/facebook/auth-url")
async def get_facebook_auth_url(
    business_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get Facebook authorization URL"""
    if not FACEBOOK_CLIENT_ID or not FACEBOOK_CLIENT_SECRET:
        raise HTTPException(
            status_code=500, 
            detail="Facebook integration not configured. Please add FACEBOOK_APP_ID and FACEBOOK_APP_SECRET to environment variables."
        )
    
    # Verify business belongs to user
    business_profile = await db.business_profiles.find_one({
        "id": business_id,
        "user_id": current_user.id
    })
    
    if not business_profile:
        raise HTTPException(status_code=404, detail="Business profile not found")
    
    scopes = ["pages_manage_posts", "pages_read_engagement", "instagram_basic", "instagram_content_publish"]
    auth_data = oauth_manager.generate_auth_url(current_user.id, business_id, scopes)
    
    return auth_data

@social_router.post("/facebook/callback")
async def facebook_callback(
    code: str,
    state: str,
    current_user: User = Depends(get_current_active_user)
):
    """Handle Facebook OAuth callback"""
    try:
        # Exchange code for token
        token_data = await oauth_manager.exchange_code_for_token(code, state)
        
        # Verify user matches
        if token_data["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="User mismatch")
        
        # Get user info and pages
        fb_client = FacebookAPIClient(token_data["access_token"])
        user_info = await fb_client.get_user_info()
        pages = await fb_client.get_user_pages()
        
        # Store connections in database
        connections_created = []
        
        for page in pages:
            # Create Facebook page connection
            fb_connection = {
                "id": str(uuid.uuid4()),
                "user_id": current_user.id,
                "business_id": token_data["business_id"],
                "platform": "facebook",
                "access_token": page.access_token,
                "page_id": page.id,
                "page_name": page.name,
                "expires_at": datetime.utcnow() + timedelta(seconds=token_data["expires_in"]),
                "active": True,
                "connected_at": datetime.utcnow(),
                "platform_user_id": user_info["id"],
                "platform_username": user_info["name"]
            }
            
            # Check if connection already exists
            existing_connection = await db.social_media_connections.find_one({
                "user_id": current_user.id,
                "business_id": token_data["business_id"],
                "platform": "facebook",
                "page_id": page.id
            })
            
            if existing_connection:
                # Update existing connection
                await db.social_media_connections.update_one(
                    {"id": existing_connection["id"]},
                    {"$set": {
                        "access_token": page.access_token,
                        "expires_at": fb_connection["expires_at"],
                        "active": True,
                        "connected_at": datetime.utcnow()
                    }}
                )
                fb_connection["id"] = existing_connection["id"]
            else:
                # Create new connection
                await db.social_media_connections.insert_one(fb_connection)
            
            connections_created.append({
                "platform": "facebook",
                "page_name": page.name,
                "page_id": page.id
            })
            
            # Create Instagram connection if available
            if page.instagram_business_account:
                ig_account = page.instagram_business_account
                
                ig_connection = {
                    "id": str(uuid.uuid4()),
                    "user_id": current_user.id,
                    "business_id": token_data["business_id"],
                    "platform": "instagram",
                    "access_token": page.access_token,  # Same token as Facebook page
                    "instagram_user_id": ig_account["id"],
                    "page_id": page.id,  # Link to Facebook page
                    "expires_at": datetime.utcnow() + timedelta(seconds=token_data["expires_in"]),
                    "active": True,
                    "connected_at": datetime.utcnow(),
                    "platform_user_id": ig_account["id"],
                    "platform_username": ig_account.get("username", "")
                }
                
                # Check if Instagram connection already exists
                existing_ig_connection = await db.social_media_connections.find_one({
                    "user_id": current_user.id,
                    "business_id": token_data["business_id"],
                    "platform": "instagram",
                    "instagram_user_id": ig_account["id"]
                })
                
                if existing_ig_connection:
                    # Update existing Instagram connection
                    await db.social_media_connections.update_one(
                        {"id": existing_ig_connection["id"]},
                        {"$set": {
                            "access_token": page.access_token,
                            "expires_at": ig_connection["expires_at"],
                            "active": True,
                            "connected_at": datetime.utcnow()
                        }}
                    )
                    ig_connection["id"] = existing_ig_connection["id"]
                else:
                    # Create new Instagram connection
                    await db.social_media_connections.insert_one(ig_connection)
                
                connections_created.append({
                    "platform": "instagram", 
                    "username": ig_account.get("username", ""),
                    "instagram_user_id": ig_account["id"]
                })
        
        return {
            "success": True,
            "message": f"Successfully connected {len(connections_created)} accounts",
            "connections": connections_created,
            "user_info": user_info
        }
        
    except Exception as e:
        logging.error(f"Facebook callback error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to complete Facebook connection: {str(e)}"
        )

@social_router.get("/connections")
async def get_social_connections(
    business_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get all social media connections for a business"""
    connections = await db.social_media_connections.find({
        "user_id": current_user.id,
        "business_id": business_id,
        "active": True
    }).to_list(100)
    
    return {
        "connections": connections,
        "total": len(connections)
    }

@social_router.post("/post")
async def create_social_media_post(
    post_data: SocialMediaPost,
    current_user: User = Depends(get_current_active_user)
):
    """Create a post on social media platforms"""
    try:
        results = []
        
        if post_data.platform == "facebook" and post_data.page_id:
            # Get Facebook page connection
            connection = await db.social_media_connections.find_one({
                "user_id": current_user.id,
                "platform": "facebook",
                "page_id": post_data.page_id,
                "active": True
            })
            
            if not connection:
                raise HTTPException(status_code=404, detail="Facebook connection not found")
            
            # Post to Facebook
            fb_client = FacebookAPIClient(connection["access_token"])
            result = await fb_client.post_to_page(
                post_data.page_id, 
                connection["access_token"], 
                post_data.content, 
                post_data.image_url
            )
            
            results.append({
                "platform": "facebook",
                "success": True,
                "post_id": result["id"],
                "page_name": connection.get("page_name", "")
            })
        
        elif post_data.platform == "instagram" and post_data.instagram_user_id:
            # Get Instagram connection
            connection = await db.social_media_connections.find_one({
                "user_id": current_user.id,
                "platform": "instagram",
                "instagram_user_id": post_data.instagram_user_id,
                "active": True
            })
            
            if not connection:
                raise HTTPException(status_code=404, detail="Instagram connection not found")
            
            if not post_data.image_url:
                raise HTTPException(status_code=400, detail="Instagram posts require an image")
            
            # Post to Instagram
            ig_client = InstagramAPIClient(connection["access_token"])
            result = await ig_client.post_to_instagram(
                post_data.instagram_user_id,
                post_data.image_url,
                post_data.content
            )
            
            results.append({
                "platform": "instagram",
                "success": True,
                "media_id": result["media_id"],
                "container_id": result["container_id"],
                "username": connection.get("platform_username", "")
            })
        
        else:
            raise HTTPException(
                status_code=400, 
                detail="Invalid platform or missing required parameters"
            )
        
        return {
            "success": True,
            "results": results,
            "message": f"Posted to {len(results)} platform(s) successfully"
        }
        
    except Exception as e:
        logging.error(f"Social media posting error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to create post: {str(e)}"
        )

@social_router.delete("/connection/{connection_id}")
async def disconnect_social_account(
    connection_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Disconnect a social media account"""
    result = await db.social_media_connections.update_one(
        {
            "id": connection_id,
            "user_id": current_user.id
        },
        {"$set": {"active": False, "disconnected_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    return {"message": "Social media account disconnected successfully"}

# Export router
__all__ = ["social_router"]