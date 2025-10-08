#!/usr/bin/env python3
"""
🚨 SECURITY FIX VALIDATION TEST - /content/pending-temp Endpoint
Test de validation de la correction de sécurité pour l'endpoint /content/pending-temp

CONTEXTE CRITIQUE:
- Correction appliquée: Remplacement du user_id hardcodé par authentification appropriée
- Endpoint utilise maintenant get_current_user_id_robust au lieu du hardcodé lperpere@yahoo.fr
- Test d'isolation des données entre comptes utilisateurs

OBJECTIFS DE TEST:
1. Vérifier que test@claire-marcus.com ne voit que ses propres données
2. Vérifier que lperpere@yahoo.fr ne voit que ses propres données  
3. Confirmer l'isolation complète des données entre comptes
4. Vérifier que l'endpoint requiert maintenant l'authentification
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://claire-marcus.com/api"

# Comptes de test
TEST_ACCOUNTS = {
    "test": {
        "email": "test@claire-marcus.com",
        "password": "test123!",
        "name": "Test Account"
    },
    "lperpere": {
        "email": "lperpere@yahoo.fr", 
        "password": "L@Reunion974!",
        "name": "LPerpere Account"
    }
}

class SecurityTestRunner:
    def __init__(self):
        self.results = []
        self.tokens = {}
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_step(self, step_name, success, details=""):
        result = "✅ PASS" if success else "❌ FAIL"
        self.log(f"{result} - {step_name}")
        if details:
            self.log(f"    Details: {details}")
        self.results.append({
            "step": step_name,
            "success": success,
            "details": details
        })
        return success
        
    def authenticate_user(self, account_key):
        """Authentifier un utilisateur et récupérer son token"""
        account = TEST_ACCOUNTS[account_key]
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login-robust",
                json={
                    "email": account["email"],
                    "password": account["password"]
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                user_id = data.get("user_id")
                
                if token and user_id:
                    self.tokens[account_key] = {
                        "token": token,
                        "user_id": user_id,
                        "email": account["email"]
                    }
                    return self.test_step(
                        f"Authentication {account['name']}", 
                        True,
                        f"User ID: {user_id}, Token: {token[:20]}..."
                    )
                else:
                    return self.test_step(
                        f"Authentication {account['name']}", 
                        False,
                        "Missing token or user_id in response"
                    )
            else:
                return self.test_step(
                    f"Authentication {account['name']}", 
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            return self.test_step(
                f"Authentication {account['name']}", 
                False,
                f"Exception: {str(e)}"
            )
    
    def test_endpoint_without_auth(self):
        """Tester l'endpoint sans authentification (doit échouer)"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/content/pending-temp",
                timeout=10
            )
            
            # L'endpoint doit maintenant requérir l'authentification
            if response.status_code == 401:
                return self.test_step(
                    "Endpoint requires authentication",
                    True,
                    "Correctly returns 401 without auth token"
                )
            else:
                return self.test_step(
                    "Endpoint requires authentication",
                    False,
                    f"Expected 401, got {response.status_code}: {response.text[:200]}"
                )
                
        except Exception as e:
            return self.test_step(
                "Endpoint requires authentication",
                False,
                f"Exception: {str(e)}"
            )
    
    def get_user_content(self, account_key):
        """Récupérer le contenu pour un utilisateur authentifié"""
        if account_key not in self.tokens:
            return None, "User not authenticated"
            
        token_info = self.tokens[account_key]
        
        try:
            headers = {
                "Authorization": f"Bearer {token_info['token']}"
            }
            
            response = requests.get(
                f"{BACKEND_URL}/content/pending-temp",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                total = data.get("total", 0)
                
                return {
                    "success": True,
                    "content": content,
                    "total": total,
                    "user_id": token_info["user_id"],
                    "email": token_info["email"]
                }, None
            else:
                return None, f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            return None, f"Exception: {str(e)}"
    
    def test_data_isolation(self):
        """Test principal: Vérifier l'isolation des données entre comptes"""
        
        # Récupérer les données pour chaque compte
        test_data, test_error = self.get_user_content("test")
        lperpere_data, lperpere_error = self.get_user_content("lperpere")
        
        if test_error:
            self.test_step("Get test account data", False, test_error)
            return False
            
        if lperpere_error:
            self.test_step("Get lperpere account data", False, lperpere_error)
            return False
        
        # Vérifier que les données ont été récupérées
        self.test_step(
            "Get test account data", 
            True,
            f"Retrieved {test_data['total']} items for {test_data['email']}"
        )
        
        self.test_step(
            "Get lperpere account data", 
            True,
            f"Retrieved {lperpere_data['total']} items for {lperpere_data['email']}"
        )
        
        # CRITIQUE: Vérifier que les user_ids sont différents
        test_user_id = test_data["user_id"]
        lperpere_user_id = lperpere_data["user_id"]
        
        different_users = test_user_id != lperpere_user_id
        self.test_step(
            "Users have different IDs",
            different_users,
            f"Test: {test_user_id}, LPerpere: {lperpere_user_id}"
        )
        
        # CRITIQUE: Vérifier l'isolation des données
        test_content_ids = set()
        lperpere_content_ids = set()
        
        for item in test_data["content"]:
            test_content_ids.add(item.get("id", ""))
            
        for item in lperpere_data["content"]:
            lperpere_content_ids.add(item.get("id", ""))
        
        # Vérifier qu'il n'y a pas de chevauchement de contenu
        overlap = test_content_ids.intersection(lperpere_content_ids)
        no_overlap = len(overlap) == 0
        
        self.test_step(
            "No content overlap between accounts",
            no_overlap,
            f"Test content IDs: {len(test_content_ids)}, LPerpere: {len(lperpere_content_ids)}, Overlap: {len(overlap)}"
        )
        
        if overlap:
            self.log(f"⚠️ SECURITY ISSUE: Overlapping content IDs: {list(overlap)[:5]}", "ERROR")
        
        # Vérifier que chaque compte a des données différentes
        if test_data["total"] > 0 and lperpere_data["total"] > 0:
            # Comparer les premiers éléments pour s'assurer qu'ils sont différents
            test_first = test_data["content"][0] if test_data["content"] else {}
            lperpere_first = lperpere_data["content"][0] if lperpere_data["content"] else {}
            
            different_content = test_first.get("id") != lperpere_first.get("id")
            self.test_step(
                "Accounts have different content",
                different_content,
                f"Test first ID: {test_first.get('id', 'None')}, LPerpere first ID: {lperpere_first.get('id', 'None')}"
            )
        
        return no_overlap and different_users
    
    def test_response_consistency(self):
        """Vérifier que les réponses sont cohérentes pour chaque utilisateur"""
        
        # Faire plusieurs appels pour chaque utilisateur
        for account_key in ["test", "lperpere"]:
            account = TEST_ACCOUNTS[account_key]
            
            # Premier appel
            data1, error1 = self.get_user_content(account_key)
            if error1:
                self.test_step(f"Consistency test {account['name']} - Call 1", False, error1)
                continue
                
            # Deuxième appel
            data2, error2 = self.get_user_content(account_key)
            if error2:
                self.test_step(f"Consistency test {account['name']} - Call 2", False, error2)
                continue
            
            # Vérifier la cohérence
            same_total = data1["total"] == data2["total"]
            same_user_id = data1["user_id"] == data2["user_id"]
            
            consistent = same_total and same_user_id
            self.test_step(
                f"Response consistency {account['name']}",
                consistent,
                f"Total: {data1['total']} vs {data2['total']}, User ID consistent: {same_user_id}"
            )
    
    def run_all_tests(self):
        """Exécuter tous les tests de sécurité"""
        self.log("🚨 STARTING SECURITY FIX VALIDATION TESTS", "INFO")
        self.log("=" * 60)
        
        # Test 1: Vérifier que l'endpoint requiert l'authentification
        self.log("\n📋 TEST 1: Authentication Requirement")
        self.test_endpoint_without_auth()
        
        # Test 2: Authentifier les deux comptes
        self.log("\n📋 TEST 2: User Authentication")
        test_auth = self.authenticate_user("test")
        lperpere_auth = self.authenticate_user("lperpere")
        
        if not (test_auth and lperpere_auth):
            self.log("❌ Cannot proceed without authentication", "ERROR")
            return False
        
        # Test 3: Test principal d'isolation des données
        self.log("\n📋 TEST 3: Data Isolation Verification")
        isolation_success = self.test_data_isolation()
        
        # Test 4: Test de cohérence des réponses
        self.log("\n📋 TEST 4: Response Consistency")
        self.test_response_consistency()
        
        # Résumé des résultats
        self.log("\n" + "=" * 60)
        self.log("🎯 SECURITY TEST RESULTS SUMMARY")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        
        self.log(f"Total Tests: {total_tests}")
        self.log(f"Passed: {passed_tests} ✅")
        self.log(f"Failed: {failed_tests} ❌")
        
        if failed_tests == 0:
            self.log("🎉 ALL SECURITY TESTS PASSED - DATA ISOLATION CONFIRMED", "SUCCESS")
            return True
        else:
            self.log("🚨 SECURITY TESTS FAILED - POTENTIAL DATA LEAKAGE", "ERROR")
            
            # Afficher les échecs
            for result in self.results:
                if not result["success"]:
                    self.log(f"❌ FAILED: {result['step']} - {result['details']}", "ERROR")
            
            return False

def main():
    """Point d'entrée principal"""
    print("🚨 SECURITY FIX VALIDATION - /content/pending-temp Endpoint")
    print("Testing data isolation between user accounts after security fix")
    print("=" * 80)
    
    runner = SecurityTestRunner()
    success = runner.run_all_tests()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ SECURITY FIX VALIDATION: SUCCESS")
        print("✅ Data isolation is working correctly")
        print("✅ No data leakage detected between accounts")
        sys.exit(0)
    else:
        print("❌ SECURITY FIX VALIDATION: FAILED")
        print("❌ Potential security issues detected")
        print("❌ Manual investigation required")
        sys.exit(1)

if __name__ == "__main__":
    main()