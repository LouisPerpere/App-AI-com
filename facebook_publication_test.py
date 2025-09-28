#!/usr/bin/env python3
"""
Facebook Publication Test - Testing the actual publication endpoints mentioned by user
Testing both text-only and text+image publication to identify the specific image issue

Credentials: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://social-publisher-10.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

def authenticate():
    """Authenticate and get JWT token"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login-robust",
            json=TEST_CREDENTIALS,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token"), data.get("user_id")
        else:
            print(f"❌ Authentication failed: {response.status_code} - {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None, None

def test_facebook_publication_endpoints():
    """Test various Facebook publication endpoints"""
    
    print("🎯 FACEBOOK PUBLICATION ENDPOINT TESTING")
    print("=" * 60)
    
    # Authenticate
    token, user_id = authenticate()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"✅ Authenticated as user: {user_id}")
    print()
    
    # Test 1: Check if there are any posts available for publication
    print("📋 Test 1: Check available posts for publication")
    try:
        response = requests.get(f"{BASE_URL}/posts/generated", headers=headers, timeout=30)
        if response.status_code == 200:
            posts = response.json().get("posts", [])
            print(f"   Found {len(posts)} generated posts")
            
            # Look for Facebook posts
            facebook_posts = [p for p in posts if p.get("platform", "").lower() == "facebook"]
            print(f"   Found {len(facebook_posts)} Facebook posts")
            
            if facebook_posts:
                sample_post = facebook_posts[0]
                print(f"   Sample Facebook post ID: {sample_post.get('id')}")
                print(f"   Sample post has image: {bool(sample_post.get('visual_url'))}")
                print(f"   Sample post image URL: {sample_post.get('visual_url', 'None')}")
        else:
            print(f"   ❌ Could not fetch posts: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error fetching posts: {e}")
    
    print()
    
    # Test 2: Test the main publication endpoint mentioned by user
    print("📤 Test 2: Test main publication endpoint (POST /api/posts/publish)")
    
    # First, let's see if we can find a post to publish
    try:
        response = requests.get(f"{BASE_URL}/posts/generated", headers=headers, timeout=30)
        if response.status_code == 200:
            posts = response.json().get("posts", [])
            facebook_posts = [p for p in posts if p.get("platform", "").lower() == "facebook"]
            
            if facebook_posts:
                test_post_id = facebook_posts[0].get("id")
                print(f"   Testing with post ID: {test_post_id}")
                
                # Test publication
                pub_response = requests.post(
                    f"{BASE_URL}/posts/publish",
                    json={"post_id": test_post_id},
                    headers=headers,
                    timeout=30
                )
                
                print(f"   Publication response status: {pub_response.status_code}")
                print(f"   Publication response: {pub_response.text}")
                
            else:
                print("   ⚠️ No Facebook posts available for testing")
        else:
            print(f"   ❌ Could not fetch posts for publication test: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing publication: {e}")
    
    print()
    
    # Test 3: Test the simple publication endpoints we found in diagnostic
    print("📤 Test 3: Test simple publication endpoints")
    
    # Test with text only
    print("   3a. Text-only publication:")
    try:
        text_only_data = {"text": "Test publication texte seulement"}
        response = requests.post(
            f"{BASE_URL}/social/facebook/publish-simple",
            json=text_only_data,
            headers=headers,
            timeout=30
        )
        print(f"      Status: {response.status_code}")
        print(f"      Response: {response.text}")
    except Exception as e:
        print(f"      ❌ Error: {e}")
    
    print()
    
    # Test with text + public image
    print("   3b. Text + Public Image publication:")
    try:
        text_image_data = {
            "text": "Test publication avec image publique",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png"
        }
        response = requests.post(
            f"{BASE_URL}/social/facebook/publish-simple",
            json=text_image_data,
            headers=headers,
            timeout=30
        )
        print(f"      Status: {response.status_code}")
        print(f"      Response: {response.text}")
    except Exception as e:
        print(f"      ❌ Error: {e}")
    
    print()
    
    # Test with text + app image (protected URL)
    print("   3c. Text + App Image publication:")
    try:
        # Get a sample app image URL
        content_response = requests.get(f"{BASE_URL}/content/pending?limit=1", headers=headers, timeout=30)
        if content_response.status_code == 200:
            content_items = content_response.json().get("content", [])
            if content_items:
                app_image_url = content_items[0].get("url", "")
                if app_image_url.startswith("/api/"):
                    app_image_url = f"https://social-publisher-10.preview.emergentagent.com{app_image_url}"
                
                text_app_image_data = {
                    "text": "Test publication avec image de l'app",
                    "image_url": app_image_url
                }
                
                print(f"      Using app image: {app_image_url}")
                
                response = requests.post(
                    f"{BASE_URL}/social/facebook/publish-simple",
                    json=text_app_image_data,
                    headers=headers,
                    timeout=30
                )
                print(f"      Status: {response.status_code}")
                print(f"      Response: {response.text}")
            else:
                print("      ⚠️ No app images available for testing")
        else:
            print(f"      ❌ Could not fetch app content: {content_response.status_code}")
    except Exception as e:
        print(f"      ❌ Error: {e}")
    
    print()
    
    # Test 4: Check backend logs for more details
    print("📋 Test 4: Check backend service logs")
    try:
        import subprocess
        result = subprocess.run(
            ["tail", "-n", "50", "/var/log/supervisor/backend.err.log"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("   Recent backend error logs:")
            print("   " + "\n   ".join(result.stdout.split("\n")[-10:]))  # Last 10 lines
        else:
            print("   ⚠️ Could not read backend logs")
    except Exception as e:
        print(f"   ❌ Error reading logs: {e}")
    
    return True

if __name__ == "__main__":
    test_facebook_publication_endpoints()