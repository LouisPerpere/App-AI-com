from fastapi import APIRouter, HTTPException, Depends, status, Request
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import uuid
import os
from dotenv import load_dotenv
from pathlib import Path
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from auth import get_current_active_user, User

# Simple Stripe integration without emergentintegrations
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False

# Simple replacement classes for emergentintegrations
class SimpleCheckoutSessionRequest(BaseModel):
    amount: float
    currency: str
    success_url: str
    cancel_url: str
    metadata: Dict[str, Any] = {}

class SimpleCheckoutSessionResponse(BaseModel):
    session_id: str
    url: str

class SimpleCheckoutStatusResponse(BaseModel):
    status: str
    payment_status: str
    amount_total: float
    currency: str
    metadata: Dict[str, Any] = {}

class SimpleStripeCheckout:
    def __init__(self, api_key: str, webhook_url: str = ""):
        self.api_key = api_key
        self.webhook_url = webhook_url
        try:
            import stripe
            stripe.api_key = api_key
            self.stripe_available = True
        except ImportError:
            self.stripe_available = False
    
    async def create_checkout_session(self, request: SimpleCheckoutSessionRequest) -> SimpleCheckoutSessionResponse:
        if not self.stripe_available:
            raise HTTPException(status_code=500, detail="Stripe not available")
        
        import stripe
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': request.currency,
                    'product_data': {
                        'name': 'Subscription',
                    },
                    'unit_amount': int(request.amount * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            metadata=request.metadata
        )
        
        return SimpleCheckoutSessionResponse(
            session_id=session.id,
            url=session.url
        )
    
    async def get_checkout_status(self, session_id: str) -> SimpleCheckoutStatusResponse:
        if not self.stripe_available:
            raise HTTPException(status_code=500, detail="Stripe not available")
        
        import stripe
        session = stripe.checkout.Session.retrieve(session_id)
        
        return SimpleCheckoutStatusResponse(
            status=session.status,
            payment_status=session.payment_status,
            amount_total=session.amount_total / 100 if session.amount_total else 0,
            currency=session.currency or "eur",
            metadata=session.metadata or {}
        )
    
    async def handle_webhook(self, body: bytes, signature: str):
        # Simple webhook handling - in production you'd want proper signature verification
        import json
        try:
            event = json.loads(body)
            return type('WebhookResponse', (), {
                'event_type': event.get('type', ''),
                'session_id': event.get('data', {}).get('object', {}).get('id', ''),
                'payment_status': event.get('data', {}).get('object', {}).get('payment_status', '')
            })()
        except:
            raise HTTPException(status_code=400, detail="Invalid webhook payload")

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Stripe configuration
if STRIPE_AVAILABLE:
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY', '')

# Payment router
payment_router = APIRouter(prefix="/payments")

# Fixed subscription plans (server-side definition for security)
SUBSCRIPTION_PACKAGES = {
    "starter_monthly": {"name": "Starter", "amount": 14.99, "period": "monthly", "plan_id": "starter"},
    "starter_yearly": {"name": "Starter", "amount": 149.99, "period": "yearly", "plan_id": "starter"},
    "rocket_monthly": {"name": "Rocket", "amount": 29.99, "period": "monthly", "plan_id": "rocket"},
    "rocket_yearly": {"name": "Rocket", "amount": 299.99, "period": "yearly", "plan_id": "rocket"},
    "pro_monthly": {"name": "Pro", "amount": 199.99, "period": "monthly", "plan_id": "pro"},
    "pro_yearly": {"name": "Pro", "amount": 1999.99, "period": "yearly", "plan_id": "pro"},
}

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

# New models for emergentintegrations Stripe checkout
class CheckoutRequest(BaseModel):
    package_id: str  # e.g., "starter_monthly", "pro_yearly"
    origin_url: str  # Frontend origin URL
    promo_code: Optional[str] = None

class PaymentTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_id: str
    payment_id: Optional[str] = None
    package_id: str
    amount: float
    currency: str = "eur"
    payment_status: str = "pending"  # pending, paid, failed, expired
    status: str = "initiated"  # initiated, completed, cancelled
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

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
        if not STRIPE_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Stripe not available"
            )
        
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
        
    except Exception as e:
        if STRIPE_AVAILABLE and hasattr(e, '__module__') and 'stripe' in str(e.__module__):
            logging.error(f"Stripe error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erreur de paiement: {str(e)}"
            )
        else:
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
        if not STRIPE_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Stripe not available"
            )
        
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
        
    except Exception as e:
        if STRIPE_AVAILABLE and hasattr(e, '__module__') and 'stripe' in str(e.__module__):
            logging.error(f"Stripe error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erreur Stripe: {str(e)}"
            )
        else:
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

# New Emergentintegrations Stripe Checkout Routes

@payment_router.post("/v1/checkout/session")
async def create_checkout_session(
    request: CheckoutRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Create Stripe checkout session using emergentintegrations"""
    try:
        # Validate package
        if request.package_id not in SUBSCRIPTION_PACKAGES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid package selected"
            )
        
        package = SUBSCRIPTION_PACKAGES[request.package_id]
        amount = package["amount"]
        
        # Apply promo code if provided
        final_amount = amount
        if request.promo_code:
            promo = await db.promo_codes.find_one({
                "code": request.promo_code,
                "active": True
            })
            
            if promo:
                # Check validity
                if promo.get("expires_at") and promo["expires_at"] < datetime.utcnow():
                    raise HTTPException(status_code=400, detail="Code promo expiré")
                
                if promo.get("max_uses") and promo["used_count"] >= promo["max_uses"]:
                    raise HTTPException(status_code=400, detail="Code promo épuisé")
                
                # Calculate discount
                if promo["discount_type"] == "percentage":
                    discount_amount = amount * (promo["discount_value"] / 100)
                else:  # fixed
                    discount_amount = min(promo["discount_value"], amount)
                
                final_amount = amount - discount_amount
        
        # Initialize Stripe checkout (dummy request for webhook URL)
        webhook_url = f"{request.origin_url.rstrip('/')}/api/webhook/stripe"
        
        # Prepare metadata (needed for both demo and real modes)
        metadata = {
            "user_id": current_user.id,
            "package_id": request.package_id,
            "plan_name": package["name"],
            "billing_period": package["period"],
            "original_amount": str(amount),
            "promo_code": request.promo_code or ""
        }
        
        # For demo/testing purposes when Stripe API key is not valid
        if not STRIPE_API_KEY or STRIPE_API_KEY == 'sk_test_emergent' or len(STRIPE_API_KEY) < 20:
            # Create a mock session for demonstration
            session_id = f"cs_test_demo_{uuid.uuid4().hex[:16]}"
            checkout_url = f"{request.origin_url.rstrip('/')}/?session_id={session_id}&payment_success=true&demo_mode=true"
            
            # Create payment transaction record
            transaction = PaymentTransaction(
                user_id=current_user.id,
                session_id=session_id,
                package_id=request.package_id,
                amount=final_amount,
                currency="eur",
                payment_status="paid",  # Auto-success for demo
                status="completed",
                metadata=metadata
            )
            
            await db.payment_transactions.insert_one(transaction.dict())
            
            # Immediately process successful payment for demo
            await process_successful_payment(transaction.dict(), current_user)
            
            return {
                "url": checkout_url,
                "session_id": session_id,
                "demo_mode": True,
                "message": "Demo mode: Payment simulation successful"
            }
        
        stripe_checkout = SimpleStripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        # Create success and cancel URLs
        success_url = f"{request.origin_url.rstrip('/')}/?session_id={{CHECKOUT_SESSION_ID}}&payment_success=true"
        cancel_url = f"{request.origin_url.rstrip('/')}/?payment_cancelled=true"
        
        # Create checkout session
        checkout_request = SimpleCheckoutSessionRequest(
            amount=final_amount,
            currency="eur",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata
        )
        
        session: SimpleCheckoutSessionResponse = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Create payment transaction record
        transaction = PaymentTransaction(
            user_id=current_user.id,
            session_id=session.session_id,
            package_id=request.package_id,
            amount=final_amount,
            currency="eur",
            payment_status="pending",
            status="initiated",
            metadata=metadata
        )
        
        await db.payment_transactions.insert_one(transaction.dict())
        
        return {
            "url": session.url,
            "session_id": session.session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error creating checkout session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création de la session de paiement"
        )

@payment_router.get("/v1/checkout/status/{session_id}")
async def get_checkout_status(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get checkout session status and update payment record"""
    try:
        # Find payment transaction
        transaction = await db.payment_transactions.find_one({
            "session_id": session_id,
            "user_id": current_user.id
        })
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        if not STRIPE_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Stripe API key not configured"
            )
        
        # Initialize Stripe checkout
        stripe_checkout = SimpleStripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
        
        # Get status from Stripe
        checkout_status: SimpleCheckoutStatusResponse = await stripe_checkout.get_checkout_status(session_id)
        
        # Update transaction record only if status changed
        if (checkout_status.payment_status != transaction["payment_status"] or 
            checkout_status.status != transaction["status"]):
            
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "payment_status": checkout_status.payment_status,
                        "status": checkout_status.status,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # If payment successful, update user subscription
            if checkout_status.payment_status == "paid" and transaction["payment_status"] != "paid":
                await process_successful_payment(transaction, current_user)
        
        return {
            "status": checkout_status.status,
            "payment_status": checkout_status.payment_status,
            "amount_total": checkout_status.amount_total,
            "currency": checkout_status.currency,
            "metadata": checkout_status.metadata
        }
        
    except Exception as e:
        logging.error(f"Error getting checkout status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la vérification du statut de paiement"
        )

