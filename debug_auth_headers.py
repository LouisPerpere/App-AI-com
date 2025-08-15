#!/usr/bin/env python3
"""
Debug script pour identifier les requêtes sans Authorization headers
qui causent le retour aux données demo
"""

import requests
import json
import time

# Configuration
BACKEND_URL = "http://localhost:8001"
API_URL = f"{BACKEND_URL}/api"

def login_and_get_token():
    """Login et récupération du token"""
    print("🔐 Test 1: Login pour obtenir le token")
    
    login_data = {
        "email": "lperpere@yahoo.fr", 
        "password": "L@Reunion974!"
    }
    
    response = requests.post(f"{API_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        data = response.json()
        token = data.get('access_token')
        print(f"✅ Login réussi, token récupéré: {token[:20]}...")
        return token
    else:
        print(f"❌ Login échoué: {response.status_code}")
        return None

def test_business_profile_with_token(token):
    """Test business profile AVEC token Authorization"""
    print("\n📋 Test 2: GET /api/business-profile AVEC Authorization header")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(f"{API_URL}/business-profile", headers=headers)
    if response.status_code == 200:
        data = response.json()
        business_name = data.get('business_name', '')
        email = data.get('email', '')
        print(f"✅ Succès: business_name='{business_name}', email='{email}'")
        
        if business_name == "Demo Business":
            print("❌ PROBLÈME: Retourne des données demo malgré l'Authorization header!")
            return False
        else:
            print("✅ OK: Retourne des vraies données utilisateur")
            return True
    else:
        print(f"❌ Erreur: {response.status_code}")
        return False

def test_business_profile_without_token():
    """Test business profile SANS token Authorization"""
    print("\n🚫 Test 3: GET /api/business-profile SANS Authorization header")
    
    response = requests.get(f"{API_URL}/business-profile")
    if response.status_code == 200:
        data = response.json()
        business_name = data.get('business_name', '')
        email = data.get('email', '')
        print(f"✅ Réponse: business_name='{business_name}', email='{email}'")
        
        if business_name == "Demo Business":
            print("✅ OK: Retourne correctement des données demo sans token")
            return True
        else:
            print("❌ PROBLÈME: Devrait retourner des données demo sans token!")
            return False
    else:
        print(f"❌ Erreur: {response.status_code}")
        return False

def test_update_business_profile(token):
    """Test update business profile pour voir la persistance"""
    print("\n💾 Test 4: PUT /api/business-profile pour tester la persistance")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Données de test avec timestamp unique
    timestamp = int(time.time())
    test_data = {
        "business_name": f"Test Persistance {timestamp}",
        "business_type": "restaurant",
        "business_description": f"Description test {timestamp}",
        "target_audience": "Clients test",
        "brand_tone": "professional",
        "posting_frequency": "weekly",
        "preferred_platforms": ["Facebook", "Instagram"],
        "budget_range": "1000-2000€",
        "email": f"test.{timestamp}@example.com",
        "website_url": f"https://test{timestamp}.com",
        "hashtags_primary": ["test", "persistance"],
        "hashtags_secondary": ["debug"]
    }
    
    # PUT pour mettre à jour
    response = requests.put(f"{API_URL}/business-profile", json=test_data, headers=headers)
    if response.status_code == 200:
        print(f"✅ PUT réussi")
        
        # Immédiatement après, faire un GET pour vérifier
        time.sleep(0.5)
        get_response = requests.get(f"{API_URL}/business-profile", headers=headers)
        if get_response.status_code == 200:
            get_data = get_response.json()
            returned_name = get_data.get('business_name', '')
            returned_email = get_data.get('email', '')
            returned_description = get_data.get('business_description', '')
            
            print(f"✅ GET après PUT: name='{returned_name}', email='{returned_email}', description='{returned_description}'")
            
            # Vérifier si les données ont persisté
            if returned_name == test_data["business_name"]:
                print("✅ OK: business_name a persisté")
            else:
                print(f"❌ PROBLÈME: business_name esperé='{test_data['business_name']}', reçu='{returned_name}'")
            
            if returned_email == test_data["email"]:
                print("✅ OK: email a persisté")
            else:
                print(f"❌ PROBLÈME: email esperé='{test_data['email']}', reçu='{returned_email}'")
            
            if returned_description == test_data["business_description"]:
                print("✅ OK: business_description a persisté")
            else:
                print(f"❌ PROBLÈME: description esperée='{test_data['business_description']}', reçue='{returned_description}'")
            
            return returned_name != "Demo Business"
        else:
            print(f"❌ GET après PUT échoué: {get_response.status_code}")
            return False
    else:
        print(f"❌ PUT échoué: {response.status_code}")
        return False

def main():
    print("🔍 DEBUG: Test des headers Authorization et persistance des données")
    print("=" * 80)
    
    # Test 1: Login
    token = login_and_get_token()
    if not token:
        return
    
    # Test 2: Business profile avec token
    test_business_profile_with_token(token)
    
    # Test 3: Business profile sans token  
    test_business_profile_without_token()
    
    # Test 4: Update et vérification persistance
    test_update_business_profile(token)
    
    print("\n🔍 Vérifiez maintenant les logs backend pour voir les requêtes sans Authorization header:")
    print("tail -f /var/log/supervisor/backend.out.log")

if __name__ == "__main__":
    main()