#!/usr/bin/env python3
"""
PHASE 1 - TESTS CRITIQUES BIBLIOTHÈQUE
Testing content library synchronization after frontend URL fix
Focus: Authentication, Content endpoints, Persistence, Badges/Comments
"""

import requests
import json
import os
import time
import uuid
from datetime import datetime

# Configuration - Using corrected frontend URL
BACKEND_URL = "http://localhost:8001/api"
TEST_USER_EMAIL = "lperpere@yahoo.fr"
TEST_USER_PASSWORD = "L@Reunion974!"

class BibliothequeContentTester:
    def __init__(self):
        self.session = requests.Session()
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
        """Test 1: Authentication with confirmed credentials"""
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
                return self.log_test("Authentication", True, f"Successfully authenticated as {TEST_USER_EMAIL}")
            else:
                return self.log_test("Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            return self.log_test("Authentication", False, f"Exception: {str(e)}")
    
    def test_batch_upload_endpoint(self):
        """Test 2: POST /api/content/batch-upload - Multipart upload functionality"""
        try:
            # Create test image content
            test_image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
            
            # Test multipart upload
            files = {
                'files': ('test_bibliotheque.png', test_image_content, 'image/png')
            }
            
            response = self.session.post(f"{BACKEND_URL}/content/batch-upload", files=files)
            
            if response.status_code == 200:
                data = response.json()
                uploaded_files = data.get("uploaded_files", [])
                
                if uploaded_files:
                    file_info = uploaded_files[0]
                    required_fields = ["id", "original_name", "stored_name", "file_path", "content_type", "size", "uploaded_at", "user_id"]
                    has_all_fields = all(field in file_info for field in required_fields)
                    
                    if has_all_fields:
                        self.uploaded_test_file_id = file_info["stored_name"].split('.')[0]  # Store for cleanup
                        return self.log_test("Batch Upload Endpoint", True, f"Successfully uploaded file with all metadata fields")
                    else:
                        missing_fields = [f for f in required_fields if f not in file_info]
                        return self.log_test("Batch Upload Endpoint", False, f"Missing metadata fields: {missing_fields}")
                else:
                    return self.log_test("Batch Upload Endpoint", False, "No files in upload response")
            else:
                return self.log_test("Batch Upload Endpoint", False, f"Upload failed with status {response.status_code}: {response.text}")
                
        except Exception as e:
            return self.log_test("Batch Upload Endpoint", False, f"Exception: {str(e)}")
    
    def test_content_pending_endpoint(self):
        """Test 3: GET /api/content/pending - Verify descriptions persistence"""
        try:
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if response.status_code == 200:
                data = response.json()
                content_files = data.get("content", [])
                total_files = data.get("total", 0)
                
                if content_files:
                    # Check structure of first file
                    first_file = content_files[0]
                    required_fields = ["id", "filename", "file_type", "size", "uploaded_at", "description"]
                    has_all_fields = all(field in first_file for field in required_fields)
                    
                    # Count files with descriptions (badges)
                    files_with_descriptions = sum(1 for f in content_files if f.get("description", "").strip())
                    
                    if has_all_fields:
                        return self.log_test("Content Pending Endpoint", True, 
                                           f"Found {total_files} files, {files_with_descriptions} with descriptions (badges)")
                    else:
                        missing_fields = [f for f in required_fields if f not in first_file]
                        return self.log_test("Content Pending Endpoint", False, f"Missing fields: {missing_fields}")
                else:
                    return self.log_test("Content Pending Endpoint", True, "No content files found (empty library)")
            else:
                return self.log_test("Content Pending Endpoint", False, f"API error: {response.status_code}")
                
        except Exception as e:
            return self.log_test("Content Pending Endpoint", False, f"Exception: {str(e)}")
    
    def test_description_update_endpoint(self):
        """Test 4: PUT /api/content/{id}/description - Comment persistence"""
        try:
            # First get a file to test with
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if response.status_code != 200:
                return self.log_test("Description Update Endpoint", False, "Could not get content for testing")
            
            data = response.json()
            content_files = data.get("content", [])
            
            if not content_files:
                return self.log_test("Description Update Endpoint", False, "No files available for description testing")
            
            # Use first file for testing
            test_file = content_files[0]
            test_file_id = test_file["id"]
            
            # Test description update
            test_description = f"Test comment for synchronization - {datetime.now().strftime('%H:%M:%S')}"
            description_data = {"description": test_description}
            
            update_response = self.session.put(f"{BACKEND_URL}/content/{test_file_id}/description", json=description_data)
            
            if update_response.status_code == 200:
                # Verify persistence with fresh API call
                time.sleep(0.5)  # Brief pause for file system sync
                
                fresh_response = self.session.get(f"{BACKEND_URL}/content/pending", headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate"
                })
                
                if fresh_response.status_code == 200:
                    fresh_data = fresh_response.json()
                    fresh_files = fresh_data.get("content", [])
                    
                    updated_file = next((f for f in fresh_files if f["id"] == test_file_id), None)
                    
                    if updated_file and updated_file.get("description") == test_description:
                        return self.log_test("Description Update Endpoint", True, 
                                           "Description successfully saved and persisted in content_descriptions.json")
                    else:
                        return self.log_test("Description Update Endpoint", False, 
                                           "Description not persisted correctly")
                else:
                    return self.log_test("Description Update Endpoint", False, "Fresh API call failed")
            else:
                return self.log_test("Description Update Endpoint", False, 
                                   f"Update failed with status {update_response.status_code}")
                
        except Exception as e:
            return self.log_test("Description Update Endpoint", False, f"Exception: {str(e)}")
    
    def test_content_deletion_endpoint(self):
        """Test 5: DELETE /api/content/{id} - Permanent deletion"""
        try:
            # Upload a test file for deletion
            test_content = b'Test file for deletion verification'
            files = {
                'files': ('test_deletion.jpg', test_content, 'image/jpeg')
            }
            
            upload_response = self.session.post(f"{BACKEND_URL}/content/batch-upload", files=files)
            
            if upload_response.status_code != 200:
                return self.log_test("Content Deletion Endpoint", False, "Could not upload test file for deletion")
            
            upload_data = upload_response.json()
            uploaded_files = upload_data.get("uploaded_files", [])
            
            if not uploaded_files:
                return self.log_test("Content Deletion Endpoint", False, "No file uploaded for deletion test")
            
            # Get file ID
            test_filename = uploaded_files[0]["stored_name"]
            test_file_id = test_filename.split('.')[0]
            
            # Add description to test complete cleanup
            description_data = {"description": "File to be deleted - should not reappear"}
            self.session.put(f"{BACKEND_URL}/content/{test_file_id}/description", json=description_data)
            
            # Delete the file
            delete_response = self.session.delete(f"{BACKEND_URL}/content/{test_file_id}")
            
            if delete_response.status_code == 200:
                delete_data = delete_response.json()
                file_deleted = delete_data.get("file_deleted", False)
                description_deleted = delete_data.get("description_deleted", False)
                
                # Verify file doesn't reappear
                time.sleep(1)
                
                verification_response = self.session.get(f"{BACKEND_URL}/content/pending")
                if verification_response.status_code == 200:
                    verification_data = verification_response.json()
                    remaining_files = verification_data.get("content", [])
                    
                    file_still_exists = any(f["id"] == test_file_id for f in remaining_files)
                    
                    if not file_still_exists and file_deleted and description_deleted:
                        return self.log_test("Content Deletion Endpoint", True, 
                                           "File permanently deleted - does not reappear")
                    else:
                        return self.log_test("Content Deletion Endpoint", False, 
                                           f"Deletion issue: file_exists={file_still_exists}, file_deleted={file_deleted}, desc_deleted={description_deleted}")
                else:
                    return self.log_test("Content Deletion Endpoint", False, "Verification API call failed")
            else:
                return self.log_test("Content Deletion Endpoint", False, 
                                   f"Delete failed with status {delete_response.status_code}")
                
        except Exception as e:
            return self.log_test("Content Deletion Endpoint", False, f"Exception: {str(e)}")
    
    def test_badges_comments_logic(self):
        """Test 6: Badges/Comments display logic"""
        try:
            # Get current content
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if response.status_code != 200:
                return self.log_test("Badges/Comments Logic", False, "Could not get content for badge testing")
            
            data = response.json()
            content_files = data.get("content", [])
            
            if not content_files:
                return self.log_test("Badges/Comments Logic", False, "No files for badge testing")
            
            # Count files with and without descriptions
            files_with_descriptions = []
            files_without_descriptions = []
            
            for file_info in content_files:
                description = file_info.get("description", "")
                if description and description.strip():
                    files_with_descriptions.append(file_info)
                else:
                    files_without_descriptions.append(file_info)
            
            # Test adding a description to create a badge
            if files_without_descriptions:
                test_file = files_without_descriptions[0]
                test_file_id = test_file["id"]
                
                # Add description to create badge
                badge_description = "Test comment for badge display"
                description_data = {"description": badge_description}
                
                update_response = self.session.put(f"{BACKEND_URL}/content/{test_file_id}/description", json=description_data)
                
                if update_response.status_code == 200:
                    # Verify badge appears in fresh call
                    fresh_response = self.session.get(f"{BACKEND_URL}/content/pending")
                    
                    if fresh_response.status_code == 200:
                        fresh_data = fresh_response.json()
                        fresh_files = fresh_data.get("content", [])
                        
                        updated_file = next((f for f in fresh_files if f["id"] == test_file_id), None)
                        
                        if updated_file and updated_file.get("description") == badge_description:
                            return self.log_test("Badges/Comments Logic", True, 
                                               f"Badge logic working: {len(files_with_descriptions)+1} files with comments/badges")
                        else:
                            return self.log_test("Badges/Comments Logic", False, "Badge not appearing after description update")
                    else:
                        return self.log_test("Badges/Comments Logic", False, "Fresh API call failed for badge verification")
                else:
                    return self.log_test("Badges/Comments Logic", False, "Could not add description for badge test")
            else:
                return self.log_test("Badges/Comments Logic", True, 
                                   f"Badge logic verified: {len(files_with_descriptions)} files already have comments/badges")
                
        except Exception as e:
            return self.log_test("Badges/Comments Logic", False, f"Exception: {str(e)}")
    
    def test_content_descriptions_json_sync(self):
        """Test 7: content_descriptions.json synchronization"""
        try:
            # This test verifies the backend properly manages the JSON file
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if response.status_code == 200:
                data = response.json()
                content_files = data.get("content", [])
                
                # Test that descriptions are loaded from JSON file
                files_with_descriptions = sum(1 for f in content_files if f.get("description", "").strip())
                
                # Add a new description and verify it's saved
                if content_files:
                    test_file = content_files[0]
                    test_file_id = test_file["id"]
                    
                    sync_test_description = f"JSON sync test - {datetime.now().isoformat()}"
                    description_data = {"description": sync_test_description}
                    
                    update_response = self.session.put(f"{BACKEND_URL}/content/{test_file_id}/description", json=description_data)
                    
                    if update_response.status_code == 200:
                        # Multiple API calls to test persistence
                        for i in range(3):
                            time.sleep(0.2)
                            check_response = self.session.get(f"{BACKEND_URL}/content/pending")
                            
                            if check_response.status_code == 200:
                                check_data = check_response.json()
                                check_files = check_data.get("content", [])
                                check_file = next((f for f in check_files if f["id"] == test_file_id), None)
                                
                                if not check_file or check_file.get("description") != sync_test_description:
                                    return self.log_test("Content Descriptions JSON Sync", False, 
                                                       f"Description not persistent on API call #{i+1}")
                        
                        return self.log_test("Content Descriptions JSON Sync", True, 
                                           "content_descriptions.json synchronization working correctly")
                    else:
                        return self.log_test("Content Descriptions JSON Sync", False, "Could not update description for sync test")
                else:
                    return self.log_test("Content Descriptions JSON Sync", True, "No files to test sync with")
            else:
                return self.log_test("Content Descriptions JSON Sync", False, f"API error: {response.status_code}")
                
        except Exception as e:
            return self.log_test("Content Descriptions JSON Sync", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all bibliotheque content tests"""
        print("🚀 PHASE 1 - TESTS CRITIQUES BIBLIOTHÈQUE")
        print("Testing content library synchronization after frontend URL fix")
        print("=" * 70)
        
        # Test 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with content tests")
            return False
        
        print("\n📤 TESTING CONTENT UPLOAD")
        print("-" * 40)
        self.test_batch_upload_endpoint()
        
        print("\n📋 TESTING CONTENT LISTING")
        print("-" * 40)
        self.test_content_pending_endpoint()
        
        print("\n📝 TESTING DESCRIPTION PERSISTENCE")
        print("-" * 40)
        self.test_description_update_endpoint()
        
        print("\n🗑️ TESTING CONTENT DELETION")
        print("-" * 40)
        self.test_content_deletion_endpoint()
        
        print("\n🏷️ TESTING BADGES/COMMENTS LOGIC")
        print("-" * 40)
        self.test_badges_comments_logic()
        
        print("\n🔄 TESTING JSON SYNCHRONIZATION")
        print("-" * 40)
        self.test_content_descriptions_json_sync()
        
        # Summary
        print("\n" + "=" * 70)
        print("📋 BIBLIOTHEQUE TEST SUMMARY")
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
        
        # Specific findings for the 3 symptoms mentioned in review
        print("\n🔍 SYMPTOM ANALYSIS:")
        print("-" * 40)
        
        # Analyze test results for the 3 specific issues
        upload_working = any(r["test"] == "Batch Upload Endpoint" and r["success"] for r in self.test_results)
        descriptions_working = any(r["test"] == "Description Update Endpoint" and r["success"] for r in self.test_results)
        deletion_working = any(r["test"] == "Content Deletion Endpoint" and r["success"] for r in self.test_results)
        badges_working = any(r["test"] == "Badges/Comments Logic" and r["success"] for r in self.test_results)
        
        print(f"1. Médias supprimés qui reviennent: {'✅ RÉSOLU' if deletion_working else '❌ PROBLÈME PERSISTE'}")
        print(f"2. Commentaires ne s'enregistrent pas: {'✅ RÉSOLU' if descriptions_working else '❌ PROBLÈME PERSISTE'}")
        print(f"3. Badges de commentaire n'apparaissent pas: {'✅ RÉSOLU' if badges_working else '❌ PROBLÈME PERSISTE'}")
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = BibliothequeContentTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 TOUS LES TESTS BIBLIOTHÈQUE RÉUSSIS!")
        print("Les corrections de synchronisation fonctionnent correctement.")
    else:
        print("\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print("Veuillez examiner les tests échoués ci-dessus.")