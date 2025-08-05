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
        if not self.chat:
            # Fallback recommendations when OpenAI is not available
            return [
                "Continuez à utiliser les hashtags qui génèrent le plus d'engagement",
                "Variez les types de contenu pour maintenir l'intérêt de votre audience",
                "Publiez régulièrement pour maintenir la visibilité",
                "Engagez avec votre communauté en répondant aux commentaires"
            ]
        
        try:
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