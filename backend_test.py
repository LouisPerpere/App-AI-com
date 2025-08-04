import requests
import sys
import json
import os
from datetime import datetime
import tempfile
from pathlib import Path

class SocialGenieAPITester:
    def __init__(self, base_url="https://4ee22552-91ab-4770-86a9-fcd889c8d854.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.business_id = None
        self.content_id = None
        self.post_id = None
        self.access_token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {}
        
        # Don't set Content-Type for multipart/form-data requests
        if not files:
            headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, data=data, files=files)
                else:
                    response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                if files:
                    response = requests.put(url, data=data, files=files)
                else:
                    response = requests.put(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
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

    def test_create_business_profile(self):
        """Test creating a business profile"""
        profile_data = {
            "business_name": "Restaurant Le Bon Goût",
            "business_type": "restaurant",
            "target_audience": "Familles et jeunes professionnels de 25-45 ans à Lyon, amateurs de cuisine française traditionnelle",
            "brand_tone": "friendly",
            "posting_frequency": "3x_week",
            "preferred_platforms": ["facebook", "instagram", "linkedin"],
            "budget_range": "100-500"
        }
        
        success, response = self.run_test(
            "Create Business Profile",
            "POST",
            "business-profile",
            200,
            data=profile_data
        )
        
        if success and 'id' in response:
            self.business_id = response['id']
            print(f"   Business ID: {self.business_id}")
            return True
        return False

    def test_get_business_profile(self):
        """Test getting a business profile by ID"""
        if not self.business_id:
            print("❌ Skipping - No business ID available")
            return False
            
        success, response = self.run_test(
            "Get Business Profile",
            "GET",
            f"business-profile/{self.business_id}",
            200
        )
        return success

    def test_get_all_business_profiles(self):
        """Test getting all business profiles"""
        success, response = self.run_test(
            "Get All Business Profiles",
            "GET",
            "business-profiles",
            200
        )
        return success

    def test_upload_content(self):
        """Test uploading content with a sample image"""
        if not self.business_id:
            print("❌ Skipping - No business ID available")
            return False

        # Create a simple test image file
        try:
            # Create a temporary image file
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                # Write some dummy image data (minimal JPEG header)
                tmp_file.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9')
                tmp_file_path = tmp_file.name

            with open(tmp_file_path, 'rb') as f:
                files = {'file': ('test_image.jpg', f, 'image/jpeg')}
                data = {'description': 'Plat signature du restaurant - Coq au vin traditionnel avec légumes de saison'}
                
                success, response = self.run_test(
                    "Upload Content",
                    "POST",
                    f"upload-content/{self.business_id}",
                    200,
                    data=data,
                    files=files
                )
                
                if success and 'content_id' in response:
                    self.content_id = response['content_id']
                    print(f"   Content ID: {self.content_id}")
                    
            # Clean up temp file
            os.unlink(tmp_file_path)
            return success
            
        except Exception as e:
            print(f"❌ Error creating test image: {e}")
            return False

    def test_get_generated_posts(self):
        """Test getting generated posts for a business"""
        if not self.business_id:
            print("❌ Skipping - No business ID available")
            return False
            
        success, response = self.run_test(
            "Get Generated Posts",
            "GET",
            f"generated-posts/{self.business_id}",
            200
        )
        
        if success and response and len(response) > 0:
            self.post_id = response[0]['id']
            print(f"   Found {len(response)} generated posts")
            print(f"   First Post ID: {self.post_id}")
        
        return success

    def test_approve_post(self):
        """Test approving a generated post"""
        if not self.post_id:
            print("❌ Skipping - No post ID available")
            return False
            
        success, response = self.run_test(
            "Approve Post",
            "PUT",
            f"post/{self.post_id}/approve",
            200
        )
        return success

    def test_reject_post(self):
        """Test rejecting a generated post (if we have multiple posts)"""
        if not self.business_id:
            print("❌ Skipping - No business ID available")
            return False
            
        # Get posts again to find another post to reject
        try:
            response = requests.get(f"{self.api_url}/generated-posts/{self.business_id}")
            if response.status_code == 200:
                posts = response.json()
                # Find a post that's not approved
                reject_post_id = None
                for post in posts:
                    if post['id'] != self.post_id and post['status'] == 'pending':
                        reject_post_id = post['id']
                        break
                
                if reject_post_id:
                    success, response = self.run_test(
                        "Reject Post",
                        "PUT",
                        f"post/{reject_post_id}/reject",
                        200
                    )
                    return success
                else:
                    print("❌ Skipping - No pending post available to reject")
                    return True  # Not a failure, just no post to reject
            else:
                print("❌ Skipping - Could not fetch posts for rejection test")
                return False
        except Exception as e:
            print(f"❌ Error in reject test: {e}")
            return False

    def test_edit_post(self):
        """Test editing a generated post"""
        if not self.post_id:
            print("❌ Skipping - No post ID available")
            return False
            
        data = {'new_text': 'Texte modifié pour le post - Découvrez notre nouveau plat signature !'}
        success, response = self.run_test(
            "Edit Post",
            "PUT",
            f"post/{self.post_id}/edit",
            200,
            data=data
        )
        return success

    def test_get_calendar(self):
        """Test getting calendar view"""
        if not self.business_id:
            print("❌ Skipping - No business ID available")
            return False
            
        success, response = self.run_test(
            "Get Calendar",
            "GET",
            f"calendar/{self.business_id}",
            200
        )
        return success

def main():
    print("🚀 Starting SocialGénie API Tests")
    print("=" * 50)
    
    tester = SocialGenieAPITester()
    
    # Test sequence
    tests = [
        ("Create Business Profile", tester.test_create_business_profile),
        ("Get Business Profile", tester.test_get_business_profile),
        ("Get All Business Profiles", tester.test_get_all_business_profiles),
        ("Upload Content", tester.test_upload_content),
        ("Get Generated Posts", tester.test_get_generated_posts),
        ("Approve Post", tester.test_approve_post),
        ("Reject Post", tester.test_reject_post),
        ("Edit Post", tester.test_edit_post),
        ("Get Calendar", tester.test_get_calendar),
    ]
    
    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 FINAL RESULTS")
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%" if tester.tests_run > 0 else "0%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())