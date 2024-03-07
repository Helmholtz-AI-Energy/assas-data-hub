import dash
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import os
import base64
import logging
import dash_uploader as du
import uuid

from dash import html, dcc, Input, Output, callback, State
from urllib.parse import quote as urlquote
from flask import Flask, send_from_directory
from collections import OrderedDict
from pathlib import Path

from ..components import content_style
from assasdb import AssasDatabaseManager

from flask import current_app as app

logger = logging.getLogger('assas_app')

logger.debug('initialize %s', __name__)

dash.register_page(__name__, path="/upload")

UPLOAD_FOLDER_ROOT = r'/home/jonas/upload'

if not os.path.exists(UPLOAD_FOLDER_ROOT):
    os.makedirs(UPLOAD_FOLDER_ROOT)
    
du.configure_upload(dash.get_app(), UPLOAD_FOLDER_ROOT)

def get_upload_component(id):
    return du.Upload(
        id=id,
        max_file_size=10000,  # 1800 Mb
        filetypes=['csv', 'zip'],
        upload_id=uuid.uuid1(),  # Unique session id
    )

layout = html.Div([
    html.H2('ASSAS Database - Upload ASSAS Training Dataset'),
    dbc.Alert("Upload interface for ASTEC binary archives", color="primary", style={'textAlign': 'center'}),
    html.H3('General meta data'),
    dbc.InputGroup(
            [dbc.InputGroupText("Name"), dbc.Input(placeholder="Name")],
            className="mb-3",
    ),
    dbc.InputGroup(
            [dbc.InputGroupText("Group"), dbc.Input(placeholder="Group")],
            className="mb-3",
    ),
    dbc.InputGroup(
            [dbc.InputGroupText("Date"), dbc.Input(placeholder="Date")],
            className="mb-3",
    ),
    dbc.InputGroup(
            [dbc.InputGroupText("Creator"), dbc.Input(placeholder="Creator")],
            className="mb-3",
    ),  
    dbc.InputGroup(
            [
                dbc.InputGroupText("Description"),
                dbc.Textarea(),
            ],
            className="mb-3",
    ),
    html.H3('Conversion schema'),
    dbc.InputGroup(
            [
                dbc.InputGroupText("Schema"),
                dbc.Select(
                    options=[
                        {"label": "Option 1", "value": 1},
                        {"label": "Option 2", "value": 2},
                    ]
                )                
            ]
    ),
    html.Hr(),
    html.H3('Archive files'),
    html.Hr(),
    get_upload_component('upload_data'),
    html.Hr(),
    dbc.Button(
            "Upload to LSDF", 
            id="upload_archive", 
            className="me-2", 
            n_clicks=0, 
            disabled=True,
        ),
    html.Hr(),
    dcc.Interval(id="progress-interval", n_intervals=0, interval=500),
    dbc.Progress(id="progress"),
    html.Hr(),
    html.H3("Report"),
    html.Ul(id="file-list")
], style = content_style())

@du.callback(
    output=Output("callback-output", "children"),
    id="dash-uploader",
)
def callback_on_completion(status: du.UploadStatus):
    return html.Ul([html.Li(str(x)) for x in status.uploaded_files])