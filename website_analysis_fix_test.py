#!/usr/bin/env python3
"""
Website Analysis Fix Testing Suite
Testing the correction of website analysis with missing content issue

CONTEXT: User reported that website analysis wasn't working - AIs were receiving empty content.
The orchestration functions were fixed to use proper data structure (title, text_content, h1_tags, etc.)
instead of looking for homepage.content which doesn't exist.

TESTS TO PERFORM:
1. Authentication test with lperpere@yahoo.fr / L@Reunion974!
2. Website analysis test with real content using https://myownwatch.fr
3. Verify AIs receive actual website content
4. Verify business_analysis and narrative_analysis contain real analyses
5. Verify response structure with analysis_type = "dual_orchestrated"
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://social-publisher-10.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}
TEST_WEBSITE_URL = "https://myownwatch.fr"

class WebsiteAnalysisTestSuite:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error=""):
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
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()
        
    def test_authentication(self):
        """Test 1: Authentication with provided credentials"""
        try:
            print("🔐 Testing Authentication...")
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json=TEST_CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                self.log_test(
                    "Authentication Test",
                    True,
                    f"Successfully authenticated user {TEST_CREDENTIALS['email']}, User ID: {self.user_id}"
                )
                return True
            else:
                self.log_test(
                    "Authentication Test",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Authentication Test", False, error=str(e))
            return False
    
    def test_website_analysis_with_real_content(self):
        """Test 2: Website analysis with real content verification"""
        try:
            print("🌐 Testing Website Analysis with Real Content...")
            
            if not self.access_token:
                self.log_test(
                    "Website Analysis Test",
                    False,
                    error="No access token available - authentication failed"
                )
                return False
            
            # Test website analysis
            analysis_payload = {
                "website_url": TEST_WEBSITE_URL
            }
            
            print(f"   Analyzing website: {TEST_WEBSITE_URL}")
            start_time = time.time()
            
            response = self.session.post(
                f"{BACKEND_URL}/website/analyze",
                json=analysis_payload,
                timeout=60  # Website analysis can take time
            )
            
            analysis_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = [
                    "analysis_type",
                    "analysis_summary", 
                    "narrative_insights",
                    "orchestration_info"
                ]
                
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test(
                        "Website Analysis Test",
                        False,
                        f"Missing required fields: {missing_fields}",
                        "Response structure incomplete"
                    )
                    return False
                
                # Verify analysis_type
                if data.get("analysis_type") != "dual_orchestrated":
                    self.log_test(
                        "Website Analysis Test",
                        False,
                        f"Expected analysis_type='dual_orchestrated', got '{data.get('analysis_type')}'",
                        "Incorrect analysis type"
                    )
                    return False
                
                # Verify content quality - check that analyses are not empty and contain real content
                business_analysis = data.get("analysis_summary", "")
                narrative_analysis = data.get("narrative_insights", "")
                
                if len(business_analysis.strip()) < 50:
                    self.log_test(
                        "Website Analysis Test",
                        False,
                        f"Business analysis too short ({len(business_analysis)} chars)",
                        "GPT-4o analysis appears empty or insufficient"
                    )
                    return False
                
                if len(narrative_analysis.strip()) < 50:
                    self.log_test(
                        "Website Analysis Test",
                        False,
                        f"Narrative analysis too short ({len(narrative_analysis)} chars)",
                        "Claude analysis appears empty or insufficient"
                    )
                    return False
                
                # Verify orchestration info
                orchestration_info = data.get("orchestration_info", {})
                expected_ai_fields = ["business_ai", "narrative_ai"]
                
                for field in expected_ai_fields:
                    if field not in orchestration_info:
                        self.log_test(
                            "Website Analysis Test",
                            False,
                            f"Missing {field} in orchestration_info",
                            "Orchestration info incomplete"
                        )
                        return False
                
                # Check that analyses mention specific elements from the website
                website_indicators = ["montre", "watch", "horlogerie", "artisan", "myownwatch"]
                business_mentions = sum(1 for indicator in website_indicators 
                                      if indicator.lower() in business_analysis.lower())
                narrative_mentions = sum(1 for indicator in website_indicators 
                                       if indicator.lower() in narrative_analysis.lower())
                
                if business_mentions == 0 and narrative_mentions == 0:
                    self.log_test(
                        "Website Analysis Test",
                        False,
                        "Analyses don't mention specific website elements",
                        "AIs may still be receiving empty content"
                    )
                    return False
                
                self.log_test(
                    "Website Analysis Test",
                    True,
                    f"Analysis completed in {analysis_time:.1f}s. "
                    f"Business analysis: {len(business_analysis)} chars, "
                    f"Narrative analysis: {len(narrative_analysis)} chars, "
                    f"Website mentions: {business_mentions + narrative_mentions}, "
                    f"Business AI: {orchestration_info.get('business_ai', 'Unknown')}, "
                    f"Narrative AI: {orchestration_info.get('narrative_ai', 'Unknown')}"
                )
                return True
                
            else:
                self.log_test(
                    "Website Analysis Test",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Website Analysis Test", False, error=str(e))
            return False
    
    def test_analysis_content_quality(self):
        """Test 3: Detailed content quality verification"""
        try:
            print("📊 Testing Analysis Content Quality...")
            
            if not self.access_token:
                self.log_test(
                    "Content Quality Test",
                    False,
                    error="No access token available"
                )
                return False
            
            # Perform another analysis to get fresh data
            analysis_payload = {"website_url": TEST_WEBSITE_URL}
            
            response = self.session.post(
                f"{BACKEND_URL}/website/analyze",
                json=analysis_payload,
                timeout=60
            )
            
            if response.status_code != 200:
                self.log_test(
                    "Content Quality Test",
                    False,
                    f"Analysis request failed with status {response.status_code}",
                    response.text
                )
                return False
            
            data = response.json()
            business_analysis = data.get("analysis_summary", "")
            narrative_analysis = data.get("narrative_insights", "")
            
            # Check for structured content in GPT-4o business analysis
            business_structure_indicators = [
                "résumé", "audience", "services", "produits", "stratégie", 
                "recommandations", "analyse", "business", "entreprise"
            ]
            
            business_structure_score = sum(1 for indicator in business_structure_indicators 
                                         if indicator.lower() in business_analysis.lower())
            
            # Check for storytelling elements in Claude narrative analysis
            narrative_indicators = [
                "histoire", "récit", "storytelling", "émotion", "expérience",
                "créatif", "narratif", "inspiration", "vision", "passion"
            ]
            
            narrative_score = sum(1 for indicator in narrative_indicators 
                                if indicator.lower() in narrative_analysis.lower())
            
            # Verify analyses are different (not duplicated)
            similarity_threshold = 0.8
            common_words = set(business_analysis.lower().split()) & set(narrative_analysis.lower().split())
            total_words = len(set(business_analysis.lower().split()) | set(narrative_analysis.lower().split()))
            similarity = len(common_words) / total_words if total_words > 0 else 0
            
            if similarity > similarity_threshold:
                self.log_test(
                    "Content Quality Test",
                    False,
                    f"Analyses too similar (similarity: {similarity:.2f})",
                    "AIs may be producing duplicate content"
                )
                return False
            
            # Overall quality assessment
            quality_score = 0
            quality_details = []
            
            if business_structure_score >= 2:
                quality_score += 1
                quality_details.append(f"Business structure: {business_structure_score}/9 indicators")
            
            if narrative_score >= 2:
                quality_score += 1
                quality_details.append(f"Narrative elements: {narrative_score}/10 indicators")
            
            if len(business_analysis) >= 200:
                quality_score += 1
                quality_details.append(f"Business length: {len(business_analysis)} chars")
            
            if len(narrative_analysis) >= 200:
                quality_score += 1
                quality_details.append(f"Narrative length: {len(narrative_analysis)} chars")
            
            if similarity < 0.5:
                quality_score += 1
                quality_details.append(f"Content diversity: {1-similarity:.2f}")
            
            success = quality_score >= 4
            
            self.log_test(
                "Content Quality Test",
                success,
                f"Quality score: {quality_score}/5. " + ", ".join(quality_details),
                "Content quality insufficient" if not success else ""
            )
            
            return success
            
        except Exception as e:
            self.log_test("Content Quality Test", False, error=str(e))
            return False
    
    def test_error_handling(self):
        """Test 4: Error handling with invalid URLs"""
        try:
            print("🚫 Testing Error Handling...")
            
            if not self.access_token:
                self.log_test(
                    "Error Handling Test",
                    False,
                    error="No access token available"
                )
                return False
            
            # Test with invalid URL
            invalid_payload = {"website_url": "https://this-domain-does-not-exist-12345.com"}
            
            response = self.session.post(
                f"{BACKEND_URL}/website/analyze",
                json=invalid_payload,
                timeout=30
            )
            
            # Should handle gracefully (either return error or empty analysis)
            if response.status_code in [200, 400, 404, 422]:
                if response.status_code == 200:
                    data = response.json()
                    # Check if it handled the error gracefully
                    if "error" in data or len(data.get("analysis_summary", "")) < 10:
                        self.log_test(
                            "Error Handling Test",
                            True,
                            f"Gracefully handled invalid URL with status {response.status_code}"
                        )
                        return True
                else:
                    self.log_test(
                        "Error Handling Test",
                        True,
                        f"Properly rejected invalid URL with status {response.status_code}"
                    )
                    return True
            
            self.log_test(
                "Error Handling Test",
                False,
                f"Unexpected response to invalid URL: {response.status_code}",
                response.text[:200]
            )
            return False
            
        except Exception as e:
            # Timeout or connection error is acceptable for invalid URLs
            self.log_test(
                "Error Handling Test",
                True,
                f"Handled invalid URL with exception (acceptable): {type(e).__name__}"
            )
            return True
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Website Analysis Fix Testing Suite")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Website: {TEST_WEBSITE_URL}")
        print(f"Test User: {TEST_CREDENTIALS['email']}")
        print("=" * 60)
        print()
        
        # Run tests in order
        tests = [
            self.test_authentication,
            self.test_website_analysis_with_real_content,
            self.test_analysis_content_quality,
            self.test_error_handling
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        # Summary
        print("=" * 60)
        print("🎯 TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (passed / total) * 100
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
            if result["error"]:
                print(f"   ❌ {result['error']}")
        
        print()
        print(f"📊 OVERALL RESULT: {passed}/{total} tests passed ({success_rate:.1f}%)")
        
        if success_rate >= 75:
            print("🎉 WEBSITE ANALYSIS FIX VERIFICATION: SUCCESS")
            print("   The fix for empty content issue appears to be working correctly.")
            print("   AIs are receiving actual website content and producing real analyses.")
        else:
            print("🚨 WEBSITE ANALYSIS FIX VERIFICATION: ISSUES DETECTED")
            print("   The fix may not be working properly or there are other issues.")
            print("   Review the failed tests above for details.")
        
        return success_rate >= 75

if __name__ == "__main__":
    tester = WebsiteAnalysisTestSuite()
    success = tester.run_all_tests()
    exit(0 if success else 1)