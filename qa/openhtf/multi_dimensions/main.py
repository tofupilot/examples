import random

import numpy as np
import openhtf as htf
from openhtf.util import units
from tofupilot.openhtf import TofuPilot


@htf.measures(
    htf.Measurement("voltage").with_dimensions(units.SECOND).with_units(units.VOLT),
    htf.Measurement("mean_voltage").with_units(units.VOLT).in_range(3.3, 3.5),
    htf.Measurement("sinus").with_dimensions(units.SECOND).with_units(units.AMPERE),
    htf.Measurement("neg_x_axis").with_dimensions(units.SECOND).with_units(units.VOLT),
    htf.Measurement("neg_y_axis").with_dimensions(units.SECOND).with_units(units.VOLT),
)
def multi_dimension_phase(test):
    len = 50
    sum_voltage = 0.0
    for t in range(len):
        voltage = round(random.uniform(3.3, 3.5), 2)
        test.measurements.voltage[t] = voltage
        sum_voltage += voltage
        negative_timestamp = -t
        test.measurements.neg_x_axis[negative_timestamp] = voltage
        test.measurements.neg_y_axis[t] = -voltage

    test.measurements.mean_voltage = sum_voltage / len

    # Sinus
    x = np.linspace(0, 2 * np.pi, 100)
    y = np.sin(x)
    for i, amp in enumerate(y):
        test.measurements.sinus[i] = amp


@htf.measures(
    htf.Measurement("current_and_voltage_over_time")
    .with_dimensions(units.SECOND, units.VOLT)
    .with_units(units.AMPERE),
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
        test.measurements.current_and_voltage_over_time[timestamp,
                                                        voltage] = current
        test.measurements.current_voltage_resistence_over_time[
            timestamp, voltage, current
        ] = resistance


def main():
    test = htf.Test(
        multi_dimension_phase,
        power_phase,
        procedure_id="FVT2",
        procedure_name="Functional Testing",
        part_number="00220S",
        part_name="Motherboard PCB",
        revision="B",
        batch_number="1124-0001",
    )

    random_digits = "".join([str(random.randint(0, 9)) for _ in range(5)])
    serial_number = f"00220D4K{random_digits}"

    with TofuPilot(test):
        test.execute(lambda: serial_number)


if __name__ == "__main__":
    main()
