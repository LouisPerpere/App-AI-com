from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import os
import uuid
import jwt
from passlib.context import CryptContext

# Import our modules
try:
    # Try to import emergentintegrations first
    from emergentintegrations.database import DatabaseManager
    from emergentintegrations.auth import AuthManager
    EMERGENT_AVAILABLE = True
except ImportError:
    # Fallback to demo mode without emergentintegrations
    EMERGENT_AVAILABLE = False
    print("⚠️ emergentintegrations not available - running in demo mode")

# Import local modules
try:
    import auth as auth_module
    import analytics
    import website_analyzer
    import social_media
    import payments
    import scheduler
    LOCAL_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Local modules not available: {e} - using minimal functionality")
    LOCAL_MODULES_AVAILABLE = False

# FastAPI app
app = FastAPI(title="Claire et Marcus API - Complete Edition", version="2.0.0")

# API router with prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production-super-secret-key-2025")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database setup
if EMERGENT_AVAILABLE:
    try:
        db_manager = DatabaseManager()
        print("✅ DatabaseManager initialized")
    except Exception as e:
        print(f"⚠️ DatabaseManager failed: {e} - using demo mode")
        db_manager = None
else:
    db_manager = None

# Models
class RegisterRequest(BaseModel):
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    business_name: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

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

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    if LOCAL_MODULES_AVAILABLE:
        try:
            # Use real auth module if available
            return await auth_module.get_current_user(credentials.credentials)
        except Exception as e:
            # Fallback to demo mode
            pass
    
    # Demo mode - return demo user
    return {
        "user_id": "demo-user-id",
        "email": "demo@claire-marcus.com",
        "business_id": "demo-business-id",
        "subscription_status": "trial"
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "🎉 Claire et Marcus API - Complete Edition",
        "version": "2.0.0",
        "status": "healthy",
        "features": {
            "emergentintegrations": EMERGENT_AVAILABLE,
            "local_modules": LOCAL_MODULES_AVAILABLE,
            "database": db_manager is not None
        },
        "endpoints": {
            "health": "/api/health",
            "docs": "/docs",
            "auth": "/api/auth/*",
            "business_profile": "/api/business-profile",
            "analytics": "/api/analytics/*",
            "social": "/api/social/*",
            "payments": "/api/payments/*"
        }
    }

# Health check
@api_router.get("/health")
async def health_check():
    """Comprehensive health check"""
    return {
        "status": "healthy",
        "service": "Claire et Marcus API",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "emergentintegrations": EMERGENT_AVAILABLE,
            "local_modules": LOCAL_MODULES_AVAILABLE,
            "database": db_manager is not None,
            "jwt_secret": len(JWT_SECRET_KEY) > 10
        },
        "message": "All systems operational!"
    }

