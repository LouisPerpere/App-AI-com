#!/usr/bin/env python3
"""
DEBUG BUSINESS PROFILE PERSISTENCE ISSUE
Detailed investigation of the business profile data persistence problem
"""

import requests
import json
import time
from datetime import datetime

class BusinessProfileDebugger:
    def __init__(self):
        self.base_url = "https://social-ai-planner-2.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.test_email = "lperpere@yahoo.fr"
        self.test_password = "L@Reunion974!"

    def authenticate(self):
        """Authenticate user"""
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        response = requests.post(f"{self.api_url}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            print(f"✅ Authenticated as {self.test_email}")
            print(f"   User ID: {data.get('user_id', 'N/A')}")
            print(f"   Token: {self.access_token[:20]}...")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False

    def get_headers(self):
        """Get headers with authentication"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

    def debug_business_profile_flow(self):
        """Debug the complete business profile flow"""
        print("\n🔍 DEBUGGING BUSINESS PROFILE PERSISTENCE")
        print("=" * 60)
        
        if not self.authenticate():
            return
        
        # Step 1: Get current profile
        print("\n1️⃣ Getting current business profile...")
        response = requests.get(f"{self.api_url}/business-profile", headers=self.get_headers())
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            current_profile = response.json()
            print(f"   Current business_name: {current_profile.get('business_name', 'N/A')}")
            print(f"   Current email: {current_profile.get('email', 'N/A')}")
            print(f"   Current website_url: {current_profile.get('website_url', 'N/A')}")
        else:
            print(f"   Error: {response.text}")
            return
        
        # Step 2: Create test data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_data = {
            "business_name": f"DEBUG TEST {timestamp}",
            "business_type": "service",
            "business_description": f"Debug description {timestamp}",
            "target_audience": "Test audience",
            "brand_tone": "professional",
            "posting_frequency": "weekly",
            "preferred_platforms": ["Facebook", "Instagram"],
            "budget_range": "100-500",
            "email": f"debug.{timestamp}@test.com",
            "website_url": f"https://debug{timestamp}.com",
            "hashtags_primary": ["debug", "test"],
            "hashtags_secondary": ["backend", "api"]
        }
        
        print(f"\n2️⃣ Updating business profile with test data...")
        print(f"   Test business_name: {test_data['business_name']}")
        print(f"   Test email: {test_data['email']}")
        print(f"   Test website_url: {test_data['website_url']}")
        
        # Step 3: PUT request
        response = requests.put(f"{self.api_url}/business-profile", json=test_data, headers=self.get_headers())
        print(f"   PUT Status: {response.status_code}")
        
        if response.status_code == 200:
            put_response = response.json()
            print(f"   PUT Response message: {put_response.get('message', 'N/A')}")
            
            # Check if PUT response contains our data
            put_profile = put_response.get('profile', {})
            if put_profile:
                print(f"   PUT Response business_name: {put_profile.get('business_name', 'N/A')}")
                print(f"   PUT Response email: {put_profile.get('email', 'N/A')}")
            else:
                print("   ⚠️ No profile data in PUT response")
        else:
            print(f"   PUT Error: {response.text}")
            return
        
        # Step 4: Immediate GET request
        print(f"\n3️⃣ Immediate GET request after PUT...")
        time.sleep(0.1)  # Small delay
        
        response = requests.get(f"{self.api_url}/business-profile", headers=self.get_headers())
        print(f"   GET Status: {response.status_code}")
        
        if response.status_code == 200:
            immediate_profile = response.json()
            print(f"   Immediate GET business_name: {immediate_profile.get('business_name', 'N/A')}")
            print(f"   Immediate GET email: {immediate_profile.get('email', 'N/A')}")
            print(f"   Immediate GET website_url: {immediate_profile.get('website_url', 'N/A')}")
            
            # Compare with test data
            if immediate_profile.get('business_name') == test_data['business_name']:
                print("   ✅ business_name matches test data")
            else:
                print("   ❌ business_name does NOT match test data")
                
            if immediate_profile.get('email') == test_data['email']:
                print("   ✅ email matches test data")
            else:
                print("   ❌ email does NOT match test data")
        else:
            print(f"   GET Error: {response.text}")
            return
        
        # Step 5: Delayed GET request
        print(f"\n4️⃣ Delayed GET request (2 seconds later)...")
        time.sleep(2)
        
        response = requests.get(f"{self.api_url}/business-profile", headers=self.get_headers())
        print(f"   Delayed GET Status: {response.status_code}")
        
        if response.status_code == 200:
            delayed_profile = response.json()
            print(f"   Delayed GET business_name: {delayed_profile.get('business_name', 'N/A')}")
            print(f"   Delayed GET email: {delayed_profile.get('email', 'N/A')}")
            print(f"   Delayed GET website_url: {delayed_profile.get('website_url', 'N/A')}")
            
            # Compare with test data
            if delayed_profile.get('business_name') == test_data['business_name']:
                print("   ✅ Delayed: business_name still matches test data")
            else:
                print("   ❌ Delayed: business_name does NOT match test data")
                
            if delayed_profile.get('email') == test_data['email']:
                print("   ✅ Delayed: email still matches test data")
            else:
                print("   ❌ Delayed: email does NOT match test data")
        else:
            print(f"   Delayed GET Error: {response.text}")
        
        # Step 6: Test with minimal data
        print(f"\n5️⃣ Testing with minimal required data...")
        minimal_data = {
            "business_name": f"MINIMAL TEST {timestamp}",
            "business_type": "service",
            "business_description": "",
            "target_audience": "",
            "brand_tone": "professional",
            "posting_frequency": "weekly",
            "preferred_platforms": ["Facebook"],
            "budget_range": "",
            "email": "",
            "website_url": "",
            "hashtags_primary": [],
            "hashtags_secondary": []
        }
        
        response = requests.put(f"{self.api_url}/business-profile", json=minimal_data, headers=self.get_headers())
        print(f"   Minimal PUT Status: {response.status_code}")
        
        if response.status_code == 200:
            time.sleep(0.1)
            response = requests.get(f"{self.api_url}/business-profile", headers=self.get_headers())
            if response.status_code == 200:
                minimal_profile = response.json()
                print(f"   Minimal GET business_name: {minimal_profile.get('business_name', 'N/A')}")
                
                if minimal_profile.get('business_name') == minimal_data['business_name']:
                    print("   ✅ Minimal data persisted correctly")
                else:
                    print("   ❌ Minimal data did NOT persist")
            else:
                print(f"   Minimal GET Error: {response.text}")
        else:
            print(f"   Minimal PUT Error: {response.text}")
        
        # Step 7: Check database diagnostic
        print(f"\n6️⃣ Checking database diagnostic...")
        response = requests.get(f"{self.api_url}/diag", headers=self.get_headers())
        if response.status_code == 200:
            diag = response.json()
            print(f"   Database connected: {diag.get('database_connected', False)}")
            print(f"   Database name: {diag.get('database_name', 'N/A')}")
            print(f"   MongoDB URL prefix: {diag.get('mongo_url_prefix', 'N/A')}")
        else:
            print(f"   Diagnostic Error: {response.text}")

if __name__ == "__main__":
    debugger = BusinessProfileDebugger()
    debugger.debug_business_profile_flow()