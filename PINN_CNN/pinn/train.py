"""PINN training entry-point for battery SOH estimation.

Target:  RTX 4060 Laptop GPU 8 GB  |  CPU: i7-14700HX  |  RAM: 64 GB
Usage:  python -m pinn.train
"""
import torch
import torch.nn as nn
from torch.utils.tensorboard import SummaryWriter
from pathlib import Path
import time
import sys
import math
import numpy as np

from .config import Config
from .model import BatteryPINN
from .physics import PhysicsLoss
from .dataset import create_dataloaders


def _format_time(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}m{secs:02d}s"


def train(cfg: Config | None = None):
    if cfg is None:
        cfg = Config()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    if device.type == "cuda":
        print(f"  GPU: {torch.cuda.get_device_name(0)}")
        print(f"  VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        torch.backends.cudnn.benchmark = True

    # ---- data ----
    dl_train, dl_val, dl_test, scaler = create_dataloaders(cfg)

    # Print scaler stats for diagnosis
    print(f"Scaler mean:  {scaler.mean_}")
    print(f"Scaler scale: {scaler.scale_}")
    for i, (name, m, s) in enumerate(zip(
        ["temp", "log_cycle", "dv_start", "capacity_meas"],
        scaler.mean_, scaler.scale_
    )):
        print(f"  {name}: μ={m:.6f}, σ={s:.6f}")

    # Validate data: check for NaN/Inf in first batch
    x0, soh0, dv0, _, _ = next(iter(dl_train))
    for name, t in [("features", x0), ("soh", soh0), ("dv", dv0)]:
        if torch.isnan(t).any():
            raise RuntimeError(f"NaN detected in {name}! Check raw data / scaler.")
        if torch.isinf(t).any():
            raise RuntimeError(f"Inf detected in {name}! Check raw data / scaler.")
    # Clip extreme features to stabilise training
    extreme_mask = (x0 < -10) | (x0 > 10)
    n_extreme = extreme_mask.any(dim=1).sum().item()
    print(f"Data sanity OK — features ∈ [{x0.min():.4f}, {x0.max():.4f}], "
          f"SOH ∈ [{soh0.min():.4f}, {soh0.max():.4f}], "
          f"extreme samples: {n_extreme}/{x0.size(0)}")

    # ---- model ----
    model = BatteryPINN(cfg).to(device)
    physics_loss_fn = PhysicsLoss(cfg)

    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Model params: {total_params:,} total  |  {trainable_params:,} trainable")

    # ---- optimiser & scheduler ----
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=cfg.training.learning_rate,
        weight_decay=cfg.training.weight_decay,
    )
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=cfg.training.lr_factor,
        patience=cfg.training.lr_patience,
    )
    data_criterion = nn.MSELoss()
    scaler_amp = torch.amp.GradScaler('cuda', enabled=cfg.training.use_amp)
    use_amp = cfg.training.use_amp and device.type == 'cuda'

    # ---- checkpoint & logging ----
    cfg.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    cfg.log_dir.mkdir(parents=True, exist_ok=True)
    writer = SummaryWriter(cfg.log_dir)
    best_val_loss = float("inf")
    best_epoch = 0
    patience_counter = 0

    # ---- training loop ----
    print(f"\n{'='*60}")
    print(f"Training: {cfg.training.epochs} epochs  |  batch={cfg.training.batch_size}")
    print(f"Physics weights: ecm={cfg.physics.ecm_weight}  "
          f"smooth={cfg.physics.smoothness_weight}  mono={cfg.physics.monotonic_weight}")
    print(f"{'='*60}\n")

    t_start = time.perf_counter()

    nan_detected = False

    for epoch in range(1, cfg.training.epochs + 1):
        # ----- TRAIN -----
        model.train()
        total_data_loss = 0.0
        total_phys_loss = 0.0
        phys_components = {"phys_ecm": 0.0, "phys_smooth": 0.0, "phys_mono": 0.0}

        for batch_idx, (x, soh_true, dv_meas, cell_ids, cycles) in enumerate(dl_train):
            x = x.to(device)
            soh_true = soh_true.to(device)
            dv_meas = dv_meas.to(device)
            cell_ids = cell_ids.to(device)
            cycles = cycles.to(device)

            with torch.amp.autocast('cuda', enabled=use_amp):
                soh_pred, _r_proxy = model(x)
                loss_data = data_criterion(soh_pred, soh_true)
                loss_phys, phys_dict = physics_loss_fn(soh_pred, dv_meas, cell_ids, cycles)
                loss = loss_data + loss_phys

            # NaN detection — skip corrupted batches instead of crashing
            if torch.isnan(loss) or torch.isinf(loss):
                if not nan_detected:
                    nan_detected = True
                    nan_cols = torch.isnan(x).any(dim=0).nonzero(as_tuple=True)[0]
                    nan_col_names = []
                    ic_cols = []
                    aux_names = ["temp", "log_cycle", "dv_start", "capacity_meas"]
                    for col_idx in nan_cols.tolist():
                        if col_idx < 128:
                            ic_cols.append(col_idx)
                        else:
                            nan_col_names.append(aux_names[col_idx - 128])
                    print(f"\n  [NaN DETECTED] epoch {epoch}, batch {batch_idx}/{len(dl_train)}")
                    print(f"    NaN feature columns: IC indices={ic_cols[:5]}{'...' if len(ic_cols) > 5 else ''}, "
                          f"aux={nan_col_names}")
                    print(f"    soh_pred: min={soh_pred.min():.6f} max={soh_pred.max():.6f} "
                          f"mean={soh_pred.mean():.6f}")
                    print(f"    loss_data={loss_data.item():.6f}  loss_phys={loss_phys.item():.6f}")
                continue  # skip this batch

            optimizer.zero_grad(set_to_none=True)
            scaler_amp.scale(loss).backward()
            scaler_amp.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.training.grad_clip)
            scaler_amp.step(optimizer)
            scaler_amp.update()

            total_data_loss += loss_data.item()
            total_phys_loss += loss_phys.item()
            for k in phys_components:
                phys_components[k] += phys_dict[k]

        n_batches = len(dl_train)
        avg_data_loss = total_data_loss / n_batches
        avg_phys_loss = total_phys_loss / n_batches

        writer.add_scalar("train/data_loss", avg_data_loss, epoch)
        writer.add_scalar("train/phys_loss", avg_phys_loss, epoch)
        for k, v in phys_components.items():
            writer.add_scalar(f"train/{k}", v / n_batches, epoch)

        # ----- VALIDATION -----
        model.eval()
        val_data_loss = 0.0
        val_mae = 0.0
        n_val_samples = 0
        with torch.no_grad():
            for x, soh_true, dv_meas, cell_ids, cycles in dl_val:
                x = x.to(device)
                soh_true = soh_true.to(device)
                dv_meas = dv_meas.to(device)
                cell_ids = cell_ids.to(device)
                cycles = cycles.to(device)

                soh_pred, _ = model(x)
                loss_val = data_criterion(soh_pred, soh_true)

                val_data_loss += loss_val.item() * x.size(0)
                val_mae += (soh_pred - soh_true).abs().sum().item()
                n_val_samples += x.size(0)

        val_data_loss /= n_val_samples
        val_mae /= n_val_samples

        writer.add_scalar("val/data_loss", val_data_loss, epoch)
        writer.add_scalar("val/mae", val_mae, epoch)
        writer.add_scalar("lr", optimizer.param_groups[0]["lr"], epoch)

        scheduler.step(val_data_loss)

        # ----- checkpointing & early stop -----
        is_best = val_data_loss < best_val_loss
        # Always save first valid checkpoint; skip NaN losses
        if not math.isfinite(val_data_loss):
            pass  # skip NaN — don't save, don't count as best
        elif is_best:
            best_val_loss = val_data_loss
            best_epoch = epoch
            patience_counter = 0
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_loss": val_data_loss,
                "val_mae": val_mae,
                "scaler_mean": scaler.mean_.tolist(),
                "scaler_scale": scaler.scale_.tolist(),
            }, cfg.checkpoint_dir / "best_model.pt")
        else:
            patience_counter += 1

        # Log every 10 epochs or on improvement
        if epoch % 10 == 0 or is_best:
            elapsed = time.perf_counter() - t_start
            marker = " *" if is_best else ""
            print(
                f"Epoch {epoch:4d}/{cfg.training.epochs} | "
                f"data: {avg_data_loss:.6f} | phys: {avg_phys_loss:.6f} | "
                f"val_loss: {val_data_loss:.6f} | val_MAE: {val_mae:.6f} | "
                f"lr: {optimizer.param_groups[0]['lr']:.1e} | "
                f"{_format_time(elapsed)}{marker}"
            )

        if patience_counter >= cfg.training.early_stop_patience:
            print(f"\nEarly stop at epoch {epoch} (best: {best_epoch}, val_loss={best_val_loss:.6f})")
            break

    writer.close()

    # ---- final test evaluation ----
    print(f"\n{'='*60}")
    print("Loading best checkpoint for test evaluation ...")
    ckpt = torch.load(cfg.checkpoint_dir / "best_model.pt", map_location=device, weights_only=True)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()

    test_data_loss = 0.0
    test_mae = 0.0
    test_samples = 0
    soh_preds = []
    soh_trues = []

    with torch.no_grad():
        for x, soh_true, dv_meas, cell_ids, cycles in dl_test:
            x = x.to(device)
            soh_pred, _ = model(x)
            soh_preds.append(soh_pred.cpu().numpy())
            soh_trues.append(soh_true.cpu().numpy())
            loss_test = data_criterion(soh_pred, soh_true.to(device))
            test_data_loss += loss_test.item() * x.size(0)
            test_mae += (soh_pred - soh_true.to(device)).abs().sum().item()
            test_samples += x.size(0)

    test_data_loss /= test_samples
    test_mae /= test_samples

    soh_preds = np.concatenate(soh_preds).flatten()
    soh_trues = np.concatenate(soh_trues).flatten()
    rmse = np.sqrt(np.mean((soh_preds - soh_trues) ** 2))
    r2 = 1 - np.sum((soh_trues - soh_preds) ** 2) / np.sum((soh_trues - soh_trues.mean()) ** 2)

    print(f"Test Results:")
    print(f"  MSE:  {test_data_loss:.6f}")
    print(f"  MAE:  {test_mae:.6f}  ({test_mae*100:.2f}% SOH)")
    print(f"  RMSE: {rmse:.6f}  ({rmse*100:.2f}% SOH)")
    print(f"  R²:   {r2:.6f}")
    print(f"Best model: {cfg.checkpoint_dir / 'best_model.pt'}")

    return model, cfg


if __name__ == "__main__":
    train()
