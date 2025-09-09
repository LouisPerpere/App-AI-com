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
        
        # CRITICAL FIX: Get ALL available media, not just month-specific
        logger.info(f"   🔍 Searching for media with owner_id: {user_id}")
        
        # First try month-specific content (if attributed_month exists)
        month_content = list(self.db.media.find({
            "owner_id": user_id,
            "attributed_month": target_month,
            "deleted": {"$ne": True}
        }).limit(50))
        
        logger.info(f"   📅 Month-specific content found: {len(month_content)}")
        
        # If no month-specific content, get ALL available media for this user
        if len(month_content) == 0:
            logger.info("   📂 No month-specific content, getting all available media...")
            all_media = list(self.db.media.find({
                "owner_id": user_id,
                "deleted": {"$ne": True}
            }).sort([("created_at", -1)]).limit(50))  # Newest first
            
            logger.info(f"   📂 Total media found: {len(all_media)}")
            
            # Treat all media as "month content" for the calendar
            for item in all_media:
                # Use filename as title if no title, description as context if available
                original_filename = item.get("original_filename", "")
                # Clean filename for title (remove pixabay prefix and extensions)
                title = item.get("title") or original_filename.replace('pixabay_', '').replace('.jpg', '').replace('.jpeg', '').replace('.png', '')
                context = item.get("context") or item.get("description", "")
                
                # Truncate long context for better AI processing
                if context and len(context) > 200:
                    context = context[:200] + "..."
                
                content["month_content"].append(ContentSource(
                    id=str(item.get("_id", "")),
                    title=title if title else "Photo",
                    context=context if context else "Image pour votre business",
                    visual_url=item.get("url", ""),
                    file_type=item.get("file_type", "image/jpeg"),
                    attributed_month=target_month,  # Assign to current month
                    source=item.get("source", "upload")  # Keep source info (pixabay vs upload)
                ))
        else:
            # Process month-specific content normally
            for item in month_content:
                title = item.get("title") or item.get("original_filename", "").replace('.jpg', '').replace('.jpeg', '').replace('.png', '')
                context = item.get("context") or item.get("description", "")
                
                content["month_content"].append(ContentSource(
                    id=str(item.get("_id", "")),
                    title=title if title else "Photo",
                    context=context if context else "Contenu visuel pour votre entreprise",
                    visual_url=item.get("url", ""),
                    file_type=item.get("file_type", "image/jpeg"),
                    attributed_month=target_month,
                    source="upload"
                ))
        
        logger.info(f"   ✅ FINAL month content available: {len(content['month_content'])}")
        
        # Log first few items for debugging
        for i, item in enumerate(content["month_content"][:3]):
            logger.info(f"   📸 Content {i+1}: ID={item.id}, Title='{item.title}', Context='{item.context[:50]}...'")
        
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
        """Format complete business profile for AI context - ALL DATA"""
        if not business_profile:
            return "Aucun profil business disponible."
        
        context_parts = ["=== PROFIL BUSINESS COMPLET ==="]
        
        # Basic business info
        context_parts.append(f"Nom de l'entreprise: {business_profile.get('business_name', 'Non défini')}")
        context_parts.append(f"Type d'entreprise: {business_profile.get('business_type', 'Non défini')}")
        context_parts.append(f"Secteur d'activité: {business_profile.get('industry', 'Non défini')}")
        
        # Detailed descriptions
        if business_profile.get('business_description'):
            context_parts.append(f"Description détaillée: {business_profile['business_description']}")
        
        if business_profile.get('value_proposition'):
            context_parts.append(f"Proposition de valeur: {business_profile['value_proposition']}")
        
        # Target audience details
        if business_profile.get('target_audience'):
            context_parts.append(f"Public cible: {business_profile['target_audience']}")
            
        if business_profile.get('target_audience_details'):
            context_parts.append(f"Détails audience: {business_profile['target_audience_details']}")
        
        # Marketing info
        if business_profile.get('brand_voice'):
            context_parts.append(f"Ton de marque: {business_profile['brand_voice']}")
            
        if business_profile.get('content_themes'):
            context_parts.append(f"Thèmes de contenu: {business_profile['content_themes']}")
        
        # Business specifics
        if business_profile.get('products_services'):
            context_parts.append(f"Produits/Services: {business_profile['products_services']}")
            
        if business_profile.get('unique_selling_points'):
            context_parts.append(f"Points de différenciation: {business_profile['unique_selling_points']}")
        
        # Goals and objectives
        if business_profile.get('business_goals'):
            context_parts.append(f"Objectifs business: {business_profile['business_goals']}")
            
        if business_profile.get('social_media_goals'):
            context_parts.append(f"Objectifs réseaux sociaux: {business_profile['social_media_goals']}")
        
        # Posting preferences
        if business_profile.get('posting_frequency'):
            context_parts.append(f"Fréquence de publication: {business_profile['posting_frequency']}")
            
        if business_profile.get('preferred_post_types'):
            context_parts.append(f"Types de posts préférés: {business_profile['preferred_post_types']}")
        
        # Additional context
        if business_profile.get('competitors'):
            context_parts.append(f"Concurrents: {business_profile['competitors']}")
            
        if business_profile.get('location'):
            context_parts.append(f"Localisation: {business_profile['location']}")
        
        return "\n".join(context_parts)
    
    def _format_notes_context(self, notes: List) -> str:
        """Format notes for the global prompt"""
        if not notes:
            return "Aucune note disponible."
        
        context_parts = []
        for note in notes[:10]:  # Limit to avoid token overflow
            context_parts.append(f"- {note.get('title', '')}: {note.get('content', '')}")
        
        return "\n".join(context_parts)
    
    def _format_website_analysis_context(self, website_analysis: Dict) -> str:
        """Format complete website analysis for AI context - ALL DATA"""
        if not website_analysis:
            return "Aucune analyse de site web disponible."
        
        context_parts = ["=== ANALYSE COMPLÈTE DU SITE WEB ==="]
        
        # Basic site info
        if website_analysis.get('url'):
            context_parts.append(f"URL du site: {website_analysis['url']}")
            
        if website_analysis.get('title'):
            context_parts.append(f"Titre du site: {website_analysis['title']}")
            
        if website_analysis.get('description'):
            context_parts.append(f"Description: {website_analysis['description']}")
        
        # Content analysis
        if website_analysis.get('main_content'):
            context_parts.append(f"Contenu principal: {website_analysis['main_content']}")
            
        if website_analysis.get('key_topics'):
            context_parts.append(f"Sujets clés: {website_analysis['key_topics']}")
            
        if website_analysis.get('keywords'):
            context_parts.append(f"Mots-clés: {website_analysis['keywords']}")
        
        # Business insights
        if website_analysis.get('business_model'):
            context_parts.append(f"Modèle économique: {website_analysis['business_model']}")
            
        if website_analysis.get('target_market'):
            context_parts.append(f"Marché cible: {website_analysis['target_market']}")
            
        if website_analysis.get('value_proposition'):
            context_parts.append(f"Proposition de valeur (site): {website_analysis['value_proposition']}")
        
        # Products/Services
        if website_analysis.get('products_services'):
            context_parts.append(f"Produits/Services (site): {website_analysis['products_services']}")
            
        if website_analysis.get('unique_features'):
            context_parts.append(f"Caractéristiques uniques: {website_analysis['unique_features']}")
        
        # Marketing insights
        if website_analysis.get('content_strategy_suggestions'):
            context_parts.append(f"Suggestions stratégie contenu: {website_analysis['content_strategy_suggestions']}")
            
        if website_analysis.get('social_media_angles'):
            context_parts.append(f"Angles réseaux sociaux: {website_analysis['social_media_angles']}")
            
        if website_analysis.get('brand_personality'):
            context_parts.append(f"Personnalité de marque: {website_analysis['brand_personality']}")
        
        # Additional insights
        if website_analysis.get('competitive_advantages'):
            context_parts.append(f"Avantages concurrentiels: {website_analysis['competitive_advantages']}")
            
        if website_analysis.get('customer_pain_points'):
            context_parts.append(f"Points de douleur clients: {website_analysis['customer_pain_points']}")
            
        if website_analysis.get('content_opportunities'):
            context_parts.append(f"Opportunités de contenu: {website_analysis['content_opportunities']}")
        
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
            # Get website analysis context from source_data
            website_analysis = available_content.get("website_analysis") if hasattr(available_content, 'get') else {}
            website_context = self._format_website_analysis_context(website_analysis)
            
            # Build the global prompt for generating all posts at once
            prompt = f"""Tu dois créer un calendrier complet de {num_posts} posts Instagram pour ce business.

{business_context}

{website_context}

NOTES IMPORTANTES:
{notes_context}

{recent_posts_context}

{content_inventory}

STRATÉGIE DE CONTENU À DÉFINIR:
Analyse ce business et détermine la meilleure répartition de types de posts selon :
- Les tendances du secteur d'activité
- Les préférences de l'audience cible
- Le type d'entreprise et ses objectifs
- L'analyse du site web et des contenus disponibles

Types de posts possibles :
- MISE EN AVANT de produits/services (product)
- CONTENU INFORMATIF et éducatif (educational) 
- BACKSTAGE et coulisses (backstage)
- CONTENU DE VALEUR et conseils (value)
- PROMOTION et vente (sales)
- TÉMOIGNAGES et social proof (testimonials)
- TENDANCES et actualités du secteur (trends)

Choisis et répartis intelligemment ces types selon ce qui fonctionnera le mieux pour cette entreprise et son audience.

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
            "visual_id": "ID_exact_du_contenu_utilisé_de_la_liste_ci-dessus"
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
            
            # CRITICAL DEBUG: Log the full ChatGPT response to see what it actually returns
            logger.info("🔍 FULL CHATGPT RESPONSE:")
            logger.info(f"{response_text}")
            
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
            
            # Debug: Log the first post structure
            if posts_data:
                logger.info(f"🔍 DEBUG: First post structure: {posts_data[0]}")
                logger.info(f"🔍 DEBUG: Visual ID in first post: {posts_data[0].get('visual_id', 'NOT_FOUND')}")
            
            # Collect all available content IDs for validation
            all_content_ids = []
            if available_content:
                logger.info(f"🔍 DEBUG: available_content keys: {list(available_content.keys())}")
                for key, content_list in available_content.items():
                    logger.info(f"🔍 DEBUG: {key} has {len(content_list)} items")
                    all_content_ids.extend([content.id for content in content_list])
            
            logger.info(f"🔍 DEBUG: Total content IDs available: {len(all_content_ids)}")
            logger.info(f"🔍 DEBUG: Content IDs: {all_content_ids[:5]}...")  # Show first 5
            
            generated_posts = []
            
            for i, post_data in enumerate(posts_data):
                # Extract the real visual_id from ChatGPT response
                visual_id = post_data.get("visual_id", "")
                
                # CRITICAL: Only accept posts with REAL visual_id from available content
                if visual_id and visual_id in all_content_ids:
                    # Valid visual_id found - construct full URL like other images in the app
                    visual_url = f"/api/content/{visual_id}/file"
                    logger.info(f"   ✅ Post {i+1}: Using REAL photo ID {visual_id}")
                    logger.info(f"   📸 Constructed visual_url: {visual_url}")
                    
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
                elif visual_id and visual_id != "":
                    logger.warning(f"⚠️ Post {i+1}: visual_id '{visual_id}' not found in available content - SKIPPING POST")
                else:
                    logger.warning(f"⚠️ Post {i+1}: no visual_id provided by ChatGPT - SKIPPING POST")
                    
            # CRITICAL: Only return posts that use real photos
            logger.info(f"   ✅ Final result: {len(generated_posts)} posts with REAL photos only (no fallbacks)")
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