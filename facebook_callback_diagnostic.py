#!/usr/bin/env python3
"""
🎯 DIAGNOSTIC CALLBACK FACEBOOK EN TEMPS RÉEL
Test complet pour diagnostiquer pourquoi le callback Facebook ne fonctionne pas
alors qu'Instagram fonctionne.

Identifiants: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import time
from datetime import datetime
import urllib.parse

# Configuration
BACKEND_URL = "https://claire-marcus-app-1.preview.emergentagent.com/api"
EMAIL = "lperpere@yahoo.fr"
PASSWORD = "L@Reunion974!"

class FacebookCallbackDiagnostic:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        
    def authenticate(self):
        """Authentification avec les identifiants fournis"""
        print("🔐 ÉTAPE 1: Authentification...")
        
        auth_data = {
            "email": EMAIL,
            "password": PASSWORD
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login-robust", json=auth_data)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                print(f"✅ Authentification réussie - User ID: {self.user_id}")
                return True
            else:
                print(f"❌ Échec authentification: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur authentification: {e}")
            return False
    
    def check_social_connections_state(self):
        """Vérifier l'état actuel des connexions sociales"""
        print("\n🔍 ÉTAPE 2: Vérification état connexions sociales...")
        
        try:
            # Vérifier les connexions via l'endpoint de debug
            response = self.session.get(f"{BACKEND_URL}/debug/social-connections")
            
            if response.status_code == 200:
                data = response.json()
                print("📊 État des connexions sociales:")
                print(f"   - Connexions actives: {data.get('active_connections', 0)}")
                print(f"   - Connexions Facebook: {data.get('facebook_connections', 0)}")
                print(f"   - Connexions Instagram: {data.get('instagram_connections', 0)}")
                
                # Détails des collections
                collections = data.get('collections_analysis', {})
                for collection_name, info in collections.items():
                    print(f"   - Collection {collection_name}: {info.get('count', 0)} connexions")
                
                return data
            else:
                print(f"❌ Impossible de récupérer l'état des connexions: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur vérification connexions: {e}")
            return None
    
    def test_facebook_auth_url_generation(self):
        """Tester la génération d'URL d'authentification Facebook"""
        print("\n🔗 ÉTAPE 3: Test génération URL d'authentification Facebook...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/social/facebook/auth-url")
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get('auth_url', '')
                state = data.get('state', '')
                
                print(f"✅ URL d'authentification générée:")
                print(f"   - URL: {auth_url[:100]}...")
                print(f"   - State: {state}")
                
                # Analyser les paramètres de l'URL
                parsed_url = urllib.parse.urlparse(auth_url)
                params = urllib.parse.parse_qs(parsed_url.query)
                
                print("📋 Paramètres de l'URL:")
                for key, value in params.items():
                    print(f"   - {key}: {value[0] if value else 'N/A'}")
                
                return auth_url, state
            else:
                print(f"❌ Échec génération URL: {response.status_code} - {response.text}")
                return None, None
                
        except Exception as e:
            print(f"❌ Erreur génération URL: {e}")
            return None, None
    
    def test_facebook_callback_endpoint(self, state=None):
        """Tester l'endpoint de callback Facebook directement"""
        print("\n🎯 ÉTAPE 4: Test direct de l'endpoint callback Facebook...")
        
        # Utiliser un state approprié si fourni
        if not state:
            state = f"test_state_{int(time.time())}|{self.user_id}"
        
        # Paramètres de test pour simuler un callback Facebook
        test_params = {
            "code": "test_authorization_code_123",
            "state": state
        }
        
        try:
            # Test sans paramètres (vérifier que l'endpoint existe)
            print("   🔍 Test 1: Endpoint accessible...")
            response = self.session.get(f"{BACKEND_URL}/social/facebook/callback")
            print(f"   - Status sans paramètres: {response.status_code}")
            
            # Test avec paramètres de callback
            print("   🔍 Test 2: Callback avec paramètres...")
            response = self.session.get(f"{BACKEND_URL}/social/facebook/callback", params=test_params)
            print(f"   - Status avec paramètres: {response.status_code}")
            print(f"   - Response headers: {dict(response.headers)}")
            
            if response.status_code in [302, 307]:
                redirect_url = response.headers.get('Location', 'N/A')
                print(f"   - Redirection vers: {redirect_url}")
            
            return response.status_code
            
        except Exception as e:
            print(f"❌ Erreur test callback: {e}")
            return None
    
    def test_instagram_callback_comparison(self):
        """Tester le callback Instagram pour comparaison"""
        print("\n📱 ÉTAPE 5: Test callback Instagram (pour comparaison)...")
        
        state = f"test_state_{int(time.time())}|{self.user_id}"
        test_params = {
            "code": "test_instagram_code_123",
            "state": state
        }
        
        try:
            response = self.session.get(f"{BACKEND_URL}/social/instagram/callback", params=test_params)
            print(f"   - Status Instagram callback: {response.status_code}")
            
            if response.status_code in [302, 307]:
                redirect_url = response.headers.get('Location', 'N/A')
                print(f"   - Redirection Instagram vers: {redirect_url}")
            
            return response.status_code
            
        except Exception as e:
            print(f"❌ Erreur test Instagram callback: {e}")
            return None
    
    def analyze_environment_variables(self):
        """Analyser les variables d'environnement Facebook"""
        print("\n🔧 ÉTAPE 6: Analyse configuration Facebook...")
        
        try:
            # Tester l'endpoint de debug de configuration (s'il existe)
            response = self.session.get(f"{BACKEND_URL}/test/config-debug")
            
            if response.status_code == 200:
                data = response.json()
                print("📋 Configuration Facebook:")
                
                facebook_config = data.get('facebook', {})
                for key, value in facebook_config.items():
                    if 'secret' in key.lower():
                        print(f"   - {key}: {'✅ Configuré' if value else '❌ Manquant'}")
                    else:
                        print(f"   - {key}: {value}")
                
                return data
            else:
                print(f"⚠️ Endpoint de debug config non disponible: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"⚠️ Impossible d'analyser la configuration: {e}")
            return None
    
    def test_token_exchange_simulation(self):
        """Simuler l'échange de token Facebook"""
        print("\n🔄 ÉTAPE 7: Simulation échange de token Facebook...")
        
        # Ceci est une simulation - nous ne pouvons pas faire un vrai échange sans code valide
        facebook_token_url = "https://graph.facebook.com/v20.0/oauth/access_token"
        
        print(f"   - URL d'échange de token: {facebook_token_url}")
        print("   - ⚠️ Simulation seulement (pas de code valide disponible)")
        
        # Vérifier si l'API Facebook est accessible
        try:
            test_response = requests.get("https://graph.facebook.com/v20.0/me", timeout=5)
            print(f"   - API Facebook accessible: {test_response.status_code}")
        except Exception as e:
            print(f"   - ⚠️ Problème d'accès API Facebook: {e}")
    
    def check_backend_logs_for_facebook(self):
        """Vérifier les logs backend pour les erreurs Facebook"""
        print("\n📋 ÉTAPE 8: Vérification logs backend Facebook...")
        
        try:
            # Simuler une tentative de callback pour générer des logs
            print("   🔍 Génération de logs via tentative callback...")
            
            state = f"diagnostic_{int(time.time())}|{self.user_id}"
            test_params = {
                "code": "AQD_diagnostic_test_code_123",
                "state": state,
                "error": None
            }
            
            # Faire l'appel pour générer des logs
            response = self.session.get(f"{BACKEND_URL}/social/facebook/callback", params=test_params)
            
            print(f"   - Callback test effectué: {response.status_code}")
            print("   - ⚠️ Vérifiez les logs backend avec: tail -f /var/log/supervisor/backend.out.log")
            print("   - Recherchez: 'Facebook OAuth callback' dans les logs")
            
            return response.status_code
            
        except Exception as e:
            print(f"   ❌ Erreur génération logs: {e}")
            return None
    
    def run_complete_diagnostic(self):
        """Exécuter le diagnostic complet"""
        print("🚨 DIAGNOSTIC CALLBACK FACEBOOK EN TEMPS RÉEL")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Identifiants: {EMAIL}")
        print()
        
        # Étape 1: Authentification
        if not self.authenticate():
            print("❌ DIAGNOSTIC ARRÊTÉ - Échec authentification")
            return
        
        # Étape 2: État des connexions
        connections_state = self.check_social_connections_state()
        
        # Étape 3: Génération URL Facebook
        auth_url, state = self.test_facebook_auth_url_generation()
        
        # Étape 4: Test callback Facebook
        facebook_callback_status = self.test_facebook_callback_endpoint(state)
        
        # Étape 5: Test callback Instagram (comparaison)
        instagram_callback_status = self.test_instagram_callback_comparison()
        
        # Étape 6: Configuration
        config_data = self.analyze_environment_variables()
        
        # Étape 7: Simulation échange token
        self.test_token_exchange_simulation()
        
        # Étape 8: Génération de logs
        log_test_status = self.check_backend_logs_for_facebook()
        
        # Résumé du diagnostic
        print("\n" + "=" * 60)
        print("📋 RÉSUMÉ DU DIAGNOSTIC")
        print("=" * 60)
        
        print(f"✅ Authentification: {'OK' if self.token else 'ÉCHEC'}")
        print(f"📊 Connexions sociales: {connections_state.get('active_connections', 0) if connections_state else 'N/A'} actives")
        print(f"🔗 URL Facebook: {'OK' if auth_url else 'ÉCHEC'}")
        print(f"🎯 Callback Facebook: {facebook_callback_status if facebook_callback_status else 'ÉCHEC'}")
        print(f"📱 Callback Instagram: {instagram_callback_status if instagram_callback_status else 'ÉCHEC'}")
        print(f"🔧 Configuration: {'OK' if config_data else 'PARTIELLE'}")
        print(f"📋 Logs générés: {'OK' if log_test_status else 'ÉCHEC'}")
        
        # Diagnostic des problèmes identifiés
        print("\n🔍 PROBLÈMES IDENTIFIÉS:")
        
        if not auth_url:
            print("❌ CRITIQUE: Impossible de générer l'URL d'authentification Facebook")
        
        if facebook_callback_status != instagram_callback_status:
            print(f"⚠️ DIFFÉRENCE: Facebook callback ({facebook_callback_status}) vs Instagram ({instagram_callback_status})")
        
        if connections_state and connections_state.get('facebook_connections', 0) == 0:
            print("⚠️ AUCUNE CONNEXION FACEBOOK: Pas de connexions Facebook actives trouvées")
        
        print("\n🎯 RECOMMANDATIONS:")
        print("1. Vérifier les logs backend pendant une tentative de connexion Facebook réelle")
        print("2. Comparer le flow Facebook vs Instagram dans le code")
        print("3. Tester avec un code d'autorisation Facebook valide")
        print("4. Vérifier la configuration Facebook Developer Console")
        print("5. Analyser les différences de collection entre Instagram et Facebook")
        
        # Instructions pour l'utilisateur
        print("\n📝 INSTRUCTIONS POUR L'UTILISATEUR:")
        print("1. Tentez une connexion Facebook réelle sur l'interface")
        print("2. Pendant la tentative, surveillez les logs avec:")
        print("   tail -f /var/log/supervisor/backend.out.log | grep -i facebook")
        print("3. Recherchez spécifiquement les messages 'Facebook OAuth callback'")
        print("4. Notez toute erreur d'échange de token ou de sauvegarde")

if __name__ == "__main__":
    diagnostic = FacebookCallbackDiagnostic()
    diagnostic.run_complete_diagnostic()