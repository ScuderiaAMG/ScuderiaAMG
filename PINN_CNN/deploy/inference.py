"""Battery SOH dual-model inference — RZ/G2L Cortex-A55 deployment.

Models:
  PINN  → SOH regression (fast screening, 8-min data)
  CNN   → 3-stage classification + RUL (precise assessment)

Usage:  python3 inference.py <model> <input_data.npy>
        python3 inference.py pinn  sample.npy
        python3 inference.py cnn   sample.npy
"""
import numpy as np
import onnxruntime as ort
import pickle
import sys
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parent

# Stage labels for CNN
STAGE_NAMES = {0: "healthy", 1: "degrading", 2: "EOL"}


class PINNInference:
    """PINN model: 132-d features → SOH ∈ [0, 1]."""

    def __init__(self):
        onnx_path = MODEL_DIR / "battery_pinn_int8.onnx"
        scaler_path = MODEL_DIR / "feature_scaler.pkl"

        with open(scaler_path, "rb") as f:
            self.scaler = pickle.load(f)

        opts = ort.SessionOptions()
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        opts.intra_op_num_threads = 2           # Cortex-A55 dual-core
        opts.inter_op_num_threads = 1
        self.sess = ort.InferenceSession(
            str(onnx_path), providers=["CPUExecutionProvider"], sess_options=opts
        )
        self.input_name = self.sess.get_inputs()[0].name

    def predict(self, features_132d: np.ndarray) -> float:
        """features_132d: raw 132-d vector (IC[128] + temp + log_cycle + dv + cap)."""
        x = features_132d.reshape(1, -1).astype(np.float32)
        x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
        x = self.scaler.transform(x).astype(np.float32)
        x = np.clip(x, -5.0, 5.0)
        soh = self.sess.run(None, {self.input_name: x})[0]
        return float(np.clip(soh[0, 0], 0.0, 1.0))


class CNNInference:
    """CNN model: IC curve (128,) → stage + RUL."""

    def __init__(self):
        onnx_path = MODEL_DIR / "battery_cnn_int8.onnx"
        scaler_path = MODEL_DIR / "ic_scaler.pkl"

        with open(scaler_path, "rb") as f:
            scalers = pickle.load(f)
            self.ic_scaler = scalers["ic_scaler"]
            self.ig_scaler = scalers["ig_scaler"]

        opts = ort.SessionOptions()
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        opts.intra_op_num_threads = 2
        opts.inter_op_num_threads = 1
        self.sess = ort.InferenceSession(
            str(onnx_path), providers=["CPUExecutionProvider"], sess_options=opts
        )
        self.input_name = self.sess.get_inputs()[0].name

    def predict(self, ic_curve: np.ndarray) -> dict:
        """ic_curve: (128,) raw IC curve (dQ/dV)."""
        ic = ic_curve.reshape(1, -1).astype(np.float32)
        ic = np.nan_to_num(ic, nan=0.0, posinf=0.0, neginf=0.0)

        # Channel 1: standardised IC
        ic_norm = self.ic_scaler.transform(ic)
        ic_norm = np.clip(ic_norm, -5.0, 5.0)

        # Channel 2: standardised IC gradient
        ic_grad = np.gradient(ic_norm, axis=1)
        abs_max = np.abs(ic_grad).max(axis=1, keepdims=True)
        if abs_max[0, 0] > 1e-6:
            ic_grad /= abs_max
        ic_grad = self.ig_scaler.transform(ic_grad).astype(np.float32)
        ic_grad = np.clip(ic_grad, -5.0, 5.0)

        # Stack dual-channel
        x = np.stack([ic_norm, ic_grad], axis=1).astype(np.float32)

        outputs = self.sess.run(None, {self.input_name: x})
        stage_logits = outputs[0]
        rul = float(outputs[1][0, 0])

        stage = int(np.argmax(stage_logits[0]))
        return {
            "stage": stage,
            "stage_name": STAGE_NAMES[stage],
            "rul": max(0.0, min(1.0, rul)),
        }


# ============================================================
def main():
    if len(sys.argv) < 2:
        print("Usage: python3 inference.py <pinn|cnn|benchmark> [input.npy]")
        sys.exit(1)

    if sys.argv[1] == "pinn":
        model = PINNInference()
        if len(sys.argv) > 2:
            data = np.load(sys.argv[2])
        else:
            data = np.random.randn(132).astype(np.float32)
        soh = model.predict(data)
        print(f"PINN SOH: {soh:.4f}  ({soh*100:.1f}%)")

    elif sys.argv[1] == "cnn":
        model = CNNInference()
        if len(sys.argv) > 2:
            data = np.load(sys.argv[2])
        else:
            data = np.random.randn(128).astype(np.float32)
        result = model.predict(data)
        print(f"CNN Stage: {result['stage_name']} ({result['stage']})")
        print(f"CNN RUL:   {result['rul']:.4f}")

    elif sys.argv[1] == "benchmark":
        _benchmark()

    else:
        print(f"Unknown model: {sys.argv[1]}")


def _benchmark():
    """Measure inference latency on RZ/G2L."""
    import time

    pinn = PINNInference()
    cnn = CNNInference()

    dummy_132d = np.random.randn(132).astype(np.float32)
    dummy_ic = np.random.randn(128).astype(np.float32)

    # Warmup
    for _ in range(10):
        pinn.predict(dummy_132d)
        cnn.predict(dummy_ic)

    # PINN benchmark
    n = 500
    t0 = time.perf_counter()
    for _ in range(n):
        pinn.predict(dummy_132d)
    t_pinn = (time.perf_counter() - t0) / n * 1000
    print(f"PINN latency: {t_pinn:.1f} ms  ({n} runs)")

    # CNN benchmark
    t0 = time.perf_counter()
    for _ in range(n):
        cnn.predict(dummy_ic)
    t_cnn = (time.perf_counter() - t0) / n * 1000
    print(f"CNN  latency: {t_cnn:.1f} ms  ({n} runs)")


if __name__ == "__main__":
    main()
