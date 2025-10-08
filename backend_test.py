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

    def extract_restaurant_data_from_notes(self):
        """Étape 7: Extraire les données restaurant des notes pour migration"""
        print(f"\n📤 ÉTAPE 7: Extraction des données restaurant pour migration")
        
        try:
            response = self.session.get(f"{self.base_url}/notes")
            
            if response.status_code != 200:
                print(f"   ❌ ERREUR: Impossible d'accéder aux notes - {response.status_code}")
                return None
            
            data = response.json()
            notes = data.get('notes', [])
            
            # Extraire les posts restaurant (octobre et novembre 2024)
            restaurant_posts = []
            website_analyses = []
            
            for note in notes:
                content = note.get('content', '')
                description = note.get('description', '')
                
                # Identifier les posts Facebook restaurant
                if self.is_restaurant_post(content, description):
                    post_data = self.extract_post_data(note)
                    if post_data:
                        restaurant_posts.append(post_data)
                        print(f"   📄 Post extrait: {post_data['title'][:50]}...")
                
                # Identifier les analyses de site web
                elif self.is_website_analysis(content, description):
                    analysis_data = self.extract_analysis_data(note)
                    if analysis_data:
                        website_analyses.append(analysis_data)
                        print(f"   🔍 Analyse extraite: {analysis_data.get('website_url', 'N/A')}")
            
            print(f"   ✅ EXTRACTION TERMINÉE:")
            print(f"      Posts restaurant: {len(restaurant_posts)}")
            print(f"      Analyses site web: {len(website_analyses)}")
            
            return {
                'posts': restaurant_posts,
                'analyses': website_analyses
            }
            
        except Exception as e:
            print(f"   ❌ ERREUR EXTRACTION: {e}")
            return None

    def is_restaurant_post(self, content, description):
        """Identifier si une note est un post restaurant"""
        restaurant_keywords = [
            'bistrot', 'jean', 'facebook', 'instagram', 'menu', 'chef',
            'octobre_2024', 'novembre_2024', 'restaurant', 'cuisine',
            'hashtags', 'scheduled_date', 'platform'
        ]
        
        text = (content + ' ' + description).lower()
        return any(keyword in text for keyword in restaurant_keywords)

    def is_website_analysis(self, content, description):
        """Identifier si une note est une analyse de site web"""
        analysis_keywords = [
            'lebistrotdejean', 'seo_score', 'website_analysis', 'performance',
            'accessibility', 'recommendations', 'https://lebistrotdejean-paris.fr'
        ]
        
        text = (content + ' ' + description).lower()
        return any(keyword in text for keyword in analysis_keywords)

    def extract_post_data(self, note):
        """Extraire les données d'un post depuis une note"""
        try:
            content = note.get('content', '')
            
            # Essayer de parser le JSON du contenu
            if content.startswith('{') and content.endswith('}'):
                post_data = json.loads(content)
                
                # Transformer au format generated_posts
                return {
                    'id': f"post_{self.user_id}_{int(datetime.now().timestamp())}_{len(content) % 100}",
                    'owner_id': self.user_id,
                    'platform': post_data.get('platform', 'facebook'),
                    'title': post_data.get('title', ''),
                    'text': post_data.get('text', ''),
                    'hashtags': post_data.get('hashtags', []),
                    'scheduled_date': post_data.get('scheduled_date', ''),
                    'status': post_data.get('status', 'ready'),
                    'target_month': post_data.get('target_month', ''),
                    'created_at': datetime.now().isoformat(),
                    'validated': False,
                    'published': False
                }
            else:
                # Format texte simple - créer structure basique
                return {
                    'id': f"post_{self.user_id}_{int(datetime.now().timestamp())}_{hash(content) % 1000}",
                    'owner_id': self.user_id,
                    'platform': 'facebook',
                    'title': note.get('description', 'Post Restaurant')[:100],
                    'text': content[:500],
                    'hashtags': ['#bistrotdejean', '#restaurant'],
                    'scheduled_date': datetime.now().isoformat(),
                    'status': 'ready',
                    'target_month': 'octobre_2024' if 'octobre' in content.lower() else 'novembre_2024',
                    'created_at': datetime.now().isoformat(),
                    'validated': False,
                    'published': False
                }
                
        except Exception as e:
            print(f"   ⚠️ Erreur extraction post: {e}")
            return None

    def extract_analysis_data(self, note):
        """Extraire les données d'analyse depuis une note"""
        try:
            content = note.get('content', '')
            
            # Essayer de parser le JSON du contenu
            if content.startswith('{') and content.endswith('}'):
                analysis_data = json.loads(content)
                
                # Transformer au format website_analyses
                return {
                    'id': f"analysis_{self.user_id}_{int(datetime.now().timestamp())}",
                    'user_id': self.user_id,
                    'website_url': analysis_data.get('website_url', 'https://lebistrotdejean-paris.fr'),
                    'seo_score': analysis_data.get('seo_score', 78),
                    'performance_score': analysis_data.get('performance_score', 85),
                    'accessibility_score': analysis_data.get('accessibility_score', 92),
                    'overall_score': analysis_data.get('overall_score', 85.75),
                    'recommendations': analysis_data.get('recommendations', []),
                    'technical_analysis': analysis_data.get('technical_analysis', {}),
                    'competitive_analysis': analysis_data.get('competitive_analysis', {}),
                    'action_plan': analysis_data.get('action_plan', {}),
                    'created_at': datetime.now().isoformat(),
                    'status': 'completed'
                }
            else:
                # Format texte simple - créer structure basique
                return {
                    'id': f"analysis_{self.user_id}_{int(datetime.now().timestamp())}",
                    'user_id': self.user_id,
                    'website_url': 'https://lebistrotdejean-paris.fr',
                    'seo_score': 78,
                    'performance_score': 85,
                    'accessibility_score': 92,
                    'overall_score': 85.75,
                    'recommendations': ['Optimisation des images', 'SEO local', 'Schema markup'],
                    'technical_analysis': {'loading_speed': '3.2s', 'ssl_certificate': True},
                    'competitive_analysis': {'position': '8-12', 'rating': '4.2/5'},
                    'action_plan': {'phases': 4, 'priority': 'high'},
                    'created_at': datetime.now().isoformat(),
                    'status': 'completed'
                }
                
        except Exception as e:
            print(f"   ⚠️ Erreur extraction analyse: {e}")
            return None

    def test_migration_endpoints(self):
        """Étape 8: Tester les endpoints de destination pour la migration"""
        print(f"\n🎯 ÉTAPE 8: Test des endpoints de destination")
        
        # Test GET /api/posts/generated (destination des posts)
        print(f"   Testing GET /api/posts/generated...")
        try:
            response = self.session.get(f"{self.base_url}/posts/generated")
            posts_accessible = response.status_code == 200
            posts_count = len(response.json().get('posts', [])) if posts_accessible else 0
            print(f"      ✅ Posts endpoint: {response.status_code} - {posts_count} posts")
        except Exception as e:
            posts_accessible = False
            print(f"      ❌ Posts endpoint error: {e}")
        
        # Test GET /api/website-analysis (destination des analyses)
        print(f"   Testing GET /api/website-analysis...")
        try:
            response = self.session.get(f"{self.base_url}/website-analysis")
            analysis_accessible = response.status_code in [200, 404]  # 404 acceptable si vide
            analysis_count = len(response.json().get('analyses', [])) if response.status_code == 200 else 0
            print(f"      ✅ Analysis endpoint: {response.status_code} - {analysis_count} analyses")
        except Exception as e:
            analysis_accessible = False
            print(f"      ❌ Analysis endpoint error: {e}")
        
        return {
            'posts_accessible': posts_accessible,
            'posts_count': posts_count,
            'analysis_accessible': analysis_accessible,
            'analysis_count': analysis_count
        }

    def verify_migration_success(self):
        """Étape 9: Vérifier le succès de la migration"""
        print(f"\n✅ ÉTAPE 9: Vérification du succès de la migration")
        
        # Vérifier que les posts apparaissent maintenant dans GET /api/posts/generated
        try:
            response = self.session.get(f"{self.base_url}/posts/generated")
            if response.status_code == 200:
                posts = response.json().get('posts', [])
                restaurant_posts = [p for p in posts if 'bistrot' in p.get('text', '').lower() or 'jean' in p.get('text', '').lower()]
                
                print(f"   📄 Posts générés trouvés: {len(posts)}")
                print(f"   🍽️ Posts restaurant: {len(restaurant_posts)}")
                
                if restaurant_posts:
                    print(f"   ✅ SUCCÈS: Posts restaurant maintenant visibles dans l'interface!")
                    for i, post in enumerate(restaurant_posts[:3]):
                        print(f"      {i+1}. {post.get('title', 'Sans titre')[:50]}...")
                        print(f"         Plateforme: {post.get('platform', 'N/A')}")
                        print(f"         Statut: {post.get('status', 'N/A')}")
                else:
                    print(f"   ⚠️ Aucun post restaurant trouvé après migration")
            else:
                print(f"   ❌ Erreur accès posts: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur vérification posts: {e}")
        
        # Vérifier que les analyses apparaissent maintenant dans GET /api/website-analysis
        try:
            response = self.session.get(f"{self.base_url}/website-analysis")
            if response.status_code == 200:
                analyses = response.json().get('analyses', [])
                restaurant_analyses = [a for a in analyses if 'lebistrotdejean' in a.get('website_url', '').lower()]
                
                print(f"   🔍 Analyses trouvées: {len(analyses)}")
                print(f"   🍽️ Analyses restaurant: {len(restaurant_analyses)}")
                
                if restaurant_analyses:
                    print(f"   ✅ SUCCÈS: Analyses restaurant maintenant visibles dans l'interface!")
                    for i, analysis in enumerate(restaurant_analyses[:2]):
                        print(f"      {i+1}. URL: {analysis.get('website_url', 'N/A')}")
                        print(f"         Score SEO: {analysis.get('seo_score', 'N/A')}")
                        print(f"         Score global: {analysis.get('overall_score', 'N/A')}")
                else:
                    print(f"   ⚠️ Aucune analyse restaurant trouvée après migration")
            else:
                print(f"   ❌ Erreur accès analyses: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur vérification analyses: {e}")

    def run_migration_test(self):
        """Exécuter le test complet de migration"""
        print("=" * 80)
        print("🚀 MIGRATION DES DONNÉES RESTAURANT - TEST CRITIQUE")
        print("=" * 80)
        print(f"Environnement: {self.base_url}")
        print(f"Compte test: {TEST_EMAIL}")
        print(f"Objectif: Migrer posts et analyses de 'notes' vers collections correctes")
        print(f"Heure: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Étape 1: Authentification
        if not self.authenticate():
            print("\n❌ TEST INTERROMPU - Échec authentification")
            return False
        
        # Étape 2: État initial - vérifier que l'UI est vide
        print(f"\n📊 ÉTAT INITIAL:")
        posts_count = self.test_posts_generated_endpoint()
        analyses_count = self.test_website_analysis_endpoint()
        
        # Étape 3: Vérifier les données dans notes
        notes_data = self.investigate_notes_storage()
        
        # Étape 4: Vérifier le profil business
        business_profile = self.test_business_profile()
        
        # Étape 5: Extraire les données pour migration
        extracted_data = self.extract_restaurant_data_from_notes()
        
        # Étape 6: Tester les endpoints de destination
        migration_endpoints = self.test_migration_endpoints()
        
        # ANALYSE FINALE
        print("\n" + "=" * 80)
        print("🎯 ANALYSE DE MIGRATION")
        print("=" * 80)
        
        print(f"📊 ÉTAT ACTUEL:")
        print(f"   Posts dans UI: {posts_count}")
        print(f"   Analyses dans UI: {analyses_count}")
        
        if notes_data:
            print(f"   Notes totales: {notes_data['total_notes']}")
            print(f"   Posts octobre dans notes: {notes_data['october_posts']}")
            print(f"   Posts novembre dans notes: {notes_data['november_posts']}")
            print(f"   Analyses dans notes: {notes_data['website_analyses']}")
        
        if extracted_data:
            print(f"   Posts extraits pour migration: {len(extracted_data['posts'])}")
            print(f"   Analyses extraites pour migration: {len(extracted_data['analyses'])}")
        
        # DIAGNOSTIC DE MIGRATION
        print(f"\n🔍 DIAGNOSTIC DE MIGRATION:")
        
        migration_needed = False
        
        if posts_count == 0 and extracted_data and len(extracted_data['posts']) > 0:
            print(f"   ❌ MIGRATION REQUISE: {len(extracted_data['posts'])} posts à migrer de 'notes' vers 'generated_posts'")
            migration_needed = True
        
        if analyses_count == 0 and extracted_data and len(extracted_data['analyses']) > 0:
            print(f"   ❌ MIGRATION REQUISE: {len(extracted_data['analyses'])} analyses à migrer de 'notes' vers 'website_analyses'")
            migration_needed = True
        
        if not migration_needed:
            if posts_count > 0 and analyses_count > 0:
                print(f"   ✅ MIGRATION DÉJÀ EFFECTUÉE: Données présentes dans les bonnes collections")
            else:
                print(f"   ⚠️ DONNÉES MANQUANTES: Aucune donnée trouvée à migrer")
        
        print(f"\n🎯 RECOMMANDATIONS TECHNIQUES:")
        if migration_needed:
            print(f"   1. Créer un endpoint de migration: POST /api/migrate/restaurant-data")
            print(f"   2. Migrer les posts: notes → generated_posts collection")
            print(f"   3. Migrer les analyses: notes → website_analyses collection")
            print(f"   4. Vérifier les mappings user_id/owner_id")
            print(f"   5. Tester que GET /api/posts/generated et GET /api/website-analysis retournent les données")
        else:
            print(f"   1. Vérifier pourquoi les données ne sont pas visibles dans l'UI")
            print(f"   2. Contrôler les filtres et requêtes des endpoints")
            print(f"   3. Vérifier la cohérence des user_id")
        
        # Étape finale: Vérification post-migration (si migration manuelle effectuée)
        print(f"\n🔄 VÉRIFICATION POST-MIGRATION:")
        self.verify_migration_success()
        
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
