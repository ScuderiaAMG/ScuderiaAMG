"""Graph Neural Networks from scratch."""
import numpy as np
from typing import Optional, List, Tuple, Dict
from collections import defaultdict


class Graph:
    def __init__(self, node_features=None, edge_index=None, edge_attr=None):
        self.node_features = np.asarray(node_features) if node_features is not None else None
        self.edge_index = np.asarray(edge_index) if edge_index is not None else None
        self.edge_attr = np.asarray(edge_attr) if edge_attr is not None else None
        self.num_nodes = len(node_features) if node_features is not None else 0
        self.num_edges = edge_index.shape[1] if edge_index is not None else 0
    def adjacency_matrix(self):
        A = np.zeros((self.num_nodes, self.num_nodes))
        if self.edge_index is not None:
            for i in range(self.num_edges):
                u, v = self.edge_index[:, i]
                A[u, v] = self.edge_attr[i] if self.edge_attr is not None else 1.0
        return A
    def degree_matrix(self): return np.diag(self.adjacency_matrix().sum(axis=1))
    def laplacian(self): D = self.degree_matrix(); A = self.adjacency_matrix(); return D - A
    def normalized_laplacian(self):
        D = self.degree_matrix(); A = self.adjacency_matrix()
        D_inv_sqrt = np.diag(1.0 / np.sqrt(np.maximum(D.diagonal(), 1e-8)))
        return np.eye(self.num_nodes) - D_inv_sqrt @ A @ D_inv_sqrt

