#!/usr/bin/env python3
"""
Script pour nettoyer les fichiers corrompus de la bibliothèque
et synchroniser les descriptions avec les fichiers valides
"""
import os
import json
from PIL import Image

def check_image_validity(file_path):
    """Vérifie si un fichier image est valide et peut être ouvert"""
    try:
        with Image.open(file_path) as img:
            img.verify()  # Vérifie l'intégrité du fichier
        return True
    except Exception as e:
        print(f"🔴 Fichier corrompu: {os.path.basename(file_path)} - {e}")
        return False

def load_descriptions():
    """Charge les descriptions depuis le fichier JSON"""
    descriptions_file = "content_descriptions.json"
    if os.path.exists(descriptions_file):
        try:
            with open(descriptions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Erreur lors du chargement des descriptions: {e}")
            return {}
    return {}

def save_descriptions(descriptions):
    """Sauvegarde les descriptions dans le fichier JSON"""
    descriptions_file = "content_descriptions.json"
    try:
        with open(descriptions_file, 'w', encoding='utf-8') as f:
            json.dump(descriptions, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"⚠️ Erreur lors de la sauvegarde des descriptions: {e}")
        return False

def cleanup_corrupted_files():
    """Nettoie les fichiers corrompus et synchronise les descriptions"""
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        print("❌ Dossier uploads non trouvé")
        return
    
    print("🔍 Vérification des fichiers...")
    
    # Charger les descriptions actuelles
    descriptions = load_descriptions()
    print(f"📊 {len(descriptions)} descriptions trouvées")
    
    # Vérifier tous les fichiers
    valid_files = []
    corrupted_files = []
    
    for filename in os.listdir(uploads_dir):
        file_path = os.path.join(uploads_dir, filename)
        if os.path.isfile(file_path):
            file_extension = os.path.splitext(filename)[1].lower()
            
            # Vérifier seulement les images
            if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                if check_image_validity(file_path):
                    valid_files.append(filename)
                else:
                    corrupted_files.append(filename)
            else:
                # Les fichiers non-image sont considérés comme valides
                valid_files.append(filename)
    
    print(f"✅ {len(valid_files)} fichiers valides")
    print(f"🔴 {len(corrupted_files)} fichiers corrompus")
    
    if corrupted_files:
        print("\n🗑️ Suppression des fichiers corrompus:")
        for filename in corrupted_files:
            file_path = os.path.join(uploads_dir, filename)
            file_id = filename.split('.')[0]
            
            try:
                # Supprimer le fichier physique
                os.remove(file_path)
                print(f"   ✅ Supprimé: {filename}")
                
                # Supprimer la description associée
                if file_id in descriptions:
                    del descriptions[file_id]
                    print(f"   ✅ Description supprimée: {file_id}")
                    
            except Exception as e:
                print(f"   ❌ Erreur lors de la suppression de {filename}: {e}")
    
    # Nettoyer les descriptions orphelines
    print("\n🔄 Nettoyage des descriptions orphelines...")
    valid_file_ids = set()
    for filename in valid_files:
        file_id = filename.split('.')[0]
        valid_file_ids.add(file_id)
    
    orphaned_descriptions = []
    for file_id in list(descriptions.keys()):
        if file_id not in valid_file_ids:
            orphaned_descriptions.append(file_id)
            del descriptions[file_id]
    
    if orphaned_descriptions:
        print(f"   🗑️ Supprimé {len(orphaned_descriptions)} descriptions orphelines")
    
    # Ajouter des descriptions vides pour les nouveaux fichiers
    new_files = []
    for file_id in valid_file_ids:
        if file_id not in descriptions:
            descriptions[file_id] = ""
            new_files.append(file_id)
    
    if new_files:
        print(f"   ➕ Ajouté {len(new_files)} descriptions vides pour nouveaux fichiers")
    
    # Sauvegarder les descriptions mises à jour
    if save_descriptions(descriptions):
        print("✅ Descriptions synchronisées avec succès")
    else:
        print("❌ Erreur lors de la synchronisation des descriptions")
    
    print(f"\n📊 Résumé final:")
    print(f"   • Fichiers valides: {len(valid_files)}")
    print(f"   • Descriptions: {len(descriptions)}")
    print(f"   • Fichiers corrompus supprimés: {len(corrupted_files)}")
    print(f"   • Descriptions orphelines supprimées: {len(orphaned_descriptions)}")

if __name__ == "__main__":
    print("🧹 Nettoyage de la bibliothèque en cours...")
    cleanup_corrupted_files()
    print("🎉 Nettoyage terminé!")