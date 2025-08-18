#!/usr/bin/env python3
"""
Cleanup corrupted files from MongoDB
Remove documents that have null thumb_url and cannot generate thumbnails (corrupted files)
"""

import os
from pymongo import MongoClient

# Configuration
MONGO_URL = "mongodb+srv://lperpere:ClaireMarcus2025@cluster0.24k0jzd.mongodb.net/claire_marcus?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "claire_marcus"
USER_ID = "8aa0e7b1-5279-468b-bbce-028f7a70282d"

def cleanup_corrupted_files():
    """Remove documents with null thumb_url (corrupted files that can't generate thumbnails)"""
    
    print("🔗 Connecting to MongoDB...")
    mongo_client = MongoClient(MONGO_URL)
    db = mongo_client[DB_NAME]
    media_collection = db.media
    
    # Find documents with null thumb_url
    null_thumb_docs = list(media_collection.find({
        "owner_id": USER_ID,
        "deleted": {"$ne": True},
        "$or": [
            {"thumb_url": None},
            {"thumb_url": ""}
        ]
    }))
    
    print(f"📊 Found {len(null_thumb_docs)} documents with null thumb_url")
    
    deleted_count = 0
    for doc in null_thumb_docs:
        filename = doc.get("filename", "unknown")
        doc_id = doc.get("_id")
        
        # Check if file is corrupted by trying to verify it exists and is readable
        file_path = f"/app/backend/uploads/{filename}"
        is_corrupted = False
        
        if os.path.exists(file_path):
            try:
                # Try to read the file
                with open(file_path, 'rb') as f:
                    # Read first few bytes to check if file is readable
                    data = f.read(100)
                    if len(data) < 10:  # Very small files are likely corrupted
                        is_corrupted = True
            except Exception:
                is_corrupted = True
        else:
            is_corrupted = True
        
        # For images, try to open with PIL to verify they're not corrupted
        if not is_corrupted and filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            try:
                from PIL import Image
                with Image.open(file_path) as img:
                    # Try to load the image
                    img.load()
            except Exception as e:
                print(f"   Image {filename} is corrupted: {e}")
                is_corrupted = True
        
        if is_corrupted:
            # Delete corrupted document from MongoDB
            result = media_collection.delete_one({"_id": doc_id})
            if result.deleted_count == 1:
                deleted_count += 1
                print(f"🗑️ Deleted corrupted file: {filename}")
        else:
            print(f"⚠️ File {filename} exists but has no thumbnail - keeping it")
    
    print(f"\n✅ Cleanup completed: {deleted_count} corrupted documents deleted")
    
    # Verify final state
    remaining_docs = media_collection.count_documents({
        "owner_id": USER_ID,
        "deleted": {"$ne": True}
    })
    
    null_thumb_remaining = media_collection.count_documents({
        "owner_id": USER_ID,
        "deleted": {"$ne": True},
        "$or": [
            {"thumb_url": None},
            {"thumb_url": ""}
        ]
    })
    
    print(f"📊 Final state:")
    print(f"   Total documents: {remaining_docs}")
    print(f"   With null thumb_url: {null_thumb_remaining}")
    print(f"   Success: {'✅' if null_thumb_remaining == 0 else '❌'}")
    
    mongo_client.close()

if __name__ == "__main__":
    cleanup_corrupted_files()