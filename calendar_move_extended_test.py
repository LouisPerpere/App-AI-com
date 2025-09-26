#!/usr/bin/env python3
"""
Test étendu du déplacement de post calendrier
Test avec plusieurs dates pour validation complète
"""

import requests
import json
import sys
from datetime import datetime

class ExtendedCalendarMoveTest:
    def __init__(self):
        self.base_url = "https://post-validator.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        
    def authenticate(self, email, password):
        """Authentification avec l'API"""
        try:
            print(f"🔐 Authentification avec {email}")
            
            response = self.session.post(
                f"{self.base_url}/auth/login-robust",
                json={"email": email, "password": password},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                })
                
                print(f"   ✅ Authentification réussie (User ID: {self.user_id})")
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
            response = self.session.get(f"{self.base_url}/calendar/posts")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                return posts
            else:
                print(f"   ❌ Erreur récupération posts: {response.text}")
                return []
                
        except Exception as e:
            print(f"   ❌ Erreur récupération posts: {str(e)}")
            return []
    
    def test_move_calendar_post(self, post_id, new_date, test_name):
        """Tester le déplacement d'un post calendrier"""
        try:
            print(f"\n🔄 {test_name}")
            print(f"   Post ID: {post_id}")
            print(f"   Nouvelle date: {new_date}")
            
            response = self.session.put(
                f"{self.base_url}/posts/move-calendar-post/{post_id}",
                json={"scheduled_date": new_date}
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                message = data.get("message", "")
                
                if success:
                    print(f"   ✅ {message}")
                    
                    # Vérifier immédiatement
                    posts = self.get_calendar_posts()
                    moved_post = next((p for p in posts if p.get("id") == post_id), None)
                    
                    if moved_post and moved_post.get("scheduled_date") == new_date:
                        print(f"   ✅ Vérification: Date mise à jour correctement")
                        return True
                    else:
                        print(f"   ❌ Vérification: Date non mise à jour")
                        return False
                else:
                    print(f"   ❌ Déplacement échoué: {message}")
                    return False
            else:
                print(f"   ❌ Erreur HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Erreur déplacement: {str(e)}")
            return False
    
    def test_invalid_date_format(self, post_id):
        """Tester avec un format de date invalide"""
        try:
            print(f"\n🔄 Test format de date invalide")
            
            response = self.session.put(
                f"{self.base_url}/posts/move-calendar-post/{post_id}",
                json={"scheduled_date": "invalid-date-format"}
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 400:
                print(f"   ✅ Validation de format correcte (400 attendu)")
                return True
            else:
                print(f"   ❌ Validation de format incorrecte: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Erreur test format: {str(e)}")
            return False
    
    def test_nonexistent_post(self):
        """Tester avec un post inexistant"""
        try:
            print(f"\n🔄 Test post inexistant")
            
            response = self.session.put(
                f"{self.base_url}/posts/move-calendar-post/nonexistent-post-id",
                json={"scheduled_date": "2025-09-27T11:00:00.000Z"}
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 404:
                print(f"   ✅ Gestion post inexistant correcte (404 attendu)")
                return True
            else:
                print(f"   ❌ Gestion post inexistant incorrecte: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Erreur test post inexistant: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Exécuter le test complet"""
        print("🎯 TEST ÉTENDU - DÉPLACEMENT POST CALENDRIER")
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
        
        test_post = posts[0]
        post_id = test_post.get("id")
        original_date = test_post.get("scheduled_date", "")
        
        print(f"\n📋 Post de test: {post_id}")
        print(f"   Date originale: {original_date}")
        
        # Tests multiples
        test_results = []
        
        # Test 1: Date spécifiée dans la demande
        test_results.append(self.test_move_calendar_post(
            post_id, 
            "2025-09-27T11:00:00.000Z", 
            "Test 1: Date demandée (27 sept 2025 11:00)"
        ))
        
        # Test 2: Autre date pour vérifier la flexibilité
        test_results.append(self.test_move_calendar_post(
            post_id, 
            "2025-10-15T14:30:00.000Z", 
            "Test 2: Date alternative (15 oct 2025 14:30)"
        ))
        
        # Test 3: Retour à la date originale
        test_results.append(self.test_move_calendar_post(
            post_id, 
            original_date, 
            "Test 3: Retour date originale"
        ))
        
        # Test 4: Format de date invalide
        test_results.append(self.test_invalid_date_format(post_id))
        
        # Test 5: Post inexistant
        test_results.append(self.test_nonexistent_post())
        
        # Résultats
        successful_tests = sum(test_results)
        total_tests = len(test_results)
        
        print(f"\n📊 RÉSULTATS:")
        print(f"   Tests réussis: {successful_tests}/{total_tests}")
        print(f"   Taux de réussite: {(successful_tests/total_tests)*100:.1f}%")
        
        if successful_tests == total_tests:
            print(f"\n🎉 SUCCÈS COMPLET: Tous les tests sont passés!")
            return True
        else:
            print(f"\n⚠️ SUCCÈS PARTIEL: {total_tests - successful_tests} test(s) échoué(s)")
            return False

def main():
    """Fonction principale"""
    tester = ExtendedCalendarMoveTest()
    
    try:
        success = tester.run_comprehensive_test()
        
        if success:
            print(f"\n✅ RÉSULTAT FINAL: Endpoint de déplacement calendrier PLEINEMENT FONCTIONNEL")
            sys.exit(0)
        else:
            print(f"\n⚠️ RÉSULTAT FINAL: Endpoint de déplacement calendrier PARTIELLEMENT FONCTIONNEL")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⚠️ Test interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()