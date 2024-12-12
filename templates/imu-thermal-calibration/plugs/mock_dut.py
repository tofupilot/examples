import time
from openhtf.plugs import BasePlug

class MockDutPlug(BasePlug):
    """
    A mock plug for simulating communication with a DUT.

    Provides methods to connect, disconnect, and save calibration data for the DUT.
    """

    def connect(self) -> bool:
        self.logger.info("Simulated: Connecting to DUT.")
        time.sleep(1)
        return True

    def disconnect(self) -> None:
        self.logger.info("Simulated: Disconnecting from DUT.")
        time.sleep(1)

    def save_imu_thermal_calibration(self, calibration_results: dict) -> None:
        self.logger.info("Simulated: Saving IMU thermal calibration to DUT.")
        time.sleep(0.5)

    def teardown(self) -> None:
        """
        OpenHTF automatically calls the teardown method after the test phase ends.
        This ensures that any required cleanup (like disconnecting from the DUT) is performed.
        """
        self.logger.info("Simulated: Performing teardown.")
        self.disconnect()
