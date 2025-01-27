from tofupilot import TofuPilotClient
from datetime import datetime, timedelta
import random


client = TofuPilotClient()


def simulate_test_result(yield_percentage):
    return random.random() < (yield_percentage / 100.0)


def esr_test():
    passed = simulate_test_result(99)
    value_measured = (
        round(random.uniform(5, 9), 2) if passed else round(random.uniform(10, 15), 2)
    )
    return passed, value_measured, "mOhm", None, 10


def cell_voltage_test():
    passed = simulate_test_result(99)
    value_measured = (
        round(random.uniform(3.65, 3.75), 2)
        if passed
        else round(random.uniform(3.5, 3.64), 2)
    )
    return passed, value_measured, "V", 3.65, 3.75


# FINAL Tests
def battery_connection():
    passed = simulate_test_result(100)
    return passed, None, None, None, None


def check_voltage():
    passed = simulate_test_result(95)
    value_measured = (
        round(random.uniform(10.1, 12.0), 0)
        if passed
        else round(random.uniform(9.0, 10.0), 1)
    )
    return passed, value_measured, "V", 10.1, None


def check_soc():
    passed = simulate_test_result(95)
    value_measured = (
        round(random.uniform(40, 60), 0) if passed else round(random.uniform(20, 39), 2)
    )
    return passed, value_measured, "%", 40, 60


def check_soh():
    passed = simulate_test_result(60)
    value_measured = (
        round(random.uniform(96, 100), 0)
        if passed
        else round(random.uniform(70, 95), 2)
    )
    #    value_measured = round(random.uniform(96, 100), 0) if passed else round(random.uniform(0, 20), 2)
    return passed, value_measured, "%", 95, None


def take_picture():
    passed = simulate_test_result(100)
    return passed, None, None, None, None


def run_test(test, duration):
    start_time = datetime.now()
    passed, value_measured, unit, limit_low, limit_high = test()

    step = {
        "name": test.__name__,
        "started_at": start_time,
        "duration": duration,
        "step_passed": passed,
        "measurement_unit": unit,
        "measurement_value": value_measured,
        "limit_low": limit_low,
        "limit_high": limit_high,
    }
    return passed, step


def run_all_tests(tests, previous_failed_step=None):
    steps = []
    all_tests_passed = True
    current_duration = timedelta(0)
    failed_at_step = None

    for index, (test, duration) in enumerate(tests):
        if previous_failed_step is not None and index == previous_failed_step["index"]:
            passed = previous_failed_step["step_passed"]
            step = previous_failed_step
        else:
            passed, step = run_test(test, duration)

        steps.append(step)

        if not passed:
            failed_at_step = {
                "index": index,
                "step_passed": passed,
                "name": step["name"],
                "started_at": step["started_at"],
                "duration": step["duration"],
                "measurement_unit": step["measurement_unit"],
                "measurement_value": step["measurement_value"],
                "limit_low": step["limit_low"],
                "limit_high": step["limit_high"],
            }
            all_tests_passed = False
            break

        current_duration += duration

    return all_tests_passed, steps, failed_at_step


def handle_procedure(
    procedure_id, tests, serial_number, part_number, revision, sub_units
):
    run_passed, steps, failed_step = run_all_tests(tests)

    client.create_run(
        procedure_id=procedure_id,
        unit_under_test={
            "part_number": part_number,
            "revision": revision,
            "serial_number": serial_number,
        },
        run_passed=run_passed,
        steps=steps,
        sub_units=sub_units,
        report_variables=(
            {
                "variable1": "X",
                "variable2": "Y",
            }
            if procedure_id == "FVT2"
            else None
        ),
    )

    return run_passed, failed_step


def main():
    serial_number_cell = "A0B8-0:04d"
    # serial_number_pcb = f"A0X4-{i:04d}"

    # Gérer les tests CELL
    tests_cell = [
        (esr_test, timedelta(seconds=4)),
        (cell_voltage_test, timedelta(seconds=0.1)),
    ]
    passed_cell, _ = handle_procedure(
        "FVT2", tests_cell, serial_number_cell, "CELL0B8", "A", None
    )

    if not passed_cell:
        return

    tests_final = [
        (battery_connection, timedelta(seconds=0.1)),
        (check_voltage, timedelta(seconds=3)),
        (check_soc, timedelta(seconds=1)),
        (check_soh, timedelta(seconds=1)),
        (take_picture, timedelta(seconds=12)),
    ]
    handle_procedure(
        "FVT3",
        tests_final,
        "B1F3-04d",
        "BAT123",
        "C",
        [{"serial_number": serial_number_cell}],
    )


main()
