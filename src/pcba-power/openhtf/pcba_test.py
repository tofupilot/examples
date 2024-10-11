import openhtf as htf
from openhtf.output.callbacks import json_factory
import tofupilot as tp
from openhtf.util import units
import random
import os


# Initialize the TofuPilot client
client = tp.TofuPilotClient()


# Utility function to simulate the test result with a given pass probability
def simulate_test_result(passed_prob):
    return random.random() < passed_prob

@htf.measures(htf.Measurement("device_firmware"))
def pcba_firmware_version(test):
    if simulate_test_result(1):
        test.measurements.device_firmware = "1.4.3"
    else:
        test.measurements.device_firmware = "Unknown"

def check_button():
    if simulate_test_result(1):
        return htf.PhaseResult.CONTINUE
    else:
        return htf.PhaseResult.STOP

def check_led_switch_on():
    if simulate_test_result(0.98):
        return htf.PhaseResult.CONTINUE
    else:
        return htf.PhaseResult.STOP

@htf.measures(
    htf.Measurement('input_voltage').in_range(20, 60).with_units(units.VOLT))
def test_voltage_input(test):
    passed = simulate_test_result(0.99) 
    test.measurements.input_voltage = round(random.uniform(40, 60)) if passed else round(random.uniform(20, 30))

@htf.measures(
    htf.Measurement('output_voltage').in_range(220, 240).with_units(units.VOLT))
def test_voltage_output(test):
    passed = simulate_test_result(0.99) 
    test.measurements.output_voltage = round(random.uniform(220, 240)) if passed else round(random.uniform(190, 200))

@htf.measures(
    htf.Measurement('current_protection_triggered').in_range(maximum=25).with_units(units.AMPERE))
def test_overcurrent_protection(test):
    passed = simulate_test_result(0.80)
    test.measurements.current_protection_triggered = round(random.uniform(26, 32),1) if passed else round(random.uniform(20, 24),1)

def test_battery_switch(test):
    if simulate_test_result(0.98):
        return htf.PhaseResult.CONTINUE
    else:
        return htf.PhaseResult.STOP

@htf.measures(
    htf.Measurement('efficiency').in_range(85, 98).with_units(units.Unit('%')))
def test_converter_efficiency(test):
    passed = simulate_test_result(0.99) 
    input_power = 500
    output_power = round(random.uniform(450, 480)) if passed else round(random.uniform(400, 425))
    test.measurements.efficiency = round(((output_power / input_power) * 100),1)

def test_power_saving_mode():
    if simulate_test_result(1):
        return htf.PhaseResult.CONTINUE
    else:
        return htf.PhaseResult.STOP
    
def visual_control_pcb_coating():
    if simulate_test_result(1):
        return htf.PhaseResult.CONTINUE
    else:
        return htf.PhaseResult.STOP

# Define the test plan with all steps
test = htf.Test(
    pcba_firmware_version,
    check_button,
    check_led_switch_on,
    test_voltage_input,
    test_voltage_output,
    test_overcurrent_protection,
    test_battery_switch,
    test_converter_efficiency,
    test_power_saving_mode,
    visual_control_pcb_coating,
    procedure_id="FVT197",
    part_number="00220",
    revision="A",
)


# Output the results to a JSON file
file_path = "result.json"
test.add_output_callbacks(json_factory.OutputToJSON(file_path))
# Generate random Serial Number
random_digits = "".join([str(random.randint(0, 9)) for _ in range(5)])
serial_number = f"00220A4J{random_digits}"
# Execute the test
test.execute(lambda: serial_number)

# Send the report to TofuPilot
client.create_run_from_report(file_path)