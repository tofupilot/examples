import platform
import subprocess
from typing import List
from openhtf.plugs import BasePlug
from openhtf.util.configuration import CONF


class Lsusb(BasePlug):
    """
    A plug to list connected USB devices, providing their VID:PID pairs.

    Supports both Linux and Windows platforms, with an option for simulated output.
    """

    def __init__(self):
        self.simulated_mode: bool = CONF.get('simulated', False)

    def list_devices(self) -> List[str]:
        if self.simulated_mode:
            self.logger.info(
                "Running in simulated mode.\n"
                "Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub\n"
                "Bus 001 Device 002: ID 04f5:0c7f Fingerprint sensor\n"
                "Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub\n"
                "Bus 003 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub\n"
                "Bus 003 Device 002: ID 8087:0032 Drone in DFU mode"
            )
            # Return a list of VID:PID pairs simulating multiple USB devices
            return ["1d6b:0002", "04f5:0c7f", "1d6b:0003", "1d6b:0002", "8087:0032"]
        else:
            system = platform.system()
            if system == "Linux":
                return self._list_devices_linux()
            elif system == "Windows":
                return self._list_devices_windows()
            else:
                raise RuntimeError(f"Unsupported platform: {system}")

    def _list_devices_linux(self) -> List[str]:
        try:
            output = subprocess.check_output("lsusb", shell=True, text=True)
            self.logger.info("lsusb output:\n" + output)
            vid_pid_list = []
            for line in output.strip().split('\n'):
                parts = line.split()
                if len(parts) >= 6 and ':' in parts[5]:
                    vid_pid = parts[5]
                    vid_pid_list.append(vid_pid)
            return vid_pid_list
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to run 'lsusb': {e}") from e

    def _list_devices_windows(self) -> List[str]:
        try:
            powershell_cmd = [
                'powershell', '-Command',
                'Get-PnpDevice -Class USB | Select-Object -ExpandProperty InstanceId'
            ]
            output = subprocess.check_output(powershell_cmd, text=True)
            self.logger.info("PowerShell output:\n" + output)
            vid_pid_list = []
            for line in output.strip().split('\n'):
                line = line.strip()
                if line.startswith("USB\\VID_"):
                    vid_pid_part = line.split('\\')[1]
                    vid_pid_pairs = vid_pid_part.split('&')
                    vid = ''
                    pid = ''
                    for pair in vid_pid_pairs:
                        if pair.startswith('VID_'):
                            vid = pair[4:]
                        elif pair.startswith('PID_'):
                            pid = pair[4:]
                    if vid and pid:
                        vid_pid_list.append(f"{vid.lower()}:{pid.lower()}")
            return vid_pid_list
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to list USB devices on Windows: {e}") from e
