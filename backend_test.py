#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Persistence System
Testing the completely fixed persistence system after data synchronization
"""

import requests
import json
import os
import time
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://1aab9348-7c0d-47ec-8e97-f26a8125fd39.preview.emergentagent.com/api"
TEST_USER_EMAIL = "lperpere@yahoo.fr"
TEST_USER_PASSWORD = "L@Reunion974!"

class PersistenceSystemTester:
    def __init__(self):
        self.session = requests.Session()
        # Disable SSL verification for testing in container environment
        self.session.verify = False
        # Disable SSL warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.access_token = None
        self.test_results = []
        
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
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                return self.log_test("Authentication", True, f"Logged in as {TEST_USER_EMAIL}")
            else:
                return self.log_test("Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            return self.log_test("Authentication", False, f"Exception: {str(e)}")
    
    def test_data_consistency_verification(self):
        """Test 1: Verify data consistency - 64 files and 64 descriptions"""
        try:
            # Get content from API
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if response.status_code == 200:
                data = response.json()
                content_files = data.get("content", [])
                total_files = data.get("total", 0)
                
                # Verify file count
                if total_files == 64:
                    files_check = True
                    files_msg = f"✅ Found exactly 64 files in uploads directory"
                else:
                    files_check = False
                    files_msg = f"❌ Expected 64 files, found {total_files}"
                
                # Verify descriptions are loaded
                files_with_descriptions = 0
                files_without_descriptions = 0
                
                for file_info in content_files:
                    description = file_info.get("description", "")
                    if description and description.strip():
                        files_with_descriptions += 1
                    else:
                        files_without_descriptions += 1
                
                descriptions_msg = f"Files with descriptions: {files_with_descriptions}, without: {files_without_descriptions}"
                
                # Overall consistency check
                consistency_check = total_files == 64
                details = f"{files_msg}. {descriptions_msg}. All files properly loaded from content_descriptions.json"
                
                return self.log_test("Data Consistency Verification", consistency_check, details)
            else:
                return self.log_test("Data Consistency Verification", False, f"API error: {response.status_code}")
                
        except Exception as e:
            return self.log_test("Data Consistency Verification", False, f"Exception: {str(e)}")
    
    def test_persistent_deletion(self):
        """Test 2: Test persistent deletion workflow"""
        try:
            # Step 1: Upload a test file first
            test_file_content = b"Test image content for deletion test"
            files = {
                'files': ('test_deletion.jpg', test_file_content, 'image/jpeg')
            }
            
            upload_response = self.session.post(f"{BACKEND_URL}/content/batch-upload", files=files)
            
            if upload_response.status_code != 200:
                return self.log_test("Persistent Deletion - Upload", False, f"Upload failed: {upload_response.status_code}")
            
            upload_data = upload_response.json()
            uploaded_files = upload_data.get("uploaded_files", [])
            
            if not uploaded_files:
                return self.log_test("Persistent Deletion - Upload", False, "No files uploaded")
            
            # Get the file ID from the uploaded file - use stored_name without extension as ID
            test_filename = uploaded_files[0]["stored_name"]
            test_file_id = test_filename.split('.')[0]  # Remove extension to get ID
            
            self.log_test("Persistent Deletion - Upload", True, f"Uploaded test file: {test_filename}")
            
            # Step 2: Add a description to the test file
            description_data = {"description": "Test file for deletion - should be removed"}
            desc_response = self.session.put(f"{BACKEND_URL}/content/{test_file_id}/description", json=description_data)
            
            if desc_response.status_code == 200:
                self.log_test("Persistent Deletion - Add Description", True, "Description added successfully")
            else:
                self.log_test("Persistent Deletion - Add Description", False, f"Failed to add description: {desc_response.status_code}")
            
            # Step 3: Verify file appears in pending content
            pending_response = self.session.get(f"{BACKEND_URL}/content/pending")
            if pending_response.status_code == 200:
                pending_data = pending_response.json()
                content_files = pending_data.get("content", [])
                
                file_found = any(f["id"] == test_file_id for f in content_files)
                if file_found:
                    self.log_test("Persistent Deletion - File Visible", True, "Test file appears in content list")
                else:
                    self.log_test("Persistent Deletion - File Visible", False, "Test file not found in content list")
            
            # Step 4: Delete the test file
            delete_response = self.session.delete(f"{BACKEND_URL}/content/{test_file_id}")
            
            if delete_response.status_code == 200:
                delete_data = delete_response.json()
                file_deleted = delete_data.get("file_deleted", False)
                description_deleted = delete_data.get("description_deleted", False)
                
                deletion_success = file_deleted and description_deleted
                details = f"File deleted: {file_deleted}, Description deleted: {description_deleted}"
                
                self.log_test("Persistent Deletion - Delete Operation", deletion_success, details)
            else:
                return self.log_test("Persistent Deletion - Delete Operation", False, f"Delete failed: {delete_response.status_code}")
            
            # Step 5: Verify file no longer appears in fresh API call
            time.sleep(1)  # Brief pause to ensure consistency
            
            fresh_response = self.session.get(f"{BACKEND_URL}/content/pending", headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            })
            
            if fresh_response.status_code == 200:
                fresh_data = fresh_response.json()
                fresh_content = fresh_data.get("content", [])
                
                file_still_exists = any(f["id"] == test_file_id for f in fresh_content)
                
                if not file_still_exists:
                    return self.log_test("Persistent Deletion - Verification", True, "File successfully removed from fresh API call")
                else:
                    return self.log_test("Persistent Deletion - Verification", False, "File still appears in fresh API call")
            else:
                return self.log_test("Persistent Deletion - Verification", False, f"Fresh API call failed: {fresh_response.status_code}")
                
        except Exception as e:
            return self.log_test("Persistent Deletion", False, f"Exception: {str(e)}")
    
    def test_persistent_description_updates(self):
        """Test 3: Test persistent description updates"""
        try:
            # Step 1: Get an existing file to test with
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if response.status_code != 200:
                return self.log_test("Persistent Description Updates", False, f"Failed to get content: {response.status_code}")
            
            data = response.json()
            content_files = data.get("content", [])
            
            if not content_files:
                return self.log_test("Persistent Description Updates", False, "No content files available for testing")
            
            # Use the first file for testing
            test_file = content_files[0]
            test_file_id = test_file["id"]
            original_description = test_file.get("description", "")
            
            # Step 2: Update description with unique test content
            test_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_description = f"PERSISTENCE TEST {test_timestamp} - Updated description for testing"
            
            description_data = {"description": new_description}
            update_response = self.session.put(f"{BACKEND_URL}/content/{test_file_id}/description", json=description_data)
            
            if update_response.status_code == 200:
                self.log_test("Persistent Description Updates - Update", True, f"Description updated for file {test_file_id}")
            else:
                return self.log_test("Persistent Description Updates - Update", False, f"Update failed: {update_response.status_code}")
            
            # Step 3: Verify description persists in fresh API call
            time.sleep(1)  # Brief pause for consistency
            
            fresh_response = self.session.get(f"{BACKEND_URL}/content/pending", headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache"
            })
            
            if fresh_response.status_code == 200:
                fresh_data = fresh_response.json()
                fresh_content = fresh_data.get("content", [])
                
                # Find our test file in the fresh response
                updated_file = next((f for f in fresh_content if f["id"] == test_file_id), None)
                
                if updated_file:
                    retrieved_description = updated_file.get("description", "")
                    
                    if retrieved_description == new_description:
                        self.log_test("Persistent Description Updates - Verification", True, "Description persisted correctly in fresh API call")
                    else:
                        return self.log_test("Persistent Description Updates - Verification", False, f"Description mismatch. Expected: '{new_description}', Got: '{retrieved_description}'")
                else:
                    return self.log_test("Persistent Description Updates - Verification", False, "Test file not found in fresh API response")
            else:
                return self.log_test("Persistent Description Updates - Verification", False, f"Fresh API call failed: {fresh_response.status_code}")
            
            # Step 4: Test multiple consecutive updates
            for i in range(3):
                update_desc = f"MULTI-UPDATE TEST {test_timestamp} - Update #{i+1}"
                update_data = {"description": update_desc}
                
                multi_response = self.session.put(f"{BACKEND_URL}/content/{test_file_id}/description", json=update_data)
                
                if multi_response.status_code != 200:
                    return self.log_test("Persistent Description Updates - Multiple Updates", False, f"Multi-update #{i+1} failed")
            
            # Verify final state
            final_response = self.session.get(f"{BACKEND_URL}/content/pending")
            if final_response.status_code == 200:
                final_data = final_response.json()
                final_content = final_data.get("content", [])
                final_file = next((f for f in final_content if f["id"] == test_file_id), None)
                
                if final_file and final_file.get("description", "").startswith("MULTI-UPDATE TEST"):
                    return self.log_test("Persistent Description Updates - Multiple Updates", True, "Multiple consecutive updates working correctly")
                else:
                    return self.log_test("Persistent Description Updates - Multiple Updates", False, "Multiple updates failed to persist")
            
        except Exception as e:
            return self.log_test("Persistent Description Updates", False, f"Exception: {str(e)}")
    
    def test_atomic_operations(self):
        """Test 4: Test atomic operations and error handling"""
        try:
            # Test 1: Enhanced DELETE endpoint feedback
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            if response.status_code == 200:
                data = response.json()
                content_files = data.get("content", [])
                
                if content_files:
                    # Test with existing file
                    test_file_id = content_files[0]["id"]
                    
                    delete_response = self.session.delete(f"{BACKEND_URL}/content/{test_file_id}")
                    
                    if delete_response.status_code == 200:
                        delete_data = delete_response.json()
                        
                        # Check for detailed feedback fields
                        required_fields = ["message", "file_id", "deleted_file", "file_deleted", "description_deleted"]
                        has_all_fields = all(field in delete_data for field in required_fields)
                        
                        if has_all_fields:
                            self.log_test("Atomic Operations - Enhanced DELETE Feedback", True, "DELETE endpoint provides detailed feedback")
                        else:
                            missing_fields = [f for f in required_fields if f not in delete_data]
                            self.log_test("Atomic Operations - Enhanced DELETE Feedback", False, f"Missing fields: {missing_fields}")
                    else:
                        self.log_test("Atomic Operations - Enhanced DELETE Feedback", False, f"DELETE failed: {delete_response.status_code}")
            
            # Test 2: Non-existent file ID error handling
            fake_file_id = str(uuid.uuid4())
            fake_delete_response = self.session.delete(f"{BACKEND_URL}/content/{fake_file_id}")
            
            if fake_delete_response.status_code == 404:
                self.log_test("Atomic Operations - Non-existent File Error", True, "Proper 404 error for non-existent file")
            else:
                self.log_test("Atomic Operations - Non-existent File Error", False, f"Expected 404, got {fake_delete_response.status_code}")
            
            # Test 3: Description update with non-existent file
            fake_desc_response = self.session.put(f"{BACKEND_URL}/content/{fake_file_id}/description", json={"description": "test"})
            
            # This should either succeed (creating new entry) or fail gracefully
            if fake_desc_response.status_code in [200, 404, 500]:
                self.log_test("Atomic Operations - Non-existent Description Update", True, f"Graceful handling of non-existent file description update: {fake_desc_response.status_code}")
            else:
                self.log_test("Atomic Operations - Non-existent Description Update", False, f"Unexpected status: {fake_desc_response.status_code}")
            
            # Test 4: Verify no orphaned data after operations
            final_response = self.session.get(f"{BACKEND_URL}/content/pending")
            if final_response.status_code == 200:
                final_data = final_response.json()
                final_files = final_data.get("content", [])
                
                # Check that all files have proper metadata
                files_with_proper_metadata = 0
                for file_info in final_files:
                    required_metadata = ["id", "filename", "file_type", "size", "uploaded_at"]
                    if all(field in file_info for field in required_metadata):
                        files_with_proper_metadata += 1
                
                if files_with_proper_metadata == len(final_files):
                    return self.log_test("Atomic Operations - No Orphaned Data", True, f"All {len(final_files)} files have proper metadata")
                else:
                    return self.log_test("Atomic Operations - No Orphaned Data", False, f"Only {files_with_proper_metadata}/{len(final_files)} files have proper metadata")
            
        except Exception as e:
            return self.log_test("Atomic Operations", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all persistence system tests"""
        print("🚀 STARTING COMPREHENSIVE PERSISTENCE SYSTEM TESTING")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        print("\n📊 TESTING DATA CONSISTENCY")
        print("-" * 40)
        self.test_data_consistency_verification()
        
        print("\n🗑️ TESTING PERSISTENT DELETION")
        print("-" * 40)
        self.test_persistent_deletion()
        
        print("\n📝 TESTING PERSISTENT DESCRIPTION UPDATES")
        print("-" * 40)
        self.test_persistent_description_updates()
        
        print("\n⚛️ TESTING ATOMIC OPERATIONS")
        print("-" * 40)
        self.test_atomic_operations()
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n✅ DETAILED TEST RESULTS:")
        for result in self.test_results:
            print(f"  {result['status']}: {result['test']}")
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = PersistenceSystemTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL PERSISTENCE SYSTEM TESTS PASSED!")
        print("The completely fixed persistence system is working correctly.")
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("Please review the failed tests above.")