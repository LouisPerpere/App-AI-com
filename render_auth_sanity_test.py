#!/usr/bin/env python3
"""
Render Backend Auth Sanity Test
Testing against: https://claire-marcus-api.onrender.com

Test Flow:
1) GET /api/health -> expect 200 JSON
2) POST /api/auth/login-robust with {"email":"lperpere@yahoo.fr","password":"L@Reunion974!"} -> expect 200, access_token
3) GET /api/auth/me with Authorization: Bearer <token> -> expect 200 user payload
4) Report status codes and response bodies
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://claire-marcus-api.onrender.com"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

def log_test(step, description, status_code=None, response_data=None, error=None):
    """Log test results with consistent formatting"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] Step {step}: {description}")
    if status_code:
        print(f"Status Code: {status_code}")
    if response_data:
        if isinstance(response_data, dict):
            print(f"Response: {json.dumps(response_data, indent=2)}")
        else:
            print(f"Response: {response_data}")
    if error:
        print(f"❌ Error: {error}")

def test_health_check():
    """Test 1: GET /api/health -> expect 200 JSON"""
    try:
        url = f"{BACKEND_URL}/api/health"
        print(f"\n🔍 Testing: GET {url}")
        
        response = requests.get(url, timeout=30)
        
        log_test(1, "Health Check", response.status_code, response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text)
        
        if response.status_code == 200:
            print("✅ Step 1 PASSED: Health check successful")
            return True
        else:
            print(f"❌ Step 1 FAILED: Expected 200, got {response.status_code}")
            return False
            
    except Exception as e:
        log_test(1, "Health Check", error=str(e))
        print("❌ Step 1 FAILED: Exception occurred")
        return False

def test_login_robust():
    """Test 2: POST /api/auth/login-robust -> expect 200, access_token"""
    try:
        url = f"{BACKEND_URL}/api/auth/login-robust"
        print(f"\n🔍 Testing: POST {url}")
        print(f"Credentials: {TEST_CREDENTIALS}")
        
        response = requests.post(
            url,
            json=TEST_CREDENTIALS,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        log_test(2, "Login Robust", response.status_code, response_data)
        
        if response.status_code == 200 and isinstance(response_data, dict) and 'access_token' in response_data:
            print("✅ Step 2 PASSED: Login successful, access_token obtained")
            return response_data['access_token']
        else:
            print(f"❌ Step 2 FAILED: Expected 200 with access_token, got {response.status_code}")
            return None
            
    except Exception as e:
        log_test(2, "Login Robust", error=str(e))
        print("❌ Step 2 FAILED: Exception occurred")
        return None

def test_auth_me(access_token):
    """Test 3: GET /api/auth/me with Bearer token -> expect 200 user payload"""
    try:
        url = f"{BACKEND_URL}/api/auth/me"
        print(f"\n🔍 Testing: GET {url}")
        print(f"Using Bearer token: {access_token[:20]}..." if len(access_token) > 20 else f"Using Bearer token: {access_token}")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        log_test(3, "Auth Me", response.status_code, response_data)
        
        if response.status_code == 200:
            print("✅ Step 3 PASSED: Auth me successful, user payload retrieved")
            return True
        else:
            print(f"❌ Step 3 FAILED: Expected 200, got {response.status_code}")
            return False
            
    except Exception as e:
        log_test(3, "Auth Me", error=str(e))
        print("❌ Step 3 FAILED: Exception occurred")
        return False

def main():
    """Run all auth sanity tests"""
    print("🚀 RENDER BACKEND AUTH SANITY TEST")
    print(f"Target: {BACKEND_URL}")
    print(f"Test User: {TEST_CREDENTIALS['email']}")
    print("=" * 60)
    
    results = []
    
    # Test 1: Health Check
    health_passed = test_health_check()
    results.append(("Health Check", health_passed))
    
    # Test 2: Login
    access_token = test_login_robust()
    login_passed = access_token is not None
    results.append(("Login Robust", login_passed))
    
    # Test 3: Auth Me (only if login succeeded)
    if access_token:
        auth_me_passed = test_auth_me(access_token)
        results.append(("Auth Me", auth_me_passed))
    else:
        print("\n⚠️ Skipping Step 3 (Auth Me) - no access token available")
        results.append(("Auth Me", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed_count}/{total_count} tests passed ({passed_count/total_count*100:.1f}%)")
    
    if passed_count == total_count:
        print("🎉 ALL TESTS PASSED - Render backend auth is fully functional!")
        return 0
    else:
        print("⚠️ SOME TESTS FAILED - Check the details above")
        return 1

if __name__ == "__main__":
    sys.exit(main())