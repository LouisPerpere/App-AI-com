#!/usr/bin/env python3
"""
VÉRIFICATION NOTES SEPTEMBRE ET GÉNÉRATION POSTS
Test spécifique pour le problème de note de fermeture du 30 septembre non prise en compte

CONTEXTE: L'utilisateur a inséré une note de fermeture du 30 septembre qui ne semble pas 
être prise en compte dans la génération de posts.

TESTS CRITIQUES REQUIS:
1. Vérification note de fermeture 30 septembre
2. Vérification récupération notes dans génération  
3. Génération posts avec nouveau target_month
4. Vérification contenu septembre vs octobre

Credentials: lperpere@yahoo.fr / L@Reunion974!
Backend URL: https://post-validator.preview.emergentagent.com/api
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://post-validator.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class SeptemberNotesTest:
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
    
    def test_1_verify_september_closure_note(self):
        """Test 1: Vérification note de fermeture 30 septembre"""
        print("\n📝 TEST 1: Vérification note de fermeture 30 septembre...")
        
        try:
            # GET /api/notes pour récupérer toutes les notes
            response = self.session.get(f"{BACKEND_URL}/notes", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                notes = data.get("notes", [])
                
                print(f"✅ GET /api/notes réussi - {len(notes)} notes trouvées")
                
                # Chercher spécifiquement une note contenant "30 septembre", "fermeture", ou "fermé"
                closure_notes = []
                september_notes = []
                
                for note in notes:
                    note_content = note.get("content", "").lower()
                    note_description = note.get("description", "").lower()
                    note_text = f"{note_content} {note_description}".lower()
                    
                    # Vérifier si c'est une note de septembre
                    if any(keyword in note_text for keyword in ["septembre", "september", "09"]):
                        september_notes.append(note)
                        print(f"   📅 Note septembre trouvée: {note.get('note_id', 'N/A')}")
                        print(f"      Description: {note.get('description', 'N/A')}")
                        print(f"      Content: {note.get('content', 'N/A')[:100]}...")
                        print(f"      is_monthly_note: {note.get('is_monthly_note', 'N/A')}")
                        print(f"      target_month: {note.get('target_month', 'N/A')}")
                        print(f"      note_month: {note.get('note_month', 'N/A')}")
                        print(f"      note_year: {note.get('note_year', 'N/A')}")
                        print(f"      deleted: {note.get('deleted', 'N/A')}")
                    
                    # Vérifier si c'est une note de fermeture
                    if any(keyword in note_text for keyword in ["30 septembre", "fermeture", "fermé", "ferme"]):
                        closure_notes.append(note)
                        print(f"   🔒 Note de fermeture trouvée: {note.get('note_id', 'N/A')}")
                        print(f"      Description: {note.get('description', 'N/A')}")
                        print(f"      Content: {note.get('content', 'N/A')}")
                        print(f"      is_monthly_note: {note.get('is_monthly_note', 'N/A')}")
                        print(f"      deleted: {note.get('deleted', False)}")
                
                # Résultats du test 1
                print(f"\n📊 RÉSULTATS TEST 1:")
                print(f"   Total notes: {len(notes)}")
                print(f"   Notes septembre: {len(september_notes)}")
                print(f"   Notes de fermeture: {len(closure_notes)}")
                
                if closure_notes:
                    print(f"✅ Note de fermeture trouvée!")
                    for note in closure_notes:
                        is_active = not note.get('deleted', False)
                        print(f"   Note active: {'✅ OUI' if is_active else '❌ NON'}")
                    return True, closure_notes
                else:
                    print(f"❌ Aucune note de fermeture du 30 septembre trouvée")
                    print(f"   Mots-clés recherchés: '30 septembre', 'fermeture', 'fermé', 'ferme'")
                    return False, []
                    
            else:
                print(f"❌ Échec GET /api/notes: {response.status_code}")
                print(f"   Response: {response.text}")
                return False, []
                
        except Exception as e:
            print(f"❌ Erreur Test 1: {str(e)}")
            return False, []
    
    def test_2_verify_notes_collection_logic(self):
        """Test 2: Vérification récupération notes dans génération"""
        print("\n🔍 TEST 2: Vérification récupération notes comme dans posts_generator.py...")
        
        try:
            # Simuler la collecte des notes comme dans posts_generator.py
            response = self.session.get(f"{BACKEND_URL}/notes", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                all_notes = data.get("notes", [])
                
                print(f"✅ Récupération de {len(all_notes)} notes totales")
                
                # Simuler les deux requêtes du posts_generator
                # 1. Always valid notes: is_monthly_note = true, deleted != true
                always_valid_notes = []
                for note in all_notes:
                    if note.get('is_monthly_note', False) and not note.get('deleted', False):
                        always_valid_notes.append(note)
                
                print(f"   📅 Notes toujours valides (is_monthly_note=true): {len(always_valid_notes)}")
                for note in always_valid_notes:
                    print(f"      - {note.get('description', 'N/A')}: {note.get('content', 'N/A')[:50]}...")
                
                # 2. Month-specific notes: target_month = "septembre_2025", deleted != true
                september_specific_notes = []
                for note in all_notes:
                    # Vérifier différents formats possibles pour septembre
                    target_month = note.get('target_month', '')
                    note_month = note.get('note_month')
                    note_year = note.get('note_year')
                    
                    is_september_specific = False
                    
                    # Format target_month
                    if target_month in ["septembre_2025", "september_2025"]:
                        is_september_specific = True
                    
                    # Format note_month/note_year
                    if note_month == 9 and note_year == 2025:
                        is_september_specific = True
                    
                    if is_september_specific and not note.get('deleted', False):
                        september_specific_notes.append(note)
                
                print(f"   📅 Notes spécifiques septembre 2025: {len(september_specific_notes)}")
                for note in september_specific_notes:
                    print(f"      - {note.get('description', 'N/A')}: {note.get('content', 'N/A')[:50]}...")
                    print(f"        target_month: {note.get('target_month', 'N/A')}")
                    print(f"        note_month/year: {note.get('note_month', 'N/A')}/{note.get('note_year', 'N/A')}")
                
                # Vérifier que la note de fermeture apparaît dans l'une des deux listes
                total_relevant_notes = len(always_valid_notes) + len(september_specific_notes)
                
                print(f"\n📊 RÉSULTATS TEST 2:")
                print(f"   Notes toujours valides: {len(always_valid_notes)}")
                print(f"   Notes septembre spécifiques: {len(september_specific_notes)}")
                print(f"   Total notes pertinentes: {total_relevant_notes}")
                
                # Chercher la note de fermeture dans les listes
                closure_in_always_valid = any("fermeture" in note.get('content', '').lower() or 
                                             "fermé" in note.get('content', '').lower() or
                                             "30 septembre" in note.get('content', '').lower()
                                             for note in always_valid_notes)
                
                closure_in_september = any("fermeture" in note.get('content', '').lower() or 
                                         "fermé" in note.get('content', '').lower() or
                                         "30 septembre" in note.get('content', '').lower()
                                         for note in september_specific_notes)
                
                if closure_in_always_valid:
                    print(f"✅ Note de fermeture trouvée dans les notes toujours valides")
                elif closure_in_september:
                    print(f"✅ Note de fermeture trouvée dans les notes septembre spécifiques")
                else:
                    print(f"❌ Note de fermeture NON trouvée dans les listes de génération")
                    print(f"   Cela explique pourquoi elle n'est pas prise en compte!")
                
                return total_relevant_notes > 0, {
                    "always_valid": always_valid_notes,
                    "september_specific": september_specific_notes,
                    "closure_found": closure_in_always_valid or closure_in_september
                }
                
            else:
                print(f"❌ Échec récupération notes: {response.status_code}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Erreur Test 2: {str(e)}")
            return False, {}
    
    def test_3_generate_posts_september(self):
        """Test 3: Génération posts avec nouveau target_month"""
        print("\n🚀 TEST 3: Génération posts avec target_month septembre_2025...")
        
        try:
            # POST /api/posts/generate avec target_month="septembre_2025"
            print(f"   Appel POST /api/posts/generate avec target_month='septembre_2025'")
            
            response = self.session.post(
                f"{BACKEND_URL}/posts/generate",
                params={"target_month": "septembre_2025"},
                timeout=120  # Timeout étendu pour la génération IA
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Génération de posts réussie")
                print(f"   Posts générés: {data.get('posts_count', 0)}")
                print(f"   Stratégie: {data.get('strategy', {})}")
                print(f"   Sources utilisées: {data.get('sources_used', {})}")
                
                # Vérifier que le mois cible est bien septembre_2025
                sources_used = data.get('sources_used', {})
                target_month_used = data.get('target_month', 'N/A')
                
                print(f"\n📊 ANALYSE DES SOURCES:")
                print(f"   Target month utilisé: {target_month_used}")
                
                if 'notes' in sources_used:
                    notes_info = sources_used['notes']
                    print(f"   Notes utilisées: {notes_info}")
                
                if 'content' in sources_used:
                    content_info = sources_used['content']
                    print(f"   Contenu utilisé: {content_info}")
                
                # Vérifier si les notes de fermeture sont mentionnées
                strategy_text = str(data.get('strategy', {})).lower()
                sources_text = str(sources_used).lower()
                
                if any(keyword in strategy_text or keyword in sources_text 
                       for keyword in ["fermeture", "fermé", "30 septembre"]):
                    print(f"✅ Note de fermeture détectée dans les sources utilisées!")
                else:
                    print(f"❌ Note de fermeture NON détectée dans les sources utilisées")
                
                return True, data
                
            else:
                print(f"❌ Échec génération posts: {response.status_code}")
                print(f"   Response: {response.text}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Erreur Test 3: {str(e)}")
            return False, {}
    
    def test_4_verify_september_vs_october_content(self):
        """Test 4: Vérification contenu septembre vs octobre"""
        print("\n📅 TEST 4: Vérification contenu septembre vs octobre...")
        
        try:
            # GET /api/content/pending pour voir le contenu disponible
            response = self.session.get(
                f"{BACKEND_URL}/content/pending",
                params={"limit": 100},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                
                print(f"✅ Récupération de {len(content_items)} éléments de contenu")
                
                # Filtrer par mois
                september_content = []
                october_content = []
                other_content = []
                
                for item in content_items:
                    attributed_month = item.get("attributed_month", "")
                    
                    if "septembre" in attributed_month.lower() or "september" in attributed_month.lower():
                        september_content.append(item)
                    elif "octobre" in attributed_month.lower() or "october" in attributed_month.lower():
                        october_content.append(item)
                    else:
                        other_content.append(item)
                
                print(f"\n📊 RÉPARTITION DU CONTENU PAR MOIS:")
                print(f"   Contenu septembre: {len(september_content)} éléments")
                print(f"   Contenu octobre: {len(october_content)} éléments")
                print(f"   Autre contenu: {len(other_content)} éléments")
                
                # Afficher quelques exemples de contenu septembre
                if september_content:
                    print(f"\n📝 EXEMPLES CONTENU SEPTEMBRE:")
                    for i, item in enumerate(september_content[:3], 1):
                        print(f"   {i}. {item.get('filename', 'N/A')}")
                        print(f"      Title: {item.get('title', 'N/A')}")
                        print(f"      Context: {item.get('context', 'N/A')[:50]}...")
                        print(f"      Attributed month: {item.get('attributed_month', 'N/A')}")
                
                # Vérifier qu'il y a du contenu disponible pour septembre
                if len(september_content) > 0:
                    print(f"✅ Contenu disponible pour septembre: {len(september_content)} éléments")
                    return True, {
                        "september_count": len(september_content),
                        "october_count": len(october_content),
                        "september_content": september_content[:5]  # Premiers 5 éléments
                    }
                else:
                    print(f"❌ Aucun contenu trouvé pour septembre")
                    print(f"   Cela pourrait expliquer pourquoi la génération utilise octobre par défaut")
                    return False, {
                        "september_count": 0,
                        "october_count": len(october_content)
                    }
                
            else:
                print(f"❌ Échec récupération contenu: {response.status_code}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Erreur Test 4: {str(e)}")
            return False, {}
    
    def run_comprehensive_test(self):
        """Exécuter tous les tests de diagnostic"""
        print("=" * 80)
        print("🔍 VÉRIFICATION NOTES SEPTEMBRE ET GÉNÉRATION POSTS")
        print("=" * 80)
        print("CONTEXTE: Note de fermeture du 30 septembre non prise en compte")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Credentials: {TEST_EMAIL} / {TEST_PASSWORD}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Authentification
        if not self.authenticate():
            print("\n❌ TESTS ÉCHOUÉS: Impossible de s'authentifier")
            return False
        
        # Test 1: Vérification note de fermeture
        test1_success, closure_notes = self.test_1_verify_september_closure_note()
        
        # Test 2: Vérification logique de récupération des notes
        test2_success, notes_analysis = self.test_2_verify_notes_collection_logic()
        
        # Test 3: Génération de posts
        test3_success, generation_result = self.test_3_generate_posts_september()
        
        # Test 4: Vérification contenu septembre vs octobre
        test4_success, content_analysis = self.test_4_verify_september_vs_october_content()
        
        # Résumé final
        print("\n" + "=" * 80)
        print("📋 RÉSUMÉ DIAGNOSTIC COMPLET")
        print("=" * 80)
        
        print(f"Test 1 - Note fermeture 30 septembre: {'✅ TROUVÉE' if test1_success else '❌ NON TROUVÉE'}")
        if test1_success and closure_notes:
            print(f"   Nombre de notes de fermeture: {len(closure_notes)}")
            for note in closure_notes:
                print(f"   - {note.get('description', 'N/A')}: Active = {not note.get('deleted', False)}")
        
        print(f"Test 2 - Récupération notes génération: {'✅ OK' if test2_success else '❌ PROBLÈME'}")
        if test2_success and notes_analysis:
            print(f"   Notes toujours valides: {len(notes_analysis.get('always_valid', []))}")
            print(f"   Notes septembre spécifiques: {len(notes_analysis.get('september_specific', []))}")
            print(f"   Note fermeture dans génération: {'✅ OUI' if notes_analysis.get('closure_found', False) else '❌ NON'}")
        
        print(f"Test 3 - Génération posts septembre: {'✅ RÉUSSIE' if test3_success else '❌ ÉCHOUÉE'}")
        if test3_success and generation_result:
            print(f"   Posts générés: {generation_result.get('posts_count', 0)}")
            sources = generation_result.get('sources_used', {})
            if 'notes' in sources:
                print(f"   Notes utilisées: {sources['notes']}")
        
        print(f"Test 4 - Contenu septembre disponible: {'✅ OUI' if test4_success else '❌ NON'}")
        if content_analysis:
            print(f"   Éléments septembre: {content_analysis.get('september_count', 0)}")
            print(f"   Éléments octobre: {content_analysis.get('october_count', 0)}")
        
        # Diagnostic final
        print("\n" + "=" * 80)
        print("🎯 DIAGNOSTIC FINAL")
        print("=" * 80)
        
        if test1_success and test2_success and notes_analysis.get('closure_found', False):
            print("✅ PROBLÈME RÉSOLU: La note de fermeture est correctement configurée et récupérée")
            print("   La note devrait maintenant apparaître dans la génération de posts")
        elif test1_success and not notes_analysis.get('closure_found', False):
            print("❌ PROBLÈME IDENTIFIÉ: Note de fermeture existe mais n'est pas récupérée par la génération")
            print("   CAUSE PROBABLE: Problème de configuration des champs is_monthly_note ou target_month")
            print("   SOLUTION: Vérifier et corriger les champs de la note de fermeture")
        elif not test1_success:
            print("❌ PROBLÈME IDENTIFIÉ: Note de fermeture du 30 septembre introuvable")
            print("   CAUSE PROBABLE: Note supprimée, mal configurée, ou mots-clés différents")
            print("   SOLUTION: Recréer la note avec les bons mots-clés et configuration")
        
        if not test4_success:
            print("⚠️  ATTENTION: Peu de contenu disponible pour septembre")
            print("   Cela pourrait affecter la qualité de la génération de posts")
        
        overall_success = test1_success and test2_success and test3_success
        return overall_success

def main():
    """Point d'entrée principal"""
    tester = SeptemberNotesTest()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 DIAGNOSTIC TERMINÉ AVEC SUCCÈS")
        sys.exit(0)
    else:
        print("\n💥 DIAGNOSTIC RÉVÈLE DES PROBLÈMES À CORRIGER")
        sys.exit(1)

if __name__ == "__main__":
    main()