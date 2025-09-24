#!/usr/bin/env python3
"""
Test upload functionality only
"""

import requests
import json

# Configuration
BACKEND_URL = "https://instamanager-1.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

def test_upload():
    session = requests.Session()
    
    # Authenticate
    auth_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
    response = session.post(f"{BACKEND_URL}/auth/login-robust", json=auth_data)
    
    if response.status_code != 200:
        print(f"❌ Auth failed: {response.status_code}")
        return
    
    data = response.json()
    token = data.get("access_token")
    session.headers.update({"Authorization": f"Bearer {token}"})
    
    print("✅ Authenticated")
    
    # Test upload
    test_image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
    
    # Remove Content-Type header for multipart
    headers = session.headers.copy()
    if 'Content-Type' in headers:
        del headers['Content-Type']
    
    files = {'files': ('test.png', test_image_content, 'image/png')}
    data = {'upload_type': 'single', 'attributed_month': 'decembre_2025'}
    
    response = session.post(
        f"{BACKEND_URL}/content/batch-upload",
        files=files,
        data=data,
        headers=headers
    )
    
    print(f"📊 Upload Status: {response.status_code}")
    print(f"📊 Upload Response: {response.text}")

if __name__ == "__main__":
    test_upload()