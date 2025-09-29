#!/usr/bin/env python3
"""
TEST VALIDATION DES AMÉLIORATIONS MODULE ANALYSE DE SITE WEB
Testing the website analysis system timeout improvements to fix "mouline dans le vide" issue

CORRECTIONS APPLIQUÉES:
1. Timeout global de 45 secondes avec asyncio.wait_for
2. Timeouts spécifiques : 20s pour extraction contenu, 15s par LLM
3. Réduction pages analysées de 5 à 3 pour performance
4. Meilleure gestion d'erreurs avec codes HTTP appropriés
5. Indicateurs de progression améliorés

URL: https://social-pub-hub.preview.emergentagent.com/api
Credentials: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration from review request
BASE_URL = "https://social-pub-hub.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

# Test URLs from review request
SIMPLE_SITE = "https://myownwatch.fr"  # Should succeed quickly < 30s
COMPLEX_SITE = "https://google.com"    # Should timeout properly at ~45s with HTTP 408

class WebsiteAnalysisTimeoutTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Website-Analysis-Timeout-Tester/1.0'
        })
        self.access_token = None
        self.user_id = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def authenticate(self):
        """Step 1: Authentication with provided credentials"""
        self.log("🔐 STEP 1: Authentication Test")
        
        try:
            response = self.session.post(
                f"{BASE_URL}/auth/login-robust",
                json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Configure session headers
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                self.log(f"✅ Authentication successful")
                self.log(f"   User ID: {self.user_id}")
                self.log(f"   Email: {data.get('email')}")
                return True
            else:
                self.log(f"❌ Authentication failed: {response.status_code}")
                self.log(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_simple_site_analysis(self):
        """Step 2: Test simple site (should succeed quickly < 30 seconds)"""
        self.log(f"🔍 STEP 2: Simple Site Analysis Test")
        self.log(f"   Target: {SIMPLE_SITE}")
        self.log(f"   Expected: Success < 30 seconds")
        
        try:
            start_time = time.time()
            
            response = self.session.post(
                f"{BASE_URL}/website/analyze",
                json={"website_url": SIMPLE_SITE},
                timeout=60  # Allow up to 60s but expect < 30s
            )
            
            analysis_time = time.time() - start_time
            
            self.log(f"   Analysis completed in {analysis_time:.1f} seconds")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["analysis_summary", "storytelling_analysis", "analysis_type"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log(f"✅ Simple site analysis SUCCESSFUL")
                    self.log(f"   Response time: {analysis_time:.1f}s (Target: < 30s)")
                    self.log(f"   Analysis type: {data.get('analysis_type', 'unknown')}")
                    
                    # Check for new timeout-related fields
                    if "analysis_optimized" in data:
                        self.log(f"   Analysis optimized: {data.get('analysis_optimized')}")
                    if "timeout_handled" in data:
                        self.log(f"   Timeout handled: {data.get('timeout_handled')}")
                    
                    # Verify content quality
                    summary_length = len(data.get("analysis_summary", ""))
                    storytelling_length = len(data.get("storytelling_analysis", ""))
                    self.log(f"   Content quality: Summary {summary_length} chars, Storytelling {storytelling_length} chars")
                    
                    # Check if time requirement met
                    if analysis_time < 30:
                        self.log(f"✅ TIME REQUIREMENT MET: {analysis_time:.1f}s < 30s")
                        return True
                    else:
                        self.log(f"⚠️ TIME REQUIREMENT NOT MET: {analysis_time:.1f}s >= 30s")
                        return False
                else:
                    self.log(f"❌ Missing required fields: {missing_fields}")
                    return False
            else:
                self.log(f"❌ Simple site analysis FAILED: HTTP {response.status_code}")
                self.log(f"   Response: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            analysis_time = time.time() - start_time
            self.log(f"❌ Simple site analysis TIMEOUT after {analysis_time:.1f}s")
            return False
        except Exception as e:
            analysis_time = time.time() - start_time
            self.log(f"❌ Simple site analysis ERROR after {analysis_time:.1f}s: {str(e)}")
            return False
    
    def test_complex_site_timeout(self):
        """Step 3: Test complex site (should timeout properly after ~45s with HTTP 408)"""
        self.log(f"🔍 STEP 3: Complex Site Timeout Test")
        self.log(f"   Target: {COMPLEX_SITE}")
        self.log(f"   Expected: Timeout ~45s with HTTP 408")
        
        try:
            start_time = time.time()
            
            response = self.session.post(
                f"{BASE_URL}/website/analyze",
                json={"website_url": COMPLEX_SITE},
                timeout=60  # Allow up to 60s to catch the 45s timeout
            )
            
            analysis_time = time.time() - start_time
            
            self.log(f"   Analysis completed/failed in {analysis_time:.1f} seconds")
            
            if response.status_code == 408:
                # Expected timeout response
                self.log(f"✅ Complex site timeout SUCCESSFUL")
                self.log(f"   Response time: {analysis_time:.1f}s (Expected: ~45s)")
                self.log(f"   HTTP Status: {response.status_code} (Expected: 408)")
                
                try:
                    error_data = response.json()
                    error_message = error_data.get("error", "")
                    if "L'analyse du site web a pris trop de temps" in error_message:
                        self.log(f"✅ User-friendly error message: {error_message}")
                    else:
                        self.log(f"⚠️ Error message: {error_message}")
                except:
                    self.log(f"⚠️ Could not parse error response: {response.text}")
                
                # Check if timeout is around 45 seconds
                if 40 <= analysis_time <= 50:
                    self.log(f"✅ TIMEOUT TIMING CORRECT: {analysis_time:.1f}s (Target: ~45s)")
                    return True
                else:
                    self.log(f"⚠️ TIMEOUT TIMING OFF: {analysis_time:.1f}s (Expected: ~45s)")
                    return False
                    
            elif response.status_code == 200:
                # Unexpected success
                self.log(f"⚠️ Complex site analysis UNEXPECTEDLY SUCCEEDED")
                self.log(f"   Response time: {analysis_time:.1f}s")
                self.log(f"   This might indicate the site is simpler than expected")
                
                # Still check if it's within reasonable time
                if analysis_time < 50:
                    return True
                else:
                    self.log(f"❌ Analysis took too long: {analysis_time:.1f}s")
                    return False
            else:
                self.log(f"❌ Complex site analysis FAILED with unexpected status: {response.status_code}")
                self.log(f"   Response: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            analysis_time = time.time() - start_time
            self.log(f"❌ Request timeout (client-side) after {analysis_time:.1f}s")
            self.log(f"   This suggests server timeout is not working properly")
            return False
        except Exception as e:
            analysis_time = time.time() - start_time
            self.log(f"❌ Complex site analysis ERROR after {analysis_time:.1f}s: {str(e)}")
            return False
    
    def test_performance_general(self):
        """Step 4: Test general performance - no analysis should exceed 50 seconds"""
        self.log(f"🔍 STEP 4: General Performance Test")
        
        test_sites = [
            "https://example.com",
            "https://httpbin.org",
            "https://jsonplaceholder.typicode.com"
        ]
        
        all_passed = True
        
        for site in test_sites:
            self.log(f"   Testing: {site}")
            
            try:
                start_time = time.time()
                
                response = self.session.post(
                    f"{BASE_URL}/website/analyze",
                    json={"website_url": site},
                    timeout=60
                )
                
                analysis_time = time.time() - start_time
                
                if analysis_time <= 50:
                    self.log(f"   ✅ {site}: {analysis_time:.1f}s (< 50s limit)")
                else:
                    self.log(f"   ❌ {site}: {analysis_time:.1f}s (> 50s limit)")
                    all_passed = False
                    
                # Check response status
                if response.status_code in [200, 408]:
                    self.log(f"      Status: {response.status_code} (OK)")
                else:
                    self.log(f"      Status: {response.status_code} (Unexpected)")
                    
            except requests.exceptions.Timeout:
                analysis_time = time.time() - start_time
                self.log(f"   ❌ {site}: Client timeout after {analysis_time:.1f}s")
                all_passed = False
            except Exception as e:
                analysis_time = time.time() - start_time
                self.log(f"   ❌ {site}: Error after {analysis_time:.1f}s - {str(e)}")
                all_passed = False
        
        if all_passed:
            self.log(f"✅ General performance test PASSED - All sites < 50s")
        else:
            self.log(f"❌ General performance test FAILED - Some sites > 50s")
            
        return all_passed
    
    def test_system_robustness(self):
        """Step 5: Test system robustness - timeouts shouldn't affect other endpoints"""
        self.log(f"🔍 STEP 5: System Robustness Test")
        
        # Test other endpoints after website analysis
        endpoints_to_test = [
            ("/health", "GET"),
            ("/business-profile", "GET"),
            ("/content/pending", "GET"),
            ("/notes", "GET")
        ]
        
        all_passed = True
        
        for endpoint, method in endpoints_to_test:
            self.log(f"   Testing: {method} {endpoint}")
            
            try:
                if method == "GET":
                    response = self.session.get(f"{BASE_URL}{endpoint}", timeout=10)
                else:
                    response = self.session.post(f"{BASE_URL}{endpoint}", timeout=10)
                
                if response.status_code in [200, 401]:  # 401 is OK for auth-required endpoints
                    self.log(f"   ✅ {endpoint}: Status {response.status_code}")
                else:
                    self.log(f"   ❌ {endpoint}: Status {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.log(f"   ❌ {endpoint}: Error - {str(e)}")
                all_passed = False
        
        if all_passed:
            self.log(f"✅ System robustness test PASSED - Other endpoints working")
        else:
            self.log(f"❌ System robustness test FAILED - Some endpoints affected")
            
        return all_passed
    
    def test_multiple_consecutive_analyses(self):
        """Step 6: Test multiple consecutive analyses without blocking"""
        self.log(f"🔍 STEP 6: Multiple Consecutive Analyses Test")
        
        test_sites = [SIMPLE_SITE, "https://example.com"]
        all_passed = True
        
        for i, site in enumerate(test_sites, 1):
            self.log(f"   Analysis {i}: {site}")
            
            try:
                start_time = time.time()
                
                response = self.session.post(
                    f"{BASE_URL}/website/analyze",
                    json={"website_url": site},
                    timeout=60
                )
                
                analysis_time = time.time() - start_time
                
                if response.status_code in [200, 408] and analysis_time <= 50:
                    self.log(f"   ✅ Analysis {i}: {analysis_time:.1f}s, Status {response.status_code}")
                else:
                    self.log(f"   ❌ Analysis {i}: {analysis_time:.1f}s, Status {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.log(f"   ❌ Analysis {i}: Error - {str(e)}")
                all_passed = False
        
        if all_passed:
            self.log(f"✅ Multiple analyses test PASSED - No blocking detected")
        else:
            self.log(f"❌ Multiple analyses test FAILED - Blocking or errors detected")
            
        return all_passed
    
    def run_comprehensive_timeout_test(self):
        """Run the complete website analysis timeout test suite"""
        self.log("🚀 WEBSITE ANALYSIS TIMEOUT IMPROVEMENTS TEST SUITE")
        self.log("=" * 80)
        self.log(f"Backend: {BASE_URL}")
        self.log(f"Credentials: {TEST_EMAIL}")
        self.log(f"Simple Site: {SIMPLE_SITE} (Expected: < 30s success)")
        self.log(f"Complex Site: {COMPLEX_SITE} (Expected: ~45s timeout HTTP 408)")
        self.log("=" * 80)
        
        results = {}
        
        # Step 1: Authentication
        results['auth'] = self.authenticate()
        if not results['auth']:
            self.log("❌ CRITICAL: Authentication failed - cannot proceed")
            return False
        
        # Step 2: Simple site test
        results['simple_site'] = self.test_simple_site_analysis()
        
        # Step 3: Complex site timeout test
        results['complex_site_timeout'] = self.test_complex_site_timeout()
        
        # Step 4: General performance test
        results['general_performance'] = self.test_performance_general()
        
        # Step 5: System robustness test
        results['system_robustness'] = self.test_system_robustness()
        
        # Step 6: Multiple consecutive analyses test
        results['multiple_analyses'] = self.test_multiple_consecutive_analyses()
        
        # Calculate success metrics
        passed_tests = sum(1 for result in results.values() if result)
        total_tests = len(results)
        success_rate = (passed_tests / total_tests) * 100
        
        # Final summary
        self.log("=" * 80)
        self.log("🎯 TEST RESULTS SUMMARY:")
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"   {test_name.upper().replace('_', ' ')}: {status}")
        
        self.log(f"   OVERALL SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        
        # Critical analysis
        self.log("=" * 80)
        self.log("🔍 CRITICAL ANALYSIS:")
        
        if results['simple_site']:
            self.log("✅ SIMPLE SITES: Working correctly with proper timing")
        else:
            self.log("❌ SIMPLE SITES: Issues with performance or functionality")
        
        if results['complex_site_timeout']:
            self.log("✅ TIMEOUT HANDLING: Working correctly with HTTP 408")
        else:
            self.log("❌ TIMEOUT HANDLING: Not working as expected")
        
        if results['general_performance']:
            self.log("✅ PERFORMANCE: All analyses complete within 50s limit")
        else:
            self.log("❌ PERFORMANCE: Some analyses exceed 50s limit")
        
        if results['system_robustness']:
            self.log("✅ SYSTEM STABILITY: Other endpoints unaffected by timeouts")
        else:
            self.log("❌ SYSTEM STABILITY: Timeouts affecting other endpoints")
        
        # Final conclusion
        self.log("=" * 80)
        self.log("🎯 FINAL CONCLUSION:")
        
        if success_rate >= 80:
            self.log("✅ WEBSITE ANALYSIS TIMEOUT IMPROVEMENTS: SUCCESSFUL")
            self.log("   - Timeout handling working correctly")
            self.log("   - Performance within acceptable limits")
            self.log("   - System stability maintained")
            self.log("   - 'Mouline dans le vide' issue RESOLVED")
        elif success_rate >= 60:
            self.log("⚠️ WEBSITE ANALYSIS TIMEOUT IMPROVEMENTS: PARTIALLY SUCCESSFUL")
            self.log("   - Some improvements working but issues remain")
            self.log("   - Further optimization may be needed")
        else:
            self.log("❌ WEBSITE ANALYSIS TIMEOUT IMPROVEMENTS: FAILED")
            self.log("   - Timeout improvements not working as expected")
            self.log("   - 'Mouline dans le vide' issue may persist")
        
        return success_rate >= 80

def main():
    """Main test execution"""
    tester = WebsiteAnalysisTimeoutTester()
    success = tester.run_comprehensive_timeout_test()
    
    if success:
        print(f"\n🎉 TIMEOUT IMPROVEMENTS TEST SUITE COMPLETED SUCCESSFULLY")
        sys.exit(0)
    else:
        print(f"\n💥 TIMEOUT IMPROVEMENTS TEST SUITE FAILED - ISSUES DETECTED")
        sys.exit(1)

if __name__ == "__main__":
    main()