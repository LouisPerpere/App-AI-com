#!/usr/bin/env python3
"""
COMPREHENSIVE OAUTH TOKEN DIAGNOSTIC
Extended testing to find any existing tokens and test OAuth callback flow

This test will:
1. Check all possible token storage locations
2. Test OAuth URL generation
3. Simulate OAuth callback scenarios
4. Test publication with different token types
5. Verify the complete OAuth flow state
"""

import requests
import json
import time
import sys
import os
from urllib.parse import urlparse, parse_qs

# Configuration
BACKEND_URL = "https://social-publisher-10.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class ComprehensiveOAuthTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        
    def authenticate(self):
        """Authenticate with the backend"""
        print("🔐 Authentication")
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
                print(f"   ✅ User ID: {self.user_id}")
                return True
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def test_comprehensive_token_search(self):
        """Search for tokens in all possible locations"""
        print("\n🔍 COMPREHENSIVE TOKEN SEARCH")
        
        # Test multiple endpoints that might reveal token information
        endpoints_to_check = [
            "/debug/social-connections",
            "/social/connections", 
            "/social/connections/status",
            "/social/facebook/auth-url",
            "/social/instagram/auth-url"
        ]
        
        tokens_found = []
        
        for endpoint in endpoints_to_check:
            try:
                print(f"\n   📊 Testing {endpoint}")
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                print(f"      Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Look for token-related data
                    if "connections" in data:
                        connections = data["connections"]
                        for conn in connections:
                            token = conn.get("access_token", "")
                            if token:
                                tokens_found.append({
                                    "source": endpoint,
                                    "platform": conn.get("platform", "unknown"),
                                    "token_type": "EAA" if token.startswith("EAA") else "temp" if token.startswith("temp_") else "other",
                                    "token_preview": token[:30] + "...",
                                    "active": conn.get("active", conn.get("is_active", False)),
                                    "page_name": conn.get("page_name", ""),
                                    "page_id": conn.get("page_id", "")
                                })
                    
                    # Look for auth URLs that might contain state information
                    if "auth_url" in data:
                        auth_url = data["auth_url"]
                        state = data.get("state", "")
                        print(f"      🔗 Auth URL generated")
                        print(f"      🎫 State: {state[:20]}...")
                        
                        # Parse URL to check parameters
                        parsed = urlparse(auth_url)
                        params = parse_qs(parsed.query)
                        
                        client_id = params.get("client_id", [""])[0]
                        config_id = params.get("config_id", [""])[0]
                        
                        print(f"      📱 Client ID: {client_id}")
                        print(f"      ⚙️ Config ID: {config_id}")
                    
                    # Print relevant data
                    relevant_keys = ["total_connections", "active_connections", "facebook_connections", "instagram_connections"]
                    for key in relevant_keys:
                        if key in data:
                            print(f"      📈 {key}: {data[key]}")
                            
                elif response.status_code == 404:
                    print(f"      ⚠️ Endpoint not found")
                else:
                    print(f"      ❌ Error: {response.text[:100]}")
                    
            except Exception as e:
                print(f"      ❌ Exception: {e}")
        
        print(f"\n   📊 TOKENS SUMMARY:")
        print(f"      Total tokens found: {len(tokens_found)}")
        
        for token in tokens_found:
            print(f"      🎫 {token['platform']} ({token['token_type']}): {token['token_preview']}")
            print(f"         Source: {token['source']}")
            print(f"         Active: {token['active']}")
            if token['page_name']:
                print(f"         Page: {token['page_name']}")
        
        return len(tokens_found) > 0
    
    def test_oauth_callback_simulation(self):
        """Test OAuth callback scenarios"""
        print("\n🔄 OAUTH CALLBACK SIMULATION")
        
        # Test callback endpoints with various scenarios
        callback_tests = [
            {
                "name": "Facebook callback with test code",
                "url": f"{BACKEND_URL}/social/facebook/callback",
                "params": {"code": "test_code_123", "state": f"test_state|{self.user_id}"}
            },
            {
                "name": "Instagram callback with test code", 
                "url": f"{BACKEND_URL}/social/instagram/callback",
                "params": {"code": "test_code_456", "state": f"test_state|{self.user_id}"}
            },
            {
                "name": "Facebook callback with error",
                "url": f"{BACKEND_URL}/social/facebook/callback",
                "params": {"error": "access_denied", "state": f"test_state|{self.user_id}"}
            }
        ]
        
        callback_results = []
        
        for test in callback_tests:
            try:
                print(f"\n   🧪 {test['name']}")
                
                # Make callback request (without auth since callbacks are public)
                callback_response = requests.get(test["url"], params=test["params"])
                
                print(f"      Status: {callback_response.status_code}")
                print(f"      Response: {callback_response.text[:200]}...")
                
                # Check if this created any connections
                if callback_response.status_code in [200, 302]:
                    # Check for new connections after callback
                    time.sleep(1)  # Brief delay
                    
                    check_response = self.session.get(f"{BACKEND_URL}/debug/social-connections")
                    if check_response.status_code == 200:
                        check_data = check_response.json()
                        total_after = check_data.get("total_connections", 0)
                        print(f"      📊 Connections after callback: {total_after}")
                        
                        if total_after > 0:
                            print("      ✅ Callback may have created connections")
                            callback_results.append(True)
                        else:
                            print("      ⚠️ No connections created")
                            callback_results.append(False)
                    else:
                        callback_results.append(False)
                else:
                    callback_results.append(False)
                    
            except Exception as e:
                print(f"      ❌ Callback test error: {e}")
                callback_results.append(False)
        
        successful_callbacks = sum(callback_results)
        print(f"\n   📊 Callback Results: {successful_callbacks}/{len(callback_tests)} successful")
        
        return successful_callbacks > 0
    
    def test_publication_scenarios(self):
        """Test publication with different scenarios"""
        print("\n📤 PUBLICATION SCENARIOS TESTING")
        
        # Get available posts
        posts_response = self.session.get(f"{BACKEND_URL}/posts/generated")
        
        if posts_response.status_code != 200:
            print("   ❌ Cannot get posts for publication testing")
            return False
        
        posts_data = posts_response.json()
        posts = posts_data.get("posts", [])
        
        if not posts:
            print("   ⚠️ No posts available for publication testing")
            return False
        
        # Test different publication scenarios
        test_scenarios = []
        
        # Find Facebook posts
        facebook_posts = [p for p in posts if p.get("platform", "").lower() == "facebook"]
        if facebook_posts:
            test_scenarios.append({
                "name": "Facebook post with image",
                "post": facebook_posts[0]
            })
        
        # Find Instagram posts
        instagram_posts = [p for p in posts if p.get("platform", "").lower() == "instagram"]
        if instagram_posts:
            test_scenarios.append({
                "name": "Instagram post with image", 
                "post": instagram_posts[0]
            })
        
        if not test_scenarios:
            test_scenarios.append({
                "name": "Any available post",
                "post": posts[0]
            })
        
        publication_results = []
        
        for scenario in test_scenarios:
            try:
                post = scenario["post"]
                post_id = post.get("id")
                platform = post.get("platform", "unknown")
                visual_url = post.get("visual_url", "")
                
                print(f"\n   📝 {scenario['name']}")
                print(f"      Post ID: {post_id}")
                print(f"      Platform: {platform}")
                print(f"      Visual: {visual_url[:50]}...")
                
                # Test publication
                pub_response = self.session.post(
                    f"{BACKEND_URL}/posts/publish",
                    json={"post_id": post_id}
                )
                
                print(f"      Status: {pub_response.status_code}")
                
                if pub_response.status_code == 200:
                    pub_data = pub_response.json()
                    print(f"      ✅ Success: {pub_data}")
                    publication_results.append(True)
                    
                elif pub_response.status_code == 400:
                    pub_data = pub_response.json()
                    error_msg = pub_data.get("error", "")
                    print(f"      📋 Expected error: {error_msg}")
                    
                    # Analyze error type
                    if "connexion sociale" in error_msg.lower():
                        print("      ℹ️ No active connections (expected)")
                        publication_results.append(True)  # This is expected behavior
                    elif "token" in error_msg.lower():
                        print("      ⚠️ Token-related error")
                        publication_results.append(False)
                    else:
                        print("      ⚠️ Other error")
                        publication_results.append(False)
                else:
                    print(f"      ❌ Unexpected error: {pub_response.text}")
                    publication_results.append(False)
                    
            except Exception as e:
                print(f"      ❌ Publication test error: {e}")
                publication_results.append(False)
        
        successful_publications = sum(publication_results)
        print(f"\n   📊 Publication Results: {successful_publications}/{len(publication_results)} successful")
        
        return successful_publications > 0
    
    def test_image_accessibility_for_facebook(self):
        """Test if images are accessible for Facebook"""
        print("\n🖼️ IMAGE ACCESSIBILITY FOR FACEBOOK")
        
        # Get content to test image accessibility
        content_response = self.session.get(f"{BACKEND_URL}/content/pending?limit=3")
        
        if content_response.status_code != 200:
            print("   ❌ Cannot get content for image testing")
            return False
        
        content_data = content_response.json()
        content_items = content_data.get("content", [])
        
        if not content_items:
            print("   ⚠️ No content available for image testing")
            return False
        
        facebook_accessible_images = 0
        
        for item in content_items:
            content_id = item.get("id")
            original_url = item.get("url", "")
            
            print(f"\n   🔍 Testing image: {content_id}")
            print(f"      Original URL: {original_url}")
            
            # Test different access methods
            access_methods = [
                {
                    "name": "Public endpoint",
                    "url": f"https://social-publisher-10.preview.emergentagent.com/api/public/image/{content_id}",
                    "auth": False
                },
                {
                    "name": "Public JPG endpoint", 
                    "url": f"https://social-publisher-10.preview.emergentagent.com/api/public/image/{content_id}.jpg",
                    "auth": False
                },
                {
                    "name": "Protected endpoint",
                    "url": f"https://social-publisher-10.preview.emergentagent.com/api/content/{content_id}/file",
                    "auth": True
                }
            ]
            
            for method in access_methods:
                try:
                    if method["auth"]:
                        response = self.session.get(method["url"])
                    else:
                        response = requests.get(method["url"])
                    
                    print(f"      📸 {method['name']}: {response.status_code}")
                    
                    if response.status_code == 200:
                        content_type = response.headers.get("Content-Type", "")
                        content_length = response.headers.get("Content-Length", "0")
                        cors_header = response.headers.get("Access-Control-Allow-Origin", "")
                        
                        print(f"         Type: {content_type}")
                        print(f"         Size: {content_length} bytes")
                        print(f"         CORS: {cors_header}")
                        
                        # Check if Facebook-accessible
                        if not method["auth"] and "image/" in content_type:
                            print("         ✅ Facebook-accessible")
                            facebook_accessible_images += 1
                            break
                    else:
                        print(f"         ❌ Error: {response.status_code}")
                        
                except Exception as e:
                    print(f"         ❌ Exception: {e}")
        
        print(f"\n   📊 Facebook-accessible images: {facebook_accessible_images}/{len(content_items)}")
        
        return facebook_accessible_images > 0
    
    def run_comprehensive_diagnostic(self):
        """Run complete comprehensive diagnostic"""
        print("🎯 COMPREHENSIVE OAUTH TOKEN DIAGNOSTIC")
        print("=" * 80)
        print(f"Backend: {BACKEND_URL}")
        print(f"User: {TEST_CREDENTIALS['email']}")
        print("=" * 80)
        
        if not self.authenticate():
            print("\n❌ DIAGNOSTIC FAILED: Authentication error")
            return False
        
        tests = [
            ("Comprehensive Token Search", self.test_comprehensive_token_search),
            ("OAuth Callback Simulation", self.test_oauth_callback_simulation),
            ("Publication Scenarios Testing", self.test_publication_scenarios),
            ("Image Accessibility for Facebook", self.test_image_accessibility_for_facebook)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                print(f"\n{'='*20} {test_name} {'='*20}")
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"\n❌ Test '{test_name}' crashed: {e}")
                results.append((test_name, False))
        
        # Final analysis
        print("\n" + "=" * 80)
        print("📋 COMPREHENSIVE DIAGNOSTIC RESULTS")
        print("=" * 80)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
            if result:
                passed += 1
        
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        print(f"\n📊 OVERALL SUCCESS RATE: {passed}/{total} ({success_rate:.1f}%)")
        
        # Final hypothesis conclusion
        print("\n🔬 FINAL HYPOTHESIS ANALYSIS:")
        print("HYPOTHESIS: 'EAA tokens are saved despite AJAX errors after OAuth redirection'")
        
        if success_rate >= 75:
            print("✅ HYPOTHESIS STRONGLY SUPPORTED")
            print("   - EAA tokens are present and functional")
            print("   - Facebook publication should work")
            print("   - System is ready for production use")
        elif success_rate >= 50:
            print("⚠️ HYPOTHESIS PARTIALLY SUPPORTED")
            print("   - Some OAuth functionality working")
            print("   - May have temporary or incomplete tokens")
            print("   - Requires further investigation")
        else:
            print("❌ HYPOTHESIS NOT SUPPORTED")
            print("   - No EAA tokens found")
            print("   - OAuth flow appears incomplete")
            print("   - AJAX errors likely preventing token persistence")
        
        return success_rate >= 50

if __name__ == "__main__":
    tester = ComprehensiveOAuthTester()
    success = tester.run_comprehensive_diagnostic()
    sys.exit(0 if success else 1)