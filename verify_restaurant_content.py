#!/usr/bin/env python3
"""
VERIFICATION - Vérifier la présence du contenu restaurant créé sur l'environnement LIVE
"""

import requests
import json
import sys
from datetime import datetime

# CONFIGURATION CRITIQUE - ENVIRONNEMENT LIVE UNIQUEMENT
LIVE_BASE_URL = "https://claire-marcus.com/api"
TEST_EMAIL = "test@claire-marcus.com"
TEST_PASSWORD = "test123!"

class ContentVerifier:
    def __init__(self):
        self.base_url = LIVE_BASE_URL
        self.token = None
        self.user_id = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Claire-Marcus-Content-Verifier/1.0'
        })
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def authenticate(self):
        """Authentification sur l'environnement LIVE"""
        self.log("🔐 Authenticating on LIVE environment")
        
        try:
            response = self.session.post(f"{self.base_url}/auth/login-robust", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token')
                self.user_id = data.get('user_id')
                
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}'
                })
                
                self.log(f"✅ Authentication successful - User ID: {self.user_id}")
                return True
            else:
                self.log(f"❌ Authentication failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Authentication error: {str(e)}", "ERROR")
            return False
    
    def verify_business_profile(self):
        """Vérifier le profil business"""
        self.log("🏪 Verifying Business Profile")
        
        try:
            response = self.session.get(f"{self.base_url}/business-profile")
            
            if response.status_code == 200:
                data = response.json()
                business_name = data.get('business_name')
                industry = data.get('industry')
                website_url = data.get('website_url')
                
                self.log(f"✅ Business Profile Found:")
                self.log(f"   Name: {business_name}")
                self.log(f"   Industry: {industry}")
                self.log(f"   Website: {website_url}")
                
                if business_name == "Le Bistrot de Jean":
                    return True
                else:
                    self.log("❌ Business name mismatch", "ERROR")
                    return False
            else:
                self.log(f"❌ Business profile not found: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Business profile verification error: {str(e)}", "ERROR")
            return False
    
    def verify_content_notes(self):
        """Vérifier les notes/contenus créés"""
        self.log("📝 Verifying Content Notes")
        
        try:
            response = self.session.get(f"{self.base_url}/notes")
            
            if response.status_code == 200:
                data = response.json()
                notes = data.get('notes', [])
                
                # Analyze notes
                restaurant_notes = []
                website_analyses = []
                october_posts = []
                november_posts = []
                
                for note in notes:
                    note_content = str(note)
                    note_description = note.get('description', '')
                    
                    if 'Le Bistrot de Jean' in note_content or 'bistrotdejean' in note_content:
                        restaurant_notes.append(note)
                    
                    if 'website_analysis' in note_content or 'lebistrotdejean-paris.fr' in note_content:
                        website_analyses.append(note)
                    
                    if 'octobre' in note_content.lower() or 'october' in note_content.lower():
                        october_posts.append(note)
                    
                    if 'novembre' in note_content.lower() or 'november' in note_content.lower():
                        november_posts.append(note)
                
                self.log(f"📊 Content Analysis:")
                self.log(f"   Total notes: {len(notes)}")
                self.log(f"   Restaurant-related: {len(restaurant_notes)}")
                self.log(f"   Website analyses: {len(website_analyses)}")
                self.log(f"   October posts: {len(october_posts)}")
                self.log(f"   November posts: {len(november_posts)}")
                
                # Detailed verification
                if website_analyses:
                    self.log("✅ Website Analysis Found:")
                    for analysis in website_analyses[:1]:  # Show first one
                        self.log(f"   Description: {analysis.get('description', 'N/A')}")
                        try:
                            content = json.loads(analysis.get('content', '{}'))
                            seo_score = content.get('seo_score', 'N/A')
                            self.log(f"   SEO Score: {seo_score}/100")
                        except:
                            pass
                
                if october_posts:
                    self.log("✅ October Posts Found:")
                    for post in october_posts[:2]:  # Show first 2
                        self.log(f"   - {post.get('description', 'N/A')}")
                
                if november_posts:
                    self.log("✅ November Posts Found:")
                    for post in november_posts[:2]:  # Show first 2
                        self.log(f"   - {post.get('description', 'N/A')}")
                
                # Success criteria
                success = (
                    len(website_analyses) >= 1 and
                    len(october_posts) >= 4 and
                    len(november_posts) >= 4
                )
                
                if success:
                    self.log("✅ All required content verified successfully")
                else:
                    self.log("❌ Some required content missing", "ERROR")
                
                return success
                
            else:
                self.log(f"❌ Notes retrieval failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Content verification error: {str(e)}", "ERROR")
            return False
    
    def run_verification(self):
        """Run complete verification"""
        self.log("🚀 STARTING CONTENT VERIFICATION ON LIVE ENVIRONMENT")
        self.log("=" * 60)
        
        results = {
            'authentication': False,
            'business_profile': False,
            'content_notes': False
        }
        
        if self.authenticate():
            results['authentication'] = True
            
            if self.verify_business_profile():
                results['business_profile'] = True
            
            if self.verify_content_notes():
                results['content_notes'] = True
        
        # Summary
        self.log("=" * 60)
        self.log("🎯 VERIFICATION SUMMARY")
        
        passed_tests = sum(results.values())
        total_tests = len(results)
        success_rate = (passed_tests / total_tests) * 100
        
        self.log(f"📊 Results: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)")
        
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            self.log(f"   {test_name.replace('_', ' ').title()}: {status}")
        
        if passed_tests == total_tests:
            self.log("\n🎉 VERIFICATION SUCCESSFUL - All restaurant content is present on LIVE!")
        else:
            self.log("\n❌ VERIFICATION FAILED - Some content is missing")
        
        return results

def main():
    verifier = ContentVerifier()
    results = verifier.run_verification()
    
    if all(results.values()):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()