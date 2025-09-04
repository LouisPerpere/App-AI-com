#!/usr/bin/env python3
"""
🔧 SCRIPT DE RÉPARATION DES VIGNETTES

Ce script régénère les vignettes manquantes pour les images uploadées
en corrigeant les problèmes de structure de données.
"""

import os
import sys
sys.path.append('/app/backend')

from database import get_database
from thumbs import generate_image_thumb_from_bytes
from routes_thumbs import save_db_thumbnail
import gridfs
import requests
from datetime import datetime

def fix_thumbnails():
    """Fix missing thumbnails for uploaded images"""
    try:
        print("🔧 Démarrage de la réparation des vignettes...")
        print(f"⏰ Début: {datetime.now().isoformat()}")
        
        # Get database connection
        dbm = get_database()
        db = dbm.db
        
        # Find all images without proper thumbnails
        images = list(db.media.find({
            'file_type': {'$regex': '^image/'},
            '$or': [
                {'thumb_url': None},
                {'thumb_url': {'$regex': 'claire-marcus-api.onrender.com'}},  # External URLs
                {'id': {'$exists': False}},  # Missing ID
                {'gridfs_id': {'$exists': False}}  # Missing GridFS ID
            ]
        }))
        
        print(f"📊 Trouvé {len(images)} images à traiter")
        
        processed = 0
        skipped = 0
        errors = 0
        
        for image in images:
            try:
                filename = image.get('filename', 'unknown')
                print(f"\n📱 Traitement: {filename}")
                print(f"   Owner ID: {image.get('owner_id', 'N/A')}")
                print(f"   Current thumb_url: {image.get('thumb_url', 'N/A')}")
                
                # Skip if no owner_id
                if not image.get('owner_id'):
                    print("   ⚠️ Ignoré: pas d'owner_id")
                    skipped += 1
                    continue
                
                # Try to get image data
                image_data = None
                
                # Method 1: GridFS (if gridfs_id exists)
                if image.get('gridfs_id'):
                    try:
                        fs = gridfs.GridFS(db, collection='fs')
                        grid_file = fs.get(image['gridfs_id'])
                        image_data = grid_file.read()
                        print(f"   ✅ Image récupérée depuis GridFS: {len(image_data)} bytes")
                    except Exception as gridfs_error:
                        print(f"   ❌ Erreur GridFS: {gridfs_error}")
                
                # Method 2: External URL (if no GridFS data)
                if not image_data and image.get('thumb_url'):
                    try:
                        # Try to download from external URL (original image)
                        original_url = image.get('url', '')
                        if 'claire-marcus-api.onrender.com' in original_url:
                            print(f"   🌐 Tentative de téléchargement: {original_url}")
                            response = requests.get(original_url, timeout=10)
                            if response.status_code == 200:
                                image_data = response.content
                                print(f"   ✅ Image téléchargée: {len(image_data)} bytes")
                            else:
                                print(f"   ❌ Échec téléchargement: HTTP {response.status_code}")
                    except Exception as download_error:
                        print(f"   ❌ Erreur téléchargement: {download_error}")
                
                # Skip if no image data found
                if not image_data:
                    print("   ⚠️ Ignoré: impossible de récupérer les données image")
                    skipped += 1
                    continue
                
                # Generate thumbnail
                try:
                    thumb_bytes = generate_image_thumb_from_bytes(image_data)
                    print(f"   ✅ Vignette générée: {len(thumb_bytes)} bytes")
                    
                    # Ensure image has an ID field
                    image_id = image.get('id')
                    if not image_id:
                        # Use the _id as string
                        image_id = str(image['_id'])
                        # Update the document with the id field
                        db.media.update_one(
                            {'_id': image['_id']},
                            {'$set': {'id': image_id}}
                        )
                        print(f"   ✅ ID ajouté: {image_id}")
                    
                    # Save thumbnail
                    save_db_thumbnail(image['owner_id'], image_id, thumb_bytes)
                    print("   ✅ Vignette sauvegardée")
                    
                    # Verify the thumbnail was saved
                    updated_image = db.media.find_one({'_id': image['_id']})
                    new_thumb_url = updated_image.get('thumb_url')
                    print(f"   🔗 Nouvelle thumb_url: {new_thumb_url}")
                    
                    processed += 1
                    
                except Exception as thumb_error:
                    print(f"   ❌ Erreur génération vignette: {thumb_error}")
                    errors += 1
                
            except Exception as item_error:
                print(f"   ❌ Erreur traitement {filename}: {item_error}")
                errors += 1
        
        print(f"\n🎉 Réparation terminée!")
        print(f"📊 Résultats:")
        print(f"   ✅ Traitées: {processed}")
        print(f"   ⚠️ Ignorées: {skipped}")
        print(f"   ❌ Erreurs: {errors}")
        print(f"⏰ Fin: {datetime.now().isoformat()}")
        
        return processed > 0
        
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_thumbnails()
    if success:
        print("\n✅ RÉPARATION RÉUSSIE")
        print("🚀 Les vignettes devraient maintenant s'afficher correctement")
    else:
        print("\n❌ RÉPARATION ÉCHOUÉE")
        print("🔍 Vérifiez les erreurs ci-dessus")