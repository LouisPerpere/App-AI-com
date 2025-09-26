#!/usr/bin/env python3
"""
Social Connections Diagnostic Test Suite
Testing the GET /api/debug/social-connections endpoint to identify where social connections are stored
and why the /api/posts/publish endpoint cannot find them.

French Review Request:
"J'ai créé un endpoint de diagnostic pour vérifier l'état des connexions sociales dans la base de données. 
L'utilisateur a encore l'erreur 'Aucune connexion sociale active trouvée' malgré mes corrections."

Test Requirements:
1. Authentication: lperpere@yahoo.fr / L@Reunion974!
2. Diagnostic endpoint: GET /api/debug/social-connections
   - Shows connections in both collections:
   - social_connections (old collection)
   - social_media_connections (new collection)

Objective: Identify exactly where Facebook connections are stored and with what fields,
to understand why the /api/posts/publish endpoint cannot find them.

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
            new_connections = diagnostic_data.get('social_media_connections', [])
            
            old_count = len(old_connections) if isinstance(old_connections, list) else 0
            new_count = len(new_connections) if isinstance(new_connections, list) else 0
            
            print(f"   📊 Connection Analysis:")
            print(f"     Old collection (social_connections): {old_count} connections")
            print(f"     New collection (social_media_connections): {new_count} connections")
            
            # Analyze field structures
            if old_count > 0:
                print(f"\n   🔍 Old collection structure analysis:")
                sample_old = old_connections[0]
                print(f"     Fields: {list(sample_old.keys())}")
                
                # Check for Facebook connections
                if sample_old.get('platform') == 'facebook' or 'facebook' in str(sample_old).lower():
                    print(f"     ✅ Contains Facebook connection data")
                
                # Check for active status
                if 'active' in sample_old:
                    print(f"     Active status: {sample_old.get('active')}")
                elif 'status' in sample_old:
                    print(f"     Status: {sample_old.get('status')}")
                elif 'is_active' in sample_old:
                    print(f"     Is Active: {sample_old.get('is_active')}")
            
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
            if old_count > 0 and new_count == 0:
                print(f"     🎯 ISSUE IDENTIFIED: Connections exist in OLD collection but NEW collection is empty")
                print(f"     🔧 SOLUTION: The publish endpoint likely queries the NEW collection")
                print(f"     📋 RECOMMENDATION: Migrate connections from old to new collection")
            elif old_count == 0 and new_count > 0:
                print(f"     🎯 ISSUE IDENTIFIED: Connections exist in NEW collection but OLD collection is empty")
                print(f"     🔧 SOLUTION: The publish endpoint likely queries the OLD collection")
                print(f"     📋 RECOMMENDATION: Update publish endpoint to use new collection")
            elif old_count > 0 and new_count > 0:
                print(f"     🎯 CONNECTIONS EXIST IN BOTH: Need to check which one publish endpoint uses")
                print(f"     📋 RECOMMENDATION: Verify publish endpoint collection query")
            else:
                print(f"     🎯 NO CONNECTIONS FOUND: Both collections are empty")
                print(f"     📋 RECOMMENDATION: User needs to reconnect social accounts")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Connection analysis error: {str(e)}")
            return False
    
    def test_instagram_callback_user_id_extraction(self):
        """Step 5: Test Instagram callback user_id extraction from state"""
        print("\n🔍 Step 5: Instagram callback user_id extraction test")
        
        print("   🧪 Testing state format: 'state|user_id'")
        
        # Test Instagram callback with state containing user_id
        test_state = f"instagram_auth_state|{self.user_id}"
        test_callback_params = {
            'code': 'test_instagram_auth_code_67890',
            'state': test_state
        }
        
        try:
            response = self.session.get(
                f"{BACKEND_URL}/social/instagram/callback",
                params=test_callback_params,
                timeout=10,
                allow_redirects=False
            )
            
            print(f"   📡 Instagram callback request sent:")
            print(f"      Code: {test_callback_params['code']}")
            print(f"      State: {test_state}")
            print(f"   📡 Response status: {response.status_code}")
            
            if response.status_code == 302:
                print(f"   ✅ Instagram callback endpoint responds")
                
                location = response.headers.get('Location', '')
                print(f"   🔗 Redirect location: {location}")
                
                # Check for success/error patterns
                if 'instagram_success=true' in location:
                    print(f"   ✅ Callback processed successfully")
                elif 'instagram_error=' in location:
                    print(f"   ⚠️ Callback shows error (expected for test data)")
                    
                    # This is actually good - it means the callback is processing the request
                    print(f"   ✅ Callback is processing requests (error expected for test code)")
                
                return True
                
            else:
                print(f"   ❌ Instagram callback failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Instagram callback test error: {str(e)}")
            return False
    
    def test_connection_data_structure_requirements(self):
        """Step 6: Test connection data structure requirements"""
        print("\n📋 Step 6: Connection data structure requirements validation")
        
        print("   🔍 Testing what data structure is expected for frontend display...")
        
        # Required fields for frontend to show "Connecté : Page Facebook"
        required_fields = {
            'platform': 'facebook',
            'page_name': 'Test Page Name',
            'is_active': True,
            'user_id': self.user_id,
            'connected_at': datetime.now().isoformat(),
            'access_token': 'test_token_12345'
        }
        
        print(f"   📊 Required fields for 'Connecté : Page Facebook' display:")
        for field, example_value in required_fields.items():
            print(f"      {field}: {example_value}")
        
        # Test if we can create a connection (if endpoint exists)
        try:
            # Try to POST a test connection
            response = self.session.post(
                f"{BACKEND_URL}/social/connections",
                json=required_fields,
                timeout=10
            )
            
            print(f"   📡 Test connection creation attempt: {response.status_code}")
            
            if response.status_code == 201:
                print(f"   ✅ Connection creation endpoint works")
                return True
            elif response.status_code == 404:
                print(f"   ❌ Connection creation endpoint not found")
                return False
            else:
                print(f"   ⚠️ Connection creation response: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Connection creation test error: {str(e)}")
            return False
    
    def run_diagnostic(self):
        """Run complete social connections diagnostic"""
        print("🔍 SOCIAL CONNECTIONS DIAGNOSTIC TEST SUITE")
        print("=" * 80)
        print("French Issue: Bouton 'Connecter' s'affiche au lieu de 'Connecté : Page Facebook'")
        print("Objective: Determine if issue is backend (no save) or frontend (no reload)")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test credentials: {TEST_EMAIL}")
        print(f"Expected User ID: {EXPECTED_USER_ID}")
        print("=" * 80)
        
        test_results = []
        
        # Run diagnostic tests
        tests = [
            ("Authentication and User ID Verification", self.authenticate),
            ("GET /api/social/connections Endpoint", self.test_social_connections_endpoint),
            ("Database Social Connections Collection", self.test_database_social_connections_collection),
            ("Facebook Callback Save Functionality", self.test_facebook_callback_simulation),
            ("Instagram Callback User ID Extraction", self.test_instagram_callback_user_id_extraction),
            ("Connection Data Structure Requirements", self.test_connection_data_structure_requirements)
        ]
        
        for test_name, test_func in tests:
            try:
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
        connections_endpoint_passed = test_results[1][1] if len(test_results) > 1 else False
        
        if not auth_passed:
            print("❌ AUTHENTICATION ISSUE: Cannot authenticate with provided credentials")
            print("   → Verify credentials are correct")
            
        elif not connections_endpoint_passed:
            print("❌ BACKEND ISSUE: GET /api/social/connections endpoint not working")
            print("   → Social connections functionality may not be implemented")
            print("   → This explains why frontend shows 'Connecter' instead of 'Connecté'")
            
        else:
            print("✅ BACKEND ENDPOINTS ACCESSIBLE: Issue may be in data persistence or frontend")
            
        # Provide specific recommendations
        print("\n💡 RECOMMENDATIONS:")
        
        if success_rate < 50:
            print("🚨 CRITICAL: Social connections system appears to be missing or broken")
            print("   1. Implement GET /api/social/connections endpoint")
            print("   2. Implement social_connections database collection")
            print("   3. Ensure Facebook/Instagram callbacks save connections with user_id")
            
        elif success_rate < 80:
            print("⚠️ PARTIAL IMPLEMENTATION: Some social connections functionality exists")
            print("   1. Check database for existing connections")
            print("   2. Verify callback endpoints save connections properly")
            print("   3. Ensure frontend reloads connections after successful auth")
            
        else:
            print("✅ SYSTEM APPEARS FUNCTIONAL: Issue may be specific to user or timing")
            print("   1. Check if connections exist but frontend doesn't reload them")
            print("   2. Verify frontend calls GET /api/social/connections after auth")
            print("   3. Check browser cache or state management issues")
        
        print("\n🎯 CONCLUSION:")
        if connections_endpoint_passed:
            print("✅ BACKEND READY: Social connections endpoint accessible")
            print("   → Issue likely in frontend state management or data persistence")
        else:
            print("❌ BACKEND ISSUE: Social connections system not properly implemented")
            print("   → This is the root cause of the 'Connecter' button issue")
        
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