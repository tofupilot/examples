import openhtf as htf
from tofupilot.openhtf import TofuPilot
from openhtf.util import units


def step_connect():
    htf.PhaseResult.CONTINUE


@htf.measures(htf.Measurement("firmware_version").equals("v2.5.1"))
def step_firmware_version_check(test):
    test.measurements.firmware_version = "v2.5.1"


@htf.measures(
    htf.Measurement("temperature").in_range(70, 80).with_units(units.DEGREE_CELSIUS)
)
def step_temperature_calibration(test):
    test.measurements.temperature = 75


def main():
    test = htf.Test(
        step_connect,
        step_firmware_version_check,
        step_temperature_calibration,
        procedure_id="FVT2",
        procedure_name="PCB Temperature Calibration",
        part_number="PCB1",
    )
    with TofuPilot(test):
        test.execute(lambda: "PCB1A002")


if __name__ == "__main__":
    main()
