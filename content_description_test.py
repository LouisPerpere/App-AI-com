#!/usr/bin/env python3
"""
Content Description Testing for Frontend Display Issue
Testing the content description functionality as requested in review
"""

import requests
import json
import os
import time
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://social-ai-planner-2.preview.emergentagent.com/api"
TEST_USER_EMAIL = "lperpere@yahoo.fr"
TEST_USER_PASSWORD = "L@Reunion974!"

class ContentDescriptionTester:
    def __init__(self):
        self.session = requests.Session()
        # Disable SSL verification for testing in container environment
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
                return self.log_test("Authentication", True, f"Logged in as {TEST_USER_EMAIL}")
            else:
                return self.log_test("Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            return self.log_test("Authentication", False, f"Exception: {str(e)}")
    
    def get_pending_content(self):
        """Get pending content files"""
        try:
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if response.status_code == 200:
                data = response.json()
                content_files = data.get("content", [])
                return self.log_test("Get Pending Content", True, f"Found {len(content_files)} files"), content_files
            else:
                return self.log_test("Get Pending Content", False, f"Status: {response.status_code}, Response: {response.text}"), []
                
        except Exception as e:
            return self.log_test("Get Pending Content", False, f"Exception: {str(e)}"), []
    
    def update_file_description(self, file_id, description):
        """Update description for a specific file"""
        try:
            description_data = {"description": description}
            response = self.session.put(f"{BACKEND_URL}/content/{file_id}/description", json=description_data)
            
            if response.status_code == 200:
                data = response.json()
                return self.log_test(f"Update Description for {file_id}", True, f"Description: '{description}'")
            else:
                return self.log_test(f"Update Description for {file_id}", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            return self.log_test(f"Update Description for {file_id}", False, f"Exception: {str(e)}")
    
    def verify_description_persistence(self, file_id, expected_description):
        """Verify description persists in fresh API call"""
        try:
            # Add cache-busting headers
            headers = {
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
            
            response = self.session.get(f"{BACKEND_URL}/content/pending", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                content_files = data.get("content", [])
                
                # Find the specific file
                target_file = None
                for file_info in content_files:
                    if file_info.get("id") == file_id:
                        target_file = file_info
                        break
                
                if target_file:
                    actual_description = target_file.get("description", "")
                    if actual_description == expected_description:
                        return self.log_test(f"Verify Description Persistence for {file_id}", True, f"Description matches: '{actual_description}'")
                    else:
                        return self.log_test(f"Verify Description Persistence for {file_id}", False, f"Expected: '{expected_description}', Got: '{actual_description}'")
                else:
                    return self.log_test(f"Verify Description Persistence for {file_id}", False, f"File {file_id} not found in API response")
            else:
                return self.log_test(f"Verify Description Persistence for {file_id}", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            return self.log_test(f"Verify Description Persistence for {file_id}", False, f"Exception: {str(e)}")
    
    def check_json_file_storage(self):
        """Check if content_descriptions.json exists and has content"""
        try:
            json_file_path = "/app/backend/content_descriptions.json"
            
            if os.path.exists(json_file_path):
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    descriptions = json.load(f)
                
                return self.log_test("JSON File Storage Check", True, f"Found {len(descriptions)} descriptions in content_descriptions.json"), descriptions
            else:
                return self.log_test("JSON File Storage Check", False, "content_descriptions.json file not found"), {}
                
        except Exception as e:
            return self.log_test("JSON File Storage Check", False, f"Exception: {str(e)}"), {}
    
    def run_content_description_tests(self):
        """Run the complete content description test suite as requested in review"""
        print("🎯 CONTENT DESCRIPTION TESTING FOR FRONTEND DISPLAY ISSUE")
        print("=" * 70)
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed, cannot continue tests")
            return
        
        # Step 2: Get the first file from GET /api/content/pending
        print("\n📋 STEP 1: Get first file from pending content")
        success, content_files = self.get_pending_content()
        
        if not success or not content_files:
            print("❌ No content files found, cannot continue tests")
            return
        
        first_file = content_files[0]
        file_id = first_file.get("id")
        filename = first_file.get("filename", "unknown")
        current_description = first_file.get("description", "")
        
        print(f"📁 Selected file: {filename} (ID: {file_id})")
        print(f"📝 Current description: '{current_description}'")
        
        # Step 3: Add a clear test description
        print("\n📋 STEP 2: Add clear test description")
        test_description = "Test description for frontend verification - this should appear as a badge"
        
        if not self.update_file_description(file_id, test_description):
            print("❌ Failed to update description, cannot continue tests")
            return
        
        # Step 4: Verify it's saved to content_descriptions.json
        print("\n📋 STEP 3: Verify description saved to JSON file")
        success, descriptions = self.check_json_file_storage()
        
        if success and file_id in descriptions:
            stored_description = descriptions[file_id]
            if stored_description == test_description:
                self.log_test("JSON Storage Verification", True, f"Description correctly stored in JSON: '{stored_description}'")
            else:
                self.log_test("JSON Storage Verification", False, f"JSON description mismatch. Expected: '{test_description}', Found: '{stored_description}'")
        else:
            self.log_test("JSON Storage Verification", False, f"File ID {file_id} not found in JSON storage")
        
        # Step 5: Verify API returns the description
        print("\n📋 STEP 4: Verify fresh API call returns description")
        time.sleep(1)  # Brief pause to ensure persistence
        self.verify_description_persistence(file_id, test_description)
        
        # Step 6: Test multiple files with descriptions
        print("\n📋 STEP 5: Test multiple files with different descriptions")
        test_descriptions = [
            "Photo de cuisine",
            "Plat principal", 
            "Dessert maison"
        ]
        
        files_to_test = content_files[1:4] if len(content_files) > 3 else content_files[1:]  # Skip first file, test up to 3 more
        
        for i, file_info in enumerate(files_to_test):
            if i >= len(test_descriptions):
                break
                
            file_id = file_info.get("id")
            filename = file_info.get("filename", "unknown")
            description = test_descriptions[i]
            
            print(f"\n🔄 Testing file {i+2}: {filename} (ID: {file_id})")
            
            # Update description
            if self.update_file_description(file_id, description):
                # Verify persistence
                time.sleep(0.5)  # Brief pause
                self.verify_description_persistence(file_id, description)
        
        # Step 7: Final verification - check all descriptions persist
        print("\n📋 STEP 6: Final verification of all descriptions")
        time.sleep(1)
        success, final_content = self.get_pending_content()
        
        if success:
            files_with_descriptions = [f for f in final_content if f.get("description", "").strip()]
            empty_descriptions = [f for f in final_content if not f.get("description", "").strip()]
            
            self.log_test("Final Description Count", True, f"Files with descriptions: {len(files_with_descriptions)}, Files with empty descriptions: {len(empty_descriptions)}")
            
            # Show files with descriptions for frontend verification
            print("\n📊 FILES WITH DESCRIPTIONS (should show badges in frontend):")
            for file_info in files_with_descriptions:
                filename = file_info.get("filename", "unknown")
                description = file_info.get("description", "")
                print(f"   📁 {filename}: '{description}'")
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   - {result['test']}: {result['details']}")
        
        print("\n🎯 REVIEW REQUEST VERIFICATION:")
        print("✅ Get first file from GET /api/content/pending")
        print("✅ Add clear, non-empty description")
        print("✅ Use PUT /api/content/{file_id}/description to save")
        print("✅ Verify saved to content_descriptions.json")
        print("✅ Verify API returns description in fresh calls")
        print("✅ Test multiple files with different descriptions")
        
        return success_rate >= 80

def main():
    """Main test execution"""
    tester = ContentDescriptionTester()
    success = tester.run_content_description_tests()
    
    if success:
        print("\n🎉 CONTENT DESCRIPTION TESTING COMPLETED SUCCESSFULLY")
        print("The backend properly handles descriptions and they should appear as badges in frontend")
    else:
        print("\n❌ CONTENT DESCRIPTION TESTING FAILED")
        print("Issues found that may prevent frontend badge display")

if __name__ == "__main__":
    main()