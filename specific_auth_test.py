#!/usr/bin/env python3
"""
Specific Test for Review Request Issue
Testing the exact scenario: login -> get token -> use token for business-profile
"""

import requests
import json
from datetime import datetime

def test_specific_scenario():
    """Test the exact scenario from the review request"""
    base_url = "https://post-validator.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("🔍 TESTING SPECIFIC SCENARIO FROM REVIEW REQUEST")
    print("=" * 80)
    
    # Step 1: Login with specified credentials
    print("STEP 1: POST /api/auth/login with lperpere@yahoo.fr / L@Reunion974!")
    login_response = requests.post(
        f"{api_url}/auth/login",
        json={
            "email": "lperpere@yahoo.fr",
            "password": "L@Reunion974!"
        },
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Login Status: {login_response.status_code}")
    try:
        login_data = login_response.json()
        print(f"Login Response: {json.dumps(login_data, indent=2)}")
    except:
        print(f"Login Response Text: {login_response.text}")
        login_data = {}
    
    if login_response.status_code != 200 or 'access_token' not in login_data:
        print("❌ LOGIN FAILED")
        return False
    
    # Step 2: Extract access token
    access_token = login_data['access_token']
    print(f"\nSTEP 2: Access token extracted: {access_token[:50]}...")
    
    # Step 3: Test GET /api/business-profile with Authorization header
    print(f"\nSTEP 3: GET /api/business-profile with Authorization: Bearer {access_token[:20]}...")
    
    profile_response = requests.get(
        f"{api_url}/business-profile",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    
    print(f"Business Profile Status: {profile_response.status_code}")
    try:
        profile_data = profile_response.json()
        print(f"Business Profile Response: {json.dumps(profile_data, indent=2)}")
    except:
        print(f"Business Profile Response Text: {profile_response.text}")
        profile_data = {}
    
    # Step 4: Analyze the response
    print(f"\nSTEP 4: ANALYSIS")
    business_name = profile_data.get('business_name', '')
    email = profile_data.get('email', '')
    
    print(f"Business Name: {business_name}")
    print(f"Email: {email}")
    
    if business_name == "Demo Business" and email == "demo@claire-marcus.com":
        print("❌ ISSUE CONFIRMED: System is returning demo data despite valid authentication!")
        print("   This indicates the token validation is failing and falling back to demo mode")
        return False
    else:
        print("✅ SUCCESS: System is returning real user data")
        print("   Token validation is working correctly")
        return True

if __name__ == "__main__":
    success = test_specific_scenario()
    if success:
        print("\n🎉 CONCLUSION: Authentication flow is working correctly!")
        print("   The issue described in the review request is NOT occurring.")
    else:
        print("\n⚠️  CONCLUSION: Authentication issue confirmed!")
        print("   The system is falling back to demo mode despite valid authentication.")