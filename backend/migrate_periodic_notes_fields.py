#!/usr/bin/env python3
"""
🔧 MIGRATION SCRIPT - PERIODIC NOTES FIELD NAMES CORRECTION

This script migrates existing ContentNote records from old field names to new field names:
- is_permanent → is_monthly_note  
- target_month → note_month
- target_year → note_year

This restores access to user data after the periodic notes system implementation.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# Load environment variables
from dotenv import load_dotenv
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def migrate_periodic_notes_fields():
    """Migrate ContentNote field names from old to new structure"""
    try:
        print("🔧 Starting ContentNote field migration...")
        print(f"⏰ Migration started at: {datetime.utcnow().isoformat()}")
        
        # Connect to MongoDB
        mongo_url = os.environ.get('MONGO_URL')
        if not mongo_url:
            print("❌ MONGO_URL not found in environment variables")
            return False
        
        print(f"🔗 Connecting to MongoDB...")
        client = AsyncIOMotorClient(mongo_url)
        
        # Use environment variable for database name, with fallback
        db_name = os.environ.get('DB_NAME', 'social_media_manager')
        db = client[db_name]
        
        print(f"📊 Using database: {db_name}")
        
        collection = db.content_notes
        
        # First, check what we're working with
        print("\n📋 PHASE 1: Analyzing existing data...")
        
        # Count total notes
        total_notes = await collection.count_documents({})
        print(f"📝 Total notes in database: {total_notes}")
        
        # Count notes with old field structure
        old_structure_count = await collection.count_documents({
            "$or": [
                {"is_permanent": {"$exists": True}},
                {"target_month": {"$exists": True}},
                {"target_year": {"$exists": True}}
            ]
        })
        
        print(f"🔄 Notes with old field structure: {old_structure_count}")
        
        # Count notes with new field structure
        new_structure_count = await collection.count_documents({
            "$or": [
                {"is_monthly_note": {"$exists": True}},
                {"note_month": {"$exists": True}},
                {"note_year": {"$exists": True}}
            ]
        })
        
        print(f"✅ Notes with new field structure: {new_structure_count}")
        
        if old_structure_count == 0:
            print("✅ No migration needed - all notes already use new field structure")
            return True
        
        print(f"\n🔧 PHASE 2: Migrating {old_structure_count} notes...")
        
        # Get all notes with old field structure
        old_notes = await collection.find({
            "$or": [
                {"is_permanent": {"$exists": True}},
                {"target_month": {"$exists": True}},
                {"target_year": {"$exists": True}}
            ]
        }).to_list(length=None)
        
        migrated_count = 0
        for note in old_notes:
            try:
                note_id = note.get('note_id', note.get('_id', 'unknown'))
                note_title = note.get('description', note.get('title', 'Sans titre'))
                
                # Prepare migration update
                update_operations = {"$set": {}, "$unset": {}}
                
                # Migrate is_permanent → is_monthly_note
                if 'is_permanent' in note:
                    update_operations["$set"]["is_monthly_note"] = note['is_permanent']
                    update_operations["$unset"]["is_permanent"] = 1
                    print(f"   🔄 {note_title}: is_permanent({note['is_permanent']}) → is_monthly_note")
                
                # Migrate target_month → note_month
                if 'target_month' in note:
                    update_operations["$set"]["note_month"] = note['target_month']
                    update_operations["$unset"]["target_month"] = 1
                    print(f"   🔄 {note_title}: target_month({note['target_month']}) → note_month")
                
                # Migrate target_year → note_year
                if 'target_year' in note:
                    update_operations["$set"]["note_year"] = note['target_year']
                    update_operations["$unset"]["target_year"] = 1
                    print(f"   🔄 {note_title}: target_year({note['target_year']}) → note_year")
                
                # Add migration metadata
                update_operations["$set"]["migrated_at"] = datetime.utcnow().isoformat()
                update_operations["$set"]["migration_version"] = "periodic_notes_fields_v1"
                
                # Perform the update
                if update_operations["$set"] or update_operations["$unset"]:
                    # Clean up empty operations
                    update_ops = {}
                    if update_operations["$set"]:
                        update_ops["$set"] = update_operations["$set"]
                    if update_operations["$unset"]:
                        update_ops["$unset"] = update_operations["$unset"]
                    
                    result = await collection.update_one(
                        {"_id": note["_id"]},
                        update_ops
                    )
                    
                    if result.modified_count > 0:
                        migrated_count += 1
                        print(f"   ✅ Migrated: {note_title}")
                    else:
                        print(f"   ⚠️  No changes for: {note_title}")
                
            except Exception as e:
                print(f"   ❌ Error migrating note {note_id}: {str(e)}")
        
        print(f"\n✅ PHASE 3: Migration completed!")
        print(f"   📊 Total notes processed: {len(old_notes)}")
        print(f"   ✅ Successfully migrated: {migrated_count}")
        print(f"   ❌ Failed migrations: {len(old_notes) - migrated_count}")
        
        # Verification phase
        print(f"\n🔍 PHASE 4: Verification...")
        
        # Check that old fields are gone
        remaining_old = await collection.count_documents({
            "$or": [
                {"is_permanent": {"$exists": True}},
                {"target_month": {"$exists": True}},
                {"target_year": {"$exists": True}}
            ]
        })
        
        # Check new field count
        final_new_count = await collection.count_documents({
            "$or": [
                {"is_monthly_note": {"$exists": True}},
                {"note_month": {"$exists": True}},
                {"note_year": {"$exists": True}}
            ]
        })
        
        print(f"   📊 Remaining old fields: {remaining_old}")
        print(f"   📊 Total with new fields: {final_new_count}")
        
        if remaining_old == 0:
            print("   ✅ All old fields successfully removed")
        else:
            print(f"   ⚠️  {remaining_old} notes still have old fields")
        
        # Sample verification - show a few migrated notes
        print(f"\n📋 SAMPLE VERIFICATION: Showing 3 migrated notes...")
        sample_notes = await collection.find({
            "migration_version": "periodic_notes_fields_v1"
        }).limit(3).to_list(length=3)
        
        for i, note in enumerate(sample_notes, 1):
            print(f"   {i}. {note.get('description', 'Sans titre')}")
            print(f"      - is_monthly_note: {note.get('is_monthly_note', 'None')}")
            print(f"      - note_month: {note.get('note_month', 'None')}")  
            print(f"      - note_year: {note.get('note_year', 'None')}")
            print(f"      - migrated_at: {note.get('migrated_at', 'None')}")
        
        print(f"\n🎉 Migration completed successfully!")
        print(f"⏰ Migration finished at: {datetime.utcnow().isoformat()}")
        
        await client.close()
        return True
        
    except Exception as e:
        print(f"❌ Critical error during migration: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main migration function"""
    print("=" * 60)
    print("🔧 CONTENTOTE FIELD MIGRATION SCRIPT")
    print("=" * 60)
    
    success = await migrate_periodic_notes_fields()
    
    if success:
        print("\n✅ MIGRATION SUCCESSFUL")
        print("🚀 The application should now have access to all note data")
        print("💡 Restart the backend service to apply changes")
        sys.exit(0)
    else:
        print("\n❌ MIGRATION FAILED")
        print("🔍 Check the error messages above for details")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())