#!/usr/bin/env python3
"""
🎯 VÉRIFICATION CONVERSION JPG EN TEMPS RÉÉL - PUBLICATION RÉELLE
Test complet de la conversion JPG lors de la publication Facebook

Identifiants: lperpere@yahoo.fr / L@Reunion974!
Objectif: Vérifier si la conversion JPG fonctionne vraiment lors du clic sur "Publier"
"""

import requests
import json
import time
import sys
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://post-restore.preview.emergentagent.com/api"
EMAIL = "lperpere@yahoo.fr"
PASSWORD = "L@Reunion974!"

class FacebookJPGConversionTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        
    def authenticate(self):
        """Étape 1: Authentification"""
        print("🔐 ÉTAPE 1: Authentification...")
        
        auth_data = {
            "email": EMAIL,
            "password": PASSWORD
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login-robust", json=auth_data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Configurer les headers pour toutes les requêtes suivantes
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                })
                
                print(f"✅ Authentification réussie")
                print(f"   User ID: {self.user_id}")
                print(f"   Token: {self.token[:30]}...")
                return True
            else:
                print(f"❌ Échec authentification: {response.status_code}")
                print(f"   Réponse: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur authentification: {e}")
            return False
    
    def check_social_connections(self):
        """Étape 2: Vérifier l'état des tokens Facebook actuels"""
        print("\n🔍 ÉTAPE 2: Vérification des connexions sociales...")
        
        try:
            # Vérifier les connexions via l'endpoint de debug
            response = self.session.get(f"{BACKEND_URL}/debug/social-connections", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Diagnostic des connexions sociales:")
                print(f"   Total connexions: {data.get('total_connections', 0)}")
                print(f"   Connexions actives: {data.get('active_connections', 0)}")
                print(f"   Facebook: {data.get('facebook_connections', 0)}")
                print(f"   Instagram: {data.get('instagram_connections', 0)}")
                
                # Analyser les tokens
                connections = data.get('connections_details', [])
                facebook_tokens = []
                
                for conn in connections:
                    if conn.get('platform') == 'facebook' and conn.get('active'):
                        token = conn.get('access_token', 'N/A')
                        if token.startswith('EAA'):
                            print(f"   ✅ Token Facebook EAA trouvé: {token[:20]}...")
                            facebook_tokens.append(token)
                        elif 'temp_facebook_token' in token:
                            print(f"   ⚠️ Token temporaire détecté: {token}")
                        else:
                            print(f"   ❓ Token Facebook: {token[:20]}...")
                
                if facebook_tokens:
                    print(f"✅ {len(facebook_tokens)} token(s) Facebook EAA valide(s) trouvé(s)")
                    return True
                else:
                    print("❌ Aucun token Facebook EAA valide trouvé")
                    return False
                    
            else:
                print(f"❌ Erreur diagnostic connexions: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur vérification connexions: {e}")
            return False
    
    def find_post_with_image(self):
        """Étape 3: Trouver un post avec image pour tester la publication"""
        print("\n🖼️ ÉTAPE 3: Recherche d'un post avec image...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/posts/generated", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('posts', [])
                
                print(f"📊 {len(posts)} posts trouvés")
                
                # Chercher un post Facebook avec image
                facebook_posts_with_images = []
                
                for post in posts:
                    if (post.get('platform') == 'facebook' and 
                        post.get('visual_url') and 
                        not post.get('published', False)):
                        
                        facebook_posts_with_images.append(post)
                        print(f"   ✅ Post Facebook avec image trouvé:")
                        print(f"      ID: {post.get('id')}")
                        print(f"      Titre: {post.get('title', 'N/A')}")
                        print(f"      Image: {post.get('visual_url')}")
                        print(f"      Publié: {post.get('published', False)}")
                
                if facebook_posts_with_images:
                    # Retourner le premier post trouvé
                    selected_post = facebook_posts_with_images[0]
                    print(f"🎯 Post sélectionné pour test: {selected_post.get('id')}")
                    return selected_post
                else:
                    print("❌ Aucun post Facebook avec image non publié trouvé")
                    return None
                    
            else:
                print(f"❌ Erreur récupération posts: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur recherche posts: {e}")
            return None
    
    def test_jpg_conversion_publication(self, post):
        """Étape 4: Test publication réelle avec logs détaillés de conversion JPG"""
        print("\n🚀 ÉTAPE 4: Test publication avec conversion JPG...")
        
        post_id = post.get('id')
        image_url = post.get('visual_url')
        
        print(f"📝 Publication du post: {post_id}")
        print(f"🖼️ Image URL: {image_url}")
        
        try:
            # Effectuer la publication
            pub_data = {"post_id": post_id}
            
            print("⏳ Envoi de la requête de publication...")
            print("🔍 Recherche des logs de conversion JPG...")
            
            response = self.session.post(f"{BACKEND_URL}/posts/publish", json=pub_data, timeout=60)
            
            print(f"📤 Statut de réponse: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Réponse de publication reçue:")
                print(f"   Message: {data.get('message', 'N/A')}")
                print(f"   Succès: {data.get('success', False)}")
                
                # Analyser la réponse pour les indices de conversion JPG
                response_text = response.text.lower()
                
                # Rechercher des indices de conversion JPG
                jpg_indicators = [
                    "jpg", "jpeg", "conversion", "convert", "image", 
                    "facebook jpg upload", "downloading and converting",
                    "conversion jpg réussie", "envoi à facebook"
                ]
                
                found_indicators = []
                for indicator in jpg_indicators:
                    if indicator in response_text:
                        found_indicators.append(indicator)
                
                if found_indicators:
                    print(f"🔍 Indices de traitement d'image trouvés: {found_indicators}")
                else:
                    print("⚠️ Aucun indice de conversion JPG dans la réponse")
                
                return True
                
            else:
                print(f"❌ Échec publication: {response.status_code}")
                print(f"   Réponse: {response.text}")
                
                # Même en cas d'échec, analyser la réponse pour les logs
                if "facebook" in response.text.lower():
                    print("🔍 Réponse contient des références Facebook")
                if "image" in response.text.lower():
                    print("🔍 Réponse contient des références d'image")
                
                return False
                
        except Exception as e:
            print(f"❌ Erreur publication: {e}")
            return False
    
    def analyze_backend_logs(self):
        """Étape 5: Analyser les logs backend pour la conversion JPG"""
        print("\n📋 ÉTAPE 5: Analyse des logs backend...")
        
        # Note: Dans un environnement de production, nous ne pouvons pas accéder directement aux logs
        # Mais nous pouvons essayer de déclencher des endpoints qui pourraient révéler des informations
        
        try:
            # Essayer d'accéder à un endpoint de diagnostic si disponible
            response = self.session.get(f"{BACKEND_URL}/health", timeout=30)
            
            if response.status_code == 200:
                print("✅ Backend accessible pour diagnostic")
                
                # Essayer d'autres endpoints de diagnostic
                diagnostic_endpoints = [
                    "/diag",
                    "/debug/status",
                    "/debug/logs"
                ]
                
                for endpoint in diagnostic_endpoints:
                    try:
                        diag_response = self.session.get(f"{BACKEND_URL}{endpoint}", timeout=10)
                        if diag_response.status_code == 200:
                            print(f"✅ Endpoint diagnostic accessible: {endpoint}")
                        else:
                            print(f"⚠️ Endpoint {endpoint}: {diag_response.status_code}")
                    except:
                        print(f"❌ Endpoint {endpoint} non accessible")
                
            else:
                print("❌ Backend non accessible pour diagnostic")
                
        except Exception as e:
            print(f"❌ Erreur analyse logs: {e}")
    
    def test_image_accessibility(self, image_url):
        """Étape 6: Tester l'accessibilité de l'image pour Facebook"""
        print(f"\n🌐 ÉTAPE 6: Test d'accessibilité de l'image...")
        print(f"🔗 URL testée: {image_url}")
        
        try:
            # Test d'accès direct à l'image
            img_response = requests.get(image_url, timeout=30, allow_redirects=True)
            
            print(f"📊 Statut d'accès: {img_response.status_code}")
            print(f"📏 Taille: {len(img_response.content)} bytes")
            print(f"🏷️ Content-Type: {img_response.headers.get('content-type', 'N/A')}")
            
            # Vérifier si c'est une image JPG
            content_type = img_response.headers.get('content-type', '').lower()
            if 'jpeg' in content_type or 'jpg' in content_type:
                print("✅ Image déjà en format JPG")
            elif 'png' in content_type:
                print("🔄 Image PNG - conversion JPG nécessaire")
            elif 'webp' in content_type:
                print("🔄 Image WebP - conversion JPG nécessaire")
            else:
                print(f"❓ Format d'image: {content_type}")
            
            # Test avec User-Agent Facebook
            fb_headers = {
                'User-Agent': 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)'
            }
            
            fb_response = requests.get(image_url, headers=fb_headers, timeout=30, allow_redirects=True)
            print(f"🤖 Accès Facebook Bot: {fb_response.status_code}")
            
            if img_response.status_code == 200:
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Erreur test accessibilité: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Exécuter le test complet de conversion JPG"""
        print("🎯 DÉMARRAGE DU TEST DE CONVERSION JPG FACEBOOK")
        print("=" * 60)
        
        # Étape 1: Authentification
        if not self.authenticate():
            print("❌ ÉCHEC: Impossible de s'authentifier")
            return False
        
        # Étape 2: Vérifier les connexions sociales
        has_valid_tokens = self.check_social_connections()
        if not has_valid_tokens:
            print("⚠️ ATTENTION: Aucun token Facebook EAA valide")
            print("   La publication échouera probablement")
        
        # Étape 3: Trouver un post avec image
        test_post = self.find_post_with_image()
        if not test_post:
            print("❌ ÉCHEC: Aucun post avec image trouvé pour le test")
            return False
        
        # Étape 6: Tester l'accessibilité de l'image
        image_url = test_post.get('visual_url')
        if image_url:
            self.test_image_accessibility(image_url)
        
        # Étape 4: Test de publication avec conversion JPG
        publication_success = self.test_jpg_conversion_publication(test_post)
        
        # Étape 5: Analyser les logs
        self.analyze_backend_logs()
        
        # Résumé final
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DU TEST DE CONVERSION JPG")
        print("=" * 60)
        
        print(f"✅ Authentification: Réussie")
        print(f"{'✅' if has_valid_tokens else '❌'} Tokens Facebook: {'Valides' if has_valid_tokens else 'Invalides/Temporaires'}")
        print(f"✅ Post avec image: Trouvé ({test_post.get('id')})")
        print(f"{'✅' if publication_success else '❌'} Publication: {'Réussie' if publication_success else 'Échouée'}")
        
        # Question centrale
        print("\n🎯 QUESTION CENTRALE:")
        print("Est-ce que les logs montrent 'Conversion JPG réussie' et 'Envoi à Facebook: X bytes JPG' ?")
        
        if publication_success and has_valid_tokens:
            print("✅ RÉPONSE: Le système de publication fonctionne")
            print("   Vérifiez les logs backend pour les messages de conversion JPG")
        elif publication_success and not has_valid_tokens:
            print("⚠️ RÉPONSE: Publication traitée mais tokens invalides")
            print("   La conversion JPG peut fonctionner mais l'envoi Facebook échoue")
        else:
            print("❌ RÉPONSE: Le système de publication ne fonctionne pas correctement")
        
        return publication_success

def main():
    """Point d'entrée principal"""
    tester = FacebookJPGConversionTester()
    
    try:
        success = tester.run_comprehensive_test()
        
        if success:
            print("\n🎉 TEST TERMINÉ AVEC SUCCÈS")
            sys.exit(0)
        else:
            print("\n❌ TEST TERMINÉ AVEC DES PROBLÈMES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Test interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 ERREUR CRITIQUE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()