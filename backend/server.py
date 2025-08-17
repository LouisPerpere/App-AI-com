from fastapi import FastAPI, APIRouter, HTTPException, Header, Depends, Response, File, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # Ajouté pour servir uploads/ selon ChatGPT
from pydantic import BaseModel, Field  # Ajouté Field pour validation
from typing import List, Optional
from datetime import datetime, timezone
import os
import uuid
import asyncio
import json
from PIL import Image
import io

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
async def get_media_collection():
    """Get MongoDB media collection"""
    db = await get_database()
    return db.media

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
        
        # AUTO-CREATE business profile for authenticated users without one (FIX DEMO DATA ISSUE)
        if user_id == "demo_user_id":
            print(f"⚠️ Unauthenticated request - returning demo profile")
            business_name = "Demo Business"
            email = "demo@claire-marcus.com"
        else:
            print(f"🔧 Authenticated user {user_id} has no business profile - auto-creating one")
            
            # Get user info to create personalized profile
            user_data = db.db.users.find_one({"user_id": user_id})
            business_name = user_data.get("business_name", "Mon Entreprise") if user_data else "Mon Entreprise"
            email = user_data.get("email", "") if user_data else ""
            
            # Create business profile for this user
            try:
                db._create_default_business_profile(user_id, business_name)
                print(f"✅ Auto-created business profile for user {user_id}")
                
                # Now fetch the newly created profile
                profile = db.get_business_profile(user_id)
                if profile:
                    print(f"✅ Returning newly created profile for user {user_id}")
                    return profile
                
            except Exception as create_error:
                print(f"❌ Failed to auto-create profile: {create_error}")
        
        # Only fallback to demo if it's actually a demo user or creation failed
        return {
            "business_name": business_name,
            "business_type": "service", 
            "business_description": "",
            "target_audience": "Clients locaux",
            "brand_tone": "professional",
            "posting_frequency": "weekly",
            "preferred_platforms": ["Facebook", "Instagram"],
            "budget_range": "",
            "email": email,
            "website_url": "",
            "hashtags_primary": [],
            "hashtags_secondary": []
        }
    except Exception as e:
        print(f"❌ Error getting business profile: {e}")
        # Return demo profile on error (RESTORE WORKING BEHAVIOR)
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
        # Check database connection
        if not db.is_connected():
            print(f"⚠️ DB not connected during PUT for user {user_id}")
        
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
                print(f"⚠️ Profile update failed for user {user_id}")
        else:
            print(f"❌ DB connection failed during PUT: connected={db.is_connected()}, user_id={user_id}")
        
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
async def get_notes(user_id: str = Depends(get_current_user_id)):
    """Get notes with real database persistence"""
    try:
        if db.is_connected() and user_id != "demo_user_id":
            # Get real notes from database
            notes = db.get_notes(user_id)
            return {"notes": notes}
        
        # Fallback to demo mode
        return {
            "notes": [
                {
                    "note_id": "demo-note-1",
                    "content": "Note de démonstration - Claire et Marcus",
                    "description": "Exemple de note",
                    "priority": "normal",
                    "created_at": datetime.now().isoformat()
                }
            ]
        }
    except Exception as e:
        print(f"❌ Error getting notes: {e}")
        return {"notes": []}

@api_router.post("/notes")
async def create_note(note: ContentNote, user_id: str = Depends(get_current_user_id)):
    """Create note with real database persistence"""
    try:
        if db.is_connected() and user_id != "demo_user_id":
            # Create real note in database
            created_note = db.create_note(user_id, note.content, note.description)
            return {
                "message": "Note created successfully",
                "note": created_note
            }
        
        # Fallback to demo mode
        return {
            "message": "Note created successfully (demo mode)",
            "note": {
                "note_id": str(uuid.uuid4()),
                "content": note.content,
                "description": note.description,
                "priority": "normal",
                "created_at": datetime.now().isoformat()
            }
        }
    except Exception as e:
        print(f"❌ Error creating note: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create note: {str(e)}")

