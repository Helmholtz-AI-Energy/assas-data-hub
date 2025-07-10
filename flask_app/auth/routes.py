"""Authentication routes."""

from flask import Blueprint, render_template, session, redirect, url_for
from ..auth_utils import is_authenticated

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login')
def login_page():
    """Display login page."""
    if is_authenticated():
        return redirect(url_for('dash_app.home'))
    
    return render_template('auth/login.html')

@auth_bp.route('/profile')
def profile():
    """User profile page."""
    if not is_authenticated():
        return redirect(url_for('auth.login_page'))
    
    return render_template('auth/profile.html', user=session['user'])