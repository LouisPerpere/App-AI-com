#!/usr/bin/env python3
"""
Diagnostic simple des vignettes manquantes
Test direct avec curl pour éviter les problèmes de certificats SSL
"""

import subprocess
import json
import sys

# Configuration
BACKEND_URL = "https://post-validator.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

def run_curl(url, method="GET", headers=None, data=None):
    """Execute curl command and return response"""
    cmd = ["curl", "-s"]
    
    if method == "POST":
        cmd.append("-X")
        cmd.append("POST")
    
    if headers:
        for header in headers:
            cmd.extend(["-H", header])
    
    if data:
        cmd.extend(["-d", data])
    
    cmd.append(url)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error: {result.stderr}"
    except Exception as e:
        return f"Exception: {str(e)}"

def main():
    print("🔍 DIAGNOSTIC SIMPLE DES VIGNETTES MANQUANTES")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Utilisateur de test: {TEST_EMAIL}")
    print("=" * 60)
    print()
    
    # Step 1: Authentication
    print("🔐 ÉTAPE 1: Authentification")
    print("-" * 40)
    
    auth_data = json.dumps({"email": TEST_EMAIL, "password": TEST_PASSWORD})
    auth_response = run_curl(
        f"{API_BASE}/auth/login",
        method="POST",
        headers=["Content-Type: application/json"],
        data=auth_data
    )
    
    try:
        auth_json = json.loads(auth_response)
        access_token = auth_json.get("access_token")
        user_id = auth_json.get("user_id")
        
        if access_token:
            print(f"✅ Authentification réussie")
            print(f"   User ID: {user_id}")
            print(f"   Token: {access_token[:20]}...")
        else:
            print(f"❌ Authentification échouée: {auth_response}")
            return False
    except Exception as e:
        print(f"❌ Erreur d'authentification: {e}")
        print(f"   Response: {auth_response}")
        return False
    
    print()
    
    # Step 2: Test GET /api/content/pending
    print("📋 ÉTAPE 2: Test GET /api/content/pending")
    print("-" * 40)
    
    content_response = run_curl(
        f"{API_BASE}/content/pending?limit=10",
        headers=[f"Authorization: Bearer {access_token}"]
    )
    
    try:
        content_json = json.loads(content_response)
        content_list = content_json.get("content", [])
        total = content_json.get("total", 0)
        
        print(f"✅ Récupération du contenu réussie")
        print(f"   Total fichiers: {total}")
        print(f"   Fichiers récupérés: {len(content_list)}")
        
        # Analyze thumb_url patterns
        thumb_url_analysis = {
            "with_thumb_url": 0,
            "without_thumb_url": 0,
            "absolute_urls": 0,
            "relative_urls": 0,
            "webp_extensions": 0,
            "other_extensions": 0,
            "claire_marcus_domain": 0,
            "libfusion_domain": 0,
            "examples": []
        }
        
        for item in content_list:
            thumb_url = item.get("thumb_url")
            filename = item.get("filename", "unknown")
            file_id = item.get("id", "unknown")
            
            if thumb_url:
                thumb_url_analysis["with_thumb_url"] += 1
                
                # Check if absolute or relative URL
                if thumb_url.startswith("http"):
                    thumb_url_analysis["absolute_urls"] += 1
                    
                    # Check domain
                    if "claire-marcus.com" in thumb_url:
                        thumb_url_analysis["claire_marcus_domain"] += 1
                    elif "libfusion.preview.emergentagent.com" in thumb_url:
                        thumb_url_analysis["libfusion_domain"] += 1
                else:
                    thumb_url_analysis["relative_urls"] += 1
                
                # Check extension
                if thumb_url.endswith(".webp"):
                    thumb_url_analysis["webp_extensions"] += 1
                else:
                    thumb_url_analysis["other_extensions"] += 1
                
                # Store examples
                if len(thumb_url_analysis["examples"]) < 5:
                    thumb_url_analysis["examples"].append({
                        "file_id": file_id,
                        "filename": filename,
                        "thumb_url": thumb_url
                    })
            else:
                thumb_url_analysis["without_thumb_url"] += 1
        
        print()
        print("📊 ANALYSE DES THUMB_URL:")
        print(f"   Avec thumb_url: {thumb_url_analysis['with_thumb_url']}")
        print(f"   Sans thumb_url: {thumb_url_analysis['without_thumb_url']}")
        print(f"   URLs absolues: {thumb_url_analysis['absolute_urls']}")
        print(f"   URLs relatives: {thumb_url_analysis['relative_urls']}")
        print(f"   Extensions .webp: {thumb_url_analysis['webp_extensions']}")
        print(f"   Autres extensions: {thumb_url_analysis['other_extensions']}")
        print(f"   Domaine claire-marcus.com: {thumb_url_analysis['claire_marcus_domain']}")
        print(f"   Domaine libfusion: {thumb_url_analysis['libfusion_domain']}")
        
        print()
        print("📝 EXEMPLES DE THUMB_URL:")
        for i, example in enumerate(thumb_url_analysis["examples"], 1):
            print(f"   {i}. File: {example['filename']}")
            print(f"      ID: {example['file_id']}")
            print(f"      thumb_url: {example['thumb_url']}")
            
            # Analyze URL format
            thumb_url = example['thumb_url']
            if thumb_url.startswith("https://claire-marcus.com/uploads/thumbs/"):
                url_type = "Absolue (claire-marcus.com)"
            elif thumb_url.startswith("https://post-validator.preview.emergentagent.com/uploads/thumbs/"):
                url_type = "Absolue (libfusion)"
            elif thumb_url.startswith("/uploads/thumbs/"):
                url_type = "Relative"
            else:
                url_type = "Format non standard"
            
            extension = thumb_url.split(".")[-1] if "." in thumb_url else "none"
            print(f"      Type: {url_type}")
            print(f"      Extension: {extension}")
            print()
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse du contenu: {e}")
        print(f"   Response: {content_response}")
        return False
    
    # Step 3: Test thumbnails status
    print("📊 ÉTAPE 3: Test GET /api/content/thumbnails/status")
    print("-" * 40)
    
    status_response = run_curl(
        f"{API_BASE}/content/thumbnails/status",
        headers=[f"Authorization: Bearer {access_token}"]
    )
    
    try:
        status_json = json.loads(status_response)
        
        print(f"✅ Statut des vignettes récupéré")
        print(f"   Total fichiers: {status_json.get('total_files', 0)}")
        print(f"   Avec vignettes: {status_json.get('with_thumbnails', 0)}")
        print(f"   Vignettes manquantes: {status_json.get('missing_thumbnails', 0)}")
        print(f"   Pourcentage complet: {status_json.get('completion_percentage', 0)}%")
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération du statut: {e}")
        print(f"   Response: {status_response}")
    
    print()
    
    # Step 4: Test thumbnail accessibility
    print("🌐 ÉTAPE 4: Test d'accessibilité des vignettes")
    print("-" * 40)
    
    if thumb_url_analysis["examples"]:
        for i, example in enumerate(thumb_url_analysis["examples"][:3], 1):
            thumb_url = example["thumb_url"]
            filename = example["filename"]
            
            print(f"   Test {i}: {filename}")
            print(f"   URL: {thumb_url}")
            
            # Test accessibility
            test_response = run_curl(thumb_url)
            
            if "Error:" in test_response or "Exception:" in test_response:
                print(f"   ❌ Non accessible: {test_response}")
            elif len(test_response) > 100:  # Assume it's binary image data
                print(f"   ✅ Accessible (taille: {len(test_response)} bytes)")
            else:
                print(f"   ⚠️ Réponse inattendue: {test_response[:100]}...")
            print()
    
    print("🎯 DIAGNOSTIC TERMINÉ")
    print()
    
    # Conclusions
    print("📝 CONCLUSIONS:")
    if thumb_url_analysis["with_thumb_url"] > 0:
        if thumb_url_analysis["webp_extensions"] == thumb_url_analysis["with_thumb_url"]:
            print("✅ Toutes les vignettes utilisent l'extension .webp")
        else:
            print("⚠️ Certaines vignettes n'utilisent pas l'extension .webp")
        
        if thumb_url_analysis["absolute_urls"] == thumb_url_analysis["with_thumb_url"]:
            print("✅ Toutes les thumb_url sont des URLs absolues")
        else:
            print("⚠️ Certaines thumb_url sont relatives")
        
        if thumb_url_analysis["claire_marcus_domain"] > 0 and thumb_url_analysis["libfusion_domain"] > 0:
            print("⚠️ Incohérence: URLs pointent vers différents domaines")
            print(f"   - claire-marcus.com: {thumb_url_analysis['claire_marcus_domain']}")
            print(f"   - libfusion: {thumb_url_analysis['libfusion_domain']}")
        elif thumb_url_analysis["claire_marcus_domain"] > 0:
            print("✅ Toutes les thumb_url pointent vers claire-marcus.com")
        elif thumb_url_analysis["libfusion_domain"] > 0:
            print("✅ Toutes les thumb_url pointent vers libfusion")
    else:
        print("❌ Aucune thumb_url trouvée")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)