# routes_thumbs.py
import os
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Header
from bson import ObjectId
from datetime import datetime
from thumbs import (
    generate_image_thumb, generate_video_thumb, build_thumb_path,
    generate_image_thumb_bytes, generate_video_thumb_bytes
)
from database import get_database
import asyncio
import pymongo
import jwt
from typing import Optional
from fastapi.responses import StreamingResponse, JSONResponse
from io import BytesIO

router = APIRouter()

UPLOADS_DIR = os.environ.get("UPLOADS_DIR", "uploads")
# We will no longer build absolute public base URLs; API will return relative /api paths
RELATIVE_THUMB_ENDPOINT = "/api/content/{file_id}/thumb"

# JWT Configuration (same as server.py)
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-this-in-production')
JWT_ALG = os.environ.get("JWT_ALG", "HS256")
JWT_TTL = int(os.environ.get("JWT_TTL_SECONDS", "604800"))  # 7 jours
JWT_ISS = os.environ.get("JWT_ISS", "claire-marcus-api")

async def get_media_collection():
    db = get_database()
    return db.db.media

def get_sync_media_collection():
    db = get_database()
    return db.db.media

# Thumbnails collection (binary storage)
_sync_client = None

def get_sync_db():
    global _sync_client
    if _sync_client is None:
        from pymongo import MongoClient
        mongo_url = os.environ.get("MONGO_URL")
        _sync_client = MongoClient(mongo_url)
    return _sync_client.claire_marcus

THUMBS_COLLECTION = "thumbnails"

def save_db_thumbnail(owner_id: str, media_obj_id: ObjectId, content: bytes, content_type: str = "image/webp"):
    """Upsert thumbnail binary into MongoDB thumbnails collection and update media.thumb_url to relative API path"""
    dbp = get_sync_db()
    thumbs_col = dbp[THUMBS_COLLECTION]
    now = datetime.utcnow()
    thumbs_col.update_one(
        {"media_id": media_obj_id},
        {"$set": {
            "media_id": media_obj_id,
            "owner_id": owner_id,
            "content_type": content_type,
            "size": len(content),
            "data": content,
            "updated_at": now
        }, "$setOnInsert": {"created_at": now}},
        upsert=True
    )
    # update media doc to point to API relative endpoint
    dbp.media.update_one({"_id": media_obj_id}, {"$set": {"thumb_url": RELATIVE_THUMB_ENDPOINT.format(file_id=str(media_obj_id))}})

def get_db_thumbnail(media_obj_id: ObjectId):
    dbp = get_sync_db()
    thumbs_col = dbp[THUMBS_COLLECTION]
    return thumbs_col.find_one({"media_id": media_obj_id})

# Robust auth (duplicated to avoid import cycles)
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
        return sub
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(401, f"Invalid token: {e}")

def is_image(ft: str) -> bool:
    return ft and ft.startswith("image/")

def is_video(ft: str) -> bool:
    return ft and ft.startswith("video/")

