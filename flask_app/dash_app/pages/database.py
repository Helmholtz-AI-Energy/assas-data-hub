"""ASSAS Database Page.

This module provides the layout and functionality for the ASSAS Database page,
which allows users to view, search, and download datasets from the ASSAS training
dataset index.
"""

import os
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import logging
import shutil
import math

from pymongo import MongoClient
from dash import dash_table, html, dcc, Input, Output, callback, State, callback_context
from flask import current_app as app
from zipfile import ZipFile
from uuid import uuid4
from pathlib import Path
from typing import List

from assasdb import AssasDatabaseManager, AssasDatabaseHandler
from ..components import content_style, conditional_table_style, responsive_table_style
from ..components import ultra_minimal_style, full_width_style

# Define a common style dictionary
COMMON_STYLE = {
    "fontSize": "18px",
    "textAlign": "center",
    "margin": "1% auto",
    "padding": "10px",
    "width": "100%",
    "fontFamily": "arial, sans-serif",
}

# Define responsive layout using Bootstrap classes
RESPONSIVE_STYLE = {
    "width": "100%",
    "padding-left": "5%",
    "padding-right": "5%",
}

logger = logging.getLogger("assas_app")

colors = {"background": "#111111", "text": "#7FDBFF"}

operators = [
    ["ge ", ">="],
    ["le ", "<="],
    ["lt ", "<"],
    ["gt ", ">"],
    ["ne ", "!="],
    ["eq ", "="],
    ["contains "],
    ["datestartswith "],
]


def update_table_data() -> pd.DataFrame:
    """Update the table data from the database.

    Returns:
        pd.DataFrame: DataFrame with the table data.

    """
    logger.info("Load database entries to table.")

    database_manager = AssasDatabaseManager(
        database_handler = AssasDatabaseHandler(
            client=MongoClient(app.config["CONNECTIONSTRING"]),
            backup_directory=app.config["BACKUP_DIRECTORY"],
            database_name=app.config["MONGO_DB_NAME"],
        )
    )

    table_data_local = database_manager.get_all_database_entries()
    table_data_local["system_download"] = [
        f'<a href="/assas_app/hdf5_file?uuid={entry.system_uuid}">hdf5 file</a>'
        if entry.system_status == "Valid"
        else "no hdf5 file available"
        for entry in table_data_local.itertuples()
    ]
    table_data_local["meta_name"] = [
        f'<a href="/assas_app/details/{entry.system_uuid}">{entry.meta_name}</a>'
        for entry in table_data_local.itertuples()
    ]

    return table_data_local


def get_database_size() -> str:
    """Get the overall size of the ASSAS database.

    Returns:
        str: Overall size of the database in a human-readable format.

    """
    database_manager = AssasDatabaseManager(
        database_handler=AssasDatabaseHandler(
            client=MongoClient(app.config["CONNECTIONSTRING"]),
            backup_directory=app.config["BACKUP_DIRECTORY"],
            database_name=app.config["MONGO_DB_NAME"],
        )
    )
    size = database_manager.get_overall_database_size()

    if size is None or len(size) == 0:
        return "0 B"

    return size


table_data = update_table_data()
database_size = get_database_size()
now = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

ALL = len(table_data)
PAGE_SIZE = 30
PAGE_MAX_SIZE = 100

PAGE_COUNT = ALL / PAGE_SIZE

dash.register_page(__name__, path="/database")


# Updated modern style dictionary
MODERN_STYLE = {
    "fontFamily": "Arial, sans-serif",
    "fontSize": "16px",
    "color": "#2c3e50",
    "lineHeight": "1.6",
}

CARD_STYLE = {
    "backgroundColor": "#ffffff",
    "border": "1px solid #e0e6ed",
    "borderRadius": "8px",
    "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.1)",
    "padding": "1.5rem",
    "marginBottom": "1.5rem",
    "transition": "all 0.3s ease",
}

