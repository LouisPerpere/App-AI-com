#!/usr/bin/env python3
"""
Debug test to understand content structure and image attachment issues
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://social-ai-planner-2.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class ContentDebugger:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        
    def authenticate(self):
        """Authentification avec les credentials fournis"""
        print("🔐 Authentification...")
        
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
                
                print(f"✅ Authentification réussie - User ID: {self.user_id}")
                return True
            else:
                print(f"❌ Échec authentification: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur authentification: {e}")
            return False
    
    def debug_content_structure(self):
        """Debug the content structure to understand the data format"""
        print("\n🔍 ANALYSE STRUCTURE CONTENU")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                
                print(f"📊 Total items: {len(content_items)}")
                
                if content_items:
                    # Analyze first few items
                    for i, item in enumerate(content_items[:3]):
                        print(f"\n📄 Item {i+1}:")
                        print(f"   ID: {item.get('id', 'N/A')}")
                        print(f"   Filename: {item.get('filename', 'N/A')}")
                        print(f"   File Type: {item.get('file_type', 'N/A')}")
                        print(f"   Source: {item.get('source', 'N/A')}")
                        print(f"   Title: {item.get('title', 'N/A')}")
                        print(f"   Context: {item.get('context', 'N/A')}")
                        print(f"   Used in posts: {item.get('used_in_posts', 'N/A')}")
                        print(f"   All fields: {list(item.keys())}")
                
                # Find image items specifically
                image_items = [item for item in content_items if item.get('file_type', '').startswith('image')]
                print(f"\n🖼️ Image items: {len(image_items)}")
                
                if image_items:
                    print(f"   First image ID: {image_items[0].get('id')}")
                    print(f"   First image filename: {image_items[0].get('filename')}")
                    
                return content_items
            else:
                print(f"❌ Erreur récupération contenu: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Erreur debug contenu: {e}")
            return []
    
    def debug_posts_structure(self):
        """Debug the posts structure"""
        print("\n🔍 ANALYSE STRUCTURE POSTS")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/posts/generated")
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                
                print(f"📊 Total posts: {len(posts)}")
                
                # Find posts with and without images
                posts_with_images = [p for p in posts if p.get('visual_id')]
                posts_without_images = [p for p in posts if not p.get('visual_id')]
                posts_with_carousel = [p for p in posts if p.get('visual_id', '').startswith('carousel_')]
                
                print(f"   Posts with images: {len(posts_with_images)}")
                print(f"   Posts without images: {len(posts_without_images)}")
                print(f"   Posts with carousel: {len(posts_with_carousel)}")
                
                if posts_with_images:
                    sample_post = posts_with_images[0]
                    print(f"\n📄 Sample post with image:")
                    print(f"   ID: {sample_post.get('id')}")
                    print(f"   Visual ID: {sample_post.get('visual_id')}")
                    print(f"   Visual URL: {sample_post.get('visual_url')}")
                    print(f"   Status: {sample_post.get('status')}")
                
                if posts_without_images:
                    sample_post = posts_without_images[0]
                    print(f"\n📄 Sample post without image:")
                    print(f"   ID: {sample_post.get('id')}")
                    print(f"   Status: {sample_post.get('status')}")
                
                return posts
            else:
                print(f"❌ Erreur récupération posts: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Erreur debug posts: {e}")
            return []
    
    def test_image_attachment_debug(self, post_id, image_id):
        """Test image attachment with detailed debugging"""
        print(f"\n🧪 TEST ATTACHEMENT IMAGE DEBUG")
        print(f"   Post ID: {post_id}")
        print(f"   Image ID: {image_id}")
        print("=" * 50)
        
        attach_data = {
            "image_source": "library",
            "image_id": image_id
        }
        
        try:
            response = self.session.put(
                f"{BACKEND_URL}/posts/{post_id}/attach-image",
                json=attach_data
            )
            
            print(f"📊 Response Status: {response.status_code}")
            print(f"📊 Response Headers: {dict(response.headers)}")
            print(f"📊 Response Body: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success: {result}")
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    def test_upload_debug(self):
        """Test upload functionality with debugging"""
        print(f"\n🧪 TEST UPLOAD DEBUG")
        print("=" * 50)
        
        # Create a simple test image file
        test_image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
        
        files = {
            'files': ('test_debug.png', test_image_content, 'image/png')
        }
        
        data = {
            'upload_type': 'single',
            'attributed_month': 'decembre_2025'
        }
        
        try:
            # Remove Content-Type header for multipart upload
            headers = self.session.headers.copy()
            if 'Content-Type' in headers:
                del headers['Content-Type']
            
            response = self.session.post(
                f"{BACKEND_URL}/content/batch-upload",
                files=files,
                data=data,
                headers=headers
            )
            
            print(f"📊 Upload Response Status: {response.status_code}")
            print(f"📊 Upload Response Body: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                uploaded_files = result.get("uploaded_files", [])
                if uploaded_files:
                    print(f"✅ Upload successful: {uploaded_files[0].get('id')}")
                    return uploaded_files[0].get('id')
            else:
                print(f"❌ Upload failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Upload exception: {e}")
        
        return None
    
    def run_debug(self):
        """Run all debug tests"""
        print("🚀 DÉBUT DEBUG CAROUSEL ET ATTACHEMENT")
        print("=" * 80)
        
        if not self.authenticate():
            return
        
        # Debug content structure
        content_items = self.debug_content_structure()
        
        # Debug posts structure
        posts = self.debug_posts_structure()
        
        # Test upload
        uploaded_id = self.test_upload_debug()
        
        # Test image attachment if we have data
        if content_items and posts:
            # Find an image and a post
            image_items = [item for item in content_items if item.get('file_type', '').startswith('image')]
            posts_without_images = [p for p in posts if not p.get('visual_id')]
            
            if image_items and posts_without_images:
                self.test_image_attachment_debug(
                    posts_without_images[0]['id'],
                    image_items[0]['id']
                )

if __name__ == "__main__":
    debugger = ContentDebugger()
    debugger.run_debug()