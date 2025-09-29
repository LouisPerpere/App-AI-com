#!/usr/bin/env python3
"""
Database Post Modifier
Directly modifies the post in MongoDB to change platform from Instagram to Facebook
"""

import sys
import os
from datetime import datetime

# Add the backend directory to the path to import database module
sys.path.append('/app/backend')

try:
    from database import get_database
    print("✅ Database module imported successfully")
except ImportError as e:
    print(f"❌ Failed to import database module: {e}")
    sys.exit(1)

class DatabasePostModifier:
    def __init__(self):
        self.db_manager = None
        self.db = None
        
    def connect_database(self):
        """Connect to the database"""
        try:
            print("🔌 Connecting to database...")
            self.db_manager = get_database()
            
            if self.db_manager.is_connected():
                self.db = self.db_manager.db
                print("✅ Database connection successful")
                return True
            else:
                print("❌ Database connection failed")
                return False
                
        except Exception as e:
            print(f"❌ Database connection error: {str(e)}")
            return False
    
    def find_target_post(self, user_id):
        """Find the target Instagram post from September"""
        try:
            print(f"🔍 Finding Instagram posts from September for user {user_id}")
            
            # Query for Instagram posts from this user
            posts = list(self.db.generated_posts.find({
                "owner_id": user_id,
                "platform": "instagram"
            }))
            
            print(f"   Found {len(posts)} Instagram posts")
            
            # Filter for September posts
            september_posts = []
            for post in posts:
                scheduled_date = post.get("scheduled_date", "")
                created_at = post.get("created_at", "")
                published = post.get("published", False)
                
                # Check if it's from September and not published
                is_september = False
                if scheduled_date and "2025-09" in str(scheduled_date):
                    is_september = True
                elif created_at and "2025-09" in str(created_at):
                    is_september = True
                
                if is_september and not published:
                    september_posts.append(post)
                    print(f"   📅 Found September Instagram post:")
                    print(f"      ID: {post.get('id')}")
                    print(f"      Title: {post.get('title', 'N/A')[:50]}...")
                    print(f"      Status: {post.get('status')}")
                    print(f"      Published: {published}")
            
            if september_posts:
                # Return the first unpublished September post
                target_post = september_posts[0]
                print(f"✅ Selected target post: {target_post.get('id')}")
                return target_post
            else:
                print(f"❌ No unpublished September Instagram posts found")
                return None
                
        except Exception as e:
            print(f"❌ Error finding target post: {str(e)}")
            return None
    
    def modify_post_to_facebook(self, post_id, user_id):
        """Modify the post platform from Instagram to Facebook"""
        try:
            print(f"🔄 Modifying post {post_id} from Instagram to Facebook")
            
            # Prepare the update
            update_data = {
                "platform": "facebook",
                "status": "draft",
                "validated": False,
                "published": False,
                "updated_at": datetime.utcnow().isoformat(),
                "modified_for_testing": True,
                "original_platform": "instagram"
            }
            
            # Perform the update
            result = self.db.generated_posts.update_one(
                {
                    "id": post_id,
                    "owner_id": user_id
                },
                {
                    "$set": update_data
                }
            )
            
            print(f"   Update result:")
            print(f"   - Matched count: {result.matched_count}")
            print(f"   - Modified count: {result.modified_count}")
            
            if result.matched_count == 0:
                print(f"   ❌ Post not found in database")
                return False
            elif result.modified_count == 0:
                print(f"   ⚠️ Post found but not modified (may already have these values)")
                return True
            else:
                print(f"   ✅ Post successfully modified to Facebook")
                return True
                
        except Exception as e:
            print(f"   ❌ Error modifying post: {str(e)}")
            return False
    
    def verify_modification(self, post_id, user_id):
        """Verify that the modification was successful"""
        try:
            print(f"🔍 Verifying modification for post {post_id}")
            
            # Find the modified post
            modified_post = self.db.generated_posts.find_one({
                "id": post_id,
                "owner_id": user_id
            })
            
            if not modified_post:
                print(f"   ❌ Post not found for verification")
                return False
            
            print(f"   📋 Post after modification:")
            print(f"      ID: {modified_post.get('id')}")
            print(f"      Platform: {modified_post.get('platform')}")
            print(f"      Status: {modified_post.get('status')}")
            print(f"      Validated: {modified_post.get('validated')}")
            print(f"      Published: {modified_post.get('published')}")
            print(f"      Title: {modified_post.get('title', 'N/A')[:50]}...")
            print(f"      Modified for testing: {modified_post.get('modified_for_testing')}")
            print(f"      Original platform: {modified_post.get('original_platform')}")
            
            # Check if modification was successful
            if (modified_post.get('platform') == 'facebook' and
                modified_post.get('status') == 'draft' and
                not modified_post.get('validated', False) and
                not modified_post.get('published', False)):
                print(f"   ✅ Modification verified successfully!")
                return True
            else:
                print(f"   ❌ Modification verification failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Error verifying modification: {str(e)}")
            return False
    
    def run_modification(self):
        """Run the complete modification process"""
        print("🚀 Database Post Platform Modification")
        print("=" * 60)
        
        # User ID from the authentication
        user_id = "6a670c66-c06c-4d75-9dd5-c747e8a0281a"
        
        # Step 1: Connect to database
        if not self.connect_database():
            print("❌ Cannot proceed without database connection")
            return False
        
        # Step 2: Find target post
        target_post = self.find_target_post(user_id)
        if not target_post:
            print("❌ Cannot proceed without target post")
            return False
        
        post_id = target_post.get("id")
        
        # Step 3: Modify the post
        if not self.modify_post_to_facebook(post_id, user_id):
            print("❌ Post modification failed")
            return False
        
        # Step 4: Verify the modification
        if not self.verify_modification(post_id, user_id):
            print("❌ Modification verification failed")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 MISSION ACCOMPLISHED!")
        print("=" * 60)
        print(f"✅ Instagram post successfully modified to Facebook")
        print(f"✅ Post ID: {post_id}")
        print(f"✅ Platform: facebook")
        print(f"✅ Status: draft")
        print(f"✅ Validated: false")
        print(f"✅ Published: false")
        
        print(f"\n🎯 TESTING INSTRUCTIONS:")
        print(f"   1. Use the following endpoint to test Facebook publication:")
        print(f"      POST https://social-pub-hub.preview.emergentagent.com/api/posts/publish")
        print(f"      Body: {{'post_id': '{post_id}'}}")
        print(f"      Headers: Authorization: Bearer <token>")
        
        print(f"\n   2. Expected behavior:")
        print(f"      - Should attempt Facebook publication")
        print(f"      - Should show Facebook-specific logs")
        print(f"      - May show 'no active social connections' error (normal)")
        
        print(f"\n   3. This will help diagnose:")
        print(f"      - Facebook publication workflow")
        print(f"      - Interface behavior with Facebook posts")
        print(f"      - Publication logs and error handling")
        
        print("=" * 60)
        
        return True

def main():
    modifier = DatabasePostModifier()
    
    try:
        success = modifier.run_modification()
        if success:
            print(f"\n🎯 RESULT: Database modification COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print(f"\n💥 RESULT: Database modification FAILED")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()