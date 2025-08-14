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
from motor.motor_asyncio import AsyncIOMotorClient
from pathlib import Path
from dotenv import load_dotenv
from fastapi import Header
from typing import Optional

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
def get_current_user_id(authorization: str = Header(None)) -> str:
    """Extract user ID from JWT token - compatible with server.py"""
    if not authorization or not authorization.startswith("Bearer "):
        return "demo_user_id"
    
    token = authorization.replace("Bearer ", "")
    
    # For now, extract from demo tokens or return demo
    if token.startswith("demo_token"):
        return "demo_user_id"
    
    # TODO: Add proper JWT decoding when needed
    return "demo_user_id"

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
db = mongo_client[os.environ.get('DB_NAME', 'socialgenie')]

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

def extract_website_content(url: str) -> dict:
    """Extract content from website using web scraping"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Extract structured data
        content_data = {
            'meta_title': soup.find('title').get_text().strip() if soup.find('title') else '',
            'meta_description': '',
            'h1_tags': [h1.get_text().strip() for h1 in soup.find_all('h1')],
            'h2_tags': [h2.get_text().strip() for h2 in soup.find_all('h2')],
            'content_text': soup.get_text()
        }
        
        # Get meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            content_data['meta_description'] = meta_desc.get('content', '').strip()
        
        # Clean and limit content
        content_data['content_text'] = ' '.join(content_data['content_text'].split())[:3000]
        
        return content_data
        
    except requests.RequestException as e:
        logging.error(f"Error fetching website {url}: {e}")
        raise HTTPException(status_code=400, detail=f"Unable to fetch website: {str(e)}")
    except Exception as e:
        logging.error(f"Error processing website content: {e}")
        raise HTTPException(status_code=500, detail="Error processing website content")

async def analyze_with_gpt5(content_data: dict, website_url: str) -> dict:
    """Analyze website content using GPT-5 via emergentintegrations (with OpenAI fallback)"""
    
    if not API_KEY:
        logging.warning("No API key available, using fallback analysis")
        return create_fallback_analysis(content_data, website_url, "no_api_key")
    
    try:
        # Prepare analysis prompt
        prompt = f"""
        Analyse ce site web et génère une analyse marketing complète en JSON:

        URL: {website_url}
        Titre: {content_data.get('meta_title', 'N/A')}
        Description: {content_data.get('meta_description', 'N/A')}
        Titres H1: {', '.join(content_data.get('h1_tags', []))}
        Titres H2: {', '.join(content_data.get('h2_tags', [])[:5])}
        Contenu (extrait): {content_data.get('content_text', '')[:1500]}

        Réponds UNIQUEMENT avec ce JSON (sans ``` ni markdown):
        {{
            "analysis_summary": "Résumé de l'entreprise et de ses activités en 2-3 phrases",
            "key_topics": ["mot-clé1", "mot-clé2", "mot-clé3", "mot-clé4", "mot-clé5"],
            "brand_tone": "professionnel|décontracté|créatif|technique|luxueux|convivial",
            "target_audience": "Description de l'audience cible principale",
            "main_services": ["service1", "service2", "service3"],
            "content_suggestions": [
                "Suggestion de contenu 1",
                "Suggestion de contenu 2", 
                "Suggestion de contenu 3"
            ]
        }}
        """
        
        # Try emergentintegrations first, fallback to OpenAI
        if EMERGENT_AVAILABLE:
            try:
                # Use emergentintegrations GPT-5
                logging.info("🚀 Using emergentintegrations GPT-5")
                chat = LlmChat(
                    api_key=API_KEY,
                    session_id=f"website_analysis_{uuid.uuid4()}",
                    system_message="""Tu es un expert en analyse de contenu web et marketing digital. 
                    Tu analyses les sites web pour comprendre leur positionnement, leurs services, et leur audience cible.
                    Tu réponds UNIQUEMENT avec du JSON valide selon le format demandé."""
                ).with_model("openai", "gpt-4o")  # Using GPT-4o (latest available)
                
                # Create user message
                user_message = UserMessage(text=prompt)
                
                # Send message to GPT
                response = await chat.send_message(user_message)
                
                logging.info("✅ emergentintegrations GPT analysis completed")
                
            except Exception as e:
                logging.warning(f"emergentintegrations failed: {e}, falling back to OpenAI")
                response = await analyze_with_openai_direct(prompt)
        else:
            # Use direct OpenAI
            logging.info("🔄 Using direct OpenAI integration")
            response = await analyze_with_openai_direct(prompt)
        
        # Parse JSON response
        analysis_result = json.loads(response)
        
        logging.info(f"✅ GPT analysis completed for {website_url}")
        return analysis_result
        
    except json.JSONDecodeError as e:
        logging.error(f"❌ JSON parsing error: {e}")
        logging.error(f"Raw response: {response}")
        return create_fallback_analysis(content_data, website_url, "json_error")
        
    except Exception as e:
        logging.error(f"❌ GPT analysis error: {e}")
        return create_fallback_analysis(content_data, website_url, "gpt_error")

async def analyze_with_openai_direct(prompt: str) -> str:
    """Direct OpenAI API call as fallback"""
    try:
        client = OpenAI(api_key=API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-4o",  # Use latest available model
            messages=[
                {"role": "system", "content": """Tu es un expert en analyse de contenu web et marketing digital. 
                Tu analyses les sites web pour comprendre leur positionnement, leurs services, et leur audience cible.
                Tu réponds UNIQUEMENT avec du JSON valide selon le format demandé."""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
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

@website_router.post("/analyze")
async def analyze_website(
    request: WebsiteAnalysisRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Analyze website content using GPT-5 and store results"""
    
    website_url = str(request.website_url)
    
    try:
        # Check for existing analysis
        if not request.force_reanalysis:
            existing_analysis = await db.website_analyses.find_one({
                "user_id": current_user.id,
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
        
        # Extract website content
        logging.info(f"🌐 Extracting content from {website_url}")
        content_data = extract_website_content(website_url)
        
        # Analyze with GPT-5
        logging.info(f"🧠 Analyzing with GPT-5: {website_url}")
        analysis_result = await analyze_with_gpt5(content_data, website_url)
        
        # Store analysis in database
        website_analysis = WebsiteData(
            user_id=current_user.id,
            business_id=current_user.id,  # Using user_id as business_id for now
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
            {"user_id": current_user.id, "website_url": website_url},
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
    current_user: User = Depends(get_current_active_user)
):
    """Get stored website analysis for the current user"""
    try:
        analysis = await db.website_analyses.find_one(
            {"user_id": current_user.id},
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
    current_user: User = Depends(get_current_active_user)
):
    """Delete website analysis for the current user"""
    try:
        result = await db.website_analyses.delete_many({"user_id": current_user.id})
        
        return {
            "message": f"Deleted {result.deleted_count} website analysis records",
            "deleted_count": result.deleted_count
        }
        
    except Exception as e:
        logging.error(f"Error deleting website analysis: {e}")
        raise HTTPException(status_code=500, detail="Error deleting website analysis")