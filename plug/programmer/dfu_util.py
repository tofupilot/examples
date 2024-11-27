import subprocess
import time
from typing import Optional
from openhtf.plugs import BasePlug
from openhtf.util.configuration import CONF

class DfuUtil(BasePlug):
    """
    A plug for flashing firmware to a device using dfu-util.

    Supports both real and simulated modes for flashing.
    """

    def __init__(self):
        self.simulated_mode: bool = getattr(CONF, 'simulated', False)

    def flash_firmware(self, firmware_path: str = "/..", vid_pid: Optional[str] = None) -> bool:
        """
        Flash firmware to the device using dfu-util.

        Args:
            firmware_path (str): Path to the firmware file to be flashed.
            vid_pid (Optional[str]): USB VID:PID of the device, if needed.

        Returns:
            bool: True if the flashing was successful, False otherwise.
        """
        command = ["dfu-util", "-D", firmware_path]

        if vid_pid:
            command.extend(["-d", vid_pid])

        if self.simulated_mode:
            self.logger.info("Running in simulated mode. Flashing operation is mocked.")
            time.sleep(3)
            return True

        try:
            subprocess.run(command, check=True)
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Flashing failed: {e}")
            return False
        except FileNotFoundError:
            self.logger.error("dfu-util executable not found. Please ensure dfu-util is installed and available in PATH.")
            return False
