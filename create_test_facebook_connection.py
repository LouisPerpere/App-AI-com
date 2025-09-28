#!/usr/bin/env python3
"""
Create a test Facebook connection with temporary token to simulate the issue
"""

import requests
import json
from datetime import datetime
import time

def create_test_facebook_connection():
    """Create a test Facebook connection with temporary token"""
    
    base_url = "https://social-ai-planner-2.preview.emergentagent.com/api"
    credentials = {
        "email": "lperpere@yahoo.fr",
        "password": "L@Reunion974!"
    }
    
    # Authenticate
    session = requests.Session()
    response = session.post(
        f"{base_url}/auth/login-robust",
        json=credentials,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print(f"❌ Authentication failed: {response.text}")
        return False
    
    data = response.json()
    token = data.get("access_token")
    user_id = data.get("user_id")
    
    session.headers.update({
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })
    
    print(f"✅ Authenticated as user: {user_id}")
    
    # Create a test Facebook connection directly via MongoDB
    from pymongo import MongoClient
    import os
    
    # Connect to MongoDB
    mongo_url = "mongodb://localhost:27017/claire_marcus"
    client = MongoClient(mongo_url)
    db = client.claire_marcus
    
    # Create test Facebook connection with temporary token
    timestamp = int(time.time())
    test_connection = {
        "user_id": user_id,
        "platform": "facebook",
        "access_token": f"temp_facebook_token_{timestamp}",
        "page_id": "test_page_123",
        "page_name": "My Test Page",
        "active": True,
        "created_at": datetime.utcnow().isoformat(),
        "connected_at": datetime.utcnow().isoformat()
    }
    
    # Insert into social_media_connections collection
    result = db.social_media_connections.insert_one(test_connection)
    
    print(f"✅ Created test Facebook connection with ID: {result.inserted_id}")
    print(f"   Token: {test_connection['access_token']}")
    print(f"   Page: {test_connection['page_name']}")
    print(f"   Active: {test_connection['active']}")
    
    return True

if __name__ == "__main__":
    create_test_facebook_connection()