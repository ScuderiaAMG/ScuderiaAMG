"""CNN Dataset — 3-stage labels, dual-channel IC input, augmentation, cell-based split.

Each sample:
    ic_dual:   (2, 128)  — ch1: IC curve, ch2: IC gradient
    stage:     int [0..2] — 0=healthy(SOH≥0.82), 1=degrading(0.82>SOH≥0.70), 2=EOL
    rul:       float     — normalised remaining useful cycles ∈ [0, 1]
    soh:       float     — ground-truth SOH
    cell_id:   int       — cell identifier
    cycle:     int       — cycle index
"""

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
import sys
import pickle


def _ensure_pinn_on_path():
    parent_dir = str(Path(__file__).resolve().parent.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)


# ============================================================
# Label builders (3-stage)
# ============================================================

def soh_to_stage(soh: np.ndarray, thresholds) -> np.ndarray:
    """3-stage: healthy (SOH>=0.82), degrading (0.82>SOH>=0.70), EOL (SOH<0.70)."""
    stages = np.full_like(soh, 2, dtype=np.int64)  # default: EOL
    stages[soh >= thresholds.degrading] = 1         # degrading
    stages[soh >= thresholds.healthy] = 0           # healthy
    return stages


def compute_rul(raw_data: dict, eol_soh_threshold: float) -> np.ndarray:
    cell_ids = np.asarray(raw_data["cell_id"])
    soh = np.asarray(raw_data["soh"])
    cycles = np.asarray(raw_data["cycle"])
    threshold = eol_soh_threshold
    rul = np.zeros(len(soh), dtype=np.float32)

    for cid in np.unique(cell_ids):
        mask = cell_ids == cid
        cyc_cell = cycles[mask]
        soh_cell = soh[mask]
        sort_idx = np.argsort(cyc_cell)
        cyc_sorted = cyc_cell[sort_idx]
        soh_sorted = soh_cell[sort_idx]

        below = np.where(soh_sorted < threshold)[0]
        eol_cycle = cyc_sorted[below[0]] if len(below) > 0 else cyc_sorted[-1]
        raw_rul = np.maximum(0, eol_cycle - cyc_sorted).astype(np.float32)
        norm_rul = raw_rul / max(eol_cycle, 1)
        rul[mask] = norm_rul[sort_idx.argsort()]
    return rul


# ============================================================
# IC curve helpers
# ============================================================

def compute_ic_gradient(ic: np.ndarray) -> np.ndarray:
    grad = np.gradient(ic, axis=1)
    abs_max = np.abs(grad).max(axis=1, keepdims=True)
    mask = abs_max > 1e-6
    grad[mask.squeeze()] /= abs_max[mask.squeeze()]
    return grad


def filter_valid_curves(ic: np.ndarray) -> np.ndarray:
    N = len(ic)
    valid = np.ones(N, dtype=bool)
    abs_max = np.abs(ic).max(axis=1)
    curve_std = np.std(ic, axis=1)
    valid &= abs_max > 0.001
    valid &= abs_max < 1e6
    valid &= curve_std > 0.0001
    return valid


def augment_ic(ic: np.ndarray, cfg) -> np.ndarray:
    aug = cfg.augment
    rng = np.random.default_rng()
    ic_aug = ic.copy()
    ic_aug += rng.normal(0, aug.gaussian_noise_std, size=ic_aug.shape).astype(np.float32)
    scale = rng.uniform(*aug.scale_range)
    ic_aug *= scale
    shift = rng.integers(-aug.shift_max, aug.shift_max + 1)
    if shift > 0:
        ic_aug[:, shift:] = ic_aug[:, :-shift]
        ic_aug[:, :shift] = 0
    elif shift < 0:
        shift = -shift
        ic_aug[:, :-shift] = ic_aug[:, shift:]
        ic_aug[:, -shift:] = 0
    return ic_aug


# ============================================================
# Dataset
# ============================================================

