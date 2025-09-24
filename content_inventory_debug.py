#!/usr/bin/env python3
"""
CONTENT INVENTORY DEBUG TEST
Debug the content inventory preparation for post generation.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://instamanager-1.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

def test_content_inventory():
    """Test content inventory preparation"""
    session = requests.Session()
    
    # Authenticate
    auth_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
    response = session.post(f"{BACKEND_URL}/auth/login-robust", json=auth_data, timeout=30)
    
    if response.status_code != 200:
        print("❌ Authentication failed")
        return
    
    data = response.json()
    token = data.get("access_token")
    user_id = data.get("user_id")
    
    session.headers.update({
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })
    
    print(f"✅ Authenticated as user: {user_id}")
    
    # Get content from API
    response = session.get(f"{BACKEND_URL}/content/pending", timeout=30)
    if response.status_code != 200:
        print("❌ Failed to get content")
        return
    
    content_data = response.json()
    content_items = content_data.get("content", [])
    
    print(f"\n📂 CONTENT ANALYSIS:")
    print(f"   Total items: {len(content_items)}")
    
    # Check attributed_month field
    items_with_month = [item for item in content_items if item.get("attributed_month")]
    items_without_month = [item for item in content_items if not item.get("attributed_month")]
    
    print(f"   Items with attributed_month: {len(items_with_month)}")
    print(f"   Items without attributed_month: {len(items_without_month)}")
    
    # Show first few items with attributed_month details
    print(f"\n📋 ATTRIBUTED_MONTH ANALYSIS:")
    for i, item in enumerate(content_items[:5]):
        print(f"   {i+1}. ID: {item.get('id')}")
        print(f"      Filename: {item.get('filename')}")
        print(f"      Attributed month: {item.get('attributed_month', 'NOT SET')}")
        print(f"      Title: {item.get('title', 'No title')}")
        print(f"      Context: {item.get('context', 'No context')[:50]}...")
        print()
    
    # Check if any items have septembre_2025
    septembre_items = [item for item in content_items if item.get("attributed_month") == "septembre_2025"]
    print(f"   Items with attributed_month='septembre_2025': {len(septembre_items)}")
    
    if len(septembre_items) == 0:
        print("\n🔍 ROOT CAUSE IDENTIFIED:")
        print("   No content items have attributed_month='septembre_2025'")
        print("   This explains why the post generator finds 0 month_content items")
        print("   The generator first looks for month-specific content, finds none,")
        print("   then should fall back to all available content, but this fallback may not be working.")

if __name__ == "__main__":
    test_content_inventory()