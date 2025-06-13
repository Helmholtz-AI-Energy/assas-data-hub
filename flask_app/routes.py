'''Routes for parent Flask app.'''
import logging
import uuid
import numpy as np
import shutil

from urllib.parse import urlencode
from flask import redirect, render_template, send_file, request, jsonify
from flask import current_app as app
from pathlib import Path

from assasdb import AssasDatabaseManager

TMP_FOLDER = '/root/tmp'

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
    
    manager = AssasDatabaseManager()
    document = manager.get_database_entry_by_uuid(system_uuid)
    filepath = document['system_result']
    file = Path(filepath)
    
    if file.exists():
    
        logger.info(f'Handle request of {str(file)}.')
    
        return send_file(
            path_or_file = filepath,
            download_name = f'dataset_{system_uuid}.h5',
            as_attachment = True,
        )

@app.route('/assas_app/hdf5_download', methods=['GET'])
def get_download_archive():
    
    args = request.args
    system_uuid = args.get('uuid', type=str)
    
    temp_folder = f'{TMP_FOLDER}/download_{system_uuid}'
    filepath = f'{temp_folder}/download_{system_uuid}.zip'
    file = Path(filepath)
    
    if file.exists():
    
        logger.info(f'Handle request of {str(file)}.')
    
        response = send_file(
            path_or_file = filepath,
            download_name = f'download_{system_uuid}.zip',
            as_attachment = True,
        )
        
        return response
 
    else:
        
        logger.error(f'File not found: {filepath}.')
        return "File not found", 404

@app.route('/assas_app/query_data', methods=['GET'])
def query_data():
    
    args = request.args
    logger.info(f'Received request with arguments: {args}')

    system_uuid = uuid.UUID(args.get('uuid', type=str))
    
    variable = args.get('variable', type=str)
    tstart = args.get('tstart', type=int)
    tend = args.get('tend', type=int)
   
    logger.info(f'{system_uuid} {variable} {tstart} {tend}')
    
    manager = AssasDatabaseManager()
    document = manager.get_database_entry_by_uuid(system_uuid)
    filepath = document['system_result']
    
    logger.info(f'Handle request of {filepath}')
    #array = AssasHdf5DatasetHandler.get_variable_data_from_hdf5(filepath, variable)
    array = np.zeros((1,2))
    
    return jsonify({'data_shape': np.shape(array), 'data': array.tolist()})

@app.route('/index')
def index():
    return render_template('index_login.html')
