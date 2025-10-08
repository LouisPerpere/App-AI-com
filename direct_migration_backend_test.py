#!/usr/bin/env python3
"""
MIGRATION DIRECTE - Insérer les données restaurant dans les bonnes collections MongoDB
Script pour migrer directement les données de 'notes' vers 'generated_posts' et 'website_analyses'
"""

import requests
import json
import sys
from datetime import datetime
import uuid
import os
from pymongo import MongoClient

# Configuration LIVE
LIVE_BASE_URL = "https://claire-marcus.com/api"
TEST_EMAIL = "test@claire-marcus.com"
TEST_PASSWORD = "test123!"
USER_ID = "82ce1284-ca2e-469a-8521-2a9116ef7826"

# Configuration MongoDB (depuis backend/.env)
MONGO_URL = "mongodb://localhost:27017/claire_marcus"
DB_NAME = "claire_marcus"

class DirectDatabaseMigration:
    def __init__(self):
        self.base_url = LIVE_BASE_URL
        self.token = None
        self.user_id = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Direct-Migration/1.0'
        })
        self.mongo_client = None
        self.db = None

    def connect_to_database(self):
        """Connexion directe à MongoDB"""
        print(f"🗄️ CONNEXION À MONGODB")
        print(f"   URL: {MONGO_URL}")
        print(f"   Database: {DB_NAME}")
        
        try:
            self.mongo_client = MongoClient(MONGO_URL)
            self.db = self.mongo_client[DB_NAME]
            
            # Test de connexion
            self.db.command('ping')
            print(f"   ✅ CONNEXION MONGODB RÉUSSIE")
            
            # Lister les collections existantes
            collections = self.db.list_collection_names()
            print(f"   📋 Collections disponibles: {len(collections)}")
            
            # Vérifier les collections cibles
            target_collections = ['generated_posts', 'website_analyses', 'notes']
            for collection in target_collections:
                if collection in collections:
                    count = self.db[collection].count_documents({})
                    print(f"      ✅ {collection}: {count} documents")
                else:
                    print(f"      ⚠️ {collection}: collection n'existe pas")
            
            return True
            
        except Exception as e:
            print(f"   ❌ ERREUR CONNEXION MONGODB: {e}")
            return False

    def authenticate(self):
        """Authentification API pour récupérer les données"""
        print(f"\n🔐 AUTHENTIFICATION API")
        print(f"   Email: {TEST_EMAIL}")
        
        try:
            response = self.session.post(f"{self.base_url}/auth/login-robust", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token')
                self.user_id = data.get('user_id')
                
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}'
                })
                
                print(f"   ✅ AUTHENTIFICATION RÉUSSIE")
                print(f"   User ID: {self.user_id}")
                return True
            else:
                print(f"   ❌ ÉCHEC: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ ERREUR: {e}")
            return False

    def extract_and_analyze_notes(self):
        """Extraire et analyser les notes depuis l'API"""
        print(f"\n📝 EXTRACTION DES NOTES")
        
        try:
            response = self.session.get(f"{self.base_url}/notes")
            
            if response.status_code == 200:
                data = response.json()
                notes = data.get('notes', [])
                print(f"   ✅ {len(notes)} notes récupérées")
                
                # Analyser et séparer les données
                website_analyses = []
                posts = []
                
                for note in notes:
                    try:
                        content = note.get('content', '')
                        
                        # Parser le contenu JSON
                        if isinstance(content, str) and content.startswith('{'):
                            content_data = json.loads(content)
                        else:
                            content_data = content
                        
                        if isinstance(content_data, dict):
                            content_type = content_data.get('type', '')
                            
                            if content_type == 'website_analysis':
                                website_analyses.append({
                                    'note': note,
                                    'content': content_data
                                })
                                print(f"      📊 Analyse: {content_data.get('business_name', 'N/A')}")
                            
                            elif content_type == 'social_media_post':
                                posts.append({
                                    'note': note,
                                    'content': content_data
                                })
                                target_month = content_data.get('target_month', '')
                                print(f"      📅 Post {target_month}: {content_data.get('title', 'N/A')}")
                    
                    except Exception as parse_error:
                        print(f"      ⚠️ Erreur parsing: {parse_error}")
                        continue
                
                print(f"   📊 RÉSULTATS:")
                print(f"      Analyses site web: {len(website_analyses)}")
                print(f"      Posts sociaux: {len(posts)}")
                
                return {
                    'website_analyses': website_analyses,
                    'posts': posts
                }
            else:
                print(f"   ❌ ERREUR API: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ ERREUR: {e}")
            return None

    def migrate_posts_to_generated_collection(self, posts_data):
        """Migrer les posts vers la collection generated_posts"""
        print(f"\n📤 MIGRATION POSTS → generated_posts")
        
        if not posts_data:
            print(f"   ⚠️ Aucun post à migrer")
            return 0
        
        # Vérifier l'état actuel de la collection
        current_count = self.db.generated_posts.count_documents({"owner_id": USER_ID})
        print(f"   📊 Posts actuels dans generated_posts: {current_count}")
        
        migrated_count = 0
        
        for post_data in posts_data:
            try:
                note = post_data['note']
                content = post_data['content']
                
                # Générer un ID unique
                post_id = f"post_{USER_ID}_{int(datetime.now().timestamp())}_{migrated_count}"
                
                # Créer le document pour generated_posts
                post_doc = {
                    "id": post_id,
                    "owner_id": USER_ID,
                    "user_id": USER_ID,
                    "platform": content.get('platform', 'facebook'),
                    "title": content.get('title', ''),
                    "text": content.get('content', ''),
                    "hashtags": content.get('hashtags', []),
                    "scheduled_date": content.get('scheduled_date', content.get('publication_date')),
                    "target_month": content.get('target_month', ''),
                    "status": "ready",
                    "validated": False,
                    "published": False,
                    "created_at": note.get('created_at', datetime.now().isoformat()),
                    "visual_url": content.get('image_description', ''),
                    "visual_id": "",
                    "generation_batch": f"migration_{datetime.now().strftime('%Y%m%d')}",
                    "migrated_from_notes": True,
                    "original_note_id": note.get('note_id'),
                    "migration_timestamp": datetime.now().isoformat()
                }
                
                # Insérer dans la collection
                result = self.db.generated_posts.insert_one(post_doc)
                
                if result.inserted_id:
                    migrated_count += 1
                    print(f"      ✅ Post migré: {post_doc['title'][:50]}...")
                else:
                    print(f"      ❌ Échec insertion: {post_doc['title'][:50]}...")
                
            except Exception as e:
                print(f"      ❌ Erreur migration post: {e}")
                continue
        
        print(f"   ✅ {migrated_count} posts migrés vers generated_posts")
        return migrated_count

    def migrate_analyses_to_website_collection(self, analyses_data):
        """Migrer les analyses vers la collection website_analyses"""
        print(f"\n📤 MIGRATION ANALYSES → website_analyses")
        
        if not analyses_data:
            print(f"   ⚠️ Aucune analyse à migrer")
            return 0
        
        # Vérifier l'état actuel de la collection
        current_count = self.db.website_analyses.count_documents({"user_id": USER_ID})
        print(f"   📊 Analyses actuelles dans website_analyses: {current_count}")
        
        migrated_count = 0
        
        for analysis_data in analyses_data:
            try:
                note = analysis_data['note']
                content = analysis_data['content']
                
                # Générer un ID unique
                analysis_id = f"analysis_{USER_ID}_{int(datetime.now().timestamp())}_{migrated_count}"
                
                # Créer le document pour website_analyses
                analysis_doc = {
                    "id": analysis_id,
                    "user_id": USER_ID,
                    "owner_id": USER_ID,
                    "website_url": content.get('url', ''),
                    "business_name": content.get('business_name', ''),
                    "seo_score": content.get('seo_score', 0),
                    "performance_score": content.get('performance_score', 0),
                    "accessibility_score": content.get('accessibility_score', 0),
                    "overall_score": content.get('overall_score', 0),
                    "recommendations": content.get('recommendations', []),
                    "strengths": content.get('strengths', []),
                    "improvements": content.get('improvements', []),
                    "technical_analysis": content.get('technical_analysis', {}),
                    "competitive_analysis": content.get('competitive_analysis', {}),
                    "action_plan": content.get('action_plan', {}),
                    "created_at": note.get('created_at', datetime.now().isoformat()),
                    "analysis_date": content.get('analysis_date', datetime.now().isoformat()),
                    "migrated_from_notes": True,
                    "original_note_id": note.get('note_id'),
                    "migration_timestamp": datetime.now().isoformat()
                }
                
                # Insérer dans la collection
                result = self.db.website_analyses.insert_one(analysis_doc)
                
                if result.inserted_id:
                    migrated_count += 1
                    print(f"      ✅ Analyse migrée: {analysis_doc['business_name']}")
                else:
                    print(f"      ❌ Échec insertion: {analysis_doc['business_name']}")
                
            except Exception as e:
                print(f"      ❌ Erreur migration analyse: {e}")
                continue
        
        print(f"   ✅ {migrated_count} analyses migrées vers website_analyses")
        return migrated_count

    def verify_migration_via_api(self):
        """Vérifier la migration via les endpoints API"""
        print(f"\n✅ VÉRIFICATION VIA API")
        
        # Test 1: Vérifier /api/posts/generated
        try:
            response = self.session.get(f"{self.base_url}/posts/generated")
            print(f"   📄 GET /posts/generated: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('posts', [])
                print(f"      ✅ {len(posts)} posts trouvés")
                
                # Analyser par mois
                october_posts = [p for p in posts if 'octobre' in p.get('target_month', '').lower()]
                november_posts = [p for p in posts if 'novembre' in p.get('target_month', '').lower()]
                
                print(f"      📅 Posts octobre: {len(october_posts)}")
                print(f"      📅 Posts novembre: {len(november_posts)}")
                
                # Afficher quelques exemples
                for i, post in enumerate(posts[:3]):
                    print(f"         {i+1}. {post.get('title', 'N/A')} ({post.get('platform', 'N/A')})")
                
                return len(posts)
            else:
                print(f"      ❌ Erreur: {response.text[:100]}")
                return 0
                
        except Exception as e:
            print(f"   ❌ Erreur vérification posts: {e}")
            return 0

    def verify_migration_via_database(self):
        """Vérifier la migration directement en base"""
        print(f"\n🗄️ VÉRIFICATION DIRECTE BASE DE DONNÉES")
        
        try:
            # Vérifier generated_posts
            posts_count = self.db.generated_posts.count_documents({"owner_id": USER_ID})
            migrated_posts = self.db.generated_posts.count_documents({
                "owner_id": USER_ID,
                "migrated_from_notes": True
            })
            
            print(f"   📄 generated_posts:")
            print(f"      Total posts utilisateur: {posts_count}")
            print(f"      Posts migrés: {migrated_posts}")
            
            # Vérifier website_analyses
            analyses_count = self.db.website_analyses.count_documents({"user_id": USER_ID})
            migrated_analyses = self.db.website_analyses.count_documents({
                "user_id": USER_ID,
                "migrated_from_notes": True
            })
            
            print(f"   🔍 website_analyses:")
            print(f"      Total analyses utilisateur: {analyses_count}")
            print(f"      Analyses migrées: {migrated_analyses}")
            
            return {
                'posts_total': posts_count,
                'posts_migrated': migrated_posts,
                'analyses_total': analyses_count,
                'analyses_migrated': migrated_analyses
            }
            
        except Exception as e:
            print(f"   ❌ Erreur vérification base: {e}")
            return None

    def run_direct_migration(self):
        """Exécuter la migration directe complète"""
        print("=" * 80)
        print("🚀 MIGRATION DIRECTE - BASE DE DONNÉES MONGODB")
        print("=" * 80)
        print(f"API: {self.base_url}")
        print(f"MongoDB: {MONGO_URL}")
        print(f"User ID: {USER_ID}")
        print(f"Heure: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Étape 1: Connexion MongoDB
        if not self.connect_to_database():
            print("\n❌ MIGRATION INTERROMPUE - Échec connexion MongoDB")
            return False
        
        # Étape 2: Authentification API
        if not self.authenticate():
            print("\n❌ MIGRATION INTERROMPUE - Échec authentification API")
            return False
        
        # Étape 3: Extraction des données
        extracted_data = self.extract_and_analyze_notes()
        if not extracted_data:
            print("\n❌ MIGRATION INTERROMPUE - Échec extraction")
            return False
        
        # Étape 4: Migration des posts
        posts_migrated = self.migrate_posts_to_generated_collection(extracted_data['posts'])
        
        # Étape 5: Migration des analyses
        analyses_migrated = self.migrate_analyses_to_website_collection(extracted_data['website_analyses'])
        
        # Étape 6: Vérification API
        posts_found_api = self.verify_migration_via_api()
        
        # Étape 7: Vérification base de données
        db_verification = self.verify_migration_via_database()
        
        # RÉSUMÉ FINAL
        print("\n" + "=" * 80)
        print("📊 RÉSUMÉ MIGRATION DIRECTE")
        print("=" * 80)
        
        print(f"📝 DONNÉES SOURCES (notes):")
        print(f"   Posts extraits: {len(extracted_data['posts'])}")
        print(f"   Analyses extraites: {len(extracted_data['website_analyses'])}")
        
        print(f"\n📤 MIGRATION RÉALISÉE:")
        print(f"   Posts migrés: {posts_migrated}")
        print(f"   Analyses migrées: {analyses_migrated}")
        
        print(f"\n✅ VÉRIFICATION API:")
        print(f"   Posts trouvés via /posts/generated: {posts_found_api}")
        
        if db_verification:
            print(f"\n🗄️ VÉRIFICATION BASE:")
            print(f"   Posts total: {db_verification['posts_total']}")
            print(f"   Analyses total: {db_verification['analyses_total']}")
        
        # Évaluation du succès
        success = (posts_migrated > 0 or analyses_migrated > 0)
        
        if success:
            print(f"\n🎉 MIGRATION RÉUSSIE!")
            print(f"   Les données sont maintenant dans les bonnes collections")
            print(f"   Le frontend devrait pouvoir les afficher")
        else:
            print(f"\n❌ MIGRATION ÉCHOUÉE")
            print(f"   Aucune donnée n'a été migrée")
        
        return success

    def cleanup(self):
        """Nettoyer les connexions"""
        if self.mongo_client:
            self.mongo_client.close()

def main():
    """Point d'entrée principal"""
    migration = DirectDatabaseMigration()
    
    try:
        success = migration.run_direct_migration()
        
        if success:
            print(f"\n✅ MIGRATION DIRECTE TERMINÉE AVEC SUCCÈS")
            sys.exit(0)
        else:
            print(f"\n❌ MIGRATION DIRECTE ÉCHOUÉE")
            sys.exit(1)
    
    finally:
        migration.cleanup()

if __name__ == "__main__":
    main()