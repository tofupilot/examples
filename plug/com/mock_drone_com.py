# plug/com/mock_drone_com.py
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

    def switch_on(self, component: str) -> None:
        self.logger.info(f"Simulated: Switching on {component}.")
        time.sleep(0.5)

    def switch_off(self) -> None:
        self.logger.info("Simulated: Switching off drone.")
        time.sleep(0.5)

    def connect(self) -> bool:
        self.logger.info("Simulated: Connecting to drone.")
        time.sleep(1)
        return True

    def connect_modem(self) -> bool:
        self.logger.info("Simulated: Connecting to drone modem.")
        time.sleep(1)
        return True

    def configure_ground_modem(self) -> None:
        self.logger.info("Simulated: Configuring ground modem.")
        time.sleep(1)

    def set_rtk_antenna_type(self, antenna_type: str) -> None:
        self.logger.info(f"Simulated: Setting RTK antenna type to {antenna_type}.")
        time.sleep(0.5)

    def send_sensors_telemetry(self) -> None:
        self.logger.info("Simulated: Sending telemetry sensors.")
        time.sleep(0.5)

    def measure_downlink_quality(self) -> float:
        self.logger.info("Simulated: Measuring downlink quality.")
        time.sleep(1)
        return 99.0  # Simulated quality percentage

    def get_rssi(self) -> float:
        self.logger.info("Simulated: Getting RSSI values.")
        time.sleep(0.5)
        return 90.0

    def wait_for_gnss_configuration(self, timeout: int) -> bool:
        self.logger.info("Simulated: Waiting for GNSS configuration.")
        time.sleep(1)
        return True  # Simulate success

    def wait_for_gnss_fix(self, timeout: int) -> bool:
        self.logger.info("Simulated: Waiting for GNSS fix.")
        time.sleep(1)
        return True  # Simulate success

    def send_telemetry_gnss_bands(self) -> None:
        self.logger.info("Simulated: Sending telemetry GNSS bands.")
        time.sleep(0.5)

    def receive_gnss_status(self) -> dict:
        self.logger.info("Simulated: Receiving GNSS status.")
        time.sleep(1)
        # Simulated GNSS status data
        return {'sat_count': 10, 'strength_L1': 40, 'strength_L2': 41}

    def check_gnss_status(self, gnss_status: dict) -> bool:
        self.logger.info("Simulated: Checking GNSS status.")
        # Implement logic to check GNSS status against limits
        # For simulation, return True
        return True

    def update_gnss_license(self, license_file: str) -> bool:
        self.logger.info(f"Simulated: Updating GNSS license using file {license_file}.")
        time.sleep(1)
        return True  # Simulate success

    def is_remote_id_applicable(self) -> bool:
        self.logger.info("Simulated: Checking if WiFi Remote ID is applicable.")
        return True  # Simulate that it is applicable

    def enable_wifi_remote_id(self) -> None:
        self.logger.info("Simulated: Enabling WiFi Remote ID.")
        time.sleep(0.5)

    def check_wifi_remote_id(self) -> bool:
        self.logger.info("Simulated: Checking WiFi Remote ID.")
        time.sleep(1)
        return True  # Simulate success

    def disable_wifi_remote_id(self) -> None:
        self.logger.info("Simulated: Disabling WiFi Remote ID.")
        time.sleep(0.5)

    def reset_logs_counter(self) -> None:
        self.logger.info("Simulated: Resetting logs counter.")
        time.sleep(0.5)

    def set_imu_mode(self, mode: str) -> None:
        self.logger.info(f"Simulated: Setting IMU mode to {mode}.")
        time.sleep(0.5)

    def log_imu_data(self, duration: int) -> None:
        self.logger.info(f"Simulated: Collecting static IMU data")
        time.sleep(1)

    def fit_static_calibration_data(self, data_path: str) -> dict:
        self.logger.info("Simulated: Fitting static calibration data.")
        time.sleep(1)
        return {'bias': 0.3}  # Simulated bias value

    def send_calibration_results(self, calibration_results: dict) -> None:
        self.logger.info("Simulated: Sending static calibration to drone.")
        time.sleep(0.5)

    def collect_dynamic_imu_data(self, duration: int, temperature: float, axis: str, save_path: str) -> None:
        self.logger.info(f"Simulated: Collecting dynamic IMU data on axis {axis} at {temperature}°C for {duration} seconds.")
        time.sleep(1)

    def fit_dynamic_calibration_data(self, data_path: str) -> dict:
        self.logger.info("Simulated: Fitting dynamic calibration data.")
        time.sleep(1)
        return {'scale_factor_error': 800.0}  # Simulated scale factor error

    def send_dynamic_calibration(self, calibration_results: dict) -> None:
        self.logger.info("Simulated: Sending dynamic calibration to drone.")
        time.sleep(0.5)
