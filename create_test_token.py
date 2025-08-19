#!/usr/bin/env python3
"""
Create a test JWT token for thumbnail testing
"""

import jwt
import os
from datetime import datetime, timedelta

# JWT Configuration (same as server.py)
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-this-in-production')
JWT_ALG = os.environ.get("JWT_ALG", "HS256")
JWT_TTL = int(os.environ.get("JWT_TTL_SECONDS", "604800"))  # 7 days
JWT_ISS = os.environ.get("JWT_ISS", "claire-marcus-api")

# Use the user ID from the media documents
USER_ID = "11d1e3d2-0223-4ddd-9407-74e0bb626818"

print("🔑 CREATING TEST JWT TOKEN")
print("=" * 50)
print(f"User ID: {USER_ID}")
print(f"JWT Secret: {JWT_SECRET[:10]}...")
print(f"JWT Algorithm: {JWT_ALG}")
print(f"JWT Issuer: {JWT_ISS}")

# Create token payload
now = datetime.utcnow()
payload = {
    "sub": USER_ID,
    "iss": JWT_ISS,
    "iat": now,
    "exp": now + timedelta(seconds=JWT_TTL)
}

# Generate token
token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
print(f"\n✅ Generated JWT Token:")
print(f"Bearer {token}")

# Verify token
try:
    decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG], issuer=JWT_ISS)
    print(f"\n✅ Token verification successful:")
    print(f"Subject: {decoded.get('sub')}")
    print(f"Issuer: {decoded.get('iss')}")
    print(f"Expires: {datetime.fromtimestamp(decoded.get('exp'))}")
except Exception as e:
    print(f"\n❌ Token verification failed: {e}")