#!/usr/bin/env python3
"""
🎯 TEST DÉTAILLÉ CALLBACK FACEBOOK AVEC STATE APPROPRIÉ
Test avec le format de state correct pour diagnostiquer l'échange de token
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://social-publisher-10.preview.emergentagent.com/api"
EMAIL = "lperpere@yahoo.fr"
PASSWORD = "L@Reunion974!"

def authenticate():
    """Authentification"""
    session = requests.Session()
    auth_data = {"email": EMAIL, "password": PASSWORD}
    
    response = session.post(f"{BACKEND_URL}/auth/login-robust", json=auth_data)
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        user_id = data.get("user_id")
        session.headers.update({"Authorization": f"Bearer {token}"})
        return session, user_id
    return None, None

def test_facebook_callback_with_proper_state():
    """Test callback Facebook avec state approprié"""
    print("🎯 TEST CALLBACK FACEBOOK AVEC STATE APPROPRIÉ")
    print("=" * 50)
    
    session, user_id = authenticate()
    if not session:
        print("❌ Échec authentification")
        return
    
    print(f"✅ Authentifié - User ID: {user_id}")
    
    # Générer un state au format approprié
    random_state = f"fb_test_{int(time.time())}"
    proper_state = f"{random_state}|{user_id}"
    
    print(f"🔑 State généré: {proper_state}")
    
    # Test 1: Callback avec code invalide (pour voir l'erreur d'échange)
    print("\n📋 Test 1: Callback avec code invalide...")
    test_params_invalid = {
        "code": "invalid_test_code_123",
        "state": proper_state
    }
    
    response = session.get(f"{BACKEND_URL}/social/facebook/callback", params=test_params_invalid)
    print(f"Status: {response.status_code}")
    if response.status_code in [302, 307]:
        redirect_url = response.headers.get('Location', 'N/A')
        print(f"Redirection: {redirect_url}")
        
        # Analyser la redirection
        if "auth_error" in redirect_url:
            print("❌ Redirection d'erreur détectée")
        elif "auth_success" in redirect_url:
            print("✅ Redirection de succès détectée (malgré code invalide)")
    
    # Test 2: Callback sans code (pour voir le comportement par défaut)
    print("\n📋 Test 2: Callback sans code...")
    test_params_no_code = {
        "state": proper_state
    }
    
    response = session.get(f"{BACKEND_URL}/social/facebook/callback", params=test_params_no_code)
    print(f"Status: {response.status_code}")
    if response.status_code in [302, 307]:
        redirect_url = response.headers.get('Location', 'N/A')
        print(f"Redirection: {redirect_url}")
    
    # Test 3: Callback avec erreur Facebook
    print("\n📋 Test 3: Callback avec erreur Facebook...")
    test_params_error = {
        "error": "access_denied",
        "error_description": "User denied the request",
        "state": proper_state
    }
    
    response = session.get(f"{BACKEND_URL}/social/facebook/callback", params=test_params_error)
    print(f"Status: {response.status_code}")
    if response.status_code in [302, 307]:
        redirect_url = response.headers.get('Location', 'N/A')
        print(f"Redirection: {redirect_url}")
    
    # Vérifier l'état des connexions après les tests
    print("\n📊 État des connexions après tests...")
    response = session.get(f"{BACKEND_URL}/debug/social-connections")
    if response.status_code == 200:
        data = response.json()
        print(f"Connexions actives: {data.get('active_connections', 0)}")
        print(f"Connexions Facebook: {data.get('facebook_connections', 0)}")
        
        # Montrer les dernières connexions créées
        connections = data.get('social_media_connections', [])
        recent_facebook = [c for c in connections if c.get('platform') == 'facebook'][-3:]
        
        print(f"\n📋 Dernières connexions Facebook ({len(recent_facebook)}):")
        for i, conn in enumerate(recent_facebook):
            print(f"  {i+1}. Active: {conn.get('active')}, Created: {conn.get('created_at', 'unknown')}")
            print(f"     Access Token: {'✅ Present' if conn.get('access_token') else '❌ Missing'}")
            print(f"     Page Name: {conn.get('page_name', 'N/A')}")

def check_backend_logs_during_test():
    """Vérifier les logs pendant le test"""
    print("\n📋 VÉRIFICATION LOGS BACKEND")
    print("=" * 30)
    print("Exécutez cette commande dans un autre terminal pour voir les logs en temps réel:")
    print("tail -f /var/log/supervisor/backend.out.log | grep -i 'facebook\\|oauth\\|callback'")
    print("\nRecherchez spécifiquement:")
    print("- '🔄 Facebook OAuth callback received'")
    print("- '❌ Erreur OAuth Facebook'")
    print("- 'Invalid verification code format'")
    print("- '✅ Created Facebook connection'")

if __name__ == "__main__":
    check_backend_logs_during_test()
    test_facebook_callback_with_proper_state()