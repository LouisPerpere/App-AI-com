#!/usr/bin/env python3
"""
Test complet du système après les corrections d'ID et de fichiers statiques
Testing the complete system after ID and static file corrections as requested in French review

Tests à effectuer:
1. Authentifier avec lperpere@yahoo.fr / L@Reunion974!
2. Tester GET /api/content/pending pour vérifier que les ID retournés sont bien des ObjectId MongoDB
3. Tester PUT /api/content/{file_id}/description avec un ObjectId MongoDB pour vérifier la compatibilité
4. Tester DELETE /api/content/{file_id} avec un ObjectId MongoDB et vérifier que deleted_count = 1
5. Tester POST /api/content/batch-upload pour un nouveau fichier et vérifier qu'il retourne un ObjectId MongoDB
6. Tester l'accessibilité des vignettes via GET /uploads/thumbs/{filename}.webp
7. Vérifier que les headers de cache sont corrects (no-cache pour API, cache pour vignettes)
8. Compter le nombre final de fichiers pour voir si la discordance 36 vs 7 est résolue
"""

import requests
import json
import os
import time
import base64
from io import BytesIO
from PIL import Image
import re

# Configuration
BACKEND_URL = "https://instamanager-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials as specified in review request
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class MongoDBIDFixTester:
    def __init__(self):
        self.session = requests.Session()
        # Disable SSL verification for testing in container environment
        self.session.verify = False
        # Disable SSL warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        self.access_token = None
        self.user_id = None
        self.test_results = []
        self.uploaded_file_id = None
        self.uploaded_filename = None
        
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
    
    def is_mongodb_objectid(self, id_string):
        """Check if string is a valid MongoDB ObjectId (24 hex characters)"""
        if not id_string or not isinstance(id_string, str):
            return False
        return len(id_string) == 24 and re.match(r'^[0-9a-fA-F]{24}$', id_string) is not None
    
    def authenticate(self):
        """1. Authentifier avec lperpere@yahoo.fr / L@Reunion974!"""
        print("🔐 TEST 1: Authentication avec lperpere@yahoo.fr / L@Reunion974!")
        print("=" * 70)
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                self.log_result(
                    "Authentication", 
                    True, 
                    f"Authentification réussie pour {TEST_EMAIL}, User ID: {self.user_id}"
                )
                return True
            else:
                self.log_result(
                    "Authentication", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, error=str(e))
            return False
    
    def test_get_content_pending_objectids(self):
        """2. Tester GET /api/content/pending pour vérifier que les ID retournés sont bien des ObjectId MongoDB"""
        print("📋 TEST 2: GET /api/content/pending - Vérification des ObjectId MongoDB")
        print("=" * 70)
        
        try:
            response = self.session.get(f"{API_BASE}/content/pending?limit=10")
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                total = data.get("total", 0)
                
                # Check cache headers
                cache_control = response.headers.get('Cache-Control', '')
                has_no_cache = 'no-cache' in cache_control or 'no-store' in cache_control
                
                # Verify ObjectIds
                objectid_count = 0
                uuid_count = 0
                invalid_count = 0
                
                for item in content:
                    item_id = item.get("id", "")
                    if self.is_mongodb_objectid(item_id):
                        objectid_count += 1
                    elif len(item_id) == 36 and item_id.count('-') == 4:  # UUID format
                        uuid_count += 1
                    else:
                        invalid_count += 1
                
                success = objectid_count > 0 and uuid_count == 0 and invalid_count == 0
                
                self.log_result(
                    "GET /api/content/pending ObjectId Check", 
                    success, 
                    f"Total fichiers: {total}, Chargés: {len(content)}, ObjectIds: {objectid_count}, UUIDs: {uuid_count}, Invalides: {invalid_count}, Headers no-cache: {has_no_cache}"
                )
                
                # Store first ObjectId for later tests
                if content and objectid_count > 0:
                    self.existing_file_id = content[0].get("id")
                    self.existing_filename = content[0].get("filename", "")
                    print(f"   Premier fichier ID pour tests suivants: {self.existing_file_id}")
                
                return success
            else:
                self.log_result(
                    "GET /api/content/pending ObjectId Check", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("GET /api/content/pending ObjectId Check", False, error=str(e))
            return False
    
    def test_put_description_with_objectid(self):
        """3. Tester PUT /api/content/{file_id}/description avec un ObjectId MongoDB pour vérifier la compatibilité"""
        print("✏️ TEST 3: PUT /api/content/{file_id}/description avec ObjectId MongoDB")
        print("=" * 70)
        
        if not hasattr(self, 'existing_file_id') or not self.existing_file_id:
            self.log_result(
                "PUT description avec ObjectId", 
                False, 
                "Aucun ObjectId disponible du test précédent"
            )
            return False
        
        try:
            test_description = f"Test description mise à jour - {int(time.time())}"
            
            response = self.session.put(
                f"{API_BASE}/content/{self.existing_file_id}/description",
                json={"description": test_description}
            )
            
            if response.status_code == 200:
                data = response.json()
                returned_file_id = data.get("file_id", "")
                returned_description = data.get("description", "")
                
                # Verify returned ID is still ObjectId
                is_objectid = self.is_mongodb_objectid(returned_file_id)
                description_matches = returned_description == test_description
                
                success = is_objectid and description_matches
                
                self.log_result(
                    "PUT description avec ObjectId", 
                    success, 
                    f"File ID retourné: {returned_file_id} (ObjectId: {is_objectid}), Description mise à jour: {description_matches}"
                )
                return success
            else:
                self.log_result(
                    "PUT description avec ObjectId", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("PUT description avec ObjectId", False, error=str(e))
            return False
    
    def create_test_image(self):
        """Create a test image for upload"""
        img = Image.new('RGB', (800, 600), color='red')
        
        try:
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            draw.text((50, 50), f"Test Upload {int(time.time())}", fill='white')
        except:
            pass
        
        img_buffer = BytesIO()
        img.save(img_buffer, format='JPEG', quality=90)
        img_buffer.seek(0)
        
        return img_buffer.getvalue()
    
    def test_batch_upload_returns_objectid(self):
        """5. Tester POST /api/content/batch-upload pour un nouveau fichier et vérifier qu'il retourne un ObjectId MongoDB"""
        print("📤 TEST 5: POST /api/content/batch-upload - Vérification ObjectId retourné")
        print("=" * 70)
        
        try:
            test_image_data = self.create_test_image()
            
            files = {
                'files': ('test_objectid_upload.jpg', test_image_data, 'image/jpeg')
            }
            
            response = self.session.post(f"{API_BASE}/content/batch-upload", files=files)
            
            if response.status_code == 200:
                data = response.json()
                uploaded_files = data.get("uploaded_files", [])
                
                if uploaded_files:
                    self.uploaded_file_id = uploaded_files[0].get("id")
                    self.uploaded_filename = uploaded_files[0].get("stored_name")
                    
                    # Verify returned ID is ObjectId
                    is_objectid = self.is_mongodb_objectid(self.uploaded_file_id)
                    
                    self.log_result(
                        "POST batch-upload ObjectId Check", 
                        is_objectid, 
                        f"Fichier uploadé avec ID: {self.uploaded_file_id} (ObjectId: {is_objectid}), Filename: {self.uploaded_filename}"
                    )
                    
                    # Wait for background processing
                    print("⏳ Attente 3 secondes pour génération thumbnail...")
                    time.sleep(3)
                    
                    return is_objectid
                else:
                    self.log_result(
                        "POST batch-upload ObjectId Check", 
                        False, 
                        "Aucun fichier uploadé"
                    )
                    return False
            else:
                self.log_result(
                    "POST batch-upload ObjectId Check", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("POST batch-upload ObjectId Check", False, error=str(e))
            return False
    
    def test_delete_with_objectid(self):
        """4. Tester DELETE /api/content/{file_id} avec un ObjectId MongoDB et vérifier que deleted_count = 1"""
        print("🗑️ TEST 4: DELETE /api/content/{file_id} avec ObjectId et vérification deleted_count")
        print("=" * 70)
        
        if not hasattr(self, 'uploaded_file_id') or not self.uploaded_file_id:
            self.log_result(
                "DELETE avec ObjectId", 
                False, 
                "Aucun fichier uploadé disponible pour suppression"
            )
            return False
        
        try:
            response = self.session.delete(f"{API_BASE}/content/{self.uploaded_file_id}")
            
            if response.status_code == 200:
                data = response.json()
                deleted_count = data.get("deleted_count", 0)
                returned_file_id = data.get("file_id", "")
                
                # Verify deleted_count = 1 and returned ID is ObjectId
                is_objectid = self.is_mongodb_objectid(returned_file_id)
                correct_count = deleted_count == 1
                
                success = is_objectid and correct_count
                
                self.log_result(
                    "DELETE avec ObjectId", 
                    success, 
                    f"Deleted count: {deleted_count} (attendu: 1), File ID retourné: {returned_file_id} (ObjectId: {is_objectid})"
                )
                return success
            else:
                self.log_result(
                    "DELETE avec ObjectId", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("DELETE avec ObjectId", False, error=str(e))
            return False
    
    def test_thumbnail_accessibility(self):
        """6. Tester l'accessibilité des vignettes via GET /uploads/thumbs/{filename}.webp"""
        print("🖼️ TEST 6: Accessibilité des vignettes /uploads/thumbs/{filename}.webp")
        print("=" * 70)
        
        # First, get a list of files to find one with a thumbnail
        try:
            response = self.session.get(f"{API_BASE}/content/pending?limit=5")
            
            if response.status_code != 200:
                self.log_result(
                    "Thumbnail Accessibility", 
                    False, 
                    "Impossible de récupérer la liste des fichiers"
                )
                return False
            
            data = response.json()
            content = data.get("content", [])
            
            if not content:
                self.log_result(
                    "Thumbnail Accessibility", 
                    False, 
                    "Aucun fichier disponible pour test thumbnail"
                )
                return False
            
            # Try to access thumbnail for first file
            first_file = content[0]
            filename = first_file.get("filename", "")
            
            if not filename:
                self.log_result(
                    "Thumbnail Accessibility", 
                    False, 
                    "Nom de fichier manquant"
                )
                return False
            
            # Build thumbnail URL
            base_filename = os.path.splitext(filename)[0]
            thumbnail_url = f"{BACKEND_URL}/uploads/thumbs/{base_filename}.webp"
            
            print(f"🔗 Test URL thumbnail: {thumbnail_url}")
            
            # Test thumbnail accessibility
            thumb_response = requests.get(thumbnail_url)
            
            if thumb_response.status_code == 200:
                # Check cache headers for thumbnails
                cache_control = thumb_response.headers.get('Cache-Control', '')
                has_cache = 'max-age' in cache_control or 'public' in cache_control
                
                # Verify it's an image
                content_type = thumb_response.headers.get('content-type', '')
                is_image = 'image' in content_type.lower()
                
                success = is_image
                
                self.log_result(
                    "Thumbnail Accessibility", 
                    success, 
                    f"Thumbnail accessible: {thumbnail_url}, Content-Type: {content_type}, Cache headers: {has_cache}, Cache-Control: {cache_control}"
                )
                return success
            else:
                self.log_result(
                    "Thumbnail Accessibility", 
                    False, 
                    f"Thumbnail non accessible. Status: {thumb_response.status_code}",
                    f"URL: {thumbnail_url}"
                )
                return False
                
        except Exception as e:
            self.log_result("Thumbnail Accessibility", False, error=str(e))
            return False
    
    def test_cache_headers(self):
        """7. Vérifier que les headers de cache sont corrects (no-cache pour API, cache pour vignettes)"""
        print("🔄 TEST 7: Vérification des headers de cache")
        print("=" * 70)
        
        try:
            # Test API endpoint cache headers (should be no-cache)
            api_response = self.session.get(f"{API_BASE}/content/pending?limit=1")
            api_cache = api_response.headers.get('Cache-Control', '')
            api_no_cache = 'no-cache' in api_cache or 'no-store' in api_cache
            
            # Test thumbnail cache headers (should have cache)
            # First get a file to test thumbnail
            if api_response.status_code == 200:
                data = api_response.json()
                content = data.get("content", [])
                
                thumbnail_cache_ok = True  # Default to true if no thumbnails to test
                
                if content:
                    filename = content[0].get("filename", "")
                    if filename:
                        base_filename = os.path.splitext(filename)[0]
                        thumbnail_url = f"{BACKEND_URL}/uploads/thumbs/{base_filename}.webp"
                        
                        thumb_response = requests.get(thumbnail_url)
                        if thumb_response.status_code == 200:
                            thumb_cache = thumb_response.headers.get('Cache-Control', '')
                            thumbnail_cache_ok = 'max-age' in thumb_cache or 'public' in thumb_cache
                
                success = api_no_cache and thumbnail_cache_ok
                
                self.log_result(
                    "Cache Headers Verification", 
                    success, 
                    f"API no-cache: {api_no_cache} (Cache-Control: {api_cache}), Thumbnail cache: {thumbnail_cache_ok}"
                )
                return success
            else:
                self.log_result(
                    "Cache Headers Verification", 
                    False, 
                    "Impossible de tester les headers de cache"
                )
                return False
                
        except Exception as e:
            self.log_result("Cache Headers Verification", False, error=str(e))
            return False
    
    def test_file_count_discrepancy(self):
        """8. Compter le nombre final de fichiers pour voir si la discordance 36 vs 7 est résolue"""
        print("📊 TEST 8: Comptage final des fichiers - Résolution discordance 36 vs 7")
        print("=" * 70)
        
        try:
            # Get total count from API
            response = self.session.get(f"{API_BASE}/content/pending?limit=1")
            
            if response.status_code == 200:
                data = response.json()
                api_total = data.get("total", 0)
                
                # Get a larger sample to verify consistency
                large_response = self.session.get(f"{API_BASE}/content/pending?limit=100")
                
                if large_response.status_code == 200:
                    large_data = large_response.json()
                    loaded_count = len(large_data.get("content", []))
                    reported_total = large_data.get("total", 0)
                    
                    # Check consistency
                    counts_match = api_total == reported_total
                    reasonable_count = api_total > 0 and api_total < 1000  # Sanity check
                    
                    success = counts_match and reasonable_count
                    
                    self.log_result(
                        "File Count Discrepancy Check", 
                        success, 
                        f"Total fichiers API: {api_total}, Fichiers chargés: {loaded_count}, Cohérence: {counts_match}, Nombre raisonnable: {reasonable_count}"
                    )
                    
                    # Additional info about the discrepancy resolution
                    if api_total != 36 and api_total != 7:
                        print(f"   ℹ️ Nouveau total: {api_total} (différent de 36 et 7 - potentiellement résolu)")
                    elif api_total == 36:
                        print(f"   ⚠️ Total toujours à 36 - discordance peut persister")
                    elif api_total == 7:
                        print(f"   ⚠️ Total maintenant à 7 - vérifier si c'est le bon nombre")
                    
                    return success
                else:
                    self.log_result(
                        "File Count Discrepancy Check", 
                        False, 
                        f"Erreur lors du test étendu. Status: {large_response.status_code}"
                    )
                    return False
            else:
                self.log_result(
                    "File Count Discrepancy Check", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("File Count Discrepancy Check", False, error=str(e))
            return False
    
    def run_all_tests(self):
        """Run all MongoDB ID fix tests as requested in French review"""
        print("🚀 TEST COMPLET SYSTÈME APRÈS CORRECTIONS ID ET FICHIERS STATIQUES")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Utilisateur test: {TEST_EMAIL}")
        print("=" * 80)
        print()
        
        # Initialize test variables
        self.existing_file_id = None
        self.existing_filename = None
        self.uploaded_file_id = None
        self.uploaded_filename = None
        
        # Run tests in the order specified in the review
        tests = [
            self.authenticate,                          # 1. Authentication
            self.test_get_content_pending_objectids,    # 2. GET /api/content/pending ObjectIds
            self.test_put_description_with_objectid,    # 3. PUT description with ObjectId
            self.test_batch_upload_returns_objectid,    # 5. POST batch-upload ObjectId (before delete)
            self.test_delete_with_objectid,             # 4. DELETE with ObjectId
            self.test_thumbnail_accessibility,          # 6. Thumbnail accessibility
            self.test_cache_headers,                    # 7. Cache headers
            self.test_file_count_discrepancy           # 8. File count discrepancy
        ]
        
        for test in tests:
            if not test():
                print("❌ Test échoué, continuation avec les tests restants...")
            print()
        
        # Summary
        print("📋 RÉSUMÉ DES TESTS")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Réussis: {passed}")
        print(f"Échoués: {total - passed}")
        print(f"Taux de réussite: {success_rate:.1f}%")
        print()
        
        # Detailed results
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
            if result['error']:
                print(f"   Erreur: {result['error']}")
        
        print()
        print("🎯 TESTS CORRECTIONS ID ET FICHIERS STATIQUES TERMINÉS")
        
        # Specific conclusions for the review
        print("\n🔍 CONCLUSIONS POUR LA REVIEW:")
        print("=" * 50)
        
        objectid_tests = [r for r in self.test_results if "ObjectId" in r["test"]]
        objectid_success = all(r["success"] for r in objectid_tests)
        
        if objectid_success:
            print("✅ CORRECTION ID: Les ObjectId MongoDB sont correctement utilisés")
        else:
            print("❌ CORRECTION ID: Problèmes persistants avec les ObjectId MongoDB")
        
        cache_tests = [r for r in self.test_results if "Cache" in r["test"] or "Thumbnail" in r["test"]]
        cache_success = all(r["success"] for r in cache_tests)
        
        if cache_success:
            print("✅ FICHIERS STATIQUES: Headers de cache et accessibilité OK")
        else:
            print("❌ FICHIERS STATIQUES: Problèmes avec headers de cache ou accessibilité")
        
        return success_rate >= 75  # Consider successful if 75% or more tests pass

if __name__ == "__main__":
    tester = MongoDBIDFixTester()
    success = tester.run_all_tests()
    
    if success:
        print("✅ Tests globaux: SUCCÈS")
        exit(0)
    else:
        print("❌ Tests globaux: ÉCHEC")
        exit(1)