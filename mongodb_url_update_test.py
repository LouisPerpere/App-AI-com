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
BACKEND_URL = "https://5f4ed9f9-c147-4a28-b85c-5a25b4d4a7d1.preview.emergentagent.com"
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
        """Step 2: Analyze current URLs in MongoDB before update"""
        print("🔍 STEP 2: Analyze Current URLs in MongoDB")
        print("=" * 50)
        
        try:
            # Get all content files to analyze URLs
            response = self.session.get(f"{API_BASE}/content/pending?limit=100")
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                total_files = len(content)
                
                # Analyze URL patterns
                claire_marcus_com_urls = 0
                claire_marcus_api_urls = 0
                libfusion_urls = 0
                null_urls = 0
                other_urls = 0
                
                claire_marcus_com_examples = []
                claire_marcus_api_examples = []
                
                for item in content:
                    thumb_url = item.get("thumb_url")
                    url = item.get("url")
                    filename = item.get("filename", "unknown")
                    
                    # Check thumb_url
                    if thumb_url is None or thumb_url == "":
                        null_urls += 1
                    elif "claire-marcus.com/uploads/" in thumb_url:
                        claire_marcus_com_urls += 1
                        if len(claire_marcus_com_examples) < 3:
                            claire_marcus_com_examples.append(f"{filename}: {thumb_url}")
                    elif "claire-marcus-api.onrender.com/uploads/" in thumb_url:
                        claire_marcus_api_urls += 1
                        if len(claire_marcus_api_examples) < 3:
                            claire_marcus_api_examples.append(f"{filename}: {thumb_url}")
                    elif "libfusion.preview.emergentagent.com" in thumb_url:
                        libfusion_urls += 1
                    else:
                        other_urls += 1
                
                # Report current state
                details = f"ANALYSE ACTUELLE DES {total_files} FICHIERS: "
                details += f"URLs claire-marcus.com: {claire_marcus_com_urls}, "
                details += f"URLs claire-marcus-api.onrender.com: {claire_marcus_api_urls}, "
                details += f"URLs libfusion: {libfusion_urls}, "
                details += f"URLs null: {null_urls}, "
                details += f"Autres: {other_urls}. "
                
                if claire_marcus_com_examples:
                    details += f"Exemples claire-marcus.com: {claire_marcus_com_examples}. "
                if claire_marcus_api_examples:
                    details += f"Exemples claire-marcus-api.onrender.com: {claire_marcus_api_examples}. "
                
                self.log_result(
                    "Analyse URLs actuelles", 
                    True, 
                    details
                )
                
                # Store for comparison after update
                self.before_update = {
                    "total_files": total_files,
                    "claire_marcus_com_urls": claire_marcus_com_urls,
                    "claire_marcus_api_urls": claire_marcus_api_urls,
                    "libfusion_urls": libfusion_urls,
                    "null_urls": null_urls,
                    "other_urls": other_urls
                }
                
                return True
            else:
                self.log_result(
                    "Analyse URLs actuelles", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Analyse URLs actuelles", False, error=str(e))
            return False
    
    def test_url_update_endpoint(self):
        """Step 3: Test if there's an endpoint to update URLs"""
        print("🔄 STEP 3: Test URL Update Functionality")
        print("=" * 50)
        
        try:
            # Check if there's a specific endpoint for URL updates
            # This might be a custom endpoint or we might need to use existing ones
            
            # First, let's check if there's a bulk update endpoint
            response = self.session.post(f"{API_BASE}/content/urls/update", json={
                "from_domain": "https://claire-marcus.com/uploads/",
                "to_domain": "https://claire-marcus-api.onrender.com/uploads/"
            })
            
            if response.status_code == 200:
                data = response.json()
                updated_count = data.get("updated_count", 0)
                
                self.log_result(
                    "URL Update Endpoint", 
                    True, 
                    f"Successfully updated {updated_count} URLs from claire-marcus.com to claire-marcus-api.onrender.com"
                )
                return True
            elif response.status_code == 404:
                # Endpoint doesn't exist, we'll need to check if the update was done manually
                self.log_result(
                    "URL Update Endpoint", 
                    False, 
                    "URL update endpoint not found - checking if update was done manually",
                    "Endpoint /api/content/urls/update not available"
                )
                return False
            else:
                self.log_result(
                    "URL Update Endpoint", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("URL Update Endpoint", False, error=str(e))
            return False
    
    def verify_url_update_results(self):
        """Step 4: Verify URLs have been updated to claire-marcus-api.onrender.com"""
        print("✅ STEP 4: Verify URL Update Results")
        print("=" * 50)
        
        try:
            # Get all content files to verify URLs after update
            response = self.session.get(f"{API_BASE}/content/pending?limit=100")
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                total_files = len(content)
                
                # Analyze URL patterns after update
                claire_marcus_com_urls = 0
                claire_marcus_api_urls = 0
                libfusion_urls = 0
                null_urls = 0
                other_urls = 0
                
                claire_marcus_api_examples = []
                remaining_com_examples = []
                
                for item in content:
                    thumb_url = item.get("thumb_url")
                    filename = item.get("filename", "unknown")
                    
                    if thumb_url is None or thumb_url == "":
                        null_urls += 1
                    elif "claire-marcus.com/uploads/" in thumb_url:
                        claire_marcus_com_urls += 1
                        if len(remaining_com_examples) < 3:
                            remaining_com_examples.append(f"{filename}: {thumb_url}")
                    elif "claire-marcus-api.onrender.com/uploads/" in thumb_url:
                        claire_marcus_api_urls += 1
                        if len(claire_marcus_api_examples) < 3:
                            claire_marcus_api_examples.append(f"{filename}: {thumb_url}")
                    elif "libfusion.preview.emergentagent.com" in thumb_url:
                        libfusion_urls += 1
                    else:
                        other_urls += 1
                
                # Calculate update success
                update_successful = claire_marcus_api_urls > 0 and claire_marcus_com_urls == 0
                
                # Compare with before state if available
                if hasattr(self, 'before_update'):
                    before = self.before_update
                    urls_converted = before['claire_marcus_com_urls'] - claire_marcus_com_urls
                    details = f"RÉSULTATS MISE À JOUR: {total_files} fichiers analysés. "
                    details += f"AVANT: {before['claire_marcus_com_urls']} URLs claire-marcus.com. "
                    details += f"APRÈS: {claire_marcus_com_urls} URLs claire-marcus.com restantes, "
                    details += f"{claire_marcus_api_urls} URLs claire-marcus-api.onrender.com. "
                    details += f"URLs converties: {urls_converted}. "
                else:
                    details = f"RÉSULTATS MISE À JOUR: {total_files} fichiers analysés. "
                    details += f"URLs claire-marcus-api.onrender.com: {claire_marcus_api_urls}, "
                    details += f"URLs claire-marcus.com restantes: {claire_marcus_com_urls}. "
                
                if claire_marcus_api_examples:
                    details += f"Exemples API: {claire_marcus_api_examples}. "
                if remaining_com_examples:
                    details += f"URLs .com restantes: {remaining_com_examples}. "
                
                details += f"OBJECTIF ATTEINT: {'✅ OUI' if update_successful else '❌ NON'}"
                
                self.log_result(
                    "Vérification mise à jour URLs", 
                    update_successful, 
                    details
                )
                
                # Store results for final summary
                self.after_update = {
                    "total_files": total_files,
                    "claire_marcus_com_urls": claire_marcus_com_urls,
                    "claire_marcus_api_urls": claire_marcus_api_urls,
                    "update_successful": update_successful
                }
                
                return update_successful
            else:
                self.log_result(
                    "Vérification mise à jour URLs", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Vérification mise à jour URLs", False, error=str(e))
            return False
    
    def test_api_accessibility(self):
        """Step 5: Test that claire-marcus-api.onrender.com URLs are accessible"""
        print("🌐 STEP 5: Test API URL Accessibility")
        print("=" * 50)
        
        try:
            # Get sample files with claire-marcus-api URLs
            response = self.session.get(f"{API_BASE}/content/pending?limit=10")
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                
                accessible_count = 0
                inaccessible_count = 0
                webp_content_type_count = 0
                
                tested_samples = []
                
                for item in content:
                    thumb_url = item.get("thumb_url")
                    filename = item.get("filename", "unknown")
                    
                    if thumb_url and "claire-marcus-api.onrender.com/uploads/" in thumb_url:
                        try:
                            # Test accessibility
                            thumb_response = requests.get(thumb_url, timeout=10)
                            
                            if thumb_response.status_code == 200:
                                content_type = thumb_response.headers.get('content-type', '')
                                content_length = len(thumb_response.content)
                                
                                if 'image/webp' in content_type.lower():
                                    accessible_count += 1
                                    webp_content_type_count += 1
                                    
                                    if len(tested_samples) < 3:
                                        tested_samples.append(f"✅ {filename} (WEBP, {content_length}b)")
                                elif 'image' in content_type.lower():
                                    accessible_count += 1
                                    
                                    if len(tested_samples) < 3:
                                        tested_samples.append(f"✅ {filename} ({content_type}, {content_length}b)")
                                else:
                                    inaccessible_count += 1
                                    if len(tested_samples) < 3:
                                        tested_samples.append(f"❌ {filename} (pas image: {content_type})")
                            else:
                                inaccessible_count += 1
                                if len(tested_samples) < 3:
                                    tested_samples.append(f"❌ {filename} (status: {thumb_response.status_code})")
                                
                        except Exception as thumb_error:
                            inaccessible_count += 1
                            if len(tested_samples) < 3:
                                tested_samples.append(f"❌ {filename} (erreur: {str(thumb_error)[:30]})")
                        
                        # Limit testing to avoid timeout
                        if len(tested_samples) >= 5:
                            break
                
                total_tested = accessible_count + inaccessible_count
                success_rate = (accessible_count / total_tested * 100) if total_tested > 0 else 0
                webp_rate = (webp_content_type_count / accessible_count * 100) if accessible_count > 0 else 0
                
                details = f"TEST ACCESSIBILITÉ API: {total_tested} URLs testées, "
                details += f"{accessible_count} accessibles ({success_rate:.1f}%), "
                details += f"{webp_content_type_count} avec content-type: image/webp ({webp_rate:.1f}%). "
                details += f"Échantillons: {tested_samples}"
                
                # Success if we have accessible URLs and proper WEBP content-type
                test_success = accessible_count > 0 and webp_content_type_count > 0
                
                self.log_result(
                    "Test accessibilité URLs API", 
                    test_success, 
                    details
                )
                
                return test_success
            else:
                self.log_result(
                    "Test accessibilité URLs API", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Test accessibilité URLs API", False, error=str(e))
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
            self.test_url_update_endpoint,
            self.verify_url_update_results,
            self.test_api_accessibility
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
        
        if hasattr(self, 'before_update') and hasattr(self, 'after_update'):
            before = self.before_update
            after = self.after_update
            print(f"1. AVANT MISE À JOUR:")
            print(f"   • URLs claire-marcus.com: {before['claire_marcus_com_urls']}")
            print(f"   • URLs claire-marcus-api.onrender.com: {before['claire_marcus_api_urls']}")
            print()
            print(f"2. APRÈS MISE À JOUR:")
            print(f"   • URLs claire-marcus.com: {after['claire_marcus_com_urls']}")
            print(f"   • URLs claire-marcus-api.onrender.com: {after['claire_marcus_api_urls']}")
            print(f"   • Objectif atteint: {'✅ OUI' if after['update_successful'] else '❌ NON'}")
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