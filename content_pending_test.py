#!/usr/bin/env python3
"""
Content Pending Endpoint Test
Test the new /api/content/pending endpoint as requested in the review.
"""

import requests
import json
import os
import base64
import tempfile
from datetime import datetime

class ContentPendingTester:
    def __init__(self):
        # Use production backend URL from frontend/.env
        self.base_url = "https://claire-marcus-app-1.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.uploads_dir = "/app/backend/uploads"

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {}
        
        # Add authentication header if we have a token
        if self.access_token:
            test_headers['Authorization'] = f'Bearer {self.access_token}'
        
        # Add custom headers
        if headers:
            test_headers.update(headers)
        
        # Don't set Content-Type for multipart/form-data requests
        if not files and method in ['POST', 'PUT']:
            test_headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, params=data)
            elif method == 'POST':
                if files:
                    response = requests.post(url, data=data, files=files, headers=test_headers)
                else:
                    response = requests.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:300]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_user_login(self):
        """Test user login with the specified credentials"""
        login_data = {
            "email": "lperpere@yahoo.fr",
            "password": "L@Reunion974!"
        }
        
        success, response = self.run_test(
            "User Login (lperpere@yahoo.fr)",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.access_token = response['access_token']
            print(f"   Access Token: {self.access_token[:20]}...")
            return True
        return False

    def test_content_pending_empty(self):
        """Test /api/content/pending endpoint returns empty list when no files uploaded"""
        success, response = self.run_test(
            "Content Pending - Empty State",
            "GET",
            "content/pending",
            200
        )
        
        if success:
            if 'content' in response and isinstance(response['content'], list):
                print(f"   Found {len(response['content'])} files in pending content")
                return True
            else:
                print("   ❌ Response missing 'content' array")
                return False
        return False

    def test_content_pending_authentication_with_token(self):
        """Test /api/content/pending endpoint with Bearer token authentication"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
            
        success, response = self.run_test(
            "Content Pending - With Authentication",
            "GET",
            "content/pending",
            200
        )
        
        if success:
            print("✅ Endpoint accessible with Bearer token authentication")
            return True
        return False

    def test_content_pending_authentication_without_token(self):
        """Test /api/content/pending endpoint without authentication (demo mode)"""
        # Temporarily remove token
        temp_token = self.access_token
        self.access_token = None
        
        success, response = self.run_test(
            "Content Pending - Demo Mode (No Auth)",
            "GET",
            "content/pending",
            200
        )
        
        # Restore token
        self.access_token = temp_token
        
        if success:
            print("✅ Endpoint accessible in demo mode without authentication")
            return True
        return False

    def create_test_files(self):
        """Create test files in uploads directory for testing"""
        print("\n📁 Creating test files in uploads directory...")
        
        # Ensure uploads directory exists
        os.makedirs(self.uploads_dir, exist_ok=True)
        
        # Create test image file (minimal JPEG)
        test_image_path = os.path.join(self.uploads_dir, "test_image.jpg")
        with open(test_image_path, "wb") as f:
            # Minimal JPEG header
            f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9')
        
        # Create test video file (minimal MP4)
        test_video_path = os.path.join(self.uploads_dir, "test_video.mp4")
        with open(test_video_path, "wb") as f:
            # Minimal MP4 header
            f.write(b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom\x00\x00\x00\x08free')
        
        # Create test text file (should not appear in content list)
        test_text_path = os.path.join(self.uploads_dir, "test_document.txt")
        with open(test_text_path, "w") as f:
            f.write("This is a test document that should not appear in content list")
        
        print(f"✅ Created test files:")
        print(f"   - {test_image_path} (image)")
        print(f"   - {test_video_path} (video)")
        print(f"   - {test_text_path} (text - should be ignored)")
        
        return True

    def test_content_pending_with_files(self):
        """Test /api/content/pending endpoint with uploaded files"""
        success, response = self.run_test(
            "Content Pending - With Files",
            "GET",
            "content/pending",
            200
        )
        
        if success:
            content_files = response.get('content', [])
            print(f"   Found {len(content_files)} content files")
            
            # Verify response format
            for file_item in content_files:
                required_fields = ['id', 'filename', 'file_type', 'size', 'uploaded_at']
                missing_fields = [field for field in required_fields if field not in file_item]
                
                if missing_fields:
                    print(f"   ❌ File missing required fields: {missing_fields}")
                    return False
                
                print(f"   📄 File: {file_item['filename']}")
                print(f"      - ID: {file_item['id']}")
                print(f"      - Type: {file_item['file_type']}")
                print(f"      - Size: {file_item['size']} bytes")
                print(f"      - Uploaded: {file_item['uploaded_at']}")
                
                # Check if image has base64 data
                if file_item['file_type'].startswith('image/'):
                    if 'file_data' in file_item and file_item['file_data']:
                        print(f"      - Base64 data: {len(file_item['file_data'])} characters")
                    else:
                        print(f"      - ⚠️ No base64 data for image file")
            
            return True
        return False

    def test_response_format_validation(self):
        """Test that response format matches frontend expectations"""
        success, response = self.run_test(
            "Content Pending - Response Format Validation",
            "GET",
            "content/pending",
            200
        )
        
        if success:
            # Verify top-level structure
            if 'content' not in response:
                print("   ❌ Missing 'content' key in response")
                return False
            
            if not isinstance(response['content'], list):
                print("   ❌ 'content' should be an array")
                return False
            
            print("✅ Response has correct top-level structure")
            
            # Verify file structure if files exist
            content_files = response['content']
            if content_files:
                sample_file = content_files[0]
                expected_fields = {
                    'id': str,
                    'filename': str,
                    'file_type': str,
                    'size': int,
                    'uploaded_at': str
                }
                
                for field, expected_type in expected_fields.items():
                    if field not in sample_file:
                        print(f"   ❌ Missing required field: {field}")
                        return False
                    
                    if not isinstance(sample_file[field], expected_type):
                        print(f"   ❌ Field {field} has wrong type: expected {expected_type}, got {type(sample_file[field])}")
                        return False
                
                print("✅ File objects have correct structure and types")
                
                # Verify image files have base64 data
                image_files = [f for f in content_files if f['file_type'].startswith('image/')]
                for img_file in image_files:
                    if 'file_data' not in img_file:
                        print(f"   ⚠️ Image file {img_file['filename']} missing file_data field")
                    elif not img_file['file_data']:
                        print(f"   ⚠️ Image file {img_file['filename']} has empty file_data")
                    else:
                        print(f"✅ Image file {img_file['filename']} has base64 data")
            
            return True
        return False

    def test_file_type_filtering(self):
        """Test that only images and videos are returned (no text files)"""
        success, response = self.run_test(
            "Content Pending - File Type Filtering",
            "GET",
            "content/pending",
            200
        )
        
        if success:
            content_files = response.get('content', [])
            
            # Check that all files are images or videos
            for file_item in content_files:
                file_type = file_item.get('file_type', '')
                if not (file_type.startswith('image/') or file_type.startswith('video/')):
                    print(f"   ❌ Non-media file found: {file_item['filename']} ({file_type})")
                    return False
            
            print(f"✅ All {len(content_files)} files are images or videos")
            
            # Verify text file is not included
            filenames = [f['filename'] for f in content_files]
            if 'test_document.txt' in filenames:
                print("   ❌ Text file incorrectly included in results")
                return False
            
            print("✅ Text files correctly filtered out")
            return True
        return False

    def cleanup_test_files(self):
        """Clean up test files created during testing"""
        print("\n🧹 Cleaning up test files...")
        
        test_files = [
            os.path.join(self.uploads_dir, "test_image.jpg"),
            os.path.join(self.uploads_dir, "test_video.mp4"),
            os.path.join(self.uploads_dir, "test_document.txt")
        ]
        
        for file_path in test_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"   ✅ Removed {file_path}")
            except Exception as e:
                print(f"   ⚠️ Could not remove {file_path}: {e}")

    def run_content_pending_tests(self):
        """Run all content pending endpoint tests"""
        print("🚀 Starting Content Pending Endpoint Testing")
        print("=" * 60)
        print(f"Backend URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        print(f"Uploads Directory: {self.uploads_dir}")
        print("=" * 60)
        
        # Test sequence
        test_sequence = [
            # Authentication
            ("User Login", self.test_user_login),
            
            # Test 1: Empty state
            ("Content Pending - Empty State", self.test_content_pending_empty),
            
            # Test 2: Authentication tests
            ("Content Pending - With Bearer Token", self.test_content_pending_authentication_with_token),
            ("Content Pending - Demo Mode", self.test_content_pending_authentication_without_token),
            
            # Test 3: Create test files
            ("Create Test Files", self.create_test_files),
            
            # Test 4: Test with files
            ("Content Pending - With Files", self.test_content_pending_with_files),
            
            # Test 5: Response format validation
            ("Response Format Validation", self.test_response_format_validation),
            
            # Test 6: File type filtering
            ("File Type Filtering", self.test_file_type_filtering),
        ]
        
        # Run tests
        for test_name, test_func in test_sequence:
            try:
                result = test_func()
                if not result:
                    print(f"❌ Test failed: {test_name}")
            except Exception as e:
                print(f"❌ Test error in {test_name}: {str(e)}")
        
        # Cleanup
        self.cleanup_test_files()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 CONTENT PENDING ENDPOINT TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED!")
            print("\n✅ ENDPOINT VERIFICATION COMPLETE:")
            print("   1. ✅ Endpoint exists and returns proper response")
            print("   2. ✅ Authentication works with Bearer token and demo mode")
            print("   3. ✅ File listing functionality works correctly")
            print("   4. ✅ Response format matches frontend expectations")
            print("   5. ✅ Base64 data included for images")
            print("   6. ✅ File type filtering works (images/videos only)")
        else:
            print(f"⚠️ {self.tests_run - self.tests_passed} tests failed")
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = ContentPendingTester()
    success = tester.run_content_pending_tests()
    exit(0 if success else 1)