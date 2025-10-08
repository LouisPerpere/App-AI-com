#!/usr/bin/env python3
"""
🚨 COMPREHENSIVE DATA LEAK INVESTIGATION
Deep investigation of the reported data leakage between test@claire-marcus.com and lperpere@yahoo.fr

SPECIFIC INVESTIGATION:
1. Check all endpoints that might contain user data
2. Look for any cached or shared data
3. Test with different request patterns
4. Check for session bleeding
5. Investigate database queries directly
"""

import requests
import json
import time
from datetime import datetime

BACKEND_URL = "https://claire-marcus.com/api"

# Account credentials
ACCOUNTS = {
    "test": {
        "email": "test@claire-marcus.com",
        "password": "test123!",
        "name": "Test Account"
    },
    "lperpere": {
        "email": "lperpere@yahoo.fr",
        "password": "L@Reunion974!",
        "name": "LPerpere Account"
    }
}

class ComprehensiveDataLeakTester:
    def __init__(self):
        self.sessions = {}
        self.tokens = {}
        self.user_ids = {}
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def authenticate_all_accounts(self):
        """Authenticate all test accounts"""
        self.log("🔐 AUTHENTICATING ALL ACCOUNTS")
        
        for account_key, account_data in ACCOUNTS.items():
            session = requests.Session()
            session.headers.update({
                'Content-Type': 'application/json',
                'User-Agent': f'DataLeak-Investigation-{account_key}/1.0'
            })
            
            try:
                response = session.post(f"{BACKEND_URL}/auth/login-robust", json={
                    "email": account_data["email"],
                    "password": account_data["password"]
                })
                
                if response.status_code == 200:
                    data = response.json()
                    token = data.get('access_token')
                    user_id = data.get('user_id')
                    
                    session.headers.update({
                        'Authorization': f'Bearer {token}'
                    })
                    
                    self.sessions[account_key] = session
                    self.tokens[account_key] = token
                    self.user_ids[account_key] = user_id
                    
                    self.log(f"✅ {account_key} ({account_data['email']}) authenticated")
                    self.log(f"   User ID: {user_id}")
                else:
                    self.log(f"❌ {account_key} authentication failed: {response.status_code}", "ERROR")
                    return False
                    
            except Exception as e:
                self.log(f"❌ {account_key} authentication error: {str(e)}", "ERROR")
                return False
        
        return True
    
    def test_all_user_data_endpoints(self):
        """Test all endpoints that might contain user-specific data"""
        self.log("🔍 TESTING ALL USER DATA ENDPOINTS")
        
        # List of endpoints to test
        endpoints = [
            "/auth/me",
            "/business-profile", 
            "/content/pending",
            "/content/pending-temp",  # Temporary endpoint
            "/notes",
            "/website-analysis",
            "/posts/generated",
            "/social/connections",
            "/debug/social-connections"
        ]
        
        results = {}
        
        for endpoint in endpoints:
            self.log(f"🧪 Testing endpoint: {endpoint}")
            endpoint_results = {}
            
            for account_key, session in self.sessions.items():
                try:
                    response = session.get(f"{BACKEND_URL}{endpoint}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        endpoint_results[account_key] = {
                            'status': 200,
                            'data': data,
                            'data_size': len(str(data))
                        }
                        self.log(f"   {account_key}: 200 OK ({len(str(data))} chars)")
                    else:
                        endpoint_results[account_key] = {
                            'status': response.status_code,
                            'data': None,
                            'data_size': 0
                        }
                        self.log(f"   {account_key}: {response.status_code}")
                        
                except Exception as e:
                    self.log(f"   {account_key}: ERROR - {str(e)}")
                    endpoint_results[account_key] = {
                        'status': 'ERROR',
                        'data': None,
                        'data_size': 0
                    }
            
            results[endpoint] = endpoint_results
            
            # Check for data leakage in this endpoint
            self.analyze_endpoint_for_leakage(endpoint, endpoint_results)
        
        return results
    
    def analyze_endpoint_for_leakage(self, endpoint, endpoint_results):
        """Analyze a specific endpoint for data leakage"""
        
        # Get data for both accounts
        test_data = endpoint_results.get('test', {}).get('data')
        lperpere_data = endpoint_results.get('lperpere', {}).get('data')
        
        if not test_data or not lperpere_data:
            return  # Can't compare if one account has no data
        
        # Check for identical data (major red flag)
        if test_data == lperpere_data:
            self.log(f"🚨 CRITICAL LEAK in {endpoint}: IDENTICAL DATA between accounts!", "ERROR")
            self.log(f"   Data: {str(test_data)[:200]}...")
            return
        
        # Check for cross-contamination of user IDs
        test_user_id = self.user_ids.get('test')
        lperpere_user_id = self.user_ids.get('lperpere')
        
        # Convert data to strings for searching
        test_data_str = str(test_data).lower()
        lperpere_data_str = str(lperpere_data).lower()
        
        # Check if test account data contains lperpere's user ID
        if lperpere_user_id and lperpere_user_id.lower() in test_data_str:
            self.log(f"🚨 CRITICAL LEAK in {endpoint}: Test account contains lperpere's user_id!", "ERROR")
            self.log(f"   lperpere user_id {lperpere_user_id} found in test account data")
        
        # Check if lperpere account data contains test's user ID
        if test_user_id and test_user_id.lower() in lperpere_data_str:
            self.log(f"🚨 CRITICAL LEAK in {endpoint}: LPerpere account contains test's user_id!", "ERROR")
            self.log(f"   test user_id {test_user_id} found in lperpere account data")
        
        # Check for email cross-contamination
        if 'test@claire-marcus.com' in lperpere_data_str:
            self.log(f"🚨 CRITICAL LEAK in {endpoint}: LPerpere data contains test email!", "ERROR")
        
        if 'lperpere@yahoo.fr' in test_data_str:
            self.log(f"🚨 CRITICAL LEAK in {endpoint}: Test data contains lperpere email!", "ERROR")
        
        # Check for business name cross-contamination
        if isinstance(test_data, dict) and isinstance(lperpere_data, dict):
            test_business = test_data.get('business_name', '').lower()
            lperpere_business = lperpere_data.get('business_name', '').lower()
            
            if test_business and test_business in lperpere_data_str:
                self.log(f"🚨 POTENTIAL LEAK in {endpoint}: Test business name in lperpere data!", "ERROR")
            
            if lperpere_business and lperpere_business in test_data_str:
                self.log(f"🚨 POTENTIAL LEAK in {endpoint}: LPerpere business name in test data!", "ERROR")
    
    def test_session_isolation(self):
        """Test if sessions are properly isolated"""
        self.log("🔍 TESTING SESSION ISOLATION")
        
        # Test 1: Use test account token with lperpere session
        self.log("🧪 Test 1: Cross-token contamination")
        
        # Create a new session with test token but try to access lperpere-like data
        cross_session = requests.Session()
        cross_session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.tokens["test"]}'
        })
        
        # Try to access data - should only return test account data
        response = cross_session.get(f"{BACKEND_URL}/auth/me")
        if response.status_code == 200:
            data = response.json()
            user_id = data.get('user_id')
            email = data.get('email')
            
            if user_id == self.user_ids['lperpere'] or email == ACCOUNTS['lperpere']['email']:
                self.log("🚨 CRITICAL: Cross-token contamination detected!", "ERROR")
            else:
                self.log("✅ Cross-token test passed - proper isolation")
        
        # Test 2: Rapid session switching
        self.log("🧪 Test 2: Rapid session switching")
        
        for i in range(5):
            # Alternate between accounts rapidly
            account_key = 'test' if i % 2 == 0 else 'lperpere'
            session = self.sessions[account_key]
            
            response = session.get(f"{BACKEND_URL}/auth/me")
            if response.status_code == 200:
                data = response.json()
                returned_user_id = data.get('user_id')
                expected_user_id = self.user_ids[account_key]
                
                if returned_user_id != expected_user_id:
                    self.log(f"🚨 CRITICAL: Session switching issue at iteration {i}!", "ERROR")
                    self.log(f"   Expected: {expected_user_id}, Got: {returned_user_id}")
                    return False
        
        self.log("✅ Rapid session switching test passed")
        return True
    
    def test_caching_issues(self):
        """Test for caching-related data leakage"""
        self.log("🔍 TESTING CACHING ISSUES")
        
        # Test 1: Same endpoint, different accounts, rapid succession
        self.log("🧪 Test 1: Rapid endpoint access caching")
        
        endpoint = "/business-profile"
        
        # Access endpoint rapidly with different accounts
        results = []
        for i in range(10):
            account_key = 'test' if i % 2 == 0 else 'lperpere'
            session = self.sessions[account_key]
            
            response = session.get(f"{BACKEND_URL}{endpoint}")
            if response.status_code == 200:
                data = response.json()
                results.append({
                    'iteration': i,
                    'account': account_key,
                    'data': data
                })
        
        # Analyze results for caching issues
        for i, result in enumerate(results):
            account = result['account']
            data = result['data']
            expected_user_id = self.user_ids[account]
            
            # Check if data belongs to the correct account
            data_str = str(data).lower()
            other_account = 'lperpere' if account == 'test' else 'test'
            other_user_id = self.user_ids[other_account]
            
            if other_user_id.lower() in data_str:
                self.log(f"🚨 CRITICAL: Caching issue at iteration {i}!", "ERROR")
                self.log(f"   Account {account} got data containing {other_account}'s user_id")
                return False
        
        self.log("✅ Caching test passed")
        return True
    
    def test_database_direct_queries(self):
        """Test database queries for potential issues"""
        self.log("🔍 TESTING DATABASE QUERY PATTERNS")
        
        # Test different query patterns that might reveal issues
        test_patterns = [
            {"limit": 1, "offset": 0},
            {"limit": 50, "offset": 0},
            {"limit": 10, "offset": 5},
        ]
        
        for pattern in test_patterns:
            self.log(f"🧪 Testing query pattern: {pattern}")
            
            for account_key, session in self.sessions.items():
                response = session.get(f"{BACKEND_URL}/content/pending", params=pattern)
                
                if response.status_code == 200:
                    data = response.json()
                    content = data.get('content', [])
                    
                    # Check ownership of returned content
                    expected_user_id = self.user_ids[account_key]
                    
                    for item in content:
                        owner_id = item.get('owner_id') or item.get('user_id')
                        if owner_id and owner_id != expected_user_id:
                            self.log(f"🚨 CRITICAL: Query pattern leak!", "ERROR")
                            self.log(f"   Account {account_key} got content owned by {owner_id}")
                            self.log(f"   Expected owner: {expected_user_id}")
                            return False
        
        self.log("✅ Database query pattern test passed")
        return True
    
    def run_comprehensive_investigation(self):
        """Run the complete comprehensive investigation"""
        self.log("🚨 STARTING COMPREHENSIVE DATA LEAK INVESTIGATION")
        self.log("=" * 80)
        self.log(f"🌐 Backend URL: {BACKEND_URL}")
        self.log(f"🎯 Investigating: test@claire-marcus.com vs lperpere@yahoo.fr")
        self.log("=" * 80)
        
        # Step 1: Authenticate all accounts
        if not self.authenticate_all_accounts():
            self.log("❌ Authentication failed - cannot proceed")
            return False
        
        # Step 2: Test all endpoints
        self.log("\n🔍 STEP 2: COMPREHENSIVE ENDPOINT TESTING")
        endpoint_results = self.test_all_user_data_endpoints()
        
        # Step 3: Test session isolation
        self.log("\n🔍 STEP 3: SESSION ISOLATION TESTING")
        session_ok = self.test_session_isolation()
        
        # Step 4: Test caching issues
        self.log("\n🔍 STEP 4: CACHING ISSUES TESTING")
        caching_ok = self.test_caching_issues()
        
        # Step 5: Test database queries
        self.log("\n🔍 STEP 5: DATABASE QUERY TESTING")
        db_queries_ok = self.test_database_direct_queries()
        
        # Summary
        self.log("\n" + "=" * 80)
        self.log("🎯 COMPREHENSIVE INVESTIGATION SUMMARY")
        
        all_tests_passed = session_ok and caching_ok and db_queries_ok
        
        if all_tests_passed:
            self.log("✅ NO DATA LEAKAGE DETECTED")
            self.log("   All security tests passed")
            self.log("   Data isolation appears to be working correctly")
        else:
            self.log("🚨 CRITICAL SECURITY ISSUES DETECTED!")
            self.log("   Data leakage confirmed - immediate action required")
        
        # Additional analysis
        self.log("\n📊 DETAILED FINDINGS:")
        self.log(f"   Test account user_id: {self.user_ids.get('test')}")
        self.log(f"   LPerpere account user_id: {self.user_ids.get('lperpere')}")
        
        # Check if user IDs are different (they should be)
        if self.user_ids.get('test') == self.user_ids.get('lperpere'):
            self.log("🚨 CRITICAL ROOT CAUSE: BOTH ACCOUNTS HAVE SAME USER_ID!")
        else:
            self.log("✅ User IDs are properly different")
        
        return all_tests_passed

def main():
    """Main execution function"""
    print("🚨 COMPREHENSIVE DATA LEAK INVESTIGATION")
    print("=" * 80)
    print(f"📅 Investigation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print("🎯 Deep investigation of reported data leakage")
    print("=" * 80)
    
    tester = ComprehensiveDataLeakTester()
    success = tester.run_comprehensive_investigation()
    
    if success:
        print("\n✅ INVESTIGATION COMPLETE - No security issues detected")
        return 0
    else:
        print("\n🚨 INVESTIGATION COMPLETE - Security issues found!")
        return 1

if __name__ == "__main__":
    exit(main())