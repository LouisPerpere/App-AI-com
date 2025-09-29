#!/usr/bin/env python3
"""
CRITICAL DISCREPANCY TEST
Testing the exact PUT success vs GET results issue reported by user
"""

import requests
import json
import time
from datetime import datetime

class CriticalDiscrepancyTester:
    def __init__(self):
        # Use the production backend URL from frontend/.env
        self.base_url = "https://social-pub-hub.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.user_id = None
        
    def log(self, message, level="INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {level}: {message}")
        
    def login_user(self):
        """Login with the specified credentials"""
        self.log("🔐 STEP 1: Login with lperpere@yahoo.fr / L@Reunion974!")
        
        login_data = {
            "email": "lperpere@yahoo.fr",
            "password": "L@Reunion974!"
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/auth/login",
                json=login_data,
                headers={'Content-Type': 'application/json'}
            )
            
            self.log(f"Login response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                self.user_id = data.get('user_id')
                self.log(f"✅ Login successful")
                self.log(f"   User ID: {self.user_id}")
                self.log(f"   Token: {self.access_token[:20]}..." if self.access_token else "   Token: None")
                return True
            else:
                self.log(f"❌ Login failed: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Login error: {str(e)}", "ERROR")
            return False
    
    def get_business_profile(self, step_name):
        """Get current business profile"""
        self.log(f"📋 {step_name}: GET /api/business-profile")
        
        if not self.access_token:
            self.log("❌ No access token available", "ERROR")
            return None
            
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(f"{self.api_url}/business-profile", headers=headers)
            
            self.log(f"GET response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ GET successful")
                
                # Log key fields for debugging
                key_fields = ['business_name', 'business_description', 'website_url', 'email']
                for field in key_fields:
                    value = data.get(field, 'NOT_FOUND')
                    self.log(f"   {field}: {value}")
                
                return data
            else:
                self.log(f"❌ GET failed: {response.text}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ GET error: {str(e)}", "ERROR")
            return None
    
    def put_business_profile(self, test_data):
        """Update business profile with test data"""
        self.log(f"📝 STEP 3: PUT /api/business-profile with test data")
        
        if not self.access_token:
            self.log("❌ No access token available", "ERROR")
            return None
            
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Log the exact data being sent
            self.log(f"PUT data: {json.dumps(test_data, indent=2)}")
            
            response = requests.put(
                f"{self.api_url}/business-profile", 
                json=test_data, 
                headers=headers
            )
            
            self.log(f"PUT response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ PUT successful")
                self.log(f"PUT response: {json.dumps(data, indent=2)}")
                return data
            else:
                self.log(f"❌ PUT failed: {response.text}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ PUT error: {str(e)}", "ERROR")
            return None
    
    def compare_data(self, put_data, get_data):
        """Compare what was PUT vs what was GET"""
        self.log("🔍 STEP 5: COMPARING PUT vs GET data")
        
        if not put_data or not get_data:
            self.log("❌ Cannot compare - missing data", "ERROR")
            return False
        
        # Extract the profile data from PUT response
        put_profile = put_data.get('profile', put_data)
        
        # Compare key fields
        test_fields = ['business_name', 'business_description', 'website_url']
        discrepancies = []
        
        for field in test_fields:
            put_value = put_profile.get(field, 'NOT_FOUND_IN_PUT')
            get_value = get_data.get(field, 'NOT_FOUND_IN_GET')
            
            if put_value != get_value:
                discrepancies.append({
                    'field': field,
                    'put_value': put_value,
                    'get_value': get_value
                })
                self.log(f"❌ DISCREPANCY in {field}:", "ERROR")
                self.log(f"   PUT sent: {put_value}", "ERROR")
                self.log(f"   GET returned: {get_value}", "ERROR")
            else:
                self.log(f"✅ {field} matches: {put_value}")
        
        return len(discrepancies) == 0, discrepancies
    
    def debug_user_id_consistency(self):
        """Debug user_id consistency between operations"""
        self.log("🔍 DEBUGGING: User ID consistency check")
        
        if not self.access_token:
            self.log("❌ No access token for debugging", "ERROR")
            return
        
        # Check /auth/me endpoint
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get(f"{self.api_url}/auth/me", headers=headers)
            
            if response.status_code == 200:
                auth_data = response.json()
                auth_user_id = auth_data.get('user_id')
                self.log(f"Auth endpoint user_id: {auth_user_id}")
                
                if auth_user_id != self.user_id:
                    self.log(f"⚠️ User ID mismatch! Login: {self.user_id}, Auth: {auth_user_id}", "WARNING")
                else:
                    self.log(f"✅ User ID consistent: {self.user_id}")
            else:
                self.log(f"❌ Auth endpoint failed: {response.status_code}", "ERROR")
                
        except Exception as e:
            self.log(f"❌ Auth debug error: {str(e)}", "ERROR")
    
    def test_database_persistence(self, test_data):
        """Test if data actually persists in database with timing checks"""
        self.log("🗄️ TESTING: Database persistence with timing")
        
        # Multiple GET requests with delays to check persistence
        delays = [0, 0.1, 0.5, 1.0, 2.0]  # seconds
        
        for i, delay in enumerate(delays):
            if delay > 0:
                self.log(f"⏱️ Waiting {delay} seconds...")
                time.sleep(delay)
            
            profile = self.get_business_profile(f"PERSISTENCE CHECK {i+1} (after {delay}s)")
            
            if profile:
                # Check if our test data is still there
                matches = True
                for field in ['business_name', 'business_description', 'website_url']:
                    expected = test_data.get(field)
                    actual = profile.get(field)
                    if expected != actual:
                        matches = False
                        self.log(f"❌ Data lost after {delay}s: {field} = {actual} (expected {expected})", "ERROR")
                
                if matches:
                    self.log(f"✅ Data persisted after {delay}s")
                else:
                    self.log(f"❌ Data corruption detected after {delay}s", "ERROR")
            else:
                self.log(f"❌ Failed to retrieve profile after {delay}s", "ERROR")
    
    def run_critical_test(self):
        """Run the critical discrepancy test"""
        self.log("🚨 STARTING CRITICAL DISCREPANCY TEST")
        self.log("=" * 80)
        
        # Step 1: Login
        if not self.login_user():
            self.log("❌ CRITICAL: Login failed - cannot proceed", "ERROR")
            return False
        
        # Debug user ID consistency
        self.debug_user_id_consistency()
        
        # Step 2: GET current state
        initial_profile = self.get_business_profile("STEP 2")
        if not initial_profile:
            self.log("❌ CRITICAL: Initial GET failed", "ERROR")
            return False
        
        # Step 3: PUT test data
        test_data = {
            "business_name": "TEST UNIQUE 999",
            "business_description": "TEST DESC 999", 
            "website_url": "https://test999.com",
            # Include all required fields to avoid validation errors
            "business_type": "service",
            "target_audience": "Test audience",
            "brand_tone": "professional",
            "posting_frequency": "weekly",
            "preferred_platforms": ["Facebook", "Instagram"],
            "budget_range": "100-500€",
            "email": "test999@example.com",
            "hashtags_primary": ["test", "unique"],
            "hashtags_secondary": ["999", "critical"]
        }
        
        put_response = self.put_business_profile(test_data)
        if not put_response:
            self.log("❌ CRITICAL: PUT failed", "ERROR")
            return False
        
        # Step 4: IMMEDIATELY GET after PUT
        self.log("⚡ STEP 4: IMMEDIATE GET after PUT (race condition test)")
        immediate_profile = self.get_business_profile("IMMEDIATE GET")
        if not immediate_profile:
            self.log("❌ CRITICAL: Immediate GET failed", "ERROR")
            return False
        
        # Step 5: Compare data
        matches, discrepancies = self.compare_data(put_response, immediate_profile)
        
        if matches:
            self.log("✅ SUCCESS: PUT and GET data match perfectly!")
        else:
            self.log("❌ CRITICAL ISSUE CONFIRMED: PUT/GET discrepancy detected!", "ERROR")
            self.log(f"Found {len(discrepancies)} discrepancies:", "ERROR")
            for disc in discrepancies:
                self.log(f"  - {disc['field']}: PUT='{disc['put_value']}' vs GET='{disc['get_value']}'", "ERROR")
        
        # Step 6: Test database persistence over time
        self.test_database_persistence(test_data)
        
        # Final summary
        self.log("=" * 80)
        if matches:
            self.log("🎉 RESULT: No discrepancy found - PUT/GET working correctly")
        else:
            self.log("🚨 RESULT: CRITICAL DISCREPANCY CONFIRMED - Data not persisting correctly")
        
        return matches

if __name__ == "__main__":
    tester = CriticalDiscrepancyTester()
    success = tester.run_critical_test()
    
    if success:
        print("\n✅ Test completed successfully - no issues found")
        exit(0)
    else:
        print("\n❌ Test failed - critical issues detected")
        exit(1)