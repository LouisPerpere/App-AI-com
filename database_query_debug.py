#!/usr/bin/env python3
"""
DATABASE QUERY DEBUG TEST
Test the exact database query used by posts_generator.
"""

import sys
import os
sys.path.append('/app/backend')

from database import get_database

def test_database_query():
    """Test the database query directly"""
    
    user_id = "bdf87a74-e3f3-44f3-bac2-649cde3ef93e"
    target_month = "septembre_2025"
    
    print(f"🔍 Testing database query for user: {user_id}")
    print(f"🔍 Target month: {target_month}")
    
    # Get database connection
    db_manager = get_database()
    if not db_manager.is_connected():
        print("❌ Database not connected")
        return
    
    print("✅ Database connected")
    
    # Test the exact query used by posts_generator
    query = {
        "owner_id": user_id,
        "attributed_month": target_month,
        "deleted": {"$ne": True}
    }
    
    print(f"\n🔍 Query: {query}")
    
    # Execute query
    month_content = list(db_manager.db.media.find(query).limit(50))
    
    print(f"✅ Query executed")
    print(f"   Results found: {len(month_content)}")
    
    # Show first few results
    for i, item in enumerate(month_content[:3]):
        print(f"   {i+1}. ID: {item.get('id', 'No ID')}")
        print(f"      Filename: {item.get('filename', 'No filename')}")
        print(f"      Attributed month: {item.get('attributed_month', 'No attributed_month')}")
        print(f"      Owner ID: {item.get('owner_id', 'No owner_id')}")
        print(f"      URL: {item.get('url', 'No URL')}")
        print()
    
    # Test fallback query (all content)
    if len(month_content) == 0:
        print("\n🔍 Testing fallback query (all content)...")
        fallback_query = {
            "owner_id": user_id,
            "deleted": {"$ne": True}
        }
        
        print(f"🔍 Fallback query: {fallback_query}")
        
        all_content = list(db_manager.db.media.find(fallback_query).sort([("created_at", -1)]).limit(50))
        
        print(f"✅ Fallback query executed")
        print(f"   Results found: {len(all_content)}")
        
        # Show first few results
        for i, item in enumerate(all_content[:3]):
            print(f"   {i+1}. ID: {item.get('id', 'No ID')}")
            print(f"      Filename: {item.get('filename', 'No filename')}")
            print(f"      Attributed month: {item.get('attributed_month', 'No attributed_month')}")
            print(f"      Owner ID: {item.get('owner_id', 'No owner_id')}")
            print(f"      URL: {item.get('url', 'No URL')}")
            print()

if __name__ == "__main__":
    test_database_query()