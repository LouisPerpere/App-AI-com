#!/usr/bin/env python3
"""
CRITICAL DELETE SYNCHRONIZATION DIAGNOSTIC TEST
Focus: Diagnosing why frontend deletions from claire-marcus.com are not synchronized with backend
Issue: User deleted 33 photos, frontend shows 6, backend shows 39 files
"""

import requests
import json
import os
import time
import uuid
from datetime import datetime

# Configuration - Using production URLs from review
BACKEND_URL = "https://social-ai-planner-2.preview.emergentagent.com/api"
FRONTEND_URL = "claire-marcus.com"
TEST_USER_EMAIL = "lperpere@yahoo.fr"
TEST_USER_PASSWORD = "L@Reunion974!"

class DeleteSyncDiagnosticTester:
    def __init__(self):
        self.session = requests.Session()
        # Disable SSL verification for testing
        self.session.verify = False
        # Disable SSL warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.access_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        return success
    
    def authenticate(self):
        """Authenticate with the backend using production credentials"""
        try:
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                return self.log_test("Authentication", True, f"Logged in as {TEST_USER_EMAIL}")
            else:
                return self.log_test("Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            return self.log_test("Authentication", False, f"Exception: {str(e)}")
    
    def test_backend_file_count(self):
        """Test 1: Get current backend file count"""
        try:
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if response.status_code == 200:
                data = response.json()
                content_files = data.get("content", [])
                total_files = data.get("total", len(content_files))
                
                details = f"Backend currently has {total_files} files. Expected: 6 files (after user deletions)"
                
                # Log the discrepancy
                if total_files == 39:
                    return self.log_test("Backend File Count", False, f"❌ CRITICAL: {details}. This confirms the synchronization issue - deletions not reaching backend")
                elif total_files == 6:
                    return self.log_test("Backend File Count", True, f"✅ RESOLVED: {details}. Synchronization working correctly")
                else:
                    return self.log_test("Backend File Count", False, f"⚠️ UNEXPECTED: {details}. Neither expected value (6 or 39)")
            else:
                return self.log_test("Backend File Count", False, f"API error: {response.status_code}")
                
        except Exception as e:
            return self.log_test("Backend File Count", False, f"Exception: {str(e)}")
    
    def test_cors_headers(self):
        """Test 2: Verify CORS headers for DELETE operations"""
        try:
            # Test OPTIONS request for DELETE endpoint
            options_response = self.session.options(f"{BACKEND_URL}/content/test-file-id", headers={
                "Origin": "https://claire-marcus.com",
                "Access-Control-Request-Method": "DELETE",
                "Access-Control-Request-Headers": "Authorization, Content-Type"
            })
            
            cors_headers = {
                "Access-Control-Allow-Origin": options_response.headers.get("Access-Control-Allow-Origin"),
                "Access-Control-Allow-Methods": options_response.headers.get("Access-Control-Allow-Methods"),
                "Access-Control-Allow-Headers": options_response.headers.get("Access-Control-Allow-Headers"),
                "Access-Control-Allow-Credentials": options_response.headers.get("Access-Control-Allow-Credentials")
            }
            
            # Check if DELETE is allowed
            allow_methods = cors_headers.get("Access-Control-Allow-Methods", "")
            delete_allowed = "DELETE" in allow_methods
            
            # Check if origin is allowed
            allow_origin = cors_headers.get("Access-Control-Allow-Origin", "")
            origin_allowed = allow_origin == "*" or "claire-marcus.com" in allow_origin
            
            details = f"DELETE allowed: {delete_allowed}, Origin allowed: {origin_allowed}, Status: {options_response.status_code}"
            
            if delete_allowed and origin_allowed:
                return self.log_test("CORS Headers for DELETE", True, details)
            else:
                return self.log_test("CORS Headers for DELETE", False, f"❌ CORS ISSUE: {details}")
                
        except Exception as e:
            return self.log_test("CORS Headers for DELETE", False, f"Exception: {str(e)}")
    
    def test_delete_endpoint_functionality(self):
        """Test 3: Test DELETE endpoint functionality with existing files"""
        try:
            # First get list of files
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if response.status_code != 200:
                return self.log_test("DELETE Endpoint Functionality", False, f"Cannot get file list: {response.status_code}")
            
            data = response.json()
            content_files = data.get("content", [])
            
            if not content_files:
                return self.log_test("DELETE Endpoint Functionality", False, "No files available to test deletion")
            
            # Test DELETE on the first file (but don't actually delete it - just test the endpoint)
            test_file = content_files[0]
            test_file_id = test_file["id"]
            
            # First, let's test with a non-existent file ID to avoid actually deleting user data
            fake_file_id = str(uuid.uuid4())
            delete_response = self.session.delete(f"{BACKEND_URL}/content/{fake_file_id}")
            
            if delete_response.status_code == 404:
                return self.log_test("DELETE Endpoint Functionality", True, f"DELETE endpoint working correctly - returns 404 for non-existent file")
            elif delete_response.status_code == 200:
                return self.log_test("DELETE Endpoint Functionality", False, f"❌ CRITICAL: DELETE endpoint returned 200 for non-existent file - this suggests endpoint issues")
            else:
                return self.log_test("DELETE Endpoint Functionality", False, f"❌ UNEXPECTED: DELETE endpoint returned {delete_response.status_code} for non-existent file")
                
        except Exception as e:
            return self.log_test("DELETE Endpoint Functionality", False, f"Exception: {str(e)}")
    
    def test_authentication_on_delete(self):
        """Test 4: Test authentication requirements for DELETE operations"""
        try:
            # Test DELETE without authentication
            session_no_auth = requests.Session()
            session_no_auth.verify = False
            
            # Get a file ID first
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            if response.status_code == 200:
                data = response.json()
                content_files = data.get("content", [])
                
                if content_files:
                    test_file_id = content_files[0]["id"]
                    
                    # Try DELETE without auth
                    unauth_response = session_no_auth.delete(f"{BACKEND_URL}/content/{test_file_id}")
                    
                    if unauth_response.status_code in [401, 403]:
                        return self.log_test("Authentication on DELETE", True, f"DELETE properly requires authentication - returns {unauth_response.status_code}")
                    elif unauth_response.status_code == 200:
                        return self.log_test("Authentication on DELETE", False, f"❌ SECURITY ISSUE: DELETE works without authentication")
                    else:
                        return self.log_test("Authentication on DELETE", True, f"DELETE endpoint accessible but returns {unauth_response.status_code} without auth")
                else:
                    return self.log_test("Authentication on DELETE", False, "No files available to test authentication")
            else:
                return self.log_test("Authentication on DELETE", False, f"Cannot get file list: {response.status_code}")
                
        except Exception as e:
            return self.log_test("Authentication on DELETE", False, f"Exception: {str(e)}")
    
    def test_network_connectivity(self):
        """Test 5: Test network connectivity and response times"""
        try:
            # Test basic connectivity
            start_time = time.time()
            health_response = self.session.get(f"{BACKEND_URL}/health")
            response_time = (time.time() - start_time) * 1000
            
            if health_response.status_code == 200:
                connectivity_ok = True
                connectivity_msg = f"Backend connectivity OK - response time: {response_time:.2f}ms"
            else:
                connectivity_ok = False
                connectivity_msg = f"Backend connectivity issue - status: {health_response.status_code}"
            
            # Test if backend is receiving requests from frontend domain
            headers_test = self.session.get(f"{BACKEND_URL}/content/pending", headers={
                "Origin": "https://claire-marcus.com",
                "Referer": "https://claire-marcus.com/"
            })
            
            origin_ok = headers_test.status_code == 200
            
            details = f"{connectivity_msg}. Origin header test: {'OK' if origin_ok else 'FAILED'}"
            
            return self.log_test("Network Connectivity", connectivity_ok and origin_ok, details)
                
        except Exception as e:
            return self.log_test("Network Connectivity", False, f"Exception: {str(e)}")
    
    def test_file_list_analysis(self):
        """Test 6: Analyze current file list to identify the 33 missing files"""
        try:
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if response.status_code == 200:
                data = response.json()
                content_files = data.get("content", [])
                total_files = len(content_files)
                
                # Analyze file metadata
                files_with_descriptions = 0
                files_without_descriptions = 0
                file_types = {}
                upload_dates = []
                
                for file_info in content_files:
                    # Count descriptions
                    description = file_info.get("description", "")
                    if description and description.strip():
                        files_with_descriptions += 1
                    else:
                        files_without_descriptions += 1
                    
                    # Count file types
                    file_type = file_info.get("file_type", "unknown")
                    file_types[file_type] = file_types.get(file_type, 0) + 1
                    
                    # Collect upload dates
                    upload_date = file_info.get("uploaded_at", "")
                    if upload_date:
                        upload_dates.append(upload_date)
                
                # Sort upload dates to see pattern
                upload_dates.sort()
                oldest_file = upload_dates[0] if upload_dates else "N/A"
                newest_file = upload_dates[-1] if upload_dates else "N/A"
                
                analysis = f"""
                Total files in backend: {total_files}
                Files with descriptions: {files_with_descriptions}
                Files without descriptions: {files_without_descriptions}
                File types: {file_types}
                Date range: {oldest_file} to {newest_file}
                Expected after deletions: 6 files
                Missing files: {total_files - 6} (should be the 33 deleted files)
                """
                
                if total_files > 6:
                    return self.log_test("File List Analysis", False, f"❌ SYNC ISSUE CONFIRMED: {analysis}")
                else:
                    return self.log_test("File List Analysis", True, f"✅ SYNC WORKING: {analysis}")
            else:
                return self.log_test("File List Analysis", False, f"Cannot get file list: {response.status_code}")
                
        except Exception as e:
            return self.log_test("File List Analysis", False, f"Exception: {str(e)}")
    
    def test_manual_delete_operation(self):
        """Test 7: Perform a manual DELETE operation to test if it works"""
        try:
            # First, upload a test file that we can safely delete
            test_file_content = b"DELETE SYNC TEST - This file can be safely deleted"
            files = {
                'files': ('delete_sync_test.jpg', test_file_content, 'image/jpeg')
            }
            
            upload_response = self.session.post(f"{BACKEND_URL}/content/batch-upload", files=files)
            
            if upload_response.status_code != 200:
                return self.log_test("Manual DELETE Operation", False, f"Cannot upload test file: {upload_response.status_code}")
            
            upload_data = upload_response.json()
            uploaded_files = upload_data.get("uploaded_files", [])
            
            if not uploaded_files:
                return self.log_test("Manual DELETE Operation", False, "No files uploaded for testing")
            
            # Get the file ID
            test_filename = uploaded_files[0]["stored_name"]
            test_file_id = test_filename.split('.')[0]
            
            # Wait a moment for file to be processed
            time.sleep(2)
            
            # Verify file exists in listing
            list_response = self.session.get(f"{BACKEND_URL}/content/pending")
            if list_response.status_code == 200:
                list_data = list_response.json()
                files_before = len(list_data.get("content", []))
                
                # Now delete the test file
                delete_response = self.session.delete(f"{BACKEND_URL}/content/{test_file_id}")
                
                if delete_response.status_code == 200:
                    delete_data = delete_response.json()
                    
                    # Wait a moment for deletion to be processed
                    time.sleep(2)
                    
                    # Verify file is gone
                    verify_response = self.session.get(f"{BACKEND_URL}/content/pending")
                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        files_after = len(verify_data.get("content", []))
                        
                        if files_after == files_before - 1:
                            return self.log_test("Manual DELETE Operation", True, f"✅ DELETE working correctly: {files_before} → {files_after} files")
                        else:
                            return self.log_test("Manual DELETE Operation", False, f"❌ DELETE failed: {files_before} → {files_after} files (expected {files_before - 1})")
                    else:
                        return self.log_test("Manual DELETE Operation", False, f"Cannot verify deletion: {verify_response.status_code}")
                else:
                    return self.log_test("Manual DELETE Operation", False, f"DELETE request failed: {delete_response.status_code}")
            else:
                return self.log_test("Manual DELETE Operation", False, f"Cannot get file list: {list_response.status_code}")
                
        except Exception as e:
            return self.log_test("Manual DELETE Operation", False, f"Exception: {str(e)}")
    
    def run_diagnostic_tests(self):
        """Run all DELETE synchronization diagnostic tests"""
        print("🚨 STARTING CRITICAL DELETE SYNCHRONIZATION DIAGNOSTIC")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Frontend URL: {FRONTEND_URL}")
        print(f"User: {TEST_USER_EMAIL}")
        print("=" * 70)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with diagnostics")
            return False
        
        print("\n📊 DIAGNOSTIC TEST 1: Backend File Count")
        print("-" * 50)
        self.test_backend_file_count()
        
        print("\n🌐 DIAGNOSTIC TEST 2: CORS Headers for DELETE")
        print("-" * 50)
        self.test_cors_headers()
        
        print("\n🔧 DIAGNOSTIC TEST 3: DELETE Endpoint Functionality")
        print("-" * 50)
        self.test_delete_endpoint_functionality()
        
        print("\n🔐 DIAGNOSTIC TEST 4: Authentication on DELETE")
        print("-" * 50)
        self.test_authentication_on_delete()
        
        print("\n🌍 DIAGNOSTIC TEST 5: Network Connectivity")
        print("-" * 50)
        self.test_network_connectivity()
        
        print("\n📋 DIAGNOSTIC TEST 6: File List Analysis")
        print("-" * 50)
        self.test_file_list_analysis()
        
        print("\n🧪 DIAGNOSTIC TEST 7: Manual DELETE Operation")
        print("-" * 50)
        self.test_manual_delete_operation()
        
        # Summary
        print("\n" + "=" * 70)
        print("📋 DIAGNOSTIC SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Diagnostic Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n🔍 CRITICAL FINDINGS:")
        for result in self.test_results:
            if not result["success"] and "CRITICAL" in result["details"]:
                print(f"  ❌ {result['test']}: {result['details']}")
        
        print("\n📊 ALL DIAGNOSTIC RESULTS:")
        for result in self.test_results:
            print(f"  {result['status']}: {result['test']}")
            if result['details']:
                print(f"      → {result['details']}")
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = DeleteSyncDiagnosticTester()
    success = tester.run_diagnostic_tests()
    
    if success:
        print("\n✅ ALL DIAGNOSTICS PASSED - DELETE synchronization working correctly")
    else:
        print("\n🚨 CRITICAL ISSUES FOUND - DELETE synchronization problems detected")
        print("\nRECOMMENDATIONS:")
        print("1. Check backend logs for DELETE requests from claire-marcus.com")
        print("2. Verify frontend is sending DELETE requests to correct endpoint")
        print("3. Check if authentication tokens are being sent correctly")
        print("4. Verify CORS configuration allows DELETE from claire-marcus.com")