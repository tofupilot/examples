from tofupilot import TofuPilotClient
from datetime import datetime, timedelta
import random

client = TofuPilotClient()


def simulate_test_result(yield_percentage):
    return random.random() < (yield_percentage / 100.0)


def battery_connection():
    passed = simulate_test_result(100)
    return passed, None, None, None, None


def check_voltage():
    passed = simulate_test_result(100)
    value_measured = (
        round(random.uniform(10.1, 12.0), 0)
        if passed
        else round(random.uniform(14.4, 15.0), 1)
    )
    return passed, value_measured, "V", None, 13


def check_soc():
    passed = simulate_test_result(95)
    value_measured = (
        round(random.uniform(50, 55), 0) if passed else round(random.uniform(20, 39), 2)
    )
    return passed, value_measured, "%", 40, 60


def check_soh():
    passed = simulate_test_result(100)
    value_measured = (
        round(random.uniform(96, 100), 0)
        if passed
        else round(random.uniform(70, 95), 2)
    )
    return passed, value_measured, "%", 95, None


def take_picture():
    passed = simulate_test_result(100)
    return passed, None, None, None, None


def flash_firmware():
    passed = simulate_test_result(90)
    value_measured = "1.2.4" if passed else "1.2.0"
    return passed, value_measured, None, None, None


# Running Tests
def run_test(test, duration):
    # start_time = datetime.now() - timedelta(days=1)
    start_time = datetime.now()
    passed, value_measured, unit, limit_low, limit_high = test()

    if passed == True:
        outcome = "PASS"
    elif passed == False:
        outcome = "FAIL"

    # ---- UPDATE PARAMETER NAMES
    step = {
        "name": test.__name__,  # Third phase
        "outcome": outcome,  # Outcome of the step
        "duration": duration,  # Duration of the step
        "started_at": start_time,
        "measurements": [
            {
                "name": test.__name__,
                "outcome": outcome,
                "value": value_measured,
                "units": unit,
                "lower_limit": limit_low,
                "upper_limit": limit_high,
            }
        ],
    }

    return step


def run_all_tests():
    tests = [
        (flash_firmware, timedelta(minutes=3, seconds=32)),
        (battery_connection, timedelta(seconds=8)),
        (check_voltage, timedelta(seconds=3)),
        (check_soc, timedelta(seconds=1)),
        (check_soh, timedelta(seconds=5)),
        (take_picture, timedelta(seconds=12)),
    ]

    steps = []
    for test, duration in tests:
        step = run_test(test, duration)
        steps.append(step)

    return steps


def handle_test():
    random_digits = "".join([str(random.randint(0, 9)) for _ in range(5)])
    serial_number = f"SI0364A{random_digits}"

    # Exécuter tous les tests
    phases = run_all_tests()

    # Créer un rapport de test
    client.create_run(
        procedure_id="FVT9",
        procedure_name="Test_QA",
        unit_under_test={
            "part_number": "SI03645A",
            "part_name": "PythonScript",
            "revision": "3.1",
            "batch_number": "11-24",
            "serial_number": serial_number,
        },
        run_passed=True,
        phases=phases,
    )


if __name__ == "__main__":
    for _ in range(1):
        handle_test()
