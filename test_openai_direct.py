#!/usr/bin/env python3
"""
Test direct d'OpenAI pour vérifier si l'API fonctionne
"""
import os
import sys
sys.path.append('/app/backend')
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
env_path = Path('/app/backend/.env')
load_dotenv(env_path)

print(f"✅ Variables d'environnement chargées depuis {env_path}")

# Vérifier la clé API
API_KEY = os.environ.get('OPENAI_API_KEY')
print(f"🔍 OPENAI_API_KEY disponible: {'Oui' if API_KEY else 'Non'}")
if API_KEY:
    print(f"🔑 Clé OpenAI: {API_KEY[:20]}...")

# Test d'import OpenAI
try:
    from openai import OpenAI
    print("✅ Module OpenAI importé avec succès")
    OPENAI_AVAILABLE = True
except ImportError as e:
    print(f"❌ Erreur import OpenAI: {e}")
    OPENAI_AVAILABLE = False

print(f"🔍 OPENAI_AVAILABLE: {OPENAI_AVAILABLE}")
print(f"🔍 API_KEY présente: {bool(API_KEY)}")

# Test direct de l'API si tout est OK
if OPENAI_AVAILABLE and API_KEY:
    print("\n🤖 Test direct de l'API OpenAI...")
    try:
        client = OpenAI(api_key=API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Tu es un assistant test. Réponds en JSON."},
                {"role": "user", "content": "Teste-moi: retourne {'status': 'success', 'message': 'OpenAI fonctionne parfaitement'}"}
            ],
            temperature=0.1,
            max_tokens=100
        )
        
        result = response.choices[0].message.content
        print(f"✅ Réponse OpenAI: {result}")
        
    except Exception as e:
        print(f"❌ Erreur OpenAI API: {e}")
        
else:
    print(f"❌ Conditions non remplies pour le test API")
    print(f"   - OPENAI_AVAILABLE: {OPENAI_AVAILABLE}")
    print(f"   - API_KEY: {'Oui' if API_KEY else 'Non'}")