#!/usr/bin/env python3
"""
Debug script to examine products_services_details field in detail
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "https://social-ai-planner-2.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}
TEST_WEBSITE = "https://myownwatch.fr"

def debug_products_services():
    session = requests.Session()
    session.headers.update({'Content-Type': 'application/json'})
    
    # Authenticate
    auth_response = session.post(f"{BACKEND_URL}/auth/login-robust", json=TEST_CREDENTIALS)
    if auth_response.status_code != 200:
        print("❌ Authentication failed")
        return
    
    token = auth_response.json().get("access_token")
    session.headers.update({"Authorization": f"Bearer {token}"})
    
    # Analyze website
    print("🔍 Analyzing website for products_services_details...")
    analysis_response = session.post(
        f"{BACKEND_URL}/website/analyze",
        json={"website_url": TEST_WEBSITE},
        timeout=120
    )
    
    if analysis_response.status_code != 200:
        print(f"❌ Analysis failed: {analysis_response.status_code}")
        return
    
    data = analysis_response.json()
    
    # Debug products_services_details specifically
    products_services = data.get("products_services_details")
    
    print(f"\n📊 products_services_details DEBUG:")
    print(f"   Type: {type(products_services)}")
    print(f"   Value: {products_services}")
    
    if isinstance(products_services, list):
        print(f"   Length: {len(products_services)}")
        if len(products_services) > 0:
            print(f"   First item: {products_services[0]}")
    elif isinstance(products_services, str):
        print(f"   Length: {len(products_services)} chars")
        print(f"   Content: {products_services}")
    
    # Check all fields for context
    print(f"\n📋 All response fields:")
    for key, value in data.items():
        if isinstance(value, str):
            print(f"   {key}: {len(value)} chars")
        elif isinstance(value, list):
            print(f"   {key}: {len(value)} items")
        else:
            print(f"   {key}: {type(value)} - {value}")

if __name__ == "__main__":
    debug_products_services()