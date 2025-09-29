#!/usr/bin/env python3
"""
TRACER OAUTH FACEBOOK EN TEMPS RÉEL - IDENTIFIER ÉCHEC TOKENS EAA
Backend testing script for Facebook OAuth callback diagnostic

Objectif: Identifier exactement à quel moment échoue l'enregistrement des tokens EAA 
lors du flow OAuth Facebook avec surveillance en temps réel des logs.

Identifiants: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import time
import os
from datetime import datetime

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://social-publisher-10.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class FacebookOAuthDiagnostic:
    def __init__(self):
        self.session = requests.Session()
        self.user_id = None
        self.access_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = f"[{timestamp}] {status} {test_name}"
        if details:
            result += f" - {details}"
        print(result)
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': timestamp
        })
        
    def authenticate(self):
        """Step 1: Authenticate user"""
        print("\n🔐 ÉTAPE PRÉLIMINAIRE: Authentification utilisateur")
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login-robust", 
                json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                self.user_id = data.get('user_id')
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                self.log_test("Authentication", True, f"User ID: {self.user_id}")
                return True
            else:
                self.log_test("Authentication", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Error: {str(e)}")
            return False
    
    def test_facebook_auth_url_generation(self):
        """Test 1: Vérifier génération URL OAuth Facebook"""
        print("\n🔗 TEST 1: Génération URL OAuth Facebook")
        
        try:
            response = self.session.get(f"{API_BASE}/social/facebook/auth-url")
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get('auth_url', '')
                
                # Vérifier les paramètres critiques
                required_params = [
                    'client_id=1115451684022643',
                    'config_id=1878388119742903', 
                    'redirect_uri=https://claire-marcus.com/api/social/facebook/callback',
                    'response_type=code',
                    'scope=pages_show_list,pages_read_engagement,pages_manage_posts'
                ]
                
                all_params_present = all(param in auth_url for param in required_params)
                
                if all_params_present:
                    self.log_test("Facebook Auth URL Generation", True, 
                                f"URL correcte avec tous paramètres requis")
                    print(f"   📋 URL générée: {auth_url[:100]}...")
                    return auth_url
                else:
                    missing = [p for p in required_params if p not in auth_url]
                    self.log_test("Facebook Auth URL Generation", False, 
                                f"Paramètres manquants: {missing}")
                    return None
            else:
                self.log_test("Facebook Auth URL Generation", False, 
                            f"Status: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("Facebook Auth URL Generation", False, f"Error: {str(e)}")
            return None
    
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
        print("   🎯 Confirmer expires_at basé sur expires_in (60 jours)")
        print("   🎯 Vérifier que tokens ne sont plus temp_facebook_token_")
        
        if not connections_data:
            print("   ❌ Pas de données de connexions à analyser")
            return False
        
        try:
            valid_permanent_tokens = 0
            invalid_temp_tokens = 0
            long_lived_tokens = 0
            
            print(f"\n📋 ANALYSE STRUCTURE DES CONNEXIONS:")
            
            for collection_name in ["social_media_connections", "social_connections_old"]:
                connections = connections_data.get(collection_name, [])
                if not connections:
                    continue
                    
                print(f"\n   📂 Collection: {collection_name}")
                
                for i, conn in enumerate(connections):
                    platform = conn.get("platform", "")
                    access_token = conn.get("access_token", "")
                    token_type = conn.get("token_type", "")
                    expires_at = conn.get("expires_at", "")
                    expires_in = conn.get("expires_in", "")
                    is_active = conn.get("active", conn.get("is_active", False))
                    
                    print(f"\n      🔗 Connexion {i+1}:")
                    print(f"         Platform: {platform}")
                    print(f"         Actif: {is_active}")
                    print(f"         Token type: {token_type}")
                    
                    if access_token:
                        if access_token.startswith("EAA"):
                            valid_permanent_tokens += 1
                            print(f"         ✅ Token EAA: {access_token[:35]}...")
                            
                            # Analyser expires_at pour 60 jours
                            if expires_at:
                                try:
                                    # Parser la date d'expiration
                                    if isinstance(expires_at, str):
                                        # Essayer différents formats
                                        for fmt in ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"]:
                                            try:
                                                exp_date = datetime.strptime(expires_at, fmt)
                                                break
                                            except ValueError:
                                                continue
                                        else:
                                            print(f"         ⚠️ Format expires_at non reconnu: {expires_at}")
                                            continue
                                    else:
                                        exp_date = expires_at
                                    
                                    now = datetime.utcnow()
                                    days_until_expiry = (exp_date - now).days
                                    
                                    print(f"         📅 Expire dans: {days_until_expiry} jours")
                                    
                                    if 50 <= days_until_expiry <= 70:  # ~60 jours avec tolérance
                                        long_lived_tokens += 1
                                        print(f"         ✅ Token long-lived (60 jours) confirmé")
                                    elif days_until_expiry > 365:
                                        print(f"         🎉 Token permanent (>1 an) confirmé")
                                    else:
                                        print(f"         ⚠️ Token court-terme ({days_until_expiry} jours)")
                                        
                                except Exception as date_error:
                                    print(f"         ⚠️ Erreur parsing date: {date_error}")
                            
                            if expires_in:
                                print(f"         📊 Expires_in: {expires_in} secondes")
                                days_from_expires_in = int(expires_in) / (24 * 3600)
                                print(f"         📊 Soit: {days_from_expires_in:.1f} jours")
                                
                        elif access_token.startswith("temp_facebook_token_"):
                            invalid_temp_tokens += 1
                            print(f"         ❌ Token temporaire: {access_token[:50]}...")
                        else:
                            print(f"         🔍 Autre format: {access_token[:35]}...")
                    else:
                        print(f"         ❌ Pas de token d'accès")
            
            print(f"\n📊 RÉSULTATS TEST 3:")
            print(f"   ✅ Tokens EAA valides: {valid_permanent_tokens}")
            print(f"   📅 Tokens long-lived (60j): {long_lived_tokens}")
            print(f"   ❌ Tokens temporaires: {invalid_temp_tokens}")
            
            if valid_permanent_tokens > 0 and invalid_temp_tokens == 0:
                print(f"   🎉 SUCCÈS: Format tokens sauvegardés VALIDE")
                print(f"   ✅ Plus de temp_facebook_token_ détectés")
                return True
            else:
                print(f"   ❌ ÉCHEC: Tokens temporaires encore présents")
                return False
                
        except Exception as e:
            print(f"   ❌ Erreur test 3: {e}")
            return False
    
    def test_4_flow_publication_complet(self):
        """TEST 4: Test flow publication complet"""
        print("\n🔄 TEST 4: Test flow publication complet...")
        print("   🎯 Objectif: Tracer publication depuis /api/posts/publish")
        print("   🎯 Voir logs 'ÉTAPE X/3' si callback a été utilisé")
        print("   🎯 Capturer requête Facebook avec vrai token EAA")
        
        try:
            # Récupérer un post pour test
            posts_response = self.session.get(f"{BACKEND_URL}/posts/generated", timeout=30)
            
            if posts_response.status_code != 200:
                print(f"   ❌ Impossible de récupérer les posts")
                return False
            
            posts_data = posts_response.json()
            posts = posts_data.get("posts", [])
            
            if not posts:
                print(f"   ⚠️ Aucun post disponible")
                return False
            
            # Chercher post Facebook avec image
            test_post = None
            for post in posts:
                if post.get("platform") == "facebook":
                    test_post = post
                    break
            
            if not test_post:
                print(f"   ❌ Aucun post Facebook trouvé")
                return False
            
            post_id = test_post.get("id")
            has_image = bool(test_post.get("visual_url"))
            
            print(f"   📋 Test flow avec post: {post_id}")
            print(f"   📋 Contient image: {'Oui' if has_image else 'Non'}")
            print(f"   📋 Image URL: {test_post.get('visual_url', 'Aucune')}")
            
            # Tracer la requête de publication
            print(f"\n🔄 TRAÇAGE DU FLOW DE PUBLICATION:")
            start_time = time.time()
            
            pub_response = self.session.post(
                f"{BACKEND_URL}/posts/publish",
                json={"post_id": post_id},
                timeout=60
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"   ⏱️ Durée totale: {duration:.2f} secondes")
            print(f"   📊 Status: {pub_response.status_code}")
            
            if pub_response.status_code == 200:
                pub_data = pub_response.json()
                print(f"   🎉 FLOW COMPLET RÉUSSI!")
                print(f"   📋 Réponse: {json.dumps(pub_data, indent=2)}")
                
                # Chercher indices d'utilisation du callback
                response_str = str(pub_data).lower()
                if "callback" in response_str or "étape" in response_str:
                    print(f"   🔍 Indices de callback détectés dans la réponse")
                
                return True
                
            elif pub_response.status_code == 400:
                pub_data = pub_response.json()
                error_msg = pub_data.get("error", "")
                print(f"   📋 Erreur flow: {error_msg}")
                
                # Analyser le type d'erreur
                if "Invalid OAuth access token" in error_msg:
                    print(f"   🚨 Token OAuth rejeté par Facebook")
                    print(f"   📋 Tokens EAA peut-être pas vraiment permanents")
                elif "Aucune connexion sociale active" in error_msg:
                    print(f"   📋 Pas de connexion active trouvée")
                    print(f"   📋 Callback n'a peut-être pas sauvegardé les connexions")
                
                return False
            else:
                print(f"   ❌ Réponse inattendue: {pub_response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Erreur test 4: {e}")
            return False
    
    def test_5_verification_instagram_meme_token(self, connections_data):
        """TEST 5: Vérification Instagram avec même token"""
        print("\n📱 TEST 5: Vérification Instagram avec même token...")
        print("   🎯 Objectif: Si Instagram Business connecté")
        print("   🎯 Vérifier qu'Instagram utilise même page_access_token")
        print("   🎯 Tester publication Instagram avec token permanent")
        
        if not connections_data:
            print("   ❌ Pas de données de connexions")
            return False
        
        try:
            facebook_tokens = []
            instagram_tokens = []
            
            # Collecter tous les tokens Facebook et Instagram
            for collection_name in ["social_media_connections", "social_connections_old"]:
                connections = connections_data.get(collection_name, [])
                
                for conn in connections:
                    platform = conn.get("platform", "").lower()
                    access_token = conn.get("access_token", "")
                    token_type = conn.get("token_type", "")
                    is_active = conn.get("active", conn.get("is_active", False))
                    
                    if platform == "facebook" and access_token:
                        facebook_tokens.append({
                            "token": access_token,
                            "type": token_type,
                            "active": is_active,
                            "collection": collection_name
                        })
                    elif platform == "instagram" and access_token:
                        instagram_tokens.append({
                            "token": access_token,
                            "type": token_type,
                            "active": is_active,
                            "collection": collection_name
                        })
            
            print(f"   📊 Tokens Facebook trouvés: {len(facebook_tokens)}")
            print(f"   📊 Tokens Instagram trouvés: {len(instagram_tokens)}")
            
            if not facebook_tokens and not instagram_tokens:
                print(f"   ⚠️ Aucun token trouvé pour comparaison")
                return False
            
            # Vérifier si Instagram utilise le même token que Facebook
            shared_tokens = 0
            for fb_token in facebook_tokens:
                for ig_token in instagram_tokens:
                    if fb_token["token"] == ig_token["token"]:
                        shared_tokens += 1
                        print(f"   ✅ TOKEN PARTAGÉ TROUVÉ!")
                        print(f"      Token: {fb_token['token'][:35]}...")
                        print(f"      Type: {fb_token['type']}")
                        print(f"      Facebook actif: {fb_token['active']}")
                        print(f"      Instagram actif: {ig_token['active']}")
                        print(f"      ✅ Même page_access_token utilisé par les deux plateformes")
            
            if shared_tokens > 0:
                print(f"   🎉 SUCCÈS: Instagram utilise même page_access_token")
                
                # Tester publication Instagram si possible
                try:
                    posts_response = self.session.get(f"{BACKEND_URL}/posts/generated", timeout=30)
                    if posts_response.status_code == 200:
                        posts_data = posts_response.json()
                        posts = posts_data.get("posts", [])
                        
                        instagram_post = None
                        for post in posts:
                            if post.get("platform") == "instagram":
                                instagram_post = post
                                break
                        
                        if instagram_post:
                            print(f"   📱 Test publication Instagram avec token permanent...")
                            pub_response = self.session.post(
                                f"{BACKEND_URL}/posts/publish",
                                json={"post_id": instagram_post.get("id")},
                                timeout=60
                            )
                            
                            if pub_response.status_code == 200:
                                print(f"   ✅ Publication Instagram réussie avec token permanent!")
                            else:
                                print(f"   📋 Publication Instagram: {pub_response.status_code}")
                        
                except Exception as ig_test_error:
                    print(f"   ⚠️ Test publication Instagram échoué: {ig_test_error}")
                
                return True
            else:
                print(f"   📋 Instagram et Facebook utilisent des tokens différents")
                
                # Afficher détails pour analyse
                if facebook_tokens:
                    print(f"   📘 Tokens Facebook:")
                    for i, token in enumerate(facebook_tokens):
                        print(f"      {i+1}. {token['token'][:35]}... (type: {token['type']})")
                
                if instagram_tokens:
                    print(f"   📷 Tokens Instagram:")
                    for i, token in enumerate(instagram_tokens):
                        print(f"      {i+1}. {token['token'][:35]}... (type: {token['type']})")
                
                return False
                
        except Exception as e:
            print(f"   ❌ Erreur test 5: {e}")
            return False
    
    def run_comprehensive_chatgpt_token_flow_test(self):
        """Exécuter tous les tests du flow ChatGPT 3-étapes"""
        print("🚀 DÉBUT TEST FLOW TOKENS PERMANENTS CHATGPT")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Utilisateur: {TEST_CREDENTIALS['email']}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 80)
        
        results = {
            "authentication": False,
            "test_1_token_state": False,
            "test_2_publication": False,
            "test_3_token_validation": False,
            "test_4_publication_flow": False,
            "test_5_instagram_verification": False,
            "has_permanent_eaa_tokens": False,
            "connections_data": None
        }
        
        # ÉTAPE 1: Authentification
        if not self.authenticate():
            print("\n❌ CRITIQUE: Authentification échouée - impossible de continuer")
            return results
        results["authentication"] = True
        
        # TEST 1: Vérifier état tokens après reconnexion
        has_eaa_tokens, connections_data = self.test_1_verifier_etat_tokens_apres_reconnexion()
        results["test_1_token_state"] = True
        results["has_permanent_eaa_tokens"] = has_eaa_tokens
        results["connections_data"] = connections_data
        
        # TEST 2: Test publication avec tokens permanents
        pub_success = self.test_2_publication_avec_tokens_permanents()
        results["test_2_publication"] = pub_success
        
        # TEST 3: Validation format tokens sauvegardés
        if connections_data:
            token_validation = self.test_3_validation_format_tokens_sauvegardes(connections_data)
            results["test_3_token_validation"] = token_validation
        
        # TEST 4: Test flow publication complet
        flow_success = self.test_4_flow_publication_complet()
        results["test_4_publication_flow"] = flow_success
        
        # TEST 5: Vérification Instagram avec même token
        if connections_data:
            instagram_verification = self.test_5_verification_instagram_meme_token(connections_data)
            results["test_5_instagram_verification"] = instagram_verification
        
        # Générer le résumé final
        self.generate_chatgpt_flow_summary(results)
        
        return results
    
    def generate_chatgpt_flow_summary(self, results):
        """Générer le résumé final du test ChatGPT flow"""
        print("\n" + "=" * 80)
        print("🎯 RÉSUMÉ FINAL - TEST FLOW TOKENS PERMANENTS CHATGPT")
        print("=" * 80)
        
        total_tests = 5
        passed_tests = sum([
            results["test_1_token_state"],
            results["test_2_publication"],
            results["test_3_token_validation"],
            results["test_4_publication_flow"],
            results["test_5_instagram_verification"]
        ])
        
        print(f"📊 Résultats globaux: {passed_tests}/{total_tests} tests réussis")
        print(f"📊 Taux de réussite: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n📋 Détail des résultats:")
        print(f"   ✅ Authentification: {'RÉUSSI' if results['authentication'] else 'ÉCHOUÉ'}")
        print(f"   🔍 Test 1 - État tokens: {'RÉUSSI' if results['test_1_token_state'] else 'ÉCHOUÉ'}")
        print(f"   📝 Test 2 - Publication: {'RÉUSSI' if results['test_2_publication'] else 'ÉCHOUÉ'}")
        print(f"   🔍 Test 3 - Validation tokens: {'RÉUSSI' if results['test_3_token_validation'] else 'ÉCHOUÉ'}")
        print(f"   🔄 Test 4 - Flow publication: {'RÉUSSI' if results['test_4_publication_flow'] else 'ÉCHOUÉ'}")
        print(f"   📱 Test 5 - Instagram: {'RÉUSSI' if results['test_5_instagram_verification'] else 'ÉCHOUÉ'}")
        
        print(f"\n🎯 Conclusions clés:")
        if results["has_permanent_eaa_tokens"]:
            print(f"   ✅ TOKENS EAA PERMANENTS DÉTECTÉS")
            print(f"   🎉 Flow 3-étapes ChatGPT RÉUSSI")
            print(f"   📋 Tokens devraient fonctionner pour publication Facebook réelle")
        else:
            print(f"   ❌ AUCUN TOKEN EAA PERMANENT TROUVÉ")
            print(f"   ⚠️ Flow 3-étapes ChatGPT NON TERMINÉ")
            print(f"   📋 Utilisateur doit reconnecter Facebook pour tokens permanents")
        
        if results["test_2_publication"]:
            print(f"   ✅ Système de publication fonctionnel")
        else:
            print(f"   ❌ Système de publication a des problèmes")
        
        if results["test_5_instagram_verification"]:
            print(f"   ✅ Instagram partage le même page_access_token")
        else:
            print(f"   ⚠️ Instagram utilise un token différent ou n'est pas connecté")
        
        print(f"\n🔧 Recommandations:")
        if not results["has_permanent_eaa_tokens"]:
            print(f"   1. Utilisateur doit reconnecter le compte Facebook")
            print(f"   2. S'assurer que le flow OAuth 3-étapes se termine correctement")
            print(f"   3. Vérifier la configuration de l'URL de callback")
        
        if not results["test_2_publication"]:
            print(f"   1. Vérifier la validité des tokens OAuth")
            print(f"   2. Vérifier les permissions de l'API Facebook")
            print(f"   3. Tester avec des tokens EAA valides")
        
        print(f"\n🎯 HYPOTHÈSE TESTÉE:")
        if results["has_permanent_eaa_tokens"] and results["test_2_publication"]:
            print(f"   ✅ CONFIRMÉE: Avec vrais tokens permanents (EAA), Facebook accepte les publications avec images")
        elif results["has_permanent_eaa_tokens"] and not results["test_2_publication"]:
            print(f"   ⚠️ PARTIELLEMENT CONFIRMÉE: Tokens EAA présents mais publication échoue")
        else:
            print(f"   ❌ NON CONFIRMÉE: Pas de tokens EAA permanents détectés")
        
        print("=" * 80)

def main():
    """Fonction principale - Test Flow Tokens Permanents ChatGPT"""
    tester = ChatGPTTokenFlowTester()
    results = tester.run_comprehensive_chatgpt_token_flow_test()
    
    print(f"\n💾 Test terminé à {datetime.now().isoformat()}")
    
    # Sauvegarder les résultats
    try:
        with open("/app/chatgpt_token_flow_test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        print("📁 Résultats sauvegardés dans chatgpt_token_flow_test_results.json")
    except Exception as e:
        print(f"⚠️ Impossible de sauvegarder: {e}")
    
    # Code de sortie basé sur les résultats
    if results["has_permanent_eaa_tokens"] and results["test_2_publication"]:
        print("\n🎉 SUCCÈS: Flow ChatGPT 3-étapes fonctionne correctement!")
        sys.exit(0)
    else:
        print("\n⚠️ PROBLÈMES DÉTECTÉS: Flow ChatGPT 3-étapes nécessite attention")
        sys.exit(1)

if __name__ == "__main__":
    main()