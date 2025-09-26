#!/usr/bin/env python3
"""
Thumbnail Test with Real File - Create a test media entry that matches existing disk file
"""

import requests
import time
import json
import os
import sys
sys.path.append('/app/backend')

from database import get_database
from bson import ObjectId
from datetime import datetime

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://social-ai-planner-2.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Known credentials
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

def get_auth_token():
    """Get authentication token"""
    response = requests.post(
        f"{API_BASE}/auth/login-robust",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    if response.status_code == 200:
        data = response.json()
        return data.get('access_token'), data.get('user_id')
    return None, None

def create_test_media_entry(user_id: str):
    """Create a test media entry in database that matches existing disk file"""
    print("🔧 Creating test media entry in database...")
    
    # Use an existing file on disk
    test_filename = "0383fc42-afb0-43a9-873f-18cd274b3b68.jpg"
    test_file_path = f"/app/backend/uploads/{test_filename}"
    
    if not os.path.exists(test_file_path):
        print(f"❌ Test file {test_filename} not found on disk")
        return None
    
    # Get database connection
    db_manager = get_database()
    media_collection = db_manager.db.media
    
    # Create media document
    media_doc = {
        "_id": ObjectId(),
        "filename": test_filename,
        "file_type": "image/jpeg",
        "owner_id": user_id,
        "url": f"/uploads/{test_filename}",
        "thumb_url": f"https://claire-marcus-api.onrender.com/uploads/thumbs/{test_filename.replace('.jpg', '.webp')}",
        "description": "Test image for thumbnail testing",
        "created_at": datetime.utcnow(),
        "deleted": False
    }
    
    # Insert into database
    result = media_collection.insert_one(media_doc)
    file_id = str(result.inserted_id)
    
    print(f"✅ Created test media entry - ID: {file_id}, Filename: {test_filename}")
    return file_id

def test_thumbnail_endpoints(token: str, file_id: str):
    """Test all thumbnail endpoints with the created file"""
    print(f"🧪 Testing thumbnail endpoints with file ID: {file_id}")
    
    headers = {'Authorization': f'Bearer {token}'}
    session = requests.Session()
    session.headers.update(headers)
    
    results = {}
    
    # Test 1: GET /api/content/{id}/thumb (initial state)
    print("\n1️⃣ Testing GET /api/content/{id}/thumb (initial state)")
    response = session.get(f"{API_BASE}/content/{file_id}/thumb")
    
    if response.status_code == 200:
        content_type = response.headers.get('content-type', '')
        content_length = len(response.content)
        print(f"✅ Thumbnail retrieved - Content-Type: {content_type}, Size: {content_length} bytes")
        results['initial_thumb'] = True
    elif response.status_code == 404:
        print("⚠️ Thumbnail not found (404) - Will test generation")
        results['initial_thumb'] = False
    else:
        print(f"❌ Unexpected response - Status: {response.status_code}")
        results['initial_thumb'] = False
    
    # Test 2: POST /api/content/{id}/thumbnail (generate)
    print("\n2️⃣ Testing POST /api/content/{id}/thumbnail (generate)")
    response = session.post(f"{API_BASE}/content/{file_id}/thumbnail")
    
    if response.status_code == 200:
        data = response.json()
        scheduled = data.get('scheduled', False)
        print(f"✅ Thumbnail generation scheduled: {scheduled}")
        results['generation'] = scheduled
        
        if scheduled:
            print("⏳ Waiting 3 seconds for generation...")
            time.sleep(3)
            
            # Test retrieval after generation
            print("🔄 Testing thumbnail retrieval after generation...")
            response = session.get(f"{API_BASE}/content/{file_id}/thumb")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                print(f"✅ Generated thumbnail retrieved - Content-Type: {content_type}, Size: {content_length} bytes")
                results['post_generation_retrieval'] = True
            else:
                print(f"❌ Failed to retrieve generated thumbnail - Status: {response.status_code}")
                results['post_generation_retrieval'] = False
    else:
        print(f"❌ Failed to schedule generation - Status: {response.status_code}, Response: {response.text}")
        results['generation'] = False
        results['post_generation_retrieval'] = False
    
    # Test 3: POST /api/content/thumbnails/rebuild
    print("\n3️⃣ Testing POST /api/content/thumbnails/rebuild")
    response = session.post(f"{API_BASE}/content/thumbnails/rebuild")
    
    if response.status_code == 200:
        data = response.json()
        scheduled = data.get('scheduled', 0)
        files_found = data.get('files_found', 0)
        print(f"✅ Rebuild triggered - Scheduled: {scheduled}, Files found: {files_found}")
        results['rebuild'] = True
    else:
        print(f"❌ Rebuild failed - Status: {response.status_code}")
        results['rebuild'] = False
    
    # Test 4: GET /api/content/thumbnails/status
    print("\n4️⃣ Testing GET /api/content/thumbnails/status")
    response = session.get(f"{API_BASE}/content/thumbnails/status")
    
    if response.status_code == 200:
        data = response.json()
        total_files = data.get('total_files', 0)
        with_thumbnails = data.get('with_thumbnails', 0)
        missing_thumbnails = data.get('missing_thumbnails', 0)
        completion_percentage = data.get('completion_percentage', 0)
        
        print(f"✅ Status retrieved:")
        print(f"   - Total files: {total_files}")
        print(f"   - With thumbnails: {with_thumbnails}")
        print(f"   - Missing thumbnails: {missing_thumbnails}")
        print(f"   - Completion: {completion_percentage}%")
        results['status'] = True
    else:
        print(f"❌ Status failed - Status: {response.status_code}")
        results['status'] = False
    
    # Test 5: Verify thumb_url update
    print("\n5️⃣ Testing thumb_url update verification")
    response = session.get(f"{API_BASE}/content/pending?limit=100&offset=0")
    
    if response.status_code == 200:
        data = response.json()
        content_items = data.get('content', [])
        
        for item in content_items:
            if item.get('id') == file_id:
                thumb_url = item.get('thumb_url', '')
                expected_url = f"/api/content/{file_id}/thumb"
                
                print(f"📋 Found file - thumb_url: '{thumb_url}'")
                print(f"📋 Expected: '{expected_url}'")
                
                if thumb_url == expected_url:
                    print("✅ thumb_url correctly updated to relative API path")
                    results['thumb_url_update'] = True
                else:
                    print(f"⚠️ thumb_url not updated yet - Expected: {expected_url}, Got: {thumb_url}")
                    results['thumb_url_update'] = False
                break
        else:
            print(f"❌ File ID {file_id} not found in content list")
            results['thumb_url_update'] = False
    else:
        print(f"❌ Failed to get content - Status: {response.status_code}")
        results['thumb_url_update'] = False
    
    return results

def cleanup_test_entry(file_id: str):
    """Clean up the test media entry"""
    print(f"🧹 Cleaning up test media entry: {file_id}")
    
    try:
        db_manager = get_database()
        media_collection = db_manager.db.media
        
        # Delete the test entry
        result = media_collection.delete_one({"_id": ObjectId(file_id)})
        
        if result.deleted_count > 0:
            print("✅ Test media entry cleaned up")
        else:
            print("⚠️ Test media entry not found for cleanup")
            
        # Also clean up thumbnail if exists
        thumbs_collection = db_manager.db.thumbnails
        thumb_result = thumbs_collection.delete_one({"media_id": ObjectId(file_id)})
        
        if thumb_result.deleted_count > 0:
            print("✅ Test thumbnail cleaned up")
        else:
            print("⚠️ Test thumbnail not found for cleanup")
            
    except Exception as e:
        print(f"❌ Cleanup error: {str(e)}")

def main():
    """Main test execution"""
    print("🚀 Starting Thumbnail Persistence Test with Real File")
    print("=" * 60)
    
    # Get authentication
    token, user_id = get_auth_token()
    if not token or not user_id:
        print("❌ Failed to authenticate")
        return False
    
    print(f"✅ Authenticated - User ID: {user_id}")
    
    # Create test media entry
    file_id = create_test_media_entry(user_id)
    if not file_id:
        print("❌ Failed to create test media entry")
        return False
    
    try:
        # Run tests
        results = test_thumbnail_endpoints(token, file_id)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY:")
        
        test_names = {
            'initial_thumb': 'Initial Thumbnail Check',
            'generation': 'Thumbnail Generation Scheduling',
            'post_generation_retrieval': 'Post-Generation Retrieval',
            'rebuild': 'Rebuild Functionality',
            'status': 'Status Endpoint',
            'thumb_url_update': 'Thumb URL Update'
        }
        
        passed = 0
        total = len(results)
        
        for key, value in results.items():
            test_name = test_names.get(key, key)
            status = "✅ PASS" if value else "❌ FAIL"
            print(f"{status} {test_name}")
            if value:
                passed += 1
        
        success_rate = (passed / total) * 100 if total > 0 else 0
        print(f"\n📈 SUCCESS RATE: {passed}/{total} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 THUMBNAIL PERSISTENCE TEST PASSED")
            return True
        else:
            print("❌ THUMBNAIL PERSISTENCE TEST FAILED")
            return False
            
    finally:
        # Always cleanup
        cleanup_test_entry(file_id)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)