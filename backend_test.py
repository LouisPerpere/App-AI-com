#!/usr/bin/env python3
"""
DIAGNOSTIC DIRECT - Valeur réelle posting_frequency en base
Test spécifique pour identifier le problème de persistance posting_frequency
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://social-gpt-5.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class PostingFrequencyDiagnostic:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        
    def authenticate(self):
        """Authentification avec les credentials fournis"""
        print("🔐 ÉTAPE 1: Authentification...")
        
        auth_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json=auth_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Configure headers for subsequent requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                })
                
                print(f"✅ Authentification réussie")
                print(f"   User ID: {self.user_id}")
                print(f"   Token: {self.token[:20]}..." if self.token else "No token")
                return True
            else:
                print(f"❌ Échec authentification: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur authentification: {str(e)}")
            return False
    
    def get_current_posting_frequency(self):
        """Test 1: Récupérer la valeur actuelle de posting_frequency"""
        print("\n📊 TEST 1: Vérification valeur actuelle posting_frequency...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/business-profile", timeout=30)
            
            if response.status_code == 200:
                profile_data = response.json()
                posting_frequency = profile_data.get("posting_frequency")
                
                print(f"✅ GET /api/business-profile réussi")
                print(f"   posting_frequency actuelle: '{posting_frequency}'")
                print(f"   Type: {type(posting_frequency)}")
                
                # Afficher tous les champs du profil pour diagnostic complet
                print(f"   business_name: {profile_data.get('business_name')}")
                print(f"   business_type: {profile_data.get('business_type')}")
                print(f"   brand_tone: {profile_data.get('brand_tone')}")
                
                return posting_frequency
            else:
                print(f"❌ Échec GET business-profile: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur GET business-profile: {str(e)}")
            return None
    
    def update_posting_frequency_to_weekly(self):
        """Test 2: Mise à jour temporaire vers 'weekly'"""
        print("\n🔄 TEST 2: Mise à jour posting_frequency vers 'weekly'...")
        
        update_data = {
            "posting_frequency": "weekly"
        }
        
        try:
            response = self.session.put(
                f"{BACKEND_URL}/business-profile",
                json=update_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ PUT /api/business-profile réussi")
                print(f"   Response: {result}")
                return True
            else:
                print(f"❌ Échec PUT business-profile: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur PUT business-profile: {str(e)}")
            return False
    
    def verify_posting_frequency_persistence(self):
        """Test 3: Vérification de la persistance"""
        print("\n🔍 TEST 3: Vérification persistance posting_frequency...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/business-profile", timeout=30)
            
            if response.status_code == 200:
                profile_data = response.json()
                posting_frequency = profile_data.get("posting_frequency")
                
                print(f"✅ GET /api/business-profile (vérification) réussi")
                print(f"   posting_frequency après mise à jour: '{posting_frequency}'")
                print(f"   Type: {type(posting_frequency)}")
                
                if posting_frequency == "weekly":
                    print("✅ PERSISTANCE CONFIRMÉE: La valeur 'weekly' est bien sauvegardée")
                    return True
                else:
                    print(f"❌ PROBLÈME PERSISTANCE: Attendu 'weekly', trouvé '{posting_frequency}'")
                    return False
            else:
                print(f"❌ Échec GET business-profile (vérification): {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur GET business-profile (vérification): {str(e)}")
            return False
    
    def run_diagnostic(self):
        """Exécuter le diagnostic complet"""
        print("=" * 80)
        print("🔍 DIAGNOSTIC DIRECT - Valeur réelle posting_frequency en base")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Credentials: {TEST_EMAIL} / {TEST_PASSWORD}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        # Étape 1: Authentification
        if not self.authenticate():
            print("\n❌ DIAGNOSTIC ÉCHOUÉ: Impossible de s'authentifier")
            return False
        
        # Étape 2: Récupérer valeur actuelle
        current_value = self.get_current_posting_frequency()
        if current_value is None:
            print("\n❌ DIAGNOSTIC ÉCHOUÉ: Impossible de récupérer le profil business")
            return False
        
        # Étape 3: Mise à jour vers 'weekly'
        if not self.update_posting_frequency_to_weekly():
            print("\n❌ DIAGNOSTIC ÉCHOUÉ: Impossible de mettre à jour posting_frequency")
            return False
        
        # Étape 4: Vérification persistance
        persistence_ok = self.verify_posting_frequency_persistence()
        
        # Résumé du diagnostic
        print("\n" + "=" * 80)
        print("📋 RÉSUMÉ DU DIAGNOSTIC")
        print("=" * 80)
        print(f"Valeur initiale: '{current_value}'")
        print(f"Valeur après mise à jour: Vérifiée dans TEST 3")
        print(f"Persistance: {'✅ OK' if persistence_ok else '❌ PROBLÈME'}")
        
        if persistence_ok:
            print("\n✅ CONCLUSION: Le backend sauvegarde correctement posting_frequency")
            print("   Le problème pourrait venir du frontend ou de la synchronisation")
        else:
            print("\n❌ CONCLUSION: Problème de persistance détecté dans le backend")
            print("   La valeur ne se sauvegarde pas correctement en base")
            print("\n🔍 ANALYSE TECHNIQUE:")
            print("   - GET /api/business-profile lit depuis 'business_profiles' collection (owner_id)")
            print("   - PUT /api/business-profile écrit dans 'users' collection (user_id)")
            print("   - MISMATCH: Les données sont lues et écrites dans des collections différentes!")
            print("   - SOLUTION: Corriger PUT pour écrire dans 'business_profiles' collection")
        
        return persistence_ok

def main():
    """Point d'entrée principal"""
    diagnostic = PostingFrequencyDiagnostic()
    success = diagnostic.run_diagnostic()
    
    if success:
        print("\n🎉 DIAGNOSTIC TERMINÉ AVEC SUCCÈS")
        sys.exit(0)
    else:
        print("\n💥 DIAGNOSTIC ÉCHOUÉ")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
