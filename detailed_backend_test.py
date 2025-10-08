#!/usr/bin/env python3
"""
Detailed Backend Testing for Virtual Keyboard Bug Fix Verification
Testing specific endpoints mentioned in review request
"""

import requests
import json
import time
from datetime import datetime

class DetailedBackendTester:
    def __init__(self):
        # Use the production backend URL from frontend .env
        self.base_url = "https://post-restore.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_issues = []
        
        # Test credentials from review request
        self.test_email = "lperpere@yahoo.fr"
        self.test_password = "L@Reunion974!"
        
        print(f"🎯 DETAILED BACKEND TESTING - Virtual Keyboard Bug Fix Verification")
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_email}")
        print("=" * 80)

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test with detailed logging"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'

        self.tests_run += 1
        print(f"\n🔍 {self.tests_run}. {name}")
        print(f"   Method: {method}")
        print(f"   URL: {url}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)[:200]}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            print(f"   Response Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error Response: {json.dumps(error_data, indent=2)}")
                    if response.status_code >= 400:
                        self.critical_issues.append(f"{name}: {error_data}")
                except:
                    print(f"   Error Text: {response.text}")
                    if response.status_code >= 400:
                        self.critical_issues.append(f"{name}: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ FAILED - Exception: {str(e)}")
            self.critical_issues.append(f"{name}: Exception - {str(e)}")
            return False, {}

    def test_detailed_authentication(self):
        """Test authentication endpoints in detail"""
        print("\n" + "="*60)
        print("🔐 DETAILED AUTHENTICATION TESTING")
        print("="*60)
        
        # 1. Test login endpoint
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        success, response = self.run_test(
            "POST /api/auth/login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.access_token = response['access_token']
            self.user_id = response.get('user_id')
            print(f"   ✅ Login successful for {self.test_email}")
            print(f"   ✅ User ID: {self.user_id}")
            print(f"   ✅ Access Token: {self.access_token[:30]}...")
            print(f"   ✅ Business Name: {response.get('business_name')}")
        else:
            print(f"   ❌ Login failed for {self.test_email}")
            return False
        
        # 2. Test /api/auth/me endpoint
        success, response = self.run_test(
            "GET /api/auth/me",
            "GET",
            "auth/me",
            200
        )
        
        if success:
            print(f"   ✅ User info retrieved successfully")
            print(f"   ✅ Email: {response.get('email')}")
            print(f"   ✅ Subscription Status: {response.get('subscription_status')}")
            print(f"   ✅ Trial Days: {response.get('trial_days_remaining')}")
        else:
            print(f"   ❌ Failed to get current user info")
            return False
            
        return True

    def test_detailed_business_profile(self):
        """Test business profile endpoints in detail"""
        print("\n" + "="*60)
        print("🏢 DETAILED BUSINESS PROFILE TESTING (Critical for keyboard fix)")
        print("="*60)
        
        if not self.access_token:
            print("❌ No access token - skipping business profile tests")
            return False
        
        # 1. Test GET /api/business-profile
        success, get_response = self.run_test(
            "GET /api/business-profile",
            "GET",
            "business-profile",
            200
        )
        
        if success:
            print(f"   ✅ Business profile retrieved successfully")
            print(f"   ✅ Business Name: {get_response.get('business_name')}")
            print(f"   ✅ Business Type: {get_response.get('business_type')}")
            print(f"   ✅ Email: {get_response.get('email')}")
            print(f"   ✅ Website URL: {get_response.get('website_url')}")
            
            # Store original data for comparison
            original_data = get_response.copy()
        else:
            print(f"   ❌ Failed to get business profile")
            return False
        
        # 2. Test PUT /api/business-profile with comprehensive data
        test_profile_data = {
            "business_name": "Restaurant Le Bon Goût Réunionnais - Test Clavier",
            "business_type": "restaurant",
            "business_description": "Restaurant traditionnel réunionnais proposant une cuisine authentique avec des produits locaux de qualité. Test du clavier virtuel iPadOS 18+.",
            "target_audience": "Familles et touristes à La Réunion, amateurs de cuisine créole et traditionnelle",
            "brand_tone": "friendly",
            "posting_frequency": "3x_week",
            "preferred_platforms": ["Facebook", "Instagram"],
            "budget_range": "500-1000€",
            "email": "contact@bongoût-test-clavier.re",
            "website_url": "https://www.restaurant-bon-gout-reunion-test.fr",
            "hashtags_primary": ["#RestaurantReunion", "#CuisineCreole", "#BonGout", "#TestClavier"],
            "hashtags_secondary": ["#Reunion974", "#CuisineLocale", "#RestaurantTraditionnel", "#iPadOS18"]
        }
        
        success, put_response = self.run_test(
            "PUT /api/business-profile",
            "PUT",
            "business-profile",
            200,
            data=test_profile_data
        )
        
        if success:
            print(f"   ✅ Business profile updated successfully")
            if 'profile' in put_response:
                updated_profile = put_response['profile']
                print(f"   ✅ Updated Business Name: {updated_profile.get('business_name')}")
                print(f"   ✅ Updated Email: {updated_profile.get('email')}")
                print(f"   ✅ Updated Website: {updated_profile.get('website_url')}")
        else:
            print(f"   ❌ Failed to update business profile")
            return False
        
        # 3. Test immediate persistence (critical for virtual keyboard fix)
        print(f"\n   🔄 Testing immediate data persistence...")
        time.sleep(1)  # Small delay to ensure database write
        
        success, verify_response = self.run_test(
            "GET /api/business-profile (Persistence Check)",
            "GET",
            "business-profile",
            200
        )
        
        if success:
            # Check if our test data persisted
            persisted_name = verify_response.get('business_name', '')
            persisted_email = verify_response.get('email', '')
            persisted_website = verify_response.get('website_url', '')
            
            print(f"   📊 Persistence Check Results:")
            print(f"      Business Name: {persisted_name}")
            print(f"      Email: {persisted_email}")
            print(f"      Website: {persisted_website}")
            
            # Check if data matches what we sent
            if "Restaurant Le Bon Goût Réunionnais - Test Clavier" in persisted_name:
                print(f"   ✅ Business name persisted correctly")
            else:
                print(f"   ❌ Business name NOT persisted - got: {persisted_name}")
                self.critical_issues.append("Business Profile: Data not persisting after PUT request")
                return False
                
            if "contact@bongoût-test-clavier.re" in persisted_email:
                print(f"   ✅ Email persisted correctly")
            else:
                print(f"   ❌ Email NOT persisted - got: {persisted_email}")
                self.critical_issues.append("Business Profile: Email not persisting after PUT request")
                return False
                
            if "restaurant-bon-gout-reunion-test.fr" in persisted_website:
                print(f"   ✅ Website URL persisted correctly")
            else:
                print(f"   ❌ Website URL NOT persisted - got: {persisted_website}")
                self.critical_issues.append("Business Profile: Website URL not persisting after PUT request")
                return False
                
            print(f"   ✅ ALL CRITICAL BUSINESS PROFILE DATA PERSISTED CORRECTLY")
        else:
            print(f"   ❌ Failed to verify business profile persistence")
            return False
            
        return True

    def test_detailed_notes(self):
        """Test notes endpoints in detail"""
        print("\n" + "="*60)
        print("📝 DETAILED NOTES TESTING (Critical for keyboard fix)")
        print("="*60)
        
        if not self.access_token:
            print("❌ No access token - skipping notes tests")
            return False
        
        # 1. Test GET /api/notes
        success, get_response = self.run_test(
            "GET /api/notes",
            "GET",
            "notes",
            200
        )
        
        if success:
            notes = get_response.get('notes', [])
            print(f"   ✅ Notes retrieved successfully - {len(notes)} notes found")
        else:
            print(f"   ❌ Failed to get notes")
            return False
        
        # 2. Test POST /api/notes with realistic data
        test_note_data = {
            "content": "Test note pour vérification clavier virtuel iPadOS 18+ - Promotion carry poulet signature avec rougail saucisse et gratin chouchou",
            "description": "Note de test pour validation du système de clavier virtuel",
            "priority": "high"
        }
        
        success, post_response = self.run_test(
            "POST /api/notes",
            "POST",
            "notes",
            200,
            data=test_note_data
        )
        
        if success:
            created_note = post_response.get('note', {})
            test_note_id = created_note.get('note_id')
            print(f"   ✅ Note created successfully")
            print(f"   ✅ Note ID: {test_note_id}")
            print(f"   ✅ Content: {created_note.get('content', '')[:80]}...")
            
            # 3. Test DELETE /api/notes/{note_id}
            if test_note_id:
                success, delete_response = self.run_test(
                    f"DELETE /api/notes/{test_note_id}",
                    "DELETE",
                    f"notes/{test_note_id}",
                    200
                )
                
                if success:
                    print(f"   ✅ Note deleted successfully")
                else:
                    print(f"   ❌ Failed to delete note")
                    return False
            else:
                print(f"   ⚠️ No note ID to test deletion")
        else:
            print(f"   ❌ Failed to create note")
            return False
            
        return True

    def test_detailed_website_analysis(self):
        """Test website analysis endpoint in detail"""
        print("\n" + "="*60)
        print("🌐 DETAILED WEBSITE ANALYSIS TESTING")
        print("="*60)
        
        if not self.access_token:
            print("❌ No access token - skipping website analysis tests")
            return False
        
        # Test website analysis with realistic data
        analysis_data = {
            "website_url": "https://www.restaurant-bon-gout-reunion.fr",
            "force_reanalysis": True
        }
        
        success, response = self.run_test(
            "POST /api/website/analyze",
            "POST",
            "website/analyze",
            200,
            data=analysis_data
        )
        
        if success:
            print(f"   ✅ Website analysis completed successfully")
            print(f"   ✅ Analyzed URL: {response.get('website_url')}")
            print(f"   ✅ Analysis Status: {response.get('status')}")
            print(f"   ✅ Message: {response.get('message')}")
            
            if 'insights' in response:
                print(f"   ✅ Insights: {response['insights'][:100]}...")
            
            if 'suggestions' in response:
                suggestions = response['suggestions']
                print(f"   ✅ Suggestions ({len(suggestions)} items):")
                for i, suggestion in enumerate(suggestions[:3], 1):
                    print(f"      {i}. {suggestion}")
            
            print(f"   ✅ Analysis timestamp: {response.get('analyzed_at')}")
        else:
            print(f"   ❌ Website analysis failed")
            return False
            
        return True

    def test_core_functionality(self):
        """Test other core endpoints for basic functionality"""
        print("\n" + "="*60)
        print("⚙️ CORE FUNCTIONALITY TESTING")
        print("="*60)
        
        if not self.access_token:
            print("❌ No access token - skipping core tests")
            return False
        
        # Test health endpoint
        success1, health_response = self.run_test(
            "GET /api/health",
            "GET",
            "health",
            200
        )
        
        if success1:
            print(f"   ✅ API Health: {health_response.get('status')}")
            print(f"   ✅ Service: {health_response.get('service')}")
        
        # Test generate posts endpoint
        posts_data = {"count": 3}
        success2, posts_response = self.run_test(
            "POST /api/generate-posts",
            "POST",
            "generate-posts",
            200,
            data=posts_data
        )
        
        if success2:
            posts = posts_response.get('posts', [])
            print(f"   ✅ Generated {len(posts)} posts")
            if posts:
                print(f"   ✅ First post preview: {posts[0].get('content', '')[:60]}...")
        
        # Test bibliotheque endpoint
        success3, biblio_response = self.run_test(
            "GET /api/bibliotheque",
            "GET",
            "bibliotheque",
            200
        )
        
        if success3:
            files = biblio_response.get('files', [])
            print(f"   ✅ Bibliotheque accessible - {len(files)} files")
        
        return all([success1, success2, success3])

    def run_comprehensive_test(self):
        """Run comprehensive backend testing"""
        print("🚀 STARTING COMPREHENSIVE BACKEND TESTING")
        print("Testing backend functionality after virtual keyboard bug fixes")
        print("=" * 80)
        
        # Test sequence
        all_tests_passed = True
        
        # 1. Authentication Tests (Priority 1)
        auth_success = self.test_detailed_authentication()
        if not auth_success:
            print("❌ CRITICAL: Authentication tests failed - cannot proceed")
            return False
        
        # 2. Business Profile Tests (Priority 2 - Critical for keyboard fix)
        profile_success = self.test_detailed_business_profile()
        if not profile_success:
            all_tests_passed = False
        
        # 3. Notes Tests (Priority 3 - Critical for keyboard fix)
        notes_success = self.test_detailed_notes()
        if not notes_success:
            all_tests_passed = False
        
        # 4. Website Analysis Test (Priority 4)
        website_success = self.test_detailed_website_analysis()
        if not website_success:
            all_tests_passed = False
        
        # 5. Core Functionality Test (Priority 5)
        core_success = self.test_core_functionality()
        if not core_success:
            all_tests_passed = False
        
        # Final Summary
        self.print_final_summary(all_tests_passed)
        
        return all_tests_passed

    def print_final_summary(self, all_tests_passed):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE BACKEND TESTING SUMMARY")
        print("="*80)
        
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.critical_issues:
            print(f"\n❌ CRITICAL ISSUES FOUND ({len(self.critical_issues)}):")
            for i, issue in enumerate(self.critical_issues, 1):
                print(f"   {i}. {issue}")
        else:
            print(f"\n✅ NO CRITICAL ISSUES FOUND")
        
        print(f"\n🎯 BACKEND STATUS AFTER VIRTUAL KEYBOARD FIXES:")
        if success_rate >= 95:
            print("✅ EXCELLENT - Backend fully functional after frontend changes")
        elif success_rate >= 80:
            print("⚠️ GOOD - Backend mostly functional with minor issues")
        elif success_rate >= 60:
            print("⚠️ FAIR - Backend functional but has some issues")
        else:
            print("❌ POOR - Backend has significant issues")
        
        print("="*80)

if __name__ == "__main__":
    tester = DetailedBackendTester()
    tester.run_comprehensive_test()