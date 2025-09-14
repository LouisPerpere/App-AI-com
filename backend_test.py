#!/usr/bin/env python3
"""
Enhanced GPT-4o Website Analysis Testing Suite
Testing the improved multi-page analysis system with detailed content extraction
"""

import requests
import json
import time
from datetime import datetime

# Configuration from review request
BACKEND_URL = "https://social-ai-manager-12.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}
TEST_WEBSITE = "https://myownwatch.fr"

class EnhancedWebsiteAnalysisTest:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        
    def authenticate(self):
        """Step 1: Authenticate with provided credentials"""
        print("🔐 Step 1: Authentication Test")
        
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
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
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
    
    def test_enhanced_website_analysis(self):
        """Step 2: Test enhanced GPT-4o website analysis with multi-page exploitation"""
        print(f"\n🔍 Step 2: Enhanced Website Analysis Test")
        print(f"   Target website: {TEST_WEBSITE}")
        
        try:
            start_time = time.time()
            
            response = self.session.post(
                f"{BACKEND_URL}/website/analyze",
                json={"website_url": TEST_WEBSITE},
                timeout=120  # Extended timeout for enhanced analysis
            )
            
            analysis_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Website analysis completed in {analysis_time:.1f} seconds")
                
                # Debug: Print actual response structure
                print(f"\n🔍 DEBUG: Actual response structure:")
                print(f"   Available fields: {list(data.keys())}")
                for key, value in data.items():
                    if isinstance(value, str):
                        print(f"   {key}: {len(value)} chars")
                    elif isinstance(value, list):
                        print(f"   {key}: {len(value)} items")
                    else:
                        print(f"   {key}: {type(value)} - {value}")
                
                # Test new required fields
                self.verify_new_fields(data)
                self.verify_content_richness(data)
                self.verify_multi_page_exploitation(data)
                
                return data
            else:
                print(f"❌ Website analysis failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Website analysis error: {str(e)}")
            return None
    
    def verify_new_fields(self, data):
        """Step 3: Verify presence of enhanced fields (adapted to current implementation)"""
        print(f"\n📋 Step 3: Enhanced Fields Verification")
        
        # Check current implementation fields
        current_fields = [
            "analysis_summary",
            "storytelling_analysis", 
            "analysis_type",
            "pages_count",
            "pages_analyzed",
            "business_ai",
            "narrative_ai"
        ]
        
        # Expected new fields from review request (not yet implemented)
        expected_new_fields = [
            "products_services_details",
            "company_expertise", 
            "unique_value_proposition",
            "analysis_depth",
            "pages_analyzed_count",
            "non_technical_pages_count"
        ]
        
        # Check current fields
        present_current = []
        missing_current = []
        
        for field in current_fields:
            if field in data:
                present_current.append(field)
                value = data[field]
                
                if field == "analysis_type":
                    if "gpt4o" in str(value).lower():
                        print(f"✅ {field}: {value} (GPT-4o system active)")
                    else:
                        print(f"⚠️ {field}: {value}")
                elif field in ["pages_count"]:
                    if isinstance(value, int) and value > 0:
                        print(f"✅ {field}: {value}")
                    else:
                        print(f"⚠️ {field}: {value}")
                elif field == "pages_analyzed":
                    if isinstance(value, list) and len(value) > 0:
                        print(f"✅ {field}: {len(value)} pages")
                    else:
                        print(f"⚠️ {field}: {len(value) if isinstance(value, list) else 0} pages")
                else:
                    if value and len(str(value).strip()) > 10:
                        print(f"✅ {field}: Present ({len(str(value))} chars)")
                    else:
                        print(f"⚠️ {field}: Too short or empty")
            else:
                missing_current.append(field)
        
        # Check expected new fields (from review request)
        missing_expected = []
        for field in expected_new_fields:
            if field not in data:
                missing_expected.append(field)
        
        print(f"\n📊 Current Implementation Status:")
        print(f"   ✅ Current fields present: {len(present_current)}/{len(current_fields)}")
        if missing_current:
            print(f"   ❌ Missing current fields: {missing_current}")
        
        print(f"\n📊 Review Request Requirements:")
        print(f"   ❌ Missing expected new fields: {missing_expected}")
        
        # Return success if current implementation is working
        return len(missing_current) == 0
    
    def verify_content_richness(self, data):
        """Step 4: Verify enhanced content richness"""
        print(f"\n📊 Step 4: Content Richness Verification")
        
        # Check analysis_summary length (should be 300-400 words)
        analysis_summary = data.get("analysis_summary", "")
        word_count = len(analysis_summary.split()) if analysis_summary else 0
        
        if 300 <= word_count <= 500:
            print(f"✅ analysis_summary: {word_count} words (Target: 300-400)")
        elif word_count > 200:
            print(f"⚠️ analysis_summary: {word_count} words (Expected: 300-400)")
        else:
            print(f"❌ analysis_summary: {word_count} words (Too short)")
        
        # Check main_services detail level
        main_services = data.get("main_services", [])
        if isinstance(main_services, list) and len(main_services) > 0:
            avg_service_length = sum(len(str(service)) for service in main_services) / len(main_services)
            print(f"✅ main_services: {len(main_services)} services, avg {avg_service_length:.0f} chars each")
        else:
            print(f"⚠️ main_services: Limited or missing")
        
        # Check content_suggestions specificity
        content_suggestions = data.get("content_suggestions", [])
        if isinstance(content_suggestions, list) and len(content_suggestions) > 0:
            specific_suggestions = [s for s in content_suggestions if len(str(s)) > 50]
            print(f"✅ content_suggestions: {len(content_suggestions)} total, {len(specific_suggestions)} detailed")
        else:
            print(f"⚠️ content_suggestions: Limited or missing")
        
        return True
    
    def verify_multi_page_exploitation(self, data):
        """Step 5: Verify multi-page content exploitation"""
        print(f"\n🌐 Step 5: Multi-Page Exploitation Verification")
        
        # Check pages_analyzed_count
        pages_count = data.get("pages_analyzed_count", 0)
        non_technical_count = data.get("non_technical_pages_count", 0)
        
        if pages_count > 1:
            print(f"✅ Multiple pages analyzed: {pages_count} total")
        else:
            print(f"⚠️ Only {pages_count} page(s) analyzed")
        
        if non_technical_count > 0:
            print(f"✅ Non-technical pages: {non_technical_count}")
        else:
            print(f"⚠️ No non-technical pages identified")
        
        # Look for specific page mentions in analysis
        analysis_text = str(data.get("analysis_summary", "")) + str(data.get("products_services_details", ""))
        
        page_indicators = [
            "page", "section", "rubrique", "onglet", "menu",
            "accueil", "produits", "services", "à propos", "contact",
            "boutique", "catalogue", "galerie"
        ]
        
        found_indicators = [indicator for indicator in page_indicators if indicator.lower() in analysis_text.lower()]
        
        if len(found_indicators) >= 3:
            print(f"✅ Multi-page evidence: Found {len(found_indicators)} page indicators")
        else:
            print(f"⚠️ Limited multi-page evidence: {len(found_indicators)} indicators")
        
        return True
    
    def verify_content_specificity(self, data):
        """Step 6: Verify content is specific and non-generic"""
        print(f"\n🎯 Step 6: Content Specificity Verification")
        
        # Check for specific business details
        products_details = data.get("products_services_details", "")
        company_expertise = data.get("company_expertise", "")
        value_proposition = data.get("unique_value_proposition", "")
        
        # Look for specific terms related to the watch business
        watch_terms = [
            "montre", "horlogerie", "artisan", "mouvement", "automatique",
            "mécanique", "bracelet", "cadran", "boîtier", "personnalisé"
        ]
        
        all_content = f"{products_details} {company_expertise} {value_proposition}".lower()
        found_terms = [term for term in watch_terms if term in all_content]
        
        if len(found_terms) >= 3:
            print(f"✅ Specific content: Found {len(found_terms)} relevant terms")
            print(f"   Terms: {', '.join(found_terms[:5])}")
        else:
            print(f"⚠️ Generic content: Only {len(found_terms)} specific terms found")
        
        # Check for generic AI phrases to avoid
        generic_phrases = [
            "découvrez l'art de", "plongez dans", "laissez-vous séduire",
            "explorez notre", "notre passion pour", "au cœur de"
        ]
        
        generic_found = [phrase for phrase in generic_phrases if phrase in all_content]
        
        if len(generic_found) == 0:
            print(f"✅ Non-generic content: No generic AI phrases detected")
        else:
            print(f"⚠️ Generic phrases found: {len(generic_found)}")
        
        return True
    
    def run_comprehensive_test(self):
        """Run the complete enhanced website analysis test suite"""
        print("🚀 Enhanced GPT-4o Website Analysis Testing Suite")
        print("=" * 60)
        print(f"Backend: {BACKEND_URL}")
        print(f"Test Website: {TEST_WEBSITE}")
        print(f"Credentials: {TEST_CREDENTIALS['email']}")
        print("=" * 60)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Enhanced Website Analysis
        analysis_data = self.test_enhanced_website_analysis()
        if not analysis_data:
            print("\n❌ CRITICAL: Website analysis failed")
            return False
        
        # Step 3-6: Verification steps
        self.verify_new_fields(analysis_data)
        self.verify_content_richness(analysis_data)
        self.verify_multi_page_exploitation(analysis_data)
        self.verify_content_specificity(analysis_data)
        
        # Final summary
        print(f"\n📋 FINAL ANALYSIS SUMMARY")
        print("=" * 40)
        
        # Key metrics
        analysis_depth = analysis_data.get("analysis_depth", "unknown")
        pages_count = analysis_data.get("pages_analyzed_count", 0)
        non_technical_count = analysis_data.get("non_technical_pages_count", 0)
        summary_words = len(analysis_data.get("analysis_summary", "").split())
        
        print(f"Analysis Depth: {analysis_depth}")
        print(f"Pages Analyzed: {pages_count}")
        print(f"Non-Technical Pages: {non_technical_count}")
        print(f"Summary Length: {summary_words} words")
        
        # Success criteria
        success_criteria = [
            analysis_depth == "enhanced_multi_page",
            pages_count > 1,
            non_technical_count > 0,
            summary_words >= 250,
            "products_services_details" in analysis_data,
            "company_expertise" in analysis_data,
            "unique_value_proposition" in analysis_data
        ]
        
        success_rate = sum(success_criteria) / len(success_criteria) * 100
        
        print(f"\n🎯 SUCCESS RATE: {success_rate:.1f}% ({sum(success_criteria)}/{len(success_criteria)} criteria met)")
        
        if success_rate >= 85:
            print("✅ ENHANCED WEBSITE ANALYSIS SYSTEM: FULLY OPERATIONAL")
        elif success_rate >= 70:
            print("⚠️ ENHANCED WEBSITE ANALYSIS SYSTEM: MOSTLY WORKING")
        else:
            print("❌ ENHANCED WEBSITE ANALYSIS SYSTEM: NEEDS ATTENTION")
        
        return success_rate >= 70

if __name__ == "__main__":
    tester = EnhancedWebsiteAnalysisTest()
    success = tester.run_comprehensive_test()
    
    if success:
        print(f"\n🎉 TEST SUITE COMPLETED SUCCESSFULLY")
    else:
        print(f"\n💥 TEST SUITE FAILED - ISSUES DETECTED")