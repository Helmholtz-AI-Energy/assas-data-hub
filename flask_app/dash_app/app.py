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
from flask import redirect, request, session
from ..auth_utils import auth, is_authenticated, get_current_user

logger = logging.getLogger('assas_app')

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        #dbc.Col(html.Img(src=encode_svg_image('assas_logo.svg'), height='60px', width='120px', style={'border':'1px grey solid'}), width=6),
                        dbc.Col(html.Img(src=encode_svg_image('assas_logo_mod.svg'), height='60px', width='120px', style={'border':'1px grey solid'}), width=4),
                        dbc.Col(html.Img(src=encode_svg_image('kit_logo.drawio.svg'), height='60px', width='120px', style={'border':'1px grey solid'}), width=4),
                        dbc.Col(dbc.NavbarBrand('ASSAS Data Hub', className='ms-2'), width=3),                                 
                    ],
                    align='center',
                    className='g-0',
                ),
                #href='https://plotly.com',
                style={'textDecoration': 'none'},
            ),
            dbc.Nav(
            [
                dbc.NavItem(dbc.NavLink('Home', href='/assas_app/home', active='exact')),
                dbc.NavItem(dbc.NavLink('Database', href='/assas_app/database', active='exact')),
                #dbc.NavItem(dbc.NavLink('Upload', href='/assas_app/upload', active='exact')),
                dbc.NavItem(dbc.NavLink('About', href='/assas_app/about', active='exact')),
                #dbc.DropdownMenu(
                #    nav=True,
                #    in_navbar=True,
                #    label='User',
                #    children=[
                #        dbc.DropdownMenuItem('Profile', href='/assas_app/profile'),
                #        dbc.DropdownMenuItem('Admin', href='/assas_app/admin'),
                #        dbc.DropdownMenuItem(divider=True),
                #        dbc.DropdownMenuItem('Logout', href='/assas_app/logout'),
                #    ],
                #),
            ],
            vertical=False,
            pills=True,
            ),
            dbc.NavbarToggler(id='navbar-toggler', n_clicks=0),
        ]
    ),    
    color='dark',
    dark=True,    
)

def init_dashboard(server):
    '''Create a Plotly Dash dashboard.'''
    
    pages_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pages')
    assets_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
    logger.debug('pages folder %s, assets_folder %s' % (pages_folder, assets_folder))
    
    launch_uid = uuid.uuid4()
       
    ## Diskcache
    cache = diskcache.Cache('./cache')
    long_callback_manager = DiskcacheLongCallbackManager(
        cache, cache_by=[lambda: launch_uid], expire=60,
    )
    
    # Background callbacks require a cache manager
    #background_callback_manager = DiskcacheManager(
    #    cache, cache_by=[lambda: launch_uid], expire=60,
    #)
    # Protect Dash pages
    @server.before_request
    @auth.login_required
    def restrict_access():
        """
        Restrict access to Dash pages for unauthenticated users.
        """
        logger.info('Checking authentication for Dash app access.')
        currrent_user = get_current_user()
        logger.info(f'Current user: {currrent_user}')
        
        if not is_authenticated() and request.path.startswith('/assas_app/'):
            return redirect('/login')  # Redirect unauthenticated users to the login page
    
    dash_app = dash.Dash(
        server=server,
        url_base_pathname='/assas_app/',
        title='ASSAS Data Hub',
        #routes_pathname_prefix='/assas_app/',
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        use_pages=True,
        pages_folder=pages_folder,
        assets_folder=assets_folder,
        long_callback_manager=long_callback_manager,
        #background_callback_manager=background_callback_manager
        suppress_callback_exceptions = True
    )
    
    # Create Dash Layout
    dash_app.layout = html.Div([
        navbar,
        html.Hr(),
        dash.page_container
        ],id='dash-container')
    
    return dash_app
