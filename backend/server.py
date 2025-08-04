from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form, Depends
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
from emergentintegrations.llm.chat import LlmChat, UserMessage, FileContentWithMimeType, ImageContent
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
    logo_url: Optional[str] = None  # NEW: Logo URL
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BusinessProfileCreate(BaseModel):
    business_name: str
    business_type: str
    target_audience: str
    brand_tone: str
    posting_frequency: str
    preferred_platforms: List[str]
    budget_range: str

class BusinessProfileUpdate(BaseModel):
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    target_audience: Optional[str] = None
    brand_tone: Optional[str] = None
    posting_frequency: Optional[str] = None
    preferred_platforms: Optional[List[str]] = None
    budget_range: Optional[str] = None

class ContentUpload(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    business_id: str
    file_path: str
    file_type: str  # image, video, note
    description: Optional[str] = None  # Can be empty initially
    title: Optional[str] = None  # For notes
    content_text: Optional[str] = None  # For text notes
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending_description"  # pending_description, ready, processed

class ContentNote(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    business_id: str
    title: str
    content: str
    priority: str = "normal"  # high, normal, low
    active_until: Optional[datetime] = None  # For time-sensitive notes
    created_at: datetime = Field(default_factory=datetime.utcnow)

class GeneratedPost(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    business_id: str
    content_id: Optional[str] = None  # Can be None for auto-generated content
    platform: str  # facebook, instagram, linkedin
    post_text: str
    hashtags: List[str]
    scheduled_date: datetime
    scheduled_time: str = "09:00"  # NEW: Scheduled time
    status: str = "pending"  # pending, approved, rejected, posted, scheduled
    auto_generated: bool = False  # NEW: Flag for auto-generated content
    visual_url: Optional[str] = None  # NEW: Associated visual
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PostScheduleUpdate(BaseModel):
    scheduled_date: datetime
    scheduled_time: str

class PostCalendar(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    business_id: str
    month: str  # YYYY-MM format
    posts: List[GeneratedPost]
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Helper function to analyze content with OpenAI
async def analyze_content_with_ai(content_path: str, description: str, business_profile: BusinessProfile, notes: List[ContentNote] = []):
    try:
        # Convert image to base64 for OpenAI
        with open(content_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Prepare notes context
        notes_context = ""
        if notes:
            notes_context = "\n\nNotes importantes à prendre en compte:\n"
            for note in notes:
                notes_context += f"- {note.title}: {note.content}\n"
        
        # Create LLM chat instance with OpenAI
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
            {notes_context}
            
            Ta mission est d'analyser le contenu fourni et de générer des posts optimisés pour chaque plateforme."""
        ).with_model("openai", "gpt-4o")

        # Generate posts for each platform
        generated_posts = []
        
        for platform in business_profile.preferred_platforms:
            try:
                # Platform-specific optimizations
                platform_specs = {
                    "facebook": {"max_chars": 2000, "hashtags_max": 5, "style": "engageant et communautaire"},
                    "instagram": {"max_chars": 2200, "hashtags_max": 10, "style": "visuel et inspirant"},
                    "linkedin": {"max_chars": 3000, "hashtags_max": 3, "style": "professionnel et informatif"}
                }
                
                specs = platform_specs.get(platform, {"max_chars": 2000, "hashtags_max": 5, "style": "engageant"})
                
                platform_prompt = f"""
                Analyse cette image et la description fournie: "{description}"
                
                Génère un post optimisé pour {platform} qui:
                1. Respecte le ton de marque ({business_profile.brand_tone})
                2. S'adresse à l'audience cible ({business_profile.target_audience})
                3. Style {specs['style']}
                4. Maximum {specs['max_chars']} caractères
                5. Maximum {specs['hashtags_max']} hashtags pertinents
                6. Intègre les notes importantes si pertinentes
                
                Format de réponse JSON strict:
                {{
                    "post_text": "texte du post ici",
                    "hashtags": ["hashtag1", "hashtag2", "hashtag3"]
                }}
                """

                # Create image content with base64
                from emergentintegrations.llm.chat import ImageContent
                image_content = ImageContent(image_base64=image_data)
                
                user_message = UserMessage(
                    text=platform_prompt,
                    file_contents=[image_content]
                )

                response = await chat.send_message(user_message)
                
                try:
                    # Clean response and parse JSON
                    response_clean = response.strip()
                    if response_clean.startswith('```json'):
                        response_clean = response_clean[7:-3].strip()
                    elif response_clean.startswith('```'):
                        response_clean = response_clean[3:-3].strip()
                    
                    post_data = json.loads(response_clean)
                    generated_posts.append({
                        "platform": platform,
                        "post_text": post_data.get("post_text", ""),
                        "hashtags": post_data.get("hashtags", [])
                    })
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    logging.warning(f"Failed to parse JSON for {platform}, using raw response")
                    generated_posts.append({
                        "platform": platform,
                        "post_text": response[:specs['max_chars']],  # Respect platform limits
                        "hashtags": []
                    })
            except Exception as platform_error:
                logging.error(f"Error generating post for {platform}: {platform_error}")
                # Create a fallback post
                generated_posts.append({
                    "platform": platform,
                    "post_text": f"Découvrez notre nouveau contenu ! {description[:100]}",
                    "hashtags": ["nouveau", "contenu", business_profile.business_type.replace(' ', '')]
                })
        
        return generated_posts
    except Exception as e:
        logging.error(f"Error analyzing content with AI: {e}")
        # Return fallback posts if AI fails
        fallback_posts = []
        for platform in business_profile.preferred_platforms:
            fallback_posts.append({
                "platform": platform,
                "post_text": f"Nouveau contenu de {business_profile.business_name}! {description[:100]}",
                "hashtags": ["nouveau", "contenu", business_profile.business_type.replace(' ', '')]
            })
        return fallback_posts

# Helper function to generate automatic content when user content is insufficient
async def generate_automatic_content(business_profile: BusinessProfile, notes: List[ContentNote] = []):
    try:
        chat = LlmChat(
            api_key=os.environ['OPENAI_API_KEY'],
            session_id=f"auto_content_{uuid.uuid4()}",
            system_message=f"""Tu es un expert en création de contenu automatique pour les réseaux sociaux.
            
            Profil de l'entreprise:
            - Nom: {business_profile.business_name}
            - Type: {business_profile.business_type}
            - Audience: {business_profile.target_audience}
            - Ton: {business_profile.brand_tone}
            
            Crée du contenu automatique naturel (citations, conseils, informations) 
            en rapport avec l'activité, sans que cela paraisse généré par IA."""
        ).with_model("openai", "gpt-4o")

        # Generate different types of content
        content_types = ["citation_inspirante", "conseil_pratique", "information_secteur"]
        generated_posts = []
        
        for platform in business_profile.preferred_platforms:
            for content_type in content_types:
                prompt = f"""
                Génère un {content_type} pour {platform} adapté à une entreprise {business_profile.business_type}.
                
                Format JSON:
                {{
                    "post_text": "contenu ici",
                    "hashtags": ["hashtag1", "hashtag2"],
                    "content_type": "{content_type}"
                }}
                """
                
                response = await chat.send_message(UserMessage(text=prompt))
                
                try:
                    response_clean = response.strip()
                    if response_clean.startswith('```json'):
                        response_clean = response_clean[7:-3].strip()
                    
                    post_data = json.loads(response_clean)
                    generated_posts.append({
                        "platform": platform,
                        "post_text": post_data.get("post_text", ""),
                        "hashtags": post_data.get("hashtags", []),
                        "auto_generated": True,
                        "content_type": content_type
                    })
                except:
                    # Fallback
                    generated_posts.append({
                        "platform": platform,
                        "post_text": f"Contenu informatif pour {business_profile.business_name}",
                        "hashtags": [business_profile.business_type.replace(' ', '')],
                        "auto_generated": True
                    })
        
        return generated_posts[:6]  # Limit to 6 auto-generated posts
    except Exception as e:
        logging.error(f"Error generating automatic content: {e}")
        return []

# API Routes

@api_router.post("/business-profile", response_model=BusinessProfile)
async def create_business_profile(profile_data: BusinessProfileCreate):
    """Create a new business profile"""
    profile = BusinessProfile(**profile_data.dict())
    await db.business_profiles.insert_one(profile.dict())
    return profile

@api_router.put("/business-profile/{profile_id}", response_model=BusinessProfile)
async def update_business_profile(profile_id: str, update_data: BusinessProfileUpdate):
    """Update business profile"""
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.utcnow()
    
    result = await db.business_profiles.update_one(
        {"id": profile_id}, 
        {"$set": update_dict}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Business profile not found")
    
    profile = await db.business_profiles.find_one({"id": profile_id})
    return BusinessProfile(**profile)

@api_router.post("/business-profile/{profile_id}/logo")
async def upload_business_logo(profile_id: str, file: UploadFile = File(...)):
    """Upload business logo"""
    try:
        # Check if profile exists
        profile = await db.business_profiles.find_one({"id": profile_id})
        if not profile:
            raise HTTPException(status_code=404, detail="Business profile not found")
        
        # Save logo file
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'png'
        logo_filename = f"logo_{profile_id}.{file_extension}"
        logo_path = UPLOAD_DIR / logo_filename
        
        with open(logo_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Update profile with logo URL
        logo_url = f"/uploads/{logo_filename}"
        await db.business_profiles.update_one(
            {"id": profile_id},
            {"$set": {"logo_url": logo_url, "updated_at": datetime.utcnow()}}
        )
        
        return {"message": "Logo uploaded successfully", "logo_url": logo_url}
        
    except Exception as e:
        logging.error(f"Error uploading logo: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading logo: {str(e)}")

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

@api_router.post("/upload-content-batch/{business_id}")
async def upload_content_batch(
    business_id: str,
    files: List[UploadFile] = File(...)
):
    """Upload multiple content files at once"""
    try:
        # Get business profile
        business_profile = await db.business_profiles.find_one({"id": business_id})
        if not business_profile:
            raise HTTPException(status_code=404, detail="Business profile not found")
        
        uploaded_content = []
        
        for file in files:
            # Save uploaded file
            file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
            file_id = str(uuid.uuid4())
            file_path = UPLOAD_DIR / f"{file_id}.{file_extension}"
            
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Create content record (without description initially)
            content_upload = ContentUpload(
                business_id=business_id,
                file_path=str(file_path),
                file_type="image" if file.content_type.startswith("image") else "video",
                status="pending_description"
            )
            
            await db.content_uploads.insert_one(content_upload.dict())
            uploaded_content.append(content_upload)
        
        return {
            "message": f"{len(uploaded_content)} files uploaded successfully",
            "uploaded_content": [{"id": c.id, "file_path": c.file_path} for c in uploaded_content]
        }
        
    except Exception as e:
        logging.error(f"Error uploading batch content: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading content: {str(e)}")

@api_router.put("/content/{content_id}/describe")
async def add_content_description(content_id: str, description: str = Form(...)):
    """Add description to uploaded content"""
    try:
        result = await db.content_uploads.update_one(
            {"id": content_id},
            {"$set": {"description": description, "status": "ready"}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Content not found")
        
        return {"message": "Description added successfully"}
        
    except Exception as e:
        logging.error(f"Error adding description: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/content/{business_id}/pending-description")
async def get_pending_description_content(business_id: str):
    """Get content that needs description"""
    content = await db.content_uploads.find({
        "business_id": business_id,
        "status": "pending_description"
    }).to_list(100)
    
    return [ContentUpload(**c) for c in content]

@api_router.post("/notes/{business_id}")
async def create_content_note(business_id: str, note: ContentNote):
    """Create a content note"""
    note.business_id = business_id
    await db.content_notes.insert_one(note.dict())
    return note

@api_router.get("/notes/{business_id}")
async def get_content_notes(business_id: str):
    """Get all content notes for a business"""
    notes = await db.content_notes.find({"business_id": business_id}).to_list(100)
    return [ContentNote(**note) for note in notes]

@api_router.post("/generate-posts/{business_id}")
async def generate_posts_for_business(business_id: str):
    """Generate posts for all ready content + auto content if needed"""
    try:
        # Get business profile
        business_profile = await db.business_profiles.find_one({"id": business_id})
        if not business_profile:
            raise HTTPException(status_code=404, detail="Business profile not found")
        
        business_prof = BusinessProfile(**business_profile)
        
        # Get ready content
        ready_content = await db.content_uploads.find({
            "business_id": business_id,
            "status": "ready"
        }).to_list(100)
        
        # Get active notes
        notes = await db.content_notes.find({
            "business_id": business_id,
            "$or": [
                {"active_until": {"$gte": datetime.utcnow()}},
                {"active_until": None}
            ]
        }).to_list(100)
        
        notes_list = [ContentNote(**note) for note in notes]
        
        all_generated_posts = []
        
        # Generate posts from user content
        for content in ready_content:
            content_obj = ContentUpload(**content)
            if content_obj.description:  # Only process content with descriptions
                generated_posts_data = await analyze_content_with_ai(
                    content_obj.file_path, 
                    content_obj.description, 
                    business_prof,
                    notes_list
                )
                
                # Save generated posts to database
                current_date = datetime.utcnow()
                for i, post_data in enumerate(generated_posts_data):
                    # Schedule posts across the next few days
                    scheduled_date = current_date + timedelta(days=i+1)
                    
                    generated_post = GeneratedPost(
                        business_id=business_id,
                        content_id=content_obj.id,
                        platform=post_data["platform"],
                        post_text=post_data["post_text"],
                        hashtags=post_data["hashtags"],
                        scheduled_date=scheduled_date,
                        visual_url=content_obj.file_path
                    )
                    
                    await db.generated_posts.insert_one(generated_post.dict())
                    all_generated_posts.append(generated_post)
                
                # Mark content as processed
                await db.content_uploads.update_one(
                    {"id": content_obj.id},
                    {"$set": {"status": "processed"}}
                )
        
        # Generate automatic content if not enough user content
        required_posts_per_week = {
            "daily": 7,
            "3x_week": 3,
            "weekly": 1,
            "bi_weekly": 2
        }
        
        required = required_posts_per_week.get(business_prof.posting_frequency, 3)
        platforms_count = len(business_prof.preferred_platforms)
        total_required = required * platforms_count
        
        if len(all_generated_posts) < total_required:
            auto_posts_data = await generate_automatic_content(business_prof, notes_list)
            
            for post_data in auto_posts_data[:total_required - len(all_generated_posts)]:
                scheduled_date = datetime.utcnow() + timedelta(days=len(all_generated_posts) + 1)
                
                generated_post = GeneratedPost(
                    business_id=business_id,
                    platform=post_data["platform"],
                    post_text=post_data["post_text"],
                    hashtags=post_data["hashtags"],
                    scheduled_date=scheduled_date,
                    auto_generated=True
                )
                
                await db.generated_posts.insert_one(generated_post.dict())
                all_generated_posts.append(generated_post)
        
        return {
            "message": "Posts generated successfully",
            "total_posts": len(all_generated_posts),
            "user_content_posts": len([p for p in all_generated_posts if not p.auto_generated]),
            "auto_generated_posts": len([p for p in all_generated_posts if p.auto_generated])
        }
        
    except Exception as e:
        logging.error(f"Error generating posts: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating posts: {str(e)}")

@api_router.get("/generated-posts/{business_id}", response_model=List[GeneratedPost])
async def get_generated_posts(business_id: str, status: Optional[str] = None):
    """Get all generated posts for a business"""
    query = {"business_id": business_id}
    if status:
        query["status"] = status
    
    posts = await db.generated_posts.find(query).sort("scheduled_date", 1).to_list(1000)
    return [GeneratedPost(**post) for post in posts]

@api_router.put("/post/{post_id}/schedule")
async def update_post_schedule(post_id: str, schedule_update: PostScheduleUpdate):
    """Update post scheduling"""
    result = await db.generated_posts.update_one(
        {"id": post_id},
        {"$set": {
            "scheduled_date": schedule_update.scheduled_date,
            "scheduled_time": schedule_update.scheduled_time
        }}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Schedule updated successfully"}

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

@api_router.put("/post/{post_id}/validate-and-schedule")
async def validate_and_schedule_post(post_id: str):
    """Validate and schedule post for automatic publication"""
    result = await db.generated_posts.update_one(
        {"id": post_id},
        {"$set": {"status": "scheduled"}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # TODO: Here we would integrate with social media APIs to actually schedule the post
    # For now, we just mark it as scheduled
    
    return {"message": "Post validated and scheduled for publication"}

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