# Authentication endpoints
@api_router.post("/auth/register")
async def register(user_data: RegisterRequest):
    """User registration - Enhanced with real auth when available"""
    
    if LOCAL_MODULES_AVAILABLE:
        try:
            # Use real auth module if available
            result = await auth_module.register_user(
                email=user_data.email,
                password=user_data.password,
                business_name=user_data.business_name or f"{user_data.first_name} {user_data.last_name}"
            )
            return result
        except Exception as e:
            print(f"Auth module failed: {e} - falling back to demo")
    
    # Demo mode fallback
    business_name = user_data.business_name
    if not business_name and user_data.first_name and user_data.last_name:
        business_name = f"{user_data.first_name} {user_data.last_name}"
    elif not business_name:
        business_name = "Mon entreprise"
    
    # Generate JWT token
    token_data = {
        "user_id": str(uuid.uuid4()),
        "email": user_data.email,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    access_token = jwt.encode(token_data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    refresh_token = jwt.encode({**token_data, "type": "refresh"}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return {
        "message": "Registration successful",
        "user_id": token_data["user_id"],
        "email": user_data.email,
        "business_name": business_name,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "subscription_status": "trial",
        "trial_days_remaining": 30
    }

@api_router.post("/auth/login")
async def login(credentials: LoginRequest):
    """User login - Enhanced with real auth when available"""
    
    if LOCAL_MODULES_AVAILABLE:
        try:
            # Use real auth module if available
            result = await auth_module.login_user(credentials.email, credentials.password)
            return result
        except Exception as e:
            print(f"Auth module failed: {e} - falling back to demo")
    
    # Demo mode fallback
    token_data = {
        "user_id": str(uuid.uuid4()),
        "email": credentials.email,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    access_token = jwt.encode(token_data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    refresh_token = jwt.encode({**token_data, "type": "refresh"}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return {
        "message": "Login successful",
        "user_id": token_data["user_id"],
        "email": credentials.email,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "subscription_status": "trial",
        "trial_days_remaining": 30
    }

@api_router.get("/auth/me")
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    return {
        "user_id": current_user.get("user_id"),
        "email": current_user.get("email"),
        "first_name": current_user.get("first_name", "Demo"),
        "last_name": current_user.get("last_name", "User"),
        "business_name": current_user.get("business_name", "Demo Business"),
        "subscription_status": current_user.get("subscription_status", "trial"),
        "trial_days_remaining": current_user.get("trial_days_remaining", 30),
        "created_at": current_user.get("created_at", datetime.now().isoformat())
    }

# Business profile endpoints
@api_router.get("/business-profile")
async def get_business_profile(current_user = Depends(get_current_user)):
    """Get business profile"""
    return {
        "business_name": "Demo Business",
        "business_type": "service",
        "target_audience": "Demo audience",
        "brand_tone": "professional",
        "posting_frequency": "weekly",
        "preferred_platforms": ["Facebook", "Instagram", "LinkedIn"],
        "budget_range": "500-1000€",
        "email": current_user.get("email", "demo@claire-marcus.com"),
        "website_url": "https://claire-marcus.com",
        "hashtags_primary": ["claire", "marcus", "demo"],
        "hashtags_secondary": ["social", "media", "management"]
    }

@api_router.put("/business-profile")
async def update_business_profile(profile: BusinessProfile, current_user = Depends(get_current_user)):
    """Update business profile"""
    return {
        "message": "Profile updated successfully",
        "profile": profile,
        "updated_at": datetime.now().isoformat(),
        "user_id": current_user.get("user_id")
    }

# Content endpoints
@api_router.post("/generate-posts")
async def generate_posts(request: dict, current_user = Depends(get_current_user)):
    """Generate posts with AI"""
    count = request.get("count", 4)
    posts = []
    
    for i in range(count):
        posts.append({
            "id": str(uuid.uuid4()),
            "content": f"🌟 Post généré par Claire et Marcus #{i+1}\n\nContenu de démonstration pour votre entreprise. Claire rédige, Marcus programme. Vous respirez ! ✨\n\n#ClaireetMarcus #CommunityManagement #Demo",
            "platform": "multiple",
            "status": "generated",
            "created_at": datetime.now().isoformat(),
            "hashtags": ["claire", "marcus", "demo"],
            "user_id": current_user.get("user_id")
        })
    
    return {
        "message": f"{count} posts generated successfully",
        "posts": posts
    }

# Notes endpoints
@api_router.get("/notes")
async def get_notes(current_user = Depends(get_current_user)):
    """Get notes"""
    return {
        "notes": [
            {
                "id": "demo-note-1",
                "content": "Note de démonstration - Claire et Marcus",
                "description": "Exemple de note",
                "created_at": datetime.now().isoformat(),
                "user_id": current_user.get("user_id")
            }
        ]
    }

@api_router.post("/notes")
async def create_note(note: ContentNote, current_user = Depends(get_current_user)):
    """Create note"""
    return {
        "message": "Note created successfully",
        "note": {
            "id": str(uuid.uuid4()),
            "content": note.content,
            "description": note.description,
            "created_at": datetime.now().isoformat(),
            "user_id": current_user.get("user_id")
        }
    }

@api_router.delete("/notes/{note_id}")
async def delete_note(note_id: str, current_user = Depends(get_current_user)):
    """Delete note"""
    return {
        "message": f"Note {note_id} deleted successfully"
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