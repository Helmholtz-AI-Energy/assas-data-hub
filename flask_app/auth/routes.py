"""Authentication routes with profile page."""

from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    url_for,
    jsonify,
    request,
)
from ..auth_utils import is_authenticated, get_current_user
from ..utils.url_utils import get_auth_base_url, get_base_url

auth_bp = Blueprint(
    name="auth", 
    import_name=__name__, 
    url_prefix=f"{get_auth_base_url()}"
)


@auth_bp.route("/login")
def login_page():
    """Display login page."""
    if is_authenticated():
        # Fix: Redirect to Dash app home instead of non-existent Flask route
        return redirect(f"{get_base_url()}/")

    return render_template("auth/login.html")


@auth_bp.route("/profile")
def profile():
    """User profile page (Flask route - redirects to Dash page)."""
    if not is_authenticated():
        return redirect(url_for("auth.login_page"))

    # Redirect to Dash profile page
    return redirect(f"{get_base_url()}/profile")


# Add this debug route to your auth routes


@auth_bp.route("/debug/oauth-urls")
def debug_oauth_urls():
    """Debug OAuth URLs to identify redirect_uri mismatch."""
    from flask import url_for, current_app

    debug_info = {
        "current_request": {
            "host": request.host,
            "scheme": request.scheme,
            "base_url": request.base_url,
            "url_root": request.url_root,
        },
        "flask_config": {
            "SERVER_NAME": current_app.config.get("SERVER_NAME"),
            "PREFERRED_URL_SCHEME": current_app.config.get(
                "PREFERRED_URL_SCHEME", "http"
            ),
            "APPLICATION_ROOT": current_app.config.get("APPLICATION_ROOT", "/"),
        },
        "oauth_settings": {
            "HELMHOLTZ_CLIENT_ID": current_app.config.get(
                "HELMHOLTZ_CLIENT_ID", "Not set"
            ),
        },
    }

    # Generate OAuth callback URLs
    try:
        debug_info["oauth_callback_urls"] = {
            "helmholtz": \
                url_for("oauth.callback", provider="helmholtz", _external=True),
        }

    except Exception as e:
        debug_info["url_generation_error"] = str(e)

    return jsonify(debug_info)


@auth_bp.route("/debug/oauth-config")
def debug_oauth_config():
    """Debug OAuth configuration."""
    from flask import current_app, jsonify

    if not current_app.debug:
        return jsonify({"error": "Debug mode disabled"}), 403

    return jsonify(
        {
            "HELMHOLTZ_CLIENT_ID": current_app.config.get("HELMHOLTZ_CLIENT_ID"),
            "HELMHOLTZ_CLIENT_SECRET": bool(
                current_app.config.get("HELMHOLTZ_CLIENT_SECRET")
            ),
            "SECRET_KEY_SET": bool(current_app.config.get("SECRET_KEY")),
        }
    )


@auth_bp.route("/debug/dash-access")
def debug_dash_access():
    """Debug Dash app access."""
    current_user = get_current_user()

    debug_info = {
        "authenticated": is_authenticated(),
        "current_user": current_user,
        "session_keys": list(session.keys()),
        "dash_urls": {
            "home": "/assas_app/",
            "database": "/assas_app/database",
            "profile": "/assas_app/profile",
            "admin": "/assas_app/admin",
        },
    }

    return jsonify(debug_info)
