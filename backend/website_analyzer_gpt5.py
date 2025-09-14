"""
Website Analyzer avec Orchestration Double IA
GPT-4o : Analyse business/exécution (concis, structuré, actionnable)
Claude Sonnet 4 : Analyse narrative/inspiration (storytelling, profondeur)
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, HttpUrl
import uuid
import requests
from bs4 import BeautifulSoup
import os
import logging
import json
import time
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pathlib import Path
from dotenv import load_dotenv
from fastapi import Header
from typing import Optional
import re

# Import du système LLM backup pour l'orchestration
from llm_backup_system import LLMBackupSystem

# EXPLICIT .env loading to ensure JWT variables are available
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)
print(f"✅ Website Analyzer: Loaded .env from {env_path}")

# Verify JWT variables after loading .env
import os
jwt_secret = os.environ.get('JWT_SECRET_KEY')
if jwt_secret:
    print(f"✅ JWT_SECRET_KEY loaded: {jwt_secret[:20]}...")
else:
    print("❌ JWT_SECRET_KEY not found after loading .env")

# Import OpenAI directly (no emergentintegrations)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
    print("✅ OpenAI module imported successfully")
except ImportError as e:
    print(f"❌ OpenAI not available: {e}")
    OPENAI_AVAILABLE = False
    OpenAI = None

# Simple User model for compatibility
class User:
    def __init__(self, user_id: str, email: str = ""):
        self.id = user_id
        self.email = email

# Import robust authentication from shared security module
from security import get_current_user_id_robust

print("✅ Website Analyzer using shared security authentication")

def get_current_user_id(authorization: str = Header(None)) -> str:
    """Extract user ID from JWT token - compatible with server.py"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    token = authorization.replace("Bearer ", "")
    # In this module, always use shared robust decoder where possible
    return get_current_user_id_robust(authorization=f"Bearer {token}")

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# API Key configuration - Use personal OpenAI API key as requested
API_KEY = os.environ.get('OPENAI_API_KEY')  # Use personal OpenAI key
if API_KEY:
    print(f"✅ Personal OpenAI API key loaded successfully")
else:
    print("❌ No OPENAI_API_KEY found - check .env configuration")

if not API_KEY:
    logging.warning("No API key found for GPT analysis. Website analysis will use fallback mode.")

# MongoDB connection with URL encoding fix
mongo_url = os.environ.get('MONGO_URL')

# Fix MongoDB URL encoding for special characters (same as in database.py)
if mongo_url and ("mongodb+srv://" in mongo_url or "@" in mongo_url):
    try:
        from urllib.parse import urlparse, urlunparse, quote_plus
        parsed = urlparse(mongo_url)
        if parsed.username and parsed.password:
            # Re-encode username and password
            encoded_username = quote_plus(parsed.username)
            encoded_password = quote_plus(parsed.password)
            # Reconstruct URL with encoded credentials
            netloc = f"{encoded_username}:{encoded_password}@{parsed.hostname}"
            if parsed.port:
                netloc += f":{parsed.port}"
            mongo_url = urlunparse((
                parsed.scheme, netloc, parsed.path, 
                parsed.params, parsed.query, parsed.fragment
            ))
            print(f"✅ Website Analyzer MongoDB URL credentials encoded for RFC 3986 compliance")
    except Exception as e:
        print(f"⚠️ Website Analyzer MongoDB URL encoding warning: {e}")

mongo_client = AsyncIOMotorClient(mongo_url)
db = mongo_client[os.environ.get('DB_NAME', 'claire_marcus')]

# Router setup
website_router = APIRouter(prefix="/website")

# Models
class WebsiteAnalysisRequest(BaseModel):
    # Accept plain string so we can normalize missing scheme (http/https) ourselves
    website_url: str
    force_reanalysis: bool = False

class WebsiteData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    business_id: str
    website_url: str
    content_text: str
    meta_description: str = ""
    meta_title: str = ""
    h1_tags: list = Field(default_factory=list)
    h2_tags: list = Field(default_factory=list)
    analysis_summary: str = ""
    key_topics: list = Field(default_factory=list)
    brand_tone: str = ""
    target_audience: str = ""
    main_services: list = Field(default_factory=list)
    content_suggestions: list = Field(default_factory=list)
    last_analyzed: datetime = Field(default_factory=datetime.utcnow)
    next_analysis_due: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=30))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

def extract_website_content_with_limits(url):
    """Extract content with strict limits (timeout, size, content-type) for robustness"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; ClaireMarcusBot/1.0; +https://claire-marcus.com)'
    }
    try:
        r = requests.get(url, headers=headers, timeout=12, allow_redirects=True, stream=True)
    except requests.exceptions.Timeout:
        return {"error": (504, "Le site met trop de temps à répondre (timeout).")}
    except requests.exceptions.ConnectionError:
        return {"error": (502, "Impossible de se connecter au site. Vérifiez l'URL.")}
    except requests.exceptions.RequestException as e:
        return {"error": (502, f"Erreur d'accès au site: {str(e)}")}

    ct = r.headers.get("Content-Type", "").lower()
    if "text/html" not in ct:
        return {"error": (415, f"Contenu non supporté ({ct or 'inconnu'}). Veuillez fournir une URL HTML.")}

    chunks, size = [], 0
    for ch in r.iter_content(8192):
        if not ch:
            break
        size += len(ch)
        if size > 2_000_000:  # 2MB
            break
        chunks.append(ch)
    html = b"".join(chunks)

    try:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = re.sub(r"\s+", " ", soup.get_text(separator=' ', strip=True))[:20000]
        title_tag = soup.find('title')
        title_text = title_tag.get_text().strip() if title_tag else "Site Web"
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        description = desc_tag.get('content', '').strip() if desc_tag else ""
        h1_tags = [h1.get_text(strip=True) for h1 in soup.find_all('h1')][:10]
        h2_tags = [h2.get_text(strip=True) for h2 in soup.find_all('h2')][:20]
        return {
            "content_text": text,
            "meta_title": title_text,
            "meta_description": description,
            "h1_tags": h1_tags,
            "h2_tags": h2_tags
        }
    except Exception as e:
        return {"error": (422, f"Impossible d'analyser le HTML de la page: {str(e)}")}

async def analyze_with_gpt4o_and_claude_backup(content_data: dict, website_url: str) -> dict:
    """Analyze website content using GPT-4o with Claude Sonnet 4 backup"""
    logging.info(f"🔥 analyze_with_gpt4o_and_claude_backup CALLED for {website_url}")
    
    try:
        # Utiliser le système de backup LLM unifié
        from llm_backup_system import llm_backup
        
        result = await llm_backup.analyze_website_content(content_data, website_url)
        logging.info(f"✅ LLM backup analysis completed for {website_url}")
        
        return result
        
    except Exception as e:
        logging.error(f"❌ LLM backup system failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback ultime
        return create_fallback_analysis(content_data, website_url, "llm_backup_failed")


# Garder l'ancienne fonction pour compatibilité, mais utiliser le backup
async def analyze_with_gpt4o(content_data: dict, website_url: str) -> dict:
    """Analyze website content using GPT-4o via OpenAI direct integration (now with Claude backup)"""
    return await analyze_with_gpt4o_and_claude_backup(content_data, website_url)

async def analyze_with_claude_storytelling(content_data: dict, website_url: str) -> dict:
    """Analyse storytelling avec Claude Sonnet 4 - dimension narrative et inspiration"""
    
    # Initialiser le système LLM
    from llm_backup_system import LLMBackupSystem
    llm_system = LLMBackupSystem()
    
    # Préparer le contenu pour l'analyse storytelling
    title = content_data.get('title', content_data.get('meta_title', ''))
    description = content_data.get('description', content_data.get('meta_description', ''))
    text_content = content_data.get('text_content', content_data.get('content_text', ''))
    h1_tags = content_data.get('h1_tags', [])
    h2_tags = content_data.get('h2_tags', [])
    pages_analyzed = content_data.get('pages_analyzed', [])
    
    # Construire le contenu pour analyse narrative
    content_summary = f"""
    Site web: {website_url}
    Titre: {title or 'Non défini'}
    Description: {description or 'Non définie'}
    H1: {h1_tags}
    H2: {h2_tags[:10]}
    Pages analysées: {len(pages_analyzed)} pages
    Contenu: {text_content[:3000] if text_content else 'Non disponible'}
    """
    
    # Prompt spécialisé pour Claude Sonnet 4 (Storytelling)
    storytelling_prompt = f"""Tu es un expert en storytelling de marque et stratégie narrative. Analyse ce site web pour révéler sa dimension émotionnelle, son potentiel narratif et ses opportunités de storytelling.

