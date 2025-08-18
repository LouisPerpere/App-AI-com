#!/usr/bin/env python3
# Database cleanup script to fix thumbnail issues
import os, sys
from database import get_database
from bson import ObjectId

def main():
    print("🔧 Starting database cleanup for thumbnail issues...")
    
    # Connect to database
    db = get_database()
    if not db.is_connected():
        print("❌ Database not connected!")
        sys.exit(1)
        
    print("✅ Database connected")
    
    # Get media collection
    media_collection = db.db.media
    user_id = "8aa0e7b1-5279-468b-bbce-028f7a70282d"
    
    # Get all files for this user
    files = list(media_collection.find({'owner_id': user_id}))
    print(f"📊 Found {len(files)} files in database")
    
    uploads_dir = "uploads"
    removed_count = 0
    fixed_count = 0
    processed_count = 0
    
    for file_doc in files:
        filename = file_doc.get('filename')
        file_id = file_doc['_id']
        thumb_url = file_doc.get('thumb_url')
        
        processed_count += 1
        
        # Check if physical file exists
        file_path = os.path.join(uploads_dir, filename)
        if not os.path.exists(file_path):
            print(f"❌ File missing from disk: {filename}")
            print(f"   Removing from database...")
            
            # Remove from database
            result = media_collection.delete_one({'_id': file_id})
            if result.deleted_count == 1:
                print(f"   ✅ Removed from database: {filename}")
                removed_count += 1
            else:
                print(f"   ❌ Failed to remove from database: {filename}")
            continue
        
        # Check for corrupted thumb_url (MongoDB expressions)
        if thumb_url and isinstance(thumb_url, (str, dict)):
            if isinstance(thumb_url, dict) or ('$replaceOne' in str(thumb_url)):
                print(f"🔧 Fixing corrupted thumb_url for: {filename}")
                print(f"   Current value: {str(thumb_url)[:100]}...")
                
                # Set thumb_url to None to trigger regeneration
                result = media_collection.update_one(
                    {'_id': file_id},
                    {'$set': {'thumb_url': None}}
                )
                
                if result.modified_count == 1:
                    print(f"   ✅ Fixed corrupted thumb_url: {filename}")
                    fixed_count += 1
                else:
                    print(f"   ❌ Failed to fix thumb_url: {filename}")
    
    print(f"\n🎉 Database cleanup complete!")
    print(f"   Processed: {processed_count} files")
    print(f"   Removed (missing from disk): {removed_count} files") 
    print(f"   Fixed (corrupted thumb_url): {fixed_count} files")
    print(f"   Remaining in database: {processed_count - removed_count} files")
    
    # Final verification
    remaining_files = media_collection.count_documents({'owner_id': user_id})
    print(f"\n📊 Final database count: {remaining_files} files")
    
    # Count how many need thumbnails
    need_thumbs = media_collection.count_documents({
        'owner_id': user_id,
        '$or': [
            {'thumb_url': None},
            {'thumb_url': ''},
            {'thumb_url': {'$exists': False}}
        ]
    })
    
    print(f"📊 Files needing thumbnails: {need_thumbs}")
    
    if need_thumbs > 0:
        print(f"\n🔄 Next step: Run thumbnail generation for {need_thumbs} files")
        print(f"   Use: POST /api/content/thumbnails/rebuild")
    
if __name__ == "__main__":
    main()