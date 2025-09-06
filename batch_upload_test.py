#!/usr/bin/env python3
"""
Test spécifique pour l'endpoint POST /api/content/batch-upload
Basé sur la review request française pour tester le nouvel endpoint d'upload
"""

import requests
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
import io

class BatchUploadTester:
    def __init__(self):
        # Use the production backend URL from frontend/.env
        self.base_url = "https://media-title-fix.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        
        print(f"🚀 BATCH UPLOAD ENDPOINT TESTING")
        print(f"📍 Backend URL: {self.base_url}")
        print(f"📍 API URL: {self.api_url}")
        print("=" * 80)

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
        
        # Don't set Content-Type for multipart/form-data requests (let requests handle it)
        if not files and method in ['POST', 'PUT'] and data:
            test_headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        print(f"   Expected Status: {expected_status}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                if files:
                    # For file uploads, don't send JSON data
                    response = requests.post(url, files=files, headers=test_headers, timeout=30)
                else:
                    response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)
            else:
                print(f"   ❌ Unsupported method: {method}")
                return False
            
            print(f"   Status Code: {response.status_code}")
            
            # Check if status matches expected
            if response.status_code == expected_status:
                print(f"   ✅ Status code matches expected ({expected_status})")
                
                # Try to parse JSON response
                try:
                    response_data = response.json()
                    print(f"   📄 Response: {json.dumps(response_data, indent=2)[:500]}...")
                    self.tests_passed += 1
                    return response_data
                except:
                    print(f"   📄 Response (non-JSON): {response.text[:200]}...")
                    self.tests_passed += 1
                    return response.text
            else:
                print(f"   ❌ Status code mismatch. Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   📄 Error Response: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   📄 Error Response (non-JSON): {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            return False

    def test_authentication(self):
        """Test 1: Authentication with provided credentials"""
        print(f"\n{'='*20} TEST 1: AUTHENTICATION {'='*20}")
        
        login_data = {
            "email": "lperpere@yahoo.fr",
            "password": "L@Reunion974!"
        }
        
        response = self.run_test(
            "User Login",
            "POST", 
            "auth/login",
            200,
            data=login_data
        )
        
        if response and isinstance(response, dict):
            self.access_token = response.get('access_token')
            self.user_id = response.get('user_id')
            
            if self.access_token:
                print(f"   ✅ Authentication successful")
                print(f"   🔑 Access Token: {self.access_token[:20]}...")
                print(f"   👤 User ID: {self.user_id}")
                return True
            else:
                print(f"   ❌ No access token in response")
                return False
        else:
            print(f"   ❌ Authentication failed")
            return False

    def test_endpoint_existence(self):
        """Test 2: Verify POST /api/content/batch-upload endpoint exists"""
        print(f"\n{'='*20} TEST 2: ENDPOINT EXISTENCE {'='*20}")
        
        # Test with empty files to check if endpoint exists (should return 422, not 404)
        response = self.run_test(
            "Batch Upload Endpoint Existence",
            "POST",
            "content/batch-upload", 
            422  # FastAPI returns 422 for missing required fields, not 404 for missing endpoint
        )
        
        if response:
            print(f"   ✅ Endpoint exists (returned 422 for missing files, not 404)")
            return True
        else:
            print(f"   ❌ Endpoint may not exist or returned unexpected status")
            return False

    def create_test_files(self):
        """Create test files for upload testing"""
        test_files = {}
        
        # Create a small test image (PNG)
        image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
        test_files['valid_image'] = ('test_image.png', io.BytesIO(image_content), 'image/png')
        
        # Create a small test video file (fake MP4 header)
        video_content = b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom\x00\x00\x00\x08free'
        test_files['valid_video'] = ('test_video.mp4', io.BytesIO(video_content), 'video/mp4')
        
        # Create an invalid file type (text file)
        text_content = b'This is a text file that should be rejected'
        test_files['invalid_text'] = ('test_file.txt', io.BytesIO(text_content), 'text/plain')
        
        # Create a large file (simulate > 10MB)
        large_content = b'x' * (11 * 1024 * 1024)  # 11MB
        test_files['large_image'] = ('large_image.png', io.BytesIO(large_content), 'image/png')
        
        return test_files

    def test_valid_upload(self):
        """Test 3: Valid file upload with image and video"""
        print(f"\n{'='*20} TEST 3: VALID FILE UPLOAD {'='*20}")
        
        test_files = self.create_test_files()
        
        # Prepare files for upload (using 'files' key as expected by frontend)
        files = [
            ('files', test_files['valid_image']),
            ('files', test_files['valid_video'])
        ]
        
        response = self.run_test(
            "Valid Files Upload",
            "POST",
            "content/batch-upload",
            200,
            files=files
        )
        
        if response and isinstance(response, dict):
            uploaded_files = response.get('uploaded_files', [])
            total_uploaded = response.get('total_uploaded', 0)
            
            print(f"   📊 Upload Results:")
            print(f"   📁 Total uploaded: {total_uploaded}")
            print(f"   📁 Files uploaded: {len(uploaded_files)}")
            
            if total_uploaded > 0:
                print(f"   ✅ Files uploaded successfully")
                
                # Check response format expected by frontend
                if 'uploaded_files' in response:
                    print(f"   ✅ Response contains 'uploaded_files' array as expected by frontend")
                    
                    # Check file metadata
                    for file_info in uploaded_files:
                        print(f"   📄 File: {file_info.get('original_name')} -> {file_info.get('stored_name')}")
                        print(f"       Size: {file_info.get('size')} bytes")
                        print(f"       Type: {file_info.get('content_type')}")
                    
                    return True
                else:
                    print(f"   ❌ Response missing 'uploaded_files' array")
                    return False
            else:
                print(f"   ❌ No files were uploaded")
                return False
        else:
            print(f"   ❌ Upload failed or invalid response")
            return False

    def test_invalid_file_types(self):
        """Test 4: Invalid file type rejection"""
        print(f"\n{'='*20} TEST 4: INVALID FILE TYPE REJECTION {'='*20}")
        
        test_files = self.create_test_files()
        
        # Try to upload invalid file type
        files = [
            ('files', test_files['invalid_text'])
        ]
        
        response = self.run_test(
            "Invalid File Type Upload",
            "POST",
            "content/batch-upload",
            200  # Should return 200 but with failed_uploads
        )
        
        if response and isinstance(response, dict):
            failed_uploads = response.get('failed_uploads', [])
            total_failed = response.get('total_failed', 0)
            total_uploaded = response.get('total_uploaded', 0)
            
            print(f"   📊 Upload Results:")
            print(f"   ❌ Total failed: {total_failed}")
            print(f"   ✅ Total uploaded: {total_uploaded}")
            
            if total_failed > 0 and total_uploaded == 0:
                print(f"   ✅ Invalid file type correctly rejected")
                
                # Check error message
                for failed in failed_uploads:
                    print(f"   📄 Failed file: {failed.get('filename')}")
                    print(f"       Error: {failed.get('error')}")
                
                return True
            else:
                print(f"   ❌ Invalid file type was not rejected properly")
                return False
        else:
            print(f"   ❌ Test failed or invalid response")
            return False

    def test_large_file_rejection(self):
        """Test 5: Large file size rejection"""
        print(f"\n{'='*20} TEST 5: LARGE FILE SIZE REJECTION {'='*20}")
        
        test_files = self.create_test_files()
        
        # Try to upload large file (> 10MB)
        files = [
            ('files', test_files['large_image'])
        ]
        
        response = self.run_test(
            "Large File Upload",
            "POST",
            "content/batch-upload",
            200  # Should return 200 but with failed_uploads
        )
        
        if response and isinstance(response, dict):
            failed_uploads = response.get('failed_uploads', [])
            total_failed = response.get('total_failed', 0)
            total_uploaded = response.get('total_uploaded', 0)
            
            print(f"   📊 Upload Results:")
            print(f"   ❌ Total failed: {total_failed}")
            print(f"   ✅ Total uploaded: {total_uploaded}")
            
            if total_failed > 0 and total_uploaded == 0:
                print(f"   ✅ Large file correctly rejected")
                
                # Check error message
                for failed in failed_uploads:
                    print(f"   📄 Failed file: {failed.get('filename')}")
                    print(f"       Error: {failed.get('error')}")
                
                return True
            else:
                print(f"   ❌ Large file was not rejected properly")
                return False
        else:
            print(f"   ❌ Test failed or invalid response")
            return False

    def test_no_files_error(self):
        """Test 6: No files provided error"""
        print(f"\n{'='*20} TEST 6: NO FILES ERROR {'='*20}")
        
        response = self.run_test(
            "No Files Provided",
            "POST",
            "content/batch-upload",
            422  # FastAPI returns 422 for missing required fields
        )
        
        if response:
            print(f"   ✅ Correctly returned 422 error for no files provided")
            return True
        else:
            print(f"   ❌ Did not handle no files case properly")
            return False

    def test_uploads_directory(self):
        """Test 7: Check if uploads directory is created"""
        print(f"\n{'='*20} TEST 7: UPLOADS DIRECTORY CHECK {'='*20}")
        
        uploads_dir = "/app/backend/uploads"
        
        if os.path.exists(uploads_dir):
            print(f"   ✅ Uploads directory exists: {uploads_dir}")
            
            # List files in directory
            files = os.listdir(uploads_dir)
            print(f"   📁 Files in uploads directory: {len(files)}")
            
            for file in files[:5]:  # Show first 5 files
                file_path = os.path.join(uploads_dir, file)
                file_size = os.path.getsize(file_path)
                print(f"       📄 {file} ({file_size} bytes)")
            
            return True
        else:
            print(f"   ❌ Uploads directory does not exist: {uploads_dir}")
            return False

    def run_all_tests(self):
        """Run all batch upload tests"""
        print(f"\n🎯 STARTING BATCH UPLOAD ENDPOINT TESTING")
        print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Test sequence based on review request
        tests = [
            ("Authentication", self.test_authentication),
            ("Endpoint Existence", self.test_endpoint_existence),
            ("Valid Upload", self.test_valid_upload),
            ("Invalid File Types", self.test_invalid_file_types),
            ("Large File Rejection", self.test_large_file_rejection),
            ("No Files Error", self.test_no_files_error),
            ("Uploads Directory", self.test_uploads_directory)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"   ❌ Test {test_name} failed with exception: {e}")
                results.append((test_name, False))
        
        # Print summary
        print(f"\n{'='*20} TEST SUMMARY {'='*20}")
        print(f"📊 Total Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        print(f"\n📋 DETAILED RESULTS:")
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status} {test_name}")
        
        # Final verdict
        if self.tests_passed == self.tests_run:
            print(f"\n🎉 ALL TESTS PASSED! Batch upload endpoint is working correctly.")
        else:
            print(f"\n⚠️ SOME TESTS FAILED. Check the results above for details.")
        
        return results

if __name__ == "__main__":
    tester = BatchUploadTester()
    tester.run_all_tests()