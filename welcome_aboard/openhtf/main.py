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
    htf.Measurement("sensor_i2c_response").equals(True),
    htf.Measurement("sensor_adc_accuracy")
    .in_range(0.95, 1.05)
    .with_units(units.PERCENT),
    htf.Measurement("sensor_temperature_reading")
    .in_range(-10, 85)
    .with_units(units.DEGREE_CELSIUS),
)
def check_sensors(test):
    test.measurements.sensor_i2c_response = True
    test.measurements.sensor_adc_accuracy = round(
        random.uniform(0.95, 1.05), 2)
    test.measurements.sensor_temperature_reading = round(
        random.uniform(-10, 85), 1)


def generate_serial_number():
    random_digits = "".join([str(random.randint(0, 9)) for _ in range(3)])
    return f"PCBA123{random_digits}"


def main():
    test = htf.Test(
        check_mcu_power,
        check_sensors,
        # Procedure information
        test_name="PCBA Functional Testing",
        procedure_id="PCBA_FVT1",  # optional
        # Unit Under Test information
        part_number="PCBA123",
        part_name="PCBA Control Board",  # optional
        revision="B",  # optional
        batch_number="01-25",  # optional
    )

    with TofuPilot(test):
        test.execute(generate_serial_number)


if __name__ == "__main__":
    main()
