#!/usr/bin/env python3
"""
Test critique pour récupération des données d'image base64 depuis MongoDB
Selon la demande française: Tous les proxies d'images sont cassés, besoin de servir directement depuis base64
"""

import requests
import json
import os
import time
import base64
from io import BytesIO
from PIL import Image

# Configuration selon la review française
BACKEND_URL = "https://post-validator.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Credentials spécifiés dans la review
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class ImageBase64Tester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.test_results = []
        
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
        """Authentifier avec lperpere@yahoo.fr / L@Reunion974!"""
        print("🔐 ÉTAPE 1: Authentification avec credentials spécifiés")
        
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
                    "Authentication avec lperpere@yahoo.fr",
                    True,
                    f"User ID: {self.user_id}, Token obtenu"
                )
                return True
            else:
                self.log_result(
                    "Authentication avec lperpere@yahoo.fr",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Authentication avec lperpere@yahoo.fr",
                False,
                "",
                str(e)
            )
            return False
    
    def analyze_content_pending(self):
        """Analyser GET /api/content/pending pour vérifier données base64"""
        print("🔍 ÉTAPE 2: Analyse des données base64 dans /api/content/pending")
        
        try:
            response = self.session.get(f"{API_BASE}/content/pending?limit=10")
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                total = data.get("total", 0)
                
                self.log_result(
                    "GET /api/content/pending accessible",
                    True,
                    f"Total files: {total}, Loaded: {len(content)}"
                )
                
                # Analyser la structure des données
                base64_analysis = {
                    "files_with_file_data": 0,
                    "files_with_thumbnail_data": 0,
                    "files_with_url": 0,
                    "files_with_thumb_url": 0,
                    "total_files": len(content)
                }
                
                sample_files = []
                
                for i, file_item in enumerate(content[:5]):  # Analyser les 5 premiers
                    file_analysis = {
                        "id": file_item.get("id"),
                        "filename": file_item.get("filename"),
                        "file_type": file_item.get("file_type"),
                        "has_file_data": "file_data" in file_item and file_item["file_data"] is not None,
                        "has_thumbnail_data": "thumbnail_data" in file_item and file_item["thumbnail_data"] is not None,
                        "has_url": "url" in file_item and file_item["url"] is not None,
                        "has_thumb_url": "thumb_url" in file_item and file_item["thumb_url"] is not None,
                        "url": file_item.get("url"),
                        "thumb_url": file_item.get("thumb_url")
                    }
                    
                    if file_analysis["has_file_data"]:
                        base64_analysis["files_with_file_data"] += 1
                        # Vérifier si c'est vraiment du base64 valide
                        try:
                            file_data = file_item["file_data"]
                            if isinstance(file_data, str) and len(file_data) > 100:
                                base64.b64decode(file_data[:100])  # Test les premiers 100 chars
                                file_analysis["file_data_valid"] = True
                                file_analysis["file_data_size"] = len(file_data)
                            else:
                                file_analysis["file_data_valid"] = False
                        except:
                            file_analysis["file_data_valid"] = False
                    
                    if file_analysis["has_thumbnail_data"]:
                        base64_analysis["files_with_thumbnail_data"] += 1
                        # Vérifier si c'est vraiment du base64 valide
                        try:
                            thumb_data = file_item["thumbnail_data"]
                            if isinstance(thumb_data, str) and len(thumb_data) > 100:
                                base64.b64decode(thumb_data[:100])  # Test les premiers 100 chars
                                file_analysis["thumbnail_data_valid"] = True
                                file_analysis["thumbnail_data_size"] = len(thumb_data)
                            else:
                                file_analysis["thumbnail_data_valid"] = False
                        except:
                            file_analysis["thumbnail_data_valid"] = False
                    
                    if file_analysis["has_url"]:
                        base64_analysis["files_with_url"] += 1
                    
                    if file_analysis["has_thumb_url"]:
                        base64_analysis["files_with_thumb_url"] += 1
                    
                    sample_files.append(file_analysis)
                
                # Compter tous les fichiers
                for file_item in content:
                    if "file_data" in file_item and file_item["file_data"] is not None:
                        base64_analysis["files_with_file_data"] += 1
                    if "thumbnail_data" in file_item and file_item["thumbnail_data"] is not None:
                        base64_analysis["files_with_thumbnail_data"] += 1
                    if "url" in file_item and file_item["url"] is not None:
                        base64_analysis["files_with_url"] += 1
                    if "thumb_url" in file_item and file_item["thumb_url"] is not None:
                        base64_analysis["files_with_thumb_url"] += 1
                
                self.log_result(
                    "Analyse des données base64",
                    True,
                    f"Files avec file_data: {base64_analysis['files_with_file_data']}, "
                    f"Files avec thumbnail_data: {base64_analysis['files_with_thumbnail_data']}, "
                    f"Files avec URL: {base64_analysis['files_with_url']}, "
                    f"Files avec thumb_url: {base64_analysis['files_with_thumb_url']}"
                )
                
                # Afficher les détails des fichiers échantillons
                print("\n📋 ANALYSE DÉTAILLÉE DES FICHIERS ÉCHANTILLONS:")
                for i, file_analysis in enumerate(sample_files):
                    print(f"\nFichier {i+1}: {file_analysis['filename']}")
                    print(f"  - ID: {file_analysis['id']}")
                    print(f"  - Type: {file_analysis['file_type']}")
                    print(f"  - file_data disponible: {file_analysis['has_file_data']}")
                    if file_analysis['has_file_data']:
                        print(f"    - file_data valide: {file_analysis.get('file_data_valid', 'N/A')}")
                        print(f"    - file_data taille: {file_analysis.get('file_data_size', 'N/A')} chars")
                    print(f"  - thumbnail_data disponible: {file_analysis['has_thumbnail_data']}")
                    if file_analysis['has_thumbnail_data']:
                        print(f"    - thumbnail_data valide: {file_analysis.get('thumbnail_data_valid', 'N/A')}")
                        print(f"    - thumbnail_data taille: {file_analysis.get('thumbnail_data_size', 'N/A')} chars")
                    print(f"  - URL: {file_analysis['url']}")
                    print(f"  - thumb_url: {file_analysis['thumb_url']}")
                
                return base64_analysis, sample_files
                
            else:
                self.log_result(
                    "GET /api/content/pending accessible",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return None, None
                
        except Exception as e:
            self.log_result(
                "Analyse des données base64",
                False,
                "",
                str(e)
            )
            return None, None
    
    def test_base64_image_conversion(self, sample_files):
        """Tester si les données base64 peuvent servir d'images de secours"""
        print("🖼️ ÉTAPE 3: Test de conversion base64 vers images")
        
        if not sample_files:
            self.log_result(
                "Test conversion base64",
                False,
                "",
                "Aucun fichier échantillon disponible"
            )
            return False
        
        successful_conversions = 0
        total_attempts = 0
        
        for file_analysis in sample_files:
            if file_analysis.get('has_file_data') and file_analysis.get('file_data_valid'):
                total_attempts += 1
                
                try:
                    # Récupérer les données base64 du fichier
                    response = self.session.get(f"{API_BASE}/content/pending?limit=50")
                    if response.status_code == 200:
                        content = response.json().get("content", [])
                        target_file = None
                        
                        for file_item in content:
                            if file_item.get("id") == file_analysis["id"]:
                                target_file = file_item
                                break
                        
                        if target_file and target_file.get("file_data"):
                            # Tenter de décoder et convertir en image
                            file_data = target_file["file_data"]
                            image_bytes = base64.b64decode(file_data)
                            
                            # Vérifier que c'est une image valide
                            image = Image.open(BytesIO(image_bytes))
                            width, height = image.size
                            format_img = image.format
                            
                            successful_conversions += 1
                            
                            self.log_result(
                                f"Conversion base64 - {file_analysis['filename']}",
                                True,
                                f"Image {width}x{height}, Format: {format_img}, Taille: {len(image_bytes)} bytes"
                            )
                        else:
                            self.log_result(
                                f"Conversion base64 - {file_analysis['filename']}",
                                False,
                                "",
                                "file_data non trouvé dans la réponse API"
                            )
                    
                except Exception as e:
                    self.log_result(
                        f"Conversion base64 - {file_analysis['filename']}",
                        False,
                        "",
                        str(e)
                    )
        
        # Test des thumbnail_data aussi
        for file_analysis in sample_files:
            if file_analysis.get('has_thumbnail_data') and file_analysis.get('thumbnail_data_valid'):
                total_attempts += 1
                
                try:
                    # Récupérer les données base64 du fichier
                    response = self.session.get(f"{API_BASE}/content/pending?limit=50")
                    if response.status_code == 200:
                        content = response.json().get("content", [])
                        target_file = None
                        
                        for file_item in content:
                            if file_item.get("id") == file_analysis["id"]:
                                target_file = file_item
                                break
                        
                        if target_file and target_file.get("thumbnail_data"):
                            # Tenter de décoder et convertir en image
                            thumb_data = target_file["thumbnail_data"]
                            image_bytes = base64.b64decode(thumb_data)
                            
                            # Vérifier que c'est une image valide
                            image = Image.open(BytesIO(image_bytes))
                            width, height = image.size
                            format_img = image.format
                            
                            successful_conversions += 1
                            
                            self.log_result(
                                f"Conversion thumbnail base64 - {file_analysis['filename']}",
                                True,
                                f"Thumbnail {width}x{height}, Format: {format_img}, Taille: {len(image_bytes)} bytes"
                            )
                        else:
                            self.log_result(
                                f"Conversion thumbnail base64 - {file_analysis['filename']}",
                                False,
                                "",
                                "thumbnail_data non trouvé dans la réponse API"
                            )
                    
                except Exception as e:
                    self.log_result(
                        f"Conversion thumbnail base64 - {file_analysis['filename']}",
                        False,
                        "",
                        str(e)
                    )
        
        success_rate = (successful_conversions / total_attempts * 100) if total_attempts > 0 else 0
        
        self.log_result(
            "Test global conversion base64",
            successful_conversions > 0,
            f"Conversions réussies: {successful_conversions}/{total_attempts} ({success_rate:.1f}%)"
        )
        
        return successful_conversions > 0
    
    def test_proxy_accessibility(self, sample_files):
        """Tester l'accessibilité des URLs proxy pour confirmer le problème"""
        print("🌐 ÉTAPE 4: Test d'accessibilité des proxies d'images")
        
        if not sample_files:
            self.log_result(
                "Test accessibilité proxies",
                False,
                "",
                "Aucun fichier échantillon disponible"
            )
            return
        
        proxy_domains = ["claire-marcus.com", "libfusion.preview.emergentagent.com"]
        proxy_results = {}
        
        for domain in proxy_domains:
            proxy_results[domain] = {"accessible": 0, "broken": 0, "total": 0}
        
        for file_analysis in sample_files:
            # Tester les URLs principales
            if file_analysis.get('has_url') and file_analysis.get('url'):
                url = file_analysis['url']
                domain = None
                
                for d in proxy_domains:
                    if d in url:
                        domain = d
                        break
                
                if domain:
                    proxy_results[domain]["total"] += 1
                    
                    try:
                        # Test avec timeout court
                        response = requests.get(url, timeout=10)
                        if response.status_code == 200 and 'image' in response.headers.get('content-type', ''):
                            proxy_results[domain]["accessible"] += 1
                            self.log_result(
                                f"Proxy URL accessible - {file_analysis['filename']}",
                                True,
                                f"URL: {url}, Content-Type: {response.headers.get('content-type')}"
                            )
                        else:
                            proxy_results[domain]["broken"] += 1
                            self.log_result(
                                f"Proxy URL cassée - {file_analysis['filename']}",
                                False,
                                f"Status: {response.status_code}, Content-Type: {response.headers.get('content-type')}",
                                f"URL: {url}"
                            )
                    except Exception as e:
                        proxy_results[domain]["broken"] += 1
                        self.log_result(
                            f"Proxy URL erreur - {file_analysis['filename']}",
                            False,
                            "",
                            f"URL: {url}, Erreur: {str(e)}"
                        )
            
            # Tester les thumb_urls
            if file_analysis.get('has_thumb_url') and file_analysis.get('thumb_url'):
                url = file_analysis['thumb_url']
                domain = None
                
                for d in proxy_domains:
                    if d in url:
                        domain = d
                        break
                
                if domain:
                    proxy_results[domain]["total"] += 1
                    
                    try:
                        # Test avec timeout court
                        response = requests.get(url, timeout=10)
                        if response.status_code == 200 and 'image' in response.headers.get('content-type', ''):
                            proxy_results[domain]["accessible"] += 1
                            self.log_result(
                                f"Proxy thumb_url accessible - {file_analysis['filename']}",
                                True,
                                f"URL: {url}, Content-Type: {response.headers.get('content-type')}"
                            )
                        else:
                            proxy_results[domain]["broken"] += 1
                            self.log_result(
                                f"Proxy thumb_url cassée - {file_analysis['filename']}",
                                False,
                                f"Status: {response.status_code}, Content-Type: {response.headers.get('content-type')}",
                                f"URL: {url}"
                            )
                    except Exception as e:
                        proxy_results[domain]["broken"] += 1
                        self.log_result(
                            f"Proxy thumb_url erreur - {file_analysis['filename']}",
                            False,
                            "",
                            f"URL: {url}, Erreur: {str(e)}"
                        )
        
        # Résumé des résultats proxy
        print("\n📊 RÉSUMÉ ACCESSIBILITÉ PROXIES:")
        for domain, results in proxy_results.items():
            total = results["total"]
            accessible = results["accessible"]
            broken = results["broken"]
            success_rate = (accessible / total * 100) if total > 0 else 0
            
            print(f"\n{domain}:")
            print(f"  - Total URLs testées: {total}")
            print(f"  - URLs accessibles: {accessible}")
            print(f"  - URLs cassées: {broken}")
            print(f"  - Taux de succès: {success_rate:.1f}%")
            
            self.log_result(
                f"Proxy {domain} fonctionnel",
                success_rate > 50,  # Considérer comme fonctionnel si > 50% marchent
                f"Taux de succès: {success_rate:.1f}% ({accessible}/{total})"
            )
    
    def generate_solution_recommendations(self, base64_analysis, sample_files):
        """Générer des recommandations de solution"""
        print("💡 ÉTAPE 5: Génération des recommandations de solution")
        
        if not base64_analysis:
            self.log_result(
                "Génération recommandations",
                False,
                "",
                "Pas de données d'analyse disponibles"
            )
            return
        
        recommendations = []
        
        # Analyser la disponibilité des données base64
        files_with_base64 = base64_analysis["files_with_file_data"] + base64_analysis["files_with_thumbnail_data"]
        total_files = base64_analysis["total_files"]
        
        if files_with_base64 > 0:
            base64_coverage = (files_with_base64 / total_files * 100) if total_files > 0 else 0
            
            if base64_coverage > 80:
                recommendations.append({
                    "priority": "HIGH",
                    "solution": "UTILISER BASE64 EXISTANT",
                    "description": f"Excellent! {base64_coverage:.1f}% des fichiers ont déjà des données base64. Modifier le frontend pour utiliser file_data/thumbnail_data au lieu des URLs proxy.",
                    "implementation": "Modifier ContentThumbnail.js pour utiliser data:image/jpeg;base64,{file_data} quand les URLs proxy échouent."
                })
            elif base64_coverage > 50:
                recommendations.append({
                    "priority": "MEDIUM",
                    "solution": "COMPLÉTER BASE64 MANQUANT",
                    "description": f"{base64_coverage:.1f}% des fichiers ont des données base64. Générer les données manquantes pour les autres fichiers.",
                    "implementation": "Créer un endpoint /api/content/generate-base64 pour générer les données manquantes."
                })
            else:
                recommendations.append({
                    "priority": "LOW",
                    "solution": "GÉNÉRER TOUTES DONNÉES BASE64",
                    "description": f"Seulement {base64_coverage:.1f}% des fichiers ont des données base64. Générer toutes les données base64 manquantes.",
                    "implementation": "Script de migration pour générer file_data et thumbnail_data pour tous les fichiers."
                })
        else:
            recommendations.append({
                "priority": "CRITICAL",
                "solution": "CRÉER SYSTÈME BASE64",
                "description": "Aucune donnée base64 disponible. Créer un système complet de génération et stockage base64.",
                "implementation": "Implémenter génération base64 à l'upload + migration des fichiers existants."
            })
        
        # Recommandations spécifiques selon les URLs proxy
        urls_working = base64_analysis["files_with_url"] + base64_analysis["files_with_thumb_url"]
        if urls_working == 0:
            recommendations.append({
                "priority": "CRITICAL",
                "solution": "FALLBACK BASE64 IMMÉDIAT",
                "description": "Aucune URL proxy disponible. Implémenter fallback base64 immédiatement.",
                "implementation": "Frontend doit utiliser base64 comme source principale, pas comme fallback."
            })
        
        print("\n🎯 RECOMMANDATIONS DE SOLUTION:")
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. [{rec['priority']}] {rec['solution']}")
            print(f"   Description: {rec['description']}")
            print(f"   Implémentation: {rec['implementation']}")
        
        self.log_result(
            "Recommandations générées",
            True,
            f"{len(recommendations)} recommandations créées"
        )
        
        return recommendations
    
    def run_complete_test(self):
        """Exécuter le test complet selon la demande française"""
        print("🚀 DÉBUT DU TEST CRITIQUE - RÉCUPÉRATION DONNÉES BASE64 MONGODB")
        print("=" * 80)
        print("PROBLÈME: Tous les proxies d'images cassés (claire-marcus.com ET libfusion.preview.emergentagent.com)")
        print("SOLUTION: Servir images directement depuis données base64 MongoDB")
        print("=" * 80)
        
        # Étape 1: Authentification
        if not self.authenticate():
            print("❌ ÉCHEC AUTHENTIFICATION - Arrêt du test")
            return False
        
        # Étape 2: Analyse des données base64
        base64_analysis, sample_files = self.analyze_content_pending()
        if not base64_analysis:
            print("❌ ÉCHEC ANALYSE BASE64 - Arrêt du test")
            return False
        
        # Étape 3: Test conversion base64
        base64_working = self.test_base64_image_conversion(sample_files)
        
        # Étape 4: Test accessibilité proxies
        self.test_proxy_accessibility(sample_files)
        
        # Étape 5: Recommandations
        recommendations = self.generate_solution_recommendations(base64_analysis, sample_files)
        
        # Résumé final
        print("\n" + "=" * 80)
        print("📊 RÉSUMÉ FINAL DU TEST")
        print("=" * 80)
        
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Tests réussis: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"Authentification: {'✅' if self.access_token else '❌'}")
        print(f"Données base64 disponibles: {'✅' if base64_analysis and (base64_analysis['files_with_file_data'] > 0 or base64_analysis['files_with_thumbnail_data'] > 0) else '❌'}")
        print(f"Conversion base64 fonctionnelle: {'✅' if base64_working else '❌'}")
        
        if base64_analysis:
            print(f"\nSTATISTIQUES BASE64:")
            print(f"- Fichiers avec file_data: {base64_analysis['files_with_file_data']}")
            print(f"- Fichiers avec thumbnail_data: {base64_analysis['files_with_thumbnail_data']}")
            print(f"- Fichiers avec URL: {base64_analysis['files_with_url']}")
            print(f"- Fichiers avec thumb_url: {base64_analysis['files_with_thumb_url']}")
            print(f"- Total fichiers: {base64_analysis['total_files']}")
        
        print("\n🎯 CONCLUSION:")
        if base64_working:
            print("✅ SOLUTION BASE64 VIABLE - Les données base64 peuvent servir d'images de secours")
            print("👉 RECOMMANDATION: Modifier le frontend pour utiliser base64 quand les proxies échouent")
        else:
            print("❌ SOLUTION BASE64 NON VIABLE - Pas assez de données base64 disponibles")
            print("👉 RECOMMANDATION: Générer/stocker les données base64 manquantes")
        
        return success_rate > 70

def main():
    """Fonction principale"""
    tester = ImageBase64Tester()
    success = tester.run_complete_test()
    
    if success:
        print("\n🎉 TEST RÉUSSI - Solution base64 identifiée")
        exit(0)
    else:
        print("\n⚠️ TEST PARTIELLEMENT RÉUSSI - Voir recommandations")
        exit(1)

if __name__ == "__main__":
    main()