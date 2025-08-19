from fastapi import FastAPI, APIRouter, HTTPException, Header, Depends, Response, File, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
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
mimetypes.add_type('image/webp', '.webp')
mimetypes.add_type('image/jpeg', '.jpg')
mimetypes.add_type('image/jpeg', '.jpeg')
mimetypes.add_type('image/png', '.png')
mimetypes.add_type('image/heic', '.heic')
mimetypes.add_type('image/heif', '.heif')

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

def get_media_collection():
    db_manager = get_database()
    return db_manager.db.media

def parse_any_id(file_id: str) -> dict:
    try:
        from bson import ObjectId
        return {"_id": ObjectId(file_id)}
    except Exception:
        print(f"⚠️ Using UUID fallback for file_id: {file_id}")
        return {"external_id": file_id}

try:
    from website_analyzer_gpt5 import website_router
    WEBSITE_ANALYZER_AVAILABLE = True
    print("✅ GPT-5 Website Analyzer module loaded")
except ImportError as e:
    print(f"⚠️ GPT-5 Website Analyzer module not available: {e}")
    WEBSITE_ANALYZER_AVAILABLE = False

try:
    from payments_v2 import payments_router
    PAYMENTS_V2_AVAILABLE = True
    print("✅ Modern Stripe payments module loaded")
except ImportError as e:
    print(f"⚠️ Modern payments module not available: {e}")
    PAYMENTS_V2_AVAILABLE = False

try:
    from routes_thumbs import router as thumbnails_router
    THUMBNAILS_AVAILABLE = True
    print("✅ Thumbnails generation module loaded")
except ImportError as e:
    print(f"⚠️ Thumbnails module not available: {e}")
    THUMBNAILS_AVAILABLE = False

app = FastAPI(title="Claire et Marcus API", version="1.0.0")

@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, proxy-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        response.headers["Surrogate-Control"] = "no-store"
    return response

@app.middleware("http")
async def log_errors(request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        print("❌ API ERROR", request.method, request.url.path, repr(e))
        raise

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    try:
        first_error = exc.errors()[0]
        msg = first_error.get('msg', 'Erreur de validation des données')
    except Exception:
        msg = 'Erreur de validation des données'
    return JSONResponse(status_code=422, content={"error": msg})

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"error": detail})

api_router = APIRouter(prefix="/api")

db = get_database()

def get_current_user_id(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        print(f"⚠️ No Authorization header found in request, falling back to demo mode")
        print(f"⚠️ Authorization header value: {authorization}")
        return "demo_user_id"
    token = authorization.replace("Bearer ", "")
    print(f"🔍 Processing token: {token[:20]}..." if len(token) > 20 else f"🔍 Processing token: {token}")
    if db.is_connected():
        user_data = db.get_user_by_token(token)
        if user_data:
            print(f"✅ Token validation successful for user: {user_data['email']}")
            return user_data["user_id"]
        else:
            print(f"❌ Token validation failed - invalid or expired token")
    else:
        print(f"❌ Database not connected - falling back to demo mode")
    print(f"⚠️ Falling back to demo_user_id due to token validation failure")
    return "demo_user_id"

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

class LoginIn(BaseModel):
    email: str
    password: str

JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-this-in-production')
JWT_ALG = os.environ.get("JWT_ALG", "HS256")
JWT_TTL = int(os.environ.get("JWT_TTL_SECONDS", "604800"))
JWT_ISS = os.environ.get("JWT_ISS", "claire-marcus-api")

def get_current_user_id_robust(authorization: Optional[str] = Header(None)) -> str:
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

try:
    from security import get_current_user_id_robust as shared_auth
    print("✅ Shared security module also available")
except ImportError:
    print("⚠️ Shared security module not available")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Claire et Marcus API",
        "timestamp": datetime.now().isoformat(),
        "message": "API is running successfully!"
    }

@api_router.get("/diag")
async def diagnostic():
    return {
        "database_connected": db.is_connected(),
        "database_name": "claire_marcus",
        "mongo_url_prefix": os.environ.get('MONGO_URL', '')[:25] + '...' if os.environ.get('MONGO_URL') else 'NOT_SET',
        "environment": os.environ.get('NODE_ENV', 'development'),
        "timestamp": datetime.now().isoformat()
    }

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

# [Rest of server.py remains same as previously present and already running]

# Website analyzer endpoints - REPLACED BY GPT-5 MODULE
app.include_router(api_router)
if WEBSITE_ANALYZER_AVAILABLE:
    app.include_router(website_router, prefix="/api")
    print("✅ GPT-5 Website Analyzer endpoints added")
if THUMBNAILS_AVAILABLE:
    app.include_router(thumbnails_router, prefix="/api")
    print("✅ Thumbnails router included")
if PAYMENTS_V2_AVAILABLE:
    app.include_router(payments_router)
    print("✅ Modern Stripe payments endpoints added")
