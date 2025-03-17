import dash
import dash_bootstrap_components as dbc
import pandas
import numpy as np
import os
import logging
import dash_uploader as du
import uuid
import json
import diskcache
import time

from dash.long_callback import DiskcacheLongCallbackManager
from dash.dependencies import Input, Output

from dash import html, dcc, Input, Output, callback, State, DiskcacheManager
from urllib.parse import quote as urlquote
from flask import Flask, send_from_directory
from collections import OrderedDict
from pathlib import Path
from datetime import datetime

from flask import current_app as flask_app

from ..components import content_style
from assasdb import AssasDatabaseManager, AssasDatabaseHandler, AssasDocumentFile, AssasDocumentFileStatus

app = dash.get_app()

logger = logging.getLogger('assas_app')

logger.debug(f'initialize {__name__}')

dash.register_page(__name__, path='/upload')

UPLOAD_FOLDER_ROOT = flask_app.config.get('LOCAL_ARCHIVE')

logger.debug(f'initialize {__name__}, upload folder {UPLOAD_FOLDER_ROOT}')

if not os.path.exists(UPLOAD_FOLDER_ROOT):
    os.makedirs(UPLOAD_FOLDER_ROOT)
    
du.configure_upload(app, UPLOAD_FOLDER_ROOT)

def get_upload_component(id):
    return du.Upload(
        id=id,
        max_file_size=10000,  # 1800 Mb
        filetypes=['csv', 'zip'],
        upload_id=uuid.uuid4(),  # Unique session id
        cancel_button=True,
        pause_button=True,
        disabled=True,                        
    )

layout = html.Div([
    html.H2('ASSAS Database - Upload ASSAS Training Dataset'),
    dbc.Alert('Upload interface for ASTEC binary archives', color='primary', style={'textAlign': 'center'}),
    html.H3('General meta data'),
    dbc.InputGroup(
            [dbc.InputGroupText('Name'), dbc.Input(id='input_name', placeholder='Enter Name', invalid=True, type='text')],
            className='mb-3',
    ),
    dbc.InputGroup(
            [dbc.InputGroupText('Group'), dbc.Input(id='input_group', placeholder='Enter Group', invalid=True, type='text')],
            className='mb-3',
    ),
    dbc.InputGroup(
            [dbc.InputGroupText('Date'), dbc.Input(id='input_date', placeholder='Enter Date', invalid=True, type='date')],
            className='mb-3',
    ),
    dbc.InputGroup(
            [dbc.InputGroupText('Creator'), dbc.Input(id='input_creator', placeholder='Enter Creator', invalid=True, type='text')],
            className='mb-3',
    ),  
    dbc.InputGroup(
            [
                dbc.InputGroupText('Description'),
                dbc.Textarea(id='input_description', placeholder='Description', invalid=True),
            ],
            className='mb-3',
    ),
    dcc.Store(id='intermediate-meta'),
    html.H3('Conversion schema'),
    dbc.InputGroup(
            [
                dbc.InputGroupText('Schema'),
                dbc.Select(
                    options=[
                        {'label': 'hdf5_full', 'value': 1},
                        {'label': 'hdf5_custom', 'value': 2},
                    ]
                )                
            ]
    ),
    html.Hr(),
    html.H3('Upload ASTEC archive'),
    html.Hr(),
    html.Div(
                [
                    html.H4('1. Upload archive to app'),
                    get_upload_component(id='dash-uploader'),
                    html.Div(id='callback-output', children='no data'),
                    html.H4('2. Store archive in LSDF'),
                    dbc.Button('Upload to LSDF', id='button', disabled=True, n_clicks=0, size='lg'),
                    dbc.Button('Cancel Upload', id='cancel_button', disabled=True, n_clicks=0, size='lg', style={'margin-left': '4rem'}),                    
                    dcc.Store(id='intermediate-system')
                ],
                style={  # wrapper div style
                    'textAlign': 'center',
                    'width': '1000px',
                    'margin-top': '1rem',
                    'margin-bottom': '1rem',
                    'margin-left': '1rem',
                    'margin-right': '2rem',
                    'padding': '2rem 1rem',
                },
            ),
    #html.Hr(),
    #html.H3('Upload to LSDF'),
    #dbc.Button(
    #        'Upload to LSDF', 
    #        id='upload-button', 
    #        className='me-2', 
    #        n_clicks=0, 
    #        disabled=True,
    #    ),
    html.Hr(),    
    #dcc.Interval(id='progress-interval', n_intervals=0, interval=500),
    dbc.Progress(id='progress', value=0, striped=True),
    html.Hr(),
    html.H3('Report'),
    html.Div(
        className='status',
        children=[
            html.Ul(id='status-list')
        ],
    )    
], style = content_style())

