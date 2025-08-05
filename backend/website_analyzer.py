from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, HttpUrl
import uuid
import requests
from bs4 import BeautifulSoup
import openai
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pathlib import Path
from dotenv import load_dotenv
from auth import get_current_active_user, User

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# OpenAI configuration
openai.api_key = os.environ.get('OPENAI_API_KEY', '')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'socialgenie')]

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
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    next_analysis_due: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=90))

class WebsiteAnalysisResponse(BaseModel):
    id: str
    website_url: str
    analysis_summary: str
    key_topics: list
    brand_tone: str
    target_audience: str
    main_services: list
    last_analyzed: datetime
    next_analysis_due: datetime

def extract_website_content(url: str) -> dict:
    """Extract content from a website URL"""
    try:
        # Add headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(str(url), headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract various elements
        title = soup.find('title')
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        h1_tags = [h1.get_text().strip() for h1 in soup.find_all('h1')]
        h2_tags = [h2.get_text().strip() for h2 in soup.find_all('h2')]
        
        # Get main content text
        text_content = soup.get_text()
        lines = (line.strip() for line in text_content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        content_text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Limit content length to avoid token limits
        content_text = content_text[:8000]  # Limit to ~8000 chars
        
        return {
            'content_text': content_text,
            'meta_title': title.get_text().strip() if title else '',
            'meta_description': meta_desc.get('content', '') if meta_desc else '',
            'h1_tags': h1_tags[:5],  # Limit to first 5
            'h2_tags': h2_tags[:10],  # Limit to first 10
        }
        
    except Exception as e:
        logging.error(f"Error extracting website content: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to extract content from website: {str(e)}"
        )

def analyze_website_with_gpt(content_data: dict, website_url: str) -> dict:
    """Analyze website content using OpenAI GPT"""
    try:
        if not openai.api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OpenAI API key not configured"
            )
        
        prompt = f"""
        Analysez le contenu de ce site web et fournissez une analyse structurée pour l'utilisation dans des posts sur les réseaux sociaux.

        URL du site: {website_url}
        Titre: {content_data['meta_title']}
        Description: {content_data['meta_description']}
        Titres H1: {', '.join(content_data['h1_tags'])}
        Titres H2: {', '.join(content_data['h2_tags'][:5])}
        
        Contenu principal:
        {content_data['content_text'][:3000]}

        Fournissez une analyse JSON avec les éléments suivants:
        {{
            "analysis_summary": "Résumé concis de l'activité et proposition de valeur",
            "key_topics": ["topic1", "topic2", "topic3"],
            "brand_tone": "description du ton de marque (professionnel, décontracté, etc.)",
            "target_audience": "description de l'audience cible",
            "main_services": ["service1", "service2", "service3"]
        }}
        
        Répondez UNIQUEMENT avec le JSON valide, sans texte supplémentaire.
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Tu es un expert en analyse de contenu web et marketing digital. Tu réponds uniquement avec du JSON valide."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.3
        )
        
        import json
        analysis_result = json.loads(response.choices[0].message.content)
        
        return analysis_result
        
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing GPT response: {e}")
        # Fallback analysis
        return {
            "analysis_summary": f"Site web analysé: {content_data['meta_title']}",
            "key_topics": ["business", "services", "entreprise"],
            "brand_tone": "professionnel",
            "target_audience": "clients potentiels",
            "main_services": ["services principaux"]
        }
    except Exception as e:
        logging.error(f"Error with GPT analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error analyzing website content"
        )

@website_router.post("/analyze", response_model=WebsiteAnalysisResponse)
async def analyze_website(
    request: WebsiteAnalysisRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Analyze a website and store the analysis"""
    try:
        # Get user's business profile
        business_profile = await db.business_profiles.find_one({"user_id": current_user.id})
        if not business_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business profile not found. Please create your business profile first."
            )
        
        website_url = str(request.website_url)
        
        # Check if we have a recent analysis (unless force reanalysis)
        if not request.force_reanalysis:
            existing_analysis = await db.website_analyses.find_one({
                "user_id": current_user.id,
                "website_url": website_url,
                "created_at": {"$gte": datetime.utcnow() - timedelta(days=7)}  # Recent analysis
            })
            
            if existing_analysis:
                return WebsiteAnalysisResponse(**existing_analysis)
        
        # Extract content from website
        content_data = extract_website_content(website_url)
        
        # Analyze with GPT
        analysis_result = analyze_website_with_gpt(content_data, website_url)
        
        # Create website data object
        website_data = WebsiteData(
            user_id=current_user.id,
            business_id=business_profile['id'],
            website_url=website_url,
            content_text=content_data['content_text'],
            meta_title=content_data['meta_title'],
            meta_description=content_data['meta_description'],
            h1_tags=content_data['h1_tags'],
            h2_tags=content_data['h2_tags'],
            analysis_summary=analysis_result.get('analysis_summary', ''),
            key_topics=analysis_result.get('key_topics', []),
            brand_tone=analysis_result.get('brand_tone', ''),
            target_audience=analysis_result.get('target_audience', ''),
            main_services=analysis_result.get('main_services', [])
        )
        
        # Store in database (replace existing if any)
        await db.website_analyses.delete_many({
            "user_id": current_user.id,
            "website_url": website_url
        })
        
        await db.website_analyses.insert_one(website_data.dict())
        
        # Update business profile with website URL if not set
        await db.business_profiles.update_one(
            {"user_id": current_user.id},
            {
                "$set": {
                    "website_url": website_url,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return WebsiteAnalysisResponse(
            id=website_data.id,
            website_url=website_data.website_url,
            analysis_summary=website_data.analysis_summary,
            key_topics=website_data.key_topics,
            brand_tone=website_data.brand_tone,
            target_audience=website_data.target_audience,
            main_services=website_data.main_services,
            last_analyzed=website_data.created_at,
            next_analysis_due=website_data.next_analysis_due
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error analyzing website: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error analyzing website"
        )

@website_router.get("/analysis", response_model=Optional[WebsiteAnalysisResponse])
async def get_website_analysis(current_user: User = Depends(get_current_active_user)):
    """Get the latest website analysis for the user"""
    try:
        analysis = await db.website_analyses.find_one(
            {"user_id": current_user.id},
            sort=[("created_at", -1)]
        )
        
        if not analysis:
            return None
            
        return WebsiteAnalysisResponse(**analysis)
        
    except Exception as e:
        logging.error(f"Error getting website analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving website analysis"
        )

@website_router.delete("/analysis")
async def delete_website_analysis(current_user: User = Depends(get_current_active_user)):
    """Delete website analysis for the user"""
    try:
        result = await db.website_analyses.delete_many({"user_id": current_user.id})
        
        return {
            "message": f"Deleted {result.deleted_count} website analysis(es)",
            "deleted_count": result.deleted_count
        }
        
    except Exception as e:
        logging.error(f"Error deleting website analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting website analysis"
        )