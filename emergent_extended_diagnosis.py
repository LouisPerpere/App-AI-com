#!/usr/bin/env python3
"""
Extended Emergent Backend Diagnosis
Testing alternative paths and root domain to understand the deployment
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://social-pub-hub.preview.emergentagent.com"

def test_endpoint(path, method="GET", data=None):
    """Test a specific endpoint and return detailed info"""
    try:
        url = f"{BASE_URL}{path}"
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "OPTIONS":
            response = requests.options(url, timeout=10)
        
        print(f"\n{method} {url}")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"JSON Response: {json.dumps(response_json, indent=2)}")
        except:
            print(f"Raw Response: {response.text[:500]}...")
            
        return response.status_code, response.text
        
    except Exception as e:
        print(f"\n{method} {BASE_URL}{path}")
        print(f"ERROR: {e}")
        return None, str(e)

def main():
    print(f"🔍 EXTENDED EMERGENT BACKEND DIAGNOSIS")
    print(f"Target: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Test various paths to understand the deployment
    test_paths = [
        "/",                    # Root
        "/health",              # Health without /api
        "/api",                 # API root
        "/api/",                # API root with slash
        "/docs",                # FastAPI docs
        "/openapi.json",        # OpenAPI spec
        "/api/docs",            # API docs
        "/api/openapi.json",    # API OpenAPI spec
        "/status",              # Alternative status
        "/ping",                # Alternative ping
        "/api/status",          # API status
        "/api/ping",            # API ping
        "/v1/health",           # Versioned health
        "/api/v1/health",       # Versioned API health
    ]
    
    print(f"\n{'='*60}")
    print(f"TESTING COMMON PATHS")
    print(f"{'='*60}")
    
    working_endpoints = []
    
    for path in test_paths:
        status, response = test_endpoint(path)
        if status and status != 404:
            working_endpoints.append((path, status, response[:100]))
    
    print(f"\n{'='*60}")
    print(f"WORKING ENDPOINTS SUMMARY")
    print(f"{'='*60}")
    
    if working_endpoints:
        for path, status, response in working_endpoints:
            print(f"✅ {path} -> {status}")
            print(f"   Response: {response}...")
    else:
        print(f"❌ NO WORKING ENDPOINTS FOUND")
        print(f"   All tested paths returned 404 or failed")
    
    # Test if it's a static site or different service
    print(f"\n{'='*60}")
    print(f"SERVICE TYPE ANALYSIS")
    print(f"{'='*60}")
    
    root_status, root_response = test_endpoint("/")
    
    if root_status == 200:
        if "<!DOCTYPE html>" in root_response or "<html" in root_response:
            print(f"🌐 DETECTED: Static HTML site or frontend application")
            print(f"   This appears to be a frontend deployment, not a backend API")
        elif "FastAPI" in root_response or "swagger" in root_response.lower():
            print(f"🚀 DETECTED: FastAPI backend with different routing")
        elif "express" in root_response.lower() or "node" in root_response.lower():
            print(f"🟢 DETECTED: Node.js/Express backend")
        else:
            print(f"❓ UNKNOWN: Service type unclear from root response")
    else:
        print(f"❌ ROOT ENDPOINT: Status {root_status} - service may be down")
    
    # Final diagnosis
    print(f"\n{'='*60}")
    print(f"FINAL DIAGNOSIS")
    print(f"{'='*60}")
    
    if not working_endpoints:
        print(f"🚨 CRITICAL ISSUE: No API endpoints responding")
        print(f"   Possible causes:")
        print(f"   1. Backend service is not deployed")
        print(f"   2. Domain is pointing to wrong service")
        print(f"   3. API routes are configured differently")
        print(f"   4. Service is down or crashed")
        print(f"   5. Firewall/proxy blocking API requests")
    else:
        print(f"✅ SERVICE PARTIALLY WORKING: {len(working_endpoints)} endpoints found")
        print(f"   The service exists but API structure differs from expected")
    
    return working_endpoints

if __name__ == "__main__":
    main()