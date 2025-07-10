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


def encode_svg_image_hq(svg_name: str) -> str:
    """Encode an SVG image to a high-quality base64 string.

    Args:
        svg_name (str): The name of the SVG file to encode.

    Returns:
        str: A high-quality base64 encoded string of the SVG image.

    """
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets/", svg_name)

    try:
        with open(path, "rb") as file:
            svg_content = file.read()

        # Optimize SVG content for better quality
        svg_string = svg_content.decode("utf-8")

        # Add high-quality rendering attributes if not present
        if "shape-rendering" not in svg_string:
            svg_string = svg_string.replace(
                "<svg", '<svg shape-rendering="geometricPrecision"'
            )
        if "text-rendering" not in svg_string:
            svg_string = svg_string.replace(
                "<svg", '<svg text-rendering="optimizeLegibility"'
            )
        if "image-rendering" not in svg_string:
            svg_string = svg_string.replace(
                "<svg", '<svg image-rendering="optimizeQuality"'
            )

        # Re-encode with optimizations
        encoded = base64.b64encode(svg_string.encode("utf-8"))
        svg = "data:image/svg+xml;base64,{}".format(encoded.decode())

        return svg

    except Exception:
        # Fallback to original method
        return encode_svg_image(svg_name)


def content_style() -> Dict:
    """Define responsive styles for the content area of the Dash application.

    Returns:
        dict: A dictionary containing CSS styles for the content area with
        responsive design.

    """
    return {
        "margin-top": "2rem",
        "margin-bottom": "2rem",
        "margin-left": "2rem",  # Reduced from 3rem
        "margin-right": "2rem",  # Reduced from 3rem
        "padding": "2rem 0.5rem",  # Minimal side padding
        "border": "2px solid #dee2e6",
        "border-radius": "8px",
        "box-shadow": "0 2px 4px rgba(0, 0, 0, 0.1)",
        "background-color": "#ffffff",
        "fontFamily": "Arial, sans-serif",  # Added Arial font
        # Extra Large desktop
        "@media (min-width: 1200px)": {
            "margin-left": "3rem",
            "margin-right": "3rem",
            "padding": "2rem 1rem",  # Slightly more padding on large screens
        },
        # Large desktop
        "@media (min-width: 992px) and (max-width: 1199px)": {
            "margin-left": "2rem",
            "margin-right": "2rem",
            "padding": "2rem 0.75rem",
        },
        # Tablet styles
        "@media (max-width: 991px) and (min-width: 769px)": {
            "margin-left": "1rem",
            "margin-right": "1rem",
            "padding": "1.5rem 0.5rem",  # Minimal side padding
            "border": "1px solid #dee2e6",
        },
        # Mobile landscape styles
        "@media (max-width: 768px) and (min-width: 577px)": {
            "margin-left": "0.5rem",
            "margin-right": "0.5rem",
            "padding": "1rem 0.25rem",  # Very minimal side padding
            "border": "1px solid #e9ecef",
            "border-radius": "6px",
        },
        # Mobile portrait styles
        "@media (max-width: 576px)": {
            "margin-left": "0.25rem",  # Minimal margins
            "margin-right": "0.25rem",
            "padding": "1rem 0.125rem",  # Almost no side padding
            "border": "1px solid #f8f9fa",
            "border-radius": "4px",
        },
        # Extra small screens
        "@media (max-width: 400px)": {
            "margin-left": "0.125rem",
            "margin-right": "0.125rem",
            "padding": "0.75rem 0.0625rem",  # Absolute minimal padding
            "border": "none",
            "box-shadow": "0 1px 3px rgba(0, 0, 0, 0.1)",
        },
    }


def minimal_padding_style() -> Dict:
    """Define styles with minimal side padding for maximum content width.

    Returns:
        dict: A dictionary containing CSS styles with minimal horizontal spacing.

    """
    return {
        "margin-top": "1.5rem",
        "margin-bottom": "1.5rem",
        "margin-left": "1rem",  # Minimal left margin
        "margin-right": "1rem",  # Minimal right margin
        "padding": "1.5rem 0.5rem",  # Minimal horizontal padding
        "border": "1px solid #e9ecef",
        "border-radius": "6px",
        "box-shadow": "0 1px 3px rgba(0, 0, 0, 0.08)",
        "background-color": "#ffffff",
        "fontFamily": "Arial, sans-serif",  # Added Arial font
        # Desktop
        "@media (min-width: 992px)": {
            "margin-left": "1.5rem",
            "margin-right": "1.5rem",
            "padding": "1.5rem 0.75rem",
        },
        # Tablet
        "@media (max-width: 991px) and (min-width: 577px)": {
            "margin-left": "0.75rem",
            "margin-right": "0.75rem",
            "padding": "1rem 0.5rem",
        },
        # Mobile
        "@media (max-width: 576px)": {
            "margin-left": "0.25rem",
            "margin-right": "0.25rem",
            "padding": "0.75rem 0.25rem",
            "border": "none",
        },
    }


