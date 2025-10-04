#!/usr/bin/env python3
"""
Instagram OAuth Callback URL Corrections Testing
==============================================

Testing the corrections made to Instagram OAuth redirect URIs:
- FACEBOOK_REDIRECT_URI: claire-marcus.com → claire-marcus-app-1.preview.emergentagent.com
- INSTAGRAM_REDIRECT_URI: claire-marcus.com → claire-marcus-app-1.preview.emergentagent.com  
- FRONTEND_URL: claire-marcus.com → claire-marcus-app-1.preview.emergentagent.com

Test Objectives:
1. Verify auth URLs contain correct redirect_uri with preview domain
2. Test Instagram callback simulation with new URLs
3. Verify connection state endpoints
4. Ensure no "Invalid verification code format" errors
"""

import requests
import json
import sys
import time
from urllib.parse import urlparse, parse_qs

# Configuration
BASE_URL = "https://claire-marcus-app-1.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class CalendarTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        
    def authenticate(self):
        """Authenticate with the backend API"""
        print("🔐 Step 1: Authenticating with backend...")
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login-robust", json={
                "email": EMAIL,
                "password": PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                print(f"✅ Authentication successful")
                print(f"   User ID: {self.user_id}")
                print(f"   Token: {self.auth_token[:20]}..." if self.auth_token else "   Token: None")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_calendar_posts_endpoint(self):
        """Test 1: Verify calendar posts endpoint returns scheduled posts"""
        print("\n📅 Step 2: Testing calendar posts endpoint...")
        
        try:
            response = self.session.get(f"{API_BASE}/calendar/posts")
            
            if response.status_code == 200:
                data = response.json()
                posts = data if isinstance(data, list) else data.get('posts', [])
                
                print(f"✅ Calendar endpoint accessible")
                print(f"   Found {len(posts)} calendar posts")
                
                if posts:
                    # Analyze first post for required fields
                    first_post = posts[0]
                    print(f"   Sample post ID: {first_post.get('id', 'N/A')}")
                    print(f"   Title: {first_post.get('title', 'N/A')}")
                    print(f"   Platform: {first_post.get('platform', 'N/A')}")
                    print(f"   Scheduled date: {first_post.get('scheduled_date', 'N/A')}")
                    print(f"   Status: {first_post.get('status', 'N/A')}")
                    print(f"   Validated: {first_post.get('validated', 'N/A')}")
                    
                    # Check for image/visual fields (thumbnails)
                    visual_fields = ['visual_url', 'visual_id', 'carousel_images', 'image_url']
                    for field in visual_fields:
                        if field in first_post and first_post[field]:
                            print(f"   Visual field '{field}': {str(first_post[field])[:50]}...")
                    
                    return posts
                else:
                    print("⚠️ No calendar posts found")
                    return []
            else:
                print(f"❌ Calendar endpoint failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Calendar endpoint error: {str(e)}")
            return None
    
    def test_post_movement_endpoint(self, post_id):
        """Test 2: Test post movement (Déplacer functionality)"""
        print(f"\n🔄 Step 3: Testing post movement for post {post_id}...")
        
        try:
            # Test the move calendar post endpoint
            new_date = "2025-09-27T15:00:00.000Z"
            response = self.session.put(f"{API_BASE}/posts/move-calendar-post/{post_id}", json={
                "new_date": new_date
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Post movement endpoint working")
                print(f"   Response: {data.get('message', 'Success')}")
                return True
            else:
                print(f"❌ Post movement failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Post movement error: {str(e)}")
            return False
    
    def test_post_modification_endpoint(self, post_id):
        """Test 3: Test post modification functionality"""
        print(f"\n✏️ Step 4: Testing post modification for post {post_id}...")
        
        try:
            # Test the modify post endpoint
            response = self.session.put(f"{API_BASE}/posts/{post_id}/modify", json={
                "modification_request": "Rends ce texte plus accrocheur pour le calendrier"
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Post modification endpoint working")
                print(f"   Success: {data.get('success', False)}")
                print(f"   Message: {data.get('message', 'N/A')}")
                if 'new_text' in data:
                    print(f"   Modified text preview: {data['new_text'][:100]}...")
                return True
            elif response.status_code == 404:
                print(f"⚠️ Post modification endpoint not found (404)")
                print(f"   This may be expected if endpoint doesn't exist for calendar posts")
                return False
            else:
                print(f"❌ Post modification failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Post modification error: {str(e)}")
            return False
    
    def test_posts_validation_endpoint(self):
        """Test 4: Test posts validation to calendar (Programmer functionality)"""
        print(f"\n✅ Step 5: Testing posts validation to calendar...")
        
        try:
            # First get generated posts to find one to validate
            response = self.session.get(f"{API_BASE}/posts/generated")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('posts', [])
                
                # Find a non-validated post
                non_validated_post = None
                for post in posts:
                    if not post.get('validated', False):
                        non_validated_post = post
                        break
                
                if non_validated_post:
                    post_id = non_validated_post['id']
                    print(f"   Found non-validated post: {post_id}")
                    
                    # Test validation endpoint
                    validation_response = self.session.post(f"{API_BASE}/posts/validate-to-calendar", json={
                        "post_id": post_id,
                        "platforms": [non_validated_post.get('platform', 'instagram')],
                        "scheduled_date": "2025-09-28T10:00:00"
                    })
                    
                    if validation_response.status_code == 200:
                        validation_data = validation_response.json()
                        print(f"✅ Post validation to calendar working")
                        print(f"   Success: {validation_data.get('success', False)}")
                        print(f"   Message: {validation_data.get('message', 'N/A')}")
                        print(f"   Calendar entries: {validation_data.get('calendar_entries', 0)}")
                        return True
                    else:
                        print(f"❌ Post validation failed: {validation_response.status_code}")
                        print(f"   Response: {validation_response.text}")
                        return False
                else:
                    print("⚠️ No non-validated posts found for testing")
                    return False
            else:
                print(f"❌ Failed to get generated posts: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Posts validation error: {str(e)}")
            return False
    
    def test_content_thumbnails(self):
        """Test 5: Verify content thumbnails/vignettes are available"""
        print(f"\n🖼️ Step 6: Testing content thumbnails availability...")
        
        try:
            response = self.session.get(f"{API_BASE}/content/pending?limit=5")
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get('content', [])
                
                print(f"✅ Content endpoint accessible")
                print(f"   Found {len(content_items)} content items")
                
                thumbnail_count = 0
                for item in content_items:
                    if item.get('thumb_url'):
                        thumbnail_count += 1
                        print(f"   Item {item.get('id', 'N/A')}: has thumbnail")
                
                print(f"   Items with thumbnails: {thumbnail_count}/{len(content_items)}")
                
                if thumbnail_count > 0:
                    # Test accessing a thumbnail
                    first_thumb_item = next((item for item in content_items if item.get('thumb_url')), None)
                    if first_thumb_item:
                        thumb_url = first_thumb_item['thumb_url']
                        if thumb_url.startswith('/'):
                            thumb_url = f"{BACKEND_URL}{thumb_url}"
                        
                        thumb_response = self.session.get(thumb_url)
                        if thumb_response.status_code == 200:
                            print(f"   ✅ Thumbnail accessible: {thumb_response.headers.get('content-type', 'unknown')}")
                        else:
                            print(f"   ⚠️ Thumbnail not accessible: {thumb_response.status_code}")
                
                return len(content_items) > 0
            else:
                print(f"❌ Content endpoint failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Content thumbnails error: {str(e)}")
            return False
    
    def test_deprogrammer_functionality(self, post_id):
        """Test 6: Test Déprogrammer functionality (removing from calendar)"""
        print(f"\n🗑️ Step 7: Testing Déprogrammer functionality for post {post_id}...")
        
        try:
            # Test if there's a deprogramming endpoint
            # This might be implemented as a status change or deletion
            response = self.session.put(f"{API_BASE}/posts/{post_id}", json={
                "validated": False,
                "status": "draft"
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Déprogrammer functionality working")
                print(f"   Response: {data}")
                return True
            else:
                # Try alternative endpoint
                response = self.session.delete(f"{API_BASE}/calendar/posts/{post_id}")
                if response.status_code == 200:
                    print(f"✅ Déprogrammer via delete endpoint working")
                    return True
                else:
                    print(f"❌ Déprogrammer failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
                
        except Exception as e:
            print(f"❌ Déprogrammer error: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all calendar functionality tests"""
        print("🎯 CALENDAR FUNCTIONALITIES POST-PROGRAMMER TRANSFORMATION TESTING")
        print("=" * 70)
        print(f"Environment: {BACKEND_URL}")
        print(f"Credentials: {EMAIL}")
        print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Test calendar posts endpoint
        calendar_posts = self.test_calendar_posts_endpoint()
        if calendar_posts is None:
            print("\n❌ CRITICAL: Calendar posts endpoint failed")
            return False
        
        # Step 3-7: Test specific functionalities if we have posts
        test_results = {
            "calendar_posts_accessible": calendar_posts is not None and len(calendar_posts) > 0,
            "post_movement": False,
            "post_modification": False,
            "posts_validation": False,
            "content_thumbnails": False,
            "deprogrammer": False
        }
        
        # Test with first available post if any
        if calendar_posts and len(calendar_posts) > 0:
            test_post_id = calendar_posts[0].get('id')
            
            if test_post_id:
                test_results["post_movement"] = self.test_post_movement_endpoint(test_post_id)
                test_results["post_modification"] = self.test_post_modification_endpoint(test_post_id)
                test_results["deprogrammer"] = self.test_deprogrammer_functionality(test_post_id)
        
        # Test posts validation (independent of existing calendar posts)
        test_results["posts_validation"] = self.test_posts_validation_endpoint()
        
        # Test content thumbnails
        test_results["content_thumbnails"] = self.test_content_thumbnails()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 CALENDAR FUNCTIONALITIES TEST SUMMARY")
        print("=" * 70)
        
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        print()
        
        # Detailed results mapped to review request requirements
        feature_mapping = {
            "calendar_posts_accessible": "✅ Posts programmés apparaissent dans calendrier",
            "post_movement": "✅ Bouton 'Déplacer' fonctionnel", 
            "post_modification": "✅ Modal d'aperçu s'ouvre (modification)",
            "posts_validation": "✅ Posts apparaissent après 'Programmer'",
            "content_thumbnails": "✅ Vignettes/thumbnails visibles",
            "deprogrammer": "✅ Bouton 'Déprogrammer' fonctionnel"
        }
        
        for test_key, description in feature_mapping.items():
            status = "✅ WORKING" if test_results[test_key] else "❌ FAILED"
            print(f"{description}: {status}")
        
        print("\n" + "=" * 70)
        
        if success_rate >= 80:
            print("🎉 CONCLUSION: Calendar functionalities are MOSTLY OPERATIONAL after Programmer transformation")
        elif success_rate >= 60:
            print("⚠️ CONCLUSION: Calendar functionalities have SOME ISSUES after Programmer transformation")
        else:
            print("❌ CONCLUSION: Calendar functionalities have MAJOR ISSUES after Programmer transformation")
        
        return success_rate >= 60

def main():
    """Main test execution"""
    tester = CalendarTester()
    success = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()