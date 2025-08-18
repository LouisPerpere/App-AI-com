#!/usr/bin/env python3
# Simple migration script using existing database connection
import os, sys, json
from datetime import datetime, timezone
from database import get_database
import mimetypes

def guess_type(path: str) -> str:
    t, _ = mimetypes.guess_type(path)
    return t or "application/octet-stream"

def load_descriptions():
    """Load existing descriptions from JSON file"""
    try:
        if os.path.exists("content_descriptions.json"):
            with open("content_descriptions.json", 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️ Error loading descriptions: {e}")
    return {}

def main():
    # User ID from test data
    user_id = "8aa0e7b1-5279-468b-bbce-028f7a70282d"
    uploads_dir = "uploads"
    public_base = "https://claire-marcus-api.onrender.com/uploads"
    
    print(f"🔄 Starting migration for user: {user_id}")
    
    # Connect to database using existing connection
    db = get_database()
    if not db.is_connected():
        print("❌ Database not connected!")
        sys.exit(1)
        
    print("✅ Database connected")
    
    # Get media collection
    media_collection = db.db.media
    
    # Load existing descriptions
    descriptions = load_descriptions()
    print(f"📝 Loaded {len(descriptions)} descriptions from JSON")
    
    # Check uploads directory
    if not os.path.isdir(uploads_dir):
        print(f"❌ Uploads directory not found: {uploads_dir}")
        sys.exit(1)
    
    # Get all files in uploads directory
    files = [f for f in os.listdir(uploads_dir) 
             if os.path.isfile(os.path.join(uploads_dir, f)) and not f.startswith('.')]
    
    print(f"📂 Found {len(files)} files to migrate")
    
    inserted = 0
    skipped = 0
    
    # Migrate each file
    for filename in files:
        try:
            path = os.path.join(uploads_dir, filename)
            file_type = guess_type(path)
            
            # Skip if not a media file
            if not (file_type.startswith('image/') or file_type.startswith('video/')):
                print(f"⚠️ Skipping non-media file: {filename}")
                skipped += 1
                continue
            
            # Check if already exists
            existing = media_collection.find_one({
                "filename": filename, 
                "owner_id": user_id, 
                "deleted": {"$ne": True}
            })
            
            if existing:
                print(f"⚠️ File already exists: {filename}")
                skipped += 1
                continue
                
            # Get file stats
            stat = os.stat(path)
            created_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
            
            # Get file ID from filename for description lookup
            file_id = os.path.splitext(filename)[0]
            description = descriptions.get(file_id, "")
            
            # Check if thumbnail exists
            from thumbs import build_thumb_path
            thumb_path = build_thumb_path(filename)
            thumb_url = None
            
            if os.path.exists(thumb_path):
                thumb_filename = os.path.basename(thumb_path)
                thumb_url = f"{public_base}/thumbs/{thumb_filename}"
                print(f"✅ Found existing thumbnail for {filename}")
            
            # Create document
            doc = {
                "owner_id": user_id,
                "filename": filename,
                "original_filename": filename,  # Same as filename for migrated files
                "file_type": file_type,
                "url": f"{public_base}/{filename}",
                "thumb_url": thumb_url,
                "description": description,
                "deleted": False,
                "created_at": created_at
            }
            
            # Insert document
            result = media_collection.insert_one(doc)
            print(f"✅ Migrated: {filename} (ID: {result.inserted_id})")
            inserted += 1
            
        except Exception as e:
            print(f"❌ Error migrating {filename}: {e}")
            skipped += 1
    
    print(f"\n🎉 Migration complete!")
    print(f"   Inserted: {inserted} files")
    print(f"   Skipped: {skipped} files")
    print(f"   Total processed: {inserted + skipped}")

if __name__ == "__main__":
    main()