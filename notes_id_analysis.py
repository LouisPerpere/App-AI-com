#!/usr/bin/env python3
"""
Notes API ID Field Analysis
Examining the structure of notes to identify ID fields (note_id, id, _id)
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://post-validator.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}

class NotesIDAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        
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
            
    def create_sample_notes(self):
        """Create sample notes with different priorities"""
        self.log("🔍 Creating sample notes for analysis...")
        
        sample_notes = [
            {"title": "Note Priorité High", "content": "Contenu priorité élevée", "priority": "high"},
            {"title": "Note Priorité Low", "content": "Contenu priorité faible", "priority": "low"},
            {"title": "Note Priorité Normal", "content": "Contenu priorité normale", "priority": "normal"}
        ]
        
        created_notes = []
        
        for note_data in sample_notes:
            try:
                response = self.session.post(
                    f"{BACKEND_URL}/notes",
                    json=note_data,
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    note = data.get("note", {})
                    created_notes.append(note)
                    self.log(f"✅ Created note: {note_data['title']} (Priority: {note_data['priority']})")
                else:
                    self.log(f"❌ Failed to create note: {response.status_code}")
            except Exception as e:
                self.log(f"❌ Create note error: {e}")
                
        return created_notes
        
    def analyze_note_structure(self):
        """Analyze the structure of notes returned by GET /api/notes"""
        self.log("🔍 Analyzing note structure from GET /api/notes...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/notes", timeout=10)
            if response.status_code == 200:
                data = response.json()
                notes = data.get("notes", [])
                
                self.log(f"✅ Retrieved {len(notes)} notes for analysis")
                self.log("\n" + "="*60)
                self.log("DETAILED NOTE STRUCTURE ANALYSIS")
                self.log("="*60)
                
                for i, note in enumerate(notes[:5], 1):  # Analyze first 5 notes
                    self.log(f"\n--- Note {i} Structure ---")
                    
                    # Check for different ID fields
                    id_fields = []
                    if "note_id" in note:
                        id_fields.append(f"note_id: {note['note_id']}")
                    if "id" in note:
                        id_fields.append(f"id: {note['id']}")
                    if "_id" in note:
                        id_fields.append(f"_id: {note['_id']}")
                    
                    self.log(f"ID Fields Found: {', '.join(id_fields) if id_fields else 'None'}")
                    
                    # Show all fields
                    self.log("All Fields:")
                    for key, value in note.items():
                        if isinstance(value, str) and len(value) > 50:
                            value = value[:50] + "..."
                        self.log(f"  {key}: {value}")
                        
                    # Priority analysis
                    priority = note.get("priority", "NOT_SET")
                    self.log(f"Priority Value: '{priority}'")
                    
                self.log("\n" + "="*60)
                self.log("ID FIELD SUMMARY")
                self.log("="*60)
                
                # Summarize ID field usage
                note_id_count = sum(1 for note in notes if "note_id" in note)
                id_count = sum(1 for note in notes if "id" in note)
                _id_count = sum(1 for note in notes if "_id" in note)
                
                self.log(f"Notes with 'note_id' field: {note_id_count}/{len(notes)}")
                self.log(f"Notes with 'id' field: {id_count}/{len(notes)}")
                self.log(f"Notes with '_id' field: {_id_count}/{len(notes)}")
                
                # Priority analysis
                priority_counts = {}
                for note in notes:
                    priority = note.get("priority", "NOT_SET")
                    priority_counts[priority] = priority_counts.get(priority, 0) + 1
                
                self.log("\nPRIORITY DISTRIBUTION:")
                for priority, count in priority_counts.items():
                    self.log(f"  {priority}: {count} notes")
                
                # Recommend ID field to use
                if note_id_count == len(notes):
                    self.log("\n✅ RECOMMENDATION: Use 'note_id' field for DELETE/PUT operations")
                elif id_count == len(notes):
                    self.log("\n✅ RECOMMENDATION: Use 'id' field for DELETE/PUT operations")
                elif _id_count == len(notes):
                    self.log("\n✅ RECOMMENDATION: Use '_id' field for DELETE/PUT operations")
                else:
                    self.log("\n⚠️ WARNING: Inconsistent ID field usage across notes")
                
                return True
            else:
                self.log(f"❌ Failed to get notes: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Analysis error: {e}")
            return False
            
    def test_id_field_usage(self):
        """Test which ID field works for DELETE operations"""
        self.log("\n🔍 Testing ID field usage for DELETE operations...")
        
        # Create a test note
        test_note = {
            "title": "Test ID Field Usage",
            "content": "This note will test ID field usage",
            "priority": "normal"
        }
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/notes",
                json=test_note,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                created_note = data.get("note", {})
                
                # Extract different ID fields
                note_id = created_note.get("note_id")
                id_field = created_note.get("id")
                _id_field = created_note.get("_id")
                
                self.log(f"Created test note with:")
                if note_id:
                    self.log(f"  note_id: {note_id}")
                if id_field:
                    self.log(f"  id: {id_field}")
                if _id_field:
                    self.log(f"  _id: {_id_field}")
                
                # Test which ID field works for DELETE
                test_ids = []
                if note_id:
                    test_ids.append(("note_id", note_id))
                if id_field:
                    test_ids.append(("id", id_field))
                if _id_field:
                    test_ids.append(("_id", _id_field))
                
                for field_name, field_value in test_ids:
                    self.log(f"\n🔍 Testing DELETE with {field_name}: {field_value}")
                    try:
                        delete_response = self.session.delete(
                            f"{BACKEND_URL}/notes/{field_value}",
                            timeout=10
                        )
                        if delete_response.status_code == 200:
                            self.log(f"✅ DELETE successful with {field_name}")
                            return True
                        elif delete_response.status_code == 404:
                            self.log(f"❌ DELETE failed with {field_name} - 404 Not Found")
                        else:
                            self.log(f"❌ DELETE failed with {field_name} - Status: {delete_response.status_code}")
                    except Exception as e:
                        self.log(f"❌ DELETE error with {field_name}: {e}")
                
                return False
            else:
                self.log(f"❌ Failed to create test note: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Test ID field error: {e}")
            return False
            
    def cleanup_test_notes(self):
        """Clean up any test notes created during analysis"""
        self.log("\n🧹 Cleaning up test notes...")
        try:
            response = self.session.get(f"{BACKEND_URL}/notes", timeout=10)
            if response.status_code == 200:
                data = response.json()
                notes = data.get("notes", [])
                
                cleanup_count = 0
                for note in notes:
                    title = note.get("title", "")
                    if "Test" in title or "Note Priorité" in title:
                        note_id = note.get("note_id")
                        if note_id:
                            try:
                                delete_response = self.session.delete(
                                    f"{BACKEND_URL}/notes/{note_id}",
                                    timeout=5
                                )
                                if delete_response.status_code == 200:
                                    cleanup_count += 1
                            except:
                                pass
                
                self.log(f"✅ Cleaned up {cleanup_count} test notes")
        except Exception as e:
            self.log(f"⚠️ Cleanup error: {e}")
            
    def run_analysis(self):
        """Run the complete ID field analysis"""
        self.log("🚀 Starting Notes API ID Field Analysis")
        self.log(f"Backend URL: {BACKEND_URL}")
        self.log(f"Test User: {TEST_CREDENTIALS['email']}")
        
        if not self.authenticate():
            return False
            
        # Create sample notes
        self.create_sample_notes()
        
        # Analyze structure
        structure_success = self.analyze_note_structure()
        
        # Test ID field usage
        id_test_success = self.test_id_field_usage()
        
        # Cleanup
        self.cleanup_test_notes()
        
        self.log(f"\n{'='*50}")
        self.log(f"ID FIELD ANALYSIS SUMMARY")
        self.log(f"{'='*50}")
        
        if structure_success and id_test_success:
            self.log("🎉 ANALYSIS COMPLETED SUCCESSFULLY")
            return True
        else:
            self.log("⚠️ ANALYSIS COMPLETED WITH ISSUES")
            return False

if __name__ == "__main__":
    analyzer = NotesIDAnalyzer()
    success = analyzer.run_analysis()
    sys.exit(0 if success else 1)