"""
Website Analyzer avec GPT-5 - Version Améliorée
Migrate from legacy OpenAI to emergentintegrations with GPT-5
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

# Import emergentintegrations for GPT-5 (with fallback to OpenAI)
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    EMERGENT_AVAILABLE = True
    print("✅ emergentintegrations module imported successfully")
except ImportError as e:
    print(f"⚠️ emergentintegrations not available: {e}")
    print("📌 Falling back to direct OpenAI integration")
    EMERGENT_AVAILABLE = False
    
    # Fallback imports for OpenAI
    try:
        from openai import OpenAI
    except Exception as oe:
        print(f"⚠️ OpenAI import issue: {oe}")
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

# API Key configuration - Use Emergent LLM Key for GPT-4o
from emergentintegrations.llm import get_key
try:
    API_KEY = get_key()  # Get the Emergent universal key
    if API_KEY:
        print(f"✅ Emergent LLM Key loaded successfully")
    else:
        print("❌ No Emergent LLM Key found")
except Exception as e:
    print(f"❌ Error loading Emergent key: {e}")
    API_KEY = None

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

async def analyze_with_gpt5(content_data: dict, website_url: str) -> dict:
    """Analyze website content using GPT via emergentintegrations (with OpenAI fallback)"""
    if not API_KEY:
        logging.warning("No API key available, using fallback analysis")
        return create_fallback_analysis(content_data, website_url, "no_api_key")

    try:
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

        # Prefer direct OpenAI when available
        if OPENAI_API_KEY and OpenAI is not None:
            client = OpenAI(api_key=API_KEY)
            resp = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Tu es un expert en analyse de contenu web et marketing. Réponds UNIQUEMENT en JSON valide."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1200
            )
            raw = resp.choices[0].message.content.strip()
        elif EMERGENT_AVAILABLE:
            chat = LlmChat(
                api_key=API_KEY,
                session_id=f"website_analysis_{uuid.uuid4()}",
                system_message="Tu es un expert en analyse de contenu web et marketing. Réponds UNIQUEMENT en JSON valide."
            ).with_model("openai", "gpt-4o")
            user_message = UserMessage(text=prompt)
            raw = await chat.send_message(user_message)
        else:
            return create_fallback_analysis(content_data, website_url, "no_sdk")

        analysis = json.loads(raw)
        return analysis

    except json.JSONDecodeError as e:
        logging.error(f"❌ JSON parsing error: {e}")
        return create_fallback_analysis(content_data, website_url, "json_error")
    except Exception as e:
        logging.error(f"❌ GPT analysis error: {e}")
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
        analysis_result = await analyze_with_gpt5(content_data, url)

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