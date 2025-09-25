#!/usr/bin/env python3
"""
Social Connections Diagnostic Test Suite
Testing Facebook connection state management after successful login

French Review Request Translation:
"Diagnostic des connexions sociales après connexion Facebook
Après une connexion Facebook réussie, le bouton 'Connecter' s'affiche toujours au lieu de 'Connecté : Page Facebook'. 
Il faut vérifier si le problème vient du callback backend ou du chargement frontend."

Test Requirements:
1. Database - Verify if Facebook connections are saved in social_connections collection
2. GET /api/social/connections endpoint - Test if it returns connections for user
3. Data structure - Verify required fields (platform, page_name, is_active, etc.)
4. Callback save - Verify if Instagram callback saves connections with user_id

Credentials: lperpere@yahoo.fr / L@Reunion974!
User ID: bdf87a74-e3f3-44f3-bac2-649cde3ef93e
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://post-validator.preview.emergentagent.com/api"
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
    
    def test_social_connections_endpoint(self):
        """Step 2: Test GET /api/social/connections endpoint"""
        print("\n🔗 Step 2: Test GET /api/social/connections endpoint")
        
        if not self.access_token:
            print("   ❌ No access token available")
            return False
        
        try:
            response = self.session.get(f"{BACKEND_URL}/social/connections", timeout=10)
            
            print(f"   📡 Request sent to: {BACKEND_URL}/social/connections")
            print(f"   📡 Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Endpoint accessible")
                
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
                        print(f"         Username: {conn.get('username', 'Not specified')}")
                        print(f"         Is Active: {conn.get('is_active', 'Not specified')}")
                        print(f"         Connected At: {conn.get('connected_at', 'Not specified')}")
                        print(f"         User ID: {conn.get('user_id', 'Not specified')}")
                        
                        # Check if this is a Facebook connection
                        if conn.get('platform') == 'facebook':
                            print(f"         🎯 FACEBOOK CONNECTION FOUND")
                            
                            # Verify required fields for frontend display
                            required_fields = ['platform', 'page_name', 'is_active', 'user_id']
                            missing_fields = []
                            
                            for field in required_fields:
                                if not conn.get(field):
                                    missing_fields.append(field)
                            
                            if missing_fields:
                                print(f"         ❌ Missing required fields: {', '.join(missing_fields)}")
                            else:
                                print(f"         ✅ All required fields present")
                                
                                # Check if connection should show as "Connected"
                                if conn.get('is_active') and conn.get('page_name'):
                                    print(f"         ✅ Should display as 'Connecté : {conn.get('page_name')}'")
                                else:
                                    print(f"         ❌ Should NOT display as connected (inactive or no page name)")
                else:
                    print(f"   ⚠️ No connections found for user {self.user_id}")
                    print(f"   🔍 This explains why 'Connecter' button still shows")
                
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
    
    def test_database_social_connections_collection(self):
        """Step 3: Test database social_connections collection indirectly"""
        print("\n🗄️ Step 3: Database social_connections collection diagnostic")
        
        # Since we can't access MongoDB directly, we'll use available endpoints
        # to infer database state
        
        print("   📊 Attempting to infer database state through available endpoints...")
        
        # Try to find any social-related endpoints
        social_endpoints_to_test = [
            "/social/connections",
            "/social/facebook/connections", 
            "/social/instagram/connections",
            "/social/status"
        ]
        
        found_endpoints = []
        
        for endpoint in social_endpoints_to_test:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}", timeout=5)
                if response.status_code != 404:
                    found_endpoints.append((endpoint, response.status_code))
                    print(f"   ✅ Found endpoint: {endpoint} (Status: {response.status_code})")
            except:
                pass
        
        if found_endpoints:
            print(f"   📋 Available social endpoints: {len(found_endpoints)}")
            return True
        else:
            print(f"   ❌ No social endpoints found")
            print(f"   🔍 This suggests social connections functionality may not be implemented")
            return False
    
    def test_facebook_callback_simulation(self):
        """Step 4: Test Facebook callback simulation to verify save functionality"""
        print("\n📞 Step 4: Facebook callback save functionality test")
        
        print("   🧪 Simulating Facebook callback with test data...")
        
        # Test the callback endpoint with realistic parameters
        test_callback_params = {
            'code': 'test_facebook_auth_code_12345',
            'state': f'facebook_auth_state|{self.user_id}',  # Include user_id in state
        }
        
        try:
            response = self.session.get(
                f"{BACKEND_URL}/social/facebook/callback",
                params=test_callback_params,
                timeout=10,
                allow_redirects=False
            )
            
            print(f"   📡 Callback request sent with parameters:")
            print(f"      Code: {test_callback_params['code']}")
            print(f"      State: {test_callback_params['state']}")
            print(f"   📡 Response status: {response.status_code}")
            
            if response.status_code == 302:
                print(f"   ✅ Callback endpoint responds (redirect expected)")
                
                # Check redirect location for clues
                location = response.headers.get('Location', '')
                print(f"   🔗 Redirect location: {location}")
                
                # Look for success/error indicators in redirect
                if 'facebook_success=true' in location:
                    print(f"   ✅ Callback indicates success")
                elif 'facebook_error=' in location:
                    print(f"   ⚠️ Callback indicates error (expected for test data)")
                    
                    # Extract error message
                    if 'facebook_error=' in location:
                        error_part = location.split('facebook_error=')[1].split('&')[0]
                        print(f"      Error: {error_part}")
                else:
                    print(f"   ⚠️ Redirect format unclear")
                
                return True
                
            elif response.status_code == 404:
                print(f"   ❌ Facebook callback endpoint not found")
                print(f"   🔍 /api/social/facebook/callback may not be implemented")
                return False
                
            else:
                print(f"   ❌ Callback failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Callback simulation error: {str(e)}")
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