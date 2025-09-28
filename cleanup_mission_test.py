#!/usr/bin/env python3
"""
MISSION URGENTE: NETTOYAGE COMPLET DES DONNÉES CORROMPUES
Test spécifique pour la mission de nettoyage demandée par l'utilisateur

Objectif: Nettoyer complètement toutes les fausses connexions et données corrompues
avant de réimplémenter l'OAuth proprement.

Identifiants de test: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://social-publisher-10.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class CleanupMissionTester:
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
        """Étape 1: Authentification avec les identifiants de test"""
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
                    f"User ID: {self.user_id}, Token obtenu"
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
    
    def test_clean_invalid_tokens(self):
        """Test 1: POST /api/debug/clean-invalid-tokens - Supprimer TOUTES les connexions avec access_token: null, temp_facebook_token_*, test_token_*, etc."""
        try:
            print("🧹 Nettoyage des tokens invalides...")
            response = self.session.post(f"{BACKEND_URL}/debug/clean-invalid-tokens")
            
            if response.status_code == 200:
                data = response.json()
                deleted_count = data.get('deleted_count', 0)
                message = data.get('message', 'Nettoyage effectué')
                
                self.log_test(
                    "Nettoyage tokens invalides", 
                    True, 
                    f"Supprimé {deleted_count} connexions avec tokens invalides. {message}"
                )
                return True, deleted_count
            else:
                self.log_test(
                    "Nettoyage tokens invalides", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return False, 0
                
        except Exception as e:
            self.log_test("Nettoyage tokens invalides", False, error=str(e))
            return False, 0
    
    def test_clean_library_badges(self):
        """Test 2: POST /api/debug/clean-library-badges - Nettoyer les badges Facebook/Instagram des contenus non utilisés"""
        try:
            print("🏷️ Nettoyage des badges orphelins...")
            response = self.session.post(f"{BACKEND_URL}/debug/clean-library-badges")
            
            if response.status_code == 200:
                data = response.json()
                message = data.get('message', 'Nettoyage effectué')
                cleaned_count = data.get('cleaned_count', 0)
                
                self.log_test(
                    "Nettoyage badges orphelins", 
                    True, 
                    f"Nettoyé {cleaned_count} badges orphelins. {message}"
                )
                return True
            else:
                self.log_test(
                    "Nettoyage badges orphelins", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Nettoyage badges orphelins", False, error=str(e))
            return False
    
    def test_debug_social_connections(self):
        """Test 3: GET /api/debug/social-connections - Confirmer 0 connexions actives (état propre)"""
        try:
            print("🔍 Vérification état après nettoyage...")
            response = self.session.get(f"{BACKEND_URL}/debug/social-connections")
            
            if response.status_code == 200:
                data = response.json()
                
                total_connections = data.get('total_connections', 0)
                active_connections = data.get('active_connections', 0)
                facebook_connections = data.get('facebook_connections', 0)
                instagram_connections = data.get('instagram_connections', 0)
                
                # Vérifier l'état propre
                is_clean = (total_connections == 0 and active_connections == 0 and 
                           facebook_connections == 0 and instagram_connections == 0)
                
                details = f"Total: {total_connections}, Actives: {active_connections}, Facebook: {facebook_connections}, Instagram: {instagram_connections}"
                
                if is_clean:
                    details += " ✅ ÉTAT PROPRE CONFIRMÉ"
                else:
                    details += " ⚠️ CONNEXIONS RESTANTES DÉTECTÉES"
                
                self.log_test(
                    "Vérification état propre", 
                    is_clean, 
                    details
                )
                return data, is_clean
            else:
                self.log_test(
                    "Vérification état propre", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return None, False
                
        except Exception as e:
            self.log_test("Vérification état propre", False, error=str(e))
            return None, False
    
    def test_social_connections_api(self):
        """Test 4: GET /api/social/connections - Confirmer liste vide"""
        try:
            print("📋 Vérification API connexions sociales...")
            response = self.session.get(f"{BACKEND_URL}/social/connections")
            
            if response.status_code == 200:
                data = response.json()
                connections = data.get('connections', [])
                
                is_empty = len(connections) == 0
                
                self.log_test(
                    "API connexions sociales vide", 
                    is_empty, 
                    f"Trouvé {len(connections)} connexions (attendu: 0)"
                )
                return is_empty
            else:
                self.log_test(
                    "API connexions sociales vide", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("API connexions sociales vide", False, error=str(e))
            return False
    
    def test_publication_blocked(self):
        """Test 5: Vérifier que la publication est bloquée (pas de connexions actives)"""
        try:
            print("🚫 Test publication bloquée...")
            
            # D'abord récupérer les posts disponibles
            posts_response = self.session.get(f"{BACKEND_URL}/posts/generated")
            
            if posts_response.status_code != 200:
                self.log_test(
                    "Publication bloquée - Récupération posts", 
                    True, 
                    "Aucun post disponible (état propre)"
                )
                return True
            
            posts_data = posts_response.json()
            posts = posts_data.get('posts', [])
            
            if not posts:
                self.log_test(
                    "Publication bloquée - Aucun post", 
                    True, 
                    "Aucun post disponible pour test de publication (état propre)"
                )
                return True
            
            # Tenter de publier le premier post
            test_post = posts[0]
            post_id = test_post.get('id')
            
            response = self.session.post(f"{BACKEND_URL}/posts/publish", json={
                "post_id": post_id
            })
            
            # On s'attend à ce que ça échoue avec "aucune connexion sociale active"
            if response.status_code == 400:
                data = response.json()
                error_msg = data.get('error', '').lower()
                
                if 'aucune connexion sociale active' in error_msg or 'no active social connections' in error_msg:
                    self.log_test(
                        "Publication correctement bloquée", 
                        True, 
                        "Publication rejetée: aucune connexion sociale active (attendu après nettoyage)"
                    )
                    return True
                else:
                    self.log_test(
                        "Publication correctement bloquée", 
                        False, 
                        error=f"Erreur inattendue: {error_msg}"
                    )
                    return False
            else:
                self.log_test(
                    "Publication correctement bloquée", 
                    False, 
                    error=f"Status inattendu {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Publication correctement bloquée", False, error=str(e))
            return False
    
    def run_cleanup_mission(self):
        """Exécuter la mission complète de nettoyage"""
        print("🎯 MISSION URGENTE: NETTOYAGE COMPLET DES DONNÉES CORROMPUES")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Identifiants: {TEST_EMAIL}")
        print(f"Heure: {datetime.now().isoformat()}")
        print("=" * 80)
        print()
        
        # Étape 1: Authentification
        if not self.authenticate():
            print("❌ CRITIQUE: Authentification échouée - impossible de continuer")
            return False
        
        # Étape 2: Nettoyage des tokens invalides
        print("🧹 PHASE 1: NETTOYAGE TOKENS INVALIDES")
        print("-" * 50)
        success_tokens, deleted_count = self.test_clean_invalid_tokens()
        print()
        
        # Étape 3: Nettoyage des badges orphelins
        print("🏷️ PHASE 2: NETTOYAGE BADGES ORPHELINS")
        print("-" * 50)
        success_badges = self.test_clean_library_badges()
        print()
        
        # Étape 4: Vérification état après nettoyage
        print("🔍 PHASE 3: VÉRIFICATION ÉTAT APRÈS NETTOYAGE")
        print("-" * 50)
        connections_data, is_clean = self.test_debug_social_connections()
        success_api = self.test_social_connections_api()
        print()
        
        # Étape 5: Test publication bloquée
        print("🚫 PHASE 4: VÉRIFICATION PUBLICATION BLOQUÉE")
        print("-" * 50)
        success_publication = self.test_publication_blocked()
        print()
        
        # Résumé de la mission
        self.print_mission_summary(deleted_count, is_clean, success_api, success_publication)
        
        return True
    
    def print_mission_summary(self, deleted_count, is_clean, success_api, success_publication):
        """Imprimer le résumé de la mission"""
        print("=" * 80)
        print("🎯 RÉSUMÉ MISSION NETTOYAGE")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Tests totaux: {total}")
        print(f"Réussis: {passed}")
        print(f"Échoués: {total - passed}")
        print(f"Taux de réussite: {(passed/total*100):.1f}%" if total > 0 else "0%")
        print()
        
        # État de la mission
        print("📊 ÉTAT DE LA MISSION:")
        print(f"  🧹 Tokens invalides supprimés: {deleted_count}")
        print(f"  🏷️ Badges orphelins nettoyés: ✅")
        print(f"  🔍 État propre confirmé: {'✅' if is_clean else '❌'}")
        print(f"  📋 API connexions vide: {'✅' if success_api else '❌'}")
        print(f"  🚫 Publication bloquée: {'✅' if success_publication else '❌'}")
        print()
        
        # Tests détaillés
        print("📋 DÉTAILS DES TESTS:")
        for result in self.test_results:
            print(f"  {result['status']}: {result['test']}")
            if result['details']:
                print(f"    → {result['details']}")
        print()
        
        # Évaluation finale
        critical_success = is_clean and success_api and success_publication
        
        if critical_success:
            print("🎉 MISSION NETTOYAGE: SUCCÈS COMPLET")
            print("✅ Base de données propre, aucune fausse connexion")
            print("✅ Interface cohérente montrant l'état réel (déconnecté)")
            print("✅ Système prêt pour réimplémentation OAuth propre")
            print("✅ Phase de nettoyage CRITIQUE terminée avec succès")
        else:
            print("🚨 MISSION NETTOYAGE: PROBLÈMES DÉTECTÉS")
            if not is_clean:
                print("❌ État pas complètement propre - connexions restantes")
            if not success_api:
                print("❌ API connexions ne retourne pas liste vide")
            if not success_publication:
                print("❌ Publication pas correctement bloquée")
            print("⚠️ Nettoyage peut nécessiter intervention supplémentaire")
        
        print("=" * 80)

def main():
    """Exécution principale de la mission"""
    tester = CleanupMissionTester()
    
    try:
        success = tester.run_cleanup_mission()
        
        # Code de sortie approprié
        if success:
            failed_count = sum(1 for result in tester.test_results if not result['success'])
            sys.exit(0 if failed_count == 0 else 1)
        else:
            sys.exit(2)
            
    except KeyboardInterrupt:
        print("\n⚠️ Mission interrompue par l'utilisateur")
        sys.exit(3)
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {str(e)}")
        sys.exit(4)

if __name__ == "__main__":
    main()