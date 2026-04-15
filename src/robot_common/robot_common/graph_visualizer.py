#!/usr/bin/env python3
"""
ROS2 Graph Visualizer - Generates visual graph as PNG image (no GUI needed)
"""
import subprocess
import time
from pathlib import Path

try:
    import networkx as nx
    from matplotlib import pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️  matplotlib and networkx not installed. Install with:")
    print("   pip3 install matplotlib networkx")


def get_ros2_graph():
    """Get all ROS2 nodes and topics"""
    try:
        nodes = subprocess.check_output(['ros2', 'node', 'list']).decode().strip().split('\n')
        topics = subprocess.check_output(['ros2', 'topic', 'list']).decode().strip().split('\n')
        return [n for n in nodes if n], [t for t in topics if t]
    except Exception as e:
        print(f"Error getting ROS2 graph: {e}")
        return [], []


def generate_graph_image(output_file="/tmp/ros2_graph.png"):
    """Generate visual graph as PNG image"""
    if not MATPLOTLIB_AVAILABLE:
        print("❌ matplotlib not available. Install first:")
        print("   pip3 install matplotlib networkx")
        return False
    
    print("📊 Generating graph visualization...")
    nodes, topics = get_ros2_graph()
    
    if not nodes and not topics:
        print("⚠️  No nodes or topics found. Is a task running?")
        return False
    
    # Create directed graph
    G = nx.DiGraph()
    
    # Add nodes with different colors
    for node in nodes:
        G.add_node(node, node_type='node')
    for topic in topics:
        G.add_node(topic, node_type='topic')
    
    # Create layout
    pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
    
    # Create figure
    plt.figure(figsize=(14, 10))
    
    # Draw nodes
    nx.draw_networkx_nodes(
        G, pos, 
        nodelist=nodes, 
        node_color='#3498db',  # Blue
        node_size=2000,
        label='Nodes'
    )
    
    nx.draw_networkx_nodes(
        G, pos, 
        nodelist=topics, 
        node_color='#2ecc71',  # Green
        node_size=1500,
        node_shape='s',
        label='Topics'
    )
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')
    
    # Draw title and legend
    plt.title(f"ROS2 System Graph\n{len(nodes)} Nodes | {len(topics)} Topics", 
              fontsize=14, fontweight='bold')
    plt.legend(scatterpoints=1, loc='upper left', fontsize=12)
    plt.axis('off')
    plt.tight_layout()
    
    # Save
    plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"✓ Graph image saved to: {output_file}")
    print(f"\nNodes ({len(nodes)}):")
    for node in nodes:
        print(f"  • {node}")
    print(f"\nTopics ({len(topics)}):")
    for topic in topics:
        print(f"  • {topic}")
    
    return True


if __name__ == "__main__":
    generate_graph_image()
