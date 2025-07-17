"""Application entry point."""

import logging
import sys
import os

from logging.handlers import RotatingFileHandler
from werkzeug.debug import DebuggedApplication
from flask_app import init_app

logger = logging.getLogger("assas_app")

# Set logging to DEBUG level for better debugging
logging.basicConfig(
    format="%(asctime)s %(process)d %(module)s %(levelname)s: %(message)s",
    level=logging.DEBUG,  # Changed to DEBUG
    stream=sys.stdout,
)

handler = RotatingFileHandler("assas_app.log", maxBytes=100000, backupCount=10)
formatter = logging.Formatter(
    "%(asctime)s - %(process)d - %(module)s - %(levelname)s: %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)

app = init_app()

if __name__ == "__main__":
    app.logger.addHandler(handler)

    if app.config["DEVELOPMENT"]:
        app.logger.setLevel(logging.DEBUG)
        app.logger.info("🚀 Running in development mode with browser debugger")
        app.run(
            host="0.0.0.0",
            port=5000,
            debug=True,
            threaded=True,
            use_reloader=True,
            use_debugger=True,  # Enable Werkzeug's debugger
        )
    else:
        app.logger.info("Running in production mode")
        app.run(host="/tmp/assas_app.sock", unix_socket=True, threaded=True)

