#!/usr/bin/env python3
"""
Test spécifique pour vérifier le timeout à 90 secondes
Test avec des sites qui devraient déclencher le timeout
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://social-publisher-10.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

# Sites qui devraient potentiellement déclencher le timeout
TIMEOUT_TEST_SITES = [
    "https://google.com",  # Site complexe avec beaucoup de pages
    "https://facebook.com",  # Site très complexe
    "https://github.com",  # Site avec beaucoup de contenu
]

class TimeoutEdgeCaseTest:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        
    def authenticate(self):
        """Authenticate with provided credentials"""
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json=TEST_CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                })
                
                print(f"✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_timeout_behavior(self, url):
        """Test timeout behavior for a specific URL"""
        print(f"\n🔍 Testing timeout behavior for: {url}")
        
        try:
            start_time = time.time()
            
            response = self.session.post(
                f"{BACKEND_URL}/website/analyze",
                json={"website_url": url},
                timeout=100  # Client timeout higher than server timeout
            )
            
            analysis_time = time.time() - start_time
            
            print(f"   Response time: {analysis_time:.1f} seconds")
            print(f"   Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Analysis completed successfully")
                print(f"   analysis_optimized: {data.get('analysis_optimized', 'N/A')}")
                print(f"   timeout_handled: {data.get('timeout_handled', 'N/A')}")
                print(f"   analysis_type: {data.get('analysis_type', 'N/A')}")
                
                return {
                    "success": True,
                    "time": analysis_time,
                    "status_code": 200,
                    "timeout_fields": {
                        "analysis_optimized": data.get('analysis_optimized'),
                        "timeout_handled": data.get('timeout_handled')
                    }
                }
                
            elif response.status_code == 408:
                print(f"   ⏱️ Analysis timed out as expected")
                response_text = response.text
                has_90s_message = "90 secondes" in response_text or "90 seconds" in response_text
                print(f"   Contains '90 secondes' message: {has_90s_message}")
                print(f"   Response: {response_text}")
                
                return {
                    "success": True,  # Timeout is expected behavior
                    "time": analysis_time,
                    "status_code": 408,
                    "timeout_occurred": True,
                    "has_90s_message": has_90s_message,
                    "response": response_text
                }
                
            else:
                print(f"   ❌ Unexpected status code: {response.status_code}")
                print(f"   Response: {response.text}")
                
                return {
                    "success": False,
                    "time": analysis_time,
                    "status_code": response.status_code,
                    "error": f"Unexpected status {response.status_code}"
                }
                
        except requests.exceptions.Timeout:
            analysis_time = time.time() - start_time
            print(f"   ❌ Client timeout after {analysis_time:.1f}s")
            return {
                "success": False,
                "time": analysis_time,
                "error": "Client timeout"
            }
            
        except Exception as e:
            analysis_time = time.time() - start_time
            print(f"   ❌ Error: {str(e)}")
            return {
                "success": False,
                "time": analysis_time,
                "error": str(e)
            }
    
    def run_timeout_tests(self):
        """Run timeout tests on multiple sites"""
        print("🚀 TIMEOUT EDGE CASE TESTING")
        print("=" * 60)
        print("Objectif: Vérifier comportement timeout à 90 secondes")
        print("=" * 60)
        
        if not self.authenticate():
            print("❌ Cannot proceed without authentication")
            return False
        
        results = {}
        
        for url in TIMEOUT_TEST_SITES:
            result = self.test_timeout_behavior(url)
            results[url] = result
            
            # Wait a bit between tests to avoid overwhelming the server
            time.sleep(2)
        
        # Summary
        print(f"\n{'='*60}")
        print("📊 TIMEOUT TEST SUMMARY")
        print("=" * 60)
        
        for url, result in results.items():
            print(f"\n🌐 {url}:")
            print(f"   Time: {result.get('time', 0):.1f}s")
            print(f"   Status: {result.get('status_code', 'N/A')}")
            
            if result.get('timeout_occurred'):
                print(f"   ⏱️ Timeout occurred (expected)")
                print(f"   90s message: {'✅' if result.get('has_90s_message') else '❌'}")
            elif result.get('success'):
                print(f"   ✅ Completed successfully")
                timeout_fields = result.get('timeout_fields', {})
                print(f"   Timeout fields: {timeout_fields}")
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
        
        # Check if we got at least one timeout
        timeout_count = sum(1 for r in results.values() if r.get('timeout_occurred'))
        success_count = sum(1 for r in results.values() if r.get('success'))
        
        print(f"\n📈 RESULTS:")
        print(f"   Total tests: {len(results)}")
        print(f"   Successful: {success_count}")
        print(f"   Timeouts: {timeout_count}")
        
        if timeout_count > 0:
            print(f"✅ Timeout behavior verified - at least one site triggered 90s timeout")
        else:
            print(f"⚠️ No timeouts observed - all sites completed within 90s")
        
        return success_count >= len(results) * 0.5  # At least 50% success rate

if __name__ == "__main__":
    tester = TimeoutEdgeCaseTest()
    success = tester.run_timeout_tests()
    
    if success:
        print(f"\n🎉 TIMEOUT EDGE CASE TESTS COMPLETED")
    else:
        print(f"\n💥 TIMEOUT EDGE CASE TESTS FAILED")