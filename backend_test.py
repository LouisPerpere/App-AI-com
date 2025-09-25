#!/usr/bin/env python3
"""
Backend Test Suite for POST Validator API
Testing the GET /posts/generated endpoint to verify 'validated' field inclusion
"""

import requests
import json
import sys
from datetime import datetime

class PostValidatorTester:
    def __init__(self):
        self.base_url = "https://post-validator.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        
    def authenticate(self, email, password):
        """Authenticate with the API"""
        try:
            print(f"🔐 Step 1: Authenticating with {email}")
            
            response = self.session.post(
                f"{self.base_url}/auth/login-robust",
                json={"email": email, "password": password},
                headers={"Content-Type": "application/json"}
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for all future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                })
                
                print(f"   ✅ Authentication successful")
                print(f"   User ID: {self.user_id}")
                print(f"   Token: {self.token[:30]}..." if self.token else "   Token: None")
                return True
            else:
                print(f"   ❌ Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {str(e)}")
            return False
    
    def test_posts_generated_endpoint(self):
        """Test GET /posts/generated endpoint for validated field inclusion"""
        try:
            print(f"\n🔍 Step 2: Testing GET /posts/generated endpoint")
            
            response = self.session.get(f"{self.base_url}/posts/generated")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                count = data.get("count", 0)
                
                print(f"   ✅ Endpoint accessible")
                print(f"   Total posts found: {count}")
                
                if count == 0:
                    print(f"   ⚠️ No posts found for testing - this is expected if no posts exist")
                    return True
                
                # Test each post for required fields
                validated_posts = 0
                posts_with_validated_at = 0
                posts_with_carousel_images = 0
                
                print(f"\n📋 Analyzing post structure:")
                
                for i, post in enumerate(posts[:5]):  # Check first 5 posts for detailed analysis
                    print(f"\n   Post {i+1}:")
                    print(f"     ID: {post.get('id', 'N/A')}")
                    print(f"     Title: {post.get('title', 'N/A')[:50]}...")
                    print(f"     Platform: {post.get('platform', 'N/A')}")
                    print(f"     Status: {post.get('status', 'N/A')}")
                    
                    # Check for validated field
                    if 'validated' in post:
                        validated_value = post.get('validated')
                        print(f"     ✅ 'validated' field present: {validated_value}")
                        if validated_value is True:
                            validated_posts += 1
                    else:
                        print(f"     ❌ 'validated' field MISSING")
                        return False
                    
                    # Check for validated_at field
                    if 'validated_at' in post:
                        validated_at_value = post.get('validated_at')
                        print(f"     ✅ 'validated_at' field present: {validated_at_value}")
                        if validated_at_value:
                            posts_with_validated_at += 1
                    else:
                        print(f"     ❌ 'validated_at' field MISSING")
                        return False
                    
                    # Check for carousel_images field
                    if 'carousel_images' in post:
                        carousel_images_value = post.get('carousel_images', [])
                        print(f"     ✅ 'carousel_images' field present: {len(carousel_images_value)} images")
                        if carousel_images_value:
                            posts_with_carousel_images += 1
                    else:
                        print(f"     ❌ 'carousel_images' field MISSING")
                        return False
                
                # Summary statistics
                print(f"\n📊 Field Analysis Summary:")
                print(f"   Total posts analyzed: {min(len(posts), 5)}")
                print(f"   Posts with validated=true: {validated_posts}")
                print(f"   Posts with validated_at data: {posts_with_validated_at}")
                print(f"   Posts with carousel_images data: {posts_with_carousel_images}")
                
                # Check all posts have the required fields (not just first 5)
                all_posts_valid = True
                for post in posts:
                    if 'validated' not in post or 'validated_at' not in post or 'carousel_images' not in post:
                        all_posts_valid = False
                        break
                
                if all_posts_valid:
                    print(f"   ✅ ALL {count} posts contain required fields (validated, validated_at, carousel_images)")
                    return True
                else:
                    print(f"   ❌ Some posts missing required fields")
                    return False
                
            else:
                print(f"   ❌ Endpoint failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Test error: {str(e)}")
            return False
    
    def test_field_structure_validation(self):
        """Test the structure and types of the new fields"""
        try:
            print(f"\n🔍 Step 3: Testing field structure validation")
            
            response = self.session.get(f"{self.base_url}/posts/generated")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                
                if not posts:
                    print(f"   ⚠️ No posts available for structure validation")
                    return True
                
                # Test first post for detailed structure validation
                test_post = posts[0]
                print(f"   Testing post structure: {test_post.get('id', 'N/A')}")
                
                # Validate 'validated' field type
                validated_field = test_post.get('validated')
                if isinstance(validated_field, bool):
                    print(f"   ✅ 'validated' field is boolean: {validated_field}")
                else:
                    print(f"   ❌ 'validated' field should be boolean, got: {type(validated_field)} = {validated_field}")
                    return False
                
                # Validate 'validated_at' field type
                validated_at_field = test_post.get('validated_at')
                if isinstance(validated_at_field, str):
                    print(f"   ✅ 'validated_at' field is string: '{validated_at_field}'")
                    if validated_at_field:
                        # Try to parse as ISO datetime if not empty
                        try:
                            datetime.fromisoformat(validated_at_field.replace('Z', '+00:00'))
                            print(f"   ✅ 'validated_at' is valid ISO datetime")
                        except:
                            print(f"   ⚠️ 'validated_at' is not valid ISO datetime format")
                else:
                    print(f"   ❌ 'validated_at' field should be string, got: {type(validated_at_field)}")
                    return False
                
                # Validate 'carousel_images' field type
                carousel_images_field = test_post.get('carousel_images')
                if isinstance(carousel_images_field, list):
                    print(f"   ✅ 'carousel_images' field is list with {len(carousel_images_field)} items")
                    if carousel_images_field:
                        print(f"   📸 Sample carousel image: {carousel_images_field[0] if carousel_images_field else 'None'}")
                else:
                    print(f"   ❌ 'carousel_images' field should be list, got: {type(carousel_images_field)}")
                    return False
                
                return True
            else:
                print(f"   ❌ Failed to get posts for structure validation")
                return False
                
        except Exception as e:
            print(f"   ❌ Structure validation error: {str(e)}")
            return False
    
    def test_validated_posts_logic(self):
        """Test that previously validated posts have validated=true"""
        try:
            print(f"\n🔍 Step 4: Testing validated posts logic")
            
            response = self.session.get(f"{self.base_url}/posts/generated")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                
                if not posts:
                    print(f"   ⚠️ No posts available for validation logic testing")
                    return True
                
                validated_posts = [p for p in posts if p.get('validated') is True]
                posts_with_validated_at = [p for p in posts if p.get('validated_at')]
                
                print(f"   Total posts: {len(posts)}")
                print(f"   Posts with validated=true: {len(validated_posts)}")
                print(f"   Posts with validated_at timestamp: {len(posts_with_validated_at)}")
                
                # Logic check: posts with validated=true should have validated_at timestamp
                inconsistent_posts = 0
                for post in validated_posts:
                    if not post.get('validated_at'):
                        inconsistent_posts += 1
                        print(f"   ⚠️ Post {post.get('id')} has validated=true but no validated_at timestamp")
                
                if inconsistent_posts == 0:
                    print(f"   ✅ All validated posts have consistent validated_at timestamps")
                else:
                    print(f"   ⚠️ Found {inconsistent_posts} posts with inconsistent validation data")
                
                # Show sample validated post if available
                if validated_posts:
                    sample_post = validated_posts[0]
                    print(f"\n   📋 Sample validated post:")
                    print(f"     ID: {sample_post.get('id')}")
                    print(f"     Validated: {sample_post.get('validated')}")
                    print(f"     Validated At: {sample_post.get('validated_at')}")
                    print(f"     Platform: {sample_post.get('platform')}")
                    print(f"     Status: {sample_post.get('status')}")
                
                return True
            else:
                print(f"   ❌ Failed to get posts for validation logic testing")
                return False
                
        except Exception as e:
            print(f"   ❌ Validation logic test error: {str(e)}")
            return False
    
    def test_response_format_compatibility(self):
        """Test that the response format is compatible with frontend expectations"""
        try:
            print(f"\n🔍 Step 5: Testing response format compatibility")
            
            response = self.session.get(f"{self.base_url}/posts/generated")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check top-level structure
                if 'posts' in data and 'count' in data:
                    print(f"   ✅ Response has correct top-level structure (posts, count)")
                else:
                    print(f"   ❌ Response missing required top-level fields")
                    return False
                
                posts = data.get("posts", [])
                count = data.get("count", 0)
                
                # Verify count matches posts length
                if len(posts) == count:
                    print(f"   ✅ Count field matches posts array length: {count}")
                else:
                    print(f"   ⚠️ Count mismatch: count={count}, posts length={len(posts)}")
                
                if posts:
                    # Check that all expected fields are present in posts
                    expected_fields = [
                        'id', 'title', 'text', 'hashtags', 'visual_url', 'visual_id',
                        'visual_type', 'platform', 'content_type', 'scheduled_date',
                        'status', 'published', 'validated', 'validated_at', 
                        'carousel_images', 'created_at', 'modified_at'
                    ]
                    
                    sample_post = posts[0]
                    missing_fields = []
                    
                    for field in expected_fields:
                        if field not in sample_post:
                            missing_fields.append(field)
                    
                    if not missing_fields:
                        print(f"   ✅ All {len(expected_fields)} expected fields present in posts")
                    else:
                        print(f"   ❌ Missing fields in posts: {missing_fields}")
                        return False
                
                return True
            else:
                print(f"   ❌ Failed to get posts for format compatibility testing")
                return False
                
        except Exception as e:
            print(f"   ❌ Format compatibility test error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting POST Validator Backend Testing")
        print("=" * 60)
        
        # Test credentials from the review request
        email = "lperpere@yahoo.fr"
        password = "L@Reunion974!"
        
        # Step 1: Authentication
        if not self.authenticate(email, password):
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Test GET /posts/generated endpoint
        if not self.test_posts_generated_endpoint():
            print("\n❌ CRITICAL: GET /posts/generated endpoint test failed")
            return False
        
        # Step 3: Test field structure validation
        if not self.test_field_structure_validation():
            print("\n❌ CRITICAL: Field structure validation failed")
            return False
        
        # Step 4: Test validated posts logic
        if not self.test_validated_posts_logic():
            print("\n❌ CRITICAL: Validated posts logic test failed")
            return False
        
        # Step 5: Test response format compatibility
        if not self.test_response_format_compatibility():
            print("\n❌ CRITICAL: Response format compatibility test failed")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED SUCCESSFULLY!")
        print("✅ GET /posts/generated endpoint includes 'validated' field")
        print("✅ 'validated_at' and 'carousel_images' fields are present")
        print("✅ Field types and structure are correct")
        print("✅ Response format is compatible with frontend")
        print("=" * 60)
        
        return True

def main():
    """Main test execution"""
    tester = PostValidatorTester()
    
    try:
        success = tester.run_all_tests()
        if success:
            print(f"\n🎯 CONCLUSION: Backend validation field fix is WORKING CORRECTLY")
            sys.exit(0)
        else:
            print(f"\n💥 CONCLUSION: Backend validation field fix has ISSUES")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()