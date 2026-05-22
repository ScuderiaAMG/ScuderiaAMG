"""CNN Dataset — reuses pinn raw-data pipeline, adds stage & RUL labels.

Each sample:
    ic_curve: (1, 128)  — raw IC curve for 1D-CNN input
    stage:    int [0..3] — aging stage I→IV
    rul:      float     — normalised remaining useful cycles ∈ [0, 1]
    soh:      float     — ground-truth SOH (for metrics)
    cell_id:  int       — cell identifier (for per-cell RUL lookup)
    cycle:    int       — cycle index
"""

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader, random_split
from pathlib import Path
import sys
import pickle


def _ensure_pinn_on_path():
    """Make pinn package importable from sibling cnn directory."""
    parent_dir = str(Path(__file__).resolve().parent.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)


# ============================================================
# Label builders
# ============================================================

def soh_to_stage(soh: np.ndarray, thresholds) -> np.ndarray:
    """Map SOH values to aging stages.

    Stage I:   formation     SOH >= 0.88
    Stage II:  stable        SOH >= 0.78
    Stage III: accelerated   SOH >= 0.68
    Stage IV:  end-of-life   SOH <  0.68
    """
    stages = np.full_like(soh, 3, dtype=np.int64)  # default: stage IV
    stages[soh >= thresholds.accelerated] = 2
    stages[soh >= thresholds.stable] = 1
    stages[soh >= thresholds.formation] = 0
    return stages


def compute_rul(raw_data: dict, cfg) -> np.ndarray:
    """Compute normalised RUL per sample.

    RUL_i = max(0, N_EOL - N_current) / N_EOL
    where N_EOL = first cycle of that cell where SOH drops below threshold.
    """
    cell_ids = np.asarray(raw_data["cell_id"])
    soh = np.asarray(raw_data["soh"])
    cycles = np.asarray(raw_data["cycle"])
    threshold = cfg.data.eol_soh_threshold

    rul = np.zeros(len(soh), dtype=np.float32)

    for cid in np.unique(cell_ids):
        mask = cell_ids == cid
        cyc_cell = cycles[mask]
        soh_cell = soh[mask]
        sort_idx = np.argsort(cyc_cell)
        cyc_sorted = cyc_cell[sort_idx]
        soh_sorted = soh_cell[sort_idx]

        below = np.where(soh_sorted < threshold)[0]
        if len(below) == 0:
            eol_cycle = cyc_sorted[-1]
        else:
            eol_cycle = cyc_sorted[below[0]]

        raw_rul = np.maximum(0, eol_cycle - cyc_sorted).astype(np.float32)
        norm_rul = raw_rul / max(eol_cycle, 1)
        rul[mask] = norm_rul[sort_idx.argsort()]  # un-sort back to original order

    return rul


# ============================================================
# Dataset
# ============================================================

class CNNDataset(Dataset):
    """Dataset for 1D-CNN: (ic_curve, stage_label, rul_target, soh, cell_id, cycle)."""

    def __init__(
        self,
        ic_curves: np.ndarray,   # (N, 128)
        stages: np.ndarray,       # (N,) int
        rul: np.ndarray,          # (N,) float
        soh: np.ndarray,          # (N,) float
        cell_ids: np.ndarray,     # (N,) int
        cycles: np.ndarray,       # (N,) int
    ):
        self.ic = torch.as_tensor(ic_curves, dtype=torch.float32).unsqueeze(1)  # (N, 1, 128)
        self.stage = torch.as_tensor(stages, dtype=torch.long)
        self.rul = torch.as_tensor(rul, dtype=torch.float32).unsqueeze(-1)
        self.soh = torch.as_tensor(soh, dtype=torch.float32).unsqueeze(-1)
        self.cell_ids = torch.as_tensor(cell_ids, dtype=torch.long)
        self.cycles = torch.as_tensor(cycles, dtype=torch.float32).unsqueeze(-1)

    def __len__(self):
        return len(self.ic)

    def __getitem__(self, idx):
        return (
            self.ic[idx],
            self.stage[idx],
            self.rul[idx],
            self.soh[idx],
            self.cell_ids[idx],
            self.cycles[idx],
        )


# ============================================================
# Data loading — reuse pinn pipeline
# ============================================================

