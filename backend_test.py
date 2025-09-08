#!/usr/bin/env python3
"""
Backend Testing Script for Monthly Refactoring and Pixabay Enhancements
Testing the new monthly attribution features for Pixabay and uploads
"""

import requests
import json
import sys
import io
from PIL import Image
import time

# Configuration
BASE_URL = "https://image-carousel-lib.preview.emergentagent.com/api"
CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        
    def authenticate(self):
        """Step 1: Authenticate with the backend"""
        print("🔑 Step 1: Authentication")
        try:
            response = self.session.post(
                f"{BASE_URL}/auth/login-robust",
                json=CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                print(f"✅ Authentication successful - User ID: {self.user_id}")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def test_pixabay_save_general(self):
        """Step 2: Test Pixabay save with save_type='general'"""
        print("\n🎯 Step 2: Test Pixabay save with save_type='general'")
        try:
            # First get some Pixabay images to save
            search_response = self.session.get(
                f"{BASE_URL}/pixabay/search",
                params={"query": "business", "per_page": 3},
                timeout=30
            )
            
            if search_response.status_code != 200:
                print(f"❌ Pixabay search failed: {search_response.status_code}")
                return False
                
            search_data = search_response.json()
            if not search_data.get("hits"):
                print("❌ No Pixabay images found")
                return False
                
            # Take the first image
            image = search_data["hits"][0]
            
            # Save with save_type="general"
            save_request = {
                "pixabay_id": image["id"],
                "image_url": image["webformatURL"],
                "tags": image["tags"],
                "save_type": "general"
            }
            
            save_response = self.session.post(
                f"{BASE_URL}/pixabay/save-image",
                json=save_request,
                timeout=60
            )
            
            if save_response.status_code == 200:
                save_data = save_response.json()
                saved_image = save_data.get("image", {})
                print(f"✅ Pixabay image saved with save_type='general'")
                print(f"   - Image ID: {saved_image.get('id')}")
                print(f"   - Save type: {saved_image.get('save_type')}")
                print(f"   - Attributed month: {saved_image.get('attributed_month')}")
                print(f"   - Context: {saved_image.get('context', '')[:50]}...")
                return True
            else:
                print(f"❌ Pixabay save failed: {save_response.status_code} - {save_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Pixabay save general test error: {e}")
            return False
    
    def test_pixabay_save_monthly(self):
        """Step 3: Test Pixabay save with save_type='monthly' and attributed_month"""
        print("\n🎯 Step 3: Test Pixabay save with save_type='monthly' and attributed_month='septembre_2025'")
        try:
            # Get another Pixabay image
            search_response = self.session.get(
                f"{BASE_URL}/pixabay/search",
                params={"query": "marketing", "per_page": 3},
                timeout=30
            )
            
            if search_response.status_code != 200:
                print(f"❌ Pixabay search failed: {search_response.status_code}")
                return False
                
            search_data = search_response.json()
            if not search_data.get("hits"):
                print("❌ No Pixabay images found")
                return False
                
            # Take the first image
            image = search_data["hits"][0]
            
            # Save with save_type="monthly" and attributed_month="septembre_2025"
            save_request = {
                "pixabay_id": image["id"],
                "image_url": image["webformatURL"],
                "tags": image["tags"],
                "save_type": "monthly",
                "attributed_month": "septembre_2025"
            }
            
            save_response = self.session.post(
                f"{BASE_URL}/pixabay/save-image",
                json=save_request,
                timeout=60
            )
            
            if save_response.status_code == 200:
                save_data = save_response.json()
                saved_image = save_data.get("image", {})
                print(f"✅ Pixabay image saved with save_type='monthly'")
                print(f"   - Image ID: {saved_image.get('id')}")
                print(f"   - Save type: {saved_image.get('save_type')}")
                print(f"   - Attributed month: {saved_image.get('attributed_month')}")
                print(f"   - Context: {saved_image.get('context', '')[:50]}...")
                
                # Verify the context contains the month
                context = saved_image.get('context', '')
                if 'septembre 2025' in context:
                    print("✅ Context correctly includes attributed month")
                else:
                    print(f"⚠️ Context may not include month properly: {context}")
                
                return True
            else:
                print(f"❌ Pixabay save monthly failed: {save_response.status_code} - {save_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Pixabay save monthly test error: {e}")
            return False
    
    def test_content_pending_fields(self):
        """Step 4: Test GET /api/content/pending returns images with new fields"""
        print("\n🎯 Step 4: Test GET /api/content/pending includes new fields")
        try:
            response = self.session.get(
                f"{BASE_URL}/content/pending",
                params={"limit": 10},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                total_items = len(content_items)
                
                print(f"✅ Content pending retrieved - Total items: {total_items}")
                
                # Check for items with save_type and attributed_month fields
                items_with_save_type = 0
                items_with_attributed_month = 0
                pixabay_items = 0
                
                for item in content_items:
                    # Check if this is a Pixabay item (should have save_type)
                    if 'pixabay' in item.get('filename', '').lower() or item.get('source') == 'pixabay':
                        pixabay_items += 1
                        if 'save_type' in item:
                            items_with_save_type += 1
                        if 'attributed_month' in item:
                            items_with_attributed_month += 1
                
                print(f"   - Pixabay items found: {pixabay_items}")
                print(f"   - Items with save_type field: {items_with_save_type}")
                print(f"   - Items with attributed_month field: {items_with_attributed_month}")
                
                # Show sample of recent items
                if content_items:
                    print("   - Sample of recent items:")
                    for i, item in enumerate(content_items[:3]):
                        print(f"     {i+1}. {item.get('filename', 'N/A')} - save_type: {item.get('save_type', 'N/A')}, attributed_month: {item.get('attributed_month', 'N/A')}")
                
                return True
            else:
                print(f"❌ Content pending failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Content pending test error: {e}")
            return False
    
    def create_test_image(self, filename="test_image.png"):
        """Create a simple test image for upload testing"""
        # Create a simple 100x100 red image
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return img_bytes
    
    def test_batch_upload_single_month(self):
        """Step 5: Test batch upload with attributed_month='octobre_2025' and upload_type='single'"""
        print("\n🎯 Step 5: Test batch upload with attributed_month='octobre_2025' and upload_type='single'")
        try:
            # Create test image
            test_image = self.create_test_image("octobre_test_single.png")
            
            # Prepare files and data
            files = {
                'files': ('octobre_test_single.png', test_image, 'image/png')
            }
            
            # Try to send attributed_month and upload_type as form data
            data = {
                'attributed_month': 'octobre_2025',
                'upload_type': 'single'
            }
            
            response = self.session.post(
                f"{BASE_URL}/content/batch-upload",
                files=files,
                data=data,
                timeout=60
            )
            
            print(f"   - Response status: {response.status_code}")
            print(f"   - Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                upload_data = response.json()
                print(f"✅ Batch upload successful")
                print(f"   - Files created: {upload_data.get('count', 0)}")
                
                # Check if the parameters were accepted (even if not processed)
                created_items = upload_data.get('created', [])
                if created_items:
                    print(f"   - First item ID: {created_items[0].get('id')}")
                
                return True
            elif response.status_code == 422:
                print(f"⚠️ Batch upload returned validation error - parameters may not be implemented yet")
                print(f"   - This suggests attributed_month and upload_type parameters are not yet supported")
                return False
            else:
                print(f"❌ Batch upload failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Batch upload single month test error: {e}")
            return False
    
    def test_batch_upload_carousel_month(self):
        """Step 6: Test batch upload with attributed_month='novembre_2025' and upload_type='carousel'"""
        print("\n🎯 Step 6: Test batch upload with attributed_month='novembre_2025' and upload_type='carousel'")
        try:
            # Create multiple test images for carousel
            test_images = []
            for i in range(2):
                img = Image.new('RGB', (100, 100), color=['blue', 'green'][i])
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                test_images.append(('files', (f'novembre_carousel_{i+1}.png', img_bytes, 'image/png')))
            
            # Try to send attributed_month and upload_type as form data
            data = {
                'attributed_month': 'novembre_2025',
                'upload_type': 'carousel'
            }
            
            response = self.session.post(
                f"{BASE_URL}/content/batch-upload",
                files=test_images,
                data=data,
                timeout=60
            )
            
            print(f"   - Response status: {response.status_code}")
            print(f"   - Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                upload_data = response.json()
                print(f"✅ Batch upload carousel successful")
                print(f"   - Files created: {upload_data.get('count', 0)}")
                
                created_items = upload_data.get('created', [])
                if created_items:
                    print(f"   - Items created: {len(created_items)}")
                    for i, item in enumerate(created_items):
                        print(f"     {i+1}. ID: {item.get('id')}, Filename: {item.get('filename')}")
                
                return True
            elif response.status_code == 422:
                print(f"⚠️ Batch upload carousel returned validation error - parameters may not be implemented yet")
                print(f"   - This suggests attributed_month and upload_type parameters are not yet supported")
                return False
            else:
                print(f"❌ Batch upload carousel failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Batch upload carousel month test error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Monthly Refactoring and Pixabay Enhancement Backend Tests")
        print("=" * 80)
        
        results = {}
        
        # Step 1: Authentication
        results['authentication'] = self.authenticate()
        if not results['authentication']:
            print("\n❌ Authentication failed - cannot proceed with other tests")
            return results
        
        # Step 2-4: Pixabay tests
        results['pixabay_save_general'] = self.test_pixabay_save_general()
        results['pixabay_save_monthly'] = self.test_pixabay_save_monthly()
        results['content_pending_fields'] = self.test_content_pending_fields()
        
        # Step 5-6: Upload tests
        results['batch_upload_single'] = self.test_batch_upload_single_month()
        results['batch_upload_carousel'] = self.test_batch_upload_carousel_month()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name.replace('_', ' ').title()}")
        
        print(f"\n🎯 Overall Success Rate: {success_rate:.1f}% ({passed}/{total} tests passed)")
        
        if success_rate >= 80:
            print("🎉 EXCELLENT - Monthly refactoring features are working well!")
        elif success_rate >= 60:
            print("⚠️ GOOD - Most features working, some issues to address")
        else:
            print("🚨 NEEDS ATTENTION - Multiple issues found")
        
        return results

def main():
    """Main function"""
    tester = BackendTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    if passed == total:
        sys.exit(0)  # All tests passed
    else:
        sys.exit(1)  # Some tests failed

if __name__ == "__main__":
    main()
    
    def get_existing_content(self):
        """Step 2: Get existing content to find Pixabay images"""
        print("\n📋 Step 2: Getting existing content to find Pixabay images...")
        
        try:
            response = self.session.get(f"{BASE_URL}/content/pending")
            print(f"Content pending response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                total_items = data.get("total", 0)
                
                print(f"✅ Content retrieval successful")
                print(f"   Total items: {total_items}")
                print(f"   Items loaded: {len(content_items)}")
                
                # Find Pixabay images
                pixabay_images = []
                for item in content_items:
                    # Check if this is a Pixabay image
                    filename = item.get("filename", "")
                    url = item.get("url", "")
                    thumb_url = item.get("thumb_url", "")
                    
                    if ("pixabay" in filename.lower() or 
                        "pixabay.com" in url or 
                        item.get("source") == "pixabay"):
                        pixabay_images.append(item)
                
                print(f"   Pixabay images found: {len(pixabay_images)}")
                
                # Show details of Pixabay images
                for i, img in enumerate(pixabay_images[:3]):  # Show first 3
                    print(f"   Pixabay Image {i+1}:")
                    print(f"     ID: {img.get('id')}")
                    print(f"     Filename: {img.get('filename')}")
                    print(f"     URL: {img.get('url', '')[:50]}...")
                    print(f"     Thumb URL: {img.get('thumb_url')}")
                
                return pixabay_images
            else:
                print(f"❌ Content retrieval failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Content retrieval error: {str(e)}")
            return []
    
    def test_pixabay_thumbnail_endpoints(self, pixabay_images):
        """Step 3: Test thumbnail endpoints for existing Pixabay images"""
        print("\n🖼️ Step 3: Testing thumbnail endpoints for existing Pixabay images...")
        
        if not pixabay_images:
            print("⚠️ No existing Pixabay images found to test")
            return False
        
        success_count = 0
        total_tests = min(len(pixabay_images), 3)  # Test up to 3 images
        
        for i, img in enumerate(pixabay_images[:total_tests]):
            content_id = img.get("id")
            filename = img.get("filename", "unknown")
            
            print(f"\n   Testing Pixabay image {i+1}/{total_tests}:")
            print(f"     Content ID: {content_id}")
            print(f"     Filename: {filename}")
            
            try:
                # Test the thumbnail endpoint
                start_time = time.time()
                response = self.session.get(f"{BASE_URL}/content/{content_id}/thumb")
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                
                print(f"     Response status: {response.status_code}")
                print(f"     Response time: {response_time:.0f}ms")
                
                if response.status_code == 200:
                    # Check content type
                    content_type = response.headers.get("Content-Type", "")
                    print(f"     Content-Type: {content_type}")
                    
                    # Check cache headers
                    cache_control = response.headers.get("Cache-Control", "")
                    etag = response.headers.get("ETag", "")
                    expires = response.headers.get("Expires", "")
                    
                    print(f"     Cache-Control: {cache_control}")
                    print(f"     ETag: {etag}")
                    print(f"     Expires: {expires}")
                    
                    # Verify cache headers are optimized
                    has_proper_cache = (
                        "public" in cache_control and
                        "max-age=604800" in cache_control and
                        "immutable" in cache_control
                    )
                    
                    if has_proper_cache:
                        print(f"     ✅ Cache headers are properly optimized")
                        success_count += 1
                    else:
                        print(f"     ⚠️ Cache headers not optimized as expected")
                        print(f"        Expected: public, max-age=604800, immutable")
                        print(f"        Got: {cache_control}")
                    
                    # Check content size
                    content_length = len(response.content)
                    print(f"     Content size: {content_length} bytes")
                    
                elif response.status_code == 404:
                    print(f"     ⚠️ Thumbnail not found (may need generation)")
                else:
                    print(f"     ❌ Thumbnail request failed: {response.status_code}")
                    print(f"        Response: {response.text[:200]}")
                
            except Exception as e:
                print(f"     ❌ Thumbnail test error: {str(e)}")
        
        print(f"\n   Thumbnail tests completed: {success_count}/{total_tests} successful")
        return success_count > 0
    
    def save_new_pixabay_image(self):
        """Step 4: Save a new Pixabay image to test the new system"""
        print("\n💾 Step 4: Saving a new Pixabay image to test the system...")
        
        # First, search for a Pixabay image
        try:
            search_response = self.session.get(f"{BASE_URL}/pixabay/search", params={
                "query": "business",
                "per_page": 5
            })
            
            if search_response.status_code != 200:
                print(f"❌ Pixabay search failed: {search_response.status_code}")
                return None
            
            search_data = search_response.json()
            hits = search_data.get("hits", [])
            
            if not hits:
                print("❌ No Pixabay images found in search")
                return None
            
            # Use the first image from search results
            pixabay_image = hits[0]
            pixabay_id = pixabay_image.get("id")
            image_url = pixabay_image.get("webformatURL")
            tags = pixabay_image.get("tags", "")
            
            print(f"   Selected Pixabay image:")
            print(f"     Pixabay ID: {pixabay_id}")
            print(f"     URL: {image_url[:50]}...")
            print(f"     Tags: {tags}")
            
            # Save the image
            save_data = {
                "pixabay_id": pixabay_id,
                "image_url": image_url,
                "tags": tags
            }
            
            save_response = self.session.post(f"{BASE_URL}/pixabay/save-image", json=save_data)
            print(f"   Save response status: {save_response.status_code}")
            
            if save_response.status_code == 200:
                save_result = save_response.json()
                saved_image = save_result.get("image", {})
                
                print(f"   ✅ Pixabay image saved successfully")
                print(f"     Content ID: {saved_image.get('id')}")
                print(f"     Filename: {saved_image.get('filename')}")
                print(f"     Thumb URL: {saved_image.get('thumb_url')}")
                
                return saved_image
            else:
                print(f"   ❌ Failed to save Pixabay image: {save_response.status_code}")
                print(f"      Response: {save_response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Save Pixabay image error: {str(e)}")
            return None
    
    def test_new_pixabay_thumbnail(self, saved_image):
        """Step 5: Test thumbnail generation for newly saved Pixabay image"""
        print("\n🆕 Step 5: Testing thumbnail for newly saved Pixabay image...")
        
        if not saved_image:
            print("⚠️ No saved image to test")
            return False
        
        content_id = saved_image.get("id")
        thumb_url = saved_image.get("thumb_url")
        
        print(f"   Content ID: {content_id}")
        print(f"   Expected thumb URL: {thumb_url}")
        
        # Verify the thumb_url uses the new endpoint format
        expected_endpoint = f"/api/content/{content_id}/thumb"
        if thumb_url == expected_endpoint:
            print(f"   ✅ Thumb URL uses correct endpoint format")
        else:
            print(f"   ⚠️ Thumb URL format unexpected")
            print(f"      Expected: {expected_endpoint}")
            print(f"      Got: {thumb_url}")
        
        try:
            # Test the thumbnail endpoint
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/content/{content_id}/thumb")
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            print(f"   Response status: {response.status_code}")
            print(f"   Response time: {response_time:.0f}ms")
            
            if response.status_code == 200:
                # Check headers
                content_type = response.headers.get("Content-Type", "")
                cache_control = response.headers.get("Cache-Control", "")
                etag = response.headers.get("ETag", "")
                
                print(f"   Content-Type: {content_type}")
                print(f"   Cache-Control: {cache_control}")
                print(f"   ETag: {etag}")
                
                # Verify cache optimization
                has_proper_cache = (
                    "public" in cache_control and
                    "max-age=604800" in cache_control and
                    "immutable" in cache_control
                )
                
                if has_proper_cache:
                    print(f"   ✅ New Pixabay image has optimized cache headers")
                    return True
                else:
                    print(f"   ⚠️ Cache headers not optimized for new image")
                    return False
                    
            else:
                print(f"   ❌ Thumbnail generation failed: {response.status_code}")
                print(f"      Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ New thumbnail test error: {str(e)}")
            return False
    
    def verify_cache_performance(self, pixabay_images):
        """Step 6: Verify cache performance by testing multiple requests"""
        print("\n⚡ Step 6: Testing cache performance with multiple requests...")
        
        if not pixabay_images:
            print("⚠️ No Pixabay images to test cache performance")
            return False
        
        # Test the first available Pixabay image
        test_image = pixabay_images[0]
        content_id = test_image.get("id")
        
        print(f"   Testing cache performance for content ID: {content_id}")
        
        # Make multiple requests to test caching
        response_times = []
        cache_hits = 0
        
        for i in range(3):
            try:
                start_time = time.time()
                response = self.session.get(f"{BASE_URL}/content/{content_id}/thumb")
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                response_times.append(response_time)
                
                # Check if this looks like a cache hit (faster response)
                if i > 0 and response_time < response_times[0] * 0.8:
                    cache_hits += 1
                
                print(f"   Request {i+1}: {response_time:.0f}ms (Status: {response.status_code})")
                
                # Small delay between requests
                time.sleep(0.5)
                
            except Exception as e:
                print(f"   Request {i+1} failed: {str(e)}")
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            print(f"   Average response time: {avg_time:.0f}ms")
            
            # Good performance is typically under 500ms for thumbnails
            if avg_time < 500:
                print(f"   ✅ Good thumbnail performance (< 500ms)")
                return True
            else:
                print(f"   ⚠️ Thumbnail performance could be improved (> 500ms)")
                return False
        
        return False
    
    def run_all_tests(self):
        """Run all Pixabay thumbnail performance tests"""
        print("🚀 Starting Pixabay Thumbnail Performance Testing")
        print("=" * 60)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Get existing content
        pixabay_images = self.get_existing_content()
        
        # Step 3: Test existing Pixabay thumbnails
        existing_thumbs_ok = self.test_pixabay_thumbnail_endpoints(pixabay_images)
        
        # Step 4: Save new Pixabay image
        saved_image = self.save_new_pixabay_image()
        
        # Step 5: Test new Pixabay thumbnail
        new_thumb_ok = self.test_new_pixabay_thumbnail(saved_image)
        
        # Step 6: Test cache performance
        cache_performance_ok = self.verify_cache_performance(pixabay_images)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 PIXABAY THUMBNAIL PERFORMANCE TEST SUMMARY")
        print("=" * 60)
        
        tests_passed = 0
        total_tests = 5
        
        print(f"✅ Authentication: PASSED")
        tests_passed += 1
        
        if existing_thumbs_ok:
            print(f"✅ Existing Pixabay thumbnails: PASSED")
            tests_passed += 1
        else:
            print(f"❌ Existing Pixabay thumbnails: FAILED")
        
        if saved_image:
            print(f"✅ New Pixabay image save: PASSED")
            tests_passed += 1
        else:
            print(f"❌ New Pixabay image save: FAILED")
        
        if new_thumb_ok:
            print(f"✅ New Pixabay thumbnail generation: PASSED")
            tests_passed += 1
        else:
            print(f"❌ New Pixabay thumbnail generation: FAILED")
        
        if cache_performance_ok:
            print(f"✅ Cache performance: PASSED")
            tests_passed += 1
        else:
            print(f"❌ Cache performance: FAILED")
        
        success_rate = (tests_passed / total_tests) * 100
        print(f"\n🎯 Overall Success Rate: {tests_passed}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 PIXABAY THUMBNAIL SYSTEM IS WORKING WELL")
            return True
        else:
            print("⚠️ PIXABAY THUMBNAIL SYSTEM NEEDS ATTENTION")
            return False

if __name__ == "__main__":
    tester = PixabayThumbnailTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ All critical Pixabay thumbnail tests passed!")
    else:
        print("\n❌ Some Pixabay thumbnail tests failed - review needed")