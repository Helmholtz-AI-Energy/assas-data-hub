"""Imprint (Impressum) page for the ASSAS Data Hub."""

import dash
from dash import html
from ..components import content_style

dash.register_page(__name__, path="/imprint")


def layout() -> html.Div:
    """Layout for the Imprint page."""
    return html.Div(
        [
            html.H1(
                "Imprint / Legal Notice", style={"fontFamily": "Arial, sans-serif"}
            ),
            html.Hr(),
            html.Div(
                [
                    html.H4(
                        "Provider according to § 5 TMG", style={"marginTop": "1.5rem"}
                    ),
                    html.P(
                        [
                            "Karlsruhe Institute of Technology (KIT)",
                            html.Br(),
                            "Scientific Center for Computing (SCC)",
                            html.Br(),
                            "Hermann-von-Helmholtz-Platz 1",
                            html.Br(),
                            "76344 Eggenstein-Leopoldshafen",
                            html.Br(),
                            "Germany",
                        ]
                    ),
                    html.H4("Contact", style={"marginTop": "1.5rem"}),
                    html.P(
                        [
                            "Email: jonas.dressner@kit.edu",
                            html.Br(),
                            "Phone: +49 721 608-0",
                            html.Br(),
                            html.A(
                                "https://www.kit.edu",
                                href="https://www.kit.edu",
                                target="_blank",
                            ),
                        ]
                    ),
                    html.H4("Represented by", style={"marginTop": "1.5rem"}),
                    html.P(["Prof. Dr. Holger Hanselka (President of KIT)"]),
                    html.H4(
                        "Responsible for content according to § 55 Abs. 2 RStV",
                        style={"marginTop": "1.5rem"},
                    ),
                    html.P(
                        [
                            "Marcus Goetz?",
                            html.Br(),
                            "Scientific Center for Computing (SCC)",
                            html.Br(),
                            "Address as above",
                        ]
                    ),
                    html.H4("Disclaimer", style={"marginTop": "1.5rem"}),
                    html.P(
                        "Despite careful content control, we assume no "
                        "liability for the content of external links. "
                        "The operators of the linked pages are solely "
                        "responsible for their content."
                    ),
                ],
                style={
                    "backgroundColor": "#f8f9fa",
                    "border": "1px solid #e9ecef",
                    "borderRadius": "8px",
                    "padding": "1.5rem",
                    "margin": "1rem 0",
                    "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.05)",
                    "fontFamily": "Arial, sans-serif",
                },
            ),
        ],
        style=content_style(),
    )