@payment_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    try:
        body = await request.body()
        signature = request.headers.get("Stripe-Signature")
        
        if not STRIPE_API_KEY:
            raise HTTPException(status_code=500, detail="Stripe not configured")
        
        stripe_checkout = SimpleStripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        # Process webhook based on event type
        if webhook_response.event_type == "checkout.session.completed":
            # Update payment transaction
            await db.payment_transactions.update_one(
                {"session_id": webhook_response.session_id},
                {
                    "$set": {
                        "payment_status": webhook_response.payment_status,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
        return {"received": True}
        
    except Exception as e:
        logging.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=400, detail="Webhook processing failed")

async def process_successful_payment(transaction: dict, user: User):
    """Process successful payment and update user subscription"""
    try:
        package = SUBSCRIPTION_PACKAGES[transaction["package_id"]]
        
        # Calculate subscription end date
        now = datetime.utcnow()
        if package["period"] == "yearly":
            end_date = now + timedelta(days=365)
        else:  # monthly
            end_date = now + timedelta(days=30)
        
        # Update user subscription
        await db.users.update_one(
            {"id": user.id},
            {
                "$set": {
                    "subscription_status": "active",
                    "subscription_plan": package["plan_id"],
                    "subscription_ends_at": end_date,
                    "updated_at": now
                }
            }
        )
        
        # Create payment record for admin tracking
        payment = {
            "id": str(uuid.uuid4()),
            "user_id": user.id,
            "stripe_payment_intent_id": transaction["session_id"],
            "amount": transaction["amount"],
            "currency": transaction["currency"],
            "status": "succeeded",
            "subscription_plan": package["name"],
            "billing_period": package["period"],
            "promo_code": transaction["metadata"].get("promo_code"),
            "created_at": now
        }
        await db.payments.insert_one(payment)
        
        # Update promo code usage if applicable
        promo_code = transaction["metadata"].get("promo_code")
        if promo_code:
            await db.promo_codes.update_one(
                {"code": promo_code},
                {"$inc": {"used_count": 1}}
            )
        
        logging.info(f"Subscription activated for user {user.id}: {package['name']} {package['period']}")
        
    except Exception as e:
        logging.error(f"Error processing successful payment: {e}")
        raise