from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import logging
import json
import os
from collections import Counter
import re
from motor.motor_asyncio import AsyncIOMotorClient
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Import authentication
from auth import get_current_active_user, User

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Analytics Router
analytics_router = APIRouter(prefix="/analytics", tags=["analytics"])

# Pydantic Models for Analytics
class PostMetrics(BaseModel):
    """Individual post performance metrics"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    post_id: str  # Reference to generated_post ID
    platform: str  # facebook, instagram, linkedin
    platform_post_id: str  # ID from social platform
    metrics: Dict[str, Any] = {}  # likes, comments, shares, reach, impressions, etc.
    collected_at: datetime = Field(default_factory=datetime.utcnow)
    analysis_period: str  # "7_days", "30_days", etc.

class ContentPattern(BaseModel):
    """Identified pattern in content performance"""
    pattern_type: str  # "hashtag", "keyword", "content_length", "post_type", "posting_time"
    pattern_value: str  # The actual pattern (e.g., "#restaurant", "promotion", "100-150_chars")
    performance_score: float  # 0.0 to 1.0
    frequency: int  # How often this pattern appears
    avg_engagement: float
    sample_posts: List[str] = []  # Post IDs that contain this pattern

class PerformanceInsights(BaseModel):
    """AI-generated insights from performance analysis"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    business_id: str
    analysis_period_start: datetime
    analysis_period_end: datetime
    total_posts_analyzed: int
    
    # Performance patterns identified
    top_hashtags: List[ContentPattern] = []
    top_keywords: List[ContentPattern] = []
    optimal_content_length: ContentPattern
    best_posting_times: List[ContentPattern] = []
    high_performing_topics: List[ContentPattern] = []
    
    # Overall performance metrics
    avg_engagement_rate: float = 0.0
    best_performing_post_id: Optional[str] = None
    worst_performing_post_id: Optional[str] = None
    
    # AI recommendations
    ai_recommendations: List[str] = []
    content_strategy_suggestions: List[str] = []
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    next_analysis_due: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=7))

