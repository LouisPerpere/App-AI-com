from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, EmailStr
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path
import logging
from auth import get_admin_user, User
import stripe

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Stripe configuration
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', '')

# Admin router
admin_router = APIRouter(prefix="/admin")

# Pydantic Models for Admin
class SubscriptionPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    price_monthly: float
    price_yearly: float
    stripe_price_id_monthly: str
    stripe_price_id_yearly: str
    features: List[str]
    max_posts_per_month: int
    max_platforms: int
    ai_generations_per_month: int
    priority_support: bool = False
    custom_branding: bool = False
    analytics: bool = False
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PromoCode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str
    discount_type: str  # percentage, fixed
    discount_value: float
    max_uses: Optional[int] = None
    used_count: int = 0
    expires_at: Optional[datetime] = None
    active: bool = True
    created_by: str  # admin user id
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PromoCodeCreate(BaseModel):
    code: str
    discount_type: str
    discount_value: float
    max_uses: Optional[int] = None
    expires_at: Optional[datetime] = None

class ReferralProgram(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    referrer_user_id: str
    referred_user_id: str
    referral_code: str
    reward_type: str = "discount"  # discount, credit, free_months
    reward_value: float = 20.0  # 20% discount or 20€ credit
    status: str = "pending"  # pending, completed, paid
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Payment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    stripe_payment_intent_id: str
    amount: float
    currency: str = "EUR"
    status: str  # succeeded, failed, pending
    subscription_plan: str
    billing_period: str  # monthly, yearly
    promo_code: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Subscription(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    plan_id: str
    stripe_subscription_id: str
    status: str  # active, cancelled, past_due, incomplete
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AdminStats(BaseModel):
    total_users: int
    active_subscriptions: int
    trial_users: int
    expired_users: int
    mrr: float  # Monthly Recurring Revenue
    churn_rate: float
    total_revenue: float
    new_users_this_month: int
    posts_generated_today: int
    posts_generated_this_month: int

class UserDetail(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    subscription_status: str
    subscription_plan: str
    trial_ends_at: Optional[datetime]
    subscription_ends_at: Optional[datetime]
    total_posts_generated: int
    last_login: Optional[datetime]
    created_at: datetime
    business_name: Optional[str] = None

# Default subscription plans
DEFAULT_PLANS = [
    {
        "name": "Starter",
        "price_monthly": 19.99,
        "price_yearly": 199.99,
        "stripe_price_id_monthly": "price_starter_monthly",
        "stripe_price_id_yearly": "price_starter_yearly",
        "features": [
            "50 posts IA par mois",
            "2 réseaux sociaux",
            "Programmation automatique",
            "Support par email"
        ],
        "max_posts_per_month": 50,
        "max_platforms": 2,
        "ai_generations_per_month": 50,
        "priority_support": False,
        "custom_branding": False,
        "analytics": False
    },
    {
        "name": "Pro",
        "price_monthly": 49.99,
        "price_yearly": 499.99,
        "stripe_price_id_monthly": "price_pro_monthly",
        "stripe_price_id_yearly": "price_pro_yearly",
        "features": [
            "200 posts IA par mois",
            "Tous les réseaux sociaux",
            "Analytics avancés",
            "Support prioritaire",
            "Calendrier de contenu"
        ],
        "max_posts_per_month": 200,
        "max_platforms": 5,
        "ai_generations_per_month": 200,
        "priority_support": True,
        "custom_branding": False,
        "analytics": True
    },
    {
        "name": "Enterprise",
        "price_monthly": 99.99,
        "price_yearly": 999.99,
        "stripe_price_id_monthly": "price_enterprise_monthly",
        "stripe_price_id_yearly": "price_enterprise_yearly",
        "features": [
            "Posts IA illimités",
            "Tous les réseaux sociaux",
            "Branding personnalisé",
            "Support dédié",
            "Analytics complets",
            "API access"
        ],
        "max_posts_per_month": -1,  # Unlimited
        "max_platforms": -1,  # Unlimited
        "ai_generations_per_month": -1,  # Unlimited
        "priority_support": True,
        "custom_branding": True,
        "analytics": True
    }
]

# Initialize default plans
async def init_default_plans():
    """Initialize default subscription plans if they don't exist"""
    try:
        existing_plans = await db.subscription_plans.count_documents({})
        if existing_plans == 0:
            plans = [SubscriptionPlan(**plan) for plan in DEFAULT_PLANS]
            for plan in plans:
                await db.subscription_plans.insert_one(plan.dict())
            logging.info("Default subscription plans initialized")
    except Exception as e:
        logging.error(f"Error initializing default plans: {e}")

# Admin Routes

@admin_router.get("/stats", response_model=AdminStats)
async def get_admin_stats(admin_user: User = Depends(get_admin_user)):
    """Get admin dashboard statistics"""
    try:
        # Calculate date ranges
        now = datetime.utcnow()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Total users
        total_users = await db.users.count_documents({})
        
        # Active subscriptions
        active_subscriptions = await db.users.count_documents({
            "subscription_status": "active"
        })
        
        # Trial users
        trial_users = await db.users.count_documents({
            "subscription_status": "trial",
            "trial_ends_at": {"$gte": now}
        })
        
        # Expired users
        expired_users = await db.users.count_documents({
            "$or": [
                {"subscription_status": "expired"},
                {"subscription_status": "trial", "trial_ends_at": {"$lt": now}}
            ]
        })
        
        # New users this month
        new_users_this_month = await db.users.count_documents({
            "created_at": {"$gte": start_of_month}
        })
        
        # Posts generated today/this month
        posts_generated_today = await db.generated_posts.count_documents({
            "created_at": {"$gte": start_of_today}
        })
        
        posts_generated_this_month = await db.generated_posts.count_documents({
            "created_at": {"$gte": start_of_month}
        })
        
        # Calculate MRR (simplified - would need proper subscription data)
        payments_this_month = await db.payments.find({
            "created_at": {"$gte": start_of_month},
            "status": "succeeded"
        }).to_list(1000)
        
        total_revenue = sum(payment.get("amount", 0) for payment in payments_this_month)
        
        # Estimate MRR (simplified calculation)
        mrr = total_revenue  # This would need more sophisticated calculation
        
        # Calculate churn rate (simplified)
        churn_rate = (expired_users / max(total_users, 1)) * 100
        
        return AdminStats(
            total_users=total_users,
            active_subscriptions=active_subscriptions,
            trial_users=trial_users,
            expired_users=expired_users,
            mrr=mrr,
            churn_rate=churn_rate,
            total_revenue=total_revenue,
            new_users_this_month=new_users_this_month,
            posts_generated_today=posts_generated_today,
            posts_generated_this_month=posts_generated_this_month
        )
        
    except Exception as e:
        logging.error(f"Error getting admin stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving statistics"
        )

@admin_router.get("/users", response_model=List[UserDetail])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    admin_user: User = Depends(get_admin_user)
):
    """Get all users with pagination and filtering"""
    try:
        # Build query
        query = {}
        if search:
            query["$or"] = [
                {"email": {"$regex": search, "$options": "i"}},
                {"first_name": {"$regex": search, "$options": "i"}},
                {"last_name": {"$regex": search, "$options": "i"}}
            ]
        
        if status:
            query["subscription_status"] = status
        
        # Get users with business profile names
        pipeline = [
            {"$match": query},
            {"$lookup": {
                "from": "business_profiles",
                "localField": "id",
                "foreignField": "user_id",
                "as": "business_profile"
            }},
            {"$lookup": {
                "from": "generated_posts",
                "localField": "id",
                "foreignField": "user_id",
                "as": "posts"
            }},
            {"$addFields": {
                "business_name": {"$arrayElemAt": ["$business_profile.business_name", 0]},
                "total_posts_generated": {"$size": "$posts"}
            }},
            {"$project": {
                "hashed_password": 0,
                "business_profile": 0,
                "posts": 0
            }},
            {"$sort": {"created_at": -1}},
            {"$skip": skip},
            {"$limit": limit}
        ]
        
        users = await db.users.aggregate(pipeline).to_list(limit)
        
        return [UserDetail(**user) for user in users]
        
    except Exception as e:
        logging.error(f"Error getting users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving users"
        )

@admin_router.put("/users/{user_id}/subscription")
async def update_user_subscription(
    user_id: str,
    subscription_status: str,
    subscription_plan: str = None,
    subscription_ends_at: datetime = None,
    admin_user: User = Depends(get_admin_user)
):
    """Update user subscription status"""
    try:
        update_data = {
            "subscription_status": subscription_status,
            "updated_at": datetime.utcnow()
        }
        
        if subscription_plan:
            update_data["subscription_plan"] = subscription_plan
        
        if subscription_ends_at:
            update_data["subscription_ends_at"] = subscription_ends_at
        
        result = await db.users.update_one(
            {"id": user_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {"message": "Subscription updated successfully"}
        
    except Exception as e:
        logging.error(f"Error updating user subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating subscription"
        )

@admin_router.get("/subscription-plans", response_model=List[SubscriptionPlan])
async def get_subscription_plans(admin_user: User = Depends(get_admin_user)):
    """Get all subscription plans"""
    try:
        plans = await db.subscription_plans.find({"active": True}).to_list(100)
        return [SubscriptionPlan(**plan) for plan in plans]
    except Exception as e:
        logging.error(f"Error getting subscription plans: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving subscription plans"
        )

@admin_router.post("/subscription-plans", response_model=SubscriptionPlan)
async def create_subscription_plan(
    plan: SubscriptionPlan,
    admin_user: User = Depends(get_admin_user)
):
    """Create a new subscription plan"""
    try:
        await db.subscription_plans.insert_one(plan.dict())
        return plan
    except Exception as e:
        logging.error(f"Error creating subscription plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating subscription plan"
        )

@admin_router.get("/promo-codes", response_model=List[PromoCode])
async def get_promo_codes(admin_user: User = Depends(get_admin_user)):
    """Get all promo codes"""
    try:
        codes = await db.promo_codes.find().sort("created_at", -1).to_list(100)
        return [PromoCode(**code) for code in codes]
    except Exception as e:
        logging.error(f"Error getting promo codes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving promo codes"
        )

@admin_router.post("/promo-codes", response_model=PromoCode)
async def create_promo_code(
    promo_data: PromoCodeCreate,
    admin_user: User = Depends(get_admin_user)
):
    """Create a new promo code"""
    try:
        # Check if code already exists
        existing = await db.promo_codes.find_one({"code": promo_data.code})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Promo code already exists"
            )
        
        promo_code = PromoCode(
            created_by=admin_user.id,
            **promo_data.dict()
        )
        
        await db.promo_codes.insert_one(promo_code.dict())
        return promo_code
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error creating promo code: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating promo code"
        )

@admin_router.get("/referrals", response_model=List[ReferralProgram])
async def get_referrals(admin_user: User = Depends(get_admin_user)):
    """Get all referrals"""
    try:
        referrals = await db.referrals.find().sort("created_at", -1).to_list(100)
        return [ReferralProgram(**referral) for referral in referrals]
    except Exception as e:
        logging.error(f"Error getting referrals: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving referrals"
        )

@admin_router.get("/payments", response_model=List[Payment])
async def get_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    admin_user: User = Depends(get_admin_user)
):
    """Get all payments"""
    try:
        payments = await db.payments.find().sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
        return [Payment(**payment) for payment in payments]
    except Exception as e:
        logging.error(f"Error getting payments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving payments"
        )

@admin_router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    admin_user: User = Depends(get_admin_user)
):
    """Delete a user and all associated data"""
    try:
        # Delete user data in order
        await db.generated_posts.delete_many({"user_id": user_id})
        await db.content_uploads.delete_many({"user_id": user_id})
        await db.content_notes.delete_many({"user_id": user_id})
        await db.business_profiles.delete_many({"user_id": user_id})
        await db.subscriptions.delete_many({"user_id": user_id})
        await db.payments.delete_many({"user_id": user_id})
        
        # Finally delete the user
        result = await db.users.delete_one({"id": user_id})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {"message": "User deleted successfully"}
        
    except Exception as e:
        logging.error(f"Error deleting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting user"
        )

