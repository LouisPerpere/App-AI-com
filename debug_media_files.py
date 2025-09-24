#!/usr/bin/env python3
"""
Debug script to check media files in database vs disk
"""

import os
import requests
from database import get_database

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://instamanager-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"
UPLOADS_DIR = "/app/backend/uploads"

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
        return response.json().get('access_token')
    return None

def check_files():
    """Check files in database vs disk"""
    print("🔍 Checking media files in database vs disk...")
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("❌ Failed to get auth token")
        return
    
    # Get files from API
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{API_BASE}/content/pending?limit=100&offset=0", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get content: {response.status_code}")
        return
    
    content_data = response.json()
    content_items = content_data.get('content', [])
    
    print(f"📋 Found {len(content_items)} items in database")
    
    # Check disk files
    disk_files = set()
    if os.path.exists(UPLOADS_DIR):
        disk_files = set(os.listdir(UPLOADS_DIR))
        disk_files.discard('thumbs')  # Remove thumbs directory
    
    print(f"💾 Found {len(disk_files)} files on disk")
    
    # Check each database item
    available_images = []
    for item in content_items:
        filename = item.get('filename', '')
        file_type = item.get('file_type', '')
        file_id = item.get('id', '')
        
        on_disk = filename in disk_files
        is_image = file_type.startswith('image/')
        
        status = "✅" if on_disk else "❌"
        type_icon = "🖼️" if is_image else "📄"
        
        print(f"{status} {type_icon} {filename} (ID: {file_id}, Type: {file_type})")
        
        if on_disk and is_image:
            available_images.append({
                'id': file_id,
                'filename': filename,
                'file_type': file_type
            })
    
    print(f"\n🎯 Available images for testing: {len(available_images)}")
    for img in available_images[:3]:  # Show first 3
        print(f"   - {img['filename']} (ID: {img['id']})")
    
    return available_images

if __name__ == "__main__":
    check_files()