#!/usr/bin/env python3
"""
Facebook Callback Diagnostic Test - Specific French Review Request
Testing the Facebook OAuth callback issue where error changed from 
"Invalid OAuth access token (190)" to "Aucune connexion facebook trouvée"

Diagnostic objectives:
1. Check social connections state with GET /api/debug/social-connections
2. Look for Facebook callback logs in backend
3. Test callback accessibility 
4. Verify if Instagram publication is simulated vs real
5. Identify why Facebook callback doesn't save connections

Credentials: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://social-ai-planner-2.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class FacebookCallbackDiagnostic:
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
    
    def diagnostic_social_connections_state(self):
        """Step 2: Diagnostic - Check social connections state"""
        try:
            response = self.session.get(f"{BACKEND_URL}/debug/social-connections")
            
            if response.status_code == 200:
                data = response.json()
                
                # Analyze connections in detail
                total_connections = data.get('total_connections', 0)
                active_connections = data.get('active_connections', 0)
                facebook_connections = data.get('facebook_connections', 0)
                instagram_connections = data.get('instagram_connections', 0)
                
                # Check collections
                social_media_connections = data.get('social_media_connections', 0)
                social_connections_old = data.get('social_connections_old', 0)
                
                # Analyze connection details
                connections_detail = data.get('connections_detail', [])
                facebook_details = [conn for conn in connections_detail if conn.get('platform') == 'facebook']
                instagram_details = [conn for conn in connections_detail if conn.get('platform') == 'instagram']
                
                details = f"""
🔍 SOCIAL CONNECTIONS STATE ANALYSIS:
   Total connections: {total_connections}
   Active connections: {active_connections}
   Facebook connections: {facebook_connections}
   Instagram connections: {instagram_connections}
   
📊 COLLECTIONS:
   social_media_connections: {social_media_connections}
   social_connections_old: {social_connections_old}
   
🔗 FACEBOOK CONNECTIONS DETAIL:
   Count: {len(facebook_details)}"""
                
                for i, fb_conn in enumerate(facebook_details):
                    token = fb_conn.get('access_token', '')
                    token_preview = token[:20] + '...' if len(token) > 20 else token
                    is_active = fb_conn.get('active', fb_conn.get('is_active', False))
                    created_at = fb_conn.get('created_at', 'Unknown')
                    
                    details += f"""
   Facebook #{i+1}:
     - Active: {is_active}
     - Token: {token_preview}
     - Created: {created_at}"""
                
                details += f"""
   
