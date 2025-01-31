import random

import openhtf as htf
from openhtf.util import units
from tofupilot.openhtf import TofuPilot


# Simulate passing probability for a test result
def simulate_test_result(passed_prob):
    return random.random() < passed_prob


def setup_and_connect():
    htf.PhaseResult.CONTINUE


@htf.measures(htf.Measurement("firmware_version").equals("prod_2.5.1"))
def flash_production_firmware(test):
    # PCBA is flashed and the version is checked by bench
    test.measurements.firmware_version = "prod_2.5.1"


@htf.measures(
    htf.Measurement("gauge_syspress").equals(True),
    htf.Measurement("calibration_voltage_cellGain").equals(12133),
    htf.Measurement("calibration_current_CCGain").equals(3.6310),
    htf.Measurement("calibration_Temperature_InternalTempOffset").equals("on"),
)
def configuration_battery_gauge(test):
    test.measurements.gauge_syspress = True
    test.measurements.calibration_voltage_cellGain = 12133
    test.measurements.calibration_current_CCGain = 3.6310
    test.measurements.calibration_Temperature_InternalTempOffset = "on"


@htf.measures(
    htf.Measurement("input_voltage").in_range(3.1, 3.5).with_units(units.VOLT),
    htf.Measurement("output_voltage").in_range(1.1, 1.3).with_units(units.VOLT),
    htf.Measurement("output_current").in_range(0.500, 0.655).with_units(units.AMPERE),
    htf.Measurement("state_of_health").in_range(minimum=0.95).with_units("%"),
)
def phase_voltage_measurements(test):
    passed = simulate_test_result(0.85)
    test.measurements.input_voltage = (
        round(random.uniform(3.1, 3.5), 1)
        if passed
        else round(random.uniform(0, 0.010), 3)
    )
    test.measurements.output_voltage = (
        round(random.uniform(1.2, 1.3), 1) if passed else 0
    )
    test.measurements.output_current = (
        round(random.uniform(0.5, 0.655), 3)
        if passed
        else round(random.uniform(0, 0.010), 3)
    )
    test.measurements.state_of_health = round(random.uniform(0.95, 0.98), 2)


@htf.measures(
    htf.Measurement("internal_resistance_value")
    .in_range(0.005, 0.015)
    .with_units(units.OHM),
)
def ir_test(test):
    test.measurements.internal_resistance_value = round(
        random.uniform(0.007, 0.012), 3)


def teardown(test):
    test.logger.info("Running teardown")


def make_test():
    return htf.Test(
        htf.PhaseGroup.with_teardown(teardown)(
            setup_and_connect,
            flash_production_firmware,
            configuration_battery_gauge,
            phase_voltage_measurements,
            ir_test,
        ),
        procedure_id="FVT1",
        procedure_name="Battery PCBA Testing",
        part_number="PCB01",
        part_name="Battery PCBA Motherboard",
        revision="A",
        batch_number="12-24",
    )


def main():
    test = make_test()

    random_digits = "".join([str(random.randint(0, 9)) for _ in range(3)])
    serial_number = f"PCB01A{random_digits}"

    with TofuPilot(test):
        test.execute(lambda: serial_number)


if __name__ == "__main__":
    main()
