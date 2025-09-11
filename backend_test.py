#!/usr/bin/env python3
"""
Backend Testing for User Data Diagnostic - lperpere@yahoo.fr
Testing user authentication, profile retrieval, content library, notes, and website analysis data
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://claire-marcus-pwa-1.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
        if error:
            print(f"    Error: {error}")
        print()
    
    def test_backend_health(self):
        """Test 1: Backend Health Check"""
        try:
            response = self.session.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Backend Health Check",
                    True,
                    f"Status: {data.get('status', 'unknown')}, Service: {data.get('service', 'unknown')}"
                )
                return True
            else:
                self.log_test(
                    "Backend Health Check",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.log_test("Backend Health Check", False, error=str(e))
            return False
    
    def test_user_authentication(self):
        """Test 2: User Authentication for lperpere@yahoo.fr"""
        try:
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                
                self.log_test(
                    "User Authentication",
                    True,
                    f"User ID: {self.user_id}, Email: {data.get('email')}, Token obtained"
                )
                return True
            else:
                self.log_test(
                    "User Authentication",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("User Authentication", False, error=str(e))
            return False
    
    def test_user_profile_retrieval(self):
        """Test 3: User Profile Retrieval"""
        if not self.token:
            self.log_test("User Profile Retrieval", False, error="No authentication token available")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/auth/me", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "User Profile Retrieval",
                    True,
                    f"User ID: {data.get('user_id')}, Email: {data.get('email')}, "
                    f"Name: {data.get('first_name', '')} {data.get('last_name', '')}, "
                    f"Business: {data.get('business_name', 'Not set')}, "
                    f"Subscription: {data.get('subscription_status', 'unknown')}"
                )
                return True
            else:
                self.log_test(
                    "User Profile Retrieval",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("User Profile Retrieval", False, error=str(e))
            return False
    
    def test_business_profile_data(self):
        """Test 4: Business Profile Data"""
        if not self.token:
            self.log_test("Business Profile Data", False, error="No authentication token available")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/business-profile", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if business profile has data
                has_data = any(value for value in data.values() if value is not None and value != "")
                
                if has_data:
                    business_fields = []
                    for key, value in data.items():
                        if value is not None and value != "":
                            if isinstance(value, list):
                                business_fields.append(f"{key}: {len(value)} items")
                            else:
                                business_fields.append(f"{key}: {str(value)[:50]}...")
                    
                    self.log_test(
                        "Business Profile Data",
                        True,
                        f"Business profile found with data: {', '.join(business_fields[:5])}"
                    )
                else:
                    self.log_test(
                        "Business Profile Data",
                        True,
                        "Business profile exists but is empty (all fields are null/empty)"
                    )
                return True
            else:
                self.log_test(
                    "Business Profile Data",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Business Profile Data", False, error=str(e))
            return False
    
    def test_content_library(self):
        """Test 5: Content Library/Uploads"""
        if not self.token:
            self.log_test("Content Library", False, error="No authentication token available")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/content/pending?limit=50", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                total = data.get("total", 0)
                
                if total > 0:
                    # Analyze content types
                    file_types = {}
                    sources = {}
                    months = {}
                    
                    for item in content_items:
                        # File types
                        file_type = item.get("file_type", "unknown")
                        file_types[file_type] = file_types.get(file_type, 0) + 1
                        
                        # Sources
                        source = item.get("source", "upload")
                        sources[source] = sources.get(source, 0) + 1
                        
                        # Attributed months
                        month = item.get("attributed_month", "unassigned")
                        months[month] = months.get(month, 0) + 1
                    
                    details = f"Total items: {total}, "
                    details += f"File types: {dict(file_types)}, "
                    details += f"Sources: {dict(sources)}, "
                    details += f"Months: {dict(months)}"
                    
                    self.log_test("Content Library", True, details)
                else:
                    self.log_test("Content Library", True, "Content library is empty (0 items)")
                return True
            else:
                self.log_test(
                    "Content Library",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Content Library", False, error=str(e))
            return False
    
    def test_notes_data(self):
        """Test 6: Notes Data (General and Monthly)"""
        if not self.token:
            self.log_test("Notes Data", False, error="No authentication token available")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/notes", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                notes = data.get("notes", [])
                
                if len(notes) > 0:
                    # Analyze notes
                    monthly_notes = 0
                    specific_month_notes = 0
                    priorities = {}
                    
                    for note in notes:
                        if note.get("is_monthly_note", False):
                            monthly_notes += 1
                        else:
                            specific_month_notes += 1
                        
                        priority = note.get("priority", "normal")
                        priorities[priority] = priorities.get(priority, 0) + 1
                    
                    details = f"Total notes: {len(notes)}, "
                    details += f"Monthly notes: {monthly_notes}, "
                    details += f"Specific month notes: {specific_month_notes}, "
                    details += f"Priorities: {dict(priorities)}"
                    
                    self.log_test("Notes Data", True, details)
                else:
                    self.log_test("Notes Data", True, "No notes found (empty notes collection)")
                return True
            else:
                self.log_test(
                    "Notes Data",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Notes Data", False, error=str(e))
            return False
    
    def test_generated_posts(self):
        """Test 7: Generated Posts Data"""
        if not self.token:
            self.log_test("Generated Posts", False, error="No authentication token available")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/posts/generated", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                
                if len(posts) > 0:
                    # Analyze posts
                    statuses = {}
                    platforms = {}
                    with_images = 0
                    
                    for post in posts:
                        status = post.get("status", "unknown")
                        statuses[status] = statuses.get(status, 0) + 1
                        
                        platform = post.get("platform", "unknown")
                        platforms[platform] = platforms.get(platform, 0) + 1
                        
                        if post.get("visual_url"):
                            with_images += 1
                    
                    details = f"Total posts: {len(posts)}, "
                    details += f"Statuses: {dict(statuses)}, "
                    details += f"Platforms: {dict(platforms)}, "
                    details += f"Posts with images: {with_images}"
                    
                    self.log_test("Generated Posts", True, details)
                else:
                    self.log_test("Generated Posts", True, "No generated posts found")
                return True
            else:
                self.log_test(
                    "Generated Posts",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Generated Posts", False, error=str(e))
            return False
    
    def test_database_connectivity(self):
        """Test 8: Database Connectivity Diagnostic"""
        try:
            response = self.session.get(f"{BACKEND_URL}/diag", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                db_connected = data.get("database_connected", False)
                db_name = data.get("database_name", "unknown")
                mongo_url_prefix = data.get("mongo_url_prefix", "unknown")
                environment = data.get("environment", "unknown")
                
                if db_connected:
                    self.log_test(
                        "Database Connectivity",
                        True,
                        f"Database connected: {db_connected}, DB name: {db_name}, "
                        f"Mongo URL prefix: {mongo_url_prefix}, Environment: {environment}"
                    )
                else:
                    self.log_test(
                        "Database Connectivity",
                        False,
                        error=f"Database not connected. DB name: {db_name}, Environment: {environment}"
                    )
                return db_connected
            else:
                self.log_test(
                    "Database Connectivity",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Database Connectivity", False, error=str(e))
            return False
    
    def run_comprehensive_diagnostic(self):
        """Run comprehensive diagnostic for user data issues"""
        print("=" * 80)
        print("🔍 COMPREHENSIVE USER DATA DIAGNOSTIC")
        print(f"📧 Testing user: {TEST_EMAIL}")
        print(f"🌐 Backend URL: {BACKEND_URL}")
        print(f"⏰ Test started: {datetime.now().isoformat()}")
        print("=" * 80)
        print()
        
        # Run all tests
        tests = [
            self.test_backend_health,
            self.test_database_connectivity,
            self.test_user_authentication,
            self.test_user_profile_retrieval,
            self.test_business_profile_data,
            self.test_content_library,
            self.test_notes_data,
            self.test_generated_posts
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_func.__name__}: {str(e)}")
        
        # Summary
        print("=" * 80)
        print("📊 DIAGNOSTIC SUMMARY")
        print("=" * 80)
        print(f"✅ Tests passed: {passed_tests}/{total_tests}")
        print(f"❌ Tests failed: {total_tests - passed_tests}/{total_tests}")
        print(f"📈 Success rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Critical findings
        print("🔍 CRITICAL FINDINGS:")
        print("-" * 40)
        
        if not self.token:
            print("❌ AUTHENTICATION FAILURE - User cannot log in")
            print("   → Check if user exists in database")
            print("   → Verify password is correct")
            print("   → Check database connectivity")
        else:
            print("✅ Authentication working - User can log in successfully")
            print(f"   → User ID: {self.user_id}")
        
        # Analyze test results for patterns
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print()
            print("❌ FAILED TESTS ANALYSIS:")
            for result in failed_tests:
                print(f"   • {result['test']}: {result['error']}")
        
        print()
        print("🎯 RECOMMENDATIONS:")
        print("-" * 40)
        
        if not self.token:
            print("1. Check user account exists in MongoDB users collection")
            print("2. Verify database connection and credentials")
            print("3. Check if user data was properly migrated to new domain")
        else:
            # Check what data is missing
            content_test = next((r for r in self.test_results if r["test"] == "Content Library"), None)
            notes_test = next((r for r in self.test_results if r["test"] == "Notes Data"), None)
            business_test = next((r for r in self.test_results if r["test"] == "Business Profile Data"), None)
            
            if content_test and "empty" in content_test.get("details", ""):
                print("1. Content library is empty - check if media collection has user's data")
            if notes_test and "No notes found" in notes_test.get("details", ""):
                print("2. Notes collection is empty - check if content_notes collection has user's data")
            if business_test and "empty" in business_test.get("details", ""):
                print("3. Business profile is empty - check if business_profiles collection has user's data")
        
        print()
        print("=" * 80)
        return passed_tests == total_tests

def main():
    """Main test execution"""
    tester = BackendTester()
    success = tester.run_comprehensive_diagnostic()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()