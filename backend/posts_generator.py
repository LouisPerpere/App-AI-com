"""
Advanced Post Generation System for Claire et Marcus
Generates intelligent social media posts based on user content, business profile, and website analysis.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import random
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from openai import OpenAI
from database import get_database

logger = logging.getLogger(__name__)

@dataclass
class PostContent:
    """Structure for a generated post"""
    visual_url: str
    visual_id: str
    title: str
    text: str
    hashtags: List[str]
    platform: str = "instagram"
    scheduled_date: datetime = None
    content_type: str = "product"  # product, backstage, value, sales, info, educational
    visual_type: str = "image"  # image, video

@dataclass
class ContentSource:
    """Source content for post generation"""
    id: str
    title: str
    context: str
    visual_url: str
    file_type: str
    attributed_month: str = None
    source: str = "upload"  # upload, pixabay
    used: bool = False

class PostsGenerator:
    """Advanced posts generation system"""
    
    def __init__(self):
        self.db = get_database().db
        self.llm_chat = None
        self._init_llm()
    
    def _init_llm(self):
        """Initialize OpenAI client for post generation"""
        try:
            # Use personal OpenAI key as requested by user
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("No OpenAI API key found")
            
            self.openai_client = OpenAI(api_key=api_key)
            self.system_message = """Tu es Claire, un expert en marketing digital et création de contenu pour les réseaux sociaux.
                
Tu génères des posts Instagram engageants et authentiques pour les entreprises.
Tu respectes toujours ces principes :
- Ton de voix adapté au business (professionnel, décontracté, etc.)
- Call-to-action pertinents selon l'objectif
- Hashtags ciblés et efficaces (max 25, mélange de populaires et niche)
- Contenus qui convertissent selon le type (vente, valeur, information, etc.)
- Adaptation parfaite à la cible définie par l'utilisateur

