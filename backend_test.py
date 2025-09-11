#!/usr/bin/env python3
"""
URGENT MongoDB Connection and User Data Retrieval Diagnostic Test
Testing for user lperpere@yahoo.fr / user_id: 6a670c66-c06c-4d75-9dd5-c747e8a0281a
Issue: User can login but sees NO business data for "My Own Watch" company
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://claire-marcus-pwa-1.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"
EXPECTED_USER_ID = "6a670c66-c06c-4d75-9dd5-c747e8a0281a"
EXPECTED_COMPANY = "My Own Watch"

class MongoDBDataDiagnostic:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def authenticate(self):
        """Step 1: Authenticate user and verify credentials"""
        self.log("🔐 STEP 1: Authenticating user lperpere@yahoo.fr")
        
        try:
            response = self.session.post(f"{BASE_URL}/auth/login-robust", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                self.log(f"✅ Authentication successful")
                self.log(f"   User ID: {self.user_id}")
                self.log(f"   Expected: {EXPECTED_USER_ID}")
                self.log(f"   Match: {'✅ YES' if self.user_id == EXPECTED_USER_ID else '❌ NO'}")
                self.log(f"   Token: {self.token[:20]}..." if self.token else "   Token: None")
                
                # Set authorization header for subsequent requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}'
                })
                
                return True
            else:
                self.log(f"❌ Authentication failed: {response.status_code}", "ERROR")
                self.log(f"   Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Authentication error: {str(e)}", "ERROR")
            return False
    
    def test_mongodb_connection(self):
        """Step 2: Test MongoDB connection via diagnostic endpoint"""
        self.log("🔍 STEP 2: Testing MongoDB connection")
        
        try:
            response = self.session.get(f"{BASE_URL}/diag")
            
            if response.status_code == 200:
                data = response.json()
                db_connected = data.get("database_connected", False)
                db_name = data.get("database_name", "Unknown")
                mongo_url_prefix = data.get("mongo_url_prefix", "Unknown")
                
                self.log(f"✅ Diagnostic endpoint accessible")
                self.log(f"   Database connected: {'✅ YES' if db_connected else '❌ NO'}")
                self.log(f"   Database name: {db_name}")
                self.log(f"   MongoDB URL prefix: {mongo_url_prefix}")
                
                return db_connected
            else:
                self.log(f"❌ Diagnostic endpoint failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ MongoDB connection test error: {str(e)}", "ERROR")
            return False
    
    def test_user_profile(self):
        """Step 3: Test GET /api/users/me (user profile)"""
        self.log("👤 STEP 3: Testing user profile endpoint")
        
        try:
            response = self.session.get(f"{BASE_URL}/auth/me")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ User profile endpoint accessible")
                self.log(f"   User ID: {data.get('user_id', 'Not found')}")
                self.log(f"   Email: {data.get('email', 'Not found')}")
                self.log(f"   Business name: {data.get('business_name', 'Not found')}")
                self.log(f"   First name: {data.get('first_name', 'Not found')}")
                self.log(f"   Last name: {data.get('last_name', 'Not found')}")
                self.log(f"   Subscription: {data.get('subscription_status', 'Not found')}")
                
                # Check if business name matches expected
                business_name = data.get('business_name', '')
                if business_name == EXPECTED_COMPANY:
                    self.log(f"   ✅ Business name matches: {EXPECTED_COMPANY}")
                elif business_name:
                    self.log(f"   ⚠️ Business name different: '{business_name}' vs expected '{EXPECTED_COMPANY}'")
                else:
                    self.log(f"   ❌ Business name is empty or missing")
                
                return True, data
            else:
                self.log(f"❌ User profile endpoint failed: {response.status_code}", "ERROR")
                self.log(f"   Response: {response.text}", "ERROR")
                return False, None
                
        except Exception as e:
            self.log(f"❌ User profile test error: {str(e)}", "ERROR")
            return False, None
    
    def test_business_profile(self):
        """Step 4: Test GET /api/business-profile (business profile)"""
        self.log("🏢 STEP 4: Testing business profile endpoint")
        
        try:
            response = self.session.get(f"{BASE_URL}/business-profile")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Business profile endpoint accessible")
                
                # Check all business profile fields
                fields_to_check = [
                    'business_name', 'business_type', 'business_description', 
                    'target_audience', 'brand_tone', 'posting_frequency',
                    'preferred_platforms', 'budget_range', 'email', 
                    'website_url', 'coordinates', 'hashtags_primary', 'hashtags_secondary'
                ]
                
                empty_fields = 0
                populated_fields = 0
                
                for field in fields_to_check:
                    value = data.get(field)
                    if value is None or value == "" or (isinstance(value, list) and len(value) == 0):
                        empty_fields += 1
                        self.log(f"   ❌ {field}: Empty/None")
                    else:
                        populated_fields += 1
                        if field == 'business_name':
                            if value == EXPECTED_COMPANY:
                                self.log(f"   ✅ {field}: '{value}' (matches expected)")
                            else:
                                self.log(f"   ⚠️ {field}: '{value}' (expected '{EXPECTED_COMPANY}')")
                        else:
                            self.log(f"   ✅ {field}: {value}")
                
                self.log(f"   📊 Summary: {populated_fields} populated, {empty_fields} empty fields")
                
                if populated_fields == 0:
                    self.log(f"   🚨 CRITICAL: ALL business profile fields are empty!", "ERROR")
                    return False, data
                else:
                    return True, data
                    
            else:
                self.log(f"❌ Business profile endpoint failed: {response.status_code}", "ERROR")
                self.log(f"   Response: {response.text}", "ERROR")
                return False, None
                
        except Exception as e:
            self.log(f"❌ Business profile test error: {str(e)}", "ERROR")
            return False, None
    
    def test_content_library(self):
        """Step 5: Test GET /api/content/pending (content library)"""
        self.log("📚 STEP 5: Testing content library endpoint")
        
        try:
            response = self.session.get(f"{BASE_URL}/content/pending")
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get('content', [])
                total = data.get('total', 0)
                loaded = data.get('loaded', 0)
                
                self.log(f"✅ Content library endpoint accessible")
                self.log(f"   Total content items: {total}")
                self.log(f"   Loaded items: {loaded}")
                self.log(f"   Items in response: {len(content_items)}")
                
                if total == 0:
                    self.log(f"   🚨 CRITICAL: No content items found for user!", "ERROR")
                    return False, data
                else:
                    # Show sample content items
                    for i, item in enumerate(content_items[:3]):  # Show first 3 items
                        self.log(f"   📄 Item {i+1}: {item.get('filename', 'No filename')} ({item.get('file_type', 'Unknown type')})")
                        self.log(f"      ID: {item.get('id', 'No ID')}")
                        self.log(f"      Title: {item.get('title', 'No title')}")
                        self.log(f"      Context: {item.get('context', 'No context')}")
                    
                    if len(content_items) > 3:
                        self.log(f"   ... and {len(content_items) - 3} more items")
                    
                    return True, data
                    
            else:
                self.log(f"❌ Content library endpoint failed: {response.status_code}", "ERROR")
                self.log(f"   Response: {response.text}", "ERROR")
                return False, None
                
        except Exception as e:
            self.log(f"❌ Content library test error: {str(e)}", "ERROR")
            return False, None
    
    def test_user_notes(self):
        """Step 6: Test GET /api/notes (user notes)"""
        self.log("📝 STEP 6: Testing user notes endpoint")
        
        try:
            response = self.session.get(f"{BASE_URL}/notes")
            
            if response.status_code == 200:
                data = response.json()
                notes = data.get('notes', [])
                
                self.log(f"✅ User notes endpoint accessible")
                self.log(f"   Total notes: {len(notes)}")
                
                if len(notes) == 0:
                    self.log(f"   ⚠️ No notes found for user")
                    return True, data  # Empty notes is not necessarily an error
                else:
                    # Show sample notes
                    for i, note in enumerate(notes[:3]):  # Show first 3 notes
                        self.log(f"   📝 Note {i+1}: {note.get('description', 'No description')}")
                        self.log(f"      Content: {note.get('content', 'No content')[:50]}...")
                        self.log(f"      Priority: {note.get('priority', 'No priority')}")
                    
                    if len(notes) > 3:
                        self.log(f"   ... and {len(notes) - 3} more notes")
                    
                    return True, data
                    
            else:
                self.log(f"❌ User notes endpoint failed: {response.status_code}", "ERROR")
                self.log(f"   Response: {response.text}", "ERROR")
                return False, None
                
        except Exception as e:
            self.log(f"❌ User notes test error: {str(e)}", "ERROR")
            return False, None
    
    def test_generated_posts(self):
        """Step 7: Test GET /api/posts/generated (generated posts)"""
        self.log("📱 STEP 7: Testing generated posts endpoint")
        
        try:
            response = self.session.get(f"{BASE_URL}/posts/generated")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('posts', [])
                count = data.get('count', 0)
                
                self.log(f"✅ Generated posts endpoint accessible")
                self.log(f"   Total posts: {count}")
                self.log(f"   Posts in response: {len(posts)}")
                
                if count == 0:
                    self.log(f"   ⚠️ No generated posts found for user")
                    return True, data  # Empty posts is not necessarily an error
                else:
                    # Show sample posts
                    for i, post in enumerate(posts[:3]):  # Show first 3 posts
                        self.log(f"   📱 Post {i+1}: {post.get('title', 'No title')}")
                        self.log(f"      Status: {post.get('status', 'No status')}")
                        self.log(f"      Platform: {post.get('platform', 'No platform')}")
                        self.log(f"      Scheduled: {post.get('scheduled_date', 'No date')}")
                    
                    if len(posts) > 3:
                        self.log(f"   ... and {len(posts) - 3} more posts")
                    
                    return True, data
                    
            else:
                self.log(f"❌ Generated posts endpoint failed: {response.status_code}", "ERROR")
                self.log(f"   Response: {response.text}", "ERROR")
                return False, None
                
        except Exception as e:
            self.log(f"❌ Generated posts test error: {str(e)}", "ERROR")
            return False, None
    
    def run_comprehensive_diagnostic(self):
        """Run complete diagnostic test suite"""
        self.log("🚀 STARTING COMPREHENSIVE MONGODB DATA DIAGNOSTIC")
        self.log(f"   Target user: {TEST_EMAIL}")
        self.log(f"   Expected user ID: {EXPECTED_USER_ID}")
        self.log(f"   Expected company: {EXPECTED_COMPANY}")
        self.log(f"   Backend URL: {BASE_URL}")
        self.log("=" * 80)
        
        results = {
            'authentication': False,
            'mongodb_connection': False,
            'user_profile': False,
            'business_profile': False,
            'content_library': False,
            'user_notes': False,
            'generated_posts': False
        }
        
        # Step 1: Authentication
        if not self.authenticate():
            self.log("🚨 CRITICAL: Authentication failed - cannot proceed with data tests", "ERROR")
            return results
        results['authentication'] = True
        
        # Step 2: MongoDB Connection
        results['mongodb_connection'] = self.test_mongodb_connection()
        
        # Step 3: User Profile
        success, data = self.test_user_profile()
        results['user_profile'] = success
        
        # Step 4: Business Profile
        success, data = self.test_business_profile()
        results['business_profile'] = success
        
        # Step 5: Content Library
        success, data = self.test_content_library()
        results['content_library'] = success
        
        # Step 6: User Notes
        success, data = self.test_user_notes()
        results['user_notes'] = success
        
        # Step 7: Generated Posts
        success, data = self.test_generated_posts()
        results['generated_posts'] = success
        
        # Final Summary
        self.log("=" * 80)
        self.log("🎯 DIAGNOSTIC SUMMARY")
        
        passed_tests = sum(1 for result in results.values() if result)
        total_tests = len(results)
        success_rate = (passed_tests / total_tests) * 100
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"   {test_name.replace('_', ' ').title()}: {status}")
        
        self.log(f"📊 Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        # Critical Issues Analysis
        critical_issues = []
        if not results['authentication']:
            critical_issues.append("Authentication failure prevents all data access")
        if not results['mongodb_connection']:
            critical_issues.append("MongoDB connection issue - database not accessible")
        if not results['business_profile']:
            critical_issues.append("Business profile data missing or empty - explains empty forms")
        if not results['content_library']:
            critical_issues.append("Content library empty - no media files found")
        
        if critical_issues:
            self.log("🚨 CRITICAL ISSUES IDENTIFIED:")
            for issue in critical_issues:
                self.log(f"   • {issue}", "ERROR")
        else:
            self.log("✅ No critical issues found - data retrieval working correctly")
        
        return results

def main():
    """Main test execution"""
    diagnostic = MongoDBDataDiagnostic()
    results = diagnostic.run_comprehensive_diagnostic()
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)  # All tests passed
    else:
        sys.exit(1)  # Some tests failed

if __name__ == "__main__":
    main()