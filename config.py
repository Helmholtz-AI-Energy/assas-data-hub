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
    ASTEC_TYPE = os.getenv("ASTEC_TYPE", r"linux_64")

    BACKUP_DIRECTORY = os.getenv(
        "BACKUP_DIRECTORY", r"Z:\\scc\\projects\\ASSAS\\backup_mongodb"
    )

    CONNECTIONSTRING = os.getenv("CONNECTIONSTRING", r"mongodb://localhost:27017/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", r"assas")

    # URL Configuration
    SERVER_NAME = os.environ.get("SERVER_NAME")
    PREFERRED_URL_SCHEME = os.environ.get("PREFERRED_URL_SCHEME", "http")

    GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")

    BWIDM_CLIENT_ID = os.getenv("BWIDM_CLIENT_ID", "")
    BWIDM_CLIENT_SECRET = os.getenv("BWIDM_CLIENT_SECRET", "")

    HELMHOLTZ_CLIENT_ID = os.getenv("HELMHOLTZ_CLIENT_ID", "")
    HELMHOLTZ_CLIENT_SECRET = os.getenv("HELMHOLTZ_CLIENT_SECRET", "")

    # Session Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-fallback-key-change-in-production")
    PERMANENT_SESSION_LIFETIME = timedelta(
        hours=int(os.getenv("SESSION_LIFETIME_HOURS", 8))
    )
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_REFRESH_EACH_REQUEST = True
    SESSION_COOKIE_NAME = "assas_session"
    SESSION_COOKIE_DOMAIN = None
    SESSION_COOKIE_PATH = "/"

    # AARC Entitlements Configuration
    AARC_GROUP_CLAIM = "eduperson_entitlement"
    ASSAS_GROUP_PREFIX = "urn:geant:helmholtz.de:group:HIFIS:"

    # Role Mapping (exactly like your assas_add_user.py)
    ROLE_MAPPING = {
        "Administrator": ["admin"],
        "Researcher": ["researcher"],
        "User": ["viewer"],
        "Curator": ["curator"],
    }

    # Available roles for the system (4 roles only)
    AVAILABLE_ROLES = [
        {
            "value": "admin",
            "label": "Administrator",
            "description": "Full system access and user management",
        },
        {
            "value": "researcher",
            "label": "Researcher",
            "description": "Research data access and analysis tools",
        },
        {
            "value": "curator",
            "label": "Curator",
            "description": "Data curation and quality control",
        },
        {
            "value": "viewer",
            "label": "User",
            "description": "Basic view access to content",
        },
    ]

    # AARC Entitlement to Role Mapping
    AARC_ROLE_MAPPINGS = {
        "urn:geant:helmholtz.de:group:HIFIS:PROJECT-X:admins": ["admin"],
        "urn:geant:helmholtz.de:group:HIFIS:PROJECT-X:researchers": ["researcher"],
        "urn:geant:helmholtz.de:group:HIFIS:PROJECT-X:curators": ["curator"],
        "urn:geant:helmholtz.de:group:HIFIS:PROJECT-X:viewers": ["viewer"],
    }

    # GitHub Role Mappings
    GITHUB_ROLE_MAPPINGS = {
        "ke4920": ["admin"],
        "jonas-dressner": ["admin"],
        "markus-goetz": ["admin"],
        "*": ["viewer"],  # Default role
    }

    # bwIDM Role Mappings
    BWIDM_ROLE_MAPPINGS = {
        "jonas.dressner@kit.edu": ["admin"],
        "markus.goetz@kit.edu": ["admin"],
        "charlotte.debus@kit.edu": ["researcher"],
        "anastasia.stakhanova@kit.edu": ["researcher"],
        "*": ["viewer"],  # Default role
    }

    HELMHOLTZ_ROLE_MAPPINGS = {
        "your-helmholtz-username-or-claim": ["admin"],
        "*": ["viewer"],
    }


class DevelopmentConfig(Config):
    """Development configuration class for the ASSAS Data Hub application."""

    DEBUG = True
    SERVER_NAME = None  # "assas.scc.kit.edu:5000"
    PREFERRED_URL_SCHEME = "https"

    # Development basic auth users
    BASIC_AUTH_USERS = {
        "admin_local": {
            "password_hash": generate_password_hash("admin123"),  # Change this!
            "roles": ["admin"],
            "email": "admin@dev.local",
            "name": "Development Admin",
            "is_active": True,
        },
        "user": {
            "password_hash": generate_password_hash("user123"),  # Change this!
            "roles": ["viewer"],
            "email": "user@dev.local",
            "name": "Development User",
            "is_active": True,
        },
    }


class ProductionConfig(Config):
    """Production configuration class for the ASSAS Data Hub application."""

    DEBUG = False
    # SERVER_NAME should be set via environment variable in production
    PREFERRED_URL_SCHEME = "https"
