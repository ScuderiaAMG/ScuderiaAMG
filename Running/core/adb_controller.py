import os
import subprocess
import shutil
import sys
from pathlib import Path
from typing import Optional

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


def _safe(s: Optional[str]) -> str:
    """安全转字符串，处理 None"""
    return (s or "").strip()


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
        return subprocess.run(cmd, capture_output=True, text=True,
                              encoding="utf-8", errors="replace")

    def _adb_out(self, *args) -> str:
        return _safe(self._adb(*args).stdout)

    # ─── 诊断 ─────────────────────────────────

    def diagnose(self):
        print("=" * 60)
        print("  定位诊断报告")
        print("=" * 60)

        # 设备信息
        print("\n── 设备信息 ──")
        brand = self._adb_out("shell", "getprop", "ro.product.brand")
        model = self._adb_out("shell", "getprop", "ro.product.model")
        android = self._adb_out("shell", "getprop", "ro.build.version.release")
        print(f"  品牌/型号: {brand} {model}  |  Android {android}")

        # Mock 权限
        print("\n── Mock 权限 ──")
        r = self._adb("shell", "appops", "get", "com.android.shell",
                       "android:mock_location")
        print(f"  shell mock_location: {_safe(r.stdout)}")

        mock_setting = self._adb_out("shell", "settings", "get", "secure", "mock_location")
        print(f"  secure.mock_location: {mock_setting}")
        if mock_setting == "0":
            print("    ⚠ 系统级 mock 开关是关闭的！这会导致 mock 定位无法被 App 读取")
            print("    → 请手动操作: 手机 设置 → 开发者选项 → 找到「允许模拟位置」并打开")
            print("    → 或在 setup_mock 时会自动尝试开启")

        # GPS 状态
        print("\n── GPS / 定位状态 ──")
        mode = self._adb_out("shell", "settings", "get", "secure", "location_mode")
        mode_map = {"0": "关闭", "1": "仅GPS", "2": "仅网络", "3": "高精度"}
        print(f"  location_mode: {mode} ({mode_map.get(mode, '未知')})")
        print(f"  is-location-enabled: {self._adb_out('shell', 'cmd', 'location', 'is-location-enabled')}")

        # Test Provider 状态（当前可能不存在）
        print("\n── Test Provider 当前状态 ──")
        for provider in ["gps", "network"]:
            pos = self._adb("shell", "cmd", "location", "providers",
                            "get-test-provider-location", provider)
            loc_str = _safe(pos.stdout) if pos.returncode == 0 else "(命令失败)"
            if not loc_str or "null" in loc_str.lower():
                loc_str = "(未设置 — setup_mock 尚未执行)"
            print(f"  {provider}: {loc_str[:120]}")

        # 尝试快速建立 test provider 看是否支持
        print("\n── 试探性创建 Test Provider ──")
        self._adb("shell", "cmd", "location", "providers", "remove-test-provider", "diag-gps")
        r = self._adb("shell", "cmd", "location", "providers",
                       "add-test-provider", "diag-gps")
        if r.returncode == 0:
            self._adb("shell", "cmd", "location", "providers",
                       "set-test-provider-enabled", "diag-gps", "true")
            self._adb("shell", "cmd", "location", "providers",
                       "set-test-provider-location", "diag-gps",
                       "--location", "30.508800,114.411500")
            verify = self._adb_out("shell", "cmd", "location", "providers",
                                    "get-test-provider-location", "diag-gps")
            if "30.508" in verify:
                print(f"  ✓ 成功: test provider 可正常读写坐标")
            else:
                print(f"  ⚠ 添加成功但回读失败: {verify[:120]}")
            # 清理
            self._adb("shell", "cmd", "location", "providers", "remove-test-provider", "diag-gps")
        else:
            err = _safe(r.stderr) or _safe(r.stdout)
            print(f"  ❌ test provider 创建失败: {err[:200]}")
            print(f"  → Android {android} / {brand} {model} 可能不支持 cmd location test provider")
            print(f"  → 需要换用 Mock GPS App 方案")

        # 诊断结论
        print("\n── 诊断结论 ──")
        issues = []
        if mode == "0":
            issues.append("GPS 关闭 → 手动打开手机 GPS")
        if mock_setting == "0":
            issues.append("secure.mock_location=0 → 开发者选项中开启「允许模拟位置」")
        if r.returncode != 0:
            issues.append("test provider 创建失败 → 该设备不支持 cmd location，需换方案")
        if not issues:
            print("  ✓ 环境检查通过，setup_mock 应该可以正常工作")
            print("  → 如果 App 里程仍不增加，是 App 自身绕过了系统定位（常见于高德/百度地图 SDK）")
        else:
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")
        print("=" * 60)

    # ─── Mock 环境 ────────────────────────────

    def setup_mock(self):
        print("🔧 正在配置模拟定位环境...")

        # 1. 系统级 mock 开关（HyperOS/Android 14+ 仍然需要）
        before = self._adb_out("shell", "settings", "get", "secure", "mock_location")
        if before == "0":
            print("   secure.mock_location 当前为 0，正在设为 1...")
            self._adb("shell", "settings", "put", "secure", "mock_location", "1")
            after = self._adb_out("shell", "settings", "get", "secure", "mock_location")
            if after == "1":
                print("   ✓ 已开启")
            else:
                print(f"   ⚠ 设置失败（当前值: {after}），请手动在手机 开发者选项 → 允许模拟位置 中开启")

        # 2. Shell 权限
        self._adb("shell", "appops", "set", "com.android.shell",
                   "android:mock_location", "allow")

        # 3. 强开 GPS
        self._adb("shell", "settings", "put", "secure", "location_mode", "3")
        self._adb("shell", "cmd", "location", "set-location-enabled", "true")

        # 4. 重建 gps + network 双 provider
        for provider in ["gps", "network"]:
            self._adb("shell", "cmd", "location", "providers",
                       "remove-test-provider", provider)

        r_gps = self._adb("shell", "cmd", "location", "providers",
                           "add-test-provider", "gps")
        r_net = self._adb("shell", "cmd", "location", "providers",
                           "add-test-provider", "network")

        if r_gps.returncode != 0 and r_net.returncode != 0:
            err = _safe(r_gps.stderr) or _safe(r_gps.stdout)
            print(f"❌ 无法添加 test provider: {err}")
            print("   该设备可能不支持 cmd location test provider")
            print("   需要换用 Mock GPS App 方案，参考 README")
            sys.exit(1)

        # 5. 启用
        for provider in ["gps", "network"]:
            self._adb("shell", "cmd", "location", "providers",
                       "set-test-provider-enabled", provider, "true")

        # 6. 初始定位 + 验证
        self.send_location(30.508800, 114.411500)

        ok_gps = False
        verify = self._adb("shell", "cmd", "location", "providers",
                            "get-test-provider-location", "gps")
        if verify.returncode == 0 and "30.508" in verify.stdout:
            ok_gps = True

        if ok_gps:
            print("✅ 模拟定位环境配置完成（gps 已验证）")
        else:
            print("✅ 模拟定位环境配置完成")
            print(f"   (gps 回读: {_safe(verify.stdout)[:100]})")

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