class AnalyticsReport(BaseModel):
    """Comprehensive analytics report for user"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    business_id: str
    report_type: str  # "weekly", "monthly", "custom"
    period_start: datetime
    period_end: datetime
    
    # Summary statistics
    total_posts: int = 0
    total_engagement: int = 0
    avg_engagement_rate: float = 0.0
    reach_growth: float = 0.0
    follower_growth: float = 0.0
    
    # Performance insights reference
    insights_id: str
    
    # Key findings
    key_wins: List[str] = []
    areas_for_improvement: List[str] = []
    recommended_actions: List[str] = []
    
    generated_at: datetime = Field(default_factory=datetime.utcnow)

# Analytics Engine Functions
class AnalyticsEngine:
    """Core analytics processing engine"""
    
    def __init__(self):
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        if self.openai_api_key:
            # Initialize LlmChat with proper parameters when needed
            self.chat = None  # Will be initialized when needed
        else:
            self.chat = None
            logging.warning("OpenAI API key not found - AI insights will be limited")
    
    async def collect_post_metrics(self, business_id: str, days_back: int = 7) -> List[PostMetrics]:
        """Collect metrics for all posts from the specified period"""
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)
            
            # Get published posts from the period
            published_posts = await db.generated_posts.find({
                "business_id": business_id,
                "status": "posted",
                "published_at": {"$gte": start_date, "$lte": end_date}
            }).to_list(100)
            
            metrics_list = []
            
            for post in published_posts:
                # TODO: In real implementation, this would call Facebook/Instagram Graph API
                # For now, we'll simulate metrics based on post characteristics
                simulated_metrics = await self._simulate_post_metrics(post)
                
                post_metrics = PostMetrics(
                    post_id=post["id"],
                    platform=post.get("platform", "facebook"),
                    platform_post_id=post.get("platform_post_id", f"sim_{post['id'][:8]}"),
                    metrics=simulated_metrics,
                    analysis_period=f"{days_back}_days"
                )
                
                # Store metrics in database
                await db.post_metrics.insert_one(post_metrics.dict())
                metrics_list.append(post_metrics)
            
            logging.info(f"Collected metrics for {len(metrics_list)} posts")
            return metrics_list
            
        except Exception as e:
            logging.error(f"Error collecting post metrics: {e}")
            return []
    
    async def _simulate_post_metrics(self, post: Dict) -> Dict[str, Any]:
        """Simulate realistic post metrics based on content characteristics"""
        content = post.get("content", "")
        platform = post.get("platform", "facebook")
        
        # Base metrics simulation
        base_likes = 50 + len(content.split()) * 2  # More words = more engagement
        base_comments = max(5, len(re.findall(r'[?!]', content)) * 3)  # Questions/exclamations drive comments
        base_shares = max(2, len(re.findall(r'#\w+', content)))  # Hashtags encourage shares
        
        # Platform-specific adjustments
        if platform == "instagram":
            base_likes = int(base_likes * 1.5)  # Instagram typically has higher engagement
            base_comments = int(base_comments * 1.2)
        elif platform == "facebook":
            base_shares = int(base_shares * 1.8)  # Facebook shares more
        
        # Add some randomness for realism
        import random
        variation = random.uniform(0.7, 1.5)
        
        metrics = {
            "likes": int(base_likes * variation),
            "comments": int(base_comments * variation),
            "shares": int(base_shares * variation),
            "reach": int((base_likes + base_comments * 2) * 5 * variation),
            "impressions": int((base_likes + base_comments * 2) * 8 * variation),
            "engagement_rate": round(((base_likes + base_comments + base_shares) / max(100, base_likes * 5)) * 100, 2),
            "click_throughs": max(1, int(base_likes * 0.1 * variation)),
            "saves": max(0, int(base_likes * 0.05 * variation)) if platform == "instagram" else 0
        }
        
        return metrics

class PromptOptimizer:
    """Advanced prompt optimization system for continuous improvement"""
    
    def __init__(self):
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        if self.openai_api_key:
            # Initialize LlmChat with proper parameters when needed
            self.chat = None  # Will be initialized when needed
        else:
            self.chat = None
            logging.warning("OpenAI API key not found - Prompt optimization will be limited")
    
    async def analyze_prompt_performance(self, business_id: str, days_back: int = 30) -> Dict[str, Any]:
        """Analyze which prompts generate the best performing content"""
        try:
            logging.info(f"🔍 Analyzing prompt performance for business {business_id}")
            
            # Get posts with prompt metadata from the analysis period
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)
            
            posts_with_prompts = await db.generated_posts.find({
                "business_id": business_id,
                "created_at": {"$gte": start_date, "$lte": end_date},
                "generation_metadata.prompt_version": {"$exists": True}
            }).to_list(200)
            
            if not posts_with_prompts:
                logging.info("No posts with prompt metadata found")
                return {"has_data": False, "message": "No prompt performance data available"}
            
            # Get corresponding metrics for these posts
            post_ids = [post["id"] for post in posts_with_prompts]
            metrics_cursor = db.post_metrics.find({"post_id": {"$in": post_ids}})
            metrics_list = await metrics_cursor.to_list(200)
            
            # Create mapping of post_id to metrics
            metrics_map = {m["post_id"]: m["metrics"] for m in metrics_list}
            
            # Analyze prompt patterns and their performance
            prompt_performance = {}
            
            for post in posts_with_prompts:
                post_id = post["id"]
                prompt_data = post.get("generation_metadata", {})
                prompt_version = prompt_data.get("prompt_version", "unknown")
                prompt_type = prompt_data.get("prompt_type", "standard")
                prompt_elements = prompt_data.get("prompt_elements", {})
                
                metrics = metrics_map.get(post_id)
                if not metrics:
                    continue
                
                engagement_rate = metrics.get("engagement_rate", 0)
                total_engagement = (metrics.get("likes", 0) + 
                                  metrics.get("comments", 0) + 
                                  metrics.get("shares", 0))
                
                # Track performance by prompt version
                if prompt_version not in prompt_performance:
                    prompt_performance[prompt_version] = {
                        "total_posts": 0,
                        "total_engagement": 0,
                        "engagement_rates": [],
                        "prompt_elements": prompt_elements,
                        "prompt_type": prompt_type,
                        "sample_posts": []
                    }
                
                prompt_performance[prompt_version]["total_posts"] += 1
                prompt_performance[prompt_version]["total_engagement"] += total_engagement
                prompt_performance[prompt_version]["engagement_rates"].append(engagement_rate)
                prompt_performance[prompt_version]["sample_posts"].append(post_id)
            
            # Calculate performance scores and rankings
            performance_ranking = []
            for prompt_version, data in prompt_performance.items():
                avg_engagement_rate = sum(data["engagement_rates"]) / len(data["engagement_rates"])
                avg_total_engagement = data["total_engagement"] / data["total_posts"]
                
                performance_score = (avg_engagement_rate * 0.7) + (avg_total_engagement / 100 * 0.3)
                
                performance_ranking.append({
                    "prompt_version": prompt_version,
                    "prompt_type": data["prompt_type"],
                    "prompt_elements": data["prompt_elements"],
                    "total_posts": data["total_posts"],
                    "avg_engagement_rate": avg_engagement_rate,
                    "avg_total_engagement": avg_total_engagement,
                    "performance_score": performance_score,
                    "sample_posts": data["sample_posts"][:3]
                })
            
            # Sort by performance score
            performance_ranking.sort(key=lambda x: x["performance_score"], reverse=True)
            
            # Generate optimization insights
            optimization_insights = await self._generate_prompt_optimization_insights(performance_ranking)
            
            analysis_result = {
                "has_data": True,
                "analysis_period_days": days_back,
                "total_posts_analyzed": len(posts_with_prompts),
                "prompt_versions_tested": len(prompt_performance),
                "performance_ranking": performance_ranking,
                "optimization_insights": optimization_insights,
                "best_performing_prompt": performance_ranking[0] if performance_ranking else None,
                "worst_performing_prompt": performance_ranking[-1] if performance_ranking else None,
                "analyzed_at": datetime.utcnow()
            }
            
            # Store analysis results
            await db.prompt_performance_analysis.insert_one({
                "id": str(uuid.uuid4()),
                "business_id": business_id,
                "analysis_data": analysis_result,
                "created_at": datetime.utcnow()
            })
            
            logging.info(f"✅ Prompt performance analysis complete: {len(performance_ranking)} prompt versions analyzed")
            return analysis_result
            
        except Exception as e:
            logging.error(f"Error analyzing prompt performance: {e}")
            return {"has_data": False, "error": str(e)}
    
    async def _generate_prompt_optimization_insights(self, performance_ranking: List[Dict]) -> List[str]:
        """Generate AI insights for prompt optimization"""
        if not self.chat or not performance_ranking:
            return [
                "Continuez à tester différentes approches de contenu",
                "Variez la structure de vos prompts pour identifier les patterns efficaces",
                "Surveillez l'engagement pour adapter votre stratégie de contenu"
            ]
        
        try:
            # Prepare data for AI analysis
            best_prompts = performance_ranking[:3]
            worst_prompts = performance_ranking[-2:] if len(performance_ranking) > 2 else []
            
            analysis_summary = "PROMPTS PERFORMANTS:\n"
            for i, prompt in enumerate(best_prompts, 1):
                analysis_summary += f"{i}. Version {prompt['prompt_version']} - Engagement: {prompt['avg_engagement_rate']:.2f}% - Elements: {prompt['prompt_elements']}\n"
            
            if worst_prompts:
                analysis_summary += "\nPROMPTS MOINS PERFORMANTS:\n"
                for i, prompt in enumerate(worst_prompts, 1):
                    analysis_summary += f"{i}. Version {prompt['prompt_version']} - Engagement: {prompt['avg_engagement_rate']:.2f}% - Elements: {prompt['prompt_elements']}\n"
            
            prompt = f"""
            Analysez ces performances de prompts de génération de contenu et donnez 5 insights d'optimisation concrets :
            
            {analysis_summary}
            
            Identifiez les patterns qui fonctionnent le mieux et recommandez des améliorations spécifiques pour les futurs prompts.
            
            Répondez avec un JSON : {{"insights": ["insight 1", "insight 2", ...]}}
            """
            
            # Initialize chat when needed
            if not self.chat and self.openai_api_key:
                self.chat = LlmChat(
                    api_key=self.openai_api_key,
                    session_id=f"prompt_insights_{uuid.uuid4()}",
                    system_message="You are an AI optimization expert analyzing prompt performance data."
                )
            
            response = await self.chat.send_message(UserMessage(content=prompt))
            
            try:
                data = json.loads(response.content)
                return data.get("insights", [])[:5]
            except json.JSONDecodeError:
                # Fallback parsing
                lines = response.content.split('\n')
                insights = [line.strip('- ') for line in lines if line.strip().startswith('-')]
                return insights[:5] if insights else [
                    "Optimisez les prompts basés sur les éléments les plus performants",
                    "Testez des variations de structure pour améliorer l'engagement",
                    "Adaptez le ton selon les performances observées"
                ]
                
        except Exception as e:
            logging.error(f"Error generating prompt insights: {e}")
            return [
                "Analysez les patterns des prompts les plus performants",
                "Testez différentes structures de prompts",
                "Adaptez la longueur et le ton basés sur les résultats"
            ]
    
    async def generate_optimized_prompt(self, business_profile: Dict, performance_data: Dict, prompt_type: str = "social_post") -> Dict[str, Any]:
        """Generate an optimized prompt based on performance insights"""
        try:
            logging.info(f"🎯 Generating optimized prompt for {prompt_type}")
            
            # Get the latest prompt performance analysis
            latest_analysis = await db.prompt_performance_analysis.find_one(
                {"business_id": business_profile.get("id")},
                sort=[("created_at", -1)]
            )
            
            # Extract optimization insights
            best_elements = {}
            optimization_insights = []
            
            if latest_analysis and latest_analysis.get("analysis_data", {}).get("has_data"):
                analysis_data = latest_analysis["analysis_data"]
                best_prompt = analysis_data.get("best_performing_prompt", {})
                optimization_insights = analysis_data.get("optimization_insights", [])
                
                if best_prompt:
                    best_elements = best_prompt.get("prompt_elements", {})
                    logging.info(f"📊 Using insights from best performing prompt (score: {best_prompt.get('performance_score', 0):.2f})")
            
            # Combine performance data with prompt optimization insights
            combined_insights = performance_data.get("ai_recommendations", []) + optimization_insights
            
            # Generate adaptive prompt components
            prompt_components = await self._generate_adaptive_prompt_components(
                business_profile, 
                performance_data, 
                best_elements, 
                combined_insights
            )
            
            # Create version identifier
            prompt_version = f"v{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            optimized_prompt = {
                "prompt_version": prompt_version,
                "prompt_type": prompt_type,
                "business_id": business_profile.get("id"),
                "created_at": datetime.utcnow(),
                
                # Prompt components
                "system_message": prompt_components["system_message"],
                "user_prompt_template": prompt_components["user_prompt_template"],
                "optimization_focus": prompt_components["optimization_focus"],
                
                # Metadata for tracking
                "prompt_elements": {
                    "tone_adaptation": prompt_components.get("tone_adaptation", "standard"),
                    "length_optimization": prompt_components.get("length_optimization", "medium"),
                    "hashtag_strategy": prompt_components.get("hashtag_strategy", "balanced"),
                    "cta_style": prompt_components.get("cta_style", "subtle"),
                    "personalization_level": prompt_components.get("personalization_level", "medium")
                },
                
                # Performance baseline
                "expected_improvement": prompt_components.get("expected_improvement", 0),
                "based_on_insights": len(optimization_insights) > 0,
                "insights_applied": combined_insights[:3],
                
                # A/B testing info
                "is_test_variant": False,
                "parent_version": None
            }
            
            # Store optimized prompt
            await db.optimized_prompts.insert_one(optimized_prompt)
            
            logging.info(f"✅ Generated optimized prompt {prompt_version}")
            return optimized_prompt
            
        except Exception as e:
            logging.error(f"Error generating optimized prompt: {e}")
            # Return fallback prompt
            return await self._get_fallback_prompt(business_profile, prompt_type)
    
    async def _generate_adaptive_prompt_components(self, business_profile: Dict, performance_data: Dict, best_elements: Dict, insights: List[str]) -> Dict[str, Any]:
        """Generate adaptive prompt components based on performance insights"""
        
        # Extract key information
        business_name = business_profile.get("business_name", "")
        business_type = business_profile.get("business_type", "")
        target_audience = business_profile.get("target_audience", "")
        brand_tone = business_profile.get("brand_tone", "professionnel")
        
        # Performance-based optimizations
        top_hashtags = performance_data.get("recommended_hashtags", [])[:5]
        high_performing_keywords = performance_data.get("high_performing_keywords", [])[:5]
        optimal_length = performance_data.get("optimal_content_length", "100-150")
        best_topics = performance_data.get("high_performing_topics", [])[:3]
        
        # Adaptive tone based on performance
        tone_adaptation = "standard"
        if performance_data.get("avg_engagement_rate", 0) > 7.0:
            tone_adaptation = "amplify_current"  # Keep current approach
        elif performance_data.get("avg_engagement_rate", 0) < 3.0:
            tone_adaptation = "more_engaging"  # Need more engagement
        else:
            tone_adaptation = "optimize_balance"  # Balance engagement and professionalism
        
        # Length optimization based on insights
        length_optimization = "medium"
        if "court" in " ".join(insights).lower() or "150" in optimal_length:
            length_optimization = "concise"
        elif "long" in " ".join(insights).lower() or "200" in optimal_length:
            length_optimization = "detailed"
        
        # Build adaptive system message
        performance_guidance = ""
        if performance_data.get("has_insights"):
            hashtags_text = ', '.join(top_hashtags) if top_hashtags else "En cours d'analyse"
            keywords_text = ', '.join(high_performing_keywords) if high_performing_keywords else "En cours d'analyse"
            topics_text = ', '.join(best_topics) if best_topics else "En cours d'analyse"
            insights_text = '; '.join(insights[:2]) if insights else "Collecte en cours"
            
            performance_guidance = f"""
