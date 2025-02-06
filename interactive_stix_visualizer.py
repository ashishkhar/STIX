import json
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import streamlit.components.v1 as components

def load_stix_bundle(file_path):
    """Load STIX bundle from JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def create_network_graph(bundle):
    """Create an interactive network graph using pyvis."""
    # Create network
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")
    
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
            node_label = obj.get('name', obj['id'].split('--')[0])
            net.add_node(obj['id'], 
                        label=node_label,
                        title=str({k: v for k, v in obj.items() if isinstance(v, (str, int, float))}),
                        color=color_map.get(obj['type'], '#d4d4d4'))
    
    # Add edges
    for obj in bundle['objects']:
        if obj['type'] == 'relationship':
            net.add_edge(obj['source_ref'], 
                        obj['target_ref'], 
                        title=obj['relationship_type'],
                        label=obj['relationship_type'])
    
    # Set physics layout
    net.set_options("""
    {
        "physics": {
            "forceAtlas2Based": {
                "gravitationalConstant": -50,
                "centralGravity": 0.01,
                "springLength": 200,
                "springConstant": 0.08
            },
            "maxVelocity": 50,
            "solver": "forceAtlas2Based",
            "timestep": 0.35,
            "stabilization": {"iterations": 150}
        }
    }
    """)
    
    return net

def main():
    st.set_page_config(page_title="STIX 2.1 Visualizer", layout="wide")
    
    st.title("Interactive STIX 2.1 Visualization")
    
    # Load the STIX bundle
    try:
        bundle = load_stix_bundle('bundle_2025_02_06_16_44.json')
        
        # Create network
        net = create_network_graph(bundle)
        
        # Save and display the network
        net.save_graph("stix_network.html")
        
        # Display the graph
        with open("stix_network.html", 'r', encoding='utf-8') as f:
            html_string = f.read()
        components.html(html_string, height=600)
        
        # Display legend
        st.sidebar.title("Legend")
        color_map = {
            'Threat Actor': '#ff6b6b',
            'Campaign': '#4ecdc4',
            'Infrastructure': '#45b7d1',
            'Autonomous System': '#96ceb4',
            'URL': '#ffeead'
        }
        
        for obj_type, color in color_map.items():
            st.sidebar.markdown(
                f'<div style="background-color: {color}; padding: 10px; border-radius: 5px; margin: 5px 0;">'
                f'{obj_type}</div>',
                unsafe_allow_html=True
            )
        
        # Display statistics
        st.sidebar.title("Statistics")
        node_count = len([obj for obj in bundle['objects'] if obj['type'] != 'relationship'])
        edge_count = len([obj for obj in bundle['objects'] if obj['type'] == 'relationship'])
        st.sidebar.write(f"Nodes: {node_count}")
        st.sidebar.write(f"Relationships: {edge_count}")
        
    except Exception as e:
        st.error(f"Error loading or processing the STIX bundle: {str(e)}")

if __name__ == "__main__":
    main() 