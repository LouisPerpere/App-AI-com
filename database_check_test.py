#!/usr/bin/env python3
"""
DATABASE CHECK TEST - Vérifier si les fichiers sont dans la base de données

Ce test vérifie directement la base de données pour voir si les fichiers uploadés
sont bien enregistrés, même si ils n'apparaissent pas dans l'API /content/pending
"""

import requests
import json
from database import get_database

# Configuration
BASE_URL = "https://social-pub-hub.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

def authenticate():
    """Authenticate and get user ID"""
    auth_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login-robust", json=auth_data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            user_id = data.get("user_id")
            print(f"✅ Authentication successful - User ID: {user_id}")
            return user_id
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None

def check_database_directly(user_id):
    """Check database directly for uploaded files"""
    print(f"\n🔍 Checking database directly for user {user_id}")
    
    try:
        # Get database connection
        dbm = get_database()
        media_collection = dbm.db.media
        
        # Find all media for this user
        query = {"owner_id": user_id, "$or": [{"deleted": {"$ne": True}}, {"deleted": {"$exists": False}}]}
        
        print(f"📊 Query: {query}")
        
        # Get total count
        total_count = media_collection.count_documents(query)
        print(f"📊 Total media items in database: {total_count}")
        
        # Get recent items (last 10)
        recent_items = list(media_collection.find(query).sort([("created_at", -1)]).limit(10))
        
        print(f"📊 Recent items found: {len(recent_items)}")
        
        for i, item in enumerate(recent_items):
            print(f"\n📄 Item {i+1}:")
            print(f"   ID: {item.get('id', 'No ID')}")
            print(f"   Filename: {item.get('filename', 'No filename')}")
            print(f"   Created: {item.get('created_at', 'No date')}")
            print(f"   Source: {item.get('source', 'No source')}")
            print(f"   Title: {item.get('title', 'No title')}")
            print(f"   Context: {item.get('context', 'No context')}")
            print(f"   Used in posts: {item.get('used_in_posts', False)}")
            print(f"   Upload type: {item.get('upload_type', 'No type')}")
            print(f"   Attributed month: {item.get('attributed_month', 'No month')}")
        
        return recent_items
        
    except Exception as e:
        print(f"❌ Database check error: {str(e)}")
        return []

def check_api_response(user_id):
    """Check what the API returns"""
    print(f"\n🌐 Checking API response for user {user_id}")
    
    # Get token first
    auth_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login-robust", json=auth_data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            
            # Now get content
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}/content/pending", headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                
                print(f"📊 API returned {len(content)} items")
                print(f"📊 Total from API: {data.get('total', 0)}")
                print(f"📊 Loaded from API: {data.get('loaded', 0)}")
                
                # Show recent items
                for i, item in enumerate(content[:5]):
                    print(f"\n📄 API Item {i+1}:")
                    print(f"   ID: {item.get('id', 'No ID')}")
                    print(f"   Filename: {item.get('filename', 'No filename')}")
                    print(f"   Title: {item.get('title', 'No title')}")
                    print(f"   Context: {item.get('context', 'No context')}")
                    print(f"   Used in posts: {item.get('used_in_posts', False)}")
                
                return content
            else:
                print(f"❌ API request failed: {response.status_code}")
                return []
        else:
            print(f"❌ Authentication for API failed: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ API check error: {str(e)}")
        return []

def main():
    print("🔍 DATABASE CHECK TEST - Vérification directe de la base de données")
    
    # Step 1: Authenticate
    user_id = authenticate()
    if not user_id:
        print("❌ Cannot continue without user ID")
        return
    
    # Step 2: Check database directly
    db_items = check_database_directly(user_id)
    
    # Step 3: Check API response
    api_items = check_api_response(user_id)
    
    # Step 4: Compare results
    print(f"\n📊 COMPARISON:")
    print(f"   Database items: {len(db_items)}")
    print(f"   API items: {len(api_items)}")
    
    if len(db_items) > len(api_items):
        print(f"⚠️ DISCREPANCY: Database has {len(db_items) - len(api_items)} more items than API")
        print("   This suggests an issue with the API query or response formatting")
    elif len(db_items) < len(api_items):
        print(f"⚠️ DISCREPANCY: API has {len(api_items) - len(db_items)} more items than database")
        print("   This is unexpected and suggests a caching or query issue")
    else:
        print("✅ Database and API counts match")
    
    # Check for recent uploads specifically
    if db_items:
        recent_db_ids = [item.get('id') for item in db_items[:3]]
        recent_api_ids = [item.get('id') for item in api_items[:3]]
        
        print(f"\n🔍 Recent IDs comparison:")
        print(f"   Database: {recent_db_ids}")
        print(f"   API: {recent_api_ids}")
        
        missing_in_api = [id for id in recent_db_ids if id not in recent_api_ids]
        if missing_in_api:
            print(f"⚠️ IDs in database but missing from API: {missing_in_api}")

if __name__ == "__main__":
    main()