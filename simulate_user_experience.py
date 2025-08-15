#!/usr/bin/env python3
"""
Test qui reproduit exactement l'expérience utilisateur :
1. Login
2. Modifier des champs
3. Recharger la page
4. Voir ce qui persiste vs ce qui revient aux valeurs demo
"""

import time
import requests
import json

BACKEND_URL = "http://localhost:8001"
API_URL = f"{BACKEND_URL}/api"

def simulate_user_experience():
    """Simule l'expérience utilisateur exacte"""
    
    print("🎭 SIMULATION DE L'EXPÉRIENCE UTILISATEUR")
    print("=" * 50)
    
    # 1. Login (comme l'utilisateur fait)
    print("🔐 Step 1: Login comme l'utilisateur")
    login_data = {"email": "lperpere@yahoo.fr", "password": "L@Reunion974!"}
    response = requests.post(f"{API_URL}/auth/login", json=login_data)
    token = response.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    print("✅ Login successful")
    
    # 2. Voir l'état initial
    print("\n📋 Step 2: État initial du profil")
    response = requests.get(f"{API_URL}/business-profile", headers=headers)
    initial_profile = response.json()
    
    print("État initial:")
    print(f"  business_name: '{initial_profile.get('business_name')}'")
    print(f"  business_description: '{initial_profile.get('business_description')}'")
    print(f"  website_url: '{initial_profile.get('website_url')}'")
    print(f"  email: '{initial_profile.get('email')}'")
    
    # 3. Modifier comme l'utilisateur (typique : changer le nom de l'entreprise)
    print("\n✏️ Step 3: L'utilisateur modifie le nom de l'entreprise")
    
    # Simulate user typing "Mon Restaurant Favori" 
    user_business_name = "Mon Restaurant Favori"
    user_description = "Un restaurant familial authentique"
    user_website = "https://mon-restaurant-favori.fr"
    
    # PUT avec les modifications utilisateur
    modified_data = initial_profile.copy()
    modified_data.update({
        "business_name": user_business_name,
        "business_description": user_description,
        "website_url": user_website
    })
    
    response = requests.put(f"{API_URL}/business-profile", json=modified_data, headers=headers)
    print(f"✅ Profil modifié - business_name: '{user_business_name}'")
    print(f"✅ Profil modifié - description: '{user_description}'")  
    print(f"✅ Profil modifié - website: '{user_website}'")
    
    # 4. Vérification immédiate (ce que l'utilisateur voit avant F5)
    print("\n🔍 Step 4: Vérification immédiate après modification")
    response = requests.get(f"{API_URL}/business-profile", headers=headers)
    after_save = response.json()
    
    print("Après sauvegarde:")
    print(f"  business_name: '{after_save.get('business_name')}'")
    print(f"  business_description: '{after_save.get('business_description')}'")
    print(f"  website_url: '{after_save.get('website_url')}'")
    
    # 5. Simule F5 / rechargement de page
    print("\n🔄 Step 5: SIMULATION F5 - Rechargement de page")
    print("(Simulation : nouveau login + GET business-profile)")
    
    # Nouveau login (comme si la page était rechargée)
    response = requests.post(f"{API_URL}/auth/login", json=login_data)
    new_token = response.json().get('access_token')
    new_headers = {'Authorization': f'Bearer {new_token}', 'Content-Type': 'application/json'}
    
    # GET profile (comme au rechargement)
    response = requests.get(f"{API_URL}/business-profile", headers=new_headers)
    after_reload = response.json()
    
    print("APRÈS RECHARGEMENT DE PAGE (F5):")
    print(f"  business_name: '{after_reload.get('business_name')}'")
    print(f"  business_description: '{after_reload.get('business_description')}'") 
    print(f"  website_url: '{after_reload.get('website_url')}'")
    
    # 6. Analyse de ce qui a persisté
    print("\n📊 ANALYSE DE PERSISTANCE APRÈS F5:")
    
    # Check business_name
    if after_reload.get('business_name') == user_business_name:
        print("✅ business_name: PERSISTE")
    elif after_reload.get('business_name') == "Demo Business":
        print("❌ business_name: RETOURNE À 'Demo Business'")
    else:
        print(f"⚠️ business_name: Valeur inattendue '{after_reload.get('business_name')}'")
    
    # Check business_description
    if after_reload.get('business_description') == user_description:
        print("✅ business_description: PERSISTE")
    elif "Exemple d'entreprise" in after_reload.get('business_description', ''):
        print("❌ business_description: RETOURNE À LA DÉMO")
    else:
        print(f"⚠️ business_description: Valeur inattendue '{after_reload.get('business_description')}'")
    
    # Check website_url
    if after_reload.get('website_url') == user_website:
        print("✅ website_url: PERSISTE") 
    else:
        print(f"❌ website_url: Changed to '{after_reload.get('website_url')}'")
    
    return {
        'business_name_persists': after_reload.get('business_name') == user_business_name,
        'description_persists': after_reload.get('business_description') == user_description,
        'website_persists': after_reload.get('website_url') == user_website
    }

if __name__ == "__main__":
    results = simulate_user_experience()
    
    print("\n🏁 RÉSULTAT DE LA SIMULATION:")
    if all(results.values()):
        print("✅ TOUS LES CHAMPS PERSISTENT - Problème résolu !")
    elif results['website_persists'] and not all(results.values()):
        print("🎯 PROBLÈME CONFIRMÉ : Seul website_url persiste")
        print("Le problème est confirmé côté backend/API")
    else:
        print("🤔 Résultats mixtes - nécessite investigation approfondie")