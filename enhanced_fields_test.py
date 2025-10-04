#!/usr/bin/env python3
"""
Enhanced Fields Verification Test - Post-Correction
Testing specifically for the 6 new fields after main agent corrections
"""

import requests
import json
import time
from datetime import datetime

# Configuration from review request
BACKEND_URL = "https://claire-marcus-app-1.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}
TEST_WEBSITE = "https://myownwatch.fr"

class EnhancedFieldsTest:
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
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_enhanced_fields_presence(self):
        """Step 2: Test for presence of the 6 new enhanced fields"""
        print(f"\n🔍 Step 2: Enhanced Fields Presence Test")
        print(f"   Target website: {TEST_WEBSITE}")
        
        try:
            start_time = time.time()
            
            response = self.session.post(
                f"{BACKEND_URL}/website/analyze",
                json={"website_url": TEST_WEBSITE},
                timeout=120
            )
            
            analysis_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Website analysis completed in {analysis_time:.1f} seconds")
                
                # The 6 specific fields we need to verify
                required_new_fields = [
                    "products_services_details",
                    "company_expertise", 
                    "unique_value_proposition",
                    "analysis_depth",
                    "pages_analyzed_count",
                    "non_technical_pages_count"
                ]
                
                print(f"\n📋 Checking for 6 Required Enhanced Fields:")
                print("=" * 50)
                
                present_fields = []
                missing_fields = []
                
                for field in required_new_fields:
                    if field in data:
                        present_fields.append(field)
                        value = data[field]
                        
                        # Show field value details
                        if isinstance(value, str):
                            if len(value.strip()) > 0:
                                print(f"✅ {field}: Present ({len(value)} chars)")
                                if len(value) > 100:
                                    print(f"   Preview: {value[:100]}...")
                                else:
                                    print(f"   Content: {value}")
                            else:
                                print(f"⚠️ {field}: Present but empty")
                        elif isinstance(value, (int, float)):
                            print(f"✅ {field}: {value}")
                        elif isinstance(value, list):
                            print(f"✅ {field}: {len(value)} items")
                            if len(value) > 0:
                                print(f"   Items: {value[:3]}{'...' if len(value) > 3 else ''}")
                        else:
                            print(f"✅ {field}: {type(value)} - {value}")
                    else:
                        missing_fields.append(field)
                        print(f"❌ {field}: NOT FOUND")
                
                print(f"\n📊 ENHANCED FIELDS SUMMARY:")
                print(f"   ✅ Present: {len(present_fields)}/6")
                print(f"   ❌ Missing: {len(missing_fields)}/6")
                
                if len(present_fields) == 6:
                    print(f"\n🎉 SUCCESS: All 6 enhanced fields are present!")
                    success_rate = 100.0
                elif len(present_fields) > 0:
                    success_rate = (len(present_fields) / 6) * 100
                    print(f"\n⚠️ PARTIAL SUCCESS: {success_rate:.1f}% of enhanced fields present")
                    print(f"   Still missing: {', '.join(missing_fields)}")
                else:
                    success_rate = 0.0
                    print(f"\n❌ FAILURE: None of the enhanced fields are present")
                
                # Show all available fields for debugging
                print(f"\n🔍 DEBUG: All available fields in response:")
                all_fields = list(data.keys())
                print(f"   Total fields: {len(all_fields)}")
                for field in sorted(all_fields):
                    value = data[field]
                    if isinstance(value, str):
                        print(f"   • {field}: string ({len(value)} chars)")
                    elif isinstance(value, list):
                        print(f"   • {field}: list ({len(value)} items)")
                    else:
                        print(f"   • {field}: {type(value)} - {value}")
                
                return {
                    "success_rate": success_rate,
                    "present_fields": present_fields,
                    "missing_fields": missing_fields,
                    "response_data": data
                }
            else:
                print(f"❌ Website analysis failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Website analysis error: {str(e)}")
            return None
    
    def run_focused_test(self):
        """Run the focused enhanced fields test"""
        print("🎯 Enhanced Fields Verification Test - Post-Correction")
        print("=" * 60)
        print(f"Backend: {BACKEND_URL}")
        print(f"Test Website: {TEST_WEBSITE}")
        print(f"Credentials: {TEST_CREDENTIALS['email']}")
        print(f"Target: Verify 6 new enhanced fields are present")
        print("=" * 60)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Enhanced Fields Test
        result = self.test_enhanced_fields_presence()
        if not result:
            print("\n❌ CRITICAL: Website analysis failed")
            return False
        
        # Final summary
        print(f"\n📋 FINAL TEST RESULTS")
        print("=" * 40)
        
        success_rate = result["success_rate"]
        present_fields = result["present_fields"]
        missing_fields = result["missing_fields"]
        
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Fields Present: {len(present_fields)}/6")
        print(f"Fields Missing: {len(missing_fields)}/6")
        
        if success_rate == 100:
            print(f"\n🎉 TEST PASSED: All 6 enhanced fields are now present!")
            print(f"✅ The main agent's corrections were successful")
        elif success_rate >= 50:
            print(f"\n⚠️ TEST PARTIALLY PASSED: {success_rate:.1f}% of fields present")
            print(f"⚠️ Still need to implement: {', '.join(missing_fields)}")
        else:
            print(f"\n❌ TEST FAILED: Enhanced fields are still missing")
            print(f"❌ The corrections have not been implemented yet")
        
        return success_rate >= 50

if __name__ == "__main__":
    tester = EnhancedFieldsTest()
    success = tester.run_focused_test()
    
    if success:
        print(f"\n🎉 ENHANCED FIELDS TEST COMPLETED")
    else:
        print(f"\n💥 ENHANCED FIELDS TEST FAILED")