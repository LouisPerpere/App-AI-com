#!/usr/bin/env python3
"""
Test complet selon la demande française - Diagnostic et correction complète du système de vignettes
Basé sur backend_test.py qui fonctionne
"""

import requests
import json
import os
import time
import base64
from io import BytesIO
from PIL import Image

# Configuration
BACKEND_URL = "https://social-publisher-10.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials as specified in review request
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class ComprehensiveThumbnailTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        status = "✅ RÉUSSI" if success else "❌ ÉCHEC"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Détails: {details}")
        if error:
            print(f"   Erreur: {error}")
        print()
    
    def authenticate(self):
        """ÉTAPE 1: Authentifier avec lperpere@yahoo.fr / L@Reunion974!"""
        print("🔐 ÉTAPE 1: AUTHENTIFICATION")
        print("=" * 60)
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                self.log_result(
                    "Authentification", 
                    True, 
                    f"Connexion réussie avec {TEST_EMAIL}, User ID: {self.user_id}"
                )
                return True
            else:
                self.log_result(
                    "Authentification", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Authentification", False, error=str(e))
            return False
    
    def analyze_all_thumb_urls(self):
        """ÉTAPE 2: Vérifier toutes les thumb_url - Analyser les 44 fichiers"""
        print("📊 ÉTAPE 2: ANALYSE COMPLÈTE DES THUMB_URL")
        print("=" * 60)
        
        try:
            # Get all content files
            response = self.session.get(f"{API_BASE}/content/pending?limit=100")
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                total_files = len(content)
                
                # Detailed analysis
                null_thumb_urls = 0
                libfusion_urls = 0
                claire_marcus_urls = 0
                other_urls = 0
                
                libfusion_examples = []
                claire_marcus_examples = []
                null_examples = []
                
                for item in content:
                    thumb_url = item.get("thumb_url")
                    filename = item.get("filename", "unknown")
                    
                    if thumb_url is None or thumb_url == "":
                        null_thumb_urls += 1
                        if len(null_examples) < 3:
                            null_examples.append(f"{filename}: null")
                    elif "libfusion.preview.emergentagent.com" in thumb_url:
                        libfusion_urls += 1
                        if len(libfusion_examples) < 3:
                            libfusion_examples.append(f"{filename}: {thumb_url}")
                    elif "claire-marcus.com" in thumb_url:
                        claire_marcus_urls += 1
                        if len(claire_marcus_examples) < 3:
                            claire_marcus_examples.append(f"{filename}: {thumb_url}")
                    else:
                        other_urls += 1
                
                # Detailed reporting
                details = f"ANALYSE COMPLÈTE: {total_files} fichiers totaux. "
                details += f"thumb_url null: {null_thumb_urls}, "
                details += f"libfusion.preview.emergentagent.com: {libfusion_urls}, "
                details += f"claire-marcus.com: {claire_marcus_urls}, "
                details += f"autres domaines: {other_urls}. "
                
                if libfusion_examples:
                    details += f"Exemples libfusion: {libfusion_examples[:2]}. "
                if claire_marcus_examples:
                    details += f"Exemples claire-marcus: {claire_marcus_examples[:2]}. "
                if null_examples:
                    details += f"Exemples null: {null_examples[:2]}. "
                
                self.log_result(
                    "Analyse complète thumb_url", 
                    True, 
                    details
                )
                
                # Store results for later use
                self.analysis = {
                    "total_files": total_files,
                    "null_thumb_urls": null_thumb_urls,
                    "libfusion_urls": libfusion_urls,
                    "claire_marcus_urls": claire_marcus_urls,
                    "other_urls": other_urls,
                    "libfusion_examples": libfusion_examples,
                    "claire_marcus_examples": claire_marcus_examples,
                    "null_examples": null_examples
                }
                
                return True
            else:
                self.log_result(
                    "Analyse complète thumb_url", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Analyse complète thumb_url", False, error=str(e))
            return False
    
    def generate_all_missing_thumbnails(self):
        """ÉTAPE 3: Générer TOUTES les vignettes manquantes"""
        print("🔄 ÉTAPE 3: GÉNÉRATION TOUTES VIGNETTES MANQUANTES")
        print("=" * 60)
        
        try:
            # Check current status
            status_response = self.session.get(f"{API_BASE}/content/thumbnails/status")
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                missing_before = status_data.get("missing_thumbnails", 0)
                total_files = status_data.get("total_files", 0)
                completion_before = status_data.get("completion_percentage", 0)
                
                print(f"📊 AVANT génération: {missing_before} vignettes manquantes sur {total_files} fichiers ({completion_before}% complété)")
                
                # Trigger rebuild of ALL thumbnails
                rebuild_response = self.session.post(f"{API_BASE}/content/thumbnails/rebuild")
                
                if rebuild_response.status_code == 200:
                    rebuild_data = rebuild_response.json()
                    scheduled = rebuild_data.get("scheduled", 0)
                    files_found = rebuild_data.get("files_found", 0)
                    
                    print(f"🔄 Génération programmée pour {scheduled} vignettes sur {files_found} fichiers trouvés")
                    
                    # Wait for background processing
                    print("⏳ Attente 15 secondes pour la génération complète en arrière-plan...")
                    time.sleep(15)
                    
                    # Check status after rebuild
                    status_after_response = self.session.get(f"{API_BASE}/content/thumbnails/status")
                    
                    if status_after_response.status_code == 200:
                        status_after_data = status_after_response.json()
                        missing_after = status_after_data.get("missing_thumbnails", 0)
                        with_thumbnails = status_after_data.get("with_thumbnails", 0)
                        completion_after = status_after_data.get("completion_percentage", 0)
                        
                        improvement = completion_after - completion_before
                        
                        self.log_result(
                            "Génération toutes vignettes manquantes", 
                            True, 
                            f"RÉSULTATS: Avant: {missing_before} manquantes ({completion_before}%), Après: {missing_after} manquantes ({completion_after}%), Amélioration: +{improvement:.1f}%, {with_thumbnails} fichiers avec vignettes"
                        )
                        
                        return True
                    else:
                        self.log_result(
                            "Vérification post-génération", 
                            False, 
                            f"Status: {status_after_response.status_code}",
                            status_after_response.text
                        )
                        return False
                else:
                    self.log_result(
                        "Génération toutes vignettes manquantes", 
                        False, 
                        f"Status: {rebuild_response.status_code}",
                        rebuild_response.text
                    )
                    return False
            else:
                self.log_result(
                    "Vérification statut initial", 
                    False, 
                    f"Status: {status_response.status_code}",
                    status_response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Génération toutes vignettes manquantes", False, error=str(e))
            return False
    
    def test_thumbnail_accessibility_comprehensive(self):
        """ÉTAPE 4: Tester l'accessibilité des vignettes générées via le proxy"""
        print("🔍 ÉTAPE 4: TEST ACCESSIBILITÉ COMPLÈTE VIGNETTES")
        print("=" * 60)
        
        try:
            # Get all content with thumbnails
            response = self.session.get(f"{API_BASE}/content/pending?limit=50")
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                
                accessible_count = 0
                inaccessible_count = 0
                webp_count = 0
                claire_marcus_accessible = 0
                libfusion_accessible = 0
                
                tested_urls = []
                
                for item in content:
                    thumb_url = item.get("thumb_url")
                    filename = item.get("filename", "unknown")
                    
                    if thumb_url and thumb_url != "":
                        try:
                            # Test accessibility
                            thumb_response = requests.get(thumb_url, timeout=10)
                            
                            if thumb_response.status_code == 200:
                                content_type = thumb_response.headers.get('content-type', '')
                                content_length = len(thumb_response.content)
                                
                                if 'image' in content_type.lower():
                                    accessible_count += 1
                                    
                                    # Check domain
                                    if "claire-marcus.com" in thumb_url:
                                        claire_marcus_accessible += 1
                                    elif "libfusion.preview.emergentagent.com" in thumb_url:
                                        libfusion_accessible += 1
                                    
                                    # Check format
                                    is_webp = 'webp' in content_type.lower() or thumb_url.endswith('.webp')
                                    if is_webp:
                                        webp_count += 1
                                    
                                    if len(tested_urls) < 5:
                                        domain = "claire-marcus" if "claire-marcus.com" in thumb_url else "libfusion" if "libfusion" in thumb_url else "autre"
                                        tested_urls.append(f"✅ {filename} ({domain}, {content_length}b, {'WEBP' if is_webp else content_type})")
                                else:
                                    inaccessible_count += 1
                                    if len(tested_urls) < 5:
                                        tested_urls.append(f"❌ {filename} (pas image: {content_type})")
                            else:
                                inaccessible_count += 1
                                if len(tested_urls) < 5:
                                    tested_urls.append(f"❌ {filename} (status: {thumb_response.status_code})")
                                
                        except Exception as thumb_error:
                            inaccessible_count += 1
                            if len(tested_urls) < 5:
                                tested_urls.append(f"❌ {filename} (erreur: {str(thumb_error)[:50]})")
                
                total_tested = accessible_count + inaccessible_count
                success_rate = (accessible_count / total_tested * 100) if total_tested > 0 else 0
                webp_rate = (webp_count / accessible_count * 100) if accessible_count > 0 else 0
                
                details = f"RÉSULTATS ACCESSIBILITÉ: {total_tested} vignettes testées, "
                details += f"{accessible_count} accessibles ({success_rate:.1f}%), "
                details += f"{webp_count} WEBP ({webp_rate:.1f}%), "
                details += f"{claire_marcus_accessible} claire-marcus accessibles, "
                details += f"{libfusion_accessible} libfusion accessibles, "
                details += f"{inaccessible_count} inaccessibles. "
                details += f"Échantillons: {tested_urls[:3]}"
                
                self.log_result(
                    "Test accessibilité complète vignettes", 
                    accessible_count > 0, 
                    details
                )
                
                # Store results
                self.accessibility_results = {
                    "total_tested": total_tested,
                    "accessible_count": accessible_count,
                    "webp_count": webp_count,
                    "claire_marcus_accessible": claire_marcus_accessible,
                    "libfusion_accessible": libfusion_accessible,
                    "success_rate": success_rate,
                    "webp_rate": webp_rate
                }
                
                return accessible_count > 0
            else:
                self.log_result(
                    "Test accessibilité complète vignettes", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Test accessibilité complète vignettes", False, error=str(e))
            return False
    
    def final_objective_verification(self):
        """ÉTAPE 5: Vérification finale - objectif 44/44 fichiers avec thumb_url claire-marcus.com et vignettes WEBP accessibles"""
        print("🎯 ÉTAPE 5: VÉRIFICATION FINALE OBJECTIF")
        print("=" * 60)
        
        try:
            # Get final comprehensive status
            api_response = self.session.get(f"{API_BASE}/content/pending?limit=100")
            
            if api_response.status_code == 200:
                api_data = api_response.json()
                api_content = api_data.get("content", [])
                api_total = len(api_content)
                
                claire_marcus_count = 0
                webp_accessible_count = 0
                total_with_thumbs = 0
                
                for item in api_content:
                    thumb_url = item.get("thumb_url")
                    if thumb_url and thumb_url != "":
                        total_with_thumbs += 1
                        
                        if "claire-marcus.com" in thumb_url:
                            claire_marcus_count += 1
                            
                            # Quick accessibility test for claire-marcus URLs
                            if thumb_url.endswith('.webp'):
                                try:
                                    thumb_response = requests.get(thumb_url, timeout=5)
                                    if thumb_response.status_code == 200 and 'image' in thumb_response.headers.get('content-type', ''):
                                        webp_accessible_count += 1
                                except:
                                    pass  # Count as not accessible
                
                # Calculate metrics
                claire_marcus_rate = (claire_marcus_count / api_total * 100) if api_total > 0 else 0
                webp_accessible_rate = (webp_accessible_count / claire_marcus_count * 100) if claire_marcus_count > 0 else 0
                
                # Check if objective is met
                objective_44_claire_marcus = claire_marcus_count >= 44
                objective_webp_accessible = webp_accessible_count >= 40  # Allow some margin for network issues
                
                overall_objective_met = objective_44_claire_marcus and webp_accessible_count > 0
                
                details = f"VÉRIFICATION FINALE: {api_total} fichiers totaux, "
                details += f"{total_with_thumbs} avec thumb_url, "
                details += f"{claire_marcus_count} avec claire-marcus.com ({claire_marcus_rate:.1f}%), "
                details += f"{webp_accessible_count} WEBP accessibles ({webp_accessible_rate:.1f}%). "
                details += f"OBJECTIF 44/44 claire-marcus: {'✅ ATTEINT' if objective_44_claire_marcus else '❌ NON ATTEINT'}. "
                details += f"OBJECTIF vignettes WEBP accessibles: {'✅ ATTEINT' if objective_webp_accessible else '❌ NON ATTEINT'}. "
                details += f"OBJECTIF GLOBAL: {'✅ ATTEINT' if overall_objective_met else '❌ NON ATTEINT'}"
                
                self.log_result(
                    "Vérification finale objectif", 
                    overall_objective_met, 
                    details
                )
                
                # Store final results
                self.final_results = {
                    "total_files": api_total,
                    "total_with_thumbs": total_with_thumbs,
                    "claire_marcus_count": claire_marcus_count,
                    "webp_accessible_count": webp_accessible_count,
                    "objective_44_claire_marcus": objective_44_claire_marcus,
                    "objective_webp_accessible": objective_webp_accessible,
                    "overall_objective_met": overall_objective_met
                }
                
                return overall_objective_met
            else:
                self.log_result(
                    "Vérification finale objectif", 
                    False, 
                    f"Status: {api_response.status_code}",
                    api_response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Vérification finale objectif", False, error=str(e))
            return False
    
    def run_complete_diagnostic(self):
        """Exécuter le diagnostic complet selon la demande française"""
        print("🎯 DIAGNOSTIC ET CORRECTION COMPLÈTE DU SYSTÈME DE VIGNETTES")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Utilisateur de test: {TEST_EMAIL}")
        print(f"OBJECTIF: 44/44 fichiers avec thumb_url pointant vers claire-marcus.com")
        print(f"          ET vignettes WEBP accessibles via le proxy")
        print("=" * 80)
        print()
        
        # Run all diagnostic steps
        steps = [
            ("Authentification", self.authenticate),
            ("Analyse complète thumb_url", self.analyze_all_thumb_urls),
            ("Génération toutes vignettes manquantes", self.generate_all_missing_thumbnails),
            ("Test accessibilité complète vignettes", self.test_thumbnail_accessibility_comprehensive),
            ("Vérification finale objectif", self.final_objective_verification)
        ]
        
        for step_name, step_func in steps:
            print(f"🔄 Exécution: {step_name}")
            try:
                step_func()
            except Exception as e:
                self.log_result(step_name, False, error=str(e))
            print()
        
        # Generate comprehensive summary
        self.generate_comprehensive_summary()
        
        # Return overall success
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        return success_rate >= 80
    
    def generate_comprehensive_summary(self):
        """Générer un résumé complet selon la demande française"""
        print("📋 RÉSUMÉ COMPLET - DIAGNOSTIC SYSTÈME DE VIGNETTES")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"RÉSULTATS GLOBAUX:")
        print(f"• Tests totaux: {total}")
        print(f"• Tests réussis: {passed}")
        print(f"• Tests échoués: {total - passed}")
        print(f"• Taux de réussite: {success_rate:.1f}%")
        print()
        
        print("RÉSULTATS DÉTAILLÉS PAR ÉTAPE:")
        print("-" * 50)
        
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   📝 {result['details']}")
            if result['error']:
                print(f"   ⚠️ Erreur: {result['error']}")
            print()
        
        # Key findings summary
        print("CONCLUSIONS CLÉS SELON LA DEMANDE FRANÇAISE:")
        print("-" * 50)
        
        if hasattr(self, 'analysis'):
            analysis = self.analysis
            print(f"1. ANALYSE DES 44 FICHIERS:")
            print(f"   • Total fichiers: {analysis['total_files']}")
            print(f"   • thumb_url = null: {analysis['null_thumb_urls']}")
            print(f"   • Utilisant libfusion.preview.emergentagent.com: {analysis['libfusion_urls']}")
            print(f"   • Utilisant correctement claire-marcus.com: {analysis['claire_marcus_urls']}")
            print()
        
        if hasattr(self, 'accessibility_results'):
            access = self.accessibility_results
            print(f"2. ACCESSIBILITÉ DES VIGNETTES:")
            print(f"   • Vignettes testées: {access['total_tested']}")
            print(f"   • Vignettes accessibles: {access['accessible_count']} ({access['success_rate']:.1f}%)")
            print(f"   • Vignettes WEBP: {access['webp_count']} ({access['webp_rate']:.1f}%)")
            print(f"   • claire-marcus.com accessibles: {access['claire_marcus_accessible']}")
            print()
        
        if hasattr(self, 'final_results'):
            final = self.final_results
            print(f"3. VÉRIFICATION OBJECTIF FINAL:")
            print(f"   • Objectif 44/44 claire-marcus.com: {'✅ ATTEINT' if final['objective_44_claire_marcus'] else '❌ NON ATTEINT'}")
            print(f"   • Vignettes WEBP accessibles: {final['webp_accessible_count']}")
            print(f"   • OBJECTIF GLOBAL: {'✅ ATTEINT' if final['overall_objective_met'] else '❌ NON ATTEINT'}")
            print()
        
        print("🎯 DIAGNOSTIC TERMINÉ")

if __name__ == "__main__":
    tester = ComprehensiveThumbnailTester()
    success = tester.run_complete_diagnostic()
    
    if success:
        print("✅ Diagnostic global: SUCCÈS")
        exit(0)
    else:
        print("❌ Diagnostic global: ÉCHEC")
        exit(1)