BUTTON_STYLE = {
    "fontFamily": "Arial, sans-serif",
    "fontWeight": "600",
    "borderRadius": "6px",
    "padding": "12px 24px",
    "fontSize": "14px",
    "transition": "all 0.3s ease",
    "border": "none",
    "cursor": "pointer",
}

def layout() -> html.Div:
    """Layout for the ASSAS Database page.

    Returns:
        html.Div: The layout of the ASSAS Database page.

    """
    return html.Div([
        # Header Section
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1(
                        "ASSAS Database Training Dataset Index",
                        className="display-4 fw-bold text-primary mb-3 text-center",                        
                    ),
                    html.H2(
                        "Browse, Search, and Download Machine Learning Training Datasets",
                        className="text-secondary mb-4 text-center",
                        style={"fontSize": "1.5rem", "fontWeight": "400"}
                    ),
                    html.Div([
                        dbc.Button([
                            html.I(className="fas fa-question-circle me-2"),
                            "Usage Guide & Instructions"
                        ],
                        id="toggle-usage-guide",
                        color="primary",
                        outline=False,
                        size="lg",
                        className="w-100 mb-3",
                        style={
                            **BUTTON_STYLE,
                            "backgroundColor": "#17a2b8",
                            "borderColor": "#17a2b8",
                            "color": "#ffffff"
                        }
                        ),
                        
                        dbc.Collapse([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4("How to Use This Database Interface", 
                                           className="text-primary mb-4", 
                                           style={"fontSize": "1.4rem", "fontWeight": "600"}),
                                    
                                    dbc.Row([
                                        dbc.Col([
                                            html.H5("🔍 Searching & Filtering", className="text-secondary mb-3"),
                                            html.Ul([
                                                html.Li([
                                                    html.Strong("Sort columns: "), 
                                                    "Click on column headers to sort data in ascending or descending order"
                                                ], className="mb-2"),
                                                html.Li([
                                                    html.Strong("Filter data: "), 
                                                    "Use the filter boxes that appear when you hover over column headers"
                                                ], className="mb-2"),
                                                html.Li([
                                                    html.Strong("Filter operators: "), 
                                                    html.Code("contains"), ", ", html.Code("="), ", ", 
                                                    html.Code(">"), ", ", html.Code("<"), ", ", html.Code("!=")
                                                ], className="mb-2"),
                                                html.Li([
                                                    html.Strong("Examples: "), 
                                                    "Type 'Valid' in Status filter, or '>2024-01-01' in Date filter"
                                                ], className="mb-2"),
                                            ], style={"fontSize": "0.9rem"})
                                        ], md=6),
                                        
                                        dbc.Col([
                                            html.H5("📄 Navigation & Settings", className="text-secondary mb-3"),
                                            html.Ul([
                                                html.Li([
                                                    html.Strong("Navigate pages: "), 
                                                    "Use pagination controls below to browse through datasets"
                                                ], className="mb-2"),
                                                html.Li([
                                                    html.Strong("Adjust page size: "), 
                                                    "Change entries per page (1-100) using the input field"
                                                ], className="mb-2"),
                                                html.Li([
                                                    html.Strong("Page information: "), 
                                                    "Shows current page number and total records displayed"
                                                ], className="mb-2"),
                                                html.Li([
                                                    html.Strong("Auto-reset: "), 
                                                    "Pagination resets to page 1 when filtering or changing page size"
                                                ], className="mb-2"),
                                            ], style={"fontSize": "0.9rem"})
                                        ], md=6)
                                    ]),
                                    
                                    html.Hr(className="my-4"),
                                    
                                    dbc.Row([
                                        dbc.Col([
                                            html.H5("📥 Downloading Datasets", className="text-secondary mb-3"),
                                            html.Ul([
                                                html.Li([
                                                    html.Strong("Select datasets: "), 
                                                    "Click checkboxes in the leftmost column to select datasets"
                                                ], className="mb-2"),
                                                html.Li([
                                                    html.Strong("Bulk download: "), 
                                                    "Click 'Database Tools' to expand download options (max 20 datasets)"
                                                ], className="mb-2"),
                                                html.Li([
                                                    html.Strong("Individual downloads: "), 
                                                    "Use download links in the 'Download' column for single files"
                                                ], className="mb-2"),
                                                html.Li([
                                                    html.Strong("ZIP format: "), 
                                                    "Bulk downloads are provided as compressed ZIP archives"
                                                ], className="mb-2"),
                                            ], style={"fontSize": "0.9rem"})
                                        ], md=6),
                                        
                                        dbc.Col([
                                            html.H5("🔗 Additional Features", className="text-secondary mb-3"),
                                            html.Ul([
                                                html.Li([
                                                    html.Strong("Dataset details: "), 
                                                    "Click on dataset names to view comprehensive information"
                                                ], className="mb-2"),
                                                html.Li([
                                                    html.Strong("Refresh data: "), 
                                                    "Use the refresh button in Database Tools to reload the latest data"
                                                ], className="mb-2"),
                                                html.Li([
                                                    html.Strong("Storage statistics: "), 
                                                    "View database usage information in the Database Tools section"
                                                ], className="mb-2"),
                                                html.Li([
                                                    html.Strong("Responsive design: "), 
                                                    "Interface adapts to different screen sizes and devices"
                                                ], className="mb-2"),
                                            ], style={"fontSize": "0.9rem"})
                                        ], md=6)
                                    ]),
                                    
                                    dbc.Alert([
                                        html.I(className="fas fa-lightbulb me-2"),
                                        html.Strong("Pro Tip: "), 
                                        "Use filters to narrow down datasets before selecting for download. "
                                        "This makes it easier to find and download exactly what you need!"
                                    ], color="success", className="mt-4")
                                ])
                            ], style={
                                **CARD_STYLE,
                                "backgroundColor": "#f8f9fa",
                                "border": "1px solid #dee2e6"
                            })
                        ], id="collapse-usage-guide", is_open=False)
                    ], className="mb-4")
                ])
            ])
        ], fluid=True, className="mb-4"),
        
        # Database Tools Section
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Button([
                        html.I(className="fas fa-tools me-2"),
                        "Database Tools"
                    ],
                    id="toggle-section",
                    color="primary",
                    size="lg",
                    className="w-100 mb-3",
                    style=BUTTON_STYLE
                    ),
                    
                    dbc.Collapse([
                        dbc.Card([
                            dbc.CardBody([
                                dbc.Row([
                                    # Download Section
                                    dbc.Col([
                                        html.H5([
                                            html.I(className="fas fa-download me-2 text-primary"),
                                            "Download Datasets"
                                        ], className="mb-3"),
                                        dcc.Loading([
                                            dbc.Button([
                                                html.I(className="fas fa-file-archive me-2"),
                                                "Get Download Link"
                                            ],
                                            id="download_selected",
                                            color="success",
                                            size="lg",
                                            disabled=True,
                                            className="w-100 mb-3",
                                            style=BUTTON_STYLE
                                            )
                                        ], type="default"),
                                        html.Div(
                                            "Select datasets in the table to enable download",
                                            id="download_selected_info",
                                            className="text-muted small text-center mb-2"
                                        ),
                                        dbc.Alert([
                                            html.I(className="fas fa-exclamation-triangle me-2"),
                                            "Maximum 20 datasets per download"
                                        ], color="warning", className="small")
                                    ], md=4),
                                    
                                    # Refresh Section
                                    dbc.Col([
                                        html.H5([
                                            html.I(className="fas fa-sync-alt me-2 text-primary"),
                                            "Refresh Data"
                                        ], className="mb-3"),
                                        dbc.Button([
                                            html.I(className="fas fa-refresh me-2"),
                                            "Refresh"
                                        ],
                                        id="reload_page",
                                        color="info",
                                        size="lg",
                                        className="w-100 mb-3",
                                        style=BUTTON_STYLE
                                        ),
                                        html.Div([
                                            html.Strong("Datasets loaded: "),
                                            html.Span(f"{len(table_data)}", className="text-primary")
                                        ], id="dataset_count", className="text-center mb-2"),
                                        html.Div(
                                            f"Last updated: {now}",
                                            id="database_update_time",
                                            className="text-muted small text-center"
                                        )
                                    ], md=4),
                                    
                                    # Storage Info Section
                                    dbc.Col([
                                        html.H5([
                                            html.I(className="fas fa-hdd me-2 text-primary"),
                                            "Storage Information"
                                        ], className="mb-3"),
                                        dbc.Table([
                                            html.Tbody([
                                                html.Tr([
                                                    html.Td("Used Storage", className="fw-bold"),
                                                    html.Td(database_size, className="text-end")
                                                ]),
                                                html.Tr([
                                                    html.Td("Storage Limit", className="fw-bold"),
                                                    html.Td("100 TB", className="text-end")
                                                ])
                                            ])
                                        ], striped=True, hover=True, className="mb-0")
                                    ], md=4)
                                ]),
                                
                                # Download Link Section
                                dbc.Row([
                                    dbc.Col([
                                        html.Hr(),
                                        html.Div([
                                            html.H6("Download Link:", className="mb-2"),
                                            html.Div(
                                                "Download link will appear here after selection",
                                                id="download_link",
                                                className="text-center p-3 bg-light rounded"
                                            )
                                        ])
                                    ])
                                ])
                            ])
                        ], style=CARD_STYLE)
                    ], id="collapse-section", is_open=False)
                ])
            ])
        ], fluid=True, className="mb-4"),
        
        # Data Table Section - WITH INTEGRATED PAGINATION
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4([
                                html.I(className="fas fa-table me-2"),
                                "Dataset Overview"
                            ], className="mb-0 text-primary", style={"fontSize": "1.5rem"})
                        ], style={"padding": "1.5rem", "backgroundColor": "#f8f9fa"}),
                        dbc.CardBody([
                            # Pagination and Page Info - SIDE BY SIDE
                            dbc.Row([
                                dbc.Col([
                                    html.Div([
                                        html.H6("Navigation", className="mb-2 text-secondary"),
                                        dbc.Pagination(
                                            id="pagination",
                                            first_last=True,
                                            previous_next=True,
                                            max_value=int(PAGE_COUNT),
                                            fully_expanded=False,
                                            size="lg",
                                            className="justify-content-center mb-2"
                                        ),
                                        html.Small([
                                            html.I(className="fas fa-info-circle me-1"),
                                            html.Span(
                                                "Page 1/10",
                                                id="pagination-contents"
                                            )
                                        ], className="text-muted text-center d-block",
                                           style={"fontSize": "0.7rem"})
                                    ], style={"textAlign": "center"})
                                ], md=8),  # REDUCED FROM 12 TO 8
                                dbc.Col([
                                    html.Div([
                                        html.H6("Table Settings", className="mb-3 text-secondary"),
                                        #dcc.Checklist(
                                        #    id="datatable-use-page-size",
                                        #    options=[{"label": " Enable custom page size", "value": "True"}],
                                        #    value=["False"],
                                        #    className="mb-3",
                                        #    style={"fontSize": "15px"}
                                        #),
                                        dbc.InputGroup([
                                            dbc.InputGroupText([
                                                html.I(className="fas fa-list-ol me-2"),
                                                "Entries per page:"
                                            ]),
                                            dbc.Input(
                                                id="datatable-page-size",
                                                type="number",
                                                min=1,
                                                max=PAGE_MAX_SIZE,
                                                value=PAGE_SIZE,
                                                placeholder=str(PAGE_SIZE),
                                                disabled=False,
                                                size="lg"
                                            )
                                        ], size="lg", className="mb-3")
                                    ])
                                ], md=4),                               
                            ], className="mb-4"),                            
                
                            # Enhanced Table Container
                            html.Div([
                                dash_table.DataTable(
                                    id="datatable-paging-and-sorting",
                                    columns=[
                                        {
                                            "name": "Index",
                                            "id": "system_index",
                                            "selectable": True,
                                            "type": "numeric",
                                        },
                                        {
                                            "name": "Dataset Name",
                                            "id": "meta_name",
                                            "selectable": True,
                                            "presentation": "markdown",            
                                        },
                                        {
                                            "name": "Status",
                                            "id": "system_status",
                                            "selectable": True,
                                            "type": "text"
                                        },
                                        {
                                            "name": "Date Created",
                                            "id": "system_date",
                                            "selectable": True,
                                            "type": "datetime"
                                        },
                                        {
                                            "name": "User",
                                            "id": "system_user",
                                            "selectable": True,
                                            "type": "text"
                                        },
                                        {
                                            "name": "Binary Size",
                                            "id": "system_size",
                                            "selectable": True,
                                            "type": "text"
                                        },
                                        {
                                            "name": "HDF5 Size",
                                            "id": "system_size_hdf5",
                                            "selectable": True,
                                            "type": "text"
                                        },
                                        {
                                            "name": "Download",
                                            "id": "system_download",
                                            "selectable": True,
                                            "presentation": "markdown"
                                        },
                                    ],
                                    #data=table_data.to_dict("records"),
                                    data=[],
                                    style_table={
                                        "width": "100%",
                                        "height": "auto",
                                        "overflowX": "auto",
                                        "overflowY": "visible",
                                    },
                                    style_header={
                                        "backgroundColor": "#007bff",
                                        "color": "white",
                                        "fontWeight": "bold",
                                        "textAlign": "center",
                                    },
                                    style_cell={
                                        "textAlign": "center",
                                        "padding": "10px",
                                        "fontFamily": "Arial",
                                    },
                                    style_data={
                                        "backgroundColor": "white",
                                        "color": "black",
                                    },
                                    page_current=0,
                                    page_size=PAGE_SIZE,
                                    page_action="none",
                                    row_selectable="multi",
                                    merge_duplicate_headers=True,
                                    markdown_options={"html": True},
                                    style_cell_conditional=[
                                        {
                                            "if": {"column_id": "meta_name"},
                                            "textAlign": "center",  # CHANGED FROM "left" TO "center"
                                            "fontWeight": "500",
                                            "whiteSpace": "normal",
                                        },
                                    ],
                                )
                            ], 
                            className="table-responsive enhanced-table-container", 
                            style={
                                "overflow": "visible",  # CHANGED FROM "auto" TO "visible"
                                "minHeight": "300px",  # REDUCED MINIMUM HEIGHT
                                "height": "auto",  # AUTO HEIGHT
                                "maxHeight": "none",  # REMOVED MAX HEIGHT RESTRICTION
                                "padding": "1rem",
                                "backgroundColor": "#ffffff",
                                "borderRadius": "12px",
                                "boxShadow": "inset 0 2px 4px rgba(0, 0, 0, 0.05)",
                            })
                            ], style={"padding": "2rem"})
                        ], style={
                            **CARD_STYLE,
                            "minHeight": "auto",
                            "height": "auto",
                            "width": "100%",  # ADD FULL WIDTH
                            "maxWidth": "100%",  # ADD MAX WIDTH
                            "boxShadow": "0 6px 20px rgba(0, 0, 0, 0.15)",
                            "border": "2px solid #e0e6ed",
                        })
                ], width=12, className="mb-4")
            ])
        ], fluid=True, className="mb-4"),
        
        # Hidden elements
        dcc.Location(id="download_location", refresh=True),
        
    ], style={
        "backgroundColor": "#f8f9fa",
        "minHeight": "100vh",
        "paddingTop": "2rem",
        "paddingBottom": "2rem"
    })


