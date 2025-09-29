#!/usr/bin/env python3
"""
Refined Anti-Promotion Test for Posts Generation System
Testing that AI no longer creates unsolicited promotions or discounts.
"""

import requests
import json
import time
import re
from datetime import datetime
from typing import Dict, List, Any

# Configuration
BACKEND_URL = "https://social-pub-hub.preview.emergentagent.com/api"
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
            return None, None
            
    except Exception as e:
        print_error(f"Authentication error: {str(e)}")
        return None, None

def clear_existing_data(token: str, user_id: str) -> bool:
    """Clear existing posts and notes"""
    print_header("CLEARING EXISTING DATA")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Clear posts
        posts_response = requests.delete(f"{BACKEND_URL}/posts/generated/all", headers=headers)
        posts_cleared = posts_response.status_code == 200
        
        # Clear notes
        notes_response = requests.get(f"{BACKEND_URL}/notes", headers=headers)
        notes_cleared = 0
        if notes_response.status_code == 200:
            notes = notes_response.json().get("notes", [])
            for note in notes:
                note_id = note.get("note_id")
                if note_id:
                    delete_response = requests.delete(f"{BACKEND_URL}/notes/{note_id}", headers=headers)
                    if delete_response.status_code == 200:
                        notes_cleared += 1
        
        print_success(f"Cleared existing data - Notes: {notes_cleared}")
        return True
        
    except Exception as e:
        print_error(f"Error clearing data: {str(e)}")
        return False

