#!/usr/bin/env python3
"""
Diagnostic critique des URLs vs fichiers physiques pour résoudre les vignettes grises
French Review Request: Analyze MongoDB thumb_url vs physical filesystem correspondence

PROBLÈME IDENTIFIÉ: Les URLs en MongoDB ne correspondent pas aux fichiers physiques sur le serveur.

Objectifs:
1. Authentifier avec lperpere@yahoo.fr / L@Reunion974!
2. Analyser la correspondance entre MongoDB et filesystem
3. Récupérer 5 exemples de thumb_url depuis MongoDB
4. Vérifier si les fichiers correspondants existent physiquement sur le serveur
5. Identifier les patterns de différence (UUID complets vs tronqués, extensions, etc.)
6. Diagnostic spécifique pour le fichier visible dans l'UI: chercher "8ee21d73" dans MongoDB
7. Comparer avec le fichier physique "8ee21d73-914d-4a4e-8799-ced03e27ebe0.webp"
8. Identifier la cause du mismatch entre génération d'UUID et stockage
"""

import requests
import json
import os
import pymongo
from urllib.parse import urlparse
import re

# Configuration
BACKEND_URL = "https://social-pub-hub.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials as specified in review request
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

# MongoDB connection (from backend/.env)
MONGO_URL = "mongodb+srv://lperpere:ClaireMarcus2025@cluster0.24k0jzd.mongodb.net/claire_marcus?retryWrites=true&w=majority&appName=Cluster0"

