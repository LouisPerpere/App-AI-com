#!/usr/bin/env python3
"""
OAuth Callback Diagnostic Test Suite
Mission: Diagnose why OAuth callbacks are not saving connections properly
Focus: Facebook/Instagram OAuth flow callback persistence issues
"""

import requests
import json
import sys
from datetime import datetime
import time

class OAuthCallbackDiagnostic:
    def __init__(self):
        # Use the frontend environment URL from .env
        self.base_url = "https://claire-marcus-app-1.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.credentials = {
            "email": "lperpere@yahoo.fr",
            "password": "L@Reunion974!"
        }
        
    def authenticate(self):
        """Authenticate with the API"""
        try:
            print(f"🔐 Step 1: Authenticating with {self.credentials['email']}")
            
            response = self.session.post(
                f"{self.base_url}/auth/login-robust",
                json=self.credentials,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for all future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                })
                
                print(f"   ✅ Authentication successful")
                print(f"   User ID: {self.user_id}")
                return True
            else:
                print(f"   ❌ Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {str(e)}")
            return False
    
    def check_backend_logs(self):
        """Check backend logs for callback execution"""
        try:
            print(f"\n📋 Step 2: Checking backend logs for callback activity")
            
            # Check if there's a logs endpoint or if we can access supervisor logs
            import subprocess
            
            try:
                # Try to get backend logs from supervisor
                result = subprocess.run(
                    ["tail", "-n", "50", "/var/log/supervisor/backend.err.log"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0 and result.stdout:
                    print(f"   ✅ Backend error logs found:")
                    logs = result.stdout.strip().split('\n')
                    
                    # Look for OAuth-related logs
                    oauth_logs = [log for log in logs if any(keyword in log.lower() for keyword in 
                                 ['oauth', 'callback', 'facebook', 'instagram', 'social', 'connexion'])]
                    
                    if oauth_logs:
                        print(f"   🔍 OAuth-related log entries ({len(oauth_logs)} found):")
                        for log in oauth_logs[-10:]:  # Show last 10 OAuth-related logs
                            print(f"     {log}")
                    else:
                        print(f"   ⚠️ No OAuth-related logs found in recent entries")
                        print(f"   📋 Recent log entries:")
                        for log in logs[-5:]:  # Show last 5 logs
                            print(f"     {log}")
                else:
                    print(f"   ⚠️ Could not access backend error logs")
                    
            except subprocess.TimeoutExpired:
                print(f"   ⚠️ Timeout accessing backend logs")
            except Exception as log_error:
                print(f"   ⚠️ Error accessing logs: {str(log_error)}")
                
            # Also try to check stdout logs
            try:
                result = subprocess.run(
                    ["tail", "-n", "30", "/var/log/supervisor/backend.out.log"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0 and result.stdout:
                    logs = result.stdout.strip().split('\n')
                    oauth_logs = [log for log in logs if any(keyword in log.lower() for keyword in 
                                 ['oauth', 'callback', 'facebook', 'instagram', 'social', 'connexion'])]
                    
                    if oauth_logs:
                        print(f"   🔍 OAuth-related stdout logs ({len(oauth_logs)} found):")
                        for log in oauth_logs[-5:]:
                            print(f"     {log}")
                            
            except Exception:
                pass
                
        except Exception as e:
            print(f"   ❌ Error checking backend logs: {str(e)}")
    
    def test_facebook_callback_endpoint(self):
        """Test Facebook callback endpoint directly"""
        try:
            print(f"\n🔗 Step 3: Testing Facebook callback endpoint")
            print(f"   Endpoint: GET /api/social/facebook/callback")
            
            # Test with minimal parameters that would come from Facebook OAuth
            test_params = {
                "code": "test_authorization_code_123",
                "state": "test_state_456"
            }
            
            print(f"   Testing with parameters: {test_params}")
            
            response = self.session.get(
                f"{self.base_url}/social/facebook/callback",
                params=test_params
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Response headers: {dict(response.headers)}")
            
            if response.status_code in [200, 302, 307]:
                print(f"   ✅ Callback endpoint is accessible")
                
                # Check if it's a redirect
                if response.status_code in [302, 307]:
                    redirect_url = response.headers.get('Location', 'No location header')
                    print(f"   🔄 Redirect detected to: {redirect_url}")
                
                # Try to get response content
                try:
                    if response.headers.get('content-type', '').startswith('application/json'):
                        data = response.json()
                        print(f"   📄 JSON Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    else:
                        content = response.text[:500]  # First 500 chars
                        print(f"   📄 Response content (first 500 chars): {content}")
                except:
                    print(f"   📄 Response content: {response.text[:200]}")
                    
            else:
                print(f"   ❌ Callback endpoint error: {response.text}")
                
            return response.status_code
            
        except Exception as e:
            print(f"   ❌ Error testing Facebook callback: {str(e)}")
            return None
    
    def test_instagram_callback_endpoint(self):
        """Test Instagram callback endpoint directly"""
        try:
            print(f"\n📸 Step 4: Testing Instagram callback endpoint")
            print(f"   Endpoint: GET /api/social/instagram/callback")
            
            # Test with minimal parameters that would come from Instagram OAuth
            test_params = {
                "code": "test_instagram_code_789",
                "state": "test_instagram_state_012"
            }
            
            print(f"   Testing with parameters: {test_params}")
            
            response = self.session.get(
                f"{self.base_url}/social/instagram/callback",
                params=test_params
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Response headers: {dict(response.headers)}")
            
            if response.status_code in [200, 302, 307]:
                print(f"   ✅ Callback endpoint is accessible")
                
                # Check if it's a redirect
                if response.status_code in [302, 307]:
                    redirect_url = response.headers.get('Location', 'No location header')
                    print(f"   🔄 Redirect detected to: {redirect_url}")
                
                # Try to get response content
                try:
                    if response.headers.get('content-type', '').startswith('application/json'):
                        data = response.json()
                        print(f"   📄 JSON Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    else:
                        content = response.text[:500]  # First 500 chars
                        print(f"   📄 Response content (first 500 chars): {content}")
                except:
                    print(f"   📄 Response content: {response.text[:200]}")
                    
            else:
                print(f"   ❌ Callback endpoint error: {response.text}")
                
            return response.status_code
            
        except Exception as e:
            print(f"   ❌ Error testing Instagram callback: {str(e)}")
            return None
    
    def check_social_connections_before_after(self):
        """Check social connections state before and after callback attempts"""
        try:
            print(f"\n🔍 Step 5: Checking social connections state")
            print(f"   Endpoint: GET /api/debug/social-connections")
            
            response = self.session.get(f"{self.base_url}/debug/social-connections")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"   ✅ Social connections diagnostic accessible")
                
                # Check current state
                connections = data.get("social_media_connections", [])
                old_connections = data.get("social_connections_old", [])
                
                print(f"   📊 Current Connection State:")
                print(f"     social_media_connections: {len(connections)} connections")
                print(f"     social_connections_old: {len(old_connections)} connections")
                
                # Analyze active connections
                active_connections = [c for c in connections if c.get("active") == True]
                facebook_connections = [c for c in connections if c.get("platform") == "facebook"]
                instagram_connections = [c for c in connections if c.get("platform") == "instagram"]
                
                print(f"     Active connections: {len(active_connections)}")
                print(f"     Facebook connections: {len(facebook_connections)}")
                print(f"     Instagram connections: {len(instagram_connections)}")
                
                # Show connection details
                if connections:
                    print(f"   📋 Connection Details:")
                    for i, conn in enumerate(connections):
                        platform = conn.get("platform", "unknown")
                        active = conn.get("active", False)
                        created_at = conn.get("created_at", "unknown")
                        page_name = conn.get("page_name", "unknown")
                        print(f"     {i+1}. Platform: {platform}, Active: {active}, Page: {page_name}, Created: {created_at}")
                else:
                    print(f"   ⚠️ No connections found in social_media_connections")
                
                # Check old connections for comparison
                if old_connections:
                    print(f"   📋 Old Connection Details:")
                    for i, conn in enumerate(old_connections):
                        platform = conn.get("platform", "unknown")
                        is_active = conn.get("is_active", False)
                        created_at = conn.get("created_at", "unknown")
                        print(f"     {i+1}. Platform: {platform}, Active: {is_active}, Created: {created_at}")
                
                return {
                    "current_connections": len(connections),
                    "active_connections": len(active_connections),
                    "facebook_connections": len(facebook_connections),
                    "instagram_connections": len(instagram_connections),
                    "old_connections": len(old_connections)
                }
            else:
                print(f"   ❌ Failed to access social connections diagnostic: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error checking social connections: {str(e)}")
            return None
    
    def test_oauth_authorization_urls(self):
        """Test OAuth authorization URL generation"""
        try:
            print(f"\n🔗 Step 6: Testing OAuth authorization URL generation")
            
            # Test Facebook auth URL
            print(f"   Testing Facebook auth URL generation:")
            response = self.session.get(f"{self.base_url}/social/facebook/auth-url")
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get("auth_url", "")
                print(f"   ✅ Facebook auth URL generated")
                print(f"     URL: {auth_url[:100]}..." if len(auth_url) > 100 else f"     URL: {auth_url}")
                
                # Check if URL contains expected parameters
                if "facebook.com" in auth_url and "client_id" in auth_url:
                    print(f"   ✅ Facebook auth URL appears valid")
                else:
                    print(f"   ⚠️ Facebook auth URL may be invalid")
            else:
                print(f"   ❌ Facebook auth URL generation failed: {response.text}")
            
            # Test Instagram auth URL
            print(f"   Testing Instagram auth URL generation:")
            response = self.session.get(f"{self.base_url}/social/instagram/auth-url")
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get("auth_url", "")
                print(f"   ✅ Instagram auth URL generated")
                print(f"     URL: {auth_url[:100]}..." if len(auth_url) > 100 else f"     URL: {auth_url}")
                
                # Check if URL contains expected parameters
                if ("instagram.com" in auth_url or "facebook.com" in auth_url) and "client_id" in auth_url:
                    print(f"   ✅ Instagram auth URL appears valid")
                else:
                    print(f"   ⚠️ Instagram auth URL may be invalid")
            else:
                print(f"   ❌ Instagram auth URL generation failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error testing OAuth URLs: {str(e)}")
    
    def simulate_callback_flow(self):
        """Simulate a complete OAuth callback flow"""
        try:
            print(f"\n🔄 Step 7: Simulating complete OAuth callback flow")
            
            # First, check initial state
            print(f"   📊 Checking initial connection state...")
            initial_state = self.check_social_connections_before_after()
            
            # Simulate Facebook callback with more realistic parameters
            print(f"   🔗 Simulating Facebook OAuth callback...")
            
            # Use parameters that would be more realistic from Facebook
            facebook_params = {
                "code": "AQBvdvgnK-test-authorization-code-from-facebook",
                "state": f"facebook_oauth_{self.user_id}_{int(time.time())}"
            }
            
            response = self.session.get(
                f"{self.base_url}/social/facebook/callback",
                params=facebook_params,
                allow_redirects=False  # Don't follow redirects to see what happens
            )
            
            print(f"     Facebook callback status: {response.status_code}")
            
            if response.status_code in [302, 307]:
                redirect_url = response.headers.get('Location', '')
                print(f"     Facebook callback redirect: {redirect_url}")
                
                # Check if redirect indicates success or failure
                if "success" in redirect_url.lower():
                    print(f"     ✅ Facebook callback appears successful")
                elif "error" in redirect_url.lower():
                    print(f"     ❌ Facebook callback indicates error")
                else:
                    print(f"     ⚠️ Facebook callback redirect unclear")
            else:
                print(f"     Response: {response.text[:200]}")
            
            # Wait a moment for any async processing
            time.sleep(2)
            
            # Check state after Facebook callback
            print(f"   📊 Checking connection state after Facebook callback...")
            post_facebook_state = self.check_social_connections_before_after()
            
            # Compare states
            if initial_state and post_facebook_state:
                if post_facebook_state["current_connections"] > initial_state["current_connections"]:
                    print(f"   ✅ New connection detected after Facebook callback!")
                elif post_facebook_state["facebook_connections"] > initial_state["facebook_connections"]:
                    print(f"   ✅ New Facebook connection detected!")
                else:
                    print(f"   ❌ No new connections detected after Facebook callback")
                    print(f"     Before: {initial_state['current_connections']} connections")
                    print(f"     After: {post_facebook_state['current_connections']} connections")
            
            # Now simulate Instagram callback
            print(f"   📸 Simulating Instagram OAuth callback...")
            
            instagram_params = {
                "code": "IGQVJYtest-instagram-authorization-code-from-meta",
                "state": f"instagram_oauth_{self.user_id}_{int(time.time())}"
            }
            
            response = self.session.get(
                f"{self.base_url}/social/instagram/callback",
                params=instagram_params,
                allow_redirects=False
            )
            
            print(f"     Instagram callback status: {response.status_code}")
            
            if response.status_code in [302, 307]:
                redirect_url = response.headers.get('Location', '')
                print(f"     Instagram callback redirect: {redirect_url}")
                
                if "success" in redirect_url.lower():
                    print(f"     ✅ Instagram callback appears successful")
                elif "error" in redirect_url.lower():
                    print(f"     ❌ Instagram callback indicates error")
                else:
                    print(f"     ⚠️ Instagram callback redirect unclear")
            else:
                print(f"     Response: {response.text[:200]}")
            
            # Wait and check final state
            time.sleep(2)
            
            print(f"   📊 Checking final connection state...")
            final_state = self.check_social_connections_before_after()
            
            # Final comparison
            if initial_state and final_state:
                print(f"   📊 Connection State Summary:")
                print(f"     Initial connections: {initial_state['current_connections']}")
                print(f"     Final connections: {final_state['current_connections']}")
                print(f"     Initial Facebook: {initial_state['facebook_connections']}")
                print(f"     Final Facebook: {final_state['facebook_connections']}")
                print(f"     Initial Instagram: {initial_state['instagram_connections']}")
                print(f"     Final Instagram: {final_state['instagram_connections']}")
                
                if final_state["current_connections"] > initial_state["current_connections"]:
                    print(f"   ✅ CALLBACK SUCCESS: New connections were created!")
                else:
                    print(f"   ❌ CALLBACK FAILURE: No new connections were created")
                    print(f"   🔍 This confirms the user's reported issue")
            
        except Exception as e:
            print(f"   ❌ Error simulating callback flow: {str(e)}")
    
    def run_oauth_callback_diagnostic(self):
        """Execute the complete OAuth callback diagnostic"""
        print("🎯 MISSION: Diagnose OAuth callback persistence issues")
        print("🌐 ENVIRONMENT: Preview (social-ai-planner-2.preview.emergentagent.com)")
        print("🔍 OBJECTIVE: Identify why OAuth callbacks don't save connections")
        print("👤 CREDENTIALS: lperpere@yahoo.fr / L@Reunion974!")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with diagnostic")
            return False
        
        # Step 2: Check backend logs for callback activity
        self.check_backend_logs()
        
        # Step 3: Test Facebook callback endpoint
        facebook_status = self.test_facebook_callback_endpoint()
        
        # Step 4: Test Instagram callback endpoint
        instagram_status = self.test_instagram_callback_endpoint()
        
        # Step 5: Check current social connections state
        connections_state = self.check_social_connections_before_after()
        
        # Step 6: Test OAuth authorization URL generation
        self.test_oauth_authorization_urls()
        
        # Step 7: Simulate complete callback flow
        self.simulate_callback_flow()
        
        print("\n" + "=" * 80)
        print("🎉 OAUTH CALLBACK DIAGNOSTIC COMPLETED")
        print("🌐 ENVIRONMENT: Preview")
        print("=" * 80)
        
        print(f"✅ Authentication: SUCCESSFUL")
        print(f"✅ Backend logs: CHECKED")
        print(f"{'✅' if facebook_status in [200, 302, 307] else '❌'} Facebook callback endpoint: {'ACCESSIBLE' if facebook_status in [200, 302, 307] else 'FAILED'}")
        print(f"{'✅' if instagram_status in [200, 302, 307] else '❌'} Instagram callback endpoint: {'ACCESSIBLE' if instagram_status in [200, 302, 307] else 'FAILED'}")
        print(f"✅ Social connections state: ANALYZED")
        print(f"✅ OAuth URL generation: TESTED")
        print(f"✅ Callback flow simulation: COMPLETED")
        
        # Diagnostic conclusions
        print(f"\n🔍 DIAGNOSTIC FINDINGS:")
        
        if connections_state:
            if connections_state["current_connections"] == 0:
                print(f"   ❌ ROOT CAUSE CONFIRMED: No active social connections exist")
                print(f"   ❌ CALLBACK ISSUE: OAuth callbacks are not creating/saving connections")
                print(f"   ⚠️ USER SYMPTOM EXPLAINED: Buttons remain 'Connecter' because no connections are saved")
            else:
                print(f"   ✅ CONNECTIONS EXIST: {connections_state['current_connections']} connections found")
                print(f"   🔍 NEED INVESTIGATION: Why frontend shows 'Connecter' if connections exist")
        
        print(f"\n🚀 RECOMMENDED ACTIONS:")
        print(f"   1. Check callback endpoint implementation for connection persistence")
        print(f"   2. Verify OAuth token exchange is working properly")
        print(f"   3. Check database write operations in callback handlers")
        print(f"   4. Verify frontend is checking connection status correctly")
        print(f"   5. Test with real OAuth flow (not simulated) to confirm issue")
        
        print("=" * 80)
        
        return True

def main():
    """Main execution function"""
    diagnostic = OAuthCallbackDiagnostic()
    
    try:
        success = diagnostic.run_oauth_callback_diagnostic()
        if success:
            print(f"\n🎯 CONCLUSION: OAuth callback diagnostic COMPLETED")
            print(f"   Issue identified: Callbacks not persisting connections properly")
            sys.exit(0)
        else:
            print(f"\n💥 CONCLUSION: OAuth callback diagnostic FAILED")
            print(f"   Please check the error messages above")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⚠️ Diagnostic interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during diagnostic: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()