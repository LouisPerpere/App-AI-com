"""
Database module for Claire et Marcus
Handles MongoDB connections and operations
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import bcrypt
import jwt
from bson import ObjectId
import urllib.parse

class DatabaseManager:
    """MongoDB database manager for Claire et Marcus"""
    
    def __init__(self):
        """Initialize database connection"""
        self.mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        
        # Fix MongoDB URL encoding for special characters (Render compatibility)
        if "mongodb+srv://" in self.mongo_url or "@" in self.mongo_url:
            # Parse and re-encode URL components to handle special characters
            try:
                from urllib.parse import urlparse, urlunparse, quote_plus
                parsed = urlparse(self.mongo_url)
                if parsed.username and parsed.password:
                    # Re-encode username and password
                    encoded_username = quote_plus(parsed.username)
                    encoded_password = quote_plus(parsed.password)
                    # Reconstruct URL with encoded credentials
                    netloc = f"{encoded_username}:{encoded_password}@{parsed.hostname}"
                    if parsed.port:
                        netloc += f":{parsed.port}"
                    self.mongo_url = urlunparse((
                        parsed.scheme, netloc, parsed.path, 
                        parsed.params, parsed.query, parsed.fragment
                    ))
                    print(f"✅ MongoDB URL credentials encoded for RFC 3986 compliance")
            except Exception as e:
                print(f"⚠️ MongoDB URL encoding warning: {e}")
        
        self.db_name = os.getenv("DB_NAME", "claire_marcus")
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
        
        try:
            self.client = MongoClient(self.mongo_url)
            self.db = self.client[self.db_name]
            
            # Test connection
            self.client.admin.command('ping')
            print(f"✅ MongoDB connected successfully to {self.db_name}")
            
            # Initialize collections
            self._initialize_collections()
            
        except ConnectionFailure as e:
            print(f"❌ MongoDB connection failed: {e}")
            self.client = None
            self.db = None
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
            self.client = None
            self.db = None
    
    def _initialize_collections(self):
        """Initialize database collections with indexes"""
        if self.db is None:
            return
        
        collections = {
            'users': [
                ('email', 1),  # Unique index on email
                ('user_id', 1)  # Index on user_id
            ],
            'business_profiles': [
                ('user_id', 1),
                ('business_id', 1)
            ],
            'content_notes': [
                ('user_id', 1),
                ('created_at', -1)  # Latest first
            ],
            'generated_posts': [
                ('user_id', 1),
                ('status', 1),
                ('created_at', -1)
            ],
            'subscriptions': [
                ('user_id', 1),
                ('status', 1)
            ]
        }
        
        for collection_name, indexes in collections.items():
            collection = self.db[collection_name]
            for index_fields in indexes:
                try:
                    if index_fields[0] == 'email':
                        collection.create_index(index_fields, unique=True)
                    else:
                        collection.create_index(index_fields)
                except Exception as e:
                    print(f"Index creation warning for {collection_name}: {e}")
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self.client is not None and self.db is not None
    
    # User Management
    def create_user(self, email: str, password: str, first_name: str = None, 
                   last_name: str = None, business_name: str = None) -> Dict[str, Any]:
        """Create a new user"""
        if not self.is_connected():
            raise Exception("Database not connected")
        
        # Check if user already exists
        existing_user = self.db.users.find_one({"email": email})
        if existing_user:
            raise Exception("User already exists")
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user document
        user_id = str(uuid.uuid4())
        business_name = business_name or f"{first_name or ''} {last_name or ''}".strip() or "Mon entreprise"
        
        user_doc = {
            "user_id": user_id,
            "email": email,
            "password_hash": password_hash.decode('utf-8'),
            "first_name": first_name,
            "last_name": last_name,
            "business_name": business_name,
            "subscription_status": "trial",
            "trial_days_remaining": 30,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        }
        
        # Insert user
        result = self.db.users.insert_one(user_doc)
        
        # Create default business profile
        self._create_default_business_profile(user_id, business_name)
        
        # Generate JWT tokens
        access_token = self._generate_access_token(user_id, email)
        refresh_token = self._generate_refresh_token(user_id, email)
        
        return {
            "user_id": user_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "business_name": business_name,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "subscription_status": "trial",
            "trial_days_remaining": 30
        }
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return user data with tokens"""
        if not self.is_connected():
            raise Exception("Database not connected")
        
        # Find user
        user = self.db.users.find_one({"email": email, "is_active": True})
        if not user:
            return None
        
        # Check password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return None
        
        # Update last login
        self.db.users.update_one(
            {"user_id": user["user_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        # Generate JWT tokens
        access_token = self._generate_access_token(user["user_id"], user["email"])
        refresh_token = self._generate_refresh_token(user["user_id"], user["email"])
        
        return {
            "user_id": user["user_id"],
            "email": user["email"],
            "first_name": user.get("first_name"),
            "last_name": user.get("last_name"),
            "business_name": user.get("business_name"),
            "access_token": access_token,
            "refresh_token": refresh_token,
            "subscription_status": user.get("subscription_status", "trial"),
            "trial_days_remaining": user.get("trial_days_remaining", 0),
            "expires_in": 3600
        }
    
    def get_user_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user info from JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            user_id = payload.get("user_id")
            
            if not user_id:
                return None
            
            user = self.db.users.find_one({"user_id": user_id, "is_active": True})
            if not user:
                return None
            
            return {
                "user_id": user["user_id"],
                "email": user["email"],
                "first_name": user.get("first_name"),
                "last_name": user.get("last_name"),
                "business_name": user.get("business_name"),
                "subscription_status": user.get("subscription_status", "trial"),
                "trial_days_remaining": user.get("trial_days_remaining", 0),
                "created_at": user.get("created_at", datetime.utcnow()).isoformat()
            }
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception as e:
            print(f"Token validation error: {e}")
            return None
    
    def _generate_access_token(self, user_id: str, email: str) -> str:
        """Generate JWT access token"""
        payload = {
            "user_id": user_id,
            "email": email,
            "type": "access",
            "exp": datetime.utcnow() + timedelta(minutes=30),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")
    
    def _generate_refresh_token(self, user_id: str, email: str) -> str:
        """Generate JWT refresh token"""
        payload = {
            "user_id": user_id,
            "email": email,
            "type": "refresh",
            "exp": datetime.utcnow() + timedelta(days=30),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")
    
    def _create_default_business_profile(self, user_id: str, business_name: str):
        """Create default business profile for new user"""
        profile_doc = {
            "profile_id": str(uuid.uuid4()),
            "user_id": user_id,
            "business_name": business_name,
            "business_type": "service",
            "business_description": "",  # Ajouté pour correspondre au modèle Pydantic
            "target_audience": "Clients locaux",
            "brand_tone": "professionnel",
            "business_objective": "equilibre",  # AJOUT CRITIQUE: Objectif par défaut
            "posting_frequency": "weekly",
            "preferred_platforms": ["Facebook", "Instagram"],
            "budget_range": "",  # Ajouté pour correspondre au modèle Pydantic
            "email": "",  # Ajouté pour correspondre au modèle Pydantic
            "hashtags_primary": [],
            "hashtags_secondary": [],
            "website_url": "",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        self.db.business_profiles.insert_one(profile_doc)
    
    # Business Profile Management
    def get_business_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get business profile for user"""
        if not self.is_connected():
            return None
        
        profile = self.db.business_profiles.find_one({"user_id": user_id})
        if profile:
            profile.pop('_id', None)  # Remove MongoDB ObjectId
        
        return profile
    
    def update_business_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Update business profile with upsert capability"""
        if not self.is_connected():
            return False
        
        profile_data["updated_at"] = datetime.utcnow()
        
        # Use upsert to create profile if it doesn't exist
        result = self.db.business_profiles.update_one(
            {"user_id": user_id},
            {"$set": profile_data},
            upsert=True
        )
        
        # Return True if document was modified OR upserted
        return result.modified_count > 0 or result.upserted_id is not None
    
    # Content Notes Management
    def create_note(self, user_id: str, content: str, description: str = None, priority: str = "normal", 
                   is_monthly_note: bool = False, note_month: Optional[int] = None, note_year: Optional[int] = None) -> Dict[str, Any]:
        """Create a content note"""
        if not self.is_connected():
            raise Exception("Database not connected")
        
        note_data = {
            "note_id": str(uuid.uuid4()),
            "owner_id": user_id,
            "description": description,
            "content": content,
            "priority": priority,
            "is_monthly_note": is_monthly_note,
            "note_month": note_month,
            "note_year": note_year,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.db.content_notes.insert_one(note_data)
        note_data.pop('_id', None)
        
        return note_data
    
    def get_notes(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all notes for user"""
        if not self.is_connected():
            return []
        
        notes = list(self.db.content_notes.find(
            {"owner_id": user_id},
            {"_id": 0}
        ).sort("created_at", -1))
        
        return notes
    
    def delete_note(self, user_id: str, note_id: str) -> bool:
        """Delete a note"""
        if not self.is_connected():
            return False
        
        result = self.db.content_notes.delete_one({
            "owner_id": user_id,
            "note_id": note_id
        })
        
        return result.deleted_count > 0

    def cleanup_expired_periodic_notes(self) -> Dict[str, Any]:
        """Clean up expired periodic notes (specific month notes past their expiration date)
        
        Notes for a specific month should be deleted on the 5th of the following month.
        For example: January 2025 notes should be deleted on February 5, 2025.
        """
        if not self.is_connected():
            return {"deleted_count": 0, "error": "Database not connected"}
        
        from datetime import datetime, timedelta
        import calendar
        
        current_date = datetime.utcnow()
        current_month = current_date.month
        current_year = current_date.year
        current_day = current_date.day
        
        # Only perform cleanup on or after the 5th of the month
        if current_day < 5:
            return {"deleted_count": 0, "reason": f"Cleanup only runs on/after 5th of month, today is {current_day}th"}
        
        # Calculate which month's notes should be deleted
        # If today is February 5+, delete January notes
        # If today is March 5+, delete February notes, etc.
        
        if current_month == 1:
            # January: delete December notes from previous year
            target_month = 12
            target_year = current_year - 1
        else:
            # Other months: delete previous month's notes
            target_month = current_month - 1
            target_year = current_year
        
        try:
            # Find specific month notes that should be deleted
            # Criteria: is_monthly_note = false, note_month = target_month, note_year = target_year
            delete_filter = {
                "is_monthly_note": {"$ne": True},  # Not monthly notes (those should persist)
                "note_month": target_month,
                "note_year": target_year
            }
            
            # Get notes that will be deleted for logging
            notes_to_delete = list(self.db.content_notes.find(delete_filter, {"note_id": 1, "description": 1, "owner_id": 1}))
            
            # Perform the deletion
            result = self.db.content_notes.delete_many(delete_filter)
            
            month_names = [
                "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
                "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
            ]
            target_month_name = month_names[target_month - 1]
            
            cleanup_log = {
                "deleted_count": result.deleted_count,
                "target_month": target_month,
                "target_year": target_year,
                "target_month_name": target_month_name,
                "current_date": current_date.isoformat(),
                "deleted_notes": [
                    {
                        "note_id": note.get("note_id"),
                        "title": note.get("description", "Sans titre"),
                        "owner_id": note.get("owner_id")
                    } for note in notes_to_delete
                ],
                "success": True
            }
            
            print(f"🗑️ Notes cleanup: Deleted {result.deleted_count} notes from {target_month_name} {target_year}")
            for note in notes_to_delete:
                print(f"   - Deleted: '{note.get('description', 'Sans titre')}' (owner: {note.get('owner_id')})")
            
            return cleanup_log
            
        except Exception as e:
            error_log = {
                "deleted_count": 0,
                "error": str(e),
                "target_month": target_month,
                "target_year": target_year,
                "current_date": current_date.isoformat(),
                "success": False
            }
            print(f"❌ Error during notes cleanup: {e}")
            return error_log
    
    # Generated Posts Management
    def create_generated_post(self, user_id: str, content: str, platform: str, 
                            hashtags: List[str] = None) -> Dict[str, Any]:
        """Create a generated post"""
        if not self.is_connected():
            raise Exception("Database not connected")
        
        post_doc = {
            "post_id": str(uuid.uuid4()),
            "user_id": user_id,
            "content": content,
            "platform": platform,
            "status": "generated",
            "hashtags": hashtags or [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        self.db.generated_posts.insert_one(post_doc)
        post_doc.pop('_id', None)
        
        return post_doc
    
    def get_generated_posts(self, user_id: str, status: str = None) -> List[Dict[str, Any]]:
        """Get generated posts for user"""
        if not self.is_connected():
            return []
        
        filter_query = {"user_id": user_id}
        if status:
            filter_query["status"] = status
        
        posts = list(self.db.generated_posts.find(
            filter_query,
            {"_id": 0}
        ).sort("created_at", -1))
        
        return posts
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            print("🔒 Database connection closed")

# Global database instance
db_manager = None

def get_database() -> DatabaseManager:
    """Get database instance"""
    global db_manager
    if not db_manager:
        db_manager = DatabaseManager()
    return db_manager

def close_database():
    """Close database connection"""
    global db_manager
    if db_manager:
        db_manager.close()
        db_manager = None