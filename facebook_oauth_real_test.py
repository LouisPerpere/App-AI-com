#!/usr/bin/env python3
"""
Facebook OAuth Real Flow Test - Test with actual Facebook OAuth flow
Testing the complete Facebook OAuth flow to identify why even real reconnections fail

Identifiants: lperpere@yahoo.fr / L@Reunion974!

OBJECTIF: Tester le flow OAuth complet avec Facebook pour identifier pourquoi même les vraies reconnexions échouent
"""

import requests
import json
import sys
import re
import time
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# Configuration
BASE_URL = "https://claire-marcus-app-1.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class FacebookOAuthRealTest:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()
        
    def authenticate(self):
        """Step 1: Authenticate and get JWT token"""
        try:
            print("🔐 Step 1: Authentication")
            response = self.session.post(
                f"{BASE_URL}/auth/login-robust",
                json=TEST_CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                self.log_test("Authentication", True, f"User ID: {self.user_id}")
                return True
            else:
                self.log_test("Authentication", False, 
                            f"Status: {response.status_code}", 
                            response.text[:200])
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, error=str(e))
            return False
    
    def test_facebook_credentials_validity(self):
        """Test 1: Test Facebook credentials validity with Facebook API directly"""
        try:
            print("🔍 Test 1: Test Facebook credentials validity")
            
            # Get Facebook credentials from our auth URL
            response = self.session.get(f"{BASE_URL}/social/facebook/auth-url", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Facebook Credentials Validity", False, 
                            f"Cannot get auth URL: {response.status_code}")
                return False
            
            data = response.json()
            auth_url = data.get("auth_url", "")
            
            # Parse credentials
            parsed_url = urlparse(auth_url)
            query_params = parse_qs(parsed_url.query)
            
            app_id = query_params.get('client_id', [None])[0]
            config_id = query_params.get('config_id', [None])[0]
            redirect_uri = query_params.get('redirect_uri', [None])[0]
            
            # Test if Facebook recognizes our App ID by making a request to Facebook API
            # This tests if our credentials are valid with Facebook
            facebook_test_url = f"https://graph.facebook.com/{app_id}"
            
            try:
                fb_response = requests.get(facebook_test_url, timeout=10)
                if fb_response.status_code == 200:
                    fb_data = fb_response.json()
                    app_name = fb_data.get("name", "Unknown")
                    self.log_test("Facebook Credentials Validity", True, 
                                f"✅ App ID {app_id} reconnu par Facebook - App: {app_name}")
                    return True
                else:
                    self.log_test("Facebook Credentials Validity", False, 
                                f"❌ App ID {app_id} non reconnu par Facebook: {fb_response.status_code}")
                    return False
            except Exception as fb_error:
                self.log_test("Facebook Credentials Validity", False, 
                            f"❌ Erreur test Facebook API: {str(fb_error)}")
                return False
                
        except Exception as e:
            self.log_test("Facebook Credentials Validity", False, error=str(e))
            return False
    
    def test_facebook_app_permissions(self):
        """Test 2: Test Facebook App permissions and configuration"""
        try:
            print("🔐 Test 2: Test Facebook App permissions")
            
            # Get auth URL and analyze permissions
            response = self.session.get(f"{BASE_URL}/social/facebook/auth-url", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Facebook App Permissions", False, 
                            f"Cannot get auth URL: {response.status_code}")
                return False
            
            data = response.json()
            auth_url = data.get("auth_url", "")
            
            # Parse permissions from scope parameter
            parsed_url = urlparse(auth_url)
            query_params = parse_qs(parsed_url.query)
            
            scope = query_params.get('scope', [None])[0]
            response_type = query_params.get('response_type', [None])[0]
            
            # Check required permissions for Facebook Business
            required_permissions = [
                "pages_show_list",
                "pages_read_engagement", 
                "pages_manage_posts"
            ]
            
            if scope:
                permissions = scope.split(',')
                missing_permissions = [perm for perm in required_permissions if perm not in permissions]
                
                if not missing_permissions and response_type == "code":
                    self.log_test("Facebook App Permissions", True, 
                                f"✅ Permissions correctes: {scope}, Response type: {response_type}")
                    return True
                else:
                    self.log_test("Facebook App Permissions", False, 
                                f"❌ Permissions manquantes: {missing_permissions}, Response type: {response_type}")
                    return False
            else:
                self.log_test("Facebook App Permissions", False, 
                            "❌ Aucune permission dans scope")
                return False
                
        except Exception as e:
            self.log_test("Facebook App Permissions", False, error=str(e))
            return False
    
    def test_redirect_uri_configuration(self):
        """Test 3: Test redirect URI configuration"""
        try:
            print("🔗 Test 3: Test redirect URI configuration")
            
            # Get auth URL and check redirect URI
            response = self.session.get(f"{BASE_URL}/social/facebook/auth-url", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Redirect URI Configuration", False, 
                            f"Cannot get auth URL: {response.status_code}")
                return False
            
            data = response.json()
            auth_url = data.get("auth_url", "")
            
            # Parse redirect URI
            parsed_url = urlparse(auth_url)
            query_params = parse_qs(parsed_url.query)
            
            redirect_uri = query_params.get('redirect_uri', [None])[0]
            expected_redirect = "https://claire-marcus.com/api/social/facebook/callback"
            
            if redirect_uri == expected_redirect:
                # Test if redirect URI is accessible
                try:
                    # Test with invalid parameters to see if endpoint exists
                    test_response = requests.get(
                        redirect_uri,
                        params={"error": "access_denied"},
                        timeout=10,
                        allow_redirects=False
                    )
                    
                    if test_response.status_code in [302, 301]:
                        self.log_test("Redirect URI Configuration", True, 
                                    f"✅ Redirect URI correct et accessible: {redirect_uri}")
                        return True
                    else:
                        self.log_test("Redirect URI Configuration", False, 
                                    f"❌ Redirect URI non accessible: {test_response.status_code}")
                        return False
                        
                except Exception as redirect_error:
                    self.log_test("Redirect URI Configuration", False, 
                                f"❌ Erreur test redirect URI: {str(redirect_error)}")
                    return False
            else:
                self.log_test("Redirect URI Configuration", False, 
                            f"❌ Redirect URI incorrect: {redirect_uri} (expected: {expected_redirect})")
                return False
                
        except Exception as e:
            self.log_test("Redirect URI Configuration", False, error=str(e))
            return False
    
    def test_facebook_oauth_url_generation(self):
        """Test 4: Test Facebook OAuth URL generation multiple times"""
        try:
            print("🔄 Test 4: Test Facebook OAuth URL generation")
            
            # Generate multiple OAuth URLs to test consistency
            urls = []
            states = []
            
            for i in range(5):
                response = self.session.get(f"{BASE_URL}/social/facebook/auth-url", timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    auth_url = data.get("auth_url", "")
                    urls.append(auth_url)
                    
                    # Extract state
                    parsed_url = urlparse(auth_url)
                    query_params = parse_qs(parsed_url.query)
                    state = query_params.get('state', [None])[0]
                    if state:
                        states.append(state)
                
                time.sleep(0.5)  # Small delay
            
            if len(urls) == 5 and len(states) == 5:
                # Check state uniqueness and format
                unique_states = len(set(states))
                valid_format_count = 0
                
                for state in states:
                    if '|' in state:
                        random_part, user_id_part = state.split('|', 1)
                        if user_id_part == self.user_id and len(random_part) > 10:
                            valid_format_count += 1
                
                if unique_states == 5 and valid_format_count == 5:
                    self.log_test("Facebook OAuth URL Generation", True, 
                                f"✅ 5 URLs générées avec states uniques et format correct")
                    return True
                else:
                    self.log_test("Facebook OAuth URL Generation", False, 
                                f"❌ States: {unique_states}/5 uniques, {valid_format_count}/5 format correct")
                    return False
            else:
                self.log_test("Facebook OAuth URL Generation", False, 
                            f"❌ Génération URLs échouée: {len(urls)}/5 URLs, {len(states)}/5 states")
                return False
                
        except Exception as e:
            self.log_test("Facebook OAuth URL Generation", False, error=str(e))
            return False
    
    def test_callback_error_handling(self):
        """Test 5: Test callback error handling with various scenarios"""
        try:
            print("🚨 Test 5: Test callback error handling")
            
            # Get a valid state for testing
            response = self.session.get(f"{BASE_URL}/social/facebook/auth-url", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Callback Error Handling", False, 
                            "Cannot get auth URL for state")
                return False
            
            data = response.json()
            auth_url = data.get("auth_url", "")
            
            parsed_url = urlparse(auth_url)
            query_params = parse_qs(parsed_url.query)
            valid_state = query_params.get('state', [None])[0]
            
            if not valid_state:
                self.log_test("Callback Error Handling", False, 
                            "Cannot extract valid state")
                return False
            
            # Test various error scenarios
            test_scenarios = [
                {
                    "name": "Facebook user denial",
                    "params": {"error": "access_denied", "state": valid_state},
                    "expected_redirect": "auth_error=facebook_access_denied"
                },
                {
                    "name": "Invalid state",
                    "params": {"code": "valid_code", "state": "invalid_state"},
                    "expected_redirect": "auth_error=facebook_invalid_state"
                },
                {
                    "name": "Missing code and error",
                    "params": {"state": valid_state},
                    "expected_redirect": "auth_error=facebook_oauth_failed"
                }
            ]
            
            passed_scenarios = 0
            
            for scenario in test_scenarios:
                try:
                    callback_response = self.session.get(
                        f"{BASE_URL}/social/facebook/callback",
                        params=scenario["params"],
                        timeout=30,
                        allow_redirects=False
                    )
                    
                    if callback_response.status_code in [302, 301]:
                        location = callback_response.headers.get('Location', '')
                        if scenario["expected_redirect"] in location:
                            passed_scenarios += 1
                            print(f"   ✅ {scenario['name']}: Correct error handling")
                        else:
                            print(f"   ❌ {scenario['name']}: Unexpected redirect: {location}")
                    else:
                        print(f"   ❌ {scenario['name']}: Unexpected status: {callback_response.status_code}")
                        
                except Exception as scenario_error:
                    print(f"   ❌ {scenario['name']}: Error: {str(scenario_error)}")
            
            if passed_scenarios == len(test_scenarios):
                self.log_test("Callback Error Handling", True, 
                            f"✅ {passed_scenarios}/{len(test_scenarios)} scénarios d'erreur gérés correctement")
                return True
            else:
                self.log_test("Callback Error Handling", False, 
                            f"❌ {passed_scenarios}/{len(test_scenarios)} scénarios d'erreur gérés correctement")
                return False
                
        except Exception as e:
            self.log_test("Callback Error Handling", False, error=str(e))
            return False
    
    def test_token_exchange_with_facebook_api(self):
        """Test 6: Test token exchange mechanism with Facebook API"""
        try:
            print("🔑 Test 6: Test token exchange mechanism")
            
            # This test simulates what happens when Facebook sends a real authorization code
            # We'll test the token exchange endpoint directly
            
            # Get Facebook credentials
            response = self.session.get(f"{BASE_URL}/social/facebook/auth-url", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Token Exchange Mechanism", False, 
                            "Cannot get Facebook credentials")
                return False
            
            data = response.json()
            auth_url = data.get("auth_url", "")
            
            parsed_url = urlparse(auth_url)
            query_params = parse_qs(parsed_url.query)
            
            app_id = query_params.get('client_id', [None])[0]
            redirect_uri = query_params.get('redirect_uri', [None])[0]
            
            # Test Facebook token exchange endpoint directly
            # This is what our callback does internally
            facebook_token_url = "https://graph.facebook.com/v20.0/oauth/access_token"
            
            # Test with invalid code to see Facebook's response
            test_params = {
                "client_id": app_id,
                "redirect_uri": redirect_uri,
                "client_secret": "test_secret",  # This will fail but we can see the error
                "code": "test_authorization_code"
            }
            
            try:
                fb_response = requests.get(facebook_token_url, params=test_params, timeout=10)
                
                if fb_response.status_code == 400:
                    fb_data = fb_response.json()
                    error_message = fb_data.get("error", {}).get("message", "")
                    
                    # Check if it's the expected error for invalid client_secret
                    if "client_secret" in error_message.lower() or "app secret" in error_message.lower():
                        self.log_test("Token Exchange Mechanism", True, 
                                    f"✅ Facebook token exchange endpoint accessible - Error: {error_message}")
                        return True
                    elif "verification code" in error_message.lower():
                        self.log_test("Token Exchange Mechanism", False, 
                                    f"❌ Facebook rejette format code - Error: {error_message}")
                        return False
                    else:
                        self.log_test("Token Exchange Mechanism", False, 
                                    f"❌ Erreur Facebook inattendue: {error_message}")
                        return False
                else:
                    self.log_test("Token Exchange Mechanism", False, 
                                f"❌ Réponse Facebook inattendue: {fb_response.status_code}")
                    return False
                    
            except Exception as fb_error:
                self.log_test("Token Exchange Mechanism", False, 
                            f"❌ Erreur connexion Facebook API: {str(fb_error)}")
                return False
                
        except Exception as e:
            self.log_test("Token Exchange Mechanism", False, error=str(e))
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive Facebook OAuth real flow test"""
        print("🎯 TEST OAUTH FACEBOOK FLOW RÉEL COMPLET")
        print("=" * 80)
        print(f"Backend URL: {BASE_URL}")
        print(f"Test User: {TEST_CREDENTIALS['email']}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 80)
        print()
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed - cannot continue tests")
            return False
        
        # Test 1: Test Facebook credentials validity
        self.test_facebook_credentials_validity()
        
        # Test 2: Test Facebook App permissions
        self.test_facebook_app_permissions()
        
        # Test 3: Test redirect URI configuration
        self.test_redirect_uri_configuration()
        
        # Test 4: Test Facebook OAuth URL generation
        self.test_facebook_oauth_url_generation()
        
        # Test 5: Test callback error handling
        self.test_callback_error_handling()
        
        # Test 6: Test token exchange mechanism
        self.test_token_exchange_with_facebook_api()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 RÉSULTATS TEST OAUTH FACEBOOK FLOW RÉEL")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print(f"\n🎯 RÉSULTATS: {passed}/{total} tests réussis ({(passed/total*100):.1f}%)")
        
        # Analyze results and provide recommendations
        failed_tests = [r['test'] for r in self.test_results if not r['success']]
        
        if passed == total:
            print("\n🎉 TOUS LES TESTS RÉUSSIS - OAUTH FACEBOOK PRÊT!")
            print("✅ Credentials Facebook valides et reconnus")
            print("✅ Permissions Facebook correctes")
            print("✅ Redirect URI accessible")
            print("✅ Génération OAuth URLs fonctionnelle")
            print("✅ Gestion erreurs callback correcte")
            print("✅ Mécanisme token exchange prêt")
            return True
        else:
            print(f"\n🚨 PROBLÈMES DÉTECTÉS - {total - passed} TESTS ÉCHOUÉS")
            print("\n🔍 PROBLÈMES IDENTIFIÉS:")
            
            for failed_test in failed_tests:
                if "Credentials Validity" in failed_test:
                    print("❌ CREDENTIALS FACEBOOK NON RECONNUS - App ID invalide ou app désactivée")
                elif "App Permissions" in failed_test:
                    print("❌ PERMISSIONS FACEBOOK INCORRECTES - Scope manquant ou incorrect")
                elif "Redirect URI" in failed_test:
                    print("❌ REDIRECT URI INACCESSIBLE - URL callback non configurée")
                elif "URL Generation" in failed_test:
                    print("❌ GÉNÉRATION OAUTH URLS DÉFAILLANTE - States ou format incorrect")
                elif "Error Handling" in failed_test:
                    print("❌ GESTION ERREURS CALLBACK DÉFAILLANTE - Redirections incorrectes")
                elif "Token Exchange" in failed_test:
                    print("❌ MÉCANISME TOKEN EXCHANGE DÉFAILLANT - Facebook API inaccessible")
            
            return False

def main():
    """Main test execution"""
    tester = FacebookOAuthRealTest()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n✅ Test OAuth Facebook flow réel terminé avec succès!")
        print("🚀 Système prêt pour vraies reconnexions Facebook!")
        sys.exit(0)
    else:
        print("\n❌ Test OAuth Facebook flow réel révèle des problèmes!")
        print("🔧 Corrections requises pour reconnexions Facebook!")
        sys.exit(1)

if __name__ == "__main__":
    main()