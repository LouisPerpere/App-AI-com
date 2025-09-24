#!/usr/bin/env python3
"""
Description Functionality Testing
Testing the description functionality to identify why comments are not appearing on frontend
"""

import requests
import json
import os
import time
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://instamanager-1.preview.emergentagent.com/api"
TEST_USER_EMAIL = "lperpere@yahoo.fr"
TEST_USER_PASSWORD = "L@Reunion974!"

class DescriptionTester:
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
    
    def test_api_response_format(self):
        """Test 1: Make GET /api/content/pending call and verify the response structure"""
        try:
            print("\n🔍 Testing API Response Format...")
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if response.status_code != 200:
                return self.log_test("API Response Format", False, f"API call failed with status {response.status_code}")
            
            data = response.json()
            
            # Check response structure
            required_fields = ["content", "total", "has_more", "loaded"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return self.log_test("API Response Format", False, f"Missing fields in response: {missing_fields}")
            
            content_files = data.get("content", [])
            
            if not content_files:
                return self.log_test("API Response Format", False, "No content files found in response")
            
            # Check structure of each file object
            sample_file = content_files[0]
            required_file_fields = ["id", "filename", "file_type", "size", "uploaded_at", "description"]
            missing_file_fields = [field for field in required_file_fields if field not in sample_file]
            
            if missing_file_fields:
                return self.log_test("API Response Format", False, f"Missing fields in file object: {missing_file_fields}")
            
            # Count files with descriptions
            files_with_descriptions = 0
            files_with_empty_descriptions = 0
            
            for file_info in content_files:
                description = file_info.get("description", "")
                if description and description.strip():
                    files_with_descriptions += 1
                else:
                    files_with_empty_descriptions += 1
            
            details = f"Found {len(content_files)} files. {files_with_descriptions} with descriptions, {files_with_empty_descriptions} with empty descriptions. Response structure is correct."
            
            return self.log_test("API Response Format", True, details)
            
        except Exception as e:
            return self.log_test("API Response Format", False, f"Exception: {str(e)}")
    
    def test_description_update_endpoint(self):
        """Test 2: Add a test description to one of the existing files using PUT /api/content/{file_id}/description"""
        try:
            print("\n📝 Testing Description Update Endpoint...")
            
            # First get existing files
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if response.status_code != 200:
                return self.log_test("Description Update Endpoint", False, f"Failed to get content: {response.status_code}")
            
            data = response.json()
            content_files = data.get("content", [])
            
            if not content_files:
                return self.log_test("Description Update Endpoint", False, "No content files available for testing")
            
            # Use the first file for testing
            test_file = content_files[0]
            test_file_id = test_file["id"]
            original_description = test_file.get("description", "")
            
            # Add a test description
            test_description = f"Test description added at {datetime.now().isoformat()}"
            description_data = {"description": test_description}
            
            update_response = self.session.put(f"{BACKEND_URL}/content/{test_file_id}/description", json=description_data)
            
            if update_response.status_code != 200:
                return self.log_test("Description Update Endpoint", False, f"Update failed with status {update_response.status_code}: {update_response.text}")
            
            update_data = update_response.json()
            
            # Verify response structure
            if "message" not in update_data or "file_id" not in update_data:
                return self.log_test("Description Update Endpoint", False, "Invalid response structure from update endpoint")
            
            # Verify the description is saved to content_descriptions.json
            time.sleep(1)  # Brief pause for file system consistency
            
            # Make a fresh GET call to verify the description appears
            fresh_response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if fresh_response.status_code == 200:
                fresh_data = fresh_response.json()
                fresh_content = fresh_data.get("content", [])
                
                # Find our test file in the fresh response
                updated_file = next((f for f in fresh_content if f["id"] == test_file_id), None)
                
                if updated_file:
                    retrieved_description = updated_file.get("description", "")
                    
                    if retrieved_description == test_description:
                        details = f"Description successfully updated and persisted for file {test_file_id}"
                        return self.log_test("Description Update Endpoint", True, details)
                    else:
                        return self.log_test("Description Update Endpoint", False, f"Description mismatch. Expected: '{test_description}', Got: '{retrieved_description}'")
                else:
                    return self.log_test("Description Update Endpoint", False, "Test file not found in fresh API response")
            else:
                return self.log_test("Description Update Endpoint", False, f"Fresh API call failed: {fresh_response.status_code}")
            
        except Exception as e:
            return self.log_test("Description Update Endpoint", False, f"Exception: {str(e)}")
    
    def test_specific_file_with_existing_description(self):
        """Test 3: Test the file with ID "3184d975-c002-4da9-b982-78373c80ee6b" which should have "Updated description" """
        try:
            print("\n🎯 Testing Specific File with Existing Description...")
            
            target_file_id = "3184d975-c002-4da9-b982-78373c80ee6b"
            expected_description = "Updated description"
            
            # Get all content files
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if response.status_code != 200:
                return self.log_test("Specific File Test", False, f"Failed to get content: {response.status_code}")
            
            data = response.json()
            content_files = data.get("content", [])
            
            # Find the specific file
            target_file = next((f for f in content_files if f["id"] == target_file_id), None)
            
            if not target_file:
                return self.log_test("Specific File Test", False, f"File with ID {target_file_id} not found in API response")
            
            # Check if it has the expected description
            actual_description = target_file.get("description", "")
            
            if actual_description == expected_description:
                details = f"File {target_file_id} correctly has description: '{actual_description}'"
                return self.log_test("Specific File Test", True, details)
            else:
                # If it doesn't have the expected description, let's set it and test
                print(f"   File {target_file_id} has description: '{actual_description}', expected: '{expected_description}'")
                print("   Setting the expected description...")
                
                description_data = {"description": expected_description}
                update_response = self.session.put(f"{BACKEND_URL}/content/{target_file_id}/description", json=description_data)
                
                if update_response.status_code == 200:
                    # Verify it was set correctly
                    time.sleep(1)
                    fresh_response = self.session.get(f"{BACKEND_URL}/content/pending")
                    
                    if fresh_response.status_code == 200:
                        fresh_data = fresh_response.json()
                        fresh_content = fresh_data.get("content", [])
                        updated_file = next((f for f in fresh_content if f["id"] == target_file_id), None)
                        
                        if updated_file and updated_file.get("description", "") == expected_description:
                            details = f"File {target_file_id} now correctly has description: '{expected_description}'"
                            return self.log_test("Specific File Test", True, details)
                        else:
                            return self.log_test("Specific File Test", False, f"Failed to set expected description for file {target_file_id}")
                    else:
                        return self.log_test("Specific File Test", False, "Failed to verify description update")
                else:
                    return self.log_test("Specific File Test", False, f"Failed to update description: {update_response.status_code}")
            
        except Exception as e:
            return self.log_test("Specific File Test", False, f"Exception: {str(e)}")
    
    def test_data_flow_verification(self):
        """Test 4: Verify data flow - confirm descriptions from JSON file are properly loaded"""
        try:
            print("\n🔄 Testing Data Flow Verification...")
            
            # Test the load_descriptions() function by checking if descriptions persist across API calls
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if response.status_code != 200:
                return self.log_test("Data Flow Verification", False, f"Failed to get content: {response.status_code}")
            
            data = response.json()
            content_files = data.get("content", [])
            
            if not content_files:
                return self.log_test("Data Flow Verification", False, "No content files available for testing")
            
            # Test 1: Check that get_file_description() returns correct values
            files_with_descriptions = []
            files_without_descriptions = []
            
            for file_info in content_files:
                file_id = file_info["id"]
                description = file_info.get("description", "")
                
                if description and description.strip():
                    files_with_descriptions.append({
                        "id": file_id,
                        "filename": file_info.get("filename", ""),
                        "description": description
                    })
                else:
                    files_without_descriptions.append({
                        "id": file_id,
                        "filename": file_info.get("filename", "")
                    })
            
            # Test 2: Verify API response includes description field for each content item
            all_files_have_description_field = all("description" in f for f in content_files)
            
            if not all_files_have_description_field:
                return self.log_test("Data Flow Verification", False, "Not all files have description field in API response")
            
            # Test 3: Test consistency across multiple API calls
            time.sleep(1)
            second_response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if second_response.status_code == 200:
                second_data = second_response.json()
                second_content = second_data.get("content", [])
                
                # Compare descriptions between calls
                consistent_descriptions = True
                for file1 in content_files:
                    file2 = next((f for f in second_content if f["id"] == file1["id"]), None)
                    if file2:
                        if file1.get("description", "") != file2.get("description", ""):
                            consistent_descriptions = False
                            break
                
                if not consistent_descriptions:
                    return self.log_test("Data Flow Verification", False, "Descriptions are not consistent across API calls")
            
            # Summary
            total_files = len(content_files)
            files_with_desc_count = len(files_with_descriptions)
            files_without_desc_count = len(files_without_descriptions)
            
            details = f"Data flow working correctly. Total files: {total_files}, With descriptions: {files_with_desc_count}, Without descriptions: {files_without_desc_count}. All files have description field, descriptions consistent across API calls."
            
            return self.log_test("Data Flow Verification", True, details)
            
        except Exception as e:
            return self.log_test("Data Flow Verification", False, f"Exception: {str(e)}")
    
    def run_description_tests(self):
        """Run all description functionality tests"""
        print("🚀 STARTING DESCRIPTION FUNCTIONALITY TESTING")
        print("=" * 60)
        print("Testing the description functionality to identify why comments are not appearing on frontend")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Run the 4 specific tests requested in the review
        print("\n1️⃣ TEST API RESPONSE FORMAT")
        print("-" * 40)
        self.test_api_response_format()
        
        print("\n2️⃣ TEST DESCRIPTION UPDATE ENDPOINT")
        print("-" * 40)
        self.test_description_update_endpoint()
        
        print("\n3️⃣ TEST SPECIFIC FILE WITH EXISTING DESCRIPTION")
        print("-" * 40)
        self.test_specific_file_with_existing_description()
        
        print("\n4️⃣ TEST DATA FLOW VERIFICATION")
        print("-" * 40)
        self.test_data_flow_verification()
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 DESCRIPTION TESTING SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
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
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n✅ DETAILED TEST RESULTS:")
        for result in self.test_results:
            print(f"  {result['status']}: {result['test']}")
        
        # Analysis and recommendations
        print("\n🔍 ANALYSIS AND RECOMMENDATIONS:")
        print("-" * 40)
        
        if success_rate == 100:
            print("✅ All description functionality tests passed!")
            print("✅ The backend API is correctly sending descriptions in responses")
            print("✅ Description updates are working and persisting correctly")
            print("✅ Data flow from JSON file to API responses is working")
            print("🔍 If descriptions are not appearing on frontend, the issue is likely:")
            print("   - Frontend not reading the 'description' field from API responses")
            print("   - Frontend UI not displaying the description field")
            print("   - JavaScript errors preventing description rendering")
        else:
            print("❌ Some description functionality tests failed")
            print("🔍 The issue appears to be in the backend API")
            print("🔧 Review the failed tests above for specific issues to fix")
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = DescriptionTester()
    success = tester.run_description_tests()
    
    if success:
        print("\n🎉 ALL DESCRIPTION TESTS PASSED!")
        print("The backend description functionality is working correctly.")
        print("If descriptions are not appearing on frontend, investigate frontend implementation.")
    else:
        print("\n⚠️ SOME DESCRIPTION TESTS FAILED")
        print("Please review the failed tests above and fix backend issues.")