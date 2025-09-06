#!/usr/bin/env python3
"""
UPLOAD DATA PERSISTENCE TESTING
Critical issue: User fills title and context during upload preview but data is not visible in library after upload.

Test Requirements:
1. Content Listing Analysis - GET /api/content/pending 
2. Upload Flow Testing - POST /api/content/batch-upload endpoint  
3. Update API Testing - PUT /api/content/{id}/title and PUT /api/content/{id}/context
4. Data Persistence Verification

Credentials: lperpere@yahoo.fr / L@Reunion974!
Backend URL: https://media-title-fix.preview.emergentagent.com/api
"""

import requests
import json
import sys
from datetime import datetime
import io
from PIL import Image

# Configuration
BASE_URL = "https://media-title-fix.preview.emergentagent.com/api"
EMAIL = "lperpere@yahoo.fr"
PASSWORD = "L@Reunion974!"

class UploadDataPersistenceTest:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        
    def authenticate(self):
        """Step 1: Authenticate with provided credentials"""
        print("🔐 Step 1: Authentication")
        
        auth_data = {
            "email": EMAIL,
            "password": PASSWORD
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/auth/login-robust", json=auth_data)
            print(f"Auth response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for all future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                })
                
                print(f"✅ Authentication successful")
                print(f"   User ID: {self.user_id}")
                print(f"   Token: {self.token[:20]}..." if self.token else "No token")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def analyze_content_listing(self):
        """Step 2: Content Listing Analysis - Check existing uploads for empty title/context"""
        print("\n📋 Step 2: Content Listing Analysis")
        
        try:
            response = self.session.get(f"{BASE_URL}/content/pending")
            print(f"Content listing response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                total_items = data.get("total", 0)
                
                print(f"✅ Content listing successful")
                print(f"   Total items: {total_items}")
                print(f"   Items loaded: {len(content_items)}")
                
                # Analyze title/context fields
                items_with_title = 0
                items_with_context = 0
                items_with_empty_title = 0
                items_with_empty_context = 0
                
                print(f"\n📊 Title/Context Analysis:")
                for i, item in enumerate(content_items[:5]):  # Check first 5 items
                    item_id = item.get("id", "unknown")
                    title = item.get("title", "")
                    context = item.get("context", "")
                    filename = item.get("filename", "")
                    
                    print(f"   Item {i+1} (ID: {item_id[:8]}...):")
                    print(f"     Filename: {filename}")
                    print(f"     Title: '{title}' {'(EMPTY)' if not title else '(HAS DATA)'}")
                    print(f"     Context: '{context}' {'(EMPTY)' if not context else '(HAS DATA)'}")
                    
                    if title:
                        items_with_title += 1
                    else:
                        items_with_empty_title += 1
                        
                    if context:
                        items_with_context += 1
                    else:
                        items_with_empty_context += 1
                
                print(f"\n📈 Summary:")
                print(f"   Items with title: {items_with_title}")
                print(f"   Items with empty title: {items_with_empty_title}")
                print(f"   Items with context: {items_with_context}")
                print(f"   Items with empty context: {items_with_empty_context}")
                
                return content_items
            else:
                print(f"❌ Content listing failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Content listing error: {e}")
            return []
    
    def test_batch_upload_flow(self):
        """Step 3: Upload Flow Testing - Test batch upload endpoint"""
        print("\n📤 Step 3: Upload Flow Testing")
        
        try:
            # Create a test image in memory
            img = Image.new('RGB', (100, 100), color='red')
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            # Prepare multipart form data
            files = {
                'files': ('test_upload_persistence.png', img_buffer, 'image/png')
            }
            
            # Remove Content-Type header for multipart upload
            headers = {"Authorization": f"Bearer {self.token}"}
            
            response = self.session.post(f"{BASE_URL}/content/batch-upload", files=files, headers=headers)
            print(f"Batch upload response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                uploaded_files = data.get("uploaded_files", [])
                
                print(f"✅ Batch upload successful")
                print(f"   Files uploaded: {len(uploaded_files)}")
                
                if uploaded_files:
                    first_file = uploaded_files[0]
                    file_id = first_file.get("id")
                    filename = first_file.get("filename")
                    title = first_file.get("title", "")
                    context = first_file.get("context", "")
                    
                    print(f"   First uploaded file:")
                    print(f"     ID: {file_id}")
                    print(f"     Filename: {filename}")
                    print(f"     Title in response: '{title}' {'(EMPTY)' if not title else '(HAS DATA)'}")
                    print(f"     Context in response: '{context}' {'(EMPTY)' if not context else '(HAS DATA)'}")
                    
                    return file_id
                else:
                    print(f"❌ No files in upload response")
                    return None
            else:
                print(f"❌ Batch upload failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Batch upload error: {e}")
            return None
    
    def test_title_update_api(self, content_id):
        """Step 4: Update API Testing - Test title update endpoint"""
        print(f"\n✏️ Step 4: Title Update API Testing")
        
        if not content_id:
            print("❌ No content ID provided for title update test")
            return False
            
        test_title = "Modèle 39mm sur mesure - Test Title"
        
        try:
            update_data = {"title": test_title}
            response = self.session.put(f"{BASE_URL}/content/{content_id}/title", json=update_data)
            print(f"Title update response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                
                print(f"✅ Title update successful")
                print(f"   Response message: {message}")
                print(f"   Test title: '{test_title}'")
                return True
            else:
                print(f"❌ Title update failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Title update error: {e}")
            return False
    
    def test_context_update_api(self, content_id):
        """Step 5: Context Update API Testing - Test context update endpoint"""
        print(f"\n📝 Step 5: Context Update API Testing")
        
        if not content_id:
            print("❌ No content ID provided for context update test")
            return False
            
        test_context = "Description détaillée du modèle avec mots-clés pour génération de contenu"
        
        try:
            update_data = {"context": test_context}
            response = self.session.put(f"{BASE_URL}/content/{content_id}/context", json=update_data)
            print(f"Context update response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                
                print(f"✅ Context update successful")
                print(f"   Response message: {message}")
                print(f"   Test context: '{test_context}'")
                return True
            else:
                print(f"❌ Context update failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Context update error: {e}")
            return False
    
    def verify_data_persistence(self, content_id):
        """Step 6: Data Persistence Verification - Check if updates persist"""
        print(f"\n🔍 Step 6: Data Persistence Verification")
        
        if not content_id:
            print("❌ No content ID provided for persistence verification")
            return False
            
        try:
            response = self.session.get(f"{BASE_URL}/content/pending")
            print(f"Persistence check response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                
                # Find our test content
                test_item = None
                for item in content_items:
                    if item.get("id") == content_id:
                        test_item = item
                        break
                
                if test_item:
                    title = test_item.get("title", "")
                    context = test_item.get("context", "")
                    filename = test_item.get("filename", "")
                    
                    print(f"✅ Test content found in listing")
                    print(f"   ID: {content_id}")
                    print(f"   Filename: {filename}")
                    print(f"   Persisted title: '{title}'")
                    print(f"   Persisted context: '{context}'")
                    
                    # Check if our test data persisted
                    title_persisted = "Modèle 39mm sur mesure" in title
                    context_persisted = "Description détaillée" in context
                    
                    print(f"\n📊 Persistence Results:")
                    print(f"   Title persisted correctly: {'✅ YES' if title_persisted else '❌ NO'}")
                    print(f"   Context persisted correctly: {'✅ YES' if context_persisted else '❌ NO'}")
                    
                    return title_persisted and context_persisted
                else:
                    print(f"❌ Test content not found in listing")
                    return False
            else:
                print(f"❌ Persistence check failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Persistence check error: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run the complete upload data persistence test"""
        print("🎯 UPLOAD DATA PERSISTENCE TESTING")
        print("=" * 60)
        print(f"Backend URL: {BASE_URL}")
        print(f"Test User: {EMAIL}")
        print(f"Issue: Upload data not persisting after batch upload")
        print("=" * 60)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with testing")
            return False
        
        # Step 2: Content Listing Analysis
        existing_content = self.analyze_content_listing()
        
        # Step 3: Upload Flow Testing
        uploaded_content_id = self.test_batch_upload_flow()
        
        # Step 4: Update API Testing
        title_update_success = self.test_title_update_api(uploaded_content_id)
        
        # Step 5: Context Update API Testing  
        context_update_success = self.test_context_update_api(uploaded_content_id)
        
        # Step 6: Data Persistence Verification
        persistence_success = self.verify_data_persistence(uploaded_content_id)
        
        # Final Results
        print("\n" + "=" * 60)
        print("🎯 FINAL TEST RESULTS")
        print("=" * 60)
        
        tests_passed = 0
        total_tests = 6
        
        print(f"✅ Step 1: Authentication - {'PASS' if self.token else 'FAIL'}")
        if self.token: tests_passed += 1
        
        print(f"✅ Step 2: Content Listing - {'PASS' if existing_content else 'FAIL'}")
        if existing_content: tests_passed += 1
        
        print(f"✅ Step 3: Batch Upload - {'PASS' if uploaded_content_id else 'FAIL'}")
        if uploaded_content_id: tests_passed += 1
        
        print(f"✅ Step 4: Title Update API - {'PASS' if title_update_success else 'FAIL'}")
        if title_update_success: tests_passed += 1
        
        print(f"✅ Step 5: Context Update API - {'PASS' if context_update_success else 'FAIL'}")
        if context_update_success: tests_passed += 1
        
        print(f"✅ Step 6: Data Persistence - {'PASS' if persistence_success else 'FAIL'}")
        if persistence_success: tests_passed += 1
        
        success_rate = (tests_passed / total_tests) * 100
        print(f"\n📊 SUCCESS RATE: {tests_passed}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        if success_rate == 100:
            print("🎉 ALL TESTS PASSED - Upload data persistence is working correctly")
        elif success_rate >= 80:
            print("⚠️ MOSTLY WORKING - Minor issues detected")
        else:
            print("🚨 CRITICAL ISSUES - Upload data persistence has significant problems")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = UploadDataPersistenceTest()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)