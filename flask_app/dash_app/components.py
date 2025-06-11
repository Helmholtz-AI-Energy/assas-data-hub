import dash
import os
import base64

def encode_svg_image(svg_name):
    
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets/') + svg_name
    encoded = base64.b64encode(open(path,'rb').read())
    svg = 'data:image/svg+xml;base64,{}'.format(encoded.decode())
    
    return svg

def content_style():
    
    return {
                'margin-top': '2rem',
                'margin-bottom': '2rem',
                'margin-left': '5rem',
                'margin-right': '5rem',
                'padding': '2rem 1rem',
                'border':'4px grey solid',
            }

def conditional_table_style(): 

    return [
                {'if': {'column_id': 'system_index'}, 'backgroundColor': 'grey', 'textAlign':' center', 'color':'black'},
                {'if': {'column_id': 'system_download'}, 'backgroundColor': 'grey', 'textAlign': 'center', 'textDecoration': 'underline', 'cursor': 'pointer', 'color': 'blue'},
                {'if': {'column_id': 'meta_name'}, 'backgroundColor': 'grey', 'color': 'blue', 'textAlign': 'center', 'textDecoration': 'underline', 'cursor': 'pointer', 'color': 'blue'}
        ]
    

