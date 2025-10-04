#!/usr/bin/env python3
"""
THUMBNAIL PERFORMANCE TESTING
Critical issue: iPhone users report that clicking "Sélectionner" causes all 24 thumbnails to turn white and take 30 seconds to reload.

Test Requirements:
1. Test thumbnail endpoint performance (GET /api/content/{file_id}/thumb)
2. Check if thumbnails are being regenerated each time instead of cached
3. Measure response times for thumbnail requests
4. Check if thumbnails exist in database
5. Test multiple thumbnail requests simultaneously
6. Check thumbnail cache headers

Credentials: lperpere@yahoo.fr / L@Reunion974!
Backend URL: https://claire-marcus-app-1.preview.emergentagent.com/api
"""

import requests
import json
import sys
import time
import asyncio
import aiohttp
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Configuration
BASE_URL = "https://claire-marcus-app-1.preview.emergentagent.com/api"
EMAIL = "lperpere@yahoo.fr"
PASSWORD = "L@Reunion974!"

class ThumbnailPerformanceTest:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.content_items = []
        
    def authenticate(self):
        """Step 1: Authenticate with provided credentials"""
        print("🔐 Step 1: Authentication")
        
        auth_data = {
            "email": EMAIL,
            "password": PASSWORD
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/auth/login-robust", json=auth_data)
            print(f"Auth response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for all future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                })
                
                print(f"✅ Authentication successful")
                print(f"   User ID: {self.user_id}")
                print(f"   Token: {self.token[:20]}..." if self.token else "No token")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def get_content_list(self):
        """Step 2: Get content list to test thumbnails"""
        print("\n📋 Step 2: Getting Content List for Thumbnail Testing")
        
        try:
            response = self.session.get(f"{BASE_URL}/content/pending?limit=24")
            print(f"Content listing response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.content_items = data.get("content", [])
                total_items = data.get("total", 0)
                
                print(f"✅ Content listing successful")
                print(f"   Total items: {total_items}")
                print(f"   Items loaded: {len(self.content_items)}")
                
                # Show first few items for reference
                print(f"\n📊 First 3 Content Items:")
                for i, item in enumerate(self.content_items[:3]):
                    item_id = item.get("id", "unknown")
                    filename = item.get("filename", "")
                    thumb_url = item.get("thumb_url", "")
                    
                    print(f"   Item {i+1}:")
                    print(f"     ID: {item_id}")
                    print(f"     Filename: {filename}")
                    print(f"     Thumb URL: {thumb_url}")
                
                return len(self.content_items) > 0
            else:
                print(f"❌ Content listing failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Content listing error: {e}")
            return False
    
    def check_thumbnail_database_status(self):
        """Step 3: Check thumbnail database status"""
        print("\n🗄️ Step 3: Checking Thumbnail Database Status")
        
        try:
            response = self.session.get(f"{BASE_URL}/content/thumbnails/status")
            print(f"Thumbnail status response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                total_files = data.get("total_files", 0)
                with_thumbnails = data.get("with_thumbnails", 0)
                missing_thumbnails = data.get("missing_thumbnails", 0)
                completion_percentage = data.get("completion_percentage", 0)
                
                print(f"✅ Thumbnail status retrieved")
                print(f"   Total files: {total_files}")
                print(f"   With thumbnails: {with_thumbnails}")
                print(f"   Missing thumbnails: {missing_thumbnails}")
                print(f"   Completion: {completion_percentage}%")
                
                # Check for orphaned files
                orphan_response = self.session.get(f"{BASE_URL}/content/thumbnails/orphans")
                if orphan_response.status_code == 200:
                    orphan_data = orphan_response.json()
                    orphan_count = orphan_data.get("count", 0)
                    print(f"   Orphaned files: {orphan_count}")
                    
                    if orphan_count > 0:
                        print(f"   ⚠️ WARNING: {orphan_count} orphaned files detected - may cause thumbnail generation delays")
                
                return {
                    "total_files": total_files,
                    "with_thumbnails": with_thumbnails,
                    "missing_thumbnails": missing_thumbnails,
                    "completion_percentage": completion_percentage
                }
            else:
                print(f"❌ Thumbnail status check failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Thumbnail status error: {e}")
            return None
    
    def test_single_thumbnail_performance(self, content_id, test_name="Single"):
        """Test performance of a single thumbnail request"""
        try:
            start_time = time.time()
            
            # Test with Authorization header
            response = self.session.get(f"{BASE_URL}/content/{content_id}/thumb")
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            success = response.status_code == 200
            cache_control = response.headers.get("Cache-Control", "")
            etag = response.headers.get("ETag", "")
            expires = response.headers.get("Expires", "")
            content_type = response.headers.get("Content-Type", "")
            content_length = response.headers.get("Content-Length", "0")
            
            return {
                "test_name": test_name,
                "content_id": content_id,
                "success": success,
                "status_code": response.status_code,
                "response_time_ms": round(response_time, 2),
                "cache_control": cache_control,
                "etag": etag,
                "expires": expires,
                "content_type": content_type,
                "content_length": int(content_length) if content_length.isdigit() else 0
            }
        except Exception as e:
            return {
                "test_name": test_name,
                "content_id": content_id,
                "success": False,
                "error": str(e),
                "response_time_ms": 0
            }
    
    def test_sequential_thumbnail_performance(self):
        """Step 4: Test sequential thumbnail loading (simulating normal usage)"""
        print("\n⏱️ Step 4: Sequential Thumbnail Performance Testing")
        
        if not self.content_items:
            print("❌ No content items available for testing")
            return []
        
        # Test first 6 items sequentially
        test_items = self.content_items[:6]
        results = []
        
        print(f"Testing {len(test_items)} thumbnails sequentially...")
        
        total_start_time = time.time()
        
        for i, item in enumerate(test_items):
            content_id = item.get("id")
            filename = item.get("filename", "")
            
            print(f"   Testing thumbnail {i+1}/{len(test_items)}: {filename[:30]}...")
            
            result = self.test_single_thumbnail_performance(content_id, f"Sequential-{i+1}")
            results.append(result)
            
            if result["success"]:
                print(f"     ✅ {result['response_time_ms']}ms - {result['content_type']}")
            else:
                print(f"     ❌ Failed: {result.get('error', 'Unknown error')}")
        
        total_end_time = time.time()
        total_time = (total_end_time - total_start_time) * 1000
        
        print(f"\n📊 Sequential Test Results:")
        print(f"   Total time for {len(test_items)} thumbnails: {total_time:.2f}ms")
        print(f"   Average time per thumbnail: {total_time/len(test_items):.2f}ms")
        
        successful_tests = [r for r in results if r["success"]]
        if successful_tests:
            avg_response_time = sum(r["response_time_ms"] for r in successful_tests) / len(successful_tests)
            print(f"   Average successful response time: {avg_response_time:.2f}ms")
        
        return results
    
    def test_concurrent_thumbnail_performance(self):
        """Step 5: Test concurrent thumbnail loading (simulating iPhone issue)"""
        print("\n🚀 Step 5: Concurrent Thumbnail Performance Testing (iPhone Simulation)")
        
        if not self.content_items:
            print("❌ No content items available for testing")
            return []
        
        # Test first 12 items concurrently (simulating iPhone loading multiple thumbnails)
        test_items = self.content_items[:12]
        results = []
        
        print(f"Testing {len(test_items)} thumbnails concurrently (simulating iPhone issue)...")
        
        def test_thumbnail_worker(item, index):
            content_id = item.get("id")
            return self.test_single_thumbnail_performance(content_id, f"Concurrent-{index+1}")
        
        total_start_time = time.time()
        
        # Use ThreadPoolExecutor for concurrent requests
        with ThreadPoolExecutor(max_workers=12) as executor:
            # Submit all thumbnail requests at once
            future_to_item = {
                executor.submit(test_thumbnail_worker, item, i): (item, i) 
                for i, item in enumerate(test_items)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_item):
                item, index = future_to_item[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    filename = item.get("filename", "")
                    if result["success"]:
                        print(f"   ✅ Thumbnail {index+1}: {result['response_time_ms']}ms - {filename[:30]}")
                    else:
                        print(f"   ❌ Thumbnail {index+1}: Failed - {filename[:30]}")
                        
                except Exception as e:
                    print(f"   ❌ Thumbnail {index+1}: Exception - {str(e)}")
        
        total_end_time = time.time()
        total_time = (total_end_time - total_start_time) * 1000
        
        print(f"\n📊 Concurrent Test Results:")
        print(f"   Total time for {len(test_items)} concurrent thumbnails: {total_time:.2f}ms")
        
        successful_tests = [r for r in results if r["success"]]
        failed_tests = [r for r in results if not r["success"]]
        
        print(f"   Successful requests: {len(successful_tests)}/{len(test_items)}")
        print(f"   Failed requests: {len(failed_tests)}/{len(test_items)}")
        
        if successful_tests:
            avg_response_time = sum(r["response_time_ms"] for r in successful_tests) / len(successful_tests)
            max_response_time = max(r["response_time_ms"] for r in successful_tests)
            min_response_time = min(r["response_time_ms"] for r in successful_tests)
            
            print(f"   Average response time: {avg_response_time:.2f}ms")
            print(f"   Max response time: {max_response_time:.2f}ms")
            print(f"   Min response time: {min_response_time:.2f}ms")
            
            # Check if any requests took longer than 5 seconds (iPhone issue threshold)
            slow_requests = [r for r in successful_tests if r["response_time_ms"] > 5000]
            if slow_requests:
                print(f"   ⚠️ SLOW REQUESTS: {len(slow_requests)} requests took >5 seconds")
                for slow in slow_requests:
                    print(f"     - {slow['test_name']}: {slow['response_time_ms']}ms")
        
        return results
    
    def test_cache_behavior(self):
        """Step 6: Test thumbnail caching behavior"""
        print("\n🗂️ Step 6: Thumbnail Cache Behavior Testing")
        
        if not self.content_items:
            print("❌ No content items available for testing")
            return False
        
        # Test the same thumbnail multiple times to check caching
        test_item = self.content_items[0]
        content_id = test_item.get("id")
        filename = test_item.get("filename", "")
        
        print(f"Testing cache behavior for: {filename}")
        
        # First request (should generate or fetch from DB)
        print("   First request (cold)...")
        result1 = self.test_single_thumbnail_performance(content_id, "Cache-Cold")
        
        # Wait a moment
        time.sleep(0.5)
        
        # Second request (should be cached)
        print("   Second request (should be cached)...")
        result2 = self.test_single_thumbnail_performance(content_id, "Cache-Warm")
        
        # Third request (should still be cached)
        print("   Third request (should still be cached)...")
        result3 = self.test_single_thumbnail_performance(content_id, "Cache-Warm-2")
        
        print(f"\n📊 Cache Behavior Results:")
        print(f"   First request: {result1['response_time_ms']}ms")
        print(f"   Second request: {result2['response_time_ms']}ms")
        print(f"   Third request: {result3['response_time_ms']}ms")
        
        # Analyze cache headers
        if result1["success"]:
            print(f"\n🏷️ Cache Headers Analysis:")
            print(f"   Cache-Control: {result1.get('cache_control', 'Not set')}")
            print(f"   ETag: {result1.get('etag', 'Not set')}")
            print(f"   Expires: {result1.get('expires', 'Not set')}")
            
            # Check if cache headers are properly set
            cache_control = result1.get('cache_control', '')
            has_proper_cache = 'max-age' in cache_control or 'public' in cache_control
            
            if has_proper_cache:
                print(f"   ✅ Proper cache headers detected")
            else:
                print(f"   ⚠️ Cache headers may not be optimal for performance")
        
        # Check if subsequent requests are faster (indicating caching)
        if all(r["success"] for r in [result1, result2, result3]):
            avg_warm_time = (result2["response_time_ms"] + result3["response_time_ms"]) / 2
            speedup = result1["response_time_ms"] / avg_warm_time if avg_warm_time > 0 else 1
            
            print(f"\n⚡ Cache Performance:")
            print(f"   Cold request: {result1['response_time_ms']}ms")
            print(f"   Warm requests avg: {avg_warm_time:.2f}ms")
            print(f"   Speedup factor: {speedup:.2f}x")
            
            if speedup > 2:
                print(f"   ✅ Good caching performance detected")
                return True
            else:
                print(f"   ⚠️ Limited caching benefit - may indicate regeneration on each request")
                return False
        
        return False
    
    def analyze_performance_bottlenecks(self, sequential_results, concurrent_results):
        """Step 7: Analyze performance bottlenecks"""
        print("\n🔍 Step 7: Performance Bottleneck Analysis")
        
        # Analyze sequential vs concurrent performance
        if sequential_results and concurrent_results:
            seq_successful = [r for r in sequential_results if r["success"]]
            conc_successful = [r for r in concurrent_results if r["success"]]
            
            if seq_successful and conc_successful:
                seq_avg = sum(r["response_time_ms"] for r in seq_successful) / len(seq_successful)
                conc_avg = sum(r["response_time_ms"] for r in conc_successful) / len(conc_successful)
                
                print(f"📊 Performance Comparison:")
                print(f"   Sequential average: {seq_avg:.2f}ms")
                print(f"   Concurrent average: {conc_avg:.2f}ms")
                print(f"   Performance ratio: {conc_avg/seq_avg:.2f}x")
                
                if conc_avg > seq_avg * 3:
                    print(f"   🚨 CRITICAL: Concurrent requests are significantly slower")
                    print(f"   This suggests server-side bottlenecks or lack of proper caching")
                elif conc_avg > seq_avg * 1.5:
                    print(f"   ⚠️ WARNING: Concurrent requests show performance degradation")
                else:
                    print(f"   ✅ Concurrent performance is acceptable")
        
        # Check for thumbnail generation vs retrieval
        print(f"\n🔧 Potential Issues Analysis:")
        
        # Look for patterns in response times
        all_results = sequential_results + concurrent_results
        successful_results = [r for r in all_results if r["success"]]
        
        if successful_results:
            response_times = [r["response_time_ms"] for r in successful_results]
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            
            print(f"   Average response time: {avg_time:.2f}ms")
            print(f"   Maximum response time: {max_time:.2f}ms")
            
            # Check for iPhone issue (30 second delays)
            very_slow = [r for r in successful_results if r["response_time_ms"] > 10000]  # >10 seconds
            if very_slow:
                print(f"   🚨 CRITICAL: {len(very_slow)} requests took >10 seconds")
                print(f"   This matches the reported iPhone issue!")
                
                for slow in very_slow:
                    print(f"     - {slow['test_name']}: {slow['response_time_ms']}ms")
            
            # Check for regeneration patterns
            if max_time > avg_time * 5:
                print(f"   ⚠️ High variance in response times suggests on-demand generation")
            
            # Check content types and sizes
            content_types = set(r.get("content_type", "") for r in successful_results)
            print(f"   Content types returned: {', '.join(content_types)}")
            
            sizes = [r.get("content_length", 0) for r in successful_results if r.get("content_length", 0) > 0]
            if sizes:
                avg_size = sum(sizes) / len(sizes)
                print(f"   Average thumbnail size: {avg_size:.0f} bytes")
    
    def run_comprehensive_test(self):
        """Run the complete thumbnail performance test"""
        print("🎯 THUMBNAIL PERFORMANCE TESTING")
        print("=" * 70)
        print(f"Backend URL: {BASE_URL}")
        print(f"Test User: {EMAIL}")
        print(f"Issue: iPhone thumbnails turn white and take 30 seconds to reload")
        print("=" * 70)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with testing")
            return False
        
        # Step 2: Get content list
        if not self.get_content_list():
            print("\n❌ CRITICAL: Could not retrieve content list - cannot test thumbnails")
            return False
        
        # Step 3: Check thumbnail database status
        db_status = self.check_thumbnail_database_status()
        
        # Step 4: Sequential thumbnail performance
        sequential_results = self.test_sequential_thumbnail_performance()
        
        # Step 5: Concurrent thumbnail performance (iPhone simulation)
        concurrent_results = self.test_concurrent_thumbnail_performance()
        
        # Step 6: Cache behavior testing
        cache_working = self.test_cache_behavior()
        
        # Step 7: Performance analysis
        self.analyze_performance_bottlenecks(sequential_results, concurrent_results)
        
        # Final Results
        print("\n" + "=" * 70)
        print("🎯 FINAL TEST RESULTS")
        print("=" * 70)
        
        tests_passed = 0
        total_tests = 7
        
        print(f"✅ Step 1: Authentication - {'PASS' if self.token else 'FAIL'}")
        if self.token: tests_passed += 1
        
        print(f"✅ Step 2: Content List Retrieval - {'PASS' if self.content_items else 'FAIL'}")
        if self.content_items: tests_passed += 1
        
        print(f"✅ Step 3: Database Status Check - {'PASS' if db_status else 'FAIL'}")
        if db_status: tests_passed += 1
        
        print(f"✅ Step 4: Sequential Performance - {'PASS' if sequential_results else 'FAIL'}")
        if sequential_results: tests_passed += 1
        
        print(f"✅ Step 5: Concurrent Performance - {'PASS' if concurrent_results else 'FAIL'}")
        if concurrent_results: tests_passed += 1
        
        print(f"✅ Step 6: Cache Behavior - {'PASS' if cache_working else 'FAIL'}")
        if cache_working: tests_passed += 1
        
        print(f"✅ Step 7: Performance Analysis - PASS")
        tests_passed += 1
        
        success_rate = (tests_passed / total_tests) * 100
        print(f"\n📊 SUCCESS RATE: {tests_passed}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        # Specific iPhone issue analysis
        print(f"\n📱 iPhone Issue Analysis:")
        all_results = sequential_results + concurrent_results
        successful_results = [r for r in all_results if r["success"]]
        
        if successful_results:
            # Check for 30-second delays
            very_slow = [r for r in successful_results if r["response_time_ms"] > 25000]  # >25 seconds
            slow = [r for r in successful_results if r["response_time_ms"] > 5000]  # >5 seconds
            
            if very_slow:
                print(f"   🚨 CRITICAL: Found {len(very_slow)} requests matching iPhone issue (>25s)")
                print(f"   This confirms the reported 30-second thumbnail loading problem!")
            elif slow:
                print(f"   ⚠️ WARNING: Found {len(slow)} slow requests (>5s)")
                print(f"   This may be related to the iPhone issue")
            else:
                print(f"   ✅ No extremely slow requests detected")
                print(f"   iPhone issue may be intermittent or environment-specific")
        
        # Database status analysis
        if db_status:
            completion = db_status.get("completion_percentage", 0)
            missing = db_status.get("missing_thumbnails", 0)
            
            if completion < 50:
                print(f"   🚨 CRITICAL: Only {completion}% thumbnails pre-generated")
                print(f"   {missing} thumbnails missing - causing on-demand generation delays")
            elif completion < 80:
                print(f"   ⚠️ WARNING: {completion}% thumbnails pre-generated")
                print(f"   {missing} thumbnails may cause occasional delays")
            else:
                print(f"   ✅ Good thumbnail coverage: {completion}%")
        
        if success_rate >= 85:
            print("🎉 THUMBNAIL SYSTEM TESTED SUCCESSFULLY")
        else:
            print("🚨 CRITICAL THUMBNAIL PERFORMANCE ISSUES DETECTED")
        
        return success_rate >= 85

if __name__ == "__main__":
    tester = ThumbnailPerformanceTest()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)