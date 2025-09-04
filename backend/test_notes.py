#!/usr/bin/env python3
"""
Test script to verify the note creation with new fields works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_database

def test_note_creation():
    """Test creating a note with the new fields"""
    print("🧪 Testing note creation with new fields...")
    
    # Get database instance
    db = get_database()
    
    if not db.is_connected():
        print("❌ Database not connected")
        return False
    
    # Test user ID
    test_user_id = "test_user_123"
    
    try:
        # Create a note with all new fields
        note = db.create_note(
            user_id=test_user_id,
            content="Test note content",
            description="Test note description",
            priority="high",
            is_permanent=True,
            target_month=12,
            target_year=2024
        )
        
        print("✅ Note created successfully!")
        print(f"   Note ID: {note['note_id']}")
        print(f"   Owner ID: {note['owner_id']}")
        print(f"   Description: {note['description']}")
        print(f"   Content: {note['content']}")
        print(f"   Priority: {note['priority']}")
        print(f"   Is Permanent: {note['is_permanent']}")
        print(f"   Target Month: {note['target_month']}")
        print(f"   Target Year: {note['target_year']}")
        print(f"   Created At: {note['created_at']}")
        print(f"   Updated At: {note['updated_at']}")
        
        # Verify the note was saved correctly
        notes = db.get_notes(test_user_id)
        if notes and len(notes) > 0:
            saved_note = notes[0]
            print("✅ Note retrieved successfully!")
            print(f"   Retrieved note has all fields: {all(field in saved_note for field in ['is_permanent', 'target_month', 'target_year'])}")
        else:
            print("❌ Failed to retrieve saved note")
            return False
        
        # Clean up - delete the test note
        db.delete_note(test_user_id, note['note_id'])
        print("✅ Test note cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    success = test_note_creation()
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Tests failed!")
        sys.exit(1)