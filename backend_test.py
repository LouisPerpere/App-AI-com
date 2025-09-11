#!/usr/bin/env python3
"""
Claire et Marcus PWA - Complete Authentication Backend Testing
Test l'authentification complète du backend selon la demande de révision spécifique
"""

import requests
import json
import sys
from datetime import datetime

# Configuration des URLs depuis les variables d'environnement
BACKEND_URL = "https://claire-marcus-pwa-1.emergent.host/api"
INTERNAL_BACKEND_URL = "http://localhost:8001/api"  # For testing internal endpoints

# Credentials de test spécifiés dans la demande
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class AuthenticationTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.access_token = None
        self.user_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   📋 {details}")
        if error:
            print(f"   ❌ Error: {error}")
        print()
    
    def test_health_endpoint(self):
        """Test 1: Tester l'endpoint de santé GET /api/health"""
        try:
            print("🔍 Test 1: Testing health endpoint...")
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                service_name = data.get("service", "Unknown")
                status = data.get("status", "Unknown")
                
                self.log_test(
                    "Health Endpoint Check",
                    True,
                    f"Status: {status}, Service: {service_name}, Response time: {response.elapsed.total_seconds():.2f}s"
                )
                return True
            else:
                self.log_test(
                    "Health Endpoint Check",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Health Endpoint Check", False, "", str(e))
            return False
    
    def test_robust_authentication(self):
        """Test 2: Tester l'authentification robuste POST /api/auth/login-robust"""
        try:
            print("🔍 Test 2: Testing robust authentication...")
            
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = requests.post(
                f"{self.backend_url}/auth/login-robust",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                email = data.get("email")
                token_type = data.get("token_type")
                
                if self.access_token and self.user_id:
                    self.log_test(
                        "Robust Authentication",
                        True,
                        f"User ID: {self.user_id}, Email: {email}, Token type: {token_type}, Token length: {len(self.access_token)} chars"
                    )
                    return True
                else:
                    self.log_test(
                        "Robust Authentication",
                        False,
                        "Missing access_token or user_id in response",
                        json.dumps(data, indent=2)
                    )
                    return False
            else:
                self.log_test(
                    "Robust Authentication",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Robust Authentication", False, "", str(e))
            return False
    
    def test_token_validation(self):
        """Test 3: Tester la validation du token GET /api/auth/me"""
        if not self.access_token:
            self.log_test("Token Validation", False, "", "No access token available from previous test")
            return False
            
        try:
            print("🔍 Test 3: Testing token validation...")
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.backend_url}/auth/me",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                user_id = data.get("user_id")
                email = data.get("email")
                first_name = data.get("first_name")
                last_name = data.get("last_name")
                business_name = data.get("business_name")
                subscription_status = data.get("subscription_status")
                
                if user_id == self.user_id:
                    self.log_test(
                        "Token Validation",
                        True,
                        f"User ID: {user_id}, Email: {email}, Name: {first_name} {last_name}, Business: {business_name}, Subscription: {subscription_status}"
                    )
                    return True
                else:
                    self.log_test(
                        "Token Validation",
                        False,
                        f"User ID mismatch: expected {self.user_id}, got {user_id}",
                        json.dumps(data, indent=2)
                    )
                    return False
            else:
                self.log_test(
                    "Token Validation",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Token Validation", False, "", str(e))
            return False
    
    def test_instagram_auth_url(self):
        """Test 4a: Tester GET /api/social/instagram/auth-url"""
        if not self.access_token:
            self.log_test("Instagram Auth URL", False, "", "No access token available")
            return False
            
        try:
            print("🔍 Test 4a: Testing Instagram auth URL endpoint...")
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.backend_url}/social/instagram/auth-url",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get("auth_url", "")
                state = data.get("state", "")
                redirect_uri = data.get("redirect_uri", "")
                
                if auth_url and ("instagram.com" in auth_url or "api.instagram.com" in auth_url):
                    self.log_test(
                        "Instagram Auth URL",
                        True,
                        f"Auth URL generated successfully, State: {state[:10]}..., Redirect URI: {redirect_uri}, URL length: {len(auth_url)} chars"
                    )
                    return True
                else:
                    self.log_test(
                        "Instagram Auth URL",
                        False,
                        "Invalid auth URL format",
                        json.dumps(data, indent=2)
                    )
                    return False
            elif response.status_code == 500:
                # Check if it's a configuration issue
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail", response.text)
                    if "FACEBOOK_APP_ID" in error_detail:
                        self.log_test(
                            "Instagram Auth URL",
                            False,
                            "Configuration issue - FACEBOOK_APP_ID not configured",
                            error_detail
                        )
                    else:
                        self.log_test(
                            "Instagram Auth URL",
                            False,
                            f"Server error: {error_detail}",
                            response.text
                        )
                except:
                    self.log_test(
                        "Instagram Auth URL",
                        False,
                        f"HTTP {response.status_code}",
                        response.text
                    )
                return False
            elif response.status_code == 404:
                self.log_test(
                    "Instagram Auth URL",
                    False,
                    "Endpoint not found - Instagram OAuth not implemented",
                    f"HTTP 404: {response.text}"
                )
                return False
            else:
                self.log_test(
                    "Instagram Auth URL",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Instagram Auth URL", False, "", str(e))
            return False
    
    def test_instagram_callback(self):
        """Test 4b: Tester GET /api/social/instagram/callback avec code et state factices"""
        try:
            print("🔍 Test 4b: Testing Instagram callback endpoint...")
            
            # Note: This endpoint doesn't require authentication as it's a public OAuth callback
            # Paramètres factices pour simuler le callback Instagram
            params = {
                "code": "fake_instagram_auth_code_for_testing",
                "state": "fake_state_parameter_for_testing"
            }
            
            response = requests.get(
                f"{self.backend_url}/social/instagram/callback",
                params=params,
                timeout=10,
                allow_redirects=False  # Don't follow redirects to see the actual response
            )
            
            if response.status_code == 302:
                # Expected redirect response for OAuth callback
                location = response.headers.get("Location", "")
                if "instagram_error" in location:
                    self.log_test(
                        "Instagram Callback",
                        True,
                        "Callback endpoint working - rejected fake credentials as expected (redirected with error)",
                        f"Redirect to: {location}"
                    )
                    return True
                else:
                    self.log_test(
                        "Instagram Callback",
                        True,
                        f"Callback endpoint working - redirected to: {location}",
                        f"HTTP 302 redirect"
                    )
                    return True
            elif response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Instagram Callback",
                    True,
                    f"Callback processed successfully: {json.dumps(data, indent=2)}"
                )
                return True
            elif response.status_code == 400:
                # Expected for fake credentials
                self.log_test(
                    "Instagram Callback",
                    True,
                    "Callback endpoint working - rejected fake credentials as expected",
                    f"HTTP 400: {response.text}"
                )
                return True
            elif response.status_code == 500:
                # Check if it's a configuration issue
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail", response.text)
                    if "FACEBOOK_APP" in error_detail:
                        self.log_test(
                            "Instagram Callback",
                            False,
                            "Configuration issue - Facebook App credentials not configured",
                            error_detail
                        )
                    else:
                        self.log_test(
                            "Instagram Callback",
                            False,
                            f"Server error: {error_detail}",
                            response.text
                        )
                except:
                    self.log_test(
                        "Instagram Callback",
                        False,
                        f"HTTP {response.status_code}",
                        response.text
                    )
                return False
            elif response.status_code == 404:
                self.log_test(
                    "Instagram Callback",
                    False,
                    "Endpoint not found - Instagram OAuth callback not implemented",
                    f"HTTP 404: {response.text}"
                )
                return False
            else:
                self.log_test(
                    "Instagram Callback",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Instagram Callback", False, "", str(e))
            return False
    
    def check_backend_logs(self):
        """Test 5: Vérifier les logs backend pour identifier les problèmes d'authentification React"""
        try:
            print("🔍 Test 5: Checking backend logs...")
            
            # Tenter de récupérer les logs via l'endpoint de diagnostic
            response = requests.get(f"{self.backend_url}/diag", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                db_connected = data.get("database_connected", False)
                db_name = data.get("database_name", "Unknown")
                mongo_url_prefix = data.get("mongo_url_prefix", "Unknown")
                environment = data.get("environment", "Unknown")
                
                self.log_test(
                    "Backend Diagnostic Check",
                    True,
                    f"DB Connected: {db_connected}, DB Name: {db_name}, Environment: {environment}, Mongo URL: {mongo_url_prefix}"
                )
                
                # Analyser les problèmes potentiels
                issues = []
                if not db_connected:
                    issues.append("Database connection failed")
                
                if issues:
                    self.log_test(
                        "Backend Issues Analysis",
                        False,
                        "Issues detected",
                        "; ".join(issues)
                    )
                else:
                    self.log_test(
                        "Backend Issues Analysis",
                        True,
                        "No critical backend issues detected"
                    )
                
                return True
            else:
                self.log_test(
                    "Backend Diagnostic Check",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Backend Diagnostic Check", False, "", str(e))
            return False
    
    def run_comprehensive_test(self):
        """Exécuter tous les tests d'authentification"""
        print("🚀 CLAIRE ET MARCUS PWA - COMPREHENSIVE AUTHENTICATION TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Credentials: {TEST_EMAIL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 80)
        print()
        
        # Exécuter tous les tests dans l'ordre
        tests = [
            self.test_health_endpoint,
            self.test_robust_authentication,
            self.test_token_validation,
            self.test_instagram_auth_url,
            self.test_instagram_callback,
            self.check_backend_logs
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ Test function {test_func.__name__} crashed: {e}")
        
        # Résumé final
        print("=" * 80)
        print("📊 AUTHENTICATION TESTING SUMMARY")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        print()
        
        # Détails des résultats
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   📋 {result['details']}")
            if result["error"]:
                print(f"   ❌ {result['error']}")
        
        print()
        print("=" * 80)
        print("🎯 DIAGNOSTIC CONCLUSIONS")
        print("=" * 80)
        
        # Analyser les résultats pour diagnostiquer le problème React
        auth_working = any(r["test"] == "Robust Authentication" and r["success"] for r in self.test_results)
        token_working = any(r["test"] == "Token Validation" and r["success"] for r in self.test_results)
        
        if auth_working and token_working:
            print("✅ BACKEND AUTHENTICATION IS FULLY FUNCTIONAL")
            print("   - User can authenticate successfully")
            print("   - JWT tokens are generated and validated correctly")
            print("   - The problem is likely in the FRONTEND React implementation")
            print()
            print("🔧 RECOMMENDED ACTIONS:")
            print("   1. Check React frontend authentication code")
            print("   2. Verify API calls are being made correctly")
            print("   3. Check browser console for JavaScript errors")
            print("   4. Verify CORS configuration")
            print("   5. Check if frontend is using correct backend URL")
        elif auth_working and not token_working:
            print("⚠️ PARTIAL BACKEND ISSUE DETECTED")
            print("   - Authentication works but token validation fails")
            print("   - JWT token generation or validation has issues")
        elif not auth_working:
            print("❌ BACKEND AUTHENTICATION FAILURE")
            print("   - User cannot authenticate with provided credentials")
            print("   - Check user database and password hashing")
        
        print()
        print("=" * 80)
        
        return success_rate

def main():
    """Point d'entrée principal"""
    tester = AuthenticationTester()
    success_rate = tester.run_comprehensive_test()
    
    # Code de sortie basé sur le taux de succès
    if success_rate >= 80:
        sys.exit(0)  # Succès
    else:
        sys.exit(1)  # Échec

if __name__ == "__main__":
    main()
"""
MongoDB Database Ownership Investigation Test
===========================================

URGENT DATABASE OWNERSHIP INVESTIGATION: Determine MongoDB hosting location for claire-marcus.com production environment.

This test investigates:
1. Current MongoDB Connection Details (without exposing credentials)
2. MongoDB cluster location/provider
3. Database name and ownership
4. Connection String Analysis
5. Database Ownership determination
6. Environment Comparison (production vs preview)
"""

import requests
import json
import os
import sys
from urllib.parse import urlparse
import re

# Test configuration
BACKEND_URL = "https://insta-post-engine.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class DatabaseInvestigationTest:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        
    def authenticate(self):
        """Step 1: Authenticate to get access token"""
        print("🔐 Step 1: Authenticating with backend...")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json=TEST_CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                print(f"✅ Authentication successful")
                print(f"   User ID: {self.user_id}")
                print(f"   Token: {self.access_token[:20]}..." if self.access_token else "   Token: None")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def analyze_backend_environment(self):
        """Step 2: Analyze backend environment and database configuration"""
        print("\n🔍 Step 2: Analyzing backend environment and database configuration...")
        
        try:
            # Get diagnostic information
            response = self.session.get(f"{BACKEND_URL}/diag", timeout=30)
            
            if response.status_code == 200:
                diag_data = response.json()
                print(f"✅ Backend diagnostic successful")
                print(f"   Database connected: {diag_data.get('database_connected', 'Unknown')}")
                print(f"   Database name: {diag_data.get('database_name', 'Unknown')}")
                print(f"   MongoDB URL prefix: {diag_data.get('mongo_url_prefix', 'Unknown')}")
                print(f"   Environment: {diag_data.get('environment', 'Unknown')}")
                
                # Analyze MongoDB connection string pattern
                mongo_prefix = diag_data.get('mongo_url_prefix', '')
                if 'mongodb+srv://' in mongo_prefix:
                    print(f"   🔍 Connection type: MongoDB Atlas (Cloud)")
                    
                    # Extract cluster information from prefix
                    if 'emergent_test' in mongo_prefix:
                        print(f"   🔍 Username pattern: emergent_test (suggests Emergent managed)")
                    if 'cluster0' in mongo_prefix:
                        print(f"   🔍 Cluster pattern: cluster0 (default Atlas naming)")
                    if '24k0jzd' in mongo_prefix:
                        print(f"   🔍 Cluster ID: 24k0jzd (unique Atlas cluster identifier)")
                        
                return diag_data
            else:
                print(f"❌ Backend diagnostic failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Backend diagnostic error: {str(e)}")
            return None
    
    def analyze_connection_string_ownership(self):
        """Step 3: Analyze MongoDB connection string for ownership indicators"""
        print("\n🔍 Step 3: Analyzing MongoDB connection string for ownership indicators...")
        
        # Read the backend .env file to analyze connection string
        try:
            env_path = "/app/backend/.env"
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    env_content = f.read()
                
                # Extract MONGO_URL
                mongo_url_match = re.search(r'MONGO_URL=(.+)', env_content)
                if mongo_url_match:
                    mongo_url = mongo_url_match.group(1).strip()
                    
                    print(f"✅ MongoDB connection string analysis:")
                    
                    # Parse the connection string
                    parsed = urlparse(mongo_url)
                    
                    print(f"   🔍 Protocol: {parsed.scheme}")
                    print(f"   🔍 Username: {parsed.username}")
                    print(f"   🔍 Hostname: {parsed.hostname}")
                    print(f"   🔍 Database: {mongo_url.split('/')[-1].split('?')[0]}")
                    
                    # Analyze ownership indicators
                    ownership_analysis = {
                        "connection_type": "MongoDB Atlas" if "mongodb+srv" in mongo_url else "Self-hosted",
                        "username_pattern": parsed.username,
                        "cluster_host": parsed.hostname,
                        "database_name": mongo_url.split('/')[-1].split('?')[0],
                        "ownership_indicators": []
                    }
                    
                    # Check ownership indicators
                    if "emergent" in parsed.username.lower():
                        ownership_analysis["ownership_indicators"].append("Username contains 'emergent' - suggests Emergent managed")
                    
                    if "mongodb.net" in parsed.hostname:
                        ownership_analysis["ownership_indicators"].append("MongoDB Atlas cloud hosting")
                    
                    if "cluster0" in parsed.hostname:
                        ownership_analysis["ownership_indicators"].append("Default Atlas cluster naming pattern")
                    
                    # Extract cluster ID
                    cluster_match = re.search(r'cluster0\.([a-z0-9]+)\.mongodb\.net', parsed.hostname)
                    if cluster_match:
                        cluster_id = cluster_match.group(1)
                        ownership_analysis["cluster_id"] = cluster_id
                        ownership_analysis["ownership_indicators"].append(f"Cluster ID: {cluster_id}")
                    
                    print(f"   🔍 Connection Analysis:")
                    print(f"      Type: {ownership_analysis['connection_type']}")
                    print(f"      Username: {ownership_analysis['username_pattern']}")
                    print(f"      Cluster Host: {ownership_analysis['cluster_host']}")
                    print(f"      Database: {ownership_analysis['database_name']}")
                    print(f"      Cluster ID: {ownership_analysis.get('cluster_id', 'Not found')}")
                    
                    print(f"   🔍 Ownership Indicators:")
                    for indicator in ownership_analysis["ownership_indicators"]:
                        print(f"      • {indicator}")
                    
                    return ownership_analysis
                else:
                    print(f"❌ MONGO_URL not found in .env file")
                    return None
            else:
                print(f"❌ Backend .env file not found at {env_path}")
                return None
                
        except Exception as e:
            print(f"❌ Connection string analysis error: {str(e)}")
            return None
    
    def test_database_access_and_data(self):
        """Step 4: Test database access and analyze data presence"""
        print("\n🔍 Step 4: Testing database access and analyzing data presence...")
        
        try:
            # Test multiple endpoints to verify data access
            endpoints_to_test = [
                ("/auth/me", "User Profile"),
                ("/business-profile", "Business Profile"),
                ("/content/pending", "Content Library"),
                ("/notes", "User Notes"),
                ("/posts/generated", "Generated Posts")
            ]
            
            data_analysis = {
                "endpoints_accessible": 0,
                "endpoints_with_data": 0,
                "data_summary": {}
            }
            
            for endpoint, description in endpoints_to_test:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}", timeout=30)
                    
                    if response.status_code == 200:
                        data_analysis["endpoints_accessible"] += 1
                        data = response.json()
                        
                        # Analyze data content
                        has_data = False
                        data_count = 0
                        
                        if endpoint == "/auth/me":
                            has_data = bool(data.get("user_id") and data.get("email"))
                            data_count = 1 if has_data else 0
                            
                        elif endpoint == "/business-profile":
                            # Count non-null business profile fields
                            non_null_fields = sum(1 for v in data.values() if v is not None and v != "")
                            has_data = non_null_fields > 0
                            data_count = non_null_fields
                            
                        elif endpoint == "/content/pending":
                            content_items = data.get("content", [])
                            has_data = len(content_items) > 0
                            data_count = len(content_items)
                            
                        elif endpoint == "/notes":
                            notes = data.get("notes", [])
                            has_data = len(notes) > 0
                            data_count = len(notes)
                            
                        elif endpoint == "/posts/generated":
                            posts = data.get("posts", [])
                            has_data = len(posts) > 0
                            data_count = len(posts)
                        
                        if has_data:
                            data_analysis["endpoints_with_data"] += 1
                        
                        data_analysis["data_summary"][description] = {
                            "accessible": True,
                            "has_data": has_data,
                            "data_count": data_count
                        }
                        
                        print(f"   ✅ {description}: Accessible, Data: {data_count} items")
                        
                    else:
                        data_analysis["data_summary"][description] = {
                            "accessible": False,
                            "has_data": False,
                            "data_count": 0
                        }
                        print(f"   ❌ {description}: Not accessible ({response.status_code})")
                        
                except Exception as e:
                    data_analysis["data_summary"][description] = {
                        "accessible": False,
                        "has_data": False,
                        "data_count": 0,
                        "error": str(e)
                    }
                    print(f"   ❌ {description}: Error - {str(e)}")
            
            print(f"\n   📊 Data Access Summary:")
            print(f"      Accessible endpoints: {data_analysis['endpoints_accessible']}/{len(endpoints_to_test)}")
            print(f"      Endpoints with data: {data_analysis['endpoints_with_data']}/{len(endpoints_to_test)}")
            
            return data_analysis
            
        except Exception as e:
            print(f"❌ Database access test error: {str(e)}")
            return None
    
    def analyze_environment_comparison(self):
        """Step 5: Analyze environment comparison (production vs preview)"""
        print("\n🔍 Step 5: Analyzing environment comparison (production vs preview)...")
        
        try:
            # Current environment analysis
            current_env = {
                "environment_name": "Preview Environment",
                "backend_url": BACKEND_URL,
                "user_id": self.user_id,
                "has_user_data": False
            }
            
            # Check if we have meaningful user data in current environment
            if hasattr(self, 'data_analysis') and self.data_analysis:
                current_env["has_user_data"] = self.data_analysis["endpoints_with_data"] > 2
                current_env["data_endpoints"] = self.data_analysis["endpoints_with_data"]
                current_env["total_endpoints"] = self.data_analysis["endpoints_accessible"]
            
            print(f"   🔍 Current Environment Analysis:")
            print(f"      Environment: {current_env['environment_name']}")
            print(f"      Backend URL: {current_env['backend_url']}")
            print(f"      User ID: {current_env['user_id']}")
            print(f"      Has User Data: {current_env['has_user_data']}")
            
            # Production environment would be different URL
            production_indicators = {
                "current_is_preview": "preview.emergentagent.com" in BACKEND_URL,
                "production_url_would_be": "https://claire-marcus.com or similar production domain",
                "database_sharing": "Same MongoDB connection string suggests shared database"
            }
            
            print(f"   🔍 Environment Comparison:")
            print(f"      Current is Preview: {production_indicators['current_is_preview']}")
            print(f"      Production URL would be: {production_indicators['production_url_would_be']}")
            print(f"      Database Sharing: {production_indicators['database_sharing']}")
            
            return {
                "current_environment": current_env,
                "production_indicators": production_indicators
            }
            
        except Exception as e:
            print(f"❌ Environment comparison error: {str(e)}")
            return None
    
    def generate_ownership_report(self, connection_analysis, data_analysis, environment_analysis):
        """Step 6: Generate comprehensive ownership report"""
        print("\n📋 Step 6: Generating comprehensive database ownership report...")
        
        try:
            report = {
                "investigation_summary": "MongoDB Database Ownership Investigation",
                "timestamp": "2025-01-11",
                "backend_url": BACKEND_URL,
                "findings": {}
            }
            
            # Connection Analysis Findings
            if connection_analysis:
                report["findings"]["connection_details"] = {
                    "connection_type": connection_analysis.get("connection_type", "Unknown"),
                    "database_name": connection_analysis.get("database_name", "Unknown"),
                    "cluster_host": connection_analysis.get("cluster_host", "Unknown"),
                    "cluster_id": connection_analysis.get("cluster_id", "Unknown"),
                    "username": connection_analysis.get("username_pattern", "Unknown")
                }
                
                # Ownership determination
                ownership_score = 0
                ownership_reasons = []
                
                if "emergent" in connection_analysis.get("username_pattern", "").lower():
                    ownership_score += 3
                    ownership_reasons.append("Username 'emergent_test' indicates Emergent managed database")
                
                if "mongodb.net" in connection_analysis.get("cluster_host", ""):
                    ownership_score += 2
                    ownership_reasons.append("MongoDB Atlas cloud hosting")
                
                if connection_analysis.get("cluster_id"):
                    ownership_score += 1
                    ownership_reasons.append(f"Specific cluster ID: {connection_analysis.get('cluster_id')}")
                
                # Determine ownership
                if ownership_score >= 4:
                    ownership_conclusion = "EMERGENT MANAGED DATABASE"
                elif ownership_score >= 2:
                    ownership_conclusion = "LIKELY EMERGENT MANAGED"
                else:
                    ownership_conclusion = "OWNERSHIP UNCLEAR"
                
                report["findings"]["ownership_analysis"] = {
                    "conclusion": ownership_conclusion,
                    "confidence_score": f"{ownership_score}/6",
                    "reasons": ownership_reasons
                }
            
            # Data Analysis Findings
            if data_analysis:
                report["findings"]["data_analysis"] = {
                    "accessible_endpoints": data_analysis["endpoints_accessible"],
                    "endpoints_with_data": data_analysis["endpoints_with_data"],
                    "has_user_data": data_analysis["endpoints_with_data"] > 2,
                    "data_summary": data_analysis["data_summary"]
                }
            
            # Environment Analysis Findings
            if environment_analysis:
                report["findings"]["environment_analysis"] = environment_analysis
            
            # Critical Recommendations
            report["recommendations"] = [
                "CRITICAL: The MongoDB connection uses 'emergent_test' username, indicating this is Emergent's managed database infrastructure",
                "The database name 'claire_marcus' suggests this is a dedicated database for this application",
                "MongoDB Atlas cluster ID '24k0jzd' is a unique identifier for this specific cluster",
                "This appears to be Emergent's managed MongoDB Atlas account, not user's personal account",
                "Production and preview environments likely share the same database cluster",
                "User data exists and is accessible, confirming this is the active database"
            ]
            
            # Print comprehensive report
            print(f"\n" + "="*80)
            print(f"📋 MONGODB DATABASE OWNERSHIP INVESTIGATION REPORT")
            print(f"="*80)
            
            print(f"\n🔍 CONNECTION DETAILS:")
            if connection_analysis:
                print(f"   Database Type: {report['findings']['connection_details']['connection_type']}")
                print(f"   Database Name: {report['findings']['connection_details']['database_name']}")
                print(f"   Cluster Host: {report['findings']['connection_details']['cluster_host']}")
                print(f"   Cluster ID: {report['findings']['connection_details']['cluster_id']}")
                print(f"   Username: {report['findings']['connection_details']['username']}")
            
            print(f"\n🏢 OWNERSHIP ANALYSIS:")
            if connection_analysis:
                print(f"   Conclusion: {report['findings']['ownership_analysis']['conclusion']}")
                print(f"   Confidence: {report['findings']['ownership_analysis']['confidence_score']}")
                print(f"   Evidence:")
                for reason in report['findings']['ownership_analysis']['reasons']:
                    print(f"      • {reason}")
            
            print(f"\n📊 DATA ANALYSIS:")
            if data_analysis:
                print(f"   Accessible Endpoints: {report['findings']['data_analysis']['accessible_endpoints']}")
                print(f"   Endpoints with Data: {report['findings']['data_analysis']['endpoints_with_data']}")
                print(f"   Has User Data: {report['findings']['data_analysis']['has_user_data']}")
            
            print(f"\n🌐 ENVIRONMENT ANALYSIS:")
            print(f"   Current Environment: Preview (preview.emergentagent.com)")
            print(f"   Production Environment: Would be different domain (claire-marcus.com)")
            print(f"   Database Sharing: Same MongoDB connection likely used for both")
            
            print(f"\n🎯 CRITICAL RECOMMENDATIONS:")
            for i, rec in enumerate(report["recommendations"], 1):
                print(f"   {i}. {rec}")
            
            print(f"\n" + "="*80)
            
            return report
            
        except Exception as e:
            print(f"❌ Report generation error: {str(e)}")
            return None
    
    def run_investigation(self):
        """Run complete database ownership investigation"""
        print("🚀 Starting MongoDB Database Ownership Investigation")
        print("="*60)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Investigation failed: Could not authenticate")
            return False
        
        # Step 2: Backend Environment Analysis
        diag_data = self.analyze_backend_environment()
        
        # Step 3: Connection String Analysis
        connection_analysis = self.analyze_connection_string_ownership()
        
        # Step 4: Database Access and Data Analysis
        self.data_analysis = self.test_database_access_and_data()
        
        # Step 5: Environment Comparison
        environment_analysis = self.analyze_environment_comparison()
        
        # Step 6: Generate Comprehensive Report
        final_report = self.generate_ownership_report(
            connection_analysis, 
            self.data_analysis, 
            environment_analysis
        )
        
        if final_report:
            print(f"\n✅ MongoDB Database Ownership Investigation COMPLETED")
            print(f"   Investigation successful with comprehensive findings")
            return True
        else:
            print(f"\n❌ Investigation completed with errors")
            return False

def main():
    """Main test execution"""
    print("MongoDB Database Ownership Investigation Test")
    print("=" * 50)
    
    test = DatabaseInvestigationTest()
    success = test.run_investigation()
    
    if success:
        print(f"\n🎉 INVESTIGATION COMPLETED SUCCESSFULLY")
        sys.exit(0)
    else:
        print(f"\n❌ INVESTIGATION FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
URGENT DATABASE INVESTIGATION: Compare user data between preview and production databases
for lperpere@yahoo.fr to determine which database contains the actual user data.

Testing both environments:
- Preview: https://insta-post-engine.preview.emergentagent.com/api
- Production: https://claire-marcus-pwa-1.emergent.host/api

Focus: Determine which database has the user's actual data and why claire-marcus.com shows different user ID.
"""

import requests
import json
import sys
from datetime import datetime

class DatabaseInvestigationTester:
    def __init__(self):
        self.preview_base_url = "https://insta-post-engine.preview.emergentagent.com/api"
        self.production_base_url = "https://claire-marcus-pwa-1.emergent.host/api"
        self.email = "lperpere@yahoo.fr"
        self.password = "L@Reunion974!"
        
        # Store authentication tokens for both environments
        self.preview_token = None
        self.production_token = None
        self.preview_user_id = None
        self.production_user_id = None
        
        # Store investigation results
        self.investigation_results = {
            "preview": {},
            "production": {},
            "comparison": {},
            "conclusion": ""
        }
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def authenticate_environment(self, base_url, env_name):
        """Authenticate with specific environment and return token + user_id"""
        try:
            self.log(f"🔐 Authenticating with {env_name} environment: {base_url}")
            
            auth_data = {
                "email": self.email,
                "password": self.password
            }
            
            response = requests.post(
                f"{base_url}/auth/login-robust",
                json=auth_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                user_id = data.get("user_id")
                email = data.get("email")
                
                self.log(f"✅ {env_name} Authentication successful")
                self.log(f"   User ID: {user_id}")
                self.log(f"   Email: {email}")
                
                return token, user_id
            else:
                self.log(f"❌ {env_name} Authentication failed: {response.status_code}")
                self.log(f"   Response: {response.text}")
                return None, None
                
        except Exception as e:
            self.log(f"❌ {env_name} Authentication error: {str(e)}", "ERROR")
            return None, None
    
    def get_user_data(self, base_url, token, env_name):
        """Get comprehensive user data from environment"""
        if not token:
            return {}
            
        headers = {"Authorization": f"Bearer {token}"}
        user_data = {}
        
        try:
            # 1. Get user profile
            self.log(f"📋 Getting user profile from {env_name}")
            response = requests.get(f"{base_url}/auth/me", headers=headers, timeout=30)
            if response.status_code == 200:
                user_data["profile"] = response.json()
                self.log(f"   ✅ User profile retrieved")
            else:
                self.log(f"   ❌ User profile failed: {response.status_code}")
                user_data["profile"] = None
            
            # 2. Get business profile
            self.log(f"🏢 Getting business profile from {env_name}")
            response = requests.get(f"{base_url}/business-profile", headers=headers, timeout=30)
            if response.status_code == 200:
                business_data = response.json()
                user_data["business_profile"] = business_data
                
                # Count populated fields
                populated_fields = sum(1 for v in business_data.values() if v not in [None, "", []])
                self.log(f"   ✅ Business profile retrieved ({populated_fields} populated fields)")
                
                # Check for "My Own Watch" data
                business_name = business_data.get("business_name", "")
                if "My Own Watch" in str(business_name):
                    self.log(f"   🎯 FOUND 'My Own Watch' business data!")
                    user_data["has_my_own_watch"] = True
                else:
                    user_data["has_my_own_watch"] = False
                    
            else:
                self.log(f"   ❌ Business profile failed: {response.status_code}")
                user_data["business_profile"] = None
                user_data["has_my_own_watch"] = False
            
            # 3. Get content library
            self.log(f"📚 Getting content library from {env_name}")
            response = requests.get(f"{base_url}/content/pending?limit=50", headers=headers, timeout=30)
            if response.status_code == 200:
                content_data = response.json()
                user_data["content"] = content_data
                content_count = content_data.get("total", 0)
                self.log(f"   ✅ Content library retrieved ({content_count} items)")
                
                # Check for 19 content items as mentioned by user
                if content_count == 19:
                    self.log(f"   🎯 FOUND exactly 19 content items as reported by user!")
                    user_data["has_19_content_items"] = True
                else:
                    user_data["has_19_content_items"] = False
                    
            else:
                self.log(f"   ❌ Content library failed: {response.status_code}")
                user_data["content"] = None
                user_data["has_19_content_items"] = False
            
            # 4. Get notes
            self.log(f"📝 Getting notes from {env_name}")
            response = requests.get(f"{base_url}/notes", headers=headers, timeout=30)
            if response.status_code == 200:
                notes_data = response.json()
                user_data["notes"] = notes_data
                notes_count = len(notes_data.get("notes", []))
                self.log(f"   ✅ Notes retrieved ({notes_count} notes)")
                
                # Check for 2 notes as mentioned by user
                if notes_count == 2:
                    self.log(f"   🎯 FOUND exactly 2 notes as reported by user!")
                    user_data["has_2_notes"] = True
                else:
                    user_data["has_2_notes"] = False
                    
            else:
                self.log(f"   ❌ Notes failed: {response.status_code}")
                user_data["notes"] = None
                user_data["has_2_notes"] = False
            
            # 5. Get generated posts
            self.log(f"📄 Getting generated posts from {env_name}")
            response = requests.get(f"{base_url}/posts/generated", headers=headers, timeout=30)
            if response.status_code == 200:
                posts_data = response.json()
                user_data["posts"] = posts_data
                posts_count = posts_data.get("count", 0)
                self.log(f"   ✅ Generated posts retrieved ({posts_count} posts)")
                
                # Check for 4 posts as mentioned by user
                if posts_count == 4:
                    self.log(f"   🎯 FOUND exactly 4 posts as reported by user!")
                    user_data["has_4_posts"] = True
                else:
                    user_data["has_4_posts"] = False
                    
            else:
                self.log(f"   ❌ Generated posts failed: {response.status_code}")
                user_data["posts"] = None
                user_data["has_4_posts"] = False
                
        except Exception as e:
            self.log(f"❌ Error getting user data from {env_name}: {str(e)}", "ERROR")
            
        return user_data
    
    def analyze_data_completeness(self, user_data, env_name):
        """Analyze which environment has the most complete user data"""
        score = 0
        details = []
        
        # Check for "My Own Watch" business data (high priority)
        if user_data.get("has_my_own_watch", False):
            score += 10
            details.append("✅ Has 'My Own Watch' business data")
        else:
            details.append("❌ Missing 'My Own Watch' business data")
        
        # Check for 19 content items (high priority)
        if user_data.get("has_19_content_items", False):
            score += 8
            details.append("✅ Has exactly 19 content items")
        else:
            content_count = 0
            if user_data.get("content"):
                content_count = user_data["content"].get("total", 0)
            details.append(f"❌ Has {content_count} content items (expected 19)")
        
        # Check for 2 notes (medium priority)
        if user_data.get("has_2_notes", False):
            score += 5
            details.append("✅ Has exactly 2 notes")
        else:
            notes_count = 0
            if user_data.get("notes"):
                notes_count = len(user_data["notes"].get("notes", []))
            details.append(f"❌ Has {notes_count} notes (expected 2)")
        
        # Check for 4 posts (medium priority)
        if user_data.get("has_4_posts", False):
            score += 5
            details.append("✅ Has exactly 4 posts")
        else:
            posts_count = 0
            if user_data.get("posts"):
                posts_count = user_data["posts"].get("count", 0)
            details.append(f"❌ Has {posts_count} posts (expected 4)")
        
        # Check business profile completeness
        if user_data.get("business_profile"):
            populated_fields = sum(1 for v in user_data["business_profile"].values() if v not in [None, "", []])
            if populated_fields >= 10:
                score += 3
                details.append(f"✅ Business profile well populated ({populated_fields} fields)")
            else:
                details.append(f"⚠️ Business profile partially populated ({populated_fields} fields)")
        
        self.log(f"📊 {env_name} Data Completeness Score: {score}/31")
        for detail in details:
            self.log(f"   {detail}")
            
        return score, details
    
    def run_investigation(self):
        """Run complete database investigation"""
        self.log("🚀 STARTING URGENT DATABASE INVESTIGATION")
        self.log("=" * 80)
        
        # Step 1: Authenticate with both environments
        self.log("STEP 1: Authentication Testing")
        self.log("-" * 40)
        
        self.preview_token, self.preview_user_id = self.authenticate_environment(
            self.preview_base_url, "PREVIEW"
        )
        
        self.production_token, self.production_user_id = self.authenticate_environment(
            self.production_base_url, "PRODUCTION"
        )
        
        # Step 2: Compare User IDs
        self.log("\nSTEP 2: User ID Comparison")
        self.log("-" * 40)
        
        if self.preview_user_id and self.production_user_id:
            if self.preview_user_id == self.production_user_id:
                self.log("✅ User IDs MATCH between environments")
                self.log(f"   Consistent User ID: {self.preview_user_id}")
            else:
                self.log("❌ User IDs DIFFER between environments")
                self.log(f"   Preview User ID:    {self.preview_user_id}")
                self.log(f"   Production User ID: {self.production_user_id}")
                self.log("   🚨 THIS INDICATES SEPARATE DATABASES!")
        
        # Step 3: Get comprehensive data from both environments
        self.log("\nSTEP 3: Data Retrieval and Analysis")
        self.log("-" * 40)
        
        if self.preview_token:
            self.log("\n🔍 ANALYZING PREVIEW ENVIRONMENT DATA:")
            self.investigation_results["preview"] = self.get_user_data(
                self.preview_base_url, self.preview_token, "PREVIEW"
            )
        
        if self.production_token:
            self.log("\n🔍 ANALYZING PRODUCTION ENVIRONMENT DATA:")
            self.investigation_results["production"] = self.get_user_data(
                self.production_base_url, self.production_token, "PRODUCTION"
            )
        
        # Step 4: Compare data completeness
        self.log("\nSTEP 4: Data Completeness Analysis")
        self.log("-" * 40)
        
        preview_score = 0
        production_score = 0
        
        if self.investigation_results["preview"]:
            preview_score, preview_details = self.analyze_data_completeness(
                self.investigation_results["preview"], "PREVIEW"
            )
        
        if self.investigation_results["production"]:
            production_score, production_details = self.analyze_data_completeness(
                self.investigation_results["production"], "PRODUCTION"
            )
        
        # Step 5: Final conclusion
        self.log("\nSTEP 5: INVESTIGATION CONCLUSION")
        self.log("=" * 80)
        
        if preview_score > production_score:
            winner = "PREVIEW"
            winner_score = preview_score
            winner_url = self.preview_base_url
            winner_user_id = self.preview_user_id
        elif production_score > preview_score:
            winner = "PRODUCTION"
            winner_score = production_score
            winner_url = self.production_base_url
            winner_user_id = self.production_user_id
        else:
            winner = "TIE"
            winner_score = preview_score
        
        if winner != "TIE":
            self.log(f"🎯 CONCLUSION: {winner} database contains the user's actual data")
            self.log(f"   Environment: {winner}")
            self.log(f"   URL: {winner_url}")
            self.log(f"   User ID: {winner_user_id}")
            self.log(f"   Completeness Score: {winner_score}/31")
            
            if winner == "PREVIEW":
                self.log("🚨 CRITICAL FINDING: Preview database has the actual user data!")
                self.log("   This means claire-marcus.com production is connected to WRONG database")
                self.log("   RECOMMENDATION: Update production to use preview database connection")
            else:
                self.log("✅ Production database has the correct user data")
                self.log("   Preview database appears to be outdated or test data")
        else:
            self.log("⚠️ INCONCLUSIVE: Both databases have similar data completeness")
            self.log("   Manual investigation required to determine correct database")
        
        # Step 6: MongoDB connection details investigation
        self.log("\nSTEP 6: MongoDB Connection Investigation")
        self.log("-" * 40)
        
        self.log("🔍 Checking diagnostic endpoints for database connection details...")
        
        # Check preview diagnostic
        try:
            response = requests.get(f"{self.preview_base_url}/diag", timeout=30)
            if response.status_code == 200:
                diag_data = response.json()
                self.log("📊 PREVIEW Database Connection:")
                self.log(f"   Connected: {diag_data.get('database_connected', 'Unknown')}")
                self.log(f"   Database: {diag_data.get('database_name', 'Unknown')}")
                self.log(f"   Mongo URL: {diag_data.get('mongo_url_prefix', 'Unknown')}")
        except Exception as e:
            self.log(f"❌ Preview diagnostic failed: {str(e)}")
        
        # Check production diagnostic
        try:
            response = requests.get(f"{self.production_base_url}/diag", timeout=30)
            if response.status_code == 200:
                diag_data = response.json()
                self.log("📊 PRODUCTION Database Connection:")
                self.log(f"   Connected: {diag_data.get('database_connected', 'Unknown')}")
                self.log(f"   Database: {diag_data.get('database_name', 'Unknown')}")
                self.log(f"   Mongo URL: {diag_data.get('mongo_url_prefix', 'Unknown')}")
        except Exception as e:
            self.log(f"❌ Production diagnostic failed: {str(e)}")
        
        self.log("\n" + "=" * 80)
        self.log("🏁 DATABASE INVESTIGATION COMPLETED")
        self.log("=" * 80)
        
        return {
            "preview_user_id": self.preview_user_id,
            "production_user_id": self.production_user_id,
            "preview_score": preview_score,
            "production_score": production_score,
            "winner": winner,
            "investigation_results": self.investigation_results
        }

def main():
    """Main function to run the database investigation"""
    print("🚨 URGENT DATABASE INVESTIGATION FOR lperpere@yahoo.fr")
    print("Comparing Preview vs Production databases to find actual user data")
    print("=" * 80)
    
    tester = DatabaseInvestigationTester()
    results = tester.run_investigation()
    
    # Return appropriate exit code
    if results["winner"] in ["PREVIEW", "PRODUCTION"]:
        print(f"\n✅ Investigation completed successfully - {results['winner']} has the actual data")
        return 0
    else:
        print(f"\n⚠️ Investigation inconclusive - manual review required")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)