def full_width_style() -> Dict:
    """Define styles for full-width content with minimal side spacing.

    Returns:
        dict: A dictionary containing CSS styles for maximum width utilization.

    """
    return {
        "margin-top": "1rem",
        "margin-bottom": "1rem",
        "margin-left": "0.5rem",
        "margin-right": "0.5rem",
        "padding": "1rem 0.25rem",  # Very minimal horizontal padding
        "border": "1px solid #f8f9fa",
        "border-radius": "4px",
        "background-color": "#ffffff",
        "fontFamily": "Arial, sans-serif",  # Added Arial font
        # Desktop - still keep some margin for readability
        "@media (min-width: 992px)": {
            "margin-left": "1rem",
            "margin-right": "1rem",
            "padding": "1.5rem 0.5rem",
        },
        # Mobile - maximum width usage
        "@media (max-width: 576px)": {
            "margin-left": "0.125rem",
            "margin-right": "0.125rem",
            "padding": "0.75rem 0.125rem",
            "border": "none",
            "border-radius": "2px",
        },
    }


def conditional_table_style() -> List:
    """Define conditional styles for the Dash DataTable with improved styling.

    Returns:
        list: A list of dictionaries defining conditional styles for table columns.

    """
    return [
        {
            "if": {"column_id": "system_index"},
            "backgroundColor": "#f8f9fa",  # Light gray instead of grey
            "textAlign": "center",
            "color": "#495057",  # Better contrast
            "fontWeight": "500",
            "fontFamily": "Arial, sans-serif",  # Added Arial font
        },
        {
            "if": {"column_id": "system_download"},
            "backgroundColor": "#f8f9fa",
            "textAlign": "center",
            "textDecoration": "underline",
            "cursor": "pointer",
            "color": "#007bff",  # Better blue color
            "fontWeight": "500",
            "fontFamily": "Arial, sans-serif",  # Added Arial font
        },
        {
            "if": {"column_id": "meta_name"},
            "backgroundColor": "#f8f9fa",
            "textAlign": "center",
            "textDecoration": "underline",
            "cursor": "pointer",
            "color": "#007bff",
            "fontWeight": "500",
            "fontFamily": "Arial, sans-serif",  # Added Arial font
        },
        {
            "if": {
                "column_id": "system_status",
                "filter_query": f"{{system_status}} = '{uploaded_value}'",
            },
            "backgroundColor": "#e3f2fd",  # Lighter blue
            "color": "#1976d2",
            "fontFamily": "Arial, sans-serif",  # Added Arial font
        },
        {
            "if": {
                "column_id": "system_status",
                "filter_query": f"{{system_status}} = '{valid_value}'",
            },
            "backgroundColor": "#e8f5e8",  # Lighter green
            "color": "#2e7d32",
            "fontFamily": "Arial, sans-serif",  # Added Arial font
        },
        {
            "if": {
                "column_id": "system_status",
                "filter_query": f"{{system_status}} = '{invalid_value}'",
            },
            "backgroundColor": "#ffebee",  # Lighter red
            "color": "#c62828",
            "fontFamily": "Arial, sans-serif",  # Added Arial font
        },
        {
            "if": {
                "column_id": "system_status",
                "filter_query": f"{{system_status}} = '{convert_value}'",
            },
            "backgroundColor": "#fff8e1",  # Lighter yellow
            "color": "#f57f17",
            "fontFamily": "Arial, sans-serif",  # Added Arial font
        },
    ]


def ultra_minimal_style() -> Dict:
    """Define ultra-minimal styles for maximum content width.

    Returns:
        dict: A dictionary containing CSS styles with virtually no side spacing.

    """
    return {
        "margin-top": "1rem",
        "margin-bottom": "1rem",
        "margin-left": "0.25rem",
        "margin-right": "0.25rem",
        "padding": "1rem 0.125rem",  # Almost no horizontal padding
        "border": "1px solid #f1f3f4",
        "border-radius": "4px",
        "background-color": "#ffffff",
        "fontFamily": "Arial, sans-serif",  # Added Arial font
        # Desktop - still minimal but readable
        "@media (min-width: 992px)": {
            "margin-left": "1rem",
            "margin-right": "1rem",
            "padding": "1.5rem 0.5rem",
        },
        # Tablet
        "@media (max-width: 991px) and (min-width: 577px)": {
            "margin-left": "0.5rem",
            "margin-right": "0.5rem",
            "padding": "1rem 0.25rem",
        },
        # Mobile - maximum width usage
        "@media (max-width: 576px)": {
            "margin-left": "0.125rem",
            "margin-right": "0.125rem",
            "padding": "0.75rem 0.0625rem",
            "border": "none",
        },
    }


