#!/usr/bin/env python3
"""
🎯 COMPLETE OAUTH URL COMPARISON TEST
Test complet pour comparer les URLs OAuth Facebook et Instagram
Demande française: Identifier la différence entre diagnostic précédent et code actuel
"""

import requests
import json
import os
from urllib.parse import urlparse, parse_qs

# Configuration
BACKEND_URL = "https://social-publisher-10.preview.emergentagent.com/api"
EMAIL = "lperpere@yahoo.fr"
PASSWORD = "L@Reunion974!"

def authenticate():
    """Authentification utilisateur"""
    try:
        auth_response = requests.post(f"{BACKEND_URL}/auth/login-robust", json={
            "email": EMAIL,
            "password": PASSWORD
        })
        
        if auth_response.status_code == 200:
            auth_data = auth_response.json()
            token = auth_data["access_token"]
            user_id = auth_data["user_id"]
            print(f"✅ Authentication successful - User ID: {user_id}")
            return {"Authorization": f"Bearer {token}"}
        else:
            print(f"❌ Authentication failed: {auth_response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def analyze_oauth_url(platform, url_data):
    """Analyser une URL OAuth et ses paramètres"""
    print(f"\n🔍 {platform.upper()} OAUTH URL ANALYSIS:")
    
    auth_url = url_data.get("auth_url", "")
    print(f"   Full URL: {auth_url}")
    
    # Parser l'URL pour extraire les paramètres
    parsed_url = urlparse(auth_url)
    params = parse_qs(parsed_url.query)
    
    print(f"\n📊 {platform.upper()} URL PARAMETERS:")
    for key, value in params.items():
        print(f"   {key}: {value[0] if value else 'MISSING'}")
    
    # Vérifications des paramètres requis
    required_params = ["client_id", "redirect_uri", "scope", "response_type", "state", "config_id"]
    
    print(f"\n🎯 {platform.upper()} PARAMETER VERIFICATION:")
    all_present = True
    for param in required_params:
        if param in params and params[param][0]:
            print(f"   ✅ {param}: {params[param][0]}")
        else:
            print(f"   ❌ {param}: MISSING")
            all_present = False
    
    return all_present, params

def main():
    """Test principal de comparaison OAuth"""
    print("🚨 COMPLETE OAUTH URL COMPARISON TEST")
    print("Objectif: Comparer Facebook vs Instagram et identifier les différences")
    print("=" * 80)
    
    # Authentification
    headers = authenticate()
    if not headers:
        return
    
    # Test Facebook Auth URL
    print("\n📋 TESTING FACEBOOK AUTH URL")
    try:
        fb_response = requests.get(f"{BACKEND_URL}/social/facebook/auth-url", headers=headers)
        if fb_response.status_code == 200:
            fb_data = fb_response.json()
            fb_success, fb_params = analyze_oauth_url("Facebook", fb_data)
        else:
            print(f"❌ Facebook auth URL failed: {fb_response.status_code}")
            fb_success = False
            fb_params = {}
    except Exception as e:
        print(f"❌ Facebook auth URL error: {e}")
        fb_success = False
        fb_params = {}
    
    # Test Instagram Auth URL
    print("\n📋 TESTING INSTAGRAM AUTH URL")
    try:
        ig_response = requests.get(f"{BACKEND_URL}/social/instagram/auth-url", headers=headers)
        if ig_response.status_code == 200:
            ig_data = ig_response.json()
            ig_success, ig_params = analyze_oauth_url("Instagram", ig_data)
        else:
            print(f"❌ Instagram auth URL failed: {ig_response.status_code}")
            ig_success = False
            ig_params = {}
    except Exception as e:
        print(f"❌ Instagram auth URL error: {e}")
        ig_success = False
        ig_params = {}
    
    # Comparaison des paramètres
    print("\n" + "=" * 80)
    print("📊 COMPARISON ANALYSIS:")
    
    if fb_success and ig_success:
        print("\n🔍 PARAMETER COMPARISON:")
        all_params = set(list(fb_params.keys()) + list(ig_params.keys()))
        
        for param in sorted(all_params):
            fb_value = fb_params.get(param, ["MISSING"])[0]
            ig_value = ig_params.get(param, ["MISSING"])[0]
            
            if fb_value == ig_value:
                print(f"   ✅ {param}: SAME ({fb_value})")
            else:
                print(f"   🔄 {param}: DIFFERENT")
                print(f"      Facebook: {fb_value}")
                print(f"      Instagram: {ig_value}")
    
    # Résumé final
    print("\n" + "=" * 80)
    print("📊 FINAL SUMMARY:")
    print(f"   Facebook OAuth URL: {'✅ ALL PARAMETERS PRESENT' if fb_success else '❌ MISSING PARAMETERS'}")
    print(f"   Instagram OAuth URL: {'✅ ALL PARAMETERS PRESENT' if ig_success else '❌ MISSING PARAMETERS'}")
    
    if fb_success and ig_success:
        print("\n🎉 CONCLUSION: Both Facebook and Instagram OAuth URLs contain ALL required parameters!")
        print("   The previous diagnostic showing missing parameters may have been from a different version.")
        print("   Current implementation is working correctly.")
    else:
        print("\n🚨 CONCLUSION: Issues found with OAuth URL generation!")
        print("   Check the detailed analysis above for specific problems.")
    
    print("=" * 80)

if __name__ == "__main__":
    main()