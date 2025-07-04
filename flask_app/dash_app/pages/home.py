"""Home page for the ASSAS Data Hub Dash application.

This page provides an introduction to the ASSAS Data Hub, including a brief description
of its purpose, a link to the ASSAS Training Dataset Index, and an image
illustrating the system.
"""

import dash

from dash import html, dcc
from ..components import content_style, encode_svg_image

dash.register_page(__name__, path="/home")


def layout():
    """Layout for the Home page."""
    return html.Div(
        [
            html.Hr(),
            html.H1("ASSAS Database - ASSAS Data Hub"),
            html.H5(
                (
                    "ASSAS Data Hub is a software platform to store and visualize "
                    "training datasets for ASTEC simulations."
                )
            ),
            html.H5("ASSAS Training Datasets stored on the LSDF at the KIT."),
            html.Div(
                dcc.Link("ASSAS Training Dataset Index", href="/assas_app/database")
            ),
            html.Img(
                src=encode_svg_image("assas_introduction.drawio.svg"),
                height="600px",
                width="600px",
            ),
            html.Hr(),
        ],
        style=content_style(),
    )
