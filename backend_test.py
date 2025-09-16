#!/usr/bin/env python3
"""
DIAGNOSTIC ANALYSE CLAUDE MANQUANTE - storytelling_analysis
Backend testing for Claude Storytelling Analysis missing issue

Test credentials:
- Email: lperpere@yahoo.fr  
- Password: L@Reunion974!
- Backend URL: https://insta-automate-2.preview.emergentagent.com/api
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://insta-automate-2.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"
TEST_WEBSITE_URL = "https://myownwatch.fr"

class ClaudeAnalysisTest:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        
    def authenticate(self):
        """Step 1: Authenticate with backend"""
        print("🔐 Step 1: Authentication with POST /api/auth/login-robust")
        
        auth_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json=auth_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                print(f"✅ Authentication successful")
                print(f"   User ID: {self.user_id}")
                print(f"   Token: {self.access_token[:20]}..." if self.access_token else "   Token: None")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_existing_analysis_retrieval(self):
        """Step 2: Test récupération analyse existante - GET /api/website/analysis"""
        print("\n📊 Step 2: Test récupération analyse existante")
        print("   GET /api/website/analysis pour lperpere@yahoo.fr")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/website/analysis")
            
            print(f"   📋 Response status: {response.status_code}")
            print(f"   📋 Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Analysis retrieval successful")
                print(f"   📋 Response type: {type(data)}")
                
                # Handle both single object and array responses
                if isinstance(data, list):
                    if len(data) > 0:
                        analysis_data = data[0]  # Get first analysis
                        print(f"   📋 Found {len(data)} analyses, using first one")
                    else:
                        print(f"   📋 Empty analysis list returned")
                        analysis_data = {}
                elif isinstance(data, dict):
                    analysis_data = data
                    print(f"   📋 Single analysis object returned")
                else:
                    print(f"   ⚠️ Unexpected response format: {type(data)}")
                    analysis_data = {}
                
                # Check for storytelling_analysis field
                storytelling_analysis = analysis_data.get("storytelling_analysis")
                analysis_summary = analysis_data.get("analysis_summary")
                analysis_type = analysis_data.get("analysis_type")
                
                print(f"   📋 Analysis type: {analysis_type}")
                print(f"   📋 Analysis summary present: {'✅' if analysis_summary else '❌'}")
                print(f"   📋 Storytelling analysis present: {'✅' if storytelling_analysis else '❌'}")
                
                if storytelling_analysis:
                    print(f"   📋 Storytelling analysis length: {len(str(storytelling_analysis))} chars")
                    if isinstance(storytelling_analysis, str) and len(storytelling_analysis) > 0:
                        print(f"   📋 Storytelling analysis preview: {storytelling_analysis[:100]}...")
                    else:
                        print(f"   ⚠️ Storytelling analysis is empty or null: {storytelling_analysis}")
                else:
                    print(f"   ❌ CRITICAL: storytelling_analysis field is missing or null")
                
                if analysis_summary:
                    print(f"   📋 Analysis summary length: {len(str(analysis_summary))} chars")
                
                # Check metadata fields
                storytelling_ai = analysis_data.get("storytelling_ai")
                business_ai = analysis_data.get("business_ai")
                
                print(f"   📋 Business AI: {business_ai}")
                print(f"   📋 Storytelling AI: {storytelling_ai}")
                
                # Show all available fields for debugging
                if analysis_data:
                    all_fields = list(analysis_data.keys())
                    print(f"   📋 Available fields ({len(all_fields)}): {', '.join(all_fields[:10])}{'...' if len(all_fields) > 10 else ''}")
                
                return {
                    "success": True,
                    "has_storytelling_analysis": bool(storytelling_analysis),
                    "has_analysis_summary": bool(analysis_summary),
                    "analysis_type": analysis_type,
                    "storytelling_ai": storytelling_ai,
                    "business_ai": business_ai,
                    "data_found": bool(analysis_data)
                }
            else:
                print(f"❌ Analysis retrieval failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Analysis retrieval error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def test_new_analysis_generation(self):
        """Step 3: Test génération nouvelle analyse - POST /api/website/analyze"""
        print(f"\n🔍 Step 3: Test génération nouvelle analyse")
        print(f"   POST /api/website/analyze avec URL: {TEST_WEBSITE_URL}")
        
        analyze_data = {
            "website_url": TEST_WEBSITE_URL
        }
        
        try:
            print("   🚀 Launching website analysis...")
            response = self.session.post(
                f"{BACKEND_URL}/website/analyze",
                json=analyze_data,
                headers={"Content-Type": "application/json"},
                timeout=60  # 60 seconds timeout for analysis
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ New analysis generation successful")
                
                # Verify both analyses are present
                storytelling_analysis = data.get("storytelling_analysis")
                analysis_summary = data.get("analysis_summary")
                analysis_type = data.get("analysis_type")
                
                print(f"   📋 Analysis type: {analysis_type}")
                print(f"   📋 Expected: 'gpt4o_plus_claude_storytelling'")
                
                # Check GPT-4o analysis
                if analysis_summary:
                    print(f"   ✅ GPT-4o analysis (analysis_summary) present: {len(str(analysis_summary))} chars")
                    print(f"   📋 GPT-4o preview: {str(analysis_summary)[:100]}...")
                else:
                    print(f"   ❌ GPT-4o analysis (analysis_summary) missing")
                
                # Check Claude analysis
                if storytelling_analysis:
                    print(f"   ✅ Claude analysis (storytelling_analysis) present: {len(str(storytelling_analysis))} chars")
                    print(f"   📋 Claude preview: {str(storytelling_analysis)[:100]}...")
                else:
                    print(f"   ❌ CRITICAL: Claude analysis (storytelling_analysis) missing or null")
                    print(f"   📋 storytelling_analysis value: {storytelling_analysis}")
                
                # Check AI metadata
                storytelling_ai = data.get("storytelling_ai")
                business_ai = data.get("business_ai")
                
                print(f"   📋 Business AI: {business_ai} (expected: 'GPT-4o')")
                print(f"   📋 Storytelling AI: {storytelling_ai} (expected: 'Claude Sonnet 4')")
                
                # Check all fields present
                all_fields = list(data.keys())
                print(f"   📋 Total response fields: {len(all_fields)}")
                print(f"   📋 Response fields: {', '.join(all_fields[:10])}{'...' if len(all_fields) > 10 else ''}")
                
                return {
                    "success": True,
                    "has_storytelling_analysis": bool(storytelling_analysis and str(storytelling_analysis).strip()),
                    "has_analysis_summary": bool(analysis_summary and str(analysis_summary).strip()),
                    "analysis_type": analysis_type,
                    "storytelling_ai": storytelling_ai,
                    "business_ai": business_ai,
                    "storytelling_content": str(storytelling_analysis)[:200] if storytelling_analysis else None,
                    "analysis_content": str(analysis_summary)[:200] if analysis_summary else None
                }
            else:
                print(f"❌ New analysis generation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ New analysis generation error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def test_analysis_persistence_after_generation(self):
        """Step 4: Test that newly generated analysis persists and can be retrieved"""
        print(f"\n💾 Step 4: Test analysis persistence after generation")
        print("   Verifying that the analysis we just generated can be retrieved")
        
        try:
            # Wait a moment for database write to complete
            import time
            time.sleep(2)
            
            response = self.session.get(f"{BACKEND_URL}/website/analysis")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Post-generation analysis retrieval successful")
                
                # Handle both single object and array responses
                if isinstance(data, list):
                    if len(data) > 0:
                        analysis_data = data[0]  # Get first analysis
                        print(f"   📋 Found {len(data)} analyses after generation")
                    else:
                        print(f"   ❌ No analyses found after generation")
                        return {"success": False, "error": "No analyses found after generation"}
                elif isinstance(data, dict):
                    analysis_data = data
                    print(f"   📋 Single analysis object found after generation")
                else:
                    print(f"   ⚠️ Unexpected response format: {type(data)}")
                    return {"success": False, "error": "Unexpected response format"}
                
                # Check if the newly generated analysis is present
                storytelling_analysis = analysis_data.get("storytelling_analysis")
                analysis_summary = analysis_data.get("analysis_summary")
                analysis_type = analysis_data.get("analysis_type")
                
                print(f"   📋 Analysis type: {analysis_type}")
                print(f"   📋 Analysis summary present: {'✅' if analysis_summary else '❌'}")
                print(f"   📋 Storytelling analysis present: {'✅' if storytelling_analysis else '❌'}")
                
                if storytelling_analysis and analysis_summary:
                    print(f"   ✅ PERSISTENCE SUCCESS: Both analyses are now retrievable")
                    print(f"   📋 Storytelling analysis length: {len(str(storytelling_analysis))} chars")
                    print(f"   📋 Analysis summary length: {len(str(analysis_summary))} chars")
                    
                    return {
                        "success": True,
                        "has_storytelling_analysis": True,
                        "has_analysis_summary": True,
                        "analysis_type": analysis_type,
                        "persistence_working": True
                    }
                else:
                    print(f"   ❌ PERSISTENCE FAILURE: Generated analysis not retrievable")
                    return {
                        "success": False,
                        "error": "Generated analysis not retrievable",
                        "has_storytelling_analysis": bool(storytelling_analysis),
                        "has_analysis_summary": bool(analysis_summary)
                    }
            else:
                print(f"❌ Post-generation analysis retrieval failed: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Post-generation analysis retrieval error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def run_diagnostic(self):
        """Run complete diagnostic for Claude storytelling analysis"""
        print("=" * 80)
        print("🔍 DIAGNOSTIC ANALYSE CLAUDE MANQUANTE - storytelling_analysis")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test credentials: {TEST_EMAIL}")
        print(f"Test website: {TEST_WEBSITE_URL}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ DIAGNOSTIC FAILED: Authentication failed")
            return False
        
        # Step 2: Test existing analysis retrieval
        existing_result = self.test_existing_analysis_retrieval()
        
        # Step 3: Test new analysis generation
        new_result = self.test_new_analysis_generation()
        
        # Step 4: Test analysis persistence after generation
        persistence_result = self.test_analysis_persistence_after_generation()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 DIAGNOSTIC SUMMARY")
        print("=" * 80)
        
        if existing_result.get("success"):
            print("✅ Existing analysis retrieval: SUCCESS")
            print(f"   - Has storytelling_analysis: {'✅' if existing_result.get('has_storytelling_analysis') else '❌'}")
            print(f"   - Has analysis_summary: {'✅' if existing_result.get('has_analysis_summary') else '❌'}")
            print(f"   - Analysis type: {existing_result.get('analysis_type')}")
        else:
            print("❌ Existing analysis retrieval: FAILED")
        
        if new_result.get("success"):
            print("✅ New analysis generation: SUCCESS")
            print(f"   - Has storytelling_analysis: {'✅' if new_result.get('has_storytelling_analysis') else '❌'}")
            print(f"   - Has analysis_summary: {'✅' if new_result.get('has_analysis_summary') else '❌'}")
            print(f"   - Analysis type: {new_result.get('analysis_type')}")
            print(f"   - Business AI: {new_result.get('business_ai')}")
            print(f"   - Storytelling AI: {new_result.get('storytelling_ai')}")
        else:
            print("❌ New analysis generation: FAILED")
        
        if persistence_result.get("success"):
            print("✅ Analysis persistence after generation: SUCCESS")
            print(f"   - Analysis retrievable after generation: {'✅' if persistence_result.get('persistence_working') else '❌'}")
        else:
            print("❌ Analysis persistence after generation: FAILED")
        
        # Determine root cause
        print("\n🔍 ROOT CAUSE ANALYSIS:")
        
        if not existing_result.get("success") and not new_result.get("success"):
            print("❌ CRITICAL: Both existing and new analysis retrieval failed")
            print("   Possible causes: Backend API issues, authentication problems")
        elif existing_result.get("success") and not existing_result.get("has_storytelling_analysis"):
            print("❌ ISSUE CONFIRMED: storytelling_analysis missing from existing data")
            print("   Possible causes: Database field missing, Claude analysis not saved")
        elif new_result.get("success") and not new_result.get("has_storytelling_analysis"):
            print("❌ ISSUE CONFIRMED: Claude analysis not generated in new analysis")
            print("   Possible causes: Claude API failure, timeout, configuration issue")
        elif (existing_result.get("has_storytelling_analysis") and 
              new_result.get("has_storytelling_analysis")):
            print("✅ ISSUE NOT REPRODUCED: Both analyses contain storytelling_analysis")
            print("   Possible causes: Issue was already fixed, frontend display problem")
        else:
            print("⚠️ MIXED RESULTS: Partial success detected")
        
        print("\n📋 RECOMMENDATION:")
        if (new_result.get("success") and 
            new_result.get("has_storytelling_analysis") and 
            new_result.get("has_analysis_summary")):
            print("✅ Backend Claude integration appears to be working correctly")
            print("   - Check frontend display logic for storytelling_analysis field")
            print("   - Verify frontend is reading the correct field names")
        else:
            print("❌ Backend Claude integration has issues")
            print("   - Check Claude API key configuration")
            print("   - Check backend logs for Claude API errors")
            print("   - Verify dual LLM system implementation")
        
        return True

if __name__ == "__main__":
    tester = ClaudeAnalysisTest()
    tester.run_diagnostic()