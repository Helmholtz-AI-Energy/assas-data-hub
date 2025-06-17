import dash

from dash import html, dcc
from ..components import content_style, encode_svg_image
from flask_app.auth_utils import is_authenticated

dash.register_page(__name__, path='/home')

def layout():
    """Layout for the Home page."""
    return html.Div([
        html.Hr(),
        #html.Img(src=encode_svg_image('ASSAS logo.svg'), height='300px', width='900px'),html.Img(src=encode_svg_image('kit_logo.drawio.svg'), height='300px', width='800px'),
        #html.Hr(),
        html.H1('ASSAS Database - ASSAS Data Hub'),
        html.H5('A software platform to store and visualize training datasets for ASTEC simulations.'),
        #html.Img(src=encode_svg_image('kit_logo.drawio.svg'), height='300px', width='800px'),
        #html.Hr(),
        html.H5('ASSAS Training Datasets stored on the LSDF at the KIT.'),
        html.Div(
                dcc.Link(f'ASSAS Training Dataset Index', href='/assas_app/database')
            ),
        html.Img(src=encode_svg_image('assas_introduction.drawio.svg'), height='600px', width='600px'),
        html.Hr(),
        ],style=content_style())