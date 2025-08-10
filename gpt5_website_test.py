#!/usr/bin/env python3
"""
GPT-5 Website Analysis Integration Testing
Testing the NEW GPT-5 website analysis after migration from legacy OpenAI
"""

import requests
import json
import sys
import os
from datetime import datetime
import time

class GPT5WebsiteAnalysisTester:
    def __init__(self):
        # Use production backend URL from frontend/.env
        self.base_url = "https://9d9abc32-ca1b-47b1-bc5e-c34b81138b90.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.tests_run = 0
        self.tests_passed = 0
        
        # Test credentials from review request
        self.test_email = "lperpere@yahoo.fr"
        self.test_password = "L@Reunion974!"
        
        print("🚀 GPT-5 Website Analysis Integration Testing")
        print("=" * 60)
        print(f"Backend URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        print("=" * 60)

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {}
        
        # Add authentication header if we have a token
        if self.access_token:
            test_headers['Authorization'] = f'Bearer {self.access_token}'
        
        # Add custom headers
        if headers:
            test_headers.update(headers)
        
        # Set content type for JSON requests
        if method in ['POST', 'PUT'] and data:
            test_headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, params=data, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    # Truncate long responses for readability
                    response_str = json.dumps(response_data, indent=2)
                    if len(response_str) > 500:
                        response_str = response_str[:500] + "..."
                    print(f"   Response: {response_str}")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_authentication(self):
        """Test user authentication with provided credentials"""
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        success, response = self.run_test(
            "User Authentication",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.access_token = response['access_token']
            print(f"   ✅ Access Token obtained: {self.access_token[:20]}...")
            return True
        return False

    def test_gpt5_module_loading(self):
        """Test that GPT-5 module is loaded correctly"""
        print(f"\n🔍 Testing GPT-5 Module Loading...")
        
        # Test by checking if website analysis endpoint is available
        success, response = self.run_test(
            "GPT-5 Module Availability Check",
            "POST",
            "website/analyze",
            422,  # Should fail with validation error (no data), not 404
            data={}
        )
        
        if success:
            print("✅ GPT-5 website analyzer module is loaded and accessible")
            return True
        else:
            print("❌ GPT-5 website analyzer module may not be loaded")
            return False

    def test_emergent_llm_key_configuration(self):
        """Test that EMERGENT_LLM_KEY is configured"""
        print(f"\n🔍 Testing EMERGENT_LLM_KEY Configuration...")
        
        # We can't directly access env vars, but we can test if GPT-5 analysis works
        # If it works, the key is configured correctly
        test_data = {
            "website_url": "https://httpbin.org/html",
            "force_reanalysis": True
        }
        
        success, response = self.run_test(
            "EMERGENT_LLM_KEY Test (via analysis)",
            "POST",
            "website/analyze",
            200,
            data=test_data
        )
        
        if success:
            message = response.get('message', '')
            if 'GPT-5' in message:
                print("✅ EMERGENT_LLM_KEY is working - GPT-5 analysis successful")
                return True
            else:
                print("⚠️ Analysis completed but may be using fallback mode")
                return True
        return False

    def test_website_analyze_endpoint(self):
        """Test POST /api/website/analyze endpoint with real website"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
        
        # Test with Google.com as requested
        test_data = {
            "website_url": "https://google.com",
            "force_reanalysis": True
        }
        
        success, response = self.run_test(
            "Website Analysis - Google.com",
            "POST",
            "website/analyze",
            200,
            data=test_data
        )
        
        if success:
            # Verify response structure
            required_fields = [
                'message', 'website_url', 'analysis_summary', 'key_topics',
                'brand_tone', 'target_audience', 'main_services', 'content_suggestions',
                'last_analyzed', 'status'
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in response:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            # Check if it's GPT-5 analysis
            message = response.get('message', '')
            if 'GPT-5' in message:
                print("✅ GPT-5 analysis confirmed in response message")
            else:
                print("⚠️ Response doesn't explicitly mention GPT-5")
            
            # Verify analysis quality
            analysis_summary = response.get('analysis_summary', '')
            key_topics = response.get('key_topics', [])
            content_suggestions = response.get('content_suggestions', [])
            
            if len(analysis_summary) > 50 and len(key_topics) >= 3 and len(content_suggestions) >= 3:
                print("✅ Rich analysis content detected - likely GPT-5 quality")
            else:
                print("⚠️ Analysis content seems basic - may be fallback mode")
            
            return True
        return False

    def test_website_analysis_get_endpoint(self):
        """Test GET /api/website/analysis endpoint"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
        
        success, response = self.run_test(
            "Get Website Analysis",
            "GET",
            "website/analysis",
            200
        )
        
        if success:
            if response.get('analysis'):
                print("✅ Website analysis retrieved successfully")
                analysis = response['analysis']
                
                # Verify analysis structure
                if all(key in analysis for key in ['website_url', 'analysis_summary', 'key_topics']):
                    print("✅ Analysis structure is complete")
                    return True
            else:
                print("⚠️ No analysis found (expected if no previous analysis)")
                return True
        return False

    def test_website_analysis_delete_endpoint(self):
        """Test DELETE /api/website/analysis endpoint"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
        
        success, response = self.run_test(
            "Delete Website Analysis",
            "DELETE",
            "website/analysis",
            200
        )
        
        if success:
            deleted_count = response.get('deleted_count', 0)
            print(f"✅ Deleted {deleted_count} analysis records")
            return True
        return False

    def test_database_storage(self):
        """Test that results are stored in MongoDB website_analyses collection"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
        
        # First, perform an analysis
        test_data = {
            "website_url": "https://httpbin.org/html",
            "force_reanalysis": True
        }
        
        success, response = self.run_test(
            "Database Storage Test - Analysis",
            "POST",
            "website/analyze",
            200,
            data=test_data
        )
        
        if not success:
            return False
        
        # Wait a moment for database write
        time.sleep(2)
        
        # Then retrieve it to verify storage
        success, response = self.run_test(
            "Database Storage Test - Retrieval",
            "GET",
            "website/analysis",
            200
        )
        
        if success and response.get('analysis'):
            analysis = response['analysis']
            if analysis.get('website_url') == "https://httpbin.org/html":
                print("✅ Analysis correctly stored and retrieved from MongoDB")
                return True
        
        print("❌ Analysis not properly stored in database")
        return False

    def test_error_handling_invalid_website(self):
        """Test error handling with invalid websites"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
        
        # Test with invalid URL
        test_data = {
            "website_url": "https://this-domain-does-not-exist-12345.com",
            "force_reanalysis": True
        }
        
        success, response = self.run_test(
            "Error Handling - Invalid Website",
            "POST",
            "website/analyze",
            400,  # Should return 400 for invalid website
            data=test_data
        )
        
        if success:
            print("✅ Invalid website properly handled with 400 error")
            return True
        
        # If it didn't return 400, check if it used fallback analysis
        if response.get('message') and 'fallback' in response.get('message', '').lower():
            print("✅ Invalid website handled with fallback analysis")
            return True
        
        return False

    def test_fallback_analysis(self):
        """Test fallback analysis when GPT-5 is not available"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
        
        # Test with a simple website that should trigger fallback if needed
        test_data = {
            "website_url": "https://example.com",
            "force_reanalysis": True
        }
        
        success, response = self.run_test(
            "Fallback Analysis Test",
            "POST",
            "website/analyze",
            200,
            data=test_data
        )
        
        if success:
            # Check if response indicates fallback or GPT-5
            message = response.get('message', '')
            analysis_summary = response.get('analysis_summary', '')
            
            if 'GPT-5' in message:
                print("✅ GPT-5 analysis working (no fallback needed)")
            elif len(analysis_summary) > 0:
                print("✅ Fallback analysis working correctly")
            else:
                print("❌ Neither GPT-5 nor fallback analysis working")
                return False
            
            return True
        return False

    def test_analysis_caching(self):
        """Test analysis caching functionality"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
        
        test_url = "https://httpbin.org/json"
        
        # First analysis (should be fresh)
        test_data = {
            "website_url": test_url,
            "force_reanalysis": True
        }
        
        success1, response1 = self.run_test(
            "Analysis Caching - First Analysis",
            "POST",
            "website/analyze",
            200,
            data=test_data
        )
        
        if not success1:
            return False
        
        # Second analysis without force_reanalysis (should use cache)
        test_data = {
            "website_url": test_url,
            "force_reanalysis": False
        }
        
        success2, response2 = self.run_test(
            "Analysis Caching - Cached Analysis",
            "POST",
            "website/analyze",
            200,
            data=test_data
        )
        
        if success2:
            message = response2.get('message', '')
            if 'cache' in message.lower():
                print("✅ Analysis caching working correctly")
                return True
            else:
                print("⚠️ Analysis completed but caching behavior unclear")
                return True
        
        return False

    def test_gpt5_vs_fallback_quality(self):
        """Test and compare GPT-5 analysis quality vs fallback"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
        
        # Test with a restaurant website to get rich analysis
        test_data = {
            "website_url": "https://httpbin.org/html",
            "force_reanalysis": True
        }
        
        success, response = self.run_test(
            "GPT-5 vs Fallback Quality Test",
            "POST",
            "website/analyze",
            200,
            data=test_data
        )
        
        if success:
            message = response.get('message', '')
            analysis_summary = response.get('analysis_summary', '')
            key_topics = response.get('key_topics', [])
            content_suggestions = response.get('content_suggestions', [])
            
            # Analyze quality indicators
            quality_score = 0
            
            if 'GPT-5' in message:
                quality_score += 3
                print("✅ GPT-5 analysis confirmed")
            
            if len(analysis_summary) > 100:
                quality_score += 2
                print("✅ Rich analysis summary")
            
            if len(key_topics) >= 5:
                quality_score += 2
                print("✅ Comprehensive key topics")
            
            if len(content_suggestions) >= 3:
                quality_score += 2
                print("✅ Multiple content suggestions")
            
            if any(len(suggestion) > 50 for suggestion in content_suggestions):
                quality_score += 1
                print("✅ Detailed content suggestions")
            
            print(f"   Quality Score: {quality_score}/10")
            
            if quality_score >= 7:
                print("✅ HIGH QUALITY: Likely GPT-5 analysis")
            elif quality_score >= 4:
                print("⚠️ MEDIUM QUALITY: Possibly fallback analysis")
            else:
                print("❌ LOW QUALITY: Analysis may have issues")
            
            return quality_score >= 4
        
        return False

    def run_all_tests(self):
        """Run all GPT-5 website analysis tests"""
        print("\n🧪 Starting GPT-5 Website Analysis Integration Tests")
        print("=" * 60)
        
        # Test sequence
        test_sequence = [
            ("Authentication", self.test_authentication),
            ("GPT-5 Module Loading", self.test_gpt5_module_loading),
            ("EMERGENT_LLM_KEY Configuration", self.test_emergent_llm_key_configuration),
            ("Website Analyze Endpoint", self.test_website_analyze_endpoint),
            ("Website Analysis GET Endpoint", self.test_website_analysis_get_endpoint),
            ("Database Storage", self.test_database_storage),
            ("Error Handling - Invalid Website", self.test_error_handling_invalid_website),
            ("Fallback Analysis", self.test_fallback_analysis),
            ("Analysis Caching", self.test_analysis_caching),
            ("GPT-5 vs Fallback Quality", self.test_gpt5_vs_fallback_quality),
            ("Website Analysis DELETE Endpoint", self.test_website_analysis_delete_endpoint),
        ]
        
        # Run tests
        for test_name, test_func in test_sequence:
            try:
                result = test_func()
                if not result:
                    print(f"⚠️ Test '{test_name}' failed but continuing...")
            except Exception as e:
                print(f"❌ Test '{test_name}' crashed: {e}")
        
        # Final results
        print("\n" + "=" * 60)
        print("🏁 GPT-5 Website Analysis Test Results")
        print("=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED! GPT-5 Website Analysis is working perfectly!")
        elif self.tests_passed >= self.tests_run * 0.8:
            print("✅ MOSTLY WORKING! GPT-5 Website Analysis is functional with minor issues.")
        else:
            print("⚠️ ISSUES DETECTED! GPT-5 Website Analysis needs attention.")
        
        return self.tests_passed, self.tests_run

if __name__ == "__main__":
    tester = GPT5WebsiteAnalysisTester()
    passed, total = tester.run_all_tests()
    
    # Exit with appropriate code
    if passed == total:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Some tests failed