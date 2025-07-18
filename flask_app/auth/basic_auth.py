"""HTTP Basic Authentication module."""

import logging
import hashlib
import secrets
from typing import Dict, Optional, Tuple
from flask import Blueprint, request, session, redirect, url_for, flash, render_template, current_app, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from bson import ObjectId
import json

from ..database.user_manager import UserManager
from ..auth_utils import get_current_user

logger = logging.getLogger("assas_app")

# HTTP Basic Auth Blueprint
basic_auth_bp = Blueprint('basic_auth', __name__, url_prefix='/auth/basic')

# Initialize HTTP Basic Auth
http_basic_auth = HTTPBasicAuth()

class BasicAuthUserManager:
    """Manage HTTP Basic Auth users."""
    
    @staticmethod
    def get_basic_auth_users() -> Dict[str, Dict]:
        """Get basic auth users from configuration and MongoDB database."""
        all_users = {}
        
        # 1. Load static users from configuration (for emergency access)
        static_users = current_app.config.get('BASIC_AUTH_USERS', {})
        all_users.update(static_users)
        logger.info(f"Loaded {len(static_users)} static basic auth users from config")
        
        # 2. Load dynamic users from MongoDB database
        try:
            user_manager = UserManager()
            
            # Get users with basic auth password hash
            db_users_with_basic_auth = user_manager.get_users_with_basic_auth()
            logger.info(f"Found {len(db_users_with_basic_auth)} users with basic auth passwords in database")
            
            for user in db_users_with_basic_auth:
                username = user.get('username')
                if username and user.get('basic_auth_password_hash'):
                    all_users[username] = {
                        'password_hash': user['basic_auth_password_hash'],
                        'roles': user.get('roles', ['viewer']),
                        'email': user.get('email'),
                        'name': user.get('name'),
                        'is_active': user.get('is_active', True),
                        'source': 'database',
                        'user_data': user
                    }
            
            # 3. Also check OAuth users who might want to use basic auth
            # Allow OAuth users to authenticate with a generated basic auth password
            all_oauth_users = user_manager.get_all_users()
            oauth_basic_count = 0
            
            for user in all_oauth_users:
                username = user.get('username')
                email = user.get('email')
                
                # Skip if already has basic auth or no username
                if not username or username in all_users:
                    continue
                
                # Check if user has OAuth provider but wants basic auth access
                if user.get('provider') in ['github', 'bwidm']:
                    # Generate a basic auth entry for OAuth users (they need to set password first)
                    temp_basic_auth = user.get('temp_basic_auth_password_hash')
                    if temp_basic_auth:
                        all_users[username] = {
                            'password_hash': temp_basic_auth,
                            'roles': user.get('roles', ['viewer']),
                            'email': email,
                            'name': user.get('name'),
                            'is_active': user.get('is_active', True),
                            'source': 'oauth_with_basic',
                            'user_data': user
                        }
                        oauth_basic_count += 1
            
            logger.info(f"Found {oauth_basic_count} OAuth users with basic auth enabled")
            logger.info(f"Total basic auth users available: {len(all_users)}")
            
            return all_users
            
        except Exception as e:
            logger.error(f"Error getting basic auth users from database: {e}")
            # Return at least the static users if database fails
            return static_users
    
    @staticmethod
    def verify_password(username: str, password: str) -> bool:
        """Verify username and password against all sources."""
        users = BasicAuthUserManager.get_basic_auth_users()
        
        if username not in users:
            logger.warning(f"Basic auth attempt for unknown user: {username}")
            return False
        
        user_data = users[username]
        
        # Check if user is active
        if not user_data.get('is_active', True):
            logger.warning(f"Basic auth attempt for inactive user: {username}")
            return False
        
        # Verify password hash
        password_hash = user_data.get('password_hash')
        if password_hash and check_password_hash(password_hash, password):
            source = user_data.get('source', 'config')
            logger.info(f"Basic auth successful for user: {username} (source: {source})")
            
            # Store authenticated user data for later retrieval
            http_basic_auth.authenticated_user = user_data
            return True
        
        logger.warning(f"Basic auth failed for user: {username}")
        return False
    
    @staticmethod
    def get_user_data(username: str) -> Optional[Dict]:
        """Get user data for authenticated user."""
        users = BasicAuthUserManager.get_basic_auth_users()
        return users.get(username)
    
    @staticmethod
    def find_user_by_email(email: str) -> Optional[Dict]:
        """Find user by email address for password reset etc."""
        try:
            user_manager = UserManager()
            return user_manager.get_user_by_email(email)
        except Exception as e:
            logger.error(f"Error finding user by email {email}: {e}")
            return None

# HTTP Basic Auth callback
@http_basic_auth.verify_password
def verify_password(username: str, password: str) -> str:
    """Verify password for HTTP Basic Auth."""
    if BasicAuthUserManager.verify_password(username, password):
        return username  # Return username if verified
    return None

class BasicAuthSession:
    """Manage session for Basic Auth users."""
    
    @staticmethod
    def create_basic_auth_session(username: str) -> None:
        """Create session for Basic Auth user."""
        user_data = BasicAuthUserManager.get_user_data(username)
        
        if not user_data:
            logger.error(f"No user data found for basic auth user: {username}")
            return
        
        session.permanent = True
        
        # Get full user data from database if available
        full_user_data = user_data.get('user_data', {})
        source = user_data.get('source', 'config')
        
        # Create session similar to OAuth
        session['user'] = {
            'id': full_user_data.get('_id', f"basic_{username}"),
            'username': username,
            'email': user_data.get('email', f"{username}@local"),
            'name': user_data.get('name', username),
            'provider': 'basic_auth',
            'authenticated': True,
            'roles': user_data.get('roles', ['viewer']),
            'auth_method': 'basic_auth',
            'auth_source': source,
            'mongodb_id': str(full_user_data.get('_id')) if full_user_data.get('_id') else None,
            'avatar_url': full_user_data.get('avatar_url'),  # In case OAuth user
            'original_provider': full_user_data.get('provider')  # Track original OAuth provider
        }
        
        # Update login count in database if user exists in DB
        try:
            user_manager = UserManager()
            if source in ['database', 'oauth_with_basic']:
                user_manager.update_last_login(username)
                logger.info(f"Updated login count for database user: {username}")
        except Exception as e:
            logger.warning(f"Could not update login for basic auth user {username}: {e}")
        
        logger.info(f"Created basic auth session for user: {username} (source: {source})")

# Update your login handler to convert ObjectId to string

