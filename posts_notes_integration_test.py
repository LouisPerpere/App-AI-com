#!/usr/bin/env python3
"""
Backend Testing for Posts Generation System - Notes Integration Focus
Testing the posts generation system specifically for notes integration verification.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://claire-marcus-app-1.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class PostsNotesIntegrationTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        
    def authenticate(self):
        """Authenticate with the backend"""
        print("🔐 Step 1: Authenticating...")
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login-robust", 
                json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
                timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                print(f"   ✅ Authentication successful")
                print(f"   👤 User ID: {self.user_id}")
                return True
            else:
                print(f"   ❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {str(e)}")
            return False
    
    def cleanup_existing_notes(self):
        """Clean up existing test notes"""
        print("\n🧹 Step 2: Cleaning up existing test notes...")
        
        try:
            # Get existing notes
            response = self.session.get(f"{BACKEND_URL}/notes", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                existing_notes = data.get("notes", [])
                
                print(f"   📋 Found {len(existing_notes)} existing notes")
                
                # Delete test notes (those containing "fermeture du 30" or "test")
                deleted_count = 0
                for note in existing_notes:
                    note_content = note.get("content", "").lower()
                    note_description = note.get("description", "").lower()
                    
                    if ("fermeture du 30" in note_content or "test" in note_content or 
                        "fermeture du 30" in note_description or "test" in note_description):
                        
                        note_id = note.get("note_id")
                        if note_id:
                            delete_response = self.session.delete(f"{BACKEND_URL}/notes/{note_id}", timeout=30)
                            if delete_response.status_code == 200:
                                deleted_count += 1
                                print(f"   🗑️ Deleted test note: {note.get('description', 'No description')}")
                
                print(f"   ✅ Cleaned up {deleted_count} test notes")
                return True
            else:
                print(f"   ❌ Failed to get existing notes: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Cleanup error: {str(e)}")
            return False
    
    def create_test_notes(self):
        """Create test notes for integration testing"""
        print("\n📝 Step 3: Creating test notes...")
        
        test_notes = [
            {
                "description": "Fermeture exceptionnelle",
                "content": "Attention, fermeture exceptionnelle du magasin le 30 septembre pour inventaire. Nous serons fermés toute la journée. Réouverture le 1er octobre à 9h00.",
                "priority": "high",
                "is_monthly_note": False,
                "note_month": 9,  # September
                "note_year": 2025
            },
            {
                "description": "Informations générales boutique",
                "content": "Notre boutique propose des montres artisanales uniques, fabriquées à la main avec des matériaux de qualité. Chaque pièce est unique et personnalisable.",
                "priority": "normal",
                "is_monthly_note": True,  # Always valid note
                "note_month": None,
                "note_year": None
            },
            {
                "description": "Promotion septembre",
                "content": "Profitez de notre promotion spéciale septembre : -20% sur toutes les montres en cuir. Offre valable jusqu'au 30 septembre.",
                "priority": "medium",
                "is_monthly_note": False,
                "note_month": 9,  # September
                "note_year": 2025
            }
        ]
        
        created_notes = []
        
        for note_data in test_notes:
            try:
                response = self.session.post(f"{BACKEND_URL}/notes", 
                    json=note_data, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    created_note = data.get("note")
                    created_notes.append(created_note)
                    
                    print(f"   ✅ Created note: {note_data['description']}")
                    print(f"      📋 Content: {note_data['content'][:50]}...")
                    print(f"      🎯 Priority: {note_data['priority']}")
                    print(f"      📅 Monthly: {note_data['is_monthly_note']}")
                    
                else:
                    print(f"   ❌ Failed to create note '{note_data['description']}': {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error creating note '{note_data['description']}': {str(e)}")
        
        print(f"   ✅ Successfully created {len(created_notes)} test notes")
        return created_notes
    
    def verify_notes_retrieval(self):
        """Verify that notes are properly retrieved from database"""
        print("\n🔍 Step 4: Verifying notes retrieval...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/notes", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                notes = data.get("notes", [])
                
                print(f"   📋 Total notes retrieved: {len(notes)}")
                
                # Categorize notes
                monthly_notes = [n for n in notes if n.get("is_monthly_note", False)]
                september_notes = [n for n in notes if n.get("note_month") == 9 and n.get("note_year") == 2025]
                closure_notes = [n for n in notes if "fermeture du 30" in n.get("content", "").lower()]
                
                print(f"   📅 Monthly notes (always valid): {len(monthly_notes)}")
                print(f"   🗓️ September 2025 specific notes: {len(september_notes)}")
                print(f"   🚪 Closure notes found: {len(closure_notes)}")
                
                # Verify closure note content
                if closure_notes:
                    closure_note = closure_notes[0]
                    print(f"   🔍 Closure note content: {closure_note.get('content', '')}")
                    
                    # Check for key closure information
                    content = closure_note.get('content', '').lower()
                    has_closure_info = any(keyword in content for keyword in [
                        'fermeture', 'fermé', '30 septembre', 'inventaire'
                    ])
                    
                    if has_closure_info:
                        print(f"   ✅ Closure note contains required information")
                    else:
                        print(f"   ❌ Closure note missing key information")
                
                return len(notes) > 0 and len(closure_notes) > 0
            else:
                print(f"   ❌ Failed to retrieve notes: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Notes retrieval error: {str(e)}")
            return False
    
    def generate_posts_for_current_month(self):
        """Generate posts for the current month (September 2025)"""
        print("\n🚀 Step 5: Generating posts for September 2025...")
        
        try:
            # Use September 2025 as target month to match our test notes
            target_month = "septembre_2025"
            
            print(f"   📅 Target month: {target_month}")
            print(f"   ⏱️ Starting post generation...")
            
            start_time = time.time()
            
            response = self.session.post(f"{BACKEND_URL}/posts/generate", 
                params={"target_month": target_month}, 
                timeout=120)  # Increased timeout for AI processing
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"   ✅ Post generation completed in {generation_time:.2f} seconds")
                print(f"   📊 Success: {data.get('success', False)}")
                print(f"   📝 Posts generated: {data.get('posts_count', 0)}")
                print(f"   🎯 Strategy: {data.get('strategy', {})}")
                
                sources_used = data.get('sources_used', {})
                print(f"   📋 Sources used:")
                print(f"      - Business profile: {sources_used.get('business_profile', False)}")
                print(f"      - Website analysis: {sources_used.get('website_analysis', False)}")
                print(f"      - Always valid notes: {sources_used.get('always_valid_notes', 0)}")
                print(f"      - Month notes: {sources_used.get('month_notes', 0)}")
                
                return data.get('success', False) and data.get('posts_count', 0) > 0
            else:
                print(f"   ❌ Post generation failed: {response.status_code}")
                print(f"   📄 Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Post generation error: {str(e)}")
            return False
    
    def verify_generated_posts_integration(self):
        """Verify that generated posts actually integrate note information"""
        print("\n🔍 Step 6: Verifying posts integration with notes...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/posts/generated", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                
                print(f"   📋 Total generated posts: {len(posts)}")
                
                if not posts:
                    print(f"   ❌ No posts found to analyze")
                    return False
                
                # Analyze posts for note integration
                closure_keywords = ['fermeture', 'fermé', '30 septembre', 'inventaire', 'réouverture']
                general_keywords = ['montre', 'artisanal', 'unique', 'qualité', 'personnalisable']
                promotion_keywords = ['promotion', '-20%', 'cuir', 'offre', 'septembre']
                
                posts_with_closure_info = []
                posts_with_general_info = []
                posts_with_promotion_info = []
                
                for i, post in enumerate(posts):
                    post_text = post.get('text', '').lower()
                    post_title = post.get('title', '').lower()
                    combined_text = f"{post_title} {post_text}"
                    
                    print(f"\n   📝 Post {i+1}:")
                    print(f"      Title: {post.get('title', 'No title')}")
                    print(f"      Text: {post.get('text', 'No text')[:100]}...")
                    print(f"      Hashtags: {len(post.get('hashtags', []))} hashtags")
                    
                    # Check for closure information
                    closure_matches = [kw for kw in closure_keywords if kw in combined_text]
                    if closure_matches:
                        posts_with_closure_info.append(post)
                        print(f"      🚪 Contains closure info: {closure_matches}")
                    
                    # Check for general business information
                    general_matches = [kw for kw in general_keywords if kw in combined_text]
                    if general_matches:
                        posts_with_general_info.append(post)
                        print(f"      🏪 Contains general info: {general_matches}")
                    
                    # Check for promotion information
                    promotion_matches = [kw for kw in promotion_keywords if kw in combined_text]
                    if promotion_matches:
                        posts_with_promotion_info.append(post)
                        print(f"      🎁 Contains promotion info: {promotion_matches}")
                
                print(f"\n   📊 Integration Analysis:")
                print(f"      🚪 Posts with closure information: {len(posts_with_closure_info)}")
                print(f"      🏪 Posts with general business info: {len(posts_with_general_info)}")
                print(f"      🎁 Posts with promotion info: {len(posts_with_promotion_info)}")
                
                # Verify critical closure information is integrated
                has_closure_integration = len(posts_with_closure_info) > 0
                has_general_integration = len(posts_with_general_info) > 0
                
                if has_closure_integration:
                    print(f"   ✅ CRITICAL: Closure information properly integrated into posts")
                else:
                    print(f"   ❌ CRITICAL: Closure information NOT integrated into posts")
                
                if has_general_integration:
                    print(f"   ✅ General business information integrated")
                else:
                    print(f"   ⚠️ General business information not well integrated")
                
                return has_closure_integration
            else:
                print(f"   ❌ Failed to retrieve generated posts: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Posts verification error: {str(e)}")
            return False
    
    def check_backend_logs_for_notes_processing(self):
        """Check if we can verify notes processing in logs (limited in this environment)"""
        print("\n📋 Step 7: Checking notes processing indicators...")
        
        # Since we can't access backend logs directly, we'll verify through API responses
        try:
            # Re-verify notes are available
            response = self.session.get(f"{BACKEND_URL}/notes", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                notes = data.get("notes", [])
                
                # Check if we have the expected test notes
                closure_notes = [n for n in notes if "fermeture du 30" in n.get("content", "").lower()]
                monthly_notes = [n for n in notes if n.get("is_monthly_note", False)]
                september_notes = [n for n in notes if n.get("note_month") == 9]
                
                print(f"   📋 Notes available for processing:")
                print(f"      🚪 Closure notes: {len(closure_notes)}")
                print(f"      📅 Monthly notes: {len(monthly_notes)}")
                print(f"      🗓️ September notes: {len(september_notes)}")
                
                # Verify note structure for AI processing
                if closure_notes:
                    closure_note = closure_notes[0]
                    print(f"   🔍 Closure note structure:")
                    print(f"      - Description: {closure_note.get('description', 'Missing')}")
                    print(f"      - Content: {closure_note.get('content', 'Missing')[:50]}...")
                    print(f"      - Priority: {closure_note.get('priority', 'Missing')}")
                    
                    # Check if note has proper fields for AI processing
                    has_description = bool(closure_note.get('description'))
                    has_content = bool(closure_note.get('content'))
                    
                    if has_description and has_content:
                        print(f"   ✅ Note structure suitable for AI processing")
                    else:
                        print(f"   ❌ Note structure missing required fields")
                
                return len(notes) > 0
            else:
                print(f"   ❌ Failed to check notes: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Notes processing check error: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run the complete posts generation notes integration test"""
        print("🎯 POSTS GENERATION SYSTEM - NOTES INTEGRATION TESTING")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test credentials: {TEST_EMAIL}")
        print(f"Focus: Notes integration in post generation")
        print("=" * 70)
        
        test_results = {
            "authentication": False,
            "notes_cleanup": False,
            "notes_creation": False,
            "notes_retrieval": False,
            "posts_generation": False,
            "posts_integration": False,
            "notes_processing": False
        }
        
        # Step 1: Authentication
        if self.authenticate():
            test_results["authentication"] = True
        else:
            print("\n❌ CRITICAL: Authentication failed - cannot proceed")
            return test_results
        
        # Step 2: Cleanup existing test notes
        if self.cleanup_existing_notes():
            test_results["notes_cleanup"] = True
        
        # Step 3: Create test notes
        created_notes = self.create_test_notes()
        if created_notes:
            test_results["notes_creation"] = True
        
        # Step 4: Verify notes retrieval
        if self.verify_notes_retrieval():
            test_results["notes_retrieval"] = True
        
        # Step 5: Generate posts
        if self.generate_posts_for_current_month():
            test_results["posts_generation"] = True
        
        # Step 6: Verify posts integration
        if self.verify_generated_posts_integration():
            test_results["posts_integration"] = True
        
        # Step 7: Check notes processing
        if self.check_backend_logs_for_notes_processing():
            test_results["notes_processing"] = True
        
        # Final results
        print("\n" + "=" * 70)
        print("🎯 FINAL TEST RESULTS")
        print("=" * 70)
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name.replace('_', ' ').title()}")
        
        print(f"\n📊 Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        # Critical assessment
        critical_tests = ["notes_retrieval", "posts_generation", "posts_integration"]
        critical_passed = sum(test_results[test] for test in critical_tests)
        
        if critical_passed == len(critical_tests):
            print("🎉 CRITICAL SUCCESS: Notes integration is working correctly!")
        else:
            print("🚨 CRITICAL FAILURE: Notes integration has issues!")
        
        return test_results

def main():
    """Main test execution"""
    tester = PostsNotesIntegrationTester()
    results = tester.run_comprehensive_test()
    
    # Return appropriate exit code
    critical_tests = ["notes_retrieval", "posts_generation", "posts_integration"]
    critical_passed = sum(results[test] for test in critical_tests)
    
    if critical_passed == len(critical_tests):
        exit(0)  # Success
    else:
        exit(1)  # Failure

if __name__ == "__main__":
    main()