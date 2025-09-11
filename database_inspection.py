#!/usr/bin/env python3
"""
DETAILED DATABASE INSPECTION
Inspect the actual database structure and content.
"""

import sys
import os
sys.path.append('/app/backend')

from database import get_database

def inspect_database():
    """Inspect database structure"""
    
    user_id = "bdf87a74-e3f3-44f3-bac2-649cde3ef93e"
    
    print(f"🔍 Inspecting database for user: {user_id}")
    
    # Get database connection
    db_manager = get_database()
    if not db_manager.is_connected():
        print("❌ Database not connected")
        return
    
    print("✅ Database connected")
    
    # List all collections
    collections = db_manager.db.list_collection_names()
    print(f"\n📋 Available collections: {collections}")
    
    # Check media collection
    media_count = db_manager.db.media.count_documents({"owner_id": user_id})
    print(f"\n📂 Media collection:")
    print(f"   Total items for user: {media_count}")
    
    # Get a sample document to see structure
    sample_doc = db_manager.db.media.find_one({"owner_id": user_id})
    if sample_doc:
        print(f"\n📄 Sample document structure:")
        for key, value in sample_doc.items():
            if key == "_id":
                print(f"   {key}: {value} (ObjectId)")
            else:
                print(f"   {key}: {value}")
    
    # Check for items with attributed_month
    items_with_month = db_manager.db.media.count_documents({
        "owner_id": user_id,
        "attributed_month": {"$exists": True, "$ne": ""}
    })
    print(f"\n📅 Items with attributed_month field: {items_with_month}")
    
    # Check for items with attributed_month = septembre_2025
    items_septembre = db_manager.db.media.count_documents({
        "owner_id": user_id,
        "attributed_month": "septembre_2025"
    })
    print(f"   Items with attributed_month='septembre_2025': {items_septembre}")
    
    # Show a few items with their attributed_month values
    print(f"\n📋 First 5 items with attributed_month details:")
    items = list(db_manager.db.media.find({"owner_id": user_id}).limit(5))
    for i, item in enumerate(items):
        print(f"   {i+1}. ID: {item.get('id', 'No ID')}")
        print(f"      _id: {item.get('_id', 'No _id')}")
        print(f"      Filename: {item.get('filename', 'No filename')}")
        print(f"      Attributed month: {repr(item.get('attributed_month', 'FIELD_NOT_FOUND'))}")
        print(f"      All fields: {list(item.keys())}")
        print()

if __name__ == "__main__":
    inspect_database()