import openhtf as htf
import os
from openhtf import measures, PhaseResult
from openhtf.plugs import plug, user_input
from openhtf.util.configuration import CONF
from tofupilot.openhtf import TofuPilot

# Import necessary plugs
from plugs.mock_drone_com import MockDroneCom
from plugs.mock_environmental_chamber import MockEnvironmentalChamber
from plugs.regression_fitter import IMUThermalCalibration

# Calibration configuration
CONF.declare('calibration_csv_file', default_value='data/sample_imu_thermal.csv', description='Path to IMU data CSV file.')

## Phase 1: Perform Calibration
@plug(drone=MockDroneCom, chamber=MockEnvironmentalChamber)
def perform_calibration(test, drone, chamber) -> PhaseResult:
    # Control environmental chamber and command drone to log IMU data

    # Create data save directory
    data_save_path = CONF.data_save_path
    os.makedirs(data_save_path, exist_ok=True)

    # Generate temperature points
    temperatures = list(range(-10, 41, 10))

    # Set drone to data logging mode
    drone.set_imu_mode('data_logging')

    for temp in temperatures:
        # Set environmental chamber temperature
        chamber.set_temperature(temp)
        chamber.wait_for_stabilization()

        # Command drone to log IMU data at this temperature
        drone.log_imu_data(duration=60)

    # Reset drone IMU to flight mode
    drone.set_imu_mode('flight')

    return PhaseResult.CONTINUE

## Phase 2: Read CSV Data
def read_csv_data(test) -> PhaseResult:
    # Read the CSV data from the SD card (path from CONF)
    csv_file_path = CONF.calibration_csv_file
    try:
        import pandas as pd
        data = pd.read_csv(csv_file_path, delimiter='\t')
        test.state['imu_data'] = data
        return PhaseResult.CONTINUE
    
    except Exception:
        return PhaseResult.STOP


## Phase 3: Calibrate Accelerometer
@plug(calibration=IMUThermalCalibration)
@measures(
    htf.Measurement('accelerometer_max_bias')
    .in_range(0.0, 0.5)
    .with_units('m/s²')
    .with_precision(5)
)
def calibrate_accelerometer(test, calibration) -> PhaseResult:
    # Get data from test state
    data = test.state.get('imu_data')
    if data is None:
        return PhaseResult.STOP

    # Calibrate accelerometer
    try:
        acc_results = calibration.calibrate_accelerometer(data)
    except ValueError:
        return PhaseResult.STOP

    # Attach figures
    for fig_file in acc_results['figures']:
        test.attach_from_file(fig_file)

    # Record measurements
    max_bias = acc_results['max_bias']
    test.measurements.accelerometer_max_bias = max_bias

    # Save calibration results to test state
    test.state['acc_calibration_results'] = acc_results

    return PhaseResult.CONTINUE

## Phase 4: Calibrate Gyroscope
@plug(calibration=IMUThermalCalibration)
@measures(
    htf.Measurement('gyroscope_max_bias')
    .in_range(0.0, 0.5)
    .with_units(htf.units.DEGREE_PER_SECOND)
    .with_precision(5)
)
def calibrate_gyroscope(test, calibration) -> PhaseResult:
    # Get data from test state
    data = test.state.get('imu_data')
    if data is None:
        return PhaseResult.STOP

    # Calibrate gyroscope
    try:
        gyro_results = calibration.calibrate_gyroscope(data)
    except ValueError:
        return PhaseResult.STOP

    # Attach figures
    for fig_file in gyro_results['figures']:
        test.attach_from_file(fig_file)

    # Record measurements
    max_bias = gyro_results['max_bias']
    test.measurements.gyroscope_max_bias = max_bias

    # Save calibration results to test state
    test.state['gyro_calibration_results'] = gyro_results

    return PhaseResult.CONTINUE

## Phase 5: Send Gains to Drone
@plug(drone=MockDroneCom)
def send_gains_to_drone(test, drone) -> PhaseResult:
    # Get calibration results from test state
    acc_calibration_results = test.state.get('acc_calibration_results')
    gyro_calibration_results = test.state.get('gyro_calibration_results')

    if acc_calibration_results is None or gyro_calibration_results is None:
        return PhaseResult.STOP

    # Send gains to drone
    drone.send_calibration_results({
        'accelerometer': acc_calibration_results['correction_gains'],
        'gyroscope': gyro_calibration_results['correction_gains']
    })

    return PhaseResult.CONTINUE

# Main test procedure with TofuPilot integration
def main():
    test = htf.Test(
        # perform_calibration,
        read_csv_data,
        calibrate_accelerometer,
        calibrate_gyroscope,
        send_gains_to_drone,
        procedure_name="IMU Thermal Calibration Test",
        procedure_id="IMUTC-1"
    )

    #with TofuPilot(test):
    test.execute(test_start=user_input.prompt_for_test_start())

if __name__ == "__main__":
    main()