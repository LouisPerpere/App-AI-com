#!/usr/bin/env python3
"""
Investigation de la base de données pour comprendre pourquoi l'API retourne 0 posts
malgré la présence de données dans les collections
"""

import sys
import os
sys.path.append('/app/backend')
from database import get_database
import json

TARGET_USER_ID = "82ce1284-ca2e-469a-8521-2a9116ef7826"

def investigate_database():
    print("🔍 INVESTIGATION BASE DE DONNÉES")
    print("=" * 60)
    
    db = get_database()
    
    # 1. Vérifier les posts dans generated_posts
    print(f"📄 COLLECTION: generated_posts")
    posts = list(db.db.generated_posts.find({}))
    print(f"   Total posts: {len(posts)}")
    
    if posts:
        print(f"   Exemples de posts:")
        for i, post in enumerate(posts[:3]):
            print(f"      {i+1}. ID: {post.get('id', 'N/A')}")
            print(f"         owner_id: {post.get('owner_id', 'N/A')}")
            print(f"         user_id: {post.get('user_id', 'N/A')}")
            print(f"         title: {post.get('title', 'N/A')[:50]}...")
            print(f"         platform: {post.get('platform', 'N/A')}")
    
    # Vérifier les posts pour notre user_id spécifique
    user_posts = list(db.db.generated_posts.find({"owner_id": TARGET_USER_ID}))
    print(f"   Posts pour owner_id {TARGET_USER_ID}: {len(user_posts)}")
    
    user_posts_alt = list(db.db.generated_posts.find({"user_id": TARGET_USER_ID}))
    print(f"   Posts pour user_id {TARGET_USER_ID}: {len(user_posts_alt)}")
    
    # 2. Vérifier les analyses dans website_analyses
    print(f"\n🔍 COLLECTION: website_analyses")
    analyses = list(db.db.website_analyses.find({}))
    print(f"   Total analyses: {len(analyses)}")
    
    if analyses:
        print(f"   Exemples d'analyses:")
        for i, analysis in enumerate(analyses[:3]):
            print(f"      {i+1}. ID: {analysis.get('id', 'N/A')}")
            print(f"         user_id: {analysis.get('user_id', 'N/A')}")
            print(f"         owner_id: {analysis.get('owner_id', 'N/A')}")
            print(f"         website_url: {analysis.get('website_url', 'N/A')}")
    
    # Vérifier les analyses pour notre user_id spécifique
    user_analyses = list(db.db.website_analyses.find({"user_id": TARGET_USER_ID}))
    print(f"   Analyses pour user_id {TARGET_USER_ID}: {len(user_analyses)}")
    
    user_analyses_alt = list(db.db.website_analyses.find({"owner_id": TARGET_USER_ID}))
    print(f"   Analyses pour owner_id {TARGET_USER_ID}: {len(user_analyses_alt)}")
    
    # 3. Vérifier les notes dans content_notes
    print(f"\n📝 COLLECTION: content_notes")
    notes = list(db.db.content_notes.find({"owner_id": TARGET_USER_ID}))
    print(f"   Notes pour owner_id {TARGET_USER_ID}: {len(notes)}")
    
    if notes:
        print(f"   Exemples de notes:")
        for i, note in enumerate(notes[:5]):
            print(f"      {i+1}. ID: {note.get('note_id', 'N/A')}")
            print(f"         description: {note.get('description', 'N/A')[:50]}...")
            print(f"         content preview: {note.get('content', '')[:100]}...")
    
    # 4. Vérifier tous les user_ids uniques dans chaque collection
    print(f"\n👥 USER_IDS UNIQUES:")
    
    # generated_posts
    owner_ids = db.db.generated_posts.distinct("owner_id")
    user_ids = db.db.generated_posts.distinct("user_id")
    print(f"   generated_posts - owner_ids: {owner_ids}")
    print(f"   generated_posts - user_ids: {user_ids}")
    
    # website_analyses
    analysis_user_ids = db.db.website_analyses.distinct("user_id")
    analysis_owner_ids = db.db.website_analyses.distinct("owner_id")
    print(f"   website_analyses - user_ids: {analysis_user_ids}")
    print(f"   website_analyses - owner_ids: {analysis_owner_ids}")
    
    # content_notes
    notes_owner_ids = db.db.content_notes.distinct("owner_id")
    print(f"   content_notes - owner_ids: {notes_owner_ids}")
    
    print(f"\n🎯 DIAGNOSTIC:")
    if len(user_posts) == 0 and len(posts) > 0:
        print(f"   ❌ PROBLÈME: Posts existent mais pas pour le bon owner_id")
        print(f"   🔧 SOLUTION: Corriger les owner_id dans generated_posts")
    
    if len(user_analyses) == 0 and len(analyses) > 0:
        print(f"   ❌ PROBLÈME: Analyses existent mais pas pour le bon user_id")
        print(f"   🔧 SOLUTION: Corriger les user_id dans website_analyses")
    
    if len(notes) > 0:
        print(f"   ✅ Notes trouvées pour le user_id correct")
    else:
        print(f"   ❌ PROBLÈME: Aucune note trouvée pour ce user_id")

if __name__ == "__main__":
    investigate_database()