@callback(
    Output("collapse-section", "is_open"),
    Input("toggle-section", "n_clicks"),
    prevent_initial_call=True,
)
def toggle_section(n_clicks: int) -> bool:
    """Toggle the visibility of the database tools section.

    Args:
        n_clicks (int): Number of clicks on the toggle button.

    Returns:
        bool: True if the section should be open, False if it should be closed.

    """
    logger.info(f"Toggle section clicked {n_clicks} times.")
    return n_clicks % 2 == 1  # Toggle between open and closed


def copy_and_zip_files(
    file_info: List[tuple], destination_folder: str, zip_file_name: str
) -> str:
    """Copy a list of files to a destination folder and zips them into an archive.

    Args:
        file_info (List[tuple]): List of tuples containing file paths and UUIDs.
            Each tuple should be in the format (file_path, file_uuid).
        destination_folder (str): Path to the folder where files will be copied.
        zip_file_name (str): Name of the zip file to be created.

    Returns:
        str: Path to the created zip file.

    """
    # Ensure the destination folder exists
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Copy files to the destination folder
    for file_path, file_uuid in file_info:
        if os.path.exists(file_path):
            destination_path = Path(destination_folder) / (
                f"{file_uuid}_" + Path(file_path).name
            )
            logger.info(f"Copying {file_path} to {destination_path}")
            # Copy the file to the destination folder with a new name
            shutil.copy(file_path, destination_path)
        else:
            logger.warning(f"File not found: {file_path}")

    file_list = [
        os.path.join(destination_folder, f"{file_uuid}_" + Path(file_path).name)
        for file_path, file_uuid in file_info
    ]
    logger.info(f"Files copied to {destination_folder}: {file_list}")

    # Create the zip file
    zip_file_path = os.path.join(destination_folder, zip_file_name)
    with ZipFile(zip_file_path, "w") as zip_object:
        for file_path in file_list:
            file_name = Path(file_path).name
            destination_path = os.path.join(destination_folder, file_name)
            if os.path.exists(destination_path):
                zip_object.write(destination_path, arcname=file_name)

    # Verify if the zip file was created
    if os.path.exists(zip_file_path):
        logger.info(f"ZIP file created: {zip_file_path}")
        return zip_file_path
    else:
        logger.error(f"Failed to create ZIP file: {zip_file_path}")
        return None


