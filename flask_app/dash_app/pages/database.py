import os
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import logging
import shutil
import time
import requests

from dash import Dash, dash_table, html, dcc, Input, Output, callback, State, callback_context
from flask import current_app as flask_app
from zipfile import ZipFile
from uuid import uuid4
from pathlib import Path
from typing import List

from assasdb import AssasDatabaseManager
from ..components import content_style, conditional_table_style

logger = logging.getLogger('assas_app')

TMP_FOLDER = '/root/tmp'

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

operators = [['ge ', '>='],
             ['le ', '<='],
             ['lt ', '<'],
             ['gt ', '>'],
             ['ne ', '!='],
             ['eq ', '='],
             ['contains '],
             ['datestartswith ']]

def update_table_data()-> pd.DataFrame:
    ''' 
    Update the table data from the database.
    
    Returns:
        pd.DataFrame: DataFrame with the table data.
    '''
     
    logger.info('Load daqtabase entries to table')
     
    database_manager = AssasDatabaseManager()
     
    table_data_local = database_manager.get_all_database_entries()
    table_data_local['system_download'] = [f'<a href="/assas_app/hdf5_file?uuid={entry.system_uuid}">hdf5 file</a>' for entry in table_data_local.itertuples()]
    table_data_local['meta_name'] = [f'<a href="/assas_app/details/{entry.system_uuid}">{entry.meta_name}</a>' for entry in table_data_local.itertuples()]
     
    return table_data_local

def get_database_size() -> str:
    ''' 
    Get the overall size of the ASSAS database.
    
    Returns:
        str: Overall size of the database in a human-readable format.
    '''
    
    
    database_manager = AssasDatabaseManager()
    size = database_manager.get_overall_database_size()
    
    if size is None or len(size) == 0:
        return '0 B'
    
    return size

table_data = update_table_data()
database_size = get_database_size()

ALL = len(table_data)
PAGE_SIZE = 30
PAGE_MAX_SIZE = 100

PAGE_COUNT = ALL / PAGE_SIZE

dash.register_page(__name__, path='/database')

