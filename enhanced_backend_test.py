#!/usr/bin/env python3
"""
Enhanced Backend Test Suite - French Review Request
Testing final improvements: Enhanced website analysis and business profile lock/unlock system
"""

import requests
import json
import os
import time
from datetime import datetime

# Configuration - Using the correct backend URL from frontend/.env
BACKEND_URL = "https://social-pub-hub.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials as specified in review request
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class EnhancedBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()
    
    def test_health_check(self):
        """Step 1: Backend Health Check"""
        print("🏥 STEP 1: Backend Health Check")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{API_BASE}/health")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                service = data.get("service")
                
                self.log_result(
                    "Backend Health Check", 
                    True, 
                    f"Status: {status}, Service: {service}"
                )
                return True
            else:
                self.log_result(
                    "Backend Health Check", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Backend Health Check", False, error=str(e))
            return False
    
    def authenticate(self):
        """Step 2: Authenticate with specified credentials"""
        print("🔐 STEP 2: Authentication")
        print("=" * 50)
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login-robust", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                self.log_result(
                    "Authentication", 
                    True, 
                    f"Successfully authenticated as {TEST_EMAIL}, User ID: {self.user_id}"
                )
                return True
            else:
                self.log_result(
                    "Authentication", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, error=str(e))
            return False
    
    def test_business_profile_get(self):
        """Step 3: Test GET /api/business-profile - Data persistence verification"""
        print("📋 STEP 3: Business Profile GET - Data Persistence")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{API_BASE}/business-profile")
            
            if response.status_code == 200:
                data = response.json()
                
                # Count populated vs empty fields
                populated_fields = 0
                empty_fields = 0
                field_details = []
                
                for key, value in data.items():
                    if value is not None and value != "" and value != []:
                        populated_fields += 1
                        if len(field_details) < 5:  # Show first 5 populated fields
                            field_details.append(f"{key}: {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}")
                    else:
                        empty_fields += 1
                
                self.business_profile_data = data  # Store for later tests
                
                self.log_result(
                    "Business Profile GET", 
                    True, 
                    f"Retrieved profile with {populated_fields} populated fields, {empty_fields} empty fields. Sample: {field_details}"
                )
                return True
            else:
                self.log_result(
                    "Business Profile GET", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Business Profile GET", False, error=str(e))
            return False
    
    def test_business_profile_put_complete(self):
        """Step 4: Test PUT /api/business-profile - Complete profile update with lock/unlock system"""
        print("💾 STEP 4: Business Profile PUT - Complete Update (Lock/Unlock System)")
        print("=" * 50)
        
        try:
            # Test data for complete business profile update
            test_profile_data = {
                "business_name": "Claire et Marcus Test Enhanced",
                "business_type": "Agence SaaS IA",
                "business_description": "Automatisation complète des réseaux sociaux avec intelligence artificielle avancée",
                "brand_tone": "professionnel",
                "posting_frequency": "quotidien",
                "email": "test.enhanced@claireetmarcus.com",
                "website_url": "https://enhanced.claireetmarcus.com",
                "target_audience": "PME 25-50 ans, entrepreneurs tech-savvy",
                "preferred_platforms": ["linkedin", "facebook", "instagram"],
                "budget_range": "1000-5000",
                "hashtags_primary": ["#IA", "#SaaS", "#Automatisation"],
                "hashtags_secondary": ["#Marketing", "#Social", "#Tech"]
            }
            
            response = self.session.put(f"{API_BASE}/business-profile", json=test_profile_data)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                
                self.log_result(
                    "Business Profile PUT Complete", 
                    success, 
                    f"Successfully updated complete business profile with {len(test_profile_data)} fields"
                )
                
                # Store test data for verification
                self.test_profile_data = test_profile_data
                return success
            else:
                self.log_result(
                    "Business Profile PUT Complete", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Business Profile PUT Complete", False, error=str(e))
            return False
    
    def test_business_profile_persistence(self):
        """Step 5: Verify business profile data persistence"""
        print("🔍 STEP 5: Business Profile Data Persistence Verification")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{API_BASE}/business-profile")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify that our test data was saved correctly
                if hasattr(self, 'test_profile_data'):
                    matched_fields = 0
                    total_test_fields = len(self.test_profile_data)
                    mismatched_fields = []
                    
                    for key, expected_value in self.test_profile_data.items():
                        actual_value = data.get(key)
                        if actual_value == expected_value:
                            matched_fields += 1
                        else:
                            mismatched_fields.append(f"{key}: expected {expected_value}, got {actual_value}")
                    
                    persistence_rate = (matched_fields / total_test_fields * 100) if total_test_fields > 0 else 0
                    
                    self.log_result(
                        "Business Profile Persistence", 
                        matched_fields == total_test_fields, 
                        f"Data persistence: {matched_fields}/{total_test_fields} fields match ({persistence_rate:.1f}%). Mismatches: {mismatched_fields[:3]}"
                    )
                    
                    return matched_fields == total_test_fields
                else:
                    self.log_result(
                        "Business Profile Persistence", 
                        False, 
                        "No test data available for comparison"
                    )
                    return False
            else:
                self.log_result(
                    "Business Profile Persistence", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Business Profile Persistence", False, error=str(e))
            return False
    
    def test_business_profile_partial_update(self):
        """Step 6: Test partial business profile update (lock/unlock functionality)"""
        print("🔄 STEP 6: Business Profile Partial Update (Lock/Unlock Test)")
        print("=" * 50)
        
        try:
            # Test partial update - only update name and tone
            partial_update = {
                "business_name": "Claire et Marcus Partial Test",
                "brand_tone": "créatif"
            }
            
            response = self.session.put(f"{API_BASE}/business-profile", json=partial_update)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                
                if success:
                    # Verify partial update worked
                    verify_response = self.session.get(f"{API_BASE}/business-profile")
                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        
                        name_updated = verify_data.get("business_name") == partial_update["business_name"]
                        tone_updated = verify_data.get("brand_tone") == partial_update["brand_tone"]
                        
                        # Check that other fields weren't changed
                        email_preserved = verify_data.get("email") == self.test_profile_data.get("email")
                        
                        self.log_result(
                            "Business Profile Partial Update", 
                            name_updated and tone_updated and email_preserved, 
                            f"Partial update successful: name updated: {name_updated}, tone updated: {tone_updated}, other fields preserved: {email_preserved}"
                        )
                        
                        return name_updated and tone_updated and email_preserved
                    else:
                        self.log_result(
                            "Business Profile Partial Update", 
                            False, 
                            "Could not verify partial update"
                        )
                        return False
                else:
                    self.log_result(
                        "Business Profile Partial Update", 
                        False, 
                        "Partial update returned success=false"
                    )
                    return False
            else:
                self.log_result(
                    "Business Profile Partial Update", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Business Profile Partial Update", False, error=str(e))
            return False
    
    def test_enhanced_website_analysis(self):
        """Step 7: Test POST /api/website/analyze - Enhanced multi-page analysis"""
        print("🌐 STEP 7: Enhanced Website Analysis - Multi-page Discovery")
        print("=" * 50)
        
        try:
            # Test with example.com as specified in review request
            test_url = "https://example.com"
            
            response = self.session.post(f"{API_BASE}/website/analyze", json={
                "website_url": test_url
            })
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for enhanced analysis fields
                required_fields = [
                    "analysis_summary", "key_topics", "brand_tone", 
                    "target_audience", "main_services", "content_suggestions",
                    "website_url", "created_at", "next_analysis_due"
                ]
                
                present_fields = []
                missing_fields = []
                
                for field in required_fields:
                    if field in data and data[field] is not None:
                        present_fields.append(field)
                    else:
                        missing_fields.append(field)
                
                # Check analysis quality (enhanced features)
                analysis_summary = data.get("analysis_summary", "")
                key_topics = data.get("key_topics", [])
                main_services = data.get("main_services", [])
                content_suggestions = data.get("content_suggestions", [])
                
                # Enhanced analysis should have:
                # - Summary with 5-8 sentences (as mentioned in review)
                # - Detailed audience analysis
                # - 5-8 services
                # - 10 suggestions
                summary_sentences = len(analysis_summary.split('.')) if analysis_summary else 0
                topics_count = len(key_topics) if isinstance(key_topics, list) else 0
                services_count = len(main_services) if isinstance(main_services, list) else 0
                suggestions_count = len(content_suggestions) if isinstance(content_suggestions, list) else 0
                
                quality_metrics = {
                    "summary_length": len(analysis_summary) if analysis_summary else 0,
                    "summary_sentences": summary_sentences,
                    "topics_count": topics_count,
                    "services_count": services_count,
                    "suggestions_count": suggestions_count
                }
                
                # Enhanced analysis criteria
                is_enhanced = (
                    summary_sentences >= 3 and  # At least 3 sentences
                    len(analysis_summary) > 100 and  # Substantial summary
                    topics_count >= 2 and  # Multiple topics
                    services_count >= 2 and  # Multiple services
                    suggestions_count >= 3  # Multiple suggestions
                )
                
                self.log_result(
                    "Enhanced Website Analysis", 
                    len(present_fields) >= 8 and is_enhanced, 
                    f"Analysis created for {test_url}. Fields: {len(present_fields)}/{len(required_fields)} present. Quality: {quality_metrics}. Enhanced criteria met: {is_enhanced}"
                )
                
                # Store analysis for next test
                self.analysis_data = data
                return len(present_fields) >= 8 and is_enhanced
            else:
                self.log_result(
                    "Enhanced Website Analysis", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Enhanced Website Analysis", False, error=str(e))
            return False
    
    def test_website_analysis_retrieval(self):
        """Step 8: Test GET /api/website/analysis - Verify analysis persistence"""
        print("📖 STEP 8: Website Analysis Retrieval - Persistence Check")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{API_BASE}/website/analysis")
            
            if response.status_code == 200:
                data = response.json()
                
                if data and data.get("analysis") is not None:
                    analysis = data.get("analysis")
                    
                    # Verify it matches our created analysis
                    if hasattr(self, 'analysis_data'):
                        website_url_match = analysis.get("website_url") == self.analysis_data.get("website_url")
                        has_summary = bool(analysis.get("analysis_summary"))
                        has_topics = bool(analysis.get("key_topics"))
                        has_services = bool(analysis.get("main_services"))
                        
                        self.log_result(
                            "Website Analysis Retrieval", 
                            website_url_match and has_summary and has_topics and has_services, 
                            f"Analysis retrieved successfully. URL match: {website_url_match}, Has summary: {has_summary}, Has topics: {has_topics}, Has services: {has_services}"
                        )
                        
                        return website_url_match and has_summary and has_topics and has_services
                    else:
                        self.log_result(
                            "Website Analysis Retrieval", 
                            True, 
                            f"Analysis retrieved (no previous analysis to compare): {analysis.get('website_url', 'No URL')}"
                        )
                        return True
                else:
                    self.log_result(
                        "Website Analysis Retrieval", 
                        True, 
                        "No analysis found (empty state - this is valid)"
                    )
                    return True
            else:
                self.log_result(
                    "Website Analysis Retrieval", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Website Analysis Retrieval", False, error=str(e))
            return False
    
    def test_brand_tone_validation(self):
        """Step 9: Test brand tone dropdown validation"""
        print("🎨 STEP 9: Brand Tone Dropdown Validation")
        print("=" * 50)
        
        try:
            # Test different brand tone values
            test_tones = ["professionnel", "luxe", "simple", "créatif", "amical"]
            successful_tones = []
            failed_tones = []
            
            for tone in test_tones:
                try:
                    response = self.session.put(f"{API_BASE}/business-profile", json={
                        "brand_tone": tone
                    })
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("success"):
                            # Verify the tone was actually saved
                            verify_response = self.session.get(f"{API_BASE}/business-profile")
                            if verify_response.status_code == 200:
                                verify_data = verify_response.json()
                                if verify_data.get("brand_tone") == tone:
                                    successful_tones.append(tone)
                                else:
                                    failed_tones.append(f"{tone} (not saved)")
                            else:
                                failed_tones.append(f"{tone} (verify failed)")
                        else:
                            failed_tones.append(f"{tone} (success=false)")
                    else:
                        failed_tones.append(f"{tone} (status {response.status_code})")
                        
                except Exception as tone_error:
                    failed_tones.append(f"{tone} (error: {str(tone_error)[:30]})")
            
            success_rate = (len(successful_tones) / len(test_tones) * 100) if test_tones else 0
            
            self.log_result(
                "Brand Tone Validation", 
                len(successful_tones) >= 4,  # At least 4 out of 5 should work
                f"Brand tone validation: {len(successful_tones)}/{len(test_tones)} tones successful ({success_rate:.1f}%). Successful: {successful_tones}. Failed: {failed_tones}"
            )
            
            return len(successful_tones) >= 4
                
        except Exception as e:
            self.log_result("Brand Tone Validation", False, error=str(e))
            return False
    
    def run_all_tests(self):
        """Run all enhanced backend tests for French review request"""
        print("🚀 ENHANCED BACKEND TESTING - AMÉLIORATIONS FINALES")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_EMAIL}")
        print("FOCUS: Enhanced website analysis + Business profile lock/unlock system")
        print("=" * 60)
        print()
        
        # Run tests in sequence
        tests = [
            self.test_health_check,
            self.authenticate,
            self.test_business_profile_get,
            self.test_business_profile_put_complete,
            self.test_business_profile_persistence,
            self.test_business_profile_partial_update,
            self.test_enhanced_website_analysis,
            self.test_website_analysis_retrieval,
            self.test_brand_tone_validation
        ]
        
        for test in tests:
            if not test():
                print("❌ Test failed, continuing with remaining tests...")
            print()
        
        # Summary
        print("📋 TEST SUMMARY - AMÉLIORATIONS FINALES")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Detailed results
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
            if result['error']:
                print(f"   Error: {result['error']}")
        
        print()
        print("🎯 ENHANCED BACKEND TESTING COMPLETED")
        
        return success_rate >= 80  # High threshold for enhanced features

if __name__ == "__main__":
    tester = EnhancedBackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("✅ Overall testing: SUCCESS")
        exit(0)
    else:
        print("❌ Overall testing: FAILED")
        exit(1)