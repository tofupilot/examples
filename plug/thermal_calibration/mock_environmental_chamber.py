import time
from openhtf.plugs import BasePlug

class MockEnvironmentalChamber(BasePlug):
    def connect(self) -> None:
        self.logger.info("Simulated: Connecting to environmental chamber.")
        time.sleep(0.5)

    def set_temperature(self, temperature: float) -> None:
        self.logger.info(f"Simulated: Setting chamber temperature to {temperature}°C.")
        time.sleep(1)

    def wait_for_stabilization(self) -> None:
        self.logger.info("Simulated: Waiting for temperature stabilization.")
        time.sleep(1)  # Simulate stabilization time

    def disconnect(self) -> None:
        self.logger.info("Simulated: Disconnecting from environmental chamber.")
        time.sleep(0.5)
