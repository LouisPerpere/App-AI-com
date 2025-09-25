#!/usr/bin/env python3
"""
DIAGNOSTIC URGENT - Post Modifié Non Affiché + Date Publication
Test spécifique pour diagnostiquer les problèmes de modification de posts identifiés par l'utilisateur.

PROBLÈMES RAPPORTÉS:
1. L'utilisateur voit le spinner de modification, mais après completion, c'est toujours l'ancien post qui s'affiche
2. Les demandes de modification de jour de publication ne semblent pas prises en compte

TESTS CRITIQUES REQUIS:
- Test 1: Vérification réponse endpoint modification
- Test 2: Test spécifique modification date  
- Test 3: Vérification format réponse modification
- Test 4: Validation complète post-modification

Credentials: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import sys
from datetime import datetime, timedelta
import time

# Configuration
BACKEND_URL = "https://post-validator.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class PostModificationDiagnostic:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.test_post_id = None
        
    def authenticate(self):
        """Authentification avec les credentials fournis"""
        print("🔐 ÉTAPE 1: Authentification...")
        
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
                
                print(f"✅ Authentification réussie")
                print(f"   User ID: {self.user_id}")
                print(f"   Token: {self.token[:20]}..." if self.token else "No token")
                return True
            else:
                print(f"❌ Échec authentification: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur authentification: {str(e)}")
            return False
    
    def get_existing_posts(self):
        """Récupérer les posts existants pour les tests"""
        print("\n📋 ÉTAPE 2: Récupération des posts existants...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/posts/generated", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                
                print(f"✅ GET /api/posts/generated réussi")
                print(f"   Nombre de posts trouvés: {len(posts)}")
                
                if posts:
                    # Prendre le premier post pour les tests
                    test_post = posts[0]
                    self.test_post_id = test_post.get("id")
                    
                    print(f"   Post de test sélectionné: {self.test_post_id}")
                    print(f"   Titre actuel: {test_post.get('title', 'N/A')}")
                    print(f"   Texte actuel: {test_post.get('text', 'N/A')[:100]}...")
                    print(f"   Date programmée: {test_post.get('scheduled_date', 'N/A')}")
                    print(f"   Modified_at: {test_post.get('modified_at', 'N/A')}")
                    
                    return test_post
                else:
                    print("⚠️ Aucun post trouvé - génération de posts requise")
                    return None
                    
            else:
                print(f"❌ Échec GET posts: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur GET posts: {str(e)}")
            return None
    
    def test_1_endpoint_modification_response(self, original_post):
        """Test 1: Vérification réponse endpoint modification"""
        print("\n🧪 TEST 1: Vérification réponse endpoint modification")
        print("=" * 60)
        
        if not self.test_post_id:
            print("❌ Pas de post ID disponible pour le test")
            return False, None
        
        # Demande de modification complète comme dans l'exemple
        modification_request = {
            "modification_request": "Change le titre pour 'Nouveau Titre Test Diagnostic' et programme ce post pour le 15 septembre au lieu du 24"
        }
        
        print(f"📤 Envoi de la demande de modification:")
        print(f"   POST ID: {self.test_post_id}")
        print(f"   Demande: {modification_request['modification_request']}")
        
        try:
            response = self.session.put(
                f"{BACKEND_URL}/posts/{self.test_post_id}/modify",
                json=modification_request,
                timeout=60  # Timeout étendu pour l'IA
            )
            
            print(f"📥 Réponse reçue:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    print(f"✅ PUT /api/posts/{self.test_post_id}/modify réussi")
                    print(f"📊 ANALYSE COMPLETE DE LA RÉPONSE JSON:")
                    print(json.dumps(response_data, indent=2, ensure_ascii=False))
                    
                    # Vérifier les champs attendus par le frontend
                    expected_fields = ["new_title", "new_text", "new_hashtags", "modified_at", "scheduled_date"]
                    missing_fields = []
                    present_fields = []
                    
                    for field in expected_fields:
                        if field in response_data:
                            present_fields.append(field)
                            print(f"   ✅ {field}: {response_data[field]}")
                        else:
                            missing_fields.append(field)
                            print(f"   ❌ {field}: MANQUANT")
                    
                    # Vérifier les champs dans modified_post si présent
                    if "modified_post" in response_data:
                        modified_post = response_data["modified_post"]
                        print(f"📊 CHAMPS DANS modified_post:")
                        for key, value in modified_post.items():
                            print(f"   {key}: {value}")
                    
                    print(f"\n📋 RÉSUMÉ CHAMPS RÉPONSE:")
                    print(f"   Champs présents: {present_fields}")
                    print(f"   Champs manquants: {missing_fields}")
                    
                    # Diagnostic spécifique
                    if missing_fields:
                        print(f"⚠️ PROBLÈME IDENTIFIÉ: Champs manquants dans la réponse")
                        print(f"   Le frontend attend: {expected_fields}")
                        print(f"   Mais reçoit seulement: {present_fields}")
                        
                        if "scheduled_date" in missing_fields:
                            print(f"🚨 CRITIQUE: scheduled_date manquant - explique pourquoi les dates ne sont pas mises à jour!")
                    
                    return True, response_data
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Erreur parsing JSON: {e}")
                    print(f"   Raw response: {response.text}")
                    return False, None
            else:
                print(f"❌ Échec modification: {response.status_code}")
                print(f"   Response: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ Erreur modification: {str(e)}")
            return False, None
    
    def test_2_date_modification_specific(self):
        """Test 2: Test spécifique modification date"""
        print("\n🧪 TEST 2: Test spécifique modification date")
        print("=" * 60)
        
        if not self.test_post_id:
            print("❌ Pas de post ID disponible pour le test")
            return False, None
        
        # Demande centrée uniquement sur la date
        date_modification_request = {
            "modification_request": "Change la date de publication pour le 20 septembre 2025 à 14h00"
        }
        
        print(f"📤 Envoi de la demande de modification de date:")
        print(f"   POST ID: {self.test_post_id}")
        print(f"   Demande: {date_modification_request['modification_request']}")
        
        try:
            response = self.session.put(
                f"{BACKEND_URL}/posts/{self.test_post_id}/modify",
                json=date_modification_request,
                timeout=60
            )
            
            print(f"📥 Réponse reçue:")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    print(f"✅ Modification de date réussie")
                    print(f"📊 RÉPONSE COMPLÈTE:")
                    print(json.dumps(response_data, indent=2, ensure_ascii=False))
                    
                    # Vérifier si l'IA GPT-4 peut identifier et traiter les dates
                    if "modified_post" in response_data:
                        modified_post = response_data["modified_post"]
                        
                        # Chercher des indices de traitement de date
                        text_content = modified_post.get("text", "")
                        title_content = modified_post.get("title", "")
                        
                        date_keywords = ["20 septembre", "septembre 2025", "14h00", "14:00", "date", "programmé"]
                        date_found_in_content = any(keyword.lower() in text_content.lower() or keyword.lower() in title_content.lower() for keyword in date_keywords)
                        
                        print(f"🔍 ANALYSE TRAITEMENT DATE PAR IA:")
                        print(f"   Date trouvée dans le contenu: {date_found_in_content}")
                        print(f"   Texte modifié: {text_content[:200]}...")
                        
                        if date_found_in_content:
                            print(f"✅ L'IA GPT-4 a identifié et traité la demande de date")
                        else:
                            print(f"❌ L'IA GPT-4 n'a pas traité la demande de date dans le contenu")
                    
                    # Vérifier si scheduled_date est retourné
                    if "scheduled_date" in response_data:
                        print(f"✅ scheduled_date présent dans la réponse: {response_data['scheduled_date']}")
                    else:
                        print(f"❌ scheduled_date MANQUANT dans la réponse - PROBLÈME CRITIQUE!")
                    
                    return True, response_data
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Erreur parsing JSON: {e}")
                    return False, None
            else:
                print(f"❌ Échec modification date: {response.status_code}")
                print(f"   Response: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ Erreur modification date: {str(e)}")
            return False, None
    
    def test_3_response_format_verification(self):
        """Test 3: Vérification format réponse modification"""
        print("\n🧪 TEST 3: Vérification format réponse modification")
        print("=" * 60)
        
        if not self.test_post_id:
            print("❌ Pas de post ID disponible pour le test")
            return False, None
        
        # Test avec une modification simple pour analyser le format
        simple_modification = {
            "modification_request": "Ajoute un emoji 🎯 au début du titre"
        }
        
        print(f"📤 Test de format avec modification simple:")
        print(f"   Demande: {simple_modification['modification_request']}")
        
        try:
            response = self.session.put(
                f"{BACKEND_URL}/posts/{self.test_post_id}/modify",
                json=simple_modification,
                timeout=60
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                print(f"✅ Modification simple réussie")
                print(f"📊 ANALYSE EXACTE DES CHAMPS RETOURNÉS:")
                
                # Analyser chaque champ de la réponse
                for key, value in response_data.items():
                    print(f"   {key}: {type(value).__name__} = {value}")
                
                # Comparer avec ce que le frontend attend
                frontend_expected = {
                    "new_title": "response.data.new_title",
                    "new_text": "response.data.new_text", 
                    "new_hashtags": "response.data.new_hashtags",
                    "modified_at": "response.data.modified_at",
                    "scheduled_date": "response.data.scheduled_date"
                }
                
                print(f"\n🔍 COMPARAISON AVEC ATTENTES FRONTEND:")
                mapping_issues = []
                
                for frontend_field, frontend_path in frontend_expected.items():
                    if frontend_field in response_data:
                        print(f"   ✅ {frontend_field} → {frontend_path} : DISPONIBLE")
                    else:
                        print(f"   ❌ {frontend_field} → {frontend_path} : MANQUANT")
                        mapping_issues.append(frontend_field)
                
                # Vérifier si les données sont dans modified_post
                if "modified_post" in response_data and mapping_issues:
                    print(f"\n🔍 VÉRIFICATION DANS modified_post:")
                    modified_post = response_data["modified_post"]
                    
                    for missing_field in mapping_issues:
                        # Mapper les champs
                        mapped_field = missing_field.replace("new_", "")
                        if mapped_field in modified_post:
                            print(f"   ℹ️ {missing_field} trouvé comme '{mapped_field}' dans modified_post")
                        else:
                            print(f"   ❌ {missing_field} introuvable même dans modified_post")
                
                if mapping_issues:
                    print(f"\n🚨 PROBLÈME MAPPING FRONTEND IDENTIFIÉ:")
                    print(f"   Champs manquants: {mapping_issues}")
                    print(f"   Le frontend ne peut pas accéder à ces données!")
                    
                    if "scheduled_date" in mapping_issues:
                        print(f"   🎯 CAUSE PROBABLE: scheduled_date manquant explique pourquoi les dates ne se mettent pas à jour!")
                
                return True, response_data
                
            else:
                print(f"❌ Échec test format: {response.status_code}")
                return False, None
                
        except Exception as e:
            print(f"❌ Erreur test format: {str(e)}")
            return False, None
    
    def test_4_complete_post_modification_validation(self):
        """Test 4: Validation complète post-modification"""
        print("\n🧪 TEST 4: Validation complète post-modification")
        print("=" * 60)
        
        if not self.test_post_id:
            print("❌ Pas de post ID disponible pour le test")
            return False
        
        # Récupérer l'état du post AVANT modification
        print("📋 Récupération état AVANT modification...")
        try:
            response_before = self.session.get(f"{BACKEND_URL}/posts/generated", timeout=30)
            if response_before.status_code == 200:
                posts_before = response_before.json().get("posts", [])
                post_before = next((p for p in posts_before if p.get("id") == self.test_post_id), None)
                
                if post_before:
                    print(f"✅ État AVANT récupéré:")
                    print(f"   Titre: {post_before.get('title', 'N/A')}")
                    print(f"   Texte: {post_before.get('text', 'N/A')[:100]}...")
                    print(f"   Hashtags: {post_before.get('hashtags', [])}")
                    print(f"   Date programmée: {post_before.get('scheduled_date', 'N/A')}")
                    print(f"   Modified_at: {post_before.get('modified_at', 'N/A')}")
                else:
                    print("❌ Post non trouvé dans la liste")
                    return False
            else:
                print("❌ Impossible de récupérer l'état avant")
                return False
        except Exception as e:
            print(f"❌ Erreur récupération avant: {str(e)}")
            return False
        
        # Effectuer une modification complète
        complete_modification = {
            "modification_request": "Change le titre pour 'Test Validation Complète', modifie le texte pour parler de validation, et programme pour le 25 septembre 2025"
        }
        
        print(f"\n📤 Modification complète:")
        print(f"   Demande: {complete_modification['modification_request']}")
        
        try:
            # Effectuer la modification
            response_modify = self.session.put(
                f"{BACKEND_URL}/posts/{self.test_post_id}/modify",
                json=complete_modification,
                timeout=60
            )
            
            if response_modify.status_code == 200:
                modify_data = response_modify.json()
                print(f"✅ Modification effectuée avec succès")
                
                # Attendre un peu pour la persistance
                time.sleep(2)
                
                # Récupérer l'état APRÈS modification
                print(f"\n📋 Vérification état APRÈS modification...")
                response_after = self.session.get(f"{BACKEND_URL}/posts/generated", timeout=30)
                
                if response_after.status_code == 200:
                    posts_after = response_after.json().get("posts", [])
                    post_after = next((p for p in posts_after if p.get("id") == self.test_post_id), None)
                    
                    if post_after:
                        print(f"✅ État APRÈS récupéré:")
                        print(f"   Titre: {post_after.get('title', 'N/A')}")
                        print(f"   Texte: {post_after.get('text', 'N/A')[:100]}...")
                        print(f"   Hashtags: {post_after.get('hashtags', [])}")
                        print(f"   Date programmée: {post_after.get('scheduled_date', 'N/A')}")
                        print(f"   Modified_at: {post_after.get('modified_at', 'N/A')}")
                        
                        # VALIDATION CRITIQUE: Comparer avant/après
                        print(f"\n🔍 VALIDATION PERSISTANCE:")
                        
                        changes_detected = []
                        
                        # Vérifier le titre
                        if post_before.get('title') != post_after.get('title'):
                            changes_detected.append("titre")
                            print(f"   ✅ Titre modifié: '{post_before.get('title')}' → '{post_after.get('title')}'")
                        else:
                            print(f"   ❌ Titre INCHANGÉ: '{post_after.get('title')}'")
                        
                        # Vérifier le texte
                        if post_before.get('text') != post_after.get('text'):
                            changes_detected.append("texte")
                            print(f"   ✅ Texte modifié")
                        else:
                            print(f"   ❌ Texte INCHANGÉ")
                        
                        # Vérifier les hashtags
                        if post_before.get('hashtags') != post_after.get('hashtags'):
                            changes_detected.append("hashtags")
                            print(f"   ✅ Hashtags modifiés")
                        else:
                            print(f"   ❌ Hashtags INCHANGÉS")
                        
                        # Vérifier la date programmée
                        if post_before.get('scheduled_date') != post_after.get('scheduled_date'):
                            changes_detected.append("scheduled_date")
                            print(f"   ✅ Date programmée modifiée: '{post_before.get('scheduled_date')}' → '{post_after.get('scheduled_date')}'")
                        else:
                            print(f"   ❌ Date programmée INCHANGÉE: '{post_after.get('scheduled_date')}'")
                        
                        # Vérifier modified_at
                        if post_before.get('modified_at') != post_after.get('modified_at'):
                            changes_detected.append("modified_at")
                            print(f"   ✅ Modified_at mis à jour: '{post_before.get('modified_at')}' → '{post_after.get('modified_at')}'")
                        else:
                            print(f"   ❌ Modified_at INCHANGÉ: '{post_after.get('modified_at')}'")
                        
                        # DIAGNOSTIC FINAL
                        print(f"\n📊 RÉSULTAT VALIDATION:")
                        print(f"   Champs modifiés: {changes_detected}")
                        print(f"   Nombre de changements: {len(changes_detected)}")
                        
                        if len(changes_detected) >= 3:  # Au moins titre, texte, modified_at
                            print(f"✅ VALIDATION RÉUSSIE: Le post a bien été modifié et persisté")
                            return True
                        else:
                            print(f"❌ VALIDATION ÉCHOUÉE: Modifications insuffisantes détectées")
                            print(f"🚨 PROBLÈME: Le post n'est pas correctement mis à jour en base!")
                            return False
                    else:
                        print("❌ Post non trouvé après modification")
                        return False
                else:
                    print("❌ Impossible de récupérer l'état après modification")
                    return False
            else:
                print(f"❌ Échec modification complète: {response_modify.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur validation complète: {str(e)}")
            return False
    
    def run_diagnostic(self):
        """Exécuter le diagnostic complet"""
        print("=" * 80)
        print("🚨 DIAGNOSTIC URGENT - Post Modifié Non Affiché + Date Publication")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Credentials: {TEST_EMAIL} / {TEST_PASSWORD}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("\nPROBLÈMES RAPPORTÉS:")
        print("1. Spinner de modification visible mais ancien post affiché après")
        print("2. Demandes de modification de date non prises en compte")
        print("=" * 80)
        
        # Étape 1: Authentification
        if not self.authenticate():
            print("\n❌ DIAGNOSTIC ÉCHOUÉ: Impossible de s'authentifier")
            return False
        
        # Étape 2: Récupérer posts existants
        original_post = self.get_existing_posts()
        if not original_post:
            print("\n❌ DIAGNOSTIC ÉCHOUÉ: Aucun post disponible pour les tests")
            return False
        
        # Tests critiques
        test_results = {}
        
        # Test 1: Vérification réponse endpoint
        print(f"\n" + "="*80)
        test_1_success, test_1_data = self.test_1_endpoint_modification_response(original_post)
        test_results["test_1"] = test_1_success
        
        # Test 2: Test spécifique modification date
        print(f"\n" + "="*80)
        test_2_success, test_2_data = self.test_2_date_modification_specific()
        test_results["test_2"] = test_2_success
        
        # Test 3: Vérification format réponse
        print(f"\n" + "="*80)
        test_3_success, test_3_data = self.test_3_response_format_verification()
        test_results["test_3"] = test_3_success
        
        # Test 4: Validation complète post-modification
        print(f"\n" + "="*80)
        test_4_success = self.test_4_complete_post_modification_validation()
        test_results["test_4"] = test_4_success
        
        # Résumé final du diagnostic
        print("\n" + "=" * 80)
        print("📋 RÉSUMÉ DIAGNOSTIC COMPLET")
        print("=" * 80)
        
        total_tests = len(test_results)
        passed_tests = sum(test_results.values())
        
        print(f"Tests réussis: {passed_tests}/{total_tests}")
        
        for test_name, result in test_results.items():
            status = "✅ RÉUSSI" if result else "❌ ÉCHOUÉ"
            print(f"   {test_name}: {status}")
        
        # Diagnostic des problèmes
        print(f"\n🔍 ANALYSE DES PROBLÈMES IDENTIFIÉS:")
        
        if not test_results.get("test_1", False):
            print("❌ PROBLÈME 1: Réponse endpoint modification incomplète")
            print("   → Champs manquants dans la réponse (new_title, new_text, etc.)")
        
        if not test_results.get("test_2", False):
            print("❌ PROBLÈME 2: IA ne traite pas les dates correctement")
            print("   → Prompt insuffisant pour modifier les dates")
        
        if not test_results.get("test_3", False):
            print("❌ PROBLÈME 3: Format réponse incompatible avec frontend")
            print("   → Frontend ne peut pas mapper les champs de réponse")
        
        if not test_results.get("test_4", False):
            print("❌ PROBLÈME 4: Modifications non persistées en base")
            print("   → Les changements ne sont pas sauvegardés correctement")
        
        # Recommandations
        print(f"\n💡 RECOMMANDATIONS:")
        
        if passed_tests == total_tests:
            print("✅ Tous les tests sont passés - le système fonctionne correctement")
            print("   Le problème pourrait venir du frontend ou du cache")
        else:
            print("🔧 CORRECTIONS REQUISES:")
            print("1. Ajouter les champs manquants dans la réponse de l'endpoint")
            print("2. Améliorer le prompt IA pour traiter les dates")
            print("3. Vérifier la persistance en base de données")
            print("4. Synchroniser le format de réponse avec les attentes frontend")
        
        return passed_tests == total_tests

def main():
    """Point d'entrée principal"""
    diagnostic = PostModificationDiagnostic()
    success = diagnostic.run_diagnostic()
    
    if success:
        print("\n🎉 DIAGNOSTIC TERMINÉ AVEC SUCCÈS")
        print("✅ Le système de modification de posts fonctionne correctement")
        sys.exit(0)
    else:
        print("\n💥 DIAGNOSTIC RÉVÈLE DES PROBLÈMES CRITIQUES")
        print("❌ Des corrections sont nécessaires pour résoudre les problèmes utilisateur")
        sys.exit(1)

if __name__ == "__main__":
    main()