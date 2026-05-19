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

Download → 放入 D:/ScuderiaAMG/PINN_CNN/data/ 下对应子目录.
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

            # Resample to fixed voltage grid (128 pts, 2.8-3.6V for NCA; LFP uses 2.8-3.6V)
            v_grid = np.linspace(2.8, 3.6, 128)
            valid = (voltage > 2.8) & (voltage < 3.6)
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


# ============================================================
# CALCE Loader
# ============================================================

def load_calce(data_dir: str | Path = "data/calce",
               cells: tuple = ("CS2_35", "CS2_36", "CS2_37", "CS2_38")) -> dict:
    """Load CALCE battery aging CSV/Excel data.

    CALCE data structure (per cell directory):
      <cell_name>/
        <cell_name>_cycle_data.csv    — 每行一个循环的汇总数据
        <cell_name>_<cycleN>_<temp>.csv — 单个循环的详细V,I,T时间序列

    CALCE data can be requested from: https://calce.umd.edu/battery-data

    Returns standardized dict.
    """
    data_dir = Path(data_dir)
    all_data = {
        "cell_id": [], "cycle": [], "soh": [], "temp": [],
        "ic": [], "dv_start": [], "capacity_meas": [],
    }

    for cell_idx, cell_name in enumerate(cells):
        cell_dir = data_dir / cell_name
        if not cell_dir.exists():
            print(f"  [跳过] {cell_dir} — 目录不存在")
            continue

        # Attempt to find cycle summary CSV
        summary_csv = cell_dir / f"{cell_name}_cycle_data.csv"
        if not summary_csv.exists():
            # Try to scan detailed CSVs
            detail_files = sorted(cell_dir.glob("*.csv"))
            if not detail_files:
                print(f"  [跳过] {cell_name}: 无CSV文件")
                continue
            _load_calce_from_details(cell_dir, cell_idx, detail_files, all_data)
        else:
            _load_calce_from_summary(cell_dir, cell_idx, summary_csv, all_data)

        print(f"  Loaded {cell_name}")

    result = {k: np.array(v) if k != "ic" else np.stack(v) if v else np.array([])
              for k, v in all_data.items()}
    return result


def _load_calce_from_summary(cell_dir, cell_idx, summary_csv, all_data):
    """Parse CALCE summary CSV format."""
    import csv
    with open(summary_csv) as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                cycle = int(row.get("cycle", row.get("Cycle", 0)))
                soh = float(row.get("soh", row.get("SOH", row.get("capacity_ratio", 1.0))))
                temp = float(row.get("temperature", row.get("Temperature", 25.0)))
                cap = float(row.get("capacity", row.get("Capacity", 1.1)))
                dv = float(row.get("dc_resistance", row.get("DC_R", 0.05)))
            except (ValueError, KeyError):
                continue

            all_data["cell_id"].append(cell_idx)
            all_data["cycle"].append(cycle)
            all_data["soh"].append(soh)
            all_data["temp"].append(temp)
            all_data["dv_start"].append(dv)
            all_data["capacity_meas"].append(cap)
            # IC curve placeholder — filled with zeros if not available
            all_data["ic"].append(np.zeros(128, dtype=np.float32))


def _load_calce_from_details(cell_dir, cell_idx, detail_files, all_data):
    """Parse CALCE per-cycle detail CSV files."""
    import csv
    n_ic = 128
    for fpath in detail_files:
        try:
            voltage, current, time_arr = [], [], []
            with open(fpath) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    voltage.append(float(row.get("Voltage", row.get("voltage", row.get("V", 0)))))
                    current.append(float(row.get("Current", row.get("current", row.get("I", 0)))))
                    time_arr.append(float(row.get("Time", row.get("time", row.get("t", 0)))))
            if len(voltage) < 50:
                continue

            voltage = np.array(voltage)
            current = np.array(current)
            time_arr = np.array(time_arr)

            # Basic feature extraction
            charge_current = float(np.mean(current[current > 0.01]))
            if charge_current < 0.01:
                continue
            dv_start = (voltage[min(5, len(voltage)-1)] - voltage[0]) / charge_current

            dt = np.diff(time_arr, prepend=time_arr[0])
            dt = np.clip(dt, 0.1, None)
            q_ah = np.cumsum(current * dt) / 3600.0

            dv_dq = np.gradient(voltage, q_ah)
            dq_dv = 1.0 / np.clip(np.abs(dv_dq), 1e-6, None)
            dq_dv_smooth = savgol_filter(dq_dv, min(31, len(dq_dv)//2*2+1), 3)

            v_grid = np.linspace(2.8, 3.6, n_ic)
            valid_mask = (voltage > 2.8) & (voltage < 3.6)
            if valid_mask.sum() < 10:
                continue
            f = interp1d(voltage[valid_mask], dq_dv_smooth[valid_mask],
                         kind='linear', bounds_error=False, fill_value=0.0)
            ic_curve = f(v_grid)
            mx = ic_curve.max()
            if mx > 0:
                ic_curve /= mx

            all_data["cell_id"].append(cell_idx)
            all_data["cycle"].append(len(all_data["cycle"]))
            all_data["soh"].append(1.0)  # placeholder, needs external SOH labels
            all_data["temp"].append(25.0)
            all_data["ic"].append(ic_curve.astype(np.float32))
            all_data["dv_start"].append(dv_start)
            all_data["capacity_meas"].append(1.0)
        except Exception:
            continue
