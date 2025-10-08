#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime

class FocusedBackendTester:
    def __init__(self):
        self.base_url = "https://post-restore.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_note_id = None
        self.updated_profile_data = None

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
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
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
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

    def test_health_check(self):
        """Test API health check"""
        success, response = self.run_test(
            "API Health Check",
            "GET",
            "health",
            200
        )
        return success

    def test_user_login(self):
        """Test user login with specified credentials"""
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
            print(f"   Access Token: {self.access_token[:20]}...")
            return True
        return False

    def test_get_current_user(self):
        """Test getting current user info"""
        success, response = self.run_test(
            "Get Current User Info",
            "GET", 
            "auth/me",
            200
        )
        
        if success:
            print(f"   User Email: {response.get('email', 'N/A')}")
            print(f"   Subscription: {response.get('subscription_status', 'N/A')}")
            print(f"   Trial Days: {response.get('trial_days_remaining', 'N/A')}")
        
        return success

    def test_get_business_profile(self):
        """Test getting business profile"""
        success, response = self.run_test(
            "Get Business Profile",
            "GET",
            "business-profile",
            200
        )
        
        if success:
            key_fields = ['business_name', 'business_type', 'business_description', 
                         'target_audience', 'brand_tone', 'posting_frequency',
                         'preferred_platforms', 'budget_range', 'email', 'website_url',
                         'hashtags_primary', 'hashtags_secondary']
            
            missing_fields = []
            for field in key_fields:
                if field not in response:
                    missing_fields.append(field)
                else:
                    print(f"   ✅ {field}: {str(response[field])[:50]}...")
            
            if missing_fields:
                print(f"   ⚠️ Missing fields: {missing_fields}")
            else:
                print("   ✅ All expected business profile fields present")
        
        return success

    def test_update_business_profile(self):
        """Test updating business profile"""
        profile_data = {
            "business_name": "Restaurant Le Bon Goût Réunionnais",
            "business_type": "restaurant", 
            "business_description": "Restaurant traditionnel réunionnais proposant une cuisine authentique avec des produits locaux. Spécialités: carry, rougail, samoussas. Ambiance familiale et chaleureuse dans le centre de Saint-Denis.",
            "target_audience": "Familles réunionnaises, touristes, amateurs de cuisine créole, professionnels pour déjeuners d'affaires",
            "brand_tone": "friendly",
            "posting_frequency": "3x_week",
            "preferred_platforms": ["facebook", "instagram", "linkedin"],
            "budget_range": "500-1000€",
            "email": "contact@bongoût.re",
            "website_url": "https://www.restaurant-bon-gout.re",
            "hashtags_primary": ["#RestaurantReunion", "#CuisineCreole", "#SaintDenis", "#ProduitLocaux"],
            "hashtags_secondary": ["#Carry", "#Rougail", "#Samoussas", "#CuisineAuthentique", "#AmbanceFamiliale"]
        }
        
        success, response = self.run_test(
            "Update Business Profile",
            "PUT",
            "business-profile",
            200,
            data=profile_data
        )
        
        if success:
            print("   ✅ Business profile update successful")
            self.updated_profile_data = profile_data
        
        return success

    def test_verify_business_profile_persistence(self):
        """Test that business profile updates persist"""
        success, response = self.run_test(
            "Verify Business Profile Persistence",
            "GET",
            "business-profile", 
            200
        )
        
        if success and self.updated_profile_data:
            persistence_checks = []
            for key, expected_value in self.updated_profile_data.items():
                actual_value = response.get(key)
                if actual_value == expected_value:
                    persistence_checks.append(f"✅ {key}: persisted correctly")
                else:
                    persistence_checks.append(f"❌ {key}: expected {expected_value}, got {actual_value}")
            
            for check in persistence_checks[:5]:
                print(f"   {check}")
            
            if len(persistence_checks) > 5:
                print(f"   ... and {len(persistence_checks) - 5} more fields")
            
            successful_persistence = sum(1 for check in persistence_checks if check.startswith("   ✅"))
            total_fields = len(persistence_checks)
            
            print(f"   📊 Persistence Rate: {successful_persistence}/{total_fields} fields ({successful_persistence/total_fields*100:.1f}%)")
            
            return successful_persistence > total_fields * 0.8
        
        return success

    def test_get_notes(self):
        """Test getting notes"""
        success, response = self.run_test(
            "Get Notes",
            "GET",
            "notes",
            200
        )
        
        if success:
            if isinstance(response, dict) and 'notes' in response:
                notes = response['notes']
                print(f"   📝 Found {len(notes)} notes")
                if notes:
                    print(f"   First note: {notes[0].get('content', 'N/A')[:50]}...")
            elif isinstance(response, list):
                print(f"   📝 Found {len(response)} notes (direct array)")
                if response:
                    print(f"   First note: {response[0].get('content', 'N/A')[:50]}...")
            else:
                print(f"   ⚠️ Unexpected response format: {type(response)}")
        
        return success

    def test_create_note(self):
        """Test creating a note"""
        note_data = {
            "title": "Promotion Spéciale Carry Poulet",
            "content": "Lancer une promotion sur notre carry poulet signature avec des légumes du jardin. Prix spécial à 12€ au lieu de 15€. Mettre en avant les produits locaux et l'authenticité de la recette familiale.",
            "priority": "high"
        }
        
        success, response = self.run_test(
            "Create Note",
            "POST",
            "notes",
            200,
            data=note_data
        )
        
        if success and 'note' in response:
            created_note = response['note']
            self.test_note_id = created_note.get('id')
            print(f"   📝 Created note ID: {self.test_note_id}")
            print(f"   Content: {created_note.get('content', 'N/A')[:50]}...")
        
        return success

    def test_delete_note(self):
        """Test deleting the created note"""
        if not self.test_note_id:
            print("   ⚠️ No test note ID available, skipping delete test")
            return True
        
        success, response = self.run_test(
            "Delete Note",
            "DELETE",
            f"notes/{self.test_note_id}",
            200
        )
        
        if success:
            print(f"   🗑️ Successfully deleted note {self.test_note_id}")
        
        return success

    def test_generate_posts(self):
        """Test post generation"""
        generation_data = {
            "count": 2,
            "business_context": "Restaurant réunionnais traditionnel"
        }
        
        success, response = self.run_test(
            "Generate Posts",
            "POST",
            "generate-posts",
            200,
            data=generation_data
        )
        
        if success:
            posts = response.get('posts', [])
            print(f"   📄 Generated {len(posts)} posts")
            if posts:
                print(f"   First post preview: {posts[0].get('content', 'N/A')[:100]}...")
        
        return success

    def run_all_tests(self):
        """Run all focused backend tests"""
        print("🚀 Starting Focused Backend API Testing")
        print("=" * 60)
        print(f"Backend URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        print("=" * 60)
        
        test_sequence = [
            ("Health Check", self.test_health_check),
            ("Authentication - User Login", self.test_user_login),
            ("Authentication - Get Current User", self.test_get_current_user),
            ("Business Profile - Get Profile", self.test_get_business_profile),
            ("Business Profile - Update Profile", self.test_update_business_profile),
            ("Business Profile - Verify Persistence", self.test_verify_business_profile_persistence),
            ("Notes API - Get Notes", self.test_get_notes),
            ("Notes API - Create Note", self.test_create_note),
            ("Notes API - Delete Note", self.test_delete_note),
            ("Generate Posts", self.test_generate_posts),
        ]
        
        print(f"\n📋 Running {len(test_sequence)} focused tests...\n")
        
        for test_name, test_func in test_sequence:
            try:
                print(f"\n{'='*50}")
                print(f"🧪 {test_name}")
                print(f"{'='*50}")
                success = test_func()
                if success:
                    print(f"✅ {test_name} - PASSED")
                else:
                    print(f"❌ {test_name} - FAILED")
            except Exception as e:
                print(f"💥 {test_name} - ERROR: {str(e)}")
                self.tests_run += 1
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"📊 FOCUSED BACKEND TESTING SUMMARY")
        print(f"{'='*60}")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        print(f"{'='*60}")
        
        return self.tests_passed, self.tests_run


if __name__ == "__main__":
    tester = FocusedBackendTester()
    passed, total = tester.run_all_tests()
    
    print(f"\n🎯 FOCUSED BACKEND TESTING COMPLETE")
    print(f"Final Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)" if total > 0 else "No tests run")
    
    exit(0 if passed == total else 1)