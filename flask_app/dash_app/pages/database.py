import os
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import logging

from dash import Dash, dash_table, html, dcc, Input, Output, callback, State
from flask import current_app as flask_app
from zipfile import ZipFile
from uuid import uuid4
from pathlib import Path

from assasdb import AssasDatabaseManager
from ..components import content_style, conditional_table_style

logger = logging.getLogger('assas_app')

print("database page executed ONCE")

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
     
     logger.info('Load daqtabase entries to table')
     
     database_manager = AssasDatabaseManager()
     
     table_data_local = database_manager.get_all_database_entries()
     table_data_local['system_download'] = [f'<a href="/assas_app/hdf5_file?uuid={entry.system_uuid}">hdf5 file</a>' for entry in table_data_local.itertuples()]
     table_data_local['meta_name'] = [f'<a href="/assas_app/details/{entry.system_uuid}">{entry.meta_name}</a>' for entry in table_data_local.itertuples()]
     
     return table_data_local

def get_database_size() -> str:
    
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
            dbc.Col(html.H4("Download selected datasets:")),
            dbc.Col(html.H4("Refresh datasets on page:")),
            dbc.Col(html.H4("Database parameters:")),
    ]),
    dbc.Row([
        dbc.Col(dbc.Button(
                    'Download', 
                    id='download_selected', 
                    className='me-2', 
                    n_clicks=0, 
                    disabled=True,
                    style = {'fontSize': 20, 'textAlign': 'center', 'margin-bottom': '1%', 'margin-left': '5%'}
                    #style = {'margin-left': '1%','margin-right': '1%','width': '10%','fontSize': 20, 'textAlign': 'center', 'margin-bottom': '1%'}
                    ),
            ),
        dbc.Col(dbc.Button(
                    'Refresh', 
                    id='reload_page', 
                    className='me-2', 
                    n_clicks=0, 
                    disabled=False,
                    style = {'fontSize': 20, 'textAlign': 'center', 'margin-bottom': '1%'}
                    #style = {'margin-left': '1%','margin-right': '1%','width': '10%','fontSize': 20, 'textAlign': 'center'}
                    ),
                ),
        dbc.Col(html.H4(f"Disk size on LSDF is {database_size}"), style={'textAlign': 'left', 'padding-top': '0.5%'}),
    ]),
    ], style={'width': '100%','padding-left':'5%', 'padding-right':'25%'}),
    dcc.Download(id='download_button'),
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
    #dcc.Location(id='location'),
    dcc.Location(id='location_download'),
    dcc.Download(id='download'),
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

def generate_archive(
    path_to_zip,
    file_path_list
):
    
    with ZipFile(path_to_zip, 'w') as zip_object:
        
        for file_path in file_path_list:
            zip_object.write(file_path)
            
    if os.path.exists(path_to_zip):
        logger.info(f'ZIP file %s created {path_to_zip}')
        return path_to_zip
    else:
        logger.info(f'ZIP file %s not created {path_to_zip}')
        return None

@callback(
    Output('location_download', 'href'),
    Input('download_selected', 'n_clicks'),
    State('datatable-paging-and-sorting', 'derived_viewport_selected_rows'),
    State('datatable-paging-and-sorting', 'derived_viewport_selected_row_ids'),
    State('datatable-paging-and-sorting', 'derived_viewport_data'))
def start_download(
    clicks,
    rows,
    ids,
    data
):
    
    if (rows is None) or (ids is None) or len(rows) == 0:
        return dash.no_update
    
    uuid = str(uuid4())
    logger.info(f'started download (id = {uuid})')
    
    download_folder = '/root/tmp'
    if not os.path.exists(download_folder):
        logger.info(f'create {download_folder}')
        os.makedirs(download_folder)
        
    selected_data = [data[i] for i in rows]
    file_list = [data_item['system_result'] for data_item in selected_data]
    
    zip_file = download_folder + '/download_' + uuid + '.zip'
    logger.info(f'generate archive {zip_file}')
    
    zip_file = generate_archive(zip_file, file_list)
    
    logger.debug(f'clicks: {clicks}, rows: {str(rows)}, files: {file_list}, zip: {zip_file}')
    
    return f'/assas_app/hdf5_download?uuid={uuid}'

@callback(
    Output('download_selected', 'disabled'),
    Input('datatable-paging-and-sorting', 'derived_viewport_selected_rows'),
    Input('datatable-paging-and-sorting', 'derived_viewport_selected_row_ids'),
    State('datatable-paging-and-sorting', 'derived_viewport_data'))
def selected_button(
    rows,
    ids,
    data
):
    
    if (rows is None) or (ids is None):
        return dash.no_update
        
    if len(rows) > 0:
        return False
    
    return True

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
        return int(len(table_data) / page_size_value) + 1,{'color': 'black'}
    
    if page_size_value is None:
        return int(len(table_data) / PAGE_SIZE) + 1,{'color': 'grey'}
    
    return int(len(table_data) / PAGE_SIZE) + 1,{'color': 'grey'}
