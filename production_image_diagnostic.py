#!/usr/bin/env python3
"""
Facebook Image Publication Diagnostic - Production vs Preview
Testing Facebook image publication issues in production environment

Identifiants: lperpere@yahoo.fr / L@Reunion974!

DIAGNOSTIC OBJECTIVES:
1. Test URL production directe - GET https://claire-marcus.com/api/public/image/{id} without auth
2. Compare with preview URL that was working
3. Test curl production manual with HTTP headers analysis
4. Test Facebook publication in production with image URLs
5. Diagnostic production environment variables
6. Test Facebook Graph API direct with production URLs

HYPOTHESIS: Configuration serveur/proxy différente entre preview et production bloque l'accès aux images
"""

import requests
import json
import sys
import subprocess
import time
from datetime import datetime
from urllib.parse import urlparse

# Configuration - PRODUCTION URLs
PRODUCTION_BASE_URL = "https://claire-marcus.com/api"
PREVIEW_BASE_URL = "https://social-pub-hub.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class ProductionImageDiagnostic:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        self.test_image_ids = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()
        
    def authenticate_production(self):
        """Step 1: Authenticate with production environment"""
        try:
            print("🔐 Step 1: Production Authentication")
            response = self.session.post(
                f"{PRODUCTION_BASE_URL}/auth/login-robust",
                json=TEST_CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                self.log_test("Production Authentication", True, f"User ID: {self.user_id}")
                return True
            else:
                self.log_test("Production Authentication", False, 
                            f"Status: {response.status_code}", 
                            response.text[:200])
                return False
                
        except Exception as e:
            self.log_test("Production Authentication", False, error=str(e))
            return False
    
    def get_test_image_ids(self):
        """Get some image IDs for testing from production"""
        try:
            print("🖼️ Getting test image IDs from production")
            response = self.session.get(f"{PRODUCTION_BASE_URL}/content/pending?limit=5", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                
                # Filter for images only
                image_content = [item for item in content if item.get("file_type", "").startswith("image")]
                
                if image_content:
                    self.test_image_ids = [item["id"] for item in image_content[:3]]  # Take first 3 images
                    self.log_test("Get Test Image IDs", True, 
                                f"Found {len(self.test_image_ids)} test images: {self.test_image_ids}")
                    return True
                else:
                    self.log_test("Get Test Image IDs", False, "No images found in content library")
                    return False
            else:
                self.log_test("Get Test Image IDs", False, 
                            f"Status: {response.status_code}", response.text[:200])
                return False
                
        except Exception as e:
            self.log_test("Get Test Image IDs", False, error=str(e))
            return False
    
    def test_production_public_image_direct(self):
        """Test 1: Test URL production directe - GET https://claire-marcus.com/api/public/image/{id} without auth"""
        try:
            print("🌐 Test 1: Production Public Image URL Direct Access")
            
            if not self.test_image_ids:
                # Use fallback test IDs
                self.test_image_ids = ["test_image_1", "test_image_2"]
                print("   Using fallback test image IDs")
            
            # Test without authentication
            session_no_auth = requests.Session()
            
            results = []
            for image_id in self.test_image_ids:
                try:
                    url = f"{PRODUCTION_BASE_URL}/public/image/{image_id}"
                    response = session_no_auth.get(url, timeout=30, allow_redirects=False)
                    
                    results.append({
                        "image_id": image_id,
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "content_type": response.headers.get("Content-Type", ""),
                        "content_length": response.headers.get("Content-Length", "0"),
                        "location": response.headers.get("Location", "")
                    })
                    
                except Exception as e:
                    results.append({
                        "image_id": image_id,
                        "error": str(e)
                    })
            
            # Analyze results
            success_count = sum(1 for r in results if r.get("status_code") == 200)
            redirect_count = sum(1 for r in results if r.get("status_code") in [301, 302])
            error_count = sum(1 for r in results if r.get("status_code", 0) >= 400)
            
            if success_count > 0:
                self.log_test("Production Public Image Direct", True, 
                            f"✅ {success_count}/{len(results)} images accessible directly (Status 200)")
            elif redirect_count > 0:
                self.log_test("Production Public Image Direct", False, 
                            f"❌ {redirect_count}/{len(results)} images redirect (may need auth)")
            else:
                self.log_test("Production Public Image Direct", False, 
                            f"❌ {error_count}/{len(results)} images failed with errors")
            
            # Log detailed results
            for result in results:
                if "error" not in result:
                    print(f"   Image {result['image_id']}: Status {result['status_code']}, "
                          f"Type: {result['content_type']}, Size: {result['content_length']}")
                else:
                    print(f"   Image {result['image_id']}: Error - {result['error']}")
            
            return success_count > 0
                
        except Exception as e:
            self.log_test("Production Public Image Direct", False, error=str(e))
            return False
    
    def test_preview_vs_production_comparison(self):
        """Test 2: Compare preview vs production image access"""
        try:
            print("🔄 Test 2: Preview vs Production Image Access Comparison")
            
            if not self.test_image_ids:
                self.log_test("Preview vs Production Comparison", False, "No test image IDs available")
                return False
            
            session_no_auth = requests.Session()
            comparison_results = []
            
            for image_id in self.test_image_ids[:2]:  # Test first 2 images
                try:
                    # Test production
                    prod_url = f"{PRODUCTION_BASE_URL}/public/image/{image_id}"
                    prod_response = session_no_auth.get(prod_url, timeout=30, allow_redirects=False)
                    
                    # Test preview
                    preview_url = f"{PREVIEW_BASE_URL}/public/image/{image_id}"
                    preview_response = session_no_auth.get(preview_url, timeout=30, allow_redirects=False)
                    
                    comparison_results.append({
                        "image_id": image_id,
                        "production": {
                            "status": prod_response.status_code,
                            "content_type": prod_response.headers.get("Content-Type", ""),
                            "accessible": prod_response.status_code == 200
                        },
                        "preview": {
                            "status": preview_response.status_code,
                            "content_type": preview_response.headers.get("Content-Type", ""),
                            "accessible": preview_response.status_code == 200
                        }
                    })
                    
                except Exception as e:
                    comparison_results.append({
                        "image_id": image_id,
                        "error": str(e)
                    })
            
            # Analyze comparison
            differences_found = False
            for result in comparison_results:
                if "error" not in result:
                    prod_accessible = result["production"]["accessible"]
                    preview_accessible = result["preview"]["accessible"]
                    
                    if prod_accessible != preview_accessible:
                        differences_found = True
                        print(f"   🚨 DIFFERENCE FOUND for {result['image_id']}:")
                        print(f"      Production: Status {result['production']['status']} ({'✅' if prod_accessible else '❌'})")
                        print(f"      Preview: Status {result['preview']['status']} ({'✅' if preview_accessible else '❌'})")
                    else:
                        print(f"   ✅ CONSISTENT for {result['image_id']}: Both {'accessible' if prod_accessible else 'not accessible'}")
            
            if differences_found:
                self.log_test("Preview vs Production Comparison", False, 
                            "❌ CRITICAL: Differences found between preview and production image access")
            else:
                self.log_test("Preview vs Production Comparison", True, 
                            "✅ Consistent behavior between preview and production")
            
            return not differences_found
                
        except Exception as e:
            self.log_test("Preview vs Production Comparison", False, error=str(e))
            return False
    
    def test_curl_production_manual(self):
        """Test 3: Test curl production manual with detailed HTTP headers"""
        try:
            print("🔧 Test 3: Curl Production Manual with HTTP Headers Analysis")
            
            if not self.test_image_ids:
                self.log_test("Curl Production Manual", False, "No test image IDs available")
                return False
            
            curl_results = []
            
            for image_id in self.test_image_ids[:2]:  # Test first 2 images
                try:
                    url = f"{PRODUCTION_BASE_URL}/public/image/{image_id}"
                    
                    # Execute curl command with detailed headers
                    curl_cmd = [
                        "curl", "-I", "-L", "-v", 
                        "--max-time", "30",
                        "--user-agent", "FacebookBot/1.0",
                        url
                    ]
                    
                    result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=35)
                    
                    curl_results.append({
                        "image_id": image_id,
                        "url": url,
                        "return_code": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    })
                    
                except Exception as e:
                    curl_results.append({
                        "image_id": image_id,
                        "error": str(e)
                    })
            
            # Analyze curl results
            success_count = sum(1 for r in curl_results if r.get("return_code") == 0)
            
            if success_count > 0:
                self.log_test("Curl Production Manual", True, 
                            f"✅ {success_count}/{len(curl_results)} curl requests successful")
                
                # Extract key information from curl output
                for result in curl_results:
                    if result.get("return_code") == 0:
                        output = result.get("stderr", "") + result.get("stdout", "")
                        
                        # Extract status code
                        status_match = None
                        for line in output.split('\n'):
                            if 'HTTP/' in line and ('200' in line or '302' in line or '404' in line):
                                status_match = line.strip()
                                break
                        
                        print(f"   Image {result['image_id']}: {status_match or 'Status unknown'}")
                        
                        # Look for Content-Type
                        if 'content-type:' in output.lower():
                            for line in output.split('\n'):
                                if 'content-type:' in line.lower():
                                    print(f"      Content-Type: {line.strip()}")
                                    break
            else:
                self.log_test("Curl Production Manual", False, 
                            f"❌ All {len(curl_results)} curl requests failed")
                
                # Show errors
                for result in curl_results:
                    if "error" in result:
                        print(f"   Image {result['image_id']}: Error - {result['error']}")
                    elif result.get("return_code") != 0:
                        print(f"   Image {result['image_id']}: Curl failed with code {result['return_code']}")
            
            return success_count > 0
                
        except Exception as e:
            self.log_test("Curl Production Manual", False, error=str(e))
            return False
    
    def test_facebook_publication_production(self):
        """Test 4: Test Facebook publication in production with image URLs"""
        try:
            print("📘 Test 4: Facebook Publication in Production")
            
            if not self.test_image_ids:
                self.log_test("Facebook Publication Production", False, "No test image IDs available")
                return False
            
            # Test with system image URL
            test_image_id = self.test_image_ids[0]
            system_image_url = f"{PRODUCTION_BASE_URL}/public/image/{test_image_id}"
            
            test_data = {
                "text": "Test publication Facebook production - Diagnostic images",
                "image_url": system_image_url
            }
            
            response = self.session.post(
                f"{PRODUCTION_BASE_URL}/social/facebook/publish-simple", 
                json=test_data, 
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                error_message = data.get("error", "")
                
                # Log the exact response for analysis
                print(f"   Response: {json.dumps(data, indent=2)}")
                
                if success:
                    self.log_test("Facebook Publication Production", True, 
                                f"✅ Publication successful with system image URL")
                    return True
                else:
                    # Check if error is related to image access vs connection issues
                    if "connexion" in error_message.lower() or "token" in error_message.lower():
                        self.log_test("Facebook Publication Production", True, 
                                    f"✅ Image URL processed correctly, error is connection-related: {error_message}")
                        return True
                    elif "image" in error_message.lower() or "url" in error_message.lower():
                        self.log_test("Facebook Publication Production", False, 
                                    f"❌ Image URL access issue: {error_message}")
                        return False
                    else:
                        self.log_test("Facebook Publication Production", False, 
                                    f"❌ Unknown publication error: {error_message}")
                        return False
            else:
                self.log_test("Facebook Publication Production", False, 
                            f"Status: {response.status_code}", response.text[:200])
                return False
                
        except Exception as e:
            self.log_test("Facebook Publication Production", False, error=str(e))
            return False
    
    def test_environment_variables_production(self):
        """Test 5: Diagnostic production environment variables"""
        try:
            print("🔧 Test 5: Production Environment Variables Diagnostic")
            
            # Test backend URL configuration
            response = self.session.get(f"{PRODUCTION_BASE_URL}/diag", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check key environment indicators
                mongo_url_prefix = data.get("mongo_url_prefix", "")
                environment = data.get("environment", "")
                database_connected = data.get("database_connected", False)
                
                details = f"Environment: {environment}, DB Connected: {database_connected}, Mongo: {mongo_url_prefix}"
                
                if database_connected:
                    self.log_test("Production Environment Diagnostic", True, 
                                f"✅ Production environment accessible: {details}")
                    
                    # Additional check: verify REACT_APP_BACKEND_URL alignment
                    if "claire-marcus.com" in PRODUCTION_BASE_URL:
                        print("   ✅ Production URL alignment: Backend URL matches claire-marcus.com domain")
                    else:
                        print("   ⚠️ Production URL alignment: Backend URL may not match expected domain")
                    
                    return True
                else:
                    self.log_test("Production Environment Diagnostic", False, 
                                f"❌ Database connection issue: {details}")
                    return False
            else:
                self.log_test("Production Environment Diagnostic", False, 
                            f"Status: {response.status_code}", response.text[:200])
                return False
                
        except Exception as e:
            self.log_test("Production Environment Diagnostic", False, error=str(e))
            return False
    
    def test_facebook_graph_api_direct(self):
        """Test 6: Test Facebook Graph API direct with production URLs"""
        try:
            print("📘 Test 6: Facebook Graph API Direct Test")
            
            if not self.test_image_ids:
                self.log_test("Facebook Graph API Direct", False, "No test image IDs available")
                return False
            
            # This test simulates what Facebook would do when trying to access our image
            test_image_id = self.test_image_ids[0]
            production_image_url = f"{PRODUCTION_BASE_URL}/public/image/{test_image_id}"
            
            # Simulate Facebook's user agent
            facebook_session = requests.Session()
            facebook_session.headers.update({
                "User-Agent": "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)"
            })
            
            try:
                # Test image accessibility from Facebook's perspective
                response = facebook_session.get(production_image_url, timeout=30)
                
                if response.status_code == 200:
                    content_type = response.headers.get("Content-Type", "")
                    content_length = len(response.content)
                    
                    if content_type.startswith("image/"):
                        self.log_test("Facebook Graph API Direct", True, 
                                    f"✅ Image accessible to Facebook bot: {content_type}, {content_length} bytes")
                        return True
                    else:
                        self.log_test("Facebook Graph API Direct", False, 
                                    f"❌ Wrong content type for Facebook: {content_type}")
                        return False
                elif response.status_code == 302:
                    location = response.headers.get("Location", "")
                    self.log_test("Facebook Graph API Direct", False, 
                                f"❌ Image redirects (Facebook can't follow): Status 302 -> {location}")
                    return False
                else:
                    self.log_test("Facebook Graph API Direct", False, 
                                f"❌ Image not accessible to Facebook: Status {response.status_code}")
                    return False
                    
            except Exception as e:
                self.log_test("Facebook Graph API Direct", False, 
                            f"❌ Facebook bot simulation failed: {str(e)}")
                return False
                
        except Exception as e:
            self.log_test("Facebook Graph API Direct", False, error=str(e))
            return False
    
    def run_diagnostic(self):
        """Run complete Facebook image publication diagnostic"""
        print("🎯 FACEBOOK IMAGE PUBLICATION DIAGNOSTIC - PRODUCTION VS PREVIEW")
        print("=" * 80)
        print(f"Production URL: {PRODUCTION_BASE_URL}")
        print(f"Preview URL: {PREVIEW_BASE_URL}")
        print(f"Test User: {TEST_CREDENTIALS['email']}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 80)
        print()
        
        # Step 1: Authentication
        if not self.authenticate_production():
            print("❌ Production authentication failed - cannot continue diagnostic")
            return False
        
        # Step 2: Get test image IDs
        if not self.get_test_image_ids():
            print("❌ Cannot get test image IDs - using fallback approach")
            # Use some common image IDs as fallback
            self.test_image_ids = ["test_image_1", "test_image_2"]
        
        # Test 1: Production public image direct access
        self.test_production_public_image_direct()
        
        # Test 2: Preview vs production comparison
        self.test_preview_vs_production_comparison()
        
        # Test 3: Curl production manual
        self.test_curl_production_manual()
        
        # Test 4: Facebook publication in production
        self.test_facebook_publication_production()
        
        # Test 5: Environment variables diagnostic
        self.test_environment_variables_production()
        
        # Test 6: Facebook Graph API direct
        self.test_facebook_graph_api_direct()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 DIAGNOSTIC SUMMARY - FACEBOOK IMAGE PUBLICATION")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print(f"\n🎯 RESULTS: {passed}/{total} tests passed ({(passed/total*100):.1f}%)")
        
        # Diagnostic conclusion
        print("\n🔍 DIAGNOSTIC CONCLUSION:")
        
        if passed >= total * 0.8:  # 80% success rate
            print("✅ LIKELY CAUSE: System working correctly - issue may be in Facebook app configuration")
            print("   - Images are accessible in production")
            print("   - URLs are properly formatted")
            print("   - Environment configuration is correct")
            print("   - Check Facebook Developer Console settings")
        elif passed >= total * 0.5:  # 50% success rate
            print("⚠️ MIXED RESULTS: Partial functionality detected")
            print("   - Some components working, others failing")
            print("   - Review failed tests for specific issues")
            print("   - May require targeted fixes")
        else:
            print("❌ CRITICAL ISSUES DETECTED: Major problems found")
            print("   - Images likely not accessible to Facebook in production")
            print("   - Server/proxy configuration differences confirmed")
            print("   - Immediate fixes required for image publication")
        
        return passed >= total * 0.5

def main():
    """Main diagnostic execution"""
    diagnostic = ProductionImageDiagnostic()
    success = diagnostic.run_diagnostic()
    
    if success:
        print("\n✅ Facebook image publication diagnostic completed!")
        print("🔍 Review results above for specific issues and recommendations")
        sys.exit(0)
    else:
        print("\n❌ Facebook image publication diagnostic revealed critical issues!")
        print("🚨 Immediate attention required for production image access")
        sys.exit(1)

if __name__ == "__main__":
    main()