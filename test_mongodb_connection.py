#!/usr/bin/env python3
"""
Test MongoDB connection for Claire et Marcus
"""

import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import sys

def test_mongodb_connection(mongo_url, db_name):
    """Test MongoDB connection"""
    print(f"🔍 Testing MongoDB connection...")
    print(f"Database: {db_name}")
    print(f"URL: {mongo_url[:50]}...{mongo_url[-20:] if len(mongo_url) > 70 else mongo_url}")
    
    try:
        # Create client
        client = MongoClient(mongo_url)
        
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # Get database
        db = client[db_name]
        
        # Test database operations
        test_collection = db.test_connection
        
        # Insert test document
        test_doc = {"test": "connection", "timestamp": "2025-08-07"}
        result = test_collection.insert_one(test_doc)
        print(f"✅ Test document inserted: {result.inserted_id}")
        
        # Read test document
        found_doc = test_collection.find_one({"_id": result.inserted_id})
        print(f"✅ Test document found: {found_doc['test']}")
        
        # Clean up test document
        test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Test document cleaned up")
        
        # List collections (should be empty initially)
        collections = db.list_collection_names()
        print(f"📋 Collections in database: {collections}")
        
        print("\n🎉 MongoDB setup is working perfectly!")
        print("Ready to use with Claire et Marcus backend!")
        
        client.close()
        return True
        
    except ConnectionFailure as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during MongoDB test: {e}")
        return False

if __name__ == "__main__":
    # You'll need to provide these values
    mongo_url = input("Enter your MongoDB URL: ").strip()
    db_name = input("Enter database name (default: claire_marcus): ").strip() or "claire_marcus"
    
    success = test_mongodb_connection(mongo_url, db_name)
    sys.exit(0 if success else 1)