Tu réponds TOUJOURS au format JSON exact demandé."""
            
            logger.info("✅ OpenAI client initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenAI client: {str(e)}")
            self.openai_client = None
    
    async def generate_posts_for_month(self, user_id: str, target_month: str, num_posts: int = 20) -> Dict[str, Any]:
        """
        Generate complete post calendar for a specific month
        
        Args:
            user_id: User ID
            target_month: Month in format "octobre_2025"
            num_posts: Number of posts to generate
            
        Returns:
            Dict with generated posts and metadata
        """
        try:
            logger.info(f"🚀 Starting post generation for user {user_id}, month {target_month}, {num_posts} posts")
            
            # STEP 1: Gather all source data
            source_data = self._gather_source_data(user_id, target_month)
            
            # STEP 2: Collect available content
            available_content = self._collect_available_content(user_id, target_month)
            
            # STEP 3: Determine content mix strategy  
            content_strategy = self._determine_content_strategy(source_data, num_posts)
            
            # STEP 4: Generate posts according to strategy
            generated_posts = await self._generate_posts_with_strategy(
                source_data, available_content, content_strategy, num_posts
            )
            
            # STEP 5: Create posting schedule
            scheduled_posts = self._create_posting_schedule(generated_posts, target_month)
            
            # STEP 6: Save to database
            self._save_generated_posts(user_id, scheduled_posts)
            
            logger.info(f"✅ Generated {len(scheduled_posts)} posts successfully")
            
            return {
                "success": True,
                "posts_count": len(scheduled_posts),
                "posts": scheduled_posts,
                "strategy": content_strategy,
                "sources_used": {
                    "business_profile": source_data.get("business_profile") is not None,
                    "website_analysis": source_data.get("website_analysis") is not None,
                    "month_content": len(source_data.get("month_content", [])),
                    "always_valid_notes": len(source_data.get("always_valid_notes", [])),
                    "month_notes": len(source_data.get("month_notes", [])),
                    "older_content": len(source_data.get("older_content", [])),
                    "pixabay_searches": source_data.get("pixabay_used", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Post generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "posts_count": 0,
                "posts": []
            }
    
    def _gather_source_data(self, user_id: str, target_month: str) -> Dict[str, Any]:
        """Gather all source data for post generation"""
        logger.info("📊 Step 1/6: Gathering source data...")
        
        source_data = {}
        
        # Business profile
        business_profile = self.db.business_profiles.find_one({"owner_id": user_id})
        source_data["business_profile"] = business_profile
        logger.info(f"   📋 Business profile: {'✅' if business_profile else '❌'}")
        
        # Website analysis
        website_analysis = self.db.website_analyses.find_one(
            {"user_id": user_id}, 
            sort=[("created_at", -1)]
        )
        source_data["website_analysis"] = website_analysis
        logger.info(f"   🌐 Website analysis: {'✅' if website_analysis else '❌'}")
        
        # Always valid notes
        always_valid_notes = list(self.db.content_notes.find({
            "owner_id": user_id,
            "is_monthly_note": True,
            "deleted": {"$ne": True}
        }).limit(100))
        source_data["always_valid_notes"] = always_valid_notes
        logger.info(f"   📝 Always valid notes: {len(always_valid_notes)}")
        
        # Month-specific notes  
        month_notes = list(self.db.content_notes.find({
            "owner_id": user_id,
            "is_monthly_note": False,
            "note_month": self._parse_month_number(target_month),
            "note_year": self._parse_year(target_month),
            "deleted": {"$ne": True}
        }).limit(100))
        source_data["month_notes"] = month_notes
        logger.info(f"   📅 Month notes: {len(month_notes)}")
        
        return source_data
    
    def _collect_available_content(self, user_id: str, target_month: str) -> Dict[str, List[ContentSource]]:
        """Collect all available visual content in priority order"""
        logger.info("🖼️ Step 2/6: Collecting available content...")
        
        content = {
            "month_content": [],
            "older_content": [],
            "pixabay_candidates": []
        }
        
        # Month-specific content (highest priority)
        month_content = list(self.db.media.find({
            "owner_id": user_id,
            "attributed_month": target_month,
            "deleted": {"$ne": True}
        }).limit(100))
        
        for item in month_content:
            content["month_content"].append(ContentSource(
                id=str(item.get("_id", "")),
                title=item.get("title", ""),
                context=item.get("context", ""),
                visual_url=item.get("url", ""),
                file_type=item.get("file_type", ""),
                attributed_month=target_month,
                source="upload"
            ))
        
        logger.info(f"   📅 Month content: {len(content['month_content'])}")
        
        # Older content (fallback)
        older_content = list(self.db.media.find({
            "owner_id": user_id,
            "attributed_month": {"$ne": target_month},
            "used_in_posts": {"$ne": True},
            "deleted": {"$ne": True}
        }).sort([("created_at", 1)]).limit(100))  # Oldest first
        
        for item in older_content:
            content["older_content"].append(ContentSource(
                id=str(item.get("_id", "")),
                title=item.get("title", ""),
                context=item.get("context", ""),
                visual_url=item.get("url", ""),
                file_type=item.get("file_type", ""),
                attributed_month=item.get("attributed_month"),
                source="upload"
            ))
        
        logger.info(f"   📂 Older content: {len(content['older_content'])}")
        
        return content
    
    def _determine_content_strategy(self, source_data: Dict, num_posts: int) -> Dict[str, Any]:
        """Determine optimal content mix based on business type"""
        logger.info("🎯 Step 3/6: Determining content strategy...")
        
        business_profile = source_data.get("business_profile", {})
        business_type = business_profile.get("business_type", "service")
        
        # Content type distribution based on business type
        if business_type == "ecommerce":
            content_mix = {
                "product": 0.40,  # Product showcase
                "backstage": 0.15,  # Behind the scenes
                "value": 0.20,  # Value/tips
                "sales": 0.15,  # Direct sales
                "educational": 0.10  # Educational content
            }
        elif business_type == "service":
            content_mix = {
                "value": 0.35,  # Value/expertise
                "educational": 0.25,  # Educational
                "backstage": 0.20,  # Behind the scenes
                "sales": 0.10,  # Service promotion
                "product": 0.10  # Service showcase
            }
        elif business_type == "restaurant":
            content_mix = {
                "product": 0.35,  # Food/dishes
                "backstage": 0.30,  # Kitchen/preparation
                "value": 0.15,  # Food tips/recipes
                "sales": 0.10,  # Promotions
                "educational": 0.10  # Food education
            }
        else:  # Default mix
            content_mix = {
                "product": 0.30,
                "value": 0.25,
                "backstage": 0.20,
                "educational": 0.15,
                "sales": 0.10
            }
        
        # Calculate actual numbers
        strategy = {}
        remaining = num_posts
        
        for content_type, ratio in content_mix.items():
            count = max(1, int(num_posts * ratio))
            strategy[content_type] = min(count, remaining)
            remaining -= strategy[content_type]
        
        # Distribute remaining posts
        while remaining > 0:
            for content_type in content_mix.keys():
                if remaining > 0:
                    strategy[content_type] += 1
                    remaining -= 1
                else:
                    break
        
        logger.info(f"   📊 Content strategy: {strategy}")
        return strategy
    
    async def _generate_posts_with_strategy(self, source_data: Dict, available_content: Dict, 
                                          strategy: Dict, num_posts: int) -> List[PostContent]:
        """Generate posts according to the determined strategy"""
        logger.info("✨ Step 4/6: Generating posts with AI...")
        
        if not self.llm_chat:
            raise Exception("LLM not initialized")
        
        generated_posts = []
        used_content = []
        
        # Prepare content pools
        month_content = available_content["month_content"].copy()
        older_content = available_content["older_content"].copy()
        
        business_profile = source_data.get("business_profile", {})
        website_analysis = source_data.get("website_analysis", {})
        always_valid_notes = source_data.get("always_valid_notes", [])
        month_notes = source_data.get("month_notes", [])
        
        # Create context for AI
        business_context = self._build_business_context(business_profile, website_analysis)
        notes_context = self._build_notes_context(always_valid_notes, month_notes)
        
        for content_type, count in strategy.items():
            logger.info(f"   🎨 Generating {count} {content_type} posts...")
            
            for i in range(count):
                # Select content source
                visual_content = None
                
                # Priority: month content first
                if month_content:
                    visual_content = month_content.pop(0)
                    logger.info(f"   📅 Using month content: {visual_content.title}")
                elif older_content:
                    visual_content = older_content.pop(0)
                    logger.info(f"   📂 Using older content: {visual_content.title}")
                else:
                    # Create fallback content for testing when no visual content is available
                    logger.info(f"   📸 No visual content available, creating fallback content")
                    visual_content = ContentSource(
                        id=f"fallback_{content_type}_{i}",
                        title=f"Contenu {content_type} pour {business_profile.get('business_name', 'votre entreprise')}",
                        context=f"Contenu généré automatiquement pour illustrer un post {content_type}",
                        visual_url="",
                        file_type="image/jpeg",
                        attributed_month="octobre_2025",
                        source="generated"
                    )
                
                if visual_content:
                    # Generate post with AI
                    post = await self._generate_single_post(
                        visual_content, content_type, business_context, notes_context
                    )
                    
                    if post:
                        generated_posts.append(post)
                        used_content.append(visual_content.id)
        
        # Mark used content
        if used_content:
            from bson import ObjectId
            object_ids = []
            for content_id in used_content:
                try:
                    object_ids.append(ObjectId(content_id))
                except:
                    pass  # Skip invalid IDs
            
            if object_ids:
                self.db.media.update_many(
                    {"_id": {"$in": object_ids}},
                    {"$set": {"used_in_posts": True}}
                )
        
        logger.info(f"   ✅ Generated {len(generated_posts)} posts")
        return generated_posts
    
    def _build_business_context(self, business_profile: Dict, website_analysis: Dict) -> str:
        """Build business context for AI generation"""
        context_parts = []
        
        if business_profile:
            context_parts.append(f"ENTREPRISE: {business_profile.get('business_name', 'Non défini')}")
            context_parts.append(f"TYPE: {business_profile.get('business_type', 'Non défini')}")
            context_parts.append(f"DESCRIPTION: {business_profile.get('business_description', 'Non définie')}")
            
            target_audience = business_profile.get('target_audience', '')
            if target_audience:
                context_parts.append(f"CIBLE: {target_audience}")
            
        if website_analysis:
            analysis_data = website_analysis.get('analysis', {})
            if analysis_data.get('target_audience_suggestions'):
                context_parts.append(f"CIBLE DÉTECTÉE: {analysis_data['target_audience_suggestions']}")
            if analysis_data.get('business_description'):
                context_parts.append(f"ACTIVITÉ DÉTECTÉE: {analysis_data['business_description']}")
        
        return "\n".join(context_parts)
    
    def _build_notes_context(self, always_valid_notes: List, month_notes: List) -> str:
        """Build notes context for AI generation"""
        context_parts = []
        
        if always_valid_notes:
            context_parts.append("NOTES TOUJOURS VALIDES:")
            for note in always_valid_notes[:5]:  # Limit to avoid token overflow
                context_parts.append(f"- {note.get('title', '')}: {note.get('content', '')}")
        
        if month_notes:
            context_parts.append("NOTES DU MOIS:")
            for note in month_notes[:5]:
                context_parts.append(f"- {note.get('title', '')}: {note.get('content', '')}")
        
        return "\n".join(context_parts)
    
    async def _generate_single_post(self, visual_content: ContentSource, content_type: str, 
                                   business_context: str, notes_context: str) -> Optional[PostContent]:
        """Generate a single post with AI"""
        try:
            # Build prompt for AI
            prompt = f"""Génère un post Instagram {content_type} parfait.

