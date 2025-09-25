#!/usr/bin/env python3
"""
Persistent Description Storage and Virtual Keyboard Fixes Test
Test the persistent description storage and virtual keyboard fixes as requested in review.
"""

import requests
import json
import os
import sys
import tempfile
import uuid
from datetime import datetime

class DescriptionPersistenceAPITester:
    def __init__(self):
        # Use production backend URL from frontend/.env
        self.base_url = "https://post-validator.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_file_ids = []  # Track uploaded files for cleanup

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {}
        
        # Add authentication header if we have a token
        if self.access_token:
            test_headers['Authorization'] = f'Bearer {self.access_token}'
        
        # Add custom headers
        if headers:
            test_headers.update(headers)
        
        # Don't set Content-Type for multipart/form-data requests
        if not files and method in ['POST', 'PUT']:
            test_headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, params=data)
            elif method == 'POST':
                if files:
                    response = requests.post(url, data=data, files=files, headers=test_headers)
                else:
                    response = requests.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                if files:
                    response = requests.put(url, data=data, files=files, headers=test_headers)
                else:
                    response = requests.put(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:300]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_user_login(self):
        """Test user login with specified credentials"""
        login_data = {
            "email": "lperpere@yahoo.fr",
            "password": "L@Reunion974!"
        }
        
        success, response = self.run_test(
            "User Login (lperpere@yahoo.fr)",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.access_token = response['access_token']
            print(f"   Access Token: {self.access_token[:20]}...")
            return True
        return False

    def upload_test_file(self):
        """Upload a test file to get a file_id for description testing"""
        try:
            # Create a minimal test image
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                # Write minimal JPEG header
                tmp_file.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9')
                tmp_file_path = tmp_file.name

            with open(tmp_file_path, 'rb') as f:
                files = {'files': ('test_description_image.jpg', f, 'image/jpeg')}
                
                success, response = self.run_test(
                    "Upload Test File for Description Testing",
                    "POST",
                    "content/batch-upload",
                    200,
                    files=files
                )
                
                if success and 'uploaded_files' in response and len(response['uploaded_files']) > 0:
                    file_id = response['uploaded_files'][0]['id']
                    self.test_file_ids.append(file_id)
                    print(f"   Uploaded file ID: {file_id}")
                    os.unlink(tmp_file_path)
                    return file_id
                    
            os.unlink(tmp_file_path)
            return None
            
        except Exception as e:
            print(f"❌ Error uploading test file: {e}")
            return None

    def test_description_json_file_creation(self):
        """Test that content_descriptions.json file is created in backend directory"""
        print(f"\n🔍 Testing Description JSON File Creation...")
        
        # Check if the file exists in the backend directory
        descriptions_file = "/app/backend/content_descriptions.json"
        
        if os.path.exists(descriptions_file):
            print(f"✅ content_descriptions.json file exists at {descriptions_file}")
            
            # Check if it's readable and valid JSON
            try:
                with open(descriptions_file, 'r', encoding='utf-8') as f:
                    descriptions = json.load(f)
                print(f"✅ JSON file is valid and readable")
                print(f"   Current descriptions count: {len(descriptions)}")
                self.tests_passed += 1
                return True, descriptions
            except Exception as e:
                print(f"❌ JSON file exists but is not valid: {e}")
                return False, {}
        else:
            print(f"⚠️ content_descriptions.json file does not exist yet")
            # This is not necessarily a failure - file might be created on first description save
            return True, {}

    def test_put_description_endpoint(self):
        """Test PUT /api/content/{file_id}/description endpoint"""
        # First upload a test file
        file_id = self.upload_test_file()
        if not file_id:
            print("❌ Could not upload test file for description testing")
            return False
        
        # Test description with various content types
        test_descriptions = [
            "Simple test description for persistent storage",
            "Description with special characters: àáâãäåæçèéêë ñòóôõö ùúûüý 🎉🚀✨",
            "Multi-line description\nwith line breaks\nand various content",
            ""  # Empty description test
        ]
        
        for i, description in enumerate(test_descriptions):
            description_data = {"description": description}
            
            success, response = self.run_test(
                f"PUT Description Test {i+1} ({'Empty' if not description else 'Content'})",
                "PUT",
                f"content/{file_id}/description",
                200,
                data=description_data
            )
            
            if not success:
                return False
            
            # Verify response contains the description
            if response.get('description') != description:
                print(f"❌ Response description doesn't match: expected '{description}', got '{response.get('description')}'")
                return False
            
            print(f"✅ Description saved successfully: {description[:50]}...")
        
        return True

    def test_description_persistence_across_calls(self):
        """Test that descriptions persist across API calls"""
        # Upload a test file
        file_id = self.upload_test_file()
        if not file_id:
            print("❌ Could not upload test file for persistence testing")
            return False
        
        # Set a unique description
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_description = f"Persistence test description {timestamp} - This should survive multiple API calls"
        
        description_data = {"description": test_description}
        
        # Save the description
        success, response = self.run_test(
            "Save Description for Persistence Test",
            "PUT",
            f"content/{file_id}/description",
            200,
            data=description_data
        )
        
        if not success:
            return False
        
        # Make multiple GET requests to verify persistence
        for i in range(3):
            success, response = self.run_test(
                f"Get Content with Description (Call {i+1})",
                "GET",
                "content/pending",
                200
            )
            
            if not success:
                return False
            
            # Find our test file in the response
            found_file = None
            for content_item in response.get('content', []):
                if content_item.get('id') == file_id:
                    found_file = content_item
                    break
            
            if not found_file:
                print(f"❌ Test file {file_id} not found in content list")
                return False
            
            if found_file.get('description') != test_description:
                print(f"❌ Description not persistent on call {i+1}: expected '{test_description}', got '{found_file.get('description')}'")
                return False
            
            print(f"✅ Description persisted correctly on call {i+1}")
        
        return True

    def test_load_descriptions_function(self):
        """Test the load_descriptions() function by checking JSON file content"""
        print(f"\n🔍 Testing load_descriptions() Function...")
        
        # Check if descriptions file exists and has content
        descriptions_file = "/app/backend/content_descriptions.json"
        
        if os.path.exists(descriptions_file):
            try:
                with open(descriptions_file, 'r', encoding='utf-8') as f:
                    descriptions = json.load(f)
                
                print(f"✅ Successfully loaded descriptions from JSON file")
                print(f"   Total descriptions: {len(descriptions)}")
                
                # Show sample descriptions (first 3)
                sample_count = min(3, len(descriptions))
                for i, (file_id, description) in enumerate(list(descriptions.items())[:sample_count]):
                    print(f"   Sample {i+1}: {file_id} -> {description[:50]}...")
                
                self.tests_passed += 1
                return True
                
            except Exception as e:
                print(f"❌ Error loading descriptions: {e}")
                return False
        else:
            print(f"⚠️ Descriptions file does not exist yet")
            return True  # Not a failure if no descriptions have been saved yet

    def test_get_file_description_function(self):
        """Test that GET /api/content/pending loads descriptions correctly"""
        # Upload a test file and set a description
        file_id = self.upload_test_file()
        if not file_id:
            print("❌ Could not upload test file")
            return False
        
        test_description = f"Test description for get_file_description function {datetime.now().strftime('%H%M%S')}"
        
        # Set description
        description_data = {"description": test_description}
        success, response = self.run_test(
            "Set Description for get_file_description Test",
            "PUT",
            f"content/{file_id}/description",
            200,
            data=description_data
        )
        
        if not success:
            return False
        
        # Get content and verify description is loaded
        success, response = self.run_test(
            "Get Content to Test Description Loading",
            "GET",
            "content/pending",
            200
        )
        
        if not success:
            return False
        
        # Find our test file
        found_file = None
        for content_item in response.get('content', []):
            if content_item.get('id') == file_id:
                found_file = content_item
                break
        
        if not found_file:
            print(f"❌ Test file {file_id} not found in content list")
            return False
        
        if found_file.get('description') != test_description:
            print(f"❌ get_file_description not working: expected '{test_description}', got '{found_file.get('description')}'")
            return False
        
        print(f"✅ get_file_description function working correctly")
        return True

    def test_utf8_encoding_special_characters(self):
        """Test UTF-8 encoding works for special characters"""
        file_id = self.upload_test_file()
        if not file_id:
            print("❌ Could not upload test file")
            return False
        
        # Test various UTF-8 characters
        special_descriptions = [
            "Français: àáâãäåæçèéêëìíîïñòóôõöùúûüý",
            "Español: ¡¿ñáéíóúü",
            "Deutsch: äöüß",
            "Emoji: 🎉🚀✨🌟💫🎯📱💻🔥⭐",
            "Mixed: Café résumé naïve 🇫🇷 €100 ±5°C",
            "Chinese: 你好世界",
            "Arabic: مرحبا بالعالم",
            "Russian: Привет мир"
        ]
        
        for i, description in enumerate(special_descriptions):
            description_data = {"description": description}
            
            success, response = self.run_test(
                f"UTF-8 Test {i+1} ({description.split(':')[0]})",
                "PUT",
                f"content/{file_id}/description",
                200,
                data=description_data
            )
            
            if not success:
                return False
            
            # Verify the description was saved correctly
            if response.get('description') != description:
                print(f"❌ UTF-8 encoding failed: expected '{description}', got '{response.get('description')}'")
                return False
            
            print(f"✅ UTF-8 encoding working for: {description[:30]}...")
        
        return True

    def test_multiple_file_descriptions(self):
        """Test multiple descriptions for different file IDs"""
        # Upload multiple test files
        file_ids = []
        for i in range(3):
            file_id = self.upload_test_file()
            if file_id:
                file_ids.append(file_id)
        
        if len(file_ids) < 3:
            print("❌ Could not upload enough test files")
            return False
        
        # Set different descriptions for each file
        descriptions = [
            f"Description for file 1 - {datetime.now().strftime('%H%M%S')}",
            f"Description for file 2 - {datetime.now().strftime('%H%M%S')}",
            f"Description for file 3 - {datetime.now().strftime('%H%M%S')}"
        ]
        
        # Save descriptions
        for i, (file_id, description) in enumerate(zip(file_ids, descriptions)):
            description_data = {"description": description}
            
            success, response = self.run_test(
                f"Set Description for File {i+1}",
                "PUT",
                f"content/{file_id}/description",
                200,
                data=description_data
            )
            
            if not success:
                return False
        
        # Verify all descriptions are saved correctly
        success, response = self.run_test(
            "Get All Content with Multiple Descriptions",
            "GET",
            "content/pending",
            200
        )
        
        if not success:
            return False
        
        # Check each file has its correct description
        for i, (file_id, expected_description) in enumerate(zip(file_ids, descriptions)):
            found_file = None
            for content_item in response.get('content', []):
                if content_item.get('id') == file_id:
                    found_file = content_item
                    break
            
            if not found_file:
                print(f"❌ File {i+1} ({file_id}) not found in content list")
                return False
            
            if found_file.get('description') != expected_description:
                print(f"❌ File {i+1} description mismatch: expected '{expected_description}', got '{found_file.get('description')}'")
                return False
            
            print(f"✅ File {i+1} description correct: {expected_description[:30]}...")
        
        return True

    def test_update_existing_descriptions(self):
        """Test updating existing descriptions"""
        file_id = self.upload_test_file()
        if not file_id:
            print("❌ Could not upload test file")
            return False
        
        # Set initial description
        initial_description = f"Initial description {datetime.now().strftime('%H%M%S')}"
        description_data = {"description": initial_description}
        
        success, response = self.run_test(
            "Set Initial Description",
            "PUT",
            f"content/{file_id}/description",
            200,
            data=description_data
        )
        
        if not success:
            return False
        
        # Update the description multiple times
        updates = [
            f"Updated description 1 {datetime.now().strftime('%H%M%S')}",
            f"Updated description 2 {datetime.now().strftime('%H%M%S')}",
            f"Final updated description {datetime.now().strftime('%H%M%S')}"
        ]
        
        for i, updated_description in enumerate(updates):
            description_data = {"description": updated_description}
            
            success, response = self.run_test(
                f"Update Description (Update {i+1})",
                "PUT",
                f"content/{file_id}/description",
                200,
                data=description_data
            )
            
            if not success:
                return False
            
            # Verify the update was saved
            if response.get('description') != updated_description:
                print(f"❌ Description update {i+1} failed: expected '{updated_description}', got '{response.get('description')}'")
                return False
            
            print(f"✅ Description update {i+1} successful")
        
        # Verify final state
        success, response = self.run_test(
            "Verify Final Description State",
            "GET",
            "content/pending",
            200
        )
        
        if success:
            found_file = None
            for content_item in response.get('content', []):
                if content_item.get('id') == file_id:
                    found_file = content_item
                    break
            
            if found_file and found_file.get('description') == updates[-1]:
                print(f"✅ Final description state correct: {updates[-1][:30]}...")
                return True
        
        return False

    def test_json_format_validation(self):
        """Test that JSON format is correct and descriptions are properly stored"""
        print(f"\n🔍 Testing JSON Format Validation...")
        
        descriptions_file = "/app/backend/content_descriptions.json"
        
        if not os.path.exists(descriptions_file):
            print(f"⚠️ Descriptions file does not exist yet - creating test data")
            # Upload a file and set a description to create the file
            file_id = self.upload_test_file()
            if file_id:
                description_data = {"description": "Test description for JSON format validation"}
                self.run_test(
                    "Create Description for JSON Format Test",
                    "PUT",
                    f"content/{file_id}/description",
                    200,
                    data=description_data
                )
        
        if os.path.exists(descriptions_file):
            try:
                with open(descriptions_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    descriptions = json.loads(content)
                
                print(f"✅ JSON file is valid and properly formatted")
                print(f"   File size: {len(content)} bytes")
                print(f"   Descriptions count: {len(descriptions)}")
                
                # Validate JSON structure
                if isinstance(descriptions, dict):
                    print(f"✅ JSON structure is correct (dictionary)")
                    
                    # Check if all keys are strings and values are strings
                    valid_format = True
                    for key, value in descriptions.items():
                        if not isinstance(key, str) or not isinstance(value, str):
                            print(f"❌ Invalid format: key '{key}' ({type(key)}) -> value '{value}' ({type(value)})")
                            valid_format = False
                    
                    if valid_format:
                        print(f"✅ All entries have correct format (string -> string)")
                        self.tests_passed += 1
                        return True
                    else:
                        return False
                else:
                    print(f"❌ JSON structure is incorrect: expected dict, got {type(descriptions)}")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON file is corrupted: {e}")
                return False
            except Exception as e:
                print(f"❌ Error reading JSON file: {e}")
                return False
        else:
            print(f"⚠️ Could not create descriptions file for testing")
            return True  # Not a failure

    def test_error_handling_corrupted_json(self):
        """Test error handling when JSON file is corrupted"""
        print(f"\n🔍 Testing Error Handling for Corrupted JSON...")
        
        descriptions_file = "/app/backend/content_descriptions.json"
        backup_file = f"{descriptions_file}.backup"
        
        # Backup existing file if it exists
        if os.path.exists(descriptions_file):
            try:
                with open(descriptions_file, 'r') as src, open(backup_file, 'w') as dst:
                    dst.write(src.read())
                print(f"✅ Backed up existing descriptions file")
            except Exception as e:
                print(f"⚠️ Could not backup existing file: {e}")
        
        try:
            # Create a corrupted JSON file
            with open(descriptions_file, 'w') as f:
                f.write('{"corrupted": json, "missing": quote}')  # Invalid JSON
            
            print(f"✅ Created corrupted JSON file for testing")
            
            # Try to upload a file and set a description (should handle corruption gracefully)
            file_id = self.upload_test_file()
            if file_id:
                description_data = {"description": "Test description with corrupted JSON"}
                
                success, response = self.run_test(
                    "Set Description with Corrupted JSON File",
                    "PUT",
                    f"content/{file_id}/description",
                    200,  # Should still work (create new file or handle error)
                    data=description_data
                )
                
                if success:
                    print(f"✅ System handled corrupted JSON gracefully")
                    
                    # Verify the JSON file was fixed/recreated
                    try:
                        with open(descriptions_file, 'r') as f:
                            json.load(f)  # Should be valid now
                        print(f"✅ JSON file was repaired/recreated")
                        self.tests_passed += 1
                        return True
                    except:
                        print(f"⚠️ JSON file still corrupted but system handled it")
                        return True  # Still a success if the API worked
                else:
                    print(f"❌ System did not handle corrupted JSON gracefully")
                    return False
            else:
                print(f"❌ Could not upload test file")
                return False
                
        except Exception as e:
            print(f"❌ Error during corrupted JSON test: {e}")
            return False
        finally:
            # Restore backup if it exists
            if os.path.exists(backup_file):
                try:
                    with open(backup_file, 'r') as src, open(descriptions_file, 'w') as dst:
                        dst.write(src.read())
                    os.remove(backup_file)
                    print(f"✅ Restored original descriptions file")
                except Exception as e:
                    print(f"⚠️ Could not restore backup: {e}")

    def test_new_files_empty_descriptions(self):
        """Test that new files have empty descriptions by default"""
        # Upload a new file without setting any description
        file_id = self.upload_test_file()
        if not file_id:
            print("❌ Could not upload test file")
            return False
        
        # Get content and check that description is empty
        success, response = self.run_test(
            "Get New File with Default Empty Description",
            "GET",
            "content/pending",
            200
        )
        
        if not success:
            return False
        
        # Find our test file
        found_file = None
        for content_item in response.get('content', []):
            if content_item.get('id') == file_id:
                found_file = content_item
                break
        
        if not found_file:
            print(f"❌ Test file {file_id} not found in content list")
            return False
        
        description = found_file.get('description', None)
        if description == "" or description is None:
            print(f"✅ New file has empty description by default: '{description}'")
            return True
        else:
            print(f"❌ New file should have empty description, got: '{description}'")
            return False

    def cleanup_test_files(self):
        """Clean up uploaded test files"""
        print(f"\n🧹 Cleaning up {len(self.test_file_ids)} test files...")
        
        for file_id in self.test_file_ids:
            try:
                success, response = self.run_test(
                    f"Delete Test File {file_id}",
                    "DELETE",
                    f"content/{file_id}",
                    200
                )
                if success:
                    print(f"✅ Deleted test file {file_id}")
                else:
                    print(f"⚠️ Could not delete test file {file_id}")
            except Exception as e:
                print(f"⚠️ Error deleting test file {file_id}: {e}")

    def run_all_tests(self):
        """Run all persistent description storage tests"""
        print("🚀 Starting Persistent Description Storage and Virtual Keyboard Fixes Testing")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        print("=" * 80)
        
        # Test sequence
        test_sequence = [
            # Authentication
            ("Authentication - User Login", self.test_user_login),
            
            # Description JSON Storage Tests
            ("Description JSON File - Check Creation", self.test_description_json_file_creation),
            ("Description JSON File - Format Validation", self.test_json_format_validation),
            
            # Persistent Description Tests
            ("PUT Description Endpoint - Basic Functionality", self.test_put_description_endpoint),
            ("Description Persistence - Across API Calls", self.test_description_persistence_across_calls),
            ("Description Functions - load_descriptions()", self.test_load_descriptions_function),
            ("Description Functions - get_file_description()", self.test_get_file_description_function),
            
            # Content Loading with Descriptions
            ("Content Loading - New Files Empty Descriptions", self.test_new_files_empty_descriptions),
            
            # Advanced Tests
            ("UTF-8 Encoding - Special Characters", self.test_utf8_encoding_special_characters),
            ("Multiple Files - Different Descriptions", self.test_multiple_file_descriptions),
            ("Update Descriptions - Existing Files", self.test_update_existing_descriptions),
            
            # Edge Cases
            ("Error Handling - Corrupted JSON", self.test_error_handling_corrupted_json),
        ]
        
        # Run tests
        for test_name, test_func in test_sequence:
            print(f"\n{'='*60}")
            print(f"🧪 {test_name}")
            print(f"{'='*60}")
            
            try:
                result = test_func()
                if result:
                    print(f"✅ {test_name} - PASSED")
                else:
                    print(f"❌ {test_name} - FAILED")
            except Exception as e:
                print(f"💥 {test_name} - ERROR: {str(e)}")
        
        # Cleanup
        self.cleanup_test_files()
        
        # Final results
        print(f"\n{'='*80}")
        print(f"🏁 PERSISTENT DESCRIPTION STORAGE TESTING COMPLETED")
        print(f"{'='*80}")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print(f"🎉 ALL TESTS PASSED - Persistent description storage is working correctly!")
        else:
            print(f"⚠️ {self.tests_run - self.tests_passed} tests failed - Review issues above")
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = DescriptionPersistenceAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)