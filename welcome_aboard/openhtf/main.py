import random

import openhtf as htf
from openhtf.util import units
from tofupilot.openhtf import TofuPilot


@htf.measures(
    htf.Measurement("mcu_core_voltage").in_range(1.7, 1.9).with_units(units.VOLT),
    htf.Measurement("mcu_clock_speed").equals(48).with_units(units.MEGAHERTZ),
    htf.Measurement("flash_integrity").equals(True),
)
def check_mcu_power(test):
    test.measurements.mcu_core_voltage = round(random.uniform(1.7, 1.9), 2)
    test.measurements.mcu_clock_speed = 48
    test.measurements.flash_integrity = True


@htf.measures(
    htf.Measurement("i2c_response").equals(True),
    htf.Measurement("accuracy").in_range(0.95, 1.05).with_units(units.PERCENT),
    htf.Measurement("temperature").in_range(-10, 85).with_units(units.DEGREE_CELSIUS),
)
def check_sensors(test):
    test.measurements.i2c_response = True
    test.measurements.accuracy = round(random.uniform(0.95, 1.05), 2)
    test.measurements.temperature = round(random.uniform(-10, 85), 1)


def main(serial_number: str):
    test = htf.Test(
        check_mcu_power,
        check_sensors,
        procedure_name="PCBA Test",
        part_number="PCBA01",
        part_name="PCBA",  # optional
        revision="A",  # optional
    )

    with TofuPilot(test):
        test.execute(lambda: serial_number)


if __name__ == "__main__":
    main(f"PCBA01{random.randint(100, 999)}")
