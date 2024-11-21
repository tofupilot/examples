import time

import openhtf as htf


class MockDroneCom(htf.plugs.BasePlug):
    def get_drone_id(self, simulated=True):
        if simulated:
            self.logger.info("Running in simulated mode. Drone ID received: ID-123")
            return "default-id-123"

    def set_drone_id(self, simulated=True):
        if simulated:
            self.logger.info("Running in simulated mode. Setting Drone ID: ID-234")
            time.sleep(1)
            return "ID-234"

    def get_pressure(self, simulated=True):
        if simulated:
            self.logger.info("Running in simulated mode. Pressure reading: 1013.8 hpa")
            return 1013.8
