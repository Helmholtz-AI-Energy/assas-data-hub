"""Logout Page for the ASSAS Data Hub.

This page serves as a placeholder for the logout functionality.
"""

import dash

from dash import html
from ..components import content_style, encode_svg_image

dash.register_page(__name__, path="/logout")


def layout():
    """Layout for the Logout page."""
    return html.Div(
        [
            html.H1("ASSAS Database - ASSAS Data Hub"),
            html.H5("Logout Page"),
            html.Hr(),
            html.Img(
                src=encode_svg_image("assas_introduction.drawio.svg"),
                height="600px",
                width="600px",
            ),
            html.Hr(),
        ],
        style=content_style(),
    )
