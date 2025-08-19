#!/usr/bin/env python3
"""
Render Backend Verification Test
Following the specific review request flow to verify Render deployment
"""

import requests
import json
import io
from PIL import Image
import time

# Configuration
RENDER_BASE_URL = "https://claire-marcus-api.onrender.com"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr", 
    "password": "L@Reunion974!"
}

def create_test_png(size=(100, 100), color=(255, 0, 0)):
    """Create a small test PNG image"""
    img = Image.new('RGB', size, color)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def test_render_verification():
    """Test the specific review request flow"""
    print("🎯 RENDER BACKEND VERIFICATION TEST")
    print("=" * 60)
    
    results = []
    token = None
    
    # Step 1: Health Check
    print("\n1️⃣ Testing GET /api/health")
    try:
        response = requests.get(f"{RENDER_BASE_URL}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check successful: {data.get('status', 'unknown')}")
            print(f"   Service: {data.get('service', 'unknown')}")
            results.append("✅ Step 1: Health check working")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            results.append(f"❌ Step 1: Health check failed ({response.status_code})")
    except Exception as e:
        print(f"❌ Health check error: {e}")
        results.append(f"❌ Step 1: Health check error - {e}")
    
    # Step 2: Authentication
    print("\n2️⃣ Testing POST /api/auth/login-robust")
    try:
        response = requests.post(
            f"{RENDER_BASE_URL}/api/auth/login-robust",
            json=TEST_CREDENTIALS,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            user_id = data.get('user_id')
            print(f"✅ Authentication successful")
            print(f"   User ID: {user_id}")
            print(f"   Token: {token[:20]}..." if token else "No token")
            results.append("✅ Step 2: Authentication working")
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            results.append(f"❌ Step 2: Authentication failed ({response.status_code})")
            return results
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        results.append(f"❌ Step 2: Authentication error - {e}")
        return results
    
    if not token:
        print("❌ No token obtained, cannot continue")
        results.append("❌ Cannot continue without token")
        return results
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 3: CRITICAL TEST - Batch Upload
    print("\n3️⃣ Testing POST /api/content/batch-upload (CRITICAL)")
    try:
        # Create two small test PNG files
        png1 = create_test_png((50, 50), (255, 0, 0))  # Red
        png2 = create_test_png((50, 50), (0, 255, 0))  # Green
        
        files = [
            ('files', ('test1.png', png1, 'image/png')),
            ('files', ('test2.png', png2, 'image/png'))
        ]
        
        response = requests.post(
            f"{RENDER_BASE_URL}/api/content/batch-upload",
            files=files,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Batch upload successful!")
            print(f"   Created items: {len(data.get('uploaded', []))}")
            results.append("✅ Step 3: Batch upload working - Render has latest code!")
            uploaded_ids = [item.get('id') for item in data.get('uploaded', [])]
        elif response.status_code == 404:
            print(f"❌ Batch upload endpoint missing (404)")
            print(f"   This means Render hasn't deployed the routes_uploads.py router")
            results.append("❌ Step 3: Batch upload endpoint missing (404) - Render deployment incomplete")
            return results + ["🚨 CONCLUSION: Render hasn't deployed the new router yet - trigger manual deploy"]
        else:
            print(f"❌ Batch upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            results.append(f"❌ Step 3: Batch upload failed ({response.status_code})")
            return results
    except Exception as e:
        print(f"❌ Batch upload error: {e}")
        results.append(f"❌ Step 3: Batch upload error - {e}")
        return results
    
    # Step 4: Check Pending Content
    print("\n4️⃣ Testing GET /api/content/pending")
    try:
        response = requests.get(
            f"{RENDER_BASE_URL}/api/content/pending",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            total_items = data.get('total', 0)
            content_items = data.get('content', [])
            print(f"✅ Pending content retrieved")
            print(f"   Total items: {total_items}")
            print(f"   Items in response: {len(content_items)}")
            results.append(f"✅ Step 4: Pending content working ({total_items} items)")
            
            # Get some IDs for thumbnail/file testing
            test_ids = [item.get('id') for item in content_items[:2] if item.get('id')]
        else:
            print(f"❌ Pending content failed: {response.status_code}")
            results.append(f"❌ Step 4: Pending content failed ({response.status_code})")
            test_ids = []
    except Exception as e:
        print(f"❌ Pending content error: {e}")
        results.append(f"❌ Step 4: Pending content error - {e}")
        test_ids = []
    
    # Step 5: Test Thumbnail Access
    print("\n5️⃣ Testing GET /api/content/{id}/thumb")
    if test_ids:
        test_id = test_ids[0]
        try:
            response = requests.get(
                f"{RENDER_BASE_URL}/api/content/{test_id}/thumb",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                print(f"✅ Thumbnail access successful")
                print(f"   Content-Type: {content_type}")
                print(f"   Size: {len(response.content)} bytes")
                results.append("✅ Step 5: Thumbnail access working")
            elif response.status_code == 404:
                print(f"⚠️ Thumbnail not found (404) - expected for missing thumbnails")
                results.append("⚠️ Step 5: Thumbnail not found (expected)")
            else:
                print(f"❌ Thumbnail access failed: {response.status_code}")
                results.append(f"❌ Step 5: Thumbnail access failed ({response.status_code})")
        except Exception as e:
            print(f"❌ Thumbnail access error: {e}")
            results.append(f"❌ Step 5: Thumbnail access error - {e}")
    else:
        print("⚠️ No test IDs available for thumbnail testing")
        results.append("⚠️ Step 5: No test IDs for thumbnail testing")
    
    # Step 6: Test File Access
    print("\n6️⃣ Testing GET /api/content/{id}/file")
    if test_ids:
        test_id = test_ids[0]
        try:
            response = requests.get(
                f"{RENDER_BASE_URL}/api/content/{test_id}/file",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                print(f"✅ File access successful")
                print(f"   Content-Type: {content_type}")
                print(f"   Size: {len(response.content)} bytes")
                results.append("✅ Step 6: File access working")
            elif response.status_code == 404:
                print(f"⚠️ File not found (404) - expected for missing files")
                results.append("⚠️ Step 6: File not found (expected)")
            else:
                print(f"❌ File access failed: {response.status_code}")
                results.append(f"❌ Step 6: File access failed ({response.status_code})")
        except Exception as e:
            print(f"❌ File access error: {e}")
            results.append(f"❌ Step 6: File access error - {e}")
    else:
        print("⚠️ No test IDs available for file testing")
        results.append("⚠️ Step 6: No test IDs for file testing")
    
    # Step 7: Test Thumbnails Status
    print("\n7️⃣ Testing GET /api/content/thumbnails/status")
    try:
        response = requests.get(
            f"{RENDER_BASE_URL}/api/content/thumbnails/status",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            total_files = data.get('total_files', 0)
            with_thumbnails = data.get('with_thumbnails', 0)
            completion = data.get('completion_percentage', 0)
            print(f"✅ Thumbnails status retrieved")
            print(f"   Total files: {total_files}")
            print(f"   With thumbnails: {with_thumbnails}")
            print(f"   Completion: {completion}%")
            results.append(f"✅ Step 7: Thumbnails status working ({total_files} files, {completion}% complete)")
        else:
            print(f"❌ Thumbnails status failed: {response.status_code}")
            results.append(f"❌ Step 7: Thumbnails status failed ({response.status_code})")
    except Exception as e:
        print(f"❌ Thumbnails status error: {e}")
        results.append(f"❌ Step 7: Thumbnails status error - {e}")
    
    return results

if __name__ == "__main__":
    results = test_render_verification()
    
    print("\n" + "=" * 60)
    print("📊 RENDER VERIFICATION SUMMARY")
    print("=" * 60)
    
    for result in results:
        print(result)
    
    # Count success/failure
    success_count = len([r for r in results if r.startswith("✅")])
    total_count = len([r for r in results if r.startswith(("✅", "❌"))])
    
    print(f"\n📈 SUCCESS RATE: {success_count}/{total_count} tests passed")
    
    if any("Render deployment incomplete" in r for r in results):
        print("\n🚨 CRITICAL FINDING:")
        print("   The batch upload endpoint is missing (404)")
        print("   This indicates Render hasn't deployed the routes_uploads.py router")
        print("   NEXT STEPS:")
        print("   1. Go to Render dashboard")
        print("   2. Find the Claire Marcus API service")
        print("   3. Trigger a manual deploy")
        print("   4. Wait for deployment to complete")
        print("   5. Re-run this test")