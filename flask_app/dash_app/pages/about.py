"""About page for the ASSAS Data Hub project."""

import dash

from dash import html
from ..components import content_style, encode_svg_image_hq

dash.register_page(__name__, path="/about")


def responsive_image_style() -> dict:
    """Define responsive styles for images with enhanced quality.

    Returns:
        dict: CSS styles for high-quality responsive images.

    """
    return {
        "maxWidth": "100%",
        "height": "auto",
        "width": "auto",
        "display": "block",
        "margin": "0 auto",
        "border": "1px solid #dee2e6",
        "borderRadius": "8px",
        "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.1)",
        # Image quality enhancements
        "imageRendering": "high-quality",
        "imageResolution": "from-image",
        "objectFit": "contain",
        "objectPosition": "center",
        "filter": "contrast(1.05) brightness(1.02)",
        # Anti-aliasing and smoothing
        "backfaceVisibility": "hidden",
        "perspective": "1000px",
        "transform": "translateZ(0)",
        "willChange": "transform",
        # Desktop styles
        "@media (min-width: 992px)": {
            "maxWidth": "1200px",
            "width": "100%",
            "imageRendering": "auto",
        },
        # Tablet styles
        "@media (max-width: 991px) and (min-width: 769px)": {
            "maxWidth": "900px",
            "width": "100%",
        },
        # Mobile landscape styles
        "@media (max-width: 768px) and (min-width: 577px)": {
            "maxWidth": "100%",
            "width": "98%",
            "imageRendering": "crisp-edges",
        },
        # Mobile portrait styles
        "@media (max-width: 576px)": {
            "maxWidth": "100%",
            "width": "100%",
            "margin": "0",
            "imageRendering": "pixelated",
            "filter": "contrast(1.1) brightness(1.05)",
        },
    }


def info_box_style() -> dict:
    """Define styles for information boxes.

    Returns:
        dict: CSS styles for info boxes.

    """
    return {
        "backgroundColor": "#f8f9fa",
        "border": "1px solid #e9ecef",
        "borderRadius": "8px",
        "padding": "1.5rem",
        "margin": "1rem 0",
        "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.05)",
        "fontFamily": "Arial, sans-serif",
    }


def code_block_style() -> dict:
    """Define styles for code blocks.

    Returns:
        dict: CSS styles for code blocks.

    """
    return {
        "backgroundColor": "#f8f9fa",
        "border": "1px solid #e9ecef",
        "borderRadius": "6px",
        "padding": "1rem",
        "margin": "0.5rem 0",
        "fontFamily": "Monaco, Consolas, 'Courier New', monospace",
        "fontSize": "14px",
        "color": "#495057",
        "overflowX": "auto",
    }


def layout() -> html.Div:
    """Layout for the About page."""
    return_div = html.Div(
        [
            html.H1(
                "About the ASSAS Data Hub", style={"fontFamily": "Arial, sans-serif"}
            ),
            html.Hr(),
            # Project Overview Section
            html.Div(
                [
                    html.H4(
                        "Project Overview",
                        style={"fontFamily": "Arial, sans-serif", "color": "#2c3e50"},
                    ),
                    html.P(
                        [
                            "The ASSAS Data Hub is a comprehensive data management "
                            "platform for ASTEC (Accident Source Term Evaluation Code) "
                            "simulation datasets. "
                            "This Flask-based web application provides researchers "
                            "and engineers with easy access to nuclear safety "
                            "simulation data stored on the "
                            "Large Scale Data Facility (LSDF) at KIT."
                        ],
                        style={"fontFamily": "Arial, sans-serif", "lineHeight": "1.6"},
                    ),
                ],
                style=info_box_style(),
            ),
            # LSDF Storage Section
            html.Div(
                [
                    html.H4(
                        "ASTEC Datasets on LSDF",
                        style={"fontFamily": "Arial, sans-serif", "color": "#2c3e50"},
                    ),
                    html.P(
                        [
                            "The Large Scale Data Facility (LSDF) at Karlsruhe "
                            "Institute of Technology (KIT) serves as the primary "
                            "storage infrastructure for ASTEC simulation datasets. "
                            "The LSDF provides:"
                        ],
                        style={"fontFamily": "Arial, sans-serif", "lineHeight": "1.6"},
                    ),
                    html.Ul(
                        [
                            html.Li(
                                "Petabyte-scale storage capacity for large "
                                "simulation datasets",
                                style={"fontFamily": "Arial, sans-serif"},
                            ),
                            html.Li(
                                "High-performance parallel file systems optimized for "
                                "scientific computing ",
                                style={"fontFamily": "Arial, sans-serif"},
                            ),
                            html.Li(
                                "Secure, backed-up storage with data integrity "
                                "verification",
                                style={"fontFamily": "Arial, sans-serif"},
                            ),
                            html.Li(
                                "Integration with HPC clusters for direct "
                                "computation access ",
                                style={"fontFamily": "Arial, sans-serif"},
                            ),
                            html.Li(
                                "Hierarchical storage management with automatic "
                                "archiving ",
                                style={"fontFamily": "Arial, sans-serif"},
                            ),
                        ],
                        style={
                            "fontFamily": "Arial, sans-serif",
                            "paddingLeft": "1.5rem",
                        },
                    ),
                    html.P(
                        [
                            "ASTEC datasets are organized in a hierarchical directory "
                            "structure on the LSDF, categorized by simulation type, "
                            "reactor model, and accident scenario. Each dataset "
                            "includes comprehensive metadata describing the simulation "
                            "parameters, boundary conditions, and physical models used."
                        ],
                        style={
                            "fontFamily": "Arial, sans-serif",
                            "lineHeight": "1.6",
                            "marginTop": "1rem",
                        },
                    ),
                ],
                style=info_box_style(),
            ),
            html.Hr(),
            html.H4("System Architecture", style={"fontFamily": "Arial, sans-serif"}),
            html.Hr(),
            html.P(
                [
                    "The ASSAS Data Hub employs a modern web architecture connecting "
                    "users to high-performance storage systems. "
                    "The Flask application interfaces with MongoDB for metadata "
                    "management and provides direct access to datasets "
                    "stored on the LSDF infrastructure."
                ],
                style={"fontFamily": "Arial, sans-serif", "lineHeight": "1.6"},
            ),
            html.Hr(),
            # System Overview Image
            html.Div(
                html.Img(
                    src=encode_svg_image_hq("assas_data_hub_system.drawio.svg"),
                    style=responsive_image_style(),
                    alt="ASSAS Data Hub System Overview",
                ),
                style={"textAlign": "center", "margin": "2rem 0", "overflow": "hidden"},
            ),
            html.Hr(),
            html.H4(
                "Data Flow Architecture", style={"fontFamily": "Arial, sans-serif"}
            ),
            html.Hr(),
            html.P(
                [
                    "The data flow diagram illustrates how ASTEC simulation "
                    "results are processed, stored, and made available through "
                    "the web interface. The system handles data "
                    "ingestion, metadata extraction, format conversion, "
                    "and provides multiple access methods for end users."
                ],
                style={"fontFamily": "Arial, sans-serif", "lineHeight": "1.6"},
            ),
            # Data Flow Image
            html.Div(
                html.Img(
                    src=encode_svg_image_hq("assas_data_flow.drawio.svg"),
                    style=responsive_image_style(),
                    alt="ASSAS Data Flow Diagram",
                ),
                style={"textAlign": "center", "margin": "2rem 0", "overflow": "hidden"},
            ),
        ],
        style=content_style(),
    )

    return return_div
