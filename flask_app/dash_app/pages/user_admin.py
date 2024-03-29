import dash
import dash_bootstrap_components as dbc
import logging

from dash import Dash, dash_table, html, dcc, Input, Output, callback, State

from ...users_mgt import show_users, add_user

logger = logging.getLogger('assas_app')

dash.register_page(__name__, path='/admin')

layout = dbc.Container([
    html.Br(),
    dbc.Container([
        dcc.Location(id='urlUserAdmin', refresh=True),
        html.H3('Add New User'),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dbc.Label('Username: '),
                dcc.Input(
                    id='newUsername',
                    className='form-control',
                    n_submit=0,
                    style={
                        'width' : '90%'
                    },
                ),
                dbc.Label('Firstname: '),
                dcc.Input(
                    id='newFirstname',
                    className='form-control',
                    n_submit=0,
                    style={
                        'width' : '90%'
                    },
                ),
                html.Br(),
                dbc.Label('Password: '),
                dcc.Input(
                    id='newPwd1',
                    type='password',
                    className='form-control',
                    n_submit=0,
                    style={
                        'width' : '90%'
                    },
                ),
                html.Br(),
                dbc.Label('Retype New Password: '),
                dcc.Input(
                    id='newPwd2',
                    type='password',
                    className='form-control',
                    n_submit=0,
                    style={
                        'width' : '90%'
                    },
                ),
                html.Br(),
            ], md=4),

            dbc.Col([
                dbc.Label('Institute: '),
                dcc.Input(
                    id='newInstitute',
                    className='form-control',
                    n_submit=0,
                    style={
                        'width' : '90%'
                    },
                ),
                dbc.Label('Lastname: '),
                dcc.Input(
                    id='newLastname',
                    className='form-control',
                    n_submit=0,
                    style={
                        'width' : '90%'
                    },
                ),
                html.Br(),
                dbc.Label('Admin? '),
                dcc.Dropdown(
                    id='admin',
                    style={
                        'width' : '90%'
                    },
                    options=[
                        {'label' : 'Yes', 'value' : 1},
                        {'label' : 'No', 'value' : 0},
                    ],
                    value=0,
                    clearable=False
                ),
                html.Br(),
                html.Br(),
                html.Button(
                    children='Create User',
                    id='createUserButton',
                    n_clicks=0,
                    type='submit',
                    className='btn btn-primary btn-lg'
                ),
                html.Br(),
                html.Div(id='createUserSuccess',children=[html.Div(children=['Invalid details submitted'], className='text-danger')])
            ], md=4),

            dbc.Col([
                dbc.Label('Email: '),
                dcc.Input(
                    id='newEmail',
                    className='form-control',
                    n_submit=0,
                    style={
                        'width' : '90%'
                    },
                ),

            ], md=4)

        ]),
    ], className='jumbotron'),

    dbc.Container([
        html.H3('View Users'),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dash_table.DataTable(
                    id='users',
                    columns = [{'name' : 'Username', 'id' : 'username'},
                                {'name' : 'Firstname', 'id' : 'firstname'},
                                {'name' : 'Lastname', 'id' : 'lastname'},
                                {'name' : 'Institute', 'id' : 'institute'},
                                {'name' : 'Email', 'id' : 'email'},
                                {'name' : 'Admin', 'id' : 'admin'}],
                    data=show_users(),
                ),
            ], md=12),
        ]),
    ], className='jumbotron')
])

################################################################################
# CREATE USER BUTTON CLICK / FORM SUBMIT - VALIDATE USERNAME
################################################################################
@callback(Output('newUsername', 'className'),

              [Input('createUserButton', 'n_clicks'),
              Input('newUsername', 'n_submit'),
              Input('newPwd1', 'n_submit'),
              Input('newPwd2', 'n_submit'),
              Input('newEmail', 'n_submit')],

              [State('newUsername', 'value')])

def validateUsername(n_clicks, usernameSubmit, newPassword1Submit,
    newPassword2Submit, newEmailSubmit, newUsername):

    logger.info(f'validate username {n_clicks}')
    
    if (n_clicks > 0) or (usernameSubmit > 0) or (newPassword1Submit > 0) or \
        (newPassword2Submit > 0) or (newEmailSubmit > 0):

        if newUsername == None or newUsername == '':
            return 'form-control is-invalid'
        else:
            return 'form-control is-valid'
    else:
        return 'form-control'



