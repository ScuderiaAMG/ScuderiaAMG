"""Export StandardScaler parameters for C++ inference engine.

Reads the fitted StandardScaler objects from PINN and CNN training checkpoints
and exports their mean/std as raw float32 binary files for direct loading in C++.

Usage:  python export_scalers.py

Output: deploy/scalers/
    pinn_mean.bin          — 132 floats, PINN feature mean
    pinn_std.bin           — 132 floats, PINN feature std
    cnn_ic_scaler_mean.bin — 128 floats, CNN IC curve mean
    cnn_ic_scaler_std.bin  — 128 floats, CNN IC curve std
    cnn_ig_scaler_mean.bin — 128 floats, CNN IC gradient mean
    cnn_ig_scaler_std.bin  — 128 floats, CNN IC gradient std
"""
import pickle
import numpy as np
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DIR = SCRIPT_DIR / "deploy" / "scalers"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def export_standard_scaler(scaler, name: str, out_dir: Path) -> tuple:
    """Export a sklearn StandardScaler as mean.bin and std.bin.

    Args:
        scaler: Fitted sklearn.preprocessing.StandardScaler instance.
        name: Human-readable name for logging.
        out_dir: Output directory.

    Returns:
        (mean_path, std_path)
    """
    mean = scaler.mean_.astype(np.float32)
    std = scaler.scale_.astype(np.float32)  # sklearn stores scale_ = std

    # Avoid division by zero: replace near-zero std with 1.0
    std = np.where(std < 1e-8, 1.0, std)

    mean_path = out_dir / f"{name}_mean.bin"
    std_path = out_dir / f"{name}_std.bin"

    mean.tofile(mean_path)
    std.tofile(std_path)

    n = len(mean)
    print(f"  {name}: {n} dims  |  mean∈[{mean.min():.4f}, {mean.max():.4f}]  "
          f"std∈[{std.min():.4f}, {std.max():.4f}]  |  {mean_path.stat().st_size} + {std_path.stat().st_size} bytes")

    return mean_path, std_path


def main():
    print("=" * 60)
    print("Exporting StandardScaler parameters for C++ inference engine")
    print(f"Output directory: {OUT_DIR}")
    print("=" * 60)

    exported = []

    # ---- PINN feature scaler ----
    pinn_scaler_paths = [
        SCRIPT_DIR / "pinn" / "checkpoints" / "feature_scaler.pkl",
        SCRIPT_DIR / "pinn" / "cache" / "feature_scaler.pkl",
    ]
    pinn_found = False
    for p in pinn_scaler_paths:
        if p.exists():
            print(f"\n[PINN] Loading scaler from: {p}")
            with open(p, "rb") as f:
                sc = pickle.load(f)
            mean_path, std_path = export_standard_scaler(sc, "pinn", OUT_DIR)
            exported.append(("PINN", mean_path, std_path))
            pinn_found = True
            break
    if not pinn_found:
        print(f"\n[PINN] WARNING: Scaler not found at any of:")
        for p in pinn_scaler_paths:
            print(f"  - {p}  (exists: {p.exists()})")
        print("  → PINN inference in C++ will expect pre-normalized input.")

    # ---- CNN IC + gradient scalers ----
    cnn_scaler_paths = [
        SCRIPT_DIR / "cnn" / "checkpoints" / "ic_scaler.pkl",
        SCRIPT_DIR / "cnn" / "cache" / "ic_scaler.pkl",
    ]
    cnn_found = False
    for p in cnn_scaler_paths:
        if p.exists():
            print(f"\n[CNN] Loading scalers from: {p}")
            with open(p, "rb") as f:
                scs = pickle.load(f)

            if isinstance(scs, dict) and "ic_scaler" in scs and "ig_scaler" in scs:
                # Production CNN format: dict with two scalers
                for key in ["ic_scaler", "ig_scaler"]:
                    mean_path, std_path = export_standard_scaler(
                        scs[key], f"cnn_{key}", OUT_DIR)
                    exported.append(("CNN", mean_path, std_path))
                cnn_found = True
                break
            elif hasattr(scs, "mean_"):
                # Legacy single-scaler format
                mean_path, std_path = export_standard_scaler(scs, "cnn_ic_scaler", OUT_DIR)
                exported.append(("CNN", mean_path, std_path))
                print("  NOTE: Single scaler found; gradient scaler not available.")
                cnn_found = True
                break

    if not cnn_found:
        print(f"\n[CNN] WARNING: Scaler not found at any of:")
        for p in cnn_scaler_paths:
            print(f"  - {p}  (exists: {p.exists()})")
        print("  → CNN inference in C++ will expect pre-normalized input.")

    # ---- Summary ----
    print(f"\n{'=' * 60}")
    print(f"Export complete. {len(exported)} files written to:")
    print(f"  {OUT_DIR}")
    print()
    print("Files:")
    for model_type, mean_p, std_p in exported:
        print(f"  [{model_type}] {mean_p.name} ({mean_p.stat().st_size} B)")
        print(f"  [{model_type}] {std_p.name}  ({std_p.stat().st_size} B)")

    print(f"\nDeploy these files alongside the ONNX models to RZ/G2L.")
    print(f"Target path on RZ/G2L: ~/battery_inference/scalers/")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
