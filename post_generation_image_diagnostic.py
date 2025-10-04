#!/usr/bin/env python3
"""
POST GENERATION IMAGE DIAGNOSTIC TEST
Diagnose why all posts are generated without images (status "needs_image" instead of "with_image").

INVESTIGATION FOCUS:
1. Check if there are uploaded content/images available in the user's library for post generation
2. Verify that the content inventory is being properly formatted and sent to the AI
3. Check the AI response to see if visual_id fields are being returned
4. Test the post generation logic to see where the visual assignment is failing

Credentials: lperpere@yahoo.fr / L@Reunion974!
Backend URL: https://claire-marcus-app-1.preview.emergentagent.com/api
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://claire-marcus-app-1.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class PostGenerationImageDiagnostic:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        
    def authenticate(self):
        """Step 1: Authenticate with test credentials"""
        print("🔐 STEP 1: Authentication...")
        
        auth_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json=auth_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Configure headers for subsequent requests
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
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def check_available_content(self):
        """Step 2: Check user's available content/images for post generation"""
        print("\n📂 STEP 2: Checking available content in user's library...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/content/pending", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                total_items = data.get("total", 0)
                
                print(f"✅ Content library retrieved successfully")
                print(f"   Total items: {total_items}")
                print(f"   Items loaded: {len(content_items)}")
                
                # Analyze content types
                images = [item for item in content_items if item.get("file_type", "").startswith("image")]
                videos = [item for item in content_items if item.get("file_type", "").startswith("video")]
                
                print(f"   📸 Images: {len(images)}")
                print(f"   🎥 Videos: {len(videos)}")
                
                # Show first few items with details
                print(f"\n   📋 First 5 content items:")
                for i, item in enumerate(content_items[:5]):
                    print(f"   {i+1}. ID: {item.get('id', 'No ID')}")
                    print(f"      Filename: {item.get('filename', 'No filename')}")
                    print(f"      File type: {item.get('file_type', 'No type')}")
                    print(f"      Title: {item.get('title', 'No title')}")
                    print(f"      Context: {item.get('context', 'No context')[:50]}...")
                    print(f"      URL: {item.get('url', 'No URL')}")
                    print(f"      Used in posts: {item.get('used_in_posts', False)}")
                    print()
                
                return {
                    "success": True,
                    "total_items": total_items,
                    "images": len(images),
                    "videos": len(videos),
                    "content_items": content_items
                }
            else:
                print(f"❌ Failed to get content: {response.status_code}")
                print(f"   Response: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Error getting content: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def check_business_profile(self):
        """Step 3: Check business profile for post generation context"""
        print("\n👤 STEP 3: Checking business profile...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/business-profile", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Business profile retrieved")
                print(f"   Business name: {data.get('business_name', 'Not set')}")
                print(f"   Business type: {data.get('business_type', 'Not set')}")
                print(f"   Posting frequency: {data.get('posting_frequency', 'Not set')}")
                print(f"   Description: {data.get('business_description', 'Not set')[:100]}...")
                
                return {"success": True, "profile": data}
            else:
                print(f"❌ Failed to get business profile: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Error getting business profile: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def check_notes(self):
        """Step 4: Check user's notes for post generation context"""
        print("\n📝 STEP 4: Checking user's notes...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/notes", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                notes = data.get("notes", [])
                
                print(f"✅ Notes retrieved")
                print(f"   Total notes: {len(notes)}")
                
                # Show first few notes
                for i, note in enumerate(notes[:3]):
                    print(f"   {i+1}. {note.get('description', 'No title')}: {note.get('content', '')[:50]}...")
                    print(f"      Priority: {note.get('priority', 'normal')}")
                    print(f"      Monthly note: {note.get('is_monthly_note', False)}")
                
                return {"success": True, "notes": notes}
            else:
                print(f"❌ Failed to get notes: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Error getting notes: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def clear_existing_posts(self):
        """Step 5: Clear existing posts for clean test"""
        print("\n🗑️ STEP 5: Clearing existing posts for clean test...")
        
        try:
            response = self.session.delete(f"{BACKEND_URL}/posts/generated/all", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Existing posts cleared")
                print(f"   Deleted posts: {data.get('deleted_posts', 0)}")
                return True
            else:
                print(f"⚠️ Could not clear posts: {response.status_code}")
                return True  # Continue anyway
                
        except Exception as e:
            print(f"⚠️ Error clearing posts: {str(e)}")
            return True  # Continue anyway
    
    def generate_posts_with_monitoring(self):
        """Step 6: Generate posts and monitor the process"""
        print("\n🚀 STEP 6: Generating posts with detailed monitoring...")
        
        try:
            print("   📤 Sending post generation request...")
            response = self.session.post(
                f"{BACKEND_URL}/posts/generate",
                params={"target_month": "septembre_2025"},
                timeout=120  # Extended timeout for AI generation
            )
            
            print(f"   📥 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Post generation completed")
                print(f"   Success: {data.get('success', False)}")
                print(f"   Posts generated: {data.get('posts_count', 0)}")
                print(f"   Strategy: {data.get('strategy', {})}")
                print(f"   Sources used: {data.get('sources_used', {})}")
                
                return {"success": True, "generation_result": data}
            else:
                print(f"❌ Post generation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Error generating posts: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def analyze_generated_posts(self):
        """Step 7: Analyze the generated posts to check image assignment"""
        print("\n🔍 STEP 7: Analyzing generated posts for image assignment...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/posts/generated", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                
                print(f"✅ Generated posts retrieved")
                print(f"   Total posts: {len(posts)}")
                
                # Analyze image assignment
                posts_with_image = [p for p in posts if p.get("visual_id") and p.get("visual_url")]
                posts_needs_image = [p for p in posts if p.get("status") == "needs_image"]
                posts_with_image_status = [p for p in posts if p.get("status") == "with_image"]
                
                print(f"\n   📊 IMAGE ASSIGNMENT ANALYSIS:")
                print(f"   Posts with visual_id: {len(posts_with_image)}")
                print(f"   Posts with status 'needs_image': {len(posts_needs_image)}")
                print(f"   Posts with status 'with_image': {len(posts_with_image_status)}")
                
                # Show detailed analysis of first few posts
                print(f"\n   📋 DETAILED POST ANALYSIS:")
                for i, post in enumerate(posts[:5]):
                    print(f"   Post {i+1}:")
                    print(f"      ID: {post.get('id', 'No ID')}")
                    print(f"      Title: {post.get('title', 'No title')}")
                    print(f"      Status: {post.get('status', 'No status')}")
                    print(f"      Visual ID: {post.get('visual_id', 'No visual_id')}")
                    print(f"      Visual URL: {post.get('visual_url', 'No visual_url')}")
                    print(f"      Content type: {post.get('content_type', 'No content_type')}")
                    print(f"      Text preview: {post.get('text', '')[:100]}...")
                    print()
                
                return {
                    "success": True,
                    "posts": posts,
                    "posts_with_image": len(posts_with_image),
                    "posts_needs_image": len(posts_needs_image),
                    "posts_with_image_status": len(posts_with_image_status)
                }
            else:
                print(f"❌ Failed to get generated posts: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Error analyzing posts: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def run_diagnostic(self):
        """Execute the complete diagnostic"""
        print("=" * 80)
        print("🔬 POST GENERATION IMAGE DIAGNOSTIC")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test credentials: {TEST_EMAIL}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ DIAGNOSTIC FAILED: Authentication failed")
            return False
        
        # Step 2: Check available content
        content_result = self.check_available_content()
        if not content_result.get("success"):
            print("\n❌ DIAGNOSTIC FAILED: Could not retrieve content")
            return False
        
        # Step 3: Check business profile
        profile_result = self.check_business_profile()
        
        # Step 4: Check notes
        notes_result = self.check_notes()
        
        # Step 5: Clear existing posts
        self.clear_existing_posts()
        
        # Step 6: Generate posts
        generation_result = self.generate_posts_with_monitoring()
        if not generation_result.get("success"):
            print("\n❌ DIAGNOSTIC FAILED: Post generation failed")
            return False
        
        # Step 7: Analyze generated posts
        analysis_result = self.analyze_generated_posts()
        if not analysis_result.get("success"):
            print("\n❌ DIAGNOSTIC FAILED: Could not analyze generated posts")
            return False
        
        # Final diagnostic summary
        print("\n" + "=" * 80)
        print("📋 DIAGNOSTIC RESULTS SUMMARY")
        print("=" * 80)
        
        # Content availability
        total_content = content_result.get("total_items", 0)
        images_available = content_result.get("images", 0)
        
        print(f"📂 CONTENT AVAILABILITY:")
        print(f"   Total content items: {total_content}")
        print(f"   Images available: {images_available}")
        print(f"   Content available for posts: {'✅ YES' if images_available > 0 else '❌ NO'}")
        
        # Post generation results
        posts_generated = generation_result.get("generation_result", {}).get("posts_count", 0)
        posts_with_image = analysis_result.get("posts_with_image", 0)
        posts_needs_image = analysis_result.get("posts_needs_image", 0)
        posts_with_image_status = analysis_result.get("posts_with_image_status", 0)
        
        print(f"\n🚀 POST GENERATION RESULTS:")
        print(f"   Posts generated: {posts_generated}")
        print(f"   Posts with visual_id assigned: {posts_with_image}")
        print(f"   Posts with status 'needs_image': {posts_needs_image}")
        print(f"   Posts with status 'with_image': {posts_with_image_status}")
        
        # Root cause analysis
        print(f"\n🔍 ROOT CAUSE ANALYSIS:")
        
        if images_available == 0:
            print("❌ ISSUE IDENTIFIED: No images available in user's library")
            print("   RECOMMENDATION: User needs to upload images before generating posts")
        elif posts_with_image == 0 and images_available > 0:
            print("❌ ISSUE IDENTIFIED: Images available but not assigned to posts")
            print("   POSSIBLE CAUSES:")
            print("   1. Content inventory not properly formatted for AI")
            print("   2. AI not returning valid visual_id fields")
            print("   3. Post generation logic not mapping visual_id correctly")
        elif posts_with_image > 0 and posts_with_image_status == 0:
            print("❌ ISSUE IDENTIFIED: Posts have visual_id but status not set to 'with_image'")
            print("   POSSIBLE CAUSE: Status assignment logic issue in post generation")
        else:
            print("✅ NO MAJOR ISSUES: Posts are being generated with images correctly")
        
        # Success criteria
        success_criteria = [
            images_available > 0,
            posts_generated > 0,
            posts_with_image_status > 0 or (posts_with_image > 0 and posts_needs_image < posts_generated)
        ]
        
        overall_success = all(success_criteria)
        
        print("\n" + "=" * 80)
        if overall_success:
            print("🎉 DIAGNOSTIC PASSED - Post generation with images working correctly!")
        else:
            print("❌ DIAGNOSTIC FAILED - Issues detected in post generation image assignment")
            print("\n🔧 RECOMMENDED ACTIONS:")
            if images_available == 0:
                print("   1. Upload images to user's library")
            if posts_generated == 0:
                print("   2. Fix post generation system")
            if posts_with_image == 0 and images_available > 0:
                print("   3. Debug content inventory formatting and AI response parsing")
            if posts_with_image > 0 and posts_with_image_status == 0:
                print("   4. Fix post status assignment logic")
        
        return overall_success

def main():
    """Main diagnostic execution"""
    diagnostic = PostGenerationImageDiagnostic()
    success = diagnostic.run_diagnostic()
    
    if success:
        print("\n🎉 POST GENERATION IMAGE DIAGNOSTIC COMPLETED SUCCESSFULLY")
        sys.exit(0)
    else:
        print("\n💥 POST GENERATION IMAGE DIAGNOSTIC FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()