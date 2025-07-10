"""User Management for MongoDB operations."""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
from flask import current_app

logger = logging.getLogger("assas_app")

class UserManager:
    """Manage user operations in MongoDB."""
    
    def __init__(self):
        """Initialize MongoDB connection."""
        try:
            self.client = MongoClient(current_app.config.get('MONGODB_URI', 'mongodb://localhost:27017/'))
            self.db = self.client[current_app.config.get('MONGODB_DB', 'assas')]
            self.users_collection = self.db['users']
            
            # Create indexes for better performance
            self.users_collection.create_index("email", unique=True)
            self.users_collection.create_index("username")
            self.users_collection.create_index("provider")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def get_all_users(self) -> List[Dict]:
        """Get all users from database."""
        try:
            users = list(self.users_collection.find({}))
            logger.info(f"Retrieved {len(users)} users from database")
            return users
        except Exception as e:
            logger.error(f"Error retrieving users: {e}")
            return []
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email address."""
        try:
            user = self.users_collection.find_one({"email": email})
            return user
        except Exception as e:
            logger.error(f"Error retrieving user by email {email}: {e}")
            return None
    
    def create_or_update_user(self, user_data: Dict) -> Dict:
        """Create new user or update existing user."""
        try:
            email = user_data.get('email')
            if not email:
                raise ValueError("Email is required for user creation")
            
            # Check if user exists
            existing_user = self.get_user_by_email(email)
            
            # Prepare user document
            user_doc = {
                'username': user_data.get('username'),
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
            
            if existing_user:
                # Update existing user
                user_doc['login_count'] = existing_user.get('login_count', 0) + 1
                
                result = self.users_collection.update_one(
                    {"email": email},
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