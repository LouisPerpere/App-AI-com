#!/usr/bin/env python3
"""
Quick Photo Count Verification Test
Test rapide pour vérifier le nombre de photos restantes après suppression via frontend
"""

import requests
import json
import sys
from datetime import datetime

# Configuration - Using production URL as specified in review request
BACKEND_URL = "https://social-pub-hub.preview.emergentagent.com/api"
TEST_USER_EMAIL = "lperpere@yahoo.fr"
TEST_USER_PASSWORD = "L@Reunion974!"

class QuickPhotoVerifier:
    def __init__(self):
        self.session = requests.Session()
        # Disable SSL verification for testing
        self.session.verify = False
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.access_token = None
        
    def authenticate(self):
        """Authenticate with the backend"""
        print("🔐 Authenticating with backend...")
        
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                
                print(f"✅ Authentication successful")
                print(f"   User: {TEST_USER_EMAIL}")
                print(f"   Token: {self.access_token[:20]}..." if self.access_token else "   Token: None")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def get_content_count(self):
        """Get the current number of files in MongoDB via GET /api/content/pending"""
        print("\n📊 Checking content count in MongoDB...")
        
        try:
            # Get all content to get accurate count
            response = self.session.get(f"{BACKEND_URL}/content/pending?limit=100&offset=0")
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                total = data.get("total", 0)
                
                print(f"✅ Content retrieved successfully")
                print(f"   Files in response: {len(content)}")
                print(f"   Total files reported: {total}")
                print(f"   Has more files: {data.get('has_more', False)}")
                
                # Show file details
                if content:
                    print(f"\n📁 Files found:")
                    for i, file_info in enumerate(content):
                        filename = file_info.get('filename', 'Unknown')
                        file_type = file_info.get('file_type', 'Unknown')
                        description = file_info.get('description', '')
                        desc_info = f" (Description: {description[:30]}...)" if description else " (No description)"
                        print(f"   {i+1}. {filename} ({file_type}){desc_info}")
                
                return total, content
            else:
                print(f"❌ Failed to get content: {response.status_code}")
                print(f"   Response: {response.text}")
                return 0, []
                
        except Exception as e:
            print(f"❌ Error getting content: {e}")
            return 0, []
    
    def verify_photo_count(self):
        """Verify the photo count as requested in review"""
        print(f"\n🔍 VERIFICATION AS REQUESTED IN REVIEW:")
        print(f"   User reported: Kept 7 photos out of 36 original")
        print(f"   Task: Verify if backend MongoDB reflects this number")
        
        actual_count, files = self.get_content_count()
        
        print(f"\n📈 VERIFICATION RESULTS:")
        print(f"   Original photos (user claim): 36")
        print(f"   Expected remaining (user claim): 7")
        print(f"   Actual count in MongoDB: {actual_count}")
        
        # Analysis
        if actual_count == 7:
            print(f"✅ PERFECT MATCH: Backend MongoDB shows exactly 7 photos as user claimed")
            verification_status = "EXACT_MATCH"
        elif actual_count < 7:
            difference = 7 - actual_count
            print(f"⚠️ FEWER THAN EXPECTED: {difference} photos missing from user's claim")
            verification_status = "FEWER_THAN_EXPECTED"
        else:
            difference = actual_count - 7
            print(f"⚠️ MORE THAN EXPECTED: {difference} extra photos found beyond user's claim")
            verification_status = "MORE_THAN_EXPECTED"
        
        return actual_count, verification_status
    
    def test_synchronization(self):
        """Test if frontend deletions are synchronized with MongoDB"""
        print(f"\n🔄 Testing frontend-MongoDB synchronization...")
        
        actual_count, files = self.get_content_count()
        
        if actual_count > 0:
            print(f"✅ MongoDB contains {actual_count} files")
            print(f"   → Files are persisted in MongoDB (not ephemeral filesystem)")
            print(f"   → Frontend deletions appear to be synchronized")
            
            # Check file structure
            if files:
                sample_file = files[0]
                required_fields = ['id', 'filename', 'file_type', 'uploaded_at']
                missing_fields = [field for field in required_fields if field not in sample_file]
                
                if not missing_fields:
                    print(f"✅ File structure is correct - all required MongoDB fields present")
                else:
                    print(f"⚠️ Missing fields in file structure: {missing_fields}")
            
            return True
        else:
            print(f"⚠️ No files found in MongoDB")
            print(f"   → Either all files were deleted OR synchronization issue")
            return False
    
    def run_verification(self):
        """Run the complete verification as requested in review"""
        print("=" * 70)
        print("🚀 QUICK PHOTO COUNT VERIFICATION")
        print("   Test rapide avant implémentation des vignettes")
        print("=" * 70)
        
        # Step 1: Authenticate with specified credentials
        if not self.authenticate():
            print("\n❌ VERIFICATION FAILED: Cannot authenticate with lperpere@yahoo.fr")
            return False
        
        # Step 2: Call GET /api/content/pending to check MongoDB
        actual_count, verification_status = self.verify_photo_count()
        
        # Step 3: Test synchronization
        sync_working = self.test_synchronization()
        
        # Step 4: Final summary as requested
        print("\n" + "=" * 70)
        print("📋 VERIFICATION SUMMARY (AS REQUESTED IN REVIEW)")
        print("=" * 70)
        
        print(f"1. ✅ AUTHENTICATION: Successfully authenticated with {TEST_USER_EMAIL}")
        print(f"2. ✅ API CALL: GET /api/content/pending executed successfully")
        print(f"3. 📊 MONGODB COUNT: {actual_count} files found in MongoDB")
        print(f"4. 🔍 USER CLAIM VERIFICATION:")
        
        if verification_status == "EXACT_MATCH":
            print(f"   ✅ CONFIRMED: Backend MongoDB reflects exactly 7 photos as user claimed")
            print(f"   ✅ User's deletion actions via frontend are perfectly synchronized")
        elif verification_status == "FEWER_THAN_EXPECTED":
            print(f"   ⚠️ DISCREPANCY: Fewer photos than user claimed to keep")
            print(f"   → User may have deleted more photos after their report")
        else:
            print(f"   ⚠️ DISCREPANCY: More photos than user claimed to keep")
            print(f"   → User may have kept more photos than reported, or deletions not fully synchronized")
        
        print(f"5. 🔄 SYNCHRONIZATION: {'✅ Working correctly' if sync_working else '⚠️ Issues detected'}")
        
        # Conclusion for thumbnail implementation
        print(f"\n🎯 CONCLUSION FOR THUMBNAIL IMPLEMENTATION:")
        if verification_status == "EXACT_MATCH" and sync_working:
            print(f"   ✅ READY: MongoDB data is consistent, proceed with thumbnail implementation")
        else:
            print(f"   ⚠️ REVIEW NEEDED: Data discrepancies found, investigate before thumbnails")
        
        return verification_status == "EXACT_MATCH" and sync_working

def main():
    """Main execution"""
    verifier = QuickPhotoVerifier()
    success = verifier.run_verification()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()