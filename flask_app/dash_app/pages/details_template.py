import dash
import dash_bootstrap_components as dbc
import logging

from flask import current_app as flask_app
from dash import html
from assasdb import AssasDatabaseManager
from ..components import content_style

logger = logging.getLogger('assas_app')

dash.register_page(__name__, path_template="/details/<report_id>")

def meta_info_table(document):
    
    general_header = [
            html.Thead(html.Tr([html.Th("General")]))
        ]
    
    general_body = [html.Tbody([html.Tr([html.Td("Name"), html.Td(document["meta_name"])]),
                                html.Tr([html.Td("Group"), html.Td(document["meta_group"])]),
                                html.Tr([html.Td("Date"), html.Td(document["meta_date"])]),
                                html.Tr([html.Td("Creator"), html.Td(document["meta_creator"])]),
                                html.Tr([html.Td("Description"), html.Td(document["meta_description"])])
                            ])]
    
    data_header = [
            html.Thead(html.Tr([html.Th("Data")]))
        ]
    
    data_body = [html.Tbody([html.Tr([html.Td("Variables"), html.Td(document["meta_data_variables"])]),
                             html.Tr([html.Td("Channels"), html.Td(document["meta_data_channels"])]),
                             html.Tr([html.Td("Meshes"), html.Td(document["meta_data_meshes"])]),
                             html.Tr([html.Td("Timesteps"), html.Td(document["meta_data_timesteps"])])
                            ])]
    
    table = general_header + general_body + data_header + data_body
    
    return dbc.Table(table, striped=True, bordered=True, hover=True, responsive=True)

def layout(report_id=None):
    
    logger.info("report_id %s" % (report_id))
    
    if (report_id == 'none') or (report_id is None):
        return html.Div([
            html.H1('This is the data details template.'),
            html.Div('The content is generated for each _id.'),
            ],style = content_style())
    else:
        database_manager = AssasDatabaseManager(flask_app.config.get('LOCAL_ARCHIVE'), flask_app.config.get('LSDF_ARCHIVE'))
        document = database_manager.get_database_entry(report_id)
        logger.info("document %s" % (document))
    
        return html.Div([    
            meta_info_table(document)            
        ],style=content_style())