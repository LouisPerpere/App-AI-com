#!/usr/bin/env python3
"""
Script pour créer un utilisateur dans la base de données MongoDB
Nécessaire car l'endpoint /register n'est pas disponible sur le serveur actuel
"""

import uuid
from passlib.context import CryptContext
from database import get_database

# Configuration du hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user():
    """Créer l'utilisateur lperpere@yahoo.fr avec le mot de passe L@Reunion974!"""
    
    # Connexion à la base de données
    db_manager = get_database()
    users_collection = db_manager.db.users
    
    # Données utilisateur
    email = "lperpere@yahoo.fr"
    password = "L@Reunion974!"
    
    # Vérifier si l'utilisateur existe déjà
    existing_user = users_collection.find_one({"email": email})
    if existing_user:
        print(f"✅ L'utilisateur {email} existe déjà dans la base de données")
        return
    
    # Créer un nouvel utilisateur
    user_id = str(uuid.uuid4())
    hashed_password = pwd_context.hash(password)
    
    user_data = {
        "user_id": user_id,
        "email": email,
        "password": hashed_password,
        "business_name": "Claire et Marcus Test",
        "created_at": "2025-01-01T00:00:00Z",
        "is_active": True,
        "is_admin": False,
        "subscription_status": "active",
        # Champs business profile par défaut
        "business_type": None,
        "business_description": None,
        "target_audience": None,
        "brand_tone": None,
        "posting_frequency": None,
        "website_url": None,
        "preferred_platforms": [],
        "budget_range": None,
        "hashtags_primary": [],
        "hashtags_secondary": []
    }
    
    # Insérer dans la base de données
    result = users_collection.insert_one(user_data)
    
    if result.inserted_id:
        print(f"✅ Utilisateur créé avec succès !")
        print(f"   Email: {email}")
        print(f"   User ID: {user_id}")
        print(f"   Mot de passe: {password}")
        print(f"   Document ID MongoDB: {result.inserted_id}")
    else:
        print("❌ Erreur lors de la création de l'utilisateur")

if __name__ == "__main__":
    create_user()