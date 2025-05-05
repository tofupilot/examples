import openhtf as htf
from openhtf.util import units
from tofupilot.openhtf import TofuPilot
import random


@htf.measures(
    htf.Measurement("current_voltage_resistence_over_time")
    .with_dimensions(units.SECOND, units.VOLT, units.AMPERE)
    .with_units(units.OHM),
)
def power_phase(test):
    for t in range(100):
        timestamp = t / 100
        voltage = round(random.uniform(3.3, 3.5), 2)
        current = round(random.uniform(0.3, 0.8), 3)
        resistance = voltage / current
        test.measurements.current_voltage_resistence_over_time[
            timestamp, voltage, current
        ] = resistance


def main():
    test = htf.Test(
        power_phase,
        procedure_id="FVT1",
        part_number="PCB01",
    )

    # Execute the test
    with TofuPilot(test):
        test.execute(lambda: "PCB1A003")


if __name__ == "__main__":
    main()
