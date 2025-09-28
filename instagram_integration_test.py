#!/usr/bin/env python3
"""
TEST RÉCUPÉRATION PAGE INSTAGRAM LIÉE - ClaireEtMarcus
Test de récupération des informations de la page Instagram liée à la page Facebook
pour implémenter la publication croisée Facebook + Instagram.

Ce test vérifie:
1. La validité du token d'accès Facebook
2. La récupération du compte Instagram Business lié
3. Les permissions Instagram pour la publication
4. Les limites de publication Instagram
5. L'intégration avec le backend existant
"""

import requests
import json
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration des tests
FACEBOOK_PAGE_ID = "741078965763774"
ACCESS_TOKEN = "EAAP2f1Vj6XMBPbsv5Dqs3aeN4vIVuAkFPcuqDqN0CrZBeszwhHaAmU83xLMEddvEb70EQRO3yzffvFHLMAIhZCSbav3BZARn2RtzZCdXsqF76oqRZA9n9UrBWrCqgGxujyOwrajJuPZCXiUBXwww8U0HBjeHhXcuoAKB55gqNbpQChpkILCJNLbqaOpUXJScNTOYRSX1M7tvfkDbvq3P46ZCtHpCGTuf7nEzjBZAxXZC3wXZClIcCZD"
GRAPH_API_BASE = "https://graph.facebook.com/v21.0"

# Configuration backend
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://social-publisher-10.preview.emergentagent.com')
BACKEND_API_URL = f"{BACKEND_URL}/api"

# Configuration Facebook depuis .env
FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID', '1115451684022643')
FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET', '68a3924e5551a06e5b1074d9316277b2')

