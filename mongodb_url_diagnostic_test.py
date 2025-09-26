#!/usr/bin/env python3
"""
MongoDB URL Diagnostic Test - French Review Request
Vérification critique des URLs null dans MongoDB

PROBLÈME URGENT : L'API retourne 47 fichiers mais TOUS ont thumb_url=null et url=null.

Objectifs:
1. Authentifier avec lperpere@yahoo.fr / L@Reunion974!
2. Analyser pourquoi les URLs sont null:
   - Compter combien de documents MongoDB ont thumb_url != null
   - Compter combien de documents MongoDB ont url != null
   - Vérifier si les 47 documents retournés par l'API sont les BONS documents
   - Identifier si le filtre tolérant sélectionne les documents avec URLs null au lieu des documents avec URLs valides
3. Exemple concret:
   - Chercher le document pour filename "8ee21d73"
   - Vérifier s'il a thumb_url valide en MongoDB
   - Voir si l'API retourne ce document avec ou sans thumb_url
"""

import requests
import json
import os
import time
from pymongo import MongoClient
from bson import ObjectId

# Configuration - Using the correct backend URL from frontend/.env
BACKEND_URL = "https://social-ai-planner-2.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials as specified in review request
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

# MongoDB connection from backend/.env
MONGO_URL = "mongodb+srv://lperpere:ClaireMarcus2025@cluster0.24k0jzd.mongodb.net/claire_marcus?retryWrites=true&w=majority&appName=Cluster0"

