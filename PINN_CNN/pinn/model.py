"""PINN model: compact MLP with residual skip for SOH regression.

Architecture:  ~25K parameters, int8-quantizable, A55-inferable in <15 ms.
"""
import torch
import torch.nn as nn


class Swish(nn.Module):
    """Swish activation — smoother gradients than ReLU, good for physics-informed."""

    def forward(self, x):
        return x * torch.sigmoid(x)


def _activation(name: str) -> nn.Module:
    return {"gelu": nn.GELU(), "silu": nn.SiLU(), "swish": Swish()}[name.lower()]


class ResidualBlock(nn.Module):
    """FC → Norm → Act → FC → Norm → Act  with residual skip."""

    def __init__(self, dim: int, dropout: float, activation: str):
        super().__init__()
        self.fc1 = nn.Linear(dim, dim)
        self.norm1 = nn.LayerNorm(dim)
        self.fc2 = nn.Linear(dim, dim)
        self.norm2 = nn.LayerNorm(dim)
        self.act = _activation(activation)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        residual = x
        x = self.dropout(self.act(self.norm1(self.fc1(x))))
        x = self.norm2(self.fc2(x))
        return self.act(x + residual)


class BatteryPINN(nn.Module):
    """Physics-informed MLP for battery SOH estimation.

    Input:  [IC curve (128), temp, cycle_norm, dv_proxy, cap_norm]  → 132-d
    Output: SOH ∈ [0, 1]
    """

    def __init__(self, config):
        super().__init__()
        cfg = config.model
        dims = [cfg.input_dim] + list(cfg.hidden_dims)

        # Input projection
        layers = []
        for i in range(len(dims) - 1):
            layers.append(nn.Linear(dims[i], dims[i + 1]))
            if i < len(dims) - 2:  # no activation after last hidden
                layers.append(nn.LayerNorm(dims[i + 1]))
                layers.append(_activation(cfg.activation))
                layers.append(nn.Dropout(cfg.dropout))
        self.encoder = nn.Sequential(*layers)

        # Residual bottleneck
        hidden_dim = dims[-1]
        self.res_block = ResidualBlock(hidden_dim, cfg.dropout, cfg.activation)

        # Output head
        self.head = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.LayerNorm(32),
            _activation(cfg.activation),
            nn.Linear(32, cfg.output_dim),
            nn.Sigmoid(),
        )

        # Aux head: predict resistance proxy (for physics-loss warm-start)
        self.aux_resistance = nn.Linear(hidden_dim, 1)

        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_normal_(m.weight, mode='fan_in', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    def forward(self, x, return_features: bool = False):
        """Forward pass.

        Args:
            x: (B, 132) input tensor
            return_features: if True, return (soh, r_proxy, features) for physics loss

        Returns:
            soh:       (B, 1) SOH ∈ [0,1]
            r_proxy:   (B, 1) resistance proxy
            features:  (B, 64) latent features (only if return_features=True)
        """
        features = self.encoder(x)
        features = self.res_block(features)
        soh = self.head[0](features)          # FC → 32
        soh = self.head[1](soh)              # LayerNorm
        soh = self.head[2](soh)              # Activation
        soh = self.head[3](soh)              # FC → 1
        soh = self.head[4](soh)              # Sigmoid
        r_proxy = self.aux_resistance(features)

        if return_features:
            return soh, r_proxy, features
        return soh, r_proxy