Contenu du site web à analyser :
{content_summary}

Fournis une analyse STORYTELLING INSPIRANTE selon ce format :

**VISION ET STORYTELLING**
[Un paragraphe de 60-80 mots qui raconte l'HISTOIRE de la marque, son essence émotionnelle, ce qu'elle représente vraiment au-delà de ses services. Utilise un ton engageant et évocateur.]

**POSITIONNEMENT NARRATIF**
[Un paragraphe de 50-70 mots qui explique le TERRITOIRE ÉMOTIONNEL de la marque, son univers narratif, comment elle touche son audience. Mets l'accent sur l'aspirationnel.]

**AXES ÉDITORIAUX STORYTELLING**
1. [Axe narratif 1] – [15-20 mots expliquant le potentiel storytelling]
2. [Axe narratif 2] – [15-20 mots sur l'opportunité émotionnelle] 
3. [Axe narratif 3] – [15-20 mots sur l'angle humain unique]
4. [Axe narratif 4] – [15-20 mots sur la dimension aspirationnelle]

**CONTENUS NARRATIFS RECOMMANDÉS**
• [Format storytelling 1 : angle émotionnel spécifique]
• [Format storytelling 2 : angle témoignage transformé]
• [Format storytelling 3 : angle communauté/appartenance]
• [Format storytelling 4 : angle expertise avec dimension humaine]

IMPORTANT : Sois INSPIRANT, ÉVOCATEUR et axé sur l'ÉMOTION. Révèle le potentiel narratif et storytelling de la marque."""

    try:
        # Messages pour Claude Sonnet 4
        messages = [
            {
                "role": "system",
                "content": "Tu es un expert en storytelling de marque et stratégie narrative. Tu révèles la dimension émotionnelle et le potentiel narratif des marques."
            },
            {
                "role": "user",
                "content": storytelling_prompt
            }
        ]
        
        # Utiliser Claude Sonnet 4 via le système LLM avec stratégie storytelling
        response = await llm_system.generate_completion_with_strategy(
            messages=messages,
            business_objective="communaute",  # Force narrative/community focus
            brand_tone="storytelling",  # Force Claude primary selection
            platform="instagram",
            temperature=0.8,  # Plus élevé pour plus de créativité narrative
            max_tokens=1200
        )
        
        return {
            "storytelling_analysis": response,
            "ai_used": "Claude Sonnet 4",
            "analysis_type": "storytelling_narrative",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logging.error(f"❌ Claude storytelling analysis failed: {e}")
        
        # Fallback storytelling basique
        return {
            "storytelling_analysis": f"""**VISION ET STORYTELLING**
{title or 'Cette marque'} représente une approche authentique et personnalisée dans son domaine. Elle incarne les valeurs de qualité et de proximité avec ses clients.

**POSITIONNEMENT NARRATIF**
La marque se positionne sur un territoire d'expertise et de confiance, créant une relation privilégiée avec son audience à travers une communication authentique.

**AXES ÉDITORIAUX STORYTELLING**
1. Authenticité – Montrer les coulisses et la réalité du métier
2. Expertise – Partager les connaissances et savoir-faire unique
3. Communauté – Créer du lien avec les clients et témoignages
4. Innovation – Présenter les nouveautés avec dimension humaine

**CONTENUS NARRATIFS RECOMMANDÉS**
• Stories behind-the-scenes : Montrer l'envers du décor
• Témoignages clients transformés en récits inspirants  
• Posts éducatifs avec storytelling autour de l'expertise
• Contenus communauté créant du lien et de l'appartenance""",
            "ai_used": "Fallback",
            "analysis_type": "storytelling_fallback",
            "timestamp": datetime.utcnow().isoformat()
        }


async def analyze_with_gpt4o_only(content_data: dict, website_url: str) -> dict:
    """Analyse approfondie avec GPT-4o - exploitation complète de toutes les pages"""
    if not OPENAI_AVAILABLE or not API_KEY:
        logging.warning("OpenAI not available, using fallback analysis")
        return create_fallback_analysis(content_data, website_url, "openai_unavailable")
    
    # Extraire les données multi-pages avec détails approfondis
    title = content_data.get('title', content_data.get('meta_title', ''))
    description = content_data.get('description', content_data.get('meta_description', ''))
    text_content = content_data.get('text_content', content_data.get('content_text', ''))
    h1_tags = content_data.get('h1_tags', [])
    h2_tags = content_data.get('h2_tags', [])
    pages_analyzed = content_data.get('pages_analyzed', [])
    
    # Construire une analyse détaillée par page
    pages_details = []
    homepage_content = ""
    
    for page_info in pages_analyzed:
        page_url = page_info.get('url', '')
        page_title = page_info.get('title', '')
        page_content = page_info.get('content', '')
        page_h1 = page_info.get('h1_tags', [])
        page_h2 = page_info.get('h2_tags', [])
        
        # Identifier le type de page (éviter les pages techniques)
        url_lower = page_url.lower()
        is_technical = any(tech in url_lower for tech in [
            '/legal', '/privacy', '/terms', '/cookies', '/sitemap', 
            '/robots.txt', '/404', '/admin', '/login', '/register'
        ])
        
        if not is_technical and page_content:
            # Classifier la page
            page_type = "homepage" if page_url == website_url else "other"
            if any(keyword in url_lower for keyword in ['/product', '/service', '/offer']):
                page_type = "product_service"
            elif any(keyword in url_lower for keyword in ['/blog', '/news', '/article']):
                page_type = "blog_content"
            elif any(keyword in url_lower for keyword in ['/about', '/team', '/company']):
                page_type = "about_company"
            elif any(keyword in url_lower for keyword in ['/contact', '/support']):
                page_type = "contact_support"
            
            if page_type == "homepage":
                homepage_content = f"""
HOMEPAGE ({page_url}):
Titre: {page_title}
H1: {', '.join(page_h1[:3])}
H2: {', '.join(page_h2[:5])}
Contenu: {page_content[:1500]}
"""
            else:
                page_detail = f"""
PAGE {page_type.upper()} ({page_url}):
Titre: {page_title}
H1: {', '.join(page_h1[:3])}
H2: {', '.join(page_h2[:5])}
Contenu détaillé: {page_content[:1200]}
"""
                pages_details.append(page_detail)
    
    # Construire le contenu enrichi pour l'analyse
    enriched_content = f"""
SITE WEB: {website_url}
TITRE PRINCIPAL: {title}
DESCRIPTION META: {description}

{homepage_content}

PAGES DÉTAILLÉES ANALYSÉES ({len(pages_details)} pages):
{''.join(pages_details)}

STRUCTURE GLOBALE:
H1 de toutes les pages: {', '.join(h1_tags[:10])}
H2 de toutes les pages: {', '.join(h2_tags[:15])}

CONTENU TEXTUEL GLOBAL (pour contexte):
{text_content[:2000]}
"""
    
    # Prompt enrichi pour analyse approfondie
    enhanced_prompt = f"""Tu es un expert en analyse web et stratégie digitale. Analyse ce site web EN PROFONDEUR en exploitant TOUTES les pages pour extraire un MAXIMUM d'informations détaillées.

CONTENU COMPLET DU SITE AVEC DÉTAILS PAR PAGE :
{enriched_content}

Fournis une analyse APPROFONDIE et STRUCTURÉE selon ce format JSON :

{{
    "analysis_summary": "Un résumé détaillé et complet de l'entreprise (300-400 mots) incluant : QUI ils sont, CE QU'ILS FONT exactement, COMMENT ils le font, leurs SPÉCIALITÉS, leur APPROCHE, leurs VALEURS, leur EXPÉRIENCE",
    
    "key_topics": ["topic1", "topic2", "topic3", "topic4", "topic5", "topic6", "topic7"],
    
    "brand_tone": "le ton de communication dominant (professionnel/décontracté/premium/accessible/expert/etc.)",
    
    "target_audience": "description PRÉCISE du public cible avec démographie, besoins, motivations, comportements",
    
    "main_services": ["service détaillé 1", "service détaillé 2", "service détaillé 3", "service détaillé 4"],
    
    "content_suggestions": [
        "suggestion 1 - basée sur les services spécifiques identifiés", 
        "suggestion 2 - basée sur l'expertise détectée",
        "suggestion 3 - basée sur les produits/projets trouvés",
        "suggestion 4 - basée sur les valeurs/approche de l'entreprise",
        "suggestion 5 - basée sur le public cible identifié"
    ],
    
    "products_services_details": "Détails PRÉCIS sur tous les produits/services trouvés avec caractéristiques, tarifs si mentionnés, processus, spécialités",
    
    "company_expertise": "Domaines d'expertise spécifiques, compétences uniques, années d'expérience, certifications, références",
    
    "unique_value_proposition": "Ce qui différencie vraiment cette entreprise de ses concurrents selon les pages analysées"
}}

INSTRUCTIONS CRITIQUES :
- Exploite CHAQUE page analysée pour extraire des détails spécifiques
- Identifie TOUS les services/produits mentionnés avec leurs détails
- Relève les SPÉCIALITÉS, PROCESSUS, MÉTHODES de travail
- Note les RÉFÉRENCES, TÉMOIGNAGES, RÉALISATIONS trouvées
- Extrais les informations sur l'ÉQUIPE, l'HISTOIRE, les VALEURS
- Sois PRÉCIS et FACTUEL, évite les généralités
- Utilise les mots-clés et termes EXACTS trouvés sur le site"""

    try:
        client = OpenAI(api_key=API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un expert en analyse web approfondie. Tu extrais le maximum d'informations détaillées de chaque page d'un site. Réponds UNIQUEMENT en JSON valide avec tous les détails trouvés."
                },
                {
                    "role": "user",
                    "content": enhanced_prompt
                }
            ],
            temperature=0.5,  # Équilibre entre précision et richesse
            max_tokens=3000   # Plus de tokens pour plus de détails
        )
        
        raw_response = response.choices[0].message.content
        
        # Parse JSON avec gestion des erreurs
        clean_response = raw_response.strip()
        if clean_response.startswith('```json'):
            clean_response = clean_response[7:]
        if clean_response.endswith('```'):
            clean_response = clean_response[:-3]
        
        result = json.loads(clean_response.strip())
        
        # Ajouter des métadonnées sur l'analyse approfondie
        result["analysis_depth"] = "enhanced_multi_page"
        result["pages_analyzed_count"] = len(pages_analyzed)
        result["non_technical_pages_count"] = len(pages_details)
        
        logging.info(f"✅ GPT-4o enhanced analysis completed for {website_url} - {len(pages_details)} pages in depth")
        return result
        
    except Exception as e:
        logging.error(f"❌ GPT-4o enhanced analysis failed: {e}")
        return create_fallback_analysis(content_data, website_url, f"gpt4o_enhanced_error: {str(e)}")

def create_fallback_analysis(content_data: dict, website_url: str, reason: str = "fallback") -> dict:
    title = content_data.get('meta_title', '').strip() or website_url
    description = content_data.get('meta_description', '').strip()
    h1_tags = content_data.get('h1_tags', [])
    content_text = content_data.get('content_text', '')[:800].strip().lower()
    logging.info(f"🔄 Using fallback analysis for {website_url} (reason: {reason})")
    # Generic fallback
    main_topic = (h1_tags[0] if h1_tags else (title.split()[0] if title else "entreprise")).lower()
    return {
        "analysis_summary": f"Entreprise analysée : {title}. {description[:100] if description else ''}",
        "key_topics": [main_topic, "services", "qualité"],
        "brand_tone": "professionnel",
        "target_audience": "grand public",
        "main_services": ["services"],
        "content_suggestions": [
            "Présenter vos services",
            "Partager des témoignages",
            "Publier des conseils utiles"
        ]
    }

@website_router.get("/analysis")
def get_website_analysis(user_id: str = Depends(get_current_user_id_robust)):
    """Get latest website analysis for user"""
    try:
        print(f"🔍 Getting website analysis for user: {user_id}")
        import pymongo
        mongo_url = os.environ.get("MONGO_URL")
        client = pymongo.MongoClient(mongo_url)
        dbp = client.claire_marcus
        collection = dbp.website_analyses
        latest = collection.find_one({"user_id": user_id}, sort=[("created_at", -1)])
        if latest:
            analysis_data = {
                "analysis_summary": latest.get("analysis_summary", ""),
                "key_topics": latest.get("key_topics", []),
                "brand_tone": latest.get("brand_tone", "professional"),
                "target_audience": latest.get("target_audience", ""),
                "main_services": latest.get("main_services", []),
                "content_suggestions": latest.get("content_suggestions", []),
                "website_url": latest.get("website_url", ""),
                "created_at": latest.get("created_at", ""),
                "next_analysis_due": latest.get("next_analysis_due", "")
            }
            client.close()
            return {"analysis": analysis_data}
        client.close()
        return {"analysis": None}
    except Exception as e:
        print(f"❌ Error getting website analysis: {e}")
        return {"analysis": None}

def discover_website_pages(base_url: str, max_pages: int = 5) -> list:
    """Discover important pages of a website"""
    try:
        from urllib.parse import urljoin, urlparse
        import requests
        from bs4 import BeautifulSoup
        
        print(f"🔍 Discovering pages for: {base_url}")
        discovered_pages = [base_url]  # Always include homepage
        
        # Get homepage to find links
        try:
            response = requests.get(base_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; Website Analyzer Bot)'
            })
            if response.status_code != 200:
                return discovered_pages
                
            soup = BeautifulSoup(response.content, 'html.parser')
            base_domain = urlparse(base_url).netloc
            
            # Keywords to look for in URLs and link text
            important_keywords = [
                'about', 'qui-sommes-nous', 'notre-histoire', 'entreprise',
                'services', 'produits', 'solutions', 'offres',
                'contact', 'contacts', 'nous-contacter',
                'concept', 'notre-concept', 'philosophie',
                'portfolio', 'realisations', 'projets',
                'equipe', 'team', 'notre-equipe'
            ]
            
            # Skip technical pages
            skip_keywords = [
                'mentions-legales', 'legal', 'privacy', 'cookies', 'cgv', 'cgu',
                'terms', 'politique', 'sitemap', 'admin', 'login', 'wp-',
                'feed', 'rss', 'xml'
            ]
            
            # Find all links
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '').lower()
                text = link.get_text(strip=True).lower()
                
                # Skip empty links, anchors, external links
                if not href or href.startswith('#') or href.startswith('mailto:'):
                    continue
                
                # Build full URL
                full_url = urljoin(base_url, href)
                parsed_url = urlparse(full_url)
                
                # Skip external domains
                if parsed_url.netloc != base_domain:
                    continue
                
                # Skip technical pages
                if any(skip in href or skip in text for skip in skip_keywords):
                    continue
                
                # Check if it's an important page
                if any(keyword in href or keyword in text for keyword in important_keywords):
                    if full_url not in discovered_pages and len(discovered_pages) < max_pages:
                        discovered_pages.append(full_url)
                        print(f"📄 Found important page: {full_url}")
            
        except Exception as e:
            print(f"⚠️ Error discovering pages: {e}")
            
        return discovered_pages[:max_pages]
        
    except Exception as e:
        print(f"❌ Page discovery failed: {e}")
        return [base_url]

