#!/usr/bin/env python3
"""
Debug thumbnail generation to understand why 80px thumbnails aren't being created
"""

import requests
import json
import base64
import os
from PIL import Image
import io

def debug_thumbnail_generation():
    """Debug the thumbnail generation process"""
    
    # Authenticate
    login_data = {
        "email": "lperpere@yahoo.fr", 
        "password": "L@Reunion974!"
    }
    
    print("🔐 Authenticating...")
    response = requests.post("https://claire-marcus-app-1.preview.emergentagent.com/api/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Authentication failed: {response.status_code}")
        return
    
    access_token = response.json().get('access_token')
    headers = {'Authorization': f'Bearer {access_token}'}
    
    print("📄 Getting content with thumbnails...")
    response = requests.get(
        "https://claire-marcus-app-1.preview.emergentagent.com/api/content/pending",
        params={'limit': 3},
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to get content: {response.status_code}")
        return
    
    data = response.json()
    content_items = data.get('content', [])
    
    print(f"📊 Analyzing {len(content_items)} items...")
    
    for i, item in enumerate(content_items):
        if item.get('file_type', '').startswith('image/'):
            filename = item.get('filename', f'item_{i}')
            print(f"\n🖼️  Analyzing {filename}:")
            
            # Check thumbnail data
            thumbnail_data = item.get('thumbnail_data')
            file_data = item.get('file_data')
            
            if thumbnail_data:
                try:
                    # Decode thumbnail
                    thumbnail_bytes = base64.b64decode(thumbnail_data)
                    thumbnail_image = Image.open(io.BytesIO(thumbnail_bytes))
                    
                    width, height = thumbnail_image.size
                    file_size = len(thumbnail_bytes)
                    
                    print(f"   📏 Thumbnail dimensions: {width}x{height}")
                    print(f"   📦 Thumbnail size: {file_size/1024:.1f}KB")
                    print(f"   🎨 Image mode: {thumbnail_image.mode}")
                    print(f"   📊 Base64 length: {len(thumbnail_data)}")
                    
                    # Check if it's actually a thumbnail or full image
                    if file_data:
                        full_bytes = base64.b64decode(file_data)
                        full_image = Image.open(io.BytesIO(full_bytes))
                        full_width, full_height = full_image.size
                        
                        print(f"   📏 Full image dimensions: {full_width}x{full_height}")
                        print(f"   📦 Full image size: {len(full_bytes)/1024:.1f}KB")
                        
                        # Check if thumbnail is actually different from full image
                        if len(thumbnail_bytes) == len(full_bytes):
                            print("   ⚠️  WARNING: Thumbnail and full image are identical!")
                            print("   ⚠️  This suggests thumbnail generation failed and fell back to full image")
                        else:
                            reduction = ((len(full_bytes) - len(thumbnail_bytes)) / len(full_bytes)) * 100
                            print(f"   ✅ Size reduction: {reduction:.1f}%")
                    
                    # Test if dimensions are within 80px constraint
                    max_dimension = max(width, height)
                    if max_dimension <= 80:
                        print(f"   ✅ Dimensions within 80px constraint")
                    else:
                        print(f"   ❌ Dimensions exceed 80px constraint (max: {max_dimension}px)")
                        
                        # Try to understand why
                        if width == height:
                            print(f"   🔍 Square image - should be exactly 80x80")
                        else:
                            aspect_ratio = width / height
                            if width > height:
                                expected_width = 80
                                expected_height = int(80 / aspect_ratio)
                                print(f"   🔍 Landscape image - expected: {expected_width}x{expected_height}")
                            else:
                                expected_height = 80
                                expected_width = int(80 * aspect_ratio)
                                print(f"   🔍 Portrait image - expected: {expected_width}x{expected_height}")
                    
                except Exception as e:
                    print(f"   ❌ Error analyzing thumbnail: {e}")
            else:
                print(f"   ❌ No thumbnail data found")
    
    print(f"\n🔍 DIAGNOSIS:")
    print(f"   If thumbnails are identical to full images, the thumbnail generation is failing")
    print(f"   If thumbnails are larger than 80px, there might be an issue with the thumbnail() method")
    print(f"   Check backend logs for thumbnail generation errors")

if __name__ == "__main__":
    debug_thumbnail_generation()