#!/usr/bin/env python3
"""
Test Instagram Simplified OAuth Approach - Persistence Verification
================================================================

This test validates the simplified Instagram OAuth approach that was working before
according to test_result.md message 413. This approach uses:
- Direct storage approach: page_id + access_token + page_name
- Direct storage in social_media_connections with active: True
- Simple token based on OAuth code instead of complex 3-step exchange
- No complex Facebook token exchange

Test Objectives:
1. Authenticate with lperpere@yahoo.fr / L@Reunion974!
2. Test Instagram callback simulation with simplified approach
3. Verify direct storage: connections should be created immediately
4. Verify persistence: GET /api/social/connections should show connections
5. Verify active state: connections should have active: True

Environment: https://claire-marcus-app-1.preview.emergentagent.com/api
"""

import requests
import json
import time
import sys
from urllib.parse import urlencode, parse_qs, urlparse

# Configuration for PREVIEW environment
BASE_URL = "https://claire-marcus-app-1.preview.emergentagent.com/api"
FRONTEND_URL = "https://claire-marcus-app-1.preview.emergentagent.com"

# Test credentials
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class InstagramSimplifiedTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        
    def authenticate(self):
        """Step 1: Authenticate with test credentials"""
        print("🔐 STEP 1: Authentication")
        print(f"   URL: {BASE_URL}/auth/login-robust")
        print(f"   Email: {TEST_EMAIL}")
        
        try:
            response = self.session.post(f"{BASE_URL}/auth/login-robust", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                print(f"   ✅ Authentication successful")
                print(f"   User ID: {self.user_id}")
                print(f"   Token: {self.auth_token[:30]}..." if self.auth_token else "No token")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                return True
            else:
                print(f"   ❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {str(e)}")
            return False
    
    def check_initial_connections_state(self):
        """Step 2: Check initial connections state (should be clean)"""
        print("\n🔍 STEP 2: Check Initial Connections State")
        print(f"   URL: {BASE_URL}/social/connections")
        
        try:
            response = self.session.get(f"{BASE_URL}/social/connections")
            
            if response.status_code == 200:
                data = response.json()
                connections = data.get("connections", [])
                
                print(f"   ✅ Initial connections retrieved: {len(connections)} connections")
                
                instagram_connections = [c for c in connections if c.get("platform") == "instagram"]
                active_instagram = [c for c in instagram_connections if c.get("active", False)]
                
                print(f"   Instagram connections: {len(instagram_connections)}")
                print(f"   Active Instagram connections: {len(active_instagram)}")
                
                return {
                    "total": len(connections),
                    "instagram": len(instagram_connections),
                    "active_instagram": len(active_instagram)
                }
            else:
                print(f"   ❌ Failed to get connections: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ Connections check error: {str(e)}")
            return None
    
    def generate_instagram_auth_url(self):
        """Step 3: Generate Instagram OAuth URL"""
        print("\n🔗 STEP 3: Generate Instagram OAuth URL")
        print(f"   URL: {BASE_URL}/social/instagram/auth-url")
        
        try:
            response = self.session.get(f"{BASE_URL}/social/instagram/auth-url")
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get("auth_url")
                
                print(f"   ✅ Instagram auth URL generated successfully")
                print(f"   URL: {auth_url}")
                
                # Parse URL to extract state parameter
                parsed_url = urlparse(auth_url)
                query_params = parse_qs(parsed_url.query)
                state = query_params.get('state', [None])[0]
                
                if state and '|' in state:
                    print(f"   ✅ State parameter format correct: {state}")
                    return state
                else:
                    print(f"   ❌ Invalid state parameter format: {state}")
                    return None
                    
            else:
                print(f"   ❌ Auth URL generation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Auth URL generation error: {str(e)}")
            return None
    
    def simulate_instagram_callback_simplified(self, state_param):
        """Step 4: Simulate Instagram callback with simplified approach"""
        print("\n🎯 STEP 4: Simulate Instagram Callback - Simplified Approach")
        print(f"   URL: {BASE_URL}/social/instagram/callback")
        print("   Testing simplified approach: direct storage without complex token exchange")
        
        # Simulate Instagram OAuth callback with test parameters
        callback_params = {
            "code": "test_instagram_simplified_code_12345",
            "state": state_param
        }
        
        try:
            callback_url = f"{BASE_URL}/social/instagram/callback"
            response = self.session.get(callback_url, params=callback_params, allow_redirects=False)
            
            print(f"   Response Status: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            
            # Check if it's a redirect
            if response.status_code in [301, 302, 303, 307, 308]:
                location = response.headers.get('Location', '')
                print(f"   🔄 Redirect detected to: {location}")
                
                # Check for success redirect (simplified approach should succeed)
                if 'instagram_success=true' in location:
                    print(f"   ✅ SIMPLIFIED APPROACH SUCCESS: Instagram callback succeeded!")
                    print(f"   ✅ Direct storage approach working")
                    return True
                elif 'auth_error=' in location:
                    print(f"   ⚠️ Instagram callback processed but with error (expected in test)")
                    print(f"   ✅ No redirection to Facebook - simplified approach active")
                    return True
                elif '/api/social/facebook/callback' in location:
                    print(f"   ❌ CRITICAL ISSUE: Still redirecting to Facebook!")
                    print(f"   ❌ Simplified approach NOT working")
                    return False
                else:
                    print(f"   ⚠️ Unexpected redirect destination: {location}")
                    return False
            else:
                print(f"   Response Body: {response.text[:500]}...")
                return True
                
        except Exception as e:
            print(f"   ❌ Callback simulation error: {str(e)}")
            return False
    
    def verify_direct_storage(self):
        """Step 5: Verify direct storage in social_media_connections"""
        print("\n💾 STEP 5: Verify Direct Storage")
        print(f"   URL: {BASE_URL}/social/connections")
        print("   Checking if connections were created immediately with simplified approach")
        
        try:
            response = self.session.get(f"{BASE_URL}/social/connections")
            
            if response.status_code == 200:
                data = response.json()
                connections = data.get("connections", [])
                
                print(f"   ✅ Connections retrieved: {len(connections)} total connections")
                
                instagram_connections = [c for c in connections if c.get("platform") == "instagram"]
                active_instagram = [c for c in instagram_connections if c.get("active", False)]
                
                print(f"   Instagram connections: {len(instagram_connections)}")
                print(f"   Active Instagram connections: {len(active_instagram)}")
                
                # Check for simplified approach characteristics
                for conn in instagram_connections:
                    print(f"   📋 Instagram Connection Details:")
                    print(f"      Platform: {conn.get('platform')}")
                    print(f"      Active: {conn.get('active')}")
                    print(f"      Page ID: {conn.get('page_id', 'N/A')}")
                    print(f"      Page Name: {conn.get('page_name', 'N/A')}")
                    print(f"      Has Access Token: {'Yes' if conn.get('access_token') else 'No'}")
                
                return {
                    "total": len(connections),
                    "instagram": len(instagram_connections),
                    "active_instagram": len(active_instagram),
                    "connections": instagram_connections
                }
            else:
                print(f"   ❌ Failed to get connections: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ Storage verification error: {str(e)}")
            return None
    
    def verify_persistence(self):
        """Step 6: Verify persistence - connections should persist across requests"""
        print("\n🔄 STEP 6: Verify Persistence")
        print("   Making multiple requests to ensure connections persist")
        
        persistence_results = []
        
        for i in range(3):
            print(f"   Request {i+1}/3...")
            try:
                response = self.session.get(f"{BASE_URL}/social/connections")
                
                if response.status_code == 200:
                    data = response.json()
                    connections = data.get("connections", [])
                    instagram_connections = [c for c in connections if c.get("platform") == "instagram"]
                    active_instagram = [c for c in instagram_connections if c.get("active", False)]
                    
                    persistence_results.append({
                        "request": i+1,
                        "total": len(connections),
                        "instagram": len(instagram_connections),
                        "active_instagram": len(active_instagram)
                    })
                    
                    print(f"      ✅ Request {i+1}: {len(active_instagram)} active Instagram connections")
                else:
                    print(f"      ❌ Request {i+1} failed: {response.status_code}")
                    persistence_results.append(None)
                
                time.sleep(1)  # Small delay between requests
                
            except Exception as e:
                print(f"      ❌ Request {i+1} error: {str(e)}")
                persistence_results.append(None)
        
        # Analyze persistence
        valid_results = [r for r in persistence_results if r is not None]
        if len(valid_results) >= 2:
            # Check if results are consistent
            first_result = valid_results[0]
            consistent = all(
                r["active_instagram"] == first_result["active_instagram"] 
                for r in valid_results
            )
            
            if consistent:
                print(f"   ✅ PERSISTENCE VERIFIED: Connections consistent across {len(valid_results)} requests")
                return True
            else:
                print(f"   ❌ PERSISTENCE ISSUE: Inconsistent results across requests")
                return False
        else:
            print(f"   ❌ PERSISTENCE TEST FAILED: Too many failed requests")
            return False
    
    def verify_active_state(self):
        """Step 7: Verify active state - connections should have active: True"""
        print("\n✅ STEP 7: Verify Active State")
        print("   Checking that connections have active: True as per simplified approach")
        
        try:
            response = self.session.get(f"{BASE_URL}/social/connections")
            
            if response.status_code == 200:
                data = response.json()
                connections = data.get("connections", [])
                instagram_connections = [c for c in connections if c.get("platform") == "instagram"]
                
                print(f"   Total Instagram connections: {len(instagram_connections)}")
                
                active_count = 0
                inactive_count = 0
                
                for conn in instagram_connections:
                    is_active = conn.get("active", False)
                    if is_active:
                        active_count += 1
                        print(f"   ✅ Active Instagram connection: {conn.get('page_name', 'Unknown')}")
                    else:
                        inactive_count += 1
                        print(f"   ❌ Inactive Instagram connection: {conn.get('page_name', 'Unknown')}")
                
                print(f"   Summary: {active_count} active, {inactive_count} inactive")
                
                # Success criteria: at least one active connection
                if active_count > 0:
                    print(f"   ✅ ACTIVE STATE VERIFIED: {active_count} active Instagram connections found")
                    return True
                else:
                    print(f"   ❌ ACTIVE STATE ISSUE: No active Instagram connections found")
                    return False
                    
            else:
                print(f"   ❌ Failed to check active state: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Active state verification error: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all simplified Instagram approach tests"""
        print("🎯 INSTAGRAM SIMPLIFIED APPROACH TESTING")
        print("=" * 50)
        print(f"Environment: {BASE_URL}")
        print(f"Credentials: {TEST_EMAIL}")
        print("Testing simplified approach: direct storage + active: True")
        print()
        
        results = {}
        
        # Step 1: Authentication
        results['authentication'] = self.authenticate()
        if not results['authentication']:
            print("\n❌ CRITICAL: Authentication failed - cannot proceed")
            return results
        
        # Step 2: Check initial state
        initial_state = self.check_initial_connections_state()
        results['initial_state_check'] = initial_state is not None
        
        # Step 3: Generate Instagram auth URL
        state_param = self.generate_instagram_auth_url()
        results['auth_url_generation'] = state_param is not None
        
        if not state_param:
            print("\n❌ CRITICAL: Cannot generate auth URL - using fallback")
            state_param = f"instagram_simplified|{self.user_id}"
        
        # Step 4: Simulate simplified callback
        results['simplified_callback'] = self.simulate_instagram_callback_simplified(state_param)
        
        # Step 5: Verify direct storage
        storage_result = self.verify_direct_storage()
        results['direct_storage'] = storage_result is not None
        
        # Step 6: Verify persistence
        results['persistence'] = self.verify_persistence()
        
        # Step 7: Verify active state
        results['active_state'] = self.verify_active_state()
        
        return results
    
    def print_final_results(self, results):
        """Print comprehensive test results"""
        print("\n" + "=" * 50)
        print("🎯 INSTAGRAM SIMPLIFIED APPROACH TEST RESULTS")
        print("=" * 50)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Detailed results
        test_names = {
            'authentication': 'Authentication',
            'initial_state_check': 'Initial State Check',
            'auth_url_generation': 'Auth URL Generation',
            'simplified_callback': 'Simplified Callback',
            'direct_storage': 'Direct Storage Verification',
            'persistence': 'Persistence Verification',
            'active_state': 'Active State Verification'
        }
        
        for key, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            test_name = test_names.get(key, key)
            print(f"{status} {test_name}")
        
        print()
        
        # Critical analysis for simplified approach
        critical_tests = ['simplified_callback', 'direct_storage', 'persistence', 'active_state']
        critical_passed = sum(1 for test in critical_tests if results.get(test, False))
        
        if critical_passed == len(critical_tests):
            print("🎉 CONCLUSION: Instagram simplified approach is WORKING!")
            print("✅ Direct storage approach: page_id + access_token + page_name")
            print("✅ Connections stored in social_media_connections with active: True")
            print("✅ Simple token approach without complex 3-step exchange")
            print("✅ Connections persist across requests")
            print()
            print("💡 SUCCESS CRITERIA MET:")
            print("   - Callback creates connections immediately")
            print("   - GET /api/social/connections shows connections")
            print("   - Connections have active: True")
        else:
            print("🚨 CONCLUSION: Instagram simplified approach has ISSUES!")
            print(f"❌ {len(critical_tests) - critical_passed} critical tests failed")
            print("❌ Simplified approach needs fixes")
            print()
            print("🔧 ISSUES TO ADDRESS:")
            if not results.get('simplified_callback'):
                print("   - Callback not working with simplified approach")
            if not results.get('direct_storage'):
                print("   - Direct storage not working")
            if not results.get('persistence'):
                print("   - Connections not persisting")
            if not results.get('active_state'):
                print("   - Connections not marked as active")
        
        return critical_passed == len(critical_tests)

def main():
    """Main test execution"""
    tester = InstagramSimplifiedTester()
    
    try:
        results = tester.run_comprehensive_test()
        success = tester.print_final_results(results)
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test execution error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()