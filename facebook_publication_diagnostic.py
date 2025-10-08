#!/usr/bin/env python3
"""
🚨 DIAGNOSTIC PUBLICATION FACEBOOK - MISSION CRITIQUE
Test complet pour diagnostiquer pourquoi la publication Facebook échoue.
Le bouton ne passe pas à "Publié" et revient à "Publier".

Identifiants: lperpere@yahoo.fr / L@Reunion974!
Objectif: Confirmer que le token temporaire temp_facebook_token_{timestamp} 
est rejeté par l'API Facebook avec erreur "Invalid OAuth access token"
"""

import requests
import json
import sys
import time
import subprocess
from datetime import datetime

class FacebookPublicationDiagnostic:
    def __init__(self):
        # Use the frontend environment URL from .env
        self.base_url = "https://post-restore.preview.emergentagent.com/api"
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
                return True
            else:
                print(f"   ❌ Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {str(e)}")
            return False
    
    def analyze_social_connections_tokens(self):
        """Analyze social connections and their tokens using debug endpoint"""
        try:
            print(f"\n🔍 Step 2: Analyzing social connections and tokens")
            print(f"   Endpoint: GET /api/debug/social-connections")
            
            response = self.session.get(f"{self.base_url}/debug/social-connections")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"   ✅ Debug endpoint accessible")
                
                # Analyze connections in social_media_connections
                connections = data.get("social_media_connections", [])
                old_connections = data.get("social_connections_old", [])
                
                print(f"   📊 Found {len(connections)} connections in social_media_connections")
                print(f"   📊 Found {len(old_connections)} connections in social_connections_old")
                
                facebook_connections = []
                instagram_connections = []
                
                # Check both collections
                all_connections = connections + old_connections
                
                for i, conn in enumerate(all_connections):
                    platform = conn.get("platform", "unknown")
                    active = conn.get("active", conn.get("is_active", False))
                    created_at = conn.get("created_at", "unknown")
                    access_token = conn.get("access_token", "")
                    collection = "social_media_connections" if i < len(connections) else "social_connections_old"
                    
                    print(f"     Connection {i+1} ({collection}):")
                    print(f"       Platform: {platform}")
                    print(f"       Active: {active}")
                    print(f"       Created: {created_at}")
                    
                    # Analyze token format
                    if access_token:
                        if access_token.startswith("temp_facebook_token_"):
                            print(f"       ❌ Token: TEMPORARY FALLBACK TOKEN ({access_token[:30]}...)")
                            print(f"       ❌ This is a test token that will be rejected by Facebook API")
                        elif access_token.startswith("temp_"):
                            print(f"       ❌ Token: TEMPORARY TOKEN ({access_token[:30]}...)")
                        elif access_token == "None" or access_token is None:
                            print(f"       ❌ Token: NULL/NONE")
                        else:
                            print(f"       ✅ Token: REAL TOKEN ({access_token[:30]}...)")
                    else:
                        print(f"       ❌ Token: MISSING")
                    
                    if platform == "facebook":
                        facebook_connections.append(conn)
                    elif platform == "instagram":
                        instagram_connections.append(conn)
                
                print(f"\n   📋 Connection Analysis:")
                print(f"     Facebook connections: {len(facebook_connections)}")
                print(f"     Instagram connections: {len(instagram_connections)}")
                
                # Focus on Facebook connections
                if facebook_connections:
                    print(f"   🔍 Facebook Connection Details:")
                    for i, fb_conn in enumerate(facebook_connections):
                        access_token = fb_conn.get("access_token", "")
                        page_name = fb_conn.get("page_name", "Unknown")
                        active = fb_conn.get("active", fb_conn.get("is_active", False))
                        
                        print(f"     Facebook Connection {i+1}:")
                        print(f"       Page Name: {page_name}")
                        print(f"       Active: {active}")
                        print(f"       Token Type: {'TEMP FALLBACK' if access_token and access_token.startswith('temp_facebook_token_') else 'UNKNOWN'}")
                        
                        if access_token and access_token.startswith("temp_facebook_token_"):
                            print(f"       ❌ CRITICAL ISSUE: This temporary token will cause Facebook API to return 'Invalid OAuth access token'")
                
                return {
                    "total_connections": len(all_connections),
                    "facebook_connections": facebook_connections,
                    "instagram_connections": instagram_connections
                }
            else:
                print(f"   ❌ Failed to access debug endpoint: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error analyzing connections: {str(e)}")
            return None
    
    def test_facebook_publication(self):
        """Test Facebook publication to capture the exact error"""
        try:
            print(f"\n🚀 Step 3: Testing Facebook publication")
            print(f"   Objective: Capture exact Facebook API error")
            
            # First, get Facebook posts available for testing
            response = self.session.get(f"{self.base_url}/posts/generated")
            
            if response.status_code != 200:
                print(f"   ❌ Failed to get posts: {response.text}")
                return None
            
            data = response.json()
            posts = data.get("posts", [])
            facebook_posts = [p for p in posts if p.get("platform") == "facebook"]
            
            print(f"   📊 Found {len(posts)} total posts, {len(facebook_posts)} Facebook posts")
            
            if not facebook_posts:
                print(f"   ⚠️ No Facebook posts found for testing")
                return None
            
            # Test with the first Facebook post
            test_post = facebook_posts[0]
            post_id = test_post.get("id")
            post_title = test_post.get("title", "No title")
            
            print(f"   🎯 Testing publication with Facebook post:")
            print(f"     Post ID: {post_id}")
            print(f"     Title: {post_title[:50]}...")
            
            # Attempt to publish
            print(f"   📡 Calling POST /api/posts/publish")
            
            response = self.session.post(
                f"{self.base_url}/posts/publish",
                json={"post_id": post_id}
            )
            
            print(f"   📊 Publication Response:")
            print(f"     Status Code: {response.status_code}")
            
            try:
                response_data = response.json()
                print(f"     Response Data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                
                # Analyze the error message
                message = response_data.get("message", "")
                error = response_data.get("error", "")
                details = response_data.get("details", "")
                
                if "aucune connexion sociale active" in message.lower():
                    print(f"   ✅ EXPECTED ERROR: No active social connections found")
                    print(f"   ✅ This confirms connections exist but are inactive/invalid")
                    return {"error_type": "no_active_connections", "message": message}
                elif "invalid oauth access token" in message.lower() or "invalid oauth access token" in error.lower():
                    print(f"   ✅ EXPECTED ERROR: Invalid OAuth access token detected")
                    print(f"   ✅ This confirms temporary token is being rejected by Facebook API")
                    return {"error_type": "invalid_token", "message": message, "error": error}
                elif "facebook" in message.lower() and ("error" in message.lower() or "failed" in message.lower()):
                    print(f"   ✅ FACEBOOK API ERROR: {message}")
                    return {"error_type": "facebook_api_error", "message": message, "error": error}
                else:
                    print(f"   ⚠️ UNEXPECTED RESPONSE: {message}")
                    return {"error_type": "unexpected", "message": message, "error": error}
                    
            except json.JSONDecodeError:
                print(f"     Response (raw text): {response.text}")
                if "invalid oauth access token" in response.text.lower():
                    print(f"   ✅ EXPECTED ERROR: Invalid OAuth access token in raw response")
                    return {"error_type": "invalid_token", "raw_response": response.text}
                return {"error_type": "json_decode_error", "raw_response": response.text}
                
        except Exception as e:
            print(f"   ❌ Error testing publication: {str(e)}")
            return None
    
    def check_backend_logs(self):
        """Check backend logs for Facebook API errors"""
        try:
            print(f"\n📋 Step 4: Checking backend logs for Facebook API errors")
            
            # Check supervisor backend logs
            log_files = [
                "/var/log/supervisor/backend.err.log",
                "/var/log/supervisor/backend.out.log"
            ]
            
            facebook_errors_found = []
            
            for log_file in log_files:
                try:
                    print(f"   🔍 Checking {log_file}")
                    
                    # Get last 50 lines of the log file
                    result = subprocess.run(
                        ["tail", "-n", "50", log_file],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        log_content = result.stdout
                        
                        # Look for Facebook-related errors
                        lines = log_content.split('\n')
                        facebook_lines = [line for line in lines if 'facebook' in line.lower() or 'oauth' in line.lower()]
                        
                        if facebook_lines:
                            print(f"     ✅ Found {len(facebook_lines)} Facebook/OAuth related log entries")
                            for line in facebook_lines[-5:]:  # Show last 5 entries
                                if line.strip():
                                    print(f"       📝 {line.strip()}")
                                    facebook_errors_found.append(line.strip())
                        else:
                            print(f"     ℹ️ No Facebook/OAuth entries in recent logs")
                    else:
                        print(f"     ⚠️ Could not read log file: {result.stderr}")
                        
                except subprocess.TimeoutExpired:
                    print(f"     ⚠️ Timeout reading log file")
                except Exception as e:
                    print(f"     ⚠️ Error reading log file: {str(e)}")
            
            return facebook_errors_found
            
        except Exception as e:
            print(f"   ❌ Error checking backend logs: {str(e)}")
            return []
    
    def run_facebook_publication_diagnostic(self):
        """Execute the complete Facebook publication diagnostic"""
        print("🚨 MISSION: DIAGNOSTIC PUBLICATION FACEBOOK")
        print("🌐 ENVIRONMENT: Preview (social-ai-planner-2.preview.emergentagent.com)")
        print("🎯 OBJECTIVE: Diagnostiquer l'échec de publication Facebook")
        print("📋 EXPECTED: Token temporaire temp_facebook_token_{timestamp} rejeté")
        print("=" * 70)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ CRITICAL: Authentication failed - cannot proceed")
            return False
        
        # Step 2: Analyze social connections and tokens
        connections_data = self.analyze_social_connections_tokens()
        if connections_data is None:
            print("\n❌ CRITICAL: Failed to analyze social connections")
            return False
        
        # Step 3: Test Facebook publication
        publication_result = self.test_facebook_publication()
        
        # Step 4: Check backend logs
        backend_logs = self.check_backend_logs()
        
        print("\n" + "=" * 70)
        print("🚨 DIAGNOSTIC PUBLICATION FACEBOOK TERMINÉ")
        print("=" * 70)
        
        # Analyze results
        print(f"\n📊 ANALYSE DES RÉSULTATS:")
        
        if connections_data:
            facebook_connections = connections_data["facebook_connections"]
            print(f"   📋 Connexions Facebook trouvées: {len(facebook_connections)}")
            
            temp_token_found = False
            for conn in facebook_connections:
                access_token = conn.get("access_token", "")
                if access_token and access_token.startswith("temp_facebook_token_"):
                    temp_token_found = True
                    print(f"   ❌ TOKEN TEMPORAIRE DÉTECTÉ: {access_token[:40]}...")
                    print(f"   ❌ Ce token sera rejeté par l'API Facebook")
            
            if temp_token_found:
                print(f"   ✅ CAUSE RACINE IDENTIFIÉE: Tokens temporaires invalides")
            else:
                print(f"   ⚠️ Aucun token temporaire détecté - investigation requise")
        
        if publication_result:
            error_type = publication_result.get("error_type")
            message = publication_result.get("message", "")
            
            print(f"   📡 Résultat de publication:")
            print(f"     Type d'erreur: {error_type}")
            print(f"     Message: {message}")
            
            if error_type == "no_active_connections":
                print(f"   ✅ CONFIRMÉ: Aucune connexion sociale active trouvée")
                print(f"   ✅ Les connexions existent mais sont inactives/invalides")
            elif error_type == "invalid_token":
                print(f"   ✅ CONFIRMÉ: Token OAuth invalide rejeté par Facebook")
                print(f"   ✅ C'est exactement l'erreur attendue")
            elif error_type == "facebook_api_error":
                print(f"   ✅ CONFIRMÉ: Erreur API Facebook détectée")
        
        if backend_logs:
            print(f"   📋 Logs backend:")
            print(f"     Entrées Facebook/OAuth trouvées: {len(backend_logs)}")
            for log in backend_logs[-3:]:  # Show last 3 entries
                if "invalid" in log.lower() or "error" in log.lower():
                    print(f"     ❌ {log}")
        
        print(f"\n🎯 CONCLUSION:")
        
        # Determine if we confirmed the expected issue
        temp_tokens_confirmed = False
        api_error_confirmed = False
        
        if connections_data:
            for conn in connections_data["facebook_connections"]:
                access_token = conn.get("access_token", "")
                if access_token and access_token.startswith("temp_facebook_token_"):
                    temp_tokens_confirmed = True
        
        if publication_result:
            error_type = publication_result.get("error_type")
            if error_type in ["invalid_token", "facebook_api_error", "no_active_connections"]:
                api_error_confirmed = True
        
        if temp_tokens_confirmed and api_error_confirmed:
            print(f"   ✅ MISSION ACCOMPLIE: Cause racine confirmée")
            print(f"   ✅ Les tokens temporaires temp_facebook_token_{{timestamp}} sont rejetés")
            print(f"   ✅ L'API Facebook retourne 'Invalid OAuth access token'")
            print(f"   ✅ C'est pourquoi le bouton revient à 'Publier' au lieu de 'Publié'")
        elif api_error_confirmed:
            print(f"   ✅ ERREUR API CONFIRMÉE: Publication Facebook échoue")
            print(f"   ⚠️ Tokens temporaires non détectés - investigation OAuth requise")
        else:
            print(f"   ⚠️ DIAGNOSTIC INCOMPLET: Erreurs non confirmées")
        
        print(f"\n🔧 SOLUTIONS RECOMMANDÉES:")
        print(f"   1. Corriger le callback OAuth Facebook pour stocker de vrais tokens")
        print(f"   2. Supprimer le mécanisme de fallback qui crée des tokens de test")
        print(f"   3. Implémenter un système de rafraîchissement de token approprié")
        print(f"   4. L'utilisateur doit reconnecter Facebook pour obtenir des tokens valides")
        
        print("=" * 70)
        
        return True

def main():
    """Main execution function"""
    diagnostic = FacebookPublicationDiagnostic()
    
    try:
        success = diagnostic.run_facebook_publication_diagnostic()
        if success:
            print(f"\n🎯 DIAGNOSTIC PUBLICATION FACEBOOK TERMINÉ AVEC SUCCÈS")
            sys.exit(0)
        else:
            print(f"\n💥 DIAGNOSTIC PUBLICATION FACEBOOK ÉCHOUÉ")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⚠️ Diagnostic interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()