"""Module to initialize the Flask application for the ASSAS Data Hub."""

import os
import secrets

from flask import Flask
from flask.config import Config
from werkzeug.middleware.proxy_fix import ProxyFix


class AttrConfig(Config):
    """Custom configuration class to allow attribute-like access to configuration keys.

    This class extends Flask's Config to allow accessing configuration values.

    Args:
        Config: The base configuration class from Flask.

    Example:
        app.config['DEBUG'] -> app.config.DEBUG

    """

    def __getattr__(self, key: str) -> object:
        """Override __getattr__ to allow attribute-like access to config keys.

        Args:
            key (str): The configuration key to access.

        Returns:
            The value of the configuration key.

        Raises:
            AttributeError: If the key does not exist in the configuration.

        """
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __dir__(self) -> list:
        """Override dir to include configuration keys in the directory listing.

        Returns:
            list: A sorted list of configuration keys and inherited attributes.

        """
        out = set(self.keys())
        out.update(super().__dir__())
        return sorted(out)


class CustomFlask(Flask):
    """Custom Flask class to use AttrConfig for configuration access.

    This class extends Flask to use the AttrConfig class for configuration,
    allowing for attribute-like access to configuration keys.

    Args:
        Flask: The base Flask class.

    Example:
        app = CustomFlask(__name__)
        app.config.DEBUG

    """

    config_class = AttrConfig


def init_app() -> CustomFlask:
    """Construct core Flask application with embedded Dash app."""
    app = CustomFlask(__name__, instance_relative_config=False)

    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1
    )

    # DEBUG TEST ROUTES
    @app.route("/debug/test-error")
    def test_error() -> str:
        """Trigger an error to test the browser debugger."""
        if app.debug:
            # This will show the interactive debugger in browser
            x = 1
            y = 0
            result = x / y  # This will cause ZeroDivisionError
            return f"Result: {result}"
        return "Debug mode not enabled", 403

    @app.route("/debug/info")
    def debug_info() -> str:
        """Show debug configuration info."""
        info = {
            "debug_mode": app.debug,
            "environment": app.config.get("ENV"),
            "werkzeug_debugger": hasattr(app, "wsgi_app"),
            "debugger_type": type(app.wsgi_app).__name__,
            "host": "0.0.0.0",
            "port": 5000,
        }
        return f"<pre>{info}</pre>"

    app.secret_key = secrets.token_hex(16)

    config_name = os.environ.get("FLASK_ENV", "development").lower()

    if config_name == "development":
        from config import DevelopmentConfig

        app.config.from_object(DevelopmentConfig)
        app.logger.info("Loaded DevelopmentConfig")
    elif config_name == "production":
        from config import ProductionConfig

        app.config.from_object(ProductionConfig)
        app.logger.info("Loaded ProductionConfig")
    else:
        # Default to development
        from config import DevelopmentConfig

        app.config.from_object(DevelopmentConfig)
        app.logger.info("Loaded DevelopmentConfig (default)")

    with app.app_context():
        # Import parts of our core Flask app
        from . import routes  # noqa: F401

        # Import Dash application
        from .dash_app.app import init_dashboard

        app = init_dashboard(app)

        return app
