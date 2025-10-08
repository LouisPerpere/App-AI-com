#!/usr/bin/env python3
"""
🚨 CRITICAL SECURITY INVESTIGATION - User Data Isolation Testing
URGENT: Data leakage between user accounts - test@claire-marcus.com seeing lperpere@yahoo.fr data

SECURITY ISSUE REPORTED:
- User test@claire-marcus.com is seeing website analysis and photos from lperpere@yahoo.fr account
- This is a CRITICAL privacy violation and data breach

INVESTIGATION OBJECTIVES:
1. Test authentication isolation between accounts
2. Verify GET /api/website-analysis returns only user-specific data
3. Verify GET /api/content/pending returns only user-specific data
4. Check for JWT token validation issues
5. Identify root cause of data cross-contamination
6. Test database query filters for user_id isolation

LIVE URL: https://claire-marcus.com/api
"""

import requests
import json
import time
import sys
from datetime import datetime
import traceback

# Configuration
BACKEND_URL = "https://claire-marcus.com/api"

# Test accounts - use the actual reported accounts
ACCOUNT_1 = {
    "email": "test@claire-marcus.com",
    "password": "test123!",  # User provided password
    "name": "Test Account"
}

ACCOUNT_2 = {
    "email": "lperpere@yahoo.fr", 
    "password": "L@Reunion974!",
    "name": "LPerpere Account"
}

