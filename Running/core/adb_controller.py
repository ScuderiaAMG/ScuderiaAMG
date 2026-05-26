import subprocess
import shutil
import sys
from typing import Optional


class ADBController:
    def __init__(self):
        self._adb_path: str = "adb"
        self._device_id: Optional[str] = None

    def is_available(self) -> bool:
        return shutil.which(self._adb_path) is not None

    def check_or_die(self):
        if not self.is_available():
            print("❌ 未找到 ADB，请先安装 Android SDK Platform Tools")
            print("   下载地址: https://developer.android.com/tools/releases/platform-tools")
            print("   下载后将 adb.exe 所在目录添加到系统 PATH 环境变量")
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

        r = self._adb("shell", "appops", "set", "com.android.shell",
                       "android:mock_location", "allow")
        if r.returncode != 0:
            print(f"⚠ appops 设置失败: {r.stderr.strip()}")

        self._adb("shell", "cmd", "location", "providers", "remove-test-provider",
                  "gps")
        r = self._adb("shell", "cmd", "location", "providers", "add-test-provider",
                      "gps")
        if r.returncode != 0:
            print(f"❌ 无法添加 test provider: {r.stderr.strip()}")
            print("   请确认手机已开启「开发者选项 → 选择模拟位置信息应用」")
            sys.exit(1)

        print("✅ 模拟定位环境配置完成")

    def send_location(self, lat: float, lng: float):
        loc_str = f"{lat},{lng}"
        self._adb("shell", "cmd", "location", "providers",
                  "set-test-provider-location", "gps", "--location", loc_str)

    def teardown(self):
        print("🧹 正在清理模拟定位环境...")
        self._adb("shell", "cmd", "location", "providers", "remove-test-provider",
                  "gps")
        print("✅ 清理完成")
