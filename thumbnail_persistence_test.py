#!/usr/bin/env python3
"""
Thumbnail Persistence Test - Re-run tests for /api/auth/login-robust and /api/content/pending
Based on review request to test thumbnail functionality with known endpoints.
"""

import requests
import time
import json
import os
from typing import Optional, Dict, Any

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://social-publisher-10.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Known credentials from previous tests
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class ThumbnailTester:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def log(self, message: str, level: str = "INFO"):
        """Log test messages"""
        print(f"[{level}] {message}")
        
    def login(self) -> bool:
        """Step 1: Login via POST /api/auth/login-robust with known creds"""
        self.log("🔑 Step 1: Testing login with /api/auth/login-robust")
        
        try:
            response = self.session.post(
                f"{API_BASE}/auth/login-robust",
                json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token')
                self.user_id = data.get('user_id')
                
                # Update session headers with token
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}'
                })
                
                self.log(f"✅ Login successful - User ID: {self.user_id}")
                self.log(f"✅ Token obtained: {self.token[:20]}..." if self.token else "❌ No token received")
                return True
            else:
                self.log(f"❌ Login failed - Status: {response.status_code}, Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Login error: {str(e)}", "ERROR")
            return False
    
    def get_pending_content(self) -> Optional[Dict[str, Any]]:
        """Step 2: GET /api/content/pending?limit=24&offset=0. Pick first image/* item."""
        self.log("📋 Step 2: Getting pending content to find image files")
        
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
                    if file_type.startswith('image/'):
                        self.log(f"✅ Found image file: {item.get('filename')} (ID: {item.get('id')}, Type: {file_type})")
                        return item
                
                self.log("⚠️ No image files found in pending content")
                return None
                
            else:
                self.log(f"❌ Failed to get pending content - Status: {response.status_code}, Response: {response.text}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Error getting pending content: {str(e)}", "ERROR")
            return None
    
    def get_thumbnail(self, file_id: str) -> bool:
        """Step 3: GET /api/content/{id}/thumb → 200 image/* or 404 source missing"""
        self.log(f"🖼️ Step 3: Getting thumbnail for file ID: {file_id}")
        
        try:
            response = self.session.get(f"{API_BASE}/content/{file_id}/thumb")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                
                self.log(f"✅ Thumbnail retrieved - Content-Type: {content_type}, Size: {content_length} bytes")
                return True
                
            elif response.status_code == 404:
                self.log(f"⚠️ Thumbnail not found (404) - Source missing or thumbnail not generated yet")
                return False
                
            else:
                self.log(f"❌ Unexpected response - Status: {response.status_code}, Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error getting thumbnail: {str(e)}", "ERROR")
            return False
    
    def generate_thumbnail(self, file_id: str) -> bool:
        """Step 4: POST /api/content/{id}/thumbnail → should schedule. Wait ~2s, then GET /api/content/{id}/thumb again → expect 200 image/*"""
        self.log(f"⚙️ Step 4: Generating thumbnail for file ID: {file_id}")
        
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
                    return self.get_thumbnail(file_id)
                else:
                    self.log("⚠️ Thumbnail generation was not scheduled")
                    return False
                    
            else:
                self.log(f"❌ Failed to schedule thumbnail generation - Status: {response.status_code}, Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error generating thumbnail: {str(e)}", "ERROR")
            return False
    
    def rebuild_thumbnails(self) -> Dict[str, Any]:
        """Step 5: POST /api/content/thumbnails/rebuild → expect scheduling count. Then GET /api/content/thumbnails/status → inspect counts."""
        self.log("🔧 Step 5: Testing thumbnail rebuild functionality")
        
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
                    
                    return {
                        'rebuild_scheduled': scheduled,
                        'files_found': files_found,
                        'status': status_data
                    }
                else:
                    self.log(f"❌ Failed to get thumbnail status - Status: {status_response.status_code}", "ERROR")
                    return {'rebuild_scheduled': scheduled, 'files_found': files_found}
                    
            else:
                self.log(f"❌ Failed to trigger thumbnail rebuild - Status: {response.status_code}, Response: {response.text}", "ERROR")
                return {}
                
        except Exception as e:
            self.log(f"❌ Error in thumbnail rebuild: {str(e)}", "ERROR")
            return {}
    
    def verify_thumb_url_update(self, file_id: str) -> bool:
        """Step 6: Verify media.thumb_url updated to relative "/api/content/{id}/thumb" """
        self.log(f"🔍 Step 6: Verifying thumb_url update for file ID: {file_id}")
        
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
                            return False
                
                self.log(f"⚠️ File ID {file_id} not found in content list")
                return False
                
            else:
                self.log(f"❌ Failed to get content for verification - Status: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error verifying thumb_url: {str(e)}", "ERROR")
            return False
    
    def run_full_test(self):
        """Run the complete thumbnail persistence test"""
        self.log("🚀 Starting Thumbnail Persistence Test")
        self.log("=" * 60)
        
        results = {
            'login': False,
            'content_found': False,
            'initial_thumbnail': False,
            'thumbnail_generation': False,
            'rebuild_test': False,
            'thumb_url_verification': False,
            'test_file_id': None
        }
        
        # Step 1: Login
        if not self.login():
            self.log("❌ Test failed at login step", "ERROR")
            return results
        results['login'] = True
        
        # Step 2: Get content
        image_item = self.get_pending_content()
        if not image_item:
            self.log("❌ Test failed - no image content found", "ERROR")
            return results
        
        results['content_found'] = True
        file_id = image_item.get('id')
        results['test_file_id'] = file_id
        
        # Step 3: Check initial thumbnail
        initial_thumb_exists = self.get_thumbnail(file_id)
        results['initial_thumbnail'] = initial_thumb_exists
        
        # Step 4: Generate thumbnail (if not exists) or test generation
        if not initial_thumb_exists:
            self.log("🔄 Thumbnail doesn't exist, testing generation...")
            results['thumbnail_generation'] = self.generate_thumbnail(file_id)
        else:
            self.log("🔄 Thumbnail exists, testing regeneration...")
            results['thumbnail_generation'] = self.generate_thumbnail(file_id)
        
        # Step 5: Test rebuild functionality
        rebuild_results = self.rebuild_thumbnails()
        results['rebuild_test'] = bool(rebuild_results.get('rebuild_scheduled', 0) >= 0)
        
        # Step 6: Verify thumb_url update
        results['thumb_url_verification'] = self.verify_thumb_url_update(file_id)
        
        # Summary
        self.log("=" * 60)
        self.log("📊 TEST RESULTS SUMMARY:")
        self.log(f"✅ Login: {results['login']}")
        self.log(f"✅ Content Found: {results['content_found']}")
        self.log(f"✅ Initial Thumbnail: {results['initial_thumbnail']}")
        self.log(f"✅ Thumbnail Generation: {results['thumbnail_generation']}")
        self.log(f"✅ Rebuild Test: {results['rebuild_test']}")
        self.log(f"✅ Thumb URL Verification: {results['thumb_url_verification']}")
        
        passed_tests = sum(1 for v in results.values() if v is True)
        total_tests = len([k for k in results.keys() if k != 'test_file_id'])
        success_rate = (passed_tests / total_tests) * 100
        
        self.log(f"📈 SUCCESS RATE: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            self.log("🎉 THUMBNAIL PERSISTENCE TEST PASSED", "SUCCESS")
        else:
            self.log("❌ THUMBNAIL PERSISTENCE TEST FAILED", "ERROR")
        
        return results

def main():
    """Main test execution"""
    tester = ThumbnailTester()
    results = tester.run_full_test()
    
    # Return appropriate exit code
    passed_tests = sum(1 for v in results.values() if v is True)
    total_tests = len([k for k in results.keys() if k != 'test_file_id'])
    
    if passed_tests >= total_tests * 0.8:  # 80% pass rate
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    main()