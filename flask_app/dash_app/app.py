import dash_bootstrap_components as dbc

from dash import dash, html
from assasdb import AssasDatabaseManager

def init_dashboard(server):
    """Create a Plotly Dash dashboard."""
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix='/dash_app/',
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        use_pages=True,
        pages_folder='/home/jonas/assas_app/flask_app/dash_app/pages',
        assets_folder='/home/jonas/assas_app/flask_app/dash_app/assets'
    )
    
    #dash_app.index_string = html_layout

    # Create Dash Layout
    dash_app.layout = html.Div([
    html.H1('ASSAS Database - ASSAS Data Hub'),
    html.H5('A software platform to store and visualize training datasets for ASTEC simulations.'),
    html.Hr(),
    dash.page_container    
    ],id='dash-container')
    
    return dash_app.server