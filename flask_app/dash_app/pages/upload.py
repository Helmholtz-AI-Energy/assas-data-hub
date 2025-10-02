"""Dash page for uploading files to LSDF (MinIO) using Uppy.

This page provides a user interface for uploading files to the LSDF
using the Uppy file uploader.
"""

import dash
from dash import html
from ...utils.url_utils import get_base_url

dash.register_page(__name__, path="/upload", name="Upload")

layout = html.Div(
    [
        html.H2("Upload to LSDF (MinIO)"),
        html.Iframe(
            src=f"{get_base_url()}/upload.html",  # Flask route serving your Uppy HTML
            style={"width": "100%", "height": "1600px", "border": "none"},
        ),
        html.Div(
            "For very large files/folders, "
            "use the command-line uploader for best reliability.",
            style={"marginTop": "2rem", "color": "#888"},
        ),
    ],
    style={"maxWidth": "1200px", "margin": "auto"},
)
