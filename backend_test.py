#!/usr/bin/env python3
"""
Backend Test for Restaurant Test User Data Verification
Testing endpoints for test@claire-marcus.com to verify migrated data accessibility
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://claire-marcus.com/api"
TEST_USER_EMAIL = "test@claire-marcus.com"
TEST_USER_PASSWORD = "test123!"
TEST_USER_ID = "82ce1284-ca2e-469a-8521-2a9116ef7826"

class RestaurantDataTester:
    def __init__(self):
        self.session = requests.Session()
        self.jwt_token = None
        self.user_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    def test_authentication(self):
        """Test 1: Authentication with test user credentials"""
        print(f"\n🔐 Testing Authentication with {TEST_USER_EMAIL}")
        
        try:
            auth_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json=auth_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.jwt_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                if self.jwt_token and self.user_id == TEST_USER_ID:
                    self.log_test(
                        "Authentication", 
                        True, 
                        f"Successfully authenticated user {self.user_id}",
                        {"token_length": len(self.jwt_token), "user_id": self.user_id}
                    )
                    
                    # Set authorization header for subsequent requests
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.jwt_token}"
                    })
                    return True
                else:
                    self.log_test(
                        "Authentication", 
                        False, 
                        f"Invalid response data: token={bool(self.jwt_token)}, user_id={self.user_id}",
                        data
                    )
                    return False
            else:
                error_msg = response.text
                self.log_test(
                    "Authentication", 
                    False, 
                    f"HTTP {response.status_code}: {error_msg}",
                    {"status_code": response.status_code, "response": error_msg}
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Authentication", 
                False, 
                f"Exception during authentication: {str(e)}",
                {"exception": str(e)}
            )
            return False
    
    def test_generated_posts(self):
        """Test 2: GET /api/posts/generated - Should return 33 posts"""
        print(f"\n📝 Testing Generated Posts Endpoint")
        
        if not self.jwt_token:
            self.log_test("Generated Posts", False, "No JWT token available")
            return False
            
        try:
            response = self.session.get(
                f"{BACKEND_URL}/posts/generated",
                timeout=30
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                count = data.get("count", len(posts))
                
                print(f"   Posts returned: {len(posts)}")
                print(f"   Count field: {count}")
                
                # Verify structure and content
                if len(posts) >= 33:
                    # Check first few posts for required fields
                    valid_posts = 0
                    for i, post in enumerate(posts[:5]):  # Check first 5 posts
                        has_title = bool(post.get("title"))
                        has_platform = bool(post.get("platform"))
                        has_status = bool(post.get("status"))
                        has_scheduled_date = bool(post.get("scheduled_date"))
                        
                        if has_title and has_platform and has_status and has_scheduled_date:
                            valid_posts += 1
                            
                        print(f"   Post {i+1}: title={has_title}, platform={has_platform}, status={has_status}, scheduled_date={has_scheduled_date}")
                    
                    if valid_posts >= 3:
                        self.log_test(
                            "Generated Posts", 
                            True, 
                            f"Successfully retrieved {len(posts)} posts with valid structure",
                            {
                                "total_posts": len(posts),
                                "count_field": count,
                                "valid_posts_checked": valid_posts,
                                "sample_post": posts[0] if posts else None
                            }
                        )
                        return True
                    else:
                        self.log_test(
                            "Generated Posts", 
                            False, 
                            f"Posts missing required fields. Only {valid_posts}/5 posts have complete structure",
                            {"posts_sample": posts[:3]}
                        )
                        return False
                else:
                    self.log_test(
                        "Generated Posts", 
                        False, 
                        f"Expected at least 33 posts, got {len(posts)}",
                        {"actual_count": len(posts), "response_data": data}
                    )
                    return False
                    
            else:
                error_msg = response.text
                self.log_test(
                    "Generated Posts", 
                    False, 
                    f"HTTP {response.status_code}: {error_msg}",
                    {"status_code": response.status_code, "response": error_msg}
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Generated Posts", 
                False, 
                f"Exception during posts retrieval: {str(e)}",
                {"exception": str(e)}
            )
            return False
    
    def test_website_analysis(self):
        """Test 3: GET /api/website-analysis - Should return at least 1 analysis"""
        print(f"\n🔍 Testing Website Analysis Endpoint")
        
        if not self.jwt_token:
            self.log_test("Website Analysis", False, "No JWT token available")
            return False
            
        try:
            response = self.session.get(
                f"{BACKEND_URL}/website-analysis",
                timeout=30
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                analyses = data.get("analyses", [])
                count = data.get("count", len(analyses))
                
                print(f"   Analyses returned: {len(analyses)}")
                print(f"   Count field: {count}")
                
                if len(analyses) >= 1:
                    # Check first analysis for required fields
                    analysis = analyses[0]
                    has_website_url = bool(analysis.get("website_url"))
                    has_seo_score = analysis.get("seo_score") is not None
                    has_overall_score = analysis.get("overall_score") is not None
                    
                    print(f"   Analysis 1: website_url={has_website_url}, seo_score={has_seo_score}, overall_score={has_overall_score}")
                    
                    if has_website_url and has_seo_score and has_overall_score:
                        self.log_test(
                            "Website Analysis", 
                            True, 
                            f"Successfully retrieved {len(analyses)} analyses with valid structure",
                            {
                                "total_analyses": len(analyses),
                                "count_field": count,
                                "sample_analysis": analysis
                            }
                        )
                        return True
                    else:
                        self.log_test(
                            "Website Analysis", 
                            False, 
                            f"Analysis missing required fields: website_url={has_website_url}, seo_score={has_seo_score}, overall_score={has_overall_score}",
                            {"analysis_sample": analysis}
                        )
                        return False
                else:
                    self.log_test(
                        "Website Analysis", 
                        False, 
                        f"Expected at least 1 analysis, got {len(analyses)}",
                        {"actual_count": len(analyses), "response_data": data}
                    )
                    return False
                    
            else:
                error_msg = response.text
                self.log_test(
                    "Website Analysis", 
                    False, 
                    f"HTTP {response.status_code}: {error_msg}",
                    {"status_code": response.status_code, "response": error_msg}
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Website Analysis", 
                False, 
                f"Exception during analysis retrieval: {str(e)}",
                {"exception": str(e)}
            )
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🎯 RESTAURANT TEST USER DATA VERIFICATION")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_USER_EMAIL}")
        print(f"Expected User ID: {TEST_USER_ID}")
        print("=" * 60)
        
        # Test 1: Authentication
        auth_success = self.test_authentication()
        
        # Test 2: Generated Posts (only if auth successful)
        posts_success = False
        if auth_success:
            posts_success = self.test_generated_posts()
        
        # Test 3: Website Analysis (only if auth successful)
        analysis_success = False
        if auth_success:
            analysis_success = self.test_website_analysis()
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status}: {result['test']} - {result['message']}")
        
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        
        # Determine overall success
        critical_tests_passed = auth_success and posts_success and analysis_success
        
        if critical_tests_passed:
            print("🎉 ALL CRITICAL TESTS PASSED - Restaurant data is accessible!")
            return True
        else:
            print("❌ CRITICAL TESTS FAILED - Restaurant data access issues detected")
            return False

def main():
    """Main test execution"""
    tester = RestaurantDataTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()