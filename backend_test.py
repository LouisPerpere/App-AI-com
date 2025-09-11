#!/usr/bin/env python3
"""
POST MODIFICATION ENDPOINT TEST - SUCCESS FIELD VERIFICATION
Test spécifique pour vérifier que l'endpoint /api/posts/{post_id}/modify retourne le bon format de réponse avec success: true.

OBJECTIF:
Tester l'endpoint PUT /api/posts/{post_id}/modify pour vérifier qu'il retourne maintenant le format correct avec "success": true.

TESTS À EFFECTUER:
1. Créer un utilisateur de test si nécessaire
2. Générer quelques posts de test
3. Tester l'endpoint PUT /api/posts/{post_id}/modify avec une demande de modification valide
4. Vérifier que la réponse contient "success": true et les autres champs attendus
5. Vérifier que le post est effectivement modifié dans la base de données

Credentials: lperpere@yahoo.fr / L@Reunion974!
Backend URL: https://claire-marcus-pwa-1.preview.emergentagent.com/api
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://claire-marcus-pwa-1.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class PostModificationTest:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        
    def authenticate(self):
        """Step 1: Authenticate with test credentials"""
        print("🔐 STEP 1: Authentication...")
        
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
                
                print(f"✅ Authentication successful")
                print(f"   User ID: {self.user_id}")
                print(f"   Token: {self.token[:20]}..." if self.token else "No token")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def get_existing_posts(self):
        """Step 2: Get existing posts to test modification"""
        print("\n📋 STEP 2: Getting existing posts...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/posts/generated", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                
                print(f"✅ Retrieved {len(posts)} existing posts")
                
                if posts:
                    # Show first few posts for testing
                    for i, post in enumerate(posts[:3]):
                        print(f"   Post {i+1}: ID={post.get('id')}, Title='{post.get('title', '')[:50]}...'")
                    
                    return posts
                else:
                    print("⚠️ No existing posts found - will need to generate some")
                    return []
            else:
                print(f"❌ Failed to get posts: {response.status_code}")
                print(f"   Response: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting posts: {str(e)}")
            return []
    
    def generate_test_posts(self):
        """Step 3: Generate some test posts if none exist"""
        print("\n🚀 STEP 3: Generating test posts...")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/posts/generate",
                params={"target_month": "septembre_2025"},
                timeout=120  # Extended timeout for AI generation
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Post generation successful")
                print(f"   Posts generated: {data.get('posts_count', 0)}")
                return True
            else:
                print(f"❌ Post generation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error generating posts: {str(e)}")
            return False
    
    def test_post_modification(self, post_id, original_post):
        """Step 4: Test the POST modification endpoint"""
        print(f"\n🔧 STEP 4: Testing post modification for post ID: {post_id}")
        
        # Show original post details
        print(f"   Original title: '{original_post.get('title', '')}'")
        print(f"   Original text: '{original_post.get('text', '')[:100]}...'")
        print(f"   Original hashtags: {original_post.get('hashtags', [])[:5]}")
        
        # Test modification request
        modification_request = {
            "modification_request": "Rendre ce post plus engageant et ajouter un appel à l'action pour visiter notre boutique"
        }
        
        try:
            print(f"   Sending modification request...")
            response = self.session.put(
                f"{BACKEND_URL}/posts/{post_id}/modify",
                json=modification_request,
                timeout=60  # Extended timeout for AI processing
            )
            
            print(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Post modification successful")
                
                # CRITICAL: Check for success field
                success_field = data.get("success")
                print(f"   'success' field: {success_field} (type: {type(success_field)})")
                
                if success_field is True:
                    print("✅ SUCCESS FIELD VERIFICATION PASSED - 'success': true found in response")
                else:
                    print(f"❌ SUCCESS FIELD VERIFICATION FAILED - Expected 'success': true, got: {success_field}")
                
                # Check other expected fields
                expected_fields = ["message", "new_title", "new_text", "new_hashtags", "modified_at"]
                missing_fields = []
                
                for field in expected_fields:
                    if field in data:
                        print(f"✅ Field '{field}' present: {str(data[field])[:50]}...")
                    else:
                        missing_fields.append(field)
                        print(f"❌ Field '{field}' missing from response")
                
                # Show modified content
                if "new_title" in data:
                    print(f"   Modified title: '{data['new_title']}'")
                if "new_text" in data:
                    print(f"   Modified text: '{data['new_text'][:100]}...'")
                if "new_hashtags" in data:
                    print(f"   Modified hashtags: {data['new_hashtags'][:5]}")
                
                return {
                    "success": success_field is True,
                    "response_data": data,
                    "missing_fields": missing_fields
                }
            else:
                print(f"❌ Post modification failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Error modifying post: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def verify_post_persistence(self, post_id, modification_result):
        """Step 5: Verify the post was actually modified in the database"""
        print(f"\n🔍 STEP 5: Verifying post persistence for post ID: {post_id}")
        
        try:
            # Get updated posts
            response = self.session.get(f"{BACKEND_URL}/posts/generated", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                
                # Find the modified post
                modified_post = None
                for post in posts:
                    if post.get("id") == post_id:
                        modified_post = post
                        break
                
                if modified_post:
                    print(f"✅ Modified post found in database")
                    
                    # Check if modifications were persisted
                    if modification_result.get("success") and "response_data" in modification_result:
                        expected_title = modification_result["response_data"].get("new_title")
                        expected_text = modification_result["response_data"].get("new_text")
                        expected_hashtags = modification_result["response_data"].get("new_hashtags")
                        
                        actual_title = modified_post.get("title")
                        actual_text = modified_post.get("text")
                        actual_hashtags = modified_post.get("hashtags")
                        
                        persistence_checks = []
                        
                        # Check title persistence
                        if expected_title and actual_title == expected_title:
                            print(f"✅ Title persistence verified")
                            persistence_checks.append(True)
                        elif expected_title:
                            print(f"❌ Title persistence failed")
                            print(f"   Expected: '{expected_title}'")
                            print(f"   Actual: '{actual_title}'")
                            persistence_checks.append(False)
                        
                        # Check text persistence
                        if expected_text and actual_text == expected_text:
                            print(f"✅ Text persistence verified")
                            persistence_checks.append(True)
                        elif expected_text:
                            print(f"❌ Text persistence failed")
                            print(f"   Expected: '{expected_text[:50]}...'")
                            print(f"   Actual: '{actual_text[:50]}...'")
                            persistence_checks.append(False)
                        
                        # Check hashtags persistence
                        if expected_hashtags and actual_hashtags == expected_hashtags:
                            print(f"✅ Hashtags persistence verified")
                            persistence_checks.append(True)
                        elif expected_hashtags:
                            print(f"❌ Hashtags persistence failed")
                            print(f"   Expected: {expected_hashtags[:5]}")
                            print(f"   Actual: {actual_hashtags[:5]}")
                            persistence_checks.append(False)
                        
                        # Check modified_at field
                        modified_at = modified_post.get("modified_at")
                        if modified_at:
                            print(f"✅ modified_at field present: {modified_at}")
                            persistence_checks.append(True)
                        else:
                            print(f"❌ modified_at field missing")
                            persistence_checks.append(False)
                        
                        return all(persistence_checks)
                    else:
                        print("⚠️ Cannot verify persistence - modification failed")
                        return False
                else:
                    print(f"❌ Modified post not found in database")
                    return False
            else:
                print(f"❌ Failed to get posts for verification: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying persistence: {str(e)}")
            return False
    
    def run_test(self):
        """Execute the complete test"""
        print("=" * 80)
        print("🧪 POST MODIFICATION ENDPOINT TEST - SUCCESS FIELD VERIFICATION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test credentials: {TEST_EMAIL}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ TEST FAILED: Authentication failed")
            return False
        
        # Step 2: Get existing posts
        posts = self.get_existing_posts()
        
        # Step 3: Generate posts if none exist
        if not posts:
            if not self.generate_test_posts():
                print("\n❌ TEST FAILED: Could not generate test posts")
                return False
            
            # Get posts again after generation
            posts = self.get_existing_posts()
            if not posts:
                print("\n❌ TEST FAILED: No posts available after generation")
                return False
        
        # Step 4: Test modification on first available post
        test_post = posts[0]
        post_id = test_post.get("id")
        
        if not post_id:
            print("\n❌ TEST FAILED: No valid post ID found")
            return False
        
        modification_result = self.test_post_modification(post_id, test_post)
        
        # Step 5: Verify persistence
        persistence_ok = self.verify_post_persistence(post_id, modification_result)
        
        # Final results
        print("\n" + "=" * 80)
        print("📋 TEST RESULTS SUMMARY")
        print("=" * 80)
        
        success_field_ok = modification_result.get("success", False)
        missing_fields = modification_result.get("missing_fields", [])
        
        print(f"✅ Authentication: PASSED")
        print(f"✅ Post retrieval: PASSED")
        print(f"{'✅' if success_field_ok else '❌'} Success field verification: {'PASSED' if success_field_ok else 'FAILED'}")
        print(f"{'✅' if not missing_fields else '❌'} Response format: {'PASSED' if not missing_fields else 'FAILED'}")
        print(f"{'✅' if persistence_ok else '❌'} Database persistence: {'PASSED' if persistence_ok else 'FAILED'}")
        
        if missing_fields:
            print(f"   Missing fields: {missing_fields}")
        
        overall_success = success_field_ok and not missing_fields and persistence_ok
        
        print("\n" + "=" * 80)
        if overall_success:
            print("🎉 TEST PASSED - Post modification endpoint working correctly!")
            print("✅ Response contains 'success': true")
            print("✅ All expected fields present")
            print("✅ Database persistence verified")
        else:
            print("❌ TEST FAILED - Issues detected:")
            if not success_field_ok:
                print("   - 'success': true field missing or incorrect")
            if missing_fields:
                print(f"   - Missing response fields: {missing_fields}")
            if not persistence_ok:
                print("   - Database persistence issues")
        
        return overall_success

def main():
    """Main test execution"""
    test = PostModificationTest()
    success = test.run_test()
    
    if success:
        print("\n🎉 POST MODIFICATION TEST COMPLETED SUCCESSFULLY")
        sys.exit(0)
    else:
        print("\n💥 POST MODIFICATION TEST FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()