#!/usr/bin/env python3
"""
Detailed Social Connections Analysis
Analyser en détail les endpoints de connexions sociales pour identifier l'inconsistance
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://claire-marcus-app-1.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def authenticate():
    """Authenticate and get token"""
    session = requests.Session()
    session.headers.update({'Content-Type': 'application/json'})
    
    response = session.post(f"{BACKEND_URL}/auth/login-robust", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    
    if response.status_code == 200:
        data = response.json()
        auth_token = data.get('access_token')
        user_id = data.get('user_id')
        
        session.headers.update({'Authorization': f'Bearer {auth_token}'})
        log(f"✅ Authentication successful - User ID: {user_id}")
        return session, user_id
    else:
        log(f"❌ Authentication failed: {response.status_code}", "ERROR")
        return None, None

def main():
    log("🔍 DETAILED SOCIAL CONNECTIONS ANALYSIS")
    log("=" * 60)
    
    session, user_id = authenticate()
    if not session:
        return
    
    # Test all social connection endpoints
    endpoints = [
        "/social/connections",
        "/social/connections/debug", 
        "/social/connections/status",
        "/debug/social-connections",
        "/social/debug-connections"
    ]
    
    for endpoint in endpoints:
        log(f"\n🔍 Testing endpoint: {endpoint}")
        try:
            response = session.get(f"{BACKEND_URL}{endpoint}")
            log(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                log(f"   Response type: {type(data)}")
                
                if isinstance(data, dict):
                    log(f"   Keys: {list(data.keys())}")
                    
                    # Look for Instagram-related data
                    instagram_found = False
                    for key, value in data.items():
                        if 'instagram' in str(key).lower() or 'instagram' in str(value).lower():
                            log(f"   Instagram data found in '{key}': {value}")
                            instagram_found = True
                    
                    if not instagram_found:
                        log("   No Instagram data found")
                        
                elif isinstance(data, list):
                    log(f"   List length: {len(data)}")
                    for i, item in enumerate(data):
                        if 'instagram' in str(item).lower():
                            log(f"   Instagram item {i}: {item}")
                
                # Pretty print the full response for analysis
                log(f"   Full response:")
                print(json.dumps(data, indent=2, default=str))
                
            elif response.status_code == 404:
                log("   Endpoint not found")
            else:
                log(f"   Error: {response.text}")
                
        except Exception as e:
            log(f"   Exception: {str(e)}", "ERROR")
    
    log("\n" + "=" * 60)
    log("🎯 ANALYSIS COMPLETE")

if __name__ == "__main__":
    main()