OPTIMISATIONS BASÉES SUR PERFORMANCE RÉELLE :
- Hashtags performants détectés : {hashtags_text}
- Mots-clés engageants : {keywords_text}
- Longueur optimale identifiée : {optimal_length} caractères
- Sujets qui engagent : {topics_text}
- Insights clés : {insights_text}

DIRECTIVE D'OPTIMISATION : Intègre ces éléments performants naturellement dans le contenu généré !
"""
        
        # Adaptive tone instructions
        tone_instructions = {
            "amplify_current": f"EXCELLENT ENGAGEMENT DÉTECTÉ ! Continue exactement dans ce style {brand_tone} qui fonctionne parfaitement.",
            "more_engaging": f"ENGAGEMENT À AMÉLIORER : Adapte le ton {brand_tone} pour être plus captivant et interactif.",
            "optimize_balance": f"BON ENGAGEMENT : Optimise le ton {brand_tone} pour équilibrer professionnalisme et engagement."
        }
        
        hashtags_rule = "Privilégie " + ", ".join(top_hashtags[:3]) if top_hashtags else "Utilise des hashtags pertinents sectoriels"
        keywords_rule = "Intègre naturellement : " + ", ".join(high_performing_keywords[:3]) if high_performing_keywords else "Utilise un vocabulaire engageant"
        length_rule = "Vise " + optimal_length + " caractères (optimisé selon tes performances)" if optimal_length else "100-150 caractères"
        topics_rule = "Concentre-toi sur : " + ", ".join(best_topics[:2]) if best_topics else "Varie les sujets pour tester l'engagement"
        
        system_message = f"""Tu génères du contenu optimisé pour {business_name} - {business_type}.

