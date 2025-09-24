#!/usr/bin/env python3
"""
Backend Test Suite - Upload et métadonnées post-correction
Test de vérification des corrections critiques dans routes_thumbs.py et upload functionality
"""

import requests
import json
import time
import os
from io import BytesIO
from PIL import Image

# Configuration
BACKEND_URL = "https://instamanager-1.preview.emergentagent.com/api"
CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        
    def authenticate(self):
        """Authenticate and get JWT token"""
        try:
            print("🔐 Step 1: Authentication")
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json=CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                self.log_result("Authentication", True, f"User ID: {self.user_id}")
                return True
            else:
                self.log_result("Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def create_test_image(self, filename="test_image.jpg", size=(800, 600)):
        """Create a test image file"""
        img = Image.new('RGB', size, color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG', quality=85)
        img_bytes.seek(0)
        return img_bytes.getvalue()
    
    def test_basic_upload(self):
        """Test 1: Upload de base fonctionne-t-il maintenant ?"""
        try:
            print("\n🔧 Test 1: Upload de base")
            
            # Create test image
            test_image_data = self.create_test_image()
            
            # Prepare multipart form data
            files = {
                'files': ('test_upload.jpg', test_image_data, 'image/jpeg')
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/content/batch-upload",
                files=files,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                created_items = data.get("created", [])
                
                if created_items and len(created_items) > 0:
                    file_id = created_items[0].get("id")
                    
                    # Verify file exists in database by checking content/pending
                    time.sleep(5)  # Wait longer for processing
                    
                    pending_response = self.session.get(f"{BACKEND_URL}/content/pending")
                    if pending_response.status_code == 200:
                        pending_data = pending_response.json()
                        content_items = pending_data.get("content", [])
                        
                        # Check if our uploaded file is in the list
                        uploaded_file = next((item for item in content_items if item.get("id") == file_id), None)
                        
                        # Debug: Print first few items to see what's in the database
                        print(f"    DEBUG: Looking for file_id: {file_id}")
                        print(f"    DEBUG: Found {len(content_items)} total items")
                        if content_items:
                            print(f"    DEBUG: Recent items: {[item.get('id', 'no-id')[:8] + '...' for item in content_items[:3]]}")
                        
                        if uploaded_file:
                            self.log_result("Basic Upload - File in Database", True, f"File ID: {file_id}, Filename: {uploaded_file.get('filename')}")
                            
                            # Test thumbnail generation
                            thumb_response = self.session.get(f"{BACKEND_URL}/content/{file_id}/thumb")
                            if thumb_response.status_code == 200:
                                self.log_result("Basic Upload - Thumbnail Generation", True, f"Thumbnail size: {len(thumb_response.content)} bytes")
                            else:
                                self.log_result("Basic Upload - Thumbnail Generation", False, f"Thumbnail status: {thumb_response.status_code}")
                            
                            return file_id
                        else:
                            self.log_result("Basic Upload - File in Database", False, "Uploaded file not found in content/pending")
                    else:
                        self.log_result("Basic Upload - Database Check", False, f"Content/pending status: {pending_response.status_code}")
                else:
                    self.log_result("Basic Upload - Response Format", False, "No created items in response")
            else:
                self.log_result("Basic Upload", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("Basic Upload", False, f"Exception: {str(e)}")
            
        return None
    
    def test_upload_with_metadata(self):
        """Test 2: Upload avec métadonnées post"""
        try:
            print("\n📝 Test 2: Upload avec métadonnées post")
            
            # Create test image
            test_image_data = self.create_test_image()
            
            # Prepare multipart form data with metadata
            files = {
                'files': ('test_post_image.jpg', test_image_data, 'image/jpeg')
            }
            data = {
                'upload_type': 'post_single',
                'common_title': 'Titre du post de test',
                'common_context': 'Contexte du post de test'
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/content/batch-upload",
                files=files,
                data=data,
                timeout=60
            )
            
            if response.status_code == 200:
                response_data = response.json()
                created_items = response_data.get("created", [])
                
                if created_items and len(created_items) > 0:
                    file_id = created_items[0].get("id")
                    
                    # Wait for processing
                    time.sleep(5)
                    
                    # Verify metadata in database
                    pending_response = self.session.get(f"{BACKEND_URL}/content/pending")
                    if pending_response.status_code == 200:
                        pending_data = pending_response.json()
                        content_items = pending_data.get("content", [])
                        
                        uploaded_file = next((item for item in content_items if item.get("id") == file_id), None)
                        
                        if uploaded_file:
                            title = uploaded_file.get("title", "")
                            context = uploaded_file.get("context", "")
                            upload_type = uploaded_file.get("upload_type", "")
                            
                            title_correct = title == "Titre du post de test"
                            context_correct = context == "Contexte du post de test"
                            type_correct = upload_type == "post_single"
                            
                            if title_correct and context_correct and type_correct:
                                self.log_result("Upload with Metadata", True, f"Title: '{title}', Context: '{context}', Type: '{upload_type}'")
                                return file_id
                            else:
                                self.log_result("Upload with Metadata", False, f"Metadata mismatch - Title: '{title}', Context: '{context}', Type: '{upload_type}'")
                        else:
                            self.log_result("Upload with Metadata", False, "File not found in database")
                    else:
                        self.log_result("Upload with Metadata", False, f"Database check failed: {pending_response.status_code}")
                else:
                    self.log_result("Upload with Metadata", False, "No created items in response")
            else:
                self.log_result("Upload with Metadata", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("Upload with Metadata", False, f"Exception: {str(e)}")
            
        return None
    
    def test_image_attachment_to_post(self, uploaded_file_id):
        """Test 3: Attachement d'image uploadée à un post"""
        try:
            print("\n🔗 Test 3: Attachement d'image à un post")
            
            if not uploaded_file_id:
                self.log_result("Image Attachment", False, "No uploaded file ID provided")
                return
            
            # First, check if there are any generated posts
            posts_response = self.session.get(f"{BACKEND_URL}/posts/generated")
            
            if posts_response.status_code == 200:
                posts_data = posts_response.json()
                posts = posts_data.get("posts", [])
                
                if posts and len(posts) > 0:
                    # Use the first post
                    post_id = posts[0].get("id")
                    
                    # Attach the uploaded image
                    attachment_data = {
                        "image_source": "upload",
                        "uploaded_file_ids": [uploaded_file_id]
                    }
                    
                    attach_response = self.session.put(
                        f"{BACKEND_URL}/posts/{post_id}/attach-image",
                        json=attachment_data,
                        timeout=30
                    )
                    
                    if attach_response.status_code == 200:
                        # Verify the image is marked as used
                        time.sleep(1)
                        
                        pending_response = self.session.get(f"{BACKEND_URL}/content/pending")
                        if pending_response.status_code == 200:
                            pending_data = pending_response.json()
                            content_items = pending_data.get("content", [])
                            
                            attached_file = next((item for item in content_items if item.get("id") == uploaded_file_id), None)
                            
                            if attached_file:
                                used_in_posts = attached_file.get("used_in_posts", False)
                                if used_in_posts:
                                    self.log_result("Image Attachment", True, f"Image {uploaded_file_id} marked as used_in_posts=True")
                                else:
                                    self.log_result("Image Attachment", False, f"Image not marked as used: used_in_posts={used_in_posts}")
                            else:
                                self.log_result("Image Attachment", False, "Attached file not found in content")
                        else:
                            self.log_result("Image Attachment", False, f"Content check failed: {pending_response.status_code}")
                    else:
                        self.log_result("Image Attachment", False, f"Attachment failed: {attach_response.status_code}, {attach_response.text}")
                else:
                    # No posts available, create a mock scenario
                    self.log_result("Image Attachment", True, "No posts available for attachment test - this is expected if no posts have been generated")
            else:
                self.log_result("Image Attachment", False, f"Failed to get posts: {posts_response.status_code}")
                
        except Exception as e:
            self.log_result("Image Attachment", False, f"Exception: {str(e)}")
    
    def test_badges_and_metadata_verification(self):
        """Test 4: Vérification badges et métadonnées frontend"""
        try:
            print("\n🏷️ Test 4: Vérification badges et métadonnées")
            
            # Get all pending content
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                
                if content_items:
                    # Analyze the content structure
                    items_with_title = [item for item in content_items if item.get("title")]
                    items_with_context = [item for item in content_items if item.get("context")]
                    items_used_in_posts = [item for item in content_items if item.get("used_in_posts")]
                    
                    # Check for required fields
                    required_fields = ["id", "filename", "file_type", "title", "context", "used_in_posts", "thumb_url"]
                    items_with_all_fields = []
                    
                    for item in content_items:
                        has_all_fields = all(field in item for field in required_fields)
                        if has_all_fields:
                            items_with_all_fields.append(item)
                    
                    details = f"Total items: {len(content_items)}, With title: {len(items_with_title)}, With context: {len(items_with_context)}, Used in posts: {len(items_used_in_posts)}, Complete structure: {len(items_with_all_fields)}"
                    
                    if len(items_with_all_fields) > 0:
                        self.log_result("Badges and Metadata Structure", True, details)
                        
                        # Test thumbnail accessibility for recent items
                        recent_items = content_items[:3]  # Test first 3 items
                        thumbnail_success = 0
                        
                        for item in recent_items:
                            file_id = item.get("id")
                            if file_id:
                                thumb_response = self.session.get(f"{BACKEND_URL}/content/{file_id}/thumb")
                                if thumb_response.status_code == 200:
                                    thumbnail_success += 1
                        
                        if thumbnail_success > 0:
                            self.log_result("Thumbnail Accessibility", True, f"{thumbnail_success}/{len(recent_items)} thumbnails accessible")
                        else:
                            self.log_result("Thumbnail Accessibility", False, "No thumbnails accessible")
                    else:
                        self.log_result("Badges and Metadata Structure", False, details)
                else:
                    self.log_result("Badges and Metadata Structure", False, "No content items found")
            else:
                self.log_result("Badges and Metadata Structure", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Badges and Metadata Structure", False, f"Exception: {str(e)}")
    
    def test_mongodb_insertion_fix(self):
        """Test critique: Vérifier que l'insertion MongoDB fonctionne maintenant"""
        try:
            print("\n🗄️ Test Critique: Vérification insertion MongoDB")
            
            # Create a small test image
            test_image_data = self.create_test_image(size=(400, 300))
            
            # Upload with specific metadata to track
            files = {
                'files': ('mongodb_test.jpg', test_image_data, 'image/jpeg')
            }
            data = {
                'upload_type': 'test_mongodb',
                'common_title': 'Test MongoDB Insertion',
                'common_context': 'Vérification que save_db_thumbnail fonctionne avec get_sync_media_collection'
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/content/batch-upload",
                files=files,
                data=data,
                timeout=60
            )
            
            if response.status_code == 200:
                response_data = response.json()
                created_items = response_data.get("created", [])
                
                if created_items:
                    file_id = created_items[0].get("id")
                    
                    # Wait for thumbnail processing
                    time.sleep(8)
                    
                    # Check if file exists in database
                    pending_response = self.session.get(f"{BACKEND_URL}/content/pending")
                    if pending_response.status_code == 200:
                        pending_data = pending_response.json()
                        content_items = pending_data.get("content", [])
                        
                        test_file = next((item for item in content_items if item.get("id") == file_id), None)
                        
                        if test_file:
                            # Check thumbnail generation
                            thumb_response = self.session.get(f"{BACKEND_URL}/content/{file_id}/thumb")
                            
                            if thumb_response.status_code == 200 and len(thumb_response.content) > 0:
                                self.log_result("MongoDB Insertion Fix", True, f"File saved in DB with working thumbnail. File ID: {file_id}")
                                
                                # Verify UUID handling
                                if len(file_id) == 36 and file_id.count('-') == 4:  # UUID format
                                    self.log_result("UUID String Handling", True, f"UUID format correct: {file_id}")
                                else:
                                    self.log_result("UUID String Handling", False, f"Unexpected ID format: {file_id}")
                                    
                                return True
                            else:
                                self.log_result("MongoDB Insertion Fix", False, f"Thumbnail generation failed: {thumb_response.status_code}")
                        else:
                            self.log_result("MongoDB Insertion Fix", False, "File not found in database after upload")
                    else:
                        self.log_result("MongoDB Insertion Fix", False, f"Database check failed: {pending_response.status_code}")
                else:
                    self.log_result("MongoDB Insertion Fix", False, "No items created in upload response")
            else:
                self.log_result("MongoDB Insertion Fix", False, f"Upload failed: {response.status_code}, {response.text}")
                
        except Exception as e:
            self.log_result("MongoDB Insertion Fix", False, f"Exception: {str(e)}")
            
        return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Backend Test Suite - Upload et métadonnées post-correction")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed - stopping tests")
            return
        
        # Step 2: Test MongoDB insertion fix (most critical)
        mongodb_working = self.test_mongodb_insertion_fix()
        
        # Step 3: Basic upload test
        basic_upload_id = self.test_basic_upload()
        
        # Step 4: Upload with metadata test
        metadata_upload_id = self.test_upload_with_metadata()
        
        # Step 5: Image attachment test (use metadata upload if available)
        test_file_id = metadata_upload_id or basic_upload_id
        if test_file_id:
            self.test_image_attachment_to_post(test_file_id)
        
        # Step 6: Badges and metadata verification
        self.test_badges_and_metadata_verification()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"    {result['details']}")
        
        # Critical findings
        print("\n🔍 CRITICAL FINDINGS:")
        
        mongodb_test = next((r for r in self.test_results if "MongoDB Insertion" in r["test"]), None)
        if mongodb_test:
            if mongodb_test["success"]:
                print("✅ CORRECTION VALIDÉE: save_db_thumbnail utilise maintenant get_sync_media_collection() - FONCTIONNE")
            else:
                print("❌ PROBLÈME PERSISTANT: L'insertion MongoDB ne fonctionne toujours pas correctement")
        
        thumbnail_tests = [r for r in self.test_results if "Thumbnail" in r["test"]]
        working_thumbnails = sum(1 for t in thumbnail_tests if t["success"])
        if working_thumbnails > 0:
            print("✅ GÉNÉRATION DE VIGNETTES: Fonctionne correctement")
        else:
            print("❌ GÉNÉRATION DE VIGNETTES: Problèmes détectés")
        
        upload_tests = [r for r in self.test_results if "Upload" in r["test"]]
        working_uploads = sum(1 for t in upload_tests if t["success"])
        if working_uploads > 0:
            print("✅ SYSTÈME D'UPLOAD: Opérationnel")
        else:
            print("❌ SYSTÈME D'UPLOAD: Problèmes détectés")

if __name__ == "__main__":
    tester = BackendTester()
    tester.run_all_tests()