'''Application entry point.'''
import logging
import os 

from logging.handlers import RotatingFileHandler
from flask_app import init_app
from dash.dependencies import Input, Output, State
from dash import dcc, callback
from flask_app.users_mgt import create_admin_user, User, AssasUserManager
from flask_login import logout_user, current_user, LoginManager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('assas_app')
handler = RotatingFileHandler('assas_app.log', maxBytes=10000, backupCount=10)
logger.addHandler(handler)

logger = logging.getLogger('assas_app')

app = init_app()

app.secret_key = 'super secret key'
#app.config.update(SECRET_KEY=os.getenv("SECRET_KEY"))

login_manager = LoginManager()
    
#dash_app.index_string = html_layout
login_manager.init_app(app)
login_manager.login_view = '/assas_app/login'

create_admin_user()

@login_manager.user_loader
def load_user(username):
    return AssasUserManager().get_user_name(username)

if __name__ == '__main__':

    app.logger.addHandler(handler)
    app.run(host='0.0.0.0', debug=True, ssl_context='adhoc')