PROFIL CIBLE ADAPTATIF :
- Entreprise : {business_name}
- Secteur : {business_type}  
- Audience : {target_audience}
- Ton de marque : {brand_tone}

{performance_guidance}

ADAPTATION INTELLIGENTE :
{tone_instructions.get(tone_adaptation, tone_instructions["optimize_balance"])}

RÈGLES D'OPTIMISATION ADAPTATIVE :
1. HASHTAGS : {hashtags_rule}
2. MOTS-CLÉS : {keywords_rule}
3. LONGUEUR : {length_rule}
4. SUJETS : {topics_rule}

AMÉLIORATION CONTINUE :
- Ce prompt s'adapte automatiquement selon tes performances réelles
- Les recommandations évoluent avec tes résultats d'engagement
- L'objectif : contenu de plus en plus performant à chaque génération

Style authentique obligatoire : Ton naturel, pas de marketing artificiel."""
        
        # Create adaptive user prompt template
        insights_text = '; '.join(insights[:2]) if insights else 'Teste différentes approches'
        hashtags_text = "Utilise ces hashtags performants : " + " ".join(top_hashtags[:3]) if top_hashtags else "Choisis des hashtags testables"
        topics_text = "Focus sujets engageants : " + ", ".join(best_topics[:2]) if best_topics else "Varie pour identifier ce qui marche"
        
        user_prompt_template = f"""Génère du contenu optimisé selon les performances analysées.

CONSIGNES ADAPTATIVES :
- Applique les insights de performance : {insights_text}
- {hashtags_text}
- Longueur cible : {optimal_length} caractères
- {topics_text}

Génère [X] posts optimisés qui s'améliorent basés sur les données réelles.

