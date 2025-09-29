#!/usr/bin/env python3
"""
Final Verification Test for Review Request Endpoints
Testing the exact endpoints mentioned in the review request
"""

import requests
import json
import time

def test_specific_endpoints():
    """Test the exact endpoints mentioned in the review request"""
    
    base_url = "https://social-pub-hub.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    # Test credentials from review request
    test_email = "lperpere@yahoo.fr"
    test_password = "L@Reunion974!"
    
    print("🎯 FINAL VERIFICATION - Review Request Endpoints")
    print("=" * 60)
    print("Testing specific endpoints mentioned in review request:")
    print("1. Authentication endpoints (/api/auth/login, /api/auth/me)")
    print("2. Business profile endpoints (GET/PUT /api/business-profile)")
    print("3. Notes endpoints (GET/POST/DELETE /api/notes)")
    print("4. Website analysis endpoint (/api/website/analyze)")
    print("5. Basic functionality of other core endpoints")
    print("=" * 60)
    
    # Step 1: Login
    print("\n🔐 Step 1: Authentication")
    login_response = requests.post(
        f"{api_url}/auth/login",
        json={"email": test_email, "password": test_password},
        headers={'Content-Type': 'application/json'}
    )
    
    if login_response.status_code == 200:
        login_data = login_response.json()
        access_token = login_data['access_token']
        print(f"✅ /api/auth/login - SUCCESS (Status: {login_response.status_code})")
        print(f"   User: {login_data.get('email')}")
        print(f"   Token: {access_token[:30]}...")
    else:
        print(f"❌ /api/auth/login - FAILED (Status: {login_response.status_code})")
        return False
    
    # Headers for authenticated requests
    auth_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    
    # Step 2: Test /api/auth/me
    me_response = requests.get(f"{api_url}/auth/me", headers=auth_headers)
    if me_response.status_code == 200:
        me_data = me_response.json()
        print(f"✅ /api/auth/me - SUCCESS (Status: {me_response.status_code})")
        print(f"   Email: {me_data.get('email')}")
        print(f"   Subscription: {me_data.get('subscription_status')}")
    else:
        print(f"❌ /api/auth/me - FAILED (Status: {me_response.status_code})")
        return False
    
    # Step 3: Test GET /api/business-profile
    print("\n🏢 Step 2: Business Profile Endpoints (Critical for keyboard fix)")
    get_profile_response = requests.get(f"{api_url}/business-profile", headers=auth_headers)
    if get_profile_response.status_code == 200:
        profile_data = get_profile_response.json()
        print(f"✅ GET /api/business-profile - SUCCESS (Status: {get_profile_response.status_code})")
        print(f"   Business Name: {profile_data.get('business_name')}")
        print(f"   Email: {profile_data.get('email')}")
        print(f"   Website: {profile_data.get('website_url')}")
    else:
        print(f"❌ GET /api/business-profile - FAILED (Status: {get_profile_response.status_code})")
        return False
    
    # Step 4: Test PUT /api/business-profile
    test_update_data = {
        "business_name": "Test Keyboard Fix - Restaurant Réunionnais",
        "business_type": "restaurant",
        "business_description": "Test de persistance des données après correction du bug clavier virtuel iPadOS 18+",
        "target_audience": "Test audience pour validation clavier",
        "brand_tone": "friendly",
        "posting_frequency": "daily",
        "preferred_platforms": ["Facebook", "Instagram"],
        "budget_range": "1000-2000€",
        "email": "test-keyboard@reunion.fr",
        "website_url": "https://test-keyboard-fix.reunion.fr",
        "hashtags_primary": ["#TestClavier", "#iPadOS18", "#BugFix"],
        "hashtags_secondary": ["#VirtualKeyboard", "#Reunion", "#Test"]
    }
    
    put_profile_response = requests.put(
        f"{api_url}/business-profile", 
        json=test_update_data, 
        headers=auth_headers
    )
    
    if put_profile_response.status_code == 200:
        put_data = put_profile_response.json()
        print(f"✅ PUT /api/business-profile - SUCCESS (Status: {put_profile_response.status_code})")
        print(f"   Updated: {put_data.get('message')}")
    else:
        print(f"❌ PUT /api/business-profile - FAILED (Status: {put_profile_response.status_code})")
        return False
    
    # Step 5: Verify persistence immediately (critical for keyboard fix)
    time.sleep(0.5)
    verify_response = requests.get(f"{api_url}/business-profile", headers=auth_headers)
    if verify_response.status_code == 200:
        verify_data = verify_response.json()
        if "Test Keyboard Fix" in verify_data.get('business_name', ''):
            print(f"✅ Business Profile Persistence - SUCCESS")
            print(f"   Data persisted: {verify_data.get('business_name')}")
        else:
            print(f"❌ Business Profile Persistence - FAILED")
            print(f"   Expected: Test Keyboard Fix, Got: {verify_data.get('business_name')}")
            return False
    
    # Step 6: Test Notes endpoints
    print("\n📝 Step 3: Notes Endpoints (Critical for keyboard fix)")
    
    # GET /api/notes
    get_notes_response = requests.get(f"{api_url}/notes", headers=auth_headers)
    if get_notes_response.status_code == 200:
        notes_data = get_notes_response.json()
        print(f"✅ GET /api/notes - SUCCESS (Status: {get_notes_response.status_code})")
        print(f"   Notes found: {len(notes_data.get('notes', []))}")
    else:
        print(f"❌ GET /api/notes - FAILED (Status: {get_notes_response.status_code})")
        return False
    
    # POST /api/notes
    test_note = {
        "content": "Test note clavier virtuel iPadOS 18+ - Promotion spéciale carry poulet avec rougail saucisse maison et gratin chouchou traditionnel",
        "description": "Note de test pour validation du système de clavier virtuel après correction bug",
        "priority": "high"
    }
    
    post_note_response = requests.post(f"{api_url}/notes", json=test_note, headers=auth_headers)
    if post_note_response.status_code == 200:
        note_data = post_note_response.json()
        test_note_id = note_data.get('note', {}).get('note_id')
        print(f"✅ POST /api/notes - SUCCESS (Status: {post_note_response.status_code})")
        print(f"   Created note ID: {test_note_id}")
    else:
        print(f"❌ POST /api/notes - FAILED (Status: {post_note_response.status_code})")
        return False
    
    # DELETE /api/notes/{note_id}
    if test_note_id:
        delete_note_response = requests.delete(f"{api_url}/notes/{test_note_id}", headers=auth_headers)
        if delete_note_response.status_code == 200:
            print(f"✅ DELETE /api/notes/{test_note_id} - SUCCESS (Status: {delete_note_response.status_code})")
        else:
            print(f"❌ DELETE /api/notes/{test_note_id} - FAILED (Status: {delete_note_response.status_code})")
            return False
    
    # Step 7: Test Website Analysis
    print("\n🌐 Step 4: Website Analysis Endpoint")
    analysis_data = {
        "website_url": "https://test-keyboard-fix.reunion.fr",
        "force_reanalysis": True
    }
    
    analyze_response = requests.post(f"{api_url}/website/analyze", json=analysis_data, headers=auth_headers)
    if analyze_response.status_code == 200:
        analysis_result = analyze_response.json()
        print(f"✅ POST /api/website/analyze - SUCCESS (Status: {analyze_response.status_code})")
        print(f"   Analyzed: {analysis_result.get('website_url')}")
        print(f"   Status: {analysis_result.get('status')}")
    else:
        print(f"❌ POST /api/website/analyze - FAILED (Status: {analyze_response.status_code})")
        return False
    
    # Step 8: Test other core endpoints
    print("\n⚙️ Step 5: Other Core Endpoints")
    
    # Health check
    health_response = requests.get(f"{api_url}/health")
    if health_response.status_code == 200:
        print(f"✅ GET /api/health - SUCCESS (Status: {health_response.status_code})")
    else:
        print(f"❌ GET /api/health - FAILED (Status: {health_response.status_code})")
        return False
    
    # Generate posts
    posts_response = requests.post(f"{api_url}/generate-posts", json={"count": 2}, headers=auth_headers)
    if posts_response.status_code == 200:
        posts_data = posts_response.json()
        print(f"✅ POST /api/generate-posts - SUCCESS (Status: {posts_response.status_code})")
        print(f"   Generated: {len(posts_data.get('posts', []))} posts")
    else:
        print(f"❌ POST /api/generate-posts - FAILED (Status: {posts_response.status_code})")
        return False
    
    # LinkedIn auth URL
    linkedin_response = requests.get(f"{api_url}/linkedin/auth-url", headers=auth_headers)
    if linkedin_response.status_code == 200:
        print(f"✅ GET /api/linkedin/auth-url - SUCCESS (Status: {linkedin_response.status_code})")
    else:
        print(f"❌ GET /api/linkedin/auth-url - FAILED (Status: {linkedin_response.status_code})")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ALL REVIEW REQUEST ENDPOINTS VERIFIED SUCCESSFULLY")
    print("✅ Authentication endpoints working")
    print("✅ Business profile endpoints working (critical for keyboard fix)")
    print("✅ Notes endpoints working (critical for keyboard fix)")
    print("✅ Website analysis endpoint working")
    print("✅ Core endpoints working")
    print("=" * 60)
    print("🎯 CONCLUSION: Backend functionality remains intact after virtual keyboard bug fixes")
    
    return True

if __name__ == "__main__":
    test_specific_endpoints()