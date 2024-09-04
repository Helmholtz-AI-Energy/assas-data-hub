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

#thread_event = threading.Event()

#def backgroundTask():
#    while thread_event.is_set():
#        print('Background task running!')
#        sleep(5)

#@app.route("/assas_app/process_uploads")
#@flask_async
#def process_uploads():
    
#    logger.info(f'Handle request for processing uploads')
    
#    manager = AssasDatabaseManager(app.config)
#    manager.process_uploads()
#    manager.convert_archives_to_hdf5()
        
#    return jsonify({'thread_name': 'Conversion', 'Result': True})

#@app.route('/assas_app/process_uploads/<task_id>', methods=['GET'])
#def foo_results(task_id):
#    """
#        Return results of asynchronous task.
#        If this request returns a 202 status code, it means that task hasn't finished yet.
#        """
#    task = tasks.get(task_id)
#    if task is None:
#        abort(404)
#    if 'result' not in task:
#        return {'TaskID': task_id}, 202
#    return task['result']
