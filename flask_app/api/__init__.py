"""API package initialization."""

from flask import Flask
from .v1.datasets import datasets_bp
from .v1.files import files_bp
from .v1.auth import auth_api_bp
from ..utils.url_utils import get_base_url


def register_api_blueprints(app: Flask) -> None:
    """Register all API blueprints with dynamic base URL."""
    base_url = get_base_url()

    # Register datasets API
    app.register_blueprint(datasets_bp, url_prefix=f"{base_url}/datasets")

    # Register files API
    app.register_blueprint(files_bp, url_prefix=f"{base_url}/files")

    # Register auth API
    app.register_blueprint(auth_api_bp, url_prefix=f"{base_url}/auth")

    app.logger.info(f"API blueprints registered with base URL: {base_url}")
    app.logger.info(f"Dataset API available at: {base_url}/datasets")
    app.logger.info(f"Files API available at: {base_url}/files")
    app.logger.info(f"Auth API available at: {base_url}/auth")
