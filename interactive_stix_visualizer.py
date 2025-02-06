import json
import dash
from dash import html
from dash import dcc
import dash_cytoscape as cyto
from dash.dependencies import Input, Output

# Load the required stylesheet
cyto.load_extra_layouts()

def load_stix_bundle(file_path):
    """Load STIX bundle from JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def create_cytoscape_elements(bundle):
    """Convert STIX bundle to Cytoscape elements."""
    elements = []
    
    # Color mapping for different STIX object types
    color_map = {
        'threat-actor': '#ff6b6b',
        'campaign': '#4ecdc4',
        'infrastructure': '#45b7d1',
        'autonomous-system': '#96ceb4',
        'url': '#ffeead',
        'relationship': '#d4d4d4'
    }
    
    # Add nodes
    for obj in bundle['objects']:
        if obj['type'] != 'relationship':
            node = {
                'data': {
                    'id': obj['id'],
                    'label': obj.get('name', obj['id'].split('--')[0]),
                    'type': obj['type'],
                    'backgroundColor': color_map.get(obj['type'], '#d4d4d4'),
                    # Add all object properties for the hover data
                    **{k: v for k, v in obj.items() if isinstance(v, (str, int, float))}
                }
            }
            elements.append(node)
    
    # Add edges
    for obj in bundle['objects']:
        if obj['type'] == 'relationship':
            edge = {
                'data': {
                    'id': obj['id'],
                    'source': obj['source_ref'],
                    'target': obj['target_ref'],
                    'label': obj['relationship_type']
                }
            }
            elements.append(edge)
    
    return elements

# Initialize the Dash app
app = dash.Dash(__name__)

# Load the STIX bundle
bundle = load_stix_bundle('bundle_2025_02_06_16_44.json')
elements = create_cytoscape_elements(bundle)

# Define the app layout
app.layout = html.Div([
    html.H1("Interactive STIX 2.1 Visualization", 
            style={'textAlign': 'center', 'marginBottom': '20px'}),
    
    html.Div([
        # Graph layout selection
        html.Label('Select Layout:'),
        dcc.Dropdown(
            id='layout-dropdown',
            options=[
                {'label': 'Concentric', 'value': 'concentric'},
                {'label': 'Circle', 'value': 'circle'},
                {'label': 'Cose', 'value': 'cose'},
                {'label': 'Cola', 'value': 'cola'},
                {'label': 'Breadthfirst', 'value': 'breadthfirst'}
            ],
            value='cola',
            style={'width': '200px', 'marginBottom': '20px'}
        ),
    ], style={'marginLeft': '20px'}),
    
    # The main graph
    cyto.Cytoscape(
        id='stix-graph',
        layout={'name': 'cola'},
        elements=elements,
        style={'width': '100%', 'height': '600px'},
        stylesheet=[
            # Node styling
            {
                'selector': 'node',
                'style': {
                    'content': 'data(label)',
                    'background-color': 'data(backgroundColor)',
                    'font-size': '12px',
                    'text-wrap': 'wrap',
                    'text-max-width': '100px'
                }
            },
            # Edge styling
            {
                'selector': 'edge',
                'style': {
                    'content': 'data(label)',
                    'curve-style': 'bezier',
                    'target-arrow-shape': 'triangle',
                    'line-color': '#666',
                    'target-arrow-color': '#666',
                    'font-size': '10px'
                }
            }
        ]
    ),
    
    # Node details panel
    html.Div(id='node-data', 
             style={
                 'marginTop': '20px',
                 'padding': '20px',
                 'backgroundColor': '#f8f9fa',
                 'borderRadius': '5px'
             })
])

# Callback to update layout
@app.callback(
    Output('stix-graph', 'layout'),
    Input('layout-dropdown', 'value')
)
def update_layout(layout):
    return {'name': layout}

# Callback to display node data
@app.callback(
    Output('node-data', 'children'),
    Input('stix-graph', 'tapNodeData')
)
def display_node_data(data):
    if not data:
        return "Click a node to see its details"
    
    # Filter out internal cytoscape properties
    relevant_data = {k: v for k, v in data.items() 
                    if k not in ['backgroundColor', 'label'] and not k.startswith('_')}
    
    return html.Div([
        html.H4(f"Details for: {data.get('label', 'Unknown')}"),
        html.Table([
            html.Tr([html.Td(k), html.Td(str(v))])
            for k, v in relevant_data.items()
        ])
    ])

if __name__ == '__main__':
    app.run_server(debug=True) 