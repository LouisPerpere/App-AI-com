#!/usr/bin/env python3
"""
Advanced thumbnail diagnostic tool to identify why some thumbnails fail to generate
"""
import os
import requests
from PIL import Image
import pillow_heif
from thumbs import generate_image_thumb, build_thumb_path
from database import get_database

# Enable HEIC support
pillow_heif.register_heif_opener()

def diagnose_thumbnails():
    """Comprehensive diagnostic of thumbnail issues"""
    print("🔍 DIAGNOSTIC AVANCÉ DES VIGNETTES")
    print("=" * 50)
    
    # Backend URL
    backend_url = 'https://post-validator.preview.emergentagent.com'
    
    # Login
    login_data = {'email': 'lperpere@yahoo.fr', 'password': 'L@Reunion974!'}
    login_response = requests.post(f'{backend_url}/api/auth/login-robust', json=login_data)
    
    if login_response.status_code != 200:
        print("❌ Authentication failed")
        return
        
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Get content from API
    content_response = requests.get(f'{backend_url}/api/content/pending?limit=50', headers=headers)
    if content_response.status_code != 200:
        print("❌ Failed to get content")
        return
        
    files = content_response.json().get('content', [])
    print(f"📊 Found {len(files)} files in API")
    
    # Analyze each file
    working_thumbs = 0
    broken_thumbs = 0
    
    for i, file_data in enumerate(files, 1):
        filename = file_data.get('filename', 'unknown')
        file_type = file_data.get('file_type', 'unknown')
        thumb_url = file_data.get('thumb_url')
        file_id = file_data.get('id')
        
        print(f"\n--- FILE {i}: {filename} ---")
        print(f"   Type: {file_type}")
        print(f"   Thumb URL: {thumb_url}")
        
        # Check if file exists on disk
        file_path = os.path.join('uploads', filename)
        exists_on_disk = os.path.exists(file_path)
        print(f"   Exists on disk: {exists_on_disk}")
        
        if not exists_on_disk:
            print(f"   ❌ ISSUE: File missing from disk")
            broken_thumbs += 1
            continue
            
        # Check file properties
        try:
            file_size = os.path.getsize(file_path)
            print(f"   File size: {file_size} bytes")
            
            # Try to open with PIL/pillow-heif
            try:
                with Image.open(file_path) as img:
                    print(f"   Image format: {img.format}")
                    print(f"   Image mode: {img.mode}")
                    print(f"   Image size: {img.size}")
                    
                    # Check if this has unusual properties
                    if hasattr(img, 'info'):
                        print(f"   Image info: {len(img.info)} properties")
                        
            except Exception as img_error:
                print(f"   ❌ Cannot open image: {img_error}")
                broken_thumbs += 1
                continue
                
            # Check if thumbnail exists
            thumb_path = build_thumb_path(filename)
            thumb_exists = os.path.exists(thumb_path)
            print(f"   Thumbnail exists: {thumb_exists}")
            
            if thumb_exists:
                thumb_size = os.path.getsize(thumb_path)
                print(f"   Thumbnail size: {thumb_size} bytes")
                
                if thumb_size > 0:
                    working_thumbs += 1
                    print(f"   ✅ WORKING THUMBNAIL")
                else:
                    print(f"   ❌ EMPTY THUMBNAIL FILE")
                    broken_thumbs += 1
            else:
                # Try to generate thumbnail now
                print(f"   🔧 Attempting thumbnail generation...")
                try:
                    os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
                    generate_image_thumb(file_path, thumb_path)
                    
                    if os.path.exists(thumb_path) and os.path.getsize(thumb_path) > 0:
                        print(f"   ✅ THUMBNAIL GENERATED SUCCESSFULLY: {os.path.getsize(thumb_path)} bytes")
                        working_thumbs += 1
                        
                        # Update database
                        try:
                            thumb_url_new = f"https://claire-marcus-api.onrender.com/uploads/thumbs/" + os.path.basename(thumb_path)
                            update_response = requests.put(
                                f'{backend_url}/api/content/{file_id}/description',
                                json={'description': file_data.get('description', ''), 'thumb_url': thumb_url_new},
                                headers=headers
                            )
                            if update_response.status_code == 200:
                                print(f"   ✅ DATABASE UPDATED")
                            else:
                                print(f"   ⚠️ Database update failed: {update_response.status_code}")
                        except Exception as update_error:
                            print(f"   ⚠️ Database update error: {update_error}")
                    else:
                        print(f"   ❌ THUMBNAIL GENERATION FAILED")
                        broken_thumbs += 1
                        
                except Exception as gen_error:
                    print(f"   ❌ THUMBNAIL GENERATION ERROR: {gen_error}")
                    broken_thumbs += 1
                    
        except Exception as file_error:
            print(f"   ❌ FILE ERROR: {file_error}")
            broken_thumbs += 1
    
    print(f"\n🎉 DIAGNOSTIC SUMMARY:")
    print(f"   Working thumbnails: {working_thumbs}")
    print(f"   Broken thumbnails: {broken_thumbs}")
    print(f"   Success rate: {working_thumbs / (working_thumbs + broken_thumbs) * 100:.1f}%")

if __name__ == "__main__":
    diagnose_thumbnails()