"""Application entry point."""

import logging
import sys

from logging.handlers import RotatingFileHandler
from flask_app import init_app

logger = logging.getLogger("assas_app")

logging.basicConfig(
    format="%(asctime)s %(process)d %(module)s %(levelname)s: %(message)s",
    level=logging.INFO,
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
    app.run(host="0.0.0.0", port=5000)
