#!/usr/bin/env python3
"""
Instagram to Facebook Post Modifier Test
Mission: Find an Instagram post from September and modify it to be a Facebook post for testing
"""

import requests
import json
import sys
from datetime import datetime

class InstagramToFacebookModifier:
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
                return True
            else:
                print(f"   ❌ Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {str(e)}")
            return False
    
    def find_instagram_posts_september(self):
        """Find Instagram posts from September"""
        try:
            print(f"\n🔍 Step 2: Finding Instagram posts from September")
            
            # Get all generated posts
            response = self.session.get(f"{self.base_url}/posts/generated")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"   ❌ Failed to get posts: {response.text}")
                return []
            
            data = response.json()
            posts = data.get("posts", [])
            
            print(f"   Total posts found: {len(posts)}")
            
            # Filter for Instagram posts from September
            instagram_posts = []
            september_posts = []
            
            for post in posts:
                platform = post.get("platform", "").lower()
                scheduled_date = post.get("scheduled_date", "")
                created_at = post.get("created_at", "")
                validated = post.get("validated", False)
                published = post.get("published", False)
                
                if platform == "instagram":
                    instagram_posts.append(post)
                    
                    # Check if it's from September (check both scheduled_date and created_at)
                    is_september = False
                    if scheduled_date and "2025-09" in scheduled_date:
                        is_september = True
                    elif created_at and "2025-09" in created_at:
                        is_september = True
                    elif scheduled_date and "septembre" in scheduled_date.lower():
                        is_september = True
                    
                    if is_september:
                        september_posts.append(post)
                        print(f"   📅 Found September Instagram post:")
                        print(f"      ID: {post.get('id')}")
                        print(f"      Title: {post.get('title', 'N/A')[:50]}...")
                        print(f"      Scheduled: {scheduled_date}")
                        print(f"      Created: {created_at}")
                        print(f"      Validated: {validated}")
                        print(f"      Published: {published}")
                        print(f"      Status: {post.get('status', 'N/A')}")
            
            print(f"\n📊 Post Analysis:")
            print(f"   Total Instagram posts: {len(instagram_posts)}")
            print(f"   September Instagram posts: {len(september_posts)}")
            
            # Prioritize unpublished posts
            unpublished_september = [p for p in september_posts if not p.get("published", False)]
            print(f"   Unpublished September posts: {len(unpublished_september)}")
            
            if unpublished_september:
                print(f"   ✅ Found {len(unpublished_september)} unpublished September Instagram posts")
                return unpublished_september
            elif september_posts:
                print(f"   ⚠️ Found {len(september_posts)} September Instagram posts (some may be published)")
                return september_posts
            else:
                print(f"   ❌ No September Instagram posts found")
                return []
                
        except Exception as e:
            print(f"   ❌ Error finding posts: {str(e)}")
            return []
    
    def modify_post_to_facebook(self, post_id, original_post):
        """Modify an Instagram post to be a Facebook post"""
        try:
            print(f"\n🔄 Step 3: Modifying post {post_id} from Instagram to Facebook")
            
            # Prepare the update data
            update_data = {
                "platform": "facebook",
                "status": "draft",  # Set to draft as requested
                "validated": False,  # Ensure it's not validated
                "published": False,  # Ensure it's not published
                "updated_at": datetime.utcnow().isoformat()
            }
            
            print(f"   Original platform: {original_post.get('platform')}")
            print(f"   Original status: {original_post.get('status')}")
            print(f"   Original validated: {original_post.get('validated')}")
            print(f"   Original published: {original_post.get('published')}")
            
            # Use PUT endpoint to update the post
            response = self.session.put(
                f"{self.base_url}/posts/{post_id}",
                json=update_data
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Post successfully modified to Facebook")
                
                # Verify the changes
                verify_response = self.session.get(f"{self.base_url}/posts/generated")
                if verify_response.status_code == 200:
                    verify_data = verify_response.json()
                    updated_posts = verify_data.get("posts", [])
                    
                    # Find the updated post
                    updated_post = None
                    for post in updated_posts:
                        if post.get("id") == post_id:
                            updated_post = post
                            break
                    
                    if updated_post:
                        print(f"   📋 Verification - Post after modification:")
                        print(f"      Platform: {updated_post.get('platform')}")
                        print(f"      Status: {updated_post.get('status')}")
                        print(f"      Validated: {updated_post.get('validated')}")
                        print(f"      Published: {updated_post.get('published')}")
                        print(f"      Title: {updated_post.get('title', 'N/A')[:50]}...")
                        
                        # Check if modification was successful
                        if (updated_post.get('platform') == 'facebook' and 
                            updated_post.get('status') == 'draft' and
                            not updated_post.get('validated', False) and
                            not updated_post.get('published', False)):
                            print(f"   ✅ Modification verified successfully!")
                            return True
                        else:
                            print(f"   ❌ Modification verification failed")
                            return False
                    else:
                        print(f"   ⚠️ Could not find updated post for verification")
                        return True  # Assume success if we can't verify
                else:
                    print(f"   ⚠️ Could not verify changes: {verify_response.status_code}")
                    return True  # Assume success if we can't verify
                
            elif response.status_code == 404:
                print(f"   ❌ Post not found: {response.text}")
                return False
            else:
                print(f"   ❌ Modification failed: {response.text}")
                
                # Try alternative approach using generated_posts collection directly
                print(f"   🔄 Trying alternative modification approach...")
                
                # This might require a different endpoint or approach
                # Let's check what endpoints are available
                return self.try_alternative_modification(post_id, update_data)
                
        except Exception as e:
            print(f"   ❌ Error modifying post: {str(e)}")
            return False
    
    def try_alternative_modification(self, post_id, update_data):
        """Try alternative approach to modify the post"""
        try:
            print(f"   🔄 Attempting alternative modification approach...")
            
            # Try using a PATCH request instead of PUT
            response = self.session.patch(
                f"{self.base_url}/posts/{post_id}",
                json=update_data
            )
            
            print(f"   PATCH Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Alternative modification successful")
                return True
            else:
                print(f"   ❌ Alternative modification failed: {response.text}")
                
                # Try using posts/generated endpoint
                response = self.session.put(
                    f"{self.base_url}/posts/generated/{post_id}",
                    json=update_data
                )
                
                print(f"   Generated PUT Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"   ✅ Generated posts modification successful")
                    return True
                else:
                    print(f"   ❌ Generated posts modification failed: {response.text}")
                    return False
                
        except Exception as e:
            print(f"   ❌ Alternative modification error: {str(e)}")
            return False
    
    def test_facebook_post_accessibility(self, post_id):
        """Test if the modified Facebook post is accessible and ready for testing"""
        try:
            print(f"\n🧪 Step 4: Testing Facebook post accessibility for {post_id}")
            
            # Get the specific post
            response = self.session.get(f"{self.base_url}/posts/generated")
            
            if response.status_code != 200:
                print(f"   ❌ Cannot access posts: {response.status_code}")
                return False
            
            data = response.json()
            posts = data.get("posts", [])
            
            # Find our modified post
            test_post = None
            for post in posts:
                if post.get("id") == post_id:
                    test_post = post
                    break
            
            if not test_post:
                print(f"   ❌ Modified post not found")
                return False
            
            print(f"   📋 Facebook Post Ready for Testing:")
            print(f"      ID: {test_post.get('id')}")
            print(f"      Platform: {test_post.get('platform')}")
            print(f"      Status: {test_post.get('status')}")
            print(f"      Title: {test_post.get('title', 'N/A')[:50]}...")
            print(f"      Text: {test_post.get('text', 'N/A')[:100]}...")
            print(f"      Has Image: {'Yes' if test_post.get('visual_url') else 'No'}")
            print(f"      Validated: {test_post.get('validated', False)}")
            print(f"      Published: {test_post.get('published', False)}")
            
            # Test if we can use this post for publication testing
            if (test_post.get('platform') == 'facebook' and 
                test_post.get('status') in ['draft', 'ready'] and
                not test_post.get('published', False)):
                print(f"   ✅ Facebook post is ready for publication testing!")
                
                # Provide the endpoint that should be used for testing
                print(f"\n🎯 TESTING ENDPOINT:")
                print(f"   POST {self.base_url}/posts/publish")
                print(f"   Body: {{'post_id': '{post_id}'}}")
                print(f"   Expected: This should now trigger Facebook publication logs")
                
                return True
            else:
                print(f"   ❌ Post is not in the correct state for testing")
                return False
                
        except Exception as e:
            print(f"   ❌ Error testing post accessibility: {str(e)}")
            return False
    
    def run_modification_task(self):
        """Run the complete Instagram to Facebook modification task"""
        print("🚀 Starting Instagram to Facebook Post Modification")
        print("=" * 70)
        print("MISSION: Find Instagram post from September and modify to Facebook for testing")
        print("=" * 70)
        
        # Credentials from the request
        email = "lperpere@yahoo.fr"
        password = "L@Reunion974!"
        
        # Step 1: Authentication
        if not self.authenticate(email, password):
            print("\n❌ CRITICAL: Authentication failed - cannot proceed")
            return False
        
        # Step 2: Find Instagram posts from September
        september_posts = self.find_instagram_posts_september()
        
        if not september_posts:
            print("\n❌ CRITICAL: No September Instagram posts found - cannot proceed")
            return False
        
        # Step 3: Select the best candidate (prioritize unpublished)
        target_post = september_posts[0]  # Take the first one (already prioritized)
        post_id = target_post.get("id")
        
        print(f"\n🎯 Selected post for modification:")
        print(f"   ID: {post_id}")
        print(f"   Title: {target_post.get('title', 'N/A')[:50]}...")
        print(f"   Current Status: {target_post.get('status')}")
        print(f"   Published: {target_post.get('published', False)}")
        
        # Step 4: Modify the post
        if not self.modify_post_to_facebook(post_id, target_post):
            print(f"\n❌ CRITICAL: Failed to modify post to Facebook")
            return False
        
        # Step 5: Test accessibility
        if not self.test_facebook_post_accessibility(post_id):
            print(f"\n❌ WARNING: Modified post may not be ready for testing")
            return False
        
        print("\n" + "=" * 70)
        print("🎉 MISSION ACCOMPLISHED!")
        print("=" * 70)
        print(f"✅ Instagram post successfully modified to Facebook post")
        print(f"✅ Post ID: {post_id}")
        print(f"✅ Status: draft (ready for testing)")
        print(f"✅ Platform: facebook")
        print(f"✅ Published: false")
        print("\n💡 NEXT STEPS:")
        print(f"   1. Use POST /api/posts/publish with post_id: {post_id}")
        print(f"   2. Monitor backend logs for Facebook publication diagnostics")
        print(f"   3. Check interface behavior with this Facebook post")
        print("=" * 70)
        
        return True

def main():
    """Main execution"""
    modifier = InstagramToFacebookModifier()
    
    try:
        success = modifier.run_modification_task()
        if success:
            print(f"\n🎯 RESULT: Instagram to Facebook modification COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print(f"\n💥 RESULT: Instagram to Facebook modification FAILED")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⚠️ Task interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()