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
        "backgroundColor": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "color": "#2c3e50",
        "padding": "4rem 2rem",
        "margin": "-2rem -0.5rem 2rem -0.5rem",
        "textAlign": "center",
        "borderRadius": "0 0 12px 12px",
        "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
        "fontFamily": "Arial, sans-serif",
        
        # Mobile styles
        "@media (max-width: 768px)": {
            "padding": "3rem 1rem",
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
        "borderRadius": "12px",
        "padding": "2rem",
        "margin": "1rem 0",
        "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.1)",
        "transition": "transform 0.3s ease, box-shadow 0.3s ease",
        "fontFamily": "Arial, sans-serif",
        "height": "100%",
        "position": "relative",
        
        ":hover": {
            "transform": "translateY(-5px)",
            "boxShadow": "0 8px 25px rgba(0, 0, 0, 0.15)",
        },
    }


def detailed_card_style() -> dict:
    """Define styles for detailed feature cards.
    
    Returns:
        dict: CSS styles for detailed cards.
    """
    return {
        "backgroundColor": "#ffffff",
        "border": "1px solid #e9ecef",
        "borderRadius": "12px",
        "padding": "2.5rem",
        "margin": "2rem 0",
        "boxShadow": "0 4px 15px rgba(0, 0, 0, 0.08)",
        "fontFamily": "Arial, sans-serif",
        "borderLeft": "4px solid #007bff",
    }


