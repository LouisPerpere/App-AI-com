from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks, Header, Form, Response
from fastapi.responses import StreamingResponse
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from database import get_database
from routes_thumbs import save_db_thumbnail
from thumbs import generate_image_thumb_from_bytes, generate_video_thumb_from_bytes
from server import get_media_collection
import jwt
import uuid
import subprocess
import tempfile
import os

router = APIRouter()

def compress_video_to_720p(input_data: bytes, max_duration_seconds: int = 300) -> bytes:
    """Compress video to max 720p resolution with reasonable quality."""
    try:
        print(f"🎥 Starting video compression...")
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_input:
            temp_input.write(input_data)
            temp_input_path = temp_input.name
        
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_output:
            temp_output_path = temp_output.name
        
        # FFmpeg command for compression to 720p max
        # -vf scale=-2:720 maintains aspect ratio, max height 720p
        # -c:v libx264 for good compression and compatibility
        # -crf 23 for good quality/size balance (18-28 range, lower = better quality)
        # -preset fast for reasonable encoding speed
        # -movflags +faststart for web streaming
        # -t limits duration to prevent huge files
        ffmpeg_cmd = [
            'ffmpeg', '-y',  # -y to overwrite output file
            '-i', temp_input_path,  # Input file
            '-vf', 'scale=-2:min(720\\,ih)',  # Scale to max 720p height, maintain aspect ratio
            '-c:v', 'libx264',  # H.264 codec for compatibility
            '-crf', '23',  # Quality setting (23 is good balance)
            '-preset', 'fast',  # Encoding speed
            '-c:a', 'aac',  # Audio codec
            '-b:a', '128k',  # Audio bitrate
            '-movflags', '+faststart',  # Web streaming optimization
            '-t', str(max_duration_seconds),  # Limit duration to 5 minutes
            temp_output_path
        ]
        
        print(f"🎬 Running FFmpeg: {' '.join(ffmpeg_cmd)}")
        
        # Run FFmpeg
        result = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        if result.returncode != 0:
            print(f"❌ FFmpeg failed: {result.stderr}")
            # Return original data if compression fails
            os.unlink(temp_input_path)
            os.unlink(temp_output_path)
            return input_data
        
        # Read compressed video
        with open(temp_output_path, 'rb') as f:
            compressed_data = f.read()
        
        # Check if compression actually reduced size
        original_size = len(input_data)
        compressed_size = len(compressed_data)
        compression_ratio = compressed_size / original_size
        
        print(f"✅ Video compressed: {original_size/1024/1024:.1f}MB → {compressed_size/1024/1024:.1f}MB ({compression_ratio:.1%})")
        
        # Cleanup
        os.unlink(temp_input_path)
        os.unlink(temp_output_path)
        
        # Use compressed version if it's smaller or similar size
        return compressed_data if compression_ratio < 1.2 else input_data
        
    except Exception as e:
        print(f"❌ Video compression failed: {str(e)}")
        # Cleanup on error
        try:
            os.unlink(temp_input_path)
            os.unlink(temp_output_path)
        except:
            pass
        return input_data

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
    attributed_month: Optional[str] = Form(None),
    upload_type: Optional[str] = Form(None),
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

        # Resize image if it's an image file
        final_data = data
        if file.content_type and file.content_type.startswith('image/'):
            try:
                import tempfile
                import os
                from PIL import Image
                import PIL.ExifTags
                
                # Create temp files
                with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as temp_input:
                    temp_input.write(data)
                    temp_input_path = temp_input.name
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_output:
                    temp_output_path = temp_output.name
                
                # Resize image inline instead of importing
                try:
                    with Image.open(temp_input_path) as im:
                        # Fix EXIF orientation (Pillow 11.x compatible)
                        try:
                            exif = im._getexif()
                            if exif is not None:
                                # Use the orientation value directly (Pillow 11.x compatibility)
                                orientation_key = None
                                for tag, value in PIL.ExifTags.TAGS.items():
                                    if value == 'Orientation':
                                        orientation_key = tag
                                        break
                                
                                if orientation_key and orientation_key in exif:
                                    orientation = exif[orientation_key]
                                    if orientation == 3:
                                        im = im.rotate(180, expand=True)
                                    elif orientation == 6:
                                        im = im.rotate(270, expand=True)
                                    elif orientation == 8:
                                        im = im.rotate(90, expand=True)
                        except (AttributeError, KeyError, TypeError):
                            pass
                        
                        # Convert to RGB
                        im = im.convert("RGB")
                        original_width, original_height = im.size
                        
                        # Calculate new dimensions (1024px on smallest side)
                        min_dimension = 1024
                        
                        if original_width <= original_height:
                            # Width is smaller - resize to 1024 width
                            if original_width > min_dimension:
                                new_width = min_dimension
                                new_height = int((original_height * new_width) / original_width)
                            else:
                                new_width = original_width
                                new_height = original_height
                        else:
                            # Height is smaller - resize to 1024 height
                            if original_height > min_dimension:
                                new_height = min_dimension
                                new_width = int((original_width * new_height) / original_height)
                            else:
                                new_width = original_width
                                new_height = original_height
                        
                        # Resize if needed
                        if new_width != original_width or new_height != original_height:
                            im = im.resize((new_width, new_height), Image.LANCZOS)
                        
                        # Save with optimizations
                        im.save(temp_output_path, format="JPEG", quality=85, optimize=True, progressive=True, dpi=(72, 72))
                        
                        # Read resized data if successful
                        with open(temp_output_path, 'rb') as f:
                            final_data = f.read()
                        
                        print(f"✅ Image resized: {new_width}x{new_height}")
                        
                except Exception as resize_error:
                    print(f"⚠️ Image resize failed: {resize_error}")
                    # Use original data if resize fails
                    final_data = data
                
                # Cleanup temp files
                os.unlink(temp_input_path)
                if os.path.exists(temp_output_path):
                    os.unlink(temp_output_path)
                
            except Exception as e:
                print(f"⚠️ Image resize failed, using original: {e}")
                final_data = data
        
        elif file.content_type and file.content_type.startswith('video/'):
            # Compress video to 720p max
            try:
                print(f"🎥 Processing video file: {file.filename}")
                original_size_mb = len(data) / 1024 / 1024
                print(f"📊 Original video size: {original_size_mb:.1f}MB")
                
                # Only compress if video is large enough to benefit
                if original_size_mb > 5:  # Only compress videos larger than 5MB
                    final_data = compress_video_to_720p(data)
                    compressed_size_mb = len(final_data) / 1024 / 1024
                    print(f"📊 Final video size: {compressed_size_mb:.1f}MB")
                else:
                    print(f"📊 Video too small to compress, keeping original")
                    final_data = data
                    
            except Exception as e:
                print(f"⚠️ Video compression failed, using original: {e}")
                final_data = data
        
        # Store in GridFS
        from gridfs import GridFS
        fs = GridFS(db)
        grid_id = fs.put(final_data, filename=file.filename, content_type=file.content_type, uploadDate=datetime.utcnow())

        # Generate unique ID first for URLs
        doc_id = str(uuid.uuid4())
        
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
            "deleted": False,
            "id": doc_id,
            "url": f"/api/content/{doc_id}/file",
            "thumb_url": f"/api/content/{doc_id}/thumb",
            "attributed_month": attributed_month,
            "upload_type": upload_type,
            "source": "upload"  # Mark as regular upload vs pixabay
        }
        res = db.media.insert_one(media_doc)
        media_id = res.inserted_id

        # Schedule thumbnail generation
        def _thumb_job():
            try:
                if file.content_type and file.content_type.startswith('image/'):
                    thumb_bytes = generate_image_thumb_from_bytes(final_data)  # Use processed data
                    save_db_thumbnail(user_id, doc_id, thumb_bytes)  # Use doc_id instead of media_id
                    print(f"✅ Thumbnail generated for {doc_id}")
                elif file.content_type and file.content_type.startswith('video/'):
                    thumb_bytes = generate_video_thumb_from_bytes(final_data)
                    save_db_thumbnail(user_id, doc_id, thumb_bytes)
                    print(f"✅ Video thumbnail generated for {doc_id}")
            except Exception as e:
                print(f"⚠️ Thumbnail generation error for upload {doc_id}: {e}")
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
    attributed_month: Optional[str] = Form(None),
    upload_type: Optional[str] = Form(None),
    common_title: Optional[str] = Form(None),
    common_context: Optional[str] = Form(None),
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
        
        # Generate a single carousel_id for all files in this batch if it's a carousel upload
        batch_carousel_id = str(uuid.uuid4()) if upload_type == "carousel" and common_title else None
        
        for file in files:
            data = await file.read()
            if not data:
                continue
            
            # Resize image if it's an image file (same logic as single upload)
            final_data = data
            if file.content_type and file.content_type.startswith('image/'):
                try:
                    import tempfile
                    import os
                    from PIL import Image
                    import PIL.ExifTags
                    
                    # Create temp files
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as temp_input:
                        temp_input.write(data)
                        temp_input_path = temp_input.name
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_output:
                        temp_output_path = temp_output.name
                    
                    try:
                        with Image.open(temp_input_path) as im:
                            # Fix EXIF orientation (Pillow 11.x compatible)
                            try:
                                exif = im._getexif()
                                if exif is not None:
                                    # Use the orientation value directly (Pillow 11.x compatibility)
                                    orientation_key = None
                                    for tag, value in PIL.ExifTags.TAGS.items():
                                        if value == 'Orientation':
                                            orientation_key = tag
                                            break
                                    
                                    if orientation_key and orientation_key in exif:
                                        orientation = exif[orientation_key]
                                        if orientation == 3:
                                            im = im.rotate(180, expand=True)
                                        elif orientation == 6:
                                            im = im.rotate(270, expand=True)
                                        elif orientation == 8:
                                            im = im.rotate(90, expand=True)
                            except (AttributeError, KeyError, TypeError):
                                pass
                            
                            # Convert to RGB and resize
                            im = im.convert("RGB")
                            original_width, original_height = im.size
                            
                            # Calculate new dimensions (1024px on smallest side)
                            min_dimension = 1024
                            
                            if original_width <= original_height:
                                if original_width > min_dimension:
                                    new_width = min_dimension
                                    new_height = int((original_height * new_width) / original_width)
                                else:
                                    new_width = original_width
                                    new_height = original_height
                            else:
                                if original_height > min_dimension:
                                    new_height = min_dimension
                                    new_width = int((original_width * new_height) / original_height)
                                else:
                                    new_width = original_width
                                    new_height = original_height
                            
                            # Resize if needed
                            if new_width != original_width or new_height != original_height:
                                im = im.resize((new_width, new_height), Image.LANCZOS)
                            
                            # Save with optimizations
                            im.save(temp_output_path, format="JPEG", quality=85, optimize=True, progressive=True, dpi=(72, 72))
                        
                        # Read resized data if successful
                        with open(temp_output_path, 'rb') as f:
                            final_data = f.read()
                        
                        print(f"✅ Batch image resized: {new_width}x{new_height}")
                        
                    except Exception as resize_error:
                        print(f"⚠️ Batch image resize failed: {resize_error}")
                        # Use original data if resize fails
                        final_data = data
                    
                    # Cleanup temp files
                    os.unlink(temp_input_path)
                    if os.path.exists(temp_output_path):
                        os.unlink(temp_output_path)
                        
                except Exception as e:
                    print(f"⚠️ Image processing error: {e}")
                    final_data = data
                    
            elif file.content_type and file.content_type.startswith('video/'):
                # Compress video to 720p max (batch version)
                try:
                    print(f"🎥 Processing batch video file: {file.filename}")
                    original_size_mb = len(data) / 1024 / 1024
                    print(f"📊 Original video size: {original_size_mb:.1f}MB")
                    
                    # Only compress if video is large enough to benefit
                    if original_size_mb > 5:  # Only compress videos larger than 5MB
                        final_data = compress_video_to_720p(data)
                        compressed_size_mb = len(final_data) / 1024 / 1024
                        print(f"📊 Final video size: {compressed_size_mb:.1f}MB")
                    else:
                        print(f"📊 Video too small to compress, keeping original")
                        final_data = data
                        
                except Exception as e:
                    print(f"⚠️ Video compression failed, using original: {e}")
                    final_data = data
            
            grid_id = fs.put(final_data, filename=file.filename, content_type=file.content_type, uploadDate=datetime.utcnow())
            
            # Generate unique ID first for URLs
            doc_id = str(uuid.uuid4())
            
            # Determine title and context based on upload type
            if upload_type == "carousel" and common_title:
                title = common_title
                context = common_context or f"Image du carrousel '{common_title}'"
            elif common_title:  # Apply common_title for any upload type when provided
                title = common_title
                context = common_context or ""
            else:
                title = file.filename
                context = ""
                
            media_doc = {
                "owner_id": user_id,
                "filename": file.filename,
                "file_type": file.content_type or "application/octet-stream",
                "storage": "gridfs",
                "gridfs_id": grid_id,
                "size": len(data),
                "description": context,
                "created_at": datetime.utcnow(),
                "deleted": False,
                "id": doc_id,
                "url": f"/api/content/{doc_id}/file",
                "thumb_url": f"/api/content/{doc_id}/thumb",
                "attributed_month": attributed_month,
                "upload_type": upload_type,
                "source": "upload",  # Mark as regular upload vs pixabay
                "title": title,  # Add title field
                "context": context,  # Add context field
                "common_title": common_title if upload_type == "carousel" else None,  # For carousel grouping
                "carousel_id": batch_carousel_id  # Group carousel items with same ID
            }
            res = db.media.insert_one(media_doc)
            media_id = res.inserted_id

            def _thumb_job_local(fid=doc_id, bytes_data=final_data, ctype=file.content_type):
                try:
                    if ctype and ctype.startswith('image/'):
                        thumb_bytes = generate_image_thumb_from_bytes(bytes_data)
                        save_db_thumbnail(user_id, fid, thumb_bytes)
                        print(f"✅ Local thumbnail generated for {fid}")
                    elif ctype and ctype.startswith('video/'):
                        thumb_bytes = generate_video_thumb_from_bytes(bytes_data)
                        save_db_thumbnail(user_id, fid, thumb_bytes)
                        print(f"✅ Local video thumbnail generated for {fid}")
                except Exception as e:
                    print(f"⚠️ Thumbnail generation error for upload {fid}: {e}")

            if bg is not None:
                bg.add_task(_thumb_job_local)
            else:
                _thumb_job_local()

            created.append({
                "id": doc_id,  # Use UUID for consistency with content/pending
                "filename": file.filename,
                "file_type": file.content_type,
                "size": len(final_data),  # Use final_data length
                "thumb_url": f"/api/content/{doc_id}/thumb"
            })

        return {"ok": True, "created": created, "count": len(created)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Batch upload failed: {str(e)}")


@router.get("/content/{file_id}/file")
async def get_original_file(file_id: str, token: Optional[str] = None, authorization: Optional[str] = Header(None), range: Optional[str] = Header(None)):
    """Stream original file from GridFS with auth and Range support for videos."""
    print(f"🔍 GET /content/{file_id}/file - token: {token is not None}, auth: {authorization is not None}, range: {range}")
    
    # Allow auth via Authorization header or ?token=
    user_id = None
    if token:
        user_id = _decode_user_from_token(token)
        print(f"🔑 Token decoded to user_id: {user_id}")
    elif authorization and authorization.startswith("Bearer "):
        user_id = _decode_user_from_token(authorization[7:])
        print(f"🔑 Bearer decoded to user_id: {user_id}")
    
    if not user_id:
        print("❌ No valid authentication found")
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        dbm = get_database()
        db = dbm.db
        from gridfs import GridFS
        fs = GridFS(db)

        # Find media using the proper collection and field
        media_collection = get_media_collection()
        media = media_collection.find_one({"id": file_id, "owner_id": user_id, "deleted": {"$ne": True}})
        if not media:
            raise HTTPException(404, "Media not found")
        if media.get("storage") != "gridfs" or not media.get("gridfs_id"):
            raise HTTPException(404, "Original not stored in GridFS")

        gid = media.get("gridfs_id")
        if isinstance(gid, str):
            gid = ObjectId(gid)
        f = fs.get(gid)
        content_type = f.content_type or media.get("file_type") or "application/octet-stream"
        
        # Read all file data into memory for range support
        file_data = f.read()
        file_size = len(file_data)
        
        # Handle Range requests for video streaming
        if range and content_type.startswith('video/'):
            try:
                ranges = range.replace('bytes=', '').split('-')
                start = int(ranges[0]) if ranges[0] else 0
                end = int(ranges[1]) if ranges[1] else file_size - 1
                
                if start >= file_size or end >= file_size:
                    raise HTTPException(416, "Range not satisfiable")
                
                chunk_data = file_data[start:end+1]
                content_length = len(chunk_data)
                
                from fastapi import Response
                headers = {
                    'Content-Range': f'bytes {start}-{end}/{file_size}',
                    'Accept-Ranges': 'bytes',
                    'Content-Length': str(content_length),
                    'Content-Type': content_type
                }
                
                return Response(
                    content=chunk_data,
                    status_code=206,  # Partial Content
                    headers=headers
                )
            except (ValueError, IndexError):
                # Invalid range, fall back to full file
                pass
        
        # Return full file with proper headers for video
        headers = {}
        if content_type.startswith('video/'):
            headers['Accept-Ranges'] = 'bytes'
            headers['Content-Length'] = str(file_size)
        
        from io import BytesIO
        return StreamingResponse(BytesIO(file_data), media_type=content_type, headers=headers)
        
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

        # Find media using the proper collection and field
        media_collection = get_media_collection()
        media = media_collection.find_one({"id": file_id, "owner_id": user_id, "deleted": {"$ne": True}})
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