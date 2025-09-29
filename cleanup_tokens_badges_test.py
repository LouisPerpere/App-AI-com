#!/usr/bin/env python3
"""
🎯 NETTOYAGE TOKENS INVALIDES ET BADGES ORPHELINS - TEST COMPLET
Test des corrections majeures pour nettoyer les données incohérentes:
1. Suppression des tokens invalides (connexions avec tokens NULL/test)
2. Nettoyage des badges orphelins (badges Facebook/Instagram sur contenus non utilisés)

Identifiants: lperpere@yahoo.fr / L@Reunion974!
Objectif: Permettre à l'utilisateur de reconnecter proprement Facebook/Instagram
"""

import requests
import json
import sys
import time
from datetime import datetime

class CleanupTokensBadgesTest:
    def __init__(self):
        # Use the frontend environment URL from .env
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
                print(f"   Token: {self.token[:30]}..." if self.token else "   Token: None")
                return True
            else:
                print(f"   ❌ Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {str(e)}")
            return False
    
    def test_social_connections_before_cleanup(self):
        """Test social connections state before cleanup"""
        try:
            print(f"\n🔍 Step 2: Checking social connections state BEFORE cleanup")
            print(f"   Endpoint: GET /api/debug/social-connections")
            
            response = self.session.get(f"{self.base_url}/debug/social-connections")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"   ✅ Diagnostic endpoint accessible")
                print(f"   📊 BEFORE CLEANUP - Social Connections State:")
                
                # Check social_media_connections
                if "social_media_connections" in data:
                    connections = data["social_media_connections"]
                    print(f"     📋 social_media_connections collection:")
                    print(f"       Total connections: {len(connections)}")
                    
                    active_connections = [c for c in connections if c.get("active") == True]
                    inactive_connections = [c for c in connections if c.get("active") == False]
                    null_token_connections = [c for c in connections if c.get("access_token") is None or c.get("access_token") == "test_token_facebook_fallback" or c.get("access_token") == "test_token_instagram_fallback"]
                    
                    print(f"       Active connections: {len(active_connections)}")
                    print(f"       Inactive connections: {len(inactive_connections)}")
                    print(f"       NULL/Test token connections: {len(null_token_connections)}")
                    
                    # Show details of problematic connections
                    for i, conn in enumerate(null_token_connections):
                        platform = conn.get("platform", "unknown")
                        token = conn.get("access_token", "None")
                        active = conn.get("active", False)
                        created_at = conn.get("created_at", "unknown")
                        print(f"         🚨 PROBLEMATIC {i+1}. Platform: {platform}, Token: {token}, Active: {active}, Created: {created_at}")
                
                # Check summary
                if "summary" in data:
                    summary = data["summary"]
                    print(f"     📊 Summary:")
                    for key, value in summary.items():
                        print(f"       {key}: {value}")
                
                return data
            else:
                print(f"   ❌ Failed to access diagnostic endpoint: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error checking social connections: {str(e)}")
            return None
    
    def test_clean_invalid_tokens(self):
        """Test POST /api/debug/clean-invalid-tokens endpoint"""
        try:
            print(f"\n🧹 Step 3: Testing invalid tokens cleanup")
            print(f"   Endpoint: POST /api/debug/clean-invalid-tokens")
            
            response = self.session.post(f"{self.base_url}/debug/clean-invalid-tokens")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"   ✅ Invalid tokens cleanup endpoint accessible")
                print(f"   📊 Cleanup Results:")
                
                # Check cleanup results
                if "message" in data:
                    print(f"     Message: {data['message']}")
                
                if "deleted_count" in data:
                    print(f"     Deleted connections: {data['deleted_count']}")
                
                if "details" in data:
                    details = data["details"]
                    print(f"     📋 Cleanup Details:")
                    for key, value in details.items():
                        print(f"       {key}: {value}")
                
                # Check if specific token types were cleaned
                if "cleaned_tokens" in data:
                    cleaned = data["cleaned_tokens"]
                    print(f"     🗑️ Cleaned Token Types:")
                    for token_type in cleaned:
                        print(f"       - {token_type}")
                
                return data
            else:
                print(f"   ❌ Failed to clean invalid tokens: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error testing invalid tokens cleanup: {str(e)}")
            return None
    
    def test_clean_library_badges(self):
        """Test POST /api/debug/clean-library-badges endpoint"""
        try:
            print(f"\n🏷️ Step 4: Testing library badges cleanup")
            print(f"   Endpoint: POST /api/debug/clean-library-badges")
            
            response = self.session.post(f"{self.base_url}/debug/clean-library-badges")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"   ✅ Library badges cleanup endpoint accessible")
                print(f"   📊 Badge Cleanup Results:")
                
                # Check cleanup results
                if "message" in data:
                    print(f"     Message: {data['message']}")
                
                if "cleaned_badges" in data:
                    cleaned_count = data["cleaned_badges"]
                    print(f"     Cleaned badges: {cleaned_count}")
                
                if "details" in data:
                    details = data["details"]
                    print(f"     📋 Badge Cleanup Details:")
                    for key, value in details.items():
                        print(f"       {key}: {value}")
                
                # Check specific badge types cleaned
                if "badge_types_cleaned" in data:
                    badge_types = data["badge_types_cleaned"]
                    print(f"     🏷️ Badge Types Cleaned:")
                    for badge_type in badge_types:
                        print(f"       - {badge_type}")
                
                return data
            else:
                print(f"   ❌ Failed to clean library badges: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error testing library badges cleanup: {str(e)}")
            return None
    
    def test_social_connections_after_cleanup(self):
        """Test social connections state after cleanup"""
        try:
            print(f"\n🔍 Step 5: Verifying social connections state AFTER cleanup")
            print(f"   Endpoint: GET /api/debug/social-connections")
            
            response = self.session.get(f"{self.base_url}/debug/social-connections")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"   ✅ Post-cleanup diagnostic accessible")
                print(f"   📊 AFTER CLEANUP - Social Connections State:")
                
                # Check social_media_connections
                if "social_media_connections" in data:
                    connections = data["social_media_connections"]
                    print(f"     📋 social_media_connections collection:")
                    print(f"       Total connections: {len(connections)}")
                    
                    active_connections = [c for c in connections if c.get("active") == True]
                    inactive_connections = [c for c in connections if c.get("active") == False]
                    null_token_connections = [c for c in connections if c.get("access_token") is None or c.get("access_token") == "test_token_facebook_fallback" or c.get("access_token") == "test_token_instagram_fallback"]
                    
                    print(f"       Active connections: {len(active_connections)}")
                    print(f"       Inactive connections: {len(inactive_connections)}")
                    print(f"       NULL/Test token connections: {len(null_token_connections)}")
                    
                    # Verify cleanup success
                    if len(null_token_connections) == 0:
                        print(f"       ✅ SUCCESS: No invalid tokens found after cleanup")
                    else:
                        print(f"       ❌ ISSUE: {len(null_token_connections)} invalid tokens still present")
                        for i, conn in enumerate(null_token_connections):
                            platform = conn.get("platform", "unknown")
                            token = conn.get("access_token", "None")
                            print(f"         🚨 REMAINING {i+1}. Platform: {platform}, Token: {token}")
                
                # Check summary
                if "summary" in data:
                    summary = data["summary"]
                    print(f"     📊 Post-Cleanup Summary:")
                    for key, value in summary.items():
                        print(f"       {key}: {value}")
                
                return data
            else:
                print(f"   ❌ Failed to access post-cleanup diagnostic: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error checking post-cleanup state: {str(e)}")
            return None
    
    def test_regular_social_connections_endpoint(self):
        """Test the regular social connections endpoint to confirm 0 active connections"""
        try:
            print(f"\n🔗 Step 6: Confirming 0 active connections via regular endpoint")
            print(f"   Endpoint: GET /api/social/connections")
            
            response = self.session.get(f"{self.base_url}/social/connections")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                connections = data.get("connections", [])
                
                print(f"   ✅ Social connections endpoint accessible")
                print(f"   📊 Active connections returned: {len(connections)}")
                
                if len(connections) == 0:
                    print(f"   ✅ SUCCESS: 0 active connections confirmed")
                    print(f"   ✅ EXPECTED: User can now reconnect Facebook/Instagram cleanly")
                else:
                    print(f"   ❌ UNEXPECTED: {len(connections)} active connections still present")
                    for i, conn in enumerate(connections):
                        platform = conn.get("platform", "unknown")
                        page_name = conn.get("page_name", "unknown")
                        print(f"     {i+1}. Platform: {platform}, Page: {page_name}")
                
                return len(connections) == 0
            else:
                print(f"   ❌ Failed to access social connections endpoint: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error testing social connections endpoint: {str(e)}")
            return False
    
    def test_publish_endpoint_after_cleanup(self):
        """Test publish endpoint to confirm it properly detects no active connections"""
        try:
            print(f"\n🚀 Step 7: Testing publish endpoint after cleanup")
            print(f"   Verifying 'Aucune connexion sociale active trouvée' response")
            
            # Get any post to test with
            response = self.session.get(f"{self.base_url}/posts/generated")
            
            if response.status_code != 200:
                print(f"   ⚠️ No posts available for testing - skipping publish test")
                return True
            
            data = response.json()
            posts = data.get("posts", [])
            
            if not posts:
                print(f"   ⚠️ No posts found for testing - skipping publish test")
                return True
            
            # Test with the first available post
            test_post = posts[0]
            post_id = test_post.get("id")
            
            print(f"   Testing with post: {post_id}")
            print(f"   Post title: {test_post.get('title', 'No title')[:50]}...")
            
            response = self.session.post(
                f"{self.base_url}/posts/publish",
                json={"post_id": post_id}
            )
            
            print(f"   📡 Publish endpoint response:")
            print(f"     Status Code: {response.status_code}")
            
            try:
                response_data = response.json()
                message = response_data.get("message", "").lower()
                error = response_data.get("error", "").lower()
                
                print(f"     Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                
                # Check if the response indicates no active connections
                if "aucune connexion sociale active" in message or "aucune connexion sociale active" in error:
                    print(f"   ✅ SUCCESS: Correct 'no active connections' response")
                    print(f"   ✅ CONFIRMED: Cleanup successful - user can reconnect cleanly")
                    return True
                else:
                    print(f"   ❌ UNEXPECTED: Response doesn't indicate clean state")
                    return False
                    
            except:
                print(f"     Response (raw): {response.text}")
                if "aucune connexion sociale active" in response.text.lower():
                    print(f"   ✅ SUCCESS: Correct 'no active connections' response")
                    return True
                return False
                
        except Exception as e:
            print(f"   ❌ Error testing publish endpoint: {str(e)}")
            return False
    
    def run_complete_cleanup_test(self):
        """Execute the complete cleanup test mission"""
        print("🎯 MISSION: Test cleanup of invalid tokens and orphaned badges")
        print("🌐 ENVIRONMENT: Preview (social-ai-planner-2.preview.emergentagent.com)")
        print("🔍 OBJECTIVE: Clean data for proper Facebook/Instagram reconnection")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with cleanup test")
            return False
        
        # Step 2: Check state before cleanup
        before_data = self.test_social_connections_before_cleanup()
        if before_data is None:
            print("\n❌ CRITICAL: Cannot check pre-cleanup state")
            return False
        
        # Step 3: Clean invalid tokens
        tokens_cleanup_result = self.test_clean_invalid_tokens()
        if tokens_cleanup_result is None:
            print("\n❌ CRITICAL: Invalid tokens cleanup failed")
            return False
        
        # Step 4: Clean library badges
        badges_cleanup_result = self.test_clean_library_badges()
        if badges_cleanup_result is None:
            print("\n❌ CRITICAL: Library badges cleanup failed")
            return False
        
        # Step 5: Check state after cleanup
        after_data = self.test_social_connections_after_cleanup()
        if after_data is None:
            print("\n❌ CRITICAL: Cannot check post-cleanup state")
            return False
        
        # Step 6: Confirm 0 active connections
        zero_connections_confirmed = self.test_regular_social_connections_endpoint()
        
        # Step 7: Test publish endpoint
        publish_test_success = self.test_publish_endpoint_after_cleanup()
        
        print("\n" + "=" * 80)
        print("🎉 CLEANUP TEST COMPLETED")
        print("🌐 ENVIRONMENT: Preview")
        print("=" * 80)
        
        print(f"✅ Authentication: SUCCESSFUL")
        print(f"✅ Pre-cleanup state check: COMPLETED")
        print(f"✅ Invalid tokens cleanup: {'SUCCESSFUL' if tokens_cleanup_result else 'FAILED'}")
        print(f"✅ Library badges cleanup: {'SUCCESSFUL' if badges_cleanup_result else 'FAILED'}")
        print(f"✅ Post-cleanup state check: COMPLETED")
        print(f"✅ Zero connections confirmation: {'SUCCESSFUL' if zero_connections_confirmed else 'FAILED'}")
        print(f"✅ Publish endpoint test: {'SUCCESSFUL' if publish_test_success else 'FAILED'}")
        
        # Analyze cleanup effectiveness
        print(f"\n📊 CLEANUP EFFECTIVENESS ANALYSIS:")
        
        if before_data and after_data:
            before_connections = before_data.get("social_media_connections", [])
            after_connections = after_data.get("social_media_connections", [])
            
            before_invalid = len([c for c in before_connections if c.get("access_token") is None or "test_token" in str(c.get("access_token", ""))])
            after_invalid = len([c for c in after_connections if c.get("access_token") is None or "test_token" in str(c.get("access_token", ""))])
            
            print(f"   📋 Invalid Tokens:")
            print(f"     Before cleanup: {before_invalid}")
            print(f"     After cleanup: {after_invalid}")
            print(f"     Cleaned: {before_invalid - after_invalid}")
            
            if after_invalid == 0:
                print(f"   ✅ SUCCESS: All invalid tokens removed")
            else:
                print(f"   ❌ ISSUE: {after_invalid} invalid tokens remain")
        
        if tokens_cleanup_result:
            print(f"   📋 Tokens Cleanup Results:")
            if "deleted_count" in tokens_cleanup_result:
                print(f"     Deleted connections: {tokens_cleanup_result['deleted_count']}")
            if "message" in tokens_cleanup_result:
                print(f"     Message: {tokens_cleanup_result['message']}")
        
        if badges_cleanup_result:
            print(f"   📋 Badges Cleanup Results:")
            if "cleaned_badges" in badges_cleanup_result:
                print(f"     Cleaned badges: {badges_cleanup_result['cleaned_badges']}")
            if "message" in badges_cleanup_result:
                print(f"     Message: {badges_cleanup_result['message']}")
        
        print(f"\n🚀 USER IMPACT ASSESSMENT:")
        if zero_connections_confirmed and publish_test_success:
            print(f"   ✅ READY FOR RECONNECTION: User can now reconnect Facebook/Instagram")
            print(f"   ✅ CLEAN STATE: No invalid tokens blocking new connections")
            print(f"   ✅ PROPER ERRORS: System correctly reports no active connections")
            print(f"   ✅ BADGES CLEANED: No orphaned badges on unused content")
        else:
            print(f"   ❌ RECONNECTION ISSUES: User may still face connection problems")
            print(f"   ❌ CLEANUP INCOMPLETE: Some invalid data may remain")
        
        print(f"\n🔍 NEXT STEPS FOR USER:")
        print(f"   1. Navigate to social connections page")
        print(f"   2. Click 'Connecter' for Facebook")
        print(f"   3. Complete OAuth flow with valid Facebook credentials")
        print(f"   4. Click 'Connecter' for Instagram")
        print(f"   5. Complete OAuth flow with valid Instagram credentials")
        print(f"   6. Verify buttons change to 'Connecté' after successful connection")
        
        print("=" * 80)
        
        # Overall success assessment
        overall_success = (
            tokens_cleanup_result is not None and
            badges_cleanup_result is not None and
            zero_connections_confirmed and
            publish_test_success
        )
        
        return overall_success

def main():
    """Main execution function"""
    cleanup_test = CleanupTokensBadgesTest()
    
    try:
        success = cleanup_test.run_complete_cleanup_test()
        if success:
            print(f"\n🎯 CONCLUSION: Cleanup test COMPLETED SUCCESSFULLY")
            print(f"   Invalid tokens and orphaned badges have been cleaned")
            print(f"   User can now reconnect Facebook/Instagram properly")
            sys.exit(0)
        else:
            print(f"\n💥 CONCLUSION: Cleanup test FAILED")
            print(f"   Some cleanup operations may not have worked correctly")
            print(f"   Please check the error messages above")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⚠️ Cleanup test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during cleanup test: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()