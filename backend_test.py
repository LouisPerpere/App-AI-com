#!/usr/bin/env python3
"""
MIGRATION DES DONNÉES RESTAURANT - Test critique pour la migration des données
Test pour migrer les posts et analyses du restaurant de la collection 'notes' vers les collections correctes
Environnement: LIVE (https://claire-marcus.com/api)
Compte: test@claire-marcus.com
"""

import requests
import json
import sys
from datetime import datetime

# Configuration LIVE
LIVE_BASE_URL = "https://claire-marcus.com/api"
TEST_EMAIL = "test@claire-marcus.com"
TEST_PASSWORD = "test123!"

class RestaurantDataMigrationTest:
    def __init__(self):
        self.base_url = LIVE_BASE_URL
        self.token = None
        self.user_id = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Backend-Test-Investigation/1.0'
        })

    def authenticate(self):
        """Étape 1: Authentification avec test@claire-marcus.com"""
        print(f"🔐 ÉTAPE 1: Authentification sur {self.base_url}")
        print(f"   Email: {TEST_EMAIL}")
        print(f"   Password: {TEST_PASSWORD}")
        
        try:
            response = self.session.post(f"{self.base_url}/auth/login-robust", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token')
                self.user_id = data.get('user_id')
                
                # Configurer l'en-tête d'autorisation
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}'
                })
                
                print(f"   ✅ AUTHENTIFICATION RÉUSSIE")
                print(f"   User ID: {self.user_id}")
                print(f"   Token: {self.token[:30]}...")
                return True
            else:
                print(f"   ❌ ÉCHEC AUTHENTIFICATION: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ ERREUR AUTHENTIFICATION: {e}")
            return False

    def test_posts_generated_endpoint(self):
        """Étape 2: Tester GET /api/posts/generated (ce que voit la page Posts)"""
        print(f"\n📄 ÉTAPE 2: Test endpoint Posts - GET /api/posts/generated")
        
        try:
            response = self.session.get(f"{self.base_url}/posts/generated")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('posts', [])
                print(f"   ✅ ENDPOINT ACCESSIBLE")
                print(f"   Nombre de posts: {len(posts)}")
                
                if posts:
                    print(f"   📊 POSTS TROUVÉS:")
                    for i, post in enumerate(posts[:5]):  # Afficher les 5 premiers
                        print(f"      {i+1}. ID: {post.get('id', 'N/A')}")
                        print(f"         Titre: {post.get('title', 'N/A')}")
                        print(f"         Plateforme: {post.get('platform', 'N/A')}")
                        print(f"         Mois cible: {post.get('target_month', 'N/A')}")
                        print(f"         Statut: {post.get('status', 'N/A')}")
                else:
                    print(f"   ⚠️ AUCUN POST TROUVÉ - C'EST LE PROBLÈME!")
                
                return len(posts)
            else:
                print(f"   ❌ ERREUR ENDPOINT: {response.text}")
                return 0
                
        except Exception as e:
            print(f"   ❌ ERREUR REQUÊTE: {e}")
            return 0

    def test_website_analysis_endpoint(self):
        """Étape 3: Tester GET /api/website-analysis (ce que voit la page Analyse)"""
        print(f"\n🔍 ÉTAPE 3: Test endpoint Analyse - GET /api/website-analysis")
        
        try:
            response = self.session.get(f"{self.base_url}/website-analysis")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                analyses = data.get('analyses', [])
                print(f"   ✅ ENDPOINT ACCESSIBLE")
                print(f"   Nombre d'analyses: {len(analyses)}")
                
                if analyses:
                    print(f"   📊 ANALYSES TROUVÉES:")
                    for i, analysis in enumerate(analyses[:3]):  # Afficher les 3 premières
                        print(f"      {i+1}. ID: {analysis.get('id', 'N/A')}")
                        print(f"         URL: {analysis.get('website_url', 'N/A')}")
                        print(f"         Score: {analysis.get('seo_score', 'N/A')}")
                        print(f"         Date: {analysis.get('created_at', 'N/A')}")
                else:
                    print(f"   ⚠️ AUCUNE ANALYSE TROUVÉE - C'EST LE PROBLÈME!")
                
                return len(analyses)
            else:
                print(f"   ❌ ERREUR ENDPOINT: {response.text}")
                return 0
                
        except Exception as e:
            print(f"   ❌ ERREUR REQUÊTE: {e}")
            return 0

    def investigate_notes_storage(self):
        """Étape 4: Investiguer le stockage dans /api/notes (où les données ont été créées)"""
        print(f"\n📝 ÉTAPE 4: Investigation stockage Notes - GET /api/notes")
        
        try:
            response = self.session.get(f"{self.base_url}/notes")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                notes = data.get('notes', [])
                print(f"   ✅ ENDPOINT ACCESSIBLE")
                print(f"   Nombre total de notes: {len(notes)}")
                
                # Analyser les types de notes
                restaurant_notes = []
                website_analyses = []
                october_posts = []
                november_posts = []
                
                for note in notes:
                    content = note.get('content', '').lower()
                    description = note.get('description', '').lower()
                    
                    # Identifier les analyses de site web
                    if 'lebistrotdejean' in content or 'seo' in content or 'analyse' in description:
                        website_analyses.append(note)
                    
                    # Identifier les posts d'octobre
                    elif 'octobre' in content or 'octobre' in description:
                        october_posts.append(note)
                    
                    # Identifier les posts de novembre
                    elif 'novembre' in content or 'novembre' in description:
                        november_posts.append(note)
                    
                    # Autres notes liées au restaurant
                    elif 'bistrot' in content or 'jean' in content or 'restaurant' in content:
                        restaurant_notes.append(note)
                
                print(f"   📊 ANALYSE DES NOTES:")
                print(f"      Analyses de site web: {len(website_analyses)}")
                print(f"      Posts octobre: {len(october_posts)}")
                print(f"      Posts novembre: {len(november_posts)}")
                print(f"      Autres notes restaurant: {len(restaurant_notes)}")
                
                # Afficher quelques exemples
                if website_analyses:
                    print(f"   🔍 EXEMPLE ANALYSE SITE WEB:")
                    analysis = website_analyses[0]
                    print(f"      ID: {analysis.get('note_id', 'N/A')}")
                    print(f"      Description: {analysis.get('description', 'N/A')}")
                    print(f"      Contenu: {analysis.get('content', '')[:200]}...")
                
                if october_posts:
                    print(f"   🔍 EXEMPLE POST OCTOBRE:")
                    post = october_posts[0]
                    print(f"      ID: {post.get('note_id', 'N/A')}")
                    print(f"      Description: {post.get('description', 'N/A')}")
                    print(f"      Contenu: {post.get('content', '')[:200]}...")
                
                return {
                    'total_notes': len(notes),
                    'website_analyses': len(website_analyses),
                    'october_posts': len(october_posts),
                    'november_posts': len(november_posts),
                    'restaurant_notes': len(restaurant_notes)
                }
            else:
                print(f"   ❌ ERREUR ENDPOINT: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ ERREUR REQUÊTE: {e}")
            return None

    def test_business_profile(self):
        """Étape 5: Vérifier le profil business"""
        print(f"\n🏢 ÉTAPE 5: Test profil business - GET /api/business-profile")
        
        try:
            response = self.session.get(f"{self.base_url}/business-profile")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                business_name = data.get('business_name')
                industry = data.get('industry')
                website_url = data.get('website_url')
                
                print(f"   ✅ PROFIL BUSINESS ACCESSIBLE")
                print(f"   Nom: {business_name}")
                print(f"   Industrie: {industry}")
                print(f"   Site web: {website_url}")
                
                return data
            else:
                print(f"   ❌ ERREUR ENDPOINT: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ ERREUR REQUÊTE: {e}")
            return None

    def investigate_database_collections(self):
        """Étape 6: Investiguer les collections de base de données disponibles"""
        print(f"\n🗄️ ÉTAPE 6: Investigation collections base de données")
        
        # Tester différents endpoints pour identifier où les données devraient être
        endpoints_to_test = [
            "/posts/generated",
            "/website-analysis", 
            "/notes",
            "/content/pending",
            "/business-profile"
        ]
        
        results = {}
        
        for endpoint in endpoints_to_test:
            try:
                print(f"   Testing {endpoint}...")
                response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Compter les éléments selon le type de réponse
                    if 'posts' in data:
                        count = len(data['posts'])
                    elif 'analyses' in data:
                        count = len(data['analyses'])
                    elif 'notes' in data:
                        count = len(data['notes'])
                    elif 'content' in data:
                        count = len(data['content'])
                    elif isinstance(data, list):
                        count = len(data)
                    else:
                        count = 1 if data else 0
                    
                    results[endpoint] = {
                        'status': response.status_code,
                        'accessible': True,
                        'count': count
                    }
                    print(f"      ✅ {endpoint}: {count} éléments")
                else:
                    results[endpoint] = {
                        'status': response.status_code,
                        'accessible': False,
                        'error': response.text[:100]
                    }
                    print(f"      ❌ {endpoint}: {response.status_code}")
                    
            except Exception as e:
                results[endpoint] = {
                    'status': 'error',
                    'accessible': False,
                    'error': str(e)
                }
                print(f"      ❌ {endpoint}: {e}")
        
        return results

    def run_investigation(self):
        """Exécuter l'investigation complète"""
        print("=" * 80)
        print("🚨 INVESTIGATION URGENTE - INTERFACE UTILISATEUR VIDE")
        print("=" * 80)
        print(f"Environnement: {self.base_url}")
        print(f"Compte test: {TEST_EMAIL}")
        print(f"Heure: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Étape 1: Authentification
        if not self.authenticate():
            print("\n❌ INVESTIGATION INTERROMPUE - Échec authentification")
            return False
        
        # Étape 2: Test endpoint Posts
        posts_count = self.test_posts_generated_endpoint()
        
        # Étape 3: Test endpoint Analyse
        analyses_count = self.test_website_analysis_endpoint()
        
        # Étape 4: Investigation Notes
        notes_data = self.investigate_notes_storage()
        
        # Étape 5: Test profil business
        business_profile = self.test_business_profile()
        
        # Étape 6: Investigation collections
        db_results = self.investigate_database_collections()
        
        # ANALYSE FINALE
        print("\n" + "=" * 80)
        print("🔍 ANALYSE FINALE - CAUSE RACINE")
        print("=" * 80)
        
        print(f"📊 RÉSULTATS:")
        print(f"   Posts générés (UI): {posts_count}")
        print(f"   Analyses site web (UI): {analyses_count}")
        
        if notes_data:
            print(f"   Notes totales: {notes_data['total_notes']}")
            print(f"   Analyses dans notes: {notes_data['website_analyses']}")
            print(f"   Posts octobre dans notes: {notes_data['october_posts']}")
            print(f"   Posts novembre dans notes: {notes_data['november_posts']}")
        
        # DIAGNOSTIC
        print(f"\n🎯 DIAGNOSTIC:")
        
        if posts_count == 0 and notes_data and (notes_data['october_posts'] > 0 or notes_data['november_posts'] > 0):
            print(f"   ❌ PROBLÈME IDENTIFIÉ: Posts stockés dans /notes mais pas dans /posts/generated")
            print(f"   🔧 SOLUTION: Les posts doivent être migrés de la collection 'notes' vers 'generated_posts'")
        
        if analyses_count == 0 and notes_data and notes_data['website_analyses'] > 0:
            print(f"   ❌ PROBLÈME IDENTIFIÉ: Analyses stockées dans /notes mais pas dans /website-analysis")
            print(f"   🔧 SOLUTION: Les analyses doivent être migrées de la collection 'notes' vers 'website_analysis'")
        
        if posts_count == 0 and analyses_count == 0:
            if notes_data and notes_data['total_notes'] > 0:
                print(f"   ❌ CAUSE RACINE: Données créées dans mauvaises tables")
                print(f"   📋 Les données existent mais dans la collection 'notes' au lieu des collections spécialisées")
            else:
                print(f"   ❌ CAUSE RACINE: Aucune donnée trouvée nulle part")
                print(f"   📋 Les données n'ont peut-être pas été créées ou ont été supprimées")
        
        print(f"\n🎯 RECOMMANDATIONS:")
        print(f"   1. Vérifier les endpoints que le frontend utilise réellement")
        print(f"   2. Migrer les données de /notes vers les bonnes collections")
        print(f"   3. Corriger le mapping user_id si nécessaire")
        print(f"   4. Tester la synchronisation cache/base de données")
        
        return True

def main():
    """Point d'entrée principal"""
    investigation = LiveUIInvestigation()
    success = investigation.run_investigation()
    
    if success:
        print(f"\n✅ INVESTIGATION TERMINÉE AVEC SUCCÈS")
        sys.exit(0)
    else:
        print(f"\n❌ INVESTIGATION ÉCHOUÉE")
        sys.exit(1)

if __name__ == "__main__":
    main()
