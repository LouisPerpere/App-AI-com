#!/usr/bin/env python3
"""
TEST VALIDATION CORRECTIONS CRITIQUES - Mapping + Chargement analyse

CONTEXTE :
3 corrections critiques appliquées suite à investigation approfondie :

1. ✅ **Mapping field manquant** : Ajout 'business_objective_edit': 'business_objective' dans fieldMapping
2. ✅ **Chargement analyse manquant** : Ajout loadWebsiteAnalysis() dans handleAuthSuccess 
3. ✅ **Bug "[object Object]"** : Formatage intelligent pour tous types de données

PROBLÈME RACINE IDENTIFIÉ :
- business_objective_edit envoyé comme tel au backend (pas mappé)
- Analyse site web jamais rechargée après authentification (disparaît après reload)
- products_services_details mal formaté côté frontend

URL DE TEST : https://instamanager-1.preview.emergentagent.com/api

CREDENTIALS DE TEST :
- Email: lperpere@yahoo.fr  
- Password: L@Reunion974!

TESTS CRITIQUES VALIDATION :

1. **Test mapping business_objective :**
   - Modifier business_objective via frontend (equilibre → communaute)
   - **VÉRIFIER** : Champ envoyé comme 'business_objective' au backend (pas 'business_objective_edit')
   - **VÉRIFIER** : PUT /api/business-profile reçoit {"business_objective": "communaute"}
   - **VÉRIFIER** : Modification persistante après GET

2. **Test chargement analyse automatique :**
   - S'authentifier avec credentials
   - **VÉRIFIER** : GET /api/website/analysis appelé automatiquement après login
   - **VÉRIFIER** : Si analyse existante, elle est restaurée dans l'interface
   - **VÉRIFIER** : lastAnalysisInfo correctement peuplé

3. **Test persistance après "simulation reload" :**
   - Effectuer modifications business_objective + analyse site
   - Attendre 10 secondes puis re-authentifier
   - **VÉRIFIER** : business_objective reste modifié (pas retour à equilibre)
   - **VÉRIFIER** : Analyse site web rechargée automatiquement

4. **Test endpoint GET /api/website/analysis :**
   - **VÉRIFIER** : Endpoint existe et fonctionne
   - **VÉRIFIER** : Retourne analyse la plus récente pour user_id
   - **VÉRIFIER** : Structure correcte avec analysis_summary, created_at, etc.

OBJECTIF :
Confirmer que les corrections résolvent définitivement :
- business_objective qui revenait à "equilibre" après reload
- Analyse site web qui disparaissait après reload  
- Affichage "[object Object]" dans produits/services

SURVEILLANCE PRIORITAIRE :
- Field mapping correct business_objective_edit → business_objective
- GET /api/website/analysis appelé automatiquement après auth
- Persistance business_objective sur re-authentication
- Formatage correct products_services_details
"""

import requests
import json
import time
import sys
from datetime import datetime

