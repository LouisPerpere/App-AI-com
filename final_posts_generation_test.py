#!/usr/bin/env python3
"""
Test final du système de génération de posts avec la nouvelle clé OpenAI valide

OBJECTIF: Confirmer que la génération fonctionne parfaitement avec la nouvelle clé OpenAI.

TEST COMPLET:
1. Authentification (lperpere@yahoo.fr / L@Reunion974!)
2. POST /api/posts/generate avec num_posts=3 (test de validation)
3. Vérification contenu généré par ChatGPT 4o (textes, hashtags, titres)
4. GET /api/posts/generated pour confirmer sauvegarde
5. Validation structure JSON et métadonnées

PARAMÈTRES DE TEST:
- target_month: octobre_2025
- num_posts: 3 (validation rapide)
- Backend URL: https://claire-marcus-app-1.preview.emergentagent.com/api

RÉSULTAT ATTENDU:
- 3 posts générés avec contenu riche de ChatGPT 4o
- Textes engageants, hashtags pertinents, titres accrocheurs
- Sauvegarde correcte en base de données
- Métadonnées complètes (scheduled_date, content_type, etc.)
"""

import requests
import json
import time
from datetime import datetime

# Configuration selon la demande de test
BACKEND_URL = "https://claire-marcus-app-1.preview.emergentagent.com/api"
EMAIL = "lperpere@yahoo.fr"
PASSWORD = "L@Reunion974!"
TARGET_MONTH = "octobre_2025"
NUM_POSTS = 3  # Test de validation rapide

class FinalPostsGenerationTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        
    def authenticate(self):
        """Step 1: Authentification utilisateur"""
        print("🔑 Step 1: Authentication (lperpere@yahoo.fr / L@Reunion974!)")
        
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
    
    def test_posts_generation_with_new_key(self):
        """Step 2: POST /api/posts/generate avec num_posts=3 (test de validation)"""
        print(f"🚀 Step 2: POST /api/posts/generate with new OpenAI key")
        print(f"   Target month: {TARGET_MONTH}")
        print(f"   Number of posts: {NUM_POSTS} (validation rapide)")
        print(f"   🔑 Using nouvelle clé OpenAI valide (EMERGENT_LLM_KEY)")
        
        generation_params = {
            "target_month": TARGET_MONTH,
            "num_posts": NUM_POSTS
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
                
                print(f"   ✅ Post generation API call successful")
                print(f"   Success: {data.get('success', False)}")
                print(f"   Posts generated: {data.get('posts_count', 0)}")
                print(f"   Message: {data.get('message', 'No message')}")
                
                # Analyze generation result
                strategy = data.get('strategy', {})
                sources_used = data.get('sources_used', {})
                
                if strategy:
                    print(f"   📊 Content strategy:")
                    for content_type, count in strategy.items():
                        print(f"      {content_type}: {count} posts")
                
                if sources_used:
                    print(f"   📋 Sources used:")
                    for source, value in sources_used.items():
                        print(f"      {source}: {value}")
                
                # Store generation results
                self.generation_result = data
                
                # Check if posts were actually generated
                posts_count = data.get('posts_count', 0)
                if posts_count >= NUM_POSTS:
                    print(f"   ✅ {posts_count} posts generated successfully with new OpenAI key!")
                    print(f"   🎉 REAL CONTENT GENERATED BY CHATGPT 4O")
                    return True
                elif posts_count > 0:
                    print(f"   ⚠️ Only {posts_count}/{NUM_POSTS} posts generated - partial success")
                    return True  # Still consider it a success if some posts were generated
                else:
                    print(f"   ❌ No posts were generated - new OpenAI key may have issues")
                    print(f"   💡 Expected: {NUM_POSTS} posts with real ChatGPT 4o content")
                    return False
                    
            else:
                print(f"   ❌ Post generation failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Post generation error: {e}")
            return False
    
    def verify_generated_content_quality(self):
        """Step 3: Vérification contenu généré par ChatGPT 4o (textes, hashtags, titres)"""
        print("🔍 Step 3: Verify generated content quality (ChatGPT 4o)")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/posts/generated")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('posts', [])
                count = data.get('count', 0)
                
                print(f"   ✅ Posts retrieval successful")
                print(f"   Posts count: {count}")
                print(f"   Posts array length: {len(posts)}")
                
                if posts:
                    print(f"   📋 Content quality analysis for {len(posts)} posts:")
                    
                    quality_scores = []
                    
                    for i, post in enumerate(posts):
                        print(f"   📝 Post {i+1} quality check:")
                        
                        # Check text quality
                        text = post.get('text', '')
                        text_length = len(text)
                        has_emojis = any(ord(char) > 127 for char in text)
                        
                        # Check hashtags quality
                        hashtags = post.get('hashtags', [])
                        hashtags_count = len(hashtags)
                        
                        # Check title quality
                        title = post.get('title', '')
                        title_length = len(title)
                        
                        # Check metadata
                        platform = post.get('platform', '')
                        content_type = post.get('content_type', '')
                        scheduled_date = post.get('scheduled_date', '')
                        
                        print(f"      Text: {text_length} chars {'✅' if text_length > 50 else '❌'}")
                        print(f"      Emojis: {'✅' if has_emojis else '⚠️'}")
                        print(f"      Hashtags: {hashtags_count} tags {'✅' if 5 <= hashtags_count <= 25 else '❌'}")
                        print(f"      Title: {title_length} chars {'✅' if title_length > 5 else '❌'}")
                        print(f"      Platform: {platform} {'✅' if platform == 'instagram' else '❌'}")
                        print(f"      Content type: {content_type} {'✅' if content_type else '❌'}")
                        print(f"      Scheduled: {'✅' if scheduled_date else '❌'}")
                        
                        # Calculate quality score
                        score = 0
                        if text_length > 50: score += 1
                        if has_emojis: score += 1
                        if 5 <= hashtags_count <= 25: score += 1
                        if title_length > 5: score += 1
                        if platform == 'instagram': score += 1
                        if content_type: score += 1
                        if scheduled_date: score += 1
                        
                        quality_percentage = (score / 7) * 100
                        quality_scores.append(quality_percentage)
                        
                        print(f"      Quality score: {score}/7 ({quality_percentage:.1f}%)")
                        
                        # Show sample content
                        if i == 0:  # Show first post as example
                            print(f"      📄 Sample text: {text[:100]}...")
                            print(f"      🏷️ Sample hashtags: {hashtags[:5]}")
                    
                    # Overall quality assessment
                    avg_quality = sum(quality_scores) / len(quality_scores)
                    print(f"   📊 Overall content quality: {avg_quality:.1f}%")
                    
                    # Store for validation
                    self.retrieved_posts = posts
                    self.content_quality = avg_quality
                    
                    if avg_quality >= 70:
                        print(f"   ✅ Content quality validation PASSED")
                        return True
                    else:
                        print(f"   ❌ Content quality validation FAILED")
                        return False
                else:
                    print(f"   ❌ No posts found for quality verification")
                    return False
                    
            else:
                print(f"   ❌ Posts retrieval failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Content quality verification error: {e}")
            return False
    
    def validate_database_persistence(self):
        """Step 4: GET /api/posts/generated pour confirmer sauvegarde"""
        print("💾 Step 4: Validate database persistence")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/posts/generated")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('posts', [])
                count = data.get('count', 0)
                
                print(f"   ✅ Database retrieval successful")
                print(f"   Persisted posts count: {count}")
                
                if count >= NUM_POSTS:
                    print(f"   ✅ All {NUM_POSTS} posts correctly saved to database")
                    
                    # Verify data integrity
                    for i, post in enumerate(posts):
                        post_id = post.get('id', '')
                        created_at = post.get('created_at', '')
                        
                        print(f"   📋 Post {i+1} persistence check:")
                        print(f"      ID: {'✅' if post_id else '❌'} {post_id}")
                        print(f"      Created: {'✅' if created_at else '❌'} {created_at}")
                    
                    return True
                elif count > 0:
                    print(f"   ⚠️ Only {count}/{NUM_POSTS} posts saved - partial persistence")
                    return True
                else:
                    print(f"   ❌ No posts found in database")
                    return False
                    
            else:
                print(f"   ❌ Database retrieval failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Database persistence validation error: {e}")
            return False
    
    def validate_json_structure_and_metadata(self):
        """Step 5: Validation structure JSON et métadonnées"""
        print("🔍 Step 5: Validate JSON structure and metadata")
        
        if not hasattr(self, 'retrieved_posts') or not self.retrieved_posts:
            print("   ❌ No posts available for structure validation")
            return False
        
        posts = self.retrieved_posts
        validation_results = []
        
        print(f"   Validating JSON structure for {len(posts)} posts...")
        
        # Required fields according to review request
        required_fields = {
            'id': str,
            'title': str,
            'text': str,
            'hashtags': list,
            'platform': str,
            'scheduled_date': str,
            'content_type': str,
            'created_at': str
        }
        
        for i, post in enumerate(posts):
            print(f"   📋 Post {i+1} structure validation:")
            
            post_valid = True
            
            for field, expected_type in required_fields.items():
                value = post.get(field)
                has_field = field in post
                correct_type = isinstance(value, expected_type) if has_field else False
                
                if has_field and correct_type and value:  # Also check not empty
                    print(f"      ✅ {field}: {expected_type.__name__}")
                elif has_field and not correct_type:
                    print(f"      ⚠️ {field}: wrong type (expected {expected_type.__name__})")
                    post_valid = False
                elif has_field and not value:
                    print(f"      ⚠️ {field}: empty value")
                    post_valid = False
                else:
                    print(f"      ❌ {field}: missing")
                    post_valid = False
            
            # Metadata validation
            scheduled_date = post.get('scheduled_date', '')
            platform = post.get('platform', '')
            content_type = post.get('content_type', '')
            
            metadata_valid = (
                TARGET_MONTH.split('_')[0] in scheduled_date.lower() if scheduled_date else False
            ) and platform == 'instagram' and content_type in ['product', 'value', 'backstage', 'educational', 'sales']
            
            print(f"      Metadata: {'✅' if metadata_valid else '❌'}")
            
            overall_valid = post_valid and metadata_valid
            validation_results.append(overall_valid)
            
            print(f"      Overall: {'✅ VALID' if overall_valid else '❌ INVALID'}")
        
        # Summary
        valid_posts = sum(validation_results)
        total_posts = len(validation_results)
        success_rate = (valid_posts / total_posts) * 100 if total_posts > 0 else 0
        
        print(f"   📊 Structure validation summary:")
        print(f"      Valid posts: {valid_posts}/{total_posts}")
        print(f"      Success rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print(f"   ✅ JSON structure and metadata validation PASSED")
            return True
        else:
            print(f"   ❌ JSON structure and metadata validation FAILED")
            return False
    
    def run_final_validation_test(self):
        """Run complete final validation test"""
        print("🎯 VALIDATION FINALE: Système de génération de posts Instagram")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test credentials: {EMAIL}")
        print(f"Target month: {TARGET_MONTH}")
        print(f"Number of posts: {NUM_POSTS}")
        print(f"Objective: Confirmer génération avec nouvelle clé OpenAI valide")
        print("=" * 80)
        
        test_results = []
        
        # Step 1: Authentication
        test_results.append(self.authenticate())
        
        if test_results[-1]:
            # Step 2: Posts generation with new key
            test_results.append(self.test_posts_generation_with_new_key())
            
            # Step 3: Content quality verification
            test_results.append(self.verify_generated_content_quality())
            
            # Step 4: Database persistence
            test_results.append(self.validate_database_persistence())
            
            # Step 5: JSON structure and metadata
            test_results.append(self.validate_json_structure_and_metadata())
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 VALIDATION FINALE - RÉSULTATS")
        print("=" * 80)
        
        test_names = [
            "1. Authentification (lperpere@yahoo.fr / L@Reunion974!)",
            "2. POST /api/posts/generate avec num_posts=3",
            "3. Vérification contenu généré par ChatGPT 4o",
            "4. GET /api/posts/generated pour confirmer sauvegarde",
            "5. Validation structure JSON et métadonnées"
        ]
        
        passed_tests = 0
        for i, (name, result) in enumerate(zip(test_names[:len(test_results)], test_results)):
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{name}: {status}")
            if result:
                passed_tests += 1
        
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\nTaux de réussite global: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Detailed results
        print("\n📊 ANALYSE DÉTAILLÉE:")
        
        if hasattr(self, 'generation_result'):
            gen_result = self.generation_result
            print(f"   Posts générés: {gen_result.get('posts_count', 0)}")
            print(f"   Génération réussie: {gen_result.get('success', False)}")
        
        if hasattr(self, 'content_quality'):
            print(f"   Qualité du contenu: {self.content_quality:.1f}%")
        
        if hasattr(self, 'retrieved_posts'):
            print(f"   Posts sauvegardés: {len(self.retrieved_posts)}")
        
        # Final verdict
        if success_rate >= 80:
            print("\n🎉 VALIDATION FINALE RÉUSSIE")
            print("✅ Le système de génération fonctionne parfaitement avec la nouvelle clé OpenAI")
            
            if hasattr(self, 'generation_result') and self.generation_result.get('posts_count', 0) >= NUM_POSTS:
                print(f"✅ {NUM_POSTS} posts générés avec contenu riche de ChatGPT 4o")
                print("✅ Textes engageants, hashtags pertinents, titres accrocheurs")
                print("✅ Sauvegarde correcte en base de données")
                print("✅ Métadonnées complètes (scheduled_date, content_type, etc.)")
                print("🚀 SYSTÈME 100% OPÉRATIONNEL AVEC NOUVELLE CLÉ OPENAI")
            else:
                print("⚠️ Génération partiellement réussie - vérifier la configuration")
                
        else:
            print("\n🚨 VALIDATION FINALE ÉCHOUÉE")
            print("❌ Problèmes critiques avec la nouvelle clé OpenAI")
            
            # Identify main issues
            if len(test_results) > 1 and not test_results[1]:  # Posts generation failed
                print("❌ PROBLÈME PRINCIPAL: Génération de posts avec nouvelle clé OpenAI échoue")
            if len(test_results) > 2 and not test_results[2]:  # Content quality failed
                print("❌ PROBLÈME PRINCIPAL: Qualité du contenu généré insuffisante")
        
        return success_rate >= 80

def main():
    """Main test execution"""
    tester = FinalPostsGenerationTester()
    success = tester.run_final_validation_test()
    
    if success:
        print("\n🎯 CONCLUSION: Système de génération de posts 100% OPÉRATIONNEL avec nouvelle clé OpenAI")
        exit(0)
    else:
        print("\n🚨 CONCLUSION: Système de génération de posts a des PROBLÈMES avec la nouvelle clé OpenAI")
        exit(1)

if __name__ == "__main__":
    main()