#!/usr/bin/env python3
"""
Content Context Verification Test
Additional verification to ensure context updates work correctly and persist
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://social-pub-hub.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class ContentContextVerificationTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        
    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def authenticate(self):
        """Authenticate and get token"""
        try:
            response = self.session.post(
                f"{BASE_URL}/auth/login-robust",
                json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
            )
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                self.log(f"✅ Authentication successful - User ID: {self.user_id}")
                return True
            else:
                self.log(f"❌ Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Authentication error: {e}")
            return False
    
    def get_content_items(self):
        """Get content items"""
        try:
            response = self.session.get(f"{BASE_URL}/content/pending")
            if response.status_code == 200:
                data = response.json()
                content_items = data.get("content", [])
                self.log(f"✅ Retrieved {len(content_items)} content items")
                return content_items
            else:
                self.log(f"❌ Failed to get content: {response.status_code}")
                return []
        except Exception as e:
            self.log(f"❌ Content retrieval error: {e}")
            return []
    
    def test_context_update_and_verification(self):
        """Test context update and verify it persists correctly"""
        content_items = self.get_content_items()
        if not content_items:
            self.log("❌ No content items available for testing")
            return False
        
        # Use first content item
        test_item = content_items[0]
        content_id = test_item.get("id")
        original_context = test_item.get("context", "")
        
        self.log(f"🔍 Testing with content ID: {content_id}")
        self.log(f"   Original context: '{original_context}'")
        
        # Test 1: Add new context
        new_context = f"Verification test context - {datetime.now().strftime('%H:%M:%S')}"
        try:
            response = self.session.put(
                f"{BASE_URL}/content/{content_id}/context",
                json={"context": new_context}
            )
            if response.status_code == 200:
                self.log(f"✅ Context update successful")
            else:
                self.log(f"❌ Context update failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ Context update error: {e}")
            return False
        
        # Test 2: Verify context was saved
        updated_items = self.get_content_items()
        updated_item = None
        for item in updated_items:
            if item.get("id") == content_id:
                updated_item = item
                break
        
        if updated_item:
            saved_context = updated_item.get("context", "")
            if saved_context == new_context:
                self.log(f"✅ Context verification successful: '{saved_context}'")
            else:
                self.log(f"❌ Context verification failed. Expected: '{new_context}', Got: '{saved_context}'")
                return False
        else:
            self.log(f"❌ Could not find updated content item")
            return False
        
        # Test 3: Update context again
        second_context = f"Second update - {datetime.now().strftime('%H:%M:%S')}"
        try:
            response = self.session.put(
                f"{BASE_URL}/content/{content_id}/context",
                json={"context": second_context}
            )
            if response.status_code == 200:
                self.log(f"✅ Second context update successful")
            else:
                self.log(f"❌ Second context update failed: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Second context update error: {e}")
            return False
        
        # Test 4: Verify second update
        final_items = self.get_content_items()
        final_item = None
        for item in final_items:
            if item.get("id") == content_id:
                final_item = item
                break
        
        if final_item:
            final_context = final_item.get("context", "")
            if final_context == second_context:
                self.log(f"✅ Second context verification successful: '{final_context}'")
                return True
            else:
                self.log(f"❌ Second context verification failed. Expected: '{second_context}', Got: '{final_context}'")
                return False
        else:
            self.log(f"❌ Could not find final content item")
            return False
    
    def run_verification(self):
        """Run verification tests"""
        self.log("🎯 CONTENT CONTEXT VERIFICATION TESTING STARTED")
        
        if not self.authenticate():
            return False
        
        success = self.test_context_update_and_verification()
        
        if success:
            self.log("🎉 VERIFICATION SUCCESSFUL - Context updates work correctly and persist")
        else:
            self.log("❌ VERIFICATION FAILED - Issues with context persistence")
        
        return success

def main():
    tester = ContentContextVerificationTester()
    success = tester.run_verification()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()