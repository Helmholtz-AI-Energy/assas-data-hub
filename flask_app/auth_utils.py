"""Authentication utilities for Flask application using MongoDB."""

import logging
from functools import wraps
from typing import Optional, List
from flask import session, request, redirect, url_for, flash
from werkzeug.security import check_password_hash
from pymongo import MongoClient

logger = logging.getLogger("assas_app")

# MongoDB connection setup
client = MongoClient(
    "mongodb://localhost:27017/"
)  # Replace with your MongoDB connection string
db = client["assas"]  # Database name
users_collection = db["users"]  # Collection name

users = users_collection.find()


def verify_password(username_or_email: str, password: str) -> str | None:
    """Verifiy the username or email and password for authentication."""
    logger.info(f"Verifying user/email {username_or_email} with password {password}.")

    user = users_collection.find_one(
        {"$or": [{"username": username_or_email}, {"email": username_or_email}]}
    )

    if user and check_password_hash(user["password"], password):
        session["user"] = user["username"]  # Store the username in the session
        return user["username"]  # Return the username if authentication is successful

    logger.error("Invalid username/email or password.")
    return None


def is_authenticated() -> bool:
    """Check if user is authenticated."""
    return session.get("user", {}).get("authenticated", False)


def get_current_user() -> Optional[dict]:
    """Get current user information."""
    logger.info("Retrieving current user from session.")
    return session.get("user")


def get_user_roles() -> List[str]:
    """Get current user's roles."""
    user = get_current_user()
    return user.get("roles", []) if user else []


def has_role(role: str) -> bool:
    """Check if current user has specific role."""
    return role in get_user_roles()


def require_auth(f: callable) -> callable:
    """Get decorator for authentication."""

    @wraps(f)
    def decorated_function(*args: any, **kwargs: any) -> any:
        if not is_authenticated():
            # Store intended URL
            session["next_url"] = request.url
            flash("Please log in to access this page", "warning")
            return redirect(url_for("auth.login_page"))
        return f(*args, **kwargs)

    return decorated_function


def require_role(role: str) -> callable:
    """Get decorator for specific role."""

    def decorator(f: callable) -> callable:
        @wraps(f)
        def decorated_function(*args: any, **kwargs: any) -> any:
            if not is_authenticated():
                session["next_url"] = request.url
                flash("Please log in to access this page", "warning")
                return redirect(url_for("auth.login_page"))

            if not has_role(role):
                flash("Insufficient permissions", "error")
                return redirect(url_for("dash_app.home"))

            return f(*args, **kwargs)

        return decorated_function

    return decorator


# Legacy compatibility
class auth:
    """Legacy auth class for compatibility."""

    @staticmethod
    def login_required(f: callable) -> callable:
        """Legacy login_required decorator."""
        return require_auth(f)
