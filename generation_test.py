#!/usr/bin/env python3
"""
🎯 TEST GÉNÉRATION POSTS - DIAGNOSTIC APPROFONDI
Test pour comprendre exactement comment la génération détermine les plateformes
"""

import requests
import json
import sys

class GenerationTest:
    def __init__(self):
        self.base_url = "https://social-pub-hub.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.credentials = {
            "email": "lperpere@yahoo.fr",
            "password": "L@Reunion974!"
        }
        
    def authenticate(self):
        """Authenticate with the API"""
        try:
            print(f"🔐 Authenticating with {self.credentials['email']}")
            
            response = self.session.post(
                f"{self.base_url}/auth/login-robust",
                json=self.credentials,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                })
                
                print(f"   ✅ Authentication successful - User ID: {self.user_id}")
                return True
            else:
                print(f"   ❌ Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {str(e)}")
            return False
    
    def test_generation_with_current_connections(self):
        """Test generation with current connection state"""
        try:
            print(f"\n🧪 Testing post generation with current connections")
            
            # Test generation for October 2025 to avoid conflicts
            generation_request = {
                "month_key": "2025-10"  # October 2025
            }
            
            print(f"   Requesting generation for: {generation_request['month_key']}")
            
            response = self.session.post(
                f"{self.base_url}/posts/generate",
                json=generation_request
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Generation successful!")
                print(f"   📊 Posts generated: {data.get('posts_count', 0)}")
                print(f"   📋 Strategy: {data.get('strategy', 'Unknown')}")
                print(f"   📋 Sources used: {data.get('sources_used', [])}")
                
                # Now check what was actually generated
                self.check_generated_posts_for_october()
                
                return True
            else:
                print(f"   ❌ Generation failed: {response.text}")
                try:
                    error_data = response.json()
                    print(f"   📋 Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
                except:
                    pass
                return False
                
        except Exception as e:
            print(f"   ❌ Error testing generation: {str(e)}")
            return False
    
    def check_generated_posts_for_october(self):
        """Check what posts were generated for October"""
        try:
            print(f"\n📝 Checking generated posts for October")
            
            response = self.session.get(f"{self.base_url}/posts/generated")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                
                # Filter October posts
                october_posts = []
                for post in posts:
                    scheduled_date = post.get("scheduled_date", "")
                    target_month = post.get("target_month", "")
                    if "2025-10" in scheduled_date or "octobre_2025" in target_month:
                        october_posts.append(post)
                
                print(f"   📊 October posts found: {len(october_posts)}")
                
                if october_posts:
                    facebook_posts = [p for p in october_posts if p.get("platform") == "facebook"]
                    instagram_posts = [p for p in october_posts if p.get("platform") == "instagram"]
                    
                    print(f"   📊 Platform distribution:")
                    print(f"     Facebook: {len(facebook_posts)}")
                    print(f"     Instagram: {len(instagram_posts)}")
                    
                    print(f"   📋 Post details:")
                    for i, post in enumerate(october_posts[:5]):  # Show first 5
                        title = post.get("title", "No title")[:40]
                        platform = post.get("platform", "Unknown")
                        date = post.get("scheduled_date", "No date")
                        print(f"     {i+1}. [{platform.upper()}] {title}... | {date}")
                
                return october_posts
            else:
                print(f"   ❌ Failed to get posts: {response.text}")
                return []
                
        except Exception as e:
            print(f"   ❌ Error checking posts: {str(e)}")
            return []
    
    def run_generation_test(self):
        """Run the complete generation test"""
        print("🎯 MISSION: Test génération posts avec connexions actuelles")
        print("🔍 OBJECTIF: Voir quelles plateformes sont utilisées lors de la génération")
        print("=" * 70)
        
        if not self.authenticate():
            return False
        
        # Test generation
        success = self.test_generation_with_current_connections()
        
        print("\n" + "=" * 70)
        print("🎉 GENERATION TEST COMPLETED")
        print("=" * 70)
        
        return success

def main():
    test = GenerationTest()
    
    try:
        success = test.run_generation_test()
        if success:
            print(f"\n🎯 CONCLUSION: Generation test COMPLETED")
        else:
            print(f"\n💥 CONCLUSION: Generation test FAILED")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()