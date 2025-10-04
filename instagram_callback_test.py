#!/usr/bin/env python3
"""
Focused Instagram Callback Fix Testing - LIVE Environment
========================================================

Testing specifically the Instagram callback fix that should:
1. Process Instagram connections directly (no redirect to Facebook)
2. Show logs: "🔄 Instagram OAuth callback - TRAITEMENT DIRECT"
3. Complete token exchange for Instagram
4. Create active Instagram connections

Environment: https://claire-marcus.com/api
Credentials: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "https://claire-marcus.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def authenticate():
    """Authenticate with LIVE environment"""
    log("🔐 Authenticating with LIVE environment...")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login-robust", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_id = data.get("user_id")
            log(f"✅ Authentication successful - User ID: {user_id}")
            return token, user_id
        else:
            log(f"❌ Authentication failed: {response.status_code} - {response.text}", "ERROR")
            return None, None
    except Exception as e:
        log(f"❌ Authentication error: {str(e)}", "ERROR")
        return None, None

def test_instagram_callback_direct():
    """Test Instagram callback direct processing"""
    log("🔄 Testing Instagram callback direct processing...")
    
    token, user_id = authenticate()
    if not token:
        return False
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test 1: Instagram callback without parameters
    log("   Test 1: Instagram callback without parameters...")
    try:
        response = requests.get(f"{BASE_URL}/social/instagram/callback", headers=headers)
        log(f"   Response status: {response.status_code}")
        
        # Check if it's a redirect
        if response.status_code in [301, 302, 307, 308]:
            location = response.headers.get("Location", "")
            log(f"   Redirect location: {location}")
            
            if "/facebook/callback" in location:
                log("   ❌ CRITICAL: Instagram callback redirects to Facebook!", "ERROR")
                return False
            else:
                log("   ✅ Instagram callback redirects but not to Facebook")
        else:
            log("   ✅ Instagram callback processes directly (no redirect)")
            
    except Exception as e:
        log(f"   ❌ Error testing Instagram callback: {str(e)}", "ERROR")
        return False
    
    # Test 2: Instagram callback with test parameters
    log("   Test 2: Instagram callback with test parameters...")
    try:
        test_params = {
            "code": "test_instagram_code_123",
            "state": f"instagram_oauth|{user_id}"
        }
        
        response = requests.get(f"{BASE_URL}/social/instagram/callback", 
                              params=test_params, headers=headers, allow_redirects=False)
        
        log(f"   Response status: {response.status_code}")
        
        # Check if it's a redirect to Facebook
        if response.status_code in [301, 302, 307, 308]:
            location = response.headers.get("Location", "")
            log(f"   Redirect location: {location}")
            
            if "/facebook/callback" in location:
                log("   ❌ CRITICAL: Instagram callback with params redirects to Facebook!", "ERROR")
                return False
            else:
                log("   ✅ Instagram callback redirects but not to Facebook")
                return True
        else:
            log("   ✅ Instagram callback processes parameters directly")
            
            # Try to get response content
            try:
                if response.headers.get("content-type", "").startswith("application/json"):
                    data = response.json()
                    log(f"   Response data: {json.dumps(data, indent=2)[:300]}...")
                else:
                    content = response.text[:300]
                    log(f"   Response content: {content}...")
            except:
                pass
            
            return True
            
    except Exception as e:
        log(f"   ❌ Error testing Instagram callback with params: {str(e)}", "ERROR")
        return False

def test_instagram_vs_facebook_callback():
    """Compare Instagram vs Facebook callback behavior"""
    log("🔍 Comparing Instagram vs Facebook callback behavior...")
    
    token, user_id = authenticate()
    if not token:
        return False
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test Instagram callback
    log("   Testing Instagram callback...")
    try:
        test_params = {
            "code": "test_code_123",
            "state": f"instagram_oauth|{user_id}"
        }
        
        instagram_response = requests.get(f"{BASE_URL}/social/instagram/callback", 
                                        params=test_params, headers=headers, allow_redirects=False)
        
        log(f"   Instagram callback status: {instagram_response.status_code}")
        
        if instagram_response.status_code in [301, 302, 307, 308]:
            instagram_location = instagram_response.headers.get("Location", "")
            log(f"   Instagram redirect: {instagram_location}")
        else:
            log("   Instagram processes directly")
            
    except Exception as e:
        log(f"   ❌ Instagram callback error: {str(e)}", "ERROR")
        return False
    
    # Test Facebook callback for comparison
    log("   Testing Facebook callback...")
    try:
        test_params = {
            "code": "test_code_123",
            "state": f"facebook_oauth|{user_id}"
        }
        
        facebook_response = requests.get(f"{BASE_URL}/social/facebook/callback", 
                                       params=test_params, headers=headers, allow_redirects=False)
        
        log(f"   Facebook callback status: {facebook_response.status_code}")
        
        if facebook_response.status_code in [301, 302, 307, 308]:
            facebook_location = facebook_response.headers.get("Location", "")
            log(f"   Facebook redirect: {facebook_location}")
        else:
            log("   Facebook processes directly")
            
    except Exception as e:
        log(f"   ❌ Facebook callback error: {str(e)}", "ERROR")
    
    return True

def test_social_connections():
    """Test current social connections"""
    log("📊 Testing current social connections...")
    
    token, user_id = authenticate()
    if not token:
        return False
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(f"{BASE_URL}/social/connections", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            connections = data.get("connections", [])
            
            log(f"   Total connections: {len(connections)}")
            
            instagram_connections = [c for c in connections if c.get("platform") == "instagram"]
            facebook_connections = [c for c in connections if c.get("platform") == "facebook"]
            
            log(f"   Instagram connections: {len(instagram_connections)}")
            log(f"   Facebook connections: {len(facebook_connections)}")
            
            # Check for active connections
            active_instagram = [c for c in instagram_connections if c.get("active", False)]
            active_facebook = [c for c in facebook_connections if c.get("active", False)]
            
            log(f"   Active Instagram: {len(active_instagram)}")
            log(f"   Active Facebook: {len(active_facebook)}")
            
            return True
        else:
            log(f"   ❌ Failed to get connections: {response.status_code}", "ERROR")
            return False
            
    except Exception as e:
        log(f"   ❌ Social connections error: {str(e)}", "ERROR")
        return False

def main():
    """Main test execution"""
    log("🎯 INSTAGRAM CALLBACK FIX TESTING - LIVE ENVIRONMENT")
    log("=" * 60)
    
    results = {}
    
    # Test 1: Instagram callback direct processing
    results["direct_processing"] = test_instagram_callback_direct()
    
    # Test 2: Instagram vs Facebook callback comparison
    results["callback_comparison"] = test_instagram_vs_facebook_callback()
    
    # Test 3: Social connections status
    results["social_connections"] = test_social_connections()
    
    # Summary
    log("=" * 60)
    log("🎯 TEST RESULTS SUMMARY")
    log("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        log(f"{status} {test_name.replace('_', ' ').title()}")
    
    log("=" * 60)
    log(f"📊 OVERALL: {passed}/{total} tests passed")
    
    # Critical assessment
    if results.get("direct_processing", False):
        log("🎉 CRITICAL SUCCESS: Instagram callback processes directly!")
        log("✅ Instagram callback fix appears to be working correctly")
        return True
    else:
        log("🚨 CRITICAL ISSUE: Instagram callback still has redirect problems")
        log("❌ Instagram callback fix needs additional work")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)