#!/usr/bin/env python3
"""
Test rapide de validation des paramètres
"""

import requests
import json

# Configuration
BACKEND_URL = "https://social-ai-planner-2.preview.emergentagent.com"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

def test_validation():
    # Authentification
    auth_response = requests.post(f"{BACKEND_URL}/api/auth/login-robust", json=TEST_CREDENTIALS)
    token = auth_response.json().get("access_token")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test missing post_id
    print("Testing missing post_id...")
    response = requests.post(
        f"{BACKEND_URL}/api/posts/validate-to-calendar",
        json={"platforms": ["instagram"], "scheduled_date": "2025-09-26T11:00:00"},
        headers=headers
    )
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {response.json()}")
    except:
        print(f"Raw response: {response.text}")
    
    # Test missing platforms
    print("\nTesting missing platforms...")
    response = requests.post(
        f"{BACKEND_URL}/api/posts/validate-to-calendar",
        json={"post_id": "test_id", "scheduled_date": "2025-09-26T11:00:00"},
        headers=headers
    )
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {response.json()}")
    except:
        print(f"Raw response: {response.text}")

if __name__ == "__main__":
    test_validation()