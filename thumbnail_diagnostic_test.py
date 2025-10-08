#!/usr/bin/env python3
"""
Diagnostic et correction complète du système de vignettes
Test complet selon la demande française dans review_request

1. Authentifier avec lperpere@yahoo.fr / L@Reunion974!
2. Vérifier toutes les thumb_url - Analyser les 44 fichiers
3. Générer TOUTES les vignettes manquantes
4. Mettre à jour TOUTES les thumb_url restantes
5. Tester l'accessibilité des vignettes générées via le proxy
"""

import requests
import json
import os
import time
import pymongo
from datetime import datetime

# Configuration
BACKEND_URL = "https://post-restore.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials as specified in review request
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

# MongoDB connection for direct database analysis
MONGO_URL = "mongodb+srv://lperpere:ClaireMarcus2025@cluster0.24k0jzd.mongodb.net/claire_marcus?retryWrites=true&w=majority&appName=Cluster0"

class ThumbnailDiagnosticTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.test_results = []
        self.mongo_client = None
        self.db = None
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        status = "✅ RÉUSSI" if success else "❌ ÉCHEC"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Détails: {details}")
        if error:
            print(f"   Erreur: {error}")
        print()
    
    def connect_mongodb(self):
        """Connect to MongoDB for direct database analysis"""
        try:
            self.mongo_client = pymongo.MongoClient(MONGO_URL)
            self.db = self.mongo_client.claire_marcus
            # Test connection
            self.db.admin.command('ping')
            print("✅ Connexion MongoDB établie")
            return True
        except Exception as e:
            print(f"❌ Erreur connexion MongoDB: {e}")
            return False
    
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
    
    def analyze_thumb_urls_api(self):
        """ÉTAPE 2A: Analyser les thumb_url via API"""
        print("📊 ÉTAPE 2A: ANALYSE THUMB_URL VIA API")
        print("=" * 60)
        
        try:
            # Get all content files
            response = self.session.get(f"{API_BASE}/content/pending?limit=100")
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                total_files = len(content)
                
                # Analyze thumb_url patterns
                null_thumb_urls = 0
                libfusion_urls = 0
                claire_marcus_urls = 0
                other_urls = 0
                
                sample_urls = []
                
                for item in content:
                    thumb_url = item.get("thumb_url")
                    if thumb_url is None or thumb_url == "":
                        null_thumb_urls += 1
                    elif "libfusion.preview.emergentagent.com" in thumb_url:
                        libfusion_urls += 1
                        if len(sample_urls) < 2:
                            sample_urls.append(f"libfusion: {thumb_url}")
                    elif "claire-marcus.com" in thumb_url:
                        claire_marcus_urls += 1
                        if len(sample_urls) < 2:
                            sample_urls.append(f"claire-marcus: {thumb_url}")
                    else:
                        other_urls += 1
                        if len(sample_urls) < 2:
                            sample_urls.append(f"autre: {thumb_url}")
                
                self.log_result(
                    "Analyse thumb_url API", 
                    True, 
                    f"Total fichiers: {total_files}, thumb_url null: {null_thumb_urls}, libfusion: {libfusion_urls}, claire-marcus: {claire_marcus_urls}, autres: {other_urls}. Échantillons: {sample_urls}"
                )
                
                # Store results for later use
                self.api_analysis = {
                    "total_files": total_files,
                    "null_thumb_urls": null_thumb_urls,
                    "libfusion_urls": libfusion_urls,
                    "claire_marcus_urls": claire_marcus_urls,
                    "other_urls": other_urls,
                    "sample_urls": sample_urls
                }
                
                return True
            else:
                self.log_result(
                    "Analyse thumb_url API", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Analyse thumb_url API", False, error=str(e))
            return False
    
    def analyze_thumb_urls_mongodb(self):
        """ÉTAPE 2B: Analyser les thumb_url directement dans MongoDB"""
        print("🗄️ ÉTAPE 2B: ANALYSE THUMB_URL MONGODB")
        print("=" * 60)
        
        if not self.db:
            self.log_result(
                "Analyse thumb_url MongoDB", 
                False, 
                "Connexion MongoDB non disponible"
            )
            return False
        
        try:
            # Get all media documents for this user
            media_collection = self.db.media
            query = {"owner_id": self.user_id, "deleted": {"$ne": True}}
            
            documents = list(media_collection.find(query))
            total_docs = len(documents)
            
            # Analyze thumb_url patterns
            null_thumb_urls = 0
            libfusion_urls = 0
            claire_marcus_urls = 0
            other_urls = 0
            
            sample_urls = []
            
            for doc in documents:
                thumb_url = doc.get("thumb_url")
                if thumb_url is None or thumb_url == "":
                    null_thumb_urls += 1
                elif "libfusion.preview.emergentagent.com" in thumb_url:
                    libfusion_urls += 1
                    if len(sample_urls) < 2:
                        sample_urls.append(f"libfusion: {thumb_url}")
                elif "claire-marcus.com" in thumb_url:
                    claire_marcus_urls += 1
                    if len(sample_urls) < 2:
                        sample_urls.append(f"claire-marcus: {thumb_url}")
                else:
                    other_urls += 1
                    if len(sample_urls) < 2:
                        sample_urls.append(f"autre: {thumb_url}")
            
            self.log_result(
                "Analyse thumb_url MongoDB", 
                True, 
                f"Total documents: {total_docs}, thumb_url null: {null_thumb_urls}, libfusion: {libfusion_urls}, claire-marcus: {claire_marcus_urls}, autres: {other_urls}. Échantillons: {sample_urls}"
            )
            
            # Store results for later use
            self.mongodb_analysis = {
                "total_docs": total_docs,
                "null_thumb_urls": null_thumb_urls,
                "libfusion_urls": libfusion_urls,
                "claire_marcus_urls": claire_marcus_urls,
                "other_urls": other_urls,
                "sample_urls": sample_urls
            }
            
            return True
                
        except Exception as e:
            self.log_result("Analyse thumb_url MongoDB", False, error=str(e))
            return False
    
    def generate_missing_thumbnails(self):
        """ÉTAPE 3: Générer TOUTES les vignettes manquantes"""
        print("🔄 ÉTAPE 3: GÉNÉRATION VIGNETTES MANQUANTES")
        print("=" * 60)
        
        try:
            # First check current status
            status_response = self.session.get(f"{API_BASE}/content/thumbnails/status")
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                missing_before = status_data.get("missing_thumbnails", 0)
                total_files = status_data.get("total_files", 0)
                
                print(f"📊 Avant génération: {missing_before} vignettes manquantes sur {total_files} fichiers")
                
                # Trigger rebuild of all thumbnails
                rebuild_response = self.session.post(f"{API_BASE}/content/thumbnails/rebuild")
                
                if rebuild_response.status_code == 200:
                    rebuild_data = rebuild_response.json()
                    scheduled = rebuild_data.get("scheduled", 0)
                    files_found = rebuild_data.get("files_found", 0)
                    
                    self.log_result(
                        "Génération vignettes manquantes", 
                        True, 
                        f"Génération programmée pour {scheduled} vignettes sur {files_found} fichiers trouvés"
                    )
                    
                    # Wait for background processing
                    print("⏳ Attente 10 secondes pour la génération en arrière-plan...")
                    time.sleep(10)
                    
                    # Check status after rebuild
                    status_after_response = self.session.get(f"{API_BASE}/content/thumbnails/status")
                    
                    if status_after_response.status_code == 200:
                        status_after_data = status_after_response.json()
                        missing_after = status_after_data.get("missing_thumbnails", 0)
                        with_thumbnails = status_after_data.get("with_thumbnails", 0)
                        completion_percentage = status_after_data.get("completion_percentage", 0)
                        
                        self.log_result(
                            "Vérification post-génération", 
                            True, 
                            f"Après génération: {missing_after} vignettes manquantes, {with_thumbnails} avec vignettes, {completion_percentage}% complété"
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
                        "Génération vignettes manquantes", 
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
            self.log_result("Génération vignettes manquantes", False, error=str(e))
            return False
    
    def update_thumb_urls_mongodb(self):
        """ÉTAPE 4: Mettre à jour TOUTES les thumb_url restantes de libfusion vers claire-marcus"""
        print("🔄 ÉTAPE 4: MISE À JOUR THUMB_URL MONGODB")
        print("=" * 60)
        
        if not self.db:
            self.log_result(
                "Mise à jour thumb_url MongoDB", 
                False, 
                "Connexion MongoDB non disponible"
            )
            return False
        
        try:
            media_collection = self.db.media
            
            # Find all documents with libfusion URLs
            query = {
                "owner_id": self.user_id,
                "thumb_url": {"$regex": "libfusion.preview.emergentagent.com"}
            }
            
            docs_to_update = list(media_collection.find(query))
            count_to_update = len(docs_to_update)
            
            print(f"📊 Trouvé {count_to_update} documents avec URLs libfusion à mettre à jour")
            
            if count_to_update > 0:
                # Update all libfusion URLs to claire-marcus
                update_result = media_collection.update_many(
                    query,
                    [{
                        "$set": {
                            "thumb_url": {
                                "$replaceOne": {
                                    "input": "$thumb_url",
                                    "find": "https://post-restore.preview.emergentagent.com",
                                    "replacement": "https://claire-marcus.com"
                                }
                            }
                        }
                    }]
                )
                
                matched_count = update_result.matched_count
                modified_count = update_result.modified_count
                
                self.log_result(
                    "Mise à jour thumb_url MongoDB", 
                    True, 
                    f"Requête MongoDB exécutée: {matched_count} documents correspondants, {modified_count} documents modifiés"
                )
                
                # Verify the update
                verification_query = {
                    "owner_id": self.user_id,
                    "thumb_url": {"$regex": "libfusion.preview.emergentagent.com"}
                }
                remaining_libfusion = media_collection.count_documents(verification_query)
                
                claire_marcus_query = {
                    "owner_id": self.user_id,
                    "thumb_url": {"$regex": "claire-marcus.com"}
                }
                claire_marcus_count = media_collection.count_documents(claire_marcus_query)
                
                self.log_result(
                    "Vérification mise à jour", 
                    True, 
                    f"Après mise à jour: {remaining_libfusion} URLs libfusion restantes, {claire_marcus_count} URLs claire-marcus"
                )
                
                return True
            else:
                self.log_result(
                    "Mise à jour thumb_url MongoDB", 
                    True, 
                    "Aucun document avec URL libfusion trouvé - mise à jour non nécessaire"
                )
                return True
                
        except Exception as e:
            self.log_result("Mise à jour thumb_url MongoDB", False, error=str(e))
            return False
    
    def test_thumbnail_accessibility(self):
        """ÉTAPE 5: Tester l'accessibilité des vignettes générées via le proxy"""
        print("🔍 ÉTAPE 5: TEST ACCESSIBILITÉ VIGNETTES")
        print("=" * 60)
        
        try:
            # Get a sample of content with thumbnails
            response = self.session.get(f"{API_BASE}/content/pending?limit=10")
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                
                accessible_count = 0
                inaccessible_count = 0
                tested_urls = []
                webp_count = 0
                
                for item in content:
                    thumb_url = item.get("thumb_url")
                    if thumb_url and thumb_url != "":
                        try:
                            # Test accessibility
                            thumb_response = requests.get(thumb_url, timeout=10)
                            
                            if thumb_response.status_code == 200:
                                content_type = thumb_response.headers.get('content-type', '')
                                content_length = len(thumb_response.content)
                                
                                if 'image' in content_type.lower():
                                    accessible_count += 1
                                    is_webp = 'webp' in content_type.lower() or thumb_url.endswith('.webp')
                                    if is_webp:
                                        webp_count += 1
                                    tested_urls.append(f"✅ {thumb_url} ({content_length} bytes, {'WEBP' if is_webp else content_type})")
                                else:
                                    inaccessible_count += 1
                                    tested_urls.append(f"❌ {thumb_url} (pas une image: {content_type})")
                            else:
                                inaccessible_count += 1
                                tested_urls.append(f"❌ {thumb_url} (status: {thumb_response.status_code})")
                                
                        except Exception as thumb_error:
                            inaccessible_count += 1
                            tested_urls.append(f"❌ {thumb_url} (erreur: {str(thumb_error)})")
                        
                        # Limit testing to avoid too much output
                        if len(tested_urls) >= 5:
                            break
                
                total_tested = accessible_count + inaccessible_count
                success_rate = (accessible_count / total_tested * 100) if total_tested > 0 else 0
                webp_rate = (webp_count / accessible_count * 100) if accessible_count > 0 else 0
                
                self.log_result(
                    "Test accessibilité vignettes", 
                    accessible_count > 0, 
                    f"Testé {total_tested} vignettes: {accessible_count} accessibles ({success_rate:.1f}%), {webp_count} WEBP ({webp_rate:.1f}%), {inaccessible_count} inaccessibles. Échantillons: {tested_urls[:3]}"
                )
                
                return accessible_count > 0
            else:
                self.log_result(
                    "Test accessibilité vignettes", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Test accessibilité vignettes", False, error=str(e))
            return False
    
    def final_verification(self):
        """ÉTAPE 6: Vérification finale - objectif 44/44 fichiers avec thumb_url claire-marcus.com"""
        print("🎯 ÉTAPE 6: VÉRIFICATION FINALE")
        print("=" * 60)
        
        try:
            # Get final status via API
            api_response = self.session.get(f"{API_BASE}/content/pending?limit=100")
            
            if api_response.status_code == 200:
                api_data = api_response.json()
                api_content = api_data.get("content", [])
                api_total = len(api_content)
                
                api_claire_marcus = 0
                api_with_thumbs = 0
                
                for item in api_content:
                    thumb_url = item.get("thumb_url")
                    if thumb_url and thumb_url != "":
                        api_with_thumbs += 1
                        if "claire-marcus.com" in thumb_url:
                            api_claire_marcus += 1
                
                # Get final status via MongoDB if available
                mongodb_total = 0
                mongodb_claire_marcus = 0
                mongodb_with_thumbs = 0
                
                if self.db:
                    media_collection = self.db.media
                    query = {"owner_id": self.user_id, "deleted": {"$ne": True}}
                    
                    all_docs = list(media_collection.find(query))
                    mongodb_total = len(all_docs)
                    
                    for doc in all_docs:
                        thumb_url = doc.get("thumb_url")
                        if thumb_url and thumb_url != "":
                            mongodb_with_thumbs += 1
                            if "claire-marcus.com" in thumb_url:
                                mongodb_claire_marcus += 1
                
                # Calculate success metrics
                api_success_rate = (api_claire_marcus / api_total * 100) if api_total > 0 else 0
                mongodb_success_rate = (mongodb_claire_marcus / mongodb_total * 100) if mongodb_total > 0 else 0
                
                # Determine if we met the objective (44/44 files with claire-marcus.com thumb_url)
                objective_met = (api_claire_marcus >= 44 or mongodb_claire_marcus >= 44)
                
                details = f"API: {api_claire_marcus}/{api_total} fichiers avec thumb_url claire-marcus.com ({api_success_rate:.1f}%)"
                if self.db:
                    details += f", MongoDB: {mongodb_claire_marcus}/{mongodb_total} fichiers avec thumb_url claire-marcus.com ({mongodb_success_rate:.1f}%)"
                
                details += f". Objectif 44/44: {'✅ ATTEINT' if objective_met else '❌ NON ATTEINT'}"
                
                self.log_result(
                    "Vérification finale", 
                    objective_met, 
                    details
                )
                
                return objective_met
            else:
                self.log_result(
                    "Vérification finale", 
                    False, 
                    f"Status: {api_response.status_code}",
                    api_response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Vérification finale", False, error=str(e))
            return False
    
    def run_complete_diagnostic(self):
        """Exécuter le diagnostic complet selon la demande française"""
        print("🎯 DIAGNOSTIC ET CORRECTION COMPLÈTE DU SYSTÈME DE VIGNETTES")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Utilisateur de test: {TEST_EMAIL}")
        print(f"Objectif: 44/44 fichiers avec thumb_url pointant vers claire-marcus.com")
        print("=" * 80)
        print()
        
        # Connect to MongoDB
        mongodb_connected = self.connect_mongodb()
        
        # Run diagnostic steps in sequence
        steps = [
            ("Authentification", self.authenticate),
            ("Analyse thumb_url API", self.analyze_thumb_urls_api),
            ("Analyse thumb_url MongoDB", self.analyze_thumb_urls_mongodb) if mongodb_connected else None,
            ("Génération vignettes manquantes", self.generate_missing_thumbnails),
            ("Mise à jour thumb_url MongoDB", self.update_thumb_urls_mongodb) if mongodb_connected else None,
            ("Test accessibilité vignettes", self.test_thumbnail_accessibility),
            ("Vérification finale", self.final_verification)
        ]
        
        # Filter out None steps
        steps = [step for step in steps if step is not None]
        
        for step_name, step_func in steps:
            print(f"🔄 Exécution: {step_name}")
            try:
                step_func()
            except Exception as e:
                self.log_result(step_name, False, error=str(e))
            print()
        
        # Generate comprehensive summary
        self.generate_summary()
        
        # Close MongoDB connection
        if self.mongo_client:
            self.mongo_client.close()
        
        # Return overall success
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        return success_rate >= 80
    
    def generate_summary(self):
        """Générer un résumé complet des résultats"""
        print("📋 RÉSUMÉ COMPLET DU DIAGNOSTIC")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Tests totaux: {total}")
        print(f"Réussis: {passed}")
        print(f"Échoués: {total - passed}")
        print(f"Taux de réussite: {success_rate:.1f}%")
        print()
        
        print("RÉSULTATS DÉTAILLÉS:")
        print("-" * 40)
        
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   📝 {result['details']}")
            if result['error']:
                print(f"   ⚠️ Erreur: {result['error']}")
            print()
        
        # Summary of key findings
        print("CONCLUSIONS CLÉS:")
        print("-" * 40)
        
        if hasattr(self, 'api_analysis'):
            api = self.api_analysis
            print(f"• API: {api['total_files']} fichiers, {api['claire_marcus_urls']} avec thumb_url claire-marcus.com")
        
        if hasattr(self, 'mongodb_analysis'):
            mongo = self.mongodb_analysis
            print(f"• MongoDB: {mongo['total_docs']} documents, {mongo['claire_marcus_urls']} avec thumb_url claire-marcus.com")
        
        print()
        print("🎯 DIAGNOSTIC TERMINÉ")

if __name__ == "__main__":
    tester = ThumbnailDiagnosticTester()
    success = tester.run_complete_diagnostic()
    
    if success:
        print("✅ Diagnostic global: SUCCÈS")
        exit(0)
    else:
        print("❌ Diagnostic global: ÉCHEC")
        exit(1)