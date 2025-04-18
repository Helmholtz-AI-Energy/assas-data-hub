'''Routes for parent Flask app.'''
import logging
import uuid
import numpy as np

from urllib.parse import urlencode
from flask import redirect, render_template, send_file, request, jsonify
from flask import current_app as app

from assasdb import AssasDatabaseManager

logger = logging.getLogger('assas_app')

@app.route('/')
def from_root_to_home():
    
    return redirect('/assas_app/home')

@app.route('/assas_app')
def from_app_to_home():
    
    return redirect('/assas_app/home')

@app.route('/assas_app/hdf5_file', methods=['GET'])
def get_data_file():
    
    args = request.args
    system_uuid = uuid.UUID(args.get('uuid', type=str))
    
    manager = AssasDatabaseManager(app.config)
    document = manager.get_database_entry_by_uuid(system_uuid)
    filepath = document['system_result']
    
    logger.info(f'Handle request of {filepath}')
    
    return send_file(filepath)

@app.route('/assas_app/query_data', methods=['GET'])
def query_data():
    
    args = request.args    
    logger.info(f'Received request with arguments: {args}')

    system_uuid = uuid.UUID(args.get('uuid', type=str))
    
    variable = args.get('variable', type=str)
    tstart = args.get('tstart', type=int)
    tend = args.get('tend', type=int)
   
    logger.info(f'{system_uuid} {variable} {tstart} {tend}')
    
    manager = AssasDatabaseManager(app.config)
    document = manager.get_database_entry_by_uuid(system_uuid)
    filepath = document['system_result']
    
    logger.info(f'Handle request of {filepath}')
    #array = AssasHdf5DatasetHandler.get_variable_data_from_hdf5(filepath, variable)
    array = np.zeros((1,2))
    
    return jsonify({'data_shape': np.shape(array), 'data': array.tolist()})

@app.route('/index')
def index():
    return render_template('index_login.html')
