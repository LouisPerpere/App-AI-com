#!/usr/bin/env python3
"""
Business Profile Save Functions Testing - French Review Request
Testing PUT /api/business-profile and GET /api/business-profile endpoints
with specific test data for Claire et Marcus business profile functionality
"""

import requests
import json
import time

# Configuration - Using the correct backend URL from frontend/.env
BACKEND_URL = "https://social-ai-planner-2.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials as specified in review request
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

# Specific test data from review request
TEST_BUSINESS_DATA = {
    "business_name": "Claire et Marcus Test",
    "business_type": "Agence SaaS", 
    "business_description": "Automatisation social media avec IA",
    "brand_tone": "professionnel",
    "email": "test@claireetmarcus.com",
    "website_url": "https://test.claireetmarcus.com",
    "target_audience": "PME 25-50 ans, entrepreneurs"
}

class BusinessProfileTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()
    
    def authenticate(self):
        """Step 1: Authenticate with specified credentials"""
        print("🔐 STEP 1: Authentication")
        print("=" * 50)
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login-robust", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                self.log_result(
                    "Authentication", 
                    True, 
                    f"Successfully authenticated as {TEST_EMAIL}, User ID: {self.user_id}"
                )
                return True
            else:
                self.log_result(
                    "Authentication", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, error=str(e))
            return False
    
    def test_get_business_profile_initial(self):
        """Step 2: Get initial business profile state"""
        print("📋 STEP 2: Get Initial Business Profile")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{API_BASE}/business-profile")
            
            if response.status_code == 200:
                data = response.json()
                
                # Store initial state for comparison
                self.initial_profile = data
                
                # Check which fields are already populated
                populated_fields = [k for k, v in data.items() if v is not None and v != ""]
                empty_fields = [k for k, v in data.items() if v is None or v == ""]
                
                self.log_result(
                    "Get Initial Business Profile", 
                    True, 
                    f"Retrieved profile. Populated fields: {len(populated_fields)}, Empty fields: {len(empty_fields)}. Populated: {populated_fields[:5]}..."
                )
                return True
            else:
                self.log_result(
                    "Get Initial Business Profile", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Get Initial Business Profile", False, error=str(e))
            return False
    
    def test_put_business_profile_complete(self):
        """Step 3: Test PUT /api/business-profile with complete test data"""
        print("💾 STEP 3: PUT Business Profile - Complete Data")
        print("=" * 50)
        
        try:
            response = self.session.put(f"{API_BASE}/business-profile", json=TEST_BUSINESS_DATA)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                
                if success:
                    self.log_result(
                        "PUT Business Profile - Complete Data", 
                        True, 
                        f"Successfully saved complete business profile. Fields saved: {list(TEST_BUSINESS_DATA.keys())}"
                    )
                    return True
                else:
                    self.log_result(
                        "PUT Business Profile - Complete Data", 
                        False, 
                        "API returned success=false",
                        data.get("message", "No message provided")
                    )
                    return False
            else:
                self.log_result(
                    "PUT Business Profile - Complete Data", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("PUT Business Profile - Complete Data", False, error=str(e))
            return False
    
    def test_get_business_profile_verification(self):
        """Step 4: Verify data persistence by retrieving saved data"""
        print("🔍 STEP 4: Verify Data Persistence")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{API_BASE}/business-profile")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify each field was saved correctly
                verification_results = {}
                all_correct = True
                
                for field, expected_value in TEST_BUSINESS_DATA.items():
                    actual_value = data.get(field)
                    is_correct = actual_value == expected_value
                    verification_results[field] = {
                        "expected": expected_value,
                        "actual": actual_value,
                        "correct": is_correct
                    }
                    if not is_correct:
                        all_correct = False
                
                # Count correct fields
                correct_count = sum(1 for result in verification_results.values() if result["correct"])
                total_count = len(verification_results)
                
                # Detailed verification report
                details = f"Data persistence verification: {correct_count}/{total_count} fields correct. "
                
                # Show first few field verifications
                sample_verifications = []
                for field, result in list(verification_results.items())[:3]:
                    status = "✅" if result["correct"] else "❌"
                    sample_verifications.append(f"{status} {field}: '{result['actual']}'")
                
                details += f"Sample: {', '.join(sample_verifications)}"
                
                if not all_correct:
                    # Show incorrect fields
                    incorrect_fields = [f for f, r in verification_results.items() if not r["correct"]]
                    details += f". Incorrect fields: {incorrect_fields}"
                
                self.log_result(
                    "Verify Data Persistence", 
                    all_correct, 
                    details,
                    "" if all_correct else f"Some fields not saved correctly: {incorrect_fields}"
                )
                
                # Store verification results for summary
                self.verification_results = verification_results
                
                return all_correct
            else:
                self.log_result(
                    "Verify Data Persistence", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Verify Data Persistence", False, error=str(e))
            return False
    
    def test_put_business_profile_partial(self):
        """Step 5: Test PUT /api/business-profile with partial data"""
        print("📝 STEP 5: PUT Business Profile - Partial Data")
        print("=" * 50)
        
        # Test with only a few fields
        partial_data = {
            "business_name": "Claire et Marcus Test - Updated",
            "brand_tone": "luxe"
        }
        
        try:
            response = self.session.put(f"{API_BASE}/business-profile", json=partial_data)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                
                if success:
                    # Verify the partial update worked
                    verify_response = self.session.get(f"{API_BASE}/business-profile")
                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        
                        # Check if partial fields were updated
                        name_updated = verify_data.get("business_name") == partial_data["business_name"]
                        tone_updated = verify_data.get("brand_tone") == partial_data["brand_tone"]
                        
                        # Check if other fields remained unchanged
                        email_unchanged = verify_data.get("email") == TEST_BUSINESS_DATA["email"]
                        
                        partial_success = name_updated and tone_updated and email_unchanged
                        
                        self.log_result(
                            "PUT Business Profile - Partial Data", 
                            partial_success, 
                            f"Partial update test. Name updated: {name_updated}, Tone updated: {tone_updated}, Email unchanged: {email_unchanged}"
                        )
                        return partial_success
                    else:
                        self.log_result(
                            "PUT Business Profile - Partial Data", 
                            False, 
                            "Could not verify partial update"
                        )
                        return False
                else:
                    self.log_result(
                        "PUT Business Profile - Partial Data", 
                        False, 
                        "API returned success=false",
                        data.get("message", "No message provided")
                    )
                    return False
            else:
                self.log_result(
                    "PUT Business Profile - Partial Data", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("PUT Business Profile - Partial Data", False, error=str(e))
            return False
    
    def test_brand_tone_validation(self):
        """Step 6: Test brand_tone dropdown values validation"""
        print("🎨 STEP 6: Brand Tone Validation")
        print("=" * 50)
        
        # Test different brand_tone values from dropdown
        brand_tones_to_test = ["professionnel", "luxe", "simple", "créatif", "amical"]
        
        successful_tones = []
        failed_tones = []
        
        for tone in brand_tones_to_test:
            try:
                test_data = {"brand_tone": tone}
                response = self.session.put(f"{API_BASE}/business-profile", json=test_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success", False):
                        # Verify it was actually saved
                        verify_response = self.session.get(f"{API_BASE}/business-profile")
                        if verify_response.status_code == 200:
                            verify_data = verify_response.json()
                            if verify_data.get("brand_tone") == tone:
                                successful_tones.append(tone)
                            else:
                                failed_tones.append(f"{tone} (not saved)")
                        else:
                            failed_tones.append(f"{tone} (verify failed)")
                    else:
                        failed_tones.append(f"{tone} (success=false)")
                else:
                    failed_tones.append(f"{tone} (status {response.status_code})")
                    
            except Exception as e:
                failed_tones.append(f"{tone} (error: {str(e)[:30]})")
        
        success_count = len(successful_tones)
        total_count = len(brand_tones_to_test)
        all_successful = success_count == total_count
        
        details = f"Brand tone validation: {success_count}/{total_count} tones accepted. "
        details += f"Successful: {successful_tones}. "
        if failed_tones:
            details += f"Failed: {failed_tones}"
        
        self.log_result(
            "Brand Tone Validation", 
            all_successful, 
            details,
            "" if all_successful else f"Some brand tones failed: {failed_tones}"
        )
        
        return all_successful
    
    def test_health_check(self):
        """Step 0: Health check to ensure backend is accessible"""
        print("🏥 STEP 0: Backend Health Check")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{API_BASE}/health")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                service = data.get("service")
                
                self.log_result(
                    "Backend Health Check", 
                    status == "healthy", 
                    f"Backend status: {status}, Service: {service}"
                )
                return status == "healthy"
            else:
                self.log_result(
                    "Backend Health Check", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Backend Health Check", False, error=str(e))
            return False
    
    def run_all_tests(self):
        """Run all business profile tests"""
        print("🚀 BUSINESS PROFILE SAVE FUNCTIONS TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_EMAIL}")
        print(f"Test Data: {TEST_BUSINESS_DATA}")
        print("=" * 60)
        print()
        
        # Initialize test variables
        self.initial_profile = None
        self.verification_results = None
        
        # Run tests in sequence
        tests = [
            self.test_health_check,
            self.authenticate,
            self.test_get_business_profile_initial,
            self.test_put_business_profile_complete,
            self.test_get_business_profile_verification,
            self.test_put_business_profile_partial,
            self.test_brand_tone_validation
        ]
        
        for test in tests:
            if not test():
                print("❌ Test failed, continuing with remaining tests...")
            print()
        
        # Summary
        print("📋 TEST SUMMARY - BUSINESS PROFILE SAVE FUNCTIONS")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Detailed results
        print("DETAILED TEST RESULTS:")
        print("-" * 40)
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
            if result['error']:
                print(f"   Error: {result['error']}")
        
        # Field-by-field verification summary if available
        if hasattr(self, 'verification_results') and self.verification_results:
            print()
            print("FIELD VERIFICATION DETAILS:")
            print("-" * 40)
            for field, result in self.verification_results.items():
                status = "✅" if result["correct"] else "❌"
                print(f"{status} {field}: Expected '{result['expected']}', Got '{result['actual']}'")
        
        print()
        print("🎯 BUSINESS PROFILE TESTING COMPLETED")
        
        return success_rate >= 85  # High threshold for business profile functionality

if __name__ == "__main__":
    tester = BusinessProfileTester()
    success = tester.run_all_tests()
    
    if success:
        print("✅ Overall testing: SUCCESS")
        exit(0)
    else:
        print("❌ Overall testing: FAILED")
        exit(1)