'''Application entry point.'''
import logging
import os 
import sys

from logging.handlers import RotatingFileHandler
from flask_app import init_app
from dash.dependencies import Input, Output, State
from dash import dcc, callback
from flask_app.users_mgt import create_admin_user, User, AssasUserManager
from flask_login import logout_user, current_user, LoginManager

#logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('assas_app')

logging.basicConfig(
    format = '%(asctime)s %(process)d %(module)s %(levelname)s: %(message)s',
    level = logging.INFO,
    stream = sys.stdout)

handler = RotatingFileHandler('assas_app.log', maxBytes=100000, backupCount=10)
formatter = logging.Formatter('%(asctime)s - %(process)d - %(module)s - %(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

app = init_app()

app.secret_key = 'super secret key'

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = '/index'

create_admin_user()

@login_manager.user_loader
def load_user(username):
    return AssasUserManager().get_user_name(username)

if __name__ == '__main__':

    app.logger.addHandler(handler)
    app.run(host='0.0.0.0', port=5000, debug=True)
