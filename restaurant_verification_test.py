#!/usr/bin/env python3
"""
VÉRIFICATION URGENTE - Test de présence du contenu restaurant sur l'environnement LIVE
Objectif: Confirmer si l'analyse de site web et les 8 posts sont réellement présents sur claire-marcus.com
"""

import requests
import json
import sys
from datetime import datetime

# CONFIGURATION CRITIQUE - ENVIRONNEMENT LIVE UNIQUEMENT
LIVE_BASE_URL = "https://claire-marcus.com/api"
TEST_EMAIL = "test@claire-marcus.com"
TEST_PASSWORD = "test123!"

class LiveEnvironmentTester:
    def __init__(self):
        self.base_url = LIVE_BASE_URL
        self.token = None
        self.user_id = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Claire-Marcus-Testing-Agent/1.0'
        })
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def authenticate(self):
        """Authentification sur l'environnement LIVE"""
        self.log("🔐 ÉTAPE 1: Authentification sur l'environnement LIVE")
        self.log(f"   URL: {self.base_url}/auth/login-robust")
        self.log(f"   Email: {TEST_EMAIL}")
        
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login-robust",
                json={
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD
                },
                timeout=30
            )
            
            self.log(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                if self.token and self.user_id:
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.token}'
                    })
                    self.log(f"✅ AUTHENTIFICATION RÉUSSIE")
                    self.log(f"   User ID: {self.user_id}")
                    self.log(f"   Token: {self.token[:20]}...")
                    return True
                else:
                    self.log("❌ ERREUR: Token ou User ID manquant dans la réponse", "ERROR")
                    return False
            else:
                self.log(f"❌ ERREUR D'AUTHENTIFICATION: {response.status_code}", "ERROR")
                try:
                    error_data = response.json()
                    self.log(f"   Détails: {error_data}", "ERROR")
                except:
                    self.log(f"   Réponse brute: {response.text}", "ERROR")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ ERREUR DE CONNEXION: {str(e)}", "ERROR")
            return False
    
    def check_website_analysis(self):
        """Vérifier la présence de l'analyse de site web"""
        self.log("🔍 ÉTAPE 2: Vérification de l'analyse de site web")
        
        # Essayer plusieurs endpoints possibles pour l'analyse de site web
        endpoints_to_check = [
            "/website-analysis",
            "/notes",  # L'analyse pourrait être stockée comme note
            "/business-profile"  # Ou dans le profil business
        ]
        
        website_analysis_found = False
        
        for endpoint in endpoints_to_check:
            self.log(f"   Vérification: GET {self.base_url}{endpoint}")
            
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=30)
                self.log(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if endpoint == "/notes":
                        # Chercher l'analyse de site web dans les notes
                        notes = data.get("notes", [])
                        for note in notes:
                            content = note.get("content", "").lower()
                            description = note.get("description", "").lower()
                            if ("lebistrotdejean" in content or "lebistrotdejean" in description or
                                "analyse" in description or "seo" in content):
                                self.log("✅ ANALYSE DE SITE WEB TROUVÉE dans les notes")
                                self.log(f"   Description: {note.get('description', 'N/A')}")
                                self.log(f"   Contenu (extrait): {content[:100]}...")
                                website_analysis_found = True
                                break
                    
                    elif endpoint == "/business-profile":
                        # Vérifier le profil business pour le restaurant
                        business_name = data.get("business_name", "")
                        website_url = data.get("website_url", "")
                        if "bistrot" in business_name.lower() or "lebistrotdejean" in website_url:
                            self.log("✅ PROFIL RESTAURANT TROUVÉ")
                            self.log(f"   Nom: {business_name}")
                            self.log(f"   Site web: {website_url}")
                            website_analysis_found = True
                    
                    elif endpoint == "/website-analysis":
                        # Endpoint dédié à l'analyse
                        if data:
                            self.log("✅ ANALYSE DE SITE WEB TROUVÉE via endpoint dédié")
                            self.log(f"   Données: {json.dumps(data, indent=2)}")
                            website_analysis_found = True
                
                elif response.status_code == 404:
                    self.log(f"   Endpoint non disponible: {endpoint}")
                else:
                    self.log(f"   Erreur {response.status_code}: {response.text[:100]}")
                    
            except requests.exceptions.RequestException as e:
                self.log(f"   Erreur de connexion: {str(e)}", "ERROR")
        
        return website_analysis_found
    
    def check_generated_posts(self):
        """Vérifier la présence des 8 posts générés"""
        self.log("📝 ÉTAPE 3: Vérification des posts générés")
        
        endpoints_to_check = [
            "/posts/generated",
            "/notes"  # Les posts pourraient être stockés comme notes
        ]
        
        posts_found = []
        
        for endpoint in endpoints_to_check:
            self.log(f"   Vérification: GET {self.base_url}{endpoint}")
            
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=30)
                self.log(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if endpoint == "/posts/generated":
                        posts = data.get("posts", []) or data.get("content", [])
                        self.log(f"   Nombre de posts trouvés: {len(posts)}")
                        
                        # Analyser les posts pour identifier ceux du restaurant
                        restaurant_posts = []
                        for post in posts:
                            post_text = post.get("post_text", "").lower()
                            title = post.get("title", "").lower()
                            if any(keyword in post_text or keyword in title for keyword in 
                                  ["bistrot", "jean", "restaurant", "menu", "chef", "bourguignon", "automne", "noël"]):
                                restaurant_posts.append(post)
                        
                        posts_found.extend(restaurant_posts)
                        self.log(f"   Posts restaurant identifiés: {len(restaurant_posts)}")
                    
                    elif endpoint == "/notes":
                        notes = data.get("notes", [])
                        restaurant_notes = []
                        
                        for note in notes:
                            content = note.get("content", "").lower()
                            description = note.get("description", "").lower()
                            
                            # Chercher les posts du restaurant dans les notes
                            if any(keyword in content or keyword in description for keyword in 
                                  ["bistrot", "jean", "restaurant", "menu", "chef", "bourguignon", "automne", "noël", "facebook", "instagram"]):
                                restaurant_notes.append(note)
                        
                        posts_found.extend(restaurant_notes)
                        self.log(f"   Notes restaurant trouvées: {len(restaurant_notes)}")
                
                elif response.status_code == 404:
                    self.log(f"   Endpoint non disponible: {endpoint}")
                else:
                    self.log(f"   Erreur {response.status_code}: {response.text[:100]}")
                    
            except requests.exceptions.RequestException as e:
                self.log(f"   Erreur de connexion: {str(e)}", "ERROR")
        
        return posts_found
    
    def analyze_posts_content(self, posts):
        """Analyser le contenu des posts trouvés"""
        if not posts:
            self.log("❌ AUCUN POST TROUVÉ", "ERROR")
            return False
        
        self.log(f"📊 ANALYSE DES {len(posts)} POSTS TROUVÉS:")
        
        october_posts = []
        november_posts = []
        
        for i, post in enumerate(posts, 1):
            content = post.get("content", "") or post.get("post_text", "")
            description = post.get("description", "") or post.get("title", "")
            created_at = post.get("created_at", "")
            
            self.log(f"   Post {i}:")
            self.log(f"     Description: {description}")
            self.log(f"     Contenu (extrait): {content[:100]}...")
            self.log(f"     Date: {created_at}")
            
            # Classifier par mois
            if "octobre" in content.lower() or "automne" in content.lower():
                october_posts.append(post)
            elif "novembre" in content.lower() or "noël" in content.lower():
                november_posts.append(post)
        
        self.log(f"📅 RÉPARTITION PAR MOIS:")
        self.log(f"   Posts octobre: {len(october_posts)}")
        self.log(f"   Posts novembre: {len(november_posts)}")
        
        # Vérifier si on a bien les 8 posts attendus (4 octobre + 4 novembre)
        expected_total = 8
        expected_october = 4
        expected_november = 4
        
        success = (len(posts) >= expected_total and 
                  len(october_posts) >= expected_october and 
                  len(november_posts) >= expected_november)
        
        if success:
            self.log("✅ POSTS COMPLETS TROUVÉS (4 octobre + 4 novembre)", "SUCCESS")
        else:
            self.log(f"❌ POSTS INCOMPLETS: {len(posts)}/{expected_total} total, {len(october_posts)}/{expected_october} octobre, {len(november_posts)}/{expected_november} novembre", "ERROR")
        
        return success
    
    def run_verification(self):
        """Exécuter la vérification complète"""
        self.log("🚨 DÉBUT DE LA VÉRIFICATION URGENTE - ENVIRONNEMENT LIVE")
        self.log(f"   URL cible: {self.base_url}")
        self.log(f"   Compte test: {TEST_EMAIL}")
        
        # Étape 1: Authentification
        if not self.authenticate():
            self.log("❌ ÉCHEC CRITIQUE: Impossible de s'authentifier", "ERROR")
            return False
        
        # Étape 2: Vérifier l'analyse de site web
        website_analysis_exists = self.check_website_analysis()
        
        # Étape 3: Vérifier les posts générés
        posts = self.check_generated_posts()
        posts_complete = self.analyze_posts_content(posts)
        
        # Résumé final
        self.log("=" * 60)
        self.log("📋 RÉSUMÉ DE LA VÉRIFICATION LIVE")
        self.log("=" * 60)
        
        if website_analysis_exists:
            self.log("✅ ANALYSE DE SITE WEB: PRÉSENTE sur LIVE")
        else:
            self.log("❌ ANALYSE DE SITE WEB: ABSENTE sur LIVE")
        
        if posts_complete:
            self.log("✅ POSTS RESTAURANT: COMPLETS sur LIVE (8 posts)")
        else:
            self.log(f"❌ POSTS RESTAURANT: INCOMPLETS sur LIVE ({len(posts)} posts trouvés)")
        
        overall_success = website_analysis_exists and posts_complete
        
        if overall_success:
            self.log("🎉 SUCCÈS: Tout le contenu restaurant est présent sur LIVE", "SUCCESS")
        else:
            self.log("🚨 PROBLÈME CRITIQUE: Contenu manquant sur l'environnement LIVE", "ERROR")
        
        self.log("=" * 60)
        
        return overall_success

def main():
    """Point d'entrée principal"""
    print("🔍 VÉRIFICATION URGENTE - Contenu restaurant sur environnement LIVE")
    print("=" * 80)
    
    tester = LiveEnvironmentTester()
    success = tester.run_verification()
    
    if success:
        print("\n✅ CONCLUSION: Le contenu restaurant est bien présent sur l'environnement LIVE")
        sys.exit(0)
    else:
        print("\n❌ CONCLUSION: Le contenu restaurant est ABSENT ou INCOMPLET sur l'environnement LIVE")
        sys.exit(1)

if __name__ == "__main__":
    main()