"""Details template page for displaying metadata of a report.

This page retrieves a report by its ID and displays its metadata in a table format.
"""

import dash
import dash_bootstrap_components as dbc
import logging

from flask import current_app as app
from dash import html, Input, Output, State, callback

from assasdb import AssasDatabaseManager, AssasDatabaseHandler
from ..components import content_style
from ...utils.url_utils import get_base_url
from ...auth_utils import get_current_user

logger = logging.getLogger("assas_app")

dash.register_page(__name__, path_template="/details/<report_id>")


def meta_info_table(document: dict) -> dbc.Table:
    """Generate a table displaying metadata information from the document."""
    general_header = [
        html.Thead(html.Tr([html.Th("NetCDF4 Dataset Attribute"), html.Th("Value")]))
    ]

    general_body = [
        html.Tbody(
            [
                html.Tr([html.Td("Name"), html.Td(document["meta_name"])]),
                html.Tr(
                    [html.Td("Description"), html.Td(document["meta_description"])]
                ),
            ]
        )
    ]

    data_header = [
        html.Thead(
            html.Tr(
                [
                    html.Th("NetCDF4 Variable Name"),
                    html.Th("Domain"),
                    html.Th("Dimensions"),
                    html.Th("Shape"),
                ]
            )
        )
    ]

    meta_data_variables = document.get("meta_data_variables")

    if meta_data_variables is None:
        table = general_header + general_body
        return dbc.Table(
            table,
            striped=True,
            bordered=True,
            hover=True,
            responsive=True,
            className="mb-4",
        )

    data_meta = []
    for meta_data in meta_data_variables:
        logger.debug(f"meta_data entry: {meta_data}")
        data_meta.append(
            html.Tr(
                [
                    html.Td(meta_data["name"]),
                    html.Td(meta_data["domain"]),
                    html.Td(meta_data["dimensions"]),
                    html.Td(meta_data["shape"]),
                ]
            )
        )

    data_body = [html.Tbody(data_meta)]

    table = general_header + general_body + data_header + data_body

    return dbc.Table(
        table,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        className="mb-4",
    )


def layout(report_id: str | None = None) -> html.Div:
    """Layout for the details template page."""
    logger.info(f"report_id {report_id}")

    if (report_id == "none") or (report_id is None):
        return html.Div(
            [
                html.H1("Data Details"),
                html.Div("The content is generated for each dataset."),
            ],
            style=content_style(),
        )
    else:
        document = AssasDatabaseManager(
            database_handler=AssasDatabaseHandler(
                database_name=app.config["MONGO_DB_NAME"],
            )
        ).get_database_entry_by_uuid(report_id)

        logger.info(f"Found document {document}")
        base_url = get_base_url()
        datacite_url = f"{base_url}/files/datacite/{report_id}"

        current_user = get_current_user()
        show_edit = "admin" in current_user.get(
            "roles", []
        ) or "curator" in current_user.get("roles", [])
        logger.info(f"Show edit section: {show_edit}")

        return html.Div(
            [
                html.Div(
                    [
                        html.H2(
                            f"Dataset Details: {document.get('meta_name', report_id)}",
                            style={
                                "fontWeight": "bold",
                                "color": "#2c3e50",
                                "marginBottom": "0.5rem",
                                "fontFamily": "Arial, sans-serif",
                            },
                        ),
                        html.P(
                            document.get("meta_description", ""),
                            style={
                                "fontSize": "1.1rem",
                                "color": "#444",
                                "marginBottom": "1.5rem",
                            },
                        ),
                        dbc.Button(
                            [
                                html.I(className="fas fa-download me-2"),
                                "Show DataCite JSON",
                            ],
                            href=datacite_url,
                            color="primary",
                            outline=True,
                            external_link=True,
                            target="_blank",
                            style={"marginBottom": "1.5rem"},
                        ),
                        (
                            html.Div(
                                [
                                    dbc.Button(
                                        "Edit Metadata",
                                        id="toggle-edit-metadata",
                                        color="warning",
                                        outline=True,
                                        style={"marginBottom": "1rem"},
                                    ),
                                    html.Div(
                                        id="edit-metadata-section",
                                        children=[],
                                        style={"display": "none"},
                                    ),
                                ]
                            )
                            if show_edit
                            else None
                        ),
                    ],
                    style={
                        "textAlign": "center",
                        "marginBottom": "2rem",
                        "backgroundColor": "#f8f9fa",
                        "padding": "2rem",
                        "borderRadius": "12px",
                        "boxShadow": "0 2px 8px rgba(0,0,0,0.07)",
                    },
                ),
                html.H4(
                    "NetCDF4 Metadata",
                    style={
                        "color": "#007bff",
                        "marginTop": "2rem",
                        "marginBottom": "1rem",
                        "fontWeight": "bold",
                    },
                ),
                meta_info_table(document),
            ],
            style={
                **content_style(),
                "maxWidth": "900px",
                "margin": "2rem auto",
                "backgroundColor": "#fff",
                "borderRadius": "16px",
                "boxShadow": "0 4px 24px rgba(0,0,0,0.08)",
                "padding": "2.5rem 2rem",
            },
        )


# Callback to toggle and show the edit form
@callback(
    Output("edit-metadata-section", "style"),
    Output("edit-metadata-section", "children"),
    Input("toggle-edit-metadata", "n_clicks"),
    State("edit-metadata-section", "style"),
    prevent_initial_call=True,
)
def toggle_edit_metadata(n_clicks: int, current_style: dict) -> tuple[dict, list]:
    """Toggle the visibility of the edit metadata form."""
    if n_clicks is None:
        return {"display": "none"}, []
    # Toggle display and show form if visible
    if current_style.get("display") == "none":
        # Show form
        return (
            {"display": "block"},
            [
                dbc.Form(
                    [
                        dbc.Label("Name"),
                        dbc.Input(id="edit-meta-name", type="text"),
                        dbc.Label("Description", style={"marginTop": "1rem"}),
                        dbc.Textarea(
                            id="edit-meta-description", style={"height": "100px"}
                        ),
                        dbc.Button(
                            "Save Changes",
                            id="save-meta-btn",
                            color="success",
                            style={"marginTop": "1rem"},
                        ),
                        html.Div(id="edit-meta-feedback", style={"marginTop": "1rem"}),
                    ]
                )
            ],
        )
    else:
        # Hide form
        return {"display": "none"}, []
