#!/usr/bin/env python3
"""
Post Generation Image Assignment Debug Test
Testing the image assignment fix with comprehensive debug logging
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://claire-marcus-pwa-1.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class PostGenerationDebugTest:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        
    def authenticate(self):
        """Authenticate and get JWT token"""
        print("🔐 Step 1: Authentication")
        
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        response = self.session.post(f"{BASE_URL}/auth/login-robust", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.user_id = data["user_id"]
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            print(f"   ✅ Authentication successful")
            print(f"   👤 User ID: {self.user_id}")
            return True
        else:
            print(f"   ❌ Authentication failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return False
    
    def clear_existing_posts(self):
        """Clear all existing posts to start fresh"""
        print("\n🗑️ Step 2: Clearing existing posts")
        
        response = self.session.delete(f"{BASE_URL}/posts/generated/all")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Cleared {data.get('deleted_posts', 0)} existing posts")
            print(f"   🔄 Reset {data.get('reset_media_flags', 0)} media usage flags")
            return True
        else:
            print(f"   ❌ Failed to clear posts: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return False
    
    def check_available_content(self):
        """Check available content for post generation"""
        print("\n📂 Step 3: Checking available content")
        
        response = self.session.get(f"{BASE_URL}/content/pending?limit=50")
        
        if response.status_code == 200:
            data = response.json()
            content_items = data.get("content", [])
            total_items = len(content_items)
            
            print(f"   📊 Total content items available: {total_items}")
            
            # Analyze content by type and month
            images = [item for item in content_items if item.get("file_type", "").startswith("image")]
            videos = [item for item in content_items if item.get("file_type", "").startswith("video")]
            september_items = [item for item in content_items if item.get("attributed_month") == "septembre_2025"]
            
            print(f"   🖼️ Images: {len(images)}")
            print(f"   🎥 Videos: {len(videos)}")
            print(f"   📅 September 2025 attributed: {len(september_items)}")
            
            # Show first few items for debugging
            print(f"   🔍 First 3 content items:")
            for i, item in enumerate(content_items[:3]):
                print(f"      {i+1}. ID: {item.get('id', 'N/A')}")
                print(f"         Title: {item.get('title', 'N/A')}")
                print(f"         Filename: {item.get('filename', 'N/A')}")
                print(f"         Type: {item.get('file_type', 'N/A')}")
                print(f"         Month: {item.get('attributed_month', 'N/A')}")
                print(f"         URL: {item.get('url', 'N/A')}")
                print(f"         Used in posts: {item.get('used_in_posts', False)}")
                print()
            
            return content_items
        else:
            print(f"   ❌ Failed to get content: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return []
    
    def check_business_profile(self):
        """Check business profile for posting frequency"""
        print("\n👔 Step 4: Checking business profile")
        
        response = self.session.get(f"{BASE_URL}/business-profile")
        
        if response.status_code == 200:
            profile = response.json()
            print(f"   ✅ Business profile found")
            print(f"   🏢 Business name: {profile.get('business_name', 'N/A')}")
            print(f"   📊 Business type: {profile.get('business_type', 'N/A')}")
            print(f"   📅 Posting frequency: {profile.get('posting_frequency', 'N/A')}")
            return profile
        else:
            print(f"   ❌ Failed to get business profile: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return None
    
    def generate_posts_with_debug(self):
        """Generate posts for septembre_2025 and capture debug logs"""
        print("\n🚀 Step 5: Generating posts for septembre_2025")
        print("   📝 This will capture comprehensive debug logs...")
        
        # Start generation
        response = self.session.post(f"{BASE_URL}/posts/generate?target_month=septembre_2025")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Post generation completed successfully")
            print(f"   📊 Posts generated: {data.get('posts_count', 0)}")
            print(f"   🎯 Strategy: {data.get('strategy', {})}")
            print(f"   📂 Sources used: {data.get('sources_used', {})}")
            
            # Detailed analysis of sources used
            sources = data.get('sources_used', {})
            print(f"   🔍 DETAILED SOURCE ANALYSIS:")
            print(f"      📋 Business profile: {sources.get('business_profile', False)}")
            print(f"      🌐 Website analysis: {sources.get('website_analysis', False)}")
            print(f"      📅 Month content: {sources.get('month_content', 0)}")
            print(f"      📝 Always valid notes: {sources.get('always_valid_notes', 0)}")
            print(f"      📆 Month notes: {sources.get('month_notes', 0)}")
            print(f"      📂 Older content: {sources.get('older_content', 0)}")
            print(f"      🎨 Pixabay searches: {sources.get('pixabay_searches', 0)}")
            
            return True
        else:
            print(f"   ❌ Post generation failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return False
    
    def analyze_generated_posts(self):
        """Analyze the generated posts to check image assignment"""
        print("\n📋 Step 6: Analyzing generated posts")
        
        response = self.session.get(f"{BASE_URL}/posts/generated")
        
        if response.status_code == 200:
            data = response.json()
            posts = data.get("posts", [])
            total_posts = len(posts)
            
            print(f"   📊 Total posts retrieved: {total_posts}")
            
            # Analyze posts by status
            with_image = [post for post in posts if post.get("status") == "with_image"]
            needs_image = [post for post in posts if post.get("status") == "needs_image"]
            
            print(f"   🖼️ Posts with images: {len(with_image)}")
            print(f"   ❓ Posts needing images: {len(needs_image)}")
            
            # Analyze visual_id and visual_url assignment
            posts_with_visual_id = [post for post in posts if post.get("visual_id")]
            posts_with_visual_url = [post for post in posts if post.get("visual_url")]
            
            print(f"   🆔 Posts with visual_id: {len(posts_with_visual_id)}")
            print(f"   🔗 Posts with visual_url: {len(posts_with_visual_url)}")
            
            # Detailed analysis of first few posts
            print(f"   🔍 DETAILED POST ANALYSIS:")
            for i, post in enumerate(posts[:5]):
                print(f"      📝 Post {i+1}:")
                print(f"         ID: {post.get('id', 'N/A')}")
                print(f"         Title: {post.get('title', 'N/A')[:50]}...")
                print(f"         Status: {post.get('status', 'N/A')}")
                print(f"         Visual ID: {post.get('visual_id', 'N/A')}")
                print(f"         Visual URL: {post.get('visual_url', 'N/A')}")
                print(f"         Platform: {post.get('platform', 'N/A')}")
                print(f"         Content Type: {post.get('content_type', 'N/A')}")
                print(f"         Scheduled: {post.get('scheduled_date', 'N/A')}")
                print()
            
            # Critical analysis: Check if the image assignment fix worked
            success_rate = len(with_image) / total_posts * 100 if total_posts > 0 else 0
            
            print(f"   📈 IMAGE ASSIGNMENT SUCCESS RATE: {success_rate:.1f}%")
            
            if success_rate >= 80:
                print(f"   ✅ IMAGE ASSIGNMENT FIX APPEARS TO BE WORKING!")
            elif success_rate >= 50:
                print(f"   ⚠️ IMAGE ASSIGNMENT PARTIALLY WORKING - NEEDS INVESTIGATION")
            else:
                print(f"   ❌ IMAGE ASSIGNMENT FIX NOT WORKING - CRITICAL ISSUE")
            
            return posts
        else:
            print(f"   ❌ Failed to get generated posts: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return []
    
    def check_backend_logs(self):
        """Check backend logs for debug information"""
        print("\n📋 Step 7: Checking backend logs for debug information")
        print("   📝 Note: Debug logs should show content inventory processing")
        
        # This would typically require access to server logs
        # For now, we'll indicate what to look for
        print("   🔍 WHAT TO LOOK FOR IN BACKEND LOGS:")
        print("      - 'Collecting available content...'")
        print("      - 'Month-specific content found: X'")
        print("      - 'Total media found: X'")
        print("      - 'DEBUG: Processing item with URL: ...'")
        print("      - 'DEBUG: Extracted ID: ...'")
        print("      - 'FINAL month content available: X'")
        print("      - Content inventory sent to AI with proper IDs")
        print("      - AI response with visual_id values")
        
        return True
    
    def run_complete_test(self):
        """Run the complete post generation debug test"""
        print("🧪 POST GENERATION IMAGE ASSIGNMENT DEBUG TEST")
        print("=" * 60)
        print(f"🕐 Test started at: {datetime.now().isoformat()}")
        print(f"🎯 Target: Verify image assignment fix for septembre_2025")
        print()
        
        # Step 1: Authentication
        if not self.authenticate():
            return False
        
        # Step 2: Clear existing posts
        if not self.clear_existing_posts():
            return False
        
        # Step 3: Check available content
        content_items = self.check_available_content()
        if not content_items:
            print("   ⚠️ No content available - this may affect post generation")
        
        # Step 4: Check business profile
        profile = self.check_business_profile()
        if not profile:
            print("   ⚠️ No business profile - this may affect post generation")
        
        # Step 5: Generate posts with debug
        if not self.generate_posts_with_debug():
            return False
        
        # Wait a moment for processing
        print("\n⏳ Waiting 3 seconds for post processing...")
        time.sleep(3)
        
        # Step 6: Analyze generated posts
        posts = self.analyze_generated_posts()
        if not posts:
            return False
        
        # Step 7: Check backend logs
        self.check_backend_logs()
        
        # Final summary
        print("\n" + "=" * 60)
        print("📊 FINAL TEST SUMMARY")
        print("=" * 60)
        
        with_image_count = len([p for p in posts if p.get("status") == "with_image"])
        total_posts = len(posts)
        success_rate = with_image_count / total_posts * 100 if total_posts > 0 else 0
        
        print(f"✅ Total posts generated: {total_posts}")
        print(f"🖼️ Posts with images: {with_image_count}")
        print(f"📈 Success rate: {success_rate:.1f}%")
        print(f"📂 Content items available: {len(content_items)}")
        
        if success_rate >= 80:
            print(f"\n🎉 TEST RESULT: SUCCESS - Image assignment fix is working!")
            print(f"   The debug logs should show proper ID extraction and content inventory.")
        elif success_rate >= 50:
            print(f"\n⚠️ TEST RESULT: PARTIAL SUCCESS - Some images assigned but needs investigation")
            print(f"   Check debug logs for content inventory and ID extraction issues.")
        else:
            print(f"\n❌ TEST RESULT: FAILURE - Image assignment fix not working")
            print(f"   Critical issue: Posts are not getting images assigned properly.")
        
        print(f"\n🕐 Test completed at: {datetime.now().isoformat()}")
        return True

def main():
    """Main test execution"""
    test = PostGenerationDebugTest()
    success = test.run_complete_test()
    
    if success:
        print("\n✅ Test execution completed successfully")
    else:
        print("\n❌ Test execution failed")
    
    return success

if __name__ == "__main__":
    main()