#!/usr/bin/env python3
"""
DIAGNOSTIC CRITIQUE - AUTHENTIFICATION FACEBOOK OAUTH CALLBACK - ENVIRONNEMENT LIVE
Test spécifique pour l'environnement de production claire-marcus.com
"""

import requests
import json
import time
from datetime import datetime

# Configuration pour l'environnement LIVE
LIVE_BACKEND_URL = "https://claire-marcus.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

def log_message(message, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def test_live_environment():
    """Test complet de l'environnement LIVE"""
    log_message("🚀 DÉBUT DIAGNOSTIC FACEBOOK OAUTH - ENVIRONNEMENT LIVE")
    log_message("=" * 80)
    log_message(f"🌐 URL CIBLE: {LIVE_BACKEND_URL}")
    log_message(f"👤 CREDENTIALS: {TEST_CREDENTIALS['email']}")
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    results = {}
    
    # TEST 1: Authentification
    try:
        log_message("🔐 TEST 1: Authentification sur environnement LIVE")
        
        response = session.post(
            f"{LIVE_BACKEND_URL}/auth/login-robust",
            json=TEST_CREDENTIALS,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            auth_token = data.get('access_token')
            user_id = data.get('user_id')
            
            session.headers.update({
                'Authorization': f'Bearer {auth_token}'
            })
            
            log_message(f"✅ Authentification réussie - User ID: {user_id}")
            results['authentication'] = True
        else:
            log_message(f"❌ Échec authentification: {response.status_code} - {response.text}", "ERROR")
            results['authentication'] = False
            return results
            
    except Exception as e:
        log_message(f"❌ Erreur authentification: {str(e)}", "ERROR")
        results['authentication'] = False
        return results
    
    # TEST 2: Status connexions sociales
    try:
        log_message("📊 TEST 2: GET /api/social/connections/status - État connexions LIVE")
        
        response = session.get(
            f"{LIVE_BACKEND_URL}/social/connections/status",
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            log_message(f"✅ Status connexions récupéré:")
            log_message(f"   Facebook connecté: {data.get('facebook_connected', False)}")
            log_message(f"   Instagram connecté: {data.get('instagram_connected', False)}")
            log_message(f"   Total connexions: {data.get('total_connections', 0)}")
            results['social_status'] = data
        else:
            log_message(f"❌ Erreur status connexions: {response.status_code}", "ERROR")
            results['social_status'] = None
            
    except Exception as e:
        log_message(f"❌ Erreur test status: {str(e)}", "ERROR")
        results['social_status'] = None
    
    # TEST 3: Debug connexions sociales
    try:
        log_message("🔍 TEST 3: GET /api/debug/social-connections - Analyse BDD LIVE")
        
        response = session.get(
            f"{LIVE_BACKEND_URL}/debug/social-connections",
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            log_message(f"✅ Diagnostic BDD récupéré:")
            log_message(f"   Total connexions: {data.get('total_connections', 0)}")
            log_message(f"   Connexions actives: {data.get('active_connections', 0)}")
            log_message(f"   Facebook: {data.get('facebook_connections', 0)}")
            log_message(f"   Instagram: {data.get('instagram_connections', 0)}")
            
            # Analyser les collections
            if 'social_media_connections' in data:
                smc = data['social_media_connections']
                log_message(f"   Collection social_media_connections: {len(smc)} items")
                for i, conn in enumerate(smc[:2]):
                    platform = conn.get('platform', 'unknown')
                    active = conn.get('active', False)
                    connected_at = conn.get('connected_at', 'unknown')
                    log_message(f"     [{i+1}] {platform} - Active: {active} - Date: {connected_at}")
            
            if 'social_connections_old' in data:
                sco = data['social_connections_old']
                log_message(f"   Collection social_connections_old: {len(sco)} items")
                for i, conn in enumerate(sco[:2]):
                    platform = conn.get('platform', 'unknown')
                    is_active = conn.get('is_active', False)
                    connected_at = conn.get('connected_at', 'unknown')
                    log_message(f"     [{i+1}] {platform} - Active: {is_active} - Date: {connected_at}")
            
            results['debug_connections'] = data
        else:
            log_message(f"❌ Erreur debug connexions: {response.status_code}", "ERROR")
            results['debug_connections'] = None
            
    except Exception as e:
        log_message(f"❌ Erreur test debug: {str(e)}", "ERROR")
        results['debug_connections'] = None
    
    # TEST 4: Callback Facebook accessibilité
    try:
        log_message("🌐 TEST 4: GET /api/social/facebook/callback - Accessibilité callback LIVE")
        
        response = session.get(
            f"{LIVE_BACKEND_URL}/social/facebook/callback",
            timeout=30,
            allow_redirects=False
        )
        
        log_message(f"✅ Callback accessible - Status: {response.status_code}")
        
        if response.status_code in [302, 307]:
            location = response.headers.get('Location', 'Non spécifié')
            log_message(f"   Redirection vers: {location}")
        elif response.status_code == 200:
            log_message(f"   Réponse directe: {response.text[:200]}...")
        else:
            log_message(f"   Réponse: {response.text[:200]}...")
            
        results['callback_accessible'] = response.status_code
        
    except Exception as e:
        log_message(f"❌ Erreur test callback: {str(e)}", "ERROR")
        results['callback_accessible'] = None
    
    # TEST 5: Génération URL OAuth
    try:
        log_message("🔗 TEST 5: GET /api/social/facebook/auth-url - Génération URL OAuth LIVE")
        
        response = session.get(
            f"{LIVE_BACKEND_URL}/social/facebook/auth-url",
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            auth_url = data.get('auth_url', '')
            
            log_message(f"✅ URL OAuth générée:")
            log_message(f"   URL: {auth_url[:100]}...")
            
            # Analyser les paramètres de l'URL
            if 'client_id=' in auth_url:
                client_id = auth_url.split('client_id=')[1].split('&')[0]
                log_message(f"   Client ID: {client_id}")
            
            if 'redirect_uri=' in auth_url:
                redirect_uri = auth_url.split('redirect_uri=')[1].split('&')[0]
                log_message(f"   Redirect URI: {redirect_uri}")
            
            if 'config_id=' in auth_url:
                config_id = auth_url.split('config_id=')[1].split('&')[0]
                log_message(f"   Config ID: {config_id}")
            
            results['oauth_url'] = data
        else:
            log_message(f"❌ Erreur génération URL: {response.status_code}", "ERROR")
            results['oauth_url'] = None
            
    except Exception as e:
        log_message(f"❌ Erreur test URL OAuth: {str(e)}", "ERROR")
        results['oauth_url'] = None
    
    # TEST 6: Configuration environnement
    try:
        log_message("⚙️ TEST 6: Vérification configuration environnement LIVE")
        
        response = session.get(
            f"{LIVE_BACKEND_URL}/health",
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            log_message(f"✅ Santé API LIVE:")
            log_message(f"   Status: {data.get('status', 'unknown')}")
            log_message(f"   Service: {data.get('service', 'unknown')}")
            log_message(f"   Timestamp: {data.get('timestamp', 'unknown')}")
            results['environment_config'] = True
        else:
            log_message(f"❌ Erreur santé API: {response.status_code}", "ERROR")
            results['environment_config'] = False
        
    except Exception as e:
        log_message(f"❌ Erreur vérification environnement: {str(e)}", "ERROR")
        results['environment_config'] = False
    
    # Analyse finale
    log_message("=" * 80)
    log_message("📋 ANALYSE FINALE - DIAGNOSTIC FACEBOOK OAUTH CALLBACK LIVE")
    log_message("=" * 80)
    
    # Compter les succès
    success_count = 0
    total_tests = 6
    
    test_results = [
        ('Authentification', results.get('authentication', False)),
        ('Status connexions sociales', results.get('social_status') is not None),
        ('Debug connexions', results.get('debug_connections') is not None),
        ('Callback accessible', results.get('callback_accessible') is not None),
        ('Génération URL OAuth', results.get('oauth_url') is not None),
        ('Configuration environnement', results.get('environment_config', False))
    ]
    
    for test_name, test_result in test_results:
        if test_result:
            success_count += 1
            log_message(f"✅ {test_name}: SUCCÈS")
        else:
            log_message(f"❌ {test_name}: ÉCHEC")
    
    success_rate = (success_count / total_tests) * 100
    log_message(f"📊 TAUX DE SUCCÈS: {success_rate:.1f}% ({success_count}/{total_tests} tests)")
    
    # Analyse de la cause racine
    log_message("=" * 80)
    log_message("🔍 ANALYSE CAUSE RACINE:")
    
    if results.get('debug_connections'):
        debug_data = results['debug_connections']
        total_connections = debug_data.get('total_connections', 0)
        active_connections = debug_data.get('active_connections', 0)
        facebook_connections = debug_data.get('facebook_connections', 0)
        
        if total_connections == 0:
            log_message("❌ CAUSE RACINE: Aucune connexion Facebook n'existe dans la base de données LIVE")
            log_message("   SOLUTION: L'utilisateur doit reconnecter son compte Facebook sur LIVE")
        elif active_connections == 0:
            log_message("❌ CAUSE RACINE: Connexions Facebook existent mais sont INACTIVES sur LIVE")
            log_message("   SOLUTION: Vérifier pourquoi les connexions sont marquées comme inactives")
        elif facebook_connections == 0:
            log_message("❌ CAUSE RACINE: Connexions existent mais aucune n'est Facebook sur LIVE")
            log_message("   SOLUTION: L'utilisateur doit connecter spécifiquement Facebook")
        else:
            log_message("⚠️ CAUSE RACINE: Connexions Facebook actives existent - problème dans l'échange de tokens")
            log_message("   INVESTIGATION: Vérifier la qualité des tokens et l'échange OAuth sur LIVE")
    
    # Recommandations finales
    log_message("=" * 80)
    log_message("💡 RECOMMANDATIONS POUR ENVIRONNEMENT LIVE:")
    
    if success_rate < 50:
        log_message("🚨 CRITIQUE: Problèmes majeurs détectés sur LIVE - intervention urgente requise")
    elif success_rate < 80:
        log_message("⚠️ ATTENTION: Problèmes modérés sur LIVE - corrections nécessaires")
    else:
        log_message("✅ BON: Système LIVE majoritairement fonctionnel - ajustements mineurs")
    
    log_message("=" * 80)
    log_message("🏁 DIAGNOSTIC FACEBOOK OAUTH CALLBACK LIVE TERMINÉ")
    log_message("=" * 80)
    
    return results

if __name__ == "__main__":
    test_live_environment()