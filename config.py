"""Configuration file for the ASSAS Data Hub application."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config(object):
    """Base configuration class for the ASSAS Data Hub application."""

    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    DEVELOPMENT = os.getenv("DEVELOPMENT", "True").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

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
