from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form, Depends, BackgroundTasks, status
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import base64
import json
from emergentintegrations.llm.chat import LlmChat, UserMessage, FileContentWithMimeType, ImageContent
import asyncio

# Import authentication and admin modules
from auth import (
    User, UserCreate, UserLogin, UserResponse, Token, PasswordReset, PasswordResetConfirm,
    create_user, authenticate_user, create_access_token, create_refresh_token, create_reset_token,
    get_current_user, get_current_active_user, get_admin_user, check_subscription_status,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from admin import admin_router, init_admin_data
from payments import payment_router
from social_media import social_router

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
app = FastAPI(title="PostCraft API", version="1.0.0")

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Pydantic Models (Business models remain the same but now linked to users)
class BusinessProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # NEW: Link to user
    business_name: str
    business_type: str
    target_audience: str
    brand_tone: str  # professional, casual, friendly, etc.
    posting_frequency: str  # daily, 3x/week, weekly
    preferred_platforms: List[str]  # facebook, instagram, linkedin
    budget_range: str
    logo_url: Optional[str] = None
    email: Optional[str] = None
    hashtags_primary: List[str] = []  # NEW: Always included
    hashtags_secondary: List[str] = []  # NEW: Context-dependent
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    first_generation_date: Optional[datetime] = None

class BusinessProfileCreate(BaseModel):
    business_name: str
    business_type: str
    target_audience: str
    brand_tone: str
    posting_frequency: str
    preferred_platforms: List[str]
    budget_range: str
    email: Optional[str] = None
    hashtags_primary: List[str] = []
    hashtags_secondary: List[str] = []

class BusinessProfileUpdate(BaseModel):
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    target_audience: Optional[str] = None
    brand_tone: Optional[str] = None
    posting_frequency: Optional[str] = None
    preferred_platforms: Optional[List[str]] = None
    budget_range: Optional[str] = None
    email: Optional[str] = None
    hashtags_primary: Optional[List[str]] = None
    hashtags_secondary: Optional[List[str]] = None

class ContentUpload(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # NEW: Link to user
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
    user_id: str  # NEW: Link to user
    business_id: str
    title: str
    content: str
    priority: str = "normal"  # high, normal, low
    active_until: Optional[datetime] = None  # For time-sensitive notes
    created_at: datetime = Field(default_factory=datetime.utcnow)

class GeneratedPost(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # NEW: Link to user
    business_id: str
    content_id: Optional[str] = None  # Can be None for auto-generated content
    platform: str  # facebook, instagram, linkedin
    post_text: str
    hashtags: List[str]
    scheduled_date: datetime
    scheduled_time: str = "09:00"
    status: str = "pending"  # pending, approved, rejected, posted, scheduled
    auto_generated: bool = False
    visual_url: Optional[str] = None
    generation_batch: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PostScheduleUpdate(BaseModel):
    scheduled_date: datetime
    scheduled_time: str

class SocialMediaConnection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    business_id: str
    platform: str  # facebook, instagram, linkedin
    access_token: str
    refresh_token: Optional[str] = None
    page_id: Optional[str] = None  # For Facebook pages
    page_name: Optional[str] = None
    instagram_user_id: Optional[str] = None  # For Instagram
    platform_user_id: Optional[str] = None  # Platform-specific user ID
    platform_username: Optional[str] = None  # Platform username
    expires_at: Optional[datetime] = None
    active: bool = True
    connected_at: datetime = Field(default_factory=datetime.utcnow)
    disconnected_at: Optional[datetime] = None

class ScheduledTask(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    business_id: str
    task_type: str  # 'generate_posts', 'content_reminder', 'post_ready_notification'
    scheduled_date: datetime
    frequency: str  # 'weekly', 'monthly', 'daily'
    next_run: datetime
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Helper function to get recent posts history for anti-repetition
async def get_recent_posts_history(business_id: str, months_back: int = 12) -> str:
    """Get recent posts to avoid repetition"""
    try:
        # Calculate date 12 months ago
        cutoff_date = datetime.utcnow() - timedelta(days=months_back * 30)
        
        # Get recent posts
        recent_posts = await db.generated_posts.find({
            "business_id": business_id,
            "created_at": {"$gte": cutoff_date},
            "status": {"$in": ["approved", "scheduled", "posted"]}
        }).sort("created_at", -1).to_list(200)  # Last 200 posts max
        
        if not recent_posts:
            return "Aucun historique de posts précédents."
        
        # Format history for AI context
        history_text = "POSTS DÉJÀ PUBLIÉS (à ne pas répéter):\n"
        for post in recent_posts[:50]:  # Limit to 50 most recent
            post_obj = GeneratedPost(**post)
            # Extract key themes and angles
            text_preview = post_obj.post_text[:100].replace('\n', ' ')
            history_text += f"- {post_obj.platform}: \"{text_preview}...\"\n"
        
        return history_text
        
    except Exception as e:
        logging.error(f"Error getting posts history: {e}")
        return "Historique indisponible."

# Helper function to combine hashtags (primary + secondary)
def combine_hashtags(primary_hashtags: List[str], secondary_hashtags: List[str], generated_hashtags: List[str], max_hashtags: int = 10) -> List[str]:
    """Combine and prioritize hashtags"""
    # Start with primary hashtags (always included)
    combined = list(primary_hashtags)
    
    # Add generated hashtags
    for hashtag in generated_hashtags:
        if hashtag not in combined and len(combined) < max_hashtags:
            combined.append(hashtag)
    
    # Fill remaining slots with secondary hashtags
    for hashtag in secondary_hashtags:
        if hashtag not in combined and len(combined) < max_hashtags:
            combined.append(hashtag)
    
    return combined[:max_hashtags]

# Helper function to analyze content with OpenAI (updated with hashtags)
async def analyze_content_with_ai(content_path: str, description: str, business_profile: BusinessProfile, notes: List[ContentNote] = []):
    try:
        # Convert image to base64 for OpenAI
        with open(content_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Prepare notes context
        notes_context = ""
        if notes:
            notes_context = "\n\nInformations importantes à intégrer naturellement:\n"
            for note in notes:
                notes_context += f"- {note.title}: {note.content}\n"
        
        # Get recent posts history to avoid repetition
        posts_history = await get_recent_posts_history(business_profile.id)
        
        # Prepare hashtags context
        hashtags_context = ""
        if business_profile.hashtags_primary:
            hashtags_context += f"\nHashtags PRIORITAIRES (toujours inclure): {', '.join(business_profile.hashtags_primary)}"
        if business_profile.hashtags_secondary:
            hashtags_context += f"\nHashtags SECONDAIRES (selon contexte): {', '.join(business_profile.hashtags_secondary)}"
        
        # Create LLM chat instance with OpenAI
        chat = LlmChat(
            api_key=os.environ['OPENAI_API_KEY'],
            session_id=f"content_analysis_{uuid.uuid4()}",
            system_message=f"""Tu écris comme un vrai humain qui gère les réseaux sociaux d'une entreprise.

PROFIL ENTREPRISE:
- Nom: {business_profile.business_name}
- Secteur: {business_profile.business_type}
- Audience: {business_profile.target_audience}
- Ton: {business_profile.brand_tone}
- Réseaux: {', '.join(business_profile.preferred_platforms)}
{notes_context}
{hashtags_context}

{posts_history}

RÈGLES ABSOLUES pour un style NATUREL:
❌ JAMAIS d'emojis clichés: ✨💫🌟🚀💡🎯🔥💪⚡
❌ JAMAIS "Plongeons dans", "Explorons", "N'hésitez pas à", "Il est crucial"
❌ JAMAIS de structure parfaite intro-développement-conclusion
❌ JAMAIS de listes à puces ou de tirets longs (—)
❌ JAMAIS de transitions fluides artificielles
❌ JAMAIS répéter les mêmes angles/idées que les posts précédents

✅ TOUJOURS écrire comme si c'était TOI qui gérais ces réseaux sociaux
✅ Langage spontané, familier mais pro selon le ton
✅ Phrases courtes et variées
✅ Emojis simples et rares (😊❤️👍)
✅ Imperfections volontaires qui rendent humain
✅ References locales quand possible
✅ Angles NOUVEAUX et FRAIS par rapport à l'historique
✅ Utiliser les hashtags prioritaires quand pertinents"""
        ).with_model("openai", "gpt-4o")

        # Generate posts for each platform
        generated_posts = []
        
        for platform in business_profile.preferred_platforms:
            try:
                # Platform-specific optimizations with natural approach
                platform_specs = {
                    "facebook": {
                        "max_chars": 2000, 
                        "hashtags_max": 5, 
                        "style": "conversationnel et proche, comme si tu parlais à tes voisins"
                    },
                    "instagram": {
                        "max_chars": 2200, 
                        "hashtags_max": 10, 
                        "style": "authentique et visuel, sans en faire trop"
                    },
                    "linkedin": {
                        "max_chars": 3000, 
                        "hashtags_max": 3, 
                        "style": "professionnel mais humain, pas corporate"
                    }
                }
                
                specs = platform_specs.get(platform, {
                    "max_chars": 2000, 
                    "hashtags_max": 5, 
                    "style": "naturel et engageant"
                })
                
                platform_prompt = f"""Regarde cette image et sa description: "{description}"

Écris un post pour {platform} comme si TU gérais vraiment ce compte.

IMPORTANT: Trouve un ANGLE NOUVEAU, différent des posts précédents listés ci-dessus.
Ne répète PAS les mêmes idées, formulations, ou approches.

Style {specs['style']}.
Ton {business_profile.brand_tone}.
Max {specs['max_chars']} caractères.
Suggère max {specs['hashtags_max']} hashtags complémentaires (les hashtags prioritaires seront ajoutés automatiquement).

EXEMPLES de ce qu'on VEUT (naturel):
- "On a testé ça toute la semaine... franchement, on est contents du résultat 😊"
- "Petite question: vous préférez quoi vous, le matin ?"
- "Bon, on avoue, on est un peu fiers de celui-là"
- "Ça faisait longtemps qu'on voulait vous montrer ça"

EXEMPLES de ce qu'on VEUT PAS (IA détectable):
- "Découvrez notre nouvelle création exceptionnelle ✨"
- "Plongeons ensemble dans cette expérience unique 🚀"
- "Il est temps de révolutionner votre quotidien 💡"

Réponds UNIQUEMENT en JSON:
{{
    "post_text": "ton post naturel ici",
    "hashtags": ["hashtag1", "hashtag2"]
}}"""

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
                    
                    # Combine hashtags intelligently
                    final_hashtags = combine_hashtags(
                        business_profile.hashtags_primary,
                        business_profile.hashtags_secondary,
                        post_data.get("hashtags", []),
                        specs['hashtags_max']
                    )
                    
                    generated_posts.append({
                        "platform": platform,
                        "post_text": post_data.get("post_text", ""),
                        "hashtags": final_hashtags
                    })
                except json.JSONDecodeError:
                    # Fallback with natural style
                    logging.warning(f"Failed to parse JSON for {platform}, using fallback")
                    fallback_hashtags = combine_hashtags(
                        business_profile.hashtags_primary,
                        business_profile.hashtags_secondary,
                        ["nouveau"],
                        specs['hashtags_max']
                    )
                    generated_posts.append({
                        "platform": platform,
                        "post_text": f"On voulait vous montrer ça... {description[:100]}",
                        "hashtags": fallback_hashtags
                    })
            except Exception as platform_error:
                logging.error(f"Error generating post for {platform}: {platform_error}")
                # Natural fallback post
                fallback_hashtags = combine_hashtags(
                    business_profile.hashtags_primary,
                    business_profile.hashtags_secondary,
                    ["nouveaute"],
                    5
                )
                generated_posts.append({
                    "platform": platform,
                    "post_text": f"Petite nouveauté chez {business_profile.business_name}... {description[:80]}",
                    "hashtags": fallback_hashtags
                })
        
        return generated_posts
    except Exception as e:
        logging.error(f"Error analyzing content with AI: {e}")
        # Natural fallback posts
        fallback_posts = []
        for platform in business_profile.preferred_platforms:
            fallback_hashtags = combine_hashtags(
                business_profile.hashtags_primary,
                business_profile.hashtags_secondary,
                ["nouveau"],
                5
            )
            fallback_posts.append({
                "platform": platform,
                "post_text": f"Du nouveau chez {business_profile.business_name}... {description[:80]}",
                "hashtags": fallback_hashtags
            })
        return fallback_posts

# Background task to set up automatic scheduling
async def setup_automatic_scheduling(business_id: str):
    """Set up automatic scheduling for a business"""
    try:
        business_profile = await db.business_profiles.find_one({"id": business_id})
        if not business_profile:
            return
        
        business_prof = BusinessProfile(**business_profile)
        
        # Calculate next generation date based on frequency
        now = datetime.utcnow()
        
        # Set first generation date if not set
        if not business_prof.first_generation_date:
            await db.business_profiles.update_one(
                {"id": business_id},
                {"$set": {"first_generation_date": now}}
            )
        
        frequency_map = {
            "daily": 7,        # Generate weekly for daily posts
            "3x_week": 7,      # Generate weekly for 3x/week posts  
            "weekly": 30,      # Generate monthly for weekly posts
            "bi_weekly": 30    # Generate monthly for bi-weekly posts
        }
        
        days_to_add = frequency_map.get(business_prof.posting_frequency, 7)
        next_generation = now + timedelta(days=days_to_add)
        reminder_date = next_generation - timedelta(days=3)
        
        # Create scheduled tasks
        generation_task = {
            "id": str(uuid.uuid4()),
            "business_id": business_id,
            "task_type": "generate_posts",
            "scheduled_date": next_generation,
            "frequency": "weekly" if business_prof.posting_frequency in ["daily", "3x_week"] else "monthly",
            "next_run": next_generation,
            "active": True,
            "created_at": datetime.utcnow()
        }
        
        reminder_task = {
            "id": str(uuid.uuid4()),
            "business_id": business_id,
            "task_type": "content_reminder", 
            "scheduled_date": reminder_date,
            "frequency": "weekly" if business_prof.posting_frequency in ["daily", "3x_week"] else "monthly",
            "next_run": reminder_date,
            "active": True,
            "created_at": datetime.utcnow()
        }
        
        # Check if tasks already exist
        existing_gen = await db.scheduled_tasks.find_one({
            "business_id": business_id,
            "task_type": "generate_posts",
            "active": True
        })
        
        existing_reminder = await db.scheduled_tasks.find_one({
            "business_id": business_id,
            "task_type": "content_reminder",
            "active": True
        })
        
        if not existing_gen:
            await db.scheduled_tasks.insert_one(generation_task)
        
        if not existing_reminder:
            await db.scheduled_tasks.insert_one(reminder_task)
        
        logging.info(f"Automatic scheduling set up for {business_prof.business_name}")
        
    except Exception as e:
        logging.error(f"Error setting up automatic scheduling: {e}")

# Authentication Routes
@api_router.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        user = await create_user(user_data)
        return UserResponse(**user.dict())
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création du compte"
        )

@api_router.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Login user"""
    user = await authenticate_user(user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return UserResponse(**current_user.dict())

@api_router.get("/auth/subscription-status")
async def get_subscription_status(current_user: User = Depends(get_current_active_user)):
    """Get current user's subscription status"""
    return check_subscription_status(current_user)

@api_router.post("/auth/logout")
async def logout():
    """Logout user (client-side token removal)"""
    return {"message": "Déconnexion réussie"}

# Business Profile Routes (now protected)
@api_router.post("/business-profile", response_model=BusinessProfile)
async def create_business_profile(
    profile_data: BusinessProfileCreate, 
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new business profile"""
    # Check if user already has a business profile
    existing_profile = await db.business_profiles.find_one({"user_id": current_user.id})
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous avez déjà un profil d'entreprise"
        )
    
    profile = BusinessProfile(user_id=current_user.id, **profile_data.dict())
    await db.business_profiles.insert_one(profile.dict())
    
    # Link business profile to user
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"business_profile_id": profile.id}}
    )
    
    # Set up automatic scheduling in background
    background_tasks.add_task(setup_automatic_scheduling, profile.id)
    
    return profile

@api_router.get("/business-profile", response_model=BusinessProfile)
async def get_user_business_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user's business profile"""
    profile = await db.business_profiles.find_one({"user_id": current_user.id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profil d'entreprise non trouvé")
    return BusinessProfile(**profile)

@api_router.put("/business-profile", response_model=BusinessProfile)
async def update_business_profile(
    update_data: BusinessProfileUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update business profile"""
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.utcnow()
    
    result = await db.business_profiles.update_one(
        {"user_id": current_user.id}, 
        {"$set": update_dict}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Profil d'entreprise non trouvé")
    
    profile = await db.business_profiles.find_one({"user_id": current_user.id})
    return BusinessProfile(**profile)

# Content Routes (now protected and user-scoped)
@api_router.post("/upload-content-batch")
async def upload_content_batch(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """Upload multiple content files at once"""
    try:
        # Get user's business profile
        business_profile = await db.business_profiles.find_one({"user_id": current_user.id})
        if not business_profile:
            raise HTTPException(status_code=404, detail="Profil d'entreprise non trouvé")
        
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
                user_id=current_user.id,
                business_id=business_profile['id'],
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

@api_router.post("/content/{content_id}/describe")
async def describe_content(
    content_id: str,
    description: str = Form(...),
    current_user: User = Depends(get_current_active_user)
):
    """Add description to uploaded content and generate social media posts"""
    try:
        # Get the content upload
        content_upload = await db.content_uploads.find_one({
            "id": content_id,
            "user_id": current_user.id
        })
        
        if not content_upload:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Get business profile
        business_profile = await db.business_profiles.find_one({
            "id": content_upload["business_id"],
            "user_id": current_user.id
        })
        
        if not business_profile:
            raise HTTPException(status_code=404, detail="Business profile not found")
        
        business_prof = BusinessProfile(**business_profile)
        
        # Get active notes for context
        notes = await db.content_notes.find({
            "business_id": business_prof.id,
            "user_id": current_user.id
        }).to_list(50)
        
        notes_list = [ContentNote(**note) for note in notes]
        
        # Generate AI posts
        generated_posts = await analyze_content_with_ai(
            content_upload["file_path"], 
            description, 
            business_prof, 
            notes_list
        )
        
        # Save generated posts to database
        saved_posts = []
        batch_id = str(uuid.uuid4())
        
        for post_data in generated_posts:
            # Calculate scheduling date (next 7 days distributed)
            days_ahead = len(saved_posts) % 7 + 1
            scheduled_date = datetime.utcnow() + timedelta(days=days_ahead)
            
            generated_post = GeneratedPost(
                user_id=current_user.id,
                business_id=business_prof.id,
                content_id=content_id,
                platform=post_data["platform"],
                post_text=post_data["post_text"],
                hashtags=post_data["hashtags"],
                scheduled_date=scheduled_date,
                status="pending",
                auto_generated=False,
                visual_url=f"/uploads/{content_upload['file_path'].split('/')[-1]}",
                generation_batch=batch_id
            )
            
            await db.generated_posts.insert_one(generated_post.dict())
            saved_posts.append(generated_post)
        
        # Update content status
        await db.content_uploads.update_one(
            {"id": content_id},
            {"$set": {
                "description": description,
                "status": "ready"
            }}
        )
        
        return {
            "message": "Content described and posts generated successfully",
            "generated_posts": len(saved_posts),
            "batch_id": batch_id,
            "posts": [{"platform": p.platform, "id": p.id} for p in saved_posts]
        }
        
    except Exception as e:
        logging.error(f"Error describing content: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing content: {str(e)}")

@api_router.get("/posts")
async def get_user_posts(
    current_user: User = Depends(get_current_active_user),
    status: Optional[str] = None,
    limit: int = 50
):
    """Get user's generated posts"""
    try:
        # Get user's business profile
        business_profile = await db.business_profiles.find_one({"user_id": current_user.id})
        if not business_profile:
            raise HTTPException(status_code=404, detail="Business profile not found")
        
        # Build query
        query = {
            "user_id": current_user.id,
            "business_id": business_profile["id"]
        }
        
        if status:
            query["status"] = status
        
        # Get posts
        posts = await db.generated_posts.find(query).sort("created_at", -1).limit(limit).to_list(limit)
        
        return {
            "posts": posts,
            "total": len(posts)
        }
        
    except Exception as e:
        logging.error(f"Error getting posts: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving posts: {str(e)}")

@api_router.put("/posts/{post_id}/approve")
async def approve_post(
    post_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Approve a generated post"""
    result = await db.generated_posts.update_one(
        {
            "id": post_id,
            "user_id": current_user.id
        },
        {"$set": {"status": "approved"}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return {"message": "Post approved successfully"}

@api_router.put("/posts/{post_id}/schedule")
async def update_post_schedule(
    post_id: str,
    schedule_data: PostScheduleUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update post schedule"""
    result = await db.generated_posts.update_one(
        {
            "id": post_id,
            "user_id": current_user.id
        },
        {"$set": {
            "scheduled_date": schedule_data.scheduled_date,
            "scheduled_time": schedule_data.scheduled_time
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return {"message": "Post schedule updated successfully"}

@api_router.post("/posts/{post_id}/publish")
async def publish_post_now(
    post_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Publish a post immediately to connected social media accounts"""
    try:
        # Get the post
        post = await db.generated_posts.find_one({
            "id": post_id,
            "user_id": current_user.id
        })
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        post_obj = GeneratedPost(**post)
        
        # Get social media connections for this business
        connections = await db.social_media_connections.find({
            "user_id": current_user.id,
            "business_id": post_obj.business_id,
            "platform": post_obj.platform,
            "active": True
        }).to_list(10)
        
        if not connections:
            raise HTTPException(
                status_code=404, 
                detail=f"No active {post_obj.platform} connections found"
            )
        
        results = []
        
        # Import social media clients
        from social_media import FacebookAPIClient, InstagramAPIClient
        
        for connection in connections:
            try:
                if post_obj.platform == "facebook":
                    fb_client = FacebookAPIClient(connection["access_token"])
                    result = await fb_client.post_to_page(
                        connection["page_id"],
                        connection["access_token"],
                        f"{post_obj.post_text}\n\n{' '.join(['#' + tag for tag in post_obj.hashtags])}",
                        post_obj.visual_url
                    )
                    
                    results.append({
                        "platform": "facebook",
                        "page_name": connection.get("page_name", ""),
                        "post_id": result["id"],
                        "success": True
                    })
                
                elif post_obj.platform == "instagram":
                    if not post_obj.visual_url:
                        raise HTTPException(
                            status_code=400, 
                            detail="Instagram posts require an image"
                        )
                    
                    ig_client = InstagramAPIClient(connection["access_token"])
                    result = await ig_client.post_to_instagram(
                        connection["instagram_user_id"],
                        f"http://localhost:8001{post_obj.visual_url}",  # Full URL for Instagram
                        f"{post_obj.post_text}\n\n{' '.join(['#' + tag for tag in post_obj.hashtags])}"
                    )
                    
                    results.append({
                        "platform": "instagram",
                        "username": connection.get("platform_username", ""),
                        "media_id": result["media_id"],
                        "success": True
                    })
                
            except Exception as conn_error:
                logging.error(f"Error posting to {connection.get('page_name', connection.get('platform_username', 'unknown'))}: {conn_error}")
                results.append({
                    "platform": post_obj.platform,
                    "account": connection.get("page_name", connection.get("platform_username", "unknown")),
                    "success": False,
                    "error": str(conn_error)
                })
        
        # Update post status
        if any(r["success"] for r in results):
            await db.generated_posts.update_one(
                {"id": post_id},
                {"$set": {"status": "posted", "published_at": datetime.utcnow()}}
            )
            status_message = "posted"
        else:
            status_message = "failed"
        
        return {
            "message": f"Post {status_message}",
            "results": results,
            "successful_posts": sum(1 for r in results if r["success"]),
            "total_attempts": len(results)
        }
        
    except Exception as e:
        logging.error(f"Error publishing post: {e}")
        raise HTTPException(status_code=500, detail=f"Error publishing post: {str(e)}")

@api_router.post("/notes")
async def create_content_note(
    note_data: ContentNote,
    current_user: User = Depends(get_current_active_user)
):
    """Create a content note"""
    # Get user's business profile
    business_profile = await db.business_profiles.find_one({"user_id": current_user.id})
    if not business_profile:
        raise HTTPException(status_code=404, detail="Business profile not found")
    
    note = ContentNote(
        user_id=current_user.id,
        business_id=business_profile["id"],
        **{k: v for k, v in note_data.dict().items() if k not in ["id", "user_id", "business_id"]}
    )
    
    await db.content_notes.insert_one(note.dict())
    return note

@api_router.get("/notes")
async def get_content_notes(
    current_user: User = Depends(get_current_active_user)
):
    """Get user's content notes"""
    # Get user's business profile
    business_profile = await db.business_profiles.find_one({"user_id": current_user.id})
    if not business_profile:
        raise HTTPException(status_code=404, detail="Business profile not found")
    
    notes = await db.content_notes.find({
        "user_id": current_user.id,
        "business_id": business_profile["id"]
    }).sort("created_at", -1).to_list(100)
    
    return {"notes": notes}

# Include routers in the main app
app.include_router(api_router)
app.include_router(admin_router, prefix="/api")  # Admin routes
app.include_router(payment_router, prefix="/api")  # Payment routes
app.include_router(social_router, prefix="/api")  # Social media routes

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

# Initialize admin data on startup
@app.on_event("startup")
async def startup_event():
    """Initialize data on startup"""
    await init_admin_data()
    logging.info("PostCraft API started successfully")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()