#!/usr/bin/env python3
"""
Authentication Flow Testing for Claire et Marcus
Tests the complete authentication workflow: register → login → auth verification
"""

import requests
import json
import sys
from datetime import datetime

class AuthenticationTester:
    def __init__(self, base_url=None):
        # Use production backend URL from review request
        if base_url:
            self.base_url = base_url
        else:
            # Production backend URL mentioned in review request
            self.base_url = "https://claire-marcus-api.onrender.com"
            
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test_result(self, test_name, success, details):
        """Log test result for summary"""
        self.test_results.append({
            'name': test_name,
            'success': success,
            'details': details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        # Add authentication header if we have a token
        if self.access_token:
            test_headers['Authorization'] = f'Bearer {self.access_token}'
        
        # Add custom headers
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

            print(f"   Response Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:300]}...")
                    self.log_test_result(name, True, f"Status {response.status_code}: {str(response_data)[:100]}...")
                    return True, response_data
                except:
                    print(f"   Response: {response.text[:200]}...")
                    self.log_test_result(name, True, f"Status {response.status_code}: {response.text[:100]}...")
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    self.log_test_result(name, False, f"Expected {expected_status}, got {response.status_code}: {str(error_data)[:100]}...")
                except:
                    print(f"   Error: {response.text}")
                    self.log_test_result(name, False, f"Expected {expected_status}, got {response.status_code}: {response.text[:100]}...")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout (30s)")
            self.log_test_result(name, False, "Request timeout after 30 seconds")
            return False, {}
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Failed - Connection error: {str(e)}")
            self.log_test_result(name, False, f"Connection error: {str(e)[:100]}...")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.log_test_result(name, False, f"Error: {str(e)[:100]}...")
            return False, {}

    def test_backend_health(self):
        """Test if backend is responding"""
        print("\n🏥 Testing Backend Health...")
        success, response = self.run_test(
            "Backend Health Check",
            "GET",
            "health",
            200
        )
        return success

    def test_user_registration(self):
        """Test user registration with realistic data"""
        print("\n👤 Testing User Registration...")
        
        # Use realistic test data as per instructions
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        user_data = {
            "email": f"claire.test.{timestamp}@example.com",
            "password": "SecurePassword123!",
            "first_name": "Claire",
            "last_name": "Test",
            "business_name": "Claire Test Business"
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        if success:
            # Extract user info from response
            if 'user_id' in response:
                self.user_id = response['user_id']
                print(f"   User ID: {self.user_id}")
            if 'access_token' in response:
                self.access_token = response['access_token']
                print(f"   Access Token: {self.access_token[:20]}...")
            if 'refresh_token' in response:
                self.refresh_token = response['refresh_token']
                print(f"   Refresh Token: {self.refresh_token[:20]}...")
        
        return success

    def test_user_login(self):
        """Test user login with the registered credentials"""
        print("\n🔐 Testing User Login...")
        
        # Use the same credentials from registration
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        login_data = {
            "email": f"claire.test.{timestamp}@example.com",
            "password": "SecurePassword123!"
        }
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success:
            # Extract tokens from response
            if 'access_token' in response:
                self.access_token = response['access_token']
                print(f"   Access Token: {self.access_token[:20]}...")
            if 'refresh_token' in response:
                self.refresh_token = response['refresh_token']
                print(f"   Refresh Token: {self.refresh_token[:20]}...")
            if 'user_id' in response:
                self.user_id = response['user_id']
                print(f"   User ID: {self.user_id}")
        
        return success

    def test_auth_verification(self):
        """Test authentication verification with GET /api/auth/me"""
        print("\n✅ Testing Authentication Verification...")
        
        if not self.access_token:
            print("❌ Skipping - No access token available")
            self.log_test_result("Authentication Verification", False, "No access token available")
            return False
        
        success, response = self.run_test(
            "Authentication Verification (/api/auth/me)",
            "GET",
            "auth/me",
            200
        )
        
        if success:
            # Verify response contains user data
            expected_fields = ['user_id', 'email']
            missing_fields = []
            for field in expected_fields:
                if field not in response:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"⚠️  Missing expected fields: {missing_fields}")
            else:
                print("✅ All expected user fields present")
        
        return success

    def test_complete_auth_workflow(self):
        """Test the complete authentication workflow"""
        print("\n🔄 Testing Complete Authentication Workflow...")
        
        workflow_success = True
        
        # Step 1: Health check
        if not self.test_backend_health():
            print("❌ Backend health check failed - cannot proceed")
            return False
        
        # Step 2: Registration
        if not self.test_user_registration():
            print("❌ Registration failed - cannot proceed with login")
            workflow_success = False
        
        # Step 3: Login (only if registration succeeded or we have credentials)
        if workflow_success:
            if not self.test_user_login():
                print("❌ Login failed - cannot proceed with auth verification")
                workflow_success = False
        
        # Step 4: Auth verification (only if login succeeded)
        if workflow_success:
            if not self.test_auth_verification():
                print("❌ Auth verification failed")
                workflow_success = False
        
        return workflow_success

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("🎯 AUTHENTICATION TESTING SUMMARY")
        print("="*60)
        print(f"Backend URL: {self.base_url}")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['name']}")
            if not result['success']:
                print(f"   └─ {result['details']}")
        
        print("\n🔍 CRITICAL FINDINGS:")
        failed_tests = [r for r in self.test_results if not r['success']]
        if not failed_tests:
            print("✅ All authentication endpoints working correctly")
            print("✅ Complete registration → login → auth verification workflow functional")
        else:
            print("❌ Authentication issues detected:")
            for test in failed_tests:
                print(f"   • {test['name']}: {test['details']}")
        
        print("\n" + "="*60)

def main():
    """Main test execution"""
    print("🚀 Starting Authentication Flow Testing for Claire et Marcus")
    print("="*60)
    
    # Test with production backend
    tester = AuthenticationTester()
    
    # Run complete workflow test
    workflow_success = tester.test_complete_auth_workflow()
    
    # Print summary
    tester.print_summary()
    
    # Return appropriate exit code
    return 0 if workflow_success else 1

if __name__ == "__main__":
    sys.exit(main())