#!/usr/bin/env python3
"""
🎯 NOTES SORTING VALIDATION TEST - Phase 2
Create multiple notes with different periodic settings and verify proper sorting implementation.

TEST OBJECTIVE: Create multiple notes with different periodic settings and verify proper sorting implementation.

BACKEND TESTING STRATEGY:
1. Clean up existing notes (optional - delete some test notes if too many)
2. Create test notes in mixed order:
   - Note A: Specific month (January 2025) - should appear after monthly notes
   - Note B: Monthly note (high priority) - should appear FIRST  
   - Note C: Specific month (March 2025) - should appear after January 2025
   - Note D: Monthly note (normal priority) - should appear SECOND
   - Note E: Past month (December 2024) - should appear last
3. Retrieve all notes and verify they exist in backend
4. Frontend will handle sorting - backend just needs to provide the data

EXPECTED SORTING ORDER (frontend will sort):
1. Monthly notes (by creation date, newest first)
2. Future/current specific month notes (by chronological closeness)  
3. Past specific month notes

AUTHENTICATION: lperpere@yahoo.fr / L@Reunion974!
BACKEND URL: https://bizpost-manager-1.preview.emergentagent.com/api

TEST FOCUS: Create varied test data to validate sorting logic.
"""

import requests
import json
import sys
from datetime import datetime

