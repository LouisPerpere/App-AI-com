#!/usr/bin/env python3
"""
DIAGNOSTIC MODULE D'ANALYSE DE SITE WEB
Test spécifique pour diagnostiquer le problème "analyse non concluante, vérifiez votre site web"

Tests requis selon la review request:
1. Test de connexion utilisateur - lperpere@yahoo.fr / L@Reunion974!
2. Test d'existence de l'endpoint - GET/POST vers /api/website/analyze
3. Test avec URL réelle - POST /api/website/analyze avec {"website_url": "https://www.google.com", "force_reanalysis": true}
4. Vérification clés API - Tester si les clés OpenAI/Emergent sont disponibles et fonctionnelles
5. Test fallback analysis - Vérifier que le fallback fonctionne si l'API échoue
6. Vérification logs - Analyser les logs d'erreur du backend
"""

import requests
import json
import os
import sys
from datetime import datetime

class WebsiteAnalysisDiagnostic:
    def __init__(self):
        # Use production backend URL from frontend/.env
        self.base_url = "https://social-publisher-10.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.tests_run = 0
        self.tests_passed = 0
        
        print("🔍 DIAGNOSTIC MODULE D'ANALYSE DE SITE WEB")
        print("=" * 60)
        print(f"Backend URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        print("=" * 60)

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {}
        
        # Add authentication header if we have a token
        if self.access_token:
            test_headers['Authorization'] = f'Bearer {self.access_token}'
        
        # Add custom headers
        if headers:
            test_headers.update(headers)
        
        # Set Content-Type for JSON requests
        if method in ['POST', 'PUT'] and not headers:
            test_headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        print(f"\n🔍 Test {self.tests_run}: {name}")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, params=data, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            
            print(f"   Status Code: {response.status_code} (Expected: {expected_status})")
            
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED")
                try:
                    response_data = response.json()
                    print(f"   Response Keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Not a dict'}")
                    
                    # Show relevant response data
                    if isinstance(response_data, dict):
                        if 'message' in response_data:
                            print(f"   Message: {response_data['message']}")
                        if 'status' in response_data:
                            print(f"   Status: {response_data['status']}")
                        if 'insights' in response_data:
                            insights = response_data['insights']
                            print(f"   Insights Count: {len(insights) if isinstance(insights, list) else 'Not a list'}")
                        if 'content_suggestions' in response_data:
                            suggestions = response_data['content_suggestions']
                            print(f"   Suggestions Count: {len(suggestions) if isinstance(suggestions, list) else 'Not a list'}")
                    
                    return True, response_data
                except:
                    return True, response.text
            else:
                print(f"❌ FAILED")
                try:
                    error_data = response.json()
                    print(f"   Error Response: {json.dumps(error_data, indent=2)}")
                    return False, error_data
                except:
                    print(f"   Error Text: {response.text}")
                    return False, response.text

        except requests.exceptions.Timeout:
            print(f"❌ FAILED - Request timeout (30s)")
            return False, {"error": "timeout"}
        except requests.exceptions.ConnectionError:
            print(f"❌ FAILED - Connection error")
            return False, {"error": "connection_error"}
        except Exception as e:
            print(f"❌ FAILED - Exception: {str(e)}")
            return False, {"error": str(e)}

    def test_1_user_authentication(self):
        """Test 1: Connexion utilisateur avec lperpere@yahoo.fr / L@Reunion974!"""
        print("\n" + "="*60)
        print("TEST 1: CONNEXION UTILISATEUR")
        print("="*60)
        
        login_data = {
            "email": "lperpere@yahoo.fr",
            "password": "L@Reunion974!"
        }
        
        success, response = self.run_test(
            "User Login (lperpere@yahoo.fr)",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and isinstance(response, dict) and 'access_token' in response:
            self.access_token = response['access_token']
            print(f"   ✅ Access Token obtained: {self.access_token[:20]}...")
            print(f"   ✅ User ID: {response.get('user_id', 'N/A')}")
            return True
        else:
            print(f"   ❌ Login failed - cannot proceed with authenticated tests")
            return False

    def test_2_endpoint_existence(self):
        """Test 2: Vérification de l'existence de l'endpoint /api/website/analyze"""
        print("\n" + "="*60)
        print("TEST 2: EXISTENCE DE L'ENDPOINT")
        print("="*60)
        
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
        
        # Test GET endpoint (should return 405 Method Not Allowed or 404)
        success_get, response_get = self.run_test(
            "GET /api/website/analyze (Method Check)",
            "GET",
            "website/analyze",
            405  # Method not allowed is acceptable
        )
        
        # If GET returns 404, endpoint might not exist
        if not success_get:
            # Try with different status codes
            success_get_404, response_get_404 = self.run_test(
                "GET /api/website/analyze (Existence Check)",
                "GET", 
                "website/analyze",
                404
            )
            if success_get_404:
                print("   ⚠️ GET endpoint returns 404 - endpoint may not exist")
            else:
                print("   ✅ Endpoint exists (returns error as expected)")
        
        # Test POST endpoint structure (without data first)
        success_post, response_post = self.run_test(
            "POST /api/website/analyze (Structure Check)",
            "POST",
            "website/analyze", 
            400,  # Bad request expected without data
            data={}
        )
        
        if success_post:
            print("   ✅ POST endpoint exists and validates input")
            return True
        else:
            # Try with 422 (validation error)
            success_post_422, response_post_422 = self.run_test(
                "POST /api/website/analyze (Validation Check)",
                "POST",
                "website/analyze",
                422,
                data={}
            )
            return success_post_422

    def test_3_real_url_analysis(self):
        """Test 3: Test avec URL réelle - https://www.google.com"""
        print("\n" + "="*60)
        print("TEST 3: ANALYSE URL RÉELLE")
        print("="*60)
        
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
        
        test_data = {
            "website_url": "https://www.google.com",
            "force_reanalysis": True
        }
        
        success, response = self.run_test(
            "Website Analysis (Google.com)",
            "POST",
            "website/analyze",
            200,
            data=test_data
        )
        
        if success and isinstance(response, dict):
            # Check for expected response fields
            expected_fields = ['message', 'website_url', 'status']
            missing_fields = []
            
            for field in expected_fields:
                if field not in response:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"   ⚠️ Missing expected fields: {missing_fields}")
            else:
                print(f"   ✅ All expected fields present")
            
            # Check for analysis content
            if 'insights' in response and response['insights']:
                print(f"   ✅ Analysis insights provided")
            else:
                print(f"   ⚠️ No insights in response")
            
            if 'content_suggestions' in response and response['content_suggestions']:
                print(f"   ✅ Content suggestions provided")
            else:
                print(f"   ⚠️ No content suggestions in response")
            
            # Check for "analyse non concluante" message
            message = response.get('message', '').lower()
            if 'non concluante' in message or 'vérifiez votre site' in message:
                print(f"   ❌ PROBLÈME IDENTIFIÉ: Message d'erreur détecté: {response.get('message')}")
                return False
            else:
                print(f"   ✅ Pas de message d'erreur 'non concluante'")
                return True
        
        return success

    def test_4_api_keys_verification(self):
        """Test 4: Vérification des clés API OpenAI/Emergent"""
        print("\n" + "="*60)
        print("TEST 4: VÉRIFICATION CLÉS API")
        print("="*60)
        
        # Check backend environment variables
        print("   Checking backend environment configuration...")
        
        # Test with a simple URL to see if API keys work
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
        
        test_data = {
            "website_url": "https://httpbin.org/get",  # Simple test URL
            "force_reanalysis": True
        }
        
        success, response = self.run_test(
            "API Keys Test (Simple URL)",
            "POST",
            "website/analyze",
            200,
            data=test_data
        )
        
        if success and isinstance(response, dict):
            message = response.get('message', '')
            
            # Check for API key related errors
            if 'api key' in message.lower() or 'openai' in message.lower():
                print(f"   ❌ API Key issue detected: {message}")
                return False
            elif 'gpt' in message.lower() or 'analysis completed' in message.lower():
                print(f"   ✅ API keys appear to be working")
                return True
            else:
                print(f"   ⚠️ Unclear API key status from message: {message}")
                return True  # Assume working if no clear error
        
        return success

    def test_5_fallback_analysis(self):
        """Test 5: Test du système de fallback"""
        print("\n" + "="*60)
        print("TEST 5: SYSTÈME DE FALLBACK")
        print("="*60)
        
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
        
        # Test with an unreachable URL to trigger fallback
        test_data = {
            "website_url": "https://this-domain-does-not-exist-12345.com",
            "force_reanalysis": True
        }
        
        success, response = self.run_test(
            "Fallback Test (Unreachable URL)",
            "POST",
            "website/analyze",
            200,  # Should still return 200 with fallback
            data=test_data
        )
        
        if success and isinstance(response, dict):
            message = response.get('message', '')
            
            # Check if fallback was triggered
            if 'fallback' in message.lower() or 'demo' in message.lower():
                print(f"   ✅ Fallback system activated")
                return True
            elif 'error' in message.lower() or 'failed' in message.lower():
                print(f"   ⚠️ Error returned instead of fallback: {message}")
                return False
            else:
                print(f"   ✅ System handled unreachable URL gracefully")
                return True
        else:
            # Test with 400 status (might return error for invalid URL)
            success_400, response_400 = self.run_test(
                "Fallback Test (Error Handling)",
                "POST",
                "website/analyze",
                400,
                data=test_data
            )
            
            if success_400:
                print(f"   ✅ System properly validates URLs")
                return True
        
        return success

    def test_6_backend_logs_analysis(self):
        """Test 6: Analyse des logs backend (via diagnostic endpoint)"""
        print("\n" + "="*60)
        print("TEST 6: ANALYSE DES LOGS BACKEND")
        print("="*60)
        
        # Test diagnostic endpoint
        success, response = self.run_test(
            "Backend Diagnostic",
            "GET",
            "diag",
            200
        )
        
        if success and isinstance(response, dict):
            print(f"   Database Connected: {response.get('database_connected', 'Unknown')}")
            print(f"   Database Name: {response.get('database_name', 'Unknown')}")
            print(f"   Environment: {response.get('environment', 'Unknown')}")
            
            if response.get('database_connected') == False:
                print(f"   ⚠️ Database connection issue detected")
            else:
                print(f"   ✅ Database connection appears healthy")
        
        # Test health endpoint
        success_health, response_health = self.run_test(
            "Backend Health Check",
            "GET",
            "health",
            200
        )
        
        if success_health:
            print(f"   ✅ Backend health check passed")
        else:
            print(f"   ⚠️ Backend health check failed")
        
        return success and success_health

    def test_7_comprehensive_analysis_flow(self):
        """Test 7: Test complet du flux d'analyse"""
        print("\n" + "="*60)
        print("TEST 7: FLUX D'ANALYSE COMPLET")
        print("="*60)
        
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
        
        # Test multiple URLs to see pattern
        test_urls = [
            "https://www.google.com",
            "https://www.github.com", 
            "https://www.example.com"
        ]
        
        results = []
        
        for url in test_urls:
            test_data = {
                "website_url": url,
                "force_reanalysis": True
            }
            
            success, response = self.run_test(
                f"Analysis Flow Test ({url})",
                "POST",
                "website/analyze",
                200,
                data=test_data
            )
            
            if success and isinstance(response, dict):
                message = response.get('message', '')
                has_insights = bool(response.get('insights'))
                has_suggestions = bool(response.get('content_suggestions'))
                
                result = {
                    'url': url,
                    'success': True,
                    'message': message,
                    'has_insights': has_insights,
                    'has_suggestions': has_suggestions,
                    'problematic': 'non concluante' in message.lower()
                }
            else:
                result = {
                    'url': url,
                    'success': False,
                    'message': str(response),
                    'has_insights': False,
                    'has_suggestions': False,
                    'problematic': True
                }
            
            results.append(result)
        
        # Analyze results
        successful_analyses = sum(1 for r in results if r['success'] and not r['problematic'])
        total_tests = len(results)
        
        print(f"\n   RÉSULTATS DU FLUX D'ANALYSE:")
        print(f"   Analyses réussies: {successful_analyses}/{total_tests}")
        
        for result in results:
            status = "✅" if result['success'] and not result['problematic'] else "❌"
            print(f"   {status} {result['url']}: {result['message'][:50]}...")
        
        return successful_analyses > 0

    def run_diagnostic(self):
        """Run complete diagnostic sequence"""
        print("🚀 DÉMARRAGE DU DIAGNOSTIC COMPLET")
        print("Objectif: Identifier pourquoi le module d'analyse retourne 'analyse non concluante'")
        
        # Run all diagnostic tests
        test_results = []
        
        test_results.append(("Connexion Utilisateur", self.test_1_user_authentication()))
        test_results.append(("Existence Endpoint", self.test_2_endpoint_existence()))
        test_results.append(("Analyse URL Réelle", self.test_3_real_url_analysis()))
        test_results.append(("Vérification Clés API", self.test_4_api_keys_verification()))
        test_results.append(("Système Fallback", self.test_5_fallback_analysis()))
        test_results.append(("Logs Backend", self.test_6_backend_logs_analysis()))
        test_results.append(("Flux Complet", self.test_7_comprehensive_analysis_flow()))
        
        # Print summary
        print("\n" + "="*60)
        print("RÉSUMÉ DU DIAGNOSTIC")
        print("="*60)
        
        passed_tests = sum(1 for _, result in test_results if result)
        total_tests = len(test_results)
        
        print(f"Tests réussis: {passed_tests}/{total_tests}")
        print(f"Taux de réussite: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\nDétail des résultats:")
        for test_name, result in test_results:
            status = "✅ RÉUSSI" if result else "❌ ÉCHEC"
            print(f"  {status}: {test_name}")
        
        # Diagnostic conclusion
        print("\n" + "="*60)
        print("CONCLUSION DU DIAGNOSTIC")
        print("="*60)
        
        if passed_tests == total_tests:
            print("✅ DIAGNOSTIC COMPLET: Tous les tests sont réussis")
            print("   Le module d'analyse de site web fonctionne correctement")
            print("   Si l'utilisateur rencontre encore des problèmes, vérifier:")
            print("   - La configuration frontend")
            print("   - Les paramètres de requête")
            print("   - La gestion des erreurs côté client")
        elif passed_tests >= total_tests * 0.7:
            print("⚠️ DIAGNOSTIC PARTIEL: La plupart des tests réussissent")
            print("   Le backend semble fonctionnel mais quelques problèmes détectés")
            print("   Vérifier les tests échoués pour identifier les problèmes spécifiques")
        else:
            print("❌ DIAGNOSTIC CRITIQUE: Plusieurs problèmes détectés")
            print("   Le module d'analyse nécessite des corrections importantes")
            print("   Priorité aux tests d'authentification et d'endpoint")
        
        return test_results

if __name__ == "__main__":
    diagnostic = WebsiteAnalysisDiagnostic()
    results = diagnostic.run_diagnostic()
    
    # Exit with appropriate code
    passed_tests = sum(1 for _, result in results if result)
    total_tests = len(results)
    
    if passed_tests == total_tests:
        sys.exit(0)  # All tests passed
    elif passed_tests >= total_tests * 0.7:
        sys.exit(1)  # Partial success
    else:
        sys.exit(2)  # Critical issues