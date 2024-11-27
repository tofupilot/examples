import openhtf as htf
from openhtf import measures
from openhtf.plugs import plug, user_input
from openhtf.util import units
from openhtf.util.configuration import CONF
from tofupilot.openhtf import TofuPilot

from plug.com.mock_drone_com import MockDroneCom  # Assuming this plug can read all sensors
from plug.power.mock_psu_control import MockPsuControl

# Test station specific configuration
CONF.declare('known_distance_mm', default_value=1000, description='Known distance in millimeters for the laser distance sensor calibration.')
CONF.declare('distance_tolerance_mm', default_value=5, description='Tolerance in millimeters for laser distance measurement.')
CONF.declare('simulated', default_value=True, description='Simulated mode toggle.')

## Step 1: Check temperature sensor calibration against golden sample
@plug(drone_com=MockDroneCom)
@measures(htf.Measurement('temperature_difference')
          .in_range(-1.0, 1.0)  # Tolerance of +/-1°C
          .with_units(units.DEGREE_CELSIUS)
          .with_precision(1))
def check_temperature_sensor(test: htf.TestApi, drone_com: MockDroneCom) -> None:
    dut_temperature = drone_com.get_temperature()
    golden_temperature = drone_com.get_temperature(golden_sample=True)
    temperature_difference = dut_temperature - golden_temperature
    test.logger.info(f"DUT Temperature: {dut_temperature} °C")
    test.logger.info(f"Golden Sample Temperature: {golden_temperature} °C")
    test.logger.info(f"Temperature Difference: {temperature_difference} °C")
    test.measurements.temperature_difference = temperature_difference

## Step 2: Check pressure sensor calibration against golden sample
@plug(drone_com=MockDroneCom)
@measures(htf.Measurement('pressure_difference')
          .in_range(-1.0, 1.0)  # Tolerance of +/-1 hPa
          .with_units(units.HECTOPASCAL)
          .with_precision(1))
def check_pressure_sensor(test: htf.TestApi, drone_com: MockDroneCom) -> None:
    dut_pressure = drone_com.get_pressure()
    golden_pressure = drone_com.get_pressure(golden_sample=True)
    pressure_difference = dut_pressure - golden_pressure
    test.logger.info(f"DUT Pressure: {dut_pressure} hPa")
    test.logger.info(f"Golden Sample Pressure: {golden_pressure} hPa")
    test.logger.info(f"Pressure Difference: {pressure_difference} hPa")
    test.measurements.pressure_difference = pressure_difference

## Step 3: Check laser distance sensor calibration
@plug(drone_com=MockDroneCom)
@measures(htf.Measurement('distance_error')
          .in_range(-CONF.distance_tolerance_mm, CONF.distance_tolerance_mm)
          .with_units(units.MILLIMETRE)
          .with_precision(1))
def check_distance_sensor(test: htf.TestApi, drone_com: MockDroneCom) -> None:
    known_distance = CONF.known_distance_mm
    dut_distance = drone_com.get_distance()
    distance_error = dut_distance - known_distance
    test.logger.info(f"DUT Measured Distance: {dut_distance} mm")
    test.logger.info(f"Known Distance: {known_distance} mm")
    test.logger.info(f"Distance Error: {distance_error} mm")
    test.measurements.distance_error = distance_error

## Teardown
@plug(power_supply=MockPsuControl)
def teardown(power_supply: MockPsuControl) -> None:
    power_supply.turn_off()

# Main test procedure
def main() -> None:
    test = htf.Test(
        check_temperature_sensor,
        check_pressure_sensor,
        check_distance_sensor,
        teardown,
        procedure_name="Sensor Calibration Test",
        procedure_id="SCT-1"
    )

    with TofuPilot(test):
        test.execute(test_start=user_input.prompt_for_test_start())

if __name__ == "__main__":
    main()
