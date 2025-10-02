"""Visitor page for users without AARC entitlement."""

import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(
    __name__,
    path="/visitor",
    title="Visitor Access - ASSAS Data Hub",
    description="Landing page for users without AARC entitlement.",
)

layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        html.H1(
                            "Welcome to the ASSAS Data Hub",
                            style={"textAlign": "center"},
                        ),
                        html.P(
                            "You are currently visiting as a guest. "
                            "To access full features, please contact support.",
                            style={"textAlign": "center"},
                        ),
                        html.P(
                            [
                                "Contact ",
                                html.A("support", href="mailto:jonas.dressner@kit.edu"),
                                " for access.",
                            ],
                            style={"textAlign": "center", "marginTop": "2rem"},
                        ),
                    ],
                    style={
                        "backgroundColor": "#f8f9fa",
                        "border": "1px solid #e1e1e1",
                        "borderRadius": "8px",
                        "padding": "2rem",
                        "maxWidth": "800px",
                        "margin": "2rem auto",
                        "boxShadow": "0 2px 8px rgba(0,0,0,0.05)",
                    },
                ),
                width=12,
            )
        ),
    ],
    fluid=True,
    style={"paddingTop": "3rem", "paddingBottom": "3rem"},
)
