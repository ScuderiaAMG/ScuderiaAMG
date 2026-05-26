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
    """查找 adb.exe，优先 PATH，其次常见目录"""
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

    def setup_mock(self):
        print("🔧 正在配置模拟定位环境...")

        # 1. 授权 shell 模拟定位权限
        r = self._adb("shell", "appops", "set", "com.android.shell",
                       "android:mock_location", "allow")
        if r.returncode != 0:
            print(f"⚠ appops 设置失败: {r.stderr.strip()}")

        # 2. 强制开启手机 GPS（location_mode: 0=off, 1=gps, 2=network, 3=high_accuracy）
        self._adb("shell", "settings", "put", "secure", "location_mode", "3")

        # 3. 启用全局定位服务
        self._adb("shell", "cmd", "location", "set-location-enabled", "true")

        # 4. 清理旧 provider，重新创建
        self._adb("shell", "cmd", "location", "providers", "remove-test-provider", "gps")

        r = self._adb("shell", "cmd", "location", "providers", "add-test-provider",
                       "gps", "gps", "network")
        if r.returncode != 0:
            print(f"❌ 无法添加 test provider: {r.stderr.strip()}")
            print("   请确认手机已开启「开发者选项 → USB 调试」")
            print("   以及在开发者选项中能找到「选择模拟位置信息应用」")
            sys.exit(1)

        # 5. 启用 test provider（关键步骤！不加这行 mock 不会生效）
        r = self._adb("shell", "cmd", "location", "providers",
                       "set-test-provider-enabled", "gps", "true")
        if r.returncode != 0:
            print(f"⚠ 启用 test provider 失败: {r.stderr.strip()}")

        # 6. 发送一个初始位置做验证
        r = self._adb("shell", "cmd", "location", "providers",
                       "set-test-provider-location", "gps",
                       "--location", "30.508800,114.411500",
                       "--accuracy", "5")
        if r.returncode != 0:
            print(f"⚠ 初始定位注入失败: {r.stderr.strip()}")

        # 7. 回读验证
        verify = self._adb("shell", "cmd", "location", "providers",
                            "get-test-provider-location", "gps")
        if "30.508" in verify.stdout and "114.411" in verify.stdout:
            print("✅ 模拟定位环境配置完成（已验证）")
        else:
            print("✅ 模拟定位环境配置完成")
            print(f"   (验证回读: {verify.stdout.strip()[:120]})")

    def send_location(self, lat: float, lng: float):
        loc_str = f"{lat},{lng}"
        self._adb("shell", "cmd", "location", "providers",
                  "set-test-provider-location", "gps",
                  "--location", loc_str,
                  "--accuracy", "5")

    def teardown(self):
        print("🧹 正在清理模拟定位环境...")
        self._adb("shell", "cmd", "location", "providers",
                   "set-test-provider-enabled", "gps", "false")
        self._adb("shell", "cmd", "location", "providers",
                   "remove-test-provider", "gps")
        print("✅ 清理完成")
