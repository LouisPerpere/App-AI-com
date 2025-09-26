import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
import os
from pathlib import Path
from server import (
    BusinessProfile, ContentUpload, GeneratedPost, ContentNote,
    analyze_content_with_ai
)
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json
import uuid
import base64
import requests

# Import analytics engine
from analytics import analytics_engine, PerformanceInsights, prompt_optimizer

# Load environment variables
from dotenv import load_dotenv
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Email configuration
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USER = os.environ.get('EMAIL_USER', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
EMAIL_FROM = os.environ.get('EMAIL_FROM', 'noreply@socialgenie.com')

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Website analysis auto-refresh functionality
async def monthly_rotation_check():
    """Check if it's time for monthly rotation and perform it"""
    try:
        now = datetime.utcnow()
        
        # Check if it's the 1st of the month at 1 AM (or later in the same hour)
        if now.day == 1 and now.hour == 1:
            logger.info("🔄 Monthly rotation time detected! Performing monthly updates...")
            
            # Update website analyses that need monthly refresh  
            await check_and_update_website_analyses()
            
            # Trigger monthly rotation for all active users
            await trigger_monthly_rotation_for_users()
            
            logger.info("✅ Monthly rotation completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Error during monthly rotation: {e}")

async def trigger_monthly_rotation_for_users():
    """Trigger monthly rotation logic for all users (update month organization)"""
    try:
        logger.info("🔄 Triggering monthly rotation for all users...")
        
        # Get all unique user IDs from various collections
        users_collection = db.users
        all_users = await users_collection.find({}, {"user_id": 1}).to_list(length=None)
        
        logger.info(f"📊 Found {len(all_users)} users for monthly rotation")
        
        for user in all_users:
            user_id = user.get("user_id")
            if user_id:
                await update_user_monthly_organization(user_id)
        
        logger.info("✅ Monthly rotation completed for all users")
        
    except Exception as e:
        logger.error(f"❌ Error in monthly rotation for users: {e}")

async def update_user_monthly_organization(user_id: str):
    """Update monthly organization for a specific user"""
    try:
        logger.info(f"🔄 Updating monthly organization for user {user_id}")
        
        current_date = datetime.utcnow()
        current_month = current_date.month
        current_year = current_date.year
        
        # Update media attribution - move unattributed media to previous month
        previous_month = current_month - 1 if current_month > 1 else 12
        previous_year = current_year if current_month > 1 else current_year - 1
        
        # French month mapping for attribution
        french_months = {
            1: "janvier", 2: "février", 3: "mars", 4: "avril", 5: "mai", 6: "juin",
            7: "juillet", 8: "août", 9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"
        }
        
        previous_month_name = f"{french_months[previous_month]}_{previous_year}"
        
        # Update media that doesn't have attribution to previous month
        media_update_result = await db.media.update_many(
            {
                "owner_id": user_id,
                "attributed_month": {"$exists": False},
                "created_at": {"$lt": current_date.replace(day=1)}  # Created before this month
            },
            {
                "$set": {"attributed_month": previous_month_name}
            }
        )
        
        # Update notes monthly organization
        notes_update_result = await db.content_notes.update_many(
            {
                "owner_id": user_id,
                "note_month": {"$exists": False},
                "created_at": {"$lt": current_date.replace(day=1)}
            },
            {
                "$set": {
                    "note_month": previous_month,
                    "note_year": previous_year
                }
            }
        )
        
        logger.info(f"✅ Updated {media_update_result.modified_count} media items and {notes_update_result.modified_count} notes for user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error updating monthly organization for user {user_id}: {e}")

async def check_and_update_website_analyses():
    """Check for website analyses that need monthly refresh and update them"""
    try:
        logger.info("🔍 Checking for website analyses that need monthly updates...")
        
        # Get all analyses that are due for refresh
        now = datetime.utcnow()
        analyses_collection = db.website_analyses
        
        # Find analyses where next_analysis_due is in the past
        due_analyses = await analyses_collection.find({
            "next_analysis_due": {"$lt": now}
        }).to_list(length=100)
        
        logger.info(f"📊 Found {len(due_analyses)} website analyses due for refresh")
        
        for analysis in due_analyses:
            try:
                user_id = analysis.get("user_id")
                website_url = analysis.get("website_url")
                
                if not user_id or not website_url:
                    continue
                
                logger.info(f"🔄 Auto-refreshing analysis for user {user_id}, website {website_url}")
                
                # Import and call the website analysis function
                from website_analyzer_gpt5 import analyze_multiple_pages, discover_website_pages, analyze_with_gpt4o
                
                # Discover and analyze pages
                important_pages = discover_website_pages(website_url, max_pages=5)
                content_data = await analyze_multiple_pages(important_pages, website_url)
                
                if "error" not in content_data:
                    # Analyze with GPT
                    analysis_result = await analyze_with_gpt4o(content_data, website_url)
                    
                    # Update the analysis in database
                    updated_analysis = {
                        "analysis_summary": analysis_result.get("analysis_summary", ""),
                        "key_topics": analysis_result.get("key_topics", []),
                        "brand_tone": analysis_result.get("brand_tone", "professional"),
                        "target_audience": analysis_result.get("target_audience", ""),
                        "main_services": analysis_result.get("main_services", []),
                        "content_suggestions": analysis_result.get("content_suggestions", []),
                        "pages_analyzed": content_data.get("pages_analyzed", []),
                        "pages_count": len(important_pages),
                        "last_analyzed": now,
                        "next_analysis_due": now + timedelta(days=30)
                    }
                    
                    await analyses_collection.update_one(
                        {"_id": analysis["_id"]},
                        {"$set": updated_analysis}
                    )
                    
                    logger.info(f"✅ Auto-refresh completed for {website_url}")
                    
            except Exception as e:
                logger.error(f"❌ Error auto-refreshing analysis for {analysis.get('website_url', 'unknown')}: {e}")
                
    except Exception as e:
        logger.error(f"❌ Error in check_and_update_website_analyses: {e}")

# Periodic notes cleanup functionality (Phase 3)
def cleanup_expired_periodic_notes():
    """Clean up expired periodic notes on the 5th of each month"""
    try:
        logger.info("🗑️ Starting periodic notes cleanup...")
        
        # Import database manager
        from database import get_database, DatabaseManager
        
        # Get database instance
        dbm = get_database()
        
        # Perform cleanup
        result = dbm.cleanup_expired_periodic_notes()
        
        if result.get("success", False):
            deleted_count = result.get("deleted_count", 0)
            target_month_name = result.get("target_month_name", "Unknown")
            target_year = result.get("target_year", "Unknown")
            
            if deleted_count > 0:
                logger.info(f"🗑️ Periodic notes cleanup successful: {deleted_count} notes from {target_month_name} {target_year} deleted")
                
                # Log details of deleted notes
                deleted_notes = result.get("deleted_notes", [])
                for note in deleted_notes:
                    logger.info(f"   ✅ Deleted note: '{note.get('title', 'Sans titre')}' (ID: {note.get('note_id')})")
            else:
                reason = result.get("reason", "No notes to delete")
                logger.info(f"🗑️ Periodic notes cleanup: {reason}")
        else:
            error = result.get("error", "Unknown error")
            logger.error(f"❌ Periodic notes cleanup failed: {error}")
            
        return result
        
    except Exception as e:
        logger.error(f"❌ Error in cleanup_expired_periodic_notes: {e}")
        return {"deleted_count": 0, "error": str(e), "success": False}

class ScheduledTask(BaseModel):
    id: str
    business_id: str
    task_type: str  # 'generate_posts', 'content_reminder', 'post_ready_notification'
    scheduled_date: datetime
    frequency: str  # 'weekly', 'monthly', 'daily'
    next_run: datetime
    active: bool = True
    created_at: datetime

class EmailService:
    """Service for sending emails"""
    
    @staticmethod
    async def send_email(to_email: str, subject: str, html_content: str):
        """Send HTML email"""
        try:
            if not EMAIL_USER or not EMAIL_PASSWORD:
                logger.warning("Email credentials not configured")
                return False
                
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = EMAIL_FROM
            msg['To'] = to_email
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    @staticmethod
    async def send_posts_ready_notification(business_profile: BusinessProfile, post_count: int):
        """Notify user that posts are ready for validation"""
        subject = f"🎉 {post_count} nouveaux posts prêts à valider - {business_profile.business_name}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; color: white;">
                <h1>✨ SocialGénie</h1>
                <h2>Vos posts sont prêts !</h2>
            </div>
            
            <div style="padding: 30px; background: #f9fafb;">
                <p>Bonjour,</p>
                
                <p>Excellente nouvelle ! <strong>{post_count} nouveaux posts</strong> ont été générés pour <strong>{business_profile.business_name}</strong> et sont maintenant prêts à être validés.</p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea;">
                    <h3>📊 Récapitulatif :</h3>
                    <ul>
                        <li><strong>Entreprise :</strong> {business_profile.business_name}</li>
                        <li><strong>Posts générés :</strong> {post_count}</li>
                        <li><strong>Plateformes :</strong> {', '.join(business_profile.preferred_platforms)}</li>
                        <li><strong>Fréquence :</strong> {business_profile.posting_frequency}</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://social-ai-planner-2.preview.emergentagent.com" 
                       style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                              color: white; padding: 15px 30px; text-decoration: none; 
                              border-radius: 8px; font-weight: bold; display: inline-block;">
                        🚀 Valider mes posts
                    </a>
                </div>
                
                <p style="color: #6b7280; font-size: 14px;">
                    💡 <strong>Astuce :</strong> Plus vous validez rapidement vos posts, plus votre audience reste engagée !
                </p>
            </div>
            
            <div style="background: #374151; color: white; padding: 20px; text-align: center; font-size: 12px;">
                <p>SocialGénie - Automatisez votre présence sur les réseaux sociaux</p>
                <p>Cet email a été envoyé automatiquement. Ne pas répondre.</p>
            </div>
        </body>
        </html>
        """
        
        # For demo purposes, we'll use a placeholder email
        demo_email = "user@example.com"  # In production, get from business profile
        return await EmailService.send_email(demo_email, subject, html_content)
    
    @staticmethod
    async def send_content_reminder(business_profile: BusinessProfile, days_until_generation: int):
        """Send reminder to upload content"""
        subject = f"📸 Uploadez du contenu pour {business_profile.business_name} - Génération dans {days_until_generation} jours"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); padding: 30px; text-align: center; color: white;">
                <h1>⏰ SocialGénie</h1>
                <h2>Rappel upload contenu</h2>
            </div>
            
            <div style="padding: 30px; background: #f9fafb;">
                <p>Bonjour,</p>
                
                <p>La prochaine génération de posts pour <strong>{business_profile.business_name}</strong> aura lieu dans <strong>{days_until_generation} jour{'s' if days_until_generation > 1 else ''}</strong>.</p>
                
                <div style="background: #fef3c7; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #f59e0b;">
                    <h3>📋 Action requise :</h3>
                    <p>Pour des posts personnalisés et engageants, pensez à uploader :</p>
                    <ul>
                        <li>📷 Photos de vos produits/services</li>
                        <li>🎥 Vidéos de votre activité</li>
                        <li>📝 Descriptions détaillées</li>
                        <li>📌 Notes importantes (promotions, fermetures, etc.)</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://social-ai-planner-2.preview.emergentagent.com" 
                       style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); 
                              color: white; padding: 15px 30px; text-decoration: none; 
                              border-radius: 8px; font-weight: bold; display: inline-block;">
                        📤 Uploader du contenu
                    </a>
                </div>
                
                <div style="background: white; padding: 15px; border-radius: 8px; font-size: 14px;">
                    <p><strong>💡 Astuce :</strong></p>
                    <p>Si vous n'uploadez pas de contenu, SocialGénie générera automatiquement des posts informatifs, des citations inspirantes et du contenu éducatif en rapport avec votre secteur d'activité.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        demo_email = "user@example.com"
        return await EmailService.send_email(demo_email, subject, html_content)

class AutoContentGenerator:
    """Advanced automatic content generation"""
    
    @staticmethod
    async def generate_visual_content(business_profile: BusinessProfile, content_type: str = "inspirational"):
        """Generate visual content using AI"""
        try:
            chat = LlmChat(
                api_key=os.environ['OPENAI_API_KEY'],
                session_id=f"visual_gen_{uuid.uuid4()}",
                system_message=f"""Tu es un expert en création de visuels pour réseaux sociaux.
                
                Profil entreprise: {business_profile.business_name} - {business_profile.business_type}
                Audience: {business_profile.target_audience}
                Ton: {business_profile.brand_tone}
                
                Génère des concepts visuels simples et élégants qui ne paraissent pas créés par IA."""
            ).with_model("openai", "gpt-4o")
            
            prompt = f"""
            Crée un concept visuel {content_type} pour {business_profile.business_type}.
            
            Réponds uniquement en JSON:
            {{
                "visual_description": "description détaillée du visuel",
                "colors": ["couleur1", "couleur2", "couleur3"],
                "text_overlay": "texte à superposer sur l'image",
                "style": "style visuel (minimal, moderne, vintage, etc.)"
            }}
            """
            
            response = await chat.send_message(UserMessage(text=prompt))
            
            try:
                response_clean = response.strip()
                if response_clean.startswith('```json'):
                    response_clean = response_clean[7:-3].strip()
                elif response_clean.startswith('```'):
                    response_clean = response_clean[3:-3].strip()
                
                visual_data = json.loads(response_clean)
                return visual_data
            except:
                return {
                    "visual_description": "Image simple avec couleurs douces",
                    "colors": ["#f3f4f6", "#6b7280", "#374151"],
                    "text_overlay": "Contenu inspirant",
                    "style": "minimal"
                }
                
        except Exception as e:
            logger.error(f"Error generating visual content: {e}")
            return None
    
    @staticmethod  
    async def generate_sector_specific_content(business_profile: BusinessProfile):
        """Generate sector-specific content (tips, quotes, facts)"""
        try:
            chat = LlmChat(
                api_key=os.environ['OPENAI_API_KEY'],
                session_id=f"sector_content_{uuid.uuid4()}",
                system_message=f"""Tu écris pour les réseaux sociaux comme quelqu'un qui bosse vraiment dans le {business_profile.business_type}.

PAS d'expert marketing, PAS de consultant. Juste quelqu'un de normal qui partage son expérience.

⚠️ FILTRAGE DE CONTENU OBLIGATOIRE - REFUS ABSOLU:
❌ JAMAIS de contenu injurieux, offensant, discriminatoire
❌ JAMAIS de références sexuelles, pornographiques ou suggestives
❌ JAMAIS de contenu violent, haineux ou agressif
❌ JAMAIS de références aux drogues, alcool excessif, substances illégales
❌ JAMAIS de contenu lié aux armes, violence, criminalité
❌ JAMAIS de propos politiques extrêmes ou controversés
❌ JAMAIS de contenu pouvant nuire à des mineurs
❌ JAMAIS de fake news, désinformation ou théories complotistes
❌ JAMAIS de promotion d'activités illégales ou dangereuses

✅ OBJECTIF: Contenu professionnel, bienveillant et constructif uniquement

STYLE NATUREL OBLIGATOIRE:
❌ JAMAIS: "Découvrez", "Explorons", "Il est crucial", "N'hésitez pas", "Plongeons"
❌ JAMAIS: ✨🚀💡🎯💫🌟🔥💪⚡ (emojis marketing)
❌ JAMAIS: Listes parfaites ou transitions fluides artificielles
❌ JAMAIS: Langage corporate ou trop léché

✅ TOUJOURS: Parler normalement, comme à un pote
✅ Partager de vraies expériences, pas des théories
✅ Être utile sans prétention
✅ Garder des imperfections humaines
✅ Contenu respectueux et professionnel

EXEMPLES BONS:
- "Truc qu'on fait ici depuis toujours..."
- "Ça nous est arrivé la semaine dernière"
- "Vous voyez ce que je veux dire ?"
- "On a appris ça à nos dépens"

EXEMPLES MAUVAIS:
- "Découvrez ces stratégies révolutionnaires ✨"
- "Explorons ensemble les secrets de..."
- "Il est crucial d'optimiser votre approche 🚀\""""
            ).with_model("openai", "gpt-4o")
            
            content_types = [
                "astuce_vraiment_utile",
                "anecdote_du_metier", 
                "erreur_commune_eviter",
                "observation_terrain",
                "conseil_experience"
            ]
            
            generated_content = []
            
            for content_type in content_types:
                prompt = f"""Écris un {content_type} pour {business_profile.business_type}.

Tu parles comme quelqu'un qui fait vraiment ce métier au quotidien.
Ton {business_profile.brand_tone}.
Audience: {business_profile.target_audience}.

50-120 mots max. Naturel et utile.
SANS emojis clichés, SANS jargon marketing.

JSON uniquement:
{{
    "content": "ton contenu naturel ici",
    "hashtags": ["hashtag1", "hashtag2"],
    "call_to_action": "question ou phrase d'engagement simple",
    "content_type": "{content_type}"
}}"""
                
                response = await chat.send_message(UserMessage(text=prompt))
                
                try:
                    response_clean = response.strip()
                    if response_clean.startswith('```json'):
                        response_clean = response_clean[7:-3].strip()
                    
                    content_data = json.loads(response_clean) 
                    generated_content.append(content_data)
                except:
                    # Natural fallback
                    generated_content.append({
                        "content": f"Petite observation sur notre métier de {business_profile.business_type}...",
                        "hashtags": [business_profile.business_type.replace(' ', '').lower()],
                        "call_to_action": "Ça vous parle ?",
                        "content_type": content_type
                    })
            
            return generated_content
            
        except Exception as e:
            logger.error(f"Error generating sector content: {e}")
            return []
    
    @staticmethod
    async def generate_performance_optimized_content(business_profile: BusinessProfile, performance_data: Dict[str, Any], notes_list: List[ContentNote] = None):
        """Generate content optimized based on performance insights with adaptive prompts"""
        try:
            logger.info("🎯 Generating performance-optimized content with adaptive prompts...")
            
            if notes_list is None:
                notes_list = []
            
            # PHASE 3: GET OPTIMIZED PROMPT
            logger.info("🧠 Step 1: Generating optimized prompt...")
            business_profile_dict = business_profile.dict() if hasattr(business_profile, 'dict') else business_profile
            
            optimized_prompt = await prompt_optimizer.generate_optimized_prompt(
                business_profile_dict,
                performance_data,
                "social_post"
            )
            
            logger.info(f"✅ Using optimized prompt version: {optimized_prompt['prompt_version']}")
            logger.info(f"🎯 Expected improvement: {optimized_prompt.get('expected_improvement', 0)}%")
            
            # Prepare notes context
            notes_context = ""
            if notes_list:
                notes_context = "\nINFORMATIONS IMPORTANTES À INTÉGRER:\n"
                for note in notes_list:
                    priority_emoji = "🔴" if note.priority == "high" else "🟡" if note.priority == "medium" else "🟢"
                    notes_context += f"- {priority_emoji} {note.title}: {note.content}\n"
            
            # PHASE 3: USE ADAPTIVE SYSTEM MESSAGE
            adaptive_system_message = optimized_prompt["system_message"] + notes_context
            
            chat = LlmChat(
                api_key=os.environ['OPENAI_API_KEY'],
                session_id=f"adaptive_{optimized_prompt['prompt_version']}",
                system_message=adaptive_system_message
            ).with_model("openai", "gpt-4o")
            
            # PHASE 3: USE ADAPTIVE USER PROMPT
            adaptive_user_prompt = optimized_prompt["user_prompt_template"].replace("[X]", "3")
            
            logger.info("🚀 Step 2: Generating content with adaptive prompt...")
            response = await chat.send_message(UserMessage(content=adaptive_user_prompt))
            
            try:
                data = json.loads(response.content)
                posts = data.get("posts", [])
                
                logger.info(f"✅ Generated {len(posts)} posts using adaptive prompt {optimized_prompt['prompt_version']}")
                
                # PHASE 3: ADD COMPREHENSIVE METADATA
                for post in posts:
                    post["generation_type"] = "adaptive_optimized"
                    post["prompt_version"] = optimized_prompt["prompt_version"]
                    post["prompt_type"] = optimized_prompt["prompt_type"]
                    post["based_on_insights"] = optimized_prompt["based_on_insights"]
                    post["expected_improvement"] = optimized_prompt.get("expected_improvement", 0)
                    
                    # Detailed prompt elements metadata
                    post["prompt_elements"] = optimized_prompt["prompt_elements"]
                    post["optimization_focus"] = optimized_prompt["optimization_focus"]
                    post["insights_applied"] = optimized_prompt.get("insights_applied", [])
                    
                    # Performance tracking metadata
                    post["generation_metadata"] = {
                        "prompt_version": optimized_prompt["prompt_version"],
                        "prompt_type": optimized_prompt["prompt_type"],
                        "prompt_elements": optimized_prompt["prompt_elements"],
                        "optimization_focus": optimized_prompt["optimization_focus"],
                        "generation_timestamp": datetime.utcnow(),
                        "adaptive_features_used": [
                            "tone_adaptation",
                            "length_optimization", 
                            "hashtag_strategy",
                            "keyword_integration",
                            "topic_selection"
                        ],
                        "performance_baseline": performance_data.get("avg_engagement_rate", 0),
                        "expected_improvement": optimized_prompt.get("expected_improvement", 0)
                    }
                    
                    # Track specific optimizations applied
                    optimization_applied = []
                    if performance_data.get("recommended_hashtags"):
                        optimization_applied.append("performance_hashtags")
                    if performance_data.get("high_performing_keywords"):
                        optimization_applied.append("keyword_optimization")
                    if performance_data.get("optimal_content_length"):
                        optimization_applied.append("length_optimization")
                    if performance_data.get("high_performing_topics"):
                        optimization_applied.append("topic_focus")
                    
                    post["optimization_applied"] = optimization_applied
                
                return posts
                
            except json.JSONDecodeError:
                logger.error("Failed to parse adaptive prompt response")
                # Fallback to basic content with metadata
                fallback_posts = [{
                    "platform": "facebook",
                    "content": response.content[:200] + "...",
                    "hashtags": performance_data.get("recommended_hashtags", [])[:3],
                    "visual_description": "Contenu généré par prompt adaptatif",
                    "generation_type": "adaptive_fallback",
                    "prompt_version": optimized_prompt["prompt_version"],
                    "based_on_insights": optimized_prompt["based_on_insights"]
                }]
                return fallback_posts
                
        except Exception as e:
            logger.error(f"Error in adaptive content generation: {e}")
            # Ultimate fallback to original method
            logger.info("🔄 Falling back to original performance optimization...")
            return await AutoContentGenerator._generate_fallback_optimized_content(business_profile, performance_data, notes_list)
    
    @staticmethod
    async def _generate_fallback_optimized_content(business_profile: BusinessProfile, performance_data: Dict[str, Any], notes_list: List[ContentNote] = None):
        """Fallback method for when adaptive prompts fail"""
        try:
            # Extract performance insights (original logic)
            has_insights = performance_data.get('has_insights', False)
            recommended_hashtags = performance_data.get('recommended_hashtags', [])
            high_performing_keywords = performance_data.get('high_performing_keywords', [])
            high_performing_topics = performance_data.get('high_performing_topics', [])
            ai_recommendations = performance_data.get('ai_recommendations', [])
            content_length = performance_data.get('optimal_content_length', '100-150')
            
            if notes_list is None:
                notes_list = []
            
            # Build performance-aware system message (original logic but simplified)
            if has_insights:
                performance_context = f"""
INSIGHTS DE PERFORMANCE ANALYSÉS:
- Hashtags performants: {', '.join(recommended_hashtags[:3]) if recommended_hashtags else 'Aucun data disponible'}
- Mots-clés qui marchent: {', '.join(high_performing_keywords[:3]) if high_performing_keywords else 'Aucun data disponible'}
- Sujets engageants: {', '.join(high_performing_topics[:2]) if high_performing_topics else 'Aucun data disponible'}
- Longueur optimale: {content_length} caractères

UTILISE CES INSIGHTS pour optimiser le contenu généré !
"""
            else:
                performance_context = "Focus sur du contenu engageant et authentique."
            
            # Prepare notes context
            notes_context = ""
            if notes_list:
                notes_context = "\nINFORMATIONS IMPORTANTES À INTÉGRER:\n"
                for note in notes_list:
                    priority_emoji = "🔴" if note.priority == "high" else "🟡" if note.priority == "medium" else "🟢"
                    notes_context += f"- {priority_emoji} {note.title}: {note.content}\n"
            
            system_message = f"""Tu génères du contenu pour {business_profile.business_name} - {business_profile.business_type}.

⚠️ FILTRAGE DE CONTENU STRICT - REFUS ABSOLU:
❌ JAMAIS de contenu injurieux, offensant, discriminatoire, haineux
❌ JAMAIS de références sexuelles, pornographiques ou suggestives
❌ JAMAIS de contenu violent, agressif ou menaçant
❌ JAMAIS de références aux drogues, substances illégales, alcool excessif
❌ JAMAIS de contenu lié aux armes, violence, criminalité
❌ JAMAIS de propos politiques extrêmes ou controversés
❌ JAMAIS de contenu pouvant nuire à des mineurs
❌ JAMAIS de fake news, désinformation ou théories complotistes
❌ JAMAIS de promotion d'activités illégales ou dangereuses

✅ CONTENU REQUIS: Professionnel, bienveillant, constructif et légal uniquement

PROFIL ENTREPRISE:
- Audience: {business_profile.target_audience}
- Ton: {business_profile.brand_tone}

{performance_context}
{notes_context}

Style authentique obligatoire mais respectueux. Génère 3 posts variés et optimisés."""
            
            chat = LlmChat(
                api_key=os.environ['OPENAI_API_KEY'],
                session_id=f"fallback_{uuid.uuid4()}",
                system_message=system_message
            ).with_model("openai", "gpt-4o")
            
            prompt = f"""Génère 3 posts optimisés pour les réseaux sociaux.
            
            JSON uniquement:
            {{"posts": [
              {{"platform": "facebook", "content": "contenu du post", "hashtags": ["hashtag1", "hashtag2"], "visual_description": "description visuel"}},
              {{"platform": "instagram", "content": "contenu du post", "hashtags": ["hashtag1", "hashtag2"], "visual_description": "description visuel"}},
              {{"platform": "linkedin", "content": "contenu du post", "hashtags": ["hashtag1", "hashtag2"], "visual_description": "description visuel"}}
            ]}}"""
            
            response = await chat.send_message(UserMessage(content=prompt))
            
            try:
                data = json.loads(response.content)
                posts = data.get("posts", [])
                
                # Add basic metadata
                for post in posts:
                    post["generation_type"] = "fallback_optimized"
                    post["based_on_insights"] = has_insights
                
                return posts
                
            except json.JSONDecodeError:
                return [{
                    "platform": "facebook",
                    "content": "Contenu généré en mode fallback - merci de votre patience !",
                    "hashtags": recommended_hashtags[:3] if recommended_hashtags else ["#entreprise"],
                    "visual_description": "Contenu de secours",
                    "generation_type": "emergency_fallback"
                }]
                
        except Exception as e:
            logger.error(f"Error in fallback content generation: {e}")
            return [{
                "platform": "facebook",
                "content": "Nous travaillons à améliorer notre service. Restez connectés !",
                "hashtags": ["#service", "#amélioration"],
                "visual_description": "Message de service",
                "generation_type": "emergency"
            }]

