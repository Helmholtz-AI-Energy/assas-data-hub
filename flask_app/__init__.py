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
    
    with app.app_context():
        # Import parts of our core Flask app
        from . import routes

        # Import Dash application
        from .dash_app.app import init_dashboard
        app = init_dashboard(app)

        return app
    
