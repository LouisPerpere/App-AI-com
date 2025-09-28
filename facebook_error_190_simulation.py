#!/usr/bin/env python3
"""
🚨 SIMULATION TEST - FACEBOOK ERROR 190 REPRODUCTION
Créer une connexion Facebook avec un token temporaire pour reproduire l'erreur 190
et tester les corrections OAuth.

Identifiants: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import sys
import time
from datetime import datetime

class FacebookError190Simulation:
    def __init__(self):
        self.base_url = "https://social-ai-planner-2.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.credentials = {
            "email": "lperpere@yahoo.fr",
            "password": "L@Reunion974!"
        }
        
    def authenticate(self):
        """Authenticate with the API"""
        try:
            print(f"🔐 Step 1: Authenticating with {self.credentials['email']}")
            
            response = self.session.post(
                f"{self.base_url}/auth/login-robust",
                json=self.credentials,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                })
                
                print(f"   ✅ Authentication successful - User ID: {self.user_id}")
                return True
            else:
                print(f"   ❌ Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {str(e)}")
            return False
    
    def create_test_facebook_connection(self):
        """Créer une connexion Facebook avec un token temporaire pour reproduire l'erreur"""
        try:
            print(f"\n🔧 Step 2: Creating test Facebook connection with temporary token")
            
            # Create a temporary token like the fallback mechanism would
            timestamp = int(time.time())
            temp_token = f"temp_facebook_token_{timestamp}"
            
            print(f"   Creating connection with token: {temp_token}")
            
            # Use direct MongoDB insertion to simulate the fallback mechanism
            from pymongo import MongoClient
            import os
            
            # Connect to MongoDB
            mongo_url = "mongodb://localhost:27017/claire_marcus"
            client = MongoClient(mongo_url)
            db = client.claire_marcus
            
            # Create a Facebook connection like the fallback mechanism does
            connection_data = {
                "user_id": self.user_id,
                "platform": "facebook",
                "access_token": temp_token,
                "page_id": "test_page_id",
                "page_name": "Test Facebook Page",
                "active": True,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": None,
                "token_type": "temporary_fallback"
            }
            
            # Insert into social_media_connections collection
            result = db.social_media_connections.insert_one(connection_data)
            
            print(f"   ✅ Test Facebook connection created with ID: {result.inserted_id}")
            print(f"   📊 Connection details:")
            print(f"     Platform: facebook")
            print(f"     Active: True")
            print(f"     Token: {temp_token}")
            print(f"     Page: Test Facebook Page")
            
            client.close()
            return temp_token
            
        except Exception as e:
            print(f"   ❌ Error creating test connection: {str(e)}")
            return None
    
    def verify_connection_created(self):
        """Vérifier que la connexion a été créée"""
        try:
            print(f"\n🔍 Step 3: Verifying test connection was created")
            
            response = self.session.get(f"{self.base_url}/debug/social-connections")
            
            if response.status_code == 200:
                data = response.json()
                connections = data.get("social_media_connections", [])
                facebook_connections = [c for c in connections if c.get("platform") == "facebook"]
                
                print(f"   ✅ Debug endpoint accessible")
                print(f"   📊 Facebook connections found: {len(facebook_connections)}")
                
                if facebook_connections:
                    conn = facebook_connections[0]
                    token = conn.get("access_token", "")
                    print(f"   📋 Connection details:")
                    print(f"     Platform: {conn.get('platform')}")
                    print(f"     Active: {conn.get('active')}")
                    print(f"     Token: {token}")
                    print(f"     Page: {conn.get('page_name')}")
                    
                    if token.startswith("temp_facebook_token_"):
                        print(f"   ✅ CONFIRMED: Temporary token detected")
                        return True
                    else:
                        print(f"   ⚠️ Unexpected token format")
                        return False
                else:
                    print(f"   ❌ No Facebook connections found")
                    return False
            else:
                print(f"   ❌ Failed to verify connection: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error verifying connection: {str(e)}")
            return False
    
    def test_publication_with_temp_token(self):
        """Tester la publication avec le token temporaire pour reproduire l'erreur 190"""
        try:
            print(f"\n🚀 Step 4: Testing publication with temporary token")
            
            # Get a Facebook post to test with
            response = self.session.get(f"{self.base_url}/posts/generated")
            
            if response.status_code != 200:
                print(f"   ❌ Failed to get posts: {response.text}")
                return False
            
            data = response.json()
            posts = data.get("posts", [])
            facebook_posts = [p for p in posts if p.get("platform") == "facebook"]
            
            if not facebook_posts:
                print(f"   ⚠️ No Facebook posts available for testing")
                return False
            
            test_post = facebook_posts[0]
            post_id = test_post.get("id")
            
            print(f"   Testing publication with post: {post_id}")
            print(f"   Post title: {test_post.get('title', 'No title')[:50]}...")
            
            response = self.session.post(
                f"{self.base_url}/posts/publish",
                json={"post_id": post_id}
            )
            
            print(f"   📡 Publication response:")
            print(f"     Status: {response.status_code}")
            
            try:
                response_data = response.json()
                print(f"     Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                
                # Look for Facebook Error 190
                response_str = str(response_data).lower()
                if "190" in response_str and ("invalid oauth access token" in response_str or "cannot parse access token" in response_str):
                    print(f"   🚨 SUCCESS: Facebook Error 190 reproduced!")
                    print(f"   🚨 CONFIRMED: Temporary token rejected by Facebook API")
                    return {
                        "error_reproduced": True,
                        "error_code": 190,
                        "error_message": "Invalid OAuth access token",
                        "token_type": "temporary"
                    }
                else:
                    print(f"   ⚠️ Different response than expected")
                    return {
                        "error_reproduced": False,
                        "response": response_data
                    }
                    
            except:
                print(f"     Raw response: {response.text}")
                if "190" in response.text:
                    print(f"   🚨 SUCCESS: Error 190 found in raw response!")
                    return {
                        "error_reproduced": True,
                        "error_code": 190
                    }
                return {
                    "error_reproduced": False,
                    "raw_response": response.text
                }
                
        except Exception as e:
            print(f"   ❌ Error testing publication: {str(e)}")
            return None
    
    def cleanup_test_connection(self):
        """Nettoyer la connexion de test"""
        try:
            print(f"\n🧹 Step 5: Cleaning up test connection")
            
            response = self.session.post(f"{self.base_url}/debug/clean-invalid-tokens")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Cleanup successful")
                print(f"   📊 Cleanup result: {data.get('message', 'No message')}")
                return True
            else:
                print(f"   ⚠️ Cleanup response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error during cleanup: {str(e)}")
            return False
    
    def run_error_190_simulation(self):
        """Execute the complete Error 190 simulation"""
        print("🚨 MISSION: SIMULATION FACEBOOK ERROR 190 REPRODUCTION")
        print("🎯 OBJECTIVE: Reproduire l'erreur 190 avec un token temporaire")
        print("=" * 70)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ CRITICAL: Authentication failed")
            return False
        
        # Step 2: Create test Facebook connection
        temp_token = self.create_test_facebook_connection()
        if not temp_token:
            print("\n❌ CRITICAL: Failed to create test connection")
            return False
        
        # Step 3: Verify connection was created
        if not self.verify_connection_created():
            print("\n❌ CRITICAL: Failed to verify test connection")
            return False
        
        # Step 4: Test publication to reproduce error
        publication_result = self.test_publication_with_temp_token()
        
        # Step 5: Cleanup
        self.cleanup_test_connection()
        
        print("\n" + "=" * 70)
        print("🚨 FACEBOOK ERROR 190 SIMULATION COMPLETED")
        print("=" * 70)
        
        if publication_result and publication_result.get("error_reproduced"):
            print(f"✅ SUCCESS: Facebook Error 190 successfully reproduced")
            print(f"🚨 CONFIRMED: Temporary tokens are rejected by Facebook API")
            print(f"🚨 ROOT CAUSE: OAuth fallback mechanism creates invalid tokens")
            
            print(f"\n🔍 DIAGNOSTIC SUMMARY:")
            print(f"   📊 Error Code: {publication_result.get('error_code', 'Unknown')}")
            print(f"   📊 Error Type: {publication_result.get('error_message', 'Unknown')}")
            print(f"   📊 Token Type: {publication_result.get('token_type', 'Unknown')}")
            
            print(f"\n🚀 SOLUTION REQUIRED:")
            print(f"   1. Fix OAuth token exchange to get real Facebook tokens")
            print(f"   2. Remove or fix fallback mechanism")
            print(f"   3. Ensure proper Facebook App configuration")
            
        else:
            print(f"⚠️ PARTIAL: Error 190 not reproduced as expected")
            if publication_result:
                print(f"   Response: {publication_result}")
        
        print("=" * 70)
        return True

def main():
    """Main execution function"""
    simulation = FacebookError190Simulation()
    
    try:
        success = simulation.run_error_190_simulation()
        if success:
            print(f"\n🎯 CONCLUSION: Error 190 simulation completed")
            sys.exit(0)
        else:
            print(f"\n💥 CONCLUSION: Simulation failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⚠️ Simulation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()