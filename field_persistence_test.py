#!/usr/bin/env python3
"""
Business Profile Field Persistence Test
Tests the specific scenario described in review request
"""

import requests
import json
import time
from datetime import datetime

class BusinessProfileFieldTest:
    def __init__(self):
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
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                print(f"   ✅ Login successful")
                return True
            else:
                print(f"   ❌ Login failed: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Login error: {e}")
            return False

    def get_business_profile(self, step_name=""):
        """Get current business profile"""
        if step_name:
            print(f"\n📊 {step_name}")
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(f"{self.api_url}/business-profile", headers=headers)
            if response.status_code == 200:
                data = response.json()
                
                # Focus on key fields mentioned in review
                key_fields = ['business_name', 'business_description', 'website_url', 'email']
                print("Key fields:")
                for field in key_fields:
                    value = data.get(field, 'NOT_FOUND')
                    print(f"  {field}: {value}")
                
                return data
            else:
                print(f"❌ Failed to get profile: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    def update_business_profile(self, test_data):
        """Update business profile with test data"""
        print(f"\n📝 UPDATING BUSINESS PROFILE")
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.put(f"{self.api_url}/business-profile", json=test_data, headers=headers)
            print(f"Update Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Update successful")
                return True
            else:
                print(f"❌ Update failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Update error: {e}")
            return False

    def test_field_persistence_scenario(self):
        """Test the exact scenario described in review request"""
        print("🧪 TESTING FIELD PERSISTENCE SCENARIO")
        print("=" * 60)
        
        # Step 1: Login
        if not self.login_user():
            return
        
        # Step 2: Get initial state
        initial_data = self.get_business_profile("STEP 1: Initial business profile state")
        
        # Step 3: Create test data with unique timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_data = {
            "business_name": f"TEST PERSISTENCE {timestamp}",
            "business_type": "restaurant",
            "business_description": f"Test description {timestamp}",
            "target_audience": f"Test audience {timestamp}",
            "brand_tone": "friendly",
            "posting_frequency": "daily",
            "preferred_platforms": ["Facebook", "Instagram", "LinkedIn"],
            "budget_range": "500-1000€",
            "email": f"test.persistence.{timestamp}@example.com",
            "website_url": f"https://test-persistence-{timestamp}.com",
            "hashtags_primary": ["test", "persistence"],
            "hashtags_secondary": ["debug", "review"]
        }
        
        print(f"\nTest data to save:")
        for key, value in test_data.items():
            print(f"  {key}: {value}")
        
        # Step 4: Update profile
        if not self.update_business_profile(test_data):
            return
        
        # Step 5: Immediately get profile after update
        immediate_data = self.get_business_profile("STEP 2: Immediately after update")
        
        # Step 6: Wait and get profile again (simulate tab switching)
        print("\n⏳ Waiting 2 seconds (simulating tab switch)...")
        time.sleep(2)
        
        delayed_data = self.get_business_profile("STEP 3: After 2 second delay")
        
        # Step 7: Multiple rapid requests (simulate frontend refreshBusinessProfileData)
        print("\n🔄 Multiple rapid requests (simulating refreshBusinessProfileData):")
        for i in range(3):
            print(f"Request {i+1}:")
            rapid_data = self.get_business_profile("")
            time.sleep(0.5)
        
        # Step 8: Analysis
        print("\n🔍 PERSISTENCE ANALYSIS")
        print("=" * 40)
        
        if immediate_data and delayed_data:
            # Check each field for persistence
            fields_to_check = ['business_name', 'business_description', 'website_url', 'email']
            
            for field in fields_to_check:
                expected = test_data.get(field)
                immediate = immediate_data.get(field)
                delayed = delayed_data.get(field)
                
                print(f"\n{field}:")
                print(f"  Expected:  {expected}")
                print(f"  Immediate: {immediate}")
                print(f"  Delayed:   {delayed}")
                
                if immediate == expected and delayed == expected:
                    print(f"  ✅ PERSISTS CORRECTLY")
                elif immediate == expected and delayed != expected:
                    print(f"  ❌ LOST AFTER DELAY")
                elif immediate != expected:
                    print(f"  ❌ NOT SAVED INITIALLY")
                else:
                    print(f"  ❓ UNKNOWN STATE")
        
        # Step 9: Check for demo data override
        print(f"\n🔍 DEMO DATA OVERRIDE CHECK")
        if delayed_data:
            demo_indicators = {
                'business_name': 'Demo Business',
                'email': 'demo@claire-marcus.com',
                'business_description': 'Exemple d\'entreprise utilisant Claire et Marcus'
            }
            
            demo_override_detected = False
            for field, demo_value in demo_indicators.items():
                current_value = delayed_data.get(field)
                if current_value == demo_value:
                    print(f"  ❌ {field}: Demo data override detected")
                    demo_override_detected = True
                else:
                    print(f"  ✅ {field}: User data preserved")
            
            if not demo_override_detected:
                print("  ✅ No demo data override detected")

    def test_website_url_specific_behavior(self):
        """Test why website_url might behave differently"""
        print("\n🌐 TESTING WEBSITE_URL SPECIFIC BEHAVIOR")
        print("=" * 60)
        
        # Get current profile
        current_data = self.get_business_profile("Current profile state")
        
        if current_data:
            # Test updating only website_url
            website_only_update = {
                "business_name": current_data.get("business_name", ""),
                "business_type": current_data.get("business_type", "service"),
                "business_description": current_data.get("business_description", ""),
                "target_audience": current_data.get("target_audience", ""),
                "brand_tone": current_data.get("brand_tone", "professional"),
                "posting_frequency": current_data.get("posting_frequency", "weekly"),
                "preferred_platforms": current_data.get("preferred_platforms", ["Facebook"]),
                "budget_range": current_data.get("budget_range", ""),
                "email": current_data.get("email", ""),
                "website_url": f"https://website-only-test-{datetime.now().strftime('%H%M%S')}.com",
                "hashtags_primary": current_data.get("hashtags_primary", []),
                "hashtags_secondary": current_data.get("hashtags_secondary", [])
            }
            
            print(f"Updating only website_url to: {website_only_update['website_url']}")
            
            if self.update_business_profile(website_only_update):
                # Check if website_url persists while other fields remain
                after_website_update = self.get_business_profile("After website-only update")
                
                if after_website_update:
                    website_url = after_website_update.get('website_url')
                    business_name = after_website_update.get('business_name')
                    
                    print(f"\nResult:")
                    print(f"  Website URL: {website_url}")
                    print(f"  Business Name: {business_name}")
                    
                    if website_url == website_only_update['website_url']:
                        print("  ✅ Website URL updated successfully")
                    else:
                        print("  ❌ Website URL update failed")

if __name__ == "__main__":
    tester = BusinessProfileFieldTest()
    tester.test_field_persistence_scenario()
    tester.test_website_url_specific_behavior()