def load_cnn_data(cfg):
    """Load raw data via pinn pipeline, then build CNN-specific labels.

    Returns:
        ic_curves: (N, 128) float32
        stages:    (N,) int64
        rul:       (N,) float32
        soh:       (N,) float32
        cell_ids:  (N,) int64
        cycles:    (N,) int64
    """
    _ensure_pinn_on_path()
    from pinn.config import Config as PinnConfig
    from pinn.dataset import load_all_data

    pinn_cfg = PinnConfig()
    pinn_cfg.data.ic_curve_pts = cfg.data.ic_curve_pts
    pinn_cfg.data_cache = Path(__file__).resolve().parent.parent / "pinn" / "cache"
    pinn_cfg.data_cache.mkdir(parents=True, exist_ok=True)

    raw = load_all_data(pinn_cfg)

    if len(raw["soh"]) == 0:
        raise RuntimeError("无有效数据! 请下载 NASA/CALCE 数据集或允许合成数据生成")

    ic = raw["ic"].astype(np.float32)
    if ic.ndim == 1:
        ic = ic.reshape(1, -1)
    ic = ic[:, :cfg.data.ic_curve_pts]
    if ic.shape[1] < cfg.data.ic_curve_pts:
        pad = np.zeros((ic.shape[0], cfg.data.ic_curve_pts - ic.shape[1]), dtype=np.float32)
        ic = np.concatenate([ic, pad], axis=1)
    ic = np.nan_to_num(ic, nan=0.0, posinf=0.0, neginf=0.0)

    soh = raw["soh"].astype(np.float32)
    stages = soh_to_stage(soh, cfg.thresholds)
    rul = compute_rul(raw, cfg)
    cell_ids = raw["cell_id"].astype(np.int64)
    cycles = raw["cycle"].astype(np.int64)

    # Print label distribution
    unique, counts = np.unique(stages, return_counts=True)
    stage_names = {0: "I-formation", 1: "II-stable", 2: "III-accelerated", 3: "IV-EOL"}
    print("Stage distribution:")
    for s, c in zip(unique, counts):
        print(f"  {stage_names.get(s, s)}: {c} ({100*c/len(stages):.1f}%)")
    print(f"  RUL ∈ [{rul.min():.4f}, {rul.max():.4f}], μ={rul.mean():.4f}")

    return ic, stages, rul, soh, cell_ids, cycles


# ============================================================
# Dataloader factory
# ============================================================

def create_dataloaders(cfg, raw_data: dict | None = None):
    """Build train/val/test dataloaders for CNN.

    Args:
        cfg: CNN Config object
        raw_data: if None, auto-load via pinn pipeline

    Returns:
        dl_train, dl_val, dl_test
    """
    # Build a temporary PINN-style config for data loading compatibility
    _ensure_pinn_on_path()
    from pinn.config import Config as PinnConfig, DataConfig as PinnDataConfig

    pinn_cfg = PinnConfig()
    pinn_cfg.data.ic_curve_pts = cfg.data.ic_curve_pts
    pinn_cfg.data.train_ratio = cfg.data.train_ratio
    pinn_cfg.data.val_ratio = cfg.data.val_ratio
    pinn_cfg.data.test_ratio = cfg.data.test_ratio
    pinn_cfg.seed = cfg.seed

    # Create directories
    data_cache = Path(__file__).resolve().parent.parent / "pinn" / "cache"
    data_cache.mkdir(parents=True, exist_ok=True)
    pinn_cfg.data_cache = data_cache

    # Load raw data through pinn pipeline
    if raw_data is None:
        from pinn.dataset import load_all_data
        raw_data = load_all_data(pinn_cfg)

    if len(raw_data["soh"]) == 0:
        raise RuntimeError("无有效数据!")

    ic = raw_data["ic"].astype(np.float32)
    if ic.ndim == 1:
        ic = ic.reshape(1, -1)
    ic = ic[:, :cfg.data.ic_curve_pts]
    if ic.shape[1] < cfg.data.ic_curve_pts:
        pad = np.zeros((ic.shape[0], cfg.data.ic_curve_pts - ic.shape[1]), dtype=np.float32)
        ic = np.concatenate([ic, pad], axis=1)
    ic = np.nan_to_num(ic, nan=0.0, posinf=0.0, neginf=0.0)

    soh = raw_data["soh"].astype(np.float32)
    stages = soh_to_stage(soh, cfg.thresholds)
    rul = compute_rul(raw_data, cfg)
    cell_ids = raw_data["cell_id"].astype(np.int64)
    cycles = raw_data["cycle"].astype(np.int64)

    N = len(ic)
    n_train = int(N * cfg.data.train_ratio)
    n_val = int(N * cfg.data.val_ratio)
    n_test = N - n_train - n_val

    ds = CNNDataset(ic, stages, rul, soh, cell_ids, cycles)
    ds_train, ds_val, ds_test = random_split(
        ds, [n_train, n_val, n_test],
        generator=torch.Generator().manual_seed(cfg.seed),
    )

    tcfg = cfg.training

    def _seed_worker(worker_id):
        import random
        random.seed(cfg.seed + worker_id)

    dl_train = DataLoader(ds_train, batch_size=tcfg.batch_size,
                          shuffle=True, num_workers=tcfg.num_workers,
                          pin_memory=True, drop_last=True,
                          worker_init_fn=_seed_worker)
    dl_val = DataLoader(ds_val, batch_size=tcfg.batch_size * 2,
                        shuffle=False, num_workers=tcfg.num_workers,
                        pin_memory=True)
    dl_test = DataLoader(ds_test, batch_size=tcfg.batch_size * 2,
                         shuffle=False, num_workers=tcfg.num_workers,
                         pin_memory=True)

    # Print data stats
    unique, counts = np.unique(stages, return_counts=True)
    stage_names = {0: "I-formation", 1: "II-stable", 2: "III-accelerated", 3: "IV-EOL"}
    print(f"\nTrain: {n_train}  Val: {n_val}  Test: {n_test}")
    for s, c in zip(unique, counts):
        print(f"  {stage_names.get(s, s)}: {c} ({100*c/len(stages):.1f}%)")
    print(f"  RUL ∈ [{rul.min():.4f}, {rul.max():.4f}], μ={rul.mean():.4f}\n")

    return dl_train, dl_val, dl_test
