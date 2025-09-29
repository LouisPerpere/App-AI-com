#!/usr/bin/env python3
"""
TEST CORRECTION GRIDFS FILE_ID - Validation spécifique de la correction

OBJECTIF: Tester spécifiquement la correction des visual_id dans les posts générés.
La correction doit extraire les vrais GridFS file_id (format UUID) depuis les URLs existantes
au lieu d'utiliser les MongoDB _id (format 68bfea...).

CORRECTION À TESTER:
- visual_id DOIT être extrait de l'URL: /api/content/{UUID}/file
- PAS le MongoDB _id du document
- URLs fonctionnelles avec les nouveaux IDs

Backend URL: https://social-pub-hub.preview.emergentagent.com/api
"""

import requests
import json
import sys
import re
from datetime import datetime

# Configuration
BASE_URL = "https://social-pub-hub.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"
TARGET_MONTH = "septembre_2025"

def print_test_header(test_name):
    print(f"\n{'='*70}")
    print(f"🧪 TEST: {test_name}")
    print(f"{'='*70}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def extract_gridfs_id_from_url(url):
    """Extract GridFS file_id from URL like /api/content/{UUID}/file"""
    if not url:
        return None
    match = re.search(r'/api/content/([^/]+)/file', url)
    return match.group(1) if match else None

def is_uuid_format(text):
    """Check if text matches UUID format"""
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(uuid_pattern, text, re.IGNORECASE))

def authenticate():
    """Authenticate and return token"""
    print_test_header("AUTHENTIFICATION")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login-robust",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_id = data.get("user_id")
            print_success(f"Authentication successful - User ID: {user_id}")
            return token, user_id
        else:
            print_error(f"Authentication failed: {response.status_code}")
            return None, None
            
    except Exception as e:
        print_error(f"Authentication error: {str(e)}")
        return None, None

def analyze_content_structure(token, user_id):
    """Analyze current content structure to understand the correction needed"""
    print_test_header("ANALYSE STRUCTURE CONTENU ACTUEL")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/content/pending",
            headers=headers,
            params={"limit": 20},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            content_items = data.get("content", [])
            
            print_success(f"Retrieved {len(content_items)} content items")
            
            # Analyze the structure
            analysis = {
                "total_items": len(content_items),
                "items_with_urls": 0,
                "mongodb_ids": [],
                "gridfs_ids_from_urls": [],
                "url_id_mapping": {}
            }
            
            print_info("\n📊 ANALYSE DÉTAILLÉE:")
            
            for item in content_items:
                item_id = item.get("id", "")
                url = item.get("url", "")
                attributed_month = item.get("attributed_month", "")
                
                print_info(f"\n--- ITEM ---")
                print_info(f"MongoDB ID: {item_id}")
                print_info(f"URL: {url}")
                print_info(f"Month: {attributed_month}")
                
                if url:
                    analysis["items_with_urls"] += 1
                    gridfs_id = extract_gridfs_id_from_url(url)
                    
                    if gridfs_id:
                        analysis["gridfs_ids_from_urls"].append(gridfs_id)
                        analysis["url_id_mapping"][item_id] = gridfs_id
                        
                        print_info(f"GridFS ID extracted: {gridfs_id}")
                        
                        # Validate UUID format
                        if is_uuid_format(gridfs_id):
                            print_success(f"✅ Valid UUID format: {gridfs_id}")
                        else:
                            print_error(f"❌ Invalid UUID format: {gridfs_id}")
                    else:
                        print_error(f"❌ Could not extract GridFS ID from URL")
                
                analysis["mongodb_ids"].append(item_id)
            
            # Summary
            print_info(f"\n📋 RÉSUMÉ ANALYSE:")
            print_info(f"Total items: {analysis['total_items']}")
            print_info(f"Items with URLs: {analysis['items_with_urls']}")
            print_info(f"MongoDB IDs found: {len(analysis['mongodb_ids'])}")
            print_info(f"GridFS IDs extractable: {len(analysis['gridfs_ids_from_urls'])}")
            
            # Show mapping for septembre_2025 items
            septembre_items = [item for item in content_items if item.get("attributed_month") == TARGET_MONTH]
            print_info(f"\n🎯 ITEMS POUR {TARGET_MONTH}: {len(septembre_items)}")
            
            for item in septembre_items:
                mongodb_id = item.get("id")
                url = item.get("url")
                gridfs_id = extract_gridfs_id_from_url(url)
                title = item.get("title", "")
                
                print_info(f"  MongoDB ID: {mongodb_id}")
                print_info(f"  GridFS ID: {gridfs_id}")
                print_info(f"  Title: {title}")
                print_info(f"  ---")
            
            return True, analysis
            
        else:
            print_error(f"Failed to get content: {response.status_code}")
            return False, {}
            
    except Exception as e:
        print_error(f"Error analyzing content: {str(e)}")
        return False, {}

