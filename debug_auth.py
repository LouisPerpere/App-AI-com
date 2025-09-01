#!/usr/bin/env python3
"""
Script de débogage pour tester l'authentification
"""

import bcrypt
import sys
import os
sys.path.append('/app/backend')

from database import get_database

def debug_auth():
    """Déboguer l'authentification"""
    
    # Données de test
    email = "lperpere@yahoo.fr"
    password = "L@Reunion974!"
    
    print(f"🔍 DÉBOGAGE AUTHENTIFICATION")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    print("=" * 50)
    
    # Connexion à la base de données
    db_manager = get_database()
    users_collection = db_manager.db.users
    
    # Trouver l'utilisateur
    email_clean = email.lower().strip()
    user = users_collection.find_one({"email": email_clean})
    
    if not user:
        print(f"❌ Utilisateur non trouvé avec email: {email_clean}")
        return
    
    print(f"✅ Utilisateur trouvé:")
    print(f"   User ID: {user.get('user_id')}")
    print(f"   Email stocké: {user.get('email')}")
    
    # Vérifier le mot de passe
    stored_pw = user.get("password_hash") or user.get("hashed_password")
    if not stored_pw:
        print(f"❌ Aucun mot de passe stocké")
        return
    
    print(f"✅ Mot de passe stocké trouvé:")
    print(f"   Hash: {stored_pw[:50]}...")
    
    # Test de vérification bcrypt
    try:
        password_bytes = password.encode("utf-8")
        stored_bytes = stored_pw.encode("utf-8")
        
        print(f"🔍 Test bcrypt:")
        print(f"   Password bytes: {password_bytes}")
        print(f"   Stored bytes: {stored_bytes[:50]}...")
        
        is_valid = bcrypt.checkpw(password_bytes, stored_bytes)
        print(f"   ✅ Résultat: {is_valid}")
        
        if is_valid:
            print(f"🎉 Authentification réussie !")
        else:
            print(f"❌ Authentification échouée")
            
    except Exception as e:
        print(f"❌ Erreur lors du test bcrypt: {e}")

if __name__ == "__main__":
    debug_auth()