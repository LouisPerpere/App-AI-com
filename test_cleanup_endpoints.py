#!/usr/bin/env python3
"""
Test the cleanup endpoints mentioned in the review request
"""

import requests
import json

def test_cleanup_endpoints():
    """Test the cleanup endpoints"""
    
    base_url = "https://claire-marcus-app-1.preview.emergentagent.com/api"
    credentials = {
        "email": "lperpere@yahoo.fr",
        "password": "L@Reunion974!"
    }
    
    # Authenticate
    session = requests.Session()
    response = session.post(
        f"{base_url}/auth/login-robust",
        json=credentials,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print(f"❌ Authentication failed: {response.text}")
        return False
    
    data = response.json()
    token = data.get("access_token")
    user_id = data.get("user_id")
    
    session.headers.update({
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })
    
    print(f"✅ Authenticated as user: {user_id}")
    
    # Test 1: Check current state
    print(f"\n🔍 Step 1: Checking current social connections state")
    response = session.get(f"{base_url}/debug/social-connections")
    if response.status_code == 200:
        data = response.json()
        connections = data.get("social_media_connections", [])
        print(f"   📊 Found {len(connections)} connections before cleanup")
        for i, conn in enumerate(connections):
            platform = conn.get("platform")
            token = conn.get("access_token", "")
            active = conn.get("active")
            print(f"     {i+1}. Platform: {platform}, Active: {active}, Token: {token[:30]}...")
    
    # Test 2: Clean invalid tokens
    print(f"\n🧹 Step 2: Testing POST /api/debug/clean-invalid-tokens")
    response = session.post(f"{base_url}/debug/clean-invalid-tokens")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Cleanup successful")
        print(f"   📊 Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    else:
        print(f"   ❌ Cleanup failed: {response.text}")
    
    # Test 3: Check state after cleanup
    print(f"\n🔍 Step 3: Checking social connections state after cleanup")
    response = session.get(f"{base_url}/debug/social-connections")
    if response.status_code == 200:
        data = response.json()
        connections = data.get("social_media_connections", [])
        print(f"   📊 Found {len(connections)} connections after cleanup")
        for i, conn in enumerate(connections):
            platform = conn.get("platform")
            token = conn.get("access_token", "")
            active = conn.get("active")
            print(f"     {i+1}. Platform: {platform}, Active: {active}, Token: {token[:30]}...")
    
    # Test 4: Clean library badges
    print(f"\n🧹 Step 4: Testing POST /api/debug/clean-library-badges")
    response = session.post(f"{base_url}/debug/clean-library-badges")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Badge cleanup successful")
        print(f"   📊 Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    else:
        print(f"   ❌ Badge cleanup failed: {response.text}")
    
    # Test 5: Final verification
    print(f"\n✅ Step 5: Final verification - checking social connections")
    response = session.get(f"{base_url}/debug/social-connections")
    if response.status_code == 200:
        data = response.json()
        connections = data.get("social_media_connections", [])
        print(f"   📊 Final state: {len(connections)} connections")
        
        if len(connections) == 0:
            print(f"   ✅ SUCCESS: All invalid tokens cleaned up")
            print(f"   ✅ User can now reconnect Facebook/Instagram with valid tokens")
        else:
            print(f"   ⚠️ Some connections remain - check if they have valid tokens")
    
    return True

if __name__ == "__main__":
    test_cleanup_endpoints()