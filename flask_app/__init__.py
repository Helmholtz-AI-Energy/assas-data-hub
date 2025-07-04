"""Module to initialize the Flask application for the ASSAS Data Hub."""

import secrets

from flask import Flask
from flask.config import Config


class AttrConfig(Config):
    """Custom configuration class to allow attribute-like access to configuration keys.

    This class extends Flask's Config to allow accessing configuration values.

    Args:
        Config: The base configuration class from Flask.

    Example:
        app.config['DEBUG'] -> app.config.DEBUG

    """

    def __getattr__(self, key):
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

    def __dir__(self):
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


def init_app():
    """Construct core Flask application with embedded Dash app."""
    app = CustomFlask(__name__, instance_relative_config=False)

    app.secret_key = secrets.token_hex(16)

    app.config.from_object("config.Config")

    with app.app_context():
        # Import parts of our core Flask app
        from . import routes  # noqa: F401

        # Import Dash application
        from .dash_app.app import init_dashboard

        app = init_dashboard(app)

        return app
