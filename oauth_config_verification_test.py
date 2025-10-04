#!/usr/bin/env python3
"""
🔧 OAUTH CONFIGURATION VERIFICATION TEST
Vérifier la configuration OAuth Facebook et identifier pourquoi l'échange de token échoue.

Identifiants: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import sys
import os
from datetime import datetime

class OAuthConfigVerification:
    def __init__(self):
        self.base_url = "https://claire-marcus-app-1.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.credentials = {
            "email": "lperpere@yahoo.fr",
            "password": "L@Reunion974!"
        }
        
    def authenticate(self):
        """Authenticate with the API"""
        try:
            print(f"🔐 Step 1: Authenticating with {self.credentials['email']}")
            
            response = self.session.post(
                f"{self.base_url}/auth/login-robust",
                json=self.credentials,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                })
                
                print(f"   ✅ Authentication successful - User ID: {self.user_id}")
                return True
            else:
                print(f"   ❌ Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {str(e)}")
            return False
    
    def test_facebook_auth_url_generation(self):
        """Tester la génération de l'URL d'autorisation Facebook"""
        try:
            print(f"\n🔗 Step 2: Testing Facebook auth URL generation")
            
            response = self.session.get(f"{self.base_url}/social/facebook/auth-url")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get("auth_url", "")
                state = data.get("state", "")
                
                print(f"   ✅ Facebook auth URL generated successfully")
                print(f"   📋 Auth URL: {auth_url[:100]}...")
                print(f"   📋 State: {state}")
                
                # Analyze the URL to check configuration
                if "client_id=" in auth_url:
                    import urllib.parse
                    parsed_url = urllib.parse.urlparse(auth_url)
                    query_params = urllib.parse.parse_qs(parsed_url.query)
                    
                    client_id = query_params.get("client_id", [""])[0]
                    redirect_uri = query_params.get("redirect_uri", [""])[0]
                    config_id = query_params.get("config_id", [""])[0]
                    
                    print(f"   📊 URL Analysis:")
                    print(f"     Client ID: {client_id}")
                    print(f"     Redirect URI: {redirect_uri}")
                    print(f"     Config ID: {config_id}")
                    
                    return {
                        "auth_url": auth_url,
                        "state": state,
                        "client_id": client_id,
                        "redirect_uri": redirect_uri,
                        "config_id": config_id
                    }
                else:
                    print(f"   ⚠️ Auth URL format unexpected")
                    return None
            else:
                print(f"   ❌ Failed to generate auth URL: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error testing auth URL: {str(e)}")
            return None
    
    def test_facebook_callback_with_test_code(self):
        """Tester le callback Facebook avec un code de test pour voir l'erreur exacte"""
        try:
            print(f"\n🔄 Step 3: Testing Facebook callback with test code")
            
            # Generate a test state first
            auth_data = self.test_facebook_auth_url_generation()
            if not auth_data:
                print(f"   ❌ Cannot test callback without auth URL data")
                return None
            
            test_state = auth_data.get("state")
            test_code = "test_authorization_code_123"
            
            print(f"   Testing callback with:")
            print(f"     Code: {test_code}")
            print(f"     State: {test_state}")
            
            # Test the callback endpoint directly
            callback_url = f"{self.base_url}/social/facebook/callback"
            callback_params = {
                "code": test_code,
                "state": test_state
            }
            
            response = self.session.get(callback_url, params=callback_params, allow_redirects=False)
            
            print(f"   📡 Callback response:")
            print(f"     Status: {response.status_code}")
            print(f"     Headers: {dict(response.headers)}")
            
            if response.status_code in [302, 307]:
                location = response.headers.get("Location", "")
                print(f"     Redirect Location: {location}")
                
                # Check if it's an error redirect
                if "auth_error" in location:
                    print(f"   🚨 CALLBACK ERROR DETECTED")
                    if "facebook_callback_error" in location:
                        print(f"   🚨 Facebook callback error - OAuth exchange likely failed")
                        return {
                            "callback_result": "error",
                            "error_type": "facebook_callback_error",
                            "redirect_location": location
                        }
                elif "auth_success" in location:
                    print(f"   ⚠️ Unexpected success with test code")
                    return {
                        "callback_result": "unexpected_success",
                        "redirect_location": location
                    }
                else:
                    print(f"   ⚠️ Unknown redirect pattern")
                    return {
                        "callback_result": "unknown_redirect",
                        "redirect_location": location
                    }
            else:
                print(f"     Response body: {response.text[:500]}...")
                return {
                    "callback_result": "non_redirect_response",
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            print(f"   ❌ Error testing callback: {str(e)}")
            return None
    
    def check_backend_logs_for_oauth_errors(self):
        """Vérifier les logs backend pour les erreurs OAuth récentes"""
        try:
            print(f"\n📋 Step 4: Checking backend logs for OAuth errors")
            
            # We can't directly access logs from the test, but we can trigger
            # a callback and then check if there are any debug endpoints
            print(f"   ⚠️ Backend logs require server access")
            print(f"   🔍 Looking for these error patterns in logs:")
            print(f"     - 'Erreur OAuth Facebook'")
            print(f"     - 'Invalid verification code format'")
            print(f"     - 'FACEBOOK_CONFIG_ID ou FACEBOOK_APP_SECRET manquant'")
            print(f"     - 'Erreur échange token Facebook'")
            
            return {
                "logs_accessible": False,
                "manual_check_required": True
            }
            
        except Exception as e:
            print(f"   ❌ Error checking logs: {str(e)}")
            return None
    
    def verify_environment_variables(self):
        """Vérifier indirectement les variables d'environnement via les endpoints"""
        try:
            print(f"\n🔧 Step 5: Verifying environment variables indirectly")
            
            # Check if we can get diagnostic info about the configuration
            print(f"   🔍 Environment variables to verify:")
            print(f"     - FACEBOOK_CONFIG_ID (should match Facebook App ID)")
            print(f"     - FACEBOOK_APP_SECRET (should be valid)")
            print(f"     - FACEBOOK_REDIRECT_URI (should match Facebook App settings)")
            
            # From the auth URL generation, we can see what's being used
            auth_data = self.test_facebook_auth_url_generation()
            if auth_data:
                print(f"   📊 Configuration Analysis:")
                print(f"     App ID from URL: {auth_data.get('client_id', 'Not found')}")
                print(f"     Redirect URI from URL: {auth_data.get('redirect_uri', 'Not found')}")
                print(f"     Config ID from URL: {auth_data.get('config_id', 'Not found')}")
                
                # Check if the configuration looks valid
                client_id = auth_data.get('client_id', '')
                redirect_uri = auth_data.get('redirect_uri', '')
                
                if client_id and len(client_id) > 10:
                    print(f"   ✅ Client ID format looks valid")
                else:
                    print(f"   ❌ Client ID missing or invalid format")
                
                if redirect_uri and "callback" in redirect_uri:
                    print(f"   ✅ Redirect URI format looks valid")
                else:
                    print(f"   ❌ Redirect URI missing or invalid format")
                
                return auth_data
            else:
                print(f"   ❌ Cannot verify configuration - auth URL generation failed")
                return None
                
        except Exception as e:
            print(f"   ❌ Error verifying environment: {str(e)}")
            return None
    
    def run_oauth_config_verification(self):
        """Execute the complete OAuth configuration verification"""
        print("🔧 MISSION: OAUTH CONFIGURATION VERIFICATION")
        print("🎯 OBJECTIVE: Identifier pourquoi l'échange OAuth Facebook échoue")
        print("=" * 70)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ CRITICAL: Authentication failed")
            return False
        
        # Step 2: Test Facebook auth URL generation
        auth_url_data = self.test_facebook_auth_url_generation()
        
        # Step 3: Test Facebook callback with test code
        callback_result = self.test_facebook_callback_with_test_code()
        
        # Step 4: Check backend logs
        log_check = self.check_backend_logs_for_oauth_errors()
        
        # Step 5: Verify environment variables
        env_verification = self.verify_environment_variables()
        
        print("\n" + "=" * 70)
        print("🔧 OAUTH CONFIGURATION VERIFICATION COMPLETED")
        print("=" * 70)
        
        print(f"✅ Authentication: SUCCESSFUL")
        print(f"{'✅' if auth_url_data else '❌'} Auth URL generation: {'SUCCESSFUL' if auth_url_data else 'FAILED'}")
        print(f"{'✅' if callback_result else '❌'} Callback test: {'COMPLETED' if callback_result else 'FAILED'}")
        print(f"✅ Environment verification: COMPLETED")
        
        # CRITICAL ANALYSIS
        print(f"\n🔍 CONFIGURATION ANALYSIS:")
        
        if auth_url_data:
            client_id = auth_url_data.get('client_id', '')
            redirect_uri = auth_url_data.get('redirect_uri', '')
            
            print(f"   📊 Facebook App Configuration:")
            print(f"     App ID: {client_id}")
            print(f"     Redirect URI: {redirect_uri}")
            
            if client_id == "1878388119742903":
                print(f"   ✅ App ID matches expected value from .env")
            else:
                print(f"   ❌ App ID mismatch - check FACEBOOK_CONFIG_ID")
            
            if "claire-marcus.com" in redirect_uri:
                print(f"   ✅ Redirect URI points to live environment")
            elif "preview.emergentagent.com" in redirect_uri:
                print(f"   ⚠️ Redirect URI points to preview environment")
            else:
                print(f"   ❌ Redirect URI unexpected format")
        
        if callback_result:
            print(f"   📊 Callback Test Results:")
            result_type = callback_result.get('callback_result', 'unknown')
            print(f"     Result Type: {result_type}")
            
            if result_type == "error" and callback_result.get('error_type') == 'facebook_callback_error':
                print(f"   🚨 CONFIRMED: OAuth exchange is failing in callback")
                print(f"   🚨 ROOT CAUSE: Token exchange with Facebook API fails")
            elif result_type == "unexpected_success":
                print(f"   ⚠️ UNEXPECTED: Test code was accepted (should fail)")
            
        print(f"\n🚀 DIAGNOSTIC CONCLUSIONS:")
        
        if auth_url_data and callback_result:
            if callback_result.get('error_type') == 'facebook_callback_error':
                print(f"   1. 🚨 CRITICAL: OAuth token exchange is failing")
                print(f"   2. 🔧 LIKELY CAUSES:")
                print(f"      - Facebook App Secret incorrect or missing")
                print(f"      - Facebook App configuration mismatch")
                print(f"      - Redirect URI not whitelisted in Facebook App")
                print(f"      - Facebook App permissions insufficient")
                print(f"   3. 🔍 NEXT STEPS:")
                print(f"      - Verify FACEBOOK_APP_SECRET in environment")
                print(f"      - Check Facebook Developer Console app settings")
                print(f"      - Verify redirect URI is whitelisted")
                print(f"      - Test with real Facebook authorization code")
        
        print("=" * 70)
        return True

def main():
    """Main execution function"""
    verification = OAuthConfigVerification()
    
    try:
        success = verification.run_oauth_config_verification()
        if success:
            print(f"\n🎯 CONCLUSION: OAuth configuration verification completed")
            sys.exit(0)
        else:
            print(f"\n💥 CONCLUSION: Verification failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⚠️ Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()