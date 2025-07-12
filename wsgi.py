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
    app.logger.setLevel(logging.DEBUG)
    app.run(
            host="0.0.0.0",  # 🔧 CHANGED FROM localhost to 0.0.0.0
            port=5000,
            debug=True,
            threaded=True,
            use_reloader=True,
            use_debugger=False,  # 🔧 DISABLED Flask's debugger (we use Werkzeug's)
            passthrough_errors=False,  # Let Werkzeug handle errors
        )

    # 🔧 CONFIGURE DEBUG MODE BEFORE WRAPPING
    #app.config.update({
    #    "DEBUG": True,
    #    "DEVELOPMENT": True,
    #    "ENV": "development",
    #    "TESTING": False,
    #    "PROPAGATE_EXCEPTIONS": True,  # Important for debugger
    #})
    """
    # 🔧 WRAP WITH WERKZEUG DEBUGGER (FIXED INDENTATION)
    if app.config["DEBUG"]:
        app.wsgi_app = DebuggedApplication(
            app.wsgi_app, 
            evalex=True,  # Enable code evaluation in browser
            pin_security=False,  # Disable PIN for easier debugging (dev only!)
            show_hidden_frames=True,  # Show all frames
            #lodgeit_url=None  # Disable lodgeit
        )
        
        print("🔧" + "="*60)
        print("🔧 BROWSER DEBUGGER CONFIGURATION:")
        print("🔧 - Interactive debugger: ENABLED")
        print("🔧 - Code evaluation in browser: ENABLED") 
        print("🔧 - PIN security: DISABLED")
        print("🔧 - Host: 0.0.0.0 (accessible from network)")
        print("🔧 - Port: 5000")
        print("🔧" + "="*60)
        print("🔧 To test debugger:")
        print("🔧 1. Go to http://localhost:5000/debug/test-error")
        print("🔧 2. Click on traceback lines in error page")
        print("🔧 3. Execute Python code in browser console")
        print("🔧" + "="*60)

    if app.config["DEVELOPMENT"]:
        app.logger.info("🚀 Running in development mode with browser debugger")
        app.run(
            host="0.0.0.0",  # 🔧 CHANGED FROM localhost to 0.0.0.0
            port=5000,
            #debug=True,
            threaded=True,
            use_reloader=True,
            use_debugger=False,  # 🔧 DISABLED Flask's debugger (we use Werkzeug's)
            passthrough_errors=False,  # Let Werkzeug handle errors
        )
    else:
        app.logger.info("Running in production mode")
        app.run(host="/tmp/assas_app.sock", unix_socket=True, threaded=True)
    """
