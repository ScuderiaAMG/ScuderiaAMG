"""Export trained CNN checkpoint → ONNX → quantized INT8 for RZ/G2L Cortex-A55.

Deployment target:
  - RZ/G2L  Cortex-A55 ×2  @ 1.2 GHz  (ARM NEON, no GPU/NPU)
  - ONNX Runtime 1.18+ (ARM aarch64 build, CPU EP)
  - Model size: < 100 KB (INT8), inference < 10 ms

Usage:  python -m cnn.export
"""
import torch
import onnx
import onnxruntime as ort
import numpy as np
from pathlib import Path

from .config import Config
from .model import BatteryCNN


def export_to_onnx(cfg: Config | None = None, dynamic_batch: bool = True):
    """Load best checkpoint and export CNN to ONNX (FP32 + INT8).

    Returns:
        onnx_path_fp32, onnx_path_int8
    """
    if cfg is None:
        cfg = Config()

    device = torch.device("cpu")
    ckpt_path = cfg.checkpoint_dir / "best_model.pt"

    if not ckpt_path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {ckpt_path}\nRun train.py first.")

    print(f"Loading checkpoint: {ckpt_path}")
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=True)
    model = BatteryCNN(cfg)
    model.load_state_dict(ckpt["model_state_dict"])
    model.to(device)
    model.eval()

    # ---- FP32 ONNX export ----
    dummy_input = torch.randn(1, cfg.model.in_channels, cfg.data.ic_curve_pts, device=device)

    if dynamic_batch:
        dynamic_axes = {
            "ic_curve": {0: "batch_size"},
            "stage_logits": {0: "batch_size"},
            "rul": {0: "batch_size"},
        }
    else:
        dynamic_axes = {}

    onnx_path = cfg.checkpoint_dir / "battery_cnn_fp32.onnx"
    torch.onnx.export(
        model,
        dummy_input,
        onnx_path,
        input_names=["ic_curve"],
        output_names=["stage_logits", "rul"],
        dynamic_axes=dynamic_axes,
        opset_version=14,
        do_constant_folding=True,
    )

    # Validate ONNX model
    onnx_model = onnx.load(str(onnx_path))
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
        str(onnx_path),
        providers=["CPUExecutionProvider"],
        sess_options=ort.SessionOptions(),
    )
    outputs = sess.run(None, {"ic_curve": sample_input})
    stage_logits = outputs[0]
    rul = float(outputs[1][0, 0])
    stage_pred = int(stage_logits[0].argmax())
    stage_names = {0: "healthy", 1: "degrading", 2: "EOL"}
    print(f"  Sanity: stage={stage_pred} ({stage_names.get(stage_pred, '?')}), "
          f"RUL={rul:.4f} ∈ [0,1] ✓" if 0 <= rul <= 1 else f"  WARNING: RUL={rul:.4f} out of range")
    return stage_pred, rul


def _quantize_int8(fp32_path: Path, cfg: Config) -> Path:
    """Dynamic INT8 quantization for Cortex-A55 deployment."""
    from onnxruntime.quantization import quantize_dynamic, QuantType

    int8_path = fp32_path.parent / "battery_cnn_int8.onnx"
    print(f"\nQuantizing to INT8 ...")

    quantize_dynamic(
        model_input=str(fp32_path),
        model_output=str(int8_path),
        weight_type=QuantType.QInt8,
        extra_options={"ActivationSymmetric": True},
    )

    # Validate INT8 model
    onnx_model = onnx.load(str(int8_path))
    onnx.checker.check_model(onnx_model)
    print(f"INT8 model validated ✓")

    # Compare FP32 vs INT8 outputs
    sess_fp32 = ort.InferenceSession(str(fp32_path), providers=["CPUExecutionProvider"])
    sess_int8 = ort.InferenceSession(str(int8_path), providers=["CPUExecutionProvider"])

    dummy = np.random.randn(100, cfg.model.in_channels, cfg.data.ic_curve_pts).astype(np.float32)
    out_fp32_cls, out_fp32_rul = sess_fp32.run(None, {"ic_curve": dummy})
    out_int8_cls, out_int8_rul = sess_int8.run(None, {"ic_curve": dummy})

    # Classification agreement
    cls_agree = (out_fp32_cls.argmax(axis=1) == out_int8_cls.argmax(axis=1)).mean()
    # RUL MAE
    rul_mae = np.abs(out_fp32_rul - out_int8_rul).mean()
    print(f"  FP32 vs INT8 classification agreement: {cls_agree:.4f}")
    print(f"  FP32 vs INT8 RUL MAE: {rul_mae:.6f}")
    if cls_agree > 0.98 and rul_mae < 0.01:
        print(f"  Quantization accuracy: excellent ✓")
    else:
        print(f"  WARNING: quantization error may be significant")

    return int8_path


def _file_size(path: Path) -> str:
    kb = path.stat().st_size / 1024
    return f"{kb:.1f} KB" if kb < 1024 else f"{kb/1024:.1f} MB"


if __name__ == "__main__":
    export_to_onnx()
