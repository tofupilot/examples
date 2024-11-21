import subprocess, time

import openhtf as htf


class DfuUtil(htf.plugs.BasePlug):
    def flash_firmware(self, simulated=False, firmware_path="/..", vid_pid=None):
        # Define the command to flash firmware using dfu-util
        command = [
            "dfu-util",
            "-D", firmware_path
        ]

        if vid_pid:
            command.extend(["-d", vid_pid])

        if simulated:
            self.logger.info("Running in simulated mode. Flashing operation is mocked.")
            time.sleep(3)
            return True
        else:
            try:
                # Run dfu-util using subprocess
                subprocess.run(command, check=True)
                return True
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Flashing failed: {str(e)}")
                return False
            except FileNotFoundError:
                self.logger.error(
                    "dfu-util executable not found. Please ensure dfu-util is installed and available in PATH.")
                return False
