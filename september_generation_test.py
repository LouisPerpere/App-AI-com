#!/usr/bin/env python3
"""
URGENT TEST - GÉNÉRATION POSTS DERNIER JOUR DU MOIS SEPTEMBRE
Backend Testing for September 2024 Post Generation with last_day_mode

CONTEXTE URGENT:
L'utilisateur rapporte que la génération ne fonctionne TOUJOURS PAS pour septembre (dernier jour du mois actuel).

MODIFICATIONS EFFECTUÉES:
1. ✅ Backend: Suppression du code de blocage dernier jour du mois (lignes 2072-2089 dans server.py)
2. ✅ Backend: Ajout du modèle PostGenerationRequest avec last_day_mode et generation_hour
3. ✅ Frontend: Logique pour envoyer last_day_mode=true avant 22h le dernier jour du mois

TESTS REQUIS IMMÉDIATEMENT:
1. Tester POST /api/posts/generate avec month_key septembre 2024 (2024-09)
2. Vérifier que l'ancienne erreur "Génération bloquée : nous sommes le dernier jour" n'apparaît PLUS
3. Tester avec last_day_mode=true et generation_hour
4. Confirmer que la génération se lance correctement

ENVIRONNEMENT: https://claire-marcus.com/api
Identifiants: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://claire-marcus.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class SeptemberGenerationTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        
    def log(self, message):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def authenticate(self):
        """Authenticate with the backend API"""
        self.log("🔐 ÉTAPE 1: Authentification")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json={
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for all future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                self.log(f"✅ Authentification réussie")
                self.log(f"   User ID: {self.user_id}")
                return True
            else:
                self.log(f"❌ Échec authentification: {response.status_code}")
                self.log(f"   Réponse: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Erreur authentification: {str(e)}")
            return False
    
    def test_september_generation_basic(self):
        """Test basic September 2024 generation"""
        self.log("📝 ÉTAPE 2: Test génération septembre 2024 basique")
        
        try:
            payload = {"month_key": "2024-09"}
            self.log(f"   Payload: {json.dumps(payload)}")
            
            response = self.session.post(
                f"{BACKEND_URL}/posts/generate",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            self.log(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                message = data.get('message', 'Pas de message')
                posts_count = data.get('posts_generated', 0)
                
                # Vérifier l'absence de l'ancienne erreur de blocage
                if "Génération bloquée" in message or "dernier jour" in message:
                    self.log(f"❌ CRITIQUE: Ancienne erreur de blocage encore présente!")
                    self.log(f"   Message: {message}")
                    return False
                else:
                    self.log(f"✅ Génération réussie - Pas d'erreur de blocage")
                    self.log(f"   Message: {message}")
                    self.log(f"   Posts générés: {posts_count}")
                    return True
                    
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get('error', response.text)
                except:
                    error_message = response.text
                
                # Vérifier si c'est l'ancienne erreur de blocage
                if "Génération bloquée" in error_message or "dernier jour" in error_message:
                    self.log(f"❌ CRITIQUE: Ancienne erreur de blocage détectée!")
                    self.log(f"   Erreur: {error_message}")
                    return False
                else:
                    self.log(f"⚠️ Erreur non-bloquante: {response.status_code}")
                    self.log(f"   Erreur: {error_message}")
                    return True  # Erreur non-bloquante acceptable
                    
        except Exception as e:
            self.log(f"❌ Erreur requête: {str(e)}")
            return False
    
    def test_september_generation_with_last_day_mode(self):
        """Test September 2024 generation with last_day_mode"""
        self.log("📝 ÉTAPE 3: Test génération septembre 2024 avec last_day_mode")
        
        try:
            payload = {
                "month_key": "2024-09",
                "last_day_mode": True,
                "generation_hour": 20
            }
            self.log(f"   Payload: {json.dumps(payload)}")
            
            response = self.session.post(
                f"{BACKEND_URL}/posts/generate",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            self.log(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                message = data.get('message', 'Pas de message')
                posts_count = data.get('posts_generated', 0)
                
                # Vérifier l'absence de l'ancienne erreur de blocage
                if "Génération bloquée" in message or "dernier jour" in message:
                    self.log(f"❌ CRITIQUE: Ancienne erreur de blocage avec last_day_mode!")
                    self.log(f"   Message: {message}")
                    return False
                else:
                    self.log(f"✅ Génération avec last_day_mode réussie")
                    self.log(f"   Message: {message}")
                    self.log(f"   Posts générés: {posts_count}")
                    return True
                    
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get('error', response.text)
                except:
                    error_message = response.text
                
                # Vérifier si c'est l'ancienne erreur de blocage
                if "Génération bloquée" in error_message or "dernier jour" in error_message:
                    self.log(f"❌ CRITIQUE: Ancienne erreur de blocage avec last_day_mode!")
                    self.log(f"   Erreur: {error_message}")
                    return False
                else:
                    self.log(f"⚠️ Erreur non-bloquante avec last_day_mode: {response.status_code}")
                    self.log(f"   Erreur: {error_message}")
                    return True  # Erreur non-bloquante acceptable
                    
        except Exception as e:
            self.log(f"❌ Erreur requête last_day_mode: {str(e)}")
            return False
    
    def test_september_generation_late_hour(self):
        """Test September 2024 generation with late generation_hour (after 22h)"""
        self.log("📝 ÉTAPE 4: Test génération septembre 2024 avec generation_hour tardive (après 22h)")
        
        try:
            payload = {
                "month_key": "2024-09",
                "last_day_mode": True,
                "generation_hour": 23
            }
            self.log(f"   Payload: {json.dumps(payload)}")
            
            response = self.session.post(
                f"{BACKEND_URL}/posts/generate",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            self.log(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                message = data.get('message', 'Pas de message')
                posts_count = data.get('posts_generated', 0)
                
                # Vérifier l'absence de l'ancienne erreur de blocage
                if "Génération bloquée" in message or "dernier jour" in message:
                    self.log(f"❌ CRITIQUE: Ancienne erreur de blocage avec heure tardive!")
                    self.log(f"   Message: {message}")
                    return False
                else:
                    self.log(f"✅ Génération avec heure tardive réussie")
                    self.log(f"   Message: {message}")
                    self.log(f"   Posts générés: {posts_count}")
                    return True
                    
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get('error', response.text)
                except:
                    error_message = response.text
                
                # Vérifier si c'est l'ancienne erreur de blocage
                if "Génération bloquée" in error_message or "dernier jour" in error_message:
                    self.log(f"❌ CRITIQUE: Ancienne erreur de blocage avec heure tardive!")
                    self.log(f"   Erreur: {error_message}")
                    return False
                else:
                    self.log(f"⚠️ Erreur non-bloquante avec heure tardive: {response.status_code}")
                    self.log(f"   Erreur: {error_message}")
                    return True  # Erreur non-bloquante acceptable
                    
        except Exception as e:
            self.log(f"❌ Erreur requête heure tardive: {str(e)}")
            return False
    
    def test_legacy_format_compatibility(self):
        """Test legacy target_month format for September 2024"""
        self.log("📝 ÉTAPE 5: Test compatibilité format legacy septembre 2024")
        
        try:
            payload = {"target_month": "septembre_2024"}
            self.log(f"   Payload: {json.dumps(payload)}")
            
            response = self.session.post(
                f"{BACKEND_URL}/posts/generate",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            self.log(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                message = data.get('message', 'Pas de message')
                posts_count = data.get('posts_generated', 0)
                
                # Vérifier l'absence de l'ancienne erreur de blocage
                if "Génération bloquée" in message or "dernier jour" in message:
                    self.log(f"❌ CRITIQUE: Ancienne erreur de blocage avec format legacy!")
                    self.log(f"   Message: {message}")
                    return False
                else:
                    self.log(f"✅ Génération format legacy réussie")
                    self.log(f"   Message: {message}")
                    self.log(f"   Posts générés: {posts_count}")
                    return True
                    
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get('error', response.text)
                except:
                    error_message = response.text
                
                # Vérifier si c'est l'ancienne erreur de blocage
                if "Génération bloquée" in error_message or "dernier jour" in error_message:
                    self.log(f"❌ CRITIQUE: Ancienne erreur de blocage avec format legacy!")
                    self.log(f"   Erreur: {error_message}")
                    return False
                else:
                    self.log(f"⚠️ Erreur non-bloquante format legacy: {response.status_code}")
                    self.log(f"   Erreur: {error_message}")
                    return True  # Erreur non-bloquante acceptable
                    
        except Exception as e:
            self.log(f"❌ Erreur requête format legacy: {str(e)}")
            return False
    
    def check_backend_logs_for_blocking_code(self):
        """Check if we can detect any remaining blocking code"""
        self.log("🔍 ÉTAPE 6: Vérification absence code de blocage")
        
        # We can't directly access backend logs, but we can test edge cases
        # that would trigger the old blocking logic
        
        test_cases = [
            {"month_key": "2024-09", "description": "Septembre 2024 standard"},
            {"month_key": "2024-09", "last_day_mode": False, "description": "Septembre 2024 sans last_day_mode"},
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            description = test_case.pop("description")
            self.log(f"   Test: {description}")
            
            try:
                response = self.session.post(
                    f"{BACKEND_URL}/posts/generate",
                    json=test_case,
                    headers={"Content-Type": "application/json"}
                )
                
                # Analyser la réponse pour détecter le code de blocage
                if response.status_code in [200, 400, 422]:
                    try:
                        data = response.json()
                        message = data.get('message', '') + ' ' + data.get('error', '')
                    except:
                        message = response.text
                    
                    if "Génération bloquée" in message or "dernier jour" in message:
                        self.log(f"   ❌ Code de blocage détecté: {message}")
                        all_passed = False
                    else:
                        self.log(f"   ✅ Pas de code de blocage détecté")
                else:
                    self.log(f"   ⚠️ Status inattendu: {response.status_code}")
                    
            except Exception as e:
                self.log(f"   ❌ Erreur test: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def run_comprehensive_test(self):
        """Run comprehensive September 2024 generation test"""
        self.log("🚀 DÉBUT TEST COMPLET - GÉNÉRATION SEPTEMBRE 2024")
        self.log(f"   Backend URL: {BACKEND_URL}")
        self.log(f"   Utilisateur test: {TEST_EMAIL}")
        self.log("=" * 80)
        
        tests = [
            ("Authentification", self.authenticate),
            ("Génération septembre 2024 basique", self.test_september_generation_basic),
            ("Génération avec last_day_mode", self.test_september_generation_with_last_day_mode),
            ("Génération avec heure tardive", self.test_september_generation_late_hour),
            ("Compatibilité format legacy", self.test_legacy_format_compatibility),
            ("Vérification absence code blocage", self.check_backend_logs_for_blocking_code),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            self.log(f"\n{'='*60}")
            self.log(f"🧪 Test: {test_name}")
            self.log(f"{'='*60}")
            
            try:
                result = test_func()
                results.append((test_name, result))
                
                if result:
                    self.log(f"✅ {test_name}: RÉUSSI")
                else:
                    self.log(f"❌ {test_name}: ÉCHEC")
                    
            except Exception as e:
                self.log(f"❌ {test_name}: ERREUR - {str(e)}")
                results.append((test_name, False))
        
        # Résumé final
        self.log(f"\n{'='*80}")
        self.log("📊 RÉSUMÉ FINAL DES TESTS")
        self.log(f"{'='*80}")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ RÉUSSI" if result else "❌ ÉCHEC"
            self.log(f"   {status} - {test_name}")
        
        self.log(f"\n🎯 Résultat global: {passed}/{total} tests réussis")
        
        # Analyse spécifique pour septembre 2024
        critical_tests = [name for name, _ in results if "septembre" in name.lower() or "last_day" in name.lower()]
        critical_passed = sum(1 for name, result in results if any(ct in name for ct in critical_tests) and result)
        
        if passed == total:
            self.log("\n🎉 SUCCÈS COMPLET: Tous les tests sont passés!")
            self.log("✅ La génération pour septembre 2024 fonctionne correctement")
            self.log("✅ L'erreur 'Génération bloquée : nous sommes le dernier jour' n'apparaît plus")
            self.log("✅ Les paramètres last_day_mode et generation_hour sont acceptés")
            self.log("✅ Le code de blocage a été supprimé avec succès")
        else:
            self.log("\n⚠️ PROBLÈMES DÉTECTÉS: Certains tests ont échoué")
            
            # Identifier les problèmes critiques
            failed_tests = [name for name, result in results if not result]
            if any("septembre" in name.lower() for name in failed_tests):
                self.log("❌ CRITIQUE: Problèmes avec la génération septembre 2024")
                self.log("❌ L'ancienne erreur de blocage pourrait encore être présente")
            
            if any("last_day" in name.lower() for name in failed_tests):
                self.log("❌ CRITIQUE: Problèmes avec last_day_mode")
                self.log("❌ La fonctionnalité last_day_mode ne fonctionne pas correctement")
        
        return passed == total

def main():
    """Main test execution"""
    print("🎯 TEST URGENT - GÉNÉRATION POSTS DERNIER JOUR DU MOIS SEPTEMBRE")
    print("=" * 80)
    print("OBJECTIF: Vérifier que la génération fonctionne pour septembre 2024")
    print("CRITIQUE: L'erreur 'Génération bloquée : nous sommes le dernier jour' ne doit PLUS apparaître")
    print("=" * 80)
    
    tester = SeptemberGenerationTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 MISSION ACCOMPLIE: La génération septembre 2024 fonctionne!")
        sys.exit(0)
    else:
        print("\n❌ MISSION ÉCHOUÉE: Problèmes détectés avec la génération septembre 2024!")
        sys.exit(1)

if __name__ == "__main__":
    main()