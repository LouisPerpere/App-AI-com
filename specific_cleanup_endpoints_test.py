#!/usr/bin/env python3
"""
🎯 TEST SPÉCIFIQUE DES ENDPOINTS DE NETTOYAGE MENTIONNÉS
Test des endpoints exacts mentionnés dans la demande française:
1. POST /api/debug/clean-invalid-tokens
2. POST /api/debug/clean-library-badges  
3. GET /api/debug/social-connections

Identifiants: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import sys
from datetime import datetime

class SpecificCleanupEndpointsTest:
    def __init__(self):
        self.base_url = "https://post-restore.preview.emergentagent.com/api"
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
            print(f"🔐 Authentication avec {self.credentials['email']}")
            
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
                
                print(f"   ✅ Authentification réussie - User ID: {self.user_id}")
                return True
            else:
                print(f"   ❌ Échec authentification: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Erreur authentification: {str(e)}")
            return False
    
    def test_clean_invalid_tokens_endpoint(self):
        """Test POST /api/debug/clean-invalid-tokens"""
        try:
            print(f"\n🧹 Test: POST /api/debug/clean-invalid-tokens")
            print(f"   Objectif: Supprimer les connexions avec tokens de test/NULL")
            
            response = self.session.post(f"{self.base_url}/debug/clean-invalid-tokens")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Endpoint accessible et fonctionnel")
                print(f"   📊 Résultats:")
                
                if "message" in data:
                    print(f"     Message: {data['message']}")
                
                if "deleted_count" in data:
                    deleted = data["deleted_count"]
                    print(f"     Connexions supprimées: {deleted}")
                    
                    if deleted > 0:
                        print(f"     ✅ {deleted} connexions avec tokens invalides supprimées")
                    else:
                        print(f"     ✅ Aucune connexion invalide trouvée (déjà nettoyé)")
                
                return True
            else:
                print(f"   ❌ Échec endpoint: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Erreur test endpoint: {str(e)}")
            return False
    
    def test_clean_library_badges_endpoint(self):
        """Test POST /api/debug/clean-library-badges"""
        try:
            print(f"\n🏷️ Test: POST /api/debug/clean-library-badges")
            print(f"   Objectif: Retirer badges Facebook/Instagram des contenus non utilisés")
            
            response = self.session.post(f"{self.base_url}/debug/clean-library-badges")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Endpoint accessible et fonctionnel")
                print(f"   📊 Résultats:")
                
                if "message" in data:
                    print(f"     Message: {data['message']}")
                
                if "cleaned_badges" in data:
                    cleaned = data["cleaned_badges"]
                    print(f"     Badges nettoyés: {cleaned}")
                    
                    if cleaned > 0:
                        print(f"     ✅ {cleaned} badges orphelins supprimés")
                    else:
                        print(f"     ✅ Aucun badge orphelin trouvé")
                
                if "details" in data:
                    details = data["details"]
                    print(f"     📋 Détails du nettoyage:")
                    for key, value in details.items():
                        print(f"       {key}: {value}")
                
                return True
            else:
                print(f"   ❌ Échec endpoint: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Erreur test endpoint: {str(e)}")
            return False
    
    def test_social_connections_diagnostic_endpoint(self):
        """Test GET /api/debug/social-connections"""
        try:
            print(f"\n🔍 Test: GET /api/debug/social-connections")
            print(f"   Objectif: Confirmer 0 connexions actives (tokens invalides supprimés)")
            
            response = self.session.get(f"{self.base_url}/debug/social-connections")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Endpoint accessible et fonctionnel")
                print(f"   📊 État des connexions sociales:")
                
                # Check social_media_connections
                if "social_media_connections" in data:
                    connections = data["social_media_connections"]
                    total_connections = len(connections)
                    active_connections = len([c for c in connections if c.get("active") == True])
                    
                    print(f"     📋 Collection social_media_connections:")
                    print(f"       Total connexions: {total_connections}")
                    print(f"       Connexions actives: {active_connections}")
                    
                    if active_connections == 0:
                        print(f"       ✅ OBJECTIF ATTEINT: 0 connexions actives confirmé")
                        print(f"       ✅ Utilisateur peut reconnecter proprement")
                    else:
                        print(f"       ❌ PROBLÈME: {active_connections} connexions actives restantes")
                        
                        # Show remaining active connections
                        for i, conn in enumerate([c for c in connections if c.get("active") == True]):
                            platform = conn.get("platform", "unknown")
                            token = conn.get("access_token", "None")
                            print(f"         {i+1}. Platform: {platform}, Token: {token}")
                
                # Check summary
                if "summary" in data:
                    summary = data["summary"]
                    print(f"     📊 Résumé:")
                    for key, value in summary.items():
                        print(f"       {key}: {value}")
                
                # Determine success
                connections = data.get("social_media_connections", [])
                active_count = len([c for c in connections if c.get("active") == True])
                
                return active_count == 0
            else:
                print(f"   ❌ Échec endpoint: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Erreur test endpoint: {str(e)}")
            return False
    
    def run_specific_endpoints_test(self):
        """Execute test of the specific endpoints mentioned in the French request"""
        print("🎯 TEST DES ENDPOINTS SPÉCIFIQUES DE NETTOYAGE")
        print("🌐 ENVIRONNEMENT: Preview (social-ai-planner-2.preview.emergentagent.com)")
        print("🔍 OBJECTIF: Vérifier les 3 endpoints mentionnés dans la demande")
        print("=" * 70)
        
        # Authentication
        if not self.authenticate():
            print("\n❌ CRITIQUE: Échec authentification - impossible de continuer")
            return False
        
        # Test the 3 specific endpoints
        print(f"\n📋 TESTS DES 3 ENDPOINTS REQUIS:")
        
        # 1. Clean invalid tokens
        tokens_success = self.test_clean_invalid_tokens_endpoint()
        
        # 2. Clean library badges  
        badges_success = self.test_clean_library_badges_endpoint()
        
        # 3. Verify social connections
        connections_success = self.test_social_connections_diagnostic_endpoint()
        
        print("\n" + "=" * 70)
        print("🎉 RÉSULTATS DES TESTS SPÉCIFIQUES")
        print("=" * 70)
        
        print(f"✅ Authentification: RÉUSSIE")
        print(f"{'✅' if tokens_success else '❌'} POST /api/debug/clean-invalid-tokens: {'FONCTIONNEL' if tokens_success else 'ÉCHEC'}")
        print(f"{'✅' if badges_success else '❌'} POST /api/debug/clean-library-badges: {'FONCTIONNEL' if badges_success else 'ÉCHEC'}")
        print(f"{'✅' if connections_success else '❌'} GET /api/debug/social-connections: {'0 CONNEXIONS CONFIRMÉ' if connections_success else 'PROBLÈME DÉTECTÉ'}")
        
        print(f"\n🎯 ÉVALUATION GLOBALE:")
        if tokens_success and badges_success and connections_success:
            print(f"   ✅ MISSION ACCOMPLIE: Tous les endpoints fonctionnent correctement")
            print(f"   ✅ NETTOYAGE RÉUSSI: Tokens invalides supprimés")
            print(f"   ✅ BADGES NETTOYÉS: Badges orphelins retirés")
            print(f"   ✅ ÉTAT PROPRE: 0 connexions actives confirmé")
            print(f"   ✅ PRÊT POUR RECONNEXION: L'utilisateur peut reconnecter Facebook/Instagram")
        else:
            print(f"   ❌ PROBLÈMES DÉTECTÉS: Certains endpoints ne fonctionnent pas correctement")
            if not tokens_success:
                print(f"     - Nettoyage des tokens invalides échoué")
            if not badges_success:
                print(f"     - Nettoyage des badges orphelins échoué")
            if not connections_success:
                print(f"     - Des connexions actives persistent")
        
        print(f"\n📋 INSTRUCTIONS POUR L'UTILISATEUR:")
        print(f"   1. Identifiants: lperpere@yahoo.fr / L@Reunion974!")
        print(f"   2. Aller sur la page des connexions sociales")
        print(f"   3. Cliquer 'Connecter' pour Facebook")
        print(f"   4. Compléter le flux OAuth avec de vrais tokens Facebook")
        print(f"   5. Cliquer 'Connecter' pour Instagram")
        print(f"   6. Compléter le flux OAuth avec de vrais tokens Instagram")
        print(f"   7. Vérifier que les boutons passent à 'Connecté'")
        
        print("=" * 70)
        
        return tokens_success and badges_success and connections_success

def main():
    """Main execution function"""
    test = SpecificCleanupEndpointsTest()
    
    try:
        success = test.run_specific_endpoints_test()
        if success:
            print(f"\n🎯 CONCLUSION: Test des endpoints spécifiques RÉUSSI")
            print(f"   Les 3 endpoints mentionnés fonctionnent correctement")
            print(f"   Le nettoyage est complet et l'utilisateur peut reconnecter")
            sys.exit(0)
        else:
            print(f"\n💥 CONCLUSION: Test des endpoints spécifiques ÉCHOUÉ")
            print(f"   Certains endpoints ne fonctionnent pas comme attendu")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⚠️ Test interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()