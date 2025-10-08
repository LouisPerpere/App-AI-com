#!/usr/bin/env python3
"""
ANALYSE DÉTAILLÉE - Contenu restaurant sur environnement LIVE
Analyser précisément ce qui est présent vs ce qui est attendu
"""

import requests
import json
import sys
from datetime import datetime

# CONFIGURATION CRITIQUE - ENVIRONNEMENT LIVE UNIQUEMENT
LIVE_BASE_URL = "https://claire-marcus.com/api"
TEST_EMAIL = "test@claire-marcus.com"
TEST_PASSWORD = "test123!"

class DetailedRestaurantAnalyzer:
    def __init__(self):
        self.base_url = LIVE_BASE_URL
        self.token = None
        self.user_id = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Claire-Marcus-Detailed-Analyzer/1.0'
        })
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def authenticate(self):
        """Authentification sur l'environnement LIVE"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login-robust",
                json={
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                if self.token and self.user_id:
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.token}'
                    })
                    self.log(f"✅ Authentification réussie - User ID: {self.user_id}")
                    return True
            
            self.log("❌ Échec d'authentification", "ERROR")
            return False
                
        except Exception as e:
            self.log(f"❌ Erreur d'authentification: {str(e)}", "ERROR")
            return False
    
    def analyze_website_analysis(self):
        """Analyser l'analyse de site web en détail"""
        self.log("🔍 ANALYSE DÉTAILLÉE - Analyse de site web")
        
        try:
            response = self.session.get(f"{self.base_url}/notes", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                notes = data.get("notes", [])
                
                website_analyses = []
                for note in notes:
                    content = note.get("content", "").lower()
                    description = note.get("description", "").lower()
                    
                    if ("lebistrotdejean" in content or "lebistrotdejean" in description or
                        ("analyse" in description and "site" in description)):
                        website_analyses.append(note)
                
                self.log(f"📊 ANALYSES DE SITE WEB TROUVÉES: {len(website_analyses)}")
                
                for i, analysis in enumerate(website_analyses, 1):
                    self.log(f"   Analyse {i}:")
                    self.log(f"     Description: {analysis.get('description', 'N/A')}")
                    self.log(f"     Date: {analysis.get('created_at', 'N/A')}")
                    
                    content = analysis.get('content', '')
                    if 'seo' in content.lower():
                        # Extraire le score SEO si présent
                        import re
                        seo_match = re.search(r'seo[:\s]*(\d+)', content.lower())
                        if seo_match:
                            self.log(f"     Score SEO détecté: {seo_match.group(1)}/100")
                    
                    if len(content) > 200:
                        self.log(f"     Contenu (extrait): {content[:200]}...")
                    else:
                        self.log(f"     Contenu complet: {content}")
                
                return len(website_analyses) > 0
            
            return False
            
        except Exception as e:
            self.log(f"❌ Erreur analyse site web: {str(e)}", "ERROR")
            return False
    
    def analyze_restaurant_posts(self):
        """Analyser les posts restaurant en détail"""
        self.log("📝 ANALYSE DÉTAILLÉE - Posts restaurant")
        
        try:
            response = self.session.get(f"{self.base_url}/notes", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                notes = data.get("notes", [])
                
                restaurant_posts = []
                for note in notes:
                    content = note.get("content", "").lower()
                    description = note.get("description", "").lower()
                    
                    # Identifier les posts restaurant (exclure les analyses de site)
                    if (any(keyword in content or keyword in description for keyword in 
                           ["post octobre", "post novembre", "menu", "chef jean", "bourguignon", "ambiance", "noël"]) and
                        "analyse" not in description):
                        restaurant_posts.append(note)
                
                self.log(f"📊 POSTS RESTAURANT TROUVÉS: {len(restaurant_posts)}")
                
                # Classifier par mois
                october_posts = []
                november_posts = []
                
                for post in restaurant_posts:
                    description = post.get("description", "").lower()
                    content = post.get("content", "").lower()
                    
                    if "octobre" in description or "octobre" in content:
                        october_posts.append(post)
                    elif "novembre" in description or "novembre" in content:
                        november_posts.append(post)
                
                self.log(f"📅 RÉPARTITION PAR MOIS:")
                self.log(f"   Posts Octobre 2024: {len(october_posts)}")
                self.log(f"   Posts Novembre 2024: {len(november_posts)}")
                
                # Analyser les posts d'octobre
                self.log("🍂 POSTS OCTOBRE 2024:")
                expected_october = [
                    "menu d'automne",
                    "chef jean",
                    "ambiance cosy", 
                    "bœuf bourguignon"
                ]
                
                found_october_themes = []
                for i, post in enumerate(october_posts, 1):
                    description = post.get("description", "")
                    content = post.get("content", "")
                    
                    self.log(f"   Post Octobre {i}: {description}")
                    
                    # Identifier le thème
                    theme = "autre"
                    if "menu" in description.lower() or "menu" in content.lower():
                        theme = "menu d'automne"
                    elif "chef" in description.lower() or "jean" in description.lower():
                        theme = "chef jean"
                    elif "ambiance" in description.lower() or "cosy" in description.lower():
                        theme = "ambiance cosy"
                    elif "bourguignon" in description.lower() or "bourguignon" in content.lower():
                        theme = "bœuf bourguignon"
                    
                    found_october_themes.append(theme)
                    self.log(f"     Thème identifié: {theme}")
                
                # Analyser les posts de novembre
                self.log("🎄 POSTS NOVEMBRE 2024:")
                expected_november = [
                    "menu de noël",
                    "vins d'automne",
                    "coulisses cuisine",
                    "soirée dégustation"
                ]
                
                found_november_themes = []
                for i, post in enumerate(november_posts, 1):
                    description = post.get("description", "")
                    content = post.get("content", "")
                    
                    self.log(f"   Post Novembre {i}: {description}")
                    
                    # Identifier le thème
                    theme = "autre"
                    if "noël" in description.lower() or "noël" in content.lower():
                        theme = "menu de noël"
                    elif "vin" in description.lower() or "vin" in content.lower():
                        theme = "vins d'automne"
                    elif "coulisse" in description.lower() or "cuisine" in description.lower():
                        theme = "coulisses cuisine"
                    elif "dégustation" in description.lower() or "événement" in description.lower():
                        theme = "soirée dégustation"
                    
                    found_november_themes.append(theme)
                    self.log(f"     Thème identifié: {theme}")
                
                # Vérification de complétude
                self.log("✅ VÉRIFICATION DE COMPLÉTUDE:")
                
                october_complete = len(october_posts) >= 4
                november_complete = len(november_posts) >= 4
                
                self.log(f"   Octobre: {len(october_posts)}/4 posts ({'✅ COMPLET' if october_complete else '❌ INCOMPLET'})")
                self.log(f"   Novembre: {len(november_posts)}/4 posts ({'✅ COMPLET' if november_complete else '❌ INCOMPLET'})")
                
                # Identifier les posts manquants
                if not november_complete:
                    self.log("🔍 POSTS NOVEMBRE MANQUANTS:")
                    for expected_theme in expected_november:
                        if expected_theme not in found_november_themes:
                            self.log(f"   ❌ Manque: {expected_theme}")
                
                return {
                    'total_posts': len(restaurant_posts),
                    'october_posts': len(october_posts),
                    'november_posts': len(november_posts),
                    'october_complete': october_complete,
                    'november_complete': november_complete,
                    'overall_complete': october_complete and november_complete
                }
            
            return None
            
        except Exception as e:
            self.log(f"❌ Erreur analyse posts: {str(e)}", "ERROR")
            return None
    
    def check_business_profile(self):
        """Vérifier le profil business restaurant"""
        self.log("🏪 ANALYSE PROFIL BUSINESS")
        
        try:
            response = self.session.get(f"{self.base_url}/business-profile", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                business_name = data.get("business_name", "")
                website_url = data.get("website_url", "")
                industry = data.get("industry", "")
                
                self.log(f"   Nom du business: {business_name}")
                self.log(f"   Site web: {website_url}")
                self.log(f"   Industrie: {industry}")
                
                is_restaurant = ("bistrot" in business_name.lower() or 
                               "lebistrotdejean" in website_url or
                               "restaurant" in industry.lower())
                
                if is_restaurant:
                    self.log("✅ PROFIL RESTAURANT CONFIRMÉ")
                    return True
                else:
                    self.log("❌ PROFIL RESTAURANT NON CONFIRMÉ")
                    return False
            
            return False
            
        except Exception as e:
            self.log(f"❌ Erreur profil business: {str(e)}", "ERROR")
            return False
    
    def run_detailed_analysis(self):
        """Exécuter l'analyse détaillée complète"""
        self.log("🔍 DÉBUT DE L'ANALYSE DÉTAILLÉE - ENVIRONNEMENT LIVE")
        self.log(f"   URL: {self.base_url}")
        self.log(f"   Compte: {TEST_EMAIL}")
        
        # Authentification
        if not self.authenticate():
            return False
        
        # Analyses détaillées
        website_analysis_ok = self.analyze_website_analysis()
        business_profile_ok = self.check_business_profile()
        posts_analysis = self.analyze_restaurant_posts()
        
        # Résumé final
        self.log("=" * 80)
        self.log("📋 RÉSUMÉ DÉTAILLÉ DE L'ANALYSE LIVE")
        self.log("=" * 80)
        
        self.log(f"✅ Analyse de site web: {'PRÉSENTE' if website_analysis_ok else 'ABSENTE'}")
        self.log(f"✅ Profil business restaurant: {'CONFIRMÉ' if business_profile_ok else 'NON CONFIRMÉ'}")
        
        if posts_analysis:
            self.log(f"📝 Posts restaurant: {posts_analysis['total_posts']} trouvés")
            self.log(f"   - Octobre 2024: {posts_analysis['october_posts']}/4 ({'✅' if posts_analysis['october_complete'] else '❌'})")
            self.log(f"   - Novembre 2024: {posts_analysis['november_posts']}/4 ({'✅' if posts_analysis['november_complete'] else '❌'})")
            
            overall_success = (website_analysis_ok and 
                             business_profile_ok and 
                             posts_analysis['overall_complete'])
        else:
            self.log("❌ Impossible d'analyser les posts")
            overall_success = False
        
        self.log("=" * 80)
        
        if overall_success:
            self.log("🎉 CONCLUSION: TOUT LE CONTENU RESTAURANT EST PRÉSENT ET COMPLET")
        else:
            self.log("🚨 CONCLUSION: CONTENU RESTAURANT INCOMPLET OU MANQUANT")
        
        return overall_success

def main():
    """Point d'entrée principal"""
    print("🔍 ANALYSE DÉTAILLÉE - Contenu restaurant sur environnement LIVE")
    print("=" * 80)
    
    analyzer = DetailedRestaurantAnalyzer()
    success = analyzer.run_detailed_analysis()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()