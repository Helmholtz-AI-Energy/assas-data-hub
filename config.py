"""Configuration file for the ASSAS Data Hub application."""

import os
from datetime import timedelta
from dotenv import load_dotenv

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

    CONNECTIONSTRING = os.getenv("CONNECTIONSTRING", r"mongodb://localhost:27018/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", r"assas")

    # Optional settings (uncomment in .env as needed)
    # FLASK_HTPASSWD_PATH = os.getenv('FLASK_HTPASSWD_PATH')
    # FLASK_SECRET = os.getenv('FLASK_SECRET', SECRET_KEY)
    # DB_HOST = os.getenv('DB_HOST')

    # OAuth Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'

    # bwIDM Configuration (Primary Identity Provider)
    BWIDM_CLIENT_ID = os.environ.get('BWIDM_CLIENT_ID')
    BWIDM_CLIENT_SECRET = os.environ.get('BWIDM_CLIENT_SECRET')
    BWIDM_DISCOVERY_URL = 'https://login.bwidm.de/auth/realms/bw/.well-known/openid_configuration'

    # GitHub Configuration (Testing)
    GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
    GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')

    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

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