layout = html.Div([
    html.H2('ASSAS Database - Training Dataset Index'),
    dbc.Alert('Search interface for the available ASSAS training datasets', color='primary', style={'textAlign': 'center'}),
    html.Hr(),
    html.Div([
    dbc.Pagination(
                id='pagination', 
                first_last=True,
                previous_next=True,
                max_value=PAGE_COUNT, 
                fully_expanded=False,
                size='lg'
                )
    ], style={'width': '100%','padding-left':'30%', 'padding-right':'25%'}),
    html.Hr(),
    html.Div([
    dbc.Row([
            dbc.Col(html.H4("Select datasets for download:")),
            dbc.Col(html.H4("Refresh datasets on page:")),
            dbc.Col(html.H4("Database parameters:")),
    ]),
    dbc.Row([
        dbc.Col(dcc.Loading(
                children=[
                    dbc.Button(
                        'Get Download Link', 
                        id='download_selected', 
                        className='me-2', 
                        n_clicks=0, 
                        disabled=True,
                        style = {'fontSize': 20, 'textAlign': 'center', 'margin-bottom': '1%', 'margin-left': '5%'}
                        ),
                ],
                type='circle',
                fullscreen=False
                ),
            ),
        dbc.Col(dbc.Button(
                    'Refresh', 
                    id='reload_page', 
                    className='me-2', 
                    n_clicks=0, 
                    disabled=False,
                    style = {'fontSize': 20, 'textAlign': 'center', 'margin-bottom': '1%'}
                    ),
                ),
        dbc.Col(html.H4(f"Disk size on LSDF is {database_size}"), style={'textAlign': 'left', 'padding-top': '0.5%'}),
    ]),
    dbc.Row([
        dbc.Col(html.Div('Status', id='download_status', style={'fontSize': 20, 'textAlign': 'left', 'padding-top': '0.5%'})),
    ]),
    dbc.Row([
        dbc.Col(html.Div('Link', id='download_link', style={'fontSize': 20,  'textAlign': 'left', 'padding-top': '0.5%'})), 
    ]),
    ], style={'width': '100%','padding-left':'5%', 'padding-right':'25%'}),
    dcc.Location(id='download_location', refresh=True),
    html.Hr(),
    dash_table.DataTable(
        id='datatable-paging-and-sorting',
        columns=[
        {'name': '_id', 'id': '_id', 'hideable': True},
        {'name': 'Uuid', 'id': 'system_uuid', 'hideable': True},
        {'name': 'Upload Uuid', 'id': 'system_upload_uuid', 'hideable': True},
        {'name': 'Path', 'id': 'system_path', 'hideable': True},
        {'name': 'Result', 'id': 'system_result', 'hideable': True},
        {'name': 'Index', 'id': 'system_index', 'selectable': True},
        {'name': 'Size binary', 'id': 'system_size', 'selectable': True},
        {'name': 'Size hdf5', 'id': 'system_size_hdf5', 'selectable': True},
        {'name': 'Date', 'id': 'system_date', 'selectable': True},
        {'name': 'User', 'id': 'system_user', 'selectable': True},
        {'name': 'Download', 'id': 'system_download', 'selectable': True, 'presentation': 'markdown'},
        {'name': 'Status', 'id': 'system_status', 'selectable': True},
        {'name': 'Name', 'id': 'meta_name', 'selectable': True, 'presentation': 'markdown'},
        ],
        markdown_options={'html': True},
        hidden_columns=['', '_id', 'system_uuid', 'system_upload_uuid', 'system_path', 'system_result'],
        data=table_data.to_dict('records'),
        style_cell={
            'fontSize': 17,
            'padding': '2px',
            'textAlign': 'center',
            'font-family':'sans-serif',
        },
        merge_duplicate_headers= True,
        
        style_header={
            'backgroundColor': 'black',
            'color': 'white',
            'fontWeight': 'bold'
        },
        
        style_data={
            'backgroundColor': 'black',
            'color': 'white'
        },
        
        row_selectable='multi',
        
        page_current=0,
        page_size=PAGE_SIZE,
        page_action='none',
                
        filter_action='custom',
        filter_query='',

        sort_action='custom',
        sort_mode='multi',
        sort_by=[],
        
        is_focused=True,
        
        style_data_conditional=conditional_table_style(),
        css=[dict(selector= "p", rule= "margin: 0; text-align: center")]
    ),
    html.Hr(),
    html.Br(),
    dcc.Checklist(
        id='datatable-use-page-size',
        options=[
            {'label': ' Change entries per page', 'value': 'True'}
        ],
        value=['False']
    ),
    'Entries per page: ',
    dcc.Input(
        id='datatable-page-size',
        type='number',
        min=1,
        max=PAGE_MAX_SIZE,
        value=PAGE_SIZE,
        placeholder=PAGE_SIZE,
        style={'color': 'grey'},
        disabled=False,
    ),
    html.Div('Select a page', id='pagination-contents'),
],style=content_style())

def copy_and_zip_files(
    file_info: List[tuple],
    destination_folder,
    zip_file_name
)-> str:
    '''
    Copies a list of files to a destination folder and zips them into an archive.
    
    Args:
        file_list (list): List of file paths to copy.
        destination_folder (str): Path to the destination folder.
        zip_file_name (str): Name of the resulting zip file.
        
    Returns:
        str: Path to the created zip file.
    '''
    # Ensure the destination folder exists
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    # Copy files to the destination folder
    for file_path, file_uuid in file_info:
        if os.path.exists(file_path):
            destination_path = Path(destination_folder) / (f'{file_uuid}_' + Path(file_path).name)
            logger.info(f"Copying {file_path} to {destination_path}")
            # Copy the file to the destination folder with a new name
            shutil.copy(file_path, destination_path)
        else:
            logger.warning(f"File not found: {file_path}")
    
    file_list = [os.path.join(destination_folder, f'{file_uuid}_' + Path(file_path).name) for file_path, file_uuid in file_info]
    logger.info(f"Files copied to {destination_folder}: {file_list}")
    
    # Create the zip file
    zip_file_path = os.path.join(destination_folder, zip_file_name)
    with ZipFile(zip_file_path, 'w') as zip_object:
        for file_path in file_list:
            file_name = Path(file_path).name
            destination_path = os.path.join(destination_folder, file_name)
            if os.path.exists(destination_path):
                zip_object.write(destination_path, arcname=file_name)
    
    # Verify if the zip file was created
    if os.path.exists(zip_file_path):
        logger.info(f"ZIP file created: {zip_file_path}")
        return zip_file_path
    else:
        logger.error(f"Failed to create ZIP file: {zip_file_path}")
        return None

