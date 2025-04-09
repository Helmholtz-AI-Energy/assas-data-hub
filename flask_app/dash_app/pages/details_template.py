import dash
import dash_bootstrap_components as dbc
import logging

from flask import current_app as flask_app
from dash import html
from assasdb import AssasDatabaseManager
from ..components import content_style

logger = logging.getLogger('assas_app')

dash.register_page(__name__, path_template='/details/<report_id>')

def meta_info_table(
    document: dict
)-> dbc.Table:

    general_header = [
            html.Thead(html.Tr([html.Th('NetCDF4 Dataset Attribute'), html.Th('Value')]))
        ]
    
    general_body = [html.Tbody([html.Tr([html.Td('Name'), html.Td(document['meta_name'])]),
                                #html.Tr([html.Td('Group'), html.Td(document['meta_group'])]),
                                #html.Tr([html.Td('Date'), html.Td(document['meta_date'])]),
                                #html.Tr([html.Td('Creator'), html.Td(document['meta_creator'])]),
                                html.Tr([html.Td('Description'), html.Td(document['meta_description'])])
        ])]
    
    data_header = [
            html.Thead(html.Tr([html.Th('NetCDF4 Variable Name'), html.Th('Domain'), html.Th('Dimensions'), html.Th('Shape')]))
        ]
    
    meta_data_variables = document.get('meta_data_variables')
    
    if meta_data_variables is None:
        table = general_header + general_body
        return dbc.Table(table, striped=True, bordered=True, hover=True, responsive=True)
    
    data_meta = []
    for meta_data in meta_data_variables:
        logger.debug(f'meta_data entry: {meta_data}')
        data_meta.append(html.Tr([html.Td(meta_data['name']), html.Td(meta_data['domain']), html.Td(meta_data['dimensions']), html.Td(meta_data['shape'])]))
    data_body = [html.Tbody(data_meta)]
    
    table = general_header + general_body + data_header + data_body
    
    return dbc.Table(table, striped=True, bordered=True, hover=True, responsive=True)

def layout(report_id=None):
    
    logger.info('report_id %s' % (report_id))
    
    if (report_id == 'none') or (report_id is None):
        return html.Div([
            html.H1('This is the data details template.'),
            html.Div('The content is generated for each _id.'),
            ],style = content_style())
    else:
        document = AssasDatabaseManager().get_database_entry_by_id(report_id)
        logger.info(f'Found document {document}')

        return html.Div([
            meta_info_table(document)
        ],style=content_style())