JSON format attendu : {{"posts": [{{"content": "...", "hashtags": [...], "optimization_applied": "..."}}, ...]}}"""
        
        return {
            "system_message": system_message,
            "user_prompt_template": user_prompt_template,
            "optimization_focus": {
                "tone_adaptation": tone_adaptation,
                "length_optimization": length_optimization,
                "hashtag_strategy": "performance_based" if top_hashtags else "experimental",
                "keyword_integration": "data_driven" if high_performing_keywords else "exploratory",
                "topic_selection": "insight_based" if best_topics else "diversified"
            },
            "tone_adaptation": tone_adaptation,
            "length_optimization": length_optimization,
            "hashtag_strategy": "performance_based" if top_hashtags else "experimental",
            "cta_style": "tested" if insights else "experimental",
            "personalization_level": "high" if performance_data.get("has_insights") else "medium",
            "expected_improvement": 15 if performance_data.get("has_insights") else 5
        }
    
    async def _get_fallback_prompt(self, business_profile: Dict, prompt_type: str) -> Dict[str, Any]:
        """Generate fallback prompt when optimization data is not available"""
        prompt_version = f"fallback_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "prompt_version": prompt_version,
            "prompt_type": prompt_type,
            "business_id": business_profile.get("id"),
            "created_at": datetime.utcnow(),
            "system_message": f"Tu génères du contenu engageant pour {business_profile.get('business_name', '')} - {business_profile.get('business_type', '')}. Ton naturel et authentique.",
            "user_prompt_template": "Génère du contenu varié pour tester l'engagement et commencer à collecter des données de performance.",
            "optimization_focus": {"type": "baseline", "goal": "data_collection"},
            "prompt_elements": {"tone_adaptation": "standard", "length_optimization": "medium"},
            "based_on_insights": False,
            "is_test_variant": False
        }

# Analytics Engine Functions (moved from PromptOptimizer)
    async def analyze_content_patterns(self, business_id: str, metrics_list: List[PostMetrics]) -> PerformanceInsights:
        """Analyze content patterns and generate insights"""
        try:
            # Get the corresponding posts for analysis
            post_ids = [m.post_id for m in metrics_list]
            posts = await db.generated_posts.find({
                "id": {"$in": post_ids},
                "business_id": business_id
            }).to_list(100)
            
            # Create post-metric mapping
            post_metric_map = {m.post_id: m for m in metrics_list}
            
            # Analyze hashtags
            hashtag_performance = self._analyze_hashtags(posts, post_metric_map)
            
            # Analyze keywords
            keyword_performance = self._analyze_keywords(posts, post_metric_map)
            
            # Analyze content length
            length_performance = self._analyze_content_length(posts, post_metric_map)
            
            # Analyze posting times (if available)
            time_performance = self._analyze_posting_times(posts, post_metric_map)
            
            # Analyze topics
            topic_performance = self._analyze_topics(posts, post_metric_map)
            
            # Calculate overall metrics
            total_posts = len(posts)
            avg_engagement = sum(m.metrics.get("engagement_rate", 0) for m in metrics_list) / max(1, len(metrics_list))
            
            # Find best and worst performing posts
            best_post = max(metrics_list, key=lambda m: m.metrics.get("engagement_rate", 0)) if metrics_list else None
            worst_post = min(metrics_list, key=lambda m: m.metrics.get("engagement_rate", 0)) if metrics_list else None
            
            # Generate AI recommendations
            ai_recommendations = await self._generate_ai_recommendations(posts, metrics_list)
            
            # Create insights object
            period_start = datetime.utcnow() - timedelta(days=7)  # TODO: Make this dynamic
            period_end = datetime.utcnow()
            
            insights = PerformanceInsights(
                user_id=posts[0]["user_id"] if posts else "",
                business_id=business_id,
                analysis_period_start=period_start,
                analysis_period_end=period_end,
                total_posts_analyzed=total_posts,
                top_hashtags=hashtag_performance[:5],
                top_keywords=keyword_performance[:5],
                optimal_content_length=length_performance,
                best_posting_times=time_performance[:3],
                high_performing_topics=topic_performance[:5],
                avg_engagement_rate=avg_engagement,
                best_performing_post_id=best_post.post_id if best_post else None,
                worst_performing_post_id=worst_post.post_id if worst_post else None,
                ai_recommendations=ai_recommendations,
                content_strategy_suggestions=await self._generate_content_strategy(hashtag_performance, keyword_performance, topic_performance)
            )
            
            # Store insights in database
            await db.performance_insights.insert_one(insights.dict())
            
            logging.info(f"Generated insights for {total_posts} posts with {avg_engagement:.2f}% avg engagement")
            return insights
            
        except Exception as e:
            logging.error(f"Error analyzing content patterns: {e}")
            # Return empty insights object
            return PerformanceInsights(
                user_id="",
                business_id=business_id,
                analysis_period_start=datetime.utcnow() - timedelta(days=7),
                analysis_period_end=datetime.utcnow(),
                total_posts_analyzed=0,
                optimal_content_length=ContentPattern(
                    pattern_type="content_length",
                    pattern_value="100-150_chars",
                    performance_score=0.5,
                    frequency=0,
                    avg_engagement=0.0
                )
            )
    
    def _analyze_hashtags(self, posts: List[Dict], post_metric_map: Dict) -> List[ContentPattern]:
        """Analyze hashtag performance patterns"""
        hashtag_stats = {}
        
        for post in posts:
            content = post.get("content", "")
            hashtags = re.findall(r'#\w+', content.lower())
            metrics = post_metric_map.get(post["id"])
            
            if metrics and hashtags:
                engagement_rate = metrics.metrics.get("engagement_rate", 0)
                
                for hashtag in hashtags:
                    if hashtag not in hashtag_stats:
                        hashtag_stats[hashtag] = {"total_engagement": 0, "count": 0, "posts": []}
                    
                    hashtag_stats[hashtag]["total_engagement"] += engagement_rate
                    hashtag_stats[hashtag]["count"] += 1
                    hashtag_stats[hashtag]["posts"].append(post["id"])
        
        # Convert to ContentPattern objects
        patterns = []
        for hashtag, stats in hashtag_stats.items():
            if stats["count"] >= 2:  # Only include hashtags used at least twice
                avg_engagement = stats["total_engagement"] / stats["count"]
                pattern = ContentPattern(
                    pattern_type="hashtag",
                    pattern_value=hashtag,
                    performance_score=min(1.0, avg_engagement / 10.0),  # Normalize to 0-1
                    frequency=stats["count"],
                    avg_engagement=avg_engagement,
                    sample_posts=stats["posts"][:3]
                )
                patterns.append(pattern)
        
        # Sort by performance score
        return sorted(patterns, key=lambda p: p.performance_score, reverse=True)
    
    def _analyze_keywords(self, posts: List[Dict], post_metric_map: Dict) -> List[ContentPattern]:
        """Analyze keyword performance patterns"""
        # Common business keywords to track
        business_keywords = [
            "promotion", "offre", "nouveau", "spécial", "gratuit", "réduction",
            "qualité", "service", "client", "équipe", "innovation", "excellence",
            "découvrez", "profitez", "exclusif", "limité", "aujourd'hui"
        ]
        
        keyword_stats = {}
        
        for post in posts:
            content = post.get("content", "").lower()
            metrics = post_metric_map.get(post["id"])
            
            if metrics:
                engagement_rate = metrics.metrics.get("engagement_rate", 0)
                
                for keyword in business_keywords:
                    if keyword in content:
                        if keyword not in keyword_stats:
                            keyword_stats[keyword] = {"total_engagement": 0, "count": 0, "posts": []}
                        
                        keyword_stats[keyword]["total_engagement"] += engagement_rate
                        keyword_stats[keyword]["count"] += 1
                        keyword_stats[keyword]["posts"].append(post["id"])
        
        # Convert to ContentPattern objects
        patterns = []
        for keyword, stats in keyword_stats.items():
            if stats["count"] >= 1:
                avg_engagement = stats["total_engagement"] / stats["count"]
                pattern = ContentPattern(
                    pattern_type="keyword",
                    pattern_value=keyword,
                    performance_score=min(1.0, avg_engagement / 8.0),
                    frequency=stats["count"],
                    avg_engagement=avg_engagement,
                    sample_posts=stats["posts"][:3]
                )
                patterns.append(pattern)
        
        return sorted(patterns, key=lambda p: p.performance_score, reverse=True)
    
    def _analyze_content_length(self, posts: List[Dict], post_metric_map: Dict) -> ContentPattern:
        """Analyze optimal content length"""
        length_buckets = {
            "0-50": {"total_engagement": 0, "count": 0},
            "51-100": {"total_engagement": 0, "count": 0},
            "101-150": {"total_engagement": 0, "count": 0},
            "151-200": {"total_engagement": 0, "count": 0},
            "200+": {"total_engagement": 0, "count": 0}
        }
        
        for post in posts:
            content = post.get("content", "")
            length = len(content)
            metrics = post_metric_map.get(post["id"])
            
            if metrics:
                engagement_rate = metrics.metrics.get("engagement_rate", 0)
                
                if length <= 50:
                    bucket = "0-50"
                elif length <= 100:
                    bucket = "51-100"
                elif length <= 150:
                    bucket = "101-150"
                elif length <= 200:
                    bucket = "151-200"
                else:
                    bucket = "200+"
                
                length_buckets[bucket]["total_engagement"] += engagement_rate
                length_buckets[bucket]["count"] += 1
        
        # Find the best performing length bucket
        best_bucket = "101-150"  # Default
        best_performance = 0
        
        for bucket, stats in length_buckets.items():
            if stats["count"] > 0:
                avg_engagement = stats["total_engagement"] / stats["count"]
                if avg_engagement > best_performance:
                    best_performance = avg_engagement
                    best_bucket = bucket
        
        return ContentPattern(
            pattern_type="content_length",
            pattern_value=f"{best_bucket}_chars",
            performance_score=min(1.0, best_performance / 10.0),
            frequency=length_buckets[best_bucket]["count"],
            avg_engagement=best_performance
        )
    
    def _analyze_posting_times(self, posts: List[Dict], post_metric_map: Dict) -> List[ContentPattern]:
        """Analyze optimal posting times"""
        # For now, return some default optimal times
        # In real implementation, this would analyze actual posting times
        default_times = [
            ContentPattern(
                pattern_type="posting_time",
                pattern_value="9h-11h",
                performance_score=0.8,
                frequency=3,
                avg_engagement=7.5
            ),
            ContentPattern(
                pattern_type="posting_time",
                pattern_value="18h-20h",
                performance_score=0.9,
                frequency=5,
                avg_engagement=8.2
            ),
            ContentPattern(
                pattern_type="posting_time",
                pattern_value="12h-14h",
                performance_score=0.7,
                frequency=2,
                avg_engagement=6.8
            )
        ]
        
        return sorted(default_times, key=lambda p: p.performance_score, reverse=True)
    
    def _analyze_topics(self, posts: List[Dict], post_metric_map: Dict) -> List[ContentPattern]:
        """Analyze high-performing topics"""
        # Simple topic detection based on keywords
        topic_keywords = {
            "promotions": ["promotion", "offre", "réduction", "spécial", "gratuit"],
            "nouveautés": ["nouveau", "nouveauté", "innovation", "lancement"],
            "qualité": ["qualité", "excellence", "premium", "artisanal"],
            "service": ["service", "équipe", "accueil", "conseil"],
            "événements": ["événement", "soirée", "festival", "célébration"]
        }
        
        topic_stats = {}
        
        for post in posts:
            content = post.get("content", "").lower()
            metrics = post_metric_map.get(post["id"])
            
            if metrics:
                engagement_rate = metrics.metrics.get("engagement_rate", 0)
                
                for topic, keywords in topic_keywords.items():
                    topic_score = sum(1 for keyword in keywords if keyword in content)
                    
                    if topic_score > 0:
                        if topic not in topic_stats:
                            topic_stats[topic] = {"total_engagement": 0, "count": 0, "posts": []}
                        
                        topic_stats[topic]["total_engagement"] += engagement_rate * topic_score
                        topic_stats[topic]["count"] += 1
                        topic_stats[topic]["posts"].append(post["id"])
        
        # Convert to ContentPattern objects
        patterns = []
        for topic, stats in topic_stats.items():
            if stats["count"] >= 1:
                avg_engagement = stats["total_engagement"] / stats["count"]
                pattern = ContentPattern(
                    pattern_type="topic",
                    pattern_value=topic,
                    performance_score=min(1.0, avg_engagement / 8.0),
                    frequency=stats["count"],
                    avg_engagement=avg_engagement,
                    sample_posts=stats["posts"][:3]
                )
                patterns.append(pattern)
        
        return sorted(patterns, key=lambda p: p.performance_score, reverse=True)
    
    async def _generate_ai_recommendations(self, posts: List[Dict], metrics_list: List[PostMetrics]) -> List[str]:
        """Generate AI-powered recommendations"""
        if not self.openai_api_key:
            # Fallback recommendations when OpenAI is not available
            return [
                "Continuez à utiliser les hashtags qui génèrent le plus d'engagement",
                "Variez les types de contenu pour maintenir l'intérêt de votre audience",
                "Publiez régulièrement pour maintenir la visibilité",
                "Engagez avec votre communauté en répondant aux commentaires"
            ]
        
        try:
            # Initialize LlmChat when needed
            if not self.chat:
                self.chat = LlmChat(
                    api_key=self.openai_api_key,
                    session_id=f"analytics_{uuid.uuid4()}",
                    system_message="Tu es un expert en marketing digital et analytics des réseaux sociaux."
                )
            
            # Prepare data for AI analysis
            performance_summary = []
            for post in posts[:5]:  # Analyze top 5 posts
                metrics = next((m for m in metrics_list if m.post_id == post["id"]), None)
                if metrics:
                    summary = f"Post: '{post.get('content', '')[:100]}...' - Engagement: {metrics.metrics.get('engagement_rate', 0)}%"
                    performance_summary.append(summary)
            
            prompt = f"""
            Analysez ces performances de posts sur les réseaux sociaux et donnez 4 recommandations concrètes et actionables :
            
            PERFORMANCES:
            {chr(10).join(performance_summary)}
            
            Donnez des recommandations spécifiques pour améliorer l'engagement et la portée.
            Répondez avec une liste JSON : {{"recommendations": ["recommandation 1", "recommandation 2", ...]}}
            """
            
            # Initialize chat when needed
            if not self.chat and self.openai_api_key:
                self.chat = LlmChat(
                    api_key=self.openai_api_key,
                    session_id=f"ai_recommendations_{uuid.uuid4()}",
                    system_message="You are a social media analytics expert providing actionable recommendations."
                )
            
            response = await self.chat.send_message(UserMessage(content=prompt))
            
            try:
                data = json.loads(response.content)
                return data.get("recommendations", [])[:4]
            except json.JSONDecodeError:
                # Fallback to parsing text response
                lines = response.content.split('\n')
                recommendations = [line.strip('- ') for line in lines if line.strip().startswith('-')]
                return recommendations[:4] if recommendations else [
                    "Optimisez vos hashtags en vous basant sur ceux qui performent le mieux",
                    "Adaptez la longueur de vos posts selon votre audience",
                    "Publiez aux heures où votre audience est la plus active",
                    "Créez du contenu qui invite à l'interaction (questions, sondages)"
                ]
                
        except Exception as e:
            logging.error(f"Error generating AI recommendations: {e}")
            return [
                "Analysez vos posts les plus performants pour identifier les patterns",
                "Testez différents formats de contenu (images, vidéos, carrousels)",
                "Utilisez des call-to-action clairs dans vos posts",
                "Maintenez une cohérence dans votre style et votre ton"
            ]
    
    async def _generate_content_strategy(self, hashtags: List[ContentPattern], keywords: List[ContentPattern], topics: List[ContentPattern]) -> List[str]:
        """Generate content strategy suggestions based on patterns"""
        suggestions = []
        
        # Hashtag strategy
        if hashtags:
            top_hashtag = hashtags[0]
            suggestions.append(f"Intégrez plus souvent le hashtag '{top_hashtag.pattern_value}' qui génère {top_hashtag.avg_engagement:.1f}% d'engagement en moyenne")
        
        # Keyword strategy
        if keywords:
            top_keyword = keywords[0]
            suggestions.append(f"Le mot-clé '{top_keyword.pattern_value}' performe bien - utilisez-le plus souvent dans vos posts")
        
        # Topic strategy
        if topics:
            top_topic = topics[0]
            suggestions.append(f"Les contenus sur '{top_topic.pattern_value}' engagent bien votre audience - créez plus de contenu sur ce sujet")
        
        # General strategy
        suggestions.append("Maintenez un équilibre entre contenu promotionnel et contenu informatif/divertissant")
        
        return suggestions[:4]

# Initialize Analytics Engine
analytics_engine = AnalyticsEngine()

# Initialize Prompt Optimizer
prompt_optimizer = PromptOptimizer()

# API Endpoints
@analytics_router.post("/analyze")
async def trigger_performance_analysis(
    days_back: int = 7,
    current_user: User = Depends(get_current_active_user)
):
    """Manually trigger performance analysis"""
    try:
        # Get user's business profile
        business_profile = await db.business_profiles.find_one({"user_id": current_user.id})
        if not business_profile:
            raise HTTPException(status_code=404, detail="Business profile not found")
        
        # Collect metrics
        metrics = await analytics_engine.collect_post_metrics(business_profile["id"], days_back)
        
        if not metrics:
            return {
                "message": f"Aucun post trouvé pour les {days_back} derniers jours",
                "metrics_collected": 0,
                "insights_generated": False
            }
        
        # Analyze patterns and generate insights  
        insights = await analytics_engine.analyze_content_patterns(business_profile["id"], metrics)
        
        return {
            "message": "Analyse terminée avec succès",
            "metrics_collected": len(metrics),
            "insights_generated": True,
            "insights_id": insights.id,
            "avg_engagement_rate": insights.avg_engagement_rate,
            "top_recommendations": insights.ai_recommendations
        }
        
    except Exception as e:
        logging.error(f"Error in performance analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse: {str(e)}")

@analytics_router.get("/insights")
async def get_latest_insights(
    current_user: User = Depends(get_current_active_user)
):
    """Get the latest performance insights"""
    try:
        # Get user's business profile
        business_profile = await db.business_profiles.find_one({"user_id": current_user.id})
        if not business_profile:
            raise HTTPException(status_code=404, detail="Business profile not found")
        
        # Get latest insights
        insights = await db.performance_insights.find_one(
            {"business_id": business_profile["id"]},
            sort=[("created_at", -1)]
        )
        
        if not insights:
            return {
                "message": "Aucune analyse disponible",
                "insights": None,
                "recommendation": "Lancez une première analyse pour obtenir des insights sur vos performances"
            }
        
        return {
            "insights": insights,
            "last_analysis": insights["created_at"],
            "next_analysis_due": insights.get("next_analysis_due"),
            "posts_analyzed": insights["total_posts_analyzed"]
        }
        
    except Exception as e:
        logging.error(f"Error getting insights: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des insights: {str(e)}")

@analytics_router.get("/report")
async def generate_analytics_report(
    report_type: str = "weekly",
    current_user: User = Depends(get_current_active_user)
):
    """Generate a comprehensive analytics report"""
    try:
        # Get user's business profile
        business_profile = await db.business_profiles.find_one({"user_id": current_user.id})
        if not business_profile:
            raise HTTPException(status_code=404, detail="Business profile not found")
        
        # Get latest insights
        insights = await db.performance_insights.find_one(
            {"business_id": business_profile["id"]},
            sort=[("created_at", -1)]
        )
        
        if not insights:
            raise HTTPException(status_code=404, detail="Aucune donnée d'analyse disponible")
        
        # Calculate report period
        if report_type == "weekly":
            period_days = 7
        elif report_type == "monthly":
            period_days = 30
        else:
            period_days = 7
        
        period_start = datetime.utcnow() - timedelta(days=period_days)
        period_end = datetime.utcnow()
        
        # Get metrics for the period
        metrics = await db.post_metrics.find({
            "collected_at": {"$gte": period_start, "$lte": period_end}
        }).to_list(100)
        
        # Calculate summary statistics
        total_posts = len(metrics)
        total_engagement = sum(m.get("metrics", {}).get("likes", 0) + 
                             m.get("metrics", {}).get("comments", 0) + 
                             m.get("metrics", {}).get("shares", 0) for m in metrics)
        avg_engagement_rate = insights.get("avg_engagement_rate", 0)
        
        # Create report
        report = AnalyticsReport(
            user_id=current_user.id,
            business_id=business_profile["id"],
            report_type=report_type,
            period_start=period_start,
            period_end=period_end,
            total_posts=total_posts,
            total_engagement=total_engagement,
            avg_engagement_rate=avg_engagement_rate,
            reach_growth=5.2,  # TODO: Calculate real growth
            follower_growth=2.8,  # TODO: Calculate real growth
            insights_id=insights["id"],
            key_wins=[
                f"Taux d'engagement moyen de {avg_engagement_rate:.1f}%",
                f"{total_posts} posts publiés avec succès",
                "Amélioration de la stratégie hashtags"
            ],
            areas_for_improvement=[
                "Diversifier les types de contenu",
                "Optimiser les heures de publication",
                "Augmenter la fréquence d'interaction avec la communauté"
            ],
            recommended_actions=insights.get("ai_recommendations", [])
        )
        
        # Store report
        await db.analytics_reports.insert_one(report.dict())
        
        return {
            "report": report,
            "summary": {
                "period": f"{report_type.title()} ({period_start.strftime('%d/%m')} - {period_end.strftime('%d/%m')})",
                "performance": "Good" if avg_engagement_rate > 5.0 else "Needs Improvement",
                "trend": "Growing" if avg_engagement_rate > 3.0 else "Stable"
            }
        }
        
    except Exception as e:
        logging.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération du rapport: {str(e)}")

@analytics_router.get("/metrics/{post_id}")
async def get_post_metrics(
    post_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get detailed metrics for a specific post"""
    try:
        # Verify post belongs to user
        post = await db.generated_posts.find_one({
            "id": post_id,
            "user_id": current_user.id
        })
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Get metrics
        metrics = await db.post_metrics.find_one({"post_id": post_id})
        
        if not metrics:
            return {
                "post_id": post_id,
                "metrics": None,
                "message": "Aucune métrique disponible pour ce post"
            }
        
        return {
            "post": {
                "id": post["id"],
                "content": post.get("content", ""),
                "platform": post.get("platform", ""),
                "published_at": post.get("published_at")
            },
            "metrics": metrics["metrics"],
            "collected_at": metrics["collected_at"],
            "performance_rating": "High" if metrics["metrics"].get("engagement_rate", 0) > 5.0 else "Medium" if metrics["metrics"].get("engagement_rate", 0) > 2.0 else "Low"
        }
        
    except Exception as e:
        logging.error(f"Error getting post metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des métriques: {str(e)}")

