import logging

from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
from pymongo import MongoClient

auth = HTTPBasicAuth()

logger = logging.getLogger('assas_app')

# MongoDB connection setup
client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB connection string
db = client['assas']  # Database name
users_collection = db['users']  # Collection name

users = users_collection.find()

@auth.verify_password
def verify_password(username_or_email, password):
    """
    Verifies the username or email and password for authentication.
    """
    logger.info(f'Verifying user/email {username_or_email} with password {password}.')
    
    user = users_collection.find_one({
        "$or": [
            {"username": username_or_email},
            {"email": username_or_email}
        ]
    })
    
    if user and check_password_hash(user['password'], password):
        session['user'] = user['username']  # Store the username in the session
        return user['username']  # Return the username if authentication is successful
    
    logger.error('Invalid username/email or password.')
    return None

def is_authenticated():
    """
    Checks if the user is authenticated.
    """
    is_auth = 'user' in session
    logger.info(f'User authentication status: {is_auth}')
    
    return is_auth
    
def get_current_user():
    
    return session.get('user', None)