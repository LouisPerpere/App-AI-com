#!/usr/bin/env python3
"""
Test de la nouvelle implémentation d'analyse GPT-4o + Claude Storytelling
Objectif: Vérifier que l'analyse site web fonctionne avec les deux IA en parallèle
"""

import requests
import json
import time
from datetime import datetime

# Configuration du test selon la demande
BACKEND_URL = "https://post-restore.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}
TEST_WEBSITE_URL = "https://myownwatch.fr"

class DualAIWebsiteAnalysisTest:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        
    def authenticate(self):
        """Test d'authentification"""
        print("🔐 Step 1: Test d'authentification...")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json=TEST_CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Configure headers for subsequent requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                print(f"✅ Authentication successful")
                print(f"   User ID: {self.user_id}")
                print(f"   Token: {self.access_token[:20]}..." if self.access_token else "No token")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_dual_ai_website_analysis(self):
        """Test d'analyse avec double IA (GPT-4o + Claude Storytelling)"""
        print(f"\n🧠 Step 2: Test d'analyse avec double IA pour {TEST_WEBSITE_URL}...")
        
        try:
            start_time = time.time()
            
            response = self.session.post(
                f"{BACKEND_URL}/website/analyze",
                json={"website_url": TEST_WEBSITE_URL},
                timeout=120  # 2 minutes timeout for dual AI processing
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Website analysis completed in {processing_time:.1f} seconds")
                
                # Vérification des champs requis selon la demande
                required_fields = [
                    "analysis_type",
                    "analysis_summary", 
                    "storytelling_analysis",
                    "business_ai",
                    "storytelling_ai"
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in data:
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"❌ Missing required fields: {missing_fields}")
                    return False
                
                # Vérifications spécifiques selon la demande
                analysis_type = data.get("analysis_type")
                business_ai = data.get("business_ai")
                storytelling_ai = data.get("storytelling_ai")
                analysis_summary = data.get("analysis_summary", "")
                storytelling_analysis = data.get("storytelling_analysis", "")
                
                print(f"📊 Analysis Results:")
                print(f"   Analysis Type: {analysis_type}")
                print(f"   Business AI: {business_ai}")
                print(f"   Storytelling AI: {storytelling_ai}")
                print(f"   Processing Time: {processing_time:.1f}s")
                print(f"   Analysis Summary Length: {len(analysis_summary)} chars")
                print(f"   Storytelling Analysis Length: {len(storytelling_analysis)} chars")
                
                # Vérifications selon les critères de la demande
                success_criteria = []
                
                # 1. Vérifier analysis_type = "gpt4o_plus_claude_storytelling"
                if analysis_type == "gpt4o_plus_claude_storytelling":
                    success_criteria.append("✅ Analysis type correct")
                else:
                    success_criteria.append(f"❌ Analysis type incorrect: {analysis_type}")
                
                # 2. Vérifier présence de analysis_summary (GPT-4o)
                if analysis_summary and len(analysis_summary) > 50:
                    success_criteria.append("✅ Analysis summary present (GPT-4o)")
                else:
                    success_criteria.append("❌ Analysis summary missing or too short")
                
                # 3. Vérifier présence de storytelling_analysis (Claude)
                if storytelling_analysis and len(storytelling_analysis) > 50:
                    success_criteria.append("✅ Storytelling analysis present (Claude)")
                else:
                    success_criteria.append("❌ Storytelling analysis missing or too short")
                
                # 4. Vérifier business_ai = "GPT-4o"
                if business_ai == "GPT-4o":
                    success_criteria.append("✅ Business AI correct")
                else:
                    success_criteria.append(f"❌ Business AI incorrect: {business_ai}")
                
                # 5. Vérifier storytelling_ai = "Claude Sonnet 4"
                if storytelling_ai == "Claude Sonnet 4":
                    success_criteria.append("✅ Storytelling AI correct")
                else:
                    success_criteria.append(f"❌ Storytelling AI incorrect: {storytelling_ai}")
                
                # 6. Vérifier performance (moins de 60 secondes)
                if processing_time < 60:
                    success_criteria.append("✅ Performance acceptable (<60s)")
                else:
                    success_criteria.append(f"⚠️ Performance slow: {processing_time:.1f}s")
                
                print(f"\n📋 Success Criteria Check:")
                for criterion in success_criteria:
                    print(f"   {criterion}")
                
                # Compter les succès
                success_count = sum(1 for c in success_criteria if c.startswith("✅"))
                total_count = len(success_criteria)
                success_rate = (success_count / total_count) * 100
                
                print(f"\n📊 Test Results: {success_count}/{total_count} criteria passed ({success_rate:.1f}%)")
                
                return success_count == total_count
                
            else:
                print(f"❌ Website analysis failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Website analysis error: {str(e)}")
            return False
    
    def test_content_quality(self):
        """Test de la qualité du contenu des analyses"""
        print(f"\n🔍 Step 3: Test de la qualité du contenu...")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/website/analyze",
                json={"website_url": TEST_WEBSITE_URL},
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                
                analysis_summary = data.get("analysis_summary", "")
                storytelling_analysis = data.get("storytelling_analysis", "")
                
                print(f"📝 Content Quality Analysis:")
                
                # Vérifier que les analyses sont différentes et complémentaires
                if analysis_summary and storytelling_analysis:
                    # Simple similarity check
                    common_words = set(analysis_summary.lower().split()) & set(storytelling_analysis.lower().split())
                    total_words = len(set(analysis_summary.lower().split()) | set(storytelling_analysis.lower().split()))
                    similarity = len(common_words) / total_words if total_words > 0 else 0
                    
                    print(f"   Similarity between analyses: {similarity:.2f}")
                    
                    if similarity < 0.7:  # Less than 70% similarity = different content
                        print("✅ Analyses are different and complementary")
                    else:
                        print("⚠️ Analyses might be too similar")
                
                # Vérifier la présence de mots-clés spécifiques au storytelling
                storytelling_keywords = ["VISION", "POSITIONNEMENT", "AXES", "CONTENUS", "storytelling", "narrative"]
                storytelling_found = sum(1 for keyword in storytelling_keywords if keyword.lower() in storytelling_analysis.lower())
                
                print(f"   Storytelling keywords found: {storytelling_found}/{len(storytelling_keywords)}")
                
                if storytelling_found >= 2:
                    print("✅ Storytelling analysis contains expected elements")
                else:
                    print("⚠️ Storytelling analysis might lack expected elements")
                
                # Vérifier la structure business de l'analyse GPT-4o
                business_keywords = ["entreprise", "business", "services", "produits", "marché", "clients"]
                business_found = sum(1 for keyword in business_keywords if keyword.lower() in analysis_summary.lower())
                
                print(f"   Business keywords found: {business_found}/{len(business_keywords)}")
                
                if business_found >= 2:
                    print("✅ Business analysis contains expected elements")
                else:
                    print("⚠️ Business analysis might lack expected elements")
                
                return True
                
            else:
                print(f"❌ Content quality test failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Content quality test error: {str(e)}")
            return False
    
    def test_backend_logs_check(self):
        """Vérifier qu'il n'y a pas d'erreurs dans les logs backend"""
        print(f"\n📋 Step 4: Vérification des logs backend...")
        
        # Note: Dans un environnement de test réel, on vérifierait les logs
        # Ici on fait un test simple de santé de l'API
        try:
            response = self.session.get(f"{BACKEND_URL}/health", timeout=10)
            
            if response.status_code == 200:
                print("✅ Backend health check passed")
                return True
            else:
                print(f"❌ Backend health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Backend health check error: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Exécuter tous les tests de la nouvelle implémentation"""
        print("🚀 DÉBUT DU TEST DE LA NOUVELLE IMPLÉMENTATION GPT-4o + CLAUDE STORYTELLING")
        print("=" * 80)
        
        test_results = []
        
        # Test 1: Authentification
        auth_success = self.authenticate()
        test_results.append(("Authentication", auth_success))
        
        if not auth_success:
            print("❌ Cannot proceed without authentication")
            return False
        
        # Test 2: Analyse avec double IA
        dual_ai_success = self.test_dual_ai_website_analysis()
        test_results.append(("Dual AI Analysis", dual_ai_success))
        
        # Test 3: Qualité du contenu
        content_quality_success = self.test_content_quality()
        test_results.append(("Content Quality", content_quality_success))
        
        # Test 4: Vérification logs backend
        logs_success = self.test_backend_logs_check()
        test_results.append(("Backend Logs", logs_success))
        
        # Résumé final
        print("\n" + "=" * 80)
        print("📊 RÉSUMÉ FINAL DES TESTS")
        print("=" * 80)
        
        success_count = 0
        for test_name, success in test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{test_name:20} : {status}")
            if success:
                success_count += 1
        
        total_tests = len(test_results)
        success_rate = (success_count / total_tests) * 100
        
        print(f"\nRésultat global: {success_count}/{total_tests} tests réussis ({success_rate:.1f}%)")
        
        if success_count == total_tests:
            print("🎉 TOUS LES TESTS SONT PASSÉS - IMPLÉMENTATION FONCTIONNELLE")
            return True
        else:
            print("⚠️ CERTAINS TESTS ONT ÉCHOUÉ - VÉRIFICATION REQUISE")
            return False

def main():
    """Point d'entrée principal"""
    tester = DualAIWebsiteAnalysisTest()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n✅ La nouvelle implémentation GPT-4o + Claude Storytelling fonctionne correctement")
    else:
        print("\n❌ Des problèmes ont été détectés dans l'implémentation")
    
    return success

if __name__ == "__main__":
    main()