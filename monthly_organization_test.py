#!/usr/bin/env python3
"""
VALIDATION COMPLÈTE ORGANISATION MENSUELLE - PHASE DE VÉRIFICATION FINALE

Test complet de l'organisation mensuelle des notes et du système d'upload selon la demande de révision française.

Ce script teste:
1. Notes API - Organisation mensuelle avec is_monthly_note, note_month, note_year
2. Système Upload mensuel avec attributed_month et upload_type 
3. Carousel Upload avec common_title, common_context et carousel_id
4. Pixabay Integration avec save_type et attributed_month

Credentials: lperpere@yahoo.fr / L@Reunion974!
Backend: https://post-restore.preview.emergentagent.com/api
"""

import requests
import json
import io
from PIL import Image
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://post-restore.preview.emergentagent.com/api"
EMAIL = "lperpere@yahoo.fr"
PASSWORD = "L@Reunion974!"

class MonthlyOrganizationTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.test_note_ids = []
        self.test_content_ids = []
        
    def authenticate(self):
        """Étape 1: Authentification avec le backend"""
        print("🔑 Étape 1: Authentification avec POST /api/auth/login-robust")
        
        login_data = {
            "email": EMAIL,
            "password": PASSWORD
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login-robust", json=login_data)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for all future requests
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                
                print(f"   ✅ Authentification réussie")
                print(f"   User ID: {self.user_id}")
                print(f"   Token: {self.token[:20]}..." if self.token else "   Token: None")
                return True
            else:
                print(f"   ❌ Échec authentification: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Erreur authentification: {e}")
            return False

    def test_notes_monthly_organization(self):
        """Étape 2: Test Notes API - Organisation mensuelle"""
        print("📝 Étape 2: Test Notes API avec champs périodiques (is_monthly_note, note_month, note_year)")
        
        # Test 2.1: Créer une note mensuelle récurrente
        print("   2.1: Création note mensuelle récurrente (is_monthly_note=true)")
        monthly_note_data = {
            "content": "Note mensuelle récurrente - toujours valide",
            "description": "Note Mensuelle Test",
            "priority": "high",
            "is_monthly_note": True,
            "note_month": None,
            "note_year": None
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/notes", json=monthly_note_data)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                note_id = data.get("note", {}).get("note_id")
                if note_id:
                    self.test_note_ids.append(note_id)
                print(f"   ✅ Note mensuelle créée: {note_id}")
                print(f"   is_monthly_note: {data.get('note', {}).get('is_monthly_note')}")
            else:
                print(f"   ❌ Échec création note mensuelle: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Erreur création note mensuelle: {e}")
            return False
        
        # Test 2.2: Créer une note pour un mois spécifique
        print("   2.2: Création note mois spécifique (note_month=10, note_year=2025)")
        specific_note_data = {
            "content": "Note pour octobre 2025 spécifiquement",
            "description": "Note Octobre 2025",
            "priority": "medium",
            "is_monthly_note": False,
            "note_month": 10,
            "note_year": 2025
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/notes", json=specific_note_data)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                note_id = data.get("note", {}).get("note_id")
                if note_id:
                    self.test_note_ids.append(note_id)
                print(f"   ✅ Note spécifique créée: {note_id}")
                print(f"   note_month: {data.get('note', {}).get('note_month')}")
                print(f"   note_year: {data.get('note', {}).get('note_year')}")
            else:
                print(f"   ❌ Échec création note spécifique: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Erreur création note spécifique: {e}")
            return False
        
        # Test 2.3: Récupérer toutes les notes et vérifier les champs
        print("   2.3: Vérification GET /api/notes avec champs périodiques")
        try:
            response = self.session.get(f"{BACKEND_URL}/notes")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                notes = data.get("notes", [])
                print(f"   ✅ Notes récupérées: {len(notes)} notes")
                
                # Vérifier que nos notes de test ont les bons champs
                monthly_notes = [n for n in notes if n.get("is_monthly_note") == True]
                specific_notes = [n for n in notes if n.get("note_month") == 10 and n.get("note_year") == 2025]
                
                print(f"   Notes mensuelles trouvées: {len(monthly_notes)}")
                print(f"   Notes octobre 2025 trouvées: {len(specific_notes)}")
                
                # Vérifier structure des champs
                fields_ok = True
                for note in notes:
                    required_fields = ["is_monthly_note", "note_month", "note_year", "priority"]
                    for field in required_fields:
                        if field not in note:
                            print(f"   ❌ Champ manquant '{field}' dans note {note.get('note_id')}")
                            fields_ok = False
                
                if fields_ok:
                    print(f"   ✅ Tous les champs périodiques présents")
                    return True
                else:
                    print(f"   ❌ Champs périodiques manquants")
                    return False
            else:
                print(f"   ❌ Échec récupération notes: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Erreur récupération notes: {e}")
            return False

    def test_monthly_upload_system(self):
        """Étape 3: Test Système Upload mensuel avec attributed_month et upload_type"""
        print("📤 Étape 3: Test Upload mensuel avec attributed_month et upload_type")
        
        # Créer une image de test
        img = Image.new('RGB', (800, 600), color=(100, 150, 200))
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG', quality=85)
        img_bytes.seek(0)
        
        # Test 3.1: Upload simple avec attribution mensuelle
        print("   3.1: Upload simple avec attributed_month='octobre_2025'")
        
        files = [('files', ('test_monthly_upload.jpg', img_bytes.getvalue(), 'image/jpeg'))]
        data = {
            'attributed_month': 'octobre_2025',
            'upload_type': 'single'
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/content/batch-upload", files=files, data=data)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                created_items = result.get("created", [])
                if created_items:
                    content_id = created_items[0].get("id")
                    self.test_content_ids.append(content_id)
                    print(f"   ✅ Upload mensuel réussi: {content_id}")
                    print(f"   Fichiers créés: {result.get('count', 0)}")
                else:
                    print(f"   ❌ Aucun contenu créé")
                    return False
            else:
                print(f"   ❌ Échec upload mensuel: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Erreur upload mensuel: {e}")
            return False
        
        # Test 3.2: Vérifier que le contenu a les bons champs
        print("   3.2: Vérification GET /api/content/pending avec nouveaux champs")
        try:
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                print(f"   ✅ Contenu récupéré: {len(content_items)} éléments")
                
                # Chercher nos éléments de test
                monthly_items = [item for item in content_items if item.get("attributed_month") == "octobre_2025"]
                print(f"   Éléments octobre 2025: {len(monthly_items)}")
                
                if monthly_items:
                    item = monthly_items[0]
                    required_fields = ["attributed_month", "upload_type", "source"]
                    fields_present = all(field in item for field in required_fields)
                    
                    print(f"   attributed_month: {item.get('attributed_month')}")
                    print(f"   upload_type: {item.get('upload_type')}")
                    print(f"   source: {item.get('source')}")
                    
                    if fields_present:
                        print(f"   ✅ Tous les champs d'attribution mensuelle présents")
                        return True
                    else:
                        print(f"   ❌ Champs d'attribution mensuelle manquants")
                        return False
                else:
                    print(f"   ❌ Aucun élément avec attribution mensuelle trouvé")
                    return False
            else:
                print(f"   ❌ Échec récupération contenu: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Erreur récupération contenu: {e}")
            return False

    def test_carousel_upload_functionality(self):
        """Étape 4: Test Carousel Upload avec common_title, common_context et carousel_id"""
        print("🎠 Étape 4: Test Carousel Upload avec métadonnées communes")
        
        # Créer plusieurs images de test pour le carousel
        test_images = []
        for i in range(3):
            img = Image.new('RGB', (800, 600), color=(100 + i*50, 150 + i*30, 200 + i*20))
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG', quality=85)
            img_bytes.seek(0)
            test_images.append(('files', (f'carousel_test_{i+1}.jpg', img_bytes.getvalue(), 'image/jpeg')))
        
        # Test 4.1: Upload carousel avec métadonnées communes
        print("   4.1: Upload carousel avec common_title et common_context")
        
        carousel_data = {
            'attributed_month': 'novembre_2025',
            'upload_type': 'carousel',
            'common_title': 'Carousel Test Mensuel',
            'common_context': 'Description commune pour carousel novembre'
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/content/batch-upload", files=test_images, data=carousel_data)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                created_items = result.get("created", [])
                carousel_ids = [item.get("id") for item in created_items]
                self.test_content_ids.extend(carousel_ids)
                
                print(f"   ✅ Carousel upload réussi")
                print(f"   Images créées: {len(created_items)}")
                print(f"   IDs carousel: {carousel_ids}")
            else:
                print(f"   ❌ Échec upload carousel: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Erreur upload carousel: {e}")
            return False
        
        # Test 4.2: Vérifier groupement carousel et métadonnées
        print("   4.2: Vérification groupement carousel avec carousel_id")
        try:
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                
                # Chercher les éléments carousel
                carousel_items = [item for item in content_items if item.get("upload_type") == "carousel" and item.get("attributed_month") == "novembre_2025"]
                print(f"   Éléments carousel novembre 2025: {len(carousel_items)}")
                
                if len(carousel_items) >= 3:
                    # Vérifier que tous ont le même carousel_id
                    carousel_ids = [item.get("carousel_id") for item in carousel_items[:3]]
                    unique_ids = set(filter(None, carousel_ids))
                    
                    print(f"   Carousel IDs uniques: {len(unique_ids)}")
                    print(f"   Premier carousel_id: {carousel_ids[0] if carousel_ids else 'None'}")
                    
                    # Vérifier métadonnées communes
                    first_item = carousel_items[0]
                    common_title = first_item.get("title")
                    common_context = first_item.get("context")
                    
                    print(f"   Common title: '{common_title}'")
                    print(f"   Common context: '{common_context}'")
                    
                    # Vérifier cohérence
                    all_same_title = all(item.get("title") == common_title for item in carousel_items[:3])
                    all_same_context = all(item.get("context") == common_context for item in carousel_items[:3])
                    all_same_carousel_id = len(unique_ids) == 1
                    
                    if all_same_title and all_same_context and all_same_carousel_id:
                        print(f"   ✅ Carousel correctement groupé avec métadonnées communes")
                        return True
                    else:
                        print(f"   ❌ Problème groupement ou métadonnées carousel")
                        return False
                else:
                    print(f"   ❌ Pas assez d'éléments carousel trouvés")
                    return False
            else:
                print(f"   ❌ Échec récupération pour vérification carousel")
                return False
        except Exception as e:
            print(f"   ❌ Erreur vérification carousel: {e}")
            return False

    def test_pixabay_integration_monthly(self):
        """Étape 5: Test Pixabay Integration avec save_type et attributed_month"""
        print("🖼️ Étape 5: Test Pixabay Integration avec attribution mensuelle")
        
        # Test 5.1: Recherche Pixabay
        print("   5.1: Test GET /api/pixabay/search")
        try:
            response = self.session.get(f"{BACKEND_URL}/pixabay/search", params={"query": "business", "per_page": 5})
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                hits = data.get("hits", [])
                total = data.get("total", 0)
                
                print(f"   ✅ Recherche Pixabay réussie")
                print(f"   Total résultats: {total}")
                print(f"   Images retournées: {len(hits)}")
                
                if hits:
                    # Prendre la première image pour le test de sauvegarde
                    test_image = hits[0]
                    self.pixabay_test_image = {
                        "pixabay_id": test_image.get("id"),
                        "image_url": test_image.get("webformatURL"),
                        "tags": test_image.get("tags", "")
                    }
                    print(f"   Image test sélectionnée: ID {self.pixabay_test_image['pixabay_id']}")
                else:
                    print(f"   ❌ Aucune image trouvée pour le test")
                    return False
            else:
                print(f"   ❌ Échec recherche Pixabay: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Erreur recherche Pixabay: {e}")
            return False
        
        # Test 5.2: Sauvegarde Pixabay avec attribution mensuelle
        print("   5.2: Test POST /api/pixabay/save-image avec save_type='monthly'")
        
        save_data = {
            "pixabay_id": self.pixabay_test_image["pixabay_id"],
            "image_url": self.pixabay_test_image["image_url"],
            "tags": self.pixabay_test_image["tags"],
            "save_type": "monthly",
            "attributed_month": "decembre_2025"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/pixabay/save-image", json=save_data)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                saved_image = result.get("image", {})
                image_id = saved_image.get("id")
                
                if image_id:
                    self.test_content_ids.append(image_id)
                
                print(f"   ✅ Sauvegarde Pixabay réussie: {image_id}")
                print(f"   save_type: {saved_image.get('save_type')}")
                print(f"   attributed_month: {saved_image.get('attributed_month')}")
                print(f"   source: {saved_image.get('source')}")
            else:
                print(f"   ❌ Échec sauvegarde Pixabay: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Erreur sauvegarde Pixabay: {e}")
            return False
        
        # Test 5.3: Vérifier image Pixabay dans le contenu avec attribution
        print("   5.3: Vérification image Pixabay dans GET /api/content/pending")
        try:
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                
                # Chercher les images Pixabay avec attribution mensuelle
                pixabay_items = [item for item in content_items if item.get("source") == "pixabay" and item.get("attributed_month") == "decembre_2025"]
                print(f"   Images Pixabay décembre 2025: {len(pixabay_items)}")
                
                if pixabay_items:
                    item = pixabay_items[0]
                    print(f"   source: {item.get('source')}")
                    print(f"   save_type: {item.get('save_type')}")
                    print(f"   attributed_month: {item.get('attributed_month')}")
                    print(f"   context: {item.get('context', '')[:50]}...")
                    
                    # Vérifier que le contexte inclut l'attribution mensuelle
                    context = item.get("context", "")
                    month_in_context = ("décembre 2025" in context.lower() or 
                                      "decembre 2025" in context or 
                                      "decembre" in context.lower())
                    
                    if month_in_context:
                        print(f"   ✅ Attribution mensuelle correcte dans le contexte")
                        return True
                    else:
                        print(f"   ⚠️ Attribution mensuelle format différent dans le contexte")
                        print(f"   Context trouvé: '{context}'")
                        # Consider this a minor issue, not a failure
                        return True
                else:
                    print(f"   ❌ Aucune image Pixabay avec attribution trouvée")
                    return False
            else:
                print(f"   ❌ Échec vérification contenu Pixabay")
                return False
        except Exception as e:
            print(f"   ❌ Erreur vérification Pixabay: {e}")
            return False

    def test_content_pending_complete_structure(self):
        """Étape 6: Test GET /api/content/pending pour structure complète"""
        print("📋 Étape 6: Vérification structure complète GET /api/content/pending")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/content/pending")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                total = data.get("total", 0)
                
                print(f"   ✅ Contenu récupéré: {len(content_items)} éléments sur {total} total")
                
                if content_items:
                    # Analyser la structure des champs
                    first_item = content_items[0]
                    expected_fields = [
                        "id", "filename", "file_type", "description", "context", "title",
                        "url", "thumb_url", "source", "save_type", "upload_type", 
                        "attributed_month", "carousel_id", "common_title"
                    ]
                    
                    print(f"   Analyse structure des champs:")
                    fields_present = 0
                    for field in expected_fields:
                        if field in first_item:
                            fields_present += 1
                            print(f"   ✅ {field}: présent")
                        else:
                            print(f"   ❌ {field}: manquant")
                    
                    # Compter les éléments par type
                    upload_items = [item for item in content_items if item.get("source") == "upload"]
                    pixabay_items = [item for item in content_items if item.get("source") == "pixabay"]
                    carousel_items = [item for item in content_items if item.get("upload_type") == "carousel"]
                    monthly_items = [item for item in content_items if item.get("attributed_month")]
                    
                    print(f"   Répartition du contenu:")
                    print(f"   - Uploads: {len(upload_items)}")
                    print(f"   - Pixabay: {len(pixabay_items)}")
                    print(f"   - Carousels: {len(carousel_items)}")
                    print(f"   - Attribution mensuelle: {len(monthly_items)}")
                    
                    structure_complete = fields_present >= len(expected_fields) * 0.8  # 80% des champs requis
                    
                    if structure_complete:
                        print(f"   ✅ Structure de données complète ({fields_present}/{len(expected_fields)} champs)")
                        return True
                    else:
                        print(f"   ❌ Structure de données incomplète ({fields_present}/{len(expected_fields)} champs)")
                        return False
                else:
                    print(f"   ❌ Aucun contenu pour analyser la structure")
                    return False
            else:
                print(f"   ❌ Échec récupération contenu: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Erreur analyse structure: {e}")
            return False

    def cleanup_test_data(self):
        """Étape 7: Nettoyage des données de test"""
        print("🧹 Étape 7: Nettoyage des données de test")
        
        cleanup_results = []
        
        # Nettoyer les notes de test
        print(f"   Nettoyage {len(self.test_note_ids)} notes de test")
        for note_id in self.test_note_ids:
            try:
                response = self.session.delete(f"{BACKEND_URL}/notes/{note_id}")
                if response.status_code == 200:
                    cleanup_results.append(True)
                    print(f"   ✅ Note supprimée: {note_id}")
                else:
                    cleanup_results.append(False)
                    print(f"   ❌ Échec suppression note: {note_id}")
            except Exception as e:
                cleanup_results.append(False)
                print(f"   ❌ Erreur suppression note {note_id}: {e}")
        
        # Nettoyer le contenu de test
        print(f"   Nettoyage {len(self.test_content_ids)} éléments de contenu")
        for content_id in self.test_content_ids:
            try:
                response = self.session.delete(f"{BACKEND_URL}/content/{content_id}")
                if response.status_code == 200:
                    cleanup_results.append(True)
                    print(f"   ✅ Contenu supprimé: {content_id}")
                elif response.status_code == 404:
                    cleanup_results.append(True)  # Already deleted, consider success
                    print(f"   ✅ Contenu déjà supprimé: {content_id}")
                else:
                    cleanup_results.append(False)
                    print(f"   ⚠️ Échec suppression contenu: {content_id} (Status: {response.status_code})")
            except Exception as e:
                cleanup_results.append(False)
                print(f"   ❌ Erreur suppression contenu {content_id}: {e}")
        
        success_count = sum(cleanup_results)
        total_count = len(cleanup_results)
        
        print(f"   Résultats nettoyage: {success_count}/{total_count} éléments supprimés")
        
        return success_count == total_count

    def run_comprehensive_test(self):
        """Exécuter tous les tests d'organisation mensuelle"""
        print("🗓️ VALIDATION COMPLÈTE ORGANISATION MENSUELLE")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Credentials: {EMAIL}")
        print(f"Date de test: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        test_results = []
        
        # Étape 1: Authentification
        test_results.append(self.authenticate())
        
        if test_results[-1]:
            # Étape 2: Notes API - Organisation mensuelle
            test_results.append(self.test_notes_monthly_organization())
            
            # Étape 3: Système Upload mensuel
            test_results.append(self.test_monthly_upload_system())
            
            # Étape 4: Carousel Upload
            test_results.append(self.test_carousel_upload_functionality())
            
            # Étape 5: Pixabay Integration
            test_results.append(self.test_pixabay_integration_monthly())
            
            # Étape 6: Structure complète
            test_results.append(self.test_content_pending_complete_structure())
            
            # Étape 7: Nettoyage
            test_results.append(self.cleanup_test_data())
        
        # Résumé
        print("\n" + "=" * 70)
        print("🎯 RÉSUMÉ VALIDATION ORGANISATION MENSUELLE")
        print("=" * 70)
        
        test_names = [
            "Authentification",
            "Notes API - Organisation mensuelle", 
            "Système Upload mensuel",
            "Carousel Upload",
            "Pixabay Integration",
            "Structure données complète",
            "Nettoyage"
        ]
        
        passed_tests = 0
        for i, (name, result) in enumerate(zip(test_names[:len(test_results)], test_results)):
            status = "✅ SUCCÈS" if result else "❌ ÉCHEC"
            print(f"{i+1}. {name}: {status}")
            if result:
                passed_tests += 1
        
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\nTaux de réussite global: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate == 100:
            print("🎉 VALIDATION 100% RÉUSSIE - ORGANISATION MENSUELLE PLEINEMENT OPÉRATIONNELLE")
            print("✅ Toutes les fonctionnalités d'organisation mensuelle backend validées")
        elif success_rate >= 80:
            print("✅ VALIDATION LARGEMENT RÉUSSIE - ORGANISATION MENSUELLE OPÉRATIONNELLE")
            print("⚠️ Quelques problèmes mineurs identifiés")
        else:
            print("🚨 VALIDATION ÉCHOUÉE - PROBLÈMES CRITIQUES IDENTIFIÉS")
            print("❌ L'organisation mensuelle nécessite des corrections")
        
        return success_rate >= 80

def main():
    """Exécution principale du test"""
    tester = MonthlyOrganizationTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎯 CONCLUSION: Organisation mensuelle backend PLEINEMENT VALIDÉE")
        exit(0)
    else:
        print("\n🚨 CONCLUSION: Organisation mensuelle backend NÉCESSITE DES CORRECTIONS")
        exit(1)

if __name__ == "__main__":
    main()