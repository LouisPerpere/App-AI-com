"""
Shared authentication module for all backend services
Ensures consistent JWT validation across all endpoints
"""
import os
import jwt
from fastapi import Header, HTTPException
from typing import Optional

# JWT Configuration - SHARED across all modules
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-this-in-production')
JWT_ALG = os.environ.get("JWT_ALG", "HS256")
JWT_TTL = int(os.environ.get("JWT_TTL_SECONDS", "604800"))  # 7 days
JWT_ISS = os.environ.get("JWT_ISS", "claire-marcus-api")

def get_current_user_id_robust(authorization: Optional[str] = Header(None)) -> str:
    """
    Robust JWT token validation - NO FALLBACK TO DEMO
    Used by all modules to ensure consistent authentication
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Missing bearer token")
    
    token = authorization.split(" ", 1)[1]
    
    try:
        payload = jwt.decode(
            token, 
            JWT_SECRET, 
            algorithms=[JWT_ALG], 
            options={"require": ["sub", "exp"]}, 
            issuer=JWT_ISS
        )
        
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(401, "Invalid token: sub missing")
        
        return sub
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(401, f"Invalid token: {e}")

print("✅ Shared security module loaded with robust JWT authentication")