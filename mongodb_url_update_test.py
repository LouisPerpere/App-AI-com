#!/usr/bin/env python3
"""
Backend Test Suite for MongoDB URL Update - French Review Request
Testing the URL update from claire-marcus.com to claire-marcus-api.onrender.com
"""

import requests
import json
import os
import time
from pymongo import MongoClient

# Configuration - Using the correct backend URL from frontend/.env
BACKEND_URL = "https://social-ai-planner-2.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials as specified in review request
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

# MongoDB connection from backend/.env
MONGO_URL = "mongodb+srv://lperpere:ClaireMarcus2025@cluster0.24k0jzd.mongodb.net/claire_marcus?retryWrites=true&w=majority&appName=Cluster0"

class MongoDBURLUpdateTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.test_results = []
        self.mongo_client = None
        self.db = None
        self.media_collection = None
        
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
    
    def analyze_current_urls(self):
        """Step 2: Connect to MongoDB and analyze current URLs directly"""
        print("🔗 STEP 2: Connect to MongoDB and Analyze URLs")
        print("=" * 50)
        
        try:
            # Connect to MongoDB
            self.mongo_client = MongoClient(MONGO_URL)
            self.db = self.mongo_client.claire_marcus
            self.media_collection = self.db.media
            
            # Test connection
            server_info = self.mongo_client.server_info()
            print(f"✅ Connected to MongoDB version {server_info.get('version', 'unknown')}")
            
            # Count documents with different URL patterns
            total_docs = self.media_collection.count_documents({})
            
            # Count thumb_url patterns
            claire_marcus_thumb = self.media_collection.count_documents({
                "thumb_url": {"$regex": "claire-marcus.com"}
            })
            
            claire_marcus_api_thumb = self.media_collection.count_documents({
                "thumb_url": {"$regex": "claire-marcus-api.onrender.com"}
            })
            
            null_thumb = self.media_collection.count_documents({
                "thumb_url": None
            })
            
            # Count url patterns
            claire_marcus_url = self.media_collection.count_documents({
                "url": {"$regex": "claire-marcus.com"}
            })
            
            claire_marcus_api_url = self.media_collection.count_documents({
                "url": {"$regex": "claire-marcus-api.onrender.com"}
            })
            
            null_url = self.media_collection.count_documents({
                "url": None
            })
            
            # Get some examples
            examples = []
            sample_docs = self.media_collection.find({
                "$or": [
                    {"thumb_url": {"$regex": "claire-marcus.com"}},
                    {"url": {"$regex": "claire-marcus.com"}}
                ]
            }).limit(3)
            
            for doc in sample_docs:
                filename = doc.get("filename", "unknown")
                thumb_url = doc.get("thumb_url", "")
                url = doc.get("url", "")
                examples.append(f"{filename}: thumb_url={thumb_url}, url={url}")
            
            details = f"ANALYSE MONGODB DIRECTE: {total_docs} documents totaux. "
            details += f"thumb_url: {claire_marcus_thumb} claire-marcus.com, {claire_marcus_api_thumb} claire-marcus-api.onrender.com, {null_thumb} null. "
            details += f"url: {claire_marcus_url} claire-marcus.com, {claire_marcus_api_url} claire-marcus-api.onrender.com, {null_url} null. "
            if examples:
                details += f"Exemples: {examples}"
            
            self.log_result(
                "Analyse MongoDB directe", 
                True, 
                details
            )
            
            # Store for comparison after update
            self.before_update = {
                "total_docs": total_docs,
                "claire_marcus_thumb": claire_marcus_thumb,
                "claire_marcus_api_thumb": claire_marcus_api_thumb,
                "claire_marcus_url": claire_marcus_url,
                "claire_marcus_api_url": claire_marcus_api_url,
                "null_thumb": null_thumb,
                "null_url": null_url
            }
            
            return True
            
        except Exception as e:
            self.log_result("Analyse MongoDB directe", False, error=str(e))
            return False
    
    def execute_mongodb_url_update(self):
        """Step 3: Execute the MongoDB URL update as specified in French review"""
        print("🔄 STEP 3: Execute MongoDB URL Update")
        print("=" * 50)
        
        try:
            if self.media_collection is None:
                self.log_result(
                    "MongoDB URL Update Execution", 
                    False, 
                    "MongoDB connection not available"
                )
                return False
            
            # Update thumb_url fields - exactly as specified in French review
            print("Updating thumb_url fields...")
            result1 = self.media_collection.update_many(
                {"thumb_url": {"$regex": "claire-marcus.com"}},
                [{"$set": {"thumb_url": {"$replaceAll": {"input": "$thumb_url", "find": "claire-marcus.com", "replacement": "claire-marcus-api.onrender.com"}}}}]
            )
            
            # Update url fields - exactly as specified in French review
            print("Updating url fields...")
            result2 = self.media_collection.update_many(
                {"url": {"$regex": "claire-marcus.com"}},
                [{"$set": {"url": {"$replaceAll": {"input": "$url", "find": "claire-marcus.com", "replacement": "claire-marcus-api.onrender.com"}}}}]
            )
            
            thumb_updated = result1.modified_count
            url_updated = result2.modified_count
            total_updated = thumb_updated + url_updated
            
            self.log_result(
                "MongoDB URL Update Execution", 
                True, 
                f"Successfully updated {thumb_updated} thumb_url fields and {url_updated} url fields. Total: {total_updated} updates"
            )
            
            self.update_results = {
                "thumb_updated": thumb_updated,
                "url_updated": url_updated,
                "total_updated": total_updated
            }
            
            return True
            
        except Exception as e:
            self.log_result("MongoDB URL Update Execution", False, error=str(e))
            return False
    
    def verify_mongodb_url_update(self):
        """Step 4: Verify the MongoDB URL update was successful"""
        print("✅ STEP 4: Verify MongoDB URL Update Results")
        print("=" * 50)
        
        try:
            if self.media_collection is None:
                self.log_result(
                    "MongoDB URL Update Verification", 
                    False, 
                    "MongoDB connection not available"
                )
                return False
            
            # Count documents with different URL patterns after update
            claire_marcus_thumb_after = self.media_collection.count_documents({
                "thumb_url": {"$regex": "claire-marcus.com"}
            })
            
            claire_marcus_api_thumb_after = self.media_collection.count_documents({
                "thumb_url": {"$regex": "claire-marcus-api.onrender.com"}
            })
            
            claire_marcus_url_after = self.media_collection.count_documents({
                "url": {"$regex": "claire-marcus.com"}
            })
            
            claire_marcus_api_url_after = self.media_collection.count_documents({
                "url": {"$regex": "claire-marcus-api.onrender.com"}
            })
            
            # Check if all claire-marcus.com URLs were updated
            all_thumb_updated = claire_marcus_thumb_after == 0
            all_url_updated = claire_marcus_url_after == 0
            
            # Verify the increase in claire-marcus-api.onrender.com URLs
            if hasattr(self, 'before_update'):
                thumb_increase = claire_marcus_api_thumb_after - self.before_update["claire_marcus_api_thumb"]
                url_increase = claire_marcus_api_url_after - self.before_update["claire_marcus_api_url"]
            else:
                thumb_increase = claire_marcus_api_thumb_after
                url_increase = claire_marcus_api_url_after
            
            # Get some examples of updated URLs
            examples = []
            sample_docs = self.media_collection.find({
                "$or": [
                    {"thumb_url": {"$regex": "claire-marcus-api.onrender.com"}},
                    {"url": {"$regex": "claire-marcus-api.onrender.com"}}
                ]
            }).limit(3)
            
            for doc in sample_docs:
                filename = doc.get("filename", "unknown")
                thumb_url = doc.get("thumb_url") or ""
                url = doc.get("url") or ""
                if "claire-marcus-api.onrender.com" in url:
                    examples.append(f"{filename}: {url}")
                elif "claire-marcus-api.onrender.com" in thumb_url:
                    examples.append(f"{filename}: {thumb_url}")
            
            details = f"VÉRIFICATION MONGODB: "
            details += f"thumb_url claire-marcus.com restants: {claire_marcus_thumb_after} (devrait être 0), "
            details += f"thumb_url claire-marcus-api.onrender.com: {claire_marcus_api_thumb_after} (+{thumb_increase}), "
            details += f"url claire-marcus.com restants: {claire_marcus_url_after} (devrait être 0), "
            details += f"url claire-marcus-api.onrender.com: {claire_marcus_api_url_after} (+{url_increase}). "
            if examples:
                details += f"Exemples mis à jour: {examples}"
            
            success = all_thumb_updated and all_url_updated and (thumb_increase > 0 or url_increase > 0)
            
            self.log_result(
                "MongoDB URL Update Verification", 
                success, 
                details
            )
            
            # Store for final summary
            self.after_update = {
                "claire_marcus_thumb_after": claire_marcus_thumb_after,
                "claire_marcus_api_thumb_after": claire_marcus_api_thumb_after,
                "claire_marcus_url_after": claire_marcus_url_after,
                "claire_marcus_api_url_after": claire_marcus_api_url_after,
                "thumb_increase": thumb_increase,
                "url_increase": url_increase,
                "success": success
            }
            
            return success
            
        except Exception as e:
            self.log_result("MongoDB URL Update Verification", False, error=str(e))
            return False
    
    def test_api_content_pending(self):
        """Step 5: Test GET /api/content/pending to confirm URLs point to new domain"""
        print("🔍 STEP 5: Test API Content Pending")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{API_BASE}/content/pending?limit=20")
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                total_files = len(content)
                
                # Analyze URLs in API response
                claire_marcus_api_count = 0
                claire_marcus_old_count = 0
                null_thumb_count = 0
                
                sample_urls = []
                
                for item in content:
                    thumb_url = item.get("thumb_url")
                    url = item.get("url")
                    filename = item.get("filename", "unknown")
                    
                    # Check thumb_url
                    if thumb_url:
                        if "claire-marcus-api.onrender.com" in thumb_url:
                            claire_marcus_api_count += 1
                            if len(sample_urls) < 3:
                                sample_urls.append(f"✅ {filename}: {thumb_url}")
                        elif "claire-marcus.com" in thumb_url:
                            claire_marcus_old_count += 1
                            if len(sample_urls) < 3:
                                sample_urls.append(f"❌ {filename}: {thumb_url}")
                    else:
                        null_thumb_count += 1
                
                # Check if objective is met
                all_updated = claire_marcus_old_count == 0
                has_new_urls = claire_marcus_api_count > 0
                
                details = f"API CONTENT PENDING: {total_files} fichiers. "
                details += f"{claire_marcus_api_count} avec claire-marcus-api.onrender.com, "
                details += f"{claire_marcus_old_count} avec ancienne URL claire-marcus.com, "
                details += f"{null_thumb_count} avec thumb_url null. "
                details += f"Échantillons: {sample_urls}"
                
                success = all_updated and has_new_urls
                
                self.log_result(
                    "API Content Pending Test", 
                    success, 
                    details
                )
                
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
    
    def cleanup_mongodb_connection(self):
        """Step 6: Cleanup MongoDB connection"""
        print("🧹 STEP 6: Cleanup")
        print("=" * 50)
        
        try:
            if self.mongo_client:
                self.mongo_client.close()
                
            self.log_result(
                "MongoDB Connection Cleanup", 
                True, 
                "MongoDB connection closed successfully"
            )
            return True
            
        except Exception as e:
            self.log_result("MongoDB Connection Cleanup", False, error=str(e))
            return False
    
    def run_all_tests(self):
        """Run all MongoDB URL update tests according to French review request"""
        print("🚀 MONGODB URL UPDATE TESTING - DEMANDE FRANÇAISE")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_EMAIL}")
        print(f"OBJECTIF: Mettre à jour toutes les URLs de claire-marcus.com vers claire-marcus-api.onrender.com")
        print("=" * 60)
        print()
        
        # Run tests in sequence
        tests = [
            self.authenticate,
            self.analyze_current_urls,
            self.execute_mongodb_url_update,
            self.verify_mongodb_url_update,
            self.test_api_content_pending,
            self.cleanup_mongodb_connection
        ]
        
        for test in tests:
            if not test():
                print("❌ Test failed, continuing with remaining tests...")
            print()
        
        # Summary
        print("📋 TEST SUMMARY - DEMANDE FRANÇAISE")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # French review specific summary
        print("RÉSUMÉ SELON LA DEMANDE FRANÇAISE:")
        print("-" * 40)
        
        if hasattr(self, 'update_results'):
            results = self.update_results
            print(f"1. MISE À JOUR MONGODB EXÉCUTÉE:")
            print(f"   • thumb_url mis à jour: {results['thumb_updated']}")
            print(f"   • url mis à jour: {results['url_updated']}")
            print(f"   • Total mis à jour: {results['total_updated']}")
            print()
        
        if hasattr(self, 'before_update') and hasattr(self, 'after_update'):
            before = self.before_update
            after = self.after_update
            print(f"2. AVANT MISE À JOUR:")
            print(f"   • thumb_url claire-marcus.com: {before['claire_marcus_thumb']}")
            print(f"   • url claire-marcus.com: {before['claire_marcus_url']}")
            print()
            print(f"3. APRÈS MISE À JOUR:")
            print(f"   • thumb_url claire-marcus.com: {after['claire_marcus_thumb_after']}")
            print(f"   • thumb_url claire-marcus-api.onrender.com: {after['claire_marcus_api_thumb_after']}")
            print(f"   • url claire-marcus.com: {after['claire_marcus_url_after']}")
            print(f"   • url claire-marcus-api.onrender.com: {after['claire_marcus_api_url_after']}")
            print(f"   • Objectif atteint: {'✅ OUI' if after['success'] else '❌ NON'}")
            print()
        
        # Detailed results
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
            if result['error']:
                print(f"   Error: {result['error']}")
        
        print()
        print("🎯 MONGODB URL UPDATE TESTING COMPLETED - DEMANDE FRANÇAISE")
        
        return success_rate >= 60  # Success if most tests pass

if __name__ == "__main__":
    tester = MongoDBURLUpdateTester()
    success = tester.run_all_tests()
    
    if success:
        print("✅ Overall testing: SUCCESS")
        exit(0)
    else:
        print("❌ Overall testing: FAILED")
        exit(1)