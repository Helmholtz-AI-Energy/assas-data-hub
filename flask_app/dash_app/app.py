import os
import logging
import uuid
import diskcache
import dash_bootstrap_components as dbc

from dash import dash, html, Output, DiskcacheManager
from dash.long_callback import DiskcacheLongCallbackManager
from dash.dependencies import Input, Output
from assasdb import AssasDatabaseManager
from .components import encode_svg_image

logger = logging.getLogger('assas_app')

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [                     
                        dbc.Col(html.Img(src=encode_svg_image('kit_logo.drawio.svg'), height='60px', width='120px'), width=6),
                        dbc.Col(html.Img(src=encode_svg_image('assas_logo.svg'), height='60px', width='60px'), width=3),
                        dbc.Col(dbc.NavbarBrand("ASSAS Data Hub", className="ms-2"), width=3),                                           
                    ],
                    align="center",
                    className="g-0",
                ),
                #href="https://plotly.com",
                style={"textDecoration": "none"},
            ),
            dbc.Nav(
            [
                dbc.NavItem(dbc.NavLink("Home", href="/assas_app/home", active="exact")),
                dbc.NavItem(dbc.NavLink("Database", href="/assas_app/database", active="exact")),
                dbc.NavItem(dbc.NavLink("Upload", href="/assas_app/upload", active="exact")),
                dbc.NavItem(dbc.NavLink("About", href="/assas_app/about", active="exact")),
            ],
            vertical=False,
            pills=True,
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),            
        ]
    ),    
    color="dark",
    dark=True,    
)

def init_dashboard(server):
    """Create a Plotly Dash dashboard."""
    
    pages_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pages")
    assets_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    logger.debug('pages folder %s, assets_folder %s' % (pages_folder, assets_folder))
    
    launch_uid = uuid.uuid4()
       
    ## Diskcache
    cache = diskcache.Cache("./cache")
    long_callback_manager = DiskcacheLongCallbackManager(
        cache, cache_by=[lambda: launch_uid], expire=60,
    )
    
    # Background callbacks require a cache manager
    #background_callback_manager = DiskcacheManager(
    #    cache, cache_by=[lambda: launch_uid], expire=60,
    #)
    
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix='/assas_app/',
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        use_pages=True,
        pages_folder=pages_folder,
        assets_folder=assets_folder,
        long_callback_manager=long_callback_manager,
        #background_callback_manager=background_callback_manager
    )
    
    #dash_app.index_string = html_layout

    # Create Dash Layout
    dash_app.layout = html.Div([
        navbar,
        html.Hr(),
        dash.page_container    
        ],id='dash-container')
    
    return dash_app.server
