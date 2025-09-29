#!/usr/bin/env python3
"""
Focused test for Phase 1 Business Profile Editing functionality
"""

import requests
import json
import sys

class BusinessProfileEditingTester:
    def __init__(self, base_url="https://social-pub-hub.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.access_token = None
        self.business_id = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {}
        
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        if method in ['POST', 'PUT']:
            headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json()
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

    def test_login(self):
        """Test user login with lperpere@yahoo.fr credentials"""
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
            print(f"   ✅ Login successful")
            return True
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
            # Store business_id for other tests
            if 'id' in response:
                self.business_id = response['id']
            
            # Verify all expected fields are present
            expected_fields = [
                'id', 'user_id', 'business_name', 'business_type', 'target_audience',
                'brand_tone', 'posting_frequency', 'preferred_platforms', 'budget_range',
                'email', 'website_url', 'hashtags_primary', 'hashtags_secondary'
            ]
            
            missing_fields = []
            for field in expected_fields:
                if field not in response:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"   ⚠️ Missing fields: {missing_fields}")
            else:
                print("   ✅ All expected fields present")
            
            # Display current profile data
            print(f"   Business Name: {response.get('business_name', 'N/A')}")
            print(f"   Business Type: {response.get('business_type', 'N/A')}")
            print(f"   Email: {response.get('email', 'N/A')}")
            print(f"   Website URL: {response.get('website_url', 'N/A')}")
            print(f"   Primary Hashtags: {response.get('hashtags_primary', [])}")
            print(f"   Secondary Hashtags: {response.get('hashtags_secondary', [])}")
        
        return success

    def test_update_business_profile_all_fields(self):
        """Test PUT /api/business-profile endpoint with all form fields"""
        update_data = {
            "business_name": "Restaurant Le Bon Goût Réunionnais",
            "business_type": "restaurant_gastronomique",
            "target_audience": "Familles créoles et touristes de 25-55 ans à La Réunion, amateurs de cuisine traditionnelle réunionnaise et française",
            "brand_tone": "friendly_authentic",
            "posting_frequency": "daily",
            "preferred_platforms": ["facebook", "instagram", "linkedin"],
            "budget_range": "500-1000",
            "email": "contact@bongoût-reunion.fr",
            "website_url": "https://www.bongoût-reunion.fr",
            "hashtags_primary": ["#RestaurantReunion", "#CuisineCreole", "#BonGoutReunion"],
            "hashtags_secondary": ["#GastronomieReunion", "#TraditionCreole", "#SaintDenis", "#Reunion974", "#CuisineTropicale"]
        }
        
        success, response = self.run_test(
            "PUT Business Profile (All Fields)",
            "PUT",
            "business-profile",
            200,
            data=update_data
        )
        
        if success:
            print("   ✅ Business profile updated successfully")
            
            # Verify all fields were updated correctly
            field_checks = [
                ("business_name", update_data["business_name"]),
                ("business_type", update_data["business_type"]),
                ("target_audience", update_data["target_audience"]),
                ("brand_tone", update_data["brand_tone"]),
                ("posting_frequency", update_data["posting_frequency"]),
                ("budget_range", update_data["budget_range"]),
                ("email", update_data["email"]),
                ("website_url", update_data["website_url"])
            ]
            
            all_correct = True
            for field_name, expected_value in field_checks:
                actual_value = response.get(field_name)
                if actual_value == expected_value:
                    print(f"   ✅ {field_name}: Updated correctly")
                else:
                    print(f"   ❌ {field_name}: Expected '{expected_value}', got '{actual_value}'")
                    all_correct = False
            
            # Check array fields
            if response.get("preferred_platforms") == update_data["preferred_platforms"]:
                print("   ✅ preferred_platforms: Updated correctly")
            else:
                print(f"   ❌ preferred_platforms: Expected {update_data['preferred_platforms']}, got {response.get('preferred_platforms')}")
                all_correct = False
            
            if response.get("hashtags_primary") == update_data["hashtags_primary"]:
                print("   ✅ hashtags_primary: Updated correctly")
            else:
                print(f"   ❌ hashtags_primary: Expected {update_data['hashtags_primary']}, got {response.get('hashtags_primary')}")
                all_correct = False
            
            if response.get("hashtags_secondary") == update_data["hashtags_secondary"]:
                print("   ✅ hashtags_secondary: Updated correctly")
            else:
                print(f"   ❌ hashtags_secondary: Expected {update_data['hashtags_secondary']}, got {response.get('hashtags_secondary')}")
                all_correct = False
            
            if all_correct:
                print("   🎉 All fields updated correctly!")
        
        return success

    def test_hashtags_arrays_validation(self):
        """Test hashtags as arrays (primary and secondary)"""
        hashtag_data = {
            "hashtags_primary": [
                "#RestaurantReunion",
                "#CuisineCreole", 
                "#BonGoutReunion",
                "#Reunion974",
                "#SaintDenis"
            ],
            "hashtags_secondary": [
                "#GastronomieReunion",
                "#TraditionCreole",
                "#CuisineTropicale",
                "#RestaurantLocal",
                "#SpecialitesCreoles",
                "#PlatsTraditionnels",
                "#CuisineAuthentique",
                "#RestaurantFamilial",
                "#SaveursTropicales",
                "#HeritageCreole"
            ]
        }
        
        success, response = self.run_test(
            "PUT Business Profile (Hashtags Arrays)",
            "PUT",
            "business-profile",
            200,
            data=hashtag_data
        )
        
        if success:
            print("   ✅ Hashtags arrays update successful")
            
            # Verify primary hashtags
            primary_hashtags = response.get("hashtags_primary", [])
            if isinstance(primary_hashtags, list) and len(primary_hashtags) == len(hashtag_data["hashtags_primary"]):
                print(f"   ✅ hashtags_primary: {len(primary_hashtags)} hashtags stored correctly")
                for hashtag in hashtag_data["hashtags_primary"]:
                    if hashtag in primary_hashtags:
                        print(f"     ✅ {hashtag}")
                    else:
                        print(f"     ❌ Missing: {hashtag}")
            else:
                print(f"   ❌ hashtags_primary: Expected {len(hashtag_data['hashtags_primary'])}, got {len(primary_hashtags) if isinstance(primary_hashtags, list) else 'not a list'}")
            
            # Verify secondary hashtags
            secondary_hashtags = response.get("hashtags_secondary", [])
            if isinstance(secondary_hashtags, list) and len(secondary_hashtags) == len(hashtag_data["hashtags_secondary"]):
                print(f"   ✅ hashtags_secondary: {len(secondary_hashtags)} hashtags stored correctly")
            else:
                print(f"   ❌ hashtags_secondary: Expected {len(hashtag_data['hashtags_secondary'])}, got {len(secondary_hashtags) if isinstance(secondary_hashtags, list) else 'not a list'}")
        
        return success

    def test_verify_persistence(self):
        """Test that updates persist by retrieving profile again"""
        success, response = self.run_test(
            "GET Business Profile (Verify Persistence)",
            "GET",
            "business-profile",
            200
        )
        
        if success:
            print("   ✅ Business profile retrieved successfully after updates")
            print(f"   Current Business Name: {response.get('business_name', 'N/A')}")
            print(f"   Current Email: {response.get('email', 'N/A')}")
            print(f"   Current Website: {response.get('website_url', 'N/A')}")
            print(f"   Primary Hashtags Count: {len(response.get('hashtags_primary', []))}")
            print(f"   Secondary Hashtags Count: {len(response.get('hashtags_secondary', []))}")
            
            # Verify data persistence
            if response.get('business_name') and response.get('email'):
                print("   ✅ Profile data persisted correctly")
            else:
                print("   ❌ Some profile data may not have persisted")
        
        return success

    def run_all_tests(self):
        """Run all business profile editing tests"""
        print("🚀 Starting Phase 1 Business Profile Editing Tests")
        print("=" * 60)
        print("Testing for user: lperpere@yahoo.fr")
        print("=" * 60)
        
        # Test sequence
        tests = [
            ("User Login", self.test_login),
            ("GET Business Profile", self.test_get_business_profile),
            ("PUT Business Profile (All Fields)", self.test_update_business_profile_all_fields),
            ("PUT Business Profile (Hashtags Arrays)", self.test_hashtags_arrays_validation),
            ("GET Business Profile (Verify Persistence)", self.test_verify_persistence),
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
        
        # Print final results
        print("\n" + "=" * 60)
        print(f"📊 PHASE 1 BUSINESS PROFILE EDITING TEST RESULTS")
        print("=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All Phase 1 business profile editing tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False

if __name__ == "__main__":
    tester = BusinessProfileEditingTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)