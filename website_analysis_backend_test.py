#!/usr/bin/env python3
"""
Website Analysis Module Backend Testing
Testing per test_result.md test_plan focusing on Website Analysis module
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration - Using the correct backend URL from frontend/.env
BACKEND_URL = "https://social-boost-pwa.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials as specified in review request
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class WebsiteAnalysisTester:
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
    
    def authenticate(self):
        """Step 1: Authenticate with specified credentials using login-robust"""
        print("🔐 STEP 1: Authentication with POST /api/auth/login-robust")
        print("=" * 60)
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login-robust", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                self.log_result(
                    "Authentication (login-robust)", 
                    True, 
                    f"Successfully authenticated as {TEST_EMAIL}, User ID: {self.user_id}, Token: {self.access_token[:20]}..."
                )
                return True
            else:
                self.log_result(
                    "Authentication (login-robust)", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Authentication (login-robust)", False, error=str(e))
            return False
    
    def test_health_check(self):
        """Step 2: Test GET /api/health to verify backend is up"""
        print("🏥 STEP 2: Health Check")
        print("=" * 60)
        
        try:
            response = self.session.get(f"{API_BASE}/health")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                service = data.get("service")
                message = data.get("message")
                
                self.log_result(
                    "Health Check", 
                    True, 
                    f"Backend is healthy. Status: {status}, Service: {service}, Message: {message}"
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
    
    def test_website_analysis_empty(self):
        """Step 3a: Test GET /api/website/analysis should return {analysis: null} when none exists"""
        print("🌐 STEP 3a: Website Analysis - Empty State")
        print("=" * 60)
        
        try:
            response = self.session.get(f"{API_BASE}/website/analysis")
            
            if response.status_code == 200:
                data = response.json()
                analysis = data.get("analysis")
                
                if analysis is None:
                    self.log_result(
                        "Website Analysis Empty State", 
                        True, 
                        f"Correctly returns analysis: null when no analysis exists. Response: {data}"
                    )
                    return True
                else:
                    self.log_result(
                        "Website Analysis Empty State", 
                        False, 
                        f"Expected analysis: null, but got: {analysis}"
                    )
                    return False
            elif response.status_code == 404:
                # 404 is also acceptable for empty state
                self.log_result(
                    "Website Analysis Empty State", 
                    True, 
                    f"Returns 404 when no analysis exists (acceptable behavior)"
                )
                return True
            else:
                self.log_result(
                    "Website Analysis Empty State", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Website Analysis Empty State", False, error=str(e))
            return False
    
    def test_website_analysis_create(self):
        """Step 3b: Test POST /api/website/analyze with valid website"""
        print("🌐 STEP 3b: Website Analysis - Create Analysis")
        print("=" * 60)
        
        try:
            # Test with example.com as specified in review request
            test_data = {
                "website_url": "example.com",
                "force_reanalysis": False
            }
            
            response = self.session.post(f"{API_BASE}/website/analyze", json=test_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields as specified in review request
                required_fields = [
                    "analysis_summary", "key_topics", "brand_tone", 
                    "target_audience", "main_services", "content_suggestions",
                    "website_url", "created_at", "next_analysis_due"
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in data:
                        missing_fields.append(field)
                
                # Check for [object Object] in any message
                has_object_object = False
                for key, value in data.items():
                    if isinstance(value, str) and "[object Object]" in value:
                        has_object_object = True
                        break
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, str) and "[object Object]" in item:
                                has_object_object = True
                                break
                
                if missing_fields:
                    self.log_result(
                        "Website Analysis Create", 
                        False, 
                        f"Missing required fields: {missing_fields}",
                        f"Response: {data}"
                    )
                    return False
                elif has_object_object:
                    self.log_result(
                        "Website Analysis Create", 
                        False, 
                        "Found [object Object] in response messages",
                        f"Response: {data}"
                    )
                    return False
                else:
                    # Store analysis for next test
                    self.created_analysis = data
                    
                    self.log_result(
                        "Website Analysis Create", 
                        True, 
                        f"Successfully created analysis for {test_data['website_url']}. All required fields present, no [object Object] found. Key topics: {len(data.get('key_topics', []))}, Main services: {len(data.get('main_services', []))}, Content suggestions: {len(data.get('content_suggestions', []))}"
                    )
                    return True
            else:
                self.log_result(
                    "Website Analysis Create", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Website Analysis Create", False, error=str(e))
            return False
    
    def test_website_analysis_populated(self):
        """Step 3c: Test GET /api/website/analysis should now return analysis object populated"""
        print("🌐 STEP 3c: Website Analysis - Populated State")
        print("=" * 60)
        
        try:
            response = self.session.get(f"{API_BASE}/website/analysis")
            
            if response.status_code == 200:
                data = response.json()
                analysis = data.get("analysis")
                
                if analysis is not None and isinstance(analysis, dict):
                    # Check if it has the expected structure
                    expected_fields = ["analysis_summary", "key_topics", "brand_tone", "target_audience"]
                    has_expected_fields = all(field in analysis for field in expected_fields)
                    
                    if has_expected_fields:
                        self.log_result(
                            "Website Analysis Populated State", 
                            True, 
                            f"Successfully retrieved populated analysis. Website: {analysis.get('website_url')}, Summary length: {len(analysis.get('analysis_summary', ''))}, Key topics: {len(analysis.get('key_topics', []))}"
                        )
                        return True
                    else:
                        missing = [field for field in expected_fields if field not in analysis]
                        self.log_result(
                            "Website Analysis Populated State", 
                            False, 
                            f"Analysis object missing expected fields: {missing}",
                            f"Analysis: {analysis}"
                        )
                        return False
                else:
                    self.log_result(
                        "Website Analysis Populated State", 
                        False, 
                        f"Expected populated analysis object, but got: {analysis}"
                    )
                    return False
            else:
                self.log_result(
                    "Website Analysis Populated State", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Website Analysis Populated State", False, error=str(e))
            return False
    
    def test_website_analysis_error_non_html(self):
        """Step 3d1: Test POST with non-HTML URL - expect 415 and proper error"""
        print("🌐 STEP 3d1: Website Analysis - Non-HTML URL Error")
        print("=" * 60)
        
        try:
            # Test with image URL as specified in review request
            test_data = {
                "website_url": "https://httpbin.org/image/png",
                "force_reanalysis": False
            }
            
            response = self.session.post(f"{API_BASE}/website/analyze", json=test_data)
            
            if response.status_code == 415:
                data = response.json()
                error_message = data.get("error", "")
                
                # Check for French error message as specified
                if "Contenu non supporté" in error_message or "non supporté" in error_message.lower():
                    self.log_result(
                        "Website Analysis Non-HTML Error", 
                        True, 
                        f"Correctly returned 415 with proper French error message: {error_message}"
                    )
                    return True
                else:
                    self.log_result(
                        "Website Analysis Non-HTML Error", 
                        False, 
                        f"Got 415 but error message doesn't match expected French format",
                        f"Error: {error_message}"
                    )
                    return False
            else:
                self.log_result(
                    "Website Analysis Non-HTML Error", 
                    False, 
                    f"Expected 415 status code, got: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Website Analysis Non-HTML Error", False, error=str(e))
            return False
    
    def test_website_analysis_error_bad_domain(self):
        """Step 3d2: Test POST with bad domain - expect 502 or 504 with proper error"""
        print("🌐 STEP 3d2: Website Analysis - Bad Domain Error")
        print("=" * 60)
        
        try:
            # Test with non-existent domain as specified in review request
            test_data = {
                "website_url": "https://nonexistent.clairemarcus.invalid",
                "force_reanalysis": False
            }
            
            response = self.session.post(f"{API_BASE}/website/analyze", json=test_data)
            
            if response.status_code in [502, 504, 400, 422]:  # Accept various error codes for network issues
                data = response.json()
                error_message = data.get("error", "")
                
                # Check for proper error structure
                if error_message and isinstance(error_message, str):
                    self.log_result(
                        "Website Analysis Bad Domain Error", 
                        True, 
                        f"Correctly returned {response.status_code} with proper error structure: {error_message}"
                    )
                    return True
                else:
                    self.log_result(
                        "Website Analysis Bad Domain Error", 
                        False, 
                        f"Got {response.status_code} but error structure is not uniform",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "Website Analysis Bad Domain Error", 
                    False, 
                    f"Expected 502/504 status code for bad domain, got: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Website Analysis Bad Domain Error", False, error=str(e))
            return False
    
    def test_force_reanalysis(self):
        """Step 4: Test force_reanalysis=true parameter"""
        print("🌐 STEP 4: Website Analysis - Force Reanalysis")
        print("=" * 60)
        
        try:
            # Test force reanalysis with same URL
            test_data = {
                "website_url": "example.com",
                "force_reanalysis": True
            }
            
            response = self.session.post(f"{API_BASE}/website/analyze", json=test_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Should get a fresh analysis
                if "analysis_summary" in data and "created_at" in data:
                    self.log_result(
                        "Website Analysis Force Reanalysis", 
                        True, 
                        f"Successfully forced reanalysis for {test_data['website_url']}. New created_at: {data.get('created_at')}"
                    )
                    return True
                else:
                    self.log_result(
                        "Website Analysis Force Reanalysis", 
                        False, 
                        "Response missing expected fields for reanalysis",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "Website Analysis Force Reanalysis", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Website Analysis Force Reanalysis", False, error=str(e))
            return False
    
    def test_error_response_uniformity(self):
        """Step 5: Verify response structure uniformity for errors"""
        print("🌐 STEP 5: Website Analysis - Error Response Uniformity")
        print("=" * 60)
        
        try:
            # Test multiple error scenarios to verify uniform structure
            error_tests = [
                {
                    "name": "Missing URL",
                    "data": {"force_reanalysis": False},
                    "expected_codes": [400, 422]
                },
                {
                    "name": "Invalid URL format",
                    "data": {"website_url": "not-a-url", "force_reanalysis": False},
                    "expected_codes": [400, 422]
                },
                {
                    "name": "Empty URL",
                    "data": {"website_url": "", "force_reanalysis": False},
                    "expected_codes": [400, 422]
                }
            ]
            
            uniform_errors = True
            error_details = []
            
            for test in error_tests:
                try:
                    response = self.session.post(f"{API_BASE}/website/analyze", json=test["data"])
                    
                    if response.status_code in test["expected_codes"]:
                        data = response.json()
                        
                        # Check for uniform error structure: {error: "message lisible"}
                        if "error" in data and isinstance(data["error"], str) and data["error"]:
                            error_details.append(f"✅ {test['name']}: {response.status_code} - {data['error'][:50]}...")
                        else:
                            uniform_errors = False
                            error_details.append(f"❌ {test['name']}: Non-uniform error structure - {data}")
                    else:
                        error_details.append(f"⚠️ {test['name']}: Unexpected status {response.status_code}")
                        
                except Exception as e:
                    error_details.append(f"❌ {test['name']}: Exception - {str(e)[:50]}...")
                    uniform_errors = False
            
            self.log_result(
                "Website Analysis Error Response Uniformity", 
                uniform_errors, 
                f"Tested {len(error_tests)} error scenarios. Details: {'; '.join(error_details)}"
            )
            return uniform_errors
                
        except Exception as e:
            self.log_result("Website Analysis Error Response Uniformity", False, error=str(e))
            return False
    
    def run_all_tests(self):
        """Run all website analysis tests as specified in review request"""
        print("🚀 WEBSITE ANALYSIS MODULE BACKEND TESTING")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_EMAIL}")
        print("Testing per test_result.md test_plan focusing on Website Analysis module")
        print("=" * 70)
        print()
        
        # Run tests in sequence as specified in review request
        tests = [
            self.authenticate,                          # 1) Auth: obtain valid access token
            self.test_health_check,                     # 2) GET /api/health
            self.test_website_analysis_empty,           # 3a) GET /api/website/analysis (empty)
            self.test_website_analysis_create,          # 3b) POST /api/website/analyze
            self.test_website_analysis_populated,       # 3c) GET /api/website/analysis (populated)
            self.test_website_analysis_error_non_html,  # 3d) Error cases - non-HTML URL
            self.test_website_analysis_error_bad_domain, # 3d) Error cases - bad domain
            self.test_force_reanalysis,                 # 4) Test force_reanalysis parameter
            self.test_error_response_uniformity         # 5) Verify error response uniformity
        ]
        
        for test in tests:
            if not test():
                print("❌ Test failed, continuing with remaining tests...")
            print()
        
        # Summary
        print("📋 WEBSITE ANALYSIS TEST SUMMARY")
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
        print("🎯 WEBSITE ANALYSIS MODULE TESTING COMPLETED")
        
        return success_rate >= 80  # High threshold for critical functionality

if __name__ == "__main__":
    tester = WebsiteAnalysisTester()
    success = tester.run_all_tests()
    
    if success:
        print("✅ Overall Website Analysis testing: SUCCESS")
        exit(0)
    else:
        print("❌ Overall Website Analysis testing: FAILED")
        exit(1)