#!/usr/bin/env python3
"""
Test curl manual des URLs publiques d'images selon recommandations ChatGPT
Focus sur l'accessibilité des URLs d'images pour Facebook

Credentials: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://social-publisher-10.preview.emergentagent.com/api"
FRONTEND_URL = "https://social-publisher-10.preview.emergentagent.com"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

# Images de référence externes
EXTERNAL_IMAGES = {
    "wikimedia": "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png",
    "pixabay": "https://cdn.pixabay.com/photo/2016/11/29/05/45/astronomy-1867616_960_720.jpg"
}

class CurlImageTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        
    def authenticate(self):
        """Authenticate and get JWT token"""
        try:
            print("🔐 Authentication...")
            response = self.session.post(
                f"{BASE_URL}/auth/login-robust",
                json=TEST_CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                print(f"✅ Authenticated as user: {self.user_id}")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def get_sample_image(self):
        """Get a sample image from the system"""
        try:
            print("\n📷 Getting sample image from system...")
            response = self.session.get(f"{BASE_URL}/content/pending?limit=5", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                
                # Find first image
                for item in content_items:
                    if item.get("file_type", "").startswith("image"):
                        print(f"✅ Found image: ID={item.get('id')}, URL={item.get('url')}")
                        return item
                
                print("❌ No images found in content")
                return None
            else:
                print(f"❌ Failed to get content: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting sample image: {e}")
            return None
    
    def test_curl_public_url(self, image_id):
        """Test curl manual de l'URL publique"""
        print(f"\n🔧 Test curl manual pour image {image_id}")
        
        public_url = f"{FRONTEND_URL}/api/public/image/{image_id}"
        print(f"URL publique testée: {public_url}")
        
        try:
            # Test sans authentification (comme Facebook le ferait)
            curl_session = requests.Session()
            response = curl_session.get(public_url, timeout=30, allow_redirects=True)
            
            print(f"Status Code: {response.status_code}")
            print("Headers HTTP:")
            important_headers = ['content-type', 'content-length', 'cache-control', 'access-control-allow-origin', 'location']
            for header in important_headers:
                value = response.headers.get(header, 'Not set')
                print(f"  {header}: {value}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                print(f"✅ Image accessible: Type={content_type}, Size={content_length} bytes")
                return True
            elif response.status_code == 302:
                location = response.headers.get('location', '')
                print(f"📍 Redirection vers: {location}")
                return True
            else:
                print(f"❌ Image non accessible: Status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur curl: {e}")
            return False
    
    def test_external_image_reference(self, name, url):
        """Test image externe de référence"""
        print(f"\n🌍 Test image externe {name}")
        print(f"URL: {url}")
        
        try:
            response = requests.get(url, timeout=30)
            
            print(f"Status Code: {response.status_code}")
            print("Headers HTTP:")
            important_headers = ['content-type', 'content-length', 'cache-control', 'access-control-allow-origin']
            for header in important_headers:
                value = response.headers.get(header, 'Not set')
                print(f"  {header}: {value}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                print(f"✅ Image externe accessible: Type={content_type}, Size={content_length} bytes")
                return True
            else:
                print(f"❌ Image externe non accessible: Status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur test externe: {e}")
            return False
    
    def compare_headers(self, internal_url, external_url):
        """Comparer les headers entre image interne et externe"""
        print(f"\n🔍 Comparaison headers internes vs externes")
        
        try:
            # Test image interne
            internal_response = requests.get(internal_url, timeout=30, allow_redirects=True)
            
            # Test image externe
            external_response = requests.get(external_url, timeout=30)
            
            print("COMPARAISON HEADERS:")
            print("-" * 50)
            
            important_headers = ['content-type', 'content-length', 'cache-control', 'access-control-allow-origin', 'server']
            
            for header in important_headers:
                internal_value = internal_response.headers.get(header, 'Not set')
                external_value = external_response.headers.get(header, 'Not set')
                
                match = "✅" if internal_value == external_value else "❌"
                print(f"{header}:")
                print(f"  Interne:  {internal_value}")
                print(f"  Externe:  {external_value}")
                print(f"  Match: {match}")
                print()
            
            # Analyser les différences critiques
            internal_ct = internal_response.headers.get('content-type', '')
            external_ct = external_response.headers.get('content-type', '')
            
            if internal_ct.startswith('image/') and external_ct.startswith('image/'):
                print("✅ Les deux retournent des images valides")
                return True
            else:
                print(f"❌ Problème content-type: Interne={internal_ct}, Externe={external_ct}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur comparaison: {e}")
            return False
    
    def run_curl_tests(self):
        """Run all curl tests"""
        print("🎯 TEST CURL MANUAL DES URLs PUBLIQUES IMAGES")
        print("=" * 60)
        print(f"Backend URL: {BASE_URL}")
        print(f"Frontend URL: {FRONTEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed - cannot continue")
            return False
        
        # Step 2: Get sample image
        sample_image = self.get_sample_image()
        if not sample_image:
            print("❌ No sample image available - cannot test internal URLs")
            return False
        
        image_id = sample_image.get('id')
        internal_public_url = f"{FRONTEND_URL}/api/public/image/{image_id}"
        
        # Step 3: Test curl manual de l'URL publique interne
        internal_success = self.test_curl_public_url(image_id)
        
        # Step 4: Test images externes de référence
        external_results = {}
        for name, url in EXTERNAL_IMAGES.items():
            external_results[name] = self.test_external_image_reference(name, url)
        
        # Step 5: Comparaison headers
        if internal_success and external_results.get('wikimedia'):
            self.compare_headers(internal_public_url, EXTERNAL_IMAGES['wikimedia'])
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ TEST CURL MANUAL")
        print("=" * 60)
        
        print(f"Image interne testée: {image_id}")
        print(f"URL publique: {internal_public_url}")
        print(f"Accessibilité interne: {'✅ OK' if internal_success else '❌ FAIL'}")
        
        print("\nImages externes de référence:")
        for name, success in external_results.items():
            print(f"  {name}: {'✅ OK' if success else '❌ FAIL'}")
        
        # Diagnostic final
        print("\n🔍 DIAGNOSTIC FINAL:")
        if internal_success:
            print("✅ Les URLs publiques internes sont accessibles")
            print("✅ Le problème n'est PAS l'accessibilité des URLs")
            print("💡 Le problème Facebook est probablement lié aux tokens OAuth invalides")
        else:
            print("❌ Les URLs publiques internes ne sont PAS accessibles")
            print("💡 C'est probablement la cause du problème Facebook")
            print("🔧 Vérifier l'implémentation de /api/public/image/{id}")
        
        all_external_ok = all(external_results.values())
        if all_external_ok:
            print("✅ Les images externes de référence sont accessibles")
        else:
            print("⚠️ Problème avec les images externes de référence")
        
        return internal_success

def main():
    """Main execution"""
    tester = CurlImageTester()
    success = tester.run_curl_tests()
    
    if success:
        print("\n✅ Test curl manual terminé avec succès!")
        sys.exit(0)
    else:
        print("\n❌ Test curl manual a révélé des problèmes!")
        sys.exit(1)

if __name__ == "__main__":
    main()