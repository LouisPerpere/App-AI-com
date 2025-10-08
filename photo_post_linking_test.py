#!/usr/bin/env python3
"""
Test critique du système de liaison photos-posts corrigé
Critical testing of the corrected photo-post linking system

OBJECTIF: Valider que les posts générés font maintenant le lien correct avec les photos uploadées.

CONTEXTE TECHNIQUE:
- Corrections appliquées pour résoudre le problème d'affichage des photos
- Inventory maintenant envoyé avec IDs des photos: "ID:12345 - titre - contexte"  
- Format JSON corrigé: "visual_id" au lieu de "visual_content_used"
- Parsing corrigé pour utiliser les vrais IDs au lieu de "global_fallback_X"

Backend URL: https://post-restore.preview.emergentagent.com/api
Credentials: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import time
import sys
from datetime import datetime

class PhotoPostLinkingTester:
    def __init__(self):
        self.base_url = "https://post-restore.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.user_id = None
        self.jwt_token = None
        self.test_results = []
        self.uploaded_content_ids = []
        
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
    
    def verify_existing_content(self):
        """Step 2: Vérifier contenus uploadés existants pour avoir des IDs de référence"""
        try:
            response = self.session.get(f"{self.base_url}/content/pending")
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                total_items = data.get("total", 0)
                
                # Extract content IDs and analyze structure
                self.uploaded_content_ids = []
                content_analysis = {
                    "total_items": total_items,
                    "items_with_ids": 0,
                    "items_with_titles": 0,
                    "items_with_context": 0,
                    "sample_ids": []
                }
                
                for item in content_items:
                    item_id = item.get("id")
                    title = item.get("title", "")
                    context = item.get("context", "")
                    filename = item.get("filename", "")
                    
                    if item_id:
                        self.uploaded_content_ids.append(item_id)
                        content_analysis["items_with_ids"] += 1
                        
                        # Store first 5 IDs as samples
                        if len(content_analysis["sample_ids"]) < 5:
                            content_analysis["sample_ids"].append({
                                "id": item_id,
                                "title": title or filename,
                                "context": context[:50] + "..." if len(context) > 50 else context
                            })
                    
                    if title:
                        content_analysis["items_with_titles"] += 1
                    if context:
                        content_analysis["items_with_context"] += 1
                
                self.log_test(2, "PASS", "Content verification successful", 
                            f"Found {total_items} items, {len(self.uploaded_content_ids)} with valid IDs")
                
                print(f"\n📋 CONTENT ANALYSIS:")
                print(f"   Total items: {content_analysis['total_items']}")
                print(f"   Items with IDs: {content_analysis['items_with_ids']}")
                print(f"   Items with titles: {content_analysis['items_with_titles']}")
                print(f"   Items with context: {content_analysis['items_with_context']}")
                print(f"\n📝 SAMPLE CONTENT IDS:")
                for i, sample in enumerate(content_analysis["sample_ids"], 1):
                    print(f"   {i}. ID: {sample['id']}")
                    print(f"      Title: {sample['title']}")
                    print(f"      Context: {sample['context']}")
                
                return content_analysis
            else:
                self.log_test(2, "FAIL", "Failed to retrieve content", 
                            f"Status: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test(2, "FAIL", "Content verification error", str(e))
            return None
    
    def trigger_post_generation(self):
        """Step 3: POST /api/posts/generate (nouveau système)"""
        try:
            print(f"\n🚀 TRIGGERING POST GENERATION WITH PHOTO LINKING")
            print("=" * 60)
            
            # Record start time
            start_time = time.time()
            
            # Trigger post generation
            generation_data = {
                "target_month": "octobre_2025"
            }
            
            print(f"⏱️ Starting generation at {datetime.now().strftime('%H:%M:%S')}")
            print(f"📸 Available content IDs: {len(self.uploaded_content_ids)}")
            
            response = self.session.post(f"{self.base_url}/posts/generate", 
                                       params=generation_data, timeout=180)
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            print(f"⏱️ Generation completed at {datetime.now().strftime('%H:%M:%S')}")
            print(f"⏱️ Total generation time: {generation_time:.2f} seconds")
            
            if response.status_code == 200:
                data = response.json()
                posts_count = data.get("posts_count", 0)
                success = data.get("success", False)
                
                self.log_test(3, "PASS", "Post generation triggered successfully", 
                            f"Generated: {posts_count} posts, Time: {generation_time:.2f}s, Success: {success}")
                
                return {
                    "success": success,
                    "posts_count": posts_count,
                    "generation_time": generation_time,
                    "response_data": data
                }
            else:
                error_msg = response.text
                self.log_test(3, "FAIL", "Post generation failed", 
                            f"Status: {response.status_code}, Error: {error_msg}")
                return None
                
        except Exception as e:
            self.log_test(3, "FAIL", "Post generation error", str(e))
            return None
    
    def analyze_chatgpt_response(self):
        """Step 4: ANALYSE DÉTAILLÉE de la réponse ChatGPT"""
        try:
            response = self.session.get(f"{self.base_url}/posts/generated")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                
                print(f"\n🔍 CRITICAL CHATGPT RESPONSE ANALYSIS")
                print("=" * 50)
                
                if not posts:
                    self.log_test(4, "FAIL", "No posts found for analysis", None)
                    return None
                
                analysis_results = {
                    "total_posts": len(posts),
                    "posts_with_visual_id": 0,
                    "posts_with_visual_url": 0,
                    "posts_with_real_ids": 0,
                    "posts_with_fallback_ids": 0,
                    "visual_id_samples": [],
                    "visual_url_samples": [],
                    "fallback_id_found": [],
                    "real_id_matches": 0
                }
                
                print(f"📊 Analyzing {len(posts)} generated posts...")
                
                for i, post in enumerate(posts, 1):
                    visual_id = post.get("visual_id", "")
                    visual_url = post.get("visual_url", "")
                    title = post.get("title", "")
                    
                    # Check for visual_id field
                    if visual_id:
                        analysis_results["posts_with_visual_id"] += 1
                        
                        # Check if it's a real ID (in our uploaded content) vs fallback
                        if visual_id in self.uploaded_content_ids:
                            analysis_results["posts_with_real_ids"] += 1
                            analysis_results["real_id_matches"] += 1
                            print(f"   ✅ Post {i}: Real ID found - {visual_id}")
                        elif "global_fallback" in visual_id.lower():
                            analysis_results["posts_with_fallback_ids"] += 1
                            analysis_results["fallback_id_found"].append(visual_id)
                            print(f"   ❌ Post {i}: Fallback ID found - {visual_id}")
                        else:
                            print(f"   ⚠️ Post {i}: Unknown ID format - {visual_id}")
                        
                        # Store sample for detailed analysis
                        if len(analysis_results["visual_id_samples"]) < 5:
                            analysis_results["visual_id_samples"].append({
                                "post_index": i,
                                "visual_id": visual_id,
                                "title": title,
                                "is_real_id": visual_id in self.uploaded_content_ids,
                                "is_fallback": "global_fallback" in visual_id.lower()
                            })
                    
                    # Check for visual_url field
                    if visual_url:
                        analysis_results["posts_with_visual_url"] += 1
                        
                        # Verify URL format: should be /api/content/{real_id}/file
                        expected_pattern = "/api/content/"
                        if expected_pattern in visual_url and "/file" in visual_url:
                            # Extract ID from URL
                            try:
                                url_id = visual_url.split("/api/content/")[1].split("/file")[0]
                                if url_id in self.uploaded_content_ids:
                                    print(f"   ✅ Post {i}: Correct visual_url format with real ID")
                                else:
                                    print(f"   ⚠️ Post {i}: Correct format but unknown ID in URL")
                            except:
                                print(f"   ❌ Post {i}: Malformed visual_url")
                        else:
                            print(f"   ❌ Post {i}: Incorrect visual_url format")
                        
                        # Store sample
                        if len(analysis_results["visual_url_samples"]) < 5:
                            analysis_results["visual_url_samples"].append({
                                "post_index": i,
                                "visual_url": visual_url,
                                "title": title
                            })
                
                # Print detailed analysis
                print(f"\n📋 DETAILED ANALYSIS RESULTS:")
                print(f"   Total posts analyzed: {analysis_results['total_posts']}")
                print(f"   Posts with visual_id: {analysis_results['posts_with_visual_id']}")
                print(f"   Posts with visual_url: {analysis_results['posts_with_visual_url']}")
                print(f"   Posts with REAL IDs: {analysis_results['posts_with_real_ids']}")
                print(f"   Posts with FALLBACK IDs: {analysis_results['posts_with_fallback_ids']}")
                print(f"   Real ID matches: {analysis_results['real_id_matches']}")
                
                if analysis_results["fallback_id_found"]:
                    print(f"\n❌ FALLBACK IDs DETECTED:")
                    for fallback_id in analysis_results["fallback_id_found"]:
                        print(f"   - {fallback_id}")
                
                print(f"\n📝 VISUAL_ID SAMPLES:")
                for sample in analysis_results["visual_id_samples"]:
                    status = "✅ REAL" if sample["is_real_id"] else "❌ FALLBACK" if sample["is_fallback"] else "⚠️ UNKNOWN"
                    print(f"   Post {sample['post_index']}: {status}")
                    print(f"      ID: {sample['visual_id']}")
                    print(f"      Title: {sample['title']}")
                
                print(f"\n🔗 VISUAL_URL SAMPLES:")
                for sample in analysis_results["visual_url_samples"]:
                    print(f"   Post {sample['post_index']}: {sample['visual_url']}")
                
                # Success criteria assessment
                success_rate = (analysis_results["posts_with_real_ids"] / analysis_results["total_posts"]) * 100 if analysis_results["total_posts"] > 0 else 0
                
                if analysis_results["posts_with_fallback_ids"] == 0 and analysis_results["posts_with_real_ids"] > 0:
                    self.log_test(4, "PASS", "ChatGPT response analysis successful - NO fallback IDs found", 
                                f"Real IDs: {analysis_results['posts_with_real_ids']}, Success rate: {success_rate:.1f}%")
                elif analysis_results["posts_with_fallback_ids"] > 0:
                    self.log_test(4, "FAIL", "ChatGPT response analysis failed - Fallback IDs still present", 
                                f"Fallback IDs: {analysis_results['posts_with_fallback_ids']}, Real IDs: {analysis_results['posts_with_real_ids']}")
                else:
                    self.log_test(4, "WARN", "ChatGPT response analysis inconclusive", 
                                f"No visual IDs found in posts")
                
                return analysis_results
            else:
                self.log_test(4, "FAIL", "Failed to retrieve posts for analysis", 
                            f"Status: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test(4, "FAIL", "ChatGPT response analysis error", str(e))
            return None
    
    def verify_post_persistence(self):
        """Step 5: GET /api/posts/generated pour vérifier la persistance"""
        try:
            response = self.session.get(f"{self.base_url}/posts/generated")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                
                persistence_check = {
                    "total_posts": len(posts),
                    "posts_persisted": len(posts) > 0,
                    "posts_with_complete_data": 0,
                    "posts_with_visual_data": 0
                }
                
                for post in posts:
                    # Check if post has complete data structure
                    required_fields = ["id", "title", "text", "hashtags"]
                    visual_fields = ["visual_id", "visual_url"]
                    
                    has_complete_data = all(post.get(field) for field in required_fields)
                    has_visual_data = any(post.get(field) for field in visual_fields)
                    
                    if has_complete_data:
                        persistence_check["posts_with_complete_data"] += 1
                    if has_visual_data:
                        persistence_check["posts_with_visual_data"] += 1
                
                self.log_test(5, "PASS", "Post persistence verification successful", 
                            f"Posts persisted: {persistence_check['total_posts']}, "
                            f"Complete data: {persistence_check['posts_with_complete_data']}, "
                            f"Visual data: {persistence_check['posts_with_visual_data']}")
                
                return persistence_check
            else:
                self.log_test(5, "FAIL", "Failed to verify post persistence", 
                            f"Status: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test(5, "FAIL", "Post persistence verification error", str(e))
            return None
    
    def test_image_display(self, analysis_results):
        """Step 6: Test manuel d'affichage d'une image via visual_url construite"""
        try:
            if not analysis_results or not analysis_results.get("visual_url_samples"):
                self.log_test(6, "FAIL", "No visual URLs available for testing", None)
                return None
            
            print(f"\n🖼️ TESTING IMAGE DISPLAY VIA VISUAL_URL")
            print("=" * 45)
            
            display_test_results = {
                "urls_tested": 0,
                "successful_responses": 0,
                "failed_responses": 0,
                "test_details": []
            }
            
            # Test first 3 visual URLs
            for sample in analysis_results["visual_url_samples"][:3]:
                visual_url = sample["visual_url"]
                post_index = sample["post_index"]
                
                # Construct full URL
                if visual_url.startswith("/api/"):
                    full_url = f"{self.base_url.replace('/api', '')}{visual_url}"
                else:
                    full_url = f"{self.base_url}/{visual_url.lstrip('/')}"
                
                print(f"   Testing URL {post_index}: {full_url}")
                
                try:
                    # Test image URL accessibility
                    response = self.session.get(full_url, timeout=10)
                    display_test_results["urls_tested"] += 1
                    
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '')
                        content_length = len(response.content)
                        
                        if 'image' in content_type and content_length > 0:
                            display_test_results["successful_responses"] += 1
                            print(f"      ✅ SUCCESS: {content_type}, {content_length} bytes")
                        else:
                            display_test_results["failed_responses"] += 1
                            print(f"      ❌ INVALID: {content_type}, {content_length} bytes")
                    else:
                        display_test_results["failed_responses"] += 1
                        print(f"      ❌ HTTP {response.status_code}: {response.reason}")
                    
                    display_test_results["test_details"].append({
                        "post_index": post_index,
                        "url": full_url,
                        "status_code": response.status_code,
                        "content_type": response.headers.get('content-type', ''),
                        "content_length": len(response.content),
                        "success": response.status_code == 200 and 'image' in response.headers.get('content-type', '')
                    })
                    
                except Exception as url_error:
                    display_test_results["failed_responses"] += 1
                    print(f"      ❌ ERROR: {str(url_error)}")
                    
                    display_test_results["test_details"].append({
                        "post_index": post_index,
                        "url": full_url,
                        "error": str(url_error),
                        "success": False
                    })
            
            # Assessment
            success_rate = (display_test_results["successful_responses"] / display_test_results["urls_tested"]) * 100 if display_test_results["urls_tested"] > 0 else 0
            
            if success_rate >= 80:
                self.log_test(6, "PASS", "Image display test successful", 
                            f"Success rate: {success_rate:.1f}% ({display_test_results['successful_responses']}/{display_test_results['urls_tested']})")
            elif success_rate >= 50:
                self.log_test(6, "WARN", "Image display test partially successful", 
                            f"Success rate: {success_rate:.1f}% ({display_test_results['successful_responses']}/{display_test_results['urls_tested']})")
            else:
                self.log_test(6, "FAIL", "Image display test failed", 
                            f"Success rate: {success_rate:.1f}% ({display_test_results['successful_responses']}/{display_test_results['urls_tested']})")
            
            return display_test_results
            
        except Exception as e:
            self.log_test(6, "FAIL", "Image display test error", str(e))
            return None
    
    def run_comprehensive_test(self):
        """Run the complete photo-post linking test suite"""
        print("🔗 SYSTÈME DE LIAISON PHOTOS-POSTS - TEST CRITIQUE")
        print("=" * 60)
        print("OBJECTIF: Valider que les posts générés font le lien correct avec les photos")
        print("Backend URL:", self.base_url)
        print("Credentials: lperpere@yahoo.fr / L@Reunion974!")
        print("=" * 60)
        
        # Step 1: Authentication
        if not self.authenticate():
            return False
        
        # Step 2: Verify existing uploaded content
        content_analysis = self.verify_existing_content()
        if content_analysis is None:
            return False
        
        if len(self.uploaded_content_ids) == 0:
            print("⚠️ WARNING: No uploaded content found. Photo linking cannot be tested.")
            return False
        
        # Step 3: Trigger post generation
        generation_result = self.trigger_post_generation()
        if generation_result is None:
            return False
        
        # Step 4: Analyze ChatGPT response for correct photo linking
        analysis_results = self.analyze_chatgpt_response()
        if analysis_results is None:
            return False
        
        # Step 5: Verify post persistence
        persistence_check = self.verify_post_persistence()
        
        # Step 6: Test image display
        display_test_results = self.test_image_display(analysis_results)
        
        # Final summary
        self.print_final_summary(content_analysis, generation_result, analysis_results, persistence_check, display_test_results)
        
        return True
    
    def print_final_summary(self, content_analysis, generation_result, analysis_results, persistence_check, display_test_results):
        """Print comprehensive test summary"""
        print(f"\n" + "=" * 70)
        print("🎯 RÉSULTATS FINAUX - SYSTÈME DE LIAISON PHOTOS-POSTS")
        print("=" * 70)
        
        # Test results summary
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"📊 TAUX DE RÉUSSITE: {passed_tests}/{total_tests} tests ({success_rate:.1f}%)")
        
        # Key findings
        print(f"\n🔍 RÉSULTATS CRITIQUES:")
        
        if content_analysis:
            print(f"📋 CONTENU DISPONIBLE: {content_analysis['total_items']} éléments, {len(self.uploaded_content_ids)} IDs valides")
        
        if generation_result:
            posts_generated = generation_result.get("posts_count", 0)
            print(f"📝 POSTS GÉNÉRÉS: {posts_generated} posts")
        
        if analysis_results:
            real_ids = analysis_results.get("posts_with_real_ids", 0)
            fallback_ids = analysis_results.get("posts_with_fallback_ids", 0)
            total_posts = analysis_results.get("total_posts", 0)
            
            print(f"🔗 LIAISON PHOTOS:")
            print(f"   ✅ Posts avec vrais IDs: {real_ids}/{total_posts}")
            print(f"   ❌ Posts avec IDs fallback: {fallback_ids}/{total_posts}")
            
            if fallback_ids == 0 and real_ids > 0:
                print(f"   🎉 SUCCÈS: Aucun ID fallback détecté!")
            elif fallback_ids > 0:
                print(f"   ⚠️ PROBLÈME: IDs fallback encore présents")
        
        if display_test_results:
            successful_displays = display_test_results.get("successful_responses", 0)
            total_tested = display_test_results.get("urls_tested", 0)
            print(f"🖼️ AFFICHAGE IMAGES: {successful_displays}/{total_tested} URLs fonctionnelles")
        
        # Critical success criteria for photo-post linking
        print(f"\n🎯 CRITÈRES DE SUCCÈS CRITIQUES:")
        
        success_criteria = {
            "Authentification réussie": any(r["step"] == 1 and r["status"] == "PASS" for r in self.test_results),
            "Contenu uploadé trouvé": len(self.uploaded_content_ids) > 0,
            "Posts générés": generation_result and generation_result.get("posts_count", 0) > 0,
            "Vrais IDs utilisés": analysis_results and analysis_results.get("posts_with_real_ids", 0) > 0,
            "Aucun ID fallback": analysis_results and analysis_results.get("posts_with_fallback_ids", 0) == 0,
            "URLs images fonctionnelles": display_test_results and display_test_results.get("successful_responses", 0) > 0
        }
        
        for criterion, met in success_criteria.items():
            status_icon = "✅" if met else "❌"
            print(f"   {status_icon} {criterion}")
        
        # Overall assessment
        met_criteria = sum(success_criteria.values())
        total_criteria = len(success_criteria)
        
        print(f"\n🏆 ÉVALUATION GLOBALE:")
        if met_criteria == total_criteria:
            print(f"✅ SUCCÈS COMPLET: {met_criteria}/{total_criteria} critères remplis")
            print("🎉 Le système de liaison photos-posts fonctionne parfaitement!")
            print("📸 Les posts utilisent maintenant de VRAIS IDs de photos")
            print("🚫 Aucun 'global_fallback_X' détecté")
        elif met_criteria >= total_criteria * 0.8:
            print(f"✅ SUCCÈS PARTIEL: {met_criteria}/{total_criteria} critères remplis")
            print("⚠️ Le système fonctionne mais nécessite des ajustements mineurs")
        else:
            print(f"❌ ÉCHEC: {met_criteria}/{total_criteria} critères remplis")
            print("🔧 Le système de liaison photos-posts nécessite des corrections")
            
            if analysis_results and analysis_results.get("posts_with_fallback_ids", 0) > 0:
                print("❌ PROBLÈME CRITIQUE: Des IDs 'global_fallback_X' sont encore utilisés")
                print("🔧 Le parsing des IDs de photos doit être corrigé")
        
        print("=" * 70)

def main():
    """Main test execution"""
    tester = PhotoPostLinkingTester()
    
    try:
        success = tester.run_comprehensive_test()
        
        if success:
            print(f"\n✅ Test critique terminé avec succès")
            return 0
        else:
            print(f"\n❌ Test critique échoué")
            return 1
            
    except KeyboardInterrupt:
        print(f"\n⚠️ Test interrompu par l'utilisateur")
        return 1
    except Exception as e:
        print(f"\n❌ Erreur critique du test: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())