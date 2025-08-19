#!/usr/bin/env python3
"""
Render Backend Endpoint Discovery
Check what endpoints are actually available on the Render deployment
"""

import requests
import json

# Test configuration
RENDER_BASE_URL = "https://claire-marcus-api.onrender.com"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

def discover_endpoints():
    """Discover available endpoints on Render backend"""
    print("🔍 RENDER BACKEND ENDPOINT DISCOVERY")
    print("=" * 50)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'PostCraft-Test/1.0',
        'Accept': 'application/json'
    })
    
    # First authenticate
    print("\n📋 Step 1: Authentication")
    try:
        auth_response = session.post(
            f"{RENDER_BASE_URL}/api/auth/login-robust",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        
        if auth_response.status_code == 200:
            auth_data = auth_response.json()
            token = auth_data.get('access_token')
            session.headers['Authorization'] = f'Bearer {token}'
            print(f"✅ Authentication successful")
        else:
            print(f"❌ Authentication failed")
            return
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return
    
    # Test various endpoints
    endpoints_to_test = [
        # Content endpoints
        ("GET", "/api/content/pending"),
        ("POST", "/api/content/upload"),
        ("POST", "/api/content/batch-upload"),
        ("GET", "/api/content/thumbnails/status"),
        ("GET", "/api/content/thumbnails/orphans"),
        ("POST", "/api/content/thumbnails/normalize"),
        
        # Health and diagnostic
        ("GET", "/api/health"),
        ("GET", "/api/diag"),
        
        # Website analysis
        ("GET", "/api/website/analysis"),
        ("POST", "/api/website/analyze"),
        
        # Root endpoint
        ("GET", "/"),
        
        # Check if there are any other upload endpoints
        ("POST", "/api/upload"),
        ("POST", "/api/uploads"),
        ("POST", "/api/bibliotheque"),
    ]
    
    print("\n📋 Step 2: Endpoint Discovery")
    available_endpoints = []
    unavailable_endpoints = []
    
    for method, endpoint in endpoints_to_test:
        try:
            if method == "GET":
                response = session.get(f"{RENDER_BASE_URL}{endpoint}", timeout=10)
            elif method == "POST":
                # For POST endpoints, we'll send an empty request to see if they exist
                response = session.post(f"{RENDER_BASE_URL}{endpoint}", timeout=10)
            else:
                continue
                
            status = response.status_code
            
            if status == 404:
                print(f"❌ {method} {endpoint}: 404 Not Found")
                unavailable_endpoints.append(f"{method} {endpoint}")
            elif status in [200, 400, 401, 422, 500]:  # Endpoint exists but may have validation errors
                print(f"✅ {method} {endpoint}: {status} (endpoint exists)")
                available_endpoints.append(f"{method} {endpoint} ({status})")
            else:
                print(f"⚠️  {method} {endpoint}: {status}")
                available_endpoints.append(f"{method} {endpoint} ({status})")
                
        except Exception as e:
            print(f"❌ {method} {endpoint}: Error - {e}")
            unavailable_endpoints.append(f"{method} {endpoint} (Error)")
    
    print("\n" + "=" * 50)
    print("📊 ENDPOINT DISCOVERY SUMMARY")
    print("=" * 50)
    
    print(f"\n✅ Available Endpoints ({len(available_endpoints)}):")
    for endpoint in available_endpoints:
        print(f"   {endpoint}")
    
    print(f"\n❌ Unavailable Endpoints ({len(unavailable_endpoints)}):")
    for endpoint in unavailable_endpoints:
        print(f"   {endpoint}")
    
    # Check the root endpoint for more info
    print("\n📋 Step 3: Root Endpoint Analysis")
    try:
        root_response = session.get(f"{RENDER_BASE_URL}/", timeout=10)
        if root_response.status_code == 200:
            root_data = root_response.json()
            print("✅ Root endpoint response:")
            print(json.dumps(root_data, indent=2))
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Check OpenAPI docs if available
    print("\n📋 Step 4: OpenAPI Documentation Check")
    try:
        docs_response = session.get(f"{RENDER_BASE_URL}/docs", timeout=10)
        print(f"   /docs: {docs_response.status_code}")
        
        openapi_response = session.get(f"{RENDER_BASE_URL}/openapi.json", timeout=10)
        print(f"   /openapi.json: {openapi_response.status_code}")
        
        if openapi_response.status_code == 200:
            openapi_data = openapi_response.json()
            paths = openapi_data.get('paths', {})
            print(f"   Available paths in OpenAPI: {len(paths)}")
            for path in sorted(paths.keys()):
                methods = list(paths[path].keys())
                print(f"     {path}: {methods}")
                
    except Exception as e:
        print(f"❌ OpenAPI check error: {e}")

if __name__ == "__main__":
    discover_endpoints()