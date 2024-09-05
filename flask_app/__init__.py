import os

'''Initialize Flask app.'''
from flask import Flask
from flask.app import Flask
from flask.config import Config

class AttrConfig(Config):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __dir__(self):
        out = set(self.keys())
        out.update(super().__dir__())
        return sorted(out)

class CustomFlask(Flask):
    config_class = AttrConfig

def init_app():
    '''Construct core Flask application with embedded Dash app.'''
    app = CustomFlask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')
    
    app.config['OAUTH2_PROVIDERS'] = {
        # Google OAuth 2.0 documentation:
        # https://developers.google.com/identity/protocols/oauth2/web-server#httprest
        'google': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
            'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
            'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
            'token_url': 'https://accounts.google.com/o/oauth2/token',
            'userinfo': {
                'url': 'https://www.googleapis.com/oauth2/v3/userinfo',
                'email': lambda json: json['email'],
            },
            'scopes': ['https://www.googleapis.com/auth/userinfo.email'],
        },

        # GitHub OAuth 2.0 documentation:
        # https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps
        'github': {
            'client_id': os.environ.get('GITHUB_CLIENT_ID'),
            'client_secret': os.environ.get('GITHUB_CLIENT_SECRET'),
            'authorize_url': 'https://github.com/login/oauth/authorize',
            'token_url': 'https://github.com/login/oauth/access_token',
            'userinfo': {
                'url': 'https://api.github.com/user/emails',
                'email': lambda json: json[0]['email'],
            },
            'scopes': ['user:email'],
        },
    }

    with app.app_context():
        # Import parts of our core Flask app
        from . import routes

        # Import Dash application
        from .dash_app.app import init_dashboard
        app = init_dashboard(app)

        return app
    
