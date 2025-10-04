#!/usr/bin/env python3
"""
Investigation approfondie des carousels existants et test de l'endpoint spécifique trouvé
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://claire-marcus-app-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
EMAIL = "lperpere@yahoo.fr"
PASSWORD = "L@Reunion974!"

class CarouselInvestigator:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        
    def authenticate(self):
        """Authentification"""
        print("🔐 Authentification...")
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login-robust", json={
                "email": EMAIL,
                "password": PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                print(f"✅ Authentification réussie - User ID: {self.user_id}")
                return True
            else:
                print(f"❌ Échec authentification: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur authentification: {str(e)}")
            return False
    
    def test_specific_carousel(self):
        """Tester le carousel spécifique trouvé dans les posts existants"""
        carousel_id = "carousel_90e5d8c2-ff60-4c17-b416-da6573edb492"
        print(f"\n🎠 Test du carousel spécifique: {carousel_id}")
        
        try:
            response = self.session.get(f"{API_BASE}/content/carousel/{carousel_id}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Carousel accessible!")
                print(f"   Type: {data.get('type', 'N/A')}")
                print(f"   ID: {data.get('id', 'N/A')}")
                print(f"   Post ID: {data.get('post_id', 'N/A')}")
                print(f"   Créé le: {data.get('created_at', 'N/A')}")
                
                images = data.get('images', [])
                print(f"   Images: {len(images)} éléments")
                
                for i, img in enumerate(images, 1):
                    print(f"      {i}. ID: {img.get('id', 'N/A')}")
                    print(f"         URL: {img.get('url', 'N/A')}")
                
                return data
            else:
                print(f"❌ Carousel non accessible: {response.status_code}")
                print(f"   Réponse: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur test carousel: {str(e)}")
            return None
    
    def get_all_posts(self):
        """Récupérer tous les posts pour analyser les carousels"""
        print(f"\n📝 Récupération de tous les posts...")
        
        try:
            response = self.session.get(f"{API_BASE}/posts/generated")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('posts', [])
                
                print(f"✅ Posts récupérés: {len(posts)}")
                
                # Analyser les posts avec carousels
                carousel_posts = []
                for post in posts:
                    visual_url = post.get('visual_url', '')
                    if 'carousel' in visual_url.lower():
                        carousel_posts.append(post)
                
                print(f"   Posts avec carousels: {len(carousel_posts)}")
                
                if carousel_posts:
                    print(f"\n   📋 DÉTAILS DES POSTS AVEC CAROUSELS:")
                    for i, post in enumerate(carousel_posts, 1):
                        print(f"      {i}. Post ID: {post.get('id', 'N/A')}")
                        print(f"         Titre: {post.get('title', 'Sans titre')}")
                        print(f"         Plateforme: {post.get('platform', 'N/A')}")
                        print(f"         Visual URL: {post.get('visual_url', 'N/A')}")
                        print(f"         Mois cible: {post.get('target_month', 'N/A')}")
                        print(f"         Statut: {post.get('status', 'N/A')}")
                        print(f"         Validé: {post.get('validated', 'N/A')}")
                        print(f"         Créé le: {post.get('created_at', 'N/A')}")
                        
                        # Extraire l'ID du carousel de l'URL
                        visual_url = post.get('visual_url', '')
                        if '/carousel/' in visual_url:
                            carousel_id = visual_url.split('/carousel/')[-1]
                            print(f"         Carousel ID extrait: {carousel_id}")
                        print()
                
                return carousel_posts
            else:
                print(f"❌ Échec récupération posts: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Erreur récupération posts: {str(e)}")
            return []
    
    def check_social_connections(self):
        """Vérifier les connexions sociales pour comprendre l'erreur de génération"""
        print(f"\n🔗 Vérification des connexions sociales...")
        
        try:
            response = self.session.get(f"{API_BASE}/social/connections")
            
            if response.status_code == 200:
                data = response.json()
                connections = data if isinstance(data, list) else data.get('connections', [])
                
                print(f"✅ Connexions sociales: {len(connections)}")
                
                if connections:
                    for conn in connections:
                        print(f"   - Plateforme: {conn.get('platform', 'N/A')}")
                        print(f"     Actif: {conn.get('active', 'N/A')}")
                        print(f"     Nom: {conn.get('page_name', 'N/A')}")
                else:
                    print("   ⚠️ Aucune connexion sociale active trouvée")
                    print("   Ceci explique l'erreur 'Aucun réseau social connecté'")
                
                return connections
            else:
                print(f"❌ Échec vérification connexions: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Erreur vérification connexions: {str(e)}")
            return []
    
    def test_content_with_month_filter(self):
        """Tester le contenu avec différents filtres de mois"""
        print(f"\n📅 Test du contenu avec filtres de mois...")
        
        months_to_test = ["septembre", "september", "septembre_2025", "09", "2025-09"]
        
        for month in months_to_test:
            print(f"\n   🔍 Test avec filtre: '{month}'")
            
            try:
                # Tester différents paramètres de requête
                params = {"month": month, "limit": 50}
                response = self.session.get(f"{API_BASE}/content/pending", params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    content = data.get('content', [])
                    
                    september_items = []
                    for item in content:
                        attributed_month = item.get('attributed_month', '').lower()
                        if month.lower() in attributed_month or 'septembre' in attributed_month or 'september' in attributed_month:
                            september_items.append(item)
                    
                    print(f"      Total items: {len(content)}")
                    print(f"      Items septembre: {len(september_items)}")
                    
                    if september_items:
                        print(f"      Exemples:")
                        for item in september_items[:2]:
                            print(f"         - {item.get('filename', 'N/A')} (mois: {item.get('attributed_month', 'N/A')})")
                
            except Exception as e:
                print(f"      ❌ Erreur: {str(e)}")
    
    def run_investigation(self):
        """Exécuter l'investigation complète"""
        print("🔍 INVESTIGATION APPROFONDIE DES CAROUSELS")
        print("=" * 60)
        
        if not self.authenticate():
            return False
        
        # Test du carousel spécifique trouvé
        carousel_data = self.test_specific_carousel()
        
        # Récupération de tous les posts avec carousels
        carousel_posts = self.get_all_posts()
        
        # Vérification des connexions sociales
        connections = self.check_social_connections()
        
        # Test du contenu avec filtres de mois
        self.test_content_with_month_filter()
        
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DE L'INVESTIGATION")
        print("=" * 60)
        
        print(f"✅ Carousel spécifique accessible: {'Oui' if carousel_data else 'Non'}")
        print(f"✅ Posts avec carousels trouvés: {len(carousel_posts)}")
        print(f"✅ Connexions sociales actives: {len(connections)}")
        
        if carousel_data:
            print(f"✅ Images dans le carousel testé: {len(carousel_data.get('images', []))}")
        
        print("\n💡 CONCLUSIONS:")
        if carousel_data:
            print("   - Le système de carousels fonctionne (carousel accessible)")
            print("   - Des posts avec carousels existent déjà")
        
        if not connections:
            print("   - Aucune connexion sociale active (explique l'erreur de génération)")
            print("   - Il faut connecter Facebook pour générer de nouveaux posts")
        
        if len(carousel_posts) > 0:
            print("   - Des carousels sont déjà présents dans les posts existants")
            print("   - Le système peut gérer les carousels Facebook")
        
        return True

def main():
    investigator = CarouselInvestigator()
    investigator.run_investigation()

if __name__ == "__main__":
    main()