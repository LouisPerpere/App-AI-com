#!/usr/bin/env python3
"""
Check media collection in MongoDB and create test data if needed
"""

import os
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

# MongoDB connection
mongo_url = os.environ.get("MONGO_URL")
client = MongoClient(mongo_url)
db = client.claire_marcus

print("🔍 CHECKING MEDIA COLLECTION")
print("=" * 50)

# Check media collection
media_collection = db.media
media_count = media_collection.count_documents({})
print(f"Total media documents: {media_count}")

if media_count > 0:
    print("\n📋 EXISTING MEDIA:")
    for media in media_collection.find().limit(5):
        print(f"  • ID: {media.get('_id')}")
        print(f"    Filename: {media.get('filename', 'N/A')}")
        print(f"    File Type: {media.get('file_type', 'N/A')}")
        print(f"    Owner ID: {media.get('owner_id', 'N/A')}")
        print(f"    Thumb URL: {media.get('thumb_url', 'N/A')}")
        print()
else:
    print("No media documents found.")
    
    # Create test media document
    print("\n🔧 CREATING TEST MEDIA DOCUMENT")
    test_media = {
        "_id": ObjectId(),
        "filename": "test_image.jpg",
        "file_type": "image/jpeg",
        "owner_id": "demo_user_id",
        "uploaded_at": datetime.utcnow(),
        "deleted": False,
        "description": "Test image for thumbnail testing"
    }
    
    result = media_collection.insert_one(test_media)
    print(f"✅ Created test media with ID: {result.inserted_id}")

# Check thumbnails collection
print("\n🖼️ CHECKING THUMBNAILS COLLECTION")
print("=" * 50)

thumbnails_collection = db.thumbnails
thumb_count = thumbnails_collection.count_documents({})
print(f"Total thumbnail documents: {thumb_count}")

if thumb_count > 0:
    print("\n📋 EXISTING THUMBNAILS:")
    for thumb in thumbnails_collection.find().limit(3):
        print(f"  • Media ID: {thumb.get('media_id')}")
        print(f"    Owner ID: {thumb.get('owner_id', 'N/A')}")
        print(f"    Content Type: {thumb.get('content_type', 'N/A')}")
        print(f"    Size: {thumb.get('size', 0)} bytes")
        print()

print("\n✅ Database check complete")