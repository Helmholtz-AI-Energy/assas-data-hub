"""OAuth authentication module with manual token exchange."""

import logging
import secrets
import requests
from typing import Dict
from urllib.parse import urlencode
from authlib.integrations.flask_client import OAuth
from flask import (
    Blueprint,
    current_app,
    session,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
)

logger = logging.getLogger("assas_app")

# OAuth Blueprint
oauth_bp = Blueprint("oauth", __name__, url_prefix="/auth")

# Initialize OAuth
oauth = OAuth()


def init_oauth(app):
    """Initialize OAuth with Flask app."""
    oauth.init_app(app)

    # Register GitHub provider (for testing)
    if app.config.get("GITHUB_CLIENT_ID"):
        oauth.register(
            name="github",
            client_id=app.config["GITHUB_CLIENT_ID"],
            client_secret=app.config["GITHUB_CLIENT_SECRET"],
            access_token_url="https://github.com/login/oauth/access_token",
            authorize_url="https://github.com/login/oauth/authorize",
            api_base_url="https://api.github.com/",
            client_kwargs={"scope": "user:email read:user"},
        )
        logger.info("GitHub OAuth provider registered")
        
    # Register Helmholtz provider
    if app.config.get("HELMHOLTZ_CLIENT_ID"):
        oauth.register(
            name="helmholtz",
            client_id=app.config["HELMHOLTZ_CLIENT_ID"],
            client_secret=app.config["HELMHOLTZ_CLIENT_SECRET"],
            access_token_url="https://helmholtz.de/login/oauth/access_token",
            authorize_url="https://helmholtz.de/login/oauth/authorize",
            api_base_url="https://api.helmholtz.de/",
            client_kwargs={"scope": "user:email read:user"},
        )
        logger.info("Helmholtz OAuth provider registered")


class GitHubRoleProcessor:
    """Process GitHub user data and assign roles."""

    @staticmethod
    def get_user_role(username: str, email: str) -> str:
        """Get role for GitHub user based on configuration."""
        role_mappings = current_app.config.get("GITHUB_ROLE_MAPPINGS", {})

        if username in role_mappings:
            role = role_mappings[username]
            logger.info(f"Assigned role '{role}' to GitHub user '{username}'")
            return role

        default_role = role_mappings.get("*", "viewer")
        logger.info(
            f"Assigned default role '{default_role}' to GitHub user '{username}'"
        )
        return default_role


class UserSession:
    """Manage user session data."""

    @staticmethod
    def create_user_session(user_info: Dict, provider: str) -> None:
        """Create user session from OAuth user info and store in MongoDB."""
        from ..database.user_manager import UserManager

        session.permanent = True

        if provider == "github":
            username = user_info.get("login")
            email = user_info.get("email")
            name = user_info.get("name") or username
            user_id = str(user_info.get("id"))

            role = GitHubRoleProcessor.get_user_role(username, email)

            # Prepare user data for MongoDB
            user_data = {
                "username": username,
                "email": email,
                "name": name,
                "provider": provider,
                "roles": [role],
                "github_id": user_id,
                "avatar_url": user_info.get("avatar_url"),
                "github_profile": user_info.get("html_url"),
                "is_active": True,
            }

            # Store/update user in MongoDB
            try:
                user_manager = UserManager()
                stored_user = user_manager.create_or_update_user(user_data)
                logger.info(f"User stored/updated in MongoDB: {email}")
            except Exception as e:
                logger.error(f"Failed to store user in MongoDB: {e}")
                stored_user = None

            # Create session
            session["user"] = {
                "id": user_id,
                "username": username,
                "email": email,
                "name": name,
                "provider": provider,
                "authenticated": True,
                "roles": [role],
                "avatar_url": user_info.get("avatar_url"),
                "github_profile": user_info.get("html_url"),
                "mongodb_id": str(stored_user.get("_id")) if stored_user else None,
            }

        logger.info(
            f"Created session for {provider} user: {session['user'].get('email')}"
        )


