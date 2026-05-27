import subprocess
import time
import math
import threading
import msvcrt
import random

# ======================================================================
# 配置区（修改参数在这里）（仅对于Lenovo83BF可用）
# ======================================================================

MUMU_PATH = r"D:\Applications\MuMuPlayer\nx_main\MuMuManager.exe"
VM_INDEX = 0

# 东操中心（华中科技大学）
CENTER_LAT = 30.518621
CENTER_LON = 114.437872

# 操场参数
STRAIGHT_LENGTH = 100.0      # 直道（米）
CURVE_LENGTH = 100.0         # 弯道弧长（米）
TOTAL_LAPS = 8               # 圈数

# 速度参数
BASE_SPEED_KPH = 9           # 基准速度（建议 8~10）
UPDATE_INTERVAL_SEC = 2      # 基础更新间隔

# ---- 真实性增强参数 ----
ALTITUDE_BASE = 30           # 武汉海拔约30米

# ======================================================================
# 核心：Ornstein-Uhlenbeck 过程（模拟真实 GPS 漂移）
# ======================================================================
# 真实 GPS 的核心特征：误差不是每帧独立的，而是有时间相关性（漂移）
# 如果当前位置偏东5米，下一帧大概率也偏东4~6米，不会突然跳到偏西
# OU 过程完美模拟这个特性：均值回归 + 随机扰动

class OUSource:
    """Ornstein-Uhlenbeck 随机过程，模拟真实 GPS 漂移"""
    def __init__(self, theta=0.15, sigma=3.0, mean=0.0):
        """
        theta: 均值回归速度（越小漂移越持久，越大越快回归）
        sigma: 随机扰动强度（米）
        mean: 长期均值
        """
        self.theta = theta
        self.sigma = sigma
        self.mean = mean
        self.value = random.gauss(mean, sigma * 0.3)  # 初始偏差较小

    def step(self, dt=1.0):
        """推进一步，dt 为时间步长"""
        drift = self.theta * (self.mean - self.value) * dt
        diffusion = self.sigma * math.sqrt(dt) * random.gauss(0, 1)
        self.value += drift + diffusion
        return self.value

# ======================================================================
# 核心：速度平滑器（模拟真实人的加速惯性）
# ======================================================================

class SmoothSpeed:
    """
    平滑速度控制器 —— 真实人不可能瞬间变速
    速度变化有惯性：加速需要时间，减速也需要时间
    同时引入呼吸节奏（约 3~4 秒一个周期的微小速度波动）
    """
    def __init__(self, base_speed_kph):
        self.current_speed = base_speed_kph * 0.3  # 从慢速起步
        self.target_speed = base_speed_kph
        self.base_speed = base_speed_kph
        # 平滑系数：每秒向目标速度靠近的比例（越小越平滑）
        self.smoothing = 0.08
        # 呼吸节奏参数
        self.breath_phase = random.uniform(0, 2 * math.pi)
        self.breath_freq = random.uniform(0.25, 0.4)  # 约 2.5~4 秒一个呼吸
        self.breath_amplitude = 0.15  # 呼吸导致的速度波动 ±15%
        # 疲劳参数：后半程速度逐渐下降
        self.fatigue_rate = 0.02  # 每圈速度下降 2%
        self.lap_count = 0

    def set_target(self, target):
        """设置目标速度（不会瞬间到达）"""
        self.target_speed = target

    def next_lap(self):
        """每圈调用，加入疲劳效应"""
        self.lap_count += 1
        fatigue_factor = 1.0 - self.fatigue_rate * self.lap_count
        # 后半程每圈随机决定是否"缓一缓"
        if self.lap_count > TOTAL_LAPS // 2 and random.random() < 0.3:
            fatigue_factor *= random.uniform(0.85, 0.95)
        new_target = self.base_speed * fatigue_factor
        # 加入圈间随机波动（高斯分布，不是均匀分布！）
        new_target *= (1 + random.gauss(0, 0.06))
        self.set_target(max(self.base_speed * 0.6, new_target))

    def step(self, dt=1.0):
        """推进速度，返回当前速度"""
        # 平滑地向目标速度靠近（指数移动平均）
        self.current_speed += self.smoothing * (self.target_speed - self.current_speed) * dt
        # 叠加呼吸节奏
        self.breath_phase += self.breath_freq * dt
        breath_mod = 1.0 + self.breath_amplitude * math.sin(self.breath_phase)
        # 微小的步频不规则性
        stride_jitter = 1.0 + random.gauss(0, 0.02)
        return max(self.base_speed * 0.4, self.current_speed * breath_mod * stride_jitter)


