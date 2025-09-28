#!/usr/bin/env python3
"""
Thumbnail Optimization Testing Script
Tests the backend thumbnail generation functionality implemented in GET /api/content/pending
"""

import requests
import json
import base64
import os
import tempfile
from PIL import Image
import io
from datetime import datetime

class ThumbnailOptimizationTester:
    def __init__(self):
        # Use production backend URL from frontend/.env
        self.base_url = "https://social-publisher-10.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.uploaded_file_ids = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {name}")
            if details:
                print(f"   {details}")

    def authenticate(self):
        """Authenticate with the backend"""
        print("🔐 Authenticating with backend...")
        
        login_data = {
            "email": "lperpere@yahoo.fr",
            "password": "L@Reunion974!"
        }
        
        try:
            response = requests.post(f"{self.api_url}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                self.log_test("Authentication", True, f"Token obtained: {self.access_token[:20]}...")
                return True
            else:
                self.log_test("Authentication", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Authentication", False, f"Error: {str(e)}")
            return False

    def create_test_image(self, width=800, height=600, format='JPEG'):
        """Create a test image with specified dimensions"""
        # Create a colorful test image
        image = Image.new('RGB', (width, height), color='red')
        
        # Add some visual elements to make it more realistic
        from PIL import ImageDraw
        draw = ImageDraw.Draw(image)
        
        # Draw some shapes
        draw.rectangle([50, 50, width-50, height-50], outline='blue', width=5)
        draw.ellipse([100, 100, width-100, height-100], fill='green')
        draw.text((width//2-50, height//2), "TEST IMAGE", fill='white')
        
        # Convert to bytes
        buffer = io.BytesIO()
        image.save(buffer, format=format, quality=95)
        return buffer.getvalue()

    def upload_test_images(self):
        """Upload test images of various sizes"""
        print("\n📤 Uploading test images...")
        
        if not self.access_token:
            self.log_test("Upload Test Images", False, "No authentication token")
            return False

        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        # Create test images of different sizes
        test_images = [
            ("small_image.jpg", self.create_test_image(400, 300)),
            ("medium_image.jpg", self.create_test_image(800, 600)),
            ("large_image.jpg", self.create_test_image(2400, 1800)),
            ("wide_image.jpg", self.create_test_image(1920, 1080)),
            ("tall_image.jpg", self.create_test_image(600, 1200))
        ]
        
        upload_success = True
        
        for filename, image_data in test_images:
            try:
                files = {'files': (filename, image_data, 'image/jpeg')}
                response = requests.post(f"{self.api_url}/content/batch-upload", files=files, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    uploaded_files = data.get('uploaded_files', [])
                    if uploaded_files:
                        file_id = uploaded_files[0].get('id')
                        self.uploaded_file_ids.append(file_id)
                        original_size = len(image_data)
                        self.log_test(f"Upload {filename}", True, f"Size: {original_size} bytes, ID: {file_id}")
                    else:
                        self.log_test(f"Upload {filename}", False, "No file ID returned")
                        upload_success = False
                else:
                    self.log_test(f"Upload {filename}", False, f"Status: {response.status_code}")
                    upload_success = False
                    
            except Exception as e:
                self.log_test(f"Upload {filename}", False, f"Error: {str(e)}")
                upload_success = False
        
        return upload_success

    def test_thumbnail_generation(self):
        """Test thumbnail generation in GET /api/content/pending"""
        print("\n🖼️  Testing thumbnail generation...")
        
        if not self.access_token:
            self.log_test("Thumbnail Generation", False, "No authentication token")
            return False

        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        try:
            response = requests.get(f"{self.api_url}/content/pending", headers=headers)
            
            if response.status_code != 200:
                self.log_test("Thumbnail Generation", False, f"Status: {response.status_code}")
                return False
            
            data = response.json()
            content_files = data.get('content', [])
            
            if not content_files:
                self.log_test("Thumbnail Generation", False, "No content files found")
                return False
            
            # Test each uploaded file
            thumbnail_tests_passed = 0
            total_files = len(content_files)
            
            for file_info in content_files:
                filename = file_info.get('filename', 'unknown')
                file_data = file_info.get('file_data')
                thumbnail_data = file_info.get('thumbnail_data')
                
                # Test 1: Both file_data and thumbnail_data should be present
                if file_data and thumbnail_data:
                    self.log_test(f"Data Presence - {filename}", True, "Both file_data and thumbnail_data present")
                    
                    # Test 2: Thumbnail should be smaller than full image
                    full_size = len(file_data)
                    thumb_size = len(thumbnail_data)
                    
                    if thumb_size < full_size:
                        reduction_percent = ((full_size - thumb_size) / full_size) * 100
                        self.log_test(f"Size Reduction - {filename}", True, 
                                    f"Full: {full_size} bytes, Thumb: {thumb_size} bytes ({reduction_percent:.1f}% reduction)")
                        
                        # Test 3: Verify thumbnail dimensions
                        try:
                            thumb_image_data = base64.b64decode(thumbnail_data)
                            thumb_image = Image.open(io.BytesIO(thumb_image_data))
                            thumb_width, thumb_height = thumb_image.size
                            
                            # Thumbnail should be max 150px on smallest side
                            min_dimension = min(thumb_width, thumb_height)
                            if min_dimension <= 150:
                                self.log_test(f"Thumbnail Dimensions - {filename}", True, 
                                            f"Dimensions: {thumb_width}x{thumb_height} (min: {min_dimension}px)")
                                
                                # Test 4: Verify aspect ratio is maintained
                                full_image_data = base64.b64decode(file_data)
                                full_image = Image.open(io.BytesIO(full_image_data))
                                full_width, full_height = full_image.size
                                
                                full_ratio = full_width / full_height
                                thumb_ratio = thumb_width / thumb_height
                                ratio_diff = abs(full_ratio - thumb_ratio)
                                
                                if ratio_diff < 0.01:  # Allow small floating point differences
                                    self.log_test(f"Aspect Ratio - {filename}", True, 
                                                f"Full: {full_ratio:.3f}, Thumb: {thumb_ratio:.3f}")
                                    thumbnail_tests_passed += 1
                                else:
                                    self.log_test(f"Aspect Ratio - {filename}", False, 
                                                f"Ratio mismatch: Full: {full_ratio:.3f}, Thumb: {thumb_ratio:.3f}")
                            else:
                                self.log_test(f"Thumbnail Dimensions - {filename}", False, 
                                            f"Too large: {thumb_width}x{thumb_height} (min: {min_dimension}px)")
                        except Exception as e:
                            self.log_test(f"Thumbnail Analysis - {filename}", False, f"Error: {str(e)}")
                    else:
                        self.log_test(f"Size Reduction - {filename}", False, 
                                    f"Thumbnail not smaller: Full: {full_size}, Thumb: {thumb_size}")
                else:
                    self.log_test(f"Data Presence - {filename}", False, 
                                f"Missing data - file_data: {bool(file_data)}, thumbnail_data: {bool(thumbnail_data)}")
            
            # Overall success if most thumbnails passed
            success_rate = (thumbnail_tests_passed / total_files) * 100 if total_files > 0 else 0
            overall_success = success_rate >= 80  # 80% success rate threshold
            
            self.log_test("Overall Thumbnail Generation", overall_success, 
                        f"Success rate: {success_rate:.1f}% ({thumbnail_tests_passed}/{total_files} files)")
            
            return overall_success
            
        except Exception as e:
            self.log_test("Thumbnail Generation", False, f"Error: {str(e)}")
            return False

    def test_performance_comparison(self):
        """Test performance comparison between full images and thumbnails"""
        print("\n⚡ Testing performance comparison...")
        
        if not self.access_token:
            self.log_test("Performance Comparison", False, "No authentication token")
            return False

        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        try:
            response = requests.get(f"{self.api_url}/content/pending", headers=headers)
            
            if response.status_code != 200:
                self.log_test("Performance Comparison", False, f"Status: {response.status_code}")
                return False
            
            data = response.json()
            content_files = data.get('content', [])
            
            if not content_files:
                self.log_test("Performance Comparison", False, "No content files found")
                return False
            
            total_full_size = 0
            total_thumb_size = 0
            file_count = 0
            
            for file_info in content_files:
                file_data = file_info.get('file_data')
                thumbnail_data = file_info.get('thumbnail_data')
                
                if file_data and thumbnail_data:
                    total_full_size += len(file_data)
                    total_thumb_size += len(thumbnail_data)
                    file_count += 1
            
            if file_count > 0:
                # Calculate savings
                total_savings = total_full_size - total_thumb_size
                savings_percent = (total_savings / total_full_size) * 100
                
                # Calculate memory usage estimates
                full_mb = total_full_size / (1024 * 1024)
                thumb_mb = total_thumb_size / (1024 * 1024)
                
                # Estimate performance improvement (based on data transfer and memory usage)
                transfer_improvement = savings_percent
                memory_improvement = savings_percent
                
                self.log_test("Performance Comparison", True, 
                            f"Files: {file_count}, Full: {full_mb:.2f}MB, Thumbs: {thumb_mb:.2f}MB")
                self.log_test("Data Transfer Savings", True, 
                            f"{savings_percent:.1f}% reduction ({total_savings:,} bytes saved)")
                self.log_test("Memory Usage Estimate", True, 
                            f"Gallery view: {memory_improvement:.1f}% less memory usage")
                self.log_test("Performance Improvement", True, 
                            f"Estimated {transfer_improvement:.1f}% faster gallery loading")
                
                return True
            else:
                self.log_test("Performance Comparison", False, "No valid files for comparison")
                return False
                
        except Exception as e:
            self.log_test("Performance Comparison", False, f"Error: {str(e)}")
            return False

    def test_image_quality_verification(self):
        """Test that thumbnails maintain acceptable quality"""
        print("\n🎨 Testing image quality verification...")
        
        if not self.access_token:
            self.log_test("Image Quality", False, "No authentication token")
            return False

        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        try:
            response = requests.get(f"{self.api_url}/content/pending", headers=headers)
            
            if response.status_code != 200:
                self.log_test("Image Quality", False, f"Status: {response.status_code}")
                return False
            
            data = response.json()
            content_files = data.get('content', [])
            
            quality_tests_passed = 0
            total_files = len(content_files)
            
            for file_info in content_files:
                filename = file_info.get('filename', 'unknown')
                thumbnail_data = file_info.get('thumbnail_data')
                
                if thumbnail_data:
                    try:
                        # Decode and analyze thumbnail
                        thumb_image_data = base64.b64decode(thumbnail_data)
                        thumb_image = Image.open(io.BytesIO(thumb_image_data))
                        
                        # Test 1: Image should be in JPEG format
                        if thumb_image.format == 'JPEG':
                            self.log_test(f"Format - {filename}", True, "JPEG format confirmed")
                            
                            # Test 2: Image should have proper color mode
                            if thumb_image.mode in ['RGB', 'L']:
                                self.log_test(f"Color Mode - {filename}", True, f"Mode: {thumb_image.mode}")
                                
                                # Test 3: Image should be properly encoded (no corruption)
                                width, height = thumb_image.size
                                if width > 0 and height > 0:
                                    self.log_test(f"Integrity - {filename}", True, f"Valid image: {width}x{height}")
                                    quality_tests_passed += 1
                                else:
                                    self.log_test(f"Integrity - {filename}", False, "Invalid dimensions")
                            else:
                                self.log_test(f"Color Mode - {filename}", False, f"Unexpected mode: {thumb_image.mode}")
                        else:
                            self.log_test(f"Format - {filename}", False, f"Unexpected format: {thumb_image.format}")
                            
                    except Exception as e:
                        self.log_test(f"Quality Analysis - {filename}", False, f"Error: {str(e)}")
                else:
                    self.log_test(f"Quality Analysis - {filename}", False, "No thumbnail data")
            
            # Overall quality assessment
            quality_rate = (quality_tests_passed / total_files) * 100 if total_files > 0 else 0
            overall_quality = quality_rate >= 90  # 90% quality threshold
            
            self.log_test("Overall Image Quality", overall_quality, 
                        f"Quality rate: {quality_rate:.1f}% ({quality_tests_passed}/{total_files} files)")
            
            return overall_quality
            
        except Exception as e:
            self.log_test("Image Quality", False, f"Error: {str(e)}")
            return False

    def cleanup_test_files(self):
        """Clean up uploaded test files"""
        print("\n🧹 Cleaning up test files...")
        
        if not self.access_token or not self.uploaded_file_ids:
            print("   No cleanup needed")
            return
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        for file_id in self.uploaded_file_ids:
            try:
                response = requests.delete(f"{self.api_url}/content/{file_id}", headers=headers)
                if response.status_code == 200:
                    print(f"   ✅ Deleted file: {file_id}")
                else:
                    print(f"   ⚠️ Could not delete file: {file_id} (Status: {response.status_code})")
            except Exception as e:
                print(f"   ❌ Error deleting file {file_id}: {str(e)}")

    def run_all_tests(self):
        """Run all thumbnail optimization tests"""
        print("🎯 THUMBNAIL OPTIMIZATION TESTING")
        print("=" * 50)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 50)
        
        # Test sequence
        test_results = []
        
        # 1. Authentication
        if self.authenticate():
            test_results.append(True)
            
            # 2. Upload test images
            if self.upload_test_images():
                test_results.append(True)
                
                # 3. Test thumbnail generation
                test_results.append(self.test_thumbnail_generation())
                
                # 4. Test performance comparison
                test_results.append(self.test_performance_comparison())
                
                # 5. Test image quality
                test_results.append(self.test_image_quality_verification())
                
                # 6. Cleanup
                self.cleanup_test_files()
            else:
                test_results.append(False)
        else:
            test_results.append(False)
        
        # Final results
        print("\n" + "=" * 50)
        print("📊 FINAL RESULTS")
        print("=" * 50)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        overall_success = all(test_results)
        if overall_success:
            print("🎉 THUMBNAIL OPTIMIZATION: WORKING CORRECTLY")
        else:
            print("❌ THUMBNAIL OPTIMIZATION: ISSUES DETECTED")
        
        return overall_success

if __name__ == "__main__":
    tester = ThumbnailOptimizationTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)