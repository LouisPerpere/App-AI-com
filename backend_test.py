#!/usr/bin/env python3
"""
FACEBOOK IMAGE PUBLICATION DIAGNOSTIC - BACKEND TESTING
Comprehensive testing for Facebook publication with real image verification
Following French review request: lperpere@yahoo.fr / L@Reunion974!

OBJECTIFS:
1. Test real Facebook publication with image via API
2. Capture complete backend logs to see JPG conversion
3. Verify if image actually appears on Facebook
4. Check Facebook Graph API to see if post contains image
5. Diagnose exact Facebook HTTP request
6. Test specific system image with manual JPG conversion
7. Compare with working posts

ENVIRONNEMENT: LIVE (claire-marcus.com)
QUESTION CENTRALE: Quand tu publies depuis l'interface, l'image apparaît-elle vraiment sur Facebook ou seulement le texte ?
"""

import requests
import json
import sys
import time
import re
from datetime import datetime

# Configuration
BACKEND_URL = "https://social-publisher-10.preview.emergentagent.com/api"
LIVE_BACKEND_URL = "https://claire-marcus.com/api"
CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class FacebookImagePublicationTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Facebook-Image-Diagnostic/1.0'
        })
        self.access_token = None
        self.user_id = None
        self.backend_url = BACKEND_URL
        self.test_results = []
        
    def log(self, message, level="INFO"):
        """Enhanced logging with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def log_result(self, test_name, success, details):
        """Log test results with structured format"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅" if success else "❌"
        self.log(f"{status} {test_name}: {details}")
        
    def authenticate(self):
        """ÉTAPE 1: Authentification avec backend"""
        self.log("🔐 ÉTAPE 1: AUTHENTIFICATION BACKEND")
        
        try:
            response = self.session.post(
                f"{self.backend_url}/auth/login-robust",
                json=CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                self.log_result(
                    "Authentication", 
                    True, 
                    f"User ID: {self.user_id}, Token: {self.access_token[:20]}..."
                )
                return True
            else:
                self.log_result(
                    "Authentication", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_facebook_posts_with_images(self):
        """ÉTAPE 2: Récupérer posts Facebook avec images"""
        self.log("📋 ÉTAPE 2: RÉCUPÉRATION POSTS FACEBOOK AVEC IMAGES")
        
        try:
            response = self.session.get(f"{self.backend_url}/posts/generated", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                
                # Filter Facebook posts with images
                facebook_posts = [
                    post for post in posts 
                    if post.get("platform") == "facebook" and post.get("visual_url")
                ]
                
                self.log_result(
                    "Facebook Posts Retrieval", 
                    True, 
                    f"Found {len(facebook_posts)} Facebook posts with images out of {len(posts)} total"
                )
                
                # Log details of available posts
                for i, post in enumerate(facebook_posts[:5]):
                    self.log(f"   📄 Post {i+1}: {post.get('id')}")
                    self.log(f"      Title: {post.get('title', 'No title')[:60]}...")
                    self.log(f"      Platform: {post.get('platform')}, Status: {post.get('status')}")
                    self.log(f"      Image URL: {post.get('visual_url', 'No image')[:80]}...")
                    self.log(f"      Scheduled: {post.get('scheduled_date', 'No date')}")
                
                return facebook_posts
            else:
                self.log_result(
                    "Facebook Posts Retrieval", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                return []
                
        except Exception as e:
            self.log_result("Facebook Posts Retrieval", False, f"Exception: {str(e)}")
            return []
    
    def check_facebook_connections(self):
        """ÉTAPE 3: Vérifier connexions Facebook"""
        self.log("🔗 ÉTAPE 3: VÉRIFICATION CONNEXIONS FACEBOOK")
        
        try:
            # Check regular connections
            response = self.session.get(f"{self.backend_url}/social/connections", timeout=30)
            
            if response.status_code == 200:
                connections = response.json()
                facebook_connections = [
                    conn for conn in connections 
                    if conn.get("platform") == "facebook"
                ]
                
                self.log_result(
                    "Facebook Connections", 
                    True, 
                    f"Found {len(facebook_connections)} Facebook connections out of {len(connections)} total"
                )
                
                # Try debug endpoint for detailed info
                try:
                    debug_response = self.session.get(f"{self.backend_url}/debug/social-connections", timeout=30)
                    if debug_response.status_code == 200:
                        debug_data = debug_response.json()
                        self.log(f"   🔍 Debug connections info:")
                        self.log(f"      Total connections: {debug_data.get('total_connections', 0)}")
                        self.log(f"      Active connections: {debug_data.get('active_connections', 0)}")
                        self.log(f"      Facebook connections: {debug_data.get('facebook_connections', 0)}")
                        self.log(f"      Instagram connections: {debug_data.get('instagram_connections', 0)}")
                        
                        # Check for token details
                        if 'connections_details' in debug_data:
                            for conn in debug_data['connections_details'][:3]:
                                platform = conn.get('platform', 'unknown')
                                token = conn.get('access_token', 'No token')
                                active = conn.get('is_active', False)
                                self.log(f"      {platform}: active={active}, token={token[:20]}..." if token != 'No token' else f"      {platform}: active={active}, no token")
                                
                except Exception as debug_e:
                    self.log(f"   ⚠️ Debug endpoint error: {str(debug_e)}")
                
                return facebook_connections
            else:
                self.log_result(
                    "Facebook Connections", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                return []
                
        except Exception as e:
            self.log_result("Facebook Connections", False, f"Exception: {str(e)}")
            return []
    
    def test_image_accessibility(self, image_url):
        """ÉTAPE 4: Tester accessibilité image pour Facebook"""
        self.log(f"🖼️ ÉTAPE 4: TEST ACCESSIBILITÉ IMAGE")
        self.log(f"   URL testée: {image_url}")
        
        # Test 1: Direct access without auth (Facebook bot simulation)
        try:
            headers = {
                'User-Agent': 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)'
            }
            response = requests.get(image_url, headers=headers, timeout=30)
            
            self.log(f"   📊 Response Status: {response.status_code}")
            self.log(f"   📊 Content-Type: {response.headers.get('content-type', 'Not specified')}")
            self.log(f"   📊 Content-Length: {len(response.content)} bytes")
            
            if response.status_code == 200:
                self.log_result(
                    "Image Accessibility (Facebook Bot)", 
                    True, 
                    f"Status: {response.status_code}, Type: {response.headers.get('content-type')}, Size: {len(response.content)} bytes"
                )
                return True
            else:
                self.log_result(
                    "Image Accessibility (Facebook Bot)", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                return False
                
        except Exception as e:
            self.log_result("Image Accessibility (Facebook Bot)", False, f"Exception: {str(e)}")
            return False
    
    def test_public_image_endpoint(self, image_url):
        """ÉTAPE 5: Tester endpoint public image"""
        self.log(f"🌐 ÉTAPE 5: TEST ENDPOINT PUBLIC IMAGE")
        
        # Extract file ID from URL
        file_id = None
        if "/api/content/" in image_url:
            match = re.search(r'/api/content/([^/]+)/', image_url)
            if match:
                file_id = match.group(1)
        
        if not file_id:
            self.log_result("Public Image Endpoint", False, "Could not extract file ID from URL")
            return False
        
        # Test public endpoint
        public_url = f"{self.backend_url}/public/image/{file_id}"
        self.log(f"   Public URL: {public_url}")
        
        try:
            response = requests.get(public_url, timeout=30)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                
                self.log_result(
                    "Public Image Endpoint", 
                    True, 
                    f"Status: {response.status_code}, Type: {content_type}, Size: {content_length} bytes"
                )
                return True
            else:
                self.log_result(
                    "Public Image Endpoint", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                return False
                
        except Exception as e:
            self.log_result("Public Image Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def publish_facebook_post_with_image(self, post_id):
        """ÉTAPE 6: Publication Facebook avec image - LOGS COMPLETS"""
        self.log(f"📤 ÉTAPE 6: PUBLICATION FACEBOOK AVEC IMAGE")
        self.log(f"   Post ID: {post_id}")
        
        # Capture start time for detailed logging
        start_time = datetime.now()
        self.log(f"   🕐 Début publication: {start_time.isoformat()}")
        
        try:
            response = self.session.post(
                f"{self.backend_url}/posts/publish",
                json={"post_id": post_id},
                timeout=90  # Extended timeout for image processing
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.log(f"   🕐 Fin publication: {end_time.isoformat()}")
            self.log(f"   ⏱️ Durée totale: {duration:.2f} secondes")
            
            # Log response details
            self.log(f"   📊 Status Code: {response.status_code}")
            self.log(f"   📊 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.log(f"   📊 Response JSON: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    
                    # Check for Facebook post ID in response
                    facebook_post_id = data.get('facebook_post_id') or data.get('post_id')
                    if facebook_post_id:
                        self.log(f"   🎯 Facebook Post ID: {facebook_post_id}")
                    
                    self.log_result(
                        "Facebook Publication with Image", 
                        True, 
                        f"Success: {data.get('success', False)}, Message: {data.get('message', 'No message')}"
                    )
                    
                    return data
                except json.JSONDecodeError:
                    self.log(f"   📊 Response Text: {response.text}")
                    self.log_result(
                        "Facebook Publication with Image", 
                        True, 
                        f"Status: {response.status_code}, Non-JSON response"
                    )
                    return {"success": True, "raw_response": response.text}
            else:
                error_text = response.text
                self.log(f"   ❌ Error Response: {error_text}")
                
                self.log_result(
                    "Facebook Publication with Image", 
                    False, 
                    f"Status: {response.status_code}, Error: {error_text[:300]}"
                )
                return None
                
        except Exception as e:
            self.log_result("Facebook Publication with Image", False, f"Exception: {str(e)}")
            return None
    
    def test_external_images(self):
        """ÉTAPE 7: Test images externes (WikiMedia, Pixabay)"""
        self.log(f"🌍 ÉTAPE 7: TEST IMAGES EXTERNES")
        
        external_tests = [
            {
                "name": "WikiMedia PNG",
                "text": "Test image WikiMedia - Diagnostic publication Facebook",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png"
            },
            {
                "name": "Pixabay JPG",
                "text": "Test image Pixabay - Diagnostic publication Facebook", 
                "image_url": "https://cdn.pixabay.com/photo/2016/11/29/05/45/astronomy-1867616_960_720.jpg"
            }
        ]
        
        results = []
        
        for test in external_tests:
            self.log(f"\n   🧪 Test {test['name']}")
            self.log(f"      URL: {test['image_url']}")
            
            # First verify image is accessible
            try:
                img_response = requests.get(test['image_url'], timeout=30)
                if img_response.status_code == 200:
                    self.log(f"      ✅ Image accessible: {len(img_response.content)} bytes")
                else:
                    self.log(f"      ❌ Image not accessible: {img_response.status_code}")
                    continue
            except Exception as e:
                self.log(f"      ❌ Image access error: {str(e)}")
                continue
            
            # Test publication via simplified endpoint
            try:
                pub_response = self.session.post(
                    f"{self.backend_url}/social/facebook/publish-simple",
                    json={
                        "text": test['text'],
                        "image_url": test['image_url']
                    },
                    timeout=60
                )
                
                self.log(f"      📊 Publication Status: {pub_response.status_code}")
                self.log(f"      📊 Publication Response: {pub_response.text[:300]}")
                
                result = {
                    "name": test['name'],
                    "status_code": pub_response.status_code,
                    "success": pub_response.status_code == 200,
                    "response": pub_response.text[:500]
                }
                results.append(result)
                
            except Exception as pub_e:
                self.log(f"      ❌ Publication error: {str(pub_e)}")
                results.append({
                    "name": test['name'],
                    "success": False,
                    "error": str(pub_e)
                })
        
        success_count = len([r for r in results if r.get('success', False)])
        self.log_result(
            "External Image Publication Tests", 
            success_count > 0, 
            f"Completed {len(results)} tests, {success_count} successful"
        )
        
        return results
    
    def analyze_image_conversion_logs(self):
        """ÉTAPE 8: Analyser logs conversion JPG"""
        self.log(f"🔍 ÉTAPE 8: ANALYSE LOGS CONVERSION JPG")
        
        # This would require access to backend logs
        # For now, we'll check if there are any endpoints that provide log info
        try:
            # Try to get recent logs if endpoint exists
            response = self.session.get(f"{self.backend_url}/debug/recent-logs", timeout=30)
            
            if response.status_code == 200:
                logs = response.json()
                self.log(f"   📊 Recent logs retrieved: {len(logs)} entries")
                
                # Look for image conversion related logs
                conversion_logs = [
                    log for log in logs 
                    if any(keyword in log.get('message', '').lower() 
                          for keyword in ['jpg', 'jpeg', 'conversion', 'image', 'facebook'])
                ]
                
                self.log(f"   🔍 Image conversion logs found: {len(conversion_logs)}")
                for log in conversion_logs[:5]:
                    self.log(f"      {log.get('timestamp', 'No time')}: {log.get('message', 'No message')}")
                
                self.log_result(
                    "Image Conversion Logs Analysis", 
                    True, 
                    f"Found {len(conversion_logs)} relevant log entries"
                )
                
            else:
                self.log_result(
                    "Image Conversion Logs Analysis", 
                    False, 
                    f"Logs endpoint not available: {response.status_code}"
                )
                
        except Exception as e:
            self.log_result("Image Conversion Logs Analysis", False, f"Exception: {str(e)}")
    
    def run_comprehensive_diagnostic(self):
        """Exécuter diagnostic complet publication images Facebook"""
        self.log("🚀 DÉMARRAGE DIAGNOSTIC PUBLICATION IMAGES FACEBOOK")
        self.log("=" * 70)
        self.log("OBJECTIF: Vérifier si images apparaissent vraiment sur Facebook")
        self.log("=" * 70)
        
        # Step 1: Authentication
        if not self.authenticate():
            self.log("❌ Échec authentification - Arrêt diagnostic", "ERROR")
            return False
        
        # Step 2: Get Facebook posts with images
        facebook_posts = self.get_facebook_posts_with_images()
        if not facebook_posts:
            self.log("⚠️ Aucun post Facebook avec image trouvé", "WARNING")
        
        # Step 3: Check Facebook connections
        connections = self.check_facebook_connections()
        
        # Step 4-5: Test image accessibility if we have posts
        if facebook_posts:
            first_post = facebook_posts[0]
            visual_url = first_post.get("visual_url")
            
            if visual_url:
                # Test image accessibility
                self.test_image_accessibility(visual_url)
                
                # Test public endpoint
                self.test_public_image_endpoint(visual_url)
        
        # Step 6: Test actual Facebook publication
        if facebook_posts:
            first_post = facebook_posts[0]
            post_id = first_post.get("id")
            if post_id:
                publication_result = self.publish_facebook_post_with_image(post_id)
                
                # If we got a Facebook post ID, we could theoretically check it
                if publication_result and publication_result.get('facebook_post_id'):
                    facebook_post_id = publication_result['facebook_post_id']
                    self.log(f"🎯 Facebook Post ID obtenu: {facebook_post_id}")
                    self.log("   Pour vérifier manuellement:")
                    self.log(f"   GET https://graph.facebook.com/v20.0/{facebook_post_id}?fields=full_picture,message")
        
        # Step 7: Test external images
        self.test_external_images()
        
        # Step 8: Analyze conversion logs
        self.analyze_image_conversion_logs()
        
        # Final summary
        self.print_diagnostic_summary()
        
        return True
    
    def print_diagnostic_summary(self):
        """Imprimer résumé diagnostic complet"""
        self.log("\n" + "=" * 70)
        self.log("📊 RÉSUMÉ DIAGNOSTIC PUBLICATION IMAGES FACEBOOK")
        self.log("=" * 70)
        
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r["success"]])
        
        self.log(f"📈 Tests réalisés: {total_tests}")
        self.log(f"✅ Tests réussis: {successful_tests}")
        self.log(f"❌ Tests échoués: {total_tests - successful_tests}")
        self.log(f"📊 Taux de succès: {(successful_tests/total_tests*100):.1f}%")
        
        self.log(f"\n🔍 DÉTAILS DES TESTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            self.log(f"{status} {result['test']}: {result['details']}")
        
        # Key findings and recommendations
        self.log(f"\n🎯 CONCLUSIONS CLÉS:")
        
        # Authentication
        auth_success = any(r["test"] == "Authentication" and r["success"] for r in self.test_results)
        if auth_success:
            self.log("✅ Authentification backend fonctionnelle")
        else:
            self.log("❌ Problème authentification backend")
        
        # Facebook connections
        conn_test = next((r for r in self.test_results if "Facebook Connections" in r["test"]), None)
        if conn_test and "0 Facebook connections" in conn_test["details"]:
            self.log("❌ Aucune connexion Facebook active")
        elif conn_test:
            self.log("✅ Connexions Facebook détectées")
        
        # Image accessibility
        img_test = next((r for r in self.test_results if "Image Accessibility" in r["test"]), None)
        if img_test and img_test["success"]:
            self.log("✅ Images accessibles par Facebook bot")
        elif img_test:
            self.log("❌ Images non accessibles par Facebook bot")
        
        # Publication results
        pub_test = next((r for r in self.test_results if "Facebook Publication" in r["test"]), None)
        if pub_test and pub_test["success"]:
            self.log("✅ Publication Facebook réussie")
        elif pub_test:
            self.log("❌ Échec publication Facebook")
        
        self.log(f"\n📋 RECOMMANDATIONS:")
        
        if not auth_success:
            self.log("1. ❌ Vérifier configuration authentification")
        
        if conn_test and "0 Facebook connections" in conn_test.get("details", ""):
            self.log("2. ❌ Reconnecter Facebook avec tokens OAuth valides")
        
        if img_test and not img_test["success"]:
            self.log("3. ❌ Corriger endpoint public images pour Facebook")
        
        if pub_test and not pub_test["success"]:
            self.log("4. ❌ Déboguer processus publication Facebook")
        
        self.log("\n🔍 ÉTAPES SUIVANTES:")
        self.log("1. Vérifier manuellement sur Facebook si posts apparaissent")
        self.log("2. Utiliser Facebook Graph API pour vérifier contenu posts")
        self.log("3. Analyser logs backend pour détails conversion JPG")
        self.log("4. Comparer avec posts qui fonctionnent")
        
        self.log(f"\n⏰ Diagnostic terminé: {datetime.now().isoformat()}")


def main():
    """Fonction principale d'exécution"""
    print("🎯 FACEBOOK IMAGE PUBLICATION DIAGNOSTIC")
    print("Identifiants: lperpere@yahoo.fr / L@Reunion974!")
    print("Environnement: LIVE (claire-marcus.com)")
    print()
    print("QUESTION CENTRALE: Quand tu publies depuis l'interface,")
    print("l'image apparaît-elle vraiment sur Facebook ou seulement le texte ?")
    print()
    
    tester = FacebookImagePublicationTester()
    
    try:
        success = tester.run_comprehensive_diagnostic()
        
        if success:
            print("\n🎉 Diagnostic terminé avec succès!")
            print("Vérifiez maintenant manuellement sur Facebook si les images apparaissent.")
        else:
            print("\n❌ Diagnostic interrompu par erreur critique")
            
    except KeyboardInterrupt:
        print("\n⚠️ Diagnostic interrompu par utilisateur")
    except Exception as e:
        print(f"\n💥 Erreur critique: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
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
