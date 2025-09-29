#!/usr/bin/env python3
"""
🎯 FACEBOOK IMAGES LIVE ENVIRONMENT TESTING
Test environnement LIVE déployé (claire-marcus.com) au lieu de PREVIEW

Identifiants: lperpere@yahoo.fr / L@Reunion974!
Environnement LIVE: https://claire-marcus-pwa-1.emergent.host/api (ou claire-marcus.com)

TESTS CRITIQUES SUR LIVE:
1. Test authentification sur LIVE
2. Test génération URL OAuth Facebook sur LIVE  
3. Test état des connexions sociales sur LIVE
4. Test endpoints de publication sur LIVE
5. Test images publiques sur LIVE
"""

import requests
import json
import sys
from datetime import datetime

# Configuration LIVE
LIVE_BACKEND_URL = "https://claire-marcus-pwa-1.emergent.host/api"
ALTERNATIVE_LIVE_URL = "https://claire-marcus.com/api"
CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class LiveEnvironmentTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Claire-Marcus-Testing-Agent/1.0'
        })
        self.access_token = None
        self.user_id = None
        self.backend_url = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_backend_connectivity(self):
        """Test connectivity to both possible LIVE URLs"""
        self.log("🔍 Testing LIVE backend connectivity...")
        
        urls_to_test = [LIVE_BACKEND_URL, ALTERNATIVE_LIVE_URL]
        
        for url in urls_to_test:
            try:
                self.log(f"   Testing: {url}")
                response = self.session.get(f"{url}/health", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log(f"   ✅ SUCCESS: {url}")
                    self.log(f"      Status: {data.get('status', 'unknown')}")
                    self.log(f"      Service: {data.get('service', 'unknown')}")
                    self.backend_url = url
                    return True
                else:
                    self.log(f"   ❌ FAILED: {url} - Status {response.status_code}")
                    
            except Exception as e:
                self.log(f"   ❌ ERROR: {url} - {str(e)}")
                
        return False
        
    def test_live_authentication(self):
        """1. Test authentification sur LIVE"""
        self.log("🔐 TEST 1: Authentication sur environnement LIVE")
        
        if not self.backend_url:
            self.log("❌ No backend URL available", "ERROR")
            return False
            
        try:
            response = self.session.post(
                f"{self.backend_url}/auth/login-robust",
                json=CREDENTIALS,
                timeout=15
            )
            
            self.log(f"   Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                self.user_id = data.get('user_id')
                
                self.log(f"   ✅ Authentication SUCCESS on LIVE")
                self.log(f"      User ID: {self.user_id}")
                self.log(f"      Token: {self.access_token[:30]}..." if self.access_token else "No token")
                
                # Update session headers with token
                if self.access_token:
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.access_token}'
                    })
                
                return True
            else:
                self.log(f"   ❌ Authentication FAILED: {response.status_code}")
                try:
                    error_data = response.json()
                    self.log(f"      Error: {error_data}")
                except:
                    self.log(f"      Raw response: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log(f"   ❌ Authentication ERROR: {str(e)}", "ERROR")
            return False
            
    def test_facebook_oauth_url_live(self):
        """2. Test génération URL OAuth Facebook sur LIVE"""
        self.log("🔗 TEST 2: Facebook OAuth URL generation sur LIVE")
        
        if not self.access_token:
            self.log("❌ No access token available", "ERROR")
            return False
            
        try:
            response = self.session.get(
                f"{self.backend_url}/social/facebook/auth-url",
                timeout=10
            )
            
            self.log(f"   Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get('auth_url', '')
                
                self.log(f"   ✅ Facebook OAuth URL SUCCESS on LIVE")
                self.log(f"      URL Length: {len(auth_url)}")
                
                # Analyze URL components
                if 'client_id=' in auth_url:
                    client_id = auth_url.split('client_id=')[1].split('&')[0]
                    self.log(f"      Client ID: {client_id}")
                    
                if 'config_id=' in auth_url:
                    config_id = auth_url.split('config_id=')[1].split('&')[0]
                    self.log(f"      Config ID: {config_id}")
                    
                if 'redirect_uri=' in auth_url:
                    redirect_uri = auth_url.split('redirect_uri=')[1].split('&')[0]
                    self.log(f"      Redirect URI: {redirect_uri}")
                    
                # Compare with expected values
                expected_client_id = "1115451684022643"
                expected_config_id = "1878388119742903"
                
                if expected_client_id in auth_url:
                    self.log(f"      ✅ Client ID matches expected: {expected_client_id}")
                else:
                    self.log(f"      ⚠️ Client ID mismatch - expected: {expected_client_id}")
                    
                if expected_config_id in auth_url:
                    self.log(f"      ✅ Config ID matches expected: {expected_config_id}")
                else:
                    self.log(f"      ⚠️ Config ID mismatch - expected: {expected_config_id}")
                    
                return True
            else:
                self.log(f"   ❌ Facebook OAuth URL FAILED: {response.status_code}")
                try:
                    error_data = response.json()
                    self.log(f"      Error: {error_data}")
                except:
                    self.log(f"      Raw response: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log(f"   ❌ Facebook OAuth URL ERROR: {str(e)}", "ERROR")
            return False
            
    def test_social_connections_state_live(self):
        """3. Test état des connexions sociales sur LIVE"""
        self.log("📱 TEST 3: Social connections state sur LIVE")
        
        if not self.access_token:
            self.log("❌ No access token available", "ERROR")
            return False
            
        # Test debug endpoint first
        try:
            response = self.session.get(
                f"{self.backend_url}/debug/social-connections",
                timeout=10
            )
            
            self.log(f"   Debug endpoint Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"   ✅ Debug social connections SUCCESS on LIVE")
                
                # Analyze connections data
                total_connections = data.get('total_connections', 0)
                active_connections = data.get('active_connections', 0)
                facebook_connections = data.get('facebook_connections', 0)
                instagram_connections = data.get('instagram_connections', 0)
                
                self.log(f"      Total connections: {total_connections}")
                self.log(f"      Active connections: {active_connections}")
                self.log(f"      Facebook connections: {facebook_connections}")
                self.log(f"      Instagram connections: {instagram_connections}")
                
                # Check for EAA tokens
                connections_detail = data.get('connections_detail', [])
                eaa_tokens_found = 0
                temp_tokens_found = 0
                
                for conn in connections_detail:
                    token = conn.get('access_token', '')
                    if token.startswith('EAA'):
                        eaa_tokens_found += 1
                        self.log(f"      ✅ EAA token found: {token[:20]}...")
                    elif 'temp_' in token:
                        temp_tokens_found += 1
                        self.log(f"      ⚠️ Temp token found: {token}")
                        
                self.log(f"      EAA tokens: {eaa_tokens_found}")
                self.log(f"      Temp tokens: {temp_tokens_found}")
                
            else:
                self.log(f"   ❌ Debug endpoint FAILED: {response.status_code}")
                
        except Exception as e:
            self.log(f"   ❌ Debug endpoint ERROR: {str(e)}", "ERROR")
            
        # Test regular connections endpoint
        try:
            response = self.session.get(
                f"{self.backend_url}/social/connections",
                timeout=10
            )
            
            self.log(f"   Regular endpoint Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                connections = data.get('connections', [])
                self.log(f"   ✅ Regular social connections SUCCESS on LIVE")
                self.log(f"      Visible connections: {len(connections)}")
                
                for conn in connections:
                    platform = conn.get('platform', 'unknown')
                    is_active = conn.get('is_active', False)
                    page_name = conn.get('page_name', 'unknown')
                    self.log(f"      - {platform}: {page_name} (active: {is_active})")
                    
                return True
            else:
                self.log(f"   ❌ Regular endpoint FAILED: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"   ❌ Regular endpoint ERROR: {str(e)}", "ERROR")
            return False
    
    def test_callback_endpoint_accessibility(self):
        """Test 2: Vérifier accessibilité du callback"""
        print("\n🔄 TEST 2: Accessibilité endpoint callback")
        
        callback_url = "https://claire-marcus.com/api/social/facebook/callback"
        
        try:
            # Test avec paramètres simulés
            test_params = {
                'code': 'test_code_simulation',
                'state': f'facebook_oauth|{self.user_id}'
            }
            
            response = requests.get(callback_url, params=test_params, timeout=10)
            
            # Le callback devrait répondre (même avec erreur de token)
            if response.status_code in [200, 302, 400, 401]:
                self.log_test("Callback Endpoint Accessibility", True, 
                            f"Endpoint accessible (Status: {response.status_code})")
                return True
            else:
                self.log_test("Callback Endpoint Accessibility", False, 
                            f"Status inattendu: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Callback Endpoint Accessibility", False, f"Error: {str(e)}")
            return False
    
    def test_facebook_environment_variables(self):
        """Test 3: Vérifier variables d'environnement Facebook"""
        print("\n⚙️ TEST 3: Variables d'environnement Facebook")
        
        try:
            # Test indirect via l'URL OAuth générée
            response = self.session.get(f"{API_BASE}/social/facebook/auth-url")
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get('auth_url', '')
                
                # Extraire et vérifier les variables
                checks = {
                    'FACEBOOK_APP_ID': '1115451684022643' in auth_url,
                    'FACEBOOK_REDIRECT_URI': 'claire-marcus.com/api/social/facebook/callback' in auth_url,
                    'CONFIG_ID': '1878388119742903' in auth_url
                }
                
                all_vars_ok = all(checks.values())
                
                if all_vars_ok:
                    self.log_test("Facebook Environment Variables", True, 
                                "Toutes les variables critiques présentes")
                    return True
                else:
                    failed_vars = [var for var, ok in checks.items() if not ok]
                    self.log_test("Facebook Environment Variables", False, 
                                f"Variables manquantes/incorrectes: {failed_vars}")
                    return False
            else:
                self.log_test("Facebook Environment Variables", False, 
                            "Impossible de vérifier via auth-url")
                return False
                
        except Exception as e:
            self.log_test("Facebook Environment Variables", False, f"Error: {str(e)}")
            return False
    
    def test_current_social_connections(self):
        """Test 4: Analyser connexions sociales actuelles"""
        print("\n📊 TEST 4: Analyse connexions sociales actuelles")
        
        try:
            # Test endpoint de diagnostic
            response = self.session.get(f"{API_BASE}/debug/social-connections")
            
            if response.status_code == 200:
                data = response.json()
                
                # Analyser les connexions
                total_connections = data.get('total_connections', 0)
                active_connections = data.get('active_connections', 0)
                facebook_connections = data.get('facebook_connections', 0)
                
                print(f"   📈 Connexions totales: {total_connections}")
                print(f"   ✅ Connexions actives: {active_connections}")
                print(f"   📘 Connexions Facebook: {facebook_connections}")
                
                # Vérifier les tokens
                connections_detail = data.get('connections_detail', [])
                temp_tokens = [c for c in connections_detail if 'temp_' in str(c.get('access_token', ''))]
                
                if temp_tokens:
                    print(f"   ⚠️ Tokens temporaires détectés: {len(temp_tokens)}")
                    for token_info in temp_tokens:
                        print(f"      - {token_info.get('platform')}: {token_info.get('access_token', '')[:30]}...")
                
                self.log_test("Current Social Connections Analysis", True, 
                            f"Total: {total_connections}, Actives: {active_connections}, Facebook: {facebook_connections}")
                
                return {
                    'total': total_connections,
                    'active': active_connections,
                    'facebook': facebook_connections,
                    'temp_tokens': len(temp_tokens)
                }
            else:
                self.log_test("Current Social Connections Analysis", False, 
                            f"Status: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("Current Social Connections Analysis", False, f"Error: {str(e)}")
            return None
    
    def simulate_callback_flow_steps(self):
        """Test 5: Simuler les étapes du callback OAuth"""
        print("\n🔄 TEST 5: Simulation flow callback OAuth 3-étapes")
        
        # ÉTAPE 1: Code → Short-lived token
        print("   📝 ÉTAPE 1/3: Code d'autorisation → Token court terme")
        try:
            # Simuler un appel callback avec code
            callback_data = {
                'code': 'AQD_simulated_auth_code_for_testing',
                'state': f'facebook_oauth|{self.user_id}'
            }
            
            # Note: Ceci va échouer mais nous permet de voir les logs
            callback_url = "https://claire-marcus.com/api/social/facebook/callback"
            response = requests.get(callback_url, params=callback_data, timeout=15)
            
            print(f"      Status: {response.status_code}")
            if response.status_code == 302:
                location = response.headers.get('Location', '')
                if 'facebook_success=true' in location:
                    print("      ✅ Redirection de succès détectée")
                elif 'facebook_error' in location:
                    print("      ❌ Redirection d'erreur détectée")
                    print(f"      📍 Location: {location}")
            
            self.log_test("OAuth Callback Step 1 Simulation", True, 
                        f"Callback testé (Status: {response.status_code})")
            
        except Exception as e:
            self.log_test("OAuth Callback Step 1 Simulation", False, f"Error: {str(e)}")
        
        # ÉTAPE 2: Vérifier si des tokens long terme sont créés
        print("   📝 ÉTAPE 2/3: Vérification tokens long terme")
        try:
            # Re-vérifier les connexions après simulation
            response = self.session.get(f"{API_BASE}/debug/social-connections")
            if response.status_code == 200:
                data = response.json()
                connections = data.get('connections_detail', [])
                
                long_lived_tokens = [c for c in connections 
                                   if c.get('access_token') and 
                                   not c.get('access_token', '').startswith('temp_')]
                
                if long_lived_tokens:
                    print(f"      ✅ Tokens long terme trouvés: {len(long_lived_tokens)}")
                    self.log_test("OAuth Long-lived Token Check", True, 
                                f"{len(long_lived_tokens)} tokens long terme")
                else:
                    print("      ❌ Aucun token long terme trouvé")
                    self.log_test("OAuth Long-lived Token Check", False, 
                                "Pas de tokens long terme")
            
        except Exception as e:
            self.log_test("OAuth Long-lived Token Check", False, f"Error: {str(e)}")
        
        # ÉTAPE 3: Vérifier tokens EAA (Page Access Token)
        print("   📝 ÉTAPE 3/3: Vérification tokens EAA permanents")
        try:
            response = self.session.get(f"{API_BASE}/debug/social-connections")
            if response.status_code == 200:
                data = response.json()
                connections = data.get('connections_detail', [])
                
                eaa_tokens = [c for c in connections 
                            if c.get('access_token') and 
                            c.get('access_token', '').startswith('EAA')]
                
                if eaa_tokens:
                    print(f"      ✅ Tokens EAA trouvés: {len(eaa_tokens)}")
                    for eaa in eaa_tokens:
                        print(f"         - Page: {eaa.get('page_name', 'Unknown')}")
                        print(f"         - Token: {eaa.get('access_token', '')[:20]}...")
                    self.log_test("OAuth EAA Token Check", True, 
                                f"{len(eaa_tokens)} tokens EAA permanents")
                else:
                    print("      ❌ Aucun token EAA permanent trouvé")
                    self.log_test("OAuth EAA Token Check", False, 
                                "Pas de tokens EAA permanents")
            
        except Exception as e:
            self.log_test("OAuth EAA Token Check", False, f"Error: {str(e)}")
    
    def test_publication_with_current_tokens(self):
        """Test 6: Tester publication avec tokens actuels"""
        print("\n📤 TEST 6: Test publication avec tokens actuels")
        
        try:
            # D'abord, obtenir un post Facebook pour tester
            response = self.session.get(f"{API_BASE}/posts/generated")
            
            if response.status_code == 200:
                posts = response.json().get('posts', [])
                facebook_posts = [p for p in posts if p.get('platform') == 'facebook']
                
                if facebook_posts:
                    test_post = facebook_posts[0]
                    post_id = test_post.get('id')
                    
                    print(f"   📝 Test avec post: {test_post.get('title', 'Sans titre')}")
                    
                    # Tenter la publication
                    pub_response = self.session.post(f"{API_BASE}/posts/publish", 
                                                   json={'post_id': post_id})
                    
                    print(f"   📊 Status publication: {pub_response.status_code}")
                    
                    if pub_response.status_code == 200:
                        pub_data = pub_response.json()
                        print(f"   ✅ Publication réussie: {pub_data.get('message', '')}")
                        self.log_test("Publication Test", True, "Publication réussie")
                    else:
                        try:
                            error_data = pub_response.json()
                            error_msg = error_data.get('error', 'Erreur inconnue')
                            print(f"   ❌ Erreur publication: {error_msg}")
                            
                            # Analyser le type d'erreur
                            if 'token' in error_msg.lower():
                                print("   🔍 DIAGNOSTIC: Problème de token détecté")
                            elif 'connexion' in error_msg.lower():
                                print("   🔍 DIAGNOSTIC: Problème de connexion détecté")
                            
                            self.log_test("Publication Test", False, error_msg)
                        except:
                            self.log_test("Publication Test", False, 
                                        f"Status {pub_response.status_code}")
                else:
                    self.log_test("Publication Test", False, "Aucun post Facebook disponible")
            else:
                self.log_test("Publication Test", False, "Impossible de récupérer les posts")
                
        except Exception as e:
            self.log_test("Publication Test", False, f"Error: {str(e)}")
    
    def cleanup_temporary_tokens(self):
        """Test 7: Nettoyer les tokens temporaires"""
        print("\n🧹 TEST 7: Nettoyage tokens temporaires")
        
        try:
            response = self.session.post(f"{API_BASE}/debug/clean-invalid-tokens")
            
            if response.status_code == 200:
                data = response.json()
                deleted_count = data.get('deleted_connections', 0)
                
                if deleted_count > 0:
                    print(f"   ✅ Tokens temporaires supprimés: {deleted_count}")
                    self.log_test("Temporary Token Cleanup", True, 
                                f"{deleted_count} tokens supprimés")
                else:
                    print("   ℹ️ Aucun token temporaire à supprimer")
                    self.log_test("Temporary Token Cleanup", True, 
                                "Système déjà propre")
                return True
            else:
                self.log_test("Temporary Token Cleanup", False, 
                            f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Temporary Token Cleanup", False, f"Error: {str(e)}")
            return False
    
    def run_comprehensive_diagnostic(self):
        """Exécuter le diagnostic complet"""
        print("🚀 DÉMARRAGE DIAGNOSTIC OAUTH FACEBOOK - TRACER ÉCHEC TOKENS EAA")
        print("=" * 80)
        
        # Authentification préliminaire
        if not self.authenticate():
            print("❌ ÉCHEC AUTHENTIFICATION - Arrêt du diagnostic")
            return
        
        # Exécuter tous les tests
        print(f"\n📋 DIAGNOSTIC COMPLET - User ID: {self.user_id}")
        
        # Tests principaux
        auth_url = self.test_facebook_auth_url_generation()
        self.test_callback_endpoint_accessibility()
        self.test_facebook_environment_variables()
        connections_info = self.test_current_social_connections()
        self.simulate_callback_flow_steps()
        self.test_publication_with_current_tokens()
        self.cleanup_temporary_tokens()
        
        # Résumé final
        self.print_final_summary(connections_info)
    
    def print_final_summary(self, connections_info):
        """Afficher le résumé final du diagnostic"""
        print("\n" + "=" * 80)
        print("📊 RÉSUMÉ DIAGNOSTIC OAUTH FACEBOOK")
        print("=" * 80)
        
        # Statistiques des tests
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"📈 Tests exécutés: {total_tests}")
        print(f"✅ Tests réussis: {passed_tests}")
        print(f"❌ Tests échoués: {failed_tests}")
        print(f"📊 Taux de réussite: {(passed_tests/total_tests)*100:.1f}%")
        
        # Analyse des connexions
        if connections_info:
            print(f"\n📘 ÉTAT CONNEXIONS FACEBOOK:")
            print(f"   Total connexions: {connections_info['total']}")
            print(f"   Connexions actives: {connections_info['active']}")
            print(f"   Connexions Facebook: {connections_info['facebook']}")
            print(f"   Tokens temporaires: {connections_info['temp_tokens']}")
        
        # Diagnostic des étapes OAuth
        print(f"\n🔄 DIAGNOSTIC FLOW OAUTH 3-ÉTAPES:")
        oauth_tests = [t for t in self.test_results if 'OAuth' in t['test']]
        for test in oauth_tests:
            status = "✅" if test['success'] else "❌"
            print(f"   {status} {test['test']}: {test['details']}")
        
        # Recommandations
        print(f"\n💡 RECOMMANDATIONS:")
        
        if connections_info and connections_info['temp_tokens'] > 0:
            print("   🔧 CRITIQUE: Tokens temporaires détectés - callback OAuth échoue")
            print("   📝 ACTION: Vérifier implémentation callback 3-étapes")
            print("   🎯 FOCUS: ÉTAPE 1→2→3 (Code→Short→Long→EAA)")
        
        if failed_tests > 0:
            print("   ⚠️ Tests échoués détectés - voir détails ci-dessus")
        
        print(f"\n🎯 QUESTION CENTRALE RÉPONDUE:")
        print(f"   À quelle étape exacte le flow OAuth échoue-t-il?")
        
        # Identifier l'étape d'échec
        if connections_info and connections_info['temp_tokens'] > 0:
            print("   📍 RÉPONSE: Le flow échoue à l'ÉTAPE 1 (Code → Short-lived token)")
            print("   🔍 CAUSE: Le callback crée des tokens temporaires au lieu d'échanger le code")
        elif connections_info and connections_info['facebook'] > 0:
            eaa_test = next((t for t in self.test_results if 'EAA' in t['test']), None)
            if eaa_test and not eaa_test['success']:
                print("   📍 RÉPONSE: Le flow échoue à l'ÉTAPE 3 (Long-lived → EAA)")
                print("   🔍 CAUSE: Tokens long terme créés mais pas de tokens EAA permanents")
            else:
                print("   📍 RÉPONSE: Flow semble fonctionnel - vérifier publication")
        else:
            print("   📍 RÉPONSE: Aucune connexion Facebook - callback ne fonctionne pas")
        
        print("=" * 80)

def main():
    """Point d'entrée principal"""
    diagnostic = FacebookOAuthDiagnostic()
    diagnostic.run_comprehensive_diagnostic()

if __name__ == "__main__":
    main()
