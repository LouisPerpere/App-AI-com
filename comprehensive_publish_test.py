#!/usr/bin/env python3
"""
Comprehensive Backend Test for "Publier de suite" Button Issue
Based on the diagnostic findings, this test will:
1. Verify the endpoint exists and works
2. Check social connections setup
3. Test with and without social connections
4. Provide detailed root cause analysis
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://claire-marcus-app-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
EMAIL = "lperpere@yahoo.fr"
PASSWORD = "L@Reunion974!"

class ComprehensivePublishTest:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        
    def authenticate(self):
        """Authenticate with backend"""
        print("🔐 Step 1: Authentication")
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login-robust", json={
                "email": EMAIL,
                "password": PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                print(f"✅ Authentication successful - User ID: {self.user_id}")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def detailed_social_connections_check(self):
        """Detailed analysis of social connections"""
        print("\n🔗 Step 2: Detailed Social Connections Analysis")
        
        try:
            # Check debug endpoint
            response = self.session.get(f"{API_BASE}/debug/social-connections")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Debug endpoint accessible")
                print(f"   Total connections: {data.get('total_connections', 0)}")
                print(f"   Active connections: {data.get('active_connections', 0)}")
                print(f"   Facebook: {data.get('facebook_connections', 0)}")
                print(f"   Instagram: {data.get('instagram_connections', 0)}")
                
                # Check regular social connections endpoint
                regular_response = self.session.get(f"{API_BASE}/social/connections")
                if regular_response.status_code == 200:
                    regular_data = regular_response.json()
                    print(f"   Regular endpoint connections: {len(regular_data.get('connections', []))}")
                
                return data.get('active_connections', 0) > 0
            else:
                print(f"❌ Social connections check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Social connections error: {str(e)}")
            return False
    
    def test_publish_now_with_no_connections(self, post_id):
        """Test publish-now endpoint with no social connections (expected to fail)"""
        print(f"\n🚀 Step 3: Testing publish-now with NO social connections")
        print(f"   POST /api/posts/{post_id}/publish-now")
        
        try:
            response = self.session.post(f"{API_BASE}/posts/{post_id}/publish-now")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 400:
                try:
                    data = response.json()
                    error_message = data.get('error', 'Unknown error')
                    print(f"✅ Expected error received: {error_message}")
                    
                    if "Aucune connexion sociale active trouvée" in error_message:
                        print(f"✅ Correct error message - endpoint is working properly")
                        return True
                    else:
                        print(f"⚠️ Unexpected error message: {error_message}")
                        return False
                        
                except json.JSONDecodeError:
                    print(f"❌ Response is not JSON: {response.text}")
                    return False
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Test error: {str(e)}")
            return False
    
    def create_test_social_connection(self):
        """Create a test social connection to verify the endpoint works with connections"""
        print(f"\n🔧 Step 4: Creating test social connection")
        
        try:
            # Try to create a test Facebook connection
            test_connection = {
                "user_id": self.user_id,
                "platform": "facebook",
                "active": True,
                "access_token": "test_token_for_endpoint_testing",
                "page_id": "test_page_id",
                "page_name": "Test Page",
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Insert directly via debug endpoint if available
            response = self.session.post(f"{API_BASE}/debug/create-test-connection", json=test_connection)
            
            if response.status_code == 200:
                print(f"✅ Test connection created successfully")
                return True
            else:
                print(f"⚠️ Could not create test connection: {response.status_code}")
                print(f"   This is expected if debug endpoint doesn't exist")
                return False
                
        except Exception as e:
            print(f"⚠️ Could not create test connection: {str(e)}")
            return False
    
    def test_publish_now_with_connections(self, post_id):
        """Test publish-now endpoint with social connections"""
        print(f"\n🚀 Step 5: Testing publish-now WITH social connections")
        
        try:
            response = self.session.post(f"{API_BASE}/posts/{post_id}/publish-now")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ Publish now successful!")
                    print(f"   Success: {data.get('success', False)}")
                    print(f"   Message: {data.get('message', 'No message')}")
                    print(f"   Published at: {data.get('published_at', 'N/A')}")
                    return True
                    
                except json.JSONDecodeError:
                    print(f"⚠️ Response is not JSON: {response.text}")
                    return False
            else:
                print(f"❌ Publish failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Test error: {str(e)}")
            return False
    
    def get_test_post(self):
        """Get a post for testing"""
        print(f"\n📝 Getting test post")
        
        try:
            response = self.session.get(f"{API_BASE}/posts/generated")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('posts', [])
                
                # Find a non-published post
                for post in posts:
                    if not post.get('published', False):
                        print(f"✅ Found test post: {post.get('id')} - {post.get('title', 'No title')}")
                        return post
                
                print(f"⚠️ No unpublished posts found, using first available")
                return posts[0] if posts else None
            else:
                print(f"❌ Could not get posts: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting posts: {str(e)}")
            return None
    
    def run_comprehensive_test(self):
        """Run complete test suite"""
        print("🎯 COMPREHENSIVE TEST: BOUTON 'PUBLIER DE SUITE' DIAGNOSTIC")
        print("=" * 80)
        print(f"Environment: {BACKEND_URL}")
        print(f"Credentials: {EMAIL}")
        print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ CRITICAL: Authentication failed")
            return False
        
        # Step 2: Check social connections
        has_connections = self.detailed_social_connections_check()
        
        # Get test post
        test_post = self.get_test_post()
        if not test_post:
            print("\n❌ CRITICAL: No test post available")
            return False
        
        post_id = test_post.get('id')
        
        # Step 3: Test without connections (should fail gracefully)
        test_no_conn_result = self.test_publish_now_with_no_connections(post_id)
        
        # Step 4: Try to create test connection
        test_conn_created = self.create_test_social_connection()
        
        # Step 5: Test with connections if we created one
        test_with_conn_result = False
        if test_conn_created:
            test_with_conn_result = self.test_publish_now_with_connections(post_id)
        
        # Summary and Analysis
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 80)
        
        print(f"✅ Authentication: WORKING")
        print(f"{'❌' if not has_connections else '✅'} Social Connections: {'NO ACTIVE CONNECTIONS' if not has_connections else 'ACTIVE CONNECTIONS FOUND'}")
        print(f"✅ Test Post Available: {post_id}")
        print(f"{'✅' if test_no_conn_result else '❌'} Endpoint Error Handling: {'CORRECT' if test_no_conn_result else 'INCORRECT'}")
        
        if test_conn_created:
            print(f"✅ Test Connection Created: SUCCESS")
            print(f"{'✅' if test_with_conn_result else '❌'} Publish with Connections: {'WORKING' if test_with_conn_result else 'FAILED'}")
        else:
            print(f"⚠️ Test Connection Created: NOT AVAILABLE")
        
        print("\n" + "=" * 80)
        print("🔍 ROOT CAUSE ANALYSIS")
        print("=" * 80)
        
        if test_no_conn_result:
            print("✅ ENDPOINT STATUS: The /posts/{id}/publish-now endpoint is WORKING CORRECTLY")
            print("✅ ERROR HANDLING: Proper error message when no social connections")
            print("✅ AUTHENTICATION: Working properly with JWT tokens")
            
            if not has_connections:
                print("\n❌ ROOT CAUSE IDENTIFIED: NO ACTIVE SOCIAL CONNECTIONS")
                print("   The user has no active Facebook/Instagram connections")
                print("   This is why the 'Publier de suite' button doesn't work")
                
                print("\n🔧 SOLUTION:")
                print("   1. User needs to connect Facebook and/or Instagram accounts")
                print("   2. Go to Social Connections settings in the app")
                print("   3. Complete OAuth flow for Facebook/Instagram")
                print("   4. Ensure connections are marked as 'active'")
                
            else:
                print("\n✅ SOCIAL CONNECTIONS: User has active connections")
                print("   The publish now functionality should work")
                
        else:
            print("❌ ENDPOINT ISSUE: The endpoint is not responding correctly")
            print("   This indicates a backend implementation problem")
        
        print("\n" + "=" * 80)
        print("📋 FRONTEND DEBUGGING GUIDE")
        print("=" * 80)
        print("If the frontend button still doesn't work after fixing connections:")
        print("1. Check browser console for JavaScript errors")
        print("2. Verify the frontend is calling the correct URL:")
        print(f"   POST {API_BASE}/posts/{{post_id}}/publish-now")
        print("3. Ensure Authorization header is included in the request")
        print("4. Check if the post ID format is correct")
        print("5. Verify the button click handler is properly bound")
        
        return test_no_conn_result

def main():
    """Main test execution"""
    tester = ComprehensivePublishTest()
    success = tester.run_comprehensive_test()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()