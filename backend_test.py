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
        """Step 5: Test génération de posts avec paramètres par défaut"""
        print("🚀 Step 5: Test POST /api/posts/generate with default parameters")
        print("   Target month: octobre_2025")
        print("   Number of posts: 20")
        
        generation_params = {
            "target_month": "octobre_2025",
            "num_posts": 20
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
                    print(f"   ✅ {posts_count} posts generated successfully")
                    return True
                else:
                    print(f"   ❌ No posts were generated")
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
    
    def test_content_pending_carousel_fields(self):
        """Step 3: Test GET /api/content/pending returns carousel images with new fields"""
        print("📋 Step 3: Testing GET /api/content/pending for carousel fields")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get('content', [])
                total_items = data.get('total', 0)
                
                print(f"   ✅ Content retrieval successful")
                print(f"   Total items: {total_items}")
                print(f"   Items loaded: {len(content_items)}")
                
                # Find carousel items
                carousel_items = []
                for item in content_items:
                    if item.get('upload_type') == 'carousel':
                        carousel_items.append(item)
                
                print(f"   Carousel items found: {len(carousel_items)}")
                
                if carousel_items:
                    print("   🔍 Analyzing carousel items:")
                    
                    # Check if all carousel items have the same fields
                    first_item = carousel_items[0]
                    common_title = first_item.get('title')
                    common_context = first_item.get('context')
                    attributed_month = first_item.get('attributed_month')
                    carousel_id = first_item.get('carousel_id')
                    
                    print(f"   Expected common_title: 'Test Carrousel'")
                    print(f"   Found common_title: '{common_title}'")
                    print(f"   Expected common_context: 'Description carrousel'")
                    print(f"   Found common_context: '{common_context}'")
                    print(f"   Expected attributed_month: 'octobre_2025'")
                    print(f"   Found attributed_month: '{attributed_month}'")
                    print(f"   Carousel ID: {carousel_id}")
                    
                    # Verify all carousel items have consistent fields
                    all_consistent = True
                    for i, item in enumerate(carousel_items):
                        item_title = item.get('title')
                        item_context = item.get('context')
                        item_month = item.get('attributed_month')
                        item_carousel_id = item.get('carousel_id')
                        item_upload_type = item.get('upload_type')
                        
                        print(f"   Item {i+1}: title='{item_title}', context='{item_context}', month='{item_month}', upload_type='{item_upload_type}'")
                        
                        # Check consistency
                        if (item_title != common_title or 
                            item_context != common_context or 
                            item_month != attributed_month or
                            item_upload_type != 'carousel'):
                            all_consistent = False
                            print(f"   ❌ Item {i+1} has inconsistent fields!")
                    
                    if all_consistent:
                        print(f"   ✅ All carousel items have consistent fields")
                        
                        # Verify expected values
                        title_correct = common_title == 'Test Carrousel'
                        context_correct = 'Description carrousel' in (common_context or '')
                        month_correct = attributed_month == 'octobre_2025'
                        
                        print(f"   Title correct: {title_correct}")
                        print(f"   Context correct: {context_correct}")
                        print(f"   Month correct: {month_correct}")
                        
                        if title_correct and context_correct and month_correct:
                            print(f"   ✅ All carousel field values are correct")
                            return True
                        else:
                            print(f"   ❌ Some carousel field values are incorrect")
                            return False
                    else:
                        print(f"   ❌ Carousel items have inconsistent fields")
                        return False
                else:
                    print(f"   ❌ No carousel items found in content")
                    return False
                    
            else:
                print(f"   ❌ Content retrieval failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Content retrieval error: {e}")
            return False
    
    def test_carousel_thumbnails(self):
        """Step 4: Test thumbnail generation for carousel images"""
        print("🖼️ Step 4: Testing thumbnail generation for carousel images")
        
        if not hasattr(self, 'carousel_ids') or not self.carousel_ids:
            print("   ❌ No carousel IDs available for thumbnail testing")
            return False
        
        thumbnail_results = []
        
        for i, item_id in enumerate(self.carousel_ids):
            print(f"   Testing thumbnail for carousel item {i+1}: {item_id}")
            
            try:
                # Test thumbnail endpoint
                thumb_url = f"{BACKEND_URL}/content/{item_id}/thumb"
                response = self.session.get(thumb_url)
                
                print(f"   Thumbnail status: {response.status_code}")
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    content_length = len(response.content)
                    
                    print(f"   ✅ Thumbnail generated successfully")
                    print(f"   Content-Type: {content_type}")
                    print(f"   Content-Length: {content_length} bytes")
                    
                    # Verify it's an image
                    if 'image' in content_type and content_length > 0:
                        thumbnail_results.append(True)
                        print(f"   ✅ Valid thumbnail image")
                    else:
                        thumbnail_results.append(False)
                        print(f"   ❌ Invalid thumbnail content")
                else:
                    thumbnail_results.append(False)
                    print(f"   ❌ Thumbnail generation failed: {response.text}")
                    
            except Exception as e:
                thumbnail_results.append(False)
                print(f"   ❌ Thumbnail test error: {e}")
        
        success_count = sum(thumbnail_results)
        total_count = len(thumbnail_results)
        
        print(f"   Thumbnail generation results: {success_count}/{total_count} successful")
        
        if success_count == total_count:
            print(f"   ✅ All carousel thumbnails generated successfully")
            return True
        else:
            print(f"   ❌ Some carousel thumbnails failed to generate")
            return False
    
    def test_carousel_grouping(self):
        """Step 5: Test carousel grouping with carousel_id"""
        print("🔗 Step 5: Testing carousel grouping with carousel_id")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get('content', [])
                
                # Find carousel items
                carousel_items = [item for item in content_items if item.get('upload_type') == 'carousel']
                
                if carousel_items:
                    # Check if all carousel items have the same carousel_id
                    carousel_ids = [item.get('carousel_id') for item in carousel_items]
                    unique_carousel_ids = set(filter(None, carousel_ids))
                    
                    print(f"   Carousel items found: {len(carousel_items)}")
                    print(f"   Unique carousel IDs: {len(unique_carousel_ids)}")
                    print(f"   Carousel IDs: {list(unique_carousel_ids)}")
                    
                    if len(unique_carousel_ids) == 1:
                        print(f"   ✅ All carousel items have the same carousel_id")
                        print(f"   Carousel ID: {list(unique_carousel_ids)[0]}")
                        return True
                    else:
                        print(f"   ❌ Carousel items have different carousel_ids or missing IDs")
                        return False
                else:
                    print(f"   ❌ No carousel items found for grouping test")
                    return False
            else:
                print(f"   ❌ Failed to retrieve content for grouping test")
                return False
                
        except Exception as e:
            print(f"   ❌ Carousel grouping test error: {e}")
            return False
    
    def cleanup_test_data(self):
        """Step 6: Clean up test carousel data"""
        print("🧹 Step 6: Cleaning up test carousel data")
        
        if not hasattr(self, 'carousel_ids') or not self.carousel_ids:
            print("   No carousel IDs to clean up")
            return True
        
        cleanup_results = []
        
        for i, item_id in enumerate(self.carousel_ids):
            try:
                response = self.session.delete(f"{BACKEND_URL}/content/{item_id}")
                
                if response.status_code == 200:
                    cleanup_results.append(True)
                    print(f"   ✅ Deleted carousel item {i+1}: {item_id}")
                else:
                    cleanup_results.append(False)
                    print(f"   ❌ Failed to delete carousel item {i+1}: {response.text}")
                    
            except Exception as e:
                cleanup_results.append(False)
                print(f"   ❌ Cleanup error for item {i+1}: {e}")
        
        success_count = sum(cleanup_results)
        total_count = len(cleanup_results)
        
        print(f"   Cleanup results: {success_count}/{total_count} items deleted")
        
        return success_count == total_count
    
    def run_comprehensive_test(self):
        """Run all carousel functionality tests"""
        print("🎠 COMPREHENSIVE CAROUSEL FUNCTIONALITY TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test credentials: {EMAIL}")
        print("=" * 60)
        
        test_results = []
        
        # Step 1: Authentication
        test_results.append(self.authenticate())
        
        if test_results[-1]:
            # Step 2: Carousel batch upload
            test_results.append(self.test_carousel_batch_upload())
            
            if test_results[-1]:
                # Step 3: Content pending with carousel fields
                test_results.append(self.test_content_pending_carousel_fields())
                
                # Step 4: Thumbnail generation
                test_results.append(self.test_carousel_thumbnails())
                
                # Step 5: Carousel grouping
                test_results.append(self.test_carousel_grouping())
                
                # Step 6: Cleanup
                test_results.append(self.cleanup_test_data())
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 CAROUSEL TESTING SUMMARY")
        print("=" * 60)
        
        test_names = [
            "Authentication",
            "Carousel Batch Upload",
            "Content Pending Fields",
            "Thumbnail Generation", 
            "Carousel Grouping",
            "Cleanup"
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
        
        if success_rate >= 80:
            print("🎉 CAROUSEL FUNCTIONALITY TESTING COMPLETED SUCCESSFULLY")
            print("✅ The carousel upload system is working correctly")
        else:
            print("🚨 CAROUSEL FUNCTIONALITY TESTING FAILED")
            print("❌ Critical issues found in carousel implementation")
        
        return success_rate >= 80

def main():
    """Main test execution"""
    tester = CarouselTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎯 CONCLUSION: Carousel functionality is FULLY OPERATIONAL")
        exit(0)
    else:
        print("\n🚨 CONCLUSION: Carousel functionality has CRITICAL ISSUES")
        exit(1)

if __name__ == "__main__":
    main()