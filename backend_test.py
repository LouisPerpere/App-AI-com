#!/usr/bin/env python3
"""
Test de diagnostic urgent - Analyse de site web échoue à ~30%
Vérification de la sauvegarde des analyses en base de données
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://insta-automate-2.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"
TEST_WEBSITE = "https://myownwatch.fr"

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

def check_existing_analysis(token):
    """Vérifier les analyses existantes"""
    print("\n🔍 Step 2: Checking existing website analyses...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/website/analysis", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ GET /api/website/analysis successful")
        print(f"📊 Analysis data structure: {type(data)}")
        
        if isinstance(data, dict):
            print(f"📋 Analysis fields: {list(data.keys())}")
            if 'analysis_summary' in data:
                print(f"📝 Analysis summary length: {len(data.get('analysis_summary', ''))}")
            if 'storytelling_analysis' in data:
                print(f"📖 Storytelling analysis length: {len(data.get('storytelling_analysis', ''))}")
            if 'created_at' in data:
                print(f"📅 Analysis created at: {data.get('created_at')}")
            if 'website_url' in data:
                print(f"🌐 Website URL: {data.get('website_url')}")
        elif isinstance(data, list):
            print(f"📊 Found {len(data)} analyses")
            for i, analysis in enumerate(data):
                print(f"  Analysis {i+1}: {analysis.get('website_url', 'Unknown URL')} - {analysis.get('created_at', 'No date')}")
        else:
            print(f"⚠️ Unexpected data type: {type(data)}")
            
        return data
    else:
        print(f"❌ Failed to get existing analysis: {response.status_code} - {response.text}")
        return None

def run_website_analysis(token):
    """Lancer une nouvelle analyse de site web"""
    print(f"\n🚀 Step 3: Running website analysis for {TEST_WEBSITE}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    analysis_data = {"website_url": TEST_WEBSITE}
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/website/analyze", json=analysis_data, headers=headers, timeout=120)
    end_time = time.time()
    
    duration = end_time - start_time
    print(f"⏱️ Analysis duration: {duration:.1f} seconds")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Website analysis completed successfully")
        print(f"📊 Response fields: {list(data.keys())}")
        
        # Vérifier les champs critiques
        if 'analysis_summary' in data:
            summary_len = len(data.get('analysis_summary', ''))
            print(f"📝 Analysis summary: {summary_len} characters")
        
        if 'storytelling_analysis' in data:
            story_len = len(data.get('storytelling_analysis', ''))
            print(f"📖 Storytelling analysis: {story_len} characters")
            
        if 'analysis_type' in data:
            print(f"🤖 Analysis type: {data.get('analysis_type')}")
            
        return data
    else:
        print(f"❌ Website analysis failed: {response.status_code}")
        print(f"📄 Response: {response.text}")
        return None

def verify_analysis_persistence(token, wait_seconds=5):
    """Vérifier que l'analyse est bien persistée"""
    print(f"\n⏳ Step 4: Waiting {wait_seconds} seconds then checking persistence...")
    time.sleep(wait_seconds)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/website/analysis", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Analysis persistence check successful")
        
        if isinstance(data, dict) and data.get('analysis_summary'):
            print(f"✅ Analysis found in database")
            print(f"📝 Summary length: {len(data.get('analysis_summary', ''))}")
            print(f"🌐 Website URL: {data.get('website_url', 'Not found')}")
            print(f"📅 Created at: {data.get('created_at', 'Not found')}")
            return True
        elif isinstance(data, list) and len(data) > 0:
            latest = data[0] if data else {}
            print(f"✅ Found {len(data)} analyses in database")
            print(f"📝 Latest analysis URL: {latest.get('website_url', 'Not found')}")
            return True
        else:
            print(f"❌ No analysis found in database after save")
            print(f"📊 Data type: {type(data)}, Content: {data}")
            return False
    else:
        print(f"❌ Failed to verify persistence: {response.status_code} - {response.text}")
        return False

def check_database_directly(token):
    """Vérifier directement en base via un autre endpoint"""
    print(f"\n🔍 Step 5: Direct database check via business profile...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/business-profile", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Business profile accessible - User exists in database")
        print(f"📧 Email: {data.get('email', 'Not found')}")
        print(f"🏢 Business name: {data.get('business_name', 'Not found')}")
        return True
    else:
        print(f"❌ Business profile check failed: {response.status_code}")
        return False

def main():
    """Test principal de diagnostic"""
    print("🎯 DIAGNOSTIC URGENT - Analyse de site web sauvegarde")
    print("=" * 60)
    
    # Authentification
    token, user_id = authenticate()
    if not token:
        return
    
    # Vérifier analyses existantes AVANT
    print("\n📋 AVANT nouvelle analyse:")
    existing_analysis = check_existing_analysis(token)
    
    # Vérifier accès base de données
    db_accessible = check_database_directly(token)
    
    # Lancer nouvelle analyse
    new_analysis = run_website_analysis(token)
    if not new_analysis:
        print("\n❌ ÉCHEC: Analyse n'a pas pu être complétée")
        return
    
    # Vérifier persistence APRÈS
    print("\n📋 APRÈS nouvelle analyse:")
    is_persisted = verify_analysis_persistence(token)
    
    # Résumé final
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ DU DIAGNOSTIC:")
    print(f"✅ Authentification: OK")
    print(f"✅ Accès base de données: {'OK' if db_accessible else 'ÉCHEC'}")
    print(f"✅ Analyse complétée: OK")
    print(f"{'✅' if is_persisted else '❌'} Sauvegarde en base: {'OK' if is_persisted else 'ÉCHEC'}")
    
    if not is_persisted:
        print("\n🚨 PROBLÈME IDENTIFIÉ: L'analyse se termine mais n'est pas sauvegardée")
        print("🔍 Causes possibles:")
        print("  - Problème de persistence MongoDB")
        print("  - Erreur dans la fonction de sauvegarde")
        print("  - Problème de mapping user_id/owner_id")
        print("  - Transaction non commitée")
        print("  - Erreur silencieuse dans save_website_analysis()")
    else:
        print("\n✅ SYSTÈME OPÉRATIONNEL: Analyse et sauvegarde fonctionnent")

if __name__ == "__main__":
    main()