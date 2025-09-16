#!/usr/bin/env python3
"""
CRITICAL PERSISTENCE VALIDATION TEST - Async/Sync Corrections
Testing the specific fixes applied to resolve database persistence issues:
1. business_objective persistence after PUT operations
2. website analysis persistence in MongoDB
3. Verification of async/sync corrections

CONTEXTE CRITIQUE:
Corrections appliquées pour résoudre le problème systémique de persistance base de données :
1. ✅ website_analyzer_gpt5.py ligne 1753 : await dbp.website_analyses.insert_one() → dbp.db.website_analyses.insert_one()
2. ✅ server.py ligne 593 : async def put_business_profile() → def put_business_profile() (synchrone)
3. ✅ server.py ligne 609 : Appel cohérent sans await sur fonction synchrone

CREDENTIALS DE TEST:
- Email: mara.alexandra@gmail.com (utilisateur ayant reporté le problème)
- Password: password123
- URL: https://insta-automate-2.preview.emergentagent.com/api
"""

import requests
import json
import time
import sys
from datetime import datetime

# Test configuration
BASE_URL = "https://insta-automate-2.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "mara.alexandra@gmail.com",
    "password": "password123"
}

class PersistenceValidator:
    def __init__(self):
        self.session = requests.Session()
        self.user_id = None
        self.access_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def authenticate(self):
        """Step 1: Authenticate with test credentials"""
        print(f"\n🔐 STEP 1: Authentication with {TEST_CREDENTIALS['email']}")
        
        try:
            response = self.session.post(
                f"{BASE_URL}/auth/login-robust",
                json=TEST_CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for all future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                self.log_test("Authentication", True, f"User ID: {self.user_id}")
                return True
            else:
                self.log_test("Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_business_objective_persistence(self):
        """Step 2: Test business_objective persistence - CRITICAL TEST"""
        print(f"\n📊 STEP 2: Testing business_objective persistence (CRITICAL)")
        
        try:
            # Get initial business profile state
            print("   📋 Getting initial business profile state...")
            initial_response = self.session.get(f"{BASE_URL}/business-profile", timeout=30)
            
            if initial_response.status_code != 200:
                self.log_test("Business Profile Initial State", False, f"Status: {initial_response.status_code}")
                return False
            
            initial_data = initial_response.json()
            initial_objective = initial_data.get("business_objective")
            print(f"   📋 Initial business_objective: {initial_objective}")
            
            # Test 1: Save business_objective to "communaute"
            print("   💾 Saving business_objective to 'communaute'...")
            save_response = self.session.put(
                f"{BASE_URL}/business-profile",
                json={"business_objective": "communaute"},
                timeout=30
            )
            
            if save_response.status_code != 200:
                self.log_test("Business Objective Save", False, f"Status: {save_response.status_code}, Response: {save_response.text}")
                return False
            
            save_data = save_response.json()
            if not save_data.get("success"):
                self.log_test("Business Objective Save", False, f"Save response: {save_data}")
                return False
            
            self.log_test("Business Objective Save", True, "Successfully saved 'communaute'")
            
            # Test 2: Immediate verification
            print("   🔍 Immediate verification...")
            immediate_response = self.session.get(f"{BASE_URL}/business-profile", timeout=30)
            
            if immediate_response.status_code != 200:
                self.log_test("Immediate Verification", False, f"Status: {immediate_response.status_code}")
                return False
            
            immediate_data = immediate_response.json()
            immediate_objective = immediate_data.get("business_objective")
            
            if immediate_objective == "communaute":
                self.log_test("Immediate Verification", True, f"business_objective = '{immediate_objective}'")
            else:
                self.log_test("Immediate Verification", False, f"Expected 'communaute', got '{immediate_objective}'")
                return False
            
            # Test 3: Persistence after delay (simulate page reload)
            print("   ⏱️  Testing persistence after 10-second delay...")
            time.sleep(10)
            
            delayed_response = self.session.get(f"{BASE_URL}/business-profile", timeout=30)
            
            if delayed_response.status_code != 200:
                self.log_test("Delayed Persistence", False, f"Status: {delayed_response.status_code}")
                return False
            
            delayed_data = delayed_response.json()
            delayed_objective = delayed_data.get("business_objective")
            
            if delayed_objective == "communaute":
                self.log_test("Delayed Persistence", True, f"business_objective still = '{delayed_objective}' after 10s")
            else:
                self.log_test("Delayed Persistence", False, f"PERSISTENCE FAILURE: Expected 'communaute', got '{delayed_objective}' after delay")
                return False
            
            # Test 4: Multiple consecutive GET requests to verify consistency
            print("   🔄 Testing consistency across multiple requests...")
            consistent = True
            for i in range(3):
                check_response = self.session.get(f"{BASE_URL}/business-profile", timeout=30)
                if check_response.status_code == 200:
                    check_data = check_response.json()
                    check_objective = check_data.get("business_objective")
                    if check_objective != "communaute":
                        consistent = False
                        break
                else:
                    consistent = False
                    break
                time.sleep(2)
            
            if consistent:
                self.log_test("Consistency Check", True, "business_objective consistent across multiple requests")
            else:
                self.log_test("Consistency Check", False, "business_objective inconsistent across requests")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Business Objective Persistence", False, f"Exception: {str(e)}")
            return False
    
    def test_website_analysis_persistence(self):
        """Step 3: Test website analysis persistence"""
        print(f"\n🌐 STEP 3: Testing website analysis persistence")
        
        try:
            test_url = "https://myownwatch.fr"
            print(f"   🔍 Analyzing website: {test_url}")
            
            # Start website analysis
            analysis_response = self.session.post(
                f"{BASE_URL}/website/analyze",
                json={"url": test_url},
                timeout=60  # Website analysis can take time
            )
            
            if analysis_response.status_code != 200:
                self.log_test("Website Analysis", False, f"Status: {analysis_response.status_code}, Response: {analysis_response.text}")
                return False
            
            analysis_data = analysis_response.json()
            
            # Check if analysis completed successfully
            if not analysis_data.get("analysis_summary"):
                self.log_test("Website Analysis", False, "No analysis_summary in response")
                return False
            
            # Check for required fields indicating successful save
            required_fields = ["created_at", "updated_at"]
            missing_fields = [field for field in required_fields if not analysis_data.get(field)]
            
            if missing_fields:
                self.log_test("Website Analysis Fields", False, f"Missing fields: {missing_fields}")
            else:
                self.log_test("Website Analysis Fields", True, "All required timestamp fields present")
            
            self.log_test("Website Analysis", True, f"Analysis completed successfully for {test_url}")
            
            # Test persistence by retrieving analysis
            print("   📋 Verifying analysis persistence...")
            time.sleep(10)  # Wait to simulate page reload
            
            retrieval_response = self.session.get(f"{BASE_URL}/website/analysis", timeout=30)
            
            if retrieval_response.status_code == 200:
                retrieval_data = retrieval_response.json()
                if retrieval_data and len(retrieval_data) > 0:
                    self.log_test("Analysis Persistence", True, "Analysis retrieved from database after delay")
                else:
                    self.log_test("Analysis Persistence", False, "No analysis found in database")
                    return False
            else:
                self.log_test("Analysis Persistence", False, f"Failed to retrieve analysis: {retrieval_response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Website Analysis Persistence", False, f"Exception: {str(e)}")
            return False
    
    def test_save_logs_verification(self):
        """Step 4: Test for successful save logs"""
        print(f"\n📝 STEP 4: Verifying save operation logs")
        
        # This is a conceptual test - in a real environment we'd check server logs
        # For now, we verify that our previous operations succeeded without errors
        
        success_indicators = [
            "Authentication successful",
            "Business objective saved and persisted",
            "Website analysis completed and saved"
        ]
        
        failed_tests = [result for result in self.test_results if not result["success"]]
        
        if not failed_tests:
            self.log_test("Save Logs Verification", True, "All save operations completed without errors")
            return True
        else:
            self.log_test("Save Logs Verification", False, f"Found {len(failed_tests)} failed operations")
            return False
    
    def run_comprehensive_test(self):
        """Run all persistence validation tests"""
        print("🚀 STARTING CRITICAL PERSISTENCE VALIDATION TESTS")
        print("=" * 60)
        print("Testing async/sync corrections for database persistence")
        print(f"Backend URL: {BASE_URL}")
        print(f"Test User: {TEST_CREDENTIALS['email']}")
        print("=" * 60)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ CRITICAL FAILURE: Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Business objective persistence (CRITICAL)
        if not self.test_business_objective_persistence():
            print("\n❌ CRITICAL FAILURE: Business objective persistence failed")
            return False
        
        # Step 3: Website analysis persistence
        if not self.test_website_analysis_persistence():
            print("\n❌ CRITICAL FAILURE: Website analysis persistence failed")
            return False
        
        # Step 4: Save logs verification
        self.test_save_logs_verification()
        
        # Summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🎯 PERSISTENCE VALIDATION TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   - {result['test']}: {result['details']}")
        
        print("\n🔍 CRITICAL FINDINGS:")
        if passed_tests == total_tests:
            print("✅ ALL PERSISTENCE CORRECTIONS WORKING CORRECTLY")
            print("✅ business_objective persistence: RESOLVED")
            print("✅ Website analysis persistence: RESOLVED") 
            print("✅ Async/sync database issues: RESOLVED")
        else:
            print("❌ PERSISTENCE ISSUES STILL PRESENT")
            print("❌ Async/sync corrections may need additional work")
        
        print("=" * 60)

def main():
    """Main test execution"""
    validator = PersistenceValidator()
    
    try:
        success = validator.run_comprehensive_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()