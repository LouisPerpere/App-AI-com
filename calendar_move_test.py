#!/usr/bin/env python3
"""
Test urgent du déplacement de post calendrier
Test de l'endpoint PUT /api/posts/move-calendar-post/{post_id}
"""

import requests
import json
import sys
from datetime import datetime

class CalendarMoveTest:
    def __init__(self):
        self.base_url = "https://post-validator.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        
    def authenticate(self, email, password):
        """Authentification avec l'API"""
        try:
            print(f"🔐 Step 1: Authentification avec {email}")
            
            response = self.session.post(
                f"{self.base_url}/auth/login-robust",
                json={"email": email, "password": password},
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
                
                print(f"   ✅ Authentification réussie")
                print(f"   User ID: {self.user_id}")
                print(f"   Token: {self.token[:30]}..." if self.token else "   Token: None")
                return True
            else:
                print(f"   ❌ Échec authentification: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Erreur authentification: {str(e)}")
            return False
    
    def get_calendar_posts(self):
        """Récupérer les posts du calendrier"""
        try:
            print(f"\n📅 Step 2: Récupération des posts calendrier")
            
            response = self.session.get(f"{self.base_url}/calendar/posts")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                count = data.get("count", 0)
                
                print(f"   ✅ {count} posts calendrier trouvés")
                
                if posts:
                    print(f"   Premier post ID: {posts[0].get('id')}")
                    print(f"   Date actuelle: {posts[0].get('scheduled_date')}")
                    print(f"   Titre: {posts[0].get('title', 'Sans titre')}")
                    return posts
                else:
                    print(f"   ⚠️ Aucun post calendrier disponible")
                    return []
            else:
                print(f"   ❌ Erreur récupération posts: {response.text}")
                return []
                
        except Exception as e:
            print(f"   ❌ Erreur récupération posts: {str(e)}")
            return []
    
    def test_move_calendar_post(self, post_id, new_date):
        """Tester le déplacement d'un post calendrier"""
        try:
            print(f"\n🔄 Step 3: Test déplacement post {post_id}")
            print(f"   Nouvelle date: {new_date}")
            
            response = self.session.put(
                f"{self.base_url}/posts/move-calendar-post/{post_id}",
                json={"scheduled_date": new_date}
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                message = data.get("message", "")
                
                if success:
                    print(f"   ✅ Déplacement réussi: {message}")
                    return True
                else:
                    print(f"   ❌ Déplacement échoué: {message}")
                    return False
            else:
                print(f"   ❌ Erreur HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Erreur déplacement: {str(e)}")
            return False
    
    def verify_post_moved(self, post_id, expected_date):
        """Vérifier que le post a bien été déplacé"""
        try:
            print(f"\n✅ Step 4: Vérification du déplacement")
            
            # Récupérer à nouveau les posts calendrier
            posts = self.get_calendar_posts()
            
            # Trouver le post modifié
            moved_post = None
            for post in posts:
                if post.get("id") == post_id:
                    moved_post = post
                    break
            
            if moved_post:
                actual_date = moved_post.get("scheduled_date", "")
                print(f"   Date attendue: {expected_date}")
                print(f"   Date actuelle: {actual_date}")
                
                if actual_date == expected_date:
                    print(f"   ✅ Vérification réussie - Date mise à jour correctement")
                    return True
                else:
                    print(f"   ❌ Vérification échouée - Date non mise à jour")
                    return False
            else:
                print(f"   ❌ Post {post_id} non trouvé après déplacement")
                return False
                
        except Exception as e:
            print(f"   ❌ Erreur vérification: {str(e)}")
            return False
    
    def check_backend_logs(self):
        """Vérifier les logs backend (simulation)"""
        try:
            print(f"\n📋 Step 5: Vérification logs backend")
            
            # Test de santé de l'API pour vérifier la connectivité
            response = self.session.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                print(f"   ✅ Backend accessible et fonctionnel")
                return True
            else:
                print(f"   ❌ Backend non accessible: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Erreur vérification backend: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Exécuter le test complet"""
        print("🎯 TEST URGENT - DÉPLACEMENT POST CALENDRIER")
        print("=" * 60)
        
        # Authentification
        if not self.authenticate("lperpere@yahoo.fr", "L@Reunion974!"):
            print("\n❌ ÉCHEC: Impossible de s'authentifier")
            return False
        
        # Récupérer les posts calendrier
        posts = self.get_calendar_posts()
        if not posts:
            print("\n❌ ÉCHEC: Aucun post calendrier disponible pour le test")
            return False
        
        # Utiliser le premier post disponible
        test_post = posts[0]
        post_id = test_post.get("id")
        current_date = test_post.get("scheduled_date", "")
        
        print(f"\n🎯 Post de test sélectionné:")
        print(f"   ID: {post_id}")
        print(f"   Date actuelle: {current_date}")
        print(f"   Titre: {test_post.get('title', 'Sans titre')}")
        
        # Date de test spécifiée dans la demande
        new_date = "2025-09-27T11:00:00.000Z"
        
        # Tester le déplacement
        if not self.test_move_calendar_post(post_id, new_date):
            print(f"\n❌ ÉCHEC: Déplacement du post échoué")
            return False
        
        # Vérifier que le déplacement a fonctionné
        if not self.verify_post_moved(post_id, new_date):
            print(f"\n❌ ÉCHEC: Vérification du déplacement échouée")
            return False
        
        # Vérifier les logs backend
        if not self.check_backend_logs():
            print(f"\n⚠️ ATTENTION: Problème potentiel avec le backend")
        
        print(f"\n🎉 SUCCÈS: Test de déplacement post calendrier réussi!")
        return True

def main():
    """Fonction principale"""
    tester = CalendarMoveTest()
    
    try:
        success = tester.run_comprehensive_test()
        
        if success:
            print(f"\n✅ RÉSULTAT: Endpoint de déplacement calendrier FONCTIONNEL")
            sys.exit(0)
        else:
            print(f"\n❌ RÉSULTAT: Endpoint de déplacement calendrier DÉFAILLANT")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⚠️ Test interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()