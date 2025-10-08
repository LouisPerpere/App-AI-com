#!/usr/bin/env python3
"""
DIAGNOSTIC URGENT - Modification Post "Dernière Chance Avant Fermeture" Non Prise en Compte

CONTEXTE: L'utilisateur a tenté de modifier le post "Dernière Chance Avant Fermeture" du 24/09 
mais la modification ne semble pas être prise en compte après avoir cliqué sur "Envoyer".

TESTS CRITIQUES REQUIS:
1. Localiser le post spécifique avec titre "Dernière Chance Avant Fermeture" ou contenant "fermeture"
2. Tester l'endpoint PUT /api/posts/{post_id}/modify avec une demande de modification test
3. Vérifier la sauvegarde en base avec les champs modified_at, modification_status, modification_request
4. Tester le processus AI de modification (appel GPT-4)
5. Validation du workflow complet: modification → sauvegarde → récupération

Credentials: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://post-restore.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class PostModificationDiagnostic:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.target_post = None
        
    def print_header(self, title):
        print(f"\n{'='*80}")
        print(f"🔍 {title}")
        print(f"{'='*80}")
        
    def print_success(self, message):
        print(f"✅ {message}")
        
    def print_error(self, message):
        print(f"❌ {message}")
        
    def print_info(self, message):
        print(f"ℹ️  {message}")
        
    def authenticate(self):
        """Test 1: Authentification avec les credentials fournis"""
        self.print_header("TEST 1: AUTHENTIFICATION")
        
        auth_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json=auth_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Configure headers for subsequent requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                })
                
                self.print_success("Authentification réussie")
                self.print_info(f"User ID: {self.user_id}")
                self.print_info(f"Token: {self.token[:20]}..." if self.token else "No token")
                return True
            else:
                self.print_error(f"Échec authentification: {response.status_code}")
                self.print_error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            self.print_error(f"Erreur authentification: {str(e)}")
            return False
    
    def find_target_post(self):
        """Test 2: Localiser le post spécifique "Dernière Chance Avant Fermeture"""
        self.print_header("TEST 2: LOCALISATION DU POST CIBLE")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/posts/generated", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                
                self.print_success(f"Récupération de {len(posts)} posts générés")
                
                # Rechercher le post avec "Dernière Chance Avant Fermeture" ou "fermeture"
                target_posts = []
                
                for post in posts:
                    title = post.get("title", "").lower()
                    text = post.get("text", "").lower()
                    scheduled_date = post.get("scheduled_date", "")
                    
                    # Recherche par titre ou contenu contenant "fermeture"
                    if "fermeture" in title or "fermeture" in text or "dernière chance" in title or "dernière chance" in text:
                        target_posts.append(post)
                        self.print_info(f"Post trouvé:")
                        self.print_info(f"  ID: {post.get('id')}")
                        self.print_info(f"  Titre: {post.get('title', 'N/A')}")
                        self.print_info(f"  Date programmée: {scheduled_date}")
                        self.print_info(f"  Texte (extrait): {post.get('text', '')[:100]}...")
                
                if target_posts:
                    # Prendre le premier post trouvé ou celui du 24/09 si disponible
                    self.target_post = target_posts[0]
                    
                    # Chercher spécifiquement un post du 24/09 si disponible
                    for post in target_posts:
                        scheduled_date = post.get("scheduled_date", "")
                        if "24" in scheduled_date and "09" in scheduled_date:
                            self.target_post = post
                            self.print_info("Post du 24/09 sélectionné comme cible")
                            break
                    
                    self.print_success(f"Post cible identifié: {self.target_post.get('id')}")
                    self.print_info(f"Titre: {self.target_post.get('title')}")
                    self.print_info(f"Date: {self.target_post.get('scheduled_date')}")
                    return True
                else:
                    self.print_error("Aucun post contenant 'fermeture' ou 'dernière chance' trouvé")
                    
                    # Afficher tous les posts pour diagnostic
                    self.print_info("Posts disponibles:")
                    for i, post in enumerate(posts[:5], 1):  # Afficher les 5 premiers
                        self.print_info(f"  {i}. ID: {post.get('id')} - Titre: {post.get('title', 'N/A')}")
                    
                    return False
            else:
                self.print_error(f"Échec récupération posts: {response.status_code}")
                self.print_error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            self.print_error(f"Erreur localisation post: {str(e)}")
            return False
    
    def test_modification_endpoint(self):
        """Test 3: Tester l'endpoint PUT /api/posts/{post_id}/modify"""
        self.print_header("TEST 3: TEST ENDPOINT MODIFICATION")
        
        if not self.target_post:
            self.print_error("Aucun post cible - impossible de tester la modification")
            return False
        
        post_id = self.target_post.get("id")
        self.print_info(f"Test de modification du post: {post_id}")
        
        # Demande de modification test
        modification_request = {
            "modification_request": "Changer le titre pour 'Offre Spéciale Dernière Minute' et rendre le texte plus engageant avec un appel à l'action plus fort"
        }
        
        try:
            self.print_info("Envoi de la demande de modification...")
            self.print_info(f"Demande: {modification_request['modification_request']}")
            
            response = self.session.put(
                f"{BACKEND_URL}/posts/{post_id}/modify",
                json=modification_request,
                timeout=60  # Timeout étendu pour l'appel AI
            )
            
            self.print_info(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.print_success("Endpoint de modification fonctionne")
                self.print_info(f"Message: {data.get('message', 'N/A')}")
                
                # Vérifier la structure de la réponse
                modified_post = data.get("modified_post", {})
                if modified_post:
                    self.print_success("Données du post modifié reçues:")
                    self.print_info(f"  Nouveau titre: {modified_post.get('title', 'N/A')}")
                    self.print_info(f"  Nouveau texte (extrait): {modified_post.get('text', '')[:100]}...")
                    self.print_info(f"  Hashtags: {modified_post.get('hashtags', [])}")
                    return True, modified_post
                else:
                    self.print_error("Pas de données modified_post dans la réponse")
                    return False, None
                    
            elif response.status_code == 404:
                self.print_error("Post non trouvé (404)")
                self.print_error(f"Response: {response.text}")
                return False, None
            elif response.status_code == 500:
                self.print_error("Erreur serveur (500) - Problème avec l'API OpenAI ou la logique")
                self.print_error(f"Response: {response.text}")
                return False, None
            else:
                self.print_error(f"Échec modification: {response.status_code}")
                self.print_error(f"Response: {response.text}")
                return False, None
                
        except Exception as e:
            self.print_error(f"Erreur test modification: {str(e)}")
            return False, None
    
    def verify_database_persistence(self, expected_changes):
        """Test 4: Vérifier la sauvegarde en base"""
        self.print_header("TEST 4: VÉRIFICATION PERSISTANCE EN BASE")
        
        if not self.target_post:
            self.print_error("Aucun post cible - impossible de vérifier la persistance")
            return False
        
        post_id = self.target_post.get("id")
        
        try:
            # Attendre un peu pour la sauvegarde
            time.sleep(2)
            
            # Récupérer à nouveau les posts pour vérifier la persistance
            response = self.session.get(f"{BACKEND_URL}/posts/generated", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                
                # Trouver le post modifié
                modified_post = None
                for post in posts:
                    if post.get("id") == post_id:
                        modified_post = post
                        break
                
                if modified_post:
                    self.print_success("Post modifié trouvé en base")
                    
                    # Vérifier les changements
                    current_title = modified_post.get("title", "")
                    current_text = modified_post.get("text", "")
                    modified_at = modified_post.get("modified_at", "")
                    
                    self.print_info(f"Titre actuel: {current_title}")
                    self.print_info(f"Texte actuel (extrait): {current_text[:100]}...")
                    self.print_info(f"Modified_at: {modified_at}")
                    
                    # Vérifier si les changements sont persistés
                    changes_persisted = True
                    
                    if expected_changes:
                        expected_title = expected_changes.get("title", "")
                        expected_text = expected_changes.get("text", "")
                        
                        if expected_title and expected_title != current_title:
                            self.print_error(f"Titre non persisté - Attendu: {expected_title}")
                            changes_persisted = False
                        else:
                            self.print_success("Titre correctement persisté")
                        
                        if expected_text and expected_text != current_text:
                            self.print_error("Texte non persisté ou différent")
                            changes_persisted = False
                        else:
                            self.print_success("Texte correctement persisté")
                    
                    if modified_at:
                        self.print_success("Champ modified_at présent - modification enregistrée")
                    else:
                        self.print_error("Champ modified_at manquant")
                        changes_persisted = False
                    
                    return changes_persisted
                else:
                    self.print_error("Post modifié non trouvé en base")
                    return False
            else:
                self.print_error(f"Échec récupération posts pour vérification: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Erreur vérification persistance: {str(e)}")
            return False
    
    def test_ai_integration(self):
        """Test 5: Vérifier l'intégration AI (OpenAI)"""
        self.print_header("TEST 5: VÉRIFICATION INTÉGRATION AI")
        
        # Ce test vérifie si l'API OpenAI est configurée et accessible
        try:
            # Test avec un post simple pour vérifier l'intégration AI
            if not self.target_post:
                self.print_error("Aucun post cible pour tester l'AI")
                return False
            
            post_id = self.target_post.get("id")
            
            # Demande de modification simple pour tester l'AI
            simple_modification = {
                "modification_request": "Ajouter un emoji au début du titre"
            }
            
            self.print_info("Test de l'intégration AI avec une modification simple...")
            
            response = self.session.put(
                f"{BACKEND_URL}/posts/{post_id}/modify",
                json=simple_modification,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                modified_post = data.get("modified_post", {})
                
                if modified_post:
                    new_title = modified_post.get("title", "")
                    original_title = self.target_post.get("title", "")
                    
                    self.print_success("Appel AI réussi")
                    self.print_info(f"Titre original: {original_title}")
                    self.print_info(f"Titre modifié: {new_title}")
                    
                    # Vérifier que l'AI a effectivement modifié le contenu
                    if new_title != original_title:
                        self.print_success("AI a modifié le contenu comme demandé")
                        return True
                    else:
                        self.print_error("AI n'a pas modifié le contenu")
                        return False
                else:
                    self.print_error("Pas de contenu modifié retourné par l'AI")
                    return False
            elif response.status_code == 500:
                response_text = response.text
                if "OpenAI" in response_text or "API key" in response_text:
                    self.print_error("Problème avec l'API OpenAI - Clé API manquante ou invalide")
                else:
                    self.print_error("Erreur serveur lors de l'appel AI")
                self.print_error(f"Détails: {response_text}")
                return False
            else:
                self.print_error(f"Échec test AI: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Erreur test AI: {str(e)}")
            return False
    
    def run_complete_workflow_test(self):
        """Test 6: Validation du workflow complet"""
        self.print_header("TEST 6: WORKFLOW COMPLET MODIFICATION → SAUVEGARDE → RÉCUPÉRATION")
        
        if not self.target_post:
            self.print_error("Aucun post cible pour le workflow complet")
            return False
        
        post_id = self.target_post.get("id")
        original_title = self.target_post.get("title", "")
        original_text = self.target_post.get("text", "")
        
        self.print_info(f"Test workflow complet sur post: {post_id}")
        self.print_info(f"Titre original: {original_title}")
        
        # Étape 1: Modification
        workflow_modification = {
            "modification_request": "Remplacer le titre par 'WORKFLOW TEST - Offre Limitée' et ajouter 'TESTÉ LE " + datetime.now().strftime('%d/%m %H:%M') + "' à la fin du texte"
        }
        
        try:
            self.print_info("Étape 1: Envoi modification...")
            
            response = self.session.put(
                f"{BACKEND_URL}/posts/{post_id}/modify",
                json=workflow_modification,
                timeout=60
            )
            
            if response.status_code != 200:
                self.print_error(f"Échec modification workflow: {response.status_code}")
                return False
            
            modification_data = response.json()
            modified_post_data = modification_data.get("modified_post", {})
            expected_title = modified_post_data.get("title", "")
            expected_text = modified_post_data.get("text", "")
            
            self.print_success("Étape 1 réussie - Modification envoyée")
            self.print_info(f"Nouveau titre attendu: {expected_title}")
            
            # Étape 2: Attendre et vérifier la sauvegarde
            self.print_info("Étape 2: Vérification sauvegarde (attente 3s)...")
            time.sleep(3)
            
            response = self.session.get(f"{BACKEND_URL}/posts/generated", timeout=30)
            
            if response.status_code != 200:
                self.print_error("Échec récupération posts pour vérification workflow")
                return False
            
            posts = response.json().get("posts", [])
            updated_post = None
            
            for post in posts:
                if post.get("id") == post_id:
                    updated_post = post
                    break
            
            if not updated_post:
                self.print_error("Post non trouvé après modification")
                return False
            
            # Étape 3: Validation des changements
            current_title = updated_post.get("title", "")
            current_text = updated_post.get("text", "")
            modified_at = updated_post.get("modified_at", "")
            
            self.print_info("Étape 3: Validation des changements...")
            self.print_info(f"Titre récupéré: {current_title}")
            self.print_info(f"Modified_at: {modified_at}")
            
            # Vérifications finales
            workflow_success = True
            
            if expected_title and current_title == expected_title:
                self.print_success("✅ Titre correctement modifié et persisté")
            else:
                self.print_error(f"❌ Titre non persisté - Attendu: {expected_title}, Trouvé: {current_title}")
                workflow_success = False
            
            if "TESTÉ LE" in current_text:
                self.print_success("✅ Texte correctement modifié avec timestamp")
            else:
                self.print_error("❌ Texte non modifié ou timestamp manquant")
                workflow_success = False
            
            if modified_at:
                self.print_success("✅ Champ modified_at présent")
            else:
                self.print_error("❌ Champ modified_at manquant")
                workflow_success = False
            
            return workflow_success
            
        except Exception as e:
            self.print_error(f"Erreur workflow complet: {str(e)}")
            return False
    
    def run_diagnostic(self):
        """Exécuter le diagnostic complet"""
        self.print_header("DIAGNOSTIC URGENT - MODIFICATION POST NON PRISE EN COMPTE")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Credentials: {TEST_EMAIL} / {TEST_PASSWORD}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Objectif: Diagnostiquer pourquoi la modification du post 'Dernière Chance Avant Fermeture' ne fonctionne pas")
        
        results = {
            "authentication": False,
            "post_found": False,
            "modification_endpoint": False,
            "database_persistence": False,
            "ai_integration": False,
            "complete_workflow": False
        }
        
        # Test 1: Authentification
        if not self.authenticate():
            self.print_error("DIAGNOSTIC ÉCHOUÉ: Impossible de s'authentifier")
            return False
        results["authentication"] = True
        
        # Test 2: Localisation du post
        if not self.find_target_post():
            self.print_error("DIAGNOSTIC ÉCHOUÉ: Post cible non trouvé")
            return False
        results["post_found"] = True
        
        # Test 3: Test endpoint modification
        modification_success, expected_changes = self.test_modification_endpoint()
        results["modification_endpoint"] = modification_success
        
        if not modification_success:
            self.print_error("DIAGNOSTIC ÉCHOUÉ: Endpoint de modification ne fonctionne pas")
            return False
        
        # Test 4: Vérification persistance
        persistence_success = self.verify_database_persistence(expected_changes)
        results["database_persistence"] = persistence_success
        
        # Test 5: Test intégration AI
        ai_success = self.test_ai_integration()
        results["ai_integration"] = ai_success
        
        # Test 6: Workflow complet
        workflow_success = self.run_complete_workflow_test()
        results["complete_workflow"] = workflow_success
        
        # Résumé final
        self.print_header("RÉSUMÉ DU DIAGNOSTIC")
        
        print("RÉSULTATS DES TESTS:")
        for test_name, success in results.items():
            status = "✅ RÉUSSI" if success else "❌ ÉCHOUÉ"
            print(f"  {test_name.replace('_', ' ').title()}: {status}")
        
        # Analyse des problèmes
        failed_tests = [test for test, success in results.items() if not success]
        
        if not failed_tests:
            self.print_success("🎉 TOUS LES TESTS RÉUSSIS - Le système de modification fonctionne correctement")
            print("\n💡 RECOMMANDATIONS:")
            print("   - Le problème pourrait être côté frontend (interface utilisateur)")
            print("   - Vérifier les logs du navigateur pour des erreurs JavaScript")
            print("   - Vérifier que le bouton 'Envoyer' déclenche bien l'appel API")
            print("   - Vérifier la gestion des réponses côté frontend")
        else:
            self.print_error(f"❌ {len(failed_tests)} TEST(S) ÉCHOUÉ(S)")
            print("\n🔍 ANALYSE DES PROBLÈMES:")
            
            if not results["modification_endpoint"]:
                print("   - L'endpoint PUT /api/posts/{id}/modify ne fonctionne pas")
                print("   - Vérifier la configuration OpenAI API key")
                print("   - Vérifier les logs backend pour les erreurs")
            
            if not results["database_persistence"]:
                print("   - Les modifications ne sont pas sauvegardées en base")
                print("   - Problème possible avec MongoDB ou la logique de sauvegarde")
            
            if not results["ai_integration"]:
                print("   - L'intégration OpenAI ne fonctionne pas")
                print("   - Vérifier OPENAI_API_KEY dans les variables d'environnement")
                print("   - Vérifier les quotas et limites de l'API OpenAI")
            
            if not results["complete_workflow"]:
                print("   - Le workflow complet modification→sauvegarde→récupération échoue")
                print("   - Problème de synchronisation ou de persistance")
        
        return len(failed_tests) == 0

def main():
    """Point d'entrée principal"""
    diagnostic = PostModificationDiagnostic()
    success = diagnostic.run_diagnostic()
    
    if success:
        print("\n🎉 DIAGNOSTIC TERMINÉ AVEC SUCCÈS")
        sys.exit(0)
    else:
        print("\n💥 DIAGNOSTIC RÉVÈLE DES PROBLÈMES")
        sys.exit(1)

if __name__ == "__main__":
    main()