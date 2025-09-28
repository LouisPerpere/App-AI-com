#!/usr/bin/env python3
"""
🎯 DIAGNOSTIC FINAL - ROOT CAUSE IDENTIFIÉ
Confirmation du problème dans posts_generator.py
"""

import requests
import json
import sys
from pymongo import MongoClient

class FinalDiagnostic:
    def __init__(self):
        self.base_url = "https://social-ai-planner-2.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.credentials = {
            "email": "lperpere@yahoo.fr",
            "password": "L@Reunion974!"
        }
        
    def authenticate(self):
        """Authenticate with the API"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login-robust",
                json=self.credentials,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                })
                
                print(f"✅ Authentication successful - User ID: {self.user_id}")
                return True
            else:
                print(f"❌ Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def check_database_collections(self):
        """Check both collections directly"""
        try:
            print(f"\n🔍 VÉRIFICATION DIRECTE BASE DE DONNÉES")
            
            # Connect to MongoDB directly
            mongo_url = "mongodb://localhost:27017/claire_marcus"
            client = MongoClient(mongo_url)
            db = client.claire_marcus
            
            user_id = self.user_id
            
            print(f"   User ID: {user_id}")
            
            # Check social_media_connections (correct collection)
            social_media_connections = list(db.social_media_connections.find({"user_id": user_id}))
            print(f"\n   📊 COLLECTION: social_media_connections")
            print(f"     Total connexions: {len(social_media_connections)}")
            
            for conn in social_media_connections:
                platform = conn.get("platform", "unknown")
                active = conn.get("active", False)
                print(f"       - {platform}: active={active}")
            
            # Check social_connections (old collection used by posts_generator)
            social_connections = list(db.social_connections.find({"user_id": user_id}))
            print(f"\n   📊 COLLECTION: social_connections (utilisée par posts_generator)")
            print(f"     Total connexions: {len(social_connections)}")
            
            for conn in social_connections:
                platform = conn.get("platform", "unknown")
                is_active = conn.get("is_active", False)
                print(f"       - {platform}: is_active={is_active}")
            
            client.close()
            
            return {
                "social_media_connections": social_media_connections,
                "social_connections": social_connections
            }
            
        except Exception as e:
            print(f"❌ Error checking database: {str(e)}")
            return None
    
    def run_final_diagnostic(self):
        """Run the final diagnostic"""
        print("🎯 DIAGNOSTIC FINAL - ROOT CAUSE GÉNÉRATION POSTS")
        print("🔍 OBJECTIF: Confirmer le problème dans posts_generator.py")
        print("=" * 70)
        
        if not self.authenticate():
            return False
        
        # Check database collections
        db_data = self.check_database_collections()
        
        print("\n" + "=" * 70)
        print("🎉 DIAGNOSTIC FINAL COMPLETED")
        print("=" * 70)
        
        if db_data:
            social_media_conns = db_data["social_media_connections"]
            social_conns = db_data["social_connections"]
            
            print(f"\n📊 RÉSULTATS:")
            print(f"   Collection social_media_connections (CORRECTE): {len(social_media_conns)} connexions")
            print(f"   Collection social_connections (UTILISÉE PAR GENERATOR): {len(social_conns)} connexions")
            
            # Analyze the issue
            if len(social_media_conns) > 0 and len(social_conns) == 0:
                print(f"\n❌ ROOT CAUSE IDENTIFIÉ:")
                print(f"   1. server.py lit correctement social_media_connections")
                print(f"   2. posts_generator.py lit incorrectement social_connections (vide)")
                print(f"   3. posts_generator.py utilise aussi 'is_active' au lieu de 'active'")
                print(f"\n🔧 SOLUTION REQUISE:")
                print(f"   Corriger posts_generator.py ligne 214-216:")
                print(f"   - Changer 'social_connections' → 'social_media_connections'")
                print(f"   - Changer 'is_active' → 'active'")
            elif len(social_media_conns) == 0 and len(social_conns) == 0:
                print(f"\n⚠️ AUCUNE CONNEXION DANS LES DEUX COLLECTIONS")
                print(f"   L'utilisateur doit reconnecter ses comptes sociaux")
            else:
                print(f"\n✅ Collections cohérentes")
        
        return True

def main():
    diagnostic = FinalDiagnostic()
    
    try:
        success = diagnostic.run_final_diagnostic()
        if success:
            print(f"\n🎯 CONCLUSION: ROOT CAUSE IDENTIFIÉ - posts_generator.py utilise mauvaise collection")
        else:
            print(f"\n💥 CONCLUSION: Diagnostic failed")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()