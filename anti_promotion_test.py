#!/usr/bin/env python3
"""
Backend Testing for Posts Generation System - Anti-Promotion Verification
Testing that AI no longer creates unsolicited promotions or discounts.
"""

import requests
import json
import time
import re
from datetime import datetime
from typing import Dict, List, Any

# Configuration
BACKEND_URL = "https://social-ai-planner-2.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️ {message}{Colors.END}")

def print_header(message):
    print(f"\n{Colors.BOLD}{Colors.PURPLE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}{message}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}{'='*60}{Colors.END}")

def authenticate() -> tuple:
    """Authenticate and return token and user_id"""
    print_header("AUTHENTICATION")
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login-robust", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_id = data.get("user_id")
            print_success(f"Authentication successful")
            print_info(f"User ID: {user_id}")
            return token, user_id
        else:
            print_error(f"Authentication failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None, None
            
    except Exception as e:
        print_error(f"Authentication error: {str(e)}")
        return None, None

def clear_existing_posts(token: str, user_id: str) -> bool:
    """Clear existing generated posts to start fresh"""
    print_header("CLEARING EXISTING POSTS")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.delete(f"{BACKEND_URL}/posts/generated/all", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            deleted_count = data.get("deleted_posts", 0)
            print_success(f"Cleared {deleted_count} existing posts")
            return True
        else:
            print_warning(f"Failed to clear posts: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error clearing posts: {str(e)}")
        return False

def clear_existing_notes(token: str, user_id: str) -> bool:
    """Clear existing notes to start with clean slate"""
    print_header("CLEARING EXISTING NOTES")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get existing notes
        response = requests.get(f"{BACKEND_URL}/notes", headers=headers)
        if response.status_code == 200:
            data = response.json()
            notes = data.get("notes", [])
            
            # Delete each note
            deleted_count = 0
            for note in notes:
                note_id = note.get("note_id")
                if note_id:
                    delete_response = requests.delete(f"{BACKEND_URL}/notes/{note_id}", headers=headers)
                    if delete_response.status_code == 200:
                        deleted_count += 1
            
            print_success(f"Cleared {deleted_count} existing notes")
            return True
        else:
            print_warning(f"Failed to get notes for clearing: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error clearing notes: {str(e)}")
        return False

def create_test_note_without_promotion(token: str, user_id: str) -> bool:
    """Create a test note WITHOUT any promotional content"""
    print_header("CREATING TEST NOTE WITHOUT PROMOTION")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a note with general business information, no promotions
        note_data = {
            "description": "Informations générales business",
            "content": "Notre atelier d'horlogerie se spécialise dans la réparation et la restauration de montres anciennes. Nous travaillons avec passion sur chaque pièce pour lui redonner vie. Notre expertise couvre les montres mécaniques, automatiques et à quartz.",
            "priority": "high",
            "is_monthly_note": True
        }
        
        response = requests.post(f"{BACKEND_URL}/notes", headers=headers, json=note_data)
        
        if response.status_code == 200:
            data = response.json()
            note_id = data.get("note", {}).get("note_id")
            print_success(f"Created test note without promotion: {note_id}")
            print_info(f"Note content: {note_data['content'][:100]}...")
            return True
        else:
            print_error(f"Failed to create note: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error creating note: {str(e)}")
        return False

def generate_posts_without_promotion(token: str, user_id: str) -> List[Dict]:
    """Generate posts without any promotional notes"""
    print_header("GENERATING POSTS WITHOUT PROMOTIONAL NOTES")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Generate posts for current month
        response = requests.post(f"{BACKEND_URL}/posts/generate", 
                               headers=headers,
                               params={"target_month": "septembre_2025"})
        
        if response.status_code == 200:
            data = response.json()
            posts_count = data.get("posts_count", 0)
            print_success(f"Generated {posts_count} posts successfully")
            
            # Get the generated posts
            posts_response = requests.get(f"{BACKEND_URL}/posts/generated", headers=headers)
            if posts_response.status_code == 200:
                posts_data = posts_response.json()
                posts = posts_data.get("posts", [])
                print_success(f"Retrieved {len(posts)} generated posts")
                return posts
            else:
                print_error(f"Failed to retrieve posts: {posts_response.status_code}")
                return []
        else:
            print_error(f"Failed to generate posts: {response.status_code}")
            print_error(f"Response: {response.text}")
            return []
            
    except Exception as e:
        print_error(f"Error generating posts: {str(e)}")
        return []

def analyze_posts_for_promotions(posts: List[Dict]) -> Dict[str, Any]:
    """Analyze posts for unsolicited promotional content"""
    print_header("ANALYZING POSTS FOR UNSOLICITED PROMOTIONS")
    
    # Promotional patterns to detect
    promotion_patterns = [
        # Percentage discounts
        r'-?\d+%',
        r'réduction.*\d+%',
        r'remise.*\d+%',
        r'promo.*\d+%',
        
        # Promotional language (French)
        r'\bsoldes?\b',
        r'\bpromotions?\b',
        r'\bréductions?\b',
        r'\boffres?\s+spéciales?\b',
        r'\bcode\s+promo\b',
        r'\bbons?\s+plans?\b',
        r'\bprix\s+cassés?\b',
        r'\bexceptionnelle?ment\b',
        r'\blimitée?\s+dans\s+le\s+temps\b',
        r'\bdépêchez-vous\b',
        r'\bprofitez\s+maintenant\b',
        r'\boffre\s+limitée\b',
        r'\bgratuitement?\b.*\bachat\b',
        r'\b\d+\s+acheté.*\d+\s+offert\b',
        
        # Discount codes
        r'\b[A-Z0-9]{4,}\b.*\bcode\b',
        r'\bcode.*[A-Z0-9]{4,}\b',
        
        # Urgency/scarcity
        r'\bdernier.*jour\b',
        r'\bse\s+termine\b',
        r'\bplus\s+que\b.*\bjours?\b',
        r'\bstock\s+limité\b',
        r'\bquantité\s+limitée\b'
    ]
    
    analysis_results = {
        "total_posts": len(posts),
        "posts_with_promotions": 0,
        "promotional_content_found": [],
        "clean_posts": 0,
        "flagged_posts": []
    }
    
    print_info(f"Analyzing {len(posts)} posts for promotional content...")
    
    for i, post in enumerate(posts, 1):
        post_title = post.get("title", "")
        post_text = post.get("text", "")
        post_hashtags = " ".join(post.get("hashtags", []))
        
        # Combine all text content
        full_content = f"{post_title} {post_text} {post_hashtags}".lower()
        
        print_info(f"\nPost {i}:")
        print_info(f"Title: {post_title}")
        print_info(f"Text: {post_text[:100]}...")
        
        # Check for promotional patterns
        found_promotions = []
        for pattern in promotion_patterns:
            matches = re.findall(pattern, full_content, re.IGNORECASE)
            if matches:
                found_promotions.extend(matches)
        
        if found_promotions:
            analysis_results["posts_with_promotions"] += 1
            analysis_results["promotional_content_found"].extend(found_promotions)
            analysis_results["flagged_posts"].append({
                "post_number": i,
                "title": post_title,
                "text": post_text,
                "promotions_found": found_promotions
            })
            print_error(f"❌ PROMOTIONAL CONTENT DETECTED: {found_promotions}")
        else:
            analysis_results["clean_posts"] += 1
            print_success(f"✅ Clean post - no promotional content")
    
    return analysis_results

def create_note_with_explicit_promotion(token: str, user_id: str) -> bool:
    """Create a note with explicit promotion to test that only explicit promotions appear"""
    print_header("CREATING NOTE WITH EXPLICIT PROMOTION")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a note with explicit promotion
        note_data = {
            "description": "Promotion spéciale septembre",
            "content": "Promotion 15% sur les consultations ce mois-ci. Utilisez le code SEPT15 pour bénéficier de cette offre spéciale valable jusqu'au 30 septembre.",
            "priority": "high",
            "is_monthly_note": False,
            "note_month": 9,
            "note_year": 2025
        }
        
        response = requests.post(f"{BACKEND_URL}/notes", headers=headers, json=note_data)
        
        if response.status_code == 200:
            data = response.json()
            note_id = data.get("note", {}).get("note_id")
            print_success(f"Created note with explicit promotion: {note_id}")
            print_info(f"Promotion content: {note_data['content']}")
            return True
        else:
            print_error(f"Failed to create promotional note: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error creating promotional note: {str(e)}")
        return False

def generate_posts_with_explicit_promotion(token: str, user_id: str) -> List[Dict]:
    """Generate posts with explicit promotion note"""
    print_header("GENERATING POSTS WITH EXPLICIT PROMOTION NOTE")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Clear existing posts first
        requests.delete(f"{BACKEND_URL}/posts/generated/all", headers=headers)
        time.sleep(2)
        
        # Generate posts for current month
        response = requests.post(f"{BACKEND_URL}/posts/generate", 
                               headers=headers,
                               params={"target_month": "septembre_2025"})
        
        if response.status_code == 200:
            data = response.json()
            posts_count = data.get("posts_count", 0)
            print_success(f"Generated {posts_count} posts with explicit promotion")
            
            # Get the generated posts
            posts_response = requests.get(f"{BACKEND_URL}/posts/generated", headers=headers)
            if posts_response.status_code == 200:
                posts_data = posts_response.json()
                posts = posts_data.get("posts", [])
                print_success(f"Retrieved {len(posts)} generated posts")
                return posts
            else:
                print_error(f"Failed to retrieve posts: {posts_response.status_code}")
                return []
        else:
            print_error(f"Failed to generate posts: {response.status_code}")
            print_error(f"Response: {response.text}")
            return []
            
    except Exception as e:
        print_error(f"Error generating posts with promotion: {str(e)}")
        return []

def verify_explicit_promotion_usage(posts: List[Dict]) -> Dict[str, Any]:
    """Verify that only the explicit promotion appears in posts"""
    print_header("VERIFYING EXPLICIT PROMOTION USAGE")
    
    # Expected promotion content
    expected_promotion = "15%"
    expected_code = "SEPT15"
    
    analysis_results = {
        "total_posts": len(posts),
        "posts_with_expected_promotion": 0,
        "posts_with_unexpected_promotions": 0,
        "expected_promotion_found": False,
        "unexpected_promotions": [],
        "posts_containing_expected": []
    }
    
    # Patterns for unexpected promotions (different from the explicit one)
    unexpected_patterns = [
        r'-?(?!15)\d+%',  # Any percentage except 15%
        r'code.*(?!SEPT15)[A-Z0-9]{4,}',  # Any code except SEPT15
        r'réduction.*(?!15%)\d+%',  # Any reduction except 15%
        r'promo.*(?!15%)\d+%',  # Any promo except 15%
    ]
    
    print_info(f"Analyzing {len(posts)} posts for explicit promotion usage...")
    
    for i, post in enumerate(posts, 1):
        post_title = post.get("title", "")
        post_text = post.get("text", "")
        post_hashtags = " ".join(post.get("hashtags", []))
        
        # Combine all text content
        full_content = f"{post_title} {post_text} {post_hashtags}"
        
        print_info(f"\nPost {i}:")
        print_info(f"Title: {post_title}")
        print_info(f"Text: {post_text[:150]}...")
        
        # Check for expected promotion
        has_expected_15_percent = "15%" in full_content
        has_expected_code = "SEPT15" in full_content
        
        if has_expected_15_percent or has_expected_code:
            analysis_results["posts_with_expected_promotion"] += 1
            analysis_results["expected_promotion_found"] = True
            analysis_results["posts_containing_expected"].append({
                "post_number": i,
                "title": post_title,
                "text": post_text,
                "has_15_percent": has_expected_15_percent,
                "has_code_sept15": has_expected_code
            })
            print_success(f"✅ Contains expected promotion (15% or SEPT15)")
        
        # Check for unexpected promotions
        found_unexpected = []
        for pattern in unexpected_patterns:
            matches = re.findall(pattern, full_content, re.IGNORECASE)
            if matches:
                found_unexpected.extend(matches)
        
        if found_unexpected:
            analysis_results["posts_with_unexpected_promotions"] += 1
            analysis_results["unexpected_promotions"].extend(found_unexpected)
            print_error(f"❌ UNEXPECTED PROMOTIONAL CONTENT: {found_unexpected}")
        else:
            print_success(f"✅ No unexpected promotional content")
    
    return analysis_results

def run_comprehensive_promotion_test():
    """Run comprehensive test of promotion system"""
    print_header("POSTS GENERATION ANTI-PROMOTION TESTING")
    print_info("Testing that AI no longer creates unsolicited promotions or discounts")
    
    # Step 1: Authentication
    token, user_id = authenticate()
    if not token:
        print_error("Authentication failed - cannot continue")
        return False
    
    # Step 2: Clear existing data
    clear_existing_posts(token, user_id)
    clear_existing_notes(token, user_id)
    time.sleep(2)
    
    # Step 3: Test without promotional notes
    print_header("TEST 1: POSTS WITHOUT PROMOTIONAL NOTES")
    
    if not create_test_note_without_promotion(token, user_id):
        print_error("Failed to create test note")
        return False
    
    time.sleep(2)
    posts_without_promotion = generate_posts_without_promotion(token, user_id)
    
    if not posts_without_promotion:
        print_error("Failed to generate posts without promotion")
        return False
    
    # Analyze posts for unsolicited promotions
    analysis_1 = analyze_posts_for_promotions(posts_without_promotion)
    
    # Step 4: Test with explicit promotional note
    print_header("TEST 2: POSTS WITH EXPLICIT PROMOTIONAL NOTE")
    
    if not create_note_with_explicit_promotion(token, user_id):
        print_error("Failed to create promotional note")
        return False
    
    time.sleep(2)
    posts_with_promotion = generate_posts_with_explicit_promotion(token, user_id)
    
    if not posts_with_promotion:
        print_error("Failed to generate posts with promotion")
        return False
    
    # Verify explicit promotion usage
    analysis_2 = verify_explicit_promotion_usage(posts_with_promotion)
    
    # Step 5: Generate final report
    print_header("FINAL TEST RESULTS")
    
    # Test 1 Results
    print_info("TEST 1 RESULTS (Without Promotional Notes):")
    print_info(f"Total posts generated: {analysis_1['total_posts']}")
    print_info(f"Posts with unsolicited promotions: {analysis_1['posts_with_promotions']}")
    print_info(f"Clean posts (no promotions): {analysis_1['clean_posts']}")
    
    if analysis_1['posts_with_promotions'] == 0:
        print_success("✅ TEST 1 PASSED: No unsolicited promotions found")
        test_1_passed = True
    else:
        print_error(f"❌ TEST 1 FAILED: Found {analysis_1['posts_with_promotions']} posts with unsolicited promotions")
        print_error(f"Promotional content found: {analysis_1['promotional_content_found']}")
        test_1_passed = False
    
    # Test 2 Results
    print_info("\nTEST 2 RESULTS (With Explicit Promotional Note):")
    print_info(f"Total posts generated: {analysis_2['total_posts']}")
    print_info(f"Posts with expected promotion: {analysis_2['posts_with_expected_promotion']}")
    print_info(f"Posts with unexpected promotions: {analysis_2['posts_with_unexpected_promotions']}")
    
    if analysis_2['expected_promotion_found'] and analysis_2['posts_with_unexpected_promotions'] == 0:
        print_success("✅ TEST 2 PASSED: Only explicit promotion found, no unexpected promotions")
        test_2_passed = True
    else:
        if not analysis_2['expected_promotion_found']:
            print_error("❌ TEST 2 FAILED: Expected promotion (15% or SEPT15) not found in any post")
        if analysis_2['posts_with_unexpected_promotions'] > 0:
            print_error(f"❌ TEST 2 FAILED: Found {analysis_2['posts_with_unexpected_promotions']} posts with unexpected promotions")
            print_error(f"Unexpected promotions: {analysis_2['unexpected_promotions']}")
        test_2_passed = False
    
    # Overall result
    print_header("OVERALL TEST RESULT")
    
    if test_1_passed and test_2_passed:
        print_success("🎉 ALL TESTS PASSED: Anti-promotion system working correctly")
        print_success("✅ AI does not create unsolicited promotions")
        print_success("✅ AI only uses explicitly mentioned promotions")
        return True
    else:
        print_error("❌ TESTS FAILED: Anti-promotion system needs attention")
        if not test_1_passed:
            print_error("- AI is still creating unsolicited promotions")
        if not test_2_passed:
            print_error("- AI is not properly handling explicit promotions")
        return False

if __name__ == "__main__":
    success = run_comprehensive_promotion_test()
    exit(0 if success else 1)