def clean_tmp_folder(parent_folder: str) -> None:
    """Delete all folders within a specified parent folder.

    Args:
        parent_folder (str): Path to the parent folder.

    """
    try:
        parent_path = Path(parent_folder)
        if not parent_path.exists():
            logger.info(f"Parent folder {parent_folder} does not exist.")
            return

        # Iterate through all items in the parent folder
        for item in parent_path.iterdir():
            if item.is_dir():  # Check if the item is a folder
                logger.info(f"Deleting folder: {item}")
                shutil.rmtree(item)  # Delete the folder and its contents

        logger.info(f"All folders in {parent_folder} have been deleted.")

    except Exception as e:
        logger.error(f"Failed to delete folders in {parent_folder}: {e}")


@callback(
    Output("download_selected", "disabled"),
    Output("download_selected_info", "children"),
    Output("download_link", "children"),
    Input("download_selected", "n_clicks"),
    Input("datatable-paging-and-sorting", "derived_viewport_selected_rows"),
    Input("datatable-paging-and-sorting", "derived_viewport_selected_row_ids"),
    State("datatable-paging-and-sorting", "derived_viewport_data"),
)
def start_download(clicks: int, rows: List, ids: List, data: List) -> tuple:
    """Start the download process for selected rows in the data table.

    Args:
        clicks (int): Number of clicks on the download button.
        rows (List): List of selected row indices.
        ids (List): List of selected row IDs.
        data (List): Data of the data table.

    Returns:
        tuple: A tuple containing:
            - bool: Whether the download button should be disabled.
            - str: Status message for the download.
            - html.A: Download link or message indicating no link available.

    """
    logger.info(f"Starting download with clicks: {clicks}, rows: {rows}, ids: {ids}.")
    triggered_id = (
        callback_context.triggered[0]["prop_id"].split(".")[0]
        if callback_context.triggered
        else None
    )
    logger.info(f"Triggered by: {triggered_id}.")

    no_href_link = html.A(
        "Download link will be available here.", href=None, style={"color": "red"}
    )

    if (rows is None) or (ids is None):
        return False, "No rows selected for download.", no_href_link

    if len(rows) > 0:
        logger.info(f"Disabled is False, Selected rows: {rows}, ids: {ids}")

        if len(rows) > 20:
            logger.info(
                f"Too many rows selected for download: {len(rows)}. Limit is 20."
            )
            return (
                True,
                "Too many rows selected for download. Limit is to 20 rows.",
                no_href_link,
            )

        if triggered_id == "download_selected":
            logger.info(f"Download button was pressed: {clicks}, rows: {rows}")

            uuid = str(uuid4())
            logger.info(f"Started download (id = {uuid}).")

            tmp_folder = app.config["TMP_FOLDER"]
            logger.info(f"Temporary folder: {tmp_folder}.")

            destination_folder = f"{tmp_folder}/download_{uuid}"
            logger.info(f"Temporary download folder: {destination_folder}.")

            selected_data = [data[i] for i in rows]
            file_paths = [data_item["system_result"] for data_item in selected_data]
            file_uuids = [data_item["system_uuid"] for data_item in selected_data]
            file_info = list(zip(file_paths, file_uuids))

            zip_file_name = f"download_{uuid}.zip"

            logger.info(f"file paths: {file_paths}")
            logger.info(f"file uuids: {file_uuids}")
            logger.info(f"destination folder: {destination_folder}")

            copy_and_zip_files(
                file_info=file_info,
                destination_folder=destination_folder,
                zip_file_name=zip_file_name,
            )

            flask_url = f"/assas_app/hdf5_download?uuid={uuid}"
            clickable_link = html.A(
                "Click here to download the zip archive",
                href=flask_url,
                target="_blank",
            )

            return True, "Zipped archive ready for download.", clickable_link

        else:
            logger.info(
                "No download button was pressed, "
                f"just selected rows: {rows}, ids: {ids}"
            )
            return True, "Press button to generate download link.", no_href_link

    else:
        logger.info(f"Disabled is True, Selected rows: {rows}, ids: {ids}")
        return True, "No rows selected for download.", no_href_link


