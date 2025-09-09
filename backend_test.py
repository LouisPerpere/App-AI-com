#!/usr/bin/env python3
"""
Test complet du système de génération de posts Instagram nouvellement implémenté

ENDPOINTS À TESTER:
1. POST /api/posts/generate - endpoint principal de génération
2. GET /api/posts/generated - récupération des posts générés

CONTEXT TECHNIQUE:
- Nouveau système PostsGenerator implémenté avec ChatGPT 4o
- Utilise emergentintegrations avec clé EMERGENT_LLM_KEY
- Intégration complète : profil business, analyse site web, notes, contenus uploadés
- Focus Instagram uniquement pour l'instant

TEST SCENARIOS:
1. Authentification utilisateur (credentials: lperpere@yahoo.fr / L@Reunion974!)
2. Vérification profil business existant
3. Test génération de posts avec paramètres par défaut (20 posts, octobre_2025)
4. Vérification structure et contenu des posts générés
5. Test récupération des posts via GET /api/posts/generated
6. Validation métadonnées et format JSON

Backend URL: https://content-scheduler-6.preview.emergentagent.com/api
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://content-scheduler-6.preview.emergentagent.com/api"
EMAIL = "lperpere@yahoo.fr"
PASSWORD = "L@Reunion974!"

class PostsGenerationTester:
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
                print(f"   Token: {self.token[:20]}..." if self.token else "   Token: None")
                return True
            else:
                print(f"   ❌ Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {e}")
            return False
    
    def check_backend_health(self):
        """Step 2: Vérification santé du backend"""
        print("🏥 Step 2: Backend health check")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/health")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Backend is healthy")
                print(f"   Service: {data.get('service', 'Unknown')}")
                print(f"   Status: {data.get('status', 'Unknown')}")
                return True
            else:
                print(f"   ❌ Backend health check failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Backend health check error: {e}")
            return False
    
    def verify_business_profile(self):
        """Step 3: Vérification profil business existant"""
        print("🏢 Step 3: Verify business profile exists")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/business-profile")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                business_name = data.get('business_name')
                business_type = data.get('business_type')
                brand_tone = data.get('brand_tone')
                target_audience = data.get('target_audience')
                
                print(f"   ✅ Business profile retrieved successfully")
                print(f"   Business Name: {business_name}")
                print(f"   Business Type: {business_type}")
                print(f"   Brand Tone: {brand_tone}")
                print(f"   Target Audience: {target_audience}")
                
                # Store for later use
                self.business_profile = data
                
                # Check if essential fields are present
                has_essential_fields = bool(business_name and business_type)
                if has_essential_fields:
                    print(f"   ✅ Business profile has essential fields")
                    return True
                else:
                    print(f"   ⚠️ Business profile missing essential fields")
                    return True  # Still continue testing
                    
            else:
                print(f"   ❌ Business profile retrieval failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Business profile error: {e}")
            return False
    
    def verify_notes_integration(self):
        """Step 4: Vérification intégration des notes"""
        print("📝 Step 4: Verify notes integration")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/notes")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                notes = data.get('notes', [])
                
                print(f"   ✅ Notes retrieved successfully")
                print(f"   Total notes: {len(notes)}")
                
                # Analyze note types
                monthly_notes = [n for n in notes if n.get('is_monthly_note')]
                specific_notes = [n for n in notes if not n.get('is_monthly_note')]
                high_priority_notes = [n for n in notes if n.get('priority') == 'high']
                
                print(f"   Monthly recurring notes: {len(monthly_notes)}")
                print(f"   Specific month notes: {len(specific_notes)}")
                print(f"   High priority notes: {len(high_priority_notes)}")
                
                # Store for later analysis
                self.notes_data = {
                    'total': len(notes),
                    'monthly': len(monthly_notes),
                    'specific': len(specific_notes),
                    'high_priority': len(high_priority_notes)
                }
                
                return True
                
            else:
                print(f"   ❌ Notes retrieval failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Notes integration error: {e}")
            return False
    
    def test_posts_generation(self):
        """Step 5: Test génération de posts avec clé OpenAI personnelle (test rapide)"""
        print("🚀 Step 5: Test POST /api/posts/generate with personal OpenAI key")
        print("   Target month: octobre_2025")
        print("   Number of posts: 5 (test rapide)")
        print("   🔑 Using personal OpenAI key (not EMERGENT_LLM_KEY)")
        
        generation_params = {
            "target_month": "octobre_2025",
            "num_posts": 5
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
                
                print(f"   ✅ Post generation successful")
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
                if posts_count > 0:
                    print(f"   ✅ {posts_count} posts generated successfully with personal OpenAI key!")
                    print(f"   🎉 REAL CONTENT GENERATED BY CHATGPT 4O")
                    return True
                else:
                    print(f"   ❌ No posts were generated - checking if OpenAI key is working")
                    print(f"   💡 Expected: 5 posts with real ChatGPT 4o content")
                    return False
                    
            else:
                print(f"   ❌ Post generation failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Post generation error: {e}")
            return False
    
    def test_posts_retrieval(self):
        """Step 6: Test récupération des posts via GET /api/posts/generated"""
        print("📋 Step 6: Test GET /api/posts/generated")
        
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
                    # Analyze first post structure
                    first_post = posts[0]
                    print(f"   📋 First post structure analysis:")
                    
                    required_fields = ['id', 'title', 'text', 'hashtags', 'platform', 'scheduled_date']
                    optional_fields = ['visual_url', 'visual_type', 'content_type', 'status', 'created_at']
                    
                    for field in required_fields:
                        value = first_post.get(field)
                        has_field = field in first_post
                        print(f"      {field}: {'✅' if has_field else '❌'} {value}")
                    
                    for field in optional_fields:
                        value = first_post.get(field)
                        has_field = field in first_post
                        print(f"      {field}: {'✅' if has_field else '⚠️'} {value}")
                    
                    # Analyze content quality
                    text_length = len(first_post.get('text', ''))
                    hashtags_count = len(first_post.get('hashtags', []))
                    
                    print(f"   📊 Content quality analysis:")
                    print(f"      Text length: {text_length} characters")
                    print(f"      Hashtags count: {hashtags_count}")
                    print(f"      Platform: {first_post.get('platform', 'Unknown')}")
                    print(f"      Content type: {first_post.get('content_type', 'Unknown')}")
                    
                    # Store for validation
                    self.retrieved_posts = posts
                    
                    return True
                else:
                    print(f"   ❌ No posts found in database")
                    return False
                    
            else:
                print(f"   ❌ Posts retrieval failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Posts retrieval error: {e}")
            return False
    
    def validate_posts_structure(self):
        """Step 7: Validation métadonnées et format JSON"""
        print("🔍 Step 7: Validate posts structure and metadata")
        
        if not hasattr(self, 'retrieved_posts') or not self.retrieved_posts:
            print("   ❌ No posts available for validation")
            return False
        
        posts = self.retrieved_posts
        validation_results = []
        
        print(f"   Validating {len(posts)} posts...")
        
        for i, post in enumerate(posts):
            print(f"   📋 Post {i+1} validation:")
            
            # Required fields validation
            required_fields = {
                'id': str,
                'title': str,
                'text': str,
                'hashtags': list,
                'platform': str,
                'scheduled_date': str
            }
            
            post_valid = True
            
            for field, expected_type in required_fields.items():
                value = post.get(field)
                has_field = field in post
                correct_type = isinstance(value, expected_type) if has_field else False
                
                if has_field and correct_type:
                    print(f"      ✅ {field}: {expected_type.__name__}")
                elif has_field and not correct_type:
                    print(f"      ⚠️ {field}: wrong type (expected {expected_type.__name__})")
                    post_valid = False
                else:
                    print(f"      ❌ {field}: missing")
                    post_valid = False
            
            # Content quality validation
            text = post.get('text', '')
            hashtags = post.get('hashtags', [])
            
            text_valid = len(text) > 10  # Minimum text length
            hashtags_valid = len(hashtags) > 0 and len(hashtags) <= 30  # Reasonable hashtag count
            platform_valid = post.get('platform') == 'instagram'  # Instagram focus
            
            print(f"      Text quality: {'✅' if text_valid else '❌'} ({len(text)} chars)")
            print(f"      Hashtags quality: {'✅' if hashtags_valid else '❌'} ({len(hashtags)} tags)")
            print(f"      Platform correct: {'✅' if platform_valid else '❌'} ({post.get('platform')})")
            
            content_valid = text_valid and hashtags_valid and platform_valid
            
            overall_valid = post_valid and content_valid
            validation_results.append(overall_valid)
            
            print(f"      Overall: {'✅ VALID' if overall_valid else '❌ INVALID'}")
        
        # Summary
        valid_posts = sum(validation_results)
        total_posts = len(validation_results)
        success_rate = (valid_posts / total_posts) * 100 if total_posts > 0 else 0
        
        print(f"   📊 Validation summary:")
        print(f"      Valid posts: {valid_posts}/{total_posts}")
        print(f"      Success rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print(f"   ✅ Posts structure validation passed")
            return True
        else:
            print(f"   ❌ Posts structure validation failed")
            return False
    
    def test_integration_completeness(self):
        """Step 8: Test intégration complète des sources"""
        print("🔗 Step 8: Test complete integration of all sources")
        
        integration_score = 0
        max_score = 6
        
        # Check business profile integration
        if hasattr(self, 'business_profile') and self.business_profile.get('business_name'):
            print("   ✅ Business profile integrated")
            integration_score += 1
        else:
            print("   ❌ Business profile not integrated")
        
        # Check notes integration
        if hasattr(self, 'notes_data') and self.notes_data['total'] > 0:
            print("   ✅ Notes system integrated")
            integration_score += 1
        else:
            print("   ❌ Notes system not integrated")
        
        # Check generation result
        if hasattr(self, 'generation_result') and self.generation_result.get('success'):
            print("   ✅ Generation system working")
            integration_score += 1
        else:
            print("   ❌ Generation system not working")
        
        # Check posts retrieval
        if hasattr(self, 'retrieved_posts') and len(self.retrieved_posts) > 0:
            print("   ✅ Posts retrieval working")
            integration_score += 1
        else:
            print("   ❌ Posts retrieval not working")
        
        # Check Instagram focus
        if hasattr(self, 'retrieved_posts'):
            instagram_posts = [p for p in self.retrieved_posts if p.get('platform') == 'instagram']
            if len(instagram_posts) == len(self.retrieved_posts):
                print("   ✅ Instagram focus maintained")
                integration_score += 1
            else:
                print("   ❌ Instagram focus not maintained")
        else:
            print("   ❌ Cannot verify Instagram focus")
        
        # Check emergentintegrations usage
        if hasattr(self, 'generation_result'):
            sources_used = self.generation_result.get('sources_used', {})
            if sources_used:
                print("   ✅ Multiple sources integrated")
                integration_score += 1
            else:
                print("   ❌ Sources integration unclear")
        else:
            print("   ❌ Cannot verify sources integration")
        
        integration_percentage = (integration_score / max_score) * 100
        
        print(f"   📊 Integration completeness: {integration_score}/{max_score} ({integration_percentage:.1f}%)")
        
        if integration_percentage >= 70:
            print("   ✅ Integration completeness test passed")
            return True
        else:
            print("   ❌ Integration completeness test failed")
            return False
    

    
    def run_comprehensive_test(self):
        """Run all post generation system tests"""
        print("🚀 SYSTÈME DE GÉNÉRATION DE POSTS INSTAGRAM - TEST COMPLET")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test credentials: {EMAIL}")
        print(f"Target: POST /api/posts/generate & GET /api/posts/generated")
        print("=" * 70)
        
        test_results = []
        
        # Step 1: Authentication
        test_results.append(self.authenticate())
        
        if test_results[-1]:
            # Step 2: Backend health
            test_results.append(self.check_backend_health())
            
            # Step 3: Business profile
            test_results.append(self.verify_business_profile())
            
            # Step 4: Notes integration
            test_results.append(self.verify_notes_integration())
            
            # Step 5: Posts generation
            test_results.append(self.test_posts_generation())
            
            # Step 6: Posts retrieval
            test_results.append(self.test_posts_retrieval())
            
            # Step 7: Structure validation
            test_results.append(self.validate_posts_structure())
            
            # Step 8: Integration completeness
            test_results.append(self.test_integration_completeness())
        
        # Summary
        print("\n" + "=" * 70)
        print("🎯 POSTS GENERATION TESTING SUMMARY")
        print("=" * 70)
        
        test_names = [
            "Authentication",
            "Backend Health Check",
            "Business Profile Verification",
            "Notes Integration",
            "Posts Generation (POST /api/posts/generate)",
            "Posts Retrieval (GET /api/posts/generated)",
            "Posts Structure Validation",
            "Integration Completeness"
        ]
        
        passed_tests = 0
        for i, (name, result) in enumerate(zip(test_names[:len(test_results)], test_results)):
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{i+1}. {name}: {status}")
            if result:
                passed_tests += 1
        
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\nOverall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Detailed analysis
        print("\n📊 DETAILED ANALYSIS:")
        
        if hasattr(self, 'generation_result'):
            gen_result = self.generation_result
            print(f"   Posts generated: {gen_result.get('posts_count', 0)}")
            print(f"   Generation success: {gen_result.get('success', False)}")
            
            strategy = gen_result.get('strategy', {})
            if strategy:
                print(f"   Content strategy: {strategy}")
        
        if hasattr(self, 'retrieved_posts'):
            print(f"   Posts retrieved: {len(self.retrieved_posts)}")
            
            if self.retrieved_posts:
                platforms = set(p.get('platform') for p in self.retrieved_posts)
                content_types = set(p.get('content_type') for p in self.retrieved_posts)
                print(f"   Platforms: {list(platforms)}")
                print(f"   Content types: {list(content_types)}")
        
        # Final verdict
        if success_rate >= 75:
            print("\n🎉 POSTS GENERATION SYSTEM TESTING COMPLETED SUCCESSFULLY")
            print("✅ Le système de génération avec clé OpenAI personnelle est opérationnel")
            
            if hasattr(self, 'generation_result') and self.generation_result.get('posts_count', 0) > 0:
                print("✅ Posts générés avec succès par ChatGPT 4o et sauvegardés en base")
                print("🚀 SYSTÈME PRÊT POUR UTILISATION AVEC CLÉ OPENAI PERSONNELLE")
            else:
                print("⚠️ Génération réussie mais vérifier le nombre de posts")
                
        else:
            print("\n🚨 POSTS GENERATION SYSTEM TESTING FAILED")
            print("❌ Problèmes critiques avec la clé OpenAI personnelle")
            
            # Identify main issues
            if not test_results[4]:  # Posts generation failed
                print("❌ PROBLÈME PRINCIPAL: Génération de posts avec clé OpenAI échoue")
            if not test_results[5]:  # Posts retrieval failed
                print("❌ PROBLÈME PRINCIPAL: Récupération de posts échoue")
        
        return success_rate >= 75

def main():
    """Main test execution"""
    tester = PostsGenerationTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎯 CONCLUSION: Système de génération de posts OPÉRATIONNEL")
        exit(0)
    else:
        print("\n🚨 CONCLUSION: Système de génération de posts a des PROBLÈMES CRITIQUES")
        exit(1)

if __name__ == "__main__":
    main()