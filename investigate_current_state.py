#!/usr/bin/env python3
"""
Investigation script to understand current state of the Bibliothèque
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://post-validator.preview.emergentagent.com/api"
TEST_USER_EMAIL = "lperpere@yahoo.fr"
TEST_USER_PASSWORD = "L@Reunion974!"

def authenticate():
    """Authenticate and get token"""
    session = requests.Session()
    session.verify = False
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    login_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        access_token = data.get("access_token")
        session.headers.update({"Authorization": f"Bearer {access_token}"})
        print(f"✅ Authenticated as {TEST_USER_EMAIL}")
        return session
    else:
        print(f"❌ Authentication failed: {response.status_code}")
        return None

def investigate_current_state():
    """Investigate current state"""
    session = authenticate()
    if not session:
        return
    
    print("\n🔍 INVESTIGATING CURRENT STATE")
    print("=" * 50)
    
    # Get current content
    response = session.get(f"{BACKEND_URL}/content/pending")
    
    if response.status_code == 200:
        data = response.json()
        content_files = data.get("content", [])
        total_files = data.get("total", len(content_files))
        
        print(f"📊 Current file count: {total_files}")
        print(f"📊 Files in response: {len(content_files)}")
        
        # Look for the specific file
        specific_file_id = "8ee21d73-914d-4a4e-8799-ced03e27ebe0"
        specific_file = None
        
        print(f"\n🔍 Looking for specific file: {specific_file_id}")
        
        files_with_descriptions = []
        all_file_ids = []
        
        for file_info in content_files:
            file_id = file_info.get("id", "")
            filename = file_info.get("filename", "")
            description = file_info.get("description", "")
            
            all_file_ids.append(file_id)
            
            if description and description.strip():
                files_with_descriptions.append({
                    "id": file_id,
                    "filename": filename,
                    "description": description
                })
            
            if file_id == specific_file_id:
                specific_file = file_info
        
        if specific_file:
            print(f"✅ Found specific file: {specific_file['filename']}")
            print(f"   Description: '{specific_file.get('description', '')}'")
        else:
            print(f"❌ Specific file {specific_file_id} not found")
            print(f"   Available file IDs (first 10): {all_file_ids[:10]}")
        
        print(f"\n📝 Files with descriptions ({len(files_with_descriptions)}):")
        for file_desc in files_with_descriptions:
            print(f"   - {file_desc['id']}: {file_desc['filename']} -> '{file_desc['description']}'")
        
        # Check if any file has "cadran bleu" comment
        cadran_bleu_files = []
        for file_info in content_files:
            description = file_info.get("description", "")
            if "cadran bleu" in description.lower():
                cadran_bleu_files.append({
                    "id": file_info.get("id"),
                    "filename": file_info.get("filename"),
                    "description": description
                })
        
        if cadran_bleu_files:
            print(f"\n🔵 Files with 'cadran bleu' comment ({len(cadran_bleu_files)}):")
            for file_info in cadran_bleu_files:
                print(f"   - {file_info['id']}: {file_info['filename']} -> '{file_info['description']}'")
        else:
            print(f"\n❌ No files found with 'cadran bleu' comment")
        
        # Get pagination info
        print(f"\n📄 Pagination info:")
        print(f"   - Total files: {total_files}")
        print(f"   - Files returned: {len(content_files)}")
        print(f"   - Has more: {data.get('has_more', False)}")
        
        # Test with higher limit to see all files
        print(f"\n🔍 Testing with limit=100 to see all files:")
        full_response = session.get(f"{BACKEND_URL}/content/pending?limit=100")
        
        if full_response.status_code == 200:
            full_data = full_response.json()
            full_content = full_data.get("content", [])
            full_total = full_data.get("total", len(full_content))
            
            print(f"   - Total files (limit=100): {full_total}")
            print(f"   - Files returned (limit=100): {len(full_content)}")
            
            # Look for specific file in full list
            specific_in_full = None
            cadran_bleu_in_full = []
            
            for file_info in full_content:
                file_id = file_info.get("id", "")
                description = file_info.get("description", "")
                
                if file_id == specific_file_id:
                    specific_in_full = file_info
                
                if "cadran bleu" in description.lower():
                    cadran_bleu_in_full.append({
                        "id": file_id,
                        "filename": file_info.get("filename"),
                        "description": description
                    })
            
            if specific_in_full:
                print(f"   ✅ Found specific file in full list: {specific_in_full['filename']}")
                print(f"      Description: '{specific_in_full.get('description', '')}'")
            else:
                print(f"   ❌ Specific file {specific_file_id} not found in full list either")
            
            if cadran_bleu_in_full:
                print(f"   🔵 Files with 'cadran bleu' in full list ({len(cadran_bleu_in_full)}):")
                for file_info in cadran_bleu_in_full:
                    print(f"      - {file_info['id']}: {file_info['filename']} -> '{file_info['description']}'")
            else:
                print(f"   ❌ No 'cadran bleu' files found in full list")
        
    else:
        print(f"❌ Failed to get content: {response.status_code}")

if __name__ == "__main__":
    investigate_current_state()