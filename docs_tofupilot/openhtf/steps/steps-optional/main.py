import openhtf as htf
from tofupilot.openhtf import TofuPilot
from openhtf.util import units


# Add decorator to set measurement name, unit and limits
@htf.measures(htf.Measurement("voltage").in_range(3.1, 3.5).with_units(units.VOLT))
# Step return a Pass status due to measurement (3.3) within defined limits [3.1, 3.5]
def step_voltage_measure(test):
    test.measurements.voltage = 3.3


def main():
    test = htf.Test(step_voltage_measure, procedure_id="FVT1", part_number="PCB1")
    with TofuPilot(test):
        test.execute(lambda: "PCB1A001")


if __name__ == "__main__":
    main()
