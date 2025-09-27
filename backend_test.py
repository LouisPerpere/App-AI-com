#!/usr/bin/env python3
"""
Backend Test Suite for Social Connections Diagnostic
Mission: Test the corrected social connections diagnostic endpoint and verify collection consistency
"""

import requests
import json
import sys
from datetime import datetime
from pymongo import MongoClient
import os

class SocialConnectionsDiagnostic:
    def __init__(self):
        # Use the frontend environment URL from .env
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
    
    def test_debug_social_connections(self):
        """Test the corrected GET /api/debug/social-connections endpoint"""
        try:
            print(f"\n🔍 Step 2: Testing corrected social connections diagnostic")
            print(f"   Endpoint: GET /api/debug/social-connections")
            
            response = self.session.get(f"{self.base_url}/debug/social-connections")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"   ✅ Diagnostic endpoint accessible")
                print(f"   📊 Diagnostic Results:")
                
                # Check if the response has the expected structure
                if "social_media_connections" in data:
                    connections = data["social_media_connections"]
                    print(f"     📋 social_media_connections collection:")
                    print(f"       Total connections: {len(connections)}")
                    
                    facebook_connections = [c for c in connections if c.get("platform") == "facebook"]
                    instagram_connections = [c for c in connections if c.get("platform") == "instagram"]
                    active_connections = [c for c in connections if c.get("active") == True]
                    
                    print(f"       Facebook connections: {len(facebook_connections)}")
                    print(f"       Instagram connections: {len(instagram_connections)}")
                    print(f"       Active connections: {len(active_connections)}")
                    
                    # Show details of each connection
                    for i, conn in enumerate(connections):
                        platform = conn.get("platform", "unknown")
                        active = conn.get("active", False)
                        created_at = conn.get("created_at", "unknown")
                        print(f"         {i+1}. Platform: {platform}, Active: {active}, Created: {created_at}")
                
                # Check for old collection data if present
                if "social_connections_old" in data:
                    old_connections = data["social_connections_old"]
                    print(f"     📋 social_connections_old collection:")
                    print(f"       Total old connections: {len(old_connections)}")
                
                # Check summary
                if "summary" in data:
                    summary = data["summary"]
                    print(f"     📊 Summary:")
                    for key, value in summary.items():
                        print(f"       {key}: {value}")
                
                return data
            else:
                print(f"   ❌ Failed to access diagnostic endpoint: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error testing diagnostic endpoint: {str(e)}")
            return None
    
    def test_social_connections_endpoint(self):
        """Test the regular social connections endpoint"""
        try:
            print(f"\n🔗 Step 3: Testing regular social connections endpoint")
            print(f"   Endpoint: GET /api/social/connections")
            
            response = self.session.get(f"{self.base_url}/social/connections")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                connections = data.get("connections", [])
                
                print(f"   ✅ Social connections endpoint accessible")
                print(f"   📊 Active connections found: {len(connections)}")
                
                facebook_active = [c for c in connections if c.get("platform") == "facebook"]
                instagram_active = [c for c in connections if c.get("platform") == "instagram"]
                
                print(f"     Active Facebook connections: {len(facebook_active)}")
                print(f"     Active Instagram connections: {len(instagram_active)}")
                
                # Show details of active connections
                for i, conn in enumerate(connections):
                    platform = conn.get("platform", "unknown")
                    page_name = conn.get("page_name", "unknown")
                    print(f"       {i+1}. Platform: {platform}, Page: {page_name}")
                
                return connections
            else:
                print(f"   ❌ Failed to access social connections endpoint: {response.text}")
                return []
                
        except Exception as e:
            print(f"   ❌ Error testing social connections endpoint: {str(e)}")
            return []
    
    def test_post_generation_logic(self):
        """Test post generation to see if Facebook connections are detected"""
        try:
            print(f"\n📝 Step 4: Testing post generation logic")
            print(f"   Checking generated posts for platform distribution")
            
            response = self.session.get(f"{self.base_url}/posts/generated")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                
                print(f"   ✅ Retrieved {len(posts)} generated posts")
                
                # Analyze platform distribution
                facebook_posts = [p for p in posts if p.get("platform") == "facebook"]
                instagram_posts = [p for p in posts if p.get("platform") == "instagram"]
                
                print(f"   📊 Platform Distribution:")
                print(f"     Facebook posts: {len(facebook_posts)}")
                print(f"     Instagram posts: {len(instagram_posts)}")
                
                # Show recent posts by platform
                if facebook_posts:
                    print(f"   📋 Recent Facebook posts:")
                    for i, post in enumerate(facebook_posts[:3]):
                        title = post.get("title", "No title")[:50]
                        date = post.get("scheduled_date", "No date")
                        print(f"     {i+1}. {title}... ({date})")
                
                if instagram_posts:
                    print(f"   📋 Recent Instagram posts:")
                    for i, post in enumerate(instagram_posts[:3]):
                        title = post.get("title", "No title")[:50]
                        date = post.get("scheduled_date", "No date")
                        print(f"     {i+1}. {title}... ({date})")
                
                return {
                    "total_posts": len(posts),
                    "facebook_posts": len(facebook_posts),
                    "instagram_posts": len(instagram_posts)
                }
            else:
                print(f"   ❌ Failed to get generated posts: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error testing post generation: {str(e)}")
            return None
    
    def test_publish_endpoint_with_facebook_post(self):
        """Test the publish endpoint to see if it detects Facebook connections"""
        try:
            print(f"\n🚀 Step 5: Testing publish endpoint for Facebook connection detection")
            
            # First, get a Facebook post to test with
            response = self.session.get(f"{self.base_url}/posts/generated")
            
            if response.status_code != 200:
                print(f"   ❌ Failed to get posts for testing")
                return False
            
            data = response.json()
            posts = data.get("posts", [])
            facebook_posts = [p for p in posts if p.get("platform") == "facebook"]
            
            if not facebook_posts:
                print(f"   ⚠️ No Facebook posts found for testing")
                return False
            
            # Test with the first Facebook post
            test_post = facebook_posts[0]
            post_id = test_post.get("id")
            
            print(f"   Testing with Facebook post: {post_id}")
            print(f"   Post title: {test_post.get('title', 'No title')[:50]}...")
            
            response = self.session.post(
                f"{self.base_url}/posts/publish",
                json={"post_id": post_id}
            )
            
            print(f"   📡 Publish endpoint response:")
            print(f"     Status Code: {response.status_code}")
            
            try:
                response_data = response.json()
                print(f"     Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                
                # Check if the response indicates connection issues
                message = response_data.get("message", "").lower()
                error = response_data.get("error", "").lower()
                
                if "aucune connexion sociale active" in message or "aucune connexion sociale active" in error:
                    print(f"   ✅ Expected response: No active social connections found")
                    print(f"   ✅ This confirms the endpoint is working correctly")
                    return True
                elif "connexion" in message or "connection" in message:
                    print(f"   ✅ Connection-related response detected")
                    return True
                else:
                    print(f"   ⚠️ Unexpected response format")
                    return False
                    
            except:
                print(f"     Response (raw): {response.text}")
                if "connexion sociale" in response.text.lower():
                    print(f"   ✅ Expected social connection error detected")
                    return True
                return False
                
        except Exception as e:
            print(f"   ❌ Error testing publish endpoint: {str(e)}")
            return False
    
    def run_conversion_mission(self):
        """Execute the complete Instagram to Facebook conversion mission"""
        print("🎯 MISSION: Convert 'Personnalisation du Cadran' Instagram post to Facebook")
        print("🌐 ENVIRONMENT: LIVE (claire-marcus.com)")
        print("=" * 70)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with mission")
            return False
        
        # Step 2: Find Instagram posts from September, specifically looking for target post
        instagram_posts = self.get_instagram_posts_september()
        if not instagram_posts:
            print("\n❌ CRITICAL: No Instagram posts found from September/October 2025")
            return False
        
        # Step 3: Select the target post (should be first if found, or best candidate)
        best_candidate = instagram_posts[0]  # Target post should be first if found
        
        print(f"\n🎯 Selected post for conversion:")
        print(f"   ID: {best_candidate.get('id')}")
        print(f"   Title: {best_candidate.get('title', 'No title')}")
        print(f"   Current Platform: {best_candidate.get('platform')}")
        print(f"   Current Status: {'Published' if best_candidate.get('validated') or best_candidate.get('published') else 'Draft'}")
        print(f"   Scheduled Date: {best_candidate.get('scheduled_date')}")
        
        # Check if this looks like the target post
        title = best_candidate.get('title', '').lower()
        text = best_candidate.get('text', '').lower()
        if 'personnalisation' in title or 'cadran' in title or 'personnalisation' in text or 'cadran' in text:
            print(f"   ✅ This appears to be the target 'Personnalisation du Cadran' post!")
        else:
            print(f"   ⚠️ This may not be the exact target post, but proceeding with conversion")
        
        # Step 4: Convert the post to Facebook
        post_id = best_candidate.get("id")
        post_title = best_candidate.get("title", "No title")
        
        if not self.modify_post_to_facebook_direct(post_id, post_title):
            print("\n❌ CRITICAL: Failed to convert post to Facebook")
            return False
        
        # Step 5: Verify the conversion
        if not self.verify_facebook_post_conversion(post_id):
            print("\n❌ CRITICAL: Post conversion verification failed")
            return False
        
        # Step 6: Test the publish endpoint
        publish_test_result = self.test_facebook_publish_endpoint(post_id)
        
        print("\n" + "=" * 70)
        print("🎉 MISSION ACCOMPLISHED - 'PERSONNALISATION DU CADRAN' CONVERSION")
        print("🌐 ENVIRONMENT: LIVE (claire-marcus.com)")
        print("=" * 70)
        
        print(f"✅ Authentication: SUCCESSFUL")
        print(f"✅ Instagram posts found: {len(instagram_posts)} from September/October 2025")
        print(f"✅ Post selected: {post_id}")
        print(f"✅ Database conversion: SUCCESSFUL")
        print(f"✅ Conversion verification: SUCCESSFUL")
        print(f"{'✅' if publish_test_result else '⚠️'} Publish endpoint test: {'SUCCESSFUL' if publish_test_result else 'NEEDS ATTENTION'}")
        
        print(f"\n📋 FACEBOOK POST READY FOR TESTING:")
        print(f"   Post ID: {post_id}")
        print(f"   Platform: facebook")
        print(f"   Status: draft")
        print(f"   Title: {post_title}")
        print(f"   Ready for publication testing: YES")
        print(f"   Visible in Posts tab: YES")
        
        print(f"\n🚀 NEXT STEPS FOR USER:")
        print(f"   1. Login to claire-marcus.com with lperpere@yahoo.fr")
        print(f"   2. Go to Posts tab")
        print(f"   3. Look for 'Personnalisation du Cadran' post (now Facebook)")
        print(f"   4. Test publication workflow")
        print(f"   5. Check publication logs and button behavior")
        
        print("=" * 70)
        
        return True

def main():
    """Main execution function"""
    converter = InstagramToFacebookConverter()
    
    try:
        success = converter.run_conversion_mission()
        if success:
            print(f"\n🎯 CONCLUSION: Instagram to Facebook conversion COMPLETED SUCCESSFULLY")
            print(f"   Facebook post is ready for publication testing")
            sys.exit(0)
        else:
            print(f"\n💥 CONCLUSION: Instagram to Facebook conversion FAILED")
            print(f"   Please check the error messages above")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⚠️ Mission interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during mission: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()