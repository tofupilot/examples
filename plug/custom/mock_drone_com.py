import time
from openhtf.plugs import BasePlug


class MockDroneCom(BasePlug):
    """
    A mock plug for simulating communication with a drone.

    Provides methods to get and set the drone ID, and to get pressure readings.
    This class always operates in simulated mode.
    """
    def get_drone_id(self) -> str:
        self.logger.info("Simulated: Drone ID received: default-id-123")
        return "default-id-123"

    def set_drone_id(self, new_id: str = "ID-234") -> str:
        self.logger.info(f"Simulated: Setting Drone ID to: {new_id}")
        time.sleep(1)
        return new_id

    def get_pressure(self) -> float:
        self.logger.info("Simulated: Pressure reading: 1013.8 hPa")
        return 1013.8
