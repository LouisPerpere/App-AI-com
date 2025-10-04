#!/usr/bin/env python3
"""
Debug Instagram Callback Routing Issue
=====================================

This script will help identify why Instagram callback is redirecting to Facebook callback.
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://claire-marcus.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def authenticate():
    """Get auth token"""
    response = requests.post(f"{BASE_URL}/auth/login-robust", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token"), data.get("user_id")
    return None, None

def test_route_resolution():
    """Test which route is actually being called"""
    log("🔍 Testing Instagram callback route resolution...")
    
    token, user_id = authenticate()
    if not token:
        log("❌ Authentication failed")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test different Instagram callback URLs
    test_urls = [
        f"{BASE_URL}/social/instagram/callback",
        f"{BASE_URL}/auth/instagram/callback",
        f"{BASE_URL}/social/instagram/callback?code=test&state=test|{user_id}",
        f"{BASE_URL}/auth/instagram/callback?code=test&state=test|{user_id}"
    ]
    
    for url in test_urls:
        log(f"Testing URL: {url}")
        
        try:
            response = requests.get(url, headers=headers, allow_redirects=False)
            log(f"  Status: {response.status_code}")
            
            if response.status_code in [301, 302, 307, 308]:
                location = response.headers.get("Location", "")
                log(f"  Redirect to: {location}")
                
                if "/facebook/callback" in location:
                    log(f"  ❌ REDIRECTS TO FACEBOOK!")
                else:
                    log(f"  ✅ Redirects elsewhere")
            else:
                log(f"  ✅ Direct response (no redirect)")
                
                # Try to get response content
                try:
                    content = response.text[:200]
                    log(f"  Content preview: {content}...")
                except:
                    pass
                    
        except Exception as e:
            log(f"  ❌ Error: {str(e)}")
        
        log("")

def test_route_order():
    """Test if route order is causing conflicts"""
    log("🔍 Testing route registration order...")
    
    # Test health endpoint to make sure API is working
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        log("✅ API is healthy")
    else:
        log("❌ API health check failed")
        return
    
    # Test if social router is loaded
    token, user_id = authenticate()
    if not token:
        log("❌ Authentication failed")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test social connections endpoint (should exist if social router is loaded)
    response = requests.get(f"{BASE_URL}/social/connections", headers=headers)
    log(f"Social connections endpoint: {response.status_code}")
    
    # Test Facebook auth URL (should exist if social router is loaded)
    response = requests.get(f"{BASE_URL}/social/facebook/auth-url", headers=headers)
    log(f"Facebook auth URL endpoint: {response.status_code}")
    
    # Test Instagram auth URL (should exist in main server.py)
    response = requests.get(f"{BASE_URL}/social/instagram/auth-url", headers=headers)
    log(f"Instagram auth URL endpoint: {response.status_code}")

def main():
    log("🎯 DEBUGGING INSTAGRAM CALLBACK ROUTING ISSUE")
    log("=" * 60)
    
    test_route_resolution()
    test_route_order()
    
    log("=" * 60)
    log("🎯 DEBUG COMPLETE")

if __name__ == "__main__":
    main()