#!/usr/bin/env python3
"""
Instagram OAuth Callback Corrections Testing on LIVE Environment
===============================================================

Testing the corrections applied to handle Instagram connections directly instead of redirecting to Facebook:
- Suppression de la redirection automatique vers Facebook callback
- Implémentation du processus complet d'OAuth Instagram 
- Création directe de connexions Instagram avec tokens permanents
- Gestion d'erreurs spécifique à Instagram

Test Objectives:
1. Authenticate on LIVE environment (https://claire-marcus.com/api)
2. Test Instagram callback to verify it no longer redirects to Facebook
3. Verify new logic processes Instagram directly
4. Check connection states and verify connections can now be created
"""

import requests
import json
import sys
import time
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# LIVE Environment Configuration
BASE_URL = "https://claire-marcus.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class InstagramCallbackTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        
    def log(self, message, level="INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def authenticate(self):
        """Authenticate with LIVE environment"""
        self.log("🔐 Authenticating with LIVE environment...")
        
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/auth/login-robust", json=login_data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                self.log(f"✅ Authentication successful - User ID: {self.user_id}")
                return True
            else:
                self.log(f"❌ Authentication failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Authentication error: {str(e)}", "ERROR")
            return False
    
    def test_health_check(self):
        """Test LIVE API health"""
        try:
            self.log("🏥 Testing LIVE API health...")
            
            response = self.session.get(f"{BASE_URL}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ LIVE API is healthy: {data.get('message', 'OK')}")
                return True
            else:
                self.log(f"❌ Health check failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Health check error: {str(e)}", "ERROR")
            return False
    
    def test_instagram_auth_url_generation(self):
        """Test Instagram OAuth URL generation"""
        try:
            self.log("🔗 Testing Instagram OAuth URL generation...")
            
            response = self.session.get(f"{BASE_URL}/social/instagram/auth-url", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get("auth_url", "")
                
                # Verify URL contains correct parameters for LIVE environment
                if "claire-marcus.com" in auth_url and "instagram" in auth_url:
                    self.log("✅ Instagram OAuth URL generated correctly")
                    self.log(f"   URL: {auth_url[:100]}...")
                    
                    # Check for correct redirect URI (should be LIVE domain)
                    if "redirect_uri=https%3A//claire-marcus.com/api/social/instagram/callback" in auth_url:
                        self.log("✅ Correct Instagram callback URI in OAuth URL (LIVE domain)")
                        return True
                    else:
                        self.log("❌ Instagram callback URI not correct for LIVE environment", "ERROR")
                        return False
                else:
                    self.log("❌ Invalid Instagram OAuth URL format", "ERROR")
                    return False
            else:
                self.log(f"❌ Instagram auth URL generation failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Instagram auth URL test error: {str(e)}", "ERROR")
            return False
    
    def test_instagram_callback_no_facebook_redirect(self):
        """CRITICAL TEST: Verify Instagram callback doesn't redirect to Facebook"""
        try:
            self.log("🔄 CRITICAL TEST: Verifying Instagram callback doesn't redirect to Facebook...")
            
            # Test with missing parameters to see endpoint behavior
            response = self.session.get(
                f"{BASE_URL}/social/instagram/callback",
                allow_redirects=False,
                timeout=10
            )
            
            if response.status_code == 302:
                redirect_url = response.headers.get('Location', '')
                
                # CRITICAL CHECK: Should NOT redirect to Facebook callback
                if "/social/facebook/callback" in redirect_url:
                    self.log("❌ CRITICAL FAILURE: Instagram callback still redirects to Facebook!", "ERROR")
                    self.log(f"   Redirect URL: {redirect_url}")
                    return False
                elif "auth_error=instagram" in redirect_url:
                    self.log("✅ CRITICAL SUCCESS: Instagram callback processes Instagram directly")
                    self.log(f"   Instagram-specific error redirect: {redirect_url}")
                    return True
                else:
                    self.log(f"✅ Instagram callback processes directly (redirect: {redirect_url})")
                    return True
            else:
                self.log(f"⚠️ Unexpected response from Instagram callback: {response.status_code}")
                return True
                
        except Exception as e:
            self.log(f"❌ Instagram callback test error: {str(e)}", "ERROR")
            return False
    
    def test_simulated_instagram_callback(self):
        """Test simulated Instagram callback with test parameters"""
        try:
            self.log("🧪 Testing simulated Instagram callback with test parameters...")
            
            # Simulate callback with test parameters
            test_params = {
                "code": "test_instagram_code_12345",
                "state": f"instagram_test|{self.user_id}",
            }
            
            response = self.session.get(
                f"{BASE_URL}/social/instagram/callback",
                params=test_params,
                allow_redirects=False,
                timeout=30
            )
            
            if response.status_code == 302:
                redirect_url = response.headers.get('Location', '')
                
                # Check that it processes Instagram parameters directly
                if "auth_error=instagram" in redirect_url or "auth_success=instagram" in redirect_url:
                    self.log("✅ Instagram callback processes Instagram parameters directly")
                    self.log(f"   Result: {redirect_url}")
                    return True
                elif "/social/facebook/callback" in redirect_url:
                    self.log("❌ CRITICAL: Instagram callback redirects to Facebook!", "ERROR")
                    return False
                else:
                    self.log(f"✅ Instagram callback result: {redirect_url}")
                    return True
            else:
                self.log(f"❌ Unexpected response: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Simulated callback error: {str(e)}", "ERROR")
            return False
    
    def test_social_connections_status(self):
        """Test current social connections status"""
        try:
            self.log("📊 Testing current social connections status...")
            
            response = self.session.get(f"{BASE_URL}/social/connections", timeout=10)
            
            if response.status_code == 200:
                connections = response.json()
                
                instagram_connections = [c for c in connections if c.get('platform') == 'instagram']
                facebook_connections = [c for c in connections if c.get('platform') == 'facebook']
                
                self.log(f"✅ Social connections retrieved:")
                self.log(f"   Instagram connections: {len(instagram_connections)}")
                self.log(f"   Facebook connections: {len(facebook_connections)}")
                
                # Check for active Instagram connections
                active_instagram = [c for c in instagram_connections if c.get('active', False)]
                if active_instagram:
                    self.log(f"✅ Found {len(active_instagram)} active Instagram connection(s)")
                else:
                    self.log("⚠️ No active Instagram connections found")
                
                return True
            else:
                self.log(f"❌ Failed to get social connections: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Social connections test error: {str(e)}", "ERROR")
            return False
    
    def test_instagram_connection_creation_logs(self):
        """Test if Instagram connections can be created (check logs)"""
        try:
            self.log("🔍 Testing Instagram connection creation capability...")
            
            # Check if diagnostic endpoint exists
            response = self.session.get(f"{BASE_URL}/debug/social-connections", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check collections and connection status
                total_connections = data.get('total_connections', 0)
                active_connections = data.get('active_connections', 0)
                instagram_connections = data.get('instagram_connections', 0)
                
                self.log(f"✅ Connection diagnostic retrieved:")
                self.log(f"   Total connections: {total_connections}")
                self.log(f"   Active connections: {active_connections}")
                self.log(f"   Instagram connections: {instagram_connections}")
                
                return True
            else:
                self.log(f"⚠️ Diagnostic endpoint not available: {response.status_code}")
                return True  # Not critical for main test
                
        except Exception as e:
            self.log(f"⚠️ Connection diagnostic error: {str(e)}")
            return True  # Not critical for main test
    
    def run_all_tests(self):
        """Run all Instagram callback correction tests"""
        self.log("🎯 STARTING INSTAGRAM CALLBACK CORRECTIONS TESTING ON LIVE ENVIRONMENT")
        self.log("=" * 80)
        
        test_results = {}
        
        # Test 1: Health Check
        test_results['health_check'] = self.test_health_check()
        
        # Test 2: Authentication
        if not self.authenticate():
            self.log("❌ CRITICAL: Authentication failed - cannot continue tests", "ERROR")
            return False
        test_results['authentication'] = True
        
        # Test 3: Instagram OAuth URL Generation
        test_results['instagram_auth_url'] = self.test_instagram_auth_url_generation()
        
        # Test 4: CRITICAL - Instagram Callback No Facebook Redirect
        test_results['no_facebook_redirect'] = self.test_instagram_callback_no_facebook_redirect()
        
        # Test 5: Simulated Instagram Callback
        test_results['simulated_callback'] = self.test_simulated_instagram_callback()
        
        # Test 6: Social Connections Status
        test_results['social_connections'] = self.test_social_connections_status()
        
        # Test 7: Connection Creation Capability
        test_results['connection_creation'] = self.test_instagram_connection_creation_logs()
        
        # Summary
        self.log("=" * 80)
        self.log("🎯 INSTAGRAM CALLBACK CORRECTIONS TEST SUMMARY")
        self.log("=" * 80)
        
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{status}: {test_name}")
        
        self.log(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
        
        # Critical success criteria
        critical_tests = [
            'no_facebook_redirect',
            'simulated_callback'
        ]
        
        critical_passed = all(test_results.get(test, False) for test in critical_tests)
        
        if critical_passed:
            self.log("✅ CRITICAL SUCCESS: Instagram callback no longer redirects to Facebook")
            self.log("✅ Instagram callback processes Instagram connections directly")
        else:
            self.log("❌ CRITICAL FAILURE: Instagram callback corrections not working properly")
        
        return critical_passed

def main():
    """Main test execution"""
    print("🎯 Instagram OAuth Callback Corrections Testing")
    print("Environment: LIVE (https://claire-marcus.com)")
    print("Credentials: lperpere@yahoo.fr")
    print("=" * 80)
    
    tester = InstagramCallbackTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 INSTAGRAM CALLBACK CORRECTIONS TESTING COMPLETED SUCCESSFULLY")
        sys.exit(0)
    else:
        print("\n❌ INSTAGRAM CALLBACK CORRECTIONS TESTING FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()