################################################################################
# CREATE USER BUTTON CLICK / FORM SUBMIT - RED BOX IF PASSWORD DOES NOT MATCH
################################################################################
@callback(Output('newPwd1', 'className'),

              [Input('createUserButton', 'n_clicks'),
              Input('newUsername', 'n_submit'),
              Input('newPwd1', 'n_submit'),
              Input('newPwd2', 'n_submit'),
              Input('newEmail', 'n_submit')],

              [State('newPwd1', 'value'),
              State('newPwd2', 'value')])

def validatePassword1(n_clicks, usernameSubmit, newPassword1Submit,
    newPassword2Submit, newEmailSubmit, newPassword1, newPassword2):

    logger.info(f'validate pwd 1 {n_clicks}')
    
    if (n_clicks > 0) or (usernameSubmit > 0) or (newPassword1Submit > 0) or \
        (newPassword2Submit > 0) or (newEmailSubmit > 0):

        if newPassword1 == newPassword2 and len(newPassword1) > 7:
            return 'form-control is-valid'
        else:
            return 'form-control is-invalid'
    else:
        return 'form-control'


################################################################################
# CREATE USER BUTTON CLICK / FORM SUBMIT - RED BOX IF PASSWORD DOES NOT MATCH
################################################################################
@callback(Output('newPwd2', 'className'),

              [Input('createUserButton', 'n_clicks'),
              Input('newUsername', 'n_submit'),
              Input('newPwd1', 'n_submit'),
              Input('newPwd2', 'n_submit'),
              Input('newEmail', 'n_submit')],

              [State('newPwd1', 'value'),
              State('newPwd2', 'value')])

def validatePassword2(n_clicks, usernameSubmit, newPassword1Submit,
    newPassword2Submit, newEmailSubmit, newPassword1, newPassword2):

    logger.info(f'validate pwd 2 {n_clicks}')
    
    if (n_clicks > 0) or (usernameSubmit > 0) or (newPassword1Submit > 0) or \
        (newPassword2Submit > 0) or (newEmailSubmit > 0):

        if newPassword1 == newPassword2 and len(newPassword2) > 7:
            return 'form-control is-valid'
        else:
            return 'form-control is-invalid'
    else:
        return 'form-control'



################################################################################
# CREATE USER BUTTON CLICK / FORM SUBMIT - VALIDATE EMAIL
################################################################################
@callback(Output('newEmail', 'className'),

              [Input('createUserButton', 'n_clicks'),
              Input('newUsername', 'n_submit'),
              Input('newPwd1', 'n_submit'),
              Input('newPwd2', 'n_submit'),
              Input('newEmail', 'n_submit')],

              [State('newEmail', 'value')])

def validateEmail(n_clicks, usernameSubmit, newPassword1Submit,
    newPassword2Submit, newEmailSubmit, newEmail):

    logger.info(f'validate email {n_clicks}')
    
    if (n_clicks > 0) or (usernameSubmit > 0) or (newPassword1Submit > 0) or \
        (newPassword2Submit > 0) or (newEmailSubmit > 0):

        if newEmail == None or newEmail == '':
            return 'form-control is-invalid'
        else:
            return 'form-control is-valid'
    else:
        return 'form-control'




################################################################################
# CREATE USER BUTTON CLICKED / ENTER PRESSED - UPDATE DATABASE WITH NEW USER
################################################################################
@callback(Output('createUserSuccess', 'children'),

              [Input('createUserButton', 'n_clicks')],

              [State('newUsername', 'value'),
               State('newFirstname', 'value'),
               State('newLastname', 'value'),
               State('newInstitute', 'value'),
               State('newEmail', 'value'),
               State('admin', 'value'),
               State('newPwd1', 'value'),
               State('newPwd2', 'value')])

