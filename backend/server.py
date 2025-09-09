from fastapi import FastAPI, APIRouter, HTTPException, Header, Depends, Response, File, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import jwt
from passlib.context import CryptContext
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import os
import uuid
import asyncio
import json
import base64
from PIL import Image
import io
import mimetypes
import aiohttp
import aiofiles

# Enable HEIC/HEIF support for iPhone photos (optional)
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    print("✅ HEIF/HEIC support enabled")
except Exception as e:
    print(f"⚠️ HEIF/HEIC support not available: {e}")

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
    title: Optional[str] = ""
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

try:
    from routes_uploads import router as uploads_router
    UPLOADS_AVAILABLE = True
    print("✅ Uploads (GridFS) module loaded")
except ImportError as e:
    print(f"⚠️ Uploads module not available: {e}")
    UPLOADS_AVAILABLE = False

app = FastAPI(title="Claire et Marcus API", version="1.0.0")

# Enable CORS for external frontends (Netlify, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # We rely on Authorization header, not cookies
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    # Apply no-cache headers to API endpoints EXCEPT thumbnails
    if request.url.path.startswith("/api") and not "/thumb" in request.url.path:
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
    coordinates: Optional[str] = None
    hashtags_primary: List[str] = []
    hashtags_secondary: List[str] = []

class Content(BaseModel):
    """Content model for media items with operational title support"""
    id: Optional[str] = None
    filename: Optional[str] = None
    file_type: Optional[str] = None
    description: Optional[str] = ""
    context: Optional[str] = ""
    title: Optional[str] = Field(None, description="Operational title for content generation and display")
    url: Optional[str] = None
    thumb_url: Optional[str] = None
    uploaded_at: Optional[str] = None
    created_at: Optional[str] = None

class ContentNote(BaseModel):
    description: Optional[str] = Field(None, description="Note title/description")
    content: str = Field(..., description="Note content") 
    priority: Optional[str] = Field("normal", description="Priority level")
    is_monthly_note: Optional[bool] = Field(False, description="Note valid every month")
    note_month: Optional[int] = Field(None, description="Specific month (1-12)")  
    note_year: Optional[int] = Field(None, description="Specific year")

class ContentUpload(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    business_id: str
    file_path: str
    file_type: str  # image, video, note
    description: Optional[str] = None
    title: Optional[str] = None
    content_text: Optional[str] = None
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending_description"

class GeneratedPost(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    business_id: str
    content_id: Optional[str] = None
    platform: str  # facebook, instagram, linkedin
    post_text: str
    hashtags: List[str]
    scheduled_date: datetime
    scheduled_time: str = "09:00"
    status: str = "pending"
    auto_generated: bool = False
    visual_url: Optional[str] = None
    generation_batch: Optional[str] = None
    generation_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

async def analyze_content_with_ai(content_path: str, description: str, business_profile: BusinessProfile, notes: List[ContentNote] = []):
    """Analyze content with AI for post generation"""
    try:
        # Simple mock implementation for testing
        # In production, this would use emergentintegrations LLM
        return [
            {
                "platform": "facebook",
                "post_text": f"Nouveau contenu pour {business_profile.business_name}: {description}",
                "hashtags": ["#entreprise", "#contenu"]
            },
            {
                "platform": "instagram", 
                "post_text": f"Découvrez notre {description} chez {business_profile.business_name}",
                "hashtags": ["#instagram", "#contenu"]
            }
        ]
    except Exception as e:
        print(f"Error in analyze_content_with_ai: {e}")
        return []

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

# ----------------------------
# AUTH: /api/auth/login-robust
# ----------------------------
@api_router.get("/auth/me")
async def who_am_i(user_id: str = Depends(get_current_user_id_robust)):
    """Return basic user payload for the current token"""
    try:
        dbm = get_database()
        user = dbm.db.users.find_one({"user_id": user_id})
        if user:
            return {
                "user_id": user.get("user_id"),
                "email": user.get("email"),
                "first_name": user.get("first_name"),
                "last_name": user.get("last_name"),
                "business_name": user.get("business_name"),
                "subscription_status": user.get("subscription_status", "trial"),
            }
        # Basic payload if user doc not found but token valid
        return {"user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user: {str(e)}")

@api_router.post("/auth/register")
async def register(body: RegisterRequest):
    try:
        dbm = get_database()
        users = dbm.db.users
        email_clean = body.email.lower().strip()
        
        # Check if user already exists
        if users.find_one({"email": email_clean}):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password with bcrypt
        import bcrypt
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(body.password.encode("utf-8"), salt).decode("utf-8")
        
        # Create user
        user_id = str(uuid.uuid4())
        business_name = body.business_name or f"{body.first_name or ''} {body.last_name or ''}".strip()
        
        user_data = {
            "user_id": user_id,
            "email": email_clean,
            "password_hash": hashed_password,
            "business_name": business_name,
            "first_name": body.first_name,
            "last_name": body.last_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
            "is_admin": False,
            "subscription_status": "active",
            # Default business profile fields
            "business_type": None,
            "business_description": None,
            "target_audience": None,
            "brand_tone": None,
            "posting_frequency": None,
            "website_url": None,
            "preferred_platforms": [],
            "budget_range": None,
            "hashtags_primary": [],
            "hashtags_secondary": []
        }
        
        users.insert_one(user_data)
        
        # Generate JWT token for immediate login
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "email": email_clean,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=JWT_TTL)).timestamp()),
            "iss": JWT_ISS,
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user_id,
            "email": email_clean,
            "message": "User registered successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during registration")

