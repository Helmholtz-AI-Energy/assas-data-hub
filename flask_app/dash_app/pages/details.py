"""Details Page for Dash Application.

This page serves as a placeholder for the details section of the application.
It includes a header and a content area styled with a predefined style.
"""

import dash

from dash import html
from ..components import content_style

dash.register_page(__name__, path="/details")


def layout() -> html.Div:
    """Layout for the Details page."""
    return html.Div(
        [
            html.H1("This is our Details page"),
            html.Div("This is our Details page content."),
        ],
        style=content_style(),
    )
