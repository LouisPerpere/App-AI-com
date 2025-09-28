#!/usr/bin/env python3
"""
Emergent Backend Diagnosis Script
Deep diagnostics against https://social-publisher-10.preview.emergentagent.com

Steps:
1) GET /api/health
2) Attempt login via POST /api/auth/login-robust with known creds
3) If 401, try POST /api/auth/login (legacy) with same creds  
4) If both fail, GET /api/auth/me with any existing token (if available)
5) Check CORS/headers behavior
6) Record exact URLs, status codes, response bodies and headers
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://social-publisher-10.preview.emergentagent.com"
CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

def log_response(step, method, url, response, request_data=None):
    """Log detailed response information"""
    print(f"\n{'='*60}")
    print(f"STEP {step}: {method} {url}")
    print(f"{'='*60}")
    
    if request_data:
        print(f"REQUEST DATA: {json.dumps(request_data, indent=2)}")
    
    print(f"STATUS CODE: {response.status_code}")
    print(f"HEADERS: {dict(response.headers)}")
    
    try:
        response_json = response.json()
        print(f"RESPONSE BODY: {json.dumps(response_json, indent=2)}")
    except:
        print(f"RESPONSE BODY (raw): {response.text}")
    
    print(f"URL ACCESSED: {response.url}")
    print(f"ELAPSED TIME: {response.elapsed.total_seconds():.3f}s")

def test_health_endpoint():
    """Step 1: Test health endpoint"""
    try:
        url = f"{BASE_URL}/api/health"
        response = requests.get(url, timeout=10)
        log_response("1", "GET", url, response)
        return response.status_code == 200
    except Exception as e:
        print(f"\n❌ STEP 1 FAILED: Health check error: {e}")
        return False

def test_login_robust():
    """Step 2: Test login-robust endpoint"""
    try:
        url = f"{BASE_URL}/api/auth/login-robust"
        response = requests.post(url, json=CREDENTIALS, timeout=10)
        log_response("2", "POST", url, response, CREDENTIALS)
        
        if response.status_code == 200:
            try:
                data = response.json()
                token = data.get('access_token')
                if token:
                    print(f"✅ LOGIN SUCCESS: Token obtained: {token[:20]}...")
                    return True, token
                else:
                    print(f"⚠️ LOGIN PARTIAL: 200 status but no access_token in response")
                    return False, None
            except:
                print(f"⚠️ LOGIN PARTIAL: 200 status but invalid JSON response")
                return False, None
        else:
            print(f"❌ LOGIN FAILED: Status {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"\n❌ STEP 2 FAILED: Login-robust error: {e}")
        return False, None

def test_login_legacy():
    """Step 3: Test legacy login endpoint"""
    try:
        url = f"{BASE_URL}/api/auth/login"
        response = requests.post(url, json=CREDENTIALS, timeout=10)
        log_response("3", "POST", url, response, CREDENTIALS)
        
        if response.status_code == 200:
            try:
                data = response.json()
                token = data.get('access_token')
                if token:
                    print(f"✅ LEGACY LOGIN SUCCESS: Token obtained: {token[:20]}...")
                    return True, token
                else:
                    print(f"⚠️ LEGACY LOGIN PARTIAL: 200 status but no access_token in response")
                    return False, None
            except:
                print(f"⚠️ LEGACY LOGIN PARTIAL: 200 status but invalid JSON response")
                return False, None
        else:
            print(f"❌ LEGACY LOGIN FAILED: Status {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"\n❌ STEP 3 FAILED: Legacy login error: {e}")
        return False, None

def test_auth_me(token=None):
    """Step 4: Test /api/auth/me endpoint"""
    try:
        url = f"{BASE_URL}/api/auth/me"
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'
            print(f"Using token: {token[:20]}...")
        else:
            print("No token available - testing without authorization")
            
        response = requests.get(url, headers=headers, timeout=10)
        log_response("4", "GET", url, response)
        
        if response.status_code == 200:
            print(f"✅ AUTH ME SUCCESS: User data retrieved")
            return True
        else:
            print(f"❌ AUTH ME FAILED: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ STEP 4 FAILED: Auth me error: {e}")
        return False

def test_cors_behavior():
    """Step 5: Test CORS and headers behavior"""
    try:
        print(f"\n{'='*60}")
        print(f"STEP 5: CORS AND HEADERS ANALYSIS")
        print(f"{'='*60}")
        
        # Test preflight request
        url = f"{BASE_URL}/api/auth/login-robust"
        headers = {
            'Origin': 'https://social-publisher-10.preview.emergentagent.com',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type,Authorization'
        }
        
        response = requests.options(url, headers=headers, timeout=10)
        print(f"PREFLIGHT OPTIONS REQUEST:")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        # Check specific CORS headers
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
        }
        
        print(f"CORS HEADERS: {json.dumps(cors_headers, indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ STEP 5 FAILED: CORS test error: {e}")
        return False

def main():
    """Run complete Emergent backend diagnosis"""
    print(f"🔍 EMERGENT BACKEND DIAGNOSIS")
    print(f"Target: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Credentials: {CREDENTIALS['email']} / {'*' * len(CREDENTIALS['password'])}")
    
    results = {
        'health_check': False,
        'login_robust': False,
        'login_legacy': False,
        'auth_me': False,
        'cors_check': False,
        'token_obtained': None
    }
    
    # Step 1: Health check
    results['health_check'] = test_health_endpoint()
    
    # Step 2: Login robust
    login_success, token = test_login_robust()
    results['login_robust'] = login_success
    results['token_obtained'] = token
    
    # Step 3: Legacy login (only if robust failed)
    if not login_success:
        legacy_success, legacy_token = test_login_legacy()
        results['login_legacy'] = legacy_success
        if legacy_token:
            results['token_obtained'] = legacy_token
    
    # Step 4: Auth me (with token if available)
    results['auth_me'] = test_auth_me(results['token_obtained'])
    
    # Step 5: CORS behavior
    results['cors_check'] = test_cors_behavior()
    
    # Summary
    print(f"\n{'='*60}")
    print(f"DIAGNOSIS SUMMARY")
    print(f"{'='*60}")
    
    for key, value in results.items():
        if key == 'token_obtained':
            if value:
                print(f"✅ {key}: {value[:20]}...")
            else:
                print(f"❌ {key}: None")
        else:
            status = "✅" if value else "❌"
            print(f"{status} {key}: {value}")
    
    # Determine root cause
    print(f"\n🔍 ROOT CAUSE ANALYSIS:")
    
    if not results['health_check']:
        print(f"❌ CRITICAL: Health endpoint not responding - backend may be down")
    elif not results['login_robust'] and not results['login_legacy']:
        print(f"❌ CRITICAL: Both login endpoints failing - authentication system broken")
    elif results['login_robust'] or results['login_legacy']:
        print(f"✅ SUCCESS: Authentication working - login issue may be frontend-related")
    else:
        print(f"⚠️ UNCLEAR: Mixed results - requires further investigation")
    
    # Success rate
    success_count = sum(1 for k, v in results.items() if k != 'token_obtained' and v)
    total_tests = len([k for k in results.keys() if k != 'token_obtained'])
    success_rate = (success_count / total_tests) * 100
    
    print(f"\n📊 SUCCESS RATE: {success_count}/{total_tests} tests passed ({success_rate:.1f}%)")
    
    return results

if __name__ == "__main__":
    main()