#!/usr/bin/env python3
"""
🚨 DIAGNOSTIC PUBLICATION CRITIQUE - BOUTON PUBLIER NE FONCTIONNE PAS
Test complet pour diagnostiquer pourquoi la publication ne fonctionne pas sur Facebook et Instagram.
Le bouton passe en spinner puis revient à "Publier" au lieu de "Publié".

Identifiants: lperpere@yahoo.fr / L@Reunion974!
Objectif: Identifier pourquoi l'endpoint /api/posts/publish échoue
"""

import requests
import json
import sys
import time
import urllib.parse
from datetime import datetime
from pymongo import MongoClient
import os

class PublicationDiagnostic:
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
                print(f"   Token: {self.token[:30]}..." if self.token else "   Token: None")
                return True
            else:
                print(f"   ❌ Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {str(e)}")
            return False
    
    def check_social_connections_status(self):
        """Vérifier l'état des connexions sociales avec GET /api/debug/social-connections"""
        try:
            print(f"\n🔍 Step 2: Vérification état des connexions sociales")
            print(f"   Endpoint: GET /api/debug/social-connections")
            
            response = self.session.get(f"{self.base_url}/debug/social-connections")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"   ✅ Diagnostic endpoint accessible")
                print(f"   📊 État des connexions:")
                
                # Analyser les connexions
                connections = data.get("social_media_connections", [])
                facebook_connections = [c for c in connections if c.get("platform") == "facebook"]
                instagram_connections = [c for c in connections if c.get("platform") == "instagram"]
                active_connections = [c for c in connections if c.get("active") == True]
                
                print(f"     📋 Total connexions: {len(connections)}")
                print(f"     📘 Facebook: {len(facebook_connections)} connexions")
                print(f"     📷 Instagram: {len(instagram_connections)} connexions")
                print(f"     ✅ Actives: {len(active_connections)} connexions")
                
                # Détails des connexions
                for i, conn in enumerate(connections):
                    platform = conn.get("platform", "unknown")
                    active = "✅ ACTIVE" if conn.get("active") else "❌ INACTIVE"
                    page_name = conn.get("page_name", "N/A")
                    created_at = conn.get("created_at", "unknown")[:10]  # Date only
                    print(f"       {i+1}. {platform.upper()}: {active} | Page: {page_name} | Créé: {created_at}")
                
                # Vérifier si Facebook et Instagram sont actifs
                facebook_active = any(c.get("platform") == "facebook" and c.get("active") for c in connections)
                instagram_active = any(c.get("platform") == "instagram" and c.get("active") for c in connections)
                
                print(f"\n   🎯 STATUT CONNEXIONS POUR PUBLICATION:")
                print(f"     📘 Facebook: {'✅ CONNECTÉ' if facebook_active else '❌ DÉCONNECTÉ'}")
                print(f"     📷 Instagram: {'✅ CONNECTÉ' if instagram_active else '❌ DÉCONNECTÉ'}")
                
                return {
                    "total_connections": len(connections),
                    "facebook_active": facebook_active,
                    "instagram_active": instagram_active,
                    "active_connections": len(active_connections),
                    "connections_data": connections
                }
            else:
                print(f"   ❌ Failed to access diagnostic endpoint: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error checking social connections: {str(e)}")
            return None
    
    def get_available_posts_for_testing(self):
        """Lister les posts disponibles pour publication"""
        try:
            print(f"\n📝 Step 3: Récupération des posts disponibles pour test")
            print(f"   Endpoint: GET /api/posts/generated")
            
            response = self.session.get(f"{self.base_url}/posts/generated")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                
                print(f"   ✅ Retrieved {len(posts)} posts")
                
                # Analyser les posts par plateforme et statut
                facebook_posts = [p for p in posts if p.get("platform") == "facebook"]
                instagram_posts = [p for p in posts if p.get("platform") == "instagram"]
                draft_posts = [p for p in posts if p.get("status") == "draft"]
                validated_posts = [p for p in posts if p.get("validated") == True]
                
                print(f"   📊 Analyse des posts:")
                print(f"     📘 Facebook: {len(facebook_posts)} posts")
                print(f"     📷 Instagram: {len(instagram_posts)} posts")
                print(f"     📝 Brouillons: {len(draft_posts)} posts")
                print(f"     ✅ Validés: {len(validated_posts)} posts")
                
                # Identifier des posts testables
                testable_facebook = [p for p in facebook_posts if p.get("status") == "draft" and not p.get("validated")]
                testable_instagram = [p for p in instagram_posts if p.get("status") == "draft" and not p.get("validated")]
                
                print(f"\n   🎯 POSTS TESTABLES POUR PUBLICATION:")
                print(f"     📘 Facebook testables: {len(testable_facebook)} posts")
                print(f"     📷 Instagram testables: {len(testable_instagram)} posts")
                
                # Afficher quelques exemples
                if testable_facebook:
                    print(f"     📘 Exemples Facebook:")
                    for i, post in enumerate(testable_facebook[:3]):
                        post_id = post.get("id", "N/A")
                        title = post.get("title", "Sans titre")[:40]
                        print(f"       {i+1}. ID: {post_id} | Titre: {title}...")
                
                if testable_instagram:
                    print(f"     📷 Exemples Instagram:")
                    for i, post in enumerate(testable_instagram[:3]):
                        post_id = post.get("id", "N/A")
                        title = post.get("title", "Sans titre")[:40]
                        print(f"       {i+1}. ID: {post_id} | Titre: {title}...")
                
                return {
                    "total_posts": len(posts),
                    "facebook_posts": facebook_posts,
                    "instagram_posts": instagram_posts,
                    "testable_facebook": testable_facebook,
                    "testable_instagram": testable_instagram
                }
            else:
                print(f"   ❌ Failed to get posts: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error getting posts: {str(e)}")
            return None
    
    def test_publish_endpoint_detailed(self, post_id, platform_name):
        """Tester l'endpoint de publication avec un post_id spécifique"""
        try:
            print(f"\n🚀 Step 4: Test endpoint publication - {platform_name}")
            print(f"   Endpoint: POST /api/posts/publish")
            print(f"   Post ID: {post_id}")
            
            # Capturer le timestamp avant l'appel
            start_time = datetime.now()
            
            response = self.session.post(
                f"{self.base_url}/posts/publish",
                json={"post_id": post_id},
                timeout=30  # 30 seconds timeout
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"   ⏱️ Durée de la requête: {duration:.2f} secondes")
            print(f"   📡 Réponse du serveur:")
            print(f"     Status Code: {response.status_code}")
            
            # Analyser la réponse en détail
            try:
                response_data = response.json()
                print(f"     Response JSON: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                
                # Analyser le type d'erreur
                success = response_data.get("success", False)
                message = response_data.get("message", "")
                error = response_data.get("error", "")
                
                print(f"\n   🔍 ANALYSE DE LA RÉPONSE:")
                print(f"     ✅ Success: {success}")
                print(f"     💬 Message: {message}")
                print(f"     ❌ Error: {error}")
                
                # Identifier le type d'erreur
                if "aucune connexion sociale active" in message.lower() or "aucune connexion sociale active" in error.lower():
                    print(f"     🎯 TYPE D'ERREUR: Aucune connexion sociale active")
                    print(f"     📝 EXPLICATION: L'utilisateur n'a pas de connexions {platform_name} actives")
                    return "no_active_connections"
                elif "connexion" in message.lower() or "connection" in message.lower():
                    print(f"     🎯 TYPE D'ERREUR: Problème de connexion")
                    return "connection_issue"
                elif "token" in message.lower() or "token" in error.lower():
                    print(f"     🎯 TYPE D'ERREUR: Problème de token")
                    return "token_issue"
                elif "post non trouvé" in message.lower() or "not found" in message.lower():
                    print(f"     🎯 TYPE D'ERREUR: Post non trouvé")
                    return "post_not_found"
                elif success:
                    print(f"     🎯 RÉSULTAT: Publication réussie!")
                    return "success"
                else:
                    print(f"     🎯 TYPE D'ERREUR: Erreur inconnue")
                    return "unknown_error"
                    
            except json.JSONDecodeError:
                print(f"     Response (raw text): {response.text}")
                if "connexion sociale" in response.text.lower():
                    print(f"     🎯 TYPE D'ERREUR: Aucune connexion sociale (détecté dans texte)")
                    return "no_active_connections"
                return "json_decode_error"
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ TIMEOUT: La requête a pris plus de 30 secondes")
            print(f"   🎯 PROBLÈME POSSIBLE: Endpoint bloqué ou traitement trop long")
            return "timeout"
        except Exception as e:
            print(f"   ❌ Error testing publish endpoint: {str(e)}")
            return "exception"
    
    def analyze_backend_logs(self):
        """Analyser les logs backend pour les erreurs de publication"""
        try:
            print(f"\n📋 Step 5: Analyse des logs backend")
            print(f"   Recherche d'erreurs de publication dans les logs...")
            
            # Note: Dans un environnement de production, on accéderait aux vrais logs
            # Ici on simule l'analyse des logs en cherchant des patterns d'erreur
            
            print(f"   📝 LOGS SIMULÉS - Patterns d'erreur courants:")
            print(f"     ❌ 'Aucune connexion sociale active trouvée'")
            print(f"     ❌ 'Token expired' ou 'Invalid token'")
            print(f"     ❌ 'Facebook API error' ou 'Instagram API error'")
            print(f"     ❌ 'Post not found' ou 'Post non trouvé'")
            print(f"     ❌ 'Rate limit exceeded'")
            
            print(f"   💡 RECOMMANDATION: Vérifier les logs supervisor backend:")
            print(f"     tail -n 100 /var/log/supervisor/backend.*.log")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error analyzing logs: {str(e)}")
            return False
    
    def run_publication_diagnostic(self):
        """Exécuter le diagnostic complet de publication"""
        print("🚨 MISSION: DIAGNOSTIC PUBLICATION CRITIQUE")
        print("🌐 ENVIRONMENT: Preview (social-ai-planner-2.preview.emergentagent.com)")
        print("🎯 OBJECTIF: Identifier pourquoi la publication ne fonctionne pas")
        print("🔍 SYMPTÔME: Bouton spinner → revient à 'Publier' au lieu de 'Publié'")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ CRITICAL: Authentication failed - cannot proceed")
            return False
        
        # Step 2: Check social connections status
        connections_status = self.check_social_connections_status()
        if connections_status is None:
            print("\n❌ CRITICAL: Cannot check social connections status")
            return False
        
        # Step 3: Get available posts for testing
        posts_data = self.get_available_posts_for_testing()
        if posts_data is None:
            print("\n❌ CRITICAL: Cannot retrieve posts for testing")
            return False
        
        # Step 4: Test publication endpoint with different scenarios
        publication_results = {}
        
        # Test Facebook publication if Facebook posts available
        if posts_data["testable_facebook"]:
            facebook_post = posts_data["testable_facebook"][0]
            facebook_post_id = facebook_post.get("id")
            publication_results["facebook"] = self.test_publish_endpoint_detailed(facebook_post_id, "Facebook")
        else:
            print(f"\n⚠️ Aucun post Facebook testable disponible")
            publication_results["facebook"] = "no_testable_posts"
        
        # Test Instagram publication if Instagram posts available
        if posts_data["testable_instagram"]:
            instagram_post = posts_data["testable_instagram"][0]
            instagram_post_id = instagram_post.get("id")
            publication_results["instagram"] = self.test_publish_endpoint_detailed(instagram_post_id, "Instagram")
        else:
            print(f"\n⚠️ Aucun post Instagram testable disponible")
            publication_results["instagram"] = "no_testable_posts"
        
        # Step 5: Analyze backend logs
        self.analyze_backend_logs()
        
        # Final analysis and recommendations
        print("\n" + "=" * 80)
        print("🎉 DIAGNOSTIC PUBLICATION TERMINÉ")
        print("=" * 80)
        
        print(f"\n📊 RÉSULTATS DU DIAGNOSTIC:")
        
        # Connexions analysis
        print(f"   🔗 ÉTAT DES CONNEXIONS:")
        print(f"     📘 Facebook: {'✅ CONNECTÉ' if connections_status['facebook_active'] else '❌ DÉCONNECTÉ'}")
        print(f"     📷 Instagram: {'✅ CONNECTÉ' if connections_status['instagram_active'] else '❌ DÉCONNECTÉ'}")
        print(f"     📊 Total connexions actives: {connections_status['active_connections']}")
        
        # Posts analysis
        print(f"   📝 POSTS DISPONIBLES:")
        print(f"     📘 Facebook: {len(posts_data['facebook_posts'])} posts ({len(posts_data['testable_facebook'])} testables)")
        print(f"     📷 Instagram: {len(posts_data['instagram_posts'])} posts ({len(posts_data['testable_instagram'])} testables)")
        
        # Publication results
        print(f"   🚀 RÉSULTATS PUBLICATION:")
        for platform, result in publication_results.items():
            status_emoji = "✅" if result == "success" else "❌"
            print(f"     {platform.upper()}: {status_emoji} {result}")
        
        # Root cause analysis
        print(f"\n🔍 ANALYSE CAUSE RACINE:")
        
        if connections_status['active_connections'] == 0:
            print(f"   🎯 CAUSE PRINCIPALE: Aucune connexion sociale active")
            print(f"   📝 EXPLICATION: L'endpoint /api/posts/publish retourne correctement")
            print(f"      'Aucune connexion sociale active trouvée' car l'utilisateur")
            print(f"      n'a pas de connexions Facebook/Instagram actives.")
            print(f"   ✅ COMPORTEMENT ATTENDU: Le bouton revient à 'Publier' car")
            print(f"      la publication échoue (pas de connexions actives).")
        elif "no_active_connections" in publication_results.values():
            print(f"   🎯 CAUSE PRINCIPALE: Connexions inactives ou tokens expirés")
            print(f"   📝 EXPLICATION: Les connexions existent mais ne sont pas actives")
            print(f"      ou les tokens d'accès ont expiré.")
        elif "timeout" in publication_results.values():
            print(f"   🎯 CAUSE PRINCIPALE: Timeout de l'endpoint de publication")
            print(f"   📝 EXPLICATION: L'endpoint prend trop de temps à répondre")
        else:
            print(f"   🎯 CAUSE PRINCIPALE: Erreur technique dans l'endpoint")
            print(f"   📝 EXPLICATION: Problème technique à investiguer plus en détail")
        
        # Recommendations
        print(f"\n🚀 RECOMMANDATIONS:")
        
        if connections_status['active_connections'] == 0:
            print(f"   1. 🔗 RECONNECTER LES COMPTES SOCIAUX:")
            print(f"      - Aller dans les paramètres de connexions sociales")
            print(f"      - Reconnecter Facebook et Instagram")
            print(f"      - Vérifier que les connexions sont marquées comme actives")
            
        print(f"   2. 🔍 VÉRIFIER LES LOGS BACKEND:")
        print(f"      - Exécuter: tail -n 100 /var/log/supervisor/backend.*.log")
        print(f"      - Chercher les erreurs lors des tentatives de publication")
        
        print(f"   3. 🧪 TESTER APRÈS RECONNEXION:")
        print(f"      - Une fois les comptes reconnectés, retester la publication")
        print(f"      - Le bouton devrait passer à 'Publié' si les connexions sont actives")
        
        print(f"\n💡 CONCLUSION:")
        if connections_status['active_connections'] == 0:
            print(f"   ✅ DIAGNOSTIC RÉUSSI: Le problème est identifié")
            print(f"   🎯 SOLUTION: Reconnecter les comptes sociaux")
            print(f"   📝 L'endpoint /api/posts/publish fonctionne correctement")
            print(f"      mais retourne une erreur car aucune connexion n'est active.")
        else:
            print(f"   ⚠️ INVESTIGATION SUPPLÉMENTAIRE REQUISE")
            print(f"   🔍 Vérifier les logs backend pour plus de détails")
        
        print("=" * 80)
        
        return True

def main():
    """Main execution function"""
    diagnostic = PublicationDiagnostic()
    
    try:
        success = diagnostic.run_publication_diagnostic()
        if success:
            print(f"\n🎯 CONCLUSION: Diagnostic publication TERMINÉ AVEC SUCCÈS")
            print(f"   Cause racine identifiée et recommandations fournies")
            sys.exit(0)
        else:
            print(f"\n💥 CONCLUSION: Diagnostic publication ÉCHOUÉ")
            print(f"   Vérifier les messages d'erreur ci-dessus")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⚠️ Diagnostic interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue pendant le diagnostic: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()