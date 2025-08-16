#!/usr/bin/env python3
"""
Backend Test Suite for Enhanced Multi-Page Website Analysis
Testing the new features implemented for Claire et Marcus
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8001"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}
TEST_WEBSITE_URL = "https://my-own-watch.fr"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        return success
    
    def test_authentication(self):
        """Test user authentication with provided credentials"""
        print("\n🔐 Testing Authentication...")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/api/auth/login",
                json=TEST_CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                
                if self.access_token:
                    # Set authorization header for future requests
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.access_token}"
                    })
                    return self.log_test(
                        "User Authentication", 
                        True, 
                        f"Successfully authenticated user {TEST_CREDENTIALS['email']}"
                    )
                else:
                    return self.log_test(
                        "User Authentication", 
                        False, 
                        "No access token received"
                    )
            else:
                return self.log_test(
                    "User Authentication", 
                    False, 
                    f"Login failed with status {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            return self.log_test(
                "User Authentication", 
                False, 
                f"Authentication error: {str(e)}"
            )
    
    def test_multi_page_analysis(self):
        """Test the enhanced multi-page website analysis"""
        print("\n🌐 Testing Multi-Page Website Analysis...")
        
        if not self.access_token:
            return self.log_test(
                "Multi-Page Analysis", 
                False, 
                "No authentication token available"
            )
        
        try:
            # Test POST /api/website/analyze with force_reanalysis
            analysis_data = {
                "website_url": TEST_WEBSITE_URL,
                "force_reanalysis": True
            }
            
            print(f"   Analyzing website: {TEST_WEBSITE_URL}")
            start_time = time.time()
            
            response = self.session.post(
                f"{BACKEND_URL}/api/website/analyze",
                json=analysis_data,
                timeout=60  # Increased timeout for multi-page analysis
            )
            
            analysis_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify enhanced analysis fields
                required_fields = [
                    "analysis_summary", "key_topics", "brand_tone", 
                    "target_audience", "main_services", "content_suggestions"
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in data or not data[field]:
                        missing_fields.append(field)
                
                if missing_fields:
                    return self.log_test(
                        "Multi-Page Analysis", 
                        False, 
                        f"Missing required fields: {missing_fields}"
                    )
                
                # Check for multi-page specific fields
                pages_analyzed = data.get("pages_analyzed", 0)
                additional_pages_urls = data.get("additional_pages_urls", [])
                
                # Verify content richness
                analysis_summary_length = len(data.get("analysis_summary", ""))
                key_topics_count = len(data.get("key_topics", []))
                main_services_count = len(data.get("main_services", []))
                content_suggestions_count = len(data.get("content_suggestions", []))
                
                details = f"""
                Analysis completed in {analysis_time:.2f}s
                Pages analyzed: {pages_analyzed}
                Additional pages URLs: {len(additional_pages_urls)}
                Analysis summary length: {analysis_summary_length} chars
                Key topics count: {key_topics_count}
                Main services count: {main_services_count}
                Content suggestions count: {content_suggestions_count}
                Analysis summary: {data.get('analysis_summary', '')[:200]}...
                Key topics: {data.get('key_topics', [])}
                Main services: {data.get('main_services', [])}
                """
                
                # Success criteria for enhanced analysis
                success = (
                    analysis_summary_length > 100 and  # Rich summary
                    key_topics_count >= 3 and         # Multiple topics
                    main_services_count >= 1 and      # Identified services
                    content_suggestions_count >= 3    # Rich suggestions
                )
                
                return self.log_test(
                    "Multi-Page Analysis", 
                    success, 
                    details.strip()
                )
                
            else:
                return self.log_test(
                    "Multi-Page Analysis", 
                    False, 
                    f"Analysis failed with status {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            return self.log_test(
                "Multi-Page Analysis", 
                False, 
                f"Analysis error: {str(e)}"
            )
    
    def test_page_discovery(self):
        """Test the page discovery functionality by analyzing the response"""
        print("\n🔍 Testing Page Discovery...")
        
        if not self.access_token:
            return self.log_test(
                "Page Discovery", 
                False, 
                "No authentication token available"
            )
        
        try:
            # Get the latest analysis to check discovered pages
            response = self.session.get(
                f"{BACKEND_URL}/api/website/analysis",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                analysis = data.get("analysis", {})
                
                if analysis:
                    # Check if we have evidence of multi-page analysis
                    analysis_summary = analysis.get("analysis_summary", "")
                    main_services = analysis.get("main_services", [])
                    content_suggestions = analysis.get("content_suggestions", [])
                    
                    # Look for indicators of multi-page content
                    has_rich_content = (
                        len(analysis_summary) > 200 or
                        len(main_services) > 2 or
                        len(content_suggestions) > 3
                    )
                    
                    details = f"""
                    Analysis summary richness: {len(analysis_summary)} chars
                    Services identified: {len(main_services)} ({main_services})
                    Content suggestions: {len(content_suggestions)}
                    Rich content detected: {has_rich_content}
                    """
                    
                    return self.log_test(
                        "Page Discovery", 
                        has_rich_content, 
                        details.strip()
                    )
                else:
                    return self.log_test(
                        "Page Discovery", 
                        False, 
                        "No analysis data found"
                    )
            else:
                return self.log_test(
                    "Page Discovery", 
                    False, 
                    f"Failed to retrieve analysis: {response.status_code}"
                )
                
        except Exception as e:
            return self.log_test(
                "Page Discovery", 
                False, 
                f"Page discovery test error: {str(e)}"
            )
    
    def test_enriched_content_validation(self):
        """Test validation of enriched content from multi-page analysis"""
        print("\n📊 Testing Enriched Content Validation...")
        
        if not self.access_token:
            return self.log_test(
                "Enriched Content Validation", 
                False, 
                "No authentication token available"
            )
        
        try:
            # Get the latest analysis
            response = self.session.get(
                f"{BACKEND_URL}/api/website/analysis",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                analysis = data.get("analysis", {})
                
                if analysis:
                    # Validate content richness and specificity
                    analysis_summary = analysis.get("analysis_summary", "")
                    key_topics = analysis.get("key_topics", [])
                    brand_tone = analysis.get("brand_tone", "")
                    target_audience = analysis.get("target_audience", "")
                    main_services = analysis.get("main_services", [])
                    content_suggestions = analysis.get("content_suggestions", [])
                    
                    # Check for specific indicators of enhanced analysis
                    has_specific_services = any(
                        len(service) > 10 for service in main_services
                    )
                    
                    has_detailed_suggestions = any(
                        len(suggestion) > 30 for suggestion in content_suggestions
                    )
                    
                    has_specific_audience = len(target_audience) > 20
                    has_rich_topics = len(key_topics) >= 4
                    
                    validation_score = sum([
                        len(analysis_summary) > 150,  # Rich summary
                        has_specific_services,        # Specific services
                        has_detailed_suggestions,     # Detailed suggestions
                        has_specific_audience,        # Specific audience
                        has_rich_topics,             # Rich topics
                        len(brand_tone) > 5          # Defined brand tone
                    ])
                    
                    details = f"""
                    Validation Score: {validation_score}/6
                    Analysis summary: {len(analysis_summary)} chars
                    Key topics: {len(key_topics)} ({key_topics})
                    Brand tone: {brand_tone}
                    Target audience: {len(target_audience)} chars
                    Main services: {main_services}
                    Content suggestions count: {len(content_suggestions)}
                    Has specific services: {has_specific_services}
                    Has detailed suggestions: {has_detailed_suggestions}
                    """
                    
                    success = validation_score >= 4  # At least 4/6 criteria met
                    
                    return self.log_test(
                        "Enriched Content Validation", 
                        success, 
                        details.strip()
                    )
                else:
                    return self.log_test(
                        "Enriched Content Validation", 
                        False, 
                        "No analysis data found for validation"
                    )
            else:
                return self.log_test(
                    "Enriched Content Validation", 
                    False, 
                    f"Failed to retrieve analysis: {response.status_code}"
                )
                
        except Exception as e:
            return self.log_test(
                "Enriched Content Validation", 
                False, 
                f"Content validation error: {str(e)}"
            )
    
    def test_metadata_verification(self):
        """Test verification of metadata fields (pages_analyzed, additional_pages_urls)"""
        print("\n📋 Testing Metadata Verification...")
        
        # This test checks if the analysis response includes the new metadata fields
        # Since we may not have direct access to these fields in the stored analysis,
        # we'll perform a fresh analysis to check the response structure
        
        if not self.access_token:
            return self.log_test(
                "Metadata Verification", 
                False, 
                "No authentication token available"
            )
        
        try:
            # Perform a quick analysis to check response structure
            analysis_data = {
                "website_url": "https://google.com",  # Simple site for quick test
                "force_reanalysis": True
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/api/website/analyze",
                json=analysis_data,
                timeout=45
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for metadata fields
                has_pages_analyzed = "pages_analyzed" in data
                has_additional_pages = "additional_pages_urls" in data
                has_status = "status" in data
                has_message = "message" in data
                
                pages_analyzed = data.get("pages_analyzed", 0)
                additional_pages_urls = data.get("additional_pages_urls", [])
                status = data.get("status", "")
                message = data.get("message", "")
                
                details = f"""
                Has pages_analyzed field: {has_pages_analyzed}
                Has additional_pages_urls field: {has_additional_pages}
                Has status field: {has_status}
                Has message field: {has_message}
                Pages analyzed: {pages_analyzed}
                Additional pages count: {len(additional_pages_urls)}
                Status: {status}
                Message: {message}
                """
                
                # Success if we have the key metadata fields
                success = has_pages_analyzed and has_status and has_message
                
                return self.log_test(
                    "Metadata Verification", 
                    success, 
                    details.strip()
                )
            else:
                return self.log_test(
                    "Metadata Verification", 
                    False, 
                    f"Metadata test failed with status {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            return self.log_test(
                "Metadata Verification", 
                False, 
                f"Metadata verification error: {str(e)}"
            )
    
    def test_backend_health(self):
        """Test basic backend health and connectivity"""
        print("\n🏥 Testing Backend Health...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/api/health", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return self.log_test(
                    "Backend Health", 
                    True, 
                    f"Backend healthy: {data.get('message', 'OK')}"
                )
            else:
                return self.log_test(
                    "Backend Health", 
                    False, 
                    f"Health check failed: {response.status_code}"
                )
                
        except Exception as e:
            return self.log_test(
                "Backend Health", 
                False, 
                f"Health check error: {str(e)}"
            )
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Enhanced Multi-Page Website Analysis Backend Tests")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Website: {TEST_WEBSITE_URL}")
        print(f"Test User: {TEST_CREDENTIALS['email']}")
        print("=" * 80)
        
        # Run tests in order
        tests = [
            self.test_backend_health,
            self.test_authentication,
            self.test_multi_page_analysis,
            self.test_page_discovery,
            self.test_enriched_content_validation,
            self.test_metadata_verification
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (passed / total) * 100
        print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 OVERALL RESULT: SUCCESS - Enhanced multi-page analysis is working!")
        elif success_rate >= 60:
            print("⚠️ OVERALL RESULT: PARTIAL SUCCESS - Some issues detected")
        else:
            print("❌ OVERALL RESULT: FAILURE - Major issues detected")
        
        print("\nDetailed Results:")
        for result in self.test_results:
            print(f"  {result['status']}: {result['test']}")
            if result['details']:
                # Print first line of details only for summary
                first_line = result['details'].split('\n')[0].strip()
                if first_line:
                    print(f"    {first_line}")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)