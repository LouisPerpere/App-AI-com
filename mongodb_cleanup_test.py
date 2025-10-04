#!/usr/bin/env python3
"""
MongoDB Duplicate Document Cleanup Test
Testing the French review request: "Nettoyage des documents dupliqués MongoDB pour résoudre les vignettes grises"

SOLUTION SELON DIAGNOSTIC: Supprimer les documents dupliqués avec thumb_url null, garder ceux avec thumb_url valides.

1. Authentifier avec lperpere@yahoo.fr / L@Reunion974!
2. Identifier et supprimer les documents dupliqués :
   - Trouver tous les documents avec le même filename mais thumb_url = null
   - Les supprimer SEULEMENT s'il existe un autre document avec le même filename ET thumb_url valide
   - Conserver UNIQUEMENT les documents avec thumb_url valides
3. Vérification après nettoyage :
   - Compter le nombre de documents supprimés
   - Vérifier qu'il ne reste qu'un seul document par filename
   - Confirmer que tous les documents restants ont thumb_url valides
4. Test final :
   - GET /api/content/pending pour vérifier que l'API retourne maintenant les bons documents
   - Vérifier spécifiquement que le fichier "8ee21d73" retourne le document avec thumb_url valide
"""

import requests
import json
import os
import time
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

# Configuration
BACKEND_URL = "https://claire-marcus-app-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials as specified in review request
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

# MongoDB connection (from backend/.env)
MONGO_URL = "mongodb+srv://lperpere:ClaireMarcus2025@cluster0.24k0jzd.mongodb.net/claire_marcus?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "claire_marcus"

