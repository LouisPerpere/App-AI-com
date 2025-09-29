#!/usr/bin/env python3
"""
Test de la chaîne auth selon plan ChatGPT - Tests 1, 2, 3
French Review Request: Test the 3 endpoints in order to validate robust authentication chain

PLAN CHATGPT ÉTAPES 1-2-3:
1. Test /auth/login-robust with lperpere@yahoo.fr / L@Reunion974! - should return 200 with access_token, no more 502 errors
2. Test /auth/whoami with Bearer token - should return 200 with correct user_id
3. Test /content/pending with Bearer token - should return 200 with 39 files having valid URLs, no more documents with thumb_url null

OBJECTIF: Validate that robust authentication resolves fallback users problem and returns correct documents with valid URLs.
"""

import requests
import json
import time

# Configuration - Using the correct backend URL from frontend/.env
BACKEND_URL = "https://social-pub-hub.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials as specified in review request
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class AuthChainTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()
    
    def test_1_login_robust(self):
        """TEST 1: POST /auth/login-robust - Should return 200 with access_token, no more 502 errors"""
        print("🔑 TEST 1: /auth/login-robust")
        print("=" * 50)
        print(f"Testing with credentials: {TEST_EMAIL} / {TEST_PASSWORD}")
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login-robust", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response Data: {json.dumps(data, indent=2)}")
                
                # Check for required fields
                access_token = data.get("access_token")
                token_type = data.get("token_type")
                user_id = data.get("user_id")
                email = data.get("email")
                
                if access_token and user_id:
                    self.access_token = access_token
                    self.user_id = user_id
                    
                    # Set authorization header for future requests
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.access_token}"
                    })
                    
                    self.log_result(
                        "TEST 1: /auth/login-robust", 
                        True, 
                        f"✅ Login successful! Status: {response.status_code}, Token: {access_token[:20]}..., User ID: {user_id}, Email: {email}, Token Type: {token_type}"
                    )
                    return True
                else:
                    self.log_result(
                        "TEST 1: /auth/login-robust", 
                        False, 
                        f"Missing required fields in response",
                        f"access_token: {bool(access_token)}, user_id: {bool(user_id)}"
                    )
                    return False
            elif response.status_code == 502:
                self.log_result(
                    "TEST 1: /auth/login-robust", 
                    False, 
                    f"❌ 502 ERROR STILL PRESENT - Robust authentication not working!",
                    response.text
                )
                return False
            else:
                self.log_result(
                    "TEST 1: /auth/login-robust", 
                    False, 
                    f"❌ Unexpected status code: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("TEST 1: /auth/login-robust", False, error=str(e))
            return False
    
    def test_2_whoami(self):
        """TEST 2: GET /auth/whoami - Should return 200 with correct user_id"""
        print("👤 TEST 2: /auth/whoami")
        print("=" * 50)
        
        if not self.access_token:
            self.log_result(
                "TEST 2: /auth/whoami", 
                False, 
                "No access token available from TEST 1"
            )
            return False
        
        print(f"Using Bearer token: {self.access_token[:20]}...")
        
        try:
            response = self.session.get(f"{API_BASE}/auth/whoami")
            
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response Data: {json.dumps(data, indent=2)}")
                
                returned_user_id = data.get("user_id")
                authentication_status = data.get("authentication")
                
                if returned_user_id == self.user_id and authentication_status == "success":
                    self.log_result(
                        "TEST 2: /auth/whoami", 
                        True, 
                        f"✅ Authentication chain working! User ID matches: {returned_user_id}, Authentication: {authentication_status}"
                    )
                    return True
                else:
                    self.log_result(
                        "TEST 2: /auth/whoami", 
                        False, 
                        f"❌ User ID mismatch or authentication failed",
                        f"Expected user_id: {self.user_id}, Got: {returned_user_id}, Auth status: {authentication_status}"
                    )
                    return False
            else:
                self.log_result(
                    "TEST 2: /auth/whoami", 
                    False, 
                    f"❌ Unexpected status code: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("TEST 2: /auth/whoami", False, error=str(e))
            return False
    
    def test_3_content_pending(self):
        """TEST 3: GET /content/pending - Should return 200 with 39 files having valid URLs, no more thumb_url null"""
        print("📁 TEST 3: /content/pending")
        print("=" * 50)
        
        if not self.access_token:
            self.log_result(
                "TEST 3: /content/pending", 
                False, 
                "No access token available from TEST 1"
            )
            return False
        
        print(f"Using Bearer token: {self.access_token[:20]}...")
        
        try:
            # Test with higher limit to get all files
            response = self.session.get(f"{API_BASE}/content/pending?limit=100")
            
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                total = data.get("total", 0)
                
                print(f"Total files found: {len(content)}")
                print(f"Total reported: {total}")
                
                # Analyze URLs according to French review requirements
                files_with_valid_urls = 0
                files_with_null_thumb_url = 0
                files_with_valid_thumb_url = 0
                files_with_null_url = 0
                
                url_examples = []
                thumb_url_examples = []
                
                for item in content:
                    url = item.get("url")
                    thumb_url = item.get("thumb_url")
                    filename = item.get("filename", "unknown")
                    
                    # Check main URL
                    if url and url != "":
                        files_with_valid_urls += 1
                        if len(url_examples) < 3:
                            url_examples.append(f"{filename}: {url}")
                    else:
                        files_with_null_url += 1
                    
                    # Check thumb_url
                    if thumb_url and thumb_url != "":
                        files_with_valid_thumb_url += 1
                        if len(thumb_url_examples) < 3:
                            thumb_url_examples.append(f"{filename}: {thumb_url}")
                    else:
                        files_with_null_thumb_url += 1
                
                # Check if we meet the French review objectives
                expected_files = 39
                has_expected_count = len(content) >= expected_files
                no_null_thumb_urls = files_with_null_thumb_url == 0
                all_have_valid_urls = files_with_null_url == 0
                
                details = f"ANALYSE DES FICHIERS: {len(content)} fichiers trouvés (objectif: ≥{expected_files}). "
                details += f"URLs valides: {files_with_valid_urls}/{len(content)}, "
                details += f"thumb_url valides: {files_with_valid_thumb_url}/{len(content)}, "
                details += f"thumb_url null: {files_with_null_thumb_url}. "
                
                if url_examples:
                    details += f"Exemples URLs: {url_examples[:2]}. "
                if thumb_url_examples:
                    details += f"Exemples thumb_url: {thumb_url_examples[:2]}. "
                
                # Determine success based on French review criteria
                success = has_expected_count and no_null_thumb_urls and all_have_valid_urls
                
                if success:
                    details += "✅ OBJECTIF ATTEINT: Authentification robuste résout le problème des fallback users!"
                else:
                    details += f"❌ OBJECTIF NON ATTEINT: "
                    if not has_expected_count:
                        details += f"Pas assez de fichiers ({len(content)}<{expected_files}), "
                    if not no_null_thumb_urls:
                        details += f"Encore {files_with_null_thumb_url} thumb_url null, "
                    if not all_have_valid_urls:
                        details += f"Encore {files_with_null_url} URL null, "
                
                self.log_result(
                    "TEST 3: /content/pending", 
                    success, 
                    details
                )
                
                return success
            else:
                self.log_result(
                    "TEST 3: /content/pending", 
                    False, 
                    f"❌ Unexpected status code: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("TEST 3: /content/pending", False, error=str(e))
            return False
    
    def run_auth_chain_tests(self):
        """Run the 3-step authentication chain test according to ChatGPT plan"""
        print("🚀 TEST DE LA CHAÎNE AUTH SELON PLAN CHATGPT - TESTS 1, 2, 3")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_EMAIL}")
        print("OBJECTIF: Valider que l'authentification robuste résout le problème des fallback users")
        print("et retourne les BONS documents avec URLs valides.")
        print("=" * 70)
        print()
        
        # Run the 3 tests in sequence as specified in French review
        tests = [
            self.test_1_login_robust,
            self.test_2_whoami,
            self.test_3_content_pending
        ]
        
        all_passed = True
        for i, test in enumerate(tests, 1):
            print(f"🔄 Executing Test {i}/3...")
            if not test():
                all_passed = False
                print(f"❌ Test {i} failed, but continuing with remaining tests...")
            else:
                print(f"✅ Test {i} passed!")
            print()
        
        # Summary
        print("📋 RÉSUMÉ DES TESTS - CHAÎNE D'AUTHENTIFICATION")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Detailed results
        for i, result in enumerate(self.test_results, 1):
            print(f"TEST {i}: {result['status']} - {result['test']}")
            if result['details']:
                print(f"   📝 {result['details']}")
            if result['error']:
                print(f"   ❌ Error: {result['error']}")
            print()
        
        # Final verdict according to French review
        print("🎯 VERDICT FINAL SELON DEMANDE FRANÇAISE:")
        print("-" * 50)
        
        if all_passed:
            print("✅ SUCCÈS COMPLET: La chaîne d'authentification robuste fonctionne parfaitement!")
            print("✅ Plus de 502 errors sur /auth/login-robust")
            print("✅ Token Bearer validé correctement par /auth/whoami")
            print("✅ /content/pending retourne les bons documents avec URLs valides")
            print("✅ Problème des fallback users résolu!")
        else:
            print("❌ ÉCHEC: La chaîne d'authentification robuste présente encore des problèmes.")
            print("❌ Voir les détails ci-dessus pour identifier les points à corriger.")
        
        print()
        print("🏁 TEST DE LA CHAÎNE AUTH TERMINÉ")
        
        return all_passed

if __name__ == "__main__":
    tester = AuthChainTester()
    success = tester.run_auth_chain_tests()
    
    if success:
        print("✅ Overall authentication chain testing: SUCCESS")
        exit(0)
    else:
        print("❌ Overall authentication chain testing: FAILED")
        exit(1)