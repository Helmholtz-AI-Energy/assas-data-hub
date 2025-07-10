"""About page for the ASSAS Data Hub project."""

import dash

from dash import html, dcc
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
    return html.Div(
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
                            "The ASSAS Data Hub is a comprehensive data management platform for ASTEC (Accident Source Term Evaluation Code) "
                            "simulation datasets. This Flask-based web application provides researchers and engineers with easy access to "
                            "nuclear safety simulation data stored on the Large Scale Data Facility (LSDF) at KIT."
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
                            "The Large Scale Data Facility (LSDF) at Karlsruhe Institute of Technology (KIT) serves as the primary storage "
                            "infrastructure for ASTEC simulation datasets. The LSDF provides:"
                        ],
                        style={"fontFamily": "Arial, sans-serif", "lineHeight": "1.6"},
                    ),
                    html.Ul(
                        [
                            html.Li(
                                "Petabyte-scale storage capacity for large simulation datasets",
                                style={"fontFamily": "Arial, sans-serif"},
                            ),
                            html.Li(
                                "High-performance parallel file systems optimized for scientific computing",
                                style={"fontFamily": "Arial, sans-serif"},
                            ),
                            html.Li(
                                "Secure, backed-up storage with data integrity verification",
                                style={"fontFamily": "Arial, sans-serif"},
                            ),
                            html.Li(
                                "Integration with HPC clusters for direct computation access",
                                style={"fontFamily": "Arial, sans-serif"},
                            ),
                            html.Li(
                                "Hierarchical storage management with automatic archiving",
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
                            "ASTEC datasets are organized in a hierarchical directory structure on the LSDF, categorized by simulation type, "
                            "reactor model, and accident scenario. Each dataset includes comprehensive metadata describing the simulation "
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
            # Data Access Section
            html.Div(
                [
                    html.H4(
                        "Dataset Download and Access",
                        style={"fontFamily": "Arial, sans-serif", "color": "#2c3e50"},
                    ),
                    html.P(
                        [
                            "The ASSAS Data Hub provides multiple access methods for retrieving ASTEC simulation data:"
                        ],
                        style={"fontFamily": "Arial, sans-serif", "lineHeight": "1.6"},
                    ),
                    html.H5(
                        "1. Web Interface Download",
                        style={
                            "fontFamily": "Arial, sans-serif",
                            "color": "#34495e",
                            "marginTop": "1.5rem",
                        },
                    ),
                    html.P(
                        [
                            "Users can browse and download datasets directly through the web interface. The system provides:"
                        ],
                        style={"fontFamily": "Arial, sans-serif", "lineHeight": "1.6"},
                    ),
                    html.Ul(
                        [
                            html.Li(
                                "Search and filter capabilities by simulation parameters",
                                style={"fontFamily": "Arial, sans-serif"},
                            ),
                            html.Li(
                                "Dataset preview with metadata and summary statistics",
                                style={"fontFamily": "Arial, sans-serif"},
                            ),
                            html.Li(
                                "Compressed HDF5 file downloads for efficient transfer",
                                style={"fontFamily": "Arial, sans-serif"},
                            ),
                            html.Li(
                                "Batch download options for multiple related datasets",
                                style={"fontFamily": "Arial, sans-serif"},
                            ),
                        ],
                        style={
                            "fontFamily": "Arial, sans-serif",
                            "paddingLeft": "1.5rem",
                        },
                    ),
                    html.H5(
                        "2. NetCDF4 API Access",
                        style={
                            "fontFamily": "Arial, sans-serif",
                            "color": "#34495e",
                            "marginTop": "1.5rem",
                        },
                    ),
                    html.P(
                        [
                            "For programmatic access, datasets are available through the NetCDF4 API, enabling direct integration "
                            "with scientific computing workflows:"
                        ],
                        style={"fontFamily": "Arial, sans-serif", "lineHeight": "1.6"},
                    ),
                ],
                style=info_box_style(),
            ),
            # NetCDF4 Code Examples
            html.Div(
                [
                    html.H5(
                        "Python NetCDF4 Usage Examples",
                        style={"fontFamily": "Arial, sans-serif", "color": "#2c3e50"},
                    ),
                    html.P(
                        "Basic dataset access:",
                        style={"fontFamily": "Arial, sans-serif", "fontWeight": "600"},
                    ),
                    html.Pre(
                        [
                            "import netCDF4 as nc\n"
                            "import numpy as np\n"
                            "import matplotlib.pyplot as plt\n\n"
                            "# Open ASTEC dataset\n"
                            "dataset = nc.Dataset('path/to/astec_simulation.nc', 'r')\n\n"
                            "# Access time series data\n"
                            "time = dataset.variables['time'][:]\n"
                            "pressure = dataset.variables['pressure'][:]\n"
                            "temperature = dataset.variables['temperature'][:]\n\n"
                            "# Access metadata\n"
                            "simulation_type = dataset.getncattr('simulation_type')\n"
                            "reactor_model = dataset.getncattr('reactor_model')\n"
                            "print(f'Simulation: {simulation_type}, Reactor: {reactor_model}')"
                        ],
                        style=code_block_style(),
                    ),
                    html.P(
                        "Advanced data analysis:",
                        style={
                            "fontFamily": "Arial, sans-serif",
                            "fontWeight": "600",
                            "marginTop": "1.5rem",
                        },
                    ),
                    html.Pre(
                        [
                            "# Extract specific time ranges\n"
                            "start_time = 3600  # 1 hour\n"
                            "end_time = 7200    # 2 hours\n"
                            "time_mask = (time >= start_time) & (time <= end_time)\n\n"
                            "# Get thermal-hydraulic data\n"
                            "th_data = {\n"
                            "    'pressure': dataset.variables['primary_pressure'][time_mask],\n"
                            "    'level': dataset.variables['steam_generator_level'][time_mask],\n"
                            "    'flow_rate': dataset.variables['coolant_flow_rate'][time_mask]\n"
                            "}\n\n"
                            "# Access 3D spatial data\n"
                            "if 'containment_temperature_3d' in dataset.variables:\n"
                            "    temp_3d = dataset.variables['containment_temperature_3d'][:]\n"
                            "    # Shape: (time, x, y, z)\n"
                            "    print(f'3D temperature field shape: {temp_3d.shape}')"
                        ],
                        style=code_block_style(),
                    ),
                    html.P(
                        "Dataset exploration utilities:",
                        style={
                            "fontFamily": "Arial, sans-serif",
                            "fontWeight": "600",
                            "marginTop": "1.5rem",
                        },
                    ),
                    html.Pre(
                        [
                            "def explore_astec_dataset(filename):\n"
                            '    """Utility function to explore ASTEC NetCDF datasets"""\n'
                            "    with nc.Dataset(filename, 'r') as ds:\n"
                            "        print(f'Dataset: {filename}')\n"
                            "        print(f'Dimensions: {list(ds.dimensions.keys())}')\n"
                            "        print(f'Variables: {list(ds.variables.keys())}')\n"
                            "        print(f'Global attributes: {list(ds.ncattrs())}')\n"
                            "        \n"
                            "        # Print variable details\n"
                            "        for var_name, var in ds.variables.items():\n"
                            "            print(f'{var_name}: {var.shape}, {var.dtype}')\n"
                            "            if hasattr(var, 'units'):\n"
                            "                print(f'  Units: {var.units}')\n"
                            "            if hasattr(var, 'long_name'):\n"
                            "                print(f'  Description: {var.long_name}')"
                        ],
                        style=code_block_style(),
                    ),
                ],
                style=info_box_style(),
            ),
            # Data Format Section
            html.Div(
                [
                    html.H4(
                        "Data Format and Structure",
                        style={"fontFamily": "Arial, sans-serif", "color": "#2c3e50"},
                    ),
                    html.P(
                        [
                            "ASTEC datasets are stored in NetCDF4 format with HDF5 backend, providing:"
                        ],
                        style={"fontFamily": "Arial, sans-serif", "lineHeight": "1.6"},
                    ),
                    html.Ul(
                        [
                            html.Li(
                                "Self-describing data with embedded metadata",
                                style={"fontFamily": "Arial, sans-serif"},
                            ),
                            html.Li(
                                "Efficient compression and chunking for large datasets",
                                style={"fontFamily": "Arial, sans-serif"},
                            ),
                            html.Li(
                                "Cross-platform compatibility (Windows, Linux, macOS)",
                                style={"fontFamily": "Arial, sans-serif"},
                            ),
                            html.Li(
                                "Support for multidimensional arrays and time series",
                                style={"fontFamily": "Arial, sans-serif"},
                            ),
                            html.Li(
                                "Standardized units and coordinate systems",
                                style={"fontFamily": "Arial, sans-serif"},
                            ),
                        ],
                        style={
                            "fontFamily": "Arial, sans-serif",
                            "paddingLeft": "1.5rem",
                        },
                    ),
                    html.H5(
                        "Typical Dataset Contents:",
                        style={
                            "fontFamily": "Arial, sans-serif",
                            "color": "#34495e",
                            "marginTop": "1.5rem",
                        },
                    ),
                    html.Ul(
                        [
                            html.Li(
                                "Thermal-hydraulic variables (pressure, temperature, flow rates)",
                                style={"fontFamily": "Arial, sans-serif"},
                            ),
                            html.Li(
                                "Fission product transport and distribution",
                                style={"fontFamily": "Arial, sans-serif"},
                            ),
                            html.Li(
                                "Containment atmosphere conditions",
                                style={"fontFamily": "Arial, sans-serif"},
                            ),
                            html.Li(
                                "Structural response and material properties",
                                style={"fontFamily": "Arial, sans-serif"},
                            ),
                            html.Li(
                                "Time-dependent boundary conditions",
                                style={"fontFamily": "Arial, sans-serif"},
                            ),
                        ],
                        style={
                            "fontFamily": "Arial, sans-serif",
                            "paddingLeft": "1.5rem",
                        },
                    ),
                ],
                style=info_box_style(),
            ),
            html.Hr(),
            html.H5(
                "Source Code available under", style={"fontFamily": "Arial, sans-serif"}
            ),
            html.Div(
                dcc.Link(
                    "https://github.com/Helmholtz-AI-Energy/assas-data-hub",
                    href="https://github.com/Helmholtz-AI-Energy/assas-data-hub",
                    style={
                        "fontFamily": "Arial, sans-serif",
                        "fontSize": "16px",
                        "color": "#007bff",
                    },
                )
            ),
            html.Hr(),
            html.H4("System Architecture", style={"fontFamily": "Arial, sans-serif"}),
            html.Hr(),
            html.P(
                [
                    "The ASSAS Data Hub employs a modern web architecture connecting users to high-performance storage systems. "
                    "The Flask application interfaces with MongoDB for metadata management and provides direct access to "
                    "datasets stored on the LSDF infrastructure."
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
                    "The data flow diagram illustrates how ASTEC simulation results are processed, stored, and made available "
                    "through the web interface. The system handles data ingestion, metadata extraction, format conversion, "
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
            # Technical Specifications
            html.Div(
                [
                    html.H4(
                        "Technical Specifications",
                        style={"fontFamily": "Arial, sans-serif", "color": "#2c3e50"},
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H6(
                                        "Backend Technologies",
                                        style={
                                            "fontFamily": "Arial, sans-serif",
                                            "color": "#34495e",
                                        },
                                    ),
                                    html.Ul(
                                        [
                                            html.Li(
                                                "Python Flask web framework",
                                                style={
                                                    "fontFamily": "Arial, sans-serif"
                                                },
                                            ),
                                            html.Li(
                                                "MongoDB for metadata storage",
                                                style={
                                                    "fontFamily": "Arial, sans-serif"
                                                },
                                            ),
                                            html.Li(
                                                "NetCDF4/HDF5 for scientific data",
                                                style={
                                                    "fontFamily": "Arial, sans-serif"
                                                },
                                            ),
                                            html.Li(
                                                "LSDF integration for storage",
                                                style={
                                                    "fontFamily": "Arial, sans-serif"
                                                },
                                            ),
                                        ],
                                        style={"fontFamily": "Arial, sans-serif"},
                                    ),
                                ],
                                style={
                                    "width": "48%",
                                    "display": "inline-block",
                                    "verticalAlign": "top",
                                },
                            ),
                            html.Div(
                                [
                                    html.H6(
                                        "Frontend Technologies",
                                        style={
                                            "fontFamily": "Arial, sans-serif",
                                            "color": "#34495e",
                                        },
                                    ),
                                    html.Ul(
                                        [
                                            html.Li(
                                                "Plotly Dash for interactive UI",
                                                style={
                                                    "fontFamily": "Arial, sans-serif"
                                                },
                                            ),
                                            html.Li(
                                                "Bootstrap for responsive design",
                                                style={
                                                    "fontFamily": "Arial, sans-serif"
                                                },
                                            ),
                                            html.Li(
                                                "DataTables for dataset browsing",
                                                style={
                                                    "fontFamily": "Arial, sans-serif"
                                                },
                                            ),
                                            html.Li(
                                                "REST API for programmatic access",
                                                style={
                                                    "fontFamily": "Arial, sans-serif"
                                                },
                                            ),
                                        ],
                                        style={"fontFamily": "Arial, sans-serif"},
                                    ),
                                ],
                                style={
                                    "width": "48%",
                                    "display": "inline-block",
                                    "verticalAlign": "top",
                                    "marginLeft": "4%",
                                },
                            ),
                        ]
                    ),
                ],
                style=info_box_style(),
            ),
        ],
        style=content_style(),
    )
