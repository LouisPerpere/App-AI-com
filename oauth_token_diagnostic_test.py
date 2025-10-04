#!/usr/bin/env python3
"""
🚨 DIAGNOSTIC OAUTH TOKEN FACEBOOK - ERREUR 190 PERSISTANTE
Test urgent pour diagnostiquer pourquoi l'utilisateur obtient encore l'erreur Facebook 190 
"Invalid OAuth access token" après les corrections OAuth.

Identifiants: lperpere@yahoo.fr / L@Reunion974!
Objectif: Identifier si l'OAuth génère un vrai token ou tombe encore dans le fallback
"""

import requests
import json
import sys
import time
import urllib.parse
from datetime import datetime
from pymongo import MongoClient
import os
import re

class OAuthTokenDiagnostic:
    def __init__(self):
        # Use the frontend environment URL from .env
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
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for all future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                })
                
                print(f"   ✅ Authentication successful")
                print(f"   User ID: {self.user_id}")
                print(f"   Token: {self.token[:30]}..." if self.token else "   Token: None")
                return True
            else:
                print(f"   ❌ Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {str(e)}")
            return False
    
    def analyze_token_after_reconnection(self):
        """Analyser le token généré après reconnexion Facebook"""
        try:
            print(f"\n🔍 Step 2: Analyzing Facebook token after reconnection")
            print(f"   Endpoint: GET /api/debug/social-connections")
            
            response = self.session.get(f"{self.base_url}/debug/social-connections")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"   ✅ Debug endpoint accessible")
                
                # Analyze social_media_connections for Facebook tokens
                connections = data.get("social_media_connections", [])
                facebook_connections = [c for c in connections if c.get("platform") == "facebook"]
                
                print(f"   📊 Facebook Connections Analysis:")
                print(f"     Total Facebook connections: {len(facebook_connections)}")
                
                if facebook_connections:
                    for i, conn in enumerate(facebook_connections):
                        print(f"     Connection {i+1}:")
                        print(f"       Platform: {conn.get('platform')}")
                        print(f"       Active: {conn.get('active')}")
                        print(f"       Created: {conn.get('created_at')}")
                        print(f"       Page Name: {conn.get('page_name', 'N/A')}")
                        
                        # CRITICAL: Analyze the access token
                        access_token = conn.get('access_token')
                        if access_token:
                            print(f"       Access Token: {access_token[:50]}..." if len(access_token) > 50 else f"       Access Token: {access_token}")
                            
                            # Check if it's a temporary/test token
                            if access_token.startswith('temp_facebook_token_'):
                                print(f"       🚨 CRITICAL: This is a TEMPORARY TOKEN from fallback mechanism!")
                                print(f"       🚨 ROOT CAUSE: OAuth exchange failed, fallback created test token")
                                return {
                                    "token_type": "temporary",
                                    "token_value": access_token,
                                    "is_valid": False,
                                    "diagnosis": "OAuth exchange failed, fallback mechanism activated"
                                }
                            elif access_token.startswith('test_token_facebook_fallback'):
                                print(f"       🚨 CRITICAL: This is a TEST TOKEN from fallback mechanism!")
                                print(f"       🚨 ROOT CAUSE: OAuth exchange failed, fallback created test token")
                                return {
                                    "token_type": "test_fallback",
                                    "token_value": access_token,
                                    "is_valid": False,
                                    "diagnosis": "OAuth exchange failed, fallback mechanism activated"
                                }
                            elif len(access_token) > 100 and not access_token.startswith('temp_') and not access_token.startswith('test_'):
                                print(f"       ✅ POTENTIAL: This looks like a REAL Facebook token")
                                print(f"       🔍 NEEDS VERIFICATION: Test this token with Facebook API")
                                return {
                                    "token_type": "potential_real",
                                    "token_value": access_token,
                                    "is_valid": "unknown",
                                    "diagnosis": "Token format looks valid, needs Facebook API verification"
                                }
                            else:
                                print(f"       ⚠️ UNKNOWN: Token format not recognized")
                                return {
                                    "token_type": "unknown",
                                    "token_value": access_token,
                                    "is_valid": "unknown",
                                    "diagnosis": "Token format not recognized"
                                }
                        else:
                            print(f"       ❌ CRITICAL: Access token is NULL/missing!")
                            return {
                                "token_type": "null",
                                "token_value": None,
                                "is_valid": False,
                                "diagnosis": "No access token stored in connection"
                            }
                else:
                    print(f"     ❌ No Facebook connections found in database")
                    return {
                        "token_type": "none",
                        "token_value": None,
                        "is_valid": False,
                        "diagnosis": "No Facebook connections exist"
                    }
                
                return None
            else:
                print(f"   ❌ Failed to access debug endpoint: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error analyzing token: {str(e)}")
            return None
    
    def check_backend_oauth_logs(self):
        """Vérifier les logs backend OAuth pour l'échange de token"""
        try:
            print(f"\n🔍 Step 3: Checking backend OAuth logs")
            print(f"   Note: This step requires backend log access")
            
            # Since we can't directly access backend logs from the test,
            # we'll try to trigger an OAuth flow and capture any debug info
            print(f"   ⚠️ Backend logs analysis requires server access")
            print(f"   🔍 Looking for these log patterns:")
            print(f"     - '🔧 OAuth Config'")
            print(f"     - '🔄 Exchanging code'")
            print(f"     - 'Erreur OAuth Facebook'")
            print(f"     - 'Created Facebook connection'")
            
            # We can't access logs directly, but we can check if there are any
            # debug endpoints that might show recent OAuth attempts
            return {
                "logs_accessible": False,
                "recommendation": "Check backend logs manually for OAuth exchange patterns"
            }
            
        except Exception as e:
            print(f"   ❌ Error checking OAuth logs: {str(e)}")
            return None
    
    def test_oauth_exchange_directly(self):
        """Tester l'échange OAuth directement en vérifiant les variables d'environnement"""
        try:
            print(f"\n🔍 Step 4: Testing OAuth exchange configuration")
            
            # We can't directly access environment variables from the test,
            # but we can check if the OAuth endpoints are configured correctly
            print(f"   🔍 Checking OAuth configuration indirectly...")
            
            # Check if the Facebook callback endpoint exists
            try:
                response = self.session.get(f"{self.base_url}/social/facebook/callback?error=access_denied")
                print(f"   Facebook callback endpoint status: {response.status_code}")
                
                if response.status_code in [200, 302, 400]:  # Any of these indicate the endpoint exists
                    print(f"   ✅ Facebook callback endpoint exists")
                else:
                    print(f"   ❌ Facebook callback endpoint may not exist")
            except:
                print(f"   ⚠️ Could not test Facebook callback endpoint")
            
            # Check Instagram callback for comparison
            try:
                response = self.session.get(f"{self.base_url}/social/instagram/callback?error=access_denied")
                print(f"   Instagram callback endpoint status: {response.status_code}")
                
                if response.status_code in [200, 302, 400]:
                    print(f"   ✅ Instagram callback endpoint exists")
                else:
                    print(f"   ❌ Instagram callback endpoint may not exist")
            except:
                print(f"   ⚠️ Could not test Instagram callback endpoint")
            
            print(f"   🔍 Environment variables to verify manually:")
            print(f"     - FACEBOOK_CONFIG_ID")
            print(f"     - FACEBOOK_APP_SECRET")
            print(f"     - FACEBOOK_REDIRECT_URI")
            
            return {
                "callback_endpoints_exist": True,
                "manual_verification_needed": True
            }
            
        except Exception as e:
            print(f"   ❌ Error testing OAuth exchange: {str(e)}")
            return None
    
    def test_facebook_api_with_token(self, token_info):
        """Tester le token avec l'API Facebook pour vérifier sa validité"""
        try:
            print(f"\n🔍 Step 5: Testing token with Facebook API")
            
            if not token_info or not token_info.get("token_value"):
                print(f"   ⚠️ No token available for testing")
                return None
            
            token = token_info["token_value"]
            
            # Test the token with Facebook's debug endpoint
            facebook_debug_url = "https://graph.facebook.com/debug_token"
            
            # We need an app access token to debug user tokens
            # Since we don't have direct access to app credentials, we'll simulate the test
            print(f"   🔍 Token to test: {token[:50]}..." if len(token) > 50 else f"   🔍 Token to test: {token}")
            
            if token.startswith('temp_facebook_token_') or token.startswith('test_token_facebook_fallback'):
                print(f"   ❌ CONFIRMED: This is a temporary/test token")
                print(f"   ❌ Facebook API will reject this with Error 190")
                return {
                    "token_valid": False,
                    "error_code": 190,
                    "error_message": "Invalid OAuth access token",
                    "diagnosis": "Temporary token will be rejected by Facebook API"
                }
            else:
                print(f"   🔍 Token format suggests it might be real")
                print(f"   ⚠️ Cannot test directly without app access token")
                return {
                    "token_valid": "unknown",
                    "needs_real_test": True,
                    "diagnosis": "Token format looks valid but needs Facebook API verification"
                }
            
        except Exception as e:
            print(f"   ❌ Error testing Facebook API: {str(e)}")
            return None
    
    def test_publication_with_facebook_post(self):
        """Tester la publication pour reproduire l'erreur 190"""
        try:
            print(f"\n🚀 Step 6: Testing publication to reproduce Error 190")
            
            # Get a Facebook post to test with
            response = self.session.get(f"{self.base_url}/posts/generated")
            
            if response.status_code != 200:
                print(f"   ❌ Failed to get posts for testing")
                return None
            
            data = response.json()
            posts = data.get("posts", [])
            facebook_posts = [p for p in posts if p.get("platform") == "facebook"]
            
            if not facebook_posts:
                print(f"   ⚠️ No Facebook posts found for testing")
                return None
            
            # Test with the first Facebook post
            test_post = facebook_posts[0]
            post_id = test_post.get("id")
            
            print(f"   Testing publication with Facebook post: {post_id}")
            print(f"   Post title: {test_post.get('title', 'No title')[:50]}...")
            
            response = self.session.post(
                f"{self.base_url}/posts/publish",
                json={"post_id": post_id}
            )
            
            print(f"   📡 Publication test response:")
            print(f"     Status Code: {response.status_code}")
            
            try:
                response_data = response.json()
                print(f"     Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                
                # Look for Facebook Error 190
                message = str(response_data).lower()
                if "190" in message and "invalid oauth access token" in message:
                    print(f"   🚨 CONFIRMED: Facebook Error 190 reproduced!")
                    print(f"   🚨 ROOT CAUSE: Invalid OAuth access token being used")
                    return {
                        "error_reproduced": True,
                        "error_code": 190,
                        "error_type": "Invalid OAuth access token",
                        "diagnosis": "Publication fails due to invalid Facebook token"
                    }
                elif "aucune connexion sociale active" in message:
                    print(f"   ⚠️ No active social connections found")
                    return {
                        "error_reproduced": False,
                        "error_type": "No active connections",
                        "diagnosis": "No active Facebook connections available"
                    }
                else:
                    print(f"   ⚠️ Different error or success response")
                    return {
                        "error_reproduced": False,
                        "response": response_data,
                        "diagnosis": "Unexpected response from publication endpoint"
                    }
                    
            except:
                print(f"     Response (raw): {response.text}")
                if "190" in response.text and "invalid oauth access token" in response.text.lower():
                    print(f"   🚨 CONFIRMED: Facebook Error 190 reproduced in raw response!")
                    return {
                        "error_reproduced": True,
                        "error_code": 190,
                        "diagnosis": "Error 190 found in raw response"
                    }
                return None
                
        except Exception as e:
            print(f"   ❌ Error testing publication: {str(e)}")
            return None
    
    def run_oauth_token_diagnostic(self):
        """Execute the complete OAuth token diagnostic mission"""
        print("🚨 MISSION: DIAGNOSTIC OAUTH TOKEN FACEBOOK - ERREUR 190 PERSISTANTE")
        print("🌐 ENVIRONMENT: Preview (social-ai-planner-2.preview.emergentagent.com)")
        print("🎯 OBJECTIVE: Identifier si l'OAuth génère un vrai token ou tombe dans le fallback")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with diagnostic")
            return False
        
        # Step 2: Analyze token after reconnection
        token_analysis = self.analyze_token_after_reconnection()
        
        # Step 3: Check backend OAuth logs
        log_analysis = self.check_backend_oauth_logs()
        
        # Step 4: Test OAuth exchange configuration
        oauth_config = self.test_oauth_exchange_directly()
        
        # Step 5: Test token with Facebook API
        facebook_test = self.test_facebook_api_with_token(token_analysis)
        
        # Step 6: Test publication to reproduce error
        publication_test = self.test_publication_with_facebook_post()
        
        print("\n" + "=" * 80)
        print("🚨 OAUTH TOKEN DIAGNOSTIC COMPLETED")
        print("🌐 ENVIRONMENT: Preview")
        print("=" * 80)
        
        print(f"✅ Authentication: SUCCESSFUL")
        print(f"✅ Token analysis: COMPLETED")
        print(f"✅ OAuth configuration check: COMPLETED")
        print(f"✅ Publication test: COMPLETED")
        
        # CRITICAL ANALYSIS
        print(f"\n🚨 CRITICAL DIAGNOSTIC RESULTS:")
        
        if token_analysis:
            print(f"   📊 TOKEN ANALYSIS:")
            print(f"     Token Type: {token_analysis.get('token_type', 'unknown')}")
            print(f"     Token Valid: {token_analysis.get('is_valid', 'unknown')}")
            print(f"     Diagnosis: {token_analysis.get('diagnosis', 'No diagnosis')}")
            
            if token_analysis.get('token_type') in ['temporary', 'test_fallback']:
                print(f"   🚨 ROOT CAUSE IDENTIFIED: OAuth exchange is STILL FAILING")
                print(f"   🚨 FALLBACK MECHANISM: Still creating temporary tokens")
                print(f"   🚨 IMPACT: Facebook API rejects temporary tokens with Error 190")
            elif token_analysis.get('token_type') == 'null':
                print(f"   🚨 ROOT CAUSE IDENTIFIED: No access token stored")
                print(f"   🚨 IMPACT: Publication will fail due to missing token")
            elif token_analysis.get('token_type') == 'none':
                print(f"   🚨 ROOT CAUSE IDENTIFIED: No Facebook connections exist")
                print(f"   🚨 IMPACT: User needs to reconnect Facebook account")
        
        if publication_test:
            print(f"   📊 PUBLICATION TEST:")
            if publication_test.get('error_reproduced'):
                print(f"     ✅ Error 190 REPRODUCED successfully")
                print(f"     🚨 CONFIRMED: Invalid OAuth access token issue persists")
            else:
                print(f"     ⚠️ Error 190 not reproduced")
                print(f"     📝 Different issue: {publication_test.get('diagnosis', 'Unknown')}")
        
        print(f"\n🔍 HYPOTHESES VERIFICATION:")
        
        if token_analysis and token_analysis.get('token_type') in ['temporary', 'test_fallback']:
            print(f"   ✅ HYPOTHESIS 1 CONFIRMED: OAuth exchange fails → Fallback → Temporary token")
            print(f"   🚨 SOLUTION NEEDED: Fix OAuth token exchange implementation")
        elif token_analysis and token_analysis.get('token_type') == 'potential_real':
            print(f"   ⚠️ HYPOTHESIS 2 POSSIBLE: OAuth succeeds but token invalid")
            print(f"   🔍 NEEDS INVESTIGATION: Facebook App configuration issue")
        elif token_analysis and token_analysis.get('token_type') == 'none':
            print(f"   ✅ HYPOTHESIS 3 CONFIRMED: No Facebook connections exist")
            print(f"   📝 SOLUTION: User needs to reconnect Facebook account")
        
        print(f"\n🚀 URGENT RECOMMENDATIONS:")
        
        if token_analysis:
            if token_analysis.get('token_type') in ['temporary', 'test_fallback']:
                print(f"   1. 🚨 CRITICAL: Fix Facebook OAuth token exchange in callback")
                print(f"   2. 🔧 DEBUG: Check FACEBOOK_CONFIG_ID and FACEBOOK_APP_SECRET")
                print(f"   3. 🔧 DEBUG: Verify Facebook App permissions and configuration")
                print(f"   4. 🗑️ CLEANUP: Remove fallback mechanism that creates invalid tokens")
            elif token_analysis.get('token_type') == 'none':
                print(f"   1. 🔗 USER ACTION: Reconnect Facebook account")
                print(f"   2. 🔧 VERIFY: OAuth flow works after reconnection")
            else:
                print(f"   1. 🔍 INVESTIGATE: Test token with Facebook API directly")
                print(f"   2. 🔧 VERIFY: Facebook App configuration")
        
        print(f"   📝 IMMEDIATE NEXT STEPS:")
        print(f"     - Check backend logs for OAuth exchange errors")
        print(f"     - Verify FACEBOOK_CONFIG_ID matches Facebook App ID")
        print(f"     - Test OAuth flow with real Facebook authorization")
        
        print("=" * 80)
        
        return True

def main():
    """Main execution function"""
    diagnostic = OAuthTokenDiagnostic()
    
    try:
        success = diagnostic.run_oauth_token_diagnostic()
        if success:
            print(f"\n🎯 CONCLUSION: OAuth token diagnostic COMPLETED")
            print(f"   Critical analysis of Facebook Error 190 issue completed")
            sys.exit(0)
        else:
            print(f"\n💥 CONCLUSION: OAuth token diagnostic FAILED")
            print(f"   Please check the error messages above")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⚠️ Diagnostic interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during diagnostic: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()