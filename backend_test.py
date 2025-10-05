#!/usr/bin/env python3
"""
Instagram OAuth LIVE Environment Diagnostic - claire-marcus.com
Diagnostiquer le problème Instagram sur l'environnement LIVE claire-marcus.com 
où les URLs sont correctement configurées dans Facebook Developer Console.

CONTEXTE CRITIQUE:
L'utilisateur confirme que le problème est sur l'environnement LIVE (claire-marcus.com) et NON sur preview. 
Les URLs sont correctement configurées dans Facebook Developer Console pour la production. 
Facebook fonctionne mais Instagram ne persiste pas.

INVESTIGATION LIVE REQUISE:
1. **Tester sur claire-marcus.com** : https://claire-marcus.com/api
2. **Comparer Facebook vs Instagram** : Pourquoi Facebook fonctionne et pas Instagram ?
3. **Analyser la logique callback** : Vérifier si mes corrections sont appliquées sur LIVE
4. **Vérifier les tokens** : Instagram vs Facebook sur l'environnement de production
5. **Diagnostic de persistance** : Pourquoi Instagram ne "tient" pas sur LIVE ?

AUTHENTIFICATION: lperpere@yahoo.fr / L@Reunion974!
URL LIVE: https://claire-marcus.com/api
"""

import requests
import json
import time
import sys
from datetime import datetime
import urllib.parse