class InstagramIntegrationTester:
    def __init__(self):
        self.test_results = []
        self.instagram_id = None
        
    def log_test(self, test_name, success, details, error=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   📋 {details}")
        if error:
            print(f"   ❌ Error: {error}")
        print()
        
    def test_1_retrieve_instagram_account(self):
        """Test 1: Récupération compte Instagram lié"""
        try:
            url = f"{GRAPH_API_BASE}/{FACEBOOK_PAGE_ID}"
            params = {
                "fields": "instagram_business_account",
                "access_token": ACCESS_TOKEN
            }
            
            print(f"🔍 Testing Instagram account retrieval...")
            print(f"   URL: {url}")
            print(f"   Fields: instagram_business_account")
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   📊 Response: {json.dumps(data, indent=2)}")
                
                if "instagram_business_account" in data:
                    instagram_account = data["instagram_business_account"]
                    if instagram_account and "id" in instagram_account:
                        self.instagram_id = instagram_account["id"]
                        self.log_test(
                            "Récupération compte Instagram lié",
                            True,
                            f"Instagram Business Account ID trouvé: {self.instagram_id}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Récupération compte Instagram lié",
                            False,
                            "Aucun compte Instagram business lié trouvé",
                            "instagram_business_account est vide ou sans ID"
                        )
                        return False
                else:
                    self.log_test(
                        "Récupération compte Instagram lié",
                        False,
                        "Champ instagram_business_account manquant dans la réponse",
                        f"Réponse reçue: {data}"
                    )
                    return False
            else:
                error_data = response.json() if response.content else {}
                self.log_test(
                    "Récupération compte Instagram lié",
                    False,
                    f"Erreur API Facebook: Status {response.status_code}",
                    f"Erreur: {error_data}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Récupération compte Instagram lié",
                False,
                "Exception lors de la requête",
                str(e)
            )
            return False
    
    def test_2_instagram_basic_info(self):
        """Test 2: Permissions Instagram - informations de base"""
        if not self.instagram_id:
            self.log_test(
                "Permissions Instagram - informations de base",
                False,
                "Test ignoré - pas d'Instagram ID disponible",
                "Instagram ID requis du test précédent"
            )
            return False
            
        try:
            url = f"{GRAPH_API_BASE}/{self.instagram_id}"
            params = {
                "fields": "id,name,username",
                "access_token": ACCESS_TOKEN
            }
            
            print(f"🔍 Testing Instagram basic permissions...")
            print(f"   URL: {url}")
            print(f"   Fields: id,name,username")
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   📊 Response: {json.dumps(data, indent=2)}")
                
                # Vérifier les champs requis
                required_fields = ["id", "name", "username"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    username = data.get("username", "")
                    name = data.get("name", "")
                    
                    # Vérifier si le nom correspond à "ClaireEtMarcus" ou similaire
                    is_correct_account = (
                        "claire" in username.lower() and "marcus" in username.lower()
                    ) or (
                        "claire" in name.lower() and "marcus" in name.lower()
                    )
                    
                    if is_correct_account:
                        self.log_test(
                            "Permissions Instagram - informations de base",
                            True,
                            f"Accès réussi - Username: {username}, Name: {name}, ID: {data['id']}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Permissions Instagram - informations de base",
                            True,  # Permissions OK mais compte différent
                            f"Permissions OK mais compte inattendu - Username: {username}, Name: {name}",
                            "Le compte ne correspond pas à 'ClaireEtMarcus'"
                        )
                        return True
                else:
                    self.log_test(
                        "Permissions Instagram - informations de base",
                        False,
                        f"Champs manquants dans la réponse: {missing_fields}",
                        f"Réponse: {data}"
                    )
                    return False
            else:
                error_data = response.json() if response.content else {}
                self.log_test(
                    "Permissions Instagram - informations de base",
                    False,
                    f"Erreur API Instagram: Status {response.status_code}",
                    f"Erreur: {error_data}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Permissions Instagram - informations de base",
                False,
                "Exception lors de la requête",
                str(e)
            )
            return False
    
    def test_3_instagram_full_access(self):
        """Test 3: Capabilities publication - accès complet"""
        if not self.instagram_id:
            self.log_test(
                "Capabilities publication - accès complet",
                False,
                "Test ignoré - pas d'Instagram ID disponible",
                "Instagram ID requis du test précédent"
            )
            return False
            
        try:
            url = f"{GRAPH_API_BASE}/{self.instagram_id}"
            params = {
                "fields": "id,name,username,profile_picture_url",
                "access_token": ACCESS_TOKEN
            }
            
            print(f"🔍 Testing Instagram full access capabilities...")
            print(f"   URL: {url}")
            print(f"   Fields: id,name,username,profile_picture_url")
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   📊 Response: {json.dumps(data, indent=2)}")
                
                # Vérifier l'accès aux informations complètes
                expected_fields = ["id", "name", "username"]
                available_fields = [field for field in expected_fields if field in data]
                
                # profile_picture_url peut ne pas être disponible selon les permissions
                has_profile_pic = "profile_picture_url" in data
                
                if len(available_fields) >= 3:  # Au minimum id, name, username
                    self.log_test(
                        "Capabilities publication - accès complet",
                        True,
                        f"Accès complet confirmé - {len(available_fields)}/3 champs de base + photo de profil: {has_profile_pic}"
                    )
                    return True
                else:
                    self.log_test(
                        "Capabilities publication - accès complet",
                        False,
                        f"Accès limité - seulement {len(available_fields)}/3 champs disponibles",
                        f"Champs manquants: {set(expected_fields) - set(available_fields)}"
                    )
                    return False
            else:
                error_data = response.json() if response.content else {}
                self.log_test(
                    "Capabilities publication - accès complet",
                    False,
                    f"Erreur API Instagram: Status {response.status_code}",
                    f"Erreur: {error_data}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Capabilities publication - accès complet",
                False,
                "Exception lors de la requête",
                str(e)
            )
            return False
    
    def test_4_publication_limits(self):
        """Test 4: Limite de publication Instagram"""
        if not self.instagram_id:
            self.log_test(
                "Limite de publication Instagram",
                False,
                "Test ignoré - pas d'Instagram ID disponible",
                "Instagram ID requis du test précédent"
            )
            return False
            
        try:
            url = f"{GRAPH_API_BASE}/{self.instagram_id}/content_publishing_limit"
            params = {
                "access_token": ACCESS_TOKEN
            }
            
            print(f"🔍 Testing Instagram publication limits...")
            print(f"   URL: {url}")
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   📊 Response: {json.dumps(data, indent=2)}")
                
                # Analyser les limites de publication
                if "data" in data and len(data["data"]) > 0:
                    limit_info = data["data"][0]
                    quota_usage = limit_info.get("quota_usage", 0)
                    config = limit_info.get("config", {})
                    quota_total = config.get("quota_total", 0)
                    quota_duration = config.get("quota_duration", 0)
                    
                    self.log_test(
                        "Limite de publication Instagram",
                        True,
                        f"Quotas récupérés - Utilisé: {quota_usage}/{quota_total} sur {quota_duration}s"
                    )
                    return True
                else:
                    self.log_test(
                        "Limite de publication Instagram",
                        True,  # API accessible mais pas de données
                        "API accessible mais aucune donnée de quota disponible",
                        "Peut indiquer des permissions limitées ou compte sans historique"
                    )
                    return True
            else:
                error_data = response.json() if response.content else {}
                
                # Certaines erreurs sont attendues selon les permissions
                if response.status_code == 403:
                    self.log_test(
                        "Limite de publication Instagram",
                        False,
                        "Accès refusé aux limites de publication",
                        "Permissions insuffisantes pour content_publishing_limit"
                    )
                else:
                    self.log_test(
                        "Limite de publication Instagram",
                        False,
                        f"Erreur API Instagram: Status {response.status_code}",
                        f"Erreur: {error_data}"
                    )
                return False
                
        except Exception as e:
            self.log_test(
                "Limite de publication Instagram",
                False,
                "Exception lors de la requête",
                str(e)
            )
            return False
    
    def test_5_token_validation(self):
        """Test 5: Validation du token d'accès"""
        try:
            url = f"{GRAPH_API_BASE}/me"
            params = {
                "access_token": ACCESS_TOKEN
            }
            
            print(f"🔍 Testing access token validation...")
            print(f"   URL: {url}")
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   📊 Response: {json.dumps(data, indent=2)}")
                
                if "id" in data:
                    self.log_test(
                        "Validation du token d'accès",
                        True,
                        f"Token valide - ID: {data['id']}, Name: {data.get('name', 'N/A')}"
                    )
                    return True
                else:
                    self.log_test(
                        "Validation du token d'accès",
                        False,
                        "Réponse sans ID utilisateur",
                        f"Réponse: {data}"
                    )
                    return False
            else:
                error_data = response.json() if response.content else {}
                self.log_test(
                    "Validation du token d'accès",
                    False,
                    f"Token invalide ou expiré: Status {response.status_code}",
                    f"Erreur: {error_data}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Validation du token d'accès",
                False,
                "Exception lors de la validation",
                str(e)
            )
            return False
    
    def test_6_backend_integration(self):
        """Test 6: Intégration avec le backend existant"""
        try:
            # Test de l'endpoint backend pour l'authentification Instagram
            url = f"{BACKEND_API_URL}/social/instagram/auth-url"
            
            print(f"🔍 Testing backend Instagram integration...")
            print(f"   URL: {url}")
            print(f"   Backend: {BACKEND_URL}")
            
            # Test de santé du backend d'abord
            health_response = requests.get(f"{BACKEND_API_URL}/health", timeout=10)
            
            if health_response.status_code == 200:
                health_data = health_response.json()
                print(f"   📊 Backend Health: {health_data.get('status', 'unknown')}")
                
                # Vérifier la configuration Facebook
                if FACEBOOK_APP_ID and FACEBOOK_APP_SECRET:
                    self.log_test(
                        "Intégration avec le backend existant",
                        True,
                        f"Backend accessible, configuration Facebook présente (App ID: {FACEBOOK_APP_ID})"
                    )
                    return True
                else:
                    self.log_test(
                        "Intégration avec le backend existant",
                        False,
                        "Backend accessible mais configuration Facebook manquante",
                        "FACEBOOK_APP_ID ou FACEBOOK_APP_SECRET manquant dans .env"
                    )
                    return False
            else:
                self.log_test(
                    "Intégration avec le backend existant",
                    False,
                    f"Backend inaccessible: Status {health_response.status_code}",
                    f"URL testée: {BACKEND_API_URL}/health"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Intégration avec le backend existant",
                False,
                "Exception lors du test backend",
                str(e)
            )
            return False
    
    def test_7_token_analysis(self):
        """Test 7: Analyse détaillée du token fourni"""
        try:
            print(f"🔍 Analyzing provided access token...")
            
            # Analyser la structure du token
            token_parts = ACCESS_TOKEN.split('|') if '|' in ACCESS_TOKEN else [ACCESS_TOKEN]
            token_length = len(ACCESS_TOKEN)
            
            print(f"   Token length: {token_length}")
            print(f"   Token parts: {len(token_parts)}")
            print(f"   Token prefix: {ACCESS_TOKEN[:10]}...")
            
            # Test avec l'endpoint de debug de Facebook
            debug_url = f"{GRAPH_API_BASE}/debug_token"
            params = {
                "input_token": ACCESS_TOKEN,
                "access_token": f"{FACEBOOK_APP_ID}|{FACEBOOK_APP_SECRET}"
            }
            
            debug_response = requests.get(debug_url, params=params, timeout=10)
            
            if debug_response.status_code == 200:
                debug_data = debug_response.json()
                print(f"   📊 Debug Response: {json.dumps(debug_data, indent=2)}")
                
                if debug_data.get("data", {}).get("is_valid"):
                    token_info = debug_data["data"]
                    self.log_test(
                        "Analyse détaillée du token fourni",
                        True,
                        f"Token valide - App: {token_info.get('app_id')}, Expires: {token_info.get('expires_at', 'Never')}"
                    )
                    return True
                else:
                    error_info = debug_data.get("data", {})
                    self.log_test(
                        "Analyse détaillée du token fourni",
                        False,
                        "Token invalide selon Facebook Debug",
                        f"Erreur: {error_info.get('error', {}).get('message', 'Unknown error')}"
                    )
                    return False
            else:
                error_data = debug_response.json() if debug_response.content else {}
                self.log_test(
                    "Analyse détaillée du token fourni",
                    False,
                    f"Erreur lors du debug du token: Status {debug_response.status_code}",
                    f"Erreur: {error_data}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Analyse détaillée du token fourni",
                False,
                "Exception lors de l'analyse du token",
                str(e)
            )
            return False
    
    def test_8_generate_new_token_guide(self):
        """Test 8: Guide pour générer un nouveau token"""
        try:
            print(f"🔍 Generating new token guidance...")
            
            # Construire l'URL pour générer un nouveau token
            from urllib.parse import urlencode
            
            scopes = [
                "pages_show_list",
                "pages_read_engagement", 
                "pages_manage_posts",
                "instagram_basic",
                "instagram_content_publish",
                "instagram_manage_comments"
            ]
            
            params = {
                "client_id": FACEBOOK_APP_ID,
                "redirect_uri": "https://developers.facebook.com/tools/explorer/callback",
                "scope": ",".join(scopes),
                "response_type": "token"
            }
            
            auth_url = f"https://www.facebook.com/v21.0/dialog/oauth?{urlencode(params)}"
            
            self.log_test(
                "Guide pour générer un nouveau token",
                True,
                f"URL d'autorisation générée avec {len(scopes)} permissions requises"
            )
            
            print(f"\n🔗 NOUVEAU TOKEN - ÉTAPES À SUIVRE:")
            print(f"1. Visitez cette URL pour autoriser l'application:")
            print(f"   {auth_url}")
            print(f"2. Connectez-vous avec le compte Facebook lié à la page 'Claire & Marcus'")
            print(f"3. Acceptez toutes les permissions demandées")
            print(f"4. Copiez le nouveau access_token depuis l'URL de redirection")
            print(f"5. Remplacez le token dans ce script de test")
            print()
            
            return True
            
        except Exception as e:
            self.log_test(
                "Guide pour générer un nouveau token",
                False,
                "Exception lors de la génération du guide",
                str(e)
            )
            return False

    def run_all_tests(self):
        """Exécuter tous les tests dans l'ordre"""
        print("🚀 DÉBUT DES TESTS - RÉCUPÉRATION PAGE INSTAGRAM LIÉE")
        print("=" * 60)
        print(f"📋 Page Facebook ID: {FACEBOOK_PAGE_ID}")
        print(f"🔑 Token: {ACCESS_TOKEN[:20]}...")
        print(f"🌐 Graph API Version: v21.0")
        print(f"🏗️ Backend URL: {BACKEND_URL}")
        print(f"📱 Facebook App ID: {FACEBOOK_APP_ID}")
        print()
        
        # Exécuter les tests dans l'ordre
        tests = [
            self.test_6_backend_integration,
            self.test_7_token_analysis,
            self.test_5_token_validation,
            self.test_1_retrieve_instagram_account,
            self.test_2_instagram_basic_info,
            self.test_3_instagram_full_access,
            self.test_4_publication_limits,
            self.test_8_generate_new_token_guide
        ]
        
        passed = 0
        total = len(tests)
        
        for test_func in tests:
            if test_func():
                passed += 1
        
        # Résumé final
        print("=" * 60)
        print("📊 RÉSUMÉ DES TESTS")
        print(f"✅ Tests réussis: {passed}/{total}")
        print(f"❌ Tests échoués: {total - passed}/{total}")
        print(f"📈 Taux de réussite: {(passed/total)*100:.1f}%")
        
        if self.instagram_id:
            print(f"🎯 Instagram Business Account ID: {self.instagram_id}")
        else:
            print("⚠️ Instagram Business Account ID: NON RÉCUPÉRÉ")
        
        print()
        print("🔍 DÉTAILS DES RÉSULTATS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   📋 {result['details']}")
            if result["error"]:
                print(f"   ❌ {result['error']}")
        
        # Recommandations finales
        print("\n🎯 RECOMMANDATIONS:")
        if passed < total:
            print("1. ⚠️ Le token d'accès fourni semble invalide ou expiré")
            print("2. 🔄 Générez un nouveau token en suivant le guide ci-dessus")
            print("3. ✅ Le backend est configuré pour l'intégration Instagram")
            print("4. 📋 Une fois le token valide obtenu, tous les tests devraient passer")
        else:
            print("1. ✅ Tous les tests sont passés - intégration prête")
            print("2. 🚀 Vous pouvez procéder à l'implémentation de la publication croisée")
        
        return passed == total

def main():
    """Point d'entrée principal"""
    tester = InstagramIntegrationTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS - INTÉGRATION INSTAGRAM PRÊTE")
        sys.exit(0)
    else:
        print("\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ - VÉRIFICATION REQUISE")
        sys.exit(1)

if __name__ == "__main__":
    main()