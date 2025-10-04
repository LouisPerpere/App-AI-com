#!/usr/bin/env python3
"""
Instagram Connection Persistence Diagnostic
Testing why Instagram connection doesn't persist - button remains "Connecter" after successful connection.

This is a regression issue that needs to be diagnosed by checking:
1. OAuth callback saving correctly
2. Database collections consistency (social_connections vs social_media_connections)
3. State parameter format and validation
4. Token exchange process
5. Connection verification endpoints

Test URL: https://claire-marcus-app-1.preview.emergentagent.com/api
Credentials: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import sys
from datetime import datetime
import urllib.parse

# Configuration from review request
BACKEND_URL = "https://claire-marcus-app-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials from review request
EMAIL = "lperpere@yahoo.fr"
PASSWORD = "L@Reunion974!"

class InstagramConnectionDiagnostic:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        
    def authenticate(self):
        """Authenticate with the backend API"""
        print("🔐 Step 1: Authenticating with backend...")
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login-robust", json={
                "email": EMAIL,
                "password": PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                print(f"✅ Authentication successful")
                print(f"   User ID: {self.user_id}")
                print(f"   Token: {self.auth_token[:20]}..." if self.auth_token else "   Token: None")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def check_current_connections_state(self):
        """Step 2: Check current state of social connections"""
        print("\n📊 Step 2: Checking current social connections state...")
        
        try:
            # Check what frontend sees
            frontend_response = self.session.get(f"{API_BASE}/social/connections")
            print(f"Frontend view (GET /api/social/connections):")
            
            if frontend_response.status_code == 200:
                frontend_data = frontend_response.json()
                print(f"   Status: {frontend_response.status_code}")
                print(f"   Connections count: {len(frontend_data) if isinstance(frontend_data, list) else 'N/A'}")
                if isinstance(frontend_data, list) and frontend_data:
                    for conn in frontend_data:
                        print(f"   - Platform: {conn.get('platform', 'N/A')}, Active: {conn.get('active', 'N/A')}")
                else:
                    print("   - No connections found")
            else:
                print(f"   Status: {frontend_response.status_code}")
                print(f"   Error: {frontend_response.text}")
            
            # Check real database state
            debug_response = self.session.get(f"{API_BASE}/debug/social-connections")
            print(f"\nDatabase reality (GET /api/debug/social-connections):")
            
            if debug_response.status_code == 200:
                debug_data = debug_response.json()
                print(f"   Status: {debug_response.status_code}")
                print(f"   Total connections: {debug_data.get('total_connections', 'N/A')}")
                print(f"   Active connections: {debug_data.get('active_connections', 'N/A')}")
                print(f"   Facebook connections: {debug_data.get('facebook_connections', 'N/A')}")
                print(f"   Instagram connections: {debug_data.get('instagram_connections', 'N/A')}")
                
                # Show connection details if available
                if 'connections' in debug_data:
                    for conn in debug_data['connections']:
                        print(f"   - Platform: {conn.get('platform', 'N/A')}, Active: {conn.get('active', 'N/A')}, Token: {'Present' if conn.get('access_token') else 'Missing'}")
            else:
                print(f"   Status: {debug_response.status_code}")
                print(f"   Error: {debug_response.text}")
                
            return {
                'frontend_status': frontend_response.status_code,
                'frontend_data': frontend_data if frontend_response.status_code == 200 else None,
                'debug_status': debug_response.status_code,
                'debug_data': debug_data if debug_response.status_code == 200 else None
            }
            
        except Exception as e:
            print(f"❌ Error checking connections state: {str(e)}")
            return None
    
    def analyze_instagram_auth_url(self):
        """Step 3: Analyze Instagram OAuth URL generation"""
        print("\n🔗 Step 3: Analyzing Instagram OAuth URL generation...")
        
        try:
            response = self.session.get(f"{API_BASE}/social/instagram/auth-url")
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get('auth_url', '')
                
                print(f"✅ Instagram auth URL generated successfully")
                print(f"   URL: {auth_url[:100]}..." if len(auth_url) > 100 else f"   URL: {auth_url}")
                
                # Parse URL to analyze parameters
                if auth_url:
                    parsed_url = urllib.parse.urlparse(auth_url)
                    params = urllib.parse.parse_qs(parsed_url.query)
                    
                    print(f"   Domain: {parsed_url.netloc}")
                    print(f"   Path: {parsed_url.path}")
                    
                    # Check critical parameters
                    critical_params = ['client_id', 'redirect_uri', 'state', 'response_type', 'scope']
                    for param in critical_params:
                        if param in params:
                            value = params[param][0] if params[param] else 'Empty'
                            if param == 'state':
                                # Analyze state format
                                if '|' in value:
                                    parts = value.split('|')
                                    print(f"   {param}: {parts[0][:10]}...|{parts[1] if len(parts) > 1 else 'missing'}")
                                else:
                                    print(f"   {param}: {value[:20]}... (no pipe separator)")
                            else:
                                print(f"   {param}: {value[:50]}..." if len(value) > 50 else f"   {param}: {value}")
                        else:
                            print(f"   {param}: MISSING")
                
                return auth_url
            else:
                print(f"❌ Instagram auth URL generation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error analyzing Instagram auth URL: {str(e)}")
            return None
    
    def test_callback_state_validation(self):
        """Step 4: Test Instagram callback state parameter validation"""
        print("\n🔍 Step 4: Testing Instagram callback state validation...")
        
        try:
            # Generate a test state parameter like the auth URL would
            test_state = f"test_token_123|{self.user_id}"
            test_code = "test_authorization_code"
            
            # Test callback with proper state format
            callback_url = f"{API_BASE}/social/instagram/callback"
            callback_params = {
                'code': test_code,
                'state': test_state
            }
            
            print(f"   Testing callback with state: {test_state}")
            print(f"   Testing callback with code: {test_code}")
            
            # Make callback request (this will likely fail at token exchange, but we want to see state validation)
            response = self.session.get(callback_url, params=callback_params)
            
            print(f"   Callback response status: {response.status_code}")
            
            # Analyze response to understand where it fails
            if response.status_code == 302:
                # Redirect response - check location header
                location = response.headers.get('Location', '')
                print(f"   Redirect location: {location}")
                
                # Parse redirect parameters to understand success/failure
                if 'instagram_success=true' in location:
                    print("   ✅ State validation passed - redirected to success")
                elif 'instagram_invalid_state' in location:
                    print("   ❌ State validation failed - invalid state format")
                elif 'instagram_error' in location:
                    print("   ⚠️ State validation passed but token exchange failed (expected)")
                else:
                    print("   ❓ Unknown redirect pattern")
            else:
                print(f"   Response body: {response.text[:200]}...")
            
            return response.status_code
            
        except Exception as e:
            print(f"❌ Error testing callback state validation: {str(e)}")
            return None
    
    def analyze_database_collections(self):
        """Step 5: Analyze database collections for Instagram connections"""
        print("\n🗄️ Step 5: Analyzing database collections for connection storage...")
        
        try:
            # Check debug endpoint for collection analysis
            response = self.session.get(f"{API_BASE}/debug/social-connections")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Database collections analysis:")
                print(f"   Collection 1 (social_media_connections): {data.get('social_media_connections_count', 'N/A')} connections")
                print(f"   Collection 2 (social_connections): {data.get('social_connections_count', 'N/A')} connections")
                
                # Check if there's a mismatch
                smc_count = data.get('social_media_connections_count', 0)
                sc_count = data.get('social_connections_count', 0)
                
                if smc_count != sc_count:
                    print(f"   ⚠️ COLLECTION MISMATCH DETECTED!")
                    print(f"   Frontend likely reads from: social_media_connections ({smc_count})")
                    print(f"   Callback might save to: social_connections ({sc_count})")
                else:
                    print(f"   ✅ Collections are consistent")
                
                # Show Instagram-specific connections
                instagram_connections = [conn for conn in data.get('connections', []) if conn.get('platform') == 'instagram']
                print(f"   Instagram connections found: {len(instagram_connections)}")
                
                for i, conn in enumerate(instagram_connections):
                    print(f"   Instagram #{i+1}: Active={conn.get('active', 'N/A')}, Token={'Present' if conn.get('access_token') else 'Missing'}, Created={conn.get('created_at', 'N/A')}")
                
                return data
            else:
                print(f"❌ Database analysis failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error analyzing database collections: {str(e)}")
            return None
    
    def test_token_exchange_simulation(self):
        """Step 6: Simulate token exchange process"""
        print("\n🔄 Step 6: Simulating Instagram token exchange process...")
        
        try:
            # This is a simulation - we can't actually complete OAuth without real Instagram approval
            # But we can test the endpoint structure and error handling
            
            print("   Note: This is a simulation since we can't complete real OAuth in testing")
            print("   Testing endpoint structure and error handling...")
            
            # Test with invalid code to see error handling
            test_params = {
                'code': 'invalid_test_code',
                'state': f'test_state|{self.user_id}'
            }
            
            response = self.session.get(f"{API_BASE}/social/instagram/callback", params=test_params)
            
            print(f"   Test callback status: {response.status_code}")
            
            if response.status_code == 302:
                location = response.headers.get('Location', '')
                print(f"   Redirect location: {location}")
                
                # Analyze redirect to understand error handling
                if 'instagram_error' in location:
                    print("   ✅ Error handling working - invalid code properly handled")
                elif 'instagram_success' in location:
                    print("   ❓ Unexpected success with invalid code")
                else:
                    print("   ❓ Unknown error handling pattern")
            
            return True
            
        except Exception as e:
            print(f"❌ Error simulating token exchange: {str(e)}")
            return False
    
    def run_comprehensive_diagnostic(self):
        """Run complete Instagram connection persistence diagnostic"""
        print("🎯 INSTAGRAM CONNECTION PERSISTENCE DIAGNOSTIC")
        print("=" * 70)
        print(f"Environment: {BACKEND_URL}")
        print(f"Credentials: {EMAIL}")
        print(f"Issue: Instagram button remains 'Connecter' after successful connection")
        print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with diagnostic")
            return False
        
        # Step 2: Check current connections state
        connections_state = self.check_current_connections_state()
        
        # Step 3: Analyze Instagram auth URL
        auth_url = self.analyze_instagram_auth_url()
        
        # Step 4: Test callback state validation
        callback_status = self.test_callback_state_validation()
        
        # Step 5: Analyze database collections
        db_analysis = self.analyze_database_collections()
        
        # Step 6: Test token exchange simulation
        token_exchange_ok = self.test_token_exchange_simulation()
        
        # Diagnostic Summary
        print("\n" + "=" * 70)
        print("🔍 INSTAGRAM CONNECTION PERSISTENCE DIAGNOSTIC RESULTS")
        print("=" * 70)
        
        # Analyze findings
        issues_found = []
        
        # Check for collection mismatch
        if db_analysis:
            smc_count = db_analysis.get('social_media_connections_count', 0)
            sc_count = db_analysis.get('social_connections_count', 0)
            if smc_count != sc_count:
                issues_found.append("DATABASE COLLECTION MISMATCH: Frontend and callback use different collections")
        
        # Check for missing connections despite successful OAuth
        if connections_state:
            frontend_connections = connections_state.get('frontend_data', [])
            if not frontend_connections or len(frontend_connections) == 0:
                issues_found.append("NO VISIBLE CONNECTIONS: Frontend shows no connections despite OAuth attempts")
        
        # Check auth URL state format
        if not auth_url or '|' not in auth_url:
            issues_found.append("STATE FORMAT ISSUE: Auth URL state parameter may not include user_id")
        
        # Summary of findings
        if issues_found:
            print("❌ CRITICAL ISSUES IDENTIFIED:")
            for i, issue in enumerate(issues_found, 1):
                print(f"   {i}. {issue}")
        else:
            print("✅ No obvious issues detected in diagnostic")
        
        # Root cause analysis
        print(f"\n🎯 ROOT CAUSE ANALYSIS:")
        
        if db_analysis:
            instagram_connections = [conn for conn in db_analysis.get('connections', []) if conn.get('platform') == 'instagram']
            if instagram_connections:
                active_instagram = [conn for conn in instagram_connections if conn.get('active')]
                if not active_instagram:
                    print("   LIKELY CAUSE: Instagram connections exist but are marked as inactive")
                    print("   SOLUTION: Check why connections are being deactivated after creation")
                else:
                    print("   LIKELY CAUSE: Active Instagram connections exist but frontend can't see them")
                    print("   SOLUTION: Check collection consistency between callback and frontend")
            else:
                print("   LIKELY CAUSE: Instagram OAuth callback is not saving connections to database")
                print("   SOLUTION: Check callback implementation and error handling")
        
        # Recommendations
        print(f"\n💡 RECOMMENDED ACTIONS:")
        print("   1. Check Instagram callback code for proper database saving")
        print("   2. Verify collection consistency (social_connections vs social_media_connections)")
        print("   3. Test state parameter format in OAuth flow")
        print("   4. Check token exchange error handling")
        print("   5. Verify frontend connection retrieval logic")
        
        print("\n" + "=" * 70)
        
        return len(issues_found) == 0

def main():
    """Main diagnostic execution"""
    diagnostic = InstagramConnectionDiagnostic()
    success = diagnostic.run_comprehensive_diagnostic()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()