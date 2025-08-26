"""Blueprint registration utilities."""

import logging

from typing import Union
from flask import Blueprint, Flask

logger = logging.getLogger(__name__)


def safe_register_blueprint(
    app: Flask, blueprint: Blueprint, **options: Union[str, dict, bool, None]
) -> bool:
    """Safely register a blueprint, avoiding duplicates."""
    blueprint_name = blueprint.name

    if blueprint_name in app.blueprints:
        logger.warning(f"Blueprint '{blueprint_name}' already registered, skipping")
        return False

    app.register_blueprint(blueprint, **options)
    logger.info(f"Blueprint '{blueprint_name}' registered successfully")
    return True
