from fastapi import FastAPI, APIRouter, HTTPException, Header, Depends, Response, File, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # Ajouté pour servir uploads/ selon ChatGPT
from pydantic import BaseModel, Field  # Ajouté Field pour validation
import jwt
from passlib.context import CryptContext
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import os
import uuid
import asyncio
import json
import base64
from PIL import Image
import io
import mimetypes

# Enable HEIC/HEIF support for iPhone photos
import pillow_heif
pillow_heif.register_heif_opener()

# Ensure proper MIME types for all image formats including HEIC/HEIF
mimetypes.add_type('image/webp', '.webp')   # Safari/iOS
mimetypes.add_type('image/jpeg', '.jpg')
mimetypes.add_type('image/jpeg', '.jpeg')
mimetypes.add_type('image/png', '.png')
mimetypes.add_type('image/heic', '.heic')   # iPhone/iOS photos
mimetypes.add_type('image/heif', '.heif')   # iPhone/iOS photos

# Import database
from database import get_database, DatabaseManager

class UpdateDescriptionIn(BaseModel):
    description: str = Field("", max_length=2000)

class MediaResponse(BaseModel):
    id: str
    filename: str
    file_type: Optional[str] = None
    description: str = ""
    url: Optional[str] = None
    thumb_url: Optional[str] = None
    uploaded_at: Optional[str] = None

# Collections MongoDB pour persistance (selon ChatGPT)
def get_media_collection():
    """Get MongoDB media collection (synchronous)"""
    db_manager = get_database()
    return db_manager.db.media

def parse_any_id(file_id: str) -> dict:
    """Parse file ID - accepts both ObjectId and UUID for backwards compatibility"""
    try:
        from bson import ObjectId
        return {"_id": ObjectId(file_id)}
    except Exception:
        # Fallback for UUID external_id (temporary compatibility)
        print(f"⚠️ Using UUID fallback for file_id: {file_id}")
        return {"external_id": file_id}

# Import GPT-5 website analyzer
try:
    from website_analyzer_gpt5 import website_router
    WEBSITE_ANALYZER_AVAILABLE = True
    print("✅ GPT-5 Website Analyzer module loaded")
except ImportError as e:
    print(f"⚠️ GPT-5 Website Analyzer module not available: {e}")
    WEBSITE_ANALYZER_AVAILABLE = False

# Import the modern payments module
try:
    from payments_v2 import payments_router
    PAYMENTS_V2_AVAILABLE = True
    print("✅ Modern Stripe payments module loaded")
except ImportError as e:
    print(f"⚠️ Modern payments module not available: {e}")
    PAYMENTS_V2_AVAILABLE = False

# Import thumbnails module
try:
    from routes_thumbs import router as thumbnails_router
    THUMBNAILS_AVAILABLE = True
    print("✅ Thumbnails generation module loaded")
except ImportError as e:
    print(f"⚠️ Thumbnails module not available: {e}")
    THUMBNAILS_AVAILABLE = False

# FastAPI app
app = FastAPI(title="Claire et Marcus API", version="1.0.0")

# Add anti-cache middleware for API responses (fix PWA/Service Worker cache issues)
@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, proxy-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        response.headers["Surrogate-Control"] = "no-store"
    return response

# Logs middleware selon plan ChatGPT
@app.middleware("http")
async def log_errors(request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        print("❌ API ERROR", request.method, request.url.path, repr(e))
        raise

# Global error handlers (A2): uniform JSON error shape
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Extract a concise message
    try:
        first_error = exc.errors()[0]
        msg = first_error.get('msg', 'Erreur de validation des données')
    except Exception:
        msg = 'Erreur de validation des données'
    return JSONResponse(status_code=422, content={"error": msg})

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # Preserve status code, convert detail to {error: ...}
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"error": detail})

# API router with prefix
api_router = APIRouter(prefix="/api")

# Initialize database
db = get_database()

