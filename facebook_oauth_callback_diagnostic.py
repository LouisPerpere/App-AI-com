#!/usr/bin/env python3
"""
DIAGNOSTIC CRITIQUE - AUTHENTIFICATION FACEBOOK OAUTH CALLBACK

Problème rapporté par l'utilisateur français: Malgré les corrections dans Facebook Developer Console, 
le token longue durée ne se sauvegarde toujours pas.

CONTEXTE TECHNIQUE:
- Corrections Facebook App faites (HTTPS, domaines, callbacks)
- Code implémente le flow 3 étapes correct (code → short-lived → long-lived → page token EAA)
- Upload binaire via /photos endpoint implémenté correctement
- Problème persiste: boutons restent "Connecter" au lieu de "Connecté"

TESTS REQUIS:
1. Tester GET /api/social/connections/status - vérifier état actuel connexions
2. Tester GET /api/debug/social-connections - analyser base de données complète
3. Vérifier si callback Facebook est accessible: GET /api/social/facebook/callback
4. Tester generation URL OAuth: GET /api/social/facebook/auth-url
5. Analyser collections MongoDB: social_media_connections vs social_connections_old

OBJECTIF: Identifier pourquoi le callback OAuth ne sauvegarde pas les tokens EAA permanents 
malgré l'implémentation technique correcte.

Credentials: lperpere@yahoo.fr / L@Reunion974!
Backend: https://social-pub-hub.preview.emergentagent.com/api
"""

import requests
import json
import time
import sys
import os
from urllib.parse import urlparse, parse_qs

