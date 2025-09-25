#!/usr/bin/env python3
"""
Test spécifique avec le post_id exact mentionné dans la demande française
"""

import requests
import json

# Configuration
BACKEND_URL = "https://instamanager-1.preview.emergentagent.com"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

def test_specific_post_id():
    """Test avec le post_id spécifique de la demande"""
    try:
        # Authentification
        print("🔐 Authentication...")
        auth_response = requests.post(
            f"{BACKEND_URL}/api/auth/login-robust",
            json=TEST_CREDENTIALS
        )
        
        if auth_response.status_code != 200:
            print(f"❌ Authentication failed: {auth_response.status_code}")
            return False
            
        token = auth_response.json().get("access_token")
        
        # Test avec le post_id spécifique
        print("📅 Testing with specific post_id from French request...")
        
        test_data = {
            "post_id": "post_6a670c66-c06c-4d75-9dd5-c747e8a0281a_1758187803_0",
            "platforms": ["instagram"],
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
        
        print(f"📊 Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"📊 Response: {json.dumps(response_data, indent=2)}")
        except:
            print(f"📊 Raw Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Specific post_id test passed")
            return True
        elif response.status_code == 404:
            print("⚠️ Post not found - This specific post_id may not exist")
            return False
        else:
            print(f"❌ FAILED: Unexpected status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 TESTING SPECIFIC POST_ID FROM FRENCH REQUEST")
    print("=" * 60)
    result = test_specific_post_id()
    print("=" * 60)
    if result:
        print("🎉 CONCLUSION: Test avec post_id spécifique RÉUSSI")
    else:
        print("🚨 CONCLUSION: Test avec post_id spécifique ÉCHOUÉ")