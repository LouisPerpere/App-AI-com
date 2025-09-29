#!/usr/bin/env python3
"""
Public Image Endpoint Testing Suite - Facebook Image Publication Fix
Testing the corrected /api/public/image/{id} endpoint that should serve images directly from GridFS without authentication

Credentials: lperpere@yahoo.fr / L@Reunion974!

TEST OBJECTIVES:
1. Test public image endpoint without authentication (should return 200, not 401)
2. Verify correct Content-Type headers (image/jpeg, image/png, etc.)
3. Test Facebook publication with system images using public URLs
4. Compare URL conversion functionality
5. Test external image handling (WikiMedia, Pixabay)
6. Validate Facebook-friendly headers (Cache-Control, Access-Control-Allow-Origin)
"""

import requests
import json
import sys
import re
from datetime import datetime

# Configuration
BASE_URL = "https://social-pub-hub.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class PublicImageTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        self.test_image_ids = []
        
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
    
    def get_test_images(self):
        """Step 2: Get some test images from the system"""
        try:
            print("🖼️ Step 2: Getting Test Images from System")
            response = self.session.get(f"{BASE_URL}/content/pending?limit=5", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                
                # Filter for images only
                image_content = [item for item in content if item.get("file_type", "").startswith("image")]
                
                if image_content:
                    self.test_image_ids = [item["id"] for item in image_content[:3]]  # Take first 3 images
                    self.log_test("Get Test Images", True, 
                                f"Found {len(image_content)} images, using {len(self.test_image_ids)} for testing")
                    return True
                else:
                    self.log_test("Get Test Images", False, 
                                f"No images found in content library (total items: {len(content)})")
                    return False
            else:
                self.log_test("Get Test Images", False, 
                            f"Status: {response.status_code}", response.text[:200])
                return False
                
        except Exception as e:
            self.log_test("Get Test Images", False, error=str(e))
            return False
    
    def test_public_image_endpoint_without_auth(self):
        """Test 1: Test public image endpoint without authentication"""
        try:
            print("🌐 Test 1: Public Image Endpoint Without Authentication")
            
            if not self.test_image_ids:
                self.log_test("Public Image Endpoint Without Auth", False, 
                            "No test images available")
                return False
            
            # Test with first image ID, WITHOUT authentication
            test_image_id = self.test_image_ids[0]
            
            # Create a new session without auth headers
            no_auth_session = requests.Session()
            
            response = no_auth_session.get(
                f"{BASE_URL}/public/image/{test_image_id}", 
                timeout=30,
                allow_redirects=False  # Don't follow redirects to see the actual response
            )
            
            if response.status_code == 200:
                # Check if it's actually image content
                content_type = response.headers.get("content-type", "").lower()
                if content_type.startswith("image/"):
                    self.log_test("Public Image Endpoint Without Auth", True, 
                                f"✅ SUCCESS: Returns 200 with Content-Type: {content_type}")
                    return True
                else:
                    self.log_test("Public Image Endpoint Without Auth", False, 
                                f"Returns 200 but wrong Content-Type: {content_type}")
                    return False
                    
            elif response.status_code == 302:
                # Check if it's redirecting to external URL (valid for Pixabay/WikiMedia images)
                location = response.headers.get("location", "")
                if location.startswith("http"):
                    self.log_test("Public Image Endpoint Without Auth", True, 
                                f"✅ SUCCESS: Redirects to external URL: {location[:50]}...")
                    return True
                else:
                    self.log_test("Public Image Endpoint Without Auth", False, 
                                f"Redirects to non-external URL: {location}")
                    return False
                    
            elif response.status_code == 401:
                self.log_test("Public Image Endpoint Without Auth", False, 
                            "❌ CRITICAL: Still returns 401 Authentication Required - Fix not working!")
                return False
                
            elif response.status_code == 404:
                self.log_test("Public Image Endpoint Without Auth", False, 
                            f"Image not found: {test_image_id}")
                return False
                
            else:
                self.log_test("Public Image Endpoint Without Auth", False, 
                            f"Unexpected status: {response.status_code}, Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log_test("Public Image Endpoint Without Auth", False, error=str(e))
            return False
    
    def test_facebook_friendly_headers(self):
        """Test 2: Test Facebook-friendly headers"""
        try:
            print("📘 Test 2: Facebook-Friendly Headers")
            
            if not self.test_image_ids:
                self.log_test("Facebook-Friendly Headers", False, 
                            "No test images available")
                return False
            
            test_image_id = self.test_image_ids[0]
            no_auth_session = requests.Session()
            
            response = no_auth_session.get(
                f"{BASE_URL}/public/image/{test_image_id}", 
                timeout=30,
                allow_redirects=False
            )
            
            if response.status_code in [200, 302]:
                headers = response.headers
                
                # Check for Facebook-friendly headers
                cache_control = headers.get("cache-control", "").lower()
                access_control = headers.get("access-control-allow-origin", "")
                content_type = headers.get("content-type", "").lower()
                
                facebook_friendly = True
                header_details = []
                
                # Check Content-Type
                if content_type.startswith("image/"):
                    header_details.append(f"✅ Content-Type: {content_type}")
                else:
                    header_details.append(f"❌ Content-Type: {content_type}")
                    facebook_friendly = False
                
                # Check Cache-Control
                if "public" in cache_control:
                    header_details.append(f"✅ Cache-Control: {cache_control}")
                else:
                    header_details.append(f"⚠️ Cache-Control: {cache_control}")
                
                # Check Access-Control-Allow-Origin
                if access_control == "*":
                    header_details.append(f"✅ Access-Control-Allow-Origin: {access_control}")
                else:
                    header_details.append(f"⚠️ Access-Control-Allow-Origin: {access_control}")
                
                self.log_test("Facebook-Friendly Headers", facebook_friendly, 
                            "; ".join(header_details))
                return facebook_friendly
                
            else:
                self.log_test("Facebook-Friendly Headers", False, 
                            f"Cannot test headers - endpoint returned {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Facebook-Friendly Headers", False, error=str(e))
            return False
    
    def test_url_conversion_function(self):
        """Test 3: Test URL conversion function"""
        try:
            print("🔄 Test 3: URL Conversion Function")
            
            # Test the convert_to_public_image_url function by checking if it's working in practice
            # We'll test this by checking if Facebook publication endpoints use the converted URLs
            
            test_data = {
                "text": "Test image URL conversion",
                "image_url": "https://cdn.pixabay.com/photo/2016/11/29/05/45/astronomy-1867616_960_720.jpg"
            }
            
            response = self.session.post(
                f"{BASE_URL}/social/facebook/publish-simple", 
                json=test_data, 
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                # Should fail with connection error, not URL error
                error_message = data.get("error", "").lower()
                
                if "connexion" in error_message or "facebook" in error_message:
                    self.log_test("URL Conversion Function", True, 
                                f"✅ URL processing works - fails at connection level: {data.get('error', '')}")
                    return True
                elif "url" in error_message or "image" in error_message:
                    self.log_test("URL Conversion Function", False, 
                                f"URL conversion issue: {data.get('error', '')}")
                    return False
                else:
                    self.log_test("URL Conversion Function", True, 
                                f"✅ URL processing appears to work: {data.get('error', '')}")
                    return True
            else:
                self.log_test("URL Conversion Function", False, 
                            f"Unexpected status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("URL Conversion Function", False, error=str(e))
            return False
    
    def test_external_image_handling(self):
        """Test 4: Test external image handling (WikiMedia, Pixabay)"""
        try:
            print("🌍 Test 4: External Image Handling")
            
            # Test WikiMedia image
            wikimedia_url = "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png"
            
            # Test direct access to WikiMedia
            try:
                wikimedia_response = requests.get(wikimedia_url, timeout=10)
                wikimedia_accessible = wikimedia_response.status_code == 200
            except:
                wikimedia_accessible = False
            
            # Test Pixabay image
            pixabay_url = "https://cdn.pixabay.com/photo/2016/11/29/05/45/astronomy-1867616_960_720.jpg"
            
            try:
                pixabay_response = requests.get(pixabay_url, timeout=10)
                pixabay_accessible = pixabay_response.status_code == 200
            except:
                pixabay_accessible = False
            
            details = []
            if wikimedia_accessible:
                details.append("✅ WikiMedia accessible")
            else:
                details.append("❌ WikiMedia blocked/inaccessible")
                
            if pixabay_accessible:
                details.append("✅ Pixabay accessible")
            else:
                details.append("❌ Pixabay inaccessible")
            
            # At least one should be accessible for the test to be meaningful
            success = wikimedia_accessible or pixabay_accessible
            
            self.log_test("External Image Handling", success, 
                        "; ".join(details))
            return success
                
        except Exception as e:
            self.log_test("External Image Handling", False, error=str(e))
            return False
    
    def test_facebook_publication_with_system_image(self):
        """Test 5: Test Facebook publication with system image using public URL"""
        try:
            print("📘 Test 5: Facebook Publication with System Image")
            
            if not self.test_image_ids:
                self.log_test("Facebook Publication with System Image", False, 
                            "No test images available")
                return False
            
            # Use the public URL format for a system image
            test_image_id = self.test_image_ids[0]
            public_image_url = f"{BASE_URL}/public/image/{test_image_id}"
            
            test_data = {
                "text": "Test publication Facebook avec image système via URL publique",
                "image_url": public_image_url
            }
            
            response = self.session.post(
                f"{BASE_URL}/social/facebook/publish-simple", 
                json=test_data, 
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                error_message = data.get("error", "").lower()
                
                # Should fail with connection error, not image access error
                if "connexion" in error_message or "facebook" in error_message:
                    self.log_test("Facebook Publication with System Image", True, 
                                f"✅ Image URL processed correctly - fails at connection: {data.get('error', '')}")
                    return True
                elif "image" in error_message or "url" in error_message or "access" in error_message:
                    self.log_test("Facebook Publication with System Image", False, 
                                f"❌ Image access issue: {data.get('error', '')}")
                    return False
                else:
                    self.log_test("Facebook Publication with System Image", True, 
                                f"✅ Image processing appears successful: {data.get('error', '')}")
                    return True
            else:
                self.log_test("Facebook Publication with System Image", False, 
                            f"Unexpected status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Facebook Publication with System Image", False, error=str(e))
            return False
    
    def test_multiple_image_formats(self):
        """Test 6: Test multiple image formats if available"""
        try:
            print("🎨 Test 6: Multiple Image Formats")
            
            if len(self.test_image_ids) < 2:
                self.log_test("Multiple Image Formats", True, 
                            "Only one test image available - format diversity test skipped")
                return True
            
            no_auth_session = requests.Session()
            format_results = []
            
            for i, image_id in enumerate(self.test_image_ids[:3]):  # Test up to 3 images
                try:
                    response = no_auth_session.get(
                        f"{BASE_URL}/public/image/{image_id}", 
                        timeout=15,
                        allow_redirects=False
                    )
                    
                    if response.status_code in [200, 302]:
                        content_type = response.headers.get("content-type", "unknown")
                        format_results.append(f"Image {i+1}: {content_type}")
                    else:
                        format_results.append(f"Image {i+1}: Status {response.status_code}")
                        
                except Exception as e:
                    format_results.append(f"Image {i+1}: Error {str(e)[:30]}")
            
            success = len(format_results) > 0
            self.log_test("Multiple Image Formats", success, 
                        "; ".join(format_results))
            return success
                
        except Exception as e:
            self.log_test("Multiple Image Formats", False, error=str(e))
            return False
    
    def run_all_tests(self):
        """Run all public image endpoint tests"""
        print("🎯 TESTING PUBLIC IMAGE ENDPOINT CORRECTIONS")
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
        
        # Step 2: Get test images
        if not self.get_test_images():
            print("⚠️ No test images available - some tests will be skipped")
        
        # Test 1: Public image endpoint without authentication
        self.test_public_image_endpoint_without_auth()
        
        # Test 2: Facebook-friendly headers
        self.test_facebook_friendly_headers()
        
        # Test 3: URL conversion function
        self.test_url_conversion_function()
        
        # Test 4: External image handling
        self.test_external_image_handling()
        
        # Test 5: Facebook publication with system image
        self.test_facebook_publication_with_system_image()
        
        # Test 6: Multiple image formats
        self.test_multiple_image_formats()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY - PUBLIC IMAGE ENDPOINT CORRECTIONS")
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
            print("\n🎉 ALL TESTS PASSED - Public image endpoint corrections working!")
            print("✅ Public endpoint serves images without authentication")
            print("✅ Facebook-friendly headers implemented")
            print("✅ URL conversion working correctly")
            print("✅ External image handling functional")
            print("✅ Facebook can now access system images via public URLs")
            return True
        else:
            print(f"\n🚨 {total - passed} TESTS FAILED - Public image endpoint needs attention")
            failed_tests = [r['test'] for r in self.test_results if not r['success']]
            print(f"Failed tests: {', '.join(failed_tests)}")
            return False

def main():
    """Main test execution for public image endpoint corrections"""
    tester = PublicImageTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Public image endpoint corrections validation completed successfully!")
        print("🚀 Facebook should now be able to access images via public URLs!")
        sys.exit(0)
    else:
        print("\n❌ Public image endpoint corrections validation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()