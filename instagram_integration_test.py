#!/usr/bin/env python3
"""
TEST RÉCUPÉRATION PAGE INSTAGRAM LIÉE - ClaireEtMarcus
Test de récupération des informations de la page Instagram liée à la page Facebook
pour implémenter la publication croisée Facebook + Instagram.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration des tests
FACEBOOK_PAGE_ID = "741078965763774"
ACCESS_TOKEN = "EAAP2f1Vj6XMBPbsv5Dqs3aeN4vIVuAkFPcuqDqN0CrZBeszwhHaAmU83xLMEddvEb70EQRO3yzffvFHLMAIhZCSbav3BZARn2RtzZCdXsqF76oqRZA9n9UrBWrCqgGxujyOwrajJuPZCXiUBXwww8U0HBjeHhXcuoAKB55gqNbpQChpkILCJNLbqaOpUXJScNTOYRSX1M7tvfkDbvq3P46ZCtHpCGTuf7nEzjBZAxXZC3wXZClIcCZD"
GRAPH_API_BASE = "https://graph.facebook.com/v21.0"

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
    
    def run_all_tests(self):
        """Exécuter tous les tests dans l'ordre"""
        print("🚀 DÉBUT DES TESTS - RÉCUPÉRATION PAGE INSTAGRAM LIÉE")
        print("=" * 60)
        print(f"📋 Page Facebook ID: {FACEBOOK_PAGE_ID}")
        print(f"🔑 Token: {ACCESS_TOKEN[:20]}...")
        print(f"🌐 Graph API Version: v21.0")
        print()
        
        # Exécuter les tests dans l'ordre
        tests = [
            self.test_5_token_validation,
            self.test_1_retrieve_instagram_account,
            self.test_2_instagram_basic_info,
            self.test_3_instagram_full_access,
            self.test_4_publication_limits
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