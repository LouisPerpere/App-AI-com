#!/usr/bin/env python3
"""
Script pour corriger l'environnement LIVE via API calls
"""

import requests
import json
import time

class LiveEnvironmentFixer:
    def __init__(self):
        self.live_url = 'https://claire-marcus.com'
        self.user_id = '6a670c66-c06c-4d75-9dd5-c747e8a0281a'
        self.credentials = {
            'email': 'lperpere@yahoo.fr',
            'password': 'L@Reunion974!'
        }
        self.token = None
        self.headers = None
    
    def login(self):
        """Login sur l'environnement live"""
        try:
            response = requests.post(
                f"{self.live_url}/api/auth/login-robust",
                json=self.credentials,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data['access_token']
                self.headers = {
                    'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/json'
                }
                print("✅ Login LIVE réussi")
                return True
            else:
                print(f"❌ Login LIVE échec: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur login LIVE: {str(e)}")
            return False
    
    def check_endpoints_exist(self):
        """Vérifier que les endpoints de correction existent sur LIVE"""
        endpoints_to_check = [
            '/api/posts/clear-cache',
            '/api/posts/generated'
        ]
        
        results = {}
        
        for endpoint in endpoints_to_check:
            try:
                response = requests.get(f"{self.live_url}{endpoint}", headers=self.headers, timeout=5)
                results[endpoint] = response.status_code
                print(f"  {endpoint}: {response.status_code}")
            except Exception as e:
                results[endpoint] = f"Error: {str(e)[:50]}"
                print(f"  {endpoint}: Error - {str(e)[:50]}")
        
        return results
    
    def fix_posts_status(self):
        """Corriger les posts avec status incorrect via API"""
        print("\n🔧 CORRECTION POSTS LIVE")
        print("="*30)
        
        try:
            # Obtenir tous les posts
            posts_response = requests.get(f"{self.live_url}/api/posts/generated", headers=self.headers)
            
            if posts_response.status_code != 200:
                print(f"❌ Erreur récupération posts: {posts_response.status_code}")
                return False
            
            posts = posts_response.json().get('posts', [])
            print(f"📊 Posts trouvés: {len(posts)}")
            
            posts_to_fix = []
            
            for post in posts:
                visual_url = post.get('visual_url', '')
                status = post.get('status', '')
                
                # Si le post a une visual_url mais l'image n'est pas accessible
                if visual_url and status == 'with_image':
                    # Test si l'image est accessible
                    img_url = f"{self.live_url}{visual_url}"
                    try:
                        img_test = requests.head(img_url, headers=self.headers, timeout=3)
                        if img_test.status_code not in [200, 302]:
                            posts_to_fix.append(post)
                    except:
                        posts_to_fix.append(post)
            
            print(f"📊 Posts à corriger: {len(posts_to_fix)}")
            
            # Créer un endpoint de correction de batch si nécessaire
            # Pour l'instant, on ne peut pas modifier les posts directement via API
            # car il n'y a pas d'endpoint pour ça
            
            print("⚠️ Correction posts nécessite l'endpoint de correction backend")
            return {'posts_identified': len(posts_to_fix), 'posts_fixed': 0}
            
        except Exception as e:
            print(f"❌ Erreur correction posts: {str(e)}")
            return False
    
    def test_image_access(self):
        """Tester l'accès aux images via différentes méthodes"""
        print("\n🧪 TEST ACCÈS IMAGES LIVE")
        print("="*30)
        
        try:
            # Obtenir quelques images
            media_response = requests.get(f"{self.live_url}/api/content/pending?limit=3", headers=self.headers)
            
            if media_response.status_code != 200:
                print(f"❌ Erreur récupération média: {media_response.status_code}")
                return False
            
            images = media_response.json().get('images', [])
            print(f"📊 Images à tester: {len(images)}")
            
            for i, img in enumerate(images):
                img_id = img.get('id')
                img_name = img.get('filename', 'unknown')
                
                # Test différentes URLs
                test_urls = [
                    f"{self.live_url}/api/content/{img_id}/file",
                    f"{self.live_url}/api/content/{img_id}/thumb"
                ]
                
                print(f"  {i+1}. {img_name}:")
                
                for url in test_urls:
                    try:
                        response = requests.head(url, headers=self.headers, timeout=3)
                        print(f"    {url.split('/')[-1]}: {response.status_code}")
                    except Exception as e:
                        print(f"    {url.split('/')[-1]}: Error")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur test images: {str(e)}")
            return False
    
    def clear_cache(self):
        """Essayer de vider le cache"""
        print("\n🧹 NETTOYAGE CACHE LIVE")
        print("="*25)
        
        try:
            # Test si l'endpoint existe
            cache_response = requests.post(f"{self.live_url}/api/posts/clear-cache", headers=self.headers)
            
            print(f"Clear cache status: {cache_response.status_code}")
            
            if cache_response.status_code == 200:
                data = cache_response.json()
                print(f"✅ Cache nettoyé: {data}")
                return True
            else:
                print(f"⚠️ Endpoint clear-cache: {cache_response.text[:100]}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur nettoyage cache: {str(e)}")
            return False

def main():
    print("🔴 CORRECTION ENVIRONNEMENT LIVE")
    print("="*50)
    
    fixer = LiveEnvironmentFixer()
    
    # Login
    if not fixer.login():
        print("❌ Impossible de continuer sans login")
        return
    
    # Vérifier les endpoints
    print("\n📋 VÉRIFICATION ENDPOINTS:")
    fixer.check_endpoints_exist()
    
    # Test accès images
    fixer.test_image_access()
    
    # Correction posts
    fixer.fix_posts_status()
    
    # Nettoyage cache
    fixer.clear_cache()
    
    print("\n📋 RÉSUMÉ LIVE:")
    print("  ⚠️ Corrections limitées par l'absence d'endpoints de correction")
    print("  💡 Solution: Déployer les corrections backend sur LIVE")

if __name__ == "__main__":
    main()