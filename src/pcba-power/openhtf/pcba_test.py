import openhtf as htf
from openhtf.util import units
import random
from tofupilot.openhtf import TofuPilot


# Utility function to simulate the test result with a given pass probability
def simulate_test_result(passed_prob):
    return random.random() < passed_prob


@htf.measures(htf.Measurement("firmware_version").equals("1.4.3"))
def pcba_firmware_version(test):
    firmware_version = "1.4.3" if simulate_test_result(0.99) else "1.4.2"


@htf.measures(htf.Measurement("button_status").equals(True))
def check_button(test):
    button_status = simulate_test_result(1)


@htf.measures(htf.Measurement("led_status").equals(True))
def check_led_switch_on(test):
    button_status = simulate_test_result(0.98)


@htf.measures(htf.Measurement("input_voltage").in_range(20, 60).with_units(units.VOLT))
def test_voltage_input(test):
    passed = simulate_test_result(0.99)
    test.measurements.input_voltage = (
        round(random.uniform(40, 60)) if passed else round(random.uniform(20, 30))
    )


@htf.measures(
    htf.Measurement("output_voltage").in_range(220, 240).with_units(units.VOLT)
)
def test_voltage_output(test):
    passed = simulate_test_result(0.99)
    test.measurements.output_voltage = (
        round(random.uniform(220, 240)) if passed else round(random.uniform(190, 200))
    )


@htf.measures(
    htf.Measurement("current_protection_triggered")
    .in_range(maximum=25)
    .with_units(units.AMPERE)
)
def test_overcurrent_protection(test):
    passed = simulate_test_result(0.80)
    test.measurements.current_protection_triggered = (
        round(random.uniform(26, 32), 1) if passed else round(random.uniform(20, 24), 1)
    )


def test_battery_switch(test):
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


@htf.measures(htf.Measurement("power_mode_functional").equals(True))
def test_power_saving_mode(test):
    test.measurement.power_mode_functional = simulate_test_result(1)


def visual_control_pcb_coating(test):
    if simulate_test_result(1):
        test.attach_from_file("pcba-power/openhtf/pcb_coating.jpeg")
        return htf.PhaseResult.CONTINUE
    else:
        return htf.PhaseResult.STOP


def main(test_qty):
    for _ in range(test_qty):
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
            procedure_id="FVT1",
            part_number="00220",
            revision="A",
        )

        # Generate random Serial Number
        random_digits = "".join([str(random.randint(0, 9)) for _ in range(5)])
        serial_number = f"00220A4J{random_digits}"

        # Execute the test
        with TofuPilot(test):
            test.execute(lambda: serial_number)


if __name__ == "__main__":
    main(5)