def string_validation(text: str):
    
    invalid = True
    
    if text is not None and len(text) > 0:
        invalid = False  
    
    return invalid

@callback(     
     Output('input_name', 'invalid'),
     Output('input_name', 'valid'),
     State('intermediate-meta', 'data'),
     Input("input_name", "value"),
)
def input_validator_name_callback(data, name):
    
    invalid = string_validation(name)     
    
    return invalid, (not invalid)

@callback(     
     Output('input_group', 'invalid'),
     Output('input_group', 'valid'),
     State('intermediate-meta', 'data'),
     Input("input_group", "value"),
)
def input_validator_group_callback(data, group):
    
    invalid = string_validation(group)     
    
    return invalid, (not invalid)

@callback(     
     Output('input_date', 'invalid'),
     Output('input_date', 'valid'),
     State('intermediate-meta', 'data'),
     Input("input_date", "value"),
)
def input_validator_date_callback(data, date):
    
    invalid = string_validation(date)     
    
    return invalid, (not invalid)

@callback(     
     Output('input_creator', 'invalid'),
     Output('input_creator', 'valid'),
     State('intermediate-meta', 'data'),
     Input("input_creator", "value"),
)
def input_validator_creator_callback(data, creator):
    
    invalid = string_validation(creator)     
    
    return invalid, (not invalid)

@callback(     
     Output('input_description', 'invalid'),
     Output('input_description', 'valid'),
     State('intermediate-meta', 'data'),
     Input("input_description", "value"),
)
def input_validator_description_callback(data, description):
    
    invalid = string_validation(description)     
    
    return invalid, (not invalid)

@callback(
     Output('intermediate-meta', 'data'),
     Output('dash-uploader', 'disabled'),
     State('intermediate-meta', 'data'),
     Input("input_name", "value"), 
     Input("input_group", "value"), 
     Input("input_date", "value"), 
     Input("input_creator", "value"), 
     Input("input_description", "value"))
def meta_collector_callback(meta, name, group, date, creator, description):
  
    document = AssasDocumentFile()
    if meta is not None:
        document.set_document(json.loads(meta))
    
    if (not string_validation(name)):
        document.set_value('meta_name', name)  
    else:
        document.delete_key('meta_name')
            
    if (not string_validation(group)):
        document.set_value('meta_group', group)  
    else:
        document.delete_key('meta_group')
            
    if (not string_validation(date)):
        document.set_value('meta_date', date)  
    else:
        document.delete_key('meta_date')
            
    if (not string_validation(creator)):
        document.set_value('meta_creator', creator)  
    else:
        document.delete_key('meta_creator')
            
    if (not string_validation(description)):
        document.set_value('meta_description', description)  
    else:
        document.delete_key('meta_description')
            
    if len(document.get_document()) == len(dash.callback_context.inputs_list):
        disable_upload = False
    else: 
        disable_upload = True
        
    logger.debug(f'updated document ({document.get_document()}, {len(document.get_document())}, {disable_upload})')
    
    return json.dumps(document.get_document()), disable_upload

