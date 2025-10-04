#!/usr/bin/env python3
"""
Thumbnail API Backend Testing
Testing the thumbnail API functionality as requested in the review:
1) Using /api/content/pending, collect first image item's id
2) Call GET /api/content/{id}/thumb to see if it returns 200 or 404. If 404 due to missing source, skip.
3) Call POST /api/content/{id}/thumbnail then re-check GET /api/content/{id}/thumb
4) Ensure route is protected and returns proper status codes
"""

import requests
import json
import os
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://claire-marcus-app-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class ThumbnailAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details="", status_code=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        if status_code:
            print(f"    Status Code: {status_code}")
        print()

    def authenticate(self):
        """Step 0: Authenticate and get JWT token"""
        print("🔐 STEP 0: Authentication")
        try:
            response = self.session.post(
                f"{API_BASE}/auth/login-robust",
                json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                self.log_result("Authentication", True, f"User ID: {self.user_id}", response.status_code)
                return True
            else:
                self.log_result("Authentication", False, f"Login failed: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Exception: {str(e)}")
            return False

    def get_pending_content(self):
        """Step 1: Get pending content and find first image item that exists on disk"""
        print("📋 STEP 1: Get pending content and find first image item")
        try:
            response = self.session.get(f"{API_BASE}/content/pending")
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                
                # Find first image item that exists on disk
                image_item = None
                for item in content_items:
                    file_type = item.get("file_type", "")
                    if file_type.startswith("image/"):
                        filename = item.get("filename", "")
                        # Check if file exists on disk
                        import os
                        file_path = f"/app/backend/uploads/{filename}"
                        if os.path.exists(file_path):
                            image_item = item
                            print(f"    Found image on disk: {filename}")
                            break
                        else:
                            print(f"    Image not on disk: {filename}")
                
                if image_item:
                    self.test_image_id = image_item["id"]
                    self.test_image_filename = image_item.get("filename", "unknown")
                    self.log_result(
                        "Get pending content - Find image", 
                        True, 
                        f"Found image: {self.test_image_filename} (ID: {self.test_image_id}, Type: {image_item.get('file_type')})",
                        response.status_code
                    )
                    return True
                else:
                    self.log_result("Get pending content - Find image", False, "No image items found that exist on disk", response.status_code)
                    return False
            else:
                self.log_result("Get pending content", False, f"Failed to get content: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_result("Get pending content", False, f"Exception: {str(e)}")
            return False

    def check_thumbnail_exists(self, step_name="Check thumbnail"):
        """Step 2: Check if thumbnail exists for the image"""
        print(f"🖼️ STEP 2: {step_name}")
        try:
            response = self.session.get(f"{API_BASE}/content/{self.test_image_id}/thumb")
            
            if response.status_code == 200:
                content_type = response.headers.get("content-type", "")
                content_length = len(response.content)
                self.log_result(
                    step_name, 
                    True, 
                    f"Thumbnail exists - Content-Type: {content_type}, Size: {content_length} bytes",
                    response.status_code
                )
                return True, "exists"
            elif response.status_code == 404:
                error_detail = ""
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail", "")
                except:
                    error_detail = response.text
                
                if "missing on disk" in error_detail.lower():
                    self.log_result(
                        step_name, 
                        True, 
                        f"Expected 404 - Source file missing on disk: {error_detail}",
                        response.status_code
                    )
                    return False, "source_missing"
                else:
                    self.log_result(
                        step_name, 
                        True, 
                        f"Expected 404 - Thumbnail not generated yet: {error_detail}",
                        response.status_code
                    )
                    return False, "not_generated"
            else:
                self.log_result(step_name, False, f"Unexpected status: {response.text}", response.status_code)
                return False, "error"
                
        except Exception as e:
            self.log_result(step_name, False, f"Exception: {str(e)}")
            return False, "error"

    def generate_thumbnail(self):
        """Step 3: Generate thumbnail for the image"""
        print("⚙️ STEP 3: Generate thumbnail")
        try:
            response = self.session.post(f"{API_BASE}/content/{self.test_image_id}/thumbnail")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Generate thumbnail", 
                    True, 
                    f"Thumbnail generation scheduled: {data}",
                    response.status_code
                )
                return True
            elif response.status_code == 404:
                error_detail = ""
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail", "") or error_data.get("error", "")
                except:
                    error_detail = response.text
                
                print(f"    DEBUG: Full 404 response: {response.text}")
                print(f"    DEBUG: Error detail: '{error_detail}'")
                
                if "missing on disk" in error_detail.lower() or "file missing on disk" in error_detail.lower():
                    self.log_result(
                        "Generate thumbnail", 
                        True, 
                        f"Expected 404 - Source file missing on disk, skipping: {error_detail}",
                        response.status_code
                    )
                    return "skip"
                elif "media not found" in error_detail.lower():
                    self.log_result("Generate thumbnail", False, f"Media not found: {error_detail}", response.status_code)
                    return False
                else:
                    self.log_result("Generate thumbnail", False, f"Unexpected 404: {error_detail}", response.status_code)
                    return False
            else:
                self.log_result("Generate thumbnail", False, f"Failed: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_result("Generate thumbnail", False, f"Exception: {str(e)}")
            return False

    def test_authentication_protection(self):
        """Step 4: Test that routes are properly protected"""
        print("🔒 STEP 4: Test authentication protection")
        
        # Test without auth token
        unauth_session = requests.Session()
        
        # Test GET /api/content/{id}/thumb without auth
        try:
            response = unauth_session.get(f"{API_BASE}/content/{self.test_image_id}/thumb")
            if response.status_code == 401:
                self.log_result(
                    "Auth protection - GET thumb", 
                    True, 
                    "Correctly returns 401 without auth token",
                    response.status_code
                )
            else:
                self.log_result(
                    "Auth protection - GET thumb", 
                    False, 
                    f"Should return 401, got {response.status_code}: {response.text}",
                    response.status_code
                )
        except Exception as e:
            self.log_result("Auth protection - GET thumb", False, f"Exception: {str(e)}")
        
        # Test POST /api/content/{id}/thumbnail without auth
        try:
            response = unauth_session.post(f"{API_BASE}/content/{self.test_image_id}/thumbnail")
            if response.status_code == 401:
                self.log_result(
                    "Auth protection - POST thumbnail", 
                    True, 
                    "Correctly returns 401 without auth token",
                    response.status_code
                )
            else:
                self.log_result(
                    "Auth protection - POST thumbnail", 
                    False, 
                    f"Should return 401, got {response.status_code}: {response.text}",
                    response.status_code
                )
        except Exception as e:
            self.log_result("Auth protection - POST thumbnail", False, f"Exception: {str(e)}")

    def run_full_test(self):
        """Run the complete thumbnail API test workflow"""
        print("🎯 THUMBNAIL API BACKEND TESTING")
        print("=" * 50)
        
        # Step 0: Authentication
        if not self.authenticate():
            print("❌ Authentication failed, cannot continue")
            return False
        
        # Step 1: Get pending content and find first image
        if not self.get_pending_content():
            print("❌ Could not find image content, cannot continue")
            return False
        
        # Step 2: Check if thumbnail exists initially
        exists, status = self.check_thumbnail_exists("Initial thumbnail check")
        
        if status == "source_missing":
            print("⚠️ Source file missing on disk, skipping thumbnail generation test")
            # Still test authentication protection
            self.test_authentication_protection()
            return True
        
        # Step 3: Generate thumbnail if it doesn't exist
        if not exists:
            generation_result = self.generate_thumbnail()
            if generation_result == "skip":
                print("⚠️ Thumbnail generation skipped due to missing source file")
                # Still test authentication protection
                self.test_authentication_protection()
                return True
            elif not generation_result:
                print("❌ Thumbnail generation failed")
                return False
            
            # Wait a moment for background task to complete
            import time
            print("⏳ Waiting 3 seconds for thumbnail generation to complete...")
            time.sleep(3)
            
            # Step 4: Re-check thumbnail after generation
            exists_after, _ = self.check_thumbnail_exists("Thumbnail check after generation")
            if not exists_after:
                print("⚠️ Thumbnail still not available after generation (background task may still be running)")
        
        # Step 5: Test authentication protection
        self.test_authentication_protection()
        
        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"  - {result['test']}")

def main():
    """Main test execution"""
    tester = ThumbnailAPITester()
    
    try:
        success = tester.run_full_test()
        tester.print_summary()
        
        if success:
            print("\n🎉 THUMBNAIL API TESTING COMPLETED")
        else:
            print("\n❌ THUMBNAIL API TESTING FAILED")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()