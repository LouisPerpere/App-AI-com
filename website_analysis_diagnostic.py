#!/usr/bin/env python3
"""
DIAGNOSTIC MODULE ANALYSE DE SITE WEB - Backend Testing
Testing the website analysis system that "mouline dans le vide" (spins endlessly)

Focus: Identify where the website analysis gets stuck and why it never completes
URL: https://social-pub-hub.preview.emergentagent.com/api
Credentials: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://social-pub-hub.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

# Test URLs suggested in the review request
TEST_URLS = [
    "https://myownwatch.fr",  # User's simple site
    "https://google.com",     # Very simple site for quick test
    "https://example.com"     # Minimalist site
]

class WebsiteAnalysisTestSuite:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Website-Analysis-Diagnostic/1.0'
        })
        self.access_token = None
        self.user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details, duration=None):
        """Log test results with timing information"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        duration_str = f" ({duration:.1f}s)" if duration else ""
        print(f"{status}: {test_name}{duration_str}")
        print(f"   Details: {details}")
        print()

    def test_authentication(self):
        """Test 1: Authentication with provided credentials"""
        start_time = time.time()
        
        try:
            response = self.session.post(f"{BASE_URL}/auth/login-robust", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                self.user_id = data.get('user_id')
                
                if self.access_token:
                    self.session.headers['Authorization'] = f'Bearer {self.access_token}'
                    self.log_result(
                        "Authentication", 
                        True, 
                        f"Successfully authenticated user {self.user_id}",
                        duration
                    )
                    return True
                else:
                    self.log_result("Authentication", False, "No access token received", duration)
                    return False
            else:
                self.log_result(
                    "Authentication", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_result("Authentication", False, f"Exception: {str(e)}", duration)
            return False

    def test_backend_health(self):
        """Test 2: Backend health check"""
        start_time = time.time()
        
        try:
            response = self.session.get(f"{BASE_URL}/health")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Backend Health", 
                    True, 
                    f"API healthy: {data.get('service', 'Unknown service')}",
                    duration
                )
                return True
            else:
                self.log_result(
                    "Backend Health", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_result("Backend Health", False, f"Exception: {str(e)}", duration)
            return False

    def test_website_analysis_endpoint(self, test_url, timeout=60):
        """Test website analysis with specific URL and timeout monitoring"""
        start_time = time.time()
        
        try:
            print(f"🔍 Testing website analysis for: {test_url}")
            print(f"   Timeout set to: {timeout} seconds")
            
            response = self.session.post(
                f"{BASE_URL}/website/analyze",
                json={"website_url": test_url},
                timeout=timeout
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields in response
                required_fields = ['analysis_summary', 'storytelling_analysis', 'analysis_type']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        f"Website Analysis - {test_url}",
                        False,
                        f"Missing required fields: {missing_fields}. Duration: {duration:.1f}s",
                        duration
                    )
                    return False
                
                # Check content quality
                analysis_length = len(data.get('analysis_summary', ''))
                storytelling_length = len(data.get('storytelling_analysis', ''))
                
                self.log_result(
                    f"Website Analysis - {test_url}",
                    True,
                    f"Analysis completed successfully. Analysis: {analysis_length} chars, Storytelling: {storytelling_length} chars, Type: {data.get('analysis_type', 'unknown')}",
                    duration
                )
                return True
                
            elif response.status_code == 408 or "timeout" in response.text.lower():
                self.log_result(
                    f"Website Analysis - {test_url}",
                    False,
                    f"TIMEOUT after {duration:.1f}s - This is the 'mouline dans le vide' issue!",
                    duration
                )
                return False
                
            else:
                self.log_result(
                    f"Website Analysis - {test_url}",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}...",
                    duration
                )
                return False
                
        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            self.log_result(
                f"Website Analysis - {test_url}",
                False,
                f"REQUEST TIMEOUT after {duration:.1f}s - Analysis 'mouline dans le vide'!",
                duration
            )
            return False
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_result(
                f"Website Analysis - {test_url}",
                False,
                f"Exception after {duration:.1f}s: {str(e)}",
                duration
            )
            return False

    def test_debug_endpoints(self):
        """Test debug endpoints to identify where analysis blocks"""
        debug_tests = []
        
        # Test 1: Debug analyze endpoint
        start_time = time.time()
        try:
            response = self.session.post(
                f"{BASE_URL}/website/debug-analyze",
                json={"website_url": "https://example.com"},
                timeout=30
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                debug_tests.append(f"Debug analyze endpoint working ({duration:.1f}s)")
            else:
                debug_tests.append(f"Debug analyze failed: HTTP {response.status_code}")
                
        except Exception as e:
            duration = time.time() - start_time
            debug_tests.append(f"Debug analyze exception after {duration:.1f}s: {str(e)}")
        
        # Test 2: Super unique test endpoint
        start_time = time.time()
        try:
            response = self.session.get(f"{BASE_URL}/website/super-unique-test-endpoint-12345", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                debug_tests.append(f"Test endpoint accessible ({duration:.1f}s)")
            else:
                debug_tests.append(f"Test endpoint: HTTP {response.status_code}")
                
        except Exception as e:
            duration = time.time() - start_time
            debug_tests.append(f"Test endpoint exception after {duration:.1f}s: {str(e)}")
        
        self.log_result(
            "Debug Endpoints",
            len([t for t in debug_tests if "working" in t or "accessible" in t]) > 0,
            "; ".join(debug_tests)
        )

    def test_llm_api_keys(self):
        """Test if LLM API keys are working by checking environment/config"""
        start_time = time.time()
        
        try:
            # Test diagnostic endpoint to check API key status
            response = self.session.get(f"{BASE_URL}/diag", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "LLM API Keys Check",
                    True,
                    f"Diagnostic endpoint accessible. Database: {data.get('database_connected', 'unknown')}",
                    duration
                )
                return True
            else:
                self.log_result(
                    "LLM API Keys Check",
                    False,
                    f"Diagnostic endpoint failed: HTTP {response.status_code}",
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_result(
                "LLM API Keys Check",
                False,
                f"Exception: {str(e)}",
                duration
            )
            return False

    def test_timeout_scenarios(self):
        """Test different timeout scenarios to identify blocking points"""
        timeout_tests = []
        
        for timeout_duration in [10, 30, 60]:
            start_time = time.time()
            try:
                print(f"   Testing with {timeout_duration}s timeout...")
                response = self.session.post(
                    f"{BASE_URL}/website/analyze",
                    json={"website_url": "https://example.com"},
                    timeout=timeout_duration
                )
                
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    timeout_tests.append(f"{timeout_duration}s: SUCCESS ({duration:.1f}s)")
                    break  # If it works with this timeout, no need to test longer ones
                else:
                    timeout_tests.append(f"{timeout_duration}s: HTTP {response.status_code}")
                    
            except requests.exceptions.Timeout:
                duration = time.time() - start_time
                timeout_tests.append(f"{timeout_duration}s: TIMEOUT after {duration:.1f}s")
            except Exception as e:
                duration = time.time() - start_time
                timeout_tests.append(f"{timeout_duration}s: Exception after {duration:.1f}s")
        
        success = any("SUCCESS" in test for test in timeout_tests)
        self.log_result(
            "Timeout Scenarios",
            success,
            "; ".join(timeout_tests)
        )

    def run_comprehensive_diagnostic(self):
        """Run comprehensive diagnostic of website analysis system"""
        print("🚨 DIAGNOSTIC MODULE ANALYSE DE SITE WEB - 'Mouline dans le vide'")
        print("=" * 70)
        print(f"Testing backend: {BASE_URL}")
        print(f"User credentials: {TEST_EMAIL}")
        print(f"Test URLs: {', '.join(TEST_URLS)}")
        print("=" * 70)
        print()
        
        # Step 1: Authentication
        if not self.test_authentication():
            print("❌ CRITICAL: Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Backend health
        self.test_backend_health()
        
        # Step 3: Test website analysis with different URLs
        print("🔍 TESTING WEBSITE ANALYSIS ENDPOINTS")
        print("-" * 40)
        
        for test_url in TEST_URLS:
            self.test_website_analysis_endpoint(test_url, timeout=60)
            time.sleep(2)  # Brief pause between tests
        
        # Step 4: Debug endpoints
        print("🔧 TESTING DEBUG ENDPOINTS")
        print("-" * 40)
        self.test_debug_endpoints()
        
        # Step 5: LLM API keys check
        print("🤖 TESTING LLM API CONFIGURATION")
        print("-" * 40)
        self.test_llm_api_keys()
        
        # Step 6: Timeout scenarios
        print("⏱️ TESTING TIMEOUT SCENARIOS")
        print("-" * 40)
        self.test_timeout_scenarios()
        
        # Summary
        self.print_diagnostic_summary()
        
        return True

    def print_diagnostic_summary(self):
        """Print comprehensive diagnostic summary"""
        print("\n" + "=" * 70)
        print("🎯 DIAGNOSTIC SUMMARY - WEBSITE ANALYSIS 'MOULINE DANS LE VIDE'")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Critical issues
        critical_issues = []
        timeout_issues = []
        
        for result in self.test_results:
            if not result['success']:
                if 'timeout' in result['details'].lower() or 'mouline' in result['details'].lower():
                    timeout_issues.append(f"   - {result['test']}: {result['details']}")
                else:
                    critical_issues.append(f"   - {result['test']}: {result['details']}")
        
        if timeout_issues:
            print("🚨 TIMEOUT ISSUES IDENTIFIED (Root cause of 'mouline dans le vide'):")
            for issue in timeout_issues:
                print(issue)
            print()
        
        if critical_issues:
            print("❌ OTHER CRITICAL ISSUES:")
            for issue in critical_issues:
                print(issue)
            print()
        
        # Performance analysis
        analysis_times = []
        for result in self.test_results:
            if 'Website Analysis' in result['test'] and result['duration']:
                analysis_times.append(result['duration'])
        
        if analysis_times:
            avg_time = sum(analysis_times) / len(analysis_times)
            max_time = max(analysis_times)
            print(f"⏱️ PERFORMANCE ANALYSIS:")
            print(f"   Average analysis time: {avg_time:.1f}s")
            print(f"   Maximum analysis time: {max_time:.1f}s")
            print(f"   Expected time: <60s")
            
            if max_time > 60:
                print(f"   🚨 ISSUE: Analysis taking longer than 60s timeout!")
            print()
        
        # Recommendations
        print("💡 RECOMMENDATIONS:")
        if timeout_issues:
            print("   1. 🔍 INVESTIGATE LLM API CALLS - Check OpenAI and Claude API response times")
            print("   2. 🔍 CHECK CONTENT EXTRACTION - Verify website scraping is not hanging")
            print("   3. 🔍 MONITOR BACKUP SYSTEM - Ensure fallback LLM system works correctly")
            print("   4. 🔍 ADD LOGGING - Implement detailed logging in website_analyzer_gpt5.py")
        
        if not self.access_token:
            print("   1. ❌ FIX AUTHENTICATION - Cannot test without valid credentials")
        
        print("   5. 🔧 IMPLEMENT TIMEOUT HANDLING - Add proper timeout management in analysis")
        print("   6. 📊 ADD PROGRESS INDICATORS - Show analysis progress to user")
        print()
        
        print("🎯 CONCLUSION:")
        if timeout_issues:
            print("   The 'mouline dans le vide' issue is confirmed - website analysis is timing out.")
            print("   Focus investigation on LLM API calls and content extraction processes.")
        elif failed_tests == 0:
            print("   All tests passed - the issue may be intermittent or environment-specific.")
        else:
            print("   Multiple issues identified - see critical issues above for details.")
        
        print("=" * 70)

def main():
    """Main diagnostic function"""
    print("Starting Website Analysis Diagnostic...")
    
    tester = WebsiteAnalysisTestSuite()
    
    try:
        tester.run_comprehensive_diagnostic()
    except KeyboardInterrupt:
        print("\n⚠️ Diagnostic interrupted by user")
    except Exception as e:
        print(f"\n❌ Diagnostic failed with exception: {str(e)}")
    
    print("\nDiagnostic completed.")

if __name__ == "__main__":
    main()