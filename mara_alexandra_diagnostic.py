#!/usr/bin/env python3
"""
DIAGNOSTIC URGENT - business_objective persistence test for mara.alexandra
Testing the specific issue where business_objective reverts from "communauté" to "equilibré"

CONTEXTE CRITIQUE:
Malgré les corrections appliquées, l'utilisateur "mara.alexandra" a modifié l'objectif à "communauté" 
mais après rechargement ça revient à "equilibré". Le problème de persistance n'est PAS résolu.

CREDENTIALS DE TEST:
- Email: mara.alexandra@gmail.com (utilisateur ayant le problème)  
- Password: [utiliser les credentials standards si disponibles]
- URL: https://instamanager-1.preview.emergentagent.com/api
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration de test
BASE_URL = "https://instamanager-1.preview.emergentagent.com/api"
TEST_EMAIL = "mara.alexandra@gmail.com"
TEST_PASSWORD = "password123"

class BusinessObjectiveDiagnostic:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.test_results = []
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} - {test_name}"
        if details:
            result += f": {details}"
        self.log(result)
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        
    def test_authentication(self):
        """Test 1: Authenticate mara.alexandra"""
        self.log("🔐 TEST 1: Authentication mara.alexandra")
        
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login-robust",
                json={
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            self.log(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                self.log_test("Authentication", True, f"User ID: {self.user_id}")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                return True
            else:
                self.log_test("Authentication", False, f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_current_business_objective(self):
        """Test 2: Check current business_objective value"""
        self.log("🔍 TEST 2: Current business_objective state")
        
        try:
            response = self.session.get(
                f"{self.base_url}/business-profile",
                timeout=30
            )
            
            self.log(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                current_objective = data.get("business_objective")
                
                self.log(f"   Current business_objective: '{current_objective}'")
                
                # Check if it's the problematic "equilibre" value
                if current_objective == "equilibre":
                    self.log_test("Current state check", False, "business_objective is 'equilibre' (should be 'communaute')")
                elif current_objective == "communaute":
                    self.log_test("Current state check", True, "business_objective is correctly set to 'communaute'")
                else:
                    self.log_test("Current state check", False, f"Unexpected business_objective value: '{current_objective}'")
                
                return current_objective
            else:
                self.log_test("Current state check", False, f"Status {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Current state check", False, f"Exception: {str(e)}")
            return None
    
    def test_manual_save(self):
        """Test 3: Manual save of business_objective to 'communaute'"""
        self.log("💾 TEST 3: Manual save business_objective to 'communaute'")
        
        try:
            response = self.session.put(
                f"{self.base_url}/business-profile",
                json={
                    "business_objective": "communaute"
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            self.log(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Manual save", True, f"Save successful: {data}")
                return True
            else:
                self.log_test("Manual save", False, f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Manual save", False, f"Exception: {str(e)}")
            return False
    
    def test_immediate_verification(self):
        """Test 4: Immediate verification after save"""
        self.log("🔍 TEST 4: Immediate verification after save")
        
        try:
            response = self.session.get(
                f"{self.base_url}/business-profile",
                timeout=30
            )
            
            self.log(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                current_objective = data.get("business_objective")
                
                self.log(f"   Current business_objective: '{current_objective}'")
                
                if current_objective == "communaute":
                    self.log_test("Immediate verification", True, "Value correctly saved as 'communaute'")
                    return True
                else:
                    self.log_test("Immediate verification", False, f"Expected 'communaute', got '{current_objective}'")
                    return False
            else:
                self.log_test("Immediate verification", False, f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Immediate verification", False, f"Exception: {str(e)}")
            return False
    
    def test_persistence_after_delay(self):
        """Test 5: Persistence after 10 second delay (simulating refresh)"""
        self.log("⏱️ TEST 5: Persistence after 10 second delay (simulating refresh)")
        
        self.log("   Waiting 10 seconds...")
        time.sleep(10)
        
        try:
            response = self.session.get(
                f"{self.base_url}/business-profile",
                timeout=30
            )
            
            self.log(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                current_objective = data.get("business_objective")
                
                self.log(f"   Current business_objective after delay: '{current_objective}'")
                
                if current_objective == "communaute":
                    self.log_test("Persistence after delay", True, "Value remains 'communaute' after delay")
                    return True
                elif current_objective == "equilibre":
                    self.log_test("Persistence after delay", False, "Value reverted to 'equilibre' - BUG CONFIRMED")
                    return False
                else:
                    self.log_test("Persistence after delay", False, f"Got '{current_objective}' instead of 'communaute'")
                    return False
            else:
                self.log_test("Persistence after delay", False, f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Persistence after delay", False, f"Exception: {str(e)}")
            return False
    
    def test_database_direct_check(self):
        """Test 6: Additional diagnostic information"""
        self.log("🔍 TEST 6: Additional diagnostic information")
        
        try:
            # Get user info
            response = self.session.get(
                f"{self.base_url}/auth/me",
                timeout=30
            )
            
            if response.status_code == 200:
                user_data = response.json()
                self.log(f"   User data: {user_data}")
            else:
                self.log(f"   Could not get user data: {response.text}")
            
            # Test health check
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=30
            )
            
            if response.status_code == 200:
                health_data = response.json()
                self.log(f"   Backend health: {health_data}")
            else:
                self.log(f"   Backend health check failed: {response.text}")
                
        except Exception as e:
            self.log(f"   ❌ Diagnostic error: {str(e)}")
    
    def run_full_diagnostic(self):
        """Run complete diagnostic test suite"""
        self.log("🚨 STARTING URGENT DIAGNOSTIC - business_objective persistence for mara.alexandra")
        self.log("=" * 80)
        
        results = {
            "authentication": False,
            "current_state": None,
            "manual_save": False,
            "immediate_verification": False,
            "persistence_after_delay": False
        }
        
        # Test 1: Authentication
        if not self.test_authentication():
            self.log("❌ CRITICAL: Cannot authenticate mara.alexandra - stopping diagnostic")
            return results
        
        results["authentication"] = True
        
        # Test 2: Current state
        current_objective = self.test_current_business_objective()
        results["current_state"] = current_objective
        
        # Test 3: Manual save
        if self.test_manual_save():
            results["manual_save"] = True
            
            # Test 4: Immediate verification
            if self.test_immediate_verification():
                results["immediate_verification"] = True
                
                # Test 5: Persistence after delay
                if self.test_persistence_after_delay():
                    results["persistence_after_delay"] = True
        
        # Test 6: Additional diagnostics
        self.test_database_direct_check()
        
        # Summary
        self.log("=" * 80)
        self.log("🎯 DIAGNOSTIC SUMMARY:")
        self.log(f"   Authentication: {'✅ PASS' if results['authentication'] else '❌ FAIL'}")
        self.log(f"   Current state: {results['current_state']}")
        self.log(f"   Manual save: {'✅ PASS' if results['manual_save'] else '❌ FAIL'}")
        self.log(f"   Immediate verification: {'✅ PASS' if results['immediate_verification'] else '❌ FAIL'}")
        self.log(f"   Persistence after delay: {'✅ PASS' if results['persistence_after_delay'] else '❌ FAIL'}")
        
        # Root cause analysis
        if not results["persistence_after_delay"] and results["immediate_verification"]:
            self.log("🚨 ROOT CAUSE IDENTIFIED: business_objective saves correctly but reverts after delay")
            self.log("   This suggests a caching issue or default value override in GET endpoint")
        elif not results["immediate_verification"] and results["manual_save"]:
            self.log("🚨 ROOT CAUSE IDENTIFIED: PUT endpoint claims success but doesn't actually save")
            self.log("   This suggests a database write issue or field mapping problem")
        elif not results["manual_save"]:
            self.log("🚨 ROOT CAUSE IDENTIFIED: PUT endpoint is failing to save business_objective")
            self.log("   This suggests a validation or database connection issue")
        
        return results

def main():
    """Main diagnostic function"""
    diagnostic = BusinessObjectiveDiagnostic()
    results = diagnostic.run_full_diagnostic()
    
    # Return exit code based on results
    if results["persistence_after_delay"]:
        print("\n✅ DIAGNOSTIC RESULT: business_objective persistence is WORKING")
        return 0
    else:
        print("\n❌ DIAGNOSTIC RESULT: business_objective persistence is BROKEN")
        return 1

if __name__ == "__main__":
    exit(main())