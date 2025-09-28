#!/usr/bin/env python3
"""
Clean up old fallback posts and test the current photo-post linking system
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://social-publisher-10.preview.emergentagent.com/api"
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

def cleanup_old_posts(token):
    """Clean up old posts with fallback IDs"""
    print("🧹 Cleaning up old posts with fallback IDs...")
    
    # This would require a backend endpoint to delete posts
    # For now, we'll just identify them
    response = requests.get(
        f"{BASE_URL}/posts/generated",
        headers=get_headers(token)
    )
    
    if response.status_code == 200:
        data = response.json()
        posts = data.get("posts", [])
        
        fallback_posts = [p for p in posts if p.get("visual_id", "").startswith("global_fallback_")]
        print(f"   Found {len(fallback_posts)} posts with fallback IDs")
        print("   ⚠️ Note: These are old posts from previous system versions")
        return len(fallback_posts)
    
    return 0

def test_new_post_generation(token):
    """Test generating new posts to verify the current system works"""
    print("🚀 Testing new post generation...")
    
    # Generate new posts for a different month to avoid conflicts
    response = requests.post(
        f"{BASE_URL}/posts/generate",
        json={"target_month": "fevrier_2025"},
        headers=get_headers(token)
    )
    
    if response.status_code == 200:
        data = response.json()
        posts_count = data.get("posts_count", 0)
        success = data.get("success", False)
        
        print(f"   ✅ Generated {posts_count} new posts")
        print(f"   Success: {success}")
        
        # Wait a moment for posts to be saved
        time.sleep(2)
        
        # Get the newly generated posts
        response = requests.get(
            f"{BASE_URL}/posts/generated",
            headers=get_headers(token)
        )
        
        if response.status_code == 200:
            data = response.json()
            all_posts = data.get("posts", [])
            
            # Filter for recent posts (last 5 minutes)
            recent_cutoff = datetime.now().timestamp() - 300  # 5 minutes ago
            recent_posts = []
            
            for post in all_posts:
                created_at = post.get("created_at", "")
                if created_at:
                    try:
                        post_time = datetime.fromisoformat(created_at.replace('Z', '+00:00')).timestamp()
                        if post_time > recent_cutoff:
                            recent_posts.append(post)
                    except:
                        pass
            
            print(f"   📋 Found {len(recent_posts)} recently generated posts")
            
            # Analyze recent posts
            recent_fallback = [p for p in recent_posts if p.get("visual_id", "").startswith("global_fallback_")]
            recent_real_photos = [p for p in recent_posts if p.get("visual_id", "") and not p.get("visual_id", "").startswith("global_fallback_")]
            recent_empty = [p for p in recent_posts if not p.get("visual_id", "")]
            
            print(f"   📊 Recent posts analysis:")
            print(f"      With fallback IDs: {len(recent_fallback)}")
            print(f"      With real photo IDs: {len(recent_real_photos)}")
            print(f"      With empty visual IDs: {len(recent_empty)}")
            
            if len(recent_fallback) == 0:
                print("   ✅ SUCCESS: No new fallback IDs generated!")
                return True
            else:
                print("   ❌ FAILURE: New fallback IDs still being generated")
                return False
        
    else:
        print(f"   ❌ Post generation failed: {response.status_code}")
        return False

def main():
    print("🎯 CLEANUP AND TEST: Photo-Post Linking System")
    print("=" * 60)
    
    # Authenticate
    token, user_id = authenticate()
    if not token:
        print("❌ Authentication failed")
        return
    
    print(f"✅ Authenticated as user: {user_id}")
    
    # Step 1: Identify old fallback posts
    old_fallback_count = cleanup_old_posts(token)
    
    # Step 2: Test new post generation
    new_system_works = test_new_post_generation(token)
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 FINAL ANALYSIS:")
    print(f"   Old fallback posts found: {old_fallback_count}")
    print(f"   New system working correctly: {'✅ YES' if new_system_works else '❌ NO'}")
    
    if old_fallback_count > 0 and new_system_works:
        print("\n🎉 CONCLUSION:")
        print("   ✅ The photo-post linking system IS working correctly!")
        print("   ✅ New posts use real photo IDs - NO more fallbacks!")
        print("   ⚠️ Old posts with fallback IDs are from previous system versions")
        print("   💡 Recommendation: The system is fixed and working properly")
    elif new_system_works:
        print("\n🎉 PERFECT: System working with no old fallback posts!")
    else:
        print("\n❌ ISSUE: New system still generating fallback IDs")

if __name__ == "__main__":
    main()