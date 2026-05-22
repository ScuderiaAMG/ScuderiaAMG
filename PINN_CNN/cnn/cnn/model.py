"""Lightweight 1D-CNN for battery aging stage classification & RUL prediction.

Architecture: ~13K parameters, INT8-quantizable, A55-inferable in <10 ms.
Input:  IC curve (B, 1, 128) — raw 1D signal preserving spatial morphology.
Output: stage logits (B, 4) + RUL (B, 1).
"""
import torch
import torch.nn as nn


class ConvBlock(nn.Module):
    """Conv1D → BatchNorm → GELU → MaxPool1d → Dropout."""

    def __init__(self, in_ch: int, out_ch: int, kernel: int, dropout: float):
        super().__init__()
        self.conv = nn.Conv1d(in_ch, out_ch, kernel, stride=1,
                              padding=kernel // 2, bias=False)
        self.bn = nn.BatchNorm1d(out_ch)
        self.act = nn.GELU()
        self.pool = nn.MaxPool1d(kernel_size=2)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        x = self.conv(x)
        x = self.bn(x)
        x = self.act(x)
        x = self.pool(x)
        x = self.dropout(x)
        return x


class BatteryCNN(nn.Module):
    """1D-CNN for multi-task battery aging assessment.

    Input:  (B, 1, 128)  IC curve
    Output: stage_logits (B, 4),  rul (B, 1)
    """

    def __init__(self, config):
        super().__init__()
        cfg = config.model
        filters = cfg.conv_filters
        kernels = cfg.conv_kernels

        # ---- Convolutional backbone ----
        blocks = []
        in_ch = cfg.in_channels
        for f, k in zip(filters, kernels):
            blocks.append(ConvBlock(in_ch, f, k, cfg.dropout))
            in_ch = f
        self.backbone = nn.Sequential(*blocks)

        # ---- Global pooling ----
        self.gap = nn.AdaptiveAvgPool1d(1)

        # ---- Classification head (aging stages I-IV) ----
        self.cls_head = nn.Sequential(
            nn.Linear(filters[-1], cfg.hidden_dim),
            nn.GELU(),
            nn.Dropout(cfg.dropout),
            nn.Linear(cfg.hidden_dim, cfg.num_stages),
        )

        # ---- RUL regression head ----
        self.rul_head = nn.Sequential(
            nn.Linear(filters[-1], cfg.hidden_dim),
            nn.GELU(),
            nn.Dropout(cfg.dropout),
            nn.Linear(cfg.hidden_dim, cfg.rul_output_dim),
        )

        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv1d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm1d):
                nn.init.ones_(m.weight)
                nn.init.zeros_(m.bias)
            elif isinstance(m, nn.Linear):
                nn.init.kaiming_normal_(m.weight, mode='fan_in', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    def forward(self, x, return_features: bool = False):
        """Forward pass.

        Args:
            x: (B, 1, 128) IC curve tensor
            return_features: if True, also return latent features

        Returns:
            stage_logits: (B, 4) unnormalised class scores
            rul:         (B, 1) normalised remaining cycles ∈ [0, 1]
            features:    (B, 64) latent features (only if return_features=True)
        """
        feats = self.backbone(x)         # (B, 64, 16)
        feats = self.gap(feats)          # (B, 64, 1)
        feats = feats.squeeze(-1)        # (B, 64)

        stage_logits = self.cls_head(feats)
        rul = self.rul_head(feats)

        if return_features:
            return stage_logits, rul, feats
        return stage_logits, rul
