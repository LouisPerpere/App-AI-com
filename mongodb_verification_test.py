#!/usr/bin/env python3
"""
MongoDB Verification Test
Direct database verification to ensure data is actually being saved
"""

import requests
import json
import time
from datetime import datetime
import sys
import os

# Add backend path for database access
sys.path.append('/app/backend')

class MongoDBVerificationTester:
    def __init__(self):
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
        self.log("🔐 Login with lperpere@yahoo.fr / L@Reunion974!")
        
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
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                self.user_id = data.get('user_id')
                self.log(f"✅ Login successful - User ID: {self.user_id}")
                return True
            else:
                self.log(f"❌ Login failed: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Login error: {str(e)}", "ERROR")
            return False
    
    def verify_mongodb_document(self):
        """Directly verify MongoDB document"""
        self.log("🗄️ VERIFYING MongoDB document directly")
        
        try:
            from database import get_database
            db = get_database()
            
            if not db.is_connected():
                self.log("❌ Database not connected", "ERROR")
                return False
            
            # Get the business profile document directly from MongoDB
            profile = db.db.business_profiles.find_one({"user_id": self.user_id})
            
            if profile:
                self.log("✅ MongoDB document found")
                self.log(f"   Document ID: {profile.get('_id')}")
                self.log(f"   User ID: {profile.get('user_id')}")
                self.log(f"   Business Name: {profile.get('business_name')}")
                self.log(f"   Business Description: {profile.get('business_description')}")
                self.log(f"   Website URL: {profile.get('website_url')}")
                self.log(f"   Email: {profile.get('email')}")
                self.log(f"   Updated At: {profile.get('updated_at')}")
                return profile
            else:
                self.log("❌ No MongoDB document found for user", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ MongoDB verification error: {str(e)}", "ERROR")
            return None
    
    def test_put_and_verify_mongodb(self):
        """Test PUT operation and verify MongoDB document is updated"""
        self.log("🧪 TESTING PUT operation with MongoDB verification")
        
        # Create unique test data with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_data = {
            "business_name": f"MONGO TEST {timestamp}",
            "business_description": f"MongoDB verification test {timestamp}",
            "website_url": f"https://mongotest{timestamp}.com",
            "business_type": "service",
            "target_audience": "Test audience",
            "brand_tone": "professional",
            "posting_frequency": "weekly",
            "preferred_platforms": ["Facebook", "Instagram"],
            "budget_range": "100-500€",
            "email": f"mongotest{timestamp}@example.com",
            "hashtags_primary": ["mongo", "test"],
            "hashtags_secondary": [timestamp, "verification"]
        }
        
        # Step 1: Verify current MongoDB state
        self.log("📋 STEP 1: Check current MongoDB document")
        before_doc = self.verify_mongodb_document()
        
        # Step 2: PUT new data
        self.log("📝 STEP 2: PUT new test data")
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.put(
                f"{self.api_url}/business-profile", 
                json=test_data, 
                headers=headers
            )
            
            if response.status_code == 200:
                put_response = response.json()
                self.log("✅ PUT successful")
                self.log(f"PUT response message: {put_response.get('message')}")
            else:
                self.log(f"❌ PUT failed: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ PUT error: {str(e)}", "ERROR")
            return False
        
        # Step 3: Immediately verify MongoDB document
        self.log("🔍 STEP 3: Verify MongoDB document immediately after PUT")
        after_doc = self.verify_mongodb_document()
        
        if not after_doc:
            self.log("❌ No document found after PUT", "ERROR")
            return False
        
        # Step 4: Compare MongoDB document with PUT data
        self.log("🔍 STEP 4: Compare MongoDB document with PUT data")
        
        test_fields = ['business_name', 'business_description', 'website_url', 'email']
        mongodb_matches = True
        
        for field in test_fields:
            expected = test_data.get(field)
            actual = after_doc.get(field)
            
            if expected != actual:
                self.log(f"❌ MongoDB mismatch in {field}: expected '{expected}', got '{actual}'", "ERROR")
                mongodb_matches = False
            else:
                self.log(f"✅ MongoDB {field} matches: {actual}")
        
        # Step 5: Verify API GET returns same data as MongoDB
        self.log("🔍 STEP 5: Verify API GET returns same data as MongoDB")
        
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get(f"{self.api_url}/business-profile", headers=headers)
            
            if response.status_code == 200:
                api_data = response.json()
                self.log("✅ API GET successful")
                
                api_matches = True
                for field in test_fields:
                    mongodb_value = after_doc.get(field)
                    api_value = api_data.get(field)
                    
                    if mongodb_value != api_value:
                        self.log(f"❌ API/MongoDB mismatch in {field}: MongoDB='{mongodb_value}', API='{api_value}'", "ERROR")
                        api_matches = False
                    else:
                        self.log(f"✅ API/MongoDB {field} consistent: {api_value}")
                
                return mongodb_matches and api_matches
            else:
                self.log(f"❌ API GET failed: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ API GET error: {str(e)}", "ERROR")
            return False
    
    def test_user_id_consistency(self):
        """Test that the same user_id is used across all operations"""
        self.log("🔍 TESTING User ID consistency across operations")
        
        # Check JWT token user_id
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get(f"{self.api_url}/auth/me", headers=headers)
            
            if response.status_code == 200:
                auth_data = response.json()
                jwt_user_id = auth_data.get('user_id')
                self.log(f"JWT user_id: {jwt_user_id}")
                
                if jwt_user_id != self.user_id:
                    self.log(f"❌ User ID mismatch: Login={self.user_id}, JWT={jwt_user_id}", "ERROR")
                    return False
                else:
                    self.log("✅ User ID consistent between login and JWT")
            else:
                self.log(f"❌ Auth endpoint failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Auth check error: {str(e)}", "ERROR")
            return False
        
        # Check MongoDB document user_id
        try:
            from database import get_database
            db = get_database()
            
            profile = db.db.business_profiles.find_one({"user_id": self.user_id})
            if profile:
                mongodb_user_id = profile.get('user_id')
                self.log(f"MongoDB user_id: {mongodb_user_id}")
                
                if mongodb_user_id != self.user_id:
                    self.log(f"❌ User ID mismatch: Login={self.user_id}, MongoDB={mongodb_user_id}", "ERROR")
                    return False
                else:
                    self.log("✅ User ID consistent between login and MongoDB")
            else:
                self.log("❌ No MongoDB document found", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ MongoDB check error: {str(e)}", "ERROR")
            return False
        
        return True
    
    def run_verification_test(self):
        """Run the comprehensive MongoDB verification test"""
        self.log("🚨 STARTING MongoDB VERIFICATION TEST")
        self.log("=" * 80)
        
        # Step 1: Login
        if not self.login_user():
            self.log("❌ CRITICAL: Login failed - cannot proceed", "ERROR")
            return False
        
        # Step 2: Test user ID consistency
        if not self.test_user_id_consistency():
            self.log("❌ CRITICAL: User ID inconsistency detected", "ERROR")
            return False
        
        # Step 3: Test PUT and MongoDB verification
        if not self.test_put_and_verify_mongodb():
            self.log("❌ CRITICAL: PUT/MongoDB verification failed", "ERROR")
            return False
        
        # Final summary
        self.log("=" * 80)
        self.log("🎉 RESULT: All MongoDB verification tests passed!")
        self.log("✅ PUT operations correctly save to MongoDB")
        self.log("✅ GET operations correctly retrieve from MongoDB")
        self.log("✅ User ID consistency maintained across all operations")
        
        return True

if __name__ == "__main__":
    tester = MongoDBVerificationTester()
    success = tester.run_verification_test()
    
    if success:
        print("\n✅ MongoDB verification completed successfully")
        exit(0)
    else:
        print("\n❌ MongoDB verification failed")
        exit(1)