def test_posts_without_promotion(token: str, user_id: str) -> Dict[str, Any]:
    """Test 1: Generate posts without promotional notes"""
    print_header("TEST 1: POSTS WITHOUT PROMOTIONAL NOTES")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a general business note (no promotions)
        note_data = {
            "description": "Informations générales",
            "content": "Notre atelier d'horlogerie se spécialise dans la réparation et la restauration de montres anciennes. Nous travaillons avec passion sur chaque pièce.",
            "priority": "high",
            "is_monthly_note": True
        }
        
        note_response = requests.post(f"{BACKEND_URL}/notes", headers=headers, json=note_data)
        if note_response.status_code != 200:
            return {"success": False, "error": "Failed to create note"}
        
        print_success("Created general business note")
        time.sleep(2)
        
        # Generate posts
        gen_response = requests.post(f"{BACKEND_URL}/posts/generate", 
                                   headers=headers,
                                   params={"target_month": "septembre_2025"})
        
        if gen_response.status_code != 200:
            return {"success": False, "error": "Failed to generate posts"}
        
        posts_count = gen_response.json().get("posts_count", 0)
        print_success(f"Generated {posts_count} posts")
        
        # Get generated posts
        posts_response = requests.get(f"{BACKEND_URL}/posts/generated", headers=headers)
        if posts_response.status_code != 200:
            return {"success": False, "error": "Failed to retrieve posts"}
        
        posts = posts_response.json().get("posts", [])
        print_success(f"Retrieved {len(posts)} posts")
        
        # Analyze posts for promotional content
        analysis = analyze_posts_for_unsolicited_promotions(posts)
        
        return {
            "success": True,
            "posts_count": len(posts),
            "posts": posts,
            "analysis": analysis
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def test_posts_with_explicit_promotion(token: str, user_id: str) -> Dict[str, Any]:
    """Test 2: Generate posts with explicit promotional note"""
    print_header("TEST 2: POSTS WITH EXPLICIT PROMOTIONAL NOTE")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Clear existing posts
        requests.delete(f"{BACKEND_URL}/posts/generated/all", headers=headers)
        time.sleep(1)
        
        # Create explicit promotional note
        promo_note = {
            "description": "Promotion septembre",
            "content": "Promotion 15% sur les consultations ce mois-ci. Utilisez le code SEPT15 pour bénéficier de cette offre spéciale valable jusqu'au 30 septembre.",
            "priority": "high",
            "is_monthly_note": False,
            "note_month": 9,
            "note_year": 2025
        }
        
        note_response = requests.post(f"{BACKEND_URL}/notes", headers=headers, json=promo_note)
        if note_response.status_code != 200:
            return {"success": False, "error": "Failed to create promotional note"}
        
        print_success("Created explicit promotional note")
        time.sleep(2)
        
        # Generate posts
        gen_response = requests.post(f"{BACKEND_URL}/posts/generate", 
                                   headers=headers,
                                   params={"target_month": "septembre_2025"})
        
        if gen_response.status_code != 200:
            return {"success": False, "error": "Failed to generate posts"}
        
        posts_count = gen_response.json().get("posts_count", 0)
        print_success(f"Generated {posts_count} posts with promotional note")
        
        # Get generated posts
        posts_response = requests.get(f"{BACKEND_URL}/posts/generated", headers=headers)
        if posts_response.status_code != 200:
            return {"success": False, "error": "Failed to retrieve posts"}
        
        posts = posts_response.json().get("posts", [])
        print_success(f"Retrieved {len(posts)} posts")
        
        # Analyze posts for explicit promotion usage
        analysis = analyze_explicit_promotion_usage(posts)
        
        return {
            "success": True,
            "posts_count": len(posts),
            "posts": posts,
            "analysis": analysis
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def analyze_posts_for_unsolicited_promotions(posts: List[Dict]) -> Dict[str, Any]:
    """Analyze posts for unsolicited promotional content"""
    print_info("Analyzing posts for unsolicited promotional content...")
    
    # Simple promotional indicators
    promotional_keywords = [
        "soldes", "promotion", "réduction", "remise", "promo", 
        "offre spéciale", "code promo", "bon plan", "prix cassé",
        "exceptionnellement", "dépêchez-vous", "profitez maintenant",
        "offre limitée", "gratuitement", "stock limité"
    ]
    
    # Percentage patterns
    percentage_pattern = r'\b\d+%\b'
    
    analysis = {
        "total_posts": len(posts),
        "posts_with_promotions": 0,
        "promotional_content": [],
        "clean_posts": 0
    }
    
    for i, post in enumerate(posts, 1):
        title = post.get("title", "").lower()
        text = post.get("text", "").lower()
        hashtags = " ".join(post.get("hashtags", [])).lower()
        
        full_content = f"{title} {text} {hashtags}"
        
        print_info(f"Post {i}: {post.get('title', 'No title')}")
        print_info(f"Text preview: {post.get('text', '')[:100]}...")
        
        # Check for promotional keywords
        found_keywords = [kw for kw in promotional_keywords if kw in full_content]
        
        # Check for percentages
        percentages = re.findall(percentage_pattern, full_content)
        
        if found_keywords or percentages:
            analysis["posts_with_promotions"] += 1
            analysis["promotional_content"].extend(found_keywords + percentages)
            print_error(f"❌ Promotional content found: {found_keywords + percentages}")
        else:
            analysis["clean_posts"] += 1
            print_success("✅ Clean post - no promotional content")
    
    return analysis

def analyze_explicit_promotion_usage(posts: List[Dict]) -> Dict[str, Any]:
    """Analyze posts for proper usage of explicit promotion"""
    print_info("Analyzing posts for explicit promotion usage...")
    
    analysis = {
        "total_posts": len(posts),
        "posts_with_expected_promotion": 0,
        "expected_promotion_found": False,
        "posts_with_15_percent": 0,
        "posts_with_sept15": 0
    }
    
    for i, post in enumerate(posts, 1):
        title = post.get("title", "")
        text = post.get("text", "")
        hashtags = " ".join(post.get("hashtags", []))
        
        full_content = f"{title} {text} {hashtags}"
        
        print_info(f"Post {i}: {post.get('title', 'No title')}")
        print_info(f"Text preview: {post.get('text', '')[:150]}...")
        
        # Check for expected promotion elements
        has_15_percent = "15%" in full_content
        has_sept15 = "SEPT15" in full_content
        
        if has_15_percent:
            analysis["posts_with_15_percent"] += 1
            print_success("✅ Contains expected 15% promotion")
        
        if has_sept15:
            analysis["posts_with_sept15"] += 1
            print_success("✅ Contains expected SEPT15 code")
        
        if has_15_percent or has_sept15:
            analysis["posts_with_expected_promotion"] += 1
            analysis["expected_promotion_found"] = True
            print_success("✅ Contains expected promotional content")
        else:
            print_info("ℹ️ No explicit promotional content in this post")
    
    return analysis

def run_anti_promotion_test():
    """Run the complete anti-promotion test suite"""
    print_header("POSTS GENERATION ANTI-PROMOTION TEST SUITE")
    print_info("Testing that AI follows the new anti-promotion rules")
    
    # Authentication
    token, user_id = authenticate()
    if not token:
        print_error("Authentication failed")
        return False
    
    # Clear existing data
    if not clear_existing_data(token, user_id):
        print_error("Failed to clear existing data")
        return False
    
    time.sleep(2)
    
    # Test 1: Posts without promotional notes
    test1_result = test_posts_without_promotion(token, user_id)
    if not test1_result["success"]:
        print_error(f"Test 1 failed: {test1_result['error']}")
        return False
    
    time.sleep(3)
    
    # Test 2: Posts with explicit promotional note
    test2_result = test_posts_with_explicit_promotion(token, user_id)
    if not test2_result["success"]:
        print_error(f"Test 2 failed: {test2_result['error']}")
        return False
    
    # Generate final report
    print_header("FINAL TEST RESULTS")
    
    # Test 1 Analysis
    analysis1 = test1_result["analysis"]
    print_info("TEST 1 RESULTS (Without Promotional Notes):")
    print_info(f"Total posts: {analysis1['total_posts']}")
    print_info(f"Posts with unsolicited promotions: {analysis1['posts_with_promotions']}")
    print_info(f"Clean posts: {analysis1['clean_posts']}")
    
    test1_passed = analysis1['posts_with_promotions'] == 0
    if test1_passed:
        print_success("✅ TEST 1 PASSED: No unsolicited promotions found")
    else:
        print_error(f"❌ TEST 1 FAILED: Found {analysis1['posts_with_promotions']} posts with unsolicited promotions")
        print_error(f"Promotional content: {analysis1['promotional_content']}")
    
    # Test 2 Analysis
    analysis2 = test2_result["analysis"]
    print_info("\nTEST 2 RESULTS (With Explicit Promotional Note):")
    print_info(f"Total posts: {analysis2['total_posts']}")
    print_info(f"Posts with expected promotion: {analysis2['posts_with_expected_promotion']}")
    print_info(f"Posts with 15%: {analysis2['posts_with_15_percent']}")
    print_info(f"Posts with SEPT15: {analysis2['posts_with_sept15']}")
    
    test2_passed = analysis2['expected_promotion_found']
    if test2_passed:
        print_success("✅ TEST 2 PASSED: Explicit promotion properly integrated")
    else:
        print_error("❌ TEST 2 FAILED: Expected promotion not found in any post")
    
    # Overall result
    print_header("OVERALL RESULT")
    
    if test1_passed and test2_passed:
        print_success("🎉 ALL TESTS PASSED")
        print_success("✅ AI does not create unsolicited promotions")
        print_success("✅ AI properly integrates explicit promotions")
        return True
    else:
        print_error("❌ SOME TESTS FAILED")
        if not test1_passed:
            print_error("- AI is still creating unsolicited promotions")
        if not test2_passed:
            print_error("- AI is not properly integrating explicit promotions")
        return False

if __name__ == "__main__":
    success = run_anti_promotion_test()
    exit(0 if success else 1)