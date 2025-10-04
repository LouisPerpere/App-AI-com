#!/usr/bin/env python3
"""
Pixabay Save Endpoint Diagnostic Test
Testing the Pixabay save endpoint with different image URLs to identify issues.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://claire-marcus-app-1.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class PixabaySaveEndpointTest:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.user_id = None
        self.access_token = None
        
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
    
    def test_pixabay_search_first(self):
        """Step 2: Test Pixabay search to get valid image URLs"""
        print("\n🔍 Step 2: Testing Pixabay search to get valid image URLs...")
        
        try:
            response = self.session.get(
                f"{BACKEND_URL}/pixabay/search?query=business&per_page=5",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                hits = data.get('hits', [])
                
                print(f"✅ Pixabay search successful")
                print(f"   Total results: {data.get('total', 0)}")
                print(f"   Images returned: {len(hits)}")
                
                if hits:
                    print(f"\n   Sample images from search:")
                    for i, hit in enumerate(hits[:3], 1):
                        print(f"     {i}. ID: {hit.get('id')}")
                        print(f"        Tags: {hit.get('tags', '')[:50]}...")
                        print(f"        WebFormat URL: {hit.get('webformatURL', '')}")
                        print(f"        Preview URL: {hit.get('previewURL', '')}")
                        print()
                    
                    return hits
                else:
                    print(f"⚠️ No images returned from search")
                    return []
            else:
                print(f"❌ Pixabay search failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Pixabay search error: {e}")
            return []
    
    def test_pixabay_save_with_search_results(self, search_results):
        """Step 3: Test save endpoint with images from search results"""
        print("\n💾 Step 3: Testing Pixabay save with search results...")
        
        if not search_results:
            print("❌ No search results available for save test")
            return False
        
        success_count = 0
        
        for i, image in enumerate(search_results[:2], 1):  # Test first 2 images
            print(f"\n   Testing save for image {i}:")
            print(f"     Pixabay ID: {image.get('id')}")
            print(f"     Tags: {image.get('tags', '')[:50]}...")
            
            # Try with webformatURL first
            save_data = {
                "pixabay_id": image.get('id'),
                "image_url": image.get('webformatURL'),
                "tags": image.get('tags', '')
            }
            
            try:
                print(f"     Attempting save with webformatURL...")
                response = self.session.post(
                    f"{BACKEND_URL}/pixabay/save-image",
                    json=save_data,
                    timeout=60
                )
                
                print(f"     Response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    saved_image = data.get('image', {})
                    
                    print(f"     ✅ Save successful!")
                    print(f"       Saved ID: {saved_image.get('id')}")
                    print(f"       Filename: {saved_image.get('filename')}")
                    print(f"       File size: {saved_image.get('file_size')} bytes")
                    success_count += 1
                else:
                    print(f"     ❌ Save failed: {response.status_code}")
                    print(f"       Error: {response.text}")
                    
                    # Try with previewURL as fallback
                    if image.get('previewURL'):
                        print(f"     Trying fallback with previewURL...")
                        save_data['image_url'] = image.get('previewURL')
                        
                        fallback_response = self.session.post(
                            f"{BACKEND_URL}/pixabay/save-image",
                            json=save_data,
                            timeout=60
                        )
                        
                        if fallback_response.status_code == 200:
                            print(f"     ✅ Fallback save successful!")
                            success_count += 1
                        else:
                            print(f"     ❌ Fallback also failed: {fallback_response.status_code}")
                            
            except Exception as e:
                print(f"     ❌ Save error: {e}")
        
        print(f"\n   Save test results: {success_count}/{len(search_results[:2])} successful")
        return success_count > 0
    
    def test_manual_pixabay_urls(self):
        """Step 4: Test with manually constructed Pixabay URLs"""
        print("\n🔧 Step 4: Testing with manually constructed Pixabay URLs...")
        
        # Test with simpler, more reliable Pixabay URLs
        test_images = [
            {
                "pixabay_id": 195893,
                "image_url": "https://cdn.pixabay.com/photo/2013/07/12/15/36/motorsports-150157_640.jpg",
                "tags": "motorsports, racing, speed"
            },
            {
                "pixabay_id": 736885,
                "image_url": "https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885_640.jpg", 
                "tags": "tree, nature, landscape"
            }
        ]
        
        success_count = 0
        
        for i, image_data in enumerate(test_images, 1):
            print(f"\n   Testing manual URL {i}:")
            print(f"     Pixabay ID: {image_data['pixabay_id']}")
            print(f"     URL: {image_data['image_url']}")
            
            try:
                response = self.session.post(
                    f"{BACKEND_URL}/pixabay/save-image",
                    json=image_data,
                    timeout=60
                )
                
                print(f"     Response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    saved_image = data.get('image', {})
                    
                    print(f"     ✅ Manual URL save successful!")
                    print(f"       Saved ID: {saved_image.get('id')}")
                    print(f"       Filename: {saved_image.get('filename')}")
                    success_count += 1
                else:
                    print(f"     ❌ Manual URL save failed: {response.status_code}")
                    print(f"       Error: {response.text}")
                    
            except Exception as e:
                print(f"     ❌ Manual URL save error: {e}")
        
        print(f"\n   Manual URL test results: {success_count}/{len(test_images)} successful")
        return success_count > 0
    
    def verify_saved_images_in_library(self):
        """Step 5: Verify saved images appear in content library"""
        print("\n📚 Step 5: Verifying saved images appear in content library...")
        
        try:
            response = self.session.get(
                f"{BACKEND_URL}/content/pending?limit=50",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get('content', [])
                
                # Find recently added Pixabay images (check timestamps)
                recent_pixabay = []
                current_time = datetime.now()
                
                for item in content_items:
                    if 'pixabay' in item.get('filename', '').lower():
                        created_at = item.get('created_at')
                        if created_at:
                            try:
                                # Check if created in last 10 minutes
                                created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                                time_diff = (current_time - created_time.replace(tzinfo=None)).total_seconds()
                                if time_diff < 600:  # 10 minutes
                                    recent_pixabay.append(item)
                            except:
                                pass
                
                print(f"✅ Content library checked")
                print(f"   Total items: {data.get('total', 0)}")
                print(f"   Recent Pixabay images: {len(recent_pixabay)}")
                
                if recent_pixabay:
                    print(f"\n   Recently saved Pixabay images:")
                    for img in recent_pixabay:
                        print(f"     - ID: {img.get('id')}")
                        print(f"       Filename: {img.get('filename')}")
                        print(f"       Created: {img.get('created_at')}")
                        print(f"       Thumb URL: {img.get('thumb_url', 'Not set')}")
                    return True
                else:
                    print(f"   ⚠️ No recently saved Pixabay images found")
                    return False
            else:
                print(f"❌ Content library check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Content library check error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all Pixabay save endpoint tests"""
        print("🎯 PIXABAY SAVE ENDPOINT DIAGNOSTIC TESTING STARTED")
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
        
        # Step 2: Test Pixabay search
        search_results = self.test_pixabay_search_first()
        results['pixabay_search'] = len(search_results) > 0
        
        # Step 3: Test save with search results
        results['save_search_results'] = self.test_pixabay_save_with_search_results(search_results)
        
        # Step 4: Test with manual URLs
        results['save_manual_urls'] = self.test_manual_pixabay_urls()
        
        # Step 5: Verify in library
        results['verify_library'] = self.verify_saved_images_in_library()
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 PIXABAY SAVE ENDPOINT DIAGNOSTIC TEST SUMMARY")
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
        
        if results.get('pixabay_search'):
            print("   ✅ Pixabay search endpoint working correctly")
        else:
            print("   ❌ Pixabay search endpoint has issues")
        
        if results.get('save_search_results') or results.get('save_manual_urls'):
            print("   ✅ Pixabay save endpoint working with some image URLs")
        else:
            print("   ❌ Pixabay save endpoint failing with all tested URLs")
        
        if results.get('verify_library'):
            print("   ✅ Saved Pixabay images appear correctly in content library")
        else:
            print("   ❌ Saved images not appearing in content library")
        
        print()
        print("📋 CONCLUSION:")
        if success_rate >= 80:
            print("   🎉 Pixabay save endpoint working correctly")
        elif success_rate >= 60:
            print("   ⚠️ Pixabay save endpoint has some issues but partially functional")
        else:
            print("   ❌ Pixabay save endpoint has significant issues")
        
        print(f"\nTest completed at: {datetime.now().isoformat()}")
        print("=" * 80)
        
        return results

if __name__ == "__main__":
    tester = PixabaySaveEndpointTest()
    results = tester.run_all_tests()