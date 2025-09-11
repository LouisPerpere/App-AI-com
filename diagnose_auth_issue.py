#!/usr/bin/env python3
"""
Script de diagnostic rapide pour identifier le problème d'authentification
"""
import requests
import json

def test_auth_flow():
    """Test complet du flow d'authentification"""
    
    print("🔍 DIAGNOSTIC D'AUTHENTIFICATION")
    print("="*50)
    
    base_url = "https://claire-marcus-pwa-1.emergent.host"
    
    # Test 1: Santé de l'API
    print("\n1. Test de santé de l'API")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📄 Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Erreur API santé: {e}")
        return
    
    # Test 2: Authentification
    print("\n2. Test d'authentification")
    try:
        auth_data = {
            "email": "lperpere@yahoo.fr",
            "password": "L@Reunion974!"
        }
        
        response = requests.post(
            f"{base_url}/api/auth/login-robust",
            json=auth_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Authentification réussie!")
            print(f"   🔑 Token reçu: {data.get('access_token', 'MANQUANT')[:30]}...")
            print(f"   👤 User ID: {data.get('user_id', 'MANQUANT')}")
            print(f"   📧 Email: {data.get('email', 'MANQUANT')}")
            
            # Test 3: Utilisation du token
            print("\n3. Test d'utilisation du token")
            token = data.get('access_token')
            if token:
                try:
                    headers = {"Authorization": f"Bearer {token}"}
                    me_response = requests.get(f"{base_url}/api/auth/me", headers=headers, timeout=10)
                    print(f"   📊 Status /api/auth/me: {me_response.status_code}")
                    if me_response.status_code == 200:
                        print(f"   ✅ Token valide - données utilisateur récupérées")
                        print(f"   📄 Données: {me_response.json()}")
                    else:
                        print(f"   ❌ Token invalide: {me_response.text}")
                except Exception as e:
                    print(f"   ❌ Erreur test token: {e}")
            
        else:
            print(f"   ❌ Authentification échouée")
            print(f"   📄 Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erreur authentification: {e}")
    
    # Test 4: CORS et headers
    print("\n4. Test CORS et headers")
    try:
        # Test avec différents headers pour simuler le navigateur
        headers = {
            "Content-Type": "application/json",
            "Origin": "https://claire-marcus-pwa-1.emergent.host",
            "Referer": "https://claire-marcus-pwa-1.emergent.host/"
        }
        
        response = requests.post(
            f"{base_url}/api/auth/login-robust",
            json=auth_data,
            headers=headers,
            timeout=15
        )
        
        print(f"   📊 Status avec headers CORS: {response.status_code}")
        print(f"   🔍 CORS headers dans response:")
        for header, value in response.headers.items():
            if 'access-control' in header.lower() or 'cors' in header.lower():
                print(f"      {header}: {value}")
                
    except Exception as e:
        print(f"   ❌ Erreur test CORS: {e}")
    
    print(f"\n✅ Diagnostic terminé")

if __name__ == "__main__":
    test_auth_flow()