class ContentScheduler:
    """Main scheduler for automatic content generation"""
    
    @staticmethod
    async def calculate_next_generation_date(business_profile: BusinessProfile) -> datetime:
        """Calculate when the next generation should happen"""
        now = datetime.utcnow()
        
        frequency_map = {
            "daily": 7,        # Generate weekly for daily posts
            "3x_week": 7,      # Generate weekly for 3x/week posts  
            "weekly": 30,      # Generate monthly for weekly posts
            "bi_weekly": 30    # Generate monthly for bi-weekly posts
        }
        
        days_to_add = frequency_map.get(business_profile.posting_frequency, 7)
        return now + timedelta(days=days_to_add)
    
    @staticmethod
    async def calculate_content_reminder_date(next_generation: datetime) -> datetime:
        """Calculate when to send content reminder (3 days before)"""
        return next_generation - timedelta(days=3)
    
    @staticmethod
    async def check_content_sufficiency(business_id: str, required_posts: int) -> dict:
        """Check if business has enough content for generation"""
        ready_content = await db.content_uploads.find({
            "business_id": business_id,
            "status": "ready"
        }).to_list(100)
        
        return {
            "available_content": len(ready_content),
            "required_posts": required_posts,
            "sufficient": len(ready_content) >= required_posts,
            "deficit": max(0, required_posts - len(ready_content))
        }
    
    @staticmethod
    async def analyze_performance_before_generation(business_id: str, frequency: str) -> Dict[str, Any]:
        """Analyze post performance before generating new content"""
        try:
            logger.info(f"🔍 Starting performance analysis for business {business_id}")
            
            # Determine analysis period based on frequency
            if frequency in ["weekly", "bi_weekly"]:
                days_back = 7  # Analyze last week for weekly generation
                analysis_type = "weekly"
            elif frequency in ["daily", "3x_week"]:
                days_back = 30  # Analyze last month for monthly generation  
                analysis_type = "monthly"
            else:
                days_back = 7
                analysis_type = "weekly"
            
            logger.info(f"📊 Analyzing last {days_back} days ({analysis_type} analysis)")
            
            # Collect metrics using analytics engine
            metrics = await analytics_engine.collect_post_metrics(business_id, days_back)
            
            if not metrics:
                logger.info("📈 No metrics found - using fallback recommendations")
                return {
                    "has_insights": False,
                    "analysis_type": analysis_type,
                    "metrics_collected": 0,
                    "fallback_recommendations": [
                        "Utilisez des hashtags pertinents pour votre secteur",
                        "Variez entre contenu promotionnel et informatif",
                        "Engagez avec votre audience via des questions",
                        "Maintenez une cohérence dans votre ton de marque"
                    ],
                    "optimal_content_length": "100-150",
                    "recommended_hashtags": [],
                    "high_performing_topics": []
                }
            
            # Analyze patterns and generate insights
            insights = await analytics_engine.analyze_content_patterns(business_id, metrics)
            
            logger.info(f"✅ Analysis complete: {insights.total_posts_analyzed} posts analyzed, {insights.avg_engagement_rate:.2f}% avg engagement")
            
            # Extract actionable insights for content generation
            performance_data = {
                "has_insights": True,
                "analysis_type": analysis_type,
                "metrics_collected": len(metrics),
                "total_posts_analyzed": insights.total_posts_analyzed,
                "avg_engagement_rate": insights.avg_engagement_rate,
                
                # AI recommendations
                "ai_recommendations": insights.ai_recommendations,
                "content_strategy_suggestions": insights.content_strategy_suggestions,
                
                # Content optimization data
                "optimal_content_length": insights.optimal_content_length.pattern_value if insights.optimal_content_length else "100-150",
                "recommended_hashtags": [h.pattern_value for h in insights.top_hashtags[:5]],
                "high_performing_keywords": [k.pattern_value for k in insights.top_keywords[:5]],
                "high_performing_topics": [t.pattern_value for t in insights.high_performing_topics[:3]],
                "best_posting_times": [t.pattern_value for t in insights.best_posting_times[:2]],
                
                # Performance benchmarks
                "best_performing_post_id": insights.best_performing_post_id,
                "performance_insights_id": insights.id,
                
                # Generation guidance
                "content_generation_guidance": {
                    "tone_suggestions": "Continuez avec votre ton actuel" if insights.avg_engagement_rate > 5.0 else "Essayez un ton plus engageant et personnel",
                    "hashtag_strategy": f"Intégrez ces hashtags performants: {', '.join([h.pattern_value for h in insights.top_hashtags[:3]])}",
                    "topic_focus": f"Concentrez-vous sur: {', '.join([t.pattern_value for t in insights.high_performing_topics[:2]])}" if insights.high_performing_topics else "Variez vos sujets pour maintenir l'intérêt",
                    "length_optimization": f"Visez {insights.optimal_content_length.pattern_value.replace('_chars', ' caractères')}" if insights.optimal_content_length else "Gardez vos posts entre 100-150 caractères"
                }
            }
            
            # Store analysis results for use in generation
            analysis_record = {
                "id": str(uuid.uuid4()),
                "business_id": business_id,
                "analysis_date": datetime.utcnow(),
                "analysis_type": analysis_type,
                "performance_data": performance_data,
                "insights_id": insights.id,
                "used_for_generation": False,
                "created_at": datetime.utcnow()
            }
            
            await db.performance_analysis_results.insert_one(analysis_record)
            
            logger.info(f"💾 Performance analysis stored with ID: {analysis_record['id']}")
            return performance_data
            
        except Exception as e:
            logger.error(f"❌ Error in performance analysis: {e}")
            # Return fallback data
            return {
                "has_insights": False,
                "analysis_type": "fallback",
                "metrics_collected": 0,
                "error": str(e),
                "fallback_recommendations": [
                    "Focalisez-vous sur la qualité du contenu",
                    "Utilisez des visuels attractifs",
                    "Publiez régulièrement pour maintenir l'engagement",
                    "Répondez aux commentaires pour créer une communauté"
                ],
                "optimal_content_length": "100-150",
                "recommended_hashtags": [],
                "high_performing_topics": []
            }
    
    @staticmethod
    async def generate_posts_automatically(business_id: str):
        """Automatically generate posts for a business with performance analysis"""
        try:
            logger.info(f"🚀 Starting automatic post generation for business {business_id}")
            
            # Get business profile
            business_profile = await db.business_profiles.find_one({"id": business_id})
            if not business_profile:
                logger.error(f"Business profile not found: {business_id}")
                return
            
            business_prof = BusinessProfile(**business_profile)
            logger.info(f"📋 Business: {business_prof.business_name} - Frequency: {business_prof.posting_frequency}")
            
            # PHASE 2: PERFORMANCE ANALYSIS BEFORE GENERATION
            logger.info("🔍 Step 1/4: Analyzing previous post performance...")
            performance_data = await ContentScheduler.analyze_performance_before_generation(
                business_id, 
                business_prof.posting_frequency
            )
            
            logger.info(f"📊 Analysis complete - Insights available: {performance_data['has_insights']}")
            if performance_data['has_insights']:
                logger.info(f"💡 Key recommendations: {performance_data['ai_recommendations'][:2]}")
            
            logger.info("📝 Step 2/4: Preparing content generation...")
            
            # Calculate required posts
            frequency_requirements = {
                "daily": 7,
                "3x_week": 3, 
                "weekly": 1,
                "bi_weekly": 2
            }
            
            required_weekly = frequency_requirements.get(business_prof.posting_frequency, 3)
            platforms_count = len(business_prof.preferred_platforms)
            total_required = required_weekly * platforms_count
            
            logger.info(f"📊 Posts needed: {total_required} ({required_weekly} per platform × {platforms_count} platforms)")
            
            # Check content sufficiency
            content_status = await ContentScheduler.check_content_sufficiency(business_id, total_required)
            
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
            
            logger.info("📝 Step 3/4: Generating content from user uploads...")
            
            # Generate from user content first
            for content in ready_content:
                content_obj = ContentUpload(**content)
                if content_obj.description:
                    generated_posts_data = await analyze_content_with_ai(
                        content_obj.file_path,
                        content_obj.description,
                        business_prof,
                        notes_list
                    )
                    
                    # Save posts with proper scheduling
                    for i, post_data in enumerate(generated_posts_data):
                        scheduled_date = datetime.utcnow() + timedelta(days=i+1)
                        
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
                    
                    # Mark as processed
                    await db.content_uploads.update_one(
                        {"id": content_obj.id},
                        {"$set": {"status": "processed"}}
                    )
            
            logger.info(f"✅ Generated {len(all_generated_posts)} posts from user content")
            
            # Generate automatic content if needed (PERFORMANCE-OPTIMIZED)
            if len(all_generated_posts) < total_required:
                remaining_needed = total_required - len(all_generated_posts)
                logger.info(f"🎯 Step 4/4: Generating {remaining_needed} performance-optimized posts...")
                
                # Use performance-optimized generation
                optimized_content = await AutoContentGenerator.generate_performance_optimized_content(
                    business_prof, 
                    performance_data, 
                    notes_list
                )
                
                logger.info(f"🤖 Generated {len(optimized_content)} optimized content pieces")
                
                # Save optimized posts
                posts_created = 0
                for content_data in optimized_content[:remaining_needed]:
                    for platform in business_prof.preferred_platforms:
                        if posts_created >= remaining_needed:
                            break
                            
                        scheduled_date = datetime.utcnow() + timedelta(days=len(all_generated_posts) + 1)
                        
                        # Extract content details
                        post_text = content_data.get('content', '')
                        hashtags = content_data.get('hashtags', [])
                        visual_desc = content_data.get('visual_description', 'Contenu généré automatiquement')
                        
                        generated_post = GeneratedPost(
                            business_id=business_id,
                            platform=platform,
                            post_text=post_text,
                            hashtags=hashtags,
                            scheduled_date=scheduled_date,
                            auto_generated=True,
                            visual_url=None,  # Would be generated visual URL in full implementation
                            # Add performance metadata
                            generation_metadata={
                                "type": "performance_optimized",
                                "based_on_insights": performance_data.get('has_insights', False),
                                "insights_id": performance_data.get('performance_insights_id'),
                                "analysis_type": performance_data.get('analysis_type', 'fallback'),
                                "insights_applied": content_data.get('insights_applied', {})
                            }
                        )
                        
                        await db.generated_posts.insert_one(generated_post.dict())
                        all_generated_posts.append(generated_post)
                        posts_created += 1
                    
                    if posts_created >= remaining_needed:
                        break
                
                logger.info(f"✅ Total posts generated: {len(all_generated_posts)} (Performance-optimized: {posts_created})")
                
                # Mark analysis as used for generation
                if performance_data.get('has_insights'):
                    await db.performance_analysis_results.update_one(
                        {"insights_id": performance_data.get('performance_insights_id')},
                        {"$set": {"used_for_generation": True, "generation_date": datetime.utcnow()}}
                    )
            
            # Schedule next generation
            next_generation = await ContentScheduler.calculate_next_generation_date(business_prof)
            reminder_date = await ContentScheduler.calculate_content_reminder_date(next_generation)
            
            # Create scheduled tasks
            generation_task = ScheduledTask(
                id=str(uuid.uuid4()),
                business_id=business_id,
                task_type="generate_posts",
                scheduled_date=next_generation,
                frequency="weekly" if business_prof.posting_frequency in ["daily", "3x_week"] else "monthly",
                next_run=next_generation
            )
            
            reminder_task = ScheduledTask(
                id=str(uuid.uuid4()),
                business_id=business_id,
                task_type="content_reminder", 
                scheduled_date=reminder_date,
                frequency="weekly" if business_prof.posting_frequency in ["daily", "3x_week"] else "monthly",
                next_run=reminder_date
            )
            
            await db.scheduled_tasks.insert_one(generation_task.dict())
            await db.scheduled_tasks.insert_one(reminder_task.dict())
            
            # Send notification email
            await EmailService.send_posts_ready_notification(business_prof, len(all_generated_posts))
            
            logger.info(f"Generated {len(all_generated_posts)} posts for business {business_prof.business_name}")
            return len(all_generated_posts)
            
        except Exception as e:
            logger.error(f"Error in automatic generation: {e}")
            return 0
    
    @staticmethod
    async def send_content_reminders():
        """Send content upload reminders"""
        try:
            now = datetime.utcnow()
            
            # Find reminder tasks due now
            reminder_tasks = await db.scheduled_tasks.find({
                "task_type": "content_reminder",
                "next_run": {"$lte": now},
                "active": True
            }).to_list(100)
            
            for task_data in reminder_tasks:
                task = ScheduledTask(**task_data)
                
                # Get business profile
                business_profile = await db.business_profiles.find_one({"id": task.business_id})
                if business_profile:
                    business_prof = BusinessProfile(**business_profile)
                    
                    # Calculate days until generation
                    generation_tasks = await db.scheduled_tasks.find({
                        "business_id": task.business_id,
                        "task_type": "generate_posts",
                        "next_run": {"$gt": now}
                    }).sort("next_run", 1).to_list(1)
                    
                    if generation_tasks:
                        gen_task = ScheduledTask(**generation_tasks[0])
                        days_until = (gen_task.next_run - now).days
                        
                        # Send reminder
                        await EmailService.send_content_reminder(business_prof, days_until)
                        
                        # Update next run
                        if days_until <= 0:  # If generation is today or overdue
                            next_run = now + timedelta(days=1)  # Daily reminder
                        else:
                            next_run = now + timedelta(days=1)  # Daily until generation
                        
                        await db.scheduled_tasks.update_one(
                            {"id": task.id},
                            {"$set": {"next_run": next_run}}
                        )
                        
                        logger.info(f"Sent content reminder for {business_prof.business_name}")
            
        except Exception as e:
            logger.error(f"Error sending reminders: {e}")
    
    @staticmethod
    async def run_scheduled_generations():
        """Run scheduled post generations"""
        try:
            now = datetime.utcnow()
            
            # Find generation tasks due now
            generation_tasks = await db.scheduled_tasks.find({
                "task_type": "generate_posts",
                "next_run": {"$lte": now},
                "active": True
            }).to_list(100)
            
            for task_data in generation_tasks:
                task = ScheduledTask(**task_data)
                
                # Generate posts
                posts_count = await ContentScheduler.generate_posts_automatically(task.business_id)
                
                # Calculate next run
                business_profile = await db.business_profiles.find_one({"id": task.business_id})
                if business_profile:
                    business_prof = BusinessProfile(**business_profile)
                    next_run = await ContentScheduler.calculate_next_generation_date(business_prof)
                    
                    await db.scheduled_tasks.update_one(
                        {"id": task.id},
                        {"$set": {"next_run": next_run}}
                    )
                    
                    logger.info(f"Auto-generated {posts_count} posts for {business_prof.business_name}")
            
        except Exception as e:
            logger.error(f"Error in scheduled generations: {e}")

async def main_scheduler():
    """Main scheduler loop"""
    logger.info("Starting SocialGénie Scheduler...")
    
    while True:
        try:
            # Run scheduled tasks every minute
            await ContentScheduler.run_scheduled_generations()
            await ContentScheduler.send_content_reminders()
            
            # Check for website analyses that need monthly refresh (run every hour)
            import time
            current_minute = int(time.time() / 60)
            if current_minute % 60 == 0:  # Run every hour (when minutes = 0)
                await check_and_update_website_analyses()
            
            # Check for monthly rotation (run every hour on the 1st of the month)
            if current_minute % 60 == 0:  # Run every hour
                await monthly_rotation_check()
            
            # Check for periodic notes cleanup (run once daily at midnight UTC)
            current_hour = datetime.utcnow().hour
            current_minute_exact = datetime.utcnow().minute
            
            # Run cleanup daily at 00:05 UTC to ensure we're past midnight
            if current_hour == 0 and current_minute_exact == 5:
                logger.info("🕐 Daily cleanup time reached - checking for expired periodic notes...")
                cleanup_expired_periodic_notes()
            
            # Wait 60 seconds before next check
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"Error in main scheduler: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main_scheduler())