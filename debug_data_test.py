#!/usr/bin/env python3
"""
Debug Test to Check Data Location for Restaurant Test User
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://claire-marcus.com/api"
TEST_USER_EMAIL = "test@claire-marcus.com"
TEST_USER_PASSWORD = "test123!"
TEST_USER_ID = "82ce1284-ca2e-469a-8521-2a9116ef7826"

class DataLocationDebugger:
    def __init__(self):
        self.session = requests.Session()
        self.jwt_token = None
        self.user_id = None
        
    def authenticate(self):
        """Authenticate with test user"""
        print(f"🔐 Authenticating with {TEST_USER_EMAIL}")
        
        try:
            auth_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json=auth_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.jwt_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                self.session.headers.update({
                    "Authorization": f"Bearer {self.jwt_token}"
                })
                
                print(f"✅ Authentication successful - User ID: {self.user_id}")
                return True
            else:
                print(f"❌ Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def check_notes_collection(self):
        """Check what data exists in the notes collection"""
        print(f"\\n📝 Checking Notes Collection")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/notes", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                notes = data.get("notes", [])
                
                print(f"   Total notes found: {len(notes)}")
                
                # Analyze notes content
                restaurant_posts = []
                website_analyses = []
                other_notes = []
                
                for note in notes:
                    content = note.get("content", "").lower()
                    description = note.get("description", "").lower()
                    
                    # Check for restaurant-related content
                    if any(keyword in content or keyword in description for keyword in 
                           ["bistrot", "jean", "restaurant", "lebistrotdejean", "octobre", "novembre"]):
                        if "seo" in content or "analyse" in description or "website" in content:
                            website_analyses.append(note)
                        else:
                            restaurant_posts.append(note)
                    else:
                        other_notes.append(note)\n                \n                print(f"   Restaurant posts: {len(restaurant_posts)}")\n                print(f"   Website analyses: {len(website_analyses)}")\n                print(f"   Other notes: {len(other_notes)}")\n                \n                # Show sample restaurant posts\n                if restaurant_posts:
                    print(f"\n   📊 Sample Restaurant Posts:")
                    for i, post in enumerate(restaurant_posts[:5]):
                        print(f"      {i+1}. ID: {post.get('note_id', 'N/A')}")
                        print(f"         Description: {post.get('description', 'N/A')}")
                        print(f"         Content preview: {post.get('content', '')[:100]}...")
                        print()
                
                # Show sample website analyses
                if website_analyses:
                    print(f"\n   🔍 Sample Website Analyses:")
                    for i, analysis in enumerate(website_analyses[:3]):
                        print(f"      {i+1}. ID: {analysis.get('note_id', 'N/A')}")
                        print(f"         Description: {analysis.get('description', 'N/A')}")
                        print(f"         Content preview: {analysis.get('content', '')[:100]}...")
                        print()\n                \n                return {
                    "total_notes": len(notes),
                    "restaurant_posts": len(restaurant_posts),
                    "website_analyses": len(website_analyses),
                    "other_notes": len(other_notes)
                }\n            else:\n                print(f\"   ❌ Error accessing notes: {response.text}\")\n                return None\n                \n        except Exception as e:\n            print(f\"   ❌ Exception checking notes: {str(e)}\")\n            return None\n    \n    def check_generated_posts_collection(self):\n        \"\"\"Check generated_posts collection directly\"\"\"\n        print(f\"\\n📝 Checking Generated Posts Collection\")\n        \n        try:\n            response = self.session.get(f\"{BACKEND_URL}/posts/generated\", timeout=30)\n            \n            if response.status_code == 200:\n                data = response.json()\n                posts = data.get(\"posts\", [])\n                \n                print(f\"   Posts in generated_posts collection: {len(posts)}\")\n                \n                if posts:\n                    print(f\"\\n   📊 Sample Generated Posts:\")\n                    for i, post in enumerate(posts[:3]):\n                        print(f\"      {i+1}. ID: {post.get('id', 'N/A')}\")\n                        print(f\"         Title: {post.get('title', 'N/A')}\")\n                        print(f\"         Platform: {post.get('platform', 'N/A')}\")\n                        print(f\"         Status: {post.get('status', 'N/A')}\")\n                        print()\n                \n                return len(posts)\n            else:\n                print(f\"   ❌ Error accessing generated posts: {response.text}\")\n                return 0\n                \n        except Exception as e:\n            print(f\"   ❌ Exception checking generated posts: {str(e)}\")\n            return 0\n    \n    def check_website_analyses_collection(self):\n        \"\"\"Check website_analyses collection directly\"\"\"\n        print(f\"\\n🔍 Checking Website Analyses Collection\")\n        \n        try:\n            response = self.session.get(f\"{BACKEND_URL}/website-analysis\", timeout=30)\n            \n            if response.status_code == 200:\n                data = response.json()\n                analyses = data.get(\"analyses\", [])\n                \n                print(f\"   Analyses in website_analyses collection: {len(analyses)}\")\n                \n                if analyses:\n                    print(f\"\\n   🔍 Sample Website Analyses:\")\n                    for i, analysis in enumerate(analyses[:3]):\n                        print(f\"      {i+1}. ID: {analysis.get('id', 'N/A')}\")\n                        print(f\"         URL: {analysis.get('website_url', 'N/A')}\")\n                        print(f\"         SEO Score: {analysis.get('seo_score', 'N/A')}\")\n                        print(f\"         Overall Score: {analysis.get('overall_score', 'N/A')}\")\n                        print()\n                \n                return len(analyses)\n            else:\n                print(f\"   ❌ Error accessing website analyses: {response.text}\")\n                return 0\n                \n        except Exception as e:\n            print(f\"   ❌ Exception checking website analyses: {str(e)}\")\n            return 0\n    \n    def run_debug(self):\n        \"\"\"Run all debug checks\"\"\"\n        print(\"🔍 RESTAURANT DATA LOCATION DEBUG\")\n        print(\"=\" * 60)\n        print(f\"Backend URL: {BACKEND_URL}\")\n        print(f\"Test User: {TEST_USER_EMAIL}\")\n        print(f\"Expected User ID: {TEST_USER_ID}\")\n        print(\"=\" * 60)\n        \n        # Authenticate\n        if not self.authenticate():\n            return False\n        \n        # Check all data locations\n        notes_data = self.check_notes_collection()\n        posts_count = self.check_generated_posts_collection()\n        analyses_count = self.check_website_analyses_collection()\n        \n        # Summary\n        print(\"\\n\" + \"=\" * 60)\n        print(\"🎯 DATA LOCATION SUMMARY\")\n        print(\"=\" * 60)\n        \n        if notes_data:\n            print(f\"📝 Notes Collection:\")\n            print(f\"   Total notes: {notes_data['total_notes']}\")\n            print(f\"   Restaurant posts: {notes_data['restaurant_posts']}\")\n            print(f\"   Website analyses: {notes_data['website_analyses']}\")\n            print(f\"   Other notes: {notes_data['other_notes']}\")\n        \n        print(f\"\\n📊 Generated Posts Collection: {posts_count} posts\")\n        print(f\"🔍 Website Analyses Collection: {analyses_count} analyses\")\n        \n        # Diagnosis\n        print(\"\\n\" + \"=\" * 60)\n        print(\"🩺 DIAGNOSIS\")\n        print(\"=\" * 60)\n        \n        if notes_data and (notes_data['restaurant_posts'] > 0 or notes_data['website_analyses'] > 0):\n            if posts_count == 0 and analyses_count == 0:\n                print(\"❌ MIGRATION ISSUE CONFIRMED:\")\n                print(\"   - Restaurant data exists in 'notes' collection\")\n                print(\"   - No data in 'generated_posts' or 'website_analyses' collections\")\n                print(\"   - Migration from notes to proper collections is required\")\n                return False\n            else:\n                print(\"✅ DATA PARTIALLY MIGRATED:\")\n                print(\"   - Some data exists in proper collections\")\n                print(\"   - May need to complete migration\")\n                return True\n        else:\n            print(\"❌ NO RESTAURANT DATA FOUND:\")\n            print(\"   - No restaurant data in any collection\")\n            print(\"   - Data may have been lost or not created\")\n            return False\n\ndef main():\n    \"\"\"Main debug execution\"\"\"\n    debugger = DataLocationDebugger()\n    success = debugger.run_debug()\n    \n    sys.exit(0 if success else 1)\n\nif __name__ == \"__main__\":\n    main()