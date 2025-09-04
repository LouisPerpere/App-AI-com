# routes_thumbs.py
import os
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Header
from bson import ObjectId
from datetime import datetime
from thumbs import (
    generate_image_thumb, generate_video_thumb, build_thumb_path,
    generate_image_thumb_bytes, generate_video_thumb_bytes,
    generate_image_thumb_from_bytes, generate_video_thumb_from_bytes
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
RELATIVE_THUMB_ENDPOINT = "/api/content/{file_id}/thumb"

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-this-in-production')
JWT_ALG = os.environ.get("JWT_ALG", "HS256")
JWT_TTL = int(os.environ.get("JWT_TTL_SECONDS", "604800"))
JWT_ISS = os.environ.get("JWT_ISS", "claire-marcus-api")

# Sync DB client for GridFS access
_sync_client = None

def get_sync_db():
    global _sync_client
    if _sync_client is None:
        from pymongo import MongoClient
        mongo_url = os.environ.get("MONGO_URL")
        _sync_client = MongoClient(mongo_url)
    return _sync_client[os.environ.get("DB_NAME", "claire_marcus")]

async def get_media_collection():
    db = get_database()
    return db.db.media

def get_sync_media_collection():
    db = get_database()
    return db.db.media

THUMBS_COLLECTION = "thumbnails"

def save_db_thumbnail(owner_id: str, media_obj_id: ObjectId, content: bytes, content_type: str = "image/webp"):
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

# Helpers to fetch original media bytes (GridFS or disk)

def _fetch_original_bytes(media_doc) -> Optional[bytes]:
    storage = media_doc.get("storage")
    filename = media_doc.get("filename")
    if storage == "gridfs":
        try:
            from gridfs import GridFS
            dbp = get_sync_db()
            fs = GridFS(dbp)
            grid_id = media_doc.get("gridfs_id")
            if not grid_id:
                return None
            if isinstance(grid_id, str):
                try:
                    gid = ObjectId(grid_id)
                except Exception:
                    gid = None
            else:
                gid = grid_id
            if gid is None:
                return None
            f = fs.get(gid)
            return f.read()
        except Exception:
            return None
    # Fallback to disk if present
    if filename:
        src_path = os.path.join(UPLOADS_DIR, filename)
        if os.path.isfile(src_path):
            try:
                with open(src_path, 'rb') as fh:
                    return fh.read()
            except Exception:
                return None
    return None

def _decode_user_from_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG], options={"require": ["sub", "exp"]}, issuer=JWT_ISS)
        return payload.get("sub")
    except Exception:
        return None