def convert_objectid_to_string(obj):
    """Recursively convert ObjectId objects to strings for JSON serialization."""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {key: convert_objectid_to_string(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_string(item) for item in obj]
    else:
        return obj

# Routes
@basic_auth_bp.route('/login', methods=['GET', 'POST'])
def basic_login():
    """Basic Auth login form."""
    if get_current_user():
        return redirect('/assas_app/')
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please provide both username and password', 'error')
            return render_template('auth/basic_login.html')
        
        # Try authentication
        if BasicAuthUserManager.verify_password(username, password):
            BasicAuthSession.create_basic_auth_session(username)
            
            # Get user data to show personalized message
            user_data = BasicAuthUserManager.get_user_data(username)
            source = user_data.get('source', 'config')
            
            if source == 'database':
                flash(f'Welcome back, {username}! (Database user)', 'success')
            elif source == 'oauth_with_basic':
                flash(f'Welcome back, {username}! (OAuth user with basic auth)', 'success')
            else:
                flash(f'Welcome back, {username}!', 'success')
            
            # Redirect to intended page or home
            next_page = session.pop('next_url', None)
            return redirect(next_page or '/assas_app/')
        else:
            flash('Invalid username or password', 'error')
            return render_template('auth/basic_login.html')
    
    return render_template('auth/basic_login.html')

@basic_auth_bp.route('/set-password', methods=['GET', 'POST'])
def set_basic_auth_password():
    """Allow OAuth users to set a basic auth password."""
    current_user = get_current_user()
    
    if not current_user:
        flash('Please log in first', 'error')
        return redirect('/auth/login')
    
    # Only allow OAuth users to set basic auth password
    if current_user.get('provider') not in ['github', 'bwidm']:
        flash('This feature is only available for OAuth users', 'error')
        return redirect('/assas_app/profile')
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not password or not confirm_password:
            flash('Both password fields are required', 'error')
            return render_template('auth/set_basic_password.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/set_basic_password.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return render_template('auth/set_basic_password.html')
        
        # Set basic auth password for OAuth user
        try:
            user_manager = UserManager()
            username = current_user.get('username')
            password_hash = generate_password_hash(password)
            
            if user_manager.set_temp_basic_auth_password(username, password_hash):
                flash('Basic auth password set successfully! You can now use basic auth login.', 'success')
                logger.info(f"OAuth user {username} set basic auth password")
                return redirect('/assas_app/profile')
            else:
                flash('Failed to set basic auth password', 'error')
                
        except Exception as e:
            logger.error(f"Error setting basic auth password for {username}: {e}")
            flash('An error occurred while setting password', 'error')
    
    return render_template('auth/set_basic_password.html')

@basic_auth_bp.route('/api-login')
@http_basic_auth.login_required
def api_login():
    """API endpoint for Basic Auth login."""
    # Get the authenticated username
    username = http_basic_auth.current_user()
    
    if not username:
        return {'error': 'Authentication failed'}, 401
    
    # Create session for API user
    BasicAuthSession.create_basic_auth_session(username)
    
    user_session = session.get('user', {})
    
    return {
        'status': 'success',
        'message': f'Authenticated as {username}',
        'user': {
            'username': user_session.get('username'),
            'email': user_session.get('email'),
            'roles': user_session.get('roles', []),
            'auth_source': user_session.get('auth_source'),
            'provider': user_session.get('provider')
        }
    }

@basic_auth_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    """Change password for basic auth users."""
    current_user = get_current_user()
    
    if not current_user:
        flash('Please log in first', 'error')
        return redirect('/auth/login')
    
    # Allow both basic auth users and OAuth users with basic auth enabled
    auth_method = current_user.get('auth_method')
    provider = current_user.get('provider')
    
    if not (auth_method == 'basic_auth' or provider in ['github', 'bwidm']):
        flash('Password change not available for your account type', 'error')
        return redirect('/assas_app/profile')
    
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not all([new_password, confirm_password]):
            flash('New password fields are required', 'error')
            return render_template('auth/change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return render_template('auth/change_password.html')
        
        if len(new_password) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return render_template('auth/change_password.html')
        
        username = current_user.get('username')
        
        # For OAuth users, they might not have a current password
        if auth_method == 'basic_auth' and current_password:
            # Verify current password for existing basic auth users
            if not BasicAuthUserManager.verify_password(username, current_password):
                flash('Current password is incorrect', 'error')
                return render_template('auth/change_password.html')
        
        # Update password in database
        try:
            user_manager = UserManager()
            new_password_hash = generate_password_hash(new_password)
            
            # Use different methods based on user type
            if provider in ['github', 'bwidm']:
                # OAuth user setting/changing basic auth password
                success = user_manager.set_temp_basic_auth_password(username, new_password_hash)
            else:
                # Pure basic auth user
                success = user_manager.update_basic_auth_password(username, new_password_hash)
            
            if success:
                flash('Password updated successfully', 'success')
                logger.info(f"Password updated for user: {username} (method: {auth_method})")
                return redirect('/assas_app/profile')
            else:
                flash('Failed to update password', 'error')
                
        except Exception as e:
            logger.error(f"Error updating password for {username}: {e}")
            flash('An error occurred while updating password', 'error')
    
    return render_template('auth/change_password.html')

@basic_auth_bp.route('/admin/create-user', methods=['POST'])
def admin_create_basic_user():
    """Admin route to create basic auth user."""
    current_user = get_current_user()
    
    if not current_user or 'admin' not in current_user.get('roles', []):
        return {'error': 'Admin access required'}, 403
    
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        email = data.get('email', '').strip()
        name = data.get('name', '').strip()
        roles = data.get('roles', ['viewer'])
        
        if not all([username, password, email]):
            return {'error': 'Username, password, and email are required'}, 400
        
        if len(password) < 8:
            return {'error': 'Password must be at least 8 characters long'}, 400
        
        # Create user in database
        user_manager = UserManager()
        password_hash = generate_password_hash(password)
        
        user_data = {
            'username': username,
            'email': email,
            'name': name or username,
            'provider': 'basic_auth',
            'roles': roles,
            'basic_auth_password_hash': password_hash,
            'is_active': True
        }
        
        created_user = user_manager.create_or_update_user(user_data)
        
        logger.info(f"Admin {current_user.get('username')} created basic auth user: {username}")
        
        return {
            'status': 'success',
            'message': f'User {username} created successfully',
            'user_id': str(created_user.get('_id'))
        }
        
    except Exception as e:
        logger.error(f"Error creating basic auth user: {e}")
        return {'error': str(e)}, 500

@basic_auth_bp.route('/status')
def basic_auth_status():
    """Get basic auth status and available users (for debugging)."""
    if not current_app.debug:
        return {'error': 'Debug mode only'}, 403
    
    users = BasicAuthUserManager.get_basic_auth_users()
    user_list = []
    
    for username, user_data in users.items():
        user_list.append({
            'username': username,
            'email': user_data.get('email'),
            'roles': user_data.get('roles', []),
            'is_active': user_data.get('is_active', True),
            'has_password': bool(user_data.get('password_hash')),
            'source': user_data.get('source', 'config'),
            'original_provider': user_data.get('user_data', {}).get('provider')
        })
    
    return {
        'basic_auth_enabled': True,
        'total_users': len(users),
        'config_users': len([u for u in users.values() if u.get('source') != 'database']),
        'database_users': len([u for u in users.values() if u.get('source') == 'database']),
        'oauth_with_basic': len([u for u in users.values() if u.get('source') == 'oauth_with_basic']),
        'users': user_list
    }

def init_basic_auth(app):
    """Initialize basic auth configuration."""
    # This function can be used for any additional basic auth setup
    logger.info("Basic Auth initialized")
    pass