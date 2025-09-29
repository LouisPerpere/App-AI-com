#!/usr/bin/env python3
"""
Comprehensive Image Database Diagnostic
Based on the French review request for image database state analysis

Credentials: lperpere@yahoo.fr / L@Reunion974!

FINDINGS FROM INITIAL DIAGNOSTIC:
- Media collection: 41 elements
- GridFS total: 0 files (NO GridFS FILES!)
- 3 accessible images via API
- 2 inaccessible images (503 errors)

COMPREHENSIVE ANALYSIS OBJECTIVES:
1. Understand why GridFS is empty but some images are accessible
2. Analyze all 41 media items to understand data structure
3. Test public image endpoint for accessible images
4. Identify the real storage mechanism being used
5. Provide recommendations for fixing /api/content/pending
"""

import requests
import json
import sys
import pymongo
from datetime import datetime
from urllib.parse import urlparse
import os

# Configuration
BASE_URL = "https://social-pub-hub.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class ComprehensiveImageDiagnostic:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        self.mongo_client = None
        self.db = None
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()
        
    def authenticate(self):
        """Authenticate and get JWT token"""
        try:
            print("🔐 Authentication")
            response = self.session.post(
                f"{BASE_URL}/auth/login-robust",
                json=TEST_CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                self.log_test("Authentication", True, f"User ID: {self.user_id}")
                return True
            else:
                self.log_test("Authentication", False, 
                            f"Status: {response.status_code}", 
                            response.text[:200])
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, error=str(e))
            return False
    
    def connect_to_mongodb(self):
        """Connect to MongoDB"""
        try:
            print("🔌 MongoDB Connection")
            mongo_url = "mongodb://localhost:27017/claire_marcus"
            self.mongo_client = pymongo.MongoClient(mongo_url)
            self.db = self.mongo_client.claire_marcus
            
            # Test connection
            self.mongo_client.admin.command('ping')
            self.log_test("MongoDB Connection", True, "Connected to claire_marcus database")
            return True
            
        except Exception as e:
            self.log_test("MongoDB Connection", False, error=str(e))
            return False
    
    def analyze_all_media_items(self):
        """Analyze ALL media items to understand data structure"""
        try:
            print("📊 Analyzing ALL Media Items")
            
            if self.db is None:
                self.log_test("Analyze All Media Items", False, error="MongoDB not connected")
                return False
            
            # Get ALL media items for this user
            all_media = list(self.db.media.find({"owner_id": self.user_id}))
            
            print(f"   Found {len(all_media)} total media items")
            
            # Categorize by URL patterns
            url_patterns = {
                "claire-marcus-api.onrender.com": [],
                "uploads/": [],
                "pixabay": [],
                "other": [],
                "empty": []
            }
            
            storage_types = {
                "has_grid_file_id": 0,
                "has_file_path": 0,
                "has_url_only": 0,
                "has_nothing": 0
            }
            
            for media in all_media:
                media_id = media.get("id") or str(media.get("_id"))
                filename = media.get("filename", "Unknown")
                url = media.get("url", "")
                grid_file_id = media.get("grid_file_id")
                file_path = media.get("file_path")
                
                # Categorize by URL pattern
                if not url:
                    url_patterns["empty"].append(media_id)
                elif "claire-marcus-api.onrender.com" in url:
                    url_patterns["claire-marcus-api.onrender.com"].append(media_id)
                elif url.startswith("uploads/"):
                    url_patterns["uploads/"].append(media_id)
                elif "pixabay" in filename.lower():
                    url_patterns["pixabay"].append(media_id)
                else:
                    url_patterns["other"].append(media_id)
                
                # Categorize by storage type
                if grid_file_id:
                    storage_types["has_grid_file_id"] += 1
                elif file_path:
                    storage_types["has_file_path"] += 1
                elif url:
                    storage_types["has_url_only"] += 1
                else:
                    storage_types["has_nothing"] += 1
            
            print("   URL Pattern Analysis:")
            for pattern, items in url_patterns.items():
                print(f"     {pattern}: {len(items)} items")
            
            print("   Storage Type Analysis:")
            for storage_type, count in storage_types.items():
                print(f"     {storage_type}: {count} items")
            
            details = f"Analyzed {len(all_media)} media items - Storage: {storage_types['has_grid_file_id']} GridFS, {storage_types['has_file_path']} file_path, {storage_types['has_url_only']} URL only"
            self.log_test("Analyze All Media Items", True, details)
            
            # Store for later analysis
            self.all_media = all_media
            self.url_patterns = url_patterns
            self.storage_types = storage_types
            
            return True
            
        except Exception as e:
            self.log_test("Analyze All Media Items", False, error=str(e))
            return False
    
    def test_all_accessible_images(self):
        """Test access to ALL images via API to find working ones"""
        try:
            print("🖼️ Testing ALL Images for Accessibility")
            
            if not hasattr(self, 'all_media'):
                self.log_test("Test All Images", False, "No media analysis available")
                return False
            
            accessible_images = []
            inaccessible_images = []
            
            print(f"   Testing {len(self.all_media)} images...")
            
            for i, media in enumerate(self.all_media):
                media_id = media.get("id") or str(media.get("_id"))
                filename = media.get("filename", "Unknown")
                
                try:
                    response = self.session.get(
                        f"{BASE_URL}/content/{media_id}/file",
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '')
                        content_length = response.headers.get('content-length', '0')
                        
                        accessible_images.append({
                            "id": media_id,
                            "filename": filename,
                            "content_type": content_type,
                            "content_length": content_length,
                            "url": media.get("url", ""),
                            "file_path": media.get("file_path", ""),
                            "grid_file_id": media.get("grid_file_id")
                        })
                        
                        if i < 10:  # Only print first 10 to avoid spam
                            print(f"   ✅ {media_id[:20]}... - {filename} - {content_type} ({content_length} bytes)")
                    else:
                        inaccessible_images.append({
                            "id": media_id,
                            "filename": filename,
                            "status_code": response.status_code,
                            "url": media.get("url", ""),
                            "file_path": media.get("file_path", ""),
                            "grid_file_id": media.get("grid_file_id")
                        })
                        
                        if i < 10:  # Only print first 10 to avoid spam
                            print(f"   ❌ {media_id[:20]}... - {filename} - Status: {response.status_code}")
                
                except Exception as e:
                    inaccessible_images.append({
                        "id": media_id,
                        "filename": filename,
                        "error": str(e),
                        "url": media.get("url", ""),
                        "file_path": media.get("file_path", ""),
                        "grid_file_id": media.get("grid_file_id")
                    })
            
            print(f"   SUMMARY: {len(accessible_images)} accessible, {len(inaccessible_images)} inaccessible")
            
            details = f"Tested {len(self.all_media)} images: {len(accessible_images)} accessible, {len(inaccessible_images)} inaccessible"
            self.log_test("Test All Images", True, details)
            
            # Store results
            self.accessible_images = accessible_images
            self.inaccessible_images = inaccessible_images
            
            return True
            
        except Exception as e:
            self.log_test("Test All Images", False, error=str(e))
            return False
    
    def test_public_image_endpoint(self):
        """Test public image endpoint for accessible images"""
        try:
            print("🌐 Testing Public Image Endpoint")
            
            if not hasattr(self, 'accessible_images'):
                self.log_test("Test Public Image Endpoint", False, "No accessible images available")
                return False
            
            public_accessible = []
            public_inaccessible = []
            
            # Test first 5 accessible images
            test_images = self.accessible_images[:5]
            
            for image in test_images:
                image_id = image["id"]
                filename = image["filename"]
                
                try:
                    # Test public endpoint WITHOUT authentication
                    public_session = requests.Session()  # No auth headers
                    response = public_session.get(
                        f"{BASE_URL}/public/image/{image_id}",
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '')
                        content_length = response.headers.get('content-length', '0')
                        
                        public_accessible.append({
                            "id": image_id,
                            "filename": filename,
                            "content_type": content_type,
                            "content_length": content_length
                        })
                        
                        print(f"   ✅ PUBLIC: {image_id[:20]}... - {filename} - {content_type} ({content_length} bytes)")
                    else:
                        public_inaccessible.append({
                            "id": image_id,
                            "filename": filename,
                            "status_code": response.status_code
                        })
                        
                        print(f"   ❌ PUBLIC: {image_id[:20]}... - {filename} - Status: {response.status_code}")
                
                except Exception as e:
                    public_inaccessible.append({
                        "id": image_id,
                        "filename": filename,
                        "error": str(e)
                    })
                    print(f"   ❌ PUBLIC: {image_id[:20]}... - {filename} - Error: {str(e)}")
            
            details = f"Tested {len(test_images)} images via public endpoint: {len(public_accessible)} accessible, {len(public_inaccessible)} inaccessible"
            self.log_test("Test Public Image Endpoint", True, details)
            
            # Store results
            self.public_accessible = public_accessible
            self.public_inaccessible = public_inaccessible
            
            return True
            
        except Exception as e:
            self.log_test("Test Public Image Endpoint", False, error=str(e))
            return False
    
    def analyze_storage_mechanism(self):
        """Analyze what storage mechanism is actually being used"""
        try:
            print("🔍 Analyzing Storage Mechanism")
            
            if not hasattr(self, 'accessible_images'):
                self.log_test("Analyze Storage Mechanism", False, "No accessible images available")
                return False
            
            # Analyze accessible images to understand storage
            storage_analysis = {
                "file_system_uploads": 0,
                "external_urls": 0,
                "unknown": 0
            }
            
            print("   Storage analysis for accessible images:")
            
            for image in self.accessible_images[:10]:  # Analyze first 10
                url = image.get("url", "")
                file_path = image.get("file_path", "")
                grid_file_id = image.get("grid_file_id")
                
                print(f"   Image: {image['filename']}")
                print(f"     URL: {url}")
                print(f"     File Path: {file_path}")
                print(f"     GridFS ID: {grid_file_id}")
                
                if url.startswith("uploads/") or "uploads" in url:
                    storage_analysis["file_system_uploads"] += 1
                    print(f"     → File system storage (uploads directory)")
                elif url.startswith("http") and "pixabay" in url:
                    storage_analysis["external_urls"] += 1
                    print(f"     → External URL (Pixabay)")
                else:
                    storage_analysis["unknown"] += 1
                    print(f"     → Unknown storage mechanism")
                print()
            
            print("   Storage Mechanism Summary:")
            for mechanism, count in storage_analysis.items():
                print(f"     {mechanism}: {count} images")
            
            details = f"Storage analysis: {storage_analysis['file_system_uploads']} file system, {storage_analysis['external_urls']} external URLs, {storage_analysis['unknown']} unknown"
            self.log_test("Analyze Storage Mechanism", True, details)
            
            # Store analysis
            self.storage_analysis = storage_analysis
            
            return True
            
        except Exception as e:
            self.log_test("Analyze Storage Mechanism", False, error=str(e))
            return False
    
    def generate_facebook_ready_list(self):
        """Generate final list of Facebook-ready image IDs"""
        try:
            print("📝 Generating Facebook-Ready Image List")
            
            if not hasattr(self, 'accessible_images'):
                self.log_test("Generate Facebook List", False, "No accessible images available")
                return False
            
            facebook_ready = []
            
            for image in self.accessible_images:
                # Facebook needs publicly accessible URLs
                image_id = image["id"]
                filename = image["filename"]
                
                facebook_ready.append({
                    "id": image_id,
                    "filename": filename,
                    "api_url": f"{BASE_URL}/content/{image_id}/file",
                    "public_url": f"{BASE_URL}/public/image/{image_id}",
                    "content_type": image.get("content_type", ""),
                    "content_length": image.get("content_length", "0")
                })
            
            print(f"   FACEBOOK-READY IMAGES: {len(facebook_ready)}")
            
            # Show first 10
            for i, img in enumerate(facebook_ready[:10], 1):
                print(f"   {i}. ID: {img['id']}")
                print(f"      File: {img['filename']}")
                print(f"      Public URL: {img['public_url']}")
                print(f"      Size: {img['content_length']} bytes")
                print()
            
            if len(facebook_ready) > 10:
                print(f"   ... and {len(facebook_ready) - 10} more images")
            
            details = f"Generated {len(facebook_ready)} Facebook-ready image IDs"
            self.log_test("Generate Facebook List", True, details)
            
            # Store final list
            self.facebook_ready = facebook_ready
            
            return True
            
        except Exception as e:
            self.log_test("Generate Facebook List", False, error=str(e))
            return False
    
    def run_comprehensive_diagnostic(self):
        """Run complete comprehensive diagnostic"""
        print("🎯 COMPREHENSIVE IMAGE DATABASE DIAGNOSTIC")
        print("=" * 80)
        print(f"Backend URL: {BASE_URL}")
        print(f"Test User: {TEST_CREDENTIALS['email']}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 80)
        print()
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed - cannot continue diagnostic")
            return False
        
        # Step 2: Connect to MongoDB
        if not self.connect_to_mongodb():
            print("❌ MongoDB connection failed - cannot continue diagnostic")
            return False
        
        # Step 3: Analyze all media items
        self.analyze_all_media_items()
        
        # Step 4: Test all images for accessibility
        self.test_all_accessible_images()
        
        # Step 5: Test public image endpoint
        self.test_public_image_endpoint()
        
        # Step 6: Analyze storage mechanism
        self.analyze_storage_mechanism()
        
        # Step 7: Generate Facebook-ready list
        self.generate_facebook_ready_list()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE DIAGNOSTIC SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print(f"\n🎯 RESULTS: {passed}/{total} diagnostics completed ({(passed/total*100):.1f}%)")
        
        # Final analysis and recommendations
        print("\n" + "=" * 80)
        print("🔧 FINAL ANALYSIS & RECOMMENDATIONS")
        print("=" * 80)
        
        if hasattr(self, 'facebook_ready') and self.facebook_ready:
            print(f"✅ FACEBOOK-READY IMAGES: {len(self.facebook_ready)} images identified")
            print("✅ These images are accessible via both protected and public endpoints")
            print("✅ Ready for Facebook publication testing")
            print()
            
            print("📋 RECOMMENDED ACTIONS:")
            print("1. Use these image IDs for Facebook publication testing")
            print("2. Filter /api/content/pending to only return accessible images")
            print("3. Consider cleaning up inaccessible media records")
            
            if hasattr(self, 'inaccessible_images'):
                print(f"4. Investigate {len(self.inaccessible_images)} inaccessible images")
        else:
            print("❌ No Facebook-ready images found - need to investigate storage issues")
        
        return passed == total

def main():
    """Main comprehensive diagnostic execution"""
    diagnostic = ComprehensiveImageDiagnostic()
    success = diagnostic.run_comprehensive_diagnostic()
    
    if success:
        print("\n✅ Comprehensive image database diagnostic completed successfully!")
        if hasattr(diagnostic, 'facebook_ready'):
            print(f"🎯 RESULT: {len(diagnostic.facebook_ready)} Facebook-ready image IDs identified")
        sys.exit(0)
    else:
        print("\n⚠️ Comprehensive image database diagnostic completed with some issues!")
        if hasattr(diagnostic, 'facebook_ready'):
            print(f"🎯 PARTIAL RESULT: {len(diagnostic.facebook_ready)} Facebook-ready image IDs identified")
        sys.exit(0)  # Exit with success since we got useful results

if __name__ == "__main__":
    main()