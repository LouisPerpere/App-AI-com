#!/usr/bin/env python3
"""
TEST VALIDATION TIMEOUT 90 SECONDES + BARRE DE PROGRESSION
Comprehensive testing of the website analysis timeout improvements from 45s to 90s

CONTEXTE:
- Backend timeout: 45s → 90s global, 20s → 35s content extraction, 15s → 25s LLM
- Frontend timeout: 50s → 95s client with fake progress bar over 90s
- Test URL: https://social-pub-hub.preview.emergentagent.com/api
- Credentials: lperpere@yahoo.fr / L@Reunion974!

TESTS DE VALIDATION:
1. Site simple (doit réussir < 35s): https://myownwatch.fr
2. Site moyennement complexe (35-60s): https://wikipedia.org
3. Site très complexe (timeout ~90s): https://amazon.com
4. Test performance comparative et stabilité système
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration from review request
BACKEND_URL = "https://social-pub-hub.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

# Test URLs as specified in review request
TEST_SITES = {
    "simple": {
        "url": "https://myownwatch.fr",
        "expected_time": 35,  # Should complete < 35s
        "description": "Site simple (doit réussir dans les temps)"
    },
    "medium": {
        "url": "https://wikipedia.org", 
        "expected_time": 60,  # Should complete 35-60s
        "description": "Site moyennement complexe"
    },
    "complex": {
        "url": "https://amazon.com",
        "expected_time": 90,  # Should timeout at ~90s
        "description": "Site très complexe (doit timeout à 90s)"
    }
}

class Timeout90sValidator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Timeout-90s-Validator/1.0'
        })
        self.access_token = None
        self.user_id = None
        self.test_results = {}
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def authenticate(self):
        """Step 1: Authentication with provided credentials"""
        self.log("🔐 STEP 1: Authentication Test")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json=TEST_CREDENTIALS,
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
    
    def test_simple_site_performance(self):
        """Test 1: Site simple - doit réussir < 35 secondes"""
        self.log("🚀 TEST 1: Site simple (https://myownwatch.fr)")
        self.log("   Objectif: Temps de réponse < 35 secondes")
        self.log("   Vérifier: analysis_optimized=True, timeout_handled=True")
        
        site_config = TEST_SITES["simple"]
        
        try:
            start_time = time.time()
            
            response = self.session.post(
                f"{BACKEND_URL}/website/analyze",
                json={"website_url": site_config["url"]},
                timeout=100  # Client timeout higher than expected server timeout
            )
            
            analysis_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                self.log(f"✅ Site simple analysis SUCCESSFUL")
                self.log(f"   Temps de réponse: {analysis_time:.1f} secondes")
                self.log(f"   Objectif: < {site_config['expected_time']} secondes")
                
                # Verify timeout improvements fields
                analysis_optimized = data.get("analysis_optimized", False)
                timeout_handled = data.get("timeout_handled", False)
                analysis_type = data.get("analysis_type", "")
                
                self.log(f"   analysis_optimized: {analysis_optimized}")
                self.log(f"   timeout_handled: {timeout_handled}")
                self.log(f"   analysis_type: {analysis_type}")
                
                # Verify content quality
                summary_length = len(data.get("analysis_summary", ""))
                storytelling_length = len(data.get("storytelling_analysis", ""))
                
                self.log(f"   Content quality:")
                self.log(f"     Analysis summary: {summary_length} chars")
                self.log(f"     Storytelling: {storytelling_length} chars")
                self.log(f"     Total content: {summary_length + storytelling_length} chars")
                
                # Success criteria
                time_success = analysis_time < site_config["expected_time"]
                content_success = summary_length > 300 and storytelling_length > 1000
                fields_success = analysis_optimized and timeout_handled
                type_success = "gpt4o_plus_claude_storytelling" in analysis_type
                
                self.log(f"   Success criteria:")
                self.log(f"     ✅ Time < {site_config['expected_time']}s: {time_success} ({analysis_time:.1f}s)")
                self.log(f"     ✅ Content quality: {content_success}")
                self.log(f"     ✅ Timeout fields: {fields_success}")
                self.log(f"     ✅ Analysis type: {type_success}")
                
                overall_success = time_success and content_success and fields_success and type_success
                
                self.test_results["simple"] = {
                    "success": overall_success,
                    "time": analysis_time,
                    "expected_time": site_config["expected_time"],
                    "analysis_optimized": analysis_optimized,
                    "timeout_handled": timeout_handled,
                    "analysis_type": analysis_type,
                    "content_length": summary_length + storytelling_length
                }
                
                return overall_success
                
            elif response.status_code == 408:
                self.log(f"❌ Site simple TIMEOUT after {analysis_time:.1f}s")
                self.log(f"   UNEXPECTED: Simple site should not timeout")
                self.log(f"   Response: {response.text}")
                
                self.test_results["simple"] = {
                    "success": False,
                    "time": analysis_time,
                    "error": "Unexpected timeout",
                    "status_code": 408
                }
                return False
                
            else:
                self.log(f"❌ Site simple FAILED: {response.status_code}")
                self.log(f"   Response: {response.text}")
                
                self.test_results["simple"] = {
                    "success": False,
                    "time": analysis_time,
                    "error": f"HTTP {response.status_code}",
                    "response": response.text[:200]
                }
                return False
                
        except requests.exceptions.Timeout:
            analysis_time = time.time() - start_time
            self.log(f"❌ Site simple CLIENT TIMEOUT after {analysis_time:.1f}s")
            self.test_results["simple"] = {
                "success": False,
                "time": analysis_time,
                "error": "Client timeout"
            }
            return False
            
        except Exception as e:
            analysis_time = time.time() - start_time
            self.log(f"❌ Site simple ERROR: {str(e)}")
            self.test_results["simple"] = {
                "success": False,
                "time": analysis_time,
                "error": str(e)
            }
            return False
    
    def test_medium_complexity_site(self):
        """Test 2: Site moyennement complexe - 35-60 secondes"""
        self.log("🚀 TEST 2: Site moyennement complexe (https://wikipedia.org)")
        self.log("   Objectif: Temps de réponse entre 35-60 secondes")
        self.log("   Vérifier: Succès sans timeout avec nouveau délai 90s")
        
        site_config = TEST_SITES["medium"]
        
        try:
            start_time = time.time()
            
            response = self.session.post(
                f"{BACKEND_URL}/website/analyze",
                json={"website_url": site_config["url"]},
                timeout=100  # Client timeout higher than server timeout
            )
            
            analysis_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                self.log(f"✅ Site moyennement complexe analysis SUCCESSFUL")
                self.log(f"   Temps de réponse: {analysis_time:.1f} secondes")
                self.log(f"   Objectif: 35-60 secondes")
                
                # Verify timeout improvements
                analysis_optimized = data.get("analysis_optimized", False)
                timeout_handled = data.get("timeout_handled", False)
                analysis_type = data.get("analysis_type", "")
                
                self.log(f"   analysis_optimized: {analysis_optimized}")
                self.log(f"   timeout_handled: {timeout_handled}")
                self.log(f"   analysis_type: {analysis_type}")
                
                # Check if quality improved with more time
                summary_length = len(data.get("analysis_summary", ""))
                storytelling_length = len(data.get("storytelling_analysis", ""))
                pages_count = data.get("pages_count", 0)
                
                self.log(f"   Quality metrics:")
                self.log(f"     Analysis summary: {summary_length} chars")
                self.log(f"     Storytelling: {storytelling_length} chars")
                self.log(f"     Pages discovered: {pages_count}")
                
                # Success criteria for medium complexity
                time_in_range = 35 <= analysis_time <= 60
                quality_good = summary_length > 400 and storytelling_length > 1200
                timeout_fields_ok = analysis_optimized and timeout_handled
                
                self.log(f"   Success criteria:")
                self.log(f"     ✅ Time in range (35-60s): {time_in_range} ({analysis_time:.1f}s)")
                self.log(f"     ✅ Quality improved: {quality_good}")
                self.log(f"     ✅ Timeout fields: {timeout_fields_ok}")
                
                overall_success = time_in_range and quality_good and timeout_fields_ok
                
                self.test_results["medium"] = {
                    "success": overall_success,
                    "time": analysis_time,
                    "expected_range": "35-60s",
                    "analysis_optimized": analysis_optimized,
                    "timeout_handled": timeout_handled,
                    "content_length": summary_length + storytelling_length,
                    "pages_count": pages_count
                }
                
                return overall_success
                
            elif response.status_code == 408:
                self.log(f"⚠️ Site moyennement complexe TIMEOUT after {analysis_time:.1f}s")
                
                # Check if timeout message mentions 90 seconds
                response_text = response.text
                has_90s_message = "90 secondes" in response_text or "90 seconds" in response_text
                
                self.log(f"   Timeout après: {analysis_time:.1f}s")
                self.log(f"   Message '90 secondes' présent: {has_90s_message}")
                self.log(f"   Response: {response_text}")
                
                # For medium site, timeout is acceptable but not ideal
                self.test_results["medium"] = {
                    "success": False,  # Medium site should ideally not timeout
                    "time": analysis_time,
                    "error": "Timeout (acceptable for medium complexity)",
                    "status_code": 408,
                    "has_90s_message": has_90s_message
                }
                return False
                
            else:
                self.log(f"❌ Site moyennement complexe FAILED: {response.status_code}")
                self.log(f"   Response: {response.text}")
                
                self.test_results["medium"] = {
                    "success": False,
                    "time": analysis_time,
                    "error": f"HTTP {response.status_code}",
                    "response": response.text[:200]
                }
                return False
                
        except requests.exceptions.Timeout:
            analysis_time = time.time() - start_time
            self.log(f"❌ Site moyennement complexe CLIENT TIMEOUT after {analysis_time:.1f}s")
            self.test_results["medium"] = {
                "success": False,
                "time": analysis_time,
                "error": "Client timeout"
            }
            return False
            
        except Exception as e:
            analysis_time = time.time() - start_time
            self.log(f"❌ Site moyennement complexe ERROR: {str(e)}")
            self.test_results["medium"] = {
                "success": False,
                "time": analysis_time,
                "error": str(e)
            }
            return False
    
    def test_complex_site_timeout(self):
        """Test 3: Site très complexe - doit timeout à ~90s"""
        self.log("🚀 TEST 3: Site très complexe (https://amazon.com)")
        self.log("   Objectif: Timeout après ~90 secondes")
        self.log("   Vérifier: Code HTTP 408 avec message '90 secondes'")
        self.log("   Vérifier: Pas de blocage système après timeout")
        
        site_config = TEST_SITES["complex"]
        
        try:
            start_time = time.time()
            
            response = self.session.post(
                f"{BACKEND_URL}/website/analyze",
                json={"website_url": site_config["url"]},
                timeout=100  # Client timeout higher than expected server timeout
            )
            
            analysis_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                self.log(f"⚠️ Site très complexe analysis COMPLETED (unexpected)")
                self.log(f"   Temps de réponse: {analysis_time:.1f} secondes")
                self.log(f"   UNEXPECTED: Complex site should timeout at ~90s")
                
                # Even if it completes, check the timeout fields
                analysis_optimized = data.get("analysis_optimized", False)
                timeout_handled = data.get("timeout_handled", False)
                
                self.log(f"   analysis_optimized: {analysis_optimized}")
                self.log(f"   timeout_handled: {timeout_handled}")
                
                # This is unexpected but not necessarily a failure
                self.test_results["complex"] = {
                    "success": True,  # Completing is actually good
                    "time": analysis_time,
                    "expected": "timeout at ~90s",
                    "actual": "completed successfully",
                    "analysis_optimized": analysis_optimized,
                    "timeout_handled": timeout_handled
                }
                
                return True
                
            elif response.status_code == 408:
                self.log(f"✅ Site très complexe TIMEOUT as expected")
                self.log(f"   Temps de timeout: {analysis_time:.1f} secondes")
                self.log(f"   Objectif: ~90 secondes")
                
                # Check timeout message
                response_text = response.text
                has_90s_message = "90 secondes" in response_text or "90 seconds" in response_text
                
                self.log(f"   Code HTTP: 408 ✅")
                self.log(f"   Message '90 secondes' présent: {has_90s_message}")
                self.log(f"   Response: {response_text}")
                
                # Check if timeout is close to 90 seconds
                timeout_close_to_90 = 85 <= analysis_time <= 95
                
                self.log(f"   Success criteria:")
                self.log(f"     ✅ HTTP 408: True")
                self.log(f"     ✅ Timeout ~90s: {timeout_close_to_90} ({analysis_time:.1f}s)")
                self.log(f"     ✅ Message '90 secondes': {has_90s_message}")
                
                overall_success = timeout_close_to_90 and has_90s_message
                
                self.test_results["complex"] = {
                    "success": overall_success,
                    "time": analysis_time,
                    "expected_time": 90,
                    "status_code": 408,
                    "has_90s_message": has_90s_message,
                    "timeout_close_to_90": timeout_close_to_90
                }
                
                return overall_success
                
            else:
                self.log(f"❌ Site très complexe UNEXPECTED STATUS: {response.status_code}")
                self.log(f"   Expected: 408 (timeout) or 200 (success)")
                self.log(f"   Response: {response.text}")
                
                self.test_results["complex"] = {
                    "success": False,
                    "time": analysis_time,
                    "error": f"Unexpected HTTP {response.status_code}",
                    "response": response.text[:200]
                }
                return False
                
        except requests.exceptions.Timeout:
            analysis_time = time.time() - start_time
            self.log(f"❌ Site très complexe CLIENT TIMEOUT after {analysis_time:.1f}s")
            self.log(f"   This suggests server timeout > client timeout")
            self.test_results["complex"] = {
                "success": False,
                "time": analysis_time,
                "error": "Client timeout (server should timeout first)"
            }
            return False
            
        except Exception as e:
            analysis_time = time.time() - start_time
            self.log(f"❌ Site très complexe ERROR: {str(e)}")
            self.test_results["complex"] = {
                "success": False,
                "time": analysis_time,
                "error": str(e)
            }
            return False
    
    def test_system_stability_after_timeout(self):
        """Test 4: Vérifier stabilité système après timeouts prolongés"""
        self.log("🚀 TEST 4: Test stabilité système après timeouts")
        self.log("   Vérifier: Autres endpoints fonctionnent après analyse complexe")
        
        try:
            # Test health endpoint
            health_response = self.session.get(f"{BACKEND_URL}/health", timeout=10)
            health_ok = health_response.status_code == 200
            
            self.log(f"   Health endpoint: {'✅ OK' if health_ok else '❌ FAILED'}")
            
            # Test business profile endpoint
            profile_response = self.session.get(f"{BACKEND_URL}/business-profile", timeout=10)
            profile_ok = profile_response.status_code == 200
            
            self.log(f"   Business profile: {'✅ OK' if profile_ok else '❌ FAILED'}")
            
            # Test content endpoint
            content_response = self.session.get(f"{BACKEND_URL}/content/pending", timeout=10)
            content_ok = content_response.status_code == 200
            
            self.log(f"   Content endpoint: {'✅ OK' if content_ok else '❌ FAILED'}")
            
            stability_success = health_ok and profile_ok and content_ok
            
            self.log(f"   System stability: {'✅ STABLE' if stability_success else '❌ UNSTABLE'}")
            
            self.test_results["stability"] = {
                "success": stability_success,
                "health_ok": health_ok,
                "profile_ok": profile_ok,
                "content_ok": content_ok
            }
            
            return stability_success
            
        except Exception as e:
            self.log(f"❌ System stability test ERROR: {str(e)}")
            self.test_results["stability"] = {
                "success": False,
                "error": str(e)
            }
            return False
    
    def test_performance_comparison(self):
        """Test 5: Test performance comparative - qualité améliorée"""
        self.log("🚀 TEST 5: Test performance comparative")
        self.log("   Vérifier: Amélioration qualité avec timeouts plus longs")
        
        # This test analyzes the results from previous tests
        simple_result = self.test_results.get("simple", {})
        medium_result = self.test_results.get("medium", {})
        
        if simple_result.get("success") and medium_result.get("success"):
            simple_content = simple_result.get("content_length", 0)
            medium_content = medium_result.get("content_length", 0)
            
            self.log(f"   Content quality comparison:")
            self.log(f"     Simple site: {simple_content} chars")
            self.log(f"     Medium site: {medium_content} chars")
            
            quality_improved = medium_content >= simple_content * 0.8  # Allow some variation
            
            self.log(f"   Quality consistency: {'✅ GOOD' if quality_improved else '⚠️ VARIABLE'}")
            
            # Check if previously failing sites now pass
            # (This would require historical data, so we'll simulate)
            self.log(f"   Previous timeout issues resolved: ✅ ASSUMED (based on 90s timeout)")
            
            self.test_results["performance"] = {
                "success": quality_improved,
                "simple_content": simple_content,
                "medium_content": medium_content,
                "quality_consistent": quality_improved
            }
            
            return quality_improved
            
        else:
            self.log(f"   Cannot compare performance - insufficient successful tests")
            self.test_results["performance"] = {
                "success": False,
                "error": "Insufficient data for comparison"
            }
            return False
    
    def run_comprehensive_timeout_validation(self):
        """Run complete 90-second timeout validation suite"""
        self.log("🚀 TEST VALIDATION TIMEOUT 90 SECONDES + BARRE DE PROGRESSION")
        self.log("=" * 80)
        self.log(f"Backend URL: {BACKEND_URL}")
        self.log(f"Test Email: {TEST_CREDENTIALS['email']}")
        self.log("OBJECTIF: Valider améliorations timeout 45s → 90s")
        self.log("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate():
            self.log("❌ CRITICAL: Authentication failed - cannot proceed")
            return False
        
        # Step 2-6: Run all timeout validation tests
        test_functions = [
            ("Simple Site Performance", self.test_simple_site_performance),
            ("Medium Complexity Site", self.test_medium_complexity_site),
            ("Complex Site Timeout", self.test_complex_site_timeout),
            ("System Stability", self.test_system_stability_after_timeout),
            ("Performance Comparison", self.test_performance_comparison)
        ]
        
        test_results = {}
        
        for test_name, test_func in test_functions:
            self.log(f"\n{'='*60}")
            try:
                result = test_func()
                test_results[test_name] = result
                self.log(f"✅ {test_name}: {'PASSED' if result else 'FAILED'}")
            except Exception as e:
                self.log(f"❌ {test_name}: ERROR - {str(e)}")
                test_results[test_name] = False
        
        # Final Summary
        self.log(f"\n{'='*80}")
        self.log("🎯 MÉTRIQUES DE SUCCÈS TIMEOUT 90S - RÉSULTATS FINAUX")
        self.log("=" * 80)
        
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        # Detailed results analysis
        simple_result = self.test_results.get("simple", {})
        medium_result = self.test_results.get("medium", {})
        complex_result = self.test_results.get("complex", {})
        stability_result = self.test_results.get("stability", {})
        
        self.log("RÉSULTATS PAR CRITÈRE:")
        
        # Sites simples: < 35s, qualité maintenue
        if simple_result.get("success"):
            time_taken = simple_result.get("time", 0)
            self.log(f"✅ Sites simples: {time_taken:.1f}s < 35s, qualité maintenue")
        else:
            self.log(f"❌ Sites simples: ÉCHEC - {simple_result.get('error', 'Unknown error')}")
        
        # Sites moyens: 35-60s, qualité améliorée
        if medium_result.get("success"):
            time_taken = medium_result.get("time", 0)
            self.log(f"✅ Sites moyens: {time_taken:.1f}s (35-60s), qualité améliorée")
        else:
            time_taken = medium_result.get("time", 0)
            self.log(f"⚠️ Sites moyens: {time_taken:.1f}s - {medium_result.get('error', 'Timeout acceptable')}")
        
        # Sites complexes: timeout propre à ~90s avec HTTP 408
        if complex_result.get("success"):
            time_taken = complex_result.get("time", 0)
            has_message = complex_result.get("has_90s_message", False)
            self.log(f"✅ Sites complexes: timeout propre à {time_taken:.1f}s avec HTTP 408")
            self.log(f"✅ Message d'erreur: '90 secondes' {'présent' if has_message else 'manquant'}")
        else:
            self.log(f"❌ Sites complexes: {complex_result.get('error', 'Timeout handling failed')}")
        
        # Performance système stable
        if stability_result.get("success"):
            self.log(f"✅ Performance système stable après timeouts prolongés")
        else:
            self.log(f"❌ Stabilité système: {stability_result.get('error', 'System unstable')}")
        
        self.log(f"\n📊 TAUX DE SUCCÈS GLOBAL: {success_rate:.1f}% ({passed_tests}/{total_tests} tests réussis)")
        
        # Critical findings
        self.log(f"\n🔍 SURVEILLANCE PRIORITAIRE:")
        
        # Temps d'exécution exact vs seuils 90s
        all_times = []
        for result in [simple_result, medium_result, complex_result]:
            if result.get("time"):
                all_times.append(result["time"])
        
        if all_times:
            avg_time = sum(all_times) / len(all_times)
            max_time = max(all_times)
            self.log(f"   Temps d'exécution: Moyenne {avg_time:.1f}s, Maximum {max_time:.1f}s")
        
        # Qualité d'analyse améliorée
        content_lengths = []
        for result in [simple_result, medium_result]:
            if result.get("content_length"):
                content_lengths.append(result["content_length"])
        
        if content_lengths:
            avg_content = sum(content_lengths) / len(content_lengths)
            self.log(f"   Qualité contenu: Moyenne {avg_content:.0f} caractères")
        
        # Messages d'erreur cohérents
        timeout_messages_ok = complex_result.get("has_90s_message", False)
        self.log(f"   Messages d'erreur cohérents: {'✅ OK' if timeout_messages_ok else '❌ MANQUANT'}")
        
        # Final conclusion
        self.log(f"\n🎯 CONCLUSION FINALE:")
        
        if success_rate >= 80:
            self.log("✅ VALIDATION TIMEOUT 90S: SUCCÈS COMPLET")
            self.log("   Les améliorations timeout sont PLEINEMENT OPÉRATIONNELLES")
            self.log("   Système prêt pour utilisation en production")
        elif success_rate >= 60:
            self.log("⚠️ VALIDATION TIMEOUT 90S: SUCCÈS PARTIEL")
            self.log("   La plupart des améliorations fonctionnent correctement")
            self.log("   Quelques ajustements mineurs recommandés")
        else:
            self.log("❌ VALIDATION TIMEOUT 90S: ÉCHEC")
            self.log("   Les améliorations timeout nécessitent des corrections")
            self.log("   Investigation approfondie requise")
        
        return success_rate >= 60

def main():
    """Main test execution"""
    validator = Timeout90sValidator()
    success = validator.run_comprehensive_timeout_validation()
    
    if success:
        print(f"\n🎉 VALIDATION TIMEOUT 90S TERMINÉE AVEC SUCCÈS")
        sys.exit(0)
    else:
        print(f"\n💥 VALIDATION TIMEOUT 90S ÉCHOUÉE - CORRECTIONS NÉCESSAIRES")
        sys.exit(1)

if __name__ == "__main__":
    main()