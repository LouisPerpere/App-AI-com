from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import uuid

# FastAPI app
app = FastAPI(title="Claire et Marcus API", version="1.0.0")

# API router with prefix
api_router = APIRouter(prefix="/api")

# Simple models
class BusinessProfile(BaseModel):
    business_name: str
    business_type: str
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

# Authentication endpoints (mock)
@api_router.post("/auth/register")
async def register(user_data: RegisterRequest):
    """User registration (demo mode)"""
    # Create a business name from first_name + last_name if not provided
    business_name = user_data.business_name
    if not business_name and user_data.first_name and user_data.last_name:
        business_name = f"{user_data.first_name} {user_data.last_name}"
    elif not business_name:
        business_name = "Mon entreprise"
    
    return {
        "message": "Registration successful (demo mode)",
        "user_id": str(uuid.uuid4()),
        "email": user_data.email,
        "business_name": business_name,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "access_token": f"demo_token_{uuid.uuid4()}",
        "refresh_token": f"demo_refresh_{uuid.uuid4()}"
    }

@api_router.post("/auth/login")
async def login(credentials: LoginRequest):
    """User login (demo mode)"""
    return {
        "message": "Login successful (demo mode)",
        "user_id": str(uuid.uuid4()),
        "email": credentials.email,
        "access_token": f"demo_token_{uuid.uuid4()}",
        "refresh_token": f"demo_refresh_{uuid.uuid4()}",
        "expires_in": 3600
    }

@api_router.get("/auth/me")
async def get_current_user():
    """Get current user info (demo mode)"""
    return {
        "user_id": str(uuid.uuid4()),
        "email": "demo@claire-marcus.com",
        "first_name": "Demo",
        "last_name": "User",
        "business_name": "Demo Business",
        "subscription_status": "trial",
        "trial_days_remaining": 14,
        "created_at": datetime.now().isoformat()
    }

@api_router.get("/auth/me")
async def get_current_user_info():
    """Get current user information (demo mode)"""
    return {
        "user_id": str(uuid.uuid4()),
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
async def get_business_profile():
    """Get business profile (demo mode)"""
    return {
        "business_name": "Demo Business",
        "business_type": "service",
        "target_audience": "Demo audience",
        "brand_tone": "professional",
        "posting_frequency": "weekly",
        "preferred_platforms": ["Facebook", "Instagram", "LinkedIn"],
        "budget_range": "500-1000€",
        "email": "demo@claire-marcus.com",
        "hashtags_primary": ["demo", "claire", "marcus"]
    }

@api_router.put("/business-profile")
async def update_business_profile(profile: BusinessProfile):
    """Update business profile (demo mode)"""
    return {
        "message": "Profile updated successfully (demo mode)",
        "profile": profile,
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