def split_filter_part(filter_part: str) -> List[str]:
    """Split a filter part into name, operator, and value.

    Args:
        filter_part (str): The filter part to split, e.g., "{name} contains 'value'".

    Returns:
        List[str]: A list containing the name, operator, and value.
            If no operator is found, returns [None, None, None].

    """
    logger.info(f"Operators: {operators}")
    logger.info(f"Filter part: {filter_part}")

    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find("{") + 1 : name_part.rfind("}")]

                value_part = value_part.strip()
                v0 = value_part[0]

                if v0 == value_part[-1] and v0 in (""", """, "`"):
                    value = value_part[1:-1].replace("\\" + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3


@callback(
    [Output("datatable-paging-and-sorting", "data"),
     Output("pagination-contents", "children")],
    [Input("pagination", "active_page"),
     Input("datatable-page-size", "value"),
     Input("datatable-paging-and-sorting", "sort_by"),
     Input("datatable-paging-and-sorting", "filter_query"),
     Input("reload_page", "n_clicks")],
    prevent_initial_call=False
)
def update_table_with_pagination(active_page, page_size, sort_by, filter_query, n_clicks):
    """Update table data based on pagination, sorting, filtering, and refresh"""
    
    # Use default values if None
    if active_page is None:
        active_page = 1
    if page_size is None:
        page_size = PAGE_SIZE
    if sort_by is None:
        sort_by = []
    
    # Get fresh data (especially important after refresh)
    dataframe = update_table_data()
    
    # Apply filtering
    if filter_query:
        filtering_expressions = filter_query.split(" && ")
        
        for filter_part in filtering_expressions:
            col_name, operator, filter_value = split_filter_part(filter_part)
            
            if operator in ("eq", "ne", "lt", "le", "gt", "ge"):
                dataframe = dataframe.loc[
                    getattr(dataframe[col_name], operator)(filter_value)
                ]
            elif operator == "contains":
                dataframe = dataframe.loc[dataframe[col_name].str.contains(filter_value)]
            elif operator == "datestartswith":
                dataframe = dataframe.loc[dataframe[col_name].str.startswith(filter_value)]
    
    # Apply sorting
    if len(sort_by):
        dataframe = dataframe.sort_values(
            [col["column_id"] for col in sort_by],
            ascending=[col["direction"] == "asc" for col in sort_by],
            inplace=False,
        )
    
    # Calculate pagination
    start_idx = (active_page - 1) * page_size
    end_idx = start_idx + page_size
    
    # Get paginated data
    paginated_data = dataframe.iloc[start_idx:end_idx].to_dict("records")
    
    # Update pagination info text
    total_records = len(dataframe)  # Use filtered dataframe length
    start_record = start_idx + 1 if total_records > 0 else 0
    end_record = min(end_idx, total_records)
    
    pagination_text = f"Page {active_page} | Showing {start_record}-{end_record} of {total_records}"
    
    return paginated_data, pagination_text

# Keep these callbacks - they don't conflict:

@callback(
    Output("pagination", "max_value"),
    [Input("datatable-page-size", "value"),
     Input("datatable-paging-and-sorting", "filter_query")],
    prevent_initial_call=False
)
def update_pagination_max_value(page_size, filter_query):
    """Update pagination max value when page size or filter changes"""
    if page_size is None:
        page_size = PAGE_SIZE
    
    # Get filtered data count
    dataframe = update_table_data()
    
    # Apply filtering to get accurate count
    if filter_query:
        filtering_expressions = filter_query.split(" && ")
        
        for filter_part in filtering_expressions:
            col_name, operator, filter_value = split_filter_part(filter_part)
            
            if operator in ("eq", "ne", "lt", "le", "gt", "ge"):
                dataframe = dataframe.loc[
                    getattr(dataframe[col_name], operator)(filter_value)
                ]
            elif operator == "contains":
                dataframe = dataframe.loc[dataframe[col_name].str.contains(filter_value)]
            elif operator == "datestartswith":
                dataframe = dataframe.loc[dataframe[col_name].str.startswith(filter_value)]
    
    total_pages = math.ceil(len(dataframe) / page_size) if len(dataframe) > 0 else 1
    return total_pages

@callback(
    Output("pagination", "active_page"),
    [Input("datatable-page-size", "value"),
     Input("datatable-paging-and-sorting", "filter_query")],
    prevent_initial_call=True
)
def reset_pagination_on_changes(page_size, filter_query):
    """Reset to page 1 when page size or filter changes"""
    return 1

# Keep the table height callback as is:
@callback(
    Output("datatable-paging-and-sorting", "style_table"),
    Input("datatable-page-size", "value"),
    prevent_initial_call=False
)
def update_table_height(page_size):
    """Dynamically adjust table height based on page size - NO SCROLLING"""
    if page_size is None:
        page_size = PAGE_SIZE
    
    # Calculate height based on number of rows
    padding_height = 40  # Additional padding and borders
    
    # Calculate total height needed
    calculated_height = (page_size * 60) + 50 + padding_height
    
    # Convert to CSS height
    table_height = f"{calculated_height}px"
    
    return {
        "overflowX": "auto",
        "overflowY": "visible",
        "borderRadius": "12px",
        "border": "2px solid #e0e6ed",
        "fontFamily": "Arial, sans-serif",
        "width": "100%",
        "height": table_height,
        "minHeight": "300px",
        "maxHeight": "none",
        "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.15)",
        "tableLayout": "fixed",
    }

# Add this callback after your existing callbacks:

@callback(
    Output("collapse-usage-guide", "is_open"),
    Input("toggle-usage-guide", "n_clicks"),
    prevent_initial_call=True,
)
def toggle_usage_guide(n_clicks: int) -> bool:
    """Toggle the visibility of the usage guide section.

    Args:
        n_clicks (int): Number of clicks on the toggle button.

    Returns:
        bool: True if the section should be open, False if it should be closed.

    """
    logger.info(f"Usage guide toggle clicked {n_clicks} times.")
    return n_clicks % 2 == 1  # Toggle between open and closed
