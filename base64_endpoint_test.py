#!/usr/bin/env python3
"""
Test pour créer un endpoint de génération base64 d'urgence
Solution immédiate pour permettre à l'utilisateur de voir ses images
"""

import requests
import json
import os
import time
import base64
from io import BytesIO
from PIL import Image

# Configuration
BACKEND_URL = "https://claire-marcus-app-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Credentials
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class Base64EndpointTester:
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
        """Authentifier"""
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                self.log_result("Authentication", True, f"User ID: {self.user_id}")
                return True
            else:
                self.log_result("Authentication", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, "", str(e))
            return False
    
    def test_existing_endpoints(self):
        """Tester les endpoints existants pour voir s'il y a une solution"""
        print("🔍 ÉTAPE 1: Test des endpoints existants")
        
        endpoints_to_test = [
            "/content/pending",
            "/health",
            "/diag",
            "/content/thumbnails/test",
            "/content/thumbnails/status"
        ]
        
        working_endpoints = []
        
        for endpoint in endpoints_to_test:
            try:
                response = self.session.get(f"{API_BASE}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    working_endpoints.append({
                        "endpoint": endpoint,
                        "data": data
                    })
                    
                    self.log_result(
                        f"Endpoint {endpoint}",
                        True,
                        f"Status: 200, Keys: {list(data.keys()) if isinstance(data, dict) else 'Non-dict response'}"
                    )
                else:
                    self.log_result(
                        f"Endpoint {endpoint}",
                        False,
                        f"Status: {response.status_code}",
                        response.text[:200] if response.text else "No response text"
                    )
                    
            except Exception as e:
                self.log_result(
                    f"Endpoint {endpoint}",
                    False,
                    "",
                    str(e)
                )
        
        return working_endpoints
    
    def analyze_thumbnails_system(self):
        """Analyser le système de thumbnails pour voir s'il peut aider"""
        print("🖼️ ÉTAPE 2: Analyse du système de thumbnails")
        
        try:
            # Test du statut des thumbnails
            response = self.session.get(f"{API_BASE}/content/thumbnails/status")
            
            if response.status_code == 200:
                data = response.json()
                
                self.log_result(
                    "Thumbnails Status",
                    True,
                    f"Total files: {data.get('total_files', 'N/A')}, "
                    f"With thumbnails: {data.get('files_with_thumbnails', 'N/A')}, "
                    f"Missing: {data.get('missing_thumbnails', 'N/A')}"
                )
                
                # Test du rebuild des thumbnails
                try:
                    rebuild_response = self.session.post(f"{API_BASE}/content/thumbnails/rebuild")
                    
                    if rebuild_response.status_code == 200:
                        rebuild_data = rebuild_response.json()
                        
                        self.log_result(
                            "Thumbnails Rebuild",
                            True,
                            f"Message: {rebuild_data.get('message', 'N/A')}, "
                            f"Scheduled: {rebuild_data.get('thumbnails_scheduled', 'N/A')}"
                        )
                    else:
                        self.log_result(
                            "Thumbnails Rebuild",
                            False,
                            f"Status: {rebuild_response.status_code}",
                            rebuild_response.text[:200]
                        )
                        
                except Exception as e:
                    self.log_result("Thumbnails Rebuild", False, "", str(e))
                
                return data
            else:
                self.log_result(
                    "Thumbnails Status",
                    False,
                    f"Status: {response.status_code}",
                    response.text[:200]
                )
                return None
                
        except Exception as e:
            self.log_result("Thumbnails Status", False, "", str(e))
            return None
    
    def test_content_with_base64_fallback(self):
        """Tester si on peut modifier l'endpoint content pour inclure base64"""
        print("📊 ÉTAPE 3: Test de modification de l'endpoint content")
        
        try:
            # Récupérer le contenu actuel
            response = self.session.get(f"{API_BASE}/content/pending?limit=5")
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                
                self.log_result(
                    "Content Pending Access",
                    True,
                    f"Files retrieved: {len(content)}"
                )
                
                # Analyser la structure actuelle
                if content:
                    first_file = content[0]
                    available_fields = list(first_file.keys())
                    
                    self.log_result(
                        "Content Structure Analysis",
                        True,
                        f"Available fields: {available_fields}"
                    )
                    
                    # Vérifier si des champs base64 existent déjà
                    base64_fields = [field for field in available_fields if 'data' in field.lower() or 'base64' in field.lower()]
                    
                    if base64_fields:
                        self.log_result(
                            "Base64 Fields Found",
                            True,
                            f"Fields: {base64_fields}"
                        )
                    else:
                        self.log_result(
                            "Base64 Fields Found",
                            False,
                            "No base64 fields in current structure"
                        )
                    
                    return {
                        "content": content,
                        "available_fields": available_fields,
                        "base64_fields": base64_fields
                    }
                else:
                    self.log_result(
                        "Content Analysis",
                        False,
                        "No content files found"
                    )
                    return None
            else:
                self.log_result(
                    "Content Pending Access",
                    False,
                    f"Status: {response.status_code}",
                    response.text[:200]
                )
                return None
                
        except Exception as e:
            self.log_result("Content Analysis", False, "", str(e))
            return None
    
    def propose_immediate_solutions(self, content_analysis, thumbnails_data):
        """Proposer des solutions immédiates"""
        print("💡 ÉTAPE 4: Proposition de solutions immédiates")
        
        solutions = []
        
        # Solution 1: Modifier l'endpoint existant pour inclure base64
        if content_analysis:
            solutions.append({
                "priority": "IMMEDIATE",
                "title": "Modifier /api/content/pending pour inclure base64",
                "description": "Ajouter file_data et thumbnail_data base64 à la réponse existante",
                "implementation": "Modifier server.py pour générer base64 à la volée depuis les fichiers du système",
                "code_example": """
# Dans server.py, fonction get_pending_content_mongo:
if os.path.exists(file_path):
    with open(file_path, 'rb') as f:
        file_content = f.read()
        file_data = base64.b64encode(file_content).decode('utf-8')
        
        # Générer thumbnail
        image = Image.open(io.BytesIO(file_content))
        image.thumbnail((320, 320), Image.Resampling.LANCZOS)
        thumb_buffer = io.BytesIO()
        image.save(thumb_buffer, format='JPEG', quality=75)
        thumbnail_data = base64.b64encode(thumb_buffer.getvalue()).decode('utf-8')
                """,
                "impact": "L'utilisateur verra ses images immédiatement sans changement frontend"
            })
        
        # Solution 2: Créer un endpoint de secours
        solutions.append({
            "priority": "IMMEDIATE",
            "title": "Créer /api/content/{file_id}/base64",
            "description": "Endpoint dédié pour récupérer base64 d'un fichier spécifique",
            "implementation": "Nouvel endpoint qui lit le fichier depuis le système et retourne base64",
            "code_example": """
@api_router.get("/content/{file_id}/base64")
async def get_file_base64(file_id: str, user_id: str = Depends(get_current_user_id)):
    # Trouver le fichier dans uploads/
    for filename in os.listdir("uploads"):
        if filename.startswith(file_id):
            file_path = os.path.join("uploads", filename)
            with open(file_path, 'rb') as f:
                file_content = f.read()
                file_data = base64.b64encode(file_content).decode('utf-8')
                return {"file_data": file_data, "content_type": "image/jpeg"}
    raise HTTPException(404, "File not found")
            """,
            "impact": "Frontend peut faire des appels individuels pour récupérer base64"
        })
        
        # Solution 3: Endpoint de migration en masse
        solutions.append({
            "priority": "SHORT_TERM",
            "title": "Créer /api/content/migrate-to-base64",
            "description": "Endpoint pour migrer tous les fichiers vers base64 en MongoDB",
            "implementation": "Script qui lit tous les fichiers et met à jour MongoDB avec base64",
            "code_example": """
@api_router.post("/content/migrate-to-base64")
async def migrate_to_base64(user_id: str = Depends(get_current_user_id)):
    media_collection = get_media_collection()
    updated_count = 0
    
    for filename in os.listdir("uploads"):
        file_path = os.path.join("uploads", filename)
        with open(file_path, 'rb') as f:
            file_content = f.read()
            file_data = base64.b64encode(file_content).decode('utf-8')
            
            # Mettre à jour MongoDB
            media_collection.update_one(
                {"filename": filename},
                {"$set": {"file_data": file_data}}
            )
            updated_count += 1
    
    return {"message": f"Migrated {updated_count} files to base64"}
            """,
            "impact": "Migration permanente vers base64, résout le problème définitivement"
        })
        
        print("\n🎯 SOLUTIONS PROPOSÉES:")
        for i, solution in enumerate(solutions, 1):
            print(f"\n{i}. [{solution['priority']}] {solution['title']}")
            print(f"   Description: {solution['description']}")
            print(f"   Implémentation: {solution['implementation']}")
            print(f"   Impact: {solution['impact']}")
        
        self.log_result(
            "Solutions proposées",
            True,
            f"{len(solutions)} solutions identifiées"
        )
        
        return solutions
    
    def run_complete_analysis(self):
        """Exécuter l'analyse complète"""
        print("🔍 DÉBUT DE L'ANALYSE ENDPOINT BASE64")
        print("=" * 80)
        print("OBJECTIF: Identifier comment créer un endpoint base64 d'urgence")
        print("=" * 80)
        
        # Authentification
        if not self.authenticate():
            return False
        
        # Test des endpoints existants
        working_endpoints = self.test_existing_endpoints()
        
        # Analyse du système de thumbnails
        thumbnails_data = self.analyze_thumbnails_system()
        
        # Analyse du contenu
        content_analysis = self.test_content_with_base64_fallback()
        
        # Proposer des solutions
        solutions = self.propose_immediate_solutions(content_analysis, thumbnails_data)
        
        # Résumé final
        print("\n" + "=" * 80)
        print("📊 RÉSUMÉ DE L'ANALYSE")
        print("=" * 80)
        
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Tests réussis: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"Endpoints fonctionnels: {len(working_endpoints)}")
        print(f"Système thumbnails: {'✅' if thumbnails_data else '❌'}")
        print(f"Analyse contenu: {'✅' if content_analysis else '❌'}")
        print(f"Solutions proposées: {len(solutions) if solutions else 0}")
        
        print("\n🎯 CONCLUSION:")
        if success_rate > 50 and solutions:
            print("✅ ANALYSE RÉUSSIE - Solutions d'urgence identifiées")
            print("👉 RECOMMANDATION: Implémenter la Solution 1 (modifier /api/content/pending)")
            print("👉 IMPACT: Solution la plus rapide pour débloquer l'utilisateur")
        else:
            print("❌ ANALYSE PROBLÉMATIQUE - Investigation approfondie requise")
        
        return success_rate > 50

def main():
    """Fonction principale"""
    tester = Base64EndpointTester()
    success = tester.run_complete_analysis()
    
    if success:
        print("\n🎉 ANALYSE TERMINÉE - Solutions identifiées")
        exit(0)
    else:
        print("\n⚠️ ANALYSE INCOMPLÈTE - Problèmes détectés")
        exit(1)

if __name__ == "__main__":
    main()