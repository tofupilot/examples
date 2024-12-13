import openhtf as htf
from openhtf import Test, measures
from openhtf.plugs import plug
from openhtf.util.configuration import CONF
from openhtf.util import units
from tofupilot.openhtf import TofuPilot

from plugs.mock_dut import MockDutPlug
from utils.calibrate_sensor import calibrate_sensor
from utils.compute_residuals import compute_residuals
from utils.compute_r2 import compute_r2
from utils.compute_noise_density import compute_noise_density
from utils.compute_temp_sensitivity import compute_temp_sensitivity

CONF.declare(
    "dataset_file",
    default_value="data/imu_raw_data.csv",
    description="Path to IMU raw acquisitions .csv file.",
)

# In-range limits based on MATLAB script
ACC_MAX_BIAS_LIMIT = 0.5  # m/s^2
ACC_RESIDUAL_MEAN_LIMIT = 0.01  # m/s^2
ACC_RESIDUAL_STD_LIMIT = 5.0  # m/s^2
ACC_RESIDUAL_P2P_LIMIT_XY = 15.0  # m/s^2
ACC_RESIDUAL_P2P_LIMIT_Z = 35.0  # m/s^2
ACC_NOISE_DENSITY_LIMIT = 1.0  # m/s^2/sqrt(Hz)
ACC_TEMP_SENSITIVITY_LIMIT_XY = 0.5  # m/s^2/°C
ACC_TEMP_SENSITIVITY_LIMIT_Z = 1.0  # m/s^2/°C

GYRO_MAX_BIAS_LIMIT = 0.5  # °/s
GYRO_RESIDUAL_MEAN_LIMIT = 0.01  # °/s
GYRO_RESIDUAL_STD_LIMIT = 0.3  # °/s
GYRO_RESIDUAL_P2P_LIMIT = 2.0  # °/s
GYRO_NOISE_DENSITY_LIMIT = 0.04  # °/s/sqrt(Hz)
GYRO_TEMP_SENSITIVITY_LIMIT = 0.05  # °/s/°C

@plug(drone=MockDutPlug)
def connect_dut(test: Test, drone: MockDutPlug) -> None:
    """Connect to the Device Under Test (DUT)."""
    drone.connect()

@plug(drone=MockDutPlug)
@measures(
    htf.Measurement("lin_acc_temp")
    .doc("Linear acceleration over temperature")
    .with_dimensions(units.DEGREE_CELSIUS,
                     units.METRE_PER_SECOND_SQUARED,
                     units.METRE_PER_SECOND_SQUARED,
                     units.METRE_PER_SECOND_SQUARED),
    htf.Measurement("ang_acc_temp")
    .doc("Angular acceleration over temperature")
    .with_dimensions(units.DEGREE_CELSIUS,
                     units.DEGREE_PER_SECOND,
                     units.DEGREE_PER_SECOND,
                     units.DEGREE_PER_SECOND)
)
def get_calibration_data(test: Test, drone: MockDutPlug) -> None:
    """Retrieve calibration data from the DUT."""
    calibration_data = drone.send_csv_data(CONF.dataset_file)

    test.measurements.lin_acc_temp = (
        calibration_data["imu.temperature"],
        calibration_data["imu.acc.x"],
        calibration_data["imu.acc.y"],
        calibration_data["imu.acc.z"] + 9.81
    )

    test.measurements.ang_acc_temp = (
        calibration_data["imu.temperature"],
        calibration_data["imu.gyro.x"],
        calibration_data["imu.gyro.y"],
        calibration_data["imu.gyro.z"]
    )