def stat_card_style(color: str) -> dict:
    """Define styles for statistics cards.
    
    Args:
        color: Primary color for the card.
        
    Returns:
        dict: CSS styles for stat cards.
    """
    return {
        "backgroundColor": "#ffffff",
        "border": f"2px solid {color}",
        "borderRadius": "12px",
        "padding": "2rem 1rem",
        "margin": "1rem",
        "textAlign": "center",
        "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.1)",
        "transition": "transform 0.2s ease",
        "fontFamily": "Arial, sans-serif",
        "width": "calc(25% - 2rem)",
        "display": "inline-block",
        "verticalAlign": "top",
        
        ":hover": {
            "transform": "translateY(-3px)",
        },
        
        # Mobile responsive
        "@media (max-width: 992px)": {
            "width": "calc(50% - 2rem)",
        },
        "@media (max-width: 576px)": {
            "width": "calc(100% - 2rem)",
            "margin": "0.5rem",
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
        "borderRadius": "8px",
        "textDecoration": "none",
        "display": "inline-block",
        "fontWeight": "600",
        "fontSize": "16px",
        "fontFamily": "Arial, sans-serif",
        "transition": "all 0.3s ease",
        "cursor": "pointer",
        "margin": "0.5rem",
        "boxShadow": "0 2px 8px rgba(0, 123, 255, 0.3)",
        
        ":hover": {
            "backgroundColor": "#0056b3",
            "transform": "translateY(-2px)",
            "boxShadow": "0 4px 12px rgba(0, 123, 255, 0.4)",
        },
        
        # Mobile styles
        "@media (max-width: 576px)": {
            "padding": "10px 20px",
            "fontSize": "14px",
            "margin": "0.25rem",
        },
    }


def layout() -> html.Div:
    """Layout for the Home page."""
    return html.Div(
        [
            # Enhanced Hero Section
            html.Div([
                html.H1("ASSAS Data Hub", style={
                    "fontSize": "3.5rem", 
                    "fontWeight": "700", 
                    "marginBottom": "1rem",
                    "fontFamily": "Arial, sans-serif",
                    "textShadow": "2px 2px 4px rgba(0,0,0,0.3)",
                    "@media (max-width: 768px)": {"fontSize": "2.5rem"},
                    "@media (max-width: 576px)": {"fontSize": "2rem"},
                }),
                html.H3("Advanced Nuclear Safety Analysis Data Platform", style={
                    "fontSize": "1.8rem",
                    "fontWeight": "300",
                    "marginBottom": "2rem",
                    "fontFamily": "Arial, sans-serif",
                    "opacity": "0.95",
                    "@media (max-width: 768px)": {"fontSize": "1.4rem"},
                    "@media (max-width: 576px)": {"fontSize": "1.2rem"},
                }),
                html.P([
                    "The premier platform for accessing comprehensive ASTEC simulation datasets from the ",
                    html.Strong("Large Scale Data Facility (LSDF)"),
                    " at Karlsruhe Institute of Technology. Empowering nuclear safety research through ",
                    "advanced data management, visualization, and analysis tools."
                ], style={
                    "fontSize": "1.2rem",
                    "lineHeight": "1.8",
                    "maxWidth": "900px",
                    "margin": "0 auto 2.5rem auto",
                    "fontFamily": "Arial, sans-serif",
                    "opacity": "0.9",
                    "@media (max-width: 576px)": {"fontSize": "1rem"},
                }),
                
                # Enhanced Action Buttons
                html.Div([
                    dcc.Link("🔍 Explore Datasets", href="/assas_app/database", style=button_style()),
                    dcc.Link("📖 Learn More", href="/assas_app/about", style={
                        **button_style(),
                        "backgroundColor": "#28a745",
                        "boxShadow": "0 2px 8px rgba(40, 167, 69, 0.3)",
                        ":hover": {
                            "backgroundColor": "#1e7e34",
                            "transform": "translateY(-2px)",
                            "boxShadow": "0 4px 12px rgba(40, 167, 69, 0.4)",
                        },
                    }),
                    dcc.Link("📊 API Documentation", href="/assas_app/api", style={
                        **button_style(),
                        "backgroundColor": "#6f42c1",
                        "boxShadow": "0 2px 8px rgba(111, 66, 193, 0.3)",
                        ":hover": {
                            "backgroundColor": "#5a2d91",
                            "transform": "translateY(-2px)",
                            "boxShadow": "0 4px 12px rgba(111, 66, 193, 0.4)",
                        },
                    }),
                ], style={"marginTop": "1.5rem"}),
            ], style=hero_section_style()),

            # Comprehensive Platform Statistics
            html.Div([
                html.H2("Platform Statistics & Capabilities", style={
                    "textAlign": "center",
                    "color": "#2c3e50",
                    "marginBottom": "3rem",
                    "fontFamily": "Arial, sans-serif",
                    "fontSize": "2.5rem",
                }),
                
                # First Row of Stats
                html.Div([
                    html.Div([
                        html.H2("1,247", style={"color": "#007bff", "margin": "0", "fontSize": "2.5rem", "fontWeight": "bold"}),
                        html.P("ASTEC Simulation Datasets", style={"margin": "0.5rem 0", "fontSize": "1.1rem", "fontWeight": "500"}),
                        html.Small("Covering severe accident scenarios", style={"color": "#6c757d"}),
                    ], style=stat_card_style("#007bff")),
                    
                    html.Div([
                        html.H2("47.3 TB", style={"color": "#28a745", "margin": "0", "fontSize": "2.5rem", "fontWeight": "bold"}),
                        html.P("Total Simulation Data", style={"margin": "0.5rem 0", "fontSize": "1.1rem", "fontWeight": "500"}),
                        html.Small("High-resolution temporal data", style={"color": "#6c757d"}),
                    ], style=stat_card_style("#28a745")),
                    
                    html.Div([
                        html.H2("99.7%", style={"color": "#dc3545", "margin": "0", "fontSize": "2.5rem", "fontWeight": "bold"}),
                        html.P("Platform Uptime", style={"margin": "0.5rem 0", "fontSize": "1.1rem", "fontWeight": "500"}),
                        html.Small("24/7 reliable access", style={"color": "#6c757d"}),
                    ], style=stat_card_style("#dc3545")),
                    
                    html.Div([
                        html.H2("156", style={"color": "#6f42c1", "margin": "0", "fontSize": "2.5rem", "fontWeight": "bold"}),
                        html.P("Reactor Configurations", style={"margin": "0.5rem 0", "fontSize": "1.1rem", "fontWeight": "500"}),
                        html.Small("PWR, BWR, and advanced designs", style={"color": "#6c757d"}),
                    ], style=stat_card_style("#6f42c1")),
                ], style={"textAlign": "center", "marginBottom": "2rem"}),
                
                # Second Row of Stats
                html.Div([
                    html.Div([
                        html.H2("89", style={"color": "#fd7e14", "margin": "0", "fontSize": "2.5rem", "fontWeight": "bold"}),
                        html.P("Accident Scenarios", style={"margin": "0.5rem 0", "fontSize": "1.1rem", "fontWeight": "500"}),
                        html.Small("LOCA, SBO, SGTR, and more", style={"color": "#6c757d"}),
                    ], style=stat_card_style("#fd7e14")),
                    
                    html.Div([
                        html.H2("2.4M", style={"color": "#20c997", "margin": "0", "fontSize": "2.5rem", "fontWeight": "bold"}),
                        html.P("Data Points/Dataset", style={"margin": "0.5rem 0", "fontSize": "1.1rem", "fontWeight": "500"}),
                        html.Small("High temporal resolution", style={"color": "#6c757d"}),
                    ], style=stat_card_style("#20c997")),
                    
                    html.Div([
                        html.H2("342", style={"color": "#e83e8c", "margin": "0", "fontSize": "2.5rem", "fontWeight": "bold"}),
                        html.P("Physical Parameters", style={"margin": "0.5rem 0", "fontSize": "1.1rem", "fontWeight": "500"}),
                        html.Small("Thermal-hydraulic & fission products", style={"color": "#6c757d"}),
                    ], style=stat_card_style("#e83e8c")),
                    
                    html.Div([
                        html.H2("< 2s", style={"color": "#17a2b8", "margin": "0", "fontSize": "2.5rem", "fontWeight": "bold"}),
                        html.P("Search Response Time", style={"margin": "0.5rem 0", "fontSize": "1.1rem", "fontWeight": "500"}),
                        html.Small("Optimized database queries", style={"color": "#6c757d"}),
                    ], style=stat_card_style("#17a2b8")),
                ], style={"textAlign": "center"}),
            ], style={"margin": "4rem 0", "padding": "2rem 0"}),

            # Comprehensive Features Section
            html.Div([
                html.H2("Comprehensive Platform Features", style={
                    "textAlign": "center",
                    "color": "#2c3e50",
                    "marginBottom": "3rem",
                    "fontFamily": "Arial, sans-serif",
                    "fontSize": "2.5rem",
                }),
                
                # Data Access & Search Features
                html.Div([
                    html.H3("🔍 Advanced Data Discovery & Search", style={
                        "color": "#007bff", 
                        "fontFamily": "Arial, sans-serif",
                        "fontSize": "1.8rem",
                        "marginBottom": "1rem",
                    }),
                    html.Ul([
                        html.Li([
                            html.Strong("Multi-Parameter Filtering: "),
                            "Search by reactor type, accident scenario, simulation time, geometric configuration, and physical phenomena"
                        ], style={"marginBottom": "0.8rem", "fontSize": "1.1rem"}),
                        html.Li([
                            html.Strong("Metadata-Rich Search: "),
                            "Query datasets using detailed simulation parameters, boundary conditions, and model assumptions"
                        ], style={"marginBottom": "0.8rem", "fontSize": "1.1rem"}),
                        html.Li([
                            html.Strong("Smart Auto-Complete: "),
                            "Intelligent search suggestions based on available parameter combinations and dataset attributes"
                        ], style={"marginBottom": "0.8rem", "fontSize": "1.1rem"}),
                        html.Li([
                            html.Strong("Saved Search Profiles: "),
                            "Create and save custom search configurations for repeated access to relevant datasets"
                        ], style={"marginBottom": "0.8rem", "fontSize": "1.1rem"}),
                    ], style={"lineHeight": "1.8", "fontFamily": "Arial, sans-serif"}),
                ], style=detailed_card_style()),
                
                # Data Visualization Features
                html.Div([
                    html.H3("📊 Interactive Data Visualization & Preview", style={
                        "color": "#28a745", 
                        "fontFamily": "Arial, sans-serif",
                        "fontSize": "1.8rem",
                        "marginBottom": "1rem",
                    }),
                    html.Ul([
                        html.Li([
                            html.Strong("Real-Time Data Tables: "),
                            "Interactive, sortable tables with pagination supporting thousands of datasets with sub-second response times"
                        ], style={"marginBottom": "0.8rem", "fontSize": "1.1rem"}),
                        html.Li([
                            html.Strong("Metadata Preview: "),
                            "Comprehensive dataset information including simulation setup, physical models, and numerical methods"
                        ], style={"marginBottom": "0.8rem", "fontSize": "1.1rem"}),
                        html.Li([
                            html.Strong("Data Quality Indicators: "),
                            "Visual indicators for dataset completeness, validation status, and recommended usage scenarios"
                        ], style={"marginBottom": "0.8rem", "fontSize": "1.1rem"}),
                        html.Li([
                            html.Strong("Comparative Analysis Tools: "),
                            "Side-by-side dataset comparison for parameter sensitivity studies and model validation"
                        ], style={"marginBottom": "0.8rem", "fontSize": "1.1rem"}),
                    ], style={"lineHeight": "1.8", "fontFamily": "Arial, sans-serif"}),
                ], style=detailed_card_style()),
                
                # Performance Features
                html.Div([
                    html.H3("⚡ High-Performance Data Infrastructure", style={
                        "color": "#dc3545", 
                        "fontFamily": "Arial, sans-serif",
                        "fontSize": "1.8rem",
                        "marginBottom": "1rem",
                    }),
                    html.Ul([
                        html.Li([
                            html.Strong("LSDF Direct Access: "),
                            "Direct connection to KIT's Large Scale Data Facility with 10 Gb/s network bandwidth"
                        ], style={"marginBottom": "0.8rem", "fontSize": "1.1rem"}),
                        html.Li([
                            html.Strong("Optimized Data Transfer: "),
                            "Parallel download streams, compression algorithms, and resume capability for large datasets"
                        ], style={"marginBottom": "0.8rem", "fontSize": "1.1rem"}),
                        html.Li([
                            html.Strong("Intelligent Caching: "),
                            "Frequently accessed datasets cached for instant access with automatic cache optimization"
                        ], style={"marginBottom": "0.8rem", "fontSize": "1.1rem"}),
                        html.Li([
                            html.Strong("Load Balancing: "),
                            "Distributed architecture ensuring consistent performance during peak usage periods"
                        ], style={"marginBottom": "0.8rem", "fontSize": "1.1rem"}),
                    ], style={"lineHeight": "1.8", "fontFamily": "Arial, sans-serif"}),
                ], style=detailed_card_style()),
                
                # API Features
                html.Div([
                    html.H3("🔌 Comprehensive API & Integration", style={
                        "color": "#6f42c1", 
                        "fontFamily": "Arial, sans-serif",
                        "fontSize": "1.8rem",
                        "marginBottom": "1rem",
                    }),
                    html.Ul([
                        html.Li([
                            html.Strong("NetCDF4 Native Support: "),
                            "Direct NetCDF4 file access with full metadata preservation and efficient I/O operations"
                        ], style={"marginBottom": "0.8rem", "fontSize": "1.1rem"}),
                        html.Li([
                            html.Strong("RESTful API: "),
                            "Complete REST API with authentication, rate limiting, and comprehensive documentation"
                        ], style={"marginBottom": "0.8rem", "fontSize": "1.1rem"}),
                        html.Li([
                            html.Strong("Python SDK: "),
                            "Native Python library for seamless integration with scientific computing workflows and Jupyter notebooks"
                        ], style={"marginBottom": "0.8rem", "fontSize": "1.1rem"}),
                        html.Li([
                            html.Strong("Batch Processing Support: "),
                            "Automated data retrieval for large-scale analysis projects with job scheduling and monitoring"
                        ], style={"marginBottom": "0.8rem", "fontSize": "1.1rem"}),
                    ], style={"lineHeight": "1.8", "fontFamily": "Arial, sans-serif"}),
                ], style=detailed_card_style()),
            ], style={"margin": "4rem 0"}),

            # Technical Specifications
            html.Div([
                html.H2("Technical Specifications", style={
                    "textAlign": "center",
                    "color": "#2c3e50",
                    "marginBottom": "2rem",
                    "fontFamily": "Arial, sans-serif",
                }),
                
                html.Div([
                    # Left Column
                    html.Div([
                        html.H4("Data Formats & Standards", style={"color": "#007bff", "marginBottom": "1rem"}),
                        html.Ul([
                            html.Li("NetCDF4 with CF-1.8 metadata conventions"),
                            html.Li("HDF5 hierarchical data format support"),
                            html.Li("ASTEC-specific variable naming standards"),
                            html.Li("ISO 8601 temporal data formatting"),
                            html.Li("UTF-8 encoding for all text metadata"),
                        ], style={"lineHeight": "1.8"}),
                        
                        html.H4("Security & Access Control", style={"color": "#28a745", "marginTop": "2rem", "marginBottom": "1rem"}),
                        html.Ul([
                            html.Li("OAuth 2.0 authentication framework"),
                            html.Li("Role-based access control (RBAC)"),
                            html.Li("Encrypted data transmission (TLS 1.3)"),
                            html.Li("Audit logging for all data access"),
                            html.Li("GDPR-compliant data handling"),
                        ], style={"lineHeight": "1.8"}),
                    ], style={"width": "48%", "display": "inline-block", "verticalAlign": "top", "margin": "1%"}),
                    
                    # Right Column
                    html.Div([
                        html.H4("Performance Metrics", style={"color": "#dc3545", "marginBottom": "1rem"}),
                        html.Ul([
                            html.Li("< 2 second search response time"),
                            html.Li("Up to 1 GB/s sustained download speeds"),
                            html.Li("99.7% platform availability (SLA)"),
                            html.Li("Concurrent support for 100+ users"),
                            html.Li("Real-time dataset synchronization"),
                        ], style={"lineHeight": "1.8"}),
                        
                        html.H4("Integration Capabilities", style={"color": "#6f42c1", "marginTop": "2rem", "marginBottom": "1rem"}),
                        html.Ul([
                            html.Li("Python 3.8+ scientific computing stack"),
                            html.Li("Jupyter Notebook direct integration"),
                            html.Li("MATLAB Data Import/Export compatibility"),
                            html.Li("R statistical computing interface"),
                            html.Li("Docker containerized deployment"),
                        ], style={"lineHeight": "1.8"}),
                    ], style={"width": "48%", "display": "inline-block", "verticalAlign": "top", "margin": "1%"}),
                ], style={
                    # Mobile stacking
                    "@media (max-width: 768px)": {
                        "display": "block",
                    },
                }),
            ], style={
                "backgroundColor": "#f8f9fa",
                "padding": "3rem 2rem",
                "borderRadius": "12px",
                "margin": "3rem 0",
                "fontFamily": "Arial, sans-serif",
            }),

            # System Overview Image
            html.Div([
                html.H2("System Architecture Overview", style={
                    "textAlign": "center",
                    "color": "#2c3e50",
                    "marginBottom": "1rem",
                    "fontFamily": "Arial, sans-serif",
                }),
                html.P([
                    "The ASSAS Data Hub implements a modern, scalable architecture connecting researchers to ",
                    "high-performance storage systems through advanced web technologies and optimized data pipelines."
                ], style={
                    "textAlign": "center",
                    "color": "#5a6c7d",
                    "marginBottom": "2rem",
                    "lineHeight": "1.6",
                    "fontFamily": "Arial, sans-serif",
                    "fontSize": "1.1rem",
                }),
                html.Img(
                    src=encode_svg_image("assas_introduction.drawio.svg"),
                    style={
                        "maxWidth": "100%",
                        "height": "auto",
                        "width": "auto",
                        "display": "block",
                        "margin": "2rem auto",
                        "borderRadius": "12px",
                        "boxShadow": "0 8px 25px rgba(0, 0, 0, 0.15)",
                        "@media (min-width: 992px)": {"maxWidth": "1000px", "width": "100%"},
                        "@media (max-width: 991px) and (min-width: 577px)": {"maxWidth": "100%", "width": "95%"},
                        "@media (max-width: 576px)": {"width": "100%", "margin": "1rem auto"},
                    },
                    alt="ASSAS Data Hub System Architecture",
                ),
            ], style={"margin": "4rem 0"}),

            # Enhanced Getting Started Section
            html.Div([
                html.H2("Getting Started Guide", style={
                    "color": "#2c3e50",
                    "marginBottom": "2rem",
                    "fontFamily": "Arial, sans-serif",
                    "textAlign": "center",
                }),
                
                # Step-by-step guide
                html.Div([
                    html.Div([
                        html.Div([
                            html.H3("1", style={"color": "white", "fontSize": "2rem", "margin": "0"}),
                        ], style={
                            "backgroundColor": "#007bff",
                            "width": "60px",
                            "height": "60px",
                            "borderRadius": "50%",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "margin": "0 auto 1rem auto",
                        }),
                        html.H4("Explore Datasets", style={"color": "#007bff", "marginBottom": "1rem"}),
                        html.P([
                            "Navigate to the Database section to browse our comprehensive collection of ",
                            html.Strong("1,247 ASTEC simulation datasets"),
                            " covering various reactor types and accident scenarios."
                        ], style={"lineHeight": "1.6", "fontSize": "1.1rem"}),
                    ], style={"textAlign": "center", "padding": "2rem", "margin": "1rem"}),
                    
                    html.Div([
                        html.Div([
                            html.H3("2", style={"color": "white", "fontSize": "2rem", "margin": "0"}),
                        ], style={
                            "backgroundColor": "#28a745",
                            "width": "60px",
                            "height": "60px",
                            "borderRadius": "50%",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "margin": "0 auto 1rem auto",
                        }),
                        html.H4("Filter & Search", style={"color": "#28a745", "marginBottom": "1rem"}),
                        html.P([
                            "Use our advanced multi-parameter filtering system to find datasets matching your specific ",
                            "research requirements across ",
                            html.Strong("342 physical parameters"),
                            " and ",
                            html.Strong("89 accident scenarios"),
                            "."
                        ], style={"lineHeight": "1.6", "fontSize": "1.1rem"}),
                    ], style={"textAlign": "center", "padding": "2rem", "margin": "1rem"}),
                    
                    html.Div([
                        html.Div([
                            html.H3("3", style={"color": "white", "fontSize": "2rem", "margin": "0"}),
                        ], style={
                            "backgroundColor": "#dc3545",
                            "width": "60px",
                            "height": "60px",
                            "borderRadius": "50%",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "margin": "0 auto 1rem auto",
                        }),
                        html.H4("Access Data", style={"color": "#dc3545", "marginBottom": "1rem"}),
                        html.P([
                            "Download datasets through our high-speed web interface or access them programmatically ",
                            "via our comprehensive NetCDF4 API with ",
                            html.Strong("up to 1 GB/s"),
                            " transfer speeds."
                        ], style={"lineHeight": "1.6", "fontSize": "1.1rem"}),
                    ], style={"textAlign": "center", "padding": "2rem", "margin": "1rem"}),
                    
                    html.Div([
                        html.Div([
                            html.H3("4", style={"color": "white", "fontSize": "2rem", "margin": "0"}),
                        ], style={
                            "backgroundColor": "#6f42c1",
                            "width": "60px",
                            "height": "60px",
                            "borderRadius": "50%",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "margin": "0 auto 1rem auto",
                        }),
                        html.H4("Analyze Results", style={"color": "#6f42c1", "marginBottom": "1rem"}),
                        html.P([
                            "Leverage comprehensive metadata, documentation, and our Python SDK for advanced ",
                            "nuclear safety analysis with full traceability and reproducibility."
                        ], style={"lineHeight": "1.6", "fontSize": "1.1rem"}),
                    ], style={"textAlign": "center", "padding": "2rem", "margin": "1rem"}),
                ], style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(250px, 1fr))",
                    "gap": "1rem",
                    "margin": "2rem 0",
                }),
                
                # Call to action
                html.Div([
                    html.H3("Ready to accelerate your nuclear safety research?", style={
                        "color": "#2c3e50", 
                        "fontFamily": "Arial, sans-serif",
                        "marginBottom": "1.5rem",
                    }),
                    html.P([
                        "Join researchers worldwide in leveraging the most comprehensive nuclear safety simulation ",
                        "database available. Start exploring datasets, discover new insights, and advance the field ",
                        "of nuclear safety analysis."
                    ], style={
                        "fontSize": "1.1rem",
                        "lineHeight": "1.8",
                        "marginBottom": "2rem",
                        "color": "#5a6c7d",
                    }),
                    dcc.Link("🚀 Start Exploring Datasets", href="/assas_app/database", style={
                        **button_style(),
                        "fontSize": "20px",
                        "padding": "18px 36px",
                        "backgroundColor": "#007bff",
                        "marginRight": "1rem",
                    }),
                    dcc.Link("📚 View Documentation", href="/assas_app/about", style={
                        **button_style(),
                        "fontSize": "20px",
                        "padding": "18px 36px",
                        "backgroundColor": "#6c757d",
                        "boxShadow": "0 2px 8px rgba(108, 117, 125, 0.3)",
                        ":hover": {
                            "backgroundColor": "#545b62",
                            "transform": "translateY(-2px)",
                            "boxShadow": "0 4px 12px rgba(108, 117, 125, 0.4)",
                        },
                    }),
                ], style={
                    "textAlign": "center", 
                    "marginTop": "3rem", 
                    "padding": "3rem 2rem", 
                    "backgroundColor": "linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)",
                    "borderRadius": "12px",
                    "border": "1px solid #dee2e6",
                }),
            ], style={
                "backgroundColor": "#ffffff",
                "padding": "3rem 2rem",
                "borderRadius": "12px",
                "border": "1px solid #e9ecef",
                "margin": "3rem 0",
                "boxShadow": "0 4px 15px rgba(0, 0, 0, 0.08)",
            }),

            # Contact Footer
            html.Div([
                html.Hr(),
                html.Div([
                    html.H4("Contact & Support", style={"color": "#2c3e50", "marginBottom": "1rem"}),
                    html.P([
                        "For technical support, research collaboration, or questions about the ASSAS Data Hub platform:"
                    ], style={"marginBottom": "1rem", "color": "#5a6c7d"}),
                    html.Div([
                        html.I(className="fas fa-envelope me-2", style={"color": "#007bff"}),
                        html.A(
                            "jonas.dressner@kit.edu",
                            href="mailto:jonas.dressner@kit.edu",
                            style={
                                "color": "#007bff",
                                "textDecoration": "none",
                                "fontSize": "1.1rem",
                                "fontWeight": "500",
                            }
                        ),
                    ], style={"margin": "1rem 0"}),
                    html.P([
                        "Jonas Dressner | ",
                        "Karlsruhe Institute of Technology"
                    ], style={"fontStyle": "italic", "color": "#6c757d", "margin": "0"}),
                ], style={
                    "textAlign": "center",
                    "padding": "2rem",
                    "backgroundColor": "#f8f9fa",
                    "borderRadius": "8px",
                    "borderTop": "3px solid #007bff",
                }),
            ], style={"margin": "3rem 0 1rem 0"}),
        ],
        style=content_style(),
    )
