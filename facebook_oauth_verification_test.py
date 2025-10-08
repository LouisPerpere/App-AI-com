#!/usr/bin/env python3
"""
🎯 FACEBOOK OAUTH URL VERIFICATION TEST
Test spécifique pour vérifier les variables d'environnement Facebook et la génération d'URL OAuth
Demande française: Vérification des paramètres manquants dans l'URL OAuth générée
"""

import requests
import json
import os
from urllib.parse import urlparse, parse_qs

# Configuration
BACKEND_URL = "https://post-restore.preview.emergentagent.com/api"
EMAIL = "lperpere@yahoo.fr"
PASSWORD = "L@Reunion974!"

def test_facebook_oauth_url_generation():
    """Test complet de la génération d'URL OAuth Facebook"""
    print("🎯 FACEBOOK OAUTH URL GENERATION TESTING STARTED")
    print("=" * 80)
    
    # Step 1: Authentication
    print("\n📋 Step 1: Authentication")
    try:
        auth_response = requests.post(f"{BACKEND_URL}/auth/login-robust", json={
            "email": EMAIL,
            "password": PASSWORD
        })
        
        if auth_response.status_code == 200:
            auth_data = auth_response.json()
            token = auth_data["access_token"]
            user_id = auth_data["user_id"]
            print(f"✅ Authentication successful")
            print(f"   User ID: {user_id}")
            print(f"   Token: {token[:30]}...")
        else:
            print(f"❌ Authentication failed: {auth_response.status_code}")
            print(f"   Response: {auth_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Test Facebook Auth URL Generation
    print("\n📋 Step 2: Facebook Auth URL Generation")
    try:
        fb_auth_response = requests.get(f"{BACKEND_URL}/social/facebook/auth-url", headers=headers)
        
        if fb_auth_response.status_code == 200:
            fb_data = fb_auth_response.json()
            print(f"✅ Facebook auth URL generated successfully")
            
            # Analyser l'URL générée
            auth_url = fb_data.get("auth_url", "")
            print(f"\n🔍 URL ANALYSIS:")
            print(f"   Full URL: {auth_url}")
            
            # Parser l'URL pour extraire les paramètres
            parsed_url = urlparse(auth_url)
            params = parse_qs(parsed_url.query)
            
            print(f"\n📊 URL PARAMETERS:")
            for key, value in params.items():
                print(f"   {key}: {value[0] if value else 'MISSING'}")
            
            # Vérifications spécifiques demandées
            print(f"\n🎯 VERIFICATION DES PARAMETRES REQUIS:")
            
            required_params = {
                "client_id": "FACEBOOK_APP_ID",
                "redirect_uri": "FACEBOOK_REDIRECT_URI", 
                "scope": "Scopes Facebook",
                "response_type": "Type de réponse",
                "state": "Token de sécurité",
                "config_id": "FACEBOOK_CONFIG_ID"
            }
            
            all_params_present = True
            for param, description in required_params.items():
                if param in params and params[param][0]:
                    print(f"   ✅ {param}: {params[param][0]} ({description})")
                else:
                    print(f"   ❌ {param}: MISSING ({description})")
                    all_params_present = False
            
            # Vérifications spécifiques mentionnées dans la demande
            print(f"\n🔍 VERIFICATIONS SPECIFIQUES:")
            
            # Vérifier redirect_uri
            redirect_uri = params.get("redirect_uri", [""])[0]
            expected_redirect = "https://claire-marcus.com/api/social/facebook/callback"
            if redirect_uri == expected_redirect:
                print(f"   ✅ redirect_uri correct: {redirect_uri}")
            else:
                print(f"   ❌ redirect_uri incorrect: {redirect_uri}")
                print(f"      Attendu: {expected_redirect}")
            
            # Vérifier scope
            scope = params.get("scope", [""])[0]
            expected_scopes = "pages_show_list,pages_read_engagement,pages_manage_posts"
            if scope == expected_scopes:
                print(f"   ✅ scope correct: {scope}")
            else:
                print(f"   ❌ scope incorrect: {scope}")
                print(f"      Attendu: {expected_scopes}")
            
            # Vérifier config_id
            config_id = params.get("config_id", [""])[0]
            if config_id:
                print(f"   ✅ config_id présent: {config_id}")
            else:
                print(f"   ❌ config_id manquant")
            
            # Afficher les données de réponse complètes
            print(f"\n📋 RESPONSE DATA COMPLETE:")
            for key, value in fb_data.items():
                if key != "auth_url":  # URL déjà affichée
                    print(f"   {key}: {value}")
            
            return all_params_present
            
        else:
            print(f"❌ Facebook auth URL generation failed: {fb_auth_response.status_code}")
            print(f"   Response: {fb_auth_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Facebook auth URL generation error: {e}")
        return False

def test_environment_variables():
    """Test des variables d'environnement Facebook"""
    print("\n📋 Step 3: Environment Variables Verification")
    
    # Lire le fichier .env du backend
    env_file_path = "/app/backend/.env"
    env_vars = {}
    
    try:
        with open(env_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value.strip('"')
        
        print("✅ Environment file read successfully")
        
        # Vérifier les variables Facebook spécifiques
        facebook_vars = {
            "FACEBOOK_APP_ID": "ID de l'application Facebook",
            "FACEBOOK_CONFIG_ID": "ID de configuration Facebook Login for Business", 
            "FACEBOOK_REDIRECT_URI": "URI de redirection Facebook"
        }
        
        print(f"\n🔍 FACEBOOK ENVIRONMENT VARIABLES:")
        all_vars_present = True
        
        for var_name, description in facebook_vars.items():
            if var_name in env_vars and env_vars[var_name]:
                print(f"   ✅ {var_name}: {env_vars[var_name]} ({description})")
            else:
                print(f"   ❌ {var_name}: NOT SET ({description})")
                all_vars_present = False
        
        return all_vars_present
        
    except Exception as e:
        print(f"❌ Error reading environment variables: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚨 FACEBOOK OAUTH DIAGNOSTIC - VERIFICATION VARIABLES ENVIRONNEMENT")
    print("Identifiants: lperpere@yahoo.fr / L@Reunion974!")
    print("Objectif: Comprendre pourquoi l'URL OAuth générée ne contient pas les bons paramètres")
    print("=" * 80)
    
    # Test des variables d'environnement
    env_test_passed = test_environment_variables()
    
    # Test de génération d'URL OAuth
    oauth_test_passed = test_facebook_oauth_url_generation()
    
    # Résumé final
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ FINAL:")
    print(f"   Variables d'environnement: {'✅ OK' if env_test_passed else '❌ PROBLÈME'}")
    print(f"   Génération URL OAuth: {'✅ OK' if oauth_test_passed else '❌ PROBLÈME'}")
    
    if env_test_passed and oauth_test_passed:
        print("\n🎉 DIAGNOSTIC COMPLET: Toutes les vérifications sont passées!")
        print("   L'URL OAuth contient bien tous les paramètres requis.")
    else:
        print("\n🚨 DIAGNOSTIC COMPLET: Des problèmes ont été identifiés!")
        print("   Vérifiez les détails ci-dessus pour identifier la cause racine.")
    
    print("=" * 80)

if __name__ == "__main__":
    main()