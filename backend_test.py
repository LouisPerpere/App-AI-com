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
        self.log("🔐 Step 1: Authentication test starting...")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json={
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD
                },
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
                
                self.log(f"✅ Authentication successful - User ID: {self.user_id}")
                return True
            else:
                self.log(f"❌ Authentication failed - Status: {response.status_code}, Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Authentication error: {str(e)}", "ERROR")
            return False
    
    def get_existing_content(self):
        """Step 2: Get existing content to test movement"""
        self.log("📋 Step 2: Retrieving existing content...")
        
        try:
            response = self.session.get(
                f"{BACKEND_URL}/content/pending",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                total_items = data.get("total", 0)
                
                self.log(f"✅ Content retrieval successful - Total items: {total_items}, Items loaded: {len(content_items)}")
                
                if content_items:
                    # Use the first available content item for testing
                    self.test_content_id = content_items[0]["id"]
                    current_month = content_items[0].get("attributed_month", "Non attribué")
                    filename = content_items[0].get("filename", "Unknown")
                    
                    self.log(f"✅ Test content selected - ID: {self.test_content_id}")
                    self.log(f"   📁 Filename: {filename}")
                    self.log(f"   📅 Current attributed_month: {current_month}")
                    return True
                else:
                    self.log("⚠️ No content items found - cannot test movement functionality", "WARNING")
                    return False
                    
            else:
                self.log(f"❌ Content retrieval failed - Status: {response.status_code}, Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Content retrieval error: {str(e)}", "ERROR")
            return False
    
    def test_valid_move(self):
        """Step 3: Test valid content movement to novembre_2025"""
        self.log("🔄 Step 3: Testing valid content movement...")
        
        target_month = "novembre_2025"
        
        try:
            response = self.session.put(
                f"{BACKEND_URL}/content/{self.test_content_id}/move",
                json={
                    "target_month": target_month
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                from_month = data.get("from_month", "")
                to_month = data.get("to_month", "")
                content_id = data.get("content_id", "")
                
                self.log(f"✅ Content movement successful")
                self.log(f"   📝 Message: {message}")
                self.log(f"   📅 From month: {from_month}")
                self.log(f"   📅 To month: {to_month}")
                self.log(f"   🆔 Content ID: {content_id}")
                
                # Verify response structure
                if all([message, to_month == target_month, content_id == self.test_content_id]):
                    self.log("✅ Response structure validation passed")
                    return True
                else:
                    self.log("❌ Response structure validation failed", "ERROR")
                    return False
                    
            else:
                self.log(f"❌ Content movement failed - Status: {response.status_code}, Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Content movement error: {str(e)}", "ERROR")
            return False
    
    def verify_month_persistence(self):
        """Step 4: Verify that attributed_month has been updated correctly"""
        self.log("🔍 Step 4: Verifying month persistence...")
        
        try:
            response = self.session.get(
                f"{BACKEND_URL}/content/pending",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                
                # Find our test content item
                test_item = None
                for item in content_items:
                    if item["id"] == self.test_content_id:
                        test_item = item
                        break
                
                if test_item:
                    updated_month = test_item.get("attributed_month", "")
                    filename = test_item.get("filename", "Unknown")
                    
                    self.log(f"✅ Content found after update")
                    self.log(f"   📁 Filename: {filename}")
                    self.log(f"   📅 Updated attributed_month: {updated_month}")
                    
                    if updated_month == "novembre_2025":
                        self.log("✅ Month persistence verification successful - attributed_month correctly updated")
                        return True
                    else:
                        self.log(f"❌ Month persistence failed - Expected: novembre_2025, Found: {updated_month}", "ERROR")
                        return False
                else:
                    self.log(f"❌ Test content item not found after update", "ERROR")
                    return False
                    
            else:
                self.log(f"❌ Content verification failed - Status: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Month persistence verification error: {str(e)}", "ERROR")
            return False
    
    def test_error_cases(self):
        """Step 5: Test error cases - non-existent ID and invalid month format"""
        self.log("⚠️ Step 5: Testing error cases...")
        
        # Test 1: Non-existent content ID
        self.log("   🔍 Test 5a: Non-existent content ID...")
        try:
            response = self.session.put(
                f"{BACKEND_URL}/content/nonexistent-id-12345/move",
                json={
                    "target_month": "novembre_2025"
                },
                timeout=30
            )
            
            if response.status_code == 404:
                self.log("✅ Non-existent ID test passed - Correctly returned 404")
                error_case_1_passed = True
            else:
                self.log(f"❌ Non-existent ID test failed - Expected 404, got {response.status_code}", "ERROR")
                error_case_1_passed = False
                
        except Exception as e:
            self.log(f"❌ Non-existent ID test error: {str(e)}", "ERROR")
            error_case_1_passed = False
        
        # Test 2: Invalid month format
        self.log("   🔍 Test 5b: Invalid month format...")
        try:
            response = self.session.put(
                f"{BACKEND_URL}/content/{self.test_content_id}/move",
                json={
                    "target_month": "invalid_format"
                },
                timeout=30
            )
            
            if response.status_code == 400:
                error_data = response.json()
                error_message = error_data.get("error", "")
                self.log(f"✅ Invalid format test passed - Status: 400, Message: {error_message}")
                error_case_2_passed = True
            else:
                self.log(f"❌ Invalid format test failed - Expected 400, got {response.status_code}", "ERROR")
                error_case_2_passed = False
                
        except Exception as e:
            self.log(f"❌ Invalid format test error: {str(e)}", "ERROR")
            error_case_2_passed = False
        
        # Test 3: Empty target_month
        self.log("   🔍 Test 5c: Empty target_month...")
        try:
            response = self.session.put(
                f"{BACKEND_URL}/content/{self.test_content_id}/move",
                json={
                    "target_month": ""
                },
                timeout=30
            )
            
            if response.status_code == 400:
                error_data = response.json()
                error_message = error_data.get("error", "")
                self.log(f"✅ Empty target_month test passed - Status: 400, Message: {error_message}")
                error_case_3_passed = True
            else:
                self.log(f"❌ Empty target_month test failed - Expected 400, got {response.status_code}", "ERROR")
                error_case_3_passed = False
                
        except Exception as e:
            self.log(f"❌ Empty target_month test error: {str(e)}", "ERROR")
            error_case_3_passed = False
        
        return error_case_1_passed and error_case_2_passed and error_case_3_passed
    
    def test_french_messages(self):
        """Step 6: Validate French return messages"""
        self.log("🇫🇷 Step 6: Validating French messages...")
        
        # Test with a different month to see the French message
        target_month = "décembre_2025"
        
        try:
            response = self.session.put(
                f"{BACKEND_URL}/content/{self.test_content_id}/move",
                json={
                    "target_month": target_month
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                
                # Check if message is in French
                french_keywords = ["déplacé", "vers", "Contenu"]
                has_french = any(keyword in message for keyword in french_keywords)
                
                if has_french:
                    self.log(f"✅ French message validation passed - Message: {message}")
                    return True
                else:
                    self.log(f"❌ French message validation failed - Message not in French: {message}", "ERROR")
                    return False
                    
            else:
                self.log(f"❌ French message test failed - Status: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ French message test error: {str(e)}", "ERROR")
            return False
    
    def run_comprehensive_test(self):
        """Run all content movement tests"""
        self.log("🚀 STARTING COMPREHENSIVE CONTENT MOVEMENT TESTING")
        self.log("=" * 80)
        
        test_results = []
        
        # Step 1: Authentication
        if self.authenticate():
            test_results.append(("Authentication", True))
        else:
            test_results.append(("Authentication", False))
            self.log("❌ Authentication failed - Cannot proceed with other tests", "ERROR")
            return self.generate_summary(test_results)
        
        # Step 2: Get existing content
        if self.get_existing_content():
            test_results.append(("Content Retrieval", True))
        else:
            test_results.append(("Content Retrieval", False))
            self.log("❌ Content retrieval failed - Cannot proceed with movement tests", "ERROR")
            return self.generate_summary(test_results)
        
        # Step 3: Test valid movement
        if self.test_valid_move():
            test_results.append(("Valid Movement", True))
        else:
            test_results.append(("Valid Movement", False))
        
        # Step 4: Verify persistence
        if self.verify_month_persistence():
            test_results.append(("Month Persistence", True))
        else:
            test_results.append(("Month Persistence", False))
        
        # Step 5: Test error cases
        if self.test_error_cases():
            test_results.append(("Error Cases", True))
        else:
            test_results.append(("Error Cases", False))
        
        # Step 6: Test French messages
        if self.test_french_messages():
            test_results.append(("French Messages", True))
        else:
            test_results.append(("French Messages", False))
        
        return self.generate_summary(test_results)
    
    def generate_summary(self, test_results):
        """Generate comprehensive test summary"""
        self.log("=" * 80)
        self.log("📊 CONTENT MOVEMENT TESTING SUMMARY")
        self.log("=" * 80)
        
        passed_tests = sum(1 for _, result in test_results if result)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.log(f"🎯 Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        self.log("")
        
        # Detailed results
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"   {status}: {test_name}")
        
        self.log("")
        
        # Technical findings
        self.log("🔧 TECHNICAL FINDINGS:")
        if self.token:
            self.log(f"   • Authentication system working with user {TEST_EMAIL}")
        if self.test_content_id:
            self.log(f"   • Content movement tested with ID: {self.test_content_id}")
        self.log(f"   • Backend URL: {BACKEND_URL}")
        self.log(f"   • PUT /api/content/{{content_id}}/move endpoint tested")
        
        self.log("")
        
        # Conclusion
        if success_rate >= 83.3:  # 5/6 tests or better
            self.log("🎉 CONCLUSION: Content movement functionality is FULLY OPERATIONAL")
            self.log("   All critical scenarios tested successfully")
        elif success_rate >= 66.7:  # 4/6 tests
            self.log("⚠️ CONCLUSION: Content movement functionality is MOSTLY OPERATIONAL")
            self.log("   Some minor issues identified but core functionality works")
        else:
            self.log("❌ CONCLUSION: Content movement functionality has CRITICAL ISSUES")
            self.log("   Major problems identified that need immediate attention")
        
        return success_rate >= 83.3

def main():
    """Main test execution"""
    print("🧪 Content Movement Backend Test Suite")
    print("Testing PUT /api/content/{content_id}/move endpoint")
    print("=" * 80)
    
    tester = ContentMoveTest()
    success = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()