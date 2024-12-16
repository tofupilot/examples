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
def get_calibration_data(test: Test, drone: MockDutPlug) -> None:
    """Retrieve calibration data from the DUT."""
    calibration_data = drone.send_csv_data(CONF.dataset_file)

    test.state["lin_acc_temp"] = {
        "temperature": calibration_data["imu.temperature"],
        "acc_x": calibration_data["imu.acc.x"],
        "acc_y": calibration_data["imu.acc.y"],
        "acc_z": calibration_data["imu.acc.z"] + 9.81,
    }

    test.state["gyro_data"] = {
        "temperature": calibration_data["imu.temperature"],
        "gyro_x": calibration_data["imu.gyro.x"],
        "gyro_y": calibration_data["imu.gyro.y"],
        "gyro_z": calibration_data["imu.gyro.z"],
    }


@measures(
    htf.Measurement("acc_max_bias_x")
    .in_range(0.0, ACC_MAX_BIAS_LIMIT)
    .with_units(units.METRE_PER_SECOND_SQUARED),
    htf.Measurement("acc_max_bias_y")
    .in_range(0.0, ACC_MAX_BIAS_LIMIT)
    .with_units(units.METRE_PER_SECOND_SQUARED),
    htf.Measurement("acc_max_bias_z")
    .in_range(0.0, ACC_MAX_BIAS_LIMIT)
    .with_units(units.METRE_PER_SECOND_SQUARED),
    htf.Measurement("acc_residuals_x")
    .with_units(units.METRE_PER_SECOND_SQUARED),
    htf.Measurement("acc_residuals_y")
    .with_units(units.METRE_PER_SECOND_SQUARED),
    htf.Measurement("acc_residuals_z")
    .with_units(units.METRE_PER_SECOND_SQUARED),
    htf.Measurement("acc_r2_x"),
    htf.Measurement("acc_r2_y"),
    htf.Measurement("acc_r2_z"),
    htf.Measurement("acc_noise_density_x")
    .in_range(0.0, ACC_NOISE_DENSITY_LIMIT)
    .with_units(units.METRE_PER_SECOND_SQUARED),
    htf.Measurement("acc_noise_density_y")
    .in_range(0.0, ACC_NOISE_DENSITY_LIMIT)
    .with_units(units.METRE_PER_SECOND_SQUARED),
    htf.Measurement("acc_noise_density_z")
    .in_range(0.0, ACC_NOISE_DENSITY_LIMIT)
    .with_units(units.METRE_PER_SECOND_SQUARED),
    htf.Measurement("acc_temp_sensitivity_x"),
    htf.Measurement("acc_temp_sensitivity_y"),
    htf.Measurement("acc_temp_sensitivity_z"),
    htf.Measurement("acc_polynomial_coefficients_x").doc(
        "Coefficients of the polynomial that models the accelerometer temperature response."
    ),
    htf.Measurement("acc_polynomial_coefficients_y").doc(
        "Coefficients of the polynomial that models the accelerometer temperature response."
    ),
    htf.Measurement("acc_polynomial_coefficients_z").doc(
        "Coefficients of the polynomial that models the accelerometer temperature response."
    ),
)
def compute_accelerometer_calibration(test: Test) -> None:
    """Perform calibration and metrics computation for the accelerometer."""
    # Extract data from test.state
    lin_acc_temp = test.state["lin_acc_temp"]
    data = (
        lin_acc_temp["temperature"].to_numpy(),
        lin_acc_temp["acc_x"].to_numpy(),
        lin_acc_temp["acc_y"].to_numpy(),
        lin_acc_temp["acc_z"].to_numpy(),
    )

    # Perform calibration
    calibration_results = calibrate_sensor(data)

    # Compute metrics for each axis
    metrics = {}
    for axis, axis_name in enumerate(["x", "y", "z"]):
        axis_data = data[axis + 1]  # Skip temperature
        fitted_values = calibration_results["fitted_values"][f"axis_{axis}"]

        residuals = compute_residuals(axis_data, fitted_values)
        r2 = compute_r2(axis_data, fitted_values)
        noise_density = compute_noise_density(axis_data)
        temp_sensitivity = compute_temp_sensitivity(axis_data, data[0])

        metrics[axis_name] = {
            "residuals": residuals,
            "r2": r2,
            "noise_density": noise_density,
            "temp_sensitivity": temp_sensitivity,
            "max_bias": abs(residuals["mean_residual"]),  # Max bias directly from residuals
        }

    # Update measurements
    for axis_name, axis_metrics in metrics.items():
        test.measurements[f"acc_max_bias_{axis_name}"] = axis_metrics["max_bias"]
        test.measurements[f"acc_residuals_{axis_name}"] = axis_metrics["residuals"]
        test.measurements[f"acc_r2_{axis_name}"] = axis_metrics["r2"]
        test.measurements[f"acc_noise_density_{axis_name}"] = axis_metrics[
            "noise_density"
        ]
        test.measurements[f"acc_temp_sensitivity_{axis_name}"] = axis_metrics[
            "temp_sensitivity"
        ]
        test.measurements[f"acc_polynomial_coefficients_{axis_name}"] = calibration_results[
            "polynomial_coefficients"
        ][f"axis_{list(metrics.keys()).index(axis_name)}"]

    # Attach calibration figures
    for axis, fig in zip(["x", "y", "z"], calibration_results["figures"]):
        test.attach(f"acc_calibration_figure_{axis}", fig.getvalue(), "image/png")





