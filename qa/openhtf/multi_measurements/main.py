import openhtf as htf
from openhtf.util import units
import random
from tofupilot.openhtf import TofuPilot


# Utility function to simulate the test result with a given pass probability
def simulate_test_result(passed_prob):
    return random.random() < passed_prob


@htf.measures(htf.Measurement("firmware_version").equals("1.4.3"))
def pcba_firmware_version(test):
    test.measurements.firmware_version = (
        "1.4.3" if simulate_test_result(0.99) else "1.4.2"
    )


@htf.measures(htf.Measurement("button_status").equals(True))
def check_button(test):
    test.measurements.button_status = simulate_test_result(1)


@htf.measures(htf.Measurement("led_status").equals(True))
def check_led_switch_on(test):
    test.measurements.led_status = simulate_test_result(1)


@htf.measures(htf.Measurement("input_voltage").in_range(4.5, 5).with_units(units.VOLT))
def test_voltage_input(test):
    passed = simulate_test_result(0.99)
    test.measurements.input_voltage = (
        round(random.uniform(4.7, 4.9), 2)
        if passed
        else round(random.uniform(3.0, 3.8), 2)
    )


@htf.measures(
    htf.Measurement("output_voltage").in_range(3.2, 3.4).with_units(units.VOLT)
)
def test_voltage_output(test):
    passed = simulate_test_result(1)
    test.measurements.output_voltage = (
        round(random.uniform(3.25, 3.35), 2)
        if passed
        else round(random.uniform(0.1, 0.3), 2)
    )
    # time.sleep(5)


@htf.measures(
    htf.Measurement("current_protection_triggered")
    .in_range(maximum=1.5)
    .with_units(units.AMPERE)
)
def test_overcurrent_protection(test):
    passed = simulate_test_result(0.80)
    test.measurements.current_protection_triggered = (
        round(random.uniform(1.0, 1.4), 3)
        if passed
        else round(random.uniform(1.7, 1.8), 3)
    )
    time.sleep(0)


def test_battery_switch():
    if simulate_test_result(0.98):
        return htf.PhaseResult.CONTINUE
    else:
        return htf.PhaseResult.STOP


@htf.measures(
    htf.Measurement("efficiency").in_range(85, 98).with_units(units.Unit("%"))
)
def test_converter_efficiency(test):
    passed = simulate_test_result(0.99)
    input_power = 500
    output_power = (
        round(random.uniform(450, 480)) if passed else round(random.uniform(400, 425))
    )
    test.measurements.efficiency = round(((output_power / input_power) * 100), 1)
    # time.sleep(5)


@htf.measures(htf.Measurement("power_mode_functional").equals("on"))
def test_power_saving_mode(test):
    test.measurements.power_mode_functional = "on" if simulate_test_result(1) else "off"
    time.sleep(1)


def visual_control_pcb_coating(test):
    if simulate_test_result(1):
        test.attach_from_file("data/oscilloscope.jpeg")
        return htf.PhaseResult.CONTINUE
    else:
        return htf.PhaseResult.STOP


@htf.measures(
    htf.Measurement("is_connected").equals(True),
    htf.Measurement("firmware_version").equals("1.2.7"),
    htf.Measurement("temperature").in_range(20, 25).with_units(units.DEGREE_CELSIUS),
)
def phase_multi_measurements(test):
    test.measurements.is_connected = True
    test.measurements.firmware_version = (
        "1.2.7" if test.measurements.is_connected else "N/A"
    )
    test.measurements.temperature = round(random.uniform(22.5, 23), 2)


def main():
    # Define the test plan with all steps
    test = htf.Test(
        phase_multi_measurements,
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
        procedure_id="FVT9",
        procedure_name="Test QA",
        part_number="00220D",
        part_name="OpenHTF Script",
        revision="B",
        batch_number="1124-0001",
        sub_units=[{"serial_number": "00102"}],
        report_variables={
            "var1": "other automatic text from the script !!!!!???1234567890'±“#Ç[]|{}≠¿≠}{|][‘§æ¢]}",
            "var2": "I'm an automatic text from the script",
        },
    )

    # Generate random Serial Number
    random_digits = "".join([str(random.randint(0, 9)) for _ in range(5)])
    serial_number = f"00220D4K{random_digits}"

    # Execute the test
    with TofuPilot(test):
        test.execute(lambda: serial_number)


if __name__ == "__main__":
    main()
