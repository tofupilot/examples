import openhtf as htf
from openhtf import Test, measures
from openhtf.plugs import plug
from openhtf.util import units
from tofupilot.openhtf import TofuPilot

from plugs.mock_dut import MockDutPlug
from utils.calibrate_sensor import calibrate_sensor
from utils.compute_noise_density import compute_noise_density
from utils.compute_r2 import compute_r2
from utils.compute_residuals import compute_residuals
from utils.compute_temp_sensitivity import compute_temp_sensitivity

@plug(dut=MockDutPlug)
def connect_dut(test: Test, dut: MockDutPlug) -> None:
    """Connect to the Device Under Test (DUT)."""
    dut.connect()

@measures(
    # Noise Density (uses raw data only)
    *(htf.Measurement("{sensor}_noise_density_{axis}")
      .in_range(0.0, {"acc": 1.0, "gyro": 0.04}.get(sensor))
      .with_units({"acc": units.METRE_PER_SECOND_SQUARED, "gyro": units.DEGREE_PER_SECOND}.get(sensor))
      .with_args(sensor=sensor, axis=axis)
      for sensor in ("acc", "gyro") for axis in ("x", "y", "z")),

    # Temperature Sensitivity - Max (uses raw data only)
    *(htf.Measurement("{sensor}_temp_sensitivity_max_{axis}")
      .with_units({"acc": units.METRE_PER_SECOND_SQUARED, "gyro": units.DEGREE_PER_SECOND}.get(sensor))
      .with_args(sensor=sensor, axis=axis)
      for sensor in ("acc", "gyro") for axis in ("x", "y", "z")),

    # Temperature Sensitivity - Reference (uses raw data only)
    *(htf.Measurement("{sensor}_temp_sensitivity_ref_{axis}")
      .in_range(0.0, {"acc": {"x": 0.5, "y": 0.5, "z": 1.0}, "gyro": {"x": 0.05, "y": 0.05, "z": 0.05}}[sensor][axis])
      .with_units({"acc": units.METRE_PER_SECOND_SQUARED, "gyro": units.DEGREE_PER_SECOND}.get(sensor))
      .with_args(sensor=sensor, axis=axis)
      for sensor in ("acc", "gyro") for axis in ("x", "y", "z")),
)
@plug(dut=MockDutPlug)
def get_calibration_data(test: Test, dut: MockDutPlug) -> None:
    """Retrieve calibration data from the DUT."""
    test.state.update(dut.get_imu_data(test))

    for sensor, data_key, calibration_key in [
        ("acc", "acc_data", "acc_calibration_results"),
        ("gyro", "gyro_data", "gyro_calibration_results"),
    ]:
        # Data preparation: extract data from test.state
        sensor_temp_data = test.state[data_key]
        data = (
            sensor_temp_data["temperature"],
            sensor_temp_data[f"{sensor}_x"],
            sensor_temp_data[f"{sensor}_y"],
            sensor_temp_data[f"{sensor}_z"],
        )

        # Validate raw data for each axis
        metrics = {}
        for axis, axis_name in enumerate(["x", "y", "z"]):
            axis_data = data[axis + 1]  # Skip temperature
            noise_density = compute_noise_density(axis_data)
            temp_sensitivity = compute_temp_sensitivity(axis_data, data[0])

            metrics[axis_name] = {"noise_density": noise_density, "temp_sensitivity": temp_sensitivity}

        for axis_name, axis_metrics in metrics.items():
            # Fill measurements on raw data
            test.measurements[f"{sensor}_noise_density_{axis_name}"] = axis_metrics["noise_density"]
            test.measurements[f"{sensor}_temp_sensitivity_max_{axis_name}"] = axis_metrics["temp_sensitivity"][
                "max_sensitivity"]
            test.measurements[f"{sensor}_temp_sensitivity_ref_{axis_name}"] = axis_metrics["temp_sensitivity"][
                "sensitivity_at_ref"]


