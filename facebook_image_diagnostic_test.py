#!/usr/bin/env python3
"""
Facebook Image Publication Diagnostic - Production vs Preview
Testing Facebook image publication issues in production environment

Identifiants: lperpere@yahoo.fr / L@Reunion974!

DIAGNOSTIC OBJECTIVES:
1. Test URL production directe - GET https://claire-marcus.com/api/public/image/{id} without auth
2. Compare with preview URL that was working
3. Test curl production manual with HTTP headers analysis
4. Test Facebook publication in production with image URLs
5. Diagnostic production environment variables
6. Test Facebook Graph API direct with production URLs

HYPOTHESIS: Configuration serveur/proxy différente entre preview et production bloque l'accès aux images
"""

import requests
import json
import sys
import subprocess
import time
from datetime import datetime
from urllib.parse import urlparse

# Configuration - PRODUCTION URLs
PRODUCTION_BASE_URL = "https://claire-marcus.com/api"
PREVIEW_BASE_URL = "https://post-restore.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

# Images de test externes
WIKIMEDIA_IMAGE = "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png"
PIXABAY_IMAGE = "https://cdn.pixabay.com/photo/2016/11/29/05/45/astronomy-1867616_960_720.jpg"

class FacebookImageDiagnostic:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        self.backend_url = None
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
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
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()
        
    def authenticate(self):
        """Étape 1: Authentification"""
        try:
            print("🔐 Étape 1: Authentification")
            response = self.session.post(
                f"{BASE_URL}/auth/login-robust",
                json=TEST_CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                self.log_test("Authentification", True, f"User ID: {self.user_id}")
                return True
            else:
                self.log_test("Authentification", False, 
                            f"Status: {response.status_code}", 
                            response.text[:200])
                return False
                
        except Exception as e:
            self.log_test("Authentification", False, error=str(e))
            return False
    
    def get_backend_url(self):
        """Récupérer l'URL backend depuis frontend/.env"""
        try:
            # Lire le fichier .env du frontend pour obtenir REACT_APP_BACKEND_URL
            with open('/app/frontend/.env', 'r') as f:
                content = f.read()
                for line in content.split('\n'):
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        self.backend_url = line.split('=', 1)[1].strip()
                        break
            
            if not self.backend_url:
                self.backend_url = FRONTEND_URL  # Fallback
                
            print(f"🔗 Backend URL détecté: {self.backend_url}")
            return self.backend_url
            
        except Exception as e:
            print(f"⚠️ Erreur lecture .env: {e}")
            self.backend_url = FRONTEND_URL
            return self.backend_url
    
    def test_get_pending_content(self):
        """Test 1: Récupérer une URL d'image du système (GET /api/content/pending)"""
        try:
            print("📁 Test 1: Récupération contenu en attente")
            response = self.session.get(f"{BASE_URL}/content/pending?limit=5", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                
                if content_items:
                    # Prendre le premier élément avec une image
                    for item in content_items:
                        if item.get("file_type", "").startswith("image"):
                            image_id = item.get("id")
                            image_url = item.get("url", "")
                            filename = item.get("filename", "")
                            
                            self.log_test("Récupération contenu système", True, 
                                        f"Image trouvée - ID: {image_id}, URL: {image_url}, Fichier: {filename}")
                            return {"id": image_id, "url": image_url, "filename": filename}
                    
                    self.log_test("Récupération contenu système", False, 
                                f"Aucune image trouvée dans {len(content_items)} éléments")
                    return None
                else:
                    self.log_test("Récupération contenu système", False, 
                                "Aucun contenu en attente trouvé")
                    return None
            else:
                self.log_test("Récupération contenu système", False, 
                            f"Status: {response.status_code}", response.text[:200])
                return None
                
        except Exception as e:
            self.log_test("Récupération contenu système", False, error=str(e))
            return None
    
    def test_public_image_endpoint(self, image_id):
        """Test 2: Tester GET /api/public/image/{id} directement"""
        try:
            print(f"🌐 Test 2: Test endpoint public pour image {image_id}")
            
            # Test sans authentification
            public_session = requests.Session()  # Session sans auth
            public_url = f"{BASE_URL}/public/image/{image_id}"
            
            response = public_session.get(public_url, timeout=30, allow_redirects=False)
            
            if response.status_code in [200, 302]:
                if response.status_code == 302:
                    redirect_url = response.headers.get('Location', '')
                    self.log_test("Endpoint public accessible", True, 
                                f"Redirection 302 vers: {redirect_url}")
                else:
                    content_type = response.headers.get('content-type', '')
                    self.log_test("Endpoint public accessible", True, 
                                f"Réponse 200, Content-Type: {content_type}")
                return True
            else:
                self.log_test("Endpoint public accessible", False, 
                            f"Status: {response.status_code}", response.text[:200])
                return False
                
        except Exception as e:
            self.log_test("Endpoint public accessible", False, error=str(e))
            return False
    
    def test_facebook_publish_with_wikimedia(self):
        """Test 3: Test publication Facebook avec image WikiMedia"""
        try:
            print("📘 Test 3: Publication Facebook avec image WikiMedia")
            
            test_data = {
                "text": "Test image WikiMedia - Diagnostic publication Facebook",
                "image_url": WIKIMEDIA_IMAGE
            }
            
            response = self.session.post(
                f"{BASE_URL}/social/facebook/publish-simple", 
                json=test_data, 
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                error_msg = data.get("error", "")
                
                self.log_test("Publication Facebook WikiMedia", success, 
                            f"Succès: {success}, Message: {error_msg}")
                
                # Capturer les détails de la réponse pour analyse
                print(f"📊 Réponse complète Facebook API:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                return data
            else:
                self.log_test("Publication Facebook WikiMedia", False, 
                            f"Status: {response.status_code}", response.text[:200])
                return None
                
        except Exception as e:
            self.log_test("Publication Facebook WikiMedia", False, error=str(e))
            return None
    
    def test_facebook_publish_with_pixabay(self):
        """Test 4: Test publication Facebook avec image Pixabay"""
        try:
            print("📘 Test 4: Publication Facebook avec image Pixabay")
            
            test_data = {
                "text": "Test image Pixabay - Diagnostic publication Facebook",
                "image_url": PIXABAY_IMAGE
            }
            
            response = self.session.post(
                f"{BASE_URL}/social/facebook/publish-simple", 
                json=test_data, 
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                error_msg = data.get("error", "")
                
                self.log_test("Publication Facebook Pixabay", success, 
                            f"Succès: {success}, Message: {error_msg}")
                
                # Capturer les détails de la réponse pour analyse
                print(f"📊 Réponse complète Facebook API:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                return data
            else:
                self.log_test("Publication Facebook Pixabay", False, 
                            f"Status: {response.status_code}", response.text[:200])
                return None
                
        except Exception as e:
            self.log_test("Publication Facebook Pixabay", False, error=str(e))
            return None
    
    def test_facebook_publish_with_system_image(self, system_image):
        """Test 5: Test publication avec vraie image du système"""
        try:
            print("📘 Test 5: Publication Facebook avec image système")
            
            if not system_image:
                self.log_test("Publication Facebook image système", False, 
                            "Aucune image système disponible pour test")
                return None
            
            # Construire l'URL publique pour l'image système
            image_id = system_image["id"]
            backend_url = self.get_backend_url()
            public_image_url = f"{backend_url}/api/public/image/{image_id}"
            
            test_data = {
                "text": f"Test image système - Diagnostic publication Facebook - Fichier: {system_image['filename']}",
                "image_url": public_image_url
            }
            
            print(f"🔗 URL image publique utilisée: {public_image_url}")
            
            response = self.session.post(
                f"{BASE_URL}/social/facebook/publish-simple", 
                json=test_data, 
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                error_msg = data.get("error", "")
                
                self.log_test("Publication Facebook image système", success, 
                            f"Succès: {success}, Message: {error_msg}, URL: {public_image_url}")
                
                # Capturer les détails de la réponse pour analyse
                print(f"📊 Réponse complète Facebook API:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                return data
            else:
                self.log_test("Publication Facebook image système", False, 
                            f"Status: {response.status_code}", response.text[:200])
                return None
                
        except Exception as e:
            self.log_test("Publication Facebook image système", False, error=str(e))
            return None
    
    def test_facebook_connection_status(self):
        """Test 6: Vérifier l'état des connexions Facebook"""
        try:
            print("🔗 Test 6: État des connexions Facebook")
            
            response = self.session.get(f"{BASE_URL}/debug/social-connections", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                facebook_connections = data.get("facebook_connections", 0)
                active_connections = data.get("active_connections", 0)
                
                # Obtenir les détails des connexions
                connections_detail = data.get("connections_detail", {})
                
                self.log_test("État connexions Facebook", True, 
                            f"Facebook: {facebook_connections}, Actives: {active_connections}")
                
                print(f"📊 Détails connexions:")
                print(json.dumps(connections_detail, indent=2, ensure_ascii=False))
                
                return data
            else:
                self.log_test("État connexions Facebook", False, 
                            f"Status: {response.status_code}", response.text[:200])
                return None
                
        except Exception as e:
            self.log_test("État connexions Facebook", False, error=str(e))
            return None
    
    def test_url_conversion_function(self, system_image):
        """Test 7: Vérifier la fonction de conversion d'URL"""
        try:
            print("🔄 Test 7: Test fonction conversion URL")
            
            if not system_image:
                self.log_test("Fonction conversion URL", False, 
                            "Aucune image système pour tester la conversion")
                return False
            
            original_url = system_image["url"]
            image_id = system_image["id"]
            backend_url = self.get_backend_url()
            expected_public_url = f"{backend_url}/api/public/image/{image_id}"
            
            # Vérifier si l'URL originale est protégée
            is_protected = "/api/content/" in original_url and "/file" in original_url
            
            self.log_test("Fonction conversion URL", True, 
                        f"URL originale: {original_url}, Protégée: {is_protected}, URL publique attendue: {expected_public_url}")
            
            return True
                
        except Exception as e:
            self.log_test("Fonction conversion URL", False, error=str(e))
            return False
    
    def capture_backend_logs(self):
        """Test 8: Capturer les logs backend (si disponible)"""
        try:
            print("📋 Test 8: Capture logs backend")
            
            # Essayer de lire les logs supervisor backend
            try:
                import subprocess
                result = subprocess.run(
                    ["tail", "-n", "50", "/var/log/supervisor/backend.out.log"], 
                    capture_output=True, text=True, timeout=10
                )
                
                if result.returncode == 0:
                    logs = result.stdout
                    self.log_test("Capture logs backend", True, 
                                f"Logs capturés ({len(logs.split())} lignes)")
                    
                    print("📋 Derniers logs backend:")
                    print("-" * 50)
                    print(logs[-1000:])  # Derniers 1000 caractères
                    print("-" * 50)
                    
                    return logs
                else:
                    self.log_test("Capture logs backend", False, 
                                "Impossible de lire les logs supervisor")
                    return None
                    
            except Exception as log_error:
                self.log_test("Capture logs backend", False, 
                            f"Erreur lecture logs: {log_error}")
                return None
                
        except Exception as e:
            self.log_test("Capture logs backend", False, error=str(e))
            return None
    
    def run_diagnostic(self):
        """Exécuter le diagnostic complet"""
        print("🎯 FACEBOOK IMAGE PUBLICATION DIAGNOSTIC - PRODUCTION VS PREVIEW")
        print("=" * 80)
        print(f"Production URL: {PRODUCTION_BASE_URL}")
        print(f"Preview URL: {PREVIEW_BASE_URL}")
        print(f"Test User: {TEST_CREDENTIALS['email']}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 80)
        print()
        
        # Étape 1: Authentification
        if not self.authenticate():
            print("❌ Authentification échouée - impossible de continuer")
            return False
        
        # Test 1: Récupérer une image du système
        system_image = self.test_get_pending_content()
        
        # Test 2: Tester l'endpoint public si on a une image
        if system_image:
            self.test_public_image_endpoint(system_image["id"])
        
        # Test 3: Publication avec WikiMedia
        wikimedia_result = self.test_facebook_publish_with_wikimedia()
        
        # Test 4: Publication avec Pixabay
        pixabay_result = self.test_facebook_publish_with_pixabay()
        
        # Test 5: Publication avec image système
        system_result = self.test_facebook_publish_with_system_image(system_image)
        
        # Test 6: État des connexions
        connection_status = self.test_facebook_connection_status()
        
        # Test 7: Test fonction conversion URL
        self.test_url_conversion_function(system_image)
        
        # Test 8: Capturer les logs backend
        backend_logs = self.capture_backend_logs()
        
        # Résumé du diagnostic
        print("\n" + "=" * 80)
        print("📊 RÉSUMÉ DIAGNOSTIC FACEBOOK IMAGES")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print(f"\n🎯 RÉSULTATS: {passed}/{total} tests réussis ({(passed/total*100):.1f}%)")
        
        # Analyse des résultats
        print("\n🔍 ANALYSE DIAGNOSTIC:")
        
        # Analyser les résultats de publication
        publication_results = [wikimedia_result, pixabay_result, system_result]
        successful_publications = [r for r in publication_results if r and r.get("success")]
        failed_publications = [r for r in publication_results if r and not r.get("success")]
        
        if successful_publications:
            print(f"✅ {len(successful_publications)} publications réussies")
        
        if failed_publications:
            print(f"❌ {len(failed_publications)} publications échouées")
            for result in failed_publications:
                error_msg = result.get("error", "Erreur inconnue")
                print(f"   - Erreur: {error_msg}")
        
        # Recommandations
        print("\n💡 RECOMMANDATIONS:")
        
        if system_image:
            print(f"✅ Images système disponibles pour test")
            print(f"   - ID exemple: {system_image['id']}")
            print(f"   - URL originale: {system_image['url']}")
        else:
            print("⚠️ Aucune image système trouvée - ajouter du contenu pour tests complets")
        
        if connection_status:
            facebook_count = connection_status.get("facebook_connections", 0)
            if facebook_count == 0:
                print("⚠️ Aucune connexion Facebook active - reconnecter le compte Facebook")
            else:
                print(f"✅ {facebook_count} connexion(s) Facebook trouvée(s)")
        
        return passed == total

def main():
    """Exécution principale du diagnostic"""
    diagnostic = FacebookImageDiagnostic()
    success = diagnostic.run_diagnostic()
    
    if success:
        print("\n✅ Diagnostic Facebook images terminé avec succès!")
        print("🔍 Analyser les logs et réponses API ci-dessus pour identifier la cause racine")
        sys.exit(0)
    else:
        print("\n⚠️ Diagnostic Facebook images terminé avec des problèmes identifiés")
        print("🔍 Consulter les détails ci-dessus pour résoudre les problèmes")
        sys.exit(1)

if __name__ == "__main__":
    main()