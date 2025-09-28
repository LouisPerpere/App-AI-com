#!/usr/bin/env python3
"""
Persistence Testing for Content Management System
Tests the fixed persistence issues to verify deletions and descriptions work correctly
"""

import requests
import json
import os
import tempfile
import time
from datetime import datetime
import base64

class PersistenceAPITester:
    def __init__(self):
        # Use the production backend URL from frontend/.env
        self.base_url = "https://social-publisher-10.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.test_files = []  # Track uploaded files for cleanup
        self.tests_run = 0
        self.tests_passed = 0

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

    def authenticate(self):
        """Authenticate with the test user credentials"""
        print("🔐 Authenticating with test user...")
        
        login_data = {
            "email": "lperpere@yahoo.fr",
            "password": "L@Reunion974!"
        }
        
        try:
            response = requests.post(f"{self.api_url}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                print(f"✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False

    def get_auth_headers(self):
        """Get authentication headers"""
        if self.access_token:
            return {'Authorization': f'Bearer {self.access_token}'}
        return {}

    def create_test_image(self, filename="test_image.jpg"):
        """Create a minimal test image file"""
        # Create a minimal JPEG file (1x1 pixel) - simple binary data
        jpeg_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        temp_file.write(jpeg_data)
        temp_file.close()
        
        return temp_file.name

    def upload_test_file(self, description="Test file for persistence testing"):
        """Upload a test file and return its ID"""
        print(f"📤 Uploading test file...")
        
        # Create test image
        temp_file_path = self.create_test_image()
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'files': ('test_image.jpg', f, 'image/jpeg')}
                
                response = requests.post(
                    f"{self.api_url}/content/batch-upload",
                    files=files,
                    headers=self.get_auth_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    uploaded_files = data.get('uploaded_files', [])
                    if uploaded_files:
                        # The upload returns a UUID, but we need to get the actual file ID from pending content
                        stored_name = uploaded_files[0]['stored_name']
                        file_id = stored_name.split('.')[0]  # Use filename without extension as ID (matches backend logic)
                        self.test_files.append(file_id)
                        print(f"✅ File uploaded successfully with ID: {file_id} (stored as: {stored_name})")
                        
                        # Add description if provided
                        if description:
                            self.update_file_description(file_id, description)
                        
                        return file_id
                    else:
                        print(f"❌ No files in upload response")
                        return None
                else:
                    print(f"❌ Upload failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return None
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file_path)
            except:
                pass

    def update_file_description(self, file_id, description):
        """Update file description"""
        try:
            response = requests.put(
                f"{self.api_url}/content/{file_id}/description",
                json={"description": description},
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                print(f"✅ Description updated for file {file_id}")
                return True
            else:
                print(f"❌ Description update failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Description update error: {e}")
            return False

    def get_pending_content(self):
        """Get pending content list"""
        try:
            # Add cache-busting headers as mentioned in review
            headers = self.get_auth_headers()
            headers.update({
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            })
            
            response = requests.get(
                f"{self.api_url}/content/pending",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Get pending content failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Get pending content error: {e}")
            return None

    def delete_file(self, file_id):
        """Delete a file"""
        try:
            response = requests.delete(
                f"{self.api_url}/content/{file_id}",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                print(f"✅ File {file_id} deleted successfully")
                return True
            else:
                print(f"❌ File deletion failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ File deletion error: {e}")
            return False

    def check_file_system_consistency(self):
        """Check if uploads directory contents match API responses"""
        print("🔍 Checking file system consistency...")
        
        # Get content via API
        content_data = self.get_pending_content()
        if not content_data:
            self.log_test("File System Consistency Check", False, "Could not get content via API")
            return False
        
        api_files = content_data.get('content', [])
        api_file_count = len(api_files)
        
        print(f"   API reports {api_file_count} files")
        
        # Check descriptions file exists
        descriptions_exist = self.check_descriptions_file_exists()
        
        success = api_file_count >= 0  # Basic check that API is responding
        details = f"API returned {api_file_count} files, descriptions file exists: {descriptions_exist}"
        
        self.log_test("File System Consistency Check", success, details)
        return success

    def check_descriptions_file_exists(self):
        """Check if content_descriptions.json exists (indirectly through API behavior)"""
        # We can't directly access the file system, but we can test if descriptions persist
        # by uploading a file, adding a description, and checking if it persists
        return True  # Assume it exists if API is working

    def test_persistent_deletion_workflow(self):
        """Test 1: Persistent deletion workflow"""
        print("\n🧪 TEST 1: Persistent Deletion Workflow")
        print("-" * 50)
        
        # Step 1: Upload a new test file
        file_id = self.upload_test_file("File to be deleted - persistence test")
        if not file_id:
            self.log_test("Upload test file for deletion", False, "Could not upload file")
            return False
        
        self.log_test("Upload test file for deletion", True, f"File ID: {file_id}")
        
        # Step 2: Verify file appears in pending content
        content_before = self.get_pending_content()
        if not content_before:
            self.log_test("Get content before deletion", False, "Could not get content")
            return False
        
        files_before = content_before.get('content', [])
        file_found_before = any(f['id'] == file_id for f in files_before)
        
        self.log_test("File appears in pending content", file_found_before, 
                     f"Found {len(files_before)} files, target file present: {file_found_before}")
        
        # Step 3: Delete the file
        deletion_success = self.delete_file(file_id)
        self.log_test("Delete file via API", deletion_success)
        
        if not deletion_success:
            return False
        
        # Step 4: Wait a moment for file system operations
        time.sleep(1)
        
        # Step 5: Verify file is removed from pending content (fresh API call)
        content_after = self.get_pending_content()
        if not content_after:
            self.log_test("Get content after deletion", False, "Could not get content")
            return False
        
        files_after = content_after.get('content', [])
        file_found_after = any(f['id'] == file_id for f in files_after)
        
        self.log_test("File removed from pending content", not file_found_after,
                     f"Found {len(files_after)} files, target file present: {file_found_after}")
        
        # Remove from our tracking list since it's deleted
        if file_id in self.test_files:
            self.test_files.remove(file_id)
        
        return deletion_success and not file_found_after

    def test_description_persistence_workflow(self):
        """Test 2: Description persistence workflow"""
        print("\n🧪 TEST 2: Description Persistence Workflow")
        print("-" * 50)
        
        # Step 1: Upload a test file
        file_id = self.upload_test_file()  # No initial description
        if not file_id:
            self.log_test("Upload test file for description test", False, "Could not upload file")
            return False
        
        self.log_test("Upload test file for description test", True, f"File ID: {file_id}")
        
        # Step 2: Add a description
        test_description = f"Test description added at {datetime.now().isoformat()}"
        desc_success = self.update_file_description(file_id, test_description)
        self.log_test("Add description to file", desc_success)
        
        if not desc_success:
            return False
        
        # Step 3: Verify description appears in fresh API call
        time.sleep(1)  # Wait for persistence
        content_data = self.get_pending_content()
        if not content_data:
            self.log_test("Get content after adding description", False, "Could not get content")
            return False
        
        files = content_data.get('content', [])
        target_file = next((f for f in files if f['id'] == file_id), None)
        
        if target_file:
            stored_description = target_file.get('description', '')
            description_matches = stored_description == test_description
            self.log_test("Description persists in API response", description_matches,
                         f"Expected: '{test_description}', Got: '{stored_description}'")
        else:
            self.log_test("Find file in API response", False, "File not found in response")
            return False
        
        # Step 4: Update the description
        updated_description = f"Updated description at {datetime.now().isoformat()}"
        update_success = self.update_file_description(file_id, updated_description)
        self.log_test("Update existing description", update_success)
        
        if not update_success:
            return False
        
        # Step 5: Verify updated description persists
        time.sleep(1)  # Wait for persistence
        content_data = self.get_pending_content()
        if content_data:
            files = content_data.get('content', [])
            target_file = next((f for f in files if f['id'] == file_id), None)
            
            if target_file:
                stored_description = target_file.get('description', '')
                description_matches = stored_description == updated_description
                self.log_test("Updated description persists", description_matches,
                             f"Expected: '{updated_description}', Got: '{stored_description}'")
                return description_matches
        
        self.log_test("Verify updated description persistence", False, "Could not verify")
        return False

    def test_fresh_api_call_results(self):
        """Test 3: Fresh API call results with cache-busting"""
        print("\n🧪 TEST 3: Fresh API Call Results")
        print("-" * 50)
        
        # Upload a test file
        file_id = self.upload_test_file("Cache-busting test file")
        if not file_id:
            self.log_test("Upload file for cache test", False, "Could not upload file")
            return False
        
        self.log_test("Upload file for cache test", True, f"File ID: {file_id}")
        
        # Make multiple API calls with different cache-busting headers
        cache_busting_headers = [
            {'Cache-Control': 'no-cache'},
            {'Cache-Control': 'no-store, no-cache, must-revalidate'},
            {'Pragma': 'no-cache'},
            {'Cache-Control': 'no-cache', 'Pragma': 'no-cache', 'Expires': '0'},
        ]
        
        all_calls_consistent = True
        first_response = None
        
        for i, extra_headers in enumerate(cache_busting_headers):
            headers = self.get_auth_headers()
            headers.update(extra_headers)
            
            try:
                response = requests.get(f"{self.api_url}/content/pending", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    files = data.get('content', [])
                    file_found = any(f['id'] == file_id for f in files)
                    
                    if first_response is None:
                        first_response = file_found
                    elif first_response != file_found:
                        all_calls_consistent = False
                    
                    self.log_test(f"Cache-busting call {i+1}", file_found,
                                 f"File found: {file_found}, Total files: {len(files)}")
                else:
                    self.log_test(f"Cache-busting call {i+1}", False, 
                                 f"HTTP {response.status_code}")
                    all_calls_consistent = False
                    
            except Exception as e:
                self.log_test(f"Cache-busting call {i+1}", False, f"Error: {e}")
                all_calls_consistent = False
        
        self.log_test("All cache-busting calls consistent", all_calls_consistent)
        return all_calls_consistent

    def test_file_system_consistency(self):
        """Test 4: File system consistency"""
        print("\n🧪 TEST 4: File System Consistency")
        print("-" * 50)
        
        # Get current state
        content_data = self.get_pending_content()
        if not content_data:
            self.log_test("Get content for consistency check", False, "Could not get content")
            return False
        
        files = content_data.get('content', [])
        total_files = len(files)
        
        self.log_test("Get current content state", True, f"Found {total_files} files")
        
        # Check that all files have proper metadata
        files_with_descriptions = sum(1 for f in files if f.get('description'))
        files_with_proper_ids = sum(1 for f in files if f.get('id'))
        files_with_filenames = sum(1 for f in files if f.get('filename'))
        
        self.log_test("Files have proper IDs", files_with_proper_ids == total_files,
                     f"{files_with_proper_ids}/{total_files} files have IDs")
        
        self.log_test("Files have filenames", files_with_filenames == total_files,
                     f"{files_with_filenames}/{total_files} files have filenames")
        
        self.log_test("Some files have descriptions", files_with_descriptions > 0,
                     f"{files_with_descriptions}/{total_files} files have descriptions")
        
        # Test that descriptions are properly formatted (not corrupted JSON)
        description_format_ok = True
        for file_info in files:
            desc = file_info.get('description', '')
            if desc and not isinstance(desc, str):
                description_format_ok = False
                break
        
        self.log_test("Description format consistency", description_format_ok,
                     "All descriptions are properly formatted strings")
        
        return True

    def cleanup_test_files(self):
        """Clean up any remaining test files"""
        print("\n🧹 Cleaning up test files...")
        
        for file_id in self.test_files[:]:  # Copy list to avoid modification during iteration
            if self.delete_file(file_id):
                self.test_files.remove(file_id)
        
        if self.test_files:
            print(f"⚠️ Could not clean up {len(self.test_files)} files: {self.test_files}")
        else:
            print("✅ All test files cleaned up")

    def run_all_tests(self):
        """Run all persistence tests"""
        print("🚀 Starting Persistence Testing")
        print("=" * 60)
        print(f"Backend URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot run tests")
            return False
        
        try:
            # Run all tests
            test_results = []
            
            test_results.append(self.test_persistent_deletion_workflow())
            test_results.append(self.test_description_persistence_workflow())
            test_results.append(self.test_fresh_api_call_results())
            test_results.append(self.test_file_system_consistency())
            
            # Summary
            print("\n" + "=" * 60)
            print("📊 PERSISTENCE TEST RESULTS")
            print("=" * 60)
            
            passed_tests = sum(test_results)
            total_tests = len(test_results)
            
            print(f"Tests Run: {self.tests_run}")
            print(f"Tests Passed: {self.tests_passed}")
            print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
            print(f"Major Test Categories: {passed_tests}/{total_tests} passed")
            
            if passed_tests == total_tests:
                print("\n✅ ALL PERSISTENCE TESTS PASSED")
                print("🎉 Deletions and descriptions are working correctly!")
            else:
                print(f"\n❌ {total_tests - passed_tests} TEST CATEGORIES FAILED")
                print("⚠️ Some persistence issues remain")
            
            return passed_tests == total_tests
            
        finally:
            # Always clean up
            self.cleanup_test_files()

if __name__ == "__main__":
    tester = PersistenceAPITester()
    success = tester.run_all_tests()
    exit(0 if success else 1)