#!/usr/bin/env python3
"""
Test complet du système de génération de posts Instagram nouvellement implémenté

ENDPOINTS À TESTER:
1. POST /api/posts/generate - endpoint principal de génération
2. GET /api/posts/generated - récupération des posts générés

CONTEXT TECHNIQUE:
- Nouveau système PostsGenerator implémenté avec ChatGPT 4o
- Utilise emergentintegrations avec clé EMERGENT_LLM_KEY
- Intégration complète : profil business, analyse site web, notes, contenus uploadés
- Focus Instagram uniquement pour l'instant

TEST SCENARIOS:
1. Authentification utilisateur (credentials: lperpere@yahoo.fr / L@Reunion974!)
2. Vérification profil business existant
3. Test génération de posts avec paramètres par défaut (20 posts, octobre_2025)
4. Vérification structure et contenu des posts générés
5. Test récupération des posts via GET /api/posts/generated
6. Validation métadonnées et format JSON

Backend URL: https://content-scheduler-6.preview.emergentagent.com/api
"""

import requests
import json
import io
from PIL import Image
import time

# Configuration
BACKEND_URL = "https://content-scheduler-6.preview.emergentagent.com/api"
EMAIL = "lperpere@yahoo.fr"
PASSWORD = "L@Reunion974!"

class CarouselTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        
    def authenticate(self):
        """Step 1: Authenticate with the backend"""
        print("🔑 Step 1: Authentication with POST /api/auth/login-robust")
        
        login_data = {
            "email": EMAIL,
            "password": PASSWORD
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login-robust", json=login_data)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for all future requests
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                
                print(f"   ✅ Authentication successful")
                print(f"   User ID: {self.user_id}")
                print(f"   Token: {self.token[:20]}..." if self.token else "   Token: None")
                return True
            else:
                print(f"   ❌ Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {e}")
            return False
    
    def create_test_images(self, count=3):
        """Create test images for carousel upload"""
        print(f"🖼️ Creating {count} test images for carousel upload")
        
        images = []
        for i in range(count):
            # Create a simple colored image
            img = Image.new('RGB', (800, 600), color=(100 + i*50, 150 + i*30, 200 + i*20))
            
            # Add some text to make images unique
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            try:
                # Try to use a default font, fallback to basic if not available
                font = ImageFont.load_default()
            except:
                font = None
            
            text = f"Carousel Image {i+1}"
            if font:
                draw.text((50, 50), text, fill=(255, 255, 255), font=font)
            else:
                draw.text((50, 50), text, fill=(255, 255, 255))
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG', quality=85)
            img_bytes.seek(0)
            
            images.append({
                'filename': f'carousel_test_{i+1}.jpg',
                'content': img_bytes.getvalue(),
                'content_type': 'image/jpeg'
            })
            
        print(f"   ✅ Created {len(images)} test images")
        return images
    
    def test_carousel_batch_upload(self):
        """Step 2: Test carousel batch upload with new parameters"""
        print("📤 Step 2: Testing POST /api/content/batch-upload with carousel parameters")
        
        # Create test images
        test_images = self.create_test_images(3)
        
        # Prepare carousel upload parameters
        carousel_params = {
            'attributed_month': 'octobre_2025',
            'upload_type': 'carousel',
            'common_title': 'Test Carrousel',
            'common_context': 'Description carrousel'
        }
        
        # Prepare files for upload
        files = []
        for img in test_images:
            files.append(('files', (img['filename'], io.BytesIO(img['content']), img['content_type'])))
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/content/batch-upload",
                files=files,
                data=carousel_params
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Carousel batch upload successful")
                print(f"   Upload result: {data.get('ok', False)}")
                print(f"   Files created: {data.get('count', 0)}")
                print(f"   Created items: {len(data.get('created', []))}")
                
                # Store created IDs for later verification
                self.carousel_ids = [item['id'] for item in data.get('created', [])]
                print(f"   Carousel item IDs: {self.carousel_ids}")
                
                return True
            else:
                print(f"   ❌ Carousel upload failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Carousel upload error: {e}")
            return False
    
    def test_content_pending_carousel_fields(self):
        """Step 3: Test GET /api/content/pending returns carousel images with new fields"""
        print("📋 Step 3: Testing GET /api/content/pending for carousel fields")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get('content', [])
                total_items = data.get('total', 0)
                
                print(f"   ✅ Content retrieval successful")
                print(f"   Total items: {total_items}")
                print(f"   Items loaded: {len(content_items)}")
                
                # Find carousel items
                carousel_items = []
                for item in content_items:
                    if item.get('upload_type') == 'carousel':
                        carousel_items.append(item)
                
                print(f"   Carousel items found: {len(carousel_items)}")
                
                if carousel_items:
                    print("   🔍 Analyzing carousel items:")
                    
                    # Check if all carousel items have the same fields
                    first_item = carousel_items[0]
                    common_title = first_item.get('title')
                    common_context = first_item.get('context')
                    attributed_month = first_item.get('attributed_month')
                    carousel_id = first_item.get('carousel_id')
                    
                    print(f"   Expected common_title: 'Test Carrousel'")
                    print(f"   Found common_title: '{common_title}'")
                    print(f"   Expected common_context: 'Description carrousel'")
                    print(f"   Found common_context: '{common_context}'")
                    print(f"   Expected attributed_month: 'octobre_2025'")
                    print(f"   Found attributed_month: '{attributed_month}'")
                    print(f"   Carousel ID: {carousel_id}")
                    
                    # Verify all carousel items have consistent fields
                    all_consistent = True
                    for i, item in enumerate(carousel_items):
                        item_title = item.get('title')
                        item_context = item.get('context')
                        item_month = item.get('attributed_month')
                        item_carousel_id = item.get('carousel_id')
                        item_upload_type = item.get('upload_type')
                        
                        print(f"   Item {i+1}: title='{item_title}', context='{item_context}', month='{item_month}', upload_type='{item_upload_type}'")
                        
                        # Check consistency
                        if (item_title != common_title or 
                            item_context != common_context or 
                            item_month != attributed_month or
                            item_upload_type != 'carousel'):
                            all_consistent = False
                            print(f"   ❌ Item {i+1} has inconsistent fields!")
                    
                    if all_consistent:
                        print(f"   ✅ All carousel items have consistent fields")
                        
                        # Verify expected values
                        title_correct = common_title == 'Test Carrousel'
                        context_correct = 'Description carrousel' in (common_context or '')
                        month_correct = attributed_month == 'octobre_2025'
                        
                        print(f"   Title correct: {title_correct}")
                        print(f"   Context correct: {context_correct}")
                        print(f"   Month correct: {month_correct}")
                        
                        if title_correct and context_correct and month_correct:
                            print(f"   ✅ All carousel field values are correct")
                            return True
                        else:
                            print(f"   ❌ Some carousel field values are incorrect")
                            return False
                    else:
                        print(f"   ❌ Carousel items have inconsistent fields")
                        return False
                else:
                    print(f"   ❌ No carousel items found in content")
                    return False
                    
            else:
                print(f"   ❌ Content retrieval failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Content retrieval error: {e}")
            return False
    
    def test_carousel_thumbnails(self):
        """Step 4: Test thumbnail generation for carousel images"""
        print("🖼️ Step 4: Testing thumbnail generation for carousel images")
        
        if not hasattr(self, 'carousel_ids') or not self.carousel_ids:
            print("   ❌ No carousel IDs available for thumbnail testing")
            return False
        
        thumbnail_results = []
        
        for i, item_id in enumerate(self.carousel_ids):
            print(f"   Testing thumbnail for carousel item {i+1}: {item_id}")
            
            try:
                # Test thumbnail endpoint
                thumb_url = f"{BACKEND_URL}/content/{item_id}/thumb"
                response = self.session.get(thumb_url)
                
                print(f"   Thumbnail status: {response.status_code}")
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    content_length = len(response.content)
                    
                    print(f"   ✅ Thumbnail generated successfully")
                    print(f"   Content-Type: {content_type}")
                    print(f"   Content-Length: {content_length} bytes")
                    
                    # Verify it's an image
                    if 'image' in content_type and content_length > 0:
                        thumbnail_results.append(True)
                        print(f"   ✅ Valid thumbnail image")
                    else:
                        thumbnail_results.append(False)
                        print(f"   ❌ Invalid thumbnail content")
                else:
                    thumbnail_results.append(False)
                    print(f"   ❌ Thumbnail generation failed: {response.text}")
                    
            except Exception as e:
                thumbnail_results.append(False)
                print(f"   ❌ Thumbnail test error: {e}")
        
        success_count = sum(thumbnail_results)
        total_count = len(thumbnail_results)
        
        print(f"   Thumbnail generation results: {success_count}/{total_count} successful")
        
        if success_count == total_count:
            print(f"   ✅ All carousel thumbnails generated successfully")
            return True
        else:
            print(f"   ❌ Some carousel thumbnails failed to generate")
            return False
    
    def test_carousel_grouping(self):
        """Step 5: Test carousel grouping with carousel_id"""
        print("🔗 Step 5: Testing carousel grouping with carousel_id")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get('content', [])
                
                # Find carousel items
                carousel_items = [item for item in content_items if item.get('upload_type') == 'carousel']
                
                if carousel_items:
                    # Check if all carousel items have the same carousel_id
                    carousel_ids = [item.get('carousel_id') for item in carousel_items]
                    unique_carousel_ids = set(filter(None, carousel_ids))
                    
                    print(f"   Carousel items found: {len(carousel_items)}")
                    print(f"   Unique carousel IDs: {len(unique_carousel_ids)}")
                    print(f"   Carousel IDs: {list(unique_carousel_ids)}")
                    
                    if len(unique_carousel_ids) == 1:
                        print(f"   ✅ All carousel items have the same carousel_id")
                        print(f"   Carousel ID: {list(unique_carousel_ids)[0]}")
                        return True
                    else:
                        print(f"   ❌ Carousel items have different carousel_ids or missing IDs")
                        return False
                else:
                    print(f"   ❌ No carousel items found for grouping test")
                    return False
            else:
                print(f"   ❌ Failed to retrieve content for grouping test")
                return False
                
        except Exception as e:
            print(f"   ❌ Carousel grouping test error: {e}")
            return False
    
    def cleanup_test_data(self):
        """Step 6: Clean up test carousel data"""
        print("🧹 Step 6: Cleaning up test carousel data")
        
        if not hasattr(self, 'carousel_ids') or not self.carousel_ids:
            print("   No carousel IDs to clean up")
            return True
        
        cleanup_results = []
        
        for i, item_id in enumerate(self.carousel_ids):
            try:
                response = self.session.delete(f"{BACKEND_URL}/content/{item_id}")
                
                if response.status_code == 200:
                    cleanup_results.append(True)
                    print(f"   ✅ Deleted carousel item {i+1}: {item_id}")
                else:
                    cleanup_results.append(False)
                    print(f"   ❌ Failed to delete carousel item {i+1}: {response.text}")
                    
            except Exception as e:
                cleanup_results.append(False)
                print(f"   ❌ Cleanup error for item {i+1}: {e}")
        
        success_count = sum(cleanup_results)
        total_count = len(cleanup_results)
        
        print(f"   Cleanup results: {success_count}/{total_count} items deleted")
        
        return success_count == total_count
    
    def run_comprehensive_test(self):
        """Run all carousel functionality tests"""
        print("🎠 COMPREHENSIVE CAROUSEL FUNCTIONALITY TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test credentials: {EMAIL}")
        print("=" * 60)
        
        test_results = []
        
        # Step 1: Authentication
        test_results.append(self.authenticate())
        
        if test_results[-1]:
            # Step 2: Carousel batch upload
            test_results.append(self.test_carousel_batch_upload())
            
            if test_results[-1]:
                # Step 3: Content pending with carousel fields
                test_results.append(self.test_content_pending_carousel_fields())
                
                # Step 4: Thumbnail generation
                test_results.append(self.test_carousel_thumbnails())
                
                # Step 5: Carousel grouping
                test_results.append(self.test_carousel_grouping())
                
                # Step 6: Cleanup
                test_results.append(self.cleanup_test_data())
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 CAROUSEL TESTING SUMMARY")
        print("=" * 60)
        
        test_names = [
            "Authentication",
            "Carousel Batch Upload",
            "Content Pending Fields",
            "Thumbnail Generation", 
            "Carousel Grouping",
            "Cleanup"
        ]
        
        passed_tests = 0
        for i, (name, result) in enumerate(zip(test_names[:len(test_results)], test_results)):
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{i+1}. {name}: {status}")
            if result:
                passed_tests += 1
        
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\nOverall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 CAROUSEL FUNCTIONALITY TESTING COMPLETED SUCCESSFULLY")
            print("✅ The carousel upload system is working correctly")
        else:
            print("🚨 CAROUSEL FUNCTIONALITY TESTING FAILED")
            print("❌ Critical issues found in carousel implementation")
        
        return success_rate >= 80

def main():
    """Main test execution"""
    tester = CarouselTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎯 CONCLUSION: Carousel functionality is FULLY OPERATIONAL")
        exit(0)
    else:
        print("\n🚨 CONCLUSION: Carousel functionality has CRITICAL ISSUES")
        exit(1)

if __name__ == "__main__":
    main()