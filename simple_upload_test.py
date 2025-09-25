#!/usr/bin/env python3
"""
Simple test for batch upload endpoint focusing on the specific issues
"""

import requests
import json
import tempfile
import os

def test_batch_upload():
    base_url = "https://post-validator.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    # Login first
    login_data = {
        "email": "lperpere@yahoo.fr",
        "password": "L@Reunion974!"
    }
    
    print("🔐 Logging in...")
    login_response = requests.post(f"{api_url}/auth/login", json=login_data)
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    access_token = login_response.json().get('access_token')
    headers = {'Authorization': f'Bearer {access_token}'}
    
    print("✅ Login successful")
    
    # Test 1: Valid image upload
    print("\n📸 Testing valid image upload...")
    
    # Create a small PNG file
    png_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
    
    files = {'files': ('test.png', png_content, 'image/png')}
    
    response = requests.post(f"{api_url}/content/batch-upload", files=files, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 2: Invalid file type
    print("\n📄 Testing invalid file type...")
    
    files = {'files': ('test.txt', b'This is a text file', 'text/plain')}
    
    response = requests.post(f"{api_url}/content/batch-upload", files=files, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 3: Large file (simulate)
    print("\n📦 Testing large file...")
    
    # Create a 11MB file
    large_content = b'x' * (11 * 1024 * 1024)
    files = {'files': ('large.png', large_content, 'image/png')}
    
    response = requests.post(f"{api_url}/content/batch-upload", files=files, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    test_batch_upload()