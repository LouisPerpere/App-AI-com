#!/usr/bin/env python3
"""
Diagnostic des vignettes manquantes - Test spécialisé
Test spécifique pour la review française: vérification des thumb_url en base de données
"""

import requests
import json
import os
import time
from urllib.parse import urlparse

# Configuration
BACKEND_URL = "https://libfusion.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Credentials as specified in review request
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class ThumbnailDiagnosticTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.test_results = []
        self.thumb_url_examples = []
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
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
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()
    
    def authenticate(self):
        """Étape 1: Authentifier avec lperpere@yahoo.fr / L@Reunion974!"""
        print("🔐 ÉTAPE 1: Authentification")
        print("=" * 50)
        
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
                    f"Connexion réussie: {TEST_EMAIL}, User ID: {self.user_id}"
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
    
    def test_content_pending_api(self):
        """Étape 2: Tester GET /api/content/pending pour examiner les thumb_url"""
        print("📋 ÉTAPE 2: Test GET /api/content/pending")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{API_BASE}/content/pending?limit=50")
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                total = data.get("total", 0)
                
                # Analyze thumb_url patterns
                thumb_url_analysis = {
                    "total_files": len(content),
                    "with_thumb_url": 0,
                    "without_thumb_url": 0,
                    "absolute_urls": 0,
                    "relative_urls": 0,
                    "webp_extensions": 0,
                    "other_extensions": 0,
                    "examples": []
                }
                
                for item in content:
                    thumb_url = item.get("thumb_url")
                    filename = item.get("filename", "unknown")
                    file_id = item.get("id", "unknown")
                    
                    if thumb_url:
                        thumb_url_analysis["with_thumb_url"] += 1
                        
                        # Check if absolute or relative URL
                        if thumb_url.startswith("http"):
                            thumb_url_analysis["absolute_urls"] += 1
                        else:
                            thumb_url_analysis["relative_urls"] += 1
                        
                        # Check extension
                        if thumb_url.endswith(".webp"):
                            thumb_url_analysis["webp_extensions"] += 1
                        else:
                            thumb_url_analysis["other_extensions"] += 1
                        
                        # Store examples for detailed analysis
                        if len(thumb_url_analysis["examples"]) < 5:
                            thumb_url_analysis["examples"].append({
                                "file_id": file_id,
                                "filename": filename,
                                "thumb_url": thumb_url,
                                "is_absolute": thumb_url.startswith("http"),
                                "extension": thumb_url.split(".")[-1] if "." in thumb_url else "none"
                            })
                    else:
                        thumb_url_analysis["without_thumb_url"] += 1
                
                # Store for later analysis
                self.thumb_url_examples = thumb_url_analysis["examples"]
                
                details = f"""Analyse des thumb_url:
- Total fichiers: {thumb_url_analysis['total_files']}
- Avec thumb_url: {thumb_url_analysis['with_thumb_url']}
- Sans thumb_url: {thumb_url_analysis['without_thumb_url']}
- URLs absolues: {thumb_url_analysis['absolute_urls']}
- URLs relatives: {thumb_url_analysis['relative_urls']}
- Extensions .webp: {thumb_url_analysis['webp_extensions']}
- Autres extensions: {thumb_url_analysis['other_extensions']}"""
                
                self.log_result(
                    "GET /api/content/pending", 
                    True, 
                    details
                )
                
                # Log examples for detailed analysis
                print("📝 EXEMPLES DE THUMB_URL:")
                for i, example in enumerate(thumb_url_analysis["examples"], 1):
                    print(f"   {i}. File: {example['filename']}")
                    print(f"      ID: {example['file_id']}")
                    print(f"      thumb_url: {example['thumb_url']}")
                    print(f"      Type: {'Absolue' if example['is_absolute'] else 'Relative'}")
                    print(f"      Extension: {example['extension']}")
                    print()
                
                return True
            else:
                self.log_result(
                    "GET /api/content/pending", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("GET /api/content/pending", False, error=str(e))
            return False
    
    def test_thumbnails_status_api(self):
        """Étape 4: Tester GET /api/content/thumbnails/status"""
        print("📊 ÉTAPE 4: Test GET /api/content/thumbnails/status")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{API_BASE}/content/thumbnails/status")
            
            if response.status_code == 200:
                data = response.json()
                
                details = f"""Statut des vignettes:
- Total fichiers: {data.get('total_files', 0)}
- Avec vignettes: {data.get('with_thumbnails', 0)}
- Vignettes manquantes: {data.get('missing_thumbnails', 0)}
- Pourcentage complet: {data.get('completion_percentage', 0)}%"""
                
                self.log_result(
                    "GET /api/content/thumbnails/status", 
                    True, 
                    details
                )
                return True
            else:
                self.log_result(
                    "GET /api/content/thumbnails/status", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("GET /api/content/thumbnails/status", False, error=str(e))
            return False
    
    def analyze_thumb_url_patterns(self):
        """Étape 5: Analyser 3-5 exemples de thumb_url pour identifier le pattern"""
        print("🔍 ÉTAPE 5: Analyse des patterns d'URL")
        print("=" * 50)
        
        if not self.thumb_url_examples:
            self.log_result(
                "Analyse des patterns d'URL", 
                False, 
                "Aucun exemple de thumb_url disponible"
            )
            return False
        
        try:
            pattern_analysis = {
                "consistent_domain": True,
                "consistent_path": True,
                "consistent_extension": True,
                "domain_found": None,
                "path_pattern": None,
                "extension_found": None,
                "issues": []
            }
            
            # Analyze patterns
            domains = set()
            paths = set()
            extensions = set()
            
            for example in self.thumb_url_examples:
                thumb_url = example["thumb_url"]
                
                if example["is_absolute"]:
                    parsed = urlparse(thumb_url)
                    domains.add(parsed.netloc)
                    path_parts = parsed.path.split("/")
                    if len(path_parts) >= 3:
                        paths.add("/".join(path_parts[:-1]))  # Path without filename
                else:
                    # Relative URL
                    domains.add("RELATIVE")
                    path_parts = thumb_url.split("/")
                    if len(path_parts) >= 2:
                        paths.add("/".join(path_parts[:-1]))  # Path without filename
                
                extensions.add(example["extension"])
            
            # Check consistency
            if len(domains) > 1:
                pattern_analysis["consistent_domain"] = False
                pattern_analysis["issues"].append(f"Domaines incohérents: {list(domains)}")
            else:
                pattern_analysis["domain_found"] = list(domains)[0]
            
            if len(paths) > 1:
                pattern_analysis["consistent_path"] = False
                pattern_analysis["issues"].append(f"Chemins incohérents: {list(paths)}")
            else:
                pattern_analysis["path_pattern"] = list(paths)[0] if paths else "N/A"
            
            if len(extensions) > 1:
                pattern_analysis["consistent_extension"] = False
                pattern_analysis["issues"].append(f"Extensions incohérentes: {list(extensions)}")
            else:
                pattern_analysis["extension_found"] = list(extensions)[0] if extensions else "N/A"
            
            # Determine if patterns are correct
            is_correct_pattern = (
                pattern_analysis["consistent_domain"] and
                pattern_analysis["consistent_path"] and
                pattern_analysis["consistent_extension"] and
                pattern_analysis["extension_found"] == "webp"
            )
            
            details = f"""Analyse des patterns:
- Domaine cohérent: {pattern_analysis['consistent_domain']} ({pattern_analysis['domain_found']})
- Chemin cohérent: {pattern_analysis['consistent_path']} ({pattern_analysis['path_pattern']})
- Extension cohérente: {pattern_analysis['consistent_extension']} ({pattern_analysis['extension_found']})
- Pattern correct: {is_correct_pattern}"""
            
            if pattern_analysis["issues"]:
                details += f"\n- Problèmes détectés: {'; '.join(pattern_analysis['issues'])}"
            
            self.log_result(
                "Analyse des patterns d'URL", 
                is_correct_pattern, 
                details
            )
            
            return is_correct_pattern
            
        except Exception as e:
            self.log_result("Analyse des patterns d'URL", False, error=str(e))
            return False
    
    def test_thumb_url_accessibility(self):
        """Étape 6: Tester l'accessibilité des thumb_url"""
        print("🌐 ÉTAPE 6: Test d'accessibilité des thumb_url")
        print("=" * 50)
        
        if not self.thumb_url_examples:
            self.log_result(
                "Test d'accessibilité", 
                False, 
                "Aucun exemple de thumb_url disponible"
            )
            return False
        
        try:
            accessibility_results = {
                "total_tested": 0,
                "accessible": 0,
                "not_accessible": 0,
                "details": []
            }
            
            for example in self.thumb_url_examples[:3]:  # Test first 3 examples
                thumb_url = example["thumb_url"]
                filename = example["filename"]
                
                # Make URL absolute if relative
                if not thumb_url.startswith("http"):
                    if thumb_url.startswith("/"):
                        test_url = f"{BACKEND_URL}{thumb_url}"
                    else:
                        test_url = f"{BACKEND_URL}/{thumb_url}"
                else:
                    test_url = thumb_url
                
                accessibility_results["total_tested"] += 1
                
                try:
                    response = requests.get(test_url, timeout=10)
                    
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '')
                        is_image = 'image' in content_type.lower()
                        
                        accessibility_results["accessible"] += 1
                        accessibility_results["details"].append({
                            "filename": filename,
                            "url": test_url,
                            "status": "accessible",
                            "content_type": content_type,
                            "is_image": is_image
                        })
                    else:
                        accessibility_results["not_accessible"] += 1
                        accessibility_results["details"].append({
                            "filename": filename,
                            "url": test_url,
                            "status": f"not_accessible ({response.status_code})",
                            "content_type": None,
                            "is_image": False
                        })
                        
                except Exception as url_error:
                    accessibility_results["not_accessible"] += 1
                    accessibility_results["details"].append({
                        "filename": filename,
                        "url": test_url,
                        "status": f"error ({str(url_error)})",
                        "content_type": None,
                        "is_image": False
                    })
            
            success_rate = (accessibility_results["accessible"] / accessibility_results["total_tested"] * 100) if accessibility_results["total_tested"] > 0 else 0
            
            details = f"""Test d'accessibilité:
- Total testé: {accessibility_results['total_tested']}
- Accessibles: {accessibility_results['accessible']}
- Non accessibles: {accessibility_results['not_accessible']}
- Taux de succès: {success_rate:.1f}%"""
            
            # Add detailed results
            for detail in accessibility_results["details"]:
                details += f"\n- {detail['filename']}: {detail['status']}"
                if detail['content_type']:
                    details += f" (Type: {detail['content_type']})"
            
            is_success = success_rate >= 80  # Consider success if 80% or more are accessible
            
            self.log_result(
                "Test d'accessibilité des thumb_url", 
                is_success, 
                details
            )
            
            return is_success
            
        except Exception as e:
            self.log_result("Test d'accessibilité des thumb_url", False, error=str(e))
            return False
    
    def run_diagnostic(self):
        """Exécuter le diagnostic complet des vignettes"""
        print("🔍 DIAGNOSTIC DES VIGNETTES MANQUANTES")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Utilisateur de test: {TEST_EMAIL}")
        print("Objectif: Vérifier si les thumb_url stockées en MongoDB sont correctes")
        print("=" * 60)
        print()
        
        # Run diagnostic steps
        steps = [
            self.authenticate,
            self.test_content_pending_api,
            self.test_thumbnails_status_api,
            self.analyze_thumb_url_patterns,
            self.test_thumb_url_accessibility
        ]
        
        for step in steps:
            if not step():
                print("⚠️ Étape échouée, continuation du diagnostic...")
            print()
        
        # Summary
        print("📋 RÉSUMÉ DU DIAGNOSTIC")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total étapes: {total}")
        print(f"Réussies: {passed}")
        print(f"Échouées: {total - passed}")
        print(f"Taux de réussite: {success_rate:.1f}%")
        print()
        
        # Detailed results
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
            if result['error']:
                print(f"   Erreur: {result['error']}")
        
        print()
        print("🎯 DIAGNOSTIC DES VIGNETTES TERMINÉ")
        
        # Conclusions
        print("\n📝 CONCLUSIONS:")
        if success_rate >= 80:
            print("✅ Les thumb_url en base de données semblent correctes")
        else:
            print("❌ Des problèmes ont été détectés avec les thumb_url")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = ThumbnailDiagnosticTester()
    success = tester.run_diagnostic()
    
    if success:
        print("\n✅ Diagnostic global: SUCCÈS")
        exit(0)
    else:
        print("\n❌ Diagnostic global: PROBLÈMES DÉTECTÉS")
        exit(1)