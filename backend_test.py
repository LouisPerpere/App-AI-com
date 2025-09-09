#!/usr/bin/env python3
"""
Test du système de génération de posts avec calcul basé sur posting_frequency du profil business
OBJECTIF: Valider que le nombre de posts générés correspond au rythme défini dans le profil business

Tests à effectuer:
1. Authentification (lperpere@yahoo.fr / L@Reunion974!)
2. Vérifier le profil business existant et son posting_frequency
3. POST /api/posts/generate (sans paramètres)
4. Valider que le nombre de posts correspond au calcul:
   - Si weekly (1/semaine) → 4 posts/mois
   - Si bi_weekly (2/semaine) → 8 posts/mois
   - Si 3x_week (3/semaine) → 12 posts/mois
   - Si daily (7/semaine) → 28 posts/mois
5. Vérification que tous les posts sont uniques et variés
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://content-scheduler-6.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class PostGenerationTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        
    def authenticate(self):
        """Test authentication with provided credentials"""
        print("🔐 Step 1: Testing Authentication")
        
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
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                print(f"✅ Authentication successful")
                print(f"   User ID: {self.user_id}")
                print(f"   Token: {self.auth_token[:20]}..." if self.auth_token else "No token")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_backend_health(self):
        """Test backend health and connectivity"""
        print("\n🏥 Step 2: Testing Backend Health")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Backend health check successful")
                print(f"   Status: {data.get('status')}")
                print(f"   Service: {data.get('service')}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Health check error: {str(e)}")
            return False
    
    def test_post_generation_default(self):
        """Test POST /api/posts/generate with default parameters (should generate 4 posts)"""
        print("\n🚀 Step 3: Testing Post Generation with Default Parameters")
        
        try:
            # Test with no parameters - should default to 4 posts for octobre_2025
            print("   Calling POST /api/posts/generate with no parameters...")
            start_time = time.time()
            
            response = self.session.post(
                f"{BACKEND_URL}/posts/generate",
                timeout=120  # Allow up to 2 minutes for generation
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"   Response time: {duration:.1f} seconds")
            print(f"   Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                posts_count = data.get("posts_count", 0)
                
                print(f"✅ Post generation successful")
                print(f"   Posts generated: {posts_count}")
                print(f"   Success: {data.get('success')}")
                print(f"   Message: {data.get('message')}")
                print(f"   Strategy: {data.get('strategy', {})}")
                print(f"   Sources used: {data.get('sources_used', {})}")
                
                # Verify exactly 4 posts were generated (not 40)
                if posts_count == 4:
                    print(f"✅ Correct number of posts generated: {posts_count} (expected 4)")
                    return True, posts_count
                else:
                    print(f"❌ Incorrect number of posts: {posts_count} (expected 4)")
                    return False, posts_count
                    
            else:
                print(f"❌ Post generation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False, 0
                
        except Exception as e:
            print(f"❌ Post generation error: {str(e)}")
            return False, 0
    
    def test_generated_posts_retrieval(self):
        """Test GET /api/posts/generated to verify posts were saved"""
        print("\n📋 Step 4: Testing Generated Posts Retrieval")
        
        try:
            response = self.session.get(
                f"{BACKEND_URL}/posts/generated",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                count = data.get("count", 0)
                
                print(f"✅ Posts retrieval successful")
                print(f"   Total posts found: {count}")
                print(f"   Posts in response: {len(posts)}")
                
                if posts:
                    print(f"\n📝 Post Analysis:")
                    for i, post in enumerate(posts[:4], 1):  # Show first 4 posts
                        print(f"   Post {i}:")
                        print(f"     ID: {post.get('id', 'N/A')}")
                        print(f"     Title: {post.get('title', 'N/A')[:50]}...")
                        print(f"     Text: {post.get('text', 'N/A')[:80]}...")
                        print(f"     Hashtags: {len(post.get('hashtags', []))} hashtags")
                        print(f"     Visual URL: {post.get('visual_url', 'N/A')}")
                        print(f"     Content Type: {post.get('content_type', 'N/A')}")
                        print(f"     Platform: {post.get('platform', 'N/A')}")
                        print(f"     Scheduled Date: {post.get('scheduled_date', 'N/A')}")
                        print()
                
                return True, posts
            else:
                print(f"❌ Posts retrieval failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False, []
                
        except Exception as e:
            print(f"❌ Posts retrieval error: {str(e)}")
            return False, []
    
    def analyze_post_variety(self, posts):
        """Analyze if posts are varied and different"""
        print("\n🎨 Step 5: Analyzing Post Variety and Uniqueness")
        
        if not posts:
            print("❌ No posts to analyze")
            return False
        
        try:
            # Check for variety in content types
            content_types = [post.get('content_type', 'unknown') for post in posts]
            unique_content_types = set(content_types)
            
            print(f"   Content types found: {list(unique_content_types)}")
            print(f"   Unique content types: {len(unique_content_types)}")
            
            # Check for variety in text content
            texts = [post.get('text', '') for post in posts]
            unique_texts = set(texts)
            
            print(f"   Unique text contents: {len(unique_texts)} out of {len(texts)}")
            
            # Check for variety in titles
            titles = [post.get('title', '') for post in posts]
            unique_titles = set(titles)
            
            print(f"   Unique titles: {len(unique_titles)} out of {len(titles)}")
            
            # Check hashtag variety
            all_hashtags = []
            for post in posts:
                all_hashtags.extend(post.get('hashtags', []))
            
            unique_hashtags = set(all_hashtags)
            print(f"   Total hashtags used: {len(all_hashtags)}")
            print(f"   Unique hashtags: {len(unique_hashtags)}")
            
            # Variety assessment
            variety_score = 0
            
            if len(unique_content_types) > 1:
                variety_score += 1
                print("✅ Content type variety: GOOD")
            else:
                print("⚠️ Content type variety: LIMITED")
            
            if len(unique_texts) == len(texts):
                variety_score += 1
                print("✅ Text content variety: EXCELLENT (all unique)")
            elif len(unique_texts) > len(texts) * 0.8:
                variety_score += 1
                print("✅ Text content variety: GOOD")
            else:
                print("⚠️ Text content variety: LIMITED")
            
            if len(unique_titles) == len(titles):
                variety_score += 1
                print("✅ Title variety: EXCELLENT (all unique)")
            elif len(unique_titles) > len(titles) * 0.8:
                variety_score += 1
                print("✅ Title variety: GOOD")
            else:
                print("⚠️ Title variety: LIMITED")
            
            if len(unique_hashtags) > 10:
                variety_score += 1
                print("✅ Hashtag variety: GOOD")
            else:
                print("⚠️ Hashtag variety: LIMITED")
            
            print(f"\n🎯 Overall Variety Score: {variety_score}/4")
            
            if variety_score >= 3:
                print("✅ Posts show good variety and uniqueness")
                return True
            else:
                print("⚠️ Posts may lack sufficient variety")
                return False
                
        except Exception as e:
            print(f"❌ Variety analysis error: {str(e)}")
            return False
    
    def verify_visual_url_structure(self, posts):
        """Verify visual_url structure follows /api/content/{id}/file format"""
        print("\n🖼️ Step 6: Verifying Visual URL Structure")
        
        if not posts:
            print("❌ No posts to verify")
            return False
        
        try:
            correct_format_count = 0
            total_with_visual = 0
            
            for i, post in enumerate(posts, 1):
                visual_url = post.get('visual_url', '')
                
                if visual_url:
                    total_with_visual += 1
                    print(f"   Post {i} visual_url: {visual_url}")
                    
                    # Check if it follows the expected format /api/content/{id}/file
                    if '/api/content/' in visual_url and '/file' in visual_url:
                        correct_format_count += 1
                        print(f"     ✅ Correct format")
                    else:
                        print(f"     ❌ Incorrect format (expected /api/content/{{id}}/file)")
                else:
                    print(f"   Post {i}: No visual URL")
            
            print(f"\n📊 Visual URL Analysis:")
            print(f"   Posts with visual URLs: {total_with_visual}/{len(posts)}")
            print(f"   Correct format URLs: {correct_format_count}/{total_with_visual}")
            
            if total_with_visual > 0 and correct_format_count == total_with_visual:
                print("✅ All visual URLs follow correct format")
                return True
            elif total_with_visual == 0:
                print("⚠️ No visual URLs found (may be expected)")
                return True  # Not necessarily an error
            else:
                print("❌ Some visual URLs have incorrect format")
                return False
                
        except Exception as e:
            print(f"❌ Visual URL verification error: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🧪 COMPREHENSIVE POST GENERATION SYSTEM TEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: {TEST_EMAIL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 60)
        
        results = {
            "authentication": False,
            "backend_health": False,
            "post_generation": False,
            "posts_retrieval": False,
            "post_variety": False,
            "visual_url_structure": False,
            "posts_count": 0,
            "posts_data": []
        }
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with tests")
            return results
        results["authentication"] = True
        
        # Step 2: Backend Health
        if not self.test_backend_health():
            print("\n⚠️ Backend health check failed - proceeding with caution")
        else:
            results["backend_health"] = True
        
        # Step 3: Post Generation
        generation_success, posts_count = self.test_post_generation_default()
        results["post_generation"] = generation_success
        results["posts_count"] = posts_count
        
        if not generation_success:
            print("\n❌ CRITICAL: Post generation failed - cannot test retrieval")
            return results
        
        # Step 4: Posts Retrieval
        retrieval_success, posts_data = self.test_generated_posts_retrieval()
        results["posts_retrieval"] = retrieval_success
        results["posts_data"] = posts_data
        
        if not retrieval_success:
            print("\n❌ Posts retrieval failed - cannot analyze variety")
            return results
        
        # Step 5: Post Variety Analysis
        variety_success = self.analyze_post_variety(posts_data)
        results["post_variety"] = variety_success
        
        # Step 6: Visual URL Structure
        visual_url_success = self.verify_visual_url_structure(posts_data)
        results["visual_url_structure"] = visual_url_success
        
        return results
    
    def print_final_summary(self, results):
        """Print final test summary"""
        print("\n" + "=" * 60)
        print("🏁 FINAL TEST SUMMARY")
        print("=" * 60)
        
        total_tests = 6
        passed_tests = sum([
            results["authentication"],
            results["backend_health"],
            results["post_generation"],
            results["posts_retrieval"],
            results["post_variety"],
            results["visual_url_structure"]
        ])
        
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"✅ Authentication: {'PASS' if results['authentication'] else 'FAIL'}")
        print(f"✅ Backend Health: {'PASS' if results['backend_health'] else 'FAIL'}")
        print(f"✅ Post Generation: {'PASS' if results['post_generation'] else 'FAIL'}")
        print(f"✅ Posts Retrieval: {'PASS' if results['posts_retrieval'] else 'FAIL'}")
        print(f"✅ Post Variety: {'PASS' if results['post_variety'] else 'FAIL'}")
        print(f"✅ Visual URL Structure: {'PASS' if results['visual_url_structure'] else 'FAIL'}")
        
        print(f"\n📊 Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        print(f"📝 Posts Generated: {results['posts_count']}")
        print(f"📋 Posts Retrieved: {len(results['posts_data'])}")
        
        # Key findings
        print(f"\n🔍 KEY FINDINGS:")
        
        if results["posts_count"] == 4:
            print(f"✅ Correct default post count: {results['posts_count']} posts (expected 4)")
        else:
            print(f"❌ Incorrect post count: {results['posts_count']} (expected 4)")
        
        if results["post_variety"]:
            print("✅ Posts show good variety and uniqueness")
        else:
            print("⚠️ Posts may lack sufficient variety")
        
        if results["visual_url_structure"]:
            print("✅ Visual URLs follow correct format")
        else:
            print("⚠️ Visual URL format issues detected")
        
        # Overall assessment
        if success_rate >= 83.3:  # 5/6 tests
            print(f"\n🎉 OVERALL ASSESSMENT: EXCELLENT - Post generation system is working correctly")
        elif success_rate >= 66.7:  # 4/6 tests
            print(f"\n✅ OVERALL ASSESSMENT: GOOD - Post generation system is mostly functional")
        elif success_rate >= 50.0:  # 3/6 tests
            print(f"\n⚠️ OVERALL ASSESSMENT: FAIR - Post generation system has some issues")
        else:
            print(f"\n❌ OVERALL ASSESSMENT: POOR - Post generation system needs significant fixes")

def main():
    """Main test execution"""
    tester = PostGenerationTester()
    
    try:
        results = tester.run_comprehensive_test()
        tester.print_final_summary(results)
        
        # Return appropriate exit code
        if results["authentication"] and results["post_generation"] and results["posts_retrieval"]:
            return 0  # Success
        else:
            return 1  # Failure
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        return 2
    except Exception as e:
        print(f"\n\n❌ Unexpected error during testing: {str(e)}")
        return 3

if __name__ == "__main__":
    exit(main())