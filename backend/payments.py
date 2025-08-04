from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import uuid
import stripe
import os
from dotenv import load_dotenv
from pathlib import Path
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from auth import get_current_active_user, User

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Stripe configuration
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')

# Payment router
payment_router = APIRouter(prefix="/payments")

# Pydantic Models
class PaymentIntent(BaseModel):
    plan_id: str
    billing_period: str  # monthly, yearly
    promo_code: Optional[str] = None

class PaymentIntentResponse(BaseModel):
    client_secret: str
    amount: float
    currency: str = "EUR"

class SubscriptionCreate(BaseModel):
    payment_intent_id: str
    plan_id: str
    billing_period: str

class WebhookEvent(BaseModel):
    type: str
    data: dict

# Payment Routes

@payment_router.post("/create-payment-intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    payment_data: PaymentIntent,
    current_user: User = Depends(get_current_active_user)
):
    """Create a Stripe payment intent"""
    try:
        # Get subscription plan
        plan = await db.subscription_plans.find_one({"id": payment_data.plan_id})
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan d'abonnement non trouvé"
            )
        
        # Calculate amount
        if payment_data.billing_period == "yearly":
            amount = plan["price_yearly"]
        else:
            amount = plan["price_monthly"]
        
        # Apply promo code if provided
        discount_amount = 0
        if payment_data.promo_code:
            promo = await db.promo_codes.find_one({
                "code": payment_data.promo_code,
                "active": True
            })
            
            if promo:
                # Check if promo code is still valid
                if promo.get("expires_at") and promo["expires_at"] < datetime.utcnow():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Code promo expiré"
                    )
                
                # Check usage limit
                if promo.get("max_uses") and promo["used_count"] >= promo["max_uses"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Code promo épuisé"
                    )
                
                # Calculate discount
                if promo["discount_type"] == "percentage":
                    discount_amount = amount * (promo["discount_value"] / 100)
                else:  # fixed
                    discount_amount = min(promo["discount_value"], amount)
                
                amount -= discount_amount
        
        # Create Stripe payment intent
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Stripe uses cents
            currency="eur",
            metadata={
                "user_id": current_user.id,
                "plan_id": payment_data.plan_id,
                "billing_period": payment_data.billing_period,
                "promo_code": payment_data.promo_code or "",
                "original_amount": str(amount + discount_amount),
                "discount_amount": str(discount_amount)
            },
            automatic_payment_methods={
                "enabled": True,
            },
        )
        
        return PaymentIntentResponse(
            client_secret=intent.client_secret,
            amount=amount,
            currency="EUR"
        )
        
    except stripe.error.StripeError as e:
        logging.error(f"Stripe error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur de paiement: {str(e)}"
        )
    except Exception as e:
        logging.error(f"Payment intent creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création du paiement"
        )

