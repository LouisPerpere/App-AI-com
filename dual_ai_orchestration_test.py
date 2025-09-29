#!/usr/bin/env python3
"""
Test de l'orchestration double IA pour l'analyse de site web
Teste la nouvelle fonctionnalité majeure qui orchestre GPT-4o + Claude Sonnet 4 en parallèle
"""

import requests
import json
import time
from datetime import datetime

class DualAIOrchestrationTester:
    def __init__(self):
        self.base_url = "https://social-pub-hub.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        
        # Test credentials from review request
        self.email = "lperpere@yahoo.fr"
        self.password = "L@Reunion974!"
        
        # Test website URL from review request
        self.test_website = "https://myownwatch.fr"
        
        print("🎭 Dual AI Orchestration Tester Initialized")
        print(f"   Backend: {self.base_url}")
        print(f"   Test Website: {self.test_website}")
        print(f"   Test User: {self.email}")

    def make_request(self, method, endpoint, data=None, expected_status=200):
        """Make HTTP request with proper error handling"""
        url = f"{self.base_url}/{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        try:
            if method == "GET":
                response = self.session.get(url, headers=headers, timeout=60)
            elif method == "POST":
                response = self.session.post(url, headers=headers, json=data, timeout=120)
            elif method == "PUT":
                response = self.session.put(url, headers=headers, json=data, timeout=60)
            elif method == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=60)
            
            print(f"   {method} {endpoint} -> {response.status_code}")
            
            if response.status_code == expected_status:
                try:
                    return True, response.status_code, response.json()
                except:
                    return True, response.status_code, response.text
            else:
                try:
                    error_data = response.json()
                    print(f"   ❌ Error: {error_data}")
                    return False, response.status_code, error_data
                except:
                    print(f"   ❌ Error: {response.text}")
                    return False, response.status_code, response.text
                    
        except requests.exceptions.Timeout:
            print(f"   ⏰ Request timeout for {method} {endpoint}")
            return False, 408, {"error": "Request timeout"}
        except Exception as e:
            print(f"   ❌ Request failed: {str(e)}")
            return False, 500, {"error": str(e)}

    def test_authentication(self):
        """Test 1: Authentication with provided credentials"""
        print("\n🔐 Step 1: Authentication Test")
        
        auth_data = {
            "email": self.email,
            "password": self.password
        }
        
        success, status, response = self.make_request("POST", "auth/login-robust", auth_data, 200)
        
        if success and "access_token" in response:
            self.access_token = response["access_token"]
            self.user_id = response.get("user_id", "")
            print(f"   ✅ Authentication successful")
            print(f"   ✅ User ID: {self.user_id}")
            print(f"   ✅ Token obtained: {self.access_token[:20]}...")
            return True
        else:
            print(f"   ❌ Authentication failed: {response}")
            return False

    def test_website_analysis_dual_orchestration(self):
        """Test 2: Website Analysis with Dual AI Orchestration"""
        print("\n🎭 Step 2: Dual AI Orchestration Website Analysis Test")
        
        analysis_data = {
            "website_url": self.test_website
        }
        
        print(f"   🔍 Analyzing website: {self.test_website}")
        print(f"   ⏳ This may take 30-60 seconds for dual AI processing...")
        
        start_time = time.time()
        success, status, response = self.make_request("POST", "website/analyze", analysis_data, 200)
        end_time = time.time()
        
        analysis_duration = end_time - start_time
        print(f"   ⏱️ Analysis completed in {analysis_duration:.1f} seconds")
        
        if success:
            print(f"   ✅ Website analysis successful")
            return True, response
        else:
            print(f"   ❌ Website analysis failed: {response}")
            return False, response

    def test_dual_orchestration_structure(self, analysis_response):
        """Test 3: Verify Dual Orchestration Response Structure"""
        print("\n🏗️ Step 3: Dual Orchestration Structure Verification")
        
        required_fields = [
            "analysis_type",
            "analysis_summary", 
            "narrative_insights",
            "orchestration_info",
            "business_ai",
            "narrative_ai"
        ]
        
        missing_fields = []
        present_fields = []
        
        for field in required_fields:
            if field in analysis_response:
                present_fields.append(field)
                print(f"   ✅ {field}: Present")
            else:
                missing_fields.append(field)
                print(f"   ❌ {field}: Missing")
        
        # Verify analysis_type
        if analysis_response.get("analysis_type") == "dual_orchestrated":
            print(f"   ✅ analysis_type = 'dual_orchestrated' ✓")
        else:
            print(f"   ❌ analysis_type = '{analysis_response.get('analysis_type')}' (expected 'dual_orchestrated')")
            missing_fields.append("correct_analysis_type")
        
        # Verify AI assignments
        business_ai = analysis_response.get("business_ai", "")
        narrative_ai = analysis_response.get("narrative_ai", "")
        
        if "GPT" in business_ai or "gpt" in business_ai.lower():
            print(f"   ✅ business_ai = '{business_ai}' (GPT-4o detected)")
        else:
            print(f"   ❌ business_ai = '{business_ai}' (GPT-4o expected)")
            missing_fields.append("correct_business_ai")
            
        if "Claude" in narrative_ai or "claude" in narrative_ai.lower():
            print(f"   ✅ narrative_ai = '{narrative_ai}' (Claude detected)")
        else:
            print(f"   ❌ narrative_ai = '{narrative_ai}' (Claude expected)")
            missing_fields.append("correct_narrative_ai")
        
        success_rate = len(present_fields) / len(required_fields) * 100
        print(f"   📊 Structure compliance: {success_rate:.1f}% ({len(present_fields)}/{len(required_fields)} fields)")
        
        return len(missing_fields) == 0, missing_fields

    def test_analysis_content_quality(self, analysis_response):
        """Test 4: Verify Analysis Content Quality and Differentiation"""
        print("\n📝 Step 4: Analysis Content Quality and Differentiation Test")
        
        analysis_summary = analysis_response.get("analysis_summary", "")
        narrative_insights = analysis_response.get("narrative_insights", "")
        
        # Test content presence
        if len(analysis_summary) > 50:
            print(f"   ✅ Business analysis (GPT-4o): {len(analysis_summary)} characters")
        else:
            print(f"   ❌ Business analysis too short: {len(analysis_summary)} characters")
            
        if len(narrative_insights) > 50:
            print(f"   ✅ Narrative analysis (Claude): {len(narrative_insights)} characters")
        else:
            print(f"   ❌ Narrative analysis too short: {len(narrative_insights)} characters")
        
        # Test content differentiation
        if analysis_summary != narrative_insights:
            print(f"   ✅ Analyses are different and complementary")
            
            # Check for business-oriented keywords in GPT-4o analysis
            business_keywords = ["service", "client", "marché", "stratégie", "business", "vente", "produit"]
            business_score = sum(1 for keyword in business_keywords if keyword.lower() in analysis_summary.lower())
            
            # Check for narrative-oriented keywords in Claude analysis  
            narrative_keywords = ["histoire", "vision", "storytelling", "émotion", "inspiration", "récit", "narrative"]
            narrative_score = sum(1 for keyword in narrative_keywords if keyword.lower() in narrative_insights.lower())
            
            print(f"   📊 Business keywords in GPT-4o analysis: {business_score}")
            print(f"   📊 Narrative keywords in Claude analysis: {narrative_score}")
            
            if business_score > 0:
                print(f"   ✅ GPT-4o analysis shows business orientation")
            else:
                print(f"   ⚠️ GPT-4o analysis lacks clear business orientation")
                
            if narrative_score > 0:
                print(f"   ✅ Claude analysis shows narrative orientation")
            else:
                print(f"   ⚠️ Claude analysis lacks clear narrative orientation")
                
            return True
        else:
            print(f"   ❌ Analyses are identical - no differentiation detected")
            return False

    def test_orchestration_info(self, analysis_response):
        """Test 5: Verify Orchestration Information"""
        print("\n🎯 Step 5: Orchestration Information Verification")
        
        orchestration_info = analysis_response.get("orchestration_info", {})
        
        if not orchestration_info:
            print(f"   ❌ orchestration_info is empty or missing")
            return False
            
        print(f"   ✅ orchestration_info present with {len(orchestration_info)} fields")
        
        # Check for expected orchestration fields
        expected_fields = ["business_ai", "narrative_ai", "completion_time", "status"]
        present_count = 0
        
        for field in expected_fields:
            if field in orchestration_info:
                present_count += 1
                print(f"   ✅ {field}: {orchestration_info[field]}")
            else:
                print(f"   ⚠️ {field}: Not present in orchestration_info")
        
        if orchestration_info.get("status") == "completed":
            print(f"   ✅ Orchestration status: completed")
        else:
            print(f"   ⚠️ Orchestration status: {orchestration_info.get('status')}")
            
        success_rate = present_count / len(expected_fields) * 100
        print(f"   📊 Orchestration info completeness: {success_rate:.1f}%")
        
        return present_count >= 2  # At least 2 fields should be present

    def test_robustness_and_error_handling(self):
        """Test 6: Robustness and Error Handling"""
        print("\n🛡️ Step 6: Robustness and Error Handling Test")
        
        # Test with invalid URL
        print("   🔍 Testing with invalid URL...")
        invalid_data = {"website_url": "https://this-domain-does-not-exist-12345.com"}
        
        success, status, response = self.make_request("POST", "website/analyze", invalid_data, expected_status=None)
        
        if status in [200, 500]:  # Either works or fails gracefully
            if status == 200:
                print(f"   ✅ Invalid URL handled gracefully (returned analysis)")
            else:
                print(f"   ✅ Invalid URL failed gracefully (status {status})")
            
            # Test timeout handling by checking if response came back quickly for invalid domain
            return True
        else:
            print(f"   ❌ Unexpected status for invalid URL: {status}")
            return False

    def test_performance_and_timeout(self):
        """Test 7: Performance and Timeout Handling"""
        print("\n⏱️ Step 7: Performance and Timeout Test")
        
        # Test with a simple, fast website
        simple_data = {"website_url": "https://example.com"}
        
        start_time = time.time()
        success, status, response = self.make_request("POST", "website/analyze", simple_data, expected_status=None)
        end_time = time.time()
        
        duration = end_time - start_time
        
        if success and status == 200:
            print(f"   ✅ Simple website analysis completed in {duration:.1f}s")
            
            if duration < 60:  # Should complete within 60 seconds
                print(f"   ✅ Performance acceptable (< 60s)")
                return True
            else:
                print(f"   ⚠️ Performance slow (> 60s)")
                return False
        else:
            print(f"   ❌ Simple website analysis failed: {status}")
            return False

    def run_comprehensive_test(self):
        """Run comprehensive dual AI orchestration test suite"""
        print("=" * 80)
        print("🎭 DUAL AI ORCHESTRATION COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        print(f"Objectif: Vérifier l'orchestration GPT-4o + Claude Sonnet 4")
        print(f"Backend: {self.base_url}")
        print(f"Website: {self.test_website}")
        print(f"User: {self.email}")
        print("=" * 80)
        
        test_results = []
        
        # Test 1: Authentication
        auth_success = self.test_authentication()
        test_results.append(("Authentication", auth_success))
        
        if not auth_success:
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with tests")
            return self.generate_summary(test_results)
        
        # Test 2: Website Analysis with Dual Orchestration
        analysis_success, analysis_response = self.test_website_analysis_dual_orchestration()
        test_results.append(("Website Analysis", analysis_success))
        
        if not analysis_success:
            print("\n❌ CRITICAL: Website analysis failed - cannot test orchestration features")
            return self.generate_summary(test_results)
        
        # Test 3: Structure Verification
        structure_success, missing_fields = self.test_dual_orchestration_structure(analysis_response)
        test_results.append(("Response Structure", structure_success))
        
        # Test 4: Content Quality
        content_success = self.test_analysis_content_quality(analysis_response)
        test_results.append(("Content Quality", content_success))
        
        # Test 5: Orchestration Info
        orchestration_success = self.test_orchestration_info(analysis_response)
        test_results.append(("Orchestration Info", orchestration_success))
        
        # Test 6: Robustness
        robustness_success = self.test_robustness_and_error_handling()
        test_results.append(("Robustness", robustness_success))
        
        # Test 7: Performance
        performance_success = self.test_performance_and_timeout()
        test_results.append(("Performance", performance_success))
        
        return self.generate_summary(test_results, analysis_response)

    def generate_summary(self, test_results, analysis_response=None):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 DUAL AI ORCHESTRATION TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(1 for _, success in test_results if success)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        print()
        
        # Individual test results
        for test_name, success in test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print()
        
        # Detailed findings if analysis was successful
        if analysis_response:
            print("🔍 DETAILED ANALYSIS FINDINGS:")
            print(f"   Analysis Type: {analysis_response.get('analysis_type', 'N/A')}")
            print(f"   Business AI: {analysis_response.get('business_ai', 'N/A')}")
            print(f"   Narrative AI: {analysis_response.get('narrative_ai', 'N/A')}")
            print(f"   Website Analyzed: {analysis_response.get('website_url', 'N/A')}")
            print(f"   Pages Count: {analysis_response.get('pages_count', 'N/A')}")
            
            # Show sample content
            analysis_summary = analysis_response.get('analysis_summary', '')
            narrative_insights = analysis_response.get('narrative_insights', '')
            
            if analysis_summary:
                print(f"\n📋 BUSINESS ANALYSIS SAMPLE (GPT-4o):")
                print(f"   {analysis_summary[:200]}{'...' if len(analysis_summary) > 200 else ''}")
                
            if narrative_insights:
                print(f"\n📖 NARRATIVE ANALYSIS SAMPLE (Claude):")
                print(f"   {narrative_insights[:200]}{'...' if len(narrative_insights) > 200 else ''}")
        
        print("\n" + "=" * 80)
        
        # Final assessment
        if success_rate >= 85:
            print("🎉 CONCLUSION: Dual AI Orchestration is FULLY OPERATIONAL")
            print("   The new GPT-4o + Claude Sonnet 4 system is working correctly")
        elif success_rate >= 70:
            print("⚠️ CONCLUSION: Dual AI Orchestration is MOSTLY OPERATIONAL")
            print("   Minor issues detected but core functionality works")
        else:
            print("❌ CONCLUSION: Dual AI Orchestration has CRITICAL ISSUES")
            print("   Major problems detected - requires immediate attention")
        
        print("=" * 80)
        
        return {
            "success_rate": success_rate,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "test_results": test_results,
            "analysis_response": analysis_response
        }

if __name__ == "__main__":
    tester = DualAIOrchestrationTester()
    results = tester.run_comprehensive_test()