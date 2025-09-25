#!/usr/bin/env python3
"""
Debug Website Analysis API Response
"""

import requests
import json

def debug_website_analysis():
    base_url = "https://post-validator.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    # Login first
    login_data = {
        "email": "lperpere@yahoo.fr",
        "password": "L@Reunion974!"
    }
    
    response = requests.post(f"{api_url}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return
    
    access_token = response.json()['access_token']
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Test website analysis
    analysis_data = {
        "website_url": "https://google.com",
        "force_reanalysis": True
    }
    
    response = requests.post(f"{api_url}/website/analyze", json=analysis_data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    try:
        response_json = response.json()
        print(f"Response JSON:")
        print(json.dumps(response_json, indent=2))
        
        # Check what fields are actually present
        print(f"\nActual fields in response: {list(response_json.keys())}")
        
    except Exception as e:
        print(f"Could not parse JSON: {e}")
        print(f"Raw response: {response.text}")

if __name__ == "__main__":
    debug_website_analysis()