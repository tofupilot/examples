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

ACCELERATION_OF_FREEFALL = -9.80600  # m/s^2, standard gravity in Switzerland zone 2


@plug(dut=MockDutPlug)
def connect_dut(test: Test, dut: MockDutPlug) -> None:
    """Connect to the Device Under Test (DUT)."""
    dut.connect()


@plug(dut=MockDutPlug)
def get_calibration_data(test: Test, dut: MockDutPlug) -> None:
    """Retrieve calibration data from the DUT."""
    
    calibration_data = dut.send_raw_data()

    # Attach the raw data directly to the test
    test.attach("raw_calibration_data", calibration_data.to_csv(), "text/csv")

    test.state["lin_acc_temp"] = {
        "temperature": calibration_data["imu.temperature"],
        "acc_x": calibration_data["imu.acc.x"],
        "acc_y": calibration_data["imu.acc.y"],
        "acc_z": calibration_data["imu.acc.z"] - ACCELERATION_OF_FREEFALL,
    }

    test.state["gyro_data"] = {
        "temperature": calibration_data["imu.temperature"],
        "gyro_x": calibration_data["imu.gyro.x"],
        "gyro_y": calibration_data["imu.gyro.y"],
        "gyro_z": calibration_data["imu.gyro.z"],
    }


@measures(
    # Max Bias
    *(htf.Measurement("{sensor}_max_bias_{axis}")
      .in_range(0.0, ACC_MAX_BIAS_LIMIT if sensor == "acc" else GYRO_MAX_BIAS_LIMIT)
      .with_units(units.METRE_PER_SECOND_SQUARED if sensor == "acc" else units.DEGREE_PER_SECOND)
      .with_args(sensor=sensor, axis=axis)
      for sensor in ("acc", "gyro") for axis in ("x", "y", "z")),

    # Residuals
    *(htf.Measurement("{sensor}_residuals_{axis}")
      .with_units(units.METRE_PER_SECOND_SQUARED if sensor == "acc" else units.DEGREE_PER_SECOND)
      .with_args(sensor=sensor, axis=axis)
      for sensor in ("acc", "gyro") for axis in ("x", "y", "z")),

    # R²
    *(htf.Measurement("{sensor}_r2_{axis}")
      .with_args(sensor=sensor, axis=axis)
      for sensor in ("acc", "gyro") for axis in ("x", "y", "z")),

    # Noise Density
    *(htf.Measurement("{sensor}_noise_density_{axis}")
      .in_range(0.0, ACC_NOISE_DENSITY_LIMIT if sensor == "acc" else GYRO_NOISE_DENSITY_LIMIT)
      .with_units(units.METRE_PER_SECOND_SQUARED if sensor == "acc" else units.DEGREE_PER_SECOND)
      .with_args(sensor=sensor, axis=axis)
      for sensor in ("acc", "gyro") for axis in ("x", "y", "z")),

    # Temperature Sensitivity
    *(htf.Measurement("{sensor}_temp_sensitivity_{axis}")
      .with_args(sensor=sensor, axis=axis)
      for sensor in ("acc", "gyro") for axis in ("x", "y", "z")),

    # Polynomial Coefficients
    *(htf.Measurement("{sensor}_polynomial_coefficients_{axis}")
      .doc("Coefficients of the polynomial that models the {sensor} temperature response.")
      .with_args(sensor=sensor, axis=axis)
      for sensor in ("acc", "gyro") for axis in ("x", "y", "z"))
)
def compute_sensors_calibration(test: Test) -> None:
    """Perform calibration and metrics computation for both accelerometer and gyroscope."""
    # Iterate over both sensors (accelerometer and gyroscope)
    for sensor, data_key, calibration_key in [
        ("acc", "lin_acc_temp", "acc_calibration_results"),
        ("gyro", "gyro_data", "gyro_calibration_results"),
    ]:
        # Extract data from test.state
        sensor_temp_data = test.state[data_key]
        data = (
            sensor_temp_data["temperature"],
            sensor_temp_data[f"{sensor}_x"],
            sensor_temp_data[f"{sensor}_y"],
            sensor_temp_data[f"{sensor}_z"],
        )

        # Perform calibration
        test.state[calibration_key] = calibrate_sensor(data)

        # Compute metrics for each axis
        metrics = {}
        for axis, axis_name in enumerate(["x", "y", "z"]):
            axis_data = data[axis + 1]  # Skip temperature
            fitted_values = test.state[calibration_key]["fitted_values"][f"axis_{axis}"]

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

        # Update measurements for the current sensor
        for axis_name, axis_metrics in metrics.items():
            test.measurements[f"{sensor}_max_bias_{axis_name}"] = axis_metrics["max_bias"]
            test.measurements[f"{sensor}_residuals_{axis_name}"] = axis_metrics["residuals"]
            test.measurements[f"{sensor}_r2_{axis_name}"] = axis_metrics["r2"]
            test.measurements[f"{sensor}_noise_density_{axis_name}"] = axis_metrics[
                "noise_density"
            ]
            test.measurements[f"{sensor}_temp_sensitivity_{axis_name}"] = axis_metrics[
                "temp_sensitivity"
            ]
            test.measurements[f"{sensor}_polynomial_coefficients_{axis_name}"] = test.state[calibration_key][
                "polynomial_coefficients"
            ][f"axis_{list(metrics.keys()).index(axis_name)}"]

        # Attach calibration figures for the current sensor
        for axis, fig in zip(["x", "y", "z"], test.state[calibration_key]["figures"]):
            test.attach(f"{sensor}_calibration_figure_{axis}", fig.getvalue(), "image/png")



@plug(dut=MockDutPlug)
def save_calibration(test: Test, dut: MockDutPlug) -> None:
    """Save calibration data to the DUT."""
    dut.save_accelerometer_calibration(test.state["acc_calibration_results"])
    dut.save_gyroscope_calibration(test.state["gyro_calibration_results"])



def main():
    test = htf.Test(
        connect_dut,
        get_calibration_data,
        compute_sensors_calibration,
        save_calibration,
        procedure_id="IMUTC-1",
        procedure_name="IMU Thermal Calibration",
        part_name="PCB01",
    )

    with TofuPilot(test):
        test.execute(lambda: "00001")  # mock operator S/N input


if __name__ == "__main__":
    main()
