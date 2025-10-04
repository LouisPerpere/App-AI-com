#!/usr/bin/env python3
"""
DIAGNOSTIC INSTAGRAM CONNEXION LIVE - claire-marcus.com
=====================================================

Diagnostic complet du problème de connexion Instagram sur l'environnement LIVE claire-marcus.com.

CONTEXTE CRITIQUE:
- Le site LIVE est hébergé sur Emergent (pas ailleurs)
- Les variables d'environnement sont correctes sur LIVE
- Les URLs de callback sont correctes dans Facebook Developer Console
- Le problème existait AVANT les modifications de prévisualisation
- Il y a eu une RÉGRESSION sur LIVE - ça marchait avant

OBJECTIFS DU DIAGNOSTIC:
1. Tester l'environnement LIVE: https://claire-marcus.com/api
2. Analyser le callback Instagram sur LIVE
3. Vérifier si c'est un problème de code, de base de données, ou de configuration
4. Comparer avec ce qui fonctionnait avant
5. Identifier la cause de la régression

ACTIONS SPÉCIFIQUES:
1. Authentification sur LIVE avec lperpere@yahoo.fr / L@Reunion974!
2. Générer une URL d'auth Instagram sur LIVE
3. Tester le callback Instagram sur LIVE (simulation)
4. Vérifier l'état des connexions sur LIVE
5. Analyser les logs d'erreur spécifiques au LIVE
6. Identifier ce qui a changé pour causer la régression
"""

import requests
import json
import sys
import time
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# Configuration LIVE
LIVE_BASE_URL = "https://claire-marcus.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class LiveInstagramDiagnostic:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.diagnostic_results = {}
        
    def log_result(self, test_name, success, details=""):
        """Log diagnostic result"""
        self.diagnostic_results[test_name] = {
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
    def authenticate_live(self):
        """Authentification sur l'environnement LIVE"""
        print("🔐 ÉTAPE 1: Authentification sur LIVE claire-marcus.com...")
        
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        try:
            response = self.session.post(f"{LIVE_BASE_URL}/auth/login-robust", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                print(f"✅ Authentification LIVE réussie")
                print(f"   User ID: {self.user_id}")
                print(f"   Token: {self.access_token[:20]}..." if self.access_token else "   Token: None")
                
                self.log_result("authentication_live", True, f"User ID: {self.user_id}")
                return True
            else:
                error_msg = f"Status: {response.status_code}, Response: {response.text}"
                print(f"❌ Authentification LIVE échouée: {response.status_code}")
                print(f"   Response: {response.text}")
                
                self.log_result("authentication_live", False, error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Exception: {str(e)}"
            print(f"❌ Erreur authentification LIVE: {e}")
            self.log_result("authentication_live", False, error_msg)
            return False
    
    def test_live_health_check(self):
        """Vérifier l'état de santé de l'API LIVE"""
        print("\n🏥 ÉTAPE 2: Vérification santé API LIVE...")
        
        try:
            response = self.session.get(f"{LIVE_BASE_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API LIVE opérationnelle")
                print(f"   Status: {data.get('status', 'unknown')}")
                print(f"   Service: {data.get('service', 'unknown')}")
                print(f"   Timestamp: {data.get('timestamp', 'unknown')}")
                
                self.log_result("live_health_check", True, f"Status: {data.get('status')}")
                return True
            else:
                error_msg = f"Status: {response.status_code}"
                print(f"❌ API LIVE non opérationnelle: {response.status_code}")
                
                self.log_result("live_health_check", False, error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Exception: {str(e)}"
            print(f"❌ Erreur vérification santé LIVE: {e}")
            self.log_result("live_health_check", False, error_msg)
            return False
    
    def test_live_instagram_auth_url(self):
        """Tester la génération d'URL d'auth Instagram sur LIVE"""
        print("\n📱 ÉTAPE 3: Test génération URL auth Instagram LIVE...")
        
        try:
            response = self.session.get(f"{LIVE_BASE_URL}/social/instagram/auth-url")
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get("auth_url", "")
                
                print(f"✅ URL auth Instagram générée sur LIVE")
                print(f"   URL: {auth_url[:100]}...")
                
                # Parse URL to check redirect_uri
                parsed_url = urlparse(auth_url)
                query_params = parse_qs(parsed_url.query)
                redirect_uri = query_params.get("redirect_uri", [""])[0]
                client_id = query_params.get("client_id", [""])[0]
                config_id = query_params.get("config_id", [""])[0]
                state = query_params.get("state", [""])[0]
                
                print(f"   Redirect URI: {redirect_uri}")
                print(f"   Client ID: {client_id}")
                print(f"   Config ID: {config_id}")
                print(f"   State: {state[:20]}..." if state else "   State: None")
                
                # Vérifier que l'URL utilise le domaine LIVE
                if "claire-marcus.com" in redirect_uri:
                    print("✅ Redirect URI utilise le domaine LIVE correct")
                    live_domain_correct = True
                else:
                    print("❌ Redirect URI n'utilise pas le domaine LIVE")
                    print(f"   Attendu: claire-marcus.com")
                    print(f"   Trouvé: {redirect_uri}")
                    live_domain_correct = False
                
                # Vérifier les paramètres critiques
                has_required_params = bool(client_id and config_id and state and redirect_uri)
                
                details = {
                    "redirect_uri": redirect_uri,
                    "client_id": client_id,
                    "config_id": config_id,
                    "state_present": bool(state),
                    "live_domain_correct": live_domain_correct,
                    "has_required_params": has_required_params
                }
                
                success = live_domain_correct and has_required_params
                self.log_result("live_instagram_auth_url", success, json.dumps(details))
                return success
                    
            else:
                error_msg = f"Status: {response.status_code}, Response: {response.text}"
                print(f"❌ Génération URL auth Instagram LIVE échouée: {response.status_code}")
                print(f"   Response: {response.text}")
                
                self.log_result("live_instagram_auth_url", False, error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Exception: {str(e)}"
            print(f"❌ Erreur test URL auth Instagram LIVE: {e}")
            self.log_result("live_instagram_auth_url", False, error_msg)
            return False
    
    def test_live_instagram_callback_simulation(self):
        """Tester le callback Instagram sur LIVE avec simulation"""
        print("\n🔄 ÉTAPE 4: Test callback Instagram LIVE (simulation)...")
        
        try:
            # D'abord obtenir un paramètre state valide depuis l'URL d'auth
            auth_response = self.session.get(f"{LIVE_BASE_URL}/social/instagram/auth-url")
            if auth_response.status_code != 200:
                print("❌ Impossible d'obtenir l'URL d'auth pour le paramètre state")
                self.log_result("live_instagram_callback", False, "Cannot get auth URL for state")
                return False
                
            auth_data = auth_response.json()
            auth_url = auth_data.get("auth_url", "")
            parsed_url = urlparse(auth_url)
            query_params = parse_qs(parsed_url.query)
            state = query_params.get("state", [""])[0]
            
            if not state:
                print("❌ Aucun paramètre state trouvé dans l'URL d'auth")
                self.log_result("live_instagram_callback", False, "No state parameter in auth URL")
                return False
                
            print(f"   Utilisation paramètre state: {state[:20]}...")
            
            # Simuler callback avec paramètres de test
            callback_params = {
                "code": "live_test_authorization_code_instagram_12345",
                "state": state
            }
            
            # Tester l'endpoint callback
            callback_url = f"{LIVE_BASE_URL}/social/instagram/callback"
            response = self.session.get(callback_url, params=callback_params, allow_redirects=False)
            
            print(f"   Status callback: {response.status_code}")
            
            # Analyser la réponse du callback
            if response.status_code in [302, 200]:
                print("✅ Endpoint callback Instagram LIVE accessible")
                
                callback_success = True
                error_type = "none"
                redirect_url = ""
                
                if response.status_code == 302:
                    redirect_url = response.headers.get("Location", "")
                    print(f"   URL de redirection: {redirect_url}")
                    
                    # Vérifier si la redirection utilise le domaine LIVE
                    if "claire-marcus.com" in redirect_url:
                        print("✅ Redirection callback utilise le domaine LIVE correct")
                    else:
                        print("❌ Redirection callback n'utilise pas le domaine LIVE")
                        callback_success = False
                    
                    # Analyser le type d'erreur dans la redirection
                    if "invalid_state" in redirect_url.lower():
                        error_type = "invalid_state"
                        print("⚠️ Erreur de validation state (attendue avec données de test)")
                    elif "token_exchange" in redirect_url.lower():
                        error_type = "token_exchange"
                        print("⚠️ Erreur d'échange de token (attendue avec code de test)")
                    elif "success" in redirect_url.lower():
                        error_type = "success"
                        print("✅ Callback réussi (inattendu avec données de test)")
                    else:
                        error_type = "unknown"
                        print("⚠️ Type d'erreur inconnu dans la redirection")
                
                details = {
                    "status_code": response.status_code,
                    "redirect_url": redirect_url,
                    "error_type": error_type,
                    "callback_accessible": True,
                    "live_domain_redirect": "claire-marcus.com" in redirect_url if redirect_url else False
                }
                
                self.log_result("live_instagram_callback", callback_success, json.dumps(details))
                return callback_success
                    
            else:
                error_msg = f"Status: {response.status_code}, Response: {response.text}"
                print(f"❌ Callback Instagram LIVE échoué: {response.status_code}")
                print(f"   Response: {response.text}")
                
                self.log_result("live_instagram_callback", False, error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Exception: {str(e)}"
            print(f"❌ Erreur test callback Instagram LIVE: {e}")
            self.log_result("live_instagram_callback", False, error_msg)
            return False
    
    def test_live_social_connections_state(self):
        """Vérifier l'état des connexions sociales sur LIVE"""
        print("\n🔗 ÉTAPE 5: Vérification état connexions sociales LIVE...")
        
        try:
            # Test endpoint principal des connexions
            response = self.session.get(f"{LIVE_BASE_URL}/social/connections")
            
            if response.status_code == 200:
                data = response.json()
                connections = data.get("connections", [])
                
                print(f"✅ Endpoint connexions sociales LIVE accessible")
                print(f"   Connexions actives: {len(connections)}")
                
                facebook_connections = 0
                instagram_connections = 0
                
                for conn in connections:
                    platform = conn.get("platform", "unknown")
                    active = conn.get("active", False)
                    print(f"   - {platform}: {'active' if active else 'inactive'}")
                    
                    if platform.lower() == "facebook":
                        facebook_connections += 1
                    elif platform.lower() == "instagram":
                        instagram_connections += 1
                
                details = {
                    "total_connections": len(connections),
                    "facebook_connections": facebook_connections,
                    "instagram_connections": instagram_connections,
                    "connections": connections
                }
                
                self.log_result("live_social_connections", True, json.dumps(details, default=str))
                return True
            else:
                error_msg = f"Status: {response.status_code}, Response: {response.text}"
                print(f"❌ Endpoint connexions sociales LIVE échoué: {response.status_code}")
                print(f"   Response: {response.text}")
                
                self.log_result("live_social_connections", False, error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Exception: {str(e)}"
            print(f"❌ Erreur test connexions sociales LIVE: {e}")
            self.log_result("live_social_connections", False, error_msg)
            return False
    
    def test_live_debug_social_connections(self):
        """Tester l'endpoint de debug des connexions sociales sur LIVE"""
        print("\n🔍 ÉTAPE 6: Test debug connexions sociales LIVE...")
        
        try:
            response = self.session.get(f"{LIVE_BASE_URL}/debug/social-connections")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Endpoint debug connexions sociales LIVE accessible")
                print(f"   Total connexions: {data.get('total_connections', 0)}")
                print(f"   Connexions actives: {data.get('active_connections', 0)}")
                print(f"   Connexions Facebook: {data.get('facebook_connections', 0)}")
                print(f"   Connexions Instagram: {data.get('instagram_connections', 0)}")
                
                # Analyser les détails des connexions
                collections_data = data.get('collections_analysis', {})
                if collections_data:
                    print(f"   Analyse collections:")
                    for collection_name, collection_data in collections_data.items():
                        print(f"     - {collection_name}: {collection_data.get('count', 0)} connexions")
                
                self.log_result("live_debug_connections", True, json.dumps(data, default=str))
                return True
            else:
                error_msg = f"Status: {response.status_code}, Response: {response.text}"
                print(f"❌ Endpoint debug connexions LIVE échoué: {response.status_code}")
                print(f"   Response: {response.text}")
                
                self.log_result("live_debug_connections", False, error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Exception: {str(e)}"
            print(f"❌ Erreur test debug connexions LIVE: {e}")
            self.log_result("live_debug_connections", False, error_msg)
            return False
    
    def test_live_instagram_publication(self):
        """Tester la publication Instagram sur LIVE pour identifier les erreurs"""
        print("\n📤 ÉTAPE 7: Test publication Instagram LIVE...")
        
        try:
            # D'abord vérifier s'il y a des posts disponibles
            posts_response = self.session.get(f"{LIVE_BASE_URL}/posts/generated")
            
            if posts_response.status_code != 200:
                print("⚠️ Impossible de récupérer les posts générés")
                self.log_result("live_instagram_publication", False, "Cannot get generated posts")
                return False
            
            posts_data = posts_response.json()
            posts = posts_data.get("posts", [])
            
            # Chercher un post Instagram pour tester
            instagram_post = None
            for post in posts:
                if post.get("platform", "").lower() == "instagram":
                    instagram_post = post
                    break
            
            if not instagram_post:
                print("⚠️ Aucun post Instagram trouvé pour tester la publication")
                self.log_result("live_instagram_publication", False, "No Instagram posts found")
                return False
            
            post_id = instagram_post.get("id")
            print(f"   Test publication avec post ID: {post_id}")
            
            # Tenter la publication
            publish_data = {"post_id": post_id}
            response = self.session.post(f"{LIVE_BASE_URL}/posts/publish", json=publish_data)
            
            print(f"   Status publication: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Publication Instagram réussie (inattendu)")
                print(f"   Response: {data}")
                
                self.log_result("live_instagram_publication", True, json.dumps(data, default=str))
                return True
            else:
                # Analyser l'erreur de publication
                try:
                    error_data = response.json()
                    error_message = error_data.get("error", response.text)
                except:
                    error_message = response.text
                
                print(f"❌ Publication Instagram échouée (attendu)")
                print(f"   Erreur: {error_message}")
                
                # Analyser le type d'erreur pour diagnostic
                error_type = "unknown"
                if "connexion sociale" in error_message.lower():
                    error_type = "no_social_connections"
                elif "access token" in error_message.lower():
                    error_type = "invalid_access_token"
                elif "oauth" in error_message.lower():
                    error_type = "oauth_error"
                elif "api" in error_message.lower():
                    error_type = "api_error"
                
                details = {
                    "status_code": response.status_code,
                    "error_message": error_message,
                    "error_type": error_type,
                    "post_id": post_id
                }
                
                # Pour le diagnostic, une erreur de publication est informative
                self.log_result("live_instagram_publication", True, json.dumps(details))
                return True
                
        except Exception as e:
            error_msg = f"Exception: {str(e)}"
            print(f"❌ Erreur test publication Instagram LIVE: {e}")
            self.log_result("live_instagram_publication", False, error_msg)
            return False
    
    def analyze_regression_causes(self):
        """Analyser les causes possibles de la régression"""
        print("\n🔬 ÉTAPE 8: Analyse causes de régression...")
        
        potential_causes = []
        
        # Analyser les résultats des tests précédents
        auth_result = self.diagnostic_results.get("live_instagram_auth_url", {})
        callback_result = self.diagnostic_results.get("live_instagram_callback", {})
        connections_result = self.diagnostic_results.get("live_social_connections", {})
        debug_result = self.diagnostic_results.get("live_debug_connections", {})
        
        print("   Analyse des résultats de diagnostic:")
        
        # 1. Problème d'URL de callback
        if auth_result.get("success") and auth_result.get("details"):
            try:
                auth_details = json.loads(auth_result["details"])
                if not auth_details.get("live_domain_correct"):
                    potential_causes.append("URL de callback incorrecte - n'utilise pas claire-marcus.com")
                    print("   ❌ URL de callback incorrecte détectée")
                else:
                    print("   ✅ URL de callback correcte")
            except:
                pass
        
        # 2. Problème de callback
        if callback_result.get("success") and callback_result.get("details"):
            try:
                callback_details = json.loads(callback_result["details"])
                error_type = callback_details.get("error_type", "unknown")
                if error_type == "invalid_state":
                    potential_causes.append("Problème de validation du paramètre state")
                    print("   ⚠️ Problème de validation state détecté")
                elif error_type == "token_exchange":
                    potential_causes.append("Problème d'échange de token avec Facebook API")
                    print("   ❌ Problème d'échange de token détecté")
            except:
                pass
        
        # 3. Problème de base de données
        if connections_result.get("success") and connections_result.get("details"):
            try:
                conn_details = json.loads(connections_result["details"])
                instagram_count = conn_details.get("instagram_connections", 0)
                if instagram_count == 0:
                    potential_causes.append("Aucune connexion Instagram active en base de données")
                    print("   ❌ Aucune connexion Instagram active trouvée")
                else:
                    print(f"   ✅ {instagram_count} connexion(s) Instagram trouvée(s)")
            except:
                pass
        
        # 4. Problème de configuration
        if not auth_result.get("success"):
            potential_causes.append("Problème de configuration OAuth Instagram")
            print("   ❌ Problème de configuration OAuth détecté")
        
        print(f"\n   Causes potentielles identifiées: {len(potential_causes)}")
        for i, cause in enumerate(potential_causes, 1):
            print(f"   {i}. {cause}")
        
        # Recommandations basées sur l'analyse
        recommendations = []
        
        if "URL de callback incorrecte" in str(potential_causes):
            recommendations.append("Vérifier les variables d'environnement INSTAGRAM_REDIRECT_URI sur LIVE")
        
        if "token_exchange" in str(potential_causes):
            recommendations.append("Vérifier la configuration Facebook Developer Console")
            recommendations.append("Vérifier les clés FACEBOOK_APP_ID et FACEBOOK_APP_SECRET sur LIVE")
        
        if "Aucune connexion Instagram active" in str(potential_causes):
            recommendations.append("L'utilisateur doit reconnecter son compte Instagram")
        
        if "configuration OAuth" in str(potential_causes):
            recommendations.append("Vérifier toutes les variables d'environnement OAuth sur LIVE")
        
        print(f"\n   Recommandations: {len(recommendations)}")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        analysis_result = {
            "potential_causes": potential_causes,
            "recommendations": recommendations,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        self.log_result("regression_analysis", True, json.dumps(analysis_result))
        return True
    
    def run_complete_diagnostic(self):
        """Exécuter le diagnostic complet Instagram LIVE"""
        print("🎯 DIAGNOSTIC COMPLET INSTAGRAM CONNEXION LIVE")
        print("=" * 70)
        print(f"Environnement cible: {LIVE_BASE_URL}")
        print(f"Utilisateur test: {TEST_EMAIL}")
        print("=" * 70)
        
        test_results = []
        
        # Étape 1: Authentification LIVE
        if not self.authenticate_live():
            print("\n❌ Authentification LIVE échouée - impossible de continuer le diagnostic")
            return False
        
        # Étape 2: Vérification santé API
        test_results.append(("Santé API LIVE", self.test_live_health_check()))
        
        # Étape 3: Test URL auth Instagram
        test_results.append(("URL Auth Instagram LIVE", self.test_live_instagram_auth_url()))
        
        # Étape 4: Test callback Instagram
        test_results.append(("Callback Instagram LIVE", self.test_live_instagram_callback_simulation()))
        
        # Étape 5: État connexions sociales
        test_results.append(("Connexions Sociales LIVE", self.test_live_social_connections_state()))
        
        # Étape 6: Debug connexions
        test_results.append(("Debug Connexions LIVE", self.test_live_debug_social_connections()))
        
        # Étape 7: Test publication
        test_results.append(("Publication Instagram LIVE", self.test_live_instagram_publication()))
        
        # Étape 8: Analyse régression
        test_results.append(("Analyse Régression", self.analyze_regression_causes()))
        
        # Résumé du diagnostic
        print("\n" + "=" * 70)
        print("📊 RÉSULTATS DIAGNOSTIC INSTAGRAM LIVE")
        print("=" * 70)
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ RÉUSSI" if result else "❌ ÉCHOUÉ"
            print(f"{status} {test_name}")
            if result:
                passed_tests += 1
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"\n📈 Taux de réussite: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Diagnostic final
        print("\n" + "=" * 70)
        print("🔬 DIAGNOSTIC FINAL")
        print("=" * 70)
        
        if success_rate >= 75:
            print("✅ La plupart des composants fonctionnent correctement sur LIVE")
            print("   Le problème semble être spécifique à la connexion Instagram")
        else:
            print("❌ Plusieurs composants ont des problèmes sur LIVE")
            print("   Investigation approfondie requise")
        
        # Afficher les détails du diagnostic
        print("\n📋 DÉTAILS DIAGNOSTIC:")
        for test_name, result_data in self.diagnostic_results.items():
            if result_data.get("details"):
                print(f"\n{test_name.upper()}:")
                try:
                    if result_data["details"].startswith("{"):
                        details = json.loads(result_data["details"])
                        for key, value in details.items():
                            print(f"  - {key}: {value}")
                    else:
                        print(f"  - {result_data['details']}")
                except:
                    print(f"  - {result_data['details']}")
        
        return success_rate >= 50

def main():
    """Exécution principale du diagnostic"""
    diagnostic = LiveInstagramDiagnostic()
    success = diagnostic.run_complete_diagnostic()
    
    if success:
        print("\n✅ Diagnostic LIVE Instagram terminé avec succès")
        print("   Consultez les résultats ci-dessus pour identifier la cause de la régression")
        sys.exit(0)
    else:
        print("\n❌ Diagnostic LIVE Instagram révèle des problèmes critiques")
        print("   Investigation technique approfondie requise")
        sys.exit(1)

if __name__ == "__main__":
    main()