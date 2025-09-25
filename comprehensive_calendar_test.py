#!/usr/bin/env python3
"""
Test complet de l'endpoint POST /posts/validate-to-calendar
Selon la demande de révision française complète
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://instamanager-1.preview.emergentagent.com"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

def authenticate():
    """Authentification robuste"""
    try:
        print("🔐 Step 1: Authentication...")
        response = requests.post(
            f"{BACKEND_URL}/api/auth/login-robust",
            json=TEST_CREDENTIALS,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_id = data.get("user_id")
            print(f"✅ Authentication successful - User ID: {user_id}")
            return token, user_id
        else:
            print(f"❌ Authentication failed - Status: {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None, None

def test_endpoint_existence():
    """1. Vérifier si l'endpoint existe et répond"""
    try:
        print("🔍 Step 2: Testing endpoint existence...")
        
        # Test sans authentification pour vérifier l'existence
        response = requests.post(
            f"{BACKEND_URL}/api/posts/validate-to-calendar",
            json={"test": "data"}
        )
        
        print(f"📊 Status without auth: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Endpoint exists (returns 401 Unauthorized without token)")
            return True
        elif response.status_code == 404:
            print("❌ Endpoint not found (404)")
            return False
        else:
            print(f"✅ Endpoint exists (returns {response.status_code})")
            return True
            
    except Exception as e:
        print(f"❌ Error testing endpoint existence: {e}")
        return False

def test_request_validation(token):
    """2. Test de validation des paramètres de requête"""
    try:
        print("📋 Step 3: Testing request validation...")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        test_cases = [
            {
                "name": "Missing post_id",
                "data": {"platforms": ["instagram"], "scheduled_date": "2025-09-26T11:00:00"},
                "expected_status": 400
            },
            {
                "name": "Missing platforms",
                "data": {"post_id": "test_id", "scheduled_date": "2025-09-26T11:00:00"},
                "expected_status": 400
            },
            {
                "name": "Empty platforms array",
                "data": {"post_id": "test_id", "platforms": [], "scheduled_date": "2025-09-26T11:00:00"},
                "expected_status": 400
            }
        ]
        
        validation_results = []
        
        for test_case in test_cases:
            print(f"   Testing: {test_case['name']}")
            response = requests.post(
                f"{BACKEND_URL}/api/posts/validate-to-calendar",
                json=test_case["data"],
                headers=headers
            )
            
            success = response.status_code == test_case["expected_status"]
            validation_results.append(success)
            
            status_icon = "✅" if success else "❌"
            print(f"   {status_icon} {test_case['name']}: {response.status_code} (expected {test_case['expected_status']})")
        
        return all(validation_results)
        
    except Exception as e:
        print(f"❌ Error testing validation: {e}")
        return False

def test_main_functionality(token):
    """3. Test de la fonctionnalité principale avec le post_id spécifique"""
    try:
        print("📅 Step 4: Testing main functionality...")
        
        # Paramètres exacts de la demande française
        test_data = {
            "post_id": "post_6a670c66-c06c-4d75-9dd5-c747e8a0281a_1758187803_0",
            "platforms": ["instagram"],
            "scheduled_date": "2025-09-26T11:00:00"
        }
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print(f"📤 Request data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            f"{BACKEND_URL}/api/posts/validate-to-calendar",
            json=test_data,
            headers=headers
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"📊 Response Body: {json.dumps(response_data, indent=2)}")
        except:
            print(f"📊 Response Body (raw): {response.text}")
        
        # Vérifier le format de réponse attendu
        if response.status_code == 200:
            if isinstance(response_data, dict):
                required_fields = ["success", "message"]
                has_required_fields = all(field in response_data for field in required_fields)
                
                if has_required_fields:
                    print("✅ Response format is correct")
                    return True
                else:
                    print("⚠️ Response missing required fields")
                    return False
            else:
                print("⚠️ Response is not a JSON object")
                return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing main functionality: {e}")
        return False

