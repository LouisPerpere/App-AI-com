#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Critical Fixes
Tests both local and production backends for the two definitive fixes.
"""

import requests
import json
import time
from datetime import datetime

class ComprehensiveBackendTester:
    def __init__(self):
        self.backends = {
            "Local": "http://localhost:8001",
            "Production": "https://social-ai-planner-2.preview.emergentagent.com"
        }
        self.email = "lperpere@yahoo.fr"
        self.password = "L@Reunion974!"
        self.total_tests = 0
        self.total_passed = 0

    def test_backend(self, backend_name, base_url):
        """Test a specific backend"""
        print(f"\n{'='*60}")
        print(f"🔧 Testing {backend_name} Backend: {base_url}")
        print(f"{'='*60}")
        
        api_url = f"{base_url}/api"
        access_token = None
        tests_run = 0
        tests_passed = 0
        
        def make_request(method, endpoint, data=None, expected_status=200):
            url = f"{api_url}/{endpoint}"
            headers = {'Content-Type': 'application/json'}
            
            if access_token:
                headers['Authorization'] = f'Bearer {access_token}'
            
            try:
                if method == 'GET':
                    response = requests.get(url, headers=headers, params=data)
                elif method == 'POST':
                    response = requests.post(url, headers=headers, json=data)
                elif method == 'PUT':
                    response = requests.put(url, headers=headers, json=data)
                
                success = response.status_code == expected_status
                try:
                    response_data = response.json()
                except:
                    response_data = {"text": response.text}
                
                return success, response.status_code, response_data
            except Exception as e:
                return False, 0, {"error": str(e)}
        
        # Test 1: Authentication
        print("🔐 Testing Authentication...")
        login_data = {"email": self.email, "password": self.password}
        success, status, response = make_request("POST", "auth/login", login_data, 200)
        tests_run += 1
        
        if success and 'access_token' in response:
            access_token = response['access_token']
            tests_passed += 1
            print(f"   ✅ Authentication successful")
        else:
            print(f"   ❌ Authentication failed: Status {status}")
            return tests_run, tests_passed
        
        # Test 2: Website URL Persistence
        print("🌐 Testing Website URL Persistence...")
        test_website = f"https://test-{backend_name.lower()}-{int(time.time())}.com"
        
        # Get current profile
        success, status, profile = make_request("GET", "business-profile", None, 200)
        tests_run += 1
        
        if not success:
            print(f"   ❌ Failed to get profile: Status {status}")
            tests_passed += 1 if success else 0
        else:
            tests_passed += 1
            
            # Update with test website
            update_data = {
                "business_name": profile.get("business_name", "Test Business"),
                "business_type": profile.get("business_type", "service"),
                "business_description": profile.get("business_description", "Test"),
                "target_audience": profile.get("target_audience", "Test audience"),
                "brand_tone": profile.get("brand_tone", "professional"),
                "posting_frequency": profile.get("posting_frequency", "weekly"),
                "preferred_platforms": profile.get("preferred_platforms", ["Facebook"]),
                "budget_range": profile.get("budget_range", "100-500"),
                "email": profile.get("email", self.email),
                "website_url": test_website,
                "hashtags_primary": profile.get("hashtags_primary", []),
                "hashtags_secondary": profile.get("hashtags_secondary", [])
            }
            
            success, status, update_response = make_request("PUT", "business-profile", update_data, 200)
            tests_run += 1
            
            if success:
                tests_passed += 1
                
                # Verify persistence
                success, status, updated_profile = make_request("GET", "business-profile", None, 200)
                tests_run += 1
                
                if success and updated_profile.get("website_url") == test_website:
                    tests_passed += 1
                    print(f"   ✅ Website URL persistence working: {test_website}")
                else:
                    print(f"   ❌ Website URL not persisted correctly")
            else:
                print(f"   ❌ Failed to update profile: Status {status}")
        
        # Test 3: Website Analysis Authentication
        print("🔍 Testing Website Analysis Authentication...")
        analysis_data = {
            "website_url": "https://google.com",
            "force_reanalysis": True
        }
        
        success, status, analysis_response = make_request("POST", "website/analyze", analysis_data, 200)
        tests_run += 1
        
        if success:
            tests_passed += 1
            # Check for demo_user_id
            response_str = json.dumps(analysis_response).lower()
            if "demo_user_id" not in response_str:
                tests_run += 1
                tests_passed += 1
                print(f"   ✅ Website analysis with proper authentication (no demo_user_id)")
            else:
                tests_run += 1
                print(f"   ❌ Still using demo_user_id in analysis")
        else:
            print(f"   ❌ Website analysis failed: Status {status}")
        
        # Test 4: Authentication validation (should fail without token)
        print("🔒 Testing Authentication Validation...")
        temp_token = access_token
        access_token = None
        
        success, status, no_auth_response = make_request("POST", "website/analyze", analysis_data, 401)
        tests_run += 1
        
        if success or status == 401:
            tests_passed += 1
            print(f"   ✅ Properly rejects unauthenticated requests")
        else:
            print(f"   ❌ Should reject unauthenticated requests")
        
        access_token = temp_token
        
        print(f"\n📊 {backend_name} Backend Results:")
        print(f"   Tests Run: {tests_run}")
        print(f"   Tests Passed: {tests_passed}")
        print(f"   Success Rate: {(tests_passed/tests_run*100):.1f}%")
        
        return tests_run, tests_passed
    
    def run_all_tests(self):
        """Run tests on all backends"""
        print("🚀 COMPREHENSIVE BACKEND TESTING")
        print("Testing critical fixes on both local and production backends")
        print("="*80)
        
        for backend_name, base_url in self.backends.items():
            try:
                tests_run, tests_passed = self.test_backend(backend_name, base_url)
                self.total_tests += tests_run
                self.total_passed += tests_passed
            except Exception as e:
                print(f"❌ Error testing {backend_name} backend: {str(e)}")
        
        # Final summary
        print(f"\n{'='*80}")
        print("🏁 COMPREHENSIVE TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Total Tests Run: {self.total_tests}")
        print(f"Total Tests Passed: {self.total_passed}")
        print(f"Total Tests Failed: {self.total_tests - self.total_passed}")
        print(f"Overall Success Rate: {(self.total_passed/self.total_tests*100):.1f}%" if self.total_tests > 0 else "0%")
        
        if self.total_passed == self.total_tests:
            print("\n🎉 ALL CRITICAL FIXES WORKING ON ALL BACKENDS!")
            print("✅ Website URL Persistence Fix: WORKING")
            print("✅ Website Analysis Authentication Fix: WORKING")
            print("✅ Both fixes verified on local and production backends")
        else:
            print(f"\n⚠️ {self.total_tests - self.total_passed} ISSUES DETECTED")
        
        print("="*80)
        return self.total_passed == self.total_tests

if __name__ == "__main__":
    tester = ComprehensiveBackendTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)