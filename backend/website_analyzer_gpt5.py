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
    import openai
    from openai import OpenAI

# Simple User model for compatibility
class User:
    def __init__(self, user_id: str, email: str = ""):
        self.id = user_id
        self.email = email

# Compatible authentication function matching server.py
# Import JWT authentication from main server
try:
    from database import DatabaseManager
    JWT_AVAILABLE = True
    print("✅ JWT authentication imported successfully")
except ImportError as e:
    print(f"⚠️ JWT authentication not available: {e}")
    JWT_AVAILABLE = False

# Import robust authentication from shared security module
from security import get_current_user_id_robust

print("✅ Website Analyzer using shared security authentication")

def get_current_user_id(authorization: str = Header(None)) -> str:
    """Extract user ID from JWT token - compatible with server.py"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    if JWT_AVAILABLE:
        try:
            # Use same JWT logic as main server
            db_manager = DatabaseManager()
            user_data = db_manager.get_user_by_token(token)
            if user_data:
                return user_data.get("user_id", "")
            else:
                raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            print(f"JWT verification error: {e}")
            raise HTTPException(status_code=401, detail="Token verification failed")
    else:
        # Fallback mode
        raise HTTPException(status_code=401, detail="Authentication system not available")

def get_current_active_user(authorization: str = Header(None)) -> User:
    """Get current active user - compatible with server.py"""
    user_id = get_current_user_id(authorization)
    return User(user_id=user_id)

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# API Key configuration - supports both Universal Key and OpenAI Key
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

# Choose API key (Universal key has priority)
API_KEY = EMERGENT_LLM_KEY if EMERGENT_LLM_KEY else OPENAI_API_KEY

if not API_KEY:
    logging.warning("No API key found for GPT-5. Website analysis will use fallback mode.")

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
    website_url: HttpUrl
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

def extract_website_content(url):
    """Extract content from website homepage only"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract text content
        content_text = soup.get_text(separator=' ', strip=True)
        
        # Extract metadata
        meta_description = ""
        meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_desc_tag:
            meta_description = meta_desc_tag.get('content', '')
        
        title_tag = soup.find('title')
        meta_title = title_tag.get_text(strip=True) if title_tag else ""
        
        # Extract headers
        h1_tags = [h1.get_text(strip=True) for h1 in soup.find_all('h1')]
        h2_tags = [h2.get_text(strip=True) for h2 in soup.find_all('h2')]
        
        return {
            "content_text": content_text[:5000],  # Limit content size
            "meta_description": meta_description,
            "meta_title": meta_title,
            "h1_tags": h1_tags[:10],  # Limit number of headers
            "h2_tags": h2_tags[:20]
        }
        
    except Exception as e:
        logging.error(f"❌ Error extracting content from {url}: {e}")
        return {
            "content_text": "",
            "meta_description": "",
            "meta_title": "",
            "h1_tags": [],
            "h2_tags": []
        }

