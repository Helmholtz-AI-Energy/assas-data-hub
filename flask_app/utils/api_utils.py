"""API utility functions and classes."""

import logging
import uuid
from typing import Dict, Any, Optional, Union, List

from flask import jsonify, Response

logger = logging.getLogger("assas_app")

DataType = Union[Dict[str, Any], List[Any], str, int, float, bool, None]


class APIResponse:
    """Standardized API response helper."""

    @staticmethod
    def success(
        data: Optional[DataType] = None,
        message: str = "Success",
        status_code: int = 200,
    ) -> Response:
        """Create a success response."""
        response_data = {
            "success": True,
            "message": message,
            "data": data,
        }
        return jsonify(response_data), status_code

    @staticmethod
    def error(message: str, status_code: int = 400, error_code: str = None) -> Response:
        """Create an error response."""
        response_data = {
            "success": False,
            "message": message,
            "error": {
                "code": error_code or f"E{status_code}",
                "message": message,
            },
        }
        return jsonify(response_data), status_code

    @staticmethod
    def not_found(message: str = "Resource not found") -> Response:
        """Create a 404 response."""
        return APIResponse.error(message, 404, "NOT_FOUND")

    @staticmethod
    def unauthorized(message: str = "Unauthorized access") -> Response:
        """Create a 401 response."""
        return APIResponse.error(message, 401, "UNAUTHORIZED")

    @staticmethod
    def forbidden(message: str = "Access forbidden") -> Response:
        """Create a 403 response."""
        return APIResponse.error(message, 403, "FORBIDDEN")

    @staticmethod
    def validation_error(message: str, details: Dict = None) -> Response:
        """Create a validation error response."""
        response_data = {
            "success": False,
            "message": message,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": message,
                "details": details or {},
            },
        }
        return jsonify(response_data), 422


def validate_uuid(uuid_string: str) -> Optional[uuid.UUID]:
    """Validate and convert UUID string."""
    try:
        return uuid.UUID(uuid_string)
    except (ValueError, TypeError):
        return None


def handle_api_error(
    exception: Exception, message: str = "An error occurred"
) -> Response:
    """Handle API errors consistently."""
    logger.error(f"{message}: {str(exception)}", exc_info=True)

    # You can add specific exception handling here
    if isinstance(exception, ValueError):
        return APIResponse.validation_error(str(exception))

    return APIResponse.error(message, 500, "INTERNAL_ERROR")


def paginate_query(query_params: Dict[str, Any]) -> Dict[str, Union[int, bool]]:
    """Extract pagination parameters from query."""
    limit = min(int(query_params.get("limit", 100)), 1000)
    offset = int(query_params.get("offset", 0))

    return {"limit": limit, "offset": offset, "has_pagination": limit > 0}