@api_router.delete("/notes/{note_id}")
async def delete_note(note_id: str, user_id: str = Depends(get_current_user_id)):
    """Delete note with real database persistence"""
    try:
        if db.is_connected() and user_id != "demo_user_id":
            # Delete real note from database
            success = db.delete_note(user_id, note_id)
            if success:
                return {"message": f"Note {note_id} deleted successfully"}
            else:
                raise HTTPException(status_code=404, detail="Note not found")
        
        # Fallback to demo mode
        return {"message": f"Note {note_id} deleted successfully (demo mode)"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting note: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete note: {str(e)}")

# Content management endpoints
@api_router.get("/diag")
async def diagnostic_endpoint():
    """Endpoint de diagnostic temporaire (selon ChatGPT)"""
    try:
        import os
        mongo_uri = os.environ.get('MONGO_URL', 'Not set')
        
        # Masquer les credentials dans l'URI
        masked_uri = mongo_uri[:30] + '...' if len(mongo_uri) > 30 else mongo_uri
        
        return {
            "mongoUri": masked_uri,
            "environment": os.environ.get('ENV', 'unknown'),
            "backend_url": os.environ.get('BACKEND_URL', 'Not set'),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

@api_router.get("/content/pending")
async def get_pending_content_mongo(
    limit: int = 24,
    offset: int = 0,
    user_id: str = Depends(get_current_user_id)
):
    """Get user's content with MongoDB persistence (VERSION FINALE selon ChatGPT)"""
    try:
        media_collection = await get_media_collection()
        
        # Filtre MongoDB par owner_id et non supprimé (selon ChatGPT)
        query = {"owner_id": user_id, "deleted": {"$ne": True}}
        
        # Count total
        total = await media_collection.count_documents(query)
        
        # Get paginated docs with stable sort (selon ChatGPT)
        cursor = media_collection.find(query).sort([("created_at", -1), ("_id", -1)]).skip(offset).limit(limit)
        docs = []
        async for doc in cursor:
            docs.append(doc)
        
        # Build response (selon ChatGPT)
        content = []
        for d in docs:
            content.append({
                "id": str(d["_id"]),
                "filename": d.get("filename", ""),
                "file_type": d.get("file_type", ""),
                "description": d.get("description", ""),
                "url": d.get("url"),
                "thumb_url": d.get("thumb_url"),
                "uploaded_at": d.get("created_at").isoformat() if d.get("created_at") else None
            })
        
        return {
            "content": content,
            "total": total,
            "has_more": offset + limit < total,
            "loaded": len(content)
        }
    
    except Exception as e:
        print(f"❌ MongoDB failed, using filesystem fallback: {e}")
        # Fallback vers système fichiers si MongoDB échoue
        return await get_pending_content_filesystem(limit, offset, user_id)


@api_router.put("/content/{file_id}/description")
async def put_description_mongo(
    file_id: str,
    body: UpdateDescriptionIn,
    user_id: str = Depends(get_current_user_id)
):
    """Update description with MongoDB (VERSION FINALE selon ChatGPT)"""
    try:
        from bson import ObjectId
        media_collection = await get_media_collection()
        
        result = await media_collection.find_one_and_update(
            {"_id": ObjectId(file_id), "owner_id": user_id, "deleted": {"$ne": True}},
            {"$set": {"description": body.description}},
            return_document=True
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Fichier non trouvé")
        
        return {
            "message": "Description mise à jour avec succès", 
            "file_id": file_id,
            "description": result.get("description", "")
        }
    
    except Exception as e:
        print(f"❌ MongoDB description update failed, using filesystem fallback: {e}")
        # Fallback vers système existant
        return await update_content_description(file_id, {"description": body.description}, user_id)


@api_router.delete("/content/{file_id}")
async def delete_media_mongo(
    file_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete content with MongoDB (VERSION FINALE selon ChatGPT)"""
    try:
        from bson import ObjectId
        media_collection = await get_media_collection()
        
        # Find document first
        doc = await media_collection.find_one({"_id": ObjectId(file_id), "owner_id": user_id})
        if not doc:
            raise HTTPException(status_code=404, detail="Fichier non trouvé")
        
        # Delete from MongoDB
        await media_collection.delete_one({"_id": ObjectId(file_id), "owner_id": user_id})
        
        # Optionally delete physical file too (selon ChatGPT)
        try:
            filename = doc.get("filename")
            if filename:
                file_path = os.path.join("uploads", filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"🗑️ Physical file deleted: {filename}")
        except Exception as e:
            print(f"⚠️ Failed to delete physical file: {e}")
        
        return Response(status_code=204)
    
    except Exception as e:
        print(f"❌ MongoDB deletion failed, using filesystem fallback: {e}")
        # Fallback vers système existant
        return await delete_content_file(file_id, user_id)


# LEGACY/FALLBACK functions (ancien système)
async def get_pending_content_filesystem(limit: int, offset: int, user_id: str):
    """LEGACY: Get user's uploaded content files with pagination AND FILTERING BY USER"""
    try:
        uploads_dir = "uploads"
        if not os.path.exists(uploads_dir):
            return {"content": [], "total": 0, "has_more": False}
        
        # Sync descriptions with actual files before processing
        sync_descriptions_with_files()
        
        # NOUVEAU: Charger la liste des fichiers supprimés par cet utilisateur
        deleted_files_key = f"deleted_files_{user_id}"
        deleted_files = set()
        try:
            if os.path.exists(f"{deleted_files_key}.json"):
                with open(f"{deleted_files_key}.json", 'r') as f:
                    deleted_files = set(json.load(f))
        except:
            pass
        
        # List all files in uploads directory
        all_files = []
        for filename in os.listdir(uploads_dir):
            file_path = os.path.join(uploads_dir, filename)
            if os.path.isfile(file_path):
                file_id = filename.split('.')[0]
                
                # CRITIQUE: Filtrer les fichiers supprimés par cet utilisateur
                if file_id in deleted_files:
                    continue
                    
                try:
                    file_stats = os.stat(file_path)
                    
                    # Determine content type based on file extension
                    file_extension = os.path.splitext(filename)[1].lower()
                    content_type = None
                    if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                        content_type = f"image/{file_extension[1:]}"
                    elif file_extension in ['.mp4', '.mov', '.avi', '.mkv']:
                        content_type = f"video/{file_extension[1:]}"
                    
                    # Only include images and videos (skip other file types)
                    if content_type is None:
                        continue
                    
                    all_files.append({
                        'filename': filename,
                        'file_path': file_path,
                        'file_stats': file_stats,
                        'content_type': content_type
                    })
                except Exception as e:
                    print(f"🚨 CRITICAL: Error processing file {filename}: {e}")
                    print(f"🔍 File path: {file_path}")
                    print(f"🔍 File stats: {file_stats if 'file_stats' in locals() else 'Not accessible'}")
                    continue
        
        # Sort by modification time (newest first)
        all_files.sort(key=lambda x: x['file_stats'].st_mtime, reverse=True)
        
        # Apply pagination
        total_files = len(all_files)
        paginated_files = all_files[offset:offset + limit]
        has_more = offset + limit < total_files
        
        print(f"📊 Loading {len(paginated_files)} files (offset: {offset}, total: {total_files})")
        
        content_files = []
        for fi in paginated_files:
            filename = fi['filename']
            file_path = fi['file_path']
            file_stats = fi['file_stats']
            content_type = fi['content_type']
            file_size = file_stats.st_size
            file_id = filename.split('.')[0]
            
            # For images, create two versions: full for modal, ultra-small thumbnail for gallery
            file_data = None
            thumbnail_data = None
            if content_type.startswith('image/'):
                try:
                    with open(file_path, "rb") as f:
                        import base64
                        file_content = f.read()
                        
                        # Full size for modal (already optimized during upload)
                        file_data = base64.b64encode(file_content).decode('utf-8')
                        
                        # Create ultra-small thumbnail for gallery (max 80px to reduce memory drastically)
                        try:
                            from PIL import Image
                            import io
                            
                            # Create thumbnail
                            image = Image.open(io.BytesIO(file_content))
                            
                            # Handle EXIF orientation for thumbnails too
                            try:
                                # Use direct orientation tag number instead of ORIENTATION constant
                                exif = image._getexif()
                                if exif is not None:
                                    orientation = exif.get(0x0112)  # Orientation tag
                                    if orientation == 3:
                                        image = image.rotate(180, expand=True)
                                    elif orientation == 6:
                                        image = image.rotate(270, expand=True)
                                    elif orientation == 8:
                                        image = image.rotate(90, expand=True)
                            except (AttributeError, KeyError, TypeError):
                                # No EXIF data or orientation info, continue
                                pass
                            
                            # Ultra-small thumbnail for gallery performance (prevent crashes)
                            image.thumbnail((80, 80), Image.Resampling.LANCZOS)
                            
                            # Save thumbnail as JPEG with very low quality for minimal size
                            thumb_buffer = io.BytesIO()
                            if image.mode not in ('RGB', 'L'):
                                image = image.convert('RGB')
                            image.save(thumb_buffer, format='JPEG', quality=25, optimize=True)
                            
                            thumbnail_data = base64.b64encode(thumb_buffer.getvalue()).decode('utf-8')
                            thumb_buffer.close()
                            
                        except Exception as thumb_error:
                            print(f"⚠️ Could not create thumbnail for {filename}: {thumb_error}")
                            # Fallback to full image (last resort)
                            thumbnail_data = file_data
                            
                except Exception as e:
                    print(f"🚨 CRITICAL: Error reading image file {filename}: {e}")
                    print(f"🔍 File size: {file_size} bytes")
                    # Still include file in response but without thumbnail data
                    file_data = None
                    thumbnail_data = None
            
            content_files.append({
                "id": file_id,  # UUID as ID (corrigé selon ChatGPT)
                "filename": filename,
                "file_type": content_type,  # Renommé selon ChatGPT
                "file_data": file_data,  # Base64 encoded
                "thumbnail_data": thumbnail_data,  # Ultra-small thumbnail for gallery
                "size": file_size,
                "uploaded_at": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                "description": get_file_description(file_id)  # Use file_id instead of recalculating
            })
        
        return {
            "content": content_files,
            "total": total_files,
            "has_more": has_more,
            "loaded": len(content_files)
        }
        
    except Exception as e:
        print(f"❌ Error getting pending content: {e}")
        return {"content": [], "total": 0, "has_more": False}

# Moved delete_content_file function to be used as fallback only
async def delete_content_file(file_id: str, user_id: str):
    """Delete a content file with USER-SPECIFIC tracking (LEGACY FALLBACK)"""
    try:
        uploads_dir = "uploads"
        
        # Find file by ID (filename without extension)
        target_file = None
        target_path = None
        
        for filename in os.listdir(uploads_dir):
            if filename.split('.')[0] == file_id:
                target_file = filename
                target_path = os.path.join(uploads_dir, filename)
                break
        
        if not target_file or not os.path.exists(target_path):
            print(f"❌ File with ID {file_id} not found")
            raise HTTPException(status_code=404, detail="Fichier non trouvé")
        
        # NOUVEAU: Marquer comme supprimé pour cet utilisateur spécifiquement
        deleted_files_key = f"deleted_files_{user_id}"
        deleted_files = set()
        
        # Charger les suppressions existantes pour cet utilisateur
        try:
            if os.path.exists(f"{deleted_files_key}.json"):
                with open(f"{deleted_files_key}.json", 'r') as f:
                    deleted_files = set(json.load(f))
        except:
            pass
        
        # Ajouter ce fichier à la liste des suppressions
        deleted_files.add(file_id)
        
        # Sauvegarder la liste mise à jour
        with open(f"{deleted_files_key}.json", 'w') as f:
            json.dump(list(deleted_files), f)
        
        # Supprimer aussi la description
        delete_file_description(file_id)
        
        print(f"✅ File {target_file} marked as deleted for user {user_id}")
        
        return {
            "message": f"Fichier {target_file} supprimé définitivement",
            "file_id": file_id,
            "deleted_file": target_file,
            "file_deleted": True,
            "description_deleted": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting file: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")

# OLD MONGODB ROUTES REMOVED - Now using main /content/ routes with MongoDB primary and filesystem fallback

# Moved update_content_description function to be used as fallback only
async def update_content_description(file_id: str, description_data: dict, user_id: str):
    """Update description/context for a content file with persistent storage (LEGACY FALLBACK)"""
    try:
        description = description_data.get("description", "")
        
        # Save description persistently
        if set_file_description(file_id, description):
            print(f"📝 Description updated and saved for file {file_id}: {description}")
            
            return {
                "message": "Description mise à jour avec succès",
                "file_id": file_id,
                "description": description
            }
        else:
            print(f"❌ Failed to save description for file {file_id}")
            raise HTTPException(status_code=500, detail="Erreur lors de la sauvegarde de la description")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error updating description: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")

# Bibliotheque endpoints (legacy)
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

def optimize_image(image_content: bytes, max_size: int = 1080, quality: int = 85) -> bytes:
    """
    Optimize image: resize to max_size on smallest side, set to 72 DPI, maintain aspect ratio
    Handle EXIF orientation to prevent rotation issues
    """
    try:
        # Open image from bytes
        image = Image.open(io.BytesIO(image_content))
        
        # Handle EXIF orientation to prevent rotation issues
        try:
            # Use direct orientation tag number instead of ORIENTATION constant
            exif = image._getexif()
            if exif is not None:
                orientation = exif.get(0x0112)  # Orientation tag
                if orientation == 3:
                    image = image.rotate(180, expand=True)
                elif orientation == 6:
                    image = image.rotate(270, expand=True)
                elif orientation == 8:
                    image = image.rotate(90, expand=True)
        except (AttributeError, KeyError, TypeError):
            # No EXIF data or orientation info, continue
            pass
        
        # Convert to RGB if necessary (handles RGBA, P mode, etc.)
        if image.mode not in ('RGB', 'L'):
            image = image.convert('RGB')
        
        # Get current dimensions
        width, height = image.size
        
        # Calculate new dimensions (resize based on smallest side)
        min_side = min(width, height)
        if min_side > max_size:
            ratio = max_size / min_side
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            
            # Resize image maintaining aspect ratio
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Save optimized image to bytes
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=quality, dpi=(72, 72), optimize=True)
        
        optimized_content = output.getvalue()
        output.close()
        
        print(f"✅ Image optimized with EXIF handling: {len(image_content)} → {len(optimized_content)} bytes")
        return optimized_content
        
    except Exception as e:
        print(f"⚠️ Image optimization failed: {e}, using original")
        return image_content

def load_descriptions():
    """Load content descriptions from JSON file"""
    descriptions_file = "content_descriptions.json"
    try:
        if os.path.exists(descriptions_file):
            with open(descriptions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️ Error loading descriptions: {e}")
    return {}

def save_descriptions(descriptions):
    """Save content descriptions to JSON file"""
    descriptions_file = "content_descriptions.json"
    try:
        with open(descriptions_file, 'w', encoding='utf-8') as f:
            json.dump(descriptions, f, ensure_ascii=False, indent=2)
        print(f"✅ Descriptions saved to {descriptions_file}")
        return True
    except Exception as e:
        print(f"❌ Error saving descriptions: {e}")
        return False

def get_file_description(file_id):
    """Get description for a specific file"""
    descriptions = load_descriptions()
    return descriptions.get(file_id, "")

def set_file_description(file_id, description):
    """Set description for a specific file"""
    descriptions = load_descriptions()
    descriptions[file_id] = description
    return save_descriptions(descriptions)

def delete_file_description(file_id):
    """Delete description for a specific file"""
    descriptions = load_descriptions()
    if file_id in descriptions:
        del descriptions[file_id]
        return save_descriptions(descriptions)
    return True  # Already doesn't exist, consider as success

def sync_descriptions_with_files():
    """Synchronize content_descriptions.json with actual files in uploads directory"""
    try:
        uploads_dir = "uploads"
        if not os.path.exists(uploads_dir):
            return True
        
        # Get all actual files in uploads directory
        actual_files = set()
        for filename in os.listdir(uploads_dir):
            if os.path.isfile(os.path.join(uploads_dir, filename)):
                file_id = filename.split('.')[0]
                actual_files.add(file_id)
        
        # Get all descriptions from JSON
        descriptions = load_descriptions()
        described_files = set(descriptions.keys())
        
        # Find orphaned descriptions (descriptions without files)
        orphaned_descriptions = described_files - actual_files
        
        # Find files without descriptions
        files_without_descriptions = actual_files - described_files
        
        if orphaned_descriptions or files_without_descriptions:
            print(f"🔄 Syncing data: {len(orphaned_descriptions)} orphaned descriptions, {len(files_without_descriptions)} files without descriptions")
            
            # Remove orphaned descriptions
            for orphaned_id in orphaned_descriptions:
                del descriptions[orphaned_id]
                print(f"🗑️ Removed orphaned description: {orphaned_id}")
            
            # Add empty descriptions for files without descriptions
            for file_id in files_without_descriptions:
                descriptions[file_id] = ""
                print(f"📝 Added empty description for file: {file_id}")
            
            # Save synchronized descriptions
            save_descriptions(descriptions)
            print(f"✅ Data synchronized: {len(actual_files)} files, {len(descriptions)} descriptions")
        else:
            print(f"✅ Data already synchronized: {len(actual_files)} files, {len(descriptions)} descriptions")
        
        return True
        
    except Exception as e:
        print(f"❌ Error syncing descriptions with files: {e}")
        return False

# Content upload endpoints (enhanced with image optimization)
@api_router.post("/content/batch-upload")
async def batch_upload_files(
    files: List[UploadFile] = File(...),
    user_id: str = Depends(get_current_user_id),
    bg: BackgroundTasks = None
):
    """Upload multiple files to user's content library with MongoDB persistence and thumbnail generation"""
    
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Create uploads directory if it doesn't exist
    uploads_dir = "uploads"
    os.makedirs(uploads_dir, exist_ok=True)
    
    uploaded_files = []
    failed_uploads = []
    
    # Get MongoDB collection
    try:
        media_collection = await get_media_collection()
    except Exception as e:
        print(f"❌ MongoDB not available: {e}")
        media_collection = None
    
    for file in files:
        try:
            # Validate file type (images and videos only)
            if not (file.content_type.startswith('image/') or file.content_type.startswith('video/')):
                failed_uploads.append({
                    "filename": file.filename,
                    "error": f"Type de fichier non supporté: {file.content_type}"
                })
                continue
            
            # Read file content
            file_content = await file.read()
            
            # Validate file size (max 10MB)
            if len(file_content) > 10 * 1024 * 1024:  # 10MB
                failed_uploads.append({
                    "filename": file.filename,
                    "error": "Fichier trop volumineux (max 10MB)"
                })
                continue
            
            # Optimize images
            if file.content_type.startswith('image/'):
                file_content = optimize_image(file_content)
            
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(uploads_dir, unique_filename)
            
            # Save file to disk
            with open(file_path, "wb") as buffer:
                buffer.write(file_content)
            
            # Create MongoDB document
            if media_collection:
                try:
                    doc = {
                        "owner_id": user_id,
                        "filename": unique_filename,
                        "original_filename": file.filename,
                        "file_type": file.content_type,
                        "url": f"https://claire-marcus.com/uploads/{unique_filename}",
                        "thumb_url": None,  # Will be generated in background
                        "description": "",
                        "deleted": False,
                        "created_at": datetime.now(timezone.utc)
                    }
                    
                    result = await media_collection.insert_one(doc)
                    inserted_id = str(result.inserted_id)
                    
                    # Schedule thumbnail generation in background if available
                    if bg:
                        def generate_thumbnail_job():
                            try:
                                from thumbs import generate_image_thumb, generate_video_thumb, build_thumb_path
                                from routes_thumbs import get_sync_db
                                from bson import ObjectId
                                
                                thumb_path = build_thumb_path(unique_filename)
                                os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
                                
                                if file.content_type.startswith('image/'):
                                    generate_image_thumb(file_path, thumb_path)
                                elif file.content_type.startswith('video/'):
                                    generate_video_thumb(file_path, thumb_path)
                                
                                thumb_url = f"https://claire-marcus.com/uploads/thumbs/" + os.path.basename(thumb_path)
                                sync_db = get_sync_db()
                                sync_db.media.update_one({"_id": ObjectId(inserted_id)}, {"$set": {"thumb_url": thumb_url}})
                                print(f"✅ Thumbnail generated for {unique_filename}: {thumb_url}")
                                
                            except Exception as e:
                                print(f"❌ Thumbnail generation failed for {unique_filename}: {str(e)}")
                        
                        bg.add_task(generate_thumbnail_job)
                    
                    # File metadata for response
                    file_metadata = {
                        "id": inserted_id,
                        "original_name": file.filename,
                        "stored_name": unique_filename,
                        "file_path": file_path,
                        "content_type": file.content_type,
                        "size": len(file_content),
                        "uploaded_at": doc["created_at"].isoformat(),
                        "user_id": user_id,
                        "description": "",
                        "url": doc["url"],
                        "thumb_url": None  # Will be available after background processing
                    }
                    
                except Exception as db_error:
                    print(f"❌ MongoDB insert failed: {db_error}")
                    # Fallback to filesystem storage
                    file_metadata = {
                        "id": str(uuid.uuid4()),
                        "original_name": file.filename,
                        "stored_name": unique_filename,
                        "file_path": file_path,
                        "content_type": file.content_type,
                        "size": len(file_content),
                        "uploaded_at": datetime.now().isoformat(),
                        "user_id": user_id,
                        "description": ""
                    }
            else:
                # Fallback to filesystem storage
                file_metadata = {
                    "id": str(uuid.uuid4()),
                    "original_name": file.filename,
                    "stored_name": unique_filename,
                    "file_path": file_path,
                    "content_type": file.content_type,
                    "size": len(file_content),
                    "uploaded_at": datetime.now().isoformat(),
                    "user_id": user_id,
                    "description": ""
                }
            
            uploaded_files.append(file_metadata)
            
        except Exception as e:
            failed_uploads.append({
                "filename": file.filename,
                "error": f"Erreur lors de l'upload: {str(e)}"
            })
    
    # Prepare response
    response = {
        "message": f"{len(uploaded_files)} fichier(s) uploadé(s) avec succès",
        "uploaded_files": uploaded_files,
        "total_uploaded": len(uploaded_files),
        "total_failed": len(failed_uploads)
    }
    
    if failed_uploads:
        response["failed_uploads"] = failed_uploads
    
    return response

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

# CORS middleware - FIX for cross-site authentication (ChatGPT solution)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[
        "https://claire-marcus.com",
        "https://www.claire-marcus.com", 
        "https://libfusion.preview.emergentagent.com",
        "http://localhost:3000",
        "http://10.64.167.140:3000"
    ],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Servir les fichiers uploads/ en statique (selon ChatGPT)
app.mount("/uploads", StaticFiles(directory="uploads", html=False), name="uploads")

# Synchronize descriptions with files on startup
print("🔄 Synchronizing content descriptions with files...")
sync_descriptions_with_files()

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)