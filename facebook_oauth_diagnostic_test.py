#!/usr/bin/env python3
"""
Facebook OAuth Callback Diagnostic Test - Real-time Diagnostic
Testing Facebook OAuth callback issues as requested in French review

Identifiants: lperpere@yahoo.fr / L@Reunion974!

PROBLÈME CRITIQUE: Même après déconnexion/reconnexion Facebook, les tokens restent invalides. 
Notre callback OAuth a encore un problème.

DIAGNOSTIC APPROFONDI REQUIS:
1. Examiner les credentials Facebook actuels
2. Analyser la dernière tentative de connexion dans les logs
3. Tester l'échange OAuth manuellement
4. Vérifier configuration App Facebook
5. Examiner le callback en détail

OBJECTIF: Identifier pourquoi même une "vraie" reconnexion produit des tokens invalides.
HYPOTHÈSE: Il y a encore un problème dans nos credentials Facebook ou dans l'échange OAuth.
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

class FacebookOAuthDiagnostic:
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
    
    def examine_facebook_credentials(self):
        """Diagnostic 1: Examiner les credentials Facebook actuels"""
        try:
            print("🔍 Diagnostic 1: Examination des credentials Facebook")
            
            # Test Facebook auth URL generation to see credentials in use
            response = self.session.get(f"{BASE_URL}/social/facebook/auth-url", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get("auth_url", "")
                
                if not auth_url:
                    self.log_test("Facebook Credentials Examination", False, 
                                "No auth_url generated")
                    return False
                
                # Parse URL to extract Facebook credentials
                parsed_url = urlparse(auth_url)
                query_params = parse_qs(parsed_url.query)
                
                client_id = query_params.get('client_id', [None])[0]
                config_id = query_params.get('config_id', [None])[0]
                redirect_uri = query_params.get('redirect_uri', [None])[0]
                
                # Verify credentials match expected values
                expected_app_id = "1115451684022643"  # From .env file
                expected_config_id = "1878388119742903"  # From .env file
                expected_redirect = "https://claire-marcus.com/api/social/facebook/callback"
                
                credentials_valid = (
                    client_id == expected_app_id and
                    config_id == expected_config_id and
                    redirect_uri == expected_redirect
                )
                
                if credentials_valid:
                    self.log_test("Facebook Credentials Examination", True, 
                                f"✅ Credentials corrects - App ID: {client_id}, Config ID: {config_id}, Redirect: {redirect_uri}")
                    return True
                else:
                    self.log_test("Facebook Credentials Examination", False, 
                                f"❌ Credentials incorrects - App ID: {client_id} (expected {expected_app_id}), Config ID: {config_id} (expected {expected_config_id}), Redirect: {redirect_uri}")
                    return False
                    
            else:
                self.log_test("Facebook Credentials Examination", False, 
                            f"Status: {response.status_code}", response.text[:200])
                return False
                
        except Exception as e:
            self.log_test("Facebook Credentials Examination", False, error=str(e))
            return False
    
    def analyze_connection_logs(self):
        """Diagnostic 2: Analyser la dernière tentative de connexion dans les logs"""
        try:
            print("📋 Diagnostic 2: Analyse des logs de connexion")
            
            # Check current social connections state
            response = self.session.get(f"{BASE_URL}/debug/social-connections", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Analyze connection state
                total_connections = data.get("total_connections", 0)
                active_connections = data.get("active_connections", 0)
                facebook_connections = data.get("facebook_connections", 0)
                instagram_connections = data.get("instagram_connections", 0)
                
                # Check for any existing connections that might indicate previous attempts
                connections_analysis = f"Total: {total_connections}, Active: {active_connections}, Facebook: {facebook_connections}, Instagram: {instagram_connections}"
                
                # Look for patterns that indicate callback issues
                if total_connections > 0 and active_connections == 0:
                    self.log_test("Connection Logs Analysis", False, 
                                f"❌ Pattern détecté: {connections_analysis} - Connexions créées mais inactives (tokens invalides)")
                    return False
                elif total_connections == 0:
                    self.log_test("Connection Logs Analysis", True, 
                                f"✅ État propre: {connections_analysis} - Prêt pour test de reconnexion")
                    return True
                else:
                    self.log_test("Connection Logs Analysis", True, 
                                f"✅ État analysé: {connections_analysis}")
                    return True
                    
            else:
                self.log_test("Connection Logs Analysis", False, 
                            f"Status: {response.status_code}", response.text[:200])
                return False
                
        except Exception as e:
            self.log_test("Connection Logs Analysis", False, error=str(e))
            return False
    
    def test_oauth_exchange_manually(self):
        """Diagnostic 3: Tester l'échange OAuth manuellement"""
        try:
            print("🔄 Diagnostic 3: Test manuel de l'échange OAuth")
            
            # Test the callback endpoint with a simulated OAuth response
            # This tests if the callback can handle a proper OAuth code exchange
            
            # First, generate a proper state parameter
            auth_response = self.session.get(f"{BASE_URL}/social/facebook/auth-url", timeout=30)
            
            if auth_response.status_code != 200:
                self.log_test("OAuth Exchange Manual Test", False, 
                            "Cannot generate auth URL for state parameter")
                return False
            
            auth_data = auth_response.json()
            auth_url = auth_data.get("auth_url", "")
            
            # Extract state parameter
            parsed_url = urlparse(auth_url)
            query_params = parse_qs(parsed_url.query)
            state_param = query_params.get('state', [None])[0]
            
            if not state_param:
                self.log_test("OAuth Exchange Manual Test", False, 
                            "No state parameter in auth URL")
                return False
            
            # Test callback with simulated parameters (this will fail at token exchange but we can see the flow)
            callback_params = {
                "code": "test_authorization_code_from_facebook",
                "state": state_param
            }
            
            # Test the callback endpoint
            callback_response = self.session.get(
                f"{BASE_URL}/social/facebook/callback",
                params=callback_params,
                timeout=30,
                allow_redirects=False  # Don't follow redirects to see the response
            )
            
            # Analyze callback response
            if callback_response.status_code in [302, 301]:  # Redirect response
                location = callback_response.headers.get('Location', '')
                
                if 'facebook_success=true' in location:
                    self.log_test("OAuth Exchange Manual Test", False, 
                                "❌ Callback retourne succès avec code de test - fallback mechanism actif")
                    return False
                elif 'facebook_invalid_state' in location:
                    self.log_test("OAuth Exchange Manual Test", False, 
                                "❌ Callback rejette state parameter - problème de validation state")
                    return False
                elif 'facebook_error' in location:
                    self.log_test("OAuth Exchange Manual Test", True, 
                                f"✅ Callback rejette correctement code de test - pas de fallback: {location}")
                    return True
                else:
                    self.log_test("OAuth Exchange Manual Test", False, 
                                f"❌ Réponse callback inattendue: {location}")
                    return False
            else:
                self.log_test("OAuth Exchange Manual Test", False, 
                            f"❌ Callback response inattendue: {callback_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("OAuth Exchange Manual Test", False, error=str(e))
            return False
    
    def verify_facebook_app_configuration(self):
        """Diagnostic 4: Vérifier configuration App Facebook"""
        try:
            print("⚙️ Diagnostic 4: Vérification configuration App Facebook")
            
            # Test both Facebook and Instagram auth URLs to verify configuration
            facebook_response = self.session.get(f"{BASE_URL}/social/facebook/auth-url", timeout=30)
            instagram_response = self.session.get(f"{BASE_URL}/social/instagram/auth-url", timeout=30)
            
            if facebook_response.status_code != 200 or instagram_response.status_code != 200:
                self.log_test("Facebook App Configuration", False, 
                            f"Cannot generate auth URLs - Facebook: {facebook_response.status_code}, Instagram: {instagram_response.status_code}")
                return False
            
            facebook_data = facebook_response.json()
            instagram_data = instagram_response.json()
            
            facebook_url = facebook_data.get("auth_url", "")
            instagram_url = instagram_data.get("auth_url", "")
            
            # Parse both URLs to verify configuration consistency
            fb_parsed = urlparse(facebook_url)
            ig_parsed = urlparse(instagram_url)
            
            fb_params = parse_qs(fb_parsed.query)
            ig_params = parse_qs(ig_parsed.query)
            
            # Verify both use same App ID but different Config IDs
            fb_client_id = fb_params.get('client_id', [None])[0]
            ig_client_id = ig_params.get('client_id', [None])[0]
            fb_config_id = fb_params.get('config_id', [None])[0]
            ig_config_id = ig_params.get('config_id', [None])[0]
            
            # Expected values
            expected_app_id = "1115451684022643"
            expected_fb_config = "1878388119742903"
            expected_ig_config = "1309694717566880"
            
            config_valid = (
                fb_client_id == expected_app_id and
                ig_client_id == expected_app_id and
                fb_config_id == expected_fb_config and
                ig_config_id == expected_ig_config
            )
            
            if config_valid:
                self.log_test("Facebook App Configuration", True, 
                            f"✅ Configuration App Facebook correcte - App ID: {fb_client_id}, FB Config: {fb_config_id}, IG Config: {ig_config_id}")
                return True
            else:
                self.log_test("Facebook App Configuration", False, 
                            f"❌ Configuration incorrecte - FB Client: {fb_client_id}, IG Client: {ig_client_id}, FB Config: {fb_config_id}, IG Config: {ig_config_id}")
                return False
                
        except Exception as e:
            self.log_test("Facebook App Configuration", False, error=str(e))
            return False
    
    def examine_callback_in_detail(self):
        """Diagnostic 5: Examiner le callback en détail"""
        try:
            print("🔬 Diagnostic 5: Examen détaillé du callback")
            
            # Test callback state validation by generating multiple auth URLs and checking state format
            auth_urls = []
            for i in range(3):
                response = self.session.get(f"{BASE_URL}/social/facebook/auth-url", timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    auth_urls.append(data.get("auth_url", ""))
                time.sleep(1)  # Small delay between requests
            
            if len(auth_urls) < 3:
                self.log_test("Callback Detail Examination", False, 
                            "Cannot generate multiple auth URLs for state analysis")
                return False
            
            # Analyze state parameter consistency
            states = []
            for url in auth_urls:
                parsed_url = urlparse(url)
                query_params = parse_qs(parsed_url.query)
                state_param = query_params.get('state', [None])[0]
                if state_param:
                    states.append(state_param)
            
            if len(states) < 3:
                self.log_test("Callback Detail Examination", False, 
                            "Cannot extract state parameters from auth URLs")
                return False
            
            # Verify all states have correct format: {random}|{user_id}
            valid_states = 0
            for state in states:
                if '|' in state:
                    random_part, user_id_part = state.split('|', 1)
                    if user_id_part == self.user_id and len(random_part) > 10:
                        valid_states += 1
            
            if valid_states == 3:
                self.log_test("Callback Detail Examination", True, 
                            f"✅ State parameter format correct dans tous les tests - Format: {{random}}|{self.user_id}")
                
                # Test callback with invalid state to verify validation
                invalid_state_test = self.session.get(
                    f"{BASE_URL}/social/facebook/callback",
                    params={"code": "test_code", "state": "invalid_state_format"},
                    timeout=30,
                    allow_redirects=False
                )
                
                if invalid_state_test.status_code in [302, 301]:
                    location = invalid_state_test.headers.get('Location', '')
                    if 'facebook_invalid_state' in location:
                        self.log_test("Callback State Validation", True, 
                                    "✅ Callback rejette correctement les states invalides")
                        return True
                    else:
                        self.log_test("Callback State Validation", False, 
                                    f"❌ Callback n'a pas rejeté state invalide: {location}")
                        return False
                else:
                    self.log_test("Callback State Validation", False, 
                                f"❌ Callback response inattendue pour state invalide: {invalid_state_test.status_code}")
                    return False
            else:
                self.log_test("Callback Detail Examination", False, 
                            f"❌ Format state incorrect - {valid_states}/3 states valides")
                return False
                
        except Exception as e:
            self.log_test("Callback Detail Examination", False, error=str(e))
            return False
    
    def test_token_validity_check(self):
        """Diagnostic 6: Test de validation des tokens"""
        try:
            print("🔑 Diagnostic 6: Test de validation des tokens")
            
            # Check if there are any existing connections with tokens to test
            response = self.session.get(f"{BASE_URL}/debug/social-connections", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Look for any connections with tokens
                connections_detail = data.get("connections_detail", [])
                
                if not connections_detail:
                    self.log_test("Token Validity Check", True, 
                                "✅ Aucune connexion existante - tokens propres pour nouveau test")
                    return True
                
                # Analyze existing tokens
                invalid_tokens = 0
                temp_tokens = 0
                valid_tokens = 0
                
                for conn in connections_detail:
                    access_token = conn.get("access_token", "")
                    if not access_token or access_token == "None":
                        invalid_tokens += 1
                    elif access_token.startswith("temp_"):
                        temp_tokens += 1
                    else:
                        valid_tokens += 1
                
                total_connections = len(connections_detail)
                
                if temp_tokens > 0:
                    self.log_test("Token Validity Check", False, 
                                f"❌ {temp_tokens}/{total_connections} connexions avec tokens temporaires - fallback mechanism actif")
                    return False
                elif invalid_tokens > 0:
                    self.log_test("Token Validity Check", False, 
                                f"❌ {invalid_tokens}/{total_connections} connexions avec tokens invalides/null")
                    return False
                else:
                    self.log_test("Token Validity Check", True, 
                                f"✅ {valid_tokens}/{total_connections} connexions avec tokens valides")
                    return True
                    
            else:
                self.log_test("Token Validity Check", False, 
                            f"Status: {response.status_code}", response.text[:200])
                return False
                
        except Exception as e:
            self.log_test("Token Validity Check", False, error=str(e))
            return False
    
    def run_comprehensive_diagnostic(self):
        """Run comprehensive Facebook OAuth callback diagnostic"""
        print("🎯 DIAGNOSTIC OAUTH FACEBOOK COMPLET EN TEMPS RÉEL")
        print("=" * 80)
        print(f"Backend URL: {BASE_URL}")
        print(f"Test User: {TEST_CREDENTIALS['email']}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 80)
        print()
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed - cannot continue diagnostic")
            return False
        
        # Diagnostic 1: Examiner les credentials Facebook actuels
        self.examine_facebook_credentials()
        
        # Diagnostic 2: Analyser la dernière tentative de connexion dans les logs
        self.analyze_connection_logs()
        
        # Diagnostic 3: Tester l'échange OAuth manuellement
        self.test_oauth_exchange_manually()
        
        # Diagnostic 4: Vérifier configuration App Facebook
        self.verify_facebook_app_configuration()
        
        # Diagnostic 5: Examiner le callback en détail
        self.examine_callback_in_detail()
        
        # Diagnostic 6: Test de validation des tokens
        self.test_token_validity_check()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 RÉSULTATS DIAGNOSTIC OAUTH FACEBOOK")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print(f"\n🎯 RÉSULTATS: {passed}/{total} diagnostics réussis ({(passed/total*100):.1f}%)")
        
        # Analyze results and provide recommendations
        failed_tests = [r['test'] for r in self.test_results if not r['success']]
        
        if passed == total:
            print("\n🎉 DIAGNOSTIC COMPLET - SYSTÈME OAUTH FONCTIONNEL!")
            print("✅ Credentials Facebook corrects")
            print("✅ Configuration App Facebook valide")
            print("✅ Callback state validation fonctionnelle")
            print("✅ Pas de tokens temporaires/invalides détectés")
            print("✅ Système prêt pour reconnexion utilisateur")
            return True
        else:
            print(f"\n🚨 PROBLÈMES DÉTECTÉS - {total - passed} DIAGNOSTICS ÉCHOUÉS")
            print("\n🔍 CAUSE RACINE PROBABLE:")
            
            if "Facebook Credentials Examination" in failed_tests:
                print("❌ CREDENTIALS FACEBOOK INCORRECTS - Vérifier FACEBOOK_APP_ID, FACEBOOK_APP_SECRET, FACEBOOK_CONFIG_ID")
            
            if "OAuth Exchange Manual Test" in failed_tests:
                print("❌ CALLBACK OAUTH DÉFAILLANT - Fallback mechanism crée de faux tokens")
            
            if "Token Validity Check" in failed_tests:
                print("❌ TOKENS TEMPORAIRES DÉTECTÉS - Échange OAuth échoue, fallback actif")
            
            if "Callback Detail Examination" in failed_tests:
                print("❌ VALIDATION STATE DÉFAILLANTE - Format state incorrect ou validation échoue")
            
            print(f"\n🛠️ ACTIONS REQUISES:")
            print("1. Vérifier credentials Facebook dans .env")
            print("2. Corriger callback OAuth pour éviter fallback")
            print("3. Nettoyer tokens temporaires existants")
            print("4. Tester reconnexion avec vrais credentials Facebook")
            
            return False

def main():
    """Main diagnostic execution"""
    diagnostic = FacebookOAuthDiagnostic()
    success = diagnostic.run_comprehensive_diagnostic()
    
    if success:
        print("\n✅ Diagnostic OAuth Facebook terminé avec succès!")
        print("🚀 Système prêt pour reconnexion utilisateur!")
        sys.exit(0)
    else:
        print("\n❌ Diagnostic OAuth Facebook révèle des problèmes critiques!")
        print("🔧 Corrections requises avant reconnexion utilisateur!")
        sys.exit(1)

if __name__ == "__main__":
    main()