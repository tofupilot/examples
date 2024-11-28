# rf_box.py
import time
import re
import openhtf as htf
from openhtf import measures, PhaseResult
from openhtf.plugs import plug, user_input
from openhtf.util.configuration import CONF
from tofupilot.openhtf import TofuPilot

# Import necessary plugs
from plug.usb_switch.acroname2x4 import Acroname2x4
from plug.power.mock_psu_control import MockPsuControl
from plug.com.mock_drone_com import MockDroneCom
from plug.measuring_instrument.mock_gnss_simulator import MockGnssSimulator
from plug.measuring_instrument.mock_attenuator import MockAttenuator

# Configuration variables
CONF.declare('gnss_simulator_ip', default_value='192.168.1.100', description='IP address of the GNSS simulator.')
CONF.declare('gnss_license_file', default_value='gnss_license.dat', description='Path to the GNSS license file.')
CONF.declare('gnss_simulator_scenario_name', default_value='gnss_scenario.scen', description='GNSS simulator scenario name.')

# Dry-run?
CONF.declare('simulated', default_value=True, description='Simulated mode toggle.')

## Step 1: Setup phase - Initialize hardware devices
@plug(gnss_simulator=MockGnssSimulator, usb_hub=Acroname2x4)
def setup(test, gnss_simulator, usb_hub) -> None:
    # Start GNSS simulator
    gnss_simulator.load_scenario(scenario_name=CONF.gnss_simulator_scenario_name, reset=True)

    # Setup USB hub and reset USB ports
    usb_hub.connect()
    usb_hub.disable_all_ports()

## Step 2: Power on device
@plug(psu_control=MockPsuControl)
def power_on_device(test, psu_control) -> None:
    psu_control.turn_on()

## Step 3: Connect attenuator
@htf.PhaseOptions(repeat_limit=10, timeout_s=5)
@plug(attenuator=MockAttenuator)
def connect_attenuator(test, attenuator) -> PhaseResult:
    connected = attenuator.connect()
    if not connected:
        return PhaseResult.REPEAT
    else:
        attenuator.set_attenuation(0)
        return PhaseResult.CONTINUE

## Step 4: Initialize drone and connect
@htf.PhaseOptions(repeat_limit=10, timeout_s=5)
@plug(drone=MockDroneCom)
def initialize_drone(test, drone) -> PhaseResult:
    drone.switch_on('modem')
    if not drone.connect():
        return PhaseResult.REPEAT
    else:
        return PhaseResult.CONTINUE

## Step 5: Configure ground station modem
@plug(drone=MockDroneCom, attenuator=MockAttenuator)
def configure_ground_modem(test, drone, attenuator) -> PhaseResult:
    drone.configure_ground_modem()
    if not drone.connect_modem():
        return PhaseResult.STOP
    else:
        return PhaseResult.CONTINUE

## Step 6: Set GNSS antenna type
@plug(drone=MockDroneCom)
def set_gnss_antenna_type(test, drone) -> PhaseResult:
    match = re.search(r'\d+$', drone.get_drone_id())  # Find digits at the end of the ID

    if match and int(match.group()) >= 122:
        antenna_type = 'Type1'
    else:
        antenna_type = 'Type2'

    drone.set_rtk_antenna_type(antenna_type)
    return PhaseResult.CONTINUE

## Step 7: Communication test
@plug(drone=MockDroneCom, attenuator=MockAttenuator)
@measures(
    htf.Measurement('downlink_quality')
    .in_range(97.0, 100.0)
    .with_units('%')
    .with_precision(1)
)
def com_test(test, drone, attenuator) -> None:
    attenuation = 10
    attenuator.set_attenuation(attenuation)
    drone.send_sensors_telemetry()
    downlink_quality = drone.measure_downlink_quality()
    test.measurements.downlink_quality = downlink_quality

## Step 8: RSSI Test
@plug(drone=MockDroneCom)
@measures(
    htf.Measurement('rssi')
    .in_range(0.0, 95.0)
    .with_units('dBm')
    .with_precision(1)
)
def rssi_test(test, drone) -> None:
    test.measurements.rssi = drone.get_rssi()

## Step 9: Reset attenuation
@plug(attenuator=MockAttenuator)
def reset_attenuation(test, attenuator) -> None:
    attenuator.set_attenuation(0)

## Step 10: GNSS configuration
@plug(drone=MockDroneCom)
def gnss_configuring(test, drone) -> PhaseResult:
    if not drone.wait_for_gnss_configuration(timeout=50):
        return PhaseResult.STOP
    if not drone.wait_for_gnss_fix(timeout=120):
        return PhaseResult.STOP
    return PhaseResult.CONTINUE

## Step 11: GNSS test - Satellite Count
@plug(drone=MockDroneCom)
@measures(
    htf.Measurement('satellite_count')
    .in_range(5, 50)
    .with_precision(0)
)
def gnss_test_sat_count(test, drone) -> None:
    test.measurements.satellite_count = drone.receive_gnss_status()['sat_count']

## Step 12: GNSS test - Signal Strength
@plug(drone=MockDroneCom)
@measures(
    htf.Measurement('gnss_signal_strength')
    .in_range(38.0, 55.0)
    .with_units('dB')
    .with_precision(1)
)
def gnss_test_signal_strength(test, drone) -> None:
    test.measurements.gnss_signal_strength = drone.receive_gnss_status()['strength_L1']

## Step 13: Update GNSS license
@plug(drone=MockDroneCom)
def update_gnss_license(test, drone) -> PhaseResult:
    license_file = CONF.gnss_license_file
    if not drone.update_gnss_license(license_file):
        return PhaseResult.STOP
    else:
        return PhaseResult.CONTINUE

## Step 14: Test WiFi Remote ID
@plug(drone=MockDroneCom)
def test_wifi_remote_id(test, drone) -> PhaseResult:
    if drone.is_remote_id_applicable():
        drone.enable_wifi_remote_id()
        if not drone.check_wifi_remote_id():
            return PhaseResult.STOP

## Teardown phase
@plug(drone=MockDroneCom, psu_control=MockPsuControl)
def teardown(test, drone, psu_control) -> None:
    drone.switch_off()
    psu_control.turn_off()

# Main test procedure with TofuPilot integration
def main():
    test = htf.Test(
        setup,
        power_on_device,
        connect_attenuator,
        initialize_drone,
        configure_ground_modem,
        set_gnss_antenna_type,
        com_test,
        rssi_test,
        reset_attenuation,
        gnss_configuring,
        gnss_test_sat_count,
        gnss_test_signal_strength,
        update_gnss_license,
        test_wifi_remote_id,
        teardown,
        procedure_name="RF Box Test",
        procedure_id="RFBT-1"
    )

    with TofuPilot(test):
        test.execute(test_start=user_input.prompt_for_test_start())

if __name__ == "__main__":
    main()