@du.callback(
    output=[
        Output('callback-output', 'children'),
        Output('intermediate-system', 'data'),
        Output('button', 'disabled'),        
    ],
    id='dash-uploader',
)
def callback_on_completion(status: du.UploadStatus):
    
    files = html.Ul([html.Li(str(x)) for x in status.uploaded_files])
    
    document = AssasDocumentFile()    
    document.set_system_values(
        status.upload_id,
        datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
        str(status.uploaded_files[0]),
        ('%.2f' % status.total_size_mb) + ' MB',
        'test user',
        'Download',
        AssasDocumentFileStatus.UPLOADED
    )
    
    logger.debug(f'uploaded file with id {status.upload_id} {status.uploaded_files} {document.get_document()}')
    
    return files, json.dumps(document.get_document()), False

@app.long_callback(
    output=Output('status-list', 'children'),
    inputs=[Input('button', 'n_clicks'),State('intermediate-system', 'data'),State('intermediate-meta', 'data')],
    running=[
        (Output('button', 'disabled'), True, False),
        (Output('cancel_button', 'disabled'), False, True),
        (
            Output('status-list', 'style'),
            {'visibility': 'hidden'},
            {'visibility': 'visible'},
        ),
        (
            Output('progress', 'style'),
            {'visibility': 'visible'},
            {'visibility': 'hidden'},
        ),
    ],
    cancel=Input('cancel_button', 'n_clicks'),
    progress=[Output('progress', 'value'), Output('progress', 'max')],
    prevent_initial_call=True
)
def update_progress(set_progress, n_clicks, system, meta):
    
    result_list = []
    result_list.append(f'started upload process')
    
    set_progress((str(1), str(5)))
    
    manager = AssasDatabaseManager()
    
    #document = AssasDocumentFile()
    #document.set_document(json.loads(system))
    #document.extend_document(json.loads(meta))
        
    #uuid = document.get_value('system_uuid')
    #full_path = document.get_value('system_path')
    #path = manager.storage_handler.get_dataset_archive_dir(uuid)
    #document.set_value('system_path', path)
    
    #saved_document = manager.get_database_entry_uuid(uuid)
  
    #logger.debug(f'number of clicks {n_clicks}, intermediate document: {document.get_document()}, saved document: {saved_document}')
    
    #if saved_document is None:
        
    #    result = f'1. added new archive (uuid {uuid}, path {path})'
    #    result_list.append(result)
    #    logger.info(result)

    #    set_progress((str(2), str(5)))
        
    #    if manager.process_archive(full_path):
            
    #        result = f'2. processed archive (uuid {uuid}, path {path})'
    #        result_list.append(result)
    #        logger.info(result)
            
    #        set_progress((str(3), str(5)))
                        
    #        if manager.synchronize_archive(document.get_value('system_uuid')):
                
    #            set_progress((str(4), str(5)))
                
    #            result = f'3. synchronized archive on LSDF (uuid {uuid}, path {path})'
    #            result_list.append(result)
    #            logger.info(result)

    #            document.set_value('system_status', AssasDocumentFileStatus.ARCHIVED)
    #            document = AssasHdf5DatasetHandler.update_meta_data(document)
    #            manager.add_database_entry(document.get_document())
                
    #            result = f'4. added database entry (uuid {uuid}, path {path})'
    #            result_list.append(result)
            
    #        else:
                                
    #            result = f'3. ERROR when synchronizing archive on LSDF (uuid {uuid}, path {path})'
    #            result_list.append(result)
    #            logger.critical(result)
            
    #    else:
            
    #         result = f'2. ERROR when processing archive (uuid {uuid}, path {path})'
    #        result_list.append(result)
    #        logger.critical(result)
    #        
    #        if manager.clear_archive(uuid):
    #        
    #            result = f'3. cleared local archive (uuid {uuid}, path {path})'
    #            result_list.append(result)
    #            logger.critical(result)
            
    #else:
    #    
    #    result = f'1. archive already processed (uuid {uuid}, path {path})'
    #    result_list.append(result)  
            
    #set_progress((str(5), str(5)))
    
    return html.Ul([html.Li(str(result)) for result in result_list])