CONTEXTE BUSINESS:
{business_context}

NOTES IMPORTANTES:
{notes_context}

CONTENU VISUEL:
- Titre: {visual_content.title}
- Contexte: {visual_content.context}
- Type: {visual_content.file_type}

TYPE DE POST: {content_type}
{self._get_content_type_guidelines(content_type)}

RÉPONSE ATTENDUE (JSON exact):
{{
    "text": "Texte du post engageant avec émojis pertinents",
    "hashtags": ["hashtag1", "hashtag2", "hashtag3"],
    "title": "Titre court accrocheur"
}}

Règles:
- Texte 150-200 mots max
- 15-25 hashtags stratégiques 
- Ton adapté au business
- Call-to-action pertinent
- Émojis naturels
"""
            
            # Send to AI
            user_message = UserMessage(text=prompt)
            response = await self.llm_chat.send_message(user_message)
            
            logger.info(f"   🤖 AI Response length: {len(response) if response else 0}")
            logger.info(f"   🤖 AI Response preview: {response[:100] if response else 'Empty response'}")
            
            # Parse response
            try:
                if not response or not response.strip():
                    logger.error("   ❌ Empty response from AI")
                    return None
                    
                response_data = json.loads(response)
                
                return PostContent(
                    visual_url=visual_content.visual_url,
                    visual_id=visual_content.id,
                    title=response_data.get("title", visual_content.title),
                    text=response_data.get("text", ""),
                    hashtags=response_data.get("hashtags", []),
                    platform="instagram",
                    content_type=content_type,
                    visual_type="video" if visual_content.file_type.startswith("video") else "image"
                )
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse AI response: {e}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to generate post: {str(e)}")
            return None
    
    def _get_content_type_guidelines(self, content_type: str) -> str:
        """Get specific guidelines for each content type"""
        guidelines = {
            "product": """
