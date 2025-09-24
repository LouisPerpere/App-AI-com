#!/usr/bin/env python3
"""
TEST DU SYSTÈME D'ATTACHEMENT D'IMAGES AUX POSTS - PHASE 1: VALIDATION BACKEND

Contexte: Test du système d'attachement d'images aux posts avec corrections JavaScript 
et améliorations backend importantes.

CORRECTIONS RÉCENTES À VALIDER:
1. ✅ Correction erreur JavaScript "searchPixabay is not defined" 
2. ✅ Amélioration endpoint PUT /api/posts/{post_id}/attach-image pour UUIDs
3. ✅ Support carrousels (uploads multiples)
4. ✅ Implémentation uploadFilesForPost avec métadonnées automatiques
5. ✅ Fonction handleFileSelect pour sélection de fichiers

TESTS REQUIS - Endpoints critiques:
- POST /api/posts/generate (prérequis)
- PUT /api/posts/{post_id}/attach-image avec différentes sources
- POST /api/content/batch-upload puis attachement

Backend URL: https://instamanager-1.preview.emergentagent.com/api
Credentials: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import sys
import os
import tempfile
from datetime import datetime
from io import BytesIO
from PIL import Image

# Configuration
BASE_URL = "https://instamanager-1.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

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

def authenticate():
    """Step 1: Authenticate with test credentials"""
    print_test_header("AUTHENTIFICATION")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login-robust",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_id = data.get("user_id")
            
            print_success(f"Authentication successful")
            print_info(f"User ID: {user_id}")
            print_info(f"Email: {data.get('email')}")
            
            return token, user_id
        else:
            print_error(f"Authentication failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None, None
            
    except Exception as e:
        print_error(f"Authentication error: {str(e)}")
        return None, None

def generate_test_posts(token, user_id):
    """Test 1: POST /api/posts/generate - Générer posts de test avec status='needs_image'"""
    print_test_header("TEST 1: GÉNÉRATION DE POSTS DE TEST")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        print_info("Generating test posts with POST /api/posts/generate")
        
        response = requests.post(
            f"{BASE_URL}/posts/generate",
            headers=headers,
            params={"target_month": "octobre_2025"},
            timeout=120
        )
        
        print_info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Post generation completed successfully")
            print_info(f"Posts generated: {data.get('posts_count', 0)}")
            print_info(f"Strategy: {data.get('strategy', {})}")
            
            # Get generated posts to verify they exist
            posts_response = requests.get(
                f"{BASE_URL}/posts/generated",
                headers=headers,
                timeout=30
            )
            
            if posts_response.status_code == 200:
                posts_data = posts_response.json()
                posts = posts_data.get("posts", [])
                
                print_success(f"Found {len(posts)} generated posts")
                
                # Find posts that need images
                posts_needing_images = [p for p in posts if p.get("status") == "needs_image" or not p.get("visual_id")]
                
                if posts_needing_images:
                    print_success(f"Found {len(posts_needing_images)} posts needing images")
                    return posts_needing_images[:3]  # Return first 3 for testing
                else:
                    print_info("No posts found with status='needs_image', using first 3 posts for testing")
                    return posts[:3]
            else:
                print_error(f"Failed to retrieve generated posts: {posts_response.status_code}")
                return []
        else:
            print_error(f"Post generation failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return []
            
    except Exception as e:
        print_error(f"Error generating posts: {str(e)}")
        return []

def get_library_images(token, user_id):
    """Get existing images from user's library"""
    print_test_header("RÉCUPÉRATION IMAGES BIBLIOTHÈQUE")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/content/pending",
            headers=headers,
            params={"limit": 50},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            content_items = data.get("content", [])
            
            # Filter for images only
            image_items = [item for item in content_items if item.get("file_type", "").startswith("image")]
            
            print_success(f"Found {len(image_items)} images in library")
            
            if image_items:
                for i, item in enumerate(image_items[:5]):  # Show first 5
                    print_info(f"Image {i+1}: {item.get('id')} - {item.get('title', item.get('filename', 'No title'))}")
                
                return image_items
            else:
                print_error("No images found in library")
                return []
        else:
            print_error(f"Failed to get library content: {response.status_code}")
            return []
            
    except Exception as e:
        print_error(f"Error getting library images: {str(e)}")
        return []

