#!/usr/bin/env python3
"""
Script de migration pour peupler MongoDB avec les fichiers existants
(selon ChatGPT)
"""
import os
import asyncio
import json
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# Configuration
MONGO_URL = os.environ.get('MONGO_URL')
DEFAULT_USER_ID = "default_user"  # À remplacer par vrai user_id

async def migrate_filesystem_to_mongo():
    """Migre les fichiers du filesystem vers MongoDB"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.claire_marcus
    media_collection = db.media
    
    # Ensure index on owner_id + deleted
    await media_collection.create_index([("owner_id", 1), ("deleted", 1)])
    
    print("🔄 Starting migration from filesystem to MongoDB...")
    
    # Load existing descriptions
    descriptions_file = "content_descriptions.json"
    descriptions = {}
    if os.path.exists(descriptions_file):
        try:
            with open(descriptions_file, 'r', encoding='utf-8') as f:
                descriptions = json.load(f)
            print(f"📝 Loaded {len(descriptions)} descriptions from JSON")
        except Exception as e:
            print(f"⚠️ Error loading descriptions: {e}")
    
    # Scan uploads directory
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        print("❌ Uploads directory not found")
        return
    
    migrated_count = 0
    skipped_count = 0
    
    for filename in os.listdir(uploads_dir):
        file_path = os.path.join(uploads_dir, filename)
        if not os.path.isfile(file_path):
            continue
        
        file_id = filename.split('.')[0]
        file_stats = os.stat(file_path)
        
        # Determine file type
        file_extension = os.path.splitext(filename)[1].lower()
        if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            file_type = f"image/{file_extension[1:]}"
        elif file_extension in ['.mp4', '.mov', '.avi', '.mkv']:
            file_type = f"video/{file_extension[1:]}"
        else:
            print(f"⏭️ Skipping {filename} (unsupported type)")
            skipped_count += 1
            continue
        
        # Check if already exists in MongoDB
        existing = await media_collection.find_one({"filename": filename})
        if existing:
            print(f"⏭️ Skipping {filename} (already in MongoDB)")
            skipped_count += 1
            continue
        
        # Create MongoDB document
        doc = {
            "_id": ObjectId(),
            "owner_id": DEFAULT_USER_ID,  # TODO: Map to real user
            "filename": filename,
            "file_type": file_type,
            "description": descriptions.get(file_id, ""),
            "size": file_stats.st_size,
            "deleted": False,
            "created_at": datetime.fromtimestamp(file_stats.st_mtime),
            "migrated_from_filesystem": True
        }
        
        # Insert into MongoDB
        try:
            await media_collection.insert_one(doc)
            print(f"✅ Migrated {filename} → {doc['_id']}")
            migrated_count += 1
        except Exception as e:
            print(f"❌ Error migrating {filename}: {e}")
    
    print(f"\n🎉 Migration completed:")
    print(f"   • Migrated: {migrated_count} files")
    print(f"   • Skipped: {skipped_count} files")
    
    # Show total documents in collection
    total_docs = await media_collection.count_documents({})
    print(f"   • Total in MongoDB: {total_docs} documents")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(migrate_filesystem_to_mongo())