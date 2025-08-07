"""
Modern Stripe Payment Integration for Claire et Marcus
Using emergentintegrations library with proper security patterns
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import os
import logging
from database import get_database

# Import emergentintegrations Stripe components
try:
    from emergentintegrations.payments.stripe.checkout import (
        StripeCheckout, 
        CheckoutSessionResponse, 
        CheckoutStatusResponse, 
        CheckoutSessionRequest
    )
    EMERGENT_STRIPE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ EmergentIntegrations Stripe not available: {e}")
    EMERGENT_STRIPE_AVAILABLE = False

# Create router
payments_router = APIRouter(prefix="/api/payments")

# Get database
db = get_database()

# Stripe API Key from environment
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")

# SECURITY: Fixed subscription packages (amounts in EUR as floats)
SUBSCRIPTION_PACKAGES = {
    "starter_monthly": {
        "name": "Starter",
        "amount": 14.99,
        "period": "monthly",
        "plan_id": "starter",
        "description": "4 posts/mois, 1 réseau social",
        "features": ["4 posts par mois", "1 réseau social", "Templates de base"],
        "max_posts": 4,
        "max_networks": 1
    },
    "rocket_monthly": {
        "name": "Rocket", 
        "amount": 29.99,
        "period": "monthly",
        "plan_id": "rocket",
        "description": "Posts illimités, tous les réseaux",
        "features": ["Posts illimités", "Tous les réseaux", "Analytics avancées", "Support prioritaire"],
        "max_posts": -1,  # -1 = unlimited
        "max_networks": -1
    },
    "pro_monthly": {
        "name": "Pro",
        "amount": 199.99, 
        "period": "monthly",
        "plan_id": "pro",
        "description": "Multi-comptes + fonctionnalités avancées",
        "features": ["Tout de Rocket", "Multi-comptes", "API accès", "Manager dédié"],
        "max_posts": -1,
        "max_networks": -1,
        "multi_accounts": True
    }
}

# Pydantic Models
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

class CheckoutRequest(BaseModel):
    package_id: str
    origin_url: str

class WebhookRequest(BaseModel):
    type: str
    data: Dict[str, Any]

# Helper function to get current user (temporary demo implementation)
async def get_current_user():
    """Temporary user implementation - replace with real auth when integrated"""
    return {
        "user_id": "demo-user-id",
        "email": "demo@claire-marcus.com", 
        "subscription_status": "trial"
    }

# Payment Routes

@payments_router.get("/packages")
async def get_subscription_packages():
    """Get available subscription packages for frontend display"""
    return {
        "packages": SUBSCRIPTION_PACKAGES,
        "currency": "EUR",
        "supported_methods": ["card", "apple_pay", "google_pay"] if EMERGENT_STRIPE_AVAILABLE else ["demo"]
    }

@payments_router.post("/v1/checkout/session")
async def create_checkout_session(request: CheckoutRequest):
    """Create Stripe checkout session with emergentintegrations"""
    
    if not EMERGENT_STRIPE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Payment system temporarily unavailable"
        )
    
    # Get current user (replace with real auth dependency)
    current_user = await get_current_user()
    
    try:
        # Validate package selection
        if request.package_id not in SUBSCRIPTION_PACKAGES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid package: {request.package_id}"
            )
        
        package = SUBSCRIPTION_PACKAGES[request.package_id]
        amount = package["amount"]  # Already in correct float format (14.99)
        
        # Initialize Stripe checkout with proper webhook URL
        webhook_url = f"{request.origin_url.rstrip('/')}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        # Create success and cancel URLs with dynamic origin
        success_url = f"{request.origin_url.rstrip('/')}/?session_id={{CHECKOUT_SESSION_ID}}&payment_success=true"
        cancel_url = f"{request.origin_url.rstrip('/')}/?payment_cancelled=true"
        
        # Prepare metadata for tracking
        metadata = {
            "user_id": current_user["user_id"],
            "package_id": request.package_id,
            "plan_name": package["name"],
            "billing_period": package["period"],
            "user_email": current_user.get("email", "")
        }
        
        # Create checkout session request
        checkout_request = CheckoutSessionRequest(
            amount=amount,
            currency="eur", 
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata
        )
        
        # Create the session
        session: CheckoutSessionResponse = await stripe_checkout.create_checkout_session(checkout_request)
        
        # MANDATORY: Create payment transaction record BEFORE redirecting user
        if db.is_connected():
            transaction = PaymentTransaction(
                user_id=current_user["user_id"],
                session_id=session.session_id,
                package_id=request.package_id,
                amount=amount,
                currency="eur",
                payment_status="pending",
                status="initiated",
                metadata=metadata
            )
            
            await db.db.payment_transactions.insert_one(transaction.dict())
            logging.info(f"Payment transaction created: {session.session_id} for user {current_user['user_id']}")
        
        return {
            "url": session.url,
            "session_id": session.session_id,
            "package": package["name"],
            "amount": amount,
            "currency": "EUR"
        }
        
    except Exception as e:
        logging.error(f"Error creating checkout session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create checkout session: {str(e)}"
        )

@payments_router.get("/v1/checkout/status/{session_id}")
async def get_checkout_status(session_id: str):
    """Get checkout session status and update payment record"""
    
    if not EMERGENT_STRIPE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Payment system unavailable")
    
    # Get current user
    current_user = await get_current_user()
    
    try:
        # Find payment transaction in database
        if db.is_connected():
            transaction = await db.db.payment_transactions.find_one({
                "session_id": session_id,
                "user_id": current_user["user_id"]
            })
            
            if not transaction:
                raise HTTPException(
                    status_code=404,
                    detail="Payment session not found"
                )
        else:
            # Demo mode fallback
            transaction = {
                "payment_status": "pending",
                "status": "initiated",
                "package_id": "starter_monthly",
                "amount": 14.99
            }
        
        # Initialize Stripe checkout to check status
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
        
        # Get status from Stripe
        checkout_status: CheckoutStatusResponse = await stripe_checkout.get_checkout_status(session_id)
        
        # Update database only if status changed and DB is connected
        if (db.is_connected() and 
            (checkout_status.payment_status != transaction["payment_status"] or 
             checkout_status.status != transaction["status"])):
            
            await db.db.payment_transactions.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "payment_status": checkout_status.payment_status,
                        "status": checkout_status.status,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            logging.info(f"Transaction updated: {session_id} - Status: {checkout_status.payment_status}")
        
        # Process successful payment (only once per session)
        if (checkout_status.payment_status == "paid" and 
            transaction.get("payment_status") != "paid"):
            
            await process_successful_payment(session_id, transaction, current_user)
        
        return {
            "session_id": session_id,
            "status": checkout_status.status,
            "payment_status": checkout_status.payment_status,
            "amount_total": checkout_status.amount_total / 100,  # Convert from cents
            "currency": checkout_status.currency.upper(),
            "metadata": checkout_status.metadata
        }
        
    except Exception as e:
        logging.error(f"Error getting checkout status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check payment status: {str(e)}"
        )

@payments_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks with proper signature verification"""
    
    if not EMERGENT_STRIPE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Webhook processing unavailable")
    
    try:
        # Get webhook body and signature
        body = await request.body()
        signature = request.headers.get("Stripe-Signature")
        
        if not signature:
            raise HTTPException(status_code=400, detail="Missing Stripe signature")
        
        # Initialize Stripe checkout for webhook handling
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
        
        # Handle webhook with emergentintegrations
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        logging.info(f"Webhook received: {webhook_response.event_type} for session {webhook_response.session_id}")
        
        # Process webhook based on event type
        if webhook_response.event_type == "checkout.session.completed":
            await handle_checkout_completed(webhook_response)
        elif webhook_response.event_type == "payment_intent.succeeded":
            await handle_payment_succeeded(webhook_response)
        
        return {"received": True, "event_type": webhook_response.event_type}
        
    except Exception as e:
        logging.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=400, detail="Webhook processing failed")

