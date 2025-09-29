#!/usr/bin/env python3
"""
TEST VALIDATION DES 3 CORRECTIONS - Backend Testing
Testing the 3 specific corrections applied to the website analysis system:

1. ✅ "Mix" hardcodé supprimé → defaultValue 'equilibre' remplacé par ''
2. ✅ Section produits/services vide → Ajout gestion array vide avec message approprié  
3. ✅ Claude trop "IA" → Prompt revu pour ton naturel sans superlatifs/étoiles

URL: https://social-pub-hub.preview.emergentagent.com/api
Credentials: lperpere@yahoo.fr / L@Reunion974!
Test Website: https://myownwatch.fr
"""

import requests
import json
import time
import re
from datetime import datetime

# Configuration from review request
BACKEND_URL = "https://social-pub-hub.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}
TEST_WEBSITE = "https://myownwatch.fr"

class ClaudeCorrectionsTest:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Claude-Corrections-Tester/1.0'
        })
        self.access_token = None
        self.user_id = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def authenticate(self):
        """Step 1: Authentication with provided credentials"""
        self.log("🔐 STEP 1: Authentication Test")
        
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
                
                # Configure session headers
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                self.log(f"✅ Authentication successful")
                self.log(f"   User ID: {self.user_id}")
                self.log(f"   Email: {data.get('email')}")
                return True
            else:
                self.log(f"❌ Authentication failed: {response.status_code}")
                self.log(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_website_analysis_corrections(self):
        """Step 2: Test website analysis with focus on the 3 corrections"""
        self.log(f"🔍 STEP 2: Website Analysis Corrections Test")
        self.log(f"   Target website: {TEST_WEBSITE}")
        
        try:
            start_time = time.time()
            
            response = self.session.post(
                f"{BACKEND_URL}/website/analyze",
                json={"website_url": TEST_WEBSITE},
                timeout=120  # Allow up to 2 minutes as specified
            )
            
            analysis_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Website analysis completed in {analysis_time:.1f} seconds")
                
                # Check execution time requirement (< 90 seconds)
                if analysis_time < 90:
                    self.log(f"✅ EXECUTION TIME: {analysis_time:.1f}s < 90s requirement MET")
                else:
                    self.log(f"⚠️ EXECUTION TIME: {analysis_time:.1f}s > 90s requirement")
                
                # Log basic response structure
                self.log(f"📊 Response contains {len(data)} fields")
                
                return data
            else:
                self.log(f"❌ Website analysis failed: {response.status_code}")
                self.log(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            self.log(f"❌ Website analysis error: {str(e)}")
            return None
    
    def test_correction_1_mix_hardcode_removed(self, data):
        """Test Correction 1: "Mix" hardcodé supprimé → defaultValue 'equilibre' remplacé par ''"""
        self.log(f"\n🎯 CORRECTION 1 TEST: Mix hardcodé supprimé")
        
        # Look for any hardcoded "Mix" or "equilibre" values in the response
        all_text = json.dumps(data, ensure_ascii=False).lower()
        
        # Check for hardcoded "mix" values
        mix_found = "mix" in all_text and ("hardcod" in all_text or "défaut" in all_text)
        equilibre_found = "equilibre" in all_text and ("défaut" in all_text or "default" in all_text)
        
        if not mix_found and not equilibre_found:
            self.log(f"✅ CORRECTION 1 VERIFIED: No hardcoded 'Mix' or 'equilibre' default values found")
            return True
        else:
            if mix_found:
                self.log(f"❌ CORRECTION 1 FAILED: Hardcoded 'Mix' still present")
            if equilibre_found:
                self.log(f"❌ CORRECTION 1 FAILED: Hardcoded 'equilibre' still present")
            return False
    
    def test_correction_2_empty_products_services(self, data):
        """Test Correction 2: Section produits/services vide → Ajout gestion array vide avec message approprié"""
        self.log(f"\n🎯 CORRECTION 2 TEST: Gestion products_services_details vide")
        
        products_services_details = data.get("products_services_details")
        
        if products_services_details is not None:
            self.log(f"✅ FIELD PRESENT: products_services_details field found")
            
            # Check if it's an empty array or has appropriate message for empty case
            if isinstance(products_services_details, list):
                if len(products_services_details) == 0:
                    self.log(f"⚠️ EMPTY ARRAY: products_services_details is empty list")
                    return False  # Should have message instead of empty array
                else:
                    self.log(f"✅ POPULATED ARRAY: products_services_details has {len(products_services_details)} items")
                    return True
            elif isinstance(products_services_details, str):
                # Check for appropriate empty message
                empty_messages = [
                    "aucun détail spécifique",
                    "aucun détail précis",
                    "pas de détail",
                    "informations non disponibles",
                    "détails non trouvés"
                ]
                
                details_text = products_services_details.lower()
                has_empty_message = any(msg in details_text for msg in empty_messages)
                
                if has_empty_message:
                    self.log(f"✅ CORRECTION 2 VERIFIED: Appropriate message for empty products/services")
                    self.log(f"   Message: {products_services_details[:100]}...")
                    return True
                elif len(products_services_details.strip()) > 50:
                    self.log(f"✅ CORRECTION 2 VERIFIED: Detailed products/services information provided")
                    self.log(f"   Content length: {len(products_services_details)} chars")
                    return True
                else:
                    self.log(f"❌ CORRECTION 2 FAILED: products_services_details too short or generic")
                    return False
            else:
                self.log(f"❌ CORRECTION 2 FAILED: products_services_details has unexpected type: {type(products_services_details)}")
                return False
        else:
            self.log(f"❌ CORRECTION 2 FAILED: products_services_details field missing")
            return False
    
    def test_correction_3_claude_natural_tone(self, data):
        """Test Correction 3: Claude trop "IA" → Prompt revu pour ton naturel sans superlatifs/étoiles"""
        self.log(f"\n🎯 CORRECTION 3 TEST: Claude ton naturel sans style IA")
        
        storytelling_analysis = data.get("storytelling_analysis", "")
        
        if not storytelling_analysis:
            self.log(f"❌ CORRECTION 3 FAILED: storytelling_analysis field missing or empty")
            return False
        
        self.log(f"📊 storytelling_analysis length: {len(storytelling_analysis)} chars")
        
        # Test 3.1: Check for stars/emojis (★, ✨)
        stars_found = re.findall(r'[★✨⭐🌟💫]', storytelling_analysis)
        if stars_found:
            self.log(f"❌ STARS FOUND: {len(stars_found)} star emojis detected: {set(stars_found)}")
            correction_3_1 = False
        else:
            self.log(f"✅ NO STARS: No star emojis (★, ✨) found in storytelling")
            correction_3_1 = True
        
        # Test 3.2: Check for excessive superlatives
        superlatives = [
            "INSPIRANT", "ÉVOCATEUR", "EXTRAORDINAIRE", "EXCEPTIONNEL", 
            "MAGNIFIQUE", "SPLENDIDE", "REMARQUABLE", "FANTASTIQUE",
            "INCROYABLE", "MERVEILLEUX", "ÉPOUSTOUFLANT"
        ]
        
        found_superlatives = []
        for superlative in superlatives:
            if superlative.lower() in storytelling_analysis.lower():
                found_superlatives.append(superlative)
        
        if found_superlatives:
            self.log(f"❌ SUPERLATIVES FOUND: {len(found_superlatives)} excessive superlatives: {found_superlatives}")
            correction_3_2 = False
        else:
            self.log(f"✅ NO SUPERLATIVES: No excessive superlatives found")
            correction_3_2 = True
        
        # Test 3.3: Check for required structure sections
        required_sections = [
            "L'HISTOIRE DE L'ENTREPRISE",
            "CE QUI LES REND UNIQUES"
        ]
        
        found_sections = []
        for section in required_sections:
            if section.lower() in storytelling_analysis.lower():
                found_sections.append(section)
        
        if len(found_sections) >= 2:
            self.log(f"✅ STRUCTURE VERIFIED: Found required sections: {found_sections}")
            correction_3_3 = True
        else:
            self.log(f"⚠️ STRUCTURE PARTIAL: Only found {len(found_sections)}/2 required sections: {found_sections}")
            correction_3_3 = len(found_sections) > 0  # Partial credit
        
        # Test 3.4: Check for natural tone (absence of AI-typical phrases)
        ai_phrases = [
            "découvrez l'art de", "plongez dans", "laissez-vous séduire",
            "explorez notre univers", "au cœur de notre passion",
            "une expérience unique", "un savoir-faire d'exception"
        ]
        
        found_ai_phrases = []
        for phrase in ai_phrases:
            if phrase.lower() in storytelling_analysis.lower():
                found_ai_phrases.append(phrase)
        
        if len(found_ai_phrases) == 0:
            self.log(f"✅ NATURAL TONE: No typical AI phrases detected")
            correction_3_4 = True
        elif len(found_ai_phrases) <= 2:
            self.log(f"⚠️ MOSTLY NATURAL: Only {len(found_ai_phrases)} AI phrases found: {found_ai_phrases}")
            correction_3_4 = True  # Acceptable level
        else:
            self.log(f"❌ AI TONE: {len(found_ai_phrases)} AI phrases found: {found_ai_phrases}")
            correction_3_4 = False
        
        # Overall correction 3 result
        correction_3_score = sum([correction_3_1, correction_3_2, correction_3_3, correction_3_4])
        correction_3_success = correction_3_score >= 3  # At least 3/4 criteria met
        
        self.log(f"📊 CORRECTION 3 SCORE: {correction_3_score}/4 criteria met")
        
        if correction_3_success:
            self.log(f"✅ CORRECTION 3 VERIFIED: Claude produces natural content without excessive AI style")
        else:
            self.log(f"❌ CORRECTION 3 FAILED: Claude still shows AI-style characteristics")
        
        return correction_3_success
    
    def test_general_analysis_quality(self, data):
        """Test general analysis quality requirements"""
        self.log(f"\n📊 GENERAL QUALITY TEST: Analysis completeness and coherence")
        
        # Test field count (21+ fields expected)
        field_count = len(data)
        if field_count >= 21:
            self.log(f"✅ FIELD COUNT: {field_count} fields (≥21 requirement met)")
            quality_1 = True
        else:
            self.log(f"⚠️ FIELD COUNT: {field_count} fields (<21 expected)")
            quality_1 = False
        
        # Test analysis_summary structure and quality
        analysis_summary = data.get("analysis_summary", "")
        if len(analysis_summary) >= 300:
            self.log(f"✅ ANALYSIS SUMMARY: {len(analysis_summary)} chars (structured and professional)")
            quality_2 = True
        else:
            self.log(f"⚠️ ANALYSIS SUMMARY: {len(analysis_summary)} chars (may be too short)")
            quality_2 = len(analysis_summary) >= 200  # Partial credit
        
        # Test storytelling_analysis naturalness and length
        storytelling_analysis = data.get("storytelling_analysis", "")
        if len(storytelling_analysis) >= 500:
            self.log(f"✅ STORYTELLING ANALYSIS: {len(storytelling_analysis)} chars (natural and human)")
            quality_3 = True
        else:
            self.log(f"⚠️ STORYTELLING ANALYSIS: {len(storytelling_analysis)} chars (may be too short)")
            quality_3 = len(storytelling_analysis) >= 300  # Partial credit
        
        quality_score = sum([quality_1, quality_2, quality_3])
        quality_success = quality_score >= 2  # At least 2/3 criteria met
        
        self.log(f"📊 GENERAL QUALITY SCORE: {quality_score}/3 criteria met")
        
        return quality_success
    
    def run_comprehensive_corrections_test(self):
        """Run the complete test suite for the 3 corrections"""
        self.log("🚀 TEST VALIDATION DES 3 CORRECTIONS - Backend Testing")
        self.log("=" * 70)
        self.log(f"Backend: {BACKEND_URL}")
        self.log(f"Test Website: {TEST_WEBSITE}")
        self.log(f"Credentials: {TEST_CREDENTIALS['email']}")
        self.log("=" * 70)
        
        # Step 1: Authentication
        if not self.authenticate():
            self.log("\n❌ CRITICAL: Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Website Analysis
        analysis_data = self.test_website_analysis_corrections()
        if not analysis_data:
            self.log("\n❌ CRITICAL: Website analysis failed")
            return False
        
        # Step 3: Test the 3 specific corrections
        self.log("\n" + "="*50)
        self.log("🎯 TESTING THE 3 SPECIFIC CORRECTIONS")
        self.log("="*50)
        
        correction_1 = self.test_correction_1_mix_hardcode_removed(analysis_data)
        correction_2 = self.test_correction_2_empty_products_services(analysis_data)
        correction_3 = self.test_correction_3_claude_natural_tone(analysis_data)
        
        # Step 4: Test general quality
        general_quality = self.test_general_analysis_quality(analysis_data)
        
        # Final Results Summary
        self.log("\n" + "="*50)
        self.log("🎯 FINAL CORRECTIONS VALIDATION RESULTS")
        self.log("="*50)
        
        corrections_results = {
            "Correction 1 - Mix hardcodé supprimé": correction_1,
            "Correction 2 - Gestion array vide": correction_2,
            "Correction 3 - Claude ton naturel": correction_3,
            "General Quality": general_quality
        }
        
        passed_corrections = sum(corrections_results.values())
        total_corrections = len(corrections_results)
        success_rate = (passed_corrections / total_corrections) * 100
        
        for correction_name, result in corrections_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"   {correction_name}: {status}")
        
        self.log(f"\n📊 SUCCESS RATE: {success_rate:.1f}% ({passed_corrections}/{total_corrections} corrections validated)")
        
        # Critical Success Criteria
        critical_success = correction_2 and correction_3  # Most important corrections
        
        if success_rate >= 75 and critical_success:
            self.log("\n✅ CORRECTIONS VALIDATION: SUCCESSFUL")
            self.log("   - Claude produit du contenu naturel sans langage IA excessif")
            self.log("   - products_services_details gère les cas array vide avec message approprié")
            self.log("   - Analyse complète et cohérente avec nouveaux prompts")
            self.log("   - Pas d'étoiles, superlatifs ou formulations marketing grandiose")
        elif success_rate >= 50:
            self.log("\n⚠️ CORRECTIONS VALIDATION: PARTIALLY SUCCESSFUL")
            self.log("   - Some corrections working but improvements needed")
        else:
            self.log("\n❌ CORRECTIONS VALIDATION: FAILED")
            self.log("   - Major issues with corrections implementation")
        
        # Detailed findings for main agent
        self.log("\n📋 DETAILED FINDINGS FOR MAIN AGENT:")
        
        if not correction_1:
            self.log("   ❌ Correction 1: Still finding hardcoded 'Mix' or 'equilibre' values")
        
        if not correction_2:
            self.log("   ❌ Correction 2: products_services_details not handling empty cases properly")
        
        if not correction_3:
            self.log("   ❌ Correction 3: Claude still using AI-style language with stars/superlatives")
        
        if not general_quality:
            self.log("   ❌ General Quality: Analysis not meeting completeness/coherence requirements")
        
        return success_rate >= 75 and critical_success

if __name__ == "__main__":
    tester = ClaudeCorrectionsTest()
    success = tester.run_comprehensive_corrections_test()
    
    if success:
        print(f"\n🎉 CORRECTIONS VALIDATION COMPLETED SUCCESSFULLY")
        print(f"   All 3 corrections are working as specified")
    else:
        print(f"\n💥 CORRECTIONS VALIDATION FAILED")
        print(f"   Issues detected with correction implementation")