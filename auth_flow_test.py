#!/usr/bin/env python3
"""
CRITICAL AUTHENTICATION FLOW DEBUGGING TEST
Testing the specific authentication flow and business profile loading sequence 
that's preventing dashboard access as requested in review.
"""

import requests
import json
import os
from datetime import datetime

class AuthFlowTester:
    def __init__(self):
        # Use the production backend URL from frontend/.env
        with open('/app/frontend/.env', 'r') as f:
            env_content = f.read()
            for line in env_content.split('\n'):
                if line.startswith('REACT_APP_BACKEND_URL='):
                    self.base_url = line.split('=')[1].strip()
                    break
        
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        print(f"🔍 Testing Authentication Flow")
        print(f"Backend URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        print("=" * 80)

    def test_login_and_extract_token(self):
        """Test POST /api/auth/login with specific credentials and extract token"""
        print("\n🔐 STEP 1: Testing Login with lperpere@yahoo.fr / L@Reunion974!")
        
        login_data = {
            "email": "lperpere@yahoo.fr",
            "password": "L@Reunion974!"
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/auth/login",
                json=login_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"   ✅ Login successful!")
                print(f"   Response keys: {list(response_data.keys())}")
                
                if 'access_token' in response_data:
                    self.access_token = response_data['access_token']
                    print(f"   ✅ Access token extracted: {self.access_token[:20]}...")
                    print(f"   Token length: {len(self.access_token)} characters")
                    return True
                else:
                    print(f"   ❌ No access_token in response!")
                    print(f"   Response: {json.dumps(response_data, indent=2)}")
                    return False
            else:
                print(f"   ❌ Login failed with status {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error text: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Login request failed: {str(e)}")
            return False

    def test_business_profile_immediately_after_login(self):
        """IMMEDIATELY after login, test GET /api/business-profile with fresh token"""
        print("\n📋 STEP 2: Testing GET /api/business-profile IMMEDIATELY after login")
        
        if not self.access_token:
            print("   ❌ No access token available - cannot test business profile")
            return False
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.api_url}/business-profile",
                headers=headers
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Business profile retrieved successfully!")
                response_data = response.json()
                
                # Check data structure
                print(f"   Response keys: {list(response_data.keys())}")
                
                # Check for expected fields
                expected_fields = [
                    'business_name', 'business_type', 'business_description',
                    'target_audience', 'brand_tone', 'posting_frequency',
                    'preferred_platforms', 'budget_range', 'email', 'website_url'
                ]
                
                missing_fields = []
                present_fields = []
                
                for field in expected_fields:
                    if field in response_data:
                        present_fields.append(field)
                    else:
                        missing_fields.append(field)
                
                print(f"   ✅ Present fields ({len(present_fields)}): {present_fields}")
                if missing_fields:
                    print(f"   ⚠️ Missing fields ({len(missing_fields)}): {missing_fields}")
                
                # Check specific values
                business_name = response_data.get('business_name', '')
                business_type = response_data.get('business_type', '')
                email = response_data.get('email', '')
                
                print(f"   Business Name: '{business_name}'")
                print(f"   Business Type: '{business_type}'")
                print(f"   Email: '{email}'")
                
                # Critical check: Is this demo data or real user data?
                if business_name == "Demo Business" and email == "demo@claire-marcus.com":
                    print(f"   ❌ CRITICAL ISSUE: Returning demo data instead of user data!")
                    print(f"   This would cause frontend to redirect to onboarding instead of dashboard")
                    return False
                else:
                    print(f"   ✅ Returning real user data (not demo data)")
                    return True
                    
            elif response.status_code == 404:
                print(f"   ❌ CRITICAL ISSUE: Business profile returns 404!")
                print(f"   This would cause frontend to redirect to onboarding instead of dashboard")
                try:
                    error_data = response.json()
                    print(f"   Error response: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error text: {response.text}")
                return False
                
            else:
                print(f"   ❌ Unexpected status code: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error response: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error text: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Business profile request failed: {str(e)}")
            return False

    def test_auth_me_endpoint(self):
        """Test GET /api/auth/me to verify token validation"""
        print("\n👤 STEP 3: Testing GET /api/auth/me for token validation")
        
        if not self.access_token:
            print("   ❌ No access token available")
            return False
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.api_url}/auth/me",
                headers=headers
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"   ✅ Auth/me successful!")
                
                user_id = response_data.get('user_id', '')
                email = response_data.get('email', '')
                business_name = response_data.get('business_name', '')
                
                print(f"   User ID: {user_id}")
                print(f"   Email: {email}")
                print(f"   Business Name: {business_name}")
                
                # Check if this is demo data
                if user_id == "demo_user_id" and email == "demo@claire-marcus.com":
                    print(f"   ❌ CRITICAL: Token validation falling back to demo user!")
                    return False
                else:
                    print(f"   ✅ Token validation working correctly")
                    return True
                    
            else:
                print(f"   ❌ Auth/me failed with status {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error text: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Auth/me request failed: {str(e)}")
            return False

    def test_without_token(self):
        """Test business profile without token to verify fallback behavior"""
        print("\n🚫 STEP 4: Testing GET /api/business-profile WITHOUT token (fallback test)")
        
        try:
            response = requests.get(f"{self.api_url}/business-profile")
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                business_name = response_data.get('business_name', '')
                email = response_data.get('email', '')
                
                print(f"   Business Name: '{business_name}'")
                print(f"   Email: '{email}'")
                
                if business_name == "Demo Business" and email == "demo@claire-marcus.com":
                    print(f"   ✅ Correctly returns demo data when no token provided")
                    return True
                else:
                    print(f"   ⚠️ Unexpected data when no token provided")
                    return False
            else:
                print(f"   Status: {response.status_code} (may be expected)")
                return True
                
        except Exception as e:
            print(f"   ❌ Request failed: {str(e)}")
            return False

    def run_critical_debugging_sequence(self):
        """Run the critical debugging sequence as requested in review"""
        print("🎯 CRITICAL AUTHENTICATION FLOW DEBUGGING")
        print("Testing the specific sequence preventing dashboard access")
        print("=" * 80)
        
        results = []
        
        # Step 1: Login and extract token
        login_success = self.test_login_and_extract_token()
        results.append(("Login with lperpere@yahoo.fr", login_success))
        
        if login_success:
            # Step 2: IMMEDIATELY test business profile with fresh token
            profile_success = self.test_business_profile_immediately_after_login()
            results.append(("Business Profile with Fresh Token", profile_success))
            
            # Step 3: Test token validation
            auth_me_success = self.test_auth_me_endpoint()
            results.append(("Token Validation (/auth/me)", auth_me_success))
        
        # Step 4: Test fallback behavior
        fallback_success = self.test_without_token()
        results.append(("Fallback Behavior (No Token)", fallback_success))
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 CRITICAL DEBUGGING RESULTS SUMMARY")
        print("=" * 80)
        
        all_passed = True
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   {status} - {test_name}")
            if not success:
                all_passed = False
        
        print("\n" + "=" * 80)
        if all_passed:
            print("🎉 ALL TESTS PASSED - Authentication flow working correctly")
            print("   - Login successful with valid access_token")
            print("   - Business profile returns 200 (not 404)")
            print("   - Real user data returned (not demo data)")
            print("   - Token validation working properly")
        else:
            print("🚨 CRITICAL ISSUES FOUND:")
            for test_name, success in results:
                if not success:
                    print(f"   ❌ {test_name} - This could cause dashboard access issues")
        
        print("=" * 80)
        
        return all_passed

if __name__ == "__main__":
    tester = AuthFlowTester()
    success = tester.run_critical_debugging_sequence()
    exit(0 if success else 1)