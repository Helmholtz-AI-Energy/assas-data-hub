"""Home page for the ASSAS Data Hub Dash application.

This page provides an introduction to the ASSAS Data Hub, including a brief description
of its purpose, features, and navigation to key sections.
"""

import dash

from dash import html, dcc
from ..components import content_style, encode_svg_image

dash.register_page(__name__, path="/home")


def hero_section_style() -> dict:
    """Define styles for the hero section.
    
    Returns:
        dict: CSS styles for hero section.
    """
    return {
        "backgroundColor": "#f8f9fa",
        "padding": "3rem 2rem",
        "margin": "-2rem -0.5rem 2rem -0.5rem",
        "textAlign": "center",
        "borderRadius": "0 0 12px 12px",
        "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
        "fontFamily": "Arial, sans-serif",
        
        # Mobile styles
        "@media (max-width: 768px)": {
            "padding": "2rem 1rem",
            "margin": "-2rem -0.125rem 1.5rem -0.125rem",
        },
    }


def card_style() -> dict:
    """Define styles for feature cards.
    
    Returns:
        dict: CSS styles for cards.
    """
    return {
        "backgroundColor": "#ffffff",
        "border": "1px solid #e9ecef",
        "borderRadius": "8px",
        "padding": "1.5rem",
        "margin": "1rem 0",
        "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.08)",
        "transition": "transform 0.2s ease, box-shadow 0.2s ease",
        "fontFamily": "Arial, sans-serif",
        "height": "100%",
        
        ":hover": {
            "transform": "translateY(-2px)",
            "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.12)",
        },
    }


def button_style() -> dict:
    """Define styles for action buttons.
    
    Returns:
        dict: CSS styles for buttons.
    """
    return {
        "backgroundColor": "#007bff",
        "color": "white",
        "padding": "12px 24px",
        "border": "none",
        "borderRadius": "6px",
        "textDecoration": "none",
        "display": "inline-block",
        "fontWeight": "600",
        "fontSize": "16px",
        "fontFamily": "Arial, sans-serif",
        "transition": "background-color 0.2s ease",
        "cursor": "pointer",
        "margin": "0.5rem",
        
        ":hover": {
            "backgroundColor": "#0056b3",
        },
        
        # Mobile styles
        "@media (max-width: 576px)": {
            "padding": "10px 20px",
            "fontSize": "14px",
            "margin": "0.25rem",
        },
    }


def stats_style() -> dict:
    """Define styles for statistics section.
    
    Returns:
        dict: CSS styles for stats.
    """
    return {
        "backgroundColor": "#e3f2fd",
        "padding": "2rem",
        "borderRadius": "8px",
        "margin": "2rem 0",
        "textAlign": "center",
        "fontFamily": "Arial, sans-serif",
        
        # Mobile styles
        "@media (max-width: 768px)": {
            "padding": "1.5rem 1rem",
        },
    }


def responsive_image_style() -> dict:
    """Define responsive styles for images.
    
    Returns:
        dict: CSS styles for responsive images.
    """
    return {
        "maxWidth": "100%",
        "height": "auto",
        "width": "auto",
        "display": "block",
        "margin": "2rem auto",
        "borderRadius": "8px",
        "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
        
        # Desktop styles
        "@media (min-width: 992px)": {
            "maxWidth": "800px",
            "width": "100%",
        },
        
        # Tablet styles
        "@media (max-width: 991px) and (min-width: 577px)": {
            "maxWidth": "100%",
            "width": "95%",
        },
        
        # Mobile styles
        "@media (max-width: 576px)": {
            "width": "100%",
            "margin": "1rem auto",
        },
    }


