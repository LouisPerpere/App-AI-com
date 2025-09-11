#!/usr/bin/env python3
"""
Script pour migrer les photos de l'environnement preview vers production
L'utilisateur lperpere@yahoo.fr a deux user_id différents:
- Preview: bdf87a74-e3f3-44f3-bac2-649cde3ef93e
- Production: 6a670c66-c06c-4d75-9dd5-c747e8a0281a

Ce script migre tous les contenus média de preview vers production.
"""
import os
import sys
sys.path.append('/app/backend')

from database import get_database
from datetime import datetime
import requests
import uuid

def migrate_photos_to_production():
    """Migrer les photos de preview vers production"""
    
    # IDs utilisateur
    PREVIEW_USER_ID = "bdf87a74-e3f3-44f3-bac2-649cde3ef93e"
    PRODUCTION_USER_ID = "6a670c66-c06c-4d75-9dd5-c747e8a0281a"
    
    print("🔄 MIGRATION DES PHOTOS PREVIEW → PRODUCTION")
    print(f"📤 Source (Preview): {PREVIEW_USER_ID}")
    print(f"📥 Destination (Production): {PRODUCTION_USER_ID}")
    print("="*60)
    
    # Connexion à la base de données
    db_manager = get_database()
    db = db_manager.db
    
    # Compter les contenus existants
    preview_count = db.media.count_documents({"owner_id": PREVIEW_USER_ID})
    production_count = db.media.count_documents({"owner_id": PRODUCTION_USER_ID})
    
    print(f"📊 État initial:")
    print(f"   - Contenus Preview: {preview_count}")
    print(f"   - Contenus Production: {production_count}")
    
    if preview_count == 0:
        print("❌ Aucun contenu à migrer depuis preview")
        return
    
    # Récupérer tous les contenus de preview
    preview_contents = list(db.media.find({"owner_id": PREVIEW_USER_ID}))
    
    print(f"\n🔍 Analyse des contenus preview:")
    for i, content in enumerate(preview_contents[:5], 1):  # Afficher les 5 premiers
        print(f"   {i}. {content.get('filename', 'Sans nom')} - {content.get('title', 'Sans titre')}")
    
    if len(preview_contents) > 5:
        print(f"   ... et {len(preview_contents) - 5} autres")
    
    # Migration automatique (demandée par l'utilisateur)
    print(f"\n⚠️  Migration automatique de {len(preview_contents)} contenus vers production")
    
    print(f"\n🚀 Début de la migration...")
    
    migrated_count = 0
    errors = []
    
    for content in preview_contents:
        try:
            # Créer une copie du contenu avec le nouvel owner_id
            new_content = content.copy()
            
            # Changer l'owner_id
            new_content["owner_id"] = PRODUCTION_USER_ID
            
            # Générer un nouvel ID si nécessaire pour éviter les conflits
            if "_id" in new_content:
                del new_content["_id"]  # MongoDB générera un nouveau _id
            
            # Ajouter timestamp migration
            new_content["migrated_at"] = datetime.utcnow().isoformat()
            new_content["migrated_from"] = PREVIEW_USER_ID
            
            # Insérer dans production
            result = db.media.insert_one(new_content)
            
            print(f"   ✅ Migré: {content.get('filename', 'Sans nom')} → {result.inserted_id}")
            migrated_count += 1
            
        except Exception as e:
            error_msg = f"Erreur migration {content.get('filename', 'inconnu')}: {str(e)}"
            print(f"   ❌ {error_msg}")
            errors.append(error_msg)
    
    print(f"\n📊 Résultats de la migration:")
    print(f"   ✅ Contenus migrés: {migrated_count}")
    print(f"   ❌ Erreurs: {len(errors)}")
    
    if errors:
        print(f"\n🔍 Détails des erreurs:")
        for error in errors[:5]:  # Afficher les 5 premières erreurs
            print(f"   - {error}")
    
    # Vérifier l'état final
    final_production_count = db.media.count_documents({"owner_id": PRODUCTION_USER_ID})
    print(f"\n🎯 État final:")
    print(f"   - Contenus Production: {final_production_count}")
    print(f"   - Gain net: +{final_production_count - production_count}")
    
    print(f"\n✅ Migration terminée !")

if __name__ == "__main__":
    migrate_photos_to_production()