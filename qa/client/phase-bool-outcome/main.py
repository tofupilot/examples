from tofupilot import TofuPilotClient
from datetime import datetime, timedelta
from random import randint


def main():
    client = TofuPilotClient()

    phases = [
        {
            "name": "step_initial_temp_check",  # Third phase
            "outcome": True,  # Outcome of the step
            "duration": timedelta(seconds=1, milliseconds=100),  # Duration of the step
            "started_at": datetime.now() + timedelta(seconds=2, milliseconds=500),
            "measurements": [
                {
                    "name": "initial_temperature",
                    "outcome": "PASS",  # Measurement outcome
                    "value": randint(-5, 20),  # Measured temperature value
                    "units": "°C",  # Unit of the measurement
                    "lower_limit": 0,  # Lower limit
                    "upper_limit": None,
                }
            ],
        },
    ]

    client.create_run(
        procedure_id="FVT9",
        procedure_name="Test_QA",
        unit_under_test={
            "part_number": "SI03645A",
            "part_name": "PythonScript",
            "revision": "3.1",
            "batch_number": "11-24",
            "serial_number": "2222",
        },
        run_passed=True,
        started_at=datetime.now(),
        phases=phases,
        attachments=["1_QA/oscilloscope.jpeg"],
        report_variables={
            "var1": "serial_number",
            "var2": "hahahah",
        },
        # sub_units=[{"serial_number": "00102"}],
    )


if __name__ == "__main__":
    main()
