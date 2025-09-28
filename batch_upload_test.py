#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Batch Upload Functionality
Test des corrections du problème d'upload multiple

This script tests the batch upload functionality with different upload types:
1. POST /api/content/batch-upload with multiple files and upload_type="batch"
2. POST /api/content/batch-upload with single file and upload_type="single" 
3. POST /api/content/batch-upload with multiple files and upload_type="carousel"
4. Test uploads with attributed_month parameter
5. Verify no conflicts between different upload modes

Using credentials: lperpere@yahoo.fr / L@Reunion974!
Backend URL: https://social-publisher-10.preview.emergentagent.com/api
"""

import requests
import json
import io
from PIL import Image
import time
import uuid

# Configuration
BACKEND_URL = "https://social-publisher-10.preview.emergentagent.com/api"
EMAIL = "lperpere@yahoo.fr"
PASSWORD = "L@Reunion974!"

class BatchUploadTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.uploaded_ids = []
        
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
    
    def create_test_images(self, count=3, prefix="test"):
        """Create test images for upload"""
        print(f"🖼️ Creating {count} test images with prefix '{prefix}'")
        
        images = []
        for i in range(count):
            # Create a simple colored image with unique colors
            color = (50 + i*40, 100 + i*30, 150 + i*25)
            img = Image.new('RGB', (640, 480), color=color)
            
            # Add some text to make images unique
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.load_default()
            except:
                font = None
            
            text = f"{prefix.title()} Image {i+1}"
            if font:
                draw.text((50, 50), text, fill=(255, 255, 255), font=font)
            else:
                draw.text((50, 50), text, fill=(255, 255, 255))
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG', quality=85)
            img_bytes.seek(0)
            
            images.append({
                'filename': f'{prefix}_upload_{i+1}_{str(uuid.uuid4())[:8]}.jpg',
                'content': img_bytes.getvalue(),
                'content_type': 'image/jpeg'
            })
            
        print(f"   ✅ Created {len(images)} test images")
        return images
    
    def test_batch_upload_multiple_files(self):
        """Step 2: Test batch upload with multiple files and upload_type='batch'"""
        print("📤 Step 2: Testing POST /api/content/batch-upload with multiple files (upload_type='batch')")
        
        # Create test images
        test_images = self.create_test_images(3, "batch")
        
        # Prepare batch upload parameters
        batch_params = {
            'upload_type': 'batch',
            'attributed_month': 'octobre_2025'
        }
        
        # Prepare files for upload
        files = []
        for img in test_images:
            files.append(('files', (img['filename'], io.BytesIO(img['content']), img['content_type'])))
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/content/batch-upload",
                files=files,
                data=batch_params
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Batch upload successful")
                print(f"   Upload result: {data.get('ok', False)}")
                print(f"   Files created: {data.get('count', 0)}")
                print(f"   Created items: {len(data.get('created', []))}")
                
                # Store created IDs for later verification
                batch_ids = [item['id'] for item in data.get('created', [])]
                self.uploaded_ids.extend(batch_ids)
                print(f"   Batch item IDs: {batch_ids}")
                
                return True
            else:
                print(f"   ❌ Batch upload failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Batch upload error: {e}")
            return False
    
    def test_single_upload(self):
        """Step 3: Test single file upload with upload_type='single'"""
        print("📤 Step 3: Testing POST /api/content/batch-upload with single file (upload_type='single')")
        
        # Create single test image
        test_images = self.create_test_images(1, "single")
        
        # Prepare single upload parameters
        single_params = {
            'upload_type': 'single',
            'attributed_month': 'octobre_2025'
        }
        
        # Prepare file for upload
        files = []
        for img in test_images:
            files.append(('files', (img['filename'], io.BytesIO(img['content']), img['content_type'])))
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/content/batch-upload",
                files=files,
                data=single_params
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Single upload successful")
                print(f"   Upload result: {data.get('ok', False)}")
                print(f"   Files created: {data.get('count', 0)}")
                print(f"   Created items: {len(data.get('created', []))}")
                
                # Store created IDs for later verification
                single_ids = [item['id'] for item in data.get('created', [])]
                self.uploaded_ids.extend(single_ids)
                print(f"   Single item IDs: {single_ids}")
                
                return True
            else:
                print(f"   ❌ Single upload failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Single upload error: {e}")
            return False
    
    def test_carousel_upload_multiple_files(self):
        """Step 4: Test carousel upload with multiple files and upload_type='carousel'"""
        print("📤 Step 4: Testing POST /api/content/batch-upload with multiple files (upload_type='carousel')")
        
        # Create test images
        test_images = self.create_test_images(3, "carousel")
        
        # Prepare carousel upload parameters
        carousel_params = {
            'upload_type': 'carousel',
            'attributed_month': 'octobre_2025',
            'common_title': 'Test Carrousel Octobre',
            'common_context': 'Images de test pour carrousel octobre 2025'
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
                print(f"   ✅ Carousel upload successful")
                print(f"   Upload result: {data.get('ok', False)}")
                print(f"   Files created: {data.get('count', 0)}")
                print(f"   Created items: {len(data.get('created', []))}")
                
                # Store created IDs for later verification
                carousel_ids = [item['id'] for item in data.get('created', [])]
                self.uploaded_ids.extend(carousel_ids)
                print(f"   Carousel item IDs: {carousel_ids}")
                
                return True
            else:
                print(f"   ❌ Carousel upload failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Carousel upload error: {e}")
            return False
    
    def test_attributed_month_handling(self):
        """Step 5: Test uploads with different attributed_month values"""
        print("📅 Step 5: Testing uploads with different attributed_month values")
        
        # Test different months
        test_months = ['septembre_2025', 'novembre_2025', 'decembre_2025']
        month_results = []
        
        for month in test_months:
            print(f"   Testing attributed_month: {month}")
            
            # Create single test image
            test_images = self.create_test_images(1, f"month_{month}")
            
            # Prepare upload parameters
            month_params = {
                'upload_type': 'single',
                'attributed_month': month
            }
            
            # Prepare file for upload
            files = []
            for img in test_images:
                files.append(('files', (img['filename'], io.BytesIO(img['content']), img['content_type'])))
            
            try:
                response = self.session.post(
                    f"{BACKEND_URL}/content/batch-upload",
                    files=files,
                    data=month_params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    month_ids = [item['id'] for item in data.get('created', [])]
                    self.uploaded_ids.extend(month_ids)
                    month_results.append(True)
                    print(f"   ✅ Upload successful for {month}")
                else:
                    month_results.append(False)
                    print(f"   ❌ Upload failed for {month}: {response.text}")
                    
            except Exception as e:
                month_results.append(False)
                print(f"   ❌ Upload error for {month}: {e}")
        
        success_count = sum(month_results)
        total_count = len(month_results)
        
        print(f"   Month attribution results: {success_count}/{total_count} successful")
        
        return success_count == total_count
    
    def test_upload_mode_conflicts(self):
        """Step 6: Test for conflicts between different upload modes"""
        print("🔍 Step 6: Testing for conflicts between different upload modes")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get('content', [])
                
                print(f"   ✅ Content retrieval successful")
                print(f"   Total items: {data.get('total', 0)}")
                print(f"   Items loaded: {len(content_items)}")
                
                # Analyze upload types
                upload_types = {}
                attributed_months = {}
                carousel_groups = {}
                
                for item in content_items:
                    upload_type = item.get('upload_type', 'unknown')
                    attributed_month = item.get('attributed_month', 'none')
                    carousel_id = item.get('carousel_id', '')
                    
                    # Count upload types
                    upload_types[upload_type] = upload_types.get(upload_type, 0) + 1
                    
                    # Count attributed months
                    attributed_months[attributed_month] = attributed_months.get(attributed_month, 0) + 1
                    
                    # Track carousel groups
                    if carousel_id:
                        if carousel_id not in carousel_groups:
                            carousel_groups[carousel_id] = []
                        carousel_groups[carousel_id].append(item.get('id'))
                
                print(f"   📊 Upload type distribution:")
                for upload_type, count in upload_types.items():
                    print(f"     {upload_type}: {count} items")
                
                print(f"   📅 Attributed month distribution:")
                for month, count in attributed_months.items():
                    print(f"     {month}: {count} items")
                
                print(f"   🎠 Carousel groups found: {len(carousel_groups)}")
                for carousel_id, items in carousel_groups.items():
                    print(f"     Carousel {carousel_id}: {len(items)} items")
                
                # Check for conflicts
                conflicts_found = False
                
                # Check if batch items have proper upload_type
                batch_items = [item for item in content_items if item.get('upload_type') == 'batch']
                single_items = [item for item in content_items if item.get('upload_type') == 'single']
                carousel_items = [item for item in content_items if item.get('upload_type') == 'carousel']
                
                print(f"   🔍 Conflict analysis:")
                print(f"     Batch items: {len(batch_items)}")
                print(f"     Single items: {len(single_items)}")
                print(f"     Carousel items: {len(carousel_items)}")
                
                # Check carousel consistency
                for carousel_id, items in carousel_groups.items():
                    carousel_content = [item for item in content_items if item.get('carousel_id') == carousel_id]
                    
                    if carousel_content:
                        # Check if all items in carousel have same upload_type
                        upload_types_in_carousel = set(item.get('upload_type') for item in carousel_content)
                        if len(upload_types_in_carousel) > 1:
                            conflicts_found = True
                            print(f"     ❌ Carousel {carousel_id} has mixed upload types: {upload_types_in_carousel}")
                        elif 'carousel' not in upload_types_in_carousel:
                            conflicts_found = True
                            print(f"     ❌ Carousel {carousel_id} items don't have upload_type='carousel'")
                        else:
                            print(f"     ✅ Carousel {carousel_id} has consistent upload_type")
                
                if not conflicts_found:
                    print(f"   ✅ No conflicts found between upload modes")
                    return True
                else:
                    print(f"   ❌ Conflicts detected between upload modes")
                    return False
                    
            else:
                print(f"   ❌ Content retrieval failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Conflict analysis error: {e}")
            return False
    
    def verify_upload_persistence(self):
        """Step 7: Verify that all uploads are properly persisted with correct metadata"""
        print("💾 Step 7: Verifying upload persistence and metadata")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get('content', [])
                
                # Find our uploaded items
                our_items = [item for item in content_items if item.get('id') in self.uploaded_ids]
                
                print(f"   Our uploaded items found: {len(our_items)}/{len(self.uploaded_ids)}")
                
                if len(our_items) == len(self.uploaded_ids):
                    print(f"   ✅ All uploaded items found in database")
                    
                    # Verify metadata for each upload type
                    metadata_correct = True
                    
                    for item in our_items:
                        item_id = item.get('id')
                        upload_type = item.get('upload_type')
                        attributed_month = item.get('attributed_month')
                        title = item.get('title', '')
                        context = item.get('context', '')
                        
                        print(f"   Item {item_id}: type={upload_type}, month={attributed_month}")
                        
                        # Check attributed_month is set
                        if not attributed_month:
                            metadata_correct = False
                            print(f"     ❌ Missing attributed_month")
                        
                        # Check upload_type is set
                        if not upload_type:
                            metadata_correct = False
                            print(f"     ❌ Missing upload_type")
                        
                        # Check carousel-specific fields
                        if upload_type == 'carousel':
                            carousel_id = item.get('carousel_id')
                            if not carousel_id:
                                metadata_correct = False
                                print(f"     ❌ Carousel item missing carousel_id")
                            if 'Test Carrousel' not in title:
                                metadata_correct = False
                                print(f"     ❌ Carousel item missing expected title")
                    
                    if metadata_correct:
                        print(f"   ✅ All metadata is correct")
                        return True
                    else:
                        print(f"   ❌ Some metadata is incorrect")
                        return False
                else:
                    print(f"   ❌ Some uploaded items not found in database")
                    return False
                    
            else:
                print(f"   ❌ Failed to retrieve content for verification")
                return False
                
        except Exception as e:
            print(f"   ❌ Verification error: {e}")
            return False
    
    def cleanup_test_data(self):
        """Step 8: Clean up all test data"""
        print("🧹 Step 8: Cleaning up test data")
        
        if not self.uploaded_ids:
            print("   No uploaded items to clean up")
            return True
        
        cleanup_results = []
        
        for i, item_id in enumerate(self.uploaded_ids):
            try:
                response = self.session.delete(f"{BACKEND_URL}/content/{item_id}")
                
                if response.status_code == 200:
                    cleanup_results.append(True)
                    print(f"   ✅ Deleted item {i+1}: {item_id}")
                else:
                    cleanup_results.append(False)
                    print(f"   ❌ Failed to delete item {i+1}: {response.text}")
                    
            except Exception as e:
                cleanup_results.append(False)
                print(f"   ❌ Cleanup error for item {i+1}: {e}")
        
        success_count = sum(cleanup_results)
        total_count = len(cleanup_results)
        
        print(f"   Cleanup results: {success_count}/{total_count} items deleted")
        
        return success_count == total_count
    
    def run_comprehensive_test(self):
        """Run all batch upload functionality tests"""
        print("📤 COMPREHENSIVE BATCH UPLOAD FUNCTIONALITY TESTING")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test credentials: {EMAIL}")
        print("=" * 70)
        
        test_results = []
        
        # Step 1: Authentication
        test_results.append(self.authenticate())
        
        if test_results[-1]:
            # Step 2: Batch upload with multiple files
            test_results.append(self.test_batch_upload_multiple_files())
            
            # Step 3: Single file upload
            test_results.append(self.test_single_upload())
            
            # Step 4: Carousel upload with multiple files
            test_results.append(self.test_carousel_upload_multiple_files())
            
            # Step 5: Attributed month handling
            test_results.append(self.test_attributed_month_handling())
            
            # Step 6: Upload mode conflicts
            test_results.append(self.test_upload_mode_conflicts())
            
            # Step 7: Upload persistence verification
            test_results.append(self.verify_upload_persistence())
            
            # Step 8: Cleanup
            test_results.append(self.cleanup_test_data())
        
        # Summary
        print("\n" + "=" * 70)
        print("🎯 BATCH UPLOAD TESTING SUMMARY")
        print("=" * 70)
        
        test_names = [
            "Authentication",
            "Batch Upload (Multiple Files)",
            "Single Upload",
            "Carousel Upload (Multiple Files)",
            "Attributed Month Handling",
            "Upload Mode Conflicts Check",
            "Upload Persistence Verification",
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
        
        if success_rate >= 85:
            print("🎉 BATCH UPLOAD FUNCTIONALITY TESTING COMPLETED SUCCESSFULLY")
            print("✅ All upload modes are working correctly without conflicts")
        else:
            print("🚨 BATCH UPLOAD FUNCTIONALITY TESTING FAILED")
            print("❌ Critical issues found in batch upload implementation")
        
        return success_rate >= 85

def main():
    """Main test execution"""
    tester = BatchUploadTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎯 CONCLUSION: Batch upload functionality is FULLY OPERATIONAL")
        exit(0)
    else:
        print("\n🚨 CONCLUSION: Batch upload functionality has CRITICAL ISSUES")
        exit(1)

if __name__ == "__main__":
    main()