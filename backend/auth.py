from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
import logging
from pydantic import BaseModel, EmailStr, Field
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# JWT Configuration selon plan ChatGPT
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-this-in-production')
JWT_ALG = os.environ.get("JWT_ALG", "HS256")
JWT_TTL = int(os.environ.get("JWT_TTL_SECONDS", "604800"))  # 7 jours
JWT_ISS = os.environ.get("JWT_ISS", "claire-marcus-api")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Pydantic Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    hashed_password: str
    first_name: str
    last_name: str
    is_active: bool = True
    is_admin: bool = False
    business_profile_id: Optional[str] = None
    subscription_status: str = "trial"  # trial, active, expired, cancelled, free
    subscription_plan: str = "starter"  # starter, pro, enterprise, trial, free
    trial_ends_at: Optional[datetime] = None
    trial_end_date: Optional[datetime] = None  # For compatibility
    subscription_ends_at: Optional[datetime] = None
    posts_this_month: int = 0
    max_posts_per_month: int = 10
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    is_admin: bool
    business_profile_id: Optional[str]
    subscription_status: str
    subscription_plan: str
    created_at: datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

# Utility Functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(seconds=JWT_TTL)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALG)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(seconds=JWT_TTL)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALG)
    return encoded_jwt

def create_reset_token(email: str):
    """Create password reset token"""
    to_encode = {"email": email, "type": "reset"}
    expire = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALG)
    return encoded_jwt

async def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email"""
    user_data = await db.users.find_one({"email": email})
    if user_data:
        return User(**user_data)
    return None

async def get_user_by_id(user_id: str) -> Optional[User]:
    """Get user by ID"""
    user_data = await db.users.find_one({"id": user_id})
    if user_data:
        return User(**user_data)
    return None

async def create_user(user_data: UserCreate) -> User:
    """Create a new user with trial prevention"""
    try:
        # Check if email already exists in users table
        existing_user = await get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un compte existe déjà avec cet email"
            )
        
        # Check if email exists in trial_emails_used collection (prevents re-trials)
        used_email = await db.trial_emails_used.find_one({"email": user_data.email})
        if used_email:
            # User already had a trial, register but without trial status
            subscription_status = "free"
            subscription_plan = "free"
            trial_end_date = None
            trial_ends_at = None
            max_posts_per_month = 0
        else:
            # First time registration, grant trial
            subscription_status = "trial"
            subscription_plan = "trial"
            trial_end_date = datetime.utcnow() + timedelta(days=30)
            trial_ends_at = trial_end_date
            max_posts_per_month = 10
            
            # Record this email as having used trial
            await db.trial_emails_used.insert_one({
                "email": user_data.email,
                "first_trial_date": datetime.utcnow(),
                "created_at": datetime.utcnow()
            })
        
        # Create user
        user = User(
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            subscription_status=subscription_status,
            subscription_plan=subscription_plan,
            trial_end_date=trial_end_date,
            trial_ends_at=trial_ends_at,
            posts_this_month=0,
            max_posts_per_month=max_posts_per_month
        )
        
        # Save to database
        await db.users.insert_one(user.dict())
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création du compte"
        )

async def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate user credentials"""
    user = await get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    
    # Update last login
    await db.users.update_one(
        {"id": user.id},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    return user

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALG])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if email is None or token_type != "access":
            raise credentials_exception
            
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_email(email=token_data.email)
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Compte désactivé"
        )
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Utilisateur inactif")
    return current_user

async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current admin user"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Droits administrateur requis"
        )
    return current_user

def check_subscription_status(user: User) -> dict:
    """Check and return subscription status"""
    now = datetime.utcnow()
    
    # Check trial period
    if user.subscription_status == "trial" and user.trial_ends_at:
        if now > user.trial_ends_at:
            return {
                "status": "trial_expired",
                "active": False,
                "days_left": 0,
                "message": "Votre période d'essai a expiré"
            }
        else:
            days_left = (user.trial_ends_at - now).days
            return {
                "status": "trial",
                "active": True,
                "days_left": days_left,
                "message": f"Période d'essai - {days_left} jours restants"
            }
    
    # Check active subscription
    if user.subscription_status == "active" and user.subscription_ends_at:
        if now > user.subscription_ends_at:
            return {
                "status": "expired",
                "active": False,
                "days_left": 0,
                "message": "Votre abonnement a expiré"
            }
        else:
            days_left = (user.subscription_ends_at - now).days
            return {
                "status": "active",
                "active": True,
                "days_left": days_left,
                "message": f"Abonnement {user.subscription_plan} actif"
            }
    
    return {
        "status": user.subscription_status,
        "active": user.subscription_status == "active",
        "days_left": 0,
        "message": "Statut indéterminé"
    }