class UserDataIsolationTester:
    def __init__(self):
        self.session_1 = requests.Session()
        self.session_2 = requests.Session()
        
        # Configure sessions
        for session in [self.session_1, self.session_2]:
            session.headers.update({
                'Content-Type': 'application/json',
                'User-Agent': 'Security-Data-Isolation-Test/1.0'
            })
        
        self.account_1_token = None
        self.account_1_user_id = None
        self.account_2_token = None
        self.account_2_user_id = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def authenticate_account(self, account, session, account_name):
        """Authenticate a specific account, try to register if login fails"""
        self.log(f"🔐 Authenticating {account_name}: {account['email']}")
        
        try:
            response = session.post(f"{BACKEND_URL}/auth/login-robust", json={
                "email": account["email"],
                "password": account["password"]
            })
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_id = data.get('user_id')
                
                # Set authorization header
                session.headers.update({
                    'Authorization': f'Bearer {token}'
                })
                
                self.log(f"✅ {account_name} authentication successful")
                self.log(f"   User ID: {user_id}")
                self.log(f"   Token: {token[:20]}..." if token else "   Token: None")
                
                return token, user_id
            elif response.status_code == 401:
                # Try to register the account if login fails
                self.log(f"⚠️ {account_name} login failed, attempting registration")
                
                register_response = session.post(f"{BACKEND_URL}/auth/register", json={
                    "email": account["email"],
                    "password": account["password"],
                    "first_name": "Test",
                    "last_name": "User",
                    "business_name": f"Test Business {account_name}"
                })
                
                if register_response.status_code == 200:
                    reg_data = register_response.json()
                    token = reg_data.get('access_token')
                    user_id = reg_data.get('user_id')
                    
                    # Set authorization header
                    session.headers.update({
                        'Authorization': f'Bearer {token}'
                    })
                    
                    self.log(f"✅ {account_name} registration and authentication successful")
                    self.log(f"   User ID: {user_id}")
                    self.log(f"   Token: {token[:20]}..." if token else "   Token: None")
                    
                    return token, user_id
                else:
                    self.log(f"❌ {account_name} registration failed: {register_response.status_code} - {register_response.text}", "ERROR")
                    return None, None
            else:
                self.log(f"❌ {account_name} authentication failed: {response.status_code} - {response.text}", "ERROR")
                return None, None
                
        except Exception as e:
            self.log(f"❌ {account_name} authentication error: {str(e)}", "ERROR")
            return None, None
    
    def test_website_analysis_isolation(self):
        """Test website analysis data isolation between accounts"""
        self.log("🔍 TESTING WEBSITE ANALYSIS DATA ISOLATION")
        
        try:
            # Get website analysis for Account 1
            self.log("📊 Getting website analysis for Account 1 (test@claire-marcus.com)")
            response_1 = self.session_1.get(f"{BACKEND_URL}/website-analysis")
            
            if response_1.status_code == 200:
                data_1 = response_1.json()
                self.log(f"✅ Account 1 website analysis retrieved successfully")
                self.log(f"   Data keys: {list(data_1.keys()) if isinstance(data_1, dict) else 'Not a dict'}")
                
                # Check for user-specific identifiers
                if isinstance(data_1, dict):
                    user_id_in_data_1 = data_1.get('user_id') or data_1.get('owner_id')
                    if user_id_in_data_1:
                        self.log(f"   User ID in data: {user_id_in_data_1}")
                        if user_id_in_data_1 == self.account_1_user_id:
                            self.log("   ✅ User ID matches Account 1")
                        else:
                            self.log("   🚨 CRITICAL: User ID does NOT match Account 1!")
                            self.log(f"   Expected: {self.account_1_user_id}, Found: {user_id_in_data_1}")
                    else:
                        self.log("   ⚠️ No user_id field found in website analysis data")
                        
            elif response_1.status_code == 404:
                self.log("   ℹ️ No website analysis data for Account 1")
                data_1 = None
            else:
                self.log(f"   ❌ Account 1 website analysis failed: {response_1.status_code} - {response_1.text}")
                data_1 = None
            
            # Get website analysis for Account 2
            self.log("📊 Getting website analysis for Account 2 (lperpere@yahoo.fr)")
            response_2 = self.session_2.get(f"{BACKEND_URL}/website-analysis")
            
            if response_2.status_code == 200:
                data_2 = response_2.json()
                self.log(f"✅ Account 2 website analysis retrieved successfully")
                self.log(f"   Data keys: {list(data_2.keys()) if isinstance(data_2, dict) else 'Not a dict'}")
                
                # Check for user-specific identifiers
                if isinstance(data_2, dict):
                    user_id_in_data_2 = data_2.get('user_id') or data_2.get('owner_id')
                    if user_id_in_data_2:
                        self.log(f"   User ID in data: {user_id_in_data_2}")
                        if user_id_in_data_2 == self.account_2_user_id:
                            self.log("   ✅ User ID matches Account 2")
                        else:
                            self.log("   🚨 CRITICAL: User ID does NOT match Account 2!")
                            self.log(f"   Expected: {self.account_2_user_id}, Found: {user_id_in_data_2}")
                    else:
                        self.log("   ⚠️ No user_id field found in website analysis data")
                        
            elif response_2.status_code == 404:
                self.log("   ℹ️ No website analysis data for Account 2")
                data_2 = None
            else:
                self.log(f"   ❌ Account 2 website analysis failed: {response_2.status_code} - {response_2.text}")
                data_2 = None
            
            # CRITICAL SECURITY CHECK: Compare data between accounts
            if data_1 and data_2:
                self.log("🔍 CRITICAL SECURITY CHECK: Comparing website analysis data between accounts")
                
                # Check if data is identical (which would indicate data leakage)
                if data_1 == data_2:
                    self.log("🚨 CRITICAL SECURITY BREACH: Website analysis data is IDENTICAL between accounts!")
                    self.log("   This confirms the reported data leakage issue")
                    return False
                else:
                    self.log("✅ Website analysis data is different between accounts (good)")
                    
                # Check for cross-contamination of user IDs
                user_id_1 = data_1.get('user_id') or data_1.get('owner_id')
                user_id_2 = data_2.get('user_id') or data_2.get('owner_id')
                
                if user_id_1 and user_id_2:
                    if user_id_1 == user_id_2:
                        self.log("🚨 CRITICAL: Both accounts have same user_id in website analysis data!")
                        return False
                    elif user_id_1 == self.account_2_user_id or user_id_2 == self.account_1_user_id:
                        self.log("🚨 CRITICAL: Cross-contamination detected - Account 1 has Account 2's data or vice versa!")
                        return False
                    else:
                        self.log("✅ User IDs are properly isolated")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Website analysis isolation test error: {str(e)}", "ERROR")
            self.log(f"   Traceback: {traceback.format_exc()}")
            return False
    
    def test_content_isolation(self):
        """Test content/media data isolation between accounts"""
        self.log("🔍 TESTING CONTENT/MEDIA DATA ISOLATION")
        
        try:
            # Get content for Account 1
            self.log("📁 Getting content for Account 1 (test@claire-marcus.com)")
            response_1 = self.session_1.get(f"{BACKEND_URL}/content/pending", params={"limit": 50})
            
            if response_1.status_code == 200:
                data_1 = response_1.json()
                content_1 = data_1.get('content', [])
                self.log(f"✅ Account 1 content retrieved: {len(content_1)} items")
                
                # Check user ownership in content items
                if content_1:
                    sample_item = content_1[0]
                    self.log(f"   Sample item keys: {list(sample_item.keys())}")
                    
                    # Look for owner identification
                    owner_id = sample_item.get('owner_id') or sample_item.get('user_id')
                    if owner_id:
                        self.log(f"   Owner ID in content: {owner_id}")
                        if owner_id == self.account_1_user_id:
                            self.log("   ✅ Content ownership matches Account 1")
                        else:
                            self.log("   🚨 CRITICAL: Content ownership does NOT match Account 1!")
                            self.log(f"   Expected: {self.account_1_user_id}, Found: {owner_id}")
                else:
                    self.log("   ℹ️ No content items for Account 1")
                    
            else:
                self.log(f"   ❌ Account 1 content retrieval failed: {response_1.status_code} - {response_1.text}")
                content_1 = []
            
            # Get content for Account 2
            self.log("📁 Getting content for Account 2 (lperpere@yahoo.fr)")
            response_2 = self.session_2.get(f"{BACKEND_URL}/content/pending", params={"limit": 50})
            
            if response_2.status_code == 200:
                data_2 = response_2.json()
                content_2 = data_2.get('content', [])
                self.log(f"✅ Account 2 content retrieved: {len(content_2)} items")
                
                # Check user ownership in content items
                if content_2:
                    sample_item = content_2[0]
                    self.log(f"   Sample item keys: {list(sample_item.keys())}")
                    
                    # Look for owner identification
                    owner_id = sample_item.get('owner_id') or sample_item.get('user_id')
                    if owner_id:
                        self.log(f"   Owner ID in content: {owner_id}")
                        if owner_id == self.account_2_user_id:
                            self.log("   ✅ Content ownership matches Account 2")
                        else:
                            self.log("   🚨 CRITICAL: Content ownership does NOT match Account 2!")
                            self.log(f"   Expected: {self.account_2_user_id}, Found: {owner_id}")
                else:
                    self.log("   ℹ️ No content items for Account 2")
                    
            else:
                self.log(f"   ❌ Account 2 content retrieval failed: {response_2.status_code} - {response_2.text}")
                content_2 = []
            
            # CRITICAL SECURITY CHECK: Look for cross-contamination
            if content_1 and content_2:
                self.log("🔍 CRITICAL SECURITY CHECK: Analyzing content isolation")
                
                # Extract content IDs for comparison
                content_1_ids = set(item.get('id') for item in content_1 if item.get('id'))
                content_2_ids = set(item.get('id') for item in content_2 if item.get('id'))
                
                # Check for overlapping content IDs
                overlapping_ids = content_1_ids.intersection(content_2_ids)
                if overlapping_ids:
                    self.log(f"🚨 CRITICAL SECURITY BREACH: {len(overlapping_ids)} content items appear in BOTH accounts!")
                    self.log(f"   Overlapping IDs: {list(overlapping_ids)[:5]}...")  # Show first 5
                    return False
                else:
                    self.log("✅ No overlapping content IDs between accounts (good)")
                
                # Check for cross-contamination in owner IDs
                account_1_owners = set()
                account_2_owners = set()
                
                for item in content_1:
                    owner = item.get('owner_id') or item.get('user_id')
                    if owner:
                        account_1_owners.add(owner)
                
                for item in content_2:
                    owner = item.get('owner_id') or item.get('user_id')
                    if owner:
                        account_2_owners.add(owner)
                
                # Check if Account 1 has content from Account 2's user_id
                if self.account_2_user_id in account_1_owners:
                    self.log("🚨 CRITICAL: Account 1 has content owned by Account 2!")
                    return False
                
                # Check if Account 2 has content from Account 1's user_id
                if self.account_1_user_id in account_2_owners:
                    self.log("🚨 CRITICAL: Account 2 has content owned by Account 1!")
                    return False
                
                self.log("✅ Content ownership is properly isolated")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Content isolation test error: {str(e)}", "ERROR")
            self.log(f"   Traceback: {traceback.format_exc()}")
            return False
    
    def test_jwt_token_validation(self):
        """Test JWT token validation and cross-account access"""
        self.log("🔍 TESTING JWT TOKEN VALIDATION AND CROSS-ACCOUNT ACCESS")
        
        try:
            # Test 1: Try to use Account 1's token to access Account 2's data
            self.log("🧪 Test 1: Using Account 1 token to access endpoints")
            
            # Create a session with Account 1's token
            test_session = requests.Session()
            test_session.headers.update({
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.account_1_token}'
            })
            
            # Try to access content with Account 1's token
            response = test_session.get(f"{BACKEND_URL}/content/pending")
            if response.status_code == 200:
                data = response.json()
                content = data.get('content', [])
                
                # Check if any content belongs to Account 2
                account_2_content_found = False
                for item in content:
                    owner = item.get('owner_id') or item.get('user_id')
                    if owner == self.account_2_user_id:
                        account_2_content_found = True
                        break
                
                if account_2_content_found:
                    self.log("🚨 CRITICAL: Account 1 token can access Account 2's content!")
                    return False
                else:
                    self.log("✅ Account 1 token only accesses Account 1's content")
            
            # Test 2: Try to use Account 2's token to access Account 1's data
            self.log("🧪 Test 2: Using Account 2 token to access endpoints")
            
            # Create a session with Account 2's token
            test_session_2 = requests.Session()
            test_session_2.headers.update({
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.account_2_token}'
            })
            
            # Try to access content with Account 2's token
            response = test_session_2.get(f"{BACKEND_URL}/content/pending")
            if response.status_code == 200:
                data = response.json()
                content = data.get('content', [])
                
                # Check if any content belongs to Account 1
                account_1_content_found = False
                for item in content:
                    owner = item.get('owner_id') or item.get('user_id')
                    if owner == self.account_1_user_id:
                        account_1_content_found = True
                        break
                
                if account_1_content_found:
                    self.log("🚨 CRITICAL: Account 2 token can access Account 1's content!")
                    return False
                else:
                    self.log("✅ Account 2 token only accesses Account 2's content")
            
            # Test 3: Try invalid/malformed tokens
            self.log("🧪 Test 3: Testing invalid token handling")
            
            invalid_session = requests.Session()
            invalid_session.headers.update({
                'Content-Type': 'application/json',
                'Authorization': 'Bearer invalid_token_12345'
            })
            
            response = invalid_session.get(f"{BACKEND_URL}/content/pending")
            if response.status_code == 401:
                self.log("✅ Invalid token properly rejected")
            else:
                self.log(f"⚠️ Invalid token handling unexpected: {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log(f"❌ JWT token validation test error: {str(e)}", "ERROR")
            self.log(f"   Traceback: {traceback.format_exc()}")
            return False
    
    def test_database_query_filters(self):
        """Test if database queries properly filter by user_id"""
        self.log("🔍 TESTING DATABASE QUERY FILTERS")
        
        try:
            # Test various endpoints that should be user-specific
            endpoints_to_test = [
                "/content/pending",
                "/business-profile",
                "/notes"
            ]
            
            for endpoint in endpoints_to_test:
                self.log(f"🧪 Testing endpoint: {endpoint}")
                
                # Get data for both accounts
                response_1 = self.session_1.get(f"{BACKEND_URL}{endpoint}")
                response_2 = self.session_2.get(f"{BACKEND_URL}{endpoint}")
                
                if response_1.status_code == 200 and response_2.status_code == 200:
                    data_1 = response_1.json()
                    data_2 = response_2.json()
                    
                    # Compare responses
                    if data_1 == data_2:
                        self.log(f"🚨 CRITICAL: {endpoint} returns identical data for both accounts!")
                        return False
                    else:
                        self.log(f"✅ {endpoint} returns different data for each account")
                        
                elif response_1.status_code == 200 or response_2.status_code == 200:
                    self.log(f"ℹ️ {endpoint} - One account has data, other doesn't (normal)")
                else:
                    self.log(f"ℹ️ {endpoint} - Both accounts return non-200 status")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Database query filters test error: {str(e)}", "ERROR")
            self.log(f"   Traceback: {traceback.format_exc()}")
            return False
    
    def identify_root_cause(self):
        """Analyze findings and identify potential root causes"""
        self.log("🎯 ROOT CAUSE ANALYSIS")
        
        try:
            # Check if both accounts have the same user_id (which would be a major issue)
            if self.account_1_user_id == self.account_2_user_id:
                self.log("🚨 CRITICAL ROOT CAUSE: Both accounts have the SAME user_id!")
                self.log(f"   Both accounts resolve to user_id: {self.account_1_user_id}")
                self.log("   This explains the data leakage - the system thinks they're the same user")
                return "same_user_id"
            
            # Check if tokens are somehow shared or cached
            if self.account_1_token == self.account_2_token:
                self.log("🚨 CRITICAL ROOT CAUSE: Both accounts have the SAME JWT token!")
                self.log("   This indicates a token generation or caching issue")
                return "same_token"
            
            # Check for session sharing issues
            self.log("🔍 Checking for potential session/caching issues")
            
            # Test /auth/me endpoint for both accounts
            me_response_1 = self.session_1.get(f"{BACKEND_URL}/auth/me")
            me_response_2 = self.session_2.get(f"{BACKEND_URL}/auth/me")
            
            if me_response_1.status_code == 200 and me_response_2.status_code == 200:
                me_data_1 = me_response_1.json()
                me_data_2 = me_response_2.json()
                
                self.log(f"Account 1 /auth/me: {me_data_1}")
                self.log(f"Account 2 /auth/me: {me_data_2}")
                
                if me_data_1 == me_data_2:
                    self.log("🚨 CRITICAL: /auth/me returns identical data for both accounts!")
                    return "auth_me_identical"
                
                # Check specific fields
                user_id_1 = me_data_1.get('user_id')
                user_id_2 = me_data_2.get('user_id')
                email_1 = me_data_1.get('email')
                email_2 = me_data_2.get('email')
                
                if user_id_1 == user_id_2:
                    self.log("🚨 CRITICAL: /auth/me returns same user_id for both accounts!")
                    return "auth_me_same_user_id"
                
                if email_1 == email_2:
                    self.log("🚨 CRITICAL: /auth/me returns same email for both accounts!")
                    return "auth_me_same_email"
            
            # If we get here, the issue might be in specific endpoint implementations
            self.log("🔍 Root cause may be in specific endpoint database query filters")
            return "endpoint_specific"
            
        except Exception as e:
            self.log(f"❌ Root cause analysis error: {str(e)}", "ERROR")
            return "analysis_error"
    
    def run_security_investigation(self):
        """Run the complete security investigation"""
        self.log("🚨 STARTING CRITICAL SECURITY INVESTIGATION - USER DATA ISOLATION")
        self.log("=" * 80)
        self.log(f"🌐 Backend URL: {BACKEND_URL}")
        self.log(f"👤 Account 1: {ACCOUNT_1['email']}")
        self.log(f"👤 Account 2: {ACCOUNT_2['email']}")
        self.log("🎯 Objective: Investigate reported data leakage between accounts")
        self.log("=" * 80)
        
        results = {
            'account_1_auth': False,
            'account_2_auth': False,
            'website_analysis_isolation': False,
            'content_isolation': False,
            'jwt_validation': False,
            'database_filters': False
        }
        
        # Step 1: Authenticate both accounts
        self.log("🔐 STEP 1: AUTHENTICATION")
        self.account_1_token, self.account_1_user_id = self.authenticate_account(
            ACCOUNT_1, self.session_1, "Account 1"
        )
        if self.account_1_token:
            results['account_1_auth'] = True
        
        self.account_2_token, self.account_2_user_id = self.authenticate_account(
            ACCOUNT_2, self.session_2, "Account 2"
        )
        if self.account_2_token:
            results['account_2_auth'] = True
        
        # Only proceed if both accounts authenticated
        if results['account_1_auth'] and results['account_2_auth']:
            
            # Step 2: Test website analysis isolation
            self.log("\n🔍 STEP 2: WEBSITE ANALYSIS ISOLATION")
            if self.test_website_analysis_isolation():
                results['website_analysis_isolation'] = True
            
            # Step 3: Test content isolation
            self.log("\n🔍 STEP 3: CONTENT/MEDIA ISOLATION")
            if self.test_content_isolation():
                results['content_isolation'] = True
            
            # Step 4: Test JWT token validation
            self.log("\n🔍 STEP 4: JWT TOKEN VALIDATION")
            if self.test_jwt_token_validation():
                results['jwt_validation'] = True
            
            # Step 5: Test database query filters
            self.log("\n🔍 STEP 5: DATABASE QUERY FILTERS")
            if self.test_database_query_filters():
                results['database_filters'] = True
            
            # Step 6: Root cause analysis
            self.log("\n🎯 STEP 6: ROOT CAUSE ANALYSIS")
            root_cause = self.identify_root_cause()
            
        else:
            self.log("❌ Cannot proceed - authentication failed for one or both accounts")
        
        # Summary
        self.log("\n" + "=" * 80)
        self.log("🎯 SECURITY INVESTIGATION SUMMARY")
        
        passed_tests = sum(results.values())
        total_tests = len(results)
        
        self.log(f"📊 Test Results: {passed_tests}/{total_tests} passed")
        
        for test_name, passed in results.items():
            status = "✅ SECURE" if passed else "🚨 SECURITY ISSUE"
            self.log(f"   {test_name.replace('_', ' ').title()}: {status}")
        
        # Critical security assessment
        self.log("\n🚨 CRITICAL SECURITY ASSESSMENT:")
        
        if not results['account_1_auth'] or not results['account_2_auth']:
            self.log("❌ AUTHENTICATION FAILED - Cannot complete security assessment")
        elif passed_tests == total_tests:
            self.log("✅ NO SECURITY ISSUES DETECTED - Data isolation appears to be working correctly")
            self.log("   The reported issue may be resolved or occur under specific conditions")
        else:
            self.log("🚨 SECURITY VULNERABILITIES DETECTED!")
            self.log("   IMMEDIATE ACTION REQUIRED:")
            self.log("   1. Review database query filters for user_id isolation")
            self.log("   2. Check JWT token generation and validation")
            self.log("   3. Verify session management")
            self.log("   4. Audit all endpoints for proper user data filtering")
        
        return results

def main():
    """Main execution function"""
    print("🚨 CRITICAL SECURITY INVESTIGATION - USER DATA ISOLATION")
    print("=" * 80)
    print(f"📅 Investigation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print("🎯 Investigating reported data leakage between user accounts")
    print("=" * 80)
    
    tester = UserDataIsolationTester()
    results = tester.run_security_investigation()
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)  # All security tests passed
    else:
        sys.exit(1)  # Security issues detected

if __name__ == "__main__":
    main()