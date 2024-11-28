# plug/measuring_instrument/mock_gnss_simulator.py
import time
from openhtf.plugs import BasePlug
from openhtf.util.configuration import CONF

class MockGnssSimulator(BasePlug):
    """
    A mock plug for simulating a GNSS simulator device.

    Provides methods to load scenarios and simulate GNSS signals.
    This class operates in simulated mode.
    """

    def __init__(self):
        self.simulated_mode: bool = getattr(CONF, 'simulated', True)
        self.ip_address: str = getattr(CONF, 'gnss_simulator_ip', '127.0.0.1')

    def load_scenario(self, scenario_name: str, reset: bool = True) -> str:
        """
        Simulate loading a GNSS scenario.

        Args:
            scenario_name (str): Name of the scenario file to load.
            reset (bool): Whether to reset the simulator before loading.

        Returns:
            str: 'NoError' if successful, error message otherwise.
        """
        if self.simulated_mode:
            self.logger.info(f"Simulated: Loading GNSS scenario '{scenario_name}' with reset={reset}.")
            time.sleep(1)
            self.logger.info(f"'Simulated: {scenario_name}' loaded with reset={reset}")
            return 'NoError'
        else:
            self.logger.error("MockGnssSimulator: This is a mock plug. Actual hardware interaction is not implemented.")
            raise NotImplementedError("MockGnssSimulator: Please implement actual GNSS simulator interaction.")
