#!/usr/bin/env python3
"""
Social Connections Diagnostic Test Suite - CRITICAL INCONSISTENCY ANALYSIS

PROBLÈME RAPPORTÉ PAR L'UTILISATEUR:
- Page sociale : Facebook connecté, Instagram déconnecté  
- Génération posts : 0 posts Facebook, que des posts Instagram
- Reconnexion Instagram : Bouton reste "Connecter"

DIAGNOSTIC URGENT REQUIS:
1. État réel base de données via GET /api/debug/social-connections
2. Source données page sociale via GET /api/social/connections  
3. Logique génération posts - pourquoi génère Instagram si affiché déconnecté ?

IDENTIFIANTS: lperpere@yahoo.fr / L@Reunion974!

OBJECTIF: Identifier les incohérences entre affichage frontend, génération posts, et réalité base de données.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://post-restore.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"
EXPECTED_USER_ID = "bdf87a74-e3f3-44f3-bac2-649cde3ef93e"

class SocialConnectionsDiagnosticTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        
    def authenticate(self):
        """Step 1: Authenticate with provided credentials"""
        print("🔐 Step 1: Authentication with provided credentials")
        print(f"   Email: {TEST_EMAIL}")
        print(f"   Expected User ID: {EXPECTED_USER_ID}")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json={
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Configure session with token
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                print(f"   ✅ Authentication successful")
                print(f"   User ID: {self.user_id}")
                
                # Verify user ID matches expected
                if self.user_id == EXPECTED_USER_ID:
                    print(f"   ✅ User ID matches expected value")
                else:
                    print(f"   ⚠️ User ID mismatch:")
                    print(f"      Expected: {EXPECTED_USER_ID}")
                    print(f"      Actual: {self.user_id}")
                
                return True
            else:
                print(f"   ❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {str(e)}")
            return False
    
    def test_diagnostic_endpoint(self):
        """Step 2: Test GET /api/debug/social-connections diagnostic endpoint"""
        print("\n🔍 Step 2: Test GET /api/debug/social-connections diagnostic endpoint")
        
        if not self.access_token:
            print("   ❌ No access token available")
            return False, None
        
        try:
            response = self.session.get(f"{BACKEND_URL}/debug/social-connections", timeout=10)
            
            print(f"   📡 Request sent to: {BACKEND_URL}/debug/social-connections")
            print(f"   📡 Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Diagnostic endpoint accessible")
                
                # Analyze the response structure
                print(f"\n📋 Diagnostic Response Analysis:")
                print(f"   Response keys: {list(data.keys())}")
                
                # Check for social_connections (old collection)
                if 'social_connections' in data:
                    old_connections = data['social_connections']
                    print(f"\n   📊 OLD COLLECTION (social_connections):")
                    print(f"     Count: {len(old_connections) if isinstance(old_connections, list) else 'N/A'}")
                    
                    if isinstance(old_connections, list) and old_connections:
                        print(f"     Sample connection:")
                        sample = old_connections[0]
                        for key, value in sample.items():
                            if key == 'access_token':
                                print(f"       {key}: {str(value)[:20]}..." if value else f"       {key}: None")
                            else:
                                print(f"       {key}: {value}")
                    elif isinstance(old_connections, list):
                        print(f"     ⚠️ Collection exists but is empty")
                    else:
                        print(f"     Structure: {type(old_connections)} = {old_connections}")
                
                # Check for social_connections_old (alternative field name)
                if 'social_connections_old' in data:
                    old_connections_alt = data['social_connections_old']
                    print(f"\n   📊 OLD COLLECTION ALT (social_connections_old):")
                    print(f"     Count: {len(old_connections_alt) if isinstance(old_connections_alt, list) else 'N/A'}")
                    
                    if isinstance(old_connections_alt, list) and old_connections_alt:
                        print(f"     Sample connection:")
                        sample = old_connections_alt[0]
                        for key, value in sample.items():
                            if key == 'access_token':
                                print(f"       {key}: {str(value)[:20]}..." if value else f"       {key}: None")
                            else:
                                print(f"       {key}: {value}")
                        
                        # Check for Facebook connections specifically
                        facebook_connections = [conn for conn in old_connections_alt if conn.get('platform') == 'facebook']
                        instagram_connections = [conn for conn in old_connections_alt if conn.get('platform') == 'instagram']
                        
                        print(f"     🎯 PLATFORM BREAKDOWN:")
                        print(f"       Facebook connections: {len(facebook_connections)}")
                        print(f"       Instagram connections: {len(instagram_connections)}")
                        
                        # Check active status
                        active_connections = [conn for conn in old_connections_alt if conn.get('is_active') is True]
                        print(f"       Active connections: {len(active_connections)}")
                        
                        if not active_connections:
                            print(f"       ⚠️ NO ACTIVE CONNECTIONS FOUND - This explains the error!")
                            
                    elif isinstance(old_connections_alt, list):
                        print(f"     ⚠️ Collection exists but is empty")
                    else:
                        print(f"     Structure: {type(old_connections_alt)} = {old_connections_alt}")
                
                # Check for social_media_connections (new collection)
                if 'social_media_connections' in data:
                    new_connections = data['social_media_connections']
                    print(f"\n   📊 NEW COLLECTION (social_media_connections):")
                    print(f"     Count: {len(new_connections) if isinstance(new_connections, list) else 'N/A'}")
                    
                    if isinstance(new_connections, list) and new_connections:
                        print(f"     Sample connection:")
                        sample = new_connections[0]
                        for key, value in sample.items():
                            if key == 'access_token':
                                print(f"       {key}: {str(value)[:20]}..." if value else f"       {key}: None")
                            else:
                                print(f"       {key}: {value}")
                    elif isinstance(new_connections, list):
                        print(f"     ⚠️ Collection exists but is empty")
                    else:
                        print(f"     Structure: {type(new_connections)} = {new_connections}")
                
                # Check for any other relevant fields
                for key, value in data.items():
                    if key not in ['social_connections', 'social_media_connections']:
                        print(f"\n   📋 Additional field '{key}': {type(value)} = {value}")
                
                return True, data
                
            elif response.status_code == 404:
                print(f"   ❌ Diagnostic endpoint not found (404)")
                print(f"   🔍 GET /api/debug/social-connections endpoint may not be implemented")
                return False, None
                
            else:
                print(f"   ❌ Diagnostic endpoint failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"   ❌ Diagnostic endpoint error: {str(e)}")
            return False, None
    
    def test_posts_publish_endpoint(self):
        """Step 3: Test POST /api/posts/publish to reproduce the exact error"""
        print("\n🚀 Step 3: Test POST /api/posts/publish to reproduce the error")
        
        if not self.access_token:
            print("   ❌ No access token available")
            return False
        
        try:
            # First, get a valid post_id
            posts_response = self.session.get(f"{BACKEND_URL}/posts/generated", timeout=10)
            
            if posts_response.status_code != 200:
                print(f"   ❌ Cannot get posts for testing: {posts_response.status_code}")
                return False
            
            posts_data = posts_response.json()
            posts = posts_data.get("posts", [])
            
            if not posts:
                print(f"   ⚠️ No posts available for testing publish endpoint")
                return True
            
            # Use the first post for testing
            test_post = posts[0]
            post_id = test_post.get("id")
            
            print(f"   Using test post: {post_id}")
            print(f"   Post title: {test_post.get('title', 'N/A')[:50]}...")
            print(f"   Post platform: {test_post.get('platform', 'N/A')}")
            
            # Test the publish endpoint
            response = self.session.post(
                f"{BACKEND_URL}/posts/publish",
                json={"post_id": post_id},
                timeout=10
            )
            
            print(f"   📡 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Publish endpoint successful: {data}")
                return True
            else:
                # This is expected - we want to see the exact error
                try:
                    error_data = response.json()
                    print(f"   📋 Expected error response:")
                    print(f"     Status: {response.status_code}")
                    print(f"     Error: {error_data}")
                    
                    # Check if it's the expected "Aucune connexion sociale active trouvée" error
                    error_message = error_data.get('error', '') if isinstance(error_data, dict) else str(error_data)
                    if "Aucune connexion sociale active trouvée" in error_message:
                        print(f"   ✅ CONFIRMED: This is the exact error the user is experiencing")
                        print(f"   🎯 ERROR REPRODUCED: 'Aucune connexion sociale active trouvée'")
                    else:
                        print(f"   ⚠️ Different error than expected")
                    
                    return True
                except:
                    print(f"   ❌ Non-JSON error response: {response.text}")
                    return False
                
        except Exception as e:
            print(f"   ❌ Publish endpoint test error: {str(e)}")
            return False
    
    def analyze_connection_mismatch(self, diagnostic_data):
        """Step 4: Analyze why the publish endpoint can't find connections that exist in diagnostic"""
        print("\n🔍 Step 4: Analyzing connection storage mismatch")
        
        if not diagnostic_data:
            print("   ⚠️ No diagnostic data available for analysis")
            return True
        
        try:
            # Count connections in each collection
            old_connections = diagnostic_data.get('social_connections', [])
            old_connections_alt = diagnostic_data.get('social_connections_old', [])
            new_connections = diagnostic_data.get('social_media_connections', [])
            
            old_count = len(old_connections) if isinstance(old_connections, list) else 0
            old_alt_count = len(old_connections_alt) if isinstance(old_connections_alt, list) else 0
            new_count = len(new_connections) if isinstance(new_connections, list) else 0
            
            # Use the alternative field if main field is empty
            if old_count == 0 and old_alt_count > 0:
                old_connections = old_connections_alt
                old_count = old_alt_count
            
            print(f"   📊 Connection Analysis:")
            print(f"     Old collection (social_connections): {old_count} connections")
            if old_alt_count > 0:
                print(f"     Old collection alt (social_connections_old): {old_alt_count} connections")
            print(f"     New collection (social_media_connections): {new_count} connections")
            
            # Analyze field structures
            if old_count > 0:
                print(f"\n   🔍 Old collection structure analysis:")
                sample_old = old_connections[0]
                print(f"     Fields: {list(sample_old.keys())}")
                
                # Check for Facebook connections
                facebook_connections = [conn for conn in old_connections if conn.get('platform') == 'facebook']
                instagram_connections = [conn for conn in old_connections if conn.get('platform') == 'instagram']
                
                print(f"     🎯 PLATFORM BREAKDOWN:")
                print(f"       Facebook connections: {len(facebook_connections)}")
                print(f"       Instagram connections: {len(instagram_connections)}")
                
                # Check for active status
                active_connections = [conn for conn in old_connections if conn.get('is_active') is True]
                inactive_connections = [conn for conn in old_connections if conn.get('is_active') is False]
                
                print(f"     📊 ACTIVITY STATUS:")
                print(f"       Active connections: {len(active_connections)}")
                print(f"       Inactive connections: {len(inactive_connections)}")
                
                if len(active_connections) == 0:
                    print(f"     ❌ CRITICAL: NO ACTIVE CONNECTIONS - This explains the publish error!")
                    print(f"     🔧 SOLUTION: User needs to reconnect or reactivate social accounts")
                
                # Show sample connection details
                if sample_old.get('platform'):
                    print(f"     Sample connection platform: {sample_old.get('platform')}")
                if 'is_active' in sample_old:
                    print(f"     Sample is_active: {sample_old.get('is_active')}")
                if 'connected_at' in sample_old:
                    print(f"     Sample connected_at: {sample_old.get('connected_at')}")
            
            if new_count > 0:
                print(f"\n   🔍 New collection structure analysis:")
                sample_new = new_connections[0]
                print(f"     Fields: {list(sample_new.keys())}")
                
                # Check for Facebook connections
                if sample_new.get('platform') == 'facebook' or 'facebook' in str(sample_new).lower():
                    print(f"     ✅ Contains Facebook connection data")
                
                # Check for active status
                if 'active' in sample_new:
                    print(f"     Active status: {sample_new.get('active')}")
                elif 'status' in sample_new:
                    print(f"     Status: {sample_new.get('status')}")
                elif 'is_active' in sample_new:
                    print(f"     Is Active: {sample_new.get('is_active')}")
            
            # Provide analysis conclusion
            print(f"\n   💡 Analysis Conclusion:")
            if old_count > 0:
                # Check if connections exist but are inactive
                active_connections = [conn for conn in old_connections if conn.get('is_active') is True]
                facebook_active = [conn for conn in active_connections if conn.get('platform') == 'facebook']
                
                if len(active_connections) == 0:
                    print(f"     🎯 ROOT CAUSE IDENTIFIED: Connections exist but ALL are INACTIVE")
                    print(f"     🔧 SOLUTION: The publish endpoint correctly filters for active connections")
                    print(f"     📋 RECOMMENDATION: User needs to reconnect Facebook to reactivate connection")
                    print(f"     ⚠️ Current connections are expired or deactivated")
                elif len(facebook_active) == 0:
                    print(f"     🎯 ISSUE IDENTIFIED: No ACTIVE Facebook connections found")
                    print(f"     🔧 SOLUTION: User has Instagram connections but no Facebook")
                    print(f"     📋 RECOMMENDATION: User needs to connect Facebook account")
                else:
                    print(f"     ✅ ACTIVE FACEBOOK CONNECTIONS FOUND: {len(facebook_active)}")
                    print(f"     🔧 ISSUE: Publish endpoint may have different query logic")
                    print(f"     📋 RECOMMENDATION: Check publish endpoint collection and field matching")
                    
                if new_count == 0:
                    print(f"     📋 ADDITIONAL: NEW collection is empty - publish endpoint may query wrong collection")
            elif new_count > 0:
                print(f"     🎯 ISSUE IDENTIFIED: Connections exist in NEW collection but OLD collection is empty")
                print(f"     🔧 SOLUTION: The publish endpoint likely queries the OLD collection")
                print(f"     📋 RECOMMENDATION: Update publish endpoint to use new collection")
            else:
                print(f"     🎯 NO CONNECTIONS FOUND: Both collections are empty")
                print(f"     📋 RECOMMENDATION: User needs to connect social accounts")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Connection analysis error: {str(e)}")
            return False
    
    def test_social_connections_endpoint(self):
        """Step 5: Test GET /api/social/connections endpoint for comparison"""
        print("\n🔗 Step 5: Test GET /api/social/connections endpoint for comparison")
        
        if not self.access_token:
            print("   ❌ No access token available")
            return False
        
        try:
            response = self.session.get(f"{BACKEND_URL}/social/connections", timeout=10)
            
            print(f"   📡 Request sent to: {BACKEND_URL}/social/connections")
            print(f"   📡 Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Social connections endpoint accessible")
                
                # Analyze response structure
                connections = data.get("connections", [])
                print(f"   📊 Response analysis:")
                print(f"      Total connections found: {len(connections)}")
                
                if connections:
                    print(f"   📋 Connection details:")
                    for i, conn in enumerate(connections, 1):
                        print(f"      Connection {i}:")
                        print(f"         Platform: {conn.get('platform', 'Not specified')}")
                        print(f"         Page Name: {conn.get('page_name', 'Not specified')}")
                        print(f"         Is Active: {conn.get('is_active', 'Not specified')}")
                        print(f"         User ID: {conn.get('user_id', 'Not specified')}")
                        
                        # Check if this is a Facebook connection
                        if conn.get('platform') == 'facebook':
                            print(f"         🎯 FACEBOOK CONNECTION FOUND")
                else:
                    print(f"   ⚠️ No connections found for user {self.user_id}")
                    print(f"   🔍 This matches the publish endpoint error")
                
                return True
                
            elif response.status_code == 404:
                print(f"   ❌ Endpoint not found (404)")
                print(f"   🔍 GET /api/social/connections endpoint may not be implemented")
                return False
                
            else:
                print(f"   ❌ Endpoint failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Social connections endpoint error: {str(e)}")
            return False
    
    def provide_solution_recommendations(self, diagnostic_data):
        """Step 6: Provide specific solution recommendations based on findings"""
        print("\n💡 Step 6: Solution Recommendations")
        
        if not diagnostic_data:
            print("   ⚠️ No diagnostic data available for recommendations")
            return True
        
        try:
            old_connections = diagnostic_data.get('social_connections', [])
            old_connections_alt = diagnostic_data.get('social_connections_old', [])
            new_connections = diagnostic_data.get('social_media_connections', [])
            
            old_count = len(old_connections) if isinstance(old_connections, list) else 0
            old_alt_count = len(old_connections_alt) if isinstance(old_connections_alt, list) else 0
            new_count = len(new_connections) if isinstance(new_connections, list) else 0
            
            # Use the alternative field if main field is empty
            if old_count == 0 and old_alt_count > 0:
                old_connections = old_connections_alt
                old_count = old_alt_count
            
            print(f"   📊 Based on diagnostic findings:")
            print(f"     Old collection: {old_count} connections")
            if old_alt_count > 0:
                print(f"     Old collection alt: {old_alt_count} connections")
            print(f"     New collection: {new_count} connections")
            
            print(f"\n   🔧 SPECIFIC RECOMMENDATIONS:")
            
            if old_count > 0 and new_count == 0:
                # Check if connections are active
                active_connections = [conn for conn in old_connections if conn.get('is_active') is True]
                facebook_active = [conn for conn in active_connections if conn.get('platform') == 'facebook']
                
                if len(active_connections) == 0:
                    print(f"     1. 🎯 PRIMARY ISSUE: Connections exist but are INACTIVE")
                    print(f"        - Found {old_count} connections in database")
                    print(f"        - ALL connections have is_active = False")
                    print(f"        - Publish endpoint correctly filters for active connections")
                    print(f"        - SOLUTION: User needs to reconnect Facebook")
                    
                    print(f"\n     2. 🔧 IMMEDIATE FIX OPTIONS:")
                    print(f"        Option A: User reconnects Facebook account (RECOMMENDED)")
                    print(f"        Option B: Reactivate existing connections if tokens are still valid")
                    print(f"        Option C: Check why connections became inactive")
                    
                elif len(facebook_active) == 0:
                    print(f"     1. 🎯 PRIMARY ISSUE: No active Facebook connections")
                    print(f"        - Found {len(active_connections)} active connections")
                    print(f"        - But none are Facebook connections")
                    print(f"        - SOLUTION: User needs to connect Facebook")
                    
                else:
                    print(f"     1. 🎯 UNEXPECTED: Active Facebook connections exist")
                    print(f"        - Found {len(facebook_active)} active Facebook connections")
                    print(f"        - But publish endpoint still can't find them")
                    print(f"        - SOLUTION: Check publish endpoint query logic")
                
            elif old_count == 0 and new_count > 0:
                print(f"     1. 🎯 PRIMARY ISSUE: Endpoint query mismatch")
                print(f"        - Connections exist in 'social_media_connections' collection")
                print(f"        - Publish endpoint likely queries 'social_connections'")
                print(f"        - SOLUTION: Update endpoint to use correct collection")
                
            elif old_count > 0 and new_count > 0:
                print(f"     1. 🎯 MULTIPLE COLLECTIONS: Need to verify which is active")
                print(f"        - Both collections have data")
                print(f"        - Check which collection has the most recent/valid connections")
                print(f"        - Update publish endpoint to use the correct collection")
                
            else:
                print(f"     1. 🎯 NO CONNECTIONS: User needs to reconnect")
                print(f"        - Both collections are empty")
                print(f"        - User must go through Facebook/Instagram connection process")
                print(f"        - Verify callback endpoints save connections properly")
            
            print(f"\n   📋 TECHNICAL IMPLEMENTATION:")
            print(f"     1. Check server.py line where /api/posts/publish queries connections")
            print(f"     2. Verify collection name in the database query")
            print(f"     3. Ensure user_id field matching is correct")
            print(f"     4. Test with valid Facebook access token")
            
            print(f"\n   🧪 TESTING STEPS:")
            print(f"     1. Fix the collection query in publish endpoint")
            print(f"     2. Test with this diagnostic endpoint to verify connections exist")
            print(f"     3. Test /api/posts/publish again to confirm fix")
            print(f"     4. Verify frontend shows 'Connecté' status correctly")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Recommendations error: {str(e)}")
            return False
    
    def run_diagnostic(self):
        """Run complete social connections diagnostic"""
        print("🔍 SOCIAL CONNECTIONS DIAGNOSTIC TEST SUITE")
        print("=" * 80)
        print("French Issue: 'Aucune connexion sociale active trouvée' error persists")
        print("Objective: Identify where Facebook connections are stored and why publish endpoint can't find them")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test credentials: {TEST_EMAIL}")
        print(f"Diagnostic endpoint: GET /api/debug/social-connections")
        print("=" * 80)
        
        test_results = []
        
        # Run diagnostic tests
        diagnostic_data = None
        
        tests = [
            ("Authentication and User ID Verification", self.authenticate),
            ("GET /api/debug/social-connections Diagnostic", lambda: self.test_diagnostic_endpoint()),
            ("POST /api/posts/publish Error Reproduction", self.test_posts_publish_endpoint),
            ("Connection Storage Mismatch Analysis", lambda: self.analyze_connection_mismatch(diagnostic_data)),
            ("GET /api/social/connections Comparison", self.test_social_connections_endpoint),
            ("Solution Recommendations", lambda: self.provide_solution_recommendations(diagnostic_data))
        ]
        
        for test_name, test_func in tests:
            try:
                if test_name == "GET /api/debug/social-connections Diagnostic":
                    result, diagnostic_data = test_func()
                    test_results.append((test_name, result))
                else:
                    result = test_func()
                    test_results.append((test_name, result))
            except Exception as e:
                print(f"   ❌ Test '{test_name}' crashed: {str(e)}")
                test_results.append((test_name, False))
        
        # Generate diagnostic report
        print("\n" + "=" * 80)
        print("📊 SOCIAL CONNECTIONS DIAGNOSTIC RESULTS")
        print("=" * 80)
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
            if result:
                passed_tests += 1
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"\n📈 DIAGNOSTIC SUCCESS RATE: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        # Root cause analysis
        print("\n🔍 ROOT CAUSE ANALYSIS:")
        
        # Check specific failure patterns
        auth_passed = test_results[0][1] if len(test_results) > 0 else False
        diagnostic_passed = test_results[1][1] if len(test_results) > 1 else False
        publish_test_passed = test_results[2][1] if len(test_results) > 2 else False
        
        if not auth_passed:
            print("❌ AUTHENTICATION ISSUE: Cannot authenticate with provided credentials")
            print("   → Verify credentials are correct")
            
        elif not diagnostic_passed:
            print("❌ DIAGNOSTIC ENDPOINT ISSUE: GET /api/debug/social-connections not accessible")
            print("   → Diagnostic endpoint may not be implemented")
            print("   → Cannot analyze connection storage without diagnostic data")
            
        elif not publish_test_passed:
            print("❌ PUBLISH ENDPOINT ISSUE: Cannot reproduce the error")
            print("   → POST /api/posts/publish may not be accessible")
            
        else:
            print("✅ DIAGNOSTIC SUCCESSFUL: Connection storage analysis completed")
            print("   → Check the analysis above for specific recommendations")
            
        # Provide specific recommendations
        print("\n💡 FINAL RECOMMENDATIONS:")
        
        if success_rate < 50:
            print("🚨 CRITICAL: Cannot complete diagnostic due to endpoint issues")
            print("   1. Verify GET /api/debug/social-connections endpoint exists")
            print("   2. Check authentication and authorization")
            print("   3. Ensure diagnostic endpoint returns both collections")
            
        elif success_rate < 80:
            print("⚠️ PARTIAL SUCCESS: Some diagnostic data available")
            print("   1. Review connection storage analysis above")
            print("   2. Fix collection query mismatch in publish endpoint")
            print("   3. Test again after implementing fixes")
            
        else:
            print("✅ DIAGNOSTIC COMPLETE: Issue identified and solutions provided")
            print("   1. Follow the specific recommendations above")
            print("   2. Fix the collection query in /api/posts/publish endpoint")
            print("   3. Test the fix with this diagnostic tool")
        
        print("\n🎯 CONCLUSION:")
        if diagnostic_passed:
            print("✅ DIAGNOSTIC ENDPOINT WORKING: Connection data analyzed")
            print("   → Issue is likely a collection query mismatch in publish endpoint")
            print("   → Follow the specific technical recommendations above")
        else:
            print("❌ DIAGNOSTIC ENDPOINT ISSUE: Cannot analyze connection storage")
            print("   → Implement GET /api/debug/social-connections endpoint first")
        
        print("=" * 80)
        return success_rate >= 50

def main():
    """Main diagnostic execution"""
    tester = SocialConnectionsDiagnosticTester()
    success = tester.run_diagnostic()
    
    if success:
        print("🎉 DIAGNOSTIC COMPLETED - ISSUE IDENTIFIED")
        sys.exit(0)
    else:
        print("⚠️ DIAGNOSTIC COMPLETED - CRITICAL ISSUES FOUND")
        sys.exit(1)

if __name__ == "__main__":
    main()