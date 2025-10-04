#!/usr/bin/env python3
"""
THUMBNAIL DATABASE FUNCTION TESTING
Test the get_db_thumbnail() function mentioned in the review request around lines 200-220
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://claire-marcus-app-1.preview.emergentagent.com/api"
EMAIL = "lperpere@yahoo.fr"
PASSWORD = "L@Reunion974!"

class ThumbnailDBTest:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        
    def authenticate(self):
        """Authenticate with provided credentials"""
        print("🔐 Authentication")
        
        auth_data = {
            "email": EMAIL,
            "password": PASSWORD
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/auth/login-robust", json=auth_data)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                })
                
                print(f"✅ Authentication successful - User ID: {self.user_id}")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def test_thumbnail_regeneration_behavior(self):
        """Test if thumbnails are being regenerated each time"""
        print("\n🔄 Testing Thumbnail Regeneration Behavior")
        
        # Get content list
        response = self.session.get(f"{BASE_URL}/content/pending?limit=3")
        if response.status_code != 200:
            print("❌ Could not get content list")
            return False
            
        content_items = response.json().get("content", [])
        if not content_items:
            print("❌ No content items found")
            return False
            
        test_item = content_items[0]
        content_id = test_item.get("id")
        filename = test_item.get("filename", "")
        
        print(f"Testing regeneration for: {filename} (ID: {content_id})")
        
        # Make multiple requests and check response times
        response_times = []
        
        for i in range(5):
            print(f"   Request {i+1}/5...")
            start_time = datetime.now()
            
            response = self.session.get(f"{BASE_URL}/content/{content_id}/thumb")
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            if response.status_code == 200:
                response_times.append(response_time)
                print(f"     ✅ {response_time:.2f}ms")
            else:
                print(f"     ❌ Failed: {response.status_code}")
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            variance = max_time - min_time
            
            print(f"\n📊 Regeneration Analysis:")
            print(f"   Average response time: {avg_time:.2f}ms")
            print(f"   Min response time: {min_time:.2f}ms")
            print(f"   Max response time: {max_time:.2f}ms")
            print(f"   Variance: {variance:.2f}ms")
            
            # If variance is high, it suggests regeneration
            if variance > 1000:  # More than 1 second difference
                print(f"   🚨 HIGH VARIANCE: Suggests thumbnails are being regenerated")
                return False
            elif variance > 200:  # More than 200ms difference
                print(f"   ⚠️ MODERATE VARIANCE: Some regeneration may be occurring")
                return True
            else:
                print(f"   ✅ LOW VARIANCE: Thumbnails appear to be cached properly")
                return True
        
        return False
    
    def test_thumbnail_status_accuracy(self):
        """Test if thumbnail status endpoint is accurate"""
        print("\n📊 Testing Thumbnail Status Accuracy")
        
        # Get thumbnail status
        status_response = self.session.get(f"{BASE_URL}/content/thumbnails/status")
        if status_response.status_code != 200:
            print("❌ Could not get thumbnail status")
            return False
            
        status_data = status_response.json()
        total_files = status_data.get("total_files", 0)
        with_thumbnails = status_data.get("with_thumbnails", 0)
        completion_percentage = status_data.get("completion_percentage", 0)
        
        print(f"Status reports: {total_files} total, {with_thumbnails} with thumbnails ({completion_percentage}%)")
        
        # Get actual content list
        content_response = self.session.get(f"{BASE_URL}/content/pending")
        if content_response.status_code != 200:
            print("❌ Could not get content list")
            return False
            
        content_data = content_response.json()
        actual_total = content_data.get("total", 0)
        content_items = content_data.get("content", [])
        
        print(f"Actual content: {actual_total} total items, {len(content_items)} loaded")
        
        # Test a few thumbnails to see if they actually exist
        working_thumbnails = 0
        tested_count = min(5, len(content_items))
        
        print(f"Testing {tested_count} actual thumbnails...")
        
        for i, item in enumerate(content_items[:tested_count]):
            content_id = item.get("id")
            filename = item.get("filename", "")
            
            thumb_response = self.session.get(f"{BASE_URL}/content/{content_id}/thumb")
            
            if thumb_response.status_code == 200:
                working_thumbnails += 1
                print(f"   ✅ {filename}: Working")
            else:
                print(f"   ❌ {filename}: Failed ({thumb_response.status_code})")
        
        actual_working_percentage = (working_thumbnails / tested_count * 100) if tested_count > 0 else 0
        
        print(f"\n📈 Accuracy Analysis:")
        print(f"   Status endpoint reports: {completion_percentage}% completion")
        print(f"   Actual test results: {actual_working_percentage}% working")
        
        # Check if the numbers make sense
        if completion_percentage > 200:
            print(f"   🚨 ANOMALY: Completion percentage >200% indicates database inconsistency")
            return False
        elif abs(completion_percentage - actual_working_percentage) > 50:
            print(f"   ⚠️ DISCREPANCY: Large difference between reported and actual status")
            return False
        else:
            print(f"   ✅ Status appears reasonably accurate")
            return True
    
    def test_concurrent_load_simulation(self):
        """Simulate the iPhone concurrent load issue"""
        print("\n📱 iPhone Concurrent Load Simulation")
        
        # Get content for testing
        response = self.session.get(f"{BASE_URL}/content/pending?limit=24")
        if response.status_code != 200:
            print("❌ Could not get content list")
            return False
            
        content_items = response.json().get("content", [])
        if len(content_items) < 10:
            print("❌ Not enough content items for simulation")
            return False
        
        print(f"Simulating iPhone loading {len(content_items)} thumbnails...")
        
        # Simulate rapid sequential requests (like iPhone would do)
        start_time = datetime.now()
        failed_requests = 0
        slow_requests = 0
        response_times = []
        
        for i, item in enumerate(content_items):
            content_id = item.get("id")
            filename = item.get("filename", "")
            
            request_start = datetime.now()
            thumb_response = self.session.get(f"{BASE_URL}/content/{content_id}/thumb")
            request_end = datetime.now()
            
            response_time = (request_end - request_start).total_seconds() * 1000
            response_times.append(response_time)
            
            if thumb_response.status_code != 200:
                failed_requests += 1
                print(f"   ❌ {i+1}/{len(content_items)}: {filename} - FAILED")
            elif response_time > 5000:  # >5 seconds
                slow_requests += 1
                print(f"   🐌 {i+1}/{len(content_items)}: {filename} - SLOW ({response_time:.0f}ms)")
            else:
                print(f"   ✅ {i+1}/{len(content_items)}: {filename} - OK ({response_time:.0f}ms)")
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() * 1000
        
        print(f"\n📊 iPhone Simulation Results:")
        print(f"   Total time: {total_time:.0f}ms ({total_time/1000:.1f} seconds)")
        print(f"   Failed requests: {failed_requests}/{len(content_items)}")
        print(f"   Slow requests (>5s): {slow_requests}/{len(content_items)}")
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            print(f"   Average response time: {avg_time:.0f}ms")
            print(f"   Slowest response: {max_time:.0f}ms")
            
            # Check for iPhone issue pattern
            if total_time > 30000:  # >30 seconds total
                print(f"   🚨 MATCHES IPHONE ISSUE: Total time >30 seconds")
                return False
            elif slow_requests > len(content_items) * 0.3:  # >30% slow
                print(f"   ⚠️ PERFORMANCE ISSUE: Many slow requests detected")
                return False
            else:
                print(f"   ✅ Performance within acceptable range")
                return True
        
        return False
    
    def run_test(self):
        """Run all thumbnail database tests"""
        print("🎯 THUMBNAIL DATABASE FUNCTION TESTING")
        print("=" * 60)
        print(f"Testing get_db_thumbnail() function and related behavior")
        print("=" * 60)
        
        if not self.authenticate():
            return False
        
        # Test 1: Regeneration behavior
        regeneration_ok = self.test_thumbnail_regeneration_behavior()
        
        # Test 2: Status accuracy
        status_ok = self.test_thumbnail_status_accuracy()
        
        # Test 3: iPhone simulation
        iphone_ok = self.test_concurrent_load_simulation()
        
        # Results
        print("\n" + "=" * 60)
        print("🎯 THUMBNAIL DB TEST RESULTS")
        print("=" * 60)
        
        tests_passed = 0
        total_tests = 3
        
        print(f"✅ Regeneration Behavior: {'PASS' if regeneration_ok else 'FAIL'}")
        if regeneration_ok: tests_passed += 1
        
        print(f"✅ Status Accuracy: {'PASS' if status_ok else 'FAIL'}")
        if status_ok: tests_passed += 1
        
        print(f"✅ iPhone Load Simulation: {'PASS' if iphone_ok else 'FAIL'}")
        if iphone_ok: tests_passed += 1
        
        success_rate = (tests_passed / total_tests) * 100
        print(f"\n📊 SUCCESS RATE: {tests_passed}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        return success_rate >= 66.7

if __name__ == "__main__":
    tester = ThumbnailDBTest()
    success = tester.run_test()
    sys.exit(0 if success else 1)