class CNNDataset(Dataset):
    """Dual-channel IC dataset with optional augmentation."""

    def __init__(self, ic_curves, ic_grads, stages, rul, soh, cell_ids, cycles,
                 augment=False, aug_cfg=None):
        self.ic = ic_curves
        self.ic_grad = ic_grads
        self.stage = torch.as_tensor(stages, dtype=torch.long)
        self.rul = torch.as_tensor(rul, dtype=torch.float32).unsqueeze(-1)
        self.soh = torch.as_tensor(soh, dtype=torch.float32).unsqueeze(-1)
        self.cell_ids = torch.as_tensor(cell_ids, dtype=torch.long)
        self.cycles = torch.as_tensor(cycles, dtype=torch.float32).unsqueeze(-1)
        self.augment = augment
        self.aug_cfg = aug_cfg

    def __len__(self):
        return len(self.stage)

    def __getitem__(self, idx):
        ic = self.ic[idx:idx + 1] if self.ic.ndim == 2 else self.ic[idx]
        ig = self.ic_grad[idx:idx + 1] if self.ic_grad.ndim == 2 else self.ic_grad[idx]

        if self.augment and self.aug_cfg is not None:
            ic = augment_ic(ic.reshape(1, -1), self.aug_cfg).flatten()

        ic_dual = torch.as_tensor(
            np.stack([ic.reshape(-1), ig.reshape(-1)]), dtype=torch.float32
        )
        return (ic_dual, self.stage[idx], self.rul[idx],
                self.soh[idx], self.cell_ids[idx], self.cycles[idx])


# ============================================================
# Cell-based split
# ============================================================

def _cell_split(cell_ids, train_r, val_r, seed):
    unique_cells = np.unique(cell_ids)
    rng = np.random.default_rng(seed)
    perm = rng.permutation(unique_cells)
    n = len(perm)

    if n < 3:
        return (np.ones(len(cell_ids), dtype=bool),
                np.zeros(len(cell_ids), dtype=bool),
                np.zeros(len(cell_ids), dtype=bool))

    n_train = max(1, int(n * train_r))
    n_val = max(1, int(n * val_r))
    n_test = max(1, n - n_train - n_val)
    if n_train + n_val + n_test > n:
        n_train = n - n_val - n_test
        if n_train < 1:
            n_val = max(1, n - 2)
            n_train = 1
            n_test = n - n_train - n_val

    train_cells = set(perm[:n_train])
    val_cells = set(perm[n_train:n_train + n_val])
    test_cells = set(perm[n_train + n_val:n_train + n_val + n_test])
    return (
        np.array([cid in train_cells for cid in cell_ids]),
        np.array([cid in val_cells for cid in cell_ids]),
        np.array([cid in test_cells for cid in cell_ids]),
    )


# ============================================================
# Main pipeline
# ============================================================

