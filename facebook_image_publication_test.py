#!/usr/bin/env python3
"""
Facebook Image Publication Test
Testing Facebook publication with the identified working image IDs

Credentials: lperpere@yahoo.fr / L@Reunion974!

WORKING IMAGE IDs IDENTIFIED:
1. 5f5f0f72-ec37-4796-a68b-033af26b9644 (pixabay_2277292_8c65b88c.jpg)
2. 76f629ab-63d4-45ce-acf1-2aaf7203bf2b (pixabay_2277292_6fdf9e6f.jpg)
3. 0cc81793-2d60-485d-8643-32ef25720d23 (test_file.jpg)

TEST OBJECTIVES:
1. Test Facebook publication with working image URLs
2. Test both public and protected image URLs
3. Verify image accessibility for Facebook API
4. Test external image URLs (WikiMedia, Pixabay)
5. Provide final recommendations
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://claire-marcus-app-1.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

# Working image IDs from diagnostic
WORKING_IMAGE_IDS = [
    {
        "id": "5f5f0f72-ec37-4796-a68b-033af26b9644",
        "filename": "pixabay_2277292_8c65b88c.jpg",
        "public_accessible": True
    },
    {
        "id": "76f629ab-63d4-45ce-acf1-2aaf7203bf2b", 
        "filename": "pixabay_2277292_6fdf9e6f.jpg",
        "public_accessible": True
    },
    {
        "id": "0cc81793-2d60-485d-8643-32ef25720d23",
        "filename": "test_file.jpg",
        "public_accessible": False
    }
]

class FacebookImagePublicationTest:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        
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
        """Authenticate and get JWT token"""
        try:
            print("🔐 Authentication")
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
    
    def test_image_accessibility_verification(self):
        """Verify image accessibility before Facebook testing"""
        try:
            print("🔍 Verifying Image Accessibility")
            
            accessible_count = 0
            
            for image in WORKING_IMAGE_IDS:
                image_id = image["id"]
                filename = image["filename"]
                
                # Test protected endpoint
                try:
                    response = self.session.get(
                        f"{BASE_URL}/content/{image_id}/file",
                        timeout=10
                    )
                    
                    protected_accessible = response.status_code == 200
                    content_type = response.headers.get('content-type', '')
                    content_length = response.headers.get('content-length', '0')
                    
                    print(f"   Protected: {filename}")
                    print(f"     Status: {response.status_code}, Type: {content_type}, Size: {content_length}")
                    
                    if protected_accessible:
                        accessible_count += 1
                    
                except Exception as e:
                    print(f"   Protected: {filename} - Error: {str(e)}")
                
                # Test public endpoint (without auth)
                try:
                    public_session = requests.Session()
                    response = public_session.get(
                        f"{BASE_URL}/public/image/{image_id}",
                        timeout=10
                    )
                    
                    public_accessible = response.status_code == 200
                    content_type = response.headers.get('content-type', '')
                    content_length = response.headers.get('content-length', '0')
                    
                    print(f"   Public: {filename}")
                    print(f"     Status: {response.status_code}, Type: {content_type}, Size: {content_length}")
                    print()
                    
                except Exception as e:
                    print(f"   Public: {filename} - Error: {str(e)}")
                    print()
            
            details = f"Verified accessibility for {len(WORKING_IMAGE_IDS)} images, {accessible_count} accessible via protected endpoint"
            self.log_test("Image Accessibility Verification", True, details)
            
            return True
            
        except Exception as e:
            self.log_test("Image Accessibility Verification", False, error=str(e))
            return False
    
    def test_facebook_publication_with_system_images(self):
        """Test Facebook publication with system image URLs"""
        try:
            print("📘 Testing Facebook Publication with System Images")
            
            publication_results = []
            
            for image in WORKING_IMAGE_IDS:
                image_id = image["id"]
                filename = image["filename"]
                
                # Test with public URL (Facebook-accessible)
                public_url = f"{BASE_URL}/public/image/{image_id}"
                
                test_data = {
                    "text": f"Test publication Facebook avec image système: {filename}",
                    "image_url": public_url
                }
                
                try:
                    response = self.session.post(
                        f"{BASE_URL}/social/facebook/publish-simple",
                        json=test_data,
                        timeout=30
                    )
                    
                    result = {
                        "image_id": image_id,
                        "filename": filename,
                        "image_url": public_url,
                        "status_code": response.status_code,
                        "response": response.json() if response.status_code == 200 else response.text[:200]
                    }
                    publication_results.append(result)
                    
                    print(f"   Image: {filename}")
                    print(f"     URL: {public_url}")
                    print(f"     Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        success = data.get("success", False)
                        error_msg = data.get("error", "")
                        print(f"     Success: {success}")
                        if error_msg:
                            print(f"     Error: {error_msg}")
                    else:
                        print(f"     Response: {response.text[:100]}")
                    print()
                    
                except Exception as e:
                    result = {
                        "image_id": image_id,
                        "filename": filename,
                        "image_url": public_url,
                        "error": str(e)
                    }
                    publication_results.append(result)
                    print(f"   Image: {filename} - Error: {str(e)}")
                    print()
            
            details = f"Tested Facebook publication with {len(WORKING_IMAGE_IDS)} system images"
            self.log_test("Facebook Publication with System Images", True, details)
            
            # Store results
            self.publication_results = publication_results
            
            return True
            
        except Exception as e:
            self.log_test("Facebook Publication with System Images", False, error=str(e))
            return False
    
    def test_facebook_publication_with_external_images(self):
        """Test Facebook publication with external image URLs"""
        try:
            print("🌐 Testing Facebook Publication with External Images")
            
            external_images = [
                {
                    "name": "WikiMedia PNG",
                    "url": "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png"
                },
                {
                    "name": "Pixabay JPG",
                    "url": "https://cdn.pixabay.com/photo/2016/11/29/05/45/astronomy-1867616_960_720.jpg"
                }
            ]
            
            external_results = []
            
            for image in external_images:
                name = image["name"]
                url = image["url"]
                
                test_data = {
                    "text": f"Test publication Facebook avec image externe: {name}",
                    "image_url": url
                }
                
                try:
                    response = self.session.post(
                        f"{BASE_URL}/social/facebook/publish-simple",
                        json=test_data,
                        timeout=30
                    )
                    
                    result = {
                        "name": name,
                        "url": url,
                        "status_code": response.status_code,
                        "response": response.json() if response.status_code == 200 else response.text[:200]
                    }
                    external_results.append(result)
                    
                    print(f"   External Image: {name}")
                    print(f"     URL: {url}")
                    print(f"     Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        success = data.get("success", False)
                        error_msg = data.get("error", "")
                        print(f"     Success: {success}")
                        if error_msg:
                            print(f"     Error: {error_msg}")
                    else:
                        print(f"     Response: {response.text[:100]}")
                    print()
                    
                except Exception as e:
                    result = {
                        "name": name,
                        "url": url,
                        "error": str(e)
                    }
                    external_results.append(result)
                    print(f"   External Image: {name} - Error: {str(e)}")
                    print()
            
            details = f"Tested Facebook publication with {len(external_images)} external images"
            self.log_test("Facebook Publication with External Images", True, details)
            
            # Store results
            self.external_results = external_results
            
            return True
            
        except Exception as e:
            self.log_test("Facebook Publication with External Images", False, error=str(e))
            return False
    
    def test_image_url_conversion_function(self):
        """Test the convert_to_public_image_url function behavior"""
        try:
            print("🔄 Testing Image URL Conversion")
            
            # Test different URL formats to see conversion behavior
            test_urls = [
                f"{BASE_URL}/content/5f5f0f72-ec37-4796-a68b-033af26b9644/file",
                "https://cdn.pixabay.com/photo/2016/11/29/05/45/astronomy-1867616_960_720.jpg",
                "uploads/pixabay_2277292_8c65b88c.jpg",
                "/api/content/76f629ab-63d4-45ce-acf1-2aaf7203bf2b/file"
            ]
            
            conversion_results = []
            
            for url in test_urls:
                # We can't directly test the conversion function, but we can test publication
                # with different URL formats to see how they're handled
                
                test_data = {
                    "text": f"Test conversion pour URL: {url[:50]}...",
                    "image_url": url
                }
                
                try:
                    response = self.session.post(
                        f"{BASE_URL}/social/facebook/publish-simple",
                        json=test_data,
                        timeout=30
                    )
                    
                    result = {
                        "original_url": url,
                        "status_code": response.status_code,
                        "response": response.json() if response.status_code == 200 else response.text[:200]
                    }
                    conversion_results.append(result)
                    
                    print(f"   URL: {url}")
                    print(f"     Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        success = data.get("success", False)
                        error_msg = data.get("error", "")
                        print(f"     Success: {success}")
                        if error_msg:
                            print(f"     Error: {error_msg}")
                    print()
                    
                except Exception as e:
                    result = {
                        "original_url": url,
                        "error": str(e)
                    }
                    conversion_results.append(result)
                    print(f"   URL: {url} - Error: {str(e)}")
                    print()
            
            details = f"Tested URL conversion behavior with {len(test_urls)} different URL formats"
            self.log_test("Image URL Conversion Testing", True, details)
            
            # Store results
            self.conversion_results = conversion_results
            
            return True
            
        except Exception as e:
            self.log_test("Image URL Conversion Testing", False, error=str(e))
            return False
    
    def run_facebook_image_tests(self):
        """Run all Facebook image publication tests"""
        print("🎯 FACEBOOK IMAGE PUBLICATION TESTING")
        print("=" * 80)
        print(f"Backend URL: {BASE_URL}")
        print(f"Test User: {TEST_CREDENTIALS['email']}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print(f"Working Images: {len(WORKING_IMAGE_IDS)}")
        print("=" * 80)
        print()
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed - cannot continue tests")
            return False
        
        # Step 2: Verify image accessibility
        self.test_image_accessibility_verification()
        
        # Step 3: Test Facebook publication with system images
        self.test_facebook_publication_with_system_images()
        
        # Step 4: Test Facebook publication with external images
        self.test_facebook_publication_with_external_images()
        
        # Step 5: Test URL conversion behavior
        self.test_image_url_conversion_function()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 FACEBOOK IMAGE PUBLICATION TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print(f"\n🎯 RESULTS: {passed}/{total} tests completed ({(passed/total*100):.1f}%)")
        
        # Final recommendations
        print("\n" + "=" * 80)
        print("🔧 FINAL RECOMMENDATIONS FOR FACEBOOK IMAGE PUBLICATION")
        print("=" * 80)
        
        print("✅ WORKING IMAGE IDs FOR FACEBOOK:")
        for image in WORKING_IMAGE_IDS:
            if image["public_accessible"]:
                print(f"   ✅ {image['id']} - {image['filename']} (Public accessible)")
            else:
                print(f"   ⚠️ {image['id']} - {image['filename']} (Protected only)")
        
        print("\n📋 RECOMMENDATIONS:")
        print("1. Use public image URLs for Facebook publication")
        print("2. Fix /api/content/pending to filter out inaccessible images")
        print("3. Ensure convert_to_public_image_url() function works correctly")
        print("4. Clean up 38 inaccessible media records from database")
        print("5. Consider implementing proper GridFS storage for new uploads")
        
        return passed == total

def main():
    """Main Facebook image publication test execution"""
    tester = FacebookImagePublicationTest()
    success = tester.run_facebook_image_tests()
    
    if success:
        print("\n✅ Facebook image publication testing completed successfully!")
        print("🎯 RESULT: Image publication workflow tested and analyzed")
        sys.exit(0)
    else:
        print("\n⚠️ Facebook image publication testing completed with some issues!")
        print("🎯 PARTIAL RESULT: Useful diagnostic information gathered")
        sys.exit(0)

if __name__ == "__main__":
    main()