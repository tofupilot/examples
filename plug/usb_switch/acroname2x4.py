from typing import Optional
from brainstem.link import Spec
from brainstem.result import Result
from brainstem.stem import USBHub2x4
from openhtf.plugs import BasePlug
from openhtf.util.configuration import CONF


class PortControlError(Exception):
    # Raised when there is a failure in controlling a port.
    pass

class PortNumberOutOfRange(Exception):
    # Raised when the specified port number is invalid or not present in the hub.
    pass

class Acroname2x4(BasePlug):
    """
    A plug for controlling the Acroname USBHub2x4 USB switch.

    Provides methods to enable or disable individual ports on the hub.
    Supports simulated mode for testing without hardware.
    """
    ports: int = 4
    serial_number: Optional[str] = None

    def __init__(self):
        self.simulated_mode: bool = getattr(CONF, 'simulated', False)
        if not self.simulated_mode:
            self.stem: USBHub2x4 = USBHub2x4()

    def open(self) -> None:
        if not self.simulated_mode:
            if self.stem.discoverAndConnect(Spec.USB) != Result.NO_ERROR:
                raise ConnectionError("Failed to connect to the USBHub2x4 device.")
            self.serial_number = str(self.stem.system.getSerialNumber())
        else:
            self.logger.info("Simulated: Opened connection (no hardware).")
            self.serial_number = "SIMULATED_SERIAL_NUMBER"

    def _validate_port_number(self, port_number: int) -> None:
        if not 0 <= port_number < self.ports:
            raise PortNumberOutOfRange(f"Port number {port_number} is out of range (0 to {self.ports - 1}).")

    def enable_port(self, port_number: int) -> None:
        self._validate_port_number(port_number)
        if self.simulated_mode:
            self.logger.info(f"Simulated: Enabled port {port_number}.")
        else:
            result: int = self.stem.usb.setPortEnable(port_number)
            if result != Result.NO_ERROR:
                raise PortControlError(f"Failed to enable port {port_number} (Error code: {result}).")

    def disable_port(self, port_number: int) -> None:
        self._validate_port_number(port_number)
        if self.simulated_mode:
            self.logger.info(f"Simulated: Disabled port {port_number}.")
        else:
            result: int = self.stem.usb.setPortDisable(port_number)
            if result != Result.NO_ERROR:
                raise PortControlError(f"Failed to disable port {port_number} (Error code: {result}).")

    def enable_only_port(self, *enabled_ports: int) -> None:
        for port in enabled_ports:
            self._validate_port_number(port)
        if self.simulated_mode:
            self.logger.info(f"Simulated: Enabled ports {enabled_ports} and disabled all others.")
        else:
            for port in range(self.ports):
                try:
                    if port in enabled_ports:
                        self.enable_port(port)
                    else:
                        self.disable_port(port)
                except PortControlError as e:
                    raise PortControlError(f"Failed to set port {port}: {e}") from e

    def disable_all_ports(self) -> None:
        if self.simulated_mode:
            self.logger.info("Simulated: Disabled all ports.")
        else:
            for port in range(self.ports):
                self.disable_port(port)

    def enable_all_ports(self) -> None:
        if self.simulated_mode:
            self.logger.info("Simulated: Enabled all ports.")
        else:
            for port in range(self.ports):
                self.enable_port(port)

    def tearDown(self) -> None:
        if not self.simulated_mode:
            self.stem.disconnect()
        else:
            self.logger.info("Simulated: Tear down. No hardware to disconnect.")
