"""
LinkedIn API Integration for PostCraft
Handles OAuth authentication and posting functionality for LinkedIn
"""

import os
import secrets
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode
import httpx
from fastapi import HTTPException
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

# LinkedIn API Configuration
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET") 
LINKEDIN_REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI")

LINKEDIN_AUTH_BASE_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
LINKEDIN_API_BASE_URL = "https://api.linkedin.com/v2"

class LinkedInAuthManager:
    """Handles LinkedIn OAuth 2.0 authentication flow"""
    
    def __init__(self):
        self.client_id = LINKEDIN_CLIENT_ID
        self.client_secret = LINKEDIN_CLIENT_SECRET
        self.redirect_uri = LINKEDIN_REDIRECT_URI
        
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            logger.warning("LinkedIn credentials not fully configured")
    
    def generate_auth_url(self, scopes: List[str] = None) -> Dict[str, str]:
        """Generate LinkedIn OAuth authorization URL"""
        if scopes is None:
            scopes = ["r_liteprofile", "w_member_social", "r_organization_social", "w_organization_social"]
        
        state = secrets.token_urlsafe(32)
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": state,
            "scope": " ".join(scopes)
        }
        
        auth_url = f"{LINKEDIN_AUTH_BASE_URL}?{urlencode(params)}"
        return {"auth_url": auth_url, "state": state}
    
    async def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        token_data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(LINKEDIN_TOKEN_URL, data=token_data, headers=headers)
                
                if response.status_code == 200:
                    token_response = response.json()
                    return {
                        "access_token": token_response.get("access_token"),
                        "expires_in": token_response.get("expires_in"),
                        "refresh_token": token_response.get("refresh_token"),
                        "scope": token_response.get("scope")
                    }
                else:
                    logger.error(f"LinkedIn token exchange failed: {response.status_code} - {response.text}")
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Token exchange failed: {response.text}"
                    )
        except httpx.RequestError as e:
            logger.error(f"Network error during token exchange: {str(e)}")
            raise HTTPException(status_code=500, detail="Network error during authentication")


class LinkedInProfileManager:
    """Handles LinkedIn profile and organization information"""
    
    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """Get LinkedIn user profile information"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                # Get basic profile information
                profile_response = await client.get(f"{LINKEDIN_API_BASE_URL}/me", headers=headers)
                
                if profile_response.status_code != 200:
                    logger.error(f"Failed to get LinkedIn profile: {profile_response.status_code}")
                    raise HTTPException(status_code=400, detail="Failed to retrieve LinkedIn profile")
                
                profile_data = profile_response.json()
                
                # Try to get email address if scope permits
                email_data = {}
                try:
                    email_response = await client.get(
                        f"{LINKEDIN_API_BASE_URL}/emailAddress?q=members&projection=(elements*(handle~))", 
                        headers=headers
                    )
                    if email_response.status_code == 200:
                        email_data = email_response.json()
                except:
                    logger.info("Email scope not available or failed")
                
                return {
                    "id": profile_data.get("id"),
                    "first_name": profile_data.get("localizedFirstName"),
                    "last_name": profile_data.get("localizedLastName"),
                    "profile_picture": profile_data.get("profilePicture"),
                    "email": (
                        email_data.get("elements", [{}])[0]
                        .get("handle~", {})
                        .get("emailAddress")
                        if email_data.get("elements") 
                        else None
                    )
                }
        except httpx.RequestError as e:
            logger.error(f"Network error getting profile: {str(e)}")
            raise HTTPException(status_code=500, detail="Network error retrieving profile")
    
    async def get_user_organizations(self, access_token: str, member_urn: str) -> Dict[str, Any]:
        """Get organizations where user can post"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        params = {
            "q": "roleAssignee",
            "roleAssignee": member_urn,
            "role": "ADMINISTRATOR,CONTENT_ADMINISTRATOR,DIRECT_SPONSORED_CONTENT_POSTER"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{LINKEDIN_API_BASE_URL}/organizationAcls", 
                    headers=headers, 
                    params=params
                )
                
                if response.status_code == 200:
                    acl_data = response.json()
                    organizations = []
                    
                    for element in acl_data.get("elements", []):
                        if element.get("state") == "APPROVED":
                            org_urn = element.get("organizationTarget")
                            role = element.get("role")
                            
                            # Get organization details
                            org_details = await self._get_organization_details(access_token, org_urn)
                            
                            organizations.append({
                                "urn": org_urn,
                                "role": role,
                                "details": org_details
                            })
                    
                    return {
                        "status": "success",
                        "organizations": organizations
                    }
                else:
                    logger.error(f"Failed to get organizations: {response.status_code}")
                    return {"status": "error", "organizations": []}
        except httpx.RequestError as e:
            logger.error(f"Network error getting organizations: {str(e)}")
            return {"status": "error", "organizations": []}
    
    async def _get_organization_details(self, access_token: str, organization_urn: str) -> Dict[str, Any]:
        """Get organization details by URN"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        try:
            # Extract organization ID from URN
            org_id = organization_urn.split(":")[-1]
            
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{LINKEDIN_API_BASE_URL}/organizations/{org_id}", headers=headers)
                
                if response.status_code == 200:
                    org_data = response.json()
                    return {
                        "id": org_data.get("id"),
                        "name": org_data.get("localizedName"),
                        "vanityName": org_data.get("vanityName"),
                        "logoV2": org_data.get("logoV2")
                    }
                else:
                    logger.warning(f"Failed to get org details for {org_id}")
                    return {"error": "Failed to retrieve organization details"}
        except Exception as e:
            logger.error(f"Error getting org details: {str(e)}")
            return {"error": str(e)}


class LinkedInPostManager:
    """Handles LinkedIn post creation and management"""
    
    async def create_text_post(
        self, 
        access_token: str, 
        author_urn: str, 
        text_content: str, 
        visibility: str = "PUBLIC"
    ) -> Dict[str, Any]:
        """Create a text-only post on LinkedIn"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        post_data = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text_content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{LINKEDIN_API_BASE_URL}/ugcPosts", 
                    headers=headers, 
                    json=post_data
                )
                
                if response.status_code == 201:
                    post_id = response.headers.get("X-RestLi-Id")
                    logger.info(f"LinkedIn post created successfully: {post_id}")
                    return {
                        "status": "success",
                        "post_id": post_id,
                        "message": "Post created successfully",
                        "platform": "linkedin"
                    }
                else:
                    logger.error(f"Failed to create LinkedIn post: {response.status_code} - {response.text}")
                    raise HTTPException(
                        status_code=response.status_code, 
                        detail=f"Failed to create post: {response.text}"
                    )
        except httpx.RequestError as e:
            logger.error(f"Network error creating post: {str(e)}")
            raise HTTPException(status_code=500, detail="Network error during post creation")
    
    async def create_article_post(
        self,
        access_token: str,
        author_urn: str,
        text_content: str,
        article_url: str,
        article_title: str = None,
        article_description: str = None,
        visibility: str = "PUBLIC"
    ) -> Dict[str, Any]:
        """Create a post with article link on LinkedIn"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        media_data = {
            "status": "READY",
            "originalUrl": article_url
        }
        
        if article_title:
            media_data["title"] = {"text": article_title}
        
        if article_description:
            media_data["description"] = {"text": article_description}
        
        post_data = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text_content
                    },
                    "shareMediaCategory": "ARTICLE",
                    "media": [media_data]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{LINKEDIN_API_BASE_URL}/ugcPosts", 
                    headers=headers, 
                    json=post_data
                )
                
                if response.status_code == 201:
                    post_id = response.headers.get("X-RestLi-Id")
                    logger.info(f"LinkedIn article post created: {post_id}")
                    return {
                        "status": "success",
                        "post_id": post_id,
                        "message": "Article post created successfully",
                        "platform": "linkedin"
                    }
                else:
                    logger.error(f"Failed to create article post: {response.status_code}")
                    raise HTTPException(
                        status_code=response.status_code, 
                        detail=f"Failed to create article post: {response.text}"
                    )
        except httpx.RequestError as e:
            logger.error(f"Network error creating article post: {str(e)}")
            raise HTTPException(status_code=500, detail="Network error during article post creation")


# Initialize managers
linkedin_auth = LinkedInAuthManager()
linkedin_profile = LinkedInProfileManager() 
linkedin_posts = LinkedInPostManager()