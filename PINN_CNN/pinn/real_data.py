"""Real battery aging dataset loaders — NASA PCoE & CALCE.

Dataset sources (需手动下载):
  1. NASA PCoE Battery Dataset (18650, 额定2Ah)
     URL: https://www.nasa.gov/intelligent-systems-division/prognostics-center-of-excellence-data-set-repository/
     文件: B0005.mat, B0006.mat, B0007.mat, B0018.mat
     工况: 室温CC-CV充放电, 1.5A放电, 循环至容量衰减到70%

  2. CALCE Battery Dataset (Univ. of Maryland)
     URL: https://calce.umd.edu/battery-data
     文件: CS2_35, CS2_36, CS2_37, CS2_38 (LiCoO2 18650)
     工况: 多温度多倍率循环老化

Download → 放入项目 data/ 目录下对应子目录（如 PINN_CNN/data/nasa_pcoe/）.
"""
import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter
from pathlib import Path
from typing import Optional
import warnings


# ============================================================
# NASA PCoE Loader
# ============================================================

def load_nasa_pcoe(data_dir: str | Path = "data/nasa_pcoe",
                   cells: tuple = ("B0005", "B0006", "B0007", "B0018")) -> dict:
    """Load NASA PCoE battery aging .mat files.

    NASA data structure (per .mat file):
      cycle[n].type          — 'charge', 'discharge', 'impedance'
      cycle[n].data.Voltage_measured  — (T,) 电压 (V)
      cycle[n].data.Current_measured  — (T,) 电流 (A)
      cycle[n].data.Temperature_measured — (T,) 温度 (°C)
      cycle[n].data.Time          — (T,) 时间 (s)
      cycle[n].data.Capacity      — scalar 放电容量 (Ah)

    Returns standardized dict with same keys as battery_sim output:
      cell_id, cycle, soh, temp, ic, dv_start, capacity_meas
    """
    try:
        from scipy.io import loadmat
    except ImportError:
        raise ImportError("需要 scipy: pip install scipy")

    data_dir = Path(data_dir)
    all_data = {
        "cell_id": [], "cycle": [], "soh": [], "temp": [],
        "ic": [], "dv_start": [], "capacity_meas": [],
    }

    for cell_idx, cell_name in enumerate(cells):
        mat_path = data_dir / f"{cell_name}.mat"
        if not mat_path.exists():
            print(f"  [跳过] {mat_path} — 文件不存在")
            continue

        print(f"  Loading {cell_name} ...")
        mat = loadmat(str(mat_path))
        battery = mat[cell_name][0, 0]

        # Determine nominal capacity: max discharge capacity in first 50 cycles
        discharge_caps = []
        for cyc_idx in range(min(50, len(battery["cycle"][0]))):
            cyc_data = battery["cycle"][0, cyc_idx]
            if cyc_data["type"][0].strip().lower() == "discharge":
                discharge_caps.append(float(cyc_data["data"][0, 0]["Capacity"][0, 0]))
        if not discharge_caps:
            print(f"  [警告] {cell_name}: 找不到放电循环, 跳过")
            continue
        c_nominal = max(discharge_caps)

        # Extract charge cycles for feature building
        n_charge_cycles = 0
        n_total_cycles = len(battery["cycle"][0])

        for cyc_idx in range(n_total_cycles):
            cyc_data = battery["cycle"][0, cyc_idx]
            cycle_type = cyc_data["type"][0].strip().lower()

            if cycle_type != "charge":
                continue

            data = cyc_data["data"][0, 0]
            voltage = data["Voltage_measured"][0, 0].flatten().astype(np.float64)
            current = data["Current_measured"][0, 0].flatten().astype(np.float64)
            temp_arr = data["Temperature_measured"][0, 0].flatten().astype(np.float64)
            time_arr = data["Time"][0, 0].flatten().astype(np.float64)

            if len(voltage) < 50:
                continue  # too short, skip

            # Find preceding discharge capacity (SOH ground truth)
            soh_value = None
            for prev_idx in range(cyc_idx - 1, -1, -1):
                prev_data = battery["cycle"][0, prev_idx]
                if prev_data["type"][0].strip().lower() == "discharge":
                    cap = float(prev_data["data"][0, 0]["Capacity"][0, 0])
                    soh_value = cap / c_nominal
                    break
            if soh_value is None:
                continue

            # ---- Feature extraction ----
            # Temperature (mean of this charge cycle)
            temp_mean = float(temp_arr.mean())

            # dV_start proxy: voltage change in first few seconds / current
            charge_current = float(np.mean(current[current > 0.01]))
            if charge_current < 0.01:
                continue
            dv_start = (voltage[min(5, len(voltage)-1)] - voltage[0]) / charge_current

            # Measured capacity: from associated discharge
            cap_meas = soh_value * c_nominal

            # IC curve: dQ/dV during charge
            # Q = integral of I*dt
            dt = np.diff(time_arr, prepend=time_arr[0] - (time_arr[1]-time_arr[0]) if len(time_arr) > 1 else 1.0)
            dt = np.clip(dt, 0.1, None)  # avoid zero/negative dt
            q_ah = np.cumsum(current * dt) / 3600.0

            try:
                dv_dq = np.gradient(voltage, q_ah)
                dq_dv = 1.0 / np.clip(np.abs(dv_dq), 1e-6, None)
                dq_dv_smooth = savgol_filter(dq_dv, min(31, len(dq_dv)//2*2+1), 3)
            except (ValueError, np.linalg.LinAlgError):
                continue

            # Resample to fixed voltage grid (NCA: 3.2-4.2V)
            v_grid = np.linspace(3.2, 4.2, 128)
            valid = (voltage > 3.2) & (voltage < 4.2)
            if valid.sum() < 10:
                continue
            f = interp1d(voltage[valid], dq_dv_smooth[valid],
                         kind='linear', bounds_error=False, fill_value=0.0)
            ic_curve = f(v_grid)
            mx = ic_curve.max()
            if mx > 0:
                ic_curve /= mx

            all_data["cell_id"].append(cell_idx)
            all_data["cycle"].append(n_charge_cycles + 1)
            all_data["soh"].append(soh_value)
            all_data["temp"].append(temp_mean)
            all_data["ic"].append(ic_curve.astype(np.float32))
            all_data["dv_start"].append(dv_start)
            all_data["capacity_meas"].append(cap_meas)
            n_charge_cycles += 1

        print(f"    → {n_charge_cycles} charge cycles extracted")

    # Concatenate
    result = {k: np.array(v) if k != "ic" else np.stack(v) if v else np.array([])
              for k, v in all_data.items()}
    print(f"\nTotal: {len(result['soh'])} samples from {len(cells)} cells")
    return result


def _find_sheet(sheets: dict, prefix: str):
    """Find first sheet whose name starts with prefix."""
    for name, df in sheets.items():
        if name.startswith(prefix):
            return df
    return None


# ============================================================
# CALCE Loader  (Arbin xlsx 格式)
# ============================================================

def load_calce(data_dir: str | Path = "data/calce",
               cells: tuple = ("CS2_35", "CS2_36", "CS2_37", "CS2_38")) -> dict:
    """Load CALCE battery aging data from Arbin .xlsx files.

    每个 cell 目录下包含多个 .xlsx 文件，每个文件是一次 Arbin 测试会话。
    单-sheet 格式 (Info + Channel_1-XXX):
      Channel sheet 同时包含逐采样点 (V, I, Cycle_Index) 和累积容量/内阻列。

    首次加载后缓存为 .npz 文件，后续秒级加载。
    Returns standardized dict with keys:
      cell_id, cycle, soh, temp, ic, dv_start, capacity_meas
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("需要 pandas + openpyxl: pip install pandas openpyxl")

    data_dir = Path(data_dir)
    cache_path = data_dir / "calce_cache.npz"

    if cache_path.exists():
        print(f"  Loading cached: {cache_path}")
        cached = dict(np.load(cache_path, allow_pickle=True))
        return {k: np.asarray(v) for k, v in cached.items()}

    all_data = {
        "cell_id": [], "cycle": [], "soh": [], "temp": [],
        "ic": [], "dv_start": [], "capacity_meas": [],
    }

    for cell_idx, cell_name in enumerate(cells):
        cell_dir = data_dir / cell_name
        if not cell_dir.exists():
            continue

        xlsx_files = sorted(cell_dir.glob("*.xlsx"))
        if not xlsx_files:
            continue

        print(f"  Loading {cell_name} ({len(xlsx_files)} sessions) ...")

        # --- Pass 1: estimate nominal capacity from all discharge capacities ---
        all_dc_per_cycle = []
        for xf in xlsx_files:
            try:
                sheets = pd.read_excel(xf, sheet_name=None)
                channel = _find_sheet(sheets, "Channel")
                if channel is None:
                    continue
                df = channel
                for cyc, grp in df.groupby("Cycle_Index"):
                    dc = grp["Discharge_Capacity(Ah)"].max() - grp["Discharge_Capacity(Ah)"].min()
                    if dc > 0:
                        all_dc_per_cycle.append(dc)
            except Exception:
                continue

        if not all_dc_per_cycle:
            print(f"  [警告] {cell_name}: 无法读取放电容量, 跳过")
            continue
        c_nominal = float(np.percentile(all_dc_per_cycle, 95))

        # --- Pass 2: extract charge curves + SOH ---
        global_cycle = 0

        for xf in xlsx_files:
            try:
                sheets = pd.read_excel(xf, sheet_name=None)
                channel = _find_sheet(sheets, "Channel")
                if channel is None:
                    continue
            except Exception:
                continue

            df = channel
            # Standardise column access
            col_map = {c.lower().replace(" ", "_").replace("(", "").replace(")", ""): c
                       for c in df.columns}
            cyc_col = col_map.get("cycle_index", "Cycle_Index")
            i_col = col_map.get("current_a", "Current(A)")
            v_col = col_map.get("voltage_v", "Voltage(V)")
            t_col = col_map.get("test_time_s", "Test_Time(s)")
            dc_col = col_map.get("discharge_capacity_ah", "Discharge_Capacity(Ah)")
            cc_col = col_map.get("charge_capacity_ah", "Charge_Capacity(Ah)")

            # --- Per-cycle stats ---
            cycle_stats = {}
            for cyc, grp in df.groupby(cyc_col):
                dc = float(grp[dc_col].max() - grp[dc_col].min())
                if dc <= 0:
                    continue
                soh_val = dc / c_nominal
                if soh_val <= 0 or soh_val > 1.5:
                    continue
                cycle_stats[int(cyc)] = soh_val

            # --- Extract charge segments ---
            charge_mask = df[i_col] > 0.01
            if charge_mask.sum() < 100:
                continue

            for cyc in sorted(df.loc[charge_mask, cyc_col].unique()):
                cyc_int = int(cyc)
                if cyc_int not in cycle_stats:
                    continue
                soh_val = cycle_stats[cyc_int]

                mask = charge_mask & (df[cyc_col] == cyc)
                seg = df.loc[mask].sort_values(t_col)
                if len(seg) < 50:
                    continue

                voltage = seg[v_col].values.astype(np.float64)
                current = seg[i_col].values.astype(np.float64)
                cap_arr = seg[cc_col].values.astype(np.float64)

                charge_current = float(np.mean(current))
                if charge_current < 0.01:
                    continue

                dv_start = (voltage[min(5, len(voltage) - 1)] - voltage[0]) / charge_current

                # IC curve via dQ/dV
                try:
                    dv_dq = np.gradient(voltage, cap_arr)
                    dq_dv = 1.0 / np.clip(np.abs(dv_dq), 1e-6, None)
                    wlen = min(31, len(dq_dv) // 2 * 2 + 1)
                    dq_dv_smooth = savgol_filter(dq_dv, wlen, 3) if wlen >= 5 else dq_dv
                except (ValueError, np.linalg.LinAlgError):
                    continue

                v_grid = np.linspace(3.0, 4.2, 128)
                valid_v = (voltage > 3.0) & (voltage < 4.2)
                if valid_v.sum() < 10:
                    continue
                f = interp1d(voltage[valid_v], dq_dv_smooth[valid_v],
                             kind="linear", bounds_error=False, fill_value=0.0)
                ic_curve = f(v_grid)
                mx = ic_curve.max()
                if mx > 0:
                    ic_curve /= mx

                global_cycle += 1
                all_data["cell_id"].append(cell_idx)
                all_data["cycle"].append(global_cycle)
                all_data["soh"].append(np.clip(soh_val, 0.3, 1.02))
                all_data["temp"].append(25.0)
                all_data["ic"].append(ic_curve.astype(np.float32))
                all_data["dv_start"].append(dv_start)
                all_data["capacity_meas"].append(soh_val * c_nominal)

        print(f"    → {global_cycle} charge cycles extracted (c_nominal={c_nominal:.3f} Ah)")

    result = {k: np.array(v) if k != "ic" else np.stack(v) if v else np.array([])
              for k, v in all_data.items()}
    print(f"\nCALCE total: {len(result['soh'])} samples from {len(cells)} cells")

    if len(result["soh"]) > 0:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(cache_path, **result)
        print(f"  Cached → {cache_path}")

    return result
