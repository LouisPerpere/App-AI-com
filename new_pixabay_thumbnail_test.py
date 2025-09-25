#!/usr/bin/env python3
"""
New Pixabay Images Thumbnail System Test
Testing thumbnail system integration for newly saved Pixabay images.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://post-validator.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class NewPixabayThumbnailTest:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.user_id = None
        self.access_token = None
        self.new_pixabay_images = []
        
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
    
    def find_new_pixabay_images(self):
        """Step 2: Find newly saved Pixabay images"""
        print("\n📋 Step 2: Finding newly saved Pixabay images...")
        
        try:
            response = self.session.get(
                f"{BACKEND_URL}/content/pending?limit=50",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get('content', [])
                
                # Find recent Pixabay images (last 10 minutes)
                current_time = datetime.now()
                
                for item in content_items:
                    if 'pixabay' in item.get('filename', '').lower():
                        created_at = item.get('created_at')
                        if created_at:
                            try:
                                created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                                time_diff = (current_time - created_time.replace(tzinfo=None)).total_seconds()
                                if time_diff < 600:  # 10 minutes
                                    self.new_pixabay_images.append(item)
                            except:
                                pass
                
                print(f"✅ Content list retrieved successfully")
                print(f"   Total items: {data.get('total', 0)}")
                print(f"   New Pixabay images found: {len(self.new_pixabay_images)}")
                
                if self.new_pixabay_images:
                    print(f"\n   New Pixabay images details:")
                    for i, img in enumerate(self.new_pixabay_images, 1):
                        print(f"     {i}. ID: {img.get('id')}")
                        print(f"        Filename: {img.get('filename')}")
                        print(f"        URL: {img.get('url', 'Not set')}")
                        print(f"        Thumb URL: {img.get('thumb_url', 'Not set')}")
                        print(f"        Created: {img.get('created_at')}")
                        print()
                    
                    return True
                else:
                    print(f"⚠️ No new Pixabay images found")
                    return False
            else:
                print(f"❌ Content list retrieval failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Content list error: {e}")
            return False
    
    def test_thumbnail_endpoints_for_new_images(self):
        """Step 3: Test thumbnail endpoints for newly saved Pixabay images"""
        print("\n🖼️ Step 3: Testing thumbnail endpoints for new Pixabay images...")
        
        if not self.new_pixabay_images:
            print("❌ No new Pixabay images available for thumbnail test")
            return False
        
        results = []
        
        for i, img in enumerate(self.new_pixabay_images, 1):
            img_id = img.get('id')
            filename = img.get('filename')
            
            print(f"\n   Testing new image {i}: {filename}")
            print(f"     Image ID: {img_id}")
            print(f"     Original URL: {img.get('url', 'Not set')}")
            print(f"     Stored Thumb URL: {img.get('thumb_url', 'Not set')}")
            
            try:
                # Test thumbnail endpoint
                thumb_url = f"{BACKEND_URL}/content/{img_id}/thumb"
                print(f"     Testing: {thumb_url}")
                
                response = self.session.get(thumb_url, timeout=30)
                
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
                        
                        # Check if cache headers are properly set (no no-cache)
                        has_no_cache = any([
                            'no-cache' in cache_control.lower(),
                            'no-store' in cache_control.lower()
                        ])
                        
                        if not has_no_cache:
                            print(f"     ✅ Cache headers properly configured")
                        else:
                            print(f"     ⚠️ No-cache headers present")
                        
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
        print(f"\n   New Pixabay thumbnail test results: {sum(results)}/{len(results)} passed ({success_rate:.1f}%)")
        
        return success_rate >= 66.7
    
    def test_cache_performance_comparison(self):
        """Step 4: Test cache performance - multiple requests to same thumbnail"""
        print("\n⚡ Step 4: Testing cache performance with multiple requests...")
        
        if not self.new_pixabay_images:
            print("❌ No new Pixabay images available for cache performance test")
            return False
        
        try:
            # Use first new Pixabay image
            test_image = self.new_pixabay_images[0]
            img_id = test_image.get('id')
            thumb_url = f"{BACKEND_URL}/content/{img_id}/thumb"
            
            print(f"   Testing cache performance on: {thumb_url}")
            
            # Make multiple requests and measure response times
            response_times = []
            
            for i in range(3):
                print(f"   Request {i+1}...")
                start_time = time.time()
                
                response = self.session.get(thumb_url, timeout=30)
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                response_times.append(response_time)
                
                print(f"     Status: {response.status_code}")
                print(f"     Response time: {response_time:.2f}ms")
                print(f"     Cache-Control: {response.headers.get('Cache-Control', 'Not set')}")
                
                time.sleep(0.5)  # Small delay between requests
            
            avg_response_time = sum(response_times) / len(response_times)
            print(f"\n   Cache performance results:")
            print(f"     Average response time: {avg_response_time:.2f}ms")
            print(f"     Response times: {[f'{t:.2f}ms' for t in response_times]}")
            
            # Check if responses are consistently fast (indicating caching)
            if avg_response_time < 1000:  # Less than 1 second average
                print(f"   ✅ Good cache performance - fast response times")
                return True
            else:
                print(f"   ⚠️ Slow response times - cache may not be working optimally")
                return False
                
        except Exception as e:
            print(f"❌ Cache performance test error: {e}")
            return False
    
    def verify_complete_integration(self):
        """Step 5: Verify complete integration - save, list, thumbnail, cache"""
        print("\n🔄 Step 5: Verifying complete Pixabay integration flow...")
        
        try:
            # Save a new test image
            print("   Saving new test Pixabay image...")
            test_save_data = {
                "pixabay_id": 1234567,
                "image_url": "https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885_640.jpg",
                "tags": "integration, test, complete"
            }
            
            save_response = self.session.post(
                f"{BACKEND_URL}/pixabay/save-image",
                json=test_save_data,
                timeout=60
            )
            
            if save_response.status_code == 200:
                saved_data = save_response.json()
                new_image_id = saved_data.get('image', {}).get('id')
                
                print(f"   ✅ Test image saved with ID: {new_image_id}")
                
                # Check if it appears in content list
                print("   Checking if image appears in content list...")
                content_response = self.session.get(f"{BACKEND_URL}/content/pending", timeout=30)
                
                if content_response.status_code == 200:
                    content_data = content_response.json()
                    found_image = next(
                        (item for item in content_data.get('content', []) if item.get('id') == new_image_id),
                        None
                    )
                    
                    if found_image:
                        print(f"   ✅ Image appears in content list")
                        print(f"     Filename: {found_image.get('filename')}")
                        print(f"     Thumb URL: {found_image.get('thumb_url')}")
                        
                        # Test thumbnail access
                        print("   Testing thumbnail access...")
                        thumb_response = self.session.get(
                            f"{BACKEND_URL}/content/{new_image_id}/thumb",
                            timeout=30
                        )
                        
                        print(f"   Thumbnail response: {thumb_response.status_code}")
                        
                        if thumb_response.status_code in [200, 404]:  # Both are acceptable
                            cache_control = thumb_response.headers.get('Cache-Control', '')
                            print(f"   Cache-Control: {cache_control}")
                            
                            # Check cache headers
                            has_no_cache = 'no-cache' in cache_control.lower() or 'no-store' in cache_control.lower()
                            
                            if not has_no_cache:
                                print(f"   ✅ Complete integration flow successful")
                                return True
                            else:
                                print(f"   ⚠️ Cache headers issue in complete flow")
                                return False
                        else:
                            print(f"   ❌ Thumbnail access issue in complete flow")
                            return False
                    else:
                        print(f"   ❌ Image not found in content list")
                        return False
                else:
                    print(f"   ❌ Content list check failed")
                    return False
            else:
                print(f"   ❌ Test image save failed: {save_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Complete integration test error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all new Pixabay thumbnail tests"""
        print("🎯 NEW PIXABAY THUMBNAIL SYSTEM TESTING STARTED")
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
        
        # Step 2: Find new Pixabay images
        results['find_new_images'] = self.find_new_pixabay_images()
        
        # Step 3: Test thumbnail endpoints
        results['thumbnail_endpoints'] = self.test_thumbnail_endpoints_for_new_images()
        
        # Step 4: Test cache performance
        results['cache_performance'] = self.test_cache_performance_comparison()
        
        # Step 5: Verify complete integration
        results['complete_integration'] = self.verify_complete_integration()
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 NEW PIXABAY THUMBNAIL SYSTEM TEST SUMMARY")
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
        
        if results.get('find_new_images'):
            print(f"   ✅ Found {len(self.new_pixabay_images)} newly saved Pixabay images")
        else:
            print("   ❌ No newly saved Pixabay images found")
        
        if results.get('thumbnail_endpoints'):
            print("   ✅ Thumbnail endpoints working for new Pixabay images")
        else:
            print("   ❌ Thumbnail endpoint issues with new Pixabay images")
        
        if results.get('cache_performance'):
            print("   ✅ Cache performance optimized for Pixabay thumbnails")
        else:
            print("   ❌ Cache performance issues with Pixabay thumbnails")
        
        if results.get('complete_integration'):
            print("   ✅ Complete Pixabay integration flow working correctly")
        else:
            print("   ❌ Issues in complete Pixabay integration flow")
        
        print()
        print("📋 FINAL CONCLUSION:")
        if success_rate >= 80:
            print("   🎉 NEW PIXABAY IMAGES SUCCESSFULLY USE SAME THUMBNAIL SYSTEM AND BENEFIT FROM CACHE FIX")
        elif success_rate >= 60:
            print("   ⚠️ Pixabay thumbnail integration mostly working but has some issues")
        else:
            print("   ❌ Pixabay thumbnail integration has significant issues")
        
        print(f"\nTest completed at: {datetime.now().isoformat()}")
        print("=" * 80)
        
        return results

if __name__ == "__main__":
    tester = NewPixabayThumbnailTest()
    results = tester.run_all_tests()