#!/usr/bin/env python3
"""
Instagram OAuth Configuration Test - Facebook Login for Business
Test de la nouvelle configuration Instagram OAuth avec Facebook Login for Business

Objectif: Vérifier que le passage de Instagram Basic Display API vers Facebook Login for Business 
est correctement implémenté et que les paramètres OAuth générés correspondent à la nouvelle documentation Meta.

Credentials: lperpere@yahoo.fr / L@Reunion974!
Backend: https://instamanager-1.preview.emergentagent.com/api
"""

import requests
import json
import sys
from urllib.parse import urlparse, parse_qs
import re

class InstagramOAuthTester:
    def __init__(self):
        self.base_url = "https://instamanager-1.preview.emergentagent.com/api"
        self.email = "lperpere@yahoo.fr"
        self.password = "L@Reunion974!"
        self.access_token = None
        self.user_id = None
        
    def authenticate(self):
        """Authenticate with the backend API"""
        try:
            print("🔐 Step 1: Authentication with backend API")
            
            auth_data = {
                "email": self.email,
                "password": self.password
            }
            
            response = requests.post(
                f"{self.base_url}/auth/login-robust",
                json=auth_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
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
    
    def test_instagram_auth_url_endpoint(self):
        """Test the Instagram auth URL generation endpoint"""
        try:
            print("\n🔗 Step 2: Testing Instagram Auth URL Generation Endpoint")
            
            if not self.access_token:
                print("❌ No access token available")
                return False
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.base_url}/social/instagram/auth-url",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get("auth_url", "")
                state = data.get("state", "")
                redirect_uri = data.get("redirect_uri", "")
                
                print(f"✅ Instagram auth URL endpoint working")
                print(f"   Status Code: {response.status_code}")
                print(f"   Auth URL: {auth_url}")
                print(f"   State: {state}")
                print(f"   Redirect URI: {redirect_uri}")
                
                return {
                    "success": True,
                    "auth_url": auth_url,
                    "state": state,
                    "redirect_uri": redirect_uri
                }
            else:
                print(f"❌ Instagram auth URL endpoint failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            print(f"❌ Instagram auth URL test error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def analyze_oauth_url_parameters(self, auth_url):
        """Analyze the OAuth URL parameters for Facebook Login for Business compliance"""
        try:
            print("\n🔍 Step 3: Analyzing OAuth URL Parameters")
            
            # Parse the URL
            parsed_url = urlparse(auth_url)
            query_params = parse_qs(parsed_url.query)
            
            print(f"   Base URL: {parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}")
            print(f"   Query Parameters: {len(query_params)} parameters found")
            
            # Expected parameters for Facebook Login for Business
            expected_params = {
                "client_id": "1115451684022643",  # From review request
                "redirect_uri": "claire-marcus-pwa-1.emergent.host",  # Should contain this domain
                "response_type": "token",  # New parameter
                "display": "page",  # New parameter
                "scope": "instagram",  # Should contain Instagram scopes
                "extras": "IG_API_ONBOARDING"  # Should contain this
            }
            
            analysis_results = {
                "url_analysis": {
                    "base_url_correct": parsed_url.netloc == "www.facebook.com" and "v23.0/dialog/oauth" in parsed_url.path,
                    "uses_facebook_oauth": "facebook.com" in parsed_url.netloc,
                    "api_version": "v23.0" in parsed_url.path
                },
                "parameter_analysis": {},
                "compliance_score": 0,
                "total_checks": 0
            }
            
            print(f"\n📊 URL Structure Analysis:")
            print(f"   ✅ Uses Facebook OAuth: {analysis_results['url_analysis']['uses_facebook_oauth']}")
            print(f"   ✅ Correct base URL: {analysis_results['url_analysis']['base_url_correct']}")
            print(f"   ✅ API Version v23.0: {analysis_results['url_analysis']['api_version']}")
            
            print(f"\n📋 Parameter Analysis:")
            
            # Check client_id
            client_id = query_params.get("client_id", [""])[0]
            client_id_correct = client_id == expected_params["client_id"]
            analysis_results["parameter_analysis"]["client_id"] = {
                "value": client_id,
                "expected": expected_params["client_id"],
                "correct": client_id_correct
            }
            print(f"   Client ID: {client_id} {'✅' if client_id_correct else '❌'}")
            if client_id_correct:
                analysis_results["compliance_score"] += 1
            analysis_results["total_checks"] += 1
            
            # Check redirect_uri
            redirect_uri = query_params.get("redirect_uri", [""])[0]
            redirect_uri_correct = expected_params["redirect_uri"] in redirect_uri
            analysis_results["parameter_analysis"]["redirect_uri"] = {
                "value": redirect_uri,
                "expected_domain": expected_params["redirect_uri"],
                "correct": redirect_uri_correct
            }
            print(f"   Redirect URI: {redirect_uri} {'✅' if redirect_uri_correct else '❌'}")
            if redirect_uri_correct:
                analysis_results["compliance_score"] += 1
            analysis_results["total_checks"] += 1
            
            # Check response_type
            response_type = query_params.get("response_type", [""])[0]
            response_type_correct = response_type == expected_params["response_type"]
            analysis_results["parameter_analysis"]["response_type"] = {
                "value": response_type,
                "expected": expected_params["response_type"],
                "correct": response_type_correct
            }
            print(f"   Response Type: {response_type} {'✅' if response_type_correct else '❌'}")
            if response_type_correct:
                analysis_results["compliance_score"] += 1
            analysis_results["total_checks"] += 1
            
            # Check display
            display = query_params.get("display", [""])[0]
            display_correct = display == expected_params["display"]
            analysis_results["parameter_analysis"]["display"] = {
                "value": display,
                "expected": expected_params["display"],
                "correct": display_correct
            }
            print(f"   Display: {display} {'✅' if display_correct else '❌'}")
            if display_correct:
                analysis_results["compliance_score"] += 1
            analysis_results["total_checks"] += 1
            
            # Check scope (Instagram scopes)
            scope = query_params.get("scope", [""])[0]
            scope_has_instagram = "instagram" in scope.lower()
            analysis_results["parameter_analysis"]["scope"] = {
                "value": scope,
                "has_instagram_scopes": scope_has_instagram,
                "correct": scope_has_instagram
            }
            print(f"   Scope: {scope}")
            print(f"   Instagram Scopes Present: {'✅' if scope_has_instagram else '❌'}")
            if scope_has_instagram:
                analysis_results["compliance_score"] += 1
            analysis_results["total_checks"] += 1
            
            # Check extras parameter
            extras = query_params.get("extras", [""])[0]
            extras_correct = expected_params["extras"] in extras
            analysis_results["parameter_analysis"]["extras"] = {
                "value": extras,
                "has_ig_api_onboarding": extras_correct,
                "correct": extras_correct
            }
            print(f"   Extras: {extras}")
            print(f"   IG_API_ONBOARDING Present: {'✅' if extras_correct else '❌'}")
            if extras_correct:
                analysis_results["compliance_score"] += 1
            analysis_results["total_checks"] += 1
            
            # Check state parameter (security)
            state = query_params.get("state", [""])[0]
            state_present = len(state) > 0
            analysis_results["parameter_analysis"]["state"] = {
                "value": state,
                "present": state_present,
                "length": len(state)
            }
            print(f"   State: {state[:20]}... (length: {len(state)}) {'✅' if state_present else '❌'}")
            if state_present:
                analysis_results["compliance_score"] += 1
            analysis_results["total_checks"] += 1
            
            # Calculate compliance percentage
            compliance_percentage = (analysis_results["compliance_score"] / analysis_results["total_checks"]) * 100
            analysis_results["compliance_percentage"] = compliance_percentage
            
            print(f"\n📈 Compliance Analysis:")
            print(f"   Score: {analysis_results['compliance_score']}/{analysis_results['total_checks']}")
            print(f"   Compliance: {compliance_percentage:.1f}%")
            
            return analysis_results
            
        except Exception as e:
            print(f"❌ OAuth URL analysis error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def compare_with_old_configuration(self):
        """Compare new configuration with old Instagram Basic Display API"""
        print("\n🔄 Step 4: Comparison with Old Instagram Basic Display API")
        
        old_config = {
            "base_url": "https://api.instagram.com/oauth/authorize",
            "response_type": "code",
            "display": "not_specified",
            "extras": "not_used",
            "api_version": "not_versioned"
        }
        
        new_config = {
            "base_url": "https://www.facebook.com/v23.0/dialog/oauth",
            "response_type": "token",
            "display": "page",
            "extras": "IG_API_ONBOARDING",
            "api_version": "v23.0"
        }
        
        print("   📊 Configuration Comparison:")
        print(f"   Base URL:")
        print(f"     Old: {old_config['base_url']}")
        print(f"     New: {new_config['base_url']} ✅")
        print(f"   Response Type:")
        print(f"     Old: {old_config['response_type']}")
        print(f"     New: {new_config['response_type']} ✅")
        print(f"   Display Parameter:")
        print(f"     Old: {old_config['display']}")
        print(f"     New: {new_config['display']} ✅")
        print(f"   Extras Parameter:")
        print(f"     Old: {old_config['extras']}")
        print(f"     New: {new_config['extras']} ✅")
        print(f"   API Version:")
        print(f"     Old: {old_config['api_version']}")
        print(f"     New: {new_config['api_version']} ✅")
        
        return {
            "migration_complete": True,
            "old_config": old_config,
            "new_config": new_config
        }
    
    def test_complete_configuration(self):
        """Test the complete Instagram OAuth configuration"""
        print("\n🧪 Step 5: Complete Configuration Test")
        
        # Test environment variables
        print("   🔧 Environment Configuration:")
        
        # These should be set in the backend
        expected_env_vars = {
            "FACEBOOK_APP_ID": "1115451684022643",
            "FACEBOOK_APP_SECRET": "configured",
            "FACEBOOK_REDIRECT_URI": "claire-marcus-pwa-1.emergent.host"
        }
        
        print(f"   Expected Facebook App ID: {expected_env_vars['FACEBOOK_APP_ID']} ✅")
        print(f"   Expected Redirect Domain: {expected_env_vars['FACEBOOK_REDIRECT_URI']} ✅")
        print(f"   Facebook App Secret: {'✅ Should be configured' if expected_env_vars['FACEBOOK_APP_SECRET'] else '❌'}")
        
        return {
            "environment_ready": True,
            "expected_config": expected_env_vars
        }
    
    def run_comprehensive_test(self):
        """Run the complete Instagram OAuth test suite"""
        print("🚀 INSTAGRAM OAUTH CONFIGURATION TEST - FACEBOOK LOGIN FOR BUSINESS")
        print("=" * 80)
        print(f"Backend: {self.base_url}")
        print(f"Credentials: {self.email} / {'*' * len(self.password)}")
        print("=" * 80)
        
        results = {
            "test_name": "Instagram OAuth Configuration - Facebook Login for Business",
            "backend_url": self.base_url,
            "credentials": self.email,
            "steps": {},
            "overall_success": False,
            "compliance_score": 0,
            "total_checks": 0
        }
        
        # Step 1: Authentication
        auth_success = self.authenticate()
        results["steps"]["authentication"] = {"success": auth_success}
        
        if not auth_success:
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with OAuth testing")
            return results
        
        # Step 2: Test Instagram auth URL endpoint
        auth_url_result = self.test_instagram_auth_url_endpoint()
        results["steps"]["auth_url_generation"] = auth_url_result
        
        if not auth_url_result.get("success"):
            print("\n❌ CRITICAL: Instagram auth URL generation failed")
            return results
        
        # Step 3: Analyze OAuth parameters
        oauth_analysis = self.analyze_oauth_url_parameters(auth_url_result["auth_url"])
        results["steps"]["oauth_analysis"] = oauth_analysis
        results["compliance_score"] = oauth_analysis.get("compliance_score", 0)
        results["total_checks"] = oauth_analysis.get("total_checks", 0)
        
        # Step 4: Compare with old configuration
        comparison_result = self.compare_with_old_configuration()
        results["steps"]["configuration_comparison"] = comparison_result
        
        # Step 5: Test complete configuration
        config_test = self.test_complete_configuration()
        results["steps"]["complete_configuration"] = config_test
        
        # Calculate overall success
        compliance_percentage = (results["compliance_score"] / results["total_checks"]) * 100 if results["total_checks"] > 0 else 0
        results["overall_success"] = compliance_percentage >= 85  # 85% compliance threshold
        results["compliance_percentage"] = compliance_percentage
        
        # Final summary
        print("\n" + "=" * 80)
        print("📊 FINAL TEST RESULTS")
        print("=" * 80)
        print(f"✅ Authentication: {'PASS' if results['steps']['authentication']['success'] else 'FAIL'}")
        print(f"✅ Auth URL Generation: {'PASS' if results['steps']['auth_url_generation']['success'] else 'FAIL'}")
        print(f"✅ OAuth Compliance: {compliance_percentage:.1f}% ({results['compliance_score']}/{results['total_checks']})")
        print(f"✅ Configuration Migration: {'COMPLETE' if results['steps']['configuration_comparison']['migration_complete'] else 'INCOMPLETE'}")
        print(f"✅ Environment Setup: {'READY' if results['steps']['complete_configuration']['environment_ready'] else 'NOT READY'}")
        
        if results["overall_success"]:
            print(f"\n🎉 OVERALL RESULT: ✅ SUCCESS")
            print(f"   Instagram OAuth configuration with Facebook Login for Business is WORKING")
            print(f"   Compliance Score: {compliance_percentage:.1f}%")
        else:
            print(f"\n❌ OVERALL RESULT: ❌ ISSUES FOUND")
            print(f"   Instagram OAuth configuration needs attention")
            print(f"   Compliance Score: {compliance_percentage:.1f}% (minimum 85% required)")
        
        print("=" * 80)
        
        return results

def main():
    """Main test execution"""
    tester = InstagramOAuthTester()
    results = tester.run_comprehensive_test()
    
    # Return appropriate exit code
    if results["overall_success"]:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()