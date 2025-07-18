"""Check Flask session configuration and diagnose session issues."""

import os
import sys
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

from flask import Flask
from datetime import timedelta

def check_session_config():
    """Check current session configuration."""
    print("=" * 60)
    print("SESSION CONFIGURATION CHECK")
    print("=" * 60)
    
    # Check environment variables
    secret_key = os.getenv('SECRET_KEY', 'Not set')
    session_lifetime = os.getenv('PERMANENT_SESSION_LIFETIME', 'Not set')
    
    print(f"SECRET_KEY: {'Set' if secret_key != 'Not set' else 'NOT SET'}")
    print(f"PERMANENT_SESSION_LIFETIME: {session_lifetime}")
    
    # Import your config
    try:
        from config import Config
        config = Config()
        
        print(f"\nConfig values:")
        print(f"SECRET_KEY: {'Set' if hasattr(config, 'SECRET_KEY') and config.SECRET_KEY else 'NOT SET'}")
        print(f"PERMANENT_SESSION_LIFETIME: {getattr(config, 'PERMANENT_SESSION_LIFETIME', 'Not set')}")
        print(f"SESSION_PERMANENT: {getattr(config, 'SESSION_PERMANENT', 'Not set')}")
        print(f"SESSION_USE_SIGNER: {getattr(config, 'SESSION_USE_SIGNER', 'Not set')}")
        print(f"SESSION_COOKIE_SECURE: {getattr(config, 'SESSION_COOKIE_SECURE', 'Not set')}")
        print(f"SESSION_COOKIE_HTTPONLY: {getattr(config, 'SESSION_COOKIE_HTTPONLY', 'Not set')}")
        print(f"SESSION_COOKIE_SAMESITE: {getattr(config, 'SESSION_COOKIE_SAMESITE', 'Not set')}")
        
    except Exception as e:
        print(f"Error importing config: {e}")

if __name__ == "__main__":
    check_session_config()