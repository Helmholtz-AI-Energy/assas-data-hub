"""Dash Debugging.

To enable debugging for the Dash app,
set the `debug` parameter to `True` when running the app.
"""

from flask_app import init_app

# Initialize the full Flask app (with Dash attached)
app = init_app()

# Get the Dash app from the Flask app context
dash_app = getattr(app, "dash_app", None)
if dash_app is None:
    raise RuntimeError(
        "Dash app not found on Flask app. Make sure init_dashboard sets app.dash_app."
    )

# Run Dash in debug mode (this will use Flask's dev server)
dash_app.run(
    host="0.0.0.0",
    port=5000,
    debug=True,
    # threaded=True,
    # use_reloader=True,
    use_debugger=True,
    use_evalex=True,
)
