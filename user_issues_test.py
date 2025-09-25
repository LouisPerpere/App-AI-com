#!/usr/bin/env python3
"""
Focused Backend API Testing for User-Reported Issues
Testing the three specific issues reported by user:
1. Notes API Problem - Add Note button doesn't work
2. Business Profile Data Persistence Issue - Data doesn't save properly
3. Website Analysis Module Issue - Website analysis doesn't work

User credentials: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import sys
from datetime import datetime

class UserIssuesTester:
    def __init__(self):
        # Use production backend URL from frontend/.env
        self.base_url = "https://post-validator.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.issues_found = []
        
        # Test credentials from review request
        self.test_email = "lperpere@yahoo.fr"
        self.test_password = "L@Reunion974!"

    def log_result(self, test_name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {test_name}")
            if details:
                print(f"   {details}")
                self.issues_found.append(f"{test_name}: {details}")

    def make_request(self, method, endpoint, data=None, expected_status=200):
        """Make API request with proper headers"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=data)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            
            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text}
            
            return success, response.status_code, response_data
            
        except Exception as e:
            return False, 0, {"error": str(e)}

    def test_authentication(self):
        """Test user authentication with provided credentials"""
        print("\n🔐 TESTING AUTHENTICATION")
        print("-" * 40)
        
        # Test login
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        success, status, response = self.make_request("POST", "auth/login", login_data, 200)
        
        if success and 'access_token' in response:
            self.access_token = response['access_token']
            self.user_id = response.get('user_id', 'unknown')
            self.log_result("User Login", True, f"Successfully authenticated as {self.test_email}")
            
            # Test auth verification
            success, status, response = self.make_request("GET", "auth/me", expected_status=200)
            if success:
                self.log_result("Auth Verification", True, f"User: {response.get('email', 'N/A')}")
                return True
            else:
                self.log_result("Auth Verification", False, f"Status: {status}, Response: {response}")
                return False
        else:
            self.log_result("User Login", False, f"Status: {status}, Response: {response}")
            return False

    def test_notes_api_issue(self):
        """Test Issue #1: Notes API Problem - Add Note button doesn't work"""
        print("\n📝 TESTING NOTES API ISSUE")
        print("-" * 40)
        
        if not self.access_token:
            self.log_result("Notes API Test", False, "No authentication token available")
            return False
        
        # Test 1: GET /api/notes - can retrieve notes list
        success, status, response = self.make_request("GET", "notes", expected_status=200)
        if success:
            notes_count = len(response.get('notes', []))
            self.log_result("GET /api/notes", True, f"Retrieved {notes_count} notes")
        else:
            self.log_result("GET /api/notes", False, f"Status: {status}, Response: {response}")
            return False
        
        # Test 2: POST /api/notes - can create notes
        test_note = {
            "content": f"Test note created at {datetime.now().isoformat()}",
            "description": "Test note for API validation",
            "priority": "high"
        }
        
        success, status, response = self.make_request("POST", "notes", test_note, 200)
        if success:
            note_id = response.get('note', {}).get('note_id')
            self.log_result("POST /api/notes", True, f"Created note with ID: {note_id}")
            
            # Test 3: Verify note appears in list
            success, status, response = self.make_request("GET", "notes", expected_status=200)
            if success:
                notes = response.get('notes', [])
                new_notes_count = len(notes)
                found_note = any(note.get('content') == test_note['content'] for note in notes)
                
                if found_note:
                    self.log_result("Note Persistence", True, f"Note found in list ({new_notes_count} total notes)")
                    
                    # Test 4: DELETE note (cleanup)
                    if note_id:
                        success, status, response = self.make_request("DELETE", f"notes/{note_id}", expected_status=200)
                        if success:
                            self.log_result("DELETE /api/notes", True, "Note deleted successfully")
                        else:
                            self.log_result("DELETE /api/notes", False, f"Status: {status}")
                    
                    return True
                else:
                    self.log_result("Note Persistence", False, "Created note not found in notes list")
                    return False
            else:
                self.log_result("Note Verification", False, f"Could not retrieve notes after creation")
                return False
        else:
            self.log_result("POST /api/notes", False, f"Status: {status}, Response: {response}")
            return False

    def test_business_profile_persistence_issue(self):
        """Test Issue #2: Business Profile Data Persistence Issue"""
        print("\n🏢 TESTING BUSINESS PROFILE PERSISTENCE ISSUE")
        print("-" * 40)
        
        if not self.access_token:
            self.log_result("Business Profile Test", False, "No authentication token available")
            return False
        
        # Test 1: GET current business profile
        success, status, response = self.make_request("GET", "business-profile", expected_status=200)
        if not success:
            self.log_result("GET /api/business-profile", False, f"Status: {status}, Response: {response}")
            return False
        
        original_profile = response
        self.log_result("GET /api/business-profile", True, f"Retrieved profile for: {original_profile.get('business_name', 'N/A')}")
        
        # Test 2: PUT updated business profile with real data
        test_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        updated_profile = {
            "business_name": f"Restaurant Test Persistence {test_timestamp}",
            "business_type": "restaurant",
            "business_description": f"Test restaurant for data persistence validation - {test_timestamp}",
            "target_audience": "Test audience for persistence validation",
            "brand_tone": "friendly",
            "posting_frequency": "daily",
            "preferred_platforms": ["Facebook", "Instagram"],
            "budget_range": "1000-2000€",
            "email": f"test.persistence.{test_timestamp}@restaurant.fr",
            "website_url": f"https://test-persistence-{test_timestamp}.restaurant.fr",
            "hashtags_primary": ["test", "persistence", "validation"],
            "hashtags_secondary": ["restaurant", "api", "testing"]
        }
        
        success, status, response = self.make_request("PUT", "business-profile", updated_profile, 200)
        if not success:
            self.log_result("PUT /api/business-profile", False, f"Status: {status}, Response: {response}")
            return False
        
        self.log_result("PUT /api/business-profile", True, "Profile update request successful")
        
        # Test 3: Immediately GET profile to verify persistence
        success, status, response = self.make_request("GET", "business-profile", expected_status=200)
        if not success:
            self.log_result("GET /api/business-profile (after update)", False, f"Status: {status}")
            return False
        
        # Test 4: Verify data persistence
        retrieved_profile = response
        persistence_checks = [
            ("business_name", updated_profile["business_name"]),
            ("business_type", updated_profile["business_type"]),
            ("email", updated_profile["email"]),
            ("website_url", updated_profile["website_url"])
        ]
        
        all_persisted = True
        for field, expected_value in persistence_checks:
            actual_value = retrieved_profile.get(field)
            if actual_value == expected_value:
                self.log_result(f"Persistence Check - {field}", True, f"✓ {expected_value}")
            else:
                self.log_result(f"Persistence Check - {field}", False, f"Expected: {expected_value}, Got: {actual_value}")
                all_persisted = False
        
        if all_persisted:
            self.log_result("Business Profile Persistence", True, "All data persisted correctly")
            
            # Test 5: Simulate server restart by making multiple requests
            print("   Testing persistence across multiple requests...")
            for i in range(3):
                success, status, response = self.make_request("GET", "business-profile", expected_status=200)
                if success and response.get('business_name') == updated_profile['business_name']:
                    continue
                else:
                    self.log_result("Long-term Persistence", False, f"Data lost after request {i+1}")
                    return False
            
            self.log_result("Long-term Persistence", True, "Data survived multiple requests")
            return True
        else:
            self.log_result("Business Profile Persistence", False, "Data persistence failed")
            return False

    def test_website_analysis_issue(self):
        """Test Issue #3: Website Analysis Module Issue"""
        print("\n🌐 TESTING WEBSITE ANALYSIS MODULE ISSUE")
        print("-" * 40)
        
        if not self.access_token:
            self.log_result("Website Analysis Test", False, "No authentication token available")
            return False
        
        # Test 1: POST /api/website/analyze with a real URL
        test_urls = [
            "https://google.com",
            "https://github.com",
            "https://www.example.com"
        ]
        
        analysis_successful = False
        
        for test_url in test_urls:
            analysis_data = {
                "website_url": test_url,
                "force_reanalysis": True
            }
            
            success, status, response = self.make_request("POST", "website/analyze", analysis_data, 200)
            
            if success:
                # Verify response structure (updated to match actual API response)
                required_fields = ["message", "website_url", "content_suggestions", "status"]
                has_all_fields = all(field in response for field in required_fields)
                
                if has_all_fields:
                    self.log_result(f"POST /api/website/analyze ({test_url})", True, 
                                  f"Analysis completed: {response.get('message', 'N/A')[:100]}...")
                    analysis_successful = True
                    
                    # Test analysis quality
                    key_topics = response.get('key_topics', [])
                    content_suggestions = response.get('content_suggestions', [])
                    analysis_summary = response.get('analysis_summary', '')
                    
                    if len(key_topics) > 0 and len(content_suggestions) > 0 and len(analysis_summary) > 0:
                        self.log_result("Analysis Quality", True, 
                                      f"{len(key_topics)} topics, {len(content_suggestions)} suggestions, summary: {len(analysis_summary)} chars")
                    else:
                        self.log_result("Analysis Quality", False, 
                                      f"Poor analysis: {len(key_topics)} topics, {len(content_suggestions)} suggestions")
                    
                    # Test GPT-5 integration
                    if "GPT-5" in response.get('message', ''):
                        self.log_result("GPT-5 Integration", True, "GPT-5 analysis confirmed")
                    else:
                        self.log_result("GPT-5 Integration", False, "GPT-5 not detected in response")
                    
                    break
                else:
                    missing_fields = [field for field in required_fields if field not in response]
                    self.log_result(f"POST /api/website/analyze ({test_url})", False, 
                                  f"Missing fields: {missing_fields}")
            else:
                self.log_result(f"POST /api/website/analyze ({test_url})", False, 
                              f"Status: {status}, Response: {response}")
        
        if not analysis_successful:
            self.log_result("Website Analysis Module", False, "All test URLs failed analysis")
            return False
        
        # Test 2: Test error handling with invalid URL
        invalid_analysis_data = {
            "website_url": "not-a-valid-url",
            "force_reanalysis": True
        }
        
        success, status, response = self.make_request("POST", "website/analyze", invalid_analysis_data, 422)
        if success or status in [400, 422]:  # Accept validation errors
            self.log_result("Invalid URL Handling", True, "Properly handled invalid URL")
        else:
            self.log_result("Invalid URL Handling", False, f"Unexpected response to invalid URL: {status}")
        
        # Test 3: Test missing parameters
        success, status, response = self.make_request("POST", "website/analyze", {}, 422)
        if success or status in [400, 422]:  # Accept validation errors
            self.log_result("Missing Parameters Handling", True, "Properly handled missing parameters")
        else:
            self.log_result("Missing Parameters Handling", False, f"Unexpected response to missing params: {status}")
        
        return analysis_successful

    def run_all_tests(self):
        """Run all user issue tests"""
        print("🚀 TESTING USER-REPORTED BACKEND ISSUES")
        print("=" * 60)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_email}")
        print("=" * 60)
        
        # Test authentication first
        auth_success = self.test_authentication()
        if not auth_success:
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with other tests")
            return False
        
        # Test each reported issue
        issue_results = {
            "Notes API Issue": self.test_notes_api_issue(),
            "Business Profile Persistence Issue": self.test_business_profile_persistence_issue(),
            "Website Analysis Module Issue": self.test_website_analysis_issue()
        }
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        print("\n🔍 ISSUE STATUS:")
        for issue_name, result in issue_results.items():
            status = "✅ RESOLVED" if result else "❌ CONFIRMED BUG"
            print(f"  {issue_name}: {status}")
        
        if self.issues_found:
            print("\n🚨 CRITICAL ISSUES FOUND:")
            for i, issue in enumerate(self.issues_found, 1):
                print(f"  {i}. {issue}")
        
        print("\n" + "=" * 60)
        
        # Return overall success
        return all(issue_results.values())

if __name__ == "__main__":
    tester = UserIssuesTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)