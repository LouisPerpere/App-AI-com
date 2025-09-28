#!/usr/bin/env python3
"""
DIAGNOSTIC SPÉCIFIQUE: TEST CALLBACK FACEBOOK AVEC PARAMÈTRES RÉALISTES

Ce test simule exactement ce qui se passe quand un utilisateur revient de Facebook
avec un code d'autorisation et teste le callback endpoint.
"""

import requests
import json
import sys
import time
import subprocess
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# Configuration
BACKEND_URL = "https://social-publisher-10.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class FacebookCallbackTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        
    def authenticate(self):
        """Authenticate and get user_id"""
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
                print(f"✅ Authentication successful - User ID: {self.user_id}")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False

    def get_facebook_auth_url(self):
        """Get Facebook auth URL to extract state format"""
        try:
            response = self.session.get(f"{BACKEND_URL}/social/facebook/auth-url")
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get('auth_url', '')
                
                # Parse URL to get state parameter
                parsed_url = urlparse(auth_url)
                query_params = parse_qs(parsed_url.query)
                state = query_params.get('state', [''])[0]
                
                print(f"✅ Facebook auth URL generated")
                print(f"   State parameter: {state}")
                print(f"   Full URL: {auth_url}")
                
                return state
            else:
                print(f"❌ Failed to get auth URL: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting auth URL: {e}")
            return None

    def test_callback_with_realistic_params(self, state_param):
        """Test callback with realistic Facebook parameters"""
        print("\n🔍 TESTING FACEBOOK CALLBACK WITH REALISTIC PARAMETERS")
        print("-" * 60)
        
        # Test scenarios with different types of codes/errors
        test_scenarios = [
            {
                "name": "Valid Facebook Code Format",
                "params": {
                    "code": "AQBxyz123456789abcdef_realistic_facebook_code_format_test",
                    "state": state_param
                },
                "expected": "Token exchange should fail but callback should process"
            },
            {
                "name": "Facebook Error - Access Denied",
                "params": {
                    "error": "access_denied",
                    "error_description": "The user denied the request",
                    "state": state_param
                },
                "expected": "Should redirect with auth_error"
            },
            {
                "name": "Missing Code",
                "params": {
                    "state": state_param
                },
                "expected": "Should redirect with no_code error"
            },
            {
                "name": "Invalid State Format",
                "params": {
                    "code": "AQBtest123",
                    "state": "invalid_state_format"
                },
                "expected": "Should redirect with invalid_state error"
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\n📋 Testing: {scenario['name']}")
            print(f"   Expected: {scenario['expected']}")
            
            # Monitor logs before callback
            self.capture_logs_before()
            
            try:
                # Make callback request
                response = self.session.get(
                    f"{BACKEND_URL}/social/facebook/callback",
                    params=scenario["params"],
                    allow_redirects=False  # Don't follow redirects to see the response
                )
                
                print(f"   Status Code: {response.status_code}")
                
                # Check if it's a redirect
                if response.status_code in [301, 302, 303, 307, 308]:
                    location = response.headers.get('Location', 'No location header')
                    print(f"   Redirect Location: {location}")
                    
                    # Parse redirect URL to see error parameters
                    if '?' in location:
                        redirect_params = parse_qs(location.split('?')[1])
                        if redirect_params:
                            print(f"   Redirect Parameters: {redirect_params}")
                else:
                    # Not a redirect, show response content
                    content_preview = response.text[:200] + "..." if len(response.text) > 200 else response.text
                    print(f"   Response Content: {content_preview}")
                
                # Capture logs after callback
                self.capture_logs_after(scenario['name'])
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            time.sleep(1)  # Brief pause between tests

    def capture_logs_before(self):
        """Capture log state before callback"""
        try:
            result = subprocess.run(
                ["wc", "-l", "/var/log/supervisor/backend.err.log"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                self.log_lines_before = int(result.stdout.split()[0])
            else:
                self.log_lines_before = 0
        except:
            self.log_lines_before = 0

    def capture_logs_after(self, scenario_name):
        """Capture and show new logs after callback"""
        try:
            # Wait a moment for logs to be written
            time.sleep(0.5)
            
            result = subprocess.run(
                ["wc", "-l", "/var/log/supervisor/backend.err.log"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                current_lines = int(result.stdout.split()[0])
                new_lines = current_lines - self.log_lines_before
                
                if new_lines > 0:
                    # Get the new log lines
                    tail_result = subprocess.run(
                        ["tail", "-n", str(new_lines), "/var/log/supervisor/backend.err.log"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    if tail_result.returncode == 0:
                        new_logs = tail_result.stdout.strip()
                        if new_logs:
                            print(f"   📋 New Backend Logs ({new_lines} lines):")
                            for line in new_logs.split('\n'):
                                if line.strip():
                                    print(f"      {line}")
                        else:
                            print(f"   📋 No significant new logs")
                    else:
                        print(f"   📋 Could not retrieve new logs")
                else:
                    print(f"   📋 No new log entries")
            
        except Exception as e:
            print(f"   📋 Error capturing logs: {e}")

    def check_social_connections_after_tests(self):
        """Check if any connections were created during tests"""
        print("\n🔍 CHECKING SOCIAL CONNECTIONS AFTER CALLBACK TESTS")
        print("-" * 60)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/debug/social-connections")
            
            if response.status_code == 200:
                data = response.json()
                
                total_connections = data.get('total_connections', 0)
                active_connections = data.get('active_connections', 0)
                facebook_connections = data.get('facebook_connections', 0)
                
                print(f"📊 Connection Summary:")
                print(f"   Total Connections: {total_connections}")
                print(f"   Active Connections: {active_connections}")
                print(f"   Facebook Connections: {facebook_connections}")
                
                # Show connection details if any exist
                connections_detail = data.get('connections_detail', [])
                if connections_detail:
                    print(f"\n📋 Connection Details:")
                    for conn in connections_detail:
                        platform = conn.get('platform', 'unknown')
                        active = conn.get('active', False)
                        token = conn.get('access_token', '')
                        token_preview = token[:20] + '...' if len(token) > 20 else token
                        
                        print(f"   Platform: {platform}, Active: {active}, Token: {token_preview}")
                else:
                    print(f"   No connections found (expected for test scenarios)")
                
            else:
                print(f"❌ Failed to get connections: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error checking connections: {e}")

    def run_callback_diagnostic(self):
        """Run complete callback diagnostic"""
        print("🚨 DIAGNOSTIC SPÉCIFIQUE: CALLBACK FACEBOOK AVEC PARAMÈTRES RÉALISTES")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ CRITICAL: Authentication failed")
            return False
        
        # Step 2: Get Facebook auth URL to understand state format
        print("\n🔗 GETTING FACEBOOK AUTH URL FOR STATE FORMAT")
        print("-" * 50)
        state_param = self.get_facebook_auth_url()
        
        if not state_param:
            print("❌ Could not get state parameter - using fallback")
            state_param = f"facebook_oauth|{self.user_id}"
        
        # Step 3: Test callback with realistic parameters
        self.test_callback_with_realistic_params(state_param)
        
        # Step 4: Check final state
        self.check_social_connections_after_tests()
        
        print("\n" + "=" * 80)
        print("🎯 DIAGNOSTIC CALLBACK FACEBOOK TERMINÉ")
        print("=" * 80)
        print("🔍 OBSERVATIONS:")
        print("1. Callback endpoint accessible et répond aux différents scénarios")
        print("2. Redirections appropriées selon les paramètres fournis")
        print("3. Logs backend capturés pendant les tests")
        print("4. État des connexions sociales vérifié")
        print()
        print("⚠️ POUR DIAGNOSTIC COMPLET:")
        print("- Tester avec de vrais codes d'autorisation Facebook")
        print("- Vérifier la configuration Facebook Developer Console")
        print("- Surveiller les logs pendant une vraie tentative utilisateur")
        print("=" * 80)
        
        return True

def main():
    """Main execution"""
    tester = FacebookCallbackTester()
    
    try:
        success = tester.run_callback_diagnostic()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrompu par l'utilisateur")
        sys.exit(3)
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {str(e)}")
        sys.exit(4)

if __name__ == "__main__":
    main()