OBJECTIF: Mettre en valeur un produit/service
STYLE: Descriptif, bénéfices, caractéristiques
CTA: "Découvrez", "Commandez", "Plus d'infos"
""",
            "backstage": """
OBJECTIF: Montrer les coulisses, l'authenticité  
STYLE: Personnel, humain, transparent
CTA: "Suivez-nous", "Posez vos questions"
""",
            "value": """
OBJECTIF: Apporter de la valeur, conseils, astuces
STYLE: Informatif, utile, expertise
CTA: "Sauvegardez", "Partagez", "Commentez"
""",
            "sales": """
OBJECTIF: Conversion directe, promotion
STYLE: Urgence, bénéfices clairs, offre
CTA: "Achetez maintenant", "Profitez", "Contactez-nous"
""",
            "educational": """
OBJECTIF: Éduquer, expliquer, former
STYLE: Pédagogique, étapes, exemples
CTA: "Apprenez plus", "Essayez", "Suivez le guide"
"""
        }
        
        return guidelines.get(content_type, "")
    
    def _get_pixabay_content(self, business_context: str, content_type: str) -> Optional[ContentSource]:
        """Get Pixabay content as fallback (simplified for now)"""
        # TODO: Implement intelligent Pixabay search based on business context
        logger.info(f"   📸 Would search Pixabay for {content_type} content")
        return None
    
    def _create_posting_schedule(self, posts: List[PostContent], target_month: str) -> List[PostContent]:
        """Create intelligent posting schedule"""
        logger.info("📅 Step 5/6: Creating posting schedule...")
        
        # Parse target month
        month_name, year = target_month.split('_')
        year = int(year)
        
        month_map = {
            'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4,
            'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8,
            'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
        }
        
        month_num = month_map.get(month_name, 10)
        
        # Create schedule spread across the month
        start_date = datetime(year, month_num, 1)
        
        # Optimal posting times for Instagram (research-based)
        optimal_hours = [9, 11, 13, 17, 19, 21]  # Best engagement hours
        
        for i, post in enumerate(posts):
            # Distribute posts across the month
            day_offset = (i * 30) // len(posts) + 1
            hour = random.choice(optimal_hours)
            
            scheduled_date = start_date + timedelta(days=day_offset, hours=hour)
            post.scheduled_date = scheduled_date
        
        # Sort by scheduled date
        posts.sort(key=lambda p: p.scheduled_date)
        
        logger.info(f"   📅 Scheduled {len(posts)} posts across {target_month}")
        return posts
    
    def _save_generated_posts(self, user_id: str, posts: List[PostContent]):
        """Save generated posts to database"""
        logger.info("💾 Step 6/6: Saving generated posts...")
        
        # Clear existing posts for this month
        # TODO: Add month filtering when saving
        
        for post in posts:
            post_doc = {
                "id": f"post_{user_id}_{int(datetime.now().timestamp())}_{posts.index(post)}",
                "owner_id": user_id,
                "visual_url": post.visual_url,
                "visual_id": post.visual_id,
                "title": post.title,
                "text": post.text,
                "hashtags": post.hashtags,
                "platform": post.platform,
                "scheduled_date": post.scheduled_date.isoformat() if post.scheduled_date else None,
                "content_type": post.content_type,
                "visual_type": post.visual_type,
                "status": "draft",
                "created_at": datetime.utcnow().isoformat(),
                "published": False
            }
            
            self.db.generated_posts.insert_one(post_doc)
        
        logger.info(f"   💾 Saved {len(posts)} posts to database")
    
    def _parse_month_number(self, target_month: str) -> int:
        """Parse month number from target_month string"""
        month_name = target_month.split('_')[0]
        month_map = {
            'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4,
            'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8,
            'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
        }
        return month_map.get(month_name, 10)
    
    def _parse_year(self, target_month: str) -> int:
        """Parse year from target_month string"""
        return int(target_month.split('_')[1])