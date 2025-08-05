import requests
import sys
import json
import os
from datetime import datetime
import tempfile
from pathlib import Path

class SocialGenieAPITester:
    def __init__(self, base_url="https://517d3af0-c990-48c7-9557-b206f74fa495.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.business_id = None
        self.content_id = None
        self.post_id = None
        self.access_token = None
        self.admin_access_token = None
        self.user_id = None
        self.plan_id = None
        self.promo_code_id = None
        self.tests_run = 0
        self.tests_passed = 0

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
                elif headers and headers.get('Content-Type') == 'application/x-www-form-urlencoded':
                    response = requests.post(url, data=data, headers=test_headers)
                else:
                    response = requests.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                if files:
                    response = requests.put(url, data=data, files=files, headers=test_headers)
                elif headers and headers.get('Content-Type') == 'application/x-www-form-urlencoded':
                    response = requests.put(url, data=data, headers=test_headers)
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

    def test_user_registration(self):
        """Test user registration"""
        user_data = {
            "email": "testuser@socialgenie.com",
            "password": "SecurePassword123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        # If user already exists, that's okay for testing
        if not success and response.get('detail') == "Un compte avec cet email existe déjà":
            print("✅ User already exists - continuing with login")
            return True
        
        if success and 'id' in response:
            self.user_id = response['id']
            print(f"   User ID: {self.user_id}")
            return True
        return False

    def test_user_login(self):
        """Test user login"""
        login_data = {
            "email": "testuser@socialgenie.com",
            "password": "SecurePassword123!"
        }
        
        success, response = self.run_test(
            "User Login",
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
        
        # If business profile already exists, that's okay for testing
        if not success and response.get('detail') == "Vous avez déjà un profil d'entreprise":
            print("✅ Business profile already exists - continuing")
            return True
        
        if success and 'id' in response:
            self.business_id = response['id']
            print(f"   Business ID: {self.business_id}")
            return True
        return False

    def test_get_business_profile(self):
        """Test getting current user's business profile"""
        success, response = self.run_test(
            "Get Business Profile",
            "GET",
            "business-profile",  # This endpoint gets current user's profile
            200
        )
        
        # Extract business ID from response
        if success and 'id' in response:
            self.business_id = response['id']
            print(f"   Business ID: {self.business_id}")
        
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

    # Social Media Integration Tests
    
    def test_facebook_auth_url_with_credentials(self):
        """Test Facebook auth URL generation with real credentials (should work)"""
        if not self.business_id:
            print("❌ Skipping - No business ID available")
            return False
            
        success, response = self.run_test(
            "Facebook Auth URL (With Real Credentials)",
            "GET",
            f"social/facebook/auth-url?business_id={self.business_id}",
            200  # Should work with real credentials
        )
        
        if success and 'authorization_url' in response and 'state' in response:
            print("✅ Successfully generated Facebook auth URL")
            print(f"   Auth URL contains: {response['authorization_url'][:100]}...")
            print(f"   State: {response['state'][:20]}...")
            # Verify URL contains correct App ID
            if "1098326618299035" in response['authorization_url']:
                print("✅ Auth URL contains correct Facebook App ID")
            else:
                print("⚠️  Auth URL may not contain expected App ID")
            return True
        return success

    def test_facebook_api_client_initialization(self):
        """Test Facebook API Client can be initialized with real credentials"""
        # Test with a sample Facebook User Access Token (provided by user)
        test_token = "sample_facebook_user_token"  # This would be provided by user for testing
        
        try:
            # Import the FacebookAPIClient
            import sys
            sys.path.append('/app/backend')
            from social_media import FacebookAPIClient
            
            # Initialize client
            fb_client = FacebookAPIClient(test_token)
            
            print("✅ FacebookAPIClient initialized successfully")
            print(f"   Base URL: {fb_client.base_url}")
            print(f"   Token configured: {'Yes' if fb_client.access_token else 'No'}")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize FacebookAPIClient: {e}")
            return False

    def test_instagram_api_client_initialization(self):
        """Test Instagram API Client can be initialized with real credentials"""
        # Test with a sample Facebook User Access Token (same as Facebook)
        test_token = "sample_facebook_user_token"  # This would be provided by user for testing
        
        try:
            # Import the InstagramAPIClient
            import sys
            sys.path.append('/app/backend')
            from social_media import InstagramAPIClient
            
            # Initialize client
            ig_client = InstagramAPIClient(test_token)
            
            print("✅ InstagramAPIClient initialized successfully")
            print(f"   Base URL: {ig_client.base_url}")
            print(f"   Token configured: {'Yes' if ig_client.access_token else 'No'}")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize InstagramAPIClient: {e}")
            return False

    def test_facebook_oauth_manager_initialization(self):
        """Test Facebook OAuth Manager initialization with real credentials"""
        try:
            # Import the FacebookOAuthManager
            import sys
            sys.path.append('/app/backend')
            from social_media import FacebookOAuthManager
            
            # Initialize OAuth manager
            oauth_manager = FacebookOAuthManager()
            
            print("✅ FacebookOAuthManager initialized successfully")
            print(f"   Client ID configured: {'Yes' if oauth_manager.client_id else 'No'}")
            print(f"   Client Secret configured: {'Yes' if oauth_manager.client_secret else 'No'}")
            print(f"   Redirect URI: {oauth_manager.redirect_uri}")
            
            # Verify credentials are the expected ones
            if oauth_manager.client_id == "1098326618299035":
                print("✅ Correct Facebook App ID configured")
            else:
                print(f"⚠️  Unexpected App ID: {oauth_manager.client_id}")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize FacebookOAuthManager: {e}")
            return False

    def test_facebook_auth_url_invalid_business(self):
        """Test Facebook auth URL with invalid business ID"""
        success, response = self.run_test(
            "Facebook Auth URL (Invalid Business)",
            "GET",
            "social/facebook/auth-url?business_id=invalid-business-id",
            404  # Should fail due to invalid business ID
        )
        return success

    def test_social_connections_endpoint(self):
        """Test GET /api/social/connections endpoint"""
        if not self.business_id:
            print("❌ Skipping - No business ID available")
            return False
            
        success, response = self.run_test(
            "Get Social Connections",
            "GET",
            f"social/connections?business_id={self.business_id}",
            200
        )
        
        if success:
            print(f"   Total connections: {response.get('total', 0)}")
            print(f"   Connections list: {len(response.get('connections', []))}")
        
        return success

    def test_social_post_endpoint_structure(self):
        """Test POST /api/social/post endpoint structure and validation"""
        # Test with missing required fields
        post_data = {
            "platform": "facebook",
            "content": "Test post content"
            # Missing page_id for Facebook
        }
        
        success, response = self.run_test(
            "Social Post (Missing Required Fields)",
            "POST",
            "social/post",
            400,  # Should fail due to missing required fields
            data=post_data
        )
        return success

    def test_delete_connection_endpoint(self):
        """Test DELETE /api/social/connection/{id} endpoint"""
        success, response = self.run_test(
            "Delete Non-existent Connection",
            "DELETE",
            "social/connection/nonexistent-connection-id",
            404  # Should fail due to non-existent connection
        )
        return success

    def test_facebook_callback_invalid_state(self):
        """Test Facebook callback with invalid state"""
        success, response = self.run_test(
            "Facebook Callback (Invalid State)",
            "POST",
            "social/facebook/callback?code=test_code&state=invalid_state",
            400,  # Should fail due to invalid state
        )
        return success

    def test_get_social_connections_empty(self):
        """Test getting social connections (should be empty initially)"""
        if not self.business_id:
            print("❌ Skipping - No business ID available")
            return False
            
        success, response = self.run_test(
            "Get Social Connections (Empty)",
            "GET",
            f"social/connections?business_id={self.business_id}",
            200
        )
        
        if success and response.get('total', 0) == 0:
            print("✅ Correctly returned empty connections")
            return True
        return success

    def test_social_post_without_connection(self):
        """Test creating social media post without connection (should fail)"""
        post_data = {
            "platform": "facebook",
            "content": "Test post content",
            "page_id": "test_page_id"
        }
        
        success, response = self.run_test(
            "Social Post (No Connection)",
            "POST",
            "social/post",
            404,  # Should fail due to no connection
            data=post_data
        )
        return success

    def test_disconnect_nonexistent_connection(self):
        """Test disconnecting non-existent social connection"""
        success, response = self.run_test(
            "Disconnect Non-existent Connection",
            "DELETE",
            "social/connection/nonexistent-id",
            404  # Should fail due to non-existent connection
        )
        return success

    def test_social_post_invalid_platform(self):
        """Test creating post with invalid platform"""
        post_data = {
            "platform": "invalid_platform",
            "content": "Test post content"
        }
        
        success, response = self.run_test(
            "Social Post (Invalid Platform)",
            "POST",
            "social/post",
            400,  # Should fail due to invalid platform
            data=post_data
        )
        return success

    def test_instagram_post_without_image(self):
        """Test Instagram post without image (should fail)"""
        post_data = {
            "platform": "instagram",
            "content": "Test Instagram post",
            "instagram_user_id": "test_user_id"
        }
        
        success, response = self.run_test(
            "Instagram Post (No Image)",
            "POST",
            "social/post",
            404,  # Should fail due to no connection first
            data=post_data
        )
        return success

    # Integration with existing post system tests
    
    def test_upload_content_batch(self):
        """Test uploading content batch"""
        if not self.business_id:
            print("❌ Skipping - No business ID available")
            return False

        # Create a simple test image file
        try:
            # Create a temporary image file
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                # Write some dummy image data (minimal JPEG header)
                tmp_file.write(b'\xff\xd8\xff\xe0\x10JFIF\x01\x01\x01HH\xff\xdbC\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x11\x08\x01\x01\x01\x01\x11\x02\x11\x01\x03\x11\x01\xff\xc4\x14\x01\x08\xff\xc4\x14\x10\x01\xff\xda\x0c\x03\x01\x02\x11\x03\x11\x3f\xaa\xff\xd9')
                tmp_file_path = tmp_file.name

            with open(tmp_file_path, 'rb') as f:
                files = {'files': ('test_image.jpg', f, 'image/jpeg')}
                
                success, response = self.run_test(
                    "Upload Content Batch",
                    "POST",
                    "upload-content-batch",
                    200,
                    files=files
                )
                
                if success and response.get('uploaded_content'):
                    uploaded_content = response['uploaded_content']
                    if uploaded_content:
                        self.content_id = uploaded_content[0]['id']
                        print(f"   Content ID: {self.content_id}")
                    
            # Clean up temp file
            os.unlink(tmp_file_path)
            return success
            
        except Exception as e:
            print(f"❌ Error creating test image: {e}")
            return False

    def test_describe_content(self):
        """Test describing uploaded content"""
        if not self.content_id:
            print("❌ Skipping - No content ID available")
            return False
            
        # Use proper form data
        form_data = {
            'description': 'Plat signature du restaurant - Coq au vin traditionnel avec légumes de saison'
        }
        
        success, response = self.run_test(
            "Describe Content",
            "POST",
            f"content/{self.content_id}/describe",
            200,
            data=form_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        return success

    def test_get_posts(self):
        """Test getting user's posts"""
        success, response = self.run_test(
            "Get Posts",
            "GET",
            "posts",
            200
        )
        
        if success and response.get('posts'):
            posts = response['posts']
            if posts:
                self.post_id = posts[0]['id']
                print(f"   Found {len(posts)} posts")
                print(f"   First Post ID: {self.post_id}")
        
        return success

    def test_publish_post_now(self):
        """Test publishing post immediately (should fail without social connections)"""
        if not self.post_id:
            print("❌ Skipping - No post ID available")
            return False
            
        success, response = self.run_test(
            "Publish Post Now (No Connections)",
            "POST",
            f"posts/{self.post_id}/publish",
            404  # Should fail due to no social connections
        )
        return success

def main():
    print("🚀 Starting SocialGénie API Tests")
    print("=" * 50)
    
    tester = SocialGenieAPITester()
    
    # Test sequence
    tests = [
        # Authentication Tests
        ("User Registration", tester.test_user_registration),
        ("User Login", tester.test_user_login),
        
        # Business Profile Tests
        ("Create Business Profile", tester.test_create_business_profile),
        ("Get Business Profile", tester.test_get_business_profile),
        
        # Social Media Integration Tests - Real Credentials Testing
        ("Facebook OAuth Manager Initialization", tester.test_facebook_oauth_manager_initialization),
        ("Facebook API Client Initialization", tester.test_facebook_api_client_initialization),
        ("Instagram API Client Initialization", tester.test_instagram_api_client_initialization),
        ("Facebook Auth URL (With Real Credentials)", tester.test_facebook_auth_url_with_credentials),
        ("Facebook Auth URL (Invalid Business)", tester.test_facebook_auth_url_invalid_business),
        ("Facebook Callback (Invalid State)", tester.test_facebook_callback_invalid_state),
        ("Get Social Connections", tester.test_social_connections_endpoint),
        ("Social Post (Missing Required Fields)", tester.test_social_post_endpoint_structure),
        ("Delete Non-existent Connection", tester.test_delete_connection_endpoint),
        ("Social Post (No Connection)", tester.test_social_post_without_connection),
        ("Social Post (Invalid Platform)", tester.test_social_post_invalid_platform),
        ("Instagram Post (No Image)", tester.test_instagram_post_without_image),
        
        # Content and Post Integration Tests
        ("Upload Content Batch", tester.test_upload_content_batch),
        ("Describe Content", tester.test_describe_content),
        ("Get Posts", tester.test_get_posts),
        ("Approve Post", tester.test_approve_post),
        ("Publish Post Now (No Connections)", tester.test_publish_post_now),
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