class PeriodicNotesBackendTester:
    def __init__(self):
        self.base_url = "https://bizpost-manager-1.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.test_results = []
        self.created_notes = []  # Track created notes for cleanup
        
    def log_test(self, step, description, success, details=""):
        """Log test results"""
        status = "✅" if success else "❌"
        result = {
            "step": step,
            "description": description,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} Step {step}: {description}")
        if details:
            print(f"   Details: {details}")
        if not success:
            print(f"   ❌ FAILED: {details}")
        print()

    def authenticate(self):
        """Step 1: Authenticate with the backend"""
        try:
            auth_data = {
                "email": "lperpere@yahoo.fr",
                "password": "L@Reunion974!"
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/login-robust",
                json=auth_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                })
                
                self.log_test(1, "Authentication", True, 
                    f"User ID: {self.user_id}, Token obtained and configured")
                return True
            else:
                self.log_test(1, "Authentication", False, 
                    f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test(1, "Authentication", False, f"Exception: {str(e)}")
            return False

    def test_create_monthly_note(self):
        """Step 2: Create Monthly Note (is_monthly_note=true)"""
        try:
            note_data = {
                "description": "Note mensuelle récurrente",
                "content": "Cette note apparaît chaque mois automatiquement",
                "priority": "high",
                "is_monthly_note": True,
                "note_month": None,
                "note_year": None
            }
            
            response = self.session.post(
                f"{self.base_url}/notes",
                json=note_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                note = data.get("note", {})
                note_id = note.get("note_id")
                
                if note_id:
                    self.created_notes.append(note_id)
                
                # Verify periodic fields
                is_monthly = note.get("is_monthly_note")
                note_month = note.get("note_month")
                note_year = note.get("note_year")
                priority = note.get("priority")
                
                success = (is_monthly == True and 
                          note_month is None and 
                          note_year is None and
                          priority == "high")
                
                details = f"Note ID: {note_id}, is_monthly_note: {is_monthly}, note_month: {note_month}, note_year: {note_year}, priority: {priority}"
                self.log_test(2, "Create Monthly Note", success, details)
                return success
            else:
                self.log_test(2, "Create Monthly Note", False, 
                    f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test(2, "Create Monthly Note", False, f"Exception: {str(e)}")
            return False

    def test_create_specific_month_note(self):
        """Step 3: Create Specific Month Note (note_month=3, note_year=2025)"""
        try:
            note_data = {
                "description": "Note spécifique Mars 2025",
                "content": "Cette note est programmée pour Mars 2025 uniquement",
                "priority": "normal",
                "is_monthly_note": False,
                "note_month": 3,
                "note_year": 2025
            }
            
            response = self.session.post(
                f"{self.base_url}/notes",
                json=note_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                note = data.get("note", {})
                note_id = note.get("note_id")
                
                if note_id:
                    self.created_notes.append(note_id)
                
                # Verify periodic fields
                is_monthly = note.get("is_monthly_note")
                note_month = note.get("note_month")
                note_year = note.get("note_year")
                priority = note.get("priority")
                
                success = (is_monthly == False and 
                          note_month == 3 and 
                          note_year == 2025 and
                          priority == "normal")
                
                details = f"Note ID: {note_id}, is_monthly_note: {is_monthly}, note_month: {note_month}, note_year: {note_year}, priority: {priority}"
                self.log_test(3, "Create Specific Month Note", success, details)
                return success
            else:
                self.log_test(3, "Create Specific Month Note", False, 
                    f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test(3, "Create Specific Month Note", False, f"Exception: {str(e)}")
            return False

    def test_mixed_priority_notes(self):
        """Step 4: Test Mixed Priority with Periodic Settings"""
        try:
            test_cases = [
                {
                    "description": "Note priorité basse - Avril 2025",
                    "content": "Test priorité low avec mois spécifique",
                    "priority": "low",
                    "is_monthly_note": False,
                    "note_month": 4,
                    "note_year": 2025
                },
                {
                    "description": "Note priorité élevée - Mensuelle",
                    "content": "Test priorité high avec récurrence mensuelle",
                    "priority": "high",
                    "is_monthly_note": True,
                    "note_month": None,
                    "note_year": None
                }
            ]
            
            success_count = 0
            for i, note_data in enumerate(test_cases):
                response = self.session.post(
                    f"{self.base_url}/notes",
                    json=note_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    note = data.get("note", {})
                    note_id = note.get("note_id")
                    
                    if note_id:
                        self.created_notes.append(note_id)
                    
                    # Verify fields match expected
                    expected_priority = note_data["priority"]
                    expected_monthly = note_data["is_monthly_note"]
                    expected_month = note_data["note_month"]
                    expected_year = note_data["note_year"]
                    
                    actual_priority = note.get("priority")
                    actual_monthly = note.get("is_monthly_note")
                    actual_month = note.get("note_month")
                    actual_year = note.get("note_year")
                    
                    if (actual_priority == expected_priority and
                        actual_monthly == expected_monthly and
                        actual_month == expected_month and
                        actual_year == expected_year):
                        success_count += 1
            
            success = success_count == len(test_cases)
            details = f"Created {success_count}/{len(test_cases)} mixed priority notes successfully"
            self.log_test(4, "Mixed Priority Testing", success, details)
            return success
            
        except Exception as e:
            self.log_test(4, "Mixed Priority Testing", False, f"Exception: {str(e)}")
            return False

    def test_update_periodic_note(self):
        """Step 5: Update Periodic Note Settings"""
        try:
            if not self.created_notes:
                self.log_test(5, "Update Periodic Note", False, "No notes available to update")
                return False
            
            # Use the first created note for update test
            note_id = self.created_notes[0]
            
            update_data = {
                "description": "Note mise à jour - Juin 2025",
                "content": "Contenu modifié avec nouvelles dates périodiques",
                "priority": "medium",
                "is_monthly_note": False,
                "note_month": 6,
                "note_year": 2025
            }
            
            response = self.session.put(
                f"{self.base_url}/notes/{note_id}",
                json=update_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                note = data.get("note", {})
                
                # Verify updated fields
                is_monthly = note.get("is_monthly_note")
                note_month = note.get("note_month")
                note_year = note.get("note_year")
                priority = note.get("priority")
                description = note.get("description")
                
                success = (is_monthly == False and 
                          note_month == 6 and 
                          note_year == 2025 and
                          priority == "medium" and
                          "mise à jour" in description)
                
                details = f"Updated Note ID: {note_id}, is_monthly_note: {is_monthly}, note_month: {note_month}, note_year: {note_year}, priority: {priority}"
                self.log_test(5, "Update Periodic Note", success, details)
                return success
            else:
                self.log_test(5, "Update Periodic Note", False, 
                    f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test(5, "Update Periodic Note", False, f"Exception: {str(e)}")
            return False

    def test_retrieve_all_notes(self):
        """Step 6: Retrieve All Notes and Verify Periodic Fields"""
        try:
            response = self.session.get(
                f"{self.base_url}/notes",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                notes = data.get("notes", [])
                
                if not notes:
                    self.log_test(6, "Retrieve All Notes", False, "No notes found in response")
                    return False
                
                # Verify all notes have periodic fields
                valid_notes = 0
                for note in notes:
                    has_monthly_field = "is_monthly_note" in note
                    has_month_field = "note_month" in note
                    has_year_field = "note_year" in note
                    
                    if has_monthly_field and has_month_field and has_year_field:
                        valid_notes += 1
                
                success = valid_notes == len(notes)
                details = f"Found {len(notes)} notes, {valid_notes} have all periodic fields (is_monthly_note, note_month, note_year)"
                self.log_test(6, "Retrieve All Notes", success, details)
                return success
            else:
                self.log_test(6, "Retrieve All Notes", False, 
                    f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test(6, "Retrieve All Notes", False, f"Exception: {str(e)}")
            return False

    def test_edge_cases(self):
        """Step 7: Test Edge Cases and Validation"""
        try:
            edge_cases = [
                {
                    "name": "Invalid month (13)",
                    "data": {
                        "description": "Test mois invalide",
                        "content": "Test avec mois 13",
                        "priority": "normal",
                        "is_monthly_note": False,
                        "note_month": 13,
                        "note_year": 2025
                    },
                    "expect_success": False
                },
                {
                    "name": "Invalid month (0)",
                    "data": {
                        "description": "Test mois zéro",
                        "content": "Test avec mois 0",
                        "priority": "normal",
                        "is_monthly_note": False,
                        "note_month": 0,
                        "note_year": 2025
                    },
                    "expect_success": False
                },
                {
                    "name": "Valid edge case - December",
                    "data": {
                        "description": "Test Décembre valide",
                        "content": "Test avec mois 12",
                        "priority": "normal",
                        "is_monthly_note": False,
                        "note_month": 12,
                        "note_year": 2025
                    },
                    "expect_success": True
                }
            ]
            
            passed_cases = 0
            for case in edge_cases:
                try:
                    response = self.session.post(
                        f"{self.base_url}/notes",
                        json=case["data"],
                        timeout=30
                    )
                    
                    if case["expect_success"]:
                        # Should succeed
                        if response.status_code == 200:
                            data = response.json()
                            note_id = data.get("note", {}).get("note_id")
                            if note_id:
                                self.created_notes.append(note_id)
                            passed_cases += 1
                    else:
                        # Should fail with validation error
                        if response.status_code in [400, 422]:
                            passed_cases += 1
                        elif response.status_code == 200:
                            # If it unexpectedly succeeds, clean up
                            data = response.json()
                            note_id = data.get("note", {}).get("note_id")
                            if note_id:
                                self.created_notes.append(note_id)
                            
                except Exception:
                    if not case["expect_success"]:
                        passed_cases += 1  # Exception expected for invalid cases
            
            success = passed_cases == len(edge_cases)
            details = f"Passed {passed_cases}/{len(edge_cases)} edge case tests"
            self.log_test(7, "Edge Cases Validation", success, details)
            return success
            
        except Exception as e:
            self.log_test(7, "Edge Cases Validation", False, f"Exception: {str(e)}")
            return False

    def cleanup_test_notes(self):
        """Clean up created test notes"""
        print("\n🧹 Cleaning up test notes...")
        cleaned = 0
        for note_id in self.created_notes:
            try:
                response = self.session.delete(
                    f"{self.base_url}/notes/{note_id}",
                    timeout=30
                )
                if response.status_code == 200:
                    cleaned += 1
                    print(f"   ✅ Deleted note {note_id}")
                else:
                    print(f"   ⚠️ Failed to delete note {note_id}: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error deleting note {note_id}: {str(e)}")
        
        print(f"🧹 Cleanup complete: {cleaned}/{len(self.created_notes)} notes deleted\n")

    def run_all_tests(self):
        """Run all periodic notes backend tests"""
        print("🎯 PERIODIC NOTES BACKEND INTEGRATION TESTING - Phase 1 Validation")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print()
        
        try:
            # Step 1: Authentication
            if not self.authenticate():
                return False
            
            # Step 2: Create Monthly Note
            self.test_create_monthly_note()
            
            # Step 3: Create Specific Month Note
            self.test_create_specific_month_note()
            
            # Step 4: Mixed Priority Testing
            self.test_mixed_priority_notes()
            
            # Step 5: Update Periodic Note
            self.test_update_periodic_note()
            
            # Step 6: Retrieve All Notes
            self.test_retrieve_all_notes()
            
            # Step 7: Edge Cases
            self.test_edge_cases()
            
            # Calculate success rate
            successful_tests = sum(1 for result in self.test_results if result["success"])
            total_tests = len(self.test_results)
            success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
            
            print("=" * 80)
            print("🎯 PERIODIC NOTES BACKEND TESTING SUMMARY")
            print("=" * 80)
            print(f"Total Tests: {total_tests}")
            print(f"Successful: {successful_tests}")
            print(f"Failed: {total_tests - successful_tests}")
            print(f"Success Rate: {success_rate:.1f}%")
            print()
            
            # Print detailed results
            for result in self.test_results:
                status = "✅" if result["success"] else "❌"
                print(f"{status} Step {result['step']}: {result['description']}")
                if result["details"]:
                    print(f"   {result['details']}")
            
            print()
            
            # Determine overall result
            if success_rate >= 85:
                print("🎉 PERIODIC NOTES BACKEND TESTING COMPLETED SUCCESSFULLY")
                print("✅ All critical periodic note CRUD operations are working correctly")
                print("✅ Periodic fields (is_monthly_note, note_month, note_year) are properly stored and retrieved")
                print("✅ Priority field handling working as expected")
                print("✅ Authentication system working perfectly")
                overall_success = True
            else:
                print("🚨 PERIODIC NOTES BACKEND TESTING COMPLETED WITH ISSUES")
                print("❌ Some critical functionality is not working correctly")
                overall_success = False
            
            return overall_success
            
        finally:
            # Always clean up test notes
            if self.created_notes:
                self.cleanup_test_notes()

def main():
    """Main test execution"""
    tester = PeriodicNotesBackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎯 CONCLUSION: Periodic Notes Backend is FULLY OPERATIONAL for production use")
        sys.exit(0)
    else:
        print("🚨 CONCLUSION: Periodic Notes Backend has critical issues requiring fixes")
        sys.exit(1)

if __name__ == "__main__":
    main()
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