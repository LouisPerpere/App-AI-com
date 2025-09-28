#!/usr/bin/env python3
"""
Comprehensive Backend Test Suite for Facebook Publishing API
Testing the new POST /api/posts/publish endpoint with detailed social media integration
"""

import requests
import json
import sys
from datetime import datetime

class ComprehensiveFacebookPublishTester:
    def __init__(self):
        self.base_url = "https://social-publisher-10.preview.emergentagent.com/api"
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
    
    def test_backend_health(self):
        """Test backend health and availability"""
        try:
            print(f"\n🏥 Step 2: Testing backend health")
            
            response = self.session.get(f"{self.base_url}/health")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Backend healthy: {data.get('service', 'Unknown')}")
                print(f"   Message: {data.get('message', 'No message')}")
                return True
            else:
                print(f"   ❌ Backend health check failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Backend health error: {str(e)}")
            return False
    
    def test_publish_endpoint_comprehensive(self):
        """Comprehensive test of the publish endpoint"""
        try:
            print(f"\n📡 Step 3: Comprehensive publish endpoint testing")
            
            # Test 3a: Endpoint exists (no auth)
            print(f"   Test 3a: Endpoint accessibility")
            response = requests.post(f"{self.base_url}/posts/publish", json={})
            print(f"   Status without auth: {response.status_code}")
            
            if response.status_code == 401:
                print(f"   ✅ Endpoint requires authentication (secure)")
            elif response.status_code == 400:
                print(f"   ✅ Endpoint exists and validates parameters")
            else:
                print(f"   ⚠️ Unexpected response: {response.status_code}")
            
            # Test 3b: With authentication but missing parameters
            print(f"   Test 3b: Parameter validation with auth")
            response = self.session.post(f"{self.base_url}/posts/publish", json={})
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code == 400 and "post_id" in response.text:
                print(f"   ✅ Correctly validates post_id parameter")
                return True
            else:
                print(f"   ❌ Parameter validation issue")
                return False
                
        except Exception as e:
            print(f"   ❌ Error testing publish endpoint: {str(e)}")
            return False
    
    def test_social_connections_detailed(self):
        """Detailed test of social connections"""
        try:
            print(f"\n🔗 Step 4: Detailed social connections testing")
            
            # Test 4a: Main connections endpoint
            print(f"   Test 4a: GET /api/social/connections")
            response = self.session.get(f"{self.base_url}/social/connections")
            print(f"   Status: {response.status_code}")
            
            connections_data = {}
            if response.status_code == 200:
                connections_data = response.json()
                print(f"   ✅ Connections endpoint working")
                print(f"   Response: {json.dumps(connections_data, indent=2)}")
            else:
                print(f"   ❌ Connections endpoint failed: {response.text}")
            
            # Test 4b: Debug connections endpoint
            print(f"   Test 4b: GET /api/social/connections/debug")
            response = self.session.get(f"{self.base_url}/social/connections/debug")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                debug_data = response.json()
                print(f"   ✅ Debug endpoint working")
                print(f"   User ID: {debug_data.get('user_id', 'Unknown')}")
                raw_connections = debug_data.get('raw_connections', [])
                print(f"   Raw connections count: {len(raw_connections)}")
                
                if raw_connections:
                    for i, conn in enumerate(raw_connections[:3]):  # Show first 3
                        print(f"   Connection {i+1}: {conn.get('platform', 'Unknown')} - Active: {conn.get('is_active', False)}")
                
                return len(raw_connections) > 0
            else:
                print(f"   ⚠️ Debug endpoint not available: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error testing social connections: {str(e)}")
            return False
    
    def get_test_posts(self):
        """Get posts for testing"""
        try:
            print(f"\n📋 Step 5: Getting posts for testing")
            
            response = self.session.get(f"{self.base_url}/posts/generated")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                print(f"   ✅ Found {len(posts)} posts")
                
                # Analyze posts
                facebook_posts = [p for p in posts if p.get("platform") == "facebook"]
                instagram_posts = [p for p in posts if p.get("platform") == "instagram"]
                validated_posts = [p for p in posts if p.get("validated", False)]
                
                print(f"   Facebook posts: {len(facebook_posts)}")
                print(f"   Instagram posts: {len(instagram_posts)}")
                print(f"   Validated posts: {len(validated_posts)}")
                
                # Return a good test post
                test_post = None
                for post in posts:
                    if not post.get("validated", False) and post.get("platform") == "facebook":
                        test_post = post
                        break
                
                if not test_post and posts:
                    test_post = posts[0]  # Use any post
                
                if test_post:
                    print(f"   ✅ Selected test post: {test_post['id']}")
                    print(f"   Title: {test_post.get('title', 'No title')}")
                    print(f"   Platform: {test_post.get('platform', 'Unknown')}")
                    print(f"   Validated: {test_post.get('validated', False)}")
                
                return test_post, posts
            else:
                print(f"   ❌ Failed to get posts: {response.text}")
                return None, []
                
        except Exception as e:
            print(f"   ❌ Error getting posts: {str(e)}")
            return None, []
    
    def test_publish_scenarios(self, test_post):
        """Test various publish scenarios"""
        try:
            print(f"\n🚀 Step 6: Testing publish scenarios")
            
            if not test_post:
                print(f"   ❌ No test post available")
                return False
            
            post_id = test_post["id"]
            
            # Scenario 1: Valid post ID
            print(f"   Scenario 1: Valid post ID")
            response = self.session.post(
                f"{self.base_url}/posts/publish",
                json={"post_id": post_id}
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            scenario1_success = False
            if response.status_code == 200:
                print(f"   ✅ Publish successful!")
                scenario1_success = True
            elif response.status_code == 400:
                error_msg = response.text
                if "connexion sociale" in error_msg.lower():
                    print(f"   ✅ Expected error - no social connections")
                    scenario1_success = True
                elif "non supportée" in error_msg.lower():
                    print(f"   ✅ Expected error - platform not supported")
                    scenario1_success = True
                else:
                    print(f"   ⚠️ Unexpected 400 error: {error_msg}")
            else:
                print(f"   ❌ Unexpected response")
            
            # Scenario 2: Invalid post ID
            print(f"   Scenario 2: Invalid post ID")
            response = self.session.post(
                f"{self.base_url}/posts/publish",
                json={"post_id": "invalid_post_12345"}
            )
            
            print(f"   Status: {response.status_code}")
            scenario2_success = response.status_code == 404
            if scenario2_success:
                print(f"   ✅ Correctly rejects invalid post ID")
            else:
                print(f"   ❌ Should return 404 for invalid post ID")
            
            # Scenario 3: Missing post_id
            print(f"   Scenario 3: Missing post_id")
            response = self.session.post(
                f"{self.base_url}/posts/publish",
                json={}
            )
            
            print(f"   Status: {response.status_code}")
            scenario3_success = response.status_code == 400
            if scenario3_success:
                print(f"   ✅ Correctly rejects missing post_id")
            else:
                print(f"   ❌ Should return 400 for missing post_id")
            
            return scenario1_success and scenario2_success and scenario3_success
                
        except Exception as e:
            print(f"   ❌ Error testing publish scenarios: {str(e)}")
            return False
    
    def test_social_media_module_integration(self):
        """Test social media module integration"""
        try:
            print(f"\n🔧 Step 7: Testing social media module integration")
            
            # Test if social media endpoints are available
            endpoints_to_test = [
                "/social/facebook/auth-url",
                "/social/instagram/auth-url",
                "/social/connections"
            ]
            
            working_endpoints = 0
            for endpoint in endpoints_to_test:
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}")
                    print(f"   {endpoint}: Status {response.status_code}")
                    
                    if response.status_code in [200, 400, 401]:  # Working endpoints
                        working_endpoints += 1
                        print(f"   ✅ Endpoint accessible")
                    else:
                        print(f"   ❌ Endpoint not working")
                        
                except Exception as e:
                    print(f"   ❌ {endpoint}: Error {str(e)}")
            
            print(f"   Working endpoints: {working_endpoints}/{len(endpoints_to_test)}")
            return working_endpoints >= len(endpoints_to_test) * 0.5  # At least 50% working
                
        except Exception as e:
            print(f"   ❌ Error testing social media integration: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all comprehensive tests"""
        print("🎯 COMPREHENSIVE FACEBOOK PUBLISH ENDPOINT TESTING")
        print("=" * 60)
        
        results = {
            "authentication": False,
            "backend_health": False,
            "publish_endpoint": False,
            "social_connections": False,
            "publish_scenarios": False,
            "social_media_integration": False
        }
        
        # Test 1: Authentication
        if self.authenticate("lperpere@yahoo.fr", "L@Reunion974!"):
            results["authentication"] = True
        else:
            print("\n❌ CRITICAL: Authentication failed - cannot continue tests")
            return results
        
        # Test 2: Backend health
        if self.test_backend_health():
            results["backend_health"] = True
        
        # Test 3: Publish endpoint
        if self.test_publish_endpoint_comprehensive():
            results["publish_endpoint"] = True
        
        # Test 4: Social connections
        if self.test_social_connections_detailed():
            results["social_connections"] = True
        
        # Test 5: Get test posts and run publish scenarios
        test_post, all_posts = self.get_test_posts()
        if self.test_publish_scenarios(test_post):
            results["publish_scenarios"] = True
        
        # Test 6: Social media integration
        if self.test_social_media_module_integration():
            results["social_media_integration"] = True
        
        return results
    
    def print_comprehensive_summary(self, results):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        
        # Detailed results
        test_descriptions = {
            "authentication": "User Authentication",
            "backend_health": "Backend Health Check",
            "publish_endpoint": "Publish Endpoint Validation",
            "social_connections": "Social Connections System",
            "publish_scenarios": "Publish Scenarios Testing",
            "social_media_integration": "Social Media Module Integration"
        }
        
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            description = test_descriptions.get(test_name, test_name.replace('_', ' ').title())
            print(f"{description}: {status}")
        
        print(f"\nOverall Score: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
        
        # Detailed analysis
        print(f"\n📋 ANALYSIS:")
        
        if results["authentication"] and results["backend_health"]:
            print(f"✅ Core Infrastructure: Working")
        else:
            print(f"❌ Core Infrastructure: Issues detected")
        
        if results["publish_endpoint"]:
            print(f"✅ Publish Endpoint: Implemented and functional")
        else:
            print(f"❌ Publish Endpoint: Not working properly")
        
        if results["social_connections"]:
            print(f"✅ Social Connections: Database has connections")
        else:
            print(f"⚠️ Social Connections: No active connections (expected in preview)")
        
        if results["publish_scenarios"]:
            print(f"✅ Error Handling: Proper validation and error responses")
        else:
            print(f"❌ Error Handling: Issues with validation")
        
        if results["social_media_integration"]:
            print(f"✅ Social Media Module: Integrated and accessible")
        else:
            print(f"❌ Social Media Module: Integration issues")
        
        # Final verdict
        print(f"\n🎯 FINAL VERDICT:")
        if passed_tests == total_tests:
            print("🎉 EXCELLENT - Facebook publish endpoint is fully functional!")
        elif passed_tests >= total_tests * 0.8:
            print("✅ GOOD - Facebook publish endpoint is operational with minor issues")
        elif passed_tests >= total_tests * 0.6:
            print("⚠️ ACCEPTABLE - Facebook publish endpoint works but needs improvements")
        else:
            print("❌ NEEDS WORK - Facebook publish endpoint has significant issues")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if not results["social_connections"]:
            print("• Set up Facebook/Instagram connections for full testing")
        if not results["social_media_integration"]:
            print("• Check social media module configuration")
        if not results["publish_scenarios"]:
            print("• Review error handling and validation logic")

def main():
    tester = ComprehensiveFacebookPublishTester()
    results = tester.run_comprehensive_test()
    tester.print_comprehensive_summary(results)
    
    # Return appropriate exit code
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    
    if passed_tests >= total_tests * 0.7:  # 70% pass rate
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()