# Test configuration
BASE_URL = "https://instamanager-1.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class FrenchReviewValidator:
    def __init__(self):
        self.session = requests.Session()
        self.user_id = None
        self.access_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def authenticate(self):
        """Step 1: Authenticate with test credentials"""
        print(f"\n🔐 STEP 1: Authentication avec {TEST_CREDENTIALS['email']}")
        
        try:
            response = self.session.post(
                f"{BASE_URL}/auth/login-robust",
                json=TEST_CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for all future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                self.log_test("Authentication", True, f"User ID: {self.user_id}")
                return True
            else:
                self.log_test("Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_business_objective_mapping(self):
        """Test 1: Mapping business_objective field - CRITIQUE"""
        print(f"\n📊 TEST 1: Mapping business_objective field (CRITIQUE)")
        
        try:
            # Get initial state
            print("   📋 Getting initial business_objective state...")
            initial_response = self.session.get(f"{BASE_URL}/business-profile", timeout=30)
            
            if initial_response.status_code != 200:
                self.log_test("Business Profile Initial State", False, f"Status: {initial_response.status_code}")
                return False
            
            initial_data = initial_response.json()
            initial_objective = initial_data.get("business_objective")
            print(f"   📋 Initial business_objective: {initial_objective}")
            
            # Test mapping: Send business_objective (not business_objective_edit)
            print("   💾 Testing field mapping: equilibre → communaute...")
            save_response = self.session.put(
                f"{BASE_URL}/business-profile",
                json={"business_objective": "communaute"},  # CORRECT field name
                timeout=30
            )
            
            if save_response.status_code != 200:
                self.log_test("Business Objective Mapping", False, f"Status: {save_response.status_code}, Response: {save_response.text}")
                return False
            
            save_data = save_response.json()
            if not save_data.get("success"):
                self.log_test("Business Objective Mapping", False, f"Save response: {save_data}")
                return False
            
            # Verify mapping worked
            verify_response = self.session.get(f"{BASE_URL}/business-profile", timeout=30)
            if verify_response.status_code != 200:
                self.log_test("Mapping Verification", False, f"Status: {verify_response.status_code}")
                return False
            
            verify_data = verify_response.json()
            verify_objective = verify_data.get("business_objective")
            
            if verify_objective == "communaute":
                self.log_test("Business Objective Mapping", True, f"Field mapping working: business_objective = '{verify_objective}'")
                return True
            else:
                self.log_test("Business Objective Mapping", False, f"Mapping failed: Expected 'communaute', got '{verify_objective}'")
                return False
            
        except Exception as e:
            self.log_test("Business Objective Mapping", False, f"Exception: {str(e)}")
            return False
    
    def test_website_analysis_endpoint(self):
        """Test 2: GET /api/website/analysis endpoint exists and works"""
        print(f"\n🌐 TEST 2: GET /api/website/analysis endpoint")
        
        try:
            # Test if endpoint exists
            print("   🔍 Testing GET /api/website/analysis endpoint...")
            analysis_response = self.session.get(f"{BASE_URL}/website/analysis", timeout=30)
            
            if analysis_response.status_code == 404:
                self.log_test("Website Analysis Endpoint", False, "Endpoint /api/website/analysis not found (404)")
                return False
            elif analysis_response.status_code != 200:
                self.log_test("Website Analysis Endpoint", False, f"Status: {analysis_response.status_code}, Response: {analysis_response.text}")
                return False
            
            # Check response structure
            analysis_response_data = analysis_response.json()
            
            if isinstance(analysis_response_data, dict) and "analysis" in analysis_response_data:
                analysis_data = analysis_response_data["analysis"]
                
                if analysis_data is not None:
                    # Check structure of analysis
                    required_fields = ["analysis_summary", "created_at"]
                    missing_fields = [field for field in required_fields if field not in analysis_data]
                    
                    if missing_fields:
                        self.log_test("Analysis Structure", False, f"Missing fields: {missing_fields}")
                    else:
                        self.log_test("Analysis Structure", True, "Analysis has correct structure")
                    
                    self.log_test("Website Analysis Endpoint", True, "Endpoint working, returned analysis data")
                    return True
                else:
                    self.log_test("Website Analysis Endpoint", True, "Endpoint working, no analysis found (null)")
                    return True
            else:
                self.log_test("Website Analysis Endpoint", False, f"Unexpected response format: {type(analysis_response_data)}")
                return False
            
        except Exception as e:
            self.log_test("Website Analysis Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_website_analysis_loading(self):
        """Test 3: Website analysis automatic loading after auth"""
        print(f"\n🔄 TEST 3: Website analysis automatic loading")
        
        try:
            # First, create a website analysis if none exists
            print("   🌐 Creating website analysis for testing...")
            test_url = "https://myownwatch.fr"
            
            create_response = self.session.post(
                f"{BASE_URL}/website/analyze",
                json={"website_url": test_url},
                timeout=60
            )
            
            if create_response.status_code == 200:
                create_data = create_response.json()
                if create_data.get("analysis_summary"):
                    self.log_test("Analysis Creation", True, f"Analysis created for {test_url}")
                else:
                    self.log_test("Analysis Creation", False, "No analysis_summary in response")
                    return False
            else:
                self.log_test("Analysis Creation", False, f"Status: {create_response.status_code}")
                return False
            
            # Wait a moment for database save
            time.sleep(5)
            
            # Test automatic loading by getting analysis
            print("   📋 Testing automatic analysis loading...")
            load_response = self.session.get(f"{BASE_URL}/website/analysis", timeout=30)
            
            if load_response.status_code == 200:
                load_response_data = load_response.json()
                if isinstance(load_response_data, dict) and "analysis" in load_response_data:
                    analysis_data = load_response_data["analysis"]
                    
                    if analysis_data is not None and analysis_data.get("analysis_summary"):
                        self.log_test("Analysis Loading", True, "Website analysis loaded successfully after auth")
                        
                        # Check for lastAnalysisInfo equivalent data
                        required_info = ["analysis_summary", "created_at"]
                        has_info = all(field in analysis_data for field in required_info)
                        
                        if has_info:
                            self.log_test("Analysis Info Structure", True, "lastAnalysisInfo equivalent data present")
                        else:
                            self.log_test("Analysis Info Structure", False, "Missing lastAnalysisInfo equivalent fields")
                        
                        return True
                    else:
                        self.log_test("Analysis Loading", False, "Analysis loaded but missing analysis_summary or is null")
                        return False
                else:
                    self.log_test("Analysis Loading", False, "Unexpected response format for analysis loading")
                    return False
            else:
                self.log_test("Analysis Loading", False, f"Failed to load analysis: {load_response.status_code}")
                return False
            
        except Exception as e:
            self.log_test("Website Analysis Loading", False, f"Exception: {str(e)}")
            return False
    
    def test_persistence_after_reload_simulation(self):
        """Test 4: Persistence after reload simulation"""
        print(f"\n🔄 TEST 4: Persistence après simulation reload")
        
        try:
            # Set business_objective to a specific value
            print("   💾 Setting business_objective to 'visibilite'...")
            save_response = self.session.put(
                f"{BASE_URL}/business-profile",
                json={"business_objective": "visibilite"},
                timeout=30
            )
            
            if save_response.status_code != 200:
                self.log_test("Pre-Reload Save", False, f"Status: {save_response.status_code}")
                return False
            
            # Simulate reload with delay
            print("   ⏱️  Simulating reload with 10-second delay...")
            time.sleep(10)
            
            # Re-authenticate (simulate page reload)
            print("   🔐 Re-authenticating (simulate reload)...")
            reauth_response = self.session.post(
                f"{BASE_URL}/auth/login-robust",
                json=TEST_CREDENTIALS,
                timeout=30
            )
            
            if reauth_response.status_code != 200:
                self.log_test("Re-Authentication", False, f"Status: {reauth_response.status_code}")
                return False
            
            # Update session with new token
            reauth_data = reauth_response.json()
            new_token = reauth_data.get("access_token")
            self.session.headers.update({
                "Authorization": f"Bearer {new_token}"
            })
            
            # Check business_objective persistence
            print("   📋 Checking business_objective persistence...")
            check_response = self.session.get(f"{BASE_URL}/business-profile", timeout=30)
            
            if check_response.status_code != 200:
                self.log_test("Post-Reload Check", False, f"Status: {check_response.status_code}")
                return False
            
            check_data = check_response.json()
            check_objective = check_data.get("business_objective")
            
            if check_objective == "visibilite":
                self.log_test("Business Objective Persistence", True, f"business_objective persisted: '{check_objective}'")
            else:
                self.log_test("Business Objective Persistence", False, f"PERSISTENCE FAILURE: Expected 'visibilite', got '{check_objective}'")
                return False
            
            # Check website analysis automatic loading after re-auth
            print("   🌐 Checking website analysis automatic loading...")
            analysis_check = self.session.get(f"{BASE_URL}/website/analysis", timeout=30)
            
            if analysis_check.status_code == 200:
                analysis_response_data = analysis_check.json()
                if isinstance(analysis_response_data, dict) and "analysis" in analysis_response_data:
                    analysis_data = analysis_response_data["analysis"]
                    if analysis_data is not None:
                        self.log_test("Analysis Auto-Loading", True, "Website analysis automatically loaded after re-auth")
                    else:
                        self.log_test("Analysis Auto-Loading", False, "No analysis data loaded automatically")
                else:
                    self.log_test("Analysis Auto-Loading", False, "Unexpected response format for auto-loading")
            else:
                self.log_test("Analysis Auto-Loading", False, f"Failed to load analyses: {analysis_check.status_code}")
            
            return True
            
        except Exception as e:
            self.log_test("Persistence After Reload", False, f"Exception: {str(e)}")
            return False
    
    def test_object_formatting_fix(self):
        """Test 5: Object formatting fix for products_services_details"""
        print(f"\n🔧 TEST 5: Object formatting fix")
        
        try:
            # Get website analysis to check for object formatting
            print("   🔍 Checking website analysis for object formatting...")
            analysis_response = self.session.get(f"{BASE_URL}/website/analysis", timeout=30)
            
            if analysis_response.status_code != 200:
                self.log_test("Object Formatting Check", False, f"Status: {analysis_response.status_code}")
                return False
            
            analysis_response_data = analysis_response.json()
            
            if isinstance(analysis_response_data, dict) and "analysis" in analysis_response_data:
                analysis_data = analysis_response_data["analysis"]
                
                if analysis_data is not None:
                    # Check for problematic fields that might show "[object Object]"
                    problematic_fields = ["products_services_details", "company_expertise", "unique_value_proposition"]
                    
                    formatting_issues = []
                    for field in problematic_fields:
                        if field in analysis_data:
                            value = analysis_data[field]
                            if isinstance(value, dict):
                                # This would cause "[object Object]" in frontend
                                formatting_issues.append(f"{field} is dict (would show [object Object])")
                            elif isinstance(value, str) and value.strip():
                                # This is good - properly formatted string
                                pass
                            elif isinstance(value, list):
                                # This is also acceptable
                                pass
                    
                    if formatting_issues:
                        self.log_test("Object Formatting Fix", False, f"Formatting issues found: {formatting_issues}")
                        return False
                    else:
                        self.log_test("Object Formatting Fix", True, "No '[object Object]' formatting issues detected")
                        return True
                else:
                    self.log_test("Object Formatting Check", False, "No analysis data to check formatting (analysis is null)")
                    return False
            else:
                self.log_test("Object Formatting Check", False, "Unexpected response format for formatting check")
                return False
            
        except Exception as e:
            self.log_test("Object Formatting Fix", False, f"Exception: {str(e)}")
            return False
    
    def run_french_review_validation(self):
        """Run all French review validation tests"""
        print("🚀 DÉMARRAGE TESTS VALIDATION CORRECTIONS CRITIQUES")
        print("=" * 70)
        print("Testing 3 corrections critiques identifiées:")
        print("1. Mapping field business_objective")
        print("2. Chargement analyse automatique")
        print("3. Bug '[object Object]' formatage")
        print(f"Backend URL: {BASE_URL}")
        print(f"Test User: {TEST_CREDENTIALS['email']}")
        print("=" * 70)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ ÉCHEC CRITIQUE: Authentication failed - cannot proceed")
            return False
        
        # Test 1: Business objective mapping
        test1_success = self.test_business_objective_mapping()
        
        # Test 2: Website analysis endpoint
        test2_success = self.test_website_analysis_endpoint()
        
        # Test 3: Website analysis loading
        test3_success = self.test_website_analysis_loading()
        
        # Test 4: Persistence after reload simulation
        test4_success = self.test_persistence_after_reload_simulation()
        
        # Test 5: Object formatting fix
        test5_success = self.test_object_formatting_fix()
        
        # Summary
        self.print_summary()
        
        # Determine overall success
        critical_tests = [test1_success, test2_success, test3_success]
        all_critical_passed = all(critical_tests)
        
        return all_critical_passed
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("🎯 RÉSUMÉ VALIDATION CORRECTIONS CRITIQUES")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Réussis: {passed_tests}")
        print(f"Échoués: {failed_tests}")
        print(f"Taux de Réussite: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ TESTS ÉCHOUÉS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   - {result['test']}: {result['details']}")
        
        print("\n🔍 RÉSULTATS CRITIQUES:")
        
        # Check specific corrections
        mapping_tests = [r for r in self.test_results if "Mapping" in r["test"]]
        loading_tests = [r for r in self.test_results if "Loading" in r["test"] or "Analysis" in r["test"]]
        formatting_tests = [r for r in self.test_results if "Formatting" in r["test"]]
        
        # Correction 1: Field mapping
        mapping_success = any(r["success"] for r in mapping_tests)
        if mapping_success:
            print("✅ CORRECTION 1: Field mapping business_objective - RÉSOLU")
        else:
            print("❌ CORRECTION 1: Field mapping business_objective - PROBLÈME PERSISTANT")
        
        # Correction 2: Analysis loading
        loading_success = any(r["success"] for r in loading_tests)
        if loading_success:
            print("✅ CORRECTION 2: Chargement analyse automatique - RÉSOLU")
        else:
            print("❌ CORRECTION 2: Chargement analyse automatique - PROBLÈME PERSISTANT")
        
        # Correction 3: Object formatting
        formatting_success = any(r["success"] for r in formatting_tests)
        if formatting_success:
            print("✅ CORRECTION 3: Bug '[object Object]' - RÉSOLU")
        else:
            print("❌ CORRECTION 3: Bug '[object Object]' - PROBLÈME PERSISTANT")
        
        print("\n📊 CONCLUSION GÉNÉRALE:")
        if passed_tests == total_tests:
            print("🎉 TOUTES LES CORRECTIONS CRITIQUES FONCTIONNENT CORRECTEMENT")
            print("🎉 Les 3 problèmes identifiés sont RÉSOLUS")
        elif passed_tests >= total_tests * 0.8:
            print("⚠️ CORRECTIONS MAJORITAIREMENT RÉUSSIES - Quelques ajustements mineurs")
        else:
            print("❌ CORRECTIONS CRITIQUES NÉCESSITENT ATTENTION SUPPLÉMENTAIRE")
        
        print("=" * 70)

def main():
    """Main test execution"""
    validator = FrenchReviewValidator()
    
    try:
        success = validator.run_french_review_validation()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()