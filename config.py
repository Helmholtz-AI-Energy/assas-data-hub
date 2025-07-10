"""Configuration file for the ASSAS Data Hub application."""

import os
from datetime import timedelta
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# Load environment variables from .env file
load_dotenv()


class Config(object):
    """Base configuration class for the ASSAS Data Hub application."""

    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    DEVELOPMENT = os.getenv("DEVELOPMENT", "True").lower() == "true"

    ASTEC_ROOT = os.getenv("ASTEC_ROOT", r"/root/astecV3.1.1_linux64/astecV3.1.1")
    ASTEC_TYPE = os.getenv(
        "ASTEC_TYPE", r"linux_64"
    )  # Assuming ASTEC_TYPE is the correct variable

    BACKUP_DIRECTORY = os.getenv(
        "BACKUP_DIRECTORY", r"Z:\\scc\\projects\\ASSAS\\backup_mongodb"
    )

    CONNECTIONSTRING = os.getenv("CONNECTIONSTRING", r"mongodb://localhost:27017/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", r"assas")

    # URL Configuration
    SERVER_NAME = os.environ.get('SERVER_NAME')  # e.g., 'localhost:5000' for dev
    PREFERRED_URL_SCHEME = os.environ.get('PREFERRED_URL_SCHEME', 'http')
    
    # For development
    if os.environ.get('FLASK_ENV') == 'development':
        SERVER_NAME = 'localhost:5000'
        PREFERRED_URL_SCHEME = 'http'
    
    # OAuth Configuration
    GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
    GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')

    BWIDM_CLIENT_ID = os.getenv('BWIDM_CLIENT_ID', '')
    BWIDM_CLIENT_SECRET = os.getenv('BWIDM_CLIENT_SECRET', '')

    # Session Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-fallback-key-change-in-production')
    PERMANENT_SESSION_LIFETIME = timedelta(
        hours=int(os.getenv('SESSION_LIFETIME_HOURS', 8))
    )
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_REFRESH_EACH_REQUEST = True
    SESSION_COOKIE_NAME = 'assas_session'
    SESSION_COOKIE_DOMAIN = None
    SESSION_COOKIE_PATH = '/'
    
    # AARC Entitlements Configuration
    AARC_GROUP_CLAIM = 'eduperson_entitlement'
    ASSAS_GROUP_PREFIX = 'urn:geant:helmholtz.de:group:HIFIS:'

    # Role Mapping
    ROLE_MAPPINGS = {
        'urn:geant:helmholtz.de:group:HIFIS:PROJECT-X:admins': 'admin',
        'urn:geant:helmholtz.de:group:HIFIS:PROJECT-X:writers': 'writer',
        'urn:geant:helmholtz.de:group:HIFIS:PROJECT-X:readers': 'reader',
        'urn:geant:helmholtz.de:group:HIFIS:PROJECT-X:viewers': 'viewer',
    }

    GITHUB_ROLE_MAPPINGS = {
        # Map GitHub usernames to roles for testing
        'ke4920': 'admin',
        'test-user-1': 'writer',
        'test-user-2': 'reader',
        # Default role for any GitHub user
        '*': 'viewer'
    }

    BWIDM_ROLE_MAPPINGS = {
        'jonas.dressner@kit.edu': 'admin',
        'markus.goetz@kit.edu': 'admin',
        '*': 'viewer'
    }


class DevelopmentConfig(Config):
    DEBUG = True
    SERVER_NAME = 'localhost:5000'
    PREFERRED_URL_SCHEME = 'http'

    # Development basic auth users
    BASIC_AUTH_USERS = {
        'admin_local': {
            'password_hash': generate_password_hash('admin123'),  # Change this!
            'roles': ['admin'],
            'email': 'admin@dev.local',
            'name': 'Development Admin',
            'is_active': True
        },
        'user': {
            'password_hash': generate_password_hash('user123'),   # Change this!
            'roles': ['viewer'],
            'email': 'user@dev.local',
            'name': 'Development User',
            'is_active': True
        }
    }


class ProductionConfig(Config):
    DEBUG = False
    # SERVER_NAME should be set via environment variable in production
    PREFERRED_URL_SCHEME = 'https'