async def analyze_multiple_pages(pages: list, base_url: str) -> dict:
    """Analyze multiple pages and combine insights"""
    try:
        all_content = {
            "title": "",
            "description": "",
            "text_content": "",
            "h1_tags": [],
            "h2_tags": [],
            "pages_analyzed": []
        }
        
        for page_url in pages:
            try:
                print(f"📄 Analyzing page: {page_url}")
                extracted = extract_website_content_with_limits(page_url)
                
                if "error" not in extracted:
                    # Combine content from all pages
                    if not all_content["title"] and extracted.get("title"):
                        all_content["title"] = extracted["title"]
                    
                    if not all_content["description"] and extracted.get("description"):
                        all_content["description"] = extracted["description"]
                    
                    # Combine text content (with limits)
                    page_text = extracted.get("text_content", "")[:2000]  # Limit per page
                    all_content["text_content"] += f"\n\n=== Page: {page_url} ===\n{page_text}"
                    
                    # Combine headers
                    all_content["h1_tags"].extend(extracted.get("h1_tags", []))
                    all_content["h2_tags"].extend(extracted.get("h2_tags", []))
                    
                    all_content["pages_analyzed"].append({
                        "url": page_url,
                        "title": extracted.get("title", ""),
                        "status": "analyzed"
                    })
                else:
                    all_content["pages_analyzed"].append({
                        "url": page_url,
                        "title": "",
                        "status": "error"
                    })
                    
            except Exception as e:
                print(f"⚠️ Error analyzing {page_url}: {e}")
                all_content["pages_analyzed"].append({
                    "url": page_url,
                    "status": "error"
                })
        
        # Limit total content to avoid GPT limits
        all_content["text_content"] = all_content["text_content"][:8000]
        all_content["h1_tags"] = list(set(all_content["h1_tags"]))[:20]
        all_content["h2_tags"] = list(set(all_content["h2_tags"]))[:30]
        
        return all_content
        
    except Exception as e:
        print(f"❌ Multi-page analysis failed: {e}")
        # Fallback to single page
        return extract_website_content_with_limits(base_url)

