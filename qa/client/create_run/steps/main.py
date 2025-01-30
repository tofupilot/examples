from tofupilot import TofuPilotClient
from datetime import datetime
import time


client = TofuPilotClient()


def initial_temperature_check():
    return True, None, None, None, None


def temperature_calibration():
    return True, 75.0, "°C", 70.0, 80.0


def middle_temperature_check():
    return False, 81.2, "°C", None, 80.0


def final_temperature_check():
    return True, 75.0, "°C", None, None


def run_all_tests():
    tests = [
        initial_temperature_check,
        temperature_calibration,
        middle_temperature_check,
        final_temperature_check,
    ]
    steps = []
    all_tests_passed = True

    for test in tests:
        start_time = datetime.now()
        passed, value_measured, unit, limit_low, limit_high = test()
        end_time = datetime.now()

        step = {
            "name": test.__name__,
            "started_at": start_time,
            "duration": end_time - start_time,
            "step_passed": passed,
            "measurement_unit": unit,
            "measurement_value": value_measured,
            "limit_low": limit_low,
            "limit_high": limit_high,
        }

        steps.append(step)

        if not passed:
            all_tests_passed = False

        attachments = ["data/oscilloscope.jpeg"]

    return all_tests_passed, steps, attachments


# Run the tests and create the run
run_passed, steps, attachments = run_all_tests()

client.create_run(
    procedure_id="FVT1",
    unit_under_test={"part_number": "PCB01", "serial_number": "00121"},
    run_passed=run_passed,
    steps=steps,
    attachments=attachments,
)
