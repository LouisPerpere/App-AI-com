# routes_uploads.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks, Header
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional
from datetime import datetime
from bson import ObjectId
from database import get_database
from routes_thumbs import get_current_user_id_robust, save_db_thumbnail
from thumbs import generate_image_thumb_from_bytes, generate_video_thumb_from_bytes
from io import BytesIO

router = APIRouter()

# Upload multiple files to GridFS (batch) to stay compatible with existing frontend
from typing import List
from fastapi import File as FastFile

# Upload a single file to GridFS and create media record
@router.post("/content/upload")
# Batch upload to GridFS: accepts multiple files under field name 'files'
@router.post("/content/batch-upload")
async def upload_content_batch(
    files: list[UploadFile] = FastFile(...),
    bg: BackgroundTasks = None,
    user_id: str = Depends(get_current_user_id_robust)
):
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

async def upload_content(
    file: UploadFile = File(...),
    bg: BackgroundTasks = None,
    user_id: str = Depends(get_current_user_id_robust)
):
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

# Stream original file from GridFS
@router.get("/content/{file_id}/file")
async def get_original_file(file_id: str, user_id: str = Depends(get_current_user_id_robust)):
    try:
        dbm = get_database()
        db = dbm.db
        from gridfs import GridFS
        fs = GridFS(db)

        media = db.media.find_one({"_id": ObjectId(file_id), "owner_id": user_id, "deleted": {"$ne": True}})
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