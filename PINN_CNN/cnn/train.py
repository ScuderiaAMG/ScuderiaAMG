"""CNN multi-task training — 3-stage aging classification + RUL regression.

Target: RTX 4060 Laptop GPU 8 GB  |  CPU: i7-14700HX  |  RAM: 64 GB
Usage:  python -m cnn.train
"""
import torch
import torch.nn as nn
from torch.utils.tensorboard import SummaryWriter
from pathlib import Path
import time
import math
import numpy as np

from .config import Config
from .model import BatteryCNN
from .dataset import create_dataloaders

STAGE_NAMES = ["healthy", "degrading", "EOL"]


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

    dl_train, dl_val, dl_test, cls_weights = create_dataloaders(cfg)

    # Sanity
    ic0, st0, rul0, soh0, _, _ = next(iter(dl_train))
    for name, t in [("ic", ic0), ("stage", st0), ("rul", rul0), ("soh", soh0)]:
        if torch.isnan(t.float()).any():
            raise RuntimeError(f"NaN in {name}!")
        if torch.isinf(t.float()).any():
            raise RuntimeError(f"Inf in {name}!")
    print(f"Data OK — IC ∈ [{ic0.min():.4f}, {ic0.max():.4f}], "
          f"stages: {torch.unique(st0).tolist()}")

    # Model
    model = BatteryCNN(cfg).to(device)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Model params: {total_params:,}")

    # Losses
    cls_weights = cls_weights.to(device)
    cls_criterion = nn.CrossEntropyLoss(weight=cls_weights,
                                         label_smoothing=cfg.data.label_smoothing)
    rul_criterion = nn.MSELoss()
    cls_w, rul_w = cfg.training.cls_weight, cfg.training.rul_weight

    # Optimizer & scheduler
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.training.learning_rate,
                                   weight_decay=cfg.training.weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=cfg.training.lr_factor,
        patience=cfg.training.lr_patience,
    )
    scaler_amp = torch.amp.GradScaler('cuda', enabled=cfg.training.use_amp)
    use_amp = cfg.training.use_amp and device.type == 'cuda'

    cfg.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    cfg.log_dir.mkdir(parents=True, exist_ok=True)
    writer = SummaryWriter(cfg.log_dir)
    best_val_loss = float("inf")
    best_epoch = 0
    patience = 0

    print(f"\n{'='*60}")
    print(f"Training: {cfg.training.epochs} ep  batch={cfg.training.batch_size}")
    print(f"3-stage: healthy(SOH≥0.82)  degrading(0.82>SOH≥0.70)  EOL(SOH<0.70)")
    print(f"{'='*60}\n")

    t_start = time.perf_counter()

    for epoch in range(1, cfg.training.epochs + 1):
        # ----- TRAIN -----
        model.train()
        train_cls = 0.0
        train_rul = 0.0
        train_correct = 0
        train_n = 0

        for ic, stage, rul, _soh, _cid, _cyc in dl_train:
            ic = ic.to(device)
            stage = stage.to(device)
            rul = rul.to(device)

            with torch.amp.autocast('cuda', enabled=use_amp):
                logits, rul_pred = model(ic)
                l_cls = cls_criterion(logits, stage)
                l_rul = rul_criterion(rul_pred, rul)
                loss = cls_w * l_cls + rul_w * l_rul

            if not torch.isfinite(loss):
                continue

            optimizer.zero_grad(set_to_none=True)
            scaler_amp.scale(loss).backward()
            scaler_amp.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.training.grad_clip)
            scaler_amp.step(optimizer)
            scaler_amp.update()

            train_cls += l_cls.item()
            train_rul += l_rul.item()
            train_correct += (logits.argmax(1) == stage).sum().item()
            train_n += ic.size(0)

        nb = len(dl_train)
        avg_cls = train_cls / nb
        avg_rul = train_rul / nb
        train_acc = train_correct / train_n
        writer.add_scalar("train/cls_loss", avg_cls, epoch)
        writer.add_scalar("train/rul_loss", avg_rul, epoch)
        writer.add_scalar("train/acc", train_acc, epoch)

        # ----- VAL -----
        model.eval()
        val_cls = 0.0
        val_rul = 0.0
        val_correct = 0
        val_n = 0

        with torch.no_grad():
            for ic, stage, rul, _soh, _cid, _cyc in dl_val:
                ic = ic.to(device)
                stage = stage.to(device)
                rul = rul.to(device)
                logits, rul_pred = model(ic)
                val_cls += cls_criterion(logits, stage).item() * ic.size(0)
                val_rul += rul_criterion(rul_pred, rul).item() * ic.size(0)
                val_correct += (logits.argmax(1) == stage).sum().item()
                val_n += ic.size(0)

        val_cls /= val_n
        val_rul /= val_n
        val_acc = val_correct / val_n
        val_total = cls_w * val_cls + rul_w * val_rul
        writer.add_scalar("val/cls_loss", val_cls, epoch)
        writer.add_scalar("val/rul_loss", val_rul, epoch)
        writer.add_scalar("val/acc", val_acc, epoch)
        writer.add_scalar("lr", optimizer.param_groups[0]["lr"], epoch)
        scheduler.step(val_total)

        is_best = math.isfinite(val_total) and val_total < best_val_loss
        if is_best:
            best_val_loss = val_total
            best_epoch = epoch
            patience = 0
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_cls_loss": val_cls,
                "val_rul_loss": val_rul,
                "val_acc": val_acc,
                "num_stages": 3,
            }, cfg.checkpoint_dir / "best_model.pt")
        elif math.isfinite(val_total):
            patience += 1

        if epoch % 10 == 0 or is_best:
            elapsed = time.perf_counter() - t_start
            mark = " *" if is_best else ""
            print(f"Ep {epoch:4d}/{cfg.training.epochs} | "
                  f"cls:{avg_cls:.4f} rul:{avg_rul:.4f} acc:{train_acc:.3f} | "
                  f"v_cls:{val_cls:.4f} v_rul:{val_rul:.4f} v_acc:{val_acc:.3f} | "
                  f"lr:{optimizer.param_groups[0]['lr']:.1e} | "
                  f"{_format_time(elapsed)}{mark}")

        if patience >= cfg.training.early_stop_patience:
            print(f"\nEarly stop @ ep {epoch} (best: {best_epoch}, v_loss={best_val_loss:.6f})")
            break

    writer.close()

    # ---- TEST ----
    print(f"\n{'='*60}\nLoading best checkpoint for test eval ...")
    ckpt = torch.load(cfg.checkpoint_dir / "best_model.pt", map_location=device, weights_only=True)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()

    test_cls = 0.0
    test_rul = 0.0
    test_correct = 0
    test_n = 0
    all_preds, all_labels = [], []
    all_rul_p, all_rul_t = [], []

    with torch.no_grad():
        for ic, stage, rul, _soh, _cid, _cyc in dl_test:
            ic = ic.to(device)
            stage = stage.to(device)
            rul = rul.to(device)
            logits, rul_pred = model(ic)
            test_cls += cls_criterion(logits, stage).item() * ic.size(0)
            test_rul += rul_criterion(rul_pred, rul).item() * ic.size(0)
            test_correct += (logits.argmax(1) == stage).sum().item()
            test_n += ic.size(0)
            all_preds.append(logits.argmax(1).cpu().numpy())
            all_labels.append(stage.cpu().numpy())
            all_rul_p.append(rul_pred.cpu().numpy())
            all_rul_t.append(rul.cpu().numpy())

    test_cls /= test_n
    test_rul /= test_n
    test_acc = test_correct / test_n
    all_preds = np.concatenate(all_preds)
    all_labels = np.concatenate(all_labels)
    all_rul_p = np.concatenate(all_rul_p).flatten()
    all_rul_t = np.concatenate(all_rul_t).flatten()

    from sklearn.metrics import classification_report, confusion_matrix
    print(f"\nTest Results:")
    print(f"  CLS Loss: {test_cls:.4f}  |  RUL Loss: {test_rul:.4f}")
    print(f"  Accuracy: {test_acc:.4f}")
    print(f"  RUL MAE:  {np.abs(all_rul_p - all_rul_t).mean():.6f}")
    print(f"  RUL RMSE: {np.sqrt(np.mean((all_rul_p - all_rul_t)**2)):.6f}")
    print(f"\n{classification_report(all_labels, all_preds, target_names=STAGE_NAMES, zero_division=0)}")
    print("Confusion Matrix:")
    print(confusion_matrix(all_labels, all_preds))
    print(f"\nBest model: {cfg.checkpoint_dir / 'best_model.pt'}")
    return model, cfg


if __name__ == "__main__":
    train()