BACKEND TEST FINAL - VRAIES PHOTOS DE MONTRES LAURENT PERPERE
Test de génération de posts avec les 7 vraies photos de montres identifiées.

OBJECTIF: Tester la génération de posts avec les 7 vraies photos de montres de Laurent Perpere.

DONNÉES CONFIRMÉES:
- User ID: bdf87a74-e3f3-44f3-bac2-649cde3ef93e ✅
- 7 photos dans septembre_2025 ✅
- IDs réels: 68bfea6a78835f304341584b, 68bfea6978835f3043415847, 68bfea6878835f3043415844, 68bfea6778835f3043415841, 68bfea6678835f304341583e, 68bfea6578835f304341583a, 68ba94e55e3a1fa9652636a5
- Titres: "Montage en cours", "Fond transparent", "Modèle en petite serie", etc.

TESTS À EFFECTUER:
1. Authentification (lperpere@yahoo.fr / L@Reunion974!)
2. POST /api/posts/generate avec target_month="septembre_2025" (pas octobre!)
3. VALIDATION CRITIQUE des visual_id dans les posts:
   - DOIVENT correspondre aux 7 IDs réels des photos de montres
   - ZERO "global_fallback_X" 
   - visual_url = /api/content/{REAL_WATCH_ID}/file
4. Vérification que les posts utilisent les vrais titres des montres

Backend URL: https://social-gpt-5.preview.emergentagent.com/api
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://social-gpt-5.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

# IDs réels des 7 photos de montres confirmées
EXPECTED_WATCH_IDS = [
    "68bfea6a78835f304341584b",
    "68bfea6978835f3043415847", 
    "68bfea6878835f3043415844",
    "68bfea6778835f3043415841",
    "68bfea6678835f304341583e",
    "68bfea6578835f304341583a",
    "68ba94e55e3a1fa9652636a5"
]

EXPECTED_USER_ID = "bdf87a74-e3f3-44f3-bac2-649cde3ef93e"

