#!/usr/bin/env python3
"""
Backend Testing Suite - Simplified ChatGPT OAuth Approach
Testing the simplified Facebook/Instagram OAuth implementation with direct storage approach

Credentials: lperpere@yahoo.fr / L@Reunion974!

TEST OBJECTIVES (Simplified ChatGPT Approach):
1. Test OAuth URLs with corrected state format ({random}|{user_id})
2. Test simplified status endpoint (GET /api/social/connections/status)
3. Test simplified publication endpoints (POST /api/social/facebook/publish-simple, POST /api/social/instagram/publish-simple)
4. Validate clean database (0 connections ready for user testing)
5. Test consistency with current state and ensure corrections are still active
"""

import requests
import json
import sys
import re
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# Configuration
BASE_URL = "https://social-publisher-10.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()
        
    def authenticate(self):
        """Step 1: Authenticate and get JWT token"""
        try:
            print("🔐 Step 1: Authentication")
            response = self.session.post(
                f"{BASE_URL}/auth/login-robust",
                json=TEST_CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                self.log_test("Authentication", True, f"User ID: {self.user_id}")
                return True
            else:
                self.log_test("Authentication", False, 
                            f"Status: {response.status_code}", 
                            response.text[:200])
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, error=str(e))
            return False
    
    def test_clean_initial_state(self):
        """Test 1: Validate clean database (0 connections) - Ready for user testing"""
        try:
            print("🧹 Test 1: Clean Database Validation")
            response = self.session.get(f"{BASE_URL}/debug/social-connections", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                total_connections = data.get("total_connections", 0)
                active_connections = data.get("active_connections", 0)
                facebook_connections = data.get("facebook_connections", 0)
                instagram_connections = data.get("instagram_connections", 0)
                
                if (total_connections == 0 and active_connections == 0 and 
                    facebook_connections == 0 and instagram_connections == 0):
                    self.log_test("Clean Database Validation", True, 
                                "✅ Database ready for user testing: 0 total, 0 active, 0 Facebook, 0 Instagram")
                    return True
                else:
                    self.log_test("Clean Database Validation", False, 
                                f"Database not clean: {total_connections} total, {active_connections} active, {facebook_connections} Facebook, {instagram_connections} Instagram")
                    return False
            else:
                self.log_test("Clean Database Validation", False, 
                            f"Status: {response.status_code}", response.text[:200])
                return False
                
        except Exception as e:
            self.log_test("Clean Database Validation", False, error=str(e))
            return False
    
    def test_facebook_auth_url_state_format(self):
        """Test 2: Test Facebook OAuth URL with corrected state format"""
        try:
            print("📘 Test 2: Facebook OAuth URL with State Correction")
            response = self.session.get(f"{BASE_URL}/social/facebook/auth-url", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get("auth_url", "")
                
                if not auth_url:
                    self.log_test("Facebook OAuth URL State Correction", False, 
                                "No auth_url in response")
                    return False
                
                # Parse URL to extract state parameter
                parsed_url = urlparse(auth_url)
                query_params = parse_qs(parsed_url.query)
                state_param = query_params.get('state', [None])[0]
                
                if not state_param:
                    self.log_test("Facebook OAuth URL State Correction", False, 
                                "No state parameter in URL")
                    return False
                
                # Check if state has the corrected format: {random}|{user_id}
                if '|' in state_param:
                    random_part, user_id_part = state_param.split('|', 1)
                    if user_id_part == self.user_id and len(random_part) > 10:
                        self.log_test("Facebook OAuth URL State Correction", True, 
                                    f"✅ Corrected state format verified: {random_part[:8]}...{user_id_part}")
                        return True
                    else:
                        self.log_test("Facebook OAuth URL State Correction", False, 
                                    f"Invalid user_id in state: expected {self.user_id}, got {user_id_part}")
                        return False
                else:
                    self.log_test("Facebook OAuth URL State Correction", False, 
                                f"State missing pipe separator: {state_param}")
                    return False
                    
            else:
                self.log_test("Facebook OAuth URL State Correction", False, 
                            f"Status: {response.status_code}", response.text[:200])
                return False
                
        except Exception as e:
            self.log_test("Facebook OAuth URL State Correction", False, error=str(e))
            return False
    
    def test_instagram_auth_url_state_format(self):
        """Test 3: Test Instagram OAuth URL with corrected state format"""
        try:
            print("📷 Test 3: Instagram OAuth URL with State Correction")
            response = self.session.get(f"{BASE_URL}/social/instagram/auth-url", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get("auth_url", "")
                
                if not auth_url:
                    self.log_test("Instagram OAuth URL State Correction", False, 
                                "No auth_url in response")
                    return False
                
                # Parse URL to extract state parameter
                parsed_url = urlparse(auth_url)
                query_params = parse_qs(parsed_url.query)
                state_param = query_params.get('state', [None])[0]
                
                if not state_param:
                    self.log_test("Instagram OAuth URL State Correction", False, 
                                "No state parameter in URL")
                    return False
                
                # Check if state has the corrected format: {random}|{user_id}
                if '|' in state_param:
                    random_part, user_id_part = state_param.split('|', 1)
                    if user_id_part == self.user_id and len(random_part) > 10:
                        self.log_test("Instagram OAuth URL State Correction", True, 
                                    f"✅ Corrected state format verified: {random_part[:8]}...{user_id_part}")
                        return True
                    else:
                        self.log_test("Instagram OAuth URL State Correction", False, 
                                    f"Invalid user_id in state: expected {self.user_id}, got {user_id_part}")
                        return False
                else:
                    self.log_test("Instagram OAuth URL State Correction", False, 
                                f"State missing pipe separator: {state_param}")
                    return False
                    
            else:
                self.log_test("Instagram OAuth URL State Correction", False, 
                            f"Status: {response.status_code}", response.text[:200])
                return False
                
        except Exception as e:
            self.log_test("Instagram OAuth URL State Correction", False, error=str(e))
            return False
    
    def test_simplified_status_endpoint(self):
        """Test 4: Test simplified status endpoint (GET /api/social/connections/status)"""
        try:
            print("📊 Test 4: Simplified Status Endpoint")
            response = self.session.get(f"{BASE_URL}/social/connections/status", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for simplified response format
                expected_fields = ["facebook", "instagram"]
                has_all_fields = all(field in data for field in expected_fields)
                
                if has_all_fields:
                    facebook_status = data.get("facebook", {})
                    instagram_status = data.get("instagram", {})
                    
                    # Verify simple format structure
                    facebook_connected = facebook_status.get("connected", False)
                    instagram_connected = instagram_status.get("connected", False)
                    
                    self.log_test("Simplified Status Endpoint", True, 
                                f"✅ Simple format verified - Facebook: {facebook_connected}, Instagram: {instagram_connected}")
                    return True
                else:
                    self.log_test("Simplified Status Endpoint", False, 
                                f"Missing expected fields. Got: {list(data.keys())}")
                    return False
                    
            else:
                self.log_test("Simplified Status Endpoint", False, 
                            f"Status: {response.status_code}", response.text[:200])
                return False
                
        except Exception as e:
            self.log_test("Simplified Status Endpoint", False, error=str(e))
            return False
    
    def test_simplified_facebook_publish_endpoint(self):
        """Test 5: Test simplified Facebook publication endpoint"""
        try:
            print("📘 Test 5: Simplified Facebook Publication Endpoint")
            
            test_data = {
                "text": "Test publication Facebook - Approche simplifiée",
                "image_url": "https://example.com/test-image.jpg"
            }
            
            response = self.session.post(
                f"{BASE_URL}/social/facebook/publish-simple", 
                json=test_data, 
                timeout=30
            )
            
            # Should fail with no connections, but endpoint should exist and respond properly
            if response.status_code in [400, 401, 403]:
                data = response.json()
                error_message = data.get("error", "").lower()
                
                if "connexion" in error_message or "token" in error_message or "facebook" in error_message:
                    self.log_test("Simplified Facebook Publication Endpoint", True, 
                                f"✅ Endpoint exists and properly rejects: {data.get('error', 'No connection error')}")
                    return True
                else:
                    self.log_test("Simplified Facebook Publication Endpoint", False, 
                                f"Unexpected error message: {data.get('error', 'Unknown error')}")
                    return False
            elif response.status_code == 404:
                self.log_test("Simplified Facebook Publication Endpoint", False, 
                            "Endpoint not found - simplified publication not implemented")
                return False
            else:
                self.log_test("Simplified Facebook Publication Endpoint", False, 
                            f"Unexpected status: {response.status_code}, Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log_test("Simplified Facebook Publication Endpoint", False, error=str(e))
            return False
    
    def test_simplified_instagram_publish_endpoint(self):
        """Test 6: Test simplified Instagram publication endpoint"""
        try:
            print("📷 Test 6: Simplified Instagram Publication Endpoint")
            
            test_data = {
                "text": "Test publication Instagram - Approche simplifiée",
                "image_url": "https://example.com/test-image.jpg"
            }
            
            response = self.session.post(
                f"{BASE_URL}/social/instagram/publish-simple", 
                json=test_data, 
                timeout=30
            )
            
            # Should fail with no connections, but endpoint should exist and respond properly
            if response.status_code in [400, 401, 403]:
                data = response.json()
                error_message = data.get("error", "").lower()
                
                if "connexion" in error_message or "token" in error_message or "instagram" in error_message:
                    self.log_test("Simplified Instagram Publication Endpoint", True, 
                                f"✅ Endpoint exists and properly rejects: {data.get('error', 'No connection error')}")
                    return True
                else:
                    self.log_test("Simplified Instagram Publication Endpoint", False, 
                                f"Unexpected error message: {data.get('error', 'Unknown error')}")
                    return False
            elif response.status_code == 404:
                self.log_test("Simplified Instagram Publication Endpoint", False, 
                            "Endpoint not found - simplified publication not implemented")
                return False
            else:
                self.log_test("Simplified Instagram Publication Endpoint", False, 
                            f"Unexpected status: {response.status_code}, Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log_test("Simplified Instagram Publication Endpoint", False, error=str(e))
            return False
    
    def test_consistency_with_current_state(self):
        """Test 7: Test consistency with current state and ensure corrections are still active"""
        try:
            print("🔗 Test 7: Consistency with Current State")
            response = self.session.get(f"{BASE_URL}/social/connections", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                connections = data.get("connections", [])
                
                # Should return 0 connections since database is clean
                if len(connections) == 0:
                    self.log_test("Consistency with Current State", True, 
                                "✅ System consistent: 0 connections, ready for user reconnection with corrected state")
                    return True
                else:
                    self.log_test("Consistency with Current State", False, 
                                f"Expected 0 connections, got {len(connections)} - may interfere with user testing")
                    return False
            else:
                self.log_test("Consistency with Current State", False, 
                            f"Status: {response.status_code}", response.text[:200])
                return False
                
        except Exception as e:
            self.log_test("Consistency with Current State", False, error=str(e))
            return False
    
    def run_all_tests(self):
        """Run all OAuth state parameter correction tests"""
        print("🎯 TESTING OAUTH STATE PARAMETER CORRECTIONS")
        print("=" * 70)
        print(f"Backend URL: {BASE_URL}")
        print(f"Test User: {TEST_CREDENTIALS['email']}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 70)
        print()
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed - cannot continue tests")
            return False
        
        # Step 2: Test clean initial state
        self.test_clean_initial_state()
        
        # Step 3: Test Facebook auth URL state format
        self.test_facebook_auth_url_state_format()
        
        # Step 4: Test Instagram auth URL state format  
        self.test_instagram_auth_url_state_format()
        
        # Step 5: Test Facebook callback state validation
        self.test_facebook_callback_state_validation()
        
        # Step 6: Test social connections consistency
        self.test_social_connections_consistency()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print(f"\n🎯 RESULTS: {passed}/{total} tests passed ({(passed/total*100):.1f}%)")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED - OAuth state parameter corrections are working!")
            print("✅ URLs OAuth avec state format {random}|{user_id}")
            print("✅ Callbacks qui acceptent ce format")
            print("✅ Plus d'erreur de validation state")
            return True
        else:
            print(f"\n🚨 {total - passed} TESTS FAILED - OAuth state parameter corrections need attention")
            failed_tests = [r['test'] for r in self.test_results if not r['success']]
            print(f"Failed tests: {', '.join(failed_tests)}")
            return False

def main():
    """Main test execution"""
    tester = BackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ OAuth state parameter corrections validation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ OAuth state parameter corrections validation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()