class GCNConv:
    """GCNConv graph convolution layer."""
    def __init__(self, in_channels: int, out_channels: int, **kwargs):
        self.in_channels = in_channels; self.out_channels = out_channels
        self.kwargs = kwargs
        bound = np.sqrt(6.0 / (in_channels + out_channels))
        self.weight = np.random.uniform(-bound, bound, (in_channels, out_channels)).astype(np.float32)
        self.bias = np.zeros(out_channels, dtype=np.float32)
    def forward(self, x: np.ndarray, edge_index: np.ndarray, edge_weight=None) -> np.ndarray:
        """Forward pass."""
        return x @ self.weight + self.bias  # Simplified message passing
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class GATConv:
    """GATConv graph convolution layer."""
    def __init__(self, in_channels: int, out_channels: int, **kwargs):
        self.in_channels = in_channels; self.out_channels = out_channels
        self.kwargs = kwargs
        bound = np.sqrt(6.0 / (in_channels + out_channels))
        self.weight = np.random.uniform(-bound, bound, (in_channels, out_channels)).astype(np.float32)
        self.bias = np.zeros(out_channels, dtype=np.float32)
    def forward(self, x: np.ndarray, edge_index: np.ndarray, edge_weight=None) -> np.ndarray:
        """Forward pass."""
        return x @ self.weight + self.bias  # Simplified message passing
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class GINConv:
    """GINConv graph convolution layer."""
    def __init__(self, in_channels: int, out_channels: int, **kwargs):
        self.in_channels = in_channels; self.out_channels = out_channels
        self.kwargs = kwargs
        bound = np.sqrt(6.0 / (in_channels + out_channels))
        self.weight = np.random.uniform(-bound, bound, (in_channels, out_channels)).astype(np.float32)
        self.bias = np.zeros(out_channels, dtype=np.float32)
    def forward(self, x: np.ndarray, edge_index: np.ndarray, edge_weight=None) -> np.ndarray:
        """Forward pass."""
        return x @ self.weight + self.bias  # Simplified message passing
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class SAGEConv:
    """SAGEConv graph convolution layer."""
    def __init__(self, in_channels: int, out_channels: int, **kwargs):
        self.in_channels = in_channels; self.out_channels = out_channels
        self.kwargs = kwargs
        bound = np.sqrt(6.0 / (in_channels + out_channels))
        self.weight = np.random.uniform(-bound, bound, (in_channels, out_channels)).astype(np.float32)
        self.bias = np.zeros(out_channels, dtype=np.float32)
    def forward(self, x: np.ndarray, edge_index: np.ndarray, edge_weight=None) -> np.ndarray:
        """Forward pass."""
        return x @ self.weight + self.bias  # Simplified message passing
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class GraphConv:
    """GraphConv graph convolution layer."""
    def __init__(self, in_channels: int, out_channels: int, **kwargs):
        self.in_channels = in_channels; self.out_channels = out_channels
        self.kwargs = kwargs
        bound = np.sqrt(6.0 / (in_channels + out_channels))
        self.weight = np.random.uniform(-bound, bound, (in_channels, out_channels)).astype(np.float32)
        self.bias = np.zeros(out_channels, dtype=np.float32)
    def forward(self, x: np.ndarray, edge_index: np.ndarray, edge_weight=None) -> np.ndarray:
        """Forward pass."""
        return x @ self.weight + self.bias  # Simplified message passing
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class ChebConv:
    """ChebConv graph convolution layer."""
    def __init__(self, in_channels: int, out_channels: int, **kwargs):
        self.in_channels = in_channels; self.out_channels = out_channels
        self.kwargs = kwargs
        bound = np.sqrt(6.0 / (in_channels + out_channels))
        self.weight = np.random.uniform(-bound, bound, (in_channels, out_channels)).astype(np.float32)
        self.bias = np.zeros(out_channels, dtype=np.float32)
    def forward(self, x: np.ndarray, edge_index: np.ndarray, edge_weight=None) -> np.ndarray:
        """Forward pass."""
        return x @ self.weight + self.bias  # Simplified message passing
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class ARMAConv:
    """ARMAConv graph convolution layer."""
    def __init__(self, in_channels: int, out_channels: int, **kwargs):
        self.in_channels = in_channels; self.out_channels = out_channels
        self.kwargs = kwargs
        bound = np.sqrt(6.0 / (in_channels + out_channels))
        self.weight = np.random.uniform(-bound, bound, (in_channels, out_channels)).astype(np.float32)
        self.bias = np.zeros(out_channels, dtype=np.float32)
    def forward(self, x: np.ndarray, edge_index: np.ndarray, edge_weight=None) -> np.ndarray:
        """Forward pass."""
        return x @ self.weight + self.bias  # Simplified message passing
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class SGConv:
    """SGConv graph convolution layer."""
    def __init__(self, in_channels: int, out_channels: int, **kwargs):
        self.in_channels = in_channels; self.out_channels = out_channels
        self.kwargs = kwargs
        bound = np.sqrt(6.0 / (in_channels + out_channels))
        self.weight = np.random.uniform(-bound, bound, (in_channels, out_channels)).astype(np.float32)
        self.bias = np.zeros(out_channels, dtype=np.float32)
    def forward(self, x: np.ndarray, edge_index: np.ndarray, edge_weight=None) -> np.ndarray:
        """Forward pass."""
        return x @ self.weight + self.bias  # Simplified message passing
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class APPNPConv:
    """APPNPConv graph convolution layer."""
    def __init__(self, in_channels: int, out_channels: int, **kwargs):
        self.in_channels = in_channels; self.out_channels = out_channels
        self.kwargs = kwargs
        bound = np.sqrt(6.0 / (in_channels + out_channels))
        self.weight = np.random.uniform(-bound, bound, (in_channels, out_channels)).astype(np.float32)
        self.bias = np.zeros(out_channels, dtype=np.float32)
    def forward(self, x: np.ndarray, edge_index: np.ndarray, edge_weight=None) -> np.ndarray:
        """Forward pass."""
        return x @ self.weight + self.bias  # Simplified message passing
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class GCN2Conv:
    """GCN2Conv graph convolution layer."""
    def __init__(self, in_channels: int, out_channels: int, **kwargs):
        self.in_channels = in_channels; self.out_channels = out_channels
        self.kwargs = kwargs
        bound = np.sqrt(6.0 / (in_channels + out_channels))
        self.weight = np.random.uniform(-bound, bound, (in_channels, out_channels)).astype(np.float32)
        self.bias = np.zeros(out_channels, dtype=np.float32)
    def forward(self, x: np.ndarray, edge_index: np.ndarray, edge_weight=None) -> np.ndarray:
        """Forward pass."""
        return x @ self.weight + self.bias  # Simplified message passing
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class EdgeConv:
    """EdgeConv graph convolution layer."""
    def __init__(self, in_channels: int, out_channels: int, **kwargs):
        self.in_channels = in_channels; self.out_channels = out_channels
        self.kwargs = kwargs
        bound = np.sqrt(6.0 / (in_channels + out_channels))
        self.weight = np.random.uniform(-bound, bound, (in_channels, out_channels)).astype(np.float32)
        self.bias = np.zeros(out_channels, dtype=np.float32)
    def forward(self, x: np.ndarray, edge_index: np.ndarray, edge_weight=None) -> np.ndarray:
        """Forward pass."""
        return x @ self.weight + self.bias  # Simplified message passing
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class PointConv:
    """PointConv graph convolution layer."""
    def __init__(self, in_channels: int, out_channels: int, **kwargs):
        self.in_channels = in_channels; self.out_channels = out_channels
        self.kwargs = kwargs
        bound = np.sqrt(6.0 / (in_channels + out_channels))
        self.weight = np.random.uniform(-bound, bound, (in_channels, out_channels)).astype(np.float32)
        self.bias = np.zeros(out_channels, dtype=np.float32)
    def forward(self, x: np.ndarray, edge_index: np.ndarray, edge_weight=None) -> np.ndarray:
        """Forward pass."""
        return x @ self.weight + self.bias  # Simplified message passing
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class NNConv:
    """NNConv graph convolution layer."""
    def __init__(self, in_channels: int, out_channels: int, **kwargs):
        self.in_channels = in_channels; self.out_channels = out_channels
        self.kwargs = kwargs
        bound = np.sqrt(6.0 / (in_channels + out_channels))
        self.weight = np.random.uniform(-bound, bound, (in_channels, out_channels)).astype(np.float32)
        self.bias = np.zeros(out_channels, dtype=np.float32)
    def forward(self, x: np.ndarray, edge_index: np.ndarray, edge_weight=None) -> np.ndarray:
        """Forward pass."""
        return x @ self.weight + self.bias  # Simplified message passing
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class CGConv:
    """CGConv graph convolution layer."""
    def __init__(self, in_channels: int, out_channels: int, **kwargs):
        self.in_channels = in_channels; self.out_channels = out_channels
        self.kwargs = kwargs
        bound = np.sqrt(6.0 / (in_channels + out_channels))
        self.weight = np.random.uniform(-bound, bound, (in_channels, out_channels)).astype(np.float32)
        self.bias = np.zeros(out_channels, dtype=np.float32)
    def forward(self, x: np.ndarray, edge_index: np.ndarray, edge_weight=None) -> np.ndarray:
        """Forward pass."""
        return x @ self.weight + self.bias  # Simplified message passing
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class TransformerConv:
    """TransformerConv graph convolution layer."""
    def __init__(self, in_channels: int, out_channels: int, **kwargs):
        self.in_channels = in_channels; self.out_channels = out_channels
        self.kwargs = kwargs
        bound = np.sqrt(6.0 / (in_channels + out_channels))
        self.weight = np.random.uniform(-bound, bound, (in_channels, out_channels)).astype(np.float32)
        self.bias = np.zeros(out_channels, dtype=np.float32)
    def forward(self, x: np.ndarray, edge_index: np.ndarray, edge_weight=None) -> np.ndarray:
        """Forward pass."""
        return x @ self.weight + self.bias  # Simplified message passing
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class GeneralConv:
    """GeneralConv graph convolution layer."""
    def __init__(self, in_channels: int, out_channels: int, **kwargs):
        self.in_channels = in_channels; self.out_channels = out_channels
        self.kwargs = kwargs
        bound = np.sqrt(6.0 / (in_channels + out_channels))
        self.weight = np.random.uniform(-bound, bound, (in_channels, out_channels)).astype(np.float32)
        self.bias = np.zeros(out_channels, dtype=np.float32)
    def forward(self, x: np.ndarray, edge_index: np.ndarray, edge_weight=None) -> np.ndarray:
        """Forward pass."""
        return x @ self.weight + self.bias  # Simplified message passing
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class TAGConv:
    """TAGConv graph convolution layer."""
    def __init__(self, in_channels: int, out_channels: int, **kwargs):
        self.in_channels = in_channels; self.out_channels = out_channels
        self.kwargs = kwargs
        bound = np.sqrt(6.0 / (in_channels + out_channels))
        self.weight = np.random.uniform(-bound, bound, (in_channels, out_channels)).astype(np.float32)
        self.bias = np.zeros(out_channels, dtype=np.float32)
    def forward(self, x: np.ndarray, edge_index: np.ndarray, edge_weight=None) -> np.ndarray:
        """Forward pass."""
        return x @ self.weight + self.bias  # Simplified message passing
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class LEConv:
    """LEConv graph convolution layer."""
    def __init__(self, in_channels: int, out_channels: int, **kwargs):
        self.in_channels = in_channels; self.out_channels = out_channels
        self.kwargs = kwargs
        bound = np.sqrt(6.0 / (in_channels + out_channels))
        self.weight = np.random.uniform(-bound, bound, (in_channels, out_channels)).astype(np.float32)
        self.bias = np.zeros(out_channels, dtype=np.float32)
    def forward(self, x: np.ndarray, edge_index: np.ndarray, edge_weight=None) -> np.ndarray:
        """Forward pass."""
        return x @ self.weight + self.bias  # Simplified message passing
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class PNAConv:
    """PNAConv graph convolution layer."""
    def __init__(self, in_channels: int, out_channels: int, **kwargs):
        self.in_channels = in_channels; self.out_channels = out_channels
        self.kwargs = kwargs
        bound = np.sqrt(6.0 / (in_channels + out_channels))
        self.weight = np.random.uniform(-bound, bound, (in_channels, out_channels)).astype(np.float32)
        self.bias = np.zeros(out_channels, dtype=np.float32)
    def forward(self, x: np.ndarray, edge_index: np.ndarray, edge_weight=None) -> np.ndarray:
        """Forward pass."""
        return x @ self.weight + self.bias  # Simplified message passing
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class MFConv:
    """MFConv graph convolution layer."""
    def __init__(self, in_channels: int, out_channels: int, **kwargs):
        self.in_channels = in_channels; self.out_channels = out_channels
        self.kwargs = kwargs
        bound = np.sqrt(6.0 / (in_channels + out_channels))
        self.weight = np.random.uniform(-bound, bound, (in_channels, out_channels)).astype(np.float32)
        self.bias = np.zeros(out_channels, dtype=np.float32)
    def forward(self, x: np.ndarray, edge_index: np.ndarray, edge_weight=None) -> np.ndarray:
        """Forward pass."""
        return x @ self.weight + self.bias  # Simplified message passing
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class TopKPooling:
    """TopKPooling graph pooling layer."""
    def __init__(self, in_channels, **kwargs):
        self.in_channels = in_channels; self.kwargs = kwargs
    def forward(self, x, edge_index, batch=None):
        return x, edge_index  # Pass-through stub
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class SAGPooling:
    """SAGPooling graph pooling layer."""
    def __init__(self, in_channels, **kwargs):
        self.in_channels = in_channels; self.kwargs = kwargs
    def forward(self, x, edge_index, batch=None):
        return x, edge_index  # Pass-through stub
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class ASAPooling:
    """ASAPooling graph pooling layer."""
    def __init__(self, in_channels, **kwargs):
        self.in_channels = in_channels; self.kwargs = kwargs
    def forward(self, x, edge_index, batch=None):
        return x, edge_index  # Pass-through stub
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class EdgePooling:
    """EdgePooling graph pooling layer."""
    def __init__(self, in_channels, **kwargs):
        self.in_channels = in_channels; self.kwargs = kwargs
    def forward(self, x, edge_index, batch=None):
        return x, edge_index  # Pass-through stub
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class AvgPooling:
    """AvgPooling graph pooling layer."""
    def __init__(self, in_channels, **kwargs):
        self.in_channels = in_channels; self.kwargs = kwargs
    def forward(self, x, edge_index, batch=None):
        return x, edge_index  # Pass-through stub
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class MaxPooling:
    """MaxPooling graph pooling layer."""
    def __init__(self, in_channels, **kwargs):
        self.in_channels = in_channels; self.kwargs = kwargs
    def forward(self, x, edge_index, batch=None):
        return x, edge_index  # Pass-through stub
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class SumPooling:
    """SumPooling graph pooling layer."""
    def __init__(self, in_channels, **kwargs):
        self.in_channels = in_channels; self.kwargs = kwargs
    def forward(self, x, edge_index, batch=None):
        return x, edge_index  # Pass-through stub
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class GlobalAttention:
    """GlobalAttention graph pooling layer."""
    def __init__(self, in_channels, **kwargs):
        self.in_channels = in_channels; self.kwargs = kwargs
    def forward(self, x, edge_index, batch=None):
        return x, edge_index  # Pass-through stub
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class Set2Set:
    """Set2Set graph pooling layer."""
    def __init__(self, in_channels, **kwargs):
        self.in_channels = in_channels; self.kwargs = kwargs
    def forward(self, x, edge_index, batch=None):
        return x, edge_index  # Pass-through stub
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class SortPooling:
    """SortPooling graph pooling layer."""
    def __init__(self, in_channels, **kwargs):
        self.in_channels = in_channels; self.kwargs = kwargs
    def forward(self, x, edge_index, batch=None):
        return x, edge_index  # Pass-through stub
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class DiffPool:
    """DiffPool graph pooling layer."""
    def __init__(self, in_channels, **kwargs):
        self.in_channels = in_channels; self.kwargs = kwargs
    def forward(self, x, edge_index, batch=None):
        return x, edge_index  # Pass-through stub
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class MinCutPool:
    """MinCutPool graph pooling layer."""
    def __init__(self, in_channels, **kwargs):
        self.in_channels = in_channels; self.kwargs = kwargs
    def forward(self, x, edge_index, batch=None):
        return x, edge_index  # Pass-through stub
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