@website_router.post("/force-real-analysis")
async def force_real_gpt4o_analysis(
    request: WebsiteAnalysisRequest,
    user_id: str = Depends(get_current_user_id_robust)
):
    """FORCE l'analyse GPT-4o réelle sans cache - ENDPOINT DE PRODUCTION"""
    from fastapi.responses import JSONResponse
    import uuid
    
    url = (request.website_url or "").strip()
    if not re.match(r'^https?://', url, re.IGNORECASE):
        url = 'https://' + url
    
    # Headers anti-cache
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
        "X-Bypass-Cache": "true",
        "X-Force-Refresh": str(uuid.uuid4())
    }
    
    try:
        print(f"🔥 FORCE REAL ANALYSIS - GPT-4o pour: {url}")
        
        # Extraction rapide du contenu
        content_data = extract_website_content_with_limits(url)
        
        if "error" in content_data:
            print(f"❌ Erreur extraction: {content_data['error']}")
            # Utiliser des données minimales pour forcer l'analyse GPT
            content_data = {
                'meta_title': f'Site web {url}',
                'meta_description': 'Analyse forcée',
                'h1_tags': ['Contenu principal'],
                'h2_tags': [],
                'text_content': f'Analyse du site web {url} demandée par l\'utilisateur.'
            }
        
        print(f"✅ Contenu extrait, titre: {content_data.get('meta_title', 'N/A')}")
        
        # APPEL DIRECT à analyze_with_gpt4o
        print(f"🚀 Appel DIRECT analyze_with_gpt4o...")
        analysis_result = await analyze_with_gpt4o(content_data, url)
        
        print(f"✅ Analyse terminée, type: {type(analysis_result)}")
        
        # Réponse avec timestamp unique pour éviter le cache
        response_data = {
            "status": "force_analyzed",
            "message": f"Analyse GPT-4o forcée avec succès à {datetime.datetime.now().isoformat()}",
            "url": url,
            "forced_analysis": True,
            "cache_bypass": True,
            **analysis_result
        }
        
        return JSONResponse(
            content=response_data,
            headers=headers
        )
        
    except Exception as e:
        print(f"❌ Erreur force analysis: {e}")
        import traceback
        traceback.print_exc()
        
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Force analysis failed: {str(e)}",
                "force_analysis": True
            },
            headers=headers
        )


@website_router.post("/test-smart-generation")
async def test_smart_generation(
    request: dict,
    user_id: str = Depends(get_current_user_id_robust)
):
    """Test de la nouvelle génération intelligente avec sélection LLM"""
    
    business_objective = request.get('business_objective', 'equilibre')
    brand_tone = request.get('brand_tone', 'professionnel')
    platform = request.get('platform', 'instagram')
    business_context = request.get('business_context', 'My Own Watch - montres de luxe')
    
    try:
        from llm_backup_system import llm_backup
        
        messages = [
            {
                "role": "system", 
                "content": "Tu es un expert en réseaux sociaux. Crée du contenu authentique et engageant."
            },
            {
                "role": "user",
                "content": f"""Crée un post Instagram pour ce business. Format JSON exact:
                {{
                    "title": "Titre accrocheur",
                    "text": "Texte du post (150 mots max, 2-3 emojis max)",
                    "hashtags": ["hashtag1", "hashtag2", "hashtag3"]
                }}
                
                Business: {business_context}
                Objectif: {business_objective}
                Ton: {brand_tone}
                Plateforme: {platform}
                """
            }
        ]
        
        # Génération avec stratégie intelligente
        response_text = await llm_backup.generate_completion_with_strategy(
            messages=messages,
            business_objective=business_objective,
            brand_tone=brand_tone, 
            platform=platform,
            max_tokens=500
        )
        
        # Parse le JSON
        import json
        clean_response = response_text.strip()
        if clean_response.startswith('```json'):
            clean_response = clean_response[7:]
        if clean_response.endswith('```'):
            clean_response = clean_response[:-3]
        
        parsed_post = json.loads(clean_response.strip())
        
        # Informations sur la sélection LLM
        primary_llm, backup_llm = llm_backup.select_primary_llm(business_objective, brand_tone, platform)
        
        return {
            "status": "success",
            "strategy": {
                "business_objective": business_objective,
                "brand_tone": brand_tone,
                "platform": platform,
                "primary_llm": primary_llm,
                "backup_llm": backup_llm
            },
            "generated_post": parsed_post,
            "raw_response": response_text
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "strategy": {
                "business_objective": business_objective,
                "brand_tone": brand_tone,
                "platform": platform
            }
        }


