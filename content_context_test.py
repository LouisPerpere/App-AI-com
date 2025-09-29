#!/usr/bin/env python3
"""
Content Context Endpoints Testing
Testing the new Content Context endpoints as requested in French review.

Test Flow:
1. POST /api/auth/login-robust - Authentication
2. GET /api/content/pending - Get existing content and identify content_id
3. PUT /api/content/{content_id}/context - Add context to content
4. GET /api/content/pending - Verify context was saved
5. PUT /api/content/{content_id}/context - Update context
6. DELETE /api/content/{content_id} - Test content deletion

Credentials: lperpere@yahoo.fr / L@Reunion974!
Backend URL: https://social-pub-hub.preview.emergentagent.com/api
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://social-pub-hub.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class ContentContextTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.test_results = []
        
    def log_test(self, step, description, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "step": step,
            "description": description,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} Step {step}: {description}")
        if details:
            print(f"    Details: {details}")
        return success
    
    def test_step_1_authentication(self):
        """Step 1: POST /api/auth/login-robust pour obtenir le token"""
        try:
            url = f"{BASE_URL}/auth/login-robust"
            payload = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                if self.access_token and self.user_id:
                    # Set authorization header for future requests
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.access_token}"
                    })
                    return self.log_test(1, "Authentication successful", True, 
                                       f"User ID: {self.user_id}, Token obtained")
                else:
                    return self.log_test(1, "Authentication failed", False, 
                                       "Missing access_token or user_id in response")
            else:
                return self.log_test(1, "Authentication failed", False, 
                                   f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            return self.log_test(1, "Authentication failed", False, f"Exception: {str(e)}")
    
    def test_step_2_get_existing_content(self):
        """Step 2: GET /api/content/pending pour voir les contenus existants"""
        try:
            url = f"{BASE_URL}/content/pending"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                total = data.get("total", 0)
                
                if content_items:
                    # Store first content item for testing
                    self.test_content_id = content_items[0].get("id")
                    self.test_content_filename = content_items[0].get("filename", "unknown")
                    
                    return self.log_test(2, "Content retrieval successful", True, 
                                       f"Found {len(content_items)} items, Total: {total}, Test content ID: {self.test_content_id}")
                else:
                    return self.log_test(2, "No content found", False, 
                                       "No content items available for testing")
            else:
                return self.log_test(2, "Content retrieval failed", False, 
                                   f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            return self.log_test(2, "Content retrieval failed", False, f"Exception: {str(e)}")
    
    def test_step_3_add_context(self):
        """Step 3: PUT /api/content/{content_id}/context - Ajouter contexte"""
        try:
            if not hasattr(self, 'test_content_id'):
                return self.log_test(3, "Add context failed", False, "No content ID available from step 2")
            
            url = f"{BASE_URL}/content/{self.test_content_id}/context"
            payload = {
                "context": "Test contexte pour cette image - description et mots-clés"
            }
            
            response = self.session.put(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                return self.log_test(3, "Context addition successful", True, 
                                   f"Response: {message}")
            else:
                return self.log_test(3, "Context addition failed", False, 
                                   f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            return self.log_test(3, "Context addition failed", False, f"Exception: {str(e)}")
    
    def test_step_4_verify_context_saved(self):
        """Step 4: GET /api/content/pending à nouveau pour vérifier sauvegarde"""
        try:
            url = f"{BASE_URL}/content/pending"
            response = self.session.get(url)
            
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
                    context = test_item.get("context", "")
                    description = test_item.get("description", "")
                    
                    # Check if context was saved (could be in 'context' or 'description' field)
                    if "Test contexte pour cette image" in context or "Test contexte pour cette image" in description:
                        return self.log_test(4, "Context verification successful", True, 
                                           f"Context found in database: {context or description}")
                    else:
                        return self.log_test(4, "Context verification failed", False, 
                                           f"Context not found. Context: '{context}', Description: '{description}'")
                else:
                    return self.log_test(4, "Context verification failed", False, 
                                       f"Test content item {self.test_content_id} not found")
            else:
                return self.log_test(4, "Context verification failed", False, 
                                   f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            return self.log_test(4, "Context verification failed", False, f"Exception: {str(e)}")
    
    def test_step_5_update_context(self):
        """Step 5: PUT /api/content/{content_id}/context avec contexte différent"""
        try:
            if not hasattr(self, 'test_content_id'):
                return self.log_test(5, "Context update failed", False, "No content ID available")
            
            url = f"{BASE_URL}/content/{self.test_content_id}/context"
            payload = {
                "context": "Contexte modifié - nouvelles informations"
            }
            
            response = self.session.put(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                return self.log_test(5, "Context update successful", True, 
                                   f"Response: {message}")
            else:
                return self.log_test(5, "Context update failed", False, 
                                   f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            return self.log_test(5, "Context update failed", False, f"Exception: {str(e)}")
    
    def test_step_6_delete_content(self):
        """Step 6: DELETE /api/content/{content_id} pour tester la suppression"""
        try:
            if not hasattr(self, 'test_content_id'):
                return self.log_test(6, "Content deletion failed", False, "No content ID available")
            
            url = f"{BASE_URL}/content/{self.test_content_id}"
            response = self.session.delete(url)
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                return self.log_test(6, "Content deletion successful", True, 
                                   f"Response: {message}")
            else:
                return self.log_test(6, "Content deletion failed", False, 
                                   f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            return self.log_test(6, "Content deletion failed", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all Content Context endpoint tests"""
        print("🎯 CONTENT CONTEXT ENDPOINTS TESTING STARTED")
        print(f"Backend URL: {BASE_URL}")
        print(f"Test credentials: {TEST_EMAIL}")
        print("=" * 80)
        
        # Run tests in sequence
        tests = [
            self.test_step_1_authentication,
            self.test_step_2_get_existing_content,
            self.test_step_3_add_context,
            self.test_step_4_verify_context_saved,
            self.test_step_5_update_context,
            self.test_step_6_delete_content
        ]
        
        passed = 0
        total = len(tests)
        
        for test_func in tests:
            if test_func():
                passed += 1
            print()  # Add spacing between tests
        
        # Summary
        print("=" * 80)
        print(f"🎯 CONTENT CONTEXT ENDPOINTS TESTING COMPLETED")
        print(f"Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}% success rate)")
        
        if passed == total:
            print("✅ ALL TESTS PASSED - Content Context endpoints are fully functional")
        else:
            print("❌ SOME TESTS FAILED - Issues found with Content Context endpoints")
        
        return passed, total, self.test_results

def main():
    """Main test execution"""
    tester = ContentContextTester()
    passed, total, results = tester.run_all_tests()
    
    # Return appropriate exit code
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()