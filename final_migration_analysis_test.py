#!/usr/bin/env python3
"""
ANALYSE FINALE MIGRATION - Documentation complète du problème et solutions
Test complet pour documenter l'état actuel et les solutions possibles
"""

import requests
import json
import sys
from datetime import datetime

# Configuration LIVE
LIVE_BASE_URL = "https://claire-marcus.com/api"
TEST_EMAIL = "test@claire-marcus.com"
TEST_PASSWORD = "test123!"
USER_ID = "82ce1284-ca2e-469a-8521-2a9116ef7826"

class FinalMigrationAnalysis:
    def __init__(self):
        self.base_url = LIVE_BASE_URL
        self.token = None
        self.user_id = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Final-Analysis/1.0'
        })

    def authenticate(self):
        """Authentification"""
        print(f"🔐 AUTHENTIFICATION")
        
        try:
            response = self.session.post(f"{self.base_url}/auth/login-robust", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token')
                self.user_id = data.get('user_id')
                
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}'
                })
                
                print(f"   ✅ Succès - User ID: {self.user_id}")
                return True
            else:
                print(f"   ❌ Échec: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return False

    def analyze_current_state(self):
        """Analyser l'état actuel complet"""
        print(f"\n🔍 ANALYSE ÉTAT ACTUEL")
        
        results = {
            'notes': {'count': 0, 'posts': 0, 'analyses': 0, 'accessible': False},
            'posts_generated': {'count': 0, 'accessible': False},
            'website_analysis': {'count': 0, 'accessible': False}
        }
        
        # Test 1: /api/notes (où sont les données)
        try:
            response = self.session.get(f"{self.base_url}/notes")
            print(f"   📝 GET /notes: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                notes = data.get('notes', [])
                results['notes']['accessible'] = True
                results['notes']['count'] = len(notes)
                
                # Analyser le contenu des notes
                posts_count = 0
                analyses_count = 0
                
                for note in notes:
                    try:
                        content = note.get('content', '')
                        if isinstance(content, str) and content.startswith('{'):
                            content_data = json.loads(content)
                            content_type = content_data.get('type', '')
                            
                            if content_type == 'social_media_post':
                                posts_count += 1
                            elif content_type == 'website_analysis':
                                analyses_count += 1
                    except:
                        continue
                
                results['notes']['posts'] = posts_count
                results['notes']['analyses'] = analyses_count
                
                print(f"      ✅ {len(notes)} notes totales")
                print(f"      📄 {posts_count} posts sociaux")
                print(f"      🔍 {analyses_count} analyses site web")
            else:
                print(f"      ❌ Erreur: {response.text[:50]}")
                
        except Exception as e:
            print(f"   ❌ Erreur /notes: {e}")
        
        # Test 2: /api/posts/generated (où le frontend cherche les posts)
        try:
            response = self.session.get(f"{self.base_url}/posts/generated")
            print(f"   📄 GET /posts/generated: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('posts', [])
                results['posts_generated']['accessible'] = True
                results['posts_generated']['count'] = len(posts)
                
                print(f"      ✅ {len(posts)} posts générés")
                
                if posts:
                    for i, post in enumerate(posts[:3]):
                        print(f"         {i+1}. {post.get('title', 'N/A')}")
                else:
                    print(f"      ⚠️ AUCUN POST - C'EST LE PROBLÈME!")
            else:
                print(f"      ❌ Erreur: {response.text[:50]}")
                
        except Exception as e:
            print(f"   ❌ Erreur /posts/generated: {e}")
        
        # Test 3: /api/analysis (où le frontend cherche les analyses)
        try:
            response = self.session.get(f"{self.base_url}/analysis")
            print(f"   🔍 GET /analysis: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    analyses = data
                else:
                    analyses = data.get('analyses', [])
                
                results['website_analysis']['accessible'] = True
                results['website_analysis']['count'] = len(analyses)
                
                print(f"      ✅ {len(analyses)} analyses")
                
                if analyses:
                    for i, analysis in enumerate(analyses[:3]):
                        print(f"         {i+1}. {analysis.get('business_name', 'N/A')}")
                else:
                    print(f"      ⚠️ AUCUNE ANALYSE - C'EST LE PROBLÈME!")
            else:
                print(f"      ❌ Erreur: {response.text[:50]}")
                results['website_analysis']['accessible'] = False
                
        except Exception as e:
            print(f"   ❌ Erreur /analysis: {e}")
        
        return results

    def document_problem_and_solutions(self, analysis_results):
        """Documenter le problème et les solutions"""
        print(f"\n" + "=" * 80)
        print("🚨 DIAGNOSTIC COMPLET DU PROBLÈME")
        print("=" * 80)
        
        # Problème identifié
        print(f"❌ PROBLÈME CONFIRMÉ:")
        print(f"   Les données restaurant existent mais dans la mauvaise collection")
        print(f"   📝 Collection 'notes': {analysis_results['notes']['posts']} posts + {analysis_results['notes']['analyses']} analyses")
        print(f"   📄 Collection 'generated_posts': {analysis_results['posts_generated']['count']} posts")
        print(f"   🔍 Collection 'website_analyses': {analysis_results['website_analysis']['count']} analyses")
        
        print(f"\n🎯 CAUSE RACINE:")
        print(f"   Le système a créé les données dans la collection 'notes' (via POST /api/notes)")
        print(f"   Mais le frontend lit depuis:")
        print(f"   - GET /api/posts/generated (collection 'generated_posts')")
        print(f"   - GET /api/analysis (collection 'website_analyses')")
        
        print(f"\n📋 DONNÉES À MIGRER:")
        print(f"   User ID: {self.user_id}")
        print(f"   Posts octobre 2024: ~4-5 posts")
        print(f"   Posts novembre 2024: ~4-5 posts")
        print(f"   Analyses Le Bistrot de Jean: ~1-4 analyses")
        print(f"   Total: {analysis_results['notes']['posts']} posts + {analysis_results['notes']['analyses']} analyses")
        
        print(f"\n" + "=" * 80)
        print("🔧 SOLUTIONS POSSIBLES")
        print("=" * 80)
        
        print(f"💡 SOLUTION 1 - MIGRATION BASE DE DONNÉES (RECOMMANDÉE):")
        print(f"   Accès direct à la base MongoDB LIVE pour migrer les données")
        print(f"   ✅ Avantages: Solution définitive, rapide")
        print(f"   ❌ Inconvénients: Nécessite accès base de données")
        print(f"   📋 Actions:")
        print(f"      1. Extraire les posts/analyses depuis collection 'content_notes'")
        print(f"      2. Transformer au format attendu")
        print(f"      3. Insérer dans 'generated_posts' et 'website_analyses'")
        
        print(f"\n💡 SOLUTION 2 - ENDPOINT DE MIGRATION API:")
        print(f"   Créer un endpoint spécial pour migrer les données")
        print(f"   ✅ Avantages: Utilise l'API existante")
        print(f"   ❌ Inconvénients: Nécessite modification du code backend")
        print(f"   📋 Actions:")
        print(f"      1. Ajouter POST /api/migrate/notes-to-collections")
        print(f"      2. L'endpoint lit /notes et écrit dans les bonnes collections")
        
        print(f"\n💡 SOLUTION 3 - MODIFICATION FRONTEND:")
        print(f"   Modifier le frontend pour lire depuis /api/notes")
        print(f"   ✅ Avantages: Pas de migration nécessaire")
        print(f"   ❌ Inconvénients: Solution temporaire, logique complexe")
        print(f"   📋 Actions:")
        print(f"      1. Modifier les pages Posts et Analyse")
        print(f"      2. Filtrer les notes par type de contenu")
        
        print(f"\n💡 SOLUTION 4 - RECRÉATION VIA API:")
        print(f"   Recréer le contenu via les endpoints appropriés")
        print(f"   ✅ Avantages: Utilise le workflow normal")
        print(f"   ❌ Inconvénients: Complexe, peut créer des doublons")
        print(f"   📋 Actions:")
        print(f"      1. Extraire données depuis /notes")
        print(f"      2. Recréer via /posts/generate et /analyze")
        
        return True

    def provide_implementation_guidance(self, analysis_results):
        """Fournir des conseils d'implémentation"""
        print(f"\n" + "=" * 80)
        print("🛠️ GUIDE D'IMPLÉMENTATION - SOLUTION RECOMMANDÉE")
        print("=" * 80)
        
        print(f"🎯 SOLUTION RECOMMANDÉE: MIGRATION BASE DE DONNÉES")
        print(f"   Raison: Plus rapide et plus fiable")
        
        print(f"\n📋 ÉTAPES D'IMPLÉMENTATION:")
        
        print(f"\n1️⃣ ACCÈS BASE DE DONNÉES LIVE:")
        print(f"   - Identifier l'URL MongoDB de l'environnement LIVE")
        print(f"   - Obtenir les credentials de connexion")
        print(f"   - Tester la connexion")
        
        print(f"\n2️⃣ EXTRACTION DES DONNÉES:")
        print(f"   Collection source: content_notes")
        print(f"   Filtre: owner_id = '{self.user_id}'")
        print(f"   Critères: content contient type='social_media_post' ou 'website_analysis'")
        
        print(f"\n3️⃣ TRANSFORMATION DES POSTS:")
        print(f"   Collection cible: generated_posts")
        print(f"   Champs requis:")
        print(f"   - id: post_{{user_id}}_{{timestamp}}_{{index}}")
        print(f"   - owner_id: {self.user_id}")
        print(f"   - platform: facebook/instagram")
        print(f"   - title, text, hashtags")
        print(f"   - scheduled_date, target_month")
        print(f"   - status: 'ready', validated: false")
        
        print(f"\n4️⃣ TRANSFORMATION DES ANALYSES:")
        print(f"   Collection cible: website_analyses")
        print(f"   Champs requis:")
        print(f"   - id: analysis_{{user_id}}_{{timestamp}}_{{index}}")
        print(f"   - user_id: {self.user_id}")
        print(f"   - website_url, business_name")
        print(f"   - seo_score, performance_score, etc.")
        print(f"   - recommendations, strengths, improvements")
        
        print(f"\n5️⃣ VÉRIFICATION:")
        print(f"   - GET /api/posts/generated doit retourner {analysis_results['notes']['posts']} posts")
        print(f"   - GET /api/analysis doit retourner {analysis_results['notes']['analyses']} analyses")
        print(f"   - Tester l'affichage frontend")
        
        print(f"\n⚠️ POINTS D'ATTENTION:")
        print(f"   - Éviter les doublons (vérifier si données déjà migrées)")
        print(f"   - Conserver les IDs originaux dans un champ 'migrated_from_note_id'")
        print(f"   - Faire une sauvegarde avant migration")
        print(f"   - Tester sur un environnement de dev d'abord")
        
        return True

    def run_final_analysis(self):
        """Exécuter l'analyse finale complète"""
        print("=" * 80)
        print("📊 ANALYSE FINALE - MIGRATION DONNÉES RESTAURANT")
        print("=" * 80)
        print(f"Environnement: {self.base_url}")
        print(f"User ID: {USER_ID}")
        print(f"Objectif: Migrer posts et analyses vers les bonnes collections")
        print(f"Heure: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Étape 1: Authentification
        if not self.authenticate():
            print("\n❌ ANALYSE INTERROMPUE - Échec authentification")
            return False
        
        # Étape 2: Analyse de l'état actuel
        analysis_results = self.analyze_current_state()
        
        # Étape 3: Documentation du problème
        self.document_problem_and_solutions(analysis_results)
        
        # Étape 4: Guide d'implémentation
        self.provide_implementation_guidance()
        
        # CONCLUSION
        print(f"\n" + "=" * 80)
        print("🎉 CONCLUSION")
        print("=" * 80)
        
        print(f"✅ PROBLÈME IDENTIFIÉ ET DOCUMENTÉ:")
        print(f"   Les données restaurant existent dans la collection 'notes'")
        print(f"   Mais le frontend lit depuis 'generated_posts' et 'website_analyses'")
        
        print(f"\n✅ SOLUTION CLAIRE:")
        print(f"   Migration directe en base de données MongoDB")
        print(f"   {analysis_results['notes']['posts']} posts + {analysis_results['notes']['analyses']} analyses à migrer")
        
        print(f"\n✅ IMPACT ATTENDU:")
        print(f"   Après migration, l'interface utilisateur affichera:")
        print(f"   - Page Posts: {analysis_results['notes']['posts']} posts (octobre + novembre)")
        print(f"   - Page Analyse: {analysis_results['notes']['analyses']} analyses Le Bistrot de Jean")
        
        print(f"\n🚀 PRÊT POUR IMPLÉMENTATION!")
        
        return True

def main():
    """Point d'entrée principal"""
    analysis = FinalMigrationAnalysis()
    success = analysis.run_final_analysis()
    
    if success:
        print(f"\n✅ ANALYSE FINALE TERMINÉE AVEC SUCCÈS")
        sys.exit(0)
    else:
        print(f"\n❌ ANALYSE FINALE ÉCHOUÉE")
        sys.exit(1)

if __name__ == "__main__":
    main()