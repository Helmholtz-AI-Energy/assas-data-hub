'''Routes for parent Flask app.'''
import datetime

from flask import redirect, render_template, send_file
from flask import current_app as app

from assasdb import AssasDatabaseManager

@app.route('/')
def from_root_to_home():
    
    return redirect('/assas_app/home')

@app.route('/assas_app')
def from_app_to_home():
    
    return redirect('/assas_app/home')

@app.route('/assas_app/files/<uuid>', methods=['GET'])
def get_data_files(uuid):
    
    manager = AssasDatabaseManager(
        app.config.get('LOCAL_ARCHIVE'), 
        app.config.get('LSDF_ARCHIVE'))
    
    document = manager.get_database_entry_uuid(uuid)
    filepath = document['system_path'] + '/dataset.h5'
    
    return send_file(filepath)
