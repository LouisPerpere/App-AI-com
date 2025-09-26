#!/usr/bin/env python3
"""
Password Reset Script for lperpere@yahoo.fr
Changes password to "L@Reunion974!" and tests authentication
"""

import sys
import os
import asyncio
import requests
import json
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.append('/app/backend')

async def reset_user_password():
    """Reset password for lperpere@yahoo.fr to L@Reunion974!"""
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        from dotenv import load_dotenv
        from auth import get_password_hash
        
        print("🔧 STARTING PASSWORD RESET PROCESS")
        print("=" * 60)
        
        # Load environment
        ROOT_DIR = Path('/app/backend')
        load_dotenv(ROOT_DIR / '.env')
        
        # Connect to MongoDB
        mongo_url = os.environ['MONGO_URL']
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ['DB_NAME']]
        
        # User details
        user_email = "lperpere@yahoo.fr"
        user_id = "c1c76afa-a112-40ad-809e-a180aa04f007"
        new_password = "L@Reunion974!"
        
        print(f"📧 Target User: {user_email}")
        print(f"🆔 User ID: {user_id}")
        print(f"🔑 New Password: {new_password}")
        print()
        
        # Step 1: Verify user exists
        print("1️⃣ VERIFYING USER EXISTS...")
        user = await db.users.find_one({"email": user_email})
        
        if not user:
            print(f"❌ User {user_email} not found in database")
            return False
        
        print(f"✅ User found:")
        print(f"   - ID: {user.get('id', 'N/A')}")
        print(f"   - Email: {user.get('email', 'N/A')}")
        print(f"   - Name: {user.get('first_name', '')} {user.get('last_name', '')}")
        print(f"   - Created: {user.get('created_at', 'N/A')}")
        print(f"   - Last Login: {user.get('last_login', 'Never')}")
        print(f"   - Subscription: {user.get('subscription_status', 'N/A')}")
        print()
        
        # Step 2: Hash the new password
        print("2️⃣ HASHING NEW PASSWORD...")
        hashed_password = get_password_hash(new_password)
        print(f"✅ Password hashed successfully")
        print(f"   Hash: {hashed_password[:50]}...")
        print()
        
        # Step 3: Update password in database
        print("3️⃣ UPDATING PASSWORD IN DATABASE...")
        result = await db.users.update_one(
            {"email": user_email},
            {
                "$set": {
                    "hashed_password": hashed_password,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            print(f"❌ Failed to find user for update")
            return False
        
        if result.modified_count == 0:
            print(f"⚠️ User found but no changes made (password might be the same)")
        else:
            print(f"✅ Password updated successfully")
            print(f"   Matched: {result.matched_count} document(s)")
            print(f"   Modified: {result.modified_count} document(s)")
        print()
        
        # Step 4: Verify the update
        print("4️⃣ VERIFYING PASSWORD UPDATE...")
        updated_user = await db.users.find_one({"email": user_email})
        
        if updated_user and updated_user.get('hashed_password') == hashed_password:
            print("✅ Password hash verified in database")
        else:
            print("❌ Password hash verification failed")
            return False
        print()
        
        # Close database connection
        client.close()
        
        print("🎉 PASSWORD RESET COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ Error during password reset: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_authentication():
    """Test authentication with the new password"""
    try:
        print("\n🧪 TESTING AUTHENTICATION")
        print("=" * 60)
        
        # API endpoint
        base_url = "https://social-ai-planner-2.preview.emergentagent.com"
        login_url = f"{base_url}/api/auth/login"
        
        # Login credentials
        login_data = {
            "email": "lperpere@yahoo.fr",
            "password": "L@Reunion974!"
        }
        
        print(f"🌐 API URL: {login_url}")
        print(f"📧 Email: {login_data['email']}")
        print(f"🔑 Password: {login_data['password']}")
        print()
        
        # Step 1: Test login
        print("1️⃣ TESTING LOGIN...")
        response = requests.post(
            login_url,
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ LOGIN SUCCESSFUL!")
            
            try:
                response_data = response.json()
                print("📋 Response Data:")
                print(f"   - Access Token: {response_data.get('access_token', 'N/A')[:50]}...")
                print(f"   - Refresh Token: {response_data.get('refresh_token', 'N/A')[:50]}...")
                print(f"   - Token Type: {response_data.get('token_type', 'N/A')}")
                
                access_token = response_data.get('access_token')
                
                if access_token:
                    print()
                    # Step 2: Test authenticated endpoint
                    print("2️⃣ TESTING AUTHENTICATED ENDPOINT...")
                    me_url = f"{base_url}/api/auth/me"
                    
                    me_response = requests.get(
                        me_url,
                        headers={
                            'Authorization': f'Bearer {access_token}',
                            'Content-Type': 'application/json'
                        },
                        timeout=30
                    )
                    
                    print(f"📊 /auth/me Status: {me_response.status_code}")
                    
                    if me_response.status_code == 200:
                        print("✅ AUTHENTICATED ENDPOINT ACCESS SUCCESSFUL!")
                        
                        try:
                            user_data = me_response.json()
                            print("👤 User Information:")
                            print(f"   - ID: {user_data.get('id', 'N/A')}")
                            print(f"   - Email: {user_data.get('email', 'N/A')}")
                            print(f"   - Name: {user_data.get('first_name', '')} {user_data.get('last_name', '')}")
                            print(f"   - Admin: {user_data.get('is_admin', False)}")
                            print(f"   - Subscription: {user_data.get('subscription_status', 'N/A')}")
                            print(f"   - Plan: {user_data.get('subscription_plan', 'N/A')}")
                        except json.JSONDecodeError:
                            print("⚠️ Could not parse user data JSON")
                    else:
                        print("❌ AUTHENTICATED ENDPOINT ACCESS FAILED")
                        try:
                            error_data = me_response.json()
                            print(f"   Error: {error_data}")
                        except:
                            print(f"   Error: {me_response.text}")
                        return False
                else:
                    print("❌ No access token received")
                    return False
                    
            except json.JSONDecodeError:
                print("⚠️ Could not parse login response JSON")
                print(f"Raw response: {response.text}")
                return False
                
        else:
            print("❌ LOGIN FAILED")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return False
        
        print()
        print("🎉 AUTHENTICATION TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error during authentication test: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during authentication test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_subscription_status():
    """Test subscription status endpoint"""
    try:
        print("\n📊 TESTING SUBSCRIPTION STATUS")
        print("=" * 60)
        
        # First login to get token
        base_url = "https://social-ai-planner-2.preview.emergentagent.com"
        login_url = f"{base_url}/api/auth/login"
        
        login_data = {
            "email": "lperpere@yahoo.fr",
            "password": "L@Reunion974!"
        }
        
        login_response = requests.post(login_url, json=login_data, timeout=30)
        
        if login_response.status_code != 200:
            print("❌ Could not login for subscription test")
            return False
        
        access_token = login_response.json().get('access_token')
        if not access_token:
            print("❌ No access token for subscription test")
            return False
        
        # Test subscription status
        subscription_url = f"{base_url}/api/auth/subscription-status"
        
        subscription_response = requests.get(
            subscription_url,
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            },
            timeout=30
        )
        
        print(f"📊 Subscription Status Code: {subscription_response.status_code}")
        
        if subscription_response.status_code == 200:
            print("✅ SUBSCRIPTION STATUS CHECK SUCCESSFUL!")
            
            try:
                subscription_data = subscription_response.json()
                print("📋 Subscription Details:")
                print(f"   - Status: {subscription_data.get('status', 'N/A')}")
                print(f"   - Active: {subscription_data.get('active', 'N/A')}")
                print(f"   - Days Left: {subscription_data.get('days_left', 'N/A')}")
                print(f"   - Message: {subscription_data.get('message', 'N/A')}")
            except json.JSONDecodeError:
                print("⚠️ Could not parse subscription data JSON")
        else:
            print("❌ SUBSCRIPTION STATUS CHECK FAILED")
            try:
                error_data = subscription_response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {subscription_response.text}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error during subscription status test: {e}")
        return False

async def main():
    """Main function to run all tests"""
    print("🚀 PASSWORD RESET AND AUTHENTICATION TEST")
    print("=" * 80)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Reset password
    password_reset_success = await reset_user_password()
    
    if not password_reset_success:
        print("\n❌ PASSWORD RESET FAILED - STOPPING TESTS")
        return False
    
    # Step 2: Test authentication
    auth_success = test_authentication()
    
    if not auth_success:
        print("\n❌ AUTHENTICATION TEST FAILED")
        return False
    
    # Step 3: Test subscription status
    subscription_success = test_subscription_status()
    
    if not subscription_success:
        print("\n❌ SUBSCRIPTION STATUS TEST FAILED")
        return False
    
    print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("✅ Password reset: SUCCESS")
    print("✅ Authentication: SUCCESS")
    print("✅ Subscription status: SUCCESS")
    print()
    print("🔐 User lperpere@yahoo.fr can now login with password: L@Reunion974!")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    # Run the async main function
    success = asyncio.run(main())
    
    if success:
        print("\n✅ SCRIPT COMPLETED SUCCESSFULLY")
        sys.exit(0)
    else:
        print("\n❌ SCRIPT FAILED")
        sys.exit(1)