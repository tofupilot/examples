import openhtf as htf
from openhtf.output.callbacks import json_factory
import tofupilot as tp
from openhtf.util import units
import random
from tofupilot import UploadToTofuPilot


# Utility function to simulate the test result with a given pass probability
def simulate_test_result(passed_prob):
    return random.random() < passed_prob


# Boolean Step: Visual Inspection
def visual_inspection():
    """Perform a visual inspection of the PCBA."""
    if simulate_test_result(0.98):
        return htf.PhaseResult.CONTINUE
    else:
        return htf.PhaseResult.STOP


# Boolean Step: Validate the backplane interface connectivity
def backplane_interface_validation():
    """Validate the backplane interface connectivity."""
    if simulate_test_result(0.95): 
        return htf.PhaseResult.CONTINUE
    else:
        return htf.PhaseResult.STOP


# String Measurement: Firmware Version Check
@htf.measures(htf.Measurement("device_status"))
def pcba_firmware_version(test):
    """Check the firmware version on the PCBA."""
    if simulate_test_result(1.0):
        test.measurements.device_status = "1.4.3"
    else:
        test.measurements.device_status = "Unknown"


# Numeric Measurement: Power Consumption Check
@htf.measures(
    htf.Measurement("power_consumption")
    .in_range(maximum=80.0)
    .with_units(units.WATT)
)
def check_power_consumption(test):
    """Measure the power consumption of the unit (in Watts)."""
    passed = simulate_test_result(0.99) 
    value_measured = round(random.uniform(75, 80), 1) if passed else round(random.uniform(81, 85), 1)
    test.measurements.power_consumption = value_measured


# Numeric Measurement: Thermal Sensor Check
@htf.measures(
    htf.Measurement("thermal_value")
    .in_range(minimum=35.0, maximum=55.0)
    .with_units(units.DEGREE_CELSIUS)
)
def check_thermal_sensor(test):
    """Check the thermal sensor value (in degrees Celsius)."""
    passed = simulate_test_result(0.80) 
    value_measured = round(random.uniform(35, 55), 1) if passed else round(random.uniform(56, 85), 1)
    test.measurements.thermal_value = value_measured


# Numeric Measurement: 12V Power Supply Check
@htf.measures(
    htf.Measurement("voltage_12V")
    .in_range(minimum=11.5, maximum=12.5)
    .with_units(units.VOLT)
)
def check_power_supply_12V(test):
    """Check the 12V power supply output."""
    passed = simulate_test_result(0.95)
    value_measured = round(random.uniform(12, 12.5), 1) if passed else round(random.uniform(10.5, 11.4), 1)
    test.measurements.voltage_12V = value_measured


# Numeric Measurement: 3.3V Power Supply Check
@htf.measures(
    htf.Measurement("voltage_3V3")
    .in_range(minimum=3.0, maximum=3.6)
    .with_units(units.VOLT)
)
def check_power_supply_3V3(test):
    """Check the 3.3V power supply output."""
    passed = simulate_test_result(0.90)
    value_measured = round(random.uniform(3.3, 3.6), 2) if passed else round(random.uniform(1.1, 2.9), 2)
    test.measurements.voltage_3V3 = value_measured


# Boolean Step: EEPROM Read Check
def read_eeprom():
    """Verify the EEPROM read functionality."""
    return htf.PhaseResult.CONTINUE if simulate_test_result(0.98) else htf.PhaseResult.STOP


# Boolean Step: EEPROM Write Check
def write_eeprom():
    """Verify the EEPROM write functionality."""
    return htf.PhaseResult.CONTINUE if simulate_test_result(0.97) else htf.PhaseResult.STOP


# Boolean Step: eMMC Read and Write Check
def read_and_write_eMMC():
    """Verify read and write operations on the eMMC."""
    return htf.PhaseResult.CONTINUE if simulate_test_result(0.96) else htf.PhaseResult.STOP


# Boolean Step: JTAG Connector Check
def check_JTAG_connector():
    """Check the connectivity and integrity of the JTAG connector."""
    return htf.PhaseResult.CONTINUE if simulate_test_result(0.99) else htf.PhaseResult.STOP


# Numeric Measurement: Gain Bandwidth at 15 GHz
@htf.measures(
    htf.Measurement("gain_bandwidth_15GHz")
    .in_range(minimum=-7.2, maximum=-6.8)
    .with_units(units.DECIBEL_MILLIWATTS)
)
def check_gain_bandwidth_at_15GHz(test):
    """Check the gain and bandwidth at 15 GHz."""
    passed = simulate_test_result(0.98)
    value_measured = round(random.uniform(-7.2, -6.8), 1) if passed else round(random.uniform(-7.8, -7.3),1)
    test.measurements.gain_bandwidth_15GHz = value_measured

# Numeric Measurement: Gain Bandwidth at 15 GHz
@htf.measures(
    htf.Measurement("gain_bandwidth_15p5GHz")
    .in_range(minimum=-7.2, maximum=-6.8)
    .with_units(units.DECIBEL_MILLIWATTS)
)
def check_gain_bandwidth_at_15p5GHz(test):
    """Check the gain and bandwidth at 15 GHz."""
    passed = simulate_test_result(0.99)
    value_measured = round(random.uniform(-7.2, -6.8), 1) if passed else round(random.uniform(-7.8, -7.3),1)    
    test.measurements.gain_bandwidth_15p5GHz = value_measured

# Numeric Measurement: Gain Bandwidth at 15 GHz
@htf.measures(
    htf.Measurement("gain_bandwidth_16GHz")
    .in_range(minimum=-7.2, maximum=-6.8)
    .with_units(units.DECIBEL_MILLIWATTS)
)
def check_gain_bandwidth_at_16GHz(test):
    """Check the gain and bandwidth at 15 GHz."""
    passed = simulate_test_result(0.99)
    value_measured = round(random.uniform(-7.2, -6.8), 1) if passed else round(random.uniform(-7.8, -7.3),1)        
    test.measurements.gain_bandwidth_16GHz = value_measured


# Define the test plan with all steps
test = htf.Test(
    visual_inspection,
    backplane_interface_validation,
    pcba_firmware_version,
    check_power_supply_12V,
    check_power_supply_3V3,
    check_power_consumption,
    check_thermal_sensor,
    read_eeprom,
    write_eeprom,
    read_and_write_eMMC,
    check_JTAG_connector,
    check_gain_bandwidth_at_15GHz,
    check_gain_bandwidth_at_15p5GHz,
    check_gain_bandwidth_at_16GHz, 
    procedure_id="FVT3",
    part_number="00389",
    sub_units=[{"serial_number": "00375A4J34856"}],
    revision="A",
)

test.add_output_callbacks(UploadToTofuPilot())

# Generate random Serial Number
random_digits = "".join([str(random.randint(0, 9)) for _ in range(5)])
serial_number = f"00389B4J{random_digits}"

# Execute the test
test.execute(lambda: serial_number)