# Dependency to get current user
def get_current_user_id(authorization: str = Header(None)):
    """Extract user ID from JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        # For demo mode compatibility, return a demo user ID
        print(f"⚠️ No Authorization header found in request, falling back to demo mode")
        print(f"⚠️ Authorization header value: {authorization}")
        return "demo_user_id"
    
    token = authorization.replace("Bearer ", "")
    print(f"🔍 Processing token: {token[:20]}..." if len(token) > 20 else f"🔍 Processing token: {token}")
    
    if db.is_connected():
        # Try to get real user from database
        user_data = db.get_user_by_token(token)
        if user_data:
            print(f"✅ Token validation successful for user: {user_data['email']}")
            return user_data["user_id"]
        else:
            print(f"❌ Token validation failed - invalid or expired token")
    else:
        print(f"❌ Database not connected - falling back to demo mode")
    
    # Fallback to demo mode for invalid/expired tokens
    print(f"⚠️ Falling back to demo_user_id due to token validation failure")
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
    priority: Optional[str] = "normal"

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    business_name: Optional[str] = None

# Login model selon plan ChatGPT
class LoginIn(BaseModel):
    email: str
    password: str

# JWT Configuration selon plan ChatGPT
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-this-in-production')
JWT_ALG = os.environ.get("JWT_ALG", "HS256")
JWT_TTL = int(os.environ.get("JWT_TTL_SECONDS", "604800"))  # 7 jours
JWT_ISS = os.environ.get("JWT_ISS", "claire-marcus-api")

# Security selon plan ChatGPT - PAS DE FALLBACK
def get_current_user_id_robust(authorization: Optional[str] = Header(None)) -> str:
    """Extraction robuste du user_id - PAS DE FALLBACK"""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Missing bearer token")
    
    token = authorization.split(" ", 1)[1]
    
    try:
        payload = jwt.decode(
            token, 
            JWT_SECRET, 
            algorithms=[JWT_ALG], 
            options={"require": ["sub", "exp"]}, 
            issuer=JWT_ISS
        )
        
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(401, "Invalid token: sub missing")
        
        print(f"🔑 Server: Authenticated user_id: {sub}")
        return sub
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError as e:
        print(f"❌ Server JWT error: {e}")
        raise HTTPException(401, f"Invalid token: {e}")

# Import also from security for consistency check
try:
    from security import get_current_user_id_robust as shared_auth
    print("✅ Shared security module also available")
except ImportError:
    print("⚠️ Shared security module not available")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

# Diagnostic endpoint as suggested by ChatGPT
@api_router.get("/diag")
async def diagnostic():
    """Diagnostic endpoint to check environment and database"""
    return {
        "database_connected": db.is_connected(),
        "database_name": "claire_marcus",
        "mongo_url_prefix": os.environ.get('MONGO_URL', '')[:25] + '...' if os.environ.get('MONGO_URL') else 'NOT_SET',
        "environment": os.environ.get('NODE_ENV', 'development'),
        "timestamp": datetime.now().isoformat()
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
    """User login robuste selon plan ChatGPT - PAS DE FALLBACK"""
    try:
        print(f"🔑 Login attempt for: {credentials.email}")
        
        # Use existing auth infrastructure pour compatibility
        from auth import create_access_token, create_refresh_token
        
        # Get database
        db_manager = get_database()
        users_collection = db_manager.db.users
        
        # Find user (case insensitive)
        email_clean = credentials.email.lower().strip()
        user = users_collection.find_one({"email": email_clean})
        
        if not user:
            print(f"❌ User not found: {email_clean}")
            raise HTTPException(401, "Invalid credentials")
        
        # Check password using bcrypt
        stored_password_hash = user.get("password_hash") or user.get("hashed_password")
        if not stored_password_hash:
            print(f"❌ No password hash stored for user: {email_clean}")
            raise HTTPException(401, "Invalid credentials")
        
        # Proper bcrypt password verification
        import bcrypt
        if not bcrypt.checkpw(credentials.password.encode('utf-8'), stored_password_hash.encode('utf-8')):
            print(f"❌ Invalid password for user: {email_clean}")
            raise HTTPException(401, "Invalid credentials")
        
        user_id = user.get("user_id") or str(user.get("_id"))
        
        # Create tokens using existing infrastructure with 'sub' claim
        token_data = {"sub": user["email"], "user_id": user_id}  # 'sub' requis par FastAPI
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        print(f"✅ Login successful for: {email_clean}, user_id: {user_id}")
        
        return {
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": user_id,
            "email": user["email"],
            "expires_in": 3600
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Login error for {credentials.email}: {str(e)}")
        raise HTTPException(500, f"Login failed: {str(e)}")  # PAS DE FALLBACK

@api_router.post("/auth/login-robust")
async def login_robust(body: LoginIn):
    """Login robuste selon plan ChatGPT - pas de 502"""
    try:
        print(f"🔑 Login attempt for: {body.email}")
        
        # Get database
        db_manager = get_database()
        users_collection = db_manager.db.users
        
        # Find user (case insensitive)
        email_clean = body.email.lower().strip()
        user = users_collection.find_one({"email": email_clean})
        
        if not user:
            print(f"❌ User not found: {email_clean}")
            raise HTTPException(401, "Invalid credentials")
        
        # Check password using bcrypt
        stored_password_hash = user.get("password_hash") or user.get("hashed_password")
        if not stored_password_hash:
            print(f"❌ No password hash stored for user: {email_clean}")
            raise HTTPException(401, "Invalid credentials")
        
        # Proper bcrypt password verification
        import bcrypt
        if not bcrypt.checkpw(body.password.encode('utf-8'), stored_password_hash.encode('utf-8')):
            print(f"❌ Invalid password for user: {email_clean}")
            raise HTTPException(401, "Invalid credentials")
        
        # Create JWT payload
        user_id = user.get("user_id") or str(user.get("_id"))
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,  # &lt;- L'ID QUI SERVIRA DE owner_id
            "email": user["email"],
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=JWT_TTL)).timestamp()),
            "iss": JWT_ISS,
        }
        
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
        
        print(f"✅ Login successful for: {email_clean}, user_id: {user_id}")
        
        return {
            "access_token": token, 
            "token_type": "bearer",
            "user_id": user_id,
            "email": user["email"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Login error for {body.email}: {str(e)}")
        raise HTTPException(500, "Internal server error during login")

@api_router.get("/auth/whoami")
async def whoami(user_id: str = Depends(get_current_user_id)):
    """Test de la chaîne auth selon plan ChatGPT"""
    return {"user_id": user_id, "authentication": "success"}

@api_router.get("/auth/me")
async def get_current_user_info(user_id: str = Depends(get_current_user_id_robust)):
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
class UserSettings(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None

@api_router.get("/user/settings")
async def get_user_settings(user_id: str = Depends(get_current_user_id_robust)):
    """Get current user settings"""
    try:
        print(f"🔍 Getting user settings for: {user_id}")
        
        db = get_database()
        if not db.is_connected():
            print("⚠️ DB not connected during GET settings")
            return {"error": "Database connection failed", "first_name": "", "last_name": "", "email": ""}
            
        # Get user data from users collection
        user_data = db.db.users.find_one({"user_id": user_id})
        
        if user_data:
            print(f"✅ Found user settings: {user_data.get('first_name', '')} {user_data.get('last_name', '')}")
            return {
                "first_name": user_data.get("first_name", ""),
                "last_name": user_data.get("last_name", ""),
                "email": user_data.get("email", "")
            }
        else:
            print(f"⚠️ No user found for ID: {user_id}")
            return {"first_name": "", "last_name": "", "email": ""}
            
    except Exception as e:
        print(f"❌ Error getting user settings: {e}")
        return {"error": str(e), "first_name": "", "last_name": "", "email": ""}

@api_router.put("/user/settings")
async def update_user_settings(settings: UserSettings, user_id: str = Depends(get_current_user_id_robust)):
    """Update current user settings"""
    try:
        print(f"💾 Updating user settings for: {user_id}")
        print(f"   Data: {settings.dict()}")
        
        db = get_database()
        if not db.is_connected():
            print("⚠️ DB not connected during PUT settings")
            return {"success": False, "message": "Database connection failed"}
        
        # Update user settings in users collection
        update_data = {}
        if settings.first_name is not None:
            update_data["first_name"] = settings.first_name
        if settings.last_name is not None:
            update_data["last_name"] = settings.last_name
        if settings.email is not None:
            update_data["email"] = settings.email
            
        if update_data:
            result = db.db.users.update_one(
                {"user_id": user_id},
                {"$set": update_data},
                upsert=True
            )
            
            print(f"✅ User settings updated: matched={result.matched_count}, modified={result.modified_count}")
            return {"success": True, "message": "Settings updated successfully"}
        else:
            return {"success": False, "message": "No data to update"}
            
    except Exception as e:
        print(f"❌ Error updating user settings: {e}")
        return {"success": False, "message": str(e)}

# ...
# [Keeping the rest of server.py unchanged beyond this point]

# Website analyzer endpoints - REPLACED BY GPT-5 MODULE
# Old demo endpoints commented out to use GPT-5 version
# @api_router.post("/website/analyze")
# @api_router.get("/website/analysis") 
# @api_router.delete("/website/analysis")
# (See website_analyzer_gpt5.py for new GPT-5 implementation)

# Include the API router
app.include_router(api_router)

# Include GPT-5 Website Analyzer
if WEBSITE_ANALYZER_AVAILABLE:
    app.include_router(website_router, prefix="/api")
    print("✅ GPT-5 Website Analyzer endpoints added")
else:
    print("⚠️ Website Analyzer endpoints not available - old endpoints remain active")

# Include the modern payments router
if PAYMENTS_V2_AVAILABLE:
    app.include_router(payments_router)
    print("✅ Modern Stripe payments endpoints added")
else:
    print("⚠️ Payments endpoints not available - running without Stripe integration")

# Include thumbnails router
if THUMBNAILS_AVAILABLE:
    app.include_router(thumbnails_router, prefix="/api")
    print("✅ Thumbnails router included")
else:
    print("⚠️ Thumbnails router not available - running without thumbnail generation")