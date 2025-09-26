#!/usr/bin/env python3
"""
Test urgent de l'endpoint de déprogrammation de post calendrier
Test spécifique pour identifier pourquoi la déprogrammation ne fonctionne pas
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://social-ai-planner-2.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

def test_calendar_post_cancellation():
    """Test complet de la déprogrammation de post calendrier"""
    
    print("🎯 URGENT CALENDAR POST CANCELLATION TESTING")
    print("=" * 60)
    
    # Step 1: Authentication
    print("\n📋 Step 1: Authentication")
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login-robust", json=login_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Authentication failed: {response.text}")
            return False
            
        auth_data = response.json()
        token = auth_data["access_token"]
        user_id = auth_data["user_id"]
        
        print(f"   ✅ Authentication successful")
        print(f"   User ID: {user_id}")
        
        headers = {"Authorization": f"Bearer {token}"}
        
    except Exception as e:
        print(f"   ❌ Authentication error: {e}")
        return False
    
    # Step 2: Get calendar posts
    print("\n📋 Step 2: Get calendar posts")
    try:
        response = requests.get(f"{BACKEND_URL}/calendar/posts", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Failed to get calendar posts: {response.text}")
            return False
            
        calendar_data = response.json()
        posts = calendar_data.get("posts", [])
        
        print(f"   ✅ Found {len(posts)} calendar posts")
        
        if not posts:
            print("   ⚠️ No calendar posts found - cannot test cancellation")
            return False
            
        # Use the first post for testing
        test_post = posts[0]
        post_id = test_post["id"]
        
        print(f"   📝 Test post ID: {post_id}")
        print(f"   📝 Test post title: {test_post.get('title', 'No title')}")
        print(f"   📝 Test post platform: {test_post.get('platform', 'Unknown')}")
        print(f"   📝 Test post validated: {test_post.get('validated', False)}")
        print(f"   📝 Test post scheduled_date: {test_post.get('scheduled_date', 'No date')}")
        
    except Exception as e:
        print(f"   ❌ Error getting calendar posts: {e}")
        return False
    
    # Step 3: Test DELETE /posts/cancel-calendar-post/{post_id}
    print(f"\n📋 Step 3: Test DELETE /posts/cancel-calendar-post/{post_id}")
    try:
        response = requests.delete(f"{BACKEND_URL}/posts/cancel-calendar-post/{post_id}", headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Cancellation response received")
            print(f"   Success: {result.get('success', False)}")
            print(f"   Message: {result.get('message', 'No message')}")
            print(f"   Post ID: {result.get('post_id', 'No post_id')}")
            print(f"   Original Post ID: {result.get('original_post_id', 'No original_post_id')}")
            
            if not result.get('success', False):
                print(f"   ❌ Cancellation failed according to response")
                return False
                
        else:
            print(f"   ❌ Cancellation failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
                print(f"   Detail: {error_data.get('detail', 'No detail')}")
            except:
                print(f"   Raw error: {response.text}")
            
            # This is the critical issue - let's analyze why it's failing
            if response.status_code == 404:
                print(f"\n🔍 CRITICAL ANALYSIS - 404 Error:")
                print(f"   The endpoint is returning 404, which means:")
                print(f"   1. Post not found in publication_calendar collection")
                print(f"   2. Wrong user_id field (should be owner_id)")
                print(f"   3. Wrong collection being queried")
                print(f"\n   📊 Let's check what collections and fields exist...")
                return False
            return False
            
    except Exception as e:
        print(f"   ❌ Error calling cancellation endpoint: {e}")
        return False
    
    # Step 4: Verify post is removed from calendar
    print(f"\n📋 Step 4: Verify post removed from calendar")
    try:
        response = requests.get(f"{BACKEND_URL}/calendar/posts", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Failed to get calendar posts for verification: {response.text}")
            return False
            
        calendar_data = response.json()
        posts_after = calendar_data.get("posts", [])
        
        print(f"   📊 Calendar posts after cancellation: {len(posts_after)}")
        
        # Check if the post is still in the calendar
        post_still_in_calendar = any(p["id"] == post_id for p in posts_after)
        
        if post_still_in_calendar:
            print(f"   ❌ CRITICAL ISSUE: Post {post_id} is still in calendar after cancellation!")
            print(f"   This explains why the modal returns to preview - the post wasn't actually removed")
            return False
        else:
            print(f"   ✅ Post {post_id} successfully removed from calendar")
            
    except Exception as e:
        print(f"   ❌ Error verifying calendar posts: {e}")
        return False
    
    # Step 5: Check if post is back in draft state
    print(f"\n📋 Step 5: Check if post is back in draft state")
    try:
        response = requests.get(f"{BACKEND_URL}/posts/generated", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Failed to get generated posts: {response.text}")
            return False
            
        posts_data = response.json()
        all_posts = posts_data.get("posts", [])
        
        # Find the post that was cancelled
        cancelled_post = None
        for post in all_posts:
            if post["id"] == post_id:
                cancelled_post = post
                break
        
        if cancelled_post:
            print(f"   ✅ Found cancelled post in generated posts")
            print(f"   📝 Post validated status: {cancelled_post.get('validated', 'Unknown')}")
            print(f"   📝 Post status: {cancelled_post.get('status', 'Unknown')}")
            
            if cancelled_post.get('validated', True) == False:
                print(f"   ✅ Post correctly returned to draft state (validated=false)")
            else:
                print(f"   ❌ ISSUE: Post still shows as validated=true")
                return False
        else:
            print(f"   ⚠️ Cancelled post not found in generated posts (this might be expected)")
            
    except Exception as e:
        print(f"   ❌ Error checking generated posts: {e}")
        return False
    
    print(f"\n🎉 CALENDAR POST CANCELLATION TEST COMPLETED SUCCESSFULLY")
    print(f"✅ All tests passed - cancellation functionality is working correctly")
    return True

def analyze_database_structure(headers):
    """Analyze the database structure to understand the issue"""
    print("\n🔍 DATABASE STRUCTURE ANALYSIS")
    print("=" * 50)
    
    # Check what's in generated_posts vs publication_calendar
    print("\n📋 Checking generated_posts collection:")
    try:
        response = requests.get(f"{BACKEND_URL}/posts/generated", headers=headers)
        if response.status_code == 200:
            data = response.json()
            posts = data.get("posts", [])
            print(f"   ✅ Found {len(posts)} posts in generated_posts")
            
            if posts:
                sample_post = posts[0]
                print(f"   📝 Sample post fields:")
                for key in sample_post.keys():
                    print(f"     - {key}: {type(sample_post[key])}")
        else:
            print(f"   ❌ Failed to get generated posts: {response.text}")
    except Exception as e:
        print(f"   ❌ Error checking generated_posts: {e}")

def check_backend_logs():
    """Check backend logs for any errors during cancellation"""
    print("\n📋 Backend Logs Analysis")
    print("Note: Check supervisor logs with: tail -n 100 /var/log/supervisor/backend.*.log")

if __name__ == "__main__":
    try:
        success = test_calendar_post_cancellation()
        
        if not success:
            print(f"\n❌ CALENDAR POST CANCELLATION TESTING FAILED")
            print(f"🔍 DIAGNOSTIC RECOMMENDATIONS:")
            print(f"   1. Check if endpoint is looking in correct database collection")
            print(f"   2. Verify user_id vs owner_id field mapping")
            print(f"   3. Check if publication_calendar collection exists and has data")
            print(f"   4. Verify the post ID format and database queries")
            
            # Try to authenticate and analyze database structure
            try:
                login_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
                response = requests.post(f"{BACKEND_URL}/auth/login-robust", json=login_data)
                if response.status_code == 200:
                    auth_data = response.json()
                    headers = {"Authorization": f"Bearer {auth_data['access_token']}"}
                    analyze_database_structure(headers)
            except:
                pass
                
            check_backend_logs()
            sys.exit(1)
        else:
            print(f"\n✅ ALL TESTS PASSED")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print(f"\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)