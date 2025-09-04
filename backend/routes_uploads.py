from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks, Header
from fastapi.responses import StreamingResponse
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from database import get_database
from routes_thumbs import save_db_thumbnail
from thumbs import generate_image_thumb_from_bytes, generate_video_thumb_from_bytes
from server import get_media_collection
import jwt

router = APIRouter()

# JWT / Auth configuration (align with server.py)
import os
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-this-in-production')
JWT_ALG = os.environ.get("JWT_ALG", "HS256")
JWT_ISS = os.environ.get("JWT_ISS", "claire-marcus-api")


def get_current_user_id_robust(authorization: Optional[str] = Header(None)) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
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

def _decode_user_from_token(token: str) -> Optional[str]:
    """Decode user ID from JWT token - same as in routes_thumbs.py"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG], options={"require": ["sub", "exp"]}, issuer=JWT_ISS)
        return payload.get("sub")
    except Exception:
        return None


@router.post("/content/upload")
async def upload_content(
    file: UploadFile = File(...),
    bg: BackgroundTasks = None,
    user_id: str = Depends(get_current_user_id_robust)
):
    """Upload a single file to GridFS and create media record; schedule thumbnail generation."""
    try:
        dbm = get_database()
        db = dbm.db

        # Read file bytes
        data = await file.read()
        size = len(data)
        if size == 0:
            raise HTTPException(400, "Empty file")

        # Store in GridFS
        from gridfs import GridFS
        fs = GridFS(db)
        grid_id = fs.put(data, filename=file.filename, content_type=file.content_type, uploadDate=datetime.utcnow())

        # Create media document
        media_doc = {
            "owner_id": user_id,
            "filename": file.filename,
            "file_type": file.content_type or "application/octet-stream",
            "storage": "gridfs",
            "gridfs_id": grid_id,
            "size": size,
            "description": "",
            "created_at": datetime.utcnow(),
            "deleted": False
        }
        res = db.media.insert_one(media_doc)
        media_id = res.inserted_id

        # Schedule thumbnail generation
        def _thumb_job():
            try:
                if file.content_type and file.content_type.startswith('image/'):
                    thumb_bytes = generate_image_thumb_from_bytes(data)
                    save_db_thumbnail(user_id, media_id, thumb_bytes)
                elif file.content_type and file.content_type.startswith('video/'):
                    thumb_bytes = generate_video_thumb_from_bytes(data)
                    save_db_thumbnail(user_id, media_id, thumb_bytes)
            except Exception as e:
                print(f"⚠️ Thumbnail generation error for upload {media_id}: {e}")
        if bg is not None:
            bg.add_task(_thumb_job)
        else:
            _thumb_job()

        return {
            "ok": True,
            "id": str(media_id),
            "filename": file.filename,
            "file_type": file.content_type,
            "size": size,
            "thumb_url": f"/api/content/{media_id}/thumb"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Upload failed: {str(e)}")


@router.post("/content/batch-upload")
async def upload_content_batch(
    files: List[UploadFile] = File(...),
    bg: BackgroundTasks = None,
    user_id: str = Depends(get_current_user_id_robust)
):
    """Batch upload multiple files to GridFS, return created items."""
    try:
        dbm = get_database()
        db = dbm.db
        from gridfs import GridFS
        fs = GridFS(db)

        created = []
        for file in files:
            data = await file.read()
            if not data:
                continue
            grid_id = fs.put(data, filename=file.filename, content_type=file.content_type, uploadDate=datetime.utcnow())
            media_doc = {
                "owner_id": user_id,
                "filename": file.filename,
                "file_type": file.content_type or "application/octet-stream",
                "storage": "gridfs",
                "gridfs_id": grid_id,
                "size": len(data),
                "description": "",
                "created_at": datetime.utcnow(),
                "deleted": False
            }
            res = db.media.insert_one(media_doc)
            media_id = res.inserted_id

            def _thumb_job_local(fid=media_id, bytes_data=data, ctype=file.content_type):
                try:
                    if ctype and ctype.startswith('image/'):
                        thumb_bytes = generate_image_thumb_from_bytes(bytes_data)
                        save_db_thumbnail(user_id, fid, thumb_bytes)
                    elif ctype and ctype.startswith('video/'):
                        thumb_bytes = generate_video_thumb_from_bytes(bytes_data)
                        save_db_thumbnail(user_id, fid, thumb_bytes)
                except Exception as e:
                    print(f"⚠️ Thumbnail generation error for upload {fid}: {e}")

            if bg is not None:
                bg.add_task(_thumb_job_local)
            else:
                _thumb_job_local()

            created.append({
                "id": str(media_id),
                "filename": file.filename,
                "file_type": file.content_type,
                "size": len(data),
                "thumb_url": f"/api/content/{media_id}/thumb"
            })

        return {"ok": True, "created": created, "count": len(created)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Batch upload failed: {str(e)}")


@router.get("/content/{file_id}/file")
async def get_original_file(file_id: str, token: Optional[str] = None, authorization: Optional[str] = Header(None)):
    """Stream original file from GridFS with auth."""
    # Allow auth via Authorization header or ?token=
    user_id = None
    if token:
        user_id = _decode_user_from_token(token)
    elif authorization and authorization.startswith("Bearer "):
        user_id = _decode_user_from_token(authorization[7:])
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        dbm = get_database()
        db = dbm.db
        from gridfs import GridFS
        fs = GridFS(db)

        # Find media
        try:
            filter_id = {"_id": ObjectId(file_id)}
        except Exception:
            filter_id = {"external_id": file_id}
        media = db.media.find_one({**filter_id, "owner_id": user_id, "deleted": {"$ne": True}})
        if not media:
            raise HTTPException(404, "Media not found")
        if media.get("storage") != "gridfs" or not media.get("gridfs_id"):
            raise HTTPException(404, "Original not stored in GridFS")

        gid = media.get("gridfs_id")
        if isinstance(gid, str):
            gid = ObjectId(gid)
        f = fs.get(gid)
        content_type = f.content_type or media.get("file_type") or "application/octet-stream"
        return StreamingResponse(f, media_type=content_type)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to stream file: {str(e)}")


@router.delete("/content/{file_id}")
async def delete_content(file_id: str, user_id: str = Depends(get_current_user_id_robust)):
    """Delete media: thumbnail doc, GridFS original, and media document."""
    try:
        dbm = get_database()
        db = dbm.db
        from gridfs import GridFS
        fs = GridFS(db)

        # Find media
        try:
            filter_id = {"_id": ObjectId(file_id)}
        except Exception:
            filter_id = {"external_id": file_id}
        media = db.media.find_one({**filter_id, "owner_id": user_id, "deleted": {"$ne": True}})
        if not media:
            raise HTTPException(404, "Media not found")

        # Delete thumbnail document (if present)
        db.thumbnails.delete_one({"media_id": media.get("_id")})

        # Delete original in GridFS
        if media.get("storage") == "gridfs" and media.get("gridfs_id"):
            gid = media.get("gridfs_id")
            if isinstance(gid, str):
                try:
                    gid = ObjectId(gid)
                except Exception:
                    gid = None
            if gid is not None:
                try:
                    fs.delete(gid)
                except Exception as e:
                    print(f"⚠️ Failed to delete GridFS file: {e}")

        # Delete media document
        db.media.delete_one({"_id": media.get("_id")})

        return {"ok": True, "deleted": 1}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to delete media: {str(e)}")