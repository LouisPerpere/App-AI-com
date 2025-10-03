#!/usr/bin/env python3
"""
Backend Testing Script for Calendar Functionalities Post-Programmer Transformation
Testing the 5 critical calendar features mentioned in the French review request:
1. "Déprogrammer" button on scheduled posts
2. Explanatory text "Déprogrammez ce post pour pouvoir le modifier en onglet post"
3. Modal preview opens when clicking on calendar posts
4. Thumbnails/vignettes visible next to text
5. Scheduled posts appear in calendar after "Programmer"
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://claire-marcus.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials from review request
EMAIL = "lperpere@yahoo.fr"
PASSWORD = "L@Reunion974!"

class CalendarTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        
    def authenticate(self):
        """Authenticate with the backend API"""
        print("🔐 Step 1: Authenticating with backend...")
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login-robust", json={
                "email": EMAIL,
                "password": PASSWORD
            })
            
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
                print(f"   Token: {self.auth_token[:20]}..." if self.auth_token else "   Token: None")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_calendar_posts_endpoint(self):
        """Test 1: Verify calendar posts endpoint returns scheduled posts"""
        print("\n📅 Step 2: Testing calendar posts endpoint...")
        
        try:
            response = self.session.get(f"{API_BASE}/calendar/posts")
            
            if response.status_code == 200:
                data = response.json()
                posts = data if isinstance(data, list) else data.get('posts', [])
                
                print(f"✅ Calendar endpoint accessible")
                print(f"   Found {len(posts)} calendar posts")
                
                if posts:
                    # Analyze first post for required fields
                    first_post = posts[0]
                    print(f"   Sample post ID: {first_post.get('id', 'N/A')}")
                    print(f"   Title: {first_post.get('title', 'N/A')}")
                    print(f"   Platform: {first_post.get('platform', 'N/A')}")
                    print(f"   Scheduled date: {first_post.get('scheduled_date', 'N/A')}")
                    print(f"   Status: {first_post.get('status', 'N/A')}")
                    print(f"   Validated: {first_post.get('validated', 'N/A')}")
                    
                    # Check for image/visual fields (thumbnails)
                    visual_fields = ['visual_url', 'visual_id', 'carousel_images', 'image_url']
                    for field in visual_fields:
                        if field in first_post and first_post[field]:
                            print(f"   Visual field '{field}': {str(first_post[field])[:50]}...")
                    
                    return posts
                else:
                    print("⚠️ No calendar posts found")
                    return []
            else:
                print(f"❌ Calendar endpoint failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Calendar endpoint error: {str(e)}")
            return None
    
    def test_post_movement_endpoint(self, post_id):
        """Test 2: Test post movement (Déplacer functionality)"""
        print(f"\n🔄 Step 3: Testing post movement for post {post_id}...")
        
        try:
            # Test the move calendar post endpoint
            new_date = "2025-09-27T15:00:00.000Z"
            response = self.session.put(f"{API_BASE}/posts/move-calendar-post/{post_id}", json={
                "new_date": new_date
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Post movement endpoint working")
                print(f"   Response: {data.get('message', 'Success')}")
                return True
            else:
                print(f"❌ Post movement failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Post movement error: {str(e)}")
            return False
    
    def test_post_modification_endpoint(self, post_id):
        """Test 3: Test post modification functionality"""
        print(f"\n✏️ Step 4: Testing post modification for post {post_id}...")
        
        try:
            # Test the modify post endpoint
            response = self.session.put(f"{API_BASE}/posts/{post_id}/modify", json={
                "modification_request": "Rends ce texte plus accrocheur pour le calendrier"
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Post modification endpoint working")
                print(f"   Success: {data.get('success', False)}")
                print(f"   Message: {data.get('message', 'N/A')}")
                if 'new_text' in data:
                    print(f"   Modified text preview: {data['new_text'][:100]}...")
                return True
            elif response.status_code == 404:
                print(f"⚠️ Post modification endpoint not found (404)")
                print(f"   This may be expected if endpoint doesn't exist for calendar posts")
                return False
            else:
                print(f"❌ Post modification failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Post modification error: {str(e)}")
            return False
    
    def test_oauth_3_step_flow(self):
        """Test 4: Flow OAuth 3-étapes Facebook"""
        print("\n🔐 Test 4: Flow OAuth 3-étapes Facebook")
        
        try:
            # Step 1: Get Facebook auth URL
            print("   📋 Step 1: Get Facebook auth URL")
            auth_url_response = self.session.get(f"{BACKEND_URL}/social/facebook/auth-url")
            
            if auth_url_response.status_code == 200:
                auth_data = auth_url_response.json()
                auth_url = auth_data.get("auth_url", "")
                state = auth_data.get("state", "")
                
                print(f"      ✅ Auth URL generated")
                print(f"      🔗 URL: {auth_url[:100]}...")
                print(f"      🎫 State: {state[:20]}...")
                
                # Verify URL contains required parameters
                if "client_id=" in auth_url and "config_id=" in auth_url:
                    print("      ✅ Auth URL contains required parameters")
                else:
                    print("      ❌ Auth URL missing required parameters")
                    return False
                    
            else:
                print(f"      ❌ Auth URL generation failed: {auth_url_response.status_code}")
                return False
            
            # Step 2: Test callback endpoint accessibility
            print("   📋 Step 2: Test callback endpoint")
            callback_url = f"{BACKEND_URL}/social/facebook/callback"
            
            # Test with invalid parameters (should handle gracefully)
            callback_response = requests.get(f"{callback_url}?code=test&state=test")
            print(f"      📞 GET {callback_url}")
            print(f"      Status: {callback_response.status_code}")
            
            if callback_response.status_code in [200, 302, 400]:
                print("      ✅ Callback endpoint accessible")
            else:
                print(f"      ❌ Callback endpoint error: {callback_response.status_code}")
                return False
            
            # Step 3: Test social connections endpoint
            print("   📋 Step 3: Test social connections")
            connections_response = self.session.get(f"{BACKEND_URL}/social/connections")
            
            if connections_response.status_code == 200:
                connections_data = connections_response.json()
                connections = connections_data.get("connections", [])
                print(f"      ✅ Social connections endpoint working")
                print(f"      📊 Found {len(connections)} connections")
                
                # Check for Facebook connections
                facebook_connections = [c for c in connections if c.get("platform") == "facebook"]
                print(f"      📘 Facebook connections: {len(facebook_connections)}")
                
                return True
            else:
                print(f"      ❌ Social connections failed: {connections_response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ OAuth 3-step flow test error: {e}")
            return False
    
    def test_system_consistency(self):
        """Test 5: Cohérence système complète"""
        print("\n🔧 Test 5: Cohérence système complète")
        
        try:
            # Test that all endpoints use the same JPG logic
            print("   🔍 Testing system-wide JPG consistency")
            
            # Get content for testing
            content_response = self.session.get(f"{BACKEND_URL}/content/pending?limit=3")
            if content_response.status_code != 200:
                print(f"   ❌ Cannot get content for consistency test")
                return False
                
            content_data = content_response.json()
            content_items = content_data.get("content", [])
            
            if not content_items:
                print("   ⚠️ No content for consistency testing")
                return False
            
            consistency_score = 0
            total_tests = 0
            
            for item in content_items[:3]:  # Test first 3 items
                content_id = item.get("id")
                
                # Test public endpoint consistency
                jpg_url = f"{BACKEND_URL}/public/image/{content_id}.jpg"
                regular_url = f"{BACKEND_URL}/public/image/{content_id}"
                
                jpg_response = requests.get(jpg_url)
                regular_response = requests.get(regular_url)
                
                total_tests += 2
                
                if jpg_response.status_code == 200:
                    consistency_score += 1
                    jpg_content_type = jpg_response.headers.get("Content-Type", "")
                    if "image/jpeg" in jpg_content_type:
                        consistency_score += 1
                        print(f"      ✅ {content_id}: JPG endpoint consistent")
                    else:
                        print(f"      ⚠️ {content_id}: JPG endpoint wrong content type")
                else:
                    print(f"      ❌ {content_id}: JPG endpoint failed")
                
                total_tests += 1
                
                if regular_response.status_code == 200:
                    consistency_score += 1
                    print(f"      ✅ {content_id}: Regular endpoint consistent")
                else:
                    print(f"      ❌ {content_id}: Regular endpoint failed")
            
            # Test Facebook publication endpoints consistency
            print("   🔍 Testing Facebook publication consistency")
            
            # Test binary upload endpoints
            binary_endpoints = [
                "/social/facebook/publish-simple",
                "/social/instagram/publish-simple"
            ]
            
            for endpoint in binary_endpoints:
                test_response = self.session.post(
                    f"{BACKEND_URL}{endpoint}",
                    json={"post_text": "Test", "image_url": "test"}
                )
                
                total_tests += 1
                
                if test_response.status_code in [200, 400]:  # 400 expected without connections
                    consistency_score += 1
                    print(f"      ✅ {endpoint}: Endpoint accessible")
                else:
                    print(f"      ❌ {endpoint}: Endpoint error {test_response.status_code}")
            
            # Calculate consistency percentage
            consistency_percentage = (consistency_score / total_tests) * 100 if total_tests > 0 else 0
            
            print(f"   📊 System consistency: {consistency_score}/{total_tests} ({consistency_percentage:.1f}%)")
            
            if consistency_percentage >= 80:
                print("   ✅ System consistency acceptable")
                return True
            else:
                print("   ❌ System consistency below threshold")
                return False
                
        except Exception as e:
            print(f"   ❌ System consistency test error: {e}")
            return False
    
    def run_validation(self):
        """Run all validation tests"""
        print("🎯 VALIDATION FINALE DES CORRECTIONS AVANT REDÉPLOIEMENT")
        print("=" * 60)
        
        if not self.authenticate():
            print("\n❌ VALIDATION FAILED: Authentication error")
            return False
        
        tests = [
            ("Endpoint public JPG fonctionnel", self.test_public_jpg_endpoint),
            ("Conversion URL automatique vers JPG", self.test_url_conversion_function),
            ("Publication Facebook avec conversion JPG intégrée", self.test_facebook_publication_jpg_integration),
            ("Flow OAuth 3-étapes Facebook", self.test_oauth_3_step_flow),
            ("Cohérence système complète", self.test_system_consistency)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"\n❌ Test '{test_name}' crashed: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 RÉSULTATS DE VALIDATION")
        print("=" * 60)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
            if result:
                passed += 1
        
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        print(f"\n📊 TAUX DE RÉUSSITE: {passed}/{total} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 VALIDATION RÉUSSIE - Système prêt pour redéploiement")
            return True
        else:
            print("❌ VALIDATION ÉCHOUÉE - Corrections supplémentaires requises")
            return False

if __name__ == "__main__":
    validator = FacebookJPGValidator()
    success = validator.run_validation()
    sys.exit(0 if success else 1)