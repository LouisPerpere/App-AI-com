#!/usr/bin/env python3
"""
Render Backend Testing Script
Tests the Claire Marcus API deployed on Render at https://claire-marcus-api.onrender.com
Following the specific review request flow.
"""

import requests
import json
import io
from PIL import Image
import time

# Base URL for Render deployment
BASE_URL = "https://claire-marcus-api.onrender.com"

# Test credentials from review request
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

def create_minimal_png():
    """Create a minimal 1x1 PNG image in memory"""
    img = Image.new('RGB', (1, 1), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def test_render_backend():
    """Test the Render backend following the review request flow"""
    print("🎯 RENDER BACKEND TESTING - Claire Marcus API")
    print(f"Base URL: {BASE_URL}")
    print("=" * 60)
    
    results = []
    access_token = None
    uploaded_id = None
    
    # Step 1: Authentication
    print("\n1️⃣ STEP 1: Authentication")
    try:
        auth_url = f"{BASE_URL}/api/auth/login-robust"
        auth_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
        
        print(f"POST {auth_url}")
        print(f"Payload: {json.dumps(auth_data, indent=2)}")
        
        response = requests.post(auth_url, json=auth_data, timeout=120)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access_token')
            print(f"✅ Authentication successful")
            print(f"Access token: {access_token[:20]}..." if access_token else "No token")
            results.append("✅ Step 1: Authentication - SUCCESS")
        else:
            print(f"❌ Authentication failed")
            print(f"Response: {response.text}")
            results.append(f"❌ Step 1: Authentication - FAILED ({response.status_code})")
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        results.append(f"❌ Step 1: Authentication - ERROR ({e})")
    
    # Step 2: Health Check
    print("\n2️⃣ STEP 2: Health Check")
    try:
        health_url = f"{BASE_URL}/api/health"
        print(f"GET {health_url}")
        
        response = requests.get(health_url, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status')
            print(f"✅ Health check successful")
            print(f"Status: {status}")
            print(f"Response: {json.dumps(data, indent=2)}")
            results.append("✅ Step 2: Health check - SUCCESS")
        else:
            print(f"❌ Health check failed")
            print(f"Response: {response.text}")
            results.append(f"❌ Step 2: Health check - FAILED ({response.status_code})")
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        results.append(f"❌ Step 2: Health check - ERROR ({e})")
    
    # Step 3: Website Analysis - GET
    print("\n3️⃣ STEP 3: Website Analysis - GET")
    if access_token:
        try:
            analysis_url = f"{BASE_URL}/api/website/analysis"
            headers = {"Authorization": f"Bearer {access_token}"}
            
            print(f"GET {analysis_url}")
            print(f"Headers: Authorization: Bearer {access_token[:20]}...")
            
            response = requests.get(analysis_url, headers=headers, timeout=30)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                analysis = data.get('analysis')
                print(f"✅ Website analysis GET successful")
                print(f"Analysis: {analysis}")
                results.append("✅ Step 3: Website analysis GET - SUCCESS")
            else:
                print(f"❌ Website analysis GET failed")
                print(f"Response: {response.text}")
                results.append(f"❌ Step 3: Website analysis GET - FAILED ({response.status_code})")
                
        except Exception as e:
            print(f"❌ Website analysis GET error: {e}")
            results.append(f"❌ Step 3: Website analysis GET - ERROR ({e})")
    else:
        print("⚠️ Skipping - no access token")
        results.append("⚠️ Step 3: Website analysis GET - SKIPPED (no token)")
    
    # Step 4: Website Analysis - POST
    print("\n4️⃣ STEP 4: Website Analysis - POST")
    if access_token:
        try:
            analyze_url = f"{BASE_URL}/api/website/analyze"
            headers = {"Authorization": f"Bearer {access_token}"}
            analyze_data = {"website_url": "example.com"}
            
            print(f"POST {analyze_url}")
            print(f"Headers: Authorization: Bearer {access_token[:20]}...")
            print(f"Payload: {json.dumps(analyze_data, indent=2)}")
            
            response = requests.post(analyze_url, json=analyze_data, headers=headers, timeout=60)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Website analysis POST successful")
                print(f"Analysis keys: {list(data.keys())}")
                results.append("✅ Step 4: Website analysis POST - SUCCESS")
            else:
                print(f"❌ Website analysis POST failed")
                print(f"Response: {response.text}")
                results.append(f"❌ Step 4: Website analysis POST - FAILED ({response.status_code})")
                
        except Exception as e:
            print(f"❌ Website analysis POST error: {e}")
            results.append(f"❌ Step 4: Website analysis POST - ERROR ({e})")
    else:
        print("⚠️ Skipping - no access token")
        results.append("⚠️ Step 4: Website analysis POST - SKIPPED (no token)")
    
    # Step 5: Content Upload
    print("\n5️⃣ STEP 5: Content Upload")
    if access_token:
        try:
            upload_url = f"{BASE_URL}/api/content/upload"
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Create minimal PNG
            png_data = create_minimal_png()
            files = {"file": ("test.png", png_data, "image/png")}
            
            print(f"POST {upload_url}")
            print(f"Headers: Authorization: Bearer {access_token[:20]}...")
            print(f"Files: test.png (1x1 PNG)")
            
            response = requests.post(upload_url, files=files, headers=headers, timeout=60)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                uploaded_id = data.get('id')
                thumb_url = data.get('thumb_url')
                print(f"✅ Content upload successful")
                print(f"ID: {uploaded_id}")
                print(f"Thumb URL: {thumb_url}")
                results.append("✅ Step 5: Content upload - SUCCESS")
            else:
                print(f"❌ Content upload failed")
                print(f"Response: {response.text}")
                results.append(f"❌ Step 5: Content upload - FAILED ({response.status_code})")
                
        except Exception as e:
            print(f"❌ Content upload error: {e}")
            results.append(f"❌ Step 5: Content upload - ERROR ({e})")
    else:
        print("⚠️ Skipping - no access token")
        results.append("⚠️ Step 5: Content upload - SKIPPED (no token)")
    
    # Step 6: Content Pending
    print("\n6️⃣ STEP 6: Content Pending")
    if access_token:
        try:
            pending_url = f"{BASE_URL}/api/content/pending"
            headers = {"Authorization": f"Bearer {access_token}"}
            
            print(f"GET {pending_url}")
            print(f"Headers: Authorization: Bearer {access_token[:20]}...")
            
            response = requests.get(pending_url, headers=headers, timeout=30)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                content_list = data.get('content', [])
                total = data.get('total', 0)
                print(f"✅ Content pending successful")
                print(f"Total items: {total}")
                print(f"Items in response: {len(content_list)}")
                results.append("✅ Step 6: Content pending - SUCCESS")
            else:
                print(f"❌ Content pending failed")
                print(f"Response: {response.text}")
                results.append(f"❌ Step 6: Content pending - FAILED ({response.status_code})")
                
        except Exception as e:
            print(f"❌ Content pending error: {e}")
            results.append(f"❌ Step 6: Content pending - ERROR ({e})")
    else:
        print("⚠️ Skipping - no access token")
        results.append("⚠️ Step 6: Content pending - SKIPPED (no token)")
    
    # Step 7: Thumbnail Access
    print("\n7️⃣ STEP 7: Thumbnail Access")
    if access_token and uploaded_id:
        try:
            thumb_url = f"{BASE_URL}/api/content/{uploaded_id}/thumb"
            headers = {"Authorization": f"Bearer {access_token}"}
            
            print(f"GET {thumb_url}")
            print(f"Headers: Authorization: Bearer {access_token[:20]}...")
            
            response = requests.get(thumb_url, headers=headers, timeout=30)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                print(f"✅ Thumbnail access successful")
                print(f"Content-Type: {content_type}")
                print(f"Content length: {len(response.content)} bytes")
                results.append("✅ Step 7: Thumbnail access - SUCCESS")
            else:
                print(f"❌ Thumbnail access failed")
                print(f"Response: {response.text}")
                results.append(f"❌ Step 7: Thumbnail access - FAILED ({response.status_code})")
                
        except Exception as e:
            print(f"❌ Thumbnail access error: {e}")
            results.append(f"❌ Step 7: Thumbnail access - ERROR ({e})")
    else:
        print("⚠️ Skipping - no access token or uploaded ID")
        results.append("⚠️ Step 7: Thumbnail access - SKIPPED (no token/ID)")
    
    # Step 8: File Streaming
    print("\n8️⃣ STEP 8: File Streaming")
    if access_token and uploaded_id:
        try:
            file_url = f"{BASE_URL}/api/content/{uploaded_id}/file"
            headers = {"Authorization": f"Bearer {access_token}"}
            
            print(f"GET {file_url}")
            print(f"Headers: Authorization: Bearer {access_token[:20]}...")
            
            response = requests.get(file_url, headers=headers, timeout=30)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                print(f"✅ File streaming successful")
                print(f"Content-Type: {content_type}")
                print(f"Content length: {len(response.content)} bytes")
                results.append("✅ Step 8: File streaming - SUCCESS")
            else:
                print(f"❌ File streaming failed")
                print(f"Response: {response.text}")
                results.append(f"❌ Step 8: File streaming - FAILED ({response.status_code})")
                
        except Exception as e:
            print(f"❌ File streaming error: {e}")
            results.append(f"❌ Step 8: File streaming - ERROR ({e})")
    else:
        print("⚠️ Skipping - no access token or uploaded ID")
        results.append("⚠️ Step 8: File streaming - SKIPPED (no token/ID)")
    
    # Step 9: Thumbnails Status
    print("\n9️⃣ STEP 9: Thumbnails Status")
    try:
        status_url = f"{BASE_URL}/api/content/thumbnails/status"
        
        print(f"GET {status_url}")
        
        response = requests.get(status_url, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Thumbnails status successful")
            print(f"Response: {json.dumps(data, indent=2)}")
            results.append("✅ Step 9: Thumbnails status - SUCCESS")
        else:
            print(f"❌ Thumbnails status failed")
            print(f"Response: {response.text}")
            results.append(f"❌ Step 9: Thumbnails status - FAILED ({response.status_code})")
            
    except Exception as e:
        print(f"❌ Thumbnails status error: {e}")
        results.append(f"❌ Step 9: Thumbnails status - ERROR ({e})")
    
    # Step 10: Thumbnails Orphans
    print("\n🔟 STEP 10: Thumbnails Orphans")
    try:
        orphans_url = f"{BASE_URL}/api/content/thumbnails/orphans"
        
        print(f"GET {orphans_url}")
        
        response = requests.get(orphans_url, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Thumbnails orphans successful")
            print(f"Response structure verified")
            results.append("✅ Step 10: Thumbnails orphans - SUCCESS")
        else:
            print(f"❌ Thumbnails orphans failed")
            print(f"Response: {response.text}")
            results.append(f"❌ Step 10: Thumbnails orphans - FAILED ({response.status_code})")
            
    except Exception as e:
        print(f"❌ Thumbnails orphans error: {e}")
        results.append(f"❌ Step 10: Thumbnails orphans - ERROR ({e})")
    
    # Step 11: Thumbnails Normalize
    print("\n1️⃣1️⃣ STEP 11: Thumbnails Normalize")
    try:
        normalize_url = f"{BASE_URL}/api/content/thumbnails/normalize"
        
        print(f"POST {normalize_url}")
        
        response = requests.post(normalize_url, timeout=60)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            ok = data.get('ok')
            updated = data.get('updated', 0)
            print(f"✅ Thumbnails normalize successful")
            print(f"OK: {ok}, Updated: {updated}")
            results.append("✅ Step 11: Thumbnails normalize - SUCCESS")
        else:
            print(f"❌ Thumbnails normalize failed")
            print(f"Response: {response.text}")
            results.append(f"❌ Step 11: Thumbnails normalize - FAILED ({response.status_code})")
            
    except Exception as e:
        print(f"❌ Thumbnails normalize error: {e}")
        results.append(f"❌ Step 11: Thumbnails normalize - ERROR ({e})")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 RENDER BACKEND TEST SUMMARY")
    print("=" * 60)
    
    success_count = len([r for r in results if r.startswith("✅")])
    total_count = len(results)
    success_rate = (success_count / total_count * 100) if total_count > 0 else 0
    
    print(f"Success Rate: {success_rate:.1f}% ({success_count}/{total_count})")
    print("\nDetailed Results:")
    for result in results:
        print(f"  {result}")
    
    return results, success_rate

if __name__ == "__main__":
    test_render_backend()