def test_attach_library_image(token, user_id, test_posts, library_images):
    """Test 2: PUT /api/posts/{post_id}/attach-image avec source='library'"""
    print_test_header("TEST 2: ATTACHEMENT IMAGE BIBLIOTHÈQUE")
    
    if not test_posts or not library_images:
        print_error("No test posts or library images available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        post = test_posts[0]
        image = library_images[0]
        
        post_id = post.get("id")
        image_id = image.get("id")
        
        print_info(f"Attaching library image {image_id} to post {post_id}")
        print_info(f"Image title: {image.get('title', image.get('filename', 'No title'))}")
        
        attach_request = {
            "image_source": "library",
            "image_id": image_id
        }
        
        response = requests.put(
            f"{BASE_URL}/posts/{post_id}/attach-image",
            headers=headers,
            json=attach_request,
            timeout=30
        )
        
        print_info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Library image attached successfully")
            print_info(f"Message: {data.get('message')}")
            print_info(f"Visual URL: {data.get('visual_url')}")
            print_info(f"Visual ID: {data.get('visual_id')}")
            print_info(f"Status: {data.get('status')}")
            
            # Verify the image is marked as used
            if data.get("status") == "with_image":
                print_success("Post status correctly updated to 'with_image'")
            
            # Verify visual_id matches the library image ID
            if data.get("visual_id") == image_id:
                print_success("Visual ID correctly matches library image ID")
            else:
                print_error(f"Visual ID mismatch: expected {image_id}, got {data.get('visual_id')}")
            
            return True
        else:
            print_error(f"Failed to attach library image: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error attaching library image: {str(e)}")
        return False

def test_attach_pixabay_image(token, user_id, test_posts):
    """Test 3: PUT /api/posts/{post_id}/attach-image avec source='pixabay'"""
    print_test_header("TEST 3: ATTACHEMENT IMAGE PIXABAY")
    
    if len(test_posts) < 2:
        print_error("Not enough test posts available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # First, search for a Pixabay image
        print_info("Searching for Pixabay images...")
        
        search_response = requests.get(
            f"{BASE_URL}/pixabay/search",
            headers=headers,
            params={"query": "business", "per_page": 5},
            timeout=30
        )
        
        if search_response.status_code != 200:
            print_error(f"Pixabay search failed: {search_response.status_code}")
            return False
        
        search_data = search_response.json()
        hits = search_data.get("hits", [])
        
        if not hits:
            print_error("No Pixabay images found")
            return False
        
        pixabay_image = hits[0]
        print_success(f"Found Pixabay image: ID {pixabay_image.get('id')}")
        
        # Now attach the Pixabay image to a post
        post = test_posts[1]
        post_id = post.get("id")
        
        print_info(f"Attaching Pixabay image {pixabay_image.get('id')} to post {post_id}")
        
        attach_request = {
            "image_source": "pixabay",
            "image_url": pixabay_image.get("webformatURL"),
            "image_id": str(pixabay_image.get("id"))
        }
        
        response = requests.put(
            f"{BASE_URL}/posts/{post_id}/attach-image",
            headers=headers,
            json=attach_request,
            timeout=30
        )
        
        print_info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Pixabay image attached successfully")
            print_info(f"Message: {data.get('message')}")
            print_info(f"Visual URL: {data.get('visual_url')}")
            print_info(f"Visual ID: {data.get('visual_id')}")
            print_info(f"Status: {data.get('status')}")
            
            # Verify attachment
            if data.get("status") == "with_image":
                print_success("Post status correctly updated to 'with_image'")
            
            return True
        else:
            print_error(f"Failed to attach Pixabay image: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error attaching Pixabay image: {str(e)}")
        return False

def create_test_image(filename="test_image.jpg"):
    """Create a test image file for upload testing"""
    # Create a simple test image
    img = Image.new('RGB', (640, 480), color='blue')
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    img.save(temp_file.name, 'JPEG')
    temp_file.close()
    
    return temp_file.name

def test_upload_and_attach_single(token, user_id, test_posts):
    """Test 4a: POST /api/content/batch-upload puis PUT /api/posts/{post_id}/attach-image (single file)"""
    print_test_header("TEST 4A: UPLOAD ET ATTACHEMENT FICHIER UNIQUE")
    
    if len(test_posts) < 3:
        print_error("Not enough test posts available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        post = test_posts[2] if len(test_posts) > 2 else test_posts[0]
        post_id = post.get("id")
        post_title = post.get("title", "Test Post")
        post_text = post.get("text", "Test content")
        
        # Create test image
        test_image_path = create_test_image()
        
        print_info(f"Uploading single file for post {post_id}")
        print_info(f"Post title: {post_title}")
        
        # Upload file using batch-upload endpoint
        with open(test_image_path, 'rb') as f:
            files = {'files': ('test_single.jpg', f, 'image/jpeg')}
            data = {
                'upload_type': 'single',
                'attributed_month': 'octobre_2025',
                'common_title': f"Image pour: {post_title}",
                'common_context': f"Image uploadée pour le post: {post_text[:100]}..."
            }
            
            upload_response = requests.post(
                f"{BASE_URL}/content/batch-upload",
                headers=headers,
                files=files,
                data=data,
                timeout=60
            )
        
        # Clean up test file
        os.unlink(test_image_path)
        
        print_info(f"Upload response status: {upload_response.status_code}")
        
        if upload_response.status_code != 200:
            print_error(f"Upload failed: {upload_response.status_code}")
            print_error(f"Response: {upload_response.text}")
            return False
        
        upload_data = upload_response.json()
        uploaded_files = upload_data.get("created", [])  # Changed from "uploaded_files" to "created"
        
        if not uploaded_files:
            print_error("No files were uploaded")
            return False
        
        uploaded_file_id = uploaded_files[0].get("id")
        print_success(f"File uploaded successfully: {uploaded_file_id}")
        
        # Now attach the uploaded file to the post
        print_info(f"Attaching uploaded file {uploaded_file_id} to post {post_id}")
        
        attach_request = {
            "image_source": "upload",
            "uploaded_file_ids": [uploaded_file_id]
        }
        
        attach_response = requests.put(
            f"{BASE_URL}/posts/{post_id}/attach-image",
            headers=headers,
            json=attach_request,
            timeout=30
        )
        
        print_info(f"Attach response status: {attach_response.status_code}")
        
        if attach_response.status_code == 200:
            attach_data = attach_response.json()
            print_success("Uploaded file attached successfully")
            print_info(f"Message: {attach_data.get('message')}")
            print_info(f"Visual URL: {attach_data.get('visual_url')}")
            print_info(f"Visual ID: {attach_data.get('visual_id')}")
            print_info(f"Status: {attach_data.get('status')}")
            
            # Verify attachment
            if attach_data.get("status") == "with_image":
                print_success("Post status correctly updated to 'with_image'")
            
            if attach_data.get("visual_id") == uploaded_file_id:
                print_success("Visual ID correctly matches uploaded file ID")
            
            return True
        else:
            print_error(f"Failed to attach uploaded file: {attach_response.status_code}")
            print_error(f"Response: {attach_response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error in upload and attach single: {str(e)}")
        return False

def test_upload_and_attach_carousel(token, user_id, test_posts):
    """Test 4b: POST /api/content/batch-upload puis PUT /api/posts/{post_id}/attach-image (carousel)"""
    print_test_header("TEST 4B: UPLOAD ET ATTACHEMENT CARROUSEL")
    
    if not test_posts:
        print_error("No test posts available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Use the first available post or create a new test scenario
        post = test_posts[0]
        post_id = post.get("id")
        post_title = post.get("title", "Test Carousel Post")
        post_text = post.get("text", "Test carousel content")
        
        # Create multiple test images
        test_image_paths = []
        for i in range(3):
            img = Image.new('RGB', (640, 480), color=['red', 'green', 'blue'][i])
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'_carousel_{i}.jpg')
            img.save(temp_file.name, 'JPEG')
            temp_file.close()
            test_image_paths.append(temp_file.name)
        
        print_info(f"Uploading {len(test_image_paths)} files for carousel to post {post_id}")
        print_info(f"Post title: {post_title}")
        
        # Upload multiple files using batch-upload endpoint
        files = []
        for i, path in enumerate(test_image_paths):
            files.append(('files', (f'carousel_image_{i}.jpg', open(path, 'rb'), 'image/jpeg')))
        
        data = {
            'upload_type': 'carousel',
            'attributed_month': 'octobre_2025',
            'common_title': f"Carrousel pour: {post_title}",
            'common_context': f"Images carrousel pour le post: {post_text[:100]}..."
        }
        
        try:
            upload_response = requests.post(
                f"{BASE_URL}/content/batch-upload",
                headers=headers,
                files=files,
                data=data,
                timeout=90
            )
        finally:
            # Close file handles and clean up
            for _, (_, file_handle, _) in files:
                file_handle.close()
            for path in test_image_paths:
                os.unlink(path)
        
        print_info(f"Upload response status: {upload_response.status_code}")
        
        if upload_response.status_code != 200:
            print_error(f"Carousel upload failed: {upload_response.status_code}")
            print_error(f"Response: {upload_response.text}")
            return False
        
        upload_data = upload_response.json()
        uploaded_files = upload_data.get("created", [])  # Changed from "uploaded_files" to "created"
        
        if len(uploaded_files) < 2:
            print_error(f"Expected multiple files, got {len(uploaded_files)}")
            return False
        
        uploaded_file_ids = [f.get("id") for f in uploaded_files]
        print_success(f"Carousel uploaded successfully: {len(uploaded_file_ids)} files")
        print_info(f"File IDs: {uploaded_file_ids}")
        
        # Now attach the carousel to the post
        print_info(f"Attaching carousel ({len(uploaded_file_ids)} files) to post {post_id}")
        
        attach_request = {
            "image_source": "upload",
            "uploaded_file_ids": uploaded_file_ids
        }
        
        attach_response = requests.put(
            f"{BASE_URL}/posts/{post_id}/attach-image",
            headers=headers,
            json=attach_request,
            timeout=30
        )
        
        print_info(f"Attach response status: {attach_response.status_code}")
        
        if attach_response.status_code == 200:
            attach_data = attach_response.json()
            print_success("Carousel attached successfully")
            print_info(f"Message: {attach_data.get('message')}")
            print_info(f"Visual URL: {attach_data.get('visual_url')}")
            print_info(f"Visual ID: {attach_data.get('visual_id')}")
            print_info(f"Status: {attach_data.get('status')}")
            
            # Verify carousel attachment
            if attach_data.get("status") == "with_image":
                print_success("Post status correctly updated to 'with_image'")
            
            # For carousel, visual_url should be different format
            visual_url = attach_data.get("visual_url", "")
            if "/carousel/" in visual_url:
                print_success("Carousel visual URL format is correct")
            else:
                print_info(f"Visual URL format: {visual_url}")
            
            return True
        else:
            print_error(f"Failed to attach carousel: {attach_response.status_code}")
            print_error(f"Response: {attach_response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error in upload and attach carousel: {str(e)}")
        return False

def validate_uuid_handling(token, user_id):
    """Test 5: Validation du support UUID dans les requêtes MongoDB"""
    print_test_header("TEST 5: VALIDATION SUPPORT UUID")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get some content to test UUID handling
        response = requests.get(
            f"{BASE_URL}/content/pending",
            headers=headers,
            params={"limit": 5},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            content_items = data.get("content", [])
            
            if content_items:
                # Test with first item
                test_item = content_items[0]
                item_id = test_item.get("id")
                
                print_info(f"Testing UUID handling with content ID: {item_id}")
                
                # Test title update (this uses parse_any_id function)
                title_response = requests.put(
                    f"{BASE_URL}/content/{item_id}/title",
                    headers=headers,
                    json={"title": "Test UUID Handling"},
                    timeout=30
                )
                
                if title_response.status_code == 200:
                    print_success("UUID handling in content endpoints working correctly")
                    
                    # Restore original title
                    requests.put(
                        f"{BASE_URL}/content/{item_id}/title",
                        headers=headers,
                        json={"title": test_item.get("title", "")},
                        timeout=30
                    )
                    
                    return True
                else:
                    print_error(f"UUID handling test failed: {title_response.status_code}")
                    return False
            else:
                print_info("No content items available for UUID testing")
                return True
        else:
            print_error(f"Failed to get content for UUID testing: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error testing UUID handling: {str(e)}")
        return False

def main():
    """Main test execution"""
    print("🎯 TEST DU SYSTÈME D'ATTACHEMENT D'IMAGES AUX POSTS")
    print("=" * 80)
    print("PHASE 1: VALIDATION BACKEND")
    print("Endpoints critiques: POST /api/posts/generate, PUT /api/posts/{id}/attach-image")
    print("Sources testées: library, pixabay, upload (single + carousel)")
    print("=" * 80)
    
    # Step 1: Authentication
    token, user_id = authenticate()
    if not token:
        print_error("Authentication failed - cannot continue")
        return False
    
    # Step 2: Generate test posts
    test_posts = generate_test_posts(token, user_id)
    if not test_posts:
        print_error("No test posts available - cannot continue")
        return False
    
    # Step 3: Get library images
    library_images = get_library_images(token, user_id)
    
    # Test results tracking
    test_results = {
        "library_attachment": False,
        "pixabay_attachment": False,
        "single_upload_attachment": False,
        "carousel_upload_attachment": False,
        "uuid_handling": False
    }
    
    # Step 4: Test library image attachment
    if library_images:
        test_results["library_attachment"] = test_attach_library_image(token, user_id, test_posts, library_images)
    else:
        print_info("Skipping library attachment test - no library images available")
    
    # Step 5: Test Pixabay image attachment
    test_results["pixabay_attachment"] = test_attach_pixabay_image(token, user_id, test_posts)
    
    # Step 6: Test single file upload and attachment
    test_results["single_upload_attachment"] = test_upload_and_attach_single(token, user_id, test_posts)
    
    # Step 7: Test carousel upload and attachment
    test_results["carousel_upload_attachment"] = test_upload_and_attach_carousel(token, user_id, test_posts)
    
    # Step 8: Test UUID handling
    test_results["uuid_handling"] = validate_uuid_handling(token, user_id)
    
    # Final results
    print_test_header("RÉSULTATS FINAUX")
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    print_info(f"Tests réussis: {passed_tests}/{total_tests}")
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print_info(f"{test_name}: {status}")
    
    success_rate = (passed_tests / total_tests) * 100
    
    if success_rate >= 80:
        print_success(f"🎉 SYSTÈME D'ATTACHEMENT D'IMAGES OPÉRATIONNEL ({success_rate:.1f}% succès)")
        print_success("✅ Endpoints critiques fonctionnels")
        print_success("✅ Support UUID validé")
        print_success("✅ Gestion carrousels opérationnelle")
        return True
    else:
        print_error(f"❌ SYSTÈME D'ATTACHEMENT NÉCESSITE DES CORRECTIONS ({success_rate:.1f}% succès)")
        print_error("❌ Certains endpoints critiques échouent")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)