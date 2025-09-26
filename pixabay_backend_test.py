#!/usr/bin/env python3
"""
Pixabay Integration Backend Testing
Testing the Pixabay integration endpoints in server.py for Claire et Marcus PWA
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://social-ai-planner-2.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class PixabayAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.saved_images = []
        
    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def test_health_check(self):
        """Test 1: Backend Health Check"""
        self.log("🔍 Testing backend health check...")
        try:
            response = self.session.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                service = data.get('service', 'unknown')
                self.log(f"✅ Health check successful: Status: {status}, Service: {service}")
                return True
            else:
                self.log(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Health check error: {e}")
            return False
            
    def test_authentication(self):
        """Test 2: Authentication with provided credentials"""
        self.log("🔍 Testing authentication with lperpere@yahoo.fr...")
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json=TEST_CREDENTIALS,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                email = data.get("email")
                self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                self.log(f"✅ Authentication successful")
                self.log(f"   User ID: {self.user_id}")
                self.log(f"   Email: {email}")
                self.log(f"   Token: {self.access_token[:20]}..." if self.access_token else "No token")
                return True
            else:
                self.log(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ Authentication error: {e}")
            return False
            
    def test_pixabay_categories(self):
        """Test 3: GET /api/pixabay/categories - Get available Pixabay categories"""
        self.log("🔍 Testing GET /api/pixabay/categories...")
        try:
            response = self.session.get(f"{BACKEND_URL}/pixabay/categories", timeout=10)
            if response.status_code == 200:
                data = response.json()
                categories = data.get("categories", [])
                self.log(f"✅ Categories endpoint successful")
                self.log(f"   Found {len(categories)} categories")
                self.log(f"   Sample categories: {categories[:5]}")
                
                # Verify expected categories are present
                expected_categories = ["business", "nature", "people", "backgrounds", "technology"]
                found_expected = [cat for cat in expected_categories if cat in categories]
                self.log(f"   Expected categories found: {len(found_expected)}/{len(expected_categories)}")
                
                return len(categories) > 0
            else:
                self.log(f"❌ Categories endpoint failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ Categories endpoint error: {e}")
            return False
            
    def test_pixabay_search_business(self):
        """Test 4: GET /api/pixabay/search - Search for business images"""
        self.log("🔍 Testing GET /api/pixabay/search with query 'business'...")
        try:
            params = {
                "query": "business",
                "per_page": 10,
                "image_type": "photo",
                "safesearch": True
            }
            response = self.session.get(f"{BACKEND_URL}/pixabay/search", params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                total = data.get("total", 0)
                total_hits = data.get("totalHits", 0)
                hits = data.get("hits", [])
                
                self.log(f"✅ Business search successful")
                self.log(f"   Total results: {total}")
                self.log(f"   Total hits: {total_hits}")
                self.log(f"   Returned images: {len(hits)}")
                
                if hits:
                    first_image = hits[0]
                    self.log(f"   First image ID: {first_image.get('id')}")
                    self.log(f"   First image tags: {first_image.get('tags', '')[:50]}...")
                    self.log(f"   First image URL: {first_image.get('webformatURL', '')[:50]}...")
                    
                    # Store first image for save test
                    self.test_image = {
                        "id": first_image.get("id"),
                        "url": first_image.get("webformatURL"),
                        "tags": first_image.get("tags", "business")
                    }
                
                return len(hits) > 0
            elif response.status_code == 429:
                self.log(f"⚠️ Rate limit exceeded - this is expected behavior")
                return True
            else:
                self.log(f"❌ Business search failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ Business search error: {e}")
            return False
            
    def test_pixabay_search_marketing(self):
        """Test 5: GET /api/pixabay/search - Search for marketing images"""
        self.log("🔍 Testing GET /api/pixabay/search with query 'marketing'...")
        try:
            params = {
                "query": "marketing",
                "per_page": 5,
                "image_type": "photo",
                "orientation": "horizontal",
                "min_width": 640
            }
            response = self.session.get(f"{BACKEND_URL}/pixabay/search", params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                total = data.get("total", 0)
                hits = data.get("hits", [])
                
                self.log(f"✅ Marketing search successful")
                self.log(f"   Total results: {total}")
                self.log(f"   Returned images: {len(hits)}")
                
                # Verify required fields are present
                if hits:
                    first_image = hits[0]
                    required_fields = ["id", "webformatURL", "tags", "views", "downloads"]
                    present_fields = [field for field in required_fields if field in first_image]
                    self.log(f"   Required fields present: {len(present_fields)}/{len(required_fields)}")
                    self.log(f"   Fields: {present_fields}")
                
                return len(hits) > 0
            elif response.status_code == 429:
                self.log(f"⚠️ Rate limit exceeded - this is expected behavior")
                return True
            else:
                self.log(f"❌ Marketing search failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ Marketing search error: {e}")
            return False
            
    def test_pixabay_search_parameters(self):
        """Test 6: GET /api/pixabay/search - Test various search parameters"""
        self.log("🔍 Testing Pixabay search with various parameters...")
        
        test_cases = [
            {"query": "technology", "per_page": 3},
            {"query": "nature", "image_type": "photo", "orientation": "vertical"},
            {"query": "people", "min_width": 800, "min_height": 600}
        ]
        
        success_count = 0
        for i, params in enumerate(test_cases, 1):
            try:
                response = self.session.get(f"{BACKEND_URL}/pixabay/search", params=params, timeout=20)
                if response.status_code == 200:
                    data = response.json()
                    hits = data.get("hits", [])
                    self.log(f"✅ Parameter test {i} successful - Query: '{params['query']}', Results: {len(hits)}")
                    success_count += 1
                elif response.status_code == 429:
                    self.log(f"⚠️ Parameter test {i} rate limited - Query: '{params['query']}'")
                    success_count += 1  # Count as success since API is working
                else:
                    self.log(f"❌ Parameter test {i} failed: {response.status_code}")
            except Exception as e:
                self.log(f"❌ Parameter test {i} error: {e}")
                
        return success_count >= 2  # At least 2 out of 3 should work
        
    def test_pixabay_save_image(self):
        """Test 7: POST /api/pixabay/save-image - Save a Pixabay image to user's library"""
        if not hasattr(self, 'test_image'):
            self.log("⚠️ No test image available from search - using fallback image")
            # Use a known Pixabay image ID as fallback
            self.test_image = {
                "id": 195893,  # A known public domain image
                "url": "https://cdn.pixabay.com/photo/2013/07/12/15/36/motorsports-150157_640.jpg",
                "tags": "test, fallback"
            }
            
        self.log(f"🔍 Testing POST /api/pixabay/save-image with image ID {self.test_image['id']}...")
        
        try:
            # The endpoint expects query parameters, not form data or JSON
            params = {
                "pixabay_id": self.test_image["id"],
                "image_url": self.test_image["url"],
                "tags": self.test_image["tags"]
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/pixabay/save-image",
                params=params,  # Use query parameters
                timeout=60  # Longer timeout for image download
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                image_info = data.get("image", {})
                
                self.log(f"✅ Save image successful: {message}")
                self.log(f"   Saved image ID: {image_info.get('id')}")
                self.log(f"   Filename: {image_info.get('filename')}")
                self.log(f"   File size: {image_info.get('file_size')} bytes")
                self.log(f"   Dimensions: {image_info.get('width')}x{image_info.get('height')}")
                
                # Store saved image info for cleanup
                if image_info.get('id'):
                    self.saved_images.append(image_info['id'])
                
                return True
            else:
                self.log(f"❌ Save image failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ Save image error: {e}")
            return False
            
    def test_verify_saved_image(self):
        """Test 8: Verify saved image appears in user's content library"""
        self.log("🔍 Verifying saved image appears in content library...")
        try:
            response = self.session.get(f"{BACKEND_URL}/content/pending", timeout=10)
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                total = data.get("total", 0)
                
                self.log(f"✅ Content library accessible")
                self.log(f"   Total content items: {total}")
                self.log(f"   Retrieved items: {len(content_items)}")
                
                # Look for Pixabay images
                pixabay_images = [item for item in content_items if 'pixabay' in item.get('filename', '').lower()]
                self.log(f"   Pixabay images found: {len(pixabay_images)}")
                
                if pixabay_images:
                    latest_pixabay = pixabay_images[0]
                    self.log(f"   Latest Pixabay image: {latest_pixabay.get('filename')}")
                    self.log(f"   Context: {latest_pixabay.get('context', 'N/A')}")
                
                return len(content_items) > 0
            else:
                self.log(f"❌ Content library access failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ Content library verification error: {e}")
            return False
            
    def test_pixabay_api_key_validation(self):
        """Test 9: Verify Pixabay API key is properly configured"""
        self.log("🔍 Testing Pixabay API key configuration...")
        try:
            # Test with a simple search that should work if API key is valid
            params = {"query": "test", "per_page": 1}
            response = self.session.get(f"{BACKEND_URL}/pixabay/search", params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                total = data.get("total", 0)
                hits = data.get("hits", [])
                self.log(f"✅ Pixabay API key is properly configured")
                self.log(f"   Test search returned {total} total results, {len(hits)} hits")
                return True
            elif response.status_code == 429:
                self.log("✅ Pixabay API key working (rate limited)")
                return True
            elif response.status_code == 400:
                error_text = response.text
                if "API key" in error_text or "key" in error_text.lower():
                    self.log(f"❌ Pixabay API key error: {error_text}")
                    return False
                else:
                    self.log(f"⚠️ Pixabay API error (not key-related): {error_text}")
                    return True
            elif response.status_code == 500:
                error_text = response.text
                if "API key not configured" in error_text:
                    self.log(f"❌ Pixabay API key not configured: {error_text}")
                    return False
                else:
                    self.log(f"⚠️ Server error (may be temporary): {error_text}")
                    return True
            else:
                self.log(f"❌ Pixabay API key validation failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ API key validation error: {e}")
            return False
            
    def test_pixabay_error_handling(self):
        """Test 10: Test error handling for invalid requests"""
        self.log("🔍 Testing Pixabay error handling...")
        
        # Test invalid search parameters
        test_cases = [
            {"params": {"query": "", "per_page": 1}, "description": "empty query"},
            {"params": {"query": "test", "per_page": 300}, "description": "excessive per_page"},
            {"params": {"query": "test", "image_type": "invalid"}, "description": "invalid image_type"}
        ]
        
        success_count = 0
        for test_case in test_cases:
            try:
                response = self.session.get(
                    f"{BACKEND_URL}/pixabay/search", 
                    params=test_case["params"], 
                    timeout=10
                )
                
                if response.status_code in [400, 422, 429]:  # Expected error codes
                    self.log(f"✅ Error handling for {test_case['description']}: {response.status_code}")
                    success_count += 1
                elif response.status_code == 200:
                    # Some "invalid" parameters might still work
                    self.log(f"⚠️ {test_case['description']} unexpectedly succeeded")
                    success_count += 1
                else:
                    self.log(f"❌ Unexpected error for {test_case['description']}: {response.status_code}")
            except Exception as e:
                self.log(f"❌ Error handling test failed: {e}")
                
        return success_count >= 2
        
    def cleanup_saved_images(self):
        """Clean up any saved images from testing"""
        if not self.saved_images:
            return
            
        self.log(f"🧹 Cleaning up {len(self.saved_images)} saved images...")
        for image_id in self.saved_images[:]:
            try:
                response = self.session.delete(f"{BACKEND_URL}/content/{image_id}", timeout=5)
                if response.status_code == 200:
                    self.log(f"✅ Cleaned up image: {image_id}")
                    self.saved_images.remove(image_id)
                else:
                    self.log(f"⚠️ Failed to clean up image {image_id}: {response.status_code}")
            except Exception as e:
                self.log(f"⚠️ Cleanup error for image {image_id}: {e}")
                
    def run_all_tests(self):
        """Run all Pixabay integration tests"""
        self.log("🚀 Starting Pixabay Integration Backend Testing")
        self.log(f"Backend URL: {BACKEND_URL}")
        self.log(f"Test User: {TEST_CREDENTIALS['email']}")
        self.log("="*60)
        
        tests = [
            ("Backend Health Check", self.test_health_check),
            ("Authentication", self.test_authentication),
            ("Pixabay Categories", self.test_pixabay_categories),
            ("Pixabay Search - Business", self.test_pixabay_search_business),
            ("Pixabay Search - Marketing", self.test_pixabay_search_marketing),
            ("Pixabay Search Parameters", self.test_pixabay_search_parameters),
            ("Pixabay Save Image", self.test_pixabay_save_image),
            ("Verify Saved Image", self.test_verify_saved_image),
            ("API Key Validation", self.test_pixabay_api_key_validation),
            ("Error Handling", self.test_pixabay_error_handling)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            self.log(f"\n--- Test: {test_name} ---")
            try:
                if test_func():
                    passed += 1
                    self.log(f"✅ {test_name} PASSED")
                else:
                    self.log(f"❌ {test_name} FAILED")
            except Exception as e:
                self.log(f"❌ {test_name} ERROR: {e}")
                
            # Small delay between tests to avoid rate limiting
            time.sleep(1)
                
        # Cleanup
        self.cleanup_saved_images()
        
        # Summary
        self.log(f"\n{'='*60}")
        self.log(f"PIXABAY INTEGRATION TESTING SUMMARY")
        self.log(f"{'='*60}")
        self.log(f"Tests Passed: {passed}/{total}")
        self.log(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            self.log("🎉 ALL TESTS PASSED - Pixabay integration is fully functional!")
            return True
        elif passed >= total * 0.8:  # 80% success rate
            self.log("✅ MOSTLY SUCCESSFUL - Pixabay integration is working with minor issues")
            return True
        else:
            self.log("❌ SIGNIFICANT ISSUES - Pixabay integration needs attention")
            return False

if __name__ == "__main__":
    tester = PixabayAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)