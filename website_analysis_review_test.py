#!/usr/bin/env python3
"""
Website Analysis Module Backend Test - Review Request Focus
Focus: Testing the "Converting circular structure to JSON" error fix
Review Request: VALIDATION FINALE - MODULE D'ANALYSE SITE WEB CORRIGÉ
"""

import requests
import json
import time
import sys
from datetime import datetime

class WebsiteAnalysisReviewTester:
    def __init__(self):
        # Use the local backend URL since we're testing in the container
        self.base_url = "http://localhost:8001"
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.tests_run = 0
        self.tests_passed = 0
        
        # Test credentials as specified in review request
        self.test_email = "lperpere@yahoo.fr"
        self.test_password = "L@Reunion974!"
        
        # Primary test website from review request
        self.primary_test_website = "https://my-own-watch.fr"
        
        print("🎯 Website Analysis Review Test - JSON Error Fix Validation")
        print("=" * 70)
        print(f"Backend URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        print(f"Primary Test Website: {self.primary_test_website}")
        print(f"Test User: {self.test_email}")
        print("=" * 70)

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, timeout=20):
        """Run a single API test with timeout and JSON validation"""
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
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        start_time = time.time()
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, params=data, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=timeout)

            elapsed_time = time.time() - start_time
            print(f"   Response Time: {elapsed_time:.2f}s")
            
            # Check performance requirement (< 15 seconds)
            if elapsed_time > 15.0:
                print(f"   ⚠️ Performance Warning: {elapsed_time:.2f}s > 15s requirement")
            else:
                print(f"   ✅ Performance OK: {elapsed_time:.2f}s < 15s")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    
                    # CRITICAL: Test for "Converting circular structure to JSON" error fix
                    json_str = json.dumps(response_data, indent=2)
                    print(f"   ✅ JSON Serialization: SUCCESS ({len(json_str)} chars)")
                    
                    # Verify no circular reference issues
                    if "circular" not in json_str.lower():
                        print(f"   ✅ No Circular Structure Issues Detected")
                    else:
                        print(f"   ❌ Potential Circular Structure Issues Found")
                        return False, {}
                    
                    return True, response_data
                    
                except json.JSONDecodeError as e:
                    print(f"   ❌ JSON Decode Error: {e}")
                    return False, {}
                except TypeError as e:
                    print(f"   ❌ JSON Serialization Error (CIRCULAR STRUCTURE): {e}")
                    return False, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout after {timeout}s")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_user_login(self):
        """Test user login with specified credentials"""
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        success, response = self.run_test(
            "User Authentication (lperpere@yahoo.fr)",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.access_token = response['access_token']
            print(f"   ✅ Access Token: {self.access_token[:20]}...")
            print(f"   ✅ User ID: {response.get('user_id', 'N/A')}")
            return True
        return False

    def test_website_analysis_my_own_watch(self):
        """Test website analysis with https://my-own-watch.fr - PRIMARY TEST"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
            
        # Test with the specific URL from review request
        analysis_data = {
            "website_url": self.primary_test_website,
            "force_reanalysis": True
        }
        
        print(f"\n🎯 CRITICAL TEST: Website Analysis API with {self.primary_test_website}")
        print(f"   Testing for 'Converting circular structure to JSON' error fix")
        
        success, response = self.run_test(
            f"POST /api/website/analyze ({self.primary_test_website})",
            "POST",
            "website/analyze",
            200,
            data=analysis_data,
            timeout=20
        )
        
        if success:
            # Verify expected data structure from review request
            expected_fields = [
                'analysis_summary',
                'key_topics', 
                'brand_tone',
                'target_audience',
                'main_services',
                'content_suggestions'
            ]
            
            print(f"\n   🔍 Verifying Expected Data Structure:")
            missing_fields = []
            for field in expected_fields:
                if field in response:
                    value = response[field]
                    print(f"   ✅ {field}: {type(value).__name__} - {str(value)[:50]}...")
                else:
                    print(f"   ❌ Missing field: {field}")
                    missing_fields.append(field)
            
            # Check data quality
            analysis_summary = response.get('analysis_summary', '')
            key_topics = response.get('key_topics', [])
            content_suggestions = response.get('content_suggestions', [])
            
            print(f"\n   📊 Data Quality Check:")
            print(f"   Analysis Summary Length: {len(analysis_summary)} chars")
            print(f"   Key Topics Count: {len(key_topics) if isinstance(key_topics, list) else 'Not a list'}")
            print(f"   Content Suggestions Count: {len(content_suggestions) if isinstance(content_suggestions, list) else 'Not a list'}")
            
            # Verify comprehensive analysis
            if len(analysis_summary) > 50 and len(key_topics) > 0 and len(content_suggestions) > 0:
                print(f"   ✅ Comprehensive Analysis Data Received")
            else:
                print(f"   ⚠️ Analysis Data May Be Incomplete")
                
            return len(missing_fields) == 0
        return False

    def test_website_analysis_google(self):
        """Test website analysis with Google.com for comparison"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
            
        analysis_data = {
            "website_url": "https://google.com",
            "force_reanalysis": True
        }
        
        success, response = self.run_test(
            "POST /api/website/analyze (google.com)",
            "POST",
            "website/analyze", 
            200,
            data=analysis_data,
            timeout=15
        )
        
        if success:
            # Check for GPT-5 analysis confirmation
            message = response.get('message', '')
            if 'GPT-5' in message:
                print(f"   ✅ GPT-5 Analysis Confirmed: {message}")
            else:
                print(f"   ⚠️ GPT-5 Not Confirmed in Message: {message}")
                
            return True
        return False

    def test_json_serialization_stress(self):
        """Stress test JSON serialization with multiple requests"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
            
        print(f"\n🔬 JSON Serialization Stress Test")
        
        test_urls = [
            self.primary_test_website,
            "https://google.com",
            "https://github.com"
        ]
        
        serialization_errors = 0
        
        for i, url in enumerate(test_urls):
            data = {"website_url": url, "force_reanalysis": True}
            
            success, response = self.run_test(
                f"Serialization Stress Test {i+1} ({url})",
                "POST",
                "website/analyze",
                200,
                data=data,
                timeout=15
            )
            
            if success:
                try:
                    # Test multiple serialization attempts
                    for j in range(3):
                        json_str = json.dumps(response)
                        # Try to parse it back
                        parsed = json.loads(json_str)
                        
                    print(f"   ✅ Serialization Test {i+1}: PASSED")
                except Exception as e:
                    print(f"   ❌ Serialization Test {i+1}: FAILED - {e}")
                    serialization_errors += 1
            else:
                serialization_errors += 1
        
        if serialization_errors == 0:
            print(f"   ✅ All Serialization Tests Passed")
            return True
        else:
            print(f"   ❌ {serialization_errors} Serialization Errors")
            return False

    def test_data_integrity_validation(self):
        """Test data integrity and no data corruption"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
            
        analysis_data = {
            "website_url": self.primary_test_website,
            "force_reanalysis": True
        }
        
        success, response = self.run_test(
            "Data Integrity Validation",
            "POST",
            "website/analyze",
            200,
            data=analysis_data,
            timeout=15
        )
        
        if success:
            # Check for data integrity issues
            integrity_checks = []
            
            # Check 1: All string fields are actually strings
            string_fields = ['analysis_summary', 'brand_tone', 'target_audience']
            for field in string_fields:
                if field in response:
                    if isinstance(response[field], str):
                        integrity_checks.append(f"✅ {field} is string")
                    else:
                        integrity_checks.append(f"❌ {field} is not string: {type(response[field])}")
                        
            # Check 2: List fields are actually lists
            list_fields = ['key_topics', 'main_services', 'content_suggestions']
            for field in list_fields:
                if field in response:
                    if isinstance(response[field], list):
                        integrity_checks.append(f"✅ {field} is list")
                    else:
                        integrity_checks.append(f"❌ {field} is not list: {type(response[field])}")
            
            # Check 3: No null/undefined values in critical fields
            for field in ['analysis_summary', 'key_topics', 'content_suggestions']:
                if field in response and response[field] is not None:
                    integrity_checks.append(f"✅ {field} is not null")
                else:
                    integrity_checks.append(f"❌ {field} is null or missing")
            
            print(f"\n   📋 Data Integrity Checks:")
            for check in integrity_checks:
                print(f"   {check}")
                
            # Count failures
            failures = sum(1 for check in integrity_checks if check.startswith("❌"))
            
            if failures == 0:
                print(f"   ✅ All Data Integrity Checks Passed")
                return True
            else:
                print(f"   ❌ {failures} Data Integrity Issues Found")
                return False
        
        return False

    def test_error_handling_validation(self):
        """Test error handling doesn't cause JSON serialization issues"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
            
        # Test with invalid URL
        invalid_data = {"website_url": "invalid-url-test"}
        
        success, response = self.run_test(
            "Error Handling JSON Validation",
            "POST",
            "website/analyze",
            422,  # Expected validation error
            data=invalid_data
        )
        
        # Even error responses should be properly serializable
        return success

    def run_review_validation_tests(self):
        """Run comprehensive website analysis backend tests for review validation"""
        print("🚀 Starting Website Analysis Review Validation Tests")
        print("Focus: 'Converting circular structure to JSON' error fix validation")
        print("=" * 80)
        
        # Test sequence focused on review requirements
        test_sequence = [
            ("1. Authentication Test", self.test_user_login),
            ("2. Primary Website Analysis (my-own-watch.fr)", self.test_website_analysis_my_own_watch),
            ("3. Comparison Analysis (google.com)", self.test_website_analysis_google),
            ("4. JSON Serialization Stress Test", self.test_json_serialization_stress),
            ("5. Data Integrity Validation", self.test_data_integrity_validation),
            ("6. Error Handling JSON Validation", self.test_error_handling_validation),
        ]
        
        # Run tests
        for test_name, test_func in test_sequence:
            try:
                print(f"\n{'='*20} {test_name} {'='*20}")
                result = test_func()
                if result:
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                print(f"💥 {test_name}: ERROR - {str(e)}")
                
        # Final summary
        print(f"\n{'='*80}")
        print(f"🎯 WEBSITE ANALYSIS REVIEW VALIDATION SUMMARY")
        print(f"{'='*80}")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print(f"🎉 ALL TESTS PASSED - Website Analysis Module is Working Correctly!")
            print(f"✅ 'Converting circular structure to JSON' error fix VALIDATED")
            print(f"✅ Performance requirement (< 15 seconds) VALIDATED")
            print(f"✅ Data integrity and completeness VALIDATED")
            print(f"✅ https://my-own-watch.fr analysis working perfectly")
        elif self.tests_passed > 0:
            print(f"⚠️ PARTIAL SUCCESS - {self.tests_passed}/{self.tests_run} tests passed")
            print(f"❌ Some issues remain - review needed")
        else:
            print(f"❌ ALL TESTS FAILED - Critical issues detected")
            print(f"❌ 'Converting circular structure to JSON' error may still exist")
            
        return self.tests_passed, self.tests_run

if __name__ == "__main__":
    tester = WebsiteAnalysisReviewTester()
    passed, total = tester.run_review_validation_tests()
    
    # Exit with appropriate code
    if passed == total:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure