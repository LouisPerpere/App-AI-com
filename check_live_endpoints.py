#!/usr/bin/env python3
"""
Check which endpoints are available on LIVE environment
"""

import requests
import json

def test_live_endpoints():
    base_url = "https://claire-marcus.com/api"
    credentials = {
        "email": "lperpere@yahoo.fr",
        "password": "L@Reunion974!"
    }
    
    session = requests.Session()
    
    # Authenticate
    print("🔐 Authenticating with LIVE...")
    auth_response = session.post(
        f"{base_url}/auth/login-robust",
        json=credentials,
        headers={"Content-Type": "application/json"}
    )
    
    if auth_response.status_code == 200:
        data = auth_response.json()
        token = data.get("access_token")
        session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        })
        print("✅ Authentication successful")
    else:
        print("❌ Authentication failed")
        return
    
    # Test endpoints
    endpoints_to_test = [
        "/health",
        "/posts/generated",
        "/debug/convert-post-platform",
        "/posts/publish",
        "/debug/social-connections"
    ]
    
    print("\n🔍 Testing endpoints on LIVE:")
    for endpoint in endpoints_to_test:
        try:
            if endpoint == "/debug/convert-post-platform":
                # POST request with test data
                response = session.post(
                    f"{base_url}{endpoint}",
                    json={"post_id": "test", "platform": "facebook"},
                    timeout=10
                )
            else:
                # GET request
                response = session.get(f"{base_url}{endpoint}", timeout=10)
            
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code == 404:
                print(f"      ❌ Endpoint not found")
            elif response.status_code in [200, 400, 401]:
                print(f"      ✅ Endpoint exists")
            else:
                print(f"      ⚠️ Status: {response.status_code}")
                
        except Exception as e:
            print(f"   {endpoint}: ❌ Error - {str(e)}")

if __name__ == "__main__":
    test_live_endpoints()