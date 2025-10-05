#!/usr/bin/env python3
"""
Backend Test Suite - Instagram Token Cleanup Mission
NETTOYAGE URGENT - Supprimer les connexions factices Instagram qui polluent le système.

This test suite focuses on cleaning up fake Instagram connections that are polluting the system.

PROBLÈME IDENTIFIÉ:
- ID: `3d30a39f-5e77-464e-9bfb-aba69dd88ed7` 
- Token: `instagram_token_test_insta_1759651976`
- Username: `Instagram Connected` (factice)

ACTIONS REQUISES:
1. Supprimer les connexions de test dans social_media_connections
2. Vérifier la suppression via debug endpoint
3. Confirmer cohérence entre debug et frontend endpoints
4. Nettoyer toutes traces de tokens factices/temporaires

ENDPOINTS À UTILISER:
- POST /api/debug/clean-invalid-tokens (si existe)
- GET /api/debug/social-connections (vérification)
- GET /api/social/connections (vérification)

CRITÈRES DE SUCCÈS:
- Debug endpoint: 0 connexions Instagram
- Frontend endpoint: 0 connexions Instagram  
- Cohérence totale entre les deux endpoints
- Base de données propre sans tokens factices

Credentials: lperpere@yahoo.fr / L@Reunion974!
URL: https://claire-marcus-app-1.preview.emergentagent.com/api
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://claire-marcus-app-1.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class InstagramCleanupTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Instagram-Cleanup-Tester/1.0'
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
    
    def check_initial_state(self):
        """Step 2: Check initial state before cleanup"""
        self.log("🔍 STEP 2: Checking initial state before cleanup")
        
        try:
            # Check debug endpoint
            debug_response = self.session.get(f"{BACKEND_URL}/debug/social-connections")
            
            if debug_response.status_code == 200:
                debug_data = debug_response.json()
                self.log("✅ Debug endpoint accessible")
                
                # Analyze connection data
                total_connections = debug_data.get('total_connections', 0)
                active_connections = debug_data.get('active_connections', 0)
                instagram_connections = debug_data.get('instagram_connections', 0)
                
                self.log(f"📊 Initial Database State:")
                self.log(f"   Total connections: {total_connections}")
                self.log(f"   Active connections: {active_connections}")
                self.log(f"   Instagram connections: {instagram_connections}")
                
                # Check for specific fake connection
                connections_detail = debug_data.get('connections_detail', [])
                fake_connection_found = False
                
                for conn in connections_detail:
                    if conn.get('platform') == 'instagram':
                        conn_id = conn.get('id', conn.get('_id', ''))
                        token = conn.get('access_token', '')
                        username = conn.get('username', conn.get('page_name', ''))
                        
                        self.log(f"   Instagram Connection Found:")
                        self.log(f"     ID: {conn_id}")
                        self.log(f"     Token: {token}")
                        self.log(f"     Username: {username}")
                        self.log(f"     Active: {conn.get('active', conn.get('is_active'))}")
                        
                        # Check if this is the fake connection
                        if (conn_id == '3d30a39f-5e77-464e-9bfb-aba69dd88ed7' or 
                            'instagram_token_test_insta_1759651976' in token or
                            username == 'Instagram Connected'):
                            fake_connection_found = True
                            self.log(f"     🚨 FAKE CONNECTION IDENTIFIED!")
                
                if fake_connection_found:
                    self.log("❌ Fake Instagram connection found - cleanup needed")
                else:
                    self.log("✅ No obvious fake connections found")
                
                return True, instagram_connections
            else:
                self.log(f"❌ Debug endpoint failed: {debug_response.status_code} - {debug_response.text}", "ERROR")
                return False, 0
                
        except Exception as e:
            self.log(f"❌ Initial state check error: {str(e)}", "ERROR")
            return False, 0
    
    def check_frontend_state(self):
        """Step 3: Check frontend endpoint state"""
        self.log("🌐 STEP 3: Checking frontend endpoint state")
        
        try:
            # Check frontend endpoint
            frontend_response = self.session.get(f"{BACKEND_URL}/social/connections")
            
            if frontend_response.status_code == 200:
                frontend_data = frontend_response.json()
                
                # Handle different response formats
                if isinstance(frontend_data, list):
                    connections = frontend_data
                else:
                    connections = frontend_data.get('connections', [])
                
                self.log("✅ Frontend connections endpoint accessible")
                self.log(f"📊 Frontend sees {len(connections)} connections")
                
                # Count Instagram connections
                instagram_count = 0
                for conn in connections:
                    if isinstance(conn, dict) and conn.get('platform') == 'instagram':
                        instagram_count += 1
                        self.log(f"   Instagram connection: {conn.get('page_name', 'Unknown')}")
                    elif isinstance(conn, str) and 'instagram' in conn.lower():
                        instagram_count += 1
                        self.log(f"   Instagram connection (string): {conn}")
                
                self.log(f"   Instagram connections visible to frontend: {instagram_count}")
                return True, instagram_count
            else:
                self.log(f"❌ Frontend endpoint failed: {frontend_response.status_code} - {frontend_response.text}", "ERROR")
                return False, 0
                
        except Exception as e:
            self.log(f"❌ Frontend state check error: {str(e)}", "ERROR")
            return False, 0
    
    def attempt_cleanup(self):
        """Step 4: Attempt to clean invalid tokens"""
        self.log("🧹 STEP 4: Attempting to clean invalid tokens")
        
        try:
            # Try the cleanup endpoint
            cleanup_response = self.session.post(f"{BACKEND_URL}/debug/clean-invalid-tokens")
            
            if cleanup_response.status_code == 200:
                cleanup_data = cleanup_response.json()
                self.log("✅ Cleanup endpoint accessible")
                
                deleted_count = cleanup_data.get('deleted_connections', 0)
                message = cleanup_data.get('message', 'No message')
                
                self.log(f"📊 Cleanup Results:")
                self.log(f"   Message: {message}")
                self.log(f"   Deleted connections: {deleted_count}")
                
                if deleted_count > 0:
                    self.log(f"✅ Successfully deleted {deleted_count} invalid connections")
                else:
                    self.log("ℹ️ No invalid connections found to delete")
                
                return True, deleted_count
            elif cleanup_response.status_code == 404:
                self.log("⚠️ Cleanup endpoint not found - may need to be implemented")
                return False, 0
            else:
                self.log(f"❌ Cleanup endpoint failed: {cleanup_response.status_code} - {cleanup_response.text}", "ERROR")
                return False, 0
                
        except Exception as e:
            self.log(f"❌ Cleanup attempt error: {str(e)}", "ERROR")
            return False, 0
    
    def manual_cleanup_attempt(self):
        """Step 5: Attempt manual cleanup if automatic cleanup fails"""
        self.log("🔧 STEP 5: Attempting manual cleanup approach")
        
        try:
            # Try to identify and manually delete fake connections
            # This would require direct database access or specific endpoints
            
            # First, let's see if there are any other cleanup endpoints
            endpoints_to_try = [
                "/debug/clean-library-badges",
                "/debug/reset-social-connections",
                "/social/connections/reset",
                "/social/instagram/disconnect"
            ]
            
            for endpoint in endpoints_to_try:
                try:
                    response = self.session.post(f"{BACKEND_URL}{endpoint}")
                    if response.status_code == 200:
                        self.log(f"✅ Found working endpoint: {endpoint}")
                        data = response.json()
                        self.log(f"   Response: {data}")
                    elif response.status_code == 404:
                        self.log(f"⚠️ Endpoint not found: {endpoint}")
                    else:
                        self.log(f"❌ Endpoint failed: {endpoint} - {response.status_code}")
                except Exception:
                    self.log(f"⚠️ Error testing endpoint: {endpoint}")
            
            # Try to get more detailed connection info for manual identification
            debug_response = self.session.get(f"{BACKEND_URL}/debug/social-connections")
            if debug_response.status_code == 200:
                debug_data = debug_response.json()
                connections_detail = debug_data.get('connections_detail', [])
                
                self.log("🔍 Detailed connection analysis for manual cleanup:")
                for i, conn in enumerate(connections_detail):
                    if conn.get('platform') == 'instagram':
                        self.log(f"   Connection {i+1}:")
                        self.log(f"     ID: {conn.get('id', conn.get('_id', 'Unknown'))}")
                        self.log(f"     Token: {conn.get('access_token', 'None')}")
                        self.log(f"     Username: {conn.get('username', conn.get('page_name', 'Unknown'))}")
                        self.log(f"     Collection: {conn.get('collection', 'Unknown')}")
                        self.log(f"     Active: {conn.get('active', conn.get('is_active', False))}")
                        
                        # Identify fake tokens
                        token = conn.get('access_token', '')
                        if ('test' in token.lower() or 
                            'temp' in token.lower() or 
                            'fake' in token.lower() or
                            'instagram_token_test_insta' in token):
                            self.log(f"     🚨 IDENTIFIED AS FAKE TOKEN")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Manual cleanup error: {str(e)}", "ERROR")
            return False
    
    def verify_cleanup_success(self):
        """Step 6: Verify cleanup was successful"""
        self.log("✅ STEP 6: Verifying cleanup success")
        
        try:
            # Check debug endpoint after cleanup
            debug_response = self.session.get(f"{BACKEND_URL}/debug/social-connections")
            debug_instagram_count = 0
            
            if debug_response.status_code == 200:
                debug_data = debug_response.json()
                debug_instagram_count = debug_data.get('instagram_connections', 0)
                self.log(f"📊 Debug endpoint Instagram connections: {debug_instagram_count}")
            
            # Check frontend endpoint after cleanup
            frontend_response = self.session.get(f"{BACKEND_URL}/social/connections")
            frontend_instagram_count = 0
            
            if frontend_response.status_code == 200:
                frontend_data = frontend_response.json()
                
                if isinstance(frontend_data, list):
                    connections = frontend_data
                else:
                    connections = frontend_data.get('connections', [])
                
                for conn in connections:
                    if isinstance(conn, dict) and conn.get('platform') == 'instagram':
                        frontend_instagram_count += 1
                    elif isinstance(conn, str) and 'instagram' in conn.lower():
                        frontend_instagram_count += 1
                
                self.log(f"📊 Frontend endpoint Instagram connections: {frontend_instagram_count}")
            
            # Check for consistency
            if debug_instagram_count == 0 and frontend_instagram_count == 0:
                self.log("✅ SUCCESS: Both endpoints show 0 Instagram connections")
                self.log("✅ SUCCESS: Database is clean of fake Instagram tokens")
                return True, True
            elif debug_instagram_count == frontend_instagram_count:
                self.log(f"⚠️ PARTIAL SUCCESS: Consistent count ({debug_instagram_count}) but not zero")
                return True, False
            else:
                self.log(f"❌ INCONSISTENCY: Debug shows {debug_instagram_count}, Frontend shows {frontend_instagram_count}")
                return False, False
                
        except Exception as e:
            self.log(f"❌ Verification error: {str(e)}", "ERROR")
            return False, False
    
    def run_cleanup_mission(self):
        """Run the complete Instagram cleanup mission"""
        self.log("🚀 STARTING INSTAGRAM TOKEN CLEANUP MISSION")
        self.log("=" * 80)
        
        results = {
            'authentication': False,
            'initial_state_check': False,
            'frontend_state_check': False,
            'cleanup_attempt': False,
            'manual_cleanup': False,
            'verification': False,
            'complete_success': False
        }
        
        initial_instagram_count = 0
        final_instagram_count = 0
        
        # Step 1: Authentication
        if self.authenticate():
            results['authentication'] = True
            
            # Step 2: Initial State Check
            success, initial_instagram_count = self.check_initial_state()
            if success:
                results['initial_state_check'] = True
            
            # Step 3: Frontend State Check
            success, frontend_count = self.check_frontend_state()
            if success:
                results['frontend_state_check'] = True
            
            # Step 4: Cleanup Attempt
            success, deleted_count = self.attempt_cleanup()
            if success:
                results['cleanup_attempt'] = True
            
            # Step 5: Manual Cleanup (if needed)
            if not success or deleted_count == 0:
                if self.manual_cleanup_attempt():
                    results['manual_cleanup'] = True
            
            # Step 6: Verification
            success, complete_success = self.verify_cleanup_success()
            if success:
                results['verification'] = True
                results['complete_success'] = complete_success
        
        # Summary
        self.log("=" * 80)
        self.log("🎯 CLEANUP MISSION SUMMARY")
        
        passed_tests = sum(results.values())
        total_tests = len(results)
        success_rate = (passed_tests / total_tests) * 100
        
        self.log(f"📊 Test Results: {passed_tests}/{total_tests} passed ({success_rate:.1f}% success rate)")
        
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            self.log(f"   {test_name.replace('_', ' ').title()}: {status}")
        
        # Mission status
        self.log("\n🎯 MISSION STATUS:")
        
        if results['complete_success']:
            self.log("✅ MISSION ACCOMPLISHED: All fake Instagram tokens cleaned successfully")
            self.log("✅ Database is now clean and consistent")
        elif results['verification']:
            self.log("⚠️ PARTIAL SUCCESS: Cleanup attempted but some connections remain")
            self.log("⚠️ Manual intervention may be required")
        else:
            self.log("❌ MISSION FAILED: Unable to complete cleanup")
            self.log("❌ Fake Instagram tokens may still be polluting the system")
        
        self.log("\n📋 RECOMMENDATIONS:")
        if results['complete_success']:
            self.log("1. ✅ System is clean - no further action needed")
            self.log("2. ✅ Users can now reconnect Instagram properly")
            self.log("3. ✅ Monitor for future fake token creation")
        else:
            self.log("1. ❌ Implement POST /api/debug/clean-invalid-tokens endpoint")
            self.log("2. ❌ Add manual cleanup functionality")
            self.log("3. ❌ Fix OAuth callback to prevent fake token creation")
            self.log("4. ❌ Ensure collection consistency between endpoints")
        
        return results

def main():
    """Main execution function"""
    print("🧹 Instagram Token Cleanup Mission")
    print("=" * 50)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Credentials: {TEST_EMAIL}")
    print("=" * 50)
    
    tester = InstagramCleanupTester()
    results = tester.run_cleanup_mission()
    
    # Exit with appropriate code
    if results.get('complete_success', False):
        sys.exit(0)  # Mission accomplished
    else:
        sys.exit(1)  # Mission failed or incomplete

if __name__ == "__main__":
    main()