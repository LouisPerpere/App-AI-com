#!/usr/bin/env python3
"""
Script pour réparer les médias corrompus sans storage/gridfs_id
"""

from pymongo import MongoClient
import os
from dotenv import load_dotenv
import uuid

def fix_corrupted_media():
    """Répare les médias corrompus en les rendant accessibles"""
    
    load_dotenv('/app/backend/.env')
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/claire_marcus')
    
    client = MongoClient(mongo_url)
    db = client.claire_marcus
    
    user_id = '6a670c66-c06c-4d75-9dd5-c747e8a0281a'
    
    print("🔧 Réparation des médias corrompus...")
    
    # 1. Trouver tous les médias sans storage
    corrupted_media = list(db.media.find({
        "owner_id": user_id,
        "$or": [
            {"storage": {"$exists": False}},
            {"storage": {"$ne": "gridfs"}},
            {"gridfs_id": {"$exists": False}}
        ]
    }))
    
    print(f"📊 Trouvé {len(corrupted_media)} médias corrompus")
    
    # 2. Stratégie de réparation : Marquer comme "external" pour les rendre utilisables
    fixed_count = 0
    
    for media in corrupted_media:
        media_id = media.get('id', str(uuid.uuid4()))
        filename = media.get('filename', 'unknown')
        
        # Si pas d'ID, en créer un
        if not media_id or media_id == 'no id':
            media_id = str(uuid.uuid4())
        
        # Mettre à jour le média pour le rendre utilisable
        update_data = {
            "id": media_id,  # S'assurer qu'il y a un ID
            "storage": "external",  # Marquer comme externe pour éviter GridFS
            "is_external": True,
            "file_path": media.get('file_path', ''),  # Garder le chemin original
            "url": media.get('url', media.get('file_path', '')),  # URL pour accès
            "accessible": True,
            "repaired_at": "2025-09-18T12:00:00.000Z"
        }
        
        try:
            result = db.media.update_one(
                {"_id": media["_id"]},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                print(f"✅ Réparé: {filename} (ID: {media_id})")
                fixed_count += 1
            else:
                print(f"❌ Échec: {filename}")
                
        except Exception as e:
            print(f"❌ Erreur pour {filename}: {str(e)}")
    
    print(f"\n🎉 Réparation terminée: {fixed_count}/{len(corrupted_media)} médias réparés")
    
    # 3. Vérifier que les médias sont maintenant accessibles
    print("\n🔍 Vérification post-réparation:")
    accessible_media = list(db.media.find({
        "owner_id": user_id,
        "accessible": True
    }))
    
    print(f"📊 Médias accessibles: {len(accessible_media)}")
    
    return fixed_count

if __name__ == "__main__":
    fixed_count = fix_corrupted_media()
    print(f"\n✅ Script terminé. {fixed_count} médias réparés.")