def createUser(n_clicks, username, firstname, lastname, institute, email, admin, pwd1, pwd2):
    
    logger.info(f'create user {username} {firstname} {lastname} {institute}')
    
    if (username is not None) and (firstname is not None) and (lastname is not None) and (institute is not None) and (email is not None):
        add_user(username, firstname, lastname, institute, pwd1, email, admin)
        return html.Div(children=['added user'], className='text-success')
    else:
        return html.Div(children=['adding user failed'], className='text-danger')
    
################################################################################
# CREATE USER BUTTON CLICKED / ENTER PRESSED - UPDATE DATABASE WITH NEW USER
################################################################################
@callback(Output('users', 'data'),
         [Input('createUserButton', 'n_clicks')])
def updateTable(n_clicks):
    logger.info(f'update_table {n_clicks}')
    return show_users()
    
    #
    #if (n_clicks > 0) or (usernameSubmit > 0) or (newPassword1Submit > 0) or \
    #    (newPassword2Submit > 0) or (newEmailSubmit > 0):#
    #
#
#        if newUser and newPassword1 and newPassword2 and newEmail != '':
#            if newPassword1 == newPassword2:
#                if len(newPassword1) > 7:
#                    try:
#                        add_user(newUser, newPassword1, newEmail, admin)
#                        return html.Div(children=['New User created'], className='text-success')
#                    except Exception as e:
#                        return html.Div(children=['New User not created: {e}'.format(e=e)], className='text-danger')
 #               else:
 #                   return html.Div(children=['New Password Must Be Minimum 8 Characters'], className='text-danger')
 #           else:
 #               return html.Div(children=['Passwords do not match'], className='text-danger')
 #       else:
 #           return html.Div(children=['Invalid details submitted'], className='text-danger')