@admin_router.get("/analytics/revenue")
async def get_revenue_analytics(
    period: str = Query("month", regex="^(week|month|quarter|year)$"),
    admin_user: User = Depends(get_admin_user)
):
    """Get revenue analytics"""
    try:
        now = datetime.utcnow()
        
        # Calculate period start
        if period == "week":
            start_date = now - timedelta(weeks=1)
        elif period == "month":
            start_date = now - timedelta(days=30)
        elif period == "quarter":
            start_date = now - timedelta(days=90)
        else:  # year
            start_date = now - timedelta(days=365)
        
        # Get payments in period
        pipeline = [
            {
                "$match": {
                    "created_at": {"$gte": start_date},
                    "status": "succeeded"
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$created_at"
                        }
                    },
                    "revenue": {"$sum": "$amount"},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        revenue_data = await db.payments.aggregate(pipeline).to_list(1000)
        
        total_revenue = sum(item["revenue"] for item in revenue_data)
        total_transactions = sum(item["count"] for item in revenue_data)
        
        return {
            "period": period,
            "total_revenue": total_revenue,
            "total_transactions": total_transactions,
            "daily_data": revenue_data
        }
        
    except Exception as e:
        logging.error(f"Error getting revenue analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving revenue analytics"
        )

# Initialize admin user if it doesn't exist
async def init_admin_user():
    """Create default admin user if none exists"""
    try:
        admin_count = await db.users.count_documents({"is_admin": True})
        if admin_count == 0:
            from auth import get_password_hash
            admin_user = {
                "id": str(uuid.uuid4()),
                "email": "admin@postcraft.com",
                "hashed_password": get_password_hash("admin123"),
                "first_name": "Admin",
                "last_name": "PostCraft",
                "is_active": True,
                "is_admin": True,
                "subscription_status": "active",
                "subscription_plan": "enterprise",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await db.users.insert_one(admin_user)
            logging.info("Default admin user created: admin@postcraft.com / admin123")
    except Exception as e:
        logging.error(f"Error initializing admin user: {e}")

# Initialize on startup
async def init_admin_data():
    """Initialize admin data on startup"""
    await init_admin_user()
    await init_default_plans()