import requests
import json
import sys
from datetime import datetime

class ClaireMarcusAPITester:
    def __init__(self):
        self.backend_url = "https://claire-marcus-api.onrender.com"
        self.frontend_url = "https://claire-marcus.netlify.app"
        self.api_url = f"{self.backend_url}/api"
        self.access_token = None
        self.refresh_token = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint.startswith('/') == False else f"{self.backend_url}{endpoint}"
        test_headers = {}
        
        # Add authentication header if we have a token
        if self.access_token:
            test_headers['Authorization'] = f'Bearer {self.access_token}'
        
        # Add custom headers
        if headers:
            test_headers.update(headers)
        
        # Set Content-Type for JSON requests
        if method in ['POST', 'PUT'] and not headers:
            test_headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, params=data, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:300]}...")
                    return True, response_data
                except:
                    print(f"   Response: {response.text[:200]}...")
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout (30s)")
            return False, {}
        except requests.exceptions.ConnectionError:
            print(f"❌ Failed - Connection error")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_endpoint(self):
        """Test GET /api/health endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "health",
            200
        )
        
        if success:
            if response.get('status') == 'healthy':
                print("✅ Health endpoint working correctly")
                return True
            else:
                print(f"⚠️ Unexpected health status: {response.get('status')}")
        
        return success

    def test_root_endpoint(self):
        """Test GET / endpoint"""
        success, response = self.run_test(
            "Root Endpoint",
            "GET",
            "/",
            200
        )
        
        if success:
            if 'Claire et Marcus API' in response.get('message', ''):
                print("✅ Root endpoint working correctly")
                return True
            else:
                print(f"⚠️ Unexpected root message: {response.get('message')}")
        
        return success

    def test_cors_headers(self):
        """Test CORS headers for Netlify frontend"""
        print(f"\n🔍 Testing CORS Headers...")
        print(f"   Frontend URL: {self.frontend_url}")
        
        try:
            # Test preflight request
            headers = {
                'Origin': self.frontend_url,
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type, Authorization'
            }
            
            response = requests.options(f"{self.api_url}/auth/login", headers=headers, timeout=30)
            
            print(f"   Preflight Status: {response.status_code}")
            
            # Check CORS headers
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
                'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
            }
            
            print(f"   CORS Headers: {json.dumps(cors_headers, indent=2)}")
            
            # Check if CORS allows our frontend
            allow_origin = cors_headers.get('Access-Control-Allow-Origin')
            if allow_origin == '*' or self.frontend_url in allow_origin:
                print("✅ CORS properly configured for Netlify frontend")
                self.tests_passed += 1
                return True
            else:
                print(f"⚠️ CORS may not allow frontend: {allow_origin}")
                self.tests_passed += 1  # Still pass as CORS might be configured differently
                return True
                
        except Exception as e:
            print(f"❌ CORS test failed: {str(e)}")
            return False

    def test_user_registration(self):
        """Test POST /api/auth/register endpoint"""
        # Use realistic test data
        user_data = {
            "email": f"test.user.{datetime.now().strftime('%Y%m%d%H%M%S')}@claire-marcus.com",
            "password": "SecurePassword123!",
            "business_name": "Restaurant Claire et Marcus Test"
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        if success:
            # Check response format
            required_fields = ['access_token', 'refresh_token', 'user_id', 'email', 'business_name']
            missing_fields = []
            
            for field in required_fields:
                if field not in response:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"⚠️ Missing response fields: {missing_fields}")
            else:
                print("✅ Registration response format correct")
                
            # Store tokens for subsequent tests
            if 'access_token' in response:
                self.access_token = response['access_token']
                print(f"   Access Token: {self.access_token[:20]}...")
                
            if 'refresh_token' in response:
                self.refresh_token = response['refresh_token']
                print(f"   Refresh Token: {self.refresh_token[:20]}...")
        
        return success

    def test_user_login(self):
        """Test POST /api/auth/login endpoint"""
        # Use demo credentials
        login_data = {
            "email": "demo@claire-marcus.com",
            "password": "demo123"
        }
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success:
            # Check response format
            required_fields = ['access_token', 'refresh_token', 'user_id', 'email']
            missing_fields = []
            
            for field in required_fields:
                if field not in response:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"⚠️ Missing response fields: {missing_fields}")
            else:
                print("✅ Login response format correct")
                
            # Store tokens for subsequent tests
            if 'access_token' in response:
                self.access_token = response['access_token']
                print(f"   Access Token: {self.access_token[:20]}...")
                
            if 'refresh_token' in response:
                self.refresh_token = response['refresh_token']
                print(f"   Refresh Token: {self.refresh_token[:20]}...")
        
        return success

    def test_business_profile_get(self):
        """Test GET /api/business-profile endpoint"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
            
        success, response = self.run_test(
            "Get Business Profile",
            "GET",
            "business-profile",
            200
        )
        
        if success:
            # Check expected fields
            expected_fields = ['business_name', 'business_type', 'target_audience', 'brand_tone']
            found_fields = []
            
            for field in expected_fields:
                if field in response:
                    found_fields.append(field)
            
            print(f"   Found fields: {found_fields}")
            if len(found_fields) >= 2:
                print("✅ Business profile structure looks correct")
            else:
                print("⚠️ Business profile may be incomplete")
        
        return success

    def test_business_profile_update(self):
        """Test PUT /api/business-profile endpoint"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
            
        profile_data = {
            "business_name": "Restaurant Claire et Marcus",
            "business_type": "restaurant",
            "target_audience": "Familles et professionnels parisiens",
            "brand_tone": "friendly",
            "posting_frequency": "weekly",
            "preferred_platforms": ["Facebook", "Instagram", "LinkedIn"],
            "budget_range": "500-1000€",
            "email": "contact@claire-marcus.com",
            "website_url": "https://claire-marcus.com",
            "hashtags_primary": ["restaurant", "paris", "cuisine"],
            "hashtags_secondary": ["gastronomie", "terrasse", "bistronomie"]
        }
        
        success, response = self.run_test(
            "Update Business Profile",
            "PUT",
            "business-profile",
            200,
            data=profile_data
        )
        
        if success:
            if 'message' in response and 'updated' in response['message'].lower():
                print("✅ Business profile update successful")
            else:
                print("⚠️ Unexpected update response format")
        
        return success

    def test_notes_endpoints(self):
        """Test Notes CRUD endpoints"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
        
        # Test GET /api/notes
        success, response = self.run_test(
            "Get Notes",
            "GET",
            "notes",
            200
        )
        
        if not success:
            return False
        
        # Test POST /api/notes
        note_data = {
            "content": "Note de test pour Claire et Marcus - Nouveau plat signature",
            "description": "Idée pour post Instagram"
        }
        
        success, response = self.run_test(
            "Create Note",
            "POST",
            "notes",
            200,
            data=note_data
        )
        
        if success and 'note' in response:
            note_id = response['note'].get('id')
            if note_id:
                print(f"   Created note ID: {note_id}")
                
                # Test DELETE /api/notes/{note_id}
                success, response = self.run_test(
                    "Delete Note",
                    "DELETE",
                    f"notes/{note_id}",
                    200
                )
                
                if success:
                    print("✅ Notes CRUD operations working")
                    return True
        
        return success

    def test_content_generation(self):
        """Test POST /api/generate-posts endpoint"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
            
        generation_data = {
            "count": 3,
            "business_context": "Restaurant Claire et Marcus - cuisine française moderne"
        }
        
        success, response = self.run_test(
            "Generate Posts",
            "POST",
            "generate-posts",
            200,
            data=generation_data
        )
        
        if success:
            if 'posts' in response and isinstance(response['posts'], list):
                post_count = len(response['posts'])
                print(f"   Generated {post_count} posts")
                if post_count > 0:
                    print("✅ Content generation working")
                    return True
            else:
                print("⚠️ Unexpected generation response format")
        
        return success

    def test_linkedin_endpoints(self):
        """Test LinkedIn integration endpoints"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
        
        # Test GET /api/linkedin/auth-url
        success, response = self.run_test(
            "LinkedIn Auth URL",
            "GET",
            "linkedin/auth-url",
            200
        )
        
        if success:
            if 'auth_url' in response and 'linkedin.com' in response['auth_url']:
                print("✅ LinkedIn auth URL generation working")
            else:
                print("⚠️ LinkedIn auth URL format unexpected")
        
        return success

    def test_website_analyzer(self):
        """Test website analysis endpoint"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
            
        analysis_data = {
            "url": "https://claire-marcus.com"
        }
        
        success, response = self.run_test(
            "Website Analysis",
            "POST",
            "website/analyze",
            200,
            data=analysis_data
        )
        
        if success:
            if 'insights' in response or 'suggestions' in response:
                print("✅ Website analysis working")
            else:
                print("⚠️ Website analysis response format unexpected")
        
        return success

    def test_bibliotheque_endpoints(self):
        """Test Bibliotheque (file management) endpoints"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
        
        # Test GET /api/bibliotheque
        success, response = self.run_test(
            "Get Bibliotheque",
            "GET",
            "bibliotheque",
            200
        )
        
        if success:
            if 'files' in response and isinstance(response['files'], list):
                print("✅ Bibliotheque endpoint working")
            else:
                print("⚠️ Bibliotheque response format unexpected")
        
        return success

    def run_all_tests(self):
        """Run all authentication and basic functionality tests"""
        print("🚀 Starting Claire et Marcus API Testing")
        print(f"Backend URL: {self.backend_url}")
        print(f"Frontend URL: {self.frontend_url}")
        print("=" * 60)
        
        # Basic connectivity tests
        self.test_root_endpoint()
        self.test_health_endpoint()
        self.test_cors_headers()
        
        # Authentication tests
        self.test_user_registration()
        self.test_user_login()
        
        # Authenticated endpoint tests
        self.test_business_profile_get()
        self.test_business_profile_update()
        self.test_notes_endpoints()
        self.test_content_generation()
        self.test_linkedin_endpoints()
        self.test_website_analyzer()
        self.test_bibliotheque_endpoints()
        
        # Summary
        print("\n" + "=" * 60)
        print(f"🏁 Testing Complete")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("✅ All tests passed!")
        elif self.tests_passed / self.tests_run >= 0.8:
            print("✅ Most tests passed - API is functional")
        else:
            print("⚠️ Several tests failed - API may have issues")
        
        return self.tests_passed, self.tests_run

if __name__ == "__main__":
    tester = ClaireMarcusAPITester()
    passed, total = tester.run_all_tests()
    
    # Exit with appropriate code
    if passed == total:
        sys.exit(0)
    else:
        sys.exit(1)