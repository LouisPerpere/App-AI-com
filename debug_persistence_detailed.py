#!/usr/bin/env python3
"""
Debug script pour analyser exactement quelles données sont retournées 
par l'API business-profile et pourquoi seul website_url persiste
"""

import requests
import json

# Configuration
BACKEND_URL = "http://localhost:8001"
API_URL = f"{BACKEND_URL}/api"

def detailed_business_profile_analysis():
    """Analyse détaillée du profil business"""
    
    # 1. Login
    print("🔐 Step 1: Login")
    login_data = {"email": "lperpere@yahoo.fr", "password": "L@Reunion974!"}
    response = requests.post(f"{API_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return
    
    token = response.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    print(f"✅ Login successful")
    
    # 2. GET current business profile
    print("\n📋 Step 2: GET current business profile")
    response = requests.get(f"{API_URL}/business-profile", headers=headers)
    if response.status_code != 200:
        print(f"❌ GET failed: {response.status_code}")
        return
    
    original_profile = response.json()
    print("Current Profile Data:")
    for key, value in original_profile.items():
        # Highlight empty vs non-empty values
        status = "✅ HAS VALUE" if value else "❌ EMPTY"
        print(f"  {key}: '{value}' ({status})")
    
    # 3. PUT with test data
    print("\n💾 Step 3: PUT test data")
    test_data = {
        "business_name": "TEST UNIQUE 12345",
        "business_type": "restaurant", 
        "business_description": "TEST DESCRIPTION 12345",
        "target_audience": "TEST AUDIENCE 12345",
        "brand_tone": "professional",
        "posting_frequency": "weekly",
        "preferred_platforms": ["Facebook", "Instagram"],
        "budget_range": "TEST BUDGET 12345",
        "email": "test12345@example.com",
        "website_url": "https://test12345.com",
        "hashtags_primary": ["test"],
        "hashtags_secondary": ["debug"]
    }
    
    response = requests.put(f"{API_URL}/business-profile", json=test_data, headers=headers)
    if response.status_code != 200:
        print(f"❌ PUT failed: {response.status_code} - {response.text}")
        return
    
    put_response = response.json()
    print("✅ PUT successful")
    print("PUT Response Data:")
    for key, value in put_response.items():
        print(f"  {key}: '{value}'")
    
    # 4. Immediate GET to verify persistence
    print("\n🔍 Step 4: Immediate GET to verify persistence")
    response = requests.get(f"{API_URL}/business-profile", headers=headers)
    if response.status_code != 200:
        print(f"❌ GET after PUT failed: {response.status_code}")
        return
    
    after_put_profile = response.json()
    print("Profile After PUT:")
    
    # Compare each field
    print("\n📊 FIELD-BY-FIELD COMPARISON:")
    print("Field Name               | Expected Value      | Actual Value        | Status")
    print("-" * 85)
    
    persistence_results = {}
    
    for key in test_data.keys():
        expected = test_data[key]
        actual = after_put_profile.get(key, 'MISSING')
        
        if actual == expected:
            status = "✅ PERSISTED"
            persistence_results[key] = True
        else:
            status = "❌ LOST/CHANGED"
            persistence_results[key] = False
        
        print(f"{key:<24} | {str(expected):<18} | {str(actual):<18} | {status}")
    
    # 5. Summary
    print(f"\n📈 PERSISTENCE SUMMARY:")
    persisted_count = sum(persistence_results.values())
    total_count = len(persistence_results)
    print(f"Persisted fields: {persisted_count}/{total_count}")
    
    if persisted_count == total_count:
        print("✅ ALL FIELDS PERSIST CORRECTLY")
        print("🔍 Issue must be in frontend logic, not backend storage")
    else:
        print("❌ BACKEND PERSISTENCE ISSUE CONFIRMED")
        failed_fields = [k for k, v in persistence_results.items() if not v]
        print(f"Failed fields: {failed_fields}")
        
        # Special check for website_url
        if persistence_results.get('website_url', False) and len(failed_fields) > 0:
            print("🎯 CONFIRMED: website_url persists but other fields don't")
            print("This suggests selective persistence logic in backend")
    
    return persistence_results

if __name__ == "__main__":
    print("🔍 DETAILED BUSINESS PROFILE PERSISTENCE ANALYSIS")
    print("=" * 80)
    
    results = detailed_business_profile_analysis()
    
    if results:
        website_persists = results.get('website_url', False)
        others_persist = all(v for k, v in results.items() if k != 'website_url')
        
        if website_persists and not others_persist:
            print("\n🎯 HYPOTHESIS CONFIRMED: Only website_url persists")
            print("📋 Next step: Examine why backend treats website_url differently")
        elif all(results.values()):
            print("\n🤔 HYPOTHESIS REJECTED: All fields persist in backend")
            print("📋 Next step: Issue is in frontend data loading logic")
        else:
            print(f"\n📊 Mixed results - some fields persist, others don't")