import torch
import torch.optim as optim
import torch.nn as nn
from model import create_model
from graph import create_graph_with_traffic
import networkx as nx
import osmnx as ox  
import time

def train_model(num_epochs=100, learning_rate=0.01):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    model = create_model().to(device)
    print("Model created and moved to device.")

    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.MSELoss()
    print("Optimizer and criterion set up.")

    print("Loading graph data.")
    G = create_graph_with_traffic()
    if G is None:
        print("Failed to fetch the road network data. Aborting training.")
        return
    print("Graph data loaded successfully.")

    # Update source and destination nodes within the bounding box
    source = ox.distance.nearest_nodes(G, 78.3245, 17.3807)  # Within bounding box
    destination = ox.distance.nearest_nodes(G, 78.3444, 17.4372)  # Within bounding box

    nodes = list(G.nodes)
    print(f"Number of nodes: {len(nodes)}")

    edges = []
    for edge in G.edges:
        edges.append([nodes.index(edge[0]), nodes.index(edge[1])])
    print(f"Number of edges: {len(edges)}")

    edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous().to(device)
    node_features = torch.tensor([[G.nodes[node].get('congestion', 0)] for node in nodes], dtype=torch.float).to(device)
    print("Node features and edge index tensors created.")

    for epoch in range(num_epochs):
        print(f"Epoch {epoch + 1}/{num_epochs}")

        try:
            start_time = time.time()

            # Generate the shortest path instead of all routes
            print("Generating shortest path")
            shortest_path = nx.shortest_path(G, source, destination, weight='length')
            print("Shortest path generated")
            all_routes = [shortest_path]
            elapsed_time = time.time() - start_time
            print(f"Generated shortest path in {elapsed_time} seconds")

            targets = []
            for route in all_routes:
                total_congestion = sum(G[u][v][0].get('congestion', 0) for u, v in zip(route[:-1], route[1:]))
                total_distance = sum(G[u][v][0].get('length', 0) for u, v in zip(route[:-1], route[1:]))
                targets.append([total_congestion + total_distance])

            print("Calculated targets")

            target = torch.tensor(targets, dtype=torch.float).to(device)
            print("Converted targets to tensor")

            model.train()
            optimizer.zero_grad()
            output = model(node_features, edge_index)
            loss = criterion(output, target)
            print(f"Loss for epoch {epoch + 1}: {loss.item()}")
            loss.backward()
            optimizer.step()

            if (epoch + 1) % 10 == 0:
                print(f"Epoch [{epoch + 1}/{num_epochs}], Loss: {loss.item():.4f}")

        except Exception as e:
            print(f"Error during training loop: {e}")
            break

    torch.save(model.state_dict(), 'gnn_model.pt')
    print("Model training complete and saved as 'gnn_model.pt'.")

if __name__ == "__main__":
    train_model()
