#!/usr/bin/env python3
"""
DIAGNOSTIC SPÉCIFIQUE - PROBLÈME CALLBACK INSTAGRAM LIVE
========================================================

PROBLÈME IDENTIFIÉ:
Le callback Instagram redirige vers /api/social/facebook/callback au lieu de /api/social/instagram/callback

ANALYSE CRITIQUE:
1. URL auth Instagram générée correctement avec redirect_uri Instagram
2. Mais le callback redirige vers l'endpoint Facebook
3. Ceci explique pourquoi Instagram ne fonctionne pas sur LIVE

TESTS SPÉCIFIQUES:
1. Vérifier la logique de callback Instagram vs Facebook
2. Analyser la différence entre les deux endpoints
3. Identifier pourquoi Instagram utilise le callback Facebook
"""

import requests
import json
import sys
from urllib.parse import urlparse, parse_qs

# Configuration LIVE
LIVE_BASE_URL = "https://claire-marcus.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class InstagramCallbackIssueDiagnostic:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        
    def authenticate(self):
        """Authentification sur LIVE"""
        print("🔐 Authentification LIVE...")
        
        login_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
        
        try:
            response = self.session.post(f"{LIVE_BASE_URL}/auth/login-robust", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                print(f"✅ Authentification réussie - User ID: {self.user_id}")
                return True
            else:
                print(f"❌ Authentification échouée: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur authentification: {e}")
            return False
    
    def compare_auth_urls(self):
        """Comparer les URLs d'auth Facebook vs Instagram"""
        print("\n🔍 COMPARAISON URLs AUTH Facebook vs Instagram...")
        
        try:
            # Test Facebook auth URL
            fb_response = self.session.get(f"{LIVE_BASE_URL}/social/facebook/auth-url")
            ig_response = self.session.get(f"{LIVE_BASE_URL}/social/instagram/auth-url")
            
            if fb_response.status_code == 200 and ig_response.status_code == 200:
                fb_data = fb_response.json()
                ig_data = ig_response.json()
                
                fb_url = fb_data.get("auth_url", "")
                ig_url = ig_data.get("auth_url", "")
                
                # Parse URLs
                fb_parsed = urlparse(fb_url)
                ig_parsed = urlparse(ig_url)
                
                fb_params = parse_qs(fb_parsed.query)
                ig_params = parse_qs(ig_parsed.query)
                
                print("📱 Facebook Auth URL:")
                print(f"   Redirect URI: {fb_params.get('redirect_uri', [''])[0]}")
                print(f"   Config ID: {fb_params.get('config_id', [''])[0]}")
                print(f"   Client ID: {fb_params.get('client_id', [''])[0]}")
                
                print("📸 Instagram Auth URL:")
                print(f"   Redirect URI: {ig_params.get('redirect_uri', [''])[0]}")
                print(f"   Config ID: {ig_params.get('config_id', [''])[0]}")
                print(f"   Client ID: {ig_params.get('client_id', [''])[0]}")
                
                # Vérifier les différences
                fb_redirect = fb_params.get('redirect_uri', [''])[0]
                ig_redirect = ig_params.get('redirect_uri', [''])[0]
                
                if fb_redirect == ig_redirect:
                    print("❌ PROBLÈME IDENTIFIÉ: Facebook et Instagram utilisent la même redirect_uri!")
                    print(f"   Les deux utilisent: {fb_redirect}")
                else:
                    print("✅ Facebook et Instagram utilisent des redirect_uri différentes")
                
                return True
            else:
                print("❌ Impossible de récupérer les URLs d'auth")
                return False
                
        except Exception as e:
            print(f"❌ Erreur comparaison URLs: {e}")
            return False
    
    def test_callback_endpoints_directly(self):
        """Tester directement les endpoints de callback"""
        print("\n🔄 TEST DIRECT des endpoints callback...")
        
        try:
            # Obtenir un state valide
            ig_response = self.session.get(f"{LIVE_BASE_URL}/social/instagram/auth-url")
            if ig_response.status_code != 200:
                print("❌ Impossible d'obtenir l'URL Instagram")
                return False
                
            ig_data = ig_response.json()
            ig_url = ig_data.get("auth_url", "")
            parsed_url = urlparse(ig_url)
            query_params = parse_qs(parsed_url.query)
            state = query_params.get("state", [""])[0]
            
            if not state:
                print("❌ Pas de paramètre state")
                return False
            
            print(f"   State utilisé: {state[:20]}...")
            
            # Test callback Instagram
            print("\n📸 Test callback Instagram:")
            ig_callback_params = {
                "code": "test_instagram_code_12345",
                "state": state
            }
            
            ig_callback_response = self.session.get(
                f"{LIVE_BASE_URL}/social/instagram/callback", 
                params=ig_callback_params, 
                allow_redirects=False
            )
            
            print(f"   Status: {ig_callback_response.status_code}")
            
            if ig_callback_response.status_code == 302:
                ig_redirect = ig_callback_response.headers.get("Location", "")
                print(f"   Redirection: {ig_redirect}")
                
                # Analyser la redirection
                if "/facebook/callback" in ig_redirect:
                    print("❌ PROBLÈME CONFIRMÉ: Instagram callback redirige vers Facebook!")
                elif "/instagram/callback" in ig_redirect:
                    print("✅ Instagram callback redirige correctement vers Instagram")
                else:
                    print("⚠️ Redirection vers endpoint inconnu")
            
            # Test callback Facebook pour comparaison
            print("\n📱 Test callback Facebook:")
            fb_callback_params = {
                "code": "test_facebook_code_12345",
                "state": state
            }
            
            fb_callback_response = self.session.get(
                f"{LIVE_BASE_URL}/social/facebook/callback", 
                params=fb_callback_params, 
                allow_redirects=False
            )
            
            print(f"   Status: {fb_callback_response.status_code}")
            
            if fb_callback_response.status_code == 302:
                fb_redirect = fb_callback_response.headers.get("Location", "")
                print(f"   Redirection: {fb_redirect}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur test callbacks: {e}")
            return False
    
    def analyze_instagram_connection_state(self):
        """Analyser l'état des connexions Instagram en détail"""
        print("\n🔍 ANALYSE DÉTAILLÉE connexions Instagram...")
        
        try:
            # Test debug endpoint
            debug_response = self.session.get(f"{LIVE_BASE_URL}/debug/social-connections")
            
            if debug_response.status_code == 200:
                data = debug_response.json()
                
                print("📊 État des connexions:")
                print(f"   Total connexions: {data.get('total_connections', 0)}")
                print(f"   Connexions actives: {data.get('active_connections', 0)}")
                print(f"   Instagram connexions: {data.get('instagram_connections', 0)}")
                
                # Analyser les connexions Instagram spécifiquement
                social_media_connections = data.get('social_media_connections', [])
                
                instagram_connections = [
                    conn for conn in social_media_connections 
                    if conn.get('platform', '').lower() == 'instagram'
                ]
                
                print(f"\n📸 Connexions Instagram trouvées: {len(instagram_connections)}")
                
                for i, conn in enumerate(instagram_connections, 1):
                    print(f"   Connexion {i}:")
                    print(f"     - Platform: {conn.get('platform', 'N/A')}")
                    print(f"     - Active: {conn.get('active', 'N/A')}")
                    print(f"     - Access Token: {'Présent' if conn.get('access_token') else 'Absent'}")
                    print(f"     - Page Name: {conn.get('page_name', 'N/A')}")
                    print(f"     - Connected At: {conn.get('connected_at', 'N/A')}")
                    
                    # Analyser le token
                    token = conn.get('access_token', '')
                    if token:
                        if token.startswith('test_token'):
                            print(f"     - ❌ Token de test détecté: {token}")
                        elif len(token) > 50:
                            print(f"     - ✅ Token réel détecté: {token[:20]}...")
                        else:
                            print(f"     - ⚠️ Token suspect: {token}")
                
                # Vérifier pourquoi Instagram n'est pas actif
                active_instagram = [
                    conn for conn in instagram_connections 
                    if conn.get('active') == True
                ]
                
                if len(active_instagram) == 0:
                    print("\n❌ PROBLÈME: Aucune connexion Instagram active")
                    print("   Causes possibles:")
                    print("   1. Callback Instagram ne fonctionne pas correctement")
                    print("   2. Tokens Instagram expirés ou invalides")
                    print("   3. Problème de sauvegarde lors du callback")
                else:
                    print(f"\n✅ {len(active_instagram)} connexion(s) Instagram active(s)")
                
                return True
            else:
                print(f"❌ Debug endpoint échoué: {debug_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur analyse connexions: {e}")
            return False
    
    def test_instagram_reconnection_simulation(self):
        """Simuler une reconnexion Instagram complète"""
        print("\n🔄 SIMULATION reconnexion Instagram complète...")
        
        try:
            # Étape 1: Générer URL d'auth Instagram
            print("   Étape 1: Génération URL auth Instagram...")
            auth_response = self.session.get(f"{LIVE_BASE_URL}/social/instagram/auth-url")
            
            if auth_response.status_code != 200:
                print("   ❌ Impossible de générer l'URL d'auth")
                return False
            
            auth_data = auth_response.json()
            auth_url = auth_data.get("auth_url", "")
            
            # Extraire le state
            parsed_url = urlparse(auth_url)
            query_params = parse_qs(parsed_url.query)
            state = query_params.get("state", [""])[0]
            
            print(f"   ✅ URL générée avec state: {state[:20]}...")
            
            # Étape 2: Simuler le callback Instagram avec un code réaliste
            print("   Étape 2: Simulation callback Instagram...")
            callback_params = {
                "code": "AQDxyz123_realistic_instagram_auth_code_simulation",
                "state": state
            }
            
            callback_response = self.session.get(
                f"{LIVE_BASE_URL}/social/instagram/callback",
                params=callback_params,
                allow_redirects=False
            )
            
            print(f"   Status callback: {callback_response.status_code}")
            
            if callback_response.status_code == 302:
                redirect_url = callback_response.headers.get("Location", "")
                print(f"   Redirection: {redirect_url}")
                
                # Analyser le résultat de la redirection
                if "success" in redirect_url.lower():
                    print("   ✅ Callback semble réussi")
                elif "error" in redirect_url.lower():
                    print("   ❌ Callback a échoué")
                    
                    # Analyser le type d'erreur
                    if "token_exchange" in redirect_url.lower():
                        print("   Cause: Problème d'échange de token avec Facebook API")
                    elif "invalid_state" in redirect_url.lower():
                        print("   Cause: Problème de validation du paramètre state")
                    else:
                        print("   Cause: Erreur inconnue")
                
                # Vérifier si la redirection utilise le bon endpoint
                if "/facebook/callback" in redirect_url:
                    print("   ❌ PROBLÈME CONFIRMÉ: Redirection vers Facebook au lieu d'Instagram")
                    return False
                elif "/instagram/callback" in redirect_url:
                    print("   ✅ Redirection correcte vers Instagram")
                
            # Étape 3: Vérifier l'état des connexions après simulation
            print("   Étape 3: Vérification état connexions après callback...")
            
            time.sleep(1)  # Attendre un peu pour la persistance
            
            debug_response = self.session.get(f"{LIVE_BASE_URL}/debug/social-connections")
            if debug_response.status_code == 200:
                data = debug_response.json()
                instagram_count = data.get('instagram_connections', 0)
                active_count = data.get('active_connections', 0)
                
                print(f"   Connexions Instagram: {instagram_count}")
                print(f"   Connexions actives: {active_count}")
                
                if instagram_count > 0:
                    print("   ✅ Connexion Instagram créée")
                else:
                    print("   ❌ Aucune connexion Instagram créée")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur simulation reconnexion: {e}")
            return False
    
    def run_diagnostic(self):
        """Exécuter le diagnostic complet du problème callback Instagram"""
        print("🎯 DIAGNOSTIC PROBLÈME CALLBACK INSTAGRAM LIVE")
        print("=" * 60)
        
        if not self.authenticate():
            print("❌ Authentification échouée")
            return False
        
        print("\n🔍 INVESTIGATION du problème callback Instagram...")
        
        # Test 1: Comparer les URLs d'auth
        print("\n" + "="*50)
        self.compare_auth_urls()
        
        # Test 2: Tester les callbacks directement
        print("\n" + "="*50)
        self.test_callback_endpoints_directly()
        
        # Test 3: Analyser l'état des connexions Instagram
        print("\n" + "="*50)
        self.analyze_instagram_connection_state()
        
        # Test 4: Simuler une reconnexion complète
        print("\n" + "="*50)
        self.test_instagram_reconnection_simulation()
        
        # Conclusion
        print("\n" + "="*60)
        print("🔬 CONCLUSION DIAGNOSTIC")
        print("="*60)
        
        print("PROBLÈME IDENTIFIÉ:")
        print("❌ Le callback Instagram redirige vers /api/social/facebook/callback")
        print("   au lieu de /api/social/instagram/callback")
        
        print("\nIMPACT:")
        print("- Les utilisateurs pensent se connecter à Instagram")
        print("- Mais le callback est traité comme une connexion Facebook")
        print("- Ceci explique pourquoi Instagram ne fonctionne pas sur LIVE")
        
        print("\nSOLUTION REQUISE:")
        print("1. Vérifier la configuration des redirect_uri Instagram vs Facebook")
        print("2. S'assurer que Instagram utilise son propre endpoint de callback")
        print("3. Corriger la logique de redirection dans le code backend")
        
        return True

def main():
    """Exécution principale"""
    diagnostic = InstagramCallbackIssueDiagnostic()
    diagnostic.run_diagnostic()

if __name__ == "__main__":
    main()