class MongoDBCleanupTester:
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
            self.db = self.mongo_client[DB_NAME]
            
            # Test connection
            self.mongo_client.admin.command('ping')
            
            self.log_result(
                "MongoDB Connection", 
                True, 
                f"Successfully connected to MongoDB database: {DB_NAME}"
            )
            return True
            
        except Exception as e:
            self.log_result("MongoDB Connection", False, error=str(e))
            return False
    
    def analyze_duplicate_documents(self):
        """Step 3: Analyze duplicate documents with same filename"""
        print("🔍 STEP 3: Analyze Duplicate Documents")
        print("=" * 50)
        
        try:
            media_collection = self.db.media
            
            # Get all documents for this user
            user_docs = list(media_collection.find({
                "owner_id": self.user_id,
                "deleted": {"$ne": True}
            }))
            
            total_docs = len(user_docs)
            
            # Group by filename to find duplicates
            filename_groups = {}
            for doc in user_docs:
                filename = doc.get("filename", "")
                if filename:
                    if filename not in filename_groups:
                        filename_groups[filename] = []
                    filename_groups[filename].append(doc)
            
            # Find duplicates
            duplicates = {}
            for filename, docs in filename_groups.items():
                if len(docs) > 1:
                    duplicates[filename] = docs
            
            # Analyze thumb_url patterns in duplicates
            duplicate_analysis = []
            total_duplicates = 0
            docs_with_null_thumb = 0
            docs_with_valid_thumb = 0
            
            for filename, docs in duplicates.items():
                total_duplicates += len(docs)
                
                null_thumb_docs = []
                valid_thumb_docs = []
                
                for doc in docs:
                    thumb_url = doc.get("thumb_url")
                    if thumb_url is None or thumb_url == "":
                        null_thumb_docs.append(doc)
                        docs_with_null_thumb += 1
                    else:
                        valid_thumb_docs.append(doc)
                        docs_with_valid_thumb += 1
                
                duplicate_analysis.append({
                    "filename": filename,
                    "total_docs": len(docs),
                    "null_thumb_count": len(null_thumb_docs),
                    "valid_thumb_count": len(valid_thumb_docs),
                    "null_thumb_docs": null_thumb_docs,
                    "valid_thumb_docs": valid_thumb_docs
                })
            
            # Store analysis for cleanup
            self.duplicate_analysis = duplicate_analysis
            
            details = f"ANALYSE DOCUMENTS DUPLIQUÉS: {total_docs} documents totaux, "
            details += f"{len(duplicates)} fichiers avec doublons, "
            details += f"{total_duplicates} documents dupliqués, "
            details += f"{docs_with_null_thumb} avec thumb_url null, "
            details += f"{docs_with_valid_thumb} avec thumb_url valide. "
            
            # Show examples
            if len(duplicates) > 0:
                example_filename = list(duplicates.keys())[0]
                example_docs = duplicates[example_filename]
                details += f"Exemple: {example_filename} a {len(example_docs)} doublons"
            
            self.log_result(
                "Analyze Duplicate Documents", 
                True, 
                details
            )
            
            return True
            
        except Exception as e:
            self.log_result("Analyze Duplicate Documents", False, error=str(e))
            return False
    
    def cleanup_duplicate_documents(self):
        """Step 4: Clean up duplicate documents - keep only those with valid thumb_url"""
        print("🧹 STEP 4: Cleanup Duplicate Documents")
        print("=" * 50)
        
        if not hasattr(self, 'duplicate_analysis'):
            self.log_result(
                "Cleanup Duplicate Documents", 
                False, 
                "No duplicate analysis available"
            )
            return False
        
        try:
            media_collection = self.db.media
            deleted_count = 0
            cleanup_actions = []
            
            for analysis in self.duplicate_analysis:
                filename = analysis["filename"]
                null_thumb_docs = analysis["null_thumb_docs"]
                valid_thumb_docs = analysis["valid_thumb_docs"]
                
                # Only delete null thumb_url docs if there are valid thumb_url docs for the same filename
                if len(valid_thumb_docs) > 0 and len(null_thumb_docs) > 0:
                    # Delete documents with null thumb_url
                    for doc in null_thumb_docs:
                        result = media_collection.delete_one({"_id": doc["_id"]})
                        if result.deleted_count == 1:
                            deleted_count += 1
                            cleanup_actions.append(f"Deleted {filename} (null thumb_url, ID: {doc['_id']})")
                
                # If there are multiple valid thumb_url docs, keep only one (the first one)
                if len(valid_thumb_docs) > 1:
                    docs_to_delete = valid_thumb_docs[1:]  # Keep first, delete rest
                    for doc in docs_to_delete:
                        result = media_collection.delete_one({"_id": doc["_id"]})
                        if result.deleted_count == 1:
                            deleted_count += 1
                            cleanup_actions.append(f"Deleted duplicate {filename} (valid thumb_url, ID: {doc['_id']})")
            
            details = f"NETTOYAGE TERMINÉ: {deleted_count} documents supprimés. "
            if cleanup_actions:
                details += f"Actions: {cleanup_actions[:3]}"  # Show first 3 actions
                if len(cleanup_actions) > 3:
                    details += f" ... et {len(cleanup_actions) - 3} autres"
            
            self.cleanup_count = deleted_count
            
            self.log_result(
                "Cleanup Duplicate Documents", 
                True, 
                details
            )
            
            return True
            
        except Exception as e:
            self.log_result("Cleanup Duplicate Documents", False, error=str(e))
            return False
    
    def verify_cleanup_results(self):
        """Step 5: Verify cleanup results"""
        print("✅ STEP 5: Verify Cleanup Results")
        print("=" * 50)
        
        try:
            media_collection = self.db.media
            
            # Get all remaining documents for this user
            remaining_docs = list(media_collection.find({
                "owner_id": self.user_id,
                "deleted": {"$ne": True}
            }))
            
            total_remaining = len(remaining_docs)
            
            # Group by filename to check for remaining duplicates
            filename_groups = {}
            for doc in remaining_docs:
                filename = doc.get("filename", "")
                if filename:
                    if filename not in filename_groups:
                        filename_groups[filename] = []
                    filename_groups[filename].append(doc)
            
            # Check for remaining duplicates
            remaining_duplicates = 0
            docs_with_null_thumb = 0
            docs_with_valid_thumb = 0
            
            for filename, docs in filename_groups.items():
                if len(docs) > 1:
                    remaining_duplicates += 1
                
                for doc in docs:
                    thumb_url = doc.get("thumb_url")
                    if thumb_url is None or thumb_url == "":
                        docs_with_null_thumb += 1
                    else:
                        docs_with_valid_thumb += 1
            
            # Success criteria: no remaining duplicates, all docs have valid thumb_url
            cleanup_successful = (remaining_duplicates == 0 and docs_with_null_thumb == 0)
            
            details = f"VÉRIFICATION POST-NETTOYAGE: {total_remaining} documents restants, "
            details += f"{remaining_duplicates} doublons restants, "
            details += f"{docs_with_null_thumb} avec thumb_url null, "
            details += f"{docs_with_valid_thumb} avec thumb_url valide. "
            details += f"Nettoyage {'✅ RÉUSSI' if cleanup_successful else '❌ INCOMPLET'}"
            
            self.log_result(
                "Verify Cleanup Results", 
                cleanup_successful, 
                details
            )
            
            return cleanup_successful
            
        except Exception as e:
            self.log_result("Verify Cleanup Results", False, error=str(e))
            return False
    
    def test_api_content_pending(self):
        """Step 6: Test GET /api/content/pending returns correct documents"""
        print("🔍 STEP 6: Test API Content Pending")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{API_BASE}/content/pending?limit=50")
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                total_api_files = len(content)
                
                # Analyze thumb_url in API response
                api_null_thumb = 0
                api_valid_thumb = 0
                
                for item in content:
                    thumb_url = item.get("thumb_url")
                    if thumb_url is None or thumb_url == "":
                        api_null_thumb += 1
                    else:
                        api_valid_thumb += 1
                
                # Success criteria: API returns only documents with valid thumb_url
                api_cleanup_successful = (api_null_thumb == 0)
                
                details = f"API CONTENT PENDING: {total_api_files} fichiers retournés, "
                details += f"{api_null_thumb} avec thumb_url null, "
                details += f"{api_valid_thumb} avec thumb_url valide. "
                details += f"API {'✅ CORRECTE' if api_cleanup_successful else '❌ RETOURNE ENCORE DES NULL'}"
                
                self.log_result(
                    "Test API Content Pending", 
                    api_cleanup_successful, 
                    details
                )
                
                return api_cleanup_successful
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
    
    def test_specific_file_8ee21d73(self):
        """Step 7: Test specific file "8ee21d73" returns document with valid thumb_url"""
        print("🎯 STEP 7: Test Specific File 8ee21d73")
        print("=" * 50)
        
        try:
            # Get all content and look for file with "8ee21d73" in filename or ID
            response = self.session.get(f"{API_BASE}/content/pending?limit=100")
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                
                # Look for file containing "8ee21d73"
                target_file = None
                for item in content:
                    filename = item.get("filename", "")
                    file_id = item.get("id", "")
                    
                    if "8ee21d73" in filename or "8ee21d73" in file_id:
                        target_file = item
                        break
                
                if target_file:
                    thumb_url = target_file.get("thumb_url")
                    filename = target_file.get("filename", "")
                    file_id = target_file.get("id", "")
                    
                    has_valid_thumb = thumb_url is not None and thumb_url != ""
                    
                    details = f"FICHIER 8ee21d73 TROUVÉ: filename={filename}, id={file_id}, "
                    details += f"thumb_url={'VALIDE' if has_valid_thumb else 'NULL'}"
                    if has_valid_thumb:
                        details += f" ({thumb_url})"
                    
                    self.log_result(
                        "Test Specific File 8ee21d73", 
                        has_valid_thumb, 
                        details
                    )
                    
                    return has_valid_thumb
                else:
                    self.log_result(
                        "Test Specific File 8ee21d73", 
                        False, 
                        "Fichier contenant '8ee21d73' non trouvé dans l'API"
                    )
                    return False
            else:
                self.log_result(
                    "Test Specific File 8ee21d73", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Test Specific File 8ee21d73", False, error=str(e))
            return False
    
    def final_verification(self):
        """Step 8: Final verification of cleanup success"""
        print("🏁 STEP 8: Final Verification")
        print("=" * 50)
        
        try:
            # MongoDB verification
            media_collection = self.db.media
            total_docs = media_collection.count_documents({
                "owner_id": self.user_id,
                "deleted": {"$ne": True}
            })
            
            docs_with_null_thumb = media_collection.count_documents({
                "owner_id": self.user_id,
                "deleted": {"$ne": True},
                "$or": [
                    {"thumb_url": None},
                    {"thumb_url": ""}
                ]
            })
            
            # API verification
            response = self.session.get(f"{API_BASE}/content/pending?limit=100")
            api_total = 0
            api_null_thumb = 0
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                api_total = len(content)
                
                for item in content:
                    thumb_url = item.get("thumb_url")
                    if thumb_url is None or thumb_url == "":
                        api_null_thumb += 1
            
            # Success criteria
            mongodb_clean = (docs_with_null_thumb == 0)
            api_clean = (api_null_thumb == 0)
            overall_success = mongodb_clean and api_clean
            
            details = f"VÉRIFICATION FINALE: MongoDB={total_docs} docs ({docs_with_null_thumb} null thumb_url), "
            details += f"API={api_total} docs ({api_null_thumb} null thumb_url). "
            details += f"MongoDB {'✅ PROPRE' if mongodb_clean else '❌ CONTIENT NULL'}, "
            details += f"API {'✅ PROPRE' if api_clean else '❌ RETOURNE NULL'}. "
            details += f"OBJECTIF {'✅ ATTEINT' if overall_success else '❌ NON ATTEINT'}"
            
            if hasattr(self, 'cleanup_count'):
                details += f". Documents supprimés: {self.cleanup_count}"
            
            self.log_result(
                "Final Verification", 
                overall_success, 
                details
            )
            
            return overall_success
            
        except Exception as e:
            self.log_result("Final Verification", False, error=str(e))
            return False
    
    def cleanup_mongodb_connection(self):
        """Close MongoDB connection"""
        if self.mongo_client:
            self.mongo_client.close()
    
    def run_all_tests(self):
        """Run all MongoDB cleanup tests"""
        print("🚀 MONGODB DUPLICATE DOCUMENT CLEANUP - DEMANDE FRANÇAISE")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_EMAIL}")
        print(f"MongoDB: {DB_NAME}")
        print("OBJECTIF: Supprimer documents dupliqués avec thumb_url null, garder ceux avec thumb_url valides")
        print("=" * 70)
        print()
        
        try:
            # Run tests in sequence
            tests = [
                self.authenticate,
                self.connect_mongodb,
                self.analyze_duplicate_documents,
                self.cleanup_duplicate_documents,
                self.verify_cleanup_results,
                self.test_api_content_pending,
                self.test_specific_file_8ee21d73,
                self.final_verification
            ]
            
            for test in tests:
                if not test():
                    print("❌ Test failed, continuing with remaining tests...")
                print()
            
            # Summary
            print("📋 TEST SUMMARY - NETTOYAGE MONGODB")
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
            print("🎯 MONGODB CLEANUP TESTING COMPLETED")
            
            return success_rate >= 80
            
        finally:
            self.cleanup_mongodb_connection()

if __name__ == "__main__":
    tester = MongoDBCleanupTester()
    success = tester.run_all_tests()
    
    if success:
        print("✅ Overall MongoDB cleanup testing: SUCCESS")
        exit(0)
    else:
        print("❌ Overall MongoDB cleanup testing: FAILED")
        exit(1)