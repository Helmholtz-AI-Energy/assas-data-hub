"""Module with utility functions and constants for the Dash application.

It includes functions for encoding SVG images, defining content styles, and setting
conditional table styles.
"""

import os
import base64

from typing import Dict, List

from assasdb import AssasDocumentFileStatus

uploaded_value = AssasDocumentFileStatus.UPLOADED.value
valid_value = AssasDocumentFileStatus.VALID.value
invalid_value = AssasDocumentFileStatus.INVALID.value
convert_value = AssasDocumentFileStatus.CONVERTING.value


def encode_svg_image(svg_name: str) -> str:
    """Encode an SVG image to a base64 string.

    Args:
        svg_name (str): The name of the SVG file to encode.

    Returns:
        str: A base64 encoded string of the SVG image.

    """
    path = (
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets/") + svg_name
    )
    encoded = base64.b64encode(open(path, "rb").read())
    svg = "data:image/svg+xml;base64,{}".format(encoded.decode())

    return svg


def content_style() -> Dict:
    """Define the style for the content area of the Dash application.

    Returns:
        dict: A dictionary containing CSS styles for the content area.

    """
    return {
        "margin-top": "2rem",
        "margin-bottom": "2rem",
        "margin-left": "5rem",
        "margin-right": "5rem",
        "padding": "2rem 1rem",
        "border": "4px grey solid",
    }


def conditional_table_style() -> List:
    """Define conditional styles for the Dash DataTable.

    Returns:
        list: A list of dictionaries defining conditional styles for table columns.

    """
    return [
        {
            "if": {"column_id": "system_index"},
            "backgroundColor": "grey",
            "textAlign": " center",
            "color": "black",
        },
        {
            "if": {"column_id": "system_download"},
            "backgroundColor": "grey",
            "textAlign": "center",
            "textDecoration": "underline",
            "cursor": "pointer",
            "color": "blue",
        },
        {
            "if": {"column_id": "meta_name"},
            "backgroundColor": "grey",
            "textAlign": "center",
            "textDecoration": "underline",
            "cursor": "pointer",
            "color": "blue",
        },
        {
            "if": {
                "column_id": "system_status",
                "filter_query": f"{{system_status}} = '{uploaded_value}'",
            },
            "backgroundColor": "#D9EDF7",  # Light blue for processing
            "color": "#31708F",  # Dark blue text
        },
        {
            "if": {
                "column_id": "system_status",
                "filter_query": f"{{system_status}} = '{valid_value}'",
            },
            "backgroundColor": "#DFF0D8",  # Light green for active
            "color": "#3C763D",  # Dark green text
        },
        {
            "if": {
                "column_id": "system_status",
                "filter_query": f"{{system_status}} = '{invalid_value}'",
            },
            "backgroundColor": "#F2DEDE",  # Light red for inactive
            "color": "#A94442",  # Dark red text
        },
        {
            "if": {
                "column_id": "system_status",
                "filter_query": f"{{system_status}} = '{convert_value}'",
            },
            "backgroundColor": "#FCF8E3",  # Light yellow for pending
            "color": "#8A6D3B",  # Dark yellow text
        },
    ]
