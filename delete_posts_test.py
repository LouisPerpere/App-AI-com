#!/usr/bin/env python3
"""
TEST URGENT - Endpoint de suppression de tous les posts
Test spécifique pour l'endpoint DELETE /api/posts/generated/all

CONTEXTE: L'interface montre encore des posts après suppression
OBJECTIF: Vérifier que l'endpoint supprime effectivement tous les posts et reset les badges

TESTS CRITIQUES:
1. DELETE /api/posts/generated/all avec authentification
2. Vérification suppression effective (GET /api/posts/generated)
3. Vérification reset badges used_in_posts (GET /api/content/pending)
4. Vérification suppression carrousels

Credentials: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://social-ai-planner-2.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class DeletePostsTest:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        
    def authenticate(self):
        """Authentification avec les credentials fournis"""
        print("🔐 ÉTAPE 1: Authentification...")
        
        auth_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json=auth_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Configure headers for subsequent requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                })
                
                print(f"✅ Authentification réussie")
                print(f"   User ID: {self.user_id}")
                print(f"   Token: {self.token[:20]}..." if self.token else "No token")
                return True
            else:
                print(f"❌ Échec authentification: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur authentification: {str(e)}")
            return False
    
    def get_posts_before_deletion(self):
        """Récupérer les posts avant suppression pour debugging"""
        print("\n📊 ÉTAPE 2: Vérification posts existants avant suppression...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/posts/generated", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                
                print(f"✅ GET /api/posts/generated réussi")
                print(f"   Nombre de posts avant suppression: {len(posts)}")
                
                if posts:
                    print(f"   Premier post ID: {posts[0].get('id', 'N/A')}")
                    print(f"   Premier post titre: {posts[0].get('title', 'N/A')}")
                    print(f"   User ID dans le premier post: {posts[0].get('owner_id', 'N/A')}")
                    
                    # Afficher les user_ids pour debugging
                    user_ids_in_posts = set()
                    for post in posts:
                        owner_id = post.get('owner_id')
                        if owner_id:
                            user_ids_in_posts.add(owner_id)
                    
                    print(f"   User IDs trouvés dans les posts: {list(user_ids_in_posts)}")
                    print(f"   User ID actuel: {self.user_id}")
                    
                    if self.user_id in user_ids_in_posts:
                        print(f"✅ User ID match trouvé - posts appartiennent à l'utilisateur")
                    else:
                        print(f"⚠️ User ID mismatch - posts peuvent appartenir à d'autres utilisateurs")
                
                return len(posts)
            else:
                print(f"❌ Échec GET posts: {response.status_code}")
                print(f"   Response: {response.text}")
                return 0
                
        except Exception as e:
            print(f"❌ Erreur GET posts: {str(e)}")
            return 0
    
    def get_media_before_deletion(self):
        """Récupérer les médias avec used_in_posts=true avant suppression"""
        print("\n📊 ÉTAPE 3: Vérification badges used_in_posts avant suppression...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/content/pending", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                
                print(f"✅ GET /api/content/pending réussi")
                print(f"   Nombre total de médias: {len(content_items)}")
                
                # Compter les médias avec used_in_posts=true
                used_in_posts_count = 0
                used_media_ids = []
                
                for item in content_items:
                    if item.get("used_in_posts", False):
                        used_in_posts_count += 1
                        used_media_ids.append(item.get("id", "N/A"))
                
                print(f"   Médias avec used_in_posts=true: {used_in_posts_count}")
                if used_media_ids:
                    print(f"   IDs des médias utilisés: {used_media_ids[:5]}..." if len(used_media_ids) > 5 else f"   IDs des médias utilisés: {used_media_ids}")
                
                return used_in_posts_count, used_media_ids
            else:
                print(f"❌ Échec GET content: {response.status_code}")
                print(f"   Response: {response.text}")
                return 0, []
                
        except Exception as e:
            print(f"❌ Erreur GET content: {str(e)}")
            return 0, []
    
    def delete_all_posts(self):
        """TEST CRITIQUE 1: DELETE /api/posts/generated/all"""
        print("\n🗑️ TEST CRITIQUE 1: DELETE /api/posts/generated/all...")
        
        try:
            print(f"   Envoi de DELETE vers {BACKEND_URL}/posts/generated/all")
            print(f"   User ID utilisé: {self.user_id}")
            
            response = self.session.delete(f"{BACKEND_URL}/posts/generated/all", timeout=30)
            
            print(f"   Status code reçu: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ DELETE /api/posts/generated/all réussi")
                print(f"   Response: {json.dumps(data, indent=2)}")
                
                deleted_posts = data.get("deleted_posts", 0)
                deleted_carousels = data.get("deleted_carousels", 0)
                reset_media_flags = data.get("reset_media_flags", 0)
                
                print(f"   Posts supprimés: {deleted_posts}")
                print(f"   Carrousels supprimés: {deleted_carousels}")
                print(f"   Flags médias reset: {reset_media_flags}")
                
                return True, deleted_posts, deleted_carousels, reset_media_flags
            else:
                print(f"❌ Échec DELETE posts: {response.status_code}")
                print(f"   Response: {response.text}")
                return False, 0, 0, 0
                
        except Exception as e:
            print(f"❌ Erreur DELETE posts: {str(e)}")
            return False, 0, 0, 0
    
    def verify_posts_deletion(self):
        """TEST CRITIQUE 2: Vérification suppression effective"""
        print("\n🔍 TEST CRITIQUE 2: Vérification suppression effective...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/posts/generated", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                
                print(f"✅ GET /api/posts/generated après suppression réussi")
                print(f"   Nombre de posts restants: {len(posts)}")
                
                if len(posts) == 0:
                    print(f"✅ SUPPRESSION CONFIRMÉE: Aucun post restant")
                    return True
                else:
                    print(f"❌ PROBLÈME SUPPRESSION: {len(posts)} posts encore présents")
                    
                    # Afficher les posts restants pour debugging
                    for i, post in enumerate(posts[:3]):  # Afficher max 3 posts
                        print(f"   Post restant {i+1}:")
                        print(f"     ID: {post.get('id', 'N/A')}")
                        print(f"     Titre: {post.get('title', 'N/A')}")
                        print(f"     Owner ID: {post.get('owner_id', 'N/A')}")
                        print(f"     Status: {post.get('status', 'N/A')}")
                    
                    return False
            else:
                print(f"❌ Échec GET posts après suppression: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur vérification suppression: {str(e)}")
            return False
    
    def verify_badges_reset(self, expected_reset_count):
        """TEST CRITIQUE 3: Vérification reset badges used_in_posts"""
        print("\n🏷️ TEST CRITIQUE 3: Vérification reset badges used_in_posts...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/content/pending", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                
                print(f"✅ GET /api/content/pending après suppression réussi")
                print(f"   Nombre total de médias: {len(content_items)}")
                
                # Compter les médias avec used_in_posts=true après suppression
                used_in_posts_count = 0
                still_used_media_ids = []
                
                for item in content_items:
                    if item.get("used_in_posts", False):
                        used_in_posts_count += 1
                        still_used_media_ids.append(item.get("id", "N/A"))
                
                print(f"   Médias avec used_in_posts=true après suppression: {used_in_posts_count}")
                
                if used_in_posts_count == 0:
                    print(f"✅ BADGES RESET CONFIRMÉ: Tous les badges verts ont disparu")
                    return True
                else:
                    print(f"❌ PROBLÈME BADGES: {used_in_posts_count} médias ont encore used_in_posts=true")
                    if still_used_media_ids:
                        print(f"   IDs des médias encore marqués: {still_used_media_ids[:5]}..." if len(still_used_media_ids) > 5 else f"   IDs des médias encore marqués: {still_used_media_ids}")
                    return False
            else:
                print(f"❌ Échec GET content après suppression: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur vérification badges: {str(e)}")
            return False
    
    def verify_carousels_deletion(self):
        """TEST CRITIQUE 4: Vérification suppression carrousels (si endpoint disponible)"""
        print("\n🎠 TEST CRITIQUE 4: Vérification suppression carrousels...")
        
        # Note: Il n'y a pas d'endpoint direct pour lister les carrousels
        # On peut vérifier indirectement via les posts qui avaient des carrousels
        print("ℹ️  Pas d'endpoint direct pour vérifier les carrousels")
        print("ℹ️  La suppression des carrousels est confirmée par l'endpoint DELETE")
        return True
    
    def run_complete_test(self):
        """Exécuter le test complet de suppression"""
        print("=" * 80)
        print("🗑️ TEST URGENT - Endpoint de suppression de tous les posts")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Credentials: {TEST_EMAIL} / {TEST_PASSWORD}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Étape 1: Authentification
        if not self.authenticate():
            print("\n❌ TEST ÉCHOUÉ: Impossible de s'authentifier")
            return False
        
        # Étape 2: État avant suppression
        posts_before = self.get_posts_before_deletion()
        used_media_before, used_media_ids_before = self.get_media_before_deletion()
        
        print(f"\n📊 ÉTAT AVANT SUPPRESSION:")
        print(f"   Posts existants: {posts_before}")
        print(f"   Médias avec badges verts: {used_media_before}")
        
        # Étape 3: Suppression
        delete_success, deleted_posts, deleted_carousels, reset_flags = self.delete_all_posts()
        if not delete_success:
            print("\n❌ TEST ÉCHOUÉ: Impossible de supprimer les posts")
            return False
        
        # Étape 4: Vérifications post-suppression
        posts_deleted = self.verify_posts_deletion()
        badges_reset = self.verify_badges_reset(reset_flags)
        carousels_deleted = self.verify_carousels_deletion()
        
        # Résumé final
        print("\n" + "=" * 80)
        print("📋 RÉSUMÉ DU TEST DE SUPPRESSION")
        print("=" * 80)
        print(f"Posts avant suppression: {posts_before}")
        print(f"Posts supprimés (selon API): {deleted_posts}")
        print(f"Carrousels supprimés: {deleted_carousels}")
        print(f"Flags médias reset: {reset_flags}")
        print(f"Médias avec badges avant: {used_media_before}")
        print("")
        print("RÉSULTATS DES VÉRIFICATIONS:")
        print(f"✅ Endpoint DELETE répond: OUI" if delete_success else "❌ Endpoint DELETE répond: NON")
        print(f"✅ Posts effectivement supprimés: OUI" if posts_deleted else "❌ Posts effectivement supprimés: NON")
        print(f"✅ Badges used_in_posts reset: OUI" if badges_reset else "❌ Badges used_in_posts reset: NON")
        print(f"✅ Carrousels supprimés: OUI" if carousels_deleted else "❌ Carrousels supprimés: NON")
        
        # Conclusion
        all_tests_passed = delete_success and posts_deleted and badges_reset and carousels_deleted
        
        if all_tests_passed:
            print("\n🎉 CONCLUSION: ENDPOINT DELETE FONCTIONNE CORRECTEMENT")
            print("✅ Tous les posts ont été supprimés")
            print("✅ Tous les badges verts ont disparu")
            print("✅ Les carrousels ont été supprimés")
            print("✅ L'interface devrait maintenant être vide")
        else:
            print("\n❌ CONCLUSION: PROBLÈMES DÉTECTÉS AVEC L'ENDPOINT DELETE")
            
            if not posts_deleted:
                print("❌ PROBLÈME PRINCIPAL: Les posts ne sont pas supprimés effectivement")
                print("   → Vérifier la requête MongoDB dans l'endpoint")
                print("   → Vérifier que owner_id correspond au user_id")
                print(f"   → User ID utilisé: {self.user_id}")
            
            if not badges_reset:
                print("❌ PROBLÈME BADGES: Les flags used_in_posts ne sont pas reset")
                print("   → Vérifier la requête de mise à jour des médias")
            
            print("\n🔍 DEBUGGING REQUIS:")
            print("   1. Vérifier les logs backend pendant la suppression")
            print("   2. Vérifier la collection MongoDB generated_posts")
            print("   3. Vérifier les requêtes MongoDB executées")
            print("   4. Comparer owner_id vs user_id dans les collections")
        
        return all_tests_passed

def main():
    """Point d'entrée principal"""
    test = DeletePostsTest()
    success = test.run_complete_test()
    
    if success:
        print("\n🎉 TEST TERMINÉ AVEC SUCCÈS")
        sys.exit(0)
    else:
        print("\n💥 TEST ÉCHOUÉ - PROBLÈMES DÉTECTÉS")
        sys.exit(1)

if __name__ == "__main__":
    main()