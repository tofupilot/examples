from datetime import datetime
from tofupilot import MeasurementOutcome, PhaseOutcome, TofuPilotClient
import random

client = TofuPilotClient()


def phase_voltage_measure():
    start_time_millis = datetime.now().timestamp() * 1000

    structured_measurements = []
    for t in range(100):
        timestamp = t / 100
        voltage = round(random.uniform(3.3, 3.5), 2)
        current = round(random.uniform(0.3, 0.8), 3)
        resistance = voltage / current
        structured_measurements.append((timestamp, voltage, current, resistance))

    phase = [
        {
            "name": "power_phase",
            "outcome": PhaseOutcome.PASS,
            "start_time_millis": start_time_millis,
            "end_time_millis": start_time_millis + 30 * 1000,
            "measurements": [
                {
                    "name": "current_voltage_resistence_over_time",
                    "units": ["s", "V", "A", "Ohm"],
                    "measured_value": structured_measurements,
                    "outcome": MeasurementOutcome.PASS,
                }
            ],
        }
    ]

    return phase


def main():
    phases = phase_voltage_measure()

    client.create_run(
        procedure_id="FVT1",  # Create the procedure first in the Application
        unit_under_test={"serial_number": "PCB1A001", "part_number": "PCB1"},
        phases=phases,
        run_passed=all(phase["outcome"] == PhaseOutcome.PASS for phase in phases),
    )


if __name__ == "__main__":
    main()
