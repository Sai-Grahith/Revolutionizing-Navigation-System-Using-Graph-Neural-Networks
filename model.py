import torch
import torch.nn as nn
from torch_geometric.nn import GCNConv, SAGEConv
import os 

class GNNRoutingModel(nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels):
        super(GNNRoutingModel, self).__init__()
        self.conv1 = GCNConv(in_channels, hidden_channels)
        self.conv2 = SAGEConv(hidden_channels, hidden_channels)
        self.conv3 = GCNConv(hidden_channels, out_channels)
        self.relu = nn.ReLU()

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = self.relu(x)
        x = self.conv2(x, edge_index)
        x = self.relu(x)
        x = self.conv3(x, edge_index)
        return x

def create_model():
    in_channels = 1
    hidden_channels = 16
    out_channels = 1
    model = GNNRoutingModel(in_channels, hidden_channels, out_channels)
    return model

def load_or_initialize_model():
    model_path = 'gnn_model.pt'
    model = create_model()
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    else:
        torch.save(model.state_dict(), model_path)
    return model
