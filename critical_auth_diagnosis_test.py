#!/usr/bin/env python3
"""
CRITICAL AUTHENTICATION DIAGNOSIS TEST
Investigating why content and thumbnail endpoints return 0 files despite successful login.

CONTEXT: 
- Migration completed successfully: 49 files migrated to MongoDB  
- Database verification: User 8aa0e7b1-5279-468b-bbce-028f7a70282d has 49 files in media collection
- Authentication works: login-robust endpoint returns valid JWT token  
- BUT: All content endpoints return 0 files (content/pending, thumbnails/status, thumbnails/rebuild)

INVESTIGATION REQUIRED:
1. Test Authentication Flow with lperpere@yahoo.fr / L@Reunion974!
2. Verify JWT token structure and user_id extraction
3. Test GET /api/auth/whoami to confirm authentication works
4. Test content endpoints and compare user_id from JWT vs expected user_id in database
5. Diagnose root cause of 0 files being returned
"""

import requests
import json
import jwt as jwt_lib
import os
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://social-ai-planner-2.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials as specified in review request
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"
EXPECTED_USER_ID = "8aa0e7b1-5279-468b-bbce-028f7a70282d"  # From review request

class CriticalAuthDiagnosisTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id_from_token = None
        self.user_id_from_login = None
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
    
    def test_login_robust(self):
        """Step 1: Test login-robust endpoint and extract JWT details"""
        print("🔐 STEP 1: Testing login-robust endpoint")
        print("=" * 50)
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login-robust", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id_from_login = data.get("user_id")
                
                # Decode JWT token to inspect payload
                try:
                    # Decode without verification to inspect payload
                    decoded_payload = jwt_lib.decode(self.access_token, options={"verify_signature": False})
                    self.user_id_from_token = decoded_payload.get("sub")
                    
                    jwt_details = f"JWT payload: {json.dumps(decoded_payload, indent=2)}"
                    
                    self.log_result(
                        "Login Robust Authentication", 
                        True, 
                        f"Login successful. User ID from response: {self.user_id_from_login}, User ID from JWT 'sub': {self.user_id_from_token}, Expected: {EXPECTED_USER_ID}. {jwt_details}"
                    )
                    
                    # Set authorization header for future requests
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.access_token}"
                    })
                    
                    return True
                    
                except Exception as jwt_error:
                    self.log_result(
                        "Login Robust Authentication", 
                        False, 
                        f"Login successful but JWT decode failed: {str(jwt_error)}"
                    )
                    return False
            else:
                self.log_result(
                    "Login Robust Authentication", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Login Robust Authentication", False, error=str(e))
            return False
    
    def test_whoami_endpoint(self):
        """Step 2: Test GET /api/auth/whoami to confirm authentication works"""
        print("🔍 STEP 2: Testing /api/auth/whoami endpoint")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{API_BASE}/auth/whoami")
            
            if response.status_code == 200:
                data = response.json()
                whoami_user_id = data.get("user_id")
                
                # Compare user IDs
                ids_match = whoami_user_id == self.user_id_from_token
                
                self.log_result(
                    "Whoami Authentication Test", 
                    True, 
                    f"Whoami successful. User ID from whoami: {whoami_user_id}, User ID from JWT: {self.user_id_from_token}, IDs match: {ids_match}"
                )
                return True
            else:
                self.log_result(
                    "Whoami Authentication Test", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Whoami Authentication Test", False, error=str(e))
            return False
    
    def test_content_pending_endpoint(self):
        """Step 3: Test GET /api/content/pending - should return 49 files but currently returns 0"""
        print("📁 STEP 3: Testing /api/content/pending endpoint")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{API_BASE}/content/pending?limit=100")
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                total = data.get("total", 0)
                
                # This is the critical issue - should be 49 files but returns 0
                expected_files = 49
                actual_files = len(content)
                
                success = actual_files > 0  # Any files found is progress
                
                details = f"Expected: {expected_files} files, Actual: {actual_files} files, Total from response: {total}"
                if actual_files > 0:
                    # Show sample file details
                    sample_file = content[0]
                    details += f". Sample file: ID={sample_file.get('id')}, filename={sample_file.get('filename')}, owner info available in logs"
                
                self.log_result(
                    "Content Pending Endpoint", 
                    success, 
                    details,
                    "CRITICAL ISSUE: 0 files returned despite 49 files in database" if actual_files == 0 else ""
                )
                
                # Store for analysis
                self.content_files_count = actual_files
                self.content_response = data
                
                return success
            else:
                self.log_result(
                    "Content Pending Endpoint", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Content Pending Endpoint", False, error=str(e))
            return False
    
    def test_thumbnails_status_endpoint(self):
        """Step 4: Test GET /api/content/thumbnails/status"""
        print("🖼️ STEP 4: Testing /api/content/thumbnails/status endpoint")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{API_BASE}/content/thumbnails/status")
            
            if response.status_code == 200:
                data = response.json()
                total_files = data.get("total_files", 0)
                with_thumbnails = data.get("with_thumbnails", 0)
                missing_thumbnails = data.get("missing_thumbnails", 0)
                completion_percentage = data.get("completion_percentage", 0)
                
                # Should show files needing thumbnails, but likely shows 0 due to same issue
                success = total_files > 0
                
                self.log_result(
                    "Thumbnails Status Endpoint", 
                    success, 
                    f"Total files: {total_files}, With thumbnails: {with_thumbnails}, Missing: {missing_thumbnails}, Completion: {completion_percentage}%",
                    "Same issue as content/pending - 0 files found" if total_files == 0 else ""
                )
                return success
            else:
                self.log_result(
                    "Thumbnails Status Endpoint", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Thumbnails Status Endpoint", False, error=str(e))
            return False
    
    def test_thumbnails_rebuild_endpoint(self):
        """Step 5: Test POST /api/content/thumbnails/rebuild"""
        print("🔄 STEP 5: Testing /api/content/thumbnails/rebuild endpoint")
        print("=" * 50)
        
        try:
            response = self.session.post(f"{API_BASE}/content/thumbnails/rebuild")
            
            if response.status_code == 200:
                data = response.json()
                scheduled = data.get("scheduled", 0)
                files_found = data.get("files_found", 0)
                
                # Should find files to process, but likely finds 0 due to same issue
                success = files_found > 0
                
                self.log_result(
                    "Thumbnails Rebuild Endpoint", 
                    success, 
                    f"Files found: {files_found}, Scheduled for rebuild: {scheduled}",
                    "Same issue - 0 files found for processing" if files_found == 0 else ""
                )
                return success
            else:
                self.log_result(
                    "Thumbnails Rebuild Endpoint", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Thumbnails Rebuild Endpoint", False, error=str(e))
            return False
    
    def test_debug_endpoint(self):
        """Step 6: Test debug endpoint if available to get more insights"""
        print("🔧 STEP 6: Testing debug endpoint for insights")
        print("=" * 50)
        
        try:
            # Try the debug endpoint mentioned in server.py
            response = self.session.get(f"{API_BASE}/content/_debug")
            
            if response.status_code == 200:
                data = response.json()
                
                self.log_result(
                    "Debug Endpoint", 
                    True, 
                    f"Debug data: {json.dumps(data, indent=2)}"
                )
                return True
            elif response.status_code == 404:
                self.log_result(
                    "Debug Endpoint", 
                    False, 
                    "Debug endpoint not available (404)",
                    "This is expected if debug endpoint is not implemented"
                )
                return False
            else:
                self.log_result(
                    "Debug Endpoint", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Debug Endpoint", False, error=str(e))
            return False
    
    def analyze_user_id_mismatch(self):
        """Step 7: Analyze potential user_id mismatch issues"""
        print("🔍 STEP 7: Analyzing user_id mismatch")
        print("=" * 50)
        
        try:
            # Compare all user IDs we've collected
            user_ids = {
                "Expected (from review)": EXPECTED_USER_ID,
                "From login response": self.user_id_from_login,
                "From JWT 'sub' claim": self.user_id_from_token
            }
            
            # Check if all IDs match
            all_ids = [self.user_id_from_login, self.user_id_from_token, EXPECTED_USER_ID]
            all_match = len(set(filter(None, all_ids))) == 1
            
            # Check specific mismatches
            login_vs_expected = self.user_id_from_login == EXPECTED_USER_ID
            jwt_vs_expected = self.user_id_from_token == EXPECTED_USER_ID
            login_vs_jwt = self.user_id_from_login == self.user_id_from_token
            
            analysis = f"User ID Analysis:\n"
            for source, user_id in user_ids.items():
                analysis += f"  • {source}: {user_id}\n"
            
            analysis += f"\nComparisons:\n"
            analysis += f"  • Login response vs Expected: {'✅ MATCH' if login_vs_expected else '❌ MISMATCH'}\n"
            analysis += f"  • JWT 'sub' vs Expected: {'✅ MATCH' if jwt_vs_expected else '❌ MISMATCH'}\n"
            analysis += f"  • Login response vs JWT 'sub': {'✅ MATCH' if login_vs_jwt else '❌ MISMATCH'}\n"
            analysis += f"  • All IDs consistent: {'✅ YES' if all_match else '❌ NO'}"
            
            # Determine if this is the root cause
            is_root_cause = not all_match
            
            self.log_result(
                "User ID Mismatch Analysis", 
                not is_root_cause,  # Success if no mismatch
                analysis,
                "USER ID MISMATCH DETECTED - This is likely the root cause!" if is_root_cause else ""
            )
            
            return not is_root_cause
            
        except Exception as e:
            self.log_result("User ID Mismatch Analysis", False, error=str(e))
            return False
    
    def test_alternative_login_endpoint(self):
        """Step 8: Test alternative login endpoint for comparison"""
        print("🔐 STEP 8: Testing alternative /api/auth/login endpoint")
        print("=" * 50)
        
        try:
            # Create new session for this test
            alt_session = requests.Session()
            
            response = alt_session.post(f"{API_BASE}/auth/login", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                alt_access_token = data.get("access_token")
                alt_user_id = data.get("user_id")
                
                # Decode JWT token to inspect payload
                try:
                    decoded_payload = jwt_lib.decode(alt_access_token, options={"verify_signature": False})
                    alt_jwt_user_id = decoded_payload.get("sub")
                    
                    # Compare with robust login
                    same_token = alt_access_token == self.access_token
                    same_user_id = alt_user_id == self.user_id_from_login
                    same_jwt_sub = alt_jwt_user_id == self.user_id_from_token
                    
                    details = f"Alternative login - User ID: {alt_user_id}, JWT 'sub': {alt_jwt_user_id}. "
                    details += f"Same as robust login - Token: {'✅' if same_token else '❌'}, "
                    details += f"User ID: {'✅' if same_user_id else '❌'}, JWT 'sub': {'✅' if same_jwt_sub else '❌'}"
                    
                    self.log_result(
                        "Alternative Login Endpoint", 
                        True, 
                        details
                    )
                    
                    return True
                    
                except Exception as jwt_error:
                    self.log_result(
                        "Alternative Login Endpoint", 
                        False, 
                        f"Login successful but JWT decode failed: {str(jwt_error)}"
                    )
                    return False
            else:
                self.log_result(
                    "Alternative Login Endpoint", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Alternative Login Endpoint", False, error=str(e))
            return False
    
    def run_critical_diagnosis(self):
        """Run all critical authentication diagnosis tests"""
        print("🚨 CRITICAL AUTHENTICATION DIAGNOSIS")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_EMAIL}")
        print(f"Expected User ID: {EXPECTED_USER_ID}")
        print(f"ISSUE: Content endpoints return 0 files despite 49 files in database")
        print("=" * 60)
        print()
        
        # Run tests in sequence
        tests = [
            self.test_login_robust,
            self.test_whoami_endpoint,
            self.test_content_pending_endpoint,
            self.test_thumbnails_status_endpoint,
            self.test_thumbnails_rebuild_endpoint,
            self.test_debug_endpoint,
            self.analyze_user_id_mismatch,
            self.test_alternative_login_endpoint
        ]
        
        for test in tests:
            test()
            print()
        
        # Summary and Root Cause Analysis
        print("🔍 ROOT CAUSE ANALYSIS")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print()
        
        # Analyze the results to determine root cause
        auth_working = any(r["test"] == "Login Robust Authentication" and r["success"] for r in self.test_results)
        whoami_working = any(r["test"] == "Whoami Authentication Test" and r["success"] for r in self.test_results)
        content_working = any(r["test"] == "Content Pending Endpoint" and r["success"] for r in self.test_results)
        user_id_consistent = any(r["test"] == "User ID Mismatch Analysis" and r["success"] for r in self.test_results)
        
        print("DIAGNOSIS SUMMARY:")
        print(f"• Authentication working: {'✅ YES' if auth_working else '❌ NO'}")
        print(f"• Whoami endpoint working: {'✅ YES' if whoami_working else '❌ NO'}")
        print(f"• Content endpoints working: {'✅ YES' if content_working else '❌ NO'}")
        print(f"• User ID consistency: {'✅ YES' if user_id_consistent else '❌ NO'}")
        print()
        
        # Determine root cause
        if auth_working and whoami_working and not content_working:
            if not user_id_consistent:
                print("🎯 ROOT CAUSE IDENTIFIED: USER ID MISMATCH")
                print("   The JWT token contains a different user_id than expected in the database.")
                print("   Content endpoints filter by owner_id but JWT 'sub' claim doesn't match.")
            else:
                print("🎯 ROOT CAUSE IDENTIFIED: DATABASE QUERY FILTERING ISSUE")
                print("   Authentication works but content queries are not finding files.")
                print("   Possible issues: owner_id field name mismatch, data type mismatch, or query logic error.")
        elif not auth_working:
            print("🎯 ROOT CAUSE IDENTIFIED: AUTHENTICATION FAILURE")
            print("   Basic authentication is not working properly.")
        else:
            print("🎯 ROOT CAUSE: UNCLEAR")
            print("   Need further investigation into database queries and filtering logic.")
        
        print()
        print("📋 DETAILED TEST RESULTS:")
        print("-" * 40)
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
            if result['error']:
                print(f"   ❌ {result['error']}")
            print()
        
        print("🚨 CRITICAL AUTHENTICATION DIAGNOSIS COMPLETED")
        
        return content_working  # Success if content endpoints are working

if __name__ == "__main__":
    tester = CriticalAuthDiagnosisTester()
    success = tester.run_critical_diagnosis()
    
    if success:
        print("✅ DIAGNOSIS: Content endpoints working - issue resolved")
        exit(0)
    else:
        print("❌ DIAGNOSIS: Content endpoints still returning 0 files - issue persists")
        exit(1)