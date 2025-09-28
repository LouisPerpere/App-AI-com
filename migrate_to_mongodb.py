#!/usr/bin/env python3
"""
Migrate filesystem data to MongoDB with proper thumb_url values
This addresses the French review request by ensuring MongoDB has the correct data
"""

import os
import json
from datetime import datetime, timezone
from pymongo import MongoClient
import mimetypes

# Configuration
MONGO_URL = "mongodb+srv://lperpere:ClaireMarcus2025@cluster0.24k0jzd.mongodb.net/claire_marcus?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "claire_marcus"
USER_ID = "8aa0e7b1-5279-468b-bbce-028f7a70282d"  # lperpere@yahoo.fr user ID

def load_descriptions():
    """Load content descriptions from JSON file"""
    descriptions_file = "/app/backend/content_descriptions.json"
    try:
        if os.path.exists(descriptions_file):
            with open(descriptions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️ Error loading descriptions: {e}")
    return {}

def migrate_filesystem_to_mongodb():
    """Migrate filesystem data to MongoDB with proper thumb_url"""
    
    print("🔗 Connecting to MongoDB...")
    mongo_client = MongoClient(MONGO_URL)
    db = mongo_client[DB_NAME]
    media_collection = db.media
    
    # Load descriptions
    descriptions = load_descriptions()
    print(f"📝 Loaded {len(descriptions)} descriptions")
    
    # Get files from uploads directory
    uploads_dir = "/app/backend/uploads"
    thumbs_dir = "/app/backend/uploads/thumbs"
    
    if not os.path.exists(uploads_dir):
        print("❌ Uploads directory not found")
        return
    
    print(f"📁 Scanning {uploads_dir}...")
    
    migrated_count = 0
    skipped_count = 0
    
    for filename in os.listdir(uploads_dir):
        file_path = os.path.join(uploads_dir, filename)
        
        if not os.path.isfile(file_path):
            continue
            
        # Get file info
        file_stats = os.stat(file_path)
        file_extension = os.path.splitext(filename)[1].lower()
        
        # Determine content type
        content_type = None
        if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            content_type = f"image/{file_extension[1:]}"
        elif file_extension in ['.mp4', '.mov', '.avi', '.mkv']:
            content_type = f"video/{file_extension[1:]}"
        
        if content_type is None:
            skipped_count += 1
            continue
        
        # Get file ID (filename without extension)
        file_id = filename.split('.')[0]
        
        # Check if thumbnail exists
        thumb_filename = f"{file_id}.webp"
        thumb_path = os.path.join(thumbs_dir, thumb_filename)
        thumb_url = None
        
        if os.path.exists(thumb_path):
            # Use the correct domain as specified in the review
            thumb_url = f"https://social-publisher-10.preview.emergentagent.com/uploads/thumbs/{thumb_filename}"
        
        # Get description
        description = descriptions.get(file_id, "")
        
        # Check if document already exists
        existing_doc = media_collection.find_one({
            "owner_id": USER_ID,
            "filename": filename
        })
        
        if existing_doc:
            # Update existing document
            media_collection.update_one(
                {"_id": existing_doc["_id"]},
                {"$set": {
                    "thumb_url": thumb_url,
                    "description": description,
                    "file_type": content_type,
                    "url": f"https://social-publisher-10.preview.emergentagent.com/uploads/{filename}",
                    "deleted": False
                }}
            )
            print(f"📝 Updated: {filename} (thumb_url: {'✅' if thumb_url else '❌'})")
        else:
            # Create new document
            doc = {
                "owner_id": USER_ID,
                "filename": filename,
                "original_filename": filename,
                "file_type": content_type,
                "url": f"https://social-publisher-10.preview.emergentagent.com/uploads/{filename}",
                "thumb_url": thumb_url,
                "description": description,
                "deleted": False,
                "created_at": datetime.fromtimestamp(file_stats.st_mtime, tz=timezone.utc)
            }
            
            media_collection.insert_one(doc)
            print(f"➕ Created: {filename} (thumb_url: {'✅' if thumb_url else '❌'})")
        
        migrated_count += 1
    
    print(f"\n✅ Migration completed:")
    print(f"   Migrated: {migrated_count} files")
    print(f"   Skipped: {skipped_count} files")
    
    # Verify migration
    print(f"\n🔍 Verification:")
    total_docs = media_collection.count_documents({"owner_id": USER_ID, "deleted": {"$ne": True}})
    docs_with_thumb = media_collection.count_documents({
        "owner_id": USER_ID, 
        "deleted": {"$ne": True},
        "thumb_url": {"$ne": None, "$ne": ""}
    })
    
    print(f"   Total documents: {total_docs}")
    print(f"   With thumb_url: {docs_with_thumb}")
    print(f"   Success rate: {(docs_with_thumb/total_docs*100):.1f}%" if total_docs > 0 else "N/A")
    
    # Check for 8ee21d73 file specifically
    target_doc = media_collection.find_one({
        "owner_id": USER_ID,
        "filename": {"$regex": "8ee21d73"}
    })
    
    if target_doc:
        print(f"\n🎯 Target file 8ee21d73:")
        print(f"   Filename: {target_doc.get('filename')}")
        print(f"   Description: {target_doc.get('description')}")
        print(f"   thumb_url: {target_doc.get('thumb_url')}")
    else:
        print(f"\n❌ Target file 8ee21d73 not found")
    
    mongo_client.close()

if __name__ == "__main__":
    migrate_filesystem_to_mongodb()