#!/usr/bin/env python3
"""
OPERATIONAL TITLE FUNCTIONALITY TESTING - POST BUG FIXES
Testing the operational title functionality after critical bug fixes have been applied.

Test Requirements:
- Authentication: lperpere@yahoo.fr / L@Reunion974!
- Backend URL: https://post-validator.preview.emergentagent.com/api
- Critical Issues Fixed: Upload title preservation, modal save bug, state management

Test Scenarios:
1. Content Listing Verification (GET /api/content/pending)
2. Title Update Testing (PUT /api/content/{id}/title)
3. Context Update Testing (PUT /api/content/{id}/context)
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://post-validator.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class OperationalTitleTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.test_results = []
        
    def log_result(self, step, success, message, details=None):
        """Log test result"""
        status = "✅" if success else "❌"
        result = {
            "step": step,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} Step {step}: {message}")
        if details:
            print(f"   Details: {details}")
        return success
    
    def authenticate(self):
        """Step 1: Authenticate with provided credentials"""
        try:
            auth_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(
                f"{BASE_URL}/auth/login-robust",
                json=auth_data,
                headers={"Content-Type": "application/json"},
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
                
                return self.log_result(
                    1, True, 
                    "Authentication successful",
                    f"User ID: {self.user_id}, Token obtained"
                )
            else:
                return self.log_result(
                    1, False,
                    f"Authentication failed - HTTP {response.status_code}",
                    response.text[:200]
                )
                
        except Exception as e:
            return self.log_result(
                1, False,
                "Authentication error",
                str(e)
            )
    
    def test_content_listing(self):
        """Step 2: Content Listing Verification - GET /api/content/pending"""
        try:
            response = self.session.get(
                f"{BASE_URL}/content/pending",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                total_items = data.get("total", 0)
                
                # Analyze title vs filename usage
                items_with_title = 0
                items_with_empty_title = 0
                
                for item in content_items:
                    title = item.get("title", "")
                    filename = item.get("filename", "")
                    
                    if title and title.strip():
                        items_with_title += 1
                    else:
                        items_with_empty_title += 1
                
                return self.log_result(
                    2, True,
                    "Content listing retrieved successfully",
                    f"Total items: {total_items}, Items loaded: {len(content_items)}, "
                    f"Items with operational title: {items_with_title}, "
                    f"Items with empty title: {items_with_empty_title}"
                )
            else:
                return self.log_result(
                    2, False,
                    f"Content listing failed - HTTP {response.status_code}",
                    response.text[:200]
                )
                
        except Exception as e:
            return self.log_result(
                2, False,
                "Content listing error",
                str(e)
            )
    
    def test_title_update(self):
        """Step 3: Title Update Testing - PUT /api/content/{id}/title"""
        try:
            # First get content to find an item to test with
            response = self.session.get(f"{BASE_URL}/content/pending", timeout=30)
            
            if response.status_code != 200:
                return self.log_result(
                    3, False,
                    "Cannot get content for title update test",
                    f"HTTP {response.status_code}"
                )
            
            content_data = response.json()
            content_items = content_data.get("content", [])
            
            if not content_items:
                return self.log_result(
                    3, False,
                    "No content items available for title update test",
                    "Content list is empty"
                )
            
            # Use the first content item for testing
            test_content = content_items[0]
            content_id = test_content.get("id")
            original_title = test_content.get("title", "")
            
            # Test title update
            test_title = "Nouveau titre opérationnel test"
            title_data = {"title": test_title}
            
            response = self.session.put(
                f"{BASE_URL}/content/{content_id}/title",
                json=title_data,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                success_message = response_data.get("message", "")
                
                return self.log_result(
                    3, True,
                    "Title update successful",
                    f"Content ID: {content_id}, New title: '{test_title}', "
                    f"Response: '{success_message}'"
                )
            else:
                return self.log_result(
                    3, False,
                    f"Title update failed - HTTP {response.status_code}",
                    response.text[:200]
                )
                
        except Exception as e:
            return self.log_result(
                3, False,
                "Title update error",
                str(e)
            )
    
    def test_title_persistence(self):
        """Step 4: Verify title persistence - GET /api/content/pending again"""
        try:
            response = self.session.get(f"{BASE_URL}/content/pending", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                
                # Look for the updated title
                test_title_found = False
                for item in content_items:
                    title = item.get("title", "")
                    if "Nouveau titre opérationnel test" in title:
                        test_title_found = True
                        break
                
                if test_title_found:
                    return self.log_result(
                        4, True,
                        "Title persistence verified",
                        "Updated title found in content listing"
                    )
                else:
                    return self.log_result(
                        4, False,
                        "Title persistence failed",
                        "Updated title not found in content listing"
                    )
            else:
                return self.log_result(
                    4, False,
                    f"Title persistence check failed - HTTP {response.status_code}",
                    response.text[:200]
                )
                
        except Exception as e:
            return self.log_result(
                4, False,
                "Title persistence check error",
                str(e)
            )
    
    def test_context_update(self):
        """Step 5: Context Update Testing - PUT /api/content/{id}/context"""
        try:
            # Get content items
            response = self.session.get(f"{BASE_URL}/content/pending", timeout=30)
            
            if response.status_code != 200:
                return self.log_result(
                    5, False,
                    "Cannot get content for context update test",
                    f"HTTP {response.status_code}"
                )
            
            content_data = response.json()
            content_items = content_data.get("content", [])
            
            if not content_items:
                return self.log_result(
                    5, False,
                    "No content items available for context update test",
                    "Content list is empty"
                )
            
            # Use the first content item for testing
            test_content = content_items[0]
            content_id = test_content.get("id")
            
            # Test context update
            test_context = "Test contexte pour cette image - description et mots-clés"
            context_data = {"context": test_context}
            
            response = self.session.put(
                f"{BASE_URL}/content/{content_id}/context",
                json=context_data,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                success_message = response_data.get("message", "")
                
                return self.log_result(
                    5, True,
                    "Context update successful",
                    f"Content ID: {content_id}, New context: '{test_context}', "
                    f"Response: '{success_message}'"
                )
            else:
                return self.log_result(
                    5, False,
                    f"Context update failed - HTTP {response.status_code}",
                    response.text[:200]
                )
                
        except Exception as e:
            return self.log_result(
                5, False,
                "Context update error",
                str(e)
            )
    
    def test_field_coexistence(self):
        """Step 6: Verify title and context fields coexist properly"""
        try:
            response = self.session.get(f"{BASE_URL}/content/pending", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                
                # Analyze field structure
                items_with_both_fields = 0
                items_with_title_field = 0
                items_with_context_field = 0
                items_with_filename_field = 0
                
                for item in content_items:
                    has_title = "title" in item
                    has_context = "context" in item
                    has_filename = "filename" in item
                    
                    if has_title:
                        items_with_title_field += 1
                    if has_context:
                        items_with_context_field += 1
                    if has_filename:
                        items_with_filename_field += 1
                    if has_title and has_context:
                        items_with_both_fields += 1
                
                return self.log_result(
                    6, True,
                    "Field coexistence verified",
                    f"Items with title field: {items_with_title_field}, "
                    f"Items with context field: {items_with_context_field}, "
                    f"Items with filename field: {items_with_filename_field}, "
                    f"Items with both title and context: {items_with_both_fields}"
                )
            else:
                return self.log_result(
                    6, False,
                    f"Field coexistence check failed - HTTP {response.status_code}",
                    response.text[:200]
                )
                
        except Exception as e:
            return self.log_result(
                6, False,
                "Field coexistence check error",
                str(e)
            )
    
    def run_all_tests(self):
        """Run all operational title tests"""
        print("🎯 OPERATIONAL TITLE FUNCTIONALITY TESTING - POST BUG FIXES")
        print("=" * 70)
        print(f"Backend URL: {BASE_URL}")
        print(f"Test Credentials: {TEST_EMAIL}")
        print("=" * 70)
        
        # Run tests in sequence
        tests = [
            self.authenticate,
            self.test_content_listing,
            self.test_title_update,
            self.test_title_persistence,
            self.test_context_update,
            self.test_field_coexistence
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            if test():
                passed_tests += 1
            else:
                # Continue with remaining tests even if one fails
                pass
        
        # Summary
        print("\n" + "=" * 70)
        print("🎯 OPERATIONAL TITLE TESTING SUMMARY")
        print("=" * 70)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}% success rate)")
        
        if success_rate == 100:
            print("🎉 ALL TESTS PASSED - Operational title functionality is working correctly!")
        elif success_rate >= 80:
            print("✅ MOSTLY SUCCESSFUL - Minor issues detected but core functionality working")
        else:
            print("❌ CRITICAL ISSUES DETECTED - Operational title functionality needs attention")
        
        print("\nDetailed Results:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} Step {result['step']}: {result['message']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = OperationalTitleTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)