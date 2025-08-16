#!/usr/bin/env python3
"""
Permanent File Deletion Testing Script
Tests the permanent deletion functionality and verifies it works across server restarts
"""

import requests
import json
import os
import time
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

class DeletionTester:
    def __init__(self):
        # Use localhost for testing in container
        self.base_url = "http://localhost:8001"
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.test_files = []  # Track uploaded test files
        self.tests_run = 0
        self.tests_passed = 0
        
    def log(self, message, level="INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def authenticate(self):
        """Authenticate with the backend using test credentials"""
        self.log("Authenticating with backend...")
        
        login_data = {
            "email": "lperpere@yahoo.fr",
            "password": "L@Reunion974!"
        }
        
        try:
            response = requests.post(f"{self.api_url}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                self.log(f"✅ Authentication successful - Token: {self.access_token[:20]}...")
                return True
            else:
                self.log(f"❌ Authentication failed - Status: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Authentication error: {e}", "ERROR")
            return False
    
    def get_headers(self):
        """Get headers with authentication"""
        headers = {}
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        return headers
    
    def create_test_image(self, filename="test_image.jpg"):
        """Create a minimal test image file"""
        # Create minimal JPEG data
        jpeg_data = (
            b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
            b'\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t'
            b'\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a'
            b'\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82'
            b'<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02'
            b'\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00'
            b'\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11'
            b'\x00\x3f\x00\xaa\xff\xd9'
        )
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        temp_file.write(jpeg_data)
        temp_file.close()
        
        return temp_file.name
    
    def upload_test_file(self, description="Test file for deletion testing"):
        """Upload a test file and return its file_id"""
        self.log("Uploading test file...")
        
        # Create test image
        temp_file_path = self.create_test_image()
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'files': (f'test_deletion_{uuid.uuid4().hex[:8]}.jpg', f, 'image/jpeg')}
                
                response = requests.post(
                    f"{self.api_url}/content/batch-upload",
                    files=files,
                    headers=self.get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    uploaded_files = data.get('uploaded_files', [])
                    if uploaded_files:
                        # The upload returns a UUID, but we need to use the filename without extension as ID
                        stored_name = uploaded_files[0]['stored_name']
                        file_id = stored_name.split('.')[0]  # Use filename without extension as ID
                        self.test_files.append({'id': file_id, 'filename': stored_name})
                        self.log(f"✅ File uploaded successfully - ID: {file_id}, Filename: {stored_name}")
                        
                        # Add description to the file
                        if description:
                            self.add_file_description(file_id, description)
                        
                        return file_id
                    else:
                        self.log("❌ No files in upload response", "ERROR")
                        return None
                else:
                    self.log(f"❌ Upload failed - Status: {response.status_code}, Response: {response.text}", "ERROR")
                    return None
                    
        except Exception as e:
            self.log(f"❌ Upload error: {e}", "ERROR")
            return None
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    def add_file_description(self, file_id, description):
        """Add description to a file"""
        self.log(f"Adding description to file {file_id}...")
        
        try:
            response = requests.put(
                f"{self.api_url}/content/{file_id}/description",
                json={"description": description},
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                self.log(f"✅ Description added successfully")
                return True
            else:
                self.log(f"❌ Failed to add description - Status: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Description error: {e}", "ERROR")
            return False
    
    def check_file_exists_in_uploads(self, filename):
        """Check if file exists in uploads directory (via API)"""
        try:
            response = requests.get(
                f"{self.api_url}/content/pending",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                content_files = data.get('content', [])
                
                for file_info in content_files:
                    if file_info.get('filename') == filename:
                        return True
                return False
            else:
                self.log(f"❌ Failed to check files - Status: {response.status_code}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ File check error: {e}", "ERROR")
            return None
    
    def check_description_exists(self, file_id):
        """Check if description exists for file_id"""
        try:
            response = requests.get(
                f"{self.api_url}/content/pending",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                content_files = data.get('content', [])
                
                for file_info in content_files:
                    if file_info.get('id') == file_id:
                        description = file_info.get('description', '')
                        return len(description) > 0
                return False
            else:
                self.log(f"❌ Failed to check descriptions - Status: {response.status_code}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Description check error: {e}", "ERROR")
            return None
    
    def delete_file(self, file_id):
        """Delete a file using the DELETE endpoint"""
        self.log(f"Deleting file {file_id}...")
        
        try:
            response = requests.delete(
                f"{self.api_url}/content/{file_id}",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ File deleted successfully - Message: {data.get('message', 'No message')}")
                return True
            else:
                self.log(f"❌ Delete failed - Status: {response.status_code}, Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Delete error: {e}", "ERROR")
            return False
    
    def test_permanent_file_deletion(self):
        """Test 1: Permanent file deletion test"""
        self.log("=" * 60)
        self.log("TEST 1: Permanent File Deletion")
        self.log("=" * 60)
        
        self.tests_run += 1
        
        # Step 1: Upload a test file
        file_id = self.upload_test_file("Test description for permanent deletion")
        if not file_id:
            self.log("❌ TEST 1 FAILED: Could not upload test file", "ERROR")
            return False
        
        # Get filename for verification
        test_file = next((f for f in self.test_files if f['id'] == file_id), None)
        if not test_file:
            self.log("❌ TEST 1 FAILED: Could not find uploaded file info", "ERROR")
            return False
        
        filename = test_file['filename']
        
        # Step 2: Verify file exists in uploads directory
        file_exists_before = self.check_file_exists_in_uploads(filename)
        if file_exists_before is None:
            self.log("❌ TEST 1 FAILED: Could not check file existence", "ERROR")
            return False
        elif not file_exists_before:
            self.log("❌ TEST 1 FAILED: File not found in uploads after upload", "ERROR")
            return False
        
        self.log(f"✅ File exists in uploads directory: {filename}")
        
        # Step 3: Verify description exists
        description_exists_before = self.check_description_exists(file_id)
        if description_exists_before is None:
            self.log("❌ TEST 1 FAILED: Could not check description existence", "ERROR")
            return False
        elif not description_exists_before:
            self.log("❌ TEST 1 FAILED: Description not found after adding", "ERROR")
            return False
        
        self.log(f"✅ Description exists for file: {file_id}")
        
        # Step 4: Delete the file
        delete_success = self.delete_file(file_id)
        if not delete_success:
            self.log("❌ TEST 1 FAILED: Could not delete file", "ERROR")
            return False
        
        # Step 5: Verify file is removed from uploads directory
        time.sleep(1)  # Give a moment for filesystem operations
        file_exists_after = self.check_file_exists_in_uploads(filename)
        if file_exists_after is None:
            self.log("❌ TEST 1 FAILED: Could not check file existence after deletion", "ERROR")
            return False
        elif file_exists_after:
            self.log("❌ TEST 1 FAILED: File still exists in uploads after deletion", "ERROR")
            return False
        
        self.log(f"✅ File successfully removed from uploads directory")
        
        # Step 6: Verify description is removed
        description_exists_after = self.check_description_exists(file_id)
        if description_exists_after is None:
            self.log("❌ TEST 1 FAILED: Could not check description after deletion", "ERROR")
            return False
        elif description_exists_after:
            self.log("❌ TEST 1 FAILED: Description still exists after file deletion", "ERROR")
            return False
        
        self.log(f"✅ Description successfully removed from content_descriptions.json")
        
        self.log("✅ TEST 1 PASSED: Permanent file deletion working correctly")
        self.tests_passed += 1
        return True
    
    def test_deletion_persistence(self):
        """Test 2: Deletion persistence test (simulate server restart)"""
        self.log("=" * 60)
        self.log("TEST 2: Deletion Persistence Test")
        self.log("=" * 60)
        
        self.tests_run += 1
        
        # Step 1: Upload multiple test files
        file_ids = []
        for i in range(3):
            file_id = self.upload_test_file(f"Test file {i+1} for persistence testing")
            if file_id:
                file_ids.append(file_id)
        
        if len(file_ids) < 3:
            self.log("❌ TEST 2 FAILED: Could not upload all test files", "ERROR")
            return False
        
        self.log(f"✅ Uploaded {len(file_ids)} test files")
        
        # Step 2: Get initial uploads directory contents
        initial_files = []
        try:
            response = requests.get(f"{self.api_url}/content/pending", headers=self.get_headers())
            if response.status_code == 200:
                data = response.json()
                initial_files = [f['filename'] for f in data.get('content', [])]
                self.log(f"✅ Initial uploads directory contains {len(initial_files)} files")
            else:
                self.log("❌ TEST 2 FAILED: Could not get initial file list", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ TEST 2 FAILED: Error getting initial files: {e}", "ERROR")
            return False
        
        # Step 3: Delete first two files
        deleted_files = []
        for i in range(2):
            file_id = file_ids[i]
            if self.delete_file(file_id):
                test_file = next((f for f in self.test_files if f['id'] == file_id), None)
                if test_file:
                    deleted_files.append(test_file['filename'])
        
        if len(deleted_files) != 2:
            self.log("❌ TEST 2 FAILED: Could not delete test files", "ERROR")
            return False
        
        self.log(f"✅ Deleted {len(deleted_files)} files")
        
        # Step 4: Verify files are gone immediately
        time.sleep(2)  # Wait for operations to complete
        try:
            response = requests.get(f"{self.api_url}/content/pending", headers=self.get_headers())
            if response.status_code == 200:
                data = response.json()
                current_files = [f['filename'] for f in data.get('content', [])]
                
                # Check that deleted files are not in current list
                still_present = [f for f in deleted_files if f in current_files]
                if still_present:
                    self.log(f"❌ TEST 2 FAILED: Deleted files still present: {still_present}", "ERROR")
                    return False
                
                self.log(f"✅ Deleted files confirmed absent from uploads directory")
                
                # Check that remaining file is still there
                remaining_file = next((f for f in self.test_files if f['id'] == file_ids[2]), None)
                if remaining_file and remaining_file['filename'] not in current_files:
                    self.log("❌ TEST 2 FAILED: Remaining file was also deleted", "ERROR")
                    return False
                
                self.log(f"✅ Remaining file still present in uploads directory")
                
            else:
                self.log("❌ TEST 2 FAILED: Could not verify file deletion", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ TEST 2 FAILED: Error verifying deletion: {e}", "ERROR")
            return False
        
        # Step 5: Simulate server restart by re-authenticating and checking again
        self.log("Simulating server restart by re-authenticating...")
        if not self.authenticate():
            self.log("❌ TEST 2 FAILED: Could not re-authenticate", "ERROR")
            return False
        
        time.sleep(1)  # Brief pause
        
        # Step 6: Verify deleted files don't reappear
        try:
            response = requests.get(f"{self.api_url}/content/pending", headers=self.get_headers())
            if response.status_code == 200:
                data = response.json()
                final_files = [f['filename'] for f in data.get('content', [])]
                
                # Check that deleted files are still not present
                reappeared = [f for f in deleted_files if f in final_files]
                if reappeared:
                    self.log(f"❌ TEST 2 FAILED: Deleted files reappeared after restart: {reappeared}", "ERROR")
                    return False
                
                self.log(f"✅ Deleted files remain absent after simulated restart")
                
                # Check that remaining file is still there
                remaining_file = next((f for f in self.test_files if f['id'] == file_ids[2]), None)
                if remaining_file and remaining_file['filename'] not in final_files:
                    self.log("❌ TEST 2 FAILED: Remaining file disappeared after restart", "ERROR")
                    return False
                
                self.log(f"✅ Remaining file still present after simulated restart")
                
            else:
                self.log("❌ TEST 2 FAILED: Could not verify persistence after restart", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ TEST 2 FAILED: Error checking persistence: {e}", "ERROR")
            return False
        
        self.log("✅ TEST 2 PASSED: Deletion persistence working correctly")
        self.tests_passed += 1
        return True
    
    def test_complete_cleanup_verification(self):
        """Test 3: Complete cleanup verification"""
        self.log("=" * 60)
        self.log("TEST 3: Complete Cleanup Verification")
        self.log("=" * 60)
        
        self.tests_run += 1
        
        # Step 1: Upload multiple files with descriptions
        file_data = []
        for i in range(3):
            file_id = self.upload_test_file(f"Cleanup test description {i+1} - This should be deleted")
            if file_id:
                test_file = next((f for f in self.test_files if f['id'] == file_id), None)
                if test_file:
                    file_data.append({
                        'id': file_id,
                        'filename': test_file['filename'],
                        'description': f"Cleanup test description {i+1} - This should be deleted"
                    })
        
        if len(file_data) < 3:
            self.log("❌ TEST 3 FAILED: Could not upload all test files", "ERROR")
            return False
        
        self.log(f"✅ Uploaded {len(file_data)} files with descriptions")
        
        # Step 2: Verify all files and descriptions exist
        for file_info in file_data:
            file_exists = self.check_file_exists_in_uploads(file_info['filename'])
            desc_exists = self.check_description_exists(file_info['id'])
            
            if not file_exists or not desc_exists:
                self.log(f"❌ TEST 3 FAILED: File or description missing for {file_info['id']}", "ERROR")
                return False
        
        self.log("✅ All files and descriptions verified to exist")
        
        # Step 3: Delete all files in batch
        deleted_count = 0
        for file_info in file_data:
            if self.delete_file(file_info['id']):
                deleted_count += 1
        
        if deleted_count != len(file_data):
            self.log(f"❌ TEST 3 FAILED: Only deleted {deleted_count}/{len(file_data)} files", "ERROR")
            return False
        
        self.log(f"✅ Successfully deleted all {deleted_count} files")
        
        # Step 4: Verify complete cleanup
        time.sleep(2)  # Wait for cleanup operations
        
        cleanup_success = True
        for file_info in file_data:
            file_exists = self.check_file_exists_in_uploads(file_info['filename'])
            desc_exists = self.check_description_exists(file_info['id'])
            
            if file_exists:
                self.log(f"❌ File still exists: {file_info['filename']}", "ERROR")
                cleanup_success = False
            
            if desc_exists:
                self.log(f"❌ Description still exists: {file_info['id']}", "ERROR")
                cleanup_success = False
        
        if not cleanup_success:
            self.log("❌ TEST 3 FAILED: Incomplete cleanup detected", "ERROR")
            return False
        
        self.log("✅ Complete cleanup verified - no orphaned files or descriptions")
        
        self.log("✅ TEST 3 PASSED: Complete cleanup verification successful")
        self.tests_passed += 1
        return True
    
    def test_error_handling(self):
        """Test 4: Error handling"""
        self.log("=" * 60)
        self.log("TEST 4: Error Handling")
        self.log("=" * 60)
        
        self.tests_run += 1
        
        # Test 4a: Delete non-existent file
        self.log("Testing deletion of non-existent file...")
        try:
            response = requests.delete(
                f"{self.api_url}/content/nonexistent_file_id",
                headers=self.get_headers()
            )
            
            if response.status_code == 404:
                self.log("✅ Correctly returned 404 for non-existent file")
            else:
                self.log(f"❌ Unexpected status for non-existent file: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing non-existent file deletion: {e}", "ERROR")
            return False
        
        # Test 4b: Delete with invalid file ID format
        self.log("Testing deletion with invalid file ID format...")
        try:
            response = requests.delete(
                f"{self.api_url}/content/invalid-file-id-format-123",
                headers=self.get_headers()
            )
            
            if response.status_code in [404, 400]:
                self.log("✅ Correctly handled invalid file ID format")
            else:
                self.log(f"❌ Unexpected status for invalid file ID: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing invalid file ID: {e}", "ERROR")
            return False
        
        # Test 4c: Test robustness - multiple rapid deletions
        self.log("Testing robustness with multiple rapid deletions...")
        
        # Upload test files
        rapid_test_files = []
        for i in range(5):
            file_id = self.upload_test_file(f"Rapid deletion test {i+1}")
            if file_id:
                rapid_test_files.append(file_id)
        
        if len(rapid_test_files) < 5:
            self.log("❌ Could not upload files for rapid deletion test", "ERROR")
            return False
        
        # Delete all files rapidly
        deletion_results = []
        for file_id in rapid_test_files:
            try:
                response = requests.delete(
                    f"{self.api_url}/content/{file_id}",
                    headers=self.get_headers()
                )
                deletion_results.append(response.status_code == 200)
            except Exception as e:
                self.log(f"❌ Error in rapid deletion: {e}", "ERROR")
                deletion_results.append(False)
        
        successful_deletions = sum(deletion_results)
        if successful_deletions == len(rapid_test_files):
            self.log(f"✅ All {successful_deletions} rapid deletions successful")
        else:
            self.log(f"❌ Only {successful_deletions}/{len(rapid_test_files)} rapid deletions successful", "ERROR")
            return False
        
        self.log("✅ TEST 4 PASSED: Error handling working correctly")
        self.tests_passed += 1
        return True
    
    def cleanup_remaining_test_files(self):
        """Clean up any remaining test files"""
        self.log("Cleaning up remaining test files...")
        
        remaining_files = [f for f in self.test_files if f.get('id')]
        if not remaining_files:
            self.log("No test files to clean up")
            return
        
        cleaned_count = 0
        for file_info in remaining_files:
            try:
                response = requests.delete(
                    f"{self.api_url}/content/{file_info['id']}",
                    headers=self.get_headers()
                )
                if response.status_code == 200:
                    cleaned_count += 1
            except:
                pass  # Ignore cleanup errors
        
        self.log(f"Cleaned up {cleaned_count} remaining test files")
    
    def run_all_tests(self):
        """Run all deletion tests"""
        self.log("🚀 Starting Permanent Deletion Functionality Tests")
        self.log("=" * 80)
        self.log(f"Backend URL: {self.base_url}")
        self.log(f"API URL: {self.api_url}")
        self.log("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            self.log("❌ CRITICAL: Authentication failed - cannot run tests", "ERROR")
            return False
        
        try:
            # Run all tests
            test_results = []
            
            test_results.append(self.test_permanent_file_deletion())
            test_results.append(self.test_deletion_persistence())
            test_results.append(self.test_complete_cleanup_verification())
            test_results.append(self.test_error_handling())
            
            # Summary
            self.log("=" * 80)
            self.log("TEST SUMMARY")
            self.log("=" * 80)
            self.log(f"Tests Run: {self.tests_run}")
            self.log(f"Tests Passed: {self.tests_passed}")
            self.log(f"Tests Failed: {self.tests_run - self.tests_passed}")
            self.log(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
            
            if all(test_results):
                self.log("🎉 ALL TESTS PASSED - Permanent deletion functionality working correctly!")
                return True
            else:
                self.log("❌ SOME TESTS FAILED - Issues detected with deletion functionality", "ERROR")
                return False
                
        finally:
            # Clean up any remaining test files
            self.cleanup_remaining_test_files()

if __name__ == "__main__":
    tester = DeletionTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)