'''Routes for parent Flask app.'''
import datetime
import logging
import time
import uuid
import threading

from flask import redirect, render_template, send_file, current_app, jsonify, Flask, request, abort
from flask import current_app as app
from werkzeug.exceptions import HTTPException, InternalServerError
from functools import wraps

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
    print(f'Uuid {uuid}')
    document = manager.get_database_entry_by_uuid(uuid)
    filepath = document['result_path']
    
    logger.info(f'Handle request of {filepath}')
    
    return send_file(filepath)


thread_event = threading.Event()

def backgroundTask():
    
    while thread_event.is_set():
        
        print('Background task running!')
        manager = AssasDatabaseManager(app.config)
        #manager.process_uploads()
        manager.convert_archives_to_hdf5()
        

@app.route("/assas_app/conversion_start", methods=["POST"])
def startBackgroundTask():
    try:
        thread_event.set()
        
        thread = threading.Thread(target=backgroundTask)
        thread.start()

        return "Background task started!"
    except Exception as error:
        return str(error)
    
@app.route("/assas_app/conversion_stop", methods=["POST"])
def stopBackgroundTask():
    try:
        thread_event.clear()

        return "Background task stopped!"
    except Exception as error:
        return str(error)