def exchange_github_code_for_token(code: str, redirect_uri: str) -> str:
    """Manually exchange GitHub authorization code for access token."""
    token_data = {
        "client_id": current_app.config["GITHUB_CLIENT_ID"],
        "client_secret": current_app.config["GITHUB_CLIENT_SECRET"],
        "code": code,
        "redirect_uri": redirect_uri,
    }

    headers = {"Accept": "application/json", "User-Agent": "ASSAS-Data-Hub"}

    logger.info("Exchanging authorization code for access token...")

    response = requests.post(
        "https://github.com/login/oauth/access_token",
        data=token_data,
        headers=headers,
        timeout=30,
    )

    if response.status_code != 200:
        logger.error(
            f"Token exchange failed with status {response.status_code}: {response.text}"
        )
        raise Exception(f"Token exchange failed: {response.status_code}")

    token_info = response.json()
    logger.info(f"Token response: {token_info}")

    if "error" in token_info:
        logger.error(f"GitHub token error: {token_info}")
        raise Exception(
            f"GitHub token error: {token_info.get('error_description', token_info.get('error'))}"
        )

    access_token = token_info.get("access_token")
    if not access_token:
        logger.error(f"No access token in response: {token_info}")
        raise Exception("No access token received from GitHub")

    logger.info("Access token received successfully")
    return access_token


def get_github_user_info(access_token: str) -> Dict:
    """Get GitHub user information using access token."""
    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "ASSAS-Data-Hub",
    }

    # Get user info
    logger.info("Fetching user information from GitHub...")
    user_response = requests.get(
        "https://api.github.com/user", headers=headers, timeout=30
    )

    if user_response.status_code != 200:
        logger.error(
            f"Failed to fetch user info: {user_response.status_code} - {user_response.text}"
        )
        raise Exception(
            f"Failed to fetch user information: {user_response.status_code}"
        )

    user_info = user_response.json()
    logger.info(f"User info received for: {user_info.get('login')}")

    # Get user email if not public
    if not user_info.get("email"):
        logger.info("Fetching user email from GitHub...")
        emails_response = requests.get(
            "https://api.github.com/user/emails", headers=headers, timeout=30
        )

        if emails_response.status_code == 200:
            emails = emails_response.json()
            primary_email = next((e["email"] for e in emails if e["primary"]), None)
            if primary_email:
                user_info["email"] = primary_email
                logger.info(f"Primary email found: {primary_email}")
        else:
            logger.warning(f"Failed to fetch emails: {emails_response.status_code}")

    return user_info


# OAuth Routes
@oauth_bp.route("/login/<provider>")
def login(provider: str):
    """Initiate OAuth login flow."""
    if provider not in ["github", "bwidm"]:
        flash(f"Unknown provider: {provider}", "error")
        return redirect(url_for("auth.login_page"))

    if not current_app.config.get(f"{provider.upper()}_CLIENT_ID"):
        flash(f"{provider.title()} authentication is not configured", "error")
        return redirect(url_for("auth.login_page"))

    try:
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        session[f"oauth_state_{provider}"] = state
        session.modified = True

        # EXPLICITLY set the redirect URI
        redirect_uri = url_for("oauth.callback", provider=provider, _external=True)
        logger.info(f"OAuth login for {provider}, redirect URI: {redirect_uri}")

        if provider == "github":
            # Manual GitHub OAuth URL construction
            params = {
                "client_id": current_app.config["GITHUB_CLIENT_ID"],
                "redirect_uri": redirect_uri,
                "scope": "user:email read:user",
                "state": state,
                "response_type": "code",
            }

            auth_url = "https://github.com/login/oauth/authorize?" + urlencode(params)
            logger.info(f"GitHub auth URL: {auth_url}")
            return redirect(auth_url)

        elif provider == "bwidm":
            # Similar for bwIDM
            nonce = secrets.token_urlsafe(32)
            session[f"oidc_nonce_{provider}"] = nonce

            params = {
                "client_id": current_app.config["BWIDM_CLIENT_ID"],
                "redirect_uri": redirect_uri,
                "scope": "openid profile email eduperson_entitlement",
                "response_type": "code",
                "state": state,
                "nonce": nonce,
            }

            auth_url = (
                "https://login.bwidm.de/auth/realms/bw/protocol/openid-connect/auth?"
                + urlencode(params)
            )
            logger.info(f"bwIDM auth URL: {auth_url}")
            return redirect(auth_url)

    except Exception as e:
        logger.error(f"OAuth login error for {provider}: {e}")
        flash(f"Authentication error: {str(e)}", "error")
        return redirect(url_for("auth.login_page"))