@website_router.post("/compare-analysis")
async def compare_openai_vs_claude(
    request: WebsiteAnalysisRequest,
    user_id: str = Depends(get_current_user_id_robust)
):
    """Compare OpenAI GPT-4o vs Claude Sonnet 4 analysis side by side"""
    from fastapi.responses import JSONResponse
    
    url = (request.website_url or "").strip()
    if not re.match(r'^https?://', url, re.IGNORECASE):
        url = 'https://' + url
    
    print(f"🔍 COMPARISON: OpenAI vs Claude for {url}")
    
    # Extraction du contenu une seule fois
    content_data = extract_website_content_with_limits(url)
    
    if "error" in content_data:
        content_data = {
            'meta_title': f'Site web {url}',
            'meta_description': 'Contenu pour comparaison',
            'h1_tags': ['Titre principal'],
            'h2_tags': [],
            'text_content': f'Contenu du site web {url} pour comparaison OpenAI vs Claude.'
        }
    
    results = {
        "website_url": url,
        "comparison_timestamp": datetime.now().isoformat(),
        "content_extracted": {
            "title": content_data.get('meta_title', ''),
            "text_length": len(content_data.get('text_content', '')),
            "h1_count": len(content_data.get('h1_tags', [])),
            "h2_count": len(content_data.get('h2_tags', []))
        }
    }
    
    # Test 1: OpenAI GPT-4o uniquement
    try:
        print("🤖 Testing OpenAI GPT-4o...")
        openai_result = await test_openai_only(content_data, url)
        results["openai_gpt4o"] = {
            "status": "success",
            "analysis": openai_result,
            "model": "gpt-4o"
        }
        print(f"✅ OpenAI analysis completed: {len(openai_result.get('analysis_summary', ''))} chars")
    except Exception as e:
        results["openai_gpt4o"] = {
            "status": "error",
            "error": str(e),
            "model": "gpt-4o"
        }
        print(f"❌ OpenAI failed: {e}")
    
    # Test 2: Claude Sonnet 4 uniquement
    try:
        print("🧠 Testing Claude Sonnet 4...")
        claude_result = await test_claude_only(content_data, url)
        results["claude_sonnet4"] = {
            "status": "success", 
            "analysis": claude_result,
            "model": "claude-4-sonnet"
        }
        print(f"✅ Claude analysis completed: {len(claude_result.get('analysis_summary', ''))} chars")
    except Exception as e:
        results["claude_sonnet4"] = {
            "status": "error",
            "error": str(e),
            "model": "claude-4-sonnet"
        }
        print(f"❌ Claude failed: {e}")
    
    return JSONResponse(content=results)


async def test_openai_only(content_data: dict, website_url: str) -> dict:
    """Test OpenAI GPT-4o uniquement"""
    if not OPENAI_AVAILABLE or not API_KEY:
        raise Exception("OpenAI not available or API key missing")
    
    prompt = f"""
    Analyse ce site web en profondeur et réponds UNIQUEMENT par un JSON structuré:
    {{
        "analysis_summary": "Un résumé détaillé de l'entreprise (200-300 mots)",
        "key_topics": ["topic1", "topic2", "topic3", "topic4", "topic5"],
        "brand_tone": "le ton de communication",
        "target_audience": "description du public cible principal",
        "main_services": ["service1", "service2", "service3"],
        "content_suggestions": ["suggestion1", "suggestion2", "suggestion3", "suggestion4"]
    }}

    Site web: {website_url}
    Titre: {content_data.get('meta_title', 'Non défini')}
    Description: {content_data.get('meta_description', 'Non définie')}
    H1: {content_data.get('h1_tags', [])}
    H2: {content_data.get('h2_tags', [])}
    Contenu: {content_data.get('text_content', 'Non disponible')[:2000]}
    """
    
    client = OpenAI(api_key=API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "Tu es un expert en analyse web. Réponds UNIQUEMENT en JSON valide."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=2000
    )
    
    raw_response = response.choices[0].message.content
    
    # Parse JSON
    clean_response = raw_response.strip()
    if clean_response.startswith('```json'):
        clean_response = clean_response[7:]
    if clean_response.endswith('```'):
        clean_response = clean_response[:-3]
    
    return json.loads(clean_response.strip())


