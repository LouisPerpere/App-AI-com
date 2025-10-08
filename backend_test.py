#!/usr/bin/env python3
"""
INVESTIGATION URGENTE - Interface utilisateur vide malgré création de contenu
Test critique pour identifier pourquoi l'UI est vide pour test@claire-marcus.com
"""

import requests
import json
import sys
from datetime import datetime

# Configuration LIVE
LIVE_BASE_URL = "https://claire-marcus.com/api"
TEST_EMAIL = "test@claire-marcus.com"
TEST_PASSWORD = "test123!"

class LiveUIInvestigation:
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
                data = response.json()
                self.log("✅ LIVE Debug endpoint accessible")
                
                # Analyze connection data
                total_connections = data.get('total_connections', 0)
                active_connections = data.get('active_connections', 0)
                facebook_connections = data.get('facebook_connections', 0)
                instagram_connections = data.get('instagram_connections', 0)
                
                self.log(f"📊 LIVE Database Analysis:")
                self.log(f"   Total connections: {total_connections}")
                self.log(f"   Active connections: {active_connections}")
                self.log(f"   Facebook connections: {facebook_connections}")
                self.log(f"   Instagram connections: {instagram_connections}")
                
                # Check for detailed connection information
                connections_detail = data.get('connections_detail', [])
                
                # Analyze Facebook connections
                facebook_details = [conn for conn in connections_detail if conn.get('platform') == 'facebook']
                if facebook_details:
                    self.log(f"📋 LIVE Facebook Connection Details:")
                    for i, conn in enumerate(facebook_details, 1):
                        token = conn.get('access_token', 'None')
                        self.log(f"   Facebook Connection {i}:")
                        self.log(f"     Active: {conn.get('active', conn.get('is_active'))}")
                        self.log(f"     Token type: {'EAA (Long-lived)' if token.startswith('EAA') else 'Temp/Invalid' if token.startswith('temp_') else 'Unknown'}")
                        self.log(f"     Token preview: {token[:30]}..." if token != 'None' else "     Token: None")
                        self.log(f"     Connected at: {conn.get('connected_at', 'Unknown')}")
                        self.log(f"     Collection: {conn.get('collection', 'Unknown')}")
                else:
                    self.log("   No Facebook connections found in LIVE database")
                
                # Analyze Instagram connections
                instagram_details = [conn for conn in connections_detail if conn.get('platform') == 'instagram']
                if instagram_details:
                    self.log(f"📋 LIVE Instagram Connection Details:")
                    for i, conn in enumerate(instagram_details, 1):
                        token = conn.get('access_token', 'None')
                        self.log(f"   Instagram Connection {i}:")
                        self.log(f"     Active: {conn.get('active', conn.get('is_active'))}")
                        self.log(f"     Token type: {'EAA (Long-lived)' if token.startswith('EAA') else 'Temp/Invalid' if token.startswith('temp_') else 'Unknown'}")
                        self.log(f"     Token preview: {token[:30]}..." if token != 'None' else "     Token: None")
                        self.log(f"     Connected at: {conn.get('connected_at', 'Unknown')}")
                        self.log(f"     Collection: {conn.get('collection', 'Unknown')}")
                else:
                    self.log("   No Instagram connections found in LIVE database")
                
                return True
            else:
                self.log(f"❌ LIVE Debug endpoint failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ LIVE Database analysis error: {str(e)}", "ERROR")
            return False
    
    def compare_facebook_vs_instagram_oauth_urls(self):
        """Step 3: Compare Facebook vs Instagram OAuth URL generation on LIVE"""
        self.log("🔄 STEP 3: Facebook vs Instagram OAuth URL Comparison on LIVE")
        
        try:
            # Test Facebook OAuth URL generation
            facebook_response = self.session.get(f"{LIVE_BACKEND_URL}/social/facebook/auth-url")
            
            if facebook_response.status_code == 200:
                facebook_data = facebook_response.json()
                facebook_url = facebook_data.get('auth_url', '')
                
                self.log("✅ Facebook OAuth URL generation working on LIVE")
                self.log(f"   Facebook URL: {facebook_url[:100]}..." if facebook_url else "   No URL generated")
                
                # Parse Facebook URL parameters
                if facebook_url:
                    parsed_fb = urllib.parse.urlparse(facebook_url)
                    fb_params = urllib.parse.parse_qs(parsed_fb.query)
                    
                    self.log("📋 Facebook OAuth Parameters:")
                    self.log(f"   Client ID: {fb_params.get('client_id', ['Not found'])[0]}")
                    self.log(f"   Config ID: {fb_params.get('config_id', ['Not found'])[0]}")
                    self.log(f"   Redirect URI: {fb_params.get('redirect_uri', ['Not found'])[0]}")
                    self.log(f"   State format: {fb_params.get('state', ['Not found'])[0][:50]}..." if fb_params.get('state') else "   State: Not found")
                    
            else:
                self.log(f"❌ Facebook OAuth URL generation failed on LIVE: {facebook_response.status_code}")
            
            # Test Instagram OAuth URL generation
            instagram_response = self.session.get(f"{LIVE_BACKEND_URL}/social/instagram/auth-url")
            
            if instagram_response.status_code == 200:
                instagram_data = instagram_response.json()
                instagram_url = instagram_data.get('auth_url', '')
                
                self.log("✅ Instagram OAuth URL generation working on LIVE")
                self.log(f"   Instagram URL: {instagram_url[:100]}..." if instagram_url else "   No URL generated")
                
                # Parse Instagram URL parameters
                if instagram_url:
                    parsed_ig = urllib.parse.urlparse(instagram_url)
                    ig_params = urllib.parse.parse_qs(parsed_ig.query)
                    
                    self.log("📋 Instagram OAuth Parameters:")
                    self.log(f"   Client ID: {ig_params.get('client_id', ['Not found'])[0]}")
                    self.log(f"   Config ID: {ig_params.get('config_id', ['Not found'])[0]}")
                    self.log(f"   Redirect URI: {ig_params.get('redirect_uri', ['Not found'])[0]}")
                    self.log(f"   State format: {ig_params.get('state', ['Not found'])[0][:50]}..." if ig_params.get('state') else "   State: Not found")
                    
                    # Compare with Facebook parameters
                    fb_client_id = fb_params.get('client_id', [''])[0] if 'fb_params' in locals() else ''
                    ig_client_id = ig_params.get('client_id', [''])[0]
                    
                    if fb_client_id == ig_client_id:
                        self.log("   ✅ Client ID matches Facebook (correct)")
                    else:
                        self.log("   ❌ Client ID differs from Facebook (potential issue)")
                        
            else:
                self.log(f"❌ Instagram OAuth URL generation failed on LIVE: {instagram_response.status_code}")
            
            return True
            
        except Exception as e:
            self.log(f"❌ OAuth URL comparison error: {str(e)}", "ERROR")
            return False
    
    def test_facebook_vs_instagram_callback_logic(self):
        """Step 4: Test Facebook vs Instagram callback logic on LIVE"""
        self.log("🔄 STEP 4: Facebook vs Instagram Callback Logic Testing on LIVE")
        
        try:
            # Test Facebook callback with simulation
            facebook_callback_url = f"{LIVE_BACKEND_URL}/social/facebook/callback"
            facebook_test_params = {
                'code': 'test_facebook_code_live_diagnostic',
                'state': f'facebook_test|{self.user_id}'
            }
            
            self.log(f"🧪 Testing Facebook callback on LIVE")
            self.log(f"   Callback URL: {facebook_callback_url}")
            self.log(f"   Test code: {facebook_test_params['code']}")
            self.log(f"   State: {facebook_test_params['state']}")
            
            # Make Facebook callback request
            fb_response = self.session.get(facebook_callback_url, params=facebook_test_params, allow_redirects=False)
            
            self.log(f"📡 Facebook callback response: Status {fb_response.status_code}")
            
            if fb_response.status_code in [302, 307]:
                fb_redirect_location = fb_response.headers.get('Location', '')
                self.log(f"   Facebook redirect to: {fb_redirect_location}")
                
                # Analyze redirect for success/error indicators
                if 'facebook_success=true' in fb_redirect_location:
                    self.log("   ✅ Facebook callback indicates success")
                elif 'facebook_error' in fb_redirect_location or 'error' in fb_redirect_location:
                    self.log("   ❌ Facebook callback indicates error")
                    # Extract error details
                    if 'error=' in fb_redirect_location:
                        error_part = fb_redirect_location.split('error=')[1].split('&')[0]
                        self.log(f"   Error details: {urllib.parse.unquote(error_part)}")
                else:
                    self.log("   ⚠️ Facebook callback redirect unclear")
            
            # Test Instagram callback with simulation
            instagram_callback_url = f"{LIVE_BACKEND_URL}/social/instagram/callback"
            instagram_test_params = {
                'code': 'test_instagram_code_live_diagnostic',
                'state': f'instagram_test|{self.user_id}'
            }
            
            self.log(f"🧪 Testing Instagram callback on LIVE")
            self.log(f"   Callback URL: {instagram_callback_url}")
            self.log(f"   Test code: {instagram_test_params['code']}")
            self.log(f"   State: {instagram_test_params['state']}")
            
            # Make Instagram callback request
            ig_response = self.session.get(instagram_callback_url, params=instagram_test_params, allow_redirects=False)
            
            self.log(f"📡 Instagram callback response: Status {ig_response.status_code}")
            
            if ig_response.status_code in [302, 307]:
                ig_redirect_location = ig_response.headers.get('Location', '')
                self.log(f"   Instagram redirect to: {ig_redirect_location}")
                
                # Analyze redirect for success/error indicators
                if 'instagram_success=true' in ig_redirect_location:
                    self.log("   ✅ Instagram callback indicates success")
                elif 'instagram_error' in ig_redirect_location or 'error' in ig_redirect_location:
                    self.log("   ❌ Instagram callback indicates error")
                    # Extract error details
                    if 'error=' in ig_redirect_location:
                        error_part = ig_redirect_location.split('error=')[1].split('&')[0]
                        self.log(f"   Error details: {urllib.parse.unquote(error_part)}")
                else:
                    self.log("   ⚠️ Instagram callback redirect unclear")
            
            # Compare callback behaviors
            self.log("🔍 Callback Logic Comparison:")
            self.log(f"   Facebook status: {fb_response.status_code}")
            self.log(f"   Instagram status: {ig_response.status_code}")
            
            if fb_response.status_code == ig_response.status_code:
                self.log("   ✅ Both callbacks return same status code")
            else:
                self.log("   ❌ Callbacks return different status codes (potential issue)")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Callback logic testing error: {str(e)}", "ERROR")
            return False
    
    def analyze_token_persistence_issue(self):
        """Step 5: Analyze why Instagram tokens don't persist on LIVE"""
        self.log("🔑 STEP 5: Instagram Token Persistence Analysis on LIVE")
        
        try:
            # Check connections state before and after callback simulation
            self.log("🔍 Checking connections state after callback tests")
            
            # Wait for potential async processing
            time.sleep(3)
            
            # Re-check database state
            response = self.session.get(f"{LIVE_BACKEND_URL}/debug/social-connections")
            
            if response.status_code == 200:
                data = response.json()
                connections_detail = data.get('connections_detail', [])
                
                # Look for any new connections created by callback tests
                facebook_connections = [conn for conn in connections_detail if conn.get('platform') == 'facebook']
                instagram_connections = [conn for conn in connections_detail if conn.get('platform') == 'instagram']
                
                self.log(f"📊 Post-callback connection analysis:")
                self.log(f"   Facebook connections: {len(facebook_connections)}")
                self.log(f"   Instagram connections: {len(instagram_connections)}")
                
                # Analyze token formats and persistence
                for platform, connections in [('Facebook', facebook_connections), ('Instagram', instagram_connections)]:
                    if connections:
                        self.log(f"📋 {platform} Token Analysis:")
                        for i, conn in enumerate(connections, 1):
                            token = conn.get('access_token', '')
                            active = conn.get('active', conn.get('is_active', False))
                            
                            self.log(f"   Connection {i}:")
                            self.log(f"     Active: {active}")
                            
                            if not token or token == 'None':
                                self.log(f"     ❌ No token found")
                            elif token.startswith('temp_'):
                                self.log(f"     ❌ Temporary token: {token[:30]}...")
                                self.log(f"     🚨 PERSISTENCE ISSUE: Using temp token instead of real OAuth token")
                            elif token.startswith('EAA'):
                                self.log(f"     ✅ Long-lived token: {token[:30]}...")
                                self.log(f"     📅 Proper Facebook/Instagram token format")
                            else:
                                self.log(f"     ⚠️ Unknown token format: {token[:30]}...")
                            
                            # Check collection consistency
                            collection = conn.get('collection', 'Unknown')
                            self.log(f"     Collection: {collection}")
                            
                            if collection == 'social_connections' and platform == 'Instagram':
                                self.log(f"     🚨 COLLECTION ISSUE: Instagram in old collection")
                            elif collection == 'social_media_connections':
                                self.log(f"     ✅ Correct collection")
                    else:
                        self.log(f"   No {platform} connections found")
                
                # Test frontend visibility
                frontend_response = self.session.get(f"{LIVE_BACKEND_URL}/social/connections")
                if frontend_response.status_code == 200:
                    frontend_data = frontend_response.json()
                    
                    if isinstance(frontend_data, list):
                        frontend_connections = frontend_data
                    else:
                        frontend_connections = frontend_data.get('connections', [])
                    
                    self.log(f"🌐 Frontend visibility:")
                    self.log(f"   Frontend sees {len(frontend_connections)} connections")
                    
                    # Check for Instagram visibility
                    instagram_visible = any(
                        (isinstance(conn, dict) and conn.get('platform') == 'instagram') or
                        (isinstance(conn, str) and 'instagram' in conn.lower())
                        for conn in frontend_connections
                    )
                    
                    if instagram_visible:
                        self.log("   ✅ Instagram connections visible to frontend")
                    else:
                        self.log("   ❌ Instagram connections NOT visible to frontend")
                        self.log("   🚨 PERSISTENCE ISSUE: Backend has connections but frontend doesn't see them")
                
                return True
            else:
                self.log(f"❌ Token persistence analysis failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Token persistence analysis error: {str(e)}", "ERROR")
            return False
    
    def test_publication_endpoints_comparison(self):
        """Step 6: Test publication endpoints to verify token validity"""
        self.log("📤 STEP 6: Publication Endpoints Comparison on LIVE")
        
        try:
            # Test Facebook publication
            self.log("🧪 Testing Facebook publication on LIVE")
            
            facebook_pub_response = self.session.post(f"{LIVE_BACKEND_URL}/social/facebook/publish-simple", json={
                "text": "Test Facebook publication for LIVE diagnostic",
                "image_url": "https://via.placeholder.com/400x400.jpg"
            })
            
            self.log(f"📡 Facebook publication test: Status {facebook_pub_response.status_code}")
            
            if facebook_pub_response.status_code == 200:
                fb_pub_data = facebook_pub_response.json()
                self.log("   ✅ Facebook publication would succeed")
                self.log(f"   Response: {fb_pub_data}")
            elif facebook_pub_response.status_code == 400:
                fb_error_data = facebook_pub_response.json()
                fb_error_message = fb_error_data.get('error', fb_error_data.get('detail', 'Unknown error'))
                self.log(f"   Facebook error: {fb_error_message}")
                
                if 'Aucune connexion Facebook' in fb_error_message:
                    self.log("   ❌ No Facebook connections found")
                elif 'Invalid OAuth access token' in fb_error_message:
                    self.log("   ❌ Invalid Facebook token (temp token issue)")
                else:
                    self.log("   ⚠️ Other Facebook error")
            
            # Test Instagram publication
            self.log("🧪 Testing Instagram publication on LIVE")
            
            instagram_pub_response = self.session.post(f"{LIVE_BACKEND_URL}/social/instagram/publish-simple", json={
                "text": "Test Instagram publication for LIVE diagnostic",
                "image_url": "https://via.placeholder.com/400x400.jpg"
            })
            
            self.log(f"📡 Instagram publication test: Status {instagram_pub_response.status_code}")
            
            if instagram_pub_response.status_code == 200:
                ig_pub_data = instagram_pub_response.json()
                self.log("   ✅ Instagram publication would succeed")
                self.log(f"   Response: {ig_pub_data}")
            elif instagram_pub_response.status_code == 400:
                ig_error_data = instagram_pub_response.json()
                ig_error_message = ig_error_data.get('error', ig_error_data.get('detail', 'Unknown error'))
                self.log(f"   Instagram error: {ig_error_message}")
                
                if 'Aucune connexion Instagram' in ig_error_message:
                    self.log("   ❌ No Instagram connections found")
                elif 'Invalid OAuth access token' in ig_error_message:
                    self.log("   ❌ Invalid Instagram token (temp token issue)")
                else:
                    self.log("   ⚠️ Other Instagram error")
            
            # Compare publication results
            self.log("🔍 Publication Comparison:")
            self.log(f"   Facebook status: {facebook_pub_response.status_code}")
            self.log(f"   Instagram status: {instagram_pub_response.status_code}")
            
            if facebook_pub_response.status_code == 200 and instagram_pub_response.status_code != 200:
                self.log("   🚨 CRITICAL: Facebook works but Instagram doesn't (matches user report)")
            elif facebook_pub_response.status_code != 200 and instagram_pub_response.status_code == 200:
                self.log("   ⚠️ Instagram works but Facebook doesn't")
            elif facebook_pub_response.status_code == instagram_pub_response.status_code:
                self.log("   ✅ Both platforms have same status")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Publication endpoints testing error: {str(e)}", "ERROR")
            return False
    
    def identify_root_cause_and_solution(self):
        """Step 7: Identify root cause and provide solution"""
        self.log("🎯 STEP 7: Root Cause Analysis and Solution")
        
        try:
            # Final comprehensive check
            response = self.session.get(f"{LIVE_BACKEND_URL}/debug/social-connections")
            
            if response.status_code == 200:
                data = response.json()
                
                facebook_connections = data.get('facebook_connections', 0)
                instagram_connections = data.get('instagram_connections', 0)
                active_connections = data.get('active_connections', 0)
                
                connections_detail = data.get('connections_detail', [])
                
                # Analyze the specific issue
                self.log("🔍 ROOT CAUSE ANALYSIS:")
                
                # Check if Facebook works but Instagram doesn't
                facebook_active = any(
                    conn.get('platform') == 'facebook' and 
                    conn.get('active', conn.get('is_active', False)) and
                    conn.get('access_token', '').startswith('EAA')
                    for conn in connections_detail
                )
                
                instagram_active = any(
                    conn.get('platform') == 'instagram' and 
                    conn.get('active', conn.get('is_active', False)) and
                    conn.get('access_token', '').startswith('EAA')
                    for conn in connections_detail
                )
                
                if facebook_active and not instagram_active:
                    self.log("   🚨 CONFIRMED: Facebook works but Instagram doesn't persist")
                    self.log("   📋 Possible causes:")
                    self.log("     1. Instagram callback uses different collection than Facebook")
                    self.log("     2. Instagram callback creates temp tokens instead of real OAuth tokens")
                    self.log("     3. Instagram callback has different state validation logic")
                    self.log("     4. Instagram callback redirect parameters are incorrect")
                    
                elif not facebook_active and not instagram_active:
                    self.log("   ⚠️ Neither Facebook nor Instagram have valid tokens")
                    self.log("   📋 Both platforms may have same underlying issue")
                    
                elif facebook_active and instagram_active:
                    self.log("   ✅ Both platforms have valid tokens")
                    self.log("   📋 Issue may be in frontend display or user workflow")
                
                # Check for collection inconsistencies
                facebook_collections = set(
                    conn.get('collection', 'Unknown') 
                    for conn in connections_detail 
                    if conn.get('platform') == 'facebook'
                )
                
                instagram_collections = set(
                    conn.get('collection', 'Unknown') 
                    for conn in connections_detail 
                    if conn.get('platform') == 'instagram'
                )
                
                if facebook_collections != instagram_collections:
                    self.log("   🚨 COLLECTION INCONSISTENCY DETECTED:")
                    self.log(f"     Facebook collections: {facebook_collections}")
                    self.log(f"     Instagram collections: {instagram_collections}")
                    self.log("     This explains why Instagram doesn't persist!")
                
                # Provide specific solution
                self.log("💡 RECOMMENDED SOLUTION:")
                
                if 'social_connections' in instagram_collections and 'social_media_connections' in facebook_collections:
                    self.log("   1. Fix Instagram callback to save to 'social_media_connections' collection")
                    self.log("   2. Ensure Instagram callback uses 'active' field instead of 'is_active'")
                    self.log("   3. Update Instagram callback redirect to use 'instagram_success=true'")
                    
                elif any('temp_' in conn.get('access_token', '') for conn in connections_detail if conn.get('platform') == 'instagram'):
                    self.log("   1. Fix Instagram OAuth token exchange to get real EAA tokens")
                    self.log("   2. Remove fallback mechanism that creates temp tokens")
                    self.log("   3. Ensure Instagram uses same token exchange logic as Facebook")
                    
                else:
                    self.log("   1. Check Instagram callback state parameter format")
                    self.log("   2. Verify Instagram callback redirect parameters")
                    self.log("   3. Ensure Instagram callback error handling matches Facebook")
                
                return True
            else:
                self.log(f"❌ Root cause analysis failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Root cause analysis error: {str(e)}", "ERROR")
            return False
    
    def run_live_diagnostic(self):
        """Run the complete Instagram LIVE diagnostic"""
        self.log("🚀 STARTING INSTAGRAM OAUTH LIVE ENVIRONMENT DIAGNOSTIC")
        self.log("=" * 80)
        self.log(f"🌐 LIVE Backend URL: {LIVE_BACKEND_URL}")
        self.log(f"👤 Test User: {TEST_EMAIL}")
        self.log("=" * 80)
        
        results = {
            'live_authentication': False,
            'live_connections_analysis': False,
            'oauth_urls_comparison': False,
            'callback_logic_testing': False,
            'token_persistence_analysis': False,
            'publication_comparison': False,
            'root_cause_analysis': False
        }
        
        # Step 1: LIVE Authentication
        if self.authenticate_live():
            results['live_authentication'] = True
            
            # Step 2: LIVE Connections Analysis
            if self.analyze_live_social_connections_state():
                results['live_connections_analysis'] = True
            
            # Step 3: OAuth URLs Comparison
            if self.compare_facebook_vs_instagram_oauth_urls():
                results['oauth_urls_comparison'] = True
            
            # Step 4: Callback Logic Testing
            if self.test_facebook_vs_instagram_callback_logic():
                results['callback_logic_testing'] = True
            
            # Step 5: Token Persistence Analysis
            if self.analyze_token_persistence_issue():
                results['token_persistence_analysis'] = True
            
            # Step 6: Publication Comparison
            if self.test_publication_endpoints_comparison():
                results['publication_comparison'] = True
            
            # Step 7: Root Cause Analysis
            if self.identify_root_cause_and_solution():
                results['root_cause_analysis'] = True
        
        # Summary
        self.log("=" * 80)
        self.log("🎯 LIVE DIAGNOSTIC SUMMARY")
        
        passed_tests = sum(results.values())
        total_tests = len(results)
        success_rate = (passed_tests / total_tests) * 100
        
        self.log(f"📊 Test Results: {passed_tests}/{total_tests} passed ({success_rate:.1f}% success rate)")
        
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            self.log(f"   {test_name.replace('_', ' ').title()}: {status}")
        
        # Critical findings summary
        self.log("\n🔍 CRITICAL FINDINGS FOR LIVE ENVIRONMENT:")
        
        if not results['live_authentication']:
            self.log("❌ LIVE AUTHENTICATION FAILED - Cannot access claire-marcus.com")
        elif passed_tests == total_tests:
            self.log("✅ All diagnostic tests passed - Check detailed logs for specific issues")
        else:
            self.log("⚠️ Some diagnostic tests failed - Root cause likely identified")
        
        self.log("\n📋 NEXT STEPS FOR LIVE ENVIRONMENT:")
        self.log("1. Review detailed diagnostic logs above")
        self.log("2. Focus on Instagram vs Facebook differences")
        self.log("3. Check callback collection consistency")
        self.log("4. Verify token exchange implementation")
        self.log("5. Test Instagram reconnection on LIVE")
        
        return results

def main():
    """Main execution function"""
    print("🎯 INSTAGRAM OAUTH LIVE ENVIRONMENT DIAGNOSTIC - claire-marcus.com")
    print("=" * 80)
    print(f"📅 Diagnostic Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 LIVE Backend URL: {LIVE_BACKEND_URL}")
    print(f"👤 Test User: {TEST_EMAIL}")
    print("🎯 Objective: Diagnostiquer pourquoi Instagram ne persiste pas sur LIVE")
    print("=" * 80)
    
    diagnostic = InstagramLiveDiagnostic()
    results = diagnostic.run_live_diagnostic()
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)  # All tests passed
    else:
        sys.exit(1)  # Some tests failed

if __name__ == "__main__":
    main()