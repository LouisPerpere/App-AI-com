#!/usr/bin/env python3
"""
URL Investigation Test - Detailed analysis of current URLs in MongoDB
"""

import requests
import json

# Configuration
BACKEND_URL = "https://claire-marcus-app-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

def authenticate():
    """Authenticate and get access token"""
    session = requests.Session()
    
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
        
        print(f"✅ Authentication successful: {TEST_EMAIL}, User ID: {user_id}")
        return session, user_id
    else:
        print(f"❌ Authentication failed: {response.status_code}")
        return None, None

def investigate_urls():
    """Investigate all URLs in detail"""
    session, user_id = authenticate()
    if not session:
        return
    
    print("\n🔍 DETAILED URL INVESTIGATION")
    print("=" * 60)
    
    # Get all content
    response = session.get(f"{API_BASE}/content/pending?limit=100")
    
    if response.status_code == 200:
        data = response.json()
        content = data.get("content", [])
        total_files = len(content)
        
        print(f"Total files found: {total_files}")
        print()
        
        # Analyze each file in detail
        url_patterns = {}
        thumb_url_patterns = {}
        
        for i, item in enumerate(content):
            filename = item.get("filename", "unknown")
            url = item.get("url", "")
            thumb_url = item.get("thumb_url", "")
            file_type = item.get("file_type", "")
            
            print(f"File {i+1}: {filename}")
            print(f"  URL: {url}")
            print(f"  Thumb URL: {thumb_url}")
            print(f"  File Type: {file_type}")
            
            # Count URL patterns
            if url:
                domain = url.split('/')[2] if '://' in url else 'no_domain'
                url_patterns[domain] = url_patterns.get(domain, 0) + 1
            else:
                url_patterns['null_url'] = url_patterns.get('null_url', 0) + 1
            
            # Count thumb URL patterns
            if thumb_url:
                domain = thumb_url.split('/')[2] if '://' in thumb_url else 'no_domain'
                thumb_url_patterns[domain] = thumb_url_patterns.get(domain, 0) + 1
            else:
                thumb_url_patterns['null_thumb_url'] = thumb_url_patterns.get('null_thumb_url', 0) + 1
            
            print()
            
            # Show only first 10 files to avoid too much output
            if i >= 9:
                print(f"... (showing first 10 of {total_files} files)")
                break
        
        print("\n📊 URL PATTERN SUMMARY")
        print("-" * 30)
        print("URL patterns:")
        for domain, count in url_patterns.items():
            print(f"  {domain}: {count}")
        
        print("\nThumb URL patterns:")
        for domain, count in thumb_url_patterns.items():
            print(f"  {domain}: {count}")
        
        # Check for specific domains mentioned in the French review
        print("\n🎯 FRENCH REVIEW ANALYSIS")
        print("-" * 30)
        
        claire_marcus_com_count = sum(1 for item in content if "claire-marcus.com" in str(item.get("thumb_url", "")))
        claire_marcus_api_count = sum(1 for item in content if "claire-marcus-api.onrender.com" in str(item.get("thumb_url", "")))
        libfusion_count = sum(1 for item in content if "libfusion.preview.emergentagent.com" in str(item.get("thumb_url", "")))
        
        print(f"Files with claire-marcus.com URLs: {claire_marcus_com_count}")
        print(f"Files with claire-marcus-api.onrender.com URLs: {claire_marcus_api_count}")
        print(f"Files with libfusion.preview.emergentagent.com URLs: {libfusion_count}")
        
        # Test a sample URL for accessibility
        print("\n🌐 URL ACCESSIBILITY TEST")
        print("-" * 30)
        
        sample_urls = []
        for item in content[:5]:  # Test first 5 files
            thumb_url = item.get("thumb_url")
            if thumb_url and thumb_url != "":
                sample_urls.append((item.get("filename", "unknown"), thumb_url))
        
        for filename, url in sample_urls:
            try:
                response = requests.get(url, timeout=10)
                content_type = response.headers.get('content-type', '')
                print(f"✅ {filename}: {response.status_code} - {content_type} - {url}")
            except Exception as e:
                print(f"❌ {filename}: Error - {str(e)[:50]} - {url}")
    
    else:
        print(f"❌ Failed to get content: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    investigate_urls()