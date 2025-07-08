"""Configuration file for the ASSAS Data Hub application."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config(object):
    """Base configuration class for the ASSAS Data Hub application."""

    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    DEVELOPMENT = os.getenv('DEVELOPMENT', 'True').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    TMP_FOLDER = os.getenv('TMP_FOLDER', r"/var/tmp/assas_data_hub")
    LSDF_ARCHIVE = os.getenv('LSDF_ARCHIVE', r"/mnt/ASSAS/upload_test/")
    UPLOAD_DIRECTORY = os.getenv('UPLOAD_DIRECTORY', r"/mnt/ASSAS/upload_test/uploads/")
    UPLOAD_FILE = os.getenv('UPLOAD_FILE', r"/mnt/ASSAS/upload_test/uploads/uploads.txt")
    LOCAL_ARCHIVE = os.getenv('LOCAL_ARCHIVE', r"/root/upload/")
    PYTHON_VERSION = os.getenv('PYTHON_VERSION', r"/opt/python/3.11.8/bin/python3.11")
    ASTEC_ROOT = os.getenv('ASTEC_ROOT', r"/root/astecV3.1.1_linux64/astecV3.1.1")
    ASTEC_COMPUTER = os.getenv('ASTEC_COMPUTER', r"linux_64")
    ASTEC_COMPILER = os.getenv('ASTEC_COMPILER', r"release")
    ASTEC_PARSER = os.getenv('ASTEC_PARSER', r"/root/assas-data-hub/assas_database/assasdb/assas_astec_parser.py")
    CONNECTIONSTRING = os.getenv('CONNECTIONSTRING', r"mongodb://localhost:27017/")
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', r"assas")

    # Optional settings (uncomment in .env as needed)
    # FLASK_HTPASSWD_PATH = os.getenv('FLASK_HTPASSWD_PATH')
    # FLASK_SECRET = os.getenv('FLASK_SECRET', SECRET_KEY)
    # DB_HOST = os.getenv('DB_HOST')
