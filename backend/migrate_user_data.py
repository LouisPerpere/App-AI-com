#!/usr/bin/env python3
"""
Script de migration des données utilisateur
Transfère toutes les données de l'ancien user_id vers le nouveau
"""

import os
from database import get_database
from datetime import datetime

# IDs utilisateur
OLD_USER_ID = "11d1e3d2-0223-4ddd-9407-74e0bb626818"  # Vrai owner_id trouvé dans les données
NEW_USER_ID = "bdf87a74-e3f3-44f3-bac2-649cde3ef93e"

# Aussi migrer les profils business sans owner_id
MIGRATE_NULL_OWNER_ID = True

def migrate_user_data():
    """Migre toutes les données de l'ancien vers le nouveau user_id"""
    print(f"🔄 Début de la migration des données...")
    print(f"   Ancien user_id: {OLD_USER_ID}")
    print(f"   Nouveau user_id: {NEW_USER_ID}")
    
    dbm = get_database()
    db = dbm.db
    
    collections_to_migrate = [
        "business_profiles",
        "media", 
        "content_notes",
        "website_analyses",
        "generated_posts",
        "thumbnails",
        "user_settings"
    ]
    
    total_migrated = 0
    
    for collection_name in collections_to_migrate:
        try:
            collection = db[collection_name]
            
            # Compter les documents à migrer
            count = collection.count_documents({"owner_id": OLD_USER_ID})
            if count == 0:
                print(f"   📂 {collection_name}: 0 documents - aucune migration nécessaire")
                continue
            
            # Migrer les documents
            result = collection.update_many(
                {"owner_id": OLD_USER_ID},
                {"$set": {"owner_id": NEW_USER_ID, "migrated_at": datetime.utcnow()}}
            )
            
            print(f"   ✅ {collection_name}: {result.modified_count} documents migrés")
            total_migrated += result.modified_count
            
        except Exception as e:
            print(f"   ❌ Erreur avec {collection_name}: {e}")
    
    # Migration spéciale pour les vignettes (utilise media_id)
    try:
        thumbs_collection = db["thumbnails"]
        
        # Trouver tous les media_ids de l'ancien utilisateur
        media_collection = db["media"]
        old_media = list(media_collection.find({"owner_id": OLD_USER_ID}, {"_id": 1, "id": 1}))
        
        migrated_thumbs = 0
        for media in old_media:
            media_id = media.get("_id") or media.get("id")
            if media_id:
                result = thumbs_collection.update_many(
                    {"media_id": media_id},
                    {"$set": {"migrated_at": datetime.utcnow()}}
                )
                migrated_thumbs += result.modified_count
        
        if migrated_thumbs > 0:
            print(f"   ✅ thumbnails (media_id): {migrated_thumbs} vignettes mises à jour")
            total_migrated += migrated_thumbs
        
    except Exception as e:
        print(f"   ⚠️ Erreur migration vignettes: {e}")
    
    print(f"\n🎉 Migration terminée ! {total_migrated} documents migrés au total")
    return total_migrated

if __name__ == "__main__":
    migrate_user_data()