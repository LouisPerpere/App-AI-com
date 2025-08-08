#!/usr/bin/env python3
"""
Extended Authentication Testing for Claire et Marcus
Tests edge cases, error scenarios, and CORS issues
"""

import requests
import json
import sys
from datetime import datetime

class ExtendedAuthTester:
    def __init__(self, base_url=None):
        if base_url:
            self.base_url = base_url
        else:
            self.base_url = "https://claire-marcus-api.onrender.com"
            
        self.api_url = f"{self.base_url}/api"
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
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)

            print(f"   Response Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    self.log_test_result(name, True, f"Status {response.status_code}")
                    return True, response_data
                except:
                    self.log_test_result(name, True, f"Status {response.status_code}")
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    self.log_test_result(name, False, f"Expected {expected_status}, got {response.status_code}")
                except:
                    print(f"   Error: {response.text}")
                    self.log_test_result(name, False, f"Expected {expected_status}, got {response.status_code}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.log_test_result(name, False, f"Error: {str(e)[:100]}...")
            return False, {}

    def test_cors_headers(self):
        """Test CORS headers are present"""
        print("\n🌐 Testing CORS Configuration...")
        
        try:
            response = requests.options(f"{self.api_url}/auth/register", timeout=30)
            print(f"   OPTIONS Response Status: {response.status_code}")
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
                'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
            }
            
            print("   CORS Headers:")
            for header, value in cors_headers.items():
                print(f"     {header}: {value}")
            
            # Check if CORS is properly configured
            if cors_headers['Access-Control-Allow-Origin']:
                self.tests_passed += 1
                self.log_test_result("CORS Headers", True, "CORS headers present")
                return True
            else:
                self.log_test_result("CORS Headers", False, "Missing CORS headers")
                return False
                
        except Exception as e:
            print(f"❌ CORS test failed: {e}")
            self.log_test_result("CORS Headers", False, f"Error: {str(e)}")
            return False

    def test_invalid_registration_data(self):
        """Test registration with invalid data"""
        print("\n❌ Testing Invalid Registration Data...")
        
        # Test missing email
        success1, _ = self.run_test(
            "Registration - Missing Email",
            "POST",
            "auth/register",
            422,  # Validation error expected
            data={"password": "SecurePassword123!", "first_name": "Test"}
        )
        
        # Test invalid email format
        success2, _ = self.run_test(
            "Registration - Invalid Email Format",
            "POST",
            "auth/register",
            422,  # Validation error expected
            data={"email": "invalid-email", "password": "SecurePassword123!"}
        )
        
        # Test missing password
        success3, _ = self.run_test(
            "Registration - Missing Password",
            "POST",
            "auth/register",
            422,  # Validation error expected
            data={"email": "test@example.com"}
        )
        
        return success1 or success2 or success3  # At least one validation should work

    def test_invalid_login_data(self):
        """Test login with invalid credentials"""
        print("\n🔐 Testing Invalid Login Data...")
        
        # Test with non-existent user
        success1, _ = self.run_test(
            "Login - Non-existent User",
            "POST",
            "auth/login",
            401,  # Unauthorized expected
            data={"email": "nonexistent@example.com", "password": "WrongPassword123!"}
        )
        
        # Test with missing password
        success2, _ = self.run_test(
            "Login - Missing Password",
            "POST",
            "auth/login",
            422,  # Validation error expected
            data={"email": "test@example.com"}
        )
        
        return success1 or success2

    def test_auth_me_without_token(self):
        """Test /auth/me without authentication token"""
        print("\n🔒 Testing Auth/Me Without Token...")
        
        success, _ = self.run_test(
            "Auth/Me - No Token",
            "GET",
            "auth/me",
            401,  # Unauthorized expected
            headers={}  # No Authorization header
        )
        
        return success

    def test_auth_me_with_invalid_token(self):
        """Test /auth/me with invalid token"""
        print("\n🔒 Testing Auth/Me With Invalid Token...")
        
        success, _ = self.run_test(
            "Auth/Me - Invalid Token",
            "GET",
            "auth/me",
            401,  # Unauthorized expected
            headers={"Authorization": "Bearer invalid_token_123"}
        )
        
        return success

    def test_response_format_consistency(self):
        """Test that responses have consistent format"""
        print("\n📋 Testing Response Format Consistency...")
        
        # Test registration response format
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        success, reg_response = self.run_test(
            "Registration Response Format",
            "POST",
            "auth/register",
            200,
            data={
                "email": f"format.test.{timestamp}@example.com",
                "password": "SecurePassword123!",
                "first_name": "Format",
                "last_name": "Test"
            }
        )
        
        if success:
            # Check required fields in registration response
            required_fields = ['access_token', 'refresh_token', 'user_id', 'email']
            missing_fields = [field for field in required_fields if field not in reg_response]
            
            if missing_fields:
                print(f"⚠️  Registration response missing fields: {missing_fields}")
                self.log_test_result("Registration Format", False, f"Missing fields: {missing_fields}")
                return False
            else:
                print("✅ Registration response has all required fields")
                self.log_test_result("Registration Format", True, "All required fields present")
                return True
        
        return False

    def test_production_vs_demo_mode(self):
        """Test if backend is running in demo mode vs production mode"""
        print("\n🎭 Testing Demo vs Production Mode...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        success, response = self.run_test(
            "Demo Mode Detection",
            "POST",
            "auth/register",
            200,
            data={
                "email": f"demo.test.{timestamp}@example.com",
                "password": "SecurePassword123!",
                "first_name": "Demo",
                "last_name": "Test"
            }
        )
        
        if success:
            # Check if response indicates demo mode
            message = response.get('message', '')
            if 'demo mode' in message.lower():
                print("🎭 Backend is running in DEMO MODE")
                self.log_test_result("Demo Mode", True, "Backend running in demo mode")
                return True
            else:
                print("🏭 Backend is running in PRODUCTION MODE")
                self.log_test_result("Production Mode", True, "Backend running in production mode")
                return True
        
        return False

    def run_all_tests(self):
        """Run all extended authentication tests"""
        print("🧪 Running Extended Authentication Tests...")
        
        tests = [
            self.test_cors_headers,
            self.test_invalid_registration_data,
            self.test_invalid_login_data,
            self.test_auth_me_without_token,
            self.test_auth_me_with_invalid_token,
            self.test_response_format_consistency,
            self.test_production_vs_demo_mode
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {e}")
                self.log_test_result(test.__name__, False, f"Exception: {str(e)}")

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("🧪 EXTENDED AUTHENTICATION TESTING SUMMARY")
        print("="*60)
        print(f"Backend URL: {self.base_url}")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['name']}: {result['details']}")
        
        print("\n🔍 KEY FINDINGS:")
        failed_tests = [r for r in self.test_results if not r['success']]
        if not failed_tests:
            print("✅ All extended authentication tests passed")
        else:
            print("⚠️  Some edge cases need attention:")
            for test in failed_tests:
                print(f"   • {test['name']}: {test['details']}")
        
        print("\n" + "="*60)

def main():
    """Main test execution"""
    print("🚀 Starting Extended Authentication Testing for Claire et Marcus")
    print("="*60)
    
    tester = ExtendedAuthTester()
    tester.run_all_tests()
    tester.print_summary()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())