class ThumbnailURLDiagnostic:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.mongo_client = None
        self.db = None
        self.diagnostic_results = []
        
    def log_diagnostic(self, step, success, details="", error=""):
        """Log diagnostic result"""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        result = {
            "step": step,
            "status": status,
            "success": success,
            "details": details,
            "error": error
        }
        self.diagnostic_results.append(result)
        print(f"{status}: {step}")
        if details:
            print(f"   📋 Details: {details}")
        if error:
            print(f"   ❌ Error: {error}")
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
                
                self.log_diagnostic(
                    "Authentification", 
                    True, 
                    f"Connexion réussie avec {TEST_EMAIL}, User ID: {self.user_id}"
                )
                return True
            else:
                self.log_diagnostic(
                    "Authentification", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_diagnostic("Authentification", False, error=str(e))
            return False
    
    def connect_mongodb(self):
        """ÉTAPE 2: Connexion directe à MongoDB pour analyse"""
        print("🗄️ ÉTAPE 2: CONNEXION MONGODB")
        print("=" * 60)
        
        try:
            self.mongo_client = pymongo.MongoClient(MONGO_URL)
            self.db = self.mongo_client.claire_marcus
            
            # Test connection
            server_info = self.mongo_client.server_info()
            
            self.log_diagnostic(
                "Connexion MongoDB", 
                True, 
                f"Connexion réussie à MongoDB. Version: {server_info.get('version', 'unknown')}"
            )
            return True
            
        except Exception as e:
            self.log_diagnostic("Connexion MongoDB", False, error=str(e))
            return False
    
    def analyze_mongodb_thumb_urls(self):
        """ÉTAPE 3: Analyser les thumb_url dans MongoDB - récupérer 5 exemples"""
        print("🔍 ÉTAPE 3: ANALYSE DES THUMB_URL DANS MONGODB")
        print("=" * 60)
        
        try:
            # Get media collection
            media_collection = self.db.media
            
            # Count total documents
            total_docs = media_collection.count_documents({})
            
            # Count documents with thumb_url (handle None values properly)
            with_thumb_url = media_collection.count_documents({
                "thumb_url": {"$ne": None, "$ne": "", "$ne": "None"}
            })
            
            # Count documents with null/None thumb_url
            null_thumb_url = media_collection.count_documents({
                "$or": [
                    {"thumb_url": None},
                    {"thumb_url": ""},
                    {"thumb_url": "None"},
                    {"thumb_url": {"$exists": False}}
                ]
            })
            
            # Get 5 examples of thumb_url (excluding None/null values)
            examples = list(media_collection.find(
                {"thumb_url": {"$ne": None, "$ne": "", "$ne": "None"}}, 
                {"filename": 1, "thumb_url": 1, "url": 1, "_id": 1}
            ).limit(5))
            
            # Analyze patterns
            thumb_url_examples = []
            for doc in examples:
                thumb_url = doc.get("thumb_url", "")
                filename = doc.get("filename", "")
                url = doc.get("url", "")
                doc_id = str(doc.get("_id", ""))
                
                # Skip if thumb_url is None or "None" string
                if not thumb_url or thumb_url == "None":
                    continue
                
                # Extract UUID from thumb_url
                thumb_uuid_match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', thumb_url)
                thumb_uuid = thumb_uuid_match.group(1) if thumb_uuid_match else "NO_UUID"
                
                # Extract UUID from filename
                filename_uuid_match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', filename)
                filename_uuid = filename_uuid_match.group(1) if filename_uuid_match else "NO_UUID"
                
                thumb_url_examples.append({
                    "doc_id": doc_id,
                    "filename": filename,
                    "thumb_url": thumb_url,
                    "url": url,
                    "thumb_uuid": thumb_uuid,
                    "filename_uuid": filename_uuid,
                    "uuid_match": thumb_uuid == filename_uuid
                })
            
            details = f"MongoDB Analysis: {total_docs} documents totaux, {with_thumb_url} avec thumb_url valide, {null_thumb_url} avec thumb_url null/None. "
            details += f"Exemples analysés: {len(thumb_url_examples)}. "
            
            for i, example in enumerate(thumb_url_examples, 1):
                details += f"Ex{i}: {example['filename']} -> thumb_uuid: {example['thumb_uuid'][:8]}..., "
                details += f"filename_uuid: {example['filename_uuid'][:8]}..., match: {example['uuid_match']}. "
            
            self.log_diagnostic(
                "Analyse thumb_url MongoDB", 
                True, 
                details
            )
            
            # Store for next steps
            self.thumb_url_examples = thumb_url_examples
            return True
            
        except Exception as e:
            self.log_diagnostic("Analyse thumb_url MongoDB", False, error=str(e))
            return False
    
    def check_physical_files_existence(self):
        """ÉTAPE 4: Vérifier l'existence physique des fichiers via API content/pending"""
        print("📁 ÉTAPE 4: VÉRIFICATION EXISTENCE FICHIERS PHYSIQUES")
        print("=" * 60)
        
        if not hasattr(self, 'thumb_url_examples'):
            self.log_diagnostic(
                "Vérification fichiers physiques", 
                False, 
                "Pas d'exemples thumb_url disponibles de l'étape précédente"
            )
            return False
        
        try:
            # Get content via API to see what's actually available
            response = self.session.get(f"{API_BASE}/content/pending?limit=50")
            
            if response.status_code == 200:
                data = response.json()
                api_content = data.get("content", [])
                
                # Build list of available files from API
                api_files = {}
                for item in api_content:
                    filename = item.get("filename", "")
                    thumb_url = item.get("thumb_url", "")
                    url = item.get("url", "")
                    if filename:
                        api_files[filename] = {
                            "thumb_url": thumb_url,
                            "url": url,
                            "has_thumb_url": bool(thumb_url and thumb_url != "None")
                        }
                
                # Check correspondence with MongoDB examples
                correspondence_results = []
                for example in self.thumb_url_examples:
                    filename = example["filename"]
                    mongo_thumb_url = example["thumb_url"]
                    
                    # Check if file exists in API response
                    api_file_exists = filename in api_files
                    
                    if api_file_exists:
                        api_thumb_url = api_files[filename]["thumb_url"]
                        thumb_urls_match = mongo_thumb_url == api_thumb_url
                    else:
                        api_thumb_url = "FILE_NOT_IN_API"
                        thumb_urls_match = False
                    
                    correspondence_results.append({
                        "filename": filename,
                        "mongo_thumb_url": mongo_thumb_url,
                        "api_thumb_url": api_thumb_url,
                        "api_file_exists": api_file_exists,
                        "thumb_urls_match": thumb_urls_match
                    })
                
                # Summary
                existing_count = sum(1 for result in correspondence_results if result["api_file_exists"])
                matching_thumbs = sum(1 for result in correspondence_results if result["thumb_urls_match"])
                total_checked = len(correspondence_results)
                
                details = f"Vérification via API: {len(api_files)} fichiers dans API, {existing_count}/{total_checked} exemples MongoDB trouvés dans API, {matching_thumbs} avec thumb_url identiques. "
                
                for i, result in enumerate(correspondence_results, 1):
                    api_status = "✅" if result["api_file_exists"] else "❌"
                    thumb_status = "✅" if result["thumb_urls_match"] else "❌"
                    details += f"Ex{i}: {result['filename']} API:{api_status} Thumb:{thumb_status}. "
                
                self.log_diagnostic(
                    "Vérification fichiers physiques", 
                    existing_count > 0, 
                    details
                )
                
                # Store for next step
                self.correspondence_results = correspondence_results
                self.api_files = api_files
                return True
            else:
                self.log_diagnostic(
                    "Vérification fichiers physiques", 
                    False, 
                    f"API content/pending failed. Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_diagnostic("Vérification fichiers physiques", False, error=str(e))
            return False
    
    def search_specific_file_8ee21d73(self):
        """ÉTAPE 5: Diagnostic spécifique pour "8ee21d73" - chercher dans MongoDB"""
        print("🎯 ÉTAPE 5: DIAGNOSTIC SPÉCIFIQUE FICHIER '8ee21d73'")
        print("=" * 60)
        
        try:
            # Search for documents containing "8ee21d73" in various fields
            media_collection = self.db.media
            
            # Search patterns
            search_patterns = [
                {"filename": {"$regex": "8ee21d73", "$options": "i"}},
                {"thumb_url": {"$regex": "8ee21d73", "$options": "i"}},
                {"url": {"$regex": "8ee21d73", "$options": "i"}},
                {"original_filename": {"$regex": "8ee21d73", "$options": "i"}}
            ]
            
            found_documents = []
            for pattern in search_patterns:
                docs = list(media_collection.find(pattern, {
                    "filename": 1, 
                    "thumb_url": 1, 
                    "url": 1, 
                    "original_filename": 1,
                    "_id": 1
                }))
                found_documents.extend(docs)
            
            # Remove duplicates
            unique_docs = []
            seen_ids = set()
            for doc in found_documents:
                doc_id = str(doc["_id"])
                if doc_id not in seen_ids:
                    unique_docs.append(doc)
                    seen_ids.add(doc_id)
            
            if unique_docs:
                details = f"Trouvé {len(unique_docs)} document(s) contenant '8ee21d73': "
                
                for i, doc in enumerate(unique_docs, 1):
                    filename = doc.get("filename", "")
                    thumb_url = doc.get("thumb_url", "")
                    url = doc.get("url", "")
                    
                    details += f"Doc{i}: filename='{filename}', "
                    details += f"thumb_url='{thumb_url}', "
                    details += f"url='{url}'. "
                
                self.log_diagnostic(
                    "Recherche spécifique '8ee21d73'", 
                    True, 
                    details
                )
                
                # Store for comparison
                self.specific_file_docs = unique_docs
                return True
            else:
                self.log_diagnostic(
                    "Recherche spécifique '8ee21d73'", 
                    False, 
                    "Aucun document trouvé contenant '8ee21d73' dans MongoDB"
                )
                return False
                
        except Exception as e:
            self.log_diagnostic("Recherche spécifique '8ee21d73'", False, error=str(e))
            return False
    
    def compare_with_physical_8ee21d73(self):
        """ÉTAPE 6: Comparer avec le fichier physique "8ee21d73-914d-4a4e-8799-ced03e27ebe0.webp" """
        print("⚖️ ÉTAPE 6: COMPARAISON AVEC FICHIER PHYSIQUE")
        print("=" * 60)
        
        expected_physical_file = "8ee21d73-914d-4a4e-8799-ced03e27ebe0.webp"
        
        try:
            # Check if file exists via API content/pending
            response = self.session.get(f"{API_BASE}/content/pending?limit=100")
            
            if response.status_code == 200:
                data = response.json()
                api_content = data.get("content", [])
                
                # Look for files containing "8ee21d73"
                matching_files = []
                for item in api_content:
                    filename = item.get("filename", "")
                    thumb_url = item.get("thumb_url", "")
                    if "8ee21d73" in filename:
                        matching_files.append({
                            "filename": filename,
                            "thumb_url": thumb_url,
                            "has_thumb_url": bool(thumb_url and thumb_url != "None")
                        })
                
                # Compare with MongoDB data
                if hasattr(self, 'specific_file_docs') and self.specific_file_docs:
                    mongodb_analysis = []
                    
                    for doc in self.specific_file_docs:
                        thumb_url = doc.get("thumb_url", "")
                        filename = doc.get("filename", "")
                        
                        # Extract filename from thumb_url if it exists
                        if thumb_url and thumb_url != "None":
                            parsed_url = urlparse(thumb_url)
                            thumb_filename = os.path.basename(parsed_url.path)
                        else:
                            thumb_filename = "NO_THUMB_URL"
                        
                        # Check if it matches expected physical file
                        matches_physical = thumb_filename == expected_physical_file
                        
                        mongodb_analysis.append({
                            "filename": filename,
                            "thumb_url": thumb_url,
                            "thumb_filename": thumb_filename,
                            "matches_physical": matches_physical
                        })
                    
                    # Summary
                    matching_docs = sum(1 for analysis in mongodb_analysis if analysis["matches_physical"])
                    
                    details = f"Fichiers API contenant '8ee21d73': {len(matching_files)}. "
                    details += f"Documents MongoDB analysés: {len(mongodb_analysis)}. "
                    details += f"Documents pointant vers '{expected_physical_file}': {matching_docs}. "
                    
                    # Show API files
                    for i, api_file in enumerate(matching_files, 1):
                        thumb_status = "✅" if api_file["has_thumb_url"] else "❌"
                        details += f"API{i}: {api_file['filename']} thumb:{thumb_status}. "
                    
                    # Show MongoDB analysis
                    for i, analysis in enumerate(mongodb_analysis, 1):
                        status = "✅" if analysis["matches_physical"] else "❌"
                        details += f"MongoDB{i}: thumb_filename='{analysis['thumb_filename']}' {status}. "
                    
                    # Identify the mismatch pattern
                    if len(matching_files) > 0 and matching_docs == 0:
                        details += "🚨 MISMATCH IDENTIFIÉ: Fichiers existent dans API mais problème avec thumb_url MongoDB. "
                        
                        # Analyze the pattern
                        if mongodb_analysis:
                            for analysis in mongodb_analysis:
                                stored_thumb = analysis["thumb_filename"]
                                mongo_thumb_url = analysis["thumb_url"]
                                
                                if mongo_thumb_url == "None" or not mongo_thumb_url:
                                    details += "CAUSE: thumb_url = None dans MongoDB. "
                                elif "8ee21d73" in stored_thumb and "8ee21d73" in expected_physical_file:
                                    if stored_thumb != expected_physical_file:
                                        details += f"CAUSE: Nom fichier différent - MongoDB: '{stored_thumb}' vs Attendu: '{expected_physical_file}'. "
                    
                    self.log_diagnostic(
                        "Comparaison avec fichier physique", 
                        True, 
                        details
                    )
                    
                    return True
                else:
                    self.log_diagnostic(
                        "Comparaison avec fichier physique", 
                        False, 
                        "Pas de données MongoDB pour la comparaison"
                    )
                    return False
            else:
                self.log_diagnostic(
                    "Comparaison avec fichier physique", 
                    False, 
                    f"API content/pending failed. Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_diagnostic("Comparaison avec fichier physique", False, error=str(e))
            return False
    
    def identify_mismatch_cause(self):
        """ÉTAPE 7: Identifier la cause du mismatch entre génération d'UUID et stockage"""
        print("🔬 ÉTAPE 7: IDENTIFICATION DE LA CAUSE DU MISMATCH")
        print("=" * 60)
        
        try:
            # Analyze all collected data to identify patterns
            analysis_summary = {
                "total_examples_analyzed": len(getattr(self, 'thumb_url_examples', [])),
                "uuid_mismatches": 0,
                "truncated_uuids": 0,
                "extension_mismatches": 0,
                "domain_issues": 0,
                "patterns_identified": []
            }
            
            if hasattr(self, 'thumb_url_examples'):
                for example in self.thumb_url_examples:
                    # Check UUID matching
                    if not example["uuid_match"]:
                        analysis_summary["uuid_mismatches"] += 1
                    
                    # Check for truncated UUIDs
                    thumb_uuid = example["thumb_uuid"]
                    filename_uuid = example["filename_uuid"]
                    
                    if thumb_uuid != "NO_UUID" and filename_uuid != "NO_UUID":
                        if len(thumb_uuid) < len(filename_uuid):
                            analysis_summary["truncated_uuids"] += 1
                    
                    # Check domain issues
                    thumb_url = example["thumb_url"]
                    if "claire-marcus.com" not in thumb_url and "libfusion.preview.emergentagent.com" not in thumb_url:
                        analysis_summary["domain_issues"] += 1
            
            # Identify patterns
            if analysis_summary["uuid_mismatches"] > 0:
                analysis_summary["patterns_identified"].append("UUID mismatch entre thumb_url et filename")
            
            if analysis_summary["truncated_uuids"] > 0:
                analysis_summary["patterns_identified"].append("UUIDs tronqués dans thumb_url")
            
            if analysis_summary["domain_issues"] > 0:
                analysis_summary["patterns_identified"].append("Problèmes de domaine dans thumb_url")
            
            # Check correspondence results
            if hasattr(self, 'correspondence_results'):
                missing_files = sum(1 for result in self.correspondence_results if not result["physical_exists"])
                if missing_files > 0:
                    analysis_summary["patterns_identified"].append(f"{missing_files} fichiers physiques manquants")
            
            # Generate detailed analysis
            details = f"ANALYSE COMPLÈTE DES CAUSES: "
            details += f"{analysis_summary['total_examples_analyzed']} exemples analysés. "
            details += f"UUID mismatches: {analysis_summary['uuid_mismatches']}. "
            details += f"UUIDs tronqués: {analysis_summary['truncated_uuids']}. "
            details += f"Problèmes de domaine: {analysis_summary['domain_issues']}. "
            
            if analysis_summary["patterns_identified"]:
                details += f"PATTERNS IDENTIFIÉS: {', '.join(analysis_summary['patterns_identified'])}. "
                
                # Provide specific recommendations
                details += "RECOMMANDATIONS: "
                if "UUID mismatch" in str(analysis_summary["patterns_identified"]):
                    details += "(1) Vérifier la génération d'UUID lors de l'upload vs stockage thumb_url. "
                if "UUIDs tronqués" in str(analysis_summary["patterns_identified"]):
                    details += "(2) Corriger la troncature d'UUID dans la génération de thumb_url. "
                if "fichiers physiques manquants" in str(analysis_summary["patterns_identified"]):
                    details += "(3) Régénérer les vignettes manquantes avec les bons noms de fichiers. "
            else:
                details += "AUCUN PATTERN CLAIR IDENTIFIÉ - Investigation supplémentaire requise. "
            
            self.log_diagnostic(
                "Identification cause mismatch", 
                len(analysis_summary["patterns_identified"]) > 0, 
                details
            )
            
            # Store final analysis
            self.final_analysis = analysis_summary
            return True
            
        except Exception as e:
            self.log_diagnostic("Identification cause mismatch", False, error=str(e))
            return False
    
    def run_diagnostic(self):
        """Exécuter le diagnostic complet selon la demande française"""
        print("🇫🇷 DIAGNOSTIC CRITIQUE DES URLs vs FICHIERS PHYSIQUES")
        print("=" * 80)
        print("PROBLÈME: Les URLs en MongoDB ne correspondent pas aux fichiers physiques")
        print("OBJECTIF: Identifier la cause du mismatch entre génération d'UUID et stockage")
        print("=" * 80)
        print()
        
        # Run diagnostic steps in sequence
        steps = [
            self.authenticate,
            self.connect_mongodb,
            self.analyze_mongodb_thumb_urls,
            self.check_physical_files_existence,
            self.search_specific_file_8ee21d73,
            self.compare_with_physical_8ee21d73,
            self.identify_mismatch_cause
        ]
        
        for step in steps:
            if not step():
                print("❌ Étape échouée, continuation avec les étapes restantes...")
            print()
        
        # Final summary
        print("📋 RÉSUMÉ DU DIAGNOSTIC")
        print("=" * 60)
        
        passed = sum(1 for result in self.diagnostic_results if result["success"])
        total = len(self.diagnostic_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Étapes totales: {total}")
        print(f"Réussies: {passed}")
        print(f"Échouées: {total - passed}")
        print(f"Taux de réussite: {success_rate:.1f}%")
        print()
        
        # Detailed results
        print("RÉSULTATS DÉTAILLÉS:")
        print("-" * 40)
        for result in self.diagnostic_results:
            print(f"{result['status']}: {result['step']}")
            if result['details']:
                print(f"   📋 {result['details']}")
            if result['error']:
                print(f"   ❌ {result['error']}")
            print()
        
        # Final analysis summary
        if hasattr(self, 'final_analysis'):
            print("🔬 ANALYSE FINALE:")
            print("-" * 40)
            analysis = self.final_analysis
            print(f"• Exemples analysés: {analysis['total_examples_analyzed']}")
            print(f"• UUID mismatches: {analysis['uuid_mismatches']}")
            print(f"• UUIDs tronqués: {analysis['truncated_uuids']}")
            print(f"• Problèmes de domaine: {analysis['domain_issues']}")
            print(f"• Patterns identifiés: {len(analysis['patterns_identified'])}")
            
            if analysis['patterns_identified']:
                print("\n🎯 CAUSES IDENTIFIÉES:")
                for i, pattern in enumerate(analysis['patterns_identified'], 1):
                    print(f"   {i}. {pattern}")
        
        print()
        print("🎯 DIAGNOSTIC TERMINÉ")
        
        # Close MongoDB connection
        if self.mongo_client:
            self.mongo_client.close()
        
        return success_rate >= 70

if __name__ == "__main__":
    diagnostic = ThumbnailURLDiagnostic()
    success = diagnostic.run_diagnostic()
    
    if success:
        print("✅ Diagnostic global: SUCCÈS")
        exit(0)
    else:
        print("❌ Diagnostic global: ÉCHEC")
        exit(1)