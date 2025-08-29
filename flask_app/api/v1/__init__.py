"""API v1 package initialization."""

from flask import Blueprint
from ...utils.url_utils import get_base_url

# Create main API v1 blueprint
api_v1_bp = Blueprint("api_v1", __name__)


def create_api_v1_blueprint() -> Blueprint:
    """Create and configure API v1 blueprint with dynamic URL prefix."""
    base_url = get_base_url()
    api_v1_bp.url_prefix = base_url

    # Import and register sub-blueprints
    from .datasets import datasets_bp
    from .files import files_bp
    from .auth import auth_api_bp

    # Register sub-blueprints
    api_v1_bp.register_blueprint(datasets_bp, url_prefix="/datasets")
    api_v1_bp.register_blueprint(files_bp, url_prefix="/files")
    api_v1_bp.register_blueprint(auth_api_bp, url_prefix="/auth")

    return api_v1_bp
