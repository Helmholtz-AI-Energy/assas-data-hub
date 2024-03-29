import dash
import logging
import dash_bootstrap_components as dbc

from dash import html, dcc, Input, Output, State, callback

from flask_login import login_user, current_user
from werkzeug.security import check_password_hash

from ..components import encode_svg_image
from ...users_mgt import User, AssasUserManager

logger = logging.getLogger('assas_app')

dash.register_page(__name__, path='/login')

layout = dbc.Container([
    html.Br(),
    dbc.Container([
        dcc.Location(id='urlLogin', refresh=True),
        html.Div([
            dbc.Container(
                html.Img(
                    src=encode_svg_image('assas_logo.svg'),
                    className='center'
                ),
            ),
            dbc.Container(id='loginType', children=[
                dcc.Input(
                    placeholder='Enter your username',
                    type='text',
                    id='usernameBox',
                    className='form-control',
                    n_submit=0,
                ),
                html.Br(),
                dcc.Input(
                    placeholder='Enter your password',
                    type='password',
                    id='passwordBox',
                    className='form-control',
                    n_submit=0,
                ),
                html.Br(),
                html.Button(
                    children='Login',
                    n_clicks=0,
                    type='submit',
                    id='loginButton',
                    className='btn btn-primary btn-lg'
                ),
                html.Br(),
            ], className='form-group'),
        ]),
    ], className='jumbotron')
])



################################################################################
# LOGIN BUTTON CLICKED / ENTER PRESSED - REDIRECT TO PAGE1 IF LOGIN DETAILS ARE CORRECT
################################################################################
@callback(Output('urlLogin', 'pathname'),
              [Input('loginButton', 'n_clicks'),
              Input('usernameBox', 'n_submit'),
              Input('passwordBox', 'n_submit')],
              [State('usernameBox', 'value'),
               State('passwordBox', 'value')])
def sucess(n_clicks, usernameSubmit, passwordSubmit, username, password):
    
    #User.query.filter_by(username=username).first()
    user = AssasUserManager().get_user_o(username)
    
    if user:
        if check_password_hash(user.password(), password):
            login_user(user)
            
            logger.info(f'current_user {current_user.email()}')
            
            return '/assas_app/home'
        else:
            pass
    else:
        pass

################################################################################
# LOGIN BUTTON CLICKED / ENTER PRESSED - RETURN RED BOXES IF LOGIN DETAILS INCORRECT
################################################################################
@callback(Output('passwordBox', 'className'),
              [Input('loginButton', 'n_clicks'),
              Input('usernameBox', 'n_submit'),
              Input('passwordBox', 'n_submit')],
              [State('usernameBox', 'value'),
               State('passwordBox', 'value')])
def update_output(n_clicks, usernameSubmit, passwordSubmit, username, password):
    
    if (n_clicks > 0) or (usernameSubmit > 0) or (passwordSubmit) > 0:
        #User.query.filter_by(username=username).first()
        user = AssasUserManager().get_user_o(username)
        
        if user:
            
            logger.info(f'check {user.username()}{user.password()} {password}')
            
            if check_password_hash(user.password(), password):
                return 'form-control'
            else:
                return 'form-control is-invalid'
        else:
            return 'form-control is-invalid'
    else:
        return 'form-control'
