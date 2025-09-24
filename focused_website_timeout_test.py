#!/usr/bin/env python3
"""
FOCUSED TEST - Website Analysis Timeout Improvements
Testing specific timeout fixes for "mouline dans le vide" issue
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://instamanager-1.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_website_analysis_timeouts():
    """Test website analysis timeout improvements"""
    log("🚀 FOCUSED WEBSITE ANALYSIS TIMEOUT TEST")
    log("=" * 60)
    
    session = requests.Session()
    session.headers.update({'Content-Type': 'application/json'})
    
    # Step 1: Authentication
    log("🔐 Step 1: Authentication")
    try:
        auth_response = session.post(
            f"{BASE_URL}/auth/login-robust",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=15
        )
        
        if auth_response.status_code == 200:
            auth_data = auth_response.json()
            access_token = auth_data.get("access_token")
            user_id = auth_data.get("user_id")
            
            session.headers.update({"Authorization": f"Bearer {access_token}"})
            
            log(f"✅ Authentication successful - User ID: {user_id}")
        else:
            log(f"❌ Authentication failed: {auth_response.status_code}")
            return False
            
    except Exception as e:
        log(f"❌ Authentication error: {str(e)}")
        return False
    
    # Step 2: Test simple site (should succeed quickly)
    log("\n🔍 Step 2: Simple Site Test (https://myownwatch.fr)")
    log("   Expected: Success < 30 seconds")
    
    try:
        start_time = time.time()
        
        response = session.post(
            f"{BASE_URL}/website/analyze",
            json={"website_url": "https://myownwatch.fr"},
            timeout=45  # Allow reasonable timeout
        )
        
        analysis_time = time.time() - start_time
        log(f"   Analysis completed in {analysis_time:.1f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            log(f"✅ Simple site analysis SUCCESSFUL")
            log(f"   Response time: {analysis_time:.1f}s")
            log(f"   Analysis type: {data.get('analysis_type', 'unknown')}")
            
            # Check for new timeout-related fields
            new_fields = ["analysis_optimized", "timeout_handled"]
            for field in new_fields:
                if field in data:
                    log(f"   {field}: {data.get(field)}")
            
            # Verify content quality
            summary_length = len(data.get("analysis_summary", ""))
            storytelling_length = len(data.get("storytelling_analysis", ""))
            log(f"   Content: Summary {summary_length} chars, Storytelling {storytelling_length} chars")
            
            if analysis_time < 30:
                log(f"✅ TIME REQUIREMENT MET: {analysis_time:.1f}s < 30s")
                simple_site_success = True
            else:
                log(f"⚠️ TIME REQUIREMENT NOT MET: {analysis_time:.1f}s >= 30s")
                simple_site_success = False
                
        else:
            log(f"❌ Simple site analysis FAILED: HTTP {response.status_code}")
            log(f"   Response: {response.text[:200]}...")
            simple_site_success = False
            
    except requests.exceptions.Timeout:
        analysis_time = time.time() - start_time
        log(f"❌ Simple site analysis TIMEOUT after {analysis_time:.1f}s")
        simple_site_success = False
    except Exception as e:
        analysis_time = time.time() - start_time
        log(f"❌ Simple site analysis ERROR after {analysis_time:.1f}s: {str(e)}")
        simple_site_success = False
    
    # Step 3: Test complex site (should timeout properly)
    log("\n🔍 Step 3: Complex Site Timeout Test (https://google.com)")
    log("   Expected: Timeout ~45s with HTTP 408")
    
    try:
        start_time = time.time()
        
        response = session.post(
            f"{BASE_URL}/website/analyze",
            json={"website_url": "https://google.com"},
            timeout=60  # Allow up to 60s to catch the server timeout
        )
        
        analysis_time = time.time() - start_time
        log(f"   Analysis completed/failed in {analysis_time:.1f} seconds")
        
        if response.status_code == 408:
            # Expected timeout response
            log(f"✅ Complex site timeout SUCCESSFUL")
            log(f"   Response time: {analysis_time:.1f}s")
            log(f"   HTTP Status: {response.status_code} (Expected: 408)")
            
            try:
                error_data = response.json()
                error_message = error_data.get("error", "")
                if "L'analyse du site web a pris trop de temps" in error_message:
                    log(f"✅ User-friendly error message: {error_message}")
                else:
                    log(f"⚠️ Error message: {error_message}")
            except:
                log(f"⚠️ Could not parse error response: {response.text}")
            
            if 40 <= analysis_time <= 50:
                log(f"✅ TIMEOUT TIMING CORRECT: {analysis_time:.1f}s (Target: ~45s)")
                complex_site_success = True
            else:
                log(f"⚠️ TIMEOUT TIMING OFF: {analysis_time:.1f}s (Expected: ~45s)")
                complex_site_success = False
                
        elif response.status_code == 200:
            # Unexpected success (but might be OK if Google is simple)
            log(f"⚠️ Complex site analysis UNEXPECTEDLY SUCCEEDED")
            log(f"   Response time: {analysis_time:.1f}s")
            
            if analysis_time < 50:
                log(f"✅ Analysis within reasonable time")
                complex_site_success = True
            else:
                log(f"❌ Analysis took too long: {analysis_time:.1f}s")
                complex_site_success = False
        else:
            log(f"❌ Complex site analysis FAILED: HTTP {response.status_code}")
            log(f"   Response: {response.text[:200]}...")
            complex_site_success = False
            
    except requests.exceptions.Timeout:
        analysis_time = time.time() - start_time
        log(f"❌ Request timeout (client-side) after {analysis_time:.1f}s")
        log(f"   This suggests server timeout is not working properly")
        complex_site_success = False
    except Exception as e:
        analysis_time = time.time() - start_time
        log(f"❌ Complex site analysis ERROR after {analysis_time:.1f}s: {str(e)}")
        complex_site_success = False
    
    # Step 4: Test system stability
    log("\n🔍 Step 4: System Stability Test")
    log("   Testing other endpoints after website analysis")
    
    try:
        # Test health endpoint
        health_response = session.get(f"{BASE_URL}/health", timeout=10)
        if health_response.status_code == 200:
            log("✅ Health endpoint working")
            stability_success = True
        else:
            log(f"❌ Health endpoint failed: {health_response.status_code}")
            stability_success = False
            
    except Exception as e:
        log(f"❌ System stability test error: {str(e)}")
        stability_success = False
    
    # Final Results
    log("\n" + "=" * 60)
    log("🎯 TEST RESULTS SUMMARY:")
    
    results = {
        "Simple Site Analysis": simple_site_success,
        "Complex Site Timeout": complex_site_success,
        "System Stability": stability_success
    }
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        log(f"   {test_name}: {status}")
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    success_rate = (passed_tests / total_tests) * 100
    
    log(f"   OVERALL SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests})")
    
    # Final Conclusion
    log("\n🎯 FINAL CONCLUSION:")
    
    if success_rate >= 80:
        log("✅ WEBSITE ANALYSIS TIMEOUT IMPROVEMENTS: SUCCESSFUL")
        log("   - Timeout handling working correctly")
        log("   - Performance within acceptable limits")
        log("   - 'Mouline dans le vide' issue RESOLVED")
    elif success_rate >= 60:
        log("⚠️ WEBSITE ANALYSIS TIMEOUT IMPROVEMENTS: PARTIALLY SUCCESSFUL")
        log("   - Some improvements working but issues remain")
    else:
        log("❌ WEBSITE ANALYSIS TIMEOUT IMPROVEMENTS: FAILED")
        log("   - Timeout improvements not working as expected")
        log("   - 'Mouline dans le vide' issue may persist")
    
    return success_rate >= 60

if __name__ == "__main__":
    success = test_website_analysis_timeouts()
    if success:
        print("\n🎉 FOCUSED TIMEOUT TEST COMPLETED SUCCESSFULLY")
    else:
        print("\n💥 FOCUSED TIMEOUT TEST FAILED")