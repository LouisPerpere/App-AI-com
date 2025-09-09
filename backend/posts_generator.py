"""
Advanced Post Generation System for Claire et Marcus
Generates intelligent social media posts based on user content, business profile, and website analysis.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import random
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

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
        self.openai_client = None
        self._init_llm()
    
    def _init_llm(self):
        """Initialize OpenAI client for post generation"""
        try:
            # Use personal OpenAI key as requested by user
            api_key = os.getenv('OPENAI_API_KEY')
            print(f"🔍 DEBUG: API key loaded: {api_key[:20] if api_key else 'None'}...")
            
            if not api_key:
                raise ValueError("No OpenAI API key found")
            
            self.openai_client = OpenAI(api_key=api_key)
            self.system_message = """Tu es un rédacteur expérimenté spécialisé dans les réseaux sociaux pour PME et artisans.

RÈGLES STRICTES DE RÉDACTION :
- BANNIR le style IA grandiose et artificiel typique de ChatGPT
- PAS de formules comme "Découvrez l'art de...", "Plongez dans l'univers de..."
- LIMITER les emojis au strict minimum (max 2-3 par post, seulement si vraiment pertinents)
- INTERDICTION ABSOLUE des ✨ et autres emojis "magiques"
- Écrire comme un vrai humain, pas comme une IA
- Ton authentique et naturel, adapté au business
- Call-to-action simples et directs
- Hashtags pertinents (max 25, mix populaires/niche)

Tu réponds EXCLUSIVEMENT au format JSON exact demandé."""
            
            print("✅ OpenAI client initialized successfully")
            logger.info("✅ OpenAI client initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize OpenAI client: {str(e)}")
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
                source_data, available_content, content_strategy, num_posts, user_id
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
        
        business_profile = source_data.get("business_profile") or {}
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
                                          strategy: Dict, num_posts: int, user_id: str) -> List[PostContent]:
        """Generate posts according to the determined strategy with ONE global ChatGPT request"""
        logger.info("✨ Step 4/6: Generating posts with AI...")
        logger.info(f"🚀 NEW APPROACH: Single global request for {num_posts} posts instead of individual requests")
        
        if not self.openai_client:
            raise Exception("OpenAI client not initialized")
        
        # Get contexts for AI
        business_context = self._format_business_context(source_data.get("business_profile"))
        all_notes = source_data.get("always_valid_notes", []) + source_data.get("month_notes", [])
        notes_context = self._format_notes_context(all_notes)
        recent_posts_context = await self._get_recent_posts_context(user_id)
        
        # Prepare content inventory for AI
        content_inventory = self._prepare_content_inventory(available_content)
        
        # Generate ALL posts with a single global request
        generated_posts = await self._generate_posts_calendar(
            business_context=business_context,
            notes_context=notes_context,
            recent_posts_context=recent_posts_context,
            content_inventory=content_inventory,
            strategy=strategy,
            num_posts=num_posts,
            available_content=available_content
        )
        
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
    
    async def _get_recent_posts_context(self, user_id: str) -> str:
        """Get context from recent posts to avoid duplication"""
        try:
            # Get recent posts from last 60 days
            from datetime import datetime, timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=60)
            
            recent_posts = list(self.db.generated_posts.find({
                "owner_id": user_id,
                "created_at": {"$gte": cutoff_date.isoformat()}
            }).sort([("created_at", -1)]).limit(20))
            
            if not recent_posts:
                return "Aucun post récent à éviter."
            
            # Format recent posts for context
            context_parts = ["POSTS RÉCENTS À ÉVITER (ne pas copier ou répéter):"]
            for i, post in enumerate(recent_posts[:10], 1):  # Max 10 recent posts
                title = post.get("title", "")[:50]
                text = post.get("text", "")[:100]
                context_parts.append(f"{i}. {title}: {text}...")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"❌ Error getting recent posts context: {str(e)}")
            return "Erreur lors de la récupération des posts récents."

    def _format_business_context(self, business_profile: Dict) -> str:
        """Format business profile for the global prompt"""
        if not business_profile:
            return "Aucun profil business disponible."
        
        context_parts = []
        context_parts.append(f"ENTREPRISE: {business_profile.get('business_name', 'Non défini')}")
        context_parts.append(f"TYPE: {business_profile.get('business_type', 'Non défini')}")
        context_parts.append(f"DESCRIPTION: {business_profile.get('business_description', 'Non définie')}")
        
        target_audience = business_profile.get('target_audience', '')
        if target_audience:
            context_parts.append(f"CIBLE: {target_audience}")
        
        return "\n".join(context_parts)
    
    def _format_notes_context(self, notes: List) -> str:
        """Format notes for the global prompt"""
        if not notes:
            return "Aucune note disponible."
        
        context_parts = []
        for note in notes[:10]:  # Limit to avoid token overflow
            context_parts.append(f"- {note.get('title', '')}: {note.get('content', '')}")
        
        return "\n".join(context_parts)
    
    def _prepare_content_inventory(self, available_content: Dict) -> str:
        """Prepare content inventory description for AI"""
        inventory_parts = []
        
        month_content = available_content.get("month_content", [])
        older_content = available_content.get("older_content", [])
        
        inventory_parts.append("CONTENU DISPONIBLE:")
        inventory_parts.append(f"- Contenu du mois: {len(month_content)} éléments")
        inventory_parts.append(f"- Contenu plus ancien: {len(older_content)} éléments")
        
        # Add details about available content WITH IDs
        if month_content:
            inventory_parts.append("\nCONTENU DU MOIS:")
            for i, content in enumerate(month_content[:5], 1):  # Show first 5
                inventory_parts.append(f"{i}. ID:{content.id} - {content.title} - {content.context}")
        
        if older_content:
            inventory_parts.append("\nCONTENU PLUS ANCIEN:")
            for i, content in enumerate(older_content[:5], 1):  # Show first 5
                inventory_parts.append(f"{i}. ID:{content.id} - {content.title} - {content.context}")
        
        return "\n".join(inventory_parts)
    
    async def _generate_posts_calendar(self, business_context: str, notes_context: str, 
                                     recent_posts_context: str, content_inventory: str,
                                     strategy: Dict, num_posts: int, available_content: Dict = None) -> List[PostContent]:
        """Generate entire posts calendar with a single AI request"""
        try:
            # Build the global prompt for generating all posts at once
            prompt = f"""Tu dois créer un calendrier complet de {num_posts} posts Instagram pour ce business.

