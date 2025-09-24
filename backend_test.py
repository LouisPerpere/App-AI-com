#!/usr/bin/env python3
"""
🔧 TEST CONNEXIONS SOCIALES FACEBOOK & INSTAGRAM CONFIGURATIONS DÉDIÉES
Backend Testing Script for Social Connections with Dedicated Config IDs

CONTEXTE: L'utilisateur a fourni des config_id dédiés pour résoudre les conflits 
d'authentification entre Facebook et Instagram. Test de la séparation complète des configurations.

CHANGEMENTS TESTÉS:
1. FACEBOOK_CONFIG_ID_PAGES = "1878388119742903" (dédié Facebook)
2. INSTAGRAM_CONFIG_ID_PAGES = "1309694717566880" (dédié Instagram)
3. Endpoints de test: /test/config-debug et /test/auth-urls-debug
4. Endpoints d'auth: /api/social/facebook/auth-url et /api/social/instagram/auth-url

BASE_URL: https://instamanager-1.preview.emergentagent.com/api
CREDENTIALS: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import sys
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# Configuration
BASE_URL = "https://instamanager-1.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

# Expected config IDs
EXPECTED_FACEBOOK_CONFIG_ID = "1878388119742903"
EXPECTED_INSTAGRAM_CONFIG_ID = "1309694717566880"

class SocialConnectionsTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test result"""
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
        print(f"{status} {test_name}")
        if details:
            print(f"   📋 {details}")
        if error:
            print(f"   ❌ Error: {error}")
        print()
        
    def authenticate(self):
        """Step 1: Authenticate with backend"""
        try:
            print("🔐 Step 1: Authentication")
            response = self.session.post(f"{BASE_URL}/auth/login-robust", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                
                self.log_test(
                    "Authentication", 
                    True, 
                    f"User ID: {self.user_id}, Token obtained and configured"
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
    
    def test_config_debug(self):
        """Step 2: Test /api/test/config-debug endpoint"""
        try:
            print("🔧 Step 2: Testing Config Debug Endpoint")
            response = self.session.get(f"{BASE_URL}/test/config-debug")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify config IDs
                facebook_config_id = data.get("facebook_config_id")
                instagram_config_id = data.get("instagram_config_id")
                facebook_app_id = data.get("facebook_app_id")
                
                success = True
                details = []
                
                # Check Facebook config ID
                if facebook_config_id == EXPECTED_FACEBOOK_CONFIG_ID:
                    details.append(f"✅ Facebook config_id: {facebook_config_id} (correct)")
                else:
                    details.append(f"❌ Facebook config_id: {facebook_config_id} (expected: {EXPECTED_FACEBOOK_CONFIG_ID})")
                    success = False
                
                # Check Instagram config ID
                if instagram_config_id == EXPECTED_INSTAGRAM_CONFIG_ID:
                    details.append(f"✅ Instagram config_id: {instagram_config_id} (correct)")
                else:
                    details.append(f"❌ Instagram config_id: {instagram_config_id} (expected: {EXPECTED_INSTAGRAM_CONFIG_ID})")
                    success = False
                
                # Check Facebook App ID
                if facebook_app_id and facebook_app_id != "NOT_SET":
                    details.append(f"✅ Facebook App ID: {facebook_app_id}")
                else:
                    details.append(f"❌ Facebook App ID: {facebook_app_id}")
                    success = False
                
                # Check redirect URIs
                facebook_redirect = data.get("facebook_redirect_uri", "")
                instagram_redirect = data.get("instagram_redirect_uri", "")
                
                if facebook_redirect and "facebook/callback" in facebook_redirect:
                    details.append(f"✅ Facebook redirect URI: {facebook_redirect}")
                else:
                    details.append(f"❌ Facebook redirect URI: {facebook_redirect}")
                    success = False
                
                if instagram_redirect and "instagram/callback" in instagram_redirect:
                    details.append(f"✅ Instagram redirect URI: {instagram_redirect}")
                else:
                    details.append(f"❌ Instagram redirect URI: {instagram_redirect}")
                    success = False
                
                self.log_test(
                    "Config Debug Endpoint", 
                    success, 
                    "; ".join(details)
                )
                return success
            else:
                self.log_test(
                    "Config Debug Endpoint", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Config Debug Endpoint", False, error=str(e))
            return False
    
    def test_auth_urls_debug(self):
        """Step 3: Test /api/test/auth-urls-debug endpoint"""
        try:
            print("🔗 Step 3: Testing Auth URLs Debug Endpoint")
            response = self.session.get(f"{BASE_URL}/test/auth-urls-debug")
            
            if response.status_code == 200:
                data = response.json()
                
                facebook_data = data.get("facebook", {})
                instagram_data = data.get("instagram", {})
                
                success = True
                details = []
                
                # Verify Facebook auth URL
                facebook_config_id = facebook_data.get("config_id")
                facebook_auth_url = facebook_data.get("auth_url", "")
                
                if facebook_config_id == EXPECTED_FACEBOOK_CONFIG_ID:
                    details.append(f"✅ Facebook config_id in response: {facebook_config_id}")
                else:
                    details.append(f"❌ Facebook config_id: {facebook_config_id} (expected: {EXPECTED_FACEBOOK_CONFIG_ID})")
                    success = False
                
                if "config_id=" + EXPECTED_FACEBOOK_CONFIG_ID in facebook_auth_url:
                    details.append("✅ Facebook auth URL contains correct config_id")
                else:
                    details.append("❌ Facebook auth URL missing correct config_id")
                    success = False
                
                # Verify Instagram auth URL
                instagram_config_id = instagram_data.get("config_id")
                instagram_auth_url = instagram_data.get("auth_url", "")
                
                if instagram_config_id == EXPECTED_INSTAGRAM_CONFIG_ID:
                    details.append(f"✅ Instagram config_id in response: {instagram_config_id}")
                else:
                    details.append(f"❌ Instagram config_id: {instagram_config_id} (expected: {EXPECTED_INSTAGRAM_CONFIG_ID})")
                    success = False
                
                if "config_id=" + EXPECTED_INSTAGRAM_CONFIG_ID in instagram_auth_url:
                    details.append("✅ Instagram auth URL contains correct config_id")
                else:
                    details.append("❌ Instagram auth URL missing correct config_id")
                    success = False
                
                # Verify URL structure
                if "facebook.com/v20.0/dialog/oauth" in facebook_auth_url:
                    details.append("✅ Facebook auth URL uses correct OAuth endpoint")
                else:
                    details.append("❌ Facebook auth URL incorrect endpoint")
                    success = False
                
                if "facebook.com/v20.0/dialog/oauth" in instagram_auth_url:
                    details.append("✅ Instagram auth URL uses correct OAuth endpoint")
                else:
                    details.append("❌ Instagram auth URL incorrect endpoint")
                    success = False
                
                self.log_test(
                    "Auth URLs Debug Endpoint", 
                    success, 
                    "; ".join(details)
                )
                return success
            else:
                self.log_test(
                    "Auth URLs Debug Endpoint", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Auth URLs Debug Endpoint", False, error=str(e))
            return False
    
    def test_facebook_auth_url(self):
        """Step 4: Test /api/social/facebook/auth-url with authentication"""
        try:
            print("📘 Step 4: Testing Facebook Auth URL (Authenticated)")
            response = self.session.get(f"{BASE_URL}/social/facebook/auth-url")
            
            if response.status_code == 200:
                data = response.json()
                
                auth_url = data.get("auth_url", "")
                config_id = data.get("config_id")
                redirect_uri = data.get("redirect_uri", "")
                scopes = data.get("scopes", [])
                
                success = True
                details = []
                
                # Verify config_id
                if config_id == EXPECTED_FACEBOOK_CONFIG_ID:
                    details.append(f"✅ Facebook config_id: {config_id}")
                else:
                    details.append(f"❌ Facebook config_id: {config_id} (expected: {EXPECTED_FACEBOOK_CONFIG_ID})")
                    success = False
                
                # Verify auth URL contains config_id
                if "config_id=" + EXPECTED_FACEBOOK_CONFIG_ID in auth_url:
                    details.append("✅ Auth URL contains correct config_id")
                else:
                    details.append("❌ Auth URL missing correct config_id")
                    success = False
                
                # Verify redirect URI
                if "facebook/callback" in redirect_uri:
                    details.append(f"✅ Redirect URI: {redirect_uri}")
                else:
                    details.append(f"❌ Redirect URI: {redirect_uri}")
                    success = False
                
                # Verify scopes
                expected_scopes = ["pages_show_list", "pages_read_engagement", "pages_manage_posts"]
                if all(scope in scopes for scope in expected_scopes):
                    details.append(f"✅ Scopes: {', '.join(scopes)}")
                else:
                    details.append(f"❌ Scopes: {', '.join(scopes)} (missing expected scopes)")
                    success = False
                
                # Verify URL structure
                if "facebook.com/v20.0/dialog/oauth" in auth_url:
                    details.append("✅ Uses correct Facebook OAuth endpoint")
                else:
                    details.append("❌ Incorrect OAuth endpoint")
                    success = False
                
                self.log_test(
                    "Facebook Auth URL (Authenticated)", 
                    success, 
                    "; ".join(details)
                )
                return success
            else:
                self.log_test(
                    "Facebook Auth URL (Authenticated)", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Facebook Auth URL (Authenticated)", False, error=str(e))
            return False
    
    def test_instagram_auth_url(self):
        """Step 5: Test /api/social/instagram/auth-url with authentication"""
        try:
            print("📷 Step 5: Testing Instagram Auth URL (Authenticated)")
            response = self.session.get(f"{BASE_URL}/social/instagram/auth-url")
            
            if response.status_code == 200:
                data = response.json()
                
                auth_url = data.get("auth_url", "")
                config_id = data.get("config_id")
                redirect_uri = data.get("redirect_uri", "")
                scopes = data.get("scopes", [])
                flow_type = data.get("flow_type", "")
                
                success = True
                details = []
                
                # Verify config_id
                if config_id == EXPECTED_INSTAGRAM_CONFIG_ID:
                    details.append(f"✅ Instagram config_id: {config_id}")
                else:
                    details.append(f"❌ Instagram config_id: {config_id} (expected: {EXPECTED_INSTAGRAM_CONFIG_ID})")
                    success = False
                
                # Verify auth URL contains config_id
                if "config_id=" + EXPECTED_INSTAGRAM_CONFIG_ID in auth_url:
                    details.append("✅ Auth URL contains correct config_id")
                else:
                    details.append("❌ Auth URL missing correct config_id")
                    success = False
                
                # Verify redirect URI
                if "instagram/callback" in redirect_uri:
                    details.append(f"✅ Redirect URI: {redirect_uri}")
                else:
                    details.append(f"❌ Redirect URI: {redirect_uri}")
                    success = False
                
                # Verify scopes
                expected_scopes = ["pages_show_list", "pages_read_engagement", "pages_manage_posts"]
                if all(scope in scopes for scope in expected_scopes):
                    details.append(f"✅ Scopes: {', '.join(scopes)}")
                else:
                    details.append(f"❌ Scopes: {', '.join(scopes)} (missing expected scopes)")
                    success = False
                
                # Verify flow type
                if flow_type == "oauth_with_config_id":
                    details.append(f"✅ Flow type: {flow_type}")
                else:
                    details.append(f"❌ Flow type: {flow_type}")
                    success = False
                
                # Verify URL structure
                if "facebook.com/v20.0/dialog/oauth" in auth_url:
                    details.append("✅ Uses correct OAuth endpoint")
                else:
                    details.append("❌ Incorrect OAuth endpoint")
                    success = False
                
                self.log_test(
                    "Instagram Auth URL (Authenticated)", 
                    success, 
                    "; ".join(details)
                )
                return success
            else:
                self.log_test(
                    "Instagram Auth URL (Authenticated)", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Instagram Auth URL (Authenticated)", False, error=str(e))
            return False
    
    def test_url_parameters_validation(self):
        """Step 6: Verify generated URLs contain correct config_id and redirect_uri"""
        try:
            print("🔍 Step 6: URL Parameters Validation")
            
            # Get both auth URLs
            facebook_response = self.session.get(f"{BASE_URL}/social/facebook/auth-url")
            instagram_response = self.session.get(f"{BASE_URL}/social/instagram/auth-url")
            
            if facebook_response.status_code != 200 or instagram_response.status_code != 200:
                self.log_test(
                    "URL Parameters Validation", 
                    False, 
                    error="Failed to get auth URLs for validation"
                )
                return False
            
            facebook_data = facebook_response.json()
            instagram_data = instagram_response.json()
            
            facebook_url = facebook_data.get("auth_url", "")
            instagram_url = instagram_data.get("auth_url", "")
            
            success = True
            details = []
            
            # Parse Facebook URL parameters
            facebook_parsed = urlparse(facebook_url)
            facebook_params = parse_qs(facebook_parsed.query)
            
            # Parse Instagram URL parameters
            instagram_parsed = urlparse(instagram_url)
            instagram_params = parse_qs(instagram_parsed.query)
            
            # Validate Facebook URL parameters
            facebook_config_id = facebook_params.get("config_id", [""])[0]
            facebook_redirect = facebook_params.get("redirect_uri", [""])[0]
            facebook_client_id = facebook_params.get("client_id", [""])[0]
            facebook_response_type = facebook_params.get("response_type", [""])[0]
            
            if facebook_config_id == EXPECTED_FACEBOOK_CONFIG_ID:
                details.append(f"✅ Facebook URL config_id parameter: {facebook_config_id}")
            else:
                details.append(f"❌ Facebook URL config_id parameter: {facebook_config_id}")
                success = False
            
            if "facebook/callback" in facebook_redirect:
                details.append("✅ Facebook URL redirect_uri parameter correct")
            else:
                details.append(f"❌ Facebook URL redirect_uri parameter: {facebook_redirect}")
                success = False
            
            if facebook_client_id:
                details.append(f"✅ Facebook URL client_id parameter: {facebook_client_id}")
            else:
                details.append("❌ Facebook URL missing client_id parameter")
                success = False
            
            if facebook_response_type == "code":
                details.append("✅ Facebook URL response_type: code")
            else:
                details.append(f"❌ Facebook URL response_type: {facebook_response_type}")
                success = False
            
            # Validate Instagram URL parameters
            instagram_config_id = instagram_params.get("config_id", [""])[0]
            instagram_redirect = instagram_params.get("redirect_uri", [""])[0]
            instagram_client_id = instagram_params.get("client_id", [""])[0]
            instagram_response_type = instagram_params.get("response_type", [""])[0]
            
            if instagram_config_id == EXPECTED_INSTAGRAM_CONFIG_ID:
                details.append(f"✅ Instagram URL config_id parameter: {instagram_config_id}")
            else:
                details.append(f"❌ Instagram URL config_id parameter: {instagram_config_id}")
                success = False
            
            if "instagram/callback" in instagram_redirect:
                details.append("✅ Instagram URL redirect_uri parameter correct")
            else:
                details.append(f"❌ Instagram URL redirect_uri parameter: {instagram_redirect}")
                success = False
            
            if instagram_client_id:
                details.append(f"✅ Instagram URL client_id parameter: {instagram_client_id}")
            else:
                details.append("❌ Instagram URL missing client_id parameter")
                success = False
            
            if instagram_response_type == "code":
                details.append("✅ Instagram URL response_type: code")
            else:
                details.append(f"❌ Instagram URL response_type: {instagram_response_type}")
                success = False
            
            # Verify URLs are different (different config_ids and redirect_uris)
            if facebook_url != instagram_url:
                details.append("✅ Facebook and Instagram URLs are different (as expected)")
            else:
                details.append("❌ Facebook and Instagram URLs are identical (should be different)")
                success = False
            
            self.log_test(
                "URL Parameters Validation", 
                success, 
                "; ".join(details)
            )
            return success
            
        except Exception as e:
            self.log_test("URL Parameters Validation", False, error=str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 STARTING FACEBOOK & INSTAGRAM SOCIAL CONNECTIONS TESTING")
        print("=" * 80)
        print(f"Backend URL: {BASE_URL}")
        print(f"Test User: {TEST_EMAIL}")
        print(f"Expected Facebook Config ID: {EXPECTED_FACEBOOK_CONFIG_ID}")
        print(f"Expected Instagram Config ID: {EXPECTED_INSTAGRAM_CONFIG_ID}")
        print("=" * 80)
        print()
        
        # Run tests in sequence
        tests = [
            self.authenticate,
            self.test_config_debug,
            self.test_auth_urls_debug,
            self.test_facebook_auth_url,
            self.test_instagram_auth_url,
            self.test_url_parameters_validation
        ]
        
        for test in tests:
            if not test():
                print("❌ Test failed, continuing with remaining tests...")
                print()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Print individual results
        for result in self.test_results:
            print(f"{result['status']} {result['test']}")
            if result['details']:
                print(f"   📋 {result['details']}")
            if result['error']:
                print(f"   ❌ {result['error']}")
        
        print()
        print("=" * 80)
        
        if success_rate == 100:
            print("🎉 ALL TESTS PASSED - FACEBOOK & INSTAGRAM CONFIGURATIONS WORKING CORRECTLY!")
            print("✅ Les config_id dédiés sont correctement implémentés")
            print("✅ Les URLs d'authentification sont générées avec les bons paramètres")
            print("✅ Les redirections sont configurées correctement")
            print("✅ Les scopes sont appropriés pour chaque plateforme")
        elif success_rate >= 80:
            print("⚠️ MOST TESTS PASSED - MINOR ISSUES DETECTED")
            print("🔧 Some configuration issues may need attention")
        else:
            print("❌ MULTIPLE TEST FAILURES - CONFIGURATION ISSUES DETECTED")
            print("🚨 Significant problems with Facebook/Instagram configuration")
        
        print("=" * 80)

def main():
    """Main function"""
    tester = SocialConnectionsTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()