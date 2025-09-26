#!/usr/bin/env python3
"""
Content Library Backend Testing
Tests the enhanced content library endpoints for image optimization and file management
"""

import requests
import json
import os
import tempfile
import uuid
from datetime import datetime
from PIL import Image
import io
import base64

class ContentLibraryTester:
    def __init__(self):
        # Use production backend URL from frontend/.env
        self.base_url = "https://social-ai-planner-2.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.uploaded_file_ids = []  # Track uploaded files for cleanup

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {name}")
            if details:
                print(f"   {details}")

    def make_request(self, method, endpoint, data=None, files=None, expected_status=200):
        """Make HTTP request with authentication"""
        url = f"{self.api_url}/{endpoint}"
        headers = {}
        
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        # Don't set Content-Type for multipart requests
        if not files and method in ['POST', 'PUT'] and data:
            headers['Content-Type'] = 'application/json'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=data)
            elif method == 'POST':
                if files:
                    response = requests.post(url, data=data, files=files, headers=headers)
                else:
                    response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                if files:
                    response = requests.put(url, data=data, files=files, headers=headers)
                else:
                    response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            
            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text}
            
            return success, response_data, response.status_code
            
        except Exception as e:
            return False, {"error": str(e)}, 0

    def authenticate(self):
        """Authenticate with test user credentials"""
        print("🔐 Authenticating with test user...")
        
        login_data = {
            "email": "lperpere@yahoo.fr",
            "password": "L@Reunion974!"
        }
        
        success, response, status = self.make_request("POST", "auth/login", data=login_data)
        
        if success and 'access_token' in response:
            self.access_token = response['access_token']
            self.log_test("User Authentication", True, f"Token obtained: {self.access_token[:20]}...")
            return True
        else:
            self.log_test("User Authentication", False, f"Status: {status}, Response: {response}")
            return False

    def create_test_image(self, width=1920, height=1080, format='JPEG'):
        """Create a test image for upload testing"""
        # Create a test image with specific dimensions
        image = Image.new('RGB', (width, height), color='red')
        
        # Add some content to make it more realistic
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(image)
        try:
            # Try to use a default font
            font = ImageFont.load_default()
        except:
            font = None
        
        draw.text((width//2-50, height//2), "TEST IMAGE", fill='white', font=font)
        
        # Save to bytes
        img_bytes = io.BytesIO()
        image.save(img_bytes, format=format, quality=95)
        img_bytes.seek(0)
        
        return img_bytes.getvalue(), image.size

    def test_image_optimization_upload(self):
        """Test 1: Image optimization during batch upload"""
        print("\n🖼️ Testing Image Optimization Upload...")
        
        # Create a large test image (should be optimized)
        original_image_data, original_size = self.create_test_image(2400, 1800)  # Large image
        original_file_size = len(original_image_data)
        
        print(f"   Original image: {original_size[0]}x{original_size[1]}, {original_file_size} bytes")
        
        # Prepare multipart upload
        files = [
            ('files', ('test_large_image.jpg', original_image_data, 'image/jpeg'))
        ]
        
        success, response, status = self.make_request(
            "POST", 
            "content/batch-upload", 
            files=files,
            expected_status=200
        )
        
        if success and 'uploaded_files' in response:
            uploaded_file = response['uploaded_files'][0]
            self.uploaded_file_ids.append(uploaded_file['id'])
            
            # Verify optimization occurred
            optimized_size = uploaded_file.get('size', 0)
            
            # Check if file was actually saved and optimized
            file_path = uploaded_file.get('file_path', '')
            # Fix path - server uses relative path, but files are in backend/uploads
            if not file_path.startswith('/'):
                file_path = f"/app/backend/{file_path}"
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    optimized_data = f.read()
                    
                # Check if image was resized (should be smaller)
                try:
                    optimized_image = Image.open(io.BytesIO(optimized_data))
                    optimized_dimensions = optimized_image.size
                    
                    # Verify optimization criteria
                    min_side = min(optimized_dimensions)
                    size_reduced = len(optimized_data) < original_file_size
                    
                    details = f"Optimized to {optimized_dimensions[0]}x{optimized_dimensions[1]}, {len(optimized_data)} bytes"
                    details += f", Min side: {min_side}px, Size reduced: {size_reduced}"
                    
                    # Image should be optimized to 1080px on smallest side
                    optimization_success = min_side <= 1080 and size_reduced
                    
                    self.log_test("Image Optimization", optimization_success, details)
                    return optimization_success
                    
                except Exception as e:
                    self.log_test("Image Optimization", False, f"Error reading optimized image: {e}")
                    return False
            else:
                self.log_test("Image Optimization", False, f"Optimized file not found at {file_path}")
                return False
        else:
            self.log_test("Image Optimization", False, f"Upload failed: {response}")
            return False

    def test_content_listing(self):
        """Test 2: Content listing with proper format and base64 data"""
        print("\n📋 Testing Content Listing...")
        
        success, response, status = self.make_request("GET", "content/pending")
        
        if success and 'content' in response:
            content_files = response['content']
            
            if len(content_files) > 0:
                # Check first file structure
                first_file = content_files[0]
                required_fields = ['id', 'filename', 'file_type', 'size', 'uploaded_at', 'description']
                
                missing_fields = [field for field in required_fields if field not in first_file]
                
                if not missing_fields:
                    # Check if images have base64 data
                    has_base64 = False
                    image_count = 0
                    
                    for file_item in content_files:
                        if file_item.get('file_type', '').startswith('image/'):
                            image_count += 1
                            if file_item.get('file_data'):
                                has_base64 = True
                                break
                    
                    # Check file filtering (only images/videos)
                    valid_types = all(
                        file_item.get('file_type', '').startswith(('image/', 'video/'))
                        for file_item in content_files
                    )
                    
                    details = f"Found {len(content_files)} files, {image_count} images"
                    details += f", Base64 data: {has_base64}, Valid types only: {valid_types}"
                    
                    listing_success = has_base64 and valid_types
                    self.log_test("Content Listing", listing_success, details)
                    return listing_success
                else:
                    self.log_test("Content Listing", False, f"Missing fields: {missing_fields}")
                    return False
            else:
                self.log_test("Content Listing", True, "No files found (empty list is valid)")
                return True
        else:
            self.log_test("Content Listing", False, f"Failed to get content: {response}")
            return False

    def test_description_update(self):
        """Test 3: Description update functionality"""
        print("\n📝 Testing Description Update...")
        
        if not self.uploaded_file_ids:
            # Upload a test file first
            test_image_data, _ = self.create_test_image(800, 600)
            files = [('files', ('test_desc_image.jpg', test_image_data, 'image/jpeg'))]
            
            success, response, status = self.make_request("POST", "content/batch-upload", files=files)
            if success and 'uploaded_files' in response:
                self.uploaded_file_ids.append(response['uploaded_files'][0]['id'])
        
        if self.uploaded_file_ids:
            file_id = self.uploaded_file_ids[0]
            test_description = f"Test description updated at {datetime.now().isoformat()}"
            
            description_data = {"description": test_description}
            
            success, response, status = self.make_request(
                "PUT", 
                f"content/{file_id}/description",
                data=description_data
            )
            
            if success and response.get('message') and response.get('description') == test_description:
                self.log_test("Description Update", True, f"Updated description: {test_description[:50]}...")
                return True
            else:
                self.log_test("Description Update", False, f"Update failed: {response}")
                return False
        else:
            self.log_test("Description Update", False, "No uploaded files available for testing")
            return False

    def test_file_deletion(self):
        """Test 4: File deletion functionality"""
        print("\n🗑️ Testing File Deletion...")
        
        # Upload a test file specifically for deletion
        test_image_data, _ = self.create_test_image(400, 300)
        files = [('files', ('test_delete_image.jpg', test_image_data, 'image/jpeg'))]
        
        success, response, status = self.make_request("POST", "content/batch-upload", files=files)
        
        if success and 'uploaded_files' in response:
            uploaded_file = response['uploaded_files'][0]
            stored_filename = uploaded_file.get('stored_name', '')
            file_path = uploaded_file.get('file_path', '')
            
            # Get the correct file_id from the listing endpoint (filename without extension)
            success_list, list_response, _ = self.make_request("GET", "content/pending")
            
            if success_list and 'content' in list_response:
                # Find our uploaded file in the list
                target_file_id = None
                for file_item in list_response['content']:
                    if file_item.get('filename') == stored_filename:
                        target_file_id = file_item.get('id')
                        break
                
                if target_file_id:
                    # Fix path for checking
                    if file_path and not file_path.startswith('/'):
                        full_file_path = f"/app/backend/{file_path}"
                    else:
                        full_file_path = file_path
                    file_exists_before = os.path.exists(full_file_path) if full_file_path else False
                    
                    # Delete the file using the correct ID
                    success, response, status = self.make_request("DELETE", f"content/{target_file_id}")
                    
                    if success:
                        # Verify file was actually removed from filesystem
                        file_exists_after = os.path.exists(full_file_path) if full_file_path else True
                        
                        deletion_success = not file_exists_after
                        details = f"File existed before: {file_exists_before}, exists after: {file_exists_after}"
                        
                        self.log_test("File Deletion", deletion_success, details)
                        return deletion_success
                    else:
                        self.log_test("File Deletion", False, f"Delete request failed: {response}")
                        return False
                else:
                    self.log_test("File Deletion", False, "Could not find uploaded file in content listing")
                    return False
            else:
                self.log_test("File Deletion", False, "Could not get content listing")
                return False
        else:
            self.log_test("File Deletion", False, f"Failed to upload test file for deletion: {response}")
            return False

    def test_upload_validation(self):
        """Test 5: Upload validation (file type and size limits)"""
        print("\n🔍 Testing Upload Validation...")
        
        # Test invalid file type
        invalid_file_data = b"This is not an image file"
        files = [('files', ('test.txt', invalid_file_data, 'text/plain'))]
        
        success, response, status = self.make_request(
            "POST", 
            "content/batch-upload", 
            files=files,
            expected_status=200  # Should succeed but with failed uploads
        )
        
        type_validation_passed = False
        if success and 'failed_uploads' in response:
            failed_uploads = response['failed_uploads']
            if len(failed_uploads) > 0:
                error_msg = failed_uploads[0].get('error', '')
                if 'Type de fichier non supporté' in error_msg:
                    type_validation_passed = True
        
        # Test oversized file (create a large dummy file > 10MB)
        large_file_data = b'x' * (11 * 1024 * 1024)  # 11MB
        files = [('files', ('large_image.jpg', large_file_data, 'image/jpeg'))]
        
        success, response, status = self.make_request(
            "POST", 
            "content/batch-upload", 
            files=files,
            expected_status=200
        )
        
        size_validation_passed = False
        if success and 'failed_uploads' in response:
            failed_uploads = response['failed_uploads']
            if len(failed_uploads) > 0:
                error_msg = failed_uploads[0].get('error', '')
                if 'trop volumineux' in error_msg:
                    size_validation_passed = True
        
        validation_success = type_validation_passed and size_validation_passed
        details = f"Type validation: {type_validation_passed}, Size validation: {size_validation_passed}"
        
        self.log_test("Upload Validation", validation_success, details)
        return validation_success

    def cleanup_uploaded_files(self):
        """Clean up any uploaded test files"""
        print("\n🧹 Cleaning up uploaded test files...")
        
        for file_id in self.uploaded_file_ids:
            try:
                success, response, status = self.make_request("DELETE", f"content/{file_id}")
                if success:
                    print(f"   ✅ Cleaned up file {file_id}")
                else:
                    print(f"   ⚠️ Could not clean up file {file_id}: {response}")
            except Exception as e:
                print(f"   ⚠️ Error cleaning up file {file_id}: {e}")

    def run_all_tests(self):
        """Run all content library tests"""
        print("🚀 Starting Enhanced Content Library Backend Testing")
        print("=" * 70)
        print(f"Backend URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        print("=" * 70)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return
        
        # Run all tests
        test_results = []
        
        print("\n" + "="*50)
        print("CONTENT LIBRARY ENDPOINT TESTS")
        print("="*50)
        
        # Test 1: Image optimization
        test_results.append(self.test_image_optimization_upload())
        
        # Test 2: Content listing
        test_results.append(self.test_content_listing())
        
        # Test 3: Description update
        test_results.append(self.test_description_update())
        
        # Test 4: File deletion
        test_results.append(self.test_file_deletion())
        
        # Test 5: Upload validation
        test_results.append(self.test_upload_validation())
        
        # Cleanup
        self.cleanup_uploaded_files()
        
        # Print summary
        print("\n" + "="*50)
        print("TEST SUMMARY")
        print("="*50)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if all(test_results):
            print("\n🎉 ALL CONTENT LIBRARY TESTS PASSED!")
            return True
        else:
            print(f"\n⚠️ {len([r for r in test_results if not r])} test(s) failed")
            return False

if __name__ == "__main__":
    tester = ContentLibraryTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)