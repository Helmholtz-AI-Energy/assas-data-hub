"""Authentication API endpoints."""

import logging
from flask import Blueprint, Response, session

from ...auth_utils import get_current_user, is_authenticated
from ...utils.api_utils import APIResponse

logger = logging.getLogger("assas_app")

auth_api_bp = Blueprint("auth_api", __name__)


@auth_api_bp.route("/user", methods=["GET"])
def get_current_user_info() -> Response:
    """GET /auth/user - Get current authenticated user information."""
    if not is_authenticated():
        return APIResponse.unauthorized("No authenticated user")

    user = get_current_user()

    # Remove sensitive information
    safe_user_info = {
        "id": user.get("id"),
        "username": user.get("username"),
        "email": user.get("email"),
        "name": user.get("name"),
        "roles": user.get("roles", []),
        "provider": user.get("provider"),
        "auth_method": user.get("auth_method"),
        "authenticated": user.get("authenticated", False),
    }

    return APIResponse.success({"user": safe_user_info})


@auth_api_bp.route("/logout", methods=["POST"])
def api_logout() -> Response:
    """POST /auth/logout - Logout current user."""
    if not is_authenticated():
        return APIResponse.error("No authenticated user", 400)

    current_user = get_current_user()
    logger.info(f"API logout for user: {current_user.get('username')}")

    # Clear session
    session.clear()

    return APIResponse.success(message="Successfully logged out")


@auth_api_bp.route("/status", methods=["GET"])
def auth_status() -> Response:
    """GET /auth/status - Get authentication status."""
    authenticated = is_authenticated()

    response_data = {
        "authenticated": authenticated,
        "user": get_current_user() if authenticated else None,
    }

    return APIResponse.success(response_data)
