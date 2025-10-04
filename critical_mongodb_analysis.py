#!/usr/bin/env python3
"""
Critical MongoDB URL Analysis - French Review Request
Direct MongoDB analysis to identify why API returns null URLs

FINDINGS FROM INITIAL TEST:
- MongoDB has 75 documents with valid thumb_url
- API returns 48 files with ALL null thumb_url
- User authentication failing, falling back to demo_user_id
- Need to find the correct user_id for lperpere@yahoo.fr
"""

import requests
import json
import os
import time
from pymongo import MongoClient
from bson import ObjectId

# MongoDB connection from backend/.env
MONGO_URL = "mongodb+srv://lperpere:ClaireMarcus2025@cluster0.24k0jzd.mongodb.net/claire_marcus?retryWrites=true&w=majority&appName=Cluster0"

# Test credentials
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class CriticalMongoDBAnalyzer:
    def __init__(self):
        self.mongo_client = None
        self.db = None
        self.test_results = []
        
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
    
    def connect_mongodb(self):
        """Connect directly to MongoDB"""
        print("🔗 STEP 1: MongoDB Direct Connection")
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
    
    def find_user_id(self):
        """Find the correct user_id for lperpere@yahoo.fr"""
        print("👤 STEP 2: Find User ID for lperpere@yahoo.fr")
        print("=" * 50)
        
        try:
            users_collection = self.db.users
            
            # Find user by email
            user = users_collection.find_one({"email": TEST_EMAIL})
            
            if user:
                self.user_id = user.get("user_id")
                user_details = f"Email: {user.get('email')}, "
                user_details += f"User ID: {self.user_id}, "
                user_details += f"Business Name: {user.get('business_name', 'N/A')}, "
                user_details += f"Created: {user.get('created_at', 'N/A')}"
                
                self.log_result(
                    "Find User ID", 
                    True, 
                    f"User found: {user_details}"
                )
                return True
            else:
                self.log_result(
                    "Find User ID", 
                    False, 
                    f"User not found for email: {TEST_EMAIL}"
                )
                return False
                
        except Exception as e:
            self.log_result("Find User ID", False, error=str(e))
            return False
    
    def analyze_user_documents(self):
        """Analyze documents belonging to the specific user"""
        print("📊 STEP 3: Analyze User Documents in MongoDB")
        print("=" * 50)
        
        if not hasattr(self, 'user_id'):
            self.log_result(
                "Analyze User Documents", 
                False, 
                "No user_id available"
            )
            return False
        
        try:
            media_collection = self.db.media
            
            # Count user documents
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
            
            # Count user documents with valid url
            user_valid_url_count = media_collection.count_documents({
                "owner_id": self.user_id,
                "url": {"$ne": None, "$ne": ""}
            })
            
            # Count user documents with null url
            user_null_url_count = media_collection.count_documents({
                "owner_id": self.user_id,
                "$or": [
                    {"url": None},
                    {"url": ""},
                    {"url": {"$exists": False}}
                ]
            })
            
            details = f"USER DOCUMENTS ANALYSIS (User ID: {self.user_id}): "
            details += f"Total user documents: {user_docs_count}, "
            details += f"Valid thumb_url: {user_valid_thumb_count}, "
            details += f"Null thumb_url: {user_null_thumb_count}, "
            details += f"Valid url: {user_valid_url_count}, "
            details += f"Null url: {user_null_url_count}"
            
            self.log_result(
                "Analyze User Documents", 
                True, 
                details
            )
            
            # Store for later use
            self.user_analysis = {
                "user_docs_count": user_docs_count,
                "user_valid_thumb_count": user_valid_thumb_count,
                "user_null_thumb_count": user_null_thumb_count,
                "user_valid_url_count": user_valid_url_count,
                "user_null_url_count": user_null_url_count
            }
            
            return True
            
        except Exception as e:
            self.log_result("Analyze User Documents", False, error=str(e))
            return False
    
    def search_file_8ee21d73(self):
        """Search for the specific file 8ee21d73"""
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
                    description = doc.get("description", "")
                    
                    details += f"Document {i+1}: filename='{filename}', "
                    details += f"thumb_url={'NULL' if thumb_url is None or thumb_url == '' else f'VALID({thumb_url})'}, "
                    details += f"url={'NULL' if url is None or url == '' else f'VALID({url})'}, "
                    details += f"owner_id='{owner_id}', "
                    details += f"description='{description}', "
                    details += f"mongo_id='{mongo_id}'. "
                
                self.log_result(
                    "Search for file '8ee21d73'", 
                    True, 
                    details
                )
                
                # Store for comparison
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
    
    def analyze_duplicate_documents(self):
        """Check for duplicate documents with same filename but different URLs"""
        print("🔄 STEP 5: Analyze Duplicate Documents")
        print("=" * 50)
        
        if not hasattr(self, 'user_id'):
            self.log_result(
                "Analyze Duplicate Documents", 
                False, 
                "No user_id available"
            )
            return False
        
        try:
            media_collection = self.db.media
            
            # Get all user documents
            user_docs = list(media_collection.find({
                "owner_id": self.user_id
            }))
            
            # Group by filename to find duplicates
            filename_groups = {}
            for doc in user_docs:
                filename = doc.get("filename", "unknown")
                if filename not in filename_groups:
                    filename_groups[filename] = []
                filename_groups[filename].append(doc)
            
            # Find duplicates
            duplicates_found = 0
            duplicate_examples = []
            
            for filename, docs in filename_groups.items():
                if len(docs) > 1:
                    duplicates_found += 1
                    
                    # Analyze the duplicates
                    valid_thumb_docs = [d for d in docs if d.get("thumb_url") not in [None, ""]]
                    null_thumb_docs = [d for d in docs if d.get("thumb_url") in [None, ""]]
                    
                    if len(duplicate_examples) < 3:
                        example = f"Filename '{filename}': {len(docs)} copies "
                        example += f"({len(valid_thumb_docs)} with valid thumb_url, {len(null_thumb_docs)} with null thumb_url)"
                        duplicate_examples.append(example)
            
            details = f"DUPLICATE ANALYSIS: {len(filename_groups)} unique filenames, "
            details += f"{duplicates_found} files with duplicates. "
            if duplicate_examples:
                details += f"Examples: {'; '.join(duplicate_examples)}"
            else:
                details += "No duplicates found"
            
            self.log_result(
                "Analyze Duplicate Documents", 
                True, 
                details
            )
            
            # Store duplicate info
            self.duplicates_info = {
                "total_unique_files": len(filename_groups),
                "duplicates_found": duplicates_found,
                "duplicate_examples": duplicate_examples
            }
            
            return True
            
        except Exception as e:
            self.log_result("Analyze Duplicate Documents", False, error=str(e))
            return False
    
    def test_api_with_correct_auth(self):
        """Test API with correct authentication"""
        print("🌐 STEP 6: Test API with Correct Authentication")
        print("=" * 50)
        
        if not hasattr(self, 'user_id'):
            self.log_result(
                "Test API with Correct Auth", 
                False, 
                "No user_id available"
            )
            return False
        
        try:
            # First, try to authenticate
            session = requests.Session()
            
            auth_response = session.post("https://claire-marcus-app-1.preview.emergentagent.com/api/auth/login", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if auth_response.status_code == 200:
                auth_data = auth_response.json()
                access_token = auth_data.get("access_token")
                
                # Set authorization header
                session.headers.update({
                    "Authorization": f"Bearer {access_token}"
                })
                
                # Test API with authentication
                api_response = session.get("https://claire-marcus-app-1.preview.emergentagent.com/api/content/pending?limit=100")
                
                if api_response.status_code == 200:
                    api_data = api_response.json()
                    content = api_data.get("content", [])
                    
                    # Analyze API response
                    api_null_thumb_count = sum(1 for item in content if item.get("thumb_url") in [None, ""])
                    api_valid_thumb_count = sum(1 for item in content if item.get("thumb_url") not in [None, ""])
                    
                    # Look for file 8ee21d73
                    file_8ee21d73_found = False
                    file_8ee21d73_details = ""
                    
                    for item in content:
                        filename = item.get("filename", "")
                        if "8ee21d73" in filename:
                            file_8ee21d73_found = True
                            thumb_url = item.get("thumb_url")
                            url = item.get("url")
                            file_8ee21d73_details = f"filename='{filename}', "
                            file_8ee21d73_details += f"thumb_url={'NULL' if thumb_url in [None, ''] else f'VALID({thumb_url})'}, "
                            file_8ee21d73_details += f"url={'NULL' if url in [None, ''] else f'VALID({url})'}"
                            break
                    
                    details = f"API WITH AUTH: Total files: {len(content)}, "
                    details += f"Null thumb_url: {api_null_thumb_count}, "
                    details += f"Valid thumb_url: {api_valid_thumb_count}. "
                    
                    if file_8ee21d73_found:
                        details += f"File '8ee21d73' found: {file_8ee21d73_details}"
                    else:
                        details += "File '8ee21d73' NOT found in API response"
                    
                    self.log_result(
                        "Test API with Correct Auth", 
                        True, 
                        details
                    )
                    
                    # Store for final comparison
                    self.api_with_auth = {
                        "total_files": len(content),
                        "api_null_thumb_count": api_null_thumb_count,
                        "api_valid_thumb_count": api_valid_thumb_count,
                        "file_8ee21d73_found": file_8ee21d73_found,
                        "file_8ee21d73_details": file_8ee21d73_details
                    }
                    
                    return True
                else:
                    self.log_result(
                        "Test API with Correct Auth", 
                        False, 
                        f"API call failed: {api_response.status_code}",
                        api_response.text
                    )
                    return False
            else:
                self.log_result(
                    "Test API with Correct Auth", 
                    False, 
                    f"Authentication failed: {auth_response.status_code}",
                    auth_response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Test API with Correct Auth", False, error=str(e))
            return False
    
    def final_diagnosis(self):
        """Provide final diagnosis of the null URL issue"""
        print("🎯 STEP 7: Final Diagnosis")
        print("=" * 50)
        
        try:
            diagnosis = []
            recommendations = []
            
            if hasattr(self, 'user_analysis') and hasattr(self, 'api_with_auth'):
                mongo_data = self.user_analysis
                api_data = self.api_with_auth
                
                # Critical finding 1: MongoDB vs API mismatch
                if mongo_data["user_valid_thumb_count"] > 0 and api_data["api_valid_thumb_count"] == 0:
                    diagnosis.append(f"🚨 CRITICAL: MongoDB has {mongo_data['user_valid_thumb_count']} documents with valid thumb_url but API returns 0")
                    recommendations.append("API is selecting wrong documents - likely duplicate documents with null URLs")
                
                # Critical finding 2: Document count mismatch
                if mongo_data["user_docs_count"] != api_data["total_files"]:
                    diagnosis.append(f"🚨 MISMATCH: MongoDB has {mongo_data['user_docs_count']} user documents but API returns {api_data['total_files']} files")
                    recommendations.append("Check filtering logic and document selection criteria")
                
                # Critical finding 3: File 8ee21d73 specific issue
                if hasattr(self, 'file_8ee21d73_docs') and self.file_8ee21d73_docs:
                    mongo_has_valid = any(doc.get("thumb_url") not in [None, ""] for doc in self.file_8ee21d73_docs)
                    api_has_valid = api_data["file_8ee21d73_found"] and "VALID" in api_data["file_8ee21d73_details"]
                    
                    if mongo_has_valid and not api_has_valid:
                        diagnosis.append("🚨 CRITICAL: File '8ee21d73' has valid thumb_url in MongoDB but API returns null")
                        recommendations.append("API query is selecting duplicate document with null thumb_url instead of valid one")
                
                # Critical finding 4: Duplicate documents
                if hasattr(self, 'duplicates_info') and self.duplicates_info["duplicates_found"] > 0:
                    diagnosis.append(f"🚨 DUPLICATES: {self.duplicates_info['duplicates_found']} files have duplicate documents")
                    recommendations.append("Remove duplicate documents with null URLs, keep only documents with valid URLs")
            
            if not diagnosis:
                diagnosis.append("No critical issues identified in current analysis")
                recommendations.append("Further investigation needed")
            
            details = f"FINAL DIAGNOSIS: {'; '.join(diagnosis)}. "
            details += f"RECOMMENDATIONS: {'; '.join(recommendations)}"
            
            self.log_result(
                "Final Diagnosis", 
                len(diagnosis) > 0, 
                details
            )
            
            return True
            
        except Exception as e:
            self.log_result("Final Diagnosis", False, error=str(e))
            return False
    
    def cleanup(self):
        """Cleanup MongoDB connection"""
        if self.mongo_client:
            self.mongo_client.close()
    
    def run_analysis(self):
        """Run complete MongoDB URL analysis"""
        print("🚀 CRITICAL MONGODB URL ANALYSIS - FRENCH REVIEW REQUEST")
        print("=" * 60)
        print(f"Test User: {TEST_EMAIL}")
        print(f"OBJECTIF: Comprendre pourquoi l'API retourne des documents avec URLs null")
        print("=" * 60)
        print()
        
        try:
            # Run analysis steps
            tests = [
                self.connect_mongodb,
                self.find_user_id,
                self.analyze_user_documents,
                self.search_file_8ee21d73,
                self.analyze_duplicate_documents,
                self.test_api_with_correct_auth,
                self.final_diagnosis
            ]
            
            for test in tests:
                if not test():
                    print("❌ Test failed, continuing with remaining tests...")
                print()
            
            # Summary
            print("📋 ANALYSIS SUMMARY")
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
            print("🎯 CRITICAL MONGODB URL ANALYSIS COMPLETED")
            
            return success_rate >= 70
            
        finally:
            self.cleanup()

if __name__ == "__main__":
    analyzer = CriticalMongoDBAnalyzer()
    success = analyzer.run_analysis()
    
    if success:
        print("✅ Analysis completed successfully")
        exit(0)
    else:
        print("❌ Analysis completed with issues")
        exit(1)