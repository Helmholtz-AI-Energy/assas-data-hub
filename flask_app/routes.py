'''Routes for parent Flask app.'''
import datetime
import logging
import time
import uuid
import threading
import secrets
import requests

from urllib.parse import urlencode
from flask import redirect, render_template, send_file, current_app, jsonify, Flask, request, abort, url_for, session, flash
from flask import current_app as app
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from werkzeug.exceptions import HTTPException, InternalServerError
from functools import wraps
from flask_app.users_mgt import create_admin_user, User, AssasUserManager

from assasdb import AssasDatabaseManager

logger = logging.getLogger('assas_app')

@app.route('/')
def from_root_to_home():
    
    return redirect('/assas_app/home')

@app.route('/assas_app')
def from_app_to_home():
    
    return redirect('/assas_app/home')

@app.route('/assas_app/files/<uuid>', methods=['GET'])
def get_data_files(uuid):
    
    manager = AssasDatabaseManager(app.config)
    document = manager.get_database_entry_by_uuid(uuid)
    filepath = document['result_path']
    
    logger.info(f'Handle request of {filepath}')
    
    return send_file(filepath)

@app.route('/index')
def index():
    return render_template('index_login.html')
