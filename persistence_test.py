#!/usr/bin/env python3
"""
Focused test for Business Profile Data Persistence Issue
Testing MongoDB persistence and tab switching data retention
"""

import requests
import json
import time
from datetime import datetime

class BusinessProfilePersistenceTest:
    def __init__(self):
        # Use the frontend environment URL for testing
        self.base_url = "https://81122b8a-16ad-4551-bfac-5d567214c753.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.tests_run = 0
        self.tests_passed = 0
        
        # Test credentials from review request
        self.test_email = "lperpere@yahoo.fr"
        self.test_password = "L@Reunion974!"
        
        print("🔍 Business Profile Data Persistence Test")
        print("=" * 60)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_email}")
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
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    return False, error_data
                except:
                    print(f"   Error: {response.text}")
                    return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_user_authentication(self):
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
            print(f"   ✅ Authentication successful")
            print(f"   Access Token: {self.access_token[:20]}...")
            return True
        else:
            print(f"   ❌ Authentication failed: {response}")
            return False

    def test_get_initial_business_profile(self):
        """Test getting initial business profile data"""
        success, response = self.run_test(
            "Get Initial Business Profile",
            "GET",
            "business-profile",
            200
        )
        
        if success:
            print(f"   ✅ Initial profile retrieved")
            print(f"   Business Name: {response.get('business_name', 'N/A')}")
            print(f"   Business Type: {response.get('business_type', 'N/A')}")
            print(f"   Email: {response.get('email', 'N/A')}")
            print(f"   Website URL: {response.get('website_url', 'N/A')}")
            return True, response
        else:
            print(f"   ❌ Failed to get initial profile: {response}")
            return False, {}

    def test_update_business_profile_with_website(self):
        """Test updating business profile with comprehensive data including website URL"""
        # Comprehensive business profile data for Restaurant Le Bon Goût Réunionnais
        profile_data = {
            "business_name": "Restaurant Le Bon Goût Réunionnais",
            "business_type": "restaurant",
            "business_description": "Restaurant traditionnel réunionnais proposant une cuisine authentique avec des produits locaux. Spécialités créoles dans une ambiance chaleureuse et familiale.",
            "target_audience": "Familles, touristes et amateurs de cuisine créole à La Réunion, âgés de 25-65 ans",
            "brand_tone": "friendly",
            "posting_frequency": "3x_week",
            "preferred_platforms": ["Facebook", "Instagram", "LinkedIn"],
            "budget_range": "500-1000€",
            "email": "contact@bongoût.re",
            "website_url": "https://www.restaurant-bon-gout-reunion.fr",
            "hashtags_primary": ["#RestaurantReunion", "#CuisineCreole", "#BonGoutReunionnais", "#TraditionReunionnaise"],
            "hashtags_secondary": ["#ProduitLocaux", "#AmbanceFamiliale", "#SpecialitesCreoles", "#LaReunion", "#Gastronomie"]
        }
        
        success, response = self.run_test(
            "Update Business Profile with Website",
            "PUT",
            "business-profile",
            200,
            data=profile_data
        )
        
        if success:
            print(f"   ✅ Profile update successful")
            print(f"   Updated Business Name: {response.get('profile', {}).get('business_name', 'N/A')}")
            print(f"   Updated Website URL: {response.get('profile', {}).get('website_url', 'N/A')}")
            print(f"   Updated Email: {response.get('profile', {}).get('email', 'N/A')}")
            return True, response
        else:
            print(f"   ❌ Profile update failed: {response}")
            return False, {}

    def test_immediate_profile_retrieval(self):
        """Test getting business profile immediately after update"""
        success, response = self.run_test(
            "Get Profile Immediately After Update",
            "GET",
            "business-profile",
            200
        )
        
        if success:
            print(f"   ✅ Profile retrieved after update")
            print(f"   Business Name: {response.get('business_name', 'N/A')}")
            print(f"   Business Type: {response.get('business_type', 'N/A')}")
            print(f"   Email: {response.get('email', 'N/A')}")
            print(f"   Website URL: {response.get('website_url', 'N/A')}")
            
            # Check if data matches what we just updated
            expected_data = {
                "business_name": "Restaurant Le Bon Goût Réunionnais",
                "business_type": "restaurant",
                "email": "contact@bongoût.re",
                "website_url": "https://www.restaurant-bon-gout-reunion.fr"
            }
            
            data_persisted = True
            for key, expected_value in expected_data.items():
                actual_value = response.get(key, '')
                if actual_value != expected_value:
                    print(f"   ❌ Data mismatch for {key}: expected '{expected_value}', got '{actual_value}'")
                    data_persisted = False
                else:
                    print(f"   ✅ {key}: {actual_value}")
            
            return data_persisted, response
        else:
            print(f"   ❌ Failed to retrieve profile after update: {response}")
            return False, {}

    def test_website_analysis_with_persistence(self):
        """Test website analysis and verify it doesn't clear business profile data"""
        website_url = "https://www.restaurant-bon-gout-reunion.fr"
        
        # First, get current profile data
        success, before_profile = self.run_test(
            "Get Profile Before Website Analysis",
            "GET",
            "business-profile",
            200
        )
        
        if not success:
            print("   ❌ Failed to get profile before analysis")
            return False
        
        print(f"   📊 Profile before analysis:")
        print(f"      Business Name: {before_profile.get('business_name', 'N/A')}")
        print(f"      Website URL: {before_profile.get('website_url', 'N/A')}")
        print(f"      Email: {before_profile.get('email', 'N/A')}")
        
        # Perform website analysis
        analysis_data = {
            "website_url": website_url,
            "force_reanalysis": True
        }
        
        success, analysis_response = self.run_test(
            "Website Analysis",
            "POST",
            "website/analyze",
            200,
            data=analysis_data
        )
        
        if not success:
            print(f"   ❌ Website analysis failed: {analysis_response}")
            return False
        
        print(f"   ✅ Website analysis completed")
        print(f"   Analysis message: {analysis_response.get('message', 'N/A')}")
        
        # Get profile data after analysis
        success, after_profile = self.run_test(
            "Get Profile After Website Analysis",
            "GET",
            "business-profile",
            200
        )
        
        if not success:
            print("   ❌ Failed to get profile after analysis")
            return False
        
        print(f"   📊 Profile after analysis:")
        print(f"      Business Name: {after_profile.get('business_name', 'N/A')}")
        print(f"      Website URL: {after_profile.get('website_url', 'N/A')}")
        print(f"      Email: {after_profile.get('email', 'N/A')}")
        
        # Compare before and after data
        critical_fields = ['business_name', 'business_type', 'email', 'website_url']
        data_preserved = True
        
        for field in critical_fields:
            before_value = before_profile.get(field, '')
            after_value = after_profile.get(field, '')
            
            if before_value != after_value:
                print(f"   ❌ Data changed for {field}: '{before_value}' → '{after_value}'")
                data_preserved = False
            else:
                print(f"   ✅ {field} preserved: {after_value}")
        
        return data_preserved

    def test_multiple_profile_retrievals(self):
        """Test multiple consecutive profile retrievals to simulate tab switching"""
        print(f"\n🔄 Simulating Tab Switching (Multiple Profile Retrievals)")
        
        retrievals = []
        for i in range(5):
            print(f"   Retrieval #{i+1}...")
            success, response = self.run_test(
                f"Profile Retrieval #{i+1}",
                "GET",
                "business-profile",
                200
            )
            
            if success:
                retrievals.append({
                    'business_name': response.get('business_name', ''),
                    'website_url': response.get('website_url', ''),
                    'email': response.get('email', '')
                })
                print(f"      Business Name: {response.get('business_name', 'N/A')}")
            else:
                print(f"      ❌ Failed retrieval #{i+1}")
                return False
            
            # Small delay to simulate real usage
            time.sleep(0.5)
        
        # Check consistency across all retrievals
        if len(retrievals) > 1:
            first_retrieval = retrievals[0]
            consistent = True
            
            for i, retrieval in enumerate(retrievals[1:], 2):
                for field in ['business_name', 'website_url', 'email']:
                    if retrieval[field] != first_retrieval[field]:
                        print(f"   ❌ Inconsistency in retrieval #{i} for {field}")
                        print(f"      Expected: {first_retrieval[field]}")
                        print(f"      Got: {retrieval[field]}")
                        consistent = False
            
            if consistent:
                print(f"   ✅ All {len(retrievals)} retrievals consistent")
                return True
            else:
                print(f"   ❌ Data inconsistency detected across retrievals")
                return False
        
        return True

    def test_mongodb_persistence_verification(self):
        """Test MongoDB persistence by checking if data survives across different operations"""
        print(f"\n💾 MongoDB Persistence Verification")
        
        # Test data that should persist
        test_data = {
            "business_name": "Test Persistence Restaurant",
            "business_type": "restaurant", 
            "business_description": "Testing MongoDB persistence",
            "target_audience": "Test audience",
            "brand_tone": "professional",
            "posting_frequency": "daily",
            "preferred_platforms": ["Facebook"],
            "budget_range": "100-500€",
            "email": "test@persistence.com",
            "website_url": "https://test-persistence.com",
            "hashtags_primary": ["#test", "#persistence"],
            "hashtags_secondary": ["#mongodb", "#verification"]
        }
        
        # Update profile with test data
        success, update_response = self.run_test(
            "Update Profile for Persistence Test",
            "PUT",
            "business-profile",
            200,
            data=test_data
        )
        
        if not success:
            print("   ❌ Failed to update profile for persistence test")
            return False
        
        print("   ✅ Profile updated with test data")
        
        # Wait a moment to ensure database write completes
        time.sleep(1)
        
        # Retrieve data multiple times with delays
        for attempt in range(3):
            print(f"   Persistence check #{attempt + 1}...")
            
            success, response = self.run_test(
                f"Persistence Check #{attempt + 1}",
                "GET",
                "business-profile",
                200
            )
            
            if success:
                # Verify critical fields persist
                critical_matches = 0
                critical_fields = ['business_name', 'email', 'website_url']
                
                for field in critical_fields:
                    expected = test_data[field]
                    actual = response.get(field, '')
                    
                    if actual == expected:
                        critical_matches += 1
                        print(f"      ✅ {field}: {actual}")
                    else:
                        print(f"      ❌ {field}: expected '{expected}', got '{actual}'")
                
                if critical_matches == len(critical_fields):
                    print(f"   ✅ Persistence check #{attempt + 1} passed")
                else:
                    print(f"   ❌ Persistence check #{attempt + 1} failed ({critical_matches}/{len(critical_fields)} fields match)")
                    return False
            else:
                print(f"   ❌ Failed to retrieve profile in persistence check #{attempt + 1}")
                return False
            
            # Wait between checks
            if attempt < 2:
                time.sleep(2)
        
        print("   ✅ MongoDB persistence verified - data survives across multiple retrievals")
        return True

    def run_all_tests(self):
        """Run all persistence tests"""
        print("🚀 Starting Business Profile Persistence Tests")
        print("=" * 60)
        
        test_results = []
        
        # Test sequence
        tests = [
            ("User Authentication", self.test_user_authentication),
            ("Get Initial Business Profile", lambda: self.test_get_initial_business_profile()[0]),
            ("Update Business Profile with Website", lambda: self.test_update_business_profile_with_website()[0]),
            ("Immediate Profile Retrieval", lambda: self.test_immediate_profile_retrieval()[0]),
            ("Website Analysis with Persistence", self.test_website_analysis_with_persistence),
            ("Multiple Profile Retrievals (Tab Switching)", self.test_multiple_profile_retrievals),
            ("MongoDB Persistence Verification", self.test_mongodb_persistence_verification)
        ]
        
        for test_name, test_func in tests:
            print(f"\n{'='*60}")
            print(f"🧪 {test_name}")
            print(f"{'='*60}")
            
            try:
                result = test_func()
                test_results.append((test_name, result))
                
                if result:
                    print(f"✅ {test_name} - PASSED")
                else:
                    print(f"❌ {test_name} - FAILED")
                    
            except Exception as e:
                print(f"❌ {test_name} - ERROR: {str(e)}")
                test_results.append((test_name, False))
        
        # Final summary
        print(f"\n{'='*60}")
        print("📊 FINAL TEST SUMMARY")
        print(f"{'='*60}")
        
        passed_tests = sum(1 for _, result in test_results if result)
        total_tests = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status} - {test_name}")
        
        print(f"\n🎯 OVERALL RESULT: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED - Business Profile Persistence is working correctly!")
            return True
        else:
            print("⚠️  SOME TESTS FAILED - Business Profile Persistence issues detected")
            return False

if __name__ == "__main__":
    tester = BusinessProfilePersistenceTest()
    success = tester.run_all_tests()
    exit(0 if success else 1)