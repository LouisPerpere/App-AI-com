#!/usr/bin/env python3
"""
Simple test to verify the thumb URL update via API
"""

import requests
import json

# Configuration
BACKEND_URL = "https://libfusion.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

def test_thumb_url_update():
    """Test the thumb URL update via API"""
    print("🔍 Testing Thumb URL Update via API")
    print("=" * 50)
    
    session = requests.Session()
    
    # Step 1: Authenticate
    try:
        print("🔐 Authenticating...")
        response = session.post(f"{API_BASE}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            user_id = data.get("user_id")
            
            session.headers.update({
                "Authorization": f"Bearer {access_token}"
            })
            
            print(f"✅ Authentication successful - User ID: {user_id}")
        else:
            print(f"❌ Authentication failed - Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False
    
    # Step 2: Test GET /api/content/pending
    try:
        print("\n📋 Testing GET /api/content/pending...")
        response = session.get(f"{API_BASE}/content/pending?limit=10")
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("content", [])
            
            print(f"✅ Retrieved {len(content)} content items")
            
            # Check thumb_url domains
            claire_marcus_count = 0
            libfusion_count = 0
            sample_urls = []
            
            for item in content:
                thumb_url = item.get("thumb_url")
                if thumb_url:
                    if thumb_url.startswith("https://claire-marcus.com/uploads/thumbs/"):
                        claire_marcus_count += 1
                    elif thumb_url.startswith("https://libfusion.preview.emergentagent.com/uploads/thumbs/"):
                        libfusion_count += 1
                    
                    if len(sample_urls) < 3:
                        sample_urls.append(thumb_url)
            
            print(f"📊 Thumb URL Analysis:")
            print(f"   - Claire Marcus domain: {claire_marcus_count}")
            print(f"   - Libfusion domain: {libfusion_count}")
            
            if sample_urls:
                print(f"📝 Sample thumb URLs:")
                for url in sample_urls:
                    print(f"   - {url}")
            
            # Success if we have claire-marcus URLs and no libfusion URLs
            success = claire_marcus_count > 0 and libfusion_count == 0
            
            if success:
                print("✅ SUCCESS: All thumb_url now point to claire-marcus.com domain!")
            else:
                print("⚠️ PARTIAL: Some URLs may still point to old domain")
            
            return success
            
        else:
            print(f"❌ API call failed - Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API test error: {e}")
        return False

if __name__ == "__main__":
    success = test_thumb_url_update()
    
    if success:
        print("\n🎉 THUMB URL UPDATE VERIFICATION: SUCCESS")
        print("All thumb_url have been successfully updated to use claire-marcus.com domain!")
    else:
        print("\n❌ THUMB URL UPDATE VERIFICATION: FAILED")
        print("Some issues were found with the thumb URL update.")