"""Authentication routes with profile page."""

from flask import Blueprint, render_template, session, redirect, url_for
from ..auth_utils import is_authenticated, get_current_user

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login')
def login_page():
    """Display login page."""
    if is_authenticated():
        return redirect(url_for('dash_app.home'))
    
    return render_template('auth/login.html')

@auth_bp.route('/profile')
def profile():
    """User profile page (Flask route - redirects to Dash page)."""
    if not is_authenticated():
        return redirect(url_for('auth.login_page'))
    
    # Redirect to Dash profile page
    return redirect('/assas_app/profile')