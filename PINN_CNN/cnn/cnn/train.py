"""CNN multi-task training — aging stage classification + RUL regression.

Target: RTX 4060 Laptop GPU 8 GB  |  CPU: i7-14700HX  |  RAM: 64 GB
Usage:  python -m cnn.train
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
from .model import BatteryCNN
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
        vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"  VRAM: {vram:.1f} GB")
        torch.backends.cudnn.benchmark = True

    # ---- data ----
    dl_train, dl_val, dl_test = create_dataloaders(cfg)

    # Data sanity check
    ic0, st0, rul0, soh0, _, _ = next(iter(dl_train))
    for name, t in [("ic", ic0), ("stage", st0), ("rul", rul0), ("soh", soh0)]:
        if torch.isnan(t.float()).any():
            raise RuntimeError(f"NaN detected in {name}!")
        if torch.isinf(t.float()).any():
            raise RuntimeError(f"Inf detected in {name}!")
    print(f"Data sanity OK — IC ∈ [{ic0.min():.4f}, {ic0.max():.4f}], "
          f"RUL ∈ [{rul0.min():.4f}, {rul0.max():.4f}], "
          f"stages: {torch.unique(st0).tolist()}")

    # ---- model ----
    model = BatteryCNN(cfg).to(device)
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Model params: {total_params:,} total  |  {trainable_params:,} trainable")

    # ---- losses (multi-task) ----
    cls_criterion = nn.CrossEntropyLoss(label_smoothing=cfg.data.label_smoothing)
    rul_criterion = nn.MSELoss()

    cls_weight = cfg.training.cls_weight
    rul_weight = cfg.training.rul_weight

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
    print(f"Multi-task weights: cls={cls_weight}  rul={rul_weight}")
    print(f"Label smoothing: {cfg.data.label_smoothing}")
    print(f"{'='*60}\n")

    t_start = time.perf_counter()

    for epoch in range(1, cfg.training.epochs + 1):
        # ----- TRAIN -----
        model.train()
        total_cls_loss = 0.0
        total_rul_loss = 0.0
        total_cls_correct = 0
        total_samples = 0

        for batch_idx, (ic, stage, rul, _soh, _cell_ids, _cycles) in enumerate(dl_train):
            ic = ic.to(device)
            stage = stage.to(device)
            rul = rul.to(device)

            with torch.amp.autocast('cuda', enabled=use_amp):
                stage_logits, rul_pred = model(ic)
                loss_cls = cls_criterion(stage_logits, stage)
                loss_rul = rul_criterion(rul_pred, rul)
                loss = cls_weight * loss_cls + rul_weight * loss_rul

            if torch.isnan(loss) or torch.isinf(loss):
                print(f"\n  [NaN/Inf] epoch {epoch}, batch {batch_idx}")
                continue

            optimizer.zero_grad(set_to_none=True)
            scaler_amp.scale(loss).backward()
            scaler_amp.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.training.grad_clip)
            scaler_amp.step(optimizer)
            scaler_amp.update()

            with torch.no_grad():
                cls_pred = stage_logits.argmax(dim=1)
                total_cls_correct += (cls_pred == stage).sum().item()
            total_cls_loss += loss_cls.item()
            total_rul_loss += loss_rul.item()
            total_samples += ic.size(0)

        n_batches = len(dl_train)
        avg_cls_loss = total_cls_loss / n_batches
        avg_rul_loss = total_rul_loss / n_batches
        train_acc = total_cls_correct / total_samples

        writer.add_scalar("train/cls_loss", avg_cls_loss, epoch)
        writer.add_scalar("train/rul_loss", avg_rul_loss, epoch)
        writer.add_scalar("train/acc", train_acc, epoch)

        # ----- VALIDATION -----
        model.eval()
        val_cls_loss = 0.0
        val_rul_loss = 0.0
        val_correct = 0
        val_samples = 0

        with torch.no_grad():
            for ic, stage, rul, _soh, _cell_ids, _cycles in dl_val:
                ic = ic.to(device)
                stage = stage.to(device)
                rul = rul.to(device)

                stage_logits, rul_pred = model(ic)
                loss_cls = cls_criterion(stage_logits, stage)
                loss_rul = rul_criterion(rul_pred, rul)

                val_cls_loss += loss_cls.item() * ic.size(0)
                val_rul_loss += loss_rul.item() * ic.size(0)
                val_correct += (stage_logits.argmax(dim=1) == stage).sum().item()
                val_samples += ic.size(0)

        val_cls_loss /= val_samples
        val_rul_loss /= val_samples
        val_acc = val_correct / val_samples
        val_total_loss = cls_weight * val_cls_loss + rul_weight * val_rul_loss

        writer.add_scalar("val/cls_loss", val_cls_loss, epoch)
        writer.add_scalar("val/rul_loss", val_rul_loss, epoch)
        writer.add_scalar("val/acc", val_acc, epoch)
        writer.add_scalar("lr", optimizer.param_groups[0]["lr"], epoch)

        scheduler.step(val_total_loss)

        # ----- checkpointing & early stop -----
        is_best = val_total_loss < best_val_loss
        if math.isfinite(val_total_loss) and is_best:
            best_val_loss = val_total_loss
            best_epoch = epoch
            patience_counter = 0
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_cls_loss": val_cls_loss,
                "val_rul_loss": val_rul_loss,
                "val_acc": val_acc,
            }, cfg.checkpoint_dir / "best_model.pt")
        elif math.isfinite(val_total_loss):
            patience_counter += 1

        if epoch % 10 == 0 or is_best:
            elapsed = time.perf_counter() - t_start
            marker = " *" if is_best else ""
            print(
                f"Epoch {epoch:4d}/{cfg.training.epochs} | "
                f"cls: {avg_cls_loss:.4f} | rul: {avg_rul_loss:.4f} | "
                f"acc: {train_acc:.3f} | "
                f"v_cls: {val_cls_loss:.4f} | v_rul: {val_rul_loss:.4f} | "
                f"v_acc: {val_acc:.3f} | "
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

    test_cls_loss = 0.0
    test_rul_loss = 0.0
    test_correct = 0
    test_samples = 0
    all_preds = []
    all_labels = []
    all_rul_preds = []
    all_rul_trues = []

    with torch.no_grad():
        for ic, stage, rul, _soh, _cell_ids, _cycles in dl_test:
            ic = ic.to(device)
            stage = stage.to(device)
            rul = rul.to(device)

            stage_logits, rul_pred = model(ic)
            loss_cls = cls_criterion(stage_logits, stage)
            loss_rul = rul_criterion(rul_pred, rul)

            test_cls_loss += loss_cls.item() * ic.size(0)
            test_rul_loss += loss_rul.item() * ic.size(0)
            test_correct += (stage_logits.argmax(dim=1) == stage).sum().item()
            test_samples += ic.size(0)

            all_preds.append(stage_logits.argmax(dim=1).cpu().numpy())
            all_labels.append(stage.cpu().numpy())
            all_rul_preds.append(rul_pred.cpu().numpy())
            all_rul_trues.append(rul.cpu().numpy())

    test_cls_loss /= test_samples
    test_rul_loss /= test_samples
    test_acc = test_correct / test_samples

    all_preds = np.concatenate(all_preds)
    all_labels = np.concatenate(all_labels)
    all_rul_preds = np.concatenate(all_rul_preds).flatten()
    all_rul_trues = np.concatenate(all_rul_trues).flatten()
    rul_mae = np.abs(all_rul_preds - all_rul_trues).mean()
    rul_rmse = np.sqrt(np.mean((all_rul_preds - all_rul_trues) ** 2))

    # Per-class metrics
    from sklearn.metrics import classification_report, confusion_matrix
    stage_names = ["I-form.", "II-stable", "III-accel.", "IV-EOL"]
    print(f"\nTest Results:")
    print(f"  CLS Loss: {test_cls_loss:.6f}  |  RUL Loss: {test_rul_loss:.6f}")
    print(f"  Accuracy: {test_acc:.4f}")
    print(f"  RUL MAE:  {rul_mae:.6f}  (normalised)")
    print(f"  RUL RMSE: {rul_rmse:.6f}")
    print(f"\nClassification Report:")
    print(classification_report(all_labels, all_preds, target_names=stage_names, zero_division=0))
    print("Confusion Matrix:")
    print(confusion_matrix(all_labels, all_preds))

    print(f"\nBest model: {cfg.checkpoint_dir / 'best_model.pt'}")

    return model, cfg


if __name__ == "__main__":
    train()