def clean_tmp_folder(
    parent_folder: str):
    """
    Deletes all folders within a specified parent folder.

    Args:
        parent_folder (str): Path to the parent folder.
    """
    try:
        parent_path = Path(parent_folder)
        if not parent_path.exists():
            logger.info(f"Parent folder {parent_folder} does not exist.")
            return

        # Iterate through all items in the parent folder
        for item in parent_path.iterdir():
            if item.is_dir():  # Check if the item is a folder
                logger.info(f"Deleting folder: {item}")
                shutil.rmtree(item)  # Delete the folder and its contents

        logger.info(f"All folders in {parent_folder} have been deleted.")
    
    except Exception as e:
        logger.error(f"Failed to delete folders in {parent_folder}: {e}")

@callback(
    Output('download_selected', 'disabled'),
    Output('download_status', 'children'),
    Output('download_link', 'children'),
    Input('download_selected', 'n_clicks'),
    Input('datatable-paging-and-sorting', 'derived_viewport_selected_rows'),
    Input('datatable-paging-and-sorting', 'derived_viewport_selected_row_ids'),
    State('datatable-paging-and-sorting', 'derived_viewport_data'))
def start_download(
    clicks,
    rows,
    ids,
    data
):
    logger.info(f'Starting download with clicks: {clicks}, rows: {rows}, ids: {ids}')
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0] if callback_context.triggered else None
    logger.info(f"Triggered by: {triggered_id}")
    
    no_href_link = html.A("Download link will be available here.", href=None, style={"color": "red"})
    
    if (rows is None) or (ids is None):
        return False, 'No rows selected for download.', no_href_link
        
    if len(rows) > 0:
        
        logger.info(f'Disabled is False, Selected rows: {rows}, ids: {ids}')
        
        if triggered_id == 'download_selected':
            
            logger.info(f'Download button was pressed: {clicks}, rows: {rows}')
    
            uuid = str(uuid4())
            logger.info(f'Started download (id = {uuid}).')
            
            clean_tmp_folder(
                parent_folder = TMP_FOLDER
            )
            
            destination_folder = f'{TMP_FOLDER}/download_{uuid}'
            
            selected_data = [data[i] for i in rows]
            file_paths = [data_item['system_result'] for data_item in selected_data]
            file_uuids = [data_item['system_uuid'] for data_item in selected_data]
            file_info = list(zip(file_paths, file_uuids))
            
            zip_file_name = f'download_{uuid}.zip'
            
            logger.info(f'file paths: {file_paths}')
            logger.info(f'file uuids: {file_uuids}')
            logger.info(f'destination folder: {destination_folder}')
            
            copy_and_zip_files(
                file_info = file_info,
                destination_folder = destination_folder,
                zip_file_name = zip_file_name
            )
            
            flask_url = f"/assas_app/hdf5_download?uuid={uuid}"
            clickable_link = html.A(f"Click here to download the zip archive", href=flask_url, target="_blank")
            
            return False, f'Zipped archive ready for download.', clickable_link
        
        else:
            
            logger.info(f'No download button was pressed, just selected rows: {rows}, ids: {ids}')
            return False, 'Press button to generate download link.', no_href_link
    
    else:
        
        logger.info(f'Disabled is True, Selected rows: {rows}, ids: {ids}')
        return True, 'No rows selected for download.', no_href_link
    
