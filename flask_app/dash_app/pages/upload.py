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

from flask import current_app as flask_app

from ..components import content_style
from assasdb import AssasDatabaseManager, AssasDatabaseHandler

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
    )

layout = html.Div([
    html.H2('ASSAS Database - Upload ASSAS Training Dataset'),
    dbc.Alert('Upload interface for ASTEC binary archives', color='primary', style={'textAlign': 'center'}),
    html.H3('General meta data'),
    dbc.InputGroup(
            [dbc.InputGroupText('Name'), dbc.Input(id='input_name', placeholder='Name')],
            className='mb-3',
    ),
    dbc.InputGroup(
            [dbc.InputGroupText('Group'), dbc.Input(id='input_group', placeholder='Group')],
            className='mb-3',
    ),
    dbc.InputGroup(
            [dbc.InputGroupText('Date'), dbc.Input(id='input_date', placeholder='Date')],
            className='mb-3',
    ),
    dbc.InputGroup(
            [dbc.InputGroupText('Creator'), dbc.Input(id='input_creator', placeholder='Creator')],
            className='mb-3',
    ),  
    dbc.InputGroup(
            [
                dbc.InputGroupText('Description'),
                dbc.Textarea(id='input description', placeholder=''),
            ],
            className='mb-3',
    ),
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
                    get_upload_component(id='dash-uploader'),
                    html.Div(id='callback-output', children='no data'),
                    html.P(id='paragraph', children=['Button not clicked']),
                    dbc.Button('Upload to LSDF', id='button', disabled=True, n_clicks=0),
                    dbc.Button('Test progress', id='button2', disabled=True, n_clicks=0),
                    dbc.Button('Cancel upload', id='cancel_button', disabled=True, n_clicks=0),                    
                    dcc.Store(id='intermediate-value')
                ],
                style={  # wrapper div style
                    'textAlign': 'center',
                    'width': '1000px',
                    'margin-top': '1rem',
                    'margin-bottom': '1rem',
                    'margin-left': '1rem',
                    'margin-right': '1rem',
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
    ),
    html.Ul(id='status-list2')
], style = content_style())

@du.callback(
    output=[
        Output('callback-output', 'children'),
        Output('intermediate-value', 'data'),
        Output('button', 'disabled'),       
        Output('button2', 'disabled'),       
    ],
    id='dash-uploader',
)
def callback_on_completion(status: du.UploadStatus):
    
    files = html.Ul([html.Li(str(x)) for x in status.uploaded_files])
    
    document = AssasDatabaseHandler.get_test_document_file(status.upload_id, str(status.uploaded_files[0]))
    
    logger.info(f'uploaded file with id {status.upload_id} {status.uploaded_files} {document}')
    
    return files, json.dumps(document), False, False

@callback(
    Output('status-list', 'children'),
    Input('button', 'n_clicks'),
    State('intermediate-value', 'data'),
)
def clicked_output(clicks, data):
    
    result_list = ['recognized ASTEC archive', 'converted']
    logger.debug(f'clicked output called {clicks} {data}')
    
    if data is not None:
    
        document = json.loads(data)
    
        logger.debug(f'number of clicks {clicks}, saved document: {document}')
        
        manager = AssasDatabaseManager(flask_app.config.get('LOCAL_ARCHIVE'), flask_app.config.get('LSDF_ARCHIVE'))
        
        #manager.process_archive(document['system_path'])
        #manager.synchronize_archive(document['system_uuid'])
    
    return [html.Li('no ASTEC archive present')]

@app.long_callback(
    output=Output('paragraph', 'children'),
    inputs=[Input('button2', 'n_clicks'),State('intermediate-value', 'data')],
    #state=State('intermediate-value', 'data'),
    #background=True,
    running=[
        (Output('button2', 'disabled'), True, False),
        (Output('cancel_button', 'disabled'), False, True),
        (
            Output('paragraph', 'style'),
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
def update_progress(set_progress, n_clicks, data):
    
    set_progress((str(1), str(5)))
    
    document = json.loads(data)
    
    logger.debug(f'number of clicks {n_clicks}, saved document: {document}')
    
    set_progress((str(2), str(5)))
    
    manager = AssasDatabaseManager(
        flask_app.config.get('LOCAL_ARCHIVE'),
        flask_app.config.get('LSDF_ARCHIVE')
        )
    
    set_progress((str(3), str(5)))
        
    manager.process_archive(document['system_path'])
    
    set_progress((str(4), str(5)))
    
    manager.synchronize_archive(document['system_uuid'])
        
    set_progress((str(5), str(5)))
    
    return f'Update progress complete, started {n_clicks} times'