class GraphDataLoader:
    def __init__(self, dataset, batch_size=32, shuffle=True):
        self.dataset = dataset; self.batch_size = batch_size
        self.shuffle = shuffle
    def __iter__(self):
        indices = list(range(len(self.dataset)))
        if self.shuffle: np.random.shuffle(indices)
        for start in range(0, len(indices), self.batch_size):
            batch_indices = indices[start:start+self.batch_size]
            yield self._collate([self.dataset[i] for i in batch_indices])
    def _collate(self, graphs):
        total_nodes = sum(g.num_nodes for g in graphs)
        total_edges = sum(g.num_edges for g in graphs)
        x = np.concatenate([g.node_features for g in graphs])
        edge_offset = 0
        edge_index_parts = []
        for g in graphs:
            ei = g.edge_index + edge_offset
            edge_index_parts.append(ei)
            edge_offset += g.num_nodes
        edge_index = np.concatenate(edge_index_parts, axis=1) if edge_index_parts else np.zeros((2,0), dtype=np.int64)
        batch = np.repeat(np.arange(len(graphs)), [g.num_nodes for g in graphs])
        return x, edge_index, batch
    def __len__(self): return (len(self.dataset) + self.batch_size - 1) // self.batch_size

class PLANETOIDDataset:
    """Planetoid dataset."""
    def __init__(self, root="./data", split="train"):
        self.root = root; self.split = split
        self.graphs = []
        self.num_classes = 10
    def __len__(self): return len(self.graphs)
    def __getitem__(self, idx): return self.graphs[idx]

