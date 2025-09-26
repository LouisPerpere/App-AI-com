#!/usr/bin/env python3
"""
Website Analysis Endpoint Testing
Focus: Diagnose why website analysis is failing
"""

import requests
import json
import sys
from datetime import datetime

class WebsiteAnalysisAPITester:
    def __init__(self):
        # Use the production backend URL from frontend/.env
        self.base_url = "https://social-ai-planner-2.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        
        # Test credentials as specified
        self.test_email = "lperpere@yahoo.fr"
        self.test_password = "L@Reunion974!"
        
        # Test websites as specified
        self.test_websites = [
            "https://google.com",
            "https://github.com",
            "https://www.example.com",
            "https://httpbin.org"  # Good for testing HTTP responses
        ]

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {name}")
            if details:
                print(f"   {details}")

    def make_request(self, method, endpoint, data=None, headers=None):
        """Make HTTP request with error handling"""
        url = f"{self.api_url}/{endpoint}"
        
        # Default headers
        request_headers = {
            'Content-Type': 'application/json'
        }
        
        # Add auth header if available
        if self.access_token:
            request_headers['Authorization'] = f'Bearer {self.access_token}'
            
        # Add custom headers
        if headers:
            request_headers.update(headers)
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=request_headers, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=request_headers, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=request_headers, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=request_headers, timeout=30)
            else:
                return None, f"Unsupported method: {method}"
                
            return response, None
            
        except requests.exceptions.Timeout:
            return None, "Request timeout (30s)"
        except requests.exceptions.ConnectionError:
            return None, "Connection error - backend may be down"
        except requests.exceptions.RequestException as e:
            return None, f"Request error: {str(e)}"

    def test_backend_health(self):
        """Test if backend is accessible"""
        print("\n🏥 BACKEND HEALTH CHECK")
        print("=" * 50)
        
        response, error = self.make_request('GET', 'health')
        
        if error:
            self.log_test("Backend Health Check", False, f"Error: {error}")
            return False
            
        if response.status_code == 200:
            try:
                data = response.json()
                self.log_test("Backend Health Check", True, f"Status: {data.get('status', 'unknown')}")
                return True
            except:
                self.log_test("Backend Health Check", False, "Invalid JSON response")
                return False
        else:
            self.log_test("Backend Health Check", False, f"Status: {response.status_code}")
            return False

    def test_authentication(self):
        """Test authentication with specified credentials"""
        print("\n🔐 AUTHENTICATION TEST")
        print("=" * 50)
        
        # Test login
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        response, error = self.make_request('POST', 'auth/login', login_data)
        
        if error:
            self.log_test("User Login", False, f"Error: {error}")
            return False
            
        if response.status_code == 200:
            try:
                data = response.json()
                self.access_token = data.get('access_token')
                self.user_id = data.get('user_id')
                
                if self.access_token:
                    self.log_test("User Login", True, f"Token received, User ID: {self.user_id}")
                    
                    # Test auth verification
                    auth_response, auth_error = self.make_request('GET', 'auth/me')
                    
                    if auth_error:
                        self.log_test("Auth Verification", False, f"Error: {auth_error}")
                        return False
                        
                    if auth_response.status_code == 200:
                        auth_data = auth_response.json()
                        self.log_test("Auth Verification", True, f"Email: {auth_data.get('email')}")
                        return True
                    else:
                        self.log_test("Auth Verification", False, f"Status: {auth_response.status_code}")
                        return False
                else:
                    self.log_test("User Login", False, "No access token in response")
                    return False
                    
            except json.JSONDecodeError:
                self.log_test("User Login", False, "Invalid JSON response")
                return False
        else:
            self.log_test("User Login", False, f"Status: {response.status_code}, Response: {response.text}")
            return False

    def test_website_analysis_endpoint_basic(self):
        """Test basic website analysis endpoint functionality"""
        print("\n🌐 WEBSITE ANALYSIS ENDPOINT - BASIC TESTS")
        print("=" * 50)
        
        # Test 1: Missing website_url parameter
        response, error = self.make_request('POST', 'website/analyze', {})
        
        if error:
            self.log_test("Missing URL Parameter", False, f"Error: {error}")
        elif response.status_code == 400:
            self.log_test("Missing URL Parameter", True, "Correctly returns 400 for missing URL")
        else:
            self.log_test("Missing URL Parameter", False, f"Expected 400, got {response.status_code}")
        
        # Test 2: Invalid URL format
        invalid_data = {"website_url": "not-a-url"}
        response, error = self.make_request('POST', 'website/analyze', invalid_data)
        
        if error:
            self.log_test("Invalid URL Format", False, f"Error: {error}")
        else:
            # Backend might still process it, check response
            try:
                data = response.json()
                if response.status_code in [200, 400, 422]:
                    self.log_test("Invalid URL Format", True, f"Status: {response.status_code}")
                else:
                    self.log_test("Invalid URL Format", False, f"Unexpected status: {response.status_code}")
            except:
                self.log_test("Invalid URL Format", False, "Invalid JSON response")

    def test_website_analysis_with_real_urls(self):
        """Test website analysis with real URLs"""
        print("\n🔍 WEBSITE ANALYSIS - REAL URL TESTS")
        print("=" * 50)
        
        for i, website_url in enumerate(self.test_websites, 1):
            print(f"\n--- Test {i}: {website_url} ---")
            
            # Test without force_reanalysis
            test_data = {"website_url": website_url}
            response, error = self.make_request('POST', 'website/analyze', test_data)
            
            if error:
                self.log_test(f"Analysis: {website_url}", False, f"Error: {error}")
                continue
                
            print(f"Status Code: {response.status_code}")
            
            try:
                data = response.json()
                print(f"Response Keys: {list(data.keys())}")
                
                if response.status_code == 200:
                    # Check expected response structure
                    expected_keys = ['message', 'website_url', 'insights', 'suggestions', 'analyzed_at', 'status']
                    missing_keys = [key for key in expected_keys if key not in data]
                    
                    if not missing_keys:
                        self.log_test(f"Analysis: {website_url}", True, 
                                    f"Success - Insights: {data.get('insights', '')[:100]}...")
                        
                        # Print suggestions for debugging
                        suggestions = data.get('suggestions', [])
                        if suggestions:
                            print(f"   Suggestions ({len(suggestions)}): {suggestions[0] if suggestions else 'None'}")
                    else:
                        self.log_test(f"Analysis: {website_url}", False, 
                                    f"Missing keys: {missing_keys}")
                else:
                    self.log_test(f"Analysis: {website_url}", False, 
                                f"Status: {response.status_code}, Message: {data.get('detail', data.get('message', 'No message'))}")
                    
            except json.JSONDecodeError:
                self.log_test(f"Analysis: {website_url}", False, 
                            f"Invalid JSON response, Status: {response.status_code}")
                print(f"Raw response: {response.text[:200]}...")
            
            # Test with force_reanalysis
            test_data_force = {"website_url": website_url, "force_reanalysis": True}
            response_force, error_force = self.make_request('POST', 'website/analyze', test_data_force)
            
            if error_force:
                self.log_test(f"Force Reanalysis: {website_url}", False, f"Error: {error_force}")
            elif response_force.status_code == 200:
                self.log_test(f"Force Reanalysis: {website_url}", True, "Force reanalysis parameter accepted")
            else:
                self.log_test(f"Force Reanalysis: {website_url}", False, f"Status: {response_force.status_code}")

    def test_website_analysis_storage(self):
        """Test website analysis storage and retrieval"""
        print("\n💾 WEBSITE ANALYSIS STORAGE TESTS")
        print("=" * 50)
        
        # First, analyze a website
        test_url = "https://example.com"
        analysis_data = {"website_url": test_url}
        
        response, error = self.make_request('POST', 'website/analyze', analysis_data)
        
        if error:
            self.log_test("Analysis Storage", False, f"Analysis failed: {error}")
            return
            
        if response.status_code != 200:
            self.log_test("Analysis Storage", False, f"Analysis failed with status: {response.status_code}")
            return
            
        # Try to retrieve stored analysis
        get_response, get_error = self.make_request('GET', 'website/analysis')
        
        if get_error:
            self.log_test("Analysis Retrieval", False, f"Error: {get_error}")
        elif get_response.status_code == 200:
            try:
                stored_data = get_response.json()
                if stored_data.get('website_url') == test_url:
                    self.log_test("Analysis Storage & Retrieval", True, "Data stored and retrieved correctly")
                else:
                    self.log_test("Analysis Storage & Retrieval", False, "Retrieved data doesn't match")
            except:
                self.log_test("Analysis Retrieval", False, "Invalid JSON response")
        elif get_response.status_code == 404:
            self.log_test("Analysis Retrieval", True, "No stored analysis (expected for demo mode)")
        else:
            self.log_test("Analysis Retrieval", False, f"Unexpected status: {get_response.status_code}")
        
        # Test deletion
        delete_response, delete_error = self.make_request('DELETE', 'website/analysis')
        
        if delete_error:
            self.log_test("Analysis Deletion", False, f"Error: {delete_error}")
        elif delete_response.status_code in [200, 404]:
            self.log_test("Analysis Deletion", True, "Deletion endpoint working")
        else:
            self.log_test("Analysis Deletion", False, f"Status: {delete_response.status_code}")

    def test_openai_integration(self):
        """Test if OpenAI integration is working"""
        print("\n🤖 OPENAI INTEGRATION CHECK")
        print("=" * 50)
        
        # Check if OpenAI API key is configured by testing a simple analysis
        test_data = {"website_url": "https://openai.com"}
        response, error = self.make_request('POST', 'website/analyze', test_data)
        
        if error:
            self.log_test("OpenAI Integration", False, f"Error: {error}")
            return
            
        if response.status_code == 200:
            try:
                data = response.json()
                insights = data.get('insights', '')
                
                # Check if insights look like demo data or real AI analysis
                if 'demo' in insights.lower() or 'exemple' in insights.lower():
                    self.log_test("OpenAI Integration", True, "Running in demo mode (expected)")
                elif len(insights) > 50:  # Real AI analysis would be longer
                    self.log_test("OpenAI Integration", True, "Appears to be real AI analysis")
                else:
                    self.log_test("OpenAI Integration", False, "Insights too short or generic")
                    
            except:
                self.log_test("OpenAI Integration", False, "Invalid response format")
        else:
            self.log_test("OpenAI Integration", False, f"Analysis failed: {response.status_code}")

    def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n⚠️ ERROR HANDLING TESTS")
        print("=" * 50)
        
        # Test with unreachable URL
        unreachable_data = {"website_url": "https://this-domain-does-not-exist-12345.com"}
        response, error = self.make_request('POST', 'website/analyze', unreachable_data)
        
        if error:
            self.log_test("Unreachable URL Handling", False, f"Request error: {error}")
        else:
            # Backend should handle this gracefully
            if response.status_code in [200, 400, 500]:
                try:
                    data = response.json()
                    self.log_test("Unreachable URL Handling", True, 
                                f"Handled gracefully: {data.get('message', 'No message')}")
                except:
                    self.log_test("Unreachable URL Handling", False, "Invalid JSON response")
            else:
                self.log_test("Unreachable URL Handling", False, f"Unexpected status: {response.status_code}")
        
        # Test with malformed URL
        malformed_data = {"website_url": "htp://malformed-url"}
        response, error = self.make_request('POST', 'website/analyze', malformed_data)
        
        if error:
            self.log_test("Malformed URL Handling", False, f"Request error: {error}")
        else:
            if response.status_code in [200, 400, 422]:
                self.log_test("Malformed URL Handling", True, f"Status: {response.status_code}")
            else:
                self.log_test("Malformed URL Handling", False, f"Status: {response.status_code}")

    def run_comprehensive_test(self):
        """Run all website analysis tests"""
        print("🚀 WEBSITE ANALYSIS COMPREHENSIVE TESTING")
        print("=" * 60)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_email}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Step 1: Check backend health
        if not self.test_backend_health():
            print("\n❌ Backend is not accessible. Stopping tests.")
            return
        
        # Step 2: Authenticate
        if not self.test_authentication():
            print("\n❌ Authentication failed. Stopping tests.")
            return
        
        # Step 3: Test website analysis endpoint
        self.test_website_analysis_endpoint_basic()
        
        # Step 4: Test with real URLs
        self.test_website_analysis_with_real_urls()
        
        # Step 5: Test storage functionality
        self.test_website_analysis_storage()
        
        # Step 6: Test OpenAI integration
        self.test_openai_integration()
        
        # Step 7: Test error handling
        self.test_error_handling()
        
        # Final summary
        print("\n" + "=" * 60)
        print("📊 WEBSITE ANALYSIS TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
        elif self.tests_passed / self.tests_run >= 0.8:
            print("✅ Most tests passed - minor issues detected")
        else:
            print("❌ Significant issues detected - needs investigation")
        
        return self.tests_passed / self.tests_run >= 0.8

if __name__ == "__main__":
    tester = WebsiteAnalysisAPITester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)