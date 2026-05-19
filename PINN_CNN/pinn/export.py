"""Export trained PINN checkpoint → ONNX → quantized int8 for RZ/G2L Cortex-A55.

Deployment target:
  - RZ/G2L  Cortex-A55 ×2  @ 1.2 GHz  (ARM NEON, no GPU/NPU)
  - ONNX Runtime 1.18+ (ARM aarch64 build, CPU EP)
  - Model size: < 200 KB (int8), inference < 15 ms

Usage:  python -m pinn.export
"""
import torch
import onnx
import onnxruntime as ort
import numpy as np
from pathlib import Path
import pickle

from .config import Config
from .model import BatteryPINN


def export_to_onnx(cfg: Config, dynamic_batch: bool = True):
    """Load best checkpoint and export to ONNX.

    Args:
        cfg: Config object
        dynamic_batch: if True, export with dynamic batch dim for flexible inference

    Returns:
        onnx_path: Path to saved .onnx file
    """
    device = torch.device("cpu")  # export on CPU for ARM compatibility
    ckpt_path = cfg.checkpoint_dir / "best_model.pt"

    if not ckpt_path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {ckpt_path}\nRun train.py first.")

    print(f"Loading checkpoint: {ckpt_path}")
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=True)
    model = BatteryPINN(cfg)
    model.load_state_dict(ckpt["model_state_dict"])
    model.to(device)
    model.eval()

    # ---- FP32 ONNX export ----
    dummy_input = torch.randn(1, cfg.model.input_dim, device=device)

    if dynamic_batch:
        dynamic_axes = {
            "input": {0: "batch_size"},
            "soh": {0: "batch_size"},
        }
    else:
        dynamic_axes = {}

    onnx_path = cfg.checkpoint_dir / "battery_pinn_fp32.onnx"
    torch.onnx.export(
        model,
        dummy_input,
        onnx_path,
        input_names=["input"],
        output_names=["soh"],
        dynamic_axes=dynamic_axes,
        opset_version=14,
        do_constant_folding=True,
    )

    # Validate ONNX model
    onnx_model = onnx.load(onnx_path)
    onnx.checker.check_model(onnx_model)
    print(f"ONNX FP32 exported → {onnx_path}")

    # Quick inference test
    _test_inference(onnx_path, dummy_input.numpy())

    # ---- INT8 quantization ----
    int8_path = _quantize_int8(onnx_path, cfg)

    print(f"\n{'='*60}")
    print(f"Export complete:")
    print(f"  FP32:  {onnx_path}  ({_file_size(onnx_path)})")
    print(f"  INT8:  {int8_path}  ({_file_size(int8_path)})")
    print(f"{'='*60}")

    return onnx_path, int8_path


def _test_inference(onnx_path: Path, sample_input: np.ndarray):
    """Verify ONNX model runs and outputs are in valid range."""
    sess = ort.InferenceSession(
        onnx_path,
        providers=["CPUExecutionProvider"],
        sess_options=ort.SessionOptions(),
    )
    outputs = sess.run(None, {"input": sample_input})
    soh = float(outputs[0][0, 0])
    print(f"  Sanity check: SOH({soh:.4f}) ∈ [0,1] ✓" if 0 <= soh <= 1 else f"WARNING: SOH={soh:.4f} out of range")
    return soh


def _quantize_int8(fp32_path: Path, cfg: Config) -> Path:
    """Quantize FP32 ONNX model to INT8 via dynamic quantization.

    Dynamic quantization is chosen over static (QDQ) because:
      - No calibration dataset needed (training data may not be available at export time)
      - < 1% accuracy loss for MLP architectures empirically
      - Simpler deployment pipeline
    """
    from onnxruntime.quantization import quantize_dynamic, QuantType

    int8_path = fp32_path.parent / "battery_pinn_int8.onnx"
    print(f"\nQuantizing to INT8 ...")

    quantize_dynamic(
        model_input=str(fp32_path),
        model_output=str(int8_path),
        weight_type=QuantType.QInt8,
        extra_options={"ActivationSymmetric": True},
    )

    # Validate INT8 model
    onnx_model = onnx.load(int8_path)
    onnx.checker.check_model(onnx_model)
    print(f"INT8 model validated ✓")

    # Compare FP32 vs INT8 outputs
    sess_fp32 = ort.InferenceSession(fp32_path, providers=["CPUExecutionProvider"])
    sess_int8 = ort.InferenceSession(int8_path, providers=["CPUExecutionProvider"])

    dummy = np.random.randn(100, cfg.model.input_dim).astype(np.float32)
    out_fp32 = sess_fp32.run(None, {"input": dummy})[0]
    out_int8 = sess_int8.run(None, {"input": dummy})[0]
    mae = np.abs(out_fp32 - out_int8).mean()
    max_err = np.abs(out_fp32 - out_int8).max()
    print(f"  FP32 vs INT8 MAE: {mae:.6f}  |  Max error: {max_err:.6f}")
    if mae < 0.01:
        print(f"  Quantization accuracy: excellent (MAE < 1% SOH) ✓")
    else:
        print(f"  WARNING: quantization error may be significant")

    return int8_path


def _file_size(path: Path) -> str:
    kb = path.stat().st_size / 1024
    return f"{kb:.1f} KB" if kb < 1024 else f"{kb/1024:.1f} MB"


if __name__ == "__main__":
    cfg = Config()
    export_to_onnx(cfg)