@measures(
    # Polynomial Coefficients
    *(htf.Measurement("{sensor}_polynomial_coefficients_{axis}")
      .with_args(sensor=sensor, axis=axis)
      for sensor in ("acc", "gyro") for axis in ("x", "y", "z")),

    # Residual mean
    *(htf.Measurement("{sensor}_residual_mean_{axis}")
      .in_range(0.0, {"acc": 0.01, "gyro": 0.01}.get(sensor))
      .with_units({"acc": units.METRE_PER_SECOND_SQUARED, "gyro": units.DEGREE_PER_SECOND}.get(sensor))
      .with_args(sensor=sensor, axis=axis)
      for sensor in ("acc", "gyro") for axis in ("x", "y", "z")),

    # Residual standard deviation
    *(htf.Measurement("{sensor}_residual_std_{axis}")
      .in_range(0.0, {"acc": 5.0, "gyro": 0.3}.get(sensor))
      .with_units({"acc": units.METRE_PER_SECOND_SQUARED, "gyro": units.DEGREE_PER_SECOND}.get(sensor))
      .with_args(sensor=sensor, axis=axis)
      for sensor in ("acc", "gyro") for axis in ("x", "y", "z")),

    # Residual peak-to-peak
    *(htf.Measurement("{sensor}_residual_p2p_{axis}")
      .in_range(0.0, {"acc": {"x": 15.0, "y": 15.0, "z": 35.0}, "gyro": {"x": 2.0, "y": 2.0, "z": 2.0}}[sensor][axis])
      .with_units({"acc": units.METRE_PER_SECOND_SQUARED, "gyro": units.DEGREE_PER_SECOND}.get(sensor))
      .with_args(sensor=sensor, axis=axis)
      for sensor in ("acc", "gyro") for axis in ("x", "y", "z")),

    # R²
    *(htf.Measurement("{sensor}_r2_{axis}")
      .with_args(sensor=sensor, axis=axis)
      for sensor in ("acc", "gyro") for axis in ("x", "y", "z")),
)
def compute_sensors_calibration(test: Test) -> None:
    """Perform calibration and metrics computation for both accelerometer and gyroscope."""
    # Iterate over both sensors (accelerometer and gyroscope)
    for sensor, data_key, calibration_key in [
        ("acc", "acc_data", "acc_calibration_results"),
        ("gyro", "gyro_data", "gyro_calibration_results"),
    ]:
        # Data preparation: extract data from test.state
        sensor_temp_data = test.state[data_key]
        data = (
            sensor_temp_data["temperature"],
            sensor_temp_data[f"{sensor}_x"],
            sensor_temp_data[f"{sensor}_y"],
            sensor_temp_data[f"{sensor}_z"],
        )
        # Fit polynomial to raw data and calculate fitted temperature response
        test.state[calibration_key] = calibrate_sensor(data, sensor)

        metrics = {}
        # Compute fit metrics for each axis
        for axis, axis_name in enumerate(["x", "y", "z"]):
            axis_data = data[axis + 1]  # Skip temperature

            # Validate fit
            fitted_values = test.state[calibration_key]["fitted_values"][f"{axis_name}_axis"]
            residuals = compute_residuals(axis_data, fitted_values)
            r2 = compute_r2(axis_data, fitted_values)

            metrics[axis_name] = {"residuals": residuals, "r2": r2}

        # Update all measurements for the current sensor
        for axis_name, axis_metrics in metrics.items():
            # Polynomial coefficients
            test.measurements[
                f"{sensor}_polynomial_coefficients_{axis_name}"
            ] = test.state[calibration_key]["polynomial_coefficients"][
                f"{axis_name}_axis"
            ].tolist()

            # Measurements using raw data and fitted data
            test.measurements[f"{sensor}_residual_mean_{axis_name}"] = abs(axis_metrics["residuals"]["mean_residual"])
            test.measurements[f"{sensor}_residual_std_{axis_name}"] = axis_metrics["residuals"]["std_residual"]
            test.measurements[f"{sensor}_residual_p2p_{axis_name}"] = axis_metrics["residuals"]["p2p_residual"]
            test.measurements[f"{sensor}_r2_{axis_name}"] = axis_metrics["r2"]

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
        procedure_name="IMU Thermal Calibration",
        part_name="PCB01",
    )

    with TofuPilot(test):
        test.execute(lambda: "00001")  # mock operator S/N input


if __name__ == "__main__":
    main()
