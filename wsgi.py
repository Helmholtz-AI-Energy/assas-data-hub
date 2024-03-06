"""Application entry point."""
import logging

from logging.handlers import RotatingFileHandler
from flask_app import init_app

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('assas_app')
handler = RotatingFileHandler('assas_app.log', maxBytes=10000, backupCount=10)
logger.addHandler(handler)

logger = logging.getLogger('assas_app')

app = init_app()

if __name__ == "__main__":

    app.logger.addHandler(handler)
    app.run(host='0.0.0.0', debug=True)