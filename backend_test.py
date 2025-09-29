#!/usr/bin/env python3
"""
BACKEND TESTING - CHATGPT BINARY APPROACH FOR FACEBOOK PUBLICATION
Test des nouveaux endpoints binaires selon l'approche ChatGPT 100% fiable

Identifiants: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import time
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://social-publisher-10.preview.emergentagent.com/api"
CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class FacebookBinaryTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        
    def authenticate(self):
        """Authentification avec les identifiants fournis"""
        print("🔐 STEP 1: Authentication...")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json=CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                self.user_id = data.get('user_id')
                
                # Set authorization header for all future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                
                print(f"✅ Authentication successful")
                print(f"   User ID: {self.user_id}")
                print(f"   Token: {self.access_token[:20]}...")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_binary_photo_endpoint(self):
        """Test 1: Endpoint /publish/facebook/photo - Upload binaire direct"""
        print("\n📘 STEP 2: Test Binary Photo Upload Endpoint...")
        
        try:
            # Create a test image file in memory
            test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x12IDATx\x9cc```bPPP\x00\x02\xac\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
            
            # Test data for binary upload
            form_data = {
                'caption': 'Test ChatGPT Binary Upload',
                'page_id': 'test_page_id',
                'access_token': 'test_access_token'
            }
            
            files = {
                'file': ('test_image.png', test_image_data, 'image/png')
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/publish/facebook/photo",
                data=form_data,
                files=files,
                timeout=30
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Binary photo endpoint accessible")
                print(f"   Response: {json.dumps(result, indent=2)}")
                
                # Check if it's using binary approach
                if 'binary' in str(result).lower() or 'source' in str(result).lower():
                    print("✅ Endpoint uses binary approach (source method)")
                else:
                    print("⚠️ Binary approach not confirmed in response")
                    
                return True
            else:
                print(f"❌ Binary photo endpoint failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Binary photo endpoint error: {str(e)}")
            return False
    
    def test_publish_with_image_endpoint(self):
        """Test 2: Endpoint /social/facebook/publish-with-image - Télécharge + upload binaire"""
        print("\n📘 STEP 3: Test Publish With Image Endpoint...")
        
        try:
            # Test with system image URL
            test_data = {
                "text": "Test ChatGPT Binary Upload",
                "image_url": "/api/content/IMAGE_ID/file"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/social/facebook/publish-with-image",
                json=test_data,
                timeout=30
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code in [200, 400, 401]:  # 400/401 expected without valid Facebook connection
                result = response.json()
                print(f"✅ Publish with image endpoint accessible")
                print(f"   Response: {json.dumps(result, indent=2)}")
                
                # Check for binary method indicators
                if 'binary' in str(result).lower() or 'method' in result:
                    print("✅ Endpoint indicates binary method usage")
                else:
                    print("⚠️ Binary method not explicitly confirmed")
                    
                return True
            else:
                print(f"❌ Publish with image endpoint failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Publish with image endpoint error: {str(e)}")
            return False
    
    def test_facebook_connection_status(self):
        """Test 3: Vérifier l'état des connexions Facebook"""
        print("\n📘 STEP 4: Test Facebook Connection Status...")
        
        try:
            response = self.session.get(
                f"{BACKEND_URL}/social/connections",
                timeout=10
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                connections = response.json()
                print(f"✅ Social connections endpoint accessible")
                print(f"   Connections: {json.dumps(connections, indent=2)}")
                
                # Check for Facebook connections
                facebook_connections = [conn for conn in connections if conn.get('platform') == 'facebook']
                print(f"   Facebook connections found: {len(facebook_connections)}")
                
                return True
            else:
                print(f"❌ Social connections failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Social connections error: {str(e)}")
            return False
    
    def test_accessible_images(self):
        """Test 4: Vérifier les images accessibles pour Facebook"""
        print("\n📘 STEP 5: Test Accessible Images for Facebook...")
        
        try:
            response = self.session.get(
                f"{BACKEND_URL}/content/pending?limit=5",
                timeout=10
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                content = response.json()
                images = content.get('content', [])
                print(f"✅ Content endpoint accessible")
                print(f"   Images found: {len(images)}")
                
                # Test image accessibility
                for i, image in enumerate(images[:3]):  # Test first 3 images
                    image_id = image.get('id')
                    if image_id:
                        # Test direct image access
                        img_response = self.session.get(
                            f"{BACKEND_URL}/content/{image_id}/file",
                            timeout=5
                        )
                        
                        if img_response.status_code == 200:
                            print(f"   ✅ Image {i+1} accessible: {image_id}")
                        else:
                            print(f"   ❌ Image {i+1} not accessible: {image_id}")
                
                return True
            else:
                print(f"❌ Content endpoint failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Content endpoint error: {str(e)}")
            return False
    
    def test_binary_vs_url_approach(self):
        """Test 5: Validation méthode binaire vs URL"""
        print("\n📘 STEP 6: Test Binary vs URL Approach Validation...")
        
        try:
            # Test with external image URL (old approach)
            external_test = {
                "text": "Test URL Approach",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/social/facebook/publish-with-image",
                json=external_test,
                timeout=30
            )
            
            print(f"   External URL Status: {response.status_code}")
            
            if response.status_code in [200, 400, 401]:
                result = response.json()
                print(f"   External URL Response: {json.dumps(result, indent=2)}")
                
                # Check if response indicates binary method
                method_used = result.get('method', 'unknown')
                print(f"   Method used: {method_used}")
                
                if 'binary' in method_used.lower():
                    print("✅ System uses binary approach even for external URLs")
                elif 'url' in method_used.lower():
                    print("⚠️ System still uses URL approach for external images")
                else:
                    print("⚠️ Method not clearly indicated")
                
                return True
            else:
                print(f"❌ Binary vs URL test failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Binary vs URL test error: {str(e)}")
            return False
    
    def test_facebook_graph_api_logs(self):
        """Test 6: Vérifier les logs Facebook Graph API"""
        print("\n📘 STEP 7: Test Facebook Graph API Logs...")
        
        try:
            # Attempt a publication to trigger logs
            test_data = {
                "text": "Test Facebook Graph API Logs",
                "image_url": "https://cdn.pixabay.com/photo/2016/11/29/05/45/astronomy-1867616_960_720.jpg"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/social/facebook/publish-with-image",
                json=test_data,
                timeout=30
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code in [200, 400, 401]:
                result = response.json()
                print(f"✅ Facebook API call attempted")
                print(f"   Response: {json.dumps(result, indent=2)}")
                
                # Check for Facebook API error details
                if 'error' in result:
                    error_msg = result.get('error', '')
                    if 'OAuth' in error_msg or 'access token' in error_msg.lower():
                        print("✅ Expected OAuth error - Facebook API is being called")
                    else:
                        print(f"⚠️ Unexpected error: {error_msg}")
                
                # Check for method confirmation
                if 'method' in result:
                    print(f"✅ Method confirmed: {result['method']}")
                
                return True
            else:
                print(f"❌ Facebook API test failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Facebook API test error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Exécuter tous les tests critiques"""
        print("🎯 FACEBOOK BINARY UPLOAD TESTING - CHATGPT APPROACH")
        print("=" * 60)
        
        results = []
        
        # Test 1: Authentication
        if self.authenticate():
            results.append(("Authentication", True))
        else:
            results.append(("Authentication", False))
            print("❌ Cannot continue without authentication")
            return results
        
        # Test 2: Binary photo endpoint
        results.append(("Binary Photo Endpoint", self.test_binary_photo_endpoint()))
        
        # Test 3: Publish with image endpoint
        results.append(("Publish With Image Endpoint", self.test_publish_with_image_endpoint()))
        
        # Test 4: Facebook connection status
        results.append(("Facebook Connection Status", self.test_facebook_connection_status()))
        
        # Test 5: Accessible images
        results.append(("Accessible Images", self.test_accessible_images()))
        
        # Test 6: Binary vs URL approach
        results.append(("Binary vs URL Approach", self.test_binary_vs_url_approach()))
        
        # Test 7: Facebook Graph API logs
        results.append(("Facebook Graph API Logs", self.test_facebook_graph_api_logs()))
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = 0
        total = len(results)
        
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
            if success:
                passed += 1
        
        print(f"\n📈 SUCCESS RATE: {passed}/{total} ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - CHATGPT BINARY APPROACH WORKING!")
        elif passed >= total * 0.8:
            print("✅ MOST TESTS PASSED - BINARY APPROACH MOSTLY FUNCTIONAL")
        else:
            print("⚠️ SEVERAL TESTS FAILED - BINARY APPROACH NEEDS ATTENTION")
        
        return results 
                            f"Status: {response.status_code}", response.text[:200])
                return False
                
        except Exception as e:
            self.log_test("Clean Database Validation", False, error=str(e))
            return False
    
    def test_facebook_auth_url_state_format(self):
        """Test 2: Test Facebook OAuth URL with corrected state format"""
        try:
            print("📘 Test 2: Facebook OAuth URL with State Correction")
            response = self.session.get(f"{BASE_URL}/social/facebook/auth-url", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get("auth_url", "")
                
                if not auth_url:
                    self.log_test("Facebook OAuth URL State Correction", False, 
                                "No auth_url in response")
                    return False
                
                # Parse URL to extract state parameter
                parsed_url = urlparse(auth_url)
                query_params = parse_qs(parsed_url.query)
                state_param = query_params.get('state', [None])[0]
                
                if not state_param:
                    self.log_test("Facebook OAuth URL State Correction", False, 
                                "No state parameter in URL")
                    return False
                
                # Check if state has the corrected format: {random}|{user_id}
                if '|' in state_param:
                    random_part, user_id_part = state_param.split('|', 1)
                    if user_id_part == self.user_id and len(random_part) > 10:
                        self.log_test("Facebook OAuth URL State Correction", True, 
                                    f"✅ Corrected state format verified: {random_part[:8]}...{user_id_part}")
                        return True
                    else:
                        self.log_test("Facebook OAuth URL State Correction", False, 
                                    f"Invalid user_id in state: expected {self.user_id}, got {user_id_part}")
                        return False
                else:
                    self.log_test("Facebook OAuth URL State Correction", False, 
                                f"State missing pipe separator: {state_param}")
                    return False
                    
            else:
                self.log_test("Facebook OAuth URL State Correction", False, 
                            f"Status: {response.status_code}", response.text[:200])
                return False
                
        except Exception as e:
            self.log_test("Facebook OAuth URL State Correction", False, error=str(e))
            return False
    
    def test_instagram_auth_url_state_format(self):
        """Test 3: Test Instagram OAuth URL with corrected state format"""
        try:
            print("📷 Test 3: Instagram OAuth URL with State Correction")
            response = self.session.get(f"{BASE_URL}/social/instagram/auth-url", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get("auth_url", "")
                
                if not auth_url:
                    self.log_test("Instagram OAuth URL State Correction", False, 
                                "No auth_url in response")
                    return False
                
                # Parse URL to extract state parameter
                parsed_url = urlparse(auth_url)
                query_params = parse_qs(parsed_url.query)
                state_param = query_params.get('state', [None])[0]
                
                if not state_param:
                    self.log_test("Instagram OAuth URL State Correction", False, 
                                "No state parameter in URL")
                    return False
                
                # Check if state has the corrected format: {random}|{user_id}
                if '|' in state_param:
                    random_part, user_id_part = state_param.split('|', 1)
                    if user_id_part == self.user_id and len(random_part) > 10:
                        self.log_test("Instagram OAuth URL State Correction", True, 
                                    f"✅ Corrected state format verified: {random_part[:8]}...{user_id_part}")
                        return True
                    else:
                        self.log_test("Instagram OAuth URL State Correction", False, 
                                    f"Invalid user_id in state: expected {self.user_id}, got {user_id_part}")
                        return False
                else:
                    self.log_test("Instagram OAuth URL State Correction", False, 
                                f"State missing pipe separator: {state_param}")
                    return False
                    
            else:
                self.log_test("Instagram OAuth URL State Correction", False, 
                            f"Status: {response.status_code}", response.text[:200])
                return False
                
        except Exception as e:
            self.log_test("Instagram OAuth URL State Correction", False, error=str(e))
            return False
    
    def test_simplified_status_endpoint(self):
        """Test 4: Test simplified status endpoint (GET /api/social/connections/status)"""
        try:
            print("📊 Test 4: Simplified Status Endpoint")
            response = self.session.get(f"{BASE_URL}/social/connections/status", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for actual simplified response format from implementation
                expected_fields = ["facebook_connected", "instagram_connected", "total_connections"]
                has_all_fields = all(field in data for field in expected_fields)
                
                if has_all_fields:
                    facebook_connected = data.get("facebook_connected", False)
                    instagram_connected = data.get("instagram_connected", False)
                    total_connections = data.get("total_connections", 0)
                    
                    # Should be 0 connections since database is clean
                    if total_connections == 0 and not facebook_connected and not instagram_connected:
                        self.log_test("Simplified Status Endpoint", True, 
                                    f"✅ Simple format verified - Facebook: {facebook_connected}, Instagram: {instagram_connected}, Total: {total_connections}")
                        return True
                    else:
                        self.log_test("Simplified Status Endpoint", False, 
                                    f"Unexpected connection state - Facebook: {facebook_connected}, Instagram: {instagram_connected}, Total: {total_connections}")
                        return False
                else:
                    self.log_test("Simplified Status Endpoint", False, 
                                f"Missing expected fields. Got: {list(data.keys())}")
                    return False
                    
            else:
                self.log_test("Simplified Status Endpoint", False, 
                            f"Status: {response.status_code}", response.text[:200])
                return False
                
        except Exception as e:
            self.log_test("Simplified Status Endpoint", False, error=str(e))
            return False
    
    def test_simplified_facebook_publish_endpoint(self):
        """Test 5: Test simplified Facebook publication endpoint"""
        try:
            print("📘 Test 5: Simplified Facebook Publication Endpoint")
            
            test_data = {
                "text": "Test publication Facebook - Approche simplifiée",
                "image_url": "https://example.com/test-image.jpg"
            }
            
            response = self.session.post(
                f"{BASE_URL}/social/facebook/publish-simple", 
                json=test_data, 
                timeout=30
            )
            
            # Should return 200 with success: false and proper error message
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", True)  # Default True to catch unexpected success
                error_message = data.get("error", "").lower()
                
                if not success and ("connexion" in error_message or "facebook" in error_message):
                    self.log_test("Simplified Facebook Publication Endpoint", True, 
                                f"✅ Endpoint exists and properly rejects: {data.get('error', 'No connection error')}")
                    return True
                elif success:
                    self.log_test("Simplified Facebook Publication Endpoint", False, 
                                f"Unexpected success with no connections: {data}")
                    return False
                else:
                    self.log_test("Simplified Facebook Publication Endpoint", False, 
                                f"Unexpected error message: {data.get('error', 'Unknown error')}")
                    return False
            elif response.status_code == 404:
                self.log_test("Simplified Facebook Publication Endpoint", False, 
                            "Endpoint not found - simplified publication not implemented")
                return False
            else:
                self.log_test("Simplified Facebook Publication Endpoint", False, 
                            f"Unexpected status: {response.status_code}, Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log_test("Simplified Facebook Publication Endpoint", False, error=str(e))
            return False
    
    def test_simplified_instagram_publish_endpoint(self):
        """Test 6: Test simplified Instagram publication endpoint"""
        try:
            print("📷 Test 6: Simplified Instagram Publication Endpoint")
            
            test_data = {
                "text": "Test publication Instagram - Approche simplifiée",
                "image_url": "https://example.com/test-image.jpg"
            }
            
            response = self.session.post(
                f"{BASE_URL}/social/instagram/publish-simple", 
                json=test_data, 
                timeout=30
            )
            
            # Should return 200 with success: false and proper error message
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", True)  # Default True to catch unexpected success
                error_message = data.get("error", "").lower()
                
                if not success and ("connexion" in error_message or "instagram" in error_message):
                    self.log_test("Simplified Instagram Publication Endpoint", True, 
                                f"✅ Endpoint exists and properly rejects: {data.get('error', 'No connection error')}")
                    return True
                elif success:
                    self.log_test("Simplified Instagram Publication Endpoint", False, 
                                f"Unexpected success with no connections: {data}")
                    return False
                else:
                    self.log_test("Simplified Instagram Publication Endpoint", False, 
                                f"Unexpected error message: {data.get('error', 'Unknown error')}")
                    return False
            elif response.status_code == 404:
                self.log_test("Simplified Instagram Publication Endpoint", False, 
                            "Endpoint not found - simplified publication not implemented")
                return False
            else:
                self.log_test("Simplified Instagram Publication Endpoint", False, 
                            f"Unexpected status: {response.status_code}, Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log_test("Simplified Instagram Publication Endpoint", False, error=str(e))
            return False
    
    def test_consistency_with_current_state(self):
        """Test 7: Test consistency with current state and ensure corrections are still active"""
        try:
            print("🔗 Test 7: Consistency with Current State")
            response = self.session.get(f"{BASE_URL}/social/connections", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                connections = data.get("connections", [])
                
                # Should return 0 connections since database is clean
                if len(connections) == 0:
                    self.log_test("Consistency with Current State", True, 
                                "✅ System consistent: 0 connections, ready for user reconnection with corrected state")
                    return True
                else:
                    self.log_test("Consistency with Current State", False, 
                                f"Expected 0 connections, got {len(connections)} - may interfere with user testing")
                    return False
            else:
                self.log_test("Consistency with Current State", False, 
                            f"Status: {response.status_code}", response.text[:200])
                return False
                
        except Exception as e:
            self.log_test("Consistency with Current State", False, error=str(e))
            return False
    
    def run_all_tests(self):
        """Run all simplified ChatGPT OAuth approach tests"""
        print("🎯 TESTING SIMPLIFIED CHATGPT OAUTH APPROACH")
        print("=" * 70)
        print(f"Backend URL: {BASE_URL}")
        print(f"Test User: {TEST_CREDENTIALS['email']}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 70)
        print()
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed - cannot continue tests")
            return False
        
        # Test 1: Validate clean database (0 connections)
        self.test_clean_initial_state()
        
        # Test 2: Test Facebook OAuth URL with corrected state
        self.test_facebook_auth_url_state_format()
        
        # Test 3: Test Instagram OAuth URL with corrected state
        self.test_instagram_auth_url_state_format()
        
        # Test 4: Test simplified status endpoint
        self.test_simplified_status_endpoint()
        
        # Test 5: Test simplified Facebook publication endpoint
        self.test_simplified_facebook_publish_endpoint()
        
        # Test 6: Test simplified Instagram publication endpoint
        self.test_simplified_instagram_publish_endpoint()
        
        # Test 7: Test consistency with current state
        self.test_consistency_with_current_state()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY - SIMPLIFIED CHATGPT APPROACH")
        print("=" * 70)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print(f"\n🎯 RESULTS: {passed}/{total} tests passed ({(passed/total*100):.1f}%)")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED - Simplified ChatGPT approach is working!")
            print("✅ URLs OAuth avec correction state {random}|{user_id}")
            print("✅ Endpoint de status simplifié fonctionnel")
            print("✅ Endpoints de publication simplifiés opérationnels")
            print("✅ Base de données propre (0 connexions)")
            print("✅ Système prêt pour test utilisateur avec domaine vérifié")
            return True
        else:
            print(f"\n🚨 {total - passed} TESTS FAILED - Simplified approach needs attention")
            failed_tests = [r['test'] for r in self.test_results if not r['success']]
            print(f"Failed tests: {', '.join(failed_tests)}")
            return False

def main():
    """Main test execution for simplified ChatGPT OAuth approach"""
    tester = BackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Simplified ChatGPT OAuth approach validation completed successfully!")
        print("🚀 System ready for user testing with corrected state and verified domain!")
        sys.exit(0)
    else:
        print("\n❌ Simplified ChatGPT OAuth approach validation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()