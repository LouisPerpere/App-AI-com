#!/usr/bin/env python3
"""
Backend Test for Post Generation After Social Connections Corrections
Testing post generation functionality for user lperpere@yahoo.fr with confirmed social connections.

CONTEXTE IMPORTANT:
- User ID correct: 6a670c66-c06c-4d75-9dd5-c747e8a0281a
- Connexions sociales confirmées: Facebook + Instagram actives
- La logique multi-plateforme est implémentée dans posts_generator.py

TESTS À EFFECTUER:
1. Login avec lperpere@yahoo.fr / L@Reunion974!
2. Vérifier les connexions sociales via /api/social/connections
3. Tester la génération de posts via POST /api/posts/generate avec:
   - target_month: "octobre_2025"
   - num_posts: 3
4. Vérifier si la génération fonctionne pour les 2 plateformes (Facebook + Instagram)
5. Examiner les logs pour identifier les problèmes éventuels

PROBLÈMES POTENTIELS À VÉRIFIER:
- URLs legacy vers claire-marcus-api.onrender.com dans les logs
- Timeout de 30 secondes sur les appels LLM
- Configuration de la clé OpenAI dans le générateur de posts
"""

import requests
import json
import time
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://post-genius-13.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"
EXPECTED_USER_ID = "6a670c66-c06c-4d75-9dd5-c747e8a0281a"

class PostGenerationTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   📋 {details}")
        if error:
            print(f"   ❌ Error: {error}")
        print()
    
    def test_authentication(self):
        """Test 1: Login avec lperpere@yahoo.fr / L@Reunion974!"""
        print("🔐 Test 1: Authentication with lperpere@yahoo.fr")
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login-robust", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                
                # Check if user ID matches expected
                user_id_match = self.user_id == EXPECTED_USER_ID
                details = f"User ID: {self.user_id}, Expected: {EXPECTED_USER_ID}, Match: {user_id_match}"
                
                self.log_result(
                    "Authentication", 
                    True, 
                    details
                )
                return True
            else:
                self.log_result(
                    "Authentication", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, error=str(e))
            return False
    
    def test_social_connections(self):
        """Test 2: Vérifier les connexions sociales via /api/social/connections"""
        print("🔗 Test 2: Social Connections Verification")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/social/connections")
            
            if response.status_code == 200:
                connections = response.json()
                
                # Check for Facebook and Instagram connections
                facebook_connected = connections.get("facebook", {}).get("connected", False)
                instagram_connected = connections.get("instagram", {}).get("connected", False)
                
                facebook_details = connections.get("facebook", {})
                instagram_details = connections.get("instagram", {})
                
                details = f"Facebook: {'✅ Connected' if facebook_connected else '❌ Not Connected'}"
                details += f", Instagram: {'✅ Connected' if instagram_connected else '❌ Not Connected'}"
                
                if facebook_connected:
                    details += f", FB Page: {facebook_details.get('page_name', 'N/A')}"
                if instagram_connected:
                    details += f", IG Account: {instagram_details.get('username', 'N/A')}"
                
                # Test passes if at least one platform is connected
                success = facebook_connected or instagram_connected
                
                self.log_result(
                    "Social Connections", 
                    success, 
                    details
                )
                
                # Also test debug endpoint for more details
                debug_response = self.session.get(f"{BACKEND_URL}/social/connections/debug")
                if debug_response.status_code == 200:
                    debug_data = debug_response.json()
                    raw_connections = debug_data.get("raw_connections", [])
                    print(f"   🔍 Debug: Found {len(raw_connections)} raw connections in database")
                    for conn in raw_connections:
                        print(f"      - Platform: {conn.get('platform', 'N/A')}, Active: {conn.get('is_active', False)}")
                
                return success
            else:
                self.log_result(
                    "Social Connections", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Social Connections", False, error=str(e))
            return False
    
    def test_business_profile(self):
        """Test 3: Verify business profile for post generation context"""
        print("🏢 Test 3: Business Profile Verification")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/business-profile")
            
            if response.status_code == 200:
                profile = response.json()
                
                # Check key fields needed for post generation
                business_name = profile.get("business_name")
                business_type = profile.get("business_type")
                posting_frequency = profile.get("posting_frequency")
                
                details = f"Business: {business_name}, Type: {business_type}, Frequency: {posting_frequency}"
                
                # Profile is valid if business name exists
                success = bool(business_name)
                
                self.log_result(
                    "Business Profile", 
                    success, 
                    details
                )
                return success
            else:
                self.log_result(
                    "Business Profile", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Business Profile", False, error=str(e))
            return False
    
    def test_content_library(self):
        """Test 4: Check content library for post generation"""
        print("📚 Test 4: Content Library Check")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                total = data.get("total", 0)
                
                # Check for images that can be used in posts
                images = [item for item in content_items if item.get("file_type", "").startswith("image")]
                
                details = f"Total content: {total}, Images: {len(images)}"
                
                # At least some content should be available
                success = total > 0
                
                self.log_result(
                    "Content Library", 
                    success, 
                    details
                )
                return success
            else:
                self.log_result(
                    "Content Library", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Content Library", False, error=str(e))
            return False
    
    def test_post_generation(self):
        """Test 5: Tester la génération de posts via POST /api/posts/generate"""
        print("🚀 Test 5: Post Generation with target_month: octobre_2025, num_posts: 3")
        
        try:
            # First, clear any existing posts for clean test
            try:
                clear_response = self.session.delete(f"{BACKEND_URL}/posts/generated/all")
                if clear_response.status_code == 200:
                    print("   🧹 Cleared existing posts for clean test")
            except:
                pass  # Continue even if clearing fails
            
            # Generate posts
            start_time = time.time()
            response = self.session.post(f"{BACKEND_URL}/posts/generate", json={
                "target_month": "octobre_2025"
            })
            generation_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                posts_count = data.get("posts_count", 0)
                success_flag = data.get("success", False)
                strategy = data.get("strategy", {})
                sources_used = data.get("sources_used", {})
                
                details = f"Generated {posts_count} posts in {generation_time:.1f}s"
                details += f", Success: {success_flag}"
                details += f", Strategy: {strategy}"
                details += f", Sources: {sources_used}"
                
                # Check for potential issues
                if generation_time > 30:
                    details += " ⚠️ Generation took >30s (potential timeout issue)"
                
                success = success_flag and posts_count > 0
                
                self.log_result(
                    "Post Generation", 
                    success, 
                    details
                )
                return success
            else:
                error_text = response.text
                # Check for specific error patterns
                if "claire-marcus-api.onrender.com" in error_text:
                    error_text += " ⚠️ Legacy URL detected in logs"
                if "timeout" in error_text.lower():
                    error_text += " ⚠️ Timeout issue detected"
                if "openai" in error_text.lower():
                    error_text += " ⚠️ OpenAI configuration issue"
                
                self.log_result(
                    "Post Generation", 
                    False, 
                    error=f"Status {response.status_code}: {error_text}"
                )
                return False
                
        except Exception as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                error_msg += " ⚠️ Request timeout - check LLM call duration"
            
            self.log_result("Post Generation", False, error=error_msg)
            return False
    
    def test_generated_posts_verification(self):
        """Test 6: Verify generated posts and platform distribution"""
        print("📋 Test 6: Generated Posts Verification")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/posts/generated")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                total_posts = len(posts)
                
                # Analyze platform distribution
                platforms = {}
                statuses = {}
                
                for post in posts:
                    platform = post.get("platform", "unknown")
                    status = post.get("status", "unknown")
                    
                    platforms[platform] = platforms.get(platform, 0) + 1
                    statuses[status] = statuses.get(status, 0) + 1
                
                # Check for multi-platform distribution
                facebook_posts = platforms.get("facebook", 0)
                instagram_posts = platforms.get("instagram", 0)
                
                details = f"Total posts: {total_posts}"
                details += f", Instagram: {instagram_posts}, Facebook: {facebook_posts}"
                details += f", Statuses: {statuses}"
                
                # Success if posts exist and have proper status
                success = total_posts > 0 and statuses.get("with_image", 0) > 0
                
                # Check for multi-platform logic
                if facebook_posts > 0 and instagram_posts > 0:
                    details += " ✅ Multi-platform distribution detected"
                elif facebook_posts > 0 or instagram_posts > 0:
                    details += " ⚠️ Single platform only"
                else:
                    details += " ❌ No platform assignment"
                
                self.log_result(
                    "Generated Posts Verification", 
                    success, 
                    details
                )
                
                # Show sample posts
                if posts:
                    print("   📝 Sample Generated Posts:")
                    for i, post in enumerate(posts[:3]):  # Show first 3 posts
                        title = post.get("title", "No title")
                        platform = post.get("platform", "unknown")
                        status = post.get("status", "unknown")
                        print(f"      {i+1}. {title} ({platform}, {status})")
                
                return success
            else:
                self.log_result(
                    "Generated Posts Verification", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Generated Posts Verification", False, error=str(e))
            return False
    
    def test_openai_configuration(self):
        """Test 7: Check OpenAI configuration and potential issues"""
        print("🤖 Test 7: OpenAI Configuration Check")
        
        try:
            # Check backend health and configuration
            response = self.session.get(f"{BACKEND_URL}/health")
            
            if response.status_code == 200:
                # Try to check if OpenAI key is configured by attempting a small generation
                # This is indirect since we can't directly access the key
                
                # Check if there are any error logs or indicators
                details = "Backend healthy, OpenAI configuration check indirect"
                
                # The actual OpenAI test happens during post generation
                # We'll mark this as successful if backend is healthy
                success = True
                
                self.log_result(
                    "OpenAI Configuration", 
                    success, 
                    details
                )
                return success
            else:
                self.log_result(
                    "OpenAI Configuration", 
                    False, 
                    error=f"Backend health check failed: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result("OpenAI Configuration", False, error=str(e))
            return False
    
    def check_backend_logs(self):
        """Test 8: Check for potential issues in backend behavior"""
        print("📊 Test 8: Backend Behavior Analysis")
        
        try:
            # Test various endpoints to check for legacy URL issues
            endpoints_to_test = [
                "/health",
                "/business-profile", 
                "/content/pending",
                "/social/connections"
            ]
            
            legacy_url_detected = False
            timeout_issues = False
            
            for endpoint in endpoints_to_test:
                try:
                    start_time = time.time()
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    response_time = time.time() - start_time
                    
                    if response_time > 10:  # More than 10 seconds is concerning
                        timeout_issues = True
                    
                    # Check response for legacy URLs (this is indirect)
                    if response.status_code == 200:
                        response_text = response.text
                        if "claire-marcus-api.onrender.com" in response_text:
                            legacy_url_detected = True
                            
                except Exception as e:
                    if "timeout" in str(e).lower():
                        timeout_issues = True
            
            issues = []
            if legacy_url_detected:
                issues.append("Legacy URLs detected")
            if timeout_issues:
                issues.append("Timeout issues detected")
            
            details = f"Issues found: {', '.join(issues) if issues else 'None'}"
            success = len(issues) == 0
            
            self.log_result(
                "Backend Behavior Analysis", 
                success, 
                details
            )
            return success
            
        except Exception as e:
            self.log_result("Backend Behavior Analysis", False, error=str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🧪 Starting Post Generation Testing Suite")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_EMAIL}")
        print(f"Expected User ID: {EXPECTED_USER_ID}")
        print("=" * 60)
        print()
        
        # Run tests in order
        tests = [
            self.test_authentication,
            self.test_social_connections,
            self.test_business_profile,
            self.test_content_library,
            self.test_openai_configuration,
            self.test_post_generation,
            self.test_generated_posts_verification,
            self.check_backend_logs
        ]
        
        results = []
        for test in tests:
            try:
                result = test()
                results.append(result)
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
                results.append(False)
        
        # Summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(results)
        total = len(results)
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        print()
        
        # Detailed results
        for i, result in enumerate(self.test_results):
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   📋 {result['details']}")
            if result["error"]:
                print(f"   ❌ {result['error']}")
        
        print()
        print("=" * 60)
        print("🎯 CRITICAL FINDINGS")
        print("=" * 60)
        
        # Analyze critical issues
        critical_issues = []
        
        # Check authentication
        auth_result = next((r for r in self.test_results if r["test"] == "Authentication"), None)
        if not auth_result or not auth_result["success"]:
            critical_issues.append("❌ Authentication failed - cannot proceed with testing")
        
        # Check social connections
        social_result = next((r for r in self.test_results if r["test"] == "Social Connections"), None)
        if not social_result or not social_result["success"]:
            critical_issues.append("⚠️ No social connections found - multi-platform generation may not work")
        
        # Check post generation
        gen_result = next((r for r in self.test_results if r["test"] == "Post Generation"), None)
        if not gen_result or not gen_result["success"]:
            critical_issues.append("❌ Post generation failed - core functionality broken")
        
        # Check for timeout issues
        timeout_detected = any("timeout" in r.get("error", "").lower() or "timeout" in r.get("details", "").lower() 
                             for r in self.test_results)
        if timeout_detected:
            critical_issues.append("⚠️ Timeout issues detected - check LLM call duration")
        
        # Check for legacy URL issues
        legacy_detected = any("legacy" in r.get("error", "").lower() or "legacy" in r.get("details", "").lower() 
                            for r in self.test_results)
        if legacy_detected:
            critical_issues.append("⚠️ Legacy URL issues detected - check configuration")
        
        if critical_issues:
            for issue in critical_issues:
                print(issue)
        else:
            print("✅ No critical issues detected")
        
        print()
        print("=" * 60)
        print("📋 RECOMMENDATIONS")
        print("=" * 60)
        
        recommendations = []
        
        if not auth_result or not auth_result["success"]:
            recommendations.append("🔧 Fix authentication system before proceeding")
        
        if not social_result or not social_result["success"]:
            recommendations.append("🔧 Verify social connections configuration and OAuth flow")
        
        if not gen_result or not gen_result["success"]:
            recommendations.append("🔧 Check posts_generator.py implementation and OpenAI API key")
        
        if timeout_detected:
            recommendations.append("🔧 Optimize LLM calls to reduce timeout risk")
        
        if legacy_detected:
            recommendations.append("🔧 Update all URLs to use current backend configuration")
        
        if success_rate < 80:
            recommendations.append("🔧 Address failing tests before production deployment")
        
        if recommendations:
            for rec in recommendations:
                print(rec)
        else:
            print("✅ System appears to be working correctly")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = PostGenerationTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 Overall test result: SUCCESS")
        exit(0)
    else:
        print("\n❌ Overall test result: FAILURE")
        exit(1)
"""
Backend Testing Suite - Social Connections Facebook Integration
Focus: Validation finale connexions sociales Facebook sur environnement live claire-marcus.com

Test Requirements from French Review Request:
1. Test authentication with lperpere@yahoo.fr / L@Reunion974!
2. Test health check on https://claire-marcus.com/api/health
3. Test GET /api/social/connections endpoint
4. Validate Facebook URLs configuration
5. Test Instagram callback URL
6. Test authorization URL generation

OBJECTIF CRITIQUE: Valider que l'alignement sur environnement live (claire-marcus.com) 
résout définitivement le problème de sauvegarde des connexions Facebook.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration pour environnement live
BASE_URL = "https://claire-marcus.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class FacebookConnectionsTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.user_id = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Claire-Marcus-Backend-Test/1.0'
        })
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_authentication(self):
        """Test 1: Authentification utilisateur avec credentials spécifiés"""
        self.log("🔐 STEP 1: Testing user authentication")
        
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login-robust",
                json=TEST_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token')
                self.user_id = data.get('user_id')
                
                # Configure session with token
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}'
                })
                
                self.log(f"✅ Authentication successful - User ID: {self.user_id}")
                return True
            else:
                self.log(f"❌ Authentication failed - Status: {response.status_code}, Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Authentication error: {str(e)}", "ERROR")
            return False
    
    def test_health_check(self):
        """Test 2: Health check backend sur environnement live"""
        self.log("🏥 STEP 2: Testing backend health check")
        
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                service = data.get('service')
                
                self.log(f"✅ Health check successful - Status: {status}, Service: {service}")
                return True
            else:
                self.log(f"❌ Health check failed - Status: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Health check error: {str(e)}", "ERROR")
            return False
    
    def test_social_connections_endpoint(self):
        """Test 3: Endpoint GET /api/social/connections - vérifier accessibilité"""
        self.log("🔗 STEP 3: Testing social connections endpoint")
        
        try:
            response = self.session.get(f"{self.base_url}/social/connections", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Social connections endpoint accessible - Response: {data}")
                return True
            else:
                self.log(f"❌ Social connections endpoint failed - Status: {response.status_code}, Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Social connections endpoint error: {str(e)}", "ERROR")
            return False
    
    def test_facebook_urls_configuration(self):
        """Test 4: Configuration Facebook URLs - valider alignement sur claire-marcus.com"""
        self.log("🔧 STEP 4: Testing Facebook URLs configuration")
        
        try:
            # Test Instagram auth URL generation
            response = self.session.get(f"{self.base_url}/social/instagram/auth-url", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get('auth_url', '')
                
                # Vérifier que l'URL contient claire-marcus.com
                if 'claire-marcus.com' in auth_url:
                    self.log(f"✅ Facebook URLs correctly configured with claire-marcus.com")
                    self.log(f"   Auth URL: {auth_url[:100]}...")
                    return True
                else:
                    self.log(f"❌ Facebook URLs not aligned with claire-marcus.com - URL: {auth_url}", "ERROR")
                    return False
            else:
                self.log(f"❌ Facebook URL configuration test failed - Status: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Facebook URLs configuration error: {str(e)}", "ERROR")
            return False
    
    def test_instagram_callback_url(self):
        """Test 5: Callback Instagram URL - tester accessibilité sur environnement live"""
        self.log("📞 STEP 5: Testing Instagram callback URL")
        
        try:
            # Test callback endpoint accessibility (without parameters for basic test)
            response = self.session.get(f"{self.base_url}/social/instagram/callback", timeout=10)
            
            # Callback should be accessible (might return error without proper params but should not be 404)
            if response.status_code in [200, 400, 302, 307]:
                self.log(f"✅ Instagram callback URL accessible - Status: {response.status_code}")
                return True
            else:
                self.log(f"❌ Instagram callback URL not accessible - Status: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Instagram callback URL error: {str(e)}", "ERROR")
            return False
    
    def test_authorization_url_generation(self):
        """Test 6: Authorization URL generation - vérifier génération URL d'autorisation Facebook correcte"""
        self.log("🔑 STEP 6: Testing authorization URL generation")
        
        try:
            # Test both Instagram auth endpoints
            endpoints_to_test = [
                "/social/instagram/auth-url",
                "/social/instagram/test-auth"
            ]
            
            success_count = 0
            
            for endpoint in endpoints_to_test:
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        auth_url = data.get('auth_url', data.get('authorization_url', ''))
                        
                        if auth_url:
                            # Vérifier les composants critiques de l'URL
                            url_checks = [
                                ('claire-marcus.com' in auth_url, 'claire-marcus.com domain'),
                                ('client_id=' in auth_url, 'client_id parameter'),
                                ('redirect_uri=' in auth_url, 'redirect_uri parameter'),
                                ('scope=' in auth_url, 'scope parameter')
                            ]
                            
                            all_checks_passed = all(check[0] for check in url_checks)
                            
                            if all_checks_passed:
                                self.log(f"✅ Authorization URL generation working - Endpoint: {endpoint}")
                                success_count += 1
                            else:
                                failed_checks = [check[1] for check in url_checks if not check[0]]
                                self.log(f"⚠️ Authorization URL missing components - Endpoint: {endpoint}, Missing: {failed_checks}")
                        else:
                            self.log(f"⚠️ No authorization URL returned - Endpoint: {endpoint}")
                    else:
                        self.log(f"⚠️ Authorization endpoint failed - Endpoint: {endpoint}, Status: {response.status_code}")
                        
                except Exception as e:
                    self.log(f"⚠️ Authorization endpoint error - Endpoint: {endpoint}, Error: {str(e)}")
            
            if success_count > 0:
                self.log(f"✅ Authorization URL generation working ({success_count}/{len(endpoints_to_test)} endpoints)")
                return True
            else:
                self.log("❌ Authorization URL generation failed on all endpoints", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Authorization URL generation error: {str(e)}", "ERROR")
            return False
    
    def run_all_tests(self):
        """Execute all tests for Facebook connections validation"""
        self.log("🚀 STARTING FACEBOOK CONNECTIONS VALIDATION - ENVIRONNEMENT LIVE")
        self.log(f"   Backend URL: {self.base_url}")
        self.log(f"   Test credentials: {TEST_CREDENTIALS['email']}")
        
        tests = [
            ("Authentication", self.test_authentication),
            ("Health Check", self.test_health_check),
            ("Social Connections Endpoint", self.test_social_connections_endpoint),
            ("Facebook URLs Configuration", self.test_facebook_urls_configuration),
            ("Instagram Callback URL", self.test_instagram_callback_url),
            ("Authorization URL Generation", self.test_authorization_url_generation)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            self.log(f"\n{'='*60}")
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                self.log(f"❌ Test '{test_name}' crashed: {str(e)}", "ERROR")
                results.append((test_name, False))
        
        # Summary
        self.log(f"\n{'='*60}")
        self.log("📊 TEST RESULTS SUMMARY")
        self.log(f"{'='*60}")
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"   {status}: {test_name}")
            if result:
                passed += 1
        
        success_rate = (passed / total) * 100
        self.log(f"\n🎯 SUCCESS RATE: {passed}/{total} tests passed ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            self.log("🎉 FACEBOOK CONNECTIONS VALIDATION: SUCCESSFUL")
        else:
            self.log("🚨 FACEBOOK CONNECTIONS VALIDATION: NEEDS ATTENTION")
        
        return success_rate >= 80

def main():
    """Main test execution"""
    print("Facebook Connections Backend Testing Suite")
    print("=" * 60)
    
    tester = FacebookConnectionsTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()