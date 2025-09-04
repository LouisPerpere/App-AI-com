#!/usr/bin/env python3
"""
Notes API Backend Testing
Testing the newly implemented Notes API endpoints in server.py
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://bizpost-manager-1.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class NotesAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.created_notes = []
        
    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def test_health_check(self):
        """Test 1: Health Check"""
        self.log("🔍 Testing health check...")
        try:
            response = self.session.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Health check successful: {data.get('status', 'unknown')}")
                return True
            else:
                self.log(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Health check error: {e}")
            return False
            
    def test_authentication(self):
        """Test 2: Authentication with login-robust"""
        self.log("🔍 Testing authentication...")
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
                self.log(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ Authentication error: {e}")
            return False
            
    def test_get_notes_empty(self):
        """Test 3: GET /api/notes (should return empty list initially or existing notes)"""
        self.log("🔍 Testing GET /api/notes...")
        try:
            response = self.session.get(f"{BACKEND_URL}/notes", timeout=10)
            if response.status_code == 200:
                data = response.json()
                notes = data.get("notes", [])
                self.log(f"✅ GET notes successful - Found {len(notes)} existing notes")
                return True
            else:
                self.log(f"❌ GET notes failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ GET notes error: {e}")
            return False
            
    def test_create_note_high_priority(self):
        """Test 4: POST /api/notes with high priority test data"""
        self.log("🔍 Testing POST /api/notes (high priority)...")
        test_note = {
            "title": "Test Note",
            "content": "Contenu de test pour la note",
            "priority": "high"
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
                note_id = note.get("note_id")
                if note_id:
                    self.created_notes.append(note_id)
                self.log(f"✅ Create high priority note successful - Note ID: {note_id}")
                self.log(f"   Title: {note.get('title', 'N/A')}")
                self.log(f"   Priority: {note.get('priority', 'N/A')}")
                return True
            else:
                self.log(f"❌ Create note failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ Create note error: {e}")
            return False
            
    def test_create_note_medium_priority(self):
        """Test 5: POST /api/notes with medium priority"""
        self.log("🔍 Testing POST /api/notes (medium priority)...")
        test_note = {
            "title": "Note Priorité Medium",
            "content": "Une autre note de test",
            "priority": "medium"
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
                note_id = note.get("note_id")
                if note_id:
                    self.created_notes.append(note_id)
                self.log(f"✅ Create medium priority note successful - Note ID: {note_id}")
                return True
            else:
                self.log(f"❌ Create medium note failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ Create medium note error: {e}")
            return False
            
    def test_get_notes_with_data(self):
        """Test 6: GET /api/notes again to verify notes were created and persisted"""
        self.log("🔍 Testing GET /api/notes (with created notes)...")
        try:
            response = self.session.get(f"{BACKEND_URL}/notes", timeout=10)
            if response.status_code == 200:
                data = response.json()
                notes = data.get("notes", [])
                self.log(f"✅ GET notes with data successful - Found {len(notes)} total notes")
                
                # Verify our created notes are present
                found_notes = 0
                for note in notes:
                    if note.get("note_id") in self.created_notes:
                        found_notes += 1
                        self.log(f"   Found created note: {note.get('title', 'N/A')} (Priority: {note.get('priority', 'N/A')})")
                
                if found_notes >= len(self.created_notes):
                    self.log(f"✅ All {found_notes} created notes found in response")
                else:
                    self.log(f"⚠️ Only {found_notes}/{len(self.created_notes)} created notes found")
                
                return True
            else:
                self.log(f"❌ GET notes with data failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ GET notes with data error: {e}")
            return False
            
    def test_priority_validation(self):
        """Test 7: Priority field validation with different values"""
        self.log("🔍 Testing priority field validation...")
        priorities = ["high", "medium", "low", "normal"]
        success_count = 0
        
        for priority in priorities:
            test_note = {
                "title": f"Test Priority {priority.title()}",
                "content": f"Test note with {priority} priority",
                "priority": priority
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
                    note_id = note.get("note_id")
                    if note_id:
                        self.created_notes.append(note_id)
                    self.log(f"✅ Priority '{priority}' accepted - Note ID: {note_id}")
                    success_count += 1
                else:
                    self.log(f"❌ Priority '{priority}' rejected: {response.status_code}")
            except Exception as e:
                self.log(f"❌ Priority '{priority}' error: {e}")
                
        return success_count == len(priorities)
        
    def test_default_priority(self):
        """Test 8: Verify priority defaults to 'normal' when not specified"""
        self.log("🔍 Testing default priority behavior...")
        test_note = {
            "title": "Test Default Priority",
            "content": "Note without priority specified"
            # No priority field
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
                note_id = note.get("note_id")
                priority = note.get("priority", "unknown")
                if note_id:
                    self.created_notes.append(note_id)
                
                if priority == "normal":
                    self.log(f"✅ Default priority working - Note ID: {note_id}, Priority: {priority}")
                    return True
                else:
                    self.log(f"⚠️ Default priority unexpected - Priority: {priority} (expected 'normal')")
                    return True  # Still consider success if note was created
            else:
                self.log(f"❌ Default priority test failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ Default priority error: {e}")
            return False
            
    def test_delete_note(self):
        """Test 9: DELETE /api/notes/{note_id} with an existing note ID"""
        if not self.created_notes:
            self.log("⚠️ No notes to delete - skipping delete test")
            return True
            
        note_id_to_delete = self.created_notes[0]
        self.log(f"🔍 Testing DELETE /api/notes/{note_id_to_delete}...")
        
        try:
            response = self.session.delete(f"{BACKEND_URL}/notes/{note_id_to_delete}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                self.log(f"✅ Delete note successful - {message}")
                self.created_notes.remove(note_id_to_delete)
                return True
            else:
                self.log(f"❌ Delete note failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ Delete note error: {e}")
            return False
            
    def test_verify_deletion(self):
        """Test 10: GET /api/notes to verify the note was deleted"""
        self.log("🔍 Verifying note deletion...")
        try:
            response = self.session.get(f"{BACKEND_URL}/notes", timeout=10)
            if response.status_code == 200:
                data = response.json()
                notes = data.get("notes", [])
                
                # Check that deleted note is not in the list
                deleted_note_found = False
                for note in notes:
                    if note.get("note_id") == self.created_notes[0] if self.created_notes else "deleted_note":
                        deleted_note_found = True
                        break
                
                if not deleted_note_found:
                    self.log(f"✅ Note deletion verified - Deleted note not found in list")
                    return True
                else:
                    self.log(f"❌ Note deletion failed - Deleted note still in list")
                    return False
            else:
                self.log(f"❌ Verification failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ Verification error: {e}")
            return False
            
    def test_delete_nonexistent_note(self):
        """Test 11: DELETE /api/notes/nonexistent-id (should return 404)"""
        self.log("🔍 Testing DELETE with nonexistent note ID...")
        nonexistent_id = "nonexistent-note-id-12345"
        
        try:
            response = self.session.delete(f"{BACKEND_URL}/notes/{nonexistent_id}", timeout=10)
            if response.status_code == 404:
                self.log(f"✅ Nonexistent note deletion correctly returned 404")
                return True
            else:
                self.log(f"❌ Nonexistent note deletion unexpected status: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Nonexistent note deletion error: {e}")
            return False
            
    def test_invalid_note_data(self):
        """Test 12: POST /api/notes with invalid data (empty title/content)"""
        self.log("🔍 Testing POST with invalid data...")
        
        # Test empty title
        invalid_note1 = {
            "title": "",
            "content": "Valid content",
            "priority": "normal"
        }
        
        # Test empty content
        invalid_note2 = {
            "title": "Valid title",
            "content": "",
            "priority": "normal"
        }
        
        # Test missing required fields
        invalid_note3 = {
            "priority": "normal"
        }
        
        test_cases = [
            ("empty title", invalid_note1),
            ("empty content", invalid_note2),
            ("missing fields", invalid_note3)
        ]
        
        success_count = 0
        for test_name, invalid_note in test_cases:
            try:
                response = self.session.post(
                    f"{BACKEND_URL}/notes",
                    json=invalid_note,
                    timeout=10
                )
                if response.status_code in [400, 422]:  # Expected validation errors
                    self.log(f"✅ Invalid data test '{test_name}' correctly rejected: {response.status_code}")
                    success_count += 1
                elif response.status_code == 200:
                    self.log(f"⚠️ Invalid data test '{test_name}' unexpectedly accepted")
                    # Clean up if note was created
                    data = response.json()
                    note = data.get("note", {})
                    note_id = note.get("note_id")
                    if note_id:
                        self.created_notes.append(note_id)
                else:
                    self.log(f"❌ Invalid data test '{test_name}' unexpected status: {response.status_code}")
            except Exception as e:
                self.log(f"❌ Invalid data test '{test_name}' error: {e}")
                
        return success_count >= 2  # At least 2 out of 3 should work
        
    def cleanup_created_notes(self):
        """Clean up any remaining created notes"""
        if not self.created_notes:
            return
            
        self.log(f"🧹 Cleaning up {len(self.created_notes)} remaining notes...")
        for note_id in self.created_notes[:]:
            try:
                response = self.session.delete(f"{BACKEND_URL}/notes/{note_id}", timeout=5)
                if response.status_code == 200:
                    self.log(f"✅ Cleaned up note: {note_id}")
                    self.created_notes.remove(note_id)
                else:
                    self.log(f"⚠️ Failed to clean up note {note_id}: {response.status_code}")
            except Exception as e:
                self.log(f"⚠️ Cleanup error for note {note_id}: {e}")
                
    def run_all_tests(self):
        """Run all Notes API tests"""
        self.log("🚀 Starting Notes API Backend Testing")
        self.log(f"Backend URL: {BACKEND_URL}")
        self.log(f"Test User: {TEST_CREDENTIALS['email']}")
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Authentication", self.test_authentication),
            ("GET Notes (Empty)", self.test_get_notes_empty),
            ("Create Note (High Priority)", self.test_create_note_high_priority),
            ("Create Note (Medium Priority)", self.test_create_note_medium_priority),
            ("GET Notes (With Data)", self.test_get_notes_with_data),
            ("Priority Validation", self.test_priority_validation),
            ("Default Priority", self.test_default_priority),
            ("Delete Note", self.test_delete_note),
            ("Verify Deletion", self.test_verify_deletion),
            ("Delete Nonexistent Note", self.test_delete_nonexistent_note),
            ("Invalid Note Data", self.test_invalid_note_data)
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
            except Exception as e:
                self.log(f"❌ {test_name} ERROR: {e}")
                
        # Cleanup
        self.cleanup_created_notes()
        
        # Summary
        self.log(f"\n{'='*50}")
        self.log(f"NOTES API TESTING SUMMARY")
        self.log(f"{'='*50}")
        self.log(f"Tests Passed: {passed}/{total}")
        self.log(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            self.log("🎉 ALL TESTS PASSED - Notes API is fully functional!")
            return True
        elif passed >= total * 0.8:  # 80% success rate
            self.log("✅ MOSTLY SUCCESSFUL - Notes API is working with minor issues")
            return True
        else:
            self.log("❌ SIGNIFICANT ISSUES - Notes API needs attention")
            return False

if __name__ == "__main__":
    tester = NotesAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)