async def test_claude_only(content_data: dict, website_url: str) -> dict:
    """Test Claude Sonnet 4 uniquement"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
    except ImportError:
        raise Exception("Claude/emergentintegrations not available")
    
    claude_key = os.environ.get('CLAUDE_API_KEY')
    if not claude_key:
        raise Exception("Claude API key missing")
    
    # Construire le prompt pour Claude
    prompt = f"""
    Tu es un expert en analyse de sites web. Analyse ce site et réponds UNIQUEMENT par un JSON structuré:
    {{
        "analysis_summary": "Un résumé détaillé de l'entreprise (200-300 mots)",
        "key_topics": ["topic1", "topic2", "topic3", "topic4", "topic5"],
        "brand_tone": "le ton de communication",
        "target_audience": "description du public cible principal", 
        "main_services": ["service1", "service2", "service3"],
        "content_suggestions": ["suggestion1", "suggestion2", "suggestion3", "suggestion4"]
    }}

    Site web: {website_url}
    Titre: {content_data.get('meta_title', 'Non défini')}
    Description: {content_data.get('meta_description', 'Non définie')}
    H1: {content_data.get('h1_tags', [])}
    H2: {content_data.get('h2_tags', [])}
    Contenu: {content_data.get('text_content', 'Non disponible')[:2000]}
    
    IMPORTANT: Réponds UNIQUEMENT avec le JSON, sans texte supplémentaire.
    """
    
    claude_chat = LlmChat(
        api_key=claude_key,
        session_id="comparison-test",
        system_message="Tu es un expert en analyse web. Tu réponds toujours en JSON valide et structuré."
    ).with_model("anthropic", "claude-4-sonnet-20250514")
    
    user_message = UserMessage(text=prompt)
    response = await claude_chat.send_message(user_message)
    
    # Parse JSON from Claude response
    clean_response = response.strip()
    if clean_response.startswith('```json'):
        clean_response = clean_response[7:]
    if clean_response.endswith('```'):
        clean_response = clean_response[:-3]
    
    return json.loads(clean_response.strip())


@website_router.post("/compare-posts")
async def compare_posts_generation(
    request: dict,
    user_id: str = Depends(get_current_user_id_robust)
):
    """Compare OpenAI vs Claude pour la génération de posts"""
    
    business_context = request.get('business_context', '')
    if not business_context:
        raise HTTPException(status_code=400, detail="business_context is required")
    
    results = {
        "comparison_timestamp": datetime.now().isoformat(),
        "business_context": business_context
    }
    
    # Test 1: OpenAI GPT-4o pour posts
    try:
        print("🤖 Testing OpenAI for posts...")
        openai_post = await test_openai_post_generation(business_context)
        results["openai_gpt4o_post"] = {
            "status": "success",
            "post": openai_post,
            "model": "gpt-4o"
        }
    except Exception as e:
        results["openai_gpt4o_post"] = {
            "status": "error",
            "error": str(e),
            "model": "gpt-4o"
        }
    
    # Test 2: Claude Sonnet 4 pour posts
    try:
        print("🧠 Testing Claude for posts...")
        claude_post = await test_claude_post_generation(business_context)
        results["claude_sonnet4_post"] = {
            "status": "success",
            "post": claude_post,
            "model": "claude-4-sonnet"
        }
    except Exception as e:
        results["claude_sonnet4_post"] = {
            "status": "error",
            "error": str(e),
            "model": "claude-4-sonnet"
        }
    
    return results


async def test_openai_post_generation(business_context: str) -> dict:
    """Test génération de post avec OpenAI uniquement"""
    if not OPENAI_AVAILABLE or not API_KEY:
        raise Exception("OpenAI not available")
    
    prompt = f"""
    Crée un post Instagram pour cette entreprise. Réponds en JSON:
    {{
        "text": "Texte du post naturel, max 2-3 emojis",
        "hashtags": ["hashtag1", "hashtag2", "hashtag3"],
        "title": "Titre simple et direct"
    }}

    Contexte entreprise: {business_context}
    
    RÈGLES:
    - Style naturel, pas artificiel
    - Maximum 2-3 emojis
    - Call-to-action simple
    - Hashtags pertinents
    """
    
    client = OpenAI(api_key=API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Tu es un expert en réseaux sociaux. Réponds UNIQUEMENT en JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=500
    )
    
    raw_response = response.choices[0].message.content
    clean_response = raw_response.strip()
    if clean_response.startswith('```json'):
        clean_response = clean_response[7:]
    if clean_response.endswith('```'):
        clean_response = clean_response[:-3]
    
    return json.loads(clean_response.strip())


async def test_claude_post_generation(business_context: str) -> dict:
    """Test génération de post avec Claude uniquement"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
    except ImportError:
        raise Exception("Claude not available")
    
    claude_key = os.environ.get('CLAUDE_API_KEY')
    if not claude_key:
        raise Exception("Claude API key missing")
    
    prompt = f"""
    Crée un post Instagram pour cette entreprise. Réponds UNIQUEMENT en JSON:
    {{
        "text": "Texte du post naturel, max 2-3 emojis",
        "hashtags": ["hashtag1", "hashtag2", "hashtag3"],
        "title": "Titre simple et direct"
    }}

    Contexte entreprise: {business_context}
    
    RÈGLES:
    - Style naturel, pas artificiel
    - Maximum 2-3 emojis  
    - Call-to-action simple
    - Hashtags pertinents
    
    Réponds UNIQUEMENT avec le JSON, rien d'autre.
    """
    
    claude_chat = LlmChat(
        api_key=claude_key,
        session_id="posts-comparison",
        system_message="Tu es un expert en réseaux sociaux. Tu réponds toujours en JSON valide."
    ).with_model("anthropic", "claude-4-sonnet-20250514")
    
    user_message = UserMessage(text=prompt)
    response = await claude_chat.send_message(user_message)
    
    clean_response = response.strip()
    if clean_response.startswith('```json'):
        clean_response = clean_response[7:]
    if clean_response.endswith('```'):
        clean_response = clean_response[:-3]
    
    return json.loads(clean_response.strip())


@website_router.get("/super-unique-test-endpoint-12345")
async def super_unique_test():
    """Endpoint de test avec nom absolument unique"""
    import datetime
    
    print(f"🔥🔥🔥 ENDPOINT UNIQUE APPELÉ À {datetime.datetime.now()}")
    logging.error(f"🔥🔥🔥 ENDPOINT UNIQUE APPELÉ - FORCED ERROR LOG")
    
    return {
        "status": "SUCCESS", 
        "message": "Endpoint unique exécuté avec succès!",
        "timestamp": datetime.datetime.now().isoformat(),
        "test": "Notre code s'exécute bien!"
    }


@website_router.get("/debug-routes")
async def debug_routes():
    """Debug endpoint pour lister toutes les routes disponibles"""
    try:
        # Importer FastAPI app depuis server.py
        import sys
        import importlib
        
        # Cette approche permet de voir les routes enregistrées
        routes_info = []
        
        # Informations sur notre router
        routes_info.append({
            "router": "website_router (gpt5)",
            "prefix": "/website",
            "routes": []
        })
        
        for route in website_router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                routes_info[-1]["routes"].append({
                    "path": route.path,
                    "methods": list(route.methods) if route.methods else [],
                    "name": getattr(route, 'name', 'unknown')
                })
        
        return {
            "status": "debug_routes",
            "message": "Routes debug info",
            "routes_info": routes_info,
            "total_routes": len(website_router.routes)
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e),
            "message": "Failed to get routes info"
        }


@website_router.post("/debug-analyze")
async def debug_analyze_forced(
    request: WebsiteAnalysisRequest,
    user_id: str = Depends(get_current_user_id_robust)
):
    """Debug endpoint qui force l'analyse GPT-4o directement"""
    from fastapi.responses import JSONResponse
    
    url = (request.website_url or "").strip()
    if not re.match(r'^https?://', url, re.IGNORECASE):
        url = 'https://' + url
    
    print(f"🔥 DEBUG ENDPOINT - Forçant l'analyse GPT-4o pour: {url}")
    
    # Données de test basiques
    content_data = {
        'meta_title': 'Site de test',
        'meta_description': 'Test description', 
        'h1_tags': ['Titre principal'],
        'h2_tags': ['Sous-titre'],
        'text_content': f'Contenu du site web {url} pour test d\'analyse GPT-4o.'
    }
    
    try:
        # Appel DIRECT à analyze_with_gpt4o
        print(f"🚀 Appel DIRECT à analyze_with_gpt4o...")
        analysis_result = await analyze_with_gpt4o(content_data, url)
        print(f"✅ Résultat reçu: {type(analysis_result)}")
        
        return {
            "status": "debug_success",
            "message": "Analyse GPT-4o forcée avec succès!",
            "debug_mode": True,
            **analysis_result
        }
        
    except Exception as e:
        print(f"❌ Erreur debug: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"Debug error: {str(e)}"}
        )


