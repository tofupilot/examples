import time
from pathlib import Path

from openhtf.plugs import BasePlug
from pandas import read_csv, DataFrame


class MockDutPlug(BasePlug):
    """
    A mock plug for simulating communication with a DUT.

    Provides methods to connect, disconnect, and save calibration data for the DUT.
    """

    def connect(self) -> None:
        self.logger.info("Simulated: Connecting to DUT.")
        time.sleep(1)

    def disconnect(self) -> None:
        self.logger.info("Simulated: Disconnecting from DUT.")
        time.sleep(1)

    @staticmethod
    def send_csv_data(csv_path: Path) -> DataFrame:
        return read_csv(csv_path, delimiter="\t")

    def save_accelerometer_calibration(self, polynomial_coefficients: dict) -> None:
        self.logger.info("Simulated: Saving IMU thermal calibration to DUT.")
        time.sleep(0.5)

    def save_gyroscope_calibration(self, polynomial_coefficients: dict) -> None:
        self.logger.info("Simulated: Saving IMU thermal calibration to DUT.")
        time.sleep(0.5)

    def tearDown(self) -> None:
        """
        OpenHTF automatically calls the tearDown method after the test phase ends.
        This ensures that any required cleanup (like disconnecting from the DUT) is performed.
        """
        self.logger.info("Simulated: Performing teardown.")
        self.disconnect()