@measures(
    htf.Measurement("acc_max_bias")
    .in_range(0.0, ACC_MAX_BIAS_LIMIT).with_units(units.METRE_PER_SECOND_SQUARED),
    htf.Measurement("acc_residuals"),
    htf.Measurement("acc_r2"),
    htf.Measurement("acc_noise_density")
    .in_range(0.0, ACC_NOISE_DENSITY_LIMIT).with_units(units.METRE_PER_SECOND_SQUARED),
    htf.Measurement("acc_temp_sensitivity"),
    htf.Measurement("acc_polynomial_coefficients")
    .doc("Coefficients of the polynomial that models the accelerometer temperature response.")
)
def compute_accelerometer_calibration(test: Test) -> None:
    """Perform calibration and metrics computation for the accelerometer."""
    temp, acc_x, acc_y, acc_z = test.measurements.lin_acc_temp
    data = (temp, acc_x, acc_y, acc_z)

    # Perform calibration
    calibration_results = calibrate_sensor(data)

    # Compute metrics
    residuals = {axis: compute_residuals(data[i + 1], calibration_results["fitted_values"][f"axis_{i}"])
                 for i, axis in enumerate(["x", "y", "z"])}
    r2 = {axis: compute_r2(data[i + 1], calibration_results["fitted_values"][f"axis_{i}"])
          for i, axis in enumerate(["x", "y", "z"])}
    noise_density = {axis: compute_noise_density(data[i + 1])
                     for i, axis in enumerate(["x", "y", "z"])}
    temp_sensitivity = {axis: compute_temp_sensitivity(data[i + 1], temp)
                        for i, axis in enumerate(["x", "y", "z"])}

    # Update measurements
    test.measurements.acc_max_bias = max(
        abs(residuals[axis]["mean_residual"]) for axis in residuals
    )
    test.measurements.acc_residuals = residuals
    test.measurements.acc_r2 = r2
    test.measurements.acc_noise_density = noise_density
    test.measurements.acc_temp_sensitivity = temp_sensitivity
    test.measurements.acc_polynomial_coefficients = calibration_results["polynomial_coefficients"]

@measures(
    htf.Measurement("gyro_max_bias").in_range(0.0, GYRO_MAX_BIAS_LIMIT).with_units(units.DEGREE_PER_SECOND),
    htf.Measurement("gyro_residuals"),
    htf.Measurement("gyro_r2"),
    htf.Measurement("gyro_noise_density").in_range(0.0, GYRO_NOISE_DENSITY_LIMIT).with_units(units.DEGREE_PER_SECOND),
    htf.Measurement("gyro_temp_sensitivity"),
    htf.Measurement("gyro_polynomial_coefficients")
    .doc("Coefficients of the polynomial that models the gyroscope temperature response.")
)
def compute_gyroscope_calibration(test: Test) -> None:
    """Perform calibration and metrics computation for the gyroscope."""
    temp, gyro_x, gyro_y, gyro_z = test.measurements.ang_acc_temp
    data = (temp, gyro_x, gyro_y, gyro_z)

    # Perform calibration
    calibration_results = calibrate_sensor(data)

    # Compute metrics
    residuals = {axis: compute_residuals(data[i + 1], calibration_results["fitted_values"][f"axis_{i}"]) for i, axis in
                 enumerate(["x", "y", "z"])}
    r2 = {axis: compute_r2(data[i + 1], calibration_results["fitted_values"][f"axis_{i}"]) for i, axis in
          enumerate(["x", "y", "z"])}
    noise_density = {axis: compute_noise_density(data[i + 1]) for i, axis in enumerate(["x", "y", "z"])}
    temp_sensitivity = {axis: compute_temp_sensitivity(data[i + 1], temp) for i, axis in enumerate(["x", "y", "z"])}

    # Update measurements
    test.measurements.gyro_max_bias = max(
        abs(residuals[axis]["mean_residual"]) for axis in residuals
    )
    test.measurements.gyro_residuals = residuals
    test.measurements.gyro_r2 = r2
    test.measurements.gyro_noise_density = noise_density
    test.measurements.gyro_temp_sensitivity = temp_sensitivity
    test.measurements.gyro_polynomial_coefficients = calibration_results["polynomial_coefficients"]

@plug(drone=MockDutPlug)
def save_calibration_to(test: Test, drone: MockDutPlug) -> None:
    """Save calibration data to the DUT."""
    drone.save_accelerometer_calibration(test.measurements.acc_polynomial_coefficients)
    drone.save_gyroscope_calibration(test.measurements.gyro_polynomial_coefficients)

def main():
    test = htf.Test(
        connect_dut,
        get_calibration_data,
        compute_accelerometer_calibration,
        compute_gyroscope_calibration,
        save_calibration_to,
        procedure_id="IMUTC-1",
        procedure_name="IMU Thermal Calibration",
        part_name="PCB01",
    )

    with TofuPilot(test):
        test.execute(lambda: "00001")  # mock operator S/N input


if __name__ == "__main__":
    main()