async def handle_checkout_completed(webhook_response):
    """Handle completed checkout session webhook"""
    try:
        if db.is_connected():
            # Update payment transaction
            await db.db.payment_transactions.update_one(
                {"session_id": webhook_response.session_id},
                {
                    "$set": {
                        "payment_status": webhook_response.payment_status,
                        "status": "completed",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            logging.info(f"Checkout completed webhook processed: {webhook_response.session_id}")
    
    except Exception as e:
        logging.error(f"Error handling checkout completed: {e}")

async def handle_payment_succeeded(webhook_response):
    """Handle successful payment webhook"""
    try:
        if db.is_connected():
            # Find and update the transaction
            transaction = await db.db.payment_transactions.find_one({
                "session_id": webhook_response.session_id
            })
            
            if transaction:
                await process_successful_payment(
                    webhook_response.session_id, 
                    transaction, 
                    {"user_id": transaction["user_id"]}
                )
        
        logging.info(f"Payment succeeded webhook processed: {webhook_response.session_id}")
        
    except Exception as e:
        logging.error(f"Error handling payment succeeded: {e}")

async def process_successful_payment(session_id: str, transaction: dict, user: dict):
    """Process successful payment and update user subscription (prevent double processing)"""
    try:
        # Get package details
        package = SUBSCRIPTION_PACKAGES[transaction["package_id"]]
        
        # Calculate subscription end date
        now = datetime.utcnow()
        if package["period"] == "yearly":
            end_date = now + timedelta(days=365)
        else:  # monthly
            end_date = now + timedelta(days=30)
        
        # Update user subscription (only if database connected)
        if db.is_connected():
            # Check if user subscription already updated for this session (prevent double processing)
            existing_payment = await db.db.payments.find_one({"stripe_session_id": session_id})
            if existing_payment:
                logging.info(f"Payment already processed for session: {session_id}")
                return
            
            # Update user subscription status
            await db.db.users.update_one(
                {"user_id": user["user_id"]},
                {
                    "$set": {
                        "subscription_status": "active",
                        "subscription_plan": package["plan_id"],
                        "subscription_ends_at": end_date,
                        "max_posts_per_month": package["max_posts"],
                        "max_networks": package["max_networks"],
                        "updated_at": now
                    }
                }
            )
            
            # Create payment record for admin tracking
            payment_record = {
                "id": str(uuid.uuid4()),
                "user_id": user["user_id"],
                "stripe_session_id": session_id,
                "amount": transaction["amount"],
                "currency": transaction["currency"],
                "status": "succeeded",
                "subscription_plan": package["name"],
                "billing_period": package["period"],
                "features": package["features"],
                "created_at": now
            }
            
            await db.db.payments.insert_one(payment_record)
            
            logging.info(f"Subscription activated for user {user['user_id']}: {package['name']} {package['period']} until {end_date}")
        
    except Exception as e:
        logging.error(f"Error processing successful payment: {e}")

# Additional utility endpoints

@payments_router.get("/my-subscription")
async def get_my_subscription():
    """Get current user's subscription details"""
    current_user = await get_current_user()
    
    try:
        if db.is_connected():
            # Get user's current subscription
            user_data = await db.db.users.find_one({"user_id": current_user["user_id"]})
            
            # Get latest payment
            latest_payment = await db.db.payments.find_one(
                {"user_id": current_user["user_id"]},
                sort=[("created_at", -1)]
            )
            
            if user_data:
                return {
                    "subscription_status": user_data.get("subscription_status", "trial"),
                    "subscription_plan": user_data.get("subscription_plan", "trial"),
                    "subscription_ends_at": user_data.get("subscription_ends_at"),
                    "max_posts_per_month": user_data.get("max_posts_per_month", 2),
                    "max_networks": user_data.get("max_networks", 1),
                    "latest_payment": latest_payment
                }
        
        # Demo mode fallback
        return {
            "subscription_status": "trial",
            "subscription_plan": "trial",
            "subscription_ends_at": datetime.utcnow() + timedelta(days=30),
            "max_posts_per_month": 2,
            "max_networks": 1,
            "latest_payment": None
        }
        
    except Exception as e:
        logging.error(f"Error getting subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to get subscription details")

@payments_router.post("/cancel-subscription")
async def cancel_subscription():
    """Cancel user's subscription (keeps active until period end)"""
    current_user = await get_current_user()
    
    try:
        if db.is_connected():
            user_data = await db.db.users.find_one({"user_id": current_user["user_id"]})
            
            if not user_data or user_data.get("subscription_status") != "active":
                raise HTTPException(status_code=400, detail="No active subscription to cancel")
            
            # Mark subscription as cancelled but keep it active until end date
            await db.db.users.update_one(
                {"user_id": current_user["user_id"]},
                {
                    "$set": {
                        "subscription_status": "cancelled",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return {
                "message": "Subscription cancelled successfully",
                "active_until": user_data.get("subscription_ends_at"),
                "note": "Your subscription will remain active until the end of the current billing period"
            }
        
        return {"message": "Subscription cancelled (demo mode)"}
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error cancelling subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")

# Health check for payment system
@payments_router.get("/health")
async def payments_health():
    """Health check for payment system"""
    return {
        "status": "healthy",
        "emergent_stripe": EMERGENT_STRIPE_AVAILABLE,
        "stripe_configured": bool(STRIPE_API_KEY),
        "database": db.is_connected(),
        "packages_available": len(SUBSCRIPTION_PACKAGES),
        "supported_currency": "EUR"
    }