@oauth_bp.route("/callback/<provider>")
def callback(provider: str):
    """Handle OAuth callback with manual token exchange."""
    if provider not in ["github", "bwidm"]:
        flash("Invalid authentication provider", "error")
        return redirect(url_for("auth.login_page"))

    try:
        # Check for authorization errors first
        error = request.args.get("error")
        if error:
            error_description = request.args.get("error_description", "Unknown error")
            logger.error(f"OAuth authorization error: {error} - {error_description}")
            flash(f"Authorization failed: {error_description}", "error")
            return redirect(url_for("auth.login_page"))

        # Verify state parameter
        received_state = request.args.get("state")
        stored_state = session.pop(f"oauth_state_{provider}", None)

        logger.info("State verification:")
        logger.info(f"  Received: {received_state}")
        logger.info(f"  Stored: {stored_state}")
        logger.info(f"  Match: {received_state == stored_state}")

        if not received_state or not stored_state or received_state != stored_state:
            logger.error(
                f"State mismatch: received={received_state}, stored={stored_state}"
            )
            flash("Security error: Invalid state parameter. Please try again.", "error")
            return redirect(url_for("auth.login_page"))

        # Get authorization code
        code = request.args.get("code")
        if not code:
            logger.error("No authorization code received")
            flash("Authorization failed: No authorization code received", "error")
            return redirect(url_for("auth.login_page"))

        logger.info(f"Authorization code received: {code[:8]}...")

        if provider == "github":
            # Manual token exchange for GitHub
            redirect_uri = url_for("oauth.callback", provider=provider, _external=True)
            access_token = exchange_github_code_for_token(code, redirect_uri)

            # Get user information
            user_info = get_github_user_info(access_token)

            logger.info(
                f"GitHub user authenticated: {user_info.get('login')} ({user_info.get('email')})"
            )

        # Create user session
        UserSession.create_user_session(user_info, provider)

        flash(f"Successfully logged in via {provider.upper()}!", "success")

        # Redirect to intended page or home
        next_page = session.pop("next_url", None)
        return redirect(next_page or "/assas_app/home")

    except Exception as e:
        logger.error(f"Callback error for {provider}: {e}")
        flash(f"Authentication error: {str(e)}", "error")
        return redirect(url_for("auth.login_page"))


@oauth_bp.route("/logout")
def logout():
    """Logout user and clear session."""
    provider = session.get("user", {}).get("provider")
    username = session.get("user", {}).get("username", "Unknown")

    # Clear all session data
    session.clear()

    logger.info(f"User {username} logged out from {provider}")
    flash("Successfully logged out", "info")

    return redirect(url_for("auth.login_page"))


@oauth_bp.route("/user-info")
def user_info():
    """Get current user information (API endpoint)."""
    if "user" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    return jsonify(session["user"])


@oauth_bp.route("/debug/session")
def debug_session():
    """Debug route to check session data."""
    if not current_app.debug:
        return jsonify({"error": "Debug mode disabled"}), 403

    return jsonify(
        {
            "session_keys": list(session.keys()),
            "user_authenticated": "user" in session,
            "user_data": session.get("user", {}),
            "oauth_states": {
                k: v for k, v in session.items() if k.startswith("oauth_state_")
            },
            "config": {
                "github_configured": bool(current_app.config.get("GITHUB_CLIENT_ID")),
                "secret_key_set": bool(current_app.config.get("SECRET_KEY")),
            },
        }
    )
