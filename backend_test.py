#!/usr/bin/env python3
"""
🎯 DIAGNOSTIC SPÉCIFIQUE IMAGES FACEBOOK SUR LIVE - TEXTE OK, IMAGE KO
Test environnement LIVE (claire-marcus.com) pour diagnostic images Facebook

Identifiants: lperpere@yahoo.fr / L@Reunion974!
ENVIRONNEMENT: LIVE (claire-marcus.com)

PROBLÈME CONFIRMÉ: Publication texte fonctionne ✅, publication image ne fonctionne pas ❌

DIAGNOSTIC SPÉCIFIQUE IMAGES SUR LIVE:
1. Test publication avec image sur LIVE - logs détaillés
2. Vérifier si mes corrections sont déployées sur LIVE
3. Test requête Facebook exacte sur LIVE
4. Diagnostic images publiques sur LIVE
5. Comparaison code LIVE vs PREVIEW
"""

import requests
import json
import sys
from datetime import datetime

# Configuration LIVE
LIVE_BACKEND_URL = "https://claire-marcus.com/api"
ALTERNATIVE_LIVE_URL = "https://claire-marcus-pwa-1.emergent.host/api"
CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class LiveEnvironmentTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Claire-Marcus-Testing-Agent/1.0'
        })
        self.access_token = None
        self.user_id = None
        self.backend_url = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_backend_connectivity(self):
        """Test connectivity to both possible LIVE URLs"""
        self.log("🔍 Testing LIVE backend connectivity...")
        
        urls_to_test = [LIVE_BACKEND_URL, ALTERNATIVE_LIVE_URL]
        
        for url in urls_to_test:
            try:
                self.log(f"   Testing: {url}")
                response = self.session.get(f"{url}/health", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log(f"   ✅ SUCCESS: {url}")
                    self.log(f"      Status: {data.get('status', 'unknown')}")
                    self.log(f"      Service: {data.get('service', 'unknown')}")
                    self.backend_url = url
                    return True
                else:
                    self.log(f"   ❌ FAILED: {url} - Status {response.status_code}")
                    
            except Exception as e:
                self.log(f"   ❌ ERROR: {url} - {str(e)}")
                
        return False
        
    def test_live_authentication(self):
        """1. Test authentification sur LIVE"""
        self.log("🔐 TEST 1: Authentication sur environnement LIVE")
        
        if not self.backend_url:
            self.log("❌ No backend URL available", "ERROR")
            return False
            
        try:
            response = self.session.post(
                f"{self.backend_url}/auth/login-robust",
                json=CREDENTIALS,
                timeout=15
            )
            
            self.log(f"   Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                self.user_id = data.get('user_id')
                
                self.log(f"   ✅ Authentication SUCCESS on LIVE")
                self.log(f"      User ID: {self.user_id}")
                self.log(f"      Token: {self.access_token[:30]}..." if self.access_token else "No token")
                
                # Update session headers with token
                if self.access_token:
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.access_token}'
                    })
                
                return True
            else:
                self.log(f"   ❌ Authentication FAILED: {response.status_code}")
                try:
                    error_data = response.json()
                    self.log(f"      Error: {error_data}")
                except:
                    self.log(f"      Raw response: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log(f"   ❌ Authentication ERROR: {str(e)}", "ERROR")
            return False
            
    def test_facebook_oauth_url_live(self):
        """2. Test génération URL OAuth Facebook sur LIVE"""
        self.log("🔗 TEST 2: Facebook OAuth URL generation sur LIVE")
        
        if not self.access_token:
            self.log("❌ No access token available", "ERROR")
            return False
            
        try:
            response = self.session.get(
                f"{self.backend_url}/social/facebook/auth-url",
                timeout=10
            )
            
            self.log(f"   Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get('auth_url', '')
                
                self.log(f"   ✅ Facebook OAuth URL SUCCESS on LIVE")
                self.log(f"      URL Length: {len(auth_url)}")
                
                # Analyze URL components
                if 'client_id=' in auth_url:
                    client_id = auth_url.split('client_id=')[1].split('&')[0]
                    self.log(f"      Client ID: {client_id}")
                    
                if 'config_id=' in auth_url:
                    config_id = auth_url.split('config_id=')[1].split('&')[0]
                    self.log(f"      Config ID: {config_id}")
                    
                if 'redirect_uri=' in auth_url:
                    redirect_uri = auth_url.split('redirect_uri=')[1].split('&')[0]
                    self.log(f"      Redirect URI: {redirect_uri}")
                    
                # Compare with expected values
                expected_client_id = "1115451684022643"
                expected_config_id = "1878388119742903"
                
                if expected_client_id in auth_url:
                    self.log(f"      ✅ Client ID matches expected: {expected_client_id}")
                else:
                    self.log(f"      ⚠️ Client ID mismatch - expected: {expected_client_id}")
                    
                if expected_config_id in auth_url:
                    self.log(f"      ✅ Config ID matches expected: {expected_config_id}")
                else:
                    self.log(f"      ⚠️ Config ID mismatch - expected: {expected_config_id}")
                    
                return True
            else:
                self.log(f"   ❌ Facebook OAuth URL FAILED: {response.status_code}")
                try:
                    error_data = response.json()
                    self.log(f"      Error: {error_data}")
                except:
                    self.log(f"      Raw response: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log(f"   ❌ Facebook OAuth URL ERROR: {str(e)}", "ERROR")
            return False
            
    def test_social_connections_state_live(self):
        """3. Test état des connexions sociales sur LIVE"""
        self.log("📱 TEST 3: Social connections state sur LIVE")
        
        if not self.access_token:
            self.log("❌ No access token available", "ERROR")
            return False
            
        # Test debug endpoint first
        try:
            response = self.session.get(
                f"{self.backend_url}/debug/social-connections",
                timeout=10
            )
            
            self.log(f"   Debug endpoint Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"   ✅ Debug social connections SUCCESS on LIVE")
                
                # Analyze connections data
                total_connections = data.get('total_connections', 0)
                active_connections = data.get('active_connections', 0)
                facebook_connections = data.get('facebook_connections', 0)
                instagram_connections = data.get('instagram_connections', 0)
                
                self.log(f"      Total connections: {total_connections}")
                self.log(f"      Active connections: {active_connections}")
                self.log(f"      Facebook connections: {facebook_connections}")
                self.log(f"      Instagram connections: {instagram_connections}")
                
                # Check for EAA tokens
                connections_detail = data.get('connections_detail', [])
                eaa_tokens_found = 0
                temp_tokens_found = 0
                
                for conn in connections_detail:
                    token = conn.get('access_token', '')
                    if token.startswith('EAA'):
                        eaa_tokens_found += 1
                        self.log(f"      ✅ EAA token found: {token[:20]}...")
                    elif 'temp_' in token:
                        temp_tokens_found += 1
                        self.log(f"      ⚠️ Temp token found: {token}")
                        
                self.log(f"      EAA tokens: {eaa_tokens_found}")
                self.log(f"      Temp tokens: {temp_tokens_found}")
                
            else:
                self.log(f"   ❌ Debug endpoint FAILED: {response.status_code}")
                
        except Exception as e:
            self.log(f"   ❌ Debug endpoint ERROR: {str(e)}", "ERROR")
            
        # Test regular connections endpoint
        try:
            response = self.session.get(
                f"{self.backend_url}/social/connections",
                timeout=10
            )
            
            self.log(f"   Regular endpoint Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                connections = data.get('connections', [])
                self.log(f"   ✅ Regular social connections SUCCESS on LIVE")
                self.log(f"      Visible connections: {len(connections)}")
                
                for conn in connections:
                    if isinstance(conn, dict):
                        platform = conn.get('platform', 'unknown')
                        is_active = conn.get('is_active', False)
                        page_name = conn.get('page_name', 'unknown')
                        self.log(f"      - {platform}: {page_name} (active: {is_active})")
                    else:
                        self.log(f"      - Connection: {conn}")
                    
                return True
            else:
                self.log(f"   ❌ Regular endpoint FAILED: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"   ❌ Regular endpoint ERROR: {str(e)}", "ERROR")
            return False
            
    def test_facebook_image_publication_live(self):
        """4. Test publication avec image sur LIVE - logs détaillés"""
        self.log("🖼️ TEST 4: Facebook image publication sur LIVE")
        
        if not self.access_token:
            self.log("❌ No access token available", "ERROR")
            return False
            
        # First, get available posts with images
        try:
            response = self.session.get(
                f"{self.backend_url}/posts/generated",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('posts', [])
                self.log(f"   Available posts: {len(posts)}")
                
                # Find Facebook posts with images
                facebook_posts_with_images = []
                for p in posts:
                    if (p.get('platform') == 'facebook' and 
                        (p.get('visual_url') or p.get('visual_id'))):
                        facebook_posts_with_images.append(p)
                
                self.log(f"   Facebook posts with images: {len(facebook_posts_with_images)}")
                
                if facebook_posts_with_images:
                    test_post = facebook_posts_with_images[0]
                    post_id = test_post.get('id')
                    visual_url = test_post.get('visual_url', '')
                    visual_id = test_post.get('visual_id', '')
                    
                    self.log(f"   Testing Facebook post with image:")
                    self.log(f"      Post ID: {post_id}")
                    self.log(f"      Visual URL: {visual_url}")
                    self.log(f"      Visual ID: {visual_id}")
                    
                    # Test publication endpoint with detailed logging
                    try:
                        self.log("   🚀 Attempting Facebook image publication...")
                        pub_response = self.session.post(
                            f"{self.backend_url}/posts/publish",
                            json={"post_id": post_id},
                            timeout=30  # Longer timeout for image processing
                        )
                        
                        self.log(f"   Publication Status: {pub_response.status_code}")
                        
                        if pub_response.status_code in [200, 400, 500]:
                            try:
                                pub_data = pub_response.json()
                                self.log(f"   📡 Publication response received:")
                                
                                # Detailed error analysis
                                error_msg = pub_data.get('error', '')
                                message = pub_data.get('message', '')
                                
                                if error_msg:
                                    self.log(f"      Error: {error_msg}")
                                    
                                    # Check for specific Facebook image issues
                                    if 'image' in error_msg.lower():
                                        self.log(f"      🔍 IMAGE-RELATED ERROR DETECTED")
                                    elif 'jpg' in error_msg.lower() or 'jpeg' in error_msg.lower():
                                        self.log(f"      🔍 JPG CONVERSION ERROR DETECTED")
                                    elif 'facebook' in error_msg.lower():
                                        self.log(f"      🔍 FACEBOOK API ERROR DETECTED")
                                    elif 'token' in error_msg.lower():
                                        self.log(f"      🔍 TOKEN ERROR (expected on LIVE)")
                                    elif 'connexion' in error_msg.lower():
                                        self.log(f"      🔍 CONNECTION ERROR (expected on LIVE)")
                                
                                if message:
                                    self.log(f"      Message: {message}")
                                
                                # Look for conversion logs
                                if 'conversion' in str(pub_data).lower():
                                    self.log(f"      ✅ JPG conversion mentioned in response")
                                if 'binary' in str(pub_data).lower():
                                    self.log(f"      ✅ Binary method mentioned in response")
                                    
                                return True
                            except:
                                self.log(f"      Raw response: {pub_response.text[:500]}")
                                return True
                        else:
                            self.log(f"   ❌ Publication endpoint FAILED: {pub_response.status_code}")
                            return False
                            
                    except Exception as e:
                        self.log(f"   ❌ Publication test ERROR: {str(e)}", "ERROR")
                        return False
                else:
                    self.log(f"   ⚠️ No Facebook posts with images available for testing")
                    # Try to find any Facebook posts
                    facebook_posts = [p for p in posts if p.get('platform') == 'facebook']
                    if facebook_posts:
                        self.log(f"   Found {len(facebook_posts)} Facebook posts without images")
                        return True
                    else:
                        self.log(f"   No Facebook posts found at all")
                        return False
                    
            else:
                self.log(f"   ❌ Posts retrieval FAILED: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"   ❌ Posts retrieval ERROR: {str(e)}", "ERROR")
            return False
            
    def test_public_images_facebook_access_live(self):
        """5. Test images publiques accessibles par Facebook sur LIVE"""
        self.log("🌐 TEST 5: Public images Facebook access sur LIVE")
        
        if not self.access_token:
            self.log("❌ No access token available", "ERROR")
            return False
            
        # Get content to find image IDs
        try:
            response = self.session.get(
                f"{self.backend_url}/content/pending?limit=10",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get('content', [])
                self.log(f"   Available content items: {len(content)}")
                
                if content:
                    # Test multiple images for Facebook accessibility
                    tested_images = 0
                    successful_images = 0
                    
                    for item in content[:5]:  # Test first 5 images
                        file_id = item.get('id')
                        filename = item.get('filename', 'unknown')
                        
                        self.log(f"   Testing image: {filename} (ID: {file_id})")
                        tested_images += 1
                        
                        # Test public endpoint (Facebook-accessible)
                        try:
                            # Test with Facebook User-Agent
                            facebook_headers = {
                                'User-Agent': 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)'
                            }
                            
                            img_response = self.session.get(
                                f"{self.backend_url}/public/image/{file_id}.webp",
                                headers=facebook_headers,
                                timeout=10
                            )
                            
                            self.log(f"      Facebook bot Status: {img_response.status_code}")
                            
                            if img_response.status_code == 200:
                                content_type = img_response.headers.get('content-type', '')
                                content_length = img_response.headers.get('content-length', '0')
                                
                                self.log(f"      ✅ Facebook accessible")
                                self.log(f"         Content-Type: {content_type}")
                                self.log(f"         Content-Length: {content_length} bytes")
                                
                                # Check if it's actually an image
                                if 'image' in content_type:
                                    self.log(f"         ✅ Valid image content for Facebook")
                                    successful_images += 1
                                else:
                                    self.log(f"         ⚠️ Unexpected content type for Facebook")
                                    
                            elif img_response.status_code == 302:
                                redirect_url = img_response.headers.get('location', '')
                                self.log(f"      ✅ Facebook redirect")
                                self.log(f"         Redirect to: {redirect_url}")
                                successful_images += 1
                            else:
                                self.log(f"      ❌ Facebook access FAILED: {img_response.status_code}")
                                
                        except Exception as e:
                            self.log(f"      ❌ Facebook test ERROR: {str(e)}")
                    
                    # Test JPG conversion endpoint
                    if content:
                        test_item = content[0]
                        file_id = test_item.get('id')
                        
                        self.log(f"   Testing JPG conversion for: {file_id}")
                        try:
                            # Test if JPG conversion is available
                            jpg_response = self.session.get(
                                f"{self.backend_url}/public/image/{file_id}",  # Without .webp
                                timeout=10
                            )
                            
                            self.log(f"      JPG conversion Status: {jpg_response.status_code}")
                            
                            if jpg_response.status_code == 200:
                                content_type = jpg_response.headers.get('content-type', '')
                                if 'jpeg' in content_type or 'jpg' in content_type:
                                    self.log(f"      ✅ JPG conversion working")
                                else:
                                    self.log(f"      ⚠️ JPG conversion returns: {content_type}")
                            else:
                                self.log(f"      ❌ JPG conversion not available")
                                
                        except Exception as e:
                            self.log(f"      ❌ JPG conversion ERROR: {str(e)}")
                    
                    self.log(f"   📊 Facebook accessibility: {successful_images}/{tested_images} images")
                    return successful_images > 0
                else:
                    self.log(f"   ⚠️ No content available for testing")
                    return True
                    
            else:
                self.log(f"   ❌ Content retrieval FAILED: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"   ❌ Content retrieval ERROR: {str(e)}", "ERROR")
            return False
            
    def test_jpg_conversion_deployment_live(self):
        """6. Vérifier si mes corrections JPG sont déployées sur LIVE"""
        self.log("🔧 TEST 6: JPG conversion deployment sur LIVE")
        
        if not self.access_token:
            self.log("❌ No access token available", "ERROR")
            return False
            
        # Test if convert_to_public_image_url function is working
        try:
            # Get a post with image to test conversion
            response = self.session.get(
                f"{self.backend_url}/posts/generated?limit=5",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('posts', [])
                
                posts_with_images = [p for p in posts if p.get('visual_url')]
                self.log(f"   Posts with images: {len(posts_with_images)}")
                
                if posts_with_images:
                    test_post = posts_with_images[0]
                    visual_url = test_post.get('visual_url', '')
                    
                    self.log(f"   Testing image URL conversion:")
                    self.log(f"      Original URL: {visual_url}")
                    
                    # Check if URL looks like it's been converted
                    if '/api/public/image/' in visual_url:
                        self.log(f"      ✅ URL appears to be converted to public format")
                    elif '/api/content/' in visual_url:
                        self.log(f"      ⚠️ URL still in protected format - conversion may not be deployed")
                    else:
                        self.log(f"      ℹ️ External URL (Pixabay/WikiMedia)")
                    
                    # Test if the image is accessible
                    if visual_url.startswith('/'):
                        full_url = f"{self.backend_url.replace('/api', '')}{visual_url}"
                    else:
                        full_url = visual_url
                        
                    try:
                        img_test = self.session.get(full_url, timeout=10)
                        self.log(f"      Image accessibility: {img_test.status_code}")
                        
                        if img_test.status_code == 200:
                            content_type = img_test.headers.get('content-type', '')
                            self.log(f"      Content-Type: {content_type}")
                            
                            if 'jpeg' in content_type or 'jpg' in content_type:
                                self.log(f"      ✅ JPG format confirmed")
                            elif 'webp' in content_type:
                                self.log(f"      ⚠️ Still WebP format - JPG conversion may not be working")
                            else:
                                self.log(f"      ℹ️ Other format: {content_type}")
                                
                        return True
                    except Exception as e:
                        self.log(f"      ❌ Image test ERROR: {str(e)}")
                        return False
                else:
                    self.log(f"   ⚠️ No posts with images found")
                    return True
            else:
                self.log(f"   ❌ Posts retrieval FAILED: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"   ❌ JPG conversion test ERROR: {str(e)}", "ERROR")
            return False
            
    def compare_live_vs_preview_code(self):
        """7. Comparaison code LIVE vs PREVIEW"""
        self.log("🔄 TEST 7: LIVE vs PREVIEW code comparison")
        
        preview_url = "https://social-publisher-10.preview.emergentagent.com/api"
        
        # Test health endpoints to see if they're different versions
        try:
            live_health = self.session.get(f"{self.backend_url}/health", timeout=5)
            preview_health = self.session.get(f"{preview_url}/health", timeout=5)
            
            if live_health.status_code == 200 and preview_health.status_code == 200:
                live_data = live_health.json()
                preview_data = preview_health.json()
                
                self.log(f"   LIVE service: {live_data.get('service', 'unknown')}")
                self.log(f"   PREVIEW service: {preview_data.get('service', 'unknown')}")
                
                live_timestamp = live_data.get('timestamp', '')
                preview_timestamp = preview_data.get('timestamp', '')
                
                self.log(f"   LIVE timestamp: {live_timestamp}")
                self.log(f"   PREVIEW timestamp: {preview_timestamp}")
                
                if live_data.get('service') == preview_data.get('service'):
                    self.log(f"   ✅ Same service name")
                else:
                    self.log(f"   ⚠️ Different service names")
                    
                # Test if both have same endpoints
                endpoints_to_test = [
                    '/posts/publish',
                    '/public/image/test',
                    '/social/facebook/publish-simple'
                ]
                
                for endpoint in endpoints_to_test:
                    try:
                        live_test = self.session.get(f"{self.backend_url}{endpoint}", timeout=3)
                        preview_test = self.session.get(f"{preview_url}{endpoint}", timeout=3)
                        
                        self.log(f"   Endpoint {endpoint}:")
                        self.log(f"      LIVE: {live_test.status_code}")
                        self.log(f"      PREVIEW: {preview_test.status_code}")
                        
                        if live_test.status_code == preview_test.status_code:
                            self.log(f"      ✅ Same response codes")
                        else:
                            self.log(f"      ⚠️ Different response codes - possible version difference")
                            
                    except Exception as e:
                        self.log(f"      ❌ Endpoint test ERROR: {str(e)}")
                        
                return True
            else:
                self.log(f"   ❌ Health check failed - LIVE: {live_health.status_code}, PREVIEW: {preview_health.status_code}")
                return False
                    
        except Exception as e:
            self.log(f"   ❌ Comparison ERROR: {str(e)}", "ERROR")
            return False
            
    def run_all_tests(self):
        """Run all LIVE environment tests"""
        self.log("🚀 STARTING FACEBOOK IMAGES LIVE ENVIRONMENT TESTING")
        self.log("=" * 60)
        
        results = {}
        
        # Test backend connectivity
        results['connectivity'] = self.test_backend_connectivity()
        
        if not results['connectivity']:
            self.log("❌ CRITICAL: Cannot connect to LIVE backend", "ERROR")
            return results
            
        # Run all tests
        results['authentication'] = self.test_live_authentication()
        results['facebook_oauth'] = self.test_facebook_oauth_url_live()
        results['social_connections'] = self.test_social_connections_state_live()
        results['facebook_image_publication'] = self.test_facebook_image_publication_live()
        results['public_images_facebook'] = self.test_public_images_facebook_access_live()
        results['jpg_conversion_deployment'] = self.test_jpg_conversion_deployment_live()
        results['live_vs_preview_comparison'] = self.compare_live_vs_preview_code()
        
        # Summary
        self.log("=" * 60)
        self.log("📊 TEST RESULTS SUMMARY:")
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"   {test_name}: {status}")
            
        self.log(f"")
        self.log(f"🎯 OVERALL SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        if success_rate >= 80:
            self.log(f"🎉 LIVE ENVIRONMENT TESTING: SUCCESS")
        elif success_rate >= 60:
            self.log(f"⚠️ LIVE ENVIRONMENT TESTING: PARTIAL SUCCESS")
        else:
            self.log(f"❌ LIVE ENVIRONMENT TESTING: NEEDS ATTENTION")
            
        return results

if __name__ == "__main__":
    tester = LiveEnvironmentTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    if success_rate >= 80:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure
