#!/usr/bin/env python3
"""
Backend Compatibility Test for App.js White Screen Fix
Testing critical backend endpoints that the corrected App.js depends on
"""

import requests
import json
import os
import time
from datetime import datetime

# Configuration - Using the correct backend URL from frontend/.env
BACKEND_URL = "https://social-ai-planner-2.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials as specified in review request
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class AppJSBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()
    
    def test_health_check(self):
        """Test 1: Health Check - Verify GET /api/health endpoint"""
        print("🏥 TEST 1: Health Check")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{API_BASE}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                service = data.get("service")
                
                self.log_result(
                    "Health Check", 
                    True, 
                    f"Backend is healthy. Status: {status}, Service: {service}"
                )
                return True
            else:
                self.log_result(
                    "Health Check", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Health Check", False, error=str(e))
            return False
    
    def test_backend_url_configuration(self):
        """Test 2: Backend URL Configuration - Confirm backend is accessible"""
        print("🌐 TEST 2: Backend URL Configuration")
        print("=" * 50)
        
        try:
            # Test root endpoint
            response = self.session.get(BACKEND_URL, timeout=10)
            
            if response.status_code == 200:
                # Check if it's actually serving the backend API
                try:
                    data = response.json()
                    if "Claire et Marcus API" in str(data) or "message" in data:
                        self.log_result(
                            "Backend URL Configuration", 
                            True, 
                            f"Backend accessible at {BACKEND_URL}. Response: {data.get('message', 'API running')}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Backend URL Configuration", 
                            False, 
                            f"URL accessible but not serving expected API content",
                            f"Response: {str(data)[:100]}..."
                        )
                        return False
                except:
                    # Not JSON, might be HTML
                    content = response.text[:200]
                    if "api" in content.lower() or "backend" in content.lower():
                        self.log_result(
                            "Backend URL Configuration", 
                            True, 
                            f"Backend accessible at {BACKEND_URL} (HTML response)"
                        )
                        return True
                    else:
                        self.log_result(
                            "Backend URL Configuration", 
                            False, 
                            f"URL accessible but serving unexpected content",
                            f"Content preview: {content}"
                        )
                        return False
            else:
                self.log_result(
                    "Backend URL Configuration", 
                    False, 
                    f"Backend not accessible. Status: {response.status_code}",
                    response.text[:200]
                )
                return False
                
        except Exception as e:
            self.log_result("Backend URL Configuration", False, error=str(e))
            return False
    
    def test_authentication_flow(self):
        """Test 3: Authentication Flow - Test POST /api/auth/login-robust"""
        print("🔐 TEST 3: Authentication Flow")
        print("=" * 50)
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login-robust", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                token_type = data.get("token_type")
                email = data.get("email")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                self.log_result(
                    "Authentication Flow", 
                    True, 
                    f"Successfully authenticated as {email}, User ID: {self.user_id}, Token type: {token_type}"
                )
                return True
            else:
                self.log_result(
                    "Authentication Flow", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Authentication Flow", False, error=str(e))
            return False
    
    def test_token_validation(self):
        """Test 4: Token Validation - Test that JWT tokens work with protected endpoints"""
        print("🎫 TEST 4: Token Validation")
        print("=" * 50)
        
        if not self.access_token:
            self.log_result(
                "Token Validation", 
                False, 
                "No access token available from authentication test"
            )
            return False
        
        try:
            # Test /api/auth/me endpoint (if available)
            response = self.session.get(f"{API_BASE}/auth/me", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                user_id = data.get("user_id")
                email = data.get("email")
                
                self.log_result(
                    "Token Validation (/api/auth/me)", 
                    True, 
                    f"Token validated successfully. User: {email}, ID: {user_id}"
                )
                
                # Test another protected endpoint
                return self.test_protected_endpoint_access()
                
            elif response.status_code == 404:
                # /api/auth/me not implemented, test other protected endpoint
                self.log_result(
                    "Token Validation (/api/auth/me)", 
                    False, 
                    "Endpoint not implemented (404)",
                    "Testing alternative protected endpoint..."
                )
                return self.test_protected_endpoint_access()
            else:
                self.log_result(
                    "Token Validation", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Token Validation", False, error=str(e))
            return False
    
    def test_protected_endpoint_access(self):
        """Test protected endpoint access with JWT token"""
        try:
            # Test /api/business-profile endpoint
            response = self.session.get(f"{API_BASE}/business-profile", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                self.log_result(
                    "Token Validation (business-profile)", 
                    True, 
                    f"Protected endpoint accessible with JWT token. Business profile retrieved."
                )
                return True
            else:
                # Try /api/content/pending
                response = self.session.get(f"{API_BASE}/content/pending", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    content_count = len(data.get("content", []))
                    
                    self.log_result(
                        "Token Validation (content/pending)", 
                        True, 
                        f"Protected endpoint accessible with JWT token. Content items: {content_count}"
                    )
                    return True
                else:
                    self.log_result(
                        "Token Validation (protected endpoints)", 
                        False, 
                        f"Protected endpoints not accessible. Status: {response.status_code}",
                        response.text
                    )
                    return False
                
        except Exception as e:
            self.log_result("Token Validation (protected endpoints)", False, error=str(e))
            return False
    
    def test_cors_configuration(self):
        """Test 5: CORS Configuration - Verify CORS headers for frontend compatibility"""
        print("🌍 TEST 5: CORS Configuration")
        print("=" * 50)
        
        try:
            # Test preflight request
            headers = {
                'Origin': 'https://social-ai-planner-2.preview.emergentagent.com',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'authorization,content-type'
            }
            
            response = self.session.options(f"{API_BASE}/auth/login-robust", headers=headers, timeout=10)
            
            # Check CORS headers
            cors_origin = response.headers.get('Access-Control-Allow-Origin')
            cors_methods = response.headers.get('Access-Control-Allow-Methods')
            cors_headers = response.headers.get('Access-Control-Allow-Headers')
            
            cors_configured = (
                cors_origin == '*' or 
                'social-ai-manager-7.preview.emergentagent.com' in str(cors_origin)
            )
            
            if cors_configured:
                self.log_result(
                    "CORS Configuration", 
                    True, 
                    f"CORS properly configured. Origin: {cors_origin}, Methods: {cors_methods}"
                )
                return True
            else:
                self.log_result(
                    "CORS Configuration", 
                    False, 
                    f"CORS may not be properly configured",
                    f"Origin: {cors_origin}, Methods: {cors_methods}, Headers: {cors_headers}"
                )
                return False
                
        except Exception as e:
            self.log_result("CORS Configuration", False, error=str(e))
            return False
    
    def test_api_error_handling(self):
        """Test 6: API Error Handling - Verify proper error responses"""
        print("⚠️ TEST 6: API Error Handling")
        print("=" * 50)
        
        try:
            # Test invalid credentials
            response = self.session.post(f"{API_BASE}/auth/login-robust", json={
                "email": "invalid@example.com",
                "password": "wrongpassword"
            }, timeout=10)
            
            if response.status_code == 401:
                try:
                    data = response.json()
                    error_message = data.get("error") or data.get("detail")
                    
                    if error_message:
                        self.log_result(
                            "API Error Handling", 
                            True, 
                            f"Proper error handling for invalid credentials. Error: {error_message}"
                        )
                        return True
                    else:
                        self.log_result(
                            "API Error Handling", 
                            False, 
                            "Error response doesn't contain proper error message",
                            f"Response: {data}"
                        )
                        return False
                except:
                    self.log_result(
                        "API Error Handling", 
                        False, 
                        "Error response is not valid JSON",
                        response.text
                    )
                    return False
            else:
                self.log_result(
                    "API Error Handling", 
                    False, 
                    f"Expected 401 for invalid credentials, got {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("API Error Handling", False, error=str(e))
            return False
    
    def run_all_tests(self):
        """Run all App.js backend compatibility tests"""
        print("🚀 APP.JS BACKEND COMPATIBILITY TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_EMAIL}")
        print(f"Context: Testing backend endpoints for App.js white screen fix")
        print("=" * 60)
        print()
        
        # Run tests in sequence
        tests = [
            self.test_health_check,
            self.test_backend_url_configuration,
            self.test_authentication_flow,
            self.test_token_validation,
            self.test_cors_configuration,
            self.test_api_error_handling
        ]
        
        for test in tests:
            if not test():
                print("❌ Test failed, continuing with remaining tests...")
            print()
        
        # Summary
        print("📋 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Detailed results
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
            if result['error']:
                print(f"   Error: {result['error']}")
        
        print()
        print("🎯 APP.JS BACKEND COMPATIBILITY TESTING COMPLETED")
        
        return success_rate >= 80  # High threshold for critical compatibility

if __name__ == "__main__":
    tester = AppJSBackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("✅ Overall testing: SUCCESS")
        exit(0)
    else:
        print("❌ Overall testing: FAILED")
        exit(1)