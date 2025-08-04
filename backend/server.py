from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import base64
import json
from emergentintegrations.llm.chat import LlmChat, UserMessage, FileContentWithMimeType
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create uploads directory
UPLOAD_DIR = ROOT_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Pydantic Models
class BusinessProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    business_name: str
    business_type: str
    target_audience: str
    brand_tone: str  # professional, casual, friendly, etc.
    posting_frequency: str  # daily, 3x/week, weekly
    preferred_platforms: List[str]  # facebook, instagram, linkedin
    budget_range: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BusinessProfileCreate(BaseModel):
    business_name: str
    business_type: str
    target_audience: str
    brand_tone: str
    posting_frequency: str
    preferred_platforms: List[str]
    budget_range: str

class ContentUpload(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    business_id: str
    file_path: str
    file_type: str  # image or video
    description: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

class GeneratedPost(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    business_id: str
    content_id: str
    platform: str  # facebook, instagram, linkedin
    post_text: str
    hashtags: List[str]
    scheduled_date: datetime
    status: str = "pending"  # pending, approved, rejected, posted
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PostCalendar(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    business_id: str
    month: str  # YYYY-MM format
    posts: List[GeneratedPost]
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Helper function to analyze content with OpenAI
async def analyze_content_with_ai(content_path: str, description: str, business_profile: BusinessProfile):
    try:
        # Create LLM chat instance
        chat = LlmChat(
            api_key=os.environ['OPENAI_API_KEY'],
            session_id=f"content_analysis_{uuid.uuid4()}",
            system_message=f"""Tu es un expert en marketing digital et réseaux sociaux. 
            Voici le profil de l'entreprise:
            - Nom: {business_profile.business_name}
            - Type: {business_profile.business_type}
            - Audience cible: {business_profile.target_audience}
            - Ton de marque: {business_profile.brand_tone}
            - Plateformes: {', '.join(business_profile.preferred_platforms)}
            
            Ta mission est d'analyser le contenu fourni et de générer des posts optimisés pour chaque plateforme."""
        ).with_model("openai", "gpt-4o")

        # Create file content for image analysis
        file_content = FileContentWithMimeType(
            file_path=content_path,
            mime_type="image/jpeg" if content_path.lower().endswith(('.jpg', '.jpeg')) else "image/png"
        )

        # Generate posts for each platform
        generated_posts = []
        
        for platform in business_profile.preferred_platforms:
            platform_prompt = f"""
            Analyse cette image et la description fournie: "{description}"
            
            Génère un post optimisé pour {platform} qui:
            1. Respecte le ton de marque ({business_profile.brand_tone})
            2. S'adresse à l'audience cible ({business_profile.target_audience})
            3. Inclut des hashtags pertinents
            4. Respecte les meilleures pratiques de {platform}
            
            Format de réponse JSON:
            {{
                "post_text": "texte du post",
                "hashtags": ["hashtag1", "hashtag2", "hashtag3"]
            }}
            """

            user_message = UserMessage(
                text=platform_prompt,
                file_contents=[file_content]
            )

            response = await chat.send_message(user_message)
            
            try:
                # Parse JSON response
                post_data = json.loads(response)
                generated_posts.append({
                    "platform": platform,
                    "post_text": post_data.get("post_text", ""),
                    "hashtags": post_data.get("hashtags", [])
                })
            except:
                # Fallback if JSON parsing fails
                generated_posts.append({
                    "platform": platform,
                    "post_text": response,
                    "hashtags": []
                })
        
        return generated_posts
    except Exception as e:
        logging.error(f"Error analyzing content with AI: {e}")
        return []

# API Routes
@api_router.post("/business-profile", response_model=BusinessProfile)
async def create_business_profile(profile_data: BusinessProfileCreate):
    """Create a new business profile"""
    profile = BusinessProfile(**profile_data.dict())
    await db.business_profiles.insert_one(profile.dict())
    return profile

@api_router.get("/business-profile/{profile_id}", response_model=BusinessProfile)
async def get_business_profile(profile_id: str):
    """Get business profile by ID"""
    profile = await db.business_profiles.find_one({"id": profile_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Business profile not found")
    return BusinessProfile(**profile)

@api_router.get("/business-profiles", response_model=List[BusinessProfile])
async def get_all_business_profiles():
    """Get all business profiles"""
    profiles = await db.business_profiles.find().to_list(100)
    return [BusinessProfile(**profile) for profile in profiles]

@api_router.post("/upload-content/{business_id}")
async def upload_content(
    business_id: str,
    file: UploadFile = File(...),
    description: str = Form(...)
):
    """Upload content (image/video) with description"""
    try:
        # Get business profile
        business_profile = await db.business_profiles.find_one({"id": business_id})
        if not business_profile:
            raise HTTPException(status_code=404, detail="Business profile not found")
        
        # Save uploaded file
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        file_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{file_id}.{file_extension}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Create content record
        content_upload = ContentUpload(
            business_id=business_id,
            file_path=str(file_path),
            file_type="image" if file.content_type.startswith("image") else "video",
            description=description
        )
        
        await db.content_uploads.insert_one(content_upload.dict())
        
        # Analyze content with AI and generate posts
        business_prof = BusinessProfile(**business_profile)
        generated_posts_data = await analyze_content_with_ai(str(file_path), description, business_prof)
        
        # Save generated posts to database
        current_date = datetime.utcnow()
        for i, post_data in enumerate(generated_posts_data):
            # Schedule posts across the next few days
            scheduled_date = current_date + timedelta(days=i+1)
            
            generated_post = GeneratedPost(
                business_id=business_id,
                content_id=content_upload.id,
                platform=post_data["platform"],
                post_text=post_data["post_text"],
                hashtags=post_data["hashtags"],
                scheduled_date=scheduled_date
            )
            
            await db.generated_posts.insert_one(generated_post.dict())
        
        return {
            "message": "Content uploaded and analyzed successfully",
            "content_id": content_upload.id,
            "generated_posts_count": len(generated_posts_data)
        }
        
    except Exception as e:
        logging.error(f"Error uploading content: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading content: {str(e)}")

@api_router.get("/generated-posts/{business_id}", response_model=List[GeneratedPost])
async def get_generated_posts(business_id: str):
    """Get all generated posts for a business"""
    posts = await db.generated_posts.find({"business_id": business_id}).to_list(1000)
    return [GeneratedPost(**post) for post in posts]

@api_router.put("/post/{post_id}/approve")
async def approve_post(post_id: str):
    """Approve a generated post"""
    result = await db.generated_posts.update_one(
        {"id": post_id},
        {"$set": {"status": "approved"}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post approved successfully"}

@api_router.put("/post/{post_id}/reject")
async def reject_post(post_id: str):
    """Reject a generated post"""
    result = await db.generated_posts.update_one(
        {"id": post_id},
        {"$set": {"status": "rejected"}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post rejected successfully"}

@api_router.put("/post/{post_id}/edit")
async def edit_post(post_id: str, new_text: str = Form(...)):
    """Edit a generated post"""
    result = await db.generated_posts.update_one(
        {"id": post_id},
        {"$set": {"post_text": new_text, "status": "approved"}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post updated successfully"}

@api_router.get("/calendar/{business_id}")
async def get_calendar(business_id: str):
    """Get calendar view of posts for a business"""
    posts = await db.generated_posts.find({"business_id": business_id}).to_list(1000)
    
    # Group posts by month
    calendar_data = {}
    for post in posts:
        post_obj = GeneratedPost(**post)
        month_key = post_obj.scheduled_date.strftime("%Y-%m")
        if month_key not in calendar_data:
            calendar_data[month_key] = []
        calendar_data[month_key].append(post_obj)
    
    return calendar_data

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()