@measures(
    htf.Measurement("gyro_max_bias_x")
    .in_range(0.0, GYRO_MAX_BIAS_LIMIT)
    .with_units(units.DEGREE_PER_SECOND),
    htf.Measurement("gyro_max_bias_y")
    .in_range(0.0, GYRO_MAX_BIAS_LIMIT)
    .with_units(units.DEGREE_PER_SECOND),
    htf.Measurement("gyro_max_bias_z")
    .in_range(0.0, GYRO_MAX_BIAS_LIMIT)
    .with_units(units.DEGREE_PER_SECOND),
    htf.Measurement("gyro_residuals_x")
    .with_units(units.DEGREE_PER_SECOND),
    htf.Measurement("gyro_residuals_y")
    .with_units(units.DEGREE_PER_SECOND),
    htf.Measurement("gyro_residuals_z")
    .with_units(units.DEGREE_PER_SECOND),
    htf.Measurement("gyro_r2_x"),
    htf.Measurement("gyro_r2_y"),
    htf.Measurement("gyro_r2_z"),
    htf.Measurement("gyro_noise_density_x")
    .in_range(0.0, GYRO_NOISE_DENSITY_LIMIT)
    .with_units(units.DEGREE_PER_SECOND),
    htf.Measurement("gyro_noise_density_y")
    .in_range(0.0, GYRO_NOISE_DENSITY_LIMIT)
    .with_units(units.DEGREE_PER_SECOND),
    htf.Measurement("gyro_noise_density_z")
    .in_range(0.0, GYRO_NOISE_DENSITY_LIMIT)
    .with_units(units.DEGREE_PER_SECOND),
    htf.Measurement("gyro_temp_sensitivity_x"),
    htf.Measurement("gyro_temp_sensitivity_y"),
    htf.Measurement("gyro_temp_sensitivity_z"),
    htf.Measurement("gyro_polynomial_coefficients_x").doc(
        "Coefficients of the polynomial that models the gyroscope temperature response."
    ),
    htf.Measurement("gyro_polynomial_coefficients_y").doc(
        "Coefficients of the polynomial that models the gyroscope temperature response."
    ),
    htf.Measurement("gyro_polynomial_coefficients_z").doc(
        "Coefficients of the polynomial that models the gyroscope temperature response."
    ),
)
def compute_gyroscope_calibration(test: Test) -> None:
    """Perform calibration and metrics computation for the gyroscope."""
    # Extract data from test.state
    gyro_data = test.state["gyro_data"]
    data = (
        gyro_data["temperature"].to_numpy(),
        gyro_data["gyro_x"].to_numpy(),
        gyro_data["gyro_y"].to_numpy(),
        gyro_data["gyro_z"].to_numpy(),
    )

    # Perform calibration
    calibration_results = calibrate_sensor(data)

    # Compute metrics for each axis
    metrics = {}
    for axis, axis_name in enumerate(["x", "y", "z"]):
        axis_data = data[axis + 1]  # Skip temperature
        fitted_values = calibration_results["fitted_values"][f"axis_{axis}"]

        residuals = compute_residuals(axis_data, fitted_values)
        r2 = compute_r2(axis_data, fitted_values)
        noise_density = compute_noise_density(axis_data)
        temp_sensitivity = compute_temp_sensitivity(axis_data, data[0])

        metrics[axis_name] = {
            "residuals": residuals,
            "r2": r2,
            "noise_density": noise_density,
            "temp_sensitivity": temp_sensitivity,
            "max_bias": abs(residuals["mean_residual"]),  # Max bias directly from residuals
        }

    # Update measurements
    for axis_name, axis_metrics in metrics.items():
        test.measurements[f"gyro_max_bias_{axis_name}"] = axis_metrics["max_bias"]
        test.measurements[f"gyro_residuals_{axis_name}"] = axis_metrics["residuals"]
        test.measurements[f"gyro_r2_{axis_name}"] = axis_metrics["r2"]
        test.measurements[f"gyro_noise_density_{axis_name}"] = axis_metrics[
            "noise_density"
        ]
        test.measurements[f"gyro_temp_sensitivity_{axis_name}"] = axis_metrics[
            "temp_sensitivity"
        ]
        test.measurements[f"gyro_polynomial_coefficients_{axis_name}"] = calibration_results[
            "polynomial_coefficients"
        ][f"axis_{list(metrics.keys()).index(axis_name)}"]

    # Attach calibration figures
    for axis, fig in zip(["x", "y", "z"], calibration_results["figures"]):
        test.attach(f"gyro_calibration_figure_{axis}", fig.getvalue(), "image/png")



# @plug(drone=MockDutPlug)
# def save_calibration(test: Test, drone: MockDutPlug) -> None:
#     """Save calibration data to the DUT."""
#     for axis in ['x', 'y', 'z']:
#         drone.save_accelerometer_calibration(getattr(test.measurements, f"acc_polynomial_coefficients_{axis}"))
#         drone.save_gyroscope_calibration(getattr(test.measurements, f"gyro_polynomial_coefficients_{axis}"))



def main():
    test = htf.Test(
        connect_dut,
        get_calibration_data,
        compute_accelerometer_calibration,
        compute_gyroscope_calibration,
        # save_calibration,
        procedure_id="IMUTC-1",
        procedure_name="IMU Thermal Calibration",
        part_name="PCB01",
    )

    with TofuPilot(test):
        test.execute(lambda: "00001")  # mock operator S/N input


if __name__ == "__main__":
    main()