CONTEXTE BUSINESS:
{business_context}

NOTES IMPORTANTES:
{notes_context}

{recent_posts_context}

{content_inventory}

STRATÉGIE DE CONTENU DEMANDÉE:
{self._format_strategy_for_prompt(strategy)}

RÈGLES STRICTES DE RÉDACTION:
- BANNIR absolument le style IA artificiel et grandiose
- PAS de "Découvrez l'art de...", "Plongez dans...", "Laissez-vous séduire..."
- INTERDICTION des ✨ et emojis "magiques" 
- Maximum 2-3 emojis par post, seulement si vraiment utiles
- Écrire comme un VRAI humain, pas comme ChatGPT
- Ton naturel et authentique
- Call-to-action simples et directs
- 150-200 mots maximum par post
- 15-25 hashtags pertinents par post

CONTRAINTES DE VARIÉTÉ CRITIQUE:
- Chaque post doit être UNIQUE et suffisamment différent des autres
- Varier les angles d'approche, le vocabulaire, et la structure
- NE JAMAIS répéter exactement le même contenu ou les mêmes formulations
- Adapter le niveau de détail et le style selon le type de post
- Comme le ferait un expert community manager professionnel

RÉPONSE ATTENDUE (JSON exact avec array de {num_posts} posts):
{{
    "posts": [
        {{
            "content_type": "product",
            "text": "Texte naturel sans style IA, max 2-3 emojis",
            "hashtags": ["hashtag1", "hashtag2", "hashtag3"],
            "title": "Titre simple et direct",
            "visual_id": "ID_exact_du_contenu_utilisé_de_la_liste_ci-dessus",
            "scheduling_preference": "morning|afternoon|evening"
        }},
        // ... {num_posts-1} autres posts
    ]
}}
"""
            
            logger.info(f"🤖 Sending GLOBAL request to OpenAI for {num_posts} posts")
            logger.info(f"🤖 Prompt length: {len(prompt)} characters")
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000  # Increased for multiple posts
            )
            
            response_text = response.choices[0].message.content
            logger.info(f"🤖 Global AI Response length: {len(response_text) if response_text else 0}")
            
            # Parse the global response with content mapping
            return self._parse_global_response(response_text, strategy, available_content)
            
        except Exception as e:
            logger.error(f"❌ Failed to generate posts calendar: {str(e)}")
            return []
    
    def _format_strategy_for_prompt(self, strategy: Dict) -> str:
        """Format strategy for the AI prompt"""
        strategy_parts = []
        for content_type, count in strategy.items():
            if count > 0:
                strategy_parts.append(f"- {count} posts de type '{content_type}'")
        return "\n".join(strategy_parts)
    
    def _parse_global_response(self, response_text: str, strategy: Dict, available_content: Dict = None) -> List[PostContent]:
        """Parse the global AI response into PostContent objects"""
        try:
            if not response_text or not response_text.strip():
                logger.error("❌ Empty global response from AI")
                return []
            
            # Clean response text - remove markdown code blocks if present
            clean_response = response_text.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response[7:]  # Remove ```json
            if clean_response.endswith('```'):
                clean_response = clean_response[:-3]  # Remove ```
            clean_response = clean_response.strip()
            
            response_data = json.loads(clean_response)
            posts_data = response_data.get("posts", [])
            
            if not posts_data:
                logger.error("❌ No posts found in global AI response")
                return []
            
            # Collect all available content IDs for validation
            all_content_ids = []
            if available_content:
                for content_list in available_content.values():
                    all_content_ids.extend([content.id for content in content_list])
            
            generated_posts = []
            content_index = 0  # For fallback mapping
            
            for i, post_data in enumerate(posts_data):
                # Extract the visual_id from ChatGPT response
                visual_id = post_data.get("visual_id", "")
                
                # CRITICAL FIX: Validate if ChatGPT used a real ID
                if visual_id and visual_id in all_content_ids:
                    # ChatGPT used a real ID - perfect!
                    visual_url = f"/api/content/{visual_id}/file"
                    logger.info(f"✅ Post {i+1}: ChatGPT used real ID {visual_id}")
                else:
                    # ChatGPT didn't use real IDs - apply fallback mapping
                    if available_content and content_index < len(all_content_ids):
                        real_id = all_content_ids[content_index]
                        visual_id = real_id
                        visual_url = f"/api/content/{real_id}/file"
                        content_index += 1
                        logger.warning(f"⚠️ Post {i+1}: ChatGPT used invalid ID '{post_data.get('visual_id', '')}', mapped to real ID {real_id}")
                    else:
                        # No content available - no image
                        visual_id = ""
                        visual_url = ""
                        logger.warning(f"⚠️ Post {i+1}: No content available for mapping")
                
                post = PostContent(
                    visual_url=visual_url,
                    visual_id=visual_id,
                    title=post_data.get("title", f"Post {i+1}"),
                    text=post_data.get("text", ""),
                    hashtags=post_data.get("hashtags", []),
                    platform="instagram",
                    content_type=post_data.get("content_type", "product")
                )
                
                generated_posts.append(post)
            
            logger.info(f"✅ Successfully parsed {len(generated_posts)} posts from global response")
            return generated_posts
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse global AI response: {e}")
            logger.error(f"❌ Response was: {response_text[:500]}...")
            return []
        except Exception as e:
            logger.error(f"❌ Error parsing global response: {str(e)}")
            return []
    async def _generate_single_post(self, visual_content: ContentSource, content_type: str, 
                                   business_context: str, notes_context: str, user_id: str) -> Optional[PostContent]:
        """Generate a single post with AI"""
        try:
            # Get recent posts context to avoid duplication
            recent_posts_context = await self._get_recent_posts_context(user_id)
            
            # Build prompt for AI
            prompt = f"""Crée un post Instagram {content_type} naturel et authentique.

