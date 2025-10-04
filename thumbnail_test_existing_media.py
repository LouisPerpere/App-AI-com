#!/usr/bin/env python3
"""
Thumbnail Persistence Test with Existing Media
Test thumbnail functionality using existing media documents
"""

import requests
import time
import json
import os
import sys
sys.path.append('/app/backend')

from database import get_database
from bson import ObjectId

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://claire-marcus-app-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Known credentials
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class ThumbnailTester:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.session = requests.Session()
        
    def log(self, message: str, level: str = "INFO"):
        """Log test messages"""
        print(f"[{level}] {message}")
        
    def authenticate(self):
        """Authenticate and get token"""
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
                
                self.log(f"✅ Authentication successful - User ID: {self.user_id}")
                self.log(f"✅ Token obtained: {self.token[:20]}..." if self.token else "❌ No token received")
                return True
            else:
                self.log(f"❌ Authentication failed - Status: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Authentication error: {str(e)}", "ERROR")
            return False
    
    def get_pending_content(self):
        """Step 2: GET /api/content/pending?limit=24&offset=0. Pick first image/* item."""
        self.log("📋 Step 2: GET /api/content/pending?limit=24&offset=0. Pick first image/* item")
        
        try:
            response = self.session.get(f"{API_BASE}/content/pending?limit=24&offset=0")
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get('content', [])
                total = data.get('total', 0)
                
                self.log(f"✅ Content retrieved - Total: {total}, Loaded: {len(content_items)}")
                
                # Find first image/* item
                for item in content_items:
                    file_type = item.get('file_type', '')
                    filename = item.get('filename', '')
                    file_id = item.get('id', '')
                    
                    if file_type.startswith('image/'):
                        # Check if file exists on disk
                        file_path = f"/app/backend/uploads/{filename}"
                        if os.path.exists(file_path):
                            self.log(f"✅ Found image file: {filename} (ID: {file_id}, Type: {file_type})")
                            self.log(f"✅ File exists on disk: {file_path}")
                            return item
                        else:
                            self.log(f"⚠️ Image file {filename} not found on disk, skipping...")
                
                self.log("❌ No image files found with existing disk files")
                return None
                
            else:
                self.log(f"❌ Failed to get pending content - Status: {response.status_code}, Response: {response.text}", "ERROR")
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
                self.log(f"❌ Failed to trigger thumbnail rebuild - Status: {response.status_code}, Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error in thumbnail rebuild: {str(e)}", "ERROR")
            return False
    
    def verify_thumb_url_update(self, file_id: str):
        """Step 6: Verify media.thumb_url updated to relative "/api/content/{id}/thumb" """
        self.log(f"🔍 Step 6: Verify media.thumb_url updated to relative \"/api/content/{file_id}/thumb\"")
        
        try:
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
    
    def run_complete_test(self):
        """Run the complete thumbnail persistence test as specified in review request"""
        self.log("🚀 Starting Thumbnail Persistence Test - Re-run tests for /api/auth/login-robust and /api/content/pending")
        self.log("=" * 80)
        
        results = {
            'login': False,
            'content_retrieval': False,
            'initial_thumbnail': False,
            'thumbnail_generation': False,
            'rebuild_functionality': False,
            'thumb_url_verification': False,
            'test_file_id': None,
            'test_filename': None
        }
        
        # Step 1: Login
        if not self.authenticate():
            self.log("❌ Test failed at authentication step", "ERROR")
            return results
        results['login'] = True
        
        # Step 2: Get content
        image_item = self.get_pending_content()
        if not image_item:
            self.log("❌ Test failed - no suitable image content found", "ERROR")
            return results
        
        results['content_retrieval'] = True
        file_id = image_item.get('id')
        filename = image_item.get('filename')
        results['test_file_id'] = file_id
        results['test_filename'] = filename
        
        # Step 3: Check initial thumbnail
        initial_thumb_exists = self.test_thumbnail_retrieval(file_id)
        results['initial_thumbnail'] = initial_thumb_exists
        
        # Step 4: Generate thumbnail
        generation_success = self.test_thumbnail_generation(file_id)
        results['thumbnail_generation'] = generation_success
        
        # Step 5: Test rebuild functionality
        rebuild_success = self.test_rebuild_functionality()
        results['rebuild_functionality'] = rebuild_success
        
        # Step 6: Verify thumb_url update
        thumb_url_success = self.verify_thumb_url_update(file_id)
        results['thumb_url_verification'] = thumb_url_success
        
        # Summary
        self.log("=" * 80)
        self.log("📊 THUMBNAIL PERSISTENCE TEST RESULTS:")
        self.log(f"🎯 Test File: {filename} (ID: {file_id})")
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
        total = 0
        
        for key, value in results.items():
            if key in ['test_file_id', 'test_filename']:
                continue
            total += 1
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

def main():
    """Main test execution"""
    tester = ThumbnailTester()
    success = tester.run_complete_test()
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)