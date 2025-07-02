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

from dash import dash_table, html, dcc, Input, Output, callback, State, callback_context
from flask import current_app as app
from zipfile import ZipFile
from uuid import uuid4
from pathlib import Path
from typing import List

from assasdb import AssasDatabaseManager, AssasDatabaseHandler
from ..components import content_style, conditional_table_style

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
        database_handler=AssasDatabaseHandler(
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


def layout():
    """Layout for the ASSAS Database page.

    Returns:
        html.Div: The layout of the ASSAS Database page.

    """
    return html.Div(
        [
            html.H2(
                "ASSAS Database - Training Dataset Index",
                style={**COMMON_STYLE, "fontSize": "48px", "fontWeight": "bold"},
            ),
            dbc.Alert(
                "Welcome to the ASSAS Database page! Use this interface to search, view"
                ",and download datasets from the ASSAS training dataset index. "
                "You can navigate through the available datasets using the pagination "
                "controls below, refresh the dataset list, and access detailed storage "
                "parameters. Click on the download link for valid datasets to retrieve "
                "the corresponding files.",
                color="primary",
                style={**COMMON_STYLE},
            ),
            html.Hr(),
            html.Div(
                [
                    dbc.Row(
                        dbc.Col(
                            dbc.Pagination(
                                id="pagination",
                                first_last=True,
                                previous_next=True,
                                max_value=PAGE_COUNT,
                                fully_expanded=False,
                                size="lg",
                            ),
                            width="auto",
                        ),
                        justify="center",
                    )
                ],
                style={**RESPONSIVE_STYLE},
            ),
            html.Hr(),
            html.Div(
                [
                    dbc.Button(
                        "Database Tools",
                        id="toggle-section",
                        className="me-2",
                        n_clicks=0,
                        size="lg",
                        style={
                            **COMMON_STYLE,
                            "width": "100%",
                            "padding": "5px",
                            "fontSize": "14px",
                            "fontWeight": "bold",
                        },
                        color="primary",
                        title="Click to toggle the section below.",
                    ),
                ],
                style={
                    **COMMON_STYLE,
                    "textAlign": "center",
                    "margin": "1% auto",
                    "padding": "10px",
                    "width": "100%",
                },
            ),
            dbc.Collapse(
                html.Div(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.H4(
                                        "Select datasets for download:",
                                        style={
                                            **COMMON_STYLE,
                                            "textAlign": "center",
                                            "fontWeight": "bold",
                                        },
                                    ),
                                    width=4,
                                    style={
                                        "border": "1px solid lightgrey",
                                        "borderRadius": "2%",
                                        "padding": "2%",
                                    },
                                ),
                                dbc.Col(
                                    html.H4(
                                        "Refresh datasets on page:",
                                        style={
                                            **COMMON_STYLE,
                                            "textAlign": "center",
                                            "fontWeight": "bold",
                                        },
                                    ),
                                    width=4,
                                    style={
                                        "border": "1px solid lightgrey",
                                        "borderRadius": "2%",
                                        "padding": "2%",
                                    },
                                ),
                                dbc.Col(
                                    html.H4(
                                        "LSDF database parameters:",
                                        style={
                                            **COMMON_STYLE,
                                            "textAlign": "center",
                                            "fontWeight": "bold",
                                        },
                                    ),
                                    width=4,
                                    style={
                                        "border": "1px solid lightgrey",
                                        "borderRadius": "2%",
                                        "padding": "2%",
                                    },
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    children=[
                                        dcc.Loading(
                                            children=[
                                                dbc.Button(
                                                    "Get Download Link",
                                                    id="download_selected",
                                                    className="me-2",
                                                    n_clicks=0,
                                                    disabled=True,
                                                    size="lg",
                                                    style={
                                                        **COMMON_STYLE,
                                                        "width": "100%",
                                                        "padding": "5px",
                                                        "fontSize": "14px",
                                                    },
                                                    title="Select datasets in "
                                                    " the table to enable"
                                                    " this button.",
                                                ),
                                            ],
                                            type="circle",
                                            fullscreen=False,
                                        ),
                                        html.Div(
                                            "Select datasets to download.",
                                            id="download_selected_info",
                                            style={
                                                **COMMON_STYLE,
                                                "margin-top": "10px",
                                                "fontSize": "14px",
                                                "textAlign": "center",
                                            },
                                        ),
                                        dcc.Loading(
                                            children=[
                                                html.P(
                                                    "Note: You can select multiple "
                                                    "datasets, but the download is "
                                                    "limited to 20 datasets at a time.",
                                                    style={
                                                        **COMMON_STYLE,
                                                        "fontSize": "12px",
                                                        "color": "grey",
                                                        "textAlign": "center",
                                                    },
                                                )
                                            ],
                                            type="circle",
                                            fullscreen=False,
                                        ),
                                    ],
                                    width=4,
                                    style={
                                        "border": "1px solid lightgrey",
                                        "borderRadius": "2%",
                                        "padding": "2%",
                                        "display": "block",
                                        "textAlign": "center",
                                    },
                                ),
                                dbc.Col(
                                    children=[
                                        dbc.Button(
                                            "Refresh",
                                            id="reload_page",
                                            className="me-2",
                                            n_clicks=0,
                                            disabled=False,
                                            size="lg",
                                            style={
                                                **COMMON_STYLE,
                                                "width": "80%",
                                                "padding": "5px",
                                                "fontSize": "14px",
                                            },
                                            title="Click to refresh the dataset list.",
                                        ),
                                        html.Div(
                                            f"Number of datasets loaded: "
                                            f"{len(table_data)}",
                                            id="dataset_count",
                                            style={
                                                **COMMON_STYLE,
                                                "margin-top": "10px",
                                                "fontSize": "14px",
                                                "textAlign": "center",
                                            },
                                        ),
                                        dcc.Loading(
                                            children=[
                                                html.P(
                                                    f"Database updated at: {now}",
                                                    id="database_update_time",
                                                    style={
                                                        **COMMON_STYLE,
                                                        "fontSize": "12px",
                                                        "color": "grey",
                                                        "textAlign": "center",
                                                    },
                                                )
                                            ],
                                            type="circle",
                                            fullscreen=False,
                                        ),
                                    ],
                                    width=4,
                                    style={
                                        "border": "1px solid lightgrey",
                                        "borderRadius": "2%",
                                        "padding": "2%",
                                        "display": "block",
                                        "textAlign": "center",
                                    },
                                ),
                                dbc.Col(
                                    dbc.Table(
                                        [
                                            html.Thead(
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            html.Th("Parameter"),
                                                            width=6,
                                                            style={
                                                                "textAlign": "center"
                                                            },
                                                        ),
                                                        dbc.Col(
                                                            html.Th("Value"),
                                                            width=6,
                                                            style={
                                                                "textAlign": "center"
                                                            },
                                                        ),
                                                    ]
                                                )
                                            ),
                                            html.Tbody(
                                                [
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                html.Td("Used Storage"),
                                                                width=6,
                                                                style={
                                                                    "align": "center"
                                                                },
                                                            ),
                                                            dbc.Col(
                                                                html.Td(
                                                                    f"{database_size}"
                                                                ),
                                                                width=6,
                                                                style={
                                                                    "align": "center"
                                                                },
                                                            ),
                                                        ]
                                                    ),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                html.Td(
                                                                    "Current Storage "
                                                                    "Limit"
                                                                ),
                                                                width=6,
                                                                style={
                                                                    "align": "center"
                                                                },
                                                            ),
                                                            dbc.Col(
                                                                html.Td("100 TB"),
                                                                width=6,
                                                                style={
                                                                    "align": "center"
                                                                },
                                                            ),
                                                        ]
                                                    ),
                                                ]
                                            ),
                                        ],
                                        bordered=True,
                                        striped=True,
                                        hover=True,
                                        responsive=True,
                                        style={**COMMON_STYLE, "margin-left": "10%"},
                                    ),
                                    width=4,
                                    style={
                                        "border": "1px solid lightgrey",
                                        "borderRadius": "2%",
                                        "padding": "2%",
                                    },
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Div(
                                        "Link",
                                        id="download_link",
                                        style={
                                            **COMMON_STYLE,
                                            "textAlign": "center",
                                            "fontWeight": "bold",
                                        },
                                    ),
                                    width=4,
                                    style={
                                        "border": "1px solid lightgrey",
                                        "borderRadius": "2%",
                                        "padding": "2%",
                                    },
                                ),
                            ]
                        ),
                    ],
                    style=RESPONSIVE_STYLE,
                ),
                id="collapse-section",
                is_open=False,  # Initially collapsed
            ),
            dcc.Location(id="download_location", refresh=True),
            html.Hr(),
            dash_table.DataTable(
                id="datatable-paging-and-sorting",
                columns=[
                    {"name": "_id", "id": "_id", "hideable": True},
                    {"name": "Uuid", "id": "system_uuid", "hideable": True},
                    {
                        "name": "Upload Uuid",
                        "id": "system_upload_uuid",
                        "hideable": True,
                    },
                    {"name": "Path", "id": "system_path", "hideable": True},
                    {"name": "Result", "id": "system_result", "hideable": True},
                    {
                        "name": "Samples",
                        "id": "system_number_of_samples",
                        "hideable": True,
                    },
                    {
                        "name": "Completed Samples",
                        "id": "system_number_of_samples_completed",
                        "hideable": True,
                    },
                    {"name": "Index", "id": "system_index", "selectable": True},
                    {"name": "Size binary", "id": "system_size", "selectable": True},
                    {"name": "Size hdf5", "id": "system_size_hdf5", "selectable": True},
                    {"name": "Date", "id": "system_date", "selectable": True},
                    {"name": "User", "id": "system_user", "selectable": True},
                    {
                        "name": "Download",
                        "id": "system_download",
                        "selectable": True,
                        "presentation": "markdown",
                    },
                    {"name": "Status", "id": "system_status", "selectable": True},
                    {
                        "name": "Name",
                        "id": "meta_name",
                        "selectable": True,
                        "presentation": "markdown",
                    },
                ],
                markdown_options={"html": True},
                hidden_columns=[
                    "",
                    "_id",
                    "system_uuid",
                    "system_upload_uuid",
                    "system_path",
                    "system_result",
                    "system_number_of_samples",
                    "system_number_of_samples_completed",
                ],
                data=table_data.to_dict("records"),
                style_table={
                    "overflowX": "auto",  # Horizontal scrolling for wide tables
                    "width": "100%",  # Full width for responsiveness
                    "margin": "0 auto",  # Center the table
                },
                style_cell={
                    "fontSize": 17,
                    "padding": "2px",
                    "textAlign": "center",
                    "font-family": "sans-serif",
                },
                merge_duplicate_headers=True,
                style_header={
                    "backgroundColor": "black",
                    "color": "white",
                    "fontWeight": "bold",
                },
                style_data={"backgroundColor": "black", "color": "white"},
                row_selectable="multi",
                page_current=0,
                page_size=PAGE_SIZE,
                page_action="none",
                filter_action="custom",
                filter_query="",
                sort_action="custom",
                sort_mode="multi",
                sort_by=[],
                is_focused=True,
                style_data_conditional=conditional_table_style(),
                css=[dict(selector="p", rule="margin: 0; text-align: center")],
            ),
            html.Hr(),
            html.Br(),
            dcc.Checklist(
                id="datatable-use-page-size",
                options=[{"label": " Change entries per page", "value": "True"}],
                value=["False"],
            ),
            "Entries per page: ",
            dcc.Input(
                id="datatable-page-size",
                type="number",
                min=1,
                max=PAGE_MAX_SIZE,
                value=PAGE_SIZE,
                placeholder=PAGE_SIZE,
                style={"color": "grey"},
                disabled=False,
            ),
            html.Div("Select a page", id="pagination-contents"),
        ],
        style=content_style(),
    )


