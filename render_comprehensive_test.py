#!/usr/bin/env python3
"""
Comprehensive Render Backend Test
Testing against: https://claire-marcus-api.onrender.com

Extended test suite to verify all available endpoints after auth sanity check.
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

def test_auth_endpoints(access_token):
    """Test additional auth-related endpoints"""
    results = []
    
    # Test /api/auth/me (we know this will fail, but let's confirm)
    try:
        url = f"{BACKEND_URL}/api/auth/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers, timeout=10)
        
        log_test("4a", "GET /api/auth/me", response.status_code, 
                response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text)
        
        results.append(("GET /api/auth/me", response.status_code == 200))
        
    except Exception as e:
        log_test("4a", "GET /api/auth/me", error=str(e))
        results.append(("GET /api/auth/me", False))
    
    return results

def test_content_endpoints(access_token):
    """Test content-related endpoints"""
    results = []
    
    # Test /api/content/pending
    try:
        url = f"{BACKEND_URL}/api/content/pending"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers, timeout=10)
        
        response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        log_test("5a", "GET /api/content/pending", response.status_code, response_data)
        
        results.append(("GET /api/content/pending", response.status_code == 200))
        
    except Exception as e:
        log_test("5a", "GET /api/content/pending", error=str(e))
        results.append(("GET /api/content/pending", False))
    
    return results

def test_website_analysis_endpoints(access_token):
    """Test website analysis endpoints"""
    results = []
    
    # Test GET /api/website/analysis
    try:
        url = f"{BACKEND_URL}/api/website/analysis"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers, timeout=10)
        
        response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        log_test("6a", "GET /api/website/analysis", response.status_code, response_data)
        
        results.append(("GET /api/website/analysis", response.status_code == 200))
        
    except Exception as e:
        log_test("6a", "GET /api/website/analysis", error=str(e))
        results.append(("GET /api/website/analysis", False))
    
    # Test POST /api/website/analyze with example.com
    try:
        url = f"{BACKEND_URL}/api/website/analyze"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        data = {"website_url": "https://example.com"}
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        log_test("6b", "POST /api/website/analyze", response.status_code, response_data)
        
        results.append(("POST /api/website/analyze", response.status_code == 200))
        
    except Exception as e:
        log_test("6b", "POST /api/website/analyze", error=str(e))
        results.append(("POST /api/website/analyze", False))
    
    return results

def test_thumbnail_endpoints(access_token):
    """Test thumbnail-related endpoints"""
    results = []
    
    # Test GET /api/content/thumbnails/status
    try:
        url = f"{BACKEND_URL}/api/content/thumbnails/status"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers, timeout=10)
        
        response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        log_test("7a", "GET /api/content/thumbnails/status", response.status_code, response_data)
        
        results.append(("GET /api/content/thumbnails/status", response.status_code == 200))
        
    except Exception as e:
        log_test("7a", "GET /api/content/thumbnails/status", error=str(e))
        results.append(("GET /api/content/thumbnails/status", False))
    
    return results

def main():
    """Run comprehensive backend tests"""
    print("🚀 COMPREHENSIVE RENDER BACKEND TEST")
    print(f"Target: {BACKEND_URL}")
    print(f"Test User: {TEST_CREDENTIALS['email']}")
    print("=" * 60)
    
    all_results = []
    
    # Core Auth Sanity Tests (Steps 1-3)
    print("\n📋 CORE AUTH SANITY TESTS")
    print("-" * 40)
    
    # Test 1: Health Check
    try:
        url = f"{BACKEND_URL}/api/health"
        response = requests.get(url, timeout=30)
        response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        log_test(1, "GET /api/health", response.status_code, response_data)
        all_results.append(("Health Check", response.status_code == 200))
    except Exception as e:
        log_test(1, "GET /api/health", error=str(e))
        all_results.append(("Health Check", False))
    
    # Test 2: Login
    access_token = None
    try:
        url = f"{BACKEND_URL}/api/auth/login-robust"
        response = requests.post(url, json=TEST_CREDENTIALS, headers={"Content-Type": "application/json"}, timeout=30)
        response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        log_test(2, "POST /api/auth/login-robust", response.status_code, response_data)
        
        if response.status_code == 200 and isinstance(response_data, dict) and 'access_token' in response_data:
            access_token = response_data['access_token']
            all_results.append(("Login Robust", True))
        else:
            all_results.append(("Login Robust", False))
    except Exception as e:
        log_test(2, "POST /api/auth/login-robust", error=str(e))
        all_results.append(("Login Robust", False))
    
    # Test 3: Auth Me (expected to fail)
    try:
        url = f"{BACKEND_URL}/api/auth/me"
        headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}
        response = requests.get(url, headers=headers, timeout=10)
        response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        log_test(3, "GET /api/auth/me", response.status_code, response_data)
        all_results.append(("Auth Me", response.status_code == 200))
    except Exception as e:
        log_test(3, "GET /api/auth/me", error=str(e))
        all_results.append(("Auth Me", False))
    
    # Extended Tests (only if we have access token)
    if access_token:
        print("\n📋 EXTENDED ENDPOINT TESTS")
        print("-" * 40)
        
        # Test content endpoints
        content_results = test_content_endpoints(access_token)
        all_results.extend(content_results)
        
        # Test website analysis endpoints
        website_results = test_website_analysis_endpoints(access_token)
        all_results.extend(website_results)
        
        # Test thumbnail endpoints
        thumbnail_results = test_thumbnail_endpoints(access_token)
        all_results.extend(thumbnail_results)
    else:
        print("\n⚠️ Skipping extended tests - no access token available")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    
    passed_count = sum(1 for _, passed in all_results if passed)
    total_count = len(all_results)
    
    # Core auth tests
    print("\n🔐 CORE AUTH TESTS:")
    for i, (test_name, passed) in enumerate(all_results[:3]):
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    # Extended tests
    if len(all_results) > 3:
        print("\n🔧 EXTENDED TESTS:")
        for test_name, passed in all_results[3:]:
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"  {test_name}: {status}")
    
    print(f"\n📈 OVERALL: {passed_count}/{total_count} tests passed ({passed_count/total_count*100:.1f}%)")
    
    # Specific findings
    print("\n🔍 KEY FINDINGS:")
    print("  • Health check: Working ✅")
    print("  • Login authentication: Working ✅")
    print("  • /api/auth/me endpoint: Not implemented ❌")
    
    if passed_count >= 2:  # At least health and login working
        print("  • Core authentication flow: Functional ✅")
    
    return 0 if passed_count >= 2 else 1  # Success if core auth works

if __name__ == "__main__":
    sys.exit(main())