# Configuration
BACKEND_URL = "https://social-pub-hub.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class FacebookOAuthCallbackDiagnostic:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        
    def authenticate(self):
        """Authenticate with the backend"""
        print("🔐 Step 1: Authentication")
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json=TEST_CREDENTIALS,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                print(f"   ✅ Authentication successful")
                print(f"   ✅ User ID: {self.user_id}")
                return True
            else:
                print(f"   ❌ Authentication failed: {response.status_code}")
                print(f"   ❌ Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {e}")
            return False
    
    def test_social_connections_status(self):
        """Test 1: GET /api/social/connections/status - vérifier état actuel connexions"""
        print("\n📊 Test 1: Social Connections Status")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/social/connections/status")
            print(f"   📡 GET /api/social/connections/status")
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"      Response: {json.dumps(data, indent=2)}")
                
                # Analyze connection status
                facebook_connected = data.get("facebook", {}).get("connected", False)
                instagram_connected = data.get("instagram", {}).get("connected", False)
                
                print(f"   📘 Facebook Connected: {facebook_connected}")
                print(f"   📷 Instagram Connected: {instagram_connected}")
                
                if facebook_connected:
                    print("   ✅ Facebook appears connected in status")
                else:
                    print("   ❌ Facebook NOT connected in status")
                    
                return True
            else:
                print(f"      Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Social connections status test error: {e}")
            return False
    
    def test_debug_social_connections(self):
        """Test 2: GET /api/debug/social-connections - analyser base de données complète"""
        print("\n🔍 Test 2: Debug Social Connections Database Analysis")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/debug/social-connections")
            print(f"   📡 GET /api/debug/social-connections")
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"      Response: {json.dumps(data, indent=2)}")
                
                # Analyze database collections
                social_media_connections = data.get("social_media_connections", [])
                social_connections_old = data.get("social_connections_old", [])
                
                print(f"   📊 social_media_connections: {len(social_media_connections)} items")
                print(f"   📊 social_connections_old: {len(social_connections_old)} items")
                
                # Analyze Facebook connections specifically
                facebook_new = [c for c in social_media_connections if c.get("platform") == "facebook"]
                facebook_old = [c for c in social_connections_old if c.get("platform") == "facebook"]
                
                print(f"   📘 Facebook in new collection: {len(facebook_new)}")
                print(f"   📘 Facebook in old collection: {len(facebook_old)}")
                
                # Check for active connections
                active_facebook_new = [c for c in facebook_new if c.get("active", False)]
                active_facebook_old = [c for c in facebook_old if c.get("is_active", False)]
                
                print(f"   ✅ Active Facebook (new): {len(active_facebook_new)}")
                print(f"   ✅ Active Facebook (old): {len(active_facebook_old)}")
                
                # Check access tokens
                for conn in facebook_new:
                    token = conn.get("access_token", "")
                    token_preview = token[:20] + "..." if len(token) > 20 else token
                    print(f"   🔑 Facebook token (new): {token_preview}")
                    
                for conn in facebook_old:
                    token = conn.get("access_token", "")
                    token_preview = token[:20] + "..." if len(token) > 20 else token
                    print(f"   🔑 Facebook token (old): {token_preview}")
                
                return True
            else:
                print(f"      Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Debug social connections test error: {e}")
            return False
    
    def test_facebook_callback_accessibility(self):
        """Test 3: Vérifier si callback Facebook est accessible"""
        print("\n📞 Test 3: Facebook Callback Accessibility")
        
        try:
            callback_url = f"{BACKEND_URL}/social/facebook/callback"
            
            # Test 1: Basic accessibility (should return error but be accessible)
            print(f"   📡 GET {callback_url} (basic accessibility)")
            response = requests.get(callback_url)
            print(f"      Status: {response.status_code}")
            
            if response.status_code in [200, 302, 400]:
                print("   ✅ Callback endpoint is accessible")
            else:
                print(f"   ❌ Callback endpoint not accessible: {response.status_code}")
                return False
            
            # Test 2: With invalid parameters (should handle gracefully)
            print(f"   📡 GET {callback_url}?code=test&state=invalid")
            response_invalid = requests.get(f"{callback_url}?code=test&state=invalid")
            print(f"      Status: {response_invalid.status_code}")
            
            if response_invalid.status_code in [200, 302, 400]:
                print("   ✅ Callback handles invalid parameters gracefully")
            else:
                print(f"   ❌ Callback error with invalid params: {response_invalid.status_code}")
            
            # Test 3: Check if callback redirects properly
            if response.status_code == 302:
                location = response.headers.get("Location", "")
                print(f"   🔄 Redirect location: {location}")
                
                if "facebook_invalid_state" in location or "error" in location:
                    print("   ✅ Callback redirects with proper error handling")
                else:
                    print("   ⚠️ Callback redirect may not handle errors properly")
            
            return True
                
        except Exception as e:
            print(f"   ❌ Facebook callback accessibility test error: {e}")
            return False
    
    def test_oauth_url_generation(self):
        """Test 4: Tester generation URL OAuth"""
        print("\n🔗 Test 4: OAuth URL Generation")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/social/facebook/auth-url")
            print(f"   📡 GET /api/social/facebook/auth-url")
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get("auth_url", "")
                state = data.get("state", "")
                
                print(f"   🔗 Auth URL: {auth_url}")
                print(f"   🎫 State: {state}")
                
                # Parse and analyze the URL
                parsed_url = urlparse(auth_url)
                query_params = parse_qs(parsed_url.query)
                
                print(f"   🔍 URL Analysis:")
                print(f"      Domain: {parsed_url.netloc}")
                print(f"      Path: {parsed_url.path}")
                
                # Check required parameters
                required_params = ["client_id", "config_id", "redirect_uri", "response_type", "scope", "state"]
                missing_params = []
                
                for param in required_params:
                    if param in query_params:
                        value = query_params[param][0] if query_params[param] else ""
                        print(f"      ✅ {param}: {value[:50]}...")
                    else:
                        missing_params.append(param)
                        print(f"      ❌ {param}: MISSING")
                
                if not missing_params:
                    print("   ✅ All required OAuth parameters present")
                else:
                    print(f"   ❌ Missing parameters: {missing_params}")
                
                # Check state format (should be random|user_id)
                if "|" in state:
                    state_parts = state.split("|", 1)
                    print(f"   🎫 State format: {state_parts[0][:10]}...| {state_parts[1]}")
                    print("   ✅ State format appears correct (random|user_id)")
                else:
                    print("   ❌ State format incorrect (should be random|user_id)")
                
                return True
            else:
                print(f"      Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ OAuth URL generation test error: {e}")
            return False
    
    def test_mongodb_collections_analysis(self):
        """Test 5: Analyser collections MongoDB"""
        print("\n🗄️ Test 5: MongoDB Collections Analysis")
        
        try:
            # This test relies on the debug endpoint to analyze collections
            response = self.session.get(f"{BACKEND_URL}/debug/social-connections")
            
            if response.status_code != 200:
                print(f"   ❌ Cannot access debug endpoint for collection analysis")
                return False
            
            data = response.json()
            
            # Analyze collection structure and data consistency
            social_media_connections = data.get("social_media_connections", [])
            social_connections_old = data.get("social_connections_old", [])
            
            print(f"   📊 Collection Analysis:")
            print(f"      social_media_connections: {len(social_media_connections)} records")
            print(f"      social_connections_old: {len(social_connections_old)} records")
            
            # Check for data inconsistencies
            print(f"   🔍 Data Consistency Analysis:")
            
            # Check if there are connections in old but not in new
            old_platforms = set(c.get("platform") for c in social_connections_old)
            new_platforms = set(c.get("platform") for c in social_media_connections)
            
            print(f"      Platforms in old collection: {old_platforms}")
            print(f"      Platforms in new collection: {new_platforms}")
            
            if old_platforms - new_platforms:
                print(f"   ⚠️ Platforms only in old collection: {old_platforms - new_platforms}")
            
            if new_platforms - old_platforms:
                print(f"   ⚠️ Platforms only in new collection: {new_platforms - old_platforms}")
            
            # Check Facebook specifically
            facebook_old = [c for c in social_connections_old if c.get("platform") == "facebook"]
            facebook_new = [c for c in social_media_connections if c.get("platform") == "facebook"]
            
            print(f"   📘 Facebook Analysis:")
            print(f"      Old collection: {len(facebook_old)} Facebook connections")
            print(f"      New collection: {len(facebook_new)} Facebook connections")
            
            # Check token quality
            for i, conn in enumerate(facebook_old):
                token = conn.get("access_token", "")
                is_active = conn.get("is_active", False)
                created_at = conn.get("created_at", "")
                
                if token.startswith("temp_facebook_token"):
                    print(f"      ❌ Old[{i}]: Temporary token detected - {token[:30]}...")
                elif token == "test_token_facebook_fallback":
                    print(f"      ❌ Old[{i}]: Test fallback token detected")
                elif len(token) > 50:
                    print(f"      ✅ Old[{i}]: Real token (length: {len(token)}) - Active: {is_active}")
                else:
                    print(f"      ⚠️ Old[{i}]: Unknown token format - {token[:20]}...")
            
            for i, conn in enumerate(facebook_new):
                token = conn.get("access_token", "")
                active = conn.get("active", False)
                created_at = conn.get("created_at", "")
                
                if token and token.startswith("temp_facebook_token"):
                    print(f"      ❌ New[{i}]: Temporary token detected - {token[:30]}...")
                elif token == "test_token_facebook_fallback":
                    print(f"      ❌ New[{i}]: Test fallback token detected")
                elif token and len(token) > 50:
                    print(f"      ✅ New[{i}]: Real token (length: {len(token)}) - Active: {active}")
                else:
                    print(f"      ⚠️ New[{i}]: Token issue - {token[:20] if token else 'None'}...")
            
            return True
                
        except Exception as e:
            print(f"   ❌ MongoDB collections analysis error: {e}")
            return False
    
    def test_callback_state_validation(self):
        """Test 6: Test callback state validation logic"""
        print("\n🎫 Test 6: Callback State Validation Logic")
        
        try:
            # First get a proper state from auth URL generation
            auth_response = self.session.get(f"{BACKEND_URL}/social/facebook/auth-url")
            
            if auth_response.status_code != 200:
                print("   ❌ Cannot get auth URL for state testing")
                return False
            
            auth_data = auth_response.json()
            valid_state = auth_data.get("state", "")
            
            print(f"   🎫 Generated state: {valid_state}")
            
            # Test callback with this state (should fail at token exchange, not state validation)
            callback_url = f"{BACKEND_URL}/social/facebook/callback"
            test_params = {
                "code": "test_authorization_code",
                "state": valid_state
            }
            
            print(f"   📞 Testing callback with valid state format")
            callback_response = requests.get(callback_url, params=test_params)
            print(f"      Status: {callback_response.status_code}")
            
            # Check if it's a redirect
            if callback_response.status_code == 302:
                location = callback_response.headers.get("Location", "")
                print(f"      Redirect: {location}")
                
                if "facebook_invalid_state" in location:
                    print("   ❌ State validation failed (unexpected)")
                elif "facebook_token_error" in location or "error" in location:
                    print("   ✅ State validation passed, failed at token exchange (expected)")
                else:
                    print("   ⚠️ Unexpected redirect behavior")
            
            # Test with invalid state format
            print(f"   📞 Testing callback with invalid state format")
            invalid_test_params = {
                "code": "test_authorization_code", 
                "state": "invalid_state_no_pipe"
            }
            
            invalid_callback_response = requests.get(callback_url, params=invalid_test_params)
            print(f"      Status: {invalid_callback_response.status_code}")
            
            if invalid_callback_response.status_code == 302:
                location = invalid_callback_response.headers.get("Location", "")
                print(f"      Redirect: {location}")
                
                if "facebook_invalid_state" in location:
                    print("   ✅ Invalid state properly rejected")
                else:
                    print("   ❌ Invalid state not properly rejected")
            
            return True
                
        except Exception as e:
            print(f"   ❌ Callback state validation test error: {e}")
            return False
    
    def run_diagnostic(self):
        """Run complete Facebook OAuth callback diagnostic"""
        print("🚨 DIAGNOSTIC CRITIQUE - AUTHENTIFICATION FACEBOOK OAUTH CALLBACK")
        print("=" * 80)
        print("Problème: Tokens longue durée ne se sauvegardent pas malgré corrections Facebook App")
        print("Objectif: Identifier pourquoi callback OAuth ne sauvegarde pas tokens EAA permanents")
        print("=" * 80)
        
        if not self.authenticate():
            print("\n❌ DIAGNOSTIC FAILED: Authentication error")
            return False
        
        tests = [
            ("Social Connections Status", self.test_social_connections_status),
            ("Debug Social Connections Database", self.test_debug_social_connections),
            ("Facebook Callback Accessibility", self.test_facebook_callback_accessibility),
            ("OAuth URL Generation", self.test_oauth_url_generation),
            ("MongoDB Collections Analysis", self.test_mongodb_collections_analysis),
            ("Callback State Validation Logic", self.test_callback_state_validation)
        ]
        
        results = []
        critical_issues = []
        
        for test_name, test_func in tests:
            try:
                print(f"\n{'='*60}")
                result = test_func()
                results.append((test_name, result))
                
                if not result:
                    critical_issues.append(test_name)
                    
            except Exception as e:
                print(f"\n❌ Test '{test_name}' crashed: {e}")
                results.append((test_name, False))
                critical_issues.append(test_name)
        
        # Diagnostic Summary
        print("\n" + "=" * 80)
        print("📋 RÉSULTATS DU DIAGNOSTIC")
        print("=" * 80)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
            if result:
                passed += 1
        
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        print(f"\n📊 TAUX DE RÉUSSITE: {passed}/{total} ({success_rate:.1f}%)")
        
        # Critical Issues Analysis
        if critical_issues:
            print(f"\n🚨 PROBLÈMES CRITIQUES IDENTIFIÉS:")
            for issue in critical_issues:
                print(f"   ❌ {issue}")
        
        # Diagnostic Conclusion
        print(f"\n" + "=" * 80)
        print("🎯 CONCLUSION DU DIAGNOSTIC")
        print("=" * 80)
        
        if success_rate >= 80:
            print("✅ SYSTÈME FONCTIONNEL - Problème probablement dans la logique de sauvegarde des tokens")
            print("🔍 RECOMMANDATIONS:")
            print("   • Vérifier la logique de conversion short-lived → long-lived token")
            print("   • Analyser les logs backend pendant le callback OAuth")
            print("   • Vérifier la sauvegarde des tokens EAA dans la base de données")
        else:
            print("❌ PROBLÈMES SYSTÈME DÉTECTÉS - Corrections requises avant analyse approfondie")
            print("🔧 ACTIONS REQUISES:")
            for issue in critical_issues:
                print(f"   • Corriger: {issue}")
        
        return success_rate >= 80

if __name__ == "__main__":
    diagnostic = FacebookOAuthCallbackDiagnostic()
    success = diagnostic.run_diagnostic()
    sys.exit(0 if success else 1)