"""About page for the ASSAS Data Hub project."""

import dash

from dash import html, dcc
from ..components import content_style, encode_svg_image

dash.register_page(__name__, path="/about")


def layout() -> html.Div:
    """Layout for the About page."""
    return html.Div(
        [
            html.H1("About this Project"),
            html.Hr(),
            html.H5("Source Code available under "),
            html.Div(
                dcc.Link(
                    "https://github.com/Helmholtz-AI-Energy/assas-data-hub",
                    href="https://github.com/Helmholtz-AI-Energy/assas-data-hub",
                )
            ),
            html.Hr(),
            html.H4("System Overview"),
            html.Hr(),
            html.H5(
                (
                    "Python flask application displays "
                    "the available datasets archives on the LSDF."
                )
            ),
            html.Hr(),
            html.Img(
                src=encode_svg_image("assas_data_hub_system.drawio.svg"),
                height="600px",
                width="900px",
            ),
            html.Hr(),
            html.H4("Data Flow"),
            html.Hr(),
            html.Img(
                src=encode_svg_image("assas_data_flow.drawio.svg"),
                height="600px",
                width="900px",
            ),
        ],
        style=content_style(),
    )
