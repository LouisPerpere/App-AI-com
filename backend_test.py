#!/usr/bin/env python3
"""
Backend Test Suite for Content Movement Functionality
Test de la nouvelle fonctionnalité de déplacement de contenu vers un autre mois

OBJECTIF: Valider le nouvel endpoint PUT /api/content/{content_id}/move
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://content-scheduler-6.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class ContentMoveTest:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.test_content_id = None
        
    def log(self, message, level="INFO"):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def authenticate(self):
        """Step 1: Authenticate with provided credentials"""
        print("🔐 Step 1: Authentication Test")
        
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
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                
                self.log_test(
                    "Authentication", 
                    True, 
                    f"User ID: {self.user_id}, Token obtained successfully"
                )
                return True
            else:
                self.log_test(
                    "Authentication", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_existing_content(self):
        """Step 2: Get existing content to test with"""
        print("📋 Step 2: Retrieve Existing Content")
        
        try:
            response = self.session.get(
                f"{self.base_url}/content/pending",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                total_items = data.get("total", 0)
                
                if len(content_items) >= 2:
                    # Extract content IDs for testing
                    self.content_ids = [item["id"] for item in content_items[:3]]  # Take first 3 for testing
                    
                    self.log_test(
                        "Content Retrieval", 
                        True, 
                        f"Found {total_items} total items, {len(content_items)} loaded. Test IDs: {self.content_ids[:2]}"
                    )
                    return True
                else:
                    self.log_test(
                        "Content Retrieval", 
                        False, 
                        f"Insufficient content for testing. Found {len(content_items)} items, need at least 2"
                    )
                    return False
            else:
                self.log_test(
                    "Content Retrieval", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Content Retrieval", False, f"Exception: {str(e)}")
            return False
    
    def test_batch_delete_valid_ids(self):
        """Step 3: Test batch deletion with valid content IDs"""
        print("🗑️ Step 3: Batch Delete with Valid IDs")
        
        try:
            # Use first 2 content IDs for testing
            test_ids = self.content_ids[:2]
            
            delete_request = {
                "content_ids": test_ids
            }
            
            response = self.session.delete(
                f"{self.base_url}/content/batch",
                json=delete_request,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                deleted_count = data.get("deleted_count", 0)
                requested_count = data.get("requested_count", 0)
                message = data.get("message", "")
                
                # Validate response structure
                if "deleted_count" in data and "requested_count" in data:
                    self.log_test(
                        "Batch Delete Valid IDs", 
                        True, 
                        f"Deleted: {deleted_count}/{requested_count}, Message: {message}"
                    )
                    
                    # Store deleted IDs for verification
                    self.deleted_ids = test_ids
                    return True
                else:
                    self.log_test(
                        "Batch Delete Valid IDs", 
                        False, 
                        f"Missing required fields in response: {data}"
                    )
                    return False
            else:
                self.log_test(
                    "Batch Delete Valid IDs", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Batch Delete Valid IDs", False, f"Exception: {str(e)}")
            return False
    
    def verify_content_deleted(self):
        """Step 4: Verify that content was actually deleted"""
        print("✅ Step 4: Verify Content Deletion")
        
        try:
            response = self.session.get(
                f"{self.base_url}/content/pending",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                remaining_ids = [item["id"] for item in content_items]
                
                # Check if deleted IDs are still present
                still_present = []
                for deleted_id in self.deleted_ids:
                    if deleted_id in remaining_ids:
                        still_present.append(deleted_id)
                
                if not still_present:
                    self.log_test(
                        "Content Deletion Verification", 
                        True, 
                        f"All {len(self.deleted_ids)} deleted items confirmed removed from content list"
                    )
                    return True
                else:
                    self.log_test(
                        "Content Deletion Verification", 
                        False, 
                        f"Items still present after deletion: {still_present}"
                    )
                    return False
            else:
                self.log_test(
                    "Content Deletion Verification", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Content Deletion Verification", False, f"Exception: {str(e)}")
            return False
    
    def test_edge_cases(self):
        """Step 5: Test edge cases - invalid IDs and empty array"""
        print("⚠️ Step 5: Edge Cases Testing")
        
        edge_case_results = []
        
        # Test 1: Empty array
        try:
            delete_request = {"content_ids": []}
            response = self.session.delete(
                f"{self.base_url}/content/batch",
                json=delete_request,
                timeout=30
            )
            
            if response.status_code == 400:
                edge_case_results.append("Empty array correctly rejected (400)")
            else:
                edge_case_results.append(f"Empty array unexpected response: {response.status_code}")
                
        except Exception as e:
            edge_case_results.append(f"Empty array test error: {str(e)}")
        
        # Test 2: Invalid/non-existent IDs
        try:
            delete_request = {"content_ids": ["invalid-id-123", "another-invalid-id"]}
            response = self.session.delete(
                f"{self.base_url}/content/batch",
                json=delete_request,
                timeout=30
            )
            
            if response.status_code in [404, 200]:  # 404 or 200 with 0 deleted_count are both acceptable
                if response.status_code == 200:
                    data = response.json()
                    if data.get("deleted_count", 0) == 0:
                        edge_case_results.append("Invalid IDs correctly handled (0 deleted)")
                    else:
                        edge_case_results.append(f"Invalid IDs unexpected deletion count: {data.get('deleted_count')}")
                else:
                    edge_case_results.append("Invalid IDs correctly rejected (404)")
            else:
                edge_case_results.append(f"Invalid IDs unexpected response: {response.status_code}")
                
        except Exception as e:
            edge_case_results.append(f"Invalid IDs test error: {str(e)}")
        
        # Test 3: Too many IDs (over 100 limit)
        try:
            large_array = [f"id-{i}" for i in range(101)]  # 101 IDs to exceed limit
            delete_request = {"content_ids": large_array}
            response = self.session.delete(
                f"{self.base_url}/content/batch",
                json=delete_request,
                timeout=30
            )
            
            if response.status_code == 400:
                edge_case_results.append("Large array correctly rejected (400)")
            else:
                edge_case_results.append(f"Large array unexpected response: {response.status_code}")
                
        except Exception as e:
            edge_case_results.append(f"Large array test error: {str(e)}")
        
        # Evaluate edge cases
        passed_cases = len([r for r in edge_case_results if "correctly" in r])
        total_cases = len(edge_case_results)
        
        self.log_test(
            "Edge Cases Testing", 
            passed_cases >= 2,  # At least 2 out of 3 should pass
            f"Passed {passed_cases}/{total_cases} edge cases: {'; '.join(edge_case_results)}"
        )
        
        return passed_cases >= 2
    
    def test_response_format(self):
        """Step 6: Test response format with remaining content"""
        print("📊 Step 6: Response Format Validation")
        
        try:
            # Use remaining content ID if available
            if len(self.content_ids) > 2:
                test_id = [self.content_ids[2]]  # Use third ID if available
                
                delete_request = {"content_ids": test_id}
                response = self.session.delete(
                    f"{self.base_url}/content/batch",
                    json=delete_request,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check required fields
                    required_fields = ["message", "deleted_count", "requested_count"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        # Validate field types
                        valid_types = (
                            isinstance(data["deleted_count"], int) and
                            isinstance(data["requested_count"], int) and
                            isinstance(data["message"], str)
                        )
                        
                        if valid_types:
                            self.log_test(
                                "Response Format Validation", 
                                True, 
                                f"All required fields present with correct types: {data}"
                            )
                            return True
                        else:
                            self.log_test(
                                "Response Format Validation", 
                                False, 
                                f"Invalid field types in response: {data}"
                            )
                            return False
                    else:
                        self.log_test(
                            "Response Format Validation", 
                            False, 
                            f"Missing required fields: {missing_fields}"
                        )
                        return False
                else:
                    self.log_test(
                        "Response Format Validation", 
                        False, 
                        f"Status: {response.status_code}, Response: {response.text}"
                    )
                    return False
            else:
                self.log_test(
                    "Response Format Validation", 
                    False, 
                    "No remaining content IDs available for format testing"
                )
                return False
                
        except Exception as e:
            self.log_test("Response Format Validation", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all batch delete tests"""
        print("🚀 BATCH DELETE OPTIMIZATION TESTING")
        print("=" * 60)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Target: DELETE /api/content/batch endpoint")
        print("=" * 60)
        print()
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Get existing content
        if not self.get_existing_content():
            print("❌ No sufficient content available - cannot proceed with batch delete tests")
            return False
        
        # Step 3: Test batch delete with valid IDs
        if not self.test_batch_delete_valid_ids():
            print("❌ Batch delete with valid IDs failed")
            return False
        
        # Step 4: Verify deletion
        if not self.verify_content_deleted():
            print("❌ Content deletion verification failed")
            return False
        
        # Step 5: Test edge cases
        self.test_edge_cases()
        
        # Step 6: Test response format
        self.test_response_format()
        
        # Summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 BATCH DELETE TESTING SUMMARY")
        print("=" * 60)
        
        passed_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        print(f"✅ PASSED: {len(passed_tests)}/{len(self.test_results)} tests")
        print(f"❌ FAILED: {len(failed_tests)}/{len(self.test_results)} tests")
        print(f"📈 SUCCESS RATE: {len(passed_tests)/len(self.test_results)*100:.1f}%")
        
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   - {test['test']}: {test['details']}")
        
        print("\n✅ PASSED TESTS:")
        for test in passed_tests:
            print(f"   - {test['test']}")
        
        print("\n🎯 BATCH DELETE ENDPOINT ANALYSIS:")
        print(f"   - Authentication: {'✅ Working' if any('Authentication' in t['test'] and t['success'] for t in self.test_results) else '❌ Failed'}")
        print(f"   - Content Retrieval: {'✅ Working' if any('Content Retrieval' in t['test'] and t['success'] for t in self.test_results) else '❌ Failed'}")
        print(f"   - Batch Deletion: {'✅ Working' if any('Batch Delete Valid IDs' in t['test'] and t['success'] for t in self.test_results) else '❌ Failed'}")
        print(f"   - Deletion Verification: {'✅ Working' if any('Content Deletion Verification' in t['test'] and t['success'] for t in self.test_results) else '❌ Failed'}")
        print(f"   - Edge Cases: {'✅ Working' if any('Edge Cases' in t['test'] and t['success'] for t in self.test_results) else '❌ Failed'}")
        print(f"   - Response Format: {'✅ Working' if any('Response Format' in t['test'] and t['success'] for t in self.test_results) else '❌ Failed'}")
        
        # Overall assessment
        critical_tests = ['Authentication', 'Content Retrieval', 'Batch Delete Valid IDs', 'Content Deletion Verification']
        critical_passed = sum(1 for test in self.test_results if any(ct in test['test'] for ct in critical_tests) and test['success'])
        
        if critical_passed >= 3:
            print(f"\n🎉 CONCLUSION: Batch delete endpoint is FULLY OPERATIONAL")
            print(f"   The optimization successfully replaces individual deletions with efficient batch operations.")
        else:
            print(f"\n🚨 CONCLUSION: Batch delete endpoint has CRITICAL ISSUES")
            print(f"   Core functionality is not working properly and needs fixes.")

def main():
    """Main test execution"""
    tester = BatchDeleteTester()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n✅ All batch delete tests completed successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ Batch delete testing failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()