# PHASE 3: PROMPT OPTIMIZATION ENDPOINTS

@analytics_router.post("/prompts/analyze")
async def analyze_prompt_performance(
    days_back: int = 30,
    current_user: User = Depends(get_current_active_user)
):
    """Analyze prompt performance for optimization"""
    try:
        # Get user's business profile
        business_profile = await db.business_profiles.find_one({"user_id": current_user.id})
        if not business_profile:
            raise HTTPException(status_code=404, detail="Business profile not found")
        
        # Analyze prompt performance
        analysis_result = await prompt_optimizer.analyze_prompt_performance(
            business_profile["id"], 
            days_back
        )
        
        return {
            "message": "Analyse des prompts terminée",
            "analysis": analysis_result,
            "recommendations_count": len(analysis_result.get("optimization_insights", [])),
            "prompt_versions_analyzed": analysis_result.get("prompt_versions_tested", 0)
        }
        
    except Exception as e:
        logging.error(f"Error in prompt analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse des prompts: {str(e)}")

@analytics_router.post("/prompts/optimize")
async def generate_optimized_prompt(
    prompt_type: str = "social_post",
    current_user: User = Depends(get_current_active_user)
):
    """Generate an optimized prompt based on performance insights"""
    try:
        # Get user's business profile
        business_profile = await db.business_profiles.find_one({"user_id": current_user.id})
        if not business_profile:
            raise HTTPException(status_code=404, detail="Business profile not found")
        
        # Get latest performance data
        latest_insights = await db.performance_insights.find_one(
            {"business_id": business_profile["id"]},
            sort=[("created_at", -1)]
        )
        
        performance_data = {}
        if latest_insights:
            performance_data = {
                "has_insights": True,
                "avg_engagement_rate": latest_insights.get("avg_engagement_rate", 0),
                "recommended_hashtags": [h.get("pattern_value", "") for h in latest_insights.get("top_hashtags", [])],
                "high_performing_keywords": [k.get("pattern_value", "") for k in latest_insights.get("top_keywords", [])],
                "optimal_content_length": latest_insights.get("optimal_content_length", {}).get("pattern_value", "100-150"),
                "high_performing_topics": [t.get("pattern_value", "") for t in latest_insights.get("high_performing_topics", [])],
                "ai_recommendations": latest_insights.get("ai_recommendations", [])
            }
        else:
            performance_data = {"has_insights": False}
        
        # Generate optimized prompt
        optimized_prompt = await prompt_optimizer.generate_optimized_prompt(
            business_profile, 
            performance_data, 
            prompt_type
        )
        
        return {
            "message": "Prompt optimisé généré avec succès",
            "optimized_prompt": optimized_prompt,
            "version": optimized_prompt["prompt_version"],
            "based_on_insights": optimized_prompt["based_on_insights"],
            "expected_improvement": optimized_prompt.get("expected_improvement", 0)
        }
        
    except Exception as e:
        logging.error(f"Error generating optimized prompt: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération du prompt optimisé: {str(e)}")

