#!/usr/bin/env python3
"""
Test d'extraction de contenu web pour diagnostiquer le problème d'analyse
"""
import requests
from bs4 import BeautifulSoup
import sys

def test_website_extraction(url):
    """Test l'extraction de contenu d'un site web"""
    print(f"🔍 Test d'extraction pour: {url}")
    
    try:
        # 1. Requête HTTP
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print("📡 Envoi de la requête HTTP...")
        response = requests.get(url, headers=headers, timeout=15)
        print(f"✅ Status code: {response.status_code}")
        print(f"📄 Taille du contenu: {len(response.text)} caractères")
        
        # 2. Parse avec BeautifulSoup
        print("🔍 Parsing HTML avec BeautifulSoup...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 3. Extraction des métadonnées
        title = soup.find('title')
        title_text = title.get_text().strip() if title else ""
        print(f"📝 Titre: '{title_text}'")
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        desc_text = meta_desc.get('content', '').strip() if meta_desc else ""
        print(f"📝 Description: '{desc_text}'")
        
        # 4. Extraction des headers
        h1_tags = [h1.get_text().strip() for h1 in soup.find_all('h1')]
        h2_tags = [h2.get_text().strip() for h2 in soup.find_all('h2')]
        
        print(f"📝 H1 tags: {h1_tags}")
        print(f"📝 H2 tags: {h2_tags}")
        
        # 5. Extraction du texte principal
        for script in soup(["script", "style"]):
            script.decompose()
        
        text_content = soup.get_text()
        lines = (line.strip() for line in text_content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        print(f"📝 Texte extrait ({len(text)} chars): {text[:200]}...")
        
        return {
            "success": True,
            "title": title_text,
            "description": desc_text,
            "h1_tags": h1_tags,
            "h2_tags": h2_tags,
            "text_content": text[:500],  # Limité pour l'affichage
            "full_length": len(text)
        }
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Test avec différentes URLs
    test_urls = [
        "https://example.com", 
        "https://myownwatch.fr",
    ]
    
    for url in test_urls:
        print("=" * 60)
        result = test_website_extraction(url)
        print(f"Résultat: {result}")
        print()