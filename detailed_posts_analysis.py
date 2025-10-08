#!/usr/bin/env python3
"""
VÉRIFICATION DÉTAILLÉE DES POSTS GÉNÉRÉS - CONTENU FERMETURE SEPTEMBRE
Test pour vérifier si la note de fermeture du 30 septembre apparaît dans le contenu des posts générés
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://post-restore.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class PostContentAnalysis:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        
    def authenticate(self):
        """Authentification"""
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
                
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                })
                
                print(f"✅ Authentification réussie - User ID: {self.user_id}")
                return True
            else:
                print(f"❌ Échec authentification: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur authentification: {str(e)}")
            return False
    
    def analyze_generated_posts_content(self):
        """Analyser le contenu des posts générés pour la note de fermeture"""
        print("\n🔍 ANALYSE DÉTAILLÉE DU CONTENU DES POSTS GÉNÉRÉS...")
        
        try:
            # Récupérer les posts générés
            response = self.session.get(f"{BACKEND_URL}/posts/generated", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                
                print(f"✅ {len(posts)} posts générés récupérés")
                
                if not posts:
                    print("❌ Aucun post trouvé")
                    return False
                
                # Analyser chaque post pour la mention de fermeture
                closure_mentions = []
                september_mentions = []
                
                for i, post in enumerate(posts, 1):
                    title = post.get("title", "").lower()
                    text = post.get("text", "").lower()
                    hashtags = " ".join(post.get("hashtags", [])).lower()
                    
                    full_content = f"{title} {text} {hashtags}"
                    
                    print(f"\n--- POST {i} ---")
                    print(f"Titre: {post.get('title', 'N/A')}")
                    print(f"Texte: {post.get('text', 'N/A')[:100]}...")
                    print(f"Hashtags: {post.get('hashtags', [])}")
                    print(f"Date programmée: {post.get('scheduled_date', 'N/A')}")
                    
                    # Chercher les mentions de fermeture
                    closure_keywords = ["fermeture", "fermé", "ferme", "30 septembre", "exceptionnelle"]
                    september_keywords = ["septembre", "september"]
                    
                    found_closure = any(keyword in full_content for keyword in closure_keywords)
                    found_september = any(keyword in full_content for keyword in september_keywords)
                    
                    if found_closure:
                        closure_mentions.append({
                            "post_number": i,
                            "title": post.get('title', ''),
                            "keywords_found": [kw for kw in closure_keywords if kw in full_content]
                        })
                        print(f"🔒 FERMETURE DÉTECTÉE: {[kw for kw in closure_keywords if kw in full_content]}")
                    
                    if found_september:
                        september_mentions.append({
                            "post_number": i,
                            "title": post.get('title', ''),
                            "keywords_found": [kw for kw in september_keywords if kw in full_content]
                        })
                        print(f"📅 SEPTEMBRE DÉTECTÉ: {[kw for kw in september_keywords if kw in full_content]}")
                    
                    if not found_closure and not found_september:
                        print(f"ℹ️  Aucune mention de fermeture ou septembre")
                
                # Résumé de l'analyse
                print(f"\n📊 RÉSUMÉ ANALYSE CONTENU:")
                print(f"   Total posts: {len(posts)}")
                print(f"   Posts mentionnant fermeture: {len(closure_mentions)}")
                print(f"   Posts mentionnant septembre: {len(september_mentions)}")
                
                if closure_mentions:
                    print(f"\n✅ FERMETURE MENTIONNÉE DANS LES POSTS:")
                    for mention in closure_mentions:
                        print(f"   Post {mention['post_number']}: {mention['title']}")
                        print(f"   Mots-clés trouvés: {mention['keywords_found']}")
                else:
                    print(f"\n❌ AUCUNE MENTION DE FERMETURE DANS LES POSTS")
                    print(f"   La note de fermeture n'a pas été intégrée dans le contenu")
                
                return len(closure_mentions) > 0, {
                    "total_posts": len(posts),
                    "closure_mentions": len(closure_mentions),
                    "september_mentions": len(september_mentions),
                    "posts_with_closure": closure_mentions
                }
                
            else:
                print(f"❌ Échec récupération posts: {response.status_code}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Erreur analyse posts: {str(e)}")
            return False, {}
    
    def check_notes_content_details(self):
        """Vérifier le contenu exact de la note de fermeture"""
        print("\n📝 VÉRIFICATION DÉTAILLÉE DE LA NOTE DE FERMETURE...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/notes", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                notes = data.get("notes", [])
                
                # Trouver la note de fermeture
                closure_note = None
                for note in notes:
                    note_content = note.get("content", "").lower()
                    note_description = note.get("description", "").lower()
                    
                    if any(keyword in f"{note_content} {note_description}" 
                           for keyword in ["fermeture", "fermé", "30 septembre"]):
                        closure_note = note
                        break
                
                if closure_note:
                    print(f"✅ Note de fermeture trouvée:")
                    print(f"   ID: {closure_note.get('note_id', 'N/A')}")
                    print(f"   Description: {closure_note.get('description', 'N/A')}")
                    print(f"   Contenu complet: {closure_note.get('content', 'N/A')}")
                    print(f"   is_monthly_note: {closure_note.get('is_monthly_note', 'N/A')}")
                    print(f"   note_month: {closure_note.get('note_month', 'N/A')}")
                    print(f"   note_year: {closure_note.get('note_year', 'N/A')}")
                    print(f"   target_month: {closure_note.get('target_month', 'N/A')}")
                    print(f"   priority: {closure_note.get('priority', 'N/A')}")
                    print(f"   deleted: {closure_note.get('deleted', 'N/A')}")
                    
                    return True, closure_note
                else:
                    print(f"❌ Note de fermeture non trouvée")
                    return False, None
                    
            else:
                print(f"❌ Échec récupération notes: {response.status_code}")
                return False, None
                
        except Exception as e:
            print(f"❌ Erreur vérification notes: {str(e)}")
            return False, None
    
    def run_detailed_analysis(self):
        """Exécuter l'analyse détaillée"""
        print("=" * 80)
        print("🔍 ANALYSE DÉTAILLÉE - CONTENU FERMETURE DANS POSTS GÉNÉRÉS")
        print("=" * 80)
        print(f"Objectif: Vérifier si la note de fermeture du 30 septembre")
        print(f"apparaît effectivement dans le contenu des posts générés")
        print("=" * 80)
        
        # Authentification
        if not self.authenticate():
            return False
        
        # Vérifier le contenu de la note de fermeture
        note_found, closure_note = self.check_notes_content_details()
        
        # Analyser le contenu des posts générés
        posts_analyzed, analysis_result = self.analyze_generated_posts_content()
        
        # Diagnostic final
        print("\n" + "=" * 80)
        print("🎯 DIAGNOSTIC FINAL - INTÉGRATION NOTE DE FERMETURE")
        print("=" * 80)
        
        if note_found and closure_note:
            print(f"✅ Note de fermeture correctement configurée:")
            print(f"   Contenu: {closure_note.get('content', 'N/A')}")
            print(f"   Configuration: note_month={closure_note.get('note_month')}, note_year={closure_note.get('note_year')}")
        
        if posts_analyzed and analysis_result:
            total_posts = analysis_result.get('total_posts', 0)
            closure_mentions = analysis_result.get('closure_mentions', 0)
            
            if closure_mentions > 0:
                print(f"✅ SUCCÈS: Note de fermeture intégrée dans {closure_mentions}/{total_posts} posts")
                print(f"   La note de fermeture est correctement prise en compte!")
            else:
                print(f"❌ PROBLÈME: Note de fermeture NON intégrée dans les posts")
                print(f"   Bien que la note soit récupérée, elle n'apparaît pas dans le contenu")
                print(f"   CAUSE POSSIBLE: L'IA de génération ne l'utilise pas ou la filtre")
                print(f"   SOLUTION: Vérifier la logique de génération de contenu dans posts_generator.py")
        
        return posts_analyzed and analysis_result.get('closure_mentions', 0) > 0

def main():
    """Point d'entrée principal"""
    analyzer = PostContentAnalysis()
    success = analyzer.run_detailed_analysis()
    
    if success:
        print("\n🎉 ANALYSE TERMINÉE: Note de fermeture intégrée avec succès")
        sys.exit(0)
    else:
        print("\n⚠️  ANALYSE TERMINÉE: Note de fermeture non intégrée dans les posts")
        sys.exit(1)

if __name__ == "__main__":
    main()