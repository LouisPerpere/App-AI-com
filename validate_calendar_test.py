#!/usr/bin/env python3
"""
Test spécifique pour l'endpoint POST /posts/validate-to-calendar
Demande de révision française - Test de l'endpoint de validation au calendrier
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://social-pub-hub.preview.emergentagent.com"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

def authenticate():
    """Authentification pour obtenir un token JWT valide"""
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
            print(f"Response: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None, None

def get_existing_posts(token):
    """Récupérer les posts existants pour obtenir un post_id valide"""
    try:
        print("📋 Step 2: Getting existing posts...")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(
            f"{BACKEND_URL}/api/posts/generated",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            posts = data.get("posts", [])
            print(f"✅ Found {len(posts)} existing posts")
            
            if posts:
                # Retourner le premier post trouvé
                first_post = posts[0]
                post_id = first_post.get("id")
                print(f"✅ Using post ID: {post_id}")
                return post_id
            else:
                print("⚠️ No existing posts found")
                return None
        else:
            print(f"❌ Failed to get posts - Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting posts: {e}")
        return None

def test_validate_to_calendar_endpoint(token, post_id=None):
    """Test principal de l'endpoint POST /posts/validate-to-calendar"""
    try:
        print("📅 Step 3: Testing POST /posts/validate-to-calendar endpoint...")
        
        # Utiliser le post_id fourni dans la demande ou un post existant
        test_post_id = post_id or "post_6a670c66-c06c-4d75-9dd5-c747e8a0281a_1758187803_0"
        
        # Paramètres de test selon la demande française
        test_data = {
            "post_id": test_post_id,
            "platforms": ["instagram"],
            "scheduled_date": "2025-09-26T11:00:00"
        }
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print(f"📤 Testing with data: {json.dumps(test_data, indent=2)}")
        
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
        
        # Analyse des résultats
        if response.status_code == 200:
            print("✅ Endpoint responds successfully (200 OK)")
            return True
        elif response.status_code == 404:
            print("❌ Post not found (404) - Expected if using test post_id")
            return False
        elif response.status_code == 400:
            print("❌ Bad request (400) - Check request format")
            return False
        elif response.status_code == 401:
            print("❌ Unauthorized (401) - Token issue")
            return False
        else:
            print(f"⚠️ Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        return False

def test_endpoint_existence():
    """Test si l'endpoint existe (sans authentification)"""
    try:
        print("🔍 Step 4: Testing endpoint existence...")
        
        # Test sans token pour voir si l'endpoint existe
        response = requests.post(
            f"{BACKEND_URL}/api/posts/validate-to-calendar",
            json={"test": "data"}
        )
        
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

def main():
    """Fonction principale de test"""
    print("🎯 TESTING POST /posts/validate-to-calendar ENDPOINT")
    print("=" * 60)
    
    results = {
        "authentication": False,
        "endpoint_exists": False,
        "endpoint_responds": False,
        "posts_available": False
    }
    
    # Test 1: Authentification
    token, user_id = authenticate()
    if token:
        results["authentication"] = True
    else:
        print("❌ Cannot proceed without authentication")
        return results
    
    # Test 2: Vérifier l'existence de l'endpoint
    results["endpoint_exists"] = test_endpoint_existence()
    
    # Test 3: Récupérer les posts existants
    existing_post_id = get_existing_posts(token)
    if existing_post_id:
        results["posts_available"] = True
    
    # Test 4: Test principal avec post existant ou post_id de test
    results["endpoint_responds"] = test_validate_to_calendar_endpoint(token, existing_post_id)
    
    # Résumé des résultats
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY:")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    success_rate = sum(results.values()) / len(results) * 100
    print(f"\nOverall Success Rate: {success_rate:.1f}%")
    
    if results["endpoint_exists"] and results["endpoint_responds"]:
        print("\n🎉 CONCLUSION: L'endpoint POST /posts/validate-to-calendar est FONCTIONNEL")
    else:
        print("\n🚨 CONCLUSION: L'endpoint présente des problèmes")
    
    return results

if __name__ == "__main__":
    main()