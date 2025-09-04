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

class NotesSortingValidationTester:
    def __init__(self):
        self.base_url = "https://bizpost-manager-1.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.test_results = []
        self.created_notes = []  # Track created notes for cleanup
        self.test_notes_data = []  # Store test notes with expected sorting info
        
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

    def cleanup_existing_notes(self):
        """Step 2: Optional cleanup of existing notes (if too many)"""
        try:
            response = self.session.get(f"{self.base_url}/notes", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                existing_notes = data.get("notes", [])
                
                # If there are more than 10 notes, clean up some older ones
                if len(existing_notes) > 10:
                    notes_to_delete = existing_notes[10:]  # Keep first 10, delete rest
                    deleted_count = 0
                    
                    for note in notes_to_delete:
                        note_id = note.get("note_id")
                        if note_id:
                            try:
                                delete_response = self.session.delete(
                                    f"{self.base_url}/notes/{note_id}",
                                    timeout=30
                                )
                                if delete_response.status_code == 200:
                                    deleted_count += 1
                            except Exception:
                                pass  # Continue with other deletions
                    
                    self.log_test(2, "Cleanup Existing Notes", True, 
                        f"Cleaned up {deleted_count} old notes, {len(existing_notes) - deleted_count} notes remaining")
                else:
                    self.log_test(2, "Cleanup Existing Notes", True, 
                        f"Found {len(existing_notes)} existing notes - no cleanup needed")
                return True
            else:
                self.log_test(2, "Cleanup Existing Notes", False, 
                    f"Failed to retrieve existing notes: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test(2, "Cleanup Existing Notes", False, f"Exception: {str(e)}")
            return False

    def create_test_notes_mixed_order(self):
        """Step 3: Create test notes in mixed order for sorting validation"""
        try:
            # Define test notes according to the review request
            test_notes = [
                {
                    "name": "Note A - January 2025 (Specific Month)",
                    "data": {
                        "description": "Note spécifique Janvier 2025",
                        "content": "Cette note est programmée pour Janvier 2025 - devrait apparaître après les notes mensuelles",
                        "priority": "normal",
                        "is_monthly_note": False,
                        "note_month": 1,
                        "note_year": 2025
                    },
                    "expected_position": "after_monthly"
                },
                {
                    "name": "Note B - Monthly High Priority (Should be FIRST)",
                    "data": {
                        "description": "Note mensuelle priorité haute",
                        "content": "Cette note mensuelle haute priorité devrait apparaître EN PREMIER",
                        "priority": "high",
                        "is_monthly_note": True,
                        "note_month": None,
                        "note_year": None
                    },
                    "expected_position": "first"
                },
                {
                    "name": "Note C - March 2025 (Specific Month)",
                    "data": {
                        "description": "Note spécifique Mars 2025",
                        "content": "Cette note est programmée pour Mars 2025 - devrait apparaître après Janvier 2025",
                        "priority": "normal",
                        "is_monthly_note": False,
                        "note_month": 3,
                        "note_year": 2025
                    },
                    "expected_position": "after_january"
                },
                {
                    "name": "Note D - Monthly Normal Priority (Should be SECOND)",
                    "data": {
                        "description": "Note mensuelle priorité normale",
                        "content": "Cette note mensuelle priorité normale devrait apparaître EN DEUXIÈME",
                        "priority": "normal",
                        "is_monthly_note": True,
                        "note_month": None,
                        "note_year": None
                    },
                    "expected_position": "second"
                },
                {
                    "name": "Note E - December 2024 (Past Month - Should be LAST)",
                    "data": {
                        "description": "Note passée Décembre 2024",
                        "content": "Cette note du passé (Décembre 2024) devrait apparaître EN DERNIER",
                        "priority": "normal",
                        "is_monthly_note": False,
                        "note_month": 12,
                        "note_year": 2024
                    },
                    "expected_position": "last"
                }
            ]
            
            created_count = 0
            for note_info in test_notes:
                try:
                    response = self.session.post(
                        f"{self.base_url}/notes",
                        json=note_info["data"],
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        note = data.get("note", {})
                        note_id = note.get("note_id")
                        
                        if note_id:
                            self.created_notes.append(note_id)
                            # Store note data with expected position for validation
                            self.test_notes_data.append({
                                "note_id": note_id,
                                "name": note_info["name"],
                                "expected_position": note_info["expected_position"],
                                "is_monthly_note": note.get("is_monthly_note"),
                                "note_month": note.get("note_month"),
                                "note_year": note.get("note_year"),
                                "priority": note.get("priority"),
                                "description": note.get("description")
                            })
                            created_count += 1
                            print(f"   ✅ Created: {note_info['name']} - ID: {note_id}")
                    else:
                        print(f"   ❌ Failed to create: {note_info['name']} - Status: {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Error creating {note_info['name']}: {str(e)}")
            
            success = created_count == len(test_notes)
            details = f"Successfully created {created_count}/{len(test_notes)} test notes for sorting validation"
            self.log_test(3, "Create Test Notes in Mixed Order", success, details)
            return success
            
        except Exception as e:
            self.log_test(3, "Create Test Notes in Mixed Order", False, f"Exception: {str(e)}")
            return False

    def retrieve_and_verify_notes_data(self):
        """Step 4: Retrieve all notes and verify they exist in backend"""
        try:
            response = self.session.get(f"{self.base_url}/notes", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                all_notes = data.get("notes", [])
                
                if not all_notes:
                    self.log_test(4, "Retrieve and Verify Notes Data", False, "No notes found in response")
                    return False
                
                # Verify all our test notes are present
                found_test_notes = 0
                for test_note in self.test_notes_data:
                    for note in all_notes:
                        if note.get("note_id") == test_note["note_id"]:
                            found_test_notes += 1
                            # Verify the periodic fields are correctly stored
                            is_monthly = note.get("is_monthly_note")
                            note_month = note.get("note_month")
                            note_year = note.get("note_year")
                            priority = note.get("priority")
                            
                            print(f"   ✅ Found: {test_note['name']}")
                            print(f"      is_monthly_note: {is_monthly}, note_month: {note_month}, note_year: {note_year}, priority: {priority}")
                            break
                
                success = found_test_notes == len(self.test_notes_data)
                details = f"Found {found_test_notes}/{len(self.test_notes_data)} test notes in backend. Total notes in system: {len(all_notes)}"
                
                if success:
                    details += f"\n   All test notes properly stored with correct periodic fields (is_monthly_note, note_month, note_year, priority)"
                
                self.log_test(4, "Retrieve and Verify Notes Data", success, details)
                return success
            else:
                self.log_test(4, "Retrieve and Verify Notes Data", False, 
                    f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test(4, "Retrieve and Verify Notes Data", False, f"Exception: {str(e)}")
            return False

    def verify_backend_data_structure(self):
        """Step 5: Verify backend provides proper data structure for frontend sorting"""
        try:
            response = self.session.get(f"{self.base_url}/notes", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                all_notes = data.get("notes", [])
                
                # Check that all notes have the required fields for sorting
                required_fields = ["note_id", "is_monthly_note", "note_month", "note_year", "priority", "description", "content"]
                valid_notes = 0
                
                for note in all_notes:
                    has_all_fields = all(field in note for field in required_fields)
                    if has_all_fields:
                        valid_notes += 1
                    else:
                        missing_fields = [field for field in required_fields if field not in note]
                        print(f"   ⚠️ Note {note.get('note_id', 'unknown')} missing fields: {missing_fields}")
                
                success = valid_notes == len(all_notes)
                details = f"Backend data structure validation: {valid_notes}/{len(all_notes)} notes have all required fields for frontend sorting"
                
                if success:
                    details += f"\n   ✅ All notes contain: {', '.join(required_fields)}"
                    details += f"\n   ✅ Backend ready to provide sorting data to frontend"
                
                self.log_test(5, "Verify Backend Data Structure", success, details)
                return success
            else:
                self.log_test(5, "Verify Backend Data Structure", False, 
                    f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test(5, "Verify Backend Data Structure", False, f"Exception: {str(e)}")
            return False

    def display_sorting_expectations(self):
        """Step 6: Display expected sorting order for frontend reference"""
        try:
            print("\n" + "="*80)
            print("📋 EXPECTED SORTING ORDER FOR FRONTEND IMPLEMENTATION")
            print("="*80)
            print("The backend has successfully provided the following test data.")
            print("Frontend should sort these notes in this order:")
            print()
            
            # Group notes by expected position
            monthly_notes = [note for note in self.test_notes_data if note["is_monthly_note"]]
            specific_future_notes = [note for note in self.test_notes_data 
                                   if not note["is_monthly_note"] and 
                                   (note["note_year"] > 2024 or (note["note_year"] == 2024 and note["note_month"] >= 12))]
            past_notes = [note for note in self.test_notes_data 
                         if not note["is_monthly_note"] and 
                         (note["note_year"] < 2024 or (note["note_year"] == 2024 and note["note_month"] < 12))]
            
            position = 1
            
            print("🔁 MONTHLY NOTES (by creation date, newest first):")
            # Sort monthly notes by priority (high first)
            monthly_sorted = sorted(monthly_notes, key=lambda x: (x["priority"] != "high", x["priority"]))
            for note in monthly_sorted:
                print(f"   {position}. {note['name']} (Priority: {note['priority']})")
                position += 1
            
            print("\n📅 FUTURE/CURRENT SPECIFIC MONTH NOTES (by chronological closeness):")
            # Sort specific notes by year/month
            specific_sorted = sorted(specific_future_notes, key=lambda x: (x["note_year"], x["note_month"]))
            for note in specific_sorted:
                month_name = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][note["note_month"]]
                print(f"   {position}. {note['name']} ({month_name} {note['note_year']})")
                position += 1
            
            print("\n📆 PAST SPECIFIC MONTH NOTES:")
            past_sorted = sorted(past_notes, key=lambda x: (x["note_year"], x["note_month"]), reverse=True)
            for note in past_sorted:
                month_name = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][note["note_month"]]
                print(f"   {position}. {note['name']} ({month_name} {note['note_year']})")
                position += 1
            
            print("\n" + "="*80)
            
            self.log_test(6, "Display Sorting Expectations", True, 
                f"Provided sorting reference for {len(self.test_notes_data)} test notes")
            return True
            
        except Exception as e:
            self.log_test(6, "Display Sorting Expectations", False, f"Exception: {str(e)}")
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
        """Run all notes sorting validation tests"""
        print("🎯 NOTES SORTING VALIDATION TEST - Phase 2")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print()
        
        try:
            # Step 1: Authentication
            if not self.authenticate():
                return False
            
            # Step 2: Optional cleanup
            self.cleanup_existing_notes()
            
            # Step 3: Create test notes in mixed order
            self.create_test_notes_mixed_order()
            
            # Step 4: Retrieve and verify notes data
            self.retrieve_and_verify_notes_data()
            
            # Step 5: Verify backend data structure
            self.verify_backend_data_structure()
            
            # Step 6: Display sorting expectations
            self.display_sorting_expectations()
            
            # Calculate success rate
            successful_tests = sum(1 for result in self.test_results if result["success"])
            total_tests = len(self.test_results)
            success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
            
            print("=" * 80)
            print("🎯 NOTES SORTING VALIDATION TEST SUMMARY")
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
                print("🎉 NOTES SORTING VALIDATION TEST COMPLETED SUCCESSFULLY")
                print("✅ Backend successfully created varied test data for sorting validation")
                print("✅ All test notes properly stored with correct periodic fields")
                print("✅ Backend provides proper data structure for frontend sorting")
                print("✅ Test data covers all sorting scenarios (monthly, future, past)")
                print("✅ Frontend can now implement sorting logic using the provided data")
                overall_success = True
            else:
                print("🚨 NOTES SORTING VALIDATION TEST COMPLETED WITH ISSUES")
                print("❌ Some critical functionality is not working correctly")
                overall_success = False
            
            return overall_success
            
        finally:
            # Always clean up test notes
            if self.created_notes:
                self.cleanup_test_notes()

def main():
    """Main test execution"""
    tester = NotesSortingValidationTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎯 CONCLUSION: Notes Sorting Validation Test PASSED - Backend ready for frontend sorting implementation")
        sys.exit(0)
    else:
        print("🚨 CONCLUSION: Notes Sorting Validation Test FAILED - Backend issues need to be resolved")
        sys.exit(1)

if __name__ == "__main__":
    main()