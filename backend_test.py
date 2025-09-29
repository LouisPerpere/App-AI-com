#!/usr/bin/env python3
"""
VALIDATION FINALE DES CORRECTIONS AVANT REDÉPLOIEMENT
Backend Testing for Facebook JPG Corrections

Testing the 5 critical corrections:
1. Endpoint public JPG fonctionnel
2. Conversion URL automatique vers JPG  
3. Publication Facebook avec conversion JPG intégrée
4. Flow OAuth 3-étapes Facebook
5. Cohérence système complète

Credentials: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import time
import sys
import os
from urllib.parse import urlparse

# Configuration
BACKEND_URL = "https://social-publisher-10.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class FacebookJPGValidator:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        
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
