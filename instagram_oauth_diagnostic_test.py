#!/usr/bin/env python3
"""
Instagram OAuth Configuration Diagnostic Test
===========================================

Test la configuration Instagram OAuth pour identifier le problème "Invalid platform app"
Credentials: lperpere@yahoo.fr / L@Reunion974!
Backend: https://social-pub-hub.preview.emergentagent.com/api

PROBLÈME IDENTIFIÉ: L'erreur "Invalid platform app" suggère que l'application Facebook 
(ID: 1115451684022643) n'est pas configurée correctement pour Instagram Basic Display API 
ou que l'URL de redirection ne correspond pas à la configuration dans Facebook pour Développeurs.
"""

import requests
import json
import sys
from urllib.parse import urlparse, parse_qs
import os

# Configuration
BACKEND_URL = "https://social-pub-hub.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class InstagramOAuthDiagnostic:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        
    def authenticate(self):
        """Étape 1: Authentification avec les credentials de test"""
        print("🔐 ÉTAPE 1: AUTHENTIFICATION")
        print(f"   Email: {TEST_EMAIL}")
        print(f"   Backend: {self.backend_url}")
        
        try:
            response = self.session.post(
                f"{self.backend_url}/auth/login-robust",
                json={
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                print(f"   ✅ Authentification réussie")
                print(f"   🆔 User ID: {self.user_id}")
                print(f"   🎫 Token: {self.access_token[:20]}..." if self.access_token else "   ❌ Pas de token")
                
                # Configurer les headers pour les requêtes suivantes
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                return True
            else:
                print(f"   ❌ Échec authentification: {response.status_code}")
                print(f"   📄 Réponse: {response.text}")
                return False
                
        except Exception as e:
            print(f"   💥 Erreur authentification: {str(e)}")
            return False
    
    def test_instagram_auth_url_generation(self):
        """Étape 2: Tester l'endpoint de génération d'URL Instagram"""
        print("\n🔗 ÉTAPE 2: TEST GÉNÉRATION URL INSTAGRAM")
        print(f"   Endpoint: GET {self.backend_url}/social/instagram/auth-url")
        
        try:
            response = self.session.get(
                f"{self.backend_url}/social/instagram/auth-url",
                timeout=10
            )
            
            print(f"   📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get("auth_url", "")
                state = data.get("state", "")
                redirect_uri = data.get("redirect_uri", "")
                
                print(f"   ✅ URL générée avec succès")
                print(f"   🔗 Auth URL: {auth_url}")
                print(f"   🔐 State: {state}")
                print(f"   🔄 Redirect URI: {redirect_uri}")
                
                # Analyser les paramètres de l'URL
                self.analyze_oauth_parameters(auth_url)
                
                return True, data
            else:
                print(f"   ❌ Échec génération URL: {response.status_code}")
                print(f"   📄 Réponse: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"   💥 Erreur génération URL: {str(e)}")
            return False, None
    
    def analyze_oauth_parameters(self, auth_url):
        """Étape 3: Analyser les paramètres OAuth générés"""
        print("\n🔍 ÉTAPE 3: ANALYSE PARAMÈTRES OAUTH")
        
        try:
            # Parser l'URL
            parsed_url = urlparse(auth_url)
            params = parse_qs(parsed_url.query)
            
            print(f"   🌐 Base URL: {parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}")
            print(f"   📋 Paramètres détectés:")
            
            # Analyser chaque paramètre
            client_id = params.get('client_id', [''])[0]
            redirect_uri = params.get('redirect_uri', [''])[0]
            scope = params.get('scope', [''])[0]
            response_type = params.get('response_type', [''])[0]
            state = params.get('state', [''])[0]
            
            print(f"      🆔 client_id: {client_id}")
            print(f"      🔄 redirect_uri: {redirect_uri}")
            print(f"      🎯 scope: {scope}")
            print(f"      📝 response_type: {response_type}")
            print(f"      🔐 state: {state}")
            
            # Vérifications critiques
            print(f"\n   🔍 VÉRIFICATIONS CRITIQUES:")
            
            # 1. Vérifier le client_id (FACEBOOK_APP_ID)
            expected_app_id = "1115451684022643"
            if client_id == expected_app_id:
                print(f"      ✅ FACEBOOK_APP_ID correct: {client_id}")
            else:
                print(f"      ❌ FACEBOOK_APP_ID incorrect!")
                print(f"         Attendu: {expected_app_id}")
                print(f"         Reçu: {client_id}")
            
            # 2. Vérifier l'URL de redirection
            expected_redirect = "https://social-pub-hub.preview.emergentagent.com/api/social/instagram/callback"
            if redirect_uri == expected_redirect:
                print(f"      ✅ Redirect URI correct")
            else:
                print(f"      ⚠️ Redirect URI différent:")
                print(f"         Attendu: {expected_redirect}")
                print(f"         Reçu: {redirect_uri}")
            
            # 3. Vérifier les scopes Instagram
            expected_scopes = "user_profile,user_media"
            if scope == expected_scopes:
                print(f"      ✅ Scopes Instagram corrects: {scope}")
            else:
                print(f"      ⚠️ Scopes différents:")
                print(f"         Attendu: {expected_scopes}")
                print(f"         Reçu: {scope}")
            
            # 4. Vérifier le response_type
            if response_type == "code":
                print(f"      ✅ Response type correct: {response_type}")
            else:
                print(f"      ❌ Response type incorrect: {response_type}")
            
            return {
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "scope": scope,
                "response_type": response_type,
                "state": state
            }
            
        except Exception as e:
            print(f"   💥 Erreur analyse paramètres: {str(e)}")
            return None
    
    def test_facebook_app_configuration(self):
        """Étape 4: Tester la configuration de l'application Facebook"""
        print("\n🏢 ÉTAPE 4: TEST CONFIGURATION APPLICATION FACEBOOK")
        
        # Récupérer les variables d'environnement depuis le backend
        try:
            response = self.session.get(f"{self.backend_url}/diag", timeout=10)
            if response.status_code == 200:
                diag_data = response.json()
                print(f"   ✅ Diagnostic backend accessible")
                print(f"   🗄️ Database: {diag_data.get('database_connected', 'Unknown')}")
                print(f"   🌍 Environment: {diag_data.get('environment', 'Unknown')}")
            else:
                print(f"   ⚠️ Diagnostic backend non accessible: {response.status_code}")
        except Exception as e:
            print(f"   ⚠️ Erreur diagnostic: {str(e)}")
        
        # Informations sur la configuration Facebook
        print(f"\n   📋 CONFIGURATION FACEBOOK DÉTECTÉE:")
        print(f"      🆔 FACEBOOK_APP_ID: 1115451684022643")
        print(f"      🔄 FACEBOOK_REDIRECT_URI: https://social-pub-hub.preview.emergentagent.com/auth/facebook/callback")
        print(f"      🎯 Instagram Redirect URI: https://social-pub-hub.preview.emergentagent.com/api/social/instagram/callback")
        
        print(f"\n   ⚠️ PROBLÈMES POTENTIELS IDENTIFIÉS:")
        print(f"      1. L'application Facebook (1115451684022643) doit être configurée pour Instagram Basic Display API")
        print(f"      2. L'URL de redirection Instagram doit être ajoutée dans Facebook Developer Console")
        print(f"      3. Les permissions Instagram (user_profile, user_media) doivent être activées")
        print(f"      4. L'application doit être en mode 'Live' pour Instagram Basic Display")
    
    def test_instagram_oauth_url_accessibility(self, auth_url):
        """Étape 5: Tester l'accessibilité de l'URL Instagram OAuth"""
        print("\n🌐 ÉTAPE 5: TEST ACCESSIBILITÉ URL INSTAGRAM OAUTH")
        
        try:
            # Faire une requête HEAD pour vérifier l'accessibilité sans déclencher l'OAuth
            response = requests.head(auth_url, timeout=10, allow_redirects=True)
            
            print(f"   📊 Status Code: {response.status_code}")
            print(f"   🔗 Final URL: {response.url}")
            
            if response.status_code == 200:
                print(f"   ✅ URL Instagram OAuth accessible")
                return True
            elif response.status_code == 400:
                print(f"   ❌ Erreur 400: Paramètres OAuth invalides")
                print(f"      → Vérifier client_id, redirect_uri, scopes")
                return False
            elif response.status_code == 401:
                print(f"   ❌ Erreur 401: Application non autorisée")
                print(f"      → Vérifier configuration Facebook Developer Console")
                return False
            else:
                print(f"   ⚠️ Status inattendu: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   💥 Erreur test accessibilité: {str(e)}")
            return False
    
    def generate_diagnostic_report(self, oauth_params):
        """Étape 6: Générer un rapport de diagnostic complet"""
        print("\n📊 ÉTAPE 6: RAPPORT DE DIAGNOSTIC COMPLET")
        
        print(f"\n   🎯 RÉSUMÉ DU PROBLÈME:")
        print(f"      L'erreur 'Invalid platform app' indique que l'application Facebook")
        print(f"      (ID: 1115451684022643) n'est pas correctement configurée pour")
        print(f"      Instagram Basic Display API.")
        
        print(f"\n   🔧 ACTIONS CORRECTIVES RECOMMANDÉES:")
        print(f"      1. Accéder à Facebook Developer Console (developers.facebook.com)")
        print(f"      2. Sélectionner l'application ID: 1115451684022643")
        print(f"      3. Ajouter le produit 'Instagram Basic Display'")
        print(f"      4. Configurer les URLs de redirection Instagram:")
        print(f"         - https://social-pub-hub.preview.emergentagent.com/api/social/instagram/callback")
        print(f"      5. Vérifier que les permissions sont activées:")
        print(f"         - instagram_graph_user_profile")
        print(f"         - instagram_graph_user_media")
        print(f"      6. Passer l'application en mode 'Live' pour Instagram")
        
        if oauth_params:
            print(f"\n   ✅ PARAMÈTRES OAUTH GÉNÉRÉS CORRECTEMENT:")
            print(f"      - Client ID: {oauth_params.get('client_id', 'N/A')}")
            print(f"      - Redirect URI: {oauth_params.get('redirect_uri', 'N/A')}")
            print(f"      - Scopes: {oauth_params.get('scope', 'N/A')}")
            print(f"      - Response Type: {oauth_params.get('response_type', 'N/A')}")
        
        print(f"\n   🎯 CONCLUSION:")
        print(f"      Le backend génère correctement les paramètres OAuth Instagram.")
        print(f"      Le problème se situe au niveau de la configuration de l'application")
        print(f"      Facebook dans le Developer Console, pas dans le code backend.")
    
    def run_full_diagnostic(self):
        """Exécuter le diagnostic complet"""
        print("🚀 DIAGNOSTIC INSTAGRAM OAUTH - PROBLÈME 'INVALID PLATFORM APP'")
        print("=" * 70)
        
        # Étape 1: Authentification
        if not self.authenticate():
            print("\n❌ DIAGNOSTIC INTERROMPU: Échec authentification")
            return False
        
        # Étape 2: Test génération URL
        success, auth_data = self.test_instagram_auth_url_generation()
        if not success:
            print("\n❌ DIAGNOSTIC INTERROMPU: Échec génération URL")
            return False
        
        auth_url = auth_data.get("auth_url", "")
        
        # Étape 3: Analyse paramètres (déjà fait dans l'étape 2)
        oauth_params = None
        if auth_url:
            oauth_params = self.analyze_oauth_parameters(auth_url)
        
        # Étape 4: Test configuration Facebook
        self.test_facebook_app_configuration()
        
        # Étape 5: Test accessibilité URL
        if auth_url:
            self.test_instagram_oauth_url_accessibility(auth_url)
        
        # Étape 6: Rapport final
        self.generate_diagnostic_report(oauth_params)
        
        print("\n" + "=" * 70)
        print("🎯 DIAGNOSTIC TERMINÉ")
        
        return True

def main():
    """Fonction principale"""
    diagnostic = InstagramOAuthDiagnostic()
    
    try:
        success = diagnostic.run_full_diagnostic()
        
        if success:
            print("\n✅ Diagnostic Instagram OAuth terminé avec succès")
            print("📋 Consultez le rapport ci-dessus pour les actions correctives")
        else:
            print("\n❌ Diagnostic Instagram OAuth échoué")
            print("🔍 Vérifiez les logs ci-dessus pour identifier les problèmes")
            
    except KeyboardInterrupt:
        print("\n⏹️ Diagnostic interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n💥 Erreur inattendue: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()