@router.get("/content/{file_id}/thumb")
async def stream_thumbnail(file_id: str, user_id: str = Depends(get_current_user_id_robust)):
    """Stream thumbnail from MongoDB; if missing, attempt on-demand generation from source and save to DB."""
    media_collection = get_sync_media_collection()
    try:
        id_filter = {"_id": ObjectId(file_id)}
    except Exception:
        # fallback UUID filter
        id_filter = {"external_id": file_id}
    media_doc = media_collection.find_one({**id_filter, "owner_id": user_id, "deleted": {"$ne": True}})
    if not media_doc:
        raise HTTPException(status_code=404, detail="Media not found")

    media_obj_id = media_doc.get("_id")
    thumb_doc = get_db_thumbnail(media_obj_id)

    if not thumb_doc:
        # try to generate from source
        filename = media_doc.get("filename")
        src_path = os.path.join(UPLOADS_DIR, filename)
        if not os.path.isfile(src_path):
            raise HTTPException(status_code=404, detail="Source file missing on disk")
        try:
            if is_image(media_doc.get("file_type")):
                content = generate_image_thumb_bytes(src_path)
            elif is_video(media_doc.get("file_type")):
                content = generate_video_thumb_bytes(src_path)
            else:
                raise HTTPException(status_code=415, detail="Unsupported media type for thumbnail")
            save_db_thumbnail(media_doc.get("owner_id"), media_obj_id, content)
            thumb_doc = get_db_thumbnail(media_obj_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Thumbnail generation failed: {str(e)}")

    content_type = thumb_doc.get("content_type", "image/webp")
    data = thumb_doc.get("data")
    if data is None:
        raise HTTPException(status_code=500, detail="Thumbnail data not found")

    return StreamingResponse(BytesIO(data), media_type=content_type)

@router.post("/content/{file_id}/thumbnail")
async def generate_single_thumb(
    file_id: str,
    bg: BackgroundTasks,
    user_id: str = Depends(get_current_user_id_robust),
):
    """Generate and store thumbnail in DB for a single file; update media.thumb_url to relative API path."""
    media_collection = get_sync_media_collection()
    try:
        id_filter = {"_id": ObjectId(file_id)}
    except Exception:
        id_filter = {"external_id": file_id}
    doc = media_collection.find_one({**id_filter, "owner_id": user_id, "deleted": {"$ne": True}})
    if not doc:
        raise HTTPException(status_code=404, detail="Media not found")

    filename = doc["filename"]
    src_path = os.path.join(UPLOADS_DIR, filename)
    if not os.path.isfile(src_path):
        raise HTTPException(status_code=404, detail="File missing on disk")

    def _job():
        try:
            if is_image(doc.get("file_type")):
                content = generate_image_thumb_bytes(src_path)
            elif is_video(doc.get("file_type")):
                content = generate_video_thumb_bytes(src_path)
            else:
                return
            save_db_thumbnail(doc.get("owner_id"), doc["_id"], content)
            print(f"✅ DB thumbnail saved for {filename}")
        except Exception as e:
            print(f"❌ Thumbnail generation failed for {filename}: {str(e)}")

    bg.add_task(_job)
    return {"ok": True, "scheduled": True, "file_id": str(doc["_id"])}

@router.post("/content/thumbnails/rebuild")
async def rebuild_missing_thumbs(
    limit: int = 500,
    bg: BackgroundTasks = None,
    user_id: str = Depends(get_current_user_id_robust),
):
    """Rebuild missing DB thumbnails for user (backfill)"""
    media_collection = get_sync_media_collection()
    # find media missing thumb doc
    q = {"owner_id": user_id, "deleted": {"$ne": True}}
    cursor = media_collection.find(q).sort([("created_at", -1)]).limit(limit)
    docs = list(cursor)

    scheduled = 0
    for d in docs:
        media_obj_id = d.get("_id")
        # check if thumbnail exists in DB
        if get_db_thumbnail(media_obj_id):
            # also ensure media.thumb_url points to relative API endpoint
            media_collection.update_one({"_id": media_obj_id}, {"$set": {"thumb_url": RELATIVE_THUMB_ENDPOINT.format(file_id=str(media_obj_id))}})
            continue

        filename = d.get("filename")
        src_path = os.path.join(UPLOADS_DIR, filename)
        if not os.path.isfile(src_path):
            continue

        def make_job(doc_id, file_type, owner_id, src=src_path, fname=filename):
            def _job():
                try:
                    if is_image(file_type):
                        content = generate_image_thumb_bytes(src)
                    elif is_video(file_type):
                        content = generate_video_thumb_bytes(src)
                    else:
                        return
                    save_db_thumbnail(owner_id, doc_id, content)
                    print(f"✅ DB thumbnail backfilled for {fname}")
                except Exception as e:
                    print(f"❌ Thumbnail generation failed for {fname}: {str(e)}")
            return _job

        if bg is not None:
            bg.add_task(make_job(media_obj_id, d.get("file_type"), d.get("owner_id")))
            scheduled += 1
        else:
            job = make_job(media_obj_id, d.get("file_type"), d.get("owner_id"))
            job()
            scheduled += 1

    return {"ok": True, "scheduled": scheduled, "files_found": len(docs)}

@router.get("/content/thumbnails/status")
async def get_thumbnail_status(
    user_id: str = Depends(get_current_user_id_robust),
):
    """Get thumbnail generation status for user (DB-based)"""
    media_collection = get_sync_media_collection()
    dbp = get_sync_db()
    thumbs_col = dbp[THUMBS_COLLECTION]

    total_query = {"owner_id": user_id, "deleted": {"$ne": True}}
    total_files = media_collection.count_documents(total_query)

    with_thumbs = thumbs_col.count_documents({"owner_id": user_id})

    missing_thumbs = max(total_files - with_thumbs, 0)

    return {
        "total_files": total_files,
        "with_thumbnails": with_thumbs,
        "missing_thumbnails": missing_thumbs,
        "completion_percentage": round((with_thumbs / total_files * 100) if total_files > 0 else 0, 1)
    }

@router.post("/content/thumbnails/normalize")
async def normalize_thumb_urls(
    user_id: str = Depends(get_current_user_id_robust),
):
    """Normalize all media.thumb_url to relative API endpoint for this user"""
    media_collection = get_sync_media_collection()
    q = {"owner_id": user_id, "$or": [{"deleted": {"$ne": True}}, {"deleted": {"$exists": False}}]}
    cursor = media_collection.find(q, {"_id": 1})
    updated = 0
    for d in cursor:
        media_collection.update_one({"_id": d["_id"]}, {"$set": {"thumb_url": RELATIVE_THUMB_ENDPOINT.format(file_id=str(d["_id"]))}})
        updated += 1
    return {"ok": True, "updated": updated}

@router.get("/content/thumbnails/orphans")
async def list_orphan_media(
    limit: int = 50,
    user_id: str = Depends(get_current_user_id_robust),
):
    """List media records where source file is missing on disk"""
    media_collection = get_sync_media_collection()
    q = {"owner_id": user_id, "$or": [{"deleted": {"$ne": True}}, {"deleted": {"$exists": False}}]}
    cursor = media_collection.find(q).limit(max(1, int(limit)))
    orphans = []
    for d in cursor:
        filename = d.get("filename")
        src_path = os.path.join(UPLOADS_DIR, filename) if filename else None
        if not filename or not os.path.isfile(src_path):
            orphans.append({
                "id": str(d.get("_id")),
                "filename": filename,
                "file_type": d.get("file_type"),
                "reason": "missing_on_disk" if filename else "no_filename"
            })
    return {"orphans": orphans, "count": len(orphans)}