import openhtf as htf
from openhtf import Test, PhaseResult, measures
from openhtf.plugs import plug
from openhtf.util.configuration import CONF
from tofupilot.openhtf import TofuPilot

from plugs.mock_dut import MockDutPlug
from utils.imu_calibration import calibrate_gyroscope, calibrate_accelerometer
from utils.read_csv_data import read_csv_data

CONF.declare(
    "dataset_file",
    default_value="data/imu_raw_data.csv",
    description="Path to IMU raw acquisitions .csv file.",
)


# TODO: tout typer
# TODO: try catch with STOP?
# TODO: add connect to unit DUT mock-up
# TODO: implement read_csv_data as a mock-up method from MockDutPlug
def get_calibration_data(test: Test):
    data = read_csv_data(CONF.dataset_file)
    test.state["imu_data"] = data # TODO: store result in test for next phase
    return PhaseResult.CONTINUE


# TODO: missings tests on calibration parameters?
# TODO: do not use local files
@measures(
    htf.Measurement("acc_max_bias")
    .in_range(0.0, 0.5) # TODO: why this parameter?
    .with_units(htf.units.METRE_PER_SECOND_SQUARED)
    .with_precision(5)
)
def compute_accelerometer_calibration(test):
    # Perform accelerometer calibration
    acc_results = calibrate_accelerometer(test.state["imu_data"])
    test.state["acc_calibration_results"] = acc_results

    test.measurements.acc_max_bias = compute_viais;
    test.measurements.acc_residuals = compute_residuals
    test.measurements.accelerometer_max_bias
    test.measurements.accelerometer_max_bias

    # Attach generated calibration figures
    for fig_file in acc_results["figures"]:
        test.attach_from_file(fig_file)

    return PhaseResult.CONTINUE


# TODO: missings tests on calibration parameters?
# TODO: do not use local files
@measures(
    htf.Measurement("gyroscope_max_bias")
    .in_range(0.0, 0.5)
    .with_units(htf.units.DEGREE_PER_SECOND)
    .with_precision(5)
)
def compute_gyroscope_calibration(test):
    # Perform gyroscope calibration
    gyro_results = calibrate_gyroscope(test.state["imu_data"])
    test.state["gyro_calibration_results"] = gyro_results

    # Validate maximum bias
    test.measurements.gyroscope_max_bias = gyro_results["max_bias"]

    # Attach generated calibration figures
    for fig_file in gyro_results["figures"]:
        test.attach_from_file(fig_file)

    return PhaseResult.CONTINUE


# TODO: gains?
@plug(drone=MockDutPlug)
def save_calibration_to(test, drone):
    acc_calibration_results = test.state.get("acc_calibration_results")
    gyro_calibration_results = test.state.get("gyro_calibration_results")

    dut.send_accelero_thermal_biais(test.measurements.acc_thermal_bias)
    dut.send_accelero_thermal_biais(test.measurements.acc_thermal_bias)

    # Send gains to DUT
    drone.save_imu_thermal_calibration(
        {
            "accelerometer": acc_calibration_results["correction_gains"],
            "gyroscope": gyro_calibration_results["correction_gains"],
        }
    )

    return PhaseResult.CONTINUE


def main():
    test = htf.Test(
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
