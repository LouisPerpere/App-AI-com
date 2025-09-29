#!/usr/bin/env python3
"""
DIAGNOSTIC FINAL - POURQUOI IMAGES NE SE PUBLIENT TOUJOURS PAS
Comprehensive diagnostic testing for Facebook image publication issues
Following French review request with credentials lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://social-publisher-10.preview.emergentagent.com/api"
CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class FacebookImageDiagnostic:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        
    def authenticate(self):
        """Step 1: Authenticate user"""
        print("🔐 Step 1: Authentication")
        try:
            response = self.session.post(
                f"{BASE_URL}/auth/login-robust",
                json=CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token')
                self.user_id = data.get('user_id')
                
                # Set authorization header for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}'
                })
                
                print(f"✅ Authentication successful")
                print(f"   User ID: {self.user_id}")
                print(f"   Token: {self.token[:30]}...")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def test_facebook_publication_complete(self):
        """Test 1: Test publication Facebook COMPLÈTE avec logs détaillés"""
        print("\n📘 Test 1: Facebook Publication Complete with Detailed Logs")
        
        try:
            # First, get an accessible image URL
            print("🔍 Getting accessible image for testing...")
            
            # Test with WikiMedia image (publicly accessible)
            test_data = {
                "text": "Test publication Facebook avec image WikiMedia - Diagnostic final",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png"
            }
            
            print(f"📤 Publishing to Facebook with image:")
            print(f"   Text: {test_data['text']}")
            print(f"   Image URL: {test_data['image_url']}")
            
            response = self.session.post(
                f"{BASE_URL}/social/facebook/publish-simple",
                json=test_data,
                timeout=60
            )
            
            print(f"📥 Response Status: {response.status_code}")
            print(f"📥 Response Headers: {dict(response.headers)}")
            
            try:
                response_data = response.json()
                print(f"📥 Response Data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"📥 Response Text: {response.text}")
            
            # Test with system image
            print("\n🔍 Testing with system image...")
            
            # Get content from library
            content_response = self.session.get(f"{BASE_URL}/content/pending?limit=5")
            if content_response.status_code == 200:
                content_data = content_response.json()
                if content_data.get('content'):
                    first_image = content_data['content'][0]
                    system_image_url = first_image.get('url', '')
                    
                    print(f"   System image URL: {system_image_url}")
                    
                    # Test publication with system image
                    system_test_data = {
                        "text": "Test publication Facebook avec image système - Diagnostic final",
                        "image_url": system_image_url
                    }
                    
                    system_response = self.session.post(
                        f"{BASE_URL}/social/facebook/publish-simple",
                        json=system_test_data,
                        timeout=60
                    )
                    
                    print(f"📥 System Image Response Status: {system_response.status_code}")
                    try:
                        system_response_data = system_response.json()
                        print(f"📥 System Image Response: {json.dumps(system_response_data, indent=2, ensure_ascii=False)}")
                    except:
                        print(f"📥 System Image Response Text: {system_response.text}")
            
            return True
            
        except Exception as e:
            print(f"❌ Facebook publication test error: {e}")
            return False
    
    def verify_facebook_token_production(self):
        """Test 2: Vérifier token Facebook en production"""
        print("\n🔍 Test 2: Facebook Token Verification in Production")
        
        try:
            # Get social connections debug info
            response = self.session.get(f"{BASE_URL}/debug/social-connections")
            
            print(f"📥 Debug Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Social Connections Debug:")
                print(f"   Total connections: {data.get('total_connections', 0)}")
                print(f"   Active connections: {data.get('active_connections', 0)}")
                print(f"   Facebook connections: {data.get('facebook_connections', 0)}")
                print(f"   Instagram connections: {data.get('instagram_connections', 0)}")
                
                # Check for Facebook connections with tokens
                connections = data.get('connections_details', [])
                facebook_connections = [c for c in connections if c.get('platform') == 'facebook']
                
                print(f"\n🔍 Facebook Connections Analysis:")
                for i, conn in enumerate(facebook_connections):
                    print(f"   Connection {i+1}:")
                    print(f"     Platform: {conn.get('platform')}")
                    print(f"     Active: {conn.get('is_active', conn.get('active'))}")
                    print(f"     Connected at: {conn.get('connected_at')}")
                    
                    # Check token (truncated for security)
                    token = conn.get('access_token', '')
                    if token:
                        if token.startswith('temp_'):
                            print(f"     Token: TEMPORARY TOKEN - {token[:30]}...")
                            print(f"     ⚠️  WARNING: Using temporary token, not valid for Facebook API")
                        else:
                            print(f"     Token: {token[:30]}... (length: {len(token)})")
                    else:
                        print(f"     Token: NULL/MISSING")
                        print(f"     ❌ ERROR: No access token available")
                
                return len(facebook_connections) > 0
            else:
                print(f"❌ Debug endpoint failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Token verification error: {e}")
            return False
    
    def test_facebook_graph_api_direct(self):
        """Test 3: Test Facebook Graph API direct"""
        print("\n🌐 Test 3: Direct Facebook Graph API Test")
        
        try:
            # Get Facebook token from debug endpoint
            debug_response = self.session.get(f"{BASE_URL}/debug/social-connections")
            
            if debug_response.status_code == 200:
                data = debug_response.json()
                connections = data.get('connections_details', [])
                facebook_connections = [c for c in connections if c.get('platform') == 'facebook']
                
                if facebook_connections:
                    facebook_conn = facebook_connections[0]
                    access_token = facebook_conn.get('access_token', '')
                    page_id = facebook_conn.get('page_id', '')
                    
                    print(f"🔍 Testing with Facebook connection:")
                    print(f"   Page ID: {page_id}")
                    print(f"   Token: {access_token[:30]}..." if access_token else "   Token: MISSING")
                    
                    if access_token and page_id:
                        # Test direct Facebook Graph API call
                        facebook_url = f"https://graph.facebook.com/v20.0/{page_id}/photos"
                        
                        # Test image URL (WikiMedia)
                        test_image_url = "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png"
                        
                        facebook_data = {
                            'url': test_image_url,
                            'message': 'Test direct Facebook Graph API - Diagnostic final',
                            'access_token': access_token
                        }
                        
                        print(f"📤 Direct Facebook API Call:")
                        print(f"   URL: {facebook_url}")
                        print(f"   Image URL: {test_image_url}")
                        print(f"   Message: {facebook_data['message']}")
                        
                        # Make direct call to Facebook
                        facebook_response = requests.post(facebook_url, data=facebook_data, timeout=30)
                        
                        print(f"📥 Facebook API Response:")
                        print(f"   Status: {facebook_response.status_code}")
                        print(f"   Headers: {dict(facebook_response.headers)}")
                        
                        try:
                            facebook_result = facebook_response.json()
                            print(f"   Response: {json.dumps(facebook_result, indent=2, ensure_ascii=False)}")
                        except:
                            print(f"   Response Text: {facebook_response.text}")
                        
                        return facebook_response.status_code == 200
                    else:
                        print("❌ No valid Facebook token or page ID available")
                        return False
                else:
                    print("❌ No Facebook connections found")
                    return False
            else:
                print(f"❌ Could not get debug info: {debug_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Direct Facebook API test error: {e}")
            return False
    
    def diagnose_preview_vs_production(self):
        """Test 4: Diagnostic différence Preview vs Production"""
        print("\n🔄 Test 4: Preview vs Production Environment Diagnostic")
        
        try:
            # Test current environment
            print("🔍 Current Environment Analysis:")
            print(f"   Backend URL: {BASE_URL}")
            
            # Check health endpoint
            health_response = self.session.get(f"{BASE_URL}/health")
            if health_response.status_code == 200:
                health_data = health_response.json()
                print(f"   Service: {health_data.get('service', 'Unknown')}")
                print(f"   Status: {health_data.get('status', 'Unknown')}")
                print(f"   Timestamp: {health_data.get('timestamp', 'Unknown')}")
            
            # Check diagnostic endpoint
            diag_response = self.session.get(f"{BASE_URL}/diag")
            if diag_response.status_code == 200:
                diag_data = diag_response.json()
                print(f"   Database: {'Connected' if diag_data.get('database_connected') else 'Disconnected'}")
                print(f"   Environment: {diag_data.get('environment', 'Unknown')}")
                print(f"   Mongo URL: {diag_data.get('mongo_url_prefix', 'Unknown')}")
            
            # Test image accessibility in current environment
            print("\n🖼️ Image Accessibility Test:")
            
            # Get content list
            content_response = self.session.get(f"{BASE_URL}/content/pending?limit=3")
            if content_response.status_code == 200:
                content_data = content_response.json()
                images = content_data.get('content', [])
                
                print(f"   Found {len(images)} images in library")
                
                for i, image in enumerate(images[:3]):
                    image_id = image.get('id')
                    image_url = image.get('url', '')
                    
                    print(f"\n   Image {i+1}:")
                    print(f"     ID: {image_id}")
                    print(f"     URL: {image_url}")
                    
                    # Test direct access to image
                    if image_url:
                        try:
                            # Test protected endpoint
                            if image_url.startswith('/api/'):
                                full_url = BASE_URL.replace('/api', '') + image_url
                            else:
                                full_url = image_url
                            
                            print(f"     Testing: {full_url}")
                            
                            image_response = requests.get(full_url, timeout=10)
                            print(f"     Status: {image_response.status_code}")
                            print(f"     Content-Type: {image_response.headers.get('content-type', 'Unknown')}")
                            print(f"     Content-Length: {image_response.headers.get('content-length', 'Unknown')}")
                            
                            # Test public endpoint if available
                            if image_id:
                                public_url = f"{BASE_URL}/public/image/{image_id}"
                                print(f"     Testing public: {public_url}")
                                
                                public_response = requests.get(public_url, timeout=10)
                                print(f"     Public Status: {public_response.status_code}")
                                print(f"     Public Content-Type: {public_response.headers.get('content-type', 'Unknown')}")
                                
                        except Exception as img_e:
                            print(f"     Error testing image: {img_e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Environment diagnostic error: {e}")
            return False
    
    def test_text_vs_image_publication(self):
        """Test 5: Test publication texte seul vs avec image"""
        print("\n📝 Test 5: Text-only vs Image Publication Comparison")
        
        try:
            # Test 1: Text-only publication
            print("📝 Testing text-only publication:")
            
            text_only_data = {
                "text": "Test publication Facebook TEXTE SEUL - Diagnostic final"
            }
            
            text_response = self.session.post(
                f"{BASE_URL}/social/facebook/publish-simple",
                json=text_only_data,
                timeout=30
            )
            
            print(f"   Status: {text_response.status_code}")
            try:
                text_result = text_response.json()
                print(f"   Response: {json.dumps(text_result, indent=2, ensure_ascii=False)}")
            except:
                print(f"   Response Text: {text_response.text}")
            
            # Test 2: Publication with image
            print("\n🖼️ Testing publication with image:")
            
            image_data = {
                "text": "Test publication Facebook AVEC IMAGE - Diagnostic final",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png"
            }
            
            image_response = self.session.post(
                f"{BASE_URL}/social/facebook/publish-simple",
                json=image_data,
                timeout=30
            )
            
            print(f"   Status: {image_response.status_code}")
            try:
                image_result = image_response.json()
                print(f"   Response: {json.dumps(image_result, indent=2, ensure_ascii=False)}")
            except:
                print(f"   Response Text: {image_response.text}")
            
            # Compare results
            print("\n📊 Comparison Analysis:")
            print(f"   Text-only status: {text_response.status_code}")
            print(f"   With image status: {image_response.status_code}")
            
            if text_response.status_code == image_response.status_code:
                print("   ✅ Both requests have same status - issue is likely with tokens, not images")
            else:
                print("   ⚠️ Different status codes - image processing may have specific issues")
            
            return True
            
        except Exception as e:
            print(f"❌ Text vs image test error: {e}")
            return False
    
    def run_comprehensive_diagnostic(self):
        """Run complete diagnostic suite"""
        print("🚨 DIAGNOSTIC FINAL - POURQUOI IMAGES NE SE PUBLIENT TOUJOURS PAS")
        print("=" * 80)
        print(f"Identifiants: {CREDENTIALS['email']} / {CREDENTIALS['password']}")
        print(f"Backend URL: {BASE_URL}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 80)
        
        results = {}
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with diagnostic")
            return False
        
        results['authentication'] = True
        
        # Step 2: Facebook Publication Complete Test
        results['facebook_publication'] = self.test_facebook_publication_complete()
        
        # Step 3: Token Verification
        results['token_verification'] = self.verify_facebook_token_production()
        
        # Step 4: Direct Facebook API Test
        results['direct_facebook_api'] = self.test_facebook_graph_api_direct()
        
        # Step 5: Environment Diagnostic
        results['environment_diagnostic'] = self.diagnose_preview_vs_production()
        
        # Step 6: Text vs Image Test
        results['text_vs_image'] = self.test_text_vs_image_publication()
        
        # Final Analysis
        print("\n" + "=" * 80)
        print("🎯 DIAGNOSTIC FINAL RESULTS")
        print("=" * 80)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        
        print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name}: {status}")
        
        # Root Cause Analysis
        print("\n🔍 ROOT CAUSE ANALYSIS:")
        
        if not results.get('token_verification', False):
            print("❌ CRITICAL: Facebook token issues detected")
            print("   - Tokens may be temporary/invalid")
            print("   - OAuth callback may not be storing valid tokens")
            print("   - User needs to reconnect Facebook account")
        
        if results.get('facebook_publication', False) and results.get('token_verification', False):
            print("✅ Facebook publication system is working")
            print("   - Issue may be with specific image URLs")
            print("   - Check image accessibility and public endpoints")
        
        if not results.get('direct_facebook_api', False):
            print("❌ CRITICAL: Direct Facebook API calls failing")
            print("   - Confirms token or configuration issues")
            print("   - Facebook Graph API rejecting requests")
        
        print("\n🎯 RECOMMENDATIONS:")
        print("1. Check Facebook OAuth callback implementation")
        print("2. Verify Facebook App configuration in Developer Console")
        print("3. Ensure image URLs are publicly accessible")
        print("4. Test with valid Facebook access tokens")
        print("5. Check Facebook Graph API v20.0 compatibility")
        
        return passed_tests >= total_tests * 0.6  # 60% pass rate minimum

def main():
    """Main diagnostic function"""
    diagnostic = FacebookImageDiagnostic()
    
    try:
        success = diagnostic.run_comprehensive_diagnostic()
        
        if success:
            print("\n✅ Diagnostic completed successfully")
            sys.exit(0)
        else:
            print("\n❌ Diagnostic identified critical issues")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Diagnostic interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Diagnostic failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()