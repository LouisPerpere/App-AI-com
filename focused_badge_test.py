#!/usr/bin/env python3
"""
FOCUSED BADGE TEST - Diagnostic spécifique des problèmes identifiés

PROBLÈMES IDENTIFIÉS DANS LES LOGS:
1. ❌ Erreurs async/await: "object UpdateResult can't be used in 'await' expression"
2. ❌ Upload réussi mais erreur thumbnail: "'coroutine' object has no attribute 'update_one'"
3. ✅ Badge bibliothèque fonctionne: "Library image marked as used"

TESTS FOCALISÉS:
1. Test simple upload sans métadonnées complexes
2. Test attach-image avec upload simple
3. Vérification badge après attachement upload
"""

import requests
import json
import sys
from datetime import datetime
import uuid
import io
from PIL import Image

# Configuration
BASE_URL = "https://instamanager-1.preview.emergentagent.com/api"
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

def test_simple_upload(token, user_id):
    """Test simple upload without complex metadata"""
    print_test_header("TEST SIMPLE UPLOAD")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a simple test image
    img = Image.new('RGB', (50, 50), color='blue')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Simple upload with minimal data
    files = {
        'files': ('simple_test.png', img_bytes, 'image/png')
    }
    
    form_data = {
        'attributed_month': 'janvier_2025',
        'upload_type': 'single'
    }
    
    try:
        print_step(2, "Uploading simple image")
        response = requests.post(
            f"{BASE_URL}/content/batch-upload",
            files=files,
            data=form_data,
            headers=headers,
            timeout=60
        )
        
        print(f"📊 Upload response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            uploaded_files = data.get("created", [])  # Use "created" instead of "uploaded_files"
            
            if uploaded_files:
                uploaded_file = uploaded_files[0]
                file_id = uploaded_file.get("id")
                print_success(f"Simple upload successful - ID: {file_id}")
                
                # Verify the file appears in library
                print_step(3, "Verifying file in library")
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
                        print_success(f"File found in library: {uploaded_image['filename']}")
                        print(f"📊 used_in_posts: {uploaded_image.get('used_in_posts', False)}")
                        print(f"📊 title: '{uploaded_image.get('title', '')}'")
                        print(f"📊 context: '{uploaded_image.get('context', '')}'")
                        return file_id, uploaded_image
                    else:
                        print_error("Uploaded file not found in library")
                        return None, None
                else:
                    print_error(f"Failed to get library: {response.status_code}")
                    return None, None
            else:
                print_error("No files in upload response")
                return None, None
        else:
            print_error(f"Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None, None
            
    except Exception as e:
        print_error(f"Upload error: {str(e)}")
        return None, None

def create_simple_post(token, user_id):
    """Create a simple test post"""
    print_step(4, "Creating simple test post")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Generate a single post
        response = requests.post(
            f"{BASE_URL}/posts/generate", 
            headers=headers, 
            params={"target_month": "janvier_2025"},
            timeout=120
        )
        
        if response.status_code == 200:
            print_success("Post generated successfully")
            
            # Get the post
            response = requests.get(f"{BASE_URL}/posts/generated", headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                
                # Find a post without image
                for post in posts:
                    if not post.get("visual_id") and not post.get("visual_url"):
                        print_success(f"Found post without image: {post['id']}")
                        return post
                
                # If no post without image, use the first one
                if posts:
                    print_warning(f"Using first post (may have image): {posts[0]['id']}")
                    return posts[0]
                else:
                    print_error("No posts found")
                    return None
            else:
                print_error(f"Failed to get posts: {response.status_code}")
                return None
        else:
            print_error(f"Failed to generate post: {response.status_code}")
            return None
            
    except Exception as e:
        print_error(f"Post creation error: {str(e)}")
        return None

def test_attach_upload_to_post(token, user_id, file_id, test_post):
    """Test attaching uploaded file to post and verify badge"""
    print_test_header("TEST ATTACH UPLOAD TO POST")
    
    if not file_id or not test_post:
        print_error("Missing file ID or test post")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print_step(5, f"Attaching upload {file_id} to post {test_post['id']}")
    
    # Attach uploaded image to post
    attach_data = {
        "image_source": "upload",
        "uploaded_file_ids": [file_id]
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/posts/{test_post['id']}/attach-image",
            json=attach_data,
            headers=headers,
            timeout=30
        )
        
        print(f"📊 Attach response status: {response.status_code}")
        
        if response.status_code == 200:
            print_success("Upload attached to post successfully")
            
            print_step(6, "Verifying badge status after attachment")
            
            # Check if the uploaded image is now marked as used
            response = requests.get(f"{BASE_URL}/content/pending", headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                images = data.get("content", [])
                
                # Find our uploaded image
                updated_image = None
                for img in images:
                    if img["id"] == file_id:
                        updated_image = img
                        break
                
                if updated_image:
                    used_status = updated_image.get("used_in_posts", False)
                    print(f"📊 Image après attachement - used_in_posts: {used_status}")
                    
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
                print_error(f"Failed to verify image status: {response.status_code}")
                return False
        else:
            print_error(f"Failed to attach upload: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Attach upload error: {str(e)}")
        return False

def test_upload_with_title_context(token, user_id):
    """Test upload with explicit title and context"""
    print_test_header("TEST UPLOAD WITH TITLE AND CONTEXT")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a test image
    img = Image.new('RGB', (60, 60), color='green')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Upload with explicit title and context
    files = {
        'files': ('titled_test.png', img_bytes, 'image/png')
    }
    
    form_data = {
        'attributed_month': 'janvier_2025',
        'upload_type': 'post_single',
        'common_title': 'Titre de test explicite',
        'common_context': 'Contexte de test pour vérifier les métadonnées'
    }
    
    try:
        print_step(7, "Uploading with explicit title and context")
        response = requests.post(
            f"{BASE_URL}/content/batch-upload",
            files=files,
            data=form_data,
            headers=headers,
            timeout=60
        )
        
        print(f"📊 Upload response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            uploaded_files = data.get("created", [])  # Use "created" instead of "uploaded_files"
            
            if uploaded_files:
                uploaded_file = uploaded_files[0]
                file_id = uploaded_file.get("id")
                print_success(f"Upload with metadata successful - ID: {file_id}")
                
                # Verify metadata was applied
                print_step(8, "Verifying metadata application")
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
                        
                        print(f"📊 Titre trouvé: '{title}'")
                        print(f"📊 Contexte trouvé: '{context}'")
                        
                        # Check if our explicit metadata was applied
                        title_match = "Titre de test explicite" in title
                        context_match = "Contexte de test pour vérifier" in context
                        
                        if title_match and context_match:
                            print_success("✅ MÉTADONNÉES: Titre et contexte explicites correctement appliqués")
                            return True, file_id
                        elif title or context:
                            print_warning("⚠️ MÉTADONNÉES PARTIELLES: Certaines métadonnées appliquées")
                            print(f"   Title match: {title_match}, Context match: {context_match}")
                            return False, file_id
                        else:
                            print_error("❌ MÉTADONNÉES MANQUANTES: Aucune métadonnée appliquée")
                            return False, file_id
                    else:
                        print_error("Uploaded image not found in library")
                        return False, None
                else:
                    print_error(f"Failed to verify metadata: {response.status_code}")
                    return False, None
            else:
                print_error("No files in upload response")
                return False, None
        else:
            print_error(f"Upload with metadata failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
            
    except Exception as e:
        print_error(f"Upload with metadata error: {str(e)}")
        return False, None

def main():
    """Main test execution"""
    print_test_header("FOCUSED BADGE TEST - Diagnostic spécifique")
    
    # Step 1: Authentication
    token, user_id = authenticate()
    if not token:
        print_error("Authentication failed - cannot continue tests")
        sys.exit(1)
    
    # Test results tracking
    test_results = []
    
    # Test 1: Simple upload
    file_id, uploaded_image = test_simple_upload(token, user_id)
    if file_id:
        test_results.append(("Upload simple", True))
    else:
        test_results.append(("Upload simple", False))
        print_error("Simple upload failed - skipping attachment test")
    
    # Test 2: Create test post
    test_post = create_simple_post(token, user_id)
    if test_post:
        test_results.append(("Création post test", True))
    else:
        test_results.append(("Création post test", False))
        print_error("Post creation failed - skipping attachment test")
    
    # Test 3: Attach upload to post and verify badge
    if file_id and test_post:
        badge_result = test_attach_upload_to_post(token, user_id, file_id, test_post)
        test_results.append(("Badge après attachement upload", badge_result))
    else:
        test_results.append(("Badge après attachement upload", False))
        print_error("Skipped attachment test - missing file or post")
    
    # Test 4: Upload with explicit metadata
    metadata_result, metadata_file_id = test_upload_with_title_context(token, user_id)
    test_results.append(("Upload avec métadonnées explicites", metadata_result))
    
    # Final results
    print_test_header("RÉSULTATS FINAUX")
    
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
    
    # Specific diagnostics
    print(f"\n🔍 DIAGNOSTIC SPÉCIFIQUE:")
    
    if test_results[0][1]:  # Simple upload worked
        print("✅ Upload basique fonctionne")
    else:
        print("❌ Upload basique échoue - problème fondamental")
    
    if test_results[2][1]:  # Badge after attachment worked
        print("✅ Badge après attachement upload fonctionne")
    else:
        print("❌ Badge après attachement upload ne fonctionne pas")
    
    if test_results[3][1]:  # Metadata upload worked
        print("✅ Métadonnées explicites fonctionnent")
    else:
        print("❌ Métadonnées explicites ne fonctionnent pas")
    
    print(f"\n📋 RECOMMANDATIONS TECHNIQUES:")
    if not test_results[0][1]:
        print("- Vérifier les erreurs async/await dans routes_uploads.py")
        print("- Corriger les erreurs 'coroutine' object has no attribute 'update_one'")
    
    if not test_results[2][1]:
        print("- Vérifier la logique de marquage used_in_posts dans attach-image endpoint")
        print("- S'assurer que les UUIDs sont correctement traités")
    
    if not test_results[3][1]:
        print("- Vérifier l'application des common_title et common_context")
        print("- Contrôler la logique de métadonnées dans batch-upload")

if __name__ == "__main__":
    main()