# ======================================================================
# 核心：海拔平滑器
# ======================================================================

class SmoothAltitude:
    """海拔平滑控制器 —— 真实 GPS 海拔有漂移但不会每帧跳变"""
    def __init__(self, base_alt=30.0, noise_range=3.0):
        self.base_alt = base_alt
        self.current_alt = base_alt + random.gauss(0, 1)
        self.ou = OUSource(theta=0.05, sigma=noise_range * 0.5, mean=0)

    def step(self, dt=1.0):
        drift = self.ou.step(dt)
        self.current_alt = self.base_alt + drift
        return self.current_alt


# ======================================================================
# 全局控制
# ======================================================================

is_paused = False
should_exit = False

# ======================================================================
# 核心逻辑
# ======================================================================

def send_location(lat, lon, alt=None):
    """向 MuMu 发送坐标（含可选海拔）"""
    if alt is not None:
        cmd = f'"{MUMU_PATH}" control -v {VM_INDEX} tool location -lat {lat} -lon {lon} -alt {alt}'
    else:
        cmd = f'"{MUMU_PATH}" control -v {VM_INDEX} tool location -lat {lat} -lon {lon}'
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def get_curve_speed_factor(distance, straight_len, curve_len):
    """
    弯道减速因子 —— 真实跑者在弯道会自然减速
    直道: 1.0 (全速)
    弯道: 0.85~0.92 (减速 8~15%)
    过渡是平滑的，不是突变
    """
    total_length = 2 * straight_len + 2 * curve_len
    distance = distance % total_length

    # 判断是否在弯道区域，以及弯道内的相对位置
    if distance < straight_len:
        # 东直道
        return 1.0
    elif distance < straight_len + curve_len:
        # 北弯道 —— 进弯减速、出弯加速
        t = (distance - straight_len) / curve_len  # 0~1
        return 0.88 + 0.12 * (2 * t - 1) ** 2  # 两端慢中间快一点
    elif distance < 2 * straight_len + curve_len:
        # 西直道
        return 1.0
    else:
        # 南弯道
        t = (distance - 2 * straight_len - curve_len) / curve_len
        return 0.88 + 0.12 * (2 * t - 1) ** 2


def calculate_track_position_raw(distance, straight_len, curve_len):
    """
    计算在400米标准操场上的【原始】位置（不含噪声）
    ---
    操场布局（南北走向，逆时针）:
          北
      ┌────┐
    ← │    │ ←  ←  ←  逆时针
      └────┘
          南
    """
    total_length = 2 * straight_len + 2 * curve_len
    distance = distance % total_length

    curve_radius = curve_len / math.pi

    if distance < straight_len:
        # ① 东直道（南→北）
        x = curve_radius
        y = -straight_len / 2 + distance

    elif distance < straight_len + curve_len:
        # ② 北弯道（东→西，逆时针半圆）
        segment_dist = distance - straight_len
        angle = (segment_dist / curve_len) * math.pi
        x = curve_radius * math.cos(angle)
        y = (straight_len / 2) + curve_radius * math.sin(angle)

    elif distance < 2 * straight_len + curve_len:
        # ③ 西直道（北→南）
        segment_dist = distance - (straight_len + curve_len)
        x = -curve_radius
        y = straight_len / 2 - segment_dist

    else:
        # ④ 南弯道（西→东，逆时针半圆）
        segment_dist = distance - (2 * straight_len + curve_len)
        angle = (segment_dist / curve_len) * math.pi
        x = -curve_radius * math.cos(angle)
        y = (-straight_len / 2) - curve_radius * math.sin(angle)

    return x, y


