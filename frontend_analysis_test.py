#!/usr/bin/env python3
"""
Test de diagnostic - Analyse de site web disparaît au rechargement
Vérification du chargement de l'analyse dans le frontend
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://social-ai-planner-2.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

def authenticate():
    """Authentification utilisateur"""
    print("🔐 Step 1: Authentication...")
    
    auth_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/auth/login-robust", json=auth_data)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('access_token')
        user_id = data.get('user_id')
        print(f"✅ Authentication successful - User ID: {user_id}")
        return token, user_id
    else:
        print(f"❌ Authentication failed: {response.status_code} - {response.text}")
        return None, None

def check_analysis_endpoint(token):
    """Vérifier l'endpoint GET /api/website/analysis"""
    print("\n🔍 Step 2: Testing GET /api/website/analysis endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/website/analysis", headers=headers)
    
    print(f"📊 Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ GET /api/website/analysis successful")
        print(f"📋 Response type: {type(data)}")
        
        if isinstance(data, dict):
            print(f"📝 Analysis fields: {list(data.keys())}")
            
            # Vérifier les champs critiques
            critical_fields = ['analysis_summary', 'storytelling_analysis', 'website_url', 'created_at']
            for field in critical_fields:
                if field in data:
                    value = data[field]
                    if isinstance(value, str):
                        print(f"✅ {field}: {len(value)} characters")
                    else:
                        print(f"✅ {field}: {value}")
                else:
                    print(f"❌ {field}: MISSING")
            
            return data
        else:
            print(f"⚠️ Unexpected response type: {type(data)}")
            return data
    else:
        print(f"❌ GET /api/website/analysis failed: {response.status_code}")
        print(f"📄 Response: {response.text}")
        return None

def simulate_page_reload_scenario(token):
    """Simuler le scénario de rechargement de page"""
    print("\n🔄 Step 3: Simulating page reload scenario...")
    
    # Simuler plusieurs appels comme le ferait le frontend au rechargement
    endpoints_to_test = [
        "/auth/me",
        "/business-profile", 
        "/website/analysis",
        "/content/pending",
        "/notes"
    ]
    
    headers = {"Authorization": f"Bearer {token}"}
    results = {}
    
    for endpoint in endpoints_to_test:
        print(f"📡 Testing {endpoint}...")
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=10)
            results[endpoint] = {
                "status": response.status_code,
                "success": response.status_code == 200,
                "has_data": bool(response.json() if response.status_code == 200 else False)
            }
            
            if endpoint == "/website/analysis" and response.status_code == 200:
                data = response.json()
                results[endpoint]["analysis_present"] = bool(data.get('analysis_summary'))
                results[endpoint]["website_url"] = data.get('website_url', 'Not found')
                
        except Exception as e:
            print(f"❌ Error testing {endpoint}: {e}")
            results[endpoint] = {"status": "error", "success": False, "error": str(e)}
    
    return results

def main():
    """Test principal de diagnostic"""
    print("🎯 DIAGNOSTIC - Analyse disparaît au rechargement")
    print("=" * 60)
    
    # Authentification
    token, user_id = authenticate()
    if not token:
        return
    
    # Test endpoint analyse
    analysis_data = check_analysis_endpoint(token)
    
    # Simuler rechargement
    reload_results = simulate_page_reload_scenario(token)
    
    # Résumé final
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ DU DIAGNOSTIC:")
    print(f"✅ Authentification: OK")
    
    # Analyse des résultats
    analysis_available = analysis_data is not None and isinstance(analysis_data, dict) and analysis_data.get('analysis_summary')
    print(f"{'✅' if analysis_available else '❌'} Analyse disponible via API: {'OK' if analysis_available else 'ÉCHEC'}")
    
    # Résultats du rechargement
    print(f"\n📊 Résultats simulation rechargement:")
    for endpoint, result in reload_results.items():
        status_icon = "✅" if result.get("success") else "❌"
        print(f"  {status_icon} {endpoint}: {result.get('status', 'unknown')}")
        
        if endpoint == "/website/analysis":
            analysis_present = result.get("analysis_present", False)
            print(f"    📝 Analyse présente: {'OUI' if analysis_present else 'NON'}")
            if analysis_present:
                print(f"    🌐 URL: {result.get('website_url', 'N/A')}")
    
    # Diagnostic final
    website_analysis_works = reload_results.get("/website/analysis", {}).get("analysis_present", False)
    
    if not website_analysis_works:
        print(f"\n🚨 PROBLÈME IDENTIFIÉ:")
        print(f"  - L'endpoint /website/analysis ne retourne pas d'analyse")
        print(f"  - Cela explique pourquoi l'analyse disparaît au rechargement")
        print(f"  - Le frontend ne peut pas charger l'analyse existante")
        
        print(f"\n🔍 CAUSES POSSIBLES:")
        print(f"  - Problème de persistence en base de données")
        print(f"  - Erreur dans la fonction get_website_analysis()")
        print(f"  - Problème de mapping user_id dans la requête")
        print(f"  - Analyse sauvegardée mais non récupérable")
    else:
        print(f"\n✅ SYSTÈME OPÉRATIONNEL:")
        print(f"  - L'analyse est bien disponible via l'API")
        print(f"  - Le problème pourrait être côté frontend")
        print(f"  - Vérifier le chargement dans loadWebsiteAnalysis()")

if __name__ == "__main__":
    main()