# routes_thumbs.py
import os
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Header
from bson import ObjectId
from datetime import datetime
from thumbs import generate_image_thumb, generate_video_thumb, build_thumb_path
from database import get_database
import asyncio
import pymongo

router = APIRouter()

UPLOADS_DIR = os.environ.get("UPLOADS_DIR", "uploads")
PUBLIC_BASE = os.environ.get("PUBLIC_BASE", "https://claire-marcus.com")  # ex: https://api..../uploads

async def get_media_collection():
    """Get MongoDB media collection"""
    db = get_database()
    return db.db.media

def get_sync_media_collection():
    """Get MongoDB media collection synchronously"""
    db = get_database()
    return db.db.media

def get_current_user_id(authorization: str = Header(None)):
    """Extract user ID from JWT token - compatible with server.py"""
    if not authorization or not authorization.startswith("Bearer "):
        # For demo mode compatibility, return a demo user ID
        print(f"⚠️ No Authorization header found in request, falling back to demo mode")
        return "demo_user_id"
    
    token = authorization.replace("Bearer ", "")
    print(f"🔍 Processing token: {token[:20]}..." if len(token) > 20 else f"🔍 Processing token: {token}")
    
    # Try to get real user from database
    try:
        from database import get_database
        import asyncio
        
        # Get database synchronously for this function
        db_manager = get_database()
        if hasattr(db_manager, 'is_connected') and db_manager.is_connected():
            user_data = db_manager.get_user_by_token(token)
            if user_data:
                print(f"✅ Token validation successful for user: {user_data['email']}")
                return user_data["user_id"]
            else:
                print(f"❌ Token validation failed - invalid or expired token")
        else:
            print(f"❌ Database not connected - falling back to demo mode")
    except Exception as e:
        print(f"❌ Error validating token: {e}")
    
    # Fallback to demo mode for invalid/expired tokens
    print(f"⚠️ Falling back to demo_user_id due to token validation failure")
    return "demo_user_id"

def is_image(ft: str) -> bool:
    return ft and ft.startswith("image/")

def is_video(ft: str) -> bool:
    return ft and ft.startswith("video/")

# Synchronous MongoDB client for background tasks
_sync_client = None
def get_sync_db():
    global _sync_client
    if _sync_client is None:
        import os
        from pymongo import MongoClient
        mongo_url = os.environ.get("MONGO_URL")
        _sync_client = MongoClient(mongo_url)
    return _sync_client.claire_marcus

@router.post("/content/{file_id}/thumbnail")
async def generate_single_thumb(
    file_id: str,
    bg: BackgroundTasks,
    user_id: str = Depends(get_current_user_id),
):
    """Generate thumbnail for a single file"""
    media_collection = get_sync_media_collection()
    
    try:
        doc = media_collection.find_one({"_id": ObjectId(file_id), "owner_id": user_id, "deleted": {"$ne": True}})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid file ID: {str(e)}")
        
    if not doc:
        raise HTTPException(status_code=404, detail="Media not found")
        
    filename = doc["filename"]
    src_path = os.path.join(UPLOADS_DIR, filename)
    if not os.path.isfile(src_path):
        raise HTTPException(status_code=404, detail="File missing on disk")

    thumb_path = build_thumb_path(filename)

    def _job():
        try:
            os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
            if is_image(doc.get("file_type")):
                generate_image_thumb(src_path, thumb_path)
            elif is_video(doc.get("file_type")):
                generate_video_thumb(src_path, thumb_path)
            else:
                return
            # URL publique de la vignette
            thumb_url = f"{PUBLIC_BASE}/uploads/thumbs/" + os.path.basename(thumb_path)
            # Mise à jour Mongo
            sync_db = get_sync_db()
            sync_db.media.update_one({"_id": ObjectId(file_id)}, {"$set": {"thumb_url": thumb_url}})
            print(f"✅ Thumbnail generated for {filename}: {thumb_url}")
        except Exception as e:
            print(f"❌ Thumbnail generation failed for {filename}: {str(e)}")

    bg.add_task(_job)
    return {"ok": True, "scheduled": True, "file_id": file_id}

@router.post("/content/thumbnails/rebuild")
async def rebuild_missing_thumbs(
    limit: int = 500,
    bg: BackgroundTasks = None,
    user_id: str = Depends(get_current_user_id),
):
    """Rebuild missing thumbnails for user (backfill)"""
    media_collection = get_sync_media_collection()
    
    # backfill thumbnails manquantes de l'utilisateur
    q = {"owner_id": user_id, "deleted": {"$ne": True}, "$or": [{"thumb_url": None}, {"thumb_url": ""}]}
    cursor = media_collection.find(q).sort([("created_at", -1)]).limit(limit)
    docs = list(cursor)

    scheduled = 0
    for d in docs:
        filename = d["filename"]
        src_path = os.path.join(UPLOADS_DIR, filename)
        if not os.path.isfile(src_path):
            continue
        thumb_path = build_thumb_path(filename)

        def make_job(doc_id, file_type, src=src_path, dst=thumb_path, fname=filename):
            def _job():
                try:
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    if is_image(file_type):
                        generate_image_thumb(src, dst)
                    elif is_video(file_type):
                        generate_video_thumb(src, dst)
                    else:
                        return
                    thumb_url = f"{PUBLIC_BASE}/uploads/thumbs/" + os.path.basename(dst)
                    sync_db = get_sync_db()
                    sync_db.media.update_one({"_id": ObjectId(doc_id)}, {"$set": {"thumb_url": thumb_url}})
                    print(f"✅ Thumbnail generated for {fname}: {thumb_url}")
                except Exception as e:
                    print(f"❌ Thumbnail generation failed for {fname}: {str(e)}")
            return _job

        if bg is not None:
            bg.add_task(make_job(d["_id"], d.get("file_type")))
            scheduled += 1
        else:
            # fallback synchrone (évite si beaucoup d'items)
            job = make_job(d["_id"], d.get("file_type"))
            job()
            scheduled += 1

    return {"ok": True, "scheduled": scheduled, "files_found": len(docs)}

@router.get("/content/thumbnails/status")
async def get_thumbnail_status(
    user_id: str = Depends(get_current_user_id),
):
    """Get thumbnail generation status for user"""
    media_collection = await get_media_collection()
    
    # Count total files
    total_query = {"owner_id": user_id, "deleted": {"$ne": True}}
    total_files = await media_collection.count_documents(total_query)
    
    # Count files with thumbnails
    with_thumbs_query = {"owner_id": user_id, "deleted": {"$ne": True}, "thumb_url": {"$ne": None, "$ne": ""}}
    with_thumbs = await media_collection.count_documents(with_thumbs_query)
    
    # Count missing thumbnails
    missing_thumbs = total_files - with_thumbs
    
    return {
        "total_files": total_files,
        "with_thumbnails": with_thumbs,
        "missing_thumbnails": missing_thumbs,
        "completion_percentage": round((with_thumbs / total_files * 100) if total_files > 0 else 0, 1)
    }