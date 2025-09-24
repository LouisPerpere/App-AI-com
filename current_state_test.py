#!/usr/bin/env python3
"""
CURRENT STATE VERIFICATION TEST
Verify the actual current state of the system after seeing DELETE operations in logs
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://instamanager-1.preview.emergentagent.com/api"
TEST_USER_EMAIL = "lperpere@yahoo.fr"
TEST_USER_PASSWORD = "L@Reunion974!"

class CurrentStateVerifier:
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
    
    def get_current_file_count(self):
        """Get current file count and details"""
        try:
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if response.status_code == 200:
                data = response.json()
                content_files = data.get("content", [])
                total_files = data.get("total", len(content_files))
                
                print(f"📊 CURRENT STATE:")
                print(f"   Total files: {total_files}")
                print(f"   Files in response: {len(content_files)}")
                
                # Analyze files
                files_with_descriptions = 0
                recent_files = []
                
                for file_info in content_files:
                    description = file_info.get("description", "")
                    if description and description.strip():
                        files_with_descriptions += 1
                    
                    # Check if file was uploaded recently (today)
                    upload_date = file_info.get("uploaded_at", "")
                    if "2025-08-16" in upload_date:
                        recent_files.append({
                            "id": file_info["id"],
                            "filename": file_info["filename"],
                            "uploaded_at": upload_date,
                            "description": description
                        })
                
                print(f"   Files with descriptions: {files_with_descriptions}")
                print(f"   Files uploaded today: {len(recent_files)}")
                
                if recent_files:
                    print(f"\n📋 TODAY'S FILES:")
                    for file_info in recent_files[:5]:  # Show first 5
                        desc_status = "with description" if file_info["description"] else "no description"
                        print(f"   - {file_info['filename']} ({desc_status})")
                
                return total_files
            else:
                print(f"❌ Failed to get file count: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Exception getting file count: {str(e)}")
            return None
    
    def test_delete_functionality(self):
        """Test if DELETE is actually working by uploading and deleting a test file"""
        try:
            print(f"\n🧪 TESTING DELETE FUNCTIONALITY:")
            
            # Upload a test file
            test_file_content = b"CURRENT STATE TEST - DELETE VERIFICATION"
            files = {
                'files': ('current_state_test.jpg', test_file_content, 'image/jpeg')
            }
            
            upload_response = self.session.post(f"{BACKEND_URL}/content/batch-upload", files=files)
            
            if upload_response.status_code != 200:
                print(f"❌ Upload failed: {upload_response.status_code}")
                return False
            
            upload_data = upload_response.json()
            uploaded_files = upload_data.get("uploaded_files", [])
            
            if not uploaded_files:
                print(f"❌ No files uploaded")
                return False
            
            test_filename = uploaded_files[0]["stored_name"]
            test_file_id = test_filename.split('.')[0]
            
            print(f"   ✅ Uploaded test file: {test_filename}")
            
            # Get file count before deletion
            before_response = self.session.get(f"{BACKEND_URL}/content/pending")
            files_before = len(before_response.json().get("content", [])) if before_response.status_code == 200 else 0
            
            # Delete the test file
            delete_response = self.session.delete(f"{BACKEND_URL}/content/{test_file_id}")
            
            if delete_response.status_code == 200:
                delete_data = delete_response.json()
                print(f"   ✅ DELETE request successful")
                print(f"   Response: {delete_data}")
                
                # Wait and check if file is actually gone
                time.sleep(2)
                
                after_response = self.session.get(f"{BACKEND_URL}/content/pending")
                files_after = len(after_response.json().get("content", [])) if after_response.status_code == 200 else 0
                
                print(f"   Files before: {files_before}")
                print(f"   Files after: {files_after}")
                
                if files_after == files_before - 1:
                    print(f"   ✅ DELETE working correctly!")
                    return True
                else:
                    print(f"   ❌ DELETE not working - file count unchanged")
                    return False
            else:
                print(f"   ❌ DELETE request failed: {delete_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Exception testing DELETE: {str(e)}")
            return False
    
    def run_verification(self):
        """Run current state verification"""
        print("🔍 CURRENT STATE VERIFICATION")
        print("=" * 50)
        
        if not self.authenticate():
            return False
        
        # Get current state
        current_count = self.get_current_file_count()
        
        if current_count is None:
            return False
        
        # Test DELETE functionality
        delete_working = self.test_delete_functionality()
        
        # Final state after test
        final_count = self.get_current_file_count()
        
        print(f"\n📋 VERIFICATION SUMMARY:")
        print(f"   Initial file count: {current_count}")
        print(f"   DELETE functionality: {'✅ Working' if delete_working else '❌ Not working'}")
        print(f"   Final file count: {final_count}")
        
        # Analysis
        if current_count == 6:
            print(f"\n✅ SYNC STATUS: Files match expected count (6) - deletions are synchronized!")
        elif current_count > 6:
            missing_deletions = current_count - 6
            print(f"\n⚠️ SYNC STATUS: {missing_deletions} files more than expected - some deletions may not have been processed")
        else:
            print(f"\n⚠️ SYNC STATUS: Fewer files than expected - possible over-deletion")
        
        return True

if __name__ == "__main__":
    verifier = CurrentStateVerifier()
    verifier.run_verification()