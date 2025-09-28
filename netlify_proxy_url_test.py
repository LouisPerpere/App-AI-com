#!/usr/bin/env python3
"""
Netlify Proxy URL Update Test - French Review Request
Testing the MongoDB URL updates according to ChatGPT Option B

OBJECTIF: Mettre à jour TOUTES les thumb_url et url en MongoDB
- Remplacer "https://social-publisher-10.preview.emergentagent.com/uploads/" par "https://claire-marcus.com/uploads/"
- Utiliser le proxy Netlify configuré dans _redirects
- Vérifier le nombre d'URLs mises à jour
- Tester GET /api/content/pending pour confirmer les URLs
"""

import requests
import json
import os
import time
from pymongo import MongoClient
from urllib.parse import urlparse

# Configuration
BACKEND_URL = "https://social-publisher-10.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials as specified in review request
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

# MongoDB connection (from backend/.env)
MONGO_URL = "mongodb+srv://lperpere:ClaireMarcus2025@cluster0.24k0jzd.mongodb.net/claire_marcus?retryWrites=true&w=majority&appName=Cluster0"

class NetlifyProxyURLTester:
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
            self.mongo_client = MongoClient(MONGO_URL)
            self.db = self.mongo_client.claire_marcus
            
            # Test connection
            server_info = self.mongo_client.server_info()
            version = server_info.get("version", "unknown")
            
            self.log_result(
                "MongoDB Connection", 
                True, 
                f"Successfully connected to MongoDB (Version: {version})"
            )
            return True
            
        except Exception as e:
            self.log_result("MongoDB Connection", False, error=str(e))
            return False
    
    def analyze_current_urls(self):
        """Step 3: Analyze current URLs in MongoDB"""
        print("🔍 STEP 3: Analyze Current URLs")
        print("=" * 50)
        
        try:
            media_collection = self.db.media
            
            # Count total documents
            total_docs = media_collection.count_documents({})
            
            # Count documents with libfusion URLs
            libfusion_thumb_count = media_collection.count_documents({
                "thumb_url": {"$regex": "libfusion.preview.emergentagent.com"}
            })
            
            libfusion_url_count = media_collection.count_documents({
                "url": {"$regex": "libfusion.preview.emergentagent.com"}
            })
            
            # Count documents with claire-marcus URLs
            claire_marcus_thumb_count = media_collection.count_documents({
                "thumb_url": {"$regex": "claire-marcus.com"}
            })
            
            claire_marcus_url_count = media_collection.count_documents({
                "url": {"$regex": "claire-marcus.com"}
            })
            
            # Count null URLs
            null_thumb_count = media_collection.count_documents({
                "$or": [
                    {"thumb_url": None},
                    {"thumb_url": ""},
                    {"thumb_url": {"$exists": False}}
                ]
            })
            
            null_url_count = media_collection.count_documents({
                "$or": [
                    {"url": None},
                    {"url": ""},
                    {"url": {"$exists": False}}
                ]
            })
            
            details = f"ANALYSE MONGODB: {total_docs} documents totaux. "
            details += f"thumb_url: {libfusion_thumb_count} libfusion, {claire_marcus_thumb_count} claire-marcus, {null_thumb_count} null. "
            details += f"url: {libfusion_url_count} libfusion, {claire_marcus_url_count} claire-marcus, {null_url_count} null."
            
            self.log_result(
                "Analyze Current URLs", 
                True, 
                details
            )
            
            # Store for later comparison
            self.before_update = {
                "total_docs": total_docs,
                "libfusion_thumb_count": libfusion_thumb_count,
                "libfusion_url_count": libfusion_url_count,
                "claire_marcus_thumb_count": claire_marcus_thumb_count,
                "claire_marcus_url_count": claire_marcus_url_count,
                "null_thumb_count": null_thumb_count,
                "null_url_count": null_url_count
            }
            
            return True
            
        except Exception as e:
            self.log_result("Analyze Current URLs", False, error=str(e))
            return False
    
    def update_urls_to_netlify_proxy(self):
        """Step 4: Update URLs to use Netlify proxy (claire-marcus.com)"""
        print("🔄 STEP 4: Update URLs to Netlify Proxy")
        print("=" * 50)
        
        try:
            media_collection = self.db.media
            
            # Update thumb_url from libfusion to claire-marcus
            docs_to_update_thumb = list(media_collection.find({
                "thumb_url": {"$regex": "libfusion.preview.emergentagent.com"}
            }))
            thumb_updated_count = 0
            
            for doc in docs_to_update_thumb:
                old_thumb_url = doc.get("thumb_url", "")
                if old_thumb_url and "libfusion.preview.emergentagent.com" in old_thumb_url:
                    new_thumb_url = old_thumb_url.replace(
                        "https://social-publisher-10.preview.emergentagent.com/uploads/",
                        "https://claire-marcus.com/uploads/"
                    )
                    
                    media_collection.update_one(
                        {"_id": doc["_id"]},
                        {"$set": {"thumb_url": new_thumb_url}}
                    )
                    thumb_updated_count += 1
                    print(f"   Updated thumb_url: {old_thumb_url} → {new_thumb_url}")
            
            # Update url from libfusion to claire-marcus
            docs_to_update_url = list(media_collection.find({
                "url": {"$regex": "libfusion.preview.emergentagent.com"}
            }))
            url_updated_count = 0
            
            for doc in docs_to_update_url:
                old_url = doc.get("url", "")
                if old_url and "libfusion.preview.emergentagent.com" in old_url:
                    new_url = old_url.replace(
                        "https://social-publisher-10.preview.emergentagent.com/uploads/",
                        "https://claire-marcus.com/uploads/"
                    )
                    
                    media_collection.update_one(
                        {"_id": doc["_id"]},
                        {"$set": {"url": new_url}}
                    )
                    url_updated_count += 1
                    if url_updated_count <= 3:  # Show first 3 examples
                        print(f"   Updated url: {old_url} → {new_url}")
            
            details = f"MISE À JOUR URLS NETLIFY PROXY: {thumb_updated_count} thumb_url mises à jour, {url_updated_count} url mises à jour. "
            details += f"Remplacement: libfusion.preview.emergentagent.com → claire-marcus.com"
            
            self.log_result(
                "Update URLs to Netlify Proxy", 
                True, 
                details
            )
            
            # Store update counts
            self.update_counts = {
                "thumb_updated_count": thumb_updated_count,
                "url_updated_count": url_updated_count
            }
            
            return True
            
        except Exception as e:
            self.log_result("Update URLs to Netlify Proxy", False, error=str(e))
            return False
    
    def verify_url_updates(self):
        """Step 5: Verify URL updates in MongoDB"""
        print("✅ STEP 5: Verify URL Updates")
        print("=" * 50)
        
        try:
            media_collection = self.db.media
            
            # Count after update
            total_docs = media_collection.count_documents({})
            
            # Count documents with libfusion URLs (should be 0 now)
            libfusion_thumb_count = media_collection.count_documents({
                "thumb_url": {"$regex": "libfusion.preview.emergentagent.com"}
            })
            
            libfusion_url_count = media_collection.count_documents({
                "url": {"$regex": "libfusion.preview.emergentagent.com"}
            })
            
            # Count documents with claire-marcus URLs (should be increased)
            claire_marcus_thumb_count = media_collection.count_documents({
                "thumb_url": {"$regex": "claire-marcus.com"}
            })
            
            claire_marcus_url_count = media_collection.count_documents({
                "url": {"$regex": "claire-marcus.com"}
            })
            
            # Calculate changes
            if hasattr(self, 'before_update'):
                thumb_change = claire_marcus_thumb_count - self.before_update["claire_marcus_thumb_count"]
                url_change = claire_marcus_url_count - self.before_update["claire_marcus_url_count"]
            else:
                thumb_change = "unknown"
                url_change = "unknown"
            
            details = f"VÉRIFICATION APRÈS MISE À JOUR: {total_docs} documents totaux. "
            details += f"Restant libfusion: {libfusion_thumb_count} thumb_url, {libfusion_url_count} url. "
            details += f"Maintenant claire-marcus: {claire_marcus_thumb_count} thumb_url (+{thumb_change}), {claire_marcus_url_count} url (+{url_change}). "
            details += f"OBJECTIF ATTEINT: {'✅ OUI' if libfusion_thumb_count == 0 and libfusion_url_count == 0 else '❌ NON'}"
            
            success = libfusion_thumb_count == 0 and libfusion_url_count == 0
            
            self.log_result(
                "Verify URL Updates", 
                success, 
                details
            )
            
            return success
            
        except Exception as e:
            self.log_result("Verify URL Updates", False, error=str(e))
            return False
    
    def test_api_content_pending(self):
        """Step 6: Test GET /api/content/pending to confirm URLs"""
        print("🌐 STEP 6: Test API Content Pending")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{API_BASE}/content/pending?limit=10")
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                total = data.get("total", 0)
                
                claire_marcus_thumb_count = 0
                claire_marcus_url_count = 0
                libfusion_thumb_count = 0
                libfusion_url_count = 0
                
                sample_urls = []
                
                for item in content:
                    thumb_url = item.get("thumb_url") or ""
                    url = item.get("url") or ""
                    filename = item.get("filename", "unknown")
                    
                    # Count claire-marcus URLs
                    if "claire-marcus.com" in thumb_url:
                        claire_marcus_thumb_count += 1
                    if "claire-marcus.com" in url:
                        claire_marcus_url_count += 1
                    
                    # Count remaining libfusion URLs
                    if "libfusion.preview.emergentagent.com" in thumb_url:
                        libfusion_thumb_count += 1
                    if "libfusion.preview.emergentagent.com" in url:
                        libfusion_url_count += 1
                    
                    # Collect samples
                    if len(sample_urls) < 3 and thumb_url:
                        domain = "claire-marcus" if "claire-marcus.com" in thumb_url else "libfusion" if "libfusion.preview.emergentagent.com" in thumb_url else "autre"
                        sample_urls.append(f"{filename}: {domain}")
                
                details = f"API CONTENT PENDING: {len(content)} fichiers retournés sur {total} totaux. "
                details += f"thumb_url claire-marcus: {claire_marcus_thumb_count}, libfusion: {libfusion_thumb_count}. "
                details += f"url claire-marcus: {claire_marcus_url_count}, libfusion: {libfusion_url_count}. "
                details += f"Échantillons: {sample_urls}. "
                details += f"PROXY NETLIFY UTILISÉ: {'✅ OUI' if libfusion_thumb_count == 0 and libfusion_url_count == 0 else '❌ NON'}"
                
                success = libfusion_thumb_count == 0 and libfusion_url_count == 0
                
                self.log_result(
                    "Test API Content Pending", 
                    success, 
                    details
                )
                
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
    
    def test_netlify_proxy_accessibility(self):
        """Step 7: Test accessibility of URLs through Netlify proxy"""
        print("🔗 STEP 7: Test Netlify Proxy Accessibility")
        print("=" * 50)
        
        try:
            # Get some content to test
            response = self.session.get(f"{API_BASE}/content/pending?limit=5")
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                
                accessible_count = 0
                inaccessible_count = 0
                tested_urls = []
                
                for item in content:
                    thumb_url = item.get("thumb_url") or ""
                    url = item.get("url") or ""
                    filename = item.get("filename", "unknown")
                    
                    # Test both thumb_url and url if they use claire-marcus.com
                    test_url = thumb_url if thumb_url and "claire-marcus.com" in thumb_url else url if url and "claire-marcus.com" in url else None
                    
                    if test_url:
                        try:
                            # Test accessibility through Netlify proxy
                            proxy_response = requests.get(test_url, timeout=10)
                            
                            if proxy_response.status_code == 200:
                                content_type = proxy_response.headers.get('content-type', '')
                                content_length = len(proxy_response.content)
                                
                                if 'image' in content_type.lower():
                                    accessible_count += 1
                                    url_type = "thumb" if test_url == thumb_url else "url"
                                    tested_urls.append(f"✅ {filename} ({url_type}, {content_length}b)")
                                else:
                                    inaccessible_count += 1
                                    tested_urls.append(f"❌ {filename} (pas image: {content_type})")
                            else:
                                inaccessible_count += 1
                                tested_urls.append(f"❌ {filename} (status: {proxy_response.status_code})")
                                
                        except Exception as url_error:
                            inaccessible_count += 1
                            tested_urls.append(f"❌ {filename} (erreur: {str(url_error)[:30]})")
                        
                        # Limit testing to avoid timeout
                        if len(tested_urls) >= 5:
                            break
                
                total_tested = accessible_count + inaccessible_count
                success_rate = (accessible_count / total_tested * 100) if total_tested > 0 else 0
                
                details = f"TEST PROXY NETLIFY: {total_tested} URLs testées, "
                details += f"{accessible_count} accessibles ({success_rate:.1f}%), "
                details += f"{inaccessible_count} inaccessibles. "
                details += f"Résultats: {tested_urls}. "
                details += f"PROXY FONCTIONNEL: {'✅ OUI' if accessible_count > 0 else '❌ NON'}"
                
                success = accessible_count > 0
                
                self.log_result(
                    "Test Netlify Proxy Accessibility", 
                    success, 
                    details
                )
                
                return success
            else:
                self.log_result(
                    "Test Netlify Proxy Accessibility", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Test Netlify Proxy Accessibility", False, error=str(e))
            return False
    
    def cleanup_mongodb(self):
        """Cleanup MongoDB connection"""
        if self.mongo_client:
            self.mongo_client.close()
    
    def run_all_tests(self):
        """Run all Netlify proxy URL update tests"""
        print("🚀 NETLIFY PROXY URL UPDATE TESTING - DEMANDE FRANÇAISE")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_EMAIL}")
        print(f"OBJECTIF: Remplacer libfusion.preview.emergentagent.com → claire-marcus.com")
        print(f"SOLUTION: ChatGPT Option B - Utiliser le proxy Netlify")
        print("=" * 60)
        print()
        
        try:
            # Run tests in sequence
            tests = [
                self.authenticate,
                self.connect_mongodb,
                self.analyze_current_urls,
                self.update_urls_to_netlify_proxy,
                self.verify_url_updates,
                self.test_api_content_pending,
                self.test_netlify_proxy_accessibility
            ]
            
            for test in tests:
                if not test():
                    print("❌ Test failed, continuing with remaining tests...")
                print()
            
            # Summary
            print("📋 TEST SUMMARY - NETLIFY PROXY URL UPDATE")
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
            
            if hasattr(self, 'before_update') and hasattr(self, 'update_counts'):
                before = self.before_update
                updates = self.update_counts
                print(f"1. AVANT MISE À JOUR:")
                print(f"   • Documents totaux: {before['total_docs']}")
                print(f"   • thumb_url libfusion: {before['libfusion_thumb_count']}")
                print(f"   • url libfusion: {before['libfusion_url_count']}")
                print(f"   • thumb_url claire-marcus: {before['claire_marcus_thumb_count']}")
                print(f"   • url claire-marcus: {before['claire_marcus_url_count']}")
                print()
                print(f"2. MISE À JOUR EFFECTUÉE:")
                print(f"   • thumb_url mises à jour: {updates['thumb_updated_count']}")
                print(f"   • url mises à jour: {updates['url_updated_count']}")
                print()
            
            # Detailed results
            for result in self.test_results:
                print(f"{result['status']}: {result['test']}")
                if result['details']:
                    print(f"   {result['details']}")
                if result['error']:
                    print(f"   Error: {result['error']}")
            
            print()
            print("🎯 NETLIFY PROXY URL UPDATE TESTING COMPLETED")
            
            return success_rate >= 70
            
        finally:
            self.cleanup_mongodb()

if __name__ == "__main__":
    tester = NetlifyProxyURLTester()
    success = tester.run_all_tests()
    
    if success:
        print("✅ Overall testing: SUCCESS")
        exit(0)
    else:
        print("❌ Overall testing: FAILED")
        exit(1)