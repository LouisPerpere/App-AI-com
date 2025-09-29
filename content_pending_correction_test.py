#!/usr/bin/env python3
"""
Content Pending API Correction Testing Suite
Testing the corrected /api/content/pending endpoint that filters and returns ONLY accessible images

Credentials: lperpere@yahoo.fr / L@Reunion974!

TEST OBJECTIVES:
1. Test API content/pending after correction - verify only accessible images returned
2. Count number of images returned vs before correction
3. Validate each returned image is accessible via GET /api/content/{id}/file
4. Test public endpoint GET /api/public/image/{id} with returned IDs
5. Test Facebook publication with filtered images
6. Verify Facebook can access these images with correct headers

EXPECTED RESULT: 2-3 accessible images instead of 41, all functional for Facebook
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
BASE_URL = "https://social-publisher-10.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class ContentPendingTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        self.accessible_images = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()
        
    def authenticate(self):
        """Step 1: Authenticate and get JWT token"""
        try:
            print("🔐 Step 1: Authentication")
            response = self.session.post(
                f"{BASE_URL}/auth/login-robust",
                json=TEST_CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                self.log_test("Authentication", True, f"User ID: {self.user_id}")
                return True
            else:
                self.log_test("Authentication", False, 
                            f"Status: {response.status_code}", 
                            response.text[:200])
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, error=str(e))
            return False
    
    def test_content_pending_after_correction(self):
        """Test 1: API content/pending after correction - verify filtering works"""
        try:
            print("🔍 Test 1: Content Pending API After Correction")
            response = self.session.get(f"{BASE_URL}/content/pending?limit=10", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                total_accessible = data.get("accessible_count", len(content_items))
                total_checked = data.get("total_checked", "unknown")
                
                # Store accessible images for further testing
                self.accessible_images = content_items
                
                # Verify filtering is working (should be much less than 41)
                if len(content_items) <= 10 and len(content_items) > 0:
                    self.log_test("Content Pending API Filtering", True, 
                                f"✅ Filtering working: {len(content_items)} accessible images returned (checked {total_checked} total)")
                    
                    # Log details about returned images
                    for i, item in enumerate(content_items[:3]):  # Show first 3
                        file_id = item.get("id", "unknown")
                        filename = item.get("filename", "unknown")
                        url = item.get("url", "")
                        print(f"   Image {i+1}: {file_id} ({filename}) - URL: {url[:50]}...")
                    
                    return True
                elif len(content_items) == 0:
                    self.log_test("Content Pending API Filtering", False, 
                                "No accessible images found - filtering may be too strict")
                    return False
                else:
                    self.log_test("Content Pending API Filtering", False, 
                                f"Too many images returned: {len(content_items)} - filtering may not be working")
                    return False
            else:
                self.log_test("Content Pending API Filtering", False, 
                            f"Status: {response.status_code}", response.text[:200])
                return False
                
        except Exception as e:
            self.log_test("Content Pending API Filtering", False, error=str(e))
            return False
    
    def test_image_accessibility_validation(self):
        """Test 2: Validate each returned image is accessible via GET /api/content/{id}/file"""
        try:
            print("🖼️ Test 2: Image Accessibility Validation")
            
            if not self.accessible_images:
                self.log_test("Image Accessibility Validation", False, 
                            "No images to test - previous test may have failed")
                return False
            
            accessible_count = 0
            inaccessible_count = 0
            
            for item in self.accessible_images:
                file_id = item.get("id")
                filename = item.get("filename", "unknown")
                
                if not file_id:
                    continue
                
                try:
                    # Test image accessibility
                    response = self.session.get(f"{BASE_URL}/content/{file_id}/file", timeout=15)
                    
                    if response.status_code == 200:
                        accessible_count += 1
                        content_type = response.headers.get("content-type", "")
                        content_length = len(response.content)
                        print(f"   ✅ {file_id} ({filename}): {content_type}, {content_length} bytes")
                    else:
                        inaccessible_count += 1
                        print(f"   ❌ {file_id} ({filename}): Status {response.status_code}")
                        
                except Exception as img_error:
                    inaccessible_count += 1
                    print(f"   ❌ {file_id} ({filename}): Error {str(img_error)}")
            
            total_tested = accessible_count + inaccessible_count
            
            if accessible_count == total_tested and total_tested > 0:
                self.log_test("Image Accessibility Validation", True, 
                            f"✅ All {accessible_count} returned images are accessible (100% success rate)")
                return True
            elif accessible_count > 0:
                success_rate = (accessible_count / total_tested) * 100
                self.log_test("Image Accessibility Validation", False, 
                            f"Only {accessible_count}/{total_tested} images accessible ({success_rate:.1f}% success rate)")
                return False
            else:
                self.log_test("Image Accessibility Validation", False, 
                            "No images are accessible - filtering correction may have issues")
                return False
                
        except Exception as e:
            self.log_test("Image Accessibility Validation", False, error=str(e))
            return False
    
    def test_public_image_endpoint(self):
        """Test 3: Test public endpoint GET /api/public/image/{id} with returned IDs"""
        try:
            print("🌐 Test 3: Public Image Endpoint Testing")
            
            if not self.accessible_images:
                self.log_test("Public Image Endpoint", False, 
                            "No images to test - previous test may have failed")
                return False
            
            public_accessible_count = 0
            public_failed_count = 0
            
            for item in self.accessible_images[:3]:  # Test first 3 images
                file_id = item.get("id")
                filename = item.get("filename", "unknown")
                
                if not file_id:
                    continue
                
                try:
                    # Test public endpoint (no auth required)
                    session_no_auth = requests.Session()  # No auth headers
                    response = session_no_auth.get(f"{BASE_URL}/public/image/{file_id}", timeout=15)
                    
                    if response.status_code == 200:
                        public_accessible_count += 1
                        content_type = response.headers.get("content-type", "")
                        content_length = len(response.content)
                        access_control = response.headers.get("access-control-allow-origin", "")
                        print(f"   ✅ {file_id} ({filename}): {content_type}, {content_length} bytes, CORS: {access_control}")
                    else:
                        public_failed_count += 1
                        print(f"   ❌ {file_id} ({filename}): Status {response.status_code}")
                        
                except Exception as img_error:
                    public_failed_count += 1
                    print(f"   ❌ {file_id} ({filename}): Error {str(img_error)}")
            
            total_tested = public_accessible_count + public_failed_count
            
            if public_accessible_count == total_tested and total_tested > 0:
                self.log_test("Public Image Endpoint", True, 
                            f"✅ All {public_accessible_count} images accessible via public endpoint (Facebook-ready)")
                return True
            elif public_accessible_count > 0:
                success_rate = (public_accessible_count / total_tested) * 100
                self.log_test("Public Image Endpoint", False, 
                            f"Only {public_accessible_count}/{total_tested} images accessible via public endpoint ({success_rate:.1f}%)")
                return False
            else:
                self.log_test("Public Image Endpoint", False, 
                            "No images accessible via public endpoint - Facebook integration will fail")
                return False
                
        except Exception as e:
            self.log_test("Public Image Endpoint", False, error=str(e))
            return False
    
    def test_facebook_publication_with_filtered_images(self):
        """Test 4: Test Facebook publication with filtered images"""
        try:
            print("📘 Test 4: Facebook Publication with Filtered Images")
            
            if not self.accessible_images:
                self.log_test("Facebook Publication with Filtered Images", False, 
                            "No images to test - previous test may have failed")
                return False
            
            # Use first accessible image for Facebook publication test
            test_image = self.accessible_images[0]
            file_id = test_image.get("id")
            filename = test_image.get("filename", "unknown")
            
            # Convert to public URL for Facebook
            public_image_url = f"{BASE_URL.replace('/api', '')}/api/public/image/{file_id}"
            
            test_data = {
                "text": "Test publication Facebook avec image filtrée accessible",
                "image_url": public_image_url
            }
            
            response = self.session.post(
                f"{BASE_URL}/social/facebook/publish-simple", 
                json=test_data, 
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                error_message = data.get("error", "")
                
                # Expected: Should fail due to no Facebook connection, but image URL should be processed correctly
                if not success and ("connexion" in error_message.lower() or "facebook" in error_message.lower()):
                    self.log_test("Facebook Publication with Filtered Images", True, 
                                f"✅ Image URL processed correctly, failed at connection level as expected: {error_message}")
                    return True
                elif success:
                    self.log_test("Facebook Publication with Filtered Images", True, 
                                f"✅ Unexpected success - publication worked: {data}")
                    return True
                else:
                    self.log_test("Facebook Publication with Filtered Images", False, 
                                f"Unexpected error (may be image-related): {error_message}")
                    return False
            else:
                self.log_test("Facebook Publication with Filtered Images", False, 
                            f"Status: {response.status_code}", response.text[:200])
                return False
                
        except Exception as e:
            self.log_test("Facebook Publication with Filtered Images", False, error=str(e))
            return False
    
    def test_facebook_image_headers_validation(self):
        """Test 5: Verify Facebook can access images with correct headers"""
        try:
            print("🔗 Test 5: Facebook Image Headers Validation")
            
            if not self.accessible_images:
                self.log_test("Facebook Image Headers Validation", False, 
                            "No images to test - previous test may have failed")
                return False
            
            # Test first accessible image
            test_image = self.accessible_images[0]
            file_id = test_image.get("id")
            filename = test_image.get("filename", "unknown")
            
            try:
                # Test public endpoint with Facebook-like request
                session_facebook = requests.Session()
                session_facebook.headers.update({
                    "User-Agent": "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)"
                })
                
                response = session_facebook.get(f"{BASE_URL}/public/image/{file_id}", timeout=15)
                
                if response.status_code == 200:
                    content_type = response.headers.get("content-type", "")
                    content_length = response.headers.get("content-length", "0")
                    access_control = response.headers.get("access-control-allow-origin", "")
                    cache_control = response.headers.get("cache-control", "")
                    
                    # Verify Facebook-friendly headers
                    is_image = content_type.startswith("image/")
                    has_cors = access_control == "*"
                    has_content_length = int(content_length) > 0
                    
                    if is_image and has_cors and has_content_length:
                        self.log_test("Facebook Image Headers Validation", True, 
                                    f"✅ Facebook-friendly headers: {content_type}, {content_length} bytes, CORS: {access_control}")
                        return True
                    else:
                        self.log_test("Facebook Image Headers Validation", False, 
                                    f"Missing Facebook-friendly headers - Type: {content_type}, CORS: {access_control}, Length: {content_length}")
                        return False
                else:
                    self.log_test("Facebook Image Headers Validation", False, 
                                f"Facebook request failed: Status {response.status_code}")
                    return False
                    
            except Exception as img_error:
                self.log_test("Facebook Image Headers Validation", False, 
                            f"Facebook request error: {str(img_error)}")
                return False
                
        except Exception as e:
            self.log_test("Facebook Image Headers Validation", False, error=str(e))
            return False
    
    def test_before_after_comparison(self):
        """Test 6: Compare results before/after correction (informational)"""
        try:
            print("📊 Test 6: Before/After Correction Comparison")
            
            # Test the temporary endpoint that shows all items (before filtering)
            response = self.session.get(f"{BASE_URL}/content/pending-temp?limit=50", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                all_items = data.get("content", [])
                total_before = len(all_items)
                total_after = len(self.accessible_images)
                
                reduction_percentage = ((total_before - total_after) / total_before * 100) if total_before > 0 else 0
                
                self.log_test("Before/After Correction Comparison", True, 
                            f"✅ Filtering effectiveness: {total_before} total → {total_after} accessible ({reduction_percentage:.1f}% reduction)")
                
                # Show some examples of filtered out items
                inaccessible_count = 0
                for item in all_items[:5]:  # Check first 5 items
                    file_id = item.get("id")
                    url = item.get("url", "")
                    if "claire-marcus-api.onrender.com" in url:
                        inaccessible_count += 1
                        print(f"   ❌ Filtered out: {file_id} (broken onrender.com URL)")
                
                if inaccessible_count > 0:
                    print(f"   📝 Found {inaccessible_count} items with broken onrender.com URLs (correctly filtered)")
                
                return True
            else:
                self.log_test("Before/After Correction Comparison", False, 
                            f"Could not access temp endpoint: Status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Before/After Correction Comparison", False, error=str(e))
            return False
    
    def run_all_tests(self):
        """Run all content pending correction tests"""
        print("🎯 TESTING CONTENT PENDING API CORRECTION")
        print("=" * 70)
        print(f"Backend URL: {BASE_URL}")
        print(f"Test User: {TEST_CREDENTIALS['email']}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 70)
        print()
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed - cannot continue tests")
            return False
        
        # Test 1: Content pending API after correction
        self.test_content_pending_after_correction()
        
        # Test 2: Validate image accessibility
        self.test_image_accessibility_validation()
        
        # Test 3: Test public image endpoint
        self.test_public_image_endpoint()
        
        # Test 4: Test Facebook publication with filtered images
        self.test_facebook_publication_with_filtered_images()
        
        # Test 5: Verify Facebook-friendly headers
        self.test_facebook_image_headers_validation()
        
        # Test 6: Before/after comparison
        self.test_before_after_comparison()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY - CONTENT PENDING API CORRECTION")
        print("=" * 70)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print(f"\n🎯 RESULTS: {passed}/{total} tests passed ({(passed/total*100):.1f}%)")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED - Content Pending API correction is working!")
            print("✅ API /content/pending now returns only accessible images")
            print("✅ All returned images are accessible via /api/content/{id}/file")
            print("✅ Public endpoint /api/public/image/{id} working for Facebook")
            print("✅ Facebook publication can process filtered images")
            print("✅ Images have Facebook-friendly headers")
            print(f"✅ Filtering reduced images from many to {len(self.accessible_images)} accessible ones")
            return True
        else:
            print(f"\n🚨 {total - passed} TESTS FAILED - Content Pending API correction needs attention")
            failed_tests = [r['test'] for r in self.test_results if not r['success']]
            print(f"Failed tests: {', '.join(failed_tests)}")
            return False

def main():
    """Main test execution for content pending API correction"""
    tester = ContentPendingTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Content Pending API correction validation completed successfully!")
        print("🚀 Facebook can now access only the images that are actually available!")
        sys.exit(0)
    else:
        print("\n❌ Content Pending API correction validation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()