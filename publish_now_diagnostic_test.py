#!/usr/bin/env python3
"""
Backend Testing Script for "Publier de suite" Button Diagnostic
Testing the specific issue reported in French review request:
- Button "Publier de suite" ne fonctionne pas (doesn't work)
- Frontend calls handlePublishNow(post) which makes POST to /posts/{post.id}/publish-now
- Need to test with credentials lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import sys
from datetime import datetime

# Configuration from review request
BACKEND_URL = "https://claire-marcus-app-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials from review request
EMAIL = "lperpere@yahoo.fr"
PASSWORD = "L@Reunion974!"

class PublishNowDiagnostic:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        
    def authenticate(self):
        """Step 1: Authenticate with backend API"""
        print("🔐 Step 1: Authentication with POST /api/auth/login-robust")
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login-robust", json={
                "email": EMAIL,
                "password": PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                print(f"✅ Authentication successful")
                print(f"   User ID: {self.user_id}")
                print(f"   Token: {self.auth_token[:30]}..." if self.auth_token else "   Token: None")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def check_social_connections(self):
        """Step 2: Check social connections status"""
        print("\n🔗 Step 2: Checking social connections with GET /api/debug/social-connections")
        
        try:
            response = self.session.get(f"{API_BASE}/debug/social-connections")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Social connections endpoint accessible")
                
                # Analyze connections
                total_connections = data.get('total_connections', 0)
                active_connections = data.get('active_connections', 0)
                facebook_connections = data.get('facebook_connections', 0)
                instagram_connections = data.get('instagram_connections', 0)
                
                print(f"   Total connections: {total_connections}")
                print(f"   Active connections: {active_connections}")
                print(f"   Facebook connections: {facebook_connections}")
                print(f"   Instagram connections: {instagram_connections}")
                
                # Check connection details
                if 'connections_details' in data:
                    for conn in data['connections_details']:
                        platform = conn.get('platform', 'unknown')
                        active = conn.get('active', False)
                        has_token = bool(conn.get('access_token'))
                        print(f"   - {platform}: active={active}, has_token={has_token}")
                
                return active_connections > 0
            else:
                print(f"❌ Social connections check failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Social connections error: {str(e)}")
            return False
    
    def get_posts_list(self):
        """Step 3: Get posts list to find a post to test with"""
        print("\n📝 Step 3: Getting posts list with GET /api/posts/generated")
        
        try:
            response = self.session.get(f"{API_BASE}/posts/generated")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('posts', [])
                
                print(f"✅ Posts endpoint accessible")
                print(f"   Found {len(posts)} posts")
                
                # Find a suitable post for testing (non-published)
                test_post = None
                for post in posts:
                    if not post.get('published', False):
                        test_post = post
                        break
                
                if test_post:
                    print(f"   Selected test post:")
                    print(f"     ID: {test_post.get('id')}")
                    print(f"     Title: {test_post.get('title', 'N/A')}")
                    print(f"     Platform: {test_post.get('platform', 'N/A')}")
                    print(f"     Status: {test_post.get('status', 'N/A')}")
                    print(f"     Published: {test_post.get('published', False)}")
                    print(f"     Validated: {test_post.get('validated', False)}")
                    
                return test_post
            else:
                print(f"❌ Posts list failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Posts list error: {str(e)}")
            return None
    
    def test_publish_now_endpoint(self, post_id):
        """Step 4: Test the main issue - POST /api/posts/{post_id}/publish-now"""
        print(f"\n🚀 Step 4: Testing PUBLISH NOW endpoint - POST /api/posts/{post_id}/publish-now")
        
        try:
            # This is the exact call that the frontend makes
            response = self.session.post(f"{API_BASE}/posts/{post_id}/publish-now")
            
            print(f"   Request URL: {API_BASE}/posts/{post_id}/publish-now")
            print(f"   Request method: POST")
            print(f"   Authorization: Bearer {self.auth_token[:20]}..." if self.auth_token else "None")
            
            print(f"\n📡 Response received:")
            print(f"   Status code: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ Publish now endpoint responded successfully")
                    print(f"   Response data: {json.dumps(data, indent=2)}")
                    
                    # Check if publication was successful
                    success = data.get('success', False)
                    message = data.get('message', 'No message')
                    
                    if success:
                        print(f"✅ Publication successful: {message}")
                        return True
                    else:
                        print(f"❌ Publication failed: {message}")
                        return False
                        
                except json.JSONDecodeError:
                    print(f"⚠️ Response is not JSON: {response.text}")
                    return False
                    
            elif response.status_code == 404:
                print(f"❌ Endpoint not found (404)")
                print(f"   This suggests the endpoint /posts/{post_id}/publish-now doesn't exist")
                print(f"   Response: {response.text}")
                return False
                
            elif response.status_code == 401:
                print(f"❌ Authentication required (401)")
                print(f"   Response: {response.text}")
                return False
                
            elif response.status_code == 400:
                print(f"❌ Bad request (400)")
                print(f"   Response: {response.text}")
                return False
                
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Publish now endpoint error: {str(e)}")
            return False
    
    def test_alternative_publish_endpoints(self, post_id):
        """Step 5: Test alternative publish endpoints that might exist"""
        print(f"\n🔍 Step 5: Testing alternative publish endpoints for post {post_id}")
        
        alternative_endpoints = [
            f"/posts/{post_id}/publish",
            f"/posts/publish/{post_id}",
            f"/posts/publish",
            f"/social/publish"
        ]
        
        for endpoint in alternative_endpoints:
            try:
                print(f"\n   Testing: POST {API_BASE}{endpoint}")
                
                # Try with post_id in body for generic endpoints
                if endpoint in ["/posts/publish", "/social/publish"]:
                    response = self.session.post(f"{API_BASE}{endpoint}", json={"post_id": post_id})
                else:
                    response = self.session.post(f"{API_BASE}{endpoint}")
                
                print(f"     Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"     ✅ Alternative endpoint found and working!")
                        print(f"     Response: {json.dumps(data, indent=6)}")
                        return endpoint
                    except:
                        print(f"     Response (non-JSON): {response.text[:100]}...")
                elif response.status_code == 404:
                    print(f"     ❌ Not found")
                else:
                    print(f"     Response: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"     Error: {str(e)}")
        
        print(f"   ❌ No working alternative endpoints found")
        return None
    
    def analyze_backend_logs(self):
        """Step 6: Try to get backend logs if available"""
        print(f"\n📋 Step 6: Attempting to analyze backend logs")
        
        # Check if there's a logs endpoint
        try:
            response = self.session.get(f"{API_BASE}/debug/logs")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Backend logs available")
                print(f"   Recent logs: {json.dumps(data, indent=2)}")
            else:
                print(f"⚠️ Backend logs not accessible: {response.status_code}")
        except:
            print(f"⚠️ Backend logs endpoint not available")
    
    def run_comprehensive_diagnostic(self):
        """Run complete diagnostic for publish now button issue"""
        print("🎯 DIAGNOSTIC: BOUTON 'PUBLIER DE SUITE' NE FONCTIONNE PAS")
        print("=" * 70)
        print(f"Environment: {BACKEND_URL}")
        print(f"Credentials: {EMAIL}")
        print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ CRITICAL: Authentication failed - cannot proceed")
            return False
        
        # Step 2: Check social connections
        has_active_connections = self.check_social_connections()
        if not has_active_connections:
            print("\n⚠️ WARNING: No active social connections found")
            print("   This might be the reason why publish now doesn't work")
        
        # Step 3: Get posts list
        test_post = self.get_posts_list()
        if not test_post:
            print("\n❌ CRITICAL: No posts found for testing")
            return False
        
        post_id = test_post.get('id')
        
        # Step 4: Test the main publish now endpoint
        publish_now_works = self.test_publish_now_endpoint(post_id)
        
        # Step 5: Test alternative endpoints if main one fails
        alternative_endpoint = None
        if not publish_now_works:
            alternative_endpoint = self.test_alternative_publish_endpoints(post_id)
        
        # Step 6: Analyze logs
        self.analyze_backend_logs()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 DIAGNOSTIC SUMMARY - BOUTON 'PUBLIER DE SUITE'")
        print("=" * 70)
        
        print(f"✅ Authentication: WORKING")
        print(f"{'✅' if has_active_connections else '❌'} Social Connections: {'ACTIVE' if has_active_connections else 'NO ACTIVE CONNECTIONS'}")
        print(f"✅ Posts Available: {len([test_post]) if test_post else 0} posts found")
        print(f"{'✅' if publish_now_works else '❌'} Main Endpoint (/posts/{{id}}/publish-now): {'WORKING' if publish_now_works else 'FAILED'}")
        
        if alternative_endpoint:
            print(f"✅ Alternative Endpoint ({alternative_endpoint}): WORKING")
        
        print("\n" + "=" * 70)
        
        # Root cause analysis
        if not publish_now_works:
            print("🔍 ROOT CAUSE ANALYSIS:")
            
            if not has_active_connections:
                print("❌ LIKELY CAUSE: No active social media connections")
                print("   - User needs to connect Facebook/Instagram accounts")
                print("   - Check social connections in the app settings")
                
            else:
                print("❌ POSSIBLE CAUSES:")
                print("   1. Endpoint /posts/{id}/publish-now doesn't exist in backend")
                print("   2. Post ID format is incorrect")
                print("   3. Post status prevents publication")
                print("   4. Backend error in publication logic")
                
            print("\n🔧 RECOMMENDED ACTIONS:")
            print("   1. Check if user has active social media connections")
            print("   2. Verify the correct endpoint URL in backend code")
            print("   3. Check backend logs for detailed error messages")
            print("   4. Test with a different post ID")
            
        else:
            print("🎉 CONCLUSION: Publish now functionality is WORKING")
            print("   The button should work correctly in the frontend")
        
        return publish_now_works

def main():
    """Main diagnostic execution"""
    diagnostic = PublishNowDiagnostic()
    success = diagnostic.run_comprehensive_diagnostic()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()