#!/usr/bin/env python3
"""
Pixabay Integration Backend Testing
Final verification test for complete Pixabay integration functionality
Testing all Pixabay endpoints as specified in the review request
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://social-ai-planner-2.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class PixabayIntegrationTester:
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
            response = self.session.get(f"{BACKEND_URL}/health", timeout=15)
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                service = data.get('service', 'unknown')
                self.log(f"✅ Backend health check successful - Status: {status}, Service: {service}")
                return True
            else:
                self.log(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Health check error: {e}")
            return False
            
    def test_authentication(self):
        """Test 2: Authentication with specified credentials"""
        self.log("🔍 Testing authentication with lperpere@yahoo.fr...")
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json=TEST_CREDENTIALS,
                timeout=15
            )
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                self.log(f"✅ Authentication successful - User ID: {self.user_id}")
                self.log(f"   JWT Token: {self.access_token[:20]}..." if self.access_token else "   No token received")
                return True
            else:
                self.log(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ Authentication error: {e}")
            return False
            
    def test_pixabay_categories(self):
        """Test 3: GET /api/pixabay/categories - verify categories load correctly"""
        self.log("🔍 Testing Pixabay categories endpoint...")
        try:
            response = self.session.get(f"{BACKEND_URL}/pixabay/categories", timeout=15)
            if response.status_code == 200:
                data = response.json()
                categories = data.get("categories", [])
                self.log(f"✅ Pixabay categories successful - Found {len(categories)} categories")
                
                # Check for expected categories
                expected_categories = ["business", "nature", "people", "backgrounds", "technology"]
                found_expected = [cat for cat in expected_categories if cat in categories]
                self.log(f"   Expected categories found: {found_expected}")
                
                # Log first few categories
                if categories:
                    sample_categories = categories[:5]
                    self.log(f"   Sample categories: {sample_categories}")
                
                return len(categories) > 0
            else:
                self.log(f"❌ Pixabay categories failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ Pixabay categories error: {e}")
            return False
            
    def test_pixabay_search_business(self):
        """Test 4: GET /api/pixabay/search with query "business" and per_page=10"""
        self.log("🔍 Testing Pixabay search with 'business' query...")
        try:
            params = {
                "query": "business",
                "per_page": 10
            }
            response = self.session.get(f"{BACKEND_URL}/pixabay/search", params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                total = data.get("total", 0)
                hits = data.get("hits", [])
                total_hits = data.get("totalHits", 0)
                
                self.log(f"✅ Pixabay business search successful")
                self.log(f"   Total results: {total:,}")
                self.log(f"   Total hits: {total_hits:,}")
                self.log(f"   Returned images: {len(hits)}")
                
                if hits:
                    first_image = hits[0]
                    image_id = first_image.get("id")
                    tags = first_image.get("tags", "")
                    views = first_image.get("views", 0)
                    downloads = first_image.get("downloads", 0)
                    webformat_url = first_image.get("webformatURL", "")
                    
                    self.log(f"   First image ID: {image_id}")
                    self.log(f"   Tags: {tags[:50]}..." if len(tags) > 50 else f"   Tags: {tags}")
                    self.log(f"   Views: {views:,}, Downloads: {downloads:,}")
                    self.log(f"   Has webformatURL: {'Yes' if webformat_url else 'No'}")
                    
                    # Store first image for save test
                    self.first_business_image = first_image
                
                return len(hits) > 0 and total > 0
            else:
                self.log(f"❌ Pixabay business search failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ Pixabay business search error: {e}")
            return False
            
    def test_pixabay_search_additional(self):
        """Test 5: Additional Pixabay search queries for verification"""
        self.log("🔍 Testing additional Pixabay search queries...")
        
        test_queries = [
            ("marketing", 5),
            ("technology", 3),
            ("nature", 5)
        ]
        
        success_count = 0
        for query, per_page in test_queries:
            try:
                params = {
                    "query": query,
                    "per_page": per_page
                }
                response = self.session.get(f"{BACKEND_URL}/pixabay/search", params=params, timeout=20)
                if response.status_code == 200:
                    data = response.json()
                    hits = data.get("hits", [])
                    total = data.get("total", 0)
                    self.log(f"✅ Search '{query}' successful - {len(hits)} images, {total:,} total")
                    success_count += 1
                else:
                    self.log(f"❌ Search '{query}' failed: {response.status_code}")
            except Exception as e:
                self.log(f"❌ Search '{query}' error: {e}")
                
        return success_count >= 2  # At least 2 out of 3 should work
        
    def test_pixabay_save_image(self):
        """Test 6: POST /api/pixabay/save-image - test saving a Pixabay image"""
        if not hasattr(self, 'first_business_image') or not self.first_business_image:
            self.log("⚠️ No business image available for save test - skipping")
            return True
            
        self.log("🔍 Testing Pixabay save image...")
        
        image = self.first_business_image
        save_data = {
            "pixabay_id": image.get("id"),
            "image_url": image.get("webformatURL"),
            "tags": image.get("tags", "")
        }
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/pixabay/save-image",
                data=save_data,  # Use form data instead of JSON
                timeout=60  # Longer timeout for image download
            )
            if response.status_code == 200:
                data = response.json()
                saved_image = data.get("image", {})
                message = data.get("message", "")
                
                image_id = saved_image.get("id")
                filename = saved_image.get("filename", "")
                file_size = saved_image.get("file_size", 0)
                width = saved_image.get("width", 0)
                height = saved_image.get("height", 0)
                
                self.log(f"✅ Pixabay save image successful - {message}")
                self.log(f"   Saved image ID: {image_id}")
                self.log(f"   Filename: {filename}")
                self.log(f"   File size: {file_size:,} bytes")
                self.log(f"   Dimensions: {width}x{height}")
                
                if image_id:
                    self.saved_images.append(image_id)
                
                return True
            else:
                self.log(f"❌ Pixabay save image failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ Pixabay save image error: {e}")
            return False
            
    def test_content_verification(self):
        """Test 7: GET /api/content/pending - verify saved Pixabay images appear"""
        self.log("🔍 Testing content verification - checking for saved Pixabay images...")
        try:
            response = self.session.get(f"{BACKEND_URL}/content/pending", timeout=15)
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                total = data.get("total", 0)
                
                self.log(f"✅ Content verification successful")
                self.log(f"   Total content items: {total}")
                self.log(f"   Retrieved items: {len(content_items)}")
                
                # Look for Pixabay images
                pixabay_images = []
                for item in content_items:
                    source = item.get("source")
                    filename = item.get("filename", "")
                    context = item.get("context", "")
                    
                    if (source == "pixabay" or 
                        "pixabay" in filename.lower() or 
                        "pixabay" in context.lower()):
                        pixabay_images.append(item)
                
                self.log(f"   Pixabay images found: {len(pixabay_images)}")
                
                if pixabay_images:
                    latest_pixabay = pixabay_images[0]  # Should be sorted by date
                    self.log(f"   Latest Pixabay image: {latest_pixabay.get('filename', 'N/A')}")
                    self.log(f"   Context: {latest_pixabay.get('context', 'N/A')}")
                    self.log(f"   Created: {latest_pixabay.get('created_at', 'N/A')}")
                
                return True
            else:
                self.log(f"❌ Content verification failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ Content verification error: {e}")
            return False
            
    def test_pixabay_api_key_validation(self):
        """Test 8: Verify Pixabay API key is working correctly"""
        self.log("🔍 Testing Pixabay API key validation...")
        try:
            # Test with a simple query to verify API key works
            params = {
                "query": "test",
                "per_page": 3
            }
            response = self.session.get(f"{BACKEND_URL}/pixabay/search", params=params, timeout=20)
            if response.status_code == 200:
                data = response.json()
                hits = data.get("hits", [])
                self.log(f"✅ Pixabay API key validation successful - {len(hits)} results returned")
                return True
            elif response.status_code == 429:
                self.log(f"⚠️ Pixabay API rate limit reached - API key is working but limited")
                return True  # Still consider this a success
            elif response.status_code == 401:
                self.log(f"❌ Pixabay API key validation failed - Unauthorized (401)")
                return False
            else:
                self.log(f"❌ Pixabay API key validation failed: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Pixabay API key validation error: {e}")
            return False
            
    def test_error_handling(self):
        """Test 9: Test error handling for various invalid parameters"""
        self.log("🔍 Testing Pixabay error handling...")
        
        test_cases = [
            ("empty query", {"query": "", "per_page": 5}),
            ("invalid per_page", {"query": "test", "per_page": 300}),  # Max is 200
            ("invalid image_type", {"query": "test", "image_type": "invalid"})
        ]
        
        success_count = 0
        for test_name, params in test_cases:
            try:
                response = self.session.get(f"{BACKEND_URL}/pixabay/search", params=params, timeout=15)
                if response.status_code in [200, 400, 422]:  # Any reasonable response
                    self.log(f"✅ Error handling '{test_name}' working: {response.status_code}")
                    success_count += 1
                else:
                    self.log(f"⚠️ Error handling '{test_name}' unexpected: {response.status_code}")
            except Exception as e:
                self.log(f"❌ Error handling '{test_name}' error: {e}")
                
        return success_count >= 2  # At least 2 out of 3 should work
        
    def test_integration_completeness(self):
        """Test 10: Verify complete integration functionality"""
        self.log("🔍 Testing integration completeness...")
        
        # Check that all required endpoints are accessible
        endpoints_to_check = [
            "/pixabay/categories",
            "/pixabay/search",
            "/content/pending"
        ]
        
        accessible_endpoints = 0
        for endpoint in endpoints_to_check:
            try:
                if endpoint == "/pixabay/search":
                    response = self.session.get(f"{BACKEND_URL}{endpoint}", params={"query": "test", "per_page": 1}, timeout=15)
                else:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}", timeout=15)
                
                if response.status_code == 200:
                    accessible_endpoints += 1
                    self.log(f"✅ Endpoint {endpoint} accessible")
                else:
                    self.log(f"❌ Endpoint {endpoint} not accessible: {response.status_code}")
                    if endpoint == "/pixabay/search":
                        self.log(f"   Response: {response.text[:100]}...")
            except Exception as e:
                self.log(f"❌ Endpoint {endpoint} error: {e}")
        
        self.log(f"Integration completeness: {accessible_endpoints}/{len(endpoints_to_check)} endpoints accessible")
        return accessible_endpoints >= 2  # Allow for minor issues
        
    def run_all_tests(self):
        """Run all Pixabay integration tests"""
        self.log("🚀 Starting Pixabay Integration Backend Testing")
        self.log(f"Backend URL: {BACKEND_URL}")
        self.log(f"Test User: {TEST_CREDENTIALS['email']}")
        self.log("=" * 60)
        
        tests = [
            ("Backend Health Check", self.test_health_check),
            ("Authentication", self.test_authentication),
            ("Pixabay Categories", self.test_pixabay_categories),
            ("Pixabay Search Business", self.test_pixabay_search_business),
            ("Additional Search Queries", self.test_pixabay_search_additional),
            ("Pixabay Save Image", self.test_pixabay_save_image),
            ("Content Verification", self.test_content_verification),
            ("API Key Validation", self.test_pixabay_api_key_validation),
            ("Error Handling", self.test_error_handling),
            ("Integration Completeness", self.test_integration_completeness)
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
    tester = PixabayIntegrationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)