def table_container_style() -> Dict:
    """Define styles specifically for table containers with minimal padding.

    Returns:
        dict: A dictionary containing CSS styles optimized for table display.

    """
    return {
        "margin": "1rem 0.25rem",  # Minimal side margins
        "padding": "0.5rem 0.125rem",  # Very minimal padding
        "border": "1px solid #e9ecef",
        "border-radius": "6px",
        "background-color": "#ffffff",
        "overflow-x": "auto",  # Horizontal scroll for tables
        "fontFamily": "Arial, sans-serif",  # Added Arial font
        # Desktop
        "@media (min-width: 992px)": {
            "margin": "1.5rem 1rem",
            "padding": "1rem 0.5rem",
        },
        # Tablet
        "@media (max-width: 991px) and (min-width: 577px)": {
            "margin": "1rem 0.5rem",
            "padding": "0.75rem 0.25rem",
        },
        # Mobile - edge-to-edge table
        "@media (max-width: 576px)": {
            "margin": "0.5rem 0.125rem",
            "padding": "0.5rem 0.0625rem",
            "border": "none",
            "border-radius": "0",
        },
    }


def responsive_table_style() -> Dict:
    """Define responsive table styles with ultra-minimal padding.

    Returns:
        dict: A dictionary containing table styles with reduced padding for maximum
        content width.

    """
    return {
        "style_table": {
            "overflowX": "auto",
            "minWidth": "100%",
            "margin": "0",
            "width": "100%",
            "fontFamily": "Arial, sans-serif",  # Added Arial font
        },
        "style_cell": {
            "textAlign": "left",
            "padding": "6px 4px",  # Ultra-minimal padding
            "fontFamily": "Arial, sans-serif",  # Changed from Segoe UI
            "fontSize": "13px",  # Slightly smaller font
            "border": "1px solid #e9ecef",
            "whiteSpace": "normal",
            "height": "auto",
            "maxWidth": "150px",  # Reduced max width
            "overflow": "hidden",
            "textOverflow": "ellipsis",
        },
        "style_header": {
            "backgroundColor": "#f8f9fa",
            "fontWeight": "600",
            "textAlign": "center",
            "padding": "8px 4px",  # Minimal header padding
            "border": "1px solid #dee2e6",
            "color": "#495057",
            "fontSize": "12px",  # Smaller header font
            "fontFamily": "Arial, sans-serif",  # Added Arial font
        },
        "style_data": {
            "backgroundColor": "#ffffff",
            "color": "#212529",
            "fontFamily": "Arial, sans-serif",  # Added Arial font
        },
        # Mobile-specific cell styles
        "style_cell_conditional": [
            {
                "if": {"column_id": ["meta_name", "system_download"]},
                "minWidth": "120px",  # Reduced from 150px
                "width": "120px",
                "maxWidth": "120px",
                "padding": "4px 2px",  # Even less padding for action columns
                "fontFamily": "Arial, sans-serif",  # Added Arial font
            },
            {
                "if": {"column_id": "system_status"},
                "minWidth": "80px",  # Reduced from 100px
                "width": "80px",
                "maxWidth": "80px",
                "textAlign": "center",
                "padding": "4px 2px",
                "fontFamily": "Arial, sans-serif",  # Added Arial font
            },
            # Mobile-specific padding reduction
            {
                "if": {"state": "active"},
                "backgroundColor": "#e3f2fd",
                "border": "1px solid #2196f3",
                "fontFamily": "Arial, sans-serif",  # Added Arial font
            },
        ],
    }


def mobile_optimized_table_style() -> Dict:
    """Define table styles specifically optimized for mobile devices.

    Returns:
        dict: A dictionary containing highly compact table styles for mobile.

    """
    return {
        "style_table": {
            "overflowX": "auto",
            "minWidth": "100%",
            "margin": "0",
            "fontSize": "11px",  # Smaller font for mobile
            "fontFamily": "Arial, sans-serif",  # Added Arial font
        },
        "style_cell": {
            "textAlign": "left",
            "padding": "3px 2px",  # Extremely minimal padding
            "fontFamily": "Arial, sans-serif",  # Changed from system-ui
            "fontSize": "11px",
            "border": "1px solid #f1f3f4",
            "whiteSpace": "nowrap",
            "overflow": "hidden",
            "textOverflow": "ellipsis",
            "maxWidth": "100px",
        },
        "style_header": {
            "backgroundColor": "#f8f9fa",
            "fontWeight": "600",
            "textAlign": "center",
            "padding": "4px 2px",
            "fontSize": "10px",
            "border": "1px solid #e9ecef",
            "fontFamily": "Arial, sans-serif",  # Added Arial font
        },
        "style_data": {
            "backgroundColor": "#ffffff",
            "fontSize": "11px",
            "fontFamily": "Arial, sans-serif",  # Added Arial font
        },
    }