@payment_router.post("/confirm-subscription")
async def confirm_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Confirm subscription after successful payment"""
    try:
        # Verify payment intent
        intent = stripe.PaymentIntent.retrieve(subscription_data.payment_intent_id)
        
        if intent.status != "succeeded":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Paiement non confirmé"
            )
        
        # Get plan details
        plan = await db.subscription_plans.find_one({"id": subscription_data.plan_id})
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan non trouvé"
            )
        
        # Calculate subscription period
        now = datetime.utcnow()
        if subscription_data.billing_period == "yearly":
            end_date = now + timedelta(days=365)
            amount = plan["price_yearly"]
        else:
            end_date = now + timedelta(days=30)
            amount = plan["price_monthly"]
        
        # Update user subscription
        await db.users.update_one(
            {"id": current_user.id},
            {
                "$set": {
                    "subscription_status": "active",
                    "subscription_plan": plan["name"].lower(),
                    "subscription_ends_at": end_date,
                    "updated_at": now
                }
            }
        )
        
        # Create payment record
        payment = {
            "id": str(uuid.uuid4()),
            "user_id": current_user.id,
            "stripe_payment_intent_id": subscription_data.payment_intent_id,
            "amount": amount,
            "currency": "EUR",
            "status": "succeeded",
            "subscription_plan": plan["name"],
            "billing_period": subscription_data.billing_period,
            "promo_code": intent.metadata.get("promo_code"),
            "created_at": now
        }
        await db.payments.insert_one(payment)
        
        # Update promo code usage if applicable
        promo_code = intent.metadata.get("promo_code")
        if promo_code:
            await db.promo_codes.update_one(
                {"code": promo_code},
                {"$inc": {"used_count": 1}}
            )
        
        return {
            "message": "Abonnement activé avec succès",
            "subscription_end": end_date,
            "plan": plan["name"]
        }
        
    except stripe.error.StripeError as e:
        logging.error(f"Stripe error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur Stripe: {str(e)}"
        )
    except Exception as e:
        logging.error(f"Subscription confirmation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la confirmation de l'abonnement"
        )

@payment_router.get("/subscription-plans")
async def get_public_subscription_plans():
    """Get public subscription plans for pricing page"""
    try:
        plans = await db.subscription_plans.find({"active": True}).to_list(100)
        
        # Format plans for public consumption
        public_plans = []
        for plan in plans:
            public_plan = {
                "id": plan["id"],
                "name": plan["name"],
                "price_monthly": plan["price_monthly"],
                "price_yearly": plan["price_yearly"],
                "features": plan["features"],
                "max_posts_per_month": plan["max_posts_per_month"],
                "max_platforms": plan["max_platforms"],
                "ai_generations_per_month": plan["ai_generations_per_month"],
                "priority_support": plan["priority_support"],
                "custom_branding": plan["custom_branding"],
                "analytics": plan["analytics"]
            }
            public_plans.append(public_plan)
        
        return public_plans
        
    except Exception as e:
        logging.error(f"Error getting public plans: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des plans"
        )

@payment_router.post("/validate-promo-code")
async def validate_promo_code(
    code: str,
    plan_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Validate a promo code"""
    try:
        promo = await db.promo_codes.find_one({
            "code": code,
            "active": True
        })
        
        if not promo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Code promo invalide"
            )
        
        # Check expiration
        if promo.get("expires_at") and promo["expires_at"] < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Code promo expiré"
            )
        
        # Check usage limit
        if promo.get("max_uses") and promo["used_count"] >= promo["max_uses"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Code promo épuisé"
            )
        
        # Get plan to calculate discount
        plan = await db.subscription_plans.find_one({"id": plan_id})
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan non trouvé"
            )
        
        # Calculate discount
        monthly_price = plan["price_monthly"]
        yearly_price = plan["price_yearly"]
        
        if promo["discount_type"] == "percentage":
            monthly_discount = monthly_price * (promo["discount_value"] / 100)
            yearly_discount = yearly_price * (promo["discount_value"] / 100)
        else:  # fixed
            monthly_discount = min(promo["discount_value"], monthly_price)
            yearly_discount = min(promo["discount_value"], yearly_price)
        
        return {
            "valid": True,
            "code": code,
            "discount_type": promo["discount_type"],
            "discount_value": promo["discount_value"],
            "monthly_discount": monthly_discount,
            "yearly_discount": yearly_discount,
            "new_monthly_price": monthly_price - monthly_discount,
            "new_yearly_price": yearly_price - yearly_discount
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error validating promo code: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la validation du code promo"
        )

@payment_router.get("/my-subscription")
async def get_my_subscription(current_user: User = Depends(get_current_active_user)):
    """Get current user's subscription details"""
    try:
        # Get user's latest payment
        latest_payment = await db.payments.find_one(
            {"user_id": current_user.id},
            sort=[("created_at", -1)]
        )
        
        # Get subscription status from auth module
        from auth import check_subscription_status
        subscription_status = check_subscription_status(current_user)
        
        return {
            "subscription_status": subscription_status,
            "current_plan": current_user.subscription_plan,
            "subscription_ends_at": current_user.subscription_ends_at,
            "trial_ends_at": current_user.trial_ends_at,
            "latest_payment": latest_payment
        }
        
    except Exception as e:
        logging.error(f"Error getting subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération de l'abonnement"
        )

@payment_router.post("/cancel-subscription")
async def cancel_subscription(current_user: User = Depends(get_current_active_user)):
    """Cancel user's subscription"""
    try:
        # Update user status to cancelled (but keep active until period end)
        await db.users.update_one(
            {"id": current_user.id},
            {
                "$set": {
                    "subscription_status": "cancelled",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "message": "Abonnement annulé avec succès",
            "active_until": current_user.subscription_ends_at,
            "note": "Votre abonnement restera actif jusqu'à la fin de la période payée"
        }
        
    except Exception as e:
        logging.error(f"Error cancelling subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'annulation de l'abonnement"
        )