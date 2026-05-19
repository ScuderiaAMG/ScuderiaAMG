"""LiFePO4 18650 battery aging simulator — synthetic data generator.

Generates realistic charge curves across degradation cycles using a 2-RC
equivalent-circuit model with empirically-calibrated LFP OCV and aging laws.
Results are cached to HDF5 for fast reload during training.
"""
import numpy as np
from scipy.interpolate import interp1d, CubicSpline
from scipy.signal import savgol_filter
from pathlib import Path
import warnings


class LFPBatterySimulator:
    """2-RC ECM simulator for LiFePO4 18650 cell aging."""

    # LFP OCV anchor points (SOC 0→1, voltage in V) — flat plateau is the signature
    SOC_ANCHORS = np.array([0.0, 0.02, 0.05, 0.10, 0.20, 0.40, 0.60, 0.80, 0.90, 0.95, 0.98, 1.0])
    OCV_ANCHORS = np.array([2.80, 3.08, 3.22, 3.28, 3.31, 3.33, 3.34, 3.36, 3.42, 3.52, 3.60, 3.65])

    def __init__(self, config, seed: int = 42):
        self.data_cfg = config.data
        self.phys_cfg = config.physics
        self.rng = np.random.default_rng(seed)
        self._ocv_spline = CubicSpline(self.SOC_ANCHORS, self.OCV_ANCHORS, extrapolate=True)

    def ocv(self, soc: np.ndarray) -> np.ndarray:
        """OCV from SOC via cubic-spline interpolation."""
        soc = np.clip(soc, 0.0, 1.0)
        return self._ocv_spline(soc)

    def simulate_cell(self, cell_id: int) -> dict:
        """Simulate one cell's full aging trajectory.

        Returns dict with keys:
            cycles: (N,)       cycle indices
            soh:    (N,)       ground-truth SOH
            temp:   (N,)       temperature per cycle (°C)
            v_data: (N, T)     charge V(t) curves (resampled)
            ic:     (N, P)     IC curves dQ/dV (P = ic_curve_pts)
            dv_start:(N,)      voltage-step proxy for R_int
            capacity_meas:(N,) measured capacity per cycle (Ah)
        """
        dcfg = self.data_cfg
        pcfg = self.phys_cfg
        n_pts_ic = dcfg.ic_curve_pts
        max_cyc = dcfg.max_cycles
        rng = self.rng

        # --- cell-specific parameters (creates diversity) ---
        c0 = 1.10 + rng.normal(0, 0.03)          # nominal capacity (Ah)
        deg_rate = 10 ** rng.uniform(-3.5, -2.5)  # capacity-fade rate
        alpha = rng.uniform(0.72, 0.85)            # power-law exponent
        r0_init = pcfg.r0_initial_ohm * (1 + rng.normal(0, 0.05))
        res_growth = rng.uniform(0.08, 0.18)       # resistance growth factor
        temp_cell = rng.uniform(*dcfg.temperature_range)

        # RC parameters (mild cell-to-cell scatter)
        r1, c1 = 0.018 * (1 + rng.normal(0, 0.05)), 800 * (1 + rng.normal(0, 0.08))
        r2, c2 = 0.025 * (1 + rng.normal(0, 0.05)), 3500 * (1 + rng.normal(0, 0.08))
        tau1, tau2 = r1 * c1, r2 * c2

        charge_rate = rng.uniform(*dcfg.charge_current_pu)
        i_charge = charge_rate * c0  # constant current (A)

        # Sample cycles (log-spaced: dense early, sparse later — mirrors real testing)
        sample_cycles = np.unique(
            np.floor(np.logspace(0, np.log10(max_cyc), num=int(max_cyc * 0.6))).astype(int)
        )
        sample_cycles = sample_cycles[sample_cycles < max_cyc]
        # Pad with uniform sampling for remaining cycles
        if sample_cycles[-1] < max_cyc - 1:
            uniform_extra = np.arange(sample_cycles[-1] + 1, max_cyc,
                                      max(1, (max_cyc - sample_cycles[-1]) // 200))
            sample_cycles = np.unique(np.concatenate([sample_cycles, uniform_extra]))

        n_cycles = len(sample_cycles)
        soh_arr = np.zeros(n_cycles)
        dv_arr = np.zeros(n_cycles)
        temp_arr = np.full(n_cycles, temp_cell)
        ic_curves = np.zeros((n_cycles, n_pts_ic))
        cap_meas = np.zeros(n_cycles)

        # Time grid for charge-curve simulation (fixed-length for consistency)
        t_charge = 3600 / charge_rate  # seconds for full charge at this rate
        n_time = 512
        t = np.linspace(0, t_charge, n_time)

        for idx, cycle in enumerate(sample_cycles):
            # ---- ground-truth SOH (power-law capacity fade) ----
            soh = 1.0 - deg_rate * (cycle ** alpha)
            soh = max(soh, 0.35)  # floor: end-of-life threshold
            soh += rng.normal(0, 0.005)  # tiny cycle-to-cycle jitter
            soh = np.clip(soh, 0.3, 1.02)
            soh_arr[idx] = soh

            # ---- resistance growth (linear component + square-root) ----
            resistance = r0_init * (1 + res_growth * cycle ** 0.55)
            r1_aged = r1 * (1 + 0.3 * res_growth * cycle ** 0.4)

            # ---- simulate CC charge curve via 2-RC ECM ----
            cap_now = c0 * soh
            soc_start = rng.uniform(0.0, 0.08)  # start from near-empty
            soc_t = soc_start + (i_charge * t / 3600) / cap_now

            # OCV contribution
            v_ocv = self.ocv(soc_t)
            # ohmic drop
            v_ohmic = i_charge * resistance
            # RC transients (rise during charge)
            v_rc1 = i_charge * r1_aged * (1 - np.exp(-t / tau1))
            v_rc2 = i_charge * r2 * (1 - np.exp(-t / tau2))
            v_total = v_ocv + v_ohmic + v_rc1 + v_rc2

            # measurement noise
            v_total += rng.normal(0, dcfg.noise_voltage_mv / 1000, size=n_time)

            # ---- extract dV at charge start (resistance proxy) ----
            # voltage jump in first 5 seconds divided by current
            dv_idx = max(1, int(5 / (t_charge / n_time)))
            dv_start = (v_total[dv_idx] - v_total[0])  / i_charge
            dv_arr[idx] = dv_start

            # ---- compute IC curve dQ/dV ----
            # Use Savitzky-Golay for smooth derivative
            q_ah = (i_charge * t) / 3600  # charge in Ah
            try:
                dv_dq_raw = np.gradient(v_total, q_ah)
                # dQ/dV = 1 / (dV/dQ), clip to avoid singularities
                dq_dv_raw = 1.0 / np.clip(np.abs(dv_dq_raw), 1e-6, None)
                dq_dv_smooth = savgol_filter(dq_dv_raw, window_length=31, polyorder=3)
            except (ValueError, np.linalg.LinAlgError):
                dq_dv_smooth = np.zeros(n_time)

            # Resample to fixed voltage grid
            v_grid = np.linspace(dcfg.voltage_span[0], dcfg.voltage_span[1], n_pts_ic)
            valid = (v_total > dcfg.voltage_span[0]) & (v_total < dcfg.voltage_span[1])
            if valid.sum() < 10:
                ic_curves[idx] = np.zeros(n_pts_ic)
            else:
                f_interp = interp1d(v_total[valid], dq_dv_smooth[valid],
                                    kind='linear', bounds_error=False,
                                    fill_value=0.0)
                ic_curves[idx] = f_interp(v_grid)
                # normalize per curve
                mx = ic_curves[idx].max()
                if mx > 0:
                    ic_curves[idx] /= mx

            cap_meas[idx] = cap_now * (1 + rng.normal(0, 0.01))  # 1% measurement noise

        return {
            "cell_id": cell_id,
            "cycles": sample_cycles,
            "soh": soh_arr,
            "temp": temp_arr,
            "ic": ic_curves,
            "dv_start": dv_arr,
            "capacity_meas": cap_meas,
            "c0": c0,
            "deg_rate": deg_rate,
            "r0_init": r0_init,
        }

    def generate_dataset(self, save_path: Path | None = None) -> dict:
        """Generate full dataset across multiple virtual cells.

        Returns concatenated arrays ready for PyTorch Dataset.
        """
        all_data = {
            "cell_id": [], "cycle": [], "soh": [], "temp": [],
            "ic": [], "dv_start": [], "capacity_meas": [],
        }

        for cell_id in range(self.data_cfg.n_cells):
            cell = self.simulate_cell(cell_id)
            n = len(cell["cycles"])
            all_data["cell_id"].append(np.full(n, cell_id))
            all_data["cycle"].append(cell["cycles"].astype(np.float32))
            all_data["soh"].append(cell["soh"].astype(np.float32))
            all_data["temp"].append(cell["temp"].astype(np.float32))
            all_data["ic"].append(cell["ic"].astype(np.float32))
            all_data["dv_start"].append(cell["dv_start"].astype(np.float32))
            all_data["capacity_meas"].append(cell["capacity_meas"].astype(np.float32))
            if (cell_id + 1) % 10 == 0:
                print(f"  Simulated {cell_id + 1}/{self.data_cfg.n_cells} cells ...")

        # Concatenate
        result = {k: np.concatenate(v, axis=0) for k, v in all_data.items()}

        if save_path is not None:
            save_path = Path(save_path)
            save_path.mkdir(parents=True, exist_ok=True)
            np.savez_compressed(save_path / "lfp_synthetic.npz", **result)
            print(f"Dataset saved → {save_path / 'lfp_synthetic.npz'}")

        return result
