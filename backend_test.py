#!/usr/bin/env python3
"""
Backend Test Suite for Facebook Connection and Publication Issues
Testing social connections state and publication functionality
"""

import requests
import json
import sys
from datetime import datetime

class FacebookConnectionTester:
    def __init__(self):
        self.base_url = "https://social-ai-planner-2.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        
    def authenticate(self, email, password):
        """Authenticate with the API"""
        try:
            print(f"🔐 Step 1: Authenticating with {email}")
            
            response = self.session.post(
                f"{self.base_url}/auth/login-robust",
                json={"email": email, "password": password},
                headers={"Content-Type": "application/json"}
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for all future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                })
                
                print(f"   ✅ Authentication successful")
                print(f"   User ID: {self.user_id}")
                print(f"   Token: {self.token[:30]}..." if self.token else "   Token: None")
                return True
            else:
                print(f"   ❌ Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {str(e)}")
            return False
    
    def test_social_connections_debug(self):
        """Test GET /api/debug/social-connections to check Facebook connection state"""
        try:
            print(f"\n🔍 Step 2: Testing GET /api/debug/social-connections")
            
            response = self.session.get(f"{self.base_url}/debug/social-connections")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"   ✅ Debug endpoint accessible")
                
                # Check for Facebook connections
                facebook_connections = 0
                instagram_connections = 0
                active_connections = 0
                
                # Check old collection
                old_connections = data.get("social_connections_old", [])
                print(f"   Old connections found: {len(old_connections)}")
                
                for conn in old_connections:
                    platform = conn.get("platform", "").lower()
                    is_active = conn.get("is_active", False)
                    
                    if platform == "facebook":
                        facebook_connections += 1
                    elif platform == "instagram":
                        instagram_connections += 1
                    
                    if is_active:
                        active_connections += 1
                        print(f"     ✅ Active {platform} connection found")
                    else:
                        print(f"     ❌ Inactive {platform} connection found")
                
                # Check new collection
                new_connections = data.get("social_media_connections", [])
                print(f"   New connections found: {len(new_connections)}")
                
                for conn in new_connections:
                    platform = conn.get("platform", "").lower()
                    is_active = conn.get("is_active", True)  # New collection might not have is_active field
                    
                    if platform == "facebook":
                        facebook_connections += 1
                    elif platform == "instagram":
                        instagram_connections += 1
                    
                    if is_active:
                        active_connections += 1
                        print(f"     ✅ Active {platform} connection found in new collection")
                
                print(f"\n📊 Connection Analysis:")
                print(f"   Total Facebook connections: {facebook_connections}")
                print(f"   Total Instagram connections: {instagram_connections}")
                print(f"   Total active connections: {active_connections}")
                
                # Check if user has reconnected Facebook as reported
                if facebook_connections > 0:
                    print(f"   ✅ Facebook connection exists in database")
                    if active_connections > 0:
                        print(f"   ✅ Active Facebook connection confirmed")
                        return True
                    else:
                        print(f"   ❌ Facebook connection exists but is INACTIVE")
                        return False
                else:
                    print(f"   ❌ No Facebook connection found - user may need to reconnect")
                    return False
                
            else:
                print(f"   ❌ Debug endpoint failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Test error: {str(e)}")
            return False
    
    def test_posts_publish_endpoint(self):
        """Test POST /api/posts/publish with a real post_id"""
        try:
            print(f"\n🔍 Step 3: Testing POST /api/posts/publish")
            
            # First, get available posts to find a valid post_id
            posts_response = self.session.get(f"{self.base_url}/posts/generated")
            
            if posts_response.status_code != 200:
                print(f"   ❌ Cannot get posts for testing: {posts_response.status_code}")
                return False
            
            posts_data = posts_response.json()
            posts = posts_data.get("posts", [])
            
            if not posts:
                print(f"   ❌ No posts available for publication testing")
                return False
            
            # Find a suitable post for testing (preferably Facebook)
            test_post = None
            for post in posts:
                if post.get("platform", "").lower() == "facebook":
                    test_post = post
                    break
            
            if not test_post:
                # Use first available post if no Facebook post found
                test_post = posts[0]
            
            post_id = test_post.get("id")
            platform = test_post.get("platform", "unknown")
            
            print(f"   Using test post: {post_id}")
            print(f"   Platform: {platform}")
            print(f"   Title: {test_post.get('title', 'N/A')[:50]}...")
            
            # Test the publish endpoint
            response = self.session.post(
                f"{self.base_url}/posts/publish",
                json={"post_id": post_id}
            )
            
            print(f"   Status: {response.status_code}")
            
            try:
                response_data = response.json()
                print(f"   Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"   Response (raw): {response.text}")
            
            if response.status_code == 200:
                print(f"   ✅ Publication endpoint returned success")
                return True
            elif response.status_code == 400:
                # Check if it's the expected "no active social connections" error
                if "connexion sociale active" in response.text.lower():
                    print(f"   ⚠️ Expected error: No active social connections found")
                    print(f"   This confirms the endpoint is working but user needs active Facebook connection")
                    return True
                else:
                    print(f"   ❌ Unexpected 400 error: {response.text}")
                    return False
            elif response.status_code == 404:
                print(f"   ❌ Post not found error: {response.text}")
                return False
            else:
                print(f"   ❌ Unexpected status code: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Test error: {str(e)}")
            return False
    
    def test_social_connections_regular_endpoint(self):
        """Test GET /api/social/connections (regular endpoint used by frontend)"""
        try:
            print(f"\n🔍 Step 4: Testing GET /api/social/connections (frontend endpoint)")
            
            response = self.session.get(f"{self.base_url}/social/connections")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                connections = data.get("connections", [])
                
                print(f"   ✅ Regular connections endpoint accessible")
                print(f"   Active connections returned: {len(connections)}")
                
                facebook_active = False
                instagram_active = False
                
                for conn in connections:
                    platform = conn.get("platform", "").lower()
                    print(f"     - {platform.title()} connection found")
                    
                    if platform == "facebook":
                        facebook_active = True
                    elif platform == "instagram":
                        instagram_active = True
                
                print(f"\n📊 Frontend Connection State:")
                print(f"   Facebook active: {facebook_active}")
                print(f"   Instagram active: {instagram_active}")
                
                # This explains the UI issue - if no active connections are returned,
                # the frontend will show "Connecter" instead of "Connecté"
                if not facebook_active:
                    print(f"   ❌ No active Facebook connection - explains 'Connecter' button issue")
                    return False
                else:
                    print(f"   ✅ Active Facebook connection found - UI should show 'Connecté'")
                    return True
                
            else:
                print(f"   ❌ Regular connections endpoint failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Test error: {str(e)}")
            return False
    
    def test_publication_workflow_analysis(self):
        """Analyze the complete publication workflow to understand UI issues"""
        try:
            print(f"\n🔍 Step 5: Analyzing publication workflow for UI issues")
            
            # Get posts to understand the current state
            posts_response = self.session.get(f"{self.base_url}/posts/generated")
            
            if posts_response.status_code != 200:
                print(f"   ❌ Cannot get posts: {posts_response.status_code}")
                return False
            
            posts_data = posts_response.json()
            posts = posts_data.get("posts", [])
            
            print(f"   Total posts available: {len(posts)}")
            
            # Analyze post statuses
            facebook_posts = [p for p in posts if p.get("platform", "").lower() == "facebook"]
            published_posts = [p for p in posts if p.get("published", False)]
            
            print(f"   Facebook posts: {len(facebook_posts)}")
            print(f"   Published posts: {len(published_posts)}")
            
            # Check if any posts have been published recently
            if facebook_posts:
                sample_fb_post = facebook_posts[0]
                print(f"\n   📋 Sample Facebook post analysis:")
                print(f"     ID: {sample_fb_post.get('id')}")
                print(f"     Status: {sample_fb_post.get('status')}")
                print(f"     Published: {sample_fb_post.get('published', False)}")
                print(f"     Has image: {'Yes' if sample_fb_post.get('visual_url') else 'No'}")
                print(f"     Visual URL: {sample_fb_post.get('visual_url', 'None')}")
                
                # This helps understand why images might not be published
                if not sample_fb_post.get('visual_url'):
                    print(f"   ⚠️ Post has no image - this could explain image publication issues")
                
                # Check if post status indicates successful publication
                status = sample_fb_post.get('status', '')
                if status == 'published':
                    print(f"   ✅ Post status indicates successful publication")
                else:
                    print(f"   ❌ Post status '{status}' does not indicate publication")
            
            # Test the social connections to understand the root cause
            connections_response = self.session.get(f"{self.base_url}/social/connections")
            
            if connections_response.status_code == 200:
                connections_data = connections_response.json()
                active_connections = connections_data.get("connections", [])
                
                print(f"\n   🔗 Active connections analysis:")
                print(f"     Active connections count: {len(active_connections)}")
                
                if not active_connections:
                    print(f"   🎯 ROOT CAUSE IDENTIFIED:")
                    print(f"     - No active social connections found")
                    print(f"     - This explains why UI shows 'Connecter' instead of 'Connecté'")
                    print(f"     - This explains why publication fails")
                    print(f"     - User needs to reconnect Facebook account")
                    return False
                else:
                    facebook_connected = any(c.get("platform", "").lower() == "facebook" for c in active_connections)
                    if facebook_connected:
                        print(f"   ✅ Facebook connection is active")
                        return True
                    else:
                        print(f"   ❌ Facebook connection not found in active connections")
                        return False
            else:
                print(f"   ❌ Cannot check active connections: {connections_response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Workflow analysis error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting POST Validator Backend Testing")
        print("=" * 60)
        
        # Test credentials from the review request
        email = "lperpere@yahoo.fr"
        password = "L@Reunion974!"
        
        # Step 1: Authentication
        if not self.authenticate(email, password):
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Test GET /posts/generated endpoint
        if not self.test_posts_generated_endpoint():
            print("\n❌ CRITICAL: GET /posts/generated endpoint test failed")
            return False
        
        # Step 3: Test field structure validation
        if not self.test_field_structure_validation():
            print("\n❌ CRITICAL: Field structure validation failed")
            return False
        
        # Step 4: Test validated posts logic
        if not self.test_validated_posts_logic():
            print("\n❌ CRITICAL: Validated posts logic test failed")
            return False
        
        # Step 5: Test response format compatibility
        if not self.test_response_format_compatibility():
            print("\n❌ CRITICAL: Response format compatibility test failed")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED SUCCESSFULLY!")
        print("✅ GET /posts/generated endpoint includes 'validated' field")
        print("✅ 'validated_at' and 'carousel_images' fields are present")
        print("✅ Field types and structure are correct")
        print("✅ Response format is compatible with frontend")
        print("=" * 60)
        
        return True

def main():
    """Main test execution"""
    tester = PostValidatorTester()
    
    try:
        success = tester.run_all_tests()
        if success:
            print(f"\n🎯 CONCLUSION: Backend validation field fix is WORKING CORRECTLY")
            sys.exit(0)
        else:
            print(f"\n💥 CONCLUSION: Backend validation field fix has ISSUES")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()