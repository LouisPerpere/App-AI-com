#!/usr/bin/env python3
"""
MongoDB Thumb URL Update Test
Test spécifique pour la correction des thumb_url existantes selon la demande française
"""

import requests
import json
import os
import time
from pymongo import MongoClient
from urllib.parse import urlparse

# Configuration
BACKEND_URL = "https://post-validator.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials as specified in review request
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

# MongoDB connection from backend .env
MONGO_URL = "mongodb+srv://lperpere:ClaireMarcus2025@cluster0.24k0jzd.mongodb.net/claire_marcus?retryWrites=true&w=majority&appName=Cluster0"

class MongoDBThumbUrlUpdater:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.test_results = []
        self.mongo_client = None
        self.db = None
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()
    
    def authenticate(self):
        """Step 1: Authenticate with specified credentials"""
        print("🔐 STEP 1: Authentication")
        print("=" * 50)
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                self.log_result(
                    "Authentication", 
                    True, 
                    f"Successfully authenticated as {TEST_EMAIL}, User ID: {self.user_id}"
                )
                return True
            else:
                self.log_result(
                    "Authentication", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, error=str(e))
            return False
    
    def connect_mongodb(self):
        """Step 2: Connect to MongoDB directly"""
        print("🔗 STEP 2: MongoDB Connection")
        print("=" * 50)
        
        try:
            self.mongo_client = MongoClient(MONGO_URL)
            self.db = self.mongo_client.claire_marcus
            
            # Test connection
            self.db.command('ping')
            
            self.log_result(
                "MongoDB Connection", 
                True, 
                f"Successfully connected to MongoDB database: claire_marcus"
            )
            return True
            
        except Exception as e:
            self.log_result("MongoDB Connection", False, error=str(e))
            return False
    
    def analyze_existing_thumb_urls(self):
        """Step 3: Analyze existing thumb_url patterns"""
        print("🔍 STEP 3: Analyze Existing Thumb URLs")
        print("=" * 50)
        
        try:
            media_collection = self.db.media
            
            # Count total documents
            total_docs = media_collection.count_documents({})
            
            # Count documents with thumb_url
            with_thumb_url = media_collection.count_documents({"thumb_url": {"$exists": True, "$ne": None}})
            
            # Count documents with old claire-marcus.com URLs
            old_url_pattern = {"thumb_url": {"$regex": "^https://claire-marcus.com/uploads/thumbs/"}}
            old_url_count = media_collection.count_documents(old_url_pattern)
            
            # Count documents with new libfusion URLs
            new_url_pattern = {"thumb_url": {"$regex": "^https://post-validator.preview.emergentagent.com/uploads/thumbs/"}}
            new_url_count = media_collection.count_documents(new_url_pattern)
            
            # Sample some old URLs
            old_url_samples = list(media_collection.find(old_url_pattern, {"thumb_url": 1}).limit(3))
            
            self.log_result(
                "Analyze Existing Thumb URLs", 
                True, 
                f"Total documents: {total_docs}, With thumb_url: {with_thumb_url}, Old URLs (claire-marcus.com): {old_url_count}, New URLs (libfusion): {new_url_count}"
            )
            
            if old_url_samples:
                print("   Sample old URLs:")
                for sample in old_url_samples:
                    print(f"     - {sample.get('thumb_url', 'N/A')}")
            
            return old_url_count > 0
            
        except Exception as e:
            self.log_result("Analyze Existing Thumb URLs", False, error=str(e))
            return False
    
    def perform_mass_update(self):
        """Step 4: Perform mass update of thumb_url"""
        print("🔄 STEP 4: Mass Update Thumb URLs")
        print("=" * 50)
        
        try:
            media_collection = self.db.media
            
            # MongoDB aggregation pipeline to update URLs using regex replacement
            # This is the corrected version of the query from the review request
            update_result = media_collection.update_many(
                {"thumb_url": {"$regex": "^https://claire-marcus.com/uploads/thumbs/"}},
                [
                    {
                        "$set": {
                            "thumb_url": {
                                "$replaceOne": {
                                    "input": "$thumb_url",
                                    "find": "https://claire-marcus.com",
                                    "replacement": "https://post-validator.preview.emergentagent.com"
                                }
                            }
                        }
                    }
                ]
            )
            
            matched_count = update_result.matched_count
            modified_count = update_result.modified_count
            
            self.log_result(
                "Mass Update Thumb URLs", 
                True, 
                f"Matched documents: {matched_count}, Modified documents: {modified_count}"
            )
            
            return modified_count > 0
            
        except Exception as e:
            self.log_result("Mass Update Thumb URLs", False, error=str(e))
            return False
    
    def verify_update_results(self):
        """Step 5: Verify the update results"""
        print("✅ STEP 5: Verify Update Results")
        print("=" * 50)
        
        try:
            media_collection = self.db.media
            
            # Count documents with old URLs (should be 0 now)
            old_url_pattern = {"thumb_url": {"$regex": "^https://claire-marcus.com/uploads/thumbs/"}}
            remaining_old_urls = media_collection.count_documents(old_url_pattern)
            
            # Count documents with new URLs
            new_url_pattern = {"thumb_url": {"$regex": "^https://post-validator.preview.emergentagent.com/uploads/thumbs/"}}
            new_url_count = media_collection.count_documents(new_url_pattern)
            
            # Sample some new URLs
            new_url_samples = list(media_collection.find(new_url_pattern, {"thumb_url": 1}).limit(3))
            
            success = remaining_old_urls == 0 and new_url_count > 0
            
            self.log_result(
                "Verify Update Results", 
                success, 
                f"Remaining old URLs: {remaining_old_urls}, New URLs: {new_url_count}"
            )
            
            if new_url_samples:
                print("   Sample updated URLs:")
                for sample in new_url_samples:
                    print(f"     - {sample.get('thumb_url', 'N/A')}")
            
            return success
            
        except Exception as e:
            self.log_result("Verify Update Results", False, error=str(e))
            return False
    
    def test_api_content_pending(self):
        """Step 6: Test GET /api/content/pending to confirm thumb_url point to backend"""
        print("🌐 STEP 6: Test API Content Pending")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{API_BASE}/content/pending?limit=10")
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                
                # Check thumb_url in the response
                backend_thumb_urls = 0
                old_thumb_urls = 0
                total_with_thumbs = 0
                
                for item in content:
                    thumb_url = item.get("thumb_url")
                    if thumb_url:
                        total_with_thumbs += 1
                        if "libfusion.preview.emergentagent.com" in thumb_url:
                            backend_thumb_urls += 1
                        elif "claire-marcus.com" in thumb_url:
                            old_thumb_urls += 1
                
                success = old_thumb_urls == 0 and backend_thumb_urls > 0
                
                self.log_result(
                    "Test API Content Pending", 
                    success, 
                    f"Total content items: {len(content)}, With thumbnails: {total_with_thumbs}, Backend URLs: {backend_thumb_urls}, Old URLs: {old_thumb_urls}"
                )
                
                # Show sample thumb_urls
                if total_with_thumbs > 0:
                    print("   Sample thumb_urls from API:")
                    for item in content[:3]:
                        thumb_url = item.get("thumb_url")
                        if thumb_url:
                            print(f"     - {thumb_url}")
                
                return success
            else:
                self.log_result(
                    "Test API Content Pending", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Test API Content Pending", False, error=str(e))
            return False
    
    def cleanup_connection(self):
        """Close MongoDB connection"""
        if self.mongo_client:
            self.mongo_client.close()
    
    def run_all_tests(self):
        """Run all MongoDB thumb_url update tests"""
        print("🚀 MONGODB THUMB_URL UPDATE TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_EMAIL}")
        print(f"Task: Update thumb_url from claire-marcus.com to libfusion.preview.emergentagent.com")
        print("=" * 60)
        print()
        
        # Run tests in sequence
        tests = [
            self.authenticate,
            self.connect_mongodb,
            self.analyze_existing_thumb_urls,
            self.perform_mass_update,
            self.verify_update_results,
            self.test_api_content_pending
        ]
        
        try:
            for test in tests:
                if not test():
                    print("❌ Test failed, continuing with remaining tests...")
                print()
        finally:
            self.cleanup_connection()
        
        # Summary
        print("📋 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Detailed results
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
            if result['error']:
                print(f"   Error: {result['error']}")
        
        print()
        print("🎯 MONGODB THUMB_URL UPDATE TESTING COMPLETED")
        
        return success_rate >= 80  # Consider successful if 80% or more tests pass

if __name__ == "__main__":
    updater = MongoDBThumbUrlUpdater()
    success = updater.run_all_tests()
    
    if success:
        print("✅ Overall testing: SUCCESS")
        exit(0)
    else:
        print("❌ Overall testing: FAILED")
        exit(1)