#!/usr/bin/env python3

import sys
import os
sys.path.append('/app')

from backend_test import SocialGenieAPITester

def main():
    print("🚀 Starting Phase 2 Subscription Popup Logic Tests...")
    print("   Testing backend data for frontend popup logic")
    print("   Test user: lperpere@yahoo.fr")
    
    tester = SocialGenieAPITester()
    
    # Authentication first
    print("\n" + "="*60)
    print("🔐 AUTHENTICATION")
    print("="*60)
    
    if not tester.test_user_login():
        print("❌ Login failed - stopping tests")
        return False
    
    # Phase 2 Subscription Popup Tests
    print("\n" + "="*60)
    print("🎯 PHASE 2 SUBSCRIPTION POPUP LOGIC TESTS")
    print("="*60)
    
    # Test 1: User Data Verification
    print("\n🔍 Test 1: User Data Verification")
    result1 = tester.test_subscription_popup_user_data_verification()
    
    # Test 2: Trigger Calculation
    print("\n🔍 Test 2: Trigger Calculation")
    result2 = tester.test_subscription_popup_trigger_calculation()
    
    # Test 3: Frequency Mapping
    print("\n🔍 Test 3: Frequency Mapping")
    result3 = tester.test_subscription_popup_normalized_frequency_mapping()
    
    # Test 4: Trial Data Verification
    print("\n🔍 Test 4: Trial Data Verification")
    result4 = tester.test_subscription_popup_trial_data_verification()
    
    # Test 5: Backend Data Structure
    print("\n🔍 Test 5: Backend Data Structure")
    result5 = tester.test_subscription_popup_backend_data_structure()
    
    # Final Results
    print("\n" + "="*80)
    print("📊 PHASE 2 SUBSCRIPTION POPUP TEST RESULTS")
    print("="*80)
    print(f"Total Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    
    if tester.tests_run > 0:
        success_rate = (tester.tests_passed/tester.tests_run)*100
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 Phase 2 Subscription Popup Logic: WORKING CORRECTLY")
            return True
        elif success_rate >= 60:
            print("⚠️  Phase 2 Subscription Popup Logic: NEEDS ATTENTION")
            return False
        else:
            print("❌ Phase 2 Subscription Popup Logic: CRITICAL ISSUES")
            return False
    else:
        print("❌ No tests were run")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)