async def analyze_with_gpt4o_business(content_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyse business/exécution avec GPT-4o : concis, structuré, actionnable"""
    
    # Initialiser le système LLM
    llm_system = LLMBackupSystem()
    
    # Préparer le contenu pour l'analyse depuis la vraie structure de content_data
    title = content_data.get('title', '')
    description = content_data.get('description', '')
    text_content = content_data.get('text_content', '')
    h1_tags = content_data.get('h1_tags', [])
    h2_tags = content_data.get('h2_tags', [])
    pages_analyzed = content_data.get('pages_analyzed', [])
    
    # Construire le contenu combiné
    combined_content = f"""TITRE DU SITE: {title}
DESCRIPTION: {description}

CONTENUS PRINCIPAUX (H1): {', '.join(h1_tags[:5])}
SOUS-TITRES (H2): {', '.join(h2_tags[:10])}

CONTENU TEXTUEL EXTRAIT:
{text_content[:3000]}

PAGES ANALYSÉES: {len(pages_analyzed)} pages
{', '.join([page.get('url', '') for page in pages_analyzed[:5]])}"""
    
    # Prompt spécialisé pour GPT-4o (Business/Exécution)
    business_prompt = f"""Tu es un expert en analyse business et stratégie digitale. Analyse ce site web de manière CONCISE et STRUCTURÉE pour donner des insights immédiatement ACTIONNABLES.

Contenu du site web à analyser :
{combined_content}

Fournis une analyse business CONCISE et STRUCTURÉE selon ce format exact :

**RÉSUMÉ DE L'ANALYSE**
[En 40-60 mots maximum : Qui est l'entreprise, que fait-elle, quelle est sa proposition de valeur principale]

**AUDIENCE CIBLE**
[Profil démographique et psychographique en 30-40 mots : âge, revenus, besoins, motivations]

**SERVICES PRINCIPAUX**
• [Service 1 - en 5-8 mots max]
• [Service 2 - en 5-8 mots max] 
• [Service 3 - en 5-8 mots max]

**SUJETS CLÉS**
• [mot-clé 1]
• [mot-clé 2]
• [mot-clé 3]
• [mot-clé 4]
• [mot-clé 5]

**SUGGESTIONS DE CONTENU**
• [Idée 1 - format court, actionnable]
• [Idée 2 - format court, actionnable]
• [Idée 3 - format court, actionnable]
• [Idée 4 - format court, actionnable]

IMPORTANT : Sois CONCIS, DIRECT et ACTIONNABLE. Pas de phrases longues ou de jargon."""

    try:
        # Utiliser GPT-4o via le système LLM
        messages = [
            {
                "role": "system",
                "content": "Tu es un expert en analyse business et stratégie digitale. Tu analyses les sites web de manière CONCISE et STRUCTURÉE pour donner des insights immédiatement ACTIONNABLES."
            },
            {
                "role": "user", 
                "content": business_prompt
            }
        ]
        
        response = await llm_system.generate_completion_with_strategy(
            messages=messages,
            business_objective="conversion",  # Force business analysis
            brand_tone="professionnel",
            platform="instagram",
            temperature=0.3,  # Plus bas pour plus de cohérence business
            max_tokens=800
        )
        
        return {
            "type": "business_analysis",
            "ai_used": "GPT-4o",
            "content": response,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Erreur analyse business GPT-4o: {e}")
        return {
            "type": "business_analysis",
            "ai_used": "Error",
            "content": f"Erreur lors de l'analyse business: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }


async def analyze_with_claude_narrative(content_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyse narrative/inspiration avec Claude Sonnet 4 : storytelling, profondeur"""
    
    # Initialiser le système LLM
    llm_system = LLMBackupSystem()
    
    # Préparer le contenu pour l'analyse depuis la vraie structure de content_data
    title = content_data.get('title', '')
    description = content_data.get('description', '')
    text_content = content_data.get('text_content', '')
    h1_tags = content_data.get('h1_tags', [])
    h2_tags = content_data.get('h2_tags', [])
    pages_analyzed = content_data.get('pages_analyzed', [])
    
    # Construire le contenu combiné pour l'analyse narrative
    combined_content = f"""TITRE DU SITE: {title}
DESCRIPTION: {description}

CONTENUS PRINCIPAUX (H1): {', '.join(h1_tags[:5])}
SOUS-TITRES (H2): {', '.join(h2_tags[:10])}

CONTENU TEXTUEL EXTRAIT:
{text_content[:3000]}

PAGES ANALYSÉES: {len(pages_analyzed)} pages
{', '.join([page.get('url', '') for page in pages_analyzed[:5]])}"""
    
    # Prompt spécialisé pour Claude Sonnet 4 (Narrative/Inspiration)
    narrative_prompt = f"""Tu es un expert en storytelling de marque et stratégie éditoriale. Analyse ce site web pour révéler sa VISION, son POSITIONNEMENT et ses OPPORTUNITÉS NARRATIVES.

Contenu du site web à analyser :
{combined_content}

Fournis une analyse narrative RICHE et INSPIRANTE selon ce format :

**VISION ET STORYTELLING**
[Un paragraphe de 60-80 mots qui raconte l'histoire de la marque, son essence, ce qu'elle représente vraiment au-delà de ses services. Utilise un ton engageant et évocateur.]

**POSITIONNEMENT**
[Un paragraphe de 50-70 mots qui explique où se situe la marque sur son marché, quel territoire elle occupe, et comment elle se différencie. Mets l'accent sur l'émotionnel et l'aspirationnel.]

**AXES ÉDITORIAUX À EXPLOITER**
1. [Axe 1] – [Explication en 15-20 mots de pourquoi c'est puissant pour cette marque]
2. [Axe 2] – [Explication en 15-20 mots de l'opportunité narrative]
3. [Axe 3] – [Explication en 15-20 mots du potentiel storytelling]
4. [Axe 4] – [Explication en 15-20 mots de l'angle éditorial unique]

**IDÉES DE CONTENUS NARRATIFS**
• [Idée 1 : Format + angle storytelling spécifique]
• [Idée 2 : Format + angle émotionnel ou aspirationnel]
• [Idée 3 : Format + angle communauté ou témoignage transformé]
• [Idée 4 : Format + angle expertise avec dimension humaine]

IMPORTANT : Sois INSPIRANT, ÉVOCATEUR et axé sur le STORYTELLING. Révèle la dimension émotionnelle et narrative de la marque."""

    try:
        # Utiliser Claude Sonnet 4 via le système LLM
        messages = [
            {
                "role": "system",
                "content": "Tu es un expert en storytelling de marque et stratégie éditoriale. Tu analyses les sites web pour révéler leur VISION, leur POSITIONNEMENT et leurs OPPORTUNITÉS NARRATIVES."
            },
            {
                "role": "user",
                "content": narrative_prompt
            }
        ]
        
        response = await llm_system.generate_completion_with_strategy(
            messages=messages,
            business_objective="communaute",  # Force narrative analysis
            brand_tone="storytelling",  # Force Claude primary
            platform="instagram",
            temperature=0.7,  # Plus élevé pour plus de créativité narrative
            max_tokens=1000
        )
        
        return {
            "type": "narrative_analysis",
            "ai_used": "Claude Sonnet 4",
            "content": response,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Erreur analyse narrative Claude: {e}")
        return {
            "type": "narrative_analysis", 
            "ai_used": "Error",
            "content": f"Erreur lors de l'analyse narrative: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }


async def orchestrate_dual_analysis(content_data: Dict[str, Any]) -> Dict[str, Any]:
    """Orchestre l'analyse parallèle GPT-4o + Claude Sonnet 4"""
    
    print("🎭 Démarrage analyse orchestrée : GPT-4o (Business) + Claude (Narrative)")
    
    try:
        # Lancer les deux analyses en parallèle
        business_task = analyze_with_gpt4o_business(content_data)
        narrative_task = analyze_with_claude_narrative(content_data)
        
        # Attendre les deux résultats
        business_result, narrative_result = await asyncio.gather(
            business_task, 
            narrative_task,
            return_exceptions=True
        )
        
        # Gérer les erreurs éventuelles
        if isinstance(business_result, Exception):
            print(f"❌ Erreur analyse business: {business_result}")
            business_result = {
                "type": "business_analysis",
                "ai_used": "Error", 
                "content": f"Erreur: {str(business_result)}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        if isinstance(narrative_result, Exception):
            print(f"❌ Erreur analyse narrative: {narrative_result}")
            narrative_result = {
                "type": "narrative_analysis",
                "ai_used": "Error",
                "content": f"Erreur: {str(narrative_result)}",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Retourner l'analyse fusionnée
        dual_analysis = {
            "analysis_type": "dual_orchestrated",
            "business_analysis": business_result,
            "narrative_analysis": narrative_result,
            "orchestration_summary": {
                "business_ai": business_result.get("ai_used", "Unknown"),
                "narrative_ai": narrative_result.get("ai_used", "Unknown"),
                "completion_time": datetime.utcnow().isoformat(),
                "status": "completed"
            }
        }
        
        print("✅ Analyse orchestrée terminée avec succès")
        return dual_analysis
        
    except Exception as e:
        print(f"❌ Erreur orchestration: {e}")
        return {
            "analysis_type": "dual_orchestrated_error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@website_router.post("/analyze")
async def analyze_website_robust(
    request: WebsiteAnalysisRequest,
    user_id: str = Depends(get_current_user_id_robust)
):
    """Enhanced website analysis with multi-page scanning"""
    from fastapi.responses import JSONResponse

    # Normalize URL
    url = (request.website_url or "").strip()
    if not re.match(r'^https?://', url, re.IGNORECASE):
        url = 'https://' + url

    print(f"🔍 Starting enhanced website analysis: {url} for user: {user_id}")
    logging.error(f"🔍 FORCED ERROR LOG - Starting analysis: {url} for user: {user_id}")

    try:
        # Step 1: Discover important pages
        important_pages = discover_website_pages(url, max_pages=5)
        print(f"📋 Found {len(important_pages)} pages to analyze: {important_pages}")
        
        # Step 2: Analyze multiple pages
        content_data = await analyze_multiple_pages(important_pages, url)
        
        if "error" in content_data:
            code, msg = content_data["error"]
            return JSONResponse(status_code=code, content={"error": msg})

        # Step 3: Enhanced analyses - GPT-4o + Claude Storytelling en parallèle
        logging.info(f"🚀 About to launch parallel analyses for {url}")
        logging.info(f"🔍 Content data keys: {list(content_data.keys())}")
        
        # Lancer les deux analyses en parallèle
        gpt4o_task = analyze_with_gpt4o_only(content_data, url)
        claude_task = analyze_with_claude_storytelling(content_data, url)
        
        # Attendre les deux résultats
        gpt4o_result, claude_result = await asyncio.gather(
            gpt4o_task, 
            claude_task,
            return_exceptions=True
        )
        
        # Gérer les erreurs éventuelles pour GPT-4o
        if isinstance(gpt4o_result, Exception):
            logging.error(f"❌ GPT-4o analysis failed: {gpt4o_result}")
            gpt4o_result = create_fallback_analysis(content_data, url, f"gpt4o_error: {str(gpt4o_result)}")
            
        # Gérer les erreurs éventuelles pour Claude
        if isinstance(claude_result, Exception):
            logging.error(f"❌ Claude storytelling analysis failed: {claude_result}")
            claude_result = {
                "storytelling_analysis": "Analyse storytelling non disponible pour le moment.",
                "ai_used": "Error",
                "analysis_type": "storytelling_error"
            }
        
        # Combiner les résultats
        analysis_result = gpt4o_result.copy()  # Base GPT-4o
        analysis_result.update({
            "storytelling_analysis": claude_result.get("storytelling_analysis", ""),
            "storytelling_ai": claude_result.get("ai_used", "Claude Sonnet 4"),
            "storytelling_type": claude_result.get("analysis_type", "storytelling_narrative")
        })
        
        logging.info(f"🎯 Parallel analyses completed - GPT-4o + Claude Storytelling")

        # Step 4: Prepare enhanced response with GPT-4o + Claude Storytelling
        analysis_data = {
            "analysis_summary": analysis_result.get("analysis_summary", ""),
            "storytelling_analysis": analysis_result.get("storytelling_analysis", ""),
            "storytelling_ai": analysis_result.get("storytelling_ai", "Claude Sonnet 4"),
            "storytelling_type": analysis_result.get("storytelling_type", "storytelling_narrative"),
            # Nouveaux champs d'analyse approfondie
            "products_services_details": analysis_result.get("products_services_details", ""),
            "company_expertise": analysis_result.get("company_expertise", ""),
            "unique_value_proposition": analysis_result.get("unique_value_proposition", ""),
            "analysis_depth": analysis_result.get("analysis_depth", "enhanced_multi_page"),
            "pages_analyzed_count": analysis_result.get("pages_analyzed_count", len(important_pages)),
            "non_technical_pages_count": analysis_result.get("non_technical_pages_count", 0),
            # Champs existants
            "narrative_insights": "",  # Kept for compatibility but empty
            "orchestration_info": {},  # Kept for compatibility but empty
            "key_topics": analysis_result.get("key_topics", []),
            "brand_tone": analysis_result.get("brand_tone", "professionnel"),
            "target_audience": analysis_result.get("target_audience", ""),
            "main_services": analysis_result.get("main_services", []),
            "content_suggestions": analysis_result.get("content_suggestions", []),
            "website_url": url,
            "pages_analyzed": content_data.get("pages_analyzed", []),
            "pages_count": len(important_pages),
            "analysis_type": "gpt4o_plus_claude_storytelling",
            "business_ai": "GPT-4o",
            "narrative_ai": "Claude Sonnet 4",
            "created_at": datetime.utcnow().isoformat(),
            "next_analysis_due": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }

        # Step 5: Save enhanced analysis to MongoDB
        try:
            import pymongo
            mongo_url = os.environ.get("MONGO_URL")
            client = pymongo.MongoClient(mongo_url)
            dbp = client.claire_marcus
            dbp.website_analyses.insert_one({
                "user_id": user_id,
                "website_url": url,
                "analysis_summary": analysis_data["analysis_summary"],
                "key_topics": analysis_data["key_topics"],
                "brand_tone": analysis_data["brand_tone"],
                "target_audience": analysis_data["target_audience"],
                "main_services": analysis_data["main_services"],
                "content_suggestions": analysis_data["content_suggestions"],
                "pages_analyzed": analysis_data["pages_analyzed"],
                "pages_count": analysis_data["pages_count"],
                "created_at": datetime.utcnow(),
                "last_analyzed": datetime.utcnow(),
                "next_analysis_due": datetime.utcnow() + timedelta(days=30)
            })
            client.close()
            print("✅ Enhanced analysis saved to database")
        except Exception as db_error:
            print(f"⚠️ Database save failed: {db_error}")

        return {
            "status": "analyzed",
            "message": f"Analyse complète : GPT-4o + Claude Storytelling - {analysis_data['pages_count']} pages analysées",
            **analysis_data
        }
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return JSONResponse(
            status_code=500, 
            content={"error": "Erreur lors de l'analyse du site web"}
        )

# Remove duplicate GET definition (keep only the one above) and keep delete endpoint

@website_router.delete("/analysis")
async def delete_website_analysis(
    user_id: str = Depends(get_current_user_id_robust)
):
    """Delete website analysis for the current user"""
    try:
        result = await db.website_analyses.delete_many({"user_id": user_id})
        return {
            "message": f"Deleted {result.deleted_count} website analysis records",
            "deleted_count": result.deleted_count
        }
    except Exception as e:
        logging.error(f"Error deleting website analysis: {e}")
        raise HTTPException(status_code=500, detail="Error deleting website analysis")