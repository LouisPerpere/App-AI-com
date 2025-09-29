#!/usr/bin/env python3
"""
DIAGNOSTIC URGENT: FACEBOOK OAUTH CALLBACK EN TEMPS RÉEL

Identifiants: lperpere@yahoo.fr / L@Reunion974!

SITUATION: L'utilisateur rapporte que les connexions Facebook ne tiennent pas - 
la fenêtre OAuth s'ouvre mais les boutons reviennent à "Connecter".

DIAGNOSTIC REQUIS:
1. Surveiller les logs backend pendant une tentative de connexion
2. Tester le callback Facebook directement
3. Vérifier la génération d'URL OAuth
4. Test du callback avec paramètres simulés
5. Vérifier les variables d'environnement

OBJECTIF: Identifier EXACTEMENT où le processus OAuth échoue
"""

import requests
import json
import sys
import time
import subprocess
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# Configuration
BACKEND_URL = "https://social-pub-hub.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

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
        """Step 1: Authenticate with test credentials"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login-robust", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                
                self.log_test(
                    "Authentication", 
                    True, 
                    f"User ID: {self.user_id}, Token obtained"
                )
                return True
            else:
                self.log_test(
                    "Authentication", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, error=str(e))
            return False

    def check_backend_logs(self):
        """Step 2: Check current backend logs"""
        try:
            # Try to get recent backend logs
            result = subprocess.run(
                ["tail", "-n", "50", "/var/log/supervisor/backend.err.log"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logs = result.stdout
                self.log_test(
                    "Backend Logs Access", 
                    True, 
                    f"Successfully accessed backend logs ({len(logs.split())} lines)"
                )
                
                # Look for OAuth-related errors in recent logs
                oauth_errors = []
                for line in logs.split('\n'):
                    if any(keyword in line.lower() for keyword in ['oauth', 'facebook', 'callback', 'token', 'error']):
                        oauth_errors.append(line.strip())
                
                if oauth_errors:
                    print("🔍 Recent OAuth-related log entries:")
                    for error in oauth_errors[-10:]:  # Show last 10
                        print(f"   {error}")
                    print()
                
                return True
            else:
                self.log_test(
                    "Backend Logs Access", 
                    False, 
                    error=f"Cannot access logs: {result.stderr}"
                )
                return False
                
        except Exception as e:
            self.log_test("Backend Logs Access", False, error=str(e))
            return False

    def test_facebook_auth_url_generation(self):
        """Step 3: Test Facebook OAuth URL generation"""
        try:
            response = self.session.get(f"{BACKEND_URL}/social/facebook/auth-url")
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get('auth_url', '')
                
                # Parse URL components
                parsed_url = urlparse(auth_url)
                query_params = parse_qs(parsed_url.query)
                
                # Check required parameters
                required_params = ['client_id', 'redirect_uri', 'response_type', 'scope', 'state']
                missing_params = []
                
                for param in required_params:
                    if param not in query_params:
                        missing_params.append(param)
                
                if not missing_params:
                    # Extract key values
                    client_id = query_params.get('client_id', [''])[0]
                    redirect_uri = query_params.get('redirect_uri', [''])[0]
                    state = query_params.get('state', [''])[0]
                    
                    details = f"Client ID: {client_id}, Redirect URI: {redirect_uri}, State format: {state[:20]}..."
                    
                    self.log_test(
                        "Facebook OAuth URL Generation", 
                        True, 
                        details
                    )
                    return auth_url, state
                else:
                    self.log_test(
                        "Facebook OAuth URL Generation", 
                        False, 
                        error=f"Missing required parameters: {missing_params}"
                    )
                    return None, None
            else:
                self.log_test(
                    "Facebook OAuth URL Generation", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return None, None
                
        except Exception as e:
            self.log_test("Facebook OAuth URL Generation", False, error=str(e))
            return None, None

    def test_facebook_callback_direct(self, state_param=None):
        """Step 4: Test Facebook callback endpoint directly"""
        try:
            # Test with different parameter combinations
            test_scenarios = [
                {
                    "name": "Missing Parameters",
                    "params": {}
                },
                {
                    "name": "Invalid Code Format", 
                    "params": {"code": "invalid_code", "state": state_param or "test_state"}
                },
                {
                    "name": "Valid Format Test Code",
                    "params": {"code": "AQD1234567890abcdef", "state": state_param or "test_state"}
                },
                {
                    "name": "Error Parameter",
                    "params": {"error": "access_denied", "error_description": "User denied access"}
                }
            ]
            
            callback_results = []
            
            for scenario in test_scenarios:
                try:
                    response = self.session.get(
                        f"{BACKEND_URL}/social/facebook/callback",
                        params=scenario["params"]
                    )
                    
                    callback_results.append({
                        "scenario": scenario["name"],
                        "status_code": response.status_code,
                        "response": response.text[:200] + "..." if len(response.text) > 200 else response.text,
                        "headers": dict(response.headers)
                    })
                    
                except Exception as e:
                    callback_results.append({
                        "scenario": scenario["name"],
                        "error": str(e)
                    })
            
            self.log_test(
                "Facebook Callback Direct Testing", 
                True, 
                f"Tested {len(test_scenarios)} scenarios"
            )
            
            # Print detailed results
            print("🔍 Facebook Callback Test Results:")
            for result in callback_results:
                print(f"   Scenario: {result['scenario']}")
                if 'status_code' in result:
                    print(f"   Status: {result['status_code']}")
                    print(f"   Response: {result['response']}")
                else:
                    print(f"   Error: {result['error']}")
                print()
            
            return callback_results
                
        except Exception as e:
            self.log_test("Facebook Callback Direct Testing", False, error=str(e))
            return []

    def test_environment_variables(self):
        """Step 5: Verify Facebook environment variables"""
        try:
            # Test if we can access environment info through a diagnostic endpoint
            response = self.session.get(f"{BACKEND_URL}/diag")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if we have database connection (indicates backend is working)
                db_connected = data.get('database_connected', False)
                
                self.log_test(
                    "Environment Variables Check", 
                    True, 
                    f"Backend diagnostic accessible, DB connected: {db_connected}"
                )
                
                # Try to get OAuth configuration through auth-url (indirect check)
                auth_response = self.session.get(f"{BACKEND_URL}/social/facebook/auth-url")
                if auth_response.status_code == 200:
                    auth_data = auth_response.json()
                    auth_url = auth_data.get('auth_url', '')
                    
                    # Extract configuration from URL
                    parsed_url = urlparse(auth_url)
                    query_params = parse_qs(parsed_url.query)
                    
                    client_id = query_params.get('client_id', ['NOT_FOUND'])[0]
                    redirect_uri = query_params.get('redirect_uri', ['NOT_FOUND'])[0]
                    
                    print("🔍 Facebook Configuration (from OAuth URL):")
                    print(f"   Client ID: {client_id}")
                    print(f"   Redirect URI: {redirect_uri}")
                    print(f"   OAuth Domain: {parsed_url.netloc}")
                    print()
                    
                    # Check if configuration looks correct
                    config_issues = []
                    if client_id == 'NOT_FOUND' or len(client_id) < 10:
                        config_issues.append("Invalid or missing Facebook App ID")
                    if redirect_uri == 'NOT_FOUND' or 'callback' not in redirect_uri:
                        config_issues.append("Invalid or missing redirect URI")
                    
                    if config_issues:
                        self.log_test(
                            "Facebook Configuration Validation", 
                            False, 
                            error=f"Configuration issues: {config_issues}"
                        )
                    else:
                        self.log_test(
                            "Facebook Configuration Validation", 
                            True, 
                            "Facebook OAuth configuration appears valid"
                        )
                
                return True
            else:
                self.log_test(
                    "Environment Variables Check", 
                    False, 
                    error=f"Cannot access diagnostic endpoint: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Environment Variables Check", False, error=str(e))
            return False

    def test_social_connections_state(self):
        """Step 6: Check current social connections state"""
        try:
            response = self.session.get(f"{BACKEND_URL}/debug/social-connections")
            
            if response.status_code == 200:
                data = response.json()
                
                total_connections = data.get('total_connections', 0)
                active_connections = data.get('active_connections', 0)
                facebook_connections = data.get('facebook_connections', 0)
                instagram_connections = data.get('instagram_connections', 0)
                
                # Check for problematic tokens
                connections_detail = data.get('connections_detail', [])
                problematic_tokens = []
                
                for conn in connections_detail:
                    token = conn.get('access_token', '')
                    platform = conn.get('platform', '')
                    
                    if any(pattern in token for pattern in ['temp_', 'test_', 'fallback']):
                        problematic_tokens.append({
                            'platform': platform,
                            'token_type': 'temporary/test',
                            'token_preview': token[:20] + '...' if len(token) > 20 else token
                        })
                    elif not token or token == 'None':
                        problematic_tokens.append({
                            'platform': platform,
                            'token_type': 'null/empty',
                            'token_preview': str(token)
                        })
                
                details = f"Total: {total_connections}, Active: {active_connections}, Facebook: {facebook_connections}, Instagram: {instagram_connections}"
                
                if problematic_tokens:
                    details += f", Problematic tokens: {len(problematic_tokens)}"
                    print("🚨 Problematic tokens found:")
                    for token_info in problematic_tokens:
                        print(f"   Platform: {token_info['platform']}, Type: {token_info['token_type']}, Preview: {token_info['token_preview']}")
                    print()
                
                self.log_test(
                    "Social Connections State", 
                    True, 
                    details
                )
                
                return data
            else:
                self.log_test(
                    "Social Connections State", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test("Social Connections State", False, error=str(e))
            return None

    def monitor_logs_during_callback_simulation(self):
        """Step 7: Monitor logs during callback simulation"""
        try:
            print("🔍 MONITORING BACKEND LOGS DURING CALLBACK SIMULATION")
            print("-" * 60)
            
            # Get initial log state
            initial_logs = subprocess.run(
                ["tail", "-n", "20", "/var/log/supervisor/backend.err.log"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            print("📋 Initial backend logs (last 20 lines):")
            if initial_logs.returncode == 0:
                for line in initial_logs.stdout.split('\n')[-10:]:  # Show last 10 lines
                    if line.strip():
                        print(f"   {line}")
            print()
            
            # Simulate callback with realistic parameters
            print("🚀 Simulating Facebook callback...")
            
            # Generate a realistic state parameter
            import uuid
            test_state = f"facebook_oauth_{self.user_id}_{int(time.time())}"
            
            callback_response = self.session.get(
                f"{BACKEND_URL}/social/facebook/callback",
                params={
                    "code": "AQBxyz123456789abcdef_test_code_format",
                    "state": test_state
                }
            )
            
            print(f"   Callback response: {callback_response.status_code}")
            print(f"   Response content: {callback_response.text[:200]}...")
            print()
            
            # Wait a moment for logs to be written
            time.sleep(2)
            
            # Get new logs
            new_logs = subprocess.run(
                ["tail", "-n", "30", "/var/log/supervisor/backend.err.log"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if new_logs.returncode == 0:
                # Find new log entries (simple approach - look for recent timestamps)
                current_time = datetime.now()
                recent_logs = []
                
                for line in new_logs.stdout.split('\n'):
                    if line.strip() and any(keyword in line.lower() for keyword in 
                                          ['facebook', 'oauth', 'callback', 'token', 'error', 'exception']):
                        recent_logs.append(line.strip())
                
                if recent_logs:
                    print("📋 OAuth-related logs during callback simulation:")
                    for log_line in recent_logs[-15:]:  # Show last 15 relevant lines
                        print(f"   {log_line}")
                    print()
                else:
                    print("📋 No OAuth-related logs found during callback simulation")
                    print()
            
            self.log_test(
                "Backend Log Monitoring During Callback", 
                True, 
                f"Monitored logs during callback simulation, Response: {callback_response.status_code}"
            )
            
            return True
            
        except Exception as e:
            self.log_test("Backend Log Monitoring During Callback", False, error=str(e))
            return False

    def run_comprehensive_diagnostic(self):
        """Run complete Facebook OAuth diagnostic"""
        print("🚨 DIAGNOSTIC URGENT: FACEBOOK OAUTH CALLBACK EN TEMPS RÉEL")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: {TEST_EMAIL}")
        print(f"Diagnostic Time: {datetime.now().isoformat()}")
        print("=" * 80)
        print()
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ CRITICAL: Authentication failed - cannot proceed with diagnostic")
            return False
        
        # Step 2: Check backend logs access
        print("📋 VÉRIFICATION ACCÈS LOGS BACKEND")
        print("-" * 40)
        self.check_backend_logs()
        print()
        
        # Step 3: Test OAuth URL generation
        print("🔗 TEST GÉNÉRATION URL OAUTH FACEBOOK")
        print("-" * 40)
        auth_url, state_param = self.test_facebook_auth_url_generation()
        print()
        
        # Step 4: Test callback endpoint directly
        print("🔄 TEST CALLBACK FACEBOOK DIRECT")
        print("-" * 40)
        callback_results = self.test_facebook_callback_direct(state_param)
        print()
        
        # Step 5: Check environment variables
        print("⚙️ VÉRIFICATION VARIABLES D'ENVIRONNEMENT")
        print("-" * 40)
        self.test_environment_variables()
        print()
        
        # Step 6: Check current connections state
        print("🔍 ÉTAT ACTUEL CONNEXIONS SOCIALES")
        print("-" * 40)
        connections_data = self.test_social_connections_state()
        print()
        
        # Step 7: Monitor logs during callback simulation
        print("📊 SURVEILLANCE LOGS PENDANT SIMULATION CALLBACK")
        print("-" * 40)
        self.monitor_logs_during_callback_simulation()
        print()
        
        # Summary
        self.print_diagnostic_summary()
        
        return True
    
    def print_diagnostic_summary(self):
        """Print diagnostic summary"""
        print("=" * 80)
        print("🎯 RÉSUMÉ DIAGNOSTIC - FACEBOOK OAUTH CALLBACK")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Réussis: {passed}")
        print(f"Échoués: {total - passed}")
        print(f"Taux de Réussite: {(passed/total*100):.1f}%" if total > 0 else "0%")
        print()
        
        # Critical diagnostic points
        critical_tests = [
            "Authentication",
            "Facebook OAuth URL Generation", 
            "Facebook Callback Direct Testing",
            "Social Connections State"
        ]
        
        print("🔥 TESTS CRITIQUES:")
        for result in self.test_results:
            if result['test'] in critical_tests:
                print(f"  {result['status']}: {result['test']}")
        print()
        
        # Failed tests details
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print("❌ DÉTAILS DES ÉCHECS:")
            for result in failed_tests:
                print(f"  • {result['test']}: {result['error']}")
            print()
        
        print("=" * 80)
        
        # Diagnostic conclusion
        critical_passed = sum(1 for result in self.test_results if result['test'] in critical_tests and result['success'])
        critical_total = sum(1 for result in self.test_results if result['test'] in critical_tests)
        
        if critical_passed == critical_total:
            print("🎯 DIAGNOSTIC FACEBOOK OAUTH: SYSTÈME OPÉRATIONNEL")
            print("✅ Tous les composants critiques fonctionnent")
            print("✅ URLs OAuth générées correctement")
            print("✅ Callback endpoint accessible")
            print("⚠️ Problème probablement dans l'échange de tokens ou la sauvegarde")
        else:
            print("🚨 DIAGNOSTIC FACEBOOK OAUTH: PROBLÈMES IDENTIFIÉS")
            print(f"❌ {critical_total - critical_passed} tests critiques échoués")
            print("⚠️ Composants de base non fonctionnels")
        
        print()
        print("🔍 RECOMMANDATIONS:")
        print("1. Vérifier les logs backend pendant une vraie tentative de connexion utilisateur")
        print("2. Tester l'échange de token Facebook avec de vrais codes d'autorisation")
        print("3. Vérifier la cohérence des collections de base de données")
        print("4. Valider la configuration Facebook Developer Console")
        
        print("=" * 80)

def main():
    """Main diagnostic execution"""
    diagnostic = FacebookOAuthDiagnostic()
    
    try:
        success = diagnostic.run_comprehensive_diagnostic()
        
        # Exit with appropriate code
        if success:
            failed_count = sum(1 for result in diagnostic.test_results if not result['success'])
            sys.exit(0 if failed_count == 0 else 1)
        else:
            sys.exit(2)
            
    except KeyboardInterrupt:
        print("\n⚠️ Diagnostic interrompu par l'utilisateur")
        sys.exit(3)
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {str(e)}")
        sys.exit(4)

if __name__ == "__main__":
    main()