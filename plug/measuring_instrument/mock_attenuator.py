# plug/measuring_instrument/mock_attenuator.py
import time
from openhtf.plugs import BasePlug
from openhtf.util.configuration import CONF

class MockAttenuator(BasePlug):
    """
    A mock plug for simulating an attenuator device.

    Provides methods to connect to the attenuator and set attenuation levels.
    This class operates in simulated mode.
    """

    def __init__(self):
        self.simulated_mode: bool = getattr(CONF, 'simulated', True)
        self.connected: bool = False

    def connect(self) -> bool:
        """
        Simulate connecting to the attenuator.

        Returns:
            bool: True if connected successfully, False otherwise.
        """
        if self.simulated_mode:
            self.logger.info("Simulated: Connecting to attenuator.")
            time.sleep(0.5)
            self.connected = True
            return True
        else:
            self.logger.error("MockAttenuator: This is a mock plug. Actual hardware interaction is not implemented.")
            raise NotImplementedError("MockAttenuator: Please implement actual attenuator connection.")

    def set_attenuation(self, attenuation_db: float) -> None:
        """
        Simulate setting the attenuation level.

        Args:
            attenuation_db (float): The attenuation level in dB.
        """
        if not self.connected:
            self.logger.error("Attenuator not connected.")
            raise ConnectionError("Attenuator not connected.")
        if self.simulated_mode:
            self.logger.info(f"Simulated: Setting attenuation to {attenuation_db} dB.")
            time.sleep(0.1)
        else:
            self.logger.error("MockAttenuator: This is a mock plug. Actual hardware interaction is not implemented.")
            raise NotImplementedError("MockAttenuator: Please implement actual attenuation setting.")
