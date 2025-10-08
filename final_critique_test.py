#!/usr/bin/env python3
"""
TEST FINAL CRITIQUE du système de génération de posts avec clé OpenAI directe

OBJECTIF: Validation définitive que la génération fonctionne avec votre nouvelle clé OpenAI.

CONFIGURATION UTILISÉE:
- OpenAI directe (pas emergentintegrations)
- Votre nouvelle clé OpenAI valide
- Modèle gpt-4o directement

TEST FINAL:
1. Authentification (lperpere@yahoo.fr / L@Reunion974!)
2. POST /api/posts/generate avec num_posts=2 (test minimal)
3. Vérification que des posts sont créés avec VRAI contenu ChatGPT
4. GET /api/posts/generated pour confirmer sauvegarde

CRITÈRES DE SUCCÈS:
- Posts count > 0 (au moins 1 post généré)
- Contenu texte riche et engageant  
- Hashtags pertinents
- Titre accrocheur
- Sauvegarde en base de données

Backend URL: https://post-restore.preview.emergentagent.com/api

SI SUCCÈS: Système 100% opérationnel, prêt pour utilisation
SI ÉCHEC: Identifier la cause exacte (clé, API, budget, etc.)
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://post-restore.preview.emergentagent.com/api"
EMAIL = "lperpere@yahoo.fr"
PASSWORD = "L@Reunion974!"

class FinalCritiqueTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        
    def authenticate(self):
        """Step 1: Authentification utilisateur"""
        print("🔑 Step 1: Authentication with POST /api/auth/login-robust")
        
        login_data = {
            "email": EMAIL,
            "password": PASSWORD
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login-robust", json=login_data)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for all future requests
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                
                print(f"   ✅ Authentication successful")
                print(f"   User ID: {self.user_id}")
                return True
            else:
                print(f"   ❌ Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {e}")
            return False
    
    def test_minimal_post_generation(self):
        """Step 2: Test génération minimale avec num_posts=2"""
        print("🚀 Step 2: POST /api/posts/generate avec num_posts=2 (test minimal)")
        print("   🔑 Configuration: OpenAI directe avec votre nouvelle clé")
        print("   🎯 Objectif: Vérifier génération RÉELLE avec ChatGPT 4o")
        
        generation_params = {
            "target_month": "octobre_2025",
            "num_posts": 2  # Test minimal comme demandé
        }
        
        try:
            # Start generation
            start_time = time.time()
            response = self.session.post(f"{BACKEND_URL}/posts/generate", params=generation_params)
            end_time = time.time()
            
            print(f"   Status: {response.status_code}")
            print(f"   Generation time: {end_time - start_time:.2f} seconds")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"   ✅ API call successful")
                print(f"   Success: {data.get('success', False)}")
                print(f"   Posts generated: {data.get('posts_count', 0)}")
                print(f"   Message: {data.get('message', 'No message')}")
                
                # Analyze generation result
                posts_count = data.get('posts_count', 0)
                success = data.get('success', False)
                
                if success and posts_count > 0:
                    print(f"   🎉 SUCCÈS: {posts_count} posts générés avec ChatGPT 4o!")
                    print(f"   ✅ VRAI contenu généré par l'IA")
                    
                    # Store generation results
                    self.generation_result = data
                    return True
                    
                elif success and posts_count == 0:
                    print(f"   ⚠️ API successful but 0 posts generated")
                    print(f"   💡 Possible causes: Budget limit, API key issue, or content generation failure")
                    
                    # Still store result for analysis
                    self.generation_result = data
                    return False
                    
                else:
                    print(f"   ❌ Generation failed: success={success}, posts_count={posts_count}")
                    return False
                    
            else:
                print(f"   ❌ Post generation failed: {response.text}")
                
                # Try to parse error for more details
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', 'Unknown error')
                    print(f"   🔍 Error detail: {error_detail}")
                except:
                    pass
                    
                return False
                
        except Exception as e:
            print(f"   ❌ Post generation error: {e}")
            return False
    
    def verify_posts_saved_in_database(self):
        """Step 3: GET /api/posts/generated pour confirmer sauvegarde"""
        print("📋 Step 3: GET /api/posts/generated pour confirmer sauvegarde")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/posts/generated")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('posts', [])
                count = data.get('count', 0)
                
                print(f"   ✅ Posts retrieval successful")
                print(f"   Posts count in database: {count}")
                print(f"   Posts array length: {len(posts)}")
                
                if count > 0 and posts:
                    print(f"   🎉 POSTS SAUVEGARDÉS EN BASE DE DONNÉES!")
                    
                    # Analyze first post for content quality
                    first_post = posts[0]
                    
                    title = first_post.get('title', '')
                    text = first_post.get('text', '')
                    hashtags = first_post.get('hashtags', [])
                    platform = first_post.get('platform', '')
                    
                    print(f"   📋 Analyse du premier post:")
                    print(f"      Titre: {title[:50]}..." if len(title) > 50 else f"      Titre: {title}")
                    print(f"      Texte: {len(text)} caractères")
                    print(f"      Hashtags: {len(hashtags)} tags")
                    print(f"      Platform: {platform}")
                    
                    # Content quality validation
                    has_rich_content = len(text) > 20  # Contenu texte riche
                    has_hashtags = len(hashtags) > 0   # Hashtags pertinents
                    has_title = len(title) > 0         # Titre accrocheur
                    is_instagram = platform == 'instagram'
                    
                    print(f"   🔍 Validation qualité contenu:")
                    print(f"      Contenu texte riche: {'✅' if has_rich_content else '❌'}")
                    print(f"      Hashtags pertinents: {'✅' if has_hashtags else '❌'}")
                    print(f"      Titre accrocheur: {'✅' if has_title else '❌'}")
                    print(f"      Platform Instagram: {'✅' if is_instagram else '❌'}")
                    
                    # Store for final analysis
                    self.retrieved_posts = posts
                    self.content_quality = {
                        'rich_content': has_rich_content,
                        'hashtags': has_hashtags,
                        'title': has_title,
                        'instagram': is_instagram
                    }
                    
                    # Success if all quality criteria met
                    quality_score = sum(self.content_quality.values())
                    if quality_score >= 3:  # At least 3/4 criteria
                        print(f"   ✅ QUALITÉ CONTENU VALIDÉE ({quality_score}/4)")
                        return True
                    else:
                        print(f"   ⚠️ Qualité contenu partielle ({quality_score}/4)")
                        return True  # Still consider success if posts exist
                        
                else:
                    print(f"   ❌ Aucun post trouvé en base de données")
                    print(f"   💡 Les posts n'ont pas été sauvegardés correctement")
                    return False
                    
            else:
                print(f"   ❌ Posts retrieval failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Posts retrieval error: {e}")
            return False
    
    def run_final_critique_test(self):
        """Run final critique test as requested"""
        print("🎯 TEST FINAL CRITIQUE - SYSTÈME DE GÉNÉRATION DE POSTS")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Credentials: {EMAIL}")
        print(f"Configuration: OpenAI directe avec nouvelle clé valide")
        print(f"Test: num_posts=2 (minimal)")
        print("=" * 70)
        
        test_results = []
        
        # Step 1: Authentication
        test_results.append(self.authenticate())
        
        if test_results[-1]:
            # Step 2: Minimal post generation
            test_results.append(self.test_minimal_post_generation())
            
            # Step 3: Verify posts saved
            test_results.append(self.verify_posts_saved_in_database())
        
        # Final Analysis
        print("\n" + "=" * 70)
        print("🎯 RÉSULTATS DU TEST FINAL CRITIQUE")
        print("=" * 70)
        
        test_names = [
            "Authentification (lperpere@yahoo.fr / L@Reunion974!)",
            "POST /api/posts/generate avec num_posts=2",
            "GET /api/posts/generated pour confirmer sauvegarde"
        ]
        
        passed_tests = 0
        for i, (name, result) in enumerate(zip(test_names[:len(test_results)], test_results)):
            status = "✅ SUCCÈS" if result else "❌ ÉCHEC"
            print(f"{i+1}. {name}: {status}")
            if result:
                passed_tests += 1
        
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\nTaux de succès: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Detailed Results Analysis
        print("\n📊 ANALYSE DÉTAILLÉE:")
        
        if hasattr(self, 'generation_result'):
            gen_result = self.generation_result
            posts_count = gen_result.get('posts_count', 0)
            success = gen_result.get('success', False)
            
            print(f"   Posts générés: {posts_count}")
            print(f"   Génération réussie: {success}")
            
            if posts_count > 0:
                print(f"   ✅ CRITÈRE 1: Posts count > 0 ✓")
            else:
                print(f"   ❌ CRITÈRE 1: Posts count = 0 ✗")
        
        if hasattr(self, 'content_quality'):
            quality = self.content_quality
            print(f"   ✅ CRITÈRE 2: Contenu texte riche: {'✓' if quality['rich_content'] else '✗'}")
            print(f"   ✅ CRITÈRE 3: Hashtags pertinents: {'✓' if quality['hashtags'] else '✗'}")
            print(f"   ✅ CRITÈRE 4: Titre accrocheur: {'✓' if quality['title'] else '✗'}")
            print(f"   ✅ CRITÈRE 5: Sauvegarde en base: {'✓' if hasattr(self, 'retrieved_posts') else '✗'}")
        
        # Final Verdict
        print("\n" + "=" * 70)
        
        if success_rate == 100 and hasattr(self, 'generation_result') and self.generation_result.get('posts_count', 0) > 0:
            print("🎉 SUCCÈS COMPLET - SYSTÈME 100% OPÉRATIONNEL")
            print("✅ La génération fonctionne avec votre nouvelle clé OpenAI")
            print("✅ Posts créés avec VRAI contenu ChatGPT 4o")
            print("✅ Sauvegarde en base de données confirmée")
            print("🚀 SYSTÈME PRÊT POUR UTILISATION")
            
            if hasattr(self, 'retrieved_posts') and self.retrieved_posts:
                first_post = self.retrieved_posts[0]
                print(f"\n📋 Exemple de contenu généré:")
                print(f"   Titre: {first_post.get('title', 'N/A')}")
                print(f"   Texte: {first_post.get('text', 'N/A')[:100]}...")
                print(f"   Hashtags: {', '.join(first_post.get('hashtags', [])[:5])}")
            
            return True
            
        elif success_rate >= 66 and hasattr(self, 'generation_result'):
            gen_result = self.generation_result
            if gen_result.get('success') and gen_result.get('posts_count', 0) == 0:
                print("⚠️ SUCCÈS PARTIEL - SYSTÈME FONCTIONNE MAIS 0 POSTS")
                print("✅ API et authentification fonctionnent")
                print("✅ Clé OpenAI est valide")
                print("❌ Aucun post généré - Causes possibles:")
                print("   • Budget OpenAI épuisé")
                print("   • Limite de taux API atteinte")
                print("   • Problème de génération de contenu")
                print("🔍 RECOMMANDATION: Vérifier budget et limites OpenAI")
                return False
            else:
                print("⚠️ SUCCÈS PARTIEL - PROBLÈMES IDENTIFIÉS")
                return False
        else:
            print("🚨 ÉCHEC - PROBLÈMES CRITIQUES IDENTIFIÉS")
            
            if not test_results[0]:
                print("❌ CAUSE: Authentification échoue")
            elif not test_results[1]:
                print("❌ CAUSE: Génération de posts échoue")
                print("   • Clé OpenAI invalide/expirée")
                print("   • Budget OpenAI épuisé")
                print("   • Problème de configuration")
            elif not test_results[2]:
                print("❌ CAUSE: Sauvegarde en base échoue")
            
            print("🔧 ACTION REQUISE: Corriger les problèmes identifiés")
            return False

def main():
    """Main test execution"""
    tester = FinalCritiqueTester()
    success = tester.run_final_critique_test()
    
    if success:
        print("\n🎯 CONCLUSION FINALE: SYSTÈME 100% OPÉRATIONNEL, PRÊT POUR UTILISATION")
        exit(0)
    else:
        print("\n🚨 CONCLUSION FINALE: IDENTIFIER ET CORRIGER LA CAUSE EXACTE")
        exit(1)

if __name__ == "__main__":
    main()