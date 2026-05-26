import os
import subprocess
import shutil
import sys
from pathlib import Path
from typing import Optional

# 常见 ADB 安装目录，`shutil.which` 找不到时按顺序搜索
_COMMON_ADB_DIRS = [
    r"D:\Applications\platform-tools",
    r"C:\platform-tools",
    r"C:\adb",
    r"D:\adb",
]


def _find_adb() -> Optional[str]:
    found = shutil.which("adb")
    if found:
        return found
    for d in _COMMON_ADB_DIRS:
        p = Path(d) / "adb.exe"
        if p.is_file():
            return str(p)
    for base in [os.environ.get("LOCALAPPDATA", ""), "C:\\", "D:\\"]:
        if not base:
            continue
        candidate = Path(base) / "platform-tools" / "adb.exe"
        if candidate.is_file():
            return str(candidate)
    return None


class ADBController:
    def __init__(self):
        self._adb_path: str = _find_adb() or "adb"
        self._device_id: Optional[str] = None

    def is_available(self) -> bool:
        if Path(self._adb_path).is_file():
            return True
        found = _find_adb()
        if found:
            self._adb_path = found
            return True
        return False

    def check_or_die(self):
        if not self.is_available():
            print("❌ 未找到 ADB，请先安装 Android SDK Platform Tools")
            print("   下载地址: https://developer.android.com/tools/releases/platform-tools")
            print()
            print("   如果已安装但此处找不到，请尝试：")
            print("   1. 重新打开终端窗口（PATH 变更后需重启终端）")
            print("   2. 或将 adb.exe 复制到以下任一目录：")
            for d in _COMMON_ADB_DIRS:
                print(f"      {d}")
            sys.exit(1)

    def get_devices(self) -> list[str]:
        result = subprocess.run(
            [self._adb_path, "devices"], capture_output=True, text=True
        )
        lines = result.stdout.strip().split("\n")[1:]
        devices = []
        for line in lines:
            if "\tdevice" in line:
                devices.append(line.split("\t")[0])
        return devices

    def check_device(self) -> str:
        devices = self.get_devices()
        if not devices:
            print("❌ 未检测到已连接的 Android 设备")
            print("   请确保:")
            print("   1. 手机已通过 USB 连接到电脑")
            print("   2. 手机已开启 USB 调试")
            print("   3. 手机上已授权此电脑的调试请求")
            sys.exit(1)
        self._device_id = devices[0]
        if len(devices) > 1:
            print(f"⚠ 检测到多台设备，使用第一台: {self._device_id}")
        return self._device_id

    def _adb(self, *args) -> subprocess.CompletedProcess:
        cmd = [self._adb_path]
        if self._device_id:
            cmd.extend(["-s", self._device_id])
        cmd.extend(args)
        return subprocess.run(cmd, capture_output=True, text=True)

    def _adb_out(self, *args) -> str:
        return self._adb(*args).stdout.strip()

    # ─── 诊断 ─────────────────────────────────

    def diagnose(self):
        """打印详细定位状态，帮助排查 mock 失败原因"""
        print("=" * 60)
        print("  定位诊断报告")
        print("=" * 60)

        # 基本状态
        print("\n── 设备信息 ──")
        brand = self._adb_out("shell", "getprop", "ro.product.brand")
        model = self._adb_out("shell", "getprop", "ro.product.model")
        android = self._adb_out("shell", "getprop", "ro.build.version.release")
        print(f"  品牌/型号: {brand} {model}  |  Android {android}")

        # Mock 权限
        print("\n── Mock 权限 ──")
        r = self._adb("shell", "appops", "get", "com.android.shell",
                       "android:mock_location")
        print(f"  shell mock_location: {r.stdout.strip()}")

        r = self._adb("shell", "settings", "get", "secure", "mock_location")
        print(f"  secure.mock_location: {r.stdout.strip()}")

        # GPS 状态
        print("\n── GPS / 定位状态 ──")
        mode = self._adb_out("shell", "settings", "get", "secure", "location_mode")
        mode_map = {"0": "关闭", "1": "仅GPS", "2": "仅网络", "3": "高精度"}
        print(f"  location_mode: {mode} ({mode_map.get(mode, '未知')})")

        enabled = self._adb_out("shell", "cmd", "location", "is-location-enabled")
        print(f"  is-location-enabled: {enabled}")

        # Test Provider 状态
        print("\n── Test Provider 状态 ──")
        for provider in ["gps", "network"]:
            pos = self._adb("shell", "cmd", "location", "providers",
                            "get-test-provider-location", provider)
            loc_str = pos.stdout.strip() if pos.returncode == 0 else "(获取失败)"
            print(f"  {provider}: {loc_str[:120]}")

        # 系统中已有的 LocationProvider
        print("\n── 系统定位提供者 ──")
        r = self._adb("shell", "dumpsys", "location")
        for line in r.stdout.split("\n"):
            line = line.strip()
            if any(kw in line.lower() for kw in
                   ["test", "mock", "gps", "network", "passive", "fused",
                    "is_enabled", "provider", "is mock"]):
                if len(line) < 200:
                    print(f"  {line}")

        # 关键判断
        print("\n── 诊断结论 ──")
        if mode == "0":
            print("  ⚠ GPS 处于关闭状态！请手动打开手机 GPS")
        pos_gps = self._adb_out("shell", "cmd", "location", "providers",
                                 "get-test-provider-location", "gps")
        if "null" in pos_gps.lower() or not pos_gps.strip():
            print("  ⚠ gps test provider 未设置有效位置，setup_mock 可能未执行或失败了")
        else:
            print(f"  ✓ gps test provider 坐标已注入: {pos_gps[:80]}")
            print("  → 如果 App 里程仍不增加，说明 App 可能绕过了系统 GPS")
            print("  → 常见原因：App 使用高德/百度地图 SDK 或 Google FusedLocation")
            print("  → 这种情况需要换用 Mock GPS App 方案，参考 README")

        print("=" * 60)

    # ─── Mock 环境 ────────────────────────────

    def setup_mock(self):
        print("🔧 正在配置模拟定位环境...")

        # 1. 授权
        r = self._adb("shell", "appops", "set", "com.android.shell",
                       "android:mock_location", "allow")
        if r.returncode != 0:
            print(f"⚠ appops 设置失败: {r.stderr.strip()}")

        # 2. 强开 GPS
        self._adb("shell", "settings", "put", "secure", "location_mode", "3")
        self._adb("shell", "cmd", "location", "set-location-enabled", "true")

        # 3. 重建 gps + network 两个 test provider
        for provider in ["gps", "network"]:
            self._adb("shell", "cmd", "location", "providers",
                       "remove-test-provider", provider)

        r_gps = self._adb("shell", "cmd", "location", "providers",
                           "add-test-provider", "gps")
        r_net = self._adb("shell", "cmd", "location", "providers",
                           "add-test-provider", "network")

        if r_gps.returncode != 0 and r_net.returncode != 0:
            print(f"❌ 无法添加 test provider: {r_gps.stderr.strip()}")
            print("   请确认手机已开启「开发者选项 → USB 调试」")
            sys.exit(1)

        # 4. 启用
        for provider in ["gps", "network"]:
            self._adb("shell", "cmd", "location", "providers",
                       "set-test-provider-enabled", provider, "true")

        # 5. 初始定位 + 验证
        self.send_location(30.508800, 114.411500)

        verify = self._adb("shell", "cmd", "location", "providers",
                            "get-test-provider-location", "gps")
        if verify.returncode == 0 and "30.508" in verify.stdout:
            print("✅ 模拟定位环境配置完成（gps 已验证）")
        else:
            print("✅ 模拟定位环境配置完成")
            print(f"   (gps 回读: {verify.stdout.strip()[:100]})")

        # 6. 额外提示
        net_verify = self._adb("shell", "cmd", "location", "providers",
                                "get-test-provider-location", "network")
        if net_verify.returncode == 0 and "30.508" in net_verify.stdout:
            print("   (network 已验证)")
        else:
            print(f"   (network 回读: {net_verify.stdout.strip()[:100]})")

    def send_location(self, lat: float, lng: float):
        loc_str = f"{lat},{lng}"
        for provider in ["gps", "network"]:
            self._adb("shell", "cmd", "location", "providers",
                       "set-test-provider-location", provider,
                       "--location", loc_str,
                       "--accuracy", "5")

    def teardown(self):
        print("🧹 正在清理模拟定位环境...")
        for provider in ["gps", "network"]:
            self._adb("shell", "cmd", "location", "providers",
                       "set-test-provider-enabled", provider, "false")
            self._adb("shell", "cmd", "location", "providers",
                       "remove-test-provider", provider)
        print("✅ 清理完成")