'''
################################################################################
# CREATE USER BUTTON CLICK / FORM SUBMIT - VALIDATE USERNAME
################################################################################
@callback(Output('newUsername', 'className'),
          Input('createUserButton', 'n_clicks'),
          Input('newUsername', 'n_submit'),
          Input('newFirstname', 'n_submit'),
          Input('newLastname', 'n_submit'),
          Input('newInstitute', 'n_submit'),
          Input('newPwd1', 'n_submit'),
          Input('newPwd2', 'n_submit'),
          Input('newEmail', 'n_submit'),
          State('newUsername', 'value'),
          State('newFirstname', 'value'),
          State('newLastname', 'value'),
          State('newInstitute', 'value'))
def validate_username(n_clicks, usernameSubmit, firstnameSubmit, lastnameSubmit, instituteSubmit, newPassword1Submit,
    newPassword2Submit, newEmailSubmit, newUsername, newFirstname, newLastname, newInstitute):

    if (n_clicks > 0) or (usernameSubmit > 0) or (firstnameSubmit > 0) or \
        (lastnameSubmit > 0)or (instituteSubmit > 0) or (newPassword1Submit > 0) or \
        (newPassword2Submit > 0) or (newEmailSubmit > 0):

        if newUsername == None or newUsername == '':
            return 'form-control is-invalid'
        else:
            return 'form-control is-valid'
    else:
        return 'form-control'
    
    
################################################################################
# CREATE USER BUTTON CLICK / FORM SUBMIT - VALIDATE FIRSTNAME
################################################################################
@callback(Output('newUsername', 'className'),
          Input('createUserButton', 'n_clicks'),
          Input('newUsername', 'n_submit'),
          Input('newFirstname', 'n_submit'),
          Input('newLastname', 'n_submit'),
          Input('newInstitute', 'n_submit'),
          Input('newPwd1', 'n_submit'),
          Input('newPwd2', 'n_submit'),
          Input('newEmail', 'n_submit'),
          State('newUsername', 'value'),
          State('newFirstname', 'value'),
          State('newLastname', 'value'),
          State('newInstitute', 'value'))
def validate_firstname(n_clicks, usernameSubmit, firstnameSubmit, lastnameSubmit, instituteSubmit, newPassword1Submit,
    newPassword2Submit, newEmailSubmit, newUsername, newFirstname, newLastname, newInstitute):

    if (n_clicks > 0) or (usernameSubmit > 0) or (firstnameSubmit > 0) or \
        (lastnameSubmit > 0) or (instituteSubmit > 0) or (newPassword1Submit > 0) or \
        (newPassword2Submit > 0) or (newEmailSubmit > 0):

        if newFirstname == None or newFirstname == '':
            return 'form-control is-invalid'
        else:
            return 'form-control is-valid'
    else:
        return 'form-control'
    

################################################################################
# CREATE USER BUTTON CLICK / FORM SUBMIT - VALIDATE LASTNAME
################################################################################
@callback(Output('newUsername', 'className'),
          Input('createUserButton', 'n_clicks'),
          Input('newUsername', 'n_submit'),
          Input('newFirstname', 'n_submit'),
          Input('newLastname', 'n_submit'),
          Input('newInstitute', 'n_submit'),
          Input('newPwd1', 'n_submit'),
          Input('newPwd2', 'n_submit'),
          Input('newEmail', 'n_submit'),
          State('newUsername', 'value'),
          State('newFirstname', 'value'),
          State('newLastname', 'value'),
          State('newInstitute', 'value'))
def validate_lastname(n_clicks, usernameSubmit, firstnameSubmit, lastnameSubmit, instituteSubmit, newPassword1Submit,
    newPassword2Submit, newEmailSubmit, newUsername, newFirstname, newLastname, newInstitute):

    if (n_clicks > 0) or (usernameSubmit > 0) or (firstnameSubmit > 0) or \
        (lastnameSubmit > 0) or (instituteSubmit > 0) or (newPassword1Submit > 0) or \
        (newPassword2Submit > 0) or (newEmailSubmit > 0):

        if newLastname == None or newLastname == '':
            return 'form-control is-invalid'
        else:
            return 'form-control is-valid'
    else:
        return 'form-control'
    
################################################################################
# CREATE USER BUTTON CLICK / FORM SUBMIT - VALIDATE INSTITUTE
################################################################################
@callback(Output('newUsername', 'className'),
          Input('createUserButton', 'n_clicks'),
          Input('newUsername', 'n_submit'),
          Input('newFirstname', 'n_submit'),
          Input('newLastname', 'n_submit'),
          Input('newInstitute', 'n_submit'),
          Input('newPwd1', 'n_submit'),
          Input('newPwd2', 'n_submit'),
          Input('newEmail', 'n_submit'),
          State('newUsername', 'value'),
          State('newFirstname', 'value'),
          State('newLastname', 'value'),
          State('newInstitute', 'value'))
def validate_institute(n_clicks, usernameSubmit, firstnameSubmit, lastnameSubmit, instituteSubmit, newPassword1Submit,
    newPassword2Submit, newEmailSubmit, newUsername, newFirstname, newLastname, newInstitute):

    if (n_clicks > 0) or (usernameSubmit > 0) or (firstnameSubmit > 0) or \
        (lastnameSubmit > 0) or (instituteSubmit > 0) or (newPassword1Submit > 0) or \
        (newPassword2Submit > 0) or (newEmailSubmit > 0):

        if newInstitute == None or newInstitute == '':
            return 'form-control is-invalid'
        else:
            return 'form-control is-valid'
    else:
        return 'form-control'



################################################################################
# CREATE USER BUTTON CLICK / FORM SUBMIT - RED BOX IF PASSWORD DOES NOT MATCH
################################################################################
@callback(Output('newPwd1', 'className'),
          Input('createUserButton', 'n_clicks'),
          Input('newUsername', 'n_submit'),
          Input('newPwd1', 'n_submit'),
          Input('newPwd2', 'n_submit'),
          Input('newEmail', 'n_submit'),
          State('newPwd1', 'value'),
          State('newPwd2', 'value'))
def validate_password1(n_clicks, usernameSubmit, newPassword1Submit,
    newPassword2Submit, newEmailSubmit, newPassword1, newPassword2):

    if (n_clicks > 0) or (usernameSubmit > 0) or (newPassword1Submit > 0) or \
        (newPassword2Submit > 0) or (newEmailSubmit > 0):

        if newPassword1 == newPassword2 and len(newPassword1) > 7:
            return 'form-control is-valid'
        else:
            return 'form-control is-invalid'
    else:
        return 'form-control'


################################################################################
# CREATE USER BUTTON CLICK / FORM SUBMIT - RED BOX IF PASSWORD DOES NOT MATCH
################################################################################
@callback(Output('newPwd2', 'className'),
          Input('createUserButton', 'n_clicks'),
          Input('newUsername', 'n_submit'),
          Input('newPwd1', 'n_submit'),
          Input('newPwd2', 'n_submit'),
          Input('newEmail', 'n_submit'),
          State('newPwd1', 'value'),
          State('newPwd2', 'value'))
def validate_password2(n_clicks, usernameSubmit, newPassword1Submit,
    newPassword2Submit, newEmailSubmit, newPassword1, newPassword2):

    if (n_clicks > 0) or (usernameSubmit > 0) or (newPassword1Submit > 0) or \
        (newPassword2Submit > 0) or (newEmailSubmit > 0):

        if newPassword1 == newPassword2 and len(newPassword2) > 7:
            return 'form-control is-valid'
        else:
            return 'form-control is-invalid'
    else:
        return 'form-control'



################################################################################
# CREATE USER BUTTON CLICK / FORM SUBMIT - VALIDATE EMAIL
################################################################################
@callback(Output('newEmail', 'className'),

              [Input('createUserButton', 'n_clicks'),
              Input('newUsername', 'n_submit'),
              Input('newPwd1', 'n_submit'),
              Input('newPwd2', 'n_submit'),
              Input('newEmail', 'n_submit')],

              [State('newEmail', 'value')])

def validate_email(n_clicks, usernameSubmit, newPassword1Submit,
    newPassword2Submit, newEmailSubmit, newEmail):

    logger.info(f'validate email')
    
    if (n_clicks > 0) or (usernameSubmit > 0) or (newPassword1Submit > 0) or \
        (newPassword2Submit > 0) or (newEmailSubmit > 0):

        if newEmail == None or newEmail == '':
            return 'form-control is-invalid'
        else:
            return 'form-control is-valid'
    else:
        return 'form-control'





################################################################################
# CREATE USER BUTTON CLICKED / ENTER PRESSED - UPDATE DATABASE WITH NEW USER
################################################################################
@callback(Output('createUserSuccess', 'children'),
          Input('createUserButton', 'n_clicks'),
          Input('newUsername', 'n_submit'),
          Input('newFirstname', 'n_submit'),
          Input('newLastname', 'n_submit'),
          Input('newInstitute', 'n_submit'),
          Input('newPwd1', 'n_submit'),
          Input('newPwd2', 'n_submit'),
          Input('newEmail', 'n_submit'),
          State('pageContent', 'children'),
          State('newUsername', 'value'),
          State('newFirstname', 'value'),
          State('newLastname', 'value'),
          State('newInstitute', 'value'),
          State('newPwd1', 'value'),
          State('newPwd2', 'value'),
          State('newEmail', 'value'),
          State('admin', 'value'))
def create_user(n_clicks, usernameSubmit, firstnameSubmit, lastnameSubmit, instituteSubmit, newPassword1Submit, newPassword2Submit,
            newEmailSubmit, pageContent, newUser, newFirst, newLast, newInstitute, newPassword1, newPassword2, newEmail, admin):
    
    logger.info(f'create user')
    
    if (n_clicks > 0) or (usernameSubmit > 0) or (firstnameSubmit > 0) or \
        (lastnameSubmit > 0) or (instituteSubmit > 0) or (newPassword1Submit > 0) or \
        (newPassword2Submit > 0) or (newEmailSubmit > 0):
            
        logger.info(f'create user 2')
        
        if newUser and newFirst and newLast and newInstitute and newPassword1 and newPassword2 and newEmail != '':
            if newPassword1 == newPassword2:
                if len(newPassword1) > 7:
                    try:
                        add_user(newUser, newFirst, newLast, newInstitute, newPassword1, newEmail, admin)
                        return html.Div(children=['New User created'], className='text-success')
                    except Exception as e:
                        return html.Div(children=['New User not created: {e}'.format(e=e)], className='text-danger')
                else:
                    return html.Div(children=['New Password Must Be Minimum 8 Characters'], className='text-danger')
            else:
                return html.Div(children=['Passwords do not match'], className='text-danger')
        else:
            return html.Div(children=['Invalid details submitted'], className='text-danger')
'''
