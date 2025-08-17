#!/usr/bin/env python3
"""
Test Suite for Thumb URL Update Request (French Review)
Testing the MongoDB update to change thumb_url from libfusion.preview.emergentagent.com to claire-marcus.com
"""

import requests
import json
import os
import pymongo
from datetime import datetime

# Configuration
BACKEND_URL = "https://libfusion.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials as specified in review request
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

# MongoDB connection (from backend/.env)
MONGO_URL = "mongodb+srv://lperpere:ClaireMarcus2025@cluster0.24k0jzd.mongodb.net/claire_marcus?retryWrites=true&w=majority&appName=Cluster0"

class ThumbUrlUpdateTester:
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
        print("🗄️ STEP 2: MongoDB Connection")
        print("=" * 50)
        
        try:
            self.mongo_client = pymongo.MongoClient(MONGO_URL)
            self.db = self.mongo_client.claire_marcus
            
            # Test connection
            self.db.admin.command('ping')
            
            self.log_result(
                "MongoDB Connection", 
                True, 
                f"Successfully connected to MongoDB database: claire_marcus"
            )
            return True
            
        except Exception as e:
            self.log_result("MongoDB Connection", False, error=str(e))
            return False
    
    def analyze_current_thumb_urls(self):
        """Step 3: Analyze current thumb_url patterns in MongoDB"""
        print("🔍 STEP 3: Current Thumb URL Analysis")
        print("=" * 50)
        
        try:
            media_collection = self.db.media
            
            # Count total documents
            total_docs = media_collection.count_documents({})
            
            # Count documents with thumb_url
            with_thumb_url = media_collection.count_documents({"thumb_url": {"$ne": None}})
            
            # Count documents with old domain (libfusion)
            old_domain_count = media_collection.count_documents({
                "thumb_url": {"$regex": "^https://libfusion.preview.emergentagent.com/uploads/thumbs/"}
            })
            
            # Count documents with new domain (claire-marcus)
            new_domain_count = media_collection.count_documents({
                "thumb_url": {"$regex": "^https://claire-marcus.com/uploads/thumbs/"}
            })
            
            # Get sample URLs
            sample_old = list(media_collection.find(
                {"thumb_url": {"$regex": "^https://libfusion.preview.emergentagent.com/uploads/thumbs/"}},
                {"thumb_url": 1}
            ).limit(3))
            
            sample_new = list(media_collection.find(
                {"thumb_url": {"$regex": "^https://claire-marcus.com/uploads/thumbs/"}},
                {"thumb_url": 1}
            ).limit(3))
            
            self.log_result(
                "Current Thumb URL Analysis", 
                True, 
                f"Total documents: {total_docs}, With thumb_url: {with_thumb_url}, Old domain (libfusion): {old_domain_count}, New domain (claire-marcus): {new_domain_count}"
            )
            
            if sample_old:
                print("   Sample old URLs:")
                for doc in sample_old:
                    print(f"     {doc['thumb_url']}")
            
            if sample_new:
                print("   Sample new URLs:")
                for doc in sample_new:
                    print(f"     {doc['thumb_url']}")
            
            # Store counts for later verification
            self.old_domain_count_before = old_domain_count
            self.new_domain_count_before = new_domain_count
            
            return True
            
        except Exception as e:
            self.log_result("Current Thumb URL Analysis", False, error=str(e))
            return False
    
    def update_thumb_urls_mongodb(self):
        """Step 4: Update thumb_url in MongoDB using the specified query"""
        print("🔄 STEP 4: MongoDB Thumb URL Update")
        print("=" * 50)
        
        try:
            media_collection = self.db.media
            
            # Execute the update query as specified in the French review
            update_query = {
                "thumb_url": {"$regex": "^https://libfusion.preview.emergentagent.com/uploads/thumbs/"}
            }
            
            update_operation = [{
                "$set": {
                    "thumb_url": {
                        "$replaceOne": {
                            "input": "$thumb_url",
                            "find": "https://libfusion.preview.emergentagent.com",
                            "replacement": "https://claire-marcus.com"
                        }
                    }
                }
            }]
            
            # Execute the update
            result = media_collection.update_many(update_query, update_operation)
            
            matched_count = result.matched_count
            modified_count = result.modified_count
            
            self.log_result(
                "MongoDB Thumb URL Update", 
                True, 
                f"Update completed. Matched: {matched_count} documents, Modified: {modified_count} documents"
            )
            
            # Store counts for verification
            self.matched_count = matched_count
            self.modified_count = modified_count
            
            return True
            
        except Exception as e:
            self.log_result("MongoDB Thumb URL Update", False, error=str(e))
            return False
    
    def verify_update_results(self):
        """Step 5: Verify the update results in MongoDB"""
        print("✅ STEP 5: Update Results Verification")
        print("=" * 50)
        
        try:
            media_collection = self.db.media
            
            # Count documents with old domain after update
            old_domain_count_after = media_collection.count_documents({
                "thumb_url": {"$regex": "^https://libfusion.preview.emergentagent.com/uploads/thumbs/"}
            })
            
            # Count documents with new domain after update
            new_domain_count_after = media_collection.count_documents({
                "thumb_url": {"$regex": "^https://claire-marcus.com/uploads/thumbs/"}
            })
            
            # Get sample updated URLs
            sample_updated = list(media_collection.find(
                {"thumb_url": {"$regex": "^https://claire-marcus.com/uploads/thumbs/"}},
                {"thumb_url": 1}
            ).limit(5))
            
            # Verify the update was successful
            update_successful = (
                old_domain_count_after == 0 and 
                new_domain_count_after == (self.new_domain_count_before + self.modified_count)
            )
            
            self.log_result(
                "Update Results Verification", 
                update_successful, 
                f"After update - Old domain URLs: {old_domain_count_after}, New domain URLs: {new_domain_count_after}"
            )
            
            if sample_updated:
                print("   Sample updated URLs:")
                for doc in sample_updated:
                    print(f"     {doc['thumb_url']}")
            
            return update_successful
            
        except Exception as e:
            self.log_result("Update Results Verification", False, error=str(e))
            return False
    
    def test_api_content_pending(self):
        """Step 6: Test GET /api/content/pending to verify thumb_url in API response"""
        print("🌐 STEP 6: API Content Pending Test")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{API_BASE}/content/pending?limit=10")
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                
                # Count items with thumb_url
                items_with_thumbs = [item for item in content if item.get("thumb_url")]
                
                # Check if thumb_url point to new domain
                correct_domain_count = 0
                old_domain_count = 0
                
                sample_urls = []
                
                for item in items_with_thumbs:
                    thumb_url = item.get("thumb_url", "")
                    if thumb_url.startswith("https://claire-marcus.com/uploads/thumbs/"):
                        correct_domain_count += 1
                    elif thumb_url.startswith("https://libfusion.preview.emergentagent.com/uploads/thumbs/"):
                        old_domain_count += 1
                    
                    if len(sample_urls) < 3:
                        sample_urls.append(thumb_url)
                
                success = old_domain_count == 0 and correct_domain_count > 0
                
                self.log_result(
                    "API Content Pending Test", 
                    success, 
                    f"Retrieved {len(content)} items, {len(items_with_thumbs)} with thumbnails. Correct domain: {correct_domain_count}, Old domain: {old_domain_count}"
                )
                
                if sample_urls:
                    print("   Sample thumb_url from API:")
                    for url in sample_urls:
                        print(f"     {url}")
                
                return success
            else:
                self.log_result(
                    "API Content Pending Test", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("API Content Pending Test", False, error=str(e))
            return False
    
    def cleanup(self):
        """Cleanup MongoDB connection"""
        if self.mongo_client:
            self.mongo_client.close()
    
    def run_all_tests(self):
        """Run all thumb URL update tests"""
        print("🚀 THUMB URL UPDATE TESTING (French Review Request)")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_EMAIL}")
        print("Task: Update thumb_url from libfusion.preview.emergentagent.com to claire-marcus.com")
        print("=" * 70)
        print()
        
        try:
            # Run tests in sequence
            tests = [
                self.authenticate,
                self.connect_mongodb,
                self.analyze_current_thumb_urls,
                self.update_thumb_urls_mongodb,
                self.verify_update_results,
                self.test_api_content_pending
            ]
            
            for test in tests:
                if not test():
                    print("❌ Test failed, continuing with remaining tests...")
                print()
            
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
            print("🎯 THUMB URL UPDATE TESTING COMPLETED")
            
            return success_rate >= 80  # Consider successful if 80% or more tests pass
            
        finally:
            self.cleanup()

if __name__ == "__main__":
    tester = ThumbUrlUpdateTester()
    success = tester.run_all_tests()
    
    if success:
        print("✅ Overall testing: SUCCESS")
        exit(0)
    else:
        print("❌ Overall testing: FAILED")
        exit(1)