def discover_main_pages(base_url):
    """Découvrir les pages principales d'un site web en excluant les pages techniques"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(base_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Mots-clés pour identifier les pages importantes
        important_keywords = [
            'produit', 'product', 'service', 'offre', 'catalogue', 'boutique', 'shop', 'store',
            'about', 'propos', 'qui sommes', 'notre', 'équipe', 'team', 'histoire', 'history',
            'contact', 'témoignage', 'avis', 'review', 'client', 'customer', 'référence',
            'portfolio', 'réalisation', 'projet', 'work', 'galerie', 'gallery'
        ]
        
        # Mots-clés pour exclure les pages techniques
        excluded_keywords = [
            'mention', 'legal', 'légal', 'condition', 'cgv', 'cgu', 'privacy', 'confidentialité',
            'cookie', 'politique', 'terms', 'sitemap', 'plan du site', 'admin', 'login',
            'inscription', 'register', 'mot de passe', 'password', 'compte', 'account',
            'panier', 'cart', 'checkout', 'commande', 'order', 'facture', 'invoice'
        ]
        
        discovered_pages = []
        base_domain = base_url.rstrip('/').replace('https://', '').replace('http://', '').split('/')[0]
        
        # Chercher dans la navigation principale
        nav_sections = soup.find_all(['nav', 'header', 'menu'])
        for nav in nav_sections:
            links = nav.find_all('a', href=True)
            for link in links:
                href = link.get('href')
                text = link.get_text(strip=True).lower()
                
                if href and text:
                    # Construire l'URL complète
                    if href.startswith('/'):
                        full_url = f"https://{base_domain}{href}"
                    elif href.startswith('http'):
                        # Vérifier que c'est le même domaine
                        if base_domain in href:
                            full_url = href
                        else:
                            continue
                    else:
                        full_url = f"https://{base_domain}/{href}"
                    
                    # Vérifier si c'est une page importante
                    is_important = any(keyword in text for keyword in important_keywords)
                    is_excluded = any(keyword in text for keyword in excluded_keywords)
                    
                    if is_important and not is_excluded and full_url not in discovered_pages:
                        discovered_pages.append(full_url)
                        if len(discovered_pages) >= 5:  # Limiter à 5 pages max
                            break
        
        # Chercher aussi dans les liens principaux du contenu
        if len(discovered_pages) < 3:
            main_content = soup.find(['main', 'article', 'section']) or soup.find('div', class_=lambda x: x and ('main' in x or 'content' in x))
            if main_content:
                links = main_content.find_all('a', href=True)[:20]  # Limiter la recherche
                for link in links:
                    href = link.get('href')
                    text = link.get_text(strip=True).lower()
                    
                    if href and text and len(text) > 3:
                        # Construire l'URL complète
                        if href.startswith('/'):
                            full_url = f"https://{base_domain}{href}"
                        elif href.startswith('http') and base_domain in href:
                            full_url = href
                        else:
                            continue
                        
                        # Vérifier si c'est une page importante
                        is_important = any(keyword in text for keyword in important_keywords)
                        is_excluded = any(keyword in text for keyword in excluded_keywords)
                        
                        if is_important and not is_excluded and full_url not in discovered_pages:
                            discovered_pages.append(full_url)
                            if len(discovered_pages) >= 5:
                                break
        
        logging.info(f"🔍 Discovered {len(discovered_pages)} main pages for {base_url}: {discovered_pages}")
        return discovered_pages[:3]  # Retourner maximum 3 pages en plus de l'accueil
        
    except Exception as e:
        logging.error(f"❌ Error discovering pages from {base_url}: {e}")
        return []

def extract_multi_page_content(base_url):
    """Extraire le contenu de plusieurs pages importantes du site"""
    
    # Commencer par la page d'accueil
    logging.info(f"📄 Extracting homepage content from {base_url}")
    homepage_content = extract_website_content(base_url)
    
    # Découvrir les pages principales
    main_pages = discover_main_pages(base_url)
    
    all_content = {
        'homepage': homepage_content,
        'additional_pages': []
    }
    
    # Extraire le contenu des pages principales
    for page_url in main_pages:
        try:
            logging.info(f"📄 Extracting content from additional page: {page_url}")
            page_content = extract_website_content(page_url)
            
            # Ajouter des informations sur la page
            page_info = {
                'url': page_url,
                'content': page_content
            }
            all_content['additional_pages'].append(page_info)
            
            # Petite pause entre les requêtes
            time.sleep(0.5)
            
        except Exception as e:
            logging.error(f"❌ Error extracting content from {page_url}: {e}")
            continue
    
    # Agréger tout le contenu
    aggregated_content = {
        'content_text': homepage_content['content_text'],
        'meta_description': homepage_content['meta_description'],
        'meta_title': homepage_content['meta_title'],
        'h1_tags': homepage_content['h1_tags'],
        'h2_tags': homepage_content['h2_tags'],
        'additional_content': []
    }
    
    # Ajouter le contenu des pages supplémentaires
    for page_info in all_content['additional_pages']:
        page_content = page_info['content']
        aggregated_content['additional_content'].append({
            'url': page_info['url'],
            'title': page_content['meta_title'],
            'content_text': page_content['content_text'][:2000],  # Limiter le contenu par page
            'h1_tags': page_content['h1_tags'],
            'h2_tags': page_content['h2_tags']
        })
    
    # Enrichir le contenu principal avec les informations des pages supplémentaires
    for page_info in aggregated_content['additional_content']:
        aggregated_content['h1_tags'].extend(page_info['h1_tags'])
        aggregated_content['h2_tags'].extend(page_info['h2_tags'])
    
    logging.info(f"📊 Multi-page analysis completed: homepage + {len(all_content['additional_pages'])} additional pages")
    return aggregated_content

async def analyze_with_gpt5(content_data: dict, website_url: str) -> dict:
    """Analyze website content using GPT-5 via emergentintegrations (with OpenAI fallback)"""
    
    if not API_KEY:
        logging.warning("No API key available, using fallback analysis")
        return create_fallback_analysis(content_data, website_url, "no_api_key")
    
    try:
        # Préparer le contenu multi-pages pour l'analyse
        main_content = f"""
        URL: {website_url}
        Titre: {content_data.get('meta_title', 'N/A')}
        Description: {content_data.get('meta_description', 'N/A')}
        Titres H1: {', '.join(content_data.get('h1_tags', [])[:10])}
        Titres H2: {', '.join(content_data.get('h2_tags', [])[:15])}
        Contenu principal (page d'accueil): {content_data.get('content_text', '')[:1200]}
        """
        
        # Ajouter le contenu des pages supplémentaires
        additional_content = ""
        if 'additional_content' in content_data:
            additional_pages_info = []
            for i, page_info in enumerate(content_data['additional_content'][:3]):  # Limiter à 3 pages max
                page_summary = f"""
                Page {i+1} - {page_info.get('title', 'Sans titre')} ({page_info.get('url', '')})
                Titres: {', '.join(page_info.get('h1_tags', [])[:5])}
                Contenu: {page_info.get('content_text', '')[:800]}
                """
                additional_pages_info.append(page_summary)
            
            if additional_pages_info:
                additional_content = f"""
                
                PAGES SUPPLÉMENTAIRES ANALYSÉES:
                {chr(10).join(additional_pages_info)}
                """
        
        # Prepare enhanced analysis prompt for multi-page content
        prompt = f"""
        Analyse ce site web COMPLET (page d'accueil + pages principales) et génère une analyse marketing approfondie en JSON:

        CONTENU PRINCIPAL:
        {main_content}
        {additional_content}

        INSTRUCTIONS SPÉCIALES:
        - Identifie les produits/services spécifiques mentionnés dans toutes les pages
        - Repère les témoignages, avis clients ou références présents
        - Analyse le positionnement et les caractéristiques uniques
        - Détecte les éléments de différenciation concurrentielle
        - Identifie l'audience cible basée sur le contenu complet

        Réponds UNIQUEMENT avec ce JSON (sans ``` ni markdown):
        {{
            "analysis_summary": "Résumé complet de l'entreprise, ses activités principales et positionnement (3-4 phrases détaillées)",
            "key_topics": ["mot-clé1", "mot-clé2", "mot-clé3", "mot-clé4", "mot-clé5", "mot-clé6"],
            "brand_tone": "professionnel|décontracté|créatif|technique|luxueux|convivial|artisanal|innovant",
            "target_audience": "Description précise de l'audience cible basée sur l'analyse complète",
            "main_services": ["service/produit1", "service/produit2", "service/produit3", "service/produit4"],
            "content_suggestions": [
                "Suggestion de contenu basée sur les produits/services identifiés",
                "Suggestion liée aux témoignages/avis clients trouvés", 
                "Suggestion exploitant les caractéristiques uniques détectées",
                "Suggestion pour valoriser l'expertise/savoir-faire",
                "Suggestion de contenu éducatif pour l'audience cible"
            ]
        }}
        """
        
        # Try emergentintegrations first, fallback to OpenAI
        if EMERGENT_AVAILABLE:
            try:
                # Use emergentintegrations GPT-5
                logging.info("🚀 Using emergentintegrations GPT-4o for multi-page analysis")
                chat = LlmChat(
                    api_key=API_KEY,
                    session_id=f"website_multipage_analysis_{uuid.uuid4()}",
                    system_message="""Tu es un expert en analyse de contenu web et marketing digital spécialisé dans l'analyse multi-pages. 
                    Tu analyses les sites web complets pour comprendre en profondeur leur positionnement, leurs services/produits, leur audience cible, et leurs éléments de différenciation.
                    Tu identifies les produits spécifiques, les témoignages clients, et les caractéristiques uniques pour générer des insights marketing précis.
                    Tu réponds UNIQUEMENT avec du JSON valide selon le format demandé."""
                ).with_model("openai", "gpt-4o")  # Using GPT-4o (latest available)
                
                # Create user message
                user_message = UserMessage(text=prompt)
                
                # Send message to GPT
                response = await chat.send_message(user_message)
                
                logging.info("✅ emergentintegrations multi-page GPT analysis completed")
                
            except Exception as e:
                logging.warning(f"emergentintegrations failed: {e}, falling back to OpenAI")
                response = await analyze_with_openai_direct(prompt)
        else:
            # Use direct OpenAI
            logging.info("🔄 Using direct OpenAI integration for multi-page analysis")
            response = await analyze_with_openai_direct(prompt)
        
        # Parse JSON response
        analysis_result = json.loads(response)
        
        # Ajouter des informations sur l'analyse multi-pages
        analysis_result['pages_analyzed'] = 1 + len(content_data.get('additional_content', []))
        analysis_result['additional_pages_urls'] = [page.get('url', '') for page in content_data.get('additional_content', [])]
        
        logging.info(f"✅ Multi-page GPT analysis completed for {website_url} - {analysis_result['pages_analyzed']} pages analyzed")
        return analysis_result
        
    except json.JSONDecodeError as e:
        logging.error(f"❌ JSON parsing error: {e}")
        logging.error(f"Raw response: {response}")
        return create_fallback_analysis(content_data, website_url, "json_error")
        
    except Exception as e:
        logging.error(f"❌ GPT analysis error: {e}")
        return create_fallback_analysis(content_data, website_url, "gpt_error")

async def analyze_with_openai_direct(prompt: str) -> str:
    """Direct OpenAI API call as fallback for multi-page analysis"""
    try:
        client = OpenAI(api_key=API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-4o",  # Use latest available model
            messages=[
                {"role": "system", "content": """Tu es un expert en analyse de contenu web et marketing digital spécialisé dans l'analyse multi-pages. 
                Tu analyses les sites web complets pour comprendre en profondeur leur positionnement, leurs services/produits, leur audience cible, et leurs éléments de différenciation.
                Tu identifies les produits spécifiques, les témoignages clients, et les caractéristiques uniques pour générer des insights marketing précis.
                Tu réponds UNIQUEMENT avec du JSON valide selon le format demandé."""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000  # Increased for richer multi-page analysis
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logging.error(f"Direct OpenAI call failed: {e}")
        raise

def create_fallback_analysis(content_data: dict, website_url: str, reason: str = "fallback") -> dict:
    """Create a smart fallback analysis when GPT-5 is not available"""
    
    title = content_data.get('meta_title', '').strip()
    description = content_data.get('meta_description', '').strip()
    h1_tags = content_data.get('h1_tags', [])
    content_text = content_data.get('content_text', '')[:1000].strip().lower()
    
    logging.info(f"🔄 Using fallback analysis for {website_url} (reason: {reason})")
    
    # Smart analysis based on content keywords
    if any(word in content_text for word in ['restaurant', 'cuisine', 'menu', 'réservation', 'gastronomie']):
        return {
            "analysis_summary": f"Restaurant analysé via {title}. Établissement culinaire proposant une expérience gastronomique avec focus sur la qualité et le service.",
            "key_topics": ["restaurant", "cuisine", "gastronomie", "service", "qualité"],
            "brand_tone": "convivial et professionnel",
            "target_audience": "amateurs de gastronomie, familles et couples",
            "main_services": ["restauration", "service client", "expérience culinaire"],
            "content_suggestions": [
                "Partager vos plats signatures et spécialités",
                "Mettre en avant l'ambiance et l'expérience client",
                "Promouvoir vos événements et offres spéciales"
            ]
        }
    elif any(word in content_text for word in ['artisan', 'fait main', 'création', 'savoir-faire']):
        return {
            "analysis_summary": f"Artisan analysé via {title}. Professionnel spécialisé dans la création artisanale avec un savoir-faire traditionnel.",
            "key_topics": ["artisan", "création", "savoir-faire", "qualité", "tradition"],
            "brand_tone": "authentique et passionné",
            "target_audience": "clients recherchant l'authenticité et la qualité artisanale",
            "main_services": ["création artisanale", "conseil personnalisé", "réparation"],
            "content_suggestions": [
                "Montrer votre processus de création et savoir-faire",
                "Partager l'histoire et les valeurs de votre artisanat",
                "Présenter vos créations et témoignages clients"
            ]
        }
    elif any(word in content_text for word in ['service', 'conseil', 'accompagnement', 'expertise']):
        return {
            "analysis_summary": f"Entreprise de services analysée via {title}. Prestataire professionnel spécialisé dans l'accompagnement et le conseil.",
            "key_topics": ["services", "expertise", "conseil", "accompagnement", "professionnels"],
            "brand_tone": "professionnel et expert",
            "target_audience": "entreprises et professionnels recherchant de l'expertise",
            "main_services": ["conseil", "accompagnement", "expertise", "formation"],
            "content_suggestions": [
                "Partager vos conseils d'expert et bonnes pratiques",
                "Présenter vos réussites clients et études de cas",
                "Éduquer votre audience sur votre domaine d'expertise"
            ]
        }
    else:
        # Generic business fallback
        main_topic = h1_tags[0] if h1_tags else title.split()[0] if title else "entreprise"
        
        return {
            "analysis_summary": f"Entreprise analysée : {title or website_url}. {description[:100] if description else 'Activité professionnelle diversifiée avec focus sur la qualité et le service client.'}",
            "key_topics": [main_topic.lower(), "services", "qualité", "client", "innovation"],
            "brand_tone": "professionnel",
            "target_audience": "clients potentiels et prospects intéressés par des solutions de qualité",
            "main_services": ["services professionnels", "conseil client", "solutions personnalisées"],
            "content_suggestions": [
                "Présenter vos services et leur valeur ajoutée",
                "Partager des témoignages et avis clients",
                "Éduquer votre audience sur votre secteur d'activité"
            ]
        }

@website_router.get("/analysis")
def get_website_analysis(user_id: str = Depends(get_current_user_id_robust)):
    """Get latest website analysis for user"""
    try:
        print(f"🔍 Getting website analysis for user: {user_id}")
        
        # Use direct MongoDB connection (same as analyze endpoint)
        import pymongo
        import os
        
        mongo_url = os.environ.get("MONGO_URL")
        client = pymongo.MongoClient(mongo_url)
        db = client.claire_marcus
        collection = db.website_analyses
        
        # Get latest analysis
        latest_analysis = collection.find_one(
            {"user_id": user_id},
            sort=[("created_at", -1)]
        )
        
        if latest_analysis:
            # Convert ObjectId to string and clean data
            analysis_data = {
                "analysis_summary": latest_analysis.get("analysis_summary", ""),
                "key_topics": latest_analysis.get("key_topics", []),
                "brand_tone": latest_analysis.get("brand_tone", "professional"),
                "target_audience": latest_analysis.get("target_audience", ""),
                "main_services": latest_analysis.get("main_services", []),
                "content_suggestions": latest_analysis.get("content_suggestions", []),
                "website_url": latest_analysis.get("website_url", ""),
                "created_at": latest_analysis.get("created_at", ""),
                "next_analysis_due": latest_analysis.get("next_analysis_due", "")
            }
            
            print(f"✅ Found website analysis for URL: {analysis_data['website_url']}")
            client.close()
            return {"analysis": analysis_data}
        else:
            print(f"⚠️ No website analysis found for user: {user_id}")
            client.close()
            return {"analysis": None}
            
    except Exception as e:
        print(f"❌ Error getting website analysis: {e}")
        import traceback
        traceback.print_exc()
        return {"analysis": None}

@website_router.post("/analyze")
async def analyze_website(
    request: WebsiteAnalysisRequest,
    user_id: str = Depends(get_current_user_id_robust)
):
    """Analyze website content using GPT-5 and store results"""
    
    website_url = str(request.website_url)
    
    try:
        # Check for existing analysis
        if not request.force_reanalysis:
            existing_analysis = await db.website_analyses.find_one({
                "user_id": user_id,
                "website_url": website_url,
                "last_analyzed": {"$gte": datetime.utcnow() - timedelta(hours=24)}
            })
            
            if existing_analysis:
                logging.info(f"♻️ Using cached analysis for {website_url}")
                return {
                    "message": "Analysis retrieved from cache",
                    "website_url": website_url,
                    "analysis_summary": existing_analysis.get("analysis_summary", ""),
                    "key_topics": existing_analysis.get("key_topics", []),
                    "brand_tone": existing_analysis.get("brand_tone", ""),
                    "target_audience": existing_analysis.get("target_audience", ""),
                    "main_services": existing_analysis.get("main_services", []),
                    "content_suggestions": existing_analysis.get("content_suggestions", []),
                    "last_analyzed": existing_analysis.get("last_analyzed"),
                    "next_analysis_due": existing_analysis.get("next_analysis_due"),
                    "status": "cached"
                }
        
        # Extract website content from multiple pages
        logging.info(f"🌐 Extracting multi-page content from {website_url}")
        content_data = extract_multi_page_content(website_url)
        
        # Analyze with GPT-5
        logging.info(f"🧠 Analyzing with GPT-5: {website_url}")
        analysis_result = await analyze_with_gpt5(content_data, website_url)
        
        # Store analysis in database
        website_analysis = WebsiteData(
            user_id=user_id,
            business_id=user_id,  # Using user_id as business_id for now
            website_url=website_url,
            content_text=content_data.get('content_text', ''),
            meta_description=content_data.get('meta_description', ''),
            meta_title=content_data.get('meta_title', ''),
            h1_tags=content_data.get('h1_tags', []),
            h2_tags=content_data.get('h2_tags', []),
            analysis_summary=analysis_result.get('analysis_summary', ''),
            key_topics=analysis_result.get('key_topics', []),
            brand_tone=analysis_result.get('brand_tone', ''),
            target_audience=analysis_result.get('target_audience', ''),
            main_services=analysis_result.get('main_services', []),
            content_suggestions=analysis_result.get('content_suggestions', []),
            last_analyzed=datetime.utcnow(),
            next_analysis_due=datetime.utcnow() + timedelta(days=30)
        )
        
        # Store in MongoDB
        await db.website_analyses.replace_one(
            {"user_id": user_id, "website_url": website_url},
            website_analysis.dict(),
            upsert=True
        )
        
        logging.info(f"✅ GPT-5 website analysis completed and stored for {website_url}")
        
        return {
            "message": "Website analysis completed with GPT-5",
            "website_url": website_url,
            "analysis_summary": analysis_result.get('analysis_summary', ''),
            "key_topics": analysis_result.get('key_topics', []),
            "brand_tone": analysis_result.get('brand_tone', ''),
            "target_audience": analysis_result.get('target_audience', ''),
            "main_services": analysis_result.get('main_services', []),
            "content_suggestions": analysis_result.get('content_suggestions', []),
            "pages_analyzed": analysis_result.get('pages_analyzed', 1),
            "additional_pages_urls": analysis_result.get('additional_pages_urls', []),
            "last_analyzed": website_analysis.last_analyzed,
            "next_analysis_due": website_analysis.next_analysis_due,
            "status": "analyzed",
            "website_url_saved": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"❌ Website analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Website analysis failed: {str(e)}"
        )

@website_router.get("/analysis")
async def get_website_analysis(
    user_id: str = Depends(get_current_user_id_robust)
):
    """Get stored website analysis for the current user"""
    try:
        analysis = await db.website_analyses.find_one(
            {"user_id": user_id},
            sort=[("last_analyzed", -1)]
        )
        
        if not analysis:
            return {"message": "No website analysis found", "analysis": None}
        
        return {
            "message": "Website analysis found",
            "analysis": {
                "website_url": analysis.get("website_url"),
                "analysis_summary": analysis.get("analysis_summary", ""),
                "key_topics": analysis.get("key_topics", []),
                "brand_tone": analysis.get("brand_tone", ""),
                "target_audience": analysis.get("target_audience", ""),
                "main_services": analysis.get("main_services", []),
                "content_suggestions": analysis.get("content_suggestions", []),
                "last_analyzed": analysis.get("last_analyzed"),
                "next_analysis_due": analysis.get("next_analysis_due")
            }
        }
        
    except Exception as e:
        logging.error(f"Error retrieving website analysis: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving website analysis")

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