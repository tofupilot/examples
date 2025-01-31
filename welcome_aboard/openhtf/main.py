from tofupilot.openhtf import TofuPilot
import openhtf as htf
from openhtf.util import units
import random


def setup_battery_test():
    htf.PhaseResult.CONTINUE


@htf.measures(htf.Measurement("firmware_version").equals("prod_2.5.1"))
def flash_firmware_and_check_version(test):
    test.measurements.firmware_version = "prod_2.5.1"


@htf.measures(
    htf.Measurement("gauge_syspress").equals(True),
    htf.Measurement("calibration_current_CCGain").equals(3.631),
)
def configure_gauge_parameters(test):
    test.measurements.gauge_syspress = True
    test.measurements.calibration_current_CCGain = 3.631


@htf.measures(
    htf.Measurement("input_voltage").in_range(3.1, 3.5).with_units(units.VOLT),
    htf.Measurement("output_current").in_range(maximum=0.655).with_units(units.AMPERE),
    htf.Measurement("state_of_health").in_range(minimum=0.95).with_units("%"),
)
def measure_battery_state(test):
    test.measurements.input_voltage = round(random.uniform(3.1, 3.6), 1)
    test.measurements.output_current = round(random.uniform(0.5, 0.660), 3)
    test.measurements.state_of_health = round(random.uniform(0.93, 0.98), 2)


def generate_serial_number():
    random_digits = "".join([str(random.randint(0, 9)) for _ in range(3)])
    return f"PCB01A{random_digits}"


def main():
    test = htf.Test(
        setup_battery_test,
        flash_firmware_and_check_version,
        configure_gauge_parameters,
        measure_battery_state,
        # Procedure information
        test_name="Battery PCBA Testing",
        procedure_id="FVT1",  # optional
        # Unit Under Test information
        part_number="PCB01",
        part_name="Battery PCBA Motherboard",  # optional
        revision="A",  # optional
        batch_number="12-24",  # optional
    )

    with TofuPilot(test):
        test.execute(lambda: generate_serial_number())


if __name__ == "__main__":
    main()
