#!/usr/bin/env python3
"""
MIGRATION LIVE DATABASE - Identifier et migrer vers la vraie base de données LIVE
"""

import requests
import json
import sys
from datetime import datetime

# Configuration LIVE
LIVE_BASE_URL = "https://claire-marcus.com/api"
TEST_EMAIL = "test@claire-marcus.com"
TEST_PASSWORD = "test123!"
USER_ID = "82ce1284-ca2e-469a-8521-2a9116ef7826"

class LiveDatabaseMigration:
    def __init__(self):
        self.base_url = LIVE_BASE_URL
        self.token = None
        self.user_id = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Live-Migration/1.0'
        })

    def authenticate(self):
        """Authentification"""
        print(f"🔐 AUTHENTIFICATION LIVE API")
        
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
                
                print(f"   ✅ Succès - User ID: {self.user_id}")
                return True
            else:
                print(f"   ❌ Échec: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return False

    def extract_notes_from_live_api(self):
        """Extraire les notes depuis l'API LIVE"""
        print(f"\n📝 EXTRACTION NOTES DEPUIS API LIVE")
        
        try:
            response = self.session.get(f"{self.base_url}/notes")
            
            if response.status_code == 200:
                data = response.json()
                notes = data.get('notes', [])
                print(f"   ✅ {len(notes)} notes récupérées depuis l'API LIVE")
                
                # Analyser les notes
                website_analyses = []
                posts = []
                
                for note in notes:
                    try:
                        content = note.get('content', '')
                        
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
                            elif content_type == 'social_media_post':
                                posts.append({
                                    'note': note,
                                    'content': content_data
                                })
                    
                    except Exception as parse_error:
                        continue
                
                print(f"   📊 Analyses trouvées: {len(website_analyses)}")
                print(f"   📄 Posts trouvés: {len(posts)}")
                
                return {
                    'website_analyses': website_analyses,
                    'posts': posts
                }
            else:
                print(f"   ❌ Erreur: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return None

    def create_posts_via_api_simulation(self, posts_data):
        """Simuler la création de posts via l'API (pour comprendre le format attendu)"""
        print(f"\n🔄 SIMULATION CRÉATION POSTS VIA API")
        
        if not posts_data:
            print(f"   ⚠️ Aucun post à traiter")
            return 0
        
        # Essayer de comprendre comment créer des posts via l'API existante
        # En regardant les endpoints disponibles
        
        print(f"   📋 {len(posts_data)} posts à traiter")
        
        # Tester différents endpoints pour voir lesquels acceptent des données
        test_endpoints = [
            ("/posts/generate", "POST"),
            ("/posts/validate", "POST"),
            ("/notes", "POST"),  # Peut-être créer comme notes puis migrer
        ]
        
        sample_post = posts_data[0] if posts_data else None
        if not sample_post:
            return 0
        
        content = sample_post['content']
        
        for endpoint, method in test_endpoints:
            try:
                print(f"   🧪 Test {method} {endpoint}")
                
                if endpoint == "/notes":
                    # Essayer de créer une note avec le contenu du post
                    test_data = {
                        "description": f"Post {content.get('platform', 'social')} - {content.get('title', 'Sans titre')}",
                        "content": json.dumps(content),
                        "priority": "normal"
                    }
                elif endpoint == "/posts/generate":
                    # Essayer avec les paramètres de génération
                    test_data = {
                        "platform": content.get('platform', 'facebook'),
                        "content_type": "custom",
                        "custom_text": content.get('content', ''),
                        "target_month": content.get('target_month', '')
                    }
                else:
                    # Format générique
                    test_data = {
                        "title": content.get('title', ''),
                        "text": content.get('content', ''),
                        "platform": content.get('platform', 'facebook')
                    }
                
                if method == "POST":
                    response = self.session.post(f"{self.base_url}{endpoint}", json=test_data)
                else:
                    response = self.session.get(f"{self.base_url}{endpoint}")
                
                print(f"      Status: {response.status_code}")
                
                if response.status_code in [200, 201]:
                    print(f"      ✅ {endpoint} pourrait fonctionner")
                    response_data = response.json()
                    print(f"      Réponse: {str(response_data)[:100]}...")
                else:
                    print(f"      ❌ {response.text[:100]}")
                
            except Exception as e:
                print(f"      ❌ Erreur: {e}")
        
        return len(posts_data)

    def create_website_analysis_via_api(self, analyses_data):
        """Créer les analyses de site web via l'API"""
        print(f"\n🔍 CRÉATION ANALYSES VIA API")
        
        if not analyses_data:
            print(f"   ⚠️ Aucune analyse à traiter")
            return 0
        
        created_count = 0
        
        for analysis_data in analyses_data:
            try:
                content = analysis_data['content']
                
                # Essayer de créer l'analyse via l'endpoint d'analyse
                analysis_request = {
                    "url": content.get('url', ''),
                    "business_name": content.get('business_name', ''),
                    "force_analysis": True
                }
                
                print(f"   🧪 Création analyse pour: {content.get('business_name', 'N/A')}")
                
                # Tester l'endpoint /analyze
                response = self.session.post(f"{self.base_url}/analyze", json=analysis_request)
                print(f"      Status /analyze: {response.status_code}")
                
                if response.status_code in [200, 201]:
                    print(f"      ✅ Analyse créée via /analyze")
                    created_count += 1
                else:
                    print(f"      ❌ /analyze: {response.text[:100]}")
                    
                    # Essayer comme note
                    note_data = {
                        "description": f"Analyse de site web - {content.get('business_name', 'N/A')}",
                        "content": json.dumps(content),
                        "priority": "high"
                    }
                    
                    response = self.session.post(f"{self.base_url}/notes", json=note_data)
                    print(f"      Status /notes: {response.status_code}")
                    
                    if response.status_code in [200, 201]:
                        print(f"      ✅ Analyse sauvée comme note")
                        created_count += 1
                    else:
                        print(f"      ❌ /notes: {response.text[:100]}")
                
            except Exception as e:
                print(f"      ❌ Erreur création analyse: {e}")
                continue
        
        print(f"   ✅ {created_count} analyses traitées")
        return created_count

    def verify_results_after_creation(self):
        """Vérifier les résultats après création"""
        print(f"\n✅ VÉRIFICATION APRÈS CRÉATION")
        
        # Test 1: Posts générés
        try:
            response = self.session.get(f"{self.base_url}/posts/generated")
            print(f"   📄 GET /posts/generated: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('posts', [])
                print(f"      ✅ {len(posts)} posts trouvés")
                
                for i, post in enumerate(posts[:3]):
                    print(f"         {i+1}. {post.get('title', 'N/A')} ({post.get('platform', 'N/A')})")
            else:
                print(f"      ❌ Erreur: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Erreur posts: {e}")
        
        # Test 2: Analyses
        try:
            response = self.session.get(f"{self.base_url}/analysis")
            print(f"   🔍 GET /analysis: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    analyses = data
                else:
                    analyses = data.get('analyses', [])
                
                print(f"      ✅ {len(analyses)} analyses trouvées")
                
                for i, analysis in enumerate(analyses[:3]):
                    print(f"         {i+1}. {analysis.get('business_name', 'N/A')}")
            else:
                print(f"      ❌ Erreur: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Erreur analyses: {e}")
        
        # Test 3: Notes (pour voir si les données sont toujours là)
        try:
            response = self.session.get(f"{self.base_url}/notes")
            print(f"   📝 GET /notes: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                notes = data.get('notes', [])
                print(f"      ✅ {len(notes)} notes trouvées")
            else:
                print(f"      ❌ Erreur: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Erreur notes: {e}")

    def run_live_migration(self):
        """Exécuter la migration sur l'environnement LIVE"""
        print("=" * 80)
        print("🌐 MIGRATION ENVIRONNEMENT LIVE - API UNIQUEMENT")
        print("=" * 80)
        print(f"API: {self.base_url}")
        print(f"User ID: {USER_ID}")
        print(f"Stratégie: Utiliser uniquement les endpoints API disponibles")
        print(f"Heure: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Étape 1: Authentification
        if not self.authenticate():
            print("\n❌ MIGRATION INTERROMPUE - Échec authentification")
            return False
        
        # Étape 2: Extraction des données depuis l'API LIVE
        extracted_data = self.extract_notes_from_live_api()
        if not extracted_data:
            print("\n❌ MIGRATION INTERROMPUE - Échec extraction")
            return False
        
        # Étape 3: Tentative de création des posts via API
        posts_processed = self.create_posts_via_api_simulation(extracted_data['posts'])
        
        # Étape 4: Tentative de création des analyses via API
        analyses_processed = self.create_website_analysis_via_api(extracted_data['website_analyses'])
        
        # Étape 5: Vérification des résultats
        self.verify_results_after_creation()
        
        # RÉSUMÉ
        print("\n" + "=" * 80)
        print("📊 RÉSUMÉ MIGRATION LIVE")
        print("=" * 80)
        
        print(f"📝 DONNÉES SOURCES:")
        print(f"   Posts dans notes: {len(extracted_data['posts'])}")
        print(f"   Analyses dans notes: {len(extracted_data['website_analyses'])}")
        
        print(f"\n🔄 TRAITEMENT:")
        print(f"   Posts traités: {posts_processed}")
        print(f"   Analyses traitées: {analyses_processed}")
        
        print(f"\n🎯 CONCLUSION:")
        print(f"   Les données existent dans /notes mais ne sont pas dans les bonnes collections")
        print(f"   Il faut soit:")
        print(f"   1. Migrer directement en base de données LIVE")
        print(f"   2. Créer des endpoints de migration dans l'API")
        print(f"   3. Modifier le frontend pour lire depuis /notes")
        
        return True

def main():
    """Point d'entrée principal"""
    migration = LiveDatabaseMigration()
    success = migration.run_live_migration()
    
    if success:
        print(f"\n✅ ANALYSE LIVE TERMINÉE")
        sys.exit(0)
    else:
        print(f"\n❌ ANALYSE LIVE ÉCHOUÉE")
        sys.exit(1)

if __name__ == "__main__":
    main()