def create_dataloaders(cfg, raw_data=None):
    _ensure_pinn_on_path()
    from pinn.config import Config as PinnConfig
    from pinn.dataset import load_all_data

    pinn_cfg = PinnConfig()
    pinn_cfg.data.ic_curve_pts = cfg.data.ic_curve_pts
    pinn_cfg.data.train_ratio = cfg.data.train_ratio
    pinn_cfg.data.val_ratio = cfg.data.val_ratio
    pinn_cfg.data.test_ratio = cfg.data.test_ratio
    pinn_cfg.seed = cfg.seed

    data_cache = Path(__file__).resolve().parent.parent / "pinn" / "cache"
    data_cache.mkdir(parents=True, exist_ok=True)
    pinn_cfg.data_cache = data_cache

    if raw_data is None:
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

    # Quality filter
    valid = filter_valid_curves(ic)
    n_rejected = (~valid).sum()
    if n_rejected > 0:
        print(f"  [质量过滤] 剔除 {n_rejected} 条无效IC曲线 ({100*n_rejected/len(ic):.1f}%)")
        ic = ic[valid]
        for key in ("soh", "cell_id", "cycle", "dv_start", "capacity_meas"):
            if key in raw_data:
                raw_data[key] = raw_data[key][valid]

    # Gradient channel
    ic_grad = compute_ic_gradient(ic)

    # Standardisation
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler().fit(ic)
    ic = scaler.transform(ic).astype(np.float32)
    ic = np.clip(ic, -5.0, 5.0)
    ic = np.nan_to_num(ic, nan=0.0, posinf=5.0, neginf=-5.0)
    ig_scaler = StandardScaler().fit(ic_grad)
    ic_grad = ig_scaler.transform(ic_grad).astype(np.float32)
    ic_grad = np.clip(ic_grad, -5.0, 5.0)
    ic_grad = np.nan_to_num(ic_grad, nan=0.0, posinf=5.0, neginf=-5.0)

    ckpt_dir = Path(__file__).resolve().parent / "checkpoints"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    with open(ckpt_dir / "ic_scaler.pkl", "wb") as f:
        pickle.dump({"ic_scaler": scaler, "ig_scaler": ig_scaler}, f)
    print(f"IC after norm: [{ic.min():.4f}, {ic.max():.4f}], μ={ic.mean():.4f}")

    # Labels (3-stage)
    soh = raw_data["soh"].astype(np.float32)
    stages = soh_to_stage(soh, cfg.thresholds)
    rul = compute_rul(raw_data, cfg.data.eol_soh_threshold)
    cell_ids = raw_data["cell_id"].astype(np.int64)
    cycles = raw_data["cycle"].astype(np.int64)

    # Split
    train_mask, val_mask, test_mask = _cell_split(cell_ids, cfg.data.train_ratio,
                                                   cfg.data.val_ratio, cfg.seed)

    ds_train = CNNDataset(ic[train_mask], ic_grad[train_mask],
                           stages[train_mask], rul[train_mask],
                           soh[train_mask], cell_ids[train_mask], cycles[train_mask],
                           augment=True, aug_cfg=cfg)
    ds_val = CNNDataset(ic[val_mask], ic_grad[val_mask],
                         stages[val_mask], rul[val_mask],
                         soh[val_mask], cell_ids[val_mask], cycles[val_mask],
                         augment=False)
    ds_test = CNNDataset(ic[test_mask], ic_grad[test_mask],
                          stages[test_mask], rul[test_mask],
                          soh[test_mask], cell_ids[test_mask], cycles[test_mask],
                          augment=False)

    n_train, n_val, n_test = len(ds_train), len(ds_val), len(ds_test)
    print(f"\nTrain: {n_train} ({n_train*100/(n_train+n_val+n_test):.0f}%)  "
          f"Val: {n_val}  Test: {n_test}")
    print(f"  Cells — train: {len(set(cell_ids[train_mask]))}, "
          f"val: {len(set(cell_ids[val_mask]))}, test: {len(set(cell_ids[test_mask]))}")

    for split_name, ds in [("Train", ds_train), ("Val", ds_val), ("Test", ds_test)]:
        uniq, cnt = np.unique(ds.stage.numpy(), return_counts=True)
        labels_str = ", ".join(f"{['H','D','EOL'][s]}={c}" for s, c in zip(uniq, cnt))
        print(f"  {split_name}: {labels_str}")
    print(f"  RUL ∈ [{rul.min():.4f}, {rul.max():.4f}], μ={rul.mean():.4f}")

    # Class weights
    full_weights = np.ones(3, dtype=np.float32) * 1e-6
    train_stages = stages[train_mask]
    unique_s, counts_s = np.unique(train_stages, return_counts=True)
    for s, c in zip(unique_s, counts_s):
        full_weights[s] = 1.0 / max(c, 1)
    full_weights /= full_weights.sum()
    cls_weights = torch.as_tensor(full_weights, dtype=torch.float32)
    print(f"  Class weights: {dict(zip(['H','D','EOL'], full_weights.round(4)))}")

    tcfg = cfg.training
    def _seed_worker(worker_id):
        import random
        random.seed(cfg.seed + worker_id)

    bs_train = min(tcfg.batch_size, max(4, len(ds_train) // 2))
    bs_val = min(tcfg.batch_size * 2, max(4, len(ds_val)))
    bs_test = min(tcfg.batch_size * 2, max(4, len(ds_test)))
    drop_last = len(ds_train) >= tcfg.batch_size

    dl_train = DataLoader(ds_train, batch_size=bs_train, shuffle=True,
                          num_workers=tcfg.num_workers, pin_memory=True,
                          drop_last=drop_last, worker_init_fn=_seed_worker)
    dl_val = DataLoader(ds_val, batch_size=bs_val if len(ds_val) > 0 else 4,
                        shuffle=False, num_workers=tcfg.num_workers, pin_memory=True)
    dl_test = DataLoader(ds_test, batch_size=bs_test if len(ds_test) > 0 else 4,
                         shuffle=False, num_workers=tcfg.num_workers, pin_memory=True)

    return dl_train, dl_val, dl_test, cls_weights
