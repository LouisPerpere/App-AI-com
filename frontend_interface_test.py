#!/usr/bin/env python3
"""
Test de l'interface frontend - Vérification que les boutons affichent "Connecter" 
après le nettoyage des données corrompues

Ce test vérifie les endpoints que le frontend utilise pour déterminer l'état des connexions
et s'assurer que l'interface reflète l'état réel (aucune connexion).
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://post-restore.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class FrontendInterfaceTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        status = "✅ RÉUSSI" if success else "❌ ÉCHEC"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Détails: {details}")
        if error:
            print(f"   Erreur: {error}")
        print()
        
    def authenticate(self):
        """Authentification"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login-robust", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                
                self.log_test(
                    "Authentification", 
                    True, 
                    f"User ID: {self.user_id}"
                )
                return True
            else:
                self.log_test(
                    "Authentification", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Authentification", False, error=str(e))
            return False
    
    def test_social_connections_status(self):
        """Test l'endpoint que le frontend utilise pour afficher l'état des connexions"""
        try:
            response = self.session.get(f"{BACKEND_URL}/social/connections")
            
            if response.status_code == 200:
                data = response.json()
                connections = data.get('connections', [])
                
                # Analyser les connexions par plateforme
                facebook_connected = any(conn.get('platform') == 'facebook' and conn.get('active', False) for conn in connections)
                instagram_connected = any(conn.get('platform') == 'instagram' and conn.get('active', False) for conn in connections)
                
                # L'interface devrait montrer "Connecter" pour les deux plateformes
                should_show_connect_facebook = not facebook_connected
                should_show_connect_instagram = not instagram_connected
                
                details = f"Facebook connecté: {facebook_connected}, Instagram connecté: {instagram_connected}"
                details += f" → Boutons devraient afficher: Facebook='{'Connecter' if should_show_connect_facebook else 'Connecté'}', Instagram='{'Connecter' if should_show_connect_instagram else 'Connecté'}'"
                
                # Test réussi si les deux plateformes montrent "Connecter"
                success = should_show_connect_facebook and should_show_connect_instagram
                
                self.log_test(
                    "État connexions pour interface", 
                    success, 
                    details
                )
                return success, facebook_connected, instagram_connected
            else:
                self.log_test(
                    "État connexions pour interface", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return False, None, None
                
        except Exception as e:
            self.log_test("État connexions pour interface", False, error=str(e))
            return False, None, None
    
    def test_facebook_auth_url_generation(self):
        """Test génération URL d'authentification Facebook (bouton Connecter)"""
        try:
            response = self.session.get(f"{BACKEND_URL}/social/facebook/auth-url")
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get('auth_url', '')
                
                # Vérifier que l'URL contient les paramètres nécessaires
                required_params = ['client_id=', 'redirect_uri=', 'response_type=', 'scope=']
                missing_params = [param for param in required_params if param not in auth_url]
                
                if not missing_params and 'facebook.com' in auth_url:
                    self.log_test(
                        "Génération URL Facebook (bouton Connecter)", 
                        True, 
                        "URL d'authentification Facebook générée correctement"
                    )
                    return True
                else:
                    self.log_test(
                        "Génération URL Facebook (bouton Connecter)", 
                        False, 
                        error=f"URL invalide ou paramètres manquants: {missing_params}"
                    )
                    return False
            else:
                self.log_test(
                    "Génération URL Facebook (bouton Connecter)", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Génération URL Facebook (bouton Connecter)", False, error=str(e))
            return False
    
    def test_instagram_auth_url_generation(self):
        """Test génération URL d'authentification Instagram (bouton Connecter)"""
        try:
            response = self.session.get(f"{BACKEND_URL}/social/instagram/auth-url")
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get('auth_url', '')
                
                # Vérifier que l'URL contient les paramètres nécessaires
                required_params = ['client_id=', 'redirect_uri=', 'response_type=', 'scope=']
                missing_params = [param for param in required_params if param not in auth_url]
                
                if not missing_params and 'facebook.com' in auth_url:  # Instagram utilise Facebook OAuth
                    self.log_test(
                        "Génération URL Instagram (bouton Connecter)", 
                        True, 
                        "URL d'authentification Instagram générée correctement"
                    )
                    return True
                else:
                    self.log_test(
                        "Génération URL Instagram (bouton Connecter)", 
                        False, 
                        error=f"URL invalide ou paramètres manquants: {missing_params}"
                    )
                    return False
            else:
                self.log_test(
                    "Génération URL Instagram (bouton Connecter)", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Génération URL Instagram (bouton Connecter)", False, error=str(e))
            return False
    
    def test_business_profile_access(self):
        """Test accès au profil business (nécessaire pour l'interface)"""
        try:
            response = self.session.get(f"{BACKEND_URL}/business-profile")
            
            if response.status_code == 200:
                data = response.json()
                business_name = data.get('business_name')
                
                self.log_test(
                    "Accès profil business", 
                    True, 
                    f"Profil accessible, business_name: {business_name or 'Non défini'}"
                )
                return True
            else:
                self.log_test(
                    "Accès profil business", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Accès profil business", False, error=str(e))
            return False
    
    def test_posts_generation_blocked(self):
        """Test que la génération de posts est bloquée (pas de connexions actives)"""
        try:
            # Tenter de générer des posts
            response = self.session.post(f"{BACKEND_URL}/posts/generate", json={
                "target_month": "octobre_2025",
                "posts_per_platform": 2
            })
            
            # On s'attend à ce que ça échoue car pas de connexions sociales
            if response.status_code == 400:
                data = response.json()
                error_msg = data.get('error', '').lower()
                
                if 'aucune plateforme sociale connectée' in error_msg or 'no social platforms' in error_msg:
                    self.log_test(
                        "Génération posts bloquée", 
                        True, 
                        "Génération correctement bloquée: aucune plateforme sociale connectée"
                    )
                    return True
                else:
                    self.log_test(
                        "Génération posts bloquée", 
                        False, 
                        error=f"Erreur inattendue: {error_msg}"
                    )
                    return False
            else:
                self.log_test(
                    "Génération posts bloquée", 
                    False, 
                    error=f"Status inattendu {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Génération posts bloquée", False, error=str(e))
            return False
    
    def run_frontend_interface_tests(self):
        """Exécuter tous les tests d'interface frontend"""
        print("🖥️ TEST INTERFACE FRONTEND - VÉRIFICATION BOUTONS 'CONNECTER'")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Identifiants: {TEST_EMAIL}")
        print(f"Heure: {datetime.now().isoformat()}")
        print("=" * 80)
        print()
        
        # Authentification
        if not self.authenticate():
            print("❌ CRITIQUE: Authentification échouée")
            return False
        
        # Test état des connexions
        print("🔗 PHASE 1: ÉTAT DES CONNEXIONS SOCIALES")
        print("-" * 50)
        success_connections, facebook_connected, instagram_connected = self.test_social_connections_status()
        print()
        
        # Test génération URLs d'authentification
        print("🔗 PHASE 2: GÉNÉRATION URLS AUTHENTIFICATION")
        print("-" * 50)
        success_facebook_url = self.test_facebook_auth_url_generation()
        success_instagram_url = self.test_instagram_auth_url_generation()
        print()
        
        # Test accès profil business
        print("👤 PHASE 3: ACCÈS PROFIL BUSINESS")
        print("-" * 50)
        success_profile = self.test_business_profile_access()
        print()
        
        # Test génération posts bloquée
        print("📝 PHASE 4: GÉNÉRATION POSTS BLOQUÉE")
        print("-" * 50)
        success_generation = self.test_posts_generation_blocked()
        print()
        
        # Résumé
        self.print_interface_summary(facebook_connected, instagram_connected)
        
        return True
    
    def print_interface_summary(self, facebook_connected, instagram_connected):
        """Imprimer le résumé des tests d'interface"""
        print("=" * 80)
        print("🖥️ RÉSUMÉ TESTS INTERFACE FRONTEND")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Tests totaux: {total}")
        print(f"Réussis: {passed}")
        print(f"Échoués: {total - passed}")
        print(f"Taux de réussite: {(passed/total*100):.1f}%" if total > 0 else "0%")
        print()
        
        # État de l'interface
        print("🖥️ ÉTAT INTERFACE ATTENDU:")
        facebook_button = "Connecter" if not facebook_connected else "Connecté"
        instagram_button = "Connecter" if not instagram_connected else "Connecté"
        
        print(f"  📘 Bouton Facebook: '{facebook_button}'")
        print(f"  📷 Bouton Instagram: '{instagram_button}'")
        print(f"  🚫 Génération posts: Bloquée (pas de connexions)")
        print(f"  🔗 URLs d'authentification: Disponibles")
        print()
        
        # Tests détaillés
        print("📋 RÉSULTATS DÉTAILLÉS:")
        for result in self.test_results:
            print(f"  {result['status']}: {result['test']}")
            if result['details']:
                print(f"    → {result['details']}")
        print()
        
        # Évaluation finale
        interface_coherent = not facebook_connected and not instagram_connected
        
        if interface_coherent and passed == total:
            print("🎉 INTERFACE FRONTEND: COHÉRENTE")
            print("✅ Les boutons affichent maintenant 'Connecter' (pas 'Connecté')")
            print("✅ L'interface reflète l'état réel (aucune connexion)")
            print("✅ URLs d'authentification disponibles pour reconnexion")
            print("✅ Génération posts correctement bloquée")
            print("✅ Interface prête pour réimplémentation OAuth propre")
        else:
            print("🚨 INTERFACE FRONTEND: PROBLÈMES DÉTECTÉS")
            if facebook_connected or instagram_connected:
                print("❌ Connexions encore actives - boutons peuvent montrer 'Connecté'")
            if passed != total:
                print(f"❌ {total - passed} tests d'interface échoués")
            print("⚠️ Interface peut ne pas refléter l'état réel")
        
        print("=" * 80)

def main():
    """Exécution principale des tests d'interface"""
    tester = FrontendInterfaceTester()
    
    try:
        success = tester.run_frontend_interface_tests()
        
        # Code de sortie approprié
        if success:
            failed_count = sum(1 for result in tester.test_results if not result['success'])
            sys.exit(0 if failed_count == 0 else 1)
        else:
            sys.exit(2)
            
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrompus par l'utilisateur")
        sys.exit(3)
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {str(e)}")
        sys.exit(4)

if __name__ == "__main__":
    main()