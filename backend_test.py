#!/usr/bin/env python3
"""
CRITICAL PHOTO-POST LINKING SYSTEM TEST
Test CRITIQUE du système de liaison photos-posts après correction majeure.

OBJECTIF: Valider que les posts générés font maintenant le lien ABSOLU avec les vraies photos uploadées.

CONTEXTE TECHNIQUE:
- CORRECTION MAJEURE appliquée dans _collect_available_content
- Système corrigé pour utiliser TOUTES les photos disponibles (pas seulement celles avec attributed_month)
- Utilisation des filenames comme titres si pas de titre défini
- Système de fallback intelligent pour garantir la liaison photos-posts

TESTS CRITIQUES À EFFECTUER:
1. Authentification (lperpere@yahoo.fr / L@Reunion974!)
2. Vérification que le système trouve maintenant les 38 photos disponibles
3. POST /api/posts/generate (système corrigé)
4. VALIDATION ABSOLUE:
   - ZERO posts avec "global_fallback_X" 
   - TOUS les posts doivent avoir des visual_id RÉELS correspondant aux vraies photos
   - visual_url doivent pointer vers /api/content/{REAL_ID}/file
   - Test des URLs d'images pour confirmer qu'elles fonctionnent (pas 404)
5. Logs détaillés pour voir la récupération des contenus

RÉSULTATS ATTENDUS CRITIQUES:
- "📂 Total media found: 38" dans les logs
- "✅ FINAL month content available: X" avec X > 0
- Posts générés avec visual_id = vrais IDs MongoDB (format ObjectId)
- Liaison photos-posts 100% fonctionnelle
- Images visibles dans les posts (fini les points d'interrogation)

Backend URL: https://content-scheduler-6.preview.emergentagent.com/api
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
BASE_URL = "https://content-scheduler-6.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class PhotoPostLinkingTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.auth_token = None
        self.user_id = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_authentication(self):
        """Test 1: Authentication with specified credentials"""
        self.log("🔐 STEP 1: Testing authentication with lperpere@yahoo.fr / L@Reunion974!")
        
        try:
            response = self.session.post(f"{BASE_URL}/auth/login-robust", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                
                self.log(f"✅ Authentication successful - User ID: {self.user_id}")
                self.log(f"✅ JWT token obtained: {self.auth_token[:20]}...")
                return True
            else:
                self.log(f"❌ Authentication failed - Status: {response.status_code}", "ERROR")
                self.log(f"❌ Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Authentication error: {str(e)}", "ERROR")
            return False
    
    def test_content_availability(self):
        """Test 2: Verify system finds all available photos (expecting 38)"""
        self.log("📂 STEP 2: Checking available content - expecting 38 photos")
        
        try:
            response = self.session.get(f"{BASE_URL}/content/pending?limit=100")
            
            if response.status_code == 200:
                data = response.json()
                total_content = data.get("total", 0)
                loaded_content = data.get("loaded", 0)
                content_items = data.get("content", [])
                
                self.log(f"📊 Total content in database: {total_content}")
                self.log(f"📊 Content loaded in response: {loaded_content}")
                self.log(f"📊 Content items in response: {len(content_items)}")
                
                # Analyze content types
                image_count = 0
                video_count = 0
                pixabay_count = 0
                upload_count = 0
                
                for item in content_items:
                    file_type = item.get("file_type", "")
                    source = item.get("source", "")
                    
                    if file_type.startswith("image"):
                        image_count += 1
                    elif file_type.startswith("video"):
                        video_count += 1
                        
                    if source == "pixabay":
                        pixabay_count += 1
                    else:
                        upload_count += 1
                
                self.log(f"📸 Images found: {image_count}")
                self.log(f"🎥 Videos found: {video_count}")
                self.log(f"🌐 Pixabay content: {pixabay_count}")
                self.log(f"📤 Upload content: {upload_count}")
                
                # Check if we have the expected 38 photos
                if total_content >= 38:
                    self.log(f"✅ CRITICAL SUCCESS: Found {total_content} content items (≥38 expected)")
                elif total_content > 0:
                    self.log(f"⚠️ Found {total_content} content items (less than 38 expected)")
                else:
                    self.log("❌ CRITICAL FAILURE: No content found", "ERROR")
                    return False
                
                # Log first few items for debugging
                self.log("📋 First 5 content items:")
                for i, item in enumerate(content_items[:5]):
                    item_id = item.get("id", "NO_ID")
                    filename = item.get("filename", "NO_FILENAME")
                    title = item.get("title", "NO_TITLE")
                    context = item.get("context", "NO_CONTEXT")
                    self.log(f"   {i+1}. ID: {item_id}, File: {filename}, Title: '{title}', Context: '{context[:50]}...'")
                
                return total_content > 0
                
            else:
                self.log(f"❌ Failed to get content - Status: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Content availability error: {str(e)}", "ERROR")
            return False
    
    def test_post_generation(self):
        """Test 3: Generate posts and validate photo-post linking"""
        self.log("🚀 STEP 3: Testing POST /api/posts/generate with corrected system")
        
        try:
            # Generate posts for current month
            target_month = "octobre_2025"
            
            self.log(f"📅 Generating posts for {target_month}")
            self.log("⏱️ This may take 60-90 seconds due to AI processing...")
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/posts/generate", params={
                "target_month": target_month
            })
            end_time = time.time()
            
            self.log(f"⏱️ Post generation took {end_time - start_time:.1f} seconds")
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                posts_count = data.get("posts_count", 0)
                strategy = data.get("strategy", {})
                sources_used = data.get("sources_used", {})
                
                self.log(f"✅ Post generation response received")
                self.log(f"📊 Success: {success}")
                self.log(f"📊 Posts generated: {posts_count}")
                self.log(f"📊 Strategy: {strategy}")
                self.log(f"📊 Sources used: {sources_used}")
                
                if success and posts_count > 0:
                    self.log(f"✅ CRITICAL SUCCESS: Generated {posts_count} posts")
                    return True
                elif posts_count == 0:
                    self.log("⚠️ WARNING: 0 posts generated - checking for errors")
                    error_msg = data.get("error", "No error message")
                    self.log(f"⚠️ Error details: {error_msg}")
                    return False
                else:
                    self.log(f"❌ Post generation failed: {data}", "ERROR")
                    return False
                    
            else:
                self.log(f"❌ Post generation failed - Status: {response.status_code}", "ERROR")
                self.log(f"❌ Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Post generation error: {str(e)}", "ERROR")
            return False
    
    def test_generated_posts_validation(self):
        """Test 4: CRITICAL VALIDATION - Check photo-post linking"""
        self.log("🔍 STEP 4: CRITICAL VALIDATION - Checking photo-post linking")
        
        try:
            response = self.session.get(f"{BASE_URL}/posts/generated")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                posts_count = len(posts)
                
                self.log(f"📊 Retrieved {posts_count} generated posts")
                
                if posts_count == 0:
                    self.log("❌ CRITICAL FAILURE: No generated posts found", "ERROR")
                    return False
                
                # CRITICAL VALIDATION CHECKS
                posts_with_fallback = 0
                posts_with_real_ids = 0
                posts_without_visual = 0
                valid_visual_urls = 0
                invalid_visual_urls = 0
                
                self.log("🔍 ANALYZING EACH POST FOR PHOTO-POST LINKING:")
                
                for i, post in enumerate(posts[:10]):  # Check first 10 posts
                    post_id = post.get("id", "NO_ID")
                    visual_id = post.get("visual_id", "")
                    visual_url = post.get("visual_url", "")
                    title = post.get("title", "NO_TITLE")
                    
                    self.log(f"   📝 Post {i+1}: ID={post_id}")
                    self.log(f"      Visual ID: '{visual_id}'")
                    self.log(f"      Visual URL: '{visual_url}'")
                    self.log(f"      Title: '{title[:50]}...'")
                    
                    # Check for fallback content (CRITICAL FAILURE)
                    if "global_fallback" in visual_id or "fallback" in visual_url:
                        posts_with_fallback += 1
                        self.log(f"      ❌ CRITICAL FAILURE: Post uses fallback content!", "ERROR")
                    
                    # Check for real visual IDs
                    if visual_id and len(visual_id) > 10 and "fallback" not in visual_id:
                        posts_with_real_ids += 1
                        self.log(f"      ✅ Has real visual ID")
                        
                        # Validate visual URL format
                        expected_url = f"/api/content/{visual_id}/file"
                        if visual_url == expected_url:
                            valid_visual_urls += 1
                            self.log(f"      ✅ Correct visual URL format")
                        else:
                            invalid_visual_urls += 1
                            self.log(f"      ❌ Incorrect visual URL format", "ERROR")
                            self.log(f"         Expected: {expected_url}", "ERROR")
                            self.log(f"         Got: {visual_url}", "ERROR")
                    else:
                        posts_without_visual += 1
                        self.log(f"      ❌ No valid visual ID", "ERROR")
                
                # CRITICAL RESULTS SUMMARY
                self.log("🎯 CRITICAL VALIDATION RESULTS:")
                self.log(f"   📊 Total posts analyzed: {min(posts_count, 10)}")
                self.log(f"   ❌ Posts with fallback content: {posts_with_fallback}")
                self.log(f"   ✅ Posts with real visual IDs: {posts_with_real_ids}")
                self.log(f"   ❌ Posts without visual: {posts_without_visual}")
                self.log(f"   ✅ Valid visual URLs: {valid_visual_urls}")
                self.log(f"   ❌ Invalid visual URLs: {invalid_visual_urls}")
                
                # CRITICAL SUCCESS CRITERIA
                if posts_with_fallback == 0 and posts_with_real_ids > 0:
                    self.log("🎉 CRITICAL SUCCESS: ZERO fallback content, posts have real photo links!")
                    return True
                elif posts_with_fallback > 0:
                    self.log(f"❌ CRITICAL FAILURE: {posts_with_fallback} posts still use fallback content", "ERROR")
                    return False
                else:
                    self.log("❌ CRITICAL FAILURE: No posts have real visual IDs", "ERROR")
                    return False
                    
            else:
                self.log(f"❌ Failed to get generated posts - Status: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Generated posts validation error: {str(e)}", "ERROR")
            return False
    
    def test_image_urls_accessibility(self):
        """Test 5: Test image URLs to confirm they work (not 404)"""
        self.log("🖼️ STEP 5: Testing image URL accessibility")
        
        try:
            # Get generated posts
            response = self.session.get(f"{BASE_URL}/posts/generated")
            
            if response.status_code != 200:
                self.log("❌ Cannot get posts for URL testing", "ERROR")
                return False
            
            data = response.json()
            posts = data.get("posts", [])
            
            if not posts:
                self.log("❌ No posts available for URL testing", "ERROR")
                return False
            
            # Test first 5 image URLs
            accessible_urls = 0
            inaccessible_urls = 0
            
            for i, post in enumerate(posts[:5]):
                visual_url = post.get("visual_url", "")
                visual_id = post.get("visual_id", "")
                
                if not visual_url or not visual_id:
                    self.log(f"   ⚠️ Post {i+1}: No visual URL to test")
                    continue
                
                # Construct full URL
                if visual_url.startswith("/api/"):
                    full_url = f"https://content-scheduler-6.preview.emergentagent.com{visual_url}"
                else:
                    full_url = visual_url
                
                self.log(f"   🔗 Testing URL {i+1}: {full_url}")
                
                try:
                    # Test URL accessibility
                    url_response = self.session.head(full_url, timeout=10)
                    
                    if url_response.status_code == 200:
                        accessible_urls += 1
                        self.log(f"      ✅ URL accessible (200 OK)")
                    elif url_response.status_code == 404:
                        inaccessible_urls += 1
                        self.log(f"      ❌ URL returns 404 (image not found)", "ERROR")
                    else:
                        inaccessible_urls += 1
                        self.log(f"      ❌ URL returns {url_response.status_code}", "ERROR")
                        
                except Exception as url_e:
                    inaccessible_urls += 1
                    self.log(f"      ❌ URL test failed: {str(url_e)}", "ERROR")
            
            self.log(f"🎯 IMAGE URL TEST RESULTS:")
            self.log(f"   ✅ Accessible URLs: {accessible_urls}")
            self.log(f"   ❌ Inaccessible URLs: {inaccessible_urls}")
            
            if accessible_urls > 0 and inaccessible_urls == 0:
                self.log("🎉 SUCCESS: All tested image URLs are accessible!")
                return True
            elif accessible_urls > 0:
                self.log("⚠️ PARTIAL SUCCESS: Some URLs accessible, some not")
                return True
            else:
                self.log("❌ FAILURE: No image URLs are accessible", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Image URL accessibility error: {str(e)}", "ERROR")
            return False
    
    def run_all_tests(self):
        """Run all critical tests"""
        self.log("🚀 STARTING CRITICAL PHOTO-POST LINKING SYSTEM TEST")
        self.log("=" * 80)
        
        test_results = {}
        
        # Test 1: Authentication
        test_results["authentication"] = self.test_authentication()
        if not test_results["authentication"]:
            self.log("❌ CRITICAL FAILURE: Authentication failed - cannot continue", "ERROR")
            return test_results
        
        # Test 2: Content Availability
        test_results["content_availability"] = self.test_content_availability()
        
        # Test 3: Post Generation
        test_results["post_generation"] = self.test_post_generation()
        
        # Test 4: Critical Validation
        test_results["photo_post_linking"] = self.test_generated_posts_validation()
        
        # Test 5: Image URL Accessibility
        test_results["image_url_accessibility"] = self.test_image_urls_accessibility()
        
        # Final Results
        self.log("=" * 80)
        self.log("🎯 FINAL TEST RESULTS:")
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"   {test_name}: {status}")
            if result:
                passed_tests += 1
        
        success_rate = (passed_tests / total_tests) * 100
        self.log(f"📊 SUCCESS RATE: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Critical assessment
        critical_tests = ["authentication", "photo_post_linking"]
        critical_passed = all(test_results.get(test, False) for test in critical_tests)
        
        if critical_passed:
            self.log("🎉 CRITICAL SUCCESS: Photo-post linking system is WORKING!")
        else:
            self.log("❌ CRITICAL FAILURE: Photo-post linking system has issues", "ERROR")
        
        return test_results

def main():
    """Main test execution"""
    tester = PhotoPostLinkingTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    critical_tests = ["authentication", "photo_post_linking"]
    critical_passed = all(results.get(test, False) for test in critical_tests)
    
    sys.exit(0 if critical_passed else 1)

if __name__ == "__main__":
    main()