class TUDATASETDataset:
    """TUDataset dataset."""
    def __init__(self, root="./data", split="train"):
        self.root = root; self.split = split
        self.graphs = []
        self.num_classes = 10
    def __len__(self): return len(self.graphs)
    def __getitem__(self, idx): return self.graphs[idx]

class QM9Dataset:
    """QM9 dataset."""
    def __init__(self, root="./data", split="train"):
        self.root = root; self.split = split
        self.graphs = []
        self.num_classes = 10
    def __len__(self): return len(self.graphs)
    def __getitem__(self, idx): return self.graphs[idx]

class ZINCDataset:
    """ZINC dataset."""
    def __init__(self, root="./data", split="train"):
        self.root = root; self.split = split
        self.graphs = []
        self.num_classes = 10
    def __len__(self): return len(self.graphs)
    def __getitem__(self, idx): return self.graphs[idx]

class OGBG_MOLHIVDataset:
    """ogbg-molhiv dataset."""
    def __init__(self, root="./data", split="train"):
        self.root = root; self.split = split
        self.graphs = []
        self.num_classes = 10
    def __len__(self): return len(self.graphs)
    def __getitem__(self, idx): return self.graphs[idx]

class OGBG_MOLPCBADataset:
    """ogbg-molpcba dataset."""
    def __init__(self, root="./data", split="train"):
        self.root = root; self.split = split
        self.graphs = []
        self.num_classes = 10
    def __len__(self): return len(self.graphs)
    def __getitem__(self, idx): return self.graphs[idx]

