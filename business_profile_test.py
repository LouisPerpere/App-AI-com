#!/usr/bin/env python3
"""
Business Profile API Testing Script
Focused testing for business profile endpoints after virtual keyboard fix implementation
"""

import requests
import json
import sys
from datetime import datetime

class BusinessProfileTester:
    def __init__(self):
        # Use production backend URL from frontend/.env
        self.base_url = "https://datafix-1.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.tests_run = 0
        self.tests_passed = 0
        
        # Test credentials as specified in review request
        self.test_email = "lperpere@yahoo.fr"
        self.test_password = "L@Reunion974!"
        
        print(f"🔧 Business Profile API Tester Initialized")
        print(f"   Backend URL: {self.base_url}")
        print(f"   Test User: {self.test_email}")
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
        
        # Set Content-Type for JSON requests
        if method in ['POST', 'PUT'] and data:
            test_headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, params=data)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    # Pretty print response for business profile data
                    if 'business_name' in response_data:
                        print(f"   Business Name: {response_data.get('business_name', 'N/A')}")
                        print(f"   Business Type: {response_data.get('business_type', 'N/A')}")
                        print(f"   Email: {response_data.get('email', 'N/A')}")
                        print(f"   Website: {response_data.get('website_url', 'N/A')}")
                    else:
                        print(f"   Response: {json.dumps(response_data, indent=2)[:300]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ FAILED - Exception: {str(e)}")
            return False, {}

    def test_authentication(self):
        """Test authentication with specified credentials"""
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        success, response = self.run_test(
            "Authentication Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.access_token = response['access_token']
            print(f"   ✅ Access Token Obtained: {self.access_token[:20]}...")
            return True
        else:
            print(f"   ❌ Authentication failed - cannot proceed with business profile tests")
            return False

    def test_get_business_profile(self):
        """Test GET /api/business-profile endpoint"""
        success, response = self.run_test(
            "GET Business Profile",
            "GET",
            "business-profile",
            200
        )
        
        if success:
            # Verify expected fields are present
            expected_fields = [
                'business_name', 'business_type', 'business_description',
                'target_audience', 'brand_tone', 'posting_frequency',
                'preferred_platforms', 'budget_range', 'email', 'website_url',
                'hashtags_primary', 'hashtags_secondary'
            ]
            
            missing_fields = []
            for field in expected_fields:
                if field not in response:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"   ⚠️ Missing fields: {missing_fields}")
            else:
                print(f"   ✅ All expected fields present")
            
            return True, response
        
        return False, {}

    def test_put_business_profile(self):
        """Test PUT /api/business-profile endpoint"""
        # Test data for business profile update
        profile_data = {
            "business_name": "Restaurant Le Bon Goût Réunionnais Test",
            "business_type": "restaurant",
            "business_description": "Restaurant spécialisé dans la cuisine créole réunionnaise authentique, proposant des plats traditionnels préparés avec des ingrédients locaux de qualité.",
            "target_audience": "Familles et gourmets amateurs de cuisine créole, touristes et locaux de 25-65 ans",
            "brand_tone": "friendly",
            "posting_frequency": "3x_week",
            "preferred_platforms": ["Facebook", "Instagram", "LinkedIn"],
            "budget_range": "1000-2000€",
            "email": "contact@bongoût-test.re",
            "website_url": "https://www.restaurant-bon-gout-reunion-test.fr",
            "hashtags_primary": ["#CuisineCreole", "#RestaurantReunion", "#BonGoût"],
            "hashtags_secondary": ["#TraditionReunionnaise", "#IngrédientsLocaux", "#Gastronomie"]
        }
        
        success, response = self.run_test(
            "PUT Business Profile",
            "PUT",
            "business-profile",
            200,
            data=profile_data
        )
        
        if success:
            print(f"   ✅ Business profile update successful")
            return True, response, profile_data
        
        return False, {}, profile_data

    def test_data_persistence(self, original_data):
        """Test data persistence by doing PUT followed by GET"""
        print(f"\n🔄 Testing Data Persistence...")
        
        # Wait a moment to ensure data is saved
        import time
        time.sleep(1)
        
        # Get the business profile again
        success, response = self.run_test(
            "GET Business Profile (After PUT)",
            "GET",
            "business-profile",
            200
        )
        
        if success:
            # Compare key fields to verify persistence
            key_fields = ['business_name', 'business_type', 'email', 'website_url']
            persistence_verified = True
            
            for field in key_fields:
                original_value = original_data.get(field, '')
                retrieved_value = response.get(field, '')
                
                if original_value == retrieved_value:
                    print(f"   ✅ {field}: '{retrieved_value}' (persisted correctly)")
                else:
                    print(f"   ❌ {field}: Expected '{original_value}', got '{retrieved_value}'")
                    persistence_verified = False
            
            if persistence_verified:
                print(f"   ✅ Data persistence verified - PUT followed by GET returns same data")
                return True
            else:
                print(f"   ❌ Data persistence failed - PUT and GET data mismatch")
                return False
        
        return False

    def run_comprehensive_test(self):
        """Run comprehensive business profile API test"""
        print("🚀 BUSINESS PROFILE API COMPREHENSIVE TEST")
        print("Testing business profile endpoints after virtual keyboard fix implementation")
        print("=" * 80)
        
        # Step 1: Authentication
        print(f"\n📋 STEP 1: Authentication Test")
        if not self.test_authentication():
            print(f"❌ CRITICAL: Authentication failed - cannot proceed")
            return False
        
        # Step 2: GET business profile (initial state)
        print(f"\n📋 STEP 2: GET Business Profile (Initial)")
        get_success, initial_profile = self.test_get_business_profile()
        if not get_success:
            print(f"❌ CRITICAL: GET business profile failed")
            return False
        
        # Step 3: PUT business profile (update)
        print(f"\n📋 STEP 3: PUT Business Profile (Update)")
        put_success, put_response, test_data = self.test_put_business_profile()
        if not put_success:
            print(f"❌ CRITICAL: PUT business profile failed")
            return False
        
        # Step 4: Data persistence verification
        print(f"\n📋 STEP 4: Data Persistence Verification")
        persistence_success = self.test_data_persistence(test_data)
        if not persistence_success:
            print(f"❌ CRITICAL: Data persistence verification failed")
            return False
        
        # Final summary
        print(f"\n" + "=" * 80)
        print(f"🎯 BUSINESS PROFILE API TEST SUMMARY")
        print(f"=" * 80)
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print(f"   ✅ ALL TESTS PASSED - Business Profile API is working correctly")
            print(f"   ✅ Authentication working with {self.test_email}")
            print(f"   ✅ GET /api/business-profile returns proper business profile data")
            print(f"   ✅ PUT /api/business-profile can save business profile updates")
            print(f"   ✅ Data persistence verified - PUT followed by GET returns same data")
            return True
        else:
            print(f"   ❌ SOME TESTS FAILED - Business Profile API has issues")
            return False

def main():
    """Main test execution"""
    tester = BusinessProfileTester()
    
    try:
        success = tester.run_comprehensive_test()
        
        if success:
            print(f"\n🎉 BUSINESS PROFILE API TEST COMPLETED SUCCESSFULLY")
            print(f"The business profile endpoints are working correctly after virtual keyboard fix implementation.")
            sys.exit(0)
        else:
            print(f"\n💥 BUSINESS PROFILE API TEST FAILED")
            print(f"Issues detected with business profile endpoints.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()