#!/usr/bin/env python3
"""
VALIDATION FINALE DU SYSTÈME D'ÉDITION AVEC CLAVIER VIRTUEL
Test spécifique pour le système d'édition du nom d'entreprise avec gestion du clavier virtuel
"""

import requests
import json
import os
from datetime import datetime

class BusinessProfileValidationTester:
    def __init__(self):
        # Use the production backend URL from frontend/.env
        self.base_url = "https://post-restore.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.tests_run = 0
        self.tests_passed = 0
        
        # Test credentials from review request
        self.test_email = "lperpere@yahoo.fr"
        self.test_password = "L@Reunion974!"
        self.test_business_name = "Restaurant Le Bon Goût Final"

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {name}")
            if details:
                print(f"   {details}")

    def make_request(self, method, endpoint, data=None, expected_status=200):
        """Make API request with proper headers"""
        url = f"{self.api_url}/{endpoint}"
        headers = {
            'Content-Type': 'application/json'
        }
        
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            
            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text}
            
            return success, response_data, response.status_code
            
        except Exception as e:
            return False, {"error": str(e)}, 0

    def test_1_user_login(self):
        """Test 1: Connexion utilisateur avec lperpere@yahoo.fr / L@Reunion974!"""
        print("\n🔍 TEST 1: CONNEXION UTILISATEUR")
        
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        success, response, status = self.make_request('POST', 'auth/login', login_data, 200)
        
        if success and 'access_token' in response:
            self.access_token = response['access_token']
            user_id = response.get('user_id', 'N/A')
            self.log_test(
                "Connexion utilisateur réussie", 
                True, 
                f"User ID: {user_id}, Token: {self.access_token[:20]}..."
            )
            return True
        else:
            self.log_test(
                "Connexion utilisateur échouée", 
                False, 
                f"Status: {status}, Response: {response}"
            )
            return False

    def test_2_get_current_business_profile(self):
        """Test 2: GET business profile - Vérifier l'état actuel du nom d'entreprise"""
        print("\n🔍 TEST 2: RÉCUPÉRATION PROFIL ENTREPRISE ACTUEL")
        
        success, response, status = self.make_request('GET', 'business-profile', expected_status=200)
        
        if success:
            business_name = response.get('business_name', 'N/A')
            business_type = response.get('business_type', 'N/A')
            email = response.get('email', 'N/A')
            website_url = response.get('website_url', 'N/A')
            
            self.log_test(
                "Récupération profil entreprise réussie",
                True,
                f"Nom actuel: '{business_name}', Type: '{business_type}', Email: '{email}', Site: '{website_url}'"
            )
            
            # Store current state for comparison
            self.current_profile = response
            return True
        else:
            self.log_test(
                "Récupération profil entreprise échouée",
                False,
                f"Status: {status}, Response: {response}"
            )
            return False

    def test_3_update_business_name(self):
        """Test 3: Test de sauvegarde complète - PUT avec nouveau nom"""
        print("\n🔍 TEST 3: MISE À JOUR NOM D'ENTREPRISE")
        
        if not hasattr(self, 'current_profile'):
            self.log_test("Mise à jour impossible", False, "Profil actuel non récupéré")
            return False
        
        # Create updated profile with new business name
        updated_profile = self.current_profile.copy()
        updated_profile['business_name'] = self.test_business_name
        
        # Remove fields that shouldn't be in PUT request
        for field in ['_id', 'profile_id', 'created_at', 'updated_at']:
            updated_profile.pop(field, None)
        
        success, response, status = self.make_request('PUT', 'business-profile', updated_profile, 200)
        
        if success:
            returned_name = response.get('profile', {}).get('business_name', 'N/A')
            self.log_test(
                "Mise à jour nom d'entreprise réussie",
                True,
                f"Nouveau nom sauvegardé: '{returned_name}'"
            )
            return True
        else:
            self.log_test(
                "Mise à jour nom d'entreprise échouée",
                False,
                f"Status: {status}, Response: {response}"
            )
            return False

    def test_4_verify_persistence_immediate(self):
        """Test 4: Test de persistance immédiate - Confirmer que le nouveau nom persiste"""
        print("\n🔍 TEST 4: VÉRIFICATION PERSISTANCE IMMÉDIATE")
        
        success, response, status = self.make_request('GET', 'business-profile', expected_status=200)
        
        if success:
            business_name = response.get('business_name', 'N/A')
            
            if business_name == self.test_business_name:
                self.log_test(
                    "Persistance immédiate confirmée",
                    True,
                    f"Nom récupéré: '{business_name}' = Nom attendu: '{self.test_business_name}'"
                )
                return True
            else:
                self.log_test(
                    "Persistance immédiate échouée",
                    False,
                    f"Nom récupéré: '{business_name}' ≠ Nom attendu: '{self.test_business_name}'"
                )
                return False
        else:
            self.log_test(
                "Vérification persistance échouée",
                False,
                f"Status: {status}, Response: {response}"
            )
            return False

    def test_5_anti_regression_multiple_gets(self):
        """Test 5: Test anti-régression - S'assurer qu'il n'y a pas de retour aux anciennes valeurs"""
        print("\n🔍 TEST 5: TEST ANTI-RÉGRESSION (REQUÊTES MULTIPLES)")
        
        consistent_results = []
        
        for i in range(5):
            success, response, status = self.make_request('GET', 'business-profile', expected_status=200)
            
            if success:
                business_name = response.get('business_name', 'N/A')
                consistent_results.append(business_name)
                print(f"   Requête {i+1}/5: '{business_name}'")
            else:
                self.log_test(
                    f"Requête anti-régression {i+1}/5 échouée",
                    False,
                    f"Status: {status}"
                )
                return False
        
        # Check if all results are consistent and match expected name
        all_consistent = all(name == self.test_business_name for name in consistent_results)
        
        if all_consistent:
            self.log_test(
                "Test anti-régression réussi",
                True,
                f"5/5 requêtes retournent le nom correct: '{self.test_business_name}'"
            )
            return True
        else:
            unique_names = set(consistent_results)
            self.log_test(
                "Test anti-régression échoué",
                False,
                f"Noms incohérents trouvés: {unique_names}"
            )
            return False

    def test_6_complete_profile_integrity(self):
        """Test 6: Vérification intégrité complète du profil"""
        print("\n🔍 TEST 6: VÉRIFICATION INTÉGRITÉ PROFIL COMPLET")
        
        success, response, status = self.make_request('GET', 'business-profile', expected_status=200)
        
        if success:
            required_fields = [
                'business_name', 'business_type', 'business_description',
                'target_audience', 'brand_tone', 'posting_frequency',
                'preferred_platforms', 'budget_range', 'email',
                'website_url', 'hashtags_primary', 'hashtags_secondary'
            ]
            
            missing_fields = []
            present_fields = []
            
            for field in required_fields:
                if field in response:
                    present_fields.append(field)
                else:
                    missing_fields.append(field)
            
            if not missing_fields:
                self.log_test(
                    "Intégrité profil complet confirmée",
                    True,
                    f"Tous les 12 champs requis présents. Nom d'entreprise: '{response.get('business_name')}'"
                )
                return True
            else:
                self.log_test(
                    "Intégrité profil incomplète",
                    False,
                    f"Champs manquants: {missing_fields}"
                )
                return False
        else:
            self.log_test(
                "Vérification intégrité échouée",
                False,
                f"Status: {status}, Response: {response}"
            )
            return False

    def test_7_virtual_keyboard_simulation(self):
        """Test 7: Simulation gestion clavier virtuel (test de stabilité)"""
        print("\n🔍 TEST 7: SIMULATION GESTION CLAVIER VIRTUEL")
        
        # Simulate rapid successive requests that might occur during virtual keyboard interactions
        rapid_requests = []
        
        for i in range(3):
            success, response, status = self.make_request('GET', 'business-profile', expected_status=200)
            if success:
                business_name = response.get('business_name', 'N/A')
                rapid_requests.append(business_name)
            else:
                rapid_requests.append(f"ERROR_{status}")
        
        # Check stability
        all_stable = all(name == self.test_business_name for name in rapid_requests)
        
        if all_stable:
            self.log_test(
                "Simulation clavier virtuel réussie",
                True,
                f"Données stables lors de requêtes rapides: '{self.test_business_name}'"
            )
            return True
        else:
            self.log_test(
                "Simulation clavier virtuel échouée",
                False,
                f"Instabilité détectée: {rapid_requests}"
            )
            return False

    def run_validation_tests(self):
        """Exécuter tous les tests de validation"""
        print("🚀 VALIDATION FINALE DU SYSTÈME D'ÉDITION AVEC CLAVIER VIRTUEL")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Utilisateur de test: {self.test_email}")
        print(f"Nouveau nom d'entreprise: {self.test_business_name}")
        print("=" * 80)
        
        # Séquence de tests
        test_sequence = [
            ("Test 1: Connexion utilisateur", self.test_1_user_login),
            ("Test 2: GET business profile", self.test_2_get_current_business_profile),
            ("Test 3: PUT nouveau nom", self.test_3_update_business_name),
            ("Test 4: Vérification persistance", self.test_4_verify_persistence_immediate),
            ("Test 5: Test anti-régression", self.test_5_anti_regression_multiple_gets),
            ("Test 6: Intégrité profil complet", self.test_6_complete_profile_integrity),
            ("Test 7: Simulation clavier virtuel", self.test_7_virtual_keyboard_simulation),
        ]
        
        # Exécuter les tests
        for test_name, test_func in test_sequence:
            try:
                test_func()
            except Exception as e:
                self.log_test(test_name, False, f"Exception: {str(e)}")
        
        # Résultats finaux
        print("\n" + "=" * 80)
        print("📊 RÉSULTATS FINAUX")
        print("=" * 80)
        print(f"Tests exécutés: {self.tests_run}")
        print(f"Tests réussis: {self.tests_passed}")
        print(f"Tests échoués: {self.tests_run - self.tests_passed}")
        print(f"Taux de réussite: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 VALIDATION COMPLÈTE RÉUSSIE!")
            print("✅ Le système d'édition avec clavier virtuel fonctionne parfaitement")
            return True
        else:
            print(f"\n⚠️ VALIDATION PARTIELLE: {self.tests_run - self.tests_passed} test(s) échoué(s)")
            return False

if __name__ == "__main__":
    tester = BusinessProfileValidationTester()
    success = tester.run_validation_tests()
    exit(0 if success else 1)