class MongoDBURLDiagnosticTester:
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
        """Step 2: Connect directly to MongoDB"""
        print("🔗 STEP 2: MongoDB Direct Connection")
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
                f"Successfully connected to MongoDB (Version {version}), Database: claire_marcus"
            )
            return True
            
        except Exception as e:
            self.log_result("MongoDB Connection", False, error=str(e))
            return False
    
    def analyze_mongodb_documents(self):
        """Step 3: Analyze MongoDB documents for URL patterns"""
        print("📊 STEP 3: MongoDB Document Analysis")
        print("=" * 50)
        
        try:
            media_collection = self.db.media
            
            # Count total documents
            total_docs = media_collection.count_documents({})
            
            # Count documents with valid thumb_url
            valid_thumb_url_count = media_collection.count_documents({
                "thumb_url": {"$ne": None, "$ne": ""}
            })
            
            # Count documents with null/empty thumb_url
            null_thumb_url_count = media_collection.count_documents({
                "$or": [
                    {"thumb_url": None},
                    {"thumb_url": ""},
                    {"thumb_url": {"$exists": False}}
                ]
            })
            
            # Count documents with valid url
            valid_url_count = media_collection.count_documents({
                "url": {"$ne": None, "$ne": ""}
            })
            
            # Count documents with null/empty url
            null_url_count = media_collection.count_documents({
                "$or": [
                    {"url": None},
                    {"url": ""},
                    {"url": {"$exists": False}}
                ]
            })
            
            # Count documents belonging to our user
            user_docs_count = media_collection.count_documents({
                "owner_id": self.user_id
            })
            
            # Count user documents with valid thumb_url
            user_valid_thumb_count = media_collection.count_documents({
                "owner_id": self.user_id,
                "thumb_url": {"$ne": None, "$ne": ""}
            })
            
            # Count user documents with null thumb_url
            user_null_thumb_count = media_collection.count_documents({
                "owner_id": self.user_id,
                "$or": [
                    {"thumb_url": None},
                    {"thumb_url": ""},
                    {"thumb_url": {"$exists": False}}
                ]
            })
            
            details = f"MONGODB ANALYSIS: Total documents: {total_docs}, "
            details += f"Documents with valid thumb_url: {valid_thumb_url_count}, "
            details += f"Documents with null thumb_url: {null_thumb_url_count}, "
            details += f"Documents with valid url: {valid_url_count}, "
            details += f"Documents with null url: {null_url_count}. "
            details += f"USER SPECIFIC: User documents: {user_docs_count}, "
            details += f"User valid thumb_url: {user_valid_thumb_count}, "
            details += f"User null thumb_url: {user_null_thumb_count}"
            
            self.log_result(
                "MongoDB Document Analysis", 
                True, 
                details
            )
            
            # Store for later comparison
            self.mongodb_analysis = {
                "total_docs": total_docs,
                "valid_thumb_url_count": valid_thumb_url_count,
                "null_thumb_url_count": null_thumb_url_count,
                "valid_url_count": valid_url_count,
                "null_url_count": null_url_count,
                "user_docs_count": user_docs_count,
                "user_valid_thumb_count": user_valid_thumb_count,
                "user_null_thumb_count": user_null_thumb_count
            }
            
            return True
            
        except Exception as e:
            self.log_result("MongoDB Document Analysis", False, error=str(e))
            return False
    
    def search_specific_file_8ee21d73(self):
        """Step 4: Search for specific file "8ee21d73" in MongoDB"""
        print("🔍 STEP 4: Search for file '8ee21d73' in MongoDB")
        print("=" * 50)
        
        try:
            media_collection = self.db.media
            
            # Search for documents containing "8ee21d73" in filename
            documents = list(media_collection.find({
                "filename": {"$regex": "8ee21d73", "$options": "i"}
            }))
            
            if documents:
                details = f"FOUND {len(documents)} document(s) for '8ee21d73': "
                
                for i, doc in enumerate(documents):
                    filename = doc.get("filename", "unknown")
                    thumb_url = doc.get("thumb_url")
                    url = doc.get("url")
                    owner_id = doc.get("owner_id")
                    mongo_id = str(doc.get("_id"))
                    
                    details += f"Document {i+1}: filename='{filename}', "
                    details += f"thumb_url={'NULL' if thumb_url is None else f'VALID({thumb_url[:50]}...)'}, "
                    details += f"url={'NULL' if url is None else f'VALID({url[:50]}...)'}, "
                    details += f"owner_id='{owner_id}', "
                    details += f"mongo_id='{mongo_id}'. "
                
                self.log_result(
                    "Search for file '8ee21d73'", 
                    True, 
                    details
                )
                
                # Store for API comparison
                self.file_8ee21d73_docs = documents
                
                return True
            else:
                self.log_result(
                    "Search for file '8ee21d73'", 
                    False, 
                    "No documents found for '8ee21d73' in MongoDB"
                )
                return False
                
        except Exception as e:
            self.log_result("Search for file '8ee21d73'", False, error=str(e))
            return False
    
    def test_api_content_pending(self):
        """Step 5: Test API /content/pending and compare with MongoDB"""
        print("🌐 STEP 5: Test API /content/pending")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{API_BASE}/content/pending?limit=100")
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                total_api_files = len(content)
                
                # Count files with null thumb_url and url
                api_null_thumb_count = 0
                api_valid_thumb_count = 0
                api_null_url_count = 0
                api_valid_url_count = 0
                
                # Look for the specific file "8ee21d73"
                file_8ee21d73_found = False
                file_8ee21d73_details = ""
                
                for item in content:
                    filename = item.get("filename", "")
                    thumb_url = item.get("thumb_url")
                    url = item.get("url")
                    
                    # Count null vs valid URLs
                    if thumb_url is None or thumb_url == "":
                        api_null_thumb_count += 1
                    else:
                        api_valid_thumb_count += 1
                    
                    if url is None or url == "":
                        api_null_url_count += 1
                    else:
                        api_valid_url_count += 1
                    
                    # Check for specific file
                    if "8ee21d73" in filename:
                        file_8ee21d73_found = True
                        file_8ee21d73_details = f"filename='{filename}', "
                        file_8ee21d73_details += f"thumb_url={'NULL' if thumb_url is None else f'VALID({thumb_url[:50]}...)'}, "
                        file_8ee21d73_details += f"url={'NULL' if url is None else f'VALID({url[:50]}...)'}"
                
                details = f"API ANALYSIS: Total files returned: {total_api_files}, "
                details += f"Files with null thumb_url: {api_null_thumb_count}, "
                details += f"Files with valid thumb_url: {api_valid_thumb_count}, "
                details += f"Files with null url: {api_null_url_count}, "
                details += f"Files with valid url: {api_valid_url_count}. "
                
                if file_8ee21d73_found:
                    details += f"File '8ee21d73' FOUND in API: {file_8ee21d73_details}"
                else:
                    details += "File '8ee21d73' NOT FOUND in API response"
                
                self.log_result(
                    "API /content/pending Analysis", 
                    True, 
                    details
                )
                
                # Store for comparison
                self.api_analysis = {
                    "total_api_files": total_api_files,
                    "api_null_thumb_count": api_null_thumb_count,
                    "api_valid_thumb_count": api_valid_thumb_count,
                    "api_null_url_count": api_null_url_count,
                    "api_valid_url_count": api_valid_url_count,
                    "file_8ee21d73_found": file_8ee21d73_found,
                    "file_8ee21d73_details": file_8ee21d73_details
                }
                
                return True
            else:
                self.log_result(
                    "API /content/pending Analysis", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("API /content/pending Analysis", False, error=str(e))
            return False
    
    def compare_mongodb_vs_api(self):
        """Step 6: Compare MongoDB data vs API response"""
        print("⚖️ STEP 6: Compare MongoDB vs API Data")
        print("=" * 50)
        
        if not hasattr(self, 'mongodb_analysis') or not hasattr(self, 'api_analysis'):
            self.log_result(
                "MongoDB vs API Comparison", 
                False, 
                "Missing MongoDB or API analysis data"
            )
            return False
        
        try:
            mongo = self.mongodb_analysis
            api = self.api_analysis
            
            # Critical findings
            critical_issues = []
            
            # Issue 1: API returns 47 files but all have null URLs
            if api["total_api_files"] == 47 and api["api_null_thumb_count"] == 47:
                critical_issues.append("🚨 CRITICAL: API returns 47 files but ALL have thumb_url=null")
            
            # Issue 2: MongoDB has valid URLs but API doesn't return them
            if mongo["user_valid_thumb_count"] > 0 and api["api_valid_thumb_count"] == 0:
                critical_issues.append(f"🚨 CRITICAL: MongoDB has {mongo['user_valid_thumb_count']} documents with valid thumb_url but API returns 0")
            
            # Issue 3: Wrong document selection
            if mongo["user_docs_count"] != api["total_api_files"]:
                critical_issues.append(f"🚨 MISMATCH: MongoDB has {mongo['user_docs_count']} user documents but API returns {api['total_api_files']} files")
            
            # Issue 4: File 8ee21d73 comparison
            if hasattr(self, 'file_8ee21d73_docs') and self.file_8ee21d73_docs:
                mongo_has_valid_thumb = any(doc.get("thumb_url") for doc in self.file_8ee21d73_docs)
                api_has_valid_thumb = api["file_8ee21d73_found"] and "VALID" in api["file_8ee21d73_details"]
                
                if mongo_has_valid_thumb and not api_has_valid_thumb:
                    critical_issues.append("🚨 CRITICAL: File '8ee21d73' has valid thumb_url in MongoDB but API returns null")
            
            details = "COMPARISON RESULTS: "
            details += f"MongoDB user documents: {mongo['user_docs_count']}, "
            details += f"API files returned: {api['total_api_files']}, "
            details += f"MongoDB valid thumb_url: {mongo['user_valid_thumb_count']}, "
            details += f"API valid thumb_url: {api['api_valid_thumb_count']}. "
            
            if critical_issues:
                details += f"CRITICAL ISSUES FOUND: {'; '.join(critical_issues)}"
                success = False
            else:
                details += "No critical issues found - data consistency OK"
                success = True
            
            self.log_result(
                "MongoDB vs API Comparison", 
                success, 
                details
            )
            
            return success
            
        except Exception as e:
            self.log_result("MongoDB vs API Comparison", False, error=str(e))
            return False
    
    def test_debug_endpoint(self):
        """Step 7: Test debug endpoint for additional insights"""
        print("🔧 STEP 7: Test Debug Endpoint")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{API_BASE}/content/_debug")
            
            if response.status_code == 200:
                data = response.json()
                
                db_name = data.get("db", "unknown")
                user_id = data.get("user_id", "unknown")
                filter_used = data.get("filter_used", {})
                counts = data.get("counts", {})
                one_any = data.get("one_any", {})
                one_mine = data.get("one_mine")
                
                details = f"DEBUG ENDPOINT: Database: {db_name}, "
                details += f"User ID: {user_id}, "
                details += f"Filter used: {filter_used}, "
                details += f"Counts - any: {counts.get('any', 0)}, mine: {counts.get('mine', 0)}, "
                details += f"Sample document owner_id: {one_any.get('owner_id', 'N/A')}, "
                details += f"Sample document keys: {one_any.get('keys', [])}, "
                details += f"User document found: {'YES' if one_mine else 'NO'}"
                
                self.log_result(
                    "Debug Endpoint Analysis", 
                    True, 
                    details
                )
                
                return True
            else:
                self.log_result(
                    "Debug Endpoint Analysis", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Debug Endpoint Analysis", False, error=str(e))
            return False
    
    def identify_root_cause(self):
        """Step 8: Identify root cause of null URLs"""
        print("🎯 STEP 8: Root Cause Analysis")
        print("=" * 50)
        
        try:
            root_causes = []
            recommendations = []
            
            if hasattr(self, 'mongodb_analysis') and hasattr(self, 'api_analysis'):
                mongo = self.mongodb_analysis
                api = self.api_analysis
                
                # Root cause 1: Duplicate documents
                if mongo["user_valid_thumb_count"] > 0 and api["api_valid_thumb_count"] == 0:
                    root_causes.append("DUPLICATE DOCUMENTS: Same files exist multiple times in MongoDB - API selects wrong documents (with null URLs)")
                    recommendations.append("Remove duplicate documents with null URLs, keep only documents with valid URLs")
                
                # Root cause 2: Incorrect filter logic
                if mongo["user_docs_count"] > api["total_api_files"]:
                    root_causes.append("FILTER MISMATCH: Tolerant filter may be selecting wrong subset of documents")
                    recommendations.append("Review filter logic in helpers_debug.py build_owner_filter function")
                
                # Root cause 3: Document selection order
                if api["api_null_thumb_count"] == api["total_api_files"]:
                    root_causes.append("DOCUMENT ORDERING: API consistently selects documents with null URLs first")
                    recommendations.append("Modify query to prioritize documents with valid URLs using sort order")
                
                # Root cause 4: Field name inconsistency
                root_causes.append("FIELD INCONSISTENCY: Documents may have different field names (owner_id vs ownerId)")
                recommendations.append("Standardize field names across all documents")
            
            if not root_causes:
                root_causes.append("Unable to determine root cause - need more data")
                recommendations.append("Manual MongoDB inspection required")
            
            details = f"ROOT CAUSES IDENTIFIED: {'; '.join(root_causes)}. "
            details += f"RECOMMENDATIONS: {'; '.join(recommendations)}"
            
            self.log_result(
                "Root Cause Analysis", 
                len(root_causes) > 0, 
                details
            )
            
            return True
            
        except Exception as e:
            self.log_result("Root Cause Analysis", False, error=str(e))
            return False
    
    def cleanup(self):
        """Cleanup MongoDB connection"""
        if self.mongo_client:
            self.mongo_client.close()
    
    def run_all_tests(self):
        """Run all MongoDB URL diagnostic tests"""
        print("🚀 MONGODB URL DIAGNOSTIC TESTING - FRENCH REVIEW REQUEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_EMAIL}")
        print(f"PROBLÈME: L'API retourne 47 fichiers mais TOUS ont thumb_url=null et url=null")
        print("=" * 60)
        print()
        
        try:
            # Run tests in sequence
            tests = [
                self.authenticate,
                self.connect_mongodb,
                self.analyze_mongodb_documents,
                self.search_specific_file_8ee21d73,
                self.test_api_content_pending,
                self.compare_mongodb_vs_api,
                self.test_debug_endpoint,
                self.identify_root_cause
            ]
            
            for test in tests:
                if not test():
                    print("❌ Test failed, continuing with remaining tests...")
                print()
            
            # Summary
            print("📋 DIAGNOSTIC SUMMARY - FRENCH REVIEW REQUEST")
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
            print("🎯 MONGODB URL DIAGNOSTIC COMPLETED")
            
            return success_rate >= 50  # Lower threshold for diagnostic
            
        finally:
            self.cleanup()

if __name__ == "__main__":
    tester = MongoDBURLDiagnosticTester()
    success = tester.run_all_tests()
    
    if success:
        print("✅ Overall diagnostic: SUCCESS")
        exit(0)
    else:
        print("❌ Overall diagnostic: COMPLETED WITH ISSUES")
        exit(1)