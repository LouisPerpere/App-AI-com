#!/usr/bin/env python3
"""
Test du nouveau système d'édition du nom d'entreprise avec verrouillage
Test spécifique pour la fonctionnalité crayon/coche verte de sauvegarde

Basé sur la demande de test en français:
- Connecter avec lperpere@yahoo.fr / L@Reunion974!
- Tester la sauvegarde avec PUT /api/business-profile
- Vérifier la persistance avec GET /api/business-profile
- S'assurer que les données ne reviennent pas à "Restaurant Test Persistance"
"""

import requests
import json
import sys
from datetime import datetime

class BusinessNameEditTester:
    def __init__(self):
        # Use production backend URL from frontend/.env
        self.base_url = "https://claire-marcus-app-1.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.tests_run = 0
        self.tests_passed = 0
        
        # Test credentials from review request
        self.test_email = "lperpere@yahoo.fr"
        self.test_password = "L@Reunion974!"
        
        # Test data from review request
        self.new_business_name = "Mon Super Restaurant Modifié 2025"

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
            
            return success, response.status_code, response_data
            
        except Exception as e:
            return False, 0, {"error": str(e)}

    def test_authentication(self):
        """Test 1: Authentification avec lperpere@yahoo.fr / L@Reunion974!"""
        print("\n🔐 TEST 1: Authentification utilisateur")
        
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        success, status, response = self.make_request('POST', 'auth/login', login_data, 200)
        
        if success and 'access_token' in response:
            self.access_token = response['access_token']
            user_id = response.get('user_id', 'N/A')
            self.log_test(
                "Authentification réussie", 
                True, 
                f"User ID: {user_id}, Token: {self.access_token[:20]}..."
            )
            return True
        else:
            self.log_test(
                "Authentification échouée", 
                False, 
                f"Status: {status}, Response: {response}"
            )
            return False

    def test_get_current_business_profile(self):
        """Test 2: Récupération du profil d'entreprise actuel"""
        print("\n📋 TEST 2: Récupération du profil d'entreprise actuel")
        
        success, status, response = self.make_request('GET', 'business-profile', expected_status=200)
        
        if success:
            business_name = response.get('business_name', 'N/A')
            business_type = response.get('business_type', 'N/A')
            email = response.get('email', 'N/A')
            website_url = response.get('website_url', 'N/A')
            
            self.log_test(
                "Profil d'entreprise récupéré", 
                True, 
                f"Nom: '{business_name}', Type: '{business_type}', Email: '{email}', Site: '{website_url}'"
            )
            
            # Store current profile for comparison
            self.current_profile = response
            return True
        else:
            self.log_test(
                "Échec récupération profil", 
                False, 
                f"Status: {status}, Response: {response}"
            )
            return False

    def test_update_business_name(self):
        """Test 3: Mise à jour du nom d'entreprise via PUT /api/business-profile"""
        print(f"\n✏️ TEST 3: Mise à jour du nom d'entreprise vers '{self.new_business_name}'")
        
        if not hasattr(self, 'current_profile'):
            self.log_test("Pas de profil actuel disponible", False)
            return False
        
        # Prepare updated profile with new business name
        updated_profile = self.current_profile.copy()
        updated_profile['business_name'] = self.new_business_name
        
        # Remove fields that shouldn't be in PUT request
        for field in ['_id', 'profile_id', 'created_at', 'updated_at']:
            updated_profile.pop(field, None)
        
        success, status, response = self.make_request('PUT', 'business-profile', updated_profile, 200)
        
        if success:
            returned_name = response.get('profile', {}).get('business_name', 'N/A')
            self.log_test(
                "Mise à jour du nom d'entreprise réussie", 
                True, 
                f"Nom retourné dans la réponse: '{returned_name}'"
            )
            return True
        else:
            self.log_test(
                "Échec mise à jour nom d'entreprise", 
                False, 
                f"Status: {status}, Response: {response}"
            )
            return False

    def test_verify_persistence_immediate(self):
        """Test 4: Vérification immédiate de la persistance avec GET"""
        print(f"\n🔍 TEST 4: Vérification immédiate de la persistance")
        
        success, status, response = self.make_request('GET', 'business-profile', expected_status=200)
        
        if success:
            business_name = response.get('business_name', 'N/A')
            
            if business_name == self.new_business_name:
                self.log_test(
                    "Persistance immédiate confirmée", 
                    True, 
                    f"Nom récupéré: '{business_name}' (correspond au nom sauvegardé)"
                )
                return True
            else:
                self.log_test(
                    "Échec persistance immédiate", 
                    False, 
                    f"Nom attendu: '{self.new_business_name}', Nom récupéré: '{business_name}'"
                )
                return False
        else:
            self.log_test(
                "Échec récupération pour vérification", 
                False, 
                f"Status: {status}, Response: {response}"
            )
            return False

    def test_verify_no_revert_to_test_data(self):
        """Test 5: Vérification que les données ne reviennent pas à 'Restaurant Test Persistance'"""
        print(f"\n🚫 TEST 5: Vérification anti-régression - pas de retour à 'Restaurant Test Persistance'")
        
        success, status, response = self.make_request('GET', 'business-profile', expected_status=200)
        
        if success:
            business_name = response.get('business_name', 'N/A')
            
            if business_name == "Restaurant Test Persistance":
                self.log_test(
                    "RÉGRESSION DÉTECTÉE", 
                    False, 
                    f"Le nom est revenu à 'Restaurant Test Persistance' au lieu de '{self.new_business_name}'"
                )
                return False
            elif business_name == self.new_business_name:
                self.log_test(
                    "Pas de régression - données correctes", 
                    True, 
                    f"Nom maintenu: '{business_name}'"
                )
                return True
            else:
                self.log_test(
                    "Nom inattendu mais pas de régression", 
                    True, 
                    f"Nom actuel: '{business_name}' (différent de 'Restaurant Test Persistance')"
                )
                return True
        else:
            self.log_test(
                "Échec vérification anti-régression", 
                False, 
                f"Status: {status}, Response: {response}"
            )
            return False

    def test_multiple_get_requests(self):
        """Test 6: Tests multiples GET pour simuler les rafraîchissements de l'interface"""
        print(f"\n🔄 TEST 6: Tests multiples GET (simulation rafraîchissements interface)")
        
        consistent_results = True
        results = []
        
        for i in range(5):
            success, status, response = self.make_request('GET', 'business-profile', expected_status=200)
            
            if success:
                business_name = response.get('business_name', 'N/A')
                results.append(business_name)
                print(f"   GET #{i+1}: '{business_name}'")
            else:
                results.append(f"ERROR_{status}")
                consistent_results = False
        
        # Check if all results are consistent
        if consistent_results and len(set(results)) == 1:
            final_name = results[0]
            if final_name == self.new_business_name:
                self.log_test(
                    "Consistance parfaite sur 5 requêtes", 
                    True, 
                    f"Nom stable: '{final_name}'"
                )
                return True
            else:
                self.log_test(
                    "Consistance mais nom incorrect", 
                    False, 
                    f"Nom stable: '{final_name}' (attendu: '{self.new_business_name}')"
                )
                return False
        else:
            self.log_test(
                "Inconsistance détectée", 
                False, 
                f"Résultats variables: {set(results)}"
            )
            return False

    def test_business_profile_completeness(self):
        """Test 7: Vérification de la complétude du profil d'entreprise"""
        print(f"\n📊 TEST 7: Vérification complétude du profil d'entreprise")
        
        success, status, response = self.make_request('GET', 'business-profile', expected_status=200)
        
        if success:
            expected_fields = [
                'business_name', 'business_type', 'business_description',
                'target_audience', 'brand_tone', 'posting_frequency',
                'preferred_platforms', 'budget_range', 'email', 'website_url',
                'hashtags_primary', 'hashtags_secondary'
            ]
            
            missing_fields = []
            present_fields = []
            
            for field in expected_fields:
                if field in response:
                    present_fields.append(field)
                else:
                    missing_fields.append(field)
            
            if not missing_fields:
                self.log_test(
                    "Profil complet - tous les champs présents", 
                    True, 
                    f"{len(present_fields)}/12 champs présents"
                )
                return True
            else:
                self.log_test(
                    "Profil incomplet", 
                    False, 
                    f"Champs manquants: {missing_fields}"
                )
                return False
        else:
            self.log_test(
                "Échec vérification complétude", 
                False, 
                f"Status: {status}, Response: {response}"
            )
            return False

    def run_all_tests(self):
        """Exécuter tous les tests du système d'édition du nom d'entreprise"""
        print("🚀 DÉBUT DES TESTS - SYSTÈME D'ÉDITION DU NOM D'ENTREPRISE")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Utilisateur de test: {self.test_email}")
        print(f"Nouveau nom d'entreprise: {self.new_business_name}")
        print("=" * 80)
        
        # Séquence de tests
        test_sequence = [
            ("Authentification", self.test_authentication),
            ("Récupération profil actuel", self.test_get_current_business_profile),
            ("Mise à jour nom d'entreprise", self.test_update_business_name),
            ("Vérification persistance immédiate", self.test_verify_persistence_immediate),
            ("Vérification anti-régression", self.test_verify_no_revert_to_test_data),
            ("Tests multiples GET", self.test_multiple_get_requests),
            ("Vérification complétude profil", self.test_business_profile_completeness),
        ]
        
        # Exécuter les tests
        for test_name, test_func in test_sequence:
            try:
                test_func()
            except Exception as e:
                self.log_test(f"ERREUR dans {test_name}", False, f"Exception: {str(e)}")
        
        # Résumé final
        print("\n" + "=" * 80)
        print("📊 RÉSUMÉ DES TESTS")
        print("=" * 80)
        print(f"Tests exécutés: {self.tests_run}")
        print(f"Tests réussis: {self.tests_passed}")
        print(f"Tests échoués: {self.tests_run - self.tests_passed}")
        print(f"Taux de réussite: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
            print("✅ Le système d'édition du nom d'entreprise fonctionne correctement")
            print("✅ La persistance des données est assurée")
            print("✅ Pas de régression vers 'Restaurant Test Persistance'")
        else:
            print(f"\n⚠️ {self.tests_run - self.tests_passed} TEST(S) ONT ÉCHOUÉ")
            print("❌ Le système d'édition nécessite des corrections")
        
        print("=" * 80)
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = BusinessNameEditTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)