def get_interval():
    """
    真实 GPS 采样间隔 —— 不是均匀分布！
    真实手机 GPS 采样间隔大致服从对数正态分布
    大部分 1~3 秒，偶尔 4~6 秒（信号不佳时）
    """
    # 对数正态分布模拟真实 GPS 间隔
    mu = math.log(UPDATE_INTERVAL_SEC) - 0.1
    sigma = 0.35
    interval = random.lognormvariate(mu, sigma)
    return max(0.8, min(6.0, interval))  # 钳制在合理范围


def occasional_long_pause():
    """
    偶尔产生一次较长停顿 —— 模拟真实跑者偶尔减速或走几步
    概率约 5%，模拟调整鞋带、擦汗、调整呼吸等
    """
    if random.random() < 0.03:
        return random.uniform(3.0, 8.0)
    return 0


def run_track(center_lat, center_lon, straight_len, curve_len,
              base_speed_kph, interval_sec, laps):
    """主跑步循环 —— 全面优化版"""
    global is_paused, should_exit

    total_length = 2 * straight_len + 2 * curve_len
    print(f"[操场] 标准400米操场：直道{straight_len}米，弯道{curve_len}米")
    print(f"[距离] 总长 {total_length}米 x {laps}圈 = {total_length * laps / 1000:.1f}公里")
    print(f"[速度] 基准速度：{base_speed_kph}km/h")

    # ---- 初始化各平滑器 ----
    # GPS 漂移：X 和 Y 方向各一个 OU 过程（独立漂移，模拟真实 GPS）
    # sigma=1.8 → 稳态标准差约 1.8/sqrt(2*0.15) ≈ 3.3米，偏移95%在±6米内
    gps_ou_x = OUSource(theta=0.15, sigma=1.8, mean=0)
    gps_ou_y = OUSource(theta=0.15, sigma=1.8, mean=0)

    # 速度平滑器
    speed_ctrl = SmoothSpeed(base_speed_kph)

    # 海拔平滑器
    alt_ctrl = SmoothAltitude(ALTITUDE_BASE, noise_range=2.0)

    current_distance = 0.0
    current_lap = -1
    step_count = 0

    # 记录上一次位置，用于偶尔产生"原地微漂"效果
    last_x, last_y = 0, 0

    while current_distance < (laps * total_length) and not should_exit:
        if not is_paused:
            lap_now = int(current_distance / total_length)

            # 每圈更新目标速度（含疲劳效应）
            if lap_now > current_lap:
                speed_ctrl.next_lap()
                if current_lap >= 0:
                    print(f"\n[完成] 第 {lap_now} 圈")
                print(f"[圈数] 第 {lap_now + 1}/{laps} 圈 | 目标速度 {speed_ctrl.target_speed:.1f}km/h")
                current_lap = lap_now

            # 当前时间步长
            actual_interval = get_interval()

            # 偶尔产生较长停顿（模拟调整鞋带等）
            extra_pause = occasional_long_pause()
            if extra_pause > 0:
                actual_interval += extra_pause

            # 获取当前平滑速度
            current_speed = speed_ctrl.step(actual_interval)

            # 弯道减速
            curve_factor = get_curve_speed_factor(current_distance, straight_len, curve_len)
            current_speed *= curve_factor

            # 热身段：前80米逐渐加速（不是线性的，用 ease-in 曲线）
            if current_distance < 80:
                warmup_t = current_distance / 80
                warmup_ratio = warmup_t ** 2  # 二次缓入，起步慢后加速
                current_speed *= max(0.3, warmup_ratio)

            # 计算本步距离
            distance_this_step = (current_speed * 1000 / 3600) * actual_interval

            # 不要超过剩余距离
            remaining = laps * total_length - current_distance
            distance_this_step = min(distance_this_step, remaining)

            # 计算原始轨迹位置
            x_raw, y_raw = calculate_track_position_raw(
                current_distance, straight_len, curve_len
            )

            # 应用 OU 过程 GPS 漂移（核心！这是有自相关的噪声）
            noise_x = gps_ou_x.step(actual_interval)
            noise_y = gps_ou_y.step(actual_interval)

            # 偶尔模拟 GPS "闪断"（概率 1.2%，偏移稍大但不夸张）
            if random.random() < 0.012:
                noise_x += random.gauss(0, 5)
                noise_y += random.gauss(0, 5)

            x_final = x_raw + noise_x
            y_final = y_raw + noise_y

            # 米 → 经纬度
            lat_offset = y_final / 111319.0
            lon_offset = x_final / (111319.0 * math.cos(math.radians(center_lat)))

            current_lat = center_lat + lat_offset
            current_lon = center_lon + lon_offset

            # 海拔
            altitude = alt_ctrl.step(actual_interval)

            # 发送
            send_location(current_lat, current_lon, altitude)

            last_x, last_y = x_final, y_final
            current_distance += distance_this_step
            step_count += 1

            # 进度输出
            if step_count % 30 == 0:
                dist_km = current_distance / 1000
                print(f"  [{dist_km:.2f}km] 速度 {current_speed:.1f}km/h | "
                      f"GPS偏移 ({noise_x:+.1f}, {noise_y:+.1f})m")

        else:
            # 暂停状态：模拟人在原地但 GPS 仍在漂移
            noise_x = gps_ou_x.step(2.0)
            noise_y = gps_ou_y.step(2.0)
            x_raw, y_raw = calculate_track_position_raw(
                current_distance, straight_len, curve_len
            )
            # 暂停时额外加小幅漂移
            x_final = x_raw + noise_x + random.gauss(0, 0.8)
            y_final = y_raw + noise_y + random.gauss(0, 0.8)
            lat_offset = y_final / 111319.0
            lon_offset = x_final / (111319.0 * math.cos(math.radians(center_lat)))
            current_lat = center_lat + lat_offset
            current_lon = center_lon + lon_offset
            altitude = alt_ctrl.step(2.0)
            send_location(current_lat, current_lon, altitude)
            actual_interval = get_interval()

        time.sleep(actual_interval)

    if not should_exit:
        print(f"\n[完成] 全部 {laps} 圈！共 {total_length * laps / 1000:.2f} 公里")

    # 跑完多发几次当前位置，GPS 漂移逐渐减小
    print("\n[结束] 跑步完成，保持最后位置...")
    for i in range(4):
        noise_x = gps_ou_x.step(1.5) * (0.7 ** i)  # 漂移逐渐收敛
        noise_y = gps_ou_y.step(1.5) * (0.7 ** i)
        x_raw, y_raw = calculate_track_position_raw(current_distance, straight_len, curve_len)
        x_final = x_raw + noise_x
        y_final = y_raw + noise_y
        lat_final = center_lat + y_final / 111319.0
        lon_final = center_lon + x_final / (111319.0 * math.cos(math.radians(center_lat)))
        alt_final = alt_ctrl.step(1.5)
        send_location(lat_final, lon_final, alt_final)
        time.sleep(1.5)