CONTEXTE BUSINESS:
{business_context}

NOTES IMPORTANTES:
{notes_context}

CONTENU VISUEL:
- Titre: {visual_content.title}
- Contexte: {visual_content.context}
- Type: {visual_content.file_type}

{recent_posts_context}

TYPE DE POST: {content_type}
{self._get_content_type_guidelines(content_type)}

RÈGLES STRICTES DE RÉDACTION:
- BANNIR absolument le style IA artificiel et grandiose
- PAS de "Découvrez l'art de...", "Plongez dans...", "Laissez-vous séduire..."
- INTERDICTION des ✨ et emojis "magiques" 
- Maximum 2-3 emojis par post, seulement si vraiment utiles
- Écrire comme un VRAI humain, pas comme ChatGPT
- Ton naturel et authentique
- Call-to-action simples et directs
- 150-200 mots maximum
- 15-25 hashtags pertinents

CONTRAINTES DE VARIÉTÉ CRITIQUE:
- Chaque post doit être UNIQUE et suffisamment différent des autres
- Varier les angles d'approche, le vocabulaire, et la structure
- NE JAMAIS répéter exactement le même contenu ou les mêmes formulations
- Adapter le niveau de détail et le style selon le type de post
- Comme le ferait un expert community manager professionnel

RÉPONSE ATTENDUE (JSON exact):
{{
    "text": "Texte naturel sans style IA, max 2-3 emojis",
    "hashtags": ["hashtag1", "hashtag2", "hashtag3"],
    "title": "Titre simple et direct"
}}
"""
            
            # Send to OpenAI
            print("🤖 DEBUG: Sending request to OpenAI with model gpt-4o")
            print(f"🤖 DEBUG: Prompt length: {len(prompt)}")
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content
            print(f"🤖 DEBUG: Raw response: '{response_text}'")
            print(f"🤖 DEBUG: Response length: {len(response_text) if response_text else 0}")
            
            logger.info(f"   🤖 AI Response length: {len(response_text) if response_text else 0}")
            logger.info(f"   🤖 AI Response preview: {response_text[:100] if response_text else 'Empty response'}")
            
            # Parse response
            try:
                if not response_text or not response_text.strip():
                    logger.error("   ❌ Empty response from AI")
                    return None
                
                # Clean response text - remove markdown code blocks if present
                clean_response = response_text.strip()
                if clean_response.startswith('```json'):
                    clean_response = clean_response[7:]  # Remove ```json
                if clean_response.endswith('```'):
                    clean_response = clean_response[:-3]  # Remove ```
                clean_response = clean_response.strip()
                
                print(f"🤖 DEBUG: Cleaned response: '{clean_response[:200]}...'")
                    
                response_data = json.loads(clean_response)
                
                # Construct proper visual URL for frontend display
                proper_visual_url = f"/api/content/{visual_content.id}/file" if visual_content.id else ""
                
                return PostContent(
                    visual_url=proper_visual_url,
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