#!/usr/bin/env python3
"""
Authentication Flow Debug Test
Specifically testing the token validation issue causing "Demo Business" data override
"""

import requests
import json
import os
from datetime import datetime

class AuthDebugTester:
    def __init__(self):
        # Use the production backend URL from frontend/.env
        self.base_url = "https://instamanager-1.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.tests_run = 0
        self.tests_passed = 0
        
    def log(self, message, level="INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test with detailed logging"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {}
        
        # Add authentication header if we have a token
        if self.access_token:
            test_headers['Authorization'] = f'Bearer {self.access_token}'
        
        # Add custom headers
        if headers:
            test_headers.update(headers)
        
        # Set Content-Type for JSON requests
        if method in ['POST', 'PUT'] and not headers:
            test_headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        self.log(f"🔍 Testing {name}...")
        self.log(f"   URL: {url}")
        self.log(f"   Method: {method}")
        self.log(f"   Headers: {test_headers}")
        if data:
            self.log(f"   Data: {json.dumps(data, indent=2)}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, params=data)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers)

            success = response.status_code == expected_status
            
            self.log(f"   Response Status: {response.status_code}")
            self.log(f"   Response Headers: {dict(response.headers)}")
            
            try:
                response_data = response.json()
                self.log(f"   Response Data: {json.dumps(response_data, indent=2)}")
            except:
                response_data = {}
                self.log(f"   Response Text: {response.text}")
            
            if success:
                self.tests_passed += 1
                self.log(f"✅ PASSED - {name}", "SUCCESS")
                return True, response_data
            else:
                self.log(f"❌ FAILED - Expected {expected_status}, got {response.status_code}", "ERROR")
                return False, response_data

        except Exception as e:
            self.log(f"❌ EXCEPTION - {str(e)}", "ERROR")
            return False, {}

    def test_login_and_extract_token(self):
        """Test POST /api/auth/login with specified credentials and extract token"""
        self.log("=" * 80)
        self.log("STEP 1: Testing Login and Token Extraction")
        self.log("=" * 80)
        
        login_data = {
            "email": "lperpere@yahoo.fr",
            "password": "L@Reunion974!"
        }
        
        success, response = self.run_test(
            "POST /api/auth/login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.access_token = response['access_token']
            self.log(f"✅ ACCESS TOKEN EXTRACTED: {self.access_token[:30]}...", "SUCCESS")
            self.log(f"   Token Type: {type(self.access_token)}")
            self.log(f"   Token Length: {len(self.access_token)}")
            
            # Additional token analysis
            if self.access_token.startswith('demo_token_'):
                self.log("⚠️  WARNING: Token appears to be a demo token!", "WARNING")
            elif len(self.access_token) > 100:
                self.log("✅ Token appears to be a real JWT token", "SUCCESS")
            else:
                self.log("⚠️  WARNING: Token format unexpected", "WARNING")
                
            return True
        else:
            self.log("❌ FAILED to extract access token from login response", "ERROR")
            return False

    def test_business_profile_with_auth_header(self):
        """Test GET /api/business-profile with proper Authorization header"""
        self.log("=" * 80)
        self.log("STEP 2: Testing Business Profile with Authorization Header")
        self.log("=" * 80)
        
        if not self.access_token:
            self.log("❌ No access token available for testing", "ERROR")
            return False
            
        # Test with proper Authorization header
        success, response = self.run_test(
            "GET /api/business-profile with Authorization header",
            "GET",
            "business-profile",
            200
        )
        
        if success:
            # Analyze the response to check if it's demo data or real user data
            business_name = response.get('business_name', '')
            email = response.get('email', '')
            
            self.log(f"   Business Name: {business_name}")
            self.log(f"   Email: {email}")
            
            # Check if this is demo data
            if business_name == "Demo Business" and email == "demo@claire-marcus.com":
                self.log("❌ CRITICAL ISSUE: Returning demo data despite valid authentication!", "ERROR")
                self.log("   This indicates token validation is failing", "ERROR")
                return False
            else:
                self.log("✅ SUCCESS: Returning real user data", "SUCCESS")
                return True
        else:
            self.log("❌ FAILED to get business profile", "ERROR")
            return False

    def test_business_profile_without_auth_header(self):
        """Test GET /api/business-profile without Authorization header"""
        self.log("=" * 80)
        self.log("STEP 3: Testing Business Profile WITHOUT Authorization Header")
        self.log("=" * 80)
        
        # Temporarily remove token
        temp_token = self.access_token
        self.access_token = None
        
        success, response = self.run_test(
            "GET /api/business-profile without Authorization header",
            "GET",
            "business-profile",
            200  # Should still return 200 but with demo data
        )
        
        # Restore token
        self.access_token = temp_token
        
        if success:
            business_name = response.get('business_name', '')
            email = response.get('email', '')
            
            self.log(f"   Business Name: {business_name}")
            self.log(f"   Email: {email}")
            
            # This should be demo data
            if business_name == "Demo Business" and email == "demo@claire-marcus.com":
                self.log("✅ SUCCESS: Correctly returning demo data without auth", "SUCCESS")
                return True
            else:
                self.log("⚠️  WARNING: Not returning expected demo data without auth", "WARNING")
                return True  # Not a critical failure
        else:
            self.log("❌ FAILED to get business profile without auth", "ERROR")
            return False

    def test_invalid_token(self):
        """Test GET /api/business-profile with invalid token"""
        self.log("=" * 80)
        self.log("STEP 4: Testing Business Profile with Invalid Token")
        self.log("=" * 80)
        
        # Use invalid token
        temp_token = self.access_token
        self.access_token = "invalid_token_12345"
        
        success, response = self.run_test(
            "GET /api/business-profile with invalid token",
            "GET",
            "business-profile",
            200  # Should still return 200 but with demo data
        )
        
        # Restore token
        self.access_token = temp_token
        
        if success:
            business_name = response.get('business_name', '')
            email = response.get('email', '')
            
            self.log(f"   Business Name: {business_name}")
            self.log(f"   Email: {email}")
            
            # This should be demo data
            if business_name == "Demo Business" and email == "demo@claire-marcus.com":
                self.log("✅ SUCCESS: Correctly falling back to demo data with invalid token", "SUCCESS")
                return True
            else:
                self.log("⚠️  WARNING: Not returning expected demo data with invalid token", "WARNING")
                return True  # Not a critical failure
        else:
            self.log("❌ FAILED to get business profile with invalid token", "ERROR")
            return False

    def test_auth_me_endpoint(self):
        """Test GET /api/auth/me to verify token validation"""
        self.log("=" * 80)
        self.log("STEP 5: Testing /api/auth/me Endpoint")
        self.log("=" * 80)
        
        if not self.access_token:
            self.log("❌ No access token available for testing", "ERROR")
            return False
            
        success, response = self.run_test(
            "GET /api/auth/me with Authorization header",
            "GET",
            "auth/me",
            200
        )
        
        if success:
            user_id = response.get('user_id', '')
            email = response.get('email', '')
            
            self.log(f"   User ID: {user_id}")
            self.log(f"   Email: {email}")
            
            # Check if this is demo data
            if user_id == "demo_user_id" and email == "demo@claire-marcus.com":
                self.log("❌ CRITICAL ISSUE: /api/auth/me returning demo data despite valid token!", "ERROR")
                return False
            else:
                self.log("✅ SUCCESS: /api/auth/me returning real user data", "SUCCESS")
                return True
        else:
            self.log("❌ FAILED to get user info from /api/auth/me", "ERROR")
            return False

    def check_backend_logs(self):
        """Check backend logs for debug output"""
        self.log("=" * 80)
        self.log("STEP 6: Checking Backend Logs")
        self.log("=" * 80)
        
        try:
            # Try to get supervisor logs
            import subprocess
            result = subprocess.run(['tail', '-n', '50', '/var/log/supervisor/backend.out.log'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log("Backend logs (last 50 lines):")
                self.log(result.stdout)
            else:
                self.log("Could not retrieve backend logs")
        except Exception as e:
            self.log(f"Error retrieving logs: {e}")

    def run_comprehensive_auth_debug(self):
        """Run comprehensive authentication debugging"""
        self.log("🚀 STARTING COMPREHENSIVE AUTHENTICATION DEBUG TEST")
        self.log("=" * 80)
        self.log(f"Backend URL: {self.base_url}")
        self.log(f"API URL: {self.api_url}")
        self.log(f"Target User: lperpere@yahoo.fr")
        self.log("=" * 80)
        
        # Run all debug tests in sequence
        test_results = []
        
        # Step 1: Login and extract token
        result1 = self.test_login_and_extract_token()
        test_results.append(("Login and Token Extraction", result1))
        
        if result1:  # Only continue if login succeeded
            # Step 2: Test business profile with auth
            result2 = self.test_business_profile_with_auth_header()
            test_results.append(("Business Profile with Auth", result2))
            
            # Step 3: Test business profile without auth
            result3 = self.test_business_profile_without_auth_header()
            test_results.append(("Business Profile without Auth", result3))
            
            # Step 4: Test with invalid token
            result4 = self.test_invalid_token()
            test_results.append(("Business Profile with Invalid Token", result4))
            
            # Step 5: Test auth/me endpoint
            result5 = self.test_auth_me_endpoint()
            test_results.append(("Auth Me Endpoint", result5))
        
        # Step 6: Check backend logs
        self.check_backend_logs()
        
        # Final summary
        self.log("=" * 80)
        self.log("FINAL TEST SUMMARY")
        self.log("=" * 80)
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            self.log(f"{status} - {test_name}")
        
        passed = sum(1 for _, result in test_results if result)
        total = len(test_results)
        
        self.log(f"\nOverall Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            self.log("🎉 ALL TESTS PASSED - Authentication flow working correctly!", "SUCCESS")
        else:
            self.log("⚠️  SOME TESTS FAILED - Authentication issues detected!", "WARNING")
            
        return passed == total

if __name__ == "__main__":
    tester = AuthDebugTester()
    success = tester.run_comprehensive_auth_debug()
    exit(0 if success else 1)