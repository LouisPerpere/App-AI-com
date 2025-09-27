#!/usr/bin/env python3
"""
Backend Test Suite for Instagram to Facebook Post Conversion
Mission: Convert an Instagram post from September to Facebook for testing publication
"""

import requests
import json
import sys
from datetime import datetime
from pymongo import MongoClient
import os

class InstagramToFacebookConverter:
    def __init__(self):
        self.base_url = "https://social-ai-planner-2.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.credentials = {
            "email": "lperpere@yahoo.fr",
            "password": "L@Reunion974!"
        }
        
    def authenticate(self):
        """Authenticate with the API"""
        try:
            print(f"🔐 Step 1: Authenticating with {self.credentials['email']}")
            
            response = self.session.post(
                f"{self.base_url}/auth/login-robust",
                json=self.credentials,
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
    
    def get_instagram_posts_september(self):
        """Get Instagram posts from September 2025"""
        try:
            print(f"\n📋 Step 2: Finding Instagram posts from September 2025")
            
            response = self.session.get(f"{self.base_url}/posts/generated")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                
                print(f"   ✅ Retrieved {len(posts)} total posts")
                
                # Filter Instagram posts from September 2025
                instagram_posts_september = []
                for post in posts:
                    platform = post.get("platform", "").lower()
                    scheduled_date = post.get("scheduled_date", "")
                    
                    # Check if it's Instagram and from September 2025
                    if platform == "instagram" and "2025-09" in scheduled_date:
                        instagram_posts_september.append(post)
                
                print(f"   🔍 Found {len(instagram_posts_september)} Instagram posts from September 2025")
                
                # Show details of found posts
                for i, post in enumerate(instagram_posts_september):
                    validated = post.get("validated", False)
                    published = post.get("published", False)
                    status = "Published" if validated or published else "Draft"
                    
                    print(f"     {i+1}. ID: {post.get('id')}")
                    print(f"        Title: {post.get('title', 'No title')[:50]}...")
                    print(f"        Date: {post.get('scheduled_date')}")
                    print(f"        Status: {status}")
                    print(f"        Validated: {validated}")
                    print()
                
                return instagram_posts_september
            else:
                print(f"   ❌ Failed to get posts: {response.text}")
                return []
                
        except Exception as e:
            print(f"   ❌ Error getting posts: {str(e)}")
            return []
    
    def modify_post_to_facebook_direct(self, post_id, post_title):
        """Modify Instagram post to Facebook using direct MongoDB access"""
        try:
            print(f"\n🔄 Step 3: Converting Instagram post to Facebook via MongoDB")
            print(f"   Post ID: {post_id}")
            print(f"   Title: {post_title}")
            
            # Connect to MongoDB directly
            mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/claire_marcus')
            print(f"   MongoDB URL: {mongo_url}")
            
            client = MongoClient(mongo_url)
            db = client.claire_marcus
            collection = db.generated_posts
            
            # Find the post first
            post = collection.find_one({
                "id": post_id,
                "owner_id": self.user_id
            })
            
            if not post:
                print(f"   ❌ Post not found in database")
                return False
            
            print(f"   ✅ Post found in database")
            print(f"   Current platform: {post.get('platform')}")
            print(f"   Current validated: {post.get('validated', False)}")
            
            # Update the post
            update_result = collection.update_one(
                {"id": post_id, "owner_id": self.user_id},
                {"$set": {
                    "platform": "facebook",
                    "status": "draft",
                    "validated": False,
                    "published": False,
                    "modified_at": datetime.utcnow().isoformat(),
                    "conversion_note": "Converted from Instagram to Facebook for testing"
                }}
            )
            
            if update_result.modified_count > 0:
                print(f"   ✅ Post successfully converted to Facebook!")
                print(f"   Modified count: {update_result.modified_count}")
                
                # Verify the change
                updated_post = collection.find_one({
                    "id": post_id,
                    "owner_id": self.user_id
                })
                
                if updated_post:
                    print(f"   ✅ Verification successful:")
                    print(f"     Platform: {updated_post.get('platform')}")
                    print(f"     Status: {updated_post.get('status')}")
                    print(f"     Validated: {updated_post.get('validated', False)}")
                    print(f"     Published: {updated_post.get('published', False)}")
                
                client.close()
                return True
            else:
                print(f"   ❌ No documents were modified")
                client.close()
                return False
                
        except Exception as e:
            print(f"   ❌ Error modifying post: {str(e)}")
            return False
    
    def verify_facebook_post_conversion(self, post_id):
        """Verify the post has been successfully converted to Facebook"""
        try:
            print(f"\n✅ Step 4: Verifying Facebook post conversion")
            
            response = self.session.get(f"{self.base_url}/posts/generated")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                
                # Find the converted post
                for post in posts:
                    if post.get("id") == post_id:
                        platform = post.get("platform", "")
                        status = post.get("status", "")
                        validated = post.get("validated", False)
                        published = post.get("published", False)
                        
                        print(f"   📋 Post verification results:")
                        print(f"     ID: {post_id}")
                        print(f"     Platform: {platform}")
                        print(f"     Status: {status}")
                        print(f"     Validated: {validated}")
                        print(f"     Published: {published}")
                        print(f"     Title: {post.get('title', 'No title')}")
                        print(f"     Scheduled Date: {post.get('scheduled_date')}")
                        
                        if platform.lower() == "facebook" and not validated and not published:
                            print(f"   ✅ Post successfully converted to Facebook!")
                            print(f"   ✅ Post is in draft status (not validated/published)")
                            print(f"   ✅ Ready for Facebook publication testing")
                            return True
                        else:
                            print(f"   ❌ Post conversion verification failed")
                            if platform.lower() != "facebook":
                                print(f"     - Platform is still '{platform}', expected 'facebook'")
                            if validated or published:
                                print(f"     - Post is still validated/published, expected draft")
                            return False
                
                print(f"   ❌ Post not found after conversion")
                return False
            else:
                print(f"   ❌ Failed to verify post: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error verifying post: {str(e)}")
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
        print("🚀 Starting Facebook Connection and Publication Testing")
        print("=" * 70)
        
        # Test credentials from the review request
        email = "lperpere@yahoo.fr"
        password = "L@Reunion974!"
        
        # Step 1: Authentication
        if not self.authenticate(email, password):
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Test social connections debug endpoint
        debug_result = self.test_social_connections_debug()
        
        # Step 3: Test publication endpoint
        publish_result = self.test_posts_publish_endpoint()
        
        # Step 4: Test regular social connections endpoint (used by frontend)
        frontend_result = self.test_social_connections_regular_endpoint()
        
        # Step 5: Analyze complete workflow
        workflow_result = self.test_publication_workflow_analysis()
        
        print("\n" + "=" * 70)
        print("📊 FACEBOOK CONNECTION & PUBLICATION TEST RESULTS:")
        print("=" * 70)
        
        print(f"✅ Authentication: PASSED")
        print(f"{'✅' if debug_result else '❌'} Social Connections Debug: {'PASSED' if debug_result else 'FAILED'}")
        print(f"{'✅' if publish_result else '❌'} Publication Endpoint: {'PASSED' if publish_result else 'FAILED'}")
        print(f"{'✅' if frontend_result else '❌'} Frontend Connections: {'PASSED' if frontend_result else 'FAILED'}")
        print(f"{'✅' if workflow_result else '❌'} Workflow Analysis: {'PASSED' if workflow_result else 'FAILED'}")
        
        # Determine overall result
        all_passed = debug_result and publish_result and frontend_result and workflow_result
        
        if all_passed:
            print(f"\n🎉 ALL TESTS PASSED - Facebook connection is working correctly!")
        else:
            print(f"\n⚠️ ISSUES IDENTIFIED - Facebook connection needs attention")
            print(f"\n🎯 LIKELY ROOT CAUSE:")
            if not frontend_result:
                print(f"   - No active Facebook connection found in frontend endpoint")
                print(f"   - This explains why UI shows 'Connecter' instead of 'Connecté'")
            if not publish_result:
                print(f"   - Publication endpoint cannot find active social connections")
                print(f"   - This explains why publication fails")
            print(f"\n💡 SOLUTION: User needs to reconnect Facebook account properly")
        
        print("=" * 70)
        
        return all_passed

def main():
    """Main test execution"""
    tester = FacebookConnectionTester()
    
    try:
        success = tester.run_all_tests()
        if success:
            print(f"\n🎯 CONCLUSION: Facebook connection and publication system is WORKING CORRECTLY")
            sys.exit(0)
        else:
            print(f"\n💥 CONCLUSION: Facebook connection system has ISSUES that need to be resolved")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()