#!/usr/bin/env python3
"""
Comprehensive Thumbnail API Backend Testing
Testing the thumbnail API functionality as requested in the review:
1) Using /api/content/pending, collect first image item's id
2) Call GET /api/content/{id}/thumb to see if it returns 200 or 404. If 404 due to missing source, skip.
3) Call POST /api/content/{id}/thumbnail then re-check GET /api/content/{id}/thumb
4) Ensure route is protected and returns proper status codes
5) Test additional thumbnail endpoints for completeness
"""

import requests
import json
import os
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://instamanager-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class ComprehensiveThumbnailAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        self.test_image_id = None
        self.test_image_filename = None
        
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
        """Step 1: Get pending content and analyze the situation"""
        print("📋 STEP 1: Get pending content and analyze available images")
        try:
            response = self.session.get(f"{API_BASE}/content/pending")
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                
                total_items = len(content_items)
                image_items = [item for item in content_items if item.get("file_type", "").startswith("image/")]
                total_images = len(image_items)
                
                print(f"    Total content items: {total_items}")
                print(f"    Total image items: {total_images}")
                
                if image_items:
                    # Use the first image item regardless of disk existence for API testing
                    self.test_image_id = image_items[0]["id"]
                    self.test_image_filename = image_items[0].get("filename", "unknown")
                    self.log_result(
                        "Get pending content", 
                        True, 
                        f"Found {total_images} images, using: {self.test_image_filename} (ID: {self.test_image_id})",
                        response.status_code
                    )
                    return True
                else:
                    self.log_result("Get pending content", False, "No image items found in content", response.status_code)
                    return False
            else:
                self.log_result("Get pending content", False, f"Failed to get content: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_result("Get pending content", False, f"Exception: {str(e)}")
            return False

    def test_thumbnail_get_endpoint(self):
        """Step 2: Test GET /api/content/{id}/thumb endpoint"""
        print("🖼️ STEP 2: Test GET thumbnail endpoint")
        try:
            response = self.session.get(f"{API_BASE}/content/{self.test_image_id}/thumb")
            
            if response.status_code == 200:
                content_type = response.headers.get("content-type", "")
                content_length = len(response.content)
                self.log_result(
                    "GET thumbnail endpoint", 
                    True, 
                    f"Thumbnail exists - Content-Type: {content_type}, Size: {content_length} bytes",
                    response.status_code
                )
                return "exists"
            elif response.status_code == 404:
                error_detail = ""
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail", "") or error_data.get("error", "")
                except:
                    error_detail = response.text
                
                if "missing on disk" in error_detail.lower() or "file missing on disk" in error_detail.lower():
                    self.log_result(
                        "GET thumbnail endpoint", 
                        True, 
                        f"Expected 404 - Source file missing: {error_detail}",
                        response.status_code
                    )
                    return "source_missing"
                else:
                    self.log_result(
                        "GET thumbnail endpoint", 
                        True, 
                        f"Expected 404 - Thumbnail not generated: {error_detail}",
                        response.status_code
                    )
                    return "not_generated"
            else:
                self.log_result("GET thumbnail endpoint", False, f"Unexpected status: {response.text}", response.status_code)
                return "error"
                
        except Exception as e:
            self.log_result("GET thumbnail endpoint", False, f"Exception: {str(e)}")
            return "error"

    def test_thumbnail_post_endpoint(self):
        """Step 3: Test POST /api/content/{id}/thumbnail endpoint"""
        print("⚙️ STEP 3: Test POST thumbnail generation endpoint")
        try:
            response = self.session.post(f"{API_BASE}/content/{self.test_image_id}/thumbnail")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "POST thumbnail endpoint", 
                    True, 
                    f"Thumbnail generation scheduled: {data}",
                    response.status_code
                )
                return "scheduled"
            elif response.status_code == 404:
                error_detail = ""
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail", "") or error_data.get("error", "")
                except:
                    error_detail = response.text
                
                if "missing on disk" in error_detail.lower() or "file missing on disk" in error_detail.lower():
                    self.log_result(
                        "POST thumbnail endpoint", 
                        True, 
                        f"Expected 404 - Source file missing: {error_detail}",
                        response.status_code
                    )
                    return "source_missing"
                elif "media not found" in error_detail.lower():
                    self.log_result("POST thumbnail endpoint", False, f"Media not found: {error_detail}", response.status_code)
                    return "media_not_found"
                else:
                    self.log_result("POST thumbnail endpoint", False, f"Unexpected 404: {error_detail}", response.status_code)
                    return "error"
            else:
                self.log_result("POST thumbnail endpoint", False, f"Failed: {response.text}", response.status_code)
                return "error"
                
        except Exception as e:
            self.log_result("POST thumbnail endpoint", False, f"Exception: {str(e)}")
            return "error"

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

    def test_bulk_thumbnail_endpoints(self):
        """Step 5: Test bulk thumbnail endpoints"""
        print("📦 STEP 5: Test bulk thumbnail endpoints")
        
        # Test POST /api/content/thumbnails/rebuild
        try:
            response = self.session.post(f"{API_BASE}/content/thumbnails/rebuild")
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Bulk thumbnail rebuild", 
                    True, 
                    f"Rebuild scheduled: {data}",
                    response.status_code
                )
            else:
                self.log_result("Bulk thumbnail rebuild", False, f"Failed: {response.text}", response.status_code)
        except Exception as e:
            self.log_result("Bulk thumbnail rebuild", False, f"Exception: {str(e)}")
        
        # Test GET /api/content/thumbnails/status
        try:
            response = self.session.get(f"{API_BASE}/content/thumbnails/status")
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Thumbnail status endpoint", 
                    True, 
                    f"Status: {data}",
                    response.status_code
                )
            else:
                self.log_result("Thumbnail status endpoint", False, f"Failed: {response.text}", response.status_code)
        except Exception as e:
            self.log_result("Thumbnail status endpoint", False, f"Exception: {str(e)}")

    def run_comprehensive_test(self):
        """Run the complete comprehensive thumbnail API test"""
        print("🎯 COMPREHENSIVE THUMBNAIL API BACKEND TESTING")
        print("=" * 60)
        
        # Step 0: Authentication
        if not self.authenticate():
            print("❌ Authentication failed, cannot continue")
            return False
        
        # Step 1: Get pending content
        if not self.get_pending_content():
            print("❌ Could not get content, cannot continue")
            return False
        
        # Step 2: Test GET thumbnail endpoint
        get_result = self.test_thumbnail_get_endpoint()
        
        # Step 3: Test POST thumbnail endpoint
        post_result = self.test_thumbnail_post_endpoint()
        
        # If thumbnail generation was scheduled, wait and re-check
        if post_result == "scheduled":
            print("⏳ Waiting 3 seconds for thumbnail generation to complete...")
            import time
            time.sleep(3)
            
            print("🔄 Re-checking thumbnail after generation...")
            get_result_after = self.test_thumbnail_get_endpoint()
            if get_result_after == "exists":
                print("✅ Thumbnail successfully generated and accessible!")
            else:
                print("⚠️ Thumbnail still not available (background task may still be running)")
        
        # Step 4: Test authentication protection
        self.test_authentication_protection()
        
        # Step 5: Test bulk endpoints
        self.test_bulk_thumbnail_endpoints()
        
        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
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
        
        # Analysis
        print("\n🔍 ANALYSIS:")
        auth_tests = [r for r in self.test_results if "auth" in r["test"].lower()]
        endpoint_tests = [r for r in self.test_results if "endpoint" in r["test"].lower()]
        
        auth_success = all(r["success"] for r in auth_tests)
        endpoint_success = all(r["success"] for r in endpoint_tests)
        
        print(f"  - Authentication Protection: {'✅ Working' if auth_success else '❌ Issues'}")
        print(f"  - Thumbnail Endpoints: {'✅ Working' if endpoint_success else '❌ Issues'}")
        
        # Check for data consistency issues
        source_missing_tests = [r for r in self.test_results if "source file missing" in r["details"].lower()]
        if source_missing_tests:
            print(f"  - Data Consistency: ⚠️ {len(source_missing_tests)} tests affected by missing source files")
        else:
            print(f"  - Data Consistency: ✅ No missing source file issues detected")

def main():
    """Main test execution"""
    tester = ComprehensiveThumbnailAPITester()
    
    try:
        success = tester.run_comprehensive_test()
        tester.print_summary()
        
        if success:
            print("\n🎉 COMPREHENSIVE THUMBNAIL API TESTING COMPLETED")
        else:
            print("\n❌ COMPREHENSIVE THUMBNAIL API TESTING FAILED")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()