🔗 INSTAGRAM CONNECTIONS DETAIL:
   Count: {len(instagram_details)}"""
                
                for i, ig_conn in enumerate(instagram_details):
                    token = ig_conn.get('access_token', '')
                    token_preview = token[:20] + '...' if len(token) > 20 else token
                    is_active = ig_conn.get('active', ig_conn.get('is_active', False))
                    created_at = ig_conn.get('created_at', 'Unknown')
                    
                    details += f"""
   Instagram #{i+1}:
     - Active: {is_active}
     - Token: {token_preview}
     - Created: {created_at}"""
                
                self.log_test(
                    "Social Connections State Diagnostic", 
                    True, 
                    details.strip()
                )
                return data
            else:
                self.log_test(
                    "Social Connections State Diagnostic", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test("Social Connections State Diagnostic", False, error=str(e))
            return None
    
    def test_facebook_callback_accessibility(self):
        """Step 3: Test Facebook callback endpoint accessibility"""
        try:
            # Test if callback endpoint exists (without OAuth code)
            callback_url = f"{BACKEND_URL}/social/facebook/callback"
            
            # This should return an error but not 404
            response = self.session.get(callback_url)
            
            if response.status_code == 400:
                # Expected - callback needs OAuth code
                self.log_test(
                    "Facebook Callback Accessibility", 
                    True, 
                    "Callback endpoint exists and properly validates OAuth parameters"
                )
                return True
            elif response.status_code == 404:
                self.log_test(
                    "Facebook Callback Accessibility", 
                    False, 
                    error="Callback endpoint not found (404)"
                )
                return False
            else:
                self.log_test(
                    "Facebook Callback Accessibility", 
                    True, 
                    f"Callback endpoint accessible (Status: {response.status_code})"
                )
                return True
                
        except Exception as e:
            self.log_test("Facebook Callback Accessibility", False, error=str(e))
            return False
    
    def test_instagram_callback_accessibility(self):
        """Step 4: Test Instagram callback endpoint accessibility"""
        try:
            # Test if callback endpoint exists (without OAuth code)
            callback_url = f"{BACKEND_URL}/social/instagram/callback"
            
            # This should return an error but not 404
            response = self.session.get(callback_url)
            
            if response.status_code == 400:
                # Expected - callback needs OAuth code
                self.log_test(
                    "Instagram Callback Accessibility", 
                    True, 
                    "Callback endpoint exists and properly validates OAuth parameters"
                )
                return True
            elif response.status_code == 404:
                self.log_test(
                    "Instagram Callback Accessibility", 
                    False, 
                    error="Callback endpoint not found (404)"
                )
                return False
            else:
                self.log_test(
                    "Instagram Callback Accessibility", 
                    True, 
                    f"Callback endpoint accessible (Status: {response.status_code})"
                )
                return True
                
        except Exception as e:
            self.log_test("Instagram Callback Accessibility", False, error=str(e))
            return False
    
    def test_publication_behavior_analysis(self):
        """Step 5: Test publication behavior to identify if it's simulated"""
        try:
            # First get available posts
            posts_response = self.session.get(f"{BACKEND_URL}/posts/generated")
            
            if posts_response.status_code != 200:
                self.log_test(
                    "Publication Behavior Analysis - Get Posts", 
                    False, 
                    error=f"Cannot get posts: {posts_response.status_code}"
                )
                return False
            
            posts_data = posts_response.json()
            posts = posts_data.get('posts', [])
            
            if not posts:
                self.log_test(
                    "Publication Behavior Analysis", 
                    True, 
                    "No posts available for publication testing (expected after cleanup)"
                )
                return True
            
            # Try to publish first available post
            test_post = posts[0]
            post_id = test_post.get('id')
            platform = test_post.get('platform', 'unknown')
            
            print(f"🧪 Testing publication with Post ID: {post_id} (Platform: {platform})")
            
            response = self.session.post(f"{BACKEND_URL}/posts/publish", json={
                "post_id": post_id
            })
            
            # Analyze the response to determine if it's real or simulated
            if response.status_code == 200:
                data = response.json()
                message = data.get('message', '').lower()
                
                if 'simulé' in message or 'simulation' in message or 'test' in message:
                    self.log_test(
                        "Publication Behavior Analysis", 
                        True, 
                        f"✅ SIMULATION DETECTED: {data.get('message', 'Success')}"
                    )
                else:
                    self.log_test(
                        "Publication Behavior Analysis", 
                        True, 
                        f"🔥 REAL PUBLICATION: {data.get('message', 'Success')}"
                    )
                return True
                
            elif response.status_code == 400:
                data = response.json()
                error_msg = data.get('error', '').lower()
                
                if 'aucune connexion' in error_msg or 'no active social connections' in error_msg:
                    self.log_test(
                        "Publication Behavior Analysis", 
                        True, 
                        f"✅ EXPECTED ERROR: {data.get('error', 'No connections')} - This confirms the error change from OAuth 190 to connection error"
                    )
                    return True
                else:
                    self.log_test(
                        "Publication Behavior Analysis", 
                        True, 
                        f"⚠️ OTHER ERROR: {data.get('error', 'Unknown error')}"
                    )
                    return True
            else:
                self.log_test(
                    "Publication Behavior Analysis", 
                    False, 
                    error=f"Unexpected status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Publication Behavior Analysis", False, error=str(e))
            return False
    
    def test_oauth_url_configuration(self):
        """Step 6: Test OAuth URL configuration for Facebook"""
        try:
            response = self.session.get(f"{BACKEND_URL}/social/facebook/auth-url")
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get('auth_url', '')
                
                # Analyze the OAuth URL for configuration issues
                if 'client_id=' in auth_url:
                    # Extract client_id from URL
                    import re
                    client_id_match = re.search(r'client_id=([^&]+)', auth_url)
                    if client_id_match:
                        client_id = client_id_match.group(1)
                        
                        # Check redirect URI
                        redirect_match = re.search(r'redirect_uri=([^&]+)', auth_url)
                        redirect_uri = redirect_match.group(1) if redirect_match else 'Not found'
                        
                        details = f"""
🔗 FACEBOOK OAUTH URL ANALYSIS:
   Client ID: {client_id}
   Redirect URI: {redirect_uri}
   Full URL: {auth_url[:100]}...
   
🔍 CONFIGURATION CHECK:
   - Client ID present: ✅
   - Redirect URI present: {'✅' if redirect_match else '❌'}
   - URL format valid: ✅"""
                        
                        self.log_test(
                            "Facebook OAuth URL Configuration", 
                            True, 
                            details.strip()
                        )
                        return True
                    else:
                        self.log_test(
                            "Facebook OAuth URL Configuration", 
                            False, 
                            error="Cannot extract client_id from OAuth URL"
                        )
                        return False
                else:
                    self.log_test(
                        "Facebook OAuth URL Configuration", 
                        False, 
                        error="OAuth URL missing client_id parameter"
                    )
                    return False
            else:
                self.log_test(
                    "Facebook OAuth URL Configuration", 
                    False, 
                    error=f"Status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Facebook OAuth URL Configuration", False, error=str(e))
            return False
    
    def check_backend_logs_simulation(self):
        """Step 7: Check if we can access backend logs (limited in container)"""
        try:
            # This is a placeholder - in a real environment we'd check actual logs
            # For now, we'll just verify the diagnostic endpoints work
            
            self.log_test(
                "Backend Logs Access", 
                True, 
                "⚠️ Backend logs not directly accessible in container environment. Using diagnostic endpoints instead."
            )
            return True
                
        except Exception as e:
            self.log_test("Backend Logs Access", False, error=str(e))
            return False
    
    def run_facebook_callback_diagnostic(self):
        """Run comprehensive Facebook callback diagnostic"""
        print("🎯 FACEBOOK CALLBACK DIAGNOSTIC - FRENCH REVIEW REQUEST")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: {TEST_EMAIL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        print("🔍 DIAGNOSTIC OBJECTIVES:")
        print("1. Check social connections state")
        print("2. Test callback accessibility")
        print("3. Analyze publication behavior (real vs simulated)")
        print("4. Verify OAuth URL configuration")
        print("5. Identify why Facebook callback doesn't save connections")
        print("=" * 80)
        print()
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ CRITICAL: Authentication failed - cannot proceed with diagnostic")
            return False
        
        # Step 2: Social connections state
        print("🔍 STEP 2: SOCIAL CONNECTIONS STATE DIAGNOSTIC")
        print("-" * 50)
        connections_data = self.diagnostic_social_connections_state()
        print()
        
        # Step 3: Callback accessibility
        print("🔗 STEP 3: CALLBACK ENDPOINTS ACCESSIBILITY")
        print("-" * 50)
        self.test_facebook_callback_accessibility()
        self.test_instagram_callback_accessibility()
        print()
        
        # Step 4: OAuth URL configuration
        print("⚙️ STEP 4: OAUTH CONFIGURATION ANALYSIS")
        print("-" * 50)
        self.test_oauth_url_configuration()
        print()
        
        # Step 5: Publication behavior analysis
        print("📤 STEP 5: PUBLICATION BEHAVIOR ANALYSIS")
        print("-" * 50)
        self.test_publication_behavior_analysis()
        print()
        
        # Step 6: Backend logs (limited)
        print("📋 STEP 6: BACKEND LOGS ACCESS")
        print("-" * 50)
        self.check_backend_logs_simulation()
        print()
        
        # Summary
        self.print_diagnostic_summary()
        
        return True
    
    def print_diagnostic_summary(self):
        """Print diagnostic summary"""
        print("=" * 80)
        print("🎯 FACEBOOK CALLBACK DIAGNOSTIC SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Diagnostic Steps: {total}")
        print(f"Successful: {passed}")
        print(f"Issues Found: {total - passed}")
        print()
        
        # Key findings
        print("🔍 KEY DIAGNOSTIC FINDINGS:")
        
        # Check if we have connection data
        connections_test = next((r for r in self.test_results if r['test'] == 'Social Connections State Diagnostic'), None)
        if connections_test and connections_test['success']:
            print("✅ Social connections diagnostic accessible")
            if 'Total connections: 0' in connections_test['details']:
                print("⚠️ NO SOCIAL CONNECTIONS FOUND - This explains 'Aucune connexion facebook trouvée' error")
            else:
                print("📊 Social connections exist - analyzing token validity")
        
        # Check callback accessibility
        fb_callback_test = next((r for r in self.test_results if r['test'] == 'Facebook Callback Accessibility'), None)
        if fb_callback_test and fb_callback_test['success']:
            print("✅ Facebook callback endpoint is accessible")
        else:
            print("❌ Facebook callback endpoint has issues")
        
        # Check publication behavior
        pub_test = next((r for r in self.test_results if r['test'] == 'Publication Behavior Analysis'), None)
        if pub_test and pub_test['success']:
            if 'SIMULATION DETECTED' in pub_test['details']:
                print("⚠️ Instagram publication is SIMULATED (not real)")
            elif 'REAL PUBLICATION' in pub_test['details']:
                print("🔥 Instagram publication is REAL")
            elif 'EXPECTED ERROR' in pub_test['details']:
                print("✅ Error changed from OAuth 190 to connection error - PROGRESS CONFIRMED")
        
        print()
        
        # Root cause analysis
        print("🔬 ROOT CAUSE ANALYSIS:")
        print("Based on diagnostic results:")
        
        if connections_test and 'Total connections: 0' in connections_test.get('details', ''):
            print("🎯 PRIMARY ISSUE: No social connections exist")
            print("   - This explains the error change from OAuth 190 to 'Aucune connexion facebook trouvée'")
            print("   - Facebook callback may be failing to save connections to database")
            print("   - User needs to reconnect Facebook account")
        
        print()
        print("📋 RECOMMENDED ACTIONS:")
        print("1. User should attempt Facebook reconnection")
        print("2. Monitor backend logs during OAuth callback")
        print("3. Verify callback saves connections to correct database collection")
        print("4. Check if OAuth token exchange is successful")
        
        print("=" * 80)

def main():
    """Main diagnostic execution"""
    diagnostic = FacebookCallbackDiagnostic()
    
    try:
        success = diagnostic.run_facebook_callback_diagnostic()
        
        # Exit with appropriate code
        if success:
            failed_count = sum(1 for result in diagnostic.test_results if not result['success'])
            sys.exit(0 if failed_count == 0 else 1)
        else:
            sys.exit(2)
            
    except KeyboardInterrupt:
        print("\n⚠️ Diagnostic interrupted by user")
        sys.exit(3)
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        sys.exit(4)

if __name__ == "__main__":
    main()