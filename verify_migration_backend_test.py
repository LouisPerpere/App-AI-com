#!/usr/bin/env python3
"""
VÉRIFICATION MIGRATION - Tester les endpoints après migration
"""

import requests
import json
import sys
from datetime import datetime
from pymongo import MongoClient

# Configuration
LIVE_BASE_URL = "https://claire-marcus.com/api"
TEST_EMAIL = "test@claire-marcus.com"
TEST_PASSWORD = "test123!"
USER_ID = "82ce1284-ca2e-469a-8521-2a9116ef7826"
MONGO_URL = "mongodb://localhost:27017/claire_marcus"
DB_NAME = "claire_marcus"

class MigrationVerification:
    def __init__(self):
        self.base_url = LIVE_BASE_URL
        self.token = None
        self.user_id = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Migration-Verification/1.0'
        })
        self.mongo_client = None
        self.db = None

    def authenticate(self):
        """Authentification"""
        print(f"🔐 AUTHENTIFICATION")
        
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

    def connect_database(self):
        """Connexion MongoDB"""
        print(f"\n🗄️ CONNEXION MONGODB")
        
        try:
            self.mongo_client = MongoClient(MONGO_URL)
            self.db = self.mongo_client[DB_NAME]
            self.db.command('ping')
            print(f"   ✅ Connexion réussie")
            return True
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return False

    def check_database_content(self):
        """Vérifier le contenu de la base de données"""
        print(f"\n🔍 VÉRIFICATION BASE DE DONNÉES")
        
        # Vérifier generated_posts
        posts_query = {"owner_id": self.user_id}
        posts = list(self.db.generated_posts.find(posts_query))
        print(f"   📄 generated_posts avec owner_id={self.user_id}: {len(posts)}")
        
        if posts:
            print(f"      Exemples de posts:")
            for i, post in enumerate(posts[:3]):
                print(f"         {i+1}. ID: {post.get('id', 'N/A')}")
                print(f"            Titre: {post.get('title', 'N/A')}")
                print(f"            Plateforme: {post.get('platform', 'N/A')}")
                print(f"            Mois: {post.get('target_month', 'N/A')}")
                print(f"            Owner ID: {post.get('owner_id', 'N/A')}")
        
        # Vérifier website_analyses
        analyses_query = {"user_id": self.user_id}
        analyses = list(self.db.website_analyses.find(analyses_query))
        print(f"   🔍 website_analyses avec user_id={self.user_id}: {len(analyses)}")
        
        if analyses:
            print(f"      Exemples d'analyses:")
            for i, analysis in enumerate(analyses[:3]):
                print(f"         {i+1}. ID: {analysis.get('id', 'N/A')}")
                print(f"            Business: {analysis.get('business_name', 'N/A')}")
                print(f"            URL: {analysis.get('website_url', 'N/A')}")
                print(f"            Score SEO: {analysis.get('seo_score', 'N/A')}")
                print(f"            User ID: {analysis.get('user_id', 'N/A')}")
        
        return len(posts), len(analyses)

    def test_posts_generated_endpoint(self):
        """Tester l'endpoint /posts/generated"""
        print(f"\n📄 TEST ENDPOINT /posts/generated")
        
        try:
            response = self.session.get(f"{self.base_url}/posts/generated")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('posts', [])
                count = data.get('count', 0)
                
                print(f"   ✅ Réponse reçue")
                print(f"   📊 Nombre de posts: {count}")
                
                if posts:
                    print(f"   📋 Posts trouvés:")
                    for i, post in enumerate(posts[:5]):
                        print(f"      {i+1}. {post.get('title', 'N/A')} ({post.get('platform', 'N/A')})")
                        print(f"         Mois: {post.get('target_month', 'N/A')}")
                        print(f"         Statut: {post.get('status', 'N/A')}")
                else:
                    print(f"   ⚠️ Aucun post retourné par l'API")
                
                return count
            else:
                print(f"   ❌ Erreur: {response.text}")
                return 0
                
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return 0

    def test_website_analysis_endpoint(self):
        """Tester l'endpoint /analysis"""
        print(f"\n🔍 TEST ENDPOINT /analysis")
        
        try:
            response = self.session.get(f"{self.base_url}/analysis")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # L'endpoint peut retourner différents formats
                if isinstance(data, list):
                    analyses = data
                elif isinstance(data, dict):
                    analyses = data.get('analyses', [data] if data else [])
                else:
                    analyses = []
                
                print(f"   ✅ Réponse reçue")
                print(f"   📊 Nombre d'analyses: {len(analyses)}")
                
                if analyses:
                    print(f"   📋 Analyses trouvées:")
                    for i, analysis in enumerate(analyses[:3]):
                        print(f"      {i+1}. {analysis.get('business_name', 'N/A')}")
                        print(f"         URL: {analysis.get('website_url', 'N/A')}")
                        print(f"         Score SEO: {analysis.get('seo_score', 'N/A')}")
                else:
                    print(f"   ⚠️ Aucune analyse retournée par l'API")
                
                return len(analyses)
            else:
                print(f"   ❌ Erreur: {response.text}")
                return 0
                
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return 0

    def debug_user_id_consistency(self):
        """Déboguer la cohérence des user_id"""
        print(f"\n🔍 DEBUG USER_ID CONSISTENCY")
        
        print(f"   🎯 User ID attendu: {USER_ID}")
        print(f"   🎯 User ID authentifié: {self.user_id}")
        print(f"   🎯 Correspondance: {'✅' if self.user_id == USER_ID else '❌'}")
        
        # Vérifier tous les user_id dans generated_posts
        all_posts = list(self.db.generated_posts.find({}))
        user_ids_in_posts = set(post.get('owner_id') for post in all_posts if post.get('owner_id'))
        
        print(f"   📄 User IDs dans generated_posts: {len(user_ids_in_posts)}")
        for uid in user_ids_in_posts:
            count = self.db.generated_posts.count_documents({"owner_id": uid})
            print(f"      {uid}: {count} posts")
        
        # Vérifier tous les user_id dans website_analyses
        all_analyses = list(self.db.website_analyses.find({}))
        user_ids_in_analyses = set(analysis.get('user_id') for analysis in all_analyses if analysis.get('user_id'))
        
        print(f"   🔍 User IDs dans website_analyses: {len(user_ids_in_analyses)}")
        for uid in user_ids_in_analyses:
            count = self.db.website_analyses.count_documents({"user_id": uid})
            print(f"      {uid}: {count} analyses")

    def run_verification(self):
        """Exécuter la vérification complète"""
        print("=" * 80)
        print("✅ VÉRIFICATION MIGRATION - ENDPOINTS ET BASE DE DONNÉES")
        print("=" * 80)
        print(f"API: {self.base_url}")
        print(f"User ID cible: {USER_ID}")
        print(f"Heure: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Étape 1: Authentification
        if not self.authenticate():
            print("\n❌ VÉRIFICATION INTERROMPUE - Échec authentification")
            return False
        
        # Étape 2: Connexion base
        if not self.connect_database():
            print("\n❌ VÉRIFICATION INTERROMPUE - Échec connexion MongoDB")
            return False
        
        # Étape 3: Vérification base de données
        db_posts, db_analyses = self.check_database_content()
        
        # Étape 4: Test endpoints
        api_posts = self.test_posts_generated_endpoint()
        api_analyses = self.test_website_analysis_endpoint()
        
        # Étape 5: Debug user_id
        self.debug_user_id_consistency()
        
        # RÉSUMÉ
        print("\n" + "=" * 80)
        print("📊 RÉSUMÉ VÉRIFICATION")
        print("=" * 80)
        
        print(f"🗄️ BASE DE DONNÉES:")
        print(f"   Posts dans generated_posts: {db_posts}")
        print(f"   Analyses dans website_analyses: {db_analyses}")
        
        print(f"\n📡 ENDPOINTS API:")
        print(f"   Posts via /posts/generated: {api_posts}")
        print(f"   Analyses via /analysis: {api_analyses}")
        
        print(f"\n🎯 DIAGNOSTIC:")
        if db_posts > 0 and api_posts == 0:
            print(f"   ❌ PROBLÈME: Posts en base mais pas via API")
            print(f"   🔧 Cause possible: Problème de mapping user_id/owner_id")
        elif db_posts > 0 and api_posts > 0:
            print(f"   ✅ SUCCÈS: Posts accessibles via API")
        
        if db_analyses > 0 and api_analyses == 0:
            print(f"   ❌ PROBLÈME: Analyses en base mais pas via API")
            print(f"   🔧 Cause possible: Problème de mapping user_id ou endpoint")
        elif db_analyses > 0 and api_analyses > 0:
            print(f"   ✅ SUCCÈS: Analyses accessibles via API")
        
        success = (api_posts > 0 or api_analyses > 0)
        
        if success:
            print(f"\n🎉 MIGRATION FONCTIONNELLE!")
            print(f"   Le frontend peut maintenant afficher les données")
        else:
            print(f"\n⚠️ MIGRATION PARTIELLE")
            print(f"   Données en base mais problèmes d'accès API")
        
        return success

    def cleanup(self):
        """Nettoyer les connexions"""
        if self.mongo_client:
            self.mongo_client.close()

def main():
    """Point d'entrée principal"""
    verification = MigrationVerification()
    
    try:
        success = verification.run_verification()
        
        if success:
            print(f"\n✅ VÉRIFICATION TERMINÉE - MIGRATION FONCTIONNELLE")
            sys.exit(0)
        else:
            print(f"\n⚠️ VÉRIFICATION TERMINÉE - PROBLÈMES DÉTECTÉS")
            sys.exit(1)
    
    finally:
        verification.cleanup()

if __name__ == "__main__":
    main()