import osmnx as ox
import networkx as nx
import random

def create_graph_with_traffic():
    try:
        # Define bounding box with coordinates in the order (left, bottom, right, top)
        bbox = (78.3245, 17.3807, 78.3444, 17.4372)  # MGIT to Gachibowli
        G = ox.graph_from_bbox(north=bbox[3], south=bbox[1], east=bbox[2], west=bbox[0], network_type='drive')
        print("Graph loaded successfully.")

        print("Adding synthetic traffic congestion levels to edges.")
        for u, v, key, data in G.edges(keys=True, data=True):
            data['congestion'] = random.uniform(0, 1)
        print("Traffic congestion levels added.")

        return G

    except Exception as e:
        print(f"Error fetching graph data: {e}")
        return None

# Example usage
G = create_graph_with_traffic()
if G is not None:
    print("Graph created successfully.")
else:
    print("Failed to create graph.")
