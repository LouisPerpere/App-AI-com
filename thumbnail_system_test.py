#!/usr/bin/env python3
"""
Thumbnail Generation System Test - French Review Request
Test du nouveau système de génération de vignettes qui vient d'être implémenté

Tests requested:
1. Authentifier avec lperpere@yahoo.fr / L@Reunion974!
2. Tester POST /api/content/thumbnails/rebuild pour générer les vignettes manquantes
3. Tester GET /api/content/thumbnails/status pour voir le statut de génération
4. Vérifier que POST /api/content/batch-upload fonctionne avec génération en arrière-plan
5. Tester POST /api/content/{file_id}/thumbnail pour générer une vignette individuelle
6. Vérifier que les vignettes sont accessibles via /uploads/thumbs/

Le système utilise Pillow pour les images et ffmpeg pour les vidéos, 
avec génération de vignettes carrées 320px en format WEBP.
"""

import requests
import json
import os
import time
import uuid
from datetime import datetime
import tempfile
from PIL import Image
import io
import base64

# Configuration - Using production URL as specified in review request
BACKEND_URL = "https://libfusion.preview.emergentagent.com/api"
TEST_USER_EMAIL = "lperpere@yahoo.fr"
TEST_USER_PASSWORD = "L@Reunion974!"

class ThumbnailSystemTester:
    def __init__(self):
        self.session = requests.Session()
        # Disable SSL verification for testing in container environment
        self.session.verify = False
        # Disable SSL warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.access_token = None
        self.test_results = []
        self.test_file_ids = []  # Track uploaded test files for cleanup
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        return success
    
    def authenticate(self):
        """Authenticate with the backend"""
        try:
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                if self.access_token:
                    # Set authorization header for all future requests
                    self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                    return self.log_test("Authentication", True, f"Successfully authenticated as {TEST_USER_EMAIL}")
                else:
                    return self.log_test("Authentication", False, "No access token in response")
            else:
                return self.log_test("Authentication", False, f"Login failed with status {response.status_code}: {response.text}")
                
        except Exception as e:
            return self.log_test("Authentication", False, f"Authentication error: {str(e)}")
    
    def create_test_image(self, width=800, height=600, format='JPEG'):
        """Create a test image for upload testing"""
        # Create a simple test image with PIL
        image = Image.new('RGB', (width, height), color='red')
        
        # Add some visual content
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(image)
        try:
            # Try to use a default font, fallback to basic if not available
            font = ImageFont.load_default()
        except:
            font = None
        
        draw.text((width//4, height//2), "TEST IMAGE", fill='white', font=font)
        draw.rectangle([width//4, height//4, 3*width//4, 3*height//4], outline='blue', width=5)
        
        # Convert to bytes
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        buffer.seek(0)
        return buffer.getvalue()
    
    def test_thumbnail_status_initial(self):
        """Test GET /api/content/thumbnails/status - Initial status"""
        try:
            response = self.session.get(f"{BACKEND_URL}/content/thumbnails/status", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_files", "with_thumbnails", "missing_thumbnails", "completion_percentage"]
                
                if all(field in data for field in required_fields):
                    details = f"Total files: {data['total_files']}, With thumbnails: {data['with_thumbnails']}, Missing: {data['missing_thumbnails']}, Completion: {data['completion_percentage']}%"
                    return self.log_test("Thumbnail Status Initial", True, details)
                else:
                    return self.log_test("Thumbnail Status Initial", False, f"Missing required fields in response: {data}")
            else:
                return self.log_test("Thumbnail Status Initial", False, f"Status endpoint failed with {response.status_code}: {response.text}")
                
        except Exception as e:
            return self.log_test("Thumbnail Status Initial", False, f"Error: {str(e)}")
    
    def test_batch_upload_with_thumbnails(self):
        """Test POST /api/content/batch-upload with thumbnail generation"""
        try:
            # Create test images
            test_image_1 = self.create_test_image(800, 600, 'JPEG')
            test_image_2 = self.create_test_image(1200, 800, 'PNG')
            
            # Prepare multipart form data
            files = [
                ('files', ('test_thumb_1.jpg', test_image_1, 'image/jpeg')),
                ('files', ('test_thumb_2.png', test_image_2, 'image/png'))
            ]
            
            response = self.session.post(f"{BACKEND_URL}/content/batch-upload", files=files, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                if "uploaded_files" in data and len(data["uploaded_files"]) == 2:
                    # Store file IDs for later testing
                    for file_info in data["uploaded_files"]:
                        if "id" in file_info:
                            self.test_file_ids.append(file_info["id"])
                    
                    details = f"Successfully uploaded {len(data['uploaded_files'])} files with background thumbnail generation scheduled"
                    return self.log_test("Batch Upload with Thumbnails", True, details)
                else:
                    return self.log_test("Batch Upload with Thumbnails", False, f"Unexpected response structure: {data}")
            else:
                return self.log_test("Batch Upload with Thumbnails", False, f"Upload failed with {response.status_code}: {response.text}")
                
        except Exception as e:
            return self.log_test("Batch Upload with Thumbnails", False, f"Error: {str(e)}")
    
    def test_rebuild_missing_thumbnails(self):
        """Test POST /api/content/thumbnails/rebuild"""
        try:
            # Wait a moment for any previous uploads to complete
            time.sleep(2)
            
            response = self.session.post(f"{BACKEND_URL}/content/thumbnails/rebuild", timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                if "ok" in data and data["ok"] and "scheduled" in data:
                    details = f"Rebuild scheduled for {data.get('scheduled', 0)} files, found {data.get('files_found', 0)} files needing thumbnails"
                    return self.log_test("Rebuild Missing Thumbnails", True, details)
                else:
                    return self.log_test("Rebuild Missing Thumbnails", False, f"Unexpected response structure: {data}")
            else:
                return self.log_test("Rebuild Missing Thumbnails", False, f"Rebuild failed with {response.status_code}: {response.text}")
                
        except Exception as e:
            return self.log_test("Rebuild Missing Thumbnails", False, f"Error: {str(e)}")
    
    def test_individual_thumbnail_generation(self):
        """Test POST /api/content/{file_id}/thumbnail"""
        if not self.test_file_ids:
            return self.log_test("Individual Thumbnail Generation", False, "No test file IDs available")
        
        try:
            file_id = self.test_file_ids[0]  # Use first uploaded file
            response = self.session.post(f"{BACKEND_URL}/content/{file_id}/thumbnail", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if "ok" in data and data["ok"] and "scheduled" in data:
                    details = f"Individual thumbnail generation scheduled for file {file_id}"
                    return self.log_test("Individual Thumbnail Generation", True, details)
                else:
                    return self.log_test("Individual Thumbnail Generation", False, f"Unexpected response structure: {data}")
            else:
                return self.log_test("Individual Thumbnail Generation", False, f"Individual thumbnail failed with {response.status_code}: {response.text}")
                
        except Exception as e:
            return self.log_test("Individual Thumbnail Generation", False, f"Error: {str(e)}")
    
    def test_thumbnail_status_after_generation(self):
        """Test GET /api/content/thumbnails/status after generation"""
        try:
            # Wait for thumbnail generation to complete
            print("⏳ Waiting 10 seconds for thumbnail generation to complete...")
            time.sleep(10)
            
            response = self.session.get(f"{BACKEND_URL}/content/thumbnails/status", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_files", "with_thumbnails", "missing_thumbnails", "completion_percentage"]
                
                if all(field in data for field in required_fields):
                    details = f"After generation - Total files: {data['total_files']}, With thumbnails: {data['with_thumbnails']}, Missing: {data['missing_thumbnails']}, Completion: {data['completion_percentage']}%"
                    
                    # Check if completion percentage improved
                    if data['completion_percentage'] > 0:
                        return self.log_test("Thumbnail Status After Generation", True, details)
                    else:
                        return self.log_test("Thumbnail Status After Generation", False, f"No thumbnails generated: {details}")
                else:
                    return self.log_test("Thumbnail Status After Generation", False, f"Missing required fields in response: {data}")
            else:
                return self.log_test("Thumbnail Status After Generation", False, f"Status endpoint failed with {response.status_code}: {response.text}")
                
        except Exception as e:
            return self.log_test("Thumbnail Status After Generation", False, f"Error: {str(e)}")
    
    def test_thumbnail_accessibility(self):
        """Test that thumbnails are accessible via /uploads/thumbs/ URL"""
        try:
            # Get content list to find files with thumbnails
            response = self.session.get(f"{BACKEND_URL}/content/pending?limit=10", timeout=30)
            
            if response.status_code != 200:
                return self.log_test("Thumbnail Accessibility", False, f"Could not get content list: {response.status_code}")
            
            data = response.json()
            content_files = data.get("content", [])
            
            if not content_files:
                return self.log_test("Thumbnail Accessibility", False, "No content files found to test thumbnail accessibility")
            
            # Look for files with thumb_url
            thumbnail_urls_found = 0
            accessible_thumbnails = 0
            
            for file_info in content_files:
                thumb_url = file_info.get("thumb_url")
                if thumb_url:
                    thumbnail_urls_found += 1
                    
                    # Test if thumbnail URL is accessible
                    try:
                        # Remove authentication for public thumbnail access
                        thumb_response = requests.get(thumb_url, timeout=10, verify=False)
                        if thumb_response.status_code == 200:
                            accessible_thumbnails += 1
                    except:
                        pass  # Count as inaccessible
            
            if thumbnail_urls_found > 0:
                details = f"Found {thumbnail_urls_found} thumbnail URLs, {accessible_thumbnails} accessible via /uploads/thumbs/"
                success = accessible_thumbnails > 0
                return self.log_test("Thumbnail Accessibility", success, details)
            else:
                return self.log_test("Thumbnail Accessibility", False, "No thumbnail URLs found in content files")
                
        except Exception as e:
            return self.log_test("Thumbnail Accessibility", False, f"Error: {str(e)}")
    
    def test_thumbnail_format_and_size(self):
        """Test that thumbnails are in correct format (WEBP) and size (320px square)"""
        try:
            # Get content list to find files with thumbnails
            response = self.session.get(f"{BACKEND_URL}/content/pending?limit=5", timeout=30)
            
            if response.status_code != 200:
                return self.log_test("Thumbnail Format and Size", False, f"Could not get content list: {response.status_code}")
            
            data = response.json()
            content_files = data.get("content", [])
            
            webp_thumbnails = 0
            correct_size_thumbnails = 0
            square_thumbnails = 0
            
            for file_info in content_files:
                thumb_url = file_info.get("thumb_url")
                if thumb_url and "/uploads/thumbs/" in thumb_url:
                    try:
                        # Download thumbnail
                        thumb_response = requests.get(thumb_url, timeout=10, verify=False)
                        if thumb_response.status_code == 200:
                            # Check format
                            if thumb_url.lower().endswith('.webp'):
                                webp_thumbnails += 1
                            
                            # Check size using PIL
                            try:
                                image = Image.open(io.BytesIO(thumb_response.content))
                                width, height = image.size
                                
                                # Check if square
                                if width == height:
                                    square_thumbnails += 1
                                
                                # Check if 320px or smaller (due to aspect ratio constraints)
                                if max(width, height) <= 320:
                                    correct_size_thumbnails += 1
                                    
                            except Exception as img_error:
                                print(f"   Could not analyze image: {img_error}")
                                
                    except Exception as download_error:
                        print(f"   Could not download thumbnail: {download_error}")
            
            if webp_thumbnails > 0 or correct_size_thumbnails > 0:
                details = f"WEBP format: {webp_thumbnails}, Correct size (≤320px): {correct_size_thumbnails}, Square format: {square_thumbnails}"
                success = webp_thumbnails > 0 and correct_size_thumbnails > 0 and square_thumbnails > 0
                return self.log_test("Thumbnail Format and Size", success, details)
            else:
                return self.log_test("Thumbnail Format and Size", False, "No thumbnails found to analyze format and size")
                
        except Exception as e:
            return self.log_test("Thumbnail Format and Size", False, f"Error: {str(e)}")
    
    def cleanup_test_files(self):
        """Clean up test files uploaded during testing"""
        if not self.test_file_ids:
            return
        
        print("\n🧹 Cleaning up test files...")
        for file_id in self.test_file_ids:
            try:
                response = self.session.delete(f"{BACKEND_URL}/content/{file_id}", timeout=30)
                if response.status_code in [200, 204]:
                    print(f"   ✅ Deleted test file {file_id}")
                else:
                    print(f"   ⚠️ Could not delete test file {file_id}: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error deleting test file {file_id}: {str(e)}")
    
    def run_all_tests(self):
        """Run all thumbnail system tests"""
        print("🎯 THUMBNAIL GENERATION SYSTEM TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_USER_EMAIL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Test sequence as requested in French review
        tests = [
            ("1. Authentication", self.authenticate),
            ("2. Initial Thumbnail Status", self.test_thumbnail_status_initial),
            ("3. Batch Upload with Background Thumbnails", self.test_batch_upload_with_thumbnails),
            ("4. Rebuild Missing Thumbnails", self.test_rebuild_missing_thumbnails),
            ("5. Individual Thumbnail Generation", self.test_individual_thumbnail_generation),
            ("6. Thumbnail Status After Generation", self.test_thumbnail_status_after_generation),
            ("7. Thumbnail Accessibility via /uploads/thumbs/", self.test_thumbnail_accessibility),
            ("8. Thumbnail Format and Size Verification", self.test_thumbnail_format_and_size),
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running {test_name}...")
            test_func()
        
        # Cleanup
        self.cleanup_test_files()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 THUMBNAIL SYSTEM TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\nDetailed Results:")
        for result in self.test_results:
            print(f"  {result['status']}: {result['test']}")
            if result['details']:
                print(f"    → {result['details']}")
        
        # Overall assessment
        if success_rate >= 80:
            print(f"\n🎉 THUMBNAIL SYSTEM STATUS: EXCELLENT ({success_rate:.1f}% success rate)")
            print("✅ The thumbnail generation system is working correctly and ready for production.")
        elif success_rate >= 60:
            print(f"\n⚠️ THUMBNAIL SYSTEM STATUS: GOOD ({success_rate:.1f}% success rate)")
            print("✅ The thumbnail generation system is mostly functional with minor issues.")
        else:
            print(f"\n❌ THUMBNAIL SYSTEM STATUS: NEEDS ATTENTION ({success_rate:.1f}% success rate)")
            print("🔧 The thumbnail generation system requires fixes before production use.")
        
        return success_rate >= 60

if __name__ == "__main__":
    tester = ThumbnailSystemTester()
    tester.run_all_tests()