def keyboard_listener():
    """键盘监听线程"""
    global is_paused, should_exit

    print("\n[控制] 空格=暂停/继续 | Q=退出\n")

    while not should_exit:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b' ':
                is_paused = not is_paused
                if is_paused:
                    print("[暂停] GPS仍在微漂移")
                else:
                    print("[继续] 跑步中...")
            elif key == b'q' or key == b'Q':
                print("[退出] 正在退出...")
                should_exit = True
        time.sleep(0.1)


if __name__ == "__main__":
    print("=" * 50)
    print("  华中大体育 - 优化版虚拟跑步")
    print("  GPS漂移模型: Ornstein-Uhlenbeck (自相关)")
    print("  速度模型: 平滑惯性 + 呼吸节奏 + 疲劳")
    print("  弯道减速 + 高斯分布 + 对数正态间隔")
    print("=" * 50)

    import os
    if not os.path.exists(MUMU_PATH):
        print(f"[错误] 找不到 MuMuManager.exe！")
        print(f"  当前路径：{MUMU_PATH}")
    else:
        listener_thread = threading.Thread(target=keyboard_listener, daemon=True)
        listener_thread.start()

        try:
            run_track(
                CENTER_LAT, CENTER_LON,
                STRAIGHT_LENGTH, CURVE_LENGTH,
                BASE_SPEED_KPH, UPDATE_INTERVAL_SEC, TOTAL_LAPS
            )
        except KeyboardInterrupt:
            print("\n[中断] Ctrl+C")
        finally:
            print("[结束] 程序结束")