"""
Website Analyzer avec GPT-4o - Version avec OpenAI direct
Utilise la clé OpenAI personnelle et GPT-4o directement
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, HttpUrl
import uuid
import requests
from bs4 import BeautifulSoup
import os
import logging
import json
import time
from motor.motor_asyncio import AsyncIOMotorClient
from pathlib import Path
from dotenv import load_dotenv
from fastapi import Header
from typing import Optional
import re

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

async def analyze_with_gpt4o(content_data: dict, website_url: str) -> dict:
    """Analyze website content using GPT-4o via OpenAI direct integration"""
    logging.info(f"🔥 analyze_with_gpt4o CALLED for {website_url}")
    
    if not API_KEY:
        logging.warning("No API key available, using fallback analysis")
        return create_fallback_analysis(content_data, website_url, "no_api_key")

    try:
        raw = None  # Initialize raw to avoid NameError
        
        # Construire le contenu détaillé avec informations des pages multiples
        main_content = f"""
        URL PRINCIPALE: {website_url}
        TITRE PRINCIPAL: {content_data.get('title', 'N/A')}
        META DESCRIPTION: {content_data.get('description', 'N/A')}
        
        PAGES ANALYSÉES: {len(content_data.get('pages_analyzed', []))} pages
        {chr(10).join([f"- {page.get('url', '')}: {page.get('title', 'Sans titre')}" for page in content_data.get('pages_analyzed', [])[:5]])}
        
        TITRES H1 COLLECTÉS: {', '.join(content_data.get('h1_tags', [])[:15])}
        TITRES H2 COLLECTÉS: {', '.join(content_data.get('h2_tags', [])[:20])}
        
        CONTENU TEXTUEL COMPLET (multi-pages):
        {content_data.get('text_content', '')[:4000]}
        """
        
        prompt = f"""
        Tu es un expert en analyse de sites web et marketing digital. Analyse ce site web de manière TRÈS DÉTAILLÉE pour aider à la génération de posts sur les réseaux sociaux.

        CONTENU À ANALYSER:
        {main_content}

        MISSION: Créer une analyse marketing approfondie et actionnable. Sois très spécifique et détaillé dans chaque section.

        IMPORTANT: 
        - NE PAS utiliser l'extension du domaine (.fr, .com, .net, etc.) comme partie du nom de l'entreprise
        - Identifier le vrai nom commercial de l'entreprise à partir du contenu, titres, et textes du site
        - Si le nom n'est pas clair, utiliser une description générique plutôt que l'URL

        Réponds UNIQUEMENT avec ce JSON (sans ``` ni markdown):
        {{
            "analysis_summary": "Résumé détaillé et complet de l'entreprise, ses activités, son positionnement et sa proposition de valeur unique. 5-8 phrases complètes qui donnent une vision claire de ce que fait cette entreprise et comment elle se différencie. Inclure le secteur d'activité, la localisation si mentionnée, et les points forts identifiés.",
            
            "key_topics": ["10 à 15 mots-clés et expressions stratégiques identifiés sur le site, incluant secteur d'activité, services spécifiques, valeurs de l'entreprise, expertises techniques, zone géographique"],
            
            "brand_tone": "Choisir parmi: professionnel, décontracté, créatif, technique, luxueux, convivial, artisanal, innovant, éco-responsable, dynamique",
            
            "target_audience": "Description précise et détaillée de l'audience cible: âge, profil socio-professionnel, besoins spécifiques, centres d'intérêt, localisation géographique, niveau de revenus estimé, problématiques qu'ils cherchent à résoudre. Minimum 4-5 phrases avec des détails concrets.",
            
            "main_services": ["Liste complète et détaillée de tous les services/produits identifiés. Pour chaque service, être spécifique: ne pas juste dire 'conseil' mais 'conseil en transformation digitale pour PME'. Minimum 5-8 services/produits détaillés"],
            
            "content_suggestions": [
                "10 suggestions concrètes et spécifiques de posts pour les réseaux sociaux, adaptées à cette entreprise. Chaque suggestion doit être actionnable et précise, par exemple: 'Post avant/après montrant une réalisation client avec témoignage', 'Infographie sur les 5 étapes de leur processus métier', 'Story derrière l'équipe avec présentation individuelle', etc. Varier les formats: posts éducatifs, témoignages clients, coulisses, actualités secteur, conseils pratiques, études de cas, événements."
            ]
        }}

        IMPORTANT: Sois très généreux dans les détails. Plus c'est précis et détaillé, plus ce sera utile pour créer du contenu marketing pertinent.
        """

        # Use OpenAI directly for GPT-4o analysis
        if OPENAI_AVAILABLE and API_KEY:
            logging.info(f"🤖 Using GPT-4o via OpenAI direct integration for analysis")
            logging.info(f"🔍 Content to analyze: title='{content_data.get('meta_title', '')}', text_length={len(content_data.get('text_content', ''))}")
            
            try:
                client = OpenAI(api_key=API_KEY)
                logging.info(f"📡 Sending request to OpenAI GPT-4o...")
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system", 
                            "content": "Tu es un expert en analyse de contenu web et marketing digital. Tu analyses les sites web en profondeur pour créer du contenu social media. Réponds UNIQUEMENT en JSON valide et structuré."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                raw = response.choices[0].message.content
                logging.info(f"🤖 GPT-4o raw response length: {len(raw) if raw else 0} characters")
                logging.info(f"🤖 GPT-4o raw response preview: {raw[:300] if raw else 'None'}...")
                
            except Exception as openai_error:
                logging.error(f"❌ OpenAI API error: {openai_error}")
                return create_fallback_analysis(content_data, website_url, "openai_api_error")
            
        else:
            logging.error(f"❌ Falling back - OPENAI_AVAILABLE: {OPENAI_AVAILABLE}, API_KEY: {'Yes' if API_KEY else 'No'}")
            return create_fallback_analysis(content_data, website_url, "no_api_or_sdk")

        # Parse GPT-4o response
        if not raw or len(raw.strip()) < 10:
            print(f"❌ Empty or too short GPT-4o response: '{raw}'")
            return create_fallback_analysis(content_data, website_url, "empty_response")
        
        # Clean the response (remove potential markdown artifacts)
        clean_raw = raw.strip()
        if clean_raw.startswith('```json'):
            clean_raw = clean_raw[7:]
        if clean_raw.endswith('```'):
            clean_raw = clean_raw[:-3]
        clean_raw = clean_raw.strip()
        
        print(f"🔍 Parsing GPT-4o JSON response: {clean_raw[:200]}...")
        
        analysis = json.loads(clean_raw)
        
        # Validate required fields
        required_fields = ["analysis_summary", "key_topics", "brand_tone", "target_audience", "main_services", "content_suggestions"]
        missing_fields = [field for field in required_fields if not analysis.get(field)]
        
        if missing_fields:
            print(f"⚠️ Missing fields in GPT-4o response: {missing_fields}")
            return create_fallback_analysis(content_data, website_url, f"missing_fields_{missing_fields}")
        
        print(f"✅ GPT-4o analysis successful - Summary length: {len(analysis.get('analysis_summary', ''))}")
        return analysis

    except json.JSONDecodeError as e:
        logging.error(f"❌ JSON parsing error from GPT-4o: {e}")
        logging.error(f"❌ Raw response was: {raw[:500] if raw else 'None'}")
        return create_fallback_analysis(content_data, website_url, "json_error")
    except Exception as e:
        logging.error(f"❌ GPT-4o analysis GENERAL error: {e}")
        logging.error(f"❌ Error type: {type(e)}")
        import traceback
        logging.error(f"❌ Full traceback: {traceback.format_exc()}")
        return create_fallback_analysis(content_data, website_url, "gpt_error")

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

        # Step 3: Enhanced GPT analysis with multi-page context
        logging.info(f"🚀 About to call analyze_with_gpt4o for {url}")
        logging.info(f"🔍 Content data keys: {list(content_data.keys())}")
        analysis_result = await analyze_with_gpt4o(content_data, url)
        logging.info(f"🎯 analyze_with_gpt4o completed, result type: {type(analysis_result)}")

        # Step 4: Prepare enhanced response with page details
        analysis_data = {
            "analysis_summary": analysis_result.get("analysis_summary", ""),
            "key_topics": analysis_result.get("key_topics", []),
            "brand_tone": analysis_result.get("brand_tone", "professional"),
            "target_audience": analysis_result.get("target_audience", ""),
            "main_services": analysis_result.get("main_services", []),
            "content_suggestions": analysis_result.get("content_suggestions", []),
            "website_url": url,
            "pages_analyzed": content_data.get("pages_analyzed", []),
            "pages_count": len(important_pages),
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
            "message": f"Enhanced analysis completed - {analysis_data['pages_count']} pages analyzed",
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