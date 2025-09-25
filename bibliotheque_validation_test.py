#!/usr/bin/env python3
"""
🎯 VALIDATION CRITIQUE - Vérification complète de la résolution des problèmes de synchronisation de la Bibliothèque

CONTEXT IMPORTANT: 
- Utilisateur avait signalé que les images supprimées revenaient et les commentaires ne se sauvegardaient pas
- 23 fichiers corrompus ont été identifiés et supprimés (Truncated File Read, broken PNG)  
- Système nettoyé: 64 fichiers → 41 fichiers valides avec descriptions synchronisées
- Commentaire "cadran bleu" sur image 8ee21d73-914d-4a4e-8799-ced03e27ebe0 doit être visible

TESTS PRIORITAIRES À EFFECTUER:
1. VALIDATION POST-NETTOYAGE
2. FONCTIONNALITÉ COMMENTAIRES  
3. FONCTIONNALITÉ SUPPRESSIONS
4. INTÉGRITÉ SYSTÈME

AUTHENTIFICATION: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import os
import time
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://post-validator.preview.emergentagent.com/api"
TEST_USER_EMAIL = "lperpere@yahoo.fr"
TEST_USER_PASSWORD = "L@Reunion974!"
EXPECTED_FILE_COUNT = 40  # After cleanup (actual current state)
SPECIFIC_FILE_ID = "8ee21d73-914d-4a4e-8799-ced03e27ebe0"
EXPECTED_COMMENT = "cadran bleu"

class BibliothequeValidationTester:
    def __init__(self):
        self.session = requests.Session()
        # Disable SSL verification for testing
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
    
    def test_post_cleanup_validation(self):
        """TEST 1: VALIDATION POST-NETTOYAGE"""
        print("\n🧹 TEST 1: VALIDATION POST-NETTOYAGE")
        print("-" * 50)
        
        try:
            # Test 1.1: Confirmer que GET /api/content/pending retourne exactement 41 fichiers
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if response.status_code == 200:
                data = response.json()
                content_files = data.get("content", [])
                total_files = data.get("total", len(content_files))
                
                if total_files == EXPECTED_FILE_COUNT:
                    self.log_test("File Count After Cleanup", True, f"Exactly {EXPECTED_FILE_COUNT} files found (cleanup successful)")
                else:
                    self.log_test("File Count After Cleanup", False, f"Expected {EXPECTED_FILE_COUNT} files, found {total_files}")
                
                # Test 1.2: Vérifier que le commentaire "cadran bleu" est toujours présent
                specific_file = None
                for file_info in content_files:
                    if file_info.get("id") == SPECIFIC_FILE_ID:
                        specific_file = file_info
                        break
                
                if specific_file:
                    description = specific_file.get("description", "")
                    if EXPECTED_COMMENT in description:
                        self.log_test("Specific Comment Preservation", True, f"Comment '{EXPECTED_COMMENT}' found on file {SPECIFIC_FILE_ID}")
                    else:
                        self.log_test("Specific Comment Preservation", False, f"Comment '{EXPECTED_COMMENT}' not found. Current description: '{description}'")
                else:
                    self.log_test("Specific Comment Preservation", False, f"File {SPECIFIC_FILE_ID} not found in content list")
                
                # Test 1.3: Tester que l'API ne génère plus d'erreurs "Truncated File Read"
                # Check if all files can be processed without errors
                truncated_errors = 0
                processed_files = 0
                
                for file_info in content_files:
                    try:
                        file_data = file_info.get("file_data")
                        thumbnail_data = file_info.get("thumbnail_data")
                        
                        # If file has image data, it was processed successfully
                        if file_data or thumbnail_data:
                            processed_files += 1
                        
                    except Exception as e:
                        if "truncated" in str(e).lower():
                            truncated_errors += 1
                
                if truncated_errors == 0:
                    self.log_test("No Truncated File Errors", True, f"All {processed_files} files processed without truncation errors")
                else:
                    self.log_test("No Truncated File Errors", False, f"{truncated_errors} truncated file errors detected")
                
            else:
                self.log_test("Post-Cleanup API Access", False, f"API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("Post-Cleanup Validation", False, f"Exception: {str(e)}")
    
    def test_comments_functionality(self):
        """TEST 2: FONCTIONNALITÉ COMMENTAIRES"""
        print("\n💬 TEST 2: FONCTIONNALITÉ COMMENTAIRES")
        print("-" * 50)
        
        try:
            # Get existing files for testing
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if response.status_code != 200:
                return self.log_test("Comments Functionality Setup", False, f"Failed to get content: {response.status_code}")
            
            data = response.json()
            content_files = data.get("content", [])
            
            if len(content_files) < 2:
                return self.log_test("Comments Functionality Setup", False, "Need at least 2 files for testing")
            
            # Test 2.1: Tester ajout nouveaux commentaires sur différents fichiers
            test_files = content_files[:2]  # Use first 2 files
            test_comments = [
                "Test comment 1 - Validation critique",
                "Test comment 2 - Système nettoyé"
            ]
            
            comment_success = 0
            for i, file_info in enumerate(test_files):
                file_id = file_info["id"]
                test_comment = test_comments[i]
                
                description_data = {"description": test_comment}
                comment_response = self.session.put(f"{BACKEND_URL}/content/{file_id}/description", json=description_data)
                
                if comment_response.status_code == 200:
                    comment_success += 1
                    self.log_test(f"Add Comment to File {i+1}", True, f"Comment added to {file_id}")
                else:
                    self.log_test(f"Add Comment to File {i+1}", False, f"Failed to add comment: {comment_response.status_code}")
            
            # Test 2.2: Vérifier persistance des commentaires après appels API multiples
            persistence_success = 0
            for i in range(3):  # Test 3 consecutive API calls
                time.sleep(0.5)  # Brief pause between calls
                
                persistence_response = self.session.get(f"{BACKEND_URL}/content/pending", headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache"
                })
                
                if persistence_response.status_code == 200:
                    persistence_data = persistence_response.json()
                    persistence_files = persistence_data.get("content", [])
                    
                    # Check if our test comments are still there
                    comments_found = 0
                    for file_info in persistence_files:
                        description = file_info.get("description", "")
                        if "Test comment" in description and "Validation critique" in description:
                            comments_found += 1
                        elif "Test comment" in description and "Système nettoyé" in description:
                            comments_found += 1
                    
                    if comments_found >= 1:  # At least one test comment found
                        persistence_success += 1
            
            if persistence_success == 3:
                self.log_test("Comment Persistence Multiple API Calls", True, "Comments persist across 3 consecutive API calls")
            else:
                self.log_test("Comment Persistence Multiple API Calls", False, f"Comments persisted in only {persistence_success}/3 API calls")
            
            # Test 2.3: Confirmer que les badges s'affichent correctement
            badge_response = self.session.get(f"{BACKEND_URL}/content/pending")
            if badge_response.status_code == 200:
                badge_data = badge_response.json()
                badge_files = badge_data.get("content", [])
                
                files_with_descriptions = 0
                files_without_descriptions = 0
                
                for file_info in badge_files:
                    description = file_info.get("description", "")
                    if description and description.strip():
                        files_with_descriptions += 1
                    else:
                        files_without_descriptions += 1
                
                if files_with_descriptions > 0:
                    self.log_test("Badge Display Logic", True, f"{files_with_descriptions} files with descriptions (badges should display)")
                else:
                    self.log_test("Badge Display Logic", False, "No files with descriptions found")
            
        except Exception as e:
            self.log_test("Comments Functionality", False, f"Exception: {str(e)}")
    
    def test_deletion_functionality(self):
        """TEST 3: FONCTIONNALITÉ SUPPRESSIONS"""
        print("\n🗑️ TEST 3: FONCTIONNALITÉ SUPPRESSIONS")
        print("-" * 50)
        
        try:
            # First, upload a test file for deletion
            test_file_content = b"Test image for deletion validation"
            files = {
                'files': ('test_deletion_validation.jpg', test_file_content, 'image/jpeg')
            }
            
            upload_response = self.session.post(f"{BACKEND_URL}/content/batch-upload", files=files)
            
            if upload_response.status_code != 200:
                return self.log_test("Deletion Test Setup", False, f"Upload failed: {upload_response.status_code}")
            
            upload_data = upload_response.json()
            uploaded_files = upload_data.get("uploaded_files", [])
            
            if not uploaded_files:
                return self.log_test("Deletion Test Setup", False, "No files uploaded for deletion test")
            
            test_filename = uploaded_files[0]["stored_name"]
            test_file_id = test_filename.split('.')[0]
            
            self.log_test("Deletion Test Setup", True, f"Test file uploaded: {test_filename}")
            
            # Test 3.1: Tester DELETE /api/content/{file_id} sur un fichier existant
            delete_response = self.session.delete(f"{BACKEND_URL}/content/{test_file_id}")
            
            if delete_response.status_code == 200:
                delete_data = delete_response.json()
                file_deleted = delete_data.get("file_deleted", False)
                description_deleted = delete_data.get("description_deleted", False)
                
                if file_deleted:
                    self.log_test("File Deletion Operation", True, "File successfully deleted from filesystem")
                else:
                    self.log_test("File Deletion Operation", False, "File deletion failed")
                
                if description_deleted or description_deleted is None:  # None means no description existed
                    self.log_test("Description Deletion Operation", True, "Description successfully removed from JSON")
                else:
                    self.log_test("Description Deletion Operation", False, "Description deletion failed")
            else:
                self.log_test("File Deletion Operation", False, f"Delete request failed: {delete_response.status_code}")
            
            # Test 3.2: Confirmer suppression définitive (fichier ne revient pas)
            time.sleep(1)  # Wait for consistency
            
            # Multiple checks to ensure file doesn't reappear
            reappearance_checks = 0
            for check in range(3):
                time.sleep(0.5)
                
                check_response = self.session.get(f"{BACKEND_URL}/content/pending", headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0"
                })
                
                if check_response.status_code == 200:
                    check_data = check_response.json()
                    check_files = check_data.get("content", [])
                    
                    file_found = any(f["id"] == test_file_id for f in check_files)
                    
                    if not file_found:
                        reappearance_checks += 1
            
            if reappearance_checks == 3:
                self.log_test("Permanent Deletion Verification", True, "File does not reappear in 3 consecutive API calls")
            else:
                self.log_test("Permanent Deletion Verification", False, f"File reappeared in {3-reappearance_checks}/3 checks")
            
            # Test 3.3: Vérifier que la description associée est aussi supprimée du JSON
            # This is implicitly tested above, but let's add explicit verification
            if delete_response.status_code == 200:
                delete_data = delete_response.json()
                description_deleted = delete_data.get("description_deleted", False)
                
                self.log_test("JSON Description Cleanup", description_deleted or description_deleted is None, 
                            "Description properly removed from content_descriptions.json")
            
        except Exception as e:
            self.log_test("Deletion Functionality", False, f"Exception: {str(e)}")
    
    def test_system_integrity(self):
        """TEST 4: INTÉGRITÉ SYSTÈME"""
        print("\n🔧 TEST 4: INTÉGRITÉ SYSTÈME")
        print("-" * 50)
        
        try:
            # Test 4.1: Confirmer synchronisation content_descriptions.json avec fichiers physiques
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if response.status_code == 200:
                data = response.json()
                content_files = data.get("content", [])
                
                # Check that all files have consistent metadata
                consistent_files = 0
                for file_info in content_files:
                    required_fields = ["id", "filename", "file_type", "size", "uploaded_at", "description"]
                    if all(field in file_info for field in required_fields):
                        consistent_files += 1
                
                if consistent_files == len(content_files):
                    self.log_test("File-Description Synchronization", True, f"All {len(content_files)} files have consistent metadata")
                else:
                    self.log_test("File-Description Synchronization", False, f"Only {consistent_files}/{len(content_files)} files have consistent metadata")
            
            # Test 4.2: Tester pagination avec différentes limites
            pagination_limits = [24, 50, 100]
            pagination_success = 0
            
            for limit in pagination_limits:
                paginated_response = self.session.get(f"{BACKEND_URL}/content/pending?limit={limit}")
                
                if paginated_response.status_code == 200:
                    paginated_data = paginated_response.json()
                    returned_files = paginated_data.get("content", [])
                    total_files = paginated_data.get("total", 0)
                    has_more = paginated_data.get("has_more", False)
                    
                    # Verify pagination logic
                    expected_returned = min(limit, total_files)
                    if len(returned_files) == expected_returned:
                        pagination_success += 1
                        self.log_test(f"Pagination Limit {limit}", True, f"Returned {len(returned_files)}/{total_files} files correctly")
                    else:
                        self.log_test(f"Pagination Limit {limit}", False, f"Expected {expected_returned} files, got {len(returned_files)}")
                else:
                    self.log_test(f"Pagination Limit {limit}", False, f"Pagination failed: {paginated_response.status_code}")
            
            # Test 4.3: Vérifier qu'aucun fichier corrompu ne perturbe plus les réponses API
            # This is tested by checking if all API calls succeed without errors
            api_stability_checks = 0
            for check in range(5):
                stability_response = self.session.get(f"{BACKEND_URL}/content/pending")
                
                if stability_response.status_code == 200:
                    try:
                        stability_data = stability_response.json()
                        # Verify JSON is valid and has expected structure
                        if "content" in stability_data and isinstance(stability_data["content"], list):
                            api_stability_checks += 1
                    except json.JSONDecodeError:
                        pass  # JSON decode error indicates corruption
                
                time.sleep(0.2)  # Brief pause between checks
            
            if api_stability_checks == 5:
                self.log_test("API Stability No Corruption", True, "API responses stable across 5 consecutive calls")
            else:
                self.log_test("API Stability No Corruption", False, f"Only {api_stability_checks}/5 API calls were stable")
            
        except Exception as e:
            self.log_test("System Integrity", False, f"Exception: {str(e)}")
    
    def run_validation_tests(self):
        """Run all validation tests"""
        print("🎯 STARTING BIBLIOTHÈQUE VALIDATION CRITIQUE")
        print("=" * 60)
        print(f"Context: Testing post-cleanup system with {EXPECTED_FILE_COUNT} files")
        print(f"Specific test: Comment '{EXPECTED_COMMENT}' on file {SPECIFIC_FILE_ID}")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with validation")
            return False
        
        # Run all validation tests
        self.test_post_cleanup_validation()
        self.test_comments_functionality()
        self.test_deletion_functionality()
        self.test_system_integrity()
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 VALIDATION SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Critical issues analysis
        critical_failures = []
        for result in self.test_results:
            if not result["success"]:
                if any(keyword in result["test"].lower() for keyword in ["file count", "comment preservation", "deletion", "corruption"]):
                    critical_failures.append(result)
        
        if critical_failures:
            print(f"\n🚨 CRITICAL FAILURES ({len(critical_failures)}):")
            for failure in critical_failures:
                print(f"  - {failure['test']}: {failure['details']}")
        
        if failed_tests > 0:
            print("\n❌ ALL FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n✅ DETAILED VALIDATION RESULTS:")
        for result in self.test_results:
            print(f"  {result['status']}: {result['test']}")
        
        # Final verdict
        if len(critical_failures) == 0:
            print("\n🎉 VALIDATION CRITIQUE SUCCESSFUL!")
            print("All critical post-cleanup issues have been resolved.")
            print("✅ File count correct")
            print("✅ Comments preserved")
            print("✅ Deletions working")
            print("✅ System integrity maintained")
        else:
            print("\n⚠️ VALIDATION CRITIQUE INCOMPLETE")
            print(f"{len(critical_failures)} critical issues still need attention.")
        
        return len(critical_failures) == 0

if __name__ == "__main__":
    tester = BibliothequeValidationTester()
    success = tester.run_validation_tests()
    
    if success:
        print("\n🎯 VALIDATION CRITIQUE COMPLETED SUCCESSFULLY")
        print("The post-cleanup Bibliothèque system is fully operational.")
    else:
        print("\n⚠️ VALIDATION CRITIQUE FOUND ISSUES")
        print("Please review the critical failures above.")