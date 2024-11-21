import time

import openhtf as htf


class MockPsuControl(htf.plugs.BasePlug):
    def turn_on(self, simulated=True):
        if simulated:
            self.logger.info("Running in simulated mode. Turning ON PSU.")
            time.sleep(1)
            return True

    def turn_off(self, simulated=True):
        if simulated:
            time.sleep(1)
            self.logger.info("Running in simulated mode. Turning OFF PSU.")
            return True
