#!/usr/bin/env python3
"""
Backend Testing Suite - Social Connections Facebook Integration
Focus: Validation finale connexions sociales Facebook sur environnement live claire-marcus.com

Test Requirements from French Review Request:
1. Test authentication with lperpere@yahoo.fr / L@Reunion974!
2. Test health check on https://claire-marcus.com/api/health
3. Test GET /api/social/connections endpoint
4. Validate Facebook URLs configuration
5. Test Instagram callback URL
6. Test authorization URL generation

OBJECTIF CRITIQUE: Valider que l'alignement sur environnement live (claire-marcus.com) 
résout définitivement le problème de sauvegarde des connexions Facebook.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration pour environnement live
BASE_URL = "https://claire-marcus.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class FacebookConnectionsTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.user_id = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Claire-Marcus-Backend-Test/1.0'
        })
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_authentication(self):
        """Test 1: Authentification utilisateur avec credentials spécifiés"""
        self.log("🔐 STEP 1: Testing user authentication")
        
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login-robust",
                json=TEST_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token')
                self.user_id = data.get('user_id')
                
                # Configure session with token
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}'
                })
                
                self.log(f"✅ Authentication successful - User ID: {self.user_id}")
                return True
            else:
                self.log(f"❌ Authentication failed - Status: {response.status_code}, Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Authentication error: {str(e)}", "ERROR")
            return False
    
    def test_health_check(self):
        """Test 2: Health check backend sur environnement live"""
        self.log("🏥 STEP 2: Testing backend health check")
        
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                service = data.get('service')
                
                self.log(f"✅ Health check successful - Status: {status}, Service: {service}")
                return True
            else:
                self.log(f"❌ Health check failed - Status: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Health check error: {str(e)}", "ERROR")
            return False
    
    def test_social_connections_endpoint(self):
        """Test 3: Endpoint GET /api/social/connections - vérifier accessibilité"""
        self.log("🔗 STEP 3: Testing social connections endpoint")
        
        try:
            response = self.session.get(f"{self.base_url}/social/connections", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Social connections endpoint accessible - Response: {data}")
                return True
            else:
                self.log(f"❌ Social connections endpoint failed - Status: {response.status_code}, Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Social connections endpoint error: {str(e)}", "ERROR")
            return False
    
    def test_facebook_urls_configuration(self):
        """Test 4: Configuration Facebook URLs - valider alignement sur claire-marcus.com"""
        self.log("🔧 STEP 4: Testing Facebook URLs configuration")
        
        try:
            # Test Instagram auth URL generation
            response = self.session.get(f"{self.base_url}/social/instagram/auth-url", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get('auth_url', '')
                
                # Vérifier que l'URL contient claire-marcus.com
                if 'claire-marcus.com' in auth_url:
                    self.log(f"✅ Facebook URLs correctly configured with claire-marcus.com")
                    self.log(f"   Auth URL: {auth_url[:100]}...")
                    return True
                else:
                    self.log(f"❌ Facebook URLs not aligned with claire-marcus.com - URL: {auth_url}", "ERROR")
                    return False
            else:
                self.log(f"❌ Facebook URL configuration test failed - Status: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Facebook URLs configuration error: {str(e)}", "ERROR")
            return False
    
    def test_instagram_callback_url(self):
        """Test 5: Callback Instagram URL - tester accessibilité sur environnement live"""
        self.log("📞 STEP 5: Testing Instagram callback URL")
        
        try:
            # Test callback endpoint accessibility (without parameters for basic test)
            response = self.session.get(f"{self.base_url}/social/instagram/callback", timeout=10)
            
            # Callback should be accessible (might return error without proper params but should not be 404)
            if response.status_code in [200, 400, 302, 307]:
                self.log(f"✅ Instagram callback URL accessible - Status: {response.status_code}")
                return True
            else:
                self.log(f"❌ Instagram callback URL not accessible - Status: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Instagram callback URL error: {str(e)}", "ERROR")
            return False
    
    def test_authorization_url_generation(self):
        """Test 6: Authorization URL generation - vérifier génération URL d'autorisation Facebook correcte"""
        self.log("🔑 STEP 6: Testing authorization URL generation")
        
        try:
            # Test both Instagram auth endpoints
            endpoints_to_test = [
                "/social/instagram/auth-url",
                "/social/instagram/test-auth"
            ]
            
            success_count = 0
            
            for endpoint in endpoints_to_test:
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        auth_url = data.get('auth_url', data.get('authorization_url', ''))
                        
                        if auth_url:
                            # Vérifier les composants critiques de l'URL
                            url_checks = [
                                ('claire-marcus.com' in auth_url, 'claire-marcus.com domain'),
                                ('client_id=' in auth_url, 'client_id parameter'),
                                ('redirect_uri=' in auth_url, 'redirect_uri parameter'),
                                ('scope=' in auth_url, 'scope parameter')
                            ]
                            
                            all_checks_passed = all(check[0] for check in url_checks)
                            
                            if all_checks_passed:
                                self.log(f"✅ Authorization URL generation working - Endpoint: {endpoint}")
                                success_count += 1
                            else:
                                failed_checks = [check[1] for check in url_checks if not check[0]]
                                self.log(f"⚠️ Authorization URL missing components - Endpoint: {endpoint}, Missing: {failed_checks}")
                        else:
                            self.log(f"⚠️ No authorization URL returned - Endpoint: {endpoint}")
                    else:
                        self.log(f"⚠️ Authorization endpoint failed - Endpoint: {endpoint}, Status: {response.status_code}")
                        
                except Exception as e:
                    self.log(f"⚠️ Authorization endpoint error - Endpoint: {endpoint}, Error: {str(e)}")
            
            if success_count > 0:
                self.log(f"✅ Authorization URL generation working ({success_count}/{len(endpoints_to_test)} endpoints)")
                return True
            else:
                self.log("❌ Authorization URL generation failed on all endpoints", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Authorization URL generation error: {str(e)}", "ERROR")
            return False
    
    def run_all_tests(self):
        """Execute all tests for Facebook connections validation"""
        self.log("🚀 STARTING FACEBOOK CONNECTIONS VALIDATION - ENVIRONNEMENT LIVE")
        self.log(f"   Backend URL: {self.base_url}")
        self.log(f"   Test credentials: {TEST_CREDENTIALS['email']}")
        
        tests = [
            ("Authentication", self.test_authentication),
            ("Health Check", self.test_health_check),
            ("Social Connections Endpoint", self.test_social_connections_endpoint),
            ("Facebook URLs Configuration", self.test_facebook_urls_configuration),
            ("Instagram Callback URL", self.test_instagram_callback_url),
            ("Authorization URL Generation", self.test_authorization_url_generation)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            self.log(f"\n{'='*60}")
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                self.log(f"❌ Test '{test_name}' crashed: {str(e)}", "ERROR")
                results.append((test_name, False))
        
        # Summary
        self.log(f"\n{'='*60}")
        self.log("📊 TEST RESULTS SUMMARY")
        self.log(f"{'='*60}")
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"   {status}: {test_name}")
            if result:
                passed += 1
        
        success_rate = (passed / total) * 100
        self.log(f"\n🎯 SUCCESS RATE: {passed}/{total} tests passed ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            self.log("🎉 FACEBOOK CONNECTIONS VALIDATION: SUCCESSFUL")
        else:
            self.log("🚨 FACEBOOK CONNECTIONS VALIDATION: NEEDS ATTENTION")
        
        return success_rate >= 80

def main():
    """Main test execution"""
    print("Facebook Connections Backend Testing Suite")
    print("=" * 60)
    
    tester = FacebookConnectionsTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()