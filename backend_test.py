#!/usr/bin/env python3
"""
Backend Testing Script for Claire et Marcus API
Focus: Operational Title Field Implementation Testing
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

    def test_content_listing_with_title(self):
        """Test GET /api/content/pending includes title field"""
        try:
            response = self.session.get(
                f"{self.base_url}/content/pending",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                total_items = data.get("total", 0)
                
                # Check if title field is present in all items
                title_field_present = True
                items_with_title = 0
                items_with_empty_title = 0
                
                for item in content_items:
                    if "title" not in item:
                        title_field_present = False
                        break
                    
                    title_value = item.get("title", "")
                    if title_value:
                        items_with_title += 1
                    else:
                        items_with_empty_title += 1
                
                if title_field_present:
                    self.log_test(
                        "Content Listing - Title Field Present",
                        True,
                        f"Total items: {total_items}, Items loaded: {len(content_items)}, "
                        f"Items with title: {items_with_title}, Items with empty title: {items_with_empty_title}"
                    )
                    
                    # Store first content item for title update testing
                    if content_items:
                        self.test_content_id = content_items[0].get("id")
                        self.log_test(
                            "Test Content ID Retrieved",
                            True,
                            f"Using content ID: {self.test_content_id} for title update tests"
                        )
                    
                    return True
                else:
                    self.log_test(
                        "Content Listing - Title Field Present",
                        False,
                        "",
                        "Title field missing from content items"
                    )
                    return False
            else:
                self.log_test(
                    "Content Listing - Title Field Present",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Content Listing - Title Field Present", False, "", str(e))
            return False

    def test_title_update_endpoint(self):
        """Test PUT /api/content/{content_id}/title endpoint"""
        if not hasattr(self, 'test_content_id') or not self.test_content_id:
            self.log_test(
                "Title Update - No Content ID",
                False,
                "",
                "No content ID available for testing"
            )
            return False
            
        try:
            # Test updating operational title
            test_title = "Titre opérationnel de test - Contenu marketing"
            
            response = self.session.put(
                f"{self.base_url}/content/{self.test_content_id}/title",
                json={"title": test_title},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                success_message = data.get("message", "")
                
                if "Titre mis à jour avec succès" in success_message:
                    self.log_test(
                        "Title Update - Success Response",
                        True,
                        f"Content ID: {self.test_content_id}, Title: '{test_title}', Message: '{success_message}'"
                    )
                    return True
                else:
                    self.log_test(
                        "Title Update - Success Response",
                        False,
                        f"Unexpected message: {success_message}",
                        "French success message not found"
                    )
                    return False
            else:
                self.log_test(
                    "Title Update - Success Response",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Title Update - Success Response", False, "", str(e))
            return False

    def test_title_persistence(self):
        """Test that title updates persist correctly"""
        if not hasattr(self, 'test_content_id') or not self.test_content_id:
            self.log_test(
                "Title Persistence - No Content ID",
                False,
                "",
                "No content ID available for testing"
            )
            return False
            
        try:
            # Re-fetch content to verify title persistence
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
                    expected_title = "Titre opérationnel de test - Contenu marketing"
                    
                    if updated_title == expected_title:
                        self.log_test(
                            "Title Persistence Verification",
                            True,
                            f"Title correctly persisted: '{updated_title}'"
                        )
                        return True
                    else:
                        self.log_test(
                            "Title Persistence Verification",
                            False,
                            f"Expected: '{expected_title}', Found: '{updated_title}'",
                            "Title not persisted correctly"
                        )
                        return False
                else:
                    self.log_test(
                        "Title Persistence Verification",
                        False,
                        "",
                        f"Test content item {self.test_content_id} not found"
                    )
                    return False
            else:
                self.log_test(
                    "Title Persistence Verification",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Title Persistence Verification", False, "", str(e))
            return False

    def test_edge_cases(self):
        """Test edge cases for title updates"""
        if not hasattr(self, 'test_content_id') or not self.test_content_id:
            self.log_test(
                "Edge Cases - No Content ID",
                False,
                "",
                "No content ID available for testing"
            )
            return False
            
        edge_case_results = []
        
        # Test 1: Empty string title
        try:
            response = self.session.put(
                f"{self.base_url}/content/{self.test_content_id}/title",
                json={"title": ""},
                timeout=30
            )
            
            if response.status_code == 200:
                edge_case_results.append("Empty title: PASS")
            else:
                edge_case_results.append(f"Empty title: FAIL ({response.status_code})")
                
        except Exception as e:
            edge_case_results.append(f"Empty title: ERROR ({str(e)})")
        
        # Test 2: Special characters and French accents
        try:
            special_title = "Titre avec accents éàçù et caractères spéciaux !@#$%"
            response = self.session.put(
                f"{self.base_url}/content/{self.test_content_id}/title",
                json={"title": special_title},
                timeout=30
            )
            
            if response.status_code == 200:
                edge_case_results.append("Special characters: PASS")
            else:
                edge_case_results.append(f"Special characters: FAIL ({response.status_code})")
                
        except Exception as e:
            edge_case_results.append(f"Special characters: ERROR ({str(e)})")
        
        # Test 3: Non-existent content ID
        try:
            fake_id = "nonexistent-content-id-12345"
            response = self.session.put(
                f"{self.base_url}/content/{fake_id}/title",
                json={"title": "Test title"},
                timeout=30
            )
            
            if response.status_code == 404:
                edge_case_results.append("Non-existent ID: PASS (404 returned)")
            else:
                edge_case_results.append(f"Non-existent ID: FAIL (Expected 404, got {response.status_code})")
                
        except Exception as e:
            edge_case_results.append(f"Non-existent ID: ERROR ({str(e)})")
        
        # Evaluate overall edge case testing
        passed_tests = len([r for r in edge_case_results if "PASS" in r])
        total_tests = len(edge_case_results)
        
        self.log_test(
            "Edge Cases Testing",
            passed_tests == total_tests,
            f"Passed {passed_tests}/{total_tests} edge case tests: {', '.join(edge_case_results)}",
            "" if passed_tests == total_tests else "Some edge cases failed"
        )
        
        return passed_tests == total_tests

    def run_operational_title_tests(self):
        """Run comprehensive operational title testing"""
        print("🎯 OPERATIONAL TITLE FIELD BACKEND TESTING")
        print("=" * 60)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Credentials: lperpere@yahoo.fr / L@Reunion974!")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Content Listing with Title Field
        if not self.test_content_listing_with_title():
            print("❌ Content listing test failed - cannot proceed with title update tests")
            return False
        
        # Step 3: Title Update Endpoint
        if not self.test_title_update_endpoint():
            print("❌ Title update test failed")
            return False
        
        # Step 4: Title Persistence Verification
        if not self.test_title_persistence():
            print("❌ Title persistence test failed")
            return False
        
        # Step 5: Edge Cases
        self.test_edge_cases()
        
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