def split_filter_part(
    filter_part
):
    
    logger.info(f'Operators: {operators}')
    logger.info(f'Filter part: {filter_part}')
    
    for operator_type in operators:
        
        for operator in operator_type:
            
            if operator in filter_part:
                
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

                value_part = value_part.strip()
                v0 = value_part[0]
                
                if (v0 == value_part[-1] and v0 in (''', ''', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3

@callback(
    Output('datatable-paging-and-sorting', 'data'),
    Input('datatable-paging-and-sorting', 'page_current'),
    Input('datatable-paging-and-sorting', 'page_size'),
    Input('datatable-paging-and-sorting', 'sort_by'),
    Input('datatable-paging-and-sorting', 'filter_query'),
    Input('reload_page', 'n_clicks'))
def update_table(
    page_current,
    page_size,
    sort_by,
    filter,
    n_clicks
):
    dataframe = update_table_data()
    
    filtering_expressions = filter.split(' && ')
    
    logger.info(f'filtering_expressions: {filtering_expressions}')
    logger.info(f'page_current: {page_current}, page_size: {page_size}, sort_by: {sort_by}, filter: {filter}, n_clicks: {n_clicks}')

    for filter_part in filtering_expressions:
        
        col_name, operator, filter_value = split_filter_part(filter_part)
        
        logger.info(f'filter_part: {filter_part}, col_name: {col_name}, operator: {operator}, filter_value: {filter_value}')
        
        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            # these operators match pandas series operator method names
            dataframe = dataframe.loc[getattr(dataframe[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dataframe = dataframe.loc[dataframe[col_name].str.contains(filter_value)]
        elif operator == 'datestartswith':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dataframe = dataframe.loc[dataframe[col_name].str.startswith(filter_value)]

    if len(sort_by):
        
        dataframe = dataframe.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[
                col['direction'] == 'asc'
                for col in sort_by
            ],
            inplace=False
        )

    page = page_current
    size = page_size
    
    return dataframe.iloc[page * size: (page + 1) * size].to_dict('records')

@callback(
    Output('datatable-paging-and-sorting', 'page_size'),
    Input('datatable-use-page-size', 'value'),
    Input('datatable-page-size', 'value'))
def update_page_size(
    use_page_size, 
    page_size_value
):
    
    logger.debug(f'update page size, use_page_size: {use_page_size}, page_size_value: {page_size_value}')
    
    if len(use_page_size) == 0 or page_size_value is None:
        return PAGE_SIZE
    
    return page_size_value

@callback(
    Output('pagination-contents', 'children'),
    Input('pagination', 'active_page'),
    Input('pagination', 'max_value'))
def change_page(
    page, 
    value
):
    
    logger.debug(f'page: {page}, value: {value}')
    
    if page:
        return f'Page selected: {page}/{value}'
    
    return f'Page selected: 1/{value}'

@callback(
    Output('datatable-paging-and-sorting', 'page_current'),
    Input('pagination', 'active_page'))
def change_page_table(
    page
):
    
    logger.debug(f'page {page}')
    
    if page:
        return (page - 1)
    
    return 0

@callback(
    Output('pagination', 'max_value'),
    Output('datatable-page-size', 'style'),
    Input('datatable-use-page-size', 'value'),
    Input('datatable-page-size', 'value'))
def update_page_count(
    use_page_size, 
    page_size_value
):
    
    logger.debug(f'Update page count, use page size: {use_page_size}, page size value {page_size_value}.')
    
    if len(use_page_size) > 1 and page_size_value is not None:
        return int(len(table_data) / page_size_value) + 1, {'color': 'black'}
    
    if page_size_value is None:
        return int(len(table_data) / PAGE_SIZE) + 1, {'color': 'grey'}
    
    return int(len(table_data) / PAGE_SIZE) + 1, {'color': 'grey'}