# Configuration LIVE
LIVE_BACKEND_URL = "https://claire-marcus.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class InstagramCallbackTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Instagram-OAuth-Investigation/1.0'
        })
        self.auth_token = None
        self.user_id = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def authenticate(self):
        """Step 1: Authenticate with test credentials"""
        self.log("🔐 STEP 1: Authentication with test credentials")
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login-robust", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                self.user_id = data.get('user_id')
                
                # Set authorization header for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                
                self.log(f"✅ Authentication successful")
                self.log(f"   User ID: {self.user_id}")
                self.log(f"   Token: {self.auth_token[:20]}..." if self.auth_token else "   Token: None")
                return True
            else:
                self.log(f"❌ Authentication failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Authentication error: {str(e)}", "ERROR")
            return False
    
    def analyze_database_state(self):
        """Step 2: Analyze current database state for Instagram connections"""
        self.log("🔍 STEP 2: Database state analysis for Instagram connections")
        
        try:
            # Test debug endpoint for comprehensive connection analysis
            response = self.session.get(f"{BACKEND_URL}/debug/social-connections")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Debug endpoint accessible")
                
                # Analyze connection data
                total_connections = data.get('total_connections', 0)
                active_connections = data.get('active_connections', 0)
                facebook_connections = data.get('facebook_connections', 0)
                instagram_connections = data.get('instagram_connections', 0)
                
                self.log(f"📊 Database Analysis:")
                self.log(f"   Total connections: {total_connections}")
                self.log(f"   Active connections: {active_connections}")
                self.log(f"   Facebook connections: {facebook_connections}")
                self.log(f"   Instagram connections: {instagram_connections}")
                
                # Check for Instagram-specific data
                connections_detail = data.get('connections_detail', [])
                instagram_details = [conn for conn in connections_detail if conn.get('platform') == 'instagram']
                
                if instagram_details:
                    self.log(f"📋 Instagram Connection Details:")
                    for i, conn in enumerate(instagram_details, 1):
                        self.log(f"   Connection {i}:")
                        self.log(f"     Platform: {conn.get('platform')}")
                        self.log(f"     Active: {conn.get('active', conn.get('is_active'))}")
                        self.log(f"     Token: {conn.get('access_token', 'None')}")
                        self.log(f"     Connected at: {conn.get('connected_at', 'Unknown')}")
                        self.log(f"     Collection: {conn.get('collection', 'Unknown')}")
                else:
                    self.log("   No Instagram connections found in database")
                
                return True
            else:
                self.log(f"❌ Debug endpoint failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Database analysis error: {str(e)}", "ERROR")
            return False
    
    def test_frontend_api_endpoints(self):
        """Step 3: Test frontend API endpoints for Instagram connections"""
        self.log("🌐 STEP 3: Frontend API testing for Instagram connections")
        
        try:
            # Test GET /api/social/connections (what frontend sees)
            response = self.session.get(f"{BACKEND_URL}/social/connections")
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle different response formats
                if isinstance(data, list):
                    connections = data
                else:
                    connections = data.get('connections', [])
                
                self.log("✅ Frontend connections endpoint accessible")
                self.log(f"📊 Frontend sees {len(connections)} connections")
                
                # Handle case where connections might be strings or objects
                instagram_frontend = []
                for conn in connections:
                    if isinstance(conn, dict) and conn.get('platform') == 'instagram':
                        instagram_frontend.append(conn)
                    elif isinstance(conn, str) and 'instagram' in conn.lower():
                        instagram_frontend.append({'platform': 'instagram', 'connected': True})
                
                if instagram_frontend:
                    self.log(f"📋 Instagram connections visible to frontend:")
                    for i, conn in enumerate(instagram_frontend, 1):
                        self.log(f"   Connection {i}:")
                        self.log(f"     Platform: {conn.get('platform')}")
                        self.log(f"     Connected: {conn.get('connected', False)}")
                        self.log(f"     Page name: {conn.get('page_name', 'Unknown')}")
                else:
                    self.log("   No Instagram connections visible to frontend")
                    
                # Test Instagram auth URL generation
                auth_response = self.session.get(f"{BACKEND_URL}/social/instagram/auth-url")
                
                if auth_response.status_code == 200:
                    auth_data = auth_response.json()
                    auth_url = auth_data.get('auth_url', '')
                    
                    self.log("✅ Instagram auth URL generation working")
                    self.log(f"   Auth URL: {auth_url[:100]}..." if auth_url else "   No URL generated")
                    
                    # Analyze auth URL parameters
                    if 'client_id=' in auth_url and 'config_id=' in auth_url:
                        self.log("   ✅ Auth URL contains required parameters")
                    else:
                        self.log("   ❌ Auth URL missing required parameters")
                else:
                    self.log(f"❌ Instagram auth URL generation failed: {auth_response.status_code}")
                
                return True
            else:
                self.log(f"❌ Frontend connections endpoint failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Frontend API testing error: {str(e)}", "ERROR")
            return False
    
    def test_oauth_callback_simulation(self):
        """Step 4: Test Instagram OAuth callback with simulation"""
        self.log("🔄 STEP 4: Instagram OAuth callback simulation testing")
        
        try:
            # Test Instagram callback with test parameters
            callback_url = f"{BACKEND_URL}/social/instagram/callback"
            test_params = {
                'code': 'test_instagram_code_investigation',
                'state': f'instagram_test|{self.user_id}'
            }
            
            self.log(f"🧪 Testing Instagram callback with test parameters")
            self.log(f"   Callback URL: {callback_url}")
            self.log(f"   Test code: {test_params['code']}")
            self.log(f"   State: {test_params['state']}")
            
            # Make callback request
            response = self.session.get(callback_url, params=test_params, allow_redirects=False)
            
            self.log(f"📡 Callback response: Status {response.status_code}")
            
            if response.status_code in [302, 307]:
                redirect_location = response.headers.get('Location', '')
                self.log(f"   Redirect to: {redirect_location}")
                
                # Analyze redirect for success/error indicators
                if 'instagram_success=true' in redirect_location:
                    self.log("   ✅ Callback indicates success")
                elif 'instagram_error' in redirect_location or 'error' in redirect_location:
                    self.log("   ❌ Callback indicates error")
                else:
                    self.log("   ⚠️ Callback redirect unclear")
                    
            elif response.status_code == 200:
                self.log("   📄 Callback returned HTML response")
                
            # Check if connection was created after callback
            time.sleep(2)  # Wait for potential async processing
            
            # Re-check database state
            debug_response = self.session.get(f"{BACKEND_URL}/debug/social-connections")
            if debug_response.status_code == 200:
                debug_data = debug_response.json()
                new_instagram_count = debug_data.get('instagram_connections', 0)
                self.log(f"   📊 Instagram connections after callback: {new_instagram_count}")
            
            return True
            
        except Exception as e:
            self.log(f"❌ OAuth callback simulation error: {str(e)}", "ERROR")
            return False
    
    def analyze_token_format_and_validity(self):
        """Step 5: Analyze Instagram token format and validity"""
        self.log("🔑 STEP 5: Instagram token format and validity analysis")
        
        try:
            # Get detailed connection information
            response = self.session.get(f"{BACKEND_URL}/debug/social-connections")
            
            if response.status_code == 200:
                data = response.json()
                connections_detail = data.get('connections_detail', [])
                instagram_connections = [conn for conn in connections_detail if conn.get('platform') == 'instagram']
                
                if instagram_connections:
                    self.log(f"🔍 Analyzing {len(instagram_connections)} Instagram connections:")
                    
                    for i, conn in enumerate(instagram_connections, 1):
                        token = conn.get('access_token', '')
                        self.log(f"   Connection {i} Token Analysis:")
                        
                        if not token or token == 'None':
                            self.log(f"     ❌ No token found")
                        elif token.startswith('temp_'):
                            self.log(f"     ❌ Temporary token detected: {token[:30]}...")
                        elif token.startswith('EAA'):
                            self.log(f"     ✅ Long-lived token detected: {token[:30]}...")
                            self.log(f"     📅 Token appears to be Facebook/Instagram long-lived format")
                        else:
                            self.log(f"     ⚠️ Unknown token format: {token[:30]}...")
                        
                        # Check token expiration if available
                        expires_at = conn.get('expires_at')
                        if expires_at:
                            self.log(f"     ⏰ Expires at: {expires_at}")
                        else:
                            self.log(f"     ⏰ No expiration info")
                            
                        # Check if token is marked as active
                        is_active = conn.get('active', conn.get('is_active', False))
                        self.log(f"     🔄 Active status: {is_active}")
                        
                else:
                    self.log("   No Instagram connections found for token analysis")
                
                return True
            else:
                self.log(f"❌ Token analysis failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Token analysis error: {str(e)}", "ERROR")
            return False
    
    def test_button_logic_consistency(self):
        """Step 6: Test button logic consistency between backend and frontend"""
        self.log("🔘 STEP 6: Button logic consistency testing")
        
        try:
            # Test both endpoints that determine button state
            
            # 1. Debug endpoint (comprehensive)
            debug_response = self.session.get(f"{BACKEND_URL}/debug/social-connections")
            debug_data = debug_response.json() if debug_response.status_code == 200 else {}
            
            # 2. Frontend endpoint (what buttons see)
            frontend_response = self.session.get(f"{BACKEND_URL}/social/connections")
            frontend_data = frontend_response.json() if frontend_response.status_code == 200 else {}
            
            self.log("🔍 Button Logic Analysis:")
            
            # Debug endpoint Instagram count
            debug_instagram = debug_data.get('instagram_connections', 0)
            self.log(f"   Debug endpoint Instagram count: {debug_instagram}")
            
            # Frontend endpoint Instagram connections
            if isinstance(frontend_data, list):
                frontend_connections = frontend_data
            else:
                frontend_connections = frontend_data.get('connections', [])
            
            frontend_instagram = []
            for conn in frontend_connections:
                if isinstance(conn, dict) and conn.get('platform') == 'instagram':
                    frontend_instagram.append(conn)
                elif isinstance(conn, str) and 'instagram' in conn.lower():
                    frontend_instagram.append({'platform': 'instagram', 'connected': True})
            
            frontend_instagram_count = len(frontend_instagram)
            
            self.log(f"   Frontend endpoint Instagram count: {frontend_instagram_count}")
            
            # Check for consistency
            if debug_instagram == frontend_instagram_count:
                self.log("   ✅ Consistent Instagram connection count between endpoints")
            else:
                self.log("   ❌ INCONSISTENT Instagram connection count between endpoints")
                self.log("   🚨 This explains why buttons show wrong state!")
            
            # Analyze what frontend sees for button state
            if frontend_instagram:
                for conn in frontend_instagram:
                    connected_status = conn.get('connected', False)
                    self.log(f"   Frontend connection status: {connected_status}")
                    
                    if connected_status:
                        self.log("   🔘 Button should show: 'Connecté' (Connected)")
                    else:
                        self.log("   🔘 Button should show: 'Connecter' (Connect)")
            else:
                self.log("   🔘 Button should show: 'Connecter' (Connect) - No connections")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Button logic testing error: {str(e)}", "ERROR")
            return False
    
    def test_instagram_publication_flow(self):
        """Step 7: Test Instagram publication flow to verify token validity"""
        self.log("📤 STEP 7: Instagram publication flow testing")
        
        try:
            # Test publication endpoint to verify if tokens work
            test_post_data = {
                "post_id": "test_post_for_instagram_investigation",
                "platform": "instagram"
            }
            
            # Try publication to see if tokens are valid
            pub_response = self.session.post(f"{BACKEND_URL}/posts/publish", json=test_post_data)
            
            self.log(f"📡 Publication test response: Status {pub_response.status_code}")
            
            if pub_response.status_code == 400:
                error_data = pub_response.json()
                error_message = error_data.get('error', error_data.get('detail', 'Unknown error'))
                
                if 'Aucune connexion sociale active' in error_message:
                    self.log("   ❌ No active social connections found")
                    self.log("   🔍 This confirms Instagram connections are not active/valid")
                elif 'Post non trouvé' in error_message:
                    self.log("   ✅ Publication endpoint working (test post not found is expected)")
                else:
                    self.log(f"   ⚠️ Other error: {error_message}")
                    
            elif pub_response.status_code == 200:
                self.log("   ✅ Publication would succeed (unexpected with test data)")
            else:
                self.log(f"   ⚠️ Unexpected response: {pub_response.text}")
            
            # Also test Instagram-specific publication endpoint if available
            try:
                instagram_pub_response = self.session.post(f"{BACKEND_URL}/social/instagram/publish-simple", json={
                    "text": "Test Instagram publication for investigation",
                    "image_url": "https://via.placeholder.com/400x400.jpg"
                })
                
                self.log(f"📡 Instagram-specific publication test: Status {instagram_pub_response.status_code}")
                
                if instagram_pub_response.status_code == 400:
                    error_data = instagram_pub_response.json()
                    error_message = error_data.get('error', error_data.get('detail', 'Unknown error'))
                    self.log(f"   Error: {error_message}")
                    
            except Exception:
                self.log("   Instagram-specific endpoint not available")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Publication flow testing error: {str(e)}", "ERROR")
            return False
    
    def run_comprehensive_investigation(self):
        """Run the complete Instagram OAuth persistence investigation"""
        self.log("🚀 STARTING COMPREHENSIVE INSTAGRAM OAUTH PERSISTENCE INVESTIGATION")
        self.log("=" * 80)
        
        results = {
            'authentication': False,
            'database_analysis': False,
            'frontend_api': False,
            'oauth_callback': False,
            'token_analysis': False,
            'button_logic': False,
            'publication_flow': False
        }
        
        # Step 1: Authentication
        if self.authenticate():
            results['authentication'] = True
            
            # Step 2: Database Analysis
            if self.analyze_database_state():
                results['database_analysis'] = True
            
            # Step 3: Frontend API Testing
            if self.test_frontend_api_endpoints():
                results['frontend_api'] = True
            
            # Step 4: OAuth Callback Simulation
            if self.test_oauth_callback_simulation():
                results['oauth_callback'] = True
            
            # Step 5: Token Analysis
            if self.analyze_token_format_and_validity():
                results['token_analysis'] = True
            
            # Step 6: Button Logic Testing
            if self.test_button_logic_consistency():
                results['button_logic'] = True
            
            # Step 7: Publication Flow Testing
            if self.test_instagram_publication_flow():
                results['publication_flow'] = True
        
        # Summary
        self.log("=" * 80)
        self.log("🎯 INVESTIGATION SUMMARY")
        
        passed_tests = sum(results.values())
        total_tests = len(results)
        success_rate = (passed_tests / total_tests) * 100
        
        self.log(f"📊 Test Results: {passed_tests}/{total_tests} passed ({success_rate:.1f}% success rate)")
        
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            self.log(f"   {test_name.replace('_', ' ').title()}: {status}")
        
        # Critical findings summary
        self.log("\n🔍 CRITICAL FINDINGS:")
        
        if not results['authentication']:
            self.log("❌ AUTHENTICATION FAILED - Cannot proceed with investigation")
        elif passed_tests == total_tests:
            self.log("✅ All tests passed - Need to analyze specific findings for root cause")
        else:
            self.log("⚠️ Some tests failed - Root cause likely identified in failed tests")
        
        self.log("\n📋 NEXT STEPS:")
        self.log("1. Review detailed logs above for specific issues")
        self.log("2. Focus on failed test areas for root cause")
        self.log("3. Check database collection consistency")
        self.log("4. Verify OAuth callback implementation")
        self.log("5. Validate token format and expiration")
        
        return results

def main():
    """Main execution function"""
    print("🎯 INSTAGRAM OAUTH CALLBACK TESTING - EXACT FACEBOOK LOGIC + INSTAGRAM CONFIG")
    print("=" * 80)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"👤 Test User: {TEST_EMAIL}")
    print("=" * 80)
    
    tester = InstagramCallbackTester()
    success = tester.run_comprehensive_investigation()
    
    # Exit with appropriate code
    if success:
        sys.exit(0)  # Tests passed
    else:
        sys.exit(1)  # Tests failed

if __name__ == "__main__":
    main()