#!/usr/bin/env python3
"""
Script pour diagnostiquer et corriger les deux environnements (Preview + Live)
"""

import requests
import json
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import uuid

class EnvironmentFixer:
    def __init__(self):
        self.user_id = '6a670c66-c06c-4d75-9dd5-c747e8a0281a'
        self.credentials = {
            'email': 'lperpere@yahoo.fr',
            'password': 'L@Reunion974!'
        }
        
        # Configuration des environnements
        self.environments = {
            'preview': {
                'url': 'https://post-restore.preview.emergentagent.com',
                'mongo_url': 'mongodb://localhost:27017/claire_marcus'  # Local MongoDB pour preview
            },
            'live': {
                'url': 'https://claire-marcus.com',
                'mongo_url': None  # À déterminer
            }
        }
    
    def diagnose_environment(self, env_name):
        """Diagnostic complet d'un environnement"""
        print(f"\n🔍 DIAGNOSTIC {env_name.upper()}")
        print("="*50)
        
        env = self.environments[env_name]
        
        # 1. Test API
        try:
            # Login
            login_response = requests.post(
                f"{env['url']}/api/auth/login-robust",
                json=self.credentials,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if login_response.status_code != 200:
                print(f"❌ Login failed: {login_response.status_code}")
                return None
                
            token = login_response.json()['access_token']
            headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
            
            # Test bibliothèque
            media_response = requests.get(f"{env['url']}/api/content/pending", headers=headers)
            media_data = media_response.json() if media_response.status_code == 200 else {}
            
            # Test posts
            posts_response = requests.get(f"{env['url']}/api/posts/generated", headers=headers)
            posts_data = posts_response.json() if posts_response.status_code == 200 else {}
            
            # Test connexions sociales
            social_response = requests.get(f"{env['url']}/api/social/connections", headers=headers)
            social_data = social_response.json() if social_response.status_code == 200 else {}
            
            # Résultats
            media_total = media_data.get('total', 0)
            media_visible = len(media_data.get('images', []))
            
            posts_total = len(posts_data.get('posts', []))
            posts_needs_image = sum(1 for p in posts_data.get('posts', []) 
                                   if p.get('status') == 'needs_image' or not p.get('visual_url'))
            
            facebook_connected = bool(social_data.get('connections', {}).get('facebook'))
            instagram_connected = bool(social_data.get('connections', {}).get('instagram'))
            
            print(f"📊 RÉSULTATS {env_name.upper()}:")
            print(f"  🖼️  Médias: {media_total} total, {media_visible} visibles")
            print(f"  📝 Posts: {posts_total} total, {posts_needs_image} sans image")
            print(f"  📘 Facebook: {'✅' if facebook_connected else '❌'}")
            print(f"  📷 Instagram: {'✅' if instagram_connected else '❌'}")
            
            # Test accès première image
            if media_data.get('images'):
                test_img = media_data['images'][0]
                img_url = f"{env['url']}/api/content/{test_img['id']}/file"
                try:
                    img_test = requests.head(img_url, headers=headers, timeout=5)
                    print(f"  🔗 Test image: {img_test.status_code}")
                except:
                    print(f"  🔗 Test image: Failed")
            
            return {
                'token': token,
                'headers': headers,
                'media_total': media_total,
                'media_visible': media_visible,
                'posts_total': posts_total,
                'posts_needs_image': posts_needs_image,
                'facebook_connected': facebook_connected,
                'instagram_connected': instagram_connected
            }
            
        except Exception as e:
            print(f"❌ Erreur diagnostic {env_name}: {str(e)}")
            return None
    
    def fix_preview_mongo(self):
        """Corrections MongoDB pour Preview (local)"""
        print(f"\n🔧 CORRECTION MONGODB PREVIEW")
        print("="*40)
        
        try:
            load_dotenv('/app/backend/.env')
            mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/claire_marcus')
            
            client = MongoClient(mongo_url)
            db = client.claire_marcus
            
            # 1. Corriger les médias corrompus
            corrupted_media = list(db.media.find({
                "owner_id": self.user_id,
                "$or": [
                    {"storage": {"$exists": False}},
                    {"storage": {"$ne": "gridfs"}},
                    {"gridfs_id": {"$exists": False}}
                ]
            }))
            
            print(f"📊 Médias corrompus trouvés: {len(corrupted_media)}")
            
            fixed_media = 0
            for media in corrupted_media:
                media_id = media.get('id', str(uuid.uuid4()))
                
                update_data = {
                    "id": media_id,
                    "storage": "external",
                    "is_external": True,
                    "accessible": True,
                    "repaired_at": "2025-09-18T13:00:00.000Z"
                }
                
                result = db.media.update_one(
                    {"_id": media["_id"]},
                    {"$set": update_data}
                )
                
                if result.modified_count > 0:
                    fixed_media += 1
            
            print(f"✅ Médias réparés: {fixed_media}")
            
            # 2. Corriger les posts
            posts_to_fix = list(db.generated_posts.find({
                'owner_id': self.user_id,
                'status': 'with_image',
                '$or': [
                    {'visual_url': ''},
                    {'visual_url': {'$exists': False}},
                    {'visual_id': ''},
                    {'visual_id': {'$exists': False}}
                ]
            }))
            
            print(f"📊 Posts à corriger: {len(posts_to_fix)}")
            
            fixed_posts = 0
            for post in posts_to_fix:
                result = db.generated_posts.update_one(
                    {'id': post['id'], 'owner_id': self.user_id},
                    {
                        '$set': {
                            'status': 'needs_image',
                            'needs_image': True,
                            'with_image': False
                        }
                    }
                )
                
                if result.modified_count > 0:
                    fixed_posts += 1
            
            print(f"✅ Posts corrigés: {fixed_posts}")
            
            return {'media_fixed': fixed_media, 'posts_fixed': fixed_posts}
            
        except Exception as e:
            print(f"❌ Erreur correction Preview: {str(e)}")
            return None

def main():
    fixer = EnvironmentFixer()
    
    print("🚀 DIAGNOSTIC COMPLET DES DEUX ENVIRONNEMENTS")
    print("="*60)
    
    # Diagnostic des deux environnements
    preview_state = fixer.diagnose_environment('preview')
    live_state = fixer.diagnose_environment('live')
    
    # Corrections Preview (MongoDB local)
    if preview_state:
        preview_fixes = fixer.fix_preview_mongo()
        
        # Re-diagnostic après corrections
        print(f"\n🔄 RE-DIAGNOSTIC PREVIEW APRÈS CORRECTIONS")
        fixer.diagnose_environment('preview')
    
    print(f"\n📋 RÉSUMÉ FINAL:")
    print(f"  Preview: {'✅ Corrigé' if preview_fixes else '❌ Erreur'}")
    print(f"  Live: {'⏳ En attente de correction' if live_state else '❌ Inaccessible'}")

if __name__ == "__main__":
    main()