@callback(
    Output("collapse-section", "is_open"),
    Input("toggle-section", "n_clicks"),
    prevent_initial_call=True,
)
def toggle_section(n_clicks):
    """Toggle the visibility of the database tools section.

    Args:
        n_clicks (int): Number of clicks on the toggle button.

    Returns:
        bool: True if the section should be open, False if it should be closed.

    """
    logger.info(f"Toggle section clicked {n_clicks} times.")
    return n_clicks % 2 == 1  # Toggle between open and closed


def copy_and_zip_files(
    file_info: List[tuple], destination_folder, zip_file_name
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
def start_download(clicks, rows, ids, data):
    """Start the download process for selected rows in the data table.

    Args:
        clicks (int): Number of clicks on the download button.
        rows (list): List of selected row indices.
        ids (list): List of selected row IDs.
        data (list): Data of the data table.

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


def split_filter_part(filter_part) -> List[str]:
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
    Output("datatable-paging-and-sorting", "data"),
    Input("datatable-paging-and-sorting", "page_current"),
    Input("datatable-paging-and-sorting", "page_size"),
    Input("datatable-paging-and-sorting", "sort_by"),
    Input("datatable-paging-and-sorting", "filter_query"),
    Input("reload_page", "n_clicks"),
)
def update_table(page_current, page_size, sort_by, filter, n_clicks):
    """Update the data in the data table based on pagination, sorting, and filtering.

    Args:
        page_current (int): The current page number.
        page_size (int): The number of rows per page.
        sort_by (list): List of dictionaries containing sorting information.
        filter (str): The filter query string.
        n_clicks (int): Number of clicks on the reload button.

    Returns:
        list: A list of dictionaries representing the filtered and sorted data for
            the current page.

    """
    dataframe = update_table_data()

    filtering_expressions = filter.split(" && ")

    logger.info(f"filtering_expressions: {filtering_expressions}")

    logger.info(f"page_current: {page_current}, page_size: {page_size}")
    logger.info(f"sort_by: {sort_by}, filter: {filter}, n_clicks: {n_clicks}")

    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)

        logger.info(f"filter_part: {filter_part}, col_name: {col_name}")
        logger.info(f"operator: {operator}, filter_value: {filter_value}")

        if operator in ("eq", "ne", "lt", "le", "gt", "ge"):
            # these operators match pandas series operator method names
            dataframe = dataframe.loc[
                getattr(dataframe[col_name], operator)(filter_value)
            ]
        elif operator == "contains":
            dataframe = dataframe.loc[dataframe[col_name].str.contains(filter_value)]
        elif operator == "datestartswith":
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dataframe = dataframe.loc[dataframe[col_name].str.startswith(filter_value)]

    if len(sort_by):
        dataframe = dataframe.sort_values(
            [col["column_id"] for col in sort_by],
            ascending=[col["direction"] == "asc" for col in sort_by],
            inplace=False,
        )

    page = page_current
    size = page_size

    return dataframe.iloc[page * size : (page + 1) * size].to_dict("records")


@callback(
    Output("datatable-paging-and-sorting", "page_size"),
    Input("datatable-use-page-size", "value"),
    Input("datatable-page-size", "value"),
)
def update_page_size(use_page_size, page_size_value):
    """Update the page size of the data table based on user input.

    Args:
        use_page_size (list): List of selected options from the page size checklist.
        page_size_value (int): The value entered in the page size input field.

    Returns:
        int: The updated page size value.

    """
    logger.info(
        f"update page size, use_page_size: {use_page_size}, "
        f"page_size_value: {page_size_value}"
    )

    if len(use_page_size) == 0 or page_size_value is None:
        return PAGE_SIZE

    return page_size_value


@callback(
    Output("pagination-contents", "children"),
    Input("pagination", "active_page"),
    Input("pagination", "max_value"),
)
def change_page(page, value):
    """Update the pagination display based on the current page and maximum value.

    Args:
        page (int): The current active page number.
        value (int): The maximum value for pagination.

    Returns:
        str: A string indicating the current page and maximum value.

    """
    logger.debug(f"page: {page}, value: {value}")

    if page:
        return f"Page selected: {page}/{value}"

    return f"Page selected: 1/{value}"


@callback(
    Output("datatable-paging-and-sorting", "page_current"),
    Input("pagination", "active_page"),
)
def change_page_table(page):
    """Update the current page of the data table based on the pagination input.

    Args:
        page (int): The current active page number from the pagination component.

    Returns:
        int: The current page number for the data table, adjusted to be zero-indexed.

    """
    logger.debug(f"Page: {page}.")

    if page:
        return page - 1

    return 0


@callback(
    Output("pagination", "max_value"),
    Output("datatable-page-size", "style"),
    Input("datatable-use-page-size", "value"),
    Input("datatable-page-size", "value"),
)
def update_page_count(use_page_size, page_size_value):
    """Update the maximum value for pagination.

    Args:
        use_page_size (list): List of selected options from the page size checklist.
        page_size_value (int): The value entered in the page size input field.

    Returns:
        tuple: A tuple containing:
            - int: The updated maximum value for pagination.
            - dict: A dictionary with the style for the page size input field.

    """
    logger.debug(f"Update page count, use page size: {use_page_size}.")
    logger.debug(f"page_size_value: {page_size_value}.")

    if len(use_page_size) > 1 and page_size_value is not None:
        return int(len(table_data) / page_size_value) + 1, {"color": "black"}

    if page_size_value is None:
        return int(len(table_data) / PAGE_SIZE) + 1, {"color": "grey"}

    return int(len(table_data) / PAGE_SIZE) + 1, {"color": "grey"}
