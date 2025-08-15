"""Test session management."""

import sys
import os

project_root = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, project_root)

from flask_app import init_app
from flask import session


def test_session():
    """Test session configuration."""
    app = init_app()

    with app.test_client() as client:
        with client.session_transaction() as sess:
            print(f"Session lifetime: {app.permanent_session_lifetime}")
            print(f"Secret key set: {'Yes' if app.secret_key else 'No'}")
            print(f"Session cookie name: {app.config.get('SESSION_COOKIE_NAME')}")


if __name__ == "__main__":
    test_session()
