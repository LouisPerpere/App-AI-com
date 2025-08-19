#!/usr/bin/env python3
"""
Detailed Render Backend Test - Focus on batch upload verification
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

def create_test_png(size=(100, 100), color=(255, 0, 0), name="test"):
    """Create a small test PNG image with specific properties"""
    img = Image.new('RGB', size, color)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG', optimize=True)
    img_bytes.seek(0)
    return img_bytes

def test_detailed_batch_upload():
    """Detailed test of batch upload functionality"""
    print("🔍 DETAILED RENDER BATCH UPLOAD TEST")
    print("=" * 60)
    
    # Step 1: Get authentication token
    print("\n🔑 Getting authentication token...")
    try:
        response = requests.post(
            f"{RENDER_BASE_URL}/api/auth/login-robust",
            json=TEST_CREDENTIALS,
            timeout=15
        )
        if response.status_code != 200:
            print(f"❌ Authentication failed: {response.status_code}")
            return
        
        data = response.json()
        token = data.get('access_token')
        user_id = data.get('user_id')
        print(f"✅ Authentication successful - User ID: {user_id}")
        
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Check current content count
    print("\n📊 Checking current content count...")
    try:
        response = requests.get(
            f"{RENDER_BASE_URL}/api/content/pending",
            headers=headers,
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            initial_count = data.get('total', 0)
            print(f"✅ Current content count: {initial_count}")
        else:
            print(f"❌ Failed to get content count: {response.status_code}")
            initial_count = 0
    except Exception as e:
        print(f"❌ Content count error: {e}")
        initial_count = 0
    
    # Step 3: Create and upload test files
    print("\n📤 Testing batch upload with 2 PNG files...")
    try:
        # Create two distinct test images
        png1 = create_test_png((80, 80), (255, 100, 100), "red_test")  # Light red
        png2 = create_test_png((80, 80), (100, 255, 100), "green_test")  # Light green
        
        files = [
            ('files', ('render_test_red.png', png1, 'image/png')),
            ('files', ('render_test_green.png', png2, 'image/png'))
        ]
        
        print("   Uploading files: render_test_red.png, render_test_green.png")
        
        response = requests.post(
            f"{RENDER_BASE_URL}/api/content/batch-upload",
            files=files,
            headers=headers,
            timeout=30
        )
        
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Batch upload successful!")
            print(f"   Response keys: {list(data.keys())}")
            
            uploaded = data.get('uploaded', [])
            failed = data.get('failed', [])
            
            print(f"   Uploaded count: {len(uploaded)}")
            print(f"   Failed count: {len(failed)}")
            
            if uploaded:
                print("   Uploaded items:")
                for i, item in enumerate(uploaded):
                    print(f"     {i+1}. ID: {item.get('id', 'N/A')}")
                    print(f"        Filename: {item.get('filename', 'N/A')}")
                    print(f"        Type: {item.get('file_type', 'N/A')}")
                    print(f"        URL: {item.get('url', 'N/A')}")
            
            if failed:
                print("   Failed items:")
                for i, item in enumerate(failed):
                    print(f"     {i+1}. Filename: {item.get('filename', 'N/A')}")
                    print(f"        Error: {item.get('error', 'N/A')}")
            
            uploaded_ids = [item.get('id') for item in uploaded if item.get('id')]
            
        else:
            print(f"❌ Batch upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Batch upload error: {e}")
        return
    
    # Step 4: Verify content count increased
    print("\n🔍 Verifying content count after upload...")
    try:
        time.sleep(2)  # Give a moment for processing
        response = requests.get(
            f"{RENDER_BASE_URL}/api/content/pending",
            headers=headers,
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            final_count = data.get('total', 0)
            increase = final_count - initial_count
            print(f"✅ Final content count: {final_count}")
            print(f"   Increase: +{increase}")
            
            # Show recent items
            content_items = data.get('content', [])
            if content_items:
                print("   Recent items:")
                for i, item in enumerate(content_items[:3]):
                    print(f"     {i+1}. {item.get('filename', 'N/A')} ({item.get('id', 'N/A')})")
        else:
            print(f"❌ Failed to verify content count: {response.status_code}")
    except Exception as e:
        print(f"❌ Content verification error: {e}")
    
    # Step 5: Test thumbnail and file access for uploaded items
    if uploaded_ids:
        print(f"\n🖼️ Testing thumbnail/file access for uploaded items...")
        for i, item_id in enumerate(uploaded_ids[:2]):  # Test first 2
            print(f"\n   Testing item {i+1}: {item_id}")
            
            # Test thumbnail
            try:
                response = requests.get(
                    f"{RENDER_BASE_URL}/api/content/{item_id}/thumb",
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    size = len(response.content)
                    print(f"     ✅ Thumbnail: {content_type}, {size} bytes")
                else:
                    print(f"     ⚠️ Thumbnail: {response.status_code} (may not be generated yet)")
            except Exception as e:
                print(f"     ❌ Thumbnail error: {e}")
            
            # Test file access
            try:
                response = requests.get(
                    f"{RENDER_BASE_URL}/api/content/{item_id}/file",
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    size = len(response.content)
                    print(f"     ✅ File: {content_type}, {size} bytes")
                else:
                    print(f"     ❌ File: {response.status_code}")
            except Exception as e:
                print(f"     ❌ File error: {e}")
    
    # Step 6: Final thumbnails status
    print(f"\n📈 Final thumbnails status...")
    try:
        response = requests.get(
            f"{RENDER_BASE_URL}/api/content/thumbnails/status",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Total files: {data.get('total_files', 0)}")
            print(f"   With thumbnails: {data.get('with_thumbnails', 0)}")
            print(f"   Missing thumbnails: {data.get('missing_thumbnails', 0)}")
            print(f"   Completion: {data.get('completion_percentage', 0)}%")
        else:
            print(f"❌ Thumbnails status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Thumbnails status error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 DETAILED BATCH UPLOAD TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_detailed_batch_upload()