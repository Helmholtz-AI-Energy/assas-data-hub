"""URL utilities for the ASSAS Data Hub application."""

from flask import current_app


def get_base_url() -> str:
    """Get the base URL from configuration.

    Returns:
        str: The base URL for the application (e.g., '/api/v1' or '/test/assas_app')

    """
    return current_app.config.get("BASE_URL")


def get_auth_base_url() -> str:
    """Get the auth base URL from configuration.

    Returns:
        str: The base URL for authentication routes (e.g., '/test/auth')

    """
    return current_app.config.get("AUTH_BASE_URL", "/test/auth")


def get_dash_base_url() -> str:
    """Get the Dash app base URL from configuration.

    Returns:
        str: The base URL for the Dash application

    """
    base_url = get_base_url()
    # Ensure it ends with / for Dash url_base_pathname
    return f"{base_url}/" if not base_url.endswith("/") else base_url


def build_url(endpoint: str, base_url: str = None) -> str:
    """Build a complete URL with the given endpoint.

    Args:
        endpoint: The endpoint path (e.g., '/datasets', '/login')
        base_url: Optional base URL override

    Returns:
        str: Complete URL path

    """
    if base_url is None:
        base_url = get_base_url()

    # Remove leading slash from endpoint if base_url already has trailing slash
    if base_url.endswith("/") and endpoint.startswith("/"):
        endpoint = endpoint[1:]
    # Add slash between base_url and endpoint if needed
    elif not base_url.endswith("/") and not endpoint.startswith("/"):
        endpoint = "/" + endpoint

    return f"{base_url}{endpoint}"


def build_auth_url(endpoint: str) -> str:
    """Build a complete auth URL with the given endpoint.

    Args:
        endpoint: The auth endpoint path (e.g., '/login', '/logout')

    Returns:
        str: Complete auth URL path

    """
    return build_url(endpoint, get_auth_base_url())