@api_router.post("/auth/login-robust")
async def login_robust(body: LoginIn):
    try:
        dbm = get_database()
        users = dbm.db.users
        email_clean = body.email.lower().strip()
        user = users.find_one({"email": email_clean})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        stored_pw = user.get("password_hash") or user.get("hashed_password")
        if not stored_pw:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        import bcrypt
        if not bcrypt.checkpw(body.password.encode("utf-8"), stored_pw.encode("utf-8")):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        user_id = user.get("user_id") or str(user.get("_id"))
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "email": user["email"],
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=JWT_TTL)).timestamp()),
            "iss": JWT_ISS,
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
        return {"access_token": token, "token_type": "bearer", "user_id": user_id, "email": user["email"]}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error during login")

# ----------------------------
# CONTENT LISTING: /api/content/pending
# ----------------------------
@api_router.get("/content/pending")
async def get_pending_content_mongo(offset: int = 0, limit: int = 24, user_id: str = Depends(get_current_user_id_robust)):
    try:
        media_collection = get_media_collection()
        q = {"owner_id": user_id, "$or": [{"deleted": {"$ne": True}}, {"deleted": {"$exists": False}}]}
        total = media_collection.count_documents(q)
        cursor = (
            media_collection.find(q)
            .sort([("created_at", -1), ("_id", -1)])
            .skip(max(0, int(offset)))
            .limit(max(1, int(limit)))
        )
        items = []
        for d in cursor:
            items.append({
                "id": str(d.get("_id")),
                "filename": d.get("filename", ""),
                "file_type": d.get("file_type", ""),
                "url": d.get("url", ""),
                "thumb_url": d.get("thumb_url", ""),
                "description": d.get("description", ""),
                "context": d.get("context", ""),  # Include context field
                "title": d.get("title", ""),  # Include operational title field
                "source": d.get("source", ""),  # Include source field (e.g., "pixabay")
                "save_type": d.get("save_type", ""),  # Include save_type field
                "upload_type": d.get("upload_type", ""),  # Include upload_type field
                "attributed_month": d.get("attributed_month", ""),  # Include attributed_month field
                "carousel_id": d.get("carousel_id", ""),  # Include carousel_id field for grouping
                "common_title": d.get("common_title", ""),  # Include common_title field for carousel
                "created_at": d.get("created_at").isoformat() if d.get("created_at") else None,
                "uploaded_at": d.get("uploaded_at") if d.get("uploaded_at") else None
            })
        return {"content": items, "total": total, "offset": offset, "limit": limit, "has_more": offset + limit < total, "loaded": len(items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch content: {str(e)}")

# ----------------------------
# BUSINESS PROFILE: /api/business-profile
# ----------------------------
BUSINESS_FIELDS = [
    "business_name", "business_type", "business_description", "target_audience",
    "brand_tone", "posting_frequency", "preferred_platforms", "budget_range",
    "email", "website_url", "coordinates", "hashtags_primary", "hashtags_secondary"
]

@api_router.get("/business-profile")
async def get_business_profile(user_id: str = Depends(get_current_user_id_robust)):
    try:
        dbm = get_database()
        business_profiles = dbm.db.business_profiles
        
        # Récupérer le profil business de l'utilisateur depuis business_profiles
        business_profile = business_profiles.find_one({"owner_id": user_id})
        
        if not business_profile:
            # Si pas de profil business, retourner des valeurs par défaut
            return {field: None for field in BUSINESS_FIELDS}
        
        # Mapper les champs du business profile vers la structure attendue
        out = {}
        for field in BUSINESS_FIELDS:
            if field in business_profile:
                out[field] = business_profile[field]
            else:
                out[field] = None
        
        return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch business profile: {str(e)}")

class BusinessProfileIn(BaseModel):
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    business_description: Optional[str] = None
    target_audience: Optional[str] = None
    brand_tone: Optional[str] = None
    posting_frequency: Optional[str] = None
    preferred_platforms: Optional[List[str]] = None
    budget_range: Optional[str] = None
    email: Optional[str] = None
    website_url: Optional[str] = None
    coordinates: Optional[str] = None
    hashtags_primary: Optional[List[str]] = None
    hashtags_secondary: Optional[List[str]] = None

@api_router.put("/business-profile")
async def put_business_profile(body: BusinessProfileIn, user_id: str = Depends(get_current_user_id_robust)):
    try:
        dbm = get_database()
        users = dbm.db.users
        update = {k: v for k, v in body.dict().items() if v is not None}
        if not update:
            return {"success": True, "message": "No changes"}
        users.update_one({"user_id": user_id}, {"$set": update}, upsert=True)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update business profile: {str(e)}")

@api_router.post("/business-profile")
async def post_business_profile(body: BusinessProfileIn, user_id: str = Depends(get_current_user_id_robust)):
    # For compatibility with existing frontend that may POST
    return await put_business_profile(body, user_id)

# ----------------------------
# NOTES: /api/notes
# ----------------------------


@api_router.get("/notes")
async def get_notes(user_id: str = Depends(get_current_user_id_robust)):
    """Get all notes for user"""
    try:
        dbm = get_database()
        notes = dbm.get_notes(user_id)
        return {"notes": notes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch notes: {str(e)}")

@api_router.post("/notes")
async def create_note(note: ContentNote, user_id: str = Depends(get_current_user_id_robust)):
    """Create a new note"""
    try:
        dbm = get_database()
        # Using the existing create_note function with all parameters
        created_note = dbm.create_note(
            user_id=user_id,
            content=note.content,
            description=note.description,
            priority=note.priority,
            is_monthly_note=note.is_monthly_note,
            note_month=note.note_month,
            note_year=note.note_year
        )
        # Add title field for frontend compatibility if description exists
        if note.description:
            created_note['title'] = note.description
        
        return {
            "message": "Note créée avec succès",
            "note": created_note
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create note: {str(e)}")

@api_router.put("/notes/{note_id}")
async def update_note(note_id: str, note: ContentNote, user_id: str = Depends(get_current_user_id_robust)):
    """Update an existing note"""
    try:
        dbm = get_database()
        
        # Update note in content_notes collection
        result = dbm.db.content_notes.update_one(
            {"note_id": note_id, "owner_id": user_id},
            {"$set": {
                "content": note.content,
                "description": note.description,
                "priority": note.priority,
                "is_monthly_note": note.is_monthly_note,
                "note_month": note.note_month,
                "note_year": note.note_year,
                "updated_at": datetime.now().isoformat()
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Get the updated note
        updated_note = dbm.db.content_notes.find_one(
            {"note_id": note_id, "owner_id": user_id},
            {"_id": 0}
        )
        
        return {
            "message": "Note modifiée avec succès",
            "note": updated_note
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update note: {str(e)}")

@api_router.delete("/notes/{note_id}")
async def delete_note(note_id: str, user_id: str = Depends(get_current_user_id_robust)):
    """Delete a note"""
    try:
        dbm = get_database()
        # Delete note from content_notes collection
        result = dbm.db.content_notes.delete_one({
            "note_id": note_id,
            "owner_id": user_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Note not found")
        
        return {"message": "Note supprimée avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete note: {str(e)}")

@api_router.post("/notes/cleanup-expired")
async def cleanup_expired_periodic_notes_manual(user_id: str = Depends(get_current_user_id_robust)):
    """Manually trigger cleanup of expired periodic notes (admin/test function)"""
    try:
        dbm = get_database()
        result = dbm.cleanup_expired_periodic_notes()
        
        return {
            "message": "Cleanup completed",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup notes: {str(e)}")

# ----------------------------
# CONTENT CONTEXT: /api/content/{content_id}/context
# ----------------------------

class ContentContextRequest(BaseModel):
    context: str

class ContentTitleRequest(BaseModel):
    title: str

@api_router.put("/content/{content_id}/context")
async def update_content_context(content_id: str, body: ContentContextRequest, user_id: str = Depends(get_current_user_id_robust)):
    """Update context/description for a content item"""
    try:
        dbm = get_database()
        
        # Update content context in the media collection
        query = parse_any_id(content_id)
        query["owner_id"] = user_id  # Use owner_id to match the content retrieval query
        
        result = dbm.db.media.update_one(
            query,
            {"$set": {
                "context": body.context,
                "updated_at": datetime.now().isoformat()
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Content not found")
        
        return {"message": "Contexte mis à jour avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update content context: {str(e)}")

@api_router.put("/content/{content_id}/title")
async def update_content_title(content_id: str, body: ContentTitleRequest, user_id: str = Depends(get_current_user_id_robust)):
    """Update title for a content item"""
    try:
        dbm = get_database()
        
        # Update content title in the media collection
        query = parse_any_id(content_id)
        query["owner_id"] = user_id
        
        result = dbm.db.media.update_one(
            query,
            {"$set": {"title": body.title}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Content not found")
        
        return {"message": "Titre mis à jour avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update content title: {str(e)}")

@api_router.delete("/content/{content_id}")
async def delete_content(content_id: str, user_id: str = Depends(get_current_user_id_robust)):
    """Delete a content item"""
    try:
        dbm = get_database()
        
        # Delete content from media collection
        query = parse_any_id(content_id)
        query["owner_id"] = user_id  # Use owner_id to match the content retrieval query
        
        result = dbm.db.media.delete_one(query)
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Content not found")
        
        return {"message": "Contenu supprimé avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete content: {str(e)}")

# ----------------------------
# POSTS GENERATION: /api/posts
# ----------------------------

@api_router.post("/posts/generate")
async def generate_posts_manual(user_id: str = Depends(get_current_user_id_robust)):
    """Generate posts manually for the current month"""
    try:
        # Import the scheduler here to avoid circular imports
        from scheduler import ContentScheduler
        
        scheduler = ContentScheduler()
        
        # Generate posts for the current user/business
        result = await scheduler.generate_posts_automatically(user_id)
        
        if result:
            return {
                "message": "Posts générés avec succès",
                "posts_generated": result.get("posts_generated", 0),
                "business_id": user_id
            }
        else:
            return {
                "message": "Génération terminée",
                "posts_generated": 0,
                "business_id": user_id
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate posts: {str(e)}")

@api_router.get("/posts/generated")
async def get_generated_posts(user_id: str = Depends(get_current_user_id_robust)):
    """Get all generated posts for the user"""
    try:
        dbm = get_database()
        
        # Get generated posts from the database
        posts = list(dbm.db.generated_posts.find(
            {"user_id": user_id},
            {"_id": 0}  # Exclude MongoDB _id field
        ).sort("scheduled_date", -1))  # Sort by scheduled date, newest first
        
        return {"posts": posts}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch generated posts: {str(e)}")

# ----------------------------
# PIXABAY INTEGRATION: /api/pixabay
# ----------------------------

PIXABAY_API_KEY = os.environ.get('PIXABAY_API_KEY')
PIXABAY_BASE_URL = "https://pixabay.com/api/"

class PixabaySearchRequest(BaseModel):
    query: str
    page: int = 1
    per_page: int = 20
    image_type: str = "photo"
    orientation: str = "all"
    min_width: int = 0
    min_height: int = 0
    safesearch: bool = True

class PixabayImage(BaseModel):
    id: int
    pageURL: str
    type: str
    tags: str
    previewURL: str
    webformatURL: str
    largeImageURL: str
    views: int
    downloads: int
    favorites: int
    likes: int
    user: str
    userImageURL: str

@api_router.get("/pixabay/search")
async def search_pixabay_images(
    query: str,
    page: int = 1,
    per_page: int = 20,
    image_type: str = "photo",
    orientation: str = "all",
    min_width: int = 0,
    min_height: int = 0,
    safesearch: bool = True
):
    """Search for images on Pixabay"""
    if not PIXABAY_API_KEY:
        raise HTTPException(status_code=500, detail="Pixabay API key not configured")
    
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "page": page,
        "per_page": min(per_page, 200),
        "image_type": image_type,
        "orientation": orientation,
        "min_width": min_width,
        "min_height": min_height,
        "safesearch": str(safesearch).lower(),
        "order": "popular",
        "lang": "fr",  # Forcer les résultats en français
        "category": "backgrounds,business,computer,fashion,food,health,people,places,science,sports,travel"
    }
    
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(PIXABAY_BASE_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "total": data.get("total", 0),
                        "totalHits": data.get("totalHits", 0),
                        "hits": data.get("hits", [])
                    }
                elif response.status == 429:
                    raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
                else:
                    raise HTTPException(status_code=response.status, detail=f"Pixabay API error: {response.reason}")
                    
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@api_router.post("/pixabay/save-image")
async def save_pixabay_image(
    request: dict,
    user_id: str = Depends(get_current_user_id_robust)
):
    """Save a Pixabay image to user's library"""
    try:
        # Extract data from request
        pixabay_id = request.get("pixabay_id")
        image_url = request.get("image_url")
        tags = request.get("tags", "")
        custom_title = request.get("custom_title", "")
        custom_context = request.get("custom_context", "")
        save_type = request.get("save_type", "general")  # "general" or "monthly"
        attributed_month = request.get("attributed_month")  # e.g., "septembre_2025"
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())[:8]
        filename = f"pixabay_{pixabay_id}_{unique_id}.jpg"
        
        # Create upload directory if it doesn't exist
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)
        
        # Download image from Pixabay
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    async with aiofiles.open(file_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
                else:
                    raise HTTPException(status_code=500, detail="Failed to download image")
        
        # Get image dimensions and file size
        with Image.open(file_path) as img:
            width, height = img.size
        file_size = os.path.getsize(file_path)
        
        # Save to database using the same collection as content/pending
        media_collection = get_media_collection()
        # Generate document ID first
        doc_id = str(uuid.uuid4())
        
        # Use custom context if provided, otherwise default context
        if custom_context:
            context_msg = custom_context
        elif save_type == "monthly" and attributed_month:
            context_msg = f"Image Pixabay pour {attributed_month.replace('_', ' ')} - {tags}"
        else:
            context_msg = f"Image from Pixabay - {tags}"
            
        # Use custom title if provided, otherwise use tags
        display_title = custom_title if custom_title else tags
        
        media_doc = {
            "id": doc_id,
            "owner_id": user_id,  # Use owner_id to match content/pending query
            "filename": filename,
            "original_filename": f"pixabay_{pixabay_id}.jpg",
            "file_path": image_url,  # Store original Pixabay URL
            "file_size": file_size,
            "file_type": "image/jpeg",
            "width": width,
            "height": height,
            "uploaded_at": datetime.now().isoformat(),
            "created_at": datetime.now(),
            "source": "pixabay",
            "pixabay_id": pixabay_id,
            "tags": tags,
            "title": display_title,  # Use custom title or fallback to tags
            "context": context_msg,  # Use custom context or generated one
            "url": image_url,  # Use original Pixabay URL for full image
            "thumb_url": f"/api/content/{doc_id}/thumb",  # Use optimized thumbnail endpoint
            "is_external": True,  # Flag to indicate external image
            "save_type": save_type,  # Track how this was saved
            "attributed_month": attributed_month if save_type == "monthly" else None  # Month attribution
        }
        
        media_collection.insert_one(media_doc)
        media_doc.pop('_id', None)  # Remove MongoDB _id
        
        return {
            "message": "Image saved successfully",
            "image": media_doc
        }
        
    except Exception as e:
        # Clean up file if it was created
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to save image: {str(e)}")

@api_router.get("/pixabay/categories")
async def get_pixabay_categories():
    """Get available Pixabay image categories"""
    categories = [
        "backgrounds", "fashion", "nature", "science", "education",
        "feelings", "health", "people", "religion", "places",
        "animals", "industry", "computer", "food", "sports",
        "transportation", "travel", "buildings", "business", "music"
    ]
    return {"categories": categories}

# Include the API router (auth endpoints need to stay without prefix)
app.include_router(api_router)

# Include GPT-5 Website Analyzer
if WEBSITE_ANALYZER_AVAILABLE:
    app.include_router(website_router, prefix="/api")
    print("✅ GPT-5 Website Analyzer endpoints added")

# Include thumbnails router
if THUMBNAILS_AVAILABLE:
    app.include_router(thumbnails_router, prefix="/api")
    print("✅ Thumbnails router included")

# Include uploads router (GridFS)
if UPLOADS_AVAILABLE:
    app.include_router(uploads_router, prefix="/api")
    print("✅ Uploads router included")

# Include payments router
if PAYMENTS_V2_AVAILABLE:
    app.include_router(payments_router)
    print("✅ Modern Stripe payments endpoints added")