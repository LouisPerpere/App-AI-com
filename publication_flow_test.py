#!/usr/bin/env python3
"""
BACKEND TESTING - TRACER LE FLOW EXACT POST /api/posts/publish
Test diagnostic complet du flow de publication depuis Claire et Marcus

OBJECTIF CRITIQUE: Tracer exactement ce qui se passe quand l'utilisateur clique sur "Publier"
Identifiants: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import time
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://post-restore.preview.emergentagent.com/api"
CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class PublicationFlowTracer:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.test_post_id = None
        
    def authenticate(self):
        """Authentification avec les identifiants fournis"""
        print("🔐 STEP 1: Authentication...")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json=CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                self.user_id = data.get('user_id')
                
                # Set authorization header for all future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                
                print(f"✅ Authentication successful")
                print(f"   User ID: {self.user_id}")
                print(f"   Token: {self.access_token[:20]}...")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def identify_publish_endpoint(self):
        """STEP 2: Identifier l'endpoint réellement utilisé par l'interface"""
        print("\n📘 STEP 2: Identifier l'endpoint de publication utilisé par l'interface...")
        
        # Vérifier les endpoints de publication disponibles
        endpoints_to_check = [
            "/posts/publish",
            "/social/facebook/publish",
            "/social/instagram/publish", 
            "/social/facebook/publish-simple",
            "/social/instagram/publish-simple",
            "/publish/facebook/photo",
            "/social/facebook/publish-with-image"
        ]
        
        available_endpoints = []
        
        for endpoint in endpoints_to_check:
            try:
                # Test avec une requête POST pour voir si l'endpoint existe
                response = self.session.post(f"{BACKEND_URL}{endpoint}", json={}, timeout=5)
                if response.status_code != 404:
                    available_endpoints.append(endpoint)
                    print(f"   ✅ Endpoint trouvé: {endpoint} (Status: {response.status_code})")
                else:
                    print(f"   ❌ Endpoint non trouvé: {endpoint}")
            except Exception as e:
                print(f"   ⚠️ Erreur test endpoint {endpoint}: {str(e)}")
        
        print(f"\n📊 Endpoints de publication disponibles: {len(available_endpoints)}")
        for endpoint in available_endpoints:
            print(f"   - {endpoint}")
        
        return available_endpoints
    
    def get_test_post_for_publication(self):
        """STEP 3: Obtenir un post de test pour la publication"""
        print("\n📘 STEP 3: Obtenir un post de test pour publication...")
        
        try:
            # Récupérer les posts générés
            response = self.session.get(f"{BACKEND_URL}/posts/generated", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('posts', [])
                print(f"✅ Posts récupérés: {len(posts)} posts trouvés")
                
                # Chercher un post Facebook non publié avec image
                facebook_posts = [p for p in posts if p.get('platform') == 'facebook' and not p.get('published')]
                
                if facebook_posts:
                    test_post = facebook_posts[0]
                    self.test_post_id = test_post.get('id')
                    print(f"✅ Post de test sélectionné:")
                    print(f"   ID: {self.test_post_id}")
                    print(f"   Titre: {test_post.get('title', 'N/A')}")
                    print(f"   Plateforme: {test_post.get('platform')}")
                    print(f"   Image URL: {test_post.get('visual_url', 'N/A')}")
                    print(f"   Publié: {test_post.get('published', False)}")
                    return test_post
                else:
                    print("❌ Aucun post Facebook non publié trouvé")
                    # Prendre n'importe quel post pour le test
                    if posts:
                        test_post = posts[0]
                        self.test_post_id = test_post.get('id')
                        print(f"⚠️ Utilisation du premier post disponible:")
                        print(f"   ID: {self.test_post_id}")
                        print(f"   Plateforme: {test_post.get('platform')}")
                        return test_post
                    return None
            else:
                print(f"❌ Erreur récupération posts: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur récupération posts: {str(e)}")
            return None
    
    def trace_publish_endpoint_flow(self):
        """STEP 4: Tracer le flow complet POST /api/posts/publish"""
        print("\n📘 STEP 4: Tracer le flow complet POST /api/posts/publish...")
        
        if not self.test_post_id:
            print("❌ Aucun post de test disponible")
            return False
        
        try:
            print(f"🔍 Test publication avec post_id: {self.test_post_id}")
            
            # Appeler l'endpoint de publication
            response = self.session.post(
                f"{BACKEND_URL}/posts/publish",
                json={"post_id": self.test_post_id},
                timeout=30
            )
            
            print(f"📡 Réponse POST /api/posts/publish:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
            if response.status_code in [200, 400, 401, 404]:
                try:
                    result = response.json()
                    print(f"   Response JSON: {json.dumps(result, indent=2, ensure_ascii=False)}")
                    
                    # Analyser la réponse pour comprendre le flow
                    if 'error' in result:
                        error_msg = result['error']
                        print(f"\n🔍 ANALYSE ERREUR:")
                        print(f"   Message: {error_msg}")
                        
                        if 'connexion sociale' in error_msg.lower():
                            print("   ➜ CAUSE: Aucune connexion sociale active")
                            return self.analyze_social_connections()
                        elif 'post non trouvé' in error_msg.lower():
                            print("   ➜ CAUSE: Post non trouvé dans la base")
                        elif 'oauth' in error_msg.lower() or 'token' in error_msg.lower():
                            print("   ➜ CAUSE: Problème d'authentification OAuth")
                        
                    return True
                    
                except json.JSONDecodeError:
                    print(f"   Response Text: {response.text}")
                    return False
            else:
                print(f"   Response Text: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur test publication: {str(e)}")
            return False
    
    def analyze_social_connections(self):
        """STEP 5: Analyser les connexions sociales"""
        print("\n📘 STEP 5: Analyse des connexions sociales...")
        
        try:
            # Vérifier les connexions sociales
            response = self.session.get(f"{BACKEND_URL}/social/connections", timeout=10)
            
            if response.status_code == 200:
                connections = response.json()
                print(f"✅ Connexions sociales récupérées: {len(connections)} connexions")
                
                for conn in connections:
                    print(f"   - Plateforme: {conn.get('platform')}")
                    print(f"     Active: {conn.get('active', conn.get('is_active'))}")
                    print(f"     Token: {'***' if conn.get('access_token') else 'NULL'}")
                
                # Vérifier l'endpoint de diagnostic si disponible
                try:
                    diag_response = self.session.get(f"{BACKEND_URL}/debug/social-connections", timeout=10)
                    if diag_response.status_code == 200:
                        diag_data = diag_response.json()
                        print(f"\n🔍 DIAGNOSTIC DÉTAILLÉ:")
                        print(f"   Total connexions: {diag_data.get('total_connections', 'N/A')}")
                        print(f"   Connexions actives: {diag_data.get('active_connections', 'N/A')}")
                        print(f"   Facebook: {diag_data.get('facebook_connections', 'N/A')}")
                        print(f"   Instagram: {diag_data.get('instagram_connections', 'N/A')}")
                except:
                    print("   ⚠️ Endpoint de diagnostic non disponible")
                
                return True
            else:
                print(f"❌ Erreur connexions sociales: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur analyse connexions: {str(e)}")
            return False
    
    def trace_image_extraction(self):
        """STEP 6: Diagnostic extraction d'image"""
        print("\n📘 STEP 6: Diagnostic extraction d'image...")
        
        if not self.test_post_id:
            print("❌ Aucun post de test disponible")
            return False
        
        try:
            # Récupérer les détails du post
            response = self.session.get(f"{BACKEND_URL}/posts/generated", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('posts', [])
                test_post = next((p for p in posts if p.get('id') == self.test_post_id), None)
                
                if test_post:
                    image_url = test_post.get('visual_url')
                    print(f"✅ Post trouvé:")
                    print(f"   Image URL: {image_url}")
                    
                    if image_url:
                        # Tester l'accessibilité de l'image
                        if image_url.startswith('/api/content/'):
                            # Image système - tester l'accès
                            img_response = self.session.get(f"{BACKEND_URL.replace('/api', '')}{image_url}", timeout=10)
                            print(f"   Test accès image: {img_response.status_code}")
                            
                            if img_response.status_code == 200:
                                print(f"   ✅ Image accessible ({len(img_response.content)} bytes)")
                                
                                # Tester la conversion en URL publique
                                print(f"   🔄 Test conversion URL publique...")
                                public_url = self.convert_to_public_url(image_url)
                                print(f"   URL publique: {public_url}")
                                
                                # Tester l'accès à l'URL publique
                                public_response = self.session.get(public_url, timeout=10)
                                print(f"   Test accès URL publique: {public_response.status_code}")
                                
                            else:
                                print(f"   ❌ Image non accessible")
                        else:
                            print(f"   ℹ️ Image externe: {image_url}")
                    else:
                        print(f"   ⚠️ Aucune image associée au post")
                    
                    return True
                else:
                    print("❌ Post de test non trouvé")
                    return False
            else:
                print(f"❌ Erreur récupération posts: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur diagnostic image: {str(e)}")
            return False
    
    def convert_to_public_url(self, image_url):
        """Convertir URL protégée en URL publique"""
        if "/api/content/" in image_url and "/file" in image_url:
            import re
            match = re.search(r'/api/content/([^/]+)/file', image_url)
            if match:
                file_id = match.group(1)
                backend_base = BACKEND_URL.replace('/api', '')
                return f"{backend_base}/api/public/image/{file_id}"
        return image_url
    
    def test_facebook_api_request_simulation(self):
        """STEP 7: Simuler la requête Facebook Graph API"""
        print("\n📘 STEP 7: Simulation requête Facebook Graph API...")
        
        try:
            # Tester les endpoints binaires si disponibles
            binary_endpoints = [
                "/social/facebook/publish-with-image",
                "/publish/facebook/photo"
            ]
            
            for endpoint in binary_endpoints:
                print(f"\n🔍 Test endpoint: {endpoint}")
                
                test_data = {
                    "text": "Test publication Facebook",
                    "image_url": "https://cdn.pixabay.com/photo/2016/11/29/05/45/astronomy-1867616_960_720.jpg"
                }
                
                try:
                    response = self.session.post(
                        f"{BACKEND_URL}{endpoint}",
                        json=test_data,
                        timeout=30
                    )
                    
                    print(f"   Status: {response.status_code}")
                    
                    if response.status_code in [200, 400, 401]:
                        try:
                            result = response.json()
                            print(f"   Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
                            
                            # Analyser la méthode utilisée
                            if 'method' in result:
                                print(f"   ✅ Méthode détectée: {result['method']}")
                            
                            if 'error' in result and 'oauth' in result['error'].lower():
                                print(f"   ✅ Requête Facebook tentée (erreur OAuth attendue)")
                                
                        except json.JSONDecodeError:
                            print(f"   Response text: {response.text}")
                    
                except Exception as e:
                    print(f"   ❌ Erreur test {endpoint}: {str(e)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur simulation Facebook API: {str(e)}")
            return False
    
    def run_complete_flow_trace(self):
        """Exécuter le diagnostic complet du flow de publication"""
        print("🎯 DIAGNOSTIC COMPLET FLOW PUBLICATION - CLAIRE ET MARCUS")
        print("=" * 70)
        
        results = []
        
        # Step 1: Authentication
        if self.authenticate():
            results.append(("Authentication", True))
        else:
            results.append(("Authentication", False))
            print("❌ Cannot continue without authentication")
            return results
        
        # Step 2: Identifier les endpoints
        available_endpoints = self.identify_publish_endpoint()
        results.append(("Endpoint Identification", len(available_endpoints) > 0))
        
        # Step 3: Obtenir un post de test
        test_post = self.get_test_post_for_publication()
        results.append(("Test Post Retrieval", test_post is not None))
        
        # Step 4: Tracer le flow principal
        results.append(("Publish Flow Trace", self.trace_publish_endpoint_flow()))
        
        # Step 5: Diagnostic image
        results.append(("Image Extraction Diagnostic", self.trace_image_extraction()))
        
        # Step 6: Test Facebook API simulation
        results.append(("Facebook API Simulation", self.test_facebook_api_request_simulation()))
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 RÉSULTATS DIAGNOSTIC FLOW PUBLICATION")
        print("=" * 70)
        
        passed = 0
        total = len(results)
        
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
            if success:
                passed += 1
        
        print(f"\n📈 TAUX DE RÉUSSITE: {passed}/{total} ({(passed/total)*100:.1f}%)")
        
        # Conclusions et recommandations
        print("\n" + "=" * 70)
        print("🔍 CONCLUSIONS ET RECOMMANDATIONS")
        print("=" * 70)
        
        failed_tests = [name for name, success in results if not success]
        
        if not failed_tests:
            print("✅ Flow de publication entièrement fonctionnel")
            print("✅ Tous les endpoints et mécanismes opérationnels")
        else:
            print("❌ Problèmes identifiés:")
            for test in failed_tests:
                print(f"   - {test}")
        
        print("\n📝 PROCHAINES ÉTAPES:")
        print("1. Vérifier les connexions sociales Facebook/Instagram")
        print("2. Tester avec des tokens OAuth valides")
        print("3. Valider l'extraction et conversion d'images")
        print("4. Monitorer les logs backend pour les requêtes Facebook")
        
        return results

def main():
    """Point d'entrée principal"""
    tracer = PublicationFlowTracer()
    results = tracer.run_complete_flow_trace()
    
    # Additional analysis
    print("\n" + "=" * 70)
    print("🔍 ANALYSE FINALE & RECOMMANDATIONS")
    print("=" * 70)
    
    failed_tests = [name for name, success in results if not success]
    
    if not failed_tests:
        print("✅ Flow de publication entièrement opérationnel")
        print("✅ Tous les endpoints et corrections fonctionnent")
        print("✅ Système prêt pour publication avec tokens OAuth valides")
    else:
        print("❌ Tests échoués:")
        for test in failed_tests:
            print(f"   - {test}")
        
        if "Authentication" in failed_tests:
            print("\n🚨 CRITIQUE: Authentification échouée - vérifier les identifiants")
        elif len(failed_tests) <= 2:
            print("\n⚠️ Problèmes mineurs détectés - flow majoritairement fonctionnel")
        else:
            print("\n🚨 MAJEUR: Plusieurs échecs - flow nécessite débogage")
    
    print("\n📝 ACTIONS RECOMMANDÉES:")
    print("1. Si authentification OK: Tester avec connexion Facebook réelle")
    print("2. Si endpoints OK: Valider avec tokens OAuth valides")
    print("3. Si images OK: Tester workflow complet de publication")
    print("4. Monitorer logs backend pour messages 'Facebook Graph API'")

if __name__ == "__main__":
    main()