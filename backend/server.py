from fastapi import FastAPI, APIRouter, HTTPException, Depends, Form, status
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import os
import uuid
import openai

# Import authentication module
try:
    from auth import (
        User, UserCreate, UserLogin, UserResponse, Token, 
        create_user, authenticate_user, create_access_token,
        get_current_user, get_current_active_user
    )
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

# FastAPI app
app = FastAPI(title="Claire et Marcus API", version="1.0.0")

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'claire_marcus')]

# API router with prefix
api_router = APIRouter(prefix="/api")

# Basic models
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

# Basic health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "Claire et Marcus API",
        "timestamp": datetime.now().isoformat()
    }

# Simple business profile endpoint
@api_router.get("/business-profile")
async def get_business_profile():
    """Get business profile"""
    return {"message": "Business profile endpoint working"}

@api_router.put("/business-profile")
async def update_business_profile(profile: BusinessProfile):
    """Update business profile"""
    return {"message": "Profile updated successfully", "profile": profile}

# Simple authentication endpoints
@api_router.post("/auth/register")
async def register(user_data: dict):
    """User registration"""
    return {"message": "Registration endpoint working"}

@api_router.post("/auth/login")
async def login(credentials: dict):
    """User login"""
    return {"message": "Login endpoint working"}

# Simple content generation endpoint
@api_router.post("/generate-posts")
async def generate_posts(request: dict):
    """Generate posts endpoint"""
    return {
        "message": "Post generation working",
        "posts": [
            {
                "id": str(uuid.uuid4()),
                "content": "Post généré par Claire et Marcus - Version de démo",
                "platform": "multiple",
                "status": "generated",
                "created_at": datetime.now().isoformat()
            }
        ]
    }

# Simple notes endpoints
@api_router.get("/notes")
async def get_notes():
    """Get notes"""
    return {"notes": []}

@api_router.post("/notes")
async def create_note(note: ContentNote):
    """Create note"""
    return {"message": "Note created", "note": note}

@api_router.delete("/notes/{note_id}")
async def delete_note(note_id: str):
    """Delete note"""
    return {"message": f"Note {note_id} deleted"}

# Simple bibliotheque endpoints
@api_router.get("/bibliotheque")
async def get_bibliotheque():
    """Get bibliotheque"""
    return {"files": []}

@api_router.post("/bibliotheque")
async def upload_file(file_data: dict):
    """Upload file to bibliotheque"""
    return {"message": "File uploaded"}

# LinkedIn endpoints (placeholder)
@api_router.get("/linkedin/auth-url")
async def get_linkedin_auth_url():
    """Get LinkedIn OAuth authorization URL"""
    return {"message": "LinkedIn integration in development"}

@api_router.get("/linkedin/callback")
async def linkedin_callback(code: str = None, state: str = None, error: str = None):
    """Handle LinkedIn OAuth callback"""
    if error:
        raise HTTPException(status_code=400, detail=f"LinkedIn authentication error: {error}")
    return {"status": "success", "message": "LinkedIn callback working"}

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

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Claire et Marcus API is running!",
        "version": "1.0.0",
        "status": "healthy"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)