@analytics_router.get("/prompts/performance")
async def get_prompt_performance_history(
    current_user: User = Depends(get_current_active_user)
):
    """Get prompt performance history"""
    try:
        # Get user's business profile
        business_profile = await db.business_profiles.find_one({"user_id": current_user.id})
        if not business_profile:
            raise HTTPException(status_code=404, detail="Business profile not found")
        
        # Get prompt performance analysis history
        analysis_history = await db.prompt_performance_analysis.find(
            {"business_id": business_profile["id"]}
        ).sort("created_at", -1).to_list(10)
        
        if not analysis_history:
            return {
                "message": "Aucun historique d'analyse de prompts disponible",
                "history": [],
                "total_analyses": 0
            }
        
        # Format history for frontend
        formatted_history = []
        for analysis in analysis_history:
            analysis_data = analysis.get("analysis_data", {})
            formatted_history.append({
                "analysis_date": analysis["created_at"],
                "prompt_versions_tested": analysis_data.get("prompt_versions_tested", 0),
                "total_posts_analyzed": analysis_data.get("total_posts_analyzed", 0),
                "best_performing_prompt": analysis_data.get("best_performing_prompt", {}),
                "optimization_insights": analysis_data.get("optimization_insights", [])[:3],
                "has_data": analysis_data.get("has_data", False)
            })
        
        return {
            "message": "Historique des analyses de prompts",
            "history": formatted_history,
            "total_analyses": len(analysis_history),
            "latest_analysis": formatted_history[0] if formatted_history else None
        }
        
    except Exception as e:
        logging.error(f"Error getting prompt performance history: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de l'historique: {str(e)}")

@analytics_router.get("/prompts/optimized")
async def get_optimized_prompts(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user)
):
    """Get optimized prompts for a business"""
    try:
        # Get user's business profile
        business_profile = await db.business_profiles.find_one({"user_id": current_user.id})
        if not business_profile:
            raise HTTPException(status_code=404, detail="Business profile not found")
        
        # Get optimized prompts
        optimized_prompts = await db.optimized_prompts.find(
            {"business_id": business_profile["id"]}
        ).sort("created_at", -1).to_list(limit)
        
        if not optimized_prompts:
            return {
                "message": "Aucun prompt optimisé disponible",
                "prompts": [],
                "total": 0
            }
        
        return {
            "message": f"{len(optimized_prompts)} prompts optimisés trouvés",
            "prompts": optimized_prompts,
            "total": len(optimized_prompts),
            "latest_version": optimized_prompts[0]["prompt_version"] if optimized_prompts else None
        }
        
    except Exception as e:
        logging.error(f"Error getting optimized prompts: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des prompts optimisés: {str(e)}")