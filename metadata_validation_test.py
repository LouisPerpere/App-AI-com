#!/usr/bin/env python3
"""
Validation spécifique des métadonnées du système de backup croisé
"""

import requests
import json

# Configuration
BASE_URL = "https://social-publisher-10.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"
TEST_WEBSITE = "https://myownwatch.fr"

def authenticate():
    """Authentification utilisateur"""
    auth_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
    response = requests.post(f"{BASE_URL}/auth/login-robust", json=auth_data)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('access_token'), data.get('user_id')
    return None, None

def validate_metadata():
    """Validation des métadonnées spécifiques"""
    print("🔍 VALIDATION MÉTADONNÉES SYSTÈME BACKUP CROISÉ")
    print("=" * 60)
    
    token, user_id = authenticate()
    if not token:
        print("❌ Authentication failed")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    analysis_data = {"website_url": TEST_WEBSITE}
    
    response = requests.post(f"{BASE_URL}/website/analyze", json=analysis_data, headers=headers, timeout=120)
    
    if response.status_code == 200:
        data = response.json()
        
        print("📊 MÉTADONNÉES SYSTÈME BACKUP CROISÉ:")
        print(f"   cross_backup_system: {data.get('cross_backup_system')}")
        print(f"   business_ai: {data.get('business_ai')}")
        print(f"   storytelling_ai: {data.get('storytelling_ai')}")
        print(f"   analysis_type: {data.get('analysis_type')}")
        print(f"   backup_business_available: {data.get('backup_business_available')}")
        print(f"   backup_storytelling_available: {data.get('backup_storytelling_available')}")
        print(f"   analysis_optimized: {data.get('analysis_optimized')}")
        print(f"   timeout_handled: {data.get('timeout_handled')}")
        
        # Validation des valeurs attendues
        expected_values = {
            'cross_backup_system': True,
            'business_ai': 'GPT-4o',
            'storytelling_ai': 'Claude Sonnet 4',
            'analysis_type': 'gpt4o_plus_claude_storytelling',
            'backup_business_available': 'Claude Sonnet 4',
            'backup_storytelling_available': 'GPT-4o',
            'analysis_optimized': True,
            'timeout_handled': True
        }
        
        print("\n✅ VALIDATION RÉSULTATS:")
        all_correct = True
        for key, expected in expected_values.items():
            actual = data.get(key)
            if actual == expected:
                print(f"   ✅ {key}: {actual} (correct)")
            else:
                print(f"   ❌ {key}: {actual} (expected: {expected})")
                all_correct = False
        
        if all_correct:
            print("\n🎉 TOUTES LES MÉTADONNÉES SONT CORRECTES!")
        else:
            print("\n❌ CERTAINES MÉTADONNÉES SONT INCORRECTES")
            
    else:
        print(f"❌ Analysis failed: {response.status_code}")

if __name__ == "__main__":
    validate_metadata()