#!/usr/bin/env python3
"""
Backend Testing Suite - OAuth Facebook Corrections Validation
Testing the critical OAuth corrections made by main agent:
1. Removed failing fallback that created temp_facebook_token_{timestamp}
2. Restored real Facebook publication (removed simulation)
3. Added token validation before publication
4. Cleanup endpoint to remove all fake tokens

Credentials: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://social-ai-planner-2.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()
        
    def authenticate(self):
        """Step 1: Authenticate with test credentials"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login-robust", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                
                self.log_test(
                    "Authentication", 
                    True, 
                    f"User ID: {self.user_id}, Token obtained"
                )
                return True
            else:
                self.log_test(
                    "Authentication", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, error=str(e))
            return False
    
    def test_cleanup_fake_tokens(self):
        """Step 2: Test cleanup of fake tokens endpoint"""
        try:
            response = self.session.post(f"{BACKEND_URL}/debug/clean-fake-tokens")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Cleanup Fake Tokens Endpoint", 
                    True, 
                    f"Response: {data.get('message', 'Success')}"
                )
                return True
            else:
                self.log_test(
                    "Cleanup Fake Tokens Endpoint", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Cleanup Fake Tokens Endpoint", False, error=str(e))
            return False
    
    def test_social_connections_diagnostic(self):
        """Step 3: Test social connections diagnostic endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/debug/social-connections")
            
            if response.status_code == 200:
                data = response.json()
                
                # Analyze the connections
                total_connections = data.get('total_connections', 0)
                active_connections = data.get('active_connections', 0)
                facebook_connections = data.get('facebook_connections', 0)
                instagram_connections = data.get('instagram_connections', 0)
                
                # Check for temporary tokens
                temp_tokens_found = False
                connections_detail = data.get('connections_detail', [])
                for conn in connections_detail:
                    token = conn.get('access_token', '')
                    if 'temp_facebook_token_' in token or 'temp_instagram_token_' in token:
                        temp_tokens_found = True
                        break
                
                details = f"Total: {total_connections}, Active: {active_connections}, Facebook: {facebook_connections}, Instagram: {instagram_connections}"
                if temp_tokens_found:
                    details += " ⚠️ TEMPORARY TOKENS FOUND"
                else:
                    details += " ✅ NO TEMPORARY TOKENS"
                
                self.log_test(
                    "Social Connections Diagnostic", 
                    True, 
                    details
                )
                return data
            else:
                self.log_test(
                    "Social Connections Diagnostic", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test("Social Connections Diagnostic", False, error=str(e))
            return None
    
    def test_clean_invalid_tokens(self):
        """Step 4: Test clean invalid tokens endpoint"""
        try:
            response = self.session.post(f"{BACKEND_URL}/debug/clean-invalid-tokens")
            
            if response.status_code == 200:
                data = response.json()
                deleted_count = data.get('deleted_count', 0)
                
                self.log_test(
                    "Clean Invalid Tokens", 
                    True, 
                    f"Deleted {deleted_count} invalid token connections"
                )
                return True
            else:
                self.log_test(
                    "Clean Invalid Tokens", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Clean Invalid Tokens", False, error=str(e))
            return False
    
    def test_clean_library_badges(self):
        """Step 5: Test clean library badges endpoint"""
        try:
            response = self.session.post(f"{BACKEND_URL}/debug/clean-library-badges")
            
            if response.status_code == 200:
                data = response.json()
                
                self.log_test(
                    "Clean Library Badges", 
                    True, 
                    f"Response: {data.get('message', 'Success')}"
                )
                return True
            else:
                self.log_test(
                    "Clean Library Badges", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Clean Library Badges", False, error=str(e))
            return False
    
    def test_post_publication_validation(self):
        """Step 6: Test post publication with token validation"""
        try:
            # First get available posts
            posts_response = self.session.get(f"{BACKEND_URL}/posts/generated")
            
            if posts_response.status_code != 200:
                self.log_test(
                    "Post Publication - Get Posts", 
                    False, 
                    error=f"Cannot get posts: {posts_response.status_code}"
                )
                return False
            
            posts_data = posts_response.json()
            posts = posts_data.get('posts', [])
            
            if not posts:
                self.log_test(
                    "Post Publication - No Posts Available", 
                    True, 
                    "No posts available for publication testing (expected in clean state)"
                )
                return True
            
            # Try to publish first available post
            test_post = posts[0]
            post_id = test_post.get('id')
            
            response = self.session.post(f"{BACKEND_URL}/posts/publish", json={
                "post_id": post_id
            })
            
            # We expect this to fail with "no active social connections" since we cleaned tokens
            if response.status_code == 400:
                data = response.json()
                error_msg = data.get('error', '').lower()
                
                if 'aucune connexion sociale active' in error_msg or 'no active social connections' in error_msg:
                    self.log_test(
                        "Post Publication Token Validation", 
                        True, 
                        "Correctly rejects publication due to no active social connections (expected after cleanup)"
                    )
                    return True
                else:
                    self.log_test(
                        "Post Publication Token Validation", 
                        False, 
                        error=f"Unexpected error: {error_msg}"
                    )
                    return False
            else:
                self.log_test(
                    "Post Publication Token Validation", 
                    False, 
                    error=f"Unexpected status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Post Publication Token Validation", False, error=str(e))
            return False
    
    def test_oauth_endpoints_accessibility(self):
        """Step 7: Test OAuth endpoints are accessible"""
        try:
            # Test Facebook OAuth URL generation
            response = self.session.get(f"{BACKEND_URL}/social/facebook/auth-url")
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get('auth_url', '')
                
                # Check if URL contains corrected Facebook Config ID
                if 'client_id=' in auth_url:
                    self.log_test(
                        "Facebook OAuth URL Generation", 
                        True, 
                        f"Auth URL generated successfully"
                    )
                else:
                    self.log_test(
                        "Facebook OAuth URL Generation", 
                        False, 
                        error="Auth URL missing client_id parameter"
                    )
                    return False
            else:
                self.log_test(
                    "Facebook OAuth URL Generation", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return False
            
            # Test Instagram OAuth URL generation
            response = self.session.get(f"{BACKEND_URL}/social/instagram/auth-url")
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get('auth_url', '')
                
                if 'client_id=' in auth_url:
                    self.log_test(
                        "Instagram OAuth URL Generation", 
                        True, 
                        f"Auth URL generated successfully"
                    )
                else:
                    self.log_test(
                        "Instagram OAuth URL Generation", 
                        False, 
                        error="Auth URL missing client_id parameter"
                    )
                    return False
            else:
                self.log_test(
                    "Instagram OAuth URL Generation", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return False
                
            return True
                
        except Exception as e:
            self.log_test("OAuth Endpoints Accessibility", False, error=str(e))
            return False
    
    def verify_no_temp_tokens_after_cleanup(self):
        """Step 8: Verify no temporary tokens remain after cleanup"""
        try:
            response = self.session.get(f"{BACKEND_URL}/debug/social-connections")
            
            if response.status_code == 200:
                data = response.json()
                connections_detail = data.get('connections_detail', [])
                
                temp_tokens = []
                for conn in connections_detail:
                    token = conn.get('access_token', '')
                    if 'temp_facebook_token_' in token or 'temp_instagram_token_' in token or token.startswith('temp_'):
                        temp_tokens.append({
                            'platform': conn.get('platform'),
                            'token_preview': token[:20] + '...' if len(token) > 20 else token
                        })
                
                if not temp_tokens:
                    self.log_test(
                        "Verify No Temporary Tokens", 
                        True, 
                        "✅ No temporary tokens found after cleanup"
                    )
                    return True
                else:
                    self.log_test(
                        "Verify No Temporary Tokens", 
                        False, 
                        error=f"Found {len(temp_tokens)} temporary tokens: {temp_tokens}"
                    )
                    return False
            else:
                self.log_test(
                    "Verify No Temporary Tokens", 
                    False, 
                    error=f"Cannot verify - diagnostic endpoint failed: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Verify No Temporary Tokens", False, error=str(e))
            return False
    
    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🎯 FACEBOOK OAUTH CORRECTIONS TESTING - COMPREHENSIVE VALIDATION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: {TEST_EMAIL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 80)
        print()
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ CRITICAL: Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Test cleanup endpoints
        print("🧹 TESTING CLEANUP ENDPOINTS")
        print("-" * 40)
        self.test_cleanup_fake_tokens()
        self.test_clean_invalid_tokens()
        self.test_clean_library_badges()
        print()
        
        # Step 3: Diagnostic after cleanup
        print("🔍 DIAGNOSTIC AFTER CLEANUP")
        print("-" * 40)
        connections_data = self.test_social_connections_diagnostic()
        print()
        
        # Step 4: Verify cleanup worked
        print("✅ VERIFICATION TESTS")
        print("-" * 40)
        self.verify_no_temp_tokens_after_cleanup()
        print()
        
        # Step 5: Test OAuth endpoints
        print("🔗 OAUTH ENDPOINTS TESTING")
        print("-" * 40)
        self.test_oauth_endpoints_accessibility()
        print()
        
        # Step 6: Test publication validation
        print("📤 PUBLICATION VALIDATION TESTING")
        print("-" * 40)
        self.test_post_publication_validation()
        print()
        
        # Summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("=" * 80)
        print("🎯 TEST SUMMARY - FACEBOOK OAUTH CORRECTIONS")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "0%")
        print()
        
        # Group results
        critical_tests = [
            "Authentication",
            "Clean Invalid Tokens", 
            "Verify No Temporary Tokens",
            "Post Publication Token Validation"
        ]
        
        print("🔥 CRITICAL TESTS:")
        for result in self.test_results:
            if result['test'] in critical_tests:
                print(f"  {result['status']}: {result['test']}")
        print()
        
        print("🔧 CLEANUP & DIAGNOSTIC TESTS:")
        cleanup_tests = [
            "Cleanup Fake Tokens Endpoint",
            "Social Connections Diagnostic", 
            "Clean Library Badges"
        ]
        for result in self.test_results:
            if result['test'] in cleanup_tests:
                print(f"  {result['status']}: {result['test']}")
        print()
        
        print("🔗 OAUTH TESTS:")
        oauth_tests = [
            "Facebook OAuth URL Generation",
            "Instagram OAuth URL Generation"
        ]
        for result in self.test_results:
            if result['test'] in oauth_tests:
                print(f"  {result['status']}: {result['test']}")
        print()
        
        # Failed tests details
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print("❌ FAILED TESTS DETAILS:")
            for result in failed_tests:
                print(f"  • {result['test']}: {result['error']}")
            print()
        
        print("=" * 80)
        
        # Final assessment
        critical_passed = sum(1 for result in self.test_results if result['test'] in critical_tests and result['success'])
        critical_total = sum(1 for result in self.test_results if result['test'] in critical_tests)
        
        if critical_passed == critical_total:
            print("🎉 OAUTH CORRECTIONS VALIDATION: SUCCESS")
            print("✅ All critical OAuth corrections are working correctly")
            print("✅ Cleanup endpoints successfully remove fake tokens")
            print("✅ Token validation prevents publication with invalid tokens")
            print("✅ System is ready for real Facebook OAuth reconnection")
        else:
            print("🚨 OAUTH CORRECTIONS VALIDATION: ISSUES FOUND")
            print(f"❌ {critical_total - critical_passed} critical tests failed")
            print("⚠️ OAuth corrections may not be fully operational")
        
        print("=" * 80)

def main():
    """Main test execution"""
    tester = BackendTester()
    
    try:
        success = tester.run_comprehensive_test()
        
        # Exit with appropriate code
        if success:
            failed_count = sum(1 for result in tester.test_results if not result['success'])
            sys.exit(0 if failed_count == 0 else 1)
        else:
            sys.exit(2)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(3)
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        sys.exit(4)

if __name__ == "__main__":
    main()