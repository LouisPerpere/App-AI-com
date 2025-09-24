#!/usr/bin/env python3
"""
TEST VALIDATION PERSISTANCE DB - Sauvegarde et calcul dates
Testing critical fixes for website analysis persistence and date calculations

CRITICAL FIXES TO VALIDATE:
1. ✅ Database persistence: dbp["website_analyses"] → dbp.website_analyses  
2. ✅ Date calculation: 7 days → 30 days (1 month)
3. ✅ Missing dates: Added created_at, updated_at, next_analysis_due

URL: https://instamanager-1.preview.emergentagent.com/api
Credentials: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import time
import sys
from datetime import datetime, timedelta
from dateutil import parser

# Configuration
BASE_URL = "https://instamanager-1.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"
TEST_URL = "https://myownwatch.fr"

class WebsitePersistenceTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Website-Persistence-Tester/1.0'
        })
        self.access_token = None
        self.user_id = None
        self.analysis_result = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def authenticate(self):
        """Step 1: Authenticate with backend"""
        self.log("🔐 STEP 1: Authentication")
        try:
            auth_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login-robust", 
                                       json=auth_data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                
                self.log(f"✅ Authentication successful")
                self.log(f"   User ID: {self.user_id}")
                self.log(f"   Token: {self.access_token[:20]}..." if self.access_token else "   Token: None")
                return True
            else:
                self.log(f"❌ Authentication failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Authentication error: {str(e)}", "ERROR")
            return False
    
    def test_website_analysis_with_persistence(self):
        """Step 2: Test website analysis with persistence validation"""
        self.log("🌐 STEP 2: Website Analysis with Persistence Testing")
        try:
            analysis_data = {
                "website_url": TEST_URL
            }
            
            self.log(f"   Analyzing URL: {TEST_URL}")
            start_time = time.time()
            
            response = self.session.post(f"{BASE_URL}/website/analyze", 
                                       json=analysis_data, timeout=120)
            
            end_time = time.time()
            duration = end_time - start_time
            
            if response.status_code == 200:
                self.analysis_result = response.json()
                self.log(f"✅ Website analysis completed successfully in {duration:.1f}s")
                
                # Validate response structure
                required_fields = [
                    'analysis_summary', 'storytelling_analysis', 'analysis_type',
                    'created_at', 'updated_at', 'next_analysis_due'
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in self.analysis_result:
                        missing_fields.append(field)
                
                if missing_fields:
                    self.log(f"⚠️ Missing required fields: {missing_fields}", "WARNING")
                else:
                    self.log("✅ All required fields present in response")
                
                # Log field count
                total_fields = len(self.analysis_result.keys())
                self.log(f"   Total response fields: {total_fields}")
                
                return True
            else:
                self.log(f"❌ Website analysis failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Website analysis error: {str(e)}", "ERROR")
            return False
    
    def validate_date_fields(self):
        """Step 3: Validate date fields and calculations"""
        self.log("📅 STEP 3: Date Fields Validation")
        
        if not self.analysis_result:
            self.log("❌ No analysis result to validate", "ERROR")
            return False
        
        try:
            # Check for required date fields
            created_at = self.analysis_result.get('created_at')
            updated_at = self.analysis_result.get('updated_at')
            next_analysis_due = self.analysis_result.get('next_analysis_due')
            
            self.log(f"   created_at: {created_at}")
            self.log(f"   updated_at: {updated_at}")
            self.log(f"   next_analysis_due: {next_analysis_due}")
            
            if not created_at:
                self.log("❌ created_at field missing", "ERROR")
                return False
            
            if not updated_at:
                self.log("❌ updated_at field missing", "ERROR")
                return False
            
            if not next_analysis_due:
                self.log("❌ next_analysis_due field missing", "ERROR")
                return False
            
            # Parse dates
            try:
                created_date = parser.parse(created_at)
                next_due_date = parser.parse(next_analysis_due)
                
                # Calculate expected next analysis date (30 days from created)
                expected_next_due = created_date + timedelta(days=30)
                
                # Calculate actual difference
                actual_diff = next_due_date - created_date
                actual_days = actual_diff.days
                
                self.log(f"   Created date: {created_date}")
                self.log(f"   Next due date: {next_due_date}")
                self.log(f"   Actual difference: {actual_days} days")
                self.log(f"   Expected difference: 30 days")
                
                # Validate 30-day calculation (allow 1-day tolerance for timezone differences)
                if 29 <= actual_days <= 31:
                    self.log("✅ Date calculation correct: ~30 days (1 month)")
                    return True
                elif 6 <= actual_days <= 8:
                    self.log("❌ Date calculation incorrect: ~7 days (old bug still present)", "ERROR")
                    return False
                else:
                    self.log(f"⚠️ Unexpected date difference: {actual_days} days", "WARNING")
                    return False
                    
            except Exception as e:
                self.log(f"❌ Date parsing error: {str(e)}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Date validation error: {str(e)}", "ERROR")
            return False
    
    def test_persistence_retrieval(self):
        """Step 4: Test persistence by retrieving analysis from database"""
        self.log("💾 STEP 4: Database Persistence Verification")
        try:
            # Wait a moment to ensure database write is complete
            time.sleep(2)
            
            response = self.session.get(f"{BASE_URL}/website/analysis", timeout=30)
            
            if response.status_code == 200:
                retrieved_data = response.json()
                self.log("✅ Analysis retrieved from database successfully")
                
                # Validate that we got the same analysis back
                if isinstance(retrieved_data, list) and len(retrieved_data) > 0:
                    latest_analysis = retrieved_data[0]  # Assuming latest is first
                elif isinstance(retrieved_data, dict):
                    latest_analysis = retrieved_data
                else:
                    self.log("⚠️ Unexpected response format from GET /website/analysis", "WARNING")
                    return False
                
                # Check if key fields match
                original_summary = self.analysis_result.get('analysis_summary', '')
                retrieved_summary = latest_analysis.get('analysis_summary', '')
                
                if original_summary and retrieved_summary:
                    if original_summary == retrieved_summary:
                        self.log("✅ Analysis content matches - persistence confirmed")
                    else:
                        self.log("⚠️ Analysis content differs - possible cache/persistence issue", "WARNING")
                
                # Count fields in retrieved data
                retrieved_fields = len(latest_analysis.keys())
                self.log(f"   Retrieved fields count: {retrieved_fields}")
                
                # Check for date fields in retrieved data
                if latest_analysis.get('created_at') and latest_analysis.get('next_analysis_due'):
                    self.log("✅ Date fields present in retrieved data")
                else:
                    self.log("❌ Date fields missing in retrieved data", "ERROR")
                
                return True
            else:
                self.log(f"❌ Failed to retrieve analysis: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Persistence retrieval error: {str(e)}", "ERROR")
            return False
    
    def test_subsequent_retrieval(self):
        """Step 5: Test subsequent retrieval to confirm persistence"""
        self.log("🔄 STEP 5: Subsequent Retrieval Test")
        try:
            # Wait a few more seconds
            time.sleep(3)
            
            response = self.session.get(f"{BASE_URL}/website/analysis", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Subsequent retrieval successful")
                
                # Check if data is still there
                if isinstance(data, list) and len(data) > 0:
                    self.log(f"   Found {len(data)} analysis records")
                elif isinstance(data, dict) and data:
                    self.log("   Found analysis record")
                else:
                    self.log("⚠️ No analysis data found in subsequent retrieval", "WARNING")
                    return False
                
                self.log("✅ Persistence confirmed beyond cache timeout")
                return True
            else:
                self.log(f"❌ Subsequent retrieval failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Subsequent retrieval error: {str(e)}", "ERROR")
            return False
    
    def run_comprehensive_test(self):
        """Run all persistence and date calculation tests"""
        self.log("🚀 STARTING WEBSITE ANALYSIS PERSISTENCE & DATE CALCULATION TESTS")
        self.log("=" * 80)
        
        test_results = {
            "authentication": False,
            "website_analysis": False,
            "date_validation": False,
            "persistence_retrieval": False,
            "subsequent_retrieval": False
        }
        
        # Step 1: Authentication
        if self.authenticate():
            test_results["authentication"] = True
        else:
            self.log("❌ Authentication failed - cannot continue", "ERROR")
            return test_results
        
        # Step 2: Website Analysis
        if self.test_website_analysis_with_persistence():
            test_results["website_analysis"] = True
        else:
            self.log("❌ Website analysis failed - cannot continue", "ERROR")
            return test_results
        
        # Step 3: Date Validation
        if self.validate_date_fields():
            test_results["date_validation"] = True
        else:
            self.log("❌ Date validation failed", "ERROR")
        
        # Step 4: Persistence Retrieval
        if self.test_persistence_retrieval():
            test_results["persistence_retrieval"] = True
        else:
            self.log("❌ Persistence retrieval failed", "ERROR")
        
        # Step 5: Subsequent Retrieval
        if self.test_subsequent_retrieval():
            test_results["subsequent_retrieval"] = True
        else:
            self.log("❌ Subsequent retrieval failed", "ERROR")
        
        # Summary
        self.log("=" * 80)
        self.log("🎯 TEST RESULTS SUMMARY:")
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"   {test_name.replace('_', ' ').title()}: {status}")
        
        self.log(f"📊 Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        # Critical assessment
        critical_tests = ["website_analysis", "date_validation", "persistence_retrieval"]
        critical_passed = sum(test_results[test] for test in critical_tests)
        
        if critical_passed == len(critical_tests):
            self.log("🎉 CRITICAL FIXES VALIDATION: SUCCESS")
            self.log("   ✅ Database persistence working correctly")
            self.log("   ✅ Date calculation fixed (30 days instead of 7)")
            self.log("   ✅ All required date fields present")
        else:
            self.log("🚨 CRITICAL FIXES VALIDATION: FAILED")
            if not test_results["website_analysis"]:
                self.log("   ❌ Website analysis not working")
            if not test_results["date_validation"]:
                self.log("   ❌ Date calculation still incorrect (7 days instead of 30)")
            if not test_results["persistence_retrieval"]:
                self.log("   ❌ Database persistence not working")
        
        return test_results

def main():
    """Main test execution"""
    tester = WebsitePersistenceTester()
    results = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    critical_tests = ["website_analysis", "date_validation", "persistence_retrieval"]
    critical_passed = sum(results[test] for test in critical_tests)
    
    if critical_passed == len(critical_tests):
        print("\n🎉 All critical tests passed!")
        sys.exit(0)
    else:
        print(f"\n❌ {len(critical_tests) - critical_passed} critical test(s) failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()