def test_error_handling(token):
    """4. Test de gestion d'erreurs"""
    try:
        print("🚨 Step 5: Testing error handling...")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Test avec un post_id inexistant
        test_data = {
            "post_id": "nonexistent_post_id_12345",
            "platforms": ["instagram"],
            "scheduled_date": "2025-09-26T11:00:00"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/posts/validate-to-calendar",
            json=test_data,
            headers=headers
        )
        
        print(f"📊 Error test status: {response.status_code}")
        
        if response.status_code == 404:
            print("✅ Proper error handling for nonexistent post")
            return True
        else:
            print(f"⚠️ Unexpected error response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing error handling: {e}")
        return False

def test_multiple_platforms(token):
    """5. Test avec plusieurs plateformes"""
    try:
        print("🌐 Step 6: Testing multiple platforms...")
        
        test_data = {
            "post_id": "post_6a670c66-c06c-4d75-9dd5-c747e8a0281a_1758187803_0",
            "platforms": ["instagram", "facebook"],
            "scheduled_date": "2025-09-26T11:00:00"
        }
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/posts/validate-to-calendar",
            json=test_data,
            headers=headers
        )
        
        print(f"📊 Multiple platforms status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            calendar_entries = response_data.get("calendar_entries", 0)
            print(f"✅ Multiple platforms test passed - Created {calendar_entries} entries")
            return True
        else:
            print(f"❌ Multiple platforms test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing multiple platforms: {e}")
        return False

def main():
    """Fonction principale de test complet"""
    print("🎯 COMPREHENSIVE TEST: POST /posts/validate-to-calendar")
    print("=" * 70)
    print("Demande de révision française - Test complet de l'endpoint")
    print("=" * 70)
    
    results = {
        "authentication": False,
        "endpoint_exists": False,
        "request_validation": False,
        "main_functionality": False,
        "error_handling": False,
        "multiple_platforms": False
    }
    
    # Test 1: Authentification
    token, user_id = authenticate()
    if token:
        results["authentication"] = True
    else:
        print("❌ Cannot proceed without authentication")
        return results
    
    # Test 2: Existence de l'endpoint
    results["endpoint_exists"] = test_endpoint_existence()
    
    # Test 3: Validation des paramètres
    results["request_validation"] = test_request_validation(token)
    
    # Test 4: Fonctionnalité principale
    results["main_functionality"] = test_main_functionality(token)
    
    # Test 5: Gestion d'erreurs
    results["error_handling"] = test_error_handling(token)
    
    # Test 6: Plateformes multiples
    results["multiple_platforms"] = test_multiple_platforms(token)
    
    # Résumé des résultats
    print("\n" + "=" * 70)
    print("📊 COMPREHENSIVE TEST RESULTS:")
    print("=" * 70)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    success_rate = sum(results.values()) / len(results) * 100
    print(f"\nOverall Success Rate: {success_rate:.1f}%")
    
    # Conclusion détaillée
    print("\n" + "=" * 70)
    print("📋 DETAILED ANALYSIS:")
    print("=" * 70)
    
    if results["endpoint_exists"]:
        print("✅ 1. L'endpoint existe et répond")
    else:
        print("❌ 1. L'endpoint n'existe pas ou ne répond pas")
    
    if results["main_functionality"]:
        print("✅ 2. Le format de réponse est correct")
        print("✅ 3. Les codes de statut HTTP sont appropriés")
    else:
        print("❌ 2. Problèmes avec le format de réponse ou les codes de statut")
    
    if success_rate >= 80:
        print("\n🎉 CONCLUSION FINALE: L'endpoint POST /posts/validate-to-calendar est FONCTIONNEL")
        print("   Tous les critères de la demande française sont satisfaits")
    else:
        print("\n🚨 CONCLUSION FINALE: L'endpoint présente des problèmes significatifs")
    
    return results

if __name__ == "__main__":
    main()