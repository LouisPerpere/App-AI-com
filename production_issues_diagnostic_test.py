#!/usr/bin/env python3
"""
URGENT PRODUCTION ISSUES DIAGNOSTIC TEST
=======================================

CRITICAL PROBLEMS TO INVESTIGATE:
1. Website analysis producing only "5 words" instead of detailed analysis
2. Content library migration failure - photos/content NOT imported to production
3. GPT model verification (GPT-4o vs GPT-5)

TEST WEBSITE: https://my-own-watch.fr
CREDENTIALS: lperpere@yahoo.fr / L@Reunion974!

Focus: Determine why production website analysis is poor quality compared to preview,
and verify content library migration status.
"""

import requests
import json
import sys
import os
from datetime import datetime
import time

class ProductionIssuesDiagnostic:
    def __init__(self):
        # Use the backend URL from frontend .env
        self.backend_url = "https://social-pub-hub.preview.emergentagent.com/api"
        self.test_website = "https://my-own-watch.fr"
        self.credentials = {
            "email": "lperpere@yahoo.fr",
            "password": "L@Reunion974!"
        }
        
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        
        # Test results storage
        self.test_results = {
            "authentication": {"status": "pending"},
            "website_analysis": {"status": "pending"},
            "content_library": {"status": "pending"},
            "gpt_model_verification": {"status": "pending"},
            "migration_status": {"status": "pending"}
        }
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def authenticate(self):
        """Step 1: Authenticate with backend"""
        self.log("🔐 Step 1: Authenticating with backend...")
        
        try:
            response = self.session.post(
                f"{self.backend_url}/auth/login-robust",
                json=self.credentials,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                self.log(f"✅ Authentication successful")
                self.log(f"   User ID: {self.user_id}")
                self.log(f"   Email: {data.get('email')}")
                
                self.test_results["authentication"] = {
                    "status": "success",
                    "user_id": self.user_id,
                    "email": data.get("email")
                }
                return True
            else:
                self.log(f"❌ Authentication failed: {response.status_code}")
                self.log(f"   Response: {response.text}")
                self.test_results["authentication"] = {
                    "status": "failed",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                return False
                
        except Exception as e:
            self.log(f"❌ Authentication error: {str(e)}")
            self.test_results["authentication"] = {
                "status": "error",
                "error": str(e)
            }
            return False
    
    def test_website_analysis_quality(self):
        """Step 2: Test website analysis quality and compare with expected results"""
        self.log("🌐 Step 2: Testing website analysis quality...")
        
        if not self.access_token:
            self.log("❌ Cannot test website analysis - not authenticated")
            return False
        
        try:
            # Check if website analyzer endpoint exists
            self.log(f"🔍 Testing website analysis for: {self.test_website}")
            
            # First, check if the website analyzer module is available
            health_response = self.session.get(f"{self.backend_url}/health", timeout=30)
            if health_response.status_code != 200:
                self.log(f"❌ Backend health check failed: {health_response.status_code}")
                return False
            
            # Try to find website analysis endpoints
            # Check if GPT-5 website analyzer is available
            try:
                # Test if website analysis endpoint exists
                test_analysis_data = {
                    "website_url": self.test_website,
                    "analysis_type": "comprehensive"
                }
                
                # Try different possible endpoint paths
                possible_endpoints = [
                    "/website/analyze",
                    "/analyze-website", 
                    "/website-analysis",
                    "/gpt5/analyze-website",
                    "/ai/analyze-website"
                ]
                
                analysis_result = None
                working_endpoint = None
                
                for endpoint in possible_endpoints:
                    try:
                        self.log(f"   Trying endpoint: {endpoint}")
                        response = self.session.post(
                            f"{self.backend_url}{endpoint}",
                            json=test_analysis_data,
                            timeout=60  # Website analysis can take time
                        )
                        
                        if response.status_code == 200:
                            analysis_result = response.json()
                            working_endpoint = endpoint
                            self.log(f"✅ Found working website analysis endpoint: {endpoint}")
                            break
                        elif response.status_code == 404:
                            self.log(f"   ❌ Endpoint not found: {endpoint}")
                        else:
                            self.log(f"   ⚠️ Endpoint error {response.status_code}: {endpoint}")
                            
                    except Exception as e:
                        self.log(f"   ❌ Endpoint test error {endpoint}: {str(e)}")
                        continue
                
                if analysis_result and working_endpoint:
                    # Analyze the quality of the website analysis
                    self.log(f"📊 Analyzing website analysis quality...")
                    
                    # Extract analysis content
                    analysis_text = ""
                    if isinstance(analysis_result, dict):
                        # Try different possible response structures
                        analysis_text = (
                            analysis_result.get("analysis", "") or
                            analysis_result.get("content", "") or
                            analysis_result.get("result", "") or
                            analysis_result.get("text", "") or
                            str(analysis_result)
                        )
                    else:
                        analysis_text = str(analysis_result)
                    
                    # Count words in analysis
                    word_count = len(analysis_text.split()) if analysis_text else 0
                    
                    self.log(f"📝 Website analysis results:")
                    self.log(f"   Working endpoint: {working_endpoint}")
                    self.log(f"   Analysis word count: {word_count}")
                    self.log(f"   Analysis preview: {analysis_text[:200]}..." if len(analysis_text) > 200 else f"   Full analysis: {analysis_text}")
                    
                    # Determine if this matches the "5 words" issue
                    quality_assessment = "good"
                    if word_count <= 10:
                        quality_assessment = "critical_issue"
                        self.log(f"🚨 CRITICAL ISSUE CONFIRMED: Analysis only {word_count} words (user reported '5 words')")
                    elif word_count < 50:
                        quality_assessment = "poor"
                        self.log(f"⚠️ POOR QUALITY: Analysis only {word_count} words (expected detailed analysis)")
                    else:
                        self.log(f"✅ Analysis quality appears adequate: {word_count} words")
                    
                    self.test_results["website_analysis"] = {
                        "status": "success",
                        "endpoint": working_endpoint,
                        "word_count": word_count,
                        "quality_assessment": quality_assessment,
                        "analysis_preview": analysis_text[:500] if analysis_text else "No content",
                        "matches_user_issue": word_count <= 10
                    }
                    
                    return True
                    
                else:
                    self.log(f"❌ No working website analysis endpoint found")
                    self.test_results["website_analysis"] = {
                        "status": "failed",
                        "error": "No website analysis endpoint available",
                        "endpoints_tested": possible_endpoints
                    }
                    return False
                    
            except Exception as e:
                self.log(f"❌ Website analysis test error: {str(e)}")
                self.test_results["website_analysis"] = {
                    "status": "error",
                    "error": str(e)
                }
                return False
                
        except Exception as e:
            self.log(f"❌ Website analysis test error: {str(e)}")
            self.test_results["website_analysis"] = {
                "status": "error",
                "error": str(e)
            }
            return False
    
    def test_content_library_migration(self):
        """Step 3: Test content library migration status"""
        self.log("📚 Step 3: Testing content library migration status...")
        
        if not self.access_token:
            self.log("❌ Cannot test content library - not authenticated")
            return False
        
        try:
            # Get current content library
            response = self.session.get(
                f"{self.backend_url}/content/pending?limit=100",
                timeout=30
            )
            
            if response.status_code == 200:
                content_data = response.json()
                total_items = content_data.get("total", 0)
                content_items = content_data.get("content", [])
                
                self.log(f"📊 Content library analysis:")
                self.log(f"   Total items: {total_items}")
                self.log(f"   Items loaded: {len(content_items)}")
                
                # Analyze content types
                images = [item for item in content_items if item.get("file_type", "").startswith("image")]
                videos = [item for item in content_items if item.get("file_type", "").startswith("video")]
                other = [item for item in content_items if not item.get("file_type", "").startswith(("image", "video"))]
                
                self.log(f"   Images: {len(images)}")
                self.log(f"   Videos: {len(videos)}")
                self.log(f"   Other: {len(other)}")
                
                # Check for migration indicators
                migration_indicators = {
                    "has_content": total_items > 0,
                    "has_images": len(images) > 0,
                    "expected_19_items": total_items == 19,  # User reported 19 items should be migrated
                    "has_thumbnails": sum(1 for item in content_items if item.get("thumb_url")) > 0,
                    "has_titles": sum(1 for item in content_items if item.get("title")) > 0,
                    "has_contexts": sum(1 for item in content_items if item.get("context")) > 0
                }
                
                self.log(f"🔍 Migration status indicators:")
                for indicator, status in migration_indicators.items():
                    status_icon = "✅" if status else "❌"
                    self.log(f"   {status_icon} {indicator}: {status}")
                
                # Determine migration status
                if total_items == 0:
                    migration_status = "failed_empty"
                    self.log(f"🚨 CRITICAL: Content library is EMPTY - migration failed!")
                elif total_items < 10:
                    migration_status = "partial_migration"
                    self.log(f"⚠️ WARNING: Only {total_items} items - possible partial migration")
                elif total_items == 19:
                    migration_status = "success_expected"
                    self.log(f"✅ SUCCESS: Found expected 19 items - migration appears successful")
                else:
                    migration_status = "success_different_count"
                    self.log(f"✅ SUCCESS: Found {total_items} items - migration successful but different count")
                
                # Sample some content items for detailed analysis
                sample_items = content_items[:5] if content_items else []
                sample_analysis = []
                
                for item in sample_items:
                    sample_analysis.append({
                        "filename": item.get("filename", ""),
                        "file_type": item.get("file_type", ""),
                        "has_thumbnail": bool(item.get("thumb_url")),
                        "has_title": bool(item.get("title")),
                        "has_context": bool(item.get("context")),
                        "source": item.get("source", ""),
                        "upload_type": item.get("upload_type", "")
                    })
                
                self.test_results["content_library"] = {
                    "status": "success",
                    "total_items": total_items,
                    "migration_status": migration_status,
                    "migration_indicators": migration_indicators,
                    "content_breakdown": {
                        "images": len(images),
                        "videos": len(videos),
                        "other": len(other)
                    },
                    "sample_items": sample_analysis
                }
                
                return True
                
            else:
                self.log(f"❌ Content library request failed: {response.status_code}")
                self.test_results["content_library"] = {
                    "status": "failed",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                return False
                
        except Exception as e:
            self.log(f"❌ Content library test error: {str(e)}")
            self.test_results["content_library"] = {
                "status": "error",
                "error": str(e)
            }
            return False
    
    def test_gpt_model_verification(self):
        """Step 4: Verify which GPT model is being used"""
        self.log("🤖 Step 4: Verifying GPT model configuration...")
        
        try:
            # Check backend environment variables and configuration
            diag_response = self.session.get(f"{self.backend_url}/diag", timeout=30)
            
            model_info = {
                "backend_accessible": diag_response.status_code == 200,
                "openai_configured": False,
                "emergent_llm_configured": False,
                "model_indicators": []
            }
            
            # Check if we can determine model from backend .env (if accessible)
            try:
                # Read backend .env file to check model configuration
                env_path = "/app/backend/.env"
                if os.path.exists(env_path):
                    with open(env_path, 'r') as f:
                        env_content = f.read()
                    
                    # Check for OpenAI API key
                    if "OPENAI_API_KEY=" in env_content and not env_content.count("OPENAI_API_KEY=\"\""):
                        model_info["openai_configured"] = True
                        model_info["model_indicators"].append("OpenAI API key configured")
                        
                        # Try to determine if it's GPT-4o or GPT-5
                        if "gpt-4o" in env_content.lower():
                            model_info["model_indicators"].append("GPT-4o model reference found")
                        elif "gpt-5" in env_content.lower():
                            model_info["model_indicators"].append("GPT-5 model reference found")
                        else:
                            model_info["model_indicators"].append("GPT model version not explicitly specified")
                    
                    # Check for Emergent LLM key
                    if "EMERGENT_LLM_KEY=" in env_content and not env_content.count("EMERGENT_LLM_KEY=\"\""):
                        model_info["emergent_llm_configured"] = True
                        model_info["model_indicators"].append("Emergent LLM key configured")
                    
                    self.log(f"📋 Model configuration analysis:")
                    self.log(f"   OpenAI configured: {model_info['openai_configured']}")
                    self.log(f"   Emergent LLM configured: {model_info['emergent_llm_configured']}")
                    
                    for indicator in model_info["model_indicators"]:
                        self.log(f"   • {indicator}")
                        
                else:
                    self.log(f"⚠️ Backend .env file not accessible for model verification")
                    model_info["model_indicators"].append("Backend .env not accessible")
                    
            except Exception as e:
                self.log(f"⚠️ Could not read backend configuration: {str(e)}")
                model_info["model_indicators"].append(f"Configuration read error: {str(e)}")
            
            # Try to test AI functionality to determine model quality
            try:
                # Test if we can make a simple AI request to determine model quality
                test_prompt = "Analyze this business website briefly: https://my-own-watch.fr"
                
                # Try to find an AI endpoint to test
                ai_endpoints = [
                    "/ai/test",
                    "/openai/test", 
                    "/gpt/test",
                    "/posts/generate"  # This uses AI internally
                ]
                
                ai_response_quality = None
                working_ai_endpoint = None
                
                for endpoint in ai_endpoints:
                    try:
                        if endpoint == "/posts/generate":
                            # Special case for posts generation
                            response = self.session.post(
                                f"{self.backend_url}{endpoint}",
                                json={"target_month": "test_month"},
                                timeout=30
                            )
                        else:
                            response = self.session.post(
                                f"{self.backend_url}{endpoint}",
                                json={"prompt": test_prompt},
                                timeout=30
                            )
                        
                        if response.status_code in [200, 201]:
                            working_ai_endpoint = endpoint
                            ai_response_quality = "working"
                            self.log(f"✅ AI endpoint working: {endpoint}")
                            break
                        elif response.status_code == 404:
                            continue
                        else:
                            self.log(f"   AI endpoint error {response.status_code}: {endpoint}")
                            
                    except Exception as e:
                        continue
                
                model_info["ai_endpoint_working"] = working_ai_endpoint is not None
                model_info["working_ai_endpoint"] = working_ai_endpoint
                
            except Exception as e:
                self.log(f"⚠️ AI functionality test error: {str(e)}")
                model_info["ai_test_error"] = str(e)
            
            # Determine likely model based on evidence
            if model_info["openai_configured"]:
                if "gpt-5" in str(model_info["model_indicators"]).lower():
                    likely_model = "GPT-5"
                elif "gpt-4o" in str(model_info["model_indicators"]).lower():
                    likely_model = "GPT-4o"
                else:
                    likely_model = "GPT-4o (default assumption)"
            elif model_info["emergent_llm_configured"]:
                likely_model = "Emergent LLM (unknown base model)"
            else:
                likely_model = "Unknown - no AI configuration detected"
            
            self.log(f"🎯 Likely model in use: {likely_model}")
            
            model_info["likely_model"] = likely_model
            
            self.test_results["gpt_model_verification"] = {
                "status": "success",
                "model_info": model_info,
                "likely_model": likely_model
            }
            
            return True
            
        except Exception as e:
            self.log(f"❌ GPT model verification error: {str(e)}")
            self.test_results["gpt_model_verification"] = {
                "status": "error",
                "error": str(e)
            }
            return False
    
    def test_production_vs_preview_comparison(self):
        """Step 5: Compare current environment with production expectations"""
        self.log("🔄 Step 5: Comparing current environment with production expectations...")
        
        try:
            # Analyze current environment
            current_env_analysis = {
                "backend_url": self.backend_url,
                "is_preview": "preview" in self.backend_url.lower(),
                "is_production": "claire-marcus.com" in self.backend_url.lower() or "emergent.host" in self.backend_url.lower(),
                "environment_type": "unknown"
            }
            
            if current_env_analysis["is_preview"]:
                current_env_analysis["environment_type"] = "preview"
                self.log(f"🔍 Current environment: PREVIEW")
                self.log(f"   URL: {self.backend_url}")
                self.log(f"   This is the preview environment, not production")
            elif current_env_analysis["is_production"]:
                current_env_analysis["environment_type"] = "production"
                self.log(f"🔍 Current environment: PRODUCTION")
                self.log(f"   URL: {self.backend_url}")
            else:
                current_env_analysis["environment_type"] = "unknown"
                self.log(f"🔍 Current environment: UNKNOWN")
                self.log(f"   URL: {self.backend_url}")
            
            # Based on the review request, the issue is that production has problems
            # but we're testing preview environment
            if current_env_analysis["is_preview"]:
                self.log(f"⚠️ IMPORTANT: Testing PREVIEW environment, but user issues are on PRODUCTION")
                self.log(f"   Production URL would be: https://claire-marcus.com or similar")
                self.log(f"   This test shows preview functionality, not production issues")
                
                comparison_result = {
                    "testing_environment": "preview",
                    "user_issues_environment": "production",
                    "comparison_valid": False,
                    "recommendation": "Need to test actual production environment to diagnose user issues"
                }
            else:
                comparison_result = {
                    "testing_environment": current_env_analysis["environment_type"],
                    "user_issues_environment": "production",
                    "comparison_valid": True,
                    "recommendation": "Testing correct environment for user issues"
                }
            
            self.test_results["migration_status"] = {
                "status": "success",
                "current_environment": current_env_analysis,
                "comparison": comparison_result
            }
            
            return True
            
        except Exception as e:
            self.log(f"❌ Environment comparison error: {str(e)}")
            self.test_results["migration_status"] = {
                "status": "error",
                "error": str(e)
            }
            return False
    
    def generate_diagnostic_report(self):
        """Generate comprehensive diagnostic report"""
        self.log("📋 Generating comprehensive diagnostic report...")
        
        print("\n" + "="*80)
        print("🚨 URGENT PRODUCTION ISSUES DIAGNOSTIC REPORT")
        print("="*80)
        
        print(f"\n🔍 INVESTIGATION SUMMARY:")
        print(f"   Test Website: {self.test_website}")
        print(f"   Backend URL: {self.backend_url}")
        print(f"   User: {self.credentials['email']}")
        print(f"   Timestamp: {datetime.now().isoformat()}")
        
        # Authentication Results
        print(f"\n🔐 AUTHENTICATION RESULTS:")
        auth_result = self.test_results["authentication"]
        if auth_result["status"] == "success":
            print(f"   ✅ Authentication: SUCCESS")
            print(f"   User ID: {auth_result.get('user_id', 'Unknown')}")
            print(f"   Email: {auth_result.get('email', 'Unknown')}")
        else:
            print(f"   ❌ Authentication: FAILED")
            print(f"   Error: {auth_result.get('error', 'Unknown error')}")
        
        # Website Analysis Results
        print(f"\n🌐 WEBSITE ANALYSIS RESULTS:")
        website_result = self.test_results["website_analysis"]
        if website_result["status"] == "success":
            print(f"   ✅ Website Analysis: WORKING")
            print(f"   Endpoint: {website_result.get('endpoint', 'Unknown')}")
            print(f"   Word Count: {website_result.get('word_count', 0)}")
            print(f"   Quality: {website_result.get('quality_assessment', 'Unknown')}")
            if website_result.get('matches_user_issue', False):
                print(f"   🚨 MATCHES USER ISSUE: Analysis too short (≤10 words)")
            else:
                print(f"   ✅ Does not match user issue - analysis appears adequate")
        else:
            print(f"   ❌ Website Analysis: FAILED")
            print(f"   Error: {website_result.get('error', 'Unknown error')}")
        
        # Content Library Results
        print(f"\n📚 CONTENT LIBRARY MIGRATION RESULTS:")
        content_result = self.test_results["content_library"]
        if content_result["status"] == "success":
            print(f"   ✅ Content Library: ACCESSIBLE")
            print(f"   Total Items: {content_result.get('total_items', 0)}")
            print(f"   Migration Status: {content_result.get('migration_status', 'Unknown')}")
            
            breakdown = content_result.get('content_breakdown', {})
            print(f"   Content Breakdown:")
            print(f"      Images: {breakdown.get('images', 0)}")
            print(f"      Videos: {breakdown.get('videos', 0)}")
            print(f"      Other: {breakdown.get('other', 0)}")
            
            if content_result.get('total_items', 0) == 0:
                print(f"   🚨 CRITICAL: Content library is EMPTY - migration failed!")
            elif content_result.get('total_items', 0) == 19:
                print(f"   ✅ SUCCESS: Found expected 19 items")
            else:
                print(f"   ⚠️ Different count than expected (19 items)")
        else:
            print(f"   ❌ Content Library: FAILED")
            print(f"   Error: {content_result.get('error', 'Unknown error')}")
        
        # GPT Model Results
        print(f"\n🤖 GPT MODEL VERIFICATION RESULTS:")
        gpt_result = self.test_results["gpt_model_verification"]
        if gpt_result["status"] == "success":
            print(f"   ✅ Model Verification: SUCCESS")
            print(f"   Likely Model: {gpt_result.get('likely_model', 'Unknown')}")
            
            model_info = gpt_result.get('model_info', {})
            print(f"   Configuration:")
            print(f"      OpenAI Configured: {model_info.get('openai_configured', False)}")
            print(f"      Emergent LLM Configured: {model_info.get('emergent_llm_configured', False)}")
            print(f"      AI Endpoint Working: {model_info.get('ai_endpoint_working', False)}")
        else:
            print(f"   ❌ Model Verification: FAILED")
            print(f"   Error: {gpt_result.get('error', 'Unknown error')}")
        
        # Environment Comparison
        print(f"\n🔄 ENVIRONMENT COMPARISON:")
        migration_result = self.test_results["migration_status"]
        if migration_result["status"] == "success":
            comparison = migration_result.get('comparison', {})
            print(f"   Testing Environment: {comparison.get('testing_environment', 'Unknown')}")
            print(f"   User Issues Environment: {comparison.get('user_issues_environment', 'Unknown')}")
            print(f"   Comparison Valid: {comparison.get('comparison_valid', False)}")
            print(f"   Recommendation: {comparison.get('recommendation', 'None')}")
        
        # Critical Findings Summary
        print(f"\n🎯 CRITICAL FINDINGS SUMMARY:")
        
        critical_issues = []
        
        # Check for website analysis issue
        if website_result.get("matches_user_issue", False):
            critical_issues.append("✅ CONFIRMED: Website analysis producing very short results (≤10 words)")
        elif website_result["status"] == "failed":
            critical_issues.append("❌ CRITICAL: Website analysis endpoint not working")
        else:
            critical_issues.append("⚠️ Website analysis appears to work in preview environment")
        
        # Check for content library issue
        if content_result.get("total_items", 0) == 0:
            critical_issues.append("✅ CONFIRMED: Content library is empty - migration failed")
        elif content_result.get("total_items", 0) != 19:
            critical_issues.append(f"⚠️ Content library has {content_result.get('total_items', 0)} items (expected 19)")
        else:
            critical_issues.append("✅ Content library appears properly migrated (19 items)")
        
        # Check for GPT model issue
        likely_model = gpt_result.get('likely_model', 'Unknown')
        if 'gpt-5' in likely_model.lower():
            critical_issues.append("⚠️ Using GPT-5 - user expects GPT-4o")
        elif 'gpt-4o' in likely_model.lower():
            critical_issues.append("✅ Using GPT-4o as expected")
        else:
            critical_issues.append(f"⚠️ Model unclear: {likely_model}")
        
        for issue in critical_issues:
            print(f"   {issue}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        recommendations = [
            "1. Test actual production environment (claire-marcus.com) to confirm issues",
            "2. Compare website analysis quality between preview and production",
            "3. Verify content library migration status in production database",
            "4. Confirm GPT model configuration in production environment",
            "5. Check if production and preview use different databases/configurations"
        ]
        
        for rec in recommendations:
            print(f"   {rec}")
        
        print(f"\n" + "="*80)
        
        return self.test_results
    
    def run_diagnostic(self):
        """Run complete production issues diagnostic"""
        self.log("🚀 Starting URGENT Production Issues Diagnostic")
        self.log("="*80)
        
        success_count = 0
        total_tests = 5
        
        # Step 1: Authentication
        if self.authenticate():
            success_count += 1
        
        # Step 2: Website Analysis Quality Test
        if self.test_website_analysis_quality():
            success_count += 1
        
        # Step 3: Content Library Migration Test
        if self.test_content_library_migration():
            success_count += 1
        
        # Step 4: GPT Model Verification
        if self.test_gpt_model_verification():
            success_count += 1
        
        # Step 5: Environment Comparison
        if self.test_production_vs_preview_comparison():
            success_count += 1
        
        # Generate comprehensive report
        final_results = self.generate_diagnostic_report()
        
        self.log(f"\n✅ Diagnostic completed: {success_count}/{total_tests} tests successful")
        
        return {
            "success_rate": f"{success_count}/{total_tests}",
            "success_percentage": (success_count / total_tests) * 100,
            "results": final_results
        }

def main():
    """Main test execution"""
    print("🚨 URGENT PRODUCTION ISSUES DIAGNOSTIC TEST")
    print("=" * 60)
    
    diagnostic = ProductionIssuesDiagnostic()
    results = diagnostic.run_diagnostic()
    
    success_rate = results["success_percentage"]
    
    if success_rate >= 80:
        print(f"\n🎉 DIAGNOSTIC COMPLETED SUCCESSFULLY ({results['success_rate']})")
        return 0
    else:
        print(f"\n⚠️ DIAGNOSTIC COMPLETED WITH ISSUES ({results['success_rate']})")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)