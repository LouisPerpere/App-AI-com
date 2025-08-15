#!/usr/bin/env python3
"""
Business Profile Data Persistence Debug Test
Specifically examines why only website_url persists while other fields don't
"""

import requests
import json
import os
from datetime import datetime

class BusinessProfileDebugTester:
    def __init__(self):
        # Use the local backend URL
        self.base_url = "http://localhost:8001"
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.user_email = "lperpere@yahoo.fr"
        self.user_password = "L@Reunion974!"

    def login_user(self):
        """Login with the specified credentials"""
        print("🔐 Logging in with lperpere@yahoo.fr / L@Reunion974!")
        
        login_data = {
            "email": self.user_email,
            "password": self.user_password
        }
        
        try:
            response = requests.post(f"{self.api_url}/auth/login", json=login_data)
            print(f"   Login Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                print(f"   ✅ Login successful")
                print(f"   Access Token: {self.access_token[:20]}..." if self.access_token else "   ❌ No access token")
                return True
            else:
                print(f"   ❌ Login failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Login error: {e}")
            return False

    def get_business_profile_detailed(self):
        """Get business profile with detailed field examination"""
        print("\n🔍 EXAMINING GET /api/business-profile DATA")
        print("=" * 60)
        
        if not self.access_token:
            print("❌ No access token available")
            return None
            
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(f"{self.api_url}/business-profile", headers=headers)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("\n📊 FIELD BY FIELD ANALYSIS:")
                print("-" * 40)
                
                # Examine each field in detail
                fields_to_check = [
                    'business_name',
                    'business_type', 
                    'business_description',
                    'target_audience',
                    'brand_tone',
                    'posting_frequency',
                    'preferred_platforms',
                    'budget_range',
                    'email',
                    'website_url',
                    'hashtags_primary',
                    'hashtags_secondary'
                ]
                
                for field in fields_to_check:
                    value = data.get(field, "FIELD_NOT_FOUND")
                    value_type = type(value).__name__
                    value_length = len(str(value)) if value else 0
                    
                    print(f"{field:20} | {value_type:10} | Length: {value_length:3} | Value: {value}")
                    
                    # Special analysis for specific fields
                    if field == 'business_name':
                        if value == "Demo Business":
                            print(f"                     ⚠️  DEMO DATA DETECTED - Expected real user data")
                        elif "TEST PERSISTENCE" in str(value):
                            print(f"                     ✅ TEST DATA FOUND - Real persistence working")
                        else:
                            print(f"                     ℹ️  Real user data: {value}")
                    
                    elif field == 'email':
                        if value == "demo@claire-marcus.com":
                            print(f"                     ⚠️  DEMO EMAIL DETECTED - Expected user email")
                        elif value == self.user_email:
                            print(f"                     ✅ CORRECT USER EMAIL")
                        else:
                            print(f"                     ℹ️  Email value: {value}")
                    
                    elif field == 'website_url':
                        if value and value != "":
                            print(f"                     ✅ WEBSITE URL PERSISTS: {value}")
                        else:
                            print(f"                     ❌ Website URL empty or missing")
                
                print("\n📋 COMPLETE RESPONSE DATA:")
                print(json.dumps(data, indent=2))
                
                return data
            else:
                print(f"❌ Failed to get business profile: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting business profile: {e}")
            return None

    def compare_with_previous_test_data(self, current_data):
        """Compare current data with previous test data mentioned in review"""
        print("\n🔄 COMPARING WITH PREVIOUS TEST DATA")
        print("=" * 60)
        
        # Previous test data mentioned in review request
        previous_test_data = {
            'business_name': 'TEST PERSISTENCE 20250814_133355',
            'email': 'test.persistence.20250814_133355@example.com'
        }
        
        print("Previous test data (from review request):")
        for field, expected_value in previous_test_data.items():
            current_value = current_data.get(field) if current_data else None
            print(f"  {field}:")
            print(f"    Expected: {expected_value}")
            print(f"    Current:  {current_value}")
            
            if current_value == expected_value:
                print(f"    ✅ MATCH - Data persisted correctly")
            elif current_value == "Demo Business" or current_value == "demo@claire-marcus.com":
                print(f"    ❌ DEMO DATA OVERRIDE - Real data replaced by demo")
            else:
                print(f"    ℹ️  Different data - May be newer user data")

    def test_demo_data_override_hypothesis(self, current_data):
        """Test if demo data is overriding user data"""
        print("\n🧪 TESTING DEMO DATA OVERRIDE HYPOTHESIS")
        print("=" * 60)
        
        if not current_data:
            print("❌ No current data to analyze")
            return
            
        demo_indicators = {
            'business_name': 'Demo Business',
            'business_type': 'service',
            'business_description': 'Exemple d\'entreprise utilisant Claire et Marcus',
            'email': 'demo@claire-marcus.com',
            'target_audience': 'Demo audience',
            'brand_tone': 'professional',
            'posting_frequency': 'weekly',
            'budget_range': '500-1000€'
        }
        
        demo_fields_found = []
        user_fields_found = []
        
        for field, demo_value in demo_indicators.items():
            current_value = current_data.get(field)
            if current_value == demo_value:
                demo_fields_found.append(field)
            elif current_value and current_value != demo_value:
                user_fields_found.append(field)
        
        print(f"Demo fields detected: {len(demo_fields_found)}")
        for field in demo_fields_found:
            print(f"  ❌ {field}: {current_data.get(field)}")
            
        print(f"\nUser fields detected: {len(user_fields_found)}")
        for field in user_fields_found:
            print(f"  ✅ {field}: {current_data.get(field)}")
        
        # Special analysis for website_url persistence
        website_url = current_data.get('website_url', '')
        if website_url and website_url != '':
            print(f"\n🌐 WEBSITE URL ANALYSIS:")
            print(f"  Value: {website_url}")
            print(f"  ✅ Website URL persists while other fields show demo data")
            print(f"  🤔 This suggests selective persistence issue")
        
        # Conclusion
        if len(demo_fields_found) > len(user_fields_found):
            print(f"\n🔍 CONCLUSION: Demo data is overriding user data")
            print(f"   Demo fields: {len(demo_fields_found)}")
            print(f"   User fields: {len(user_fields_found)}")
            print(f"   ⚠️  Backend appears to be returning demo data instead of user data")
        else:
            print(f"\n✅ CONCLUSION: User data is being returned correctly")

    def test_authentication_token_validity(self):
        """Test if the authentication token is valid and working"""
        print("\n🔑 TESTING AUTHENTICATION TOKEN VALIDITY")
        print("=" * 60)
        
        if not self.access_token:
            print("❌ No access token to test")
            return False
            
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            # Test with /api/auth/me endpoint
            response = requests.get(f"{self.api_url}/auth/me", headers=headers)
            print(f"Auth/me Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Token is valid")
                print(f"User ID: {data.get('user_id')}")
                print(f"Email: {data.get('email')}")
                print(f"Business Name: {data.get('business_name')}")
                
                # Check if we're getting demo user data
                if data.get('email') == 'demo@claire-marcus.com':
                    print(f"⚠️  WARNING: Token validation returns demo user data")
                    print(f"   This suggests token validation is failing")
                elif data.get('email') == self.user_email:
                    print(f"✅ Token validation returns correct user data")
                else:
                    print(f"ℹ️  Token validation returns different user: {data.get('email')}")
                
                return True
            else:
                print(f"❌ Token validation failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing token validity: {e}")
            return False

    def run_comprehensive_debug(self):
        """Run comprehensive debug analysis"""
        print("🚀 BUSINESS PROFILE DATA PERSISTENCE DEBUG")
        print("=" * 80)
        print(f"Target User: {self.user_email}")
        print(f"Backend URL: {self.base_url}")
        print(f"Testing Focus: Why only website_url persists")
        print("=" * 80)
        
        # Step 1: Login
        if not self.login_user():
            print("❌ Cannot proceed without successful login")
            return
        
        # Step 2: Test token validity
        token_valid = self.test_authentication_token_validity()
        
        # Step 3: Get and analyze business profile data
        current_data = self.get_business_profile_detailed()
        
        # Step 4: Compare with previous test data
        if current_data:
            self.compare_with_previous_test_data(current_data)
            
            # Step 5: Test demo data override hypothesis
            self.test_demo_data_override_hypothesis(current_data)
        
        # Step 6: Final diagnosis
        print("\n🏁 FINAL DIAGNOSIS")
        print("=" * 60)
        
        if not token_valid:
            print("❌ ISSUE: Authentication token validation failing")
            print("   → User authenticated but token validation returns demo data")
            print("   → This causes business profile to return demo data")
            
        elif current_data:
            website_url = current_data.get('website_url', '')
            business_name = current_data.get('business_name', '')
            email = current_data.get('email', '')
            
            if website_url and business_name == 'Demo Business':
                print("❌ CONFIRMED ISSUE: Selective data persistence")
                print(f"   → website_url persists: {website_url}")
                print(f"   → Other fields return demo data")
                print(f"   → Root cause: Backend logic issue in get_business_profile")
                
            elif business_name != 'Demo Business':
                print("✅ NO ISSUE DETECTED: User data is persisting correctly")
                print(f"   → business_name: {business_name}")
                print(f"   → email: {email}")
                print(f"   → website_url: {website_url}")
            else:
                print("❌ ISSUE: Complete demo data override")
                print("   → All fields returning demo data")
                print("   → Authentication or database connection issue")
        
        print("\n📝 RECOMMENDATIONS:")
        if not token_valid:
            print("1. Fix JWT token validation in get_current_user_id() function")
            print("2. Ensure database connection is working properly")
        else:
            print("1. Check get_business_profile() function logic")
            print("2. Verify database query is using correct user_id")
            print("3. Check if demo mode fallback is being triggered incorrectly")

if __name__ == "__main__":
    tester = BusinessProfileDebugTester()
    tester.run_comprehensive_debug()