@router.get("/content/{file_id}/thumb")
async def stream_thumbnail(file_id: str, token: Optional[str] = None, authorization: Optional[str] = Header(None)):
    # Allow auth via Authorization header or ?token=
    user_id = None
    if token:
        user_id = _decode_user_from_token(token)
    if not user_id and authorization and authorization.lower().startswith("bearer "):
        user_id = _decode_user_from_token(authorization.split(" ", 1)[1])
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    """Stream thumbnail from MongoDB; if missing, attempt generation from original (GridFS or disk) and save to DB."""
    media_collection = get_sync_media_collection()
    try:
        id_filter = {"_id": ObjectId(file_id)}
    except Exception:
        id_filter = {"external_id": file_id}
    media_doc = media_collection.find_one({**id_filter, "owner_id": user_id, "deleted": {"$ne": True}})
    if not media_doc:
        raise HTTPException(status_code=404, detail="Media not found")

    media_obj_id = media_doc.get("_id")
    thumb_doc = get_db_thumbnail(media_obj_id)

    if not thumb_doc:
        # try to generate from original
        file_type = media_doc.get("file_type")
        original_bytes = _fetch_original_bytes(media_doc)
        if not original_bytes:
            raise HTTPException(status_code=404, detail="Original media missing")
        try:
            if is_image(file_type):
                content = generate_image_thumb_from_bytes(original_bytes)
            elif is_video(file_type):
                content = generate_video_thumb_from_bytes(original_bytes)
            else:
                raise HTTPException(status_code=415, detail="Unsupported media type for thumbnail")
            save_db_thumbnail(media_doc.get("owner_id"), media_obj_id, content)
            thumb_doc = get_db_thumbnail(media_obj_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Thumbnail generation failed: {str(e)}")

    content_type = thumb_doc.get("content_type", "image/webp")
    data = thumb_doc.get("data")
    if data is None:
        raise HTTPException(status_code=500, detail="Thumbnail data not found")

    # Add cache headers for better performance
    headers = {
        "Cache-Control": "public, max-age=86400",  # Cache for 24 hours
        "ETag": f'"{file_id}-thumb"',
        "Vary": "Authorization"
    }
    return StreamingResponse(BytesIO(data), media_type=content_type, headers=headers)

@router.post("/content/{file_id}/thumbnail")
async def generate_single_thumb(
    file_id: str,
    bg: BackgroundTasks,
    user_id: str = Depends(get_current_user_id_robust),
):
    """Generate and store thumbnail in DB for a single file; source may be GridFS or disk."""
    media_collection = get_sync_media_collection()
    try:
        id_filter = {"_id": ObjectId(file_id)}
    except Exception:
        id_filter = {"external_id": file_id}
    doc = media_collection.find_one({**id_filter, "owner_id": user_id, "deleted": {"$ne": True}})
    if not doc:
        raise HTTPException(status_code=404, detail="Media not found")

    def _job():
        try:
            file_type = doc.get("file_type")
            original_bytes = _fetch_original_bytes(doc)
            if not original_bytes:
                print(f"❌ Original missing for media {doc.get('_id')}")
                return
            if is_image(file_type):
                content = generate_image_thumb_from_bytes(original_bytes)
            elif is_video(file_type):
                content = generate_video_thumb_from_bytes(original_bytes)
            else:
                return
            save_db_thumbnail(doc.get("owner_id"), doc["_id"], content)
            print(f"✅ DB thumbnail saved for {doc.get('filename')}")
        except Exception as e:
            print(f"❌ Thumbnail generation failed for {doc.get('filename')}: {str(e)}")

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
    q = {"owner_id": user_id, "deleted": {"$ne": True}}
    cursor = media_collection.find(q).sort([("created_at", -1)]).limit(limit)
    docs = list(cursor)

    scheduled = 0
    for d in docs:
        media_obj_id = d.get("_id")
        if get_db_thumbnail(media_obj_id):
            media_collection.update_one({"_id": media_obj_id}, {"$set": {"thumb_url": RELATIVE_THUMB_ENDPOINT.format(file_id=str(media_obj_id))}})
            continue

        def make_job(doc):
            def _job():
                try:
                    original_bytes = _fetch_original_bytes(doc)
                    if not original_bytes:
                        return
                    if is_image(doc.get("file_type")):
                        content = generate_image_thumb_from_bytes(original_bytes)
                    elif is_video(doc.get("file_type")):
                        content = generate_video_thumb_from_bytes(original_bytes)
                    else:
                        return
                    save_db_thumbnail(doc.get("owner_id"), doc["_id"], content)
                    print(f"✅ DB thumbnail backfilled for {doc.get('filename')}")
                except Exception as e:
                    print(f"❌ Thumbnail generation failed for {doc.get('filename')}: {str(e)}")
            return _job

        if bg is not None:
            bg.add_task(make_job(d))
            scheduled += 1
        else:
            job = make_job(d)
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
    """List media records where source file is missing on disk and not present in GridFS"""
    media_collection = get_sync_media_collection()
    from gridfs import GridFS
    dbp = get_sync_db()
    fs = GridFS(dbp)

    q = {"owner_id": user_id, "$or": [{"deleted": {"$ne": True}}, {"deleted": {"$exists": False}}]}
    cursor = media_collection.find(q).limit(max(1, int(limit)))
    orphans = []
    for d in cursor:
        storage = d.get("storage")
        filename = d.get("filename")
        is_missing = False
        if storage == "gridfs":
            gid = d.get("gridfs_id")
            try:
                gid = ObjectId(gid) if isinstance(gid, str) else gid
                file_exists = gid is not None and fs.exists(gid)
                is_missing = not file_exists
            except Exception:
                is_missing = True
        else:
            src_path = os.path.join(UPLOADS_DIR, filename) if filename else None
            is_missing = (not filename) or (not os.path.isfile(src_path))
        if is_missing:
            orphans.append({
                "id": str(d.get("_id")),
                "filename": filename,
                "file_type": d.get("file_type"),
                "storage": storage or "disk",
                "reason": "missing_in_gridfs" if storage == "gridfs" else ("no_filename" if not filename else "missing_on_disk")
            })
    return {"orphans": orphans, "count": len(orphans)}