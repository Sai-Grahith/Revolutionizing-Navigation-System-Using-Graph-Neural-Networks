from flask import Flask, jsonify, render_template, request
import torch
from model import create_model
from graph import create_graph_with_traffic
import osmnx as ox
import networkx as nx
import os

# Explicitly set the template folder
template_dir = os.path.abspath('templates')
app = Flask(__name__, template_folder=template_dir)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['GET'])
def predict():
    start_lat = request.args.get('startLat', type=float)
    start_lon = request.args.get('startLon', type=float)
    end_lat = request.args.get('endLat', type=float)
    end_lon = request.args.get('endLon', type=float)

    print(f"Received request for route from ({start_lat}, {start_lon}) to ({end_lat}, {end_lon})")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = create_model().to(device)
    model.load_state_dict(torch.load('gnn_model.pt', map_location=device))
    model.eval()

    G = create_graph_with_traffic()
    if G is None:
        print("Failed to fetch the road network data.")
        return jsonify({'error': 'Failed to fetch the road network data.'}), 500

    source = ox.distance.nearest_nodes(G, start_lon, start_lat)
    destination = ox.distance.nearest_nodes(G, end_lon, end_lat)

    print(f"Source node: {source}, Destination node: {destination}")

    # Calculate the shortest path based on road network
    try:
        route = nx.shortest_path(G, source, destination, weight='length')
        route_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route]
        print(f"Calculated route: {route_coords}")

        # Calculate the total distance
        total_distance = sum(ox.distance.great_circle_vec(route_coords[i-1][0], route_coords[i-1][1], route_coords[i][0], route_coords[i][1])
                             for i in range(1, len(route_coords))) / 1000  # Convert meters to kilometers
        
        # Assume an average speed (in km/h) and calculate the travel time
        average_speed_kmh = 15  # Adjust this value as needed
        travel_time_hours = total_distance / average_speed_kmh
        travel_time_minutes = travel_time_hours * 60
        
        print(f"Total distance: {total_distance:.2f} km, Estimated travel time: {travel_time_minutes:.2f} minutes")

    except nx.NetworkXNoPath:
        print("No path between these locations.")
        return jsonify({'error': 'No path between these locations.'}), 404

    return jsonify({'route': route_coords, 'distance': total_distance, 'time': travel_time_minutes})

if __name__ == '__main__':
    app.run(debug=True)
