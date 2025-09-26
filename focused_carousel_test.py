#!/usr/bin/env python3
"""
Focused Carousel Test - Only test new carousel functionality
Test only the newly uploaded carousel items to verify the fix
"""

import requests
import json
import io
from PIL import Image

# Configuration
BACKEND_URL = "https://social-ai-planner-2.preview.emergentagent.com/api"
EMAIL = "lperpere@yahoo.fr"
PASSWORD = "L@Reunion974!"

def test_new_carousel_only():
    """Test only the new carousel functionality"""
    print("🎠 FOCUSED CAROUSEL TEST - NEW ITEMS ONLY")
    print("=" * 50)
    
    session = requests.Session()
    
    # Step 1: Authenticate
    print("🔑 Step 1: Authentication")
    login_data = {"email": EMAIL, "password": PASSWORD}
    response = session.post(f"{BACKEND_URL}/auth/login-robust", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Authentication failed: {response.text}")
        return False
    
    data = response.json()
    token = data.get("access_token")
    session.headers.update({"Authorization": f"Bearer {token}"})
    print(f"✅ Authentication successful")
    
    # Step 2: Create and upload new carousel
    print("\n📤 Step 2: Upload new carousel with all parameters")
    
    # Create test images
    test_images = []
    for i in range(2):
        img = Image.new('RGB', (400, 300), color=(200, 100 + i*50, 150))
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG', quality=85)
        img_bytes.seek(0)
        test_images.append(('files', (f'focused_test_{i+1}.jpg', img_bytes, 'image/jpeg')))
    
    # Upload with all carousel parameters
    carousel_params = {
        'attributed_month': 'octobre_2025',
        'upload_type': 'carousel',
        'common_title': 'Test Carrousel',
        'common_context': 'Description carrousel'
    }
    
    response = session.post(f"{BACKEND_URL}/content/batch-upload", files=test_images, data=carousel_params)
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.text}")
        return False
    
    upload_data = response.json()
    carousel_ids = [item['id'] for item in upload_data.get('created', [])]
    print(f"✅ Uploaded {len(carousel_ids)} carousel items")
    
    # Step 3: Verify the new items have all correct fields
    print("\n📋 Step 3: Verify new carousel items")
    
    response = session.get(f"{BACKEND_URL}/content/pending")
    if response.status_code != 200:
        print(f"❌ Failed to get content: {response.text}")
        return False
    
    content_data = response.json()
    content_items = content_data.get('content', [])
    
    # Find our newly uploaded items
    new_carousel_items = []
    for item in content_items:
        if item.get('id') in carousel_ids:
            new_carousel_items.append(item)
    
    print(f"Found {len(new_carousel_items)} new carousel items")
    
    # Verify all fields are correct
    all_correct = True
    carousel_id_set = set()
    
    for i, item in enumerate(new_carousel_items):
        print(f"\nItem {i+1}:")
        print(f"  Title: '{item.get('title')}' (expected: 'Test Carrousel')")
        print(f"  Context: '{item.get('context')}' (expected: 'Description carrousel')")
        print(f"  Month: '{item.get('attributed_month')}' (expected: 'octobre_2025')")
        print(f"  Upload Type: '{item.get('upload_type')}' (expected: 'carousel')")
        print(f"  Carousel ID: '{item.get('carousel_id')}'")
        print(f"  Common Title: '{item.get('common_title')}'")
        
        # Check each field
        if item.get('title') != 'Test Carrousel':
            print(f"  ❌ Title mismatch")
            all_correct = False
        if item.get('context') != 'Description carrousel':
            print(f"  ❌ Context mismatch")
            all_correct = False
        if item.get('attributed_month') != 'octobre_2025':
            print(f"  ❌ Month mismatch")
            all_correct = False
        if item.get('upload_type') != 'carousel':
            print(f"  ❌ Upload type mismatch")
            all_correct = False
        if not item.get('carousel_id'):
            print(f"  ❌ Missing carousel_id")
            all_correct = False
        else:
            carousel_id_set.add(item.get('carousel_id'))
        
        if all_correct:
            print(f"  ✅ All fields correct")
    
    # Check that all items have the same carousel_id
    if len(carousel_id_set) == 1:
        print(f"\n✅ All items have the same carousel_id: {list(carousel_id_set)[0]}")
    else:
        print(f"\n❌ Items have different carousel_ids: {carousel_id_set}")
        all_correct = False
    
    # Step 4: Cleanup
    print(f"\n🧹 Step 4: Cleanup test items")
    for item_id in carousel_ids:
        response = session.delete(f"{BACKEND_URL}/content/{item_id}")
        if response.status_code == 200:
            print(f"✅ Deleted {item_id}")
        else:
            print(f"❌ Failed to delete {item_id}")
    
    # Final result
    print(f"\n🎯 FOCUSED TEST RESULT")
    if all_correct:
        print("✅ NEW CAROUSEL FUNCTIONALITY IS WORKING PERFECTLY")
        print("All required fields are correctly implemented:")
        print("  - common_title parameter sets title for all carousel items")
        print("  - common_context parameter sets context for all carousel items")
        print("  - attributed_month parameter is properly stored")
        print("  - carousel_id groups all items in the same batch")
        print("  - upload_type='carousel' is correctly set")
        return True
    else:
        print("❌ NEW CAROUSEL FUNCTIONALITY HAS ISSUES")
        return False

if __name__ == "__main__":
    success = test_new_carousel_only()
    exit(0 if success else 1)