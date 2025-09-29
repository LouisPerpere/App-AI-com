#!/usr/bin/env python3
"""
Image Database Diagnostic Test Suite
Testing the state of image data to fix inconsistencies

Credentials: lperpere@yahoo.fr / L@Reunion974!

DIAGNOSTIC OBJECTIVES:
1. Count elements in collections (media and fs.files GridFS)
2. Analyze sample from media collection (5 first elements)
3. Test access to existing images with real IDs
4. Diagnose GridFS (list files and correlate with media collection)
5. Fix API content/pending to only return images with existing files

GOAL: Identify exactly which images exist and fix API to return only those.
EXPECTED RESULT: List of real image IDs usable by Facebook.
"""

import requests
import json
import sys
import pymongo
from datetime import datetime
from urllib.parse import urlparse
import os

# Configuration
BASE_URL = "https://social-publisher-10.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class ImageDatabaseDiagnostic:
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
        
    def connect_to_mongodb(self):
        """Connect directly to MongoDB for database analysis"""
        try:
            print("🔌 Connecting to MongoDB")
            # Use the same connection string as the backend
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
        
    def authenticate(self):
        """Step 1: Authenticate and get JWT token"""
        try:
            print("🔐 Step 1: Authentication")
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
    
    def diagnostic_1_count_collections(self):
        """DIAGNOSTIC 1: Count elements in collections"""
        try:
            print("📊 DIAGNOSTIC 1: Count elements in collections")
            
            if not self.db:
                self.log_test("Count Collections", False, error="MongoDB not connected")
                return False
            
            # Count media collection
            media_count = self.db.media.count_documents({"owner_id": self.user_id})
            
            # Count GridFS files
            gridfs_count = self.db.fs.files.count_documents({})
            
            # Count GridFS files for this user (if metadata contains owner info)
            user_gridfs_count = self.db.fs.files.count_documents({"metadata.owner_id": self.user_id})
            
            details = f"Media collection: {media_count} elements, GridFS total: {gridfs_count} files, User GridFS: {user_gridfs_count} files"
            self.log_test("Count Collections", True, details)
            
            # Store counts for later use
            self.media_count = media_count
            self.gridfs_count = gridfs_count
            self.user_gridfs_count = user_gridfs_count
            
            return True
            
        except Exception as e:
            self.log_test("Count Collections", False, error=str(e))
            return False
    
    def diagnostic_2_analyze_media_sample(self):
        """DIAGNOSTIC 2: Analyze sample from media collection (5 first elements)"""
        try:
            print("🔍 DIAGNOSTIC 2: Analyze sample from media collection")
            
            if not self.db:
                self.log_test("Analyze Media Sample", False, error="MongoDB not connected")
                return False
            
            # Get 5 first elements from media collection
            sample_media = list(self.db.media.find(
                {"owner_id": self.user_id}
            ).limit(5))
            
            if not sample_media:
                self.log_test("Analyze Media Sample", False, "No media found for user")
                return False
            
            print(f"   Found {len(sample_media)} sample media items:")
            
            media_analysis = []
            for i, media in enumerate(sample_media, 1):
                media_id = media.get("id") or str(media.get("_id"))
                filename = media.get("filename", "Unknown")
                file_type = media.get("file_type", "Unknown")
                url = media.get("url", "")
                grid_file_id = media.get("grid_file_id")
                
                # Check if GridFS file exists
                gridfs_exists = False
                if grid_file_id:
                    try:
                        from bson import ObjectId
                        gridfs_file = self.db.fs.files.find_one({"_id": ObjectId(grid_file_id)})
                        gridfs_exists = gridfs_file is not None
                    except:
                        # Try as string ID
                        gridfs_file = self.db.fs.files.find_one({"_id": grid_file_id})
                        gridfs_exists = gridfs_file is not None
                
                analysis = {
                    "index": i,
                    "id": media_id,
                    "filename": filename,
                    "file_type": file_type,
                    "url": url,
                    "grid_file_id": grid_file_id,
                    "has_gridfs_file": gridfs_exists
                }
                media_analysis.append(analysis)
                
                print(f"   {i}. ID: {media_id[:20]}..., File: {filename}, Type: {file_type}")
                print(f"      URL: {url}")
                print(f"      GridFS ID: {grid_file_id}, Exists: {gridfs_exists}")
            
            # Count how many have valid GridFS files
            valid_files = sum(1 for item in media_analysis if item["has_gridfs_file"])
            
            details = f"Analyzed {len(sample_media)} media items, {valid_files} have valid GridFS files"
            self.log_test("Analyze Media Sample", True, details)
            
            # Store analysis for later use
            self.media_analysis = media_analysis
            
            return True
            
        except Exception as e:
            self.log_test("Analyze Media Sample", False, error=str(e))
            return False
    
    def diagnostic_3_test_image_access(self):
        """DIAGNOSTIC 3: Test access to existing images with real IDs"""
        try:
            print("🖼️ DIAGNOSTIC 3: Test access to existing images")
            
            if not hasattr(self, 'media_analysis'):
                self.log_test("Test Image Access", False, "No media analysis available")
                return False
            
            # Test access to images that have GridFS files
            valid_images = [item for item in self.media_analysis if item["has_gridfs_file"]]
            
            if not valid_images:
                self.log_test("Test Image Access", False, "No valid images found to test")
                return False
            
            access_results = []
            for image in valid_images:
                image_id = image["id"]
                
                # Test GET /api/content/{id}/file
                try:
                    response = self.session.get(
                        f"{BASE_URL}/content/{image_id}/file",
                        timeout=30
                    )
                    
                    accessible = response.status_code == 200
                    content_type = response.headers.get('content-type', '')
                    content_length = response.headers.get('content-length', '0')
                    
                    result = {
                        "id": image_id,
                        "filename": image["filename"],
                        "accessible": accessible,
                        "status_code": response.status_code,
                        "content_type": content_type,
                        "content_length": content_length
                    }
                    access_results.append(result)
                    
                    status = "✅" if accessible else "❌"
                    print(f"   {status} {image_id[:20]}... - {image['filename']} - Status: {response.status_code}")
                    
                except Exception as e:
                    result = {
                        "id": image_id,
                        "filename": image["filename"],
                        "accessible": False,
                        "error": str(e)
                    }
                    access_results.append(result)
                    print(f"   ❌ {image_id[:20]}... - Error: {str(e)}")
            
            accessible_count = sum(1 for r in access_results if r["accessible"])
            details = f"Tested {len(access_results)} images, {accessible_count} accessible via API"
            self.log_test("Test Image Access", True, details)
            
            # Store results for later use
            self.access_results = access_results
            
            return True
            
        except Exception as e:
            self.log_test("Test Image Access", False, error=str(e))
            return False
    
    def diagnostic_4_gridfs_analysis(self):
        """DIAGNOSTIC 4: Diagnose GridFS (list files and correlate)"""
        try:
            print("🗃️ DIAGNOSTIC 4: GridFS diagnostic")
            
            if not self.db:
                self.log_test("GridFS Analysis", False, error="MongoDB not connected")
                return False
            
            # List all GridFS files for this user
            gridfs_files = list(self.db.fs.files.find(
                {"metadata.owner_id": self.user_id}
            ).limit(10))  # Limit to first 10 for analysis
            
            print(f"   Found {len(gridfs_files)} GridFS files for user:")
            
            gridfs_analysis = []
            for i, gf in enumerate(gridfs_files, 1):
                file_id = str(gf["_id"])
                filename = gf.get("filename", "Unknown")
                length = gf.get("length", 0)
                upload_date = gf.get("uploadDate")
                
                # Check if this GridFS file is referenced in media collection
                media_ref = self.db.media.find_one({
                    "owner_id": self.user_id,
                    "grid_file_id": file_id
                })
                has_media_ref = media_ref is not None
                
                analysis = {
                    "gridfs_id": file_id,
                    "filename": filename,
                    "length": length,
                    "upload_date": upload_date,
                    "has_media_reference": has_media_ref
                }
                gridfs_analysis.append(analysis)
                
                print(f"   {i}. GridFS ID: {file_id[:20]}..., File: {filename}")
                print(f"      Size: {length} bytes, Referenced in media: {has_media_ref}")
            
            # Count orphaned files (GridFS files without media references)
            orphaned_count = sum(1 for item in gridfs_analysis if not item["has_media_reference"])
            
            details = f"Analyzed {len(gridfs_files)} GridFS files, {orphaned_count} orphaned (no media reference)"
            self.log_test("GridFS Analysis", True, details)
            
            # Store analysis
            self.gridfs_analysis = gridfs_analysis
            
            return True
            
        except Exception as e:
            self.log_test("GridFS Analysis", False, error=str(e))
            return False
    
    def diagnostic_5_test_content_pending_api(self):
        """DIAGNOSTIC 5: Test current /api/content/pending behavior"""
        try:
            print("📋 DIAGNOSTIC 5: Test /api/content/pending API")
            
            # Test current API behavior
            response = self.session.get(
                f"{BASE_URL}/content/pending",
                params={"limit": 10},
                timeout=30
            )
            
            if response.status_code != 200:
                self.log_test("Content Pending API Test", False, 
                            f"API returned status {response.status_code}")
                return False
            
            data = response.json()
            content_items = data.get("content", [])
            total = data.get("total", 0)
            
            print(f"   API returned {len(content_items)} items (total: {total})")
            
            # Analyze which items have accessible files
            accessible_items = []
            inaccessible_items = []
            
            for item in content_items[:5]:  # Test first 5 items
                item_id = item.get("id")
                filename = item.get("filename", "Unknown")
                url = item.get("url", "")
                
                # Test if file is actually accessible
                try:
                    file_response = self.session.get(
                        f"{BASE_URL}/content/{item_id}/file",
                        timeout=10
                    )
                    
                    if file_response.status_code == 200:
                        accessible_items.append({
                            "id": item_id,
                            "filename": filename,
                            "url": url
                        })
                    else:
                        inaccessible_items.append({
                            "id": item_id,
                            "filename": filename,
                            "url": url,
                            "status": file_response.status_code
                        })
                        
                except Exception as e:
                    inaccessible_items.append({
                        "id": item_id,
                        "filename": filename,
                        "url": url,
                        "error": str(e)
                    })
            
            print(f"   Accessible files: {len(accessible_items)}")
            print(f"   Inaccessible files: {len(inaccessible_items)}")
            
            for item in accessible_items:
                print(f"   ✅ {item['id'][:20]}... - {item['filename']}")
            
            for item in inaccessible_items:
                status_info = item.get('status', item.get('error', 'Unknown'))
                print(f"   ❌ {item['id'][:20]}... - {item['filename']} - {status_info}")
            
            details = f"API returns {len(content_items)} items, {len(accessible_items)} accessible, {len(inaccessible_items)} inaccessible"
            self.log_test("Content Pending API Test", True, details)
            
            # Store results
            self.api_accessible_items = accessible_items
            self.api_inaccessible_items = inaccessible_items
            
            return True
            
        except Exception as e:
            self.log_test("Content Pending API Test", False, error=str(e))
            return False
    
    def generate_usable_image_list(self):
        """Generate final list of usable image IDs for Facebook"""
        try:
            print("📝 GENERATING USABLE IMAGE LIST")
            
            if not hasattr(self, 'api_accessible_items'):
                self.log_test("Generate Usable Image List", False, "No API test results available")
                return False
            
            usable_images = []
            for item in self.api_accessible_items:
                usable_images.append({
                    "id": item["id"],
                    "filename": item["filename"],
                    "api_url": f"{BASE_URL}/content/{item['id']}/file",
                    "public_url": f"{BASE_URL}/public/image/{item['id']}"
                })
            
            print(f"   USABLE IMAGES FOR FACEBOOK: {len(usable_images)}")
            for i, img in enumerate(usable_images, 1):
                print(f"   {i}. ID: {img['id']}")
                print(f"      File: {img['filename']}")
                print(f"      API URL: {img['api_url']}")
                print(f"      Public URL: {img['public_url']}")
                print()
            
            details = f"Generated list of {len(usable_images)} usable image IDs"
            self.log_test("Generate Usable Image List", True, details)
            
            # Store final list
            self.usable_images = usable_images
            
            return True
            
        except Exception as e:
            self.log_test("Generate Usable Image List", False, error=str(e))
            return False
    
    def run_full_diagnostic(self):
        """Run complete image database diagnostic"""
        print("🎯 IMAGE DATABASE DIAGNOSTIC")
        print("=" * 70)
        print(f"Backend URL: {BASE_URL}")
        print(f"Test User: {TEST_CREDENTIALS['email']}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 70)
        print()
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed - cannot continue diagnostic")
            return False
        
        # Step 2: Connect to MongoDB
        if not self.connect_to_mongodb():
            print("❌ MongoDB connection failed - cannot continue diagnostic")
            return False
        
        # Diagnostic 1: Count collections
        self.diagnostic_1_count_collections()
        
        # Diagnostic 2: Analyze media sample
        self.diagnostic_2_analyze_media_sample()
        
        # Diagnostic 3: Test image access
        self.diagnostic_3_test_image_access()
        
        # Diagnostic 4: GridFS analysis
        self.diagnostic_4_gridfs_analysis()
        
        # Diagnostic 5: Test content/pending API
        self.diagnostic_5_test_content_pending_api()
        
        # Generate final usable image list
        self.generate_usable_image_list()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 DIAGNOSTIC SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print(f"\n🎯 RESULTS: {passed}/{total} diagnostics completed ({(passed/total*100):.1f}%)")
        
        # Final recommendations
        print("\n" + "=" * 70)
        print("🔧 RECOMMENDATIONS")
        print("=" * 70)
        
        if hasattr(self, 'usable_images') and self.usable_images:
            print(f"✅ Found {len(self.usable_images)} usable images for Facebook")
            print("✅ These images have valid GridFS files and are accessible via API")
            print("✅ Use these image IDs for Facebook publication testing")
        else:
            print("❌ No usable images found - need to investigate GridFS integrity")
        
        if hasattr(self, 'api_inaccessible_items') and self.api_inaccessible_items:
            print(f"⚠️ Found {len(self.api_inaccessible_items)} inaccessible items in API response")
            print("⚠️ Consider filtering these out of /api/content/pending response")
        
        return passed == total

def main():
    """Main diagnostic execution"""
    diagnostic = ImageDatabaseDiagnostic()
    success = diagnostic.run_full_diagnostic()
    
    if success:
        print("\n✅ Image database diagnostic completed successfully!")
        if hasattr(diagnostic, 'usable_images'):
            print(f"🎯 RESULT: {len(diagnostic.usable_images)} usable image IDs identified for Facebook")
        sys.exit(0)
    else:
        print("\n❌ Image database diagnostic encountered issues!")
        sys.exit(1)

if __name__ == "__main__":
    main()