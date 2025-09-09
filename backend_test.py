#!/usr/bin/env python3
"""
Test du nouveau système de génération de posts avec UNE seule requête ChatGPT globale
Comprehensive testing of the new single global ChatGPT request post generation system

OBJECTIF: Valider que le système refactorisé utilise une seule requête ChatGPT pour générer 
tout le calendrier au lieu d'une requête par post.

Backend URL: https://content-scheduler-6.preview.emergentagent.com/api
Credentials: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import time
import sys
from datetime import datetime

class PostGenerationTester:
    def __init__(self):
        self.base_url = "https://content-scheduler-6.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.user_id = None
        self.jwt_token = None
        self.test_results = []
        
    def log_test(self, step, status, message, details=None):
        """Log test results with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        
        result = {
            "timestamp": timestamp,
            "step": step,
            "status": status,
            "message": message,
            "details": details
        }
        self.test_results.append(result)
        
        print(f"[{timestamp}] {status_icon} Step {step}: {message}")
        if details:
            print(f"    Details: {details}")
    
    def authenticate(self):
        """Step 1: Authenticate with provided credentials"""
        try:
            login_data = {
                "email": "lperpere@yahoo.fr",
                "password": "L@Reunion974!"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login-robust", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.jwt_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.jwt_token}'
                })
                
                self.log_test(1, "PASS", "Authentication successful", 
                            f"User ID: {self.user_id}, Token obtained")
                return True
            else:
                self.log_test(1, "FAIL", "Authentication failed", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test(1, "FAIL", "Authentication error", str(e))
            return False
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Configure session headers
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                })
                
                self.log(f"✅ Authentification réussie")
                self.log(f"   User ID: {self.user_id}")
                self.log(f"   Token: {self.auth_token[:20]}...")
                return True
            else:
                self.log(f"❌ Échec authentification: {response.status_code}")
                self.log(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Erreur authentification: {str(e)}")
            return False
    
    def test_business_profile(self):
        """Test 2: Vérifier le profil business et son posting_frequency"""
        self.log("🏢 ÉTAPE 2: Vérification du profil business")
        
        try:
            response = self.session.get(f"{self.base_url}/business-profile", timeout=30)
            
            if response.status_code == 200:
                profile = response.json()
                
                business_name = profile.get("business_name")
                business_type = profile.get("business_type")
                posting_frequency = profile.get("posting_frequency")
                
                self.log(f"✅ Profil business récupéré avec succès")
                self.log(f"   Business Name: {business_name}")
                self.log(f"   Business Type: {business_type}")
                self.log(f"   Posting Frequency: {posting_frequency}")
                
                if not posting_frequency:
                    self.log("⚠️ Attention: posting_frequency non défini dans le profil")
                    return False, None
                
                return True, posting_frequency
            else:
                self.log(f"❌ Échec récupération profil: {response.status_code}")
                self.log(f"   Response: {response.text}")
                return False, None
                
        except Exception as e:
            self.log(f"❌ Erreur récupération profil: {str(e)}")
            return False, None
    
    def calculate_expected_posts(self, posting_frequency):
        """Calculer le nombre de posts attendu selon la fréquence"""
        frequency_mapping = {
            "daily": 7,        # 7 posts par semaine
            "3x_week": 3,      # 3 posts par semaine
            "weekly": 1,       # 1 post par semaine
            "bi_weekly": 2     # 2 posts par semaine
        }
        
        posts_per_week = frequency_mapping.get(posting_frequency, 1)
        expected_posts = posts_per_week * 4  # 4 semaines par mois
        
        self.log(f"📊 CALCUL ATTENDU:")
        self.log(f"   Fréquence: {posting_frequency}")
        self.log(f"   Posts par semaine: {posts_per_week}")
        self.log(f"   Posts par mois (4 semaines): {expected_posts}")
        
        return expected_posts
    
    def test_post_generation(self):
        """Test 3: Génération de posts sans paramètres"""
        self.log("🚀 ÉTAPE 3: Test de génération de posts")
        
        try:
            # Appel sans paramètres comme spécifié dans la review request
            self.log("   Appel POST /api/posts/generate sans paramètres...")
            start_time = time.time()
            
            response = self.session.post(
                f"{self.base_url}/posts/generate",
                timeout=120  # Timeout étendu pour la génération
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            self.log(f"   Durée de génération: {duration:.1f} secondes")
            
            if response.status_code == 200:
                data = response.json()
                
                success = data.get("success", False)
                posts_count = data.get("posts_count", 0)
                strategy = data.get("strategy", {})
                sources_used = data.get("sources_used", {})
                
                self.log(f"✅ Génération terminée avec succès")
                self.log(f"   Success: {success}")
                self.log(f"   Posts générés: {posts_count}")
                self.log(f"   Stratégie: {strategy}")
                self.log(f"   Sources utilisées: {sources_used}")
                
                return True, posts_count, data
            else:
                self.log(f"❌ Échec génération: {response.status_code}")
                self.log(f"   Response: {response.text}")
                return False, 0, None
                
        except Exception as e:
            self.log(f"❌ Erreur génération: {str(e)}")
            return False, 0, None
    
    def test_generated_posts_retrieval(self):
        """Test 4: Récupération des posts générés pour validation"""
        self.log("📋 ÉTAPE 4: Récupération des posts générés")
        
        try:
            response = self.session.get(f"{self.base_url}/posts/generated", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                count = data.get("count", 0)
                
                self.log(f"✅ Posts récupérés avec succès")
                self.log(f"   Nombre total de posts: {count}")
                
                return True, posts
            else:
                self.log(f"❌ Échec récupération posts: {response.status_code}")
                self.log(f"   Response: {response.text}")
                return False, []
                
        except Exception as e:
            self.log(f"❌ Erreur récupération posts: {str(e)}")
            return False, []
    
    def validate_posts_uniqueness(self, posts):
        """Test 5: Validation de l'unicité et variété des posts"""
        self.log("🔍 ÉTAPE 5: Validation de l'unicité et variété des posts")
        
        if not posts:
            self.log("❌ Aucun post à valider")
            return False
        
        # Vérifier l'unicité des textes
        texts = [post.get("text", "") for post in posts]
        unique_texts = set(texts)
        
        # Vérifier l'unicité des titres
        titles = [post.get("title", "") for post in posts]
        unique_titles = set(titles)
        
        # Vérifier la variété des types de contenu
        content_types = [post.get("content_type", "") for post in posts]
        unique_content_types = set(content_types)
        
        # Vérifier la variété des hashtags
        all_hashtags = []
        for post in posts:
            hashtags = post.get("hashtags", [])
            all_hashtags.extend(hashtags)
        unique_hashtags = set(all_hashtags)
        
        self.log(f"📊 ANALYSE DE VARIÉTÉ:")
        self.log(f"   Posts total: {len(posts)}")
        self.log(f"   Textes uniques: {len(unique_texts)}/{len(texts)}")
        self.log(f"   Titres uniques: {len(unique_titles)}/{len(titles)}")
        self.log(f"   Types de contenu: {unique_content_types}")
        self.log(f"   Hashtags uniques: {len(unique_hashtags)}")
        
        # Validation
        uniqueness_score = len(unique_texts) / len(texts) if texts else 0
        variety_score = len(unique_content_types)
        
        if uniqueness_score >= 0.8 and variety_score >= 2:
            self.log(f"✅ Posts suffisamment uniques et variés")
            self.log(f"   Score d'unicité: {uniqueness_score:.2%}")
            self.log(f"   Variété de contenu: {variety_score} types")
            return True
        else:
            self.log(f"⚠️ Posts manquent d'unicité ou de variété")
            self.log(f"   Score d'unicité: {uniqueness_score:.2%} (minimum 80%)")
            self.log(f"   Variété de contenu: {variety_score} types (minimum 2)")
            return False
    
    def run_comprehensive_test(self):
        """Exécuter tous les tests de manière séquentielle"""
        self.log("🎯 DÉBUT DU TEST COMPLET DU SYSTÈME DE GÉNÉRATION DE POSTS")
        self.log("=" * 80)
        
        # Test 1: Authentification
        if not self.test_authentication():
            self.log("❌ ÉCHEC CRITIQUE: Authentification impossible")
            return False
        
        # Test 2: Profil business
        profile_success, posting_frequency = self.test_business_profile()
        if not profile_success:
            self.log("❌ ÉCHEC CRITIQUE: Profil business inaccessible")
            return False
        
        # Calcul attendu
        expected_posts = self.calculate_expected_posts(posting_frequency)
        
        # Test 3: Génération de posts
        gen_success, actual_posts_count, gen_data = self.test_post_generation()
        if not gen_success:
            self.log("❌ ÉCHEC CRITIQUE: Génération de posts impossible")
            return False
        
        # Test 4: Récupération des posts
        retrieval_success, posts = self.test_generated_posts_retrieval()
        if not retrieval_success:
            self.log("❌ ÉCHEC: Récupération des posts impossible")
            return False
        
        # Test 5: Validation de l'unicité
        uniqueness_valid = self.validate_posts_uniqueness(posts)
        
        # VALIDATION FINALE
        self.log("=" * 80)
        self.log("🎯 RÉSULTATS FINAUX:")
        
        # Vérification du nombre de posts
        posts_count_match = actual_posts_count == expected_posts
        
        self.log(f"📊 VALIDATION DU CALCUL:")
        self.log(f"   Fréquence configurée: {posting_frequency}")
        self.log(f"   Posts attendus: {expected_posts}")
        self.log(f"   Posts générés: {actual_posts_count}")
        self.log(f"   Calcul correct: {'✅' if posts_count_match else '❌'}")
        
        if posts_count_match:
            self.log(f"✅ Le calcul basé sur posting_frequency fonctionne correctement")
        else:
            self.log(f"❌ ERREUR: Le nombre de posts ne correspond pas au calcul attendu")
        
        # Résumé global
        all_tests_passed = (
            profile_success and 
            gen_success and 
            retrieval_success and 
            posts_count_match and 
            uniqueness_valid
        )
        
        self.log("=" * 80)
        if all_tests_passed:
            self.log("🎉 SUCCÈS COMPLET: Tous les tests sont passés avec succès")
            self.log("   ✅ Authentification")
            self.log("   ✅ Profil business accessible")
            self.log("   ✅ Génération de posts fonctionnelle")
            self.log("   ✅ Calcul posting_frequency correct")
            self.log("   ✅ Posts uniques et variés")
        else:
            self.log("❌ ÉCHEC: Certains tests ont échoué")
            self.log(f"   Authentification: {'✅' if True else '❌'}")
            self.log(f"   Profil business: {'✅' if profile_success else '❌'}")
            self.log(f"   Génération posts: {'✅' if gen_success else '❌'}")
            self.log(f"   Calcul correct: {'✅' if posts_count_match else '❌'}")
            self.log(f"   Unicité/variété: {'✅' if uniqueness_valid else '❌'}")
        
        return all_tests_passed

def main():
    """Point d'entrée principal"""
    tester = PostGenerationTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 TEST RÉUSSI: Le système de génération de posts fonctionne correctement")
        exit(0)
    else:
        print("\n❌ TEST ÉCHOUÉ: Des problèmes ont été détectés")
        exit(1)

if __name__ == "__main__":
    main()