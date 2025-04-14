import random
import time

import numpy as np
import openhtf as htf
from openhtf.output.callbacks import json_factory
from openhtf.util import units
from tofupilot.openhtf import TofuPilot


@htf.measures(
    htf.Measurement("voltage_over_time").with_dimensions(units.VOLT_PER_SECOND),
)
def phase_array(test):
    for t in range(1, 50):
        milli_timestamp = t / 100
        voltage = round(random.uniform(3.3, 3.5), 2)
        voltage_over_time = voltage / milli_timestamp
        test.measurements.voltage_over_time[voltage_over_time] = 0  # OK


@htf.measures(
    htf.Measurement("voltage").with_dimensions(
        units.SECOND).with_units(units.VOLT),
    htf.Measurement("average_voltage").with_units(
        units.VOLT).in_range(
        3.3, 3.5),
    htf.Measurement("sinus").with_dimensions(units.SECOND, units.AMPERE),  # !
    htf.Measurement("neg_x_axis").with_dimensions(
        units.SECOND).with_units(units.VOLT),
    htf.Measurement("neg_y_axis").with_dimensions(
        units.SECOND).with_units(units.VOLT),
)
def phase_2_dim(test):
    len = 50
    sum_voltage = 0.0
    for t in range(len):
        voltage = round(random.uniform(3.3, 3.5), 2)
        test.measurements.voltage[t] = voltage
        sum_voltage += voltage
        negative_timestamp = -t
        test.measurements.neg_x_axis[negative_timestamp] = voltage
        test.measurements.neg_y_axis[t] = -voltage

    test.measurements.average_voltage = sum_voltage / len

    # Sinus
    x = np.linspace(0, 2 * np.pi, 100)
    y = np.sin(x)
    for i, amp in enumerate(y):
        test.measurements.sinus[i, amp] = 0


@htf.measures(
    htf.Measurement("current_and_voltage_over_time").with_dimensions(
        units.SECOND, units.VOLT, units.AMPERE
    ),
    htf.Measurement("current_voltage_resistence_over_time").with_dimensions(
        units.SECOND, units.VOLT, units.AMPERE, units.OHM
    ),
)
def phase_more_than_2_dim(test):
    for t in range(100):
        timestamp = t / 100
        voltage = round(random.uniform(3.3, 3.5), 2)
        current = round(random.uniform(0.3, 0.8), 3)
        resistance = voltage / current
        test.measurements.current_and_voltage_over_time[timestamp,
                                                        voltage, current] = t
        test.measurements.current_voltage_resistence_over_time[
            timestamp, voltage, current, resistance
        ] = 0


def main():
    # Define the test plan with all steps
    test = htf.Test(
        phase_array,
        phase_2_dim,
        phase_more_than_2_dim,
        procedure_id="FVT2",
        procedure_name="Functional Testing",
        part_number="00220S",
        part_name="Motherboard PCB",
        revision="B",
        batch_number="1124-0001",
    )

    # Generate random Serial Number
    random_digits = "".join([str(random.randint(0, 9)) for _ in range(5)])
    serial_number = f"00220D4K{random_digits}"

    test.add_output_callbacks(
        json_factory.OutputToJSON(
            "test_result.json", indent=2))

    start = time.time()
    # Execute the test
    with TofuPilot(
        test,
        url="https://app-git-manon-app-2831-tofupilot.vercel.app",
        api_key="589e6e00-9c6d-4126-aaab-5dbcccdb38a5",
    ):
        test.execute(lambda: serial_number)

    end = time.time()
    duration = end - start
    print(f"Durée : {duration:.2f} secondes")


if __name__ == "__main__":
    main()
