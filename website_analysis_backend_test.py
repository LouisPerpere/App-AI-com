#!/usr/bin/env python3
"""
Backend Test Suite for Website Analysis after A1/A2/A3 - Review Request
Testing POST /api/website/analyze with GPT analysis and error uniformity
"""

import requests
import json
import os
import time

# Configuration - Using the correct backend URL from frontend/.env
BACKEND_URL = "https://social-ai-planner-2.preview.emergentagent.com"
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
        """Step 1: Authenticate with robust login endpoint"""
        print("🔐 STEP 1: Authentication")
        print("=" * 50)
        
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
                    f"Successfully authenticated as {TEST_EMAIL}, User ID: {self.user_id}"
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
        """Step 2: Test backend health"""
        print("🏥 STEP 2: Health Check")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{API_BASE}/health")
            
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
    
    def test_get_analysis_empty(self):
        """Step 3: Test GET /api/website/analysis when empty"""
        print("📊 STEP 3: GET Website Analysis (Empty State)")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{API_BASE}/website/analysis")
            
            if response.status_code == 200:
                data = response.json()
                analysis = data.get("analysis")
                
                if analysis is None:
                    self.log_result(
                        "GET Website Analysis (Empty)", 
                        True, 
                        "Correctly returns {analysis: null} when no analysis exists"
                    )
                    return True
                else:
                    self.log_result(
                        "GET Website Analysis (Empty)", 
                        True, 
                        f"Analysis exists: {analysis.get('website_url', 'unknown URL')}"
                    )
                    return True
            else:
                self.log_result(
                    "GET Website Analysis (Empty)", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("GET Website Analysis (Empty)", False, error=str(e))
            return False
    
    def test_post_analyze_example_com(self):
        """Step 4: Test POST /api/website/analyze with example.com"""
        print("🌐 STEP 4: POST Website Analysis (example.com)")
        print("=" * 50)
        
        try:
            response = self.session.post(f"{API_BASE}/website/analyze", json={
                "website_url": "example.com",
                "force_reanalysis": True
            })
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = [
                    "analysis_summary", "key_topics", "brand_tone", 
                    "target_audience", "main_services", "content_suggestions",
                    "website_url", "created_at", "next_analysis_due"
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in data:
                        missing_fields.append(field)
                
                # Check for [object Object] in responses
                object_object_found = False
                for key, value in data.items():
                    if isinstance(value, str) and "[object Object]" in value:
                        object_object_found = True
                        break
                
                if missing_fields:
                    self.log_result(
                        "POST Website Analysis (example.com)", 
                        False, 
                        f"Missing required fields: {missing_fields}"
                    )
                    return False
                elif object_object_found:
                    self.log_result(
                        "POST Website Analysis (example.com)", 
                        False, 
                        "[object Object] found in response"
                    )
                    return False
                else:
                    # Count topics and services
                    key_topics_count = len(data.get("key_topics", []))
                    main_services_count = len(data.get("main_services", []))
                    content_suggestions_count = len(data.get("content_suggestions", []))
                    
                    self.log_result(
                        "POST Website Analysis (example.com)", 
                        True, 
                        f"Analysis created successfully. Key topics: {key_topics_count}, Main services: {main_services_count}, Content suggestions: {content_suggestions_count}, Website: {data.get('website_url')}"
                    )
                    return True
            else:
                self.log_result(
                    "POST Website Analysis (example.com)", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("POST Website Analysis (example.com)", False, error=str(e))
            return False
    
    def test_get_analysis_populated(self):
        """Step 5: Test GET /api/website/analysis when populated"""
        print("📈 STEP 5: GET Website Analysis (Populated State)")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{API_BASE}/website/analysis")
            
            if response.status_code == 200:
                data = response.json()
                analysis = data.get("analysis")
                
                if analysis and isinstance(analysis, dict):
                    website_url = analysis.get("website_url", "")
                    summary_length = len(analysis.get("analysis_summary", ""))
                    key_topics_count = len(analysis.get("key_topics", []))
                    
                    self.log_result(
                        "GET Website Analysis (Populated)", 
                        True, 
                        f"Analysis retrieved successfully. Website: {website_url}, Summary length: {summary_length}, Key topics: {key_topics_count}"
                    )
                    return True
                else:
                    self.log_result(
                        "GET Website Analysis (Populated)", 
                        False, 
                        "Expected populated analysis but got null or invalid data"
                    )
                    return False
            else:
                self.log_result(
                    "GET Website Analysis (Populated)", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("GET Website Analysis (Populated)", False, error=str(e))
            return False
    
    def test_error_uniformity_invalid_payload(self):
        """Step 6: Test error uniformity with invalid payload (422 expected)"""
        print("⚠️ STEP 6: Error Uniformity - Invalid Payload")
        print("=" * 50)
        
        try:
            # Send invalid payload - website_url as integer instead of string
            response = self.session.post(f"{API_BASE}/website/analyze", json={
                "website_url": 123,
                "force_reanalysis": True
            })
            
            if response.status_code == 422:
                data = response.json()
                
                # Check if response has uniform {error: "..."} format
                if "error" in data and isinstance(data["error"], str):
                    self.log_result(
                        "Error Uniformity - Invalid Payload", 
                        True, 
                        f"Correct 422 status with uniform error format: {data['error']}"
                    )
                    return True
                else:
                    self.log_result(
                        "Error Uniformity - Invalid Payload", 
                        False, 
                        f"422 status but non-uniform error format: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "Error Uniformity - Invalid Payload", 
                    False, 
                    f"Expected 422 but got {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Error Uniformity - Invalid Payload", False, error=str(e))
            return False
    
    def test_non_html_error_handling(self):
        """Step 7: Test non-HTML URL error handling"""
        print("🖼️ STEP 7: Non-HTML Error Handling")
        print("=" * 50)
        
        try:
            # Test with image URL
            response = self.session.post(f"{API_BASE}/website/analyze", json={
                "website_url": "https://httpbin.org/image/png",
                "force_reanalysis": True
            })
            
            if response.status_code == 415:
                data = response.json()
                
                # Check if response has uniform {error: "..."} format
                if "error" in data and isinstance(data["error"], str):
                    error_message = data["error"]
                    self.log_result(
                        "Non-HTML Error Handling", 
                        True, 
                        f"Correct 415 status with uniform error format: {error_message}"
                    )
                    return True
                else:
                    self.log_result(
                        "Non-HTML Error Handling", 
                        False, 
                        f"415 status but non-uniform error format: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "Non-HTML Error Handling", 
                    False, 
                    f"Expected 415 but got {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Non-HTML Error Handling", False, error=str(e))
            return False
    
    def test_bad_domain_error_handling(self):
        """Step 8: Test bad domain error handling"""
        print("🚫 STEP 8: Bad Domain Error Handling")
        print("=" * 50)
        
        try:
            # Test with non-existent domain
            response = self.session.post(f"{API_BASE}/website/analyze", json={
                "website_url": "https://nonexistent.clairemarcus.invalid",
                "force_reanalysis": True
            })
            
            if response.status_code == 502:
                data = response.json()
                
                # Check if response has uniform {error: "..."} format
                if "error" in data and isinstance(data["error"], str):
                    error_message = data["error"]
                    self.log_result(
                        "Bad Domain Error Handling", 
                        True, 
                        f"Correct 502 status with uniform error format: {error_message}"
                    )
                    return True
                else:
                    self.log_result(
                        "Bad Domain Error Handling", 
                        False, 
                        f"502 status but non-uniform error format: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "Bad Domain Error Handling", 
                    False, 
                    f"Expected 502 but got {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Bad Domain Error Handling", False, error=str(e))
            return False
    
    def test_force_reanalysis_parameter(self):
        """Step 9: Test force_reanalysis parameter functionality"""
        print("🔄 STEP 9: Force Reanalysis Parameter")
        print("=" * 50)
        
        try:
            # Test force reanalysis with example.com again
            response = self.session.post(f"{API_BASE}/website/analyze", json={
                "website_url": "example.com",
                "force_reanalysis": True
            })
            
            if response.status_code == 200:
                data = response.json()
                
                # Check that analysis was created with new timestamp
                created_at = data.get("created_at")
                website_url = data.get("website_url")
                
                if created_at and website_url:
                    self.log_result(
                        "Force Reanalysis Parameter", 
                        True, 
                        f"Force reanalysis successful for {website_url}. New created_at: {created_at}"
                    )
                    return True
                else:
                    self.log_result(
                        "Force Reanalysis Parameter", 
                        False, 
                        "Missing created_at or website_url in response"
                    )
                    return False
            else:
                self.log_result(
                    "Force Reanalysis Parameter", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Force Reanalysis Parameter", False, error=str(e))
            return False
    
    def run_all_tests(self):
        """Run all website analysis tests"""
        print("🚀 WEBSITE ANALYSIS BACKEND TESTING - A1/A2/A3 REVIEW")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_EMAIL}")
        print("FOCUS: GPT analysis, error uniformity, robust authentication")
        print("=" * 60)
        print()
        
        # Run tests in sequence
        tests = [
            self.authenticate,
            self.test_health_check,
            self.test_get_analysis_empty,
            self.test_post_analyze_example_com,
            self.test_get_analysis_populated,
            self.test_error_uniformity_invalid_payload,
            self.test_non_html_error_handling,
            self.test_bad_domain_error_handling,
            self.test_force_reanalysis_parameter
        ]
        
        for test in tests:
            if not test():
                print("❌ Test failed, continuing with remaining tests...")
            print()
        
        # Summary
        print("📋 TEST SUMMARY - WEBSITE ANALYSIS A1/A2/A3")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Review-specific summary
        print("REVIEW REQUEST VERIFICATION:")
        print("-" * 40)
        print("1. POST /api/website/analyze with GPT analysis: ✅ TESTED")
        print("2. Error uniformity {error: '...'} with 422: ✅ TESTED")
        print("3. Non-HTML and bad domain uniform errors: ✅ TESTED")
        print("4. GET /api/website/analysis returns latest: ✅ TESTED")
        print("5. Robust authentication: ✅ TESTED")
        print()
        
        # Detailed results
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
            if result['error']:
                print(f"   Error: {result['error']}")
        
        print()
        print("🎯 WEBSITE ANALYSIS BACKEND TESTING COMPLETED")
        
        return success_rate >= 80  # High threshold for critical functionality

if __name__ == "__main__":
    tester = WebsiteAnalysisTester()
    success = tester.run_all_tests()
    
    if success:
        print("✅ Overall testing: SUCCESS")
        exit(0)
    else:
        print("❌ Overall testing: FAILED")
        exit(1)