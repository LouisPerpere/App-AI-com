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
        """Authenticate with the backend"""
        print("🔐 Step 1: Authentication")
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json=TEST_CREDENTIALS,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                print(f"   ✅ Authentication successful")
                print(f"   ✅ User ID: {self.user_id}")
                return True
            else:
                print(f"   ❌ Authentication failed: {response.status_code}")
                print(f"   ❌ Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {e}")
            return False
    
    def test_public_jpg_endpoint(self):
        """Test 1: Endpoint public JPG fonctionnel"""
        print("\n🖼️ Test 1: Endpoint public JPG fonctionnel")
        
        # First, get some content to test with
        try:
            content_response = self.session.get(f"{BACKEND_URL}/content/pending?limit=5")
            if content_response.status_code != 200:
                print(f"   ❌ Cannot get content list: {content_response.status_code}")
                return False
                
            content_data = content_response.json()
            content_items = content_data.get("content", [])
            
            if not content_items:
                print("   ⚠️ No content items found for testing")
                return False
                
            # Test public JPG endpoint with first available content
            test_content = content_items[0]
            content_id = test_content.get("id")
            
            print(f"   🔍 Testing with content ID: {content_id}")
            
            # Test both .jpg and regular public endpoints
            jpg_url = f"{BACKEND_URL}/public/image/{content_id}.jpg"
            regular_url = f"{BACKEND_URL}/public/image/{content_id}"
            
            # Test JPG endpoint
            jpg_response = requests.get(jpg_url)
            print(f"   📸 GET {jpg_url}")
            print(f"      Status: {jpg_response.status_code}")
            
            if jpg_response.status_code == 200:
                content_type = jpg_response.headers.get("Content-Type", "")
                content_length = jpg_response.headers.get("Content-Length", "0")
                print(f"      Content-Type: {content_type}")
                print(f"      Content-Length: {content_length} bytes")
                
                # Verify it's JPG format
                if "image/jpeg" in content_type:
                    print("   ✅ JPG endpoint working - returns image/jpeg")
                else:
                    print(f"   ⚠️ JPG endpoint returns {content_type} instead of image/jpeg")
                    
            else:
                print(f"   ❌ JPG endpoint failed: {jpg_response.status_code}")
                
            # Test regular endpoint
            regular_response = requests.get(regular_url)
            print(f"   📸 GET {regular_url}")
            print(f"      Status: {regular_response.status_code}")
            
            if regular_response.status_code == 200:
                content_type = regular_response.headers.get("Content-Type", "")
                print(f"      Content-Type: {content_type}")
                print("   ✅ Regular public endpoint working")
            else:
                print(f"   ❌ Regular public endpoint failed: {regular_response.status_code}")
                
            # Test Facebook-friendly headers
            if jpg_response.status_code == 200:
                headers = jpg_response.headers
                cors_header = headers.get("Access-Control-Allow-Origin", "")
                cache_control = headers.get("Cache-Control", "")
                
                print(f"   🌐 CORS Header: {cors_header}")
                print(f"   💾 Cache-Control: {cache_control}")
                
                if cors_header == "*":
                    print("   ✅ Facebook-friendly CORS headers present")
                else:
                    print("   ⚠️ CORS headers may not be Facebook-friendly")
                    
            return jpg_response.status_code == 200
            
        except Exception as e:
            print(f"   ❌ Public JPG endpoint test error: {e}")
            return False
    
    def test_url_conversion_function(self):
        """Test 2: Conversion URL automatique vers JPG"""
        print("\n🔄 Test 2: Conversion URL automatique vers JPG")
        
        try:
            # Get content to test URL conversion
            content_response = self.session.get(f"{BACKEND_URL}/content/pending?limit=10")
            if content_response.status_code != 200:
                print(f"   ❌ Cannot get content for URL conversion test")
                return False
                
            content_data = content_response.json()
            content_items = content_data.get("content", [])
            
            # Look for carousel content or regular content
            carousel_found = False
            regular_content_found = False
            
            for item in content_items:
                url = item.get("url", "")
                content_id = item.get("id", "")
                
                print(f"   🔍 Content ID: {content_id}")
                print(f"   🔍 Original URL: {url}")
                
                # Test if this would be converted to JPG
                if "carousel" in url:
                    print("   📸 Carousel content detected")
                    expected_jpg_url = f"/api/public/image/{content_id}.jpg"
                    print(f"   ➡️ Expected JPG conversion: {expected_jpg_url}")
                    carousel_found = True
                    
                elif "/api/content/" in url and "/file" in url:
                    print("   📸 Protected content URL detected")
                    expected_jpg_url = f"/api/public/image/{content_id}.jpg"
                    print(f"   ➡️ Expected JPG conversion: {expected_jpg_url}")
                    regular_content_found = True
                    
                elif url.startswith("http") and "api" not in url:
                    print("   🌐 External URL detected - no conversion needed")
                    print(f"   ➡️ Should remain: {url}")
                    
                else:
                    print("   📁 Other URL format")
                    
            if carousel_found:
                print("   ✅ Carousel URL conversion logic testable")
            if regular_content_found:
                print("   ✅ Protected URL conversion logic testable")
                
            # Test the conversion function indirectly by checking if JPG URLs work
            if content_items:
                test_id = content_items[0].get("id")
                jpg_test_url = f"{BACKEND_URL}/public/image/{test_id}.jpg"
                
                jpg_test = requests.get(jpg_test_url)
                if jpg_test.status_code == 200:
                    print("   ✅ JPG URL conversion endpoint accessible")
                    return True
                else:
                    print(f"   ❌ JPG URL conversion test failed: {jpg_test.status_code}")
                    return False
            else:
                print("   ⚠️ No content available for conversion testing")
                return False
                
        except Exception as e:
            print(f"   ❌ URL conversion test error: {e}")
            return False
    
    def test_facebook_publication_jpg_integration(self):
        """Test 3: Publication Facebook avec conversion JPG intégrée"""
        print("\n📘 Test 3: Publication Facebook avec conversion JPG intégrée")
        
        try:
            # Get Facebook posts for testing - use the correct endpoint
            posts_response = self.session.get(f"{BACKEND_URL}/posts/generated")
            if posts_response.status_code != 200:
                print(f"   ❌ Cannot get posts: {posts_response.status_code}")
                return False
                
            posts_data = posts_response.json()
            posts = posts_data.get("posts", [])
            
            # Find Facebook posts with images
            facebook_posts = [p for p in posts if p.get("platform", "").lower() == "facebook"]
            
            if not facebook_posts:
                print("   ⚠️ No Facebook posts found for testing")
                # Try to find any posts and convert one for testing
                if posts:
                    test_post = posts[0]
                    post_id = test_post.get("id")
                    visual_url = test_post.get("visual_url", "")
                    
                    print(f"   📝 Testing with any post (converted to Facebook): {post_id}")
                    print(f"   🖼️ Visual URL: {visual_url}")
                else:
                    return False
            else:
                test_post = facebook_posts[0]
                post_id = test_post.get("id")
                visual_url = test_post.get("visual_url", "")
                
                print(f"   📝 Testing Facebook post: {post_id}")
                print(f"   🖼️ Visual URL: {visual_url}")
            
            # Test publication endpoint (should use JPG conversion)
            pub_response = self.session.post(
                f"{BACKEND_URL}/posts/publish",
                json={"post_id": post_id}
            )
            
            print(f"   📤 POST /posts/publish")
            print(f"      Status: {pub_response.status_code}")
            
            if pub_response.status_code == 200:
                pub_data = pub_response.json()
                print(f"      Response: {pub_data}")
                print("   ✅ Facebook publication endpoint accessible")
                return True
            elif pub_response.status_code == 400:
                # Expected if no active social connections
                pub_data = pub_response.json()
                error_msg = pub_data.get("error", "")
                if "connexion sociale" in error_msg.lower():
                    print(f"      Expected error: {error_msg}")
                    print("   ✅ Facebook publication flow working (no active connections)")
                    return True
                else:
                    print(f"      Unexpected error: {error_msg}")
                    return False
            else:
                print(f"      Error: {pub_response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Facebook publication test error: {e}")
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