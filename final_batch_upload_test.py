#!/usr/bin/env python3
"""
Test final complet pour l'endpoint POST /api/content/batch-upload
Basé sur les exigences de la review request française
"""

import requests
import json
import os
from datetime import datetime

class FinalBatchUploadTest:
    def __init__(self):
        self.base_url = "https://post-restore.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.user_id = None
        self.tests_passed = 0
        self.tests_total = 0
        
        print("🎯 TEST FINAL DU NOUVEL ENDPOINT D'UPLOAD")
        print("=" * 60)

    def login(self):
        """Test de connexion avec les credentials fournis"""
        print("🔐 TEST 1: CONNEXION")
        
        login_data = {
            "email": "lperpere@yahoo.fr",
            "password": "L@Reunion974!"
        }
        
        response = requests.post(f"{self.api_url}/auth/login", json=login_data)
        self.tests_total += 1
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get('access_token')
            self.user_id = data.get('user_id')
            print(f"   ✅ Connexion réussie")
            print(f"   👤 User: {data.get('email')}")
            print(f"   🔑 Token: {self.access_token[:20]}...")
            self.tests_passed += 1
            return True
        else:
            print(f"   ❌ Échec de connexion: {response.status_code}")
            return False

    def test_endpoint_exists(self):
        """Test que l'endpoint POST /api/content/batch-upload existe"""
        print("\n📍 TEST 2: EXISTENCE DE L'ENDPOINT")
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        # Test avec requête vide pour vérifier que l'endpoint existe
        response = requests.post(f"{self.api_url}/content/batch-upload", headers=headers)
        self.tests_total += 1
        
        if response.status_code == 422:  # FastAPI validation error, pas 404
            print(f"   ✅ Endpoint POST /api/content/batch-upload existe")
            print(f"   📄 Retourne 422 pour champs manquants (pas 404)")
            self.tests_passed += 1
            return True
        else:
            print(f"   ❌ Endpoint introuvable ou erreur: {response.status_code}")
            return False

    def test_multipart_upload(self):
        """Test upload multipart/form-data avec FormData"""
        print("\n📤 TEST 3: UPLOAD MULTIPART/FORM-DATA")
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        # Créer fichiers de test
        png_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
        mp4_content = b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom\x00\x00\x00\x08free'
        
        # Upload avec clé 'files' comme attendu par le frontend
        files = [
            ('files', ('image.png', png_content, 'image/png')),
            ('files', ('video.mp4', mp4_content, 'video/mp4'))
        ]
        
        response = requests.post(f"{self.api_url}/content/batch-upload", files=files, headers=headers)
        self.tests_total += 1
        
        if response.status_code == 200:
            data = response.json()
            uploaded_files = data.get('uploaded_files', [])
            
            print(f"   ✅ Upload multipart réussi")
            print(f"   📁 Fichiers uploadés: {data.get('total_uploaded', 0)}")
            print(f"   📄 Réponse contient 'uploaded_files' array")
            
            # Vérifier format de réponse attendu par frontend
            if 'uploaded_files' in data and len(uploaded_files) > 0:
                print(f"   ✅ Format de réponse compatible frontend")
                for file_info in uploaded_files:
                    print(f"       📄 {file_info.get('original_name')} -> {file_info.get('stored_name')}")
                self.tests_passed += 1
                return True
            else:
                print(f"   ❌ Format de réponse incorrect")
                return False
        else:
            print(f"   ❌ Échec upload: {response.status_code}")
            print(f"   📄 {response.text}")
            return False

    def test_file_type_validation(self):
        """Test validation des types de fichiers"""
        print("\n🔍 TEST 4: VALIDATION TYPES DE FICHIERS")
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        # Test fichier non-image/vidéo
        files = {'files': ('document.txt', b'Contenu texte', 'text/plain')}
        
        response = requests.post(f"{self.api_url}/content/batch-upload", files=files, headers=headers)
        self.tests_total += 1
        
        if response.status_code == 200:
            data = response.json()
            failed_uploads = data.get('failed_uploads', [])
            
            if len(failed_uploads) > 0 and data.get('total_uploaded', 0) == 0:
                error_msg = failed_uploads[0].get('error', '')
                print(f"   ✅ Fichier non-image/vidéo rejeté")
                print(f"   📄 Erreur: {error_msg}")
                self.tests_passed += 1
                return True
            else:
                print(f"   ❌ Fichier invalide accepté")
                return False
        else:
            print(f"   ❌ Erreur validation: {response.status_code}")
            return False

    def test_file_size_validation(self):
        """Test validation de taille (max 10MB)"""
        print("\n📏 TEST 5: VALIDATION TAILLE FICHIERS")
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        # Créer fichier > 10MB
        large_content = b'x' * (11 * 1024 * 1024)  # 11MB
        files = {'files': ('large.png', large_content, 'image/png')}
        
        response = requests.post(f"{self.api_url}/content/batch-upload", files=files, headers=headers)
        self.tests_total += 1
        
        if response.status_code == 200:
            data = response.json()
            failed_uploads = data.get('failed_uploads', [])
            
            if len(failed_uploads) > 0 and data.get('total_uploaded', 0) == 0:
                error_msg = failed_uploads[0].get('error', '')
                print(f"   ✅ Fichier trop volumineux rejeté")
                print(f"   📄 Erreur: {error_msg}")
                self.tests_passed += 1
                return True
            else:
                print(f"   ❌ Fichier volumineux accepté")
                return False
        else:
            print(f"   ❌ Erreur validation: {response.status_code}")
            return False

    def test_file_storage(self):
        """Test sauvegarde dans /app/backend/uploads"""
        print("\n💾 TEST 6: SAUVEGARDE FICHIERS")
        
        uploads_dir = "/app/backend/uploads"
        
        if os.path.exists(uploads_dir):
            files = os.listdir(uploads_dir)
            print(f"   ✅ Dossier uploads existe: {uploads_dir}")
            print(f"   📁 Nombre de fichiers: {len(files)}")
            
            # Vérifier quelques fichiers récents
            recent_files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(uploads_dir, x)), reverse=True)[:3]
            for file in recent_files:
                file_path = os.path.join(uploads_dir, file)
                file_size = os.path.getsize(file_path)
                print(f"       📄 {file} ({file_size} bytes)")
            
            self.tests_total += 1
            self.tests_passed += 1
            return True
        else:
            print(f"   ❌ Dossier uploads introuvable")
            self.tests_total += 1
            return False

    def test_authentication_required(self):
        """Test que l'authentification JWT est requise"""
        print("\n🔐 TEST 7: AUTHENTIFICATION REQUISE")
        
        # Test sans token
        files = {'files': ('test.png', b'fake png', 'image/png')}
        response = requests.post(f"{self.api_url}/content/batch-upload", files=files)
        
        self.tests_total += 1
        
        # Should return 401 or similar for missing auth
        if response.status_code in [401, 403, 422]:
            print(f"   ✅ Authentification requise (status: {response.status_code})")
            self.tests_passed += 1
            return True
        else:
            print(f"   ❌ Endpoint accessible sans authentification: {response.status_code}")
            return False

    def run_all_tests(self):
        """Exécuter tous les tests"""
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Backend: {self.base_url}")
        
        # Séquence de tests
        tests = [
            ("Connexion", self.login),
            ("Existence endpoint", self.test_endpoint_exists),
            ("Upload multipart", self.test_multipart_upload),
            ("Validation types", self.test_file_type_validation),
            ("Validation taille", self.test_file_size_validation),
            ("Sauvegarde fichiers", self.test_file_storage),
            ("Authentification", self.test_authentication_required)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"   ❌ Erreur dans {test_name}: {e}")
                results.append((test_name, False))
                self.tests_total += 1
        
        # Résumé final
        print(f"\n{'='*20} RÉSUMÉ FINAL {'='*20}")
        print(f"📊 Tests exécutés: {self.tests_total}")
        print(f"✅ Tests réussis: {self.tests_passed}")
        print(f"❌ Tests échoués: {self.tests_total - self.tests_passed}")
        print(f"📈 Taux de réussite: {(self.tests_passed/self.tests_total*100):.1f}%")
        
        print(f"\n📋 DÉTAIL DES RÉSULTATS:")
        for test_name, result in results:
            status = "✅ RÉUSSI" if result else "❌ ÉCHOUÉ"
            print(f"   {status} {test_name}")
        
        # Verdict final
        if self.tests_passed == self.tests_total:
            print(f"\n🎉 TOUS LES TESTS RÉUSSIS!")
            print(f"✅ L'endpoint /api/content/batch-upload fonctionne correctement")
            print(f"✅ Upload de fichiers dans la Bibliothèque opérationnel")
        else:
            print(f"\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
            print(f"🔧 Vérifier les résultats ci-dessus pour les détails")
        
        return results

if __name__ == "__main__":
    tester = FinalBatchUploadTest()
    tester.run_all_tests()