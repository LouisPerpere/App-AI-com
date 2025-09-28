#!/usr/bin/env python3
"""
OAuth Configuration Validation Test Suite
Testing Facebook and Instagram OAuth configuration with specific Config IDs

VALIDATION REQUIREMENTS:
1. Facebook auth-url endpoint with Config ID 1878388119742903
2. Instagram auth-url endpoint with Config ID 1309694717566880  
3. Both should use App ID 1115451684022643
4. Redirect URIs should point to claire-marcus.com

Credentials: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import sys
import urllib.parse
from datetime import datetime

# Configuration
BACKEND_URL = "https://social-publisher-10.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

# Expected Configuration Values
EXPECTED_APP_ID = "1115451684022643"
EXPECTED_FACEBOOK_CONFIG_ID = "1878388119742903"
EXPECTED_INSTAGRAM_CONFIG_ID = "1309694717566880"
EXPECTED_DOMAIN = "claire-marcus.com"

class OAuthConfigTester:
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
    
    def parse_auth_url(self, auth_url):
        """Parse OAuth URL and extract parameters"""
        try:
            parsed = urllib.parse.urlparse(auth_url)
            params = urllib.parse.parse_qs(parsed.query)
            
            # Convert single-item lists to strings
            for key, value in params.items():
                if isinstance(value, list) and len(value) == 1:
                    params[key] = value[0]
            
            return {
                'base_url': f"{parsed.scheme}://{parsed.netloc}{parsed.path}",
                'params': params
            }
        except Exception as e:
            return None
    
    def test_facebook_auth_url(self):
        """Test Facebook OAuth URL generation and configuration"""
        try:
            response = self.session.get(f"{BACKEND_URL}/social/facebook/auth-url")
            
            if response.status_code != 200:
                self.log_test(
                    "Facebook Auth URL - Endpoint Access", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return False
            
            data = response.json()
            auth_url = data.get('auth_url', '')
            
            if not auth_url:
                self.log_test(
                    "Facebook Auth URL - Response Format", 
                    False, 
                    error="No auth_url in response"
                )
                return False
            
            # Parse the URL
            parsed = self.parse_auth_url(auth_url)
            if not parsed:
                self.log_test(
                    "Facebook Auth URL - URL Parsing", 
                    False, 
                    error="Failed to parse auth URL"
                )
                return False
            
            params = parsed['params']
            
            # Validate App ID (client_id)
            client_id = params.get('client_id', '')
            if client_id == EXPECTED_APP_ID:
                self.log_test(
                    "Facebook Auth URL - App ID Validation", 
                    True, 
                    f"Correct App ID: {client_id}"
                )
            else:
                self.log_test(
                    "Facebook Auth URL - App ID Validation", 
                    False, 
                    error=f"Expected App ID: {EXPECTED_APP_ID}, Got: {client_id}"
                )
                return False
            
            # Validate Config ID
            config_id = params.get('config_id', '')
            if config_id == EXPECTED_FACEBOOK_CONFIG_ID:
                self.log_test(
                    "Facebook Auth URL - Config ID Validation", 
                    True, 
                    f"Correct Facebook Config ID: {config_id}"
                )
            else:
                self.log_test(
                    "Facebook Auth URL - Config ID Validation", 
                    False, 
                    error=f"Expected Facebook Config ID: {EXPECTED_FACEBOOK_CONFIG_ID}, Got: {config_id}"
                )
                return False
            
            # Validate Redirect URI
            redirect_uri = params.get('redirect_uri', '')
            if EXPECTED_DOMAIN in redirect_uri:
                self.log_test(
                    "Facebook Auth URL - Redirect URI Validation", 
                    True, 
                    f"Correct domain in redirect URI: {redirect_uri}"
                )
            else:
                self.log_test(
                    "Facebook Auth URL - Redirect URI Validation", 
                    False, 
                    error=f"Expected domain '{EXPECTED_DOMAIN}' not found in redirect URI: {redirect_uri}"
                )
                return False
            
            # Validate URL structure
            if 'facebook.com' in parsed['base_url']:
                self.log_test(
                    "Facebook Auth URL - URL Structure", 
                    True, 
                    f"Valid Facebook OAuth URL: {parsed['base_url']}"
                )
            else:
                self.log_test(
                    "Facebook Auth URL - URL Structure", 
                    False, 
                    error=f"Invalid OAuth URL base: {parsed['base_url']}"
                )
                return False
            
            # Log complete URL for verification
            self.log_test(
                "Facebook Auth URL - Complete Configuration", 
                True, 
                f"Full URL generated successfully with all required parameters"
            )
            
            return True
                
        except Exception as e:
            self.log_test("Facebook Auth URL Testing", False, error=str(e))
            return False
    
    def test_instagram_auth_url(self):
        """Test Instagram OAuth URL generation and configuration"""
        try:
            response = self.session.get(f"{BACKEND_URL}/social/instagram/auth-url")
            
            if response.status_code != 200:
                self.log_test(
                    "Instagram Auth URL - Endpoint Access", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return False
            
            data = response.json()
            auth_url = data.get('auth_url', '')
            
            if not auth_url:
                self.log_test(
                    "Instagram Auth URL - Response Format", 
                    False, 
                    error="No auth_url in response"
                )
                return False
            
            # Parse the URL
            parsed = self.parse_auth_url(auth_url)
            if not parsed:
                self.log_test(
                    "Instagram Auth URL - URL Parsing", 
                    False, 
                    error="Failed to parse auth URL"
                )
                return False
            
            params = parsed['params']
            
            # Validate App ID (client_id) - should be same as Facebook
            client_id = params.get('client_id', '')
            if client_id == EXPECTED_APP_ID:
                self.log_test(
                    "Instagram Auth URL - App ID Validation", 
                    True, 
                    f"Correct App ID: {client_id} (same as Facebook)"
                )
            else:
                self.log_test(
                    "Instagram Auth URL - App ID Validation", 
                    False, 
                    error=f"Expected App ID: {EXPECTED_APP_ID}, Got: {client_id}"
                )
                return False
            
            # Validate Config ID (should be different from Facebook)
            config_id = params.get('config_id', '')
            if config_id == EXPECTED_INSTAGRAM_CONFIG_ID:
                self.log_test(
                    "Instagram Auth URL - Config ID Validation", 
                    True, 
                    f"Correct Instagram Config ID: {config_id}"
                )
            else:
                self.log_test(
                    "Instagram Auth URL - Config ID Validation", 
                    False, 
                    error=f"Expected Instagram Config ID: {EXPECTED_INSTAGRAM_CONFIG_ID}, Got: {config_id}"
                )
                return False
            
            # Validate Redirect URI
            redirect_uri = params.get('redirect_uri', '')
            if EXPECTED_DOMAIN in redirect_uri:
                self.log_test(
                    "Instagram Auth URL - Redirect URI Validation", 
                    True, 
                    f"Correct domain in redirect URI: {redirect_uri}"
                )
            else:
                self.log_test(
                    "Instagram Auth URL - Redirect URI Validation", 
                    False, 
                    error=f"Expected domain '{EXPECTED_DOMAIN}' not found in redirect URI: {redirect_uri}"
                )
                return False
            
            # Validate URL structure
            if 'facebook.com' in parsed['base_url']:  # Instagram uses Facebook OAuth
                self.log_test(
                    "Instagram Auth URL - URL Structure", 
                    True, 
                    f"Valid Instagram OAuth URL (via Facebook): {parsed['base_url']}"
                )
            else:
                self.log_test(
                    "Instagram Auth URL - URL Structure", 
                    False, 
                    error=f"Invalid OAuth URL base: {parsed['base_url']}"
                )
                return False
            
            # Log complete URL for verification
            self.log_test(
                "Instagram Auth URL - Complete Configuration", 
                True, 
                f"Full URL generated successfully with all required parameters"
            )
            
            return True
                
        except Exception as e:
            self.log_test("Instagram Auth URL Testing", False, error=str(e))
            return False
    
    def test_configuration_consistency(self):
        """Test consistency between Facebook and Instagram configurations"""
        try:
            # Get both URLs
            fb_response = self.session.get(f"{BACKEND_URL}/social/facebook/auth-url")
            ig_response = self.session.get(f"{BACKEND_URL}/social/instagram/auth-url")
            
            if fb_response.status_code != 200 or ig_response.status_code != 200:
                self.log_test(
                    "Configuration Consistency - Endpoint Access", 
                    False, 
                    error="Cannot access both endpoints for comparison"
                )
                return False
            
            fb_data = fb_response.json()
            ig_data = ig_response.json()
            
            fb_url = fb_data.get('auth_url', '')
            ig_url = ig_data.get('auth_url', '')
            
            fb_parsed = self.parse_auth_url(fb_url)
            ig_parsed = self.parse_auth_url(ig_url)
            
            if not fb_parsed or not ig_parsed:
                self.log_test(
                    "Configuration Consistency - URL Parsing", 
                    False, 
                    error="Failed to parse one or both URLs"
                )
                return False
            
            # Check App ID consistency (should be same)
            fb_client_id = fb_parsed['params'].get('client_id', '')
            ig_client_id = ig_parsed['params'].get('client_id', '')
            
            if fb_client_id == ig_client_id == EXPECTED_APP_ID:
                self.log_test(
                    "Configuration Consistency - App ID Match", 
                    True, 
                    f"Both platforms use same App ID: {fb_client_id}"
                )
            else:
                self.log_test(
                    "Configuration Consistency - App ID Match", 
                    False, 
                    error=f"App ID mismatch - Facebook: {fb_client_id}, Instagram: {ig_client_id}"
                )
                return False
            
            # Check Config ID difference (should be different)
            fb_config_id = fb_parsed['params'].get('config_id', '')
            ig_config_id = ig_parsed['params'].get('config_id', '')
            
            if fb_config_id != ig_config_id:
                self.log_test(
                    "Configuration Consistency - Config ID Difference", 
                    True, 
                    f"Platforms have different Config IDs - Facebook: {fb_config_id}, Instagram: {ig_config_id}"
                )
            else:
                self.log_test(
                    "Configuration Consistency - Config ID Difference", 
                    False, 
                    error=f"Config IDs should be different but both are: {fb_config_id}"
                )
                return False
            
            # Check domain consistency (should be same)
            fb_redirect = fb_parsed['params'].get('redirect_uri', '')
            ig_redirect = ig_parsed['params'].get('redirect_uri', '')
            
            if EXPECTED_DOMAIN in fb_redirect and EXPECTED_DOMAIN in ig_redirect:
                self.log_test(
                    "Configuration Consistency - Domain Match", 
                    True, 
                    f"Both platforms use correct domain: {EXPECTED_DOMAIN}"
                )
            else:
                self.log_test(
                    "Configuration Consistency - Domain Match", 
                    False, 
                    error=f"Domain mismatch - Facebook: {fb_redirect}, Instagram: {ig_redirect}"
                )
                return False
            
            return True
                
        except Exception as e:
            self.log_test("Configuration Consistency Testing", False, error=str(e))
            return False
    
    def test_url_validity(self):
        """Test that generated URLs are valid and accessible"""
        try:
            # Get Facebook URL
            fb_response = self.session.get(f"{BACKEND_URL}/social/facebook/auth-url")
            if fb_response.status_code == 200:
                fb_data = fb_response.json()
                fb_url = fb_data.get('auth_url', '')
                
                # Test if URL is well-formed (don't actually visit it)
                parsed = urllib.parse.urlparse(fb_url)
                if parsed.scheme and parsed.netloc and parsed.query:
                    self.log_test(
                        "URL Validity - Facebook URL Structure", 
                        True, 
                        f"Facebook URL is well-formed with all required components"
                    )
                else:
                    self.log_test(
                        "URL Validity - Facebook URL Structure", 
                        False, 
                        error="Facebook URL missing required components"
                    )
                    return False
            
            # Get Instagram URL
            ig_response = self.session.get(f"{BACKEND_URL}/social/instagram/auth-url")
            if ig_response.status_code == 200:
                ig_data = ig_response.json()
                ig_url = ig_data.get('auth_url', '')
                
                # Test if URL is well-formed (don't actually visit it)
                parsed = urllib.parse.urlparse(ig_url)
                if parsed.scheme and parsed.netloc and parsed.query:
                    self.log_test(
                        "URL Validity - Instagram URL Structure", 
                        True, 
                        f"Instagram URL is well-formed with all required components"
                    )
                else:
                    self.log_test(
                        "URL Validity - Instagram URL Structure", 
                        False, 
                        error="Instagram URL missing required components"
                    )
                    return False
            
            return True
                
        except Exception as e:
            self.log_test("URL Validity Testing", False, error=str(e))
            return False
    
    def run_comprehensive_test(self):
        """Run all OAuth configuration validation tests"""
        print("🎯 OAUTH CONFIGURATION VALIDATION - FACEBOOK & INSTAGRAM")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: {TEST_EMAIL}")
        print(f"Expected App ID: {EXPECTED_APP_ID}")
        print(f"Expected Facebook Config ID: {EXPECTED_FACEBOOK_CONFIG_ID}")
        print(f"Expected Instagram Config ID: {EXPECTED_INSTAGRAM_CONFIG_ID}")
        print(f"Expected Domain: {EXPECTED_DOMAIN}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 80)
        print()
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ CRITICAL: Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Test Facebook OAuth URL
        print("📘 FACEBOOK OAUTH CONFIGURATION TESTING")
        print("-" * 50)
        facebook_success = self.test_facebook_auth_url()
        print()
        
        # Step 3: Test Instagram OAuth URL
        print("📷 INSTAGRAM OAUTH CONFIGURATION TESTING")
        print("-" * 50)
        instagram_success = self.test_instagram_auth_url()
        print()
        
        # Step 4: Test configuration consistency
        print("🔄 CONFIGURATION CONSISTENCY TESTING")
        print("-" * 50)
        consistency_success = self.test_configuration_consistency()
        print()
        
        # Step 5: Test URL validity
        print("✅ URL VALIDITY TESTING")
        print("-" * 50)
        validity_success = self.test_url_validity()
        print()
        
        # Summary
        self.print_summary()
        
        return facebook_success and instagram_success and consistency_success and validity_success
    
    def print_summary(self):
        """Print test summary"""
        print("=" * 80)
        print("🎯 OAUTH CONFIGURATION VALIDATION SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "0%")
        print()
        
        # Group results by category
        facebook_tests = [r for r in self.test_results if 'Facebook' in r['test']]
        instagram_tests = [r for r in self.test_results if 'Instagram' in r['test']]
        consistency_tests = [r for r in self.test_results if 'Consistency' in r['test']]
        
        print("📘 FACEBOOK CONFIGURATION TESTS:")
        for result in facebook_tests:
            print(f"  {result['status']}: {result['test']}")
        print()
        
        print("📷 INSTAGRAM CONFIGURATION TESTS:")
        for result in instagram_tests:
            print(f"  {result['status']}: {result['test']}")
        print()
        
        print("🔄 CONSISTENCY & VALIDITY TESTS:")
        for result in consistency_tests:
            print(f"  {result['status']}: {result['test']}")
        
        # Add other tests
        other_tests = [r for r in self.test_results if not any(keyword in r['test'] for keyword in ['Facebook', 'Instagram', 'Consistency'])]
        for result in other_tests:
            if result['test'] != 'Authentication':  # Skip auth as it's not part of config validation
                print(f"  {result['status']}: {result['test']}")
        print()
        
        # Failed tests details
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print("❌ FAILED TESTS DETAILS:")
            for result in failed_tests:
                print(f"  • {result['test']}: {result['error']}")
            print()
        
        print("=" * 80)
        
        # Final assessment
        config_tests = [r for r in self.test_results if r['test'] != 'Authentication']
        config_passed = sum(1 for result in config_tests if result['success'])
        config_total = len(config_tests)
        
        if config_passed == config_total:
            print("🎉 OAUTH CONFIGURATION VALIDATION: SUCCESS")
            print("✅ Facebook OAuth URL configured correctly")
            print(f"✅ Facebook Config ID: {EXPECTED_FACEBOOK_CONFIG_ID}")
            print("✅ Instagram OAuth URL configured correctly")
            print(f"✅ Instagram Config ID: {EXPECTED_INSTAGRAM_CONFIG_ID}")
            print(f"✅ Both platforms use App ID: {EXPECTED_APP_ID}")
            print(f"✅ Both platforms redirect to: {EXPECTED_DOMAIN}")
            print("✅ Configuration is ready for Facebook Login for Business")
        else:
            print("🚨 OAUTH CONFIGURATION VALIDATION: ISSUES FOUND")
            print(f"❌ {config_total - config_passed} configuration tests failed")
            print("⚠️ OAuth configuration may not work correctly")
            print("⚠️ Review failed tests above for specific issues")
        
        print("=" * 80)

def main():
    """Main test execution"""
    tester = OAuthConfigTester()
    
    try:
        success = tester.run_comprehensive_test()
        
        # Exit with appropriate code
        if success:
            failed_count = sum(1 for result in tester.test_results if not result['success'])
            sys.exit(0 if failed_count == 0 else 1)
        else:
            sys.exit(2)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(3)
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        sys.exit(4)

if __name__ == "__main__":
    main()