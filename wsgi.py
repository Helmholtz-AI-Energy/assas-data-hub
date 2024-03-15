'''Application entry point.'''
import logging

from logging.handlers import RotatingFileHandler
from flask_app import init_app

from flask_app.users_mgt import create_admin_user, User as base, AssasUserManager
from flask_login import logout_user, current_user, LoginManager, UserMixin

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('assas_app')
handler = RotatingFileHandler('assas_app.log', maxBytes=10000, backupCount=10)
logger.addHandler(handler)

logger = logging.getLogger('assas_app')

app = init_app()

login_manager = LoginManager()
    
#dash_app.index_string = html_layout
login_manager.init_app(app)
login_manager.login_view = '/assas_app/login'

create_admin_user()

@login_manager.user_loader
def load_user(user_id):
    return AssasUserManager().get_user_id(user_id)

if __name__ == '__main__':

    app.logger.addHandler(handler)
    app.run(host='0.0.0.0', debug=True, ssl_context='adhoc')