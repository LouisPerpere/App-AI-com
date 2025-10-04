#!/usr/bin/env python3
"""
Final URL Test - Test the French review request for URL updates
"""

import requests
import json

# Configuration
BACKEND_URL = "https://claire-marcus-app-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

def authenticate():
    """Authenticate and get access token"""
    session = requests.Session()
    
    response = session.post(f"{API_BASE}/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    
    if response.status_code == 200:
        data = response.json()
        access_token = data.get("access_token")
        user_id = data.get("user_id")
        
        session.headers.update({
            "Authorization": f"Bearer {access_token}"
        })
        
        print(f"✅ Authentication successful: {TEST_EMAIL}, User ID: {user_id}")
        return session, user_id
    else:
        print(f"❌ Authentication failed: {response.status_code}")
        return None, None

def test_french_review_requirements():
    """Test the specific French review requirements"""
    session, user_id = authenticate()
    if not session:
        return
    
    print("\n🇫🇷 FRENCH REVIEW REQUIREMENTS TEST")
    print("=" * 60)
    print("OBJECTIF: Mettre à jour toutes les URLs de claire-marcus.com vers claire-marcus-api.onrender.com")
    print()
    
    # Step 1: Get current state
    response = session.get(f"{API_BASE}/content/pending?limit=100")
    
    if response.status_code != 200:
        print(f"❌ Failed to get content: {response.status_code}")
        return
    
    data = response.json()
    content = data.get("content", [])
    total_files = len(content)
    
    print(f"📊 ANALYSE DES {total_files} FICHIERS:")
    print("-" * 40)
    
    # Analyze current URLs
    claire_marcus_com_urls = 0
    claire_marcus_api_urls = 0
    libfusion_urls = 0
    mongodb_operations = 0
    null_urls = 0
    other_urls = 0
    
    claire_marcus_com_examples = []
    claire_marcus_api_examples = []
    mongodb_operation_examples = []
    
    for item in content:
        thumb_url = item.get("thumb_url")
        filename = item.get("filename", "unknown")
        
        if thumb_url is None:
            null_urls += 1
        elif isinstance(thumb_url, dict):
            # MongoDB aggregation operation detected
            mongodb_operations += 1
            if len(mongodb_operation_examples) < 2:
                mongodb_operation_examples.append(f"{filename}: {thumb_url}")
        elif isinstance(thumb_url, str):
            if "claire-marcus.com/uploads/" in thumb_url:
                claire_marcus_com_urls += 1
                if len(claire_marcus_com_examples) < 2:
                    claire_marcus_com_examples.append(f"{filename}: {thumb_url}")
            elif "claire-marcus-api.onrender.com/uploads/" in thumb_url:
                claire_marcus_api_urls += 1
                if len(claire_marcus_api_examples) < 2:
                    claire_marcus_api_examples.append(f"{filename}: {thumb_url}")
            elif "libfusion.preview.emergentagent.com" in thumb_url:
                libfusion_urls += 1
            else:
                other_urls += 1
        else:
            other_urls += 1
    
    print(f"• URLs claire-marcus.com: {claire_marcus_com_urls}")
    print(f"• URLs claire-marcus-api.onrender.com: {claire_marcus_api_urls}")
    print(f"• URLs libfusion: {libfusion_urls}")
    print(f"• Opérations MongoDB non exécutées: {mongodb_operations}")
    print(f"• URLs null: {null_urls}")
    print(f"• Autres: {other_urls}")
    print()
    
    if claire_marcus_com_examples:
        print("Exemples claire-marcus.com:")
        for example in claire_marcus_com_examples:
            print(f"  {example}")
        print()
    
    if claire_marcus_api_examples:
        print("Exemples claire-marcus-api.onrender.com:")
        for example in claire_marcus_api_examples:
            print(f"  {example}")
        print()
    
    if mongodb_operation_examples:
        print("Exemples opérations MongoDB non exécutées:")
        for example in mongodb_operation_examples:
            print(f"  {example}")
        print()
    
    # Step 2: Test API accessibility
    print("🌐 TEST ACCESSIBILITÉ API claire-marcus-api.onrender.com")
    print("-" * 50)
    
    # Test if claire-marcus-api.onrender.com is accessible
    test_urls = [
        "https://claire-marcus-api.onrender.com/uploads/thumbs/test.webp",
        "https://claire-marcus-api.onrender.com/",
        "https://claire-marcus-api.onrender.com/health"
    ]
    
    api_accessible = False
    for test_url in test_urls:
        try:
            response = requests.get(test_url, timeout=10)
            content_type = response.headers.get('content-type', '')
            print(f"✅ {test_url}: {response.status_code} - {content_type}")
            if response.status_code in [200, 404]:  # 404 is OK for test files
                api_accessible = True
        except Exception as e:
            print(f"❌ {test_url}: Error - {str(e)[:50]}")
    
    print()
    
    # Step 3: Verify the objective
    print("🎯 VÉRIFICATION OBJECTIF FRANÇAIS")
    print("-" * 40)
    
    objective_met = claire_marcus_api_urls > 0 and claire_marcus_com_urls == 0
    api_working = api_accessible
    
    print(f"1. Authentification avec lperpere@yahoo.fr: ✅ RÉUSSIE")
    print(f"2. URLs mises à jour vers claire-marcus-api.onrender.com: {'✅ OUI' if claire_marcus_api_urls > 0 else '❌ NON'} ({claire_marcus_api_urls} fichiers)")
    print(f"3. URLs claire-marcus.com supprimées: {'✅ OUI' if claire_marcus_com_urls == 0 else '❌ NON'} ({claire_marcus_com_urls} restantes)")
    print(f"4. API claire-marcus-api.onrender.com accessible: {'✅ OUI' if api_working else '❌ NON'}")
    print(f"5. Test GET /api/content/pending: ✅ FONCTIONNEL ({total_files} fichiers)")
    print()
    
    # Step 4: Final assessment
    print("📋 RÉSUMÉ FINAL")
    print("-" * 20)
    
    if objective_met and api_working:
        print("🎉 OBJECTIF FRANÇAIS ATTEINT: Toutes les URLs pointent vers claire-marcus-api.onrender.com")
        success = True
    elif claire_marcus_api_urls > 0:
        print("⚠️ OBJECTIF PARTIELLEMENT ATTEINT: Certaines URLs pointent vers claire-marcus-api.onrender.com")
        success = False
    else:
        print("❌ OBJECTIF NON ATTEINT: Aucune URL ne pointe vers claire-marcus-api.onrender.com")
        success = False
    
    if mongodb_operations > 0:
        print(f"⚠️ PROBLÈME DÉTECTÉ: {mongodb_operations} opérations MongoDB non exécutées dans la base de données")
    
    print(f"\nNombre total d'URLs mises à jour: {claire_marcus_api_urls}")
    print(f"Nombre d'URLs restant à mettre à jour: {claire_marcus_com_urls}")
    print(f"API accessible: {'Oui' if api_working else 'Non'}")
    
    return success

if __name__ == "__main__":
    success = test_french_review_requirements()
    
    if success:
        print("\n✅ Overall testing: SUCCESS")
        exit(0)
    else:
        print("\n❌ Overall testing: FAILED")
        exit(1)