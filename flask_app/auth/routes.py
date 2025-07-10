"""Authentication routes with profile page."""

from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from ..auth_utils import is_authenticated, get_current_user

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login')
def login_page():
    """Display login page."""
    if is_authenticated():
        # Fix: Redirect to Dash app home instead of non-existent Flask route
        return redirect('/assas_app/')
    
    return render_template('auth/login.html')

@auth_bp.route('/profile')
def profile():
    """User profile page (Flask route - redirects to Dash page)."""
    if not is_authenticated():
        return redirect(url_for('auth.login_page'))
    
    # Redirect to Dash profile page
    return redirect('/assas_app/profile')

# Add this debug route to your auth routes

@auth_bp.route('/debug/oauth-urls')
def debug_oauth_urls():
    """Debug OAuth URLs to identify redirect_uri mismatch."""
    from flask import url_for, current_app
    
    debug_info = {
        'current_request': {
            'host': request.host,
            'scheme': request.scheme,
            'base_url': request.base_url,
            'url_root': request.url_root
        },
        'flask_config': {
            'SERVER_NAME': current_app.config.get('SERVER_NAME'),
            'PREFERRED_URL_SCHEME': current_app.config.get('PREFERRED_URL_SCHEME', 'http'),
            'APPLICATION_ROOT': current_app.config.get('APPLICATION_ROOT', '/')
        },
        'oauth_settings': {
            'github_client_id': current_app.config.get('GITHUB_CLIENT_ID', 'Not set'),
            'github_configured': bool(current_app.config.get('GITHUB_CLIENT_ID')),
            'bwidm_configured': bool(current_app.config.get('BWIDM_CLIENT_ID'))
        }
    }
    
    # Generate OAuth callback URLs
    try:
        github_callback = url_for('oauth.callback', provider='github', _external=True)
        debug_info['generated_urls'] = {
            'github_callback': github_callback
        }
        
        if current_app.config.get('BWIDM_CLIENT_ID'):
            bwidm_callback = url_for('oauth.callback', provider='bwidm', _external=True)
            debug_info['generated_urls']['bwidm_callback'] = bwidm_callback
            
    except Exception as e:
        debug_info['url_generation_error'] = str(e)
    
    return jsonify(debug_info)

@auth_bp.route('/debug/oauth-config')
def debug_oauth_config():
    """Debug OAuth configuration."""
    from flask import current_app, jsonify
    
    if not current_app.debug:
        return jsonify({'error': 'Debug mode disabled'}), 403
    
    return jsonify({
        'github_client_id': current_app.config.get('GITHUB_CLIENT_ID', 'Not set'),
        'github_configured': bool(current_app.config.get('GITHUB_CLIENT_ID')),
        'bwidm_configured': bool(current_app.config.get('BWIDM_CLIENT_ID')),
        'current_host': request.host,
        'expected_callback_github': url_for('oauth.callback', provider='github', _external=True),
        'expected_callback_bwidm': url_for('oauth.callback', provider='bwidm', _external=True) if current_app.config.get('BWIDM_CLIENT_ID') else 'Not configured'
    })

@auth_bp.route('/debug/dash-access')
def debug_dash_access():
    """Debug Dash app access."""
    from flask import url_for
    
    current_user = get_current_user()
    
    debug_info = {
        'authenticated': is_authenticated(),
        'current_user': current_user,
        'session_keys': list(session.keys()),
        'dash_urls': {
            'home': '/assas_app/',
            'database': '/assas_app/database',
            'profile': '/assas_app/profile',
            'admin': '/assas_app/admin'
        }
    }
    
    return jsonify(debug_info)