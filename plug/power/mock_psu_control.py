import time

import openhtf as htf


class MockPsuControl(htf.plugs.BasePlug):
    """
    A mock plug for simulating controlling a power relay or a simple power supply.

    Provides methods to turn on and off the power supply.
    This class always operates in simulated mode.
    """
    def turn_on(self, simulated=True) -> bool:
        if simulated:
            self.logger.info("Running in simulated mode. Turning ON PSU.")
            time.sleep(1)
            return True

    def turn_off(self, simulated=True) -> bool:
        if simulated:
            time.sleep(1)
            self.logger.info("Running in simulated mode. Turning OFF PSU.")
            return True
