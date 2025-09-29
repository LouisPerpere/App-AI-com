#!/usr/bin/env python3
"""
🎯 DIAGNOSTIC SPÉCIFIQUE FACEBOOK IMAGES - CAPTURE LOGS DÉTAILLÉS
Diagnostic approfondi pour identifier si la conversion JPG fonctionne sur LIVE

Identifiants: lperpere@yahoo.fr / L@Reunion974!
ENVIRONNEMENT: LIVE (claire-marcus.com)
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration LIVE
LIVE_BACKEND_URL = "https://claire-marcus.com/api"
CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class FacebookImageDiagnostic:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Facebook-Image-Diagnostic/1.0'
        })
        self.access_token = None
        self.user_id = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def authenticate(self):
        """Authenticate and get token"""
        self.log("🔐 Authenticating on LIVE environment...")
        
        try:
            response = self.session.post(
                f"{LIVE_BACKEND_URL}/auth/login-robust",
                json=CREDENTIALS,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                self.user_id = data.get('user_id')
                
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                
                self.log(f"✅ Authentication successful")
                self.log(f"   User ID: {self.user_id}")
                return True
            else:
                self.log(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ Authentication error: {str(e)}", "ERROR")
            return False
            
    def test_facebook_image_publication_detailed(self):
        """Test Facebook image publication with detailed logging"""
        self.log("🖼️ DETAILED Facebook image publication test")
        
        # Get posts with images
        try:
            response = self.session.get(
                f"{LIVE_BACKEND_URL}/posts/generated",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('posts', [])
                
                # Find Facebook posts with images
                facebook_posts_with_images = []
                for p in posts:
                    if (p.get('platform') == 'facebook' and 
                        (p.get('visual_url') or p.get('visual_id'))):
                        facebook_posts_with_images.append(p)
                
                self.log(f"   Found {len(facebook_posts_with_images)} Facebook posts with images")
                
                if facebook_posts_with_images:
                    test_post = facebook_posts_with_images[0]
                    post_id = test_post.get('id')
                    visual_url = test_post.get('visual_url', '')
                    visual_id = test_post.get('visual_id', '')
                    
                    self.log(f"   Testing post: {post_id}")
                    self.log(f"   Visual URL: {visual_url}")
                    self.log(f"   Visual ID: {visual_id}")
                    
                    # Test image accessibility first
                    if visual_url and visual_url.startswith('/'):
                        full_image_url = f"https://claire-marcus.com{visual_url}"
                        
                        try:
                            img_response = self.session.get(full_image_url, timeout=10)
                            self.log(f"   Image accessibility: {img_response.status_code}")
                            
                            if img_response.status_code == 200:
                                content_type = img_response.headers.get('content-type', '')
                                content_length = img_response.headers.get('content-length', '0')
                                self.log(f"   Image Content-Type: {content_type}")
                                self.log(f"   Image Size: {content_length} bytes")
                                
                                # Check if it's JPG
                                if 'jpeg' in content_type or 'jpg' in content_type:
                                    self.log(f"   ✅ Image is in JPG format")
                                else:
                                    self.log(f"   ⚠️ Image is NOT in JPG format: {content_type}")
                            else:
                                self.log(f"   ❌ Image not accessible: {img_response.status_code}")
                                
                        except Exception as e:
                            self.log(f"   ❌ Image test error: {str(e)}")
                    
                    # Now test publication
                    self.log("   🚀 Starting Facebook publication...")
                    
                    try:
                        pub_response = self.session.post(
                            f"{LIVE_BACKEND_URL}/posts/publish",
                            json={"post_id": post_id},
                            timeout=30
                        )
                        
                        self.log(f"   Publication response: {pub_response.status_code}")
                        
                        if pub_response.status_code in [200, 400, 500]:
                            try:
                                pub_data = pub_response.json()
                                
                                # Detailed response analysis
                                if pub_response.status_code == 200:
                                    self.log(f"   ✅ PUBLICATION SUCCESSFUL!")
                                    message = pub_data.get('message', '')
                                    if message:
                                        self.log(f"      Success message: {message}")
                                        
                                    # Look for Facebook-specific info
                                    facebook_post_id = pub_data.get('facebook_post_id', '')
                                    if facebook_post_id:
                                        self.log(f"      Facebook Post ID: {facebook_post_id}")
                                        
                                else:
                                    self.log(f"   ❌ PUBLICATION FAILED")
                                    error = pub_data.get('error', '')
                                    if error:
                                        self.log(f"      Error: {error}")
                                        
                                        # Analyze error for image-specific issues
                                        if 'image' in error.lower():
                                            self.log(f"      🔍 IMAGE-RELATED ERROR DETECTED")
                                        elif 'jpg' in error.lower() or 'jpeg' in error.lower():
                                            self.log(f"      🔍 JPG CONVERSION ERROR DETECTED")
                                        elif 'facebook' in error.lower():
                                            self.log(f"      🔍 FACEBOOK API ERROR DETECTED")
                                        elif 'token' in error.lower():
                                            self.log(f"      🔍 TOKEN ERROR")
                                        elif 'connexion' in error.lower():
                                            self.log(f"      🔍 CONNECTION ERROR")
                                
                                # Look for conversion logs in response
                                response_str = str(pub_data)
                                if 'conversion' in response_str.lower():
                                    self.log(f"      ✅ JPG conversion mentioned in response")
                                if 'binary' in response_str.lower():
                                    self.log(f"      ✅ Binary upload mentioned in response")
                                if 'Facebook JPG Upload' in response_str:
                                    self.log(f"      ✅ Facebook JPG Upload process detected")
                                if 'Conversion JPG réussie' in response_str:
                                    self.log(f"      ✅ JPG conversion successful")
                                if 'Envoi à Facebook' in response_str:
                                    self.log(f"      ✅ Facebook upload process detected")
                                    
                                return pub_response.status_code == 200
                                
                            except Exception as e:
                                self.log(f"      Raw response: {pub_response.text[:500]}")
                                return False
                        else:
                            self.log(f"   ❌ Unexpected status code: {pub_response.status_code}")
                            return False
                            
                    except Exception as e:
                        self.log(f"   ❌ Publication error: {str(e)}", "ERROR")
                        return False
                else:
                    self.log(f"   ⚠️ No Facebook posts with images found")
                    return False
                    
            else:
                self.log(f"   ❌ Failed to get posts: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"   ❌ Posts retrieval error: {str(e)}", "ERROR")
            return False
            
    def run_diagnostic(self):
        """Run complete Facebook image diagnostic"""
        self.log("🚀 STARTING FACEBOOK IMAGE DIAGNOSTIC ON LIVE")
        self.log("=" * 60)
        
        if not self.authenticate():
            self.log("❌ CRITICAL: Authentication failed", "ERROR")
            return False
            
        # Run diagnostic tests
        self.log("")
        publication_success = self.test_facebook_image_publication_detailed()
        
        # Summary
        self.log("")
        self.log("=" * 60)
        self.log("📊 DIAGNOSTIC SUMMARY:")
        
        if publication_success:
            self.log("✅ Facebook image publication: SUCCESS")
            self.log("   → Images are being published successfully to Facebook")
            self.log("   → The issue may be resolved or was environment-specific")
        else:
            self.log("❌ Facebook image publication: FAILED")
            self.log("   → Images are not being published to Facebook")
            self.log("   → JPG conversion or Facebook API integration issue")
            
        return publication_success

if __name__ == "__main__":
    diagnostic = FacebookImageDiagnostic()
    success = diagnostic.run_diagnostic()
    
    if success:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure