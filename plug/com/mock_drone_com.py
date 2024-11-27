import time
from openhtf.plugs import BasePlug


class MockDroneCom(BasePlug):
    """
    A mock plug for simulating communication with a drone.

    Provides methods to get and set the drone ID, and to get pressure, temperature, and distance readings.
    This class always operates in simulated mode.
    """
    def get_drone_id(self) -> str:
        self.logger.info("Simulated: Drone ID received: default-id-123")
        return "default-id-123"

    def set_drone_id(self, new_id: str = "ID-234") -> str:
        self.logger.info(f"Simulated: Setting Drone ID to: {new_id}")
        time.sleep(1)
        return new_id

    def get_pressure(self, golden_sample: bool = False) -> float:
        if golden_sample:
            self.logger.info("Simulated: Golden Sample Pressure reading: 1013.0 hPa")
            return 1013.0
        else:
            self.logger.info("Simulated: Pressure reading: 1013.5 hPa")
            return 1013.5

    def get_temperature(self, golden_sample: bool = False) -> float:
        if golden_sample:
            self.logger.info("Simulated: Golden Sample Temperature reading: 25.0 °C")
            return 25.0
        else:
            self.logger.info("Simulated: Temperature reading: 25.5 °C")
            return 25.5

    def get_distance(self) -> float:
        self.logger.info("Simulated: Distance measurement: 1002.0 mm")
        return 1002.0
