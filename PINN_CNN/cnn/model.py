"""Slim residual 1D-CNN — 3-stage battery aging classification + RUL.

Architecture: ~40K params, INT8 < 40 KB, A55 < 15 ms.
Input:  (B, 2, 128)  ch1: IC curve, ch2: IC gradient
Output: stage logits (B, 3) + RUL (B, 1)

Stages: 0=healthy(SOH≥0.82), 1=degrading(0.82>SOH≥0.70), 2=EOL(SOH<0.70)
"""
import torch
import torch.nn as nn


class ResidualBlock(nn.Module):
    """Conv1D→BN→GELU→Drop + Conv1D→BN, 1×1 shortcut if channels change."""

    def __init__(self, in_ch: int, out_ch: int, kernel: int, dropout: float):
        super().__init__()
        self.conv1 = nn.Conv1d(in_ch, out_ch, kernel, padding=kernel // 2, bias=False)
        self.bn1 = nn.BatchNorm1d(out_ch)
        self.act1 = nn.GELU()
        self.drop1 = nn.Dropout(dropout)

        self.conv2 = nn.Conv1d(out_ch, out_ch, kernel, padding=kernel // 2, bias=False)
        self.bn2 = nn.BatchNorm1d(out_ch)
        self.act2 = nn.GELU()
        self.drop2 = nn.Dropout(dropout * 0.5)

        self.shortcut = None
        if in_ch != out_ch:
            self.shortcut = nn.Sequential(
                nn.Conv1d(in_ch, out_ch, 1, bias=False),
                nn.BatchNorm1d(out_ch),
            )
        self.pool = nn.MaxPool1d(kernel_size=2)

    def forward(self, x):
        residual = x if self.shortcut is None else self.shortcut(x)
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.act1(out)
        out = self.drop1(out)
        out = self.conv2(out)
        out = self.bn2(out)
        out += residual
        out = self.act2(out)
        out = self.drop2(out)
        return self.pool(out)


class BatteryCNN(nn.Module):
    """Slim residual CNN for 3-stage aging + RUL."""

    def __init__(self, config):
        super().__init__()
        cfg = config.model
        filters = cfg.conv_filters
        kernels = cfg.conv_kernels

        # Stem: fast down-sample
        self.stem = nn.Sequential(
            nn.Conv1d(cfg.in_channels, filters[0], kernel_size=7, stride=2,
                      padding=3, bias=False),
            nn.BatchNorm1d(filters[0]),
            nn.GELU(),
        )
        # After stem: (B, 16, 64)

        # Residual body
        blocks = []
        in_ch = filters[0]
        for f, k in zip(filters, kernels):
            blocks.append(ResidualBlock(in_ch, f, k, cfg.dropout))
            in_ch = f
        self.body = nn.Sequential(*blocks)
        # After body: (B, 48, 8)

        # Global pooling
        self.gap = nn.AdaptiveAvgPool1d(1)
        head_in = filters[-1]  # 48

        # Classification head
        h = cfg.head_hidden
        self.cls_head = nn.Sequential(
            nn.Linear(head_in, h * 2),
            nn.GELU(),
            nn.Dropout(cfg.dropout),
            nn.Linear(h * 2, h),
            nn.GELU(),
            nn.Dropout(cfg.dropout * 0.5),
            nn.Linear(h, cfg.num_stages),
        )

        # RUL regression head
        self.rul_head = nn.Sequential(
            nn.Linear(head_in, h * 2),
            nn.GELU(),
            nn.Dropout(cfg.dropout),
            nn.Linear(h * 2, h),
            nn.GELU(),
            nn.Dropout(cfg.dropout * 0.5),
            nn.Linear(h, cfg.rul_output_dim),
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
        x = self.stem(x)
        feats = self.body(x)
        pooled = self.gap(feats).squeeze(-1)

        stage_logits = self.cls_head(pooled)
        rul = self.rul_head(pooled)

        if return_features:
            return stage_logits, rul, pooled
        return stage_logits, rul
