"""Serve the upload HTML page."""

from flask import Blueprint, make_response, render_template
from ...utils.url_utils import get_base_url

upload_html_bp = Blueprint("upload_html", __name__)
upload_html_bp.url_prefix = get_base_url()


@upload_html_bp.route("/upload.html")
def upload_html() -> make_response:
    """Render the upload HTML page."""
    base_url = get_base_url()
    resp = make_response(render_template("upload.html", base_url=base_url))
    resp.headers["X-Frame-Options"] = "ALLOWALL"
    return resp