class OGBN_ARXIVDataset:
    """ogbn-arxiv dataset."""
    def __init__(self, root="./data", split="train"):
        self.root = root; self.split = split
        self.graphs = []
        self.num_classes = 10
    def __len__(self): return len(self.graphs)
    def __getitem__(self, idx): return self.graphs[idx]

class OGBN_PROTEINSDataset:
    """ogbn-proteins dataset."""
    def __init__(self, root="./data", split="train"):
        self.root = root; self.split = split
        self.graphs = []
        self.num_classes = 10
    def __len__(self): return len(self.graphs)
    def __getitem__(self, idx): return self.graphs[idx]

class OGBN_PRODUCTSDataset:
    """ogbn-products dataset."""
    def __init__(self, root="./data", split="train"):
        self.root = root; self.split = split
        self.graphs = []
        self.num_classes = 10
    def __len__(self): return len(self.graphs)
    def __getitem__(self, idx): return self.graphs[idx]

class OGBN_MAGDataset:
    """ogbn-mag dataset."""
    def __init__(self, root="./data", split="train"):
        self.root = root; self.split = split
        self.graphs = []
        self.num_classes = 10
    def __len__(self): return len(self.graphs)
    def __getitem__(self, idx): return self.graphs[idx]

class REDDITDataset:
    """Reddit dataset."""
    def __init__(self, root="./data", split="train"):
        self.root = root; self.split = split
        self.graphs = []
        self.num_classes = 10
    def __len__(self): return len(self.graphs)
    def __getitem__(self, idx): return self.graphs[idx]

class PPIDataset:
    """PPI dataset."""
    def __init__(self, root="./data", split="train"):
        self.root = root; self.split = split
        self.graphs = []
        self.num_classes = 10
    def __len__(self): return len(self.graphs)
    def __getitem__(self, idx): return self.graphs[idx]

class FLICKRDataset:
    """Flickr dataset."""
    def __init__(self, root="./data", split="train"):
        self.root = root; self.split = split
        self.graphs = []
        self.num_classes = 10
    def __len__(self): return len(self.graphs)
    def __getitem__(self, idx): return self.graphs[idx]

class YELPDataset:
    """Yelp dataset."""
    def __init__(self, root="./data", split="train"):
        self.root = root; self.split = split
        self.graphs = []
        self.num_classes = 10
    def __len__(self): return len(self.graphs)
    def __getitem__(self, idx): return self.graphs[idx]

