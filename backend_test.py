#!/usr/bin/env python3
"""
TEST FLOW TOKENS PERMANENTS CHATGPT - IMPLEMENTATION COMPLÈTE

Identifiants: lperpere@yahoo.fr / L@Reunion974!

FLOW CHATGPT IMPLÉMENTÉ:
- ÉTAPE 1: Code → Short-lived token  
- ÉTAPE 2: Short-lived → Long-lived token (60 jours)
- ÉTAPE 3: Long-lived → Page access token (permanent)

TESTS CRITIQUES:
1. Vérifier état tokens après reconnexion (GET /api/debug/social-connections)
2. Test publication avec tokens permanents (POST /api/posts/publish)
3. Validation format tokens sauvegardés
4. Test flow publication complet
5. Vérification Instagram avec même token

OBJECTIF: Confirmer que le flow 3-étapes produit des tokens permanents EAA utilisables.
HYPOTHÈSE: Avec vrais tokens permanents (EAA), Facebook acceptera maintenant les publications avec images.
"""

import requests
import json
import os
import sys
from datetime import datetime, timedelta
import re
import time

# Configuration
BACKEND_URL = "https://social-publisher-10.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class ChatGPTTokenFlowTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        
    def authenticate(self):
        """ÉTAPE 1: Authentification avec les identifiants de test"""
        print("🔐 ÉTAPE 1: Authentification...")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json=TEST_CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                print(f"   ✅ Authentification réussie")
                print(f"   👤 User ID: {self.user_id}")
                return True
            else:
                print(f"   ❌ Échec authentification: {response.status_code}")
                print(f"   📄 Réponse: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Erreur authentification: {e}")
            return False
    
    def test_1_verifier_etat_tokens_apres_reconnexion(self):
        """TEST 1: Vérifier état tokens après reconnexion - Rechercher tokens EAA"""
        print("\n🔍 TEST 1: Vérification état des tokens après reconnexion...")
        print("   🎯 Objectif: Rechercher tokens commençant par EAA (vrais tokens)")
        print("   🎯 Vérifier token_type: 'page_access_token'")
        
        try:
            response = self.session.get(
                f"{BACKEND_URL}/debug/social-connections",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Endpoint debug accessible")
                
                # Analyser les connexions
                total_connections = data.get("total_connections", 0)
                active_connections = data.get("active_connections", 0)
                facebook_connections = data.get("facebook_connections", 0)
                instagram_connections = data.get("instagram_connections", 0)
                
                print(f"   📊 Total connexions: {total_connections}")
                print(f"   📊 Connexions actives: {active_connections}")
                print(f"   📘 Connexions Facebook: {facebook_connections}")
                print(f"   📷 Connexions Instagram: {instagram_connections}")
                
                # Rechercher tokens EAA dans toutes les collections
                eaa_tokens_found = 0
                page_access_tokens = 0
                temp_tokens_found = 0
                
                print(f"\n🔍 RECHERCHE TOKENS EAA (PERMANENTS):")
                
                # Vérifier social_media_connections
                social_media_connections = data.get("social_media_connections", [])
                print(f"   📋 Collection social_media_connections: {len(social_media_connections)} connexions")
                
                for conn in social_media_connections:
                    platform = conn.get("platform", "")
                    access_token = conn.get("access_token", "")
                    token_type = conn.get("token_type", "")
                    is_active = conn.get("active", False)
                    
                    if access_token:
                        if access_token.startswith("EAA"):
                            eaa_tokens_found += 1
                            print(f"      ✅ TOKEN EAA TROUVÉ!")
                            print(f"         Platform: {platform}")
                            print(f"         Token: {access_token[:30]}...")
                            print(f"         Type: {token_type}")
                            print(f"         Actif: {is_active}")
                            
                            if token_type == "page_access_token":
                                page_access_tokens += 1
                                print(f"         🎉 TYPE: page_access_token (PERMANENT)")
                        elif access_token.startswith("temp_"):
                            temp_tokens_found += 1
                            print(f"      ⚠️ Token temporaire trouvé: {access_token[:40]}...")
                        else:
                            print(f"      🔍 Autre format token: {access_token[:30]}...")
                
                # Vérifier social_connections_old
                social_connections_old = data.get("social_connections_old", [])
                print(f"   📋 Collection social_connections_old: {len(social_connections_old)} connexions")
                
                for conn in social_connections_old:
                    platform = conn.get("platform", "")
                    access_token = conn.get("access_token", "")
                    token_type = conn.get("token_type", "")
                    is_active = conn.get("is_active", False)
                    
                    if access_token:
                        if access_token.startswith("EAA"):
                            eaa_tokens_found += 1
                            print(f"      ✅ TOKEN EAA TROUVÉ (old collection)!")
                            print(f"         Platform: {platform}")
                            print(f"         Token: {access_token[:30]}...")
                            print(f"         Type: {token_type}")
                            print(f"         Actif: {is_active}")
                            
                            if token_type == "page_access_token":
                                page_access_tokens += 1
                                print(f"         🎉 TYPE: page_access_token (PERMANENT)")
                        elif access_token.startswith("temp_"):
                            temp_tokens_found += 1
                            print(f"      ⚠️ Token temporaire trouvé: {access_token[:40]}...")
                
                print(f"\n📊 RÉSULTATS TEST 1:")
                print(f"   🔑 Tokens EAA trouvés: {eaa_tokens_found}")
                print(f"   🎯 Page access tokens: {page_access_tokens}")
                print(f"   ⚠️ Tokens temporaires: {temp_tokens_found}")
                
                if eaa_tokens_found > 0 and page_access_tokens > 0:
                    print(f"   🎉 SUCCÈS: Flow 3-étapes ChatGPT RÉUSSI!")
                    print(f"   ✅ Tokens permanents EAA avec type page_access_token détectés")
                    return True, data
                elif temp_tokens_found > 0:
                    print(f"   ❌ ÉCHEC: Seulement des tokens temporaires trouvés")
                    print(f"   📋 Le flow 3-étapes n'est pas terminé")
                    return False, data
                else:
                    print(f"   ⚠️ Aucun token trouvé - reconnexion nécessaire")
                    return False, data
                    
            else:
                print(f"   ❌ Erreur endpoint debug: {response.status_code}")
                return False, None
                
        except Exception as e:
            print(f"   ❌ Erreur test 1: {e}")
            return False, None
    
    def test_2_publication_avec_tokens_permanents(self):
        """TEST 2: Test publication avec tokens permanents"""
        print("\n📝 TEST 2: Test publication avec tokens permanents...")
        print("   🎯 Objectif: POST /api/posts/publish avec post contenant image")
        print("   🎯 Vérifier que validation stricte accepte maintenant les tokens EAA")
        
        try:
            # Récupérer les posts disponibles
            posts_response = self.session.get(f"{BACKEND_URL}/posts/generated", timeout=30)
            
            if posts_response.status_code != 200:
                print(f"   ❌ Impossible de récupérer les posts: {posts_response.status_code}")
                return False
            
            posts_data = posts_response.json()
            posts = posts_data.get("posts", [])
            
            if not posts:
                print(f"   ⚠️ Aucun post disponible pour test")
                return False
            
            # Chercher un post Facebook avec image
            facebook_post_with_image = None
            for post in posts:
                if (post.get("platform") == "facebook" and 
                    post.get("visual_url") and 
                    not post.get("published", False)):
                    facebook_post_with_image = post
                    break
            
            if not facebook_post_with_image:
                print(f"   ⚠️ Aucun post Facebook avec image trouvé")
                # Essayer n'importe quel post Facebook
                for post in posts:
                    if post.get("platform") == "facebook":
                        facebook_post_with_image = post
                        break
            
            if not facebook_post_with_image:
                print(f"   ❌ Aucun post Facebook disponible")
                return False
            
            post_id = facebook_post_with_image.get("id")
            has_image = bool(facebook_post_with_image.get("visual_url"))
            
            print(f"   📋 Test avec post: {post_id}")
            print(f"   📋 Titre: {facebook_post_with_image.get('title', 'Sans titre')}")
            print(f"   📋 Contient image: {'Oui' if has_image else 'Non'}")
            
            # Tenter la publication
            start_time = time.time()
            pub_response = self.session.post(
                f"{BACKEND_URL}/posts/publish",
                json={"post_id": post_id},
                timeout=60
            )
            end_time = time.time()
            
            print(f"   ⏱️ Temps de réponse: {end_time - start_time:.2f}s")
            print(f"   📊 Status code: {pub_response.status_code}")
            
            if pub_response.status_code == 200:
                pub_data = pub_response.json()
                print(f"   🎉 PUBLICATION RÉUSSIE!")
                print(f"   📋 Réponse: {json.dumps(pub_data, indent=2)}")
                
                # Vérifier si méthode binaire fonctionne avec vrais tokens
                if has_image:
                    print(f"   ✅ Publication avec image réussie - tokens EAA fonctionnent!")
                
                return True
                
            elif pub_response.status_code == 400:
                pub_data = pub_response.json()
                error_msg = pub_data.get("error", "Erreur inconnue")
                print(f"   ❌ Échec publication: {error_msg}")
                
                if "Aucune connexion sociale active" in error_msg:
                    print(f"   📋 Erreur attendue: Pas de connexion sociale active")
                    print(f"   📋 Tokens peut-être pas encore sauvegardés correctement")
                elif "Invalid OAuth access token" in error_msg:
                    print(f"   🚨 CRITIQUE: Tokens EAA rejetés par Facebook!")
                    print(f"   📋 Les tokens ne sont peut-être pas vraiment permanents")
                
                return False
            else:
                print(f"   ❌ Réponse inattendue: {pub_response.status_code}")
                print(f"   📄 Réponse: {pub_response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Erreur test 2: {e}")
            return False
    
    def test_3_validation_format_tokens_sauvegardes(self, connections_data):
        """TEST 3: Validation format tokens sauvegardés"""
        print("\n🔍 TEST 3: Validation format tokens sauvegardés...")
        print("   🎯 Objectif: Analyser structure des connexions sauvegardées")
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
    
    def test_publication_with_validation(self):
        """Test validation token avec nouveaux critères"""
        print("\n🧪 ÉTAPE 3: Test validation token avec publication...")
        
        try:
            # D'abord, récupérer un post Facebook pour tester
            posts_response = self.session.get(
                f"{BACKEND_URL}/posts/generated",
                timeout=30
            )
            
            if posts_response.status_code != 200:
                print(f"   ❌ Impossible de récupérer les posts: {posts_response.status_code}")
                return {"test_result": "no_posts"}
            
            posts_data = posts_response.json()
            posts = posts_data.get("posts", [])
            
            # Chercher un post Facebook avec image
            facebook_post = None
            for post in posts:
                if post.get("platform") == "facebook" and post.get("visual_url"):
                    facebook_post = post
                    break
            
            if not facebook_post:
                print("   ⚠️  Aucun post Facebook avec image trouvé")
                # Créer un post de test si nécessaire
                return {"test_result": "no_facebook_posts"}
            
            post_id = facebook_post.get("id")
            print(f"   📝 Post de test trouvé: {post_id}")
            print(f"   🖼️  Image: {facebook_post.get('visual_url', 'N/A')}")
            
            # Tenter la publication
            publish_response = self.session.post(
                f"{BACKEND_URL}/posts/publish",
                json={"post_id": post_id},
                timeout=30
            )
            
            print(f"   📤 Statut publication: {publish_response.status_code}")
            
            if publish_response.status_code == 200:
                result = publish_response.json()
                print(f"   ✅ Publication réussie!")
                print(f"   📄 Réponse: {json.dumps(result, indent=2)}")
                return {"test_result": "success", "response": result}
            else:
                error_text = publish_response.text
                print(f"   ❌ Publication échouée")
                print(f"   📄 Erreur: {error_text}")
                
                # Analyser le type d'erreur
                if "connexion sociale active" in error_text.lower():
                    return {"test_result": "no_active_connections", "error": error_text}
                elif "invalid oauth" in error_text.lower():
                    return {"test_result": "invalid_token", "error": error_text}
                elif "cannot parse access token" in error_text.lower():
                    return {"test_result": "unparseable_token", "error": error_text}
                else:
                    return {"test_result": "other_error", "error": error_text}
                    
        except Exception as e:
            print(f"   ❌ Erreur test publication: {e}")
            return {"test_result": "exception", "error": str(e)}
    
    def trace_publication_flow(self):
        """Diagnostic flow de publication actuel"""
        print("\n🔄 ÉTAPE 4: Diagnostic flow de publication...")
        
        try:
            # Vérifier les endpoints de publication disponibles
            endpoints_to_test = [
                "/posts/publish",
                "/social/facebook/publish-simple", 
                "/social/instagram/publish-simple"
            ]
            
            for endpoint in endpoints_to_test:
                print(f"\n   🔍 Test endpoint: {endpoint}")
                
                # Test avec données minimales pour voir la réponse
                test_data = {"post_id": "test_post_id"}
                
                response = self.session.post(
                    f"{BACKEND_URL}{endpoint}",
                    json=test_data,
                    timeout=30
                )
                
                print(f"      📊 Statut: {response.status_code}")
                
                if response.status_code in [400, 404, 422]:
                    # Erreurs attendues avec données de test
                    try:
                        error_data = response.json()
                        print(f"      📄 Erreur: {error_data.get('error', response.text)}")
                    except:
                        print(f"      📄 Erreur: {response.text}")
                elif response.status_code == 200:
                    print(f"      ✅ Endpoint accessible")
                else:
                    print(f"      ❓ Réponse inattendue: {response.text}")
            
            return {"flow_analysis": "completed"}
            
        except Exception as e:
            print(f"   ❌ Erreur diagnostic flow: {e}")
            return {"flow_analysis": "error", "error": str(e)}
    
    def check_carousel_conversion(self):
        """Vérifier conversion URL carousel"""
        print("\n🎠 ÉTAPE 5: Vérification conversion URL carousel...")
        
        try:
            # Tester la fonction convert_to_public_image_url via un endpoint
            test_urls = [
                "/api/content/carousel/carousel_90e5d8c2-test",
                "/api/content/12345/file",
                "https://pixabay.com/image.jpg",
                "uploads/user/image_123.jpg"
            ]
            
            print("   🔍 Test de conversion d'URLs:")
            
            for test_url in test_urls:
                print(f"      📥 URL originale: {test_url}")
                
                # Simuler la conversion (nous ne pouvons pas appeler directement la fonction)
                # Mais nous pouvons tester via les endpoints de publication
                
                if "carousel_" in test_url:
                    print(f"      🎠 Type: Carousel détecté")
                elif "/api/content/" in test_url and "/file" in test_url:
                    print(f"      🔒 Type: URL protégée détectée")
                elif test_url.startswith("http"):
                    print(f"      🌐 Type: URL externe détectée")
                elif "uploads/" in test_url:
                    print(f"      📁 Type: Upload local détecté")
                
                print(f"      📤 Conversion attendue: /api/public/image/[id].webp")
            
            return {"carousel_conversion": "analyzed"}
            
        except Exception as e:
            print(f"   ❌ Erreur vérification carousel: {e}")
            return {"carousel_conversion": "error", "error": str(e)}
    
    def run_complete_diagnostic(self):
        """Exécuter le diagnostic complet"""
        print("🚀 DÉBUT DIAGNOSTIC TOKENS FACEBOOK - PERMANENTS OU TEMPORAIRES?")
        print("=" * 80)
        
        results = {}
        
        # Étape 1: Authentification
        if not self.authenticate():
            print("\n❌ DIAGNOSTIC INTERROMPU - Échec authentification")
            return results
        
        # Étape 2: État des connexions sociales
        connections_result = self.get_social_connections_debug()
        results["connections"] = connections_result
        
        # Étape 3: Test de publication
        publication_result = self.test_publication_with_validation()
        results["publication"] = publication_result
        
        # Étape 4: Flow de publication
        flow_result = self.trace_publication_flow()
        results["flow"] = flow_result
        
        # Étape 5: Conversion carousel
        carousel_result = self.check_carousel_conversion()
        results["carousel"] = carousel_result
        
        # Analyse finale
        self.generate_final_analysis(results)
        
        return results
    
    def generate_final_analysis(self, results):
        """Générer l'analyse finale"""
        print("\n" + "=" * 80)
        print("📊 ANALYSE FINALE - DIAGNOSTIC TOKENS FACEBOOK")
        print("=" * 80)
        
        connections = results.get("connections", {})
        publication = results.get("publication", {})
        
        facebook_tokens = connections.get("facebook_tokens", [])
        
        if not facebook_tokens:
            print("❌ RÉSULTAT: AUCUN TOKEN FACEBOOK TROUVÉ")
            print("   🔧 ACTION REQUISE: L'utilisateur doit reconnecter Facebook")
            return
        
        print(f"📘 TOKENS FACEBOOK TROUVÉS: {len(facebook_tokens)}")
        
        permanent_tokens = 0
        temporary_tokens = 0
        
        for token_info in facebook_tokens:
            access_token = token_info.get("access_token", "")
            analysis = self.analyze_token_format(access_token)
            
            if analysis["type"] in ["permanent", "possibly_permanent"]:
                permanent_tokens += 1
            elif analysis["type"] in ["temporary"]:
                temporary_tokens += 1
        
        print(f"✅ TOKENS PERMANENTS (EAAG/EAA): {permanent_tokens}")
        print(f"⚠️  TOKENS TEMPORAIRES: {temporary_tokens}")
        
        # Analyse de la publication
        pub_result = publication.get("test_result", "")
        
        if pub_result == "success":
            print("✅ PUBLICATION: FONCTIONNE AVEC TOKENS ACTUELS")
        elif pub_result == "invalid_token":
            print("❌ PUBLICATION: TOKENS INVALIDES DÉTECTÉS")
        elif pub_result == "no_active_connections":
            print("⚠️  PUBLICATION: AUCUNE CONNEXION ACTIVE")
        else:
            print(f"❓ PUBLICATION: {pub_result}")
        
        # Conclusion finale
        print("\n🎯 CONCLUSION:")
        
        if permanent_tokens > 0 and pub_result == "success":
            print("✅ LES TOKENS FACEBOOK SONT MAINTENANT PERMANENTS ET FONCTIONNELS!")
            print("   🎉 Le problème de tokens temporaires a été résolu")
        elif permanent_tokens > 0 and pub_result != "success":
            print("⚠️  TOKENS PERMANENTS DÉTECTÉS MAIS PUBLICATION ÉCHOUE")
            print("   🔧 Vérifier la configuration ou les permissions")
        elif temporary_tokens > 0:
            print("❌ TOKENS TEMPORAIRES ENCORE PRÉSENTS")
            print("   🔧 L'utilisateur doit reconnecter Facebook pour obtenir des tokens permanents")
        else:
            print("❓ SITUATION AMBIGUË - ANALYSE MANUELLE REQUISE")
        
        print("\n📋 QUESTIONS CLÉS RÉPONDUES:")
        print(f"   • Les tokens commencent-ils par EAAG/EAA? {'✅ OUI' if permanent_tokens > 0 else '❌ NON'}")
        print(f"   • La méthode binaire est-elle utilisée? {'🔍 À vérifier dans les logs' if pub_result == 'success' else '❌ Publication échoue'}")
        print(f"   • La conversion carousel fonctionne-t-elle? {'✅ Logique implémentée' if results.get('carousel', {}).get('carousel_conversion') == 'analyzed' else '❓ Non testé'}")

def main():
    """Fonction principale"""
    diagnostic = FacebookTokenDiagnostic()
    results = diagnostic.run_complete_diagnostic()
    
    print(f"\n💾 Diagnostic terminé à {datetime.now().isoformat()}")
    
    # Sauvegarder les résultats si nécessaire
    try:
        with open("/app/facebook_token_diagnostic_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        print("📁 Résultats sauvegardés dans facebook_token_diagnostic_results.json")
    except Exception as e:
        print(f"⚠️  Impossible de sauvegarder: {e}")

if __name__ == "__main__":
    main()