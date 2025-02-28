import random

import openhtf as htf
from openhtf.util import units
from tofupilot.openhtf import TofuPilot


def phase_without_measurement():
    if random.choice([True, False]):
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
    test = htf.Test(
        phase_without_measurement,
        phase_multi_measurements,
        procedure_id="FVT1",
        procedure_name="PCB Testing",
        # REGEX is defined in the Settings from Serial Number for:
        # part_number="00221",
        # revision="B",
        # batch="4K"
    )

    serial_number = f"00221B4K{random.randint(10000, 99999)}"

    with TofuPilot(test):
        test.execute(lambda: serial_number)


if __name__ == "__main__":
    main()
