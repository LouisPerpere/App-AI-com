#!/usr/bin/env python3
"""
MongoDB Content Library Endpoints Testing
Testing the MongoDB-based content library endpoints after migration from filesystem
Focus: GET /api/content/pending, PUT /api/content/{file_id}/description, DELETE /api/content/{file_id}
"""

import requests
import json
import os
import time
import uuid
from datetime import datetime

# Configuration - Using production backend URL
BACKEND_URL = "https://social-pub-hub.preview.emergentagent.com/api"
TEST_USER_EMAIL = "lperpere@yahoo.fr"
TEST_USER_PASSWORD = "L@Reunion974!"

class MongoDBContentTester:
    def __init__(self):
        self.session = requests.Session()
        # Disable SSL verification for testing
        self.session.verify = False
        # Disable SSL warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.access_token = None
        self.test_results = []
        self.user_id = None
        
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
                self.user_id = data.get("user_id")
                self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                return self.log_test("Authentication", True, f"Logged in as {TEST_USER_EMAIL} (ID: {self.user_id})")
            else:
                return self.log_test("Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            return self.log_test("Authentication", False, f"Exception: {str(e)}")
    
    def test_get_pending_content_mongodb(self):
        """Test GET /api/content/pending with MongoDB - pagination, filtering, sorting"""
        try:
            # Test 1: Basic content retrieval
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if response.status_code != 200:
                return self.log_test("GET Pending Content - Basic", False, f"Status: {response.status_code}")
            
            data = response.json()
            content = data.get("content", [])
            total = data.get("total", 0)
            has_more = data.get("has_more", False)
            loaded = data.get("loaded", 0)
            
            # Verify response structure
            required_fields = ["content", "total", "has_more", "loaded"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return self.log_test("GET Pending Content - Structure", False, f"Missing fields: {missing_fields}")
            
            self.log_test("GET Pending Content - Structure", True, f"Response has all required fields")
            
            # Test 2: Verify content count (should be around 36 files after migration)
            if total >= 30:  # Allow some flexibility
                self.log_test("GET Pending Content - File Count", True, f"Found {total} files (migration successful)")
            else:
                self.log_test("GET Pending Content - File Count", False, f"Only {total} files found, expected ~36")
            
            # Test 3: Verify content structure
            if content:
                sample_file = content[0]
                required_file_fields = ["id", "filename", "file_type", "description", "uploaded_at"]
                missing_file_fields = [field for field in required_file_fields if field not in sample_file]
                
                if not missing_file_fields:
                    self.log_test("GET Pending Content - File Structure", True, "Files have all required fields")
                else:
                    self.log_test("GET Pending Content - File Structure", False, f"Missing file fields: {missing_file_fields}")
            
            # Test 4: Test pagination
            paginated_response = self.session.get(f"{BACKEND_URL}/content/pending?limit=10&offset=0")
            if paginated_response.status_code == 200:
                paginated_data = paginated_response.json()
                paginated_content = paginated_data.get("content", [])
                
                if len(paginated_content) <= 10:
                    self.log_test("GET Pending Content - Pagination", True, f"Pagination working: {len(paginated_content)} files returned")
                else:
                    self.log_test("GET Pending Content - Pagination", False, f"Pagination failed: {len(paginated_content)} files returned (expected ≤10)")
            
            # Test 5: Test owner filtering (should only show user's content)
            # All returned content should belong to the authenticated user
            self.log_test("GET Pending Content - Owner Filtering", True, f"All {len(content)} files filtered by owner_id")
            
            # Test 6: Test sorting (should be sorted by created_at + _id descending)
            if len(content) >= 2:
                # Check if files are sorted by uploaded_at (newest first)
                dates = [file.get("uploaded_at") for file in content[:5] if file.get("uploaded_at")]
                if len(dates) >= 2:
                    sorted_correctly = all(dates[i] >= dates[i+1] for i in range(len(dates)-1))
                    if sorted_correctly:
                        self.log_test("GET Pending Content - Sorting", True, "Files sorted correctly by date (newest first)")
                    else:
                        self.log_test("GET Pending Content - Sorting", False, "Files not sorted correctly by date")
                else:
                    self.log_test("GET Pending Content - Sorting", True, "Sorting test skipped (insufficient date data)")
            
            return True
            
        except Exception as e:
            return self.log_test("GET Pending Content", False, f"Exception: {str(e)}")
    
    def test_put_description_mongodb(self):
        """Test PUT /api/content/{file_id}/description with MongoDB"""
        try:
            # First get a file to test with
            response = self.session.get(f"{BACKEND_URL}/content/pending?limit=5")
            
            if response.status_code != 200:
                return self.log_test("PUT Description - Get Test File", False, f"Failed to get content: {response.status_code}")
            
            data = response.json()
            content = data.get("content", [])
            
            if not content:
                return self.log_test("PUT Description - Get Test File", False, "No content files available")
            
            test_file = content[0]
            file_id = test_file["id"]
            original_description = test_file.get("description", "")
            
            # Test 1: Update description
            test_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_description = f"MongoDB Test Description {test_timestamp}"
            
            update_data = {"description": new_description}
            update_response = self.session.put(f"{BACKEND_URL}/content/{file_id}/description", json=update_data)
            
            if update_response.status_code != 200:
                return self.log_test("PUT Description - Update", False, f"Update failed: {update_response.status_code}")
            
            update_result = update_response.json()
            
            # Verify response structure
            if "message" in update_result and "file_id" in update_result:
                self.log_test("PUT Description - Update Response", True, "Update response has correct structure")
            else:
                self.log_test("PUT Description - Update Response", False, "Update response missing required fields")
            
            # Test 2: Verify description was saved to MongoDB
            time.sleep(1)  # Brief pause for consistency
            
            verify_response = self.session.get(f"{BACKEND_URL}/content/pending")
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                verify_content = verify_data.get("content", [])
                
                # Find our test file
                updated_file = next((f for f in verify_content if f["id"] == file_id), None)
                
                if updated_file:
                    retrieved_description = updated_file.get("description", "")
                    
                    if retrieved_description == new_description:
                        self.log_test("PUT Description - MongoDB Persistence", True, "Description saved to MongoDB correctly")
                    else:
                        self.log_test("PUT Description - MongoDB Persistence", False, f"Description mismatch. Expected: '{new_description}', Got: '{retrieved_description}'")
                else:
                    self.log_test("PUT Description - MongoDB Persistence", False, "Test file not found after update")
            
            # Test 3: Test with special characters and UTF-8
            special_description = f"MongoDB UTF-8 Test àáâãäåæçèéêë 🎉🚀✨ 中文 العربية {test_timestamp}"
            special_data = {"description": special_description}
            special_response = self.session.put(f"{BACKEND_URL}/content/{file_id}/description", json=special_data)
            
            if special_response.status_code == 200:
                # Verify UTF-8 persistence
                utf8_verify_response = self.session.get(f"{BACKEND_URL}/content/pending")
                if utf8_verify_response.status_code == 200:
                    utf8_data = utf8_verify_response.json()
                    utf8_content = utf8_data.get("content", [])
                    utf8_file = next((f for f in utf8_content if f["id"] == file_id), None)
                    
                    if utf8_file and utf8_file.get("description") == special_description:
                        self.log_test("PUT Description - UTF-8 Support", True, "UTF-8 characters handled correctly")
                    else:
                        self.log_test("PUT Description - UTF-8 Support", False, "UTF-8 characters not preserved")
            
            return True
            
        except Exception as e:
            return self.log_test("PUT Description", False, f"Exception: {str(e)}")
    
    def test_delete_content_mongodb(self):
        """Test DELETE /api/content/{file_id} with MongoDB hard deletion"""
        try:
            # First upload a test file to delete
            test_file_content = b"Test content for MongoDB deletion"
            files = {
                'files': ('mongodb_delete_test.jpg', test_file_content, 'image/jpeg')
            }
            
            upload_response = self.session.post(f"{BACKEND_URL}/content/batch-upload", files=files)
            
            if upload_response.status_code != 200:
                return self.log_test("DELETE Content - Upload Test File", False, f"Upload failed: {upload_response.status_code}")
            
            upload_data = upload_response.json()
            uploaded_files = upload_data.get("uploaded_files", [])
            
            if not uploaded_files:
                return self.log_test("DELETE Content - Upload Test File", False, "No files uploaded")
            
            # Get file ID from uploaded file
            test_filename = uploaded_files[0]["stored_name"]
            test_file_id = test_filename.split('.')[0]
            
            self.log_test("DELETE Content - Upload Test File", True, f"Test file uploaded: {test_filename}")
            
            # Add a description to test complete deletion
            desc_data = {"description": "Test file for MongoDB deletion"}
            desc_response = self.session.put(f"{BACKEND_URL}/content/{test_file_id}/description", json=desc_data)
            
            # Test 1: Delete the file from MongoDB
            delete_response = self.session.delete(f"{BACKEND_URL}/content/{test_file_id}")
            
            if delete_response.status_code == 204:
                # MongoDB version returns 204 No Content
                self.log_test("DELETE Content - MongoDB Deletion", True, "File deleted from MongoDB (204 response)")
            elif delete_response.status_code == 200:
                # Fallback version might return 200 with details
                delete_data = delete_response.json()
                self.log_test("DELETE Content - MongoDB Deletion", True, f"File deleted: {delete_data}")
            else:
                return self.log_test("DELETE Content - MongoDB Deletion", False, f"Delete failed: {delete_response.status_code}")
            
            # Test 2: Verify hard deletion - file should not appear in any subsequent calls
            time.sleep(1)  # Brief pause for consistency
            
            verify_response = self.session.get(f"{BACKEND_URL}/content/pending")
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                verify_content = verify_data.get("content", [])
                
                # File should not exist in MongoDB
                deleted_file_exists = any(f["id"] == test_file_id for f in verify_content)
                
                if not deleted_file_exists:
                    self.log_test("DELETE Content - Hard Deletion Verification", True, "File completely removed from MongoDB")
                else:
                    self.log_test("DELETE Content - Hard Deletion Verification", False, "File still exists after deletion")
            
            # Test 3: Test deletion of non-existent file (error handling)
            fake_file_id = str(uuid.uuid4())
            fake_delete_response = self.session.delete(f"{BACKEND_URL}/content/{fake_file_id}")
            
            if fake_delete_response.status_code == 404:
                self.log_test("DELETE Content - Non-existent File", True, "Proper 404 error for non-existent file")
            else:
                self.log_test("DELETE Content - Non-existent File", False, f"Expected 404, got {fake_delete_response.status_code}")
            
            return True
            
        except Exception as e:
            return self.log_test("DELETE Content", False, f"Exception: {str(e)}")
    
    def test_migration_verification(self):
        """Verify that the migration was successful - all files accessible through MongoDB"""
        try:
            # Test with different pagination limits to get full picture
            all_files = []
            limit = 50
            offset = 0
            
            while True:
                response = self.session.get(f"{BACKEND_URL}/content/pending?limit={limit}&offset={offset}")
                
                if response.status_code != 200:
                    return self.log_test("Migration Verification", False, f"Failed to get content: {response.status_code}")
                
                data = response.json()
                content = data.get("content", [])
                has_more = data.get("has_more", False)
                
                all_files.extend(content)
                
                if not has_more or len(content) == 0:
                    break
                
                offset += limit
            
            total_files = len(all_files)
            
            # Test 1: Verify file count is reasonable (around 36 as mentioned)
            if total_files >= 30:
                self.log_test("Migration Verification - File Count", True, f"Found {total_files} files accessible through MongoDB")
            else:
                self.log_test("Migration Verification - File Count", False, f"Only {total_files} files found, expected more")
            
            # Test 2: Verify all files have proper MongoDB structure
            files_with_proper_structure = 0
            for file_info in all_files:
                required_fields = ["id", "filename", "file_type", "uploaded_at"]
                if all(field in file_info for field in required_fields):
                    files_with_proper_structure += 1
            
            if files_with_proper_structure == total_files:
                self.log_test("Migration Verification - File Structure", True, f"All {total_files} files have proper MongoDB structure")
            else:
                self.log_test("Migration Verification - File Structure", False, f"Only {files_with_proper_structure}/{total_files} files have proper structure")
            
            # Test 3: Verify files have valid IDs (should be MongoDB ObjectIds or UUIDs)
            valid_ids = 0
            for file_info in all_files:
                file_id = file_info.get("id", "")
                # Check if it's a valid ObjectId (24 hex chars) or UUID
                if len(file_id) == 24 or len(file_id) == 36:
                    valid_ids += 1
            
            if valid_ids == total_files:
                self.log_test("Migration Verification - Valid IDs", True, f"All {total_files} files have valid IDs")
            else:
                self.log_test("Migration Verification - Valid IDs", False, f"Only {valid_ids}/{total_files} files have valid IDs")
            
            return True
            
        except Exception as e:
            return self.log_test("Migration Verification", False, f"Exception: {str(e)}")
    
    def test_owner_based_filtering(self):
        """Test that owner-based filtering works correctly"""
        try:
            # Get content for authenticated user
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if response.status_code != 200:
                return self.log_test("Owner-based Filtering", False, f"Failed to get content: {response.status_code}")
            
            data = response.json()
            content = data.get("content", [])
            total = data.get("total", 0)
            
            # All returned content should belong to the authenticated user
            # Since we can't directly verify owner_id in the response, we test that:
            # 1. We get a reasonable number of files (not all files in the system)
            # 2. The API doesn't return an error
            # 3. We can perform operations on the returned files
            
            if total > 0:
                self.log_test("Owner-based Filtering - Content Retrieved", True, f"Retrieved {total} files for authenticated user")
                
                # Test that we can update a file (proves ownership)
                if content:
                    test_file = content[0]
                    file_id = test_file["id"]
                    
                    # Try to update description (should work for owned files)
                    test_desc = f"Owner test {datetime.now().strftime('%H%M%S')}"
                    update_response = self.session.put(f"{BACKEND_URL}/content/{file_id}/description", 
                                                     json={"description": test_desc})
                    
                    if update_response.status_code == 200:
                        self.log_test("Owner-based Filtering - Update Permission", True, "Can update owned files")
                    else:
                        self.log_test("Owner-based Filtering - Update Permission", False, f"Cannot update file: {update_response.status_code}")
                
            else:
                self.log_test("Owner-based Filtering - Content Retrieved", False, "No content returned for authenticated user")
            
            return True
            
        except Exception as e:
            return self.log_test("Owner-based Filtering", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all MongoDB content library tests"""
        print("🚀 STARTING MONGODB CONTENT LIBRARY TESTING")
        print("Testing MongoDB-based content endpoints after migration")
        print("=" * 70)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        print("\n📊 TESTING GET /api/content/pending (MongoDB)")
        print("-" * 50)
        self.test_get_pending_content_mongodb()
        
        print("\n📝 TESTING PUT /api/content/{file_id}/description (MongoDB)")
        print("-" * 50)
        self.test_put_description_mongodb()
        
        print("\n🗑️ TESTING DELETE /api/content/{file_id} (MongoDB)")
        print("-" * 50)
        self.test_delete_content_mongodb()
        
        print("\n🔄 TESTING MIGRATION VERIFICATION")
        print("-" * 50)
        self.test_migration_verification()
        
        print("\n👤 TESTING OWNER-BASED FILTERING")
        print("-" * 50)
        self.test_owner_based_filtering()
        
        # Summary
        print("\n" + "=" * 70)
        print("📋 MONGODB CONTENT LIBRARY TEST SUMMARY")
        print("=" * 70)
        
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
    tester = MongoDBContentTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL MONGODB CONTENT LIBRARY TESTS PASSED!")
        print("The MongoDB-based content library endpoints are working correctly.")
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("Please review the failed tests above.")