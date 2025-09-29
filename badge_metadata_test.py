#!/usr/bin/env python3
"""
DIAGNOSTIC URGENT - Tests badges verts et métadonnées posts

PROBLÈMES SIGNALÉS PAR L'UTILISATEUR :
1. ❌ Images attachées depuis post n'ont pas badge vert "utilisée" dans bibliothèque
2. ❌ Images uploadées depuis post n'ont pas titre/contexte du post appliqués

TESTS DE DIAGNOSTIC REQUIS :

Test 1: Vérifier marquage used_in_posts après attachement
Test 2: Vérifier upload avec métadonnées post  
Test 3: Vérifier endpoint attach-image pour uploads
Test 4: Vérifier cohérence GET /api/posts/generated

Backend URL: https://social-pub-hub.preview.emergentagent.com/api
Credentials: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration
BASE_URL = "https://social-pub-hub.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"🧪 {test_name}")
    print(f"{'='*60}")

def print_step(step_num, description):
    print(f"\n📋 Step {step_num}: {description}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_warning(message):
    print(f"⚠️ {message}")

def authenticate():
    """Authenticate and get JWT token"""
    print_step(1, "Authentication")
    
    auth_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login-robust", json=auth_data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_id = data.get("user_id")
            print_success(f"Authentication successful - User ID: {user_id}")
            return token, user_id
        else:
            print_error(f"Authentication failed: {response.status_code} - {response.text}")
            return None, None
            
    except Exception as e:
        print_error(f"Authentication error: {str(e)}")
        return None, None

def get_library_images(token, user_id):
    """Get existing images from library"""
    print_step(2, "Getting library images")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/content/pending", headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            images = data.get("content", [])
            print_success(f"Found {len(images)} images in library")
            
            # Find an image that's not already used
            unused_image = None
            for img in images:
                if not img.get("used_in_posts", False):
                    unused_image = img
                    break
            
            if unused_image:
                print_success(f"Found unused image: {unused_image['id']} - {unused_image.get('filename', 'No filename')}")
                return unused_image
            else:
                print_warning("No unused images found in library")
                return images[0] if images else None
                
        else:
            print_error(f"Failed to get library images: {response.status_code}")
            return None
            
    except Exception as e:
        print_error(f"Error getting library images: {str(e)}")
        return None

def create_test_post(token, user_id):
    """Create a test post that needs an image"""
    print_step(3, "Creating test post")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # First generate posts to have something to work with
        response = requests.post(
            f"{BASE_URL}/posts/generate", 
            headers=headers, 
            params={"target_month": "decembre_2025"},
            timeout=120
        )
        
        if response.status_code == 200:
            print_success("Posts generated successfully")
            
            # Get generated posts
            response = requests.get(f"{BASE_URL}/posts/generated", headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                
                if posts:
                    test_post = posts[0]  # Use first post
                    print_success(f"Using test post: {test_post['id']}")
                    return test_post
                else:
                    print_error("No posts found after generation")
                    return None
            else:
                print_error(f"Failed to get generated posts: {response.status_code}")
                return None
        else:
            print_error(f"Failed to generate posts: {response.status_code}")
            return None
            
    except Exception as e:
        print_error(f"Error creating test post: {str(e)}")
        return None

def test_attach_library_image(token, user_id, library_image, test_post):
    """Test 1: Vérifier marquage used_in_posts après attachement"""
    print_test_header("TEST 1: Marquage used_in_posts après attachement depuis bibliothèque")
    
    if not library_image or not test_post:
        print_error("Missing library image or test post")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Note initial status
    initial_used_status = library_image.get("used_in_posts", False)
    print(f"📊 Image initiale - ID: {library_image['id']}, used_in_posts: {initial_used_status}")
    
    # Attach image to post
    attach_data = {
        "image_source": "library",
        "image_id": library_image["id"]
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/posts/{test_post['id']}/attach-image",
            json=attach_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            print_success("Image attached to post successfully")
            
            # Verify the image is now marked as used
            response = requests.get(f"{BASE_URL}/content/pending", headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                images = data.get("content", [])
                
                # Find our image
                updated_image = None
                for img in images:
                    if img["id"] == library_image["id"]:
                        updated_image = img
                        break
                
                if updated_image:
                    used_status = updated_image.get("used_in_posts", False)
                    print(f"📊 Image après attachement - used_in_posts: {used_status}")
                    
                    if used_status:
                        print_success("✅ BADGE VERT: Image correctement marquée comme utilisée")
                        return True
                    else:
                        print_error("❌ PROBLÈME BADGE: Image PAS marquée comme utilisée")
                        return False
                else:
                    print_error("Image not found after attachment")
                    return False
            else:
                print_error(f"Failed to verify image status: {response.status_code}")
                return False
        else:
            print_error(f"Failed to attach image: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error in attach library image test: {str(e)}")
        return False

def test_upload_with_post_metadata(token, user_id, test_post):
    """Test 2: Vérifier upload avec métadonnées post"""
    print_test_header("TEST 2: Upload avec métadonnées du post")
    
    if not test_post:
        print_error("Missing test post")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a simple test image file (1x1 pixel PNG)
    import io
    from PIL import Image
    
    # Create a small test image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Upload with post metadata
    files = {
        'files': ('test_post_image.png', img_bytes, 'image/png')
    }
    
    form_data = {
        'attributed_month': 'decembre_2025',
        'upload_type': 'post_single',
        'common_title': test_post.get('title', 'Titre du post de test'),
        'common_context': f"Image pour le post: {test_post.get('text', 'Texte du post')[:100]}"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/content/batch-upload",
            files=files,
            data=form_data,
            headers=headers,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            uploaded_files = data.get("uploaded_files", [])
            
            if uploaded_files:
                uploaded_file = uploaded_files[0]
                file_id = uploaded_file.get("id")
                print_success(f"File uploaded successfully - ID: {file_id}")
                
                # Verify metadata was applied
                response = requests.get(f"{BASE_URL}/content/pending", headers=headers, timeout=30)
                
                if response.status_code == 200:
                    content_data = response.json()
                    images = content_data.get("content", [])
                    
                    # Find our uploaded image
                    uploaded_image = None
                    for img in images:
                        if img["id"] == file_id:
                            uploaded_image = img
                            break
                    
                    if uploaded_image:
                        title = uploaded_image.get("title", "")
                        context = uploaded_image.get("context", "")
                        
                        print(f"📊 Image uploadée - Titre: '{title}'")
                        print(f"📊 Image uploadée - Contexte: '{context}'")
                        
                        # Check if post metadata was applied
                        has_post_title = test_post.get('title', '') in title if title else False
                        has_post_context = any(word in context.lower() for word in ['post', 'titre', 'texte']) if context else False
                        
                        if title and context:
                            print_success("✅ MÉTADONNÉES: Titre et contexte appliqués")
                            return True, file_id
                        else:
                            print_error("❌ PROBLÈME MÉTADONNÉES: Titre ou contexte manquants")
                            return False, file_id
                    else:
                        print_error("Uploaded image not found in library")
                        return False, None
                else:
                    print_error(f"Failed to verify uploaded image: {response.status_code}")
                    return False, None
            else:
                print_error("No files uploaded")
                return False, None
        else:
            print_error(f"Upload failed: {response.status_code} - {response.text}")
            return False, None
            
    except Exception as e:
        print_error(f"Error in upload with metadata test: {str(e)}")
        return False, None

def test_attach_uploaded_image(token, user_id, uploaded_file_id, test_post):
    """Test 3: Vérifier endpoint attach-image pour uploads"""
    print_test_header("TEST 3: Attach-image pour uploads avec marquage used_in_posts")
    
    if not uploaded_file_id or not test_post:
        print_error("Missing uploaded file ID or test post")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create another test post for this test
    try:
        response = requests.post(
            f"{BASE_URL}/posts/generate", 
            headers=headers, 
            params={"target_month": "decembre_2025"},
            timeout=120
        )
        
        if response.status_code == 200:
            # Get a new post
            response = requests.get(f"{BASE_URL}/posts/generated", headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                
                if len(posts) > 1:
                    new_test_post = posts[1]  # Use second post
                else:
                    new_test_post = posts[0] if posts else None
                
                if not new_test_post:
                    print_error("No test post available")
                    return False
                
                # Attach uploaded image to post
                attach_data = {
                    "image_source": "upload",
                    "uploaded_file_ids": [uploaded_file_id]
                }
                
                response = requests.put(
                    f"{BASE_URL}/posts/{new_test_post['id']}/attach-image",
                    json=attach_data,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    print_success("Uploaded image attached to post successfully")
                    
                    # Verify the uploaded image is now marked as used
                    response = requests.get(f"{BASE_URL}/content/pending", headers=headers, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        images = data.get("content", [])
                        
                        # Find our uploaded image
                        updated_image = None
                        for img in images:
                            if img["id"] == uploaded_file_id:
                                updated_image = img
                                break
                        
                        if updated_image:
                            used_status = updated_image.get("used_in_posts", False)
                            print(f"📊 Image uploadée après attachement - used_in_posts: {used_status}")
                            
                            if used_status:
                                print_success("✅ BADGE VERT UPLOAD: Image uploadée correctement marquée comme utilisée")
                                return True
                            else:
                                print_error("❌ PROBLÈME BADGE UPLOAD: Image uploadée PAS marquée comme utilisée")
                                return False
                        else:
                            print_error("Uploaded image not found after attachment")
                            return False
                    else:
                        print_error(f"Failed to verify uploaded image status: {response.status_code}")
                        return False
                else:
                    print_error(f"Failed to attach uploaded image: {response.status_code} - {response.text}")
                    return False
            else:
                print_error(f"Failed to get posts for attachment test: {response.status_code}")
                return False
        else:
            print_error(f"Failed to generate posts for attachment test: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error in attach uploaded image test: {str(e)}")
        return False

def test_posts_consistency(token, user_id):
    """Test 4: Vérifier cohérence GET /api/posts/generated"""
    print_test_header("TEST 4: Cohérence des posts générés")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/posts/generated", headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            posts = data.get("posts", [])
            
            print(f"📊 Total posts trouvés: {len(posts)}")
            
            posts_with_images = 0
            posts_with_valid_visual_id = 0
            posts_with_valid_visual_url = 0
            
            for post in posts:
                visual_id = post.get("visual_id", "")
                visual_url = post.get("visual_url", "")
                
                if visual_id or visual_url:
                    posts_with_images += 1
                    
                    if visual_id and visual_id != "":
                        posts_with_valid_visual_id += 1
                        
                    if visual_url and visual_url != "":
                        posts_with_valid_visual_url += 1
                        
                    print(f"📊 Post {post['id'][:8]}... - visual_id: {visual_id[:20] if visual_id else 'None'}..., visual_url: {visual_url[:30] if visual_url else 'None'}...")
            
            print(f"📊 Posts avec images: {posts_with_images}/{len(posts)}")
            print(f"📊 Posts avec visual_id valide: {posts_with_valid_visual_id}/{posts_with_images}")
            print(f"📊 Posts avec visual_url valide: {posts_with_valid_visual_url}/{posts_with_images}")
            
            if posts_with_images > 0:
                consistency_rate = (posts_with_valid_visual_id + posts_with_valid_visual_url) / (posts_with_images * 2) * 100
                print(f"📊 Taux de cohérence: {consistency_rate:.1f}%")
                
                if consistency_rate >= 80:
                    print_success("✅ COHÉRENCE: Posts avec images ont des visual_id/visual_url cohérents")
                    return True
                else:
                    print_warning("⚠️ COHÉRENCE PARTIELLE: Certains posts ont des visual_id/visual_url manquants")
                    return False
            else:
                print_warning("Aucun post avec image trouvé")
                return True
                
        else:
            print_error(f"Failed to get generated posts: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error in posts consistency test: {str(e)}")
        return False

def main():
    """Main test execution"""
    print_test_header("DIAGNOSTIC URGENT - Tests badges verts et métadonnées posts")
    
    # Step 1: Authentication
    token, user_id = authenticate()
    if not token:
        print_error("Authentication failed - cannot continue tests")
        sys.exit(1)
    
    # Step 2: Get library images
    library_image = get_library_images(token, user_id)
    
    # Step 3: Create test post
    test_post = create_test_post(token, user_id)
    
    # Run diagnostic tests
    test_results = []
    
    # Test 1: Library image attachment and badge
    if library_image and test_post:
        result1 = test_attach_library_image(token, user_id, library_image, test_post)
        test_results.append(("Marquage badge après attachement bibliothèque", result1))
    else:
        test_results.append(("Marquage badge après attachement bibliothèque", False))
        print_error("Skipped Test 1 - missing library image or test post")
    
    # Test 2: Upload with post metadata
    if test_post:
        result2, uploaded_file_id = test_upload_with_post_metadata(token, user_id, test_post)
        test_results.append(("Upload avec métadonnées post", result2))
    else:
        result2, uploaded_file_id = False, None
        test_results.append(("Upload avec métadonnées post", False))
        print_error("Skipped Test 2 - missing test post")
    
    # Test 3: Attach uploaded image and badge
    if uploaded_file_id and test_post:
        result3 = test_attach_uploaded_image(token, user_id, uploaded_file_id, test_post)
        test_results.append(("Marquage badge après attachement upload", result3))
    else:
        test_results.append(("Marquage badge après attachement upload", False))
        print_error("Skipped Test 3 - missing uploaded file or test post")
    
    # Test 4: Posts consistency
    result4 = test_posts_consistency(token, user_id)
    test_results.append(("Cohérence posts générés", result4))
    
    # Final results
    print_test_header("RÉSULTATS FINAUX DU DIAGNOSTIC")
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        if result:
            print_success(f"✅ {test_name}")
            passed_tests += 1
        else:
            print_error(f"❌ {test_name}")
    
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"\n📊 TAUX DE RÉUSSITE: {passed_tests}/{total_tests} tests passés ({success_rate:.1f}%)")
    
    if success_rate >= 75:
        print_success("🎉 DIAGNOSTIC: Système majoritairement fonctionnel")
    elif success_rate >= 50:
        print_warning("⚠️ DIAGNOSTIC: Problèmes partiels identifiés")
    else:
        print_error("🚨 DIAGNOSTIC: Problèmes critiques identifiés")
    
    print(f"\n📋 RECOMMANDATIONS:")
    if not test_results[0][1]:  # Library attachment badge
        print("- Vérifier la logique de marquage used_in_posts dans attach-image endpoint")
    if not test_results[1][1]:  # Upload metadata
        print("- Vérifier l'application des métadonnées lors de l'upload depuis post")
    if not test_results[2][1]:  # Upload attachment badge
        print("- Vérifier le marquage used_in_posts pour les images uploadées")
    if not test_results[3][1]:  # Posts consistency
        print("- Vérifier la cohérence des visual_id/visual_url dans les posts")

if __name__ == "__main__":
    main()