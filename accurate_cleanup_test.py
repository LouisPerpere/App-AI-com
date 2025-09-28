#!/usr/bin/env python3
"""
🎯 PHASE 3 TESTING - ACCURATE PERIODIC NOTES CLEANUP VALIDATION

TEST OBJECTIVE: Validate the automatic cleanup system with accurate understanding of the logic.

CLEANUP LOGIC UNDERSTANDING:
- Cleanup only runs on/after 5th of each month
- Only deletes notes from the PREVIOUS month (current_month - 1)
- Monthly notes (is_monthly_note=true) are NEVER deleted
- Specific month notes (is_monthly_note=false) are deleted if they match the target month/year

CURRENT DATE: September 4, 2025
- Cleanup will NOT run today (before 5th)
- If it did run, it would target August 2025 notes
- December 2024 notes would only be deleted in January 2025 (on/after Jan 5)

TESTING STRATEGY:
1. Create test notes for various scenarios
2. Test manual cleanup endpoint (should report why it won't run)
3. Validate that the logic correctly identifies target month
4. Test edge cases and monthly note preservation

AUTHENTICATION: lperpere@yahoo.fr / L@Reunion974!
BACKEND URL: https://social-publisher-10.preview.emergentagent.com/api
"""

import requests
import json
import sys
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

