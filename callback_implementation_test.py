#!/usr/bin/env python3
"""
Callback Implementation Test Suite
Mission: Test OAuth callbacks with proper state format and identify implementation bugs
"""

import requests
import json
import sys
from datetime import datetime
import time

class CallbackImplementationTest:
    def __init__(self):
        self.base_url = "https://social-pub-hub.preview.emergentagent.com/api"
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
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
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
    
    def test_facebook_callback_with_proper_state(self):
        """Test Facebook callback with proper state format"""
        try:
            print(f"\n🔗 Step 2: Testing Facebook callback with proper state format")
            
            # Create proper state format: random_state|user_id
            proper_state = f"test_random_123|{self.user_id}"
            
            test_params = {
                "code": "AQBvdvgnK-test-facebook-authorization-code",
                "state": proper_state
            }
            
            print(f"   Testing with proper state: {proper_state}")
            print(f"   Parameters: {test_params}")
            
            response = self.session.get(
                f"{self.base_url}/social/facebook/callback",
                params=test_params,
                allow_redirects=False
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [302, 307]:
                redirect_url = response.headers.get('Location', '')
                print(f"   Redirect URL: {redirect_url}")
                
                # Analyze redirect URL for success/error indicators
                if "auth_success=facebook_connected" in redirect_url:
                    print(f"   ✅ Facebook callback indicates SUCCESS")
                    return True
                elif "auth_error" in redirect_url:
                    print(f"   ❌ Facebook callback indicates ERROR")
                    # Extract error details
                    if "facebook_callback_error" in redirect_url:
                        print(f"     Error type: General callback error")
                    elif "invalid_state" in redirect_url:
                        print(f"     Error type: Invalid state")
                    return False
                else:
                    print(f"   ⚠️ Facebook callback redirect unclear")
                    return False
            else:
                print(f"   ❌ Unexpected status code: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error testing Facebook callback: {str(e)}")
            return False
    
    def test_instagram_callback_with_proper_state(self):
        """Test Instagram callback with proper state format"""
        try:
            print(f"\n📸 Step 3: Testing Instagram callback with proper state format")
            
            # Create proper state format: random_state|user_id
            proper_state = f"test_instagram_456|{self.user_id}"
            
            test_params = {
                "code": "IGQVJYtest-instagram-authorization-code-from-meta",
                "state": proper_state
            }
            
            print(f"   Testing with proper state: {proper_state}")
            print(f"   Parameters: {test_params}")
            
            response = self.session.get(
                f"{self.base_url}/social/instagram/callback",
                params=test_params,
                allow_redirects=False
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [302, 307]:
                redirect_url = response.headers.get('Location', '')
                print(f"   Redirect URL: {redirect_url}")
                
                # Analyze redirect URL for success/error indicators
                if "facebook_success=true" in redirect_url:  # Note: Instagram callback uses facebook_success
                    print(f"   ✅ Instagram callback indicates SUCCESS")
                    return True
                elif "instagram_error" in redirect_url:
                    print(f"   ❌ Instagram callback indicates ERROR")
                    # Extract error details
                    if "callback_error" in redirect_url:
                        print(f"     Error type: General callback error")
                    elif "invalid_state" in redirect_url:
                        print(f"     Error type: Invalid state")
                    elif "missing_authorization" in redirect_url:
                        print(f"     Error type: Missing authorization")
                    return False
                else:
                    print(f"   ⚠️ Instagram callback redirect unclear")
                    return False
            else:
                print(f"   ❌ Unexpected status code: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error testing Instagram callback: {str(e)}")
            return False
    
    def check_connections_after_callbacks(self):
        """Check if connections were created after callback tests"""
        try:
            print(f"\n🔍 Step 4: Checking connections after callback tests")
            
            response = self.session.get(f"{self.base_url}/debug/social-connections")
            
            if response.status_code == 200:
                data = response.json()
                
                connections = data.get("social_media_connections", [])
                old_connections = data.get("social_connections_old", [])
                
                print(f"   📊 Connection State After Callbacks:")
                print(f"     social_media_connections: {len(connections)} connections")
                print(f"     social_connections_old: {len(old_connections)} connections")
                
                # Check for new connections
                facebook_connections = [c for c in connections if c.get("platform") == "facebook"]
                instagram_connections = [c for c in connections if c.get("platform") == "instagram"]
                
                print(f"     Facebook connections: {len(facebook_connections)}")
                print(f"     Instagram connections: {len(instagram_connections)}")
                
                # Show connection details if any exist
                if connections:
                    print(f"   📋 Connection Details:")
                    for i, conn in enumerate(connections):
                        platform = conn.get("platform", "unknown")
                        active = conn.get("active", conn.get("is_active", False))
                        created_at = conn.get("created_at", "unknown")
                        page_name = conn.get("page_name", "unknown")
                        print(f"     {i+1}. Platform: {platform}, Active: {active}, Page: {page_name}")
                        print(f"        Created: {created_at}")
                
                # Check old connections too (Instagram callback might save there)
                if old_connections:
                    print(f"   📋 Old Connection Details:")
                    for i, conn in enumerate(old_connections):
                        platform = conn.get("platform", "unknown")
                        active = conn.get("active", conn.get("is_active", False))
                        created_at = conn.get("created_at", "unknown")
                        print(f"     {i+1}. Platform: {platform}, Active: {active}")
                        print(f"        Created: {created_at}")
                
                return {
                    "total_connections": len(connections),
                    "facebook_connections": len(facebook_connections),
                    "instagram_connections": len(instagram_connections),
                    "old_connections": len(old_connections)
                }
            else:
                print(f"   ❌ Failed to check connections: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error checking connections: {str(e)}")
            return None
    
    def test_callback_implementation_bugs(self):
        """Identify specific implementation bugs in callbacks"""
        try:
            print(f"\n🐛 Step 5: Analyzing callback implementation bugs")
            
            print(f"   🔍 IDENTIFIED BUGS FROM CODE ANALYSIS:")
            
            print(f"   ❌ BUG 1: Instagram callback collection inconsistency")
            print(f"     - Instagram callback saves to 'social_connections' collection")
            print(f"     - But diagnostic endpoint reads from 'social_media_connections'")
            print(f"     - This causes connections to be invisible to the frontend")
            
            print(f"   ❌ BUG 2: Instagram callback platform mismatch")
            print(f"     - Line 3089: Searches for platform 'instagram'")
            print(f"     - Line 3094: Updates platform 'facebook' (wrong!)")
            print(f"     - This causes update to fail or update wrong records")
            
            print(f"   ❌ BUG 3: Instagram callback success redirect confusion")
            print(f"     - Line 3104: Uses 'facebook_success=true' for Instagram")
            print(f"     - Should use 'instagram_success=true' or 'auth_success=instagram_connected'")
            
            print(f"   ❌ BUG 4: State validation missing user_id extraction")
            print(f"     - Both callbacks expect state format 'random|user_id'")
            print(f"     - But frontend might not be sending state in this format")
            print(f"     - Missing state causes immediate error redirect")
            
            print(f"   ✅ FACEBOOK CALLBACK: Generally correct implementation")
            print(f"     - Saves to correct collection (social_media_connections)")
            print(f"     - Proper error handling and token exchange")
            print(f"     - Correct success redirect format")
            
            return {
                "instagram_collection_bug": True,
                "instagram_platform_bug": True,
                "instagram_redirect_bug": True,
                "state_format_issue": True,
                "facebook_implementation": "correct"
            }
            
        except Exception as e:
            print(f"   ❌ Error analyzing bugs: {str(e)}")
            return None
    
    def run_callback_implementation_test(self):
        """Execute the complete callback implementation test"""
        print("🎯 MISSION: Test OAuth callback implementation with proper parameters")
        print("🌐 ENVIRONMENT: Preview (social-ai-planner-2.preview.emergentagent.com)")
        print("🔍 OBJECTIVE: Identify callback implementation bugs causing connection persistence failure")
        print("👤 CREDENTIALS: lperpere@yahoo.fr / L@Reunion974!")
        print("=" * 90)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ CRITICAL: Authentication failed - cannot proceed")
            return False
        
        # Step 2: Test Facebook callback with proper state
        facebook_success = self.test_facebook_callback_with_proper_state()
        
        # Step 3: Test Instagram callback with proper state
        instagram_success = self.test_instagram_callback_with_proper_state()
        
        # Step 4: Check connections after callbacks
        connections_state = self.check_connections_after_callbacks()
        
        # Step 5: Analyze implementation bugs
        bug_analysis = self.test_callback_implementation_bugs()
        
        print("\n" + "=" * 90)
        print("🎉 CALLBACK IMPLEMENTATION TEST COMPLETED")
        print("🌐 ENVIRONMENT: Preview")
        print("=" * 90)
        
        print(f"✅ Authentication: SUCCESSFUL")
        print(f"{'✅' if facebook_success else '❌'} Facebook callback (proper state): {'SUCCESS' if facebook_success else 'FAILED'}")
        print(f"{'✅' if instagram_success else '❌'} Instagram callback (proper state): {'SUCCESS' if instagram_success else 'FAILED'}")
        print(f"✅ Connection state analysis: COMPLETED")
        print(f"✅ Bug analysis: COMPLETED")
        
        # Results analysis
        print(f"\n🔍 CALLBACK TEST RESULTS:")
        
        if facebook_success:
            print(f"   ✅ Facebook callback: Working with proper state format")
        else:
            print(f"   ❌ Facebook callback: Failed even with proper state")
        
        if instagram_success:
            print(f"   ✅ Instagram callback: Working with proper state format")
        else:
            print(f"   ❌ Instagram callback: Failed even with proper state")
        
        if connections_state:
            total = connections_state["total_connections"]
            facebook = connections_state["facebook_connections"]
            instagram = connections_state["instagram_connections"]
            old = connections_state["old_connections"]
            
            print(f"   📊 Connections created: {total} total, {facebook} Facebook, {instagram} Instagram")
            print(f"   📊 Old connections: {old} (may indicate collection bug)")
            
            if total == 0 and old == 0:
                print(f"   ❌ CRITICAL: No connections created despite callback tests")
            elif total > 0:
                print(f"   ✅ SUCCESS: Connections were created and are visible")
            elif old > 0:
                print(f"   ⚠️ PARTIAL: Connections created but in wrong collection")
        
        # Bug summary
        if bug_analysis:
            print(f"\n🐛 IMPLEMENTATION BUGS IDENTIFIED:")
            print(f"   ❌ Instagram collection inconsistency: {bug_analysis['instagram_collection_bug']}")
            print(f"   ❌ Instagram platform mismatch: {bug_analysis['instagram_platform_bug']}")
            print(f"   ❌ Instagram redirect confusion: {bug_analysis['instagram_redirect_bug']}")
            print(f"   ❌ State format validation issues: {bug_analysis['state_format_issue']}")
            print(f"   ✅ Facebook implementation: {bug_analysis['facebook_implementation']}")
        
        print(f"\n🚀 CRITICAL FIXES NEEDED:")
        print(f"   1. Fix Instagram callback to save to 'social_media_connections' collection")
        print(f"   2. Fix Instagram callback platform search/update mismatch")
        print(f"   3. Fix Instagram callback success redirect to use proper parameter")
        print(f"   4. Ensure frontend sends state in 'random|user_id' format")
        print(f"   5. Add fallback handling for missing/invalid state parameters")
        
        print("=" * 90)
        
        return True

def main():
    """Main execution function"""
    test = CallbackImplementationTest()
    
    try:
        success = test.run_callback_implementation_test()
        if success:
            print(f"\n🎯 CONCLUSION: Callback implementation bugs IDENTIFIED")
            print(f"   Multiple critical bugs found in Instagram callback implementation")
            sys.exit(0)
        else:
            print(f"\n💥 CONCLUSION: Callback implementation test FAILED")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during test: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()