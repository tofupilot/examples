import time
from openhtf.plugs import BasePlug

class MockRateTable(BasePlug):
    def connect(self) -> None:
        self.logger.info("Simulated: Connecting to rate table.")
        time.sleep(0.5)

    def rotate(self, axis: str, rate: float) -> None:
        self.logger.info(f"Simulated: Rotating around {axis}-axis at {rate} degrees/sec.")
        time.sleep(1)

    def stop_rotation(self) -> None:
        self.logger.info("Simulated: Stopping rotation.")
        time.sleep(0.5)

    def disconnect(self) -> None:
        self.logger.info("Simulated: Disconnecting from rate table.")
        time.sleep(0.5)

