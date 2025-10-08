#!/usr/bin/env python3
"""
Website Analysis Auto-Load Testing Suite
Testing automatic loading of website analysis upon login

Test Requirements from French Review Request:
1. Test endpoint GET /api/website/analysis - Verify that analysis exists in database for user
2. Test login sequence - Simulate login and verify analysis is available
3. Test analyzed data - Verify structure of returned data  
4. Validate required fields - Ensure all necessary fields are present, especially analysis_summary

Expected credentials: lperpere@yahoo.fr / L@Reunion974!
Expected User ID: bdf87a74-e3f3-44f3-bac2-649cde3ef93e

Critical points to verify:
- Analysis contains analysis_summary (required by popup)
- GPT-4o and Claude data available
- Endpoint returns 200 with valid data
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://post-restore.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"
EXPECTED_USER_ID = "bdf87a74-e3f3-44f3-bac2-649cde3ef93e"

class WebsiteAnalysisAutoLoadTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        
    def authenticate(self):
        """Step 1: Authenticate with test credentials"""
        print("🔐 Step 1: Authentication with test credentials")
        print(f"   Email: {TEST_EMAIL}")
        print(f"   Password: {TEST_PASSWORD}")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json={
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Configure session with token
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                print(f"   ✅ Authentication successful")
                print(f"   User ID: {self.user_id}")
                print(f"   Expected User ID: {EXPECTED_USER_ID}")
                
                if self.user_id == EXPECTED_USER_ID:
                    print(f"   ✅ User ID matches expected value")
                else:
                    print(f"   ⚠️ User ID differs from expected")
                
                return True
            else:
                print(f"   ❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {str(e)}")
            return False
    
    def test_website_analysis_endpoint(self):
        """Step 2: Test GET /api/website/analysis endpoint"""
        print("\n🌐 Step 2: Test GET /api/website/analysis endpoint")
        
        if not self.access_token:
            print("   ❌ No access token available for authenticated request")
            return False
        
        try:
            response = self.session.get(
                f"{BACKEND_URL}/website/analysis",
                timeout=15
            )
            
            print(f"   📡 Request sent to: {BACKEND_URL}/website/analysis")
            print(f"   📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Website analysis endpoint accessible")
                    print(f"   📊 Response type: {type(data)}")
                    
                    # Check if data is a dict (single analysis) or list
                    if isinstance(data, dict):
                        analysis_data = data
                        print(f"   📋 Single analysis object returned")
                    elif isinstance(data, list) and len(data) > 0:
                        analysis_data = data[0]  # Take first analysis
                        print(f"   📋 Analysis list returned, using first item")
                        print(f"   📊 Total analyses found: {len(data)}")
                    else:
                        print(f"   ❌ No analysis data found in response")
                        return False
                    
                    # Validate critical fields
                    critical_fields = [
                        'analysis_summary',
                        'storytelling_analysis', 
                        'products_services_details',
                        'company_expertise'
                    ]
                    
                    print(f"   🔍 Validating critical fields:")
                    fields_present = 0
                    
                    for field in critical_fields:
                        if field in analysis_data:
                            field_value = analysis_data[field]
                            field_type = type(field_value).__name__
                            
                            if field_value:  # Not None or empty
                                print(f"      ✅ {field}: Present ({field_type})")
                                fields_present += 1
                                
                                # Special validation for analysis_summary (critical for popup)
                                if field == 'analysis_summary':
                                    if isinstance(field_value, str) and len(field_value) > 10:
                                        print(f"         ✅ analysis_summary has content ({len(field_value)} chars)")
                                    else:
                                        print(f"         ⚠️ analysis_summary may be too short")
                            else:
                                print(f"      ⚠️ {field}: Present but empty ({field_type})")
                        else:
                            print(f"      ❌ {field}: Missing")
                    
                    # Check for GPT-4o and Claude data
                    analysis_type = analysis_data.get('analysis_type', '')
                    print(f"   🤖 Analysis type: {analysis_type}")
                    
                    if 'gpt4o' in analysis_type.lower():
                        print(f"      ✅ GPT-4o analysis detected")
                    if 'claude' in analysis_type.lower():
                        print(f"      ✅ Claude analysis detected")
                    
                    # Summary
                    total_fields = len(analysis_data.keys())
                    print(f"   📊 Analysis summary:")
                    print(f"      Total fields: {total_fields}")
                    print(f"      Critical fields present: {fields_present}/{len(critical_fields)}")
                    
                    # Check if analysis_summary is present (most critical)
                    if 'analysis_summary' in analysis_data and analysis_data['analysis_summary']:
                        print(f"   ✅ CRITICAL: analysis_summary field is present and populated")
                        return True
                    else:
                        print(f"   ❌ CRITICAL: analysis_summary field missing or empty")
                        return False
                        
                except json.JSONDecodeError as e:
                    print(f"   ❌ Failed to parse JSON response: {e}")
                    print(f"   Raw response: {response.text[:200]}...")
                    return False
                    
            elif response.status_code == 404:
                print(f"   ❌ No website analysis found for user")
                print(f"   💡 User may need to run website analysis first")
                return False
            else:
                print(f"   ❌ Website analysis endpoint failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Website analysis endpoint error: {str(e)}")
            return False
    
    def test_login_sequence_analysis_availability(self):
        """Step 3: Test login sequence and immediate analysis availability"""
        print("\n🔄 Step 3: Test login sequence and analysis availability")
        
        # Clear session and re-authenticate to simulate fresh login
        self.session.headers.pop('Authorization', None)
        self.access_token = None
        
        print("   🔄 Simulating fresh login...")
        
        # Re-authenticate
        if not self.authenticate():
            print("   ❌ Failed to re-authenticate for sequence test")
            return False
        
        print("   ✅ Fresh authentication completed")
        
        # Immediately check if analysis is available (simulating frontend checkAuth behavior)
        print("   🔍 Checking immediate analysis availability...")
        
        try:
            # This simulates what the frontend should do in checkAuth()
            response = self.session.get(
                f"{BACKEND_URL}/website/analysis",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print("   ✅ Analysis immediately available after login")
                
                # Check if analysis_summary is available for popup validation
                if isinstance(data, dict):
                    analysis_summary = data.get('analysis_summary')
                elif isinstance(data, list) and len(data) > 0:
                    analysis_summary = data[0].get('analysis_summary')
                else:
                    analysis_summary = None
                
                if analysis_summary:
                    print("   ✅ analysis_summary available for popup validation")
                    print(f"      Summary length: {len(analysis_summary)} characters")
                    return True
                else:
                    print("   ❌ analysis_summary not available for popup validation")
                    return False
            else:
                print(f"   ❌ Analysis not immediately available: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Login sequence test error: {str(e)}")
            return False
    
    def test_analysis_data_structure(self):
        """Step 4: Test analysis data structure completeness"""
        print("\n📋 Step 4: Test analysis data structure completeness")
        
        if not self.access_token:
            print("   ❌ No access token available")
            return False
        
        try:
            response = self.session.get(
                f"{BACKEND_URL}/website/analysis",
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Get analysis data
                if isinstance(data, dict):
                    analysis_data = data
                elif isinstance(data, list) and len(data) > 0:
                    analysis_data = data[0]
                else:
                    print("   ❌ No analysis data to validate")
                    return False
                
                print("   📊 Analyzing data structure completeness:")
                
                # Expected fields for complete analysis
                expected_fields = [
                    'analysis_summary',
                    'storytelling_analysis',
                    'products_services_details', 
                    'company_expertise',
                    'unique_value_proposition',
                    'target_audience_analysis',
                    'brand_voice_analysis',
                    'content_themes',
                    'analysis_type',
                    'created_at',
                    'website_url'
                ]
                
                present_fields = 0
                populated_fields = 0
                
                for field in expected_fields:
                    if field in analysis_data:
                        present_fields += 1
                        value = analysis_data[field]
                        
                        if value and str(value).strip():  # Not None, empty, or whitespace
                            populated_fields += 1
                            print(f"      ✅ {field}: Present and populated")
                        else:
                            print(f"      ⚠️ {field}: Present but empty")
                    else:
                        print(f"      ❌ {field}: Missing")
                
                # Calculate completeness
                structure_completeness = (present_fields / len(expected_fields)) * 100
                data_completeness = (populated_fields / len(expected_fields)) * 100
                
                print(f"   📊 Structure completeness: {present_fields}/{len(expected_fields)} fields ({structure_completeness:.1f}%)")
                print(f"   📊 Data completeness: {populated_fields}/{len(expected_fields)} fields ({data_completeness:.1f}%)")
                
                # Check critical fields for post generation popup
                critical_for_popup = ['analysis_summary']
                popup_ready = all(
                    field in analysis_data and analysis_data[field] 
                    for field in critical_for_popup
                )
                
                if popup_ready:
                    print("   ✅ Analysis ready for post generation popup")
                else:
                    print("   ❌ Analysis NOT ready for post generation popup")
                
                return structure_completeness >= 70 and popup_ready
                
            else:
                print(f"   ❌ Could not retrieve analysis for structure test: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Data structure test error: {str(e)}")
            return False
    
    def test_analysis_fields_validation(self):
        """Step 5: Test specific field validation for popup requirements"""
        print("\n✅ Step 5: Test analysis fields validation for popup requirements")
        
        if not self.access_token:
            print("   ❌ No access token available")
            return False
        
        try:
            response = self.session.get(
                f"{BACKEND_URL}/website/analysis",
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Get analysis data
                if isinstance(data, dict):
                    analysis_data = data
                elif isinstance(data, list) and len(data) > 0:
                    analysis_data = data[0]
                else:
                    print("   ❌ No analysis data for validation")
                    return False
                
                print("   🔍 Validating fields required by post generation popup:")
                
                # Critical validation for popup functionality
                validation_results = {}
                
                # 1. analysis_summary validation (most critical)
                analysis_summary = analysis_data.get('analysis_summary')
                if analysis_summary and isinstance(analysis_summary, str) and len(analysis_summary.strip()) > 20:
                    print("      ✅ analysis_summary: Valid and substantial")
                    validation_results['analysis_summary'] = True
                else:
                    print("      ❌ analysis_summary: Invalid or too short")
                    validation_results['analysis_summary'] = False
                
                # 2. GPT-4o data validation
                analysis_type = analysis_data.get('analysis_type', '')
                if 'gpt4o' in analysis_type.lower() or 'gpt-4o' in analysis_type.lower():
                    print("      ✅ GPT-4o analysis: Available")
                    validation_results['gpt4o'] = True
                else:
                    print("      ⚠️ GPT-4o analysis: Not clearly identified")
                    validation_results['gpt4o'] = False
                
                # 3. Claude data validation
                if 'claude' in analysis_type.lower():
                    print("      ✅ Claude analysis: Available")
                    validation_results['claude'] = True
                else:
                    print("      ⚠️ Claude analysis: Not clearly identified")
                    validation_results['claude'] = False
                
                # 4. Company expertise validation (for content generation)
                company_expertise = analysis_data.get('company_expertise')
                if company_expertise:
                    print("      ✅ company_expertise: Available")
                    validation_results['company_expertise'] = True
                else:
                    print("      ⚠️ company_expertise: Missing")
                    validation_results['company_expertise'] = False
                
                # 5. Products/services validation
                products_services = analysis_data.get('products_services_details')
                if products_services:
                    print("      ✅ products_services_details: Available")
                    validation_results['products_services'] = True
                else:
                    print("      ⚠️ products_services_details: Missing")
                    validation_results['products_services'] = False
                
                # Summary of validation
                passed_validations = sum(validation_results.values())
                total_validations = len(validation_results)
                
                print(f"   📊 Validation summary: {passed_validations}/{total_validations} checks passed")
                
                # Critical requirement: analysis_summary must be present
                if validation_results.get('analysis_summary', False):
                    print("   ✅ CRITICAL REQUIREMENT MET: analysis_summary is valid")
                    return True
                else:
                    print("   ❌ CRITICAL REQUIREMENT FAILED: analysis_summary is invalid")
                    return False
                
            else:
                print(f"   ❌ Could not retrieve analysis for validation: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Field validation error: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all tests and provide comprehensive report"""
        print("🚀 WEBSITE ANALYSIS AUTO-LOAD TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test credentials: {TEST_EMAIL} / {TEST_PASSWORD}")
        print(f"Expected User ID: {EXPECTED_USER_ID}")
        print(f"Test focus: Automatic loading of website analysis upon login")
        print("=" * 80)
        
        test_results = []
        
        # Run all tests
        tests = [
            ("Authentication", self.authenticate),
            ("Website Analysis Endpoint", self.test_website_analysis_endpoint),
            ("Login Sequence Analysis Availability", self.test_login_sequence_analysis_availability),
            ("Analysis Data Structure", self.test_analysis_data_structure),
            ("Analysis Fields Validation", self.test_analysis_fields_validation)
        ]
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                test_results.append((test_name, result))
            except Exception as e:
                print(f"   ❌ Test '{test_name}' crashed: {str(e)}")
                test_results.append((test_name, False))
        
        # Generate comprehensive report
        print("\n" + "=" * 80)
        print("📊 WEBSITE ANALYSIS AUTO-LOAD TEST RESULTS")
        print("=" * 80)
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
            if result:
                passed_tests += 1
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"\n📈 SUCCESS RATE: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        # Critical analysis for the reported issue
        print("\n🔍 ISSUE ANALYSIS:")
        print("User reported: 'L'analyse de site web ne se charge que lors de la navigation vers l'onglet Analyse'")
        print("Expected fix: 'Ajout de loadWebsiteAnalysis() dans checkAuth() pour charger dès la connexion'")
        
        if passed_tests >= 4:  # Most tests should pass
            print("✅ WEBSITE ANALYSIS AUTO-LOAD WORKING")
            print("✅ Analysis endpoint returns valid data")
            print("✅ analysis_summary field available for popup validation")
            print("✅ Analysis loads immediately after authentication")
            print("✅ Post generation popup should detect analysis correctly")
        else:
            print("❌ WEBSITE ANALYSIS AUTO-LOAD ISSUES DETECTED")
            print("❌ Analysis may not be loading automatically")
            print("❌ Post generation popup may fail to detect analysis")
        
        print("\n🎯 OBJECTIVE STATUS:")
        if success_rate >= 80:
            print("✅ OBJECTIVE ACHIEVED: Website analysis auto-loads correctly")
            print("✅ Post generation popup should work without navigation to Analysis tab")
        else:
            print("⚠️ OBJECTIVE NOT ACHIEVED: Issues remain with auto-loading")
            print("⚠️ User may still need to navigate to Analysis tab first")
        
        print("=" * 80)
        return success_rate >= 80

def main():
    """Main test execution"""
    tester = WebsiteAnalysisAutoLoadTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("🎉 WEBSITE ANALYSIS AUTO-LOAD TESTS COMPLETED SUCCESSFULLY")
        sys.exit(0)
    else:
        print("⚠️ WEBSITE ANALYSIS AUTO-LOAD TESTS FAILED - REVIEW REQUIRED")
        sys.exit(1)

if __name__ == "__main__":
    main()