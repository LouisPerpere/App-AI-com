#!/usr/bin/env python3
"""
Notes API PUT Endpoint Testing
Testing the PUT /api/notes/{note_id} endpoint to modify note priority
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://claire-marcus-app-1.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class NotesPUTTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.test_note_id = None
        
    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def authenticate(self):
        """Authenticate and get access token"""
        self.log("🔍 Authenticating...")
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json=TEST_CREDENTIALS,
                timeout=10
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
            
    def create_test_note(self):
        """Create a test note to modify"""
        self.log("🔍 Creating test note...")
        test_note = {
            "title": "Test Note for PUT",
            "content": "This note will be modified",
            "priority": "low"
        }
        try:
            response = self.session.post(
                f"{BACKEND_URL}/notes",
                json=test_note,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                note = data.get("note", {})
                self.test_note_id = note.get("note_id")
                self.log(f"✅ Test note created - Note ID: {self.test_note_id}")
                self.log(f"   Initial Priority: {note.get('priority', 'N/A')}")
                return True
            else:
                self.log(f"❌ Failed to create test note: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Create test note error: {e}")
            return False
            
    def test_put_note_priority(self):
        """Test PUT /api/notes/{note_id} to change priority"""
        if not self.test_note_id:
            self.log("❌ No test note ID available")
            return False
            
        self.log(f"🔍 Testing PUT /api/notes/{self.test_note_id} (changing priority to 'high')...")
        
        updated_note = {
            "title": "Test Note for PUT - Modified",
            "content": "This note has been modified via PUT",
            "priority": "high"
        }
        
        try:
            response = self.session.put(
                f"{BACKEND_URL}/notes/{self.test_note_id}",
                json=updated_note,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                note = data.get("note", {})
                self.log(f"✅ PUT note successful - {data.get('message', '')}")
                self.log(f"   Updated Title: {note.get('title', 'N/A')}")
                self.log(f"   Updated Priority: {note.get('priority', 'N/A')}")
                return True
            else:
                self.log(f"❌ PUT note failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ PUT note error: {e}")
            return False
            
    def verify_note_update(self):
        """Verify the note was updated by getting all notes"""
        self.log("🔍 Verifying note update...")
        try:
            response = self.session.get(f"{BACKEND_URL}/notes", timeout=10)
            if response.status_code == 200:
                data = response.json()
                notes = data.get("notes", [])
                
                # Find our updated note
                for note in notes:
                    if note.get("note_id") == self.test_note_id:
                        priority = note.get("priority", "N/A")
                        title = note.get("title", "N/A")
                        self.log(f"✅ Found updated note:")
                        self.log(f"   Title: {title}")
                        self.log(f"   Priority: {priority}")
                        
                        if priority == "high":
                            self.log("✅ Priority update verified successfully")
                            return True
                        else:
                            self.log(f"❌ Priority not updated correctly (expected 'high', got '{priority}')")
                            return False
                
                self.log("❌ Updated note not found in notes list")
                return False
            else:
                self.log(f"❌ Failed to get notes: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Verify update error: {e}")
            return False
            
    def cleanup_test_note(self):
        """Clean up the test note"""
        if not self.test_note_id:
            return
            
        self.log(f"🧹 Cleaning up test note: {self.test_note_id}")
        try:
            response = self.session.delete(f"{BACKEND_URL}/notes/{self.test_note_id}", timeout=5)
            if response.status_code == 200:
                self.log("✅ Test note cleaned up successfully")
            else:
                self.log(f"⚠️ Failed to clean up test note: {response.status_code}")
        except Exception as e:
            self.log(f"⚠️ Cleanup error: {e}")
            
    def run_put_test(self):
        """Run the complete PUT test"""
        self.log("🚀 Starting Notes API PUT Endpoint Testing")
        self.log(f"Backend URL: {BACKEND_URL}")
        self.log(f"Test User: {TEST_CREDENTIALS['email']}")
        
        tests = [
            ("Authentication", self.authenticate),
            ("Create Test Note", self.create_test_note),
            ("PUT Note Priority", self.test_put_note_priority),
            ("Verify Note Update", self.verify_note_update)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            self.log(f"\n--- Test: {test_name} ---")
            try:
                if test_func():
                    passed += 1
                    self.log(f"✅ {test_name} PASSED")
                else:
                    self.log(f"❌ {test_name} FAILED")
                    break  # Stop on first failure for this sequential test
            except Exception as e:
                self.log(f"❌ {test_name} ERROR: {e}")
                break
                
        # Cleanup
        self.cleanup_test_note()
        
        # Summary
        self.log(f"\n{'='*50}")
        self.log(f"NOTES API PUT TESTING SUMMARY")
        self.log(f"{'='*50}")
        self.log(f"Tests Passed: {passed}/{total}")
        self.log(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            self.log("🎉 PUT ENDPOINT FULLY FUNCTIONAL!")
            return True
        else:
            self.log("❌ PUT ENDPOINT HAS ISSUES")
            return False

if __name__ == "__main__":
    tester = NotesPUTTester()
    success = tester.run_put_test()
    sys.exit(0 if success else 1)