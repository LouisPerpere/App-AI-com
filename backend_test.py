#!/usr/bin/env python3
"""
Backend Test Suite for Thumbnail Generation System
Testing the recently fixed MongoDB comparison bug and thumbnail generation functionality
"""

import requests
import json
import os
import time
import base64
from io import BytesIO
from PIL import Image

# Configuration
BACKEND_URL = "https://libfusion.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials as specified in review request
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class ThumbnailSystemTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()
    
    def authenticate(self):
        """Step 1: Authenticate with specified credentials"""
        print("🔐 STEP 1: Authentication")
        print("=" * 50)
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                self.log_result(
                    "Authentication", 
                    True, 
                    f"Successfully authenticated as {TEST_EMAIL}, User ID: {self.user_id}"
                )
                return True
            else:
                self.log_result(
                    "Authentication", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, error=str(e))
            return False
    
    def create_test_image(self):
        """Create a test image for upload"""
        # Create a simple test image
        img = Image.new('RGB', (800, 600), color='blue')
        
        # Add some text to make it identifiable
        try:
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            draw.text((50, 50), "Test Image for Thumbnails", fill='white')
        except:
            pass  # Font not available, continue without text
        
        # Convert to bytes
        img_buffer = BytesIO()
        img.save(img_buffer, format='JPEG', quality=90)
        img_buffer.seek(0)
        
        return img_buffer.getvalue()
    
    def test_batch_upload(self):
        """Step 2: Test POST /api/content/batch-upload with image file"""
        print("📤 STEP 2: Batch Upload Test")
        print("=" * 50)
        
        try:
            # Create test image
            test_image_data = self.create_test_image()
            
            # Prepare multipart form data
            files = {
                'files': ('test_thumbnail_image.jpg', test_image_data, 'image/jpeg')
            }
            
            response = self.session.post(f"{API_BASE}/content/batch-upload", files=files)
            
            if response.status_code == 200:
                data = response.json()
                uploaded_files = data.get("uploaded_files", [])
                
                if uploaded_files:
                    self.uploaded_file_id = uploaded_files[0].get("id")
                    self.uploaded_filename = uploaded_files[0].get("stored_name")
                    
                    self.log_result(
                        "Batch Upload", 
                        True, 
                        f"Successfully uploaded {len(uploaded_files)} file(s). File ID: {self.uploaded_file_id}, Filename: {self.uploaded_filename}"
                    )
                    
                    # Wait a moment for background thumbnail generation
                    print("⏳ Waiting 3 seconds for background thumbnail generation...")
                    time.sleep(3)
                    
                    return True
                else:
                    self.log_result(
                        "Batch Upload", 
                        False, 
                        "No files were uploaded",
                        data.get("message", "Unknown error")
                    )
                    return False
            else:
                self.log_result(
                    "Batch Upload", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Batch Upload", False, error=str(e))
            return False
    
    def test_thumbnail_status(self):
        """Step 3: Test GET /api/content/thumbnails/status"""
        print("📊 STEP 3: Thumbnail Status Test")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{API_BASE}/content/thumbnails/status")
            
            if response.status_code == 200:
                data = response.json()
                total_files = data.get("total_files", 0)
                with_thumbnails = data.get("with_thumbnails", 0)
                missing_thumbnails = data.get("missing_thumbnails", 0)
                completion_percentage = data.get("completion_percentage", 0)
                
                self.log_result(
                    "Thumbnail Status", 
                    True, 
                    f"Total files: {total_files}, With thumbnails: {with_thumbnails}, Missing: {missing_thumbnails}, Completion: {completion_percentage}%"
                )
                return True
            else:
                self.log_result(
                    "Thumbnail Status", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Thumbnail Status", False, error=str(e))
            return False
    
    def analyze_thumb_urls_french_review(self):
        """ÉTAPE FRANÇAISE: Analyser les thumb_url - Combien ont thumb_url = null, libfusion vs claire-marcus"""
        print("🇫🇷 ÉTAPE FRANÇAISE: Analyse thumb_url selon demande")
        print("=" * 50)
        
        try:
            # Get all content files
            response = self.session.get(f"{API_BASE}/content/pending?limit=100")
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                total_files = len(content)
                
                # Analyze thumb_url patterns as requested in French review
                null_thumb_urls = 0
                libfusion_urls = 0
                claire_marcus_urls = 0
                other_urls = 0
                
                libfusion_examples = []
                claire_marcus_examples = []
                
                for item in content:
                    thumb_url = item.get("thumb_url")
                    filename = item.get("filename", "unknown")
                    
                    if thumb_url is None or thumb_url == "":
                        null_thumb_urls += 1
                    elif "libfusion.preview.emergentagent.com" in thumb_url:
                        libfusion_urls += 1
                        if len(libfusion_examples) < 2:
                            libfusion_examples.append(f"{filename}: {thumb_url}")
                    elif "claire-marcus.com" in thumb_url:
                        claire_marcus_urls += 1
                        if len(claire_marcus_examples) < 2:
                            claire_marcus_examples.append(f"{filename}: {thumb_url}")
                    else:
                        other_urls += 1
                
                # Report according to French review requirements
                details = f"ANALYSE DES {total_files} FICHIERS: "
                details += f"thumb_url = null: {null_thumb_urls}, "
                details += f"utilisant libfusion.preview.emergentagent.com: {libfusion_urls}, "
                details += f"utilisant correctement claire-marcus.com: {claire_marcus_urls}, "
                details += f"autres: {other_urls}. "
                
                if libfusion_examples:
                    details += f"Exemples libfusion: {libfusion_examples}. "
                if claire_marcus_examples:
                    details += f"Exemples claire-marcus: {claire_marcus_examples}. "
                
                self.log_result(
                    "Analyse thumb_url (demande française)", 
                    True, 
                    details
                )
                
                # Store for final verification
                self.french_analysis = {
                    "total_files": total_files,
                    "null_thumb_urls": null_thumb_urls,
                    "libfusion_urls": libfusion_urls,
                    "claire_marcus_urls": claire_marcus_urls,
                    "other_urls": other_urls
                }
                
                return True
            else:
                self.log_result(
                    "Analyse thumb_url (demande française)", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Analyse thumb_url (demande française)", False, error=str(e))
            return False
    
    def test_thumbnail_rebuild(self):
        """Step 4: Test POST /api/content/thumbnails/rebuild"""
        print("🔄 STEP 4: Thumbnail Rebuild Test")
        print("=" * 50)
        
        try:
            response = self.session.post(f"{API_BASE}/content/thumbnails/rebuild")
            
            if response.status_code == 200:
                data = response.json()
                scheduled = data.get("scheduled", 0)
                files_found = data.get("files_found", 0)
                
                self.log_result(
                    "Thumbnail Rebuild", 
                    True, 
                    f"Scheduled: {scheduled} thumbnails, Files found: {files_found}"
                )
                
                # Wait for background processing
                print("⏳ Waiting 5 seconds for thumbnail generation...")
                time.sleep(5)
                
                return True
            else:
                self.log_result(
                    "Thumbnail Rebuild", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Thumbnail Rebuild", False, error=str(e))
            return False
    
    def test_individual_thumbnail_generation(self):
        """Step 5: Test POST /api/content/{file_id}/thumbnail"""
        print("🎯 STEP 5: Individual Thumbnail Generation Test")
        print("=" * 50)
        
        if not hasattr(self, 'uploaded_file_id') or not self.uploaded_file_id:
            self.log_result(
                "Individual Thumbnail Generation", 
                False, 
                "No uploaded file ID available from previous test"
            )
            return False
        
        try:
            response = self.session.post(f"{API_BASE}/content/{self.uploaded_file_id}/thumbnail")
            
            if response.status_code == 200:
                data = response.json()
                scheduled = data.get("scheduled", False)
                file_id = data.get("file_id")
                
                self.log_result(
                    "Individual Thumbnail Generation", 
                    True, 
                    f"Thumbnail generation scheduled: {scheduled}, File ID: {file_id}"
                )
                
                # Wait for background processing
                print("⏳ Waiting 3 seconds for thumbnail generation...")
                time.sleep(3)
                
                return True
            else:
                self.log_result(
                    "Individual Thumbnail Generation", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Individual Thumbnail Generation", False, error=str(e))
            return False
    
    def test_thumbnail_accessibility(self):
        """Step 6: Verify thumbnails are accessible via /uploads/thumbs/"""
        print("🔍 STEP 6: Thumbnail Accessibility Test")
        print("=" * 50)
        
        if not hasattr(self, 'uploaded_filename') or not self.uploaded_filename:
            self.log_result(
                "Thumbnail Accessibility", 
                False, 
                "No uploaded filename available from previous test"
            )
            return False
        
        try:
            # Build expected thumbnail URL
            base_filename = os.path.splitext(self.uploaded_filename)[0]
            thumbnail_url = f"{BACKEND_URL}/uploads/thumbs/{base_filename}.webp"
            
            print(f"🔗 Testing thumbnail URL: {thumbnail_url}")
            
            response = requests.get(thumbnail_url)
            
            if response.status_code == 200:
                # Check if it's actually an image
                content_type = response.headers.get('content-type', '')
                
                if 'image' in content_type.lower():
                    # Try to verify it's a WEBP image and check dimensions
                    try:
                        img = Image.open(BytesIO(response.content))
                        width, height = img.size
                        format_name = img.format
                        
                        # Check if it meets the 320px WEBP requirements
                        is_correct_format = format_name == 'WEBP'
                        is_correct_size = max(width, height) <= 320
                        
                        self.log_result(
                            "Thumbnail Accessibility", 
                            True, 
                            f"Thumbnail accessible at {thumbnail_url}. Format: {format_name}, Size: {width}x{height}px, Correct format: {is_correct_format}, Correct size: {is_correct_size}"
                        )
                        
                        # Additional test for format and size requirements
                        if is_correct_format and is_correct_size:
                            self.log_result(
                                "Thumbnail Format Validation", 
                                True, 
                                f"Thumbnail meets requirements: 320px WEBP format"
                            )
                        else:
                            self.log_result(
                                "Thumbnail Format Validation", 
                                False, 
                                f"Thumbnail doesn't meet requirements. Expected: 320px WEBP, Got: {width}x{height}px {format_name}"
                            )
                        
                        return True
                        
                    except Exception as img_error:
                        self.log_result(
                            "Thumbnail Accessibility", 
                            False, 
                            f"Could not process thumbnail image: {str(img_error)}"
                        )
                        return False
                else:
                    self.log_result(
                        "Thumbnail Accessibility", 
                        False, 
                        f"URL accessible but not an image. Content-Type: {content_type}"
                    )
                    return False
            else:
                self.log_result(
                    "Thumbnail Accessibility", 
                    False, 
                    f"Thumbnail not accessible. Status: {response.status_code}",
                    f"URL: {thumbnail_url}"
                )
                return False
                
        except Exception as e:
            self.log_result("Thumbnail Accessibility", False, error=str(e))
            return False
    
    def test_mongodb_fix_verification(self):
        """Step 7: Verify the MongoDB comparison bug fix"""
        print("🔧 STEP 7: MongoDB Fix Verification")
        print("=" * 50)
        
        try:
            # Test that we can get content without the "Collection objects do not implement truth value testing" error
            response = self.session.get(f"{API_BASE}/content/pending?limit=5")
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                
                self.log_result(
                    "MongoDB Fix Verification", 
                    True, 
                    f"Successfully retrieved content list with {len(content)} items. No 'Collection objects do not implement truth value testing' error."
                )
                return True
            else:
                self.log_result(
                    "MongoDB Fix Verification", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            error_msg = str(e)
            if "Collection objects do not implement truth value testing" in error_msg:
                self.log_result(
                    "MongoDB Fix Verification", 
                    False, 
                    "The MongoDB comparison bug is still present!",
                    error_msg
                )
            else:
                self.log_result("MongoDB Fix Verification", False, error=error_msg)
            return False
    
    def run_all_tests(self):
        """Run all thumbnail system tests"""
        print("🚀 THUMBNAIL GENERATION SYSTEM TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_EMAIL}")
        print("=" * 60)
        print()
        
        # Initialize test variables
        self.uploaded_file_id = None
        self.uploaded_filename = None
        
        # Run tests in sequence
        tests = [
            self.authenticate,
            self.test_batch_upload,
            self.test_thumbnail_status,
            self.test_thumbnail_rebuild,
            self.test_individual_thumbnail_generation,
            self.test_thumbnail_accessibility,
            self.test_mongodb_fix_verification
        ]
        
        for test in tests:
            if not test():
                print("❌ Test failed, continuing with remaining tests...")
            print()
        
        # Summary
        print("📋 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Detailed results
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
            if result['error']:
                print(f"   Error: {result['error']}")
        
        print()
        print("🎯 THUMBNAIL SYSTEM TESTING COMPLETED")
        
        return success_rate >= 80  # Consider successful if 80% or more tests pass

if __name__ == "__main__":
    tester = ThumbnailSystemTester()
    success = tester.run_all_tests()
    
    if success:
        print("✅ Overall testing: SUCCESS")
        exit(0)
    else:
        print("❌ Overall testing: FAILED")
        exit(1)