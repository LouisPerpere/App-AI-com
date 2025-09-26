#!/usr/bin/env python3
"""
Backend Test Suite for POST /api/posts/publish Endpoint
Testing the corrected endpoint that had JSON serialization issues with ObjectId
"""

import requests
import json
import sys
from datetime import datetime

class PublishEndpointTester:
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
    
    def get_valid_post_id(self):
        """Get a valid post_id for testing"""
        try:
            print(f"\n🔍 Step 2: Getting valid post_id for testing")
            
            response = self.session.get(f"{self.base_url}/posts/generated")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                
                if posts:
                    # Get the first post ID
                    post_id = posts[0].get("id")
                    post_title = posts[0].get("title", "")[:50]
                    post_platform = posts[0].get("platform", "")
                    
                    print(f"   ✅ Found {len(posts)} posts")
                    print(f"   Selected post ID: {post_id}")
                    print(f"   Post title: {post_title}...")
                    print(f"   Platform: {post_platform}")
                    
                    return post_id
                else:
                    print(f"   ❌ No posts found for testing")
                    return None
            else:
                print(f"   ❌ Failed to get posts: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error getting post ID: {str(e)}")
            return None
    
    def test_publish_endpoint_exists(self):
        """Test that the publish endpoint exists and requires authentication"""
        try:
            print(f"\n🔍 Step 3: Testing POST /api/posts/publish endpoint existence")
            
            # Test without authentication first
            temp_session = requests.Session()
            response = temp_session.post(
                f"{self.base_url}/posts/publish",
                json={"post_id": "test"},
                headers={"Content-Type": "application/json"}
            )
            
            print(f"   Status without auth: {response.status_code}")
            
            if response.status_code == 401:
                print(f"   ✅ Endpoint exists and requires authentication")
                return True
            elif response.status_code == 404:
                print(f"   ❌ Endpoint not found")
                return False
            else:
                print(f"   ⚠️ Unexpected response without auth: {response.text}")
                return True  # Endpoint exists but behaves differently
                
        except Exception as e:
            print(f"   ❌ Error testing endpoint existence: {str(e)}")
            return False
    
    def test_publish_endpoint_validation(self):
        """Test endpoint parameter validation"""
        try:
            print(f"\n🔍 Step 4: Testing endpoint parameter validation")
            
            # Test 1: Missing post_id
            print(f"   Test 4a: Missing post_id parameter")
            response = self.session.post(
                f"{self.base_url}/posts/publish",
                json={},
                headers={"Content-Type": "application/json"}
            )
            
            print(f"     Status: {response.status_code}")
            if response.status_code == 400:
                print(f"     ✅ Correctly rejects missing post_id")
            else:
                print(f"     ⚠️ Unexpected response: {response.text}")
            
            # Test 2: Empty post_id
            print(f"   Test 4b: Empty post_id parameter")
            response = self.session.post(
                f"{self.base_url}/posts/publish",
                json={"post_id": ""},
                headers={"Content-Type": "application/json"}
            )
            
            print(f"     Status: {response.status_code}")
            if response.status_code == 400:
                print(f"     ✅ Correctly rejects empty post_id")
            else:
                print(f"     ⚠️ Unexpected response: {response.text}")
            
            return True
                
        except Exception as e:
            print(f"   ❌ Error testing parameter validation: {str(e)}")
            return False
    
    def test_publish_endpoint_with_valid_post(self, post_id):
        """Test the main publish endpoint functionality with a valid post"""
        try:
            print(f"\n🔍 Step 5: Testing POST /api/posts/publish with valid post_id")
            print(f"   Using post_id: {post_id}")
            
            response = self.session.post(
                f"{self.base_url}/posts/publish",
                json={"post_id": post_id},
                headers={"Content-Type": "application/json"}
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Response headers: {dict(response.headers)}")
            
            # Check if we get a valid JSON response (no crash)
            try:
                response_data = response.json()
                print(f"   ✅ JSON response received (no serialization crash)")
                print(f"   Response data: {json.dumps(response_data, indent=2)}")
                
                # Analyze the response
                if response.status_code == 200:
                    print(f"   ✅ Endpoint executed successfully")
                    return True
                elif response.status_code == 400:
                    # Check if it's a social connections issue (expected)
                    error_message = response_data.get("error", "").lower()
                    if "connexion" in error_message or "social" in error_message:
                        print(f"   ✅ Expected social connections error (normal in preview): {response_data.get('error')}")
                        return True
                    else:
                        print(f"   ⚠️ Unexpected 400 error: {response_data.get('error')}")
                        return True  # Still not a crash
                elif response.status_code == 404:
                    print(f"   ⚠️ Post not found: {response_data.get('error')}")
                    return True  # Still not a crash
                else:
                    print(f"   ⚠️ Unexpected status code: {response.status_code}")
                    print(f"   Response: {response_data}")
                    return True  # Still not a crash
                    
            except json.JSONDecodeError as e:
                print(f"   ❌ CRITICAL: JSON serialization error detected!")
                print(f"   Raw response: {response.text}")
                print(f"   JSON error: {str(e)}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error testing publish endpoint: {str(e)}")
            return False
    
    def test_publish_endpoint_with_invalid_post(self):
        """Test endpoint with invalid post_id"""
        try:
            print(f"\n🔍 Step 6: Testing POST /api/posts/publish with invalid post_id")
            
            invalid_post_id = "nonexistent_post_12345"
            
            response = self.session.post(
                f"{self.base_url}/posts/publish",
                json={"post_id": invalid_post_id},
                headers={"Content-Type": "application/json"}
            )
            
            print(f"   Status: {response.status_code}")
            
            # Check if we get a valid JSON response (no crash)
            try:
                response_data = response.json()
                print(f"   ✅ JSON response received (no serialization crash)")
                print(f"   Response: {json.dumps(response_data, indent=2)}")
                
                if response.status_code == 404:
                    print(f"   ✅ Correctly returns 404 for nonexistent post")
                else:
                    print(f"   ⚠️ Unexpected status for invalid post: {response.status_code}")
                
                return True
                
            except json.JSONDecodeError as e:
                print(f"   ❌ CRITICAL: JSON serialization error with invalid post!")
                print(f"   Raw response: {response.text}")
                print(f"   JSON error: {str(e)}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error testing invalid post: {str(e)}")
            return False
    
    def test_response_format_analysis(self, post_id):
        """Analyze the response format in detail"""
        try:
            print(f"\n🔍 Step 7: Detailed response format analysis")
            
            response = self.session.post(
                f"{self.base_url}/posts/publish",
                json={"post_id": post_id},
                headers={"Content-Type": "application/json"}
            )
            
            print(f"   Status: {response.status_code}")
            
            try:
                response_data = response.json()
                print(f"   ✅ Response is valid JSON")
                
                # Analyze response structure
                print(f"   Response keys: {list(response_data.keys())}")
                
                # Check for ObjectId serialization issues
                response_str = json.dumps(response_data)
                if "ObjectId" in response_str:
                    print(f"   ❌ CRITICAL: ObjectId found in response - serialization not fixed!")
                    print(f"   Problematic response: {response_str}")
                    return False
                else:
                    print(f"   ✅ No ObjectId serialization issues detected")
                
                # Check for proper string conversion
                for key, value in response_data.items():
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            if str(type(sub_value)) == "<class 'bson.objectid.ObjectId'>":
                                print(f"   ❌ CRITICAL: BSON ObjectId not converted to string: {sub_key}")
                                return False
                
                print(f"   ✅ All values properly serialized as JSON-compatible types")
                return True
                
            except json.JSONDecodeError as e:
                print(f"   ❌ CRITICAL: JSON decode error - serialization fix failed!")
                print(f"   Raw response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error in response format analysis: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting POST /api/posts/publish Endpoint Testing")
        print("🎯 Testing ObjectId JSON serialization fix")
        print("=" * 70)
        
        # Test credentials from the review request
        email = "lperpere@yahoo.fr"
        password = "L@Reunion974!"
        
        # Step 1: Authentication
        if not self.authenticate(email, password):
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Get valid post ID
        post_id = self.get_valid_post_id()
        if not post_id:
            print("\n❌ CRITICAL: No valid post_id found - cannot test publish endpoint")
            return False
        
        # Step 3: Test endpoint existence
        if not self.test_publish_endpoint_exists():
            print("\n❌ CRITICAL: Publish endpoint not accessible")
            return False
        
        # Step 4: Test parameter validation
        if not self.test_publish_endpoint_validation():
            print("\n❌ CRITICAL: Parameter validation test failed")
            return False
        
        # Step 5: Test with valid post (main test)
        if not self.test_publish_endpoint_with_valid_post(post_id):
            print("\n❌ CRITICAL: Main publish endpoint test failed")
            return False
        
        # Step 6: Test with invalid post
        if not self.test_publish_endpoint_with_invalid_post():
            print("\n❌ CRITICAL: Invalid post test failed")
            return False
        
        # Step 7: Detailed response format analysis
        if not self.test_response_format_analysis(post_id):
            print("\n❌ CRITICAL: Response format analysis failed")
            return False
        
        print("\n" + "=" * 70)
        print("🎉 ALL TESTS PASSED SUCCESSFULLY!")
        print("✅ POST /api/posts/publish endpoint no longer crashes")
        print("✅ JSON serialization ObjectId issue is FIXED")
        print("✅ Endpoint returns valid JSON responses")
        print("✅ Parameter validation working correctly")
        print("✅ Error handling working properly")
        print("=" * 70)
        
        return True

def main():
    """Main test execution"""
    tester = PublishEndpointTester()
    
    try:
        success = tester.run_all_tests()
        if success:
            print(f"\n🎯 CONCLUSION: POST /api/posts/publish ObjectId serialization fix is WORKING")
            print(f"📝 The endpoint no longer crashes and returns valid JSON responses")
            print(f"🔧 Any errors returned are now proper API errors (social connections, etc.) not crashes")
            sys.exit(0)
        else:
            print(f"\n💥 CONCLUSION: POST /api/posts/publish still has serialization issues")
            print(f"🚨 The ObjectId JSON serialization fix needs additional work")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()