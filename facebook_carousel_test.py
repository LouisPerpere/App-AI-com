#!/usr/bin/env python3
"""
Test de génération de posts Facebook avec carousels présents en bibliothèque (septembre)

CONTEXTE:
L'utilisateur veut vérifier que la génération de posts Facebook fonctionne correctement 
avec les carousels présents dans la bibliothèque. Il faut tester spécifiquement la 
génération pour septembre avec des carousels.

ACTIONS À TESTER:
1. Authentification avec lperpere@yahoo.fr / L@Reunion974!
2. Vérifier les carousels disponibles : Lister les carousels en bibliothèque pour septembre
3. Tester la génération de posts Facebook avec paramètres pour Facebook
4. Analyser le contenu généré pour vérifier les carousels

ENDPOINTS À TESTER:
- POST /api/auth/login (authentification)
- GET /api/content/pending (voir les contenus disponibles)
- GET /api/content/carousel/{carousel_id} (vérifier les carousels)
- POST /api/posts/generate (génération avec carousels)

URL de test: https://post-restore.preview.emergentagent.com/api
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://post-restore.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials from review request
EMAIL = "lperpere@yahoo.fr"
PASSWORD = "L@Reunion974!"

class FacebookCarouselTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.carousels_found = []
        self.september_content = []
        
    def authenticate(self):
        """Étape 1: Authentification avec les identifiants fournis"""
        print("🔐 ÉTAPE 1: Authentification avec lperpere@yahoo.fr...")
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login-robust", json={
                "email": EMAIL,
                "password": PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                print(f"✅ Authentification réussie")
                print(f"   User ID: {self.user_id}")
                print(f"   Email: {data.get('email', 'N/A')}")
                return True
            else:
                print(f"❌ Échec de l'authentification: {response.status_code}")
                print(f"   Réponse: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur d'authentification: {str(e)}")
            return False
    
    def get_library_content(self):
        """Étape 2: Récupérer le contenu de la bibliothèque et identifier les carousels"""
        print("\n📚 ÉTAPE 2: Analyse du contenu de la bibliothèque...")
        
        try:
            # Récupérer tout le contenu disponible
            response = self.session.get(f"{API_BASE}/content/pending?limit=100")
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get('content', [])
                
                print(f"✅ Contenu de la bibliothèque accessible")
                print(f"   Total d'éléments: {len(content_items)}")
                
                # Analyser le contenu pour septembre et les carousels
                september_items = []
                carousel_items = []
                
                for item in content_items:
                    # Vérifier si c'est du contenu de septembre
                    attributed_month = item.get('attributed_month', '')
                    if 'septembre' in attributed_month.lower() or 'september' in attributed_month.lower():
                        september_items.append(item)
                    
                    # Vérifier si c'est un carousel
                    carousel_id = item.get('carousel_id', '')
                    if carousel_id:
                        carousel_items.append(item)
                        if carousel_id not in [c['id'] for c in self.carousels_found]:
                            self.carousels_found.append({
                                'id': carousel_id,
                                'common_title': item.get('common_title', ''),
                                'items_count': 1
                            })
                        else:
                            # Incrémenter le compteur d'éléments pour ce carousel
                            for carousel in self.carousels_found:
                                if carousel['id'] == carousel_id:
                                    carousel['items_count'] += 1
                
                self.september_content = september_items
                
                print(f"   Contenu de septembre: {len(september_items)} éléments")
                print(f"   Carousels détectés: {len(self.carousels_found)}")
                
                # Afficher les détails des carousels trouvés
                if self.carousels_found:
                    print("\n   📋 CAROUSELS DISPONIBLES:")
                    for i, carousel in enumerate(self.carousels_found, 1):
                        print(f"      {i}. ID: {carousel['id']}")
                        print(f"         Titre: {carousel['common_title'] or 'Sans titre'}")
                        print(f"         Images: {carousel['items_count']} éléments")
                
                # Afficher quelques exemples de contenu septembre
                if september_items:
                    print(f"\n   📅 CONTENU SEPTEMBRE (premiers 3 éléments):")
                    for i, item in enumerate(september_items[:3], 1):
                        print(f"      {i}. {item.get('filename', 'Sans nom')} - {item.get('description', 'Sans description')}")
                        if item.get('carousel_id'):
                            print(f"         🎠 Fait partie du carousel: {item.get('carousel_id')}")
                
                return len(content_items) > 0
            else:
                print(f"❌ Échec d'accès à la bibliothèque: {response.status_code}")
                print(f"   Réponse: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur d'accès à la bibliothèque: {str(e)}")
            return False
    
    def test_carousel_endpoints(self):
        """Étape 3: Tester les endpoints de carousels spécifiques"""
        print("\n🎠 ÉTAPE 3: Test des endpoints de carousels...")
        
        if not self.carousels_found:
            print("⚠️ Aucun carousel trouvé pour tester les endpoints")
            return False
        
        carousel_tests_passed = 0
        
        for carousel in self.carousels_found:
            carousel_id = carousel['id']
            print(f"\n   🔍 Test du carousel: {carousel_id}")
            
            try:
                response = self.session.get(f"{API_BASE}/content/carousel/{carousel_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Carousel accessible")
                    print(f"      Type: {data.get('type', 'N/A')}")
                    print(f"      Images: {len(data.get('images', []))} éléments")
                    
                    # Vérifier que les images ont des URLs valides
                    images = data.get('images', [])
                    valid_images = 0
                    for img in images:
                        if img.get('url') and img.get('id'):
                            valid_images += 1
                    
                    print(f"      Images valides: {valid_images}/{len(images)}")
                    carousel_tests_passed += 1
                    
                else:
                    print(f"   ❌ Carousel non accessible: {response.status_code}")
                    print(f"      Réponse: {response.text}")
                    
            except Exception as e:
                print(f"   ❌ Erreur de test du carousel: {str(e)}")
        
        success_rate = (carousel_tests_passed / len(self.carousels_found)) * 100
        print(f"\n   📊 Résultats des tests de carousels: {carousel_tests_passed}/{len(self.carousels_found)} ({success_rate:.1f}%)")
        
        return carousel_tests_passed > 0
    
    def test_facebook_post_generation(self):
        """Étape 4: Tester la génération de posts Facebook avec carousels"""
        print("\n📝 ÉTAPE 4: Test de génération de posts Facebook...")
        
        try:
            # Paramètres de génération pour Facebook avec focus sur septembre
            generation_params = {
                "platforms": ["facebook"],
                "target_month": "septembre_2025",
                "post_count": 3,
                "include_carousels": True,
                "business_objective": "engagement"
            }
            
            print(f"   📋 Paramètres de génération:")
            print(f"      Plateformes: {generation_params['platforms']}")
            print(f"      Mois cible: {generation_params['target_month']}")
            print(f"      Nombre de posts: {generation_params['post_count']}")
            print(f"      Inclure carousels: {generation_params['include_carousels']}")
            
            response = self.session.post(f"{API_BASE}/posts/generate", json=generation_params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Génération de posts réussie")
                
                # Analyser la réponse
                posts = data.get('posts', [])
                carousels_created = data.get('carousels_created', 0)
                
                print(f"      Posts générés: {len(posts)}")
                print(f"      Carousels créés: {carousels_created}")
                
                # Analyser les posts générés pour Facebook
                facebook_posts = [p for p in posts if p.get('platform', '').lower() == 'facebook']
                posts_with_carousels = [p for p in facebook_posts if 'carousel' in str(p.get('visual_url', '')).lower()]
                
                print(f"      Posts Facebook: {len(facebook_posts)}")
                print(f"      Posts avec carousels: {len(posts_with_carousels)}")
                
                # Afficher les détails des posts avec carousels
                if posts_with_carousels:
                    print(f"\n   🎠 POSTS FACEBOOK AVEC CAROUSELS:")
                    for i, post in enumerate(posts_with_carousels, 1):
                        print(f"      {i}. ID: {post.get('id', 'N/A')}")
                        print(f"         Titre: {post.get('title', 'Sans titre')}")
                        print(f"         Plateforme: {post.get('platform', 'N/A')}")
                        print(f"         Visual URL: {post.get('visual_url', 'N/A')}")
                        print(f"         Texte (extrait): {post.get('text', '')[:100]}...")
                        
                        # Vérifier les hashtags
                        hashtags = post.get('hashtags', [])
                        if hashtags:
                            print(f"         Hashtags: {', '.join(hashtags[:5])}")
                
                return {
                    'success': True,
                    'total_posts': len(posts),
                    'facebook_posts': len(facebook_posts),
                    'posts_with_carousels': len(posts_with_carousels),
                    'carousels_created': carousels_created
                }
                
            else:
                print(f"   ❌ Échec de génération: {response.status_code}")
                print(f"      Réponse: {response.text}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            print(f"   ❌ Erreur de génération: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def verify_carousel_urls_in_posts(self):
        """Étape 5: Vérifier que les URLs de carousels sont correctement formatées dans les posts"""
        print("\n🔗 ÉTAPE 5: Vérification des URLs de carousels dans les posts...")
        
        try:
            # Récupérer les posts générés
            response = self.session.get(f"{API_BASE}/posts/generated")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('posts', [])
                
                # Filtrer les posts Facebook récents
                facebook_posts = [p for p in posts if p.get('platform', '').lower() == 'facebook']
                
                print(f"   📊 Posts Facebook trouvés: {len(facebook_posts)}")
                
                carousel_url_issues = []
                valid_carousel_urls = []
                
                for post in facebook_posts:
                    visual_url = post.get('visual_url', '')
                    post_id = post.get('id', 'N/A')
                    
                    if 'carousel' in visual_url.lower():
                        # Vérifier le format de l'URL du carousel
                        if visual_url.startswith('/api/content/carousel/'):
                            valid_carousel_urls.append({
                                'post_id': post_id,
                                'url': visual_url,
                                'platform': post.get('platform')
                            })
                        else:
                            carousel_url_issues.append({
                                'post_id': post_id,
                                'url': visual_url,
                                'issue': 'Format URL incorrect'
                            })
                
                print(f"   ✅ URLs de carousels valides: {len(valid_carousel_urls)}")
                print(f"   ❌ URLs de carousels avec problèmes: {len(carousel_url_issues)}")
                
                # Afficher les détails
                if valid_carousel_urls:
                    print(f"\n   🎠 URLS DE CAROUSELS VALIDES:")
                    for item in valid_carousel_urls[:3]:  # Afficher les 3 premiers
                        print(f"      Post: {item['post_id']}")
                        print(f"      URL: {item['url']}")
                        print(f"      Plateforme: {item['platform']}")
                
                if carousel_url_issues:
                    print(f"\n   ⚠️ PROBLÈMES D'URLS DÉTECTÉS:")
                    for item in carousel_url_issues:
                        print(f"      Post: {item['post_id']}")
                        print(f"      URL problématique: {item['url']}")
                        print(f"      Problème: {item['issue']}")
                
                return {
                    'valid_urls': len(valid_carousel_urls),
                    'invalid_urls': len(carousel_url_issues),
                    'total_facebook_posts': len(facebook_posts)
                }
                
            else:
                print(f"   ❌ Impossible de récupérer les posts: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ Erreur de vérification des URLs: {str(e)}")
            return None
    
    def run_comprehensive_test(self):
        """Exécuter tous les tests de génération Facebook avec carousels"""
        print("🎯 TEST DE GÉNÉRATION DE POSTS FACEBOOK AVEC CAROUSELS (SEPTEMBRE)")
        print("=" * 80)
        print(f"URL de test: {BACKEND_URL}")
        print(f"Identifiants: {EMAIL}")
        print(f"Date du test: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Étape 1: Authentification
        if not self.authenticate():
            print("\n❌ CRITIQUE: Échec de l'authentification - impossible de continuer")
            return False
        
        # Étape 2: Analyse de la bibliothèque
        if not self.get_library_content():
            print("\n❌ CRITIQUE: Impossible d'accéder à la bibliothèque")
            return False
        
        # Étape 3: Test des endpoints de carousels
        carousel_endpoints_ok = self.test_carousel_endpoints()
        
        # Étape 4: Test de génération Facebook
        generation_result = self.test_facebook_post_generation()
        
        # Étape 5: Vérification des URLs
        url_verification = self.verify_carousel_urls_in_posts()
        
        # Résumé des résultats
        print("\n" + "=" * 80)
        print("📊 RÉSUMÉ DES TESTS DE GÉNÉRATION FACEBOOK AVEC CAROUSELS")
        print("=" * 80)
        
        # Calcul du score de réussite
        test_results = {
            "authentification": True,  # Si on arrive ici, c'est réussi
            "bibliotheque_accessible": len(self.september_content) > 0 or len(self.carousels_found) > 0,
            "carousels_detectes": len(self.carousels_found) > 0,
            "endpoints_carousels": carousel_endpoints_ok,
            "generation_facebook": generation_result.get('success', False) if generation_result else False,
            "posts_avec_carousels": generation_result.get('posts_with_carousels', 0) > 0 if generation_result else False,
            "urls_carousels_valides": url_verification.get('valid_urls', 0) > 0 if url_verification else False
        }
        
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"Taux de réussite global: {success_rate:.1f}% ({passed_tests}/{total_tests} tests réussis)")
        print()
        
        # Résultats détaillés
        status_mapping = {
            "authentification": "✅ Authentification avec lperpere@yahoo.fr",
            "bibliotheque_accessible": "✅ Accès à la bibliothèque de contenu",
            "carousels_detectes": "✅ Carousels détectés en bibliothèque",
            "endpoints_carousels": "✅ Endpoints de carousels fonctionnels",
            "generation_facebook": "✅ Génération de posts Facebook",
            "posts_avec_carousels": "✅ Posts générés incluent des carousels",
            "urls_carousels_valides": "✅ URLs de carousels correctement formatées"
        }
        
        for test_key, description in status_mapping.items():
            status = "✅ RÉUSSI" if test_results[test_key] else "❌ ÉCHEC"
            print(f"{description}: {status}")
        
        # Statistiques détaillées
        print(f"\n📈 STATISTIQUES DÉTAILLÉES:")
        print(f"   Carousels trouvés en bibliothèque: {len(self.carousels_found)}")
        print(f"   Contenu de septembre: {len(self.september_content)} éléments")
        
        if generation_result and generation_result.get('success'):
            print(f"   Posts Facebook générés: {generation_result.get('facebook_posts', 0)}")
            print(f"   Posts avec carousels: {generation_result.get('posts_with_carousels', 0)}")
            print(f"   Carousels créés: {generation_result.get('carousels_created', 0)}")
        
        if url_verification:
            print(f"   URLs de carousels valides: {url_verification.get('valid_urls', 0)}")
            print(f"   URLs de carousels invalides: {url_verification.get('invalid_urls', 0)}")
        
        print("\n" + "=" * 80)
        
        # Conclusion
        if success_rate >= 85:
            print("🎉 CONCLUSION: La génération de posts Facebook avec carousels fonctionne PARFAITEMENT")
        elif success_rate >= 70:
            print("✅ CONCLUSION: La génération de posts Facebook avec carousels fonctionne CORRECTEMENT")
        elif success_rate >= 50:
            print("⚠️ CONCLUSION: La génération de posts Facebook avec carousels a quelques PROBLÈMES")
        else:
            print("❌ CONCLUSION: La génération de posts Facebook avec carousels a des PROBLÈMES MAJEURS")
        
        # Recommandations spécifiques
        print(f"\n💡 RECOMMANDATIONS:")
        if not test_results["carousels_detectes"]:
            print("   - Vérifier la présence de carousels en bibliothèque pour septembre")
        if not test_results["generation_facebook"]:
            print("   - Vérifier l'endpoint de génération de posts")
        if not test_results["posts_avec_carousels"]:
            print("   - Vérifier que les carousels sont bien inclus dans la génération")
        if not test_results["urls_carousels_valides"]:
            print("   - Vérifier le formatage des URLs de carousels")
        
        return success_rate >= 70

def main():
    """Exécution principale du test"""
    tester = FacebookCarouselTester()
    success = tester.run_comprehensive_test()
    
    # Code de sortie approprié
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()