def test_image_access_with_gridfs_ids(token, analysis):
    """Test image access using extracted GridFS IDs"""
    print_test_header("TEST ACCÈS IMAGES AVEC GRIDFS IDs")
    
    gridfs_ids = analysis.get("gridfs_ids_from_urls", [])[:5]  # Test first 5
    
    if not gridfs_ids:
        print_error("No GridFS IDs to test")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    accessible_count = 0
    
    for gridfs_id in gridfs_ids:
        try:
            print_info(f"Testing access to GridFS ID: {gridfs_id}")
            
            response = requests.get(
                f"{BASE_URL}/content/{gridfs_id}/file",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                accessible_count += 1
                print_success(f"✅ Image accessible: {gridfs_id}")
                print_info(f"  Content-Type: {response.headers.get('content-type', 'unknown')}")
                print_info(f"  Content-Length: {response.headers.get('content-length', 'unknown')}")
            else:
                print_error(f"❌ Image not accessible: {gridfs_id} (status: {response.status_code})")
                
        except Exception as e:
            print_error(f"❌ Error accessing {gridfs_id}: {str(e)}")
    
    success_rate = (accessible_count / len(gridfs_ids)) * 100 if gridfs_ids else 0
    print_info(f"\n📊 RÉSULTATS ACCÈS IMAGES:")
    print_info(f"Images testées: {len(gridfs_ids)}")
    print_info(f"Images accessibles: {accessible_count}")
    print_info(f"Taux de succès: {success_rate:.1f}%")
    
    return accessible_count > 0

def generate_posts_and_validate_gridfs(token, user_id, analysis):
    """Generate posts and validate that visual_id uses GridFS format"""
    print_test_header("GÉNÉRATION POSTS ET VALIDATION GRIDFS")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        print_info(f"Generating posts for {TARGET_MONTH}...")
        
        response = requests.post(
            f"{BASE_URL}/posts/generate",
            headers=headers,
            params={"target_month": TARGET_MONTH},
            timeout=180
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Post generation completed: {data.get('posts_count', 0)} posts")
            
            # Get generated posts
            response = requests.get(
                f"{BASE_URL}/posts/generated",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                posts_data = response.json()
                posts = posts_data.get("posts", [])
                
                print_success(f"Retrieved {len(posts)} generated posts")
                
                # CRITICAL VALIDATION
                validation_results = {
                    "total_posts": len(posts),
                    "posts_with_visuals": 0,
                    "posts_with_gridfs_ids": 0,
                    "posts_with_mongodb_ids": 0,
                    "gridfs_ids_used": set(),
                    "mongodb_ids_used": set(),
                    "accessible_images": 0
                }
                
                expected_gridfs_ids = set(analysis.get("gridfs_ids_from_urls", []))
                mongodb_to_gridfs_mapping = analysis.get("url_id_mapping", {})
                
                print_info(f"\n🔍 VALIDATION CRITIQUE DES {len(posts)} POSTS:")
                print_info(f"Expected GridFS IDs available: {len(expected_gridfs_ids)}")
                
                for i, post in enumerate(posts, 1):
                    visual_id = post.get("visual_id", "")
                    visual_url = post.get("visual_url", "")
                    title = post.get("title", "")
                    
                    print_info(f"\n--- POST {i} ---")
                    print_info(f"Title: {title}")
                    print_info(f"Visual ID: {visual_id}")
                    print_info(f"Visual URL: {visual_url}")
                    
                    if visual_id:
                        validation_results["posts_with_visuals"] += 1
                        
                        # Check if it's GridFS UUID format
                        if is_uuid_format(visual_id):
                            validation_results["posts_with_gridfs_ids"] += 1
                            validation_results["gridfs_ids_used"].add(visual_id)
                            
                            if visual_id in expected_gridfs_ids:
                                print_success(f"✅ Uses CORRECT GridFS ID: {visual_id}")
                                
                                # Test image access
                                try:
                                    img_response = requests.get(
                                        f"{BASE_URL}/content/{visual_id}/file",
                                        headers=headers,
                                        timeout=10
                                    )
                                    if img_response.status_code == 200:
                                        validation_results["accessible_images"] += 1
                                        print_success(f"✅ Image accessible")
                                    else:
                                        print_error(f"❌ Image not accessible: {img_response.status_code}")
                                except Exception as e:
                                    print_error(f"❌ Error accessing image: {str(e)}")
                            else:
                                print_error(f"❌ GridFS ID not in expected list: {visual_id}")
                        
                        # Check if it's still using MongoDB format (DEPRECATED)
                        elif len(visual_id) == 24 and all(c in '0123456789abcdef' for c in visual_id.lower()):
                            validation_results["posts_with_mongodb_ids"] += 1
                            validation_results["mongodb_ids_used"].add(visual_id)
                            print_error(f"❌ DEPRECATED MongoDB ID format: {visual_id}")
                            
                            # Check if we can map it to GridFS
                            if visual_id in mongodb_to_gridfs_mapping:
                                expected_gridfs_id = mongodb_to_gridfs_mapping[visual_id]
                                print_error(f"❌ Should use GridFS ID: {expected_gridfs_id}")
                        
                        else:
                            print_error(f"❌ Unknown ID format: {visual_id}")
                    
                    else:
                        print_info("No visual ID (text-only post)")
                
                # FINAL ASSESSMENT
                print_test_header("RÉSULTATS VALIDATION CORRECTION GRIDFS")
                
                print_info(f"Total posts: {validation_results['total_posts']}")
                print_info(f"Posts with visuals: {validation_results['posts_with_visuals']}")
                print_info(f"Posts using GridFS IDs (CORRECT): {validation_results['posts_with_gridfs_ids']}")
                print_info(f"Posts using MongoDB IDs (DEPRECATED): {validation_results['posts_with_mongodb_ids']}")
                print_info(f"Accessible images: {validation_results['accessible_images']}")
                
                # Success criteria
                correction_success = True
                
                if validation_results["posts_with_mongodb_ids"] > 0:
                    print_error(f"❌ CORRECTION NON APPLIQUÉE: {validation_results['posts_with_mongodb_ids']} posts utilisent encore MongoDB IDs")
                    print_error(f"MongoDB IDs trouvés: {list(validation_results['mongodb_ids_used'])}")
                    correction_success = False
                else:
                    print_success("✅ Aucun MongoDB ID trouvé - Correction appliquée!")
                
                if validation_results["posts_with_gridfs_ids"] > 0:
                    print_success(f"✅ {validation_results['posts_with_gridfs_ids']} posts utilisent GridFS IDs (CORRECT)")
                    print_success(f"GridFS IDs utilisés: {list(validation_results['gridfs_ids_used'])}")
                else:
                    print_error("❌ Aucun post n'utilise GridFS IDs")
                    correction_success = False
                
                if validation_results["accessible_images"] > 0:
                    print_success(f"✅ {validation_results['accessible_images']} images accessibles avec GridFS IDs")
                else:
                    print_error("❌ Aucune image accessible")
                    correction_success = False
                
                return correction_success
                
            else:
                print_error(f"Failed to get generated posts: {response.status_code}")
                return False
        else:
            print_error(f"Post generation failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error in post generation/validation: {str(e)}")
        return False

def main():
    """Main test execution"""
    print("🎯 TEST CORRECTION GRIDFS FILE_ID")
    print("=" * 80)
    print("OBJECTIF: Valider que visual_id utilise GridFS UUID au lieu de MongoDB _id")
    print(f"TARGET MONTH: {TARGET_MONTH}")
    print("=" * 80)
    
    # Step 1: Authentication
    token, user_id = authenticate()
    if not token:
        print_error("Authentication failed - cannot continue")
        return False
    
    # Step 2: Analyze current content structure
    analysis_success, analysis = analyze_content_structure(token, user_id)
    if not analysis_success:
        print_error("Content analysis failed - cannot continue")
        return False
    
    # Step 3: Test image access with GridFS IDs
    access_success = test_image_access_with_gridfs_ids(token, analysis)
    if not access_success:
        print_error("GridFS image access failed - cannot continue")
        return False
    
    # Step 4: Generate posts and validate GridFS correction
    correction_success = generate_posts_and_validate_gridfs(token, user_id, analysis)
    
    # Final result
    print_test_header("RÉSULTAT FINAL")
    if correction_success:
        print_success("🎉 CORRECTION GRIDFS VALIDÉE!")
        print_success("✅ Posts utilisent GridFS UUID au lieu de MongoDB _id")
        print_success("✅ Images visibles avec nouveaux IDs")
        print_success("✅ Liaison photos-posts corrigée")
        return True
    else:
        print_error("❌ CORRECTION GRIDFS ÉCHOUÉE")
        print_error("❌ Posts utilisent encore MongoDB _id")
        print_error("❌ Correction non appliquée correctement")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)