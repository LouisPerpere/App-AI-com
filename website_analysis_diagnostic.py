#!/usr/bin/env python3
"""
Website Analysis Diagnostic Test
Specifically designed to diagnose the critical issue where POST /api/website/analyze
empties ALL fields in the "Entreprise" page frontend.
"""

import requests
import json
import os
from datetime import datetime

class WebsiteAnalysisDiagnostic:
    def __init__(self):
        # Use the frontend environment URL for testing
        with open('/app/frontend/.env', 'r') as f:
            env_content = f.read()
            for line in env_content.split('\n'):
                if line.startswith('REACT_APP_BACKEND_URL='):
                    self.base_url = line.split('=')[1].strip()
                    break
            else:
                self.base_url = "http://localhost:8001"
            
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        self.business_profile_before = None
        self.business_profile_after = None
        self.analysis_response = None
        
        print(f"🔍 Website Analysis Diagnostic Tool")
        print(f"Backend URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        print("=" * 60)

    def authenticate(self):
        """Authenticate with the specified credentials"""
        login_data = {
            "email": "lperpere@yahoo.fr",
            "password": "L@Reunion974!"
        }
        
        print("🔐 Authenticating with lperpere@yahoo.fr...")
        
        try:
            response = requests.post(f"{self.api_url}/auth/login", json=login_data)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                print(f"   ✅ Authentication successful")
                print(f"   Token: {self.access_token[:20]}..." if self.access_token else "   ❌ No token received")
                return True
            else:
                print(f"   ❌ Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {e}")
            return False

    def get_business_profile(self, label=""):
        """Get current business profile"""
        if not self.access_token:
            print("❌ No access token available")
            return None
            
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        try:
            response = requests.get(f"{self.api_url}/business-profile", headers=headers)
            print(f"📊 Getting Business Profile {label}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Profile retrieved successfully")
                
                # Print key fields for comparison
                key_fields = ['business_name', 'business_type', 'business_description', 
                             'target_audience', 'email', 'website_url']
                for field in key_fields:
                    value = data.get(field, 'N/A')
                    print(f"   {field}: {value}")
                
                return data
            else:
                print(f"   ❌ Failed to get profile: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error getting profile: {e}")
            return None

    def analyze_website(self):
        """Test POST /api/website/analyze with specified parameters"""
        if not self.access_token:
            print("❌ No access token available")
            return None
            
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        # Test data as specified in the request
        analysis_data = {
            "website_url": "https://example.com"
        }
        
        print("🌐 Testing POST /api/website/analyze")
        print(f"   URL: {self.api_url}/website/analyze")
        print(f"   Data: {json.dumps(analysis_data, indent=2)}")
        
        try:
            response = requests.post(f"{self.api_url}/website/analyze", 
                                   json=analysis_data, headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Analysis completed successfully")
                print(f"   Response structure:")
                
                # Analyze the complete response
                self._analyze_response_structure(data)
                
                return data
            else:
                print(f"   ❌ Analysis failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Analysis error: {e}")
            return None

    def _analyze_response_structure(self, data):
        """Analyze the response structure in detail"""
        print("   📋 COMPLETE RESPONSE ANALYSIS:")
        print("   " + "="*50)
        
        # Print the full response
        response_str = json.dumps(data, indent=4)
        print(f"   Full Response:\n{response_str}")
        
        # Look for specific patterns that might cause issues
        suspicious_patterns = []
        
        # Check for business profile related data
        business_fields = ['business_name', 'business_type', 'business_description', 
                          'target_audience', 'email', 'website_url', 'hashtags_primary', 
                          'hashtags_secondary', 'brand_tone', 'posting_frequency']
        
        for field in business_fields:
            if field in response_str.lower():
                suspicious_patterns.append(f"Contains business field reference: {field}")
        
        # Check for empty values or null values
        if 'null' in response_str or '""' in response_str or 'None' in response_str:
            suspicious_patterns.append("Contains null/empty values")
        
        # Check for profile/user data
        if 'profile' in response_str.lower() or 'user' in response_str.lower():
            suspicious_patterns.append("Contains profile/user references")
        
        # Check for update/modify commands
        update_keywords = ['update', 'modify', 'change', 'set', 'clear', 'reset']
        for keyword in update_keywords:
            if keyword in response_str.lower():
                suspicious_patterns.append(f"Contains update keyword: {keyword}")
        
        if suspicious_patterns:
            print("   ⚠️  SUSPICIOUS PATTERNS DETECTED:")
            for pattern in suspicious_patterns:
                print(f"      - {pattern}")
        else:
            print("   ✅ No obvious suspicious patterns detected")
        
        print("   " + "="*50)

    def compare_profiles(self):
        """Compare business profiles before and after analysis"""
        if not self.business_profile_before or not self.business_profile_after:
            print("❌ Cannot compare - missing profile data")
            return
        
        print("🔍 COMPARING BUSINESS PROFILES BEFORE/AFTER ANALYSIS")
        print("=" * 60)
        
        # Compare all fields
        all_fields = set(self.business_profile_before.keys()) | set(self.business_profile_after.keys())
        changes_detected = False
        
        for field in sorted(all_fields):
            before_value = self.business_profile_before.get(field, 'MISSING')
            after_value = self.business_profile_after.get(field, 'MISSING')
            
            if before_value != after_value:
                changes_detected = True
                print(f"❌ CHANGE DETECTED in {field}:")
                print(f"   Before: {before_value}")
                print(f"   After:  {after_value}")
            else:
                print(f"✅ {field}: No change")
        
        if not changes_detected:
            print("✅ NO CHANGES DETECTED in business profile")
        else:
            print("❌ CRITICAL: Business profile data changed after website analysis!")
        
        print("=" * 60)

    def test_side_effects(self):
        """Test for any side effects that might cause field clearing"""
        print("🔬 TESTING FOR SIDE EFFECTS")
        print("=" * 40)
        
        # Test if analysis affects other endpoints
        if not self.access_token:
            print("❌ No access token available")
            return
            
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        # Test various endpoints that might be affected
        test_endpoints = [
            ("GET /api/auth/me", "auth/me"),
            ("GET /api/notes", "notes"),
            ("GET /api/bibliotheque", "bibliotheque")
        ]
        
        for endpoint_name, endpoint_path in test_endpoints:
            try:
                response = requests.get(f"{self.api_url}/{endpoint_path}", headers=headers)
                print(f"   {endpoint_name}: Status {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    # Look for any business profile data in the response
                    response_str = json.dumps(data).lower()
                    if any(field in response_str for field in ['business_name', 'business_type', 'email']):
                        print(f"      ⚠️  Contains business profile data")
                    else:
                        print(f"      ✅ No business profile data")
                else:
                    print(f"      ❌ Failed: {response.text[:100]}")
                    
            except Exception as e:
                print(f"   {endpoint_name}: Error - {e}")

    def run_diagnostic(self):
        """Run the complete diagnostic sequence"""
        print("🚀 STARTING WEBSITE ANALYSIS DIAGNOSTIC")
        print("=" * 60)
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ DIAGNOSTIC FAILED: Cannot authenticate")
            return False
        
        # Step 2: Get business profile BEFORE analysis
        print("\n" + "="*60)
        self.business_profile_before = self.get_business_profile("(BEFORE ANALYSIS)")
        if not self.business_profile_before:
            print("❌ DIAGNOSTIC FAILED: Cannot get initial business profile")
            return False
        
        # Step 3: Perform website analysis
        print("\n" + "="*60)
        self.analysis_response = self.analyze_website()
        if not self.analysis_response:
            print("❌ DIAGNOSTIC FAILED: Website analysis failed")
            return False
        
        # Step 4: Get business profile AFTER analysis
        print("\n" + "="*60)
        self.business_profile_after = self.get_business_profile("(AFTER ANALYSIS)")
        if not self.business_profile_after:
            print("❌ DIAGNOSTIC FAILED: Cannot get post-analysis business profile")
            return False
        
        # Step 5: Compare profiles
        print("\n" + "="*60)
        self.compare_profiles()
        
        # Step 6: Test for side effects
        print("\n" + "="*60)
        self.test_side_effects()
        
        # Step 7: Final analysis
        print("\n" + "="*60)
        self.final_analysis()
        
        return True

    def final_analysis(self):
        """Provide final analysis and recommendations"""
        print("📋 FINAL DIAGNOSTIC ANALYSIS")
        print("=" * 60)
        
        # Check if the issue is reproduced
        profiles_changed = self.business_profile_before != self.business_profile_after
        
        if profiles_changed:
            print("❌ CRITICAL ISSUE CONFIRMED:")
            print("   Business profile data changed after website analysis")
            print("   This explains why frontend fields appear to be 'emptied'")
            
            # Identify the root cause
            print("\n🔍 ROOT CAUSE ANALYSIS:")
            
            # Check if it's a demo mode issue
            if (self.business_profile_after.get('business_name') == 'Demo Business' and
                self.business_profile_after.get('email') == 'demo@claire-marcus.com'):
                print("   ✅ ROOT CAUSE IDENTIFIED: Demo mode hardcoded responses")
                print("   The backend is returning hardcoded demo data instead of user data")
                print("   This makes it appear that user data is 'erased' when it's actually")
                print("   just being overwritten by demo responses")
            
            # Check for other patterns
            elif all(not value or value == "" for value in self.business_profile_after.values() if isinstance(value, str)):
                print("   ✅ ROOT CAUSE IDENTIFIED: Fields actually being cleared")
                print("   The analysis endpoint is somehow clearing the business profile data")
            
            else:
                print("   ⚠️  ROOT CAUSE UNCLEAR: Data changed but pattern not recognized")
        
        else:
            print("✅ NO ISSUE DETECTED:")
            print("   Business profile data remained unchanged after website analysis")
            print("   The reported issue may be frontend-specific or intermittent")
        
        print("\n💡 RECOMMENDATIONS:")
        
        if profiles_changed:
            print("   1. Fix backend to return actual user data instead of demo data")
            print("   2. Ensure website analysis doesn't modify business profile")
            print("   3. Add proper data persistence for business profile updates")
            print("   4. Test with real database instead of demo mode")
        else:
            print("   1. Test with different user accounts and data")
            print("   2. Check frontend state management after API calls")
            print("   3. Monitor network requests in browser developer tools")
            print("   4. Test with various website URLs and parameters")
        
        print("\n📊 ANALYSIS RESPONSE SUMMARY:")
        if self.analysis_response:
            print(f"   Response contains {len(self.analysis_response)} fields")
            print(f"   Response size: {len(json.dumps(self.analysis_response))} characters")
            
            # Check if response contains business profile data
            response_str = json.dumps(self.analysis_response).lower()
            business_fields_in_response = [field for field in ['business_name', 'business_type', 'email', 'website_url'] 
                                         if field in response_str]
            if business_fields_in_response:
                print(f"   ⚠️  Response contains business fields: {business_fields_in_response}")
            else:
                print("   ✅ Response doesn't contain business profile fields")
        
        print("=" * 60)

if __name__ == "__main__":
    diagnostic = WebsiteAnalysisDiagnostic()
    diagnostic.run_diagnostic()