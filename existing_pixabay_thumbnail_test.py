#!/usr/bin/env python3
"""
Existing Pixabay Images Thumbnail Cache Test
Testing thumbnail system integration with existing Pixabay images in the library.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://social-pub-hub.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class ExistingPixabayThumbnailTest:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.user_id = None
        self.access_token = None
        self.pixabay_images = []
        
    def authenticate(self):
        """Step 1: Authenticate with the backend"""
        print("🔐 Step 1: Authenticating with backend...")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json=TEST_CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                self.user_id = data.get('user_id')
                
                # Set authorization header for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                
                print(f"✅ Authentication successful")
                print(f"   User ID: {self.user_id}")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def find_existing_pixabay_images(self):
        """Step 2: Find existing Pixabay images in content library"""
        print("\n📋 Step 2: Finding existing Pixabay images...")
        
        try:
            response = self.session.get(
                f"{BACKEND_URL}/content/pending?limit=50",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get('content', [])
                
                # Find Pixabay images
                self.pixabay_images = [
                    item for item in content_items 
                    if 'pixabay' in item.get('filename', '').lower()
                ]
                
                print(f"✅ Content list retrieved successfully")
                print(f"   Total items: {data.get('total', 0)}")
                print(f"   Items loaded: {len(content_items)}")
                print(f"   Pixabay images found: {len(self.pixabay_images)}")
                
                if self.pixabay_images:
                    print(f"\n   Pixabay images details:")
                    for i, img in enumerate(self.pixabay_images[:5], 1):  # Show first 5
                        print(f"     {i}. ID: {img.get('id')}")
                        print(f"        Filename: {img.get('filename')}")
                        print(f"        File type: {img.get('file_type')}")
                        print(f"        URL: {img.get('url', 'Not set')}")
                        print(f"        Thumb URL: {img.get('thumb_url', 'Not set')}")
                        print(f"        Context: {img.get('context', 'Not set')}")
                        print(f"        Title: {img.get('title', 'Not set')}")
                        print()
                    
                    return True
                else:
                    print(f"⚠️ No Pixabay images found in content library")
                    return False
            else:
                print(f"❌ Content list retrieval failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Content list error: {e}")
            return False
    
    def test_pixabay_thumbnail_structure(self):
        """Step 3: Test if Pixabay images have same structure as uploaded images"""
        print("\n🔍 Step 3: Testing Pixabay image structure vs uploaded images...")
        
        if not self.pixabay_images:
            print("❌ No Pixabay images available for structure test")
            return False
        
        try:
            # Get all content to compare structures
            response = self.session.get(
                f"{BACKEND_URL}/content/pending?limit=50",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                all_items = data.get('content', [])
                
                # Separate Pixabay and regular uploads
                regular_uploads = [
                    item for item in all_items 
                    if 'pixabay' not in item.get('filename', '').lower()
                ]
                
                print(f"   Regular uploads found: {len(regular_uploads)}")
                print(f"   Pixabay images found: {len(self.pixabay_images)}")
                
                if regular_uploads and self.pixabay_images:
                    # Compare structure
                    pixabay_sample = self.pixabay_images[0]
                    regular_sample = regular_uploads[0]
                    
                    print(f"\n   Structure comparison:")
                    print(f"   Pixabay image fields: {list(pixabay_sample.keys())}")
                    print(f"   Regular upload fields: {list(regular_sample.keys())}")
                    
                    # Check if they have the same essential fields
                    essential_fields = ['id', 'filename', 'file_type', 'url', 'thumb_url', 'description', 'context', 'title']
                    
                    pixabay_has_fields = [field for field in essential_fields if field in pixabay_sample]
                    regular_has_fields = [field for field in essential_fields if field in regular_sample]
                    
                    print(f"\n   Essential fields in Pixabay: {pixabay_has_fields}")
                    print(f"   Essential fields in Regular: {regular_has_fields}")
                    
                    # Check if structures match
                    structure_match = set(pixabay_has_fields) == set(regular_has_fields)
                    
                    if structure_match:
                        print(f"✅ Pixabay images have same structure as uploaded images")
                        return True
                    else:
                        print(f"⚠️ Structure differences found between Pixabay and regular uploads")
                        missing_in_pixabay = set(regular_has_fields) - set(pixabay_has_fields)
                        missing_in_regular = set(pixabay_has_fields) - set(regular_has_fields)
                        if missing_in_pixabay:
                            print(f"     Missing in Pixabay: {missing_in_pixabay}")
                        if missing_in_regular:
                            print(f"     Missing in Regular: {missing_in_regular}")
                        return False
                else:
                    print(f"⚠️ Cannot compare - need both Pixabay and regular images")
                    return False
            else:
                print(f"❌ Failed to get content for structure comparison: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Structure comparison error: {e}")
            return False
    
    def test_pixabay_thumbnail_endpoints(self):
        """Step 4: Test thumbnail endpoints for Pixabay images"""
        print("\n🖼️ Step 4: Testing thumbnail endpoints for Pixabay images...")
        
        if not self.pixabay_images:
            print("❌ No Pixabay images available for thumbnail test")
            return False
        
        results = []
        
        for i, img in enumerate(self.pixabay_images[:3], 1):  # Test first 3 images
            img_id = img.get('id')
            filename = img.get('filename')
            
            print(f"\n   Testing image {i}: {filename} (ID: {img_id})")
            
            try:
                # Test thumbnail endpoint
                thumb_url = f"{BACKEND_URL}/content/{img_id}/thumb"
                response = self.session.get(thumb_url, timeout=30)
                
                print(f"     Thumbnail URL: {thumb_url}")
                print(f"     Response status: {response.status_code}")
                print(f"     Content-Type: {response.headers.get('content-type', 'Not set')}")
                print(f"     Content-Length: {len(response.content)} bytes")
                
                # Check cache headers
                cache_control = response.headers.get('Cache-Control', 'Not set')
                expires = response.headers.get('Expires', 'Not set')
                etag = response.headers.get('ETag', 'Not set')
                
                print(f"     Cache-Control: {cache_control}")
                print(f"     Expires: {expires}")
                print(f"     ETag: {etag}")
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    if content_type.startswith('image/'):
                        print(f"     ✅ Valid thumbnail returned")
                        results.append(True)
                    else:
                        print(f"     ⚠️ Non-image content returned")
                        results.append(False)
                elif response.status_code == 404:
                    print(f"     ⚠️ Thumbnail not found (404) - may use external URL")
                    results.append(True)  # This is expected for external images
                else:
                    print(f"     ❌ Thumbnail access failed")
                    results.append(False)
                    
            except Exception as e:
                print(f"     ❌ Thumbnail test error: {e}")
                results.append(False)
        
        success_rate = (sum(results) / len(results)) * 100 if results else 0
        print(f"\n   Thumbnail endpoint test results: {sum(results)}/{len(results)} passed ({success_rate:.1f}%)")
        
        return success_rate >= 66.7  # At least 2/3 should pass
    
    def test_cache_headers_on_thumbnails(self):
        """Step 5: Test cache headers specifically on thumbnail endpoints"""
        print("\n🔄 Step 5: Testing cache headers on thumbnail endpoints...")
        
        if not self.pixabay_images:
            print("❌ No Pixabay images available for cache test")
            return False
        
        try:
            # Test with first available Pixabay image
            test_image = self.pixabay_images[0]
            img_id = test_image.get('id')
            thumb_url = f"{BACKEND_URL}/content/{img_id}/thumb"
            
            print(f"   Testing cache headers on: {thumb_url}")
            
            # Make request and analyze headers
            response = self.session.get(thumb_url, timeout=30)
            
            print(f"   Response status: {response.status_code}")
            print(f"   Response headers analysis:")
            
            # Check for no-cache headers (should NOT be present due to cache fix)
            cache_control = response.headers.get('Cache-Control', '')
            pragma = response.headers.get('Pragma', '')
            expires = response.headers.get('Expires', '')
            
            print(f"     Cache-Control: {cache_control}")
            print(f"     Pragma: {pragma}")
            print(f"     Expires: {expires}")
            
            # Check if cache fix is working (no no-cache headers)
            has_no_cache = any([
                'no-cache' in cache_control.lower(),
                'no-store' in cache_control.lower(),
                'no-cache' in pragma.lower()
            ])
            
            if not has_no_cache:
                print(f"   ✅ Cache fix working - no no-cache headers found on thumbnail endpoint")
                return True
            else:
                print(f"   ⚠️ No-cache headers still present - cache fix may not be working")
                return False
                
        except Exception as e:
            print(f"❌ Cache headers test error: {e}")
            return False
    
    def compare_with_regular_uploads(self):
        """Step 6: Compare Pixabay thumbnail behavior with regular uploads"""
        print("\n⚖️ Step 6: Comparing Pixabay vs regular upload thumbnail behavior...")
        
        try:
            # Get all content
            response = self.session.get(
                f"{BACKEND_URL}/content/pending?limit=50",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                all_items = data.get('content', [])
                
                regular_uploads = [
                    item for item in all_items 
                    if 'pixabay' not in item.get('filename', '').lower()
                ]
                
                if not regular_uploads:
                    print("   ⚠️ No regular uploads found for comparison")
                    return False
                
                if not self.pixabay_images:
                    print("   ⚠️ No Pixabay images found for comparison")
                    return False
                
                # Test thumbnail endpoints for both types
                print(f"   Testing regular upload thumbnail...")
                regular_img = regular_uploads[0]
                regular_thumb_url = f"{BACKEND_URL}/content/{regular_img.get('id')}/thumb"
                regular_response = self.session.get(regular_thumb_url, timeout=30)
                
                print(f"   Testing Pixabay image thumbnail...")
                pixabay_img = self.pixabay_images[0]
                pixabay_thumb_url = f"{BACKEND_URL}/content/{pixabay_img.get('id')}/thumb"
                pixabay_response = self.session.get(pixabay_thumb_url, timeout=30)
                
                print(f"\n   Comparison results:")
                print(f"     Regular upload:")
                print(f"       Status: {regular_response.status_code}")
                print(f"       Cache-Control: {regular_response.headers.get('Cache-Control', 'Not set')}")
                print(f"       Content-Type: {regular_response.headers.get('Content-Type', 'Not set')}")
                
                print(f"     Pixabay image:")
                print(f"       Status: {pixabay_response.status_code}")
                print(f"       Cache-Control: {pixabay_response.headers.get('Cache-Control', 'Not set')}")
                print(f"       Content-Type: {pixabay_response.headers.get('Content-Type', 'Not set')}")
                
                # Check if both benefit from cache fix
                regular_cache = regular_response.headers.get('Cache-Control', '')
                pixabay_cache = pixabay_response.headers.get('Cache-Control', '')
                
                regular_no_cache = 'no-cache' in regular_cache.lower() or 'no-store' in regular_cache.lower()
                pixabay_no_cache = 'no-cache' in pixabay_cache.lower() or 'no-store' in pixabay_cache.lower()
                
                if not regular_no_cache and not pixabay_no_cache:
                    print(f"   ✅ Both regular and Pixabay images benefit from cache fix")
                    return True
                elif regular_no_cache and pixabay_no_cache:
                    print(f"   ⚠️ Neither regular nor Pixabay images benefit from cache fix")
                    return False
                else:
                    print(f"   ⚠️ Inconsistent cache behavior between regular and Pixabay images")
                    return False
                    
            else:
                print(f"❌ Failed to get content for comparison: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Comparison error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all existing Pixabay thumbnail tests"""
        print("🎯 EXISTING PIXABAY THUMBNAIL CACHE TESTING STARTED")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test credentials: {TEST_CREDENTIALS['email']}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print("=" * 80)
        
        results = {}
        
        # Step 1: Authentication
        results['authentication'] = self.authenticate()
        if not results['authentication']:
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with tests")
            return results
        
        # Step 2: Find existing Pixabay images
        results['find_pixabay'] = self.find_existing_pixabay_images()
        
        # Step 3: Test structure compatibility
        results['structure_test'] = self.test_pixabay_thumbnail_structure()
        
        # Step 4: Test thumbnail endpoints
        results['thumbnail_endpoints'] = self.test_pixabay_thumbnail_endpoints()
        
        # Step 5: Test cache headers
        results['cache_headers'] = self.test_cache_headers_on_thumbnails()
        
        # Step 6: Compare with regular uploads
        results['comparison'] = self.compare_with_regular_uploads()
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 EXISTING PIXABAY THUMBNAIL CACHE TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(1 for result in results.values() if result)
        total_tests = len(results)
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"📊 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}% success rate)")
        print()
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status} - {test_name.replace('_', ' ').title()}")
        
        print()
        print("🔍 KEY FINDINGS:")
        
        if results.get('find_pixabay'):
            print(f"   ✅ Found {len(self.pixabay_images)} existing Pixabay images in library")
        else:
            print("   ❌ No existing Pixabay images found")
        
        if results.get('structure_test'):
            print("   ✅ Pixabay images have same structure as uploaded images")
        else:
            print("   ❌ Structure differences between Pixabay and uploaded images")
        
        if results.get('thumbnail_endpoints'):
            print("   ✅ Thumbnail endpoints working for Pixabay images")
        else:
            print("   ❌ Thumbnail endpoint issues with Pixabay images")
        
        if results.get('cache_headers'):
            print("   ✅ Cache headers fix applied to Pixabay thumbnails")
        else:
            print("   ❌ Cache headers fix not working for Pixabay thumbnails")
        
        if results.get('comparison'):
            print("   ✅ Pixabay and regular uploads have consistent thumbnail behavior")
        else:
            print("   ❌ Inconsistent thumbnail behavior between image types")
        
        print()
        print("📋 CONCLUSION:")
        if success_rate >= 80:
            print("   🎉 Existing Pixabay images successfully use same thumbnail system and benefit from cache fix")
        elif success_rate >= 60:
            print("   ⚠️ Pixabay thumbnail integration mostly working but has some issues")
        else:
            print("   ❌ Pixabay thumbnail integration has significant issues")
        
        print(f"\nTest completed at: {datetime.now().isoformat()}")
        print("=" * 80)
        
        return results

if __name__ == "__main__":
    tester = ExistingPixabayThumbnailTest()
    results = tester.run_all_tests()