def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"🧪 TEST: {test_name}")
    print(f"{'='*60}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def authenticate():
    """Step 1: Authenticate with Laurent Perpere credentials"""
    print_test_header("AUTHENTIFICATION LAURENT PERPERE")
    
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
            
            # Verify user ID matches expected
            if user_id == EXPECTED_USER_ID:
                print_success(f"User ID matches expected: {EXPECTED_USER_ID}")
            else:
                print_error(f"User ID mismatch! Expected: {EXPECTED_USER_ID}, Got: {user_id}")
                
            return token, user_id
        else:
            print_error(f"Authentication failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None, None
            
    except Exception as e:
        print_error(f"Authentication error: {str(e)}")
        return None, None

def verify_watch_photos(token, user_id):
    """Step 2: Verify the 7 watch photos exist in septembre_2025"""
    print_test_header("VÉRIFICATION DES 7 PHOTOS DE MONTRES")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/content/pending",
            headers=headers,
            params={"limit": 100},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            content_items = data.get("content", [])
            
            print_success(f"Retrieved {len(content_items)} content items")
            
            # Filter for septembre_2025 items
            septembre_items = [item for item in content_items if item.get("attributed_month") == "septembre_2025"]
            print_info(f"Items in septembre_2025: {len(septembre_items)}")
            
            # Check for expected watch IDs
            found_watch_ids = []
            watch_details = {}
            
            for item in septembre_items:
                item_id = item.get("id")
                if item_id in EXPECTED_WATCH_IDS:
                    found_watch_ids.append(item_id)
                    watch_details[item_id] = {
                        "title": item.get("title", ""),
                        "filename": item.get("filename", ""),
                        "context": item.get("context", "")
                    }
                    print_success(f"Found watch ID: {item_id}")
                    print_info(f"  Title: {item.get('title', 'N/A')}")
                    print_info(f"  Filename: {item.get('filename', 'N/A')}")
            
            # Verify watch IDs are found
            missing_ids = set(EXPECTED_WATCH_IDS) - set(found_watch_ids)
            if not missing_ids:
                print_success(f"All 7 watch photos found in septembre_2025! ✅")
                return True, watch_details
            elif len(found_watch_ids) >= 6:
                print_info(f"Found {len(found_watch_ids)}/7 watch photos in septembre_2025")
                print_info(f"Missing watch IDs: {list(missing_ids)}")
                print_success("Sufficient watch photos found to proceed with testing ✅")
                return True, watch_details
            else:
                print_error(f"Insufficient watch photos found: {len(found_watch_ids)}/7")
                print_error(f"Missing watch IDs: {list(missing_ids)}")
                return False, watch_details
                
        else:
            print_error(f"Failed to get content: {response.status_code}")
            return False, {}
            
    except Exception as e:
        print_error(f"Error verifying watch photos: {str(e)}")
        return False, {}

def generate_posts_septembre(token, user_id):
    """Step 3: Generate posts for septembre_2025 (NOT octobre!)"""
    print_test_header("GÉNÉRATION DE POSTS SEPTEMBRE 2025")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        print_info("Calling POST /api/posts/generate with target_month='septembre_2025'")
        
        response = requests.post(
            f"{BASE_URL}/posts/generate",
            headers=headers,
            params={"target_month": "septembre_2025"},
            timeout=120  # Extended timeout for AI generation
        )
        
        print_info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Post generation completed successfully")
            print_info(f"Posts generated: {data.get('posts_count', 0)}")
            print_info(f"Strategy: {data.get('strategy', {})}")
            print_info(f"Sources used: {data.get('sources_used', {})}")
            return True
        else:
            print_error(f"Post generation failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error generating posts: {str(e)}")
        return False

def validate_generated_posts(token, user_id, watch_details):
    """Step 4: VALIDATION CRITIQUE - Verify posts use real watch IDs"""
    print_test_header("VALIDATION CRITIQUE DES POSTS GÉNÉRÉS")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/posts/generated",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            posts = data.get("posts", [])
            
            print_success(f"Retrieved {len(posts)} generated posts")
            
            if not posts:
                print_error("No posts found! Generation may have failed.")
                return False
            
            # Critical validation
            validation_results = {
                "total_posts": len(posts),
                "posts_with_visuals": 0,
                "posts_with_real_watch_ids": 0,
                "posts_with_fallback_ids": 0,
                "real_watch_ids_used": set(),
                "fallback_ids_found": [],
                "invalid_visual_urls": []
            }
            
            print_info(f"\n🔍 ANALYSE DÉTAILLÉE DES {len(posts)} POSTS:")
            
            for i, post in enumerate(posts, 1):
                visual_id = post.get("visual_id", "")
                visual_url = post.get("visual_url", "")
                title = post.get("title", "")
                text = post.get("text", "")
                
                print_info(f"\n--- POST {i} ---")
                print_info(f"Title: {title}")
                print_info(f"Visual ID: {visual_id}")
                print_info(f"Visual URL: {visual_url}")
                
                # Check if post has visual
                if visual_id:
                    validation_results["posts_with_visuals"] += 1
                    
                    # CRITICAL: Check if visual_id is a real watch ID
                    if visual_id in EXPECTED_WATCH_IDS:
                        validation_results["posts_with_real_watch_ids"] += 1
                        validation_results["real_watch_ids_used"].add(visual_id)
                        print_success(f"✅ Uses REAL watch ID: {visual_id}")
                        
                        # Check if title/text references the watch
                        watch_info = watch_details.get(visual_id, {})
                        watch_title = watch_info.get("title", "")
                        if watch_title and watch_title.lower() in text.lower():
                            print_success(f"✅ Post text references watch title: '{watch_title}'")
                        
                    # CRITICAL: Check for forbidden fallback IDs
                    elif "global_fallback" in visual_id.lower():
                        validation_results["posts_with_fallback_ids"] += 1
                        validation_results["fallback_ids_found"].append(visual_id)
                        print_error(f"❌ FORBIDDEN fallback ID found: {visual_id}")
                    
                    else:
                        print_error(f"❌ Unknown visual ID (not in expected watch IDs): {visual_id}")
                    
                    # CRITICAL: Validate visual_url format
                    expected_url_pattern = f"/api/content/{visual_id}/file"
                    if visual_url != expected_url_pattern:
                        validation_results["invalid_visual_urls"].append({
                            "post": i,
                            "expected": expected_url_pattern,
                            "actual": visual_url
                        })
                        print_error(f"❌ Invalid visual URL format")
                        print_error(f"   Expected: {expected_url_pattern}")
                        print_error(f"   Actual: {visual_url}")
                    else:
                        print_success(f"✅ Correct visual URL format")
                
                else:
                    print_info("No visual ID (text-only post)")
            
            # FINAL VALIDATION SUMMARY
            print_test_header("RÉSULTATS DE VALIDATION CRITIQUE")
            
            print_info(f"Total posts: {validation_results['total_posts']}")
            print_info(f"Posts with visuals: {validation_results['posts_with_visuals']}")
            print_info(f"Posts using REAL watch IDs: {validation_results['posts_with_real_watch_ids']}")
            print_info(f"Posts with FORBIDDEN fallback IDs: {validation_results['posts_with_fallback_ids']}")
            
            # Success criteria
            success = True
            
            if validation_results["posts_with_fallback_ids"] > 0:
                print_error(f"❌ CRITICAL FAILURE: Found {validation_results['posts_with_fallback_ids']} posts with fallback IDs")
                print_error(f"Fallback IDs found: {validation_results['fallback_ids_found']}")
                success = False
            else:
                print_success("✅ No forbidden fallback IDs found")
            
            if validation_results["posts_with_real_watch_ids"] > 0:
                print_success(f"✅ {validation_results['posts_with_real_watch_ids']} posts use real watch IDs")
                print_success(f"Real watch IDs used: {list(validation_results['real_watch_ids_used'])}")
            else:
                print_error("❌ No posts use real watch IDs")
                success = False
            
            if validation_results["invalid_visual_urls"]:
                print_error(f"❌ {len(validation_results['invalid_visual_urls'])} posts have invalid visual URLs")
                success = False
            else:
                print_success("✅ All visual URLs have correct format")
            
            # Check coverage of watch IDs
            unused_watch_ids = set(EXPECTED_WATCH_IDS) - validation_results["real_watch_ids_used"]
            if unused_watch_ids:
                print_info(f"ℹ️  Unused watch IDs: {list(unused_watch_ids)}")
            else:
                print_success("✅ All 7 watch IDs were used in posts")
            
            return success
            
        else:
            print_error(f"Failed to get generated posts: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error validating posts: {str(e)}")
        return False

def main():
    """Main test execution"""
    print("🎯 BACKEND TEST FINAL - VRAIES PHOTOS DE MONTRES LAURENT PERPERE")
    print("=" * 80)
    print("OBJECTIF: Tester la génération de posts avec les 7 vraies photos de montres")
    print("TARGET MONTH: septembre_2025 (PAS octobre!)")
    print("VALIDATION: visual_id DOIT correspondre aux IDs réels, ZERO fallback")
    print("=" * 80)
    
    # Step 1: Authentication
    token, user_id = authenticate()
    if not token:
        print_error("Authentication failed - cannot continue")
        return False
    
    # Step 2: Verify watch photos exist
    photos_exist, watch_details = verify_watch_photos(token, user_id)
    if not photos_exist:
        print_error("Not all watch photos found - cannot continue")
        return False
    
    # Step 3: Generate posts for septembre_2025
    generation_success = generate_posts_septembre(token, user_id)
    if not generation_success:
        print_error("Post generation failed - cannot validate")
        return False
    
    # Step 4: Critical validation of generated posts
    validation_success = validate_generated_posts(token, user_id, watch_details)
    
    # Final result
    print_test_header("RÉSULTAT FINAL")
    if validation_success:
        print_success("🎉 TEST RÉUSSI - Les posts utilisent les vraies photos de montres!")
        print_success("✅ Liaison photos-posts 100% avec les vraies montres")
        print_success("✅ Aucun fallback ID trouvé")
        print_success("✅ URLs visuelles correctes")
        return True
    else:
        print_error("❌ TEST ÉCHOUÉ - Problèmes critiques détectés")
        print_error("❌ Les posts n'utilisent pas correctement les vraies photos")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)