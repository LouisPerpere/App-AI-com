#!/usr/bin/env python3
"""
UPLOAD DEBUG TEST - Vérifier l'insertion en base de données immédiatement après upload
"""

import requests
import json
import sys
import io
from PIL import Image
import time

# Configuration
BASE_URL = "https://social-pub-hub.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

def authenticate():
    """Authenticate and get JWT token"""
    auth_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login-robust", json=auth_data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_id = data.get("user_id")
            print(f"✅ Authentication successful - User ID: {user_id}")
            return token, user_id
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None, None

def upload_and_check(token, user_id):
    """Upload a file and immediately check database"""
    print(f"\n🔍 Upload and immediate database check")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a unique test image
    unique_color = (255, 128, 64)  # Orange color for identification
    img = Image.new('RGB', (100, 100), color=unique_color)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Upload with unique identifiers
    test_title = f"DEBUG_TEST_{int(time.time())}"
    test_context = f"Debug test context {int(time.time())}"
    
    files = {
        'files': ('debug_test.png', img_bytes, 'image/png')
    }
    
    form_data = {
        'attributed_month': 'debug_2025',
        'upload_type': 'debug_test',
        'common_title': test_title,
        'common_context': test_context
    }
    
    print(f"📤 Uploading with title: {test_title}")
    
    try:
        # Step 1: Upload
        response = requests.post(
            f"{BASE_URL}/content/batch-upload",
            files=files,
            data=form_data,
            headers=headers,
            timeout=60
        )
        
        print(f"📊 Upload response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            uploaded_files = data.get("created", [])
            
            if uploaded_files:
                uploaded_file = uploaded_files[0]
                file_id = uploaded_file.get("id")
                print(f"✅ Upload successful - ID: {file_id}")
                
                # Step 2: Immediate database check via Python
                print(f"🔍 Checking database immediately...")
                
                # Import database module
                import sys
                sys.path.append('/app/backend')
                from database import get_database
                
                dbm = get_database()
                media_collection = dbm.db.media
                
                # Look for our specific upload
                db_item = media_collection.find_one({"id": file_id})
                
                if db_item:
                    print(f"✅ FOUND in database!")
                    print(f"   ID: {db_item.get('id')}")
                    print(f"   Title: {db_item.get('title')}")
                    print(f"   Context: {db_item.get('context')}")
                    print(f"   Created: {db_item.get('created_at')}")
                    
                    # Step 3: Check API response
                    print(f"🌐 Checking API response...")
                    
                    api_response = requests.get(f"{BASE_URL}/content/pending", headers=headers, timeout=30)
                    
                    if api_response.status_code == 200:
                        api_data = api_response.json()
                        api_items = api_data.get("content", [])
                        
                        # Look for our item in API response
                        found_in_api = False
                        for item in api_items:
                            if item.get("id") == file_id:
                                found_in_api = True
                                print(f"✅ FOUND in API response!")
                                print(f"   Title: {item.get('title')}")
                                print(f"   Context: {item.get('context')}")
                                break
                        
                        if not found_in_api:
                            print(f"❌ NOT FOUND in API response")
                            print(f"   API returned {len(api_items)} items")
                            print(f"   Looking for ID: {file_id}")
                            
                            # Show first few API items for comparison
                            for i, item in enumerate(api_items[:3]):
                                print(f"   API Item {i+1}: {item.get('id', 'No ID')}")
                    else:
                        print(f"❌ API request failed: {api_response.status_code}")
                    
                    return True
                else:
                    print(f"❌ NOT FOUND in database")
                    
                    # Check if there are any items with our title/context
                    title_match = media_collection.find_one({"title": test_title})
                    context_match = media_collection.find_one({"context": test_context})
                    
                    if title_match:
                        print(f"⚠️ Found item with matching title but different ID: {title_match.get('id')}")
                    if context_match:
                        print(f"⚠️ Found item with matching context but different ID: {context_match.get('id')}")
                    
                    return False
            else:
                print(f"❌ No files in upload response")
                return False
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        return False

def main():
    print("🔍 UPLOAD DEBUG TEST - Vérification immédiate de l'insertion")
    
    # Step 1: Authentication
    token, user_id = authenticate()
    if not token:
        print("❌ Cannot continue without authentication")
        sys.exit(1)
    
    # Step 2: Upload and check
    success = upload_and_check(token, user_id)
    
    if success:
        print(f"\n✅ SUCCESS: Upload and database insertion working correctly")
    else:
        print(f"\n❌ FAILURE: Upload or database insertion not working")

if __name__ == "__main__":
    main()