def layout() -> html.Div:
    """Layout for the Home page."""
    return html.Div(
        [
            # Hero Section
            html.Div([
                html.H1("ASSAS Data Hub", style={
                    "fontSize": "3rem", 
                    "fontWeight": "700", 
                    "color": "#2c3e50",
                    "marginBottom": "1rem",
                    "fontFamily": "Arial, sans-serif",
                    # Mobile responsive font size
                    "@media (max-width: 768px)": {
                        "fontSize": "2.5rem",
                    },
                    "@media (max-width: 576px)": {
                        "fontSize": "2rem",
                    },
                }),
                html.H3("Advanced Nuclear Safety Analysis Data Platform", style={
                    "fontSize": "1.5rem",
                    "fontWeight": "400",
                    "color": "#34495e",
                    "marginBottom": "2rem",
                    "fontFamily": "Arial, sans-serif",
                    # Mobile responsive
                    "@media (max-width: 768px)": {
                        "fontSize": "1.25rem",
                    },
                    "@media (max-width: 576px)": {
                        "fontSize": "1.1rem",
                    },
                }),
                html.P([
                    "Access comprehensive ASTEC simulation datasets stored on the Large Scale Data Facility (LSDF) "
                    "at Karlsruhe Institute of Technology. Our platform provides researchers and engineers with "
                    "powerful tools for nuclear safety analysis and training."
                ], style={
                    "fontSize": "1.1rem",
                    "lineHeight": "1.6",
                    "color": "#5a6c7d",
                    "maxWidth": "800px",
                    "margin": "0 auto 2rem auto",
                    "fontFamily": "Arial, sans-serif",
                    # Mobile responsive
                    "@media (max-width: 576px)": {
                        "fontSize": "1rem",
                    },
                }),
                
                # Action Buttons
                html.Div([
                    dcc.Link("Explore Datasets", href="/assas_app/database", style=button_style()),
                    dcc.Link("Learn More", href="/assas_app/about", style={
                        **button_style(),
                        "backgroundColor": "#28a745",
                        ":hover": {"backgroundColor": "#1e7e34"},
                    }),
                ], style={"marginTop": "1rem"}),
            ], style=hero_section_style()),

            # Key Features Section
            html.Div([
                html.H2("Key Features", style={
                    "textAlign": "center",
                    "color": "#2c3e50",
                    "marginBottom": "2rem",
                    "fontFamily": "Arial, sans-serif",
                }),
                
                # Feature Cards Grid
                html.Div([
                    # First Row
                    html.Div([
                        html.Div([
                            html.Div([
                                html.H4("🔍 Advanced Search", style={"color": "#007bff", "fontFamily": "Arial, sans-serif"}),
                                html.P([
                                    "Search and filter ASTEC datasets by simulation parameters, reactor models, "
                                    "accident scenarios, and physical phenomena."
                                ], style={"lineHeight": "1.6", "fontFamily": "Arial, sans-serif"}),
                            ], style=card_style()),
                        ], style={"width": "48%", "display": "inline-block", "verticalAlign": "top", "margin": "1%"}),
                        
                        html.Div([
                            html.Div([
                                html.H4("📊 Data Visualization", style={"color": "#28a745", "fontFamily": "Arial, sans-serif"}),
                                html.P([
                                    "Interactive tables and metadata preview help you understand dataset contents "
                                    "before downloading."
                                ], style={"lineHeight": "1.6", "fontFamily": "Arial, sans-serif"}),
                            ], style=card_style()),
                        ], style={"width": "48%", "display": "inline-block", "verticalAlign": "top", "margin": "1%"}),
                    ]),
                    
                    # Second Row
                    html.Div([
                        html.Div([
                            html.Div([
                                html.H4("⚡ High Performance", style={"color": "#dc3545", "fontFamily": "Arial, sans-serif"}),
                                html.P([
                                    "Direct access to LSDF storage infrastructure with optimized data transfer "
                                    "and compression for efficient downloads."
                                ], style={"lineHeight": "1.6", "fontFamily": "Arial, sans-serif"}),
                            ], style=card_style()),
                        ], style={"width": "48%", "display": "inline-block", "verticalAlign": "top", "margin": "1%"}),
                        
                        html.Div([
                            html.Div([
                                html.H4("🔌 API Access", style={"color": "#6f42c1", "fontFamily": "Arial, sans-serif"}),
                                html.P([
                                    "Programmatic access via NetCDF4 API for seamless integration with your "
                                    "scientific computing workflows."
                                ], style={"lineHeight": "1.6", "fontFamily": "Arial, sans-serif"}),
                            ], style=card_style()),
                        ], style={"width": "48%", "display": "inline-block", "verticalAlign": "top", "margin": "1%"}),
                    ]),
                ], style={
                    # Mobile stacking
                    "@media (max-width: 768px)": {
                        "display": "block",
                    },
                }),
            ], style={"margin": "3rem 0"}),

            # Statistics Section
            html.Div([
                html.H3("Platform Statistics", style={
                    "textAlign": "center",
                    "color": "#1976d2",
                    "marginBottom": "1.5rem",
                    "fontFamily": "Arial, sans-serif",
                }),
                html.Div([
                    html.Div([
                        html.H2("500+", style={"color": "#007bff", "margin": "0", "fontFamily": "Arial, sans-serif"}),
                        html.P("ASTEC Datasets", style={"margin": "0.5rem 0", "fontFamily": "Arial, sans-serif"}),
                    ], style={"width": "33%", "display": "inline-block", "textAlign": "center", "@media (max-width: 576px)": {"width": "100%", "marginBottom": "1rem"}}),
                    
                    html.Div([
                        html.H2("10TB+", style={"color": "#28a745", "margin": "0", "fontFamily": "Arial, sans-serif"}),
                        html.P("Simulation Data", style={"margin": "0.5rem 0", "fontFamily": "Arial, sans-serif"}),
                    ], style={"width": "33%", "display": "inline-block", "textAlign": "center", "@media (max-width: 576px)": {"width": "100%", "marginBottom": "1rem"}}),
                    
                    html.Div([
                        html.H2("24/7", style={"color": "#dc3545", "margin": "0", "fontFamily": "Arial, sans-serif"}),
                        html.P("Platform Availability", style={"margin": "0.5rem 0", "fontFamily": "Arial, sans-serif"}),
                    ], style={"width": "33%", "display": "inline-block", "textAlign": "center", "@media (max-width: 576px)": {"width": "100%"}}),
                ]),
            ], style=stats_style()),

            # System Overview Image
            html.Div([
                html.H3("System Overview", style={
                    "textAlign": "center",
                    "color": "#2c3e50",
                    "marginBottom": "1rem",
                    "fontFamily": "Arial, sans-serif",
                }),
                html.P([
                    "The ASSAS Data Hub connects researchers to high-performance storage systems, "
                    "providing seamless access to nuclear safety simulation data."
                ], style={
                    "textAlign": "center",
                    "color": "#5a6c7d",
                    "marginBottom": "2rem",
                    "lineHeight": "1.6",
                    "fontFamily": "Arial, sans-serif",
                }),
                html.Img(
                    src=encode_svg_image("assas_introduction.drawio.svg"),
                    style=responsive_image_style(),
                    alt="ASSAS Data Hub System Introduction",
                ),
            ], style={"margin": "3rem 0"}),

            # Getting Started Section
            html.Div([
                html.H3("Getting Started", style={
                    "color": "#2c3e50",
                    "marginBottom": "1.5rem",
                    "fontFamily": "Arial, sans-serif",
                }),
                html.Ol([
                    html.Li([
                        html.Strong("Browse Datasets: ", style={"fontFamily": "Arial, sans-serif"}),
                        "Navigate to the Database section to explore available ASTEC simulation datasets."
                    ], style={"marginBottom": "1rem", "fontFamily": "Arial, sans-serif"}),
                    html.Li([
                        html.Strong("Filter & Search: ", style={"fontFamily": "Arial, sans-serif"}),
                        "Use advanced filters to find datasets matching your research requirements."
                    ], style={"marginBottom": "1rem", "fontFamily": "Arial, sans-serif"}),
                    html.Li([
                        html.Strong("Download Data: ", style={"fontFamily": "Arial, sans-serif"}),
                        "Access datasets through the web interface or programmatically via NetCDF4 API."
                    ], style={"marginBottom": "1rem", "fontFamily": "Arial, sans-serif"}),
                    html.Li([
                        html.Strong("Analyze Results: ", style={"fontFamily": "Arial, sans-serif"}),
                        "Use the comprehensive metadata and documentation for your nuclear safety analysis."
                    ], style={"marginBottom": "1rem", "fontFamily": "Arial, sans-serif"}),
                ], style={"fontSize": "1.1rem", "lineHeight": "1.8", "fontFamily": "Arial, sans-serif"}),
                
                # Quick Action
                html.Div([
                    html.H4("Ready to explore?", style={"color": "#34495e", "fontFamily": "Arial, sans-serif"}),
                    dcc.Link("Start Browsing Datasets →", href="/assas_app/database", style={
                        **button_style(),
                        "fontSize": "18px",
                        "padding": "15px 30px",
                    }),
                ], style={"textAlign": "center", "marginTop": "2rem", "padding": "2rem", "backgroundColor": "#f8f9fa", "borderRadius": "8px"}),
            ], style={
                "backgroundColor": "#ffffff",
                "padding": "2rem",
                "borderRadius": "8px",
                "border": "1px solid #e9ecef",
                "margin": "2rem 0",
            }),

            html.Hr(),
        ],
        style=content_style(),
    )
