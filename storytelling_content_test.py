#!/usr/bin/env python3
"""
Test to examine the storytelling_analysis content in detail
"""

import requests
import json

BACKEND_URL = "https://claire-marcus-app-1.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}
TEST_WEBSITE = "https://myownwatch.fr"

def test_storytelling_content():
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
    print("🔍 Analyzing storytelling content...")
    analysis_response = session.post(
        f"{BACKEND_URL}/website/analyze",
        json={"website_url": TEST_WEBSITE},
        timeout=120
    )
    
    if analysis_response.status_code != 200:
        print(f"❌ Analysis failed: {analysis_response.status_code}")
        return
    
    data = analysis_response.json()
    storytelling = data.get("storytelling_analysis", "")
    
    print(f"\n📊 STORYTELLING ANALYSIS CONTENT:")
    print(f"Length: {len(storytelling)} chars")
    print(f"Word count: {len(storytelling.split())} words")
    print("\n" + "="*60)
    print(storytelling)
    print("="*60)
    
    # Check for required sections
    sections_to_check = [
        "L'HISTOIRE DE L'ENTREPRISE",
        "CE QUI LES REND UNIQUES",
        "histoire",
        "entreprise",
        "unique",
        "rend"
    ]
    
    print(f"\n🔍 SECTION ANALYSIS:")
    for section in sections_to_check:
        if section.lower() in storytelling.lower():
            print(f"✅ Found: '{section}'")
        else:
            print(f"❌ Missing: '{section}'")

if __name__ == "__main__":
    test_storytelling_content()