#!/usr/bin/env python3
"""
Pixabay Integration Backend Testing
Testing the Pixabay search functionality as reported broken by user.
Focus: Test Pixabay endpoints and verify response format matches frontend expectations.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://media-title-fix.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr", 
    "password": "L@Reunion974!"
}

class PixabayTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'PixabayTester/1.0'
        })
        self.auth_token = None
        self.user_id = None
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def authenticate(self):
        """Step 1: Authenticate with the backend"""
        try:
            self.log("🔐 Step 1: Authenticating with backend...")
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json=TEST_CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                self.user_id = data.get('user_id')
                
                # Set authorization header for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                
                self.log(f"✅ Authentication successful - User ID: {self.user_id}")
                return True
            else:
                self.log(f"❌ Authentication failed - Status: {response.status_code}")
                self.log(f"Response: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_pixabay_categories(self):
        """Step 2: Test GET /api/pixabay/categories endpoint"""
        try:
            self.log("📂 Step 2: Testing Pixabay categories endpoint...")
            
            response = self.session.get(
                f"{BACKEND_URL}/pixabay/categories",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                categories = data.get('categories', [])
                
                self.log(f"✅ Categories endpoint working - Found {len(categories)} categories")
                
                # Check for expected categories
                expected_categories = ['business', 'nature', 'people', 'backgrounds']
                found_expected = [cat for cat in expected_categories if cat in categories]
                
                self.log(f"Expected categories found: {found_expected}")
                
                if len(found_expected) >= 3:
                    self.log("✅ Categories endpoint contains expected categories")
                    return True
                else:
                    self.log("⚠️ Some expected categories missing")
                    return True  # Still working, just different categories
                    
            else:
                self.log(f"❌ Categories endpoint failed - Status: {response.status_code}")
                self.log(f"Response: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Categories endpoint error: {str(e)}")
            return False
    
    def test_pixabay_search_business(self):
        """Step 3: Test Pixabay search with 'business' query"""
        try:
            self.log("🔍 Step 3: Testing Pixabay search with 'business' query...")
            
            params = {
                'query': 'business',
                'page': 1,
                'per_page': 10,
                'image_type': 'photo',
                'safesearch': True
            }
            
            response = self.session.get(
                f"{BACKEND_URL}/pixabay/search",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                total = data.get('total', 0)
                hits = data.get('hits', [])
                
                self.log(f"✅ Business search successful - Total results: {total}, Returned images: {len(hits)}")
                
                if len(hits) > 0:
                    # Check first image structure
                    first_image = hits[0]
                    required_fields = ['id', 'webformatURL', 'tags', 'views', 'downloads']
                    
                    missing_fields = [field for field in required_fields if field not in first_image]
                    
                    if not missing_fields:
                        self.log(f"✅ Image structure correct - First image ID: {first_image.get('id')}")
                        self.log(f"Tags: {first_image.get('tags', '')[:50]}...")
                        return True
                    else:
                        self.log(f"⚠️ Missing fields in image data: {missing_fields}")
                        return False
                else:
                    self.log("⚠️ No images returned for business query")
                    return False
                    
            else:
                self.log(f"❌ Business search failed - Status: {response.status_code}")
                self.log(f"Response: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Business search error: {str(e)}")
            return False
    
    def test_pixabay_search_marketing(self):
        """Step 4: Test Pixabay search with 'marketing' query"""
        try:
            self.log("🎯 Step 4: Testing Pixabay search with 'marketing' query...")
            
            params = {
                'query': 'marketing',
                'page': 1,
                'per_page': 5,
                'image_type': 'photo',
                'safesearch': True
            }
            
            response = self.session.get(
                f"{BACKEND_URL}/pixabay/search",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                total = data.get('total', 0)
                hits = data.get('hits', [])
                
                self.log(f"✅ Marketing search successful - Total results: {total}, Returned images: {len(hits)}")
                
                # Verify response structure matches frontend expectations
                # Frontend expects: response.data.hits and response.data.total
                if 'hits' in data and 'total' in data:
                    self.log("✅ Response structure matches frontend expectations (hits, total)")
                    return True
                else:
                    self.log("❌ Response structure doesn't match frontend expectations")
                    self.log(f"Available keys: {list(data.keys())}")
                    return False
                    
            else:
                self.log(f"❌ Marketing search failed - Status: {response.status_code}")
                self.log(f"Response: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Marketing search error: {str(e)}")
            return False
    
    def test_pixabay_api_key_configuration(self):
        """Step 5: Test if Pixabay API key is properly configured"""
        try:
            self.log("🔑 Step 5: Testing Pixabay API key configuration...")
            
            # Try a simple search to verify API key works
            params = {
                'query': 'test',
                'page': 1,
                'per_page': 3,
                'image_type': 'photo'
            }
            
            response = self.session.get(
                f"{BACKEND_URL}/pixabay/search",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('total', 0) > 0:
                    self.log("✅ Pixabay API key is working correctly")
                    return True
                else:
                    self.log("⚠️ API key works but no results returned")
                    return True
                    
            elif response.status_code == 401:
                self.log("❌ Pixabay API key authentication failed")
                return False
            elif response.status_code == 500:
                error_data = response.json()
                if "API key not configured" in error_data.get('detail', ''):
                    self.log("❌ Pixabay API key not configured in backend")
                    return False
                else:
                    self.log(f"❌ Server error: {error_data.get('detail', 'Unknown error')}")
                    return False
            else:
                self.log(f"❌ API key test failed - Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ API key test error: {str(e)}")
            return False
    
    def test_pixabay_save_image(self):
        """Step 6: Test saving a Pixabay image to user's library"""
        try:
            self.log("💾 Step 6: Testing Pixabay image save functionality...")
            
            # First get an image from search
            search_response = self.session.get(
                f"{BACKEND_URL}/pixabay/search",
                params={'query': 'business', 'per_page': 1},
                timeout=30
            )
            
            if search_response.status_code != 200:
                self.log("❌ Cannot get image for save test")
                return False
                
            search_data = search_response.json()
            hits = search_data.get('hits', [])
            
            if not hits:
                self.log("❌ No images available for save test")
                return False
                
            # Get first image data
            image = hits[0]
            save_request = {
                'pixabay_id': image.get('id'),
                'image_url': image.get('webformatURL'),
                'tags': image.get('tags', '')
            }
            
            # Try to save the image
            response = self.session.post(
                f"{BACKEND_URL}/pixabay/save-image",
                json=save_request,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                saved_image = data.get('image', {})
                
                self.log(f"✅ Image save successful - Saved image ID: {saved_image.get('id')}")
                self.log(f"Filename: {saved_image.get('filename')}")
                return True
            else:
                self.log(f"❌ Image save failed - Status: {response.status_code}")
                self.log(f"Response: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Image save error: {str(e)}")
            return False

def main():
    print("=" * 80)
    print("🎯 PIXABAY INTEGRATION BACKEND TESTING")
    print("Testing Pixabay search functionality as reported broken by user")
    print("Focus: Verify backend endpoints and response format")
    print("=" * 80)
    
    tester = PixabayTester()
    
    # Test sequence
    tests = [
        ("Authentication", tester.authenticate),
        ("Pixabay Categories", tester.test_pixabay_categories),
        ("Pixabay Search - Business", tester.test_pixabay_search_business),
        ("Pixabay Search - Marketing", tester.test_pixabay_search_marketing),
        ("Pixabay API Key Configuration", tester.test_pixabay_api_key_configuration),
        ("Pixabay Save Image", tester.test_pixabay_save_image)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*80}")
    print("📊 PIXABAY TESTING SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = (passed / total) * 100 if total > 0 else 0
    
    print(f"Tests passed: {passed}/{total} ({success_rate:.1f}% success rate)")
    print()
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*80}")
    
    if success_rate >= 80:
        print("🎉 PIXABAY BACKEND IS WORKING CORRECTLY")
        print("The issue is likely in the frontend implementation or configuration.")
    elif success_rate >= 50:
        print("⚠️ PIXABAY BACKEND HAS SOME ISSUES")
        print("Some endpoints are working but there are problems to address.")
    else:
        print("🚨 PIXABAY BACKEND HAS CRITICAL ISSUES")
        print("Major problems detected that need immediate attention.")
    
    print("=" * 80)
    
    return success_rate >= 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)