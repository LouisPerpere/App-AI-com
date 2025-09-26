#!/usr/bin/env python3
"""
DIAGNOSTIC UPLOAD BIBLIOTHÈQUE - Backend Testing
Test script to investigate the upload functionality issue reported by user.
"""

import requests
import json
import tempfile
import os
from datetime import datetime

class UploadDiagnosticTester:
    def __init__(self):
        # Use the production backend URL from frontend/.env
        self.base_url = "https://social-ai-planner-2.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.tests_run = 0
        self.tests_passed = 0

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name}")
        
        if details:
            print(f"   {details}")

    def test_authentication(self):
        """Test authentication with specified credentials"""
        print("\n🔐 TESTING AUTHENTICATION")
        print("-" * 50)
        
        login_data = {
            "email": "lperpere@yahoo.fr",
            "password": "L@Reunion974!"
        }
        
        try:
            response = requests.post(f"{self.api_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data:
                    self.access_token = data['access_token']
                    self.log_test("User Authentication", True, f"Token obtained: {self.access_token[:20]}...")
                    return True
                else:
                    self.log_test("User Authentication", False, "No access token in response")
                    return False
            else:
                self.log_test("User Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Authentication", False, f"Error: {str(e)}")
            return False

    def test_backend_endpoints_discovery(self):
        """Discover available backend endpoints"""
        print("\n🔍 DISCOVERING BACKEND ENDPOINTS")
        print("-" * 50)
        
        # Test various endpoint patterns
        endpoints_to_test = [
            # Current endpoints from server.py
            "/api/bibliotheque",
            "/api/content/batch-upload",  # The one frontend is calling
            "/api/upload-content",
            "/api/content/upload",
            "/api/files/upload",
            "/api/media/upload",
            # Check if there are any upload-related endpoints
        ]
        
        headers = {}
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        available_endpoints = []
        
        for endpoint in endpoints_to_test:
            try:
                # Try GET first
                response = requests.get(f"{self.base_url}{endpoint}", headers=headers)
                if response.status_code != 404:
                    available_endpoints.append((endpoint, "GET", response.status_code))
                    self.log_test(f"Endpoint Discovery - GET {endpoint}", True, f"Status: {response.status_code}")
                
                # Try POST for upload endpoints
                if "upload" in endpoint or "bibliotheque" in endpoint:
                    response = requests.post(f"{self.base_url}{endpoint}", headers=headers, json={})
                    if response.status_code != 404:
                        available_endpoints.append((endpoint, "POST", response.status_code))
                        self.log_test(f"Endpoint Discovery - POST {endpoint}", True, f"Status: {response.status_code}")
                    else:
                        self.log_test(f"Endpoint Discovery - POST {endpoint}", False, "404 Not Found")
                        
            except Exception as e:
                self.log_test(f"Endpoint Discovery - {endpoint}", False, f"Error: {str(e)}")
        
        print(f"\n📋 AVAILABLE ENDPOINTS SUMMARY:")
        for endpoint, method, status in available_endpoints:
            print(f"   {method} {endpoint} -> {status}")
        
        return len(available_endpoints) > 0

    def test_bibliotheque_endpoints(self):
        """Test existing bibliotheque endpoints"""
        print("\n📚 TESTING BIBLIOTHEQUE ENDPOINTS")
        print("-" * 50)
        
        headers = {}
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        # Test GET /api/bibliotheque
        try:
            response = requests.get(f"{self.api_url}/bibliotheque", headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.log_test("GET /api/bibliotheque", True, f"Response: {json.dumps(data, indent=2)}")
            else:
                self.log_test("GET /api/bibliotheque", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("GET /api/bibliotheque", False, f"Error: {str(e)}")
        
        # Test POST /api/bibliotheque
        try:
            test_data = {
                "name": "test-upload.jpg",
                "type": "image/jpeg",
                "size": "1024"
            }
            response = requests.post(f"{self.api_url}/bibliotheque", json=test_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.log_test("POST /api/bibliotheque", True, f"Response: {json.dumps(data, indent=2)}")
            else:
                self.log_test("POST /api/bibliotheque", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("POST /api/bibliotheque", False, f"Error: {str(e)}")

    def test_batch_upload_endpoint(self):
        """Test the specific endpoint that frontend is calling"""
        print("\n📤 TESTING BATCH UPLOAD ENDPOINT")
        print("-" * 50)
        
        headers = {}
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        # Test if /api/content/batch-upload exists
        try:
            # First try with GET to see if endpoint exists
            response = requests.get(f"{self.api_url}/content/batch-upload", headers=headers)
            self.log_test("GET /api/content/batch-upload", response.status_code != 404, 
                         f"Status: {response.status_code}, Response: {response.text[:200]}")
            
            # Try POST with empty data
            response = requests.post(f"{self.api_url}/content/batch-upload", headers=headers, json={})
            self.log_test("POST /api/content/batch-upload (empty)", response.status_code != 404, 
                         f"Status: {response.status_code}, Response: {response.text[:200]}")
            
            # Try POST with multipart form data (as frontend would send)
            self.test_multipart_upload()
            
        except Exception as e:
            self.log_test("Batch Upload Endpoint Test", False, f"Error: {str(e)}")

    def test_multipart_upload(self):
        """Test multipart file upload as frontend would do"""
        print("\n📁 TESTING MULTIPART FILE UPLOAD")
        print("-" * 50)
        
        headers = {}
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        # Create a test image file
        try:
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                # Write minimal JPEG header
                tmp_file.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9')
                tmp_file_path = tmp_file.name

            # Test upload to different endpoints
            endpoints_to_test = [
                "/api/content/batch-upload",
                "/api/bibliotheque",
                "/api/upload-content",
                "/api/content/upload"
            ]
            
            for endpoint in endpoints_to_test:
                try:
                    with open(tmp_file_path, 'rb') as f:
                        files = {'files': ('test_image.jpg', f, 'image/jpeg')}
                        
                        # Don't set Content-Type header for multipart
                        upload_headers = headers.copy()
                        
                        response = requests.post(f"{self.base_url}{endpoint}", 
                                               files=files, 
                                               headers=upload_headers)
                        
                        if response.status_code == 404:
                            self.log_test(f"Multipart Upload - {endpoint}", False, "Endpoint not found (404)")
                        elif response.status_code in [200, 201]:
                            self.log_test(f"Multipart Upload - {endpoint}", True, 
                                         f"Success! Status: {response.status_code}, Response: {response.text[:200]}")
                        else:
                            self.log_test(f"Multipart Upload - {endpoint}", False, 
                                         f"Status: {response.status_code}, Response: {response.text[:200]}")
                            
                except Exception as e:
                    self.log_test(f"Multipart Upload - {endpoint}", False, f"Error: {str(e)}")
            
            # Clean up
            os.unlink(tmp_file_path)
            
        except Exception as e:
            self.log_test("Multipart Upload Test", False, f"Error creating test file: {str(e)}")

    def test_server_routes_inspection(self):
        """Inspect server routes to understand what's available"""
        print("\n🔍 SERVER ROUTES INSPECTION")
        print("-" * 50)
        
        # Test the root endpoint to see available routes
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Root Endpoint", True, f"Available endpoints: {json.dumps(data.get('endpoints', {}), indent=2)}")
            else:
                self.log_test("Root Endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Error: {str(e)}")
        
        # Test health endpoint
        try:
            response = requests.get(f"{self.api_url}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Endpoint", True, f"Service: {data.get('service', 'Unknown')}")
            else:
                self.log_test("Health Endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Health Endpoint", False, f"Error: {str(e)}")

    def test_content_endpoints_variations(self):
        """Test various content endpoint variations"""
        print("\n📋 TESTING CONTENT ENDPOINT VARIATIONS")
        print("-" * 50)
        
        headers = {}
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        # Test different content endpoint patterns
        content_endpoints = [
            "/api/content",
            "/api/content/",
            "/api/content/upload",
            "/api/content/batch-upload",
            "/api/content/files",
            "/api/upload",
            "/api/files",
            "/api/media"
        ]
        
        for endpoint in content_endpoints:
            try:
                # Test GET
                response = requests.get(f"{self.base_url}{endpoint}", headers=headers)
                if response.status_code != 404:
                    self.log_test(f"Content Endpoint GET {endpoint}", True, f"Status: {response.status_code}")
                else:
                    self.log_test(f"Content Endpoint GET {endpoint}", False, "404 Not Found")
                
                # Test POST
                response = requests.post(f"{self.base_url}{endpoint}", headers=headers, json={})
                if response.status_code != 404:
                    self.log_test(f"Content Endpoint POST {endpoint}", True, f"Status: {response.status_code}")
                else:
                    self.log_test(f"Content Endpoint POST {endpoint}", False, "404 Not Found")
                    
            except Exception as e:
                self.log_test(f"Content Endpoint {endpoint}", False, f"Error: {str(e)}")

    def run_diagnostic(self):
        """Run complete diagnostic"""
        print("🚀 DIAGNOSTIC UPLOAD BIBLIOTHÈQUE - BACKEND TESTING")
        print("=" * 70)
        print(f"Backend URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 70)
        
        # Run all tests
        self.test_authentication()
        self.test_server_routes_inspection()
        self.test_backend_endpoints_discovery()
        self.test_bibliotheque_endpoints()
        self.test_content_endpoints_variations()
        self.test_batch_upload_endpoint()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 DIAGNOSTIC SUMMARY")
        print("=" * 70)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        # Conclusions
        print("\n🎯 DIAGNOSTIC CONCLUSIONS:")
        print("-" * 30)
        
        if self.access_token:
            print("✅ Authentication working with lperpere@yahoo.fr / L@Reunion974!")
        else:
            print("❌ Authentication failed - cannot test protected endpoints")
        
        print("\n📋 RECOMMENDATIONS:")
        print("-" * 20)
        print("1. Check if /api/content/batch-upload endpoint exists in backend")
        print("2. If not, implement the missing endpoint or update frontend to use existing /api/bibliotheque")
        print("3. Verify multipart/form-data handling in backend")
        print("4. Check file upload permissions and storage configuration")
        
        return self.tests_passed / self.tests_run if self.tests_run > 0 else 0

if __name__ == "__main__":
    tester = UploadDiagnosticTester()
    success_rate = tester.run_diagnostic()
    
    if success_rate < 0.5:
        exit(1)  # Exit with error if less than 50% tests pass
    else:
        exit(0)  # Exit successfully