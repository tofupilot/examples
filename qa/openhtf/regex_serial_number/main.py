import random

import openhtf as htf
from tofupilot.openhtf import TofuPilot


@htf.measures(htf.Measurement("button_status").equals(True))
def check_button(test):
    test.measurements.button_status = bool(random.randint(0, 1))


def main():
    test = htf.Test(
        check_button,
        procedure_id="FVT1",
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
