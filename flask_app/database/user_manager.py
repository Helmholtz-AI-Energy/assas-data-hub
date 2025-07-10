"""User Management for MongoDB operations."""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
from flask import current_app
import os

logger = logging.getLogger("assas_app")

class UserManager:
    """Manage user operations in MongoDB."""
    
    def __init__(self):
        """Initialize UserManager with MongoDB connection."""
        try:
            # MongoDB connection
            connection_string = "mongodb://localhost:27017/"
            
            # MANUAL FIX: Use the database/collection where users actually are
            # Update these based on your debug script results:
            db_name = 'assas'  # Or whatever the debug script shows
            collection_name = 'users'  # Or whatever has your users
            
            self.client = MongoClient(connection_string)
            self.db = self.client[db_name]
            self.users_collection = self.db[collection_name]
            
            # Check connection without creating conflicting indexes
            self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB: {connection_string}")
            
            # Only create indexes if they don't exist or are different
            self._ensure_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def _ensure_indexes(self):
        """Ensure required indexes exist, handling conflicts gracefully."""
        try:
            existing_indexes = list(self.users_collection.list_indexes())
            existing_index_names = {idx['name'] for idx in existing_indexes}
            
            # Check if we need to create unique email index
            email_index_exists = any(
                idx.get('key', {}).get('email') == 1 and idx.get('unique', False)
                for idx in existing_indexes
            )
            
            if not email_index_exists:
                try:
                    self.users_collection.create_index("email", unique=True, name="email_unique_idx")
                    logger.info("Created unique email index")
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        logger.warning(f"Could not create email index: {e}")
            
            # Check if we need to create unique username index
            username_index_exists = any(
                idx.get('key', {}).get('username') == 1 and idx.get('unique', False)
                for idx in existing_indexes
            )
            
            if not username_index_exists:
                try:
                    self.users_collection.create_index("username", unique=True, name="username_unique_idx")
                    logger.info("Created unique username index")
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        logger.warning(f"Could not create username index: {e}")
                        
        except Exception as e:
            logger.warning(f"Could not ensure indexes: {e}")
            # Don't raise - the app can work without perfect indexes
    
    def get_all_users(self) -> List[Dict]:
        """Get all users from database."""
        try:
            logger.info("Starting get_all_users() method")
            logger.info(f"Collection: {self.users_collection}")
            logger.info(f"Database: {self.db}")
            
            # First, let's check if the collection exists and has documents
            collection_names = self.db.list_collection_names()
            logger.info(f"Available collections: {collection_names}")
            
            if 'users' not in collection_names:
                logger.error("Users collection does not exist!")
                return []
            
            # Count documents first
            count = self.users_collection.count_documents({})
            logger.info(f"Total documents in users collection: {count}")
            
            if count == 0:
                logger.warning("Users collection is empty!")
                return []
            
            # Get the users
            logger.info("Executing find() query...")
            users_cursor = self.users_collection.find({})
            users = list(users_cursor)
            
            logger.info(f"Retrieved {len(users)} users from database")
            logger.info(f"First user keys (if any): {list(users[0].keys()) if users else 'No users'}")
            
            return users
        
        except Exception as e:
            logger.error(f"Error retrieving users: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email address."""
        try:
            user = self.users_collection.find_one({"email": email.lower()})
            return user
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username."""
        try:
            user = self.users_collection.find_one({"username": username})
            return user
        except Exception as e:
            logger.error(f"Error retrieving user by username {username}: {e}")
            return None
    
    def get_users_with_basic_auth(self) -> List[Dict]:
        """Get all users with basic auth enabled."""
        try:
            users = list(self.users_collection.find({
                "basic_auth_password_hash": {"$exists": True, "$ne": None}
            }))
            logger.info(f"Found {len(users)} users with basic auth")
            return users
        except Exception as e:
            logger.error(f"Error retrieving basic auth users: {e}")
            return []
    
    def create_or_update_user(self, user_data: Dict) -> Dict:
        """Create new user or update existing user."""
        try:
            email = user_data.get('email')
            username = user_data.get('username')
            
            if not email:
                raise ValueError("Email is required for user creation")
            
            # Check if user exists (by email or username for basic auth)
            existing_user = None
            if username and user_data.get('provider') == 'basic_auth':
                existing_user = self.get_user_by_username(username)
            if not existing_user:
                existing_user = self.get_user_by_email(email)
            
            # Prepare user document
            user_doc = {
                'username': username,
                'email': email,
                'name': user_data.get('name'),
                'provider': user_data.get('provider'),
                'roles': user_data.get('roles', ['viewer']),
                'is_active': user_data.get('is_active', True),
                'last_login': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            # Add provider-specific data
            if user_data.get('provider') == 'github':
                user_doc.update({
                    'github_id': user_data.get('github_id'),
                    'avatar_url': user_data.get('avatar_url'),
                    'github_profile': user_data.get('github_profile')
                })
            elif user_data.get('provider') == 'bwidm':
                user_doc.update({
                    'bwidm_sub': user_data.get('bwidm_sub'),
                    'institution': user_data.get('institution'),
                    'entitlements': user_data.get('entitlements', []),
                    'affiliations': user_data.get('affiliations', [])
                })
            elif user_data.get('provider') == 'basic_auth':
                # Add basic auth specific fields
                if user_data.get('basic_auth_password_hash'):
                    user_doc['basic_auth_password_hash'] = user_data['basic_auth_password_hash']
            
            if existing_user:
                # Update existing user
                user_doc['login_count'] = existing_user.get('login_count', 0) + 1
                
                result = self.users_collection.update_one(
                    {"_id": existing_user["_id"]},
                    {"$set": user_doc}
                )
                
                if result.modified_count > 0:
                    logger.info(f"Updated user: {email}")
                    return self.get_user_by_email(email)
                else:
                    logger.warning(f"No changes made to user: {email}")
                    return existing_user
            else:
                # Create new user
                user_doc.update({
                    'created_at': datetime.utcnow(),
                    'login_count': 1
                })
                
                result = self.users_collection.insert_one(user_doc)
                logger.info(f"Created new user: {email} with ID: {result.inserted_id}")
                
                return self.get_user_by_id(result.inserted_id)
                
        except Exception as e:
            logger.error(f"Error creating/updating user: {e}")
            raise
    
    def update_basic_auth_password(self, username: str, password_hash: str) -> bool:
        """Update basic auth password for user."""
        try:
            result = self.users_collection.update_one(
                {"username": username},
                {
                    "$set": {
                        "basic_auth_password_hash": password_hash,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Updated basic auth password for user: {username}")
                return True
            else:
                logger.warning(f"No password update for user: {username}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating basic auth password for {username}: {e}")
            return False
    
    def update_last_login(self, username: str) -> bool:
        """Update last login timestamp."""
        try:
            result = self.users_collection.update_one(
                {"username": username},
                {
                    "$set": {"last_login": datetime.utcnow()},
                    "$inc": {"login_count": 1}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating last login for {username}: {e}")
            return False
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID."""
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            user = self.users_collection.find_one({"_id": user_id})
            return user
        except Exception as e:
            logger.error(f"Error retrieving user by ID {user_id}: {e}")
            return None
        
    def create_user(self, user_data: Dict[str, Any]) -> bool:
        """Create a new user in the database."""
        try:
            # Validate required fields
            required_fields = ['username', 'email', 'provider', 'roles']
            for field in required_fields:
                if field not in user_data:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Check for existing username
            if self.get_user_by_username(user_data['username']):
                logger.error(f"Username {user_data['username']} already exists")
                return False
            
            # Check for existing email
            if self.get_user_by_email(user_data['email']):
                logger.error(f"Email {user_data['email']} already exists")
                return False
            
            # Insert user
            result = self.users_collection.insert_one(user_data)
            
            if result.inserted_id:
                logger.info(f"Created user: {user_data['username']} with ID: {result.inserted_id}")
                return True
            else:
                logger.error("Failed to insert user")
                return False
                
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False