#!/usr/bin/env python3
"""
PAGINATION AND FILE COUNT DIAGNOSTIC TEST
Check if pagination is causing the DELETE sync issue
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://claire-marcus-app-1.preview.emergentagent.com/api"
TEST_USER_EMAIL = "lperpere@yahoo.fr"
TEST_USER_PASSWORD = "L@Reunion974!"

class PaginationDiagnostic:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.access_token = None
        
    def authenticate(self):
        """Authenticate with the backend"""
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
                print(f"✅ Authenticated as {TEST_USER_EMAIL}")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication exception: {str(e)}")
            return False
    
    def test_pagination_limits(self):
        """Test different pagination limits"""
        print(f"\n📊 TESTING PAGINATION LIMITS:")
        
        limits_to_test = [24, 50, 100, 1000]
        
        for limit in limits_to_test:
            try:
                response = self.session.get(f"{BACKEND_URL}/content/pending?limit={limit}")
                
                if response.status_code == 200:
                    data = response.json()
                    content_files = data.get("content", [])
                    total_files = data.get("total", 0)
                    has_more = data.get("has_more", False)
                    
                    print(f"   Limit {limit}: {len(content_files)} files returned, total: {total_files}, has_more: {has_more}")
                else:
                    print(f"   Limit {limit}: API error {response.status_code}")
                    
            except Exception as e:
                print(f"   Limit {limit}: Exception {str(e)}")
    
    def test_file_system_vs_api(self):
        """Compare file system count vs API count"""
        print(f"\n🔍 FILE SYSTEM VS API COMPARISON:")
        
        try:
            # Get API count
            response = self.session.get(f"{BACKEND_URL}/content/pending?limit=1000")
            
            if response.status_code == 200:
                data = response.json()
                api_files = data.get("content", [])
                api_total = data.get("total", 0)
                
                print(f"   API reports: {api_total} total files")
                print(f"   API returned: {len(api_files)} files in response")
                
                # Check if we can get file system count (this won't work in production but let's try)
                try:
                    # This is just for diagnostic - won't work in production
                    print(f"   File system: Cannot check directly in production environment")
                except:
                    pass
                
                # Analyze the files we got
                valid_files = 0
                invalid_files = 0
                files_with_data = 0
                files_without_data = 0
                
                for file_info in api_files:
                    if file_info.get("file_data") or file_info.get("thumbnail_data"):
                        files_with_data += 1
                        valid_files += 1
                    else:
                        files_without_data += 1
                        if file_info.get("size", 0) > 0:
                            valid_files += 1
                        else:
                            invalid_files += 1
                
                print(f"   Files with image data: {files_with_data}")
                print(f"   Files without image data: {files_without_data}")
                print(f"   Valid files: {valid_files}")
                print(f"   Invalid files: {invalid_files}")
                
            else:
                print(f"   API error: {response.status_code}")
                
        except Exception as e:
            print(f"   Exception: {str(e)}")
    
    def test_delete_with_full_pagination(self):
        """Test DELETE with full pagination to see real impact"""
        print(f"\n🧪 TESTING DELETE WITH FULL PAGINATION:")
        
        try:
            # Get full file list before
            before_response = self.session.get(f"{BACKEND_URL}/content/pending?limit=1000")
            
            if before_response.status_code != 200:
                print(f"   ❌ Cannot get file list: {before_response.status_code}")
                return
            
            before_data = before_response.json()
            files_before = before_data.get("content", [])
            total_before = before_data.get("total", 0)
            
            print(f"   Before: {total_before} total files, {len(files_before)} in response")
            
            # Upload a test file
            test_file_content = b"PAGINATION DELETE TEST"
            files = {
                'files': ('pagination_test.jpg', test_file_content, 'image/jpeg')
            }
            
            upload_response = self.session.post(f"{BACKEND_URL}/content/batch-upload", files=files)
            
            if upload_response.status_code != 200:
                print(f"   ❌ Upload failed: {upload_response.status_code}")
                return
            
            upload_data = upload_response.json()
            uploaded_files = upload_data.get("uploaded_files", [])
            
            if not uploaded_files:
                print(f"   ❌ No files uploaded")
                return
            
            test_filename = uploaded_files[0]["stored_name"]
            test_file_id = test_filename.split('.')[0]
            
            print(f"   ✅ Uploaded: {test_filename}")
            
            # Get count after upload
            after_upload_response = self.session.get(f"{BACKEND_URL}/content/pending?limit=1000")
            if after_upload_response.status_code == 200:
                after_upload_data = after_upload_response.json()
                total_after_upload = after_upload_data.get("total", 0)
                print(f"   After upload: {total_after_upload} total files")
            
            # Delete the test file
            delete_response = self.session.delete(f"{BACKEND_URL}/content/{test_file_id}")
            
            if delete_response.status_code == 200:
                delete_data = delete_response.json()
                print(f"   ✅ DELETE successful: {delete_data.get('message', 'No message')}")
                
                # Get count after delete with full pagination
                after_delete_response = self.session.get(f"{BACKEND_URL}/content/pending?limit=1000")
                
                if after_delete_response.status_code == 200:
                    after_delete_data = after_delete_response.json()
                    files_after = after_delete_data.get("content", [])
                    total_after = after_delete_data.get("total", 0)
                    
                    print(f"   After delete: {total_after} total files, {len(files_after)} in response")
                    
                    # Check if the specific file is gone
                    file_still_exists = any(f["id"] == test_file_id for f in files_after)
                    print(f"   Test file still exists: {file_still_exists}")
                    
                    # Summary
                    if total_after == total_before and not file_still_exists:
                        print(f"   ✅ DELETE working correctly with pagination!")
                    elif total_after == total_before and file_still_exists:
                        print(f"   ❌ DELETE failed - file still in list")
                    elif total_after != total_before:
                        print(f"   ⚠️ Total count changed: {total_before} → {total_after}")
                else:
                    print(f"   ❌ Cannot get file list after delete: {after_delete_response.status_code}")
            else:
                print(f"   ❌ DELETE failed: {delete_response.status_code}")
                
        except Exception as e:
            print(f"   Exception: {str(e)}")
    
    def run_diagnostic(self):
        """Run pagination diagnostic"""
        print("🔍 PAGINATION AND FILE COUNT DIAGNOSTIC")
        print("=" * 60)
        
        if not self.authenticate():
            return False
        
        self.test_pagination_limits()
        self.test_file_system_vs_api()
        self.test_delete_with_full_pagination()
        
        print(f"\n📋 DIAGNOSTIC COMPLETE")
        return True

if __name__ == "__main__":
    diagnostic = PaginationDiagnostic()
    diagnostic.run_diagnostic()