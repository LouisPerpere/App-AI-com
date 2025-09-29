#!/usr/bin/env python3
"""
PRIORITY BUGS TESTING - PHASE 1
Testing critical bugs as requested in French review:

PRIORITÉ 1 - BUGS DE PERSISTANCE DE DONNÉES:
1. Business Profile Data Persistence - Test if business profile data persists correctly
2. Website Analysis Field Clearing - Verify if website analysis clears business profile fields

PRIORITÉ 2 - MODULE D'ANALYSE DE SITE WEB:
3. Enhanced Website Analysis API Backend - Test GPT-5 analysis module functionality

User credentials: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import time
import uuid
from datetime import datetime

class PriorityBugsAPITester:
    def __init__(self):
        # Use production backend URL from frontend/.env
        self.base_url = "https://social-pub-hub.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        
        # Test credentials from review request
        self.test_email = "lperpere@yahoo.fr"
        self.test_password = "L@Reunion974!"

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

    def make_request(self, method, endpoint, data=None, expected_status=200):
        """Make API request with authentication"""
        url = f"{self.api_url}/{endpoint}"
        headers = {}
        
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        if method in ['POST', 'PUT'] and data:
            headers['Content-Type'] = 'application/json'
        
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
        print("=" * 50)
        
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        success, status, response = self.make_request("POST", "auth/login", login_data, 200)
        
        if success and 'access_token' in response:
            self.access_token = response['access_token']
            self.user_id = response.get('user_id')
            self.log_test(
                "User Authentication", 
                True, 
                f"Login successful for {self.test_email}, Token: {self.access_token[:20]}..."
            )
            return True
        else:
            self.log_test(
                "User Authentication", 
                False, 
                f"Login failed: Status {status}, Response: {response}"
            )
            return False

    def test_business_profile_persistence(self):
        """PRIORITÉ 1 - Test business profile data persistence"""
        print("\n🏢 TESTING BUSINESS PROFILE DATA PERSISTENCE")
        print("=" * 50)
        
        if not self.access_token:
            self.log_test("Business Profile Persistence", False, "No authentication token")
            return False
        
        # Step 1: Get current business profile
        success, status, current_profile = self.make_request("GET", "business-profile", None, 200)
        
        if not success:
            self.log_test("Get Current Business Profile", False, f"Status: {status}, Response: {current_profile}")
            return False
        
        self.log_test("Get Current Business Profile", True, f"Retrieved profile for: {current_profile.get('business_name', 'N/A')}")
        
        # Step 2: Create unique test data with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_profile_data = {
            "business_name": f"Restaurant Test Persistance {timestamp}",
            "business_type": "restaurant",
            "business_description": f"Description test persistance {timestamp}",
            "target_audience": "Familles et professionnels",
            "brand_tone": "friendly",
            "posting_frequency": "3x_week",
            "preferred_platforms": ["facebook", "instagram"],
            "budget_range": "100-500",
            "email": f"test.{timestamp}@example.com",
            "website_url": f"https://test{timestamp}.com",
            "hashtags_primary": ["restaurant", "test"],
            "hashtags_secondary": ["food", "local"]
        }
        
        # Step 3: Update business profile with test data
        success, status, update_response = self.make_request("PUT", "business-profile", test_profile_data, 200)
        
        if not success:
            self.log_test("Update Business Profile", False, f"Status: {status}, Response: {update_response}")
            return False
        
        self.log_test("Update Business Profile", True, f"Updated with test data: {test_profile_data['business_name']}")
        
        # Step 4: Immediately retrieve profile to verify persistence
        success, status, retrieved_profile = self.make_request("GET", "business-profile", None, 200)
        
        if not success:
            self.log_test("Retrieve Updated Profile", False, f"Status: {status}, Response: {retrieved_profile}")
            return False
        
        # Step 5: Verify data persistence
        persistence_checks = [
            ("business_name", test_profile_data["business_name"]),
            ("business_description", test_profile_data["business_description"]),
            ("email", test_profile_data["email"]),
            ("website_url", test_profile_data["website_url"])
        ]
        
        all_persisted = True
        for field, expected_value in persistence_checks:
            actual_value = retrieved_profile.get(field, "")
            if actual_value == expected_value:
                self.log_test(f"Field Persistence - {field}", True, f"✓ {expected_value}")
            else:
                self.log_test(f"Field Persistence - {field}", False, f"Expected: {expected_value}, Got: {actual_value}")
                all_persisted = False
        
        # Step 6: Test persistence after delay (simulate page reload)
        print("\n   🔄 Testing persistence after delay (simulating page reload)...")
        time.sleep(2)
        
        success, status, delayed_profile = self.make_request("GET", "business-profile", None, 200)
        
        if success:
            delayed_business_name = delayed_profile.get("business_name", "")
            if delayed_business_name == test_profile_data["business_name"]:
                self.log_test("Persistence After Delay", True, f"Data survived delay: {delayed_business_name}")
            else:
                self.log_test("Persistence After Delay", False, f"Data lost after delay. Got: {delayed_business_name}")
                all_persisted = False
        else:
            self.log_test("Persistence After Delay", False, f"Failed to retrieve after delay: {status}")
            all_persisted = False
        
        return all_persisted

    def test_website_analysis_field_clearing(self):
        """PRIORITÉ 1 - Test if website analysis clears business profile fields"""
        print("\n🌐 TESTING WEBSITE ANALYSIS FIELD CLEARING")
        print("=" * 50)
        
        if not self.access_token:
            self.log_test("Website Analysis Field Clearing", False, "No authentication token")
            return False
        
        # Step 1: Get current business profile before analysis
        success, status, profile_before = self.make_request("GET", "business-profile", None, 200)
        
        if not success:
            self.log_test("Get Profile Before Analysis", False, f"Status: {status}")
            return False
        
        business_name_before = profile_before.get("business_name", "")
        email_before = profile_before.get("email", "")
        website_url_before = profile_before.get("website_url", "")
        
        self.log_test("Get Profile Before Analysis", True, f"Business: {business_name_before}, Email: {email_before}")
        
        # Step 2: Perform website analysis
        analysis_data = {
            "website_url": "https://google.com",
            "force_reanalysis": True
        }
        
        success, status, analysis_response = self.make_request("POST", "website/analyze", analysis_data, 200)
        
        if not success:
            self.log_test("Website Analysis Request", False, f"Status: {status}, Response: {analysis_response}")
            return False
        
        self.log_test("Website Analysis Request", True, f"Analysis completed: {analysis_response.get('message', 'N/A')}")
        
        # Step 3: Immediately get business profile after analysis
        success, status, profile_after = self.make_request("GET", "business-profile", None, 200)
        
        if not success:
            self.log_test("Get Profile After Analysis", False, f"Status: {status}")
            return False
        
        business_name_after = profile_after.get("business_name", "")
        email_after = profile_after.get("email", "")
        website_url_after = profile_after.get("website_url", "")
        
        # Step 4: Compare data before and after analysis
        field_comparisons = [
            ("business_name", business_name_before, business_name_after),
            ("email", email_before, email_after),
            ("website_url", website_url_before, website_url_after)
        ]
        
        fields_preserved = True
        for field_name, before_value, after_value in field_comparisons:
            if before_value == after_value:
                self.log_test(f"Field Preservation - {field_name}", True, f"✓ {before_value}")
            else:
                self.log_test(f"Field Preservation - {field_name}", False, f"CLEARED! Before: {before_value}, After: {after_value}")
                fields_preserved = False
        
        # Step 5: Test multiple rapid requests (simulate tab switching)
        print("\n   🔄 Testing field preservation during rapid requests...")
        for i in range(3):
            success, status, rapid_profile = self.make_request("GET", "business-profile", None, 200)
            if success:
                rapid_business_name = rapid_profile.get("business_name", "")
                if rapid_business_name == business_name_before:
                    self.log_test(f"Rapid Request {i+1}", True, f"Data consistent: {rapid_business_name}")
                else:
                    self.log_test(f"Rapid Request {i+1}", False, f"Data inconsistent: {rapid_business_name}")
                    fields_preserved = False
            else:
                self.log_test(f"Rapid Request {i+1}", False, f"Request failed: {status}")
                fields_preserved = False
            
            time.sleep(0.1)  # Small delay between requests
        
        return fields_preserved

    def test_enhanced_website_analysis_api(self):
        """PRIORITÉ 2 - Test Enhanced Website Analysis API Backend with GPT-5"""
        print("\n🤖 TESTING ENHANCED WEBSITE ANALYSIS API (GPT-5)")
        print("=" * 50)
        
        if not self.access_token:
            self.log_test("Enhanced Website Analysis API", False, "No authentication token")
            return False
        
        # Test different websites to verify GPT-5 analysis
        test_websites = [
            "https://google.com",
            "https://github.com",
            "https://example.com"
        ]
        
        analysis_results = []
        
        for website_url in test_websites:
            print(f"\n   🔍 Analyzing: {website_url}")
            
            analysis_data = {
                "website_url": website_url,
                "force_reanalysis": True
            }
            
            success, status, response = self.make_request("POST", "website/analyze", analysis_data, 200)
            
            if success:
                # Check for GPT-5 indicators in response
                message = response.get("message", "")
                analysis_summary = response.get("analysis_summary", "")
                key_topics = response.get("key_topics", [])
                content_suggestions = response.get("content_suggestions", [])
                
                # Verify GPT-5 analysis quality
                quality_checks = [
                    ("GPT-5 Message", "GPT-5" in message or "gpt-5" in message.lower()),
                    ("Analysis Summary", len(analysis_summary) > 50),
                    ("Key Topics", len(key_topics) >= 3),
                    ("Content Suggestions", len(content_suggestions) >= 2)
                ]
                
                website_quality_score = 0
                for check_name, check_result in quality_checks:
                    if check_result:
                        website_quality_score += 1
                        self.log_test(f"{website_url} - {check_name}", True, "✓")
                    else:
                        self.log_test(f"{website_url} - {check_name}", False, "✗")
                
                analysis_results.append({
                    "url": website_url,
                    "quality_score": website_quality_score,
                    "total_checks": len(quality_checks),
                    "response": response
                })
                
                self.log_test(f"Website Analysis - {website_url}", True, f"Quality Score: {website_quality_score}/{len(quality_checks)}")
                
            else:
                self.log_test(f"Website Analysis - {website_url}", False, f"Status: {status}, Response: {response}")
                analysis_results.append({
                    "url": website_url,
                    "quality_score": 0,
                    "total_checks": 4,
                    "error": response
                })
        
        # Calculate overall success rate
        total_quality_score = sum(result["quality_score"] for result in analysis_results)
        total_possible_score = sum(result["total_checks"] for result in analysis_results)
        success_rate = (total_quality_score / total_possible_score * 100) if total_possible_score > 0 else 0
        
        overall_success = success_rate >= 70  # 70% success rate threshold
        
        self.log_test(
            "Enhanced Website Analysis API Overall", 
            overall_success, 
            f"Success Rate: {success_rate:.1f}% ({total_quality_score}/{total_possible_score})"
        )
        
        # Test additional endpoints
        print("\n   🔍 Testing additional website analysis endpoints...")
        
        # Test GET analysis endpoint
        success, status, get_response = self.make_request("GET", "website/analysis", None, 200)
        if success:
            self.log_test("GET Website Analysis", True, f"Retrieved {len(get_response.get('analyses', []))} analyses")
        else:
            self.log_test("GET Website Analysis", False, f"Status: {status}")
        
        # Test DELETE analysis endpoint
        success, status, delete_response = self.make_request("DELETE", "website/analysis", None, 200)
        if success:
            deleted_count = delete_response.get("deleted_count", 0)
            self.log_test("DELETE Website Analysis", True, f"Deleted {deleted_count} analyses")
        else:
            self.log_test("DELETE Website Analysis", False, f"Status: {status}")
        
        return overall_success

    def test_mongodb_integration(self):
        """Test MongoDB integration and data persistence"""
        print("\n🗄️ TESTING MONGODB INTEGRATION")
        print("=" * 50)
        
        if not self.access_token:
            self.log_test("MongoDB Integration", False, "No authentication token")
            return False
        
        # Test database diagnostic endpoint
        success, status, diag_response = self.make_request("GET", "diag", None, 200)
        
        if success:
            db_connected = diag_response.get("database_connected", False)
            mongo_url_prefix = diag_response.get("mongo_url_prefix", "")
            
            self.log_test("Database Connection", db_connected, f"MongoDB URL: {mongo_url_prefix}")
            
            if db_connected and "mongodb+srv" in mongo_url_prefix:
                self.log_test("MongoDB Atlas Connection", True, "Connected to MongoDB Atlas")
                return True
            else:
                self.log_test("MongoDB Atlas Connection", False, f"Connection issue: {diag_response}")
                return False
        else:
            self.log_test("Database Diagnostic", False, f"Status: {status}, Response: {diag_response}")
            return False

    def run_priority_tests(self):
        """Run all priority bug tests"""
        print("🚀 STARTING PRIORITY BUGS TESTING - PHASE 1")
        print("=" * 60)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_email}")
        print("=" * 60)
        
        # Test sequence based on French review priorities
        test_results = {}
        
        # Authentication (prerequisite)
        test_results["authentication"] = self.test_authentication()
        
        if test_results["authentication"]:
            # MongoDB Integration check
            test_results["mongodb_integration"] = self.test_mongodb_integration()
            
            # PRIORITÉ 1 - BUGS DE PERSISTANCE DE DONNÉES
            test_results["business_profile_persistence"] = self.test_business_profile_persistence()
            test_results["website_analysis_field_clearing"] = self.test_website_analysis_field_clearing()
            
            # PRIORITÉ 2 - MODULE D'ANALYSE DE SITE WEB
            test_results["enhanced_website_analysis"] = self.test_enhanced_website_analysis_api()
        else:
            print("❌ Authentication failed - skipping other tests")
            test_results.update({
                "mongodb_integration": False,
                "business_profile_persistence": False,
                "website_analysis_field_clearing": False,
                "enhanced_website_analysis": False
            })
        
        # Print final summary
        print("\n" + "=" * 60)
        print("🎯 PRIORITY BUGS TESTING SUMMARY")
        print("=" * 60)
        
        priority_1_tests = ["business_profile_persistence", "website_analysis_field_clearing"]
        priority_2_tests = ["enhanced_website_analysis"]
        
        print("\n📊 PRIORITÉ 1 - BUGS DE PERSISTANCE DE DONNÉES:")
        for test_name in priority_1_tests:
            status = "✅ WORKING" if test_results.get(test_name, False) else "❌ FAILING"
            print(f"   • {test_name.replace('_', ' ').title()}: {status}")
        
        print("\n📊 PRIORITÉ 2 - MODULE D'ANALYSE DE SITE WEB:")
        for test_name in priority_2_tests:
            status = "✅ WORKING" if test_results.get(test_name, False) else "❌ FAILING"
            print(f"   • {test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\n📈 OVERALL RESULTS:")
        print(f"   • Tests Run: {self.tests_run}")
        print(f"   • Tests Passed: {self.tests_passed}")
        print(f"   • Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        # Determine if critical bugs are resolved
        critical_bugs_resolved = all(test_results.get(test, False) for test in priority_1_tests + priority_2_tests)
        
        if critical_bugs_resolved:
            print("\n🎉 CONCLUSION: All priority bugs appear to be RESOLVED!")
            print("   ✅ Business profile data persistence working correctly")
            print("   ✅ Website analysis does not clear business profile fields")
            print("   ✅ Enhanced website analysis API with GPT-5 working correctly")
        else:
            print("\n⚠️ CONCLUSION: Some priority bugs still need attention!")
            failing_tests = [test for test, result in test_results.items() if not result and test in priority_1_tests + priority_2_tests]
            for failing_test in failing_tests:
                print(f"   ❌ {failing_test.replace('_', ' ').title()}")
        
        return test_results

if __name__ == "__main__":
    tester = PriorityBugsAPITester()
    results = tester.run_priority_tests()