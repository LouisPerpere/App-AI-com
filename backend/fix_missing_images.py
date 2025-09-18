#!/usr/bin/env python3
"""
Script pour corriger les posts avec des images manquantes/corrompues
"""

from pymongo import MongoClient
import os
from dotenv import load_dotenv

def fix_missing_images():
    """Corrige les posts avec des images manquantes"""
    
    load_dotenv('/app/backend/.env')
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/claire_marcus')
    
    client = MongoClient(mongo_url)
    db = client.claire_marcus
    
    user_id = '6a670c66-c06c-4d75-9dd5-c747e8a0281a'
    
    print("🔧 Starting image fix process...")
    
    # 1. Trouver tous les posts de l'utilisateur
    posts = list(db.generated_posts.find({"owner_id": user_id}))
    print(f"📊 Found {len(posts)} posts to analyze")
    
    # 2. Vérifier chaque post
    posts_to_fix = []
    
    for post in posts:
        visual_id = post.get('visual_id', '')
        visual_url = post.get('visual_url', '')
        
        if visual_id and visual_url:
            # Vérifier si le media existe et a un stockage GridFS valide
            media = db.media.find_one({'id': visual_id, 'owner_id': user_id})
            
            if not media:
                print(f"❌ Post {post.get('id', 'unknown')}: Media {visual_id} not found")
                posts_to_fix.append(post)
            elif media.get('storage') != 'gridfs' or not media.get('gridfs_id'):
                print(f"⚠️ Post {post.get('id', 'unknown')}: Media {visual_id} missing GridFS storage")
                posts_to_fix.append(post)
            else:
                print(f"✅ Post {post.get('id', 'unknown')}: Media {visual_id} OK")
    
    print(f"\n🔧 Found {len(posts_to_fix)} posts needing fixes")
    
    # 3. Corriger les posts problématiques
    fixed_count = 0
    
    for post in posts_to_fix:
        post_id = post.get('id', 'unknown')
        
        # Remettre le post à "sans image"
        update_result = db.generated_posts.update_one(
            {"id": post_id, "owner_id": user_id},
            {
                "$unset": {
                    "visual_id": "",
                    "visual_url": ""
                },
                "$set": {
                    "needs_image": True,
                    "with_image": False,
                    "status": "needs_image",  # CORRECTION: Changer le status
                    "fixed_at": "2025-09-18T11:30:00.000Z"
                }
            }
        )
        
        if update_result.modified_count > 0:
            print(f"✅ Fixed post {post_id} - removed corrupted image references")
            fixed_count += 1
        else:
            print(f"❌ Failed to fix post {post_id}")
    
    print(f"\n🎉 Fix completed: {fixed_count}/{len(posts_to_fix)} posts fixed")
    
    # 4. Nettoyer les médias orphelins (optionnel)
    orphan_media = list(db.media.find({
        "owner_id": user_id,
        "$or": [
            {"storage": {"$ne": "gridfs"}},
            {"gridfs_id": {"$exists": False}}
        ]
    }))
    
    print(f"\n🧹 Found {len(orphan_media)} orphan media documents")
    for media in orphan_media[:3]:  # Show first 3
        print(f"   - {media.get('id', 'no_id')}: {media.get('filename', 'no_filename')}")
    
    return fixed_count

if __name__ == "__main__":
    fixed_count = fix_missing_images()
    print(f"\n✅ Process completed. {fixed_count} posts fixed.")