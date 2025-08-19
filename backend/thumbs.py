# thumbs.py
import io, os, subprocess, tempfile
from PIL import Image

THUMB_DIR = os.environ.get("THUMB_DIR", "uploads/thumbs")
THUMB_SIZE = int(os.environ.get("THUMB_SIZE", "320"))  # 320x320
THUMB_FORMAT = os.environ.get("THUMB_FORMAT", "WEBP")  # WEBP|JPEG|PNG
QUALITY = int(os.environ.get("THUMB_QUALITY", "85"))

os.makedirs(THUMB_DIR, exist_ok=True)

def _square_crop(im: Image.Image) -> Image.Image:
    """Crop image to square format (center crop)"""
    w, h = im.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    return im.crop((left, top, left + side, top + side))

def generate_image_thumb(src_path: str, thumb_path: str) -> None:
    """Generate thumbnail from image file (filesystem output)"""
    with Image.open(src_path) as im:
        im = im.convert("RGB")
        im = _square_crop(im)
        im.thumbnail((THUMB_SIZE, THUMB_SIZE), Image.LANCZOS)
        ext = THUMB_FORMAT.lower()
        if ext == "webp":
            im.save(thumb_path, format="WEBP", quality=QUALITY, method=6)
        elif ext == "jpeg" or ext == "jpg":
            im.save(thumb_path, format="JPEG", quality=QUALITY, optimize=True, progressive=True)
        else:
            im.save(thumb_path, format="PNG", optimize=True)

def generate_image_thumb_bytes(src_path: str) -> bytes:
    """Generate thumbnail from image file and return bytes (for DB storage)"""
    with Image.open(src_path) as im:
        im = im.convert("RGB")
        im = _square_crop(im)
        im.thumbnail((THUMB_SIZE, THUMB_SIZE), Image.LANCZOS)
        buf = io.BytesIO()
        ext = THUMB_FORMAT.lower()
        if ext == "webp":
            im.save(buf, format="WEBP", quality=QUALITY, method=6)
            content_type = "image/webp"
        elif ext in ("jpeg", "jpg"):
            im.save(buf, format="JPEG", quality=QUALITY, optimize=True, progressive=True)
            content_type = "image/jpeg"
        else:
            im.save(buf, format="PNG", optimize=True)
            content_type = "image/png"
        return buf.getvalue()

def generate_video_thumb(src_path: str, thumb_path: str, time_pos="00:00:01") -> None:
    """Generate thumbnail from video file using ffmpeg (filesystem output)"""
    # 1) extraire une frame
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        jpg_frame = tmp.name
    try:
        # -ss avant -i est plus rapide ; -y overwrite
        cmd = ["ffmpeg", "-ss", time_pos, "-i", src_path, "-frames:v", "1", "-q:v", "2", "-y", jpg_frame]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # 2) transformer la frame en vignette carrée
        generate_image_thumb(jpg_frame, thumb_path)
    finally:
        try:
            os.remove(jpg_frame)
        except FileNotFoundError:
            pass

def generate_video_thumb_bytes(src_path: str, time_pos="00:00:01") -> bytes:
    """Generate thumbnail from video file and return bytes (for DB storage)"""
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        jpg_frame = tmp.name
    try:
        cmd = ["ffmpeg", "-ss", time_pos, "-i", src_path, "-frames:v", "1", "-q:v", "2", "-y", jpg_frame]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Convert the extracted frame to final format
        return generate_image_thumb_bytes(jpg_frame)
    finally:
        try:
            os.remove(jpg_frame)
        except FileNotFoundError:
            pass

def build_thumb_path(filename: str) -> str:
    """Build thumbnail path from original filename (legacy filesystem path)"""
    base, _ = os.path.splitext(filename)
    ext = THUMB_FORMAT.lower()
    return os.path.join(THUMB_DIR, f"{base}.{ext}")