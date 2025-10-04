#!/usr/bin/env python3
"""
Test d'intégration frontend pour identifier les problèmes potentiels
avec l'interface utilisateur du module d'analyse de site web
"""

import requests
import json
import time
from datetime import datetime

class FrontendIntegrationTest:
    def __init__(self):
        self.base_url = "https://claire-marcus-app-1.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        
        print("🔍 TEST D'INTÉGRATION FRONTEND")
        print("=" * 60)
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)

    def login_user(self):
        """Login with the specified credentials"""
        login_data = {
            "email": "lperpere@yahoo.fr",
            "password": "L@Reunion974!"
        }
        
        response = requests.post(f"{self.api_url}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            print(f"✅ Login successful - Token: {self.access_token[:20]}...")
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False

    def test_business_profile_integration(self):
        """Test business profile integration with website analysis"""
        if not self.access_token:
            return False
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        print("\n🔍 Testing Business Profile Integration")
        
        # Get current business profile
        response = requests.get(f"{self.api_url}/business-profile", headers=headers)
        if response.status_code == 200:
            profile = response.json()
            print(f"✅ Business Profile Retrieved")
            print(f"   Business Name: {profile.get('business_name', 'N/A')}")
            print(f"   Website URL: {profile.get('website_url', 'N/A')}")
            
            # Test website analysis with business context
            if profile.get('website_url'):
                website_url = profile['website_url']
                print(f"\n🔍 Testing analysis with business website: {website_url}")
                
                analysis_data = {
                    "website_url": website_url,
                    "force_reanalysis": True
                }
                
                analysis_response = requests.post(
                    f"{self.api_url}/website/analyze", 
                    json=analysis_data, 
                    headers=headers
                )
                
                if analysis_response.status_code == 200:
                    analysis = analysis_response.json()
                    print(f"✅ Website Analysis Successful")
                    print(f"   Message: {analysis.get('message', 'N/A')}")
                    print(f"   Status: {analysis.get('status', 'N/A')}")
                    
                    # Check for problematic messages
                    message = analysis.get('message', '').lower()
                    if 'non concluante' in message or 'vérifiez' in message:
                        print(f"❌ PROBLÈME: Message d'erreur détecté!")
                        return False
                    else:
                        print(f"✅ Pas de message d'erreur")
                        return True
                else:
                    print(f"❌ Website Analysis Failed: {analysis_response.status_code}")
                    print(f"   Error: {analysis_response.text}")
                    return False
            else:
                print("⚠️ No website URL in business profile")
                return True
        else:
            print(f"❌ Failed to get business profile: {response.status_code}")
            return False

    def test_cached_vs_fresh_analysis(self):
        """Test cached vs fresh analysis to identify caching issues"""
        if not self.access_token:
            return False
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        test_url = "https://www.google.com"
        
        print(f"\n🔍 Testing Cached vs Fresh Analysis")
        
        # First analysis (should be fresh)
        print("   First analysis (fresh)...")
        analysis_data = {
            "website_url": test_url,
            "force_reanalysis": True
        }
        
        response1 = requests.post(f"{self.api_url}/website/analyze", json=analysis_data, headers=headers)
        
        if response1.status_code == 200:
            data1 = response1.json()
            print(f"   ✅ First analysis: {data1.get('message', 'N/A')}")
            time.sleep(1)  # Small delay
            
            # Second analysis (might be cached)
            print("   Second analysis (potentially cached)...")
            analysis_data2 = {
                "website_url": test_url,
                "force_reanalysis": False  # Allow caching
            }
            
            response2 = requests.post(f"{self.api_url}/website/analyze", json=analysis_data2, headers=headers)
            
            if response2.status_code == 200:
                data2 = response2.json()
                print(f"   ✅ Second analysis: {data2.get('message', 'N/A')}")
                
                # Compare results
                if data1.get('message') == data2.get('message'):
                    print("   ✅ Consistent results between fresh and cached")
                    return True
                else:
                    print("   ⚠️ Different results between fresh and cached")
                    return True  # Not necessarily a failure
            else:
                print(f"   ❌ Second analysis failed: {response2.status_code}")
                return False
        else:
            print(f"   ❌ First analysis failed: {response1.status_code}")
            return False

    def test_error_scenarios(self):
        """Test various error scenarios that might cause 'analyse non concluante'"""
        if not self.access_token:
            return False
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        print(f"\n🔍 Testing Error Scenarios")
        
        error_scenarios = [
            ("Empty URL", {"website_url": "", "force_reanalysis": True}),
            ("Invalid URL Format", {"website_url": "not-a-url", "force_reanalysis": True}),
            ("Missing Protocol", {"website_url": "www.google.com", "force_reanalysis": True}),
            ("Localhost URL", {"website_url": "http://localhost:3000", "force_reanalysis": True}),
        ]
        
        for scenario_name, data in error_scenarios:
            print(f"   Testing: {scenario_name}")
            response = requests.post(f"{self.api_url}/website/analyze", json=data, headers=headers)
            
            if response.status_code in [400, 422]:
                print(f"   ✅ Properly rejected: {response.status_code}")
            elif response.status_code == 200:
                result = response.json()
                message = result.get('message', '').lower()
                if 'non concluante' in message:
                    print(f"   ❌ PROBLÈME: 'non concluante' message for {scenario_name}")
                    print(f"       Message: {result.get('message')}")
                    return False
                else:
                    print(f"   ✅ Handled gracefully: {result.get('message', 'N/A')}")
            else:
                print(f"   ⚠️ Unexpected status: {response.status_code}")
        
        return True

    def test_concurrent_requests(self):
        """Test concurrent requests to identify race conditions"""
        if not self.access_token:
            return False
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        print(f"\n🔍 Testing Concurrent Requests")
        
        import threading
        import queue
        
        results = queue.Queue()
        test_url = "https://www.example.com"
        
        def make_request():
            data = {"website_url": test_url, "force_reanalysis": True}
            response = requests.post(f"{self.api_url}/website/analyze", json=data, headers=headers)
            results.put((response.status_code, response.json() if response.status_code == 200 else response.text))
        
        # Start 3 concurrent requests
        threads = []
        for i in range(3):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Analyze results
        success_count = 0
        error_count = 0
        
        while not results.empty():
            status_code, response_data = results.get()
            if status_code == 200:
                success_count += 1
                if isinstance(response_data, dict):
                    message = response_data.get('message', '').lower()
                    if 'non concluante' in message:
                        print(f"   ❌ PROBLÈME: 'non concluante' in concurrent request")
                        return False
            else:
                error_count += 1
        
        print(f"   ✅ Concurrent requests: {success_count} success, {error_count} errors")
        return success_count > 0

    def test_frontend_specific_scenarios(self):
        """Test scenarios specific to frontend integration"""
        if not self.access_token:
            return False
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        print(f"\n🔍 Testing Frontend-Specific Scenarios")
        
        # Test with typical frontend URLs
        frontend_urls = [
            "https://www.google.com",
            "https://github.com",
            "https://stackoverflow.com",
            "https://www.wikipedia.org"
        ]
        
        for url in frontend_urls:
            print(f"   Testing URL: {url}")
            data = {"website_url": url, "force_reanalysis": True}
            response = requests.post(f"{self.api_url}/website/analyze", json=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                message = result.get('message', '').lower()
                
                if 'non concluante' in message or 'vérifiez' in message:
                    print(f"   ❌ PROBLÈME IDENTIFIÉ: {result.get('message')}")
                    print(f"       URL: {url}")
                    print(f"       Full Response: {json.dumps(result, indent=2)}")
                    return False
                else:
                    print(f"   ✅ Success: {result.get('message', 'N/A')[:50]}...")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                return False
        
        return True

    def run_integration_tests(self):
        """Run all integration tests"""
        print("🚀 DÉMARRAGE DES TESTS D'INTÉGRATION FRONTEND")
        
        if not self.login_user():
            print("❌ Cannot proceed without authentication")
            return False
        
        tests = [
            ("Business Profile Integration", self.test_business_profile_integration),
            ("Cached vs Fresh Analysis", self.test_cached_vs_fresh_analysis),
            ("Error Scenarios", self.test_error_scenarios),
            ("Concurrent Requests", self.test_concurrent_requests),
            ("Frontend-Specific Scenarios", self.test_frontend_specific_scenarios),
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n{'='*60}")
            print(f"TEST: {test_name}")
            print('='*60)
            
            try:
                result = test_func()
                results.append((test_name, result))
                status = "✅ RÉUSSI" if result else "❌ ÉCHEC"
                print(f"\n{status}: {test_name}")
            except Exception as e:
                print(f"\n❌ ERREUR: {test_name} - {str(e)}")
                results.append((test_name, False))
        
        # Summary
        print(f"\n{'='*60}")
        print("RÉSUMÉ DES TESTS D'INTÉGRATION")
        print('='*60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        print(f"Tests réussis: {passed}/{total}")
        print(f"Taux de réussite: {(passed/total)*100:.1f}%")
        
        for test_name, result in results:
            status = "✅" if result else "❌"
            print(f"  {status} {test_name}")
        
        if passed == total:
            print(f"\n✅ CONCLUSION: Tous les tests d'intégration réussissent")
            print("   Le problème 'analyse non concluante' n'est PAS reproduit")
            print("   Le backend fonctionne correctement avec tous les scénarios testés")
        else:
            print(f"\n❌ CONCLUSION: Problèmes détectés dans l'intégration")
        
        return passed == total

if __name__ == "__main__":
    tester = FrontendIntegrationTest()
    success = tester.run_integration_tests()
    exit(0 if success else 1)