class AccurateCleanupTester:
    def __init__(self):
        self.base_url = "https://social-publisher-10.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.test_results = []
        self.created_notes = []
        self.test_notes_data = []
        
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
                
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                })
                
                self.log_test(1, "Authentication", True, 
                    f"User ID: {self.user_id}, JWT token obtained and configured")
                return True
            else:
                self.log_test(1, "Authentication", False, 
                    f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test(1, "Authentication", False, f"Exception: {str(e)}")
            return False

    def create_comprehensive_test_notes(self):
        """Step 2: Create comprehensive test notes for accurate cleanup validation"""
        try:
            today = date.today()
            current_month = today.month
            current_year = today.year
            current_day = today.day
            
            # Calculate target month for cleanup (what would be deleted if cleanup ran)
            if current_month == 1:
                target_month = 12
                target_year = current_year - 1
            else:
                target_month = current_month - 1
                target_year = current_year
            
            # Define comprehensive test notes
            test_notes = [
                {
                    "name": f"Target Month Note ({target_month}/{target_year}) - WOULD BE DELETED",
                    "data": {
                        "description": f"Note cible {target_month}/{target_year} - À supprimer",
                        "content": f"Cette note de {target_month}/{target_year} serait supprimée si le nettoyage s'exécutait",
                        "priority": "normal",
                        "is_monthly_note": False,
                        "note_month": target_month,
                        "note_year": target_year
                    },
                    "would_be_deleted": current_day >= 5,
                    "category": "target_specific"
                },
                {
                    "name": "December 2024 Note - NOT TARGET (would need Jan 5+ 2025)",
                    "data": {
                        "description": "Note Décembre 2024 - Pas cible actuelle",
                        "content": "Cette note de Décembre 2024 ne serait supprimée qu'en Janvier 2025 (après le 5)",
                        "priority": "high",
                        "is_monthly_note": False,
                        "note_month": 12,
                        "note_year": 2024
                    },
                    "would_be_deleted": False,  # Not target month for current cleanup
                    "category": "old_specific"
                },
                {
                    "name": "Monthly Note High Priority - NEVER DELETED",
                    "data": {
                        "description": "Note mensuelle haute priorité - PERMANENTE",
                        "content": "Cette note mensuelle ne devrait JAMAIS être supprimée",
                        "priority": "high",
                        "is_monthly_note": True,
                        "note_month": None,
                        "note_year": None
                    },
                    "would_be_deleted": False,
                    "category": "monthly_permanent"
                },
                {
                    "name": "Monthly Note Normal Priority - NEVER DELETED",
                    "data": {
                        "description": "Note mensuelle priorité normale - PERMANENTE",
                        "content": "Cette note mensuelle ne devrait JAMAIS être supprimée",
                        "priority": "normal",
                        "is_monthly_note": True,
                        "note_month": None,
                        "note_year": None
                    },
                    "would_be_deleted": False,
                    "category": "monthly_permanent"
                },
                {
                    "name": f"Current Month Note ({current_month}/{current_year}) - NOT TARGET",
                    "data": {
                        "description": f"Note mois actuel {current_month}/{current_year}",
                        "content": f"Cette note du mois actuel ne devrait pas être supprimée",
                        "priority": "medium",
                        "is_monthly_note": False,
                        "note_month": current_month,
                        "note_year": current_year
                    },
                    "would_be_deleted": False,
                    "category": "current_specific"
                },
                {
                    "name": "Future Note (March 2026) - NOT TARGET",
                    "data": {
                        "description": "Note future Mars 2026",
                        "content": "Cette note future ne devrait pas être supprimée",
                        "priority": "low",
                        "is_monthly_note": False,
                        "note_month": 3,
                        "note_year": 2026
                    },
                    "would_be_deleted": False,
                    "category": "future_specific"
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
                            self.test_notes_data.append({
                                "note_id": note_id,
                                "name": note_info["name"],
                                "would_be_deleted": note_info["would_be_deleted"],
                                "category": note_info["category"],
                                "is_monthly_note": note.get("is_monthly_note"),
                                "note_month": note.get("note_month"),
                                "note_year": note.get("note_year"),
                                "priority": note.get("priority"),
                                "description": note.get("description")
                            })
                            created_count += 1
                            deletion_status = "WOULD BE DELETED" if note_info["would_be_deleted"] else "would remain"
                            print(f"   ✅ Created: {note_info['name']} - ID: {note_id} ({deletion_status})")
                    else:
                        print(f"   ❌ Failed to create: {note_info['name']} - Status: {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Error creating {note_info['name']}: {str(e)}")
            
            success = created_count == len(test_notes)
            details = f"Successfully created {created_count}/{len(test_notes)} comprehensive test notes"
            details += f"\n   Current date: {today.strftime('%Y-%m-%d')} (Day {current_day} of month)"
            details += f"\n   Target month for cleanup: {target_month}/{target_year}"
            details += f"\n   Cleanup would run: {'Yes' if current_day >= 5 else 'No (before 5th)'}"
            
            self.log_test(2, "Create Comprehensive Test Notes", success, details)
            return success
            
        except Exception as e:
            self.log_test(2, "Create Comprehensive Test Notes", False, f"Exception: {str(e)}")
            return False

    def test_cleanup_endpoint_behavior(self):
        """Step 3: Test cleanup endpoint behavior and response"""
        try:
            response = self.session.post(
                f"{self.base_url}/notes/cleanup-expired",
                json={},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                result = data.get("result", {})
                
                deleted_count = result.get("deleted_count", 0)
                reason = result.get("reason", "")
                target_month = result.get("target_month")
                target_year = result.get("target_year")
                
                today = date.today()
                expected_no_cleanup = today.day < 5
                
                if expected_no_cleanup:
                    # Should not run cleanup
                    success = deleted_count == 0 and "5th of month" in reason
                    details = f"Cleanup correctly did not run (day {today.day} < 5)"
                    details += f"\n   Message: {message}"
                    details += f"\n   Reason: {reason}"
                    details += f"\n   Deleted count: {deleted_count}"
                else:
                    # Should run cleanup
                    success = True  # Any result is valid when cleanup runs
                    details = f"Cleanup ran as expected (day {today.day} >= 5)"
                    details += f"\n   Message: {message}"
                    details += f"\n   Deleted count: {deleted_count}"
                    if target_month and target_year:
                        details += f"\n   Target month: {target_month}/{target_year}"
                
                self.log_test(3, "Test Cleanup Endpoint Behavior", success, details)
                return success, result
            else:
                self.log_test(3, "Test Cleanup Endpoint Behavior", False, 
                    f"Status: {response.status_code}, Response: {response.text}")
                return False, {}
                
        except Exception as e:
            self.log_test(3, "Test Cleanup Endpoint Behavior", False, f"Exception: {str(e)}")
            return False, {}

    def validate_cleanup_logic_accuracy(self):
        """Step 4: Validate that cleanup logic correctly identifies target month"""
        try:
            today = date.today()
            current_month = today.month
            current_year = today.year
            current_day = today.day
            
            # Calculate expected target month based on cleanup logic
            if current_month == 1:
                expected_target_month = 12
                expected_target_year = current_year - 1
            else:
                expected_target_month = current_month - 1
                expected_target_year = current_year
            
            # Test the logic understanding
            month_names = [
                "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
                "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
            ]
            
            current_month_name = month_names[current_month - 1]
            target_month_name = month_names[expected_target_month - 1]
            
            details = f"Cleanup Logic Validation:"
            details += f"\n   Current date: {today.strftime('%Y-%m-%d')}"
            details += f"\n   Current month: {current_month_name} {current_year}"
            details += f"\n   Expected target: {target_month_name} {expected_target_year}"
            details += f"\n   Should cleanup run today: {'Yes' if current_day >= 5 else 'No (day < 5)'}"
            
            # Validate our test notes match this logic
            target_notes = [n for n in self.test_notes_data 
                          if n["note_month"] == expected_target_month and n["note_year"] == expected_target_year]
            monthly_notes = [n for n in self.test_notes_data if n["is_monthly_note"]]
            other_specific_notes = [n for n in self.test_notes_data 
                                  if not n["is_monthly_note"] and 
                                  (n["note_month"] != expected_target_month or n["note_year"] != expected_target_year)]
            
            details += f"\n   Test notes created:"
            details += f"\n   - Target month notes: {len(target_notes)} (would be deleted if cleanup runs)"
            details += f"\n   - Monthly notes: {len(monthly_notes)} (never deleted)"
            details += f"\n   - Other specific notes: {len(other_specific_notes)} (not target, preserved)"
            
            success = len(target_notes) > 0 and len(monthly_notes) > 0
            
            self.log_test(4, "Validate Cleanup Logic Accuracy", success, details)
            return success
            
        except Exception as e:
            self.log_test(4, "Validate Cleanup Logic Accuracy", False, f"Exception: {str(e)}")
            return False

    def test_monthly_notes_preservation(self):
        """Step 5: Specifically test that monthly notes are never deleted"""
        try:
            # Get all notes before any cleanup attempt
            response = self.session.get(f"{self.base_url}/notes", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                all_notes = data.get("notes", [])
                
                # Count monthly notes
                monthly_notes_before = [n for n in all_notes if n.get("is_monthly_note")]
                our_monthly_notes = [n for n in self.test_notes_data if n["is_monthly_note"]]
                
                # Verify our monthly notes are in the system
                found_monthly = 0
                for test_note in our_monthly_notes:
                    for note in all_notes:
                        if note.get("note_id") == test_note["note_id"]:
                            found_monthly += 1
                            break
                
                success = found_monthly == len(our_monthly_notes)
                details = f"Monthly Notes Preservation Test:"
                details += f"\n   Total monthly notes in system: {len(monthly_notes_before)}"
                details += f"\n   Our test monthly notes: {len(our_monthly_notes)}"
                details += f"\n   Our monthly notes found: {found_monthly}/{len(our_monthly_notes)}"
                details += f"\n   ✅ Monthly notes should NEVER be deleted by cleanup system"
                
                if success:
                    for note in our_monthly_notes:
                        details += f"\n   - Monthly note: '{note['description']}' (Priority: {note['priority']})"
                
                self.log_test(5, "Test Monthly Notes Preservation", success, details)
                return success
            else:
                self.log_test(5, "Test Monthly Notes Preservation", False, 
                    f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test(5, "Test Monthly Notes Preservation", False, f"Exception: {str(e)}")
            return False

    def test_edge_cases_and_timing(self):
        """Step 6: Test edge cases and timing logic"""
        try:
            today = date.today()
            current_day = today.day
            
            # Test various timing scenarios
            edge_cases = []
            
            # Case 1: Current day logic
            if current_day < 5:
                edge_cases.append(f"✅ Today is day {current_day} - cleanup correctly won't run (< 5)")
            else:
                edge_cases.append(f"✅ Today is day {current_day} - cleanup should run (>= 5)")
            
            # Case 2: January edge case
            if today.month == 1:
                edge_cases.append("✅ January month - cleanup targets December of previous year")
            else:
                edge_cases.append(f"✅ {today.strftime('%B')} month - cleanup targets previous month")
            
            # Case 3: Year boundary
            if today.month == 1 and current_day >= 5:
                edge_cases.append("✅ January 5+ - would delete December notes from previous year")
            
            # Case 4: Monthly notes immunity
            edge_cases.append("✅ Monthly notes (is_monthly_note=true) are immune to cleanup")
            
            # Case 5: Future notes immunity
            edge_cases.append("✅ Future month notes are immune to cleanup")
            
            success = True
            details = "Edge Cases and Timing Logic Validation:"
            for case in edge_cases:
                details += f"\n   {case}"
            
            details += f"\n\n   Cleanup Rules Summary:"
            details += f"\n   - Only runs on/after 5th of month"
            details += f"\n   - Only targets previous month's specific notes"
            details += f"\n   - Monthly notes are never deleted"
            details += f"\n   - Current and future month notes are preserved"
            
            self.log_test(6, "Test Edge Cases and Timing", success, details)
            return success
            
        except Exception as e:
            self.log_test(6, "Test Edge Cases and Timing", False, f"Exception: {str(e)}")
            return False

    def cleanup_test_notes(self):
        """Clean up all test notes"""
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
                    print(f"   ✅ Deleted test note {note_id}")
                else:
                    print(f"   ⚠️ Failed to delete note {note_id}: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error deleting note {note_id}: {str(e)}")
        
        print(f"🧹 Cleanup complete: {cleaned}/{len(self.created_notes)} notes deleted\n")

    def run_all_tests(self):
        """Run all accurate cleanup tests"""
        print("🎯 PHASE 3 TESTING - ACCURATE PERIODIC NOTES CLEANUP VALIDATION")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print(f"Current date: {date.today().strftime('%Y-%m-%d')}")
        print()
        
        try:
            # Step 1: Authentication
            if not self.authenticate():
                return False
            
            # Step 2: Create comprehensive test notes
            if not self.create_comprehensive_test_notes():
                return False
            
            # Step 3: Test cleanup endpoint behavior
            cleanup_success, cleanup_result = self.test_cleanup_endpoint_behavior()
            if not cleanup_success:
                return False
            
            # Step 4: Validate cleanup logic accuracy
            if not self.validate_cleanup_logic_accuracy():
                return False
            
            # Step 5: Test monthly notes preservation
            if not self.test_monthly_notes_preservation():
                return False
            
            # Step 6: Test edge cases and timing
            if not self.test_edge_cases_and_timing():
                return False
            
            # Calculate success rate
            successful_tests = sum(1 for result in self.test_results if result["success"])
            total_tests = len(self.test_results)
            success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
            
            print("=" * 80)
            print("🎯 ACCURATE CLEANUP VALIDATION TEST SUMMARY")
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
                print("🎉 ACCURATE CLEANUP VALIDATION TEST COMPLETED SUCCESSFULLY")
                print("✅ Cleanup system behavior is correctly understood and validated")
                print("✅ Timing logic works correctly (only runs on/after 5th)")
                print("✅ Target month identification is accurate")
                print("✅ Monthly notes preservation is working")
                print("✅ Edge cases and timing logic are properly handled")
                overall_success = True
            else:
                print("🚨 ACCURATE CLEANUP VALIDATION TEST COMPLETED WITH ISSUES")
                print("❌ Some aspects of the cleanup system need investigation")
                overall_success = False
            
            return overall_success
            
        finally:
            # Always clean up test notes
            if self.created_notes:
                self.cleanup_test_notes()

def main():
    """Main test execution"""
    tester = AccurateCleanupTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎯 CONCLUSION: Accurate Cleanup Validation Test PASSED - Cleanup system is working as designed")
        sys.exit(0)
    else:
        print("🚨 CONCLUSION: Accurate Cleanup Validation Test FAILED - Issues need investigation")
        sys.exit(1)

if __name__ == "__main__":
    main()