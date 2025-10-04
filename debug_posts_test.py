#!/usr/bin/env python3
"""
Debug test to understand why fallback photos are still being used
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://claire-marcus-app-1.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

def authenticate():
    """Authenticate and get token"""
    response = requests.post(
        f"{BASE_URL}/auth/login-robust",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token"), data.get("user_id")
    return None, None

def get_headers(token):
    """Get authenticated headers"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def main():
    print("🔍 DEBUG: Investigating fallback photo issue")
    
    # Authenticate
    token, user_id = authenticate()
    if not token:
        print("❌ Authentication failed")
        return
    
    print(f"✅ Authenticated as user: {user_id}")
    
    # Get generated posts and analyze them
    response = requests.get(
        f"{BASE_URL}/posts/generated",
        headers=get_headers(token)
    )
    
    if response.status_code == 200:
        data = response.json()
        posts = data.get("posts", [])
        
        print(f"📋 Found {len(posts)} generated posts")
        
        # Analyze posts with fallback IDs
        fallback_posts = []
        real_photo_posts = []
        empty_visual_posts = []
        
        for post in posts:
            visual_id = post.get("visual_id", "")
            
            if visual_id.startswith("global_fallback_"):
                fallback_posts.append(post)
            elif visual_id and not visual_id.startswith("global_fallback_"):
                real_photo_posts.append(post)
            else:
                empty_visual_posts.append(post)
        
        print(f"📊 Analysis:")
        print(f"   Posts with fallback IDs: {len(fallback_posts)}")
        print(f"   Posts with real photo IDs: {len(real_photo_posts)}")
        print(f"   Posts with empty visual IDs: {len(empty_visual_posts)}")
        
        # Show examples of each type
        if fallback_posts:
            print(f"\n❌ FALLBACK POSTS (first 3):")
            for i, post in enumerate(fallback_posts[:3]):
                print(f"   {i+1}. Title: {post.get('title', '')}")
                print(f"      Visual ID: {post.get('visual_id', '')}")
                print(f"      Visual URL: {post.get('visual_url', '')}")
                print(f"      Created: {post.get('created_at', '')}")
        
        if real_photo_posts:
            print(f"\n✅ REAL PHOTO POSTS (first 3):")
            for i, post in enumerate(real_photo_posts[:3]):
                print(f"   {i+1}. Title: {post.get('title', '')}")
                print(f"      Visual ID: {post.get('visual_id', '')}")
                print(f"      Visual URL: {post.get('visual_url', '')}")
        
        if empty_visual_posts:
            print(f"\n⚠️ EMPTY VISUAL POSTS (first 3):")
            for i, post in enumerate(empty_visual_posts[:3]):
                print(f"   {i+1}. Title: {post.get('title', '')}")
                print(f"      Visual ID: '{post.get('visual_id', '')}'")
                print(f"      Visual URL: '{post.get('visual_url', '')}'")
        
        # Check if these are old posts or new posts
        if fallback_posts:
            print(f"\n🕐 FALLBACK POSTS TIMESTAMPS:")
            for post in fallback_posts[:5]:
                created_at = post.get('created_at', '')
                title = post.get('title', '')[:30]
                print(f"   {created_at}: {title}")
    
    else:
        print(f"❌ Failed to get posts: {response.status_code}")

if __name__ == "__main__":
    main()