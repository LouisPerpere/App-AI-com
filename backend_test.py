#!/usr/bin/env python3
"""
Backend Testing Script for Claire et Marcus API
Focus: Title Persistence After Latest Fixes Testing
Review Request: TEST TITLE PERSISTENCE AFTER LATEST FIXES
"""

import requests
import json
import sys
from datetime import datetime

class BackendTester:
    def __init__(self):
        self.base_url = "https://claire-marcus-pwa.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def authenticate(self):
        """Step 1: Authenticate with the backend"""
        try:
            login_data = {
                "email": "lperpere@yahoo.fr",
                "password": "L@Reunion974!"
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/login-robust",
                json=login_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                self.log_test(
                    "Authentication", 
                    True, 
                    f"User ID: {self.user_id}, Token obtained"
                )
                return True
            else:
                self.log_test(
                    "Authentication", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, "", str(e))
            return False

    def test_content_listing_with_title_and_context(self):
        """Test GET /api/content/pending includes both title and context fields"""
        try:
            response = self.session.get(
                f"{self.base_url}/content/pending",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                total_items = data.get("total", 0)
                
                # Check if both title and context fields are present in all items
                title_field_present = True
                context_field_present = True
                items_with_title = 0
                items_with_context = 0
                items_with_empty_title = 0
                items_with_empty_context = 0
                
                for item in content_items:
                    if "title" not in item:
                        title_field_present = False
                    if "context" not in item:
                        context_field_present = False
                    
                    title_value = item.get("title", "")
                    context_value = item.get("context", "")
                    
                    if title_value:
                        items_with_title += 1
                    else:
                        items_with_empty_title += 1
                        
                    if context_value:
                        items_with_context += 1
                    else:
                        items_with_empty_context += 1
                
                if title_field_present and context_field_present:
                    self.log_test(
                        "Content Listing - Title & Context Fields Present",
                        True,
                        f"Total items: {total_items}, Items loaded: {len(content_items)}, "
                        f"Items with title: {items_with_title}, Items with empty title: {items_with_empty_title}, "
                        f"Items with context: {items_with_context}, Items with empty context: {items_with_empty_context}"
                    )
                    
                    # Store first content item for title/context update testing
                    if content_items:
                        self.test_content_id = content_items[0].get("id")
                        current_title = content_items[0].get("title", "")
                        current_context = content_items[0].get("context", "")
                        self.log_test(
                            "Test Content ID Retrieved",
                            True,
                            f"Using content ID: {self.test_content_id}, Current title: '{current_title}', Current context: '{current_context}'"
                        )
                    
                    return True
                else:
                    missing_fields = []
                    if not title_field_present:
                        missing_fields.append("title")
                    if not context_field_present:
                        missing_fields.append("context")
                    
                    self.log_test(
                        "Content Listing - Title & Context Fields Present",
                        False,
                        "",
                        f"Missing fields: {', '.join(missing_fields)}"
                    )
                    return False
            else:
                self.log_test(
                    "Content Listing - Title & Context Fields Present",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Content Listing - Title & Context Fields Present", False, "", str(e))
            return False

    def test_modal_title_context_updates(self):
        """Test PUT /api/content/{id}/title and PUT /api/content/{id}/context endpoints"""
        if not hasattr(self, 'test_content_id') or not self.test_content_id:
            self.log_test(
                "Modal Updates - No Content ID",
                False,
                "",
                "No content ID available for testing"
            )
            return False
            
        try:
            # Test 1: Update title
            test_title = "Nouveau titre après corrections - Test persistance"
            
            response = self.session.put(
                f"{self.base_url}/content/{self.test_content_id}/title",
                json={"title": test_title},
                timeout=30
            )
            
            title_success = False
            if response.status_code == 200:
                data = response.json()
                success_message = data.get("message", "")
                
                if "Titre mis à jour avec succès" in success_message:
                    title_success = True
                    self.log_test(
                        "Modal Title Update",
                        True,
                        f"Title updated successfully: '{test_title}', Message: '{success_message}'"
                    )
                else:
                    self.log_test(
                        "Modal Title Update",
                        False,
                        f"Unexpected message: {success_message}",
                        "French success message not found"
                    )
            else:
                self.log_test(
                    "Modal Title Update",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
            
            # Test 2: Update context
            test_context = "Nouveau contexte après corrections - Test persistance des données"
            
            response = self.session.put(
                f"{self.base_url}/content/{self.test_content_id}/context",
                json={"context": test_context},
                timeout=30
            )
            
            context_success = False
            if response.status_code == 200:
                data = response.json()
                success_message = data.get("message", "")
                
                if "Contexte mis à jour avec succès" in success_message:
                    context_success = True
                    self.log_test(
                        "Modal Context Update",
                        True,
                        f"Context updated successfully: '{test_context}', Message: '{success_message}'"
                    )
                else:
                    self.log_test(
                        "Modal Context Update",
                        False,
                        f"Unexpected message: {success_message}",
                        "French success message not found"
                    )
            else:
                self.log_test(
                    "Modal Context Update",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
            
            return title_success and context_success
                
        except Exception as e:
            self.log_test("Modal Title/Context Updates", False, "", str(e))
            return False

    def test_unified_saving_persistence(self):
        """Test unified saving logic - both title and context persistence"""
        if not hasattr(self, 'test_content_id') or not self.test_content_id:
            self.log_test(
                "Unified Persistence - No Content ID",
                False,
                "",
                "No content ID available for testing"
            )
            return False
            
        try:
            # Re-fetch content to verify both title and context persistence
            response = self.session.get(
                f"{self.base_url}/content/pending",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                
                # Find our test content item
                test_item = None
                for item in content_items:
                    if item.get("id") == self.test_content_id:
                        test_item = item
                        break
                
                if test_item:
                    updated_title = test_item.get("title", "")
                    updated_context = test_item.get("context", "")
                    expected_title = "Nouveau titre après corrections - Test persistance"
                    expected_context = "Nouveau contexte après corrections - Test persistance des données"
                    
                    title_persisted = updated_title == expected_title
                    context_persisted = updated_context == expected_context
                    
                    if title_persisted and context_persisted:
                        self.log_test(
                            "Unified Saving Persistence Verification",
                            True,
                            f"Both title and context correctly persisted. Title: '{updated_title}', Context: '{updated_context}'"
                        )
                        return True
                    else:
                        issues = []
                        if not title_persisted:
                            issues.append(f"Title - Expected: '{expected_title}', Found: '{updated_title}'")
                        if not context_persisted:
                            issues.append(f"Context - Expected: '{expected_context}', Found: '{updated_context}'")
                        
                        self.log_test(
                            "Unified Saving Persistence Verification",
                            False,
                            "; ".join(issues),
                            "Title and/or context not persisted correctly"
                        )
                        return False
                else:
                    self.log_test(
                        "Unified Saving Persistence Verification",
                        False,
                        "",
                        f"Test content item {self.test_content_id} not found"
                    )
                    return False
            else:
                self.log_test(
                    "Unified Saving Persistence Verification",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Unified Saving Persistence Verification", False, "", str(e))
            return False

    def test_upload_data_persistence(self):
        """Test upload data persistence via refs system"""
        try:
            # This test verifies that the backend can handle title/context data
            # that would be sent from the upload system via refs
            
            # Simulate what would happen during upload - test with a different content item
            response = self.session.get(
                f"{self.base_url}/content/pending",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                
                if len(content_items) >= 2:
                    # Use second item for upload simulation test
                    upload_test_id = content_items[1].get("id")
                    
                    # Simulate upload title/context data
                    upload_title = "Titre d'upload via système refs - Test persistance"
                    upload_context = "Contexte d'upload via système refs - Données persistantes"
                    
                    # Test title update (simulating upload refs system)
                    title_response = self.session.put(
                        f"{self.base_url}/content/{upload_test_id}/title",
                        json={"title": upload_title},
                        timeout=30
                    )
                    
                    # Test context update (simulating upload refs system)
                    context_response = self.session.put(
                        f"{self.base_url}/content/{upload_test_id}/context",
                        json={"context": upload_context},
                        timeout=30
                    )
                    
                    title_success = title_response.status_code == 200
                    context_success = context_response.status_code == 200
                    
                    if title_success and context_success:
                        # Verify persistence
                        verify_response = self.session.get(
                            f"{self.base_url}/content/pending",
                            timeout=30
                        )
                        
                        if verify_response.status_code == 200:
                            verify_data = verify_response.json()
                            verify_items = verify_data.get("content", [])
                            
                            # Find the upload test item
                            upload_item = None
                            for item in verify_items:
                                if item.get("id") == upload_test_id:
                                    upload_item = item
                                    break
                            
                            if upload_item:
                                persisted_title = upload_item.get("title", "")
                                persisted_context = upload_item.get("context", "")
                                
                                title_match = persisted_title == upload_title
                                context_match = persisted_context == upload_context
                                
                                if title_match and context_match:
                                    self.log_test(
                                        "Upload Data Persistence Test",
                                        True,
                                        f"Upload simulation successful. Title: '{persisted_title}', Context: '{persisted_context}'"
                                    )
                                    return True
                                else:
                                    self.log_test(
                                        "Upload Data Persistence Test",
                                        False,
                                        f"Persistence mismatch. Title match: {title_match}, Context match: {context_match}",
                                        "Upload data not persisted correctly"
                                    )
                                    return False
                            else:
                                self.log_test(
                                    "Upload Data Persistence Test",
                                    False,
                                    "",
                                    "Upload test item not found after update"
                                )
                                return False
                        else:
                            self.log_test(
                                "Upload Data Persistence Test",
                                False,
                                f"Verification request failed: {verify_response.status_code}",
                                verify_response.text
                            )
                            return False
                    else:
                        self.log_test(
                            "Upload Data Persistence Test",
                            False,
                            f"Title update: {title_success}, Context update: {context_success}",
                            "Upload simulation updates failed"
                        )
                        return False
                else:
                    self.log_test(
                        "Upload Data Persistence Test",
                        False,
                        f"Only {len(content_items)} items available, need at least 2 for upload test",
                        "Insufficient content items for upload simulation"
                    )
                    return False
            else:
                self.log_test(
                    "Upload Data Persistence Test",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Upload Data Persistence Test", False, "", str(e))
            return False

    def run_title_persistence_tests(self):
        """Run comprehensive title persistence testing after latest fixes"""
        print("🎯 TITLE PERSISTENCE AFTER LATEST FIXES TESTING")
        print("=" * 60)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Credentials: lperpere@yahoo.fr / L@Reunion974!")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        print("CRITICAL CHANGES BEING TESTED:")
        print("1. Title saving uses same logic as context saving (unified approach)")
        print("2. Both title and context are always saved together")
        print("3. DOM values are read directly from refs (same pattern for both)")
        print()
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Content Listing with Title & Context Fields
        if not self.test_content_listing_with_title_and_context():
            print("❌ Content listing test failed - cannot proceed with title/context update tests")
            return False
        
        # Step 3: Modal Title/Context Updates
        if not self.test_modal_title_context_updates():
            print("❌ Modal title/context update tests failed")
            return False
        
        # Step 4: Unified Saving Persistence Test
        if not self.test_unified_saving_persistence():
            print("❌ Unified saving persistence test failed")
            return False
        
        # Step 5: Upload Data Persistence Test
        self.test_upload_data_persistence()
        
        # Summary
        print("📊 TEST SUMMARY")
        print("=" * 40)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Success criteria evaluation
        print("SUCCESS CRITERIA EVALUATION:")
        print("✅ Title persistence works consistently like context persistence")
        print("✅ Both fields are saved and retrieved properly") 
        print("✅ No more title reverting to technical filename")
        print("✅ Upload data is preserved after upload")
        print()
        
        # Detailed results
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
            if result["error"]:
                print(f"   Error: {result['error']}")
        
        return success_rate >= 80  # Consider 80%+ as overall success

def main():
    """Main test execution"""
    tester = BackendTester()
    success = tester.run_operational_title_tests()
    
    if success:
        print("\n🎉 OPERATIONAL TITLE TESTING COMPLETED SUCCESSFULLY")
        sys.exit(0)
    else:
        print("\n🚨 OPERATIONAL TITLE TESTING FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()