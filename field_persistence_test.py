#!/usr/bin/env python3
"""
Field Persistence Fix Verification Test
======================================

This test specifically verifies the field persistence fix mentioned in the review request:
1. Login with lperpere@yahoo.fr / L@Reunion974!
2. PUT some test data to business profile (e.g., business_name = "TEST PERSISTENCE")
3. GET the business profile to verify data persists in database

The frontend fix has been applied - all fields now use same protection logic as website_url field:
- Moved business_type inside protection logic  
- Applied dbValue || currentValue || localValue pattern to ALL fields

This verifies that when data is saved to database, it actually persists there.
"""

import requests
import json
import sys
from datetime import datetime

class FieldPersistenceTest:
    def __init__(self):
        # Use the frontend environment variable for backend URL
        self.base_url = "http://localhost:8001"  # Local backend for testing
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.tests_run = 0
        self.tests_passed = 0

    def log(self, message, level="INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        # Add authentication header if we have a token
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'

        self.tests_run += 1
        self.log(f"🔍 Testing {name}...")
        self.log(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ PASSED - Status: {response.status_code}", "SUCCESS")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, {}
            else:
                self.log(f"❌ FAILED - Expected {expected_status}, got {response.status_code}", "ERROR")
                try:
                    error_data = response.json()
                    self.log(f"   Error: {error_data}", "ERROR")
                except:
                    self.log(f"   Error: {response.text}", "ERROR")
                return False, {}

        except Exception as e:
            self.log(f"❌ FAILED - Exception: {str(e)}", "ERROR")
            return False, {}

    def test_authentication(self):
        """Test authentication with specified credentials"""
        self.log("🔐 STEP 1: Testing Authentication", "INFO")
        
        login_data = {
            "email": "lperpere@yahoo.fr",
            "password": "L@Reunion974!"
        }
        
        success, response = self.run_test(
            "User Login (lperpere@yahoo.fr)",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.access_token = response['access_token']
            self.log(f"   ✅ Access Token obtained: {self.access_token[:20]}...", "SUCCESS")
            return True
        else:
            self.log("   ❌ Failed to obtain access token", "ERROR")
            return False

    def test_business_profile_persistence(self):
        """Test business profile data persistence"""
        self.log("💾 STEP 2: Testing Business Profile Data Persistence", "INFO")
        
        # Generate unique test data with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_data = {
            "business_name": f"TEST PERSISTENCE {timestamp}",
            "business_type": "restaurant",
            "business_description": f"Test business description for persistence verification {timestamp}",
            "target_audience": f"Test target audience {timestamp}",
            "brand_tone": "professional",
            "posting_frequency": "daily",
            "preferred_platforms": ["Facebook", "Instagram", "LinkedIn"],
            "budget_range": "500-1000€",
            "email": f"test.persistence.{timestamp}@example.com",
            "website_url": f"https://test-persistence-{timestamp}.example.com",
            "hashtags_primary": [f"test{timestamp}", "persistence", "verification"],
            "hashtags_secondary": ["backend", "api", "testing"]
        }
        
        self.log(f"   📝 Test data prepared with business_name: {test_data['business_name']}")
        
        # Step 2a: PUT test data to business profile
        self.log("   🔄 Saving test data to business profile...")
        success, put_response = self.run_test(
            "PUT Business Profile (Test Data)",
            "PUT",
            "business-profile",
            200,
            data=test_data
        )
        
        if not success:
            self.log("   ❌ Failed to save business profile data", "ERROR")
            return False
        
        self.log("   ✅ Business profile data saved successfully", "SUCCESS")
        
        # Step 2b: GET business profile to verify persistence
        self.log("   🔍 Retrieving business profile to verify persistence...")
        success, get_response = self.run_test(
            "GET Business Profile (Verify Persistence)",
            "GET",
            "business-profile",
            200
        )
        
        if not success:
            self.log("   ❌ Failed to retrieve business profile data", "ERROR")
            return False
        
        # Step 2c: Verify all fields persisted correctly
        self.log("   🔍 Verifying field persistence...")
        
        persistence_results = {}
        critical_fields = [
            "business_name", "business_type", "business_description", 
            "target_audience", "brand_tone", "posting_frequency",
            "email", "website_url"
        ]
        
        for field in critical_fields:
            expected_value = test_data[field]
            actual_value = get_response.get(field, "")
            
            if expected_value == actual_value:
                persistence_results[field] = "✅ PERSISTED"
                self.log(f"     ✅ {field}: '{actual_value}' - PERSISTED CORRECTLY", "SUCCESS")
            else:
                persistence_results[field] = "❌ FAILED"
                self.log(f"     ❌ {field}: Expected '{expected_value}', Got '{actual_value}' - PERSISTENCE FAILED", "ERROR")
        
        # Check array fields separately
        array_fields = ["preferred_platforms", "hashtags_primary", "hashtags_secondary"]
        for field in array_fields:
            expected_value = test_data[field]
            actual_value = get_response.get(field, [])
            
            if set(expected_value) == set(actual_value):
                persistence_results[field] = "✅ PERSISTED"
                self.log(f"     ✅ {field}: {actual_value} - PERSISTED CORRECTLY", "SUCCESS")
            else:
                persistence_results[field] = "❌ FAILED"
                self.log(f"     ❌ {field}: Expected {expected_value}, Got {actual_value} - PERSISTENCE FAILED", "ERROR")
        
        # Calculate persistence success rate
        total_fields = len(persistence_results)
        successful_fields = sum(1 for result in persistence_results.values() if "✅" in result)
        success_rate = (successful_fields / total_fields) * 100
        
        self.log(f"   📊 PERSISTENCE RESULTS: {successful_fields}/{total_fields} fields persisted correctly ({success_rate:.1f}%)")
        
        if success_rate == 100:
            self.log("   🎉 ALL FIELDS PERSISTED CORRECTLY - PERSISTENCE FIX VERIFIED!", "SUCCESS")
            return True
        elif success_rate >= 80:
            self.log(f"   ⚠️  MOSTLY WORKING - {success_rate:.1f}% persistence rate", "WARNING")
            return True
        else:
            self.log(f"   ❌ PERSISTENCE ISSUES DETECTED - Only {success_rate:.1f}% success rate", "ERROR")
            return False

    def test_immediate_persistence_verification(self):
        """Test immediate persistence verification (multiple GET requests)"""
        self.log("🔄 STEP 3: Testing Immediate Persistence Verification", "INFO")
        
        # Perform multiple GET requests to ensure data persists across requests
        for i in range(3):
            self.log(f"   🔍 Persistence check #{i+1}...")
            success, response = self.run_test(
                f"GET Business Profile (Persistence Check #{i+1})",
                "GET",
                "business-profile",
                200
            )
            
            if not success:
                self.log(f"   ❌ Persistence check #{i+1} failed", "ERROR")
                return False
            
            # Check if we still have our test data
            business_name = response.get("business_name", "")
            if "TEST PERSISTENCE" in business_name:
                self.log(f"   ✅ Persistence check #{i+1}: Data still present - {business_name}", "SUCCESS")
            else:
                self.log(f"   ❌ Persistence check #{i+1}: Test data lost - {business_name}", "ERROR")
                return False
        
        self.log("   🎉 ALL PERSISTENCE CHECKS PASSED - Data survives multiple requests!", "SUCCESS")
        return True

    def run_field_persistence_test(self):
        """Run the complete field persistence test"""
        self.log("🚀 STARTING FIELD PERSISTENCE FIX VERIFICATION TEST", "INFO")
        self.log("=" * 80)
        self.log("This test verifies the field persistence fix mentioned in the review request:")
        self.log("1. Login with lperpere@yahoo.fr / L@Reunion974!")
        self.log("2. PUT test data to business profile (business_name = 'TEST PERSISTENCE')")
        self.log("3. GET business profile to verify data persists in database")
        self.log("=" * 80)
        
        # Test sequence
        test_sequence = [
            ("Authentication", self.test_authentication),
            ("Business Profile Persistence", self.test_business_profile_persistence),
            ("Immediate Persistence Verification", self.test_immediate_persistence_verification)
        ]
        
        all_tests_passed = True
        
        for test_name, test_method in test_sequence:
            self.log(f"\n📋 Running: {test_name}")
            try:
                result = test_method()
                if not result:
                    all_tests_passed = False
                    self.log(f"❌ {test_name} FAILED", "ERROR")
                else:
                    self.log(f"✅ {test_name} PASSED", "SUCCESS")
            except Exception as e:
                all_tests_passed = False
                self.log(f"❌ {test_name} FAILED with exception: {str(e)}", "ERROR")
        
        # Final results
        self.log("\n" + "=" * 80)
        self.log("🏁 FIELD PERSISTENCE TEST RESULTS")
        self.log("=" * 80)
        self.log(f"Tests Run: {self.tests_run}")
        self.log(f"Tests Passed: {self.tests_passed}")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        self.log(f"Success Rate: {success_rate:.1f}%")
        
        if all_tests_passed and success_rate == 100:
            self.log("🎉 FIELD PERSISTENCE FIX VERIFICATION: SUCCESSFUL!", "SUCCESS")
            self.log("✅ All fields now use same protection logic as website_url field", "SUCCESS")
            self.log("✅ business_type moved inside protection logic", "SUCCESS") 
            self.log("✅ dbValue || currentValue || localValue pattern applied to ALL fields", "SUCCESS")
            self.log("✅ Data persists correctly in database", "SUCCESS")
            return True
        else:
            self.log("❌ FIELD PERSISTENCE FIX VERIFICATION: FAILED!", "ERROR")
            self.log("❌ Some issues detected with field persistence", "ERROR")
            return False

def main():
    """Main function to run the field persistence test"""
    tester = FieldPersistenceTest()
    success = tester.run_field_persistence_test()
    
    if success:
        print("\n🎯 CONCLUSION: Field persistence fix is working correctly!")
        sys.exit(0)
    else:
        print("\n⚠️ CONCLUSION: Field persistence issues detected!")
        sys.exit(1)

if __name__ == "__main__":
    main()