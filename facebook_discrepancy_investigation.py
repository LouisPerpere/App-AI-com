#!/usr/bin/env python3
"""
INVESTIGATION CRITIQUE - DISCORDANCE CONNEXIONS FACEBOOK LIVE
Analyser la discordance entre status (Facebook connecté: True) et debug (0 connexions)
"""

import requests
import json
from datetime import datetime

LIVE_BACKEND_URL = "https://claire-marcus.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

def investigate_facebook_connection_discrepancy():
    """Investiguer la discordance des connexions Facebook"""
    print("🔍 INVESTIGATION CRITIQUE - DISCORDANCE CONNEXIONS FACEBOOK LIVE")
    print("=" * 80)
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # Authentification
    response = session.post(
        f"{LIVE_BACKEND_URL}/auth/login-robust",
        json=TEST_CREDENTIALS,
        timeout=30
    )
    
    if response.status_code != 200:
        print("❌ Échec authentification")
        return
    
    data = response.json()
    user_id = data.get('user_id')
    session.headers.update({
        'Authorization': f'Bearer {data.get("access_token")}'
    })
    
    print(f"✅ Authentifié - User ID: {user_id}")
    print()
    
    # TEST 1: Status endpoint
    print("📊 TEST 1: GET /api/social/connections/status")
    response = session.get(f"{LIVE_BACKEND_URL}/social/connections/status", timeout=30)
    if response.status_code == 200:
        status_data = response.json()
        print(f"   Facebook connecté: {status_data.get('facebook_connected', False)}")
        print(f"   Instagram connecté: {status_data.get('instagram_connected', False)}")
        print(f"   Total connexions: {status_data.get('total_connections', 0)}")
    print()
    
    # TEST 2: Debug endpoint
    print("🔍 TEST 2: GET /api/debug/social-connections")
    response = session.get(f"{LIVE_BACKEND_URL}/debug/social-connections", timeout=30)
    if response.status_code == 200:
        debug_data = response.json()
        print(f"   Total connexions: {debug_data.get('total_connections', 0)}")
        print(f"   Connexions actives: {debug_data.get('active_connections', 0)}")
        print(f"   Facebook: {debug_data.get('facebook_connections', 0)}")
        print(f"   Instagram: {debug_data.get('instagram_connections', 0)}")
        
        # Analyser les connexions détaillées
        smc = debug_data.get('social_media_connections', [])
        print(f"   Collection social_media_connections: {len(smc)} items")
        for i, conn in enumerate(smc):
            platform = conn.get('platform', 'unknown')
            active = conn.get('active', False)
            connected_at = conn.get('connected_at', 'unknown')
            access_token = conn.get('access_token', 'N/A')[:20] + '...' if conn.get('access_token') else 'None'
            print(f"     [{i+1}] {platform} - Active: {active} - Date: {connected_at} - Token: {access_token}")
    print()
    
    # TEST 3: Regular connections endpoint
    print("🔗 TEST 3: GET /api/social/connections")
    response = session.get(f"{LIVE_BACKEND_URL}/social/connections", timeout=30)
    if response.status_code == 200:
        connections_data = response.json()
        if isinstance(connections_data, list):
            print(f"   Connexions retournées: {len(connections_data)}")
            for i, conn in enumerate(connections_data):
                if isinstance(conn, dict):
                    platform = conn.get('platform', 'unknown')
                    active = conn.get('active', False)
                    connected_at = conn.get('connected_at', 'unknown')
                    print(f"     [{i+1}] {platform} - Active: {active} - Date: {connected_at}")
                else:
                    print(f"     [{i+1}] Connexion non-dict: {conn}")
        else:
            print(f"   Réponse non-liste: {connections_data}")
    else:
        print(f"   Erreur: {response.status_code} - {response.text[:100]}")
    print()
    
    # TEST 4: Test publication pour vérifier la connexion réelle
    print("📝 TEST 4: POST /api/posts/publish - Test publication Facebook")
    
    # D'abord, récupérer un post pour tester
    posts_response = session.get(f"{LIVE_BACKEND_URL}/posts/generated", timeout=30)
    if posts_response.status_code == 200:
        posts_data = posts_response.json()
        posts = posts_data.get('posts', [])
        facebook_posts = [p for p in posts if p.get('platform') == 'facebook']
        
        if facebook_posts:
            test_post = facebook_posts[0]
            post_id = test_post.get('id')
            print(f"   Test avec post ID: {post_id}")
            
            publish_response = session.post(
                f"{LIVE_BACKEND_URL}/posts/publish",
                json={"post_id": post_id},
                timeout=30
            )
            
            print(f"   Status publication: {publish_response.status_code}")
            if publish_response.status_code == 200:
                pub_data = publish_response.json()
                print(f"   Résultat: {pub_data.get('message', 'N/A')}")
            else:
                print(f"   Erreur: {publish_response.text[:200]}")
        else:
            print("   Aucun post Facebook trouvé pour test")
    print()
    
    # ANALYSE FINALE
    print("=" * 80)
    print("🎯 ANALYSE DE LA DISCORDANCE")
    print("=" * 80)
    
    print("OBSERVATIONS CRITIQUES:")
    print("1. Status endpoint dit: Facebook connecté = True")
    print("2. Debug endpoint dit: 0 connexions Facebook actives")
    print("3. Collection social_media_connections contient 1 connexion Facebook active")
    print()
    
    print("HYPOTHÈSES POSSIBLES:")
    print("❓ H1: Endpoints utilisent des logiques de comptage différentes")
    print("❓ H2: Problème de synchronisation entre collections")
    print("❓ H3: Token Facebook existe mais est invalide/expiré")
    print("❓ H4: Problème de filtrage dans l'endpoint debug")
    print()
    
    print("RECOMMANDATIONS:")
    print("🔧 R1: Vérifier la cohérence des requêtes entre endpoints")
    print("🔧 R2: Tester la validité du token Facebook existant")
    print("🔧 R3: Vérifier les logs backend pendant une tentative de publication")
    print("🔧 R4: Analyser le code des endpoints pour identifier la différence")
    
    print("=" * 80)

if __name__ == "__main__":
    investigate_facebook_connection_discrepancy()