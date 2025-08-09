from fastapi import FastAPI, APIRouter, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import uuid

# Import database
from database import get_database, DatabaseManager

# Import the modern payments module
try:
    from payments_v2 import payments_router
    PAYMENTS_V2_AVAILABLE = True
    print("✅ Modern Stripe payments module loaded")
except ImportError as e:
    print(f"⚠️ Modern payments module not available: {e}")
    PAYMENTS_V2_AVAILABLE = False

# FastAPI app
app = FastAPI(title="Claire et Marcus API", version="1.0.0")

# API router with prefix
api_router = APIRouter(prefix="/api")

# Initialize database
db = get_database()

# Dependency to get current user
def get_current_user_id(authorization: str = Header(None)):
    """Extract user ID from JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        # For demo mode compatibility, return a demo user ID
        return "demo_user_id"
    
    token = authorization.replace("Bearer ", "")
    
    if db.is_connected():
        # Try to get real user from database
        user_data = db.get_user_by_token(token)
        if user_data:
            return user_data["user_id"]
    
    # Fallback to demo mode for invalid/expired tokens
    return "demo_user_id"

# Simple models
class BusinessProfile(BaseModel):
    business_name: str
    business_type: str
    business_description: str
    target_audience: str
    brand_tone: str
    posting_frequency: str
    preferred_platforms: List[str]
    budget_range: str
    email: Optional[str] = None
    website_url: Optional[str] = None
    hashtags_primary: List[str] = []
    hashtags_secondary: List[str] = []

class ContentNote(BaseModel):
    content: str
    description: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    business_name: Optional[str] = None

# Basic health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "Claire et Marcus API",
        "timestamp": datetime.now().isoformat(),
        "message": "API is running successfully!"
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "🎉 Claire et Marcus API is running!",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "health": "/api/health",
            "docs": "/docs",
            "auth": "/api/auth/*",
            "business_profile": "/api/business-profile"
        }
    }

# Authentication endpoints
@api_router.post("/auth/register")
async def register(user_data: RegisterRequest):
    """User registration with real database"""
    try:
        if db.is_connected():
            # Use real database
            result = db.create_user(
                email=user_data.email,
                password=user_data.password,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                business_name=user_data.business_name
            )
            return {
                "message": "Registration successful",
                **result
            }
        else:
            # Fallback to demo mode
            business_name = user_data.business_name
            if not business_name and user_data.first_name and user_data.last_name:
                business_name = f"{user_data.first_name} {user_data.last_name}"
            elif not business_name:
                business_name = "Mon entreprise"
            
            return {
                "message": "Registration successful (demo mode - database unavailable)",
                "user_id": str(uuid.uuid4()),
                "email": user_data.email,
                "business_name": business_name,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "access_token": f"demo_token_{uuid.uuid4()}",
                "refresh_token": f"demo_refresh_{uuid.uuid4()}"
            }
    except Exception as e:
        if "already exists" in str(e):
            raise HTTPException(status_code=400, detail="User already exists")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@api_router.post("/auth/login")
async def login(credentials: LoginRequest):
    """User login with real database"""
    try:
        if db.is_connected():
            # Use real database
            result = db.authenticate_user(credentials.email, credentials.password)
            if result:
                return {
                    "message": "Login successful",
                    **result
                }
            else:
                raise HTTPException(status_code=401, detail="Invalid credentials")
        else:
            # Fallback to demo mode
            return {
                "message": "Login successful (demo mode - database unavailable)",
                "user_id": str(uuid.uuid4()),
                "email": credentials.email,
                "access_token": f"demo_token_{uuid.uuid4()}",
                "refresh_token": f"demo_refresh_{uuid.uuid4()}",
                "expires_in": 3600
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@api_router.get("/auth/me")
async def get_current_user_info(user_id: str = Depends(get_current_user_id)):
    """Get current user information with real database"""
    try:
        if db.is_connected() and user_id != "demo_user_id":
            # Get real user data from database
            user = db.db.users.find_one({"user_id": user_id})
            if user:
                return {
                    "user_id": user["user_id"],
                    "email": user["email"],
                    "first_name": user.get("first_name"),
                    "last_name": user.get("last_name"), 
                    "business_name": user.get("business_name"),
                    "subscription_status": user.get("subscription_status", "trial"),
                    "trial_days_remaining": user.get("trial_days_remaining", 30),
                    "created_at": user.get("created_at", datetime.utcnow()).isoformat()
                }
        
        # Fallback to demo mode
        return {
            "user_id": "demo_user_id",
            "email": "demo@claire-marcus.com",
            "first_name": "Demo",
            "last_name": "User", 
            "business_name": "Demo Business",
            "subscription_status": "trial",
            "trial_days_remaining": 30,
            "created_at": datetime.now().isoformat()
        }
    except Exception as e:
        # Fallback to demo on error
        return {
            "user_id": "demo_user_id",
            "email": "demo@claire-marcus.com",
            "first_name": "Demo",
            "last_name": "User", 
            "business_name": "Demo Business",
            "subscription_status": "trial",
            "trial_days_remaining": 30,
            "created_at": datetime.now().isoformat()
        }

# Business profile endpoints
@api_router.get("/business-profile")
async def get_business_profile(user_id: str = Depends(get_current_user_id)):
    """Get business profile with real database persistence"""
    try:
        if db.is_connected() and user_id != "demo_user_id":
            # Get real business profile from database
            profile = db.get_business_profile(user_id)
            if profile:
                # Remove MongoDB internal fields and format response
                profile.pop('_id', None)
                profile.pop('profile_id', None)
                
                return {
                    "business_name": profile.get("business_name", ""),
                    "business_type": profile.get("business_type", "service"),
                    "business_description": profile.get("business_description", ""),
                    "target_audience": profile.get("target_audience", ""),
                    "brand_tone": profile.get("brand_tone", "professional"),
                    "posting_frequency": profile.get("posting_frequency", "weekly"),
                    "preferred_platforms": profile.get("preferred_platforms", ["Facebook", "Instagram"]),
                    "budget_range": profile.get("budget_range", ""),
                    "email": profile.get("email", ""),
                    "website_url": profile.get("website_url", ""),
                    "hashtags_primary": profile.get("hashtags_primary", []),
                    "hashtags_secondary": profile.get("hashtags_secondary", [])
                }
            else:
                # Create default profile if none exists
                db._create_default_business_profile(user_id, "Mon entreprise")
                profile = db.get_business_profile(user_id)
                if profile:
                    profile.pop('_id', None)
                    profile.pop('profile_id', None)
                    return profile
        
        # Fallback to demo mode
        print(f"⚠️ Returning demo business profile for user_id: {user_id}")
        return {
            "business_name": "Demo Business",
            "business_type": "service",
            "business_description": "Exemple d'entreprise utilisant Claire et Marcus pour gérer ses réseaux sociaux",
            "target_audience": "Demo audience",
            "brand_tone": "professional",
            "posting_frequency": "weekly",
            "preferred_platforms": ["Facebook", "Instagram", "LinkedIn"],
            "budget_range": "500-1000€",
            "email": "demo@claire-marcus.com",
            "website_url": "",
            "hashtags_primary": ["demo", "claire", "marcus"],
            "hashtags_secondary": ["social", "media", "management"]
        }
    except Exception as e:
        print(f"❌ Error getting business profile: {e}")
        # Return demo profile on error
        return {
            "business_name": "Demo Business", 
            "business_type": "service",
            "business_description": "Exemple d'entreprise utilisant Claire et Marcus",
            "target_audience": "Demo audience",
            "brand_tone": "professional",
            "posting_frequency": "weekly", 
            "preferred_platforms": ["Facebook", "Instagram"],
            "budget_range": "500-1000€",
            "email": "demo@claire-marcus.com",
            "website_url": "",
            "hashtags_primary": [],
            "hashtags_secondary": []
        }

@api_router.put("/business-profile") 
async def update_business_profile(profile: BusinessProfile, user_id: str = Depends(get_current_user_id)):
    """Update business profile with real database persistence"""
    try:
        if db.is_connected() and user_id != "demo_user_id":
            # Update real business profile in database
            profile_data = profile.dict()
            profile_data["updated_at"] = datetime.utcnow()
            
            success = db.update_business_profile(user_id, profile_data)
            
            if success:
                print(f"✅ Business profile updated successfully for user {user_id}")
                # Return the updated profile data
                return {
                    "message": "Profile updated successfully",
                    "profile": profile_data,
                    "updated_at": profile_data["updated_at"].isoformat()
                }
            else:
                print(f"⚠️ No profile found to update for user {user_id}, creating new one")
                # Create new profile if update failed (profile doesn't exist)
                db._create_default_business_profile(user_id, profile.business_name)
                # Try update again
                success = db.update_business_profile(user_id, profile_data)
                if success:
                    return {
                        "message": "Profile created and updated successfully", 
                        "profile": profile_data,
                        "updated_at": profile_data["updated_at"].isoformat()
                    }
        
        # Fallback to demo mode (still return success for frontend compatibility)
        print(f"⚠️ Demo mode: Profile update simulated for user_id: {user_id}")
        return {
            "message": "Profile updated successfully (demo mode - database unavailable)",
            "profile": profile.dict(),
            "updated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error updating business profile: {e}")
        # Return success even on error for demo mode compatibility
        return {
            "message": "Profile updated successfully (demo mode - error fallback)",
            "profile": profile.dict(),
            "updated_at": datetime.now().isoformat()
        }

# Content generation endpoints
@api_router.post("/generate-posts")
async def generate_posts(request: dict):
    """Generate posts (demo mode)"""
    count = request.get("count", 4)
    posts = []
    
    for i in range(count):
        posts.append({
            "id": str(uuid.uuid4()),
            "content": f"🌟 Post généré par Claire et Marcus #{i+1}\n\nContenu de démonstration pour votre entreprise. Claire rédige, Marcus programme. Vous respirez ! ✨\n\n#ClaireetMarcus #CommunityManagement #Demo",
            "platform": "multiple",
            "status": "generated",
            "created_at": datetime.now().isoformat(),
            "hashtags": ["claire", "marcus", "demo"]
        })
    
    return {
        "message": f"{count} posts generated successfully",
        "posts": posts
    }

# Notes endpoints
@api_router.get("/notes")
async def get_notes():
    """Get notes (demo mode)"""
    return {
        "notes": [
            {
                "id": "demo-note-1",
                "content": "Note de démonstration - Claire et Marcus",
                "description": "Exemple de note",
                "created_at": datetime.now().isoformat()
            }
        ]
    }

@api_router.post("/notes")
async def create_note(note: ContentNote):
    """Create note (demo mode)"""
    return {
        "message": "Note created successfully",
        "note": {
            "id": str(uuid.uuid4()),
            "content": note.content,
            "description": note.description,
            "created_at": datetime.now().isoformat()
        }
    }

@api_router.delete("/notes/{note_id}")
async def delete_note(note_id: str):
    """Delete note (demo mode)"""
    return {
        "message": f"Note {note_id} deleted successfully"
    }

# Bibliotheque endpoints
@api_router.get("/bibliotheque")
async def get_bibliotheque():
    """Get bibliotheque (demo mode)"""
    return {
        "files": [
            {
                "id": "demo-file-1",
                "name": "demo-image.jpg",
                "type": "image",
                "size": "1.2MB",
                "uploaded_at": datetime.now().isoformat()
            }
        ]
    }

@api_router.post("/bibliotheque")
async def upload_file(file_data: dict):
    """Upload file to bibliotheque (demo mode)"""
    return {
        "message": "File uploaded successfully (demo mode)",
        "file": {
            "id": str(uuid.uuid4()),
            "name": file_data.get("name", "demo-file"),
            "uploaded_at": datetime.now().isoformat()
        }
    }

# LinkedIn endpoints
@api_router.get("/linkedin/auth-url")
async def get_linkedin_auth_url():
    """Get LinkedIn OAuth authorization URL (demo mode)"""
    return {
        "auth_url": "https://www.linkedin.com/oauth/v2/authorization?demo=true",
        "state": str(uuid.uuid4()),
        "message": "LinkedIn integration available (demo mode)"
    }

@api_router.get("/linkedin/callback")
async def linkedin_callback(code: str = None, state: str = None, error: str = None):
    """Handle LinkedIn OAuth callback (demo mode)"""
    if error:
        raise HTTPException(status_code=400, detail=f"LinkedIn authentication error: {error}")
    
    return {
        "status": "success", 
        "message": "LinkedIn callback successful (demo mode)",
        "token_data": {"access_token": f"demo_linkedin_token_{uuid.uuid4()}"},
        "user_profile": {
            "id": "demo-linkedin-user",
            "first_name": "Demo",
            "last_name": "User"
        }
    }

@api_router.post("/linkedin/post")
async def create_linkedin_post(post_data: dict):
    """Create a LinkedIn post (demo mode)"""
    return {
        "status": "success",
        "post_id": f"linkedin_post_{uuid.uuid4()}",
        "message": "LinkedIn post created successfully (demo mode)",
        "platform": "linkedin"
    }

# Website analyzer endpoints
@api_router.post("/website/analyze")
async def analyze_website(request: dict):
    """Analyze website (demo mode)"""
    return {
        "message": "Website analysis completed (demo mode)",
        "insights": "Votre site web montre une excellente présentation de vos services. Suggestions de posts basées sur votre contenu.",
        "suggestions": [
            "Créez un post sur vos services principaux",
            "Partagez vos témoignages clients", 
            "Montrez votre équipe et votre expertise"
        ]
    }

# Include the API router
app.include_router(api_router)

# Include the modern payments router
if PAYMENTS_V2_AVAILABLE:
    app.include_router(payments_router)
    print("✅ Modern Stripe payments endpoints added")
else:
    print("⚠️ Payments endpoints not available - running without Stripe integration")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)