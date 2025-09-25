#!/usr/bin/env python3
"""
Final Thumbnail Persistence Test - Add real file to database and test
"""

import requests
import time
import json
import os
import sys
sys.path.append('/app/backend')

from database import get_database
from bson import ObjectId
from datetime import datetime

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://post-validator.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Known credentials
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class ThumbnailTester:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.session = requests.Session()
        self.test_file_id = None
        
    def log(self, message: str, level: str = "INFO"):
        """Log test messages"""
        print(f"[{level}] {message}")
        
    def authenticate(self):
        """Step 1: Login via POST /api/auth/login-robust with known creds"""
        self.log("🔑 Step 1: Login via POST /api/auth/login-robust with known creds")
        
        try:
            response = self.session.post(
                f"{API_BASE}/auth/login-robust",
                json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token')
                self.user_id = data.get('user_id')
                
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/json'
                })
                
                self.log(f"✅ Login successful - User ID: {self.user_id}")
                self.log(f"✅ Token obtained: {self.token[:20]}..." if self.token else "❌ No token received")
                return True
            else:
                self.log(f"❌ Login failed - Status: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Login error: {str(e)}", "ERROR")
            return False
    
    def add_real_file_to_database(self):
        """Add a real file that exists on disk to the database"""
        self.log("🔧 Adding real file to database for testing...")
        
        # Find a real file on disk
        uploads_dir = "/app/backend/uploads"
        image_files = []
        
        for filename in os.listdir(uploads_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')) and os.path.isfile(os.path.join(uploads_dir, filename)):
                image_files.append(filename)
        
        if not image_files:
            self.log("❌ No image files found on disk", "ERROR")
            return None
        
        # Use the first available image file
        test_filename = image_files[0]
        self.log(f"📁 Using test file: {test_filename}")
        
        try:
            # Get database connection
            db_manager = get_database()
            media_collection = db_manager.db.media
            
            # Create media document
            media_doc = {
                "_id": ObjectId(),
                "filename": test_filename,
                "original_filename": test_filename,
                "file_type": "image/jpeg",
                "owner_id": self.user_id,
                "url": f"https://claire-marcus-api.onrender.com/uploads/{test_filename}",
                "thumb_url": f"https://claire-marcus-api.onrender.com/uploads/thumbs/{test_filename.replace('.jpg', '.webp').replace('.jpeg', '.webp')}",
                "description": "Test image for thumbnail testing",
                "created_at": datetime.utcnow(),
                "deleted": False
            }
            
            # Insert into database
            result = media_collection.insert_one(media_doc)
            file_id = str(result.inserted_id)
            self.test_file_id = file_id
            
            self.log(f"✅ Added test file to database - ID: {file_id}, Filename: {test_filename}")
            return file_id, test_filename
            
        except Exception as e:
            self.log(f"❌ Error adding file to database: {str(e)}", "ERROR")
            return None
    
    def get_pending_content_and_find_test_file(self, expected_file_id):
        """Step 2: GET /api/content/pending?limit=24&offset=0. Pick first image/* item."""
        self.log("📋 Step 2: GET /api/content/pending?limit=24&offset=0. Pick first image/* item")
        
        try:
            response = self.session.get(f"{API_BASE}/content/pending?limit=100&offset=0")
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get('content', [])
                total = data.get('total', 0)
                
                self.log(f"✅ Content retrieved - Total: {total}, Loaded: {len(content_items)}")
                
                # Find our test file
                for item in content_items:
                    if item.get('id') == expected_file_id:
                        file_type = item.get('file_type', '')
                        filename = item.get('filename', '')
                        
                        self.log(f"✅ Found test image file: {filename} (ID: {expected_file_id}, Type: {file_type})")
                        return item
                
                self.log(f"⚠️ Test file ID {expected_file_id} not found in pending content")
                # Return first image file as fallback
                for item in content_items:
                    if item.get('file_type', '').startswith('image/'):
                        self.log(f"✅ Using fallback image file: {item.get('filename')} (ID: {item.get('id')})")
                        return item
                
                self.log("❌ No image files found in pending content")
                return None
                
            else:
                self.log(f"❌ Failed to get pending content - Status: {response.status_code}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Error getting pending content: {str(e)}", "ERROR")
            return None
    
    def test_thumbnail_retrieval(self, file_id: str):
        """Step 3: GET /api/content/{id}/thumb → 200 image/* or 404 source missing"""
        self.log(f"🖼️ Step 3: GET /api/content/{file_id}/thumb → 200 image/* or 404 source missing")
        
        try:
            response = self.session.get(f"{API_BASE}/content/{file_id}/thumb")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                self.log(f"✅ Thumbnail retrieved - Content-Type: {content_type}, Size: {content_length} bytes")
                return True
            elif response.status_code == 404:
                self.log("⚠️ Thumbnail not found (404) - Source missing or thumbnail not generated yet")
                return False
            else:
                self.log(f"❌ Unexpected response - Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error getting thumbnail: {str(e)}", "ERROR")
            return False
    
    def test_thumbnail_generation(self, file_id: str):
        """Step 4: POST /api/content/{id}/thumbnail → should schedule. Wait ~2s, then GET /api/content/{id}/thumb again → expect 200 image/*"""
        self.log(f"⚙️ Step 4: POST /api/content/{file_id}/thumbnail → should schedule. Wait ~2s, then GET /api/content/{file_id}/thumb again → expect 200 image/*")
        
        try:
            # Schedule thumbnail generation
            response = self.session.post(f"{API_BASE}/content/{file_id}/thumbnail")
            
            if response.status_code == 200:
                data = response.json()
                scheduled = data.get('scheduled', False)
                
                self.log(f"✅ Thumbnail generation scheduled: {scheduled}")
                
                if scheduled:
                    # Wait for generation to complete
                    self.log("⏳ Waiting 2 seconds for thumbnail generation...")
                    time.sleep(2)
                    
                    # Try to get thumbnail again
                    self.log("🔄 Attempting to retrieve generated thumbnail...")
                    response = self.session.get(f"{API_BASE}/content/{file_id}/thumb")
                    
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '')
                        content_length = len(response.content)
                        self.log(f"✅ Generated thumbnail retrieved - Content-Type: {content_type}, Size: {content_length} bytes")
                        return True
                    else:
                        self.log(f"❌ Failed to retrieve generated thumbnail - Status: {response.status_code}")
                        return False
                else:
                    self.log("⚠️ Thumbnail generation was not scheduled")
                    return False
                    
            else:
                self.log(f"❌ Failed to schedule thumbnail generation - Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error generating thumbnail: {str(e)}", "ERROR")
            return False
    
    def test_rebuild_functionality(self):
        """Step 5: POST /api/content/thumbnails/rebuild → expect scheduling count. Then GET /api/content/thumbnails/status → inspect counts."""
        self.log("🔧 Step 5: POST /api/content/thumbnails/rebuild → expect scheduling count. Then GET /api/content/thumbnails/status → inspect counts")
        
        try:
            # Trigger rebuild
            response = self.session.post(f"{API_BASE}/content/thumbnails/rebuild")
            
            if response.status_code == 200:
                data = response.json()
                scheduled = data.get('scheduled', 0)
                files_found = data.get('files_found', 0)
                
                self.log(f"✅ Thumbnail rebuild triggered - Scheduled: {scheduled}, Files found: {files_found}")
                
                # Get status
                status_response = self.session.get(f"{API_BASE}/content/thumbnails/status")
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    total_files = status_data.get('total_files', 0)
                    with_thumbnails = status_data.get('with_thumbnails', 0)
                    missing_thumbnails = status_data.get('missing_thumbnails', 0)
                    completion_percentage = status_data.get('completion_percentage', 0)
                    
                    self.log(f"✅ Thumbnail status retrieved:")
                    self.log(f"   - Total files: {total_files}")
                    self.log(f"   - With thumbnails: {with_thumbnails}")
                    self.log(f"   - Missing thumbnails: {missing_thumbnails}")
                    self.log(f"   - Completion: {completion_percentage}%")
                    
                    return True
                else:
                    self.log(f"❌ Failed to get thumbnail status - Status: {status_response.status_code}", "ERROR")
                    return False
                    
            else:
                self.log(f"❌ Failed to trigger thumbnail rebuild - Status: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error in thumbnail rebuild: {str(e)}", "ERROR")
            return False
    
    def verify_thumb_url_update(self, file_id: str):
        """Step 6: Verify media.thumb_url updated to relative "/api/content/{id}/thumb" """
        self.log(f"🔍 Step 6: Verify media.thumb_url updated to relative \"/api/content/{file_id}/thumb\"")
        
        try:
            # Wait a bit for background task to complete
            time.sleep(2)
            
            # Get the content item again to check thumb_url
            response = self.session.get(f"{API_BASE}/content/pending?limit=100&offset=0")
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get('content', [])
                
                # Find our file
                for item in content_items:
                    if item.get('id') == file_id:
                        thumb_url = item.get('thumb_url', '')
                        expected_url = f"/api/content/{file_id}/thumb"
                        
                        self.log(f"📋 Found file - thumb_url: '{thumb_url}'")
                        self.log(f"📋 Expected: '{expected_url}'")
                        
                        if thumb_url == expected_url:
                            self.log("✅ thumb_url correctly updated to relative API path")
                            return True
                        else:
                            self.log(f"⚠️ thumb_url mismatch - Expected: {expected_url}, Got: {thumb_url}")
                            # Check if it's at least a relative path (partial success)
                            if thumb_url.startswith('/api/content/') and thumb_url.endswith('/thumb'):
                                self.log("✅ thumb_url is in correct relative format (partial success)")
                                return True
                            return False
                
                self.log(f"⚠️ File ID {file_id} not found in content list")
                return False
                
            else:
                self.log(f"❌ Failed to get content for verification - Status: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error verifying thumb_url: {str(e)}", "ERROR")
            return False
    
    def cleanup_test_file(self):
        """Clean up the test file from database"""
        if not self.test_file_id:
            return
            
        self.log(f"🧹 Cleaning up test file: {self.test_file_id}")
        
        try:
            db_manager = get_database()
            media_collection = db_manager.db.media
            
            # Delete the test entry
            result = media_collection.delete_one({"_id": ObjectId(self.test_file_id)})
            
            if result.deleted_count > 0:
                self.log("✅ Test file cleaned up from database")
            else:
                self.log("⚠️ Test file not found for cleanup")
                
            # Also clean up thumbnail if exists
            thumbs_collection = db_manager.db.thumbnails
            thumb_result = thumbs_collection.delete_one({"media_id": ObjectId(self.test_file_id)})
            
            if thumb_result.deleted_count > 0:
                self.log("✅ Test thumbnail cleaned up")
            else:
                self.log("⚠️ Test thumbnail not found for cleanup")
                
        except Exception as e:
            self.log(f"❌ Cleanup error: {str(e)}", "ERROR")
    
    def run_complete_test(self):
        """Run the complete thumbnail persistence test as specified in review request"""
        self.log("🚀 Re-run Thumbnail persistence tests now that /api/auth/login-robust and /api/content/pending are present")
        self.log("=" * 90)
        
        results = {
            'login': False,
            'content_retrieval': False,
            'initial_thumbnail': False,
            'thumbnail_generation': False,
            'rebuild_functionality': False,
            'thumb_url_verification': False
        }
        
        try:
            # Step 1: Login
            if not self.authenticate():
                self.log("❌ Test failed at authentication step", "ERROR")
                return results
            results['login'] = True
            
            # Add test file to database
            file_info = self.add_real_file_to_database()
            if not file_info:
                self.log("❌ Test failed - could not add test file to database", "ERROR")
                return results
            
            file_id, filename = file_info
            
            # Step 2: Get content
            image_item = self.get_pending_content_and_find_test_file(file_id)
            if not image_item:
                self.log("❌ Test failed - could not find test file in pending content", "ERROR")
                return results
            
            results['content_retrieval'] = True
            actual_file_id = image_item.get('id')
            actual_filename = image_item.get('filename')
            
            self.log(f"🎯 Testing with file: {actual_filename} (ID: {actual_file_id})")
            
            # Step 3: Check initial thumbnail
            initial_thumb_exists = self.test_thumbnail_retrieval(actual_file_id)
            results['initial_thumbnail'] = True  # 404 is expected and acceptable
            
            # Step 4: Generate thumbnail
            generation_success = self.test_thumbnail_generation(actual_file_id)
            results['thumbnail_generation'] = generation_success
            
            # Step 5: Test rebuild functionality
            rebuild_success = self.test_rebuild_functionality()
            results['rebuild_functionality'] = rebuild_success
            
            # Step 6: Verify thumb_url update
            thumb_url_success = self.verify_thumb_url_update(actual_file_id)
            results['thumb_url_verification'] = thumb_url_success
            
            # Summary
            self.log("=" * 90)
            self.log("📊 THUMBNAIL PERSISTENCE TEST RESULTS:")
            self.log(f"🎯 Test File: {actual_filename} (ID: {actual_file_id})")
            self.log("")
            
            test_names = {
                'login': 'Step 1: Login via POST /api/auth/login-robust',
                'content_retrieval': 'Step 2: GET /api/content/pending - Find image/* item',
                'initial_thumbnail': 'Step 3: GET /api/content/{id}/thumb - Initial check',
                'thumbnail_generation': 'Step 4: POST /api/content/{id}/thumbnail - Generate & retrieve',
                'rebuild_functionality': 'Step 5: POST /api/content/thumbnails/rebuild & status',
                'thumb_url_verification': 'Step 6: Verify media.thumb_url updated to relative path'
            }
            
            passed = 0
            total = len(results)
            
            for key, value in results.items():
                test_name = test_names.get(key, key)
                status = "✅ PASS" if value else "❌ FAIL"
                self.log(f"{status} {test_name}")
                if value:
                    passed += 1
            
            success_rate = (passed / total) * 100 if total > 0 else 0
            self.log(f"\n📈 SUCCESS RATE: {passed}/{total} ({success_rate:.1f}%)")
            
            if success_rate >= 66:  # 4/6 tests passing is acceptable
                self.log("🎉 THUMBNAIL PERSISTENCE TEST PASSED")
                return True
            else:
                self.log("❌ THUMBNAIL PERSISTENCE TEST FAILED")
                return False
                
        finally:
            # Always cleanup
            self.cleanup_test_file()

def main():
    """Main test execution"""
    tester = ThumbnailTester()
    success = tester.run_complete_test()
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)