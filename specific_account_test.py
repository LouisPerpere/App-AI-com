#!/usr/bin/env python3
"""
🚨 SPECIFIC ACCOUNT INVESTIGATION - test@claire-marcus.com
Testing the exact account mentioned in the security report
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "https://claire-marcus.com/api"

# Common passwords to try for test@claire-marcus.com
COMMON_PASSWORDS = [
    "password",
    "password123",
    "test123",
    "test",
    "123456",
    "admin",
    "claire123",
    "marcus123",
    "test@123",
    "Password123",
    "Test123",
    "claire-marcus",
    "testtest"
]

def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def try_login_with_passwords():
    """Try to login with common passwords"""
    log("🔐 Attempting to login to test@claire-marcus.com with common passwords")
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'Account-Investigation/1.0'
    })
    
    for password in COMMON_PASSWORDS:
        try:
            log(f"   Trying password: {password}")
            response = session.post(f"{BACKEND_URL}/auth/login-robust", json={
                "email": "test@claire-marcus.com",
                "password": password
            })
            
            if response.status_code == 200:
                data = response.json()
                log(f"✅ SUCCESS! Password found: {password}")
                log(f"   User ID: {data.get('user_id')}")
                log(f"   Token: {data.get('access_token', '')[:20]}...")
                
                # Set auth header and test data access
                session.headers.update({
                    'Authorization': f'Bearer {data.get("access_token")}'
                })
                
                # Test website analysis
                log("🔍 Testing website analysis access")
                wa_response = session.get(f"{BACKEND_URL}/website-analysis")
                if wa_response.status_code == 200:
                    wa_data = wa_response.json()
                    log(f"   Website analysis data found: {len(str(wa_data))} chars")
                    
                    # Check if this contains lperpere data
                    wa_str = str(wa_data).lower()
                    if 'lperpere' in wa_str or 'laurent' in wa_str or 'perpere' in wa_str:
                        log("🚨 CRITICAL: Website analysis contains lperpere data!")
                        log(f"   Data preview: {str(wa_data)[:200]}...")
                    else:
                        log("   No lperpere data detected in website analysis")
                else:
                    log(f"   Website analysis: {wa_response.status_code}")
                
                # Test content access
                log("🔍 Testing content access")
                content_response = session.get(f"{BACKEND_URL}/content/pending")
                if content_response.status_code == 200:
                    content_data = content_response.json()
                    content_items = content_data.get('content', [])
                    log(f"   Content items found: {len(content_items)}")
                    
                    # Check ownership of content items
                    lperpere_user_id = "6a670c66-c06c-4d75-9dd5-c747e8a0281a"  # Known from previous test
                    test_user_id = data.get('user_id')
                    
                    for item in content_items[:5]:  # Check first 5 items
                        owner_id = item.get('owner_id') or item.get('user_id')
                        if owner_id == lperpere_user_id:
                            log(f"🚨 CRITICAL: Content item {item.get('id')} belongs to lperpere!")
                        elif owner_id == test_user_id:
                            log(f"   ✅ Content item {item.get('id')} belongs to test account")
                        else:
                            log(f"   ⚠️ Content item {item.get('id')} has unknown owner: {owner_id}")
                else:
                    log(f"   Content access: {content_response.status_code}")
                
                return True
                
            elif response.status_code == 401:
                continue  # Try next password
            else:
                log(f"   Unexpected response: {response.status_code}")
                
        except Exception as e:
            log(f"   Error with password {password}: {str(e)}")
            continue
    
    log("❌ No valid password found for test@claire-marcus.com")
    return False

def check_account_existence():
    """Check if the account exists by trying registration"""
    log("🔍 Checking if test@claire-marcus.com account exists")
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json'
    })
    
    try:
        response = session.post(f"{BACKEND_URL}/auth/register", json={
            "email": "test@claire-marcus.com",
            "password": "dummy_password",
            "first_name": "Test",
            "last_name": "User"
        })
        
        if response.status_code == 400:
            error_data = response.json()
            if "already registered" in error_data.get('error', '').lower():
                log("✅ Account test@claire-marcus.com EXISTS")
                return True
        elif response.status_code == 200:
            log("⚠️ Account test@claire-marcus.com did NOT exist, but was just created")
            return True
        
        log(f"❌ Unexpected registration response: {response.status_code} - {response.text}")
        return False
        
    except Exception as e:
        log(f"❌ Error checking account existence: {str(e)}")
        return False

def main():
    log("🚨 SPECIFIC ACCOUNT INVESTIGATION - test@claire-marcus.com")
    log("=" * 60)
    
    # Check if account exists
    if check_account_existence():
        # Try to login with common passwords
        if try_login_with_passwords():
            log("✅ Investigation completed successfully")
        else:
            log("❌ Could not access test@claire-marcus.com account")
            log("   Recommendation: Contact user for correct password or reset password")
    else:
        log("❌ Account test@claire-marcus.com does not exist")

if __name__ == "__main__":
    main()