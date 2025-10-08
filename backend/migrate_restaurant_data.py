#!/usr/bin/env python3
"""
Script de migration pour déplacer les données du restaurant test
de la collection 'notes' vers les collections appropriées:
- Posts → generated_posts
- Analyses de site web → website_analyses
"""

import os
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()

# Importer database depuis le même répertoire
from database import get_database

def migrate_restaurant_data():
    """Migrer les données du restaurant depuis notes vers les collections appropriées"""
    
    print("=" * 80)
    print("🚀 DÉMARRAGE DE LA MIGRATION DES DONNÉES RESTAURANT")
    print("=" * 80)
    
    # ID de l'utilisateur test
    test_user_id = "82ce1284-ca2e-469a-8521-2a9116ef7826"
    print(f"\n👤 Utilisateur cible: test@claire-marcus.com ({test_user_id})")
    
    # Connexion à la base de données
    dbm = get_database()
    db = dbm.db
    
    print(f"\n📊 Base de données: {db.name}")
    print(f"✅ Connexion établie")
    
    # ========================================
    # ÉTAPE 1: Récupérer toutes les notes du test user
    # ========================================
    print("\n" + "-" * 80)
    print("ÉTAPE 1: ANALYSE DES NOTES EXISTANTES")
    print("-" * 80)
    
    notes = list(db.notes.find({"user_id": test_user_id}))
    print(f"\n📋 Total notes trouvées: {len(notes)}")
    
    if len(notes) == 0:
        print("⚠️ Aucune note trouvée pour cet utilisateur")
        return
    
    # Classifier les notes
    posts_to_migrate = []
    analyses_to_migrate = []
    other_notes = []
    
    for note in notes:
        note_type = note.get("type", "")
        title = note.get("title", "")
        content = note.get("content", "")
        
        # Identifier les posts (ont des champs platform, scheduled_date, status)
        if "platform" in note and "scheduled_date" in note:
            posts_to_migrate.append(note)
        # Identifier les analyses de site web (ont des champs seo_score, recommendations)
        elif "seo_score" in note or "recommendations" in note or "website_url" in note:
            analyses_to_migrate.append(note)
        else:
            other_notes.append(note)
    
    print(f"\n📊 Classification:")
    print(f"   ├─ Posts à migrer: {len(posts_to_migrate)}")
    print(f"   ├─ Analyses à migrer: {len(analyses_to_migrate)}")
    print(f"   └─ Autres notes (non migrées): {len(other_notes)}")
    
    # ========================================
    # ÉTAPE 2: Migrer les posts vers generated_posts
    # ========================================
    print("\n" + "-" * 80)
    print("ÉTAPE 2: MIGRATION DES POSTS")
    print("-" * 80)
    
    migrated_posts_count = 0
    post_ids_to_delete = []
    
    for note in posts_to_migrate:
        try:
            # Extraire les données du post depuis la note
            post_data = {
                "id": note.get("id", f"post_{test_user_id}_{int(datetime.now(timezone.utc).timestamp())}_{migrated_posts_count}"),
                "owner_id": test_user_id,
                "title": note.get("title", ""),
                "text": note.get("content", ""),
                "hashtags": note.get("hashtags", []),
                "visual_url": note.get("visual_url", ""),
                "visual_id": note.get("visual_id", ""),
                "visual_type": note.get("visual_type", "image"),
                "platform": note.get("platform", "facebook"),
                "content_type": note.get("content_type", "marketing"),
                "scheduled_date": note.get("scheduled_date", ""),
                "status": note.get("status", "ready"),
                "published": note.get("published", False),
                "validated": note.get("validated", False),
                "validated_at": note.get("validated_at", ""),
                "carousel_images": note.get("carousel_images", []),
                "created_at": note.get("created_at", datetime.now(timezone.utc).isoformat()),
                "modified_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Insérer dans generated_posts (ou mettre à jour si existe déjà)
            result = db.generated_posts.update_one(
                {"id": post_data["id"]},
                {"$set": post_data},
                upsert=True
            )
            
            if result.upserted_id or result.modified_count > 0:
                migrated_posts_count += 1
                post_ids_to_delete.append(note.get("id"))
                print(f"   ✅ Post migré: {post_data['title'][:50]}... (ID: {post_data['id']})")
            
        except Exception as e:
            print(f"   ❌ Erreur migration post {note.get('id')}: {str(e)}")
    
    print(f"\n📊 Résultat migration posts: {migrated_posts_count}/{len(posts_to_migrate)} posts migrés")
    
    # ========================================
    # ÉTAPE 3: Migrer les analyses vers website_analyses
    # ========================================
    print("\n" + "-" * 80)
    print("ÉTAPE 3: MIGRATION DES ANALYSES")
    print("-" * 80)
    
    migrated_analyses_count = 0
    analysis_ids_to_delete = []
    
    for note in analyses_to_migrate:
        try:
            # Extraire les données de l'analyse depuis la note
            analysis_data = {
                "id": note.get("id", f"analysis_{test_user_id}_{int(datetime.now(timezone.utc).timestamp())}_{migrated_analyses_count}"),
                "user_id": test_user_id,
                "website_url": note.get("website_url", note.get("content", {}).get("website_url", "")),
                "seo_score": note.get("seo_score", note.get("content", {}).get("seo_score", 0)),
                "performance_score": note.get("performance_score", note.get("content", {}).get("performance_score", 0)),
                "accessibility_score": note.get("accessibility_score", note.get("content", {}).get("accessibility_score", 0)),
                "overall_score": note.get("overall_score", note.get("content", {}).get("overall_score", 0)),
                "recommendations": note.get("recommendations", note.get("content", {}).get("recommendations", [])),
                "technical_analysis": note.get("technical_analysis", note.get("content", {}).get("technical_analysis", {})),
                "competitive_analysis": note.get("competitive_analysis", note.get("content", {}).get("competitive_analysis", {})),
                "action_plan": note.get("action_plan", note.get("content", {}).get("action_plan", {})),
                "created_at": note.get("created_at", datetime.now(timezone.utc).isoformat()),
                "status": note.get("status", "completed")
            }
            
            # Si les données sont dans un champ 'content' structuré, les extraire
            if isinstance(note.get("content"), dict):
                content = note.get("content", {})
                for key in ["website_url", "seo_score", "performance_score", "accessibility_score", 
                           "overall_score", "recommendations", "technical_analysis", 
                           "competitive_analysis", "action_plan"]:
                    if key in content:
                        analysis_data[key] = content[key]
            
            # Insérer dans website_analyses (ou mettre à jour si existe déjà)
            result = db.website_analyses.update_one(
                {"id": analysis_data["id"]},
                {"$set": analysis_data},
                upsert=True
            )
            
            if result.upserted_id or result.modified_count > 0:
                migrated_analyses_count += 1
                analysis_ids_to_delete.append(note.get("id"))
                url = analysis_data.get("website_url", "URL non disponible")
                print(f"   ✅ Analyse migrée: {url} (Score: {analysis_data.get('overall_score', 0)})")
            
        except Exception as e:
            print(f"   ❌ Erreur migration analyse {note.get('id')}: {str(e)}")
    
    print(f"\n📊 Résultat migration analyses: {migrated_analyses_count}/{len(analyses_to_migrate)} analyses migrées")
    
    # ========================================
    # ÉTAPE 4: Nettoyer les notes migrées
    # ========================================
    print("\n" + "-" * 80)
    print("ÉTAPE 4: NETTOYAGE DES NOTES")
    print("-" * 80)
    
    all_ids_to_delete = post_ids_to_delete + analysis_ids_to_delete
    
    if len(all_ids_to_delete) > 0:
        print(f"\n🗑️ Suppression de {len(all_ids_to_delete)} notes migrées...")
        
        result = db.notes.delete_many({"id": {"$in": all_ids_to_delete}})
        print(f"   ✅ {result.deleted_count} notes supprimées de la collection 'notes'")
    else:
        print("\n⚠️ Aucune note à supprimer")
    
    # ========================================
    # ÉTAPE 5: Vérification finale
    # ========================================
    print("\n" + "-" * 80)
    print("ÉTAPE 5: VÉRIFICATION FINALE")
    print("-" * 80)
    
    # Vérifier generated_posts
    posts_count = db.generated_posts.count_documents({"owner_id": test_user_id})
    print(f"\n📊 Collection 'generated_posts':")
    print(f"   └─ {posts_count} posts pour l'utilisateur test")
    
    # Vérifier website_analyses
    analyses_count = db.website_analyses.count_documents({"user_id": test_user_id})
    print(f"\n📊 Collection 'website_analyses':")
    print(f"   └─ {analyses_count} analyses pour l'utilisateur test")
    
    # Vérifier notes restantes
    remaining_notes = db.notes.count_documents({"user_id": test_user_id})
    print(f"\n📊 Collection 'notes' (restantes):")
    print(f"   └─ {remaining_notes} notes non migrées")
    
    # ========================================
    # RÉSUMÉ FINAL
    # ========================================
    print("\n" + "=" * 80)
    print("✅ MIGRATION TERMINÉE AVEC SUCCÈS")
    print("=" * 80)
    print(f"\n📊 Résumé:")
    print(f"   ├─ Posts migrés: {migrated_posts_count}")
    print(f"   ├─ Analyses migrées: {migrated_analyses_count}")
    print(f"   ├─ Notes supprimées: {len(all_ids_to_delete)}")
    print(f"   ├─ Notes restantes: {remaining_notes}")
    print(f"   └─ Total objets dans generated_posts: {posts_count}")
    print(f"   └─ Total objets dans website_analyses: {analyses_count}")
    
    print("\n✨ Les données devraient maintenant être visibles dans le frontend!")
    print()

if __name__ == "__main__":
    try:
        migrate_restaurant_data()
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
