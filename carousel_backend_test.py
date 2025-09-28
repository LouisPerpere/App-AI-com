#!/usr/bin/env python3
"""
TEST URGENT - Logique Caroussel et Attachement d'Images
Test spécifique pour les corrections récentes de création de carrousels
au lieu de remplacer les images existantes
"""

import requests
import json
import sys
import uuid
from datetime import datetime
import os

# Configuration
BACKEND_URL = "https://social-publisher-10.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class CarouselLogicTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        
    def authenticate(self):
        """Authentification avec les credentials fournis"""
        print("🔐 ÉTAPE 1: Authentification...")
        
        auth_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json=auth_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Configure headers for subsequent requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                })
                
                self.log_result("Authentication", True, f"User ID: {self.user_id}")
                return True
            else:
                self.log_result("Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_content_library(self):
        """Récupérer le contenu de la bibliothèque"""
        try:
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            if response.status_code == 200:
                data = response.json()
                return data.get("content", [])
            return []
        except Exception as e:
            print(f"❌ Erreur récupération bibliothèque: {e}")
            return []
    
    def get_generated_posts(self):
        """Récupérer les posts générés"""
        try:
            response = self.session.get(f"{BACKEND_URL}/posts/generated")
            if response.status_code == 200:
                data = response.json()
                return data.get("posts", [])
            return []
        except Exception as e:
            print(f"❌ Erreur récupération posts: {e}")
            return []
    
    def upload_test_image(self):
        """Upload une image de test pour les tests"""
        try:
            # Create a simple test image file
            test_image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
            
            # Remove Content-Type header for multipart upload
            headers = self.session.headers.copy()
            if 'Content-Type' in headers:
                del headers['Content-Type']
            
            files = {'files': ('test_carousel.png', test_image_content, 'image/png')}
            data = {'upload_type': 'single', 'attributed_month': 'decembre_2025'}
            
            response = self.session.post(
                f"{BACKEND_URL}/content/batch-upload",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                created_files = result.get("created", [])
                if created_files:
                    return created_files[0].get("id")
            else:
                print(f"❌ Upload failed: Status {response.status_code}, Response: {response.text}")
            return None
            
        except Exception as e:
            print(f"❌ Erreur upload image test: {e}")
            return None
    
    def test_1_post_with_existing_image_add_library(self):
        """Test 1: Post avec image existante + Ajout via Bibliothèque"""
        print("\n🧪 TEST 1: Post avec image existante + Ajout via Bibliothèque")
        
        # Étape 1: Trouver un post qui a déjà une image
        posts = self.get_generated_posts()
        post_with_image = None
        
        for post in posts:
            if post.get("visual_id") and post.get("visual_url") and not post.get("visual_id", "").startswith("carousel_"):
                post_with_image = post
                break
        
        if not post_with_image:
            self.log_result("Test 1 - Find post with image", False, "Aucun post avec image trouvé")
            return False
        
        post_id = post_with_image["id"]
        original_visual_id = post_with_image["visual_id"]
        original_visual_url = post_with_image["visual_url"]
        
        self.log_result("Test 1 - Find post with image", True, f"Post ID: {post_id}, Visual ID: {original_visual_id}")
        
        # Étape 2: Trouver une image différente dans la bibliothèque
        content_library = self.get_content_library()
        library_image = None
        
        for item in content_library:
            if item.get("id") != original_visual_id and item.get("file_type", "").startswith("image"):
                library_image = item
                break
        
        if not library_image:
            self.log_result("Test 1 - Find library image", False, "Aucune image différente trouvée dans la bibliothèque")
            return False
        
        library_image_id = library_image["id"]
        self.log_result("Test 1 - Find library image", True, f"Library Image ID: {library_image_id}")
        
        # Étape 3: Attacher l'image de la bibliothèque au post
        attach_data = {
            "image_source": "library",
            "image_id": library_image_id
        }
        
        try:
            response = self.session.put(
                f"{BACKEND_URL}/posts/{post_id}/attach-image",
                json=attach_data
            )
            
            if response.status_code == 200:
                result = response.json()
                new_visual_id = result.get("visual_id")
                new_visual_url = result.get("visual_url")
                
                self.log_result("Test 1 - Attach library image", True, f"New Visual ID: {new_visual_id}")
                
                # Vérification 1: visual_id devient "carousel_uuid"
                if new_visual_id and new_visual_id.startswith("carousel_"):
                    self.log_result("Test 1 - Visual ID becomes carousel", True, f"Carousel ID: {new_visual_id}")
                else:
                    self.log_result("Test 1 - Visual ID becomes carousel", False, f"Expected carousel_, got: {new_visual_id}")
                    return False
                
                # Vérification 2: Collection "carousels" contient le nouveau document
                carousel_id = new_visual_id
                carousel_response = self.session.get(f"{BACKEND_URL}/content/carousel/{carousel_id}")
                
                if carousel_response.status_code == 200:
                    carousel_data = carousel_response.json()
                    self.log_result("Test 1 - Carousel collection exists", True, f"Carousel found with {len(carousel_data.get('images', []))} images")
                    
                    # Vérification 3: Les deux images sont dans carousel.images[]
                    images = carousel_data.get("images", [])
                    if len(images) >= 2:
                        image_ids = [img.get("id") for img in images]
                        if original_visual_id in image_ids and library_image_id in image_ids:
                            self.log_result("Test 1 - Both images in carousel", True, f"Images: {image_ids}")
                        else:
                            self.log_result("Test 1 - Both images in carousel", False, f"Expected {original_visual_id} and {library_image_id}, got: {image_ids}")
                    else:
                        self.log_result("Test 1 - Both images in carousel", False, f"Expected 2+ images, got: {len(images)}")
                else:
                    self.log_result("Test 1 - Carousel collection exists", False, f"Status: {carousel_response.status_code}")
                    return False
                
                # Vérification 4: Le post garde son image visible (pas de point d'interrogation)
                if new_visual_url and "/carousel/" in new_visual_url:
                    self.log_result("Test 1 - Post keeps visible image", True, f"Visual URL: {new_visual_url}")
                else:
                    self.log_result("Test 1 - Post keeps visible image", False, f"Unexpected visual URL: {new_visual_url}")
                
                return True
                
            else:
                self.log_result("Test 1 - Attach library image", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Test 1 - Attach library image", False, f"Exception: {str(e)}")
            return False
    
    def test_2_post_with_existing_image_upload_new(self):
        """Test 2: Post avec image existante + Upload nouveau fichier"""
        print("\n🧪 TEST 2: Post avec image existante + Upload nouveau fichier")
        
        # Étape 1: Trouver un post qui a déjà une image (pas un carousel)
        posts = self.get_generated_posts()
        post_with_image = None
        
        for post in posts:
            visual_id = post.get("visual_id", "")
            if visual_id and post.get("visual_url") and not visual_id.startswith("carousel_"):
                post_with_image = post
                break
        
        if not post_with_image:
            self.log_result("Test 2 - Find post with image", False, "Aucun post avec image simple trouvé")
            return False
        
        post_id = post_with_image["id"]
        original_visual_id = post_with_image["visual_id"]
        
        self.log_result("Test 2 - Find post with image", True, f"Post ID: {post_id}, Visual ID: {original_visual_id}")
        
        # Étape 2: Upload un nouveau fichier (using working approach)
        try:
            test_image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
            
            # Remove Content-Type header for multipart upload
            headers = self.session.headers.copy()
            if 'Content-Type' in headers:
                del headers['Content-Type']
            
            files = {'files': ('test_carousel2.png', test_image_content, 'image/png')}
            data = {'upload_type': 'single', 'attributed_month': 'decembre_2025'}
            
            response = self.session.post(
                f"{BACKEND_URL}/content/batch-upload",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                created_files = result.get("created", [])
                if created_files:
                    uploaded_file_id = created_files[0].get("id")
                    self.log_result("Test 2 - Upload new file", True, f"Uploaded File ID: {uploaded_file_id}")
                else:
                    self.log_result("Test 2 - Upload new file", False, "No files in created array")
                    return False
            else:
                self.log_result("Test 2 - Upload new file", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Test 2 - Upload new file", False, f"Exception: {str(e)}")
            return False
        
        # Étape 3: Attacher le fichier uploadé au post
        attach_data = {
            "image_source": "upload",
            "uploaded_file_ids": [uploaded_file_id]
        }
        
        try:
            response = self.session.put(
                f"{BACKEND_URL}/posts/{post_id}/attach-image",
                json=attach_data
            )
            
            if response.status_code == 200:
                result = response.json()
                new_visual_id = result.get("visual_id")
                
                # Vérification: Création de carousel avec image existante + nouvelle uploadée
                if new_visual_id and new_visual_id.startswith("carousel_"):
                    self.log_result("Test 2 - Carousel created", True, f"Carousel ID: {new_visual_id}")
                    
                    # Vérifier le contenu du carousel
                    carousel_response = self.session.get(f"{BACKEND_URL}/content/carousel/{new_visual_id}")
                    
                    if carousel_response.status_code == 200:
                        carousel_data = carousel_response.json()
                        images = carousel_data.get("images", [])
                        
                        if len(images) >= 2:
                            image_ids = [img.get("id") for img in images]
                            if original_visual_id in image_ids and uploaded_file_id in image_ids:
                                self.log_result("Test 2 - Carousel contains both images", True, f"Images: {image_ids}")
                                return True
                            else:
                                self.log_result("Test 2 - Carousel contains both images", False, f"Expected {original_visual_id} and {uploaded_file_id}, got: {image_ids}")
                        else:
                            self.log_result("Test 2 - Carousel contains both images", False, f"Expected 2+ images, got: {len(images)}")
                    else:
                        self.log_result("Test 2 - Carousel verification", False, f"Status: {carousel_response.status_code}")
                else:
                    self.log_result("Test 2 - Carousel created", False, f"Expected carousel_, got: {new_visual_id}")
                
                return False
                
            else:
                self.log_result("Test 2 - Attach uploaded file", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Test 2 - Attach uploaded file", False, f"Exception: {str(e)}")
            return False
    
    def test_3_carousel_endpoint(self):
        """Test 3: Endpoint carrousel"""
        print("\n🧪 TEST 3: Endpoint carrousel")
        
        # Trouver un post avec un carousel
        posts = self.get_generated_posts()
        carousel_post = None
        
        for post in posts:
            visual_id = post.get("visual_id", "")
            if visual_id.startswith("carousel_"):
                carousel_post = post
                break
        
        if not carousel_post:
            self.log_result("Test 3 - Find carousel post", False, "Aucun post avec carousel trouvé")
            return False
        
        carousel_id = carousel_post["visual_id"]
        self.log_result("Test 3 - Find carousel post", True, f"Carousel ID: {carousel_id}")
        
        # Tester l'endpoint GET /api/content/carousel/{carousel_id}
        try:
            response = self.session.get(f"{BACKEND_URL}/content/carousel/{carousel_id}")
            
            if response.status_code == 200:
                carousel_data = response.json()
                
                # Vérifier la structure correcte
                required_fields = ["id", "type", "images"]
                missing_fields = [field for field in required_fields if field not in carousel_data]
                
                if not missing_fields:
                    images = carousel_data.get("images", [])
                    self.log_result("Test 3 - Carousel structure", True, f"Structure correcte avec {len(images)} images")
                    
                    # Vérifier que chaque image a les champs requis
                    if images:
                        first_image = images[0]
                        image_fields = ["id", "url"]
                        missing_image_fields = [field for field in image_fields if field not in first_image]
                        
                        if not missing_image_fields:
                            self.log_result("Test 3 - Image structure", True, f"Structure image correcte: {list(first_image.keys())}")
                            return True
                        else:
                            self.log_result("Test 3 - Image structure", False, f"Champs manquants: {missing_image_fields}")
                    else:
                        self.log_result("Test 3 - Images array", False, "Aucune image dans le carousel")
                else:
                    self.log_result("Test 3 - Carousel structure", False, f"Champs manquants: {missing_fields}")
            else:
                self.log_result("Test 3 - Carousel endpoint", False, f"Status: {response.status_code}, Response: {response.text}")
            
            return False
            
        except Exception as e:
            self.log_result("Test 3 - Carousel endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_4_post_without_image_normal_addition(self):
        """Test 4: Post sans image + Ajout normal"""
        print("\n🧪 TEST 4: Post sans image + Ajout normal")
        
        # Trouver un post sans image (status="needs_image")
        posts = self.get_generated_posts()
        post_without_image = None
        
        for post in posts:
            if post.get("status") == "needs_image" or not post.get("visual_id"):
                post_without_image = post
                break
        
        if not post_without_image:
            self.log_result("Test 4 - Find post without image", False, "Aucun post sans image trouvé")
            return False
        
        post_id = post_without_image["id"]
        self.log_result("Test 4 - Find post without image", True, f"Post ID: {post_id}")
        
        # Trouver une image dans la bibliothèque
        content_library = self.get_content_library()
        library_image = None
        
        for item in content_library:
            if item.get("file_type", "").startswith("image"):
                library_image = item
                break
        
        if not library_image:
            self.log_result("Test 4 - Find library image", False, "Aucune image trouvée dans la bibliothèque")
            return False
        
        library_image_id = library_image["id"]
        self.log_result("Test 4 - Find library image", True, f"Library Image ID: {library_image_id}")
        
        # Attacher l'image au post
        attach_data = {
            "image_source": "library",
            "image_id": library_image_id
        }
        
        try:
            response = self.session.put(
                f"{BACKEND_URL}/posts/{post_id}/attach-image",
                json=attach_data
            )
            
            if response.status_code == 200:
                result = response.json()
                new_visual_id = result.get("visual_id")
                
                # Vérification: Ça remplace normalement (pas de caroussel)
                if new_visual_id == library_image_id:
                    self.log_result("Test 4 - Normal replacement", True, f"Visual ID set to: {new_visual_id}")
                    return True
                elif new_visual_id and new_visual_id.startswith("carousel_"):
                    self.log_result("Test 4 - Normal replacement", False, f"Unexpected carousel creation: {new_visual_id}")
                else:
                    self.log_result("Test 4 - Normal replacement", False, f"Unexpected visual ID: {new_visual_id}")
            else:
                self.log_result("Test 4 - Attach image", False, f"Status: {response.status_code}, Response: {response.text}")
            
            return False
            
        except Exception as e:
            self.log_result("Test 4 - Attach image", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Exécuter tous les tests critiques"""
        print("🚀 DÉBUT DES TESTS CRITIQUES - LOGIQUE CAROUSSEL ET ATTACHEMENT D'IMAGES")
        print("=" * 80)
        
        if not self.authenticate():
            print("❌ Échec authentification - Arrêt des tests")
            return
        
        # Exécuter les 4 tests critiques
        test_1_success = self.test_1_post_with_existing_image_add_library()
        test_2_success = self.test_2_post_with_existing_image_upload_new()
        test_3_success = self.test_3_carousel_endpoint()
        test_4_success = self.test_4_post_without_image_normal_addition()
        
        # Résumé des résultats
        print("\n" + "=" * 80)
        print("📊 RÉSUMÉ DES TESTS CRITIQUES")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Tests réussis: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Détail des échecs
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print(f"\n❌ Tests échoués ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        # Tests critiques principaux
        critical_tests = [
            ("Test 1 - Carousel creation with library", test_1_success),
            ("Test 2 - Carousel creation with upload", test_2_success),
            ("Test 3 - Carousel endpoint", test_3_success),
            ("Test 4 - Normal replacement", test_4_success)
        ]
        
        print(f"\n🎯 TESTS CRITIQUES PRINCIPAUX:")
        for test_name, success in critical_tests:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   {status} {test_name}")
        
        critical_success_count = sum(1 for _, success in critical_tests if success)
        print(f"\n🏆 RÉSULTAT FINAL: {critical_success_count}/4 tests critiques réussis")
        
        if critical_success_count == 4:
            print("🎉 TOUS LES TESTS CRITIQUES SONT PASSÉS - LOGIQUE CAROUSSEL OPÉRATIONNELLE")
        else:
            print("⚠️ CERTAINS TESTS CRITIQUES ONT ÉCHOUÉ - CORRECTIONS REQUISES")

if __name__ == "__main__":
    tester = CarouselLogicTester()
    tester.run_all_tests()