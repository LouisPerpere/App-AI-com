#!/usr/bin/env python3
"""
🎯 DIAGNOSTIC GÉNÉRATION POSTS INCORRECTE
Test spécifique pour diagnostiquer pourquoi tous les posts générés pour septembre 
ont le label "Instagram" au lieu de "Facebook" alors que Facebook est connecté 
et Instagram déconnecté.

Identifiants: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import sys
import time
from datetime import datetime

class PostGenerationDiagnostic:
    def __init__(self):
        # Use the frontend environment URL from .env
        self.base_url = "https://post-restore.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.credentials = {
            "email": "lperpere@yahoo.fr",
            "password": "L@Reunion974!"
        }
        
    def authenticate(self):
        """Authenticate with the API"""
        try:
            print(f"🔐 Step 1: Authenticating with {self.credentials['email']}")
            
            response = self.session.post(
                f"{self.base_url}/auth/login-robust",
                json=self.credentials,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for all future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                })
                
                print(f"   ✅ Authentication successful")
                print(f"   User ID: {self.user_id}")
                return True
            else:
                print(f"   ❌ Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {str(e)}")
            return False
    
    def check_social_connections_state(self):
        """Vérifier l'état actuel des connexions sociales"""
        try:
            print(f"\n🔍 Step 2: Vérification état des connexions sociales")
            print(f"   Endpoint: GET /api/debug/social-connections")
            
            response = self.session.get(f"{self.base_url}/debug/social-connections")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"   ✅ Diagnostic endpoint accessible")
                
                # Analyser les connexions
                connections = data.get("social_media_connections", [])
                old_connections = data.get("social_connections_old", [])
                
                print(f"   📊 ÉTAT DES CONNEXIONS:")
                print(f"     Collection social_media_connections: {len(connections)} connexions")
                print(f"     Collection social_connections_old: {len(old_connections)} connexions")
                
                # Analyser les connexions actives
                facebook_active = [c for c in connections if c.get("platform") == "facebook" and c.get("active") == True]
                instagram_active = [c for c in connections if c.get("platform") == "instagram" and c.get("active") == True]
                facebook_inactive = [c for c in connections if c.get("platform") == "facebook" and c.get("active") == False]
                instagram_inactive = [c for c in connections if c.get("platform") == "instagram" and c.get("active") == False]
                
                print(f"     Facebook ACTIF: {len(facebook_active)}")
                print(f"     Instagram ACTIF: {len(instagram_active)}")
                print(f"     Facebook INACTIF: {len(facebook_inactive)}")
                print(f"     Instagram INACTIF: {len(instagram_inactive)}")
                
                # Analyser les anciennes connexions
                if old_connections:
                    old_facebook = [c for c in old_connections if c.get("platform") == "facebook"]
                    old_instagram = [c for c in old_connections if c.get("platform") == "instagram"]
                    print(f"     Anciennes connexions Facebook: {len(old_facebook)}")
                    print(f"     Anciennes connexions Instagram: {len(old_instagram)}")
                
                # Détails des connexions actives
                if facebook_active:
                    print(f"   📋 DÉTAILS FACEBOOK ACTIF:")
                    for i, conn in enumerate(facebook_active):
                        page_name = conn.get("page_name", "Unknown")
                        created_at = conn.get("created_at", "Unknown")
                        print(f"     {i+1}. Page: {page_name}, Créé: {created_at}")
                
                if instagram_active:
                    print(f"   📋 DÉTAILS INSTAGRAM ACTIF:")
                    for i, conn in enumerate(instagram_active):
                        page_name = conn.get("page_name", "Unknown")
                        created_at = conn.get("created_at", "Unknown")
                        print(f"     {i+1}. Page: {page_name}, Créé: {created_at}")
                
                return {
                    "facebook_active": len(facebook_active),
                    "instagram_active": len(instagram_active),
                    "facebook_inactive": len(facebook_inactive),
                    "instagram_inactive": len(instagram_inactive),
                    "connections_data": connections
                }
            else:
                print(f"   ❌ Failed to access diagnostic endpoint: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error checking social connections: {str(e)}")
            return None
    
    def analyze_september_posts(self):
        """Analyser les posts générés pour septembre"""
        try:
            print(f"\n📝 Step 3: Analyse des posts générés pour septembre")
            print(f"   Endpoint: GET /api/posts/generated")
            
            response = self.session.get(f"{self.base_url}/posts/generated")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                
                print(f"   ✅ Retrieved {len(posts)} total posts")
                
                # Filtrer les posts de septembre 2025
                september_posts = []
                for post in posts:
                    scheduled_date = post.get("scheduled_date", "")
                    if "2025-09" in scheduled_date or "septembre" in post.get("target_month", "").lower():
                        september_posts.append(post)
                
                print(f"   📊 POSTS DE SEPTEMBRE: {len(september_posts)} posts trouvés")
                
                if september_posts:
                    # Analyser la distribution des plateformes
                    facebook_posts = [p for p in september_posts if p.get("platform") == "facebook"]
                    instagram_posts = [p for p in september_posts if p.get("platform") == "instagram"]
                    
                    print(f"   📊 DISTRIBUTION PLATEFORMES SEPTEMBRE:")
                    print(f"     Posts Facebook: {len(facebook_posts)}")
                    print(f"     Posts Instagram: {len(instagram_posts)}")
                    
                    # Afficher les détails des posts
                    print(f"   📋 DÉTAILS POSTS SEPTEMBRE:")
                    for i, post in enumerate(september_posts[:10]):  # Limiter à 10 pour lisibilité
                        title = post.get("title", "Sans titre")[:50]
                        platform = post.get("platform", "Unknown")
                        date = post.get("scheduled_date", "No date")
                        status = post.get("status", "Unknown")
                        print(f"     {i+1}. [{platform.upper()}] {title}... | {date} | {status}")
                    
                    if len(september_posts) > 10:
                        print(f"     ... et {len(september_posts) - 10} autres posts")
                    
                    return {
                        "total_september": len(september_posts),
                        "facebook_september": len(facebook_posts),
                        "instagram_september": len(instagram_posts),
                        "september_posts": september_posts
                    }
                else:
                    print(f"   ⚠️ Aucun post de septembre trouvé")
                    return {
                        "total_september": 0,
                        "facebook_september": 0,
                        "instagram_september": 0,
                        "september_posts": []
                    }
            else:
                print(f"   ❌ Failed to get generated posts: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error analyzing September posts: {str(e)}")
            return None
    
    def find_post_generation_endpoint(self):
        """Identifier l'endpoint de génération de posts"""
        try:
            print(f"\n🔍 Step 4: Identification de l'endpoint de génération")
            
            # Tester plusieurs endpoints possibles
            possible_endpoints = [
                "/posts/generate",
                "/posts/generate-monthly",
                "/posts/create-batch",
                "/content/generate-posts"
            ]
            
            for endpoint in possible_endpoints:
                try:
                    print(f"   Testing: {endpoint}")
                    response = self.session.get(f"{self.base_url}{endpoint}")
                    print(f"     Status: {response.status_code}")
                    
                    if response.status_code in [200, 405, 422]:  # 405 = Method not allowed, 422 = Validation error
                        print(f"     ✅ Endpoint exists: {endpoint}")
                        
                        # Tester avec POST si GET ne fonctionne pas
                        if response.status_code == 405:
                            post_response = self.session.post(f"{self.base_url}{endpoint}", json={})
                            print(f"     POST Status: {post_response.status_code}")
                            if post_response.status_code in [200, 422, 400]:
                                print(f"     ✅ POST method available")
                                return endpoint
                        else:
                            return endpoint
                    else:
                        print(f"     ❌ Endpoint not found")
                        
                except Exception as e:
                    print(f"     ❌ Error testing {endpoint}: {str(e)}")
            
            print(f"   ⚠️ No generation endpoint found in common locations")
            return None
            
        except Exception as e:
            print(f"   ❌ Error finding generation endpoint: {str(e)}")
            return None
    
    def test_generation_logic(self, connections_state):
        """Tester la logique de génération avec l'état actuel des connexions"""
        try:
            print(f"\n🧪 Step 5: Test de la logique de génération")
            
            # Simuler une génération de test si possible
            generation_endpoint = self.find_post_generation_endpoint()
            
            if generation_endpoint:
                print(f"   Endpoint trouvé: {generation_endpoint}")
                print(f"   ⚠️ Test de génération non effectué pour éviter de créer de nouveaux posts")
                print(f"   📊 Analyse basée sur l'état des connexions:")
                
                if connections_state:
                    facebook_active = connections_state.get("facebook_active", 0)
                    instagram_active = connections_state.get("instagram_active", 0)
                    
                    print(f"     Facebook actif: {facebook_active}")
                    print(f"     Instagram actif: {instagram_active}")
                    
                    if facebook_active > 0 and instagram_active == 0:
                        print(f"   ✅ ATTENDU: Génération devrait créer des posts Facebook uniquement")
                    elif facebook_active == 0 and instagram_active > 0:
                        print(f"   ✅ ATTENDU: Génération devrait créer des posts Instagram uniquement")
                    elif facebook_active > 0 and instagram_active > 0:
                        print(f"   ✅ ATTENDU: Génération devrait créer des posts pour les deux plateformes")
                    else:
                        print(f"   ⚠️ ATTENDU: Aucune génération possible (pas de connexions actives)")
            else:
                print(f"   ❌ Impossible de tester la génération - endpoint non trouvé")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error testing generation logic: {str(e)}")
            return False
    
    def run_post_generation_diagnostic(self):
        """Exécuter le diagnostic complet de génération de posts"""
        print("🎯 MISSION: Diagnostic génération posts incorrecte")
        print("🌐 ENVIRONMENT: Preview (social-ai-planner-2.preview.emergentagent.com)")
        print("🔍 OBJECTIF: Identifier pourquoi les posts septembre sont étiquetés Instagram au lieu de Facebook")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ CRITICAL: Authentication failed - cannot proceed")
            return False
        
        # Step 2: Vérifier l'état des connexions sociales
        connections_state = self.check_social_connections_state()
        if connections_state is None:
            print("\n❌ CRITICAL: Cannot check social connections state")
            return False
        
        # Step 3: Analyser les posts de septembre
        september_analysis = self.analyze_september_posts()
        if september_analysis is None:
            print("\n❌ CRITICAL: Cannot analyze September posts")
            return False
        
        # Step 4: Tester la logique de génération
        generation_test = self.test_generation_logic(connections_state)
        
        print("\n" + "=" * 80)
        print("🎉 DIAGNOSTIC GÉNÉRATION POSTS COMPLETED")
        print("=" * 80)
        
        # Analyse des résultats
        print(f"\n📊 RÉSULTATS DU DIAGNOSTIC:")
        
        print(f"\n🔗 ÉTAT DES CONNEXIONS:")
        print(f"   Facebook actif: {connections_state.get('facebook_active', 0)}")
        print(f"   Instagram actif: {connections_state.get('instagram_active', 0)}")
        print(f"   Facebook inactif: {connections_state.get('facebook_inactive', 0)}")
        print(f"   Instagram inactif: {connections_state.get('instagram_inactive', 0)}")
        
        print(f"\n📝 POSTS DE SEPTEMBRE:")
        print(f"   Total posts septembre: {september_analysis.get('total_september', 0)}")
        print(f"   Posts Facebook: {september_analysis.get('facebook_september', 0)}")
        print(f"   Posts Instagram: {september_analysis.get('instagram_september', 0)}")
        
        # Diagnostic de l'incohérence
        print(f"\n🔍 DIAGNOSTIC DE L'INCOHÉRENCE:")
        
        facebook_active = connections_state.get('facebook_active', 0)
        instagram_active = connections_state.get('instagram_active', 0)
        facebook_posts = september_analysis.get('facebook_september', 0)
        instagram_posts = september_analysis.get('instagram_september', 0)
        
        if facebook_active > 0 and instagram_active == 0:
            if instagram_posts > 0 and facebook_posts == 0:
                print(f"   ❌ PROBLÈME IDENTIFIÉ: Facebook connecté mais posts générés pour Instagram")
                print(f"   🔍 CAUSE POSSIBLE: Logique de génération ne lit pas correctement les connexions actives")
                print(f"   🔍 CAUSE POSSIBLE: Posts générés avant connexion Facebook / après déconnexion Instagram")
            elif facebook_posts > 0 and instagram_posts == 0:
                print(f"   ✅ COHÉRENT: Facebook connecté et posts Facebook générés")
            else:
                print(f"   ⚠️ SITUATION MIXTE: Vérifier les dates de génération vs connexions")
        elif facebook_active == 0 and instagram_active > 0:
            if facebook_posts > 0 and instagram_posts == 0:
                print(f"   ❌ PROBLÈME IDENTIFIÉ: Instagram connecté mais posts générés pour Facebook")
            elif instagram_posts > 0 and facebook_posts == 0:
                print(f"   ✅ COHÉRENT: Instagram connecté et posts Instagram générés")
        elif facebook_active == 0 and instagram_active == 0:
            if facebook_posts > 0 or instagram_posts > 0:
                print(f"   ⚠️ POSTS EXISTANTS: Posts générés quand connexions étaient actives")
                print(f"   ✅ NORMAL: Posts persistent après déconnexion")
            else:
                print(f"   ✅ COHÉRENT: Pas de connexions, pas de posts")
        else:
            print(f"   ✅ CONNEXIONS MULTIPLES: Facebook et Instagram connectés")
        
        print(f"\n🚀 RECOMMANDATIONS:")
        
        if facebook_active > 0 and instagram_active == 0 and instagram_posts > 0:
            print(f"   1. ❗ URGENT: Vérifier la logique de génération de posts")
            print(f"   2. ❗ URGENT: S'assurer que la génération lit social_media_connections avec active=True")
            print(f"   3. ❗ URGENT: Vérifier que Facebook est bien marqué comme actif dans la base")
            print(f"   4. 🔧 SOLUTION: Corriger l'endpoint de génération pour utiliser les bonnes connexions")
        elif facebook_active == 0:
            print(f"   1. 🔗 Reconnecter Facebook pour activer la génération Facebook")
            print(f"   2. 📝 Les posts Instagram existants sont normaux si générés quand Instagram était actif")
        else:
            print(f"   1. ✅ État des connexions semble cohérent avec les posts")
            print(f"   2. 🔍 Vérifier les dates de génération pour confirmer la chronologie")
        
        print("=" * 80)
        
        return True

def main():
    """Main execution function"""
    diagnostic = PostGenerationDiagnostic()
    
    try:
        success = diagnostic.run_post_generation_diagnostic()
        if success:
            print(f"\n🎯 CONCLUSION: Diagnostic génération posts COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print(f